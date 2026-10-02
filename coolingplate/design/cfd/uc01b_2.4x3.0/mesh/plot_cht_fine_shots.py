# -*- coding: utf-8 -*-
"""Fine-mesh edge screenshots only. Not CFD. Avoid huge filled collections."""
from __future__ import annotations

import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from matplotlib.collections import LineCollection

for _fn in ("Microsoft YaHei", "SimHei"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
os.environ["UC01B_MESH"] = "fine"
from write_cht_circle_msh import (  # noqa: E402
    CU,
    FLUID,
    LEVELS,
    R,
    S_FR,
    T_ANN,
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
    count_bl_layers,
    zone_of,
    z_axis,
)

OUT = os.path.join(os.path.dirname(HERE), "figs")
os.makedirs(OUT, exist_ok=True)
EDGE = {FLUID: "#1a5276", CU: "#7d6608", TIM: "#7b241c"}
FACE = {FLUID: "#8ec8e8", CU: "#e0c15a", TIM: "#d4655a"}


def clip_interval(pts, axis, val, eps=1e-10):
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
    return None if hi - lo < 1e-12 else (lo, hi)


def iso_xy(x, y, z):
    c, s = math.cos(math.radians(30)), math.sin(math.radians(30))
    return (x - y) * c, z + (x + y) * s


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p, os.path.getsize(p))
    return p


def draw_rects(ax, rects):
    segs, cols = [], []
    for (a, b, z0, z1, zn) in rects:
        box = [(a, z0), (b, z0), (b, z1), (a, z1)]
        for i in range(4):
            segs.append([box[i], box[(i + 1) % 4]])
            cols.append(EDGE[zn])
    ax.add_collection(LineCollection(segs, colors=cols, linewidths=0.22, alpha=0.9))
    return len(rects)


def draw_quads_xy(ax, quads_zn):
    segs, cols = [], []
    n = 0
    for pts, zn in quads_zn:
        n += 1
        for i in range(4):
            segs.append([pts[i], pts[(i + 1) % 4]])
            cols.append(EDGE[zn])
    ax.add_collection(LineCollection(segs, colors=cols, linewidths=0.22, alpha=0.9))
    return n


def scale(ax, x0, y0, length, lab):
    ax.plot([x0, x0 + length], [y0, y0], color="#222", lw=1.4)
    ax.text(x0 + 0.5 * length, y0, "\n" + lab, ha="center", va="top", fontsize=8)


def legend(ax):
    from matplotlib.lines import Line2D
    ax.legend(
        [Line2D([0], [0], color=EDGE[k], lw=2, label=lab)
         for k, lab in ((FLUID, "water"), (CU, "Cu"), (TIM, "TIM"))],
        [l.get_label() for l in [
            type("T", (), {"get_label": lambda self, n=n: n})()
            for n in ("water", "Cu", "TIM")
        ]],
        loc="upper right", fontsize=8,
    )
    ax.legend(
        handles=[
            plt.Line2D([0], [0], color=EDGE[FLUID], lw=2, label="water"),
            plt.Line2D([0], [0], color=EDGE[CU], lw=2, label="Cu"),
            plt.Line2D([0], [0], color=EDGE[TIM], lw=2, label="TIM"),
        ],
        loc="upper right", fontsize=8,
    )


