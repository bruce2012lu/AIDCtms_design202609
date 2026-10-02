# -*- coding: utf-8 -*-
"""原理图、流程图与数据图（抽象坐标，非 mm）。"""
import math
import model as M
from svg import (Canvas, INK, BLUE, TEAL, ORANGE, RED, GREY, CU, WATER, FIN)

G = M.GEO
A = M.solve("DP-A")
B = M.solve("DP-B")


def _box(c, x, y, w, h, title, sub=None, fill="#f6f9fc", stroke=INK,
         tsize=11, ssize=9.5, tcol=INK, sw=1.0, rx=4):
    c.rect(x, y, w, h, fill, stroke, sw, rx=rx)
    if sub:
        c.text(x + w / 2, y + h / 2 - 2, title, tsize, tcol, "middle",
               cn=True, weight="bold")
        for i, s in enumerate(sub if isinstance(sub, list) else [sub]):
            c.text(x + w / 2, y + h / 2 + 11 + i * 11, s, ssize, GREY,
                   "middle", cn=True)
    else:
        c.text(x + w / 2, y + h / 2 + 4, title, tsize, tcol, "middle",
               cn=True, weight="bold")


# ============================================================
# 系统层级
# ============================================================
def fig_hierarchy():
    c = Canvas((0, 0, 940, 300), aria="GB300 system hierarchy to cold plate")
    lv = [
        (20, "GB300 NVL72 机柜", ["72× B300 + 36× Grace", "全液冷 · 48U"],
         "#e7f0fb", BLUE),
        (200, "计算托盘 ×18", ["每托盘 2× Grace + 4× B300", "冷板并联，禁串联"],
         "#eef5ff", BLUE),
        (380, "GB300 超级芯片 ×36", ["1× Grace + 2× B300", "NVLink-C2C 900 GB/s"],
         "#f3f8ff", BLUE),
        (560, "B300 GPU（本设计对象）",
         ["双 reticle die + 8× HBM3e", "TGP 1100 / 1400 W"],
         "#fff5eb", ORANGE),
        (740, "CP-B300-JM-01 冷板",
         ["GPU 射流 + HBM 微通道", "95×75×8.5 mm"],
         "#f0fbf8", TEAL),
    ]
    for i, (x, t, s, fill, col) in enumerate(lv):
        _box(c, x, 60, 168, 92, t, s, fill, col, 12, 9.5)
        if i < len(lv) - 1:
            c.arrow(x + 168, 106, x + 178, 106, GREY, 2.2)
    c.text(20, 40, "范围界定：本报告只设计最右一格；左侧四格是约束来源，"
                   "不是本文件的设计对象", 11, INK, cn=True, weight="bold")
    c.rect(556, 48, 356, 116, "none", ORANGE, 1.6, rx=6,
           extra='stroke-dasharray="7 4"')
    c.text(734, 182, "↑ 设计边界：芯片规格（输入） → 冷板（输出）", 11,
           ORANGE, "middle", cn=True, weight="bold")

    # 不在范围
    out = ["Grace CPU 冷板", "NVSwitch 托盘冷板", "CDU / 机柜歧管",
           "UQD 快接本体设计", "漏液检测链"]
    c.text(20, 218, "不在本报告范围（由 OEM / 系统方负责）：", 11, GREY,
           cn=True, weight="bold")
    for i, o in enumerate(out):
        c.rect(20 + i * 176, 232, 166, 34, "#f1f3f6", GREY, 0.9, rx=4,
               extra='stroke-dasharray="4 3"')
        c.text(103 + i * 176, 253, o, 10, GREY, "middle", cn=True)
    return c.render()


# ============================================================
# 设计流程（阶段门）
# ============================================================
def fig_process():
    c = Canvas((0, 0, 960, 470), aria="Cold plate design process with gates")
    stages = [
        ("① 需求与输入", ["芯片规格 / 热包络", "机柜水力表", "接口与标准"],
         "DR0 输入冻结"),
        ("② 概念与选型", ["方案权衡矩阵", "分区策略", "专利 FTO 初筛"],
         "DR1 方案选定"),
        ("③ 性能设计", ["热阻预算分配", "射流参数窗", "流量/压降预算"],
         "DR2 性能基线"),
        ("④ 一维计算", ["能量平衡", "水力与换热关联式", "敏感性与差距闭合"],
         "DR2 同门"),
        ("⑤ 三维仿真", ["共轭 CFD", "网格无关性", "工况矩阵"],
         "DR3 仿真通过"),
        ("⑥ 机械与图纸", ["层叠与公差", "承压/变形", "2D/3D/爆炸"],
         "DR3 同门"),
        ("⑦ 样件与试验", ["TTV 热阻", "流阻曲线", "红外/氦检"],
         "DR4 送样放行"),
    ]
    x0, y0, bw, bh, gapx = 22, 64, 122, 104, 132
    for i, (t, items, gate) in enumerate(stages):
        x = x0 + i * gapx
        c.rect(x, y0, bw, bh, "#f6f9fc", BLUE, 1.2, rx=5)
        c.text(x + bw / 2, y0 + 19, t, 11.5, INK, "middle", cn=True,
               weight="bold")
        for j, it in enumerate(items):
            c.text(x + 8, y0 + 40 + j * 15, "· " + it, 9.3, GREY, cn=True)
        # 阶段门
        c.poly([(x + bw / 2, y0 + bh + 14), (x + bw / 2 + 46, y0 + bh + 34),
                (x + bw / 2, y0 + bh + 54), (x + bw / 2 - 46, y0 + bh + 34)],
               "#fff9e9", "#a65b00", 1.1)
        c.text(x + bw / 2, y0 + bh + 38, gate, 9.0, "#a65b00", "middle",
               cn=True, weight="bold")
        c.line(x + bw / 2, y0 + bh, x + bw / 2, y0 + bh + 14, GREY, 1.0)
        if i < len(stages) - 1:
            c.arrow(x + bw, y0 + bh / 2, x + gapx, y0 + bh / 2, GREY, 2.0)

    # 迭代回路
    c.curve_arrow(f"M {x0+4*gapx+61} {y0+bh+58} "
                  f"C {x0+4*gapx+61} {y0+bh+110}, "
                  f"{x0+2*gapx+61} {y0+bh+110}, {x0+2*gapx+61} {y0+bh+58}",
                  RED, 1.8, dash="8 4")
    c.text(x0 + 3 * gapx + 40, y0 + bh + 126,
           "仿真不达标 → 回 ③/④ 改几何（孔径、阵列密度、TIM2）", 11, RED,
           "middle", cn=True, weight="bold")
    c.curve_arrow(f"M {x0+6*gapx+61} {y0+bh+58} "
                  f"C {x0+6*gapx+61} {y0+bh+168}, "
                  f"{x0+2*gapx+61} {y0+bh+168}, {x0+2*gapx+61} {y0+bh+62}",
                  ORANGE, 1.8, dash="8 4")
    c.text(x0 + 4 * gapx + 40, y0 + bh + 184,
           "试验与仿真偏差 >15% → 修正模型并回 ③（V&V 闭环）", 11, ORANGE,
           "middle", cn=True, weight="bold")

    c.text(22, 34, "设计流程：门控 + 双回路迭代。本报告 v2.0 覆盖 ①–⑥，"
                   "⑤ 的工具尚未选定，⑦ 未开始。", 12.5, INK, cn=True,
           weight="bold")
    c.rect(x0 - 6, y0 - 10, 4 * gapx + 8, bh + 74, "none", TEAL, 1.6, rx=6,
           extra='stroke-dasharray="7 4"')
    c.text(x0 + 2 * gapx, y0 - 16, "本报告已完成", 11, TEAL, "middle",
           cn=True, weight="bold")
    return c.render()


