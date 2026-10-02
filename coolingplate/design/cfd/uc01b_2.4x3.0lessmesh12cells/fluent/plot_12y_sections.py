# Section figures for the 12-cell UC-01b lessmesh field.
# Planes cover every cut in the 1-cell results report, plus the Y-join,
# the local center-slot equivalents, the Y outlets, and one-cell zooms.
import json
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.colors import Normalize

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAS = os.path.join(ROOT, "fluent", "uc01b_cht_less_12y_i300.cas.h5")
FIGS = os.path.join(ROOT, "figs")

FLUID_LAST = 12_679_440
CU_LAST = 27_120_768
TIM_LAST = 28_005_504
C1_IFACE_LAST = 176_000
C1_INTERIOR_MIN = 427_297
C1_INTERIOR_MAX = 82_962_504

# 1-based inclusive face ids from logs/zone_ids.txt
ZONES = {
    "wall_heat": (83_415_569, 83_636_752),
    "wall_tim_cu": (85_012_625, 85_233_808),
    "return_slot": (83_359_193, 83_404_984),
    "outlet_y_front": (83_404_985, 83_410_276),
    "outlet_y_back": (83_410_277, 83_415_568),
}

# Reference cell is the unit on Y = [0, 2.4] mm. Its local origin sits at Y = 1.2 mm.
Y_LOCAL = {
    "y0": 1.2e-3,
    "y04": 1.6e-3,
    "yside": 2.0e-3,
    "y10": 2.2e-3,
}
CELL_Y0 = 0.0
CELL_Y1 = 2.4e-3


def cell_kind(cid):
    k = np.zeros(cid.shape, np.int8)
    k[(cid >= 1) & (cid <= FLUID_LAST)] = 1
    k[(cid > FLUID_LAST) & (cid <= CU_LAST)] = 2
    k[(cid > CU_LAST) & (cid <= TIM_LAST)] = 3
    return k


def c1_of(idx, c1a, c1b):
    idx = np.asarray(idx, np.int64)
    out = np.zeros(idx.shape, np.int64)
    fid = idx + 1
    m = (fid >= 1) & (fid <= C1_IFACE_LAST)
    if np.any(m):
        out[m] = c1a[fid[m] - 1]
    m = (fid >= C1_INTERIOR_MIN) & (fid <= C1_INTERIOR_MAX)
    if np.any(m):
        out[m] = c1b[fid[m] - C1_INTERIOR_MIN]
    return out


def load_geometry():
    import h5py

    print("load geometry", flush=True)
    with h5py.File(CAS, "r") as fc:
        coords = np.asarray(fc["meshes/1/nodes/coords/1"][:], np.float32)
        fn = np.asarray(fc["meshes/1/faces/nodes/1/nodes"][:], np.uint32).reshape(-1, 4)
        c0 = np.asarray(fc["meshes/1/faces/c0/1"][:], np.uint32)
        c1a = np.asarray(fc["meshes/1/faces/c1/1"][:], np.uint32)
        c1b = np.asarray(fc["meshes/1/faces/c1/2"][:], np.uint32)
    print(
        "nodes", coords.shape[0],
        "faces", fn.shape[0],
        "xyz", float(coords[:, 0].min()), float(coords[:, 0].max()),
        float(coords[:, 1].min()), float(coords[:, 1].max()),
        float(coords[:, 2].min()), float(coords[:, 2].max()),
        flush=True,
    )
    return coords, fn, c0, c1a, c1b


def load_fields(step):
    import h5py

    dat = os.path.join(ROOT, "fluent", "uc01b_cht_less_12y_%s.dat.h5" % step)
    print("load fields", step, flush=True)
    with h5py.File(dat, "r") as fd:
        g = fd["results/1/phase-1/cells"]
        tcell = np.asarray(g["SV_T/1"][:], np.float32)
        ucell = np.asarray(g["SV_U/1"][:], np.float32)
        vcell = np.asarray(g["SV_V/1"][:], np.float32)
        wcell = np.asarray(g["SV_W/1"][:], np.float32)
    print("T", float(tcell.min()), float(tcell.max()), "U", float(np.max(np.abs(ucell))), flush=True)
    return tcell, ucell, vcell, wcell


def unique_axis(coords, axis):
    return np.unique(np.round(coords[:, axis].astype(np.float64), 6))


def snap(uniq, value, window=2.5e-4):
    j = int(np.argmin(np.abs(uniq - value)))
    got = float(uniq[j])
    if abs(got - value) > window:
        return None
    return got


# One mesh station only. The first boundary-layer cell is 2.5 µm, so a
# 5 µm window stacked several layers and the opaque quads looked shattered.
T_SCALE = (313.0, 342.0)
CMAP = "jet"