def main():
    lv = LEVELS["fine"]
    xy = build_xy(lv)
    z = z_axis(lv)
    quads = []
    for n0, n1, n2, n3 in xy.quads:
        pts = (xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3])
        xc = 0.25 * sum(p[0] for p in pts)
        yc = 0.25 * sum(p[1] for p in pts)
        quads.append((pts, xc, yc))
    nz = len(z) - 1
    n_cells = 4472280
    h1 = lv["first"]
    nbl = lv["n_bl"]
    n_c, d_c = count_bl_layers(xy.ys, -0.20, +1)
    d_c_um = (d_c or 0.0) * 1000.0

    def plane_rects(axis, val, ywin=None, zwin=None, stride=1):
        out = []
        for pts, xc, yc in quads:
            iv = clip_interval(pts, axis, val)
            if iv is None:
                continue
            a, b = iv
            if ywin and (b < ywin[0] or a > ywin[1]):
                continue
            for k in range(0, nz, stride):
                zn = zone_of(xc, yc, 0.5 * (z[k] + z[k + 1]))
                if not zn:
                    continue
                z0, z1 = z[k], z[k + 1]
                if zwin and (z1 < zwin[0] or z0 > zwin[1]):
                    continue
                out.append((a, b, z0, z1, zn))
        return out

    def z_quads(zc_t, rwin=None, xwin=None, ywin=None):
        zs = [0.5 * (z[k] + z[k + 1]) for k in range(nz)]
        k = min(range(nz), key=lambda i: abs(zs[i] - zc_t))
        out = []
        for pts, xc, yc in quads:
            zn = zone_of(xc, yc, zs[k])
            if not zn:
                continue
            if rwin and max(abs(xc), abs(yc)) > rwin:
                continue
            if xwin and (xc < xwin[0] or xc > xwin[1]):
                continue
            if ywin and (yc < ywin[0] or yc > ywin[1]):
                continue
            out.append((pts, zn))
        return out, zs[k], k

    # --- X=0 full (stride 2 in Z to stay light) ---
    fig, ax = plt.subplots(figsize=(8.4, 9.0), dpi=130)
    n = draw_rects(ax, plane_rects(0, 0.0, stride=2))
    ax.set_xlim(-1.28, 1.28)
    ax.set_ylim(Z_TIM_BOT - 0.15, 8.25)
    ax.set_aspect("equal")
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"fine X=0 mesh edges  {n} HEXA faces  {n_cells} HEXA\n"
                 f"msh metres / plot mm  NOT CFD")
    scale(ax, -1.15, -1.85, 0.40, "0.40 mm")
    legend(ax)
    save(fig, "fine_mesh_cut_x0.png")

    fig, ax = plt.subplots(figsize=(8.6, 9.0), dpi=130)
    n = draw_rects(ax, plane_rects(1, 0.0, stride=2))
    ax.set_xlim(-1.58, 1.58)
    ax.set_ylim(Z_TIM_BOT - 0.15, 8.25)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"fine Y=0 mesh edges  {n} HEXA faces  {n_cells} HEXA\n"
                 f"msh metres / plot mm  NOT CFD")
    scale(ax, -1.45, -1.85, 0.40, "0.40 mm")
    legend(ax)
    save(fig, "fine_mesh_cut_y0.png")

    for zc, fn, title in (
        (0.5 * (Z_LID + Z_LIDTOP), "fine_mesh_cut_z_orifice.png", "Z orifice/lid"),
        (2.50, "fine_mesh_cut_z_gap.png", "Z mid-gap"),
        (0.75, "fine_mesh_cut_z_slot.png", "Z mid-slot"),
        (0.5 * (Z_TIM_BOT + Z_CU_BOT), "fine_mesh_cut_z_timcu.png", "Z TIM"),
    ):
        qq, zc_u, k = z_quads(zc)
        fig, ax = plt.subplots(figsize=(8.0, 6.6), dpi=130)
        n = draw_quads_xy(ax, qq)
        th = [i * 2 * math.pi / 180 for i in range(181)]
        ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
                color="#c0392b", lw=0.8, ls="--")
        ax.set_xlim(-1.58, 1.58)
        ax.set_ylim(-1.28, 1.28)
        ax.set_aspect("equal")
        ax.set_xlabel("X mm")
        ax.set_ylabel("Y mm")
        ax.set_title(f"fine {title}  zc={zc_u:.3f} mm k={k}  {n} quads\n"
                     f"{n_cells} HEXA  NOT CFD")
        scale(ax, -1.45, -1.12, 0.40, "0.40 mm")
        legend(ax)
        save(fig, fn)

    # orifice + impact zoom
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 5.4), dpi=140)
    ax = axes[0]
    n0 = draw_rects(ax, plane_rects(0, 0.0, ywin=(-0.22, 0.22), zwin=(-0.04, 0.09)))
    ax.set_xlim(-0.22, 0.22)
    ax.set_ylim(-0.035, 0.085)
    ax.set_aspect("equal")
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"Impact BL X=0  {n0} cells  first={h1*1000:.1f} μm  n_BL={nbl}")
    scale(ax, -0.20, -0.028, 0.05, "50 μm")
    legend(ax)
    ax = axes[1]
    qq, zc_u, _k = z_quads(0.5 * (Z_LID + Z_LIDTOP), rwin=0.36)
    n1 = draw_quads_xy(ax, qq)
    th = [i * 2 * math.pi / 180 for i in range(181)]
    ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
            color="#c0392b", lw=1.1)
    ax.set_xlim(-0.36, 0.36)
    ax.set_ylim(-0.36, 0.36)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title(f"Orifice wall BL  zc={zc_u:.3f}  {n1} quads  h_orif=3 μm  n_ri=14")
    scale(ax, -0.33, -0.33, 0.08, "80 μm")
    legend(ax)
    fig.suptitle(f"fine {n_cells} HEXA  NOT CFD", fontsize=11)
    fig.tight_layout()
    save(fig, "fine_mesh_bl_zoom.png")

    # solid multi-layer
    fig, ax = plt.subplots(figsize=(8.2, 5.6), dpi=140)
    n = draw_rects(ax, plane_rects(0, 0.0, ywin=(-0.35, 0.35), zwin=(Z_TIM_BOT - 0.01, 0.12)))
    ax.axhline(Z_CU_BOT, color="#7b241c", lw=0.7, ls="--")
    ax.axhline(Z_IMP, color="#1a5276", lw=0.7, ls="--")
    ax.set_xlim(-0.35, 0.35)
    ax.set_ylim(Z_TIM_BOT - 0.02, 0.12)
    ax.set_aspect("equal")
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"Solid layers X=0  TIM nz=6  Cu nz=14  {n} cells\n"
                 f"fine {n_cells} HEXA  NOT CFD")
    scale(ax, -0.32, Z_TIM_BOT - 0.015, 0.08, "80 μm")
    legend(ax)
    save(fig, "fine_mesh_solid_zoom.png")

    # RETURN SLIT + DRAINAGE SLOT BL (the required proof)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), dpi=150)
    ax = axes[0]
    n_slit = draw_rects(ax, plane_rects(1, 0.0, ywin=(-1.52, -0.95), zwin=(-0.05, 3.7)))
    ax.axvline(-1.10, color="#a04000", lw=0.8, ls="--")
    ax.set_xlim(-1.52, -0.95)
    ax.set_ylim(-0.04, 3.6)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"Return slit BL  Y=0  lip x=−1.10\n"
                 f"{n_slit} cells  first={h1*1000:.1f} μm  n_BL={nbl}  growth≤1.2")
    scale(ax, -1.50, -0.03, 0.10, "0.10 mm")
    legend(ax)
    ax = axes[1]
    n_slot = draw_rects(ax, plane_rects(0, 0.80, ywin=(0.52, 1.08), zwin=(-0.05, 1.70)))
    ax.axvline(0.60, color="#1a5276", lw=0.8, ls="--")
    ax.axvline(1.00, color="#1a5276", lw=0.8, ls="--")
    ax.set_xlim(0.52, 1.08)
    ax.set_ylim(-0.04, 1.65)
    ax.set_aspect("equal")
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_title(f"Drainage slot BL  X=0.80  y∈[0.60,1.00]\n"
                 f"{n_slot} cells  first={h1*1000:.1f} μm  n_BL={nbl}  growth≤1.2")
    scale(ax, 0.54, -0.03, 0.08, "80 μm")
    legend(ax)
    fig.suptitle(f"Guide/outflow slot BL  fine {n_cells} HEXA  NOT CFD", fontsize=11)
    fig.tight_layout()
    save(fig, "fine_mesh_slot_bl.png")

    # CENTER drainage slot only (not side slots). Z-cut + YZ at X=0.80
    fig, axes = plt.subplots(1, 2, figsize=(11.6, 5.8), dpi=160)
    ax = axes[0]
    qq, zc_u, _k = z_quads(0.75, xwin=(0.42, 1.14), ywin=(-0.62, 0.62))
    n_z = draw_quads_xy(ax, qq)
    ax.axhline(-0.20, color="#c0392b", lw=0.7, ls="--")
    ax.axhline(0.20, color="#c0392b", lw=0.7, ls="--")
    ax.set_xlim(0.42, 1.12)
    ax.set_ylim(-0.60, 0.60)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title(
        f"Center slot Z-cut  zc={zc_u:.3f} mm  X∈[0.42,1.12]\n"
        f"{n_z} quads  first={d_c_um:.1f} μm  n_BL={n_c}  (from msh Y)"
    )
    scale(ax, 0.46, -0.56, 0.05, "50 μm")
    legend(ax)
    ax = axes[1]
    n_yz = draw_rects(ax, plane_rects(0, 0.80, ywin=(-0.62, 0.62), zwin=(-0.04, 1.62)))
    ax.axvline(-0.20, color="#c0392b", lw=0.7, ls="--")
    ax.axvline(0.20, color="#c0392b", lw=0.7, ls="--")
    ax.axhline(Z_IMP, color="#1a5276", lw=0.6, ls=":")
    ax.axhline(Z_RIB, color="#1a5276", lw=0.6, ls=":")
    ax.set_xlim(-0.60, 0.60)
    ax.set_ylim(-0.04, 1.60)
    ax.set_aspect("equal")
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_title(
        f"Center slot YZ  X=0.80  y∈[−0.60,0.60]\n"
        f"{n_yz} cells  walls+floor+ceil first={d_c_um:.1f} μm  n_BL={n_c}"
    )
    scale(ax, -0.56, -0.03, 0.05, "50 μm")
    legend(ax)
    fig.suptitle(
        f"CENTER slot BL  y∈[−0.20,0.20]  first={d_c_um:.1f} μm  "
        f"n_BL={n_c}  growth≤1.2  {n_cells} HEXA  NOT CFD",
        fontsize=11,
    )
    fig.tight_layout()
    save(fig, "fine_mesh_center_slot_bl.png")

    # Orifice bore + transition annulus (r=0.20 → ~0.85 mm)
    fig, axes = plt.subplots(1, 2, figsize=(11.4, 5.6), dpi=150)
    ax = axes[0]
    qq, zc_u, _k = z_quads(0.5 * (Z_LID + Z_LIDTOP), rwin=1.05)
    n_t = draw_quads_xy(ax, qq)
    th = [i * 2 * math.pi / 180 for i in range(181)]
    ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
            color="#c0392b", lw=1.0)
    ax.plot([T_ANN * math.cos(t) for t in th], [T_ANN * math.sin(t) for t in th],
            color="#a04000", lw=0.7, ls="--")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-1.05, 1.05)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title(f"Orifice + transition  zc={zc_u:.3f}  {n_t} quads\n"
                 f"solid r=0.20  dashed r={T_ANN:.2f}  S_FR={S_FR:.2f}")
    scale(ax, -0.98, -0.98, 0.20, "0.20 mm")
    legend(ax)
    ax = axes[1]
    qq, zc_u, _k = z_quads(0.5 * (Z_LID + Z_LIDTOP), rwin=0.42)
    n_z2 = draw_quads_xy(ax, qq)
    ax.plot([R * math.cos(t) for t in th], [R * math.sin(t) for t in th],
            color="#c0392b", lw=1.1)
    ax.set_xlim(-0.40, 0.40)
    ax.set_ylim(-0.40, 0.40)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title(f"Lip zoom  0.80 mm window  {n_z2} quads\n"
                 f"h_orif=3 μm  ≥10 radial layers")
    scale(ax, -0.36, -0.36, 0.05, "50 μm")
    legend(ax)
    fig.suptitle(f"Orifice / transition  fine {n_cells} HEXA  NOT CFD", fontsize=11)
    fig.tight_layout()
    save(fig, "fine_mesh_orif_trans.png")

    fig, ax = plt.subplots(figsize=(8.8, 5.8), dpi=140)
    n_xz = draw_rects(ax, plane_rects(1, 0.0, ywin=(-0.95, 0.95), zwin=(3.2, 6.2)))
    ax.axvline(-R, color="#c0392b", lw=0.7, ls="--")
    ax.axvline(R, color="#c0392b", lw=0.7, ls="--")
    ax.set_xlim(-0.95, 0.95)
    ax.set_ylim(3.25, 6.15)
    ax.set_aspect("equal")
    ax.set_xlabel("X mm")
    ax.set_ylabel("Z mm")
    ax.set_title(
        f"Orifice vertical Y=0  hole + radial transition\n"
        f"{n_xz} cells  r=0.20 dashed  fine {n_cells} HEXA  NOT CFD"
    )
    scale(ax, -0.90, 3.32, 0.20, "0.20 mm")
    legend(ax)
    save(fig, "fine_mesh_orif_trans_xz.png")

    # light isometric: X=0 every 3rd layer + 3 Z planes
    segs, cols = [], []
    n_cut = 0
    for a, b, z0, z1, zn in plane_rects(0, 0.0, stride=3):
        box = [(0.0, a, z0), (0.0, b, z0), (0.0, b, z1), (0.0, a, z1)]
        proj = [iso_xy(*p) for p in box]
        for i in range(4):
            segs.append([proj[i], proj[(i + 1) % 4]])
            cols.append(EDGE[zn])
        n_cut += 1
    n_h = 0
    for zc_t in (0.5 * (Z_TIM_BOT + Z_CU_BOT), 0.75, 0.5 * (Z_LID + Z_LIDTOP)):
        qq, zc_u, _k = z_quads(zc_t)
        for pts, zn in qq[::2]:
            poly = [(p[0], p[1], zc_u) for p in pts]
            proj = [iso_xy(*p) for p in poly]
            for i in range(4):
                segs.append([proj[i], proj[(i + 1) % 4]])
                cols.append(EDGE[zn])
            n_h += 1
    fig, ax = plt.subplots(figsize=(10.0, 8.2), dpi=130)
    ax.add_collection(LineCollection(segs, colors=cols, linewidths=0.15, alpha=0.85))
    xs = [s[0][0] for s in segs] + [s[1][0] for s in segs]
    ys = [s[0][1] for s in segs] + [s[1][1] for s in segs]
    ax.set_xlim(min(xs) - 0.2, max(xs) + 0.2)
    ax.set_ylim(min(ys) - 0.2, max(ys) + 0.2)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title(
        f"fine 3D mesh (iso, X=0 stride-3 + 3 Z layers)\n"
        f"X=0 faces {n_cut}  layer quads {n_h}  {n_cells} HEXA  NOT CFD",
        fontsize=11,
    )
    legend(ax)
    p0, p1 = iso_xy(0, 0, Z_TIM_BOT - 0.15), iso_xy(0.50, 0, Z_TIM_BOT - 0.15)
    ax.plot([p0[0], p1[0]], [p0[1], p1[1]], color="#222", lw=1.4)
    ax.text(0.5 * (p0[0] + p1[0]), p0[1] - 0.08, "0.50 mm (X)", ha="center", fontsize=8)
    save(fig, "fine_mesh3d_iso.png")

    meta = os.path.join(OUT, "fine_mesh_shot_info.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write("fine uc01b_cht_fine.msh 4472280 HEXA\n")
        f.write(f"center_slot first={d_c_um:.1f} um n_BL={n_c} growth<=1.2\n")
        f.write("slot/slit BL first=2.5 um n_BL=10 growth<=1.2\n")
        f.write("orifice h_orif=3 um n_ri=14  TIM nz=6  Cu nz=14  lid=solid_cu\n")
        f.write("NOT CFD contours\n")
    print("WROTE", meta)


if __name__ == "__main__":
    main()