# ============================================================
# 热阻网络
# ============================================================
def fig_rnetwork():
    c = Canvas((0, 0, 900, 290), aria="Thermal resistance network")
    nodes = [("Tj 结", 40), ("硅/TIM1/盖", 170), ("Tc 壳", 320),
             ("TIM2", 420), ("余铜", 545), ("对流", 665), ("Tf 进液", 820)]
    y = 108
    # 主链
    segs = [
        (120, 250, "R_pkg", "0.008–0.012", "#718096", "封装内，本设计不可改"),
        (350, 470, "R_TIM2", "0.004–0.008", ORANGE, "可改：高性能 TIM/液金"),
        (495, 600, "R_wall", f"{M.R_WALL:.4f}", CU, "余铜 2.0 mm"),
        (625, 760, "R_conv", "0.011–0.024", TEAL, "本设计主攻"),
    ]
    for x1, x2, name, val, col, note in segs:
        c.rect(x1, y - 20, x2 - x1, 40, "#fff", col, 2.0, rx=4)
        c.text((x1 + x2) / 2, y - 3, name, 12, col, "middle", weight="bold")
        c.text((x1 + x2) / 2, y + 13, val, 11, INK, "middle")
        c.text((x1 + x2) / 2, y + 42, note, 9.5, GREY, "middle", cn=True)
    # 导线
    xs = [40, 120, 250, 350, 470, 495, 600, 625, 760, 820]
    c.line(40, y, 120, y, INK, 2.0)
    c.line(250, y, 350, y, INK, 2.0)
    c.line(470, y, 495, y, INK, 2.0)
    c.line(600, y, 625, y, INK, 2.0)
    c.line(760, y, 820, y, INK, 2.0)
    # 温度节点
    for lab, x, col in (("Tj", 40, RED), ("Tc", 300, ORANGE),
                        ("Tf,in 40 °C", 820, BLUE)):
        c.circle(x, y, 7, col, col, 1)
        c.text(x, y - 16, lab, 11.5, col, "middle", cn=True, weight="bold")
    # 热流源
    c.rect(8, y - 62, 64, 30, "#fed7d7", RED, 1.2, rx=4)
    c.text(40, y - 42, "P 1100 W", 10.5, RED, "middle", weight="bold")
    c.arrow(40, y - 32, 40, y - 9, RED, 1.8)
    # 目标框
    c.rect(292, 176, 540, 44, "#f3fbf8", TEAL, 1.4, rx=5)
    c.text(562, 195, "壳–进液 R_θ,c-in = R_TIM2 + R_wall + R_conv", 12,
           INK, "middle", cn=True, weight="bold")
    c.text(562, 212, f"实算区间 {A['R_lo']:.4f} – {A['R_hi']:.4f} °C/W"
                     f"　目标 < 0.028 °C/W（DP-A）", 11, TEAL, "middle",
           cn=True)
    c.text(20, 254, "说明：冷板供货范围只含 TIM2 以下（橙/铜/青三段）。"
                    "R_pkg 由 NVIDIA 封装决定，是本设计拿不到的预算。",
           11, GREY, cn=True)
    c.text(20, 274, "R_conv 只用短槽模型。Martin 1977 因 Re_D < 2000 不采用，"
                    "不再给乐观下界。", 11, RED, cn=True)
    return c.render()