def collect_planes(fn, coord, targets, tol=1e-6):
    buckets = {t: [] for t in targets}
    n = fn.shape[0]
    chunk = 1_500_000
    for i0 in range(0, n, chunk):
        sl = fn[i0 : i0 + chunk].astype(np.int64) - 1
        vals = coord[sl]
        span = vals.max(axis=1) - vals.min(axis=1)
        mean = vals.mean(axis=1)
        flat = span < tol
        if not np.any(flat):
            continue
        for t in targets:
            m = flat & (np.abs(mean - t) < tol)
            if np.any(m):
                buckets[t].append(i0 + np.flatnonzero(m))
        if (i0 // chunk) % 8 == 0:
            print("  scan", i0, "/", n, flush=True)
    out = {}
    for t, parts in buckets.items():
        out[t] = np.concatenate(parts).astype(np.int64) if parts else np.empty(0, np.int64)
        print("  plane", t, "n", int(out[t].size), flush=True)
    return out


def pack_faces(idx, coords, fn, c0_all, c1a, c1b, fields):
    tcell, ucell, vcell, wcell = fields
    nodes = fn[idx].astype(np.int64) - 1
    xyz = coords[nodes]
    n = idx.shape[0]
    c0 = c0_all[idx].astype(np.int64)
    c1 = c1_of(idx, c1a, c1b)
    k0 = cell_kind(c0)
    k1 = cell_kind(c1)
    t = np.full(n, np.nan, np.float32)
    u = np.zeros(n, np.float32)
    v = np.zeros(n, np.float32)
    w = np.zeros(n, np.float32)
    kind = np.zeros(n, np.int8)

    both_f = (k0 == 1) & (k1 == 1)
    only0 = (k0 == 1) & (k1 != 1)
    only1 = (k1 == 1) & (k0 != 1)
    solid = (k0 >= 2) & (k1 != 1) & (k0 != 0)

    def put_t(mask, cid):
        t[mask] = tcell[cid[mask] - 1]

    if np.any(both_f):
        t[both_f] = 0.5 * (tcell[c0[both_f] - 1] + tcell[c1[both_f] - 1])
        u[both_f] = 0.5 * (ucell[c0[both_f] - 1] + ucell[c1[both_f] - 1])
        v[both_f] = 0.5 * (vcell[c0[both_f] - 1] + vcell[c1[both_f] - 1])
        w[both_f] = 0.5 * (wcell[c0[both_f] - 1] + wcell[c1[both_f] - 1])
        kind[both_f] = 1
    if np.any(only0):
        put_t(only0, c0)
        fluid = only0 & (c0 <= FLUID_LAST)
        u[fluid] = ucell[c0[fluid] - 1]
        v[fluid] = vcell[c0[fluid] - 1]
        w[fluid] = wcell[c0[fluid] - 1]
        kind[only0] = 1
    if np.any(only1):
        put_t(only1, c1)
        fluid = only1 & (c1 <= FLUID_LAST)
        u[fluid] = ucell[c1[fluid] - 1]
        v[fluid] = vcell[c1[fluid] - 1]
        w[fluid] = wcell[c1[fluid] - 1]
        kind[only1] = 1
    if np.any(solid):
        t0 = tcell[c0[solid] - 1]
        has1 = solid & (c1 > 0) & (k1 >= 2)
        t[solid] = t0
        if np.any(has1):
            t[has1] = 0.5 * (tcell[c0[has1] - 1] + tcell[c1[has1] - 1])
        kind[solid & ((k0 == 3) | (k1 == 3)) & (k0 != 2) & (k1 != 2)] = 3
        kind[solid & ((k0 == 2) | (k1 == 2))] = 2
    return xyz, t, u, v, w, kind


def zone_idx(name):
    a, b = ZONES[name]
    return np.arange(a - 1, b, dtype=np.int64)


def poly_mm(xyz, axes):
    return np.stack([xyz[:, :, axes[0]], xyz[:, :, axes[1]]], axis=2).astype(np.float64) * 1e3


def centroids(xyz, axes):
    c = xyz.mean(axis=1)
    return c[:, axes[0]] * 1e3, c[:, axes[1]] * 1e3


def figsize_for(span_h, span_v, panels=2):
    # A 0.4 mm jet across a 28.8 mm strip needs a wide panel or it becomes stripes.
    aspect = span_v / max(span_h, 0.05)
    panel_w = max(7.2, min(span_h * 0.45, 16.0))
    height = panel_w * aspect
    if height > 14:
        height = 14.0
        panel_w = height / max(aspect, 0.05)
    if height < 3.2:
        height = 3.2
    return (panel_w * panels + 1.8, height + 1.5)


def spans(verts):
    if verts.size == 0:
        return 1.0, 1.0
    h = float(verts[:, :, 0].max() - verts[:, :, 0].min())
    v = float(verts[:, :, 1].max() - verts[:, :, 1].min())
    return max(h, 0.05), max(v, 0.05)


def style(ax, xlabel, ylabel, title):
    ax.set_aspect("equal")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title, fontsize=10)
    ax.tick_params(labelsize=8)


