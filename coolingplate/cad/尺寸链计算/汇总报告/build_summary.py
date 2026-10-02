# -*- coding: utf-8 -*-
"""冷板总体设计报告：按门控 ①–⑦ 写 HTML，并给出可复算的 Excel。"""
from __future__ import annotations

import html
import math
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

OUT = Path(__file__).resolve().parent
DATE = "2026-09-29"

RHO, CP, MU, KF, KCU = 992.2, 4179.0, 6.53e-4, 0.631, 390.0
RHO_G, KF_G = 992.0, 0.632


def E(text) -> str:
    return html.escape(str(text), quote=True)


def jet(Q_lpm, D_mm, N, K=1.8):
    A = N * math.pi * (D_mm * 1e-3) ** 2 / 4.0
    V = (Q_lpm / 60000.0) / A
    Re = RHO * V * (D_mm * 1e-3) / MU
    dP = K * RHO * V * V / 2.0
    return V, Re, dP


def duct(Q_lpm, n, w_mm, h_mm, L_mm, K=0.0):
    q = Q_lpm / 60000.0
    w, h, L = w_mm * 1e-3, h_mm * 1e-3, L_mm * 1e-3
    Dh = 2 * w * h / (w + h)
    V = q / (n * w * h)
    Re = RHO * V * Dh / MU
    f = 64.0 / Re if Re else 0.0
    dP = (f * (L / Dh) + K) * RHO * V * V / 2.0
    return V, Re, Dh * 1e3, dP


def grace_branch(Q, power, P, n, w_mm, h_mm, Lf, Lh, K=3.0):
    q = Q * (power / P) / 60000.0
    w, h = w_mm * 1e-3, h_mm * 1e-3
    Dh = 2 * w * h / (w + h)
    V = q / (n * w * h)
    Re = RHO_G * V * Dh / MU
    f = 64.0 / Re
    dP = (f * (Lf * 1e-3 / Dh) + K) * RHO_G * V * V / 2.0
    Nu = 4.8
    hh = Nu * KF_G / Dh
    Awet = n * (Lh * 1e-3) * (w + 2 * h)
    R = 1.0 / (hh * Awet)
    return dict(Q=Q * power / P, V=V, Re=Re, Dh=Dh * 1e3, dP=dP, h=hh, R=R, dT=power * R)


# --- 冻结数 ---------------------------------------------------------------
P_A, Q_A, P_B, Q_B = 1100.0, 2.0, 1400.0, 2.4
Q_GPU, Q_HBM = 1.6, 0.4
N_JET = 216
V50, RE50, DP50 = jet(Q_GPU, 0.50, N_JET)
V40, RE40, DP40 = jet(Q_GPU, 0.40, N_JET)
A2 = 2 * 27.0 * 28.0 * 1e-6
R_WALL = 0.002 / (KCU * A2)
R_CONV = 0.025239009895857565
R_LO = R_WALL + 0.004 + R_CONV
R_HI = R_WALL + 0.008 + R_CONV
MDOT_A = RHO * Q_A / 60000.0
DTF_A = P_A / (MDOT_A * CP)
V_HBM_OLD, RE_HBM_OLD, _, DP_HBM_OLD = duct(Q_HBM, 16, 0.60, 1.50, 50.0)
V_HBM_NEW, RE_HBM_NEW, DH_NEW, DP_HBM_NEW = duct(0.20, 7, 0.80, 2.00, 50.0)
Q_E = 300.0 / (RHO_G * CP * 8.0) * 60000.0
G_CPU = grace_branch(0.55, 260, 300, 48, 0.40, 1.20, 40, 32)
G_MEM = grace_branch(0.55, 20, 300, 6, 1.20, 0.80, 78, 70)
G_CPU_E = grace_branch(Q_E, 260, 300, 48, 0.40, 1.20, 40, 32)
# CFD
T_IN, T_TIM12, P_DIE = 313.15, 342.04911, 900.899
R_CFD = (T_TIM12 - T_IN) / P_DIE
DP_CFD = 1099.99
T_HBM, P_HBM = 333.48854, 99.22
R_HBM = (T_HBM - T_IN) / P_HBM
# 权衡
WTS = (0.25, 0.20, 0.15, 0.20, 0.10, 0.10)
SCORES = {
    "铲齿微通道": (3, 3, 2, 5, 5, 1),
    "纯射流": (5, 1, 3, 3, 2, 2),
    "增材拓扑": (4, 3, 4, 1, 2, 3),
    "分区杂交": (5, 5, 4, 4, 3, 5),
}
PUB = {"铲齿微通道": 3.20, "纯射流": 2.95, "增材拓扑": 2.85, "分区杂交": 4.50}


def weighted(scores):
    return sum(w * s for w, s in zip(WTS, scores))


def checks():
    assert abs(DTF_A - 7.9587) < 1e-3
    assert abs(V50 - 0.62876) < 1e-4
    assert abs(DP50 - 353.03) < 0.1
    assert abs(R_LO - 0.032631) < 1e-5
    assert abs(R_HI - 0.036631) < 1e-5
    assert abs(V_HBM_OLD - 0.46296) < 1e-4
    assert abs(V_HBM_NEW - 0.29762) < 1e-4
    assert abs(R_CFD - 0.03208) < 2e-5
    assert abs(5 + 11 + 0.5 + 2 + 0.5 + 27 + 3 + 27 + 0.5 + 2 + 0.5 + 11 + 5 - 95) < 1e-9
    assert abs(6 * (50 / 6) - 50) < 1e-9
    assert abs(6 * 8.0 - 48) < 1e-9
    sig = 300e3 * (0.0264 ** 2) / (2 * 0.0025 ** 2)
    assert abs(sig / 1e6 - 16.727) < 0.01


CSS = """
:root { --ink:#1c2430; --muted:#5c6b7a; --line:#d5dde6; --navy:#0e3a5d; --ok:#0d6b3a; --bad:#9d1c1c; --wait:#8a5a00; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:#f6f4ef; font:16px/1.65 "Microsoft YaHei","PingFang SC",sans-serif; }
main { max-width:1040px; margin:0 auto; padding:28px 26px 72px; background:#fff; }
h1 { font-size:28px; line-height:1.3; margin:0 0 8px; color:var(--navy); }
h2 { font-size:20px; margin:34px 0 10px; padding-top:10px; border-top:2px solid var(--navy); color:var(--navy); }
h3 { font-size:17px; margin:18px 0 8px; }
.sub { color:var(--muted); }
.meta { display:flex; flex-wrap:wrap; gap:8px 16px; font-size:13px; color:var(--muted); }
.lead { background:#f3f7fb; border-left:4px solid var(--navy); padding:12px 14px; }
nav a { color:var(--navy); margin-right:12px; }
table { width:100%; border-collapse:collapse; margin:10px 0 16px; font-size:14px; }
th, td { border:1px solid var(--line); padding:6px 8px; vertical-align:top; text-align:left; }
th { background:#eef3f8; }
.ok { color:var(--ok); font-weight:700; }
.bad { color:var(--bad); font-weight:700; }
.wait { color:var(--wait); font-weight:700; }
.figcap { font-size:13px; color:var(--muted); }
footer { margin-top:28px; font-size:13px; color:var(--muted); }
"""


