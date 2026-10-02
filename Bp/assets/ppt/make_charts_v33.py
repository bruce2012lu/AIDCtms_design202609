# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.3 演示版 —— 新增图表生成脚本（c27–c30）

  c30（2026-09-06 页面修订新增）：三分母嵌套构成饼图，配第 15 页「30 倍差距来自分母层级」；
  数据取自报告 2.6.1 / 表 2.6.5 / 2.7.1 / 表 2.7.2，只重渲染该图： python -c "import make_charts_v33 as m; m.c30()"

复用 make_charts.py 的字体、色系、图注四段式（单位 / 口径 / 数据性质 / 来源）
与画布工具，不修改该文件、不重绘 c01–c26（旧 PNG 全部保留）。

所有数值严格取自：
  《算力冷却_验证与决策包_v1.0_20260905.html》
  《算力冷却商业调研报告_v3.3_20260906.html》
  《算力冷却系统新业务BP_v2.2_20260906.html》
不得自行增改，不得恢复任何已删除的伪精确点值。

运行： python make_charts_v33.py
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import ConnectionPatch
import numpy as np

from make_charts import (NAVY, BLUE, TEAL, RED, AMBER, GREY,
                         _finish, _plain, _canvas, _box, _arrow)


# ============================================================
# c27 价格可行域与实证毛利缺口（报告 6.2.1 / 8.1；BP §2.6、§9.2.1）
# ============================================================
def c27():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.6, 4.6),
                                   gridspec_kw={"width_ratios": [1.0, 1.22]})

    # ---------------- 左：价格可行域（元/kW） ----------------
    bands = [
        (0, 840, "#fde7e4", RED, "必然亏损"),
        (840, 1090, "#ffeede", "#c2410c", "不可接单"),
        (1090, 1440, "#fff7e8", AMBER, "容量不可达"),
        (1440, 1730, "#eaf1fd", BLUE, "可讨论区"),
        (1730, 1900, "#e8f7f0", TEAL, "可行"),
    ]
    BX0, BX1 = 0.46, 0.94
    for lo, hi, fc, ec, lab in bands:
        ax1.add_patch(mpatches.Rectangle((BX0, lo), BX1 - BX0, hi - lo, fc=fc,
                                         ec=ec, lw=1.1, zorder=2))
        ax1.text((BX0 + BX1) / 2, (lo + hi) / 2, lab, va="center", ha="center",
                 fontsize=10.2, color=ec, fontweight="bold", zorder=4)

    # 实证包价上限
    ax1.add_patch(mpatches.Rectangle((0.05, 684.75), 0.20, 715.00 - 684.75,
                                     fc=RED, ec=RED, lw=1.0, zorder=4))
    ax1.text(0.05, 640,
             "国内运营商包价上限\n684.75 – 715.00 元/kW\n两样本收敛 4.4%",
             fontsize=9.4, color=RED, fontweight="bold", ha="left", va="top",
             linespacing=1.6)

    # 缺口箭头
    ax1.annotate("", xy=(0.345, 840), xytext=(0.345, 715),
                 arrowprops=dict(arrowstyle="<|-|>", color=RED, lw=1.8))
    ax1.text(0.36, 900, "缺口 17%–23%", fontsize=9.8, color=RED,
             fontweight="bold", va="bottom", ha="center")

    ax1.set_xlim(0, 1.0)
    ax1.set_ylim(0, 1900)
    ax1.set_xticks([])
    ax1.set_yticks([700, 840, 1090, 1440, 1730])
    ax1.set_yticklabels(["700", "840", "1,090", "1,440", "1,730"], fontsize=9.0)
    for lbl, c in zip(ax1.get_yticklabels(), [RED, RED, "#c2410c", BLUE, TEAL]):
        lbl.set_color(c)
    ax1.set_ylabel("元/kW（200 kW 档，同边界）", fontsize=10, color=GREY)
    ax1.set_title("价格可行域　vs　国内运营商实证包价上限", fontsize=11.5,
                  color=NAVY, pad=12)
    for s in ("top", "right", "bottom"):
        ax1.spines[s].set_visible(False)
    ax1.spines["left"].set_color("#c9d1dc")
    ax1.tick_params(colors=GREY, length=0)

    # ---------------- 右：所需毛利率 vs 实证毛利率 ----------------
    need = [("所需\nP=1,500", 27.3), ("所需\nP=1,730", 37.0)]
    emp = [("曙光\n冷板产品", 10.36), ("Modine\n数据中心", 20.2),
           ("申菱\n设备", 21.46), ("申菱\n数据服务", 23.60), ("英维克\n境内", 23.83)]

    xs_n = [0.0, 1.0]
    xs_e = [2.6, 3.6, 4.6, 5.6, 6.6]
    b1 = ax2.bar(xs_n, [v for _, v in need], color=RED, width=0.62, zorder=3)
    b2 = ax2.bar(xs_e, [v for _, v in emp], color=BLUE, width=0.62, zorder=3)
    for x, (_, v) in zip(xs_n, need):
        ax2.text(x, v + 0.9, f"{v}%", ha="center", fontsize=11.2,
                 fontweight="bold", color=RED)
    for x, (_, v) in zip(xs_e, emp):
        ax2.text(x, v + 0.9, f"{v}%", ha="center", fontsize=9.8,
                 fontweight="bold", color=BLUE)

    ax2.axhspan(10.36, 23.83, color="#eaf1fd", alpha=0.5, zorder=0)
    ax2.axhspan(27.3, 37.0, color="#fde7e4", alpha=0.55, zorder=0)

    ax2.set_xticks(xs_n + xs_e)
    ax2.set_xticklabels([t for t, _ in need] + [t for t, _ in emp], fontsize=8.6)
    ax2.set_ylabel("贡献毛利率（%）", fontsize=10, color=GREY)
    ax2.set_ylim(0, 50)
    ax2.set_xlim(-0.75, 7.35)
    ax2.set_title("倒推所需 27%–37%　vs　国内一手实证 10.36%–23.83%",
                  fontsize=11.5, color=NAVY, pad=12)
    ax2.legend([b1, b2], ["倒推所需（必须达到什么）", "一手年报实证披露"],
               loc="upper left", frameon=False, fontsize=9.2,
               bbox_to_anchor=(0.0, 1.0))
    ax2.text(7.20, 45.0, "缺口约 4–27 个百分点", ha="right", fontsize=10.4,
             color=RED, fontweight="bold",
             bbox=dict(boxstyle="round,pad=0.40", fc="#fff7f6", ec="#f6c8c5"))

    note = (
        "单位：元/kW（左）；%（右）。\n"
        "口径：左轴为 200 kW 档同边界（CDU 本体 + 二次管路 + 工质 + 安装调试）；实证包价上限为运营商招标包价折算（含配套），"
        "裸机单价必然低于此数，且两样本均为 420/500 kW 大容量档，小容量不得插值。右轴为贡献毛利率；实证值分别取自曙光数创、申菱、英维克 2025 年报与 Modine FY2027Q1，"
        "其中仅曙光冷板产品为纯冷板式液冷，其余均含风冷或设施侧产品，四者口径不同、不可互相比较大小。\n"
        "数据性质：684.75 / 715.00 为实绩折算（1,725,576.99÷2,520；4,290,000÷6,000）；840 / 1,090 为本模型推导（BOM 假设 400/650 + 非BOM 440）；"
        "27.3% / 37.0% 为倒推所需值，回答「必须达到什么」，不是预测；实证毛利率为一手年报披露。\n"
        "来源：广东移动佛山三水询比公告 2026-07-22、中国移动江苏南京科创 C2 招标公告 2026-07-31（镜像，三级）；曙光数创／申菱／英维克 2025 年年度报告（一级）；"
        "Modine FY2027 Q1 业绩公告（二级）。报告 6.2.1、8.1；决策包 3.2–3.8。")
    _finish(fig, [ax1, ax2], note, "c27_price_band_margin_gap.png",
            left=0.085, right=0.975, bottom=0.36, top=0.90, wspace=0.24,
            spines=False)