def add_mesh_shade(ax, verts, values, norm, cmap):
    """Color the cut the way Fluent does: real quad corners, no new triangles
    across a gap. Each node takes the mean of the faces that touch it.
    """
    v = np.asarray(values, np.float64)
    if verts.shape[0] < 1 or not np.isfinite(v).any():
        return None
    pts = np.ascontiguousarray(verts.reshape(-1, 2))
    key = np.round(pts, 4)
    order = np.lexsort((key[:, 1], key[:, 0]))
    key_s = key[order]
    change = np.ones(len(key_s), dtype=bool)
    change[1:] = np.any(key_s[1:] != key_s[:-1], axis=1)
    gid_s = np.cumsum(change) - 1
    gid = np.empty(len(pts), dtype=np.int64)
    gid[order] = gid_s
    nnode = int(gid_s[-1]) + 1
    first = np.flatnonzero(change)
    xy = pts[order[first]]
    acc = np.zeros(nnode)
    cnt = np.zeros(nnode)
    np.add.at(acc, gid, np.repeat(v, 4))
    np.add.at(cnt, gid, 1.0)
    node_v = acc / np.maximum(cnt, 1.0)
    corners = gid.reshape(-1, 4)
    tris = np.empty((corners.shape[0] * 2, 3), np.int32)
    tris[0::2] = corners[:, [0, 1, 2]]
    tris[1::2] = corners[:, [0, 2, 3]]
    area = (
        (xy[tris[:, 1], 0] - xy[tris[:, 0], 0]) * (xy[tris[:, 2], 1] - xy[tris[:, 0], 1])
        - (xy[tris[:, 1], 1] - xy[tris[:, 0], 1]) * (xy[tris[:, 2], 0] - xy[tris[:, 0], 0])
    )
    keep = np.abs(area) > 1e-12
    if int(keep.sum()) < 1:
        return None
    tri = mtri.Triangulation(xy[:, 0], xy[:, 1], tris[keep])
    return ax.tripcolor(tri, node_v, shading="gouraud", cmap=cmap, norm=norm, rasterized=True)


def add_polys(ax, verts, values, norm, cmap):
    pc = PolyCollection(
        verts,
        array=np.asarray(values, np.float64),
        cmap=cmap,
        norm=norm,
        edgecolors="none",
        linewidths=0,
        antialiaseds=False,
        rasterized=True,
    )
    ax.add_collection(pc)
    return pc


def temp_limits(values):
    data_lo = float(np.nanmin(values))
    data_hi = float(np.nanmax(values))
    lo = min(T_SCALE[0], data_lo)
    hi = max(T_SCALE[1], data_hi)
    if hi <= lo:
        hi = lo + 1.0
    return data_lo, data_hi, lo, hi


def finish(ax, groups):
    xs, ys = [], []
    for g in groups:
        if g.size:
            xs.append(g[:, :, 0].ravel())
            ys.append(g[:, :, 1].ravel())
    if not xs:
        return
    x = np.concatenate(xs)
    y = np.concatenate(ys)
    pad_x = 0.02 * max(float(x.max() - x.min()), 0.1)
    pad_y = 0.02 * max(float(y.max() - y.min()), 0.1)
    ax.set_xlim(float(x.min()) - pad_x, float(x.max()) + pad_x)
    ax.set_ylim(float(y.min()) - pad_y, float(y.max()) + pad_y)


def quiver_grid(ax, a, b, u, v, n_a=32, n_b=16):
    if a.size < 8:
        return
    speed = np.hypot(u, v)
    ref = float(np.percentile(speed, 98))
    if ref < 1e-6:
        return
    lo_a, hi_a = float(a.min()), float(a.max())
    lo_b, hi_b = float(b.min()), float(b.max())
    if hi_a <= lo_a or hi_b <= lo_b:
        return
    ia = np.clip(((a - lo_a) / (hi_a - lo_a) * n_a).astype(np.int32), 0, n_a - 1)
    ib = np.clip(((b - lo_b) / (hi_b - lo_b) * n_b).astype(np.int32), 0, n_b - 1)
    key = ia * n_b + ib
    order = np.argsort(key)
    key = key[order]
    speed = speed[order]
    a, b, u, v = a[order], b[order], u[order], v[order]
    change = np.flatnonzero(np.diff(key)) + 1
    starts = np.r_[0, change]
    ends = np.r_[change, key.size]
    acc_a = np.add.reduceat(a, starts)
    acc_b = np.add.reduceat(b, starts)
    acc_u = np.add.reduceat(u, starts)
    acc_v = np.add.reduceat(v, starts)
    count = (ends - starts).astype(np.float64)
    ax.quiver(
        acc_a / count, acc_b / count, acc_u / count, acc_v / count,
        angles="xy", scale_units="xy", scale=None,
        width=0.003, color="#1a1a1a", alpha=0.85,
    )


