# -*- coding: utf-8 -*-
"""Same contour views as the n216 report, from the lessmesh iter-380 field."""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import Normalize

SRC = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0\fluent"
ROOT = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh"
sys.path.insert(0, SRC)
import plot_v2_scales as p

p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_less_m425_bc216.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_less_m425_bc216.dat.h5")
p.FIGS = os.path.join(ROOT, "figs")
os.makedirs(p.FIGS, exist_ok=True)
p.NOTE = "iter 380  m425  lessmesh"
p.FLUID_LAST = 2055516
p.CU_LAST = 4139232
p.TIM_LAST = 4259680
p.ZONE = {
    "sym017": (0, 2464),
    "sym016": (2464, 41640),
    "return015": (41640, 58764),
    "int014": (58764, 388764),
    "int013": (388764, 6551904),
    "int5": (6551904, 12644056),
    "inlet": (12644056, 12649556),
    "return": (12649556, 12657044),
    "wall_heat": (12657044, 12687156),
    "wall_orif": (12687156, 12688756),
    "wall_cu": (12688756, 12778360),
    "wall_tim": (12778360, 12808472),
    "sym12": (12808472, 12853072),
    "tim_sh": (12853072, 12883184),
    "cu_sh": (12883184, 12972788),
}
p.FACE_T_ORDER = (
    ("inlet", 5500),
    ("return", 7488),
    ("wall_heat", 30112),
    ("wall_orif", 1600),
    ("wall_cu", 89604),
    ("wall_tim", 30112),
    ("sym12", 44600),
    ("tim_sh", 30112),
    ("cu_sh", 89604),
)