# ============================================================
# 热阻预算条形图
# ============================================================
def fig_rchain_bar():
    c = Canvas((0, 0, 880, 330), aria="Thermal resistance budget bars")
    x0, y0, w, rowh = 150, 58, 560, 40
    rmax = 0.050
    sx = lambda r: x0 + r / rmax * w

    rows = [
        ("DP-A TIM2=0.004", [(M.R_TIM2[0], ORANGE), (M.R_WALL, CU),
                              (A["con"]["R"], TEAL)], A["R_lo"]),
        ("DP-A TIM2=0.008", [(M.R_TIM2[1], ORANGE), (M.R_WALL, CU),
                              (A["con"]["R"], TEAL)], A["R_hi"]),
        ("DP-B TIM2=0.004", [(M.R_TIM2[0], ORANGE), (M.R_WALL, CU),
                              (B["con"]["R"], TEAL)], B["R_lo"]),
        ("DP-B TIM2=0.008", [(M.R_TIM2[1], ORANGE), (M.R_WALL, CU),
                              (B["con"]["R"], TEAL)], B["R_hi"]),
    ]
    # 网格
    for i in range(9):
        r = i * 0.005
        c.line(sx(r), y0 - 10, sx(r), y0 + len(rows) * rowh + 4, "#e4ebf3", 1)
        c.text(sx(r), y0 - 16, f"{r:.3f}", 9.5, GREY, "middle")
    c.text(x0 + w / 2, y0 - 34, "壳–进液热阻 R_θ,c-in  (°C/W)", 12, INK,
           "middle", cn=True, weight="bold")

    for i, (name, parts, tot) in enumerate(rows):
        y = y0 + i * rowh
        c.text(x0 - 12, y + 20, name, 11, INK, "end", cn=True)
        cur = 0.0
        for val, col in parts:
            c.rect(sx(cur), y + 4, sx(cur + val) - sx(cur), 24, col, "#fff",
                   0.8)
            cur += val
        c.text(sx(cur) + 8, y + 21, f"{tot:.4f}", 11, INK, weight="bold")

    # 目标线
    for r, lab, col, an in ((0.028, "DP-A 目标 0.028", RED, "start"),
                            (0.025, "DP-B 目标 0.025", "#a65b00", "end")):
        c.line(sx(r), y0 - 6, sx(r), y0 + len(rows) * rowh + 2, col, 2.0,
               'stroke-dasharray="6 4"')
        dx = 5 if an == "start" else -5
        c.text(sx(r) + dx, y0 + len(rows) * rowh + 18, lab, 10, col, an,
               cn=True, weight="bold")

    # 图例
    for i, (col, lab) in enumerate([(ORANGE, "R_TIM2"), (CU, "R_wall 余铜"),
                                    (TEAL, "R_conv 对流")]):
        c.rect(150 + i * 150, 286, 16, 11, col, "#fff", 0.6)
        c.text(172 + i * 150, 296, lab, 10.5, GREY, cn=True)
    c.text(150, 318, "关键结论：保守模型两档均越过目标线 —— 设计尚未证明，"
                     "必须用 CFD + TTV 把区间收窄。", 11, RED, cn=True,
           weight="bold")
    return c.render()


# ============================================================
# 系统水力原理图
# ============================================================
def fig_pid():
    c = Canvas((0, 0, 940, 420), aria="System hydraulic schematic")

    def valve(x, y, r=9):
        c.poly([(x - r, y - r), (x + r, y + r), (x + r, y - r),
                (x - r, y + r)], "#fff", INK, 1.4)

    def instr(x, y, tag, col=INK):
        c.circle(x, y, 11, "#fff", col, 1.3)
        c.text(x, y + 4, tag, 9, col, "middle", weight="bold")

    # CDU
    c.rect(24, 150, 118, 110, "#eef5ff", BLUE, 1.6, rx=5)
    c.text(83, 178, "CDU", 14, BLUE, "middle", weight="bold")
    c.text(83, 197, "一次侧/二次侧", 9.5, GREY, "middle", cn=True)
    c.text(83, 213, "25–45 °C", 10, INK, "middle")
    c.text(83, 230, "59–177 L/min", 10, INK, "middle")
    c.text(83, 247, "16–127 kPa", 10, INK, "middle")
    c.text(83, 274, "机柜表（整柜口径）", 9.5, GREY, "middle", cn=True)

    # 机柜歧管
    c.rect(178, 60, 26, 300, WATER, BLUE, 1.4, rx=3)
    c.text(191, 50, "供液立管", 9.5, BLUE, "middle", cn=True)
    c.rect(742, 60, 26, 300, "#fbd38d", ORANGE, 1.4, rx=3)
    c.text(755, 50, "回液立管", 9.5, ORANGE, "middle", cn=True)
    c.arrow(142, 190, 178, 190, BLUE, 2.4)
    c.arrow(768, 230, 800, 230, ORANGE, 2.4)
    c.line(800, 230, 830, 230, ORANGE, 2.4)
    c.line(830, 230, 830, 330, ORANGE, 2.4)
    c.line(830, 330, 83, 330, ORANGE, 2.4)
    c.arrow(83, 330, 83, 262, ORANGE, 2.4)

    # 托盘
    c.rect(240, 78, 470, 264, "#fbfdff", INK, 1.4, rx=6,
           extra='stroke-dasharray="8 4"')
    c.text(475, 98, "GB300 计算托盘（1 of 18）：4× B300 冷板并联 + "
                    "2× Grace 冷板（不在本供货）", 11, INK, "middle", cn=True,
           weight="bold")

    # 托盘分流器
    c.rect(258, 120, 22, 196, WATER, BLUE, 1.2, rx=3)
    c.rect(672, 120, 22, 196, "#fbd38d", ORANGE, 1.2, rx=3)
    c.text(269, 112, "分流", 9, BLUE, "middle", cn=True)
    c.text(683, 112, "汇流", 9, ORANGE, "middle", cn=True)
    c.arrow(204, 140, 258, 140, BLUE, 1.8)
    c.arrow(694, 280, 742, 280, ORANGE, 1.8)

    # 四块冷板
    for i in range(4):
        y = 132 + i * 52
        c.rect(330, y, 300, 40, "#f0fbf8", TEAL, 1.5, rx=4)
        c.text(480, y + 17, f"CP-B300-JM-01  #{i+1}", 11, INK, "middle",
               weight="bold")
        c.text(480, y + 32, "2.0 L/min · ΔP ≤18 kPa · 1100 W", 9.5, GREY,
               "middle", cn=True)
        c.arrow(280, y + 20, 330, y + 20, BLUE, 1.5)
        c.arrow(630, y + 20, 672, y + 20, ORANGE, 1.5)
        # 托盘孔板（限流）
        c.rect(300, y + 12, 14, 16, "#cbd5e0", INK, 1.0)
        c.text(307, y + 24, "◦", 9, INK, "middle")
    c.text(307, 128, "孔板", 8.5, GREY, "middle", cn=True)

    # 仪表
    instr(310, 352, "FI", TEAL)
    instr(352, 352, "PI", TEAL)
    instr(394, 352, "TI", TEAL)
    instr(436, 352, "dP", RED)
    c.text(470, 356, "SAT 实测点：单板流量 / 进出压力 / 进出温度 / 跨板压差",
           10.5, GREY, cn=True)

    # UQD
    for x, col in ((318, BLUE), (646, ORANGE)):
        c.circle(x, 106, 6, "#fff", col, 1.4)
    c.text(318, 96, "UQD", 8.5, BLUE, "middle")
    c.text(646, 96, "UQD", 8.5, ORANGE, "middle")

    c.text(24, 30, "图 7-1 · 系统水力原理图（本冷板在回路中的位置与口径分界）",
           13, INK, cn=True, weight="bold")
    c.text(24, 392, "口径分界：整柜 59–177 L/min 与 16–127 kPa 是机柜表，"
                    "不是单板保证值；单板 2.0 L/min 由托盘孔板分配，SAT 实测。",
           11, RED, cn=True)
    c.text(24, 410, "一对 UQD 参考 4–8 kPa，是否计入冷板 20 kPa 窗必须在 ICD "
                    "中写明。四板必须并联，串联会让末板吃前三块的预热。", 11,
           GREY, cn=True)
    return c.render()


