# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.2 演示版 —— 图表生成脚本
所有数值严格取自《算力冷却商业调研报告_v3.2_20260822.html》，不得自行增改。
输出：与本脚本同目录的 PNG（200+ dpi）。
运行： python make_charts.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.path import Path
import matplotlib.path as mpath
import numpy as np

# ---------- 中文字体 ----------
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "DengXian"]
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["savefig.dpi"] = 300
plt.rcParams["figure.dpi"] = 300

OUT = os.path.dirname(os.path.abspath(__file__))

# ---------- 主色系（延续报告） ----------
NAVY = "#0b2239"
BLUE = "#175cd3"
TEAL = "#087a70"
RED = "#b42318"
AMBER = "#9a6700"
GREY = "#5d687a"
LGREY = "#e4e8ee"
BG = "#ffffff"

# 300 dpi：保证在 16:9 幻灯片中放大后有效分辨率仍高于 200 dpi
DPI = 300


def _wrap(text, fig_w_in, fontsize):
    """按 CJK=1、ASCII=0.55 的估算宽度硬折行，防止图注溢出画布。"""
    budget = (fig_w_in * 0.985) / (fontsize / 72.0)
    out = []
    for para in text.split("\n"):
        line, w = "", 0.0
        for ch in para:
            cw = 1.0 if ord(ch) > 0x2E7F else 0.55
            if w + cw > budget and line:
                out.append(line)
                line, w = "", 0.0
            line += ch
            w += cw
        out.append(line)
    return "\n".join(out)


def _finish(fig, ax_list, note, fname, left=0.075, bottom=0.26, top=0.95,
            right=0.965, wspace=None, spines=True):
    """统一图注：单位 / 口径 / 数据性质 / 来源。底部预留固定留白，避免图注与刻度重叠。"""
    if not isinstance(ax_list, (list, tuple)):
        ax_list = [ax_list]
    for ax in ax_list:
        ax.set_facecolor(BG)
        if spines:
            for s in ("top", "right"):
                ax.spines[s].set_visible(False)
            for s in ("left", "bottom"):
                ax.spines[s].set_color("#c9d1dc")
            ax.grid(axis="y", color=LGREY, lw=0.8, zorder=0)
        ax.tick_params(colors=GREY, labelsize=9.5)
        ax.set_axisbelow(True)
    fig.patch.set_facecolor(BG)
    fs = 8.0
    fw, fh = fig.get_size_inches()
    wrapped = _wrap(note, fw, fs)
    n_lines = wrapped.count("\n") + 1
    need = 0.025 + n_lines * (fs * 1.62 / 72.0) / fh
    kw = dict(left=left, right=right, top=top, bottom=max(bottom, need + 0.03))
    if wspace is not None:
        kw["wspace"] = wspace
    fig.subplots_adjust(**kw)
    fig.text(0.010, 0.014, wrapped, fontsize=fs, color=GREY, va="bottom", ha="left",
             linespacing=1.62)
    path = os.path.join(OUT, fname)
    fig.savefig(path, dpi=DPI, facecolor=BG)
    plt.close(fig)
    print("saved", fname)


def _plain(fig, fname):
    fig.patch.set_facecolor(BG)
    path = os.path.join(OUT, fname)
    fig.savefig(path, dpi=DPI, facecolor=BG, bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    print("saved", fname)


YEARS = [2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032]

# ============================================================
# c01 需求驱动：用电与容量（表 2.2 / 2.5.2）
# ============================================================
def c01():
    twh_lo = [485, 555, 635, 725, 830, 950, 980, 1020]
    twh_hi = [485, 555, 635, 725, 830, 950, 1090, 1240]
    dem_lo = [82, 100, 121, 148, 180, 219, 225, 235]
    dem_hi = [82, 100, 121, 148, 180, 219, 255, 290]
    sup_lo = [103, 118, 134, 153, 175, 200, 215, 230]
    sup_hi = [103, 118, 134, 153, 175, 200, 235, 270]

    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    ax2 = ax.twinx()
    ax.fill_between(YEARS, twh_lo, twh_hi, color=BLUE, alpha=0.16, zorder=2)
    ax.plot(YEARS, twh_lo, color=BLUE, lw=2.6, marker="o", ms=5, zorder=3,
            label="全球数据中心用电（TWh，左轴）")
    ax2.fill_between(YEARS, dem_lo, dem_hi, color=TEAL, alpha=0.15, zorder=2)
    ax2.plot(YEARS, dem_lo, color=TEAL, lw=2.4, marker="s", ms=4.5, zorder=3,
             label="关键 IT 容量需求（GW，右轴）")
    ax2.fill_between(YEARS, sup_lo, sup_hi, color=NAVY, alpha=0.12, zorder=2)
    ax2.plot(YEARS, sup_lo, color=NAVY, lw=2.4, ls="--", marker="^", ms=4.5, zorder=3,
             label="设施供给 / 市场容量（GW，右轴）")

    for x, y, t, off in [(2025, 485, "485", (0, 12)), (2030, 950, "950", (-22, 4))]:
        ax.annotate(t, (x, y), textcoords="offset points", xytext=off,
                    ha="center", fontsize=11, color=BLUE, fontweight="bold")
    for x, y, t, off in [(2025, 82, "82", (16, -4)), (2030, 219, "219", (20, 2))]:
        ax2.annotate(t, (x, y), textcoords="offset points", xytext=off,
                     ha="center", fontsize=10.5, color=TEAL, fontweight="bold")
    for x, y, t, off in [(2025, 103, "103", (-16, 2)), (2030, 200, "200", (-4, -20))]:
        ax2.annotate(t, (x, y), textcoords="offset points", xytext=off,
                     ha="center", fontsize=10.5, color=NAVY, fontweight="bold")

    ax.set_ylim(0, 1450)
    ax.axvspan(2030.5, 2032.5, color="#fff7f6", zorder=1)
    ax.text(2031.5, 100, "2031–2032\n本报告情景模型\n无机构对应端点",
            ha="center", fontsize=8.6, color=RED)

    ax.set_ylabel("用电（TWh）", color=BLUE, fontsize=10.5)
    ax2.set_ylabel("容量（GW）", color=TEAL, fontsize=10.5)
    ax.set_xticks(YEARS)
    ax2.grid(False)
    for s in ("top", "left", "right"):
        ax2.spines[s].set_visible(False)
    ax2.tick_params(colors=GREY, labelsize=9.5)
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="upper left", frameon=False, fontsize=9.5)

    note = ("单位：TWh / GW。口径：用电为 IT 与设施总用电；需求为 continued-momentum 需求情景；供给为 hyperscale+colo+on-prem 设施供给展望，三者不可相加、不可相减。\n"
            "数据性质：2025 与 2030 为机构端点（用电 IEA 机构估计/预测；需求 McKinsey；供给 JLL）；2026–2029 为本报告几何桥接模型；2031–2032 为本报告情景模型（区间）。\n"
            "来源：IEA《Key Questions on Energy and AI》2026-04-16；McKinsey《AI power》2024-10-29 Exhibit 1；JLL《2026 Global Data Center Outlook》2026-01-06。报告表 2.2 / 2.5.2。")
    _finish(fig, ax, note, "c01_power_capacity.png", right=0.925)


