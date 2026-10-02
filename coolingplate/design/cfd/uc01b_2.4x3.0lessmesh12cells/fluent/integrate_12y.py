"""Area-weighted temperatures and mass flows from the saved 12-cell fields.

i300 is checked against the Fluent surface-integral transcript. i600 uses the
same definitions because the second report session was blocked by another job's
memory use.
"""
import json
import os

import h5py
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAS = os.path.join(ROOT, "fluent", "uc01b_cht_less_12y_i300.cas.h5")
RHO = 992.2
CP = 4179.0
QPP = 579282.0
A_CELL = 3.0e-3 * 2.4e-3
P_CELL = QPP * A_CELL
P_12 = 12.0 * P_CELL
P_2DIE = 216.0 * P_CELL

# 1-based inclusive
WALL_HEAT = (83_415_569, 83_636_752)
WALL_TIM = (85_012_625, 85_233_808)
WALL_CU = (83_651_345, 84_331_984)
RETURN = (83_359_193, 83_404_984)
OUT_F = (83_404_985, 83_410_276)
OUT_B = (83_410_277, 83_415_568)
INLETS = [(82_962_505 + i * 3724, 82_962_505 + (i + 1) * 3724 - 1) for i in range(12)]


def nodes_of(fc, a, b):
    raw = np.asarray(fc["meshes/1/faces/nodes/1/nodes"][(a - 1) * 4 : b * 4], np.int64)
    return raw.reshape(-1, 4) - 1


def area_vec(coords, fn):
    xyz = coords[fn]
    return 0.5 * np.cross(xyz[:, 2] - xyz[:, 0], xyz[:, 3] - xyz[:, 1])


def aw(values, area):
    return float(np.sum(values * area) / np.sum(area))


def owner_t(fc, fd, coords, a, b):
    fn = nodes_of(fc, a, b)
    c0 = np.asarray(fc["meshes/1/faces/c0/1"][a - 1 : b], np.int64)
    tcell = fd["results/1/phase-1/cells/SV_T/1"]
    # hyperslab of the needed cells would be slower than one read; caller passes t
    return fn, c0