# ============================================================
# 冷板内部流路原理图
# ============================================================
def fig_internal():
    c = Canvas((0, 0, 920, 440), aria="Cold plate internal flow schematic")
    c.text(20, 30, "图 7-2 · 冷板内部流路原理图（流量按 DP-A 2.0 L/min）",
           13, INK, cn=True, weight="bold")

    # 进液
    _box(c, 20, 70, 128, 56, "进液 IN", ["2.0 L/min · 40 °C"], "#e7f0fb", BLUE)
    # 静压箱
    _box(c, 196, 70, 150, 56, "盖板静压箱", ["铺开静压 · 无换热任务"],
         WATER, BLUE)
    c.arrow(148, 98, 196, 98, BLUE, 2.4)

    # 分流节点
    c.poly([(392, 98), (420, 76), (448, 98), (420, 120)], "#fff9e9",
           "#a65b00", 1.5)
    c.text(420, 102, "分流", 10, "#a65b00", "middle", cn=True, weight="bold")
    c.arrow(346, 98, 392, 98, BLUE, 2.4)
    c.text(420, 62, "靠孔阻与隔墙，不靠外置调节阀", 9.5, GREY, "middle",
           cn=True)

    # GPU 支路
    c.arrow(448, 88, 520, 60, BLUE, 2.6)
    _box(c, 520, 28, 170, 62, "GPU 射流区 ×2",
         ["1.60 L/min（80%）", f"128×⌀0.50 · V={A['jet']['V']:.2f} m/s"],
         "#fff5eb", ORANGE)
    _box(c, 714, 28, 168, 62, "短槽 + 抽吸",
         [f"Re_D={A['jet']['Re']:.0f} · L≤8 mm", "驻点 → 壁面射流 → 上抽"],
         "#fffaf3", ORANGE)
    c.arrow(690, 59, 714, 59, ORANGE, 2.0)

    # HBM 支路
    c.arrow(448, 110, 520, 158, TEAL, 2.6)
    _box(c, 520, 130, 170, 62, "HBM 微通道 ×2",
         ["0.40 L/min（20%）", "无喷嘴（权项必要特征）"], "#f0fbf8", TEAL)
    _box(c, 714, 130, 168, 62, "限速平流",
         [f"V={A['hbm']['V']:.2f} m/s ≤ 0.80", "沿 HBM 长边均流"],
         "#f0fbf8", TEAL)
    c.arrow(690, 161, 714, 161, TEAL, 2.0)

    # 隔离肋
    c.rect(506, 96, 390, 22, "#1a365d", "#1a365d", 1, rx=3)
    c.text(701, 112, "隔离肋 2.0 mm：水力隔墙 + 抗弯加强筋（无流体穿越）",
           10.5, "#fff", "middle", cn=True, weight="bold")

    # 汇流
    c.poly([(798, 250), (826, 228), (854, 250), (826, 272)], "#fff9e9",
           "#a65b00", 1.5)
    c.text(826, 254, "汇流", 10, "#a65b00", "middle", cn=True, weight="bold")
    c.curve_arrow("M 882 59 C 906 59, 906 200, 854 245", ORANGE, 2.2)
    c.curve_arrow("M 882 161 C 900 161, 890 220, 852 240", TEAL, 2.2)

    _box(c, 620, 300, 160, 56, "出液歧管", ["汇合两路"], "#fbd38d", ORANGE)
    c.arrow(812, 268, 780, 300, ORANGE, 2.4)
    _box(c, 420, 300, 160, 56, "出液 OUT",
         [f"≈{A['Tin']+A['dTf']:.1f} °C（+{A['dTf']:.1f} K）"], "#fbd38d",
         ORANGE)
    c.arrow(620, 328, 580, 328, ORANGE, 2.4)

    # 压降台阶
    c.rect(20, 300, 372, 110, "#f6f9fc", GREY, 1.0, rx=5)
    c.text(30, 320, "板内压降分段（DP-A，实算）", 11.5, INK, cn=True,
           weight="bold")
    items = [("喷嘴孔口 K=1.8", A["dp"]["orifice"] / 1000),
             ("GPU 短槽", A["dp"]["channel"] / 1000),
             ("HBM 槽", A["dp"]["hbm"] / 1000),
             ("静压箱/隔墙（待 CFD）", 4.0)]
    for i, (lab, v) in enumerate(items):
        y = 338 + i * 17
        c.text(30, y, lab, 10, GREY, cn=True)
        c.rect(228, y - 8, v / 6.5 * 120, 10, BLUE if i != 3 else "#cbd5e0",
               "none", 0)
        txt = f"{v:.2f} kPa" if v >= 0.01 else f"{v*1000:.1f} Pa"
        c.text(360, y, txt, 10, INK, "end")
    c.text(30, 406, f"合计 {A['dp']['total'][0]/1000:.1f}–"
                    f"{A['dp']['total'][1]/1000:.1f} kPa，余量到 18 kPa 很大",
           10.5, TEAL, cn=True, weight="bold")
    return c.render()


