# -*- coding: utf-8 -*-
"""把 docs/plan/ 下 v1.1 规划 md 生成单文件自包含 html（基于 planning/build_plan.py 改写）。

md 是唯一正文来源。```svg:<name>``` 代码块在 html 里换成内联 SVG，
md 里保留文字示意；svg:gantt 的数据行直接驱动甘特图。
html 不引用任何外部资源：CSS / JS / SVG 全部内联。
另把设计流程模型导出为 assets/ 下的独立 SVG，便于截图展示。

用法：
  python build_plan.py           生成 html 与 assets/*.svg
  python build_plan.py --check   生成后自检：外链、锚点、ID 重复、未知标签、node 检查 JS 语法
需要 markdown 包（默认 python 已有）。
"""
from __future__ import annotations

import datetime as dt
import html
import re
import shutil
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

HERE = Path(__file__).resolve().parent
ASSETS = HERE / "assets"
DOCS = ["AIDC液冷设计平台_项目规划_v1.1_20261002.md", "AIDC液冷设计平台_实施计划_v1.1_20261002.md"]
FLOW_SVG = "AIDC液冷设计平台_设计流程模型_v1.1_20261002.svg"
W1 = dt.date(2026, 10, 5)
FONT = "'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif"

C = {
    "navy": "#123b5d", "teal": "#0e8a7a", "orange": "#c56a12", "purple": "#6b4fa0",
    "red": "#b23a3a", "grey": "#5d6b78", "line": "#9fb0bf", "bg1": "#eef6f5",
    "bg2": "#fdf3e7", "bg3": "#f2eef9", "bg0": "#f4f7fa", "green": "#2e7d32",
    "amber": "#b7791f",
}


def tw(s: str, size: float) -> float:
    return sum(size if ord(ch) > 0x2E7F else size * 0.58 for ch in s)


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def text(x, y, s, size=12, color="#1d2b36", anchor="middle", weight="normal"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" '
            f'text-anchor="{anchor}" font-weight="{weight}">{esc(s)}</text>')


def rect(x, y, w, h, fill="#fff", stroke=C["navy"], rx=6, dash=None, sw=1.3):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')


def arrow(x1, y1, x2, y2, color=C["grey"], dash=None, mk="arr", both=False):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    s = f' marker-start="url(#{mk})"' if both else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="1.6"{d}{s} marker-end="url(#{mk})"/>')


def curve(d, color=C["red"], mk="arrR", dash="7 4", sw=1.8):
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" '
            f'stroke-dasharray="{dash}" marker-end="url(#{mk})"/>')


def defs():
    out = ["<defs>"]
    for mid, col in (("arr", C["grey"]), ("arrR", C["red"]), ("arrO", C["orange"]),
                     ("arrT", C["teal"]), ("arrP", C["purple"])):
        out.append(f'<marker id="{mid}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
                   f'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
                   f'fill="{col}"/></marker>')
    out.append("</defs>")
    return "".join(out)


_SVG_SEQ = [0]


def svg_wrap(w, h, body, title, standalone=False):
    _SVG_SEQ[0] += 1
    pfx = f"f{_SVG_SEQ[0]}"
    inner = (defs() + body).replace('id="arr', f'id="{pfx}arr').replace("url(#arr", f"url(#{pfx}arr")
    size = f' width="{w}" height="{h}"' if standalone else ""
    bg = f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff"/>' if standalone else ""
    return (f'<svg class="fig-svg" viewBox="0 0 {w} {h}"{size} role="img" aria-label="{esc(title)}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">{bg}{inner}</svg>')


# ---------- 图：设计流程模型 v1.1（9 阶段 · DR0–DR6 · R1–R4） ----------
STAGES = [
    # 标题, 内容三行, AI 两行, 状态, 状态色, 备注, 实施 Phase, 门控, 门控底色
    ("① 需求与输入", ["芯片规格 / 热包络", "机柜水力表 · 接口标准", "D-001 设计工况"],
     ["RAG 抽取 · 追溯矩阵", "冲突检测 dp_diff"], "已完成", "green",
     "DR0 有条件（6 项缺失）", "实施 P0 · S01–S03", "DR0 输入冻结", "amber"),
    ("② 概念与选型", ["方案权衡矩阵", "分区策略", "专利 FTO 初筛"],
     ["矩阵复算 · 敏感性", "权利要求对照草稿"], "已完成", "green",
     "DR1 已通过（4.50）", "实施 P1 · S37", "DR1 方案选定", "green"),
    ("③ 性能设计", ["热阻预算分配", "射流参数窗", "流量 / 压降预算"],
     ["预算倒推 · 设计窗", "6~10 K 包络扫描"], "已完成（水口径）", "green",
     "DR2 有条件 · PG25 待重算", "实施 P1 · S05、S07", "DR2 性能基线", "amber"),
    ("④ 一维计算", ["能量平衡", "水力与换热关联式", "敏感性与差距闭合"],
     ["A: Python 1D（主）", "B: Simulink agent"], "已完成（水口径）", "green",
     "DR2 有条件 · PG25 待重算", "实施 P1 · S04–S09", "DR2 闸门", "amber"),
    ("⑤ 三维仿真", ["共轭 CFD", "网格无关性 · V&V", "PG25 6 工况矩阵"],
     ["Fluent 批处理 · GCI", "R1 自动扫描/优化"], "工具待决策", "orange",
     "推荐 Fluent · 待 Q-04", "实施 P3 · S14–S19", "DR3 仿真通过", "white"),
    ("⑥ 机械与图纸", ["层叠与公差", "承压 / 变形 FEA", "2D / 3D / 爆炸图"],
     ["build123d · FEA", "ezdxf 出图 · GD&T"], "未开始", "grey",
     "仅候选几何 / 解析校核", "实施 P2、P4", "DR3 闸门", "white"),
    ("⑦ 样件与试验", ["TTV 热阻", "流阻曲线", "红外 / 氦检"],
     ["DAQ 脚本 · 不确定度", "V&V 20 偏差判读"], "未开始", "grey",
     "DR4 门表实测为空", "实施 P5 · S23–S26", "DR4 送样放行", "white"),
    ("⑧ 数字孪生模型", ["ROM / 代理模型", "动态热–水力网络", "FMU · 在线标定"],
     ["A: Python ROM→FMU", "B: Simscape Fluids"], "未开始（新增）", "purple",
     "路线待选 Q-07", "实施 P6a · S27/28/30", "DR5 孪生验收", "white"),
    ("⑨ 孪生在环 AI 控制", ["PID / MPC / RL", "MIL → SIL → HIL", "温升 6~10 K 调度"],
     ["A: Python MPC/RL SIL", "B: MPC/RL Toolbox"], "未开始（新增）", "purple",
     "路线待选 Q-07", "实施 P6b · S29、S40", "DR6 控制策略放行", "white"),
]
STATUS_COL = {"green": ("#e6f4ea", C["green"]), "orange": ("#fdf0e1", C["orange"]),
              "grey": ("#eef1f4", C["grey"]), "purple": ("#f2eef9", C["purple"])}