def save(fig, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print("WROTE", path, flush=True)


def plot_scalar(path, title, xlabel, ylabel, verts, values, note):
    if verts.shape[0] < 8:
        print("SKIP", path, flush=True)
        return None
    finite = np.isfinite(values)
    verts, values = verts[finite], values[finite]
    data_lo, data_hi, lo, hi = temp_limits(values)
    norm = Normalize(lo, hi)
    sh, sv = spans(verts)
    fig, ax = plt.subplots(figsize=figsize_for(sh, sv, 1), dpi=110)
    if add_mesh_shade(ax, verts, values, norm, CMAP) is None:
        add_polys(ax, verts, values, norm, CMAP)
    finish(ax, [verts])
    cb = fig.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=CMAP), ax=ax, fraction=0.046, pad=0.02)
    cb.set_label("T (K)")
    style(ax, xlabel, ylabel, title)
    fig.text(0.01, 0.01, note + "  温度色标固定 313–342 K，与 Fluent 一致。", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    save(fig, path)
    return data_lo, data_hi, int(values.size)


def plot_tv(path, title, xlabel, ylabel, xyz, t, u, v, w, kind, plane_axes, comp, note, crop=None):
    fluid = kind == 1
    solid = kind >= 2
    if crop is not None:
        axis, lo, hi = crop
        c = xyz.mean(axis=1)[:, axis]
        keep = (c >= lo) & (c <= hi)
        fluid = fluid & keep
        solid = solid & keep
    if int(fluid.sum()) < 20 and int(solid.sum()) < 20:
        print("SKIP", path, "fluid", int(fluid.sum()), "solid", int(solid.sum()), flush=True)
        return None
    comp_map = {"u": u, "v": v, "w": w}
    rec = {"n_fluid": int(fluid.sum()), "n_solid": int(solid.sum())}
    water_v = poly_mm(xyz[fluid], plane_axes) if np.any(fluid) else np.zeros((0, 4, 2))
    solid_v = poly_mm(xyz[solid], plane_axes) if np.any(solid) else np.zeros((0, 4, 2))
    groups = []
    t_water = t[fluid] if np.any(fluid) else np.zeros(0)
    t_solid = t[solid] if np.any(solid) else np.zeros(0)
    parts = []
    if t_water.size:
        parts.append(t_water)
        rec["tmin"] = float(t_water.min())
        rec["tmax"] = float(t_water.max())
    if t_solid.size:
        parts.append(t_solid)
        rec["solid_tmin"] = float(t_solid.min())
        rec["solid_tmax"] = float(t_solid.max())
    both = np.concatenate(parts) if parts else np.zeros(1)
    _dlo, _dhi, lo, hi = temp_limits(both)
    tnorm = Normalize(lo, hi)
    if water_v.shape[0]:
        uu = comp_map[comp[0]][fluid]
        vv = comp_map[comp[1]][fluid]
        sp = np.sqrt(u[fluid] ** 2 + v[fluid] ** 2 + w[fluid] ** 2)
        rec["vmax"] = float(sp.max())
        rec["vin"] = float(np.hypot(uu, vv).max())
        vlo, vhi = 0.0, max(rec["vmax"], 1e-4)
        vnorm = Normalize(vlo, vhi)
        a, b = centroids(xyz[fluid], plane_axes)
    else:
        uu = vv = sp = a = b = None
        vnorm = Normalize(0, 1)
        rec["vmax"] = 0.0
    shown = [g for g in (water_v, solid_v) if g.shape[0]]
    sh, sv = spans(np.concatenate(shown, axis=0))
    fig, axes = plt.subplots(1, 2, figsize=figsize_for(sh, sv, 2), dpi=110, sharex=True, sharey=True)
    ax_t, ax_v = axes
    if solid_v.shape[0]:
        if add_mesh_shade(ax_t, solid_v, t_solid, tnorm, "turbo") is None:
            add_polys(ax_t, solid_v, t_solid, tnorm, "turbo")
        solid_flat = PolyCollection(solid_v, facecolors="#e4e4e4", edgecolors="none", antialiaseds=False)
        ax_v.add_collection(solid_flat)
    if water_v.shape[0]:
        if add_mesh_shade(ax_t, water_v, t_water, tnorm, "turbo") is None:
            add_polys(ax_t, water_v, t_water, tnorm, "turbo")
        if add_mesh_shade(ax_v, water_v, sp, vnorm, "viridis") is None:
            add_polys(ax_v, water_v, sp, vnorm, "viridis")
        quiver_grid(ax_t, a, b, uu, vv)
        quiver_grid(ax_v, a, b, uu, vv)
    finish(ax_t, shown)
    finish(ax_v, shown)
    fig.colorbar(plt.cm.ScalarMappable(norm=tnorm, cmap="turbo"), ax=ax_t, fraction=0.046, pad=0.02).set_label("T (K)")
    fig.colorbar(plt.cm.ScalarMappable(norm=vnorm, cmap="viridis"), ax=ax_v, fraction=0.046, pad=0.02).set_label("|V| (m/s)")
    style(ax_t, xlabel, ylabel, "温度  流体与固体同一色标")
    style(ax_v, xlabel, ylabel, "速度 |V|")
    fig.suptitle(title, fontsize=11)
    fig.text(0.01, 0.005, note + "  温度色标固定 313–343 K。", fontsize=8)
    fig.tight_layout(rect=(0, 0.03, 1, 0.94))
    save(fig, path)
    return rec


def plot_mesh(path, title, xlabel, ylabel, verts, xlim=None, ylim=None):
    if verts.shape[0] < 8:
        print("SKIP", path, flush=True)
        return 0
    # edges of each quad
    e = np.stack([
        verts[:, [0, 1], :],
        verts[:, [1, 2], :],
        verts[:, [2, 3], :],
        verts[:, [3, 0], :],
    ], axis=1).reshape(-1, 2, 2)
    sh, sv = spans(verts)
    fig, ax = plt.subplots(figsize=figsize_for(sh, sv, 1), dpi=120)
    ax.add_collection(LineCollection(e, colors="#243044", linewidths=0.2, rasterized=True))
    finish(ax, [verts])
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    style(ax, xlabel, ylabel, title)
    fig.tight_layout()
    save(fig, path)
    return int(verts.shape[0])


def window(xyz, mask, axis, lo, hi):
    if not np.any(mask):
        return mask
    c = xyz.mean(axis=1)[:, axis]
    return mask & (c >= lo) & (c <= hi)


def main():
    plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False
    steps = sys.argv[1:] or ["i300", "i600"]
    coords, fn, c0, c1a, c1b, = load_geometry()
    ux = unique_axis(coords, 0)
    uy = unique_axis(coords, 1)
    uz = unique_axis(coords, 2)
    print("nunique", ux.size, uy.size, uz.size, flush=True)

    def use(uniq, value):
        got = snap(uniq, value)
        print("SNAP", value, "->", got, flush=True)
        return got

    x_ask = {"x0": 0.0, "x04": 0.4e-3, "xmid": 0.566e-3, "x11": 1.1e-3, "x13": 1.3e-3}
    y_ask = {
        "y_local0": Y_LOCAL["y0"],
        "y_local04": Y_LOCAL["y04"],
        "y_local08": Y_LOCAL["yside"],
        "y_local10": Y_LOCAL["y10"],
        "y_glob0": 0.0,
        "y_glob04": 0.4e-3,
        "y_glob08": 0.8e-3,
        "y_glob10": 1.0e-3,
    }
    z_ask = {
        "ztim": -2.0364e-3,
        "ztimcu": -2.0e-3,
        "zcu": -1.028e-3,
        "z0": 0.0,
        "z015": 0.217e-3,
        "zmid": 0.674e-3,
        "zrib": 1.5e-3,
        "zgap": 2.5e-3,
        "z35": 3.5e-3,
        "zorif": 4.75e-3,
        "z70": 7.0e-3,
    }
    x_val = {k: use(ux, v) for k, v in x_ask.items()}
    y_val = {k: use(uy, v) for k, v in y_ask.items()}
    z_val = {k: use(uz, v) for k, v in z_ask.items()}
    if z_val["z70"] is None:
        # nearest plane at or below 7 mm, still inside the mesh
        below = uz[uz <= 7.0e-3 + 1e-9]
        z_val["z70"] = float(below[-1]) if below.size else None
        print("SNAP z70 fallback", z_val["z70"], flush=True)

    print("scan X", flush=True)
    x_idx = collect_planes(fn, coords[:, 0], [v for v in x_val.values() if v is not None])
    print("scan Y", flush=True)
    y_idx = collect_planes(fn, coords[:, 1], [v for v in y_val.values() if v is not None])
    print("scan Z", flush=True)
    z_idx = collect_planes(fn, coords[:, 2], [v for v in z_val.values() if v is not None])

    def faces(table, value):
        if value is None:
            return np.empty(0, np.int64)
        return table.get(value, np.empty(0, np.int64))

    mesh_done = False
    for step in steps:
        fields = load_fields(step)
        outdir = os.path.join(FIGS, step)
        os.makedirs(outdir, exist_ok=True)
        ranges = {"step": step, "order": "first" if step == "i300" else "second", "planes": {}}
        tag = "iter 300  一阶" if step == "i300" else "iter 600  二阶"

        def remember(stem, **kw):
            ranges["planes"][stem] = kw
            print("RANGE", step, stem, kw, flush=True)

        def grab(idx):
            return pack_faces(idx, coords, fn, c0, c1a, c1b, fields)

        # --- scalars that match section 2 and the solid cuts in section 5 ---
        def solid_cut(stem, idx, kind_want, title, note, center=False):
            # Use the solid cell on each face. A copper–water face is kept,
            # colored by the copper (or TIM) cell, not by the water.
            if idx.size < 8:
                print("SKIP", stem, flush=True)
                return
            nodes = fn[idx].astype(np.int64) - 1
            xyz = coords[nodes]
            c0s = c0[idx].astype(np.int64)
            c1s = c1_of(idx, c1a, c1b)
            k0 = cell_kind(c0s)
            k1 = cell_kind(c1s)
            tcell = fields[0]
            want = np.isin(k0, kind_want) | np.isin(k1, kind_want)
            t = np.full(idx.shape[0], np.nan, np.float32)
            use0 = want & np.isin(k0, kind_want)
            use1 = want & np.isin(k1, kind_want) & ~use0
            both = want & np.isin(k0, kind_want) & np.isin(k1, kind_want)
            t[use0] = tcell[c0s[use0] - 1]
            t[use1] = tcell[c1s[use1] - 1]
            if np.any(both):
                t[both] = 0.5 * (tcell[c0s[both] - 1] + tcell[c1s[both] - 1])
            m = want & np.isfinite(t)
            if center:
                m = window(xyz, m, 1, CELL_Y0, CELL_Y1)
                stem = stem + "_center"
                title = title + "  中部单元 Y=0–2.4 mm"
            verts = poly_mm(xyz[m], (0, 1))
            got = plot_scalar(
                os.path.join(outdir, stem + ".png"),
                "%s  %s" % (tag, title),
                "X mm", "Y mm", verts, t[m], note,
            )
            if got:
                remember(stem, tmin=got[0], tmax=got[1], n=got[2], kind="scalar")

        xyz, t, u, v, w, kind = grab(zone_idx("wall_heat"))
        tmean = float(np.nanmean(t))
        print("SANITY wall_heat cell T", tmean, "kind", int(kind.min()), int(kind.max()), flush=True)
        if not (320.0 < tmean < 360.0):
            raise SystemExit("wall_heat temperature %.3f is outside 320–360 K; c0/c1 map is wrong" % tmean)
        got = plot_scalar(
            os.path.join(outdir, "wall_heat_T.png"),
            "%s  TIM 底面 wall_heat" % tag,
            "X mm", "Y mm", poly_mm(xyz, (0, 1)), t,
            "着色是邻接 TIM 单元温度。表中面积加权是 Fluent 面温度。",
        )
        if got:
            remember("wall_heat_T", tmin=got[0], tmax=got[1], n=got[2], kind="scalar")
        m = window(xyz, np.ones(kind.shape[0], bool), 1, CELL_Y0, CELL_Y1)
        got = plot_scalar(
            os.path.join(outdir, "wall_heat_T_center.png"),
            "%s  TIM 底面  中部单元 Y=0–2.4 mm" % tag,
            "X mm", "Y mm", poly_mm(xyz[m], (0, 1)), t[m],
            "与单胞整面同尺度的局部。12 格全长见图 wall_heat_T。",
        )
        if got:
            remember("wall_heat_T_center", tmin=got[0], tmax=got[1], n=got[2], kind="scalar")

        solid_cut("ztim_mid_T", faces(z_idx, z_val["ztim"]), (3,), "TIM 中面", "固体 TIM。")
        solid_cut("ztim_mid_T", faces(z_idx, z_val["ztim"]), (3,), "TIM 中面", "固体 TIM。", center=True)
        solid_cut("ztimcu_T", faces(z_idx, z_val["ztimcu"]), (2, 3), "TIM–Cu  z=-2.000 mm", "界面两侧单元温度平均。")
        solid_cut("ztimcu_T", faces(z_idx, z_val["ztimcu"]), (2, 3), "TIM–Cu", "界面。", center=True)
        solid_cut("zcu_mid_T", faces(z_idx, z_val["zcu"]), (2,), "铜座中面", "固体铜。")
        solid_cut("zcu_mid_T", faces(z_idx, z_val["zcu"]), (2,), "铜座中面", "固体铜。", center=True)
        solid_cut("z0_T", faces(z_idx, z_val["z0"]), (2,), "铜–水底面固体  z=0", "只画铜。槽内的水在 zmid_TV。")
        solid_cut("z0_T", faces(z_idx, z_val["z0"]), (2,), "铜–水底面固体  z=0", "只画铜。", center=True)
        solid_cut("zrib_mid_T", faces(z_idx, z_val["zmid"]), (2,), "肋中固体", "只画铜肋。")
        solid_cut("zrib_mid_T", faces(z_idx, z_val["zmid"]), (2,), "肋中固体", "只画铜肋。", center=True)
        solid_cut("zrib_solid_T", faces(z_idx, z_val["zrib"]), (2,), "肋顶固体  z=1.500 mm", "只画铜。")
        solid_cut("zrib_solid_T", faces(z_idx, z_val["zrib"]), (2,), "肋顶固体", "只画铜。", center=True)

        crop_y = (1, CELL_Y0, CELL_Y1)

        def tv_cut(stem, idx, axes, cu, cv, xlabel, ylabel, title, note, crop=None, mask=None):
            if idx.size < 8:
                print("SKIP", stem, flush=True)
                return
            xyz, t, u, v, w, kind = grab(idx)
            if mask is not None:
                keep = mask(xyz, kind)
                xyz, t, u, v, w, kind = xyz[keep], t[keep], u[keep], v[keep], w[keep], kind[keep]
            use_stem = stem + ("_center" if crop else "")
            use_title = title + ("  中部单元" if crop else "")
            rec = plot_tv(
                os.path.join(outdir, use_stem + ".png"),
                "%s  %s" % (tag, use_title),
                xlabel, ylabel, xyz, t, u, v, w, kind, axes, (cu, cv), note, crop=crop,
            )
            if rec:
                rec["kind"] = "tv"
                remember(use_stem, **rec)

        def slit_mask(lo_z_note=None):
            def _m(xyz, kind):
                xc = np.abs(xyz.mean(axis=1)[:, 0])
                return (kind == 1) & (xc >= 1.10e-3 - 1e-6)
            return _m

        tv_cut("zmid_TV", faces(z_idx, z_val["zmid"]), (0, 1), "u", "v", "X mm", "Y mm",
               "槽中水  z=%.3f mm" % ((z_val["zmid"] or 0) * 1e3), "流体与固体同一温度色标。")
        tv_cut("zmid_TV", faces(z_idx, z_val["zmid"]), (0, 1), "u", "v", "X mm", "Y mm",
               "槽中水", "中部单元。", crop=crop_y)
        tv_cut("zgap_TV", faces(z_idx, z_val["zgap"]), (0, 1), "u", "v", "X mm", "Y mm",
               "间隙水  z=2.500 mm", "z=2.500 mm。")
        tv_cut("zgap_TV", faces(z_idx, z_val["zgap"]), (0, 1), "u", "v", "X mm", "Y mm",
               "间隙水  z=2.500 mm", "中部单元。", crop=crop_y)
        tv_cut("zorif_TV", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "圆孔水  z=%.3f mm" % ((z_val["zorif"] or 0) * 1e3), "喷孔与导流槽。")
        tv_cut("zorif_TV", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "圆孔水", "中部单元。", crop=crop_y)
        tv_cut("zorif_slot_vel", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "喷孔与出流导流槽  速度与温度", "左图温度，右图速度。对应单胞图 5-6。")
        tv_cut("zorif_slot_vel", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "喷孔与出流导流槽", "中部单元。", crop=crop_y)
        tv_cut("slitin_TV", faces(z_idx, z_val["z35"]), (0, 1), "u", "v", "X mm", "Y mm",
               "回液缝入口  z=3.500 mm  |X|≥1.10 mm", "间隙顶进入 ±X 回液缝。", mask=slit_mask())
        tv_cut("slitin_TV", faces(z_idx, z_val["z35"]), (0, 1), "u", "v", "X mm", "Y mm",
               "回液缝入口", "中部单元。", crop=crop_y, mask=slit_mask())
        tv_cut("zreturn_mid_TV", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "回液缝中段  z=%.3f mm  |X|≥1.10 mm" % ((z_val["zorif"] or 0) * 1e3),
               "只保留缝内的水。", mask=slit_mask())
        tv_cut("zreturn_mid_TV", faces(z_idx, z_val["zorif"]), (0, 1), "u", "v", "X mm", "Y mm",
               "回液缝中段", "中部单元。", crop=crop_y, mask=slit_mask())

        xyz, t, u, v, w, kind = grab(zone_idx("return_slot"))
        rec = plot_tv(
            os.path.join(outdir, "return_TV.png"),
            "%s  return_slot  本算例为绝热壁" % tag,
            "X mm", "Y mm", xyz, t, u, v, w, kind, (0, 1), ("u", "v"),
            "Z 顶面已改为壁面，不是压力出口。流体从 Y 两端 outlet_y 离开。",
        )
        if rec:
            rec["kind"] = "tv"
            remember("return_TV", **rec)

        y_cuts = [
            ("y0_TV", "y_local0", "中槽  全局 Y=1.200 mm（对应单胞 Y=0）"),
            ("yside_TV", "y_local08", "侧槽  全局 Y=2.000 mm（对应单胞 Y=0.800 mm）"),
            ("y04_TV", "y_local04", "肋中  全局 Y=1.600 mm（对应单胞 Y=0.400 mm）"),
            ("y10_TV", "y_local10", "侧槽中心  全局 Y=2.200 mm（对应单胞 Y=1.000 mm）"),
            ("y0_global_TV", "y_glob0", "全局 Y=0  单元交界（12 格拼接面）"),
            ("y04_global_TV", "y_glob04", "全局 Y=0.400 mm"),
            ("yside_global_TV", "y_glob08", "全局 Y=0.800 mm"),
            ("y10_global_TV", "y_glob10", "全局 Y=1.000 mm"),
        ]
        for stem, key, title in y_cuts:
            tv_cut(stem, faces(y_idx, y_val[key]), (0, 2), "u", "w", "X mm", "Z mm", title, title)

        x_cuts = [
            ("x0_TV", "x0", "X=0"),
            ("xmid_TV", "xmid", "X=0.566 mm"),
            ("x13_TV", "x13", "X=1.300 mm"),
            ("x04_TV", "x04", "X=0.400 mm  孔外槽内"),
            ("x11_TV", "x11", "X=1.100 mm  回液缝唇"),
        ]
        for stem, key, title in x_cuts:
            tv_cut(stem, faces(x_idx, x_val[key]), (1, 2), "v", "w", "Y mm", "Z mm", title, title)
            tv_cut(stem, faces(x_idx, x_val[key]), (1, 2), "v", "w", "Y mm", "Z mm", title, "中部单元。", crop=crop_y)

        z_tv = [
            ("z015_TV", "z015", "z=0.217 mm  驻点上方"),
            ("z35_TV", "z35", "z=3.500 mm  间隙顶全平面"),
            ("z70_TV", "z70", "上腔孔断面  实际 z=%.3f mm" % ((z_val["z70"] or 0) * 1e3)),
        ]
        for stem, key, title in z_tv:
            tv_cut(stem, faces(z_idx, z_val[key]), (0, 1), "u", "v", "X mm", "Y mm", title, title)
            tv_cut(stem, faces(z_idx, z_val[key]), (0, 1), "u", "v", "X mm", "Y mm", title, "中部单元。", crop=crop_y)

        for stem, zone, title in (
            ("outlet_y_front_TV", "outlet_y_front", "Y 正端压力出口 outlet_y_front"),
            ("outlet_y_back_TV", "outlet_y_back", "Y 负端压力出口 outlet_y_back"),
        ):
            xyz, t, u, v, w, kind = grab(zone_idx(zone))
            rec = plot_tv(
                os.path.join(outdir, stem + ".png"),
                "%s  %s" % (tag, title),
                "X mm", "Z mm", xyz, t, u, v, w, kind, (0, 2), ("u", "w"),
                "12 格的流体出口。单胞报告里的出口是 return_slot，本算例不是。",
            )
            if rec:
                rec["kind"] = "tv"
                remember(stem, **rec)

        path = os.path.join(FIGS, "ranges_%s.json" % step)
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(ranges, fh, ensure_ascii=False, indent=2)
        print("RANGES", path, flush=True)

        if mesh_done:
            continue
        mesh_done = True
        mdir = os.path.join(FIGS, "mesh")
        os.makedirs(mdir, exist_ok=True)

        def mesh_zone(stem, idx, axes, xlabel, ylabel, title, center=False, xlim=None, ylim=None, kind_keep=None):
            if idx.size < 8:
                print("SKIP mesh", stem, flush=True)
                return
            if center or xlim or ylim or kind_keep is not None:
                xyz, t, u, v, w, kind = grab(idx)
                m = np.ones(kind.shape[0], bool)
                if kind_keep is not None:
                    m = np.isin(kind, kind_keep)
                if center:
                    m = window(xyz, m, 1, CELL_Y0, CELL_Y1)
                verts = poly_mm(xyz[m], axes)
            else:
                nodes = fn[idx].astype(np.int64) - 1
                verts = poly_mm(coords[nodes], axes)
            n = plot_mesh(os.path.join(mdir, stem + ".png"), "网格  " + title, xlabel, ylabel, verts, xlim, ylim)
            remember_mesh(stem, n)

        mesh_meta = {}

        def remember_mesh(stem, n):
            mesh_meta[stem] = n
            print("MESH", stem, n, flush=True)

        # The seven original mesh views, framed on one cell so the lines stay readable,
        # plus the full strip and the Y=0 join where the boundary layer became uniform.
        mesh_zone("mesh_wall_heat", zone_idx("wall_heat"), (0, 1), "X mm", "Y mm",
                  "TIM 底面 wall_heat  中部单元", center=True)
        mesh_zone("mesh_wall_heat_full", zone_idx("wall_heat"), (0, 1), "X mm", "Y mm",
                  "TIM 底面 wall_heat  12 格全长")
        mesh_zone("mesh_z_floor", faces(z_idx, z_val["z0"]), (0, 1), "X mm", "Y mm",
                  "铜–水底面 z=0  中部单元", center=True)
        mesh_zone("mesh_z_rib", faces(z_idx, z_val["zrib"]), (0, 1), "X mm", "Y mm",
                  "肋顶平面 z=1.500 mm  中部单元", center=True)
        mesh_zone("mesh_z_orifice", faces(z_idx, z_val["zorif"]), (0, 1), "X mm", "Y mm",
                  "孔板 z=%.3f mm  中部单元" % ((z_val["zorif"] or 0) * 1e3), center=True)
        mesh_zone("mesh_x0", faces(x_idx, x_val["x0"]), (1, 2), "Y mm", "Z mm",
                  "X=0  中部单元", center=True)
        mesh_zone("mesh_x0_full", faces(x_idx, x_val["x0"]), (1, 2), "Y mm", "Z mm",
                  "X=0  12 格全长")
        mesh_zone("mesh_y0", faces(y_idx, y_val["y_local0"]), (0, 2), "X mm", "Z mm",
                  "中槽竖直切面  全局 Y=1.200 mm（对应单胞 Y=0）")
        # boundary-layer zoom on that center-slot cut
        xyz, t, u, v, w, kind = grab(faces(y_idx, y_val["y_local0"]))
        verts = poly_mm(xyz, (0, 2))
        plot_mesh(
            os.path.join(mdir, "mesh_y0_bl.png"),
            "网格  中槽 Y=1.200 mm  铜–水底面附近",
            "X mm", "Z mm", verts, xlim=(-0.35, 0.35), ylim=(-0.08, 0.18),
        )
        xyz, t, u, v, w, kind = grab(faces(y_idx, y_val["y_glob0"]))
        verts = poly_mm(xyz, (0, 2))
        plot_mesh(
            os.path.join(mdir, "mesh_y_join.png"),
            "网格  全局 Y=0  单元交界",
            "X mm", "Z mm", verts,
        )
        plot_mesh(
            os.path.join(mdir, "mesh_y_join_bl.png"),
            "网格  全局 Y=0 交界  底面附近（半肋边界层已改为均匀网格）",
            "X mm", "Z mm", verts, xlim=(-0.45, 0.45), ylim=(-0.08, 0.25),
        )
        with open(os.path.join(FIGS, "mesh_counts.json"), "w", encoding="utf-8") as fh:
            json.dump(mesh_meta, fh, indent=2)
        print("MESH DONE", flush=True)

    print("ALL DONE", flush=True)


if __name__ == "__main__":
    main()