# ============================================================
# c02 机柜功率密度（表 3.1）
# ============================================================
def c02():
    labels = ["Lenovo N1380 / SC750 V4\n（54 kW / enclosure）",
              "Huawei Atlas 900 A3\n（计算柜最大）",
              "NVIDIA DGX GB200\n（约）",
              "HPE GB200 NVL72 v4\n（115 kW 液体 + 17 kW 风）",
              "Lenovo GB300 NVL72\n（135 kW TDP / 155 kW peak）",
              "Supermicro DLC-2\n（方案移热能力，非铭牌）",
              "Dell IR7000 + XE8712\n（特定配置最高）"]
    vals = [54, 66, 120, 132, 155, 250, 264]
    colors = [GREY, GREY, BLUE, BLUE, NAVY, AMBER, AMBER]

    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    bars = ax.barh(range(len(vals)), vals, color=colors, height=0.6, zorder=3)
    for i, (b, v) in enumerate(zip(bars, vals)):
        ax.text(v + 4, i, f"{v} kW", va="center", fontsize=11, fontweight="bold",
                color=colors[i])
    ax.set_yticks(range(len(vals)))
    ax.set_yticklabels(labels, fontsize=8.8)
    ax.invert_yaxis()
    ax.set_xlim(0, 320)
    ax.set_xlabel("每机柜 IT 功率（kW）", fontsize=10.5, color=GREY)
    ax.grid(axis="x", color=LGREY, lw=0.8, zorder=0)
    ax.grid(axis="y", visible=False)
    ax.text(0.99, 0.97, "橙色两项不是固定 IT 铭牌功率：\nSupermicro 250 kW 为方案/in-rack CDU 移热能力；\nDell 264 kW 为特定配置最高值",
            transform=ax.transAxes, ha="right", va="top", fontsize=8.8, color=AMBER,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fffaf0", ec="#f0d9a8"))

    note = ("单位：kW / 机柜。口径：原厂公开规格中的机柜级 IT 功率或方案能力，不同厂商定义不一致，仅作密度量级对比，不得互为兼容承诺。\n"
            "数据性质：全部为原厂正式规格（实绩性质，一级来源）；括号内的口径说明取自报告原文。铭牌冷量不能证明平台兼容。\n"
            "来源：Lenovo GB300 Product Guide 2026-08-13 Table 27；Lenovo N1380 Configuration Guide Tables 1–4；Huawei Atlas 900 A3 技术规格；Dell Rack-Scale DLC Guidelines pp.4–5,18–19；HPE / Supermicro / NVIDIA 公开资料。报告表 3.1。")
    _finish(fig, ax, note, "c02_rack_power.png", left=0.235, bottom=0.24)


# ============================================================
# c03 新增投运容量（表 2.5.2）
# ============================================================
def c03():
    lo = [10, 13, 14, 17, 20, 22, 18, 15]
    hi = [14, 17, 19, 22, 25, 28, 30, 32]
    mid = [(a + b) / 2 for a, b in zip(lo, hi)]
    err = [[m - a for m, a in zip(mid, lo)], [b - m for m, b in zip(mid, hi)]]

    fig, ax = plt.subplots(figsize=(11.2, 4.8))
    cols = [BLUE] * 6 + [RED] * 2
    ax.bar(YEARS, mid, color=cols, width=0.58, zorder=3, alpha=0.9)
    ax.errorbar(YEARS, mid, yerr=err, fmt="none", ecolor=NAVY, elinewidth=1.6,
                capsize=6, zorder=4)
    for x, a, b in zip(YEARS, lo, hi):
        ax.text(x, b + 0.9, f"{a}–{b}", ha="center", fontsize=9.6, color=NAVY)
    ax.set_ylabel("年新增投运容量（GW）", fontsize=10.5, color=GREY)
    ax.set_xticks(YEARS)
    ax.set_ylim(0, 38)
    ax.axhline(0, color="#c9d1dc", lw=1)
    ax.text(2028.5, 34.5, "C&W：2025 年末全球在建约 31.7 GW —— 在建 ≠ 当年投运",
            ha="center", fontsize=9.4, color=AMBER,
            bbox=dict(boxstyle="round,pad=0.45", fc="#fff7e8", ec="#f0d9a8"))
    ax.text(2031.5, 3.0, "本报告情景", ha="center", fontsize=8.8, color="#ffffff")

    note = ("单位：GW/年。口径：当年投运（commissioned）容量，不含在建存量与规划管线。\n"
            "数据性质：全部年份均为本报告模型——由 JLL「2026–2030 累计约 100 GW 上线」的累计端点桥接而来，机构未公布逐年投运量；2031–2032（红色）为本报告情景，无机构对应端点。\n"
            "来源：JLL《2026 Global Data Center Outlook》2026-01-06；Cushman & Wakefield《Global Data Center Market Comparison》2026-05-20。报告表 2.5.2。")
    _finish(fig, ax, note, "c03_new_commissioned.png")


# ============================================================
# c04 AI 容量占比：存量口径 vs 新增口径
# ============================================================
def c04():
    lo = [24, 29, 34, 39, 44, 47, 49, 50]
    hi = [30, 35, 41, 46, 50, 53, 56, 60]
    add = [65, 72, 76, 78, 80, 82, 82, 81]

    fig, ax = plt.subplots(figsize=(11.2, 4.9))
    ax.fill_between(YEARS, lo, hi, color=BLUE, alpha=0.20, zorder=2,
                    label="AI 容量占比（存量口径，区间）")
    ax.plot(YEARS, lo, color=BLUE, lw=1.4, zorder=3)
    ax.plot(YEARS, hi, color=BLUE, lw=1.4, zorder=3)
    ax.plot(YEARS, add, color=TEAL, lw=2.8, marker="o", ms=5, zorder=4,
            label="AI 占新增容量比例（本报告模型，2.6 章使用）")
    ax.scatter([2025, 2030], [25, 50], s=95, color=NAVY, zorder=6,
               label="JLL 机构端点（存量口径 约25% → 约50%）")
    ax.annotate("约 25%", (2025, 25), xytext=(6, -22), textcoords="offset points",
                fontsize=10.5, color=NAVY, fontweight="bold")
    ax.annotate("约 50%", (2030, 50), xytext=(-16, -24), textcoords="offset points",
                fontsize=10.5, color=NAVY, fontweight="bold")
    ax.annotate("", xy=(2027.5, 76), xytext=(2027.5, 37.5),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=1.6))
    ax.text(2027.65, 56, "两者不可互换：\n存量份额 ≠ 新增份额\nAI 约占 2026–2030 新增容量的 76%",
            fontsize=9.3, color=RED, va="center")
    ax.set_ylabel("占比（%）", fontsize=10.5, color=GREY)
    ax.set_xticks(YEARS)
    ax.set_ylim(0, 95)
    ax.legend(loc="upper left", frameon=False, fontsize=9.4)

    note = ("单位：%。口径：存量口径 = AI 负载占当年全部数据中心容量比例；新增口径 = AI 占当年新增投运容量比例。两条曲线分母不同，禁止互换。\n"
            "数据性质：存量口径 2025 约25%、2030 约50% 为 JLL 机构估计/预测，其余年份与全部区间边界为本报告模型；新增口径全部为本报告模型（由 JLL 存量端点反算，JLL 未公布新增份额）。\n"
            "来源：JLL《2026 Global Data Center Outlook》2026-01-06。报告表 2.5.2 备注、2.6.3、2.6.4。")
    _finish(fig, ax, note, "c04_ai_share.png")


# ============================================================
# c05 算力基建投资分层 L1 / L2 / L3（表 2.6.5）
# ============================================================
def c05():
    l1b = [169, 203, 250, 297, 319, 321, 325, 322]   # 2031/2032 用区间中值
    l2b = [558, 751, 913, 1120, 1383, 1531, 1570, 1625]
    l3lo = [650, 855, 1040, 1260, 1515, 1640, 1645, 1550]
    l3hi = [805, 1060, 1290, 1570, 1885, 2050, 2145, 2345]

    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    x = np.arange(len(YEARS))
    ax.bar(x, l1b, color=TEAL, width=0.52, zorder=3, label="L1 设施侧 CapEx")
    ax.bar(x, l2b, bottom=l1b, color=BLUE, width=0.52, zorder=3, label="L2 IT 设备投资")
    mid = [(a + b) / 2 for a, b in zip(l3lo, l3hi)]
    err = [[m - a for m, a in zip(mid, l3lo)], [b - m for m, b in zip(mid, l3hi)]]
    ax.errorbar(x, mid, yerr=err, fmt="_", ms=22, color=NAVY, elinewidth=2.0,
                capsize=7, zorder=5, label="L3 = L1 + L2（区间）")
    for i, (a, b) in enumerate(zip(l3lo, l3hi)):
        ax.text(i, b + 60, f"{a:,}\n–{b:,}", ha="center", fontsize=8.6, color=NAVY,
                linespacing=1.15)
    ax.axvspan(5.5, 7.5, color="#fff7f6", zorder=1)
    ax.text(6.5, 3020, "2031–2032 本报告情景", ha="center", fontsize=9, color=RED)
    ax.set_xticks(x)
    ax.set_xticklabels(YEARS)
    ax.set_ylabel("十亿美元", fontsize=10.5, color=GREY)
    ax.set_ylim(0, 3250)
    ax.legend(loc="upper left", frameon=False, fontsize=9.6)
    ax.text(0.015, 0.735, "L2（IT 设备）长期占 L3 的 75%–85%\n与液冷供应商无竞争或替代关系",
            transform=ax.transAxes, ha="left", va="top", fontsize=9.6, color=BLUE,
            bbox=dict(boxstyle="round,pad=0.5", fc="#eaf1fd", ec="#c9d8ff"))

    note = ("单位：十亿美元。口径：L1 = 数据中心围墙内设施侧 CapEx（不含 IT）；L2 = IT 设备投资（服务器/存储/网络）；L3 = L1+L2，不含围墙外电力、OpEx 与融资。柱高为 Base 值，误差棒为 L3 区间。\n"
            "数据性质：L1 与 L3 全部八年均为本报告模型（机构只发布累计口径）；L2 的 AI 部分锚定 IDC 机构估计/预测（2025 3,180 亿、2026 4,970 亿、2029 1.08 万亿、2030 1.21 万亿美元），非 AI 部分与合计为本报告模型；2031–2032 全部为本报告情景。\n"
            "来源：JLL 单位建设成本 2026-01-06；Epoch AI TCO 模型 2026-05-14；IDC AI Infrastructure Tracker 2026 公开更新。报告表 2.6.5。禁止换算为公司收入预算或乘以目标份额。")
    _finish(fig, ax, note, "c05_capex_layers.png")


# ============================================================
# c06 两条路径交叉验证（表 2.6.6）
# ============================================================
def c06():
    yrs = [2025, 2026, 2027, 2028, 2029, 2030]
    a_lim = [476, 657, 827, 976, 1093, 1170]
    a_base = [613, 846, 1066, 1258, 1409, 1508]
    a_acc = [860, 1187, 1496, 1766, 1978, 2116]
    b = [837, 1095, 1328, 1607, 1907, 2062]

    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    ax.plot(yrs, a_acc, color=NAVY, lw=2.6, marker="o", ms=5,
            label="路径 A · 加速情景（McKinsey 累计 9.4 万亿）")
    ax.plot(yrs, b, color=TEAL, lw=2.8, ls="--", marker="D", ms=5,
            label="路径 B 可比值（L3 + 围墙外电力，本报告自下而上）")
    ax.plot(yrs, a_base, color=AMBER, lw=2.2, marker="s", ms=4.5,
            label="路径 A · 基准情景（6.7 万亿）—— 已过时，作下界")
    ax.plot(yrs, a_lim, color=GREY, lw=1.8, ls=":", marker="^", ms=4.5,
            label="路径 A · 受限情景（5.2 万亿）—— 融资收紧压力情景")
    ax.fill_between(yrs, a_acc, b, color=TEAL, alpha=0.12)
    ax.annotate("路径 B 落在 A-加速下方 3%–11%\n逐年吻合良好\n→ 裁决以 A-加速为顶层比对锚",
                xy=(2028.6, 1780), xytext=(2027.35, 780), fontsize=9.6, color=TEAL,
                bbox=dict(boxstyle="round,pad=0.5", fc="#f2fbf7", ec="#b6e4d2"),
                arrowprops=dict(arrowstyle="->", color=TEAL, lw=1.3))
    ax.annotate("A-基准 2025 年 6,130 亿美元\n已低于当年可核验观测值（IDC 3,180 亿 AI IT\n+ 非 AI IT 约 2,400 亿 + IEA 能源侧 >1,000 亿）",
                xy=(2025, 613), xytext=(2025.05, 130), fontsize=9.2, color=RED,
                bbox=dict(boxstyle="round,pad=0.5", fc="#fff7f6", ec="#f6c8c5"),
                arrowprops=dict(arrowstyle="->", color=RED, lw=1.3))
    ax.set_ylabel("十亿美元", fontsize=10.5, color=GREY)
    ax.set_xticks(yrs)
    ax.set_ylim(0, 2500)
    ax.legend(loc="upper left", frameon=False, fontsize=9.2,
              bbox_to_anchor=(0.005, 1.0))

    note = ("单位：十亿美元。口径：路径 A = 机构累计总额按增长指数向量年度化；路径 B = 自下而上（新增投运 GW × 每 MW 强度 + IDC 实测 IT 支出 + 围墙外可归属电力）。两条路径不取平均。\n"
            "数据性质：路径 A 的累计总额（AI 3.7/5.2/7.9 万亿 + 传统 IT 1.5 万亿）为 McKinsey 机构预测，年度分配为本报告模型；路径 B 全部为本报告模型。\n"
            "来源：McKinsey《The cost of compute》2025-04-28 Exhibit 2 与 Methodology；IDC AI Infrastructure Tracker 2026；IEA《World Energy Investment 2026》2026-05。报告表 2.6.6。")
    _finish(fig, ax, note, "c06_path_ab.png")


