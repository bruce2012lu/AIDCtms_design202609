# -*- coding: utf-8 -*-
"""Rescale and add contour figures from the iter-1439 CFF export.

Reads uc01b_cht_v2_current.cas.h5 / .dat.h5 directly. Does not start Fluent
and does not touch the live solve. Faces are the real mesh quads (circular
orifice, rectangular slots and ribs). No triangulation mask.
"""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.cm import ScalarMappable
from matplotlib.collections import PolyCollection
from matplotlib.colors import Normalize

for _fn in ("Microsoft YaHei", "SimHei"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")
CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_i7900.cas.h5")
DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_i7900.dat.h5")
NOTE = "iter 7900，已收敛"

# 0-based face-index slices, same order as meshes/1/faces/zoneTopology
ZONE = {
    "sym017": (0, 3576),
    "sym016": (3576, 30620),
    "return015": (30620, 48120),
    "int014": (48120, 551572),
    "int013": (551572, 5061462),
    "int5": (5061462, 13255426),
    "inlet": (13255426, 13260926),
    "return": (13260926, 13267646),
    "wall_heat": (13267646, 13297366),
    "wall_orif": (13297366, 13298966),
    "wall_cu": (13298966, 13403858),
    "wall_tim": (13403858, 13433578),
    "sym12": (13433578, 13491762),
    "tim_sh": (13491762, 13521482),
    "cu_sh": (13521482, 13626374),
}
FLUID_LAST = 2760804  # 1-based inclusive
CU_LAST = 4293960
TIM_LAST = 4472280

# Face static temperature SV_T/2, zones that are not the big interior blocks.
FACE_T_ORDER = (
    ("inlet", 5500),
    ("return", 6720),
    ("wall_heat", 29720),
    ("wall_orif", 1600),
    ("wall_cu", 104892),
    ("wall_tim", 29720),
    ("sym12", 58184),
    ("tim_sh", 29720),
    ("cu_sh", 104892),
)


def k2c(t):
    return t - 273.15


def signed_speed_limits(lo, hi):
    span = max(float(hi - lo), 1e-6)
    step = 0.5 if span >= 2.5 else (0.2 if span >= 1.0 else (0.1 if span >= 0.4 else 0.05))
    a = np.floor(float(lo) / step) * step
    b = np.ceil(float(hi) / step) * step
    if (float(lo) - a) > 0.55 * step or (b - float(hi)) > 0.55 * step:
        step = step / 2.0
        a = np.floor(float(lo) / step) * step
        b = np.ceil(float(hi) / step) * step
    if b <= a:
        b = a + step
    return float(a), float(b), float(step)


def nice_limits(lo, hi, kind):
    """Round a data span onto readable ticks.

    Spans of several kelvin use 1 K or 0.5 K. A span much smaller than 0.5 K
    keeps a finer step; rounding that span out to 0.5 K would be one flat color.
    """
    span = float(hi - lo)
    if span <= 0:
        span = 1e-4
    if kind == "speed":
        if span >= 2:
            step = 0.5
        elif span >= 0.8:
            step = 0.2
        elif span >= 0.3:
            step = 0.1
        elif span >= 0.08:
            step = 0.02
        else:
            step = 0.01
        a = 0.0
        b = np.ceil((hi + 1e-12) / step) * step
        if b <= 0:
            b = step
        return float(a), float(b), float(step)
    if span >= 8:
        step = 1.0
    elif span >= 2:
        step = 0.5
    elif span >= 0.8:
        step = 0.2
    elif span >= 0.25:
        step = 0.05
    elif span >= 0.08:
        step = 0.01
    else:
        step = 0.005
    a = np.floor((lo - 1e-9) / step) * step
    b = np.ceil((hi + 1e-9) / step) * step
    if b <= a:
        b = a + step
    # Drop padding that is large next to the data.
    if (b - a) > span * 1.35 and step >= 0.5:
        step = 0.5 if span >= 2 else 0.2
        a = np.floor((lo - 1e-9) / step) * step
        b = np.ceil((hi + 1e-9) / step) * step
    return float(a), float(b), float(step)


def tick_fmt(step):
    if step >= 1:
        return "%.0f"
    if step >= 0.1:
        return "%.1f"
    if step >= 0.01:
        return "%.2f"
    return "%.3f"


def faces_on_value(fn, coord, value, tol):
    hits = []
    n = fn.shape[0]
    for i0 in range(0, n, 1_500_000):
        sl = fn[i0 : i0 + 1_500_000]
        vals = coord[sl]
        m = np.abs(vals - value).max(axis=1) < tol
        if np.any(m):
            hits.append(i0 + np.flatnonzero(m))
    if not hits:
        return np.empty(0, np.int64)
    return np.concatenate(hits).astype(np.int64)


def zone_ids(idx):
    names = np.empty(idx.shape[0], dtype=object)
    names[:] = ""
    for name, (a, b) in ZONE.items():
        m = (idx >= a) & (idx < b)
        names[m] = name
    return names


def c1_of(idx, c1):
    out = np.zeros(idx.shape[0], np.int64)
    a, b = ZONE["int014"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[idx[m] - a]
    a, b = ZONE["int013"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[(503452 + (idx[m] - a))]
    a, b = ZONE["int5"]
    m = (idx >= a) & (idx < b)
    out[m] = c1[(5013342 + (idx[m] - a))]
    return out


def cell_kind(cid):
    """0 none, 1 fluid, 2 copper, 3 tim. cid is 1-based."""
    k = np.zeros(cid.shape[0], np.int8)
    k[(cid >= 1) & (cid <= FLUID_LAST)] = 1
    k[(cid > FLUID_LAST) & (cid <= CU_LAST)] = 2
    k[(cid > CU_LAST) & (cid <= TIM_LAST)] = 3
    return k


def load_mesh_fields():
    import h5py

    with h5py.File(CAS, "r") as fc, h5py.File(DAT, "r") as fd:
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
    if fn0.min() < 0 or fn0.max() >= coords.shape[0]:
        raise SystemExit("face node ids out of range")
    if c1.shape[0] != 13207306:
        raise SystemExit("unexpected c1 length %d" % c1.shape[0])
    face_t = {}
    off = 0
    for name, n in FACE_T_ORDER:
        a, b = ZONE[name]
        if b - a != n:
            raise SystemExit("zone %s count %d != %d" % (name, b - a, n))
        face_t[name] = ft[off : off + n]
        off += n
    if off != ft.shape[0]:
        raise SystemExit("SV_T/2 not fully mapped")
    # inlet (5500) then return_slot (6720)
    face_uvw = {
        "inlet": (fu[0:5500], fv[0:5500], fw[0:5500]),
        "return": (fu[5500:12220], fv[5500:12220], fw[5500:12220]),
    }
    return {
        "coords": coords,
        "fn": fn0,
        "c0": c0,
        "c1": c1,
        "tcell": tcell,
        "ucell": ucell,
        "vcell": vcell,
        "wcell": wcell,
        "face_t": face_t,
        "face_uvw": face_uvw,
    }


def quad_area(xyz):
    d02 = xyz[:, 2, :] - xyz[:, 0, :]
    d13 = xyz[:, 3, :] - xyz[:, 1, :]
    return 0.5 * np.linalg.norm(np.cross(d02, d13), axis=1)


def area_weighted(t, area):
    return float(np.sum(t * area) / np.sum(area))


def pack_faces(mesh, idx, use_face_t=None, use_face_v=None):
    """Quads + temperature + velocity for a set of global face indices."""
    fn = mesh["fn"][idx]
    xyz = mesh["coords"][fn]  # (n,4,3)
    n = idx.shape[0]
    t = np.full(n, np.nan)
    u = np.zeros(n)
    v = np.zeros(n)
    w = np.zeros(n)
    kind = np.zeros(n, np.int8)  # 1 fluid, 2 solid
    names = zone_ids(idx)
    c0 = mesh["c0"][idx]
    c1 = c1_of(idx, mesh["c1"])
    k0 = cell_kind(c0)
    k1 = cell_kind(c1)

    def cell_t(cid):
        return mesh["tcell"][cid - 1]

    def cell_uvw(cid, out_u, out_v, out_w, mask):
        fluid = (cid >= 1) & (cid <= FLUID_LAST) & mask
        if not np.any(fluid):
            return
        ii = cid[fluid] - 1
        out_u[fluid] = mesh["ucell"][ii]
        out_v[fluid] = mesh["vcell"][ii]
        out_w[fluid] = mesh["wcell"][ii]

    both_f = (k0 == 1) & (k1 == 1)
    only0 = (k0 == 1) & (k1 != 1)
    only1 = (k1 == 1) & (k0 != 1)
    solid = (k0 >= 2) & (k1 >= 2)
    # default from cells
    if np.any(both_f):
        t[both_f] = 0.5 * (cell_t(c0[both_f]) + cell_t(c1[both_f]))
        u[both_f] = 0.5 * (
            mesh["ucell"][c0[both_f] - 1] + mesh["ucell"][c1[both_f] - 1]
        )
        v[both_f] = 0.5 * (
            mesh["vcell"][c0[both_f] - 1] + mesh["vcell"][c1[both_f] - 1]
        )
        w[both_f] = 0.5 * (
            mesh["wcell"][c0[both_f] - 1] + mesh["wcell"][c1[both_f] - 1]
        )
        kind[both_f] = 1
    if np.any(only0):
        t[only0] = cell_t(c0[only0])
        cell_uvw(c0, u, v, w, only0)
        kind[only0] = 1
    if np.any(only1):
        t[only1] = cell_t(c1[only1])
        cell_uvw(c1, u, v, w, only1)
        kind[only1] = 1
    if np.any(solid):
        # average the two solid cells when both exist
        t0 = np.zeros(n)
        t1 = np.zeros(n)
        t0[solid] = cell_t(c0[solid])
        has1 = solid & (c1 > 0)
        only_s0 = solid & (c1 == 0)
        t[only_s0] = t0[only_s0]
        t[has1] = 0.5 * (t0[has1] + cell_t(c1[has1]))
        kind[solid] = 2

    if use_face_t:
        for name, arr in use_face_t.items():
            a, b = ZONE[name]
            m = names == name
            if not np.any(m):
                continue
            local = idx[m] - a
            t[m] = arr[local]
            kind[m] = 2 if name.startswith("wall") or name.endswith("_sh") else kind[m]
            if name in ("inlet", "return", "wall_orif"):
                kind[m] = 1

    if use_face_v:
        for name, (uu, vv, ww) in use_face_v.items():
            a, b = ZONE[name]
            m = names == name
            if not np.any(m):
                continue
            local = idx[m] - a
            u[m] = uu[local]
            v[m] = vv[local]
            w[m] = ww[local]
            kind[m] = 1

    return xyz, t, u, v, w, kind, names


def select_zone_plane(mesh, zone, axis, value, tol=2e-6):
    a, b = ZONE[zone]
    fn = mesh["fn"][a:b]
    vals = mesh["coords"][fn, axis]
    m = np.abs(vals - value).max(axis=1) < tol
    idx = np.flatnonzero(m).astype(np.int64) + a
    return idx


def plane_idx(mesh, axis, value, tol=2e-6):
    return faces_on_value(mesh["fn"], mesh["coords"][:, axis], value, tol)


def report_area_weights(mesh):
    """Area-weighted face temperatures from the saved i7900 field."""
    rho = 992.2
    cp = 4179.0
    mdot = 2.067e-4
    qpp = 567460.32
    p_cell = qpp * 2.4e-3 * 3.0e-3
    p_2die = 210.0 * p_cell

    def zone_aw(name, tarr):
        a, b = ZONE[name]
        xyz = mesh["coords"][mesh["fn"][a:b]]
        area = quad_area(xyz)
        return area_weighted(tarr, area), float(area.sum()), int(tarr.size)

    t_tim, a_tim, n_tim = zone_aw("wall_heat", mesh["face_t"]["wall_heat"])
    t_cu, a_cu, n_cu = zone_aw("wall_cu", mesh["face_t"]["wall_cu"])
    t_in, a_in, n_in = zone_aw("inlet", mesh["face_t"]["inlet"])
    t_out, a_out, n_out = zone_aw("return", mesh["face_t"]["return"])
    uu, vv, ww = mesh["face_uvw"]["inlet"]
    ru, rv, rw = mesh["face_uvw"]["return"]
    print(
        "AW wall_heat T", t_tim, "A", a_tim, "n", n_tim,
        "h", qpp / (t_tim - 313.15),
    )
    print(
        "AW wall_cu T", t_cu, "A", a_cu, "n", n_cu,
        "h_same_qpp", qpp / (t_cu - 313.15),
    )
    print("AW inlet T", t_in, "A", a_in, "n", n_in)
    print("AW return T", t_out, "A", a_out, "n", n_out)
    print("P_cell", p_cell, "P_2die", p_2die)
    print("R_TIM_in_2die", (t_tim - 313.15) / p_2die, "R_cell", (t_tim - 313.15) / p_cell)
    print("R_conv_2die", (t_cu - 313.15) / p_2die, "R_conv_cell", (t_cu - 313.15) / p_cell)
    q_out = mdot * cp * (t_out - t_in)
    print(
        "ENERGY area-weighted Q_out", q_out, "Q_in", p_cell,
        "ratio", q_out / p_cell, "cp", cp, "rho", rho,
        "inlet_|V|max", float(np.sqrt(uu * uu + vv * vv + ww * ww).max()),
        "return_Vz", float(rw.min()), float(rw.max()),
    )


def stats_line(tag, t, u, v, w, kind):
    sp = np.sqrt(u * u + v * v + w * w)
    def rng(mask, arr):
        if not np.any(mask):
            return None
        a = arr[mask]
        return float(a.min()), float(a.max()), int(a.size)

    print(
        tag,
        "n", int(t.size),
        "fluid", rng(kind == 1, t),
        "solid", rng(kind == 2, t),
        "speed", rng(kind == 1, sp),
        "Vz", rng(kind == 1, w),
        "Vxy", None
        if not np.any(kind == 1)
        else (
            float(np.hypot(u[kind == 1], v[kind == 1]).max()),
            float(np.hypot(u[kind == 1], v[kind == 1]).min()),
        ),
    )


def poly_mm(xyz, axes):
    return xyz[:, :, axes] * 1e3


def add_polys(ax, verts, values, norm, cmap, edges=False):
    if verts.shape[0] == 0:
        return None
    pc = PolyCollection(
        verts,
        array=values,
        cmap=cmap,
        norm=norm,
        edgecolors="none",
        linewidths=0.0,
        antialiaseds=False,
    )
    ax.add_collection(pc)
    return pc


def add_flat(ax, verts, color):
    if verts.shape[0] == 0:
        return
    pc = PolyCollection(
        verts,
        facecolors=color,
        edgecolors="none",
        linewidths=0.0,
        antialiaseds=False,
    )
    ax.add_collection(pc)


def add_outline(ax, verts, color="#1a1a1a", lw=0.85):
    """Outer edges of a quad set: circle, slot and rib rectangles, not every cell."""
    if verts is None or verts.shape[0] == 0:
        return
    from matplotlib.collections import LineCollection

    counts = {}
    for poly in verts:
        pts = [(round(float(p[0]), 4), round(float(p[1]), 4)) for p in poly]
        for i in range(4):
            a = pts[i]
            b = pts[(i + 1) % 4]
            key = (a, b) if a <= b else (b, a)
            counts[key] = counts.get(key, 0) + 1
    lines = [key for key, c in counts.items() if c == 1]
    if lines:
        ax.add_collection(LineCollection(lines, colors=color, linewidths=lw, zorder=4))


def style_ax(ax, xlabel, ylabel, title):
    ax.set_aspect("equal")
    ax.autoscale_view()
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=11)
    ax.margins(0.02)


def colorbar(fig, ax, norm, cmap, label, step):
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = fig.colorbar(sm, ax=ax, shrink=0.86, pad=0.02)
    cb.set_label(label)
    ticks = np.arange(norm.vmin, norm.vmax + step * 0.5, step)
    if ticks.size > 14:
        ticks = ticks[::2]
    cb.set_ticks(ticks)
    cb.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _p: tick_fmt(step) % x))
    return cb


