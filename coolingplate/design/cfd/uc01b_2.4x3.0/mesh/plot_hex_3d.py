# -*- coding: utf-8 -*-
"""3D / cut-plane pictures of the same hex coupon Fluent accepted.

Not CFD contours. Boundary faces from write_hex_msh.py fluid mask.
"""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

for _fn in ("Microsoft YaHei", "SimHei", "Source Han Sans CN"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from write_hex_msh import (  # noqa: E402
    FIRST,
    SLOT_YS,
    SO2,
    X0,
    X1,
    XL,
    XR,
    Y0,
    Y1,
    Z_IMP,
    Z_IN,
    Z_LID,
    Z_LIDTOP,
    Z_RIB,
    geo_seg,
    merge_axis,
)

OUT = os.path.join(os.path.dirname(HERE), "figs")
os.makedirs(OUT, exist_ok=True)

COLORS = {
    "wall_imp": "#c0392b",
    "fin": "#7f8c8d",
    "wall_lid": "#2980b9",
    "wall_orifice": "#8e44ad",
    "inlet_jet": "#27ae60",
    "return_slot": "#e67e22",
    "SYM": "#bdc3c7",
}


def build():
    nx_slit, nx_core, nx_orif = 8, 16, 10
    ny_half, ny_slot, ny_rib = 4, 10, 8
    nz_slot, nz_gap, nz_orif, nz_pl = 20, 16, 10, 6
    x = merge_axis(
        [
            geo_seg(X0, XL, nx_slit),
            geo_seg(XL, -SO2, nx_core, last=min(0.02, (-SO2 - XL) / max(nx_core, 1))),
            geo_seg(-SO2, SO2, nx_orif),
            geo_seg(SO2, XR, nx_core, first=min(0.02, (XR - SO2) / max(nx_core, 1))),
            geo_seg(XR, X1, nx_slit),
        ]
    )
    y = merge_axis(
        [
            geo_seg(Y0, -1.00, ny_half),
            geo_seg(-1.00, -0.60, ny_slot, first=0.02, last=0.02),
            geo_seg(-0.60, -0.20, ny_rib),
            geo_seg(-0.20, -SO2, max(3, ny_slot // 3)),
            geo_seg(-SO2, SO2, nx_orif),
            geo_seg(SO2, 0.20, max(3, ny_slot // 3)),
            geo_seg(0.20, 0.60, ny_rib),
            geo_seg(0.60, 1.00, ny_slot, first=0.02, last=0.02),
            geo_seg(1.00, Y1, ny_half),
        ]
    )
    z = merge_axis(
        [
            geo_seg(Z_IMP, Z_RIB, nz_slot, first=FIRST, last=FIRST),
            geo_seg(Z_RIB, Z_LID, nz_gap, first=FIRST, last=FIRST),
            geo_seg(Z_LID, Z_LIDTOP, nz_orif),
            geo_seg(Z_LIDTOP, Z_IN, nz_pl),
        ]
    )
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1

    def in_slot_y(yc):
        return any(a <= yc <= b for a, b in SLOT_YS)

    def is_fluid(i, j, k):
        xc = 0.5 * (x[i] + x[i + 1])
        yc = 0.5 * (y[j] + y[j + 1])
        zc = 0.5 * (z[k] + z[k + 1])
        slit = xc < XL - 1e-12 or xc > XR + 1e-12
        in_orif = abs(xc) <= SO2 + 1e-12 and abs(yc) <= SO2 + 1e-12
        if zc < Z_RIB - 1e-12:
            return slit or in_slot_y(yc)
        if zc < Z_LID - 1e-12:
            return True
        if zc < Z_LIDTOP + 1e-12:
            return slit or in_orif
        return in_orif

    fluid = {
        (i, j, k)
        for i in range(nx)
        for j in range(ny)
        for k in range(nz)
        if is_fluid(i, j, k)
    }

    def cell(i, j, k):
        return (i, j, k) in fluid

    def quad(pts):
        return [(p[0], p[1], p[2]) for p in pts]

    faces = []
    # only draw a subset of boundary faces for a readable iso (every face of walls)
    for i, j, k in fluid:
        # -x
        if not cell(i - 1, j, k):
            faces.append(
                quad(
                    [
                        (x[i], y[j], z[k]),
                        (x[i], y[j + 1], z[k]),
                        (x[i], y[j + 1], z[k + 1]),
                        (x[i], y[j], z[k + 1]),
                    ]
                )
            )
        if not cell(i + 1, j, k):
            faces.append(
                quad(
                    [
                        (x[i + 1], y[j], z[k]),
                        (x[i + 1], y[j + 1], z[k]),
                        (x[i + 1], y[j + 1], z[k + 1]),
                        (x[i + 1], y[j], z[k + 1]),
                    ]
                )
            )
        if not cell(i, j - 1, k):
            faces.append(
                quad(
                    [
                        (x[i], y[j], z[k]),
                        (x[i + 1], y[j], z[k]),
                        (x[i + 1], y[j], z[k + 1]),
                        (x[i], y[j], z[k + 1]),
                    ]
                )
            )
        if not cell(i, j + 1, k):
            faces.append(
                quad(
                    [
                        (x[i], y[j + 1], z[k]),
                        (x[i + 1], y[j + 1], z[k]),
                        (x[i + 1], y[j + 1], z[k + 1]),
                        (x[i], y[j + 1], z[k + 1]),
                    ]
                )
            )
        if not cell(i, j, k - 1):
            faces.append(
                quad(
                    [
                        (x[i], y[j], z[k]),
                        (x[i + 1], y[j], z[k]),
                        (x[i + 1], y[j + 1], z[k]),
                        (x[i], y[j + 1], z[k]),
                    ]
                )
            )
        if not cell(i, j, k + 1):
            faces.append(
                quad(
                    [
                        (x[i], y[j], z[k + 1]),
                        (x[i + 1], y[j], z[k + 1]),
                        (x[i + 1], y[j + 1], z[k + 1]),
                        (x[i], y[j + 1], z[k + 1]),
                    ]
                )
            )
    return np.array(x), np.array(y), np.array(z), faces, fluid


def save_iso(faces):
    fig = plt.figure(figsize=(10.2, 8.0), dpi=140)
    ax = fig.add_subplot(111, projection="3d")
    coll = Poly3DCollection(
        faces, facecolor="#5dade2", edgecolor="#1a5276", linewidths=0.12, alpha=0.55
    )
    ax.add_collection3d(coll)
    ax.set_xlim(X0, X1)
    ax.set_ylim(Y0, Y1)
    ax.set_zlim(Z_IMP, Z_IN)
    ax.set_xlabel("X mm (槽向)")
    ax.set_ylabel("Y mm (跨槽)")
    ax.set_zlabel("Z mm")
    try:
        ax.set_box_aspect((X1 - X0, Y1 - Y0, Z_IN - Z_IMP))
    except Exception:
        pass
    ax.view_init(elev=22, azim=-55)
    ax.set_title(
        "UC-01b hex 单元胞边界面  116320 HEXA\n"
        "Sx=3.0 mm × Sy=2.4 mm × Z=0–8 mm   方孔≈0.355 mm"
    )
    fig.tight_layout()
    p = os.path.join(OUT, "mesh_iso3d.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p, os.path.getsize(p))


def save_cuts(x, y, z, fluid):
    def fluid_at(i, j, k):
        return (i, j, k) in fluid

    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1

    # X=0 cells
    fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=130)
    for i in range(nx):
        if not (x[i] <= 0.0 <= x[i + 1]):
            continue
        for j in range(ny):
            for k in range(nz):
                if not fluid_at(i, j, k):
                    continue
                ax.fill(
                    [y[j], y[j + 1], y[j + 1], y[j]],
                    [z[k], z[k], z[k + 1], z[k + 1]],
                    facecolor="#5dade2",
                    edgecolor="#1b4f72",
                    linewidth=0.15,
                )
    ax.set_xlabel("Y mm")
    ax.set_ylabel("Z mm")
    ax.set_aspect("equal")
    ax.set_title("网格切面 X=0（过射流，沿槽 / YZ）  hex 单元")
    fig.tight_layout()
    p = os.path.join(OUT, "mesh_cut_x0.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)

    fig, ax = plt.subplots(figsize=(8.6, 7.2), dpi=130)
    for j in range(ny):
        if not (y[j] <= 0.0 <= y[j + 1]):
            continue
        for i in range(nx):
            for k in range(nz):
                if not fluid_at(i, j, k):
                    continue
                ax.fill(
                    [x[i], x[i + 1], x[i + 1], x[i]],
                    [z[k], z[k], z[k + 1], z[k + 1]],
                    facecolor="#58d68d",
                    edgecolor="#145a32",
                    linewidth=0.15,
                )
    ax.set_xlabel("X mm")
    ax.set_ylabel("Z mm")
    ax.set_aspect("equal")
    ax.set_title("网格切面 Y=0（过射流，跨三槽 / XZ）  hex 单元")
    fig.tight_layout()
    p = os.path.join(OUT, "mesh_cut_y0.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)

    zcut = 0.75
    fig, ax = plt.subplots(figsize=(8.2, 6.4), dpi=130)
    for k in range(nz):
        if not (z[k] <= zcut <= z[k + 1]):
            continue
        for i in range(nx):
            for j in range(ny):
                if not fluid_at(i, j, k):
                    continue
                ax.fill(
                    [x[i], x[i + 1], x[i + 1], x[i]],
                    [y[j], y[j], y[j + 1], y[j + 1]],
                    facecolor="#f5b041",
                    edgecolor="#7d6608",
                    linewidth=0.15,
                )
    ax.set_xlabel("X mm")
    ax.set_ylabel("Y mm")
    ax.set_aspect("equal")
    ax.set_title("网格切面 Z=0.75 mm（槽内水平）  hex 单元")
    fig.tight_layout()
    p = os.path.join(OUT, "mesh_cut_z075.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)


def main():
    x, y, z, faces, fluid = build()
    print("faces", len(faces), "cells", len(fluid))
    save_iso(faces)
    save_cuts(x, y, z, fluid)


if __name__ == "__main__":
    main()
