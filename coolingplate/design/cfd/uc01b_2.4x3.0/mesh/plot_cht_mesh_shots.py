# -*- coding: utf-8 -*-
"""Real CHT mesh screenshots (cell edges). Not CFD contours. Not a cartoon.

Source: write_cht_circle_msh.py medium == mesh/uc01b_cht_medium.msh
(metres in the msh; plots labelled in mm for readability).
Do not launch Fluent / ICEM.
"""
from __future__ import annotations

import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection, PolyCollection
from matplotlib.patches import FancyBboxPatch

for _fn in ("Microsoft YaHei", "SimHei", "Source Han Sans CN"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ.setdefault("UC01B_MESH", "fine")
PREFIX = os.environ.get("UC01B_FIG_PREFIX", "fine_")
from write_cht_circle_msh import (  # noqa: E402
    CU,
    D,
    FLUID,
    LEVELS,
    R,
    TIM,
    X0,
    X1,
    Y0,
    Y1,
    Z_CU_BOT,
    Z_IMP,
    Z_LID,
    Z_LIDTOP,
    Z_RIB,
    Z_TIM_BOT,
    build_xy,
    zone_of,
    z_axis,
)

OUT = os.path.join(os.path.dirname(HERE), "figs")
os.makedirs(OUT, exist_ok=True)

FACE = {FLUID: "#8ec8e8", CU: "#e0c15a", TIM: "#d4655a"}
EDGE = {FLUID: "#1a5276", CU: "#7d6608", TIM: "#7b241c"}
LABEL = {FLUID: "water", CU: "Cu", TIM: "TIM"}


def clip_interval(pts, axis, val, eps=1e-10):
    """Return (lo, hi) of the other XY coord where the quad meets axis=val."""
    # pts: 4 (x,y). axis 0=X plane (return Y), axis 1=Y plane (return X)
    ys = []
    for i in range(4):
        p, q = pts[i], pts[(i + 1) % 4]
        a0, a1 = p[axis], q[axis]
        b0, b1 = p[1 - axis], q[1 - axis]
        if abs(a0 - val) <= eps:
            ys.append(b0)
        if (a0 - val) * (a1 - val) < 0:
            t = (val - a0) / (a1 - a0)
            ys.append(b0 + t * (b1 - b0))
    if len(ys) < 2:
        return None
    lo, hi = min(ys), max(ys)
    if hi - lo < 1e-12:
        return None
    return lo, hi


def iso_xy(x, y, z):
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    return (x - y) * c, z + (x + y) * s


def add_scale(ax, x0, y0, length, label, horizontal=True):
    if horizontal:
        ax.plot([x0, x0 + length], [y0, y0], color="#222", lw=1.4)
        ax.plot([x0, x0], [y0 - 0.02 * length, y0 + 0.02 * length], color="#222", lw=1.2)
        ax.plot([x0 + length, x0 + length], [y0 - 0.02 * length, y0 + 0.02 * length],
                color="#222", lw=1.2)
        ax.text(x0 + 0.5 * length, y0, "\n" + label, ha="center", va="top", fontsize=8, color="#222")
    else:
        ax.plot([x0, x0], [y0, y0 + length], color="#222", lw=1.4)
        ax.text(x0, y0 + 0.5 * length, "  " + label, ha="left", va="center", fontsize=8, color="#222")


def legend_patches(ax):
    from matplotlib.patches import Patch
    ax.legend(
        handles=[Patch(facecolor=FACE[k], edgecolor=EDGE[k], label=LABEL[k])
                 for k in (FLUID, CU, TIM)],
        loc="upper right", fontsize=8, framealpha=0.92,
    )


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p, os.path.getsize(p))
    return p