GATE_FILL = {"green": ("#e6f4ea", C["green"]), "amber": ("#fff4dc", C["amber"]), "white": ("#ffffff", "#8a4b08")}


def svg_flow(standalone=False):
    W, H = 1500, 604
    bw, gap, x0 = 148, 14, 20
    cy0, ch = 62, 244
    gy = 350
    xc = lambda i: x0 + i * (bw + gap) + bw / 2
    b = [text(20, 24, "设计流程模型 v1.1 · 门控 + 回路迭代（9 阶段 · DR0–DR6 · R1–R4）", 15.5, C["navy"], "start", "bold"),
         text(W - 20, 24, "状态截至 2026-10-02 · D-001：PG25 · 1400 W 基线 · 温升 6~10 K · 1100 W 校核", 11.5, C["grey"], "end")]
    groups = [(0, 3, C["teal"], C["bg1"], "已完成 ①–④（v2.0 水口径；D-001 下待重算）"),
              (4, 4, C["orange"], C["bg2"], "⑤ 工具待决策"),
              (5, 6, C["grey"], C["bg0"], "未开始 ⑥–⑦"),
              (7, 8, C["purple"], C["bg3"], "新增 ⑧⑨ · 未开始")]
    for i0, i1, col, bg, lab in groups:
        gx = x0 + i0 * (bw + gap) - 6
        gw = (i1 - i0 + 1) * bw + (i1 - i0) * gap + 12
        b.append(rect(gx, 36, gw, 276, fill=bg, stroke=col, rx=10, dash="6 4", sw=1.4))
        b.append(text(gx + gw / 2, 52, lab, 12, col, weight="bold"))
    for i, (title, lines, ai, st, stc, note, phase, _g, _gc) in enumerate(STAGES):
        x = x0 + i * (bw + gap)
        col = C["teal"] if i < 4 else (C["orange"] if i == 4 else (C["grey"] if i < 7 else C["purple"]))
        b.append(rect(x, cy0, bw, ch, fill="#fff", stroke=col, rx=8, sw=1.6))
        b.append(f'<path d="M{x + 0.8:.1f},{cy0 + 28} L{x + 0.8:.1f},{cy0 + 8} Q{x + 0.8:.1f},{cy0 + 0.8} {x + 8:.1f},{cy0 + 0.8} '
                 f'L{x + bw - 8:.1f},{cy0 + 0.8} Q{x + bw - 0.8:.1f},{cy0 + 0.8} {x + bw - 0.8:.1f},{cy0 + 8} L{x + bw - 0.8:.1f},{cy0 + 28} Z" fill="{col}"/>')
        tsize = 13.5 if tw(title, 13.5) < bw - 10 else 12.5
        b.append(text(x + bw / 2, cy0 + 19, title, tsize, "#ffffff", weight="bold"))
        for k, ln in enumerate(lines):
            b.append(text(x + 10, cy0 + 46 + k * 17, "· " + ln, 10.8, "#2b3a47", "start"))
        b.append(f'<line x1="{x + 8}" y1="{cy0 + 92}" x2="{x + bw - 8}" y2="{cy0 + 92}" stroke="#dfe5ea" stroke-width="1"/>')
        b.append(text(x + 10, cy0 + 108, "AI 赋能 / 工具", 10.5, C["orange"], "start", "bold"))
        for k, ln in enumerate(ai):
            b.append(text(x + 10, cy0 + 125 + k * 16, ln, 10.6, "#1f4e6e", "start"))
        b.append(f'<line x1="{x + 8}" y1="{cy0 + 152}" x2="{x + bw - 8}" y2="{cy0 + 152}" stroke="#dfe5ea" stroke-width="1"/>')
        fill, stroke = STATUS_COL[stc]
        b.append(rect(x + 8, cy0 + 160, bw - 16, 22, fill=fill, stroke=stroke, rx=11, sw=1.1))
        b.append(text(x + bw / 2, cy0 + 175, st, 11, stroke, weight="bold"))
        b.append(text(x + bw / 2, cy0 + 200, note, 10.2, C["grey"]))
        b.append(text(x + bw / 2, cy0 + 224, phase, 10.8, C["navy"], weight="bold"))
        if i < len(STAGES) - 1:
            b.append(arrow(x + bw + 1, cy0 + 14, x + bw + gap - 1, cy0 + 14))
    for i, st in enumerate(STAGES):
        gate, gc = st[7], st[8]
        cx = xc(i)
        b.append(f'<line x1="{cx}" y1="{cy0 + ch}" x2="{cx}" y2="{gy - 22}" stroke="{C["line"]}" stroke-width="1.2"/>')
        fill, stroke = GATE_FILL[gc]
        if i >= 7:
            stroke = C["purple"]
        b.append(f'<polygon points="{cx},{gy - 22} {cx + 66},{gy} {cx},{gy + 22} {cx - 66},{gy}" '
                 f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"/>')
        b.append(text(cx, gy + 4, gate, 11, "#5a3206" if i < 7 else C["purple"], weight="bold"))
    # 回路
    b.append(curve(f"M{xc(4)},{gy + 22} C{xc(4)},{gy + 50} {xc(3)},{gy + 50} {xc(3)},{gy + 26}"))
    b.append(text((xc(3) + xc(4)) / 2, gy + 60, "R1 仿真不达标 → 回 ③/④ 改几何 · AI 自动扫描/优化", 11.5, C["red"], weight="bold"))
    b.append(curve(f"M{xc(6)},{gy + 22} C{xc(6)},{gy + 120} {xc(2) + 16},{gy + 120} {xc(2) + 16},{gy + 21}"))
    b.append(text((xc(2) + xc(6)) / 2 + 70, gy + 113, "R2 试验与仿真偏差 > 15% → 修正模型回 ③（V&V，ASME V&V 20）", 11.5, C["red"], weight="bold"))
    b.append(curve(f"M{xc(7) + 14},{gy + 17} C{xc(7) + 70},{gy + 52} {xc(7) - 70},{gy + 52} {xc(7) - 14},{gy + 20}",
                   color=C["purple"], mk="arrP"))
    b.append(text(xc(7), gy + 62, "R3 孪生–实测比对超阈值 → 重新标定", 11.5, C["purple"], weight="bold"))
    b.append(curve(f"M{xc(8)},{gy + 22} C{xc(8)},{gy + 180} {xc(2) - 16},{gy + 180} {xc(2) - 16},{gy + 21}",
                   color=C["teal"], mk="arrT"))
    b.append(text((xc(2) + xc(8)) / 2 + 60, gy + 160, "R4 控制效果反哺设计指标（流量余量、压降预算）→ ③", 11.5, C["teal"], weight="bold"))
    # 图例
    ly = H - 34
    items = [("已完成", "green"), ("工具待决策", "orange"), ("未开始", "grey"), ("新增 · 未开始", "purple")]
    lx = 20
    for lab, k in items:
        fill, stroke = STATUS_COL[k]
        wpx = tw(lab, 11) + 22
        b.append(rect(lx, ly - 14, wpx, 20, fill=fill, stroke=stroke, rx=10, sw=1.1))
        b.append(text(lx + wpx / 2, ly, lab, 11, stroke, weight="bold"))
        lx += wpx + 10
    b.append(f'<polygon points="{lx + 14},{ly - 14} {lx + 30},{ly - 4} {lx + 14},{ly + 6} {lx - 2},{ly - 4}" fill="#fff4dc" stroke="{C["amber"]}" stroke-width="1.3"/>')
    b.append(text(lx + 36, ly, "门控（黄 = 有条件，绿 = 已通过）", 11, C["grey"], "start"))
    lx += 36 + tw("门控（黄 = 有条件，绿 = 已通过）", 11) + 16
    b.append(f'<line x1="{lx}" y1="{ly - 4}" x2="{lx + 34}" y2="{ly - 4}" stroke="{C["red"]}" stroke-width="1.8" stroke-dasharray="7 4"/>')
    b.append(text(lx + 40, ly, "迭代回路 R1–R4", 11, C["grey"], "start"))
    b.append(text(20, H - 10, "所有 DR 由人签字（E3）；DR3 叠加 E1 几何冻结 / E2 大算例启动；DR4、DR6 叠加 E4 实物动作并比照平台闸门③。"
                  "⑧⑨ 与 ④ 一样走路线 A（AI 自研 Python）/ 路线 B（MATLAB/Simulink agent），一维模型为共同源，FMU 为互通接口。",
                  10.8, C["grey"], "start"))
    return svg_wrap(W, H, "".join(b), "设计流程模型 v1.1：门控与回路迭代", standalone)


# ---------- 图：孪生与控制双路线 ----------
def svg_routes():
    W, H = 1300, 462
    b = []
    b.append(rect(20, 150, 205, 150, fill="#fff", stroke=C["navy"], rx=10, sw=1.8))
    for k, (s, sz, col, wt) in enumerate([("共同源", 15, C["navy"], "bold"), ("设计点注册表（D-001）", 11.5, "#2b3a47", "normal"),
                                         ("一维模型 oned_pkg", 11.5, "#2b3a47", "normal"), ("路线 A = 唯一数值源", 11.5, C["teal"], "bold"),
                                         ("路线 B = 对照 / 系统级", 11.5, C["purple"], "bold")]):
        b.append(text(122, 180 + k * 24, s, sz, col, weight=wt))
    lanes = [
        (40, "路线 A · AI 自研（cp-design · Python）", C["teal"], 56,
         [("1D / ROM", "oned_pkg · GP 响应面"), ("孪生 FMU", "RC 网络 · pythonfmu"),
          ("Python SIL", "FMPy · do-mpc / CasADi"), ("RL 研究项 / 报告", "gymnasium + SB3 · 屏蔽")]),
        (418, "路线 B · MATLAB/Simulink agent（ai-matlab 薄加载器 · user-matlab MCP）", C["purple"], 322,
         [("Simscape Fluids", "托盘 / CDU 物理孪生"), ("MPC / RL Toolbox", "约束 MPC · 安全 RL"),
          ("Simulink SIL", "Simulink Test · Coder"), ("HIL", "Simulink Real-Time · E4")]),
    ]
    bx = [262 + k * 214 for k in range(4)]
    bwid, bh = 190, 82
    for ly, lab, col, by, boxes in lanes:
        b.append(text(262, ly + 4, lab, 12.5, col, "start", "bold"))
        for k, (t, s) in enumerate(boxes):
            b.append(rect(bx[k], by, bwid, bh, fill="#fff", stroke=col, rx=8, sw=1.6))
            b.append(text(bx[k] + bwid / 2, by + 34, t, 13.5, col, weight="bold"))
            b.append(text(bx[k] + bwid / 2, by + 58, s, 11, C["grey"]))
            if k < 3:
                b.append(arrow(bx[k] + bwid + 2, by + bh / 2, bx[k + 1] - 2, by + bh / 2, col,
                               mk="arrT" if col == C["teal"] else "arrP"))
    b.append(arrow(226, 190, 260, 100, C["teal"], mk="arrT"))
    b.append(arrow(226, 262, 260, 360, C["purple"], mk="arrP"))
    fx0, fx1 = bx[0], bx[3] + bwid
    b.append(rect(fx0, 172, fx1 - fx0, 116, fill="#fff8ee", stroke=C["orange"], rx=12, dash="7 4", sw=1.6))
    b.append(text((fx0 + fx1) / 2, 214, "FMU 互通接口（FMI 2.0 / 3.0 Co-Simulation）· 统一变量表（规划 §9.8）", 13.5, C["orange"], weight="bold"))
    b.append(text((fx0 + fx1) / 2, 240, "A 的 ROM / 孪生 FMU → Simulink FMU Import；B 的 Simscape 孪生 → Simulink Compiler 导出 FMU → FMPy", 11.5, "#5a3206"))
    b.append(text((fx0 + fx1) / 2, 262, "两路线在 DR5 / DR6 上对表：稳态差 < 2%，阶跃时间常数差 < 10%", 11.5, "#5a3206"))
    for k in (0, 1):
        x = bx[k] + bwid / 2
        b.append(arrow(x, 140, x, 170, C["orange"], dash="4 3", mk="arrO", both=True))
    for k in (0, 2):
        x = bx[k] + bwid / 2
        b.append(arrow(x, 290, x, 320, C["orange"], dash="4 3", mk="arrO", both=True))
    rx0 = 1124
    b.append(rect(rx0, 56, 156, 348, fill=C["bg0"], stroke=C["navy"], rx=10, sw=1.4))
    rows = [(88, "对表与放行", 13.5, C["navy"], "bold"), (122, "DR5 孪生验收", 12.5, C["purple"], "bold"),
            (142, "对 CFD ≤ 5%", 11, "#2b3a47", "normal"), (160, "对试验 ≤ 10%", 11, "#2b3a47", "normal"),
            (178, "A/B 稳态差 < 2%", 11, "#2b3a47", "normal"), (214, "DR6 控制策略放行", 12.5, C["purple"], "bold"),
            (234, "SIL 零约束违约", 11, "#2b3a47", "normal"), (252, "HIL 经 E4 / ③", 11, "#2b3a47", "normal"),
            (288, "回路", 12.5, C["navy"], "bold"), (308, "R3 实测比对 → 再标定", 11, "#2b3a47", "normal"),
            (326, "R4 → 反哺 ③ 设计指标", 11, "#2b3a47", "normal"), (362, "调节：温升 6~10 K", 11, C["teal"], "bold"),
            (380, "负载 1100~1400 W", 11, C["teal"], "bold")]
    for y, s, sz, col, wt in rows:
        b.append(text(rx0 + 78, y, s, sz, col, weight=wt))
    b.append(arrow(bx[3] + bwid + 2, 97, rx0 - 2, 120, C["teal"], mk="arrT"))
    b.append(arrow(fx1 + 2, 230, rx0 - 2, 190, C["orange"], mk="arrO"))
    b.append(arrow(bx[3] + bwid + 2, 363, rx0 - 2, 240, C["purple"], mk="arrP"))
    b.append(text(1280, H - 12, "一维模型为共同源，FMU 为互通接口；选哪条路线为用户决策 Q-07（推荐 A 主 B 并行的双轨）。", 11.5, C["grey"], "end"))
    return svg_wrap(W, H, "".join(b), "数字孪生与孪生在环控制的两条并列路线")


# ---------- 图：分层架构 ----------
def chip_row(x, y, w, h, items, fill, stroke, size=12, dashed_from=None):
    out = []
    widths = [tw(s, size) + 22 for s in items]
    while size > 9 and sum(widths) + 8 * (len(items) + 1) > w:
        size -= 0.5
        widths = [tw(s, size) + 18 for s in items]
    gap = max(8.0, (w - sum(widths)) / (len(items) + 1))
    cx = x + gap
    for k, (s, cw) in enumerate(zip(items, widths)):
        dash = "5 3" if dashed_from is not None and k >= dashed_from else None
        out.append(rect(cx, y, cw, h, fill=fill, stroke=stroke, rx=5, dash=dash, sw=1.1))
        out.append(text(cx + cw / 2, y + h / 2 + size * 0.36, s, size, "#1d2b36"))
        cx += cw + gap
    return "".join(out)


def svg_arch():
    W, H = 1180, 600
    layers = [
        ("交互层", ["Cursor / Claude Code 对话", "冷板设计台 UI :8765", "md + html 报告（build_plan.py）", "门控看板（新）"], 3, "#eaf2fb"),
        ("智能体层", ["orchestrator（薄）", "cp-design（主责）", "ai-matlab（路线 B）", "librarian", "thermal-management"], None, "#e8f4f1"),
        ("技能层", ["design-loop", "cad-loop", "cfd-loop", "fluent-gui-capture", "oned-calc", "cfd-batch", "vv-loop", "twin-rom", "control-sim"], 4, "#f0f3e6"),
        ("工具适配层 MCP", ["cp-design MCP（8 工具）", "user-matlab MCP", "Ansys 适配（journal / PyFluent）", "FMU 互通", "DAQ 适配"], 3, "#fdf3e7"),
        ("求解层", ["Python 1D / ROM（A）", "MATLAB / Simscape（B）", "build123d", "SpaceClaim", "Fluent / Meshing", "Mechanical", "optiSLang", "AutoCAD 2024", "OpenFOAM（备）"], 8, "#f6eef6"),
        ("数据层", ["references 报告", "设计点注册表 D-001（新）", "memory", "runs/ + manifest（新）", "大文件索引", "Dify RAG"], None, "#eef1f4"),
    ]
    lx, lw, x1, w1 = 18, 128, 156, 860
    y, lh, gap = 18, 76, 16
    b = []
    for name, items, dash_from, bg in layers:
        b.append(rect(lx, y, lw + w1 + 10, lh, fill=bg, stroke=C["line"], rx=8, sw=1))
        b.append(text(lx + lw / 2, y + lh / 2 + 5, name, 13.5, C["navy"], weight="bold"))
        b.append(chip_row(x1, y + 20, w1, 36, items, "#fff", C["navy"], 11.5, dash_from))
        y += lh + gap
    for k in range(len(layers) - 1):
        yy = 18 + (k + 1) * (lh + gap) - gap
        b.append(arrow(lx + lw / 2, yy + 1, lx + lw / 2, yy + gap - 1, C["line"]))
    gx, gw = 1040, 124
    b.append(rect(gx, 18, gw, y - 18 - gap, fill="#fff5f5", stroke=C["red"], rx=8, sw=1.5))
    b.append(text(gx + gw / 2, 46, "人工闸门", 14, C["red"], weight="bold"))
    gates = ["① 技能安装", "② 记忆继承", "③ 资金 / 实物", "", "工程闸门（试行）", "E1 几何冻结", "E2 大算例", "E3 门控放行", "E4 实物动作"]
    gy = 82
    for g in gates:
        if g:
            bold = "bold" if g.startswith("工程") else "normal"
            col = C["grey"] if g.startswith("工程") else "#5a1f1f"
            b.append(text(gx + gw / 2, gy, g, 12, col, weight=bold))
        gy += 34
    b.append(text(lx, H - 8, "实线框：已有；虚线框：本规划新增或候选", 11, C["grey"], anchor="start"))
    return svg_wrap(W, H, "".join(b), "平台分层架构")


# ---------- 图：孪生在环安全架构 ----------
def svg_twin():
    W, H = 1080, 410
    bw, bh = 200, 70
    top = [("实体对象", "试验台 / 托盘 / CDU"), ("传感器", "T / P / Q / 红外"),
           ("状态估计与标定", "EKF / 滑窗 · R3"), ("数字孪生", "A：ROM FMU · B：Simscape")]
    bot = [("执行器", "仿真默认 · 真实需确认"), ("安全屏蔽 + E4 / ③", "硬限值 · 速率 · 看门狗 · 回退 PID"),
           ("控制器", "A：Python MPC/RL · B：Toolbox")]
    b = []
    xs = [30, 290, 550, 810]
    for (t, s), x in zip(top, xs):
        col = C["navy"] if t != "数字孪生" else C["purple"]
        b.append(rect(x, 60, bw, bh, fill="#fff", stroke=col, rx=8, sw=1.6))
        b.append(text(x + bw / 2, 88, t, 14, col, weight="bold"))
        b.append(text(x + bw / 2, 112, s, 11.2, C["grey"]))
    for k in range(3):
        b.append(arrow(xs[k] + bw + 2, 95, xs[k + 1] - 2, 95))
    bxs = [30, 420, 810]
    for (t, s), x in zip(bot, bxs):
        col = C["red"] if "安全" in t else (C["teal"] if t == "控制器" else C["navy"])
        b.append(rect(x, 240, bw, bh, fill="#fff", stroke=col, rx=8, sw=1.6))
        b.append(text(x + bw / 2, 268, t, 14, col, weight="bold"))
        b.append(text(x + bw / 2, 292, s, 10.8, C["grey"]))
    b.append(arrow(910, 132, 910, 238))
    b.append(text(918, 190, "预测 / 状态", 11.5, C["grey"], anchor="start"))
    b.append(arrow(808, 275, 622, 275))
    b.append(arrow(418, 275, 232, 275))
    b.append(arrow(130, 238, 130, 132))
    b.append(text(138, 190, "物理作用", 11.5, C["grey"], anchor="start"))
    b.append(f'<path d="M390,60 C390,20 860,20 905,58" fill="none" stroke="{C["purple"]}" '
             f'stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#arrP)"/>')
    b.append(text(640, 22, "试验数据 → 孪生在线再标定（R3）", 11.5, C["purple"]))
    stages = [("MIL", "孪生 FMU 闭环"), ("SIL", "Python / Simulink Test"), ("HIL", "台架泵阀（E4）")]
    sx = 150
    for k, (t, s) in enumerate(stages):
        b.append(rect(sx, 334, 230, 32, fill=C["bg3"], stroke=C["purple"], rx=16, sw=1.2))
        b.append(text(sx + 115, 355, f"{t} · {s}", 12, C["purple"], weight="bold"))
        if k < 2:
            b.append(arrow(sx + 232, 350, sx + 268, 350, C["purple"], mk="arrP"))
        sx += 270
    b.append(text(20, 396, "调节范围（D-001）：冷却液温升 6~10 K，负载 1100~1400 W；约束 ΔP ≤ 20 kPa、孔速 ≤ 2.0 m/s、HBM 近壁 ≤ 0.80 m/s。", 11.5, C["teal"], "start", "bold"))
    return svg_wrap(W, H, "".join(b), "孪生在环控制安全架构")


# ---------- 图：链式流程 ----------
def svg_chain(items, back_label, reject, title, W=1180):
    n = len(items)
    gap = 18
    bw = (W - 40 - gap * (n - 1)) / n
    b = []
    for k, (t, col) in enumerate(items):
        x = 20 + k * (bw + gap)
        b.append(rect(x, 40, bw, 62, fill="#fff", stroke=col, rx=8, sw=1.6))
        lines = t.split("\n")
        for j, ln in enumerate(lines):
            yy = 40 + 31 + (j - (len(lines) - 1) / 2) * 17 + 5
            size = 12.5 if j == 0 else 11
            while size > 8.5 and tw(ln, size) > bw - 8:
                size -= 0.5
            b.append(text(x + bw / 2, yy, ln, size, col if j == 0 else C["grey"],
                          weight="bold" if j == 0 else "normal"))
        if k < n - 1:
            b.append(arrow(x + bw + 1, 71, x + bw + gap - 1, 71))
    x_last = 20 + (n - 1) * (bw + gap) + bw / 2
    x_first = 20 + bw / 2
    if back_label:
        b.append(f'<path d="M{x_last},{104} C{x_last},{150} {x_first},{150} {x_first},{106}" fill="none" '
                 f'stroke="{C["teal"]}" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#arrT)"/>')
        b.append(text(x_first + (x_last - x_first) * 0.22, 160, back_label, 12, C["teal"], weight="bold"))
    if reject:
        k, lab = reject
        x = 20 + k * (bw + gap) + bw / 2
        b.append(arrow(x, 104, x, 188, C["red"], dash="5 3", mk="arrR"))
        b.append(text(x + 10, 205, lab, 12, C["red"], anchor="start"))
    return svg_wrap(W, 220, "".join(b), title)


def svg_chain_cad():
    items = [("设计点 yaml\nD-001", C["navy"]), ("一维 oned\n计算书", C["navy"]), ("规则门\nrules.py", C["navy"]),
             ("E1 人确认\n几何冻结", C["red"]), ("build123d\nSTEP + 命名面", C["navy"]), ("网格\nICEM / Meshing", C["navy"]),
             ("预检 + E2\n显存 / 许可", C["red"]), ("Fluent\n批处理求解", C["navy"]), ("解析入账\nE2 / E3 证据", C["navy"]),
             ("与 1D 对表\nR1 判定", C["orange"])]
    return svg_chain(items, "R1：不达标 → 回 ③/④（S39 自动扫描 / 优化）", None, "CAD → CFD 自动化链路")


def svg_vv():
    items = [("模型预测\n1D / CFD / 孪生", C["navy"]), ("试验测量\nTTV · u_D", C["navy"]), ("偏差 ε\nu_val 合成", C["orange"]),
             ("ε ≤ 15%\nV5 通过", C["teal"]), ("DR4 闸门包\n人签字", C["teal"])]
    return svg_chain(items, "", (2, "ε > 15% → R2 工单 → 偏差分解 → 反标定 → 回 ③"), "V&V 闭环")


def svg_govern():
    items = [("步骤产出", C["navy"]), ("用户验证\n通过 / 修改", C["navy"]), ("候选登记\ncandidate", C["orange"]),
             ("人工闸门\n① 技能 / ② 记忆", C["red"]), ("入库\nsemantic / skill", C["teal"]),
             ("继承筛选\n≥0.6 · 未过期", C["teal"]), ("GC 标记\nexpired", C["grey"])]
    return svg_chain(items, "", (1, "不通过 → 只留 episodic 或丢弃"), "技能与记忆沉淀流程")


def svg_steploop():
    items = [("用户指令\n执行 Sxx", C["navy"]), ("AI 执行\n只写候选区", C["navy"]), ("产出\n报告 + 证据等级", C["navy"]),
             ("用户验证\n通过/修改/退回/暂停", C["orange"]), ("沉淀候选\nskill / memory", C["orange"]),
             ("闸门确认入库\n字段齐全", C["red"]), ("提交建议\n人执行 push", C["teal"])]
    return svg_chain(items, "下一条指令", (3, "修改 / 退回 → 同一步重做或撤回"), "按指令分步实施循环")


# ---------- 图：甘特 ----------
PHASE_COL = {"P0": "#5d6b78", "P1": "#0e8a7a", "P2": "#2f7fb8", "P3": "#c56a12", "P4": "#8a6d1d",
             "P5": "#b23a3a", "P6a": "#6b4fa0", "P6b": "#8e3b8a", "P7": "#3d5a80"}


def svg_gantt(src: str):
    rows = []
    for ln in src.strip().splitlines():
        p = [s.strip() for s in ln.split("|")]
        if len(p) == 5:
            rows.append((p[0], p[1], int(p[2]), int(p[3]), p[4]))
    weeks = max(s + max(d, 1) - 1 for _, _, s, d, _ in rows)
    lab, wk, rh, top = 300, 21.5, 24, 58
    W = lab + weeks * wk + 80
    H = top + len(rows) * rh + 34
    b = [rect(0, 0, W, H, fill="#fff", stroke="#fff", rx=0)]
    for w in range(1, weeks + 1):
        x = lab + (w - 1) * wk
        if w % 2 == 0:
            b.append(f'<rect x="{x:.1f}" y="{top - 6}" width="{wk:.1f}" height="{len(rows) * rh + 6}" fill="#f6f8fa"/>')
        b.append(text(x + wk / 2, top - 12, f"{w}", 9.5, C["grey"]))
    prev = None
    for w in range(1, weeks + 1):
        d = W1 + dt.timedelta(weeks=w - 1)
        key = (d.year, d.month)
        if key != prev:
            x = lab + (w - 1) * wk
            b.append(f'<line x1="{x:.1f}" y1="14" x2="{x:.1f}" y2="{top + len(rows) * rh}" stroke="#d6dde3" stroke-width="1"/>')
            b.append(text(x + 4, 26, f"{d.year}-{d.month:02d}", 11, C["navy"], anchor="start", weight="bold"))
            prev = key
    sf = dt.date(2027, 2, 6)
    xs = lab + (sf - W1).days / 7.0 * wk
    b.append(f'<line x1="{xs:.1f}" y1="34" x2="{xs:.1f}" y2="{top + len(rows) * rh}" stroke="{C["red"]}" '
             f'stroke-width="1.2" stroke-dasharray="4 3"/>')
    b.append(text(xs + 4, top + 16, "春节", 10.5, C["red"], anchor="start"))
    cur = "P0"
    for k, (pid, name, s, d, kind) in enumerate(rows):
        y = top + k * rh
        if pid in PHASE_COL:
            cur = pid
        col = PHASE_COL.get(cur, C["grey"])
        if kind == "phase":
            b.append(text(10, y + 16, name, 12, col, anchor="start", weight="bold"))
            x = lab + (s - 1) * wk
            b.append(f'<rect x="{x:.1f}" y="{y + 5}" width="{d * wk:.1f}" height="{rh - 10}" rx="4" fill="{col}"/>')
            b.append(text(x + d * wk + 4, y + 16, f"W{s}–W{s + d - 1}", 9.5, C["grey"], anchor="start"))
        elif kind == "task":
            b.append(text(22, y + 16, name, 11, "#33424f", anchor="start"))
            x = lab + (s - 1) * wk
            b.append(f'<rect x="{x:.1f}" y="{y + 7}" width="{d * wk:.1f}" height="{rh - 14}" rx="3" fill="{col}" '
                     f'fill-opacity="0.38" stroke="{col}" stroke-width="1"/>')
        else:
            b.append(text(22, y + 16, "◆ " + name, 11, "#8a4b08", anchor="start", weight="bold"))
            cx = lab + s * wk
            cy = y + rh / 2
            b.append(f'<polygon points="{cx:.1f},{cy - 8} {cx + 8:.1f},{cy} {cx:.1f},{cy + 8} {cx - 8:.1f},{cy}" '
                     f'fill="#f2b33d" stroke="#8a4b08" stroke-width="1.2"/>')
            b.append(text(cx + 11, cy + 4, f"W{s}", 9.5, "#8a4b08", anchor="start"))
        b.append(f'<line x1="8" y1="{y + rh}" x2="{W - 8}" y2="{y + rh}" stroke="#eef1f4" stroke-width="1"/>')
    end = W1 + dt.timedelta(weeks=weeks) - dt.timedelta(days=1)
    b.append(text(10, H - 10, f"W1 = {W1.isoformat()}（周一），W{weeks} 结束于 {end.isoformat()}。条形为阶段，浅色为子任务，菱形为门控。",
                  11, C["grey"], anchor="start"))
    return svg_wrap(int(W), int(H), "".join(b), "甘特图")


FIGS = {"flow": svg_flow, "routes": svg_routes, "arch": svg_arch, "twin": svg_twin, "chain": svg_chain_cad,
        "vv": svg_vv, "govern": svg_govern, "steploop": svg_steploop}


# ---------- md → html ----------
def convert(md_text: str):
    figs = {}

    def repl(m):
        name, body = m.group(1), m.group(2)
        token = f"FIGTOKEN{len(figs)}X"
        figs[token] = svg_gantt(body) if name == "gantt" else FIGS[name]()
        return f"\n\n{token}\n\n"

    src = re.sub(r"```svg:(\w+)\n(.*?)\n```", repl, md_text, flags=re.S)
    md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                           extension_configs={"toc": {"slugify": slugify_unicode, "toc_depth": "1-4"}})
    body = md.convert(src)
    for token, svg in figs.items():
        body = body.replace(f"<p>{token}</p>", f'<figure class="fig">{svg}</figure>')
    body = re.sub(r'href="([^"#:]+?)\.md(#[^"]*)?"', lambda m: f'href="{m.group(1)}.html{m.group(2) or ""}"', body)
    body = body.replace("<table>", '<div class="tbl"><table>').replace("</table>", "</table></div>")
    return body, md.toc_tokens