# ============================================================
# c07 液冷设备市场 Bear/Base/Bull（表 2.5.3）
# ============================================================
def c07():
    bear = [25, 30, 37, 47, 60, 82, 86, 90]
    base = [30, 37, 46, 57, 70, 88, 101, 115]
    bull = [35, 44, 55, 68, 80, 100, 120, 140]

    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    ax.fill_between(YEARS, bear, bull, color=BLUE, alpha=0.16, zorder=2,
                    label="Bear–Bull 区间")
    ax.plot(YEARS, bull, color=BLUE, lw=1.4, alpha=0.7, zorder=3)
    ax.plot(YEARS, bear, color=BLUE, lw=1.4, alpha=0.7, zorder=3)
    ax.plot(YEARS, base, color=NAVY, lw=3.0, marker="o", ms=5.5, zorder=4, label="Base")
    ax.scatter([2025, 2029], [30, 70], s=190, facecolor="none", edgecolor=RED,
               lw=2.4, zorder=6, label="Dell'Oro 机构端点（仅此两点）")
    for x, y, t in [(2025, 30, "接近 30 亿美元\n机构估计"), (2029, 70, "约 70 亿美元\n机构预测")]:
        ax.annotate(t, (x, y), xytext=(10, -34), textcoords="offset points",
                    fontsize=9.6, color=RED, fontweight="bold")
    for x, lo, hi in zip(YEARS, bear, bull):
        ax.text(x, hi + 4, f"{lo}–{hi}", ha="center", fontsize=9.2, color=GREY)
    ax.annotate("2030 存在 Dell'Oro 新版 DLC「超过 80 亿美元」\n造成的预测版本跳点，不解释为有机同比",
                xy=(2030, 88), xytext=(2026.2, 122), fontsize=9.3, color=AMBER,
                bbox=dict(boxstyle="round,pad=0.5", fc="#fff7e8", ec="#f0d9a8"),
                arrowprops=dict(arrowstyle="->", color=AMBER, lw=1.3))
    ax.axvspan(2030.5, 2032.5, color="#fff7f6", zorder=1)
    ax.text(2031.5, 12, "2031–2032\n本报告情景\n无机构端点", ha="center", fontsize=8.8, color=RED)
    ax.set_ylabel("全球液冷设备制造商收入（亿美元）", fontsize=10.5, color=GREY)
    ax.set_xticks(YEARS)
    ax.set_ylim(0, 168)
    ax.legend(loc="upper left", frameon=False, fontsize=9.5)

    note = ("单位：亿美元。口径：全球液冷设备制造商收入（DLC + 浸没 + RDHx），不含服务器整机、不含宽产业、不含设施侧一次侧与安装工程；不得与任何其他分母相加。\n"
            "数据性质：仅 2025 Base（Dell'Oro 机构估计）与 2029 Base（Dell'Oro 机构预测）有机构端点；2026–2028、2030 及全部区间边界为本报告模型；2031–2032 为本报告情景。\n"
            "来源：Dell'Oro《Data Center Liquid Cooling Advanced Research》摘要 2026-01-08；《January-2026 DCPI Forecast》2026-02-10。报告表 2.5.2 / 2.5.3。裁决：70 亿美元合理，confidence 0.88，valid_until 2027-02-28。")
    _finish(fig, ax, note, "c07_lc_scenarios.png")


# ============================================================
# c08 Dell'Oro 四个版本隔离
# ============================================================
def c08():
    fig, ax = plt.subplots(figsize=(11.2, 5.0))
    items = [
        ("July-2025 DCPI Forecast\n摘要 2025-08-15", [(2024, 11), (2029, 58)],
         "DLC 子集", GREY, "o"),
        ("Liquid Cooling Advanced Research\n摘要 2026-01-08", [(2025, 30), (2029, 70)],
         "全液冷（DLC+浸没+RDHx）", BLUE, "s"),
        ("January-2026 DCPI Forecast\n摘要 2026-02-10", [(2030, 80)],
         "DLC 更新预测（>80）", TEAL, "^"),
    ]
    for name, pts, bnd, c, m in items:
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        ax.scatter(xs, ys, s=210, color=c, marker=m, zorder=5, label=f"{name}　|　{bnd}")
        for x, y in pts:
            ax.annotate(f"{y}", (x, y), xytext=(0, 13), textcoords="offset points",
                        ha="center", fontsize=11.5, color=c, fontweight="bold")
    ax.annotate("", xy=(2029, 58), xytext=(2029, 70),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2.0))
    ax.text(2029.18, 64, "70 − 58 = 12\n不是浸没/RDHx 规模\n（跨版本、跨研究，禁止相减）",
            fontsize=9.6, color=RED, va="center", fontweight="bold")
    ax.text(2023.75, 62,
            "第四个版本：August-2026 DCPI Forecast（2026-08-19）\n"
            "DCPI 2030 达 1,200 亿美元、2025–2030 CAGR 22%\n"
            "边界已扩展，是 2.7 章组③ 的唯一分母基准，不得与前三版拼接",
            fontsize=8.8, color=AMBER, va="top", linespacing=1.75,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fff7e8", ec="#f0d9a8"))
    ax.set_xlim(2023.5, 2031)
    ax.set_ylim(0, 112)
    ax.set_xticks([2024, 2025, 2026, 2027, 2028, 2029, 2030])
    ax.set_ylabel("亿美元", fontsize=10.5, color=GREY)
    ax.legend(loc="upper left", frameon=False, fontsize=9.0,
              bbox_to_anchor=(-0.01, 1.02), labelspacing=0.9)

    note = ("单位：亿美元。口径：三组数字分属 DLC 子集、全液冷、DLC 更新预测三个不同边界，且来自三个不同发布版本；底层逐年表与方法为付费内容，不可见。\n"
            "数据性质：2024/2025 为机构估计，2029/2030 为机构预测。禁止：母子精确拆分、跨版本相减、连成连续年度曲线。\n"
            "来源：Dell'Oro 2025-08-15 / 2026-01-08 / 2026-02-10 / 2026-08-19 公开摘要。报告表 2.5.3、证据台账 D01、G05、G06、K01。")
    _finish(fig, ax, note, "c08_delloro_versions.png")


# ============================================================
# c09 三组分母对比（表 2.7.2）—— 核心页
# ============================================================
def c09():
    g1 = [(0.3, 0.5), (0.3, 0.5), (0.3, 0.5), (0.3, 0.5), (0.3, 0.5), (0.4, 0.6), (0.4, 0.7), (0.4, 0.9)]
    g2 = [(1.3, 2.3), (1.3, 2.4), (1.3, 2.5), (1.4, 2.6), (1.7, 2.9), (2.3, 3.6), (2.2, 4.5), (2.3, 5.6)]
    g3 = [(5, 9), (5, 8), (5, 8), (5, 8), (5, 8), (6, 9), (6, 10), (6, 11)]

    fig, ax = plt.subplots(figsize=(11.2, 5.1))
    for data, c, lab in [(g1, TEAL, "组① 占 L3 算力基建总投资（最宽分母）"),
                         (g2, BLUE, "组② 占 L1 设施侧 CapEx（中等分母）"),
                         (g3, NAVY, "组③ 占 DCPI 设备市场（最窄、唯一可谈份额）")]:
        lo = [d[0] for d in data]
        hi = [d[1] for d in data]
        ax.fill_between(YEARS, lo, hi, color=c, alpha=0.25, zorder=3)
        ax.plot(YEARS, hi, color=c, lw=2.2, zorder=4, label=lab)
        ax.plot(YEARS, lo, color=c, lw=2.2, zorder=4)
    ax.set_yscale("log")
    ax.set_yticks([0.3, 0.5, 1, 2, 3, 5, 8, 11])
    ax.set_yticklabels(["0.3%", "0.5%", "1%", "2%", "3%", "5%", "8%", "11%"])
    ax.set_ylim(0.24, 120)
    ax.set_xticks(YEARS)
    ax.grid(axis="y", which="major", color=LGREY, lw=0.7)

    # 30 倍标注（2032：0.4% vs 11%）
    ax.annotate("", xy=(2032, 0.4), xytext=(2032, 11),
                arrowprops=dict(arrowstyle="<->", color=RED, lw=2.4))
    ax.text(2031.85, 2.1, "同一年\n约 30 倍", ha="right", fontsize=13, color=RED,
            fontweight="bold", va="center")
    ax.text(2025.05, 88, "同一个分子（液冷设备制造商收入），换三个分母 → 结论量级完全不同",
            fontsize=11.5, color=NAVY, fontweight="bold")
    ax.set_ylabel("液冷设备收入占比（%，对数刻度）", fontsize=10.5, color=GREY)
    ax.legend(loc="upper left", frameon=False, fontsize=9.8, ncol=1,
              bbox_to_anchor=(0.005, 0.86))

    note = ("单位：%（对数刻度）。分子固定为 2.5.3 的液冷设备制造商收入序列。区间算法：下界 = 分子下界 ÷ 分母上界，上界 = 分子上界 ÷ 分母下界（最保守最宽）。\n"
            "数据性质：全部八年、全部三组均为本报告模型。分子仅有 2025 与 2029 两个 Dell'Oro 机构端点；组①/组②的分母全部为本报告模型；组③分母只有 2030 年 1,200 亿美元为 Dell'Oro 机构预测。没有任何机构发布过本图中的任何一个比例。\n"
            "来源：Dell'Oro 2026-01-08 / 2026-08-19；报告表 2.7.2。相对量级 confidence 0.80；任一点值 confidence 0.35，禁止点值引用。valid_until 2027-02-28。")
    _finish(fig, ax, note, "c09_three_denominators.png")


# ============================================================
# c10 分母版本敏感性（表 2.7.4）
# ============================================================
def c10():
    fig, ax = plt.subplots(figsize=(11.0, 4.6))
    labels = ["2029 年占比\nJuly-2025 版分母\n（DCPI 2029 = 631 亿美元）",
              "2030 年占比\nJanuary-2026 版分母\n（DCPI 2030 > 800 亿美元）",
              "2029 年占比\nAugust-2026 版分母\n（新边界）",
              "2030 年占比\nAugust-2026 版分母\n（DCPI 2030 = 1,200 亿美元）"]
    lo = [10, 10, 5, 6]
    hi = [13, 13, 8, 9]
    cols = [GREY, GREY, NAVY, NAVY]
    x = np.arange(4)
    ax.bar(x, [h - l for l, h in zip(lo, hi)], bottom=lo, color=cols, width=0.45, zorder=3)
    for i, (l, h) in enumerate(zip(lo, hi)):
        ax.text(i, h + 0.45, f"{l}%–{h}%", ha="center", fontsize=13,
                fontweight="bold", color=cols[i])
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=9.0)
    ax.set_ylim(0, 16)
    ax.set_ylabel("液冷占 DCPI 设备市场比例（%）", fontsize=10.5, color=GREY)
    ax.annotate("", xy=(2.5, 14.4), xytext=(0.5, 14.4),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2.0))
    ax.text(1.5, 14.9, "分子未变、年份未变 —— 变化几乎全部来自 Dell'Oro 扩大 DCPI 边界并上调预测，不是液冷竞争地位下降",
            ha="center", fontsize=9.6, color=RED)

    note = ("单位：%。口径：分子为同一条液冷设备制造商收入序列；分母为 Dell'Oro DCPI 的三个不同发布版本，边界不同。\n"
            "数据性质：全部比例为本报告模型；分母端点分别为 Dell'Oro July-2025 / January-2026 / August-2026 版机构预测。三个版本不得拼成一条 DCPI 序列，也不得拼成一条占比序列。\n"
            "来源：Dell'Oro 2025-08-15 / 2026-02-10 / 2026-08-19 公开摘要。报告表 2.7.4。v3.1 的「2029 液冷约占旧版 DCPI 10%–13%」仍然正确 —— 但只在旧版口径下正确。")
    _finish(fig, ax, note, "c10_version_sensitivity.png", bottom=0.35)