def main():
    print("open", flush=True)
    with h5py.File(CAS, "r") as fc:
        coords = np.asarray(fc["meshes/1/nodes/coords/1"][:], np.float64)
        bundles = {}
        for name, ab in (
            ("wall_heat", WALL_HEAT),
            ("wall_tim_cu", WALL_TIM),
            ("wall_cu_fluid", WALL_CU),
            ("return_slot", RETURN),
            ("outlet_y_front", OUT_F),
            ("outlet_y_back", OUT_B),
        ):
            fn = nodes_of(fc, *ab)
            c0 = np.asarray(fc["meshes/1/faces/c0/1"][ab[0] - 1 : ab[1]], np.int64)
            avec = area_vec(coords, fn)
            area = np.linalg.norm(avec, axis=1)
            bundles[name] = {"fn": fn, "c0": c0, "avec": avec, "area": area}
            print(name, "n", fn.shape[0], "A", float(area.sum()), flush=True)
        inlets = []
        for i, ab in enumerate(INLETS, start=1):
            fn = nodes_of(fc, *ab)
            c0 = np.asarray(fc["meshes/1/faces/c0/1"][ab[0] - 1 : ab[1]], np.int64)
            avec = area_vec(coords, fn)
            area = np.linalg.norm(avec, axis=1)
            inlets.append({"fn": fn, "c0": c0, "avec": avec, "area": area})
            print("inlet", i, "A", float(area.sum()), flush=True)

    out = {}
    for step in ("i300", "i600"):
        dat = os.path.join(ROOT, "fluent", "uc01b_cht_less_12y_%s.dat.h5" % step)
        with h5py.File(dat, "r") as fd:
            tcell = np.asarray(fd["results/1/phase-1/cells/SV_T/1"][:], np.float64)
            pcell = np.asarray(fd["results/1/phase-1/cells/SV_P/1"][:], np.float64)
            faces = fd["results/1/phase-1/faces"]
            fu = np.asarray(faces["SV_U/1"][:], np.float64)
            fv = np.asarray(faces["SV_V/1"][:], np.float64)
            fw = np.asarray(faces["SV_W/1"][:], np.float64)
            ou = np.asarray(faces["SV_U/2"][:], np.float64)
            ov = np.asarray(faces["SV_V/2"][:], np.float64)
            ow = np.asarray(faces["SV_W/2"][:], np.float64)
        rec = {}
        for name, b in bundles.items():
            cid = b["c0"]
            tt = tcell[cid - 1]
            rec[name] = {
                "T_cell_aw": aw(tt, b["area"]),
                "T_cell_min": float(tt.min()),
                "T_cell_max": float(tt.max()),
                "area": float(b["area"].sum()),
                "n": int(tt.size),
            }
            if name.startswith("outlet") or name == "return_slot":
                # pressure only exists on fluid cells
                fluid = cid <= pcell.shape[0]
                if np.all(fluid):
                    rec[name]["P_cell_aw"] = aw(pcell[cid - 1], b["area"])
        # inlets: face velocity is SV_U/1 concatenated, 3724 each, file order 01..12
        mdots = []
        pins = []
        tins = []
        us = []
        off = 0
        for i, b in enumerate(inlets):
            n = b["fn"].shape[0]
            vel = np.column_stack([fu[off : off + n], fv[off : off + n], fw[off : off + n]])
            off += n
            flux = RHO * np.einsum("ij,ij->i", vel, b["avec"])
            # positive into the domain
            mdot = float(-flux.sum()) if flux.sum() < 0 else float(flux.sum())
            # keep the raw sum too
            mdots.append({"mdot_abs": abs(float(flux.sum())), "mdot_raw": float(flux.sum())})
            cid = b["c0"]
            fluid = cid <= pcell.shape[0]
            pins.append(aw(pcell[cid[fluid] - 1], b["area"][fluid]))
            tins.append(aw(tcell[cid - 1], b["area"]))
            us.append(aw(np.linalg.norm(vel, axis=1), b["area"]))
        rec["inlets"] = {"mdot": mdots, "P_cell_aw": pins, "T_cell_aw": tins, "U_aw": us}
        # SV_U/2 = return_slot, outlet_y_front, outlet_y_back
        cuts = [("return_slot", 45792), ("outlet_y_front", 5292), ("outlet_y_back", 5292)]
        off = 0
        outs = {}
        for name, n in cuts:
            b = bundles[name]
            vel = np.column_stack([ou[off : off + n], ov[off : off + n], ow[off : off + n]])
            off += n
            flux = RHO * np.einsum("ij,ij->i", vel, b["avec"])
            speed = np.linalg.norm(vel, axis=1)
            cid = b["c0"]
            tt = tcell[cid - 1]
            positive = np.clip(flux, 0, None)
            negative = np.clip(-flux, 0, None)
            # mass-weighted by |flux|
            wt = np.abs(flux)
            t_mw = float(np.sum(tt * wt) / np.sum(wt)) if np.sum(wt) > 0 else None
            outs[name] = {
                "mdot_raw": float(flux.sum()),
                "mdot_abs": abs(float(flux.sum())),
                "T_cell_aw": aw(tt, b["area"]),
                "T_cell_mw": t_mw,
                "Vmax": float(speed.max()),
                "V_aw": aw(speed, b["area"]),
            }
        rec["flow_faces"] = outs
        out[step] = rec
        print(step, "wall_heat", rec["wall_heat"]["T_cell_aw"], "U0", us[0], "mdot0", mdots[0], flush=True)

    path = os.path.join(ROOT, "logs", "integrate_12y.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print("WROTE", path, flush=True)


if __name__ == "__main__":
    main()
