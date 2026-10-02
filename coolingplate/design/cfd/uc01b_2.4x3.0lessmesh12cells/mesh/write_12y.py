# -*- coding: utf-8 -*-
"""Tile one UC-01b unit 12 times along Y.

The geometry module is M. Callers may replace M before main()
(ribtop vs the original less mesh). Shared Y faces become interior.
Outer Y fluid faces are pressure outlets; outer Y solid faces are walls.
X faces stay symmetry.
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

SRC = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh\mesh"
sys.path.insert(0, SRC)
os.environ.setdefault("UC01B_MESH", "less")

import write_cht_circle_msh as M  # noqa: E402

N_Y = 12
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "uc01b_cht_less_12y.msh")
HEADER = "UC-01b CHT ribtop x12 along Y; outer Y fluid=pressure-outlet solid=wall"
NOTE = "12 connected ribtop jet units along Y"
JOIN_INTERFACE = False
SPLIT_INLETS = False
FACE_DIR = "_faces_12y"
META = None


def hx(n):
    return format(int(n), "x")


def build_unit():
    level, lv = M.active_level()
    xy = M.build_xy(lv)
    z = M.z_axis(lv)
    nz = len(z) - 1
    kind = {}
    for iq, (n0, n1, n2, n3) in enumerate(xy.quads):
        p0, p1, p2, p3 = xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3]
        xc = 0.25 * (p0[0] + p1[0] + p2[0] + p3[0])
        yc = 0.25 * (p0[1] + p1[1] + p2[1] + p3[1])
        for k in range(nz):
            zc = 0.5 * (z[k] + z[k + 1])
            zn = M.zone_of(xc, yc, zc)
            if zn:
                kind[(iq, k)] = zn
    cells = {}
    counts = {M.FLUID: 0, M.CU: 0, M.TIM: 0}
    cid = 0
    for name in (M.FLUID, M.CU, M.TIM):
        for qk in sorted(qk for qk, zn in kind.items() if zn == name):
            cid += 1
            cells[qk] = cid
            counts[name] += 1
    need = set()
    for iq, k in kind:
        n0, n1, n2, n3 = xy.quads[iq]
        for qn in (n0, n1, n2, n3):
            need.add((qn, k))
            need.add((qn, k + 1))
    keys = sorted(need)
    nodes = {key: i + 1 for i, key in enumerate(keys)}
    coords = []
    for qn, kk in keys:
        xx, yy = xy.xy[qn]
        coords.append((xx * 1e-3, yy * 1e-3, z[kk] * 1e-3))

    def nd(qn, kk):
        return nodes[(qn, kk)]

    interiors = []
    seen = {}
    bounds = defaultdict(list)

    def push_face(nids, cid_, zn):
        key = tuple(sorted(nids))
        if key in seen:
            c0, z0, nids0 = seen.pop(key)
            if z0 == zn:
                interiors.append((nids0, c0, cid_))
            else:
                pair = {z0, zn}
                nm = "wall_cu_fluid" if pair == {M.FLUID, M.CU} else (
                    "wall_tim_cu" if pair == {M.CU, M.TIM} else "wall_other")
                bounds[nm].append((nids0, c0, cid_))
        else:
            seen[key] = (cid_, zn, nids)

    for (iq, k), zn in kind.items():
        cid_ = cells[(iq, k)]
        a, b, c, d = xy.quads[iq]
        push_face((nd(a, k), nd(b, k), nd(c, k), nd(d, k)), cid_, zn)
        push_face((nd(a, k + 1), nd(b, k + 1), nd(c, k + 1), nd(d, k + 1)), cid_, zn)
        for q1, q2 in ((a, b), (b, c), (c, d), (d, a)):
            push_face((nd(q1, k), nd(q2, k), nd(q2, k + 1), nd(q1, k + 1)), cid_, zn)

    owner = {}
    for (iq, k), cid_ in cells.items():
        owner[cid_] = kind[(iq, k)]

    for _key, (cid_, zn, nids) in seen.items():
        xs = [coords[i - 1][0] * 1e3 for i in nids]
        ys = [coords[i - 1][1] * 1e3 for i in nids]
        zs = [coords[i - 1][2] * 1e3 for i in nids]
        xc, yc, zc = sum(xs) / 4, sum(ys) / 4, sum(zs) / 4
        name = M._bound_name(xc, yc, zc, xs, ys, zs)
        bounds[name].append((nids, cid_, 0))

    centroids = {}
    for (iq, k), cid_ in cells.items():
        qa, qb, qc, qd = xy.quads[iq]
        ids8 = [nd(q, kk) for kk in (k, k + 1) for q in (qa, qb, qc, qd)]
        centroids[cid_] = tuple(sum(coords[i - 1][a] for i in ids8) / 8.0 for a in range(3))

    def orient(nids, cid_):
        p0, p1, p2 = (coords[nids[0] - 1], coords[nids[1] - 1], coords[nids[2] - 1])
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz_ = ux * vy - uy * vx
        if nx * nx + ny * ny + nz_ * nz_ < 1e-30:
            p3 = coords[nids[3] - 1]
            vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz_ = ux * vy - uy * vx
        fc = tuple(sum(coords[i - 1][a] for i in nids) / 4.0 for a in range(3))
        gx, gy, gz = centroids[cid_]
        if nx * (gx - fc[0]) + ny * (gy - fc[1]) + nz_ * (gz - fc[2]) < 0.0:
            return (nids[0], nids[3], nids[2], nids[1])
        return nids

    interiors = [(orient(nids, c0), c0, c1) for nids, c0, c1 in interiors]
    for nm in list(bounds):
        bounds[nm] = [(orient(nids, c0), c0, c1) for nids, c0, c1 in bounds[nm]]

    y_of = [xy.xy[qn][1] for qn, _kk in keys]
    return dict(
        level=level, lv=lv, xy=xy, z=z, nz=nz,
        counts=counts, owner=owner, keys=keys, nodes=nodes,
        coords=coords, y_of=y_of, interiors=interiors, bounds=bounds,
    )


def y_slots(unit):
    y0, y1 = M.Y0, M.Y1
    keys = unit["keys"]
    coords = unit["coords"]
    on0, on1 = [], []
    for i, _key in enumerate(keys):
        yy = unit["y_of"][i]
        x, _y, z = coords[i]
        if abs(yy - y0) < 1e-8:
            on0.append((round(x, 10), round(z, 10), i))
        elif abs(yy - y1) < 1e-8:
            on1.append((round(x, 10), round(z, 10), i))
    on0.sort()
    on1.sort()
    if len(on0) != len(on1):
        raise SystemExit(f"Y0 nodes {len(on0)} != Y1 nodes {len(on1)}")
    for a, b in zip(on0, on1):
        if a[0] != b[0] or a[1] != b[1]:
            raise SystemExit("Y0/Y1 (x,z) mismatch; units would not be conformal")
    role = ["in"] * len(keys)
    slot0, slot1 = {}, {}
    for s, (_x, _z, i) in enumerate(on0):
        role[i] = "y0"
        slot0[i] = s
    for s, (_x, _z, i) in enumerate(on1):
        role[i] = "y1"
        slot1[i] = s
    interior = [i for i, r in enumerate(role) if r == "in"]
    in_slot = {i: s for s, i in enumerate(interior)}
    return role, slot0, slot1, in_slot, len(on0), len(interior)


def main():
    print("build one unit", flush=True)
    unit = build_unit()
    role, slot0, slot1, in_slot, nF, nI = y_slots(unit)
    n_fluid = unit["counts"][M.FLUID]
    n_cu = unit["counts"][M.CU]
    n_tim = unit["counts"][M.TIM]
    n_one = n_fluid + n_cu + n_tim
    print(f"unit cells {n_one} fluid {n_fluid} cu {n_cu} tim {n_tim}", flush=True)
    print(f"Y-plane nodes {nF} interior nodes/unit {nI}", flush=True)

    sym_x, y0_faces, y1_faces = [], [], []
    for nids, c0, _c1 in unit["bounds"].get("SYM", []):
        ys = [unit["y_of"][i - 1] for i in nids]
        if all(abs(y - M.Y0) < 1e-8 for y in ys):
            y0_faces.append((nids, c0))
        elif all(abs(y - M.Y1) < 1e-8 for y in ys):
            y1_faces.append((nids, c0))
        else:
            sym_x.append((nids, c0, 0))
    if not y0_faces or not y1_faces:
        raise SystemExit(f"missing Y faces y0={len(y0_faces)} y1={len(y1_faces)}")

    def face_key(nids, which):
        parts = []
        for nid in nids:
            i = nid - 1
            if role[i] != which:
                raise SystemExit(f"Y face node is not on {which}")
            parts.append(slot0[i] if which == "y0" else slot1[i])
        return tuple(sorted(parts))

    y0_by_key = {}
    for nids, c0 in y0_faces:
        y0_by_key[face_key(nids, "y0")] = (c0, unit["owner"][c0])
    interfaces = []
    for nids, c0 in y1_faces:
        key = face_key(nids, "y1")
        if key not in y0_by_key:
            raise SystemExit("Y1 face has no Y0 partner")
        c_other, zn_other = y0_by_key[key]
        if unit["owner"][c0] != zn_other:
            raise SystemExit(f"interface material mismatch {unit['owner'][c0]} vs {zn_other}")
        interfaces.append((nids, c0, c_other))
    print(f"interface faces/join {len(interfaces)} sym_x {len(sym_x)}", flush=True)

    out_y0_p, out_y0_w, out_y1_p, out_y1_w = [], [], [], []
    for nids, c0 in y0_faces:
        (out_y0_p if unit["owner"][c0] == M.FLUID else out_y0_w).append((nids, c0, 0))
    for nids, c0 in y1_faces:
        (out_y1_p if unit["owner"][c0] == M.FLUID else out_y1_w).append((nids, c0, 0))
    print(
        f"Y front fluid {len(out_y0_p)} wall {len(out_y0_w)} "
        f"back fluid {len(out_y1_p)} wall {len(out_y1_w)}",
        flush=True,
    )

    stride = nF + nI
    n_nodes = N_Y * nI + (N_Y + 1) * nF
    n_cells = N_Y * n_one

    def gid_of_local(u, nid):
        i = nid - 1
        r = role[i]
        if r == "y0":
            return u * stride + slot0[i] + 1
        if r == "y1":
            return (u + 1) * stride + slot1[i] + 1
        return u * stride + nF + in_slot[i] + 1

    def gcell(u, local):
        if local <= n_fluid:
            return u * n_fluid + local
        if local <= n_fluid + n_cu:
            return N_Y * n_fluid + u * n_cu + (local - n_fluid)
        return N_Y * (n_fluid + n_cu) + u * n_tim + (local - n_fluid - n_cu)

    inlet_faces = unit["bounds"].get("inlet_jet", [])
    zone_src = {
        "return_slot": unit["bounds"].get("return_slot", []),
        "wall_heat": unit["bounds"].get("wall_heat", []),
        "wall_lid": unit["bounds"].get("wall_lid", []),
        "wall_orifice": unit["bounds"].get("wall_orifice", []),
        "wall_cu_fluid": unit["bounds"].get("wall_cu_fluid", []),
        "wall_tim_cu": unit["bounds"].get("wall_tim_cu", []),
        "wall_other": unit["bounds"].get("wall_other", []),
        "SYM": sym_x,
    }
    bc_code = {
        "interior": 2, "inlet_jet": 10, "return_slot": 5, "interface": 24,
        "wall_heat": 3, "wall_lid": 3, "wall_orifice": 3,
        "wall_cu_fluid": 3, "wall_tim_cu": 3, "wall_other": 3, "SYM": 7,
        "outlet_y_front": 5, "outlet_y_back": 5,
        "wall_y_front": 3, "wall_y_back": 3,
    }
    inlet_names = [f"inlet_jet_{i:02d}" for i in range(1, N_Y + 1)] if SPLIT_INLETS else ["inlet_jet"]
    join_names = []
    if JOIN_INTERFACE:
        for j in range(1, N_Y):
            for tag in ("ifl", "icu", "itm"):
                join_names.append(f"{tag}_{j:02d}a")
                join_names.append(f"{tag}_{j:02d}b")
    order = [
        "interior", *inlet_names, *join_names, "return_slot",
        "outlet_y_front", "outlet_y_back",
        "wall_heat", "wall_lid", "wall_orifice",
        "wall_cu_fluid", "wall_tim_cu", "wall_other",
        "wall_y_front", "wall_y_back", "SYM",
    ]
    coupled = {"wall_cu_fluid", "wall_tim_cu", "wall_other"}
    tmp = os.path.join(HERE, FACE_DIR)
    os.makedirs(tmp, exist_ok=True)
    paths = {name: os.path.join(tmp, name + ".txt") for name in order}
    counts_f = {name: 0 for name in order}

    def write_faces(fh, u, faces, c1_mode):
        n = 0
        buf = []
        for nids, c0, c1 in faces:
            gn = [gid_of_local(u, i) for i in nids]
            gc0 = gcell(u, c0)
            if c1_mode == "next_zero":
                gc0 = gcell(u + 1, c0)
                gc1 = 0
            elif c1_mode == "zero":
                gc1 = 0
            elif c1_mode == "same":
                gc1 = gcell(u, c1)
            else:
                gc1 = gcell(u + 1, c1)
            buf.append(
                f"{hx(gn[0])} {hx(gn[1])} {hx(gn[2])} {hx(gn[3])} {hx(gc0)} {hx(gc1)}\n"
            )
            n += 1
            if len(buf) >= 20000:
                fh.writelines(buf)
                buf = []
        if buf:
            fh.writelines(buf)
        return n

    fhs = {name: open(paths[name], "w", encoding="ascii", newline="\n") for name in order}
    try:
        for u in range(N_Y):
            print(f"write faces unit {u + 1}/{N_Y}", flush=True)
            counts_f["interior"] += write_faces(fhs["interior"], u, unit["interiors"], "same")
            if SPLIT_INLETS:
                counts_f[inlet_names[u]] += write_faces(fhs[inlet_names[u]], u, inlet_faces, "zero")
            else:
                counts_f["inlet_jet"] += write_faces(fhs["inlet_jet"], u, inlet_faces, "zero")
            for name, faces in zone_src.items():
                mode = "same" if name in coupled else "zero"
                counts_f[name] += write_faces(fhs[name], u, faces, mode)
            if u == 0:
                counts_f["outlet_y_front"] += write_faces(fhs["outlet_y_front"], u, out_y0_p, "zero")
                counts_f["wall_y_front"] += write_faces(fhs["wall_y_front"], u, out_y0_w, "zero")
            if u == N_Y - 1:
                counts_f["outlet_y_back"] += write_faces(fhs["outlet_y_back"], u, out_y1_p, "zero")
                counts_f["wall_y_back"] += write_faces(fhs["wall_y_back"], u, out_y1_w, "zero")
            if u < N_Y - 1 and not JOIN_INTERFACE:
                counts_f["interior"] += write_faces(fhs["interior"], u, interfaces, "next")
            if u < N_Y - 1 and JOIN_INTERFACE:
                groups = {"ifl": [], "icu": [], "itm": []}
                for nids, c0, c_other in interfaces:
                    zn = unit["owner"][c0]
                    tag = "ifl" if zn == M.FLUID else ("icu" if zn == M.CU else "itm")
                    groups[tag].append((nids, c0, c_other))
                j = u + 1
                for tag, faces in groups.items():
                    if not faces:
                        continue
                    side_b = [((n[0], n[3], n[2], n[1]), c_other, 0) for n, _c0, c_other in faces]
                    counts_f[f"{tag}_{j:02d}a"] += write_faces(fhs[f"{tag}_{j:02d}a"], u, faces, "zero")
                    counts_f[f"{tag}_{j:02d}b"] += write_faces(fhs[f"{tag}_{j:02d}b"], u, side_b, "next_zero")
    finally:
        for fh in fhs.values():
            fh.close()

    n_faces = sum(counts_f.values())
    print(f"nodes {n_nodes} cells {n_cells} faces {n_faces}", flush=True)
    for name in order:
        print(f"  {name} {counts_f[name]}", flush=True)

    id_fluid = (1, N_Y * n_fluid)
    id_cu = (id_fluid[1] + 1, id_fluid[1] + N_Y * n_cu)
    id_tim = (id_cu[1] + 1, n_cells)
    coords = unit["coords"]

    print(f"write {OUT}", flush=True)
    with open(OUT, "w", encoding="ascii", newline="\n") as f:
        w = f.write
        w('(0 "' + HEADER + '")\n')
        w("(2 3)\n")
        w(f"(10 (0 1 {hx(n_nodes)} 0 3))\n")
        w(f"(12 (0 1 {hx(n_cells)} 0 0))\n")
        w(f"(13 (0 1 {hx(n_faces)} 0 0))\n")
        w(f"(10 (1 1 {hx(n_nodes)} 1 3)\n(\n")
        y0_idx = [i for i, r in enumerate(role) if r == "y0"]
        y0_idx.sort(key=lambda i: slot0[i])
        y1_idx = [i for i, r in enumerate(role) if r == "y1"]
        y1_idx.sort(key=lambda i: slot1[i])
        in_idx = [i for i, r in enumerate(role) if r == "in"]
        in_idx.sort(key=lambda i: in_slot[i])
        buf = []

        def emit(xx, yy, zz):
            buf.append(f"{xx:.10e} {yy:.10e} {zz:.10e}\n")
            if len(buf) >= 20000:
                f.writelines(buf)
                buf.clear()

        for u in range(N_Y):
            y_off = (u - (N_Y - 1) / 2.0) * M.SY * 1e-3
            for i in y0_idx:
                xx, _yy, zz = coords[i]
                emit(xx, M.Y0 * 1e-3 + y_off, zz)
            for i in in_idx:
                xx, yy, zz = coords[i]
                emit(xx, yy + y_off, zz)
        y_off_last = ((N_Y - 1) - (N_Y - 1) / 2.0) * M.SY * 1e-3
        for i in y1_idx:
            xx, _yy, zz = coords[i]
            emit(xx, M.Y1 * 1e-3 + y_off_last, zz)
        if buf:
            f.writelines(buf)
        w(")\n)\n")
        w(f"(12 (2 {hx(id_fluid[0])} {hx(id_fluid[1])} 1 4))\n")
        w(f"(12 (3 {hx(id_cu[0])} {hx(id_cu[1])} 1 4))\n")
        w(f"(12 (4 {hx(id_tim[0])} {hx(id_tim[1])} 1 4))\n")
        fstart = 1
        zone_ids = {}
        fid = 5
        for name in order:
            if counts_f[name] == 0:
                continue
            zone_ids[name] = fid
            fend = fstart + counts_f[name] - 1
            code = bc_code[name] if name in bc_code else (24 if name[:3] in ("ifl", "icu", "itm") else 10)
            w(f"(13 ({hx(fid)} {hx(fstart)} {hx(fend)} {hx(code)} 4)\n(\n")
            with open(paths[name], "r", encoding="ascii", newline="\n") as src:
                while True:
                    chunk = src.read(1 << 20)
                    if not chunk:
                        break
                    f.write(chunk)
            w(")\n)\n")
            fstart = fend + 1
            fid += 1
        w("(39 (2 fluid fluid)())\n")
        w("(39 (3 solid solid_cu)())\n")
        w("(39 (4 solid solid_tim2)())\n")
        kind_map = {2: "interior", 3: "wall", 5: "pressure-outlet", 7: "symmetry", 10: "mass-flow-inlet", 24: "interface"}
        for name, zid in zone_ids.items():
            code = bc_code[name] if name in bc_code else (24 if name[:3] in ("ifl", "icu", "itm") else 10)
            w(f"(39 ({zid} {kind_map[code]} {name})())\n")

    level = unit["level"]
    meta = META or os.path.join(HERE, f"cht_mesh_info_{level}_12y.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write(NOTE + "\n")
        f.write(f"level {level}\n")
        f.write(f"Sy_mm {M.SY}\n")
        f.write(f"n_units {N_Y}\n")
        f.write(f"y_min_mm {-N_Y * M.SY / 2}\n")
        f.write(f"y_max_mm {N_Y * M.SY / 2}\n")
        f.write("return floor at rib top z=1.50; X-ends below 1.50 are copper\n")
        f.write("outer Y fluid: outlet_y_front / outlet_y_back pressure-outlet\n")
        f.write("outer Y solid: wall_y_front / wall_y_back wall\n")
        f.write("X faces remain SYM\n")
        f.write(f"cells_total {n_cells}\n")
        f.write(f"cells_fluid {N_Y * n_fluid}\n")
        f.write(f"cells_solid_cu {N_Y * n_cu}\n")
        f.write(f"cells_solid_tim2 {N_Y * n_tim}\n")
        f.write(f"nodes {n_nodes}\n")
        f.write(f"faces {n_faces}\n")
        for name in order:
            f.write(f"zone {name} {counts_f[name]}\n")
        f.write(f"msh {OUT}\n")
    print(f"WROTE {OUT}", flush=True)


if __name__ == "__main__":
    main()