def build():
    lv = LEVELS["medium"]
    xy = build_xy(lv)
    z = z_axis(lv)
    quads = []
    for n0, n1, n2, n3 in xy.quads:
        pts = (xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3])
        xc = 0.25 * (pts[0][0] + pts[1][0] + pts[2][0] + pts[3][0])
        yc = 0.25 * (pts[0][1] + pts[1][1] + pts[2][1] + pts[3][1])
        quads.append((pts, xc, yc))
    nz = len(z) - 1
    kinds = []
    counts = {FLUID: 0, CU: 0, TIM: 0}
    for pts, xc, yc in quads:
        row = []
        for k in range(nz):
            zn = zone_of(xc, yc, 0.5 * (z[k] + z[k + 1]))
            row.append(zn)
            if zn:
                counts[zn] += 1
        kinds.append(row)
    dz_imp = None
    for a, b in zip(z, z[1:]):
        if abs(a - Z_IMP) < 1e-12:
            dz_imp = b - a
            break
    info = {
        "level": os.environ.get("UC01B_MESH", "fine"),
        "n_quads": len(quads),
        "nz": nz,
        "n_cells": sum(counts.values()),
        "n_fluid": counts[FLUID],
        "n_cu": counts[CU],
        "n_tim": counts[TIM],
        "first_imp_mm": dz_imp,
        "n_bl": lv["n_bl"],
        "nz_tim": lv["nz_tim"],
        "nz_cu": lv["nz_cu"],
        "h_orif": lv["h_orif"],
        "D": D,
        "msh": os.path.join(HERE, f"uc01b_cht_{os.environ.get('UC01B_MESH', 'fine')}.msh"),
    }
    return xy, z, quads, kinds, info


def plane_cells(quads, kinds, z, axis, val):
    """Cells cut by X=val (axis=0, coords YZ) or Y=val (axis=1, coords XZ)."""
    polys = {FLUID: [], CU: [], TIM: []}
    n = 0
    for (pts, _xc, _yc), row in zip(quads, kinds):
        iv = clip_interval(pts, axis, val)
        if iv is None:
            continue
        a, b = iv
        for k, zn in enumerate(row):
            if not zn:
                continue
            z0, z1 = z[k], z[k + 1]
            polys[zn].append([(a, z0), (b, z0), (b, z1), (a, z1)])
            n += 1
    return polys, n


def z_layer_cells(quads, kinds, z, zc_target):
    zs = [0.5 * (z[k] + z[k + 1]) for k in range(len(z) - 1)]
    k = min(range(len(zs)), key=lambda i: abs(zs[i] - zc_target))
    polys = {FLUID: [], CU: [], TIM: []}
    n = 0
    for (pts, _xc, _yc), row in zip(quads, kinds):
        zn = row[k]
        if not zn:
            continue
        polys[zn].append(list(pts))
        n += 1
    return polys, n, zs[k], k


def draw_polys(ax, groups, lw=0.22, alpha=0.72):
    for zn in (TIM, CU, FLUID):
        if not groups[zn]:
            continue
        pc = PolyCollection(
            groups[zn],
            facecolors=FACE[zn],
            edgecolors=EDGE[zn],
            linewidths=lw,
            alpha=alpha,
        )
        ax.add_collection(pc)


def finish_2d(ax, title, xl, yl, xlim, ylim, scale_at, scale_len, scale_lab):
    ax.set_title(title, fontsize=11)
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    add_scale(ax, scale_at[0], scale_at[1], scale_len, scale_lab)
    legend_patches(ax)
    ax.grid(False)


def plot_cut_yz(quads, kinds, z, info):
    groups, n = plane_cells(quads, kinds, z, 0, 0.0)
    fig, ax = plt.subplots(figsize=(8.6, 9.2), dpi=140)
    draw_polys(ax, groups, lw=0.18)
    finish_2d(
        ax,
        f"X=0 mesh cut  (through jet / YZ)   {n} HEXA faces\n"
        f"{info['level']} {info['n_cells']} HEXA  msh metres  plot mm  NOT a CFD contour",
        "Y mm", "Z mm",
        (-1.28, 1.28), (Z_TIM_BOT - 0.15, 8.25),
        (-1.15, -1.85), 0.40, "0.40 mm",
    )
    ax.annotate("inlet D=0.40", xy=(0.0, 7.6), fontsize=8, ha="center", color="#0e6655")
    ax.annotate("q'' TIM bottom", xy=(0.0, Z_TIM_BOT - 0.02), fontsize=8, ha="center",
                color="#7b241c", va="top")
    return save(fig, PREFIX + "mesh_cut_x0.png"), n