def quiver_sqrt(ax, a, b, u, v, speed_ref, n_a=34, n_b=26):
    """In-plane arrows. Length follows sqrt(speed) so a slow slot and a jet both show."""
    sp = np.hypot(u, v)
    keep = sp > 0.02
    if not np.any(keep):
        return 0, 0.0
    aa, bb, uu, vv, ss = a[keep], b[keep], u[keep], v[keep], sp[keep]
    # bin
    if aa.size > 8:
        ae = np.linspace(aa.min(), aa.max(), n_a + 1)
        be = np.linspace(bb.min(), bb.max(), n_b + 1)
        ai = np.clip(np.digitize(aa, ae) - 1, 0, n_a - 1)
        bi = np.clip(np.digitize(bb, be) - 1, 0, n_b - 1)
        acc_u = np.zeros((n_b, n_a))
        acc_v = np.zeros((n_b, n_a))
        cnt = np.zeros((n_b, n_a))
        for i, j, u1, v1 in zip(ai, bi, uu, vv):
            acc_u[j, i] += u1
            acc_v[j, i] += v1
            cnt[j, i] += 1
        jj, ii = np.nonzero(cnt)
        aa = 0.5 * (ae[ii] + ae[ii + 1])
        bb = 0.5 * (be[jj] + be[jj + 1])
        uu = acc_u[jj, ii] / cnt[jj, ii]
        vv = acc_v[jj, ii] / cnt[jj, ii]
        ss = np.hypot(uu, vv)
    vmax = float(max(speed_ref, ss.max(), 1e-9))
    # longest arrow ~ 0.42 mm on the geometry
    length = 0.42 * np.sqrt(ss / vmax)
    ux = np.divide(uu, ss, out=np.zeros_like(uu), where=ss > 1e-8) * length
    uy = np.divide(vv, ss, out=np.zeros_like(vv), where=ss > 1e-8) * length
    ax.quiver(
        aa, bb, ux, uy, angles="xy", scale_units="xy", scale=1,
        color="k", width=0.0032, headwidth=3.4, headlength=4.2, zorder=5,
    )
    ax.plot([], [], color="k", label="箭头长度 ∝ √速度，最长 = %.2f m/s" % vmax)
    return int(aa.size), vmax