def table(headers, rows):
    th = "".join(f"<th>{h}</th>" for h in headers)
    body = []
    for row in rows:
        tds = []
        for cell in row:
            text = str(cell)
            if text in ("完成", "通过", "闭合"):
                text = f'<span class="ok">{text}</span>'
            elif text in ("未通过", "未开始", "不闭合", "不判定"):
                text = f'<span class="bad">{text}</span>'
            elif text.startswith("有条件") or text.startswith("部分") or text == "待确认":
                text = f'<span class="wait">{E(text)}</span>'
            elif not text.startswith("<"):
                text = E(text)
            tds.append(f"<td>{text}</td>")
        body.append("<tr>" + "".join(tds) + "</tr>")
    return "<table><thead><tr>" + th + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def fig_process():
    labels = [
        ("①", "需求与输入", "DR0", "#1d6b45"),
        ("②", "概念与选型", "DR1", "#1d6b45"),
        ("③", "性能设计", "DR2", "#8a5a00"),
        ("④", "一维计算", "DR2", "#8a5a00"),
        ("⑤", "三维仿真", "DR3", "#9d1c1c"),
        ("⑥", "机械与图纸", "DR3", "#8a5a00"),
        ("⑦", "样件与试验", "DR4", "#8aa0b4"),
    ]
    parts = []
    x0, y, w, h, gap = 8, 28, 112, 82, 18
    for i, (n, name, gate, color) in enumerate(labels):
        x = x0 + i * (w + gap)
        parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" stroke="{color}" stroke-width="2"/>'
        )
        parts.append(
            f'<text x="{x+w/2}" y="{y+24}" text-anchor="middle" font-size="16" fill="{color}" '
            f'font-family="Microsoft YaHei">{n}</text>'
        )
        parts.append(
            f'<text x="{x+w/2}" y="{y+46}" text-anchor="middle" font-size="13" fill="#1c2430" '
            f'font-family="Microsoft YaHei">{name}</text>'
        )
        parts.append(
            f'<text x="{x+w/2}" y="{y+66}" text-anchor="middle" font-size="12" fill="{color}" '
            f'font-family="Microsoft YaHei">{gate}</text>'
        )
        if i < 6:
            x2 = x + w
            parts.append(
                f'<path d="M{x2} {y+h/2} H{x2+gap-2}" stroke="#0e3a5d" marker-end="url(#ar)"/>'
            )
    x_sim = x0 + 4 * (w + gap) + w / 2
    x_perf = x0 + 2 * (w + gap) + w / 2
    parts.append(
        f'<path d="M{x_sim:.0f} 112 C{x_sim:.0f} 168, {x_perf:.0f} 168, {x_perf:.0f} 112" '
        'fill="none" stroke="#9d1c1c" stroke-width="1.6" marker-end="url(#ar2)"/>'
    )
    parts.append(
        f'<text x="{(x_sim+x_perf)/2:.0f}" y="188" text-anchor="middle" font-size="13" fill="#9d1c1c" '
        'font-family="Microsoft YaHei">仿真不达标 → 回 ③/④ 改孔径、阵列密度、TIM2</text>'
    )
    svg = (
        '<svg viewBox="0 0 980 200" width="980" xmlns="http://www.w3.org/2000/svg">'
        '<defs><marker id="ar" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L6,3 L0,6 Z" fill="#0e3a5d"/></marker>'
        '<marker id="ar2" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">'
        '<path d="M0,0 L6,3 L0,6 Z" fill="#9d1c1c"/></marker></defs>'
        + "".join(parts) + "</svg>"
    )
    return (
        '<div>' + svg + '</div><p class="figcap">图 1 · 七道门。绿是已经选定，黄是有条件通过或只完成了一部分，'
        '红是还不能放行，灰是还没开始。红线是仿真回路，回到性能设计和一维计算。</p>'
    )