def plot_cut_xz(quads, kinds, z, info):
    groups, n = plane_cells(quads, kinds, z, 1, 0.0)
    fig, ax = plt.subplots(figsize=(8.8, 9.2), dpi=140)
    draw_polys(ax, groups, lw=0.18)
    finish_2d(
        ax,
        f"Y=0 mesh cut  (through jet / XZ)   {n} HEXA faces\n"
        f"{info['level']} {info['n_cells']} HEXA  msh metres  plot mm  NOT a CFD contour",
        "X mm", "Z mm",
        (-1.58, 1.58), (Z_TIM_BOT - 0.15, 8.25),
        (-1.45, -1.85), 0.40, "0.40 mm",
    )
    ax.annotate("return", xy=(-1.30, 4.6), fontsize=8, color="#a04000")
    ax.annotate("return", xy=(1.15, 4.6), fontsize=8, color="#a04000")
    return save(fig, PREFIX + "mesh_cut_y0.png"), n


def plot_zcut(quads, kinds, z, zc, fname, title_zh, info):
    groups, n, zc_used, k = z_layer_cells(quads, kinds, z, zc)
    fig, ax = plt.subplots(figsize=(8.2, 6.8), dpi=140)
    draw_polys(ax, groups, lw=0.20)
    finish_2d(
        ax,
        f"{title_zh}   zc={zc_used:.4f} mm  layer k={k}   {n} quads\n"
        f"{info['level']} {info['n_cells']} HEXA  msh metres  plot mm  NOT a CFD contour",
        "X mm", "Y mm",
        (-1.58, 1.58), (-1.28, 1.28),
        (-1.45, -1.12), 0.40, "0.40 mm",
    )
    th = [i * 2 * math.pi / 180 for i in range(181)]
    ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
            color="#c0392b", lw=0.9, ls="--", label="r=0.20")
    return save(fig, fname), n, zc_used