# ============================================================
# c11 设施侧液冷投入 vs 设备制造商收入（2.7.5）
# ============================================================
def c11():
    fig, ax = plt.subplots(figsize=(10.6, 4.6))
    ax.bar([0], [390], color=GREY, width=0.42, zorder=3)
    ax.bar([1], [70], bottom=[0], color=NAVY, width=0.42, zorder=3)
    ax.errorbar([1], [70], yerr=[[10], [10]], fmt="none", ecolor=RED,
                elinewidth=2.2, capsize=10, zorder=5)
    ax.text(0, 400, "约 390 亿美元", ha="center", fontsize=15, fontweight="bold", color=GREY)
    ax.text(1, 100, "60–80 亿美元", ha="center", fontsize=15, fontweight="bold", color=NAVY)
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["设施侧「液冷相关支出」\n约 8 GW 液冷新增容量 × 约 485 万美元/MW",
                        "独立液冷设备制造商收入\n（本报告 Bear–Bull 区间，Base 70）"], fontsize=10)
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylabel("2029 年（亿美元）", fontsize=10.5, color=GREY)
    ax.set_ylim(0, 470)
    ax.annotate("", xy=(0.55, 250), xytext=(0.45, 250),
                arrowprops=dict(arrowstyle="->", color=RED, lw=2.2))
    ax.text(0.5, 268, "约 5–6 倍", ha="center", fontsize=16, color=RED, fontweight="bold")
    ax.text(0.5, 200, "差额 = 一次侧冷源、二次管路、安装调试、EPC 与总承包毛利\n不进入独立液冷设备供应商可争夺的池子",
            ha="center", fontsize=10, color=RED,
            bbox=dict(boxstyle="round,pad=0.55", fc="#fff7f6", ec="#f6c8c5"))

    note = ("单位：亿美元（2029 年）。口径：左侧为项目造价科目下的设施侧液冷相关支出；右侧为全球液冷设备制造商收入。两者不是同一分母，不可相减为「利润」。\n"
            "数据性质：左侧单价（液冷冷却装置约 450–520 万美元/MW，风冷约 180 万美元/MW）经三级转述取得，未取得原始文档，只作量级检查；8 GW 与右侧区间为本报告模型/机构端点组合。\n"
            "来源：Turner & Townsend（经三级转述）；Dell'Oro 2026-01-08。报告 2.7.5。这解释了为什么「液冷占 AI 机房造价 15%–33%」与本报告的 1%–6% 并不矛盾。")
    _finish(fig, ax, note, "c11_facility_vs_manufacturer.png", bottom=0.30)


# ============================================================
# c12 Lenovo GB300 Q–ΔP 曲线（表 3.1）
# ============================================================
def c12():
    t = [25, 30, 35, 40, 45]
    lpm = [59, 71, 89, 119, 177]
    psi = [2.3, 3.2, 4.9, 8.5, 18.4]

    fig, ax = plt.subplots(figsize=(11.0, 4.9))
    ax2 = ax.twinx()
    ax.plot(t, lpm, color=BLUE, lw=3.0, marker="o", ms=8, zorder=4, label="流量 Q（LPM，左轴）")
    ax2.plot(t, psi, color=RED, lw=3.0, ls="--", marker="D", ms=7, zorder=4,
             label="压降 ΔP（psi，右轴）")
    for x, y in zip(t, lpm):
        ax.annotate(f"{y}", (x, y), xytext=(0, 11), textcoords="offset points",
                    ha="center", fontsize=11, color=BLUE, fontweight="bold")
    for x, y in zip(t, psi):
        off = (16, -6) if x == 25 else (0, -20)
        ax2.annotate(f"{y}", (x, y), xytext=off, textcoords="offset points",
                     ha="center", fontsize=11, color=RED, fontweight="bold")
    ax.set_xlabel("供液温度 TCS（℃）", fontsize=10.5, color=GREY)
    ax.set_ylabel("流量（LPM / 柜）", fontsize=10.5, color=BLUE)
    ax2.set_ylabel("压降（psi）", fontsize=10.5, color=RED)
    ax.set_xticks(t)
    ax2.grid(False)
    for s in ("top", "left", "right"):
        ax2.spines[s].set_visible(False)
    ax2.tick_params(colors=GREY, labelsize=9.5)
    ax.text(0.03, 0.90, "25→45℃：流量约 3.0 倍，压降约 8.0 倍\n供液温度每升一档，水力代价非线性放大",
            transform=ax.transAxes, fontsize=11, color=NAVY, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.55", fc="#f4f7ff", ec="#c9d8ff"))
    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="center left", frameon=False, fontsize=10,
              bbox_to_anchor=(0.03, 0.55))

    note = ("单位：LPM / psi。口径：Lenovo GB300 NVL72（2026-08-13 update）单柜二次侧 Q–ΔP 曲线；IT 功率 135 kW TDP / 155 kW peak，液体负荷约 90%（121.5–139.5 kW 为本报告推导）。工质 DI water 或 PG25，回液温度未披露。\n"
            "数据性质：全部为原厂正式规格（一级来源）。项目须确认曲线对应工质；不同 OEM 的流量与压降不可相互套用，支路压降不可相加。\n"
            "来源：Lenovo GB300 Product Guide, 2026-08-13, Table 27（证据台账 E01，valid_until 2026-11-30，新 revision 或 BOM 变更即失效）。报告表 3.1。")
    _finish(fig, ax, note, "c12_qdp_curve.png", bottom=0.28, right=0.935)


# ============================================================
# c13 曙光数创 实绩（第 5 章）
# ============================================================
def c13():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.0, 4.4))
    ax1.bar(["浸没", "冷板"], [4.579, 2.986], color=[TEAL, BLUE], width=0.45, zorder=3)
    for i, v in enumerate([4.579, 2.986]):
        ax1.text(i, v + 0.12, f"{v} 亿元", ha="center", fontsize=13, fontweight="bold",
                 color=[TEAL, BLUE][i])
    ax1.set_ylim(0, 6.0)
    ax1.set_title("曙光数创 2025 年收入（实绩）", fontsize=11.5, color=NAVY, pad=10)
    ax1.set_ylabel("亿元人民币", fontsize=10, color=GREY)

    ax2.bar(["浸没", "冷板", "Modine 数据中心分部\n（2026 年 6 月季度）"],
            [36.49, 10.36, 20.2], color=[TEAL, BLUE, AMBER], width=0.45, zorder=3)
    for i, v in enumerate([36.49, 10.36, 20.2]):
        ax2.text(i, v + 1.0, f"{v}%", ha="center", fontsize=13, fontweight="bold",
                 color=[TEAL, BLUE, AMBER][i])
    ax2.set_ylim(0, 46)
    ax2.set_title("已披露毛利率（实绩）", fontsize=11.5, color=NAVY, pad=10)
    ax2.set_ylabel("毛利率（%）", fontsize=10, color=GREY)
    ax1.tick_params(labelsize=10.5)
    ax2.tick_params(labelsize=9.0)

    note = ("单位：亿元人民币 / %。口径：曙光数创为公司年报披露的产品线收入与毛利率；Modine 为数据中心分部毛利率，含设施侧冷却，不是纯液冷。两家口径不同，不可直接比较，只说明「增长不保证高毛利」。\n"
            "数据性质：全部为已披露实绩。禁止：以此推导任何其他公司的 CDU 毛利率；报告已删除通用毛利率点值，不得恢复。\n"
            "来源：曙光数创 2025 年报「收入构成」；Modine 2026 年 6 月季度财报。报告第 5 章。")
    _finish(fig, [ax1, ax2], note, "c13_margin_evidence.png", left=0.07, bottom=0.30,
            top=0.88, wspace=0.26)