def centroids_xy(xyz, axes):
    c = xyz.mean(axis=1)
    return c[:, axes[0]] * 1e3, c[:, axes[1]] * 1e3


def save(fig, stem):
    out = os.path.join(FIGS, stem + ".png")
    fig.savefig(out, dpi=140, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", out)
    return out


def finish_limits(ax, verts_list, pad_frac=0.03):
    pts = np.concatenate([v.reshape(-1, 2) for v in verts_list if v.size], axis=0)
    xmin, ymin = pts.min(axis=0)
    xmax, ymax = pts.max(axis=0)
    dx = max(xmax - xmin, 1e-6)
    dy = max(ymax - ymin, 1e-6)
    ax.set_xlim(xmin - pad_frac * dx, xmax + pad_frac * dx)
    ax.set_ylim(ymin - pad_frac * dy, ymax + pad_frac * dy)


def plot_scalar_plane(
    stem, title, xlabel, ylabel, groups, caption_bits,
):
    """groups: list of dicts with verts, values, role in {water, solid, flat}."""
    fig_w = 8.6
    fig, ax = plt.subplots(figsize=(fig_w, 6.8), dpi=140)
    norms = {}
    shown = []
    for g in groups:
        role = g["role"]
        if g["verts"].shape[0] == 0:
            continue
        if role == "flat":
            add_flat(ax, g["verts"], g.get("color", "#d9d9d9"))
            add_outline(ax, g["verts"])
            shown.append(g["verts"])
            continue
        norm = g["norm"]
        cmap = g["cmap"]
        add_polys(ax, g["verts"], g["values"], norm, cmap)
        add_outline(ax, g["verts"], color="#202020", lw=0.7)
        norms[role] = (norm, cmap, g["label"], g["step"])
        shown.append(g["verts"])
    if not shown:
        plt.close(fig)
        print("EMPTY", stem)
        return None
    finish_limits(ax, shown)
    # One colorbar. Fluid and solid temperature share it.
    colored = [g for g in groups if g.get("role") in ("water", "solid") and getattr(g.get("values"), "size", 0)]
    if len(colored) >= 2:
        both = np.concatenate([np.asarray(g["values"], np.float64).ravel() for g in colored])
        both = both[np.isfinite(both)]
        lo, hi, step = nice_limits(float(both.min()), float(both.max()), "T")
        norm = Normalize(lo, hi)
        ax.collections.clear()
        shown = []
        for g in groups:
            if g["verts"].shape[0] == 0:
                continue
            if g["role"] == "flat":
                add_flat(ax, g["verts"], g.get("color", "#d9d9d9"))
                add_outline(ax, g["verts"])
            else:
                add_polys(ax, g["verts"], g["values"], norm, "turbo")
                add_outline(ax, g["verts"], color="#202020", lw=0.7)
            shown.append(g["verts"])
        finish_limits(ax, shown)
        colorbar(fig, ax, norm, "turbo", "T (K)", step)
    elif "water" in norms:
        colorbar(fig, ax, *norms["water"][:2], norms["water"][2], norms["water"][3])
    elif "solid" in norms:
        colorbar(fig, ax, *norms["solid"][:2], norms["solid"][2], norms["solid"][3])
    style_ax(ax, xlabel, ylabel, title + "\n" + NOTE)
    if caption_bits:
        ax.text(
            0.0, -0.16, caption_bits, transform=ax.transAxes, fontsize=8, va="top",
        )
    fig.tight_layout()
    return save(fig, stem)


def _paint_cbar(cax, norm, cmap, label, step):
    sm = ScalarMappable(norm=norm, cmap=cmap)
    sm.set_array([])
    cb = plt.colorbar(sm, cax=cax)
    cb.set_label(label)
    ticks = np.arange(norm.vmin, norm.vmax + step * 0.5, step)
    if ticks.size > 12:
        ticks = ticks[::2]
    cb.set_ticks(ticks)
    cb.ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _p: tick_fmt(step) % x))
    return cb