def plot_bl_zoom(quads, kinds, z, info):
    g_imp, n_imp = plane_cells(quads, kinds, z, 0, 0.0)
    g_lip, n_orif, zc_orif, _k = z_layer_cells(quads, kinds, z, 0.5 * (Z_LID + Z_LIDTOP))

    fig, axes = plt.subplots(1, 2, figsize=(11.2, 5.4), dpi=150)

    ax = axes[0]
    # keep only cells near impact (center slot)
    clipped = {zn: [p for p in g_imp[zn]
                    if abs(0.5 * (p[0][0] + p[1][0])) < 0.22
                    and p[0][1] < 0.12 and p[2][1] > -0.04]
               for zn in g_imp}
    n0 = sum(len(v) for v in clipped.values())
    draw_polys(ax, clipped, lw=0.45, alpha=0.8)
    ax.axhline(Z_IMP, color="#444", lw=0.6, ls=":")
    dz = info["first_imp_mm"]
    if dz:
        ax.annotate(
            f"first Δz = {dz * 1000:.1f} μm",
            xy=(0.02, Z_IMP + 0.5 * dz),
            xytext=(0.08, 0.035),
            fontsize=8, color="#1a5276",
            arrowprops=dict(arrowstyle="->", color="#1a5276", lw=0.8),
        )
    finish_2d(
        ax,
        f"Impact BL  X=0  |Y|<0.22  z≈0\n{n0} cut cells   target Δy≤3 μm",
        "Y mm", "Z mm",
        (-0.22, 0.22), (-0.035, 0.085),
        (-0.20, -0.028), 0.05, "50 μm",
    )

    ax = axes[1]
    clipped = {zn: [p for p in g_lip[zn] if max(abs(q[0]) for q in p) < 0.36
                    and max(abs(q[1]) for q in p) < 0.36]
               for zn in g_lip}
    n1 = sum(len(v) for v in clipped.values())
    draw_polys(ax, clipped, lw=0.40, alpha=0.85)
    th = [i * 2 * math.pi / 180 for i in range(181)]
    ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
            color="#c0392b", lw=1.1)
    ax.annotate("orifice lip\nD=0.40", xy=(R, 0.0), xytext=(0.26, 0.18),
                fontsize=8, color="#7b241c",
                arrowprops=dict(arrowstyle="->", color="#7b241c", lw=0.8))
    finish_2d(
        ax,
        f"Orifice O-grid  zc={zc_orif:.3f} mm\n{n1} quads   nodes on r=0.20",
        "X mm", "Y mm",
        (-0.36, 0.36), (-0.36, 0.36),
        (-0.33, -0.33), 0.08, "80 μm",
    )
    fig.suptitle(
        f"Mesh zooms  {info['level']} {info['n_cells']} HEXA  n_BL={info['n_bl']}  "
        f"NOT CFD  msh in metres",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    return save(fig, PREFIX + "mesh_bl_zoom.png"), n0, n1


def plot_solid_zoom(quads, kinds, z, info):
    """X=0 zoom through TIM + Cu base + first fluid cells (multi-layer solids)."""
    groups, _n = plane_cells(quads, kinds, z, 0, 0.0)
    clipped = {zn: [p for p in groups[zn]
                    if abs(0.5 * (p[0][0] + p[1][0])) < 0.35
                    and p[0][1] < 0.12 and p[2][1] > Z_TIM_BOT - 0.01]
               for zn in groups}
    n = sum(len(v) for v in clipped.values())
    fig, ax = plt.subplots(figsize=(8.4, 5.8), dpi=150)
    draw_polys(ax, clipped, lw=0.35, alpha=0.85)
    ax.axhline(Z_CU_BOT, color="#7b241c", lw=0.7, ls="--")
    ax.axhline(Z_IMP, color="#1a5276", lw=0.7, ls="--")
    ax.annotate("TIM-Cu", xy=(0.20, Z_CU_BOT), fontsize=8, color="#7b241c")
    ax.annotate("Cu-fluid", xy=(0.20, Z_IMP), fontsize=8, color="#1a5276")
    finish_2d(
        ax,
        f"Solid multi-layer  X=0  TIM {info.get('nz_tim', '?')} + Cu base\n"
        f"{n} cut cells   {info['level']} {info['n_cells']} HEXA  NOT CFD",
        "Y mm", "Z mm",
        (-0.35, 0.35), (Z_TIM_BOT - 0.02, 0.12),
        (-0.32, Z_TIM_BOT - 0.015), 0.08, "80 μm",
    )
    return save(fig, PREFIX + "mesh_solid_zoom.png"), n


def plot_slot_bl(quads, kinds, z, info):
    """Prove return-slit and drainage-slot wall BL (edges, not contours)."""
    h1 = info.get("first_imp_mm") or 0.0025
    nbl = info["n_bl"]
    # Y=0 through return slit (XZ): zoom on -X lip x=-1.10
    g_y0, _ = plane_cells(quads, kinds, z, 1, 0.0)
    slit = {zn: [p for p in g_y0[zn]
                 if -1.52 < p[0][0] < -0.95 and p[0][1] < 4.2 and p[2][1] > -0.05]
            for zn in g_y0}
    n_slit = sum(len(v) for v in slit.values())
    # X=0.80 through side drainage slot (YZ)
    g_x, _ = plane_cells(quads, kinds, z, 0, 0.80)
    slot = {zn: [p for p in g_x[zn]
                 if 0.52 < 0.5 * (p[0][0] + p[1][0]) < 1.08
                 and p[0][1] < 1.65 and p[2][1] > -0.05]
            for zn in g_x}
    n_slot = sum(len(v) for v in slot.values())

    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), dpi=150)
    ax = axes[0]
    draw_polys(ax, slit, lw=0.40, alpha=0.85)
    ax.axvline(-1.10, color="#a04000", lw=0.7, ls="--")
    ax.annotate("return lip", xy=(-1.10, 0.8), fontsize=8, color="#a04000")
    finish_2d(
        ax,
        f"Return slit BL  Y=0  x≈−1.10\n"
        f"{n_slit} cells  first={h1*1000:.1f} μm  n_BL={nbl}  growth≤1.2",
        "X mm", "Z mm",
        (-1.52, -0.95), (-0.04, 3.6),
        (-1.50, -0.03), 0.10, "0.10 mm",
    )
    ax = axes[1]
    draw_polys(ax, slot, lw=0.40, alpha=0.85)
    ax.axvline(0.60, color="#1a5276", lw=0.7, ls="--")
    ax.axvline(1.00, color="#1a5276", lw=0.7, ls="--")
    ax.annotate("slot walls", xy=(0.80, 1.35), fontsize=8, ha="center", color="#1a5276")
    finish_2d(
        ax,
        f"Drainage slot BL  X=0.80  y∈[0.60,1.00]\n"
        f"{n_slot} cells  first={h1*1000:.1f} μm  n_BL={nbl}  growth≤1.2",
        "Y mm", "Z mm",
        (0.52, 1.08), (-0.04, 1.65),
        (0.54, -0.03), 0.08, "80 μm",
    )
    fig.suptitle(
        f"Guide/outflow slot BL  {info['level']} {info['n_cells']} HEXA  "
        f"NOT CFD  msh metres",
        fontsize=11, y=1.02,
    )
    fig.tight_layout()
    return save(fig, PREFIX + "mesh_slot_bl.png"), n_slit, n_slot