# ============================================================
# c14 超大规模厂商 CapEx（表 2.6.7）
# ============================================================
def c14():
    fig, ax = plt.subplots(figsize=(10.4, 4.3))
    ax.bar([0, 1], [224, 413], color=NAVY, width=0.4, zorder=3, label="实绩（四家合计）")
    ax.bar([2], [737.5], color=AMBER, width=0.4, zorder=3, label="公司指引（730–745）")
    ax.errorbar([2], [737.5], yerr=[[7.5], [7.5]], fmt="none", ecolor=RED,
                elinewidth=2, capsize=9, zorder=5)
    for i, (v, t) in enumerate(zip([224, 413, 737.5], ["约 224", "约 413", "约 730–745"])):
        ax.text(i, v + 22, t, ha="center", fontsize=13, fontweight="bold",
                color=NAVY if i < 2 else AMBER)
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(["2024（实绩）", "2025（实绩）", "2026（公司指引）"], fontsize=10.5)
    ax.set_ylabel("十亿美元", fontsize=10.5, color=GREY)
    ax.set_ylim(0, 1080)
    ax.set_xlim(-0.6, 2.6)
    ax.legend(loc="upper left", frameon=False, fontsize=9.6)
    ax.text(0.98, 0.97,
            "仅四家公司 2026 指引即占路径 A-基准隐含全球总投资（8,460 亿）的 86%–88%\n→ 数学上不可持续，基准情景已被实际投资超越",
            transform=ax.transAxes, ha="right", va="top", fontsize=9.6, color=RED,
            bbox=dict(boxstyle="round,pad=0.5", fc="#fff7f6", ec="#f6c8c5"))

    note = ("单位：十亿美元。口径：Alphabet / Amazon / Microsoft / Meta 公司级 CapEx 合计，含办公、网络骨干、自研芯片预付等非数据中心支出，与全球 L3 口径不同。\n"
            "数据性质：2024/2025 为实绩，2026 为公司指引（机构预测性质）。四家使用三种不同 CapEx 定义（含/不含融资租赁本金、现金 vs 应计）；Microsoft 2026 数字受租赁年限会计变更（15 年改 25 年）影响。\n"
            "禁止：除以 L3 得「份额」；相加进 L3。四家之外还有 Oracle、xAI、CoreWeave、字节、阿里、腾讯与主权 AI 项目。来源：四家 2026 年 7 月下旬财报与业绩会（经二级媒体汇总）。报告表 2.6.7、台账 K08。")
    _finish(fig, ax, note, "c14_hyperscaler_capex.png", bottom=0.28)


# ============================================================
# c15 液冷渗透率（2.7.5 驱动因素，TrendForce）
# ============================================================
def c15():
    fig, ax = plt.subplots(figsize=(10.4, 4.3))
    ax.bar([0, 1], [14, 33], color=BLUE, width=0.42, zorder=3,
           label="口径 A：AI 数据中心（TrendForce）")
    ax.bar([2.4, 3.4], [53, 58], color=TEAL, width=0.42, zorder=3,
           label="口径 B：AI 芯片（TrendForce，分母不同）")
    for x, v, t in [(0, 14, "14%"), (1, 33, "33%"), (2.4, 53, "53%"), (3.4, 58, "接近 60%")]:
        ax.text(x, v + 1.6, t, ha="center", fontsize=13, fontweight="bold",
                color=BLUE if x < 2 else TEAL)
    ax.set_xticks([0, 1, 2.4, 3.4])
    ax.set_xticklabels(["2024", "2025", "2026", "2027"], fontsize=11)
    ax.set_ylabel("液冷渗透率（%）", fontsize=10.5, color=GREY)
    ax.set_ylim(0, 76)
    ax.legend(loc="upper left", frameon=False, fontsize=9.8)
    ax.axvline(1.7, color="#c9d1dc", lw=1.4, ls="--")
    ax.text(1.7, 70, "分母切换", ha="center", fontsize=9.6, color=RED,
            bbox=dict(boxstyle="round,pad=0.35", fc="#fff7f6", ec="#f6c8c5"))

    note = ("单位：%。口径：两组数字来自 TrendForce 的两个不同分母（AI 数据中心 vs AI 芯片），不可连成一条曲线，也不可计算年度增幅。\n"
            "数据性质：机构估计 / 机构预测。报告明确：两个版本分母不同，只证明渗透方向向上，不证明具体渗透率水平。\n"
            "来源：TrendForce，转引自报告表 2.7.5「比例随时间变化的驱动因素」。")
    _finish(fig, ax, note, "c15_penetration.png", bottom=0.28)


# ============================================================
# 概念示意图（自绘，无外部素材）
# ============================================================
def _box(ax, x, y, w, h, text, fc, ec, fs=10, tc="#ffffff", bold=True, r=0.02):
    box = mpatches.FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}",
                                  fc=fc, ec=ec, lw=1.4, zorder=3)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=4, linespacing=1.45)


def _arrow(ax, x1, y1, x2, y2, c=NAVY, lw=2.0, style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=c, lw=lw, mutation_scale=18),
                zorder=5)


def _canvas(w=11.2, h=5.4):
    fig, ax = plt.subplots(figsize=(w, h))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis("off")
    fig.patch.set_facecolor(BG)
    return fig, ax


# c16 OEM 微笑曲线
def c16():
    fig, ax = _canvas(11.2, 5.2)
    xs = np.linspace(6, 94, 300)
    ys = 34 + 0.0165 * (xs - 50) ** 2
    ax.plot(xs, ys, color=NAVY, lw=3.4, zorder=3)
    ax.fill_between(xs, ys, 20, color="#f4f7ff", zorder=1)

    ax.axvspan(4, 32, ymin=0.16, ymax=0.92, color="#eaf1fd", alpha=0.55, zorder=0)
    ax.axvspan(32, 68, ymin=0.16, ymax=0.92, color="#f2f4f7", alpha=0.8, zorder=0)
    ax.axvspan(68, 96, ymin=0.16, ymax=0.92, color="#f2fbf7", alpha=0.7, zorder=0)

    front = ["需求定义", "系统架构", "热工水力", "控制策略"]
    mid = ["器件采购", "基础软件", "加工装配", "整机制造"]
    back = ["系统集成", "FAT / SAT", "qualification", "质量签署", "诊断数据", "品牌客户"]

    for i, t in enumerate(front):
        ax.text(9 + i * 6.2, 30 - i * 3.0, t, fontsize=10, color=BLUE, ha="center",
                fontweight="bold", rotation=0)
    for i, t in enumerate(mid):
        ax.text(38 + i * 8.2, 25, t, fontsize=10, color=GREY, ha="center")
    for i, t in enumerate(back):
        ax.text(69 + (i % 3) * 10.5, 32 - (i // 3) * 5.0, t, fontsize=9.6, color=TEAL,
                ha="center", fontweight="bold")

    _box(ax, 6, 82, 26, 12, "前端 · 自留\n需求 / 架构 / 热工水力 / IP", BLUE, BLUE, fs=10.5)
    _box(ax, 37, 82, 26, 12, "中段 · 外协\n器件 / 基础软件 / 制造", "#ffffff", GREY, fs=10.5, tc=GREY)
    _box(ax, 68, 82, 26, 12, "后端 · 自留\nqualification / 服务 / 客户责任", TEAL, TEAL, fs=10.5)

    ax.annotate("", xy=(3, 96), xytext=(3, 18), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.6))
    ax.text(1.2, 57, "附加值", rotation=90, va="center", fontsize=10.5, color=GREY)
    ax.annotate("", xy=(97, 16), xytext=(3, 16), arrowprops=dict(arrowstyle="-|>", color=GREY, lw=1.6))
    ax.text(50, 12.5, "价值链环节", ha="center", va="top", fontsize=10.5, color=GREY)

    ax.text(50, 7.5,
            "轻资产的真实代价：固定 CapEx 下降，但供应商毛利、NRE、MOQ、关键件预付款、质量工程、供应商审核、库存缓冲、\n"
            "软件许可、托管、保险与合同管理成本上升。微笑曲线不是「少做事」，而是把资源从加工转向规格、验证、责任与数据。",
            ha="center", va="top", fontsize=9.2, color=RED, linespacing=1.7)
    ax.text(50, 76, "七项价值控制点：需求权 · 架构权 · 版本权 · 变更权 · 放行权 · 数据权 · 客户权",
            ha="center", fontsize=10.2, color=NAVY, fontweight="bold")
    _plain(fig, "c16_smile_curve.png")