def _stacked_colorbars(fig, ax, norm_a, cmap_a, label_a, step_a, norm_b, cmap_b, label_b, step_b):
    from mpl_toolkits.axes_grid1 import make_axes_locatable

    divider = make_axes_locatable(ax)
    cax_a = divider.append_axes("right", size="3.5%", pad=0.08)
    cax_b = divider.append_axes("right", size="3.5%", pad=0.55)
    _paint_cbar(cax_a, norm_a, cmap_a, label_a, step_a)
    _paint_cbar(cax_b, norm_b, cmap_b, label_b, step_b)


def plot_tv(
    stem, title, xlabel, ylabel,
    water_verts, water_t, water_speed, water_a, water_b, water_u, water_v,
    t_norm, t_step, v_norm, v_step, v_label,
    extra_verts=None, extra_role="flat", extra_values=None, extra_norm=None,
    extra_step=None, extra_label=None, extra_cmap="copper",
    vec_ref=None, note="", figsize=(13.2, 6.6),
):
    """Left: one temperature colorbar, fluid and solid share it. Right: velocity, its own colorbar."""
    fig, axes = plt.subplots(1, 2, figsize=figsize, dpi=140, sharex=True, sharey=True)
    ax_t, ax_v = axes
    shown = []
    parts = []
    if water_t is not None and getattr(water_t, "size", 0):
        parts.append(np.asarray(water_t, np.float64).ravel())
    has_solid = (
        extra_role == "solid"
        and extra_values is not None
        and getattr(extra_values, "size", 0)
    )
    if has_solid:
        parts.append(np.asarray(extra_values, np.float64).ravel())
    if parts:
        both = np.concatenate(parts)
        both = both[np.isfinite(both)]
        lo, hi, step = nice_limits(float(both.min()), float(both.max()), "T")
        t_norm = Normalize(lo, hi)
        t_step = step
    if extra_verts is not None and extra_verts.shape[0]:
        if has_solid:
            add_polys(ax_t, extra_verts, extra_values, t_norm, "turbo")
        else:
            add_flat(ax_t, extra_verts, "#e4e4e4")
        add_flat(ax_v, extra_verts, "#e4e4e4")
        add_outline(ax_t, extra_verts, color="#333333", lw=0.7)
        add_outline(ax_v, extra_verts, color="#333333", lw=0.7)
        shown.append(extra_verts)
    if water_verts.shape[0]:
        add_polys(ax_t, water_verts, water_t, t_norm, "turbo")
        add_polys(ax_v, water_verts, water_speed, v_norm, "viridis")
        add_outline(ax_t, water_verts, color="#111111", lw=0.9)
        add_outline(ax_v, water_verts, color="#111111", lw=0.9)
        shown.append(water_verts)
        ref = float(vec_ref if vec_ref is not None else max(np.hypot(water_u, water_v).max(), 1e-9))
        n_ar, vmax_ar = quiver_sqrt(ax_t, water_a, water_b, water_u, water_v, ref)
        quiver_sqrt(ax_v, water_a, water_b, water_u, water_v, ref)
        print(stem, "arrows", n_ar, "arrow_ref", vmax_ar)
    finish_limits(ax_t, shown)
    finish_limits(ax_v, shown)
    colorbar(fig, ax_v, v_norm, "viridis", v_label, v_step)
    colorbar(fig, ax_t, t_norm, "turbo", "T (K)", t_step)
    style_ax(ax_t, xlabel, ylabel, title + "\n温度  流体与固体同一色标")
    style_ax(ax_v, xlabel, ylabel, v_label)
    fig.suptitle(NOTE, fontsize=11)
    if note:
        fig.text(0.01, 0.01, note, fontsize=8, ha="left", va="bottom")
    fig.tight_layout(rect=(0, 0.04, 1, 0.94))
    return save(fig, stem)


def subset(xyz, t, u, v, w, kind, mask):
    return xyz[mask], t[mask], u[mask], v[mask], w[mask], kind[mask]


def _nearest(arr, target, lo, hi):
    band = arr[(arr >= lo - 1e-12) & (arr <= hi + 1e-12)]
    if band.size == 0:
        return None
    return float(band[np.argmin(np.abs(band - target))])


def _solid_plot(mesh, idx, stem, title, note, use_face_t=None):
    if idx.size < 8:
        print("SKIP", stem, "n", int(idx.size))
        return
    xyz, t, u, v, w, kind, names = pack_faces(mesh, idx, use_face_t=use_face_t)
    c0 = mesh["c0"][idx]
    c1 = c1_of(idx, mesh["c1"])
    k0 = cell_kind(c0)
    k1 = cell_kind(c1)
    tim = ((k0 == 3) | (k1 == 3)) & (kind >= 1)
    cu = ((k0 == 2) | (k1 == 2)) & ~tim & (kind >= 1)
    # Boundary face temperature already applied. Keep solid faces only.
    solid = kind == 2
    if use_face_t:
        solid = np.ones(idx.shape[0], dtype=bool)
    if not np.any(solid):
        print("SKIP", stem, "no solid")
        return
    tt = t[solid]
    lo, hi, step = nice_limits(float(np.nanmin(tt)), float(np.nanmax(tt)), "T")
    verts = poly_mm(xyz[solid], (0, 1))
    zone = "solid"
    if np.any(tim[solid]) and not np.any(cu[solid] if cu.shape == solid.shape else False):
        zone = "solid_tim2"
    elif np.any(cu) and not np.any(tim[solid]):
        zone = "solid_cu"
    plot_scalar_plane(
        stem, title, "X mm", "Y mm",
        [{
            "role": "solid", "verts": verts, "values": tt,
            "norm": Normalize(lo, hi), "cmap": "inferno",
            "label": "固体 T (K)", "step": step,
        }],
        note + " T %.3f–%.3f K（%.3f–%.3f °C），色标 %.3f–%.3f K，步长 %.3f K。%s"
        % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max()), lo, hi, step, zone),
    )
    print(
        "RANGE", stem,
        "tmin=%.5f" % float(tt.min()),
        "tmax=%.5f" % float(tt.max()),
        "n=%d" % int(tt.size),
        "zone=%s" % zone,
        "scale=%.5f–%.5f step %.4f" % (lo, hi, step),
    )


