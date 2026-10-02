# -*- coding: utf-8 -*-
"""Mirror-pair check on the saved iter-8587 field. Read only."""
import os
import numpy as np
import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")
mesh = p.load_mesh_fields()

def aw(name):
    a, b = p.ZONE[name]
    xyz = mesh["coords"][mesh["fn"][a:b]]
    area = p.quad_area(xyz) if hasattr(p, "quad_area") else None
    t = mesh["face_t"][name]
    # area from two triangles
    d02 = xyz[:, 2] - xyz[:, 0]
    d13 = xyz[:, 3] - xyz[:, 1]
    area = 0.5 * np.linalg.norm(np.cross(d02, d13), axis=1)
    return float(np.sum(t * area) / np.sum(area)), float(t.min()), float(t.max())

for nm in ("wall_heat", "wall_cu", "wall_tim", "inlet", "return"):
    if nm in mesh["face_t"]:
        print("AW", nm, aw(nm))


def plane_fluid(axis, value, tol):
    idx = p.plane_idx(mesh, axis, value, tol=tol)
    xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
    m = kind == 1
    c = xyz[m].mean(axis=1)
    return c, t[m], u[m], v[m], w[m]

def pair_report(tag, c, t, u, v, w, mirror_axis):
    """mirror_axis 0=X or 1=Y. Pair points with that coordinate flipped."""
    key = np.round(c / 2e-6).astype(np.int64)
    lookup = {}
    for n in range(c.shape[0]):
        lookup.setdefault((int(key[n, 0]), int(key[n, 1]), int(key[n, 2])), []).append(n)
    i_list, j_list, d_list = [], [], []
    for n in range(c.shape[0]):
        if c[n, mirror_axis] <= 5e-5:
            continue
        mk = [int(key[n, 0]), int(key[n, 1]), int(key[n, 2])]
        mk[mirror_axis] = -mk[mirror_axis]
        cands = lookup.get(tuple(mk))
        if not cands:
            continue
        target = c[n].copy()
        target[mirror_axis] *= -1
        best, bestd = None, 1e9
        for m in cands:
            dd = float(np.linalg.norm(c[m] - target))
            if dd < bestd:
                best, bestd = m, dd
        if best is None or bestd > 5e-6:
            continue
        i_list.append(n)
        j_list.append(best)
        d_list.append(bestd)
    if len(i_list) < 10:
        print(tag, "too few", len(i_list))
        return
    i = np.asarray(i_list)
    j = np.asarray(j_list)
    print(tag, "match_mm_max", round(max(d_list) * 1e3, 5))
    dT = np.abs(t[i] - t[j])
    sp_i = np.sqrt(u[i] ** 2 + v[i] ** 2 + w[i] ** 2)
    sp_j = np.sqrt(u[j] ** 2 + v[j] ** 2 + w[j] ** 2)
    dV = np.abs(sp_i - sp_j)
    # tangential velocity that should flip
    comp = v if mirror_axis == 1 else u
    dflip = np.abs(comp[i] + comp[j])
    print(
        tag,
        "pairs", int(i.size),
        "dT_med", float(np.median(dT)),
        "dT_p95", float(np.percentile(dT, 95)),
        "dT_max", float(dT.max()),
        "dV_med", float(np.median(dV)),
        "dV_max", float(dV.max()),
        "flip_med", float(np.median(dflip)),
        "flip_max", float(dflip.max()),
    )
    # a few largest dT
    order = np.argsort(dT)[-5:][::-1]
    for k in order:
        a, b = i[k], j[k]
        print(
            "  PAIR",
            "xyz_mm",
            [round(float(c[a, n] * 1e3), 4) for n in range(3)],
            "T", round(float(t[a]), 4), round(float(t[b]), 4),
            "dT", round(float(dT[k]), 4),
            "V", round(float(sp_i[k]), 4), round(float(sp_j[k]), 4),
            "mirror_mm",
            [round(float(c[b, n] * 1e3), 4) for n in range(3)],
            "comp", round(float(comp[a]), 4), round(float(comp[b]), 4),
        )