# ============================================================
# 射流机理
# ============================================================
def fig_jet_mechanism():
    c = Canvas((0, 0, 900, 354), aria="Jet impingement flow regions")
    c.text(20, 28, "图 7-3 · 冲击射流三区与本设计取值窗", 13, INK, cn=True,
           weight="bold")

    # 左：三区
    ox, oy = 40, 60
    c.rect(ox, oy, 330, 30, "#e8b97f", INK, 1.0)
    c.rect(ox + 150, oy, 14, 30, WATER, BLUE, 0.8)
    c.rect(ox, oy + 30, 330, 74, "#eaf6fd", BLUE, 0.8)
    c.rect(ox, oy + 104, 330, 34, CU, INK, 1.0)
    # 射流柱
    c.poly([(ox + 152, oy + 30), (ox + 162, oy + 30),
            (ox + 176, oy + 104), (ox + 138, oy + 104)], "#90cdf4",
           BLUE, 0.8)
    # 势核
    c.poly([(ox + 153, oy + 30), (ox + 161, oy + 30),
            (ox + 163, oy + 76), (ox + 151, oy + 76)], "#2b6cb0",
           "none", 0)
    c.arrow(ox + 157, oy + 34, ox + 157, oy + 99, BLUE, 1.6)
    # 壁面射流
    c.arrow(ox + 150, oy + 110, ox + 40, oy + 110, ORANGE, 1.6)
    c.arrow(ox + 164, oy + 110, ox + 290, oy + 110, ORANGE, 1.6)
    c.circle(ox + 157, oy + 106, 5, RED, "none", 0)

    labels = [("① 自由射流区", oy + 46, "势核未破裂，H/D=4 保证核心到壁"),
              ("② 驻点区", oy + 96, "边界层最薄，h 最高"),
              ("③ 壁面射流区", oy + 126, "沿壁外流，必须尽快抽走")]
    for t, y, s in labels:
        c.text(ox + 350, y, t, 11.5, INK, cn=True, weight="bold")
        c.text(ox + 350, y + 15, s, 9.8, GREY, cn=True)
    c.dim_v(oy + 30, oy + 104, ox + 12, "H=2.0", 10, color=BLUE, ext=5,
            sw=1.0)
    c.text(ox + 157, oy + 22, "D=0.50", 9.5, BLUE, "middle")

    # 右：设计窗
    bx, by = 40, 214
    c.text(bx, by - 8, "无量纲参数取值与文献窗", 11.5, INK, cn=True,
           weight="bold")
    wins = [("H/D", 4.0, 2, 6, 2, 12, "过近势核未展，过远到达速度掉"),
            ("S/D", 6.0, 4, 8, 2, 12, "过密射流互相干扰，过疏覆盖不足"),
            ("Re_D", A["jet"]["Re"], 2000, 100000, 200, 3000,
             "低于 Martin 有效域 2000 —— 关联式外推，必须 CFD 校正")]
    for i, (nm, val, lo, hi, amin, amax, note) in enumerate(wins):
        y = by + 12 + i * 34
        x0, w = 130, 300
        c.text(bx, y + 4, nm, 11, INK, weight="bold")
        c.rect(x0, y - 7, w, 14, "#eef3f8", "#d7e0ec", 0.8, rx=3)
        f = lambda v: x0 + (math.log10(max(v, amin)) - math.log10(amin)) / \
            (math.log10(amax) - math.log10(amin)) * w
        c.rect(f(lo), y - 7, min(f(hi), x0 + w) - f(lo), 14, "#c6f6d5",
               "#276749", 0.8, rx=3)
        ok = lo <= val <= hi
        c.circle(f(val), y, 5.5, RED if not ok else TEAL, "#fff", 1.2)
        c.text(f(val), y - 11, f"{val:.0f}" if val > 100 else f"{val:.1f}",
               9.5, RED if not ok else TEAL, "middle", weight="bold")
        c.text(x0 + w + 14, y + 4, note, 9.8, RED if not ok else GREY, cn=True)
    c.text(bx, by + 128, "绿带 = 文献/关联式有效窗；圆点 = 本设计取值。"
                          "Re_D 落在窗外是本设计最大的不确定来源。", 10.5,
           RED, cn=True, weight="bold")
    return c.render()