def extra_sections(mesh):
    """Additional solid and fluid cuts from the iter-3861 export."""
    tf = mesh["tcell"][:FLUID_LAST]
    n_cold = int(np.count_nonzero(tf < 313.15 - 1e-4))
    print(
        "FLUID_CELL_T",
        "min=%.5f" % float(tf.min()),
        "max=%.5f" % float(tf.max()),
        "below_313.15=%d" % n_cold,
    )
    z = np.unique(np.round(mesh["coords"][:, 2], 7))
    x = np.unique(np.round(mesh["coords"][:, 0], 7))
    z_tim = _nearest(z, -0.00204, -0.002079, -0.002001)
    z_cu = _nearest(z, -0.00100, -0.001999, -0.000001)
    z_ret = _nearest(z, 0.00475, 0.00351, 0.00599)
    x_mid = _nearest(x, 0.00055, 0.00020, 0.00090)
    print("PLANES", "tim_mid", z_tim, "cu_mid", z_cu, "z_ret", z_ret, "x_mid", x_mid)

    if z_tim is not None:
        idx = plane_idx(mesh, 2, z_tim, tol=5e-7)
        _solid_plot(
            mesh, idx, "v2cur_ztim_mid_T",
            "TIM 中面  z = %.3f mm  solid_tim2" % (z_tim * 1e3),
            "固体。TIM 厚度中面，不是壁面。",
        )
    if z_cu is not None:
        idx = plane_idx(mesh, 2, z_cu, tol=5e-7)
        _solid_plot(
            mesh, idx, "v2cur_zcu_mid_T",
            "铜座中面  z = %.3f mm  solid_cu" % (z_cu * 1e3),
            "固体。2 mm 铜座厚度中部，不是铜–水界面。",
        )

    idx = select_zone_plane(mesh, "wall_tim", 2, -0.002, tol=5e-6)
    _solid_plot(
        mesh, idx, "v2cur_ztimcu_T",
        "TIM–Cu 界面  z = -2.000 mm  wall_tim_cu",
        "界面面温度。",
        use_face_t={"wall_tim": mesh["face_t"]["wall_tim"]},
    )

    idx = plane_idx(mesh, 2, 0.00075, tol=5e-7)
    xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
    c0 = mesh["c0"][idx]
    c1 = c1_of(idx, mesh["c1"])
    k0 = cell_kind(c0)
    k1 = cell_kind(c1)
    cu = (kind == 2) & ((k0 == 2) | (k1 == 2))
    if int(cu.sum()) > 8:
        tt = t[cu]
        lo, hi, step = nice_limits(float(tt.min()), float(tt.max()), "T")
        plot_scalar_plane(
            "v2cur_zrib_mid_T",
            "肋中高固体  z = 0.750 mm  solid_cu",
            "X mm", "Y mm",
            [{
                "role": "solid", "verts": poly_mm(xyz[cu], (0, 1)), "values": tt,
                "norm": Normalize(lo, hi), "cmap": "inferno",
                "label": "固体 T (K)", "step": step,
            }],
            "只画铜肋，槽里的水不在这张图上。T %.2f–%.2f K（%.2f–%.2f °C）。"
            % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max())),
        )
        print("RANGE v2cur_zrib_mid_T tmin=%.5f tmax=%.5f n=%d" % (tt.min(), tt.max(), int(tt.size)))
    else:
        print("SKIP rib mid solid", int(cu.sum()))

    idx = plane_idx(mesh, 2, 0.004711, tol=2e-5)
    xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
    c0 = mesh["c0"][idx]
    c1 = c1_of(idx, mesh["c1"])
    k0 = cell_kind(c0)
    k1 = cell_kind(c1)
    cu = (kind == 2) & ((k0 == 2) | (k1 == 2))
    if int(cu.sum()) > 8:
        tt = t[cu]
        lo, hi, step = nice_limits(float(tt.min()), float(tt.max()), "T")
        plot_scalar_plane(
            "v2cur_zorif_solid_T",
            "孔板固体  z = 4.711 mm  圆孔周围的铜",
            "X mm", "Y mm",
            [{
                "role": "solid", "verts": poly_mm(xyz[cu], (0, 1)), "values": tt,
                "norm": Normalize(lo, hi), "cmap": "inferno",
                "label": "固体 T (K)", "step": step,
            }],
            "固体铜。圆孔和回液缝是空的，不是方孔。T %.2f–%.2f K（%.2f–%.2f °C）。"
            % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max())),
        )
        print("RANGE v2cur_zorif_solid_T tmin=%.5f tmax=%.5f n=%d" % (tt.min(), tt.max(), int(tt.size)))
    else:
        print("SKIP orifice solid", int(cu.sum()))

    if z_ret is not None:
        idx = plane_idx(mesh, 2, z_ret, tol=5e-7)
        xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
        xc = xyz.mean(axis=1)[:, 0]
        slit = (kind == 1) & (np.abs(xc) >= 0.00110 - 1e-6)
        print("RETURN_STATION", z_ret, "fluid", int((kind == 1).sum()), "slit", int(slit.sum()))
        if int(slit.sum()) > 50:
            xyz_s, t_s, u_s, v_s, w_s, _k = subset(xyz, t, u, v, w, kind, slit)
            sp = np.sqrt(u_s ** 2 + v_s ** 2 + w_s ** 2)
            inplane = np.hypot(u_s, v_s)
            field = w_s
            span = max(float(field.max() - field.min()), 1e-6)
            vstep = 0.05 if span < 0.4 else 0.1
            vlo = np.floor(float(field.min()) / vstep) * vstep
            vhi = np.ceil(float(field.max()) / vstep) * vstep
            rlo, rhi, rstep = nice_limits(float(t_s.min()), float(t_s.max()), "T")
            plot_tv(
                "v2cur_zreturn_mid_TV",
                "回液缝中段  z = %.3f mm  水温与 Vz" % (z_ret * 1e3),
                "X mm", "Y mm",
                poly_mm(xyz_s, (0, 1)), t_s, field,
                *centroids_xy(xyz_s, (0, 1))[:2], u_s, v_s,
                Normalize(rlo, rhi), rstep,
                Normalize(vlo, vhi), vstep, "轴向速度 Vz (m/s)",
                vec_ref=float(max(inplane.max(), 1e-6)),
                note="水 T %.2f–%.2f K。|V|max %.3f m/s，平面内最大 %.3f m/s，Vz %.3f–%.3f m/s。右图是 Vz。"
                % (t_s.min(), t_s.max(), float(sp.max()), float(inplane.max()), float(w_s.min()), float(w_s.max())),
            )
            print(
                "RANGE v2cur_zreturn_mid_TV z_mm=%.4f tmin=%.5f tmax=%.5f vmax=%.4f vin=%.4f vz=%.4f..%.4f n=%d"
                % (z_ret * 1e3, t_s.min(), t_s.max(), float(sp.max()), float(inplane.max()), float(w_s.min()), float(w_s.max()), int(t_s.size))
            )

    if x_mid is not None:
        idx = plane_idx(mesh, 0, x_mid, tol=5e-7)
        xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
        print("XMID", x_mid, "n", int(idx.size), "fluid", int((kind == 1).sum()), "solid", int((kind == 2).sum()))
        m = kind == 1
        s = kind == 2
        if int(m.sum()) > 20:
            xyz_w, t_w = xyz[m], t[m]
            uu, vv, ww = u[m], v[m], w[m]
            sp = np.sqrt(uu ** 2 + vv ** 2 + ww ** 2)
            inplane = np.hypot(vv, ww)
            vlo, vhi, vstep = nice_limits(0.0, float(sp.max()), "speed")
            extra = poly_mm(xyz[s], (1, 2)) if np.any(s) else None
            extra_values = t[s] if np.any(s) else None
            if extra_values is not None and extra_values.size:
                elo, ehi, estep = nice_limits(float(extra_values.min()), float(extra_values.max()), "T")
                enorm = Normalize(elo, ehi)
            else:
                elo = ehi = estep = enorm = None
            t_lo, t_hi, t_step = nice_limits(float(t_w.min()), float(t_w.max()), "T")
            note = "水 T %.2f–%.2f K（%.2f–%.2f °C）。|V|max %.3f m/s。" % (
                t_w.min(), t_w.max(), k2c(t_w.min()), k2c(t_w.max()), float(sp.max()),
            )
            if extra_values is not None and extra_values.size:
                note += " 固体 T %.2f–%.2f K，与水共用一把温度色标。底部是 TIM，其上是铜。右图是速度，单独色标。" % (
                    extra_values.min(), extra_values.max(),
                )
            a, b = centroids_xy(xyz_w, (1, 2))
            plot_tv(
                "v2cur_xmid_TV",
                "X = %.3f mm  离开射流、朝回液缝" % (x_mid * 1e3),
                "Y mm", "Z mm",
                poly_mm(xyz_w, (1, 2)), t_w, sp, a, b, vv, ww,
                Normalize(t_lo, t_hi), t_step,
                Normalize(vlo, vhi), vstep, "速度 |V| (m/s)",
                extra_verts=extra, extra_role="solid", extra_values=extra_values,
                extra_norm=enorm, extra_step=estep, extra_label="固体 T (K)",
                extra_cmap="plasma",
                vec_ref=float(inplane.max()) if inplane.size else 1.0,
                note=note,
                figsize=(11.4, 12.2),
            )
            print(
                "RANGE v2cur_xmid_TV x_mm=%.4f tmin=%.5f tmax=%.5f vmax=%.4f"
                % (x_mid * 1e3, t_w.min(), t_w.max(), float(sp.max()))
            )
            if extra_values is not None and extra_values.size:
                print(
                    "RANGE v2cur_xmid_TV_solid tmin=%.5f tmax=%.5f"
                    % (float(extra_values.min()), float(extra_values.max()))
                )


