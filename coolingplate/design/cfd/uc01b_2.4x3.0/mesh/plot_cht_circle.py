# -*- coding: utf-8 -*-
"""Prove CHT orifice is CIRCLE D=0.40 mm. XY only (no heavy Z fills)."""
from __future__ import annotations

import math
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

for _fn in ("Microsoft YaHei", "SimHei"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from write_cht_circle_msh import D, FLUID, R, Z_LID, Z_LIDTOP, build_xy, zone_of  # noqa: E402

OUT = os.path.join(os.path.dirname(HERE), "figs")
os.makedirs(OUT, exist_ok=True)


def main():
    xy = build_xy()
    zc = 0.5 * (Z_LID + Z_LIDTOP)
    th = np.linspace(0, 2 * math.pi, 240)
    cx, cy = R * np.cos(th), R * np.sin(th)
    polys = []
    for n0, n1, n2, n3 in xy.quads:
        pts = [xy.xy[n] for n in (n0, n1, n2, n3)]
        xc = 0.25 * sum(p[0] for p in pts)
        yc = 0.25 * sum(p[1] for p in pts)
        if zone_of(xc, yc, zc) == FLUID:
            polys.append(pts)

    fig, ax = plt.subplots(figsize=(7.0, 5.8), dpi=120)
    for pts in polys:
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]
        ax.fill(xs, ys, color="#5dade2", edgecolor="#1a5276", lw=0.12)
    ax.plot(cx, cy, color="#c0392b", lw=1.5, label="D=0.40 mm circle")
    ax.set_aspect("equal")
    ax.set_xlim(-1.55, 1.55)
    ax.set_ylim(-1.25, 1.25)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title("CHT jet at lid  Z=4.75 mm  circular D=0.40 (not square)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    p = os.path.join(OUT, "cht_orifice_circle.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)

    fig, ax = plt.subplots(figsize=(5.8, 5.8), dpi=120)
    for pts in polys:
        xc = 0.25 * sum(p[0] for p in pts)
        yc = 0.25 * sum(p[1] for p in pts)
        if max(abs(xc), abs(yc)) > 0.42:
            continue
        xs = [p[0] for p in pts] + [pts[0][0]]
        ys = [p[1] for p in pts] + [pts[0][1]]
        ax.fill(xs, ys, color="#5dade2", edgecolor="#1a5276", lw=0.28)
    ax.plot(cx, cy, color="#c0392b", lw=1.8)
    ax.set_aspect("equal")
    ax.set_xlim(-0.40, 0.40)
    ax.set_ylim(-0.40, 0.40)
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_title("O-grid zoom  nodes on r=0.20 mm")
    fig.tight_layout()
    p = os.path.join(OUT, "cht_orifice_circle_zoom.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)


if __name__ == "__main__":
    main()