# ============================================================
# 沿程温度
# ============================================================
def fig_temp_path():
    c = Canvas((0, 0, 760, 424), aria="Temperature along flow path")
    x0, y0, w, h = 86, 50, 560, 260
    tlo, thi = 35.0, 100.0
    sy = lambda t: y0 + h - (t - tlo) / (thi - tlo) * h
    stations = ["进液", "静压箱", "驻点 A", "驻点 B", "短槽出口", "集液", "出液"]
    sx = lambda i: x0 + i * (w / (len(stations) - 1))

    # 背景包络
    c.rect(x0, sy(90), w, sy(83) - sy(90), "#fed7d7", "none", 0,
           extra='opacity="0.6"')
    c.text(x0 + w - 6, sy(86.5) + 4, "结温包络 83–90 °C", 10, RED, "end",
           cn=True)

    for t in range(40, 101, 10):
        c.line(x0, sy(t), x0 + w, sy(t), "#e4ebf3", 1)
        c.text(x0 - 8, sy(t) + 4, str(t), 10, GREY, "end")
    c.line(x0, y0, x0, y0 + h, INK, 1.4)
    c.line(x0, y0 + h, x0 + w, y0 + h, INK, 1.4)
    c.text(28, y0 + h / 2, "温度 / °C", 11.5, INK, "middle", cn=True,
           extra=f'transform="rotate(-90 28 {y0+h/2})"')
    for i, s in enumerate(stations):
        c.text(sx(i), y0 + h + 20, s, 10.5, INK, "middle", cn=True)

    # Tf：线性升到 48
    Tin = A["Tin"]
    Tout = Tin + A["dTf"]
    tf = [Tin, Tin + 0.3, Tin + 2.2, Tin + 3.6, Tin + 5.6, Tin + 7.0, Tout]
    # Tw 保守/乐观
    Tc_lo, Tc_hi = A["Tc"]
    tw_lo = [Tin + 1, Tin + 2, Tc_lo, Tc_lo - 1.5, Tc_lo - 8, Tin + 8.5,
             Tout + 0.6]
    tw_hi = [Tin + 1.5, Tin + 3, Tc_hi, Tc_hi - 2.0, Tc_hi - 12, Tin + 10,
             Tout + 1.0]
    Tj_lo, Tj_hi = A["Tj"]
    tj_lo = [x + (Tj_lo - Tc_lo) for x in tw_lo]
    tj_hi = [x + (Tj_hi - Tc_hi) for x in tw_hi]

    def plot(vals, col, sw=3.0, dash=None):
        pts = [(sx(i), sy(v)) for i, v in enumerate(vals)]
        c.polyline(pts, col, sw, extra=(f'stroke-dasharray="{dash}"'
                                        if dash else ""))

    # 壳温带
    band = [(sx(i), sy(v)) for i, v in enumerate(tw_hi)] + \
           [(sx(i), sy(v)) for i, v in reversed(list(enumerate(tw_lo)))]
    c.poly(band, "#fbd38d66", "none", 0)
    plot(tf, BLUE, 3.2)
    plot(tw_lo, ORANGE, 2.4)
    plot(tw_hi, ORANGE, 2.4, "7 4")
    plot(tj_lo, RED, 2.0, "5 3")
    plot(tj_hi, RED, 2.0, "2 3")

    c.text(sx(0) + 6, sy(Tin) - 8, f"{Tin:.0f}", 10, BLUE)
    c.text(sx(6) - 6, sy(Tout) - 8, f"{Tout:.1f}", 10, BLUE, "end")
    c.text(sx(2) + 8, sy(Tc_lo) + 4, f"{Tc_lo:.0f}", 10, ORANGE)
    c.text(sx(2) + 8, sy(Tc_hi) - 6, f"{Tc_hi:.0f}", 10, ORANGE)
    c.text(sx(2) + 8, sy(Tj_hi) - 6, f"{Tj_hi:.0f}", 10, RED)

    # 图例
    leg = [(BLUE, "T_f 流体（实算 +7.96 K）", None),
           (ORANGE, "T_w 壳温（带 = 乐观↔保守）", None),
           (RED, "T_j 结温（叠封装内阻）", "5 3")]
    for i, (col, lab, dash) in enumerate(leg):
        y = 360 + i * 20
        c.line(x0, y, x0 + 40, y, col, 3.0,
               f'stroke-dasharray="{dash}"' if dash else "")
        c.text(x0 + 50, y + 4, lab, 10.5, col, cn=True)
    c.text(20, 28, "图 · 沿程三种温度（DP-A 1100 W，水 40 °C 进）", 13, INK,
           cn=True, weight="bold")
    c.text(360, 372, "处处 T_j > T_w > T_f。出液 48 °C 是三条线里最低的，"
                     "不能用它代表芯片温度。", 10.5, GREY, cn=True)
    c.text(360, 392, "保守模型下 T_j 上界 92 °C 已顶到包络上沿 —— "
                     "这就是必须收窄区间的工程理由。", 10.5, RED, cn=True)
    return c.render()


# ============================================================
# 孔径敏感性
# ============================================================
def fig_orifice_chart():
    rows = M.orifice_sweep()
    c = Canvas((-24, 0, 850, 436), aria="Orifice diameter sensitivity")
    x0, y0, w, h = 80, 60, 540, 240
    ds = [r["D"] for r in rows]
    sx = lambda i: x0 + i * (w / (len(rows) - 1))
    dpmax = 9.0
    re_max = max(r["Re"] for r in rows) * 1.15
    syr = lambda v: y0 + h - v / re_max * h
    syd = lambda v: y0 + h - v / dpmax * h

    for i in range(0, 5):
        v = i * re_max / 4
        c.line(x0, syr(v), x0 + w, syr(v), "#e4ebf3", 1)
        c.text(x0 - 8, syr(v) + 4, f"{v:.0f}", 9.5, TEAL, "end")
    c.line(x0, y0, x0, y0 + h, INK, 1.3)
    c.line(x0, y0 + h, x0 + w, y0 + h, INK, 1.3)
    c.line(x0 + w, y0, x0 + w, y0 + h, ORANGE, 1.3)
    for i in range(0, 10, 2):
        c.text(x0 + w + 8, syd(i) + 4, f"{i}", 9.5, ORANGE)

    c.text(34, y0 + h / 2, "Re_D", 11, TEAL, "middle", cn=True,
           extra=f'transform="rotate(-90 34 {y0+h/2})"')
    c.text(x0 + w + 44, y0 + h / 2, "孔口 ΔP  (kPa)", 11, ORANGE, "middle",
           cn=True,
           extra=f'transform="rotate(90 {x0+w+44} {y0+h/2})"')

    re_max = max(r["Re"] for r in rows) * 1.15
    syr = lambda v: y0 + h - v / re_max * h
    c.polyline([(sx(i), syr(r["Re"])) for i, r in enumerate(rows)], TEAL, 3.2)
    c.polyline([(sx(i), syd(r["dP"] / 1000)) for i, r in enumerate(rows)],
               ORANGE, 3.0, extra='stroke-dasharray="7 4"')
    for i, r in enumerate(rows):
        c.circle(sx(i), syr(r["Re"]), 5, TEAL, "#fff", 1.2)
        c.circle(sx(i), syd(r["dP"] / 1000), 4.5, ORANGE, "#fff", 1.2)
        c.text(sx(i), y0 + h + 20, f"{r['D']:.2f}", 10.5, INK, "middle")
        c.text(sx(i), y0 + h + 36, f"Re {r['Re']:.0f}", 9, GREY, "middle")
        c.text(sx(i), syr(r["Re"]) - 11, f"{r['Re']:.0f}", 9.5, TEAL,
               "middle", weight="bold")
        c.text(sx(i), y0 + h + 52, f"ΔP {r['dP']/1000:.2f}", 9, BLUE, "middle")
    c.text(x0 + w / 2, y0 + h + 72,
           f"喷嘴孔径 D (mm) · N={M.N_JET} 固定 · GPU 支路 1.60 L/min · "
           "Martin 不采用", 11, INK, "middle", cn=True, weight="bold")

    # 基线与推荐
    c.line(sx(0), y0 - 6, sx(0), y0 + h, GREY, 1.6,
           'stroke-dasharray="5 4"')
    c.text(sx(0), y0 - 12, "基线 0.50", 10, GREY, "middle", cn=True)
    c.rect(sx(2) - 26, y0 - 4, 52, h + 4, "#f3fbf8", TEAL, 1.4, rx=4,
           extra='stroke-dasharray="6 3"')
    c.text(sx(2), y0 - 12, "优化候选 0.40", 10, TEAL, "middle", cn=True,
           weight="bold")

    c.text(20, 30, "图 · 孔径敏感性：更小的孔换来更高的 h，代价是压降与堵塞风险",
           13, INK, cn=True, weight="bold")
    c.text(20, 402, "读法：D 0.50→0.40 mm 时 Re 与孔口 ΔP 都上升，"
                    "但 Re 仍低于 Martin 1977 的 2000，关联式不采用。", 11, INK,
           cn=True)
    c.text(20, 420, "代价：过滤要求从 50 μm 收紧到 40 μm，堵塞后果更严重。"
                    "0.35/0.30 mm 只作为 DP-B 的储备杠杆。", 11, GREY, cn=True)
    return c.render()


