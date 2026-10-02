# -*- coding: utf-8 -*-
"""CHT stack mesh pictures via pcolormesh. Not CFD contours."""
from __future__ import annotations

import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import colors, font_manager
from matplotlib.patches import Rectangle
import numpy as np

for _fn in ("Microsoft YaHei", "SimHei", "Source Han Sans CN"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from write_cht_msh import (  # noqa: E402
    CU,
    FLUID,
    TIM,
    X0,
    X1,
    Y0,
    Y1,
    Z_CU_BOT,
    Z_IMP,
    Z_IN,
    Z_LID,
    Z_RIB,
    Z_TIM_BOT,
    build_axes,
    zone_of,
)

OUT = os.path.join(os.path.dirname(HERE), "figs")
os.makedirs(OUT, exist_ok=True)

ID = {None: 0, FLUID: 1, CU: 2, TIM: 3}
CMAP = colors.ListedColormap(["#f4f6f7", "#5dade2", "#d4a017", "#c0392b"])
NORM = colors.BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], CMAP.N)


def code(xc, yc, zc):
    return ID[zone_of(xc, yc, zc)]


def save_pcolor(u, v, Z, title, fname, xl, yl):
    fig, ax = plt.subplots(figsize=(8.4, 7.2), dpi=120)
    ax.pcolormesh(u, v, Z, cmap=CMAP, norm=NORM, shading="flat")
    ax.set_xlabel(xl)
    ax.set_ylabel(yl)
    ax.set_title(title)
    ax.set_aspect("equal")
    fig.tight_layout()
    p = os.path.join(OUT, fname)
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p, os.path.getsize(p))


def main():
    x, y, z, medium, _ = build_axes()
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    xc = 0.5 * (x[:-1] + x[1:])
    yc = 0.5 * (y[:-1] + y[1:])
    zc = 0.5 * (z[:-1] + z[1:])

    ix = int(np.argmin(np.abs(xc)))
    Z = np.zeros((nz, ny), dtype=int)
    for j in range(ny):
        for k in range(nz):
            Z[k, j] = code(xc[ix], yc[j], zc[k])
    save_pcolor(y, z, Z, "CHT 网格 X=0（过射流 / YZ）蓝=fluid 金=Cu 红=TIM2",
                "cht_mesh_cut_x0.png", "Y mm", "Z mm")

    iy = int(np.argmin(np.abs(yc)))
    Z = np.zeros((nz, nx), dtype=int)
    for i in range(nx):
        for k in range(nz):
            Z[k, i] = code(xc[i], yc[iy], zc[k])
    save_pcolor(x, z, Z, "CHT 网格 Y=0（中槽 / XZ）蓝=fluid 金=Cu 红=TIM2",
                "cht_mesh_cut_y0.png", "X mm", "Z mm")

    iy8 = int(np.argmin(np.abs(yc - 0.80)))
    Z = np.zeros((nz, nx), dtype=int)
    for i in range(nx):
        for k in range(nz):
            Z[k, i] = code(xc[i], yc[iy8], zc[k])
    save_pcolor(x, z, Z, "CHT 网格 Y=+0.80 mm（侧槽 / XZ）",
                "cht_mesh_cut_y08.png", "X mm", "Z mm")

    def horiz(zval, title, fname):
        ik = int(np.argmin(np.abs(zc - zval)))
        Z = np.zeros((ny, nx), dtype=int)
        for i in range(nx):
            for j in range(ny):
                Z[j, i] = code(xc[i], yc[j], zc[ik])
        save_pcolor(x, y, Z, f"{title}  zc={zc[ik]:.3f} mm", fname, "X mm", "Y mm")

    horiz(0.75, "CHT 网格 Z≈0.75 mm（槽中）", "cht_mesh_cut_z075.png")
    horiz(2.50, "CHT 网格 Z≈2.50 mm（间隙）", "cht_mesh_cut_z250.png")
    horiz(-2.04, "CHT 网格 Z≈−2.04 mm（TIM2）", "cht_mesh_cut_ztim.png")
    horiz(-1.00, "CHT 网格 Z≈−1.00 mm（铜座）", "cht_mesh_cut_zcu.png")

    fig, ax = plt.subplots(figsize=(4.0, 6.2), dpi=120)
    ax.set_xlim(0, 10)
    ax.set_ylim(Z_TIM_BOT - 0.25, Z_IN + 0.35)
    ax.axis("off")
    bands = [
        (Z_TIM_BOT, Z_CU_BOT, "#c0392b", "TIM2 80 μm"),
        (Z_CU_BOT, Z_IMP, "#d4a017", "Cu base 2.0"),
        (Z_IMP, Z_RIB, "#85c1e9", "槽/肋 1.50"),
        (Z_RIB, Z_LID, "#5dade2", "间隙 H=2.0"),
        (Z_LID, Z_IN, "#aed6f1", "孔+箱"),
    ]
    for z0, z1, col, lab in bands:
        ax.add_patch(Rectangle((1.4, z0), 4.6, z1 - z0, facecolor=col, edgecolor="#222", lw=0.6))
        ax.text(6.4, 0.5 * (z0 + z1), lab, va="center", fontsize=9)
    ax.set_title("Z 堆叠 mm")
    fig.tight_layout()
    p = os.path.join(OUT, "cht_stack_bar.png")
    fig.savefig(p, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", p)
    print("done", medium)


if __name__ == "__main__":
    main()
