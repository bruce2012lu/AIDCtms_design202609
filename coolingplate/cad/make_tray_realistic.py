# -*- coding: utf-8 -*-
"""Tray plan aligned with the Lenovo GB300 photo, plus one NVL2 flow detail.

Photo orientation: front at the left, rear panel at the right, inlet UQD at the
top of the rear edge, outlet UQD at the bottom, 50 V bus between them.
Cold-plate outlines use the design envelopes (B300 95x75, Grace 200x120).
Zone blocks follow the photo's order; they are not a measured chassis ICD.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False

OUT = Path(__file__).resolve().parent / "out" / "asm0921"

SUP = "#1f6fb2"
RET = "#c0392b"
INK = "#1c2b3a"
MUTED = "#5c6b7a"
COPPER = "#e0a36a"
GRACE_CU = "#d08a4e"
DIE = "#9a3b32"
HBM = "#e4d09a"
MEM = "#ead9a4"
PCB = "#d7efe4"
AIR = "#eef2f5"
AIR_E = "#c5ced6"


def tube(ax, pts, color, lw=2.6, z=5):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round",
            solid_joinstyle="round", zorder=z)
    ax.annotate(
        "",
        xy=pts[-1],
        xytext=pts[-2],
        arrowprops=dict(arrowstyle="-|>", color=color, lw=lw * 0.55,
                        mutation_scale=9),
        zorder=z + 1,
    )


def label(ax, x, y, text, fs=7.5, color=INK, ha="center", va="center", z=6):
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, color=color, zorder=z)


def air(ax, x, y, w, h, text, fs=7.2):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.4,rounding_size=3",
        facecolor=AIR, edgecolor=AIR_E, lw=0.7, zorder=1,
    ))
    label(ax, x + w / 2, y + h / 2, text, fs, MUTED)


def grace(ax, x0, y0, detail=False):
    """Envelope 120 mm along +X (depth, rear at high local v) by 200 mm along +Y.

    Inlet fitting at local (u=0, v=78): low-Y edge, toward the rear plenum.
    Outlet fitting at local (u=200, v=28): high-Y edge, toward the front plenum.
    """
    ax.add_patch(Rectangle((x0, y0), 120, 200, facecolor=GRACE_CU,
                           edgecolor="#6a3e1c", lw=0.9, zorder=3))
    # front return plenum (low v) and rear supply plenum (high v)
    ax.add_patch(Rectangle((x0 + 6, y0 + 8), 16, 184, facecolor="#f6d0cb",
                           edgecolor=RET, lw=0.6, zorder=4))
    ax.add_patch(Rectangle((x0 + 98, y0 + 8), 16, 184, facecolor="#d6e6f5",
                           edgecolor=SUP, lw=0.6, zorder=4))
    # memory windows
    for u in (14, 136):
        ax.add_patch(Rectangle((x0 + 25, y0 + u), 70, 50, facecolor=MEM,
                               edgecolor="#a89050", lw=0.5, zorder=4))
        n = 6 if detail else 4
        for i in range(n):
            yy = y0 + u + 6 + i * (40 / n)
            ax.plot([x0 + 28, x0 + 92], [yy, yy], color="#8a7040", lw=0.4, zorder=5)
    # CPU window 40 x 32 mm, centered: local u 80-120, v 44-76
    ax.add_patch(Rectangle((x0 + 44, y0 + 80), 32, 40, facecolor="#f3d2cc",
                           edgecolor=DIE, lw=0.7, zorder=4))
    ncpu = 16 if detail else 8
    for i in range(ncpu):
        yy = y0 + 82 + i * (36 / ncpu)
        ax.plot([x0 + 46, x0 + 74], [yy, yy], color=DIE, lw=0.45 if detail else 0.35, zorder=5)
    # Flow runs from the rear plenum (right) toward the front plenum (left).
    ax.annotate(
        "", xy=(x0 + 28, y0 + 100), xytext=(x0 + 40, y0 + 100),
        arrowprops=dict(arrowstyle="-|>", color=SUP, lw=0.9, mutation_scale=7),
        zorder=6,
    )
    # Side fittings sit on the plenum they feed. Low-Y edge is the inlet,
    # high-Y edge is the outlet; both boards use this same copper orientation.
    inn = (x0 + 106, y0)
    out = (x0 + 14, y0 + 200)
    ax.plot([inn[0], inn[0]], [y0, y0 + 10], color=SUP, lw=1.6, zorder=5)
    ax.plot([out[0], out[0]], [y0 + 190, y0 + 200], color=RET, lw=1.6, zorder=5)
    ax.add_patch(Circle(inn, 4.2, facecolor=SUP, edgecolor="white", lw=0.4, zorder=6))
    ax.add_patch(Circle(out, 4.2, facecolor=RET, edgecolor="white", lw=0.4, zorder=6))
    return inn, out


def gpu(ax, x0, y0, detail=False):
    """95 mm along +Y, 75 mm along +X. Inlet edge is local v=75 (rear, +X)."""
    ax.add_patch(Rectangle((x0, y0), 75, 95, facecolor=COPPER,
                           edgecolor="#6a3e1c", lw=0.9, zorder=3))
    # supply plenum covers the jet field; the lid return is a separate top groove
    ax.add_patch(Rectangle((x0 + 22, y0 + 12), 50, 72, facecolor="#d6e6f5",
                           edgecolor=SUP, lw=0.4, alpha=0.55, zorder=4))
    # dies and HBM
    for u in (19, 49):
        ax.add_patch(Rectangle((x0 + 23.5, y0 + u), 28, 27, facecolor="#f0c2b4",
                               edgecolor=DIE, lw=0.55, zorder=5))
    for u in (5, 79):
        for v in (13.5, 25.5, 37.5, 49.5):
            ax.add_patch(Rectangle((x0 + v, y0 + u), 10, 11, facecolor=HBM,
                                   edgecolor="#a89050", lw=0.3, zorder=5))
    # lid return on the outer top face, in the gap between the two dies,
    # then jog to the return port so it does not land in the inlet slot
    ax.plot([x0 + 8, x0 + 66, x0 + 75], [y0 + 46, y0 + 46, y0 + 56],
            color=RET, lw=2.0, zorder=6)
    # corner windows: HBM supply, inlet end, no jets
    ax.add_patch(Rectangle((x0 + 62, y0 + 16), 8, 8, facecolor=SUP,
                           edgecolor="none", alpha=0.8, zorder=6))
    ax.add_patch(Rectangle((x0 + 62, y0 + 71), 8, 8, facecolor=SUP,
                           edgecolor="none", alpha=0.8, zorder=6))
    if detail:
        xs = list(range(22, 44, 3)) + list(range(52, 74, 3))
        ys = [26.9 + 3 * i for i in range(8)]
        rad = 0.85
    else:
        xs = (24, 31, 38, 43, 54, 61, 68, 73)
        ys = (29, 36, 43, 47)
        rad = 1.15
    for u in xs:
        for v in ys:
            ax.add_patch(Circle((x0 + v, y0 + u), rad, facecolor=SUP,
                                edgecolor="none", zorder=7))
    # ports on the rear edge, side by side across the width
    inn = (x0 + 75, y0 + 40)
    out = (x0 + 75, y0 + 56)
    ax.add_patch(Circle(inn, 2.6, facecolor=SUP, edgecolor="white", lw=0.3, zorder=7))
    ax.add_patch(Circle(out, 2.6, facecolor=RET, edgecolor="white", lw=0.3, zorder=7))
    return inn, out


def hop(ax, x0, x1, y, color, lw, jump_x):
    """Horizontal run with a semicircle so a crossing reads as a bridge, not a tee."""
    import math
    r = 7.0
    ax.plot([x0, jump_x - r], [y, y], color=color, lw=lw,
            solid_capstyle="butt", zorder=5)
    xs, ys = [], []
    for i in range(17):
        ang = math.pi - i * math.pi / 16.0
        xs.append(jump_x + r * math.cos(ang))
        ys.append(y + r * math.sin(ang))
    ax.plot(xs, ys, color=color, lw=lw, solid_capstyle="round", zorder=6)
    ax.plot([jump_x + r, x1], [y, y], color=color, lw=lw,
            solid_capstyle="butt", zorder=5)


def fig14():
    # Photo-like aspect: depth longer than width. Units are scheme millimetres.
    W, D = 480, 900
    fig, ax = plt.subplots(figsize=(15.6, 9.15))
    ax.set_xlim(-8, D + 36)
    ax.set_ylim(-28, W + 22)
    ax.set_aspect("equal")
    ax.set_axis_off()
    ax.add_patch(Rectangle((0, 0), D, W, facecolor="white", edgecolor="#8d99a6", lw=1.1))

    # Packed like the Lenovo photo: tall drive cage on the left, 1G across the
    # upper row, I/O cards along the lower row, then the fan wall.
    air(ax, 14, 16, 96, 448, "E1.S\nNVMe ×8")
    air(ax, 118, 244, 320, 220, "1G")
    air(ax, 118, 16, 74, 210, "Front\nI/O")
    air(ax, 200, 16, 74, 100, "PCIe")
    air(ax, 200, 124, 74, 102, "OSFP ×2")
    air(ax, 282, 16, 74, 120, "PDB")
    air(ax, 282, 144, 74, 82, "BF3")
    air(ax, 364, 16, 74, 210, "CX8 ×2")
    ax.add_patch(Rectangle((448, 16), 32, 448, facecolor="#dde3e8",
                           edgecolor="#b7c3ce", lw=0.7, zorder=1))
    label(ax, 464, 240, "Fan\nBay", 7, MUTED)
    air(ax, 488, 16, 46, 168, "M.2", 7)
    air(ax, 488, 196, 46, 110, "BMC", 7)
    air(ax, 488, 318, 46, 146, "HMC", 7)

    # Two NVL2 PCBs. Board 1 is the inlet side (top), board 2 the outlet side.
    for y0, tag in ((256, "1"), (24, "2")):
        ax.add_patch(Rectangle((545, y0 - 6), 250, 212, facecolor=PCB,
                               edgecolor="#2f6d4a", lw=0.7, zorder=2))
        label(ax, 552, y0 + 100, tag, 11, "#1d5a38", z=9)

    g_in, g_out = {}, {}
    for key, y0 in (("b1", 256), ("b2", 24)):
        g_in[key], g_out[key] = grace(ax, 560, y0, detail=False)

    ports = []
    for ys in ((256, 361), (24, 129)):
        for y0 in ys:
            ports.append(gpu(ax, 696, y0, detail=False))

    # Rear corridor: supply and return rails inboard of the 50 V connector.
    ax.add_patch(Rectangle((848, 0), 52, W, facecolor="#eceff2",
                           edgecolor="#9aa6b2", lw=0.8, zorder=2))
    label(ax, 874, 300, "后\n面\n板", 8, MUTED)
    ax.add_patch(FancyBboxPatch((856, 188), 36, 104, boxstyle="round,pad=0.3",
                                facecolor="#2c333a", edgecolor="#1b2026", lw=0.6, zorder=3))
    label(ax, 874, 240, "50 V\n母排", 7, "white")
    ax.add_patch(FancyBboxPatch((860, 400), 28, 52, boxstyle="round,pad=0.3",
                                facecolor="#d6e6f5", edgecolor=SUP, lw=1.0, zorder=4))
    label(ax, 874, 426, "进液\nUQD", 7, SUP)
    ax.add_patch(FancyBboxPatch((860, 28), 28, 52, boxstyle="round,pad=0.3",
                                facecolor="#f6d0cb", edgecolor=RET, lw=1.0, zorder=4))
    label(ax, 874, 54, "出液\nUQD", 7, RET)

    # Rails sit in the corridor between the GPU rear edges and the panel.
    # Return stubs cross the supply rail in plan; the hop means they pass above it.
    ax.plot([792, 792], [12, 432], color=SUP, lw=4.2, solid_capstyle="round", zorder=4)
    ax.plot([820, 820], [36, 470], color=RET, lw=4.2, solid_capstyle="round", zorder=4)
    hop(ax, 792, 874, 432, SUP, 3.0, 820)
    tube(ax, [(874, 432), (874, 400)], SUP, 3.0)
    tube(ax, [(820, 36), (874, 36), (874, 80)], RET, 3.0)
    for inn, out in ports:
        tube(ax, [inn, (792, inn[1])], SUP, 1.6)
        hop(ax, out[0], 820, out[1], RET, 1.6, 792)

    # Grace. Same copper orientation on both boards: inlet at low Y.
    # Board 1 inlet is the aisle; its outlet is the top margin.
    # Board 2 inlet is the bottom margin; its outlet is the aisle.
    tube(ax, [g_in["b1"], (g_in["b1"][0], 232), (792, 232)], SUP, 2.2)
    hop(ax, g_out["b1"][0], 820, 468, RET, 2.0, 792)
    ax.plot([g_out["b1"][0], g_out["b1"][0]], [g_out["b1"][1], 468],
            color=RET, lw=2.0, zorder=5)
    tube(ax, [g_in["b2"], (g_in["b2"][0], 12), (792, 12)], SUP, 2.2)
    hop(ax, g_out["b2"][0], 820, 240, RET, 2.0, 792)
    ax.plot([g_out["b2"][0], g_out["b2"][0]], [g_out["b2"][1], 240],
            color=RET, lw=2.0, zorder=5)

    ax.add_patch(Rectangle((538, 8), 300, 464, fill=False, edgecolor="#b3611f",
                           lw=1.0, linestyle=(0, (4, 3)), zorder=2))
    label(ax, 688, -16, "橙框内是液冷区，对应图 9 右侧。左为风扇仓，右为后面板。", 8, "#b3611f")
    label(ax, 40, W + 12, "前  ·  风冷", 8, MUTED, ha="left")
    label(ax, 760, W + 12, "后  ·  进液在上，出液在下", 8, MUTED, ha="left")

    fig.suptitle("图 11    按联想 GB300 托盘俯视布置的水路（方案坐标，不是机箱 ICD）",
                 fontsize=13, color="#0b2748", y=0.98)
    fig.text(
        0.5, 0.012,
        "蓝供液，红回液。深橙是 Grace 微通道冷板，浅橙是 B300 射流冷板。"
        "  回液管跨过供液轨处有一个拱起，表示从上方越过、并不接通。"
        "  风冷区的名称与图 9 相同，位置是对照用的，不是机箱实测坐标。",
        ha="center", fontsize=8, color=MUTED,
    )
    p = OUT / "fig14_tray_lenovo_layout.png"
    fig.savefig(p, dpi=160, facecolor="white")
    plt.close(fig)
    return p


def fig15():
    """One NVL2, large enough to read jets, slots and Grace channels."""
    fig, ax = plt.subplots(figsize=(15.4, 8.4))
    ax.set_xlim(530, 1040)
    ax.set_ylim(200, 530)
    ax.set_aspect("equal")
    ax.set_axis_off()

    ax.add_patch(Rectangle((540, 236), 250, 228, facecolor=PCB,
                           edgecolor="#2f6d4a", lw=0.8, zorder=1))
    label(ax, 620, 500, "板 1", 9, "#1d5a38", ha="left")

    gin, gout = grace(ax, 552, 248, detail=True)
    inn1, out1 = gpu(ax, 700, 248, detail=True)
    inn2, out2 = gpu(ax, 700, 353, detail=True)

    ax.plot([812, 812], [214, 490], color=SUP, lw=5, solid_capstyle="round", zorder=3)
    ax.plot([842, 842], [214, 490], color=RET, lw=5, solid_capstyle="round", zorder=3)
    label(ax, 812, 504, "供液", 8, SUP)
    label(ax, 848, 504, "回液", 8, RET)
    for inn, out in ((inn1, out1), (inn2, out2)):
        tube(ax, [inn, (812, inn[1])], SUP, 1.8)
        hop(ax, out[0], 842, out[1], RET, 1.7, 812)
    tube(ax, [gin, (gin[0], 220), (812, 220)], SUP, 2.2)
    ax.plot([gout[0], gout[0]], [gout[1], 478], color=RET, lw=2.0, zorder=5)
    hop(ax, gout[0], 842, 478, RET, 2.0, 812)

    legend = [
        ((SUP, 0.35), "进液腔，靠 GPU"),
        (RET, "出液腔，靠风扇"),
        ("#f0c2b4", "计算 die，上面是射流孔"),
        (HBM, "HBM，角窗供水"),
        (MEM, "内存槽，与 CPU 并联"),
    ]
    y = 470
    for color, text in legend:
        if isinstance(color, tuple):
            ax.add_patch(Rectangle((878, y), 16, 10, facecolor="#d6e6f5",
                                   edgecolor=SUP, lw=0.6, zorder=6))
        else:
            ax.add_patch(Rectangle((878, y), 16, 10, facecolor=color,
                                   edgecolor="#6a5a4a", lw=0.4, zorder=6))
        label(ax, 900, y + 5, text, 8, INK, ha="left")
        y -= 22
    label(ax, 878, y - 4,
          "红线在盖顶外侧，沿两 die 间隙回到后面。\n拱起表示回液从供液轨上方越过。",
          7.5, MUTED, ha="left")

    fig.suptitle("图 12    一块 NVL2：Grace 微通道与 B300 射流冷板接到同一对供回轨",
                 fontsize=13, color="#0b2748", y=0.98)
    fig.text(
        0.5, 0.015,
        "射流孔按 8×8 ×2、节距 3 mm 绘制。CPU 槽在图中抽成 16 条，真实为 48 条、宽 0.40 mm、节距 0.80 mm。"
        "  板 2 用同一块铜，进液接头改到机箱下沿。",
        ha="center", fontsize=8, color=MUTED,
    )
    p = OUT / "fig15_nvl2_flows.png"
    fig.savefig(p, dpi=160, facecolor="white")
    plt.close(fig)
    return p


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for p in (fig14(), fig15()):
        print(p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