def plot_iso(quads, kinds, z, info):
    """Isometric: X=0 cut + stacked real XY layers. Edges only."""
    segs = []
    cols = []

    def add_poly_edges(poly_xyz, zn):
        n = len(poly_xyz)
        for i in range(n):
            a, b = poly_xyz[i], poly_xyz[(i + 1) % n]
            segs.append([iso_xy(*a), iso_xy(*b)])
            cols.append(EDGE[zn])

    # X=0 cut (full) — real HEXA rectangles
    n_cut = 0
    for (pts, _xc, _yc), row in zip(quads, kinds):
        iv = clip_interval(pts, 0, 0.0)
        if iv is None:
            continue
        ya, yb = iv
        for k, zn in enumerate(row):
            if not zn:
                continue
            z0, z1 = z[k], z[k + 1]
            add_poly_edges([(0.0, ya, z0), (0.0, yb, z0), (0.0, yb, z1), (0.0, ya, z1)], zn)
            n_cut += 1

    # horizontal layers (actual XY quads at those zc)
    z_targets = (
        (0.5 * (Z_TIM_BOT + Z_CU_BOT), TIM),
        (-1.00, CU),
        (0.75, None),
        (2.50, None),
        (0.5 * (Z_LID + Z_LIDTOP), None),
    )
    n_h = 0
    zs = [0.5 * (z[k] + z[k + 1]) for k in range(len(z) - 1)]
    for zc_t, _force in z_targets:
        k = min(range(len(zs)), key=lambda i: abs(zs[i] - zc_t))
        zc = zs[k]
        for (pts, _xc, _yc), row in zip(quads, kinds):
            zn = row[k]
            if not zn:
                continue
            add_poly_edges([(p[0], p[1], zc) for p in pts], zn)
            n_h += 1

    fig, ax = plt.subplots(figsize=(10.2, 8.4), dpi=140)
    lc = LineCollection(segs, colors=cols, linewidths=0.18, alpha=0.88)
    ax.add_collection(lc)
    # coupon box hint
    box = [
        (X0, Y0, Z_TIM_BOT), (X1, Y0, Z_TIM_BOT), (X1, Y1, Z_TIM_BOT), (X0, Y1, Z_TIM_BOT),
    ]
    for i in range(4):
        a, b = box[i], box[(i + 1) % 4]
        ax.plot(*zip(iso_xy(*a), iso_xy(*b)), color="#888", lw=0.7)
    ax.set_aspect("equal")
    xs = [s[0][0] for s in segs] + [s[1][0] for s in segs]
    ys = [s[0][1] for s in segs] + [s[1][1] for s in segs]
    pad = 0.25
    ax.set_xlim(min(xs) - pad, max(xs) + pad)
    ax.set_ylim(min(ys) - pad, max(ys) + pad)
    ax.axis("off")
    ax.set_title(
        f"3D mesh (isometric cutaway)  X=0 HEXA + 5 real Z layers\n"
        f"X=0 faces {n_cut}   layer quads {n_h}   {info['level']} {info['n_cells']} HEXA\n"
        f"blue=water  gold=Cu  red=TIM   msh metres / plot mm   NOT a CFD contour",
        fontsize=11,
    )
    from matplotlib.lines import Line2D
    ax.legend(
        handles=[Line2D([0], [0], color=EDGE[k], lw=2, label=LABEL[k]) for k in (FLUID, CU, TIM)],
        loc="upper left", fontsize=8,
    )
    # scale in projected mm (X-direction 0.5 mm at origin)
    p0 = iso_xy(0.0, 0.0, Z_TIM_BOT - 0.15)
    p1 = iso_xy(0.50, 0.0, Z_TIM_BOT - 0.15)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#222", lw=1.5)
    ax.text(0.5 * (p0[0] + p1[0]), p0[1] - 0.08, "0.50 mm (X)", ha="center", fontsize=8)
    return save(fig, PREFIX + "mesh3d_iso.png"), n_cut, n_h, len(segs)