# ============================================================
# 差距闭合
# ============================================================
def fig_gap_chart():
    c = Canvas((-50, 0, 880, 360), aria="Gap closure required h")
    x0, y0, w, h = 120, 70, 560, 190
    hmax = 60000.0
    sy = lambda v: y0 + h - v / hmax * h

    for i in range(7):
        v = i * 10000
        c.line(x0, sy(v), x0 + w, sy(v), "#e4ebf3", 1)
        c.text(x0 - 8, sy(v) + 4, f"{v//1000}k", 9.5, GREY, "end")
    c.line(x0, y0, x0, y0 + h, INK, 1.3)
    c.line(x0, y0 + h, x0 + w, y0 + h, INK, 1.3)
    c.text(40, y0 + h / 2, "等效 h（footprint 基准）\nW/m²K", 10.5, INK,
           "middle", cn=True,
           extra=f'transform="rotate(-90 40 {y0+h/2})"')

    bars = [
        ("短槽模型\n实算", A["con"]["h_eff"], "#b42318"),
        ("DP-A 需要\nTIM2=0.006", M.h_required(0.028, 0.006), "#a65b00"),
        ("DP-A 需要\nTIM2=0.004", M.h_required(0.028, 0.004), "#a65b00"),
        ("DP-B 需要\nTIM2=0.004", M.h_required(0.025, 0.004), RED),
        ("DP-B 需要\nTIM2=0.002", M.h_required(0.025, 0.002), RED),
    ]
    bw = w / len(bars) * 0.52
    for i, (lab, v, col) in enumerate(bars):
        cx = x0 + (i + 0.5) * (w / len(bars))
        c.rect(cx - bw / 2, sy(v), bw, y0 + h - sy(v), col, "#fff", 1.0, rx=2)
        c.text(cx, sy(v) - 8, f"{v/1000:.1f}k", 10.5, col, "middle",
               weight="bold")
        for j, ln in enumerate(lab.split("\n")):
            c.text(cx, y0 + h + 18 + j * 14, ln, 9.8, INK, "middle", cn=True)

    # 保守水平线
    c.line(x0, sy(A["con"]["h_eff"]), x0 + w, sy(A["con"]["h_eff"]),
           "#b42318", 2.0, 'stroke-dasharray="8 4"')
    c.text(x0 + w + 8, sy(A["con"]["h_eff"]) + 4,
           f"保守模型天花板 {A['con']['h_eff']/1000:.1f}k", 10, "#b42318",
           "start", cn=True, weight="bold")

    c.text(20, 32, "图 · 差距闭合：保守模型离达标还差多少", 13, INK, cn=True,
           weight="bold")
    c.text(20, 50, "红线以上的每一根柱子，都是保守模型下打不到的目标。",
           10.5, GREY, cn=True)
    c.text(20, 318, "Martin 1977 因 Re_D < 2000 不采用，图上没有乐观柱。",
           11, INK, cn=True)
    c.text(20, 338, "红柱是为打到目标还需要的等效 h（按 216 个射流胞面积）。"
                    "短槽模型是否够，要由共轭 CFD 回答。", 11, RED, cn=True,
           weight="bold")
    return c.render()