def flat(tokens, out=None):
    out = [] if out is None else out
    for t in tokens:
        out.append(t)
        flat(t.get("children", []), out)
    return out


def toc_html(tokens):
    items = [t for t in flat(tokens) if 2 <= t["level"] <= 4]
    root = {"level": 1, "children": []}
    stack = [root]
    for t in items:
        node = {"level": t["level"], "id": t["id"], "name": t["name"], "children": []}
        while stack[-1]["level"] >= node["level"]:
            stack.pop()
        stack[-1]["children"].append(node)
        stack.append(node)

    def render(nodes, depth):
        if not nodes:
            return ""
        parts = [f'<ul class="lv{depth}">']
        for n in nodes:
            parts.append(f'<li><a href="#{n["id"]}" data-id="{n["id"]}">{n["name"]}</a>'
                         f'{render(n["children"], depth + 1)}</li>')
        parts.append("</ul>")
        return "".join(parts)

    return render(root["children"], 1)


CSS = r"""
:root{--navy:#123b5d;--teal:#0e8a7a;--ink:#1d2b36;--muted:#5d6b78;--line:#dfe5ea;--bg:#f7f9fb;--side:304px;--accent:#c56a12}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"Microsoft YaHei","PingFang SC","Noto Sans CJK SC","Segoe UI",sans-serif;color:var(--ink);background:var(--bg);line-height:1.72;font-size:15px}
#sidebar{position:fixed;top:0;left:0;bottom:0;width:var(--side);background:#0f2f4a;color:#dce6ee;display:flex;flex-direction:column;z-index:20;transition:transform .25s ease;box-shadow:2px 0 10px rgba(0,0,0,.12)}
body.toc-hidden #sidebar{transform:translateX(calc(-1 * var(--side)))}
.side-head{padding:16px 16px 10px;border-bottom:1px solid rgba(255,255,255,.1)}
.side-title{font-weight:700;font-size:14.5px;color:#fff;line-height:1.45}
.side-sub{font-size:12px;color:#9fb6c8;margin-top:4px}
.side-tools{display:flex;gap:6px;margin-top:10px}
.side-tools button{flex:1;background:#1c4466;color:#dce6ee;border:1px solid #2c5a80;border-radius:5px;font-size:12px;padding:4px 0;cursor:pointer}
.side-tools button:hover{background:#25547c}
#tocFilter{width:100%;margin-top:8px;padding:6px 9px;border-radius:5px;border:1px solid #2c5a80;background:#0b2539;color:#e8f0f6;font-size:12.5px;outline:none}
#toc{overflow-y:auto;flex:1;padding:8px 6px 24px}
#toc ul{list-style:none;margin:0;padding:0}
#toc ul ul{display:none;padding-left:14px}
#toc li.open>ul{display:block}
#toc li{position:relative}
#toc a{display:block;padding:4px 8px 4px 22px;color:#c9d7e2;text-decoration:none;border-radius:5px;font-size:13px;line-height:1.45}
#toc ul.lv1>li>a{font-weight:600;color:#e7eff5}
#toc a:hover{background:rgba(255,255,255,.07);color:#fff}
#toc a.active{background:#1f6f8f;color:#fff}
#toc .caret{position:absolute;left:2px;top:3px;width:18px;height:20px;border:0;background:transparent;color:#8fb0c7;cursor:pointer;font-size:11px;padding:0;transition:transform .15s}
#toc li.open>.caret{transform:rotate(90deg)}
#toc li.hide{display:none}
#tocToggle{position:fixed;top:12px;left:calc(var(--side) + 12px);z-index:30;background:var(--navy);color:#fff;border:0;border-radius:6px;padding:7px 11px;font-size:13px;cursor:pointer;box-shadow:0 2px 6px rgba(0,0,0,.18);transition:left .25s ease}
body.toc-hidden #tocToggle{left:12px}
main{margin-left:var(--side);transition:margin-left .25s ease;padding:30px 48px 80px}
body.toc-hidden main{margin-left:0}
.doc{max-width:1240px;margin:0 auto;background:#fff;border:1px solid var(--line);border-radius:10px;padding:34px 46px 50px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
h1{font-size:27px;color:var(--navy);margin:6px 0 16px;line-height:1.35;border-bottom:3px solid var(--teal);padding-bottom:12px}
h2{font-size:21px;color:var(--navy);margin:42px 0 14px;padding:8px 12px;background:linear-gradient(90deg,#e9f2f8,#fff);border-left:5px solid var(--navy);border-radius:4px}
h3{font-size:17px;color:#18496f;margin:28px 0 10px;padding-bottom:4px;border-bottom:1px dashed var(--line)}
h4{font-size:15px;color:#1f5a7a;margin:20px 0 8px}
h1,h2,h3,h4{scroll-margin-top:16px}
p{margin:8px 0 12px}
a{color:#1a6aa0}
code{font-family:Consolas,"Cascadia Mono",monospace;font-size:.88em;background:#f1f4f7;border:1px solid #e3e8ed;border-radius:4px;padding:1px 5px}
pre{background:#0f2233;color:#e2ecf3;border-radius:8px;padding:14px 16px;overflow:auto;font-size:13px;line-height:1.55}
pre code{background:transparent;border:0;color:inherit;padding:0}
blockquote{margin:14px 0;padding:10px 16px;background:#f2f8f7;border-left:4px solid var(--teal);border-radius:4px;color:#21413c}
blockquote p{margin:4px 0}
.tbl{overflow-x:auto;margin:12px 0 18px}
table{border-collapse:collapse;width:100%;font-size:13.5px;line-height:1.55}
th{background:#123b5d;color:#fff;font-weight:600;text-align:left;padding:7px 10px;white-space:nowrap}
td{padding:6px 10px;border-bottom:1px solid var(--line);vertical-align:top}
tr:nth-child(even) td{background:#f8fafc}
tr:hover td{background:#eef5fa}
ul,ol{padding-left:24px}
li{margin:3px 0}
figure.fig{margin:16px 0 4px;padding:12px;background:#fbfcfd;border:1px solid var(--line);border-radius:8px;overflow-x:auto}
.fig-svg{width:100%;height:auto;min-width:760px;display:block}
p>em:only-child{display:block;text-align:center;color:var(--muted);font-size:13px;font-style:normal;margin-top:2px}
.meta{display:flex;flex-wrap:wrap;gap:8px;margin:-4px 0 18px}
.meta span{background:#eef4f8;border:1px solid #d9e4ec;color:#29506d;border-radius:20px;padding:2px 11px;font-size:12.5px}
#toTop{position:fixed;right:20px;bottom:22px;background:var(--teal);color:#fff;border:0;border-radius:50%;width:40px;height:40px;font-size:18px;cursor:pointer;opacity:0;pointer-events:none;transition:opacity .2s;box-shadow:0 2px 8px rgba(0,0,0,.2)}
#toTop.show{opacity:.9;pointer-events:auto}
#progress{position:fixed;top:0;left:0;height:3px;background:var(--accent);z-index:40;width:0}
.foot{margin-top:40px;padding-top:12px;border-top:1px solid var(--line);color:var(--muted);font-size:12.5px}
@media (max-width:980px){main{margin-left:0;padding:56px 12px 60px}.doc{padding:20px 18px}#sidebar{transform:translateX(calc(-1 * var(--side)))}body.toc-open #sidebar{transform:none}#tocToggle{left:12px}body.toc-open #tocToggle{left:calc(var(--side) + 12px)}}
@media print{#sidebar,#tocToggle,#toTop,#progress{display:none!important}main{margin:0!important;padding:0}.doc{border:0;box-shadow:none;max-width:none}h2{break-after:avoid}figure,table{break-inside:avoid}}
"""

