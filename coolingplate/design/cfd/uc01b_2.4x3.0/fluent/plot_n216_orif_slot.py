# -*- coding: utf-8 -*-
"""Velocity in the jet orifice and the return slots at the orifice-plate height."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import Normalize
import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")

Z = 0.004711
mesh = p.load_mesh_fields()
idx = p.plane_idx(mesh, 2, Z, tol=2e-5)
xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
fluid = kind == 1
c = xyz.mean(axis=1)
xc, yc = c[:, 0], c[:, 1]
r = np.hypot(xc, yc)
jet = fluid & (r <= 0.00025)
slot = fluid & (np.abs(xc) >= 0.00105)
print("Z_mm", Z * 1e3)
print("fluid", int(fluid.sum()), "jet", int(jet.sum()), "slot", int(slot.sum()))
sp = np.sqrt(u * u + v * v + w * w)
for name, m in (("ALL", fluid), ("JET", jet), ("SLOT", slot)):
    print(
        name,
        "V", float(sp[m].min()), float(sp[m].max()),
        "T", float(t[m].min()), float(t[m].max()),
        "Xmm", float(xc[m].min() * 1e3), float(xc[m].max() * 1e3),
        "Ymm", float(yc[m].min() * 1e3), float(yc[m].max() * 1e3),
    )

verts = p.poly_mm(xyz[fluid], (0, 1))
vv = sp[fluid]
tt = t[fluid]
fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=140)
pc = p.PolyCollection(
    verts, array=vv, cmap="viridis", norm=Normalize(0.0, float(vv.max())),
    edgecolors="none", linewidths=0.0, antialiaseds=False,
)
ax.add_collection(pc)
cb = fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.04)
cb.set_label("速度 |V| (m/s)")
xy = c[fluid, :2] * 1e3
tri = mtri.Triangulation(xy[:, 0], xy[:, 1])
tris = tri.triangles
x, y = tri.x, tri.y
def el(i, j):
    return np.hypot(x[tris[:, i]] - x[tris[:, j]], y[tris[:, i]] - y[tris[:, j]])
tri.set_mask((el(0, 1) > 0.15) | (el(1, 2) > 0.15) | (el(2, 0) > 0.15))
levels = np.linspace(float(tt.min()), float(tt.max()), 7)
cs = ax.tricontour(tri, tt, levels=levels, colors="k", linewidths=0.7)
ax.clabel(cs, fmt="%.1f K", fontsize=7)
ax.set_aspect("equal")
ax.autoscale_view()
ax.set_xlabel("X mm")
ax.set_ylabel("Y mm")
ax.set_title(
    "iter 529  n216_q105_sym  z = 4.711 mm\n喷孔与出流导流槽  速度填色，温度等值线"
)
fig.tight_layout()
out = os.path.join(p.FIGS, "n216_sym_zorif_slot_vel.png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("WROTE", out)