def build_html():
    score_rows = []
    for name, sc in SCORES.items():
        score_rows.append([name, *(str(v) for v in sc), f"{weighted(sc):.2f}", f"{PUB[name]:.2f}"])
    body = f"""
<p class="lead">几何和分区可以往下做。GPU 壳–进液热阻还没有压进 0.028 °C/W：一维上界是 {R_HI:.4f} °C/W，12 孔共轭场按两 die 900.9 W 折算是 {R_CFD:.5f} °C/W，而且这场已经含 TIM 和铜。样件试验没开始。DR3 不放行，DR4 不启动。</p>
<div class="meta"><span>CP-TRAY-DR-01</span><span>{DATE}</span><span>覆盖 GPU 射流冷板、HBM 微通道冷板、Grace CPU 冷板、LLDDRAM（LPDDR5X）冷板</span></div>
<nav>
<a href="#s0">流程</a><a href="#s1">① 需求</a><a href="#s2">② 选型</a><a href="#s3">③ 性能</a>
<a href="#s4">④ 一维</a><a href="#s5">⑤ 仿真</a><a href="#s6">⑥ 图纸</a><a href="#s7">⑦ 试验</a><a href="#s8">结论</a>
</nav>

<h2 id="s0">0　流程和本版走到哪</h2>
<p>B300 设计报告 v2.0 的流程封面写的是：报告覆盖 ①–⑥，⑤ 的工具尚未选定，⑦ 未开始。那是 2026-09-14 的覆盖声明。到本汇总为止，ICEM 和 Fluent 已经用来算过 GPU 的 12 孔带和 HBM 的单列，四块冷板的名义尺寸链也重加过。工具选定了，放行条件没有满足。</p>
{fig_process()}
{table(["门", "阶段", "放行要看到什么", "本版"], [
    ["DR0", "① 需求与输入", "缺失项有责任人，不再靠口头假设往下画", "有条件完成"],
    ["DR1", "② 概念与选型", "权衡有权重，方案只留一个", "完成"],
    ["DR2", "③ 性能设计 + ④ 一维计算", "热阻预算和一维式子能复算", "有条件通过"],
    ["DR3", "⑤ 三维仿真", "网格无关，热阻和压降进目标，分区流量偏差在 ±10% 内", "未通过"],
    ["DR3", "⑥ 机械与图纸", "名义尺寸链闭合，承压过得去，图号能投产", "部分完成"],
    ["DR4", "⑦ 样件与试验", "TTV 热阻、流阻曲线、氦检", "未开始"],
])}
<p>两条回路都还开着。仿真回路：热阻超目标、板内压降超过 20 kPa，或 GPU/HBM 流量偏差超过 ±10%，就回到 ③ 和 ④，先动孔径、TIM2、阵列密度。验证回路要等样件：TTV 和 CFD 相差超过 15%，再回来改关联式，现在没有实测，这条回路还没触发。</p>

<h2 id="s1">①　需求与输入</h2>
<p>一块计算托盘两块 GB300 NVL2。液冷位是 4 颗 B300 加 2 颗 Grace。B300 用分区射流冷板，Grace 用另一块铜，盖住 CPU 和两侧板载 LPDDR5X。风冷位不进液冷回路。四块 GPU 冷板和两块 Grace 冷板在托盘歧管上按并联取水：4×2.0 + 2×0.55 = 9.1 L/min，热负荷约 5000 W，温升大约 8 K。Grace 入口另加孔板，避免把 GPU 的流量吸走。</p>
{table(["对象", "保证点", "包络", "冷板外形", "流量"], [
    ["B300 GPU + HBM，一块冷板", "1100 W，Lenovo TGP", "1400 W，只做包络", "95 × 75 × 8.5 mm", "2.0 / 2.4 L/min"],
    ["其中 GPU 两 die", "858 W", "随 1400 W 放大", "两颗 27 × 28 mm", "1.60 L/min（80%）"],
    ["其中 HBM 八颗", "198 W", "同上", "两列，每列 11 × 50 mm", "0.40 L/min（20%）"],
    ["Grace，含内存", "300 W", "流量可到 0.70 L/min", "200 × 120 × 8.0 mm", "0.55 L/min"],
    ["Grace CPU 窗", "260 W", "—", "40 × 32 mm", "按功率分"],
    ["LLDDRAM，两侧合计", "40 W", "—", "每侧 50 × 70 mm", "每侧约 0.037 L/min"],
])}
<p>还没有冻结的输入：官方盖板图和螺孔、官方功率图、托盘单板额定流量、TIM2 的实测面积热阻、冷却液最终是水还是 PG25。这些缺项不阻止候选几何，但阻止把热阻写成保证值。封装坐标、die 尺寸 27×28、HBM 八颗、热点系数，在算到出图之前都还是假设。</p>
<p>工作簿 <code>01_DR0_输入追溯.xlsx</code> 把每一项标成已有、假设或缺失。</p>

<h2 id="s2">②　概念与选型</h2>
<p>B300 一块板上热流差一个量级，所以分成两区：GPU 用射流加短槽，HBM 不打喷嘴，中间用隔离肋把两区的水切开。Grace 整板只有 300 W，CPU 窗大约 20 W/cm²，不再做微射流，用沿 Y 的交错槽。LLDDRAM 是这块 Grace 板上的两侧宽槽，不是第三块铜。</p>
{table(["维度", "权重", "铲齿微通道", "纯射流", "增材拓扑", "分区杂交"], [
    ["双 die 热点", "25%", "3", "5", "4", "5"],
    ["HBM 冲蚀和偏载", "20%", "3", "1", "3", "5"],
    ["压降", "15%", "2", "3", "4", "4"],
    ["可制造与交期", "20%", "5", "3", "1", "4"],
    ["防堵", "10%", "5", "2", "2", "3"],
    ["专利占位", "10%", "1", "2", "3", "5"],
] + [["加权", "100%"] + [f"{weighted(SCORES[k]):.2f}" for k in SCORES]])}
<p>按上表分数重算，分区杂交 {weighted(SCORES['分区杂交']):.2f}，高于铲齿 {weighted(SCORES['铲齿微通道']):.2f}、纯射流 {weighted(SCORES['纯射流']):.2f}、增材 {weighted(SCORES['增材拓扑']):.2f}。v2.0 印出的加权分分别是 4.50、3.20、2.95、2.85，和逐项相乘差 0.05，名次不变。工作簿用公式重乘，以公式为准。</p>
<p>工艺基线是机加加真空钎焊，整板金属增材不作出货件。专利上要保住的特征是：HBM 无喷嘴、近壁流速上限、隔离肋同时切水流和传压装载荷、额定流量下的压降窗。只写“分区用射流和微通道”覆盖不住这些特征。</p>
<p>工作簿 <code>02_DR1_方案权衡.xlsx</code>。</p>

<h2 id="s3">③　性能设计</h2>
<p>冷板只对壳到进液负责。GPU 的目标是 DP-A 小于 0.028 °C/W，门槛 0.032，包络 DP-B 小于 0.025，包络不作出厂保证。板内压降目标 ≤ 18 kPa，上限 20 kPa。HBM 近壁流速帽 0.80 m/s。Grace CPU 区的目标是壳–进液小于 0.080 °C/W。两 die 中心温差目标 ≤ 5 K。</p>
{table(["GPU 壳–进液的一段", "DP-A / °C/W", "谁能改"], [
    ["封装，硅 + TIM1 + 盖", "0.008–0.012，在壳温之上", "冷板改不了"],
    ["TIM2", "0.004–0.008", "选材"],
    ["余铜 2.0 mm 导热", f"{R_WALL:.4f}", "减薄会动刚度"],
    ["对流，短槽模型", f"{R_CONV:.4f}", "孔径、阵列、流量"],
    ["合计", f"{R_LO:.4f} – {R_HI:.4f}", "目标 0.028，上界过线"],
])}
<p>80/20 的分流是按热流，不是按面积。HBM 只有 18% 的功率，多送水主要是加冲蚀。分配靠盖板上的开孔和隔墙，不用外置阀门。</p>
<p>射流窗按孔径两个口径都落在 S/D = 4–8、H/D = 2–6 里。D = 0.50 mm 时 Sx/D = 6.0、Sy/D = 4.8、H/D = 4.0。UC01b 把孔径收到 0.40 mm 后，Sx/D = 7.5、Sy/D = 6.0、H/D = 5.0。孔数仍是 216。Martin 关联式要求 Re 大于 2000，两个口径的 Re 都在 600 上下，所以性能章不引用 Martin。</p>
<p>Grace 支路目标压降 10 kPa，和 GPU 冷板同一档，这样并联时不会互抢。通道本身大约 1 kPa，差额由入口 4 个小孔承担。</p>

<h2 id="s4">④　一维计算</h2>
<p>水按 40 °C，密度 {RHO} kg/m³，比热 {CP:.0f} J/kg·K。混合温升只由总功率和总流量决定。DP-A：1100 W、2.0 L/min，温升 {DTF_A:.2f} K。Grace 按 300 W、8 K 反算流量是 {Q_E:.3f} L/min，设计把流量收到 0.55 L/min。</p>
<h3>GPU 射流</h3>
{table(["量", "D = 0.50 mm，报告正文", "D = 0.40 mm，UC01b"], [
    ["孔数 × GPU 流量", "216 × 1.60 L/min", "同左"],
    ["孔速", f"{V50:.3f} m/s", f"{V40:.3f} m/s"],
    ["Re_D", f"{RE50:.0f}", f"{RE40:.0f}"],
    ["孔口压降，K = 1.8", f"{DP50/1000:.3f} kPa", f"{DP40/1000:.3f} kPa"],
    ["壳–进液", f"{R_LO:.4f}–{R_HI:.4f} °C/W", "一维式子仍用短槽，不随孔径自动改换热"],
])}
<p>短槽在“就近抽走”的拓扑里流速只有约 0.034 m/s，压降可以忽略。它的作用是把润湿面积放大，不是当一根长导管。板内压降一维合计约 3.5–5.5 kPa，离 20 kPa 很远。热阻上界已经过目标，所以下一轮该用压降去换换热，而不是再把压降压低。</p>
<h3>HBM</h3>
<p>一维里有两套截面，不要加在一起。</p>
{table(["量", "v2.0 表：16 条 0.60×1.50，0.40 L/min", "w08h20：单侧 7 条 0.80×2.00，0.20 L/min"], [
    ["槽速", f"{V_HBM_OLD:.3f} m/s", f"{V_HBM_NEW:.3f} m/s"],
    ["Re", f"{RE_HBM_OLD:.0f}", f"{RE_HBM_NEW:.0f}"],
    ["50 mm 直槽摩擦压降", f"{DP_HBM_OLD:.0f} Pa", f"{DP_HBM_NEW:.0f} Pa"],
    ["相对 0.80 m/s 帽", "低于帽", "低于帽"],
])}
<h3>Grace CPU 与 LLDDRAM</h3>
<p>下表按设计流量 0.55 L/min、Nu = 4.8、每个 Z 向弯头 K = 1.5（一进一出合计 3）。报告正文里的 0.34 m/s 和 0.96 kPa 对应能量平衡流量 {Q_E:.3f} L/min 下的 CPU 通道（重算 {G_CPU_E['V']:.3f} m/s、{G_CPU_E['dP']/1000:.2f} kPa），不是 0.55 L/min 这一列。</p>
{table(["量", "CPU，260 W，48 条 0.40×1.20", "单侧内存，20 W，6 条 1.20×0.80"], [
    ["分配流量", f"{G_CPU['Q']:.3f} L/min", f"{G_MEM['Q']:.3f} L/min"],
    ["流速", f"{G_CPU['V']:.3f} m/s", f"{G_MEM['V']:.3f} m/s"],
    ["Re", f"{G_CPU['Re']:.0f}", f"{G_MEM['Re']:.0f}"],
    ["通道压降", f"{G_CPU['dP']/1000:.2f} kPa", f"{G_MEM['dP']/1000:.2f} kPa"],
    ["对流热阻", f"{G_CPU['R']:.3f} °C/W", f"{G_MEM['R']:.3f} °C/W"],
    ["对流温升", f"{G_CPU['dT']:.1f} K", f"{G_MEM['dT']:.1f} K"],
])}
<p>CPU 对流热阻 {G_CPU['R']:.3f} °C/W，低于 0.080 的目标，剩下的额度留给 TIM2。这是筛算。内存对流不是驱动项。内存缝 0.80×1.20 mm、长 12 mm，用来把内存支路的压降补到和 CPU 同一量级，平面坐标还没给。</p>
<p>工作簿 <code>03_DR2_一维性能核算.xlsx</code>。蓝字是流量、孔径、槽截面；孔速、雷诺数、温升、热阻合计和加权都是公式。</p>

<h2 id="s5">⑤　三维仿真</h2>
<p>v2.0 停在“要做共轭 CFD”。现在有两场局部结果，都不是整板，也都还不能关 DR3。</p>
{table(["场", "几何", "结果", "能不能当整板结论"], [
    ["GPU，12 孔带，iter 600", "D=0.40 mm，节距 3.0×2.4，沿 Y 12 格，28,005,504 六面体",
     f"TIM 底 {T_TIM12:.3f} K；入口静压平均 {DP_CFD:.0f} Pa；R(T_TIM−T_in) = {R_CFD:.5f} °C/W，除数是 900.899 W",
     "不能。热流是边界冗余后的胞热流，不是 1100 W 整板。总压差、GCI、y+ 没有导出。出口约 2.3% 面积回流"],
    ["HBM，单侧 7 槽，iter 200", "0.80×2.00 mm，列宽 11 mm，4,677,600 六面体",
     f"TIM 底 {T_HBM:.3f} K；R = {R_HBM:.3f} °C/W，除数是这一侧 99.22 W；进口静压 409 Pa",
     "不能。连续性残差 2.6×10⁻⁴，未到 10⁻⁴。这个热阻不能和 0.028 的封装目标比"],
    ["Grace CPU / LLDDRAM", "网格方案已写", "没有 Fluent 求解场", "不能"],
])}
<p>12 孔带若再把设计假设里的 TIM2 和封装热阻叠回去，会和已经含在 TIM 底温度里的导热重复计算。报告里的 0.0226–0.0266 °C/W 只是对照行。和 0.028 的目标比，应该用场自己的 {R_CFD:.5f} °C/W，并且记住分母是 900.9 W 不是 1100 W。</p>
<p>HBM 一维 50 mm 直槽摩擦约 {DP_HBM_NEW:.0f} Pa，CFD 进口静压 409 Pa。多出来的是发展段和进出口，不是把 61 Pa 改写成 409 Pa。槽速 {V_HBM_NEW:.3f} m/s，没有碰到 0.80 m/s。</p>
<p>因此仿真回路保持打开：下一轮仍是孔径、阵列密度和 TIM2。在 GCI 和整板场出来之前，不增加阵列密度的加工承诺。</p>
<p>工作簿 <code>04_DR3_仿真图纸与试验门.xlsx</code> 的「仿真」页用温度和功率重算热阻。</p>

<h2 id="s6">⑥　机械与图纸</h2>
<p>四块冷板的名义尺寸链已经单独成报告，放在本目录的上一级。这里只收放行时要看的闭合结果，和还没合成一块铜的地方。</p>
{table(["链", "算式", "结果", "判定"], [
    ["GPU 板宽", "5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5", "95 mm", "闭合"],
    ["GPU 板长", "12.5+50+12.5", "75 mm", "闭合"],
    ["GPU 外形厚", "2+1.5+2+2.5+0.5", "8.5 mm", "闭合"],
    ["GPU 射流覆盖 X", "9×3.0", "27 mm，等于 die 宽", "闭合"],
    ["GPU 射流覆盖 Y", "12×2.4", "28.8 mm，比 die 高 0.8 mm", "闭合"],
    ["HBM 列宽，采用", "0.30+7×0.80+6×0.80+0.30", "11 mm", "闭合"],
    ["HBM 列宽，对照", "0.65+8×0.60+7×0.70", "11 mm", "闭合，不采用"],
    ["HBM 铜厚", "2+2+4", "8.0 mm", "闭合，但与 GPU 的 8.5 不是同一条厚度栈"],
    ["Grace 板宽 / 板厚", "分区相加；2+1.2+0.3+2.5+2", "200 mm；8.0 mm", "闭合"],
    ["CPU 肋场", "49×0.40+48×0.40", "38.8 mm，窗内两岸各 0.6", "闭合"],
    ["CPU / 内存口带", "补上两段各 1.2 mm 实铜之后", "跨度 44 mm / 82 mm，再加边距等于 120", "闭合"],
    ["LLDDRAM 节距 8.333 mm", "6×(50/6)", "50 mm", "闭合"],
    ["LLDDRAM 节距 8.00 mm", "同样半肋岸结构", "48 mm", "不闭合"],
])}
<p>口带表原来从 42.8 跳到 44、从 76 跳到 77.2（内存是 23.8 到 25、95 到 96.2）。这两段 1.2 mm 是实铜，补进链之后才闭合。8.00 mm 的内存节距不能铺满 50 mm 窗口，出图用 8.333 mm。</p>
<p>承压按 3 bar、两端固支板条估算。余铜跨 0.8 mm 槽，弯曲应力远小于 1 MPa。盖板若按无支撑跨过 26.4 mm 射流中心距、板厚 2.5 mm，弯曲应力约 16.7 MPa，退火铜屈服取 70 MPa，比值约 4.2。这是保守的无肋板条，不是开了短槽之后的真实盖板。</p>
<p>孔径 0.40 与 0.50 不影响孔位链，但影响钻头、过滤和压降。过滤仍按最小孔径的 1/10，0.40 mm 对应 40 μm，系统侧目前按 25 μm 写，细于这个判据。生产二维图、爆炸图和公差还没有冻结，所以 DR3 的图纸半边只算部分完成。</p>
<p>细部见上一级目录里的四份尺寸链报告和四份尺寸核实2工作簿。本目录工作簿的「尺寸链」页复算了板宽、列宽、板厚和两种节距。</p>

<h2 id="s7">⑦　样件与试验</h2>
<p>这一章还没有数据。放行要同时看到三件事：TTV 上的壳–进液热阻进 DP-A 目标，流阻曲线在设计流量下不超过 18 kPa，氦检通过。Grace 支路单独看 10 kPa 这一档。红外用来看两 die 温差和 HBM 是否比 GPU 驻点更热。试验大纲上的判据已经写进工作簿「试验门」，格子空着，等有数再填。</p>
{table(["试验", "对象", "判据", "状态"], [
    ["TTV 热阻", "GPU 冷板，1100 W，2.0 L/min，40 °C", "Rθ,c-in < 0.028 °C/W", "未开始"],
    ["流阻曲线", "GPU 冷板", "≤ 18 kPa，极限 20", "未开始"],
    ["分区流量", "GPU : HBM", "80:20，偏差 ±10%", "未开始"],
    ["支路压降", "Grace，0.55 L/min", "约 10 kPa，窗口 8–12", "未开始"],
    ["氦检", "两块冷板", "按钎焊件的漏率", "未开始"],
    ["红外", "双 die 与 HBM", "两 die 温差 ≤ 5 K", "未开始"],
])}
<p>TTV 和 CFD 相差超过 15% 时，走验证回路，回到 ③ 和 ④ 改关联式，不直接改图。</p>

<h2 id="s8">结论</h2>
{table(["#", "结论", "门"], [
    ["1", "方案选定：B300 分区杂交，Grace 交错宽槽，LLDDRAM 附在 Grace 板上。", "DR1 完成"],
    ["2", "水力余量大，GPU 热阻上界过 0.028 °C/W。优化方向是用压降换换热。", "DR2 有条件通过"],
    ["3", "局部 CFD 已经跑起来，整板热阻、网格无关和 Grace 求解都还没有。", "DR3 未通过"],
    ["4", "名义尺寸链闭合。HBM 的 8.0 mm 铜厚和 GPU 的 8.5 mm 外形还没合成一条厚度栈；内存节距用 8.333 mm。", "图纸部分完成"],
    ["5", "没有样件数据，不能送样。", "DR4 未开始"],
])}
<p>下一步按回路，不按新开课题：先把 GPU 孔径在 0.40 与 0.50 里定一个，并选 TIM2 档；HBM 只保留 0.80 mm 七槽；补一次整板或至少含歧管的共轭场，并做网格无关；尺寸上先定 GPU 与 HBM 的共用 z。这些数出来之前，不写采购保证。</p>
<footer>
数值来自 B300 设计报告 v2.0 的计算模块、UC01b 12 孔 iter 600、HBM w08h20 iter 200、Grace 冷板报告，以及上一级目录的尺寸链核实。
一维和权衡以本目录 Excel 的公式为准。本文件不是订单 ICD，也不是出厂保证。
</footer>
"""
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"/>
<title>冷板总体设计报告</title><style>{CSS}</style></head>
<body><main>
<h1>GB300 计算托盘冷板<br>总体设计报告</h1>
<p class="sub">按门控流程 ① 到 ⑦。GPU 射流冲击微通道冷板、HBM 微通道冷板、Grace CPU 冷板、LLDDRAM 冷板。</p>
{body}
</main></body></html>
"""


# --- Excel ----------------------------------------------------------------
THIN = Border(
    left=Side(style="thin", color="D5DDE6"), right=Side(style="thin", color="D5DDE6"),
    top=Side(style="thin", color="D5DDE6"), bottom=Side(style="thin", color="D5DDE6"),
)
FILL_IN = PatternFill("solid", fgColor="D6E6F5")
FILL_HD = PatternFill("solid", fgColor="0E3A5D")
FILL_SUM = PatternFill("solid", fgColor="EEF3F8")
FONT_HD = Font(name="微软雅黑", color="FFFFFF", bold=True, size=11)
FONT = Font(name="微软雅黑", size=11)
FONT_B = Font(name="微软雅黑", size=11, bold=True)
FONT_IN = Font(name="微软雅黑", size=11, color="0B3A66")


def prep(ws, title, headers, widths, landscape=True):
    ws.sheet_view.showGridLines = False
    ws.page_setup.orientation = "landscape" if landscape else "portrait"
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.page_setup.horizontalCentered = True
    ws.page_margins.left = 0.5
    ws.page_margins.right = 0.5
    ws.page_margins.top = 0.7
    ws.page_margins.bottom = 0.55
    ws.oddFooter.center.text = "冷板总体设计  ·  " + DATE
    ws.oddFooter.right.text = "第 &P 页"
    ws.oddHeader.left.text = title
    ws.sheet_properties.tabColor = "0E3A5D"
    ws["A1"] = title
    ws["A1"].font = Font(name="微软雅黑", size=16, bold=True, color="0E3A5D")
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.row_dimensions[1].height = 26
    for c, h in enumerate(headers, 1):
        cell = ws.cell(3, c, h)
        cell.font = FONT_HD
        cell.fill = FILL_HD
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        cell.border = THIN
    ws.row_dimensions[3].height = 22
    ws.freeze_panes = "A4"
    ws.print_title_rows = "1:3"
    ws.auto_filter.ref = f"A3:{get_column_letter(len(headers))}3"
    ws.page_setup.fitToHeight = 0
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def put(ws, r, values, input_cols=()):
    for c, val in enumerate(values, 1):
        cell = ws.cell(r, c, val)
        cell.font = FONT_IN if c in input_cols else FONT
        cell.border = THIN
        cell.alignment = Alignment(wrap_text=True, vertical="center",
                                   horizontal="center" if c in input_cols or isinstance(val, (int, float)) else "left")
        if c in input_cols and isinstance(val, (int, float)):
            cell.fill = FILL_IN
            cell.number_format = "0.000"
        elif isinstance(val, float):
            cell.number_format = "0.000"
            cell.alignment = Alignment(horizontal="center", vertical="center")
    ws.row_dimensions[r].height = 22
    return r + 1


def name_it(wb, key, sheet, row, col="C"):
    wb.defined_names.add(DefinedName(name=key, attr_text=f"'{sheet}'!${col}${row}"))


def cover(wb, doc, lines):
    ws = wb.active
    ws.title = "封面"
    prep(ws, doc, ["项", "内容"], [22, 88], landscape=False)
    ws.page_setup.fitToHeight = 1
    r = 4
    for k, v in lines:
        r = put(ws, r, [k, v])
        ws.row_dimensions[r - 1].height = 30
    ws.auto_filter.ref = f"A3:B{r-1}"
    return ws


def book_dr0():
    wb = Workbook()
    cover(wb, "DR0 输入追溯", [
        ("文件", "01_DR0_输入追溯.xlsx"),
        ("日期", DATE),
        ("用途", "① 需求与输入。蓝字可改。状态由人工维持，不从公式推断。"),
    ])
    ws = wb.create_sheet("输入")
    prep(ws, "输入追溯", ["编号", "项目", "采用值", "状态", "影响的门", "说明"], [12, 28, 28, 12, 14, 42])
    rows = [
        ["IN-01", "B300 保证功率", "1100 W", "已有", "DR2", "Lenovo TGP"],
        ["IN-02", "B300 包络功率", "1400 W", "已有", "DR2", "不作保证"],
        ["IN-03", "GPU 冷板流量", "2.0 L/min", "假设", "DR0", "托盘分流未冻结"],
        ["IN-04", "Grace 功率，含内存", "300 W", "已有", "DR2", "LP2357"],
        ["IN-05", "CPU / 内存分功率", "260 / 40 W", "假设", "DR2", "总和仍是 300"],
        ["IN-06", "Grace 流量", "0.55 L/min", "假设", "DR2", "8 K 反算约 0.543"],
        ["IN-07", "die 尺寸", "27×28 mm", "假设", "DR0", "等封装图"],
        ["IN-08", "HBM 颗数", "8", "假设", "DR0", "左右各 4"],
        ["IN-09", "盖板轮廓与螺孔", "未到", "缺失", "DR0", "图纸不能投产"],
        ["IN-10", "官方功率图", "未到", "缺失", "DR3", "热点系数仍是假设"],
        ["IN-11", "TIM2 实测", "0.004–0.008 °C/W", "假设", "DR2", "决定热阻上界"],
        ["IN-12", "冷却液", "水，40 °C", "假设", "DR2", "若改 PG25 要重算流量"],
        ["IN-13", "GPU 孔径", "0.40 与 0.50 并存", "待确认", "DR3", "孔位链与孔径无关"],
        ["IN-14", "HBM 截面", "0.80×2.00，7 条", "已有", "DR3", "0.60 mm 八槽不采用"],
    ]
    for i, row in enumerate(rows):
        put(ws, 4 + i, row, input_cols=(3,))
    ws.auto_filter.ref = f"A3:F{3+len(rows)}"
    wb.save(OUT / "01_DR0_输入追溯.xlsx")


def book_dr1():
    wb = Workbook()
    cover(wb, "DR1 方案权衡", [
        ("文件", "02_DR1_方案权衡.xlsx"),
        ("日期", DATE),
        ("用途", "② 概念与选型。权重和分数是蓝字，加权是公式。"),
    ])
    ws = wb.create_sheet("权衡")
    headers = ["方案", "热点", "HBM安全", "压降", "制造", "防堵", "专利", "加权", "报告印数", "差"]
    prep(ws, "方案权衡", headers, [16, 10, 12, 10, 10, 10, 10, 12, 12, 10])
    weights = list(WTS)
    put(ws, 4, ["权重"] + weights + ["", "", ""], input_cols=(2, 3, 4, 5, 6, 7))
    for col, key in enumerate(["w1", "w2", "w3", "w4", "w5", "w6"], 2):
        name_it(wb, key, "权衡", 4, get_column_letter(col))
    names = list(SCORES)
    for i, name in enumerate(names):
        r = 5 + i
        scores = SCORES[name]
        put(ws, r, [name, *scores, None, PUB[name], None], input_cols=(2, 3, 4, 5, 6, 7))
        ws.cell(r, 8, f"=B{r}*w1+C{r}*w2+D{r}*w3+E{r}*w4+F{r}*w5+G{r}*w6")
        ws.cell(r, 8).number_format = "0.00"
        ws.cell(r, 8).font = FONT_B
        ws.cell(r, 8).border = THIN
        ws.cell(r, 10, f"=H{r}-I{r}")
        ws.cell(r, 10).number_format = "0.00"
        ws.cell(r, 10).font = FONT
        ws.cell(r, 10).border = THIN
        ws.cell(r, 9).number_format = "0.00"
        ws.cell(r, 9).fill = FILL_IN
    ws.auto_filter.ref = "A3:J8"
    note = wb.create_sheet("说明")
    prep(note, "怎么读差值", ["项", "内容"], [18, 80], landscape=False)
    put(note, 4, ["重算", "加权等于六项分数乘第 4 行权重。"])
    put(note, 5, ["报告印数", "v2.0 表末的 3.20 / 2.95 / 2.85 / 4.50。"])
    put(note, 6, ["差", "公式减印数，约 0.05。名次仍是分区杂交最高。"])
    note.auto_filter.ref = "A3:B6"
    wb.save(OUT / "02_DR1_方案权衡.xlsx")


def book_dr2():
    wb = Workbook()
    cover(wb, "DR2 一维性能核算", [
        ("文件", "03_DR2_一维性能核算.xlsx"),
        ("日期", DATE),
        ("用途", "③④ 性能与一维。蓝字为输入。孔速、温升、热阻合计、Grace 通道均为公式。"),
        ("对流热阻", "GPU 短槽模型的对流热阻是模型输出，本表当作输入。改槽之后要重跑计算模块，不要只改这个格子就当成新的关联式。"),
    ])
    inp = wb.create_sheet("输入")
    prep(inp, "输入", ["符号", "含义", "数值", "单位"], [16, 28, 16, 16])
    params = [
        ("rho", "密度", RHO, "kg/m3"),
        ("cp", "比热", CP, "J/kgK"),
        ("mu", "粘度", MU, "Pa·s"),
        ("kcu", "铜导热", KCU, "W/mK"),
        ("Pa", "DP-A 功率", P_A, "W"),
        ("Qa", "DP-A 流量", Q_A, "L/min"),
        ("Qgpu", "GPU 流量", Q_GPU, "L/min"),
        ("Njet", "孔数", N_JET, "个"),
        ("Dmm", "孔径", 0.50, "mm"),
        ("Kjet", "孔口阻力系数", 1.8, "-"),
        ("Rtim_lo", "TIM2 下界", 0.004, "°C/W"),
        ("Rtim_hi", "TIM2 上界", 0.008, "°C/W"),
        ("tcu", "余铜", 2.0, "mm"),
        ("Adie", "两 die 面积", A2 * 1e6, "mm2"),
        ("Rconv", "短槽对流热阻", R_CONV, "°C/W"),
        ("Rtarget", "热阻目标", 0.028, "°C/W"),
        ("Qg_hbm", "HBM 总流量", 0.40, "L/min"),
        ("n_old", "旧截面条数", 16, "条"),
        ("w_old", "旧槽宽", 0.60, "mm"),
        ("h_old", "旧槽深", 1.50, "mm"),
        ("q_side", "新截面单侧流量", 0.20, "L/min"),
        ("n_new", "新截面条数", 7, "条"),
        ("w_new", "新槽宽", 0.80, "mm"),
        ("h_new", "新槽深", 2.00, "mm"),
        ("Lslot", "槽长", 50, "mm"),
        ("Pgr", "Grace 功率", 300, "W"),
        ("dTset", "Grace 设定温升", 8, "K"),
        ("Qgr", "Grace 设计流量", 0.55, "L/min"),
        ("Pcpu", "CPU 功率", 260, "W"),
        ("Pmem", "单侧内存功率", 20, "W"),
        ("ncpu", "CPU 槽数", 48, "条"),
        ("wcpu", "CPU 槽宽", 0.40, "mm"),
        ("hcpu", "CPU 槽深", 1.20, "mm"),
        ("Lcpu", "CPU 润湿长", 40, "mm"),
        ("Lhcpu", "CPU 受热长", 32, "mm"),
        ("nmem", "单侧内存槽数", 6, "条"),
        ("wmem", "内存槽宽", 1.20, "mm"),
        ("hmem", "内存槽深", 0.80, "mm"),
        ("Lmem", "内存润湿长", 78, "mm"),
        ("Lhmem", "内存受热长", 70, "mm"),
        ("kturn", "弯头阻力合计", 3.0, "-"),
        ("rhoG", "Grace 密度", RHO_G, "kg/m3"),
        ("kG", "Grace 水导热", KF_G, "W/mK"),
    ]
    for i, (key, label, val, unit) in enumerate(params):
        r = 4 + i
        put(inp, r, [key, label, float(val), unit], input_cols=(3,))
        name_it(wb, key, "输入", r, "C")
    inp.auto_filter.ref = f"A3:D{3+len(params)}"

    gpu = wb.create_sheet("GPU")
    prep(gpu, "GPU 能量、射流与热阻", ["量", "公式", "数值", "单位", "说明"], [22, 42, 16, 12, 28])
    put(gpu, 4, ["质量流量", "rho*Qa/60000", None, "kg/s", "DP-A"])
    gpu["C4"] = "=rho*Qa/60000"
    gpu["C4"].number_format = "0.000000"
    gpu["C4"].font = FONT
    gpu["C4"].border = THIN
    put(gpu, 5, ["流体温升", "Pa/(mdot*cp)", None, "K", ""])
    gpu["C5"] = "=Pa/(C4*cp)"
    gpu["C5"].number_format = "0.00"
    gpu["C5"].font = FONT
    gpu["C5"].border = THIN
    put(gpu, 6, ["单孔面积", "pi*D^2/4", None, "m2", "D 用 mm"])
    gpu["C6"] = "=PI()*((Dmm/1000)^2)/4"
    gpu["C6"].number_format = "0.00E+00"
    gpu["C6"].font = FONT
    gpu["C6"].border = THIN
    put(gpu, 7, ["孔速", "Qgpu/N/A", None, "m/s", ""])
    gpu["C7"] = "=(Qgpu/60000)/(Njet*C6)"
    gpu["C7"].number_format = "0.000"
    gpu["C7"].font = FONT
    gpu["C7"].border = THIN
    put(gpu, 8, ["Re", "rho*V*D/mu", None, "-", ""])
    gpu["C8"] = "=rho*C7*(Dmm/1000)/mu"
    gpu["C8"].number_format = "0.0"
    gpu["C8"].font = FONT
    gpu["C8"].border = THIN
    put(gpu, 9, ["孔口压降", "K*rho*V^2/2", None, "Pa", "K=1.8"])
    gpu["C9"] = "=Kjet*rho*C7*C7/2"
    gpu["C9"].number_format = "0.0"
    gpu["C9"].font = FONT
    gpu["C9"].border = THIN
    put(gpu, 10, ["余铜热阻", "t/(k*A)", None, "°C/W", "A 为两 die"])
    gpu["C10"] = "=(tcu/1000)/(kcu*(Adie/1000000))"
    gpu["C10"].number_format = "0.000000"
    gpu["C10"].font = FONT
    gpu["C10"].border = THIN
    put(gpu, 11, ["壳–进液下界", "Rcu+Rtim_lo+Rconv", None, "°C/W", ""])
    gpu["C11"] = "=C10+Rtim_lo+Rconv"
    gpu["C11"].number_format = "0.000000"
    gpu["C11"].font = FONT_B
    gpu["C11"].border = THIN
    put(gpu, 12, ["壳–进液上界", "Rcu+Rtim_hi+Rconv", None, "°C/W", ""])
    gpu["C12"] = "=C10+Rtim_hi+Rconv"
    gpu["C12"].number_format = "0.000000"
    gpu["C12"].font = FONT_B
    gpu["C12"].border = THIN
    put(gpu, 13, ["上界是否进目标", "上界<目标", None, "-", "不进则 DR2 仍是有条件"])
    gpu["C13"] = '=IF(C12<Rtarget,"通过","不判定")'
    gpu["C13"].font = FONT_B
    gpu["C13"].border = THIN
    gpu.conditional_formatting.add("C13", FormulaRule(formula=['C13="通过"'], fill=PatternFill("solid", fgColor="C6EFCE")))
    gpu.conditional_formatting.add("C13", FormulaRule(formula=['C13="不判定"'], fill=PatternFill("solid", fgColor="F4C7C3")))
    gpu.auto_filter.ref = "A3:E13"

    hbm = wb.create_sheet("HBM")
    prep(hbm, "HBM 两套截面的槽速", ["方案", "流量 L/min", "条数", "宽 mm", "深 mm", "速度 m/s", "Re", "摩擦压降 Pa"],
         [18, 14, 10, 12, 12, 14, 12, 16])
    put(hbm, 4, ["v2.0 十六槽", None, None, None, None, None, None, None])
    for col, formula in enumerate(["=Qg_hbm", "=n_old", "=w_old", "=h_old"], 2):
        hbm.cell(4, col, formula).font = FONT
        hbm.cell(4, col).border = THIN
        hbm.cell(4, col).number_format = "0.00"
    hbm["F4"] = "=(B4/60000)/(C4*(D4/1000)*(E4/1000))"
    hbm["G4"] = "=rho*F4*(2*(D4/1000)*(E4/1000)/((D4+E4)/1000))/mu"
    hbm["H4"] = "=(64/G4)*((Lslot/1000)/(2*(D4/1000)*(E4/1000)/((D4+E4)/1000)))*rho*F4*F4/2"
    put(hbm, 5, ["w08h20 七槽单侧", None, None, None, None, None, None, None])
    for col, formula in enumerate(["=q_side", "=n_new", "=w_new", "=h_new"], 2):
        hbm.cell(5, col, formula).font = FONT
        hbm.cell(5, col).border = THIN
        hbm.cell(5, col).number_format = "0.00"
    hbm["F5"] = "=(B5/60000)/(C5*(D5/1000)*(E5/1000))"
    hbm["G5"] = "=rho*F5*(2*(D5/1000)*(E5/1000)/((D5+E5)/1000))/mu"
    hbm["H5"] = "=(64/G5)*((Lslot/1000)/(2*(D5/1000)*(E5/1000)/((D5+E5)/1000)))*rho*F5*F5/2"
    for coord in ("F4", "G4", "H4", "F5", "G5", "H5"):
        hbm[coord].font = FONT
        hbm[coord].border = THIN
        hbm[coord].number_format = "0.000"
    hbm.auto_filter.ref = "A3:H5"

    gr = wb.create_sheet("Grace")
    prep(gr, "Grace 设计流量下的通道", ["路", "流量 L/min", "速度 m/s", "Re", "压降 kPa", "热阻 °C/W", "对流温升 K"],
         [16, 16, 14, 12, 14, 14, 14])
    # CPU
    put(gr, 4, ["CPU", None, None, None, None, None, None])
    gr["B4"] = "=Qgr*Pcpu/Pgr"
    gr["C4"] = "=(B4/60000)/(ncpu*(wcpu/1000)*(hcpu/1000))"
    gr["D4"] = "=rhoG*C4*(2*(wcpu/1000)*(hcpu/1000)/((wcpu+hcpu)/1000))/mu"
    gr["E4"] = "=((64/D4)*((Lcpu/1000)/(2*(wcpu/1000)*(hcpu/1000)/((wcpu+hcpu)/1000)))+kturn)*rhoG*C4*C4/2/1000"
    gr["F4"] = "=1/((4.8*kG/(2*(wcpu/1000)*(hcpu/1000)/((wcpu+hcpu)/1000)))*(ncpu*(Lhcpu/1000)*((wcpu/1000)+2*(hcpu/1000))))"
    gr["G4"] = "=Pcpu*F4"
    put(gr, 5, ["单侧内存", None, None, None, None, None, None])
    gr["B5"] = "=Qgr*Pmem/Pgr"
    gr["C5"] = "=(B5/60000)/(nmem*(wmem/1000)*(hmem/1000))"
    gr["D5"] = "=rhoG*C5*(2*(wmem/1000)*(hmem/1000)/((wmem+hmem)/1000))/mu"
    gr["E5"] = "=((64/D5)*((Lmem/1000)/(2*(wmem/1000)*(hmem/1000)/((wmem+hmem)/1000)))+kturn)*rhoG*C5*C5/2/1000"
    gr["F5"] = "=1/((4.8*kG/(2*(wmem/1000)*(hmem/1000)/((wmem+hmem)/1000)))*(nmem*(Lhmem/1000)*((wmem/1000)+2*(hmem/1000))))"
    gr["G5"] = "=Pmem*F5"
    put(gr, 6, ["能量平衡流量", None, None, None, None, None, None])
    gr["B6"] = "=Pgr/(rhoG*cp*dTset)*60000"
    gr["C6"] = "说明：报告表 0.34 m/s、0.96 kPa 接近这一流量下的 CPU，不是 0.55 这一行"
    for coord in ("B4", "C4", "D4", "E4", "F4", "G4", "B5", "C5", "D5", "E5", "F5", "G5", "B6"):
        gr[coord].font = FONT
        gr[coord].border = THIN
        gr[coord].number_format = "0.000"
    gr["C6"].font = FONT
    gr.merge_cells("C6:G6")
    gr.auto_filter.ref = "A3:G6"

    sweep = wb.create_sheet("孔径")
    prep(sweep, "孔径扫描（孔数与 GPU 流量不变）", ["D mm", "孔速 m/s", "Re", "压降 kPa", "Sx/D", "Sy/D", "H/D"],
         [12, 14, 12, 14, 12, 12, 12])
    for i, Dmm in enumerate((0.50, 0.45, 0.40, 0.35, 0.30)):
        r = 4 + i
        put(sweep, r, [Dmm, None, None, None, None, None, None], input_cols=(1,))
        sweep.cell(r, 1).number_format = "0.00"
        sweep.cell(r, 2, f"=(Qgpu/60000)/(Njet*PI()*((A{r}/1000)^2)/4)")
        sweep.cell(r, 3, f"=rho*B{r}*(A{r}/1000)/mu")
        sweep.cell(r, 4, f"=Kjet*rho*B{r}*B{r}/2/1000")
        sweep.cell(r, 5, f"=3/A{r}")
        sweep.cell(r, 6, f"=2.4/A{r}")
        sweep.cell(r, 7, f"=2/A{r}")
        for c in range(2, 8):
            sweep.cell(r, c).font = FONT
            sweep.cell(r, c).border = THIN
            sweep.cell(r, c).number_format = "0.000"
    sweep.auto_filter.ref = "A3:G8"
    wb.save(OUT / "03_DR2_一维性能核算.xlsx")


def book_dr3():
    wb = Workbook()
    cover(wb, "DR3 / DR4 仿真、图纸与试验", [
        ("文件", "04_DR3_仿真图纸与试验门.xlsx"),
        ("日期", DATE),
        ("仿真", "用场温度和功率重算热阻。不要把 HBM 的热阻和 0.028 放在一起比。"),
        ("尺寸", "只复算放行要用的几条链。全套在上一级目录的尺寸核实2。"),
        ("试验", "判据是输入，实测列空着。"),
    ])
    sim = wb.create_sheet("仿真")
    prep(sim, "局部 CFD 热阻", ["场", "T_TIM K", "T_in K", "功率 W", "R °C/W", "对照目标", "说明"],
         [22, 14, 12, 14, 14, 14, 36])
    put(sim, 4, ["GPU 12 孔带", T_TIM12, T_IN, P_DIE, None, 0.028, "分母是 900.9 W，已含 TIM 与铜"], input_cols=(2, 3, 4, 6))
    sim["E4"] = "=(B4-C4)/D4"
    put(sim, 5, ["HBM 单侧七槽", T_HBM, T_IN, P_HBM, None, None, "分母是单侧 99 W，不和 0.028 比"], input_cols=(2, 3, 4))
    sim["E5"] = "=(B5-C5)/D5"
    sim["F5"] = "—"
    for coord in ("E4", "E5"):
        sim[coord].number_format = "0.00000"
        sim[coord].font = FONT_B
        sim[coord].border = THIN
    sim["G4"] = '=IF(E4<F4,"低于对照","仍高于 0.028 的对照")'
    sim["G4"].font = FONT
    sim.auto_filter.ref = "A3:G5"

    dim = wb.create_sheet("尺寸链")
    prep(dim, "放行用的名义尺寸链", ["链", "组成", "计算 mm", "封闭环 mm", "差", "判定"],
         [22, 36, 14, 14, 12, 12])
    items = [
        ("GPU板宽", "=5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5", 95),
        ("GPU板长", "=12.5+50+12.5", 75),
        ("GPU板厚", "=2+1.5+2+2.5+0.5", 8.5),
        ("HBM列宽", "=0.3+7*0.8+6*0.8+0.3", 11),
        ("HBM铜厚", "=2+2+4", 8),
        ("Grace板厚", "=2+1.2+0.3+2.5+2", 8),
        ("节距8.333", "=6*(50/6)", 50),
        ("节距8.00", "=6*8", 50),
    ]
    for i, (name, formula, target) in enumerate(items):
        r = 4 + i
        put(dim, r, [name, formula, None, target, None, None], input_cols=(4,))
        dim.cell(r, 3, formula)
        dim.cell(r, 3).number_format = "0.000"
        dim.cell(r, 3).font = FONT
        dim.cell(r, 3).border = THIN
        dim.cell(r, 5, f"=C{r}-D{r}")
        dim.cell(r, 5).number_format = "0.000"
        dim.cell(r, 5).font = FONT
        dim.cell(r, 5).border = THIN
        dim.cell(r, 6, f'=IF(ABS(E{r})<0.001,"闭合","不闭合")')
        dim.cell(r, 6).font = FONT_B
        dim.cell(r, 6).border = THIN
        dim.conditional_formatting.add(f"F{r}", FormulaRule(formula=[f'F{r}="闭合"'], fill=PatternFill("solid", fgColor="C6EFCE")))
        dim.conditional_formatting.add(f"F{r}", FormulaRule(formula=[f'F{r}="不闭合"'], fill=PatternFill("solid", fgColor="F4C7C3")))
    dim.auto_filter.ref = "A3:F11"

    test = wb.create_sheet("试验门")
    prep(test, "DR4 试验门（实测未填）", ["试验", "判据", "单位", "实测", "判定"], [28, 22, 14, 14, 14])
    tests = [
        ("GPU TTV 热阻", 0.028, "°C/W", "小于"),
        ("GPU 流阻", 18, "kPa", "不大于"),
        ("Grace 支路压降下限", 8, "kPa", "不小于"),
        ("Grace 支路压降上限", 12, "kPa", "不大于"),
        ("两 die 温差", 5, "K", "不大于"),
    ]
    for i, (name, limit, unit, how) in enumerate(tests):
        r = 4 + i
        put(test, r, [name, limit, unit, None, None], input_cols=(2, 4))
        test.cell(r, 2).number_format = "0.000"
        if how == "小于":
            formula = f'=IF(D{r}="","未测",IF(D{r}<B{r},"通过","未通过"))'
        elif how == "不大于":
            formula = f'=IF(D{r}="","未测",IF(D{r}<=B{r},"通过","未通过"))'
        else:
            formula = f'=IF(D{r}="","未测",IF(D{r}>=B{r},"通过","未通过"))'
        test.cell(r, 5, formula)
        test.cell(r, 5).font = FONT_B
        test.cell(r, 5).border = THIN
    test.auto_filter.ref = "A3:E8"
    wb.save(OUT / "04_DR3_仿真图纸与试验门.xlsx")


def main():
    checks()
    html_path = OUT / "冷板总体设计报告.html"
    html_path.write_text(build_html(), encoding="utf-8")
    book_dr0()
    book_dr1()
    book_dr2()
    book_dr3()
    print("html", html_path.name)
    print("scores", {k: round(weighted(v), 2) for k, v in SCORES.items()})
    print("R", round(R_LO, 5), round(R_HI, 5), "dTf", round(DTF_A, 3))
    print("grace", round(G_CPU["V"], 3), round(G_CPU["dP"] / 1000, 3), round(G_MEM["V"], 3))
    print("Qe", round(Q_E, 3), "cpuE", round(G_CPU_E["V"], 3), round(G_CPU_E["dP"] / 1000, 3))
    print("cfd", round(R_CFD, 5), round(R_HBM, 4))


if __name__ == "__main__":
    main()