# ============================================================
# c28 责任敞口倍数（报告 8.2；BP §13.2；决策包 4.2–4.3）
# ============================================================
def c28():
    fig, ax = plt.subplots(figsize=(11.2, 4.5))

    labels = ["行业指引转引的责任上限\n（合同价 10%–20%）",
              "单块 GPU 基板损坏\n（约 50 ml 冷却液）",
              "单柜 IT 资产全损",
              "该 CDU 覆盖范围全损\n（1.65 柜）"]
    hi = [0.20, 2.52, 144.0, 237.0]
    cols = [GREY, RED, "#7f1d1d", "#5b140e"]

    xs = list(range(len(labels)))
    ax.bar(xs, hi, color=cols, width=0.46, zorder=3)
    ax.set_yscale("log")
    ax.set_ylim(0.05, 2000)
    ax.set_xlim(-0.75, 3.6)
    ax.set_ylabel("相对合同额 14.30 万元的倍数（对数轴）", fontsize=10, color=GREY)
    ax.set_xticks(xs)
    ax.set_xticklabels(labels, fontsize=9.2)
    ax.axhline(1.0, color=NAVY, lw=1.3, ls="--", zorder=4)
    ax.text(3.55, 1.16, "合同额 = 1 倍", fontsize=9.2, color=NAVY, ha="right")

    ann = ["0.10–0.20 倍（毛利 0.97–1.93 倍）",
           "1.76–2.52 倍\n毛利 17.0–24.3 倍",
           "144 倍\n毛利 1,391 倍",
           "237 倍\n毛利 2,290 倍"]
    for x, h, t, c in zip(xs, hi, ann, cols):
        ax.text(x, h * 1.35, t, ha="center", va="bottom", fontsize=9.5,
                fontweight="bold", color=c, linespacing=1.45)

    # 责任上限区间高亮（无引线，说明并入左上角信息框）
    ax.add_patch(mpatches.Rectangle((-0.30, 0.096), 0.60, 0.108, fc="none",
                                    ec=RED, lw=1.5, ls=":", zorder=5))

    ax.text(0.015, 0.975,
            "合同额 14.30 万元 = 715 元/kW × 200 kW　·　项目毛利 1.48 万元 = 14.30 × 10.36%\n"
            "行业指引转引的 10%–20% 责任上限（1.43–2.86 万元）仅覆盖单块基板成本的 4%–11%\n"
            "责任封顶不是谈判技巧，是业务成立的前提条件：R1–R6 无法达成即不接单",
            transform=ax.transAxes, ha="left", va="top", fontsize=9.6, color=RED,
            linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.45", fc="#fff7f6", ec="#f6c8c5"))

    note = (
        "单位：倍（相对合同额；对数轴）。\n"
        "口径：以单台 200 kW CDU、国内实证包价上限 715 元/kW 计合同额 14.30 万元，毛利率取曙光数创冷板液冷 10.36% 实证锚点，"
        "得项目毛利 1.48 万元。敞口按 Lenovo GB300 NVL72 机柜 135 kW TDP × 液冷占比约 90% = 121.5 kW/柜，200÷121.5 = 1.646 柜推导。"
        "低密度存量改造客户的敞口约为高密集群的 1/4.71（720 万元 vs 3,392 万元）。\n"
        "数据性质：机柜功率为原厂规格（一级）；服务器价值强度 21.2 美元/W 为第三方 TCO 模型（二级）；汇率 7.2 为假设；"
        "GPU 基板更换成本 3.5–5.0 万美元与责任上限 10%–20% 为三级来源（confidence 0.55），不得写成行业事实，须以客户实际机型备件价格与客户书面条款替换。"
        "本图量化的是「若发生，赔付相对合同额与毛利处于什么量级」，不是对赔付概率的预测。\n"
        "来源：Lenovo GB300 Product Guide Table 27；Epoch AI 一 GW AI 数据中心 TCO 模型；曙光数创 2025 年年度报告；"
        "《The Definitive Guide to AI Data Centers》§2.4（转引，三级）；印度保险行业分析（三级）。报告 8.2；决策包 4.2–4.3。")
    _finish(fig, ax, note, "c28_liability_multiples.png",
            left=0.075, right=0.975, bottom=0.36, top=0.94)


# ============================================================
# c29 最小验证集与保护比（报告 12.4；BP §12.1；决策包 6.2–6.4）
# ============================================================
def c29():
    fig, ax = _canvas(11.4, 5.0)

    ax.text(50, 97, "G0 立项　→　【G0.5 前置证据门】　→　样机与 NRE 支出　→　G1 阶段二前",
            ha="center", va="top", fontsize=11.6, color=NAVY, fontweight="bold")

    # ---- 左：四项前置证据 ----
    _box(ax, 3, 79, 42, 8.4, "四项前置证据（并行执行）", BLUE, BLUE, fs=11)
    items = [
        ("M1", "四 SKU 关键件书面报价（每类 ≥2 家）", "4–6 周", "≈0"),
        ("M3", "客户责任条款草案 + 产品责任险报价", "4–8 周", "1–3 万元"),
        ("M4", "客户书面付款条款（四项要素齐备）", "2–4 周", "≈0"),
        ("M5", "客户书面平台包（工况与故障态齐备）", "4–8 周", "≈0"),
    ]
    for i, (mid, txt, wk, cost) in enumerate(items):
        y = 66 - i * 10.8
        ax.add_patch(mpatches.FancyBboxPatch(
            (3, y), 42, 8.8, boxstyle="round,pad=0,rounding_size=0.02",
            fc="#f4f7ff", ec="#c9d8ff", lw=1.1, zorder=3))
        ax.add_patch(mpatches.Rectangle((3, y), 1.1, 8.8, fc=BLUE, ec="none",
                                        zorder=4))
        ax.text(6.6, y + 4.4, mid, fontsize=10.6, color=BLUE, fontweight="bold",
                va="center", zorder=5)
        ax.text(11.8, y + 5.9, txt, fontsize=9.5, color="#33415a", va="center",
                zorder=5)
        ax.text(11.8, y + 2.6, f"周期 {wk}　·　现金成本 {cost}", fontsize=8.7,
                color=GREY, va="center", zorder=5)

    _box(ax, 3, 12, 42, 8.4, "合计：现金成本 < 5 万元　·　周期 6–8 周", BLUE, BLUE,
         fs=11)

    _arrow(ax, 46.5, 45, 55.5, 45, c=RED, lw=2.6)
    ax.text(51, 48.5, "决定", ha="center", fontsize=10, color=RED,
            fontweight="bold")

    # ---- 右：受保护的支出 ----
    _box(ax, 57, 79, 40, 8.4, "受门禁保护的支出（M9）", RED, RED, fs=11)
    ax.add_patch(mpatches.FancyBboxPatch(
        (57, 25.5), 40, 49, boxstyle="round,pad=0,rounding_size=0.02",
        fc="#fff7f6", ec="#f6c8c5", lw=1.2, zorder=3))
    ax.text(77, 64.5, "245 万元", ha="center", va="center", fontsize=29,
            color=RED, fontweight="bold", zorder=5)
    ax.text(77, 55.0,
            "产品 NRE / 软件 / IP　115 万元\n样机 / 物料 / 工装　　　130 万元",
            ha="center", va="center", fontsize=10.2, color="#33415a",
            linespacing=1.75, zorder=5)
    ax.text(77, 46.5, "占阶段一 800 万元上限的 30.6%　·　周期 16–36 周",
            ha="center", va="center", fontsize=9.4, color=GREY, zorder=5)
    ax.text(77, 40.0,
            "阶段一唯一一笔不可回收的大额支出：\n"
            "营运资金可回收，团队与测试可按月止损，\n"
            "只有样机与 NRE 在设计输入错误时完全沉没",
            ha="center", va="top", fontsize=9.2, color=RED, linespacing=1.7,
            zorder=5)

    _box(ax, 57, 12, 40, 8.4, "保护比 = 245 ÷ 5 = 49 : 1", RED, RED, fs=13)

    ax.text(50, 7.0,
            "在 M1、M3、M4、M5 全部取得之前，样机物料、工装与 NRE 的任何采购不得启动，包括「先小批量试做」。\n"
            "若四项中任何一项 12 周内无法取得，应视为 G1 无法通过的早期信号——正确动作是暂停而非加大投入。",
            ha="center", va="top", fontsize=9.4, color=NAVY, linespacing=1.75)

    _plain(fig, "c29_min_evidence_gate.png")


# ============================================================
# c30 三分母嵌套构成饼图（报告 2.6.1 / 表 2.6.5 / 2.7.1 / 表 2.7.2）
# ============================================================
# 基准年 2029（Dell'Oro 液冷 2029 约 70 亿美元的机构预测锚点年）。
# 全部金额取自表 2.6.5 的 Base 值（十亿美元）：L1 319、L2 1,383、L3 1,702、DCPI 106；
# 液冷取 2.7.2 备注的 Dell'Oro 2029 约 70 亿美元 = 7.0 十亿美元。
# 扇区百分比全部由上述数字复算得出，不引入报告中没有的数字；
# L1 与 DCPI 的内部细分在报告与 Dell'Oro 公开摘要中均无金额，故只切两块、不编造细分。
C30_L1, C30_L2, C30_DCPI, C30_LC = 319.0, 1383.0, 106.0, 7.0
C30_L3 = C30_L1 + C30_L2          # 1,702
# Microsoft YaHei 无 ⊂ / ⊃ 字形，含该符号的文本按此顺序回退（其余字符仍用 YaHei）
SYMFALLBACK = ["Microsoft YaHei", "Segoe UI Symbol", "Cambria"]


def c30():
    LIGHT = "#d5deee"                 # 「其他 / 未拆分」扇区的中性浅色
    TX = "#33415a"
    W, H = 12.6, 5.72                 # 画布英寸；全部坐标以英寸计
    fig = plt.figure(figsize=(W, H))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.set_aspect("equal")
    ax.axis("off")

    R = 0.86                          # 饼半径（英寸）
    CY = 3.72                         # 饼心高度
    CX = [1.60, 5.70, 9.80]           # 三个饼心（右侧留出饼③ 液冷标签空间）

    # 三层数据：(总额, 高亮扇区值, 高亮色, 饼标题, 副标题)
    layers = [
        (C30_L3, C30_L1, NAVY, "① L3 算力基建总投资", "2029 ≈ 1.70 万亿美元（表 2.6.5 Base）"),
        (C30_L1, C30_DCPI, BLUE, "② L1 设施侧 CapEx", "2029 ≈ 3,190 亿美元（表 2.6.5 Base）"),
        (C30_DCPI, C30_LC, TEAL, "③ DCPI 设备市场（Aug-2026 版）", "2029 ≈ 1,060 亿美元（表 2.6.5 Base）"),
    ]
    half = []                          # 每个饼高亮扇区的半角（度）
    for cx, (tot, hi, col, head, sub) in zip(CX, layers):
        p = hi / tot * 100.0
        h = 180.0 * hi / tot           # 高亮扇区半角：扇区居中指向右侧（0°）
        half.append(h)
        ax.add_patch(mpatches.Wedge((cx, CY), R, h, 360 - h, fc=LIGHT, ec="#ffffff",
                                    lw=1.2, zorder=3))
        ax.add_patch(mpatches.Wedge((cx, CY), R, -h, h, fc=col, ec="#ffffff",
                                    lw=1.2, zorder=4))
        # 「其他」扇区百分比（居左）
        ax.text(cx - 0.30, CY + 0.02, f"{100 - p:.0f}%", ha="center", va="center",
                fontsize=14, color=TX, fontweight="bold", zorder=6)
        # 高亮扇区百分比：足够大时写在扇区内，否则写在右侧标签里
        if p >= 15:
            ax.text(cx + 0.52, CY, f"{p:.0f}%", ha="center", va="center", fontsize=11,
                    color="#ffffff", fontweight="bold", zorder=6)
        # 饼标题
        ax.text(cx, 5.32, head, ha="center", va="center", fontsize=12, color=col,
                fontweight="bold")
        ax.text(cx, 5.05, sub, ha="center", va="center", fontsize=9, color=GREY)

    # ---- 放大锥：饼 k 的高亮扇区两条边 → 饼 k+1 的上下切点 ----
    for k in (0, 1):
        cx1, cx2 = CX[k], CX[k + 1]
        col = layers[k][2]
        h = np.deg2rad(half[k])
        top1 = (cx1 + R * np.cos(h), CY + R * np.sin(h))
        bot1 = (cx1 + R * np.cos(h), CY - R * np.sin(h))
        top2 = (cx2, CY + R)
        bot2 = (cx2, CY - R)
        ax.add_patch(mpatches.Polygon([top1, top2, bot2, bot1], closed=True, fc=col,
                                      ec="none", alpha=0.07, zorder=1))
        for a, b in ((top1, top2), (bot1, bot2)):
            ax.plot([a[0], b[0]], [a[1], b[1]], color=col, lw=1.1, ls=(0, (4, 3)),
                    zorder=2)
        xm = (cx1 + R + cx2 - R) / 2
        ax.text(xm, CY + R + 0.20, "放大 L1" if k == 0 else "放大 DCPI", ha="center",
                va="center", fontsize=8.8, color=col, fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.25", fc="#ffffff", ec=col, lw=0.8))
        ax.annotate("", xy=(cx2 - R - 0.06, CY), xytext=(cx1 + R + 0.06, CY),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=1.4,
                                    mutation_scale=14), zorder=5)

    # ---- 高亮扇区标签（饼①、② 放在放大锥下方的间隙；饼③ 放在右侧，带引线） ----
    p1 = C30_L1 / C30_L3 * 100
    p2 = C30_DCPI / C30_L1 * 100
    p3 = C30_LC / C30_DCPI * 100
    ax.text((CX[0] + CX[1]) / 2, CY - R - 0.12,
            f"■ L1 设施侧 CapEx\n约 {p1:.0f}%（3,190 亿美元）\n= 饼② 的全部",
            ha="center", va="top", fontsize=8.8, color=NAVY, linespacing=1.45, zorder=6)
    ax.text((CX[1] + CX[2]) / 2, CY - R - 0.12,
            f"■ DCPI 设备制造商收入\n约 {p2:.0f}%（1,060 亿美元）\n= 饼③ 的全部",
            ha="center", va="top", fontsize=8.8, color=BLUE, linespacing=1.45, zorder=6)
    ax.annotate(f"液冷设备制造商收入\n约 {p3:.0f}%（≈70 亿美元）\n区间 5%–8%",
                xy=(CX[2] + R * 0.97, CY), xytext=(CX[2] + R + 0.32, CY + 0.42),
                ha="left", va="center", fontsize=8.8, color=TEAL, fontweight="bold",
                linespacing=1.45, zorder=6,
                arrowprops=dict(arrowstyle="-", color=TEAL, lw=1.0, shrinkA=0, shrinkB=1))
    # 液冷扇区加粗描边高亮
    hl = mpatches.Wedge((CX[2], CY), R, -half[2], half[2], fc=TEAL, ec=TEAL, lw=2.0,
                        zorder=5)
    ax.add_patch(hl)

    # ---- 「其他」扇区标签：饼下方居中，短引线指向饼底 ----
    rest = [
        (f"L2 IT 设备\n（服务器 / GPU / 存储 / 网络）\n约 {100 - p1:.0f}%（1.38 万亿美元）\n与液冷供应商无竞争或替代关系"),
        (f"L1 中 DCPI 以外的部分\n约 {100 - p2:.0f}%（几何余量，未拆分）\n不是建筑 / 安装 / EPC 价值的估算"),
        (f"DCPI 其他品类　约 {100 - p3:.0f}%（未公开细分）\nUPS、其余热管理、机柜配电与母线、\n机架配电、IT 机架与 containment、\n软件与服务"),
    ]
    for cx, txt, dx in zip(CX, rest, (0.0, 0.0, 0.22)):
        ax.plot([cx, cx], [CY - R, CY - R - 0.10], color=TX, lw=0.8, zorder=2)
        ax.text(cx + dx, CY - R - 0.12, txt, ha="center", va="top", fontsize=8.4,
                color=TX, linespacing=1.45, zorder=6)

    # ---- 图下结论句 ----
    ax.text(W / 2, 1.76,
            "三个饼不是并列，而是层层收窄：L3 ⊃ L1 ⊃ DCPI ⊃ 液冷。液冷占 DCPI 约 5%–11%，占 L1 约 1%–6%，占 L3 不到 1%"
            "——30 倍差距来自分母层级，不是液冷本身的变化。",
            ha="center", va="center", fontsize=10.2, color=RED, fontweight="bold",
            fontfamily=SYMFALLBACK,
            bbox=dict(boxstyle="round,pad=0.45", fc="#fff7f6", ec="#f6c8c5"))

    note = (
        "单位：亿美元 / 万亿美元（由表 2.6.5 的十亿美元换算）；扇区为占各自饼总额的百分比，三饼总额依次为 1,702 / 319 / 106 十亿美元。\n"
        "口径：基准年 2029（Dell'Oro 液冷 2029 约 70 亿美元的机构预测锚点年）。L3 = L1 + L2；包含链 液冷 ⊂ DCPI ⊂ L1 ⊂ L3（2.6.1），L2 与液冷供应商无竞争或替代关系。"
        "饼②「DCPI 以外」扇区只是 L1 − DCPI 的几何余量，不是对建筑、安装人工或 EPC 价值的估算（2.6.1 禁止以 DCPI 与 L1 相减推导施工价值），故不再细分；"
        "饼③ Dell'Oro 公开摘要未给出 UPS / 热管理 / 配电等品类金额，故只切「液冷 / 其他」，不编造细分。\n"
        "数据性质：扇区按 Base 值绘制，仅示意量级，Base 不作对外点值引用；可引用的是区间——2029 液冷占 L3 0.3%–0.5%、占 L1 1.7%–2.9%、占 DCPI 5%–8%（表 2.7.2）。"
        "L1 319、L3 1,702 为本报告模型；DCPI 106 为本报告桥接（仅 2030 的 1,200 亿美元是 Dell'Oro 机构预测）；L2 1,383 中 AI 部分 1.08 万亿美元为 IDC 机构预测、非 AI 部分为本报告模型；"
        "液冷 70 亿美元为 Dell'Oro 机构预测。复算：319÷1,702 = 18.7%；106÷319 = 33.2%；7.0÷106 = 6.6%；7.0÷319 = 2.2%；7.0÷1,702 = 0.41%。\n"
        "来源：Dell'Oro《Liquid Cooling Advanced Research》公开摘要 2026-01-08、《August-2026 DCPI Forecast》新闻稿 2026-08-19；IDC AI Infrastructure Tracker 公开更新 2026；"
        "JLL《2026 Global Data Center Outlook》2026-01-06（设施侧单位强度）；报告 v3.3 表 2.6.5、2.7.1、2.7.2。")
    fs = 8.0
    from make_charts import _wrap
    fw, fh = fig.get_size_inches()
    wrapped = _wrap(note, fw, fs)
    fig.text(0.010, 0.014, wrapped, fontsize=fs, color=GREY, va="bottom", ha="left",
             linespacing=1.62, fontfamily=SYMFALLBACK)
    fig.patch.set_facecolor("#ffffff")
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "c30_denominator_pies.png")
    fig.savefig(path, dpi=300, facecolor="#ffffff")
    plt.close(fig)
    print("saved c30_denominator_pies.png")


def build():
    c27()
    c28()
    c29()
    c30()
    print("done: c27 / c28 / c29 / c30")


if __name__ == "__main__":
    build()
