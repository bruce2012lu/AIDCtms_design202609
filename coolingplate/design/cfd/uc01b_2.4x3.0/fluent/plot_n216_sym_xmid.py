# -*- coding: utf-8 -*-
import os
import numpy as np
from matplotlib.colors import Normalize
import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")
mesh = p.load_mesh_fields()
import h5py
with h5py.File(p.DAT, "r") as fd:
    pcell = np.asarray(fd["results/1/phase-1/cells/SV_P/1"])

def aw_p(name):
    a, b = p.ZONE[name]
    idx = np.arange(a, b)
    xyz = mesh["coords"][mesh["fn"][idx]]
    d02 = xyz[:, 2] - xyz[:, 0]
    d13 = xyz[:, 3] - xyz[:, 1]
    area = 0.5 * np.linalg.norm(np.cross(d02, d13), axis=1)
    c0 = mesh["c0"][idx]
    c1 = p.c1_of(idx, mesh["c1"])
    pp = np.full(idx.shape[0], np.nan)
    for cid, dest in ((c0, pp),):
        m = (cid >= 1) & (cid <= p.FLUID_LAST)
        dest[m] = pcell[cid[m] - 1]
    m2 = np.isnan(pp)
    m = m2 & (c1 >= 1) & (c1 <= p.FLUID_LAST)
    pp[m] = pcell[c1[m] - 1]
    ok = np.isfinite(pp)
    print(name, "P_aw", float(np.sum(pp[ok] * area[ok]) / np.sum(area[ok])), "n", int(ok.sum()))

aw_p("inlet")
aw_p("return")

idx = p.plane_idx(mesh, 0, 0.000556, tol=5e-7)
xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
m = kind == 1
s = kind == 2
sp = np.sqrt(u[m] ** 2 + v[m] ** 2 + w[m] ** 2)
inplane = np.hypot(v[m], w[m])
print("XMID T", float(t[m].min()), float(t[m].max()), "Vmax", float(sp.max()), "solid", float(t[s].min()), float(t[s].max()))
vlo, vhi, vstep = p.nice_limits(0.0, float(sp.max()), "speed")
tlo, thi, tstep = p.nice_limits(float(t[m].min()), float(t[m].max()), "T")
elo, ehi, estep = p.nice_limits(float(t[s].min()), float(t[s].max()), "T")
p.plot_tv(
    "n216_sym_xmid_TV",
    "iter 529  X = 0.556 mm  离开射流、朝回液缝\n不是对称面；±Y 仍有温差",
    "Y mm", "Z mm",
    p.poly_mm(xyz[m], (1, 2)), t[m], sp,
    *p.centroids_xy(xyz[m], (1, 2)), v[m], w[m],
    Normalize(tlo, thi), tstep,
    Normalize(vlo, vhi), vstep, "速度 |V| (m/s)",
    extra_verts=p.poly_mm(xyz[s], (1, 2)), extra_role="solid",
    extra_values=t[s], extra_norm=Normalize(elo, ehi), extra_step=estep,
    extra_label="固体 T (K)",
    vec_ref=float(max(inplane.max(), 1e-6)),
    note="n216_q105_sym。水 T %.2f–%.2f K。|V|max %.3f m/s。固体 T %.2f–%.2f K。"
    % (t[m].min(), t[m].max(), float(sp.max()), t[s].min(), t[s].max()),
)