def main():
    print("loading", flush=True)
    mesh = load_mesh_fields()
    print("loaded nodes", mesh["coords"].shape[0], "faces", mesh["fn"].shape[0], flush=True)
    report_area_weights(mesh)

    # --- boundary surfaces ---
    idx_tim = np.arange(*ZONE["wall_heat"], dtype=np.int64)
    xyz, t, u, v, w, kind, names = pack_faces(
        mesh, idx_tim, use_face_t={"wall_heat": mesh["face_t"]["wall_heat"]}
    )
    ztim = xyz[:, :, 2]
    if np.abs(ztim - (-0.00208)).max() > 2e-6:
        raise SystemExit("wall_heat is not on z=-2.08 mm")
    stats_line("TIM", t, u, v, w, kind)
    tim = dict(xyz=xyz, t=t, u=u, v=v, w=w)

    idx_floor = select_zone_plane(mesh, "wall_cu", 2, 0.0)
    xyz, t, u, v, w, kind, names = pack_faces(
        mesh, idx_floor, use_face_t={"wall_cu": mesh["face_t"]["wall_cu"]}
    )
    kind[:] = 2
    stats_line("CU_FLOOR", t, u, v, w, kind)
    floor = dict(xyz=xyz, t=t)

    idx_rib = select_zone_plane(mesh, "wall_cu", 2, 0.0015)
    xyz, t, u, v, w, kind, names = pack_faces(
        mesh, idx_rib, use_face_t={"wall_cu": mesh["face_t"]["wall_cu"]}
    )
    kind[:] = 2
    stats_line("RIB_TOP", t, u, v, w, kind)
    # rib tops must sit on rib bands, not in the open slot |y|<0.2
    yc = xyz.mean(axis=1)[:, 1]
    in_center_slot = np.abs(yc) < 0.00019
    print("rib faces", idx_rib.size, "in center slot", int(in_center_slot.sum()))
    rib = dict(xyz=xyz, t=t)

    idx_ret = np.arange(*ZONE["return"], dtype=np.int64)
    xyz, t, u, v, w, kind, names = pack_faces(
        mesh,
        idx_ret,
        use_face_t={"return": mesh["face_t"]["return"]},
        use_face_v={"return": mesh["face_uvw"]["return"]},
    )
    kind[:] = 1
    zc = xyz.mean(axis=1)[:, 2]
    xc = xyz.mean(axis=1)[:, 0]
    print(
        "RETURN z mm", float(zc.min() * 1e3), float(zc.max() * 1e3),
        "x mm", float(xc.min() * 1e3), float(xc.max() * 1e3),
        "n", idx_ret.size,
    )
    stats_line("RETURN", t, u, v, w, kind)
    ret = dict(xyz=xyz, t=t, u=u, v=v, w=w)

    # horizontal / vertical cuts
    cuts = {}
    for key, axis, value in (
        ("zmid", 2, 0.00075),
        ("zgap", 2, 0.00250),
        ("zorif", 2, 0.004711),
        ("y0", 1, 0.0),
        ("yside", 1, 0.00080),
        ("x0", 0, 0.0),
    ):
        idx = plane_idx(mesh, axis, value)
        xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
        stats_line(key, t, u, v, w, kind)
        cuts[key] = dict(xyz=xyz, t=t, u=u, v=v, w=w, kind=kind, names=names)
        print(" ", key, "faces", int(idx.size), flush=True)

    # shared water scale: slot, gap, and the three vertical cuts (fluid only)
    water_samples = []
    for key in ("zmid", "zgap", "y0", "yside", "x0"):
        d = cuts[key]
        m = d["kind"] == 1
        water_samples.append(d["t"][m])
    wall = np.concatenate(water_samples)
    wmin, wmax = float(wall.min()), float(wall.max())
    t_lo, t_hi, t_step = nice_limits(wmin, wmax, "T")
    t_norm = Normalize(t_lo, t_hi)
    print("SHARED_WATER", wmin, wmax, "scale", t_lo, t_hi, t_step)

    ranges = []

    def remember(name, **kw):
        ranges.append((name, kw))
        bits = [name]
        for k, val in kw.items():
            if isinstance(val, float):
                bits.append("%s=%.5g" % (k, val))
            else:
                bits.append("%s=%s" % (k, val))
        print("RANGE", " ".join(bits))

    # TIM bottom
    tt = tim["t"]
    lo, hi, step = nice_limits(float(tt.min()), float(tt.max()), "T")
    verts = poly_mm(tim["xyz"], (0, 1))
    plot_scalar_plane(
        "v2cur_wall_heat_T",
        "TIM 底面 wall_heat  固体温度",
        "X mm", "Y mm",
        [{
            "role": "solid", "verts": verts, "values": tt,
            "norm": Normalize(lo, hi), "cmap": "inferno",
            "label": "固体 T (K)", "step": step,
        }],
        "T %.3f–%.3f K（%.3f–%.3f °C），色标步长 %.3f K"
        % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max()), step),
    )
    remember("TIM", tmin=float(tt.min()), tmax=float(tt.max()), scale_lo=lo, scale_hi=hi, step=step)

    # copper floor
    tt = floor["t"]
    lo, hi, step = nice_limits(float(tt.min()), float(tt.max()), "T")
    verts = poly_mm(floor["xyz"], (0, 1))
    plot_scalar_plane(
        "v2cur_z0_T",
        "铜–水底面 z = 0  固体界面温度（wall_cu_fluid）",
        "X mm", "Y mm",
        [{
            "role": "solid", "verts": verts, "values": tt,
            "norm": Normalize(lo, hi), "cmap": "inferno",
            "label": "固体 T (K)", "step": step, "edges": True,
        }],
        "仅 z=0 的铜–水界面（槽底/缝底）。T %.2f–%.2f K（%.2f–%.2f °C）"
        % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max())),
    )
    remember("CU_FLOOR", tmin=float(tt.min()), tmax=float(tt.max()), scale_lo=lo, scale_hi=hi, step=step, n=int(tt.size))

    # rib top solid
    tt = rib["t"]
    lo, hi, step = nice_limits(float(tt.min()), float(tt.max()), "T")
    verts = poly_mm(rib["xyz"], (0, 1))
    plot_scalar_plane(
        "v2cur_zrib_solid_T",
        "肋顶固体温度  z = 1.500 mm  wall_cu_fluid",
        "X mm", "Y mm",
        [{
            "role": "solid", "verts": verts, "values": tt,
            "norm": Normalize(lo, hi), "cmap": "inferno",
            "label": "固体 T (K)", "step": step,
        }],
        "固体侧界面，不是 z=1.5 mm 流体单元。T %.2f–%.2f K（%.2f–%.2f °C）"
        % (tt.min(), tt.max(), k2c(tt.min()), k2c(tt.max())),
    )
    remember("RIB", tmin=float(tt.min()), tmax=float(tt.max()), scale_lo=lo, scale_hi=hi, step=step, n=int(tt.size))

    def water_solid_split(d):
        m = d["kind"] == 1
        s = d["kind"] == 2
        return m, s

    # Cooler cross-sections (gap, orifice, return) share a scale that is not
    # stretched up to the hot slot water.
    cool_lo, cool_hi, cool_step = 313.0, 319.0, 0.5
    cool_norm = Normalize(cool_lo, cool_hi)

    def tv_horizontal(key, stem, title, speed_mode, tn, ts, scale_tag):
        d = cuts[key]
        m, s = water_solid_split(d)
        xyz_w, t_w, u_w, v_w, w_w, _k = subset(d["xyz"], d["t"], d["u"], d["v"], d["w"], d["kind"], m)
        tn_lo, tn_hi, tn_step = nice_limits(float(t_w.min()), float(t_w.max()), "T")
        tn = Normalize(tn_lo, tn_hi)
        ts = tn_step
        scale_tag = "本面最小最大"
        verts_w = poly_mm(xyz_w, (0, 1))
        a, b = centroids_xy(xyz_w, (0, 1))
        sp = np.sqrt(u_w ** 2 + v_w ** 2 + w_w ** 2)
        inplane = np.hypot(u_w, v_w)
        if speed_mode == "vz":
            field = w_w
            floc = "轴向速度 Vz (m/s)"
            vlo, vhi, vstep = signed_speed_limits(float(field.min()), float(field.max()))
        else:
            field = sp
            floc = "速度 |V| (m/s)"
            vlo, vhi, vstep = nice_limits(0.0, float(sp.max()), "speed")
        vnorm = Normalize(vlo, vhi)
        extra = None
        extra_values = None
        solid_note = ""
        if np.any(s):
            extra = poly_mm(d["xyz"][s], (0, 1))
            extra_values = d["t"][s]
            tsld = extra_values
            solid_note = " 固体 T %.2f–%.2f K（%.2f–%.2f °C），与水共用左图一把温度色标。" % (
                tsld.min(), tsld.max(), k2c(tsld.min()), k2c(tsld.max()),
            )
            remember(key + "_solid", tmin=float(tsld.min()), tmax=float(tsld.max()), n=int(tsld.size))
        note = (
            "水 T %.2f–%.2f K（%.2f–%.2f °C）。|V|max %.3f m/s，平面内最大 %.3f m/s，Vz %.3f–%.3f m/s。左图一把温度色标，右图单独速度色标。"
            % (
                t_w.min(), t_w.max(), k2c(t_w.min()), k2c(t_w.max()),
                float(sp.max()), float(inplane.max()),
                float(w_w.min()), float(w_w.max()),
            )
        )
        if speed_mode == "vz":
            note += " 孔内主速度是轴向 Vz，右图是 Vz，不是平面内矢量。"
        elif float(np.max(np.abs(w_w))) > 3.0 * float(inplane.max() + 1e-9):
            note += " 右图高速区是轴向射流；箭头是平面内的慢速流动。"
        note += solid_note
        plot_tv(
            stem, title, "X mm", "Y mm",
            verts_w, t_w, field, a, b, u_w, v_w,
            tn, ts,
            vnorm, vstep, floc,
            extra_verts=extra, extra_role="solid" if extra_values is not None else "flat",
            extra_values=extra_values,
            vec_ref=float(max(inplane.max(), 1e-6)),
            note=note,
        )
        # fix orifice to use its own T scale — plot_tv already does when speed_mode==vz
        remember(
            key,
            tmin=float(t_w.min()), tmax=float(t_w.max()),
            vmax=float(sp.max()), vin=float(inplane.max()),
            vzmin=float(w_w.min()), vzmax=float(w_w.max()),
            vlo=float(vlo), vhi=float(vhi),
            n=int(t_w.size),
        )

    # The shared-scale path above special-cases orifice. Call explicitly for clarity.
    tv_horizontal("zmid", "v2cur_zmid_TV", "z = 0.750 mm 槽中水  温度与速度", "speed", t_norm, t_step, "热槽共用")
    tv_horizontal("zgap", "v2cur_zgap_TV", "z = 2.500 mm 肋顶以上间隙  水温与速度", "speed", cool_norm, cool_step, "冷流体共用")
    tv_horizontal("zorif", "v2cur_zorif_TV", "z = 4.711 mm 圆孔与回液缝  温度与轴向速度", "vz", cool_norm, cool_step, "冷流体共用")

    # return slit: face velocity, mostly axial
    xyz = ret["xyz"]
    sp = np.sqrt(ret["u"] ** 2 + ret["v"] ** 2 + ret["w"] ** 2)
    inplane = np.hypot(ret["u"], ret["v"])
    print(
        "RETURN components Vin", float(inplane.max()),
        "Vz", float(ret["w"].min()), float(ret["w"].max()),
        "|V|", float(sp.max()),
    )
    # If axial dominates, color by Vz / speed rather than empty in-plane arrows.
    axial = float(np.max(np.abs(ret["w"]))) >= 0.75 * float(sp.max())
    verts = poly_mm(xyz, (0, 1))
    a, b = centroids_xy(xyz, (0, 1))
    rlo, rhi, rstep = nice_limits(float(ret["t"].min()), float(ret["t"].max()), "T")
    if axial:
        field = ret["w"]
        vlo = np.floor(float(field.min()) / 0.05) * 0.05
        vhi = np.ceil(float(field.max()) / 0.05) * 0.05
        # pick a readable step from the span
        _a, _b, vstep = nice_limits(float(field.min()), float(field.max()), "T")
        # signed velocity: rebuild limits without forcing a huge pad
        span = max(float(field.max() - field.min()), 1e-6)
        vstep = 0.05 if span < 0.4 else (0.1 if span < 1.2 else 0.2)
        vlo = np.floor(float(field.min()) / vstep) * vstep
        vhi = np.ceil(float(field.max()) / vstep) * vstep
        vlabel = "轴向速度 Vz (m/s)"
        vec_u, vec_v = ret["u"], ret["v"]
        note = "回液缝边界 return_slot。主速度沿轴向，右图是 Vz。平面内箭头只画得动的那一部分。"
    else:
        field = sp
        vlo, vhi, vstep = nice_limits(0.0, float(sp.max()), "speed")
        vlabel = "速度 |V| (m/s)"
        vec_u, vec_v = ret["u"], ret["v"]
        note = "回液缝边界 return_slot 的面速度。"
    note += " 水 T %.2f–%.2f K（%.2f–%.2f °C）。|V|max %.3f m/s，Vz %.3f–%.3f m/s。" % (
        ret["t"].min(), ret["t"].max(), k2c(ret["t"].min()), k2c(ret["t"].max()),
        float(sp.max()), float(ret["w"].min()), float(ret["w"].max()),
    )
    plot_tv(
        "v2cur_return_TV",
        "回液缝 return_slot  水温与速度",
        "X mm", "Y mm",
        verts, ret["t"], field, a, b, vec_u, vec_v,
        Normalize(rlo, rhi), rstep,
        Normalize(vlo, vhi), vstep, vlabel,
        vec_ref=float(max(inplane.max(), 1e-6)),
        note=note,
    )
    remember(
        "RETURN",
        tmin=float(ret["t"].min()), tmax=float(ret["t"].max()),
        scale_lo=rlo, scale_hi=rhi,
        vmax=float(sp.max()), vin=float(inplane.max()),
        vzmin=float(ret["w"].min()), vzmax=float(ret["w"].max()),
        vlo=float(vlo), vhi=float(vhi),
        zmin_mm=float(xyz.mean(axis=1)[:, 2].min() * 1e3),
        zmax_mm=float(xyz.mean(axis=1)[:, 2].max() * 1e3),
        n=int(ret["t"].size), axial=axial,
    )

    def tv_vertical(key, stem, title, h_axis, v_axis, xlabel, ylabel, comp_u, comp_v):
        d = cuts[key]
        m, s = water_solid_split(d)
        xyz_w = d["xyz"][m]
        t_w = d["t"][m]
        u_all = d["u"][m]
        v_all = d["v"][m]
        w_all = d["w"][m]
        uu = {"u": u_all, "v": v_all, "w": w_all}[comp_u]
        vv = {"u": u_all, "v": v_all, "w": w_all}[comp_v]
        verts_w = poly_mm(xyz_w, (h_axis, v_axis))
        a, b = centroids_xy(xyz_w, (h_axis, v_axis))
        sp = np.sqrt(u_all ** 2 + v_all ** 2 + w_all ** 2)
        inplane = np.hypot(uu, vv)
        vlo, vhi, vstep = nice_limits(0.0, float(sp.max()), "speed")
        extra = poly_mm(d["xyz"][s], (h_axis, v_axis)) if np.any(s) else None
        extra_values = d["t"][s] if np.any(s) else None
        if extra_values is not None and extra_values.size:
            elo, ehi, estep = nice_limits(float(extra_values.min()), float(extra_values.max()), "T")
            enorm = Normalize(elo, ehi)
            remember(
                key + "_solid",
                tmin=float(extra_values.min()), tmax=float(extra_values.max()),
                scale_lo=elo, scale_hi=ehi, step=estep,
            )
        else:
            enorm = estep = None
        own_lo, own_hi, own_step = nice_limits(float(t_w.min()), float(t_w.max()), "T")
        note = (
            "水 T %.2f–%.2f K（%.2f–%.2f °C），色标取本面 %.3f–%.3f K。|V|max %.3f m/s。"
            % (t_w.min(), t_w.max(), k2c(t_w.min()), k2c(t_w.max()), own_lo, own_hi, float(sp.max()))
        )
        if extra_values is not None and extra_values.size:
            note += " 固体 T %.2f–%.2f K（%.2f–%.2f °C），与水共用左图一把温度色标。右图是速度，单独色标。" % (
                extra_values.min(), extra_values.max(), k2c(extra_values.min()), k2c(extra_values.max()),
            )
        plot_tv(
            stem, title, xlabel, ylabel,
            verts_w, t_w, sp, a, b, uu, vv,
            Normalize(own_lo, own_hi), own_step,
            Normalize(vlo, vhi), vstep, "速度 |V| (m/s)",
            extra_verts=extra, extra_role="solid", extra_values=extra_values,
            extra_norm=enorm, extra_step=estep, extra_label="固体 T (K)",
            extra_cmap="plasma",
            vec_ref=float(inplane.max()) if inplane.size else 1.0,
            note=note,
            figsize=(11.4, 12.2),
        )
        remember(
            key,
            tmin=float(t_w.min()), tmax=float(t_w.max()),
            vmax=float(sp.max()), vin=float(inplane.max()),
            shared_lo=t_lo, shared_hi=t_hi,
            vlo=float(vlo), vhi=float(vhi),
        )

    tv_vertical("y0", "v2cur_y0_TV", "Y = 0  中槽竖直切面", 0, 2, "X mm", "Z mm", "u", "w")
    tv_vertical("yside", "v2cur_yside_TV", "Y = 0.800 mm  侧槽竖直切面", 0, 2, "X mm", "Z mm", "u", "w")
    tv_vertical("x0", "v2cur_x0_TV", "X = 0  竖直切面", 1, 2, "Y mm", "Z mm", "v", "w")

    # slit inlet: horizontal water at the top of the gap, slit bands only, if present
    d = cuts["zgap"]
    # also cut z=3.50 mm, the plane where the gap meets the return ducts
    idx = plane_idx(mesh, 2, 0.00350)
    xyz, t, u, v, w, kind, names = pack_faces(mesh, idx)
    stats_line("z35", t, u, v, w, kind)
    m = kind == 1
    xc = xyz.mean(axis=1)[:, 0]
    # half-slits |x| in [1.10, 1.50] mm
    slit = m & (np.abs(xc) >= 0.00110 - 1e-6)
    print("z=3.50 fluid", int(m.sum()), "slit-band", int(slit.sum()))
    if int(slit.sum()) > 50:
        xyz_s, t_s, u_s, v_s, w_s, _k = subset(xyz, t, u, v, w, kind, slit)
        sp = np.sqrt(u_s ** 2 + v_s ** 2 + w_s ** 2)
        inplane = np.hypot(u_s, v_s)
        axial = float(np.max(np.abs(w_s))) > 1.5 * float(inplane.max() + 1e-12)
        verts = poly_mm(xyz_s, (0, 1))
        a, b = centroids_xy(xyz_s, (0, 1))
        rlo, rhi, rstep = nice_limits(float(t_s.min()), float(t_s.max()), "T")
        if axial:
            field = w_s
            span = max(float(field.max() - field.min()), 1e-6)
            vstep = 0.05 if span < 0.4 else (0.1 if span < 1.2 else 0.2)
            vlo = np.floor(float(field.min()) / vstep) * vstep
            vhi = np.ceil(float(field.max()) / vstep) * vstep
            vlabel = "轴向速度 Vz (m/s)"
            note = "间隙顶进入 ±X 回液缝的水。主速度是轴向，右图为 Vz。"
        else:
            field = sp
            vlo, vhi, vstep = nice_limits(0.0, float(sp.max()), "speed")
            vlabel = "速度 |V| (m/s)"
            note = "z = 3.500 mm，|X|≥1.10 mm，间隙进入回液缝的入口截面。"
        note += " 水 T %.2f–%.2f K（%.2f–%.2f °C）。|V|max %.3f m/s，平面内最大 %.3f m/s，Vz %.3f–%.3f m/s。" % (
            t_s.min(), t_s.max(), k2c(t_s.min()), k2c(t_s.max()),
            float(sp.max()), float(inplane.max()), float(w_s.min()), float(w_s.max()),
        )
        plot_tv(
            "v2cur_slitin_TV",
            "回液缝入口  z = 3.500 mm  |X|≥1.10 mm",
            "X mm", "Y mm",
            verts, t_s, field, a, b, u_s, v_s,
            Normalize(rlo, rhi), rstep,
            Normalize(vlo, vhi), vstep, vlabel,
            vec_ref=float(max(inplane.max(), 1e-6)),
            note=note,
        )
        remember(
            "SLIT_IN",
            tmin=float(t_s.min()), tmax=float(t_s.max()),
            scale_lo=rlo, scale_hi=rhi,
            vmax=float(sp.max()), vin=float(inplane.max()),
            vzmin=float(w_s.min()), vzmax=float(w_s.max()),
            vlo=float(vlo), vhi=float(vhi),
            n=int(t_s.size), axial=axial,
        )
    else:
        print("SLIT_IN missing — no fluid faces in the slit bands at z=3.50 mm")

    print("SHARED", t_lo, t_hi, t_step)
    extra_sections(mesh)
    print("DONE")


if __name__ == "__main__":
    main()