def c1_of(idx, c1):
    out = np.zeros(idx.shape[0], np.int64)
    a, b = p.ZONE["int014"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[idx[m] - a]
    a, b = p.ZONE["int013"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[330000 + (idx[m] - a)]
    a, b = p.ZONE["int5"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[6493140 + (idx[m] - a)]
    return out


p.c1_of = c1_of

_load = p.load_mesh_fields


def load_mesh_fields():
    import h5py
    with h5py.File(p.CAS, "r") as fc, h5py.File(p.DAT, "r") as fd:
        coords = np.asarray(fc["meshes/1/nodes/coords/1"][:], np.float64)
        fn = np.asarray(fc["meshes/1/faces/nodes/1/nodes"][:], np.uint32).reshape(-1, 4)
        c0 = np.asarray(fc["meshes/1/faces/c0/1"][:], np.int64)
        c1 = np.asarray(fc["meshes/1/faces/c1/1"][:], np.int64)
        tcell = np.asarray(fd["results/1/phase-1/cells/SV_T/1"][:], np.float64)
        ucell = np.asarray(fd["results/1/phase-1/cells/SV_U/1"][:], np.float64)
        vcell = np.asarray(fd["results/1/phase-1/cells/SV_V/1"][:], np.float64)
        wcell = np.asarray(fd["results/1/phase-1/cells/SV_W/1"][:], np.float64)
        ft = np.asarray(fd["results/1/phase-1/faces/SV_T/2"][:], np.float64)
        fu = np.asarray(fd["results/1/phase-1/faces/SV_U/1"][:], np.float64)
        fv = np.asarray(fd["results/1/phase-1/faces/SV_V/1"][:], np.float64)
        fw = np.asarray(fd["results/1/phase-1/faces/SV_W/1"][:], np.float64)
    fn0 = fn.astype(np.int64) - 1
    if c1.shape[0] != 12585292:
        raise SystemExit("unexpected c1 length %d" % c1.shape[0])
    face_t = {}
    off = 0
    for name, n in p.FACE_T_ORDER:
        a, b = p.ZONE[name]
        if b - a != n:
            raise SystemExit("zone %s count %d != %d" % (name, b - a, n))
        face_t[name] = ft[off:off + n]
        off += n
    if off != ft.shape[0]:
        raise SystemExit("SV_T/2 not fully mapped %d %d" % (off, ft.shape[0]))
    face_uvw = {
        "inlet": (fu[0:5500], fv[0:5500], fw[0:5500]),
        "return": (fu[5500:12988], fv[5500:12988], fw[5500:12988]),
    }
    return {
        "coords": coords, "fn": fn0, "c0": c0, "c1": c1,
        "tcell": tcell, "ucell": ucell, "vcell": vcell, "wcell": wcell,
        "face_t": face_t, "face_uvw": face_uvw,
    }


p.load_mesh_fields = load_mesh_fields

_save = p.save
_plot = p.plot_scalar_plane


def save(fig, stem):
    if stem.startswith("v2cur_"):
        stem = "m425_" + stem[len("v2cur_"):]
    elif stem.startswith("n216_i8587_"):
        stem = "m425_" + stem[len("n216_i8587_"):]
    return _save(fig, stem)


def _own_scale(vals):
    lo = float(np.nanmin(vals))
    hi = float(np.nanmax(vals))
    if not np.isfinite(lo) or not np.isfinite(hi):
        return None
    if hi <= lo:
        hi = lo + 1e-6
    span = hi - lo
    step = 10 ** np.floor(np.log10(span / 4.0))
    step = float(max(step, span / 8.0))
    return lo, hi, step


def plot_scalar_plane(stem, title, xlabel, ylabel, groups, caption_bits):
    title = "iter 380 lessmesh  " + title
    ranges = []
    for g in groups:
        vals = g.get("values")
        if vals is None or getattr(vals, "size", 0) == 0:
            continue
        got = _own_scale(vals)
        if got is None:
            continue
        lo, hi, step = got
        g["norm"] = Normalize(lo, hi)
        g["step"] = step
        base = g.get("label", "T (K)").replace("  绝对", "")
        g["label"] = "%s\n%.5f–%.5f" % (base, lo, hi)
        ranges.append("%.5f–%.5f" % (lo, hi))
        print("SCALE", stem, base, "%.5f" % lo, "%.5f" % hi)
    if ranges:
        title = title + "\n" + "  ".join(ranges)
    if caption_bits:
        caption_bits = "iter 380 m425 lessmesh。色标是本面最小到最大。 " + caption_bits
    return _plot(stem, title, xlabel, ylabel, groups, caption_bits)


_tv = p.plot_tv


def plot_tv(
    stem, title, xlabel, ylabel,
    water_verts, water_t, water_speed, water_a, water_b, water_u, water_v,
    t_norm, t_step, v_norm, v_step, v_label,
    extra_verts=None, extra_role="flat", extra_values=None, extra_norm=None,
    extra_step=None, extra_label=None, extra_cmap="copper",
    vec_ref=None, note="", figsize=(13.2, 6.6),
):
    # Temperature scale is rebuilt inside plot_tv from water and solid together.
    got = _own_scale(water_speed)
    if got:
        lo, hi, step = got
        v_norm = Normalize(lo, hi)
        v_step = step
        v_label = "%s\n%.4f–%.4f" % (v_label, lo, hi)
        print("SCALE", stem, "speed", "%.5f" % lo, "%.5f" % hi)
    return _tv(
        stem, title, xlabel, ylabel,
        water_verts, water_t, water_speed, water_a, water_b, water_u, water_v,
        t_norm, t_step, v_norm, v_step, v_label,
        extra_verts=extra_verts, extra_role=extra_role, extra_values=extra_values,
        extra_norm=extra_norm, extra_step=extra_step, extra_label=extra_label,
        extra_cmap=extra_cmap, vec_ref=vec_ref, note=note, figsize=figsize,
    )


p.save = save
p.plot_scalar_plane = plot_scalar_plane

import plot_n216_8587 as wall

p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_less_m425_bc216.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_less_m425_bc216.dat.h5")
p.FIGS = os.path.join(ROOT, "figs")
p.load_mesh_fields = load_mesh_fields
p.c1_of = c1_of
p.save = save
p.plot_scalar_plane = plot_scalar_plane
p.plot_tv = plot_tv
p.NOTE = "iter 380 lessmesh"
_plane = p.plane_idx

def plane_idx(mesh, axis, value, tol=2e-6):
    idx = _plane(mesh, axis, value, tol)
    if idx.size:
        return idx
    u = np.unique(np.round(mesh["coords"][:, axis], 6))
    near = float(u[np.argmin(np.abs(u - value))])
    print("SNAP axis", axis, "asked", value, "used", near)
    return _plane(mesh, axis, near, tol=5e-6)

p.plane_idx = plane_idx
print("CAS", p.CAS)

def plot_cut(mesh, axis, value, plane_axes, cu, cv, stem, title, xlabel, ylabel, figsize):
    idx = p.plane_idx(mesh, axis, value, tol=5e-6)
    xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
    fluid = kind == 1
    solid = kind == 2
    comp = {"u": u, "v": v, "w": w}
    print(stem, "asked_mm", value * 1e3, "n", int(idx.size), "fluid", int(fluid.sum()), "solid", int(solid.sum()))
    if int(fluid.sum()) < 20:
        print("SKIP", stem)
        return None
    xyz_w, t_w = xyz[fluid], t[fluid]
    uu, vv = comp[cu][fluid], comp[cv][fluid]
    sp = np.sqrt(u[fluid] ** 2 + v[fluid] ** 2 + w[fluid] ** 2)
    inplane = np.hypot(uu, vv)
    vlo, vhi, vstep = p.nice_limits(0.0, float(sp.max()), "speed")
    extra = p.poly_mm(xyz[solid], plane_axes) if np.any(solid) else None
    extra_values = t[solid] if np.any(solid) else None
    t_lo, t_hi, t_step = p.nice_limits(float(t_w.min()), float(t_w.max()), "T")
    note = "水 T %.2f–%.2f K。|V|max %.3f m/s。左图流体与固体共用一把温度色标。右图是速度，带平面内矢量。" % (
        float(t_w.min()), float(t_w.max()), float(sp.max()),
    )
    tsolid = None
    if extra_values is not None and getattr(extra_values, "size", 0):
        tsolid = (float(extra_values.min()), float(extra_values.max()))
        note += " 固体 T %.2f–%.2f K。" % tsolid
    a, b = p.centroids_xy(xyz_w, plane_axes)
    p.plot_tv(
        stem, title, xlabel, ylabel,
        p.poly_mm(xyz_w, plane_axes), t_w, sp, a, b, uu, vv,
        p.Normalize(t_lo, t_hi), t_step,
        p.Normalize(vlo, vhi), vstep, "速度 |V| (m/s)",
        extra_verts=extra, extra_role="solid" if tsolid else "flat",
        extra_values=extra_values, extra_label="固体 T (K)",
        vec_ref=float(inplane.max()) if inplane.size else 1.0,
        note=note, figsize=figsize,
    )
    print(
        "RANGE", stem,
        "tmin=%.5f" % float(t_w.min()),
        "tmax=%.5f" % float(t_w.max()),
        "vmax=%.4f" % float(sp.max()),
        "solid", tsolid,
    )
    return float(t_w.min()), float(t_w.max()), float(sp.max()), tsolid


def plot_char_planes(mesh):
    tall = (11.4, 12.2)
    wide = (13.2, 6.6)
    # X: hole edge, slit lip. Y: center-slot wall, side-slot center.
    # Z: just above the floor, full plane at the slit mouth, mid plenum.
    plot_cut(mesh, 0, 0.00040, (1, 2), "v", "w", "v2cur_x04_TV", "X = 0.400 mm  孔外槽内", "Y mm", "Z mm", tall)
    plot_cut(mesh, 0, 0.00110, (1, 2), "v", "w", "v2cur_x11_TV", "X = 1.100 mm  回液缝唇", "Y mm", "Z mm", tall)
    plot_cut(mesh, 1, 0.00040, (0, 2), "u", "w", "v2cur_y04_TV", "Y = 0.400 mm  肋中", "X mm", "Z mm", tall)
    plot_cut(mesh, 1, 0.00100, (0, 2), "u", "w", "v2cur_y10_TV", "Y = 1.000 mm  侧槽中心", "X mm", "Z mm", tall)
    plot_cut(mesh, 2, 0.00015, (0, 1), "u", "v", "v2cur_z015_TV", "z = 0.150 mm  驻点上方槽内", "X mm", "Y mm", wide)
    plot_cut(mesh, 2, 0.00350, (0, 1), "u", "v", "v2cur_z35_TV", "z = 3.500 mm  间隙顶全平面", "X mm", "Y mm", wide)
    plot_cut(mesh, 2, 0.00700, (0, 1), "u", "v", "v2cur_z70_TV", "z = 7.000 mm  上腔中面", "X mm", "Y mm", wide)


if os.environ.get("M425_EXTRA") == "1":
    plot_char_planes(p.load_mesh_fields())
    raise SystemExit(0)

wall.main()
# wall.main wrote n216 names via savefig; rename
for src, dst in (
    ("n216_i8587_wall_heat_T.png", "m425_wall_heat_T.png"),
    ("n216_i8587_ztim_mid_T.png", "m425_ztim_mid_T.png"),
):
    a = os.path.join(p.FIGS, src)
    b = os.path.join(p.FIGS, dst)
    if os.path.exists(a):
        os.replace(a, b)
        print("RENAME", b)

p.main()

def plot_x_plane(mesh, x_m):
    idx = p.plane_idx(mesh, 0, x_m, tol=5e-6)
    xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
    m = kind == 1
    s = kind == 2
    print("X13", x_m, "n", int(idx.size), "fluid", int(m.sum()), "solid", int(s.sum()))
    if int(m.sum()) < 20:
        print("SKIP x13")
        return
    xyz_w, t_w = xyz[m], t[m]
    uu, vv, ww = u[m], v[m], w[m]
    sp = np.sqrt(uu * uu + vv * vv + ww * ww)
    inplane = np.hypot(vv, ww)
    vlo, vhi, vstep = p.nice_limits(0.0, float(sp.max()), "speed")
    extra = p.poly_mm(xyz[s], (1, 2)) if np.any(s) else None
    extra_values = t[s] if np.any(s) else None
    t_lo, t_hi, t_step = p.nice_limits(float(t_w.min()), float(t_w.max()), "T")
    note = "水 T %.2f–%.2f K。|V|max %.3f m/s。左图流体与固体共用一把温度色标。右图是速度，单独色标。" % (
        float(t_w.min()), float(t_w.max()), float(sp.max()),
    )
    if extra_values is not None and extra_values.size:
        note += " 固体 T %.2f–%.2f K。" % (float(extra_values.min()), float(extra_values.max()))
        print("X13 solid", float(extra_values.min()), float(extra_values.max()))
    a, b = p.centroids_xy(xyz_w, (1, 2))
    p.plot_tv(
        "v2cur_x13_TV",
        "X = %.3f mm" % (x_m * 1e3),
        "Y mm", "Z mm",
        p.poly_mm(xyz_w, (1, 2)), t_w, sp, a, b, vv, ww,
        p.Normalize(t_lo, t_hi), t_step,
        p.Normalize(vlo, vhi), vstep, "速度 |V| (m/s)",
        extra_verts=extra, extra_role="solid", extra_values=extra_values,
        extra_label="固体 T (K)",
        vec_ref=float(inplane.max()) if inplane.size else 1.0,
        note=note,
        figsize=(11.4, 12.2),
    )
    print("RANGE x13 tmin=%.5f tmax=%.5f vmax=%.4f" % (float(t_w.min()), float(t_w.max()), float(sp.max())))


mesh = p.load_mesh_fields()
plot_x_plane(mesh, 0.0013)
Z = 0.004711
idx = p.plane_idx(mesh, 2, Z, tol=2e-5)
xyz, t, u, v, w, kind, names = p.pack_faces(mesh, idx)
fluid = kind == 1
c = xyz.mean(axis=1)
sp = np.sqrt(u * u + v * v + w * w)
print("orif fluid", int(fluid.sum()), "T", float(t[fluid].min()), float(t[fluid].max()), "V", float(sp[fluid].min()), float(sp[fluid].max()))
verts = p.poly_mm(xyz[fluid], (0, 1))
vv = sp[fluid]
tt = t[fluid]
fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=140)
vlo, vhi = float(vv.min()), float(vv.max())
if vhi <= vlo:
    vhi = vlo + 1e-6
pc = p.PolyCollection(verts, array=vv, cmap="viridis", norm=Normalize(vlo, vhi), edgecolors="none", linewidths=0.0, antialiaseds=False)
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
ax.set_title("iter 380 lessmesh  z = 4.750 mm\n喷孔与出流导流槽  速度 %.4f–%.4f m/s" % (vlo, vhi))
fig.tight_layout()
out = os.path.join(p.FIGS, "m425_zorif_slot_vel.png")
fig.savefig(out, bbox_inches="tight", facecolor="white")
print("WROTE", out)
print("CONTOURS_DONE")