# X=0.556 mm is the plotted cut. Y mirror should hold.
c, t, u, v, w = plane_fluid(0, 0.000556, 5e-7)
print("X556 fluid", c.shape[0], "Xmm", float(c[:, 0].mean() * 1e3))
for name, m in (
    ("y>0", c[:, 1] > 0.05e-3),
    ("y<0", c[:, 1] < -0.05e-3),
):
    sp = np.sqrt(u[m] ** 2 + v[m] ** 2 + w[m] ** 2)
    print("X556", name, "n", int(m.sum()), "Tmean", float(t[m].mean()), "Vmean", float(sp.mean()))
pair_report("X=0.556 Y-mirror", c, t, u, v, w, 1)
floor = (c[:, 2] > 0.0) & (c[:, 2] < 0.40e-3) & (np.abs(c[:, 1]) < 0.40e-3) & (c[:, 1] > 5e-5)
print("X556 floor jet n", int(floor.sum()))
pair_report("X=0.556 floor |Y|<0.4 Z<0.4 Y-mirror", c[floor], t[floor], u[floor], v[floor], w[floor], 1)

c, t, u, v, w = plane_fluid(0, 0.0, 5e-7)
print("X0 fluid", c.shape[0])
pair_report("X=0 Y-mirror", c, t, u, v, w, 1)

c, t, u, v, w = plane_fluid(1, 0.0, 5e-7)
print("Y0 fluid", c.shape[0])
pair_report("Y=0 X-mirror", c, t, u, v, w, 0)

# orifice plane slots
c, t, u, v, w = plane_fluid(2, 0.004711, 2e-5)
print("Z4711 fluid", c.shape[0])
sp = np.sqrt(u * u + v * v + w * w)
for name, m in (
    ("slot+X", (c[:, 0] > 0.00105)),
    ("slot-X", (c[:, 0] < -0.00105)),
    ("jet", (np.hypot(c[:, 0], c[:, 1]) < 0.00022)),
):
    print("Z4711", name, "n", int(m.sum()), "Tmean", float(t[m].mean()), "Vmean", float(sp[m].mean()), "T", float(t[m].min()), float(t[m].max()))
pair_report("z=4.711 Y-mirror", c, t, u, v, w, 1)
pair_report("z=4.711 X-mirror", c, t, u, v, w, 0)

# inlet face direction
fu, fv, fw = mesh["face_uvw"]["inlet"]
print(
    "INLET U", float(fu.min()), float(fu.max()),
    "V", float(fv.min()), float(fv.max()),
    "W", float(fw.min()), float(fw.max()),
)

# mesh node mirror: sample 20000 nodes
xyz = mesh["coords"]
key = np.round(xyz / 1e-6).astype(np.int64)
have = set(zip(key[:, 0].tolist(), key[:, 1].tolist(), key[:, 2].tolist()))
rng = np.random.default_rng(0)
sel = rng.choice(xyz.shape[0], 8000, replace=False)
for ax, name in ((0, "X"), (1, "Y")):
    miss = 0
    for n in sel:
        mk = [int(key[n, 0]), int(key[n, 1]), int(key[n, 2])]
        mk[ax] = -mk[ax]
        if tuple(mk) not in have:
            miss += 1
    print("MESH", name, "mirror miss", miss, "of", sel.size)

import h5py
with h5py.File(p.DAT, "r") as fd:
    faces = fd["results/1/phase-1/faces"]
    print("FACE_KEYS", list(faces.keys()))
    if "SV_P" in faces:
        for sub in faces["SV_P"].keys():
            arr = np.asarray(faces["SV_P"][sub])
            print("SV_P", sub, arr.shape, float(arr.min()), float(arr.max()))