JS = r"""
(function () {
  "use strict";
  var body = document.body;
  var toc = document.getElementById("toc");
  var toggle = document.getElementById("tocToggle");
  var filter = document.getElementById("tocFilter");
  var mobile = function () { return window.matchMedia("(max-width:980px)").matches; };
  var KEY = "aidcPlanV11TocHidden";

  function store(v) { try { localStorage.setItem(KEY, v ? "1" : "0"); } catch (e) {} }
  function load() { try { return localStorage.getItem(KEY) === "1"; } catch (e) { return false; } }

  function setHidden(h) {
    if (mobile()) {
      body.classList.toggle("toc-open", !h);
    } else {
      body.classList.toggle("toc-hidden", h);
      store(h);
    }
    toggle.textContent = h ? "☰ 目录" : "◀ 收起";
    toggle.setAttribute("aria-expanded", h ? "false" : "true");
  }
  function isHidden() { return mobile() ? !body.classList.contains("toc-open") : body.classList.contains("toc-hidden"); }

  setHidden(mobile() ? true : load());
  toggle.addEventListener("click", function () { setHidden(!isHidden()); });

  var lis = toc.querySelectorAll("li");
  Array.prototype.forEach.call(lis, function (li) {
    var sub = null;
    for (var i = 0; i < li.children.length; i++) { if (li.children[i].tagName === "UL") { sub = li.children[i]; } }
    if (sub) {
      var b = document.createElement("button");
      b.className = "caret";
      b.type = "button";
      b.setAttribute("aria-label", "展开或收起");
      b.textContent = "▶";
      b.addEventListener("click", function (e) { e.preventDefault(); e.stopPropagation(); li.classList.toggle("open"); });
      li.insertBefore(b, li.firstChild);
    }
  });
  Array.prototype.forEach.call(toc.querySelectorAll("ul.lv1 > li"), function (li) { li.classList.add("open"); });

  document.getElementById("expandAll").addEventListener("click", function () {
    Array.prototype.forEach.call(lis, function (li) { if (li.querySelector("ul")) { li.classList.add("open"); } });
  });
  document.getElementById("collapseAll").addEventListener("click", function () {
    Array.prototype.forEach.call(lis, function (li) { li.classList.remove("open"); });
  });

  filter.addEventListener("input", function () {
    var q = filter.value.trim().toLowerCase();
    Array.prototype.forEach.call(lis, function (li) { li.classList.remove("hide"); });
    if (!q) { return; }
    var all = Array.prototype.slice.call(lis).reverse();
    all.forEach(function (li) {
      var a = li.querySelector("a");
      var self = a && a.textContent.toLowerCase().indexOf(q) >= 0;
      var kid = li.querySelector("li:not(.hide)") !== null;
      if (self || kid) { li.classList.add("open"); } else { li.classList.add("hide"); }
    });
  });

  var links = toc.querySelectorAll("a[data-id]");
  var map = {};
  Array.prototype.forEach.call(links, function (a) {
    map[a.getAttribute("data-id")] = a;
    a.addEventListener("click", function () { if (mobile()) { setHidden(true); } });
  });
  var heads = Array.prototype.filter.call(document.querySelectorAll("main h2[id], main h3[id], main h4[id]"), function (h) { return map[h.id]; });

  var current = null;
  function activate(id) {
    if (id === current) { return; }
    current = id;
    Array.prototype.forEach.call(links, function (a) { a.classList.remove("active"); });
    var a = map[id];
    if (!a) { return; }
    a.classList.add("active");
    var p = a.parentNode;
    while (p && p !== toc) { if (p.tagName === "LI") { p.classList.add("open"); } p = p.parentNode; }
    var r = a.getBoundingClientRect(), t = toc.getBoundingClientRect();
    if (r.top < t.top + 10 || r.bottom > t.bottom - 10) { toc.scrollTop += r.top - t.top - t.height / 3; }
  }

  var bar = document.getElementById("progress");
  var top = document.getElementById("toTop");
  var ticking = false;
  function onScroll() {
    ticking = false;
    var y = window.scrollY || document.documentElement.scrollTop;
    var max = document.documentElement.scrollHeight - window.innerHeight;
    bar.style.width = (max > 0 ? (y / max) * 100 : 0) + "%";
    top.classList.toggle("show", y > 600);
    var id = null;
    for (var i = 0; i < heads.length; i++) {
      if (heads[i].getBoundingClientRect().top - 90 <= 0) { id = heads[i].id; } else { break; }
    }
    if (!id && heads.length) { id = heads[0].id; }
    if (id) { activate(id); }
  }
  window.addEventListener("scroll", function () { if (!ticking) { ticking = true; window.requestAnimationFrame(onScroll); } }, { passive: true });
  window.addEventListener("resize", function () { setHidden(mobile() ? true : load()); });
  top.addEventListener("click", function () { window.scrollTo({ top: 0, behavior: "smooth" }); });
  document.addEventListener("keydown", function (e) {
    if (e.target && (e.target.tagName === "INPUT" || e.target.tagName === "TEXTAREA")) { return; }
    if (e.key === "t" || e.key === "T") { setHidden(!isHidden()); }
  });
  onScroll();
})();
"""