# c17 CDU 系统框图
def c17():
    fig, ax = _canvas(11.2, 5.4)
    ax.text(50, 96, "一次侧（FWS）　→　CDU（换热与隔离）　→　二次侧（TCS）　＋　控制层",
            ha="center", fontsize=12, color=NAVY, fontweight="bold")

    # 一次侧
    _box(ax, 2, 46, 20, 30, "", "#f2f4f7", "#c9d1dc", tc=GREY)
    ax.text(12, 72, "一次侧 FWS", ha="center", fontsize=11, color=GREY, fontweight="bold")
    for i, t in enumerate(["设施冷源 / 冷水机", "冷却塔 / 干冷器", "一次侧泵与阀组", "供回水温度控制"]):
        ax.text(12, 66 - i * 5, "· " + t, ha="center", fontsize=9.3, color=GREY)

    # CDU
    _box(ax, 27, 40, 30, 42, "", "#eaf1fd", BLUE, tc=NAVY)
    ax.text(42, 78, "CDU 本体", ha="center", fontsize=12, color=BLUE, fontweight="bold")
    for i, t in enumerate(["板式换热器（一/二次侧物理隔离）", "循环泵组 N / N+1",
                           "过滤 · 脱气 · 补液定压", "温度 / 压力 / 流量 / 电导率传感",
                           "泄漏检测与联锁", "钣金 / 管路 / 电控柜"]):
        ax.text(42, 72 - i * 5.2, "· " + t, ha="center", fontsize=9.3, color=NAVY)

    # 二次侧
    _box(ax, 62, 46, 22, 30, "", "#f2fbf7", TEAL, tc=TEAL)
    ax.text(73, 72, "二次侧 TCS", ha="center", fontsize=11, color=TEAL, fontweight="bold")
    for i, t in enumerate(["Manifold 歧管", "UQD 快接 / 软管", "芯片级 / 微通道冷板", "高密 AI 机柜"]):
        ax.text(73, 66 - i * 5, "· " + t, ha="center", fontsize=9.3, color=TEAL)

    _arrow(ax, 22.5, 61, 26.5, 61, c=GREY)
    _arrow(ax, 57.5, 61, 61.5, 61, c=TEAL)
    ax.text(24.5, 65, "FWS", ha="center", fontsize=8.6, color=GREY)
    ax.text(59.5, 65, "TCS", ha="center", fontsize=8.6, color=TEAL)

    # 控制层
    _box(ax, 2, 22, 82, 13, "", "#f4f7ff", NAVY, tc=NAVY)
    ax.text(6, 31.5, "控制层", fontsize=11, color=NAVY, fontweight="bold", ha="left")
    for i, t in enumerate(["应用控制算法 / 状态机", "故障降级与冗余切换", "告警联锁 / 参数标定",
                           "BMS · DCIM 接口", "远程诊断 / 数字孪生"]):
        ax.text(19 + i * 14, 26.5, t, ha="center", fontsize=9.2, color=NAVY)
    _arrow(ax, 42, 35.5, 42, 39.5, c=NAVY, style="<|-|>")

    _box(ax, 86, 40, 12, 42, "", NAVY, NAVY)
    ax.text(92, 76, "有效冷量\n≠ 铭牌冷量", ha="center", va="center", fontsize=10.5,
            color="#ffffff", fontweight="bold", linespacing=1.6, zorder=4)
    ax.text(92, 57,
            "C_effective =\nC_curve(ATD, TCS,\nFWS, fluid,\npump_state)\n× D_altitude\n× D_fouling",
            ha="center", va="center", fontsize=8.0, color="#e8eef8", linespacing=1.85,
            zorder=4)

    ax.text(50, 14,
            "选型必须同时校核：IT 功率 · HCR/液体热负荷 · TCS/FWS 温度与工质 · Q–ΔP 曲线 · 最大压力 · 冗余失效域 · 过滤污堵 · 控制接口 · 项目级 qualification",
            ha="center", fontsize=9.4, color=NAVY)
    ax.text(50, 8.5,
            "一次侧与二次侧回路不得拼接（例：华为液冷门回路与计算柜 D2C 回路）；支路流量可加，支路压降不可相加。",
            ha="center", fontsize=9.2, color=RED)
    ax.text(50, 3.5,
            "自绘示意图 · 依据报告第 3 章（表 3.1、3.2）与 12.2 模型公式；不含任何厂商实物图片。",
            ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c17_cdu_schematic.png")


# c18 商业三步走路线图
def c18():
    fig, ax = _canvas(11.6, 5.9)
    stages = [
        (2, BLUE, "阶段 1 · 产品—客户验证", "2027 启动　|　上限 800 万元",
         ["容量：优先 50–200 kW；四 SKU 经济",
          "　　　模板 100 / 200 / 300 / 450 kW",
          "验证：性能矩阵、付费 PoC、",
          "　　　FAT/SAT、合同边界",
          "门禁：客户书面平台包 · ≥2 项付费验证",
          "　　　完整项目损益 · 回款节点可执行",
          "　　　无重大可靠性缺陷"],
         ["No-Go", "无限停机 / 数据责任 · 无有效工况",
          "无付费牵引 · 现金压力情景失守"]),
        (34, TEAL, "阶段 2 · 资格—复制验证", "条件期权　|　最高 1,200 万元",
         ["容量：200–500 kW / Pod，冗余并联、",
          "　　　控制平台与远程诊断",
          "验证：项目级 qualification、批量一致性、",
          "　　　本地服务、供应链双源",
          "门禁：不可撤销订单 · 正的完全成本贡献",
          "　　　验收回款闭环 · 可靠性批次通过",
          "　　　压力情景现金跑道达标"],
         ["No-Go", "框架无订单 · 贡献持续为负",
          "DSO/库存突破阈值 · 重大质保事件"]),
        (66, NAVY, "阶段 3 · 平台—产能验证", "条件期权　|　最高 1,500 万元",
         ["产品：客户牵引的芯片级/微通道冷板托盘、",
          "　　　Manifold 与液冷模组",
          "验证：OEM/ODM 联合开发、海外服务与",
          "　　　专用产能",
          "门禁：客户订单覆盖新增固定成本",
          "　　　量产良率稳定 · 责任可保可封顶",
          "　　　本地服务 SLA 通过 · 现金跑道充分"],
         ["No-Go", "无客户 NRE / 订单即建专线 · 代际变化",
          "致专用 BOM 失效 · 单一客户风险过高"]),
    ]
    for x, c, title, cap, bullets, nogo in stages:
        _box(ax, x, 56, 30, 41, "", "#ffffff", c, tc=c)
        _box(ax, x, 89, 30, 8, title, c, c, fs=10.5)
        ax.text(x + 15, 85.5, cap, ha="center", fontsize=9.8, color=c, fontweight="bold")
        for i, b in enumerate(bullets):
            ax.text(x + 1.5, 81 - i * 3.4, b, ha="left", va="top", fontsize=8.3,
                    color=NAVY)
        _box(ax, x, 41, 30, 12, "", "#fff7f6", "#f6c8c5", tc=RED)
        ax.text(x + 15, 49.5, nogo[0], ha="center", fontsize=9.6, color=RED,
                fontweight="bold")
        ax.text(x + 15, 46.2, nogo[1], ha="center", fontsize=8.0, color=RED)
        ax.text(x + 15, 43.2, nogo[2], ha="center", fontsize=8.0, color=RED)

    for x in (32.2, 64.2):
        _arrow(ax, x, 76, x + 1.6, 76, c=GREY, lw=2.6)

    _box(ax, 2, 18, 94, 17, "", "#f4f7ff", "#c9d8ff", tc=NAVY)
    ax.text(49, 31, "三道解锁门　—　同时达标才释放，缺一冻结", ha="center", fontsize=11,
            color=NAVY, fontweight="bold")
    gates = [("订单门", "PO、最低采购或等效信用保障；", "框架份额不等于收入"),
             ("贡献门", "硬件毛利、项目贡献、现金调整后", "贡献三层均可追踪"),
             ("现金门", "按周测峰值资金；纳入 PBG、", "验收延期、质保与返修")]
    for i, (g, d1, d2) in enumerate(gates):
        cx = 18 + i * 31
        ax.text(cx, 26.5, g, ha="center", fontsize=10.2, color=BLUE, fontweight="bold")
        ax.text(cx, 23.0, d1, ha="center", fontsize=8.4, color=NAVY)
        ax.text(cx, 20.0, d2, ha="center", fontsize=8.4, color=NAVY)

    ax.text(49, 12.5,
            "阶段 2、3 不是承诺额度。外部投资增速与液冷占比上升均不构成解锁条件；只有订单、贡献、回款、",
            ha="center", fontsize=9.4, color=RED)
    ax.text(49, 8.5,
            "可靠性与现金跑道同时达标才可解锁。CapEx 不得领先已签订单和 qualification 进度。",
            ha="center", fontsize=9.4, color=RED)
    ax.text(49, 2.5, "自绘示意图 · 依据报告「两页核心观点②」与第 9 章；配套《算力冷却系统新业务BP》v2.1 第 2、10、12 章。",
            ha="center", fontsize=8.0, color=GREY)
    _plain(fig, "c18_roadmap.png")


# c19 TAM/SAM/SOM 漏斗
def c19():
    fig, ax = _canvas(11.6, 5.6)
    layers = [
        (2, 76, 70, 18, BLUE, "TAM　全球液冷设备制造商收入",
         ["2025　25–35 亿美元（Base 30，Dell'Oro 机构估计）",
          "2029　60–80 亿美元（Base 70，Dell'Oro 机构预测）　|　2032　90–140 亿美元（本报告情景）"]),
        (10, 55, 54, 18, TEAL, "SAM 24m　24 个月内可服务项目池",
         ["SAM_24m = Σ(Eligible_i × 经验证项目收入_i × 24 个月内投运开关_i)"]),
        (20, 34, 34, 18, NAVY, "SOM　公司可获收入",
         ["经 qualification、订单、交付、", "服务与回款约束后的可获收入"]),
    ]
    for x, y, w, h, c, title, subs in layers:
        verts = [(x, y + h), (x + w, y + h), (x + w - 6, y), (x + 6, y), (x, y + h)]
        poly = mpatches.Polygon(verts, closed=True, fc=c, ec=c, alpha=0.94, zorder=3)
        ax.add_patch(poly)
        ax.text(x + w / 2, y + h - 5.5, title, ha="center", fontsize=12,
                color="#ffffff", fontweight="bold", zorder=4)
        for i, s in enumerate(subs):
            ax.text(x + w / 2, y + h - 11 - i * 4.2, s, ha="center", fontsize=8.2,
                    color="#e2eaf6", zorder=4)

    _box(ax, 75, 34, 23, 60, "", "#fff7f6", "#f6c8c5", tc=RED)
    ax.text(86.5, 89, "当前裁决", ha="center", fontsize=11, color=RED, fontweight="bold")
    ax.text(86.5, 80, "SAM 24m = 无数据", ha="center", fontsize=12.5, color=RED,
            fontweight="bold")
    ax.text(86.5, 73, "SOM = 无数据", ha="center", fontsize=12.5, color=RED,
            fontweight="bold")
    for i, t in enumerate(["不是 0，是公开证据不足。", "公开可核验 Eligible 项目数",
                           "暂未闭环。四个公开候选项目", "（Stargate UAE 首簇 · Khazna 扩张",
                           "· 沙特 HUMAIN · PIF–Google", "Dammam AI Hub）逐项检验后",
                           "Eligible 均为「否」。"]):
        ax.text(86.5, 64 - i * 3.6, t, ha="center", fontsize=8.2, color=RED)

    # 五道项目门
    _box(ax, 2, 15, 71, 16, "", "#f4f7ff", "#c9d8ff", tc=NAVY)
    ax.text(37.5, 27, "Eligible_i = Power_i × Finance_i × Build_i × Platform_i × ServiceGeo_i",
            ha="center", fontsize=10, color=NAVY, fontweight="bold")
    ax.text(37.5, 23.5, "五道项目门，乘积逻辑：任一为 0 则整体为 0", ha="center",
            fontsize=8.6, color=GREY)
    for i, (g, d) in enumerate([("已获电", "接电协议"), ("已融资", "项目级融资"),
                                ("已开工", "NTP / 施工"), ("平台已冻结", "柜级 BOM"),
                                ("地理可服务", "本地服务能力")]):
        cx = 9 + i * 14
        ax.text(cx, 20, g, ha="center", fontsize=9.4, color=BLUE, fontweight="bold")
        ax.text(cx, 16.8, d, ha="center", fontsize=8.0, color=GREY)

    ax.text(50, 9.5,
            "禁止：公司收入 = TAM × 目标份额　|　公司收入 =（需求 GW − 供给 GW）× 单位设备价值　|　SAM = 公告 MW × 液冷渗透率 × 设备价值/MW",
            ha="center", fontsize=9.2, color=RED, fontweight="bold")
    ax.text(50, 5, "2.6 / 2.7 章的 L1 / L2 / L3 与三组占比不是 TAM、SAM 或 SOM 的任何一层，只是外部市场锚定。",
            ha="center", fontsize=9.0, color=NAVY)
    ax.text(50, 0.8, "自绘示意图 · 依据报告第 7 章与 12.2 模型公式。", ha="center",
            fontsize=8.0, color=GREY)
    _plain(fig, "c19_tam_sam_som.png")


# c20 证据分级金字塔 + 数据性质
def c20():
    fig, ax = _canvas(11.2, 5.0)
    tiers = [
        (34, 78, 32, 15, NAVY, "一级", "政府 / 监管 / 正式标准 / 交易所或 SEC 文件 / 采购人原件 / 原厂正式手册"),
        (24, 61, 52, 15, BLUE, "二级", "公司正式公告 / 原厂发布稿 / OCP 开放规范 / 研究机构官方摘要"),
        (14, 44, 72, 15, TEAL, "三级", "镜像 / 转录 / 二手研究 —— 仅作线索，不做关键价格与责任依据"),
        (4, 27, 92, 15, GREY, "本报告模型", "内部透明推导 —— 须给公式、输入与失效条件；不得伪装成机构逐年预测"),
    ]
    for x, y, w, h, c, name, desc in tiers:
        _box(ax, x, y, w, h, "", c, c, r=0.015)
        ax.text(x + w / 2, y + h * 0.66, name, ha="center", fontsize=13,
                color="#ffffff", fontweight="bold", zorder=4)
        ax.text(x + w / 2, y + h * 0.26, desc, ha="center", fontsize=8.6,
                color="#ffffff", zorder=4)
    ax.text(50, 96, "来源等级（中文四级）　·　自上而下证据力递减，覆盖面递增",
            ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(50, 20,
            "无数据：公开证据不足、未披露或口径不匹配　—— 不得改成 0，不得用二手区间填空",
            ha="center", fontsize=11, color=RED, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.6", fc="#fff7f6", ec="#f6c8c5"))
    ax.text(50, 11,
            "数据性质标签（与来源等级是两套独立体系）：实绩 · 机构估计 · 机构预测 · 模型 · 无数据",
            ha="center", fontsize=9.8, color=NAVY)
    ax.text(50, 5.5,
            "投资层级 L1 / L2 / L3 自 v3.2 起专指第 2.6、2.7 章的算力基建投资分层，不再表示来源等级。",
            ha="center", fontsize=9.0, color=AMBER)
    _plain(fig, "c20_evidence_pyramid.png")


# c21 项目级 qualification 链
def c21():
    fig, ax = _canvas(11.2, 4.4)
    steps = ["平台 / BOM\n冻结", "TCS/FWS 与\nQ–ΔP 对齐", "材料 · 压力\n泄漏 · 遥测\n冗余验证",
             "DVT / PVT\n或付费 PoC", "FAT", "安装联调", "SAT / ISAT", "最终验收", "项目 BOM\n/ 订单"]
    n = len(steps)
    w = 9.4
    gap = 1.2
    x0 = 2.0
    for i, s in enumerate(steps):
        x = x0 + i * (w + gap)
        c = BLUE if i < 4 else (TEAL if i < 7 else NAVY)
        _box(ax, x, 52, w, 24, s, c, c, fs=8.6)
        if i < n - 1:
            _arrow(ax, x + w + 0.05, 64, x + w + gap - 0.05, 64, c=GREY, lw=1.8)
    ax.text(50, 96,
            "截至 2026-08-22：公开证据不足以验证 NVIDIA MGX/NPN 统一 CDU 认证或公开 AVL；NPN 是伙伴计划，\n"
            "NVIDIA-Certified Systems 面向整机；华为有公司级供应商体系认证与项目物料选型，但未公开 Atlas CDU 完整名录或统一认证包。",
            ha="center", va="top", fontsize=9.3, color=RED, linespacing=1.7)
    _box(ax, 2, 24, 46, 20, "", "#f4f7ff", "#c9d8ff", tc=NAVY)
    ax.text(25, 40, "现行标准（均非现行强制产品认证）", ha="center", fontsize=10.2,
            color=NAVY, fontweight="bold")
    for i, t in enumerate(["YD/T 6049-2024 冷板式液冷整机柜服务器 · 已实施",
                           "YD/T 6358-2025 冷板式液冷数据中心 · 已实施",
                           "GB/T 48023-2026 · 已发布，2027-02-01 实施",
                           "OCP coolant base spec v1.3 · 2026-08-06 生效"]):
        ax.text(4.5, 35.5 - i * 3.4, "· " + t, ha="left", fontsize=8.6, color=NAVY)
    _box(ax, 52, 24, 46, 20, "", "#fff7f6", "#f6c8c5", tc=RED)
    ax.text(75, 40, "四项关键纠错", ha="center", fontsize=10.2, color=RED, fontweight="bold")
    for i, t in enumerate(["ASHRAE W17–W45 是供液温度能力等级，不是 PUE 等级",
                           "水质不采用跨厂商单一电导率阈值，按 OEM coolant 控制",
                           "负压可降低外泄概率，但不表述为「零泄漏」",
                           "MTBF 须声明统计模型与置信水平，当前仅为内部目标"]):
        ax.text(54.5, 35.5 - i * 3.4, "· " + t, ha="left", fontsize=8.6, color=RED)
    ax.text(50, 17.5, "2025-1993T-YD（CDU 冷板式草案）为计划/征求意见稿，草案参数不可当现行要求；valid_until 2026-11-30。",
            ha="center", fontsize=8.8, color=AMBER)
    ax.text(50, 10, "自绘示意图 · 依据报告第 4 章（表 4.1、4.2、4.3）。", ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c21_qualification_chain.png")


# c22 G0–G3 资金门禁
def c22():
    fig, ax = _canvas(11.2, 5.0)
    gates = [
        (BLUE, "G0", "立项 / 首笔", "800 万元上限内逐月预算 + 13 周现金；核心 FTE ≤ 8"),
        (TEAL, "G1", "阶段 2 前", "≥2 付费验证 · 两个同边界合同价 · 项目贡献为正 · 四 SKU BOM · 三批试制"),
        ("#175cd3", "G2", "阶段 3 前", "不可撤销订单 · ≥1 个 OEM/ODM 书面项目认可 · 现金调整后贡献持续为正"),
        (NAVY, "G3", "专用产能 / 规模", "冷板托盘 DVT/PVT 与良率稳定 · 订单覆盖新增固定成本 · Bear 情景仍满足现金安全线"),
    ]
    for i, (c, g, title, desc) in enumerate(gates):
        y = 76 - i * 17
        _box(ax, 4, y, 11, 13, g, c, c, fs=17)
        _box(ax, 16, y, 22, 13, title, "#ffffff", c, fs=11.5, tc=c)
        _box(ax, 39, y, 57, 13, "", "#f8fafc", "#dbe2ea", tc=NAVY)
        ax.text(67.5, y + 6.5, desc, ha="center", va="center", fontsize=9.3, color=NAVY,
                linespacing=1.5)
        if i < 3:
            _arrow(ax, 9.5, y - 0.3, 9.5, y - 3.7, c=GREY, lw=2.0)
    ax.text(50, 95, "资金门禁 G0–G3：任一硬门未达，自动冻结下一期资金、新增编制、专用库存与非关键 CapEx",
            ha="center", fontsize=12, color=NAVY, fontweight="bold")
    ax.text(50, 4.5,
            "董事会不得以「融资到账、框架入围、展示样机、行业景气或外部 TAM 上修」替代门禁证据。管理层只能申请整改预算。",
            ha="center", fontsize=9.8, color=RED, fontweight="bold")
    ax.text(50, 0.5, "自绘示意图 · 依据报告第 9 章与《算力冷却系统新业务BP》v2.1 第 12 章。",
            ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c22_gates.png")


# c23 液冷技术路线三层
def c23():
    fig, ax = _canvas(11.2, 4.6)
    rows = [
        (BLUE, "当前产品化", "单相 D2C · 芯片级/微通道冷板 · CDU · Manifold · UQD",
         "具体新结构仍需 DVT / PVT"),
        (TEAL, "验证路线", "喷射冲击 · 两相冷板 · 负压回路",
         "只描述机理和测试门，不给通用性能点值"),
        (GREY, "研究路线", "封装内嵌 / 硅内嵌微流道 · 金刚石扩热",
         "公开证据不足以支持量产时点、\n良率、寿命或专利壁垒点值"),
    ]
    for i, (c, name, content, caveat) in enumerate(rows):
        y = 78 - i * 21
        _box(ax, 3, y, 18, 17, name, c, c, fs=13)
        _box(ax, 22, y, 42, 17, content, "#ffffff", c, fs=9.4, tc=NAVY)
        _box(ax, 65, y, 32, 17, caveat, "#f8fafc", "#dbe2ea", fs=8.2, tc=RED, bold=False)
    ax.text(50, 22,
            "命名纪律：「PCB 冷板」仅在流道真正集成于印制电路板时使用；本报告其余统一称「芯片级 / 微通道冷板」。\n"
            "相邻路线（浸没、两相、设施侧冷源）只作比较，不进入本报告主边界。",
            ha="center", va="top", fontsize=9.6, color=AMBER, linespacing=1.7)
    ax.text(50, 5, "自绘示意图 · 依据报告第 3.3 节。", ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c23_tech_routes.png")


# c24 竞争格局与并购整合
def c24():
    fig, ax = _canvas(11.2, 5.1)
    deals = [
        (BLUE, "Ecolab / CoolIT", "2026-07-02 交割", "未来 12 个月约 5.5 亿美元\n（机构预测，非实际）",
         "水处理 + 工质 + DLC + 全球服务"),
        (TEAL, "Eaton / Boyd Thermal", "2026-03-12 交割", "2026 液冷 15 亿美元\n（机构预测，非实际）",
         "grid-to-chip 与 chip-to-ambient"),
        (NAVY, "Schneider / Motivair", "2025-02-28 取得 75%", "未拆分液冷收入\n（无数据）",
         "电力 + 预制模块 + CDU + 冷水机"),
    ]
    for i, (c, name, date, rev, strat) in enumerate(deals):
        x = 3 + i * 31.7
        _box(ax, x, 63, 29, 34, "", "#ffffff", c, tc=c)
        _box(ax, x, 89, 29, 8, name, c, c, fs=11.5)
        ax.text(x + 14.5, 84.5, date, ha="center", fontsize=9.6, color=c, fontweight="bold")
        ax.text(x + 14.5, 77, rev, ha="center", va="center", fontsize=9.2, color=NAVY,
                linespacing=1.6)
        ax.text(x + 14.5, 68, strat, ha="center", va="center", fontsize=9.0, color=GREY,
                linespacing=1.5)
    _box(ax, 3, 37, 45, 21, "", "#f4f7ff", "#c9d8ff", tc=NAVY)
    ax.text(25.5, 53.5, "可比原则：四层严格分列", ha="center", fontsize=10.5, color=NAVY,
            fontweight="bold")
    for i, t in enumerate(["纯液冷收入 / 数据中心冷却 / 数据中心基础设施 / 集团收入",
                           "实绩 / 预测 / backlog / capacity agreement 分列",
                           "不以集团收入或集团毛利冒充液冷收入或毛利"]):
        ax.text(25.5, 48.5 - i * 3.8, "· " + t, ha="center", fontsize=8.8, color=NAVY)
    _box(ax, 52, 37, 45, 21, "", "#fff7f6", "#f6c8c5", tc=RED)
    ax.text(74.5, 53.5, "已删除且不予恢复的点值", ha="center", fontsize=10.5, color=RED,
            fontweight="bold")
    for i, t in enumerate(["市场份额 · 前五集中度 · 部件价值占比",
                           "客户独家 · 通用毛利率 · 专利墙",
                           "2.7 章的液冷占比不是市场份额，不得用来间接恢复"]):
        ax.text(74.5, 48.5 - i * 3.8, "· " + t, ha="center", fontsize=8.8, color=RED)
    ax.text(50, 29,
            "Vertiv 仅有集团收入/backlog，未披露液冷毛利；英维克 / 申菱 / 高澜 均为集团或混合板块披露，不得反推液冷收入、份额或毛利。",
            ha="center", fontsize=9.3, color=GREY)
    ax.text(50, 20,
            "结论：竞争已全栈化，增长不保证高毛利。壁垒转向全球服务、流体管理与责任承担；扩产爬坡和标准化可压缩利润。",
            ha="center", fontsize=10.5, color=NAVY, fontweight="bold")
    ax.text(50, 12, "confidence 0.90 / valid_until 2026-11-15　·　invalidate_if：并购方披露独立液冷收入或利润显著优于当前可比证据",
            ha="center", fontsize=9.0, color=AMBER)
    ax.text(50, 4, "自绘示意图 · 依据报告第 5 章与证据台账 C01、C02。", ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c24_competition.png")


# c25 液冷占比驱动因素
def c25():
    fig, ax = _canvas(11.2, 4.8)
    up = [("液冷渗透率上升", "TrendForce：AI 数据中心 14%(2024)→33%(2025)"),
          ("单柜功率提高", "GB300 峰值 155 kW；Dell IR7000 最高 264 kW"),
          ("存量改造", "高密推理扩散至 colocation 与区域节点"),
          ("全液冷平台扩散", "NVIDIA Rubin 路线称 100% 液冷")]
    down = [("ASP 下降", "标准化、国产化与规模采购；Bear 假设年降 8%–12%"),
            ("OEM/ODM 垂直整合", "Lenovo、Dell、Supermicro、华为均自供 CDU/冷板"),
            ("设施侧 EPC 吃掉价值", "设施侧液冷投入 vs 设备制造商收入 约差 5–6 倍"),
            ("分母扩围", "Dell'Oro 2026-08 扩大 DCPI 边界；IDC 上调 IT 支出")]
    _box(ax, 3, 89, 45, 8, "↑ 推高占比", TEAL, TEAL, fs=12)
    _box(ax, 52, 89, 45, 8, "↓ 压低占比", RED, RED, fs=12)
    for i, (t, d) in enumerate(up):
        y = 77 - i * 13
        _box(ax, 3, y, 45, 11, "", "#f2fbf7", "#b6e4d2", tc=TEAL)
        ax.text(5.5, y + 7.0, t, ha="left", fontsize=10.2, color=TEAL, fontweight="bold")
        ax.text(5.5, y + 2.8, d, ha="left", fontsize=8.5, color=NAVY)
    for i, (t, d) in enumerate(down):
        y = 77 - i * 13
        _box(ax, 52, y, 45, 11, "", "#fff7f6", "#f6c8c5", tc=RED)
        ax.text(54.5, y + 7.0, t, ha="left", fontsize=10.2, color=RED, fontweight="bold")
        ax.text(54.5, y + 2.8, d, ha="left", fontsize=8.5, color=NAVY)
    _box(ax, 3, 13, 94, 10, "", "#fff7e8", "#f0d9a8", tc=AMBER)
    ax.text(50, 18, "方向不确定：2030 后分母减速 —— Dell'Oro 称净新增容量增速 2026 见顶；IDC 2030 后无公开端点。若 IT 支出进入消化期，占比会被动上升。",
            ha="center", va="center", fontsize=9.6, color=AMBER)
    ax.text(50, 6, "自绘示意图 · 依据报告表 2.7.5。", ha="center", fontsize=8.2, color=GREY)
    _plain(fig, "c25_share_drivers.png")


# c26 CDU 容量档「无数据」矩阵
def c26():
    fig, ax = plt.subplots(figsize=(10.6, 4.3))
    rows = ["100 kW", "200 kW", "300 kW", "450 kW"]
    cols = ["ATD 3/4/5/8℃", "水 / PG25 / 其他工质", "泵 N / N+1 故障态", "clean / dirty filter"]
    data = np.ones((4, 4))
    ax.imshow(data, cmap=matplotlib.colors.ListedColormap(["#fff7f6"]), aspect="auto")
    for i in range(4):
        for j in range(4):
            ax.text(j, i, "无数据", ha="center", va="center", fontsize=13,
                    color=RED, fontweight="bold")
    ax.set_xticks(range(4))
    ax.set_xticklabels(cols, fontsize=10.5)
    ax.set_yticks(range(4))
    ax.set_yticklabels(rows, fontsize=12, fontweight="bold")
    ax.set_xticks(np.arange(-0.5, 4, 1), minor=True)
    ax.set_yticks(np.arange(-0.5, 4, 1), minor=True)
    ax.grid(which="minor", color="#f6c8c5", lw=1.6)
    ax.grid(which="major", visible=False)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(colors=NAVY)
    for s in ax.spines.values():
        s.set_color("#f6c8c5")
    ax.set_title("CDU 有效能力矩阵：四个容量档 × 四类工况，当前全部为「无数据」",
                 fontsize=12.5, color=NAVY, pad=14, fontweight="bold")

    note = ("状态：待样机热性能与 PQ 矩阵。有效冷量公式：C_effective = C_curve(ATD, TCS, FWS, fluid, pump_state) × D_altitude × D_fouling。\n"
            "口径纪律：容量档不是平台兼容承诺。铭牌冷量不能证明平台兼容；水力、材料、冗余和故障态共同决定可用性。四 SKU 之间不得用容量线性插值生成 ASP、BOM 或毛利。\n"
            "来源：报告表 3.2、12.2 模型公式；《算力冷却系统新业务BP》v2.1 表 7.2。「无数据」不得改写为 0，也不得用二手区间填空。")
    _finish(fig, ax, note, "c26_cdu_matrix_na.png", left=0.10, bottom=0.32, top=0.86,
            spines=False)


if __name__ == "__main__":
    for fn in [c01, c02, c03, c04, c05, c06, c07, c08, c09, c10, c11, c12, c13,
               c14, c15, c16, c17, c18, c19, c20, c21, c22, c23, c24, c25, c26]:
        fn()
    print("ALL CHARTS DONE ->", OUT)