# ============================================================
# 能量分流
# ============================================================
def fig_energy():
    c = Canvas((0, 0, 760, 276), aria="Power split into coolant")
    c.rect(16, 84, 92, 82, INK, INK, 1, rx=5)
    c.text(62, 122, f"{A['P']:.0f}", 20, "#fff", "middle", weight="bold")
    c.text(62, 142, "W · DP-A", 10, "#c5d4e4", "middle", cn=True)

    items = [(f"Die-A {A['p_die']:.0f} W · 39%", "#dd6b20", 20, 30),
             (f"Die-B {A['p_die']:.0f} W · 39%", "#ed8936", 76, 30),
             (f"HBM×8 {A['p_hbm']*8:.0f} W · 18%", "#38a169", 134, 26),
             (f"其它 {A['p_other']:.0f} W · 4%", "#718096", 186, 20)]
    for lab, col, y, hh in items:
        c.path(f"M108 {110+ (y-20)*0.35} C170 {110+(y-20)*0.35}, "
               f"170 {y+hh/2}, 232 {y+hh/2}", "none", col, hh * 0.62)
        c.rect(232, y, 186, hh, col, "#fff", 0.8, rx=3)
        c.text(325, y + hh / 2 + 4, lab, 10.5, "#fff", "middle", cn=True,
               weight="bold")
        c.path(f"M418 {y+hh/2} C500 {y+hh/2}, 500 125, 560 125", "none",
               col, hh * 0.55)
    c.rect(560, 92, 182, 66, BLUE, BLUE, 1, rx=5)
    c.text(651, 120, "全部进入冷却液", 12.5, "#fff", "middle", cn=True,
           weight="bold")
    c.text(651, 140, f"{A['P']:.0f} W → ΔT_f = {A['dTf']:.2f} K", 10.5,
           "#d6eef8", "middle")
    c.text(16, 236, f"校核：{A['p_die']:.0f}+{A['p_die']:.0f}+"
                    f"{A['p_hbm']*8:.0f}+{A['p_other']:.0f} = {A['P']:.0f} W。"
                    "这是功率去向，不是流量去向（流量 80/20）。", 10.5, GREY,
           cn=True)
    c.text(16, 256, "拆分比例为封装假设（置信度中低），待 NVIDIA 官方 "
                    "power map 冻结。", 10.5, RED, cn=True)
    return c.render()


# ============================================================
# CFD 计算域
# ============================================================
def fig_cfd_domain():
    c = Canvas((-62, 0, 962, 420), aria="CFD domain and mesh strategy")
    c.text(20, 30, "图 10-1 · CFD 计算域、分区网格策略与边界条件", 13, INK,
           cn=True, weight="bold")

    # 计算域框
    c.rect(40, 56, 500, 250, "#fbfdff", INK, 1.4, rx=5)
    c.text(290, 76, "共轭计算域（流体 + 固体，1/2 对称可选）", 11.5, INK,
           "middle", cn=True, weight="bold")

    layers = [
        ("进液延长段 ≥10 Dh", 88, 26, "#e7f0fb", BLUE, "抑制入口回流"),
        ("盖板静压箱（流体）", 118, 30, WATER, BLUE, "分流均匀性在此决定"),
        ("喷嘴孔 ⌀0.50（流体）", 152, 26, "#90cdf4", BLUE,
         "径向 ≥12 层，孔长 ≥8 层"),
        ("射流间隙 H=2.0（流体）", 182, 26, "#bee3f8", BLUE,
         "驻点首层 y⁺<1"),
        ("短槽 + 肋（流体+固体耦合）", 212, 30, "#c6f6d5", TEAL,
         "壁面法向 ≥10 层"),
        ("余铜 2.0 + TIM2 + 盖板（固体）", 246, 30, CU, "#b97a45",
         "热源以面热流/体热源加载"),
        ("出液汇流 + 延长段", 280, 22, "#fbd38d", ORANGE, ""),
    ]
    for lab, y, hh, fill, col, note in layers:
        c.rect(58, y, 300, hh, fill, col, 1.1, rx=3)
        c.text(208, y + hh / 2 + 4, lab, 10, INK, "middle", cn=True)
        c.text(372, y + hh / 2 + 4, note, 9.3, GREY, cn=True)

    # 边界条件
    c.arrow(-54, 101, 56, 101, BLUE, 2.4)
    c.text(-54, 94, "质量流入口", 9.5, BLUE, cn=True)
    c.arrow(358, 291, 398, 291, ORANGE, 2.4)
    c.text(404, 295, "压力出口 0 Pa（表压）", 9.5, ORANGE, cn=True)

    # 右侧：网格与模型
    bx = 570
    c.rect(bx, 56, 310, 250, "#f6f9fc", GREY, 1.2, rx=5)
    c.text(bx + 155, 76, "网格与物理模型要求", 11.5, INK, "middle", cn=True,
           weight="bold")
    reqs = [
        ("网格量级", "3 000–8 000 万（全模）"),
        ("驻点首层", "Δy ≤ 3 μm，y⁺ < 1"),
        ("无关性判据", "加密 1.5× 后 R 与 ΔP 变化 < 3%"),
        ("流态", f"Re_D≈{A['jet']['Re']:.0f} 属层流–过渡"),
        ("湍流模型", "转捩 SST 或 k-ω SST（低 Re 修正）"),
        ("层流对照", "必须同时跑层流算例做包络"),
        ("共轭", "固体 Cu 390 W/mK，必须共轭"),
        ("收敛", "残差 <1e-4 且 R/ΔP 连续 500 步漂移 <0.5%"),
    ]
    for i, (k, v) in enumerate(reqs):
        y = 98 + i * 26
        c.text(bx + 14, y, k, 10, INK, cn=True, weight="bold")
        c.text(bx + 104, y, v, 9.8, GREY, cn=True)

    # 下方：工况矩阵
    c.rect(40, 326, 840, 76, "#fff9e9", "#a65b00", 1.2, rx=5)
    c.text(54, 346, "最小工况矩阵（12 个算例）", 11.5, "#a65b00", cn=True,
           weight="bold")
    cases = ["功率 1100 / 1400 W", "流量 1.6 / 2.0 / 2.4 L/min",
             "工质 水 / PG25", "进液 40 °C（基线）+ 45 °C（最恶）",
             "均匀热流 vs 双 die 热点 ×2.5", "含/不含 HBM 支路堵塞 20%"]
    for i, cs in enumerate(cases):
        c.rect(54 + (i % 3) * 276, 356 + (i // 3) * 22, 266, 18, "#fff",
               "#a65b00", 0.7, rx=3)
        c.text(187 + (i % 3) * 276, 369 + (i // 3) * 22, cs, 9.6, INK,
               "middle", cn=True)
    return c.render()