def main():
    xy, z, quads, kinds, info = build()
    print("BUILD", info)
    paths = {}
    p, n_x0 = plot_cut_yz(quads, kinds, z, info)
    paths["mesh_cut_x0.png"] = n_x0
    p, n_y0 = plot_cut_xz(quads, kinds, z, info)
    paths["mesh_cut_y0.png"] = n_y0
    p, n_zo, z_o = plot_zcut(quads, kinds, z, 0.5 * (Z_LID + Z_LIDTOP),
                             PREFIX + "mesh_cut_z_orifice.png",
                             "Z cut  orifice / lid (circle + return slits)", info)
    paths[PREFIX + "mesh_cut_z_orifice.png"] = (n_zo, z_o)
    p, n_zg, z_g = plot_zcut(quads, kinds, z, 2.50,
                             PREFIX + "mesh_cut_z_gap.png",
                             "Z cut  mid-gap (wall-jet plane)", info)
    paths[PREFIX + "mesh_cut_z_gap.png"] = (n_zg, z_g)
    p, n_zs, z_s = plot_zcut(quads, kinds, z, 0.75,
                             PREFIX + "mesh_cut_z_slot.png",
                             "Z cut  mid-slot (three channels + Cu ribs)", info)
    paths[PREFIX + "mesh_cut_z_slot.png"] = (n_zs, z_s)
    p, n_zt, z_t = plot_zcut(quads, kinds, z, 0.5 * (Z_TIM_BOT + Z_CU_BOT),
                             PREFIX + "mesh_cut_z_timcu.png",
                             "Z cut  TIM2 slab (TIM–Cu interface neighbour)", info)
    paths[PREFIX + "mesh_cut_z_timcu.png"] = (n_zt, z_t)
    p, n_bl0, n_bl1 = plot_bl_zoom(quads, kinds, z, info)
    paths[PREFIX + "mesh_bl_zoom.png"] = (n_bl0, n_bl1)
    p, n_sol = plot_solid_zoom(quads, kinds, z, info)
    paths[PREFIX + "mesh_solid_zoom.png"] = n_sol
    p, n_slit, n_slot = plot_slot_bl(quads, kinds, z, info)
    paths[PREFIX + "mesh_slot_bl.png"] = (n_slit, n_slot)
    p, n_cut, n_h, n_seg = plot_iso(quads, kinds, z, info)
    paths[PREFIX + "mesh3d_iso.png"] = (n_cut, n_h, n_seg)

    meta = os.path.join(OUT, PREFIX + "mesh_shot_info.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write(f"source write_cht_circle_msh.py {info['level']} == {info['msh']}\n")
        f.write("units msh metres; plots labelled mm. NOT CFD contours.\n")
        for k, v in info.items():
            f.write(f"{k} {v}\n")
        f.write(f"cut_x0_faces {n_x0}\n")
        f.write(f"cut_y0_faces {n_y0}\n")
        f.write(f"cut_z_orifice {n_zo} zc {z_o}\n")
        f.write(f"cut_z_gap {n_zg} zc {z_g}\n")
        f.write(f"cut_z_slot {n_zs} zc {z_s}\n")
        f.write(f"cut_z_timcu {n_zt} zc {z_t}\n")
        f.write(f"bl_impact_cells {n_bl0}\n")
        f.write(f"bl_orifice_quads {n_bl1}\n")
        f.write(f"solid_zoom_cells {n_sol}\n")
        f.write(f"return_slit_bl_cells {n_slit}\n")
        f.write(f"drainage_slot_bl_cells {n_slot}\n")
        f.write(f"iso_x0_faces {n_cut}\n")
        f.write(f"iso_layer_quads {n_h}\n")
        f.write(f"iso_edge_segs {n_seg}\n")
        f.write("medium kept at uc01b_cht_medium.msh 425320 HEXA\n")
    print("WROTE", meta)
    print("PATHS", paths)


if __name__ == "__main__":
    main()
