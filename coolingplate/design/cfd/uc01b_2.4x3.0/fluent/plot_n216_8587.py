# -*- coding: utf-8 -*-
"""TIM bottom and mid-plane contours from the saved iter-8587 field.

Reads uc01b_cht_v2_n216_q105.cas.h5 / .dat.h5. Does not start Fluent
and does not write v2cur_* (those are the iter-7900 figures).
"""
from __future__ import annotations

import os

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize

import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")
p.NOTE = "iter 529  n216_q105_sym"


def quad_area(xyz):
    a = xyz[:, 1] - xyz[:, 0]
    b = xyz[:, 2] - xyz[:, 0]
    c = np.cross(a, b)
    return 0.5 * np.linalg.norm(c, axis=1) + 0.5 * np.linalg.norm(
        np.cross(xyz[:, 2] - xyz[:, 1], xyz[:, 3] - xyz[:, 1]), axis=1
    )


def main():
    print("CAS", p.CAS)
    print("DAT", p.DAT)
    mesh = p.load_mesh_fields()
    t = mesh["face_t"]["wall_heat"]
    a, b = p.ZONE["wall_heat"]
    xyz = mesh["coords"][mesh["fn"][a:b]]
    area = quad_area(xyz)
    aw = float(np.sum(t * area) / np.sum(area))
    print("WALL_HEAT n", int(t.size), "min", float(t.min()), "max", float(t.max()), "AW", aw)
    print("WALL_HEAT span", float(t.max() - t.min()))

    verts = p.poly_mm(xyz, (0, 1))
    lo, hi = float(t.min()), float(t.max())
    span = hi - lo
    fig, axes = plt.subplots(1, 2, figsize=(14.2, 6.6), dpi=140)
    # left: this face's own min/max, ticks stay near 341.93 K
    n1 = Normalize(lo, hi if hi > lo else lo + 1e-4)
    p.add_polys(axes[0], verts, t, n1, "inferno")
    p.add_outline(axes[0], verts, color="#202020", lw=0.6)
    p.finish_limits(axes[0], [verts])
    p.colorbar(fig, axes[0], n1, "inferno", "本面 T (K)", max(span, 1e-4))
    p.style_ax(axes[0], "X mm", "Y mm", "本面最小–最大\n%.5f–%.5f K" % (lo, hi))
    # right: absolute scale so 341.9 is not mistaken for 332.5
    n2 = Normalize(330.0, 345.0)
    p.add_polys(axes[1], verts, t, n2, "inferno")
    p.add_outline(axes[1], verts, color="#202020", lw=0.6)
    p.finish_limits(axes[1], [verts])
    p.colorbar(fig, axes[1], n2, "inferno", "绝对 T (K)", 1.0)
    p.style_ax(axes[1], "X mm", "Y mm", "绝对温度色标 330–345 K\n底面面积加权 %.3f K" % aw)
    fig.suptitle(
        "iter 529  n216_q105_sym  TIM 底面 wall_heat\n"
        "面积加权 %.4f K（%.2f °C）    面内 %.5f–%.5f K    变化 %.4f K"
        % (aw, aw - 273.15, lo, hi, span),
        fontsize=13,
    )
    fig.tight_layout(rect=(0, 0.04, 1, 0.88))
    fig.text(
        0.5, 0.01,
        "场 uc01b_cht_v2_n216_q105。z = −2.080 mm。左图色标是本面真实最小最大；"
        "面内只有约 %.3f K，所以左图看起来几乎一色。右图把同一温度放在 330–345 K 上，"
        "用来看绝对水平。不是 iter 7900 的 332.5 K 中面。" % span,
        ha="center", fontsize=8,
    )
    out1 = os.path.join(p.FIGS, "n216_sym_wall_heat_T.png")
    fig.savefig(out1)
    plt.close(fig)
    print("WROTE", out1)

    z = np.unique(np.round(mesh["coords"][:, 2], 7))
    z_tim = p._nearest(z, -0.00204, -0.002079, -0.002001)
    print("TIM_MID_Z", z_tim)
    idx = p.plane_idx(mesh, 2, z_tim, tol=5e-7)
    xyz, tt, u, v, w, kind, names = p.pack_faces(mesh, idx)
    solid = kind == 2
    # keep TIM cells only
    c0 = mesh["c0"][idx]
    c1 = p.c1_of(idx, mesh["c1"])
    k0 = p.cell_kind(c0)
    k1 = p.cell_kind(c1)
    tim = (kind == 2) & ((k0 == 3) | (k1 == 3))
    tt = tt[tim]
    verts = p.poly_mm(xyz[tim], (0, 1))
    lo, hi = float(tt.min()), float(tt.max())
    print("TIM_MID n", int(tt.size), "min", lo, "max", hi, "mean", float(tt.mean()))
    fig, ax = plt.subplots(figsize=(8.8, 6.8), dpi=140)
    n = Normalize(lo, hi if hi > lo else lo + 1e-4)
    p.add_polys(ax, verts, tt, n, "inferno")
    p.add_outline(ax, verts, color="#202020", lw=0.6)
    p.finish_limits(ax, [verts])
    p.colorbar(fig, ax, n, "inferno", "solid_tim2 T (K)", max(hi - lo, 1e-4))
    p.style_ax(
        ax, "X mm", "Y mm",
        "iter 529  TIM 中面  z = %.4f mm  solid_tim2\n%.3f–%.3f K，低于底面 %.4f K"
        % (z_tim * 1e3, lo, hi, aw),
    )
    ax.text(
        0.0, -0.18,
        "同一场 n216_q105_sym。中面比 TIM 底 wall_heat 低。",
        transform=ax.transAxes, fontsize=8, va="top",
    )
    fig.tight_layout()
    out2 = os.path.join(p.FIGS, "n216_sym_ztim_mid_T.png")
    fig.savefig(out2, bbox_inches="tight")
    plt.close(fig)
    print("WROTE", out2)


if __name__ == "__main__":
    main()