def page(title: str, sub: str, body: str, toc: str, meta: list[str]) -> str:
    meta_html = "".join(f"<span>{esc(m)}</span>" for m in meta)
    body = body.replace("</h1>", f'</h1><div class="meta">{meta_html}</div>', 1)
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<style>{CSS}</style>
</head>
<body>
<div id="progress"></div>
<nav id="sidebar" aria-label="目录">
  <div class="side-head">
    <div class="side-title">{esc(title)}</div>
    <div class="side-sub">{esc(sub)}</div>
    <div class="side-tools"><button type="button" id="expandAll">全部展开</button><button type="button" id="collapseAll">全部收起</button></div>
    <input id="tocFilter" type="search" placeholder="筛选目录…" aria-label="筛选目录">
  </div>
  <div id="toc">{toc}</div>
</nav>
<button type="button" id="tocToggle" aria-controls="sidebar" title="收起 / 展开目录（快捷键 T）">◀ 收起</button>
<main><article class="doc">
{body}
<div class="foot">由 docs/plan/build_plan.py 从同名 md 生成 · 单文件自包含，离线可用 · md 为正文唯一来源</div>
</article></main>
<button type="button" id="toTop" title="回到顶部">↑</button>
<script>{JS}</script>
</body>
</html>
"""


def build() -> list[Path]:
    outs = []
    for name in DOCS:
        src = HERE / name
        md_text = src.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", md_text, flags=re.M).group(1).strip()
        body, tokens = convert(md_text)
        short = title.split("·")[-1].strip()
        meta = ["cp-design", "v1.1 · 2026-10-02", short, "合并定稿草案 · 待评审", "D-001 已决策"]
        out = src.with_suffix(".html")
        out.write_text(page(title, "AIDCtms · coolingplate · practice01_0926", body, toc_html(tokens), meta),
                       encoding="utf-8")
        print(f"{out.name}  {out.stat().st_size / 1024:.1f} KB")
        outs.append(out)
    ASSETS.mkdir(exist_ok=True)
    svg = svg_flow(standalone=True)
    fp = ASSETS / FLOW_SVG
    fp.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + svg, encoding="utf-8")
    print(f"assets/{fp.name}  {fp.stat().st_size / 1024:.1f} KB")
    return outs


# ---------- 自检 ----------
class _Scan(HTMLParser):
    KNOWN = set("html head meta title style body div nav input button main article h1 h2 h3 h4 h5 h6 p a ul ol li "
                "table thead tbody tr th td code pre em strong blockquote figure svg defs marker path rect text line "
                "polygon g script span br hr img sup sub".split())

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.hrefs, self.ext, self.unknown, self.scripts = [], [], [], set(), []
        self._in_script = False

    def handle_starttag(self, tag, attrs):
        if tag not in self.KNOWN:
            self.unknown.add(tag)
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        for k in ("href", "src", "data", "action"):
            v = a.get(k)
            if v is None:
                continue
            if k == "href":
                self.hrefs.append(v)
            if re.match(r"^(https?:)?//", v) or v.startswith(("http:", "https:", "data:", "ftp:")):
                self.ext.append(f"{tag}[{k}]={v}")
        if tag == "script":
            self._in_script = True
            if a.get("src"):
                self.ext.append(f"script[src]={a['src']}")

    def handle_endtag(self, tag):
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_script:
            self.scripts.append(data)


def check(outs: list[Path]) -> int:
    bad = 0
    node = shutil.which("node")
    for p in outs:
        s = p.read_text(encoding="utf-8")
        sc = _Scan()
        sc.feed(s)
        dup = sorted({i for i in sc.ids if sc.ids.count(i) > 1})
        idset = set(sc.ids)
        dead = [h for h in sc.hrefs if h.startswith("#") and h[1:] not in idset]
        css_ext = re.findall(r"@import|url\(\s*['\"]?(?:https?:)?//", s)
        local = [h for h in sc.hrefs if not h.startswith("#")]
        heads = len(re.findall(r"<h[2-4] id=", s))
        tocs = len(re.findall(r'data-id="', s))
        print(f"\n[{p.name}]")
        print(f"  外部资源引用: {len(sc.ext) + len(css_ext)} {sc.ext[:5]}")
        print(f"  非锚点链接: {local}")
        print(f"  ID 总数 {len(sc.ids)}，重复 {len(dup)} {dup[:10]}")
        print(f"  目录项 {tocs} / h2–h4 标题 {heads}；锚点不可达 {len(dead)} {dead[:10]}")
        print(f"  未知标签: {sorted(sc.unknown)}")
        print(f"  内联 SVG: {s.count('<svg ')}")
        if sc.ext or css_ext or dup or dead or sc.unknown or tocs != heads:
            bad += 1
        js = "\n".join(sc.scripts)
        if node:
            with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
                f.write(js)
            r = subprocess.run([node, "--check", f.name], capture_output=True, text=True)
            Path(f.name).unlink(missing_ok=True)
            print(f"  node --check JS: {'通过' if r.returncode == 0 else '失败 ' + r.stderr.strip()}")
            bad += r.returncode != 0
        else:
            print("  node 未找到，跳过 JS 语法检查")
    print(f"\n自检结果：{'全部通过' if bad == 0 else f'{bad} 项未通过'}")
    return bad


def main() -> int:
    outs = build()
    if "--check" in sys.argv:
        return 1 if check(outs) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
