# -*- coding: utf-8 -*-
"""把 planning/ 下的规划 md 生成单文件自包含 html。

md 是唯一正文来源。```svg:<name>``` 代码块在 html 里换成内联 SVG，
md 里保留文字示意；svg:gantt 的数据行直接驱动甘特图。
html 不引用任何外部资源：CSS / JS / SVG 全部内联。

用法：python build_plan.py      （需要 markdown 包，系统 Python 已有 3.10）
"""
from __future__ import annotations

import datetime as dt
import html
import re
import sys
from pathlib import Path

import markdown
from markdown.extensions.toc import slugify_unicode

HERE = Path(__file__).resolve().parent
DOCS = ["项目规划_v1.0_20261002.md", "实施计划_v1.0_20261002.md"]
W1 = dt.date(2026, 10, 5)
FONT = "'Microsoft YaHei','PingFang SC','Noto Sans CJK SC',sans-serif"

C = {
    "navy": "#123b5d", "teal": "#0e8a7a", "orange": "#c56a12", "purple": "#6b4fa0",
    "red": "#b23a3a", "grey": "#5d6b78", "line": "#9fb0bf", "bg1": "#eef6f5",
    "bg2": "#fdf3e7", "bg3": "#f2eef9", "bg0": "#f4f7fa",
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


def arrow(x1, y1, x2, y2, color=C["grey"], dash=None, mk="arr"):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{color}" '
            f'stroke-width="1.6"{d} marker-end="url(#{mk})"/>')


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


def svg_wrap(w, h, body, title):
    _SVG_SEQ[0] += 1
    pfx = f"f{_SVG_SEQ[0]}"
    inner = (defs() + body).replace('id="arr', f'id="{pfx}arr').replace("url(#arr", f"url(#{pfx}arr")
    return (f'<svg class="fig-svg" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}" '
            f'xmlns="http://www.w3.org/2000/svg" font-family="{FONT}">{inner}</svg>')


# ---------- 图：门控流程 ----------
def svg_flow():
    stages = [
        ("① 需求与输入", "ICD/规格抽取", "输入追溯矩阵", "DR0", "cp-design", "librarian"),
        ("② 概念与选型", "文献/专利检索", "权衡矩阵", "DR1", "cp-design", "librarian"),
        ("③ 性能设计", "热阻预算", "设计窗检查", "DR2", "cp-design", ""),
        ("④ 一维计算", "网络法 + UQ", "DOE/敏感性", "DR2", "cp-design", "ai-matlab"),
        ("⑤ 三维仿真", "Fluent 批处理", "GCI/契合性", "DR3·仿真", "cp-design", ""),
        ("⑥ 机械与图纸", "参数化 CAD", "GD&T/出图", "DR3·图纸", "cp-design", ""),
        ("⑦ 样件与试验", "DOE/DAQ", "V&V 20", "DR4", "cp-design", ""),
        ("⑧ 数字孪生", "ROM/FMU", "在线校准", "DT 门", "cp-design", "ai-matlab"),
        ("⑨ 在环控制", "MPC/RL", "MIL→SIL→HIL", "CTRL 门", "ai-matlab", "cp-design"),
    ]
    W, H = 1180, 470
    bw, gap, x0, y0, bh = 112, 16, 22, 62, 92
    b = []
    groups = [(0, 3, C["teal"], C["bg1"], "v2.0 已完成 ①–④"),
              (4, 6, C["orange"], C["bg2"], "本平台重点补齐 ⑤–⑦"),
              (7, 8, C["purple"], C["bg3"], "新增 ⑧⑨")]
    for i0, i1, col, bg, lab in groups:
        gx = x0 + i0 * (bw + gap) - 8
        gw = (i1 - i0 + 1) * bw + (i1 - i0) * gap + 16
        b.append(rect(gx, 30, gw, 215, fill=bg, stroke=col, rx=10, dash="6 4", sw=1.4))
        b.append(text(gx + gw / 2, 50, lab, 12.5, col, weight="bold"))
    for i, (t, s1, s2, gate, a1, a2) in enumerate(stages):
        x = x0 + i * (bw + gap)
        col = C["teal"] if i < 4 else (C["orange"] if i < 7 else C["purple"])
        b.append(rect(x, y0, bw, bh, fill="#fff", stroke=col, rx=7, sw=1.6))
        b.append(text(x + bw / 2, y0 + 24, t, 13, C["navy"], weight="bold"))
        b.append(text(x + bw / 2, y0 + 50, s1, 11, C["grey"]))
        b.append(text(x + bw / 2, y0 + 70, s2, 11, C["grey"]))
        if i < len(stages) - 1:
            b.append(arrow(x + bw + 1, y0 + bh / 2, x + bw + gap - 1, y0 + bh / 2))
        cx, cy = x + bw / 2, 200
        b.append(f'<line x1="{cx}" y1="{y0 + bh}" x2="{cx}" y2="{cy - 20}" stroke="{C["line"]}" stroke-width="1.2"/>')
        b.append(f'<polygon points="{cx},{cy - 20} {cx + 50},{cy} {cx},{cy + 20} {cx - 50},{cy}" '
                 f'fill="#fff8e6" stroke="{C["orange"]}" stroke-width="1.4"/>')
        b.append(text(cx, cy + 4, gate, 11.5, "#8a4b08", weight="bold"))
        b.append(rect(x + 4, 400, bw - 8, 46, fill=C["bg0"], stroke=C["line"], rx=5, sw=1))
        b.append(text(x + bw / 2, 419, a1, 11, C["navy"], weight="bold"))
        if a2:
            b.append(text(x + bw / 2, 436, "+ " + a2, 10.5, C["grey"]))
    xc = lambda i: x0 + i * (bw + gap) + bw / 2
    # R1：⑤ DR3 → ③/④
    b.append(f'<path d="M{xc(4)},{220} C{xc(4)},{290} {xc(2) + 60},{290} {xc(2) + 60},{246}" fill="none" '
             f'stroke="{C["red"]}" stroke-width="1.8" stroke-dasharray="7 4" marker-end="url(#arrR)"/>')
    b.append(text((xc(2) + xc(4)) / 2 + 30, 300, "R1 仿真不达标 → 回 ③/④ 改几何（孔径、阵列密度、TIM2）", 12, C["red"], weight="bold"))
    # R2：⑦ → ③
    b.append(f'<path d="M{xc(6)},{220} C{xc(6)},{360} {xc(2)},{360} {xc(2)},{246}" fill="none" '
             f'stroke="{C["red"]}" stroke-width="1.8" stroke-dasharray="7 4" marker-end="url(#arrR)"/>')
    b.append(text((xc(2) + xc(6)) / 2, 372, "R2 试验与仿真偏差 > 15% → 修正模型并回 ③（V&V 闭环）", 12, C["red"], weight="bold"))
    b.append(text(14, 392, "主责 / 协作智能体", 11, C["grey"], anchor="start"))
    return svg_wrap(W, H, "".join(b), "门控流程与两条迭代回路")


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
        ("交互层", ["Cursor / Claude Code 对话", "冷板设计台 UI :8765", "md + html 报告 / 规划", "门控看板（新）"], 3, "#eaf2fb"),
        ("智能体编排层", ["orchestrator（薄）", "cp-design（主责）", "ai-matlab", "librarian", "thermal-management"], None, "#e8f4f1"),
        ("技能层", ["design-loop", "cad-loop", "cfd-loop", "fluent-gui-capture", "oned-network", "cfd-batch", "vv20", "rom-fmu", "ctrl-mil"], 4, "#f0f3e6"),
        ("工具适配层 MCP", ["cp-design MCP（8 工具）", "user-matlab MCP", "Ansys 适配（journal / PyFluent / SpaceClaim）", "DAQ 适配", "报告生成"], 2, "#fdf3e7"),
        ("求解与工具层", ["Python 一维", "MATLAB / Simscape", "build123d", "SpaceClaim", "Fluent / Meshing", "Mechanical", "optiSLang", "AutoCAD", "测试台 DAQ"], None, "#f6eef6"),
        ("知识与数据层", ["references 报告", "设计点注册表（新）", "memory", "runs/ 算例包", "大文件索引", "Dify RAG"], None, "#eef1f4"),
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
    gates = ["① 技能安装", "② 记忆继承", "③ 资金动作", "", "建议工程闸门", "E1 几何冻结", "E2 大算例", "E3 门控放行", "E4 实物动作"]
    gy = 82
    for g in gates:
        if g:
            bold = "bold" if g == "建议工程闸门" else "normal"
            col = C["grey"] if g == "建议工程闸门" else "#5a1f1f"
            b.append(text(gx + gw / 2, gy, g, 12, col, weight=bold))
        gy += 34
    b.append(text(lx, H - 8, "实线框：已有；虚线框：本规划新增或候选", 11, C["grey"], anchor="start"))
    return svg_wrap(W, H, "".join(b), "平台分层架构")


# ---------- 图：孪生在环 ----------
def svg_twin():
    W, H = 1080, 380
    bw, bh = 200, 70
    top = [("实体对象", "测试台 / CDU + 冷板"), ("传感器", "T / P / Q / 红外"),
           ("状态估计", "EKF / 数据管道"), ("数字孪生 ROM", "FMU · 一维 + 代理")]
    bot = [("执行器", "泵 / 阀 / 加热"), ("安全屏蔽 + 闸门 E4", "联锁 · 约束投影"),
           ("控制器", "PID / MPC / RL")]
    b = []
    xs = [30, 290, 550, 810]
    for (t, s), x in zip(top, xs):
        col = C["navy"] if t != "数字孪生 ROM" else C["purple"]
        b.append(rect(x, 60, bw, bh, fill="#fff", stroke=col, rx=8, sw=1.6))
        b.append(text(x + bw / 2, 88, t, 14, col, weight="bold"))
        b.append(text(x + bw / 2, 112, s, 11.5, C["grey"]))
    for k in range(3):
        b.append(arrow(xs[k] + bw + 2, 95, xs[k + 1] - 2, 95))
    bxs = [30, 420, 810]
    for (t, s), x in zip(bot, bxs):
        col = C["red"] if "安全" in t else (C["teal"] if t == "控制器" else C["navy"])
        b.append(rect(x, 240, bw, bh, fill="#fff", stroke=col, rx=8, sw=1.6))
        b.append(text(x + bw / 2, 268, t, 14, col, weight="bold"))
        b.append(text(x + bw / 2, 292, s, 11.5, C["grey"]))
    b.append(arrow(910, 132, 910, 238))
    b.append(text(918, 190, "预测 / 状态", 11.5, C["grey"], anchor="start"))
    b.append(arrow(808, 275, 622, 275))
    b.append(arrow(418, 275, 232, 275))
    b.append(arrow(130, 238, 130, 132))
    b.append(text(138, 190, "物理作用", 11.5, C["grey"], anchor="start"))
    b.append(f'<path d="M650,132 C650,200 760,200 830,236" fill="none" stroke="{C["purple"]}" '
             f'stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#arrP)"/>')
    b.append(f'<path d="M390,60 C390,20 860,20 905,58" fill="none" stroke="{C["purple"]}" '
             f'stroke-width="1.5" stroke-dasharray="6 4" marker-end="url(#arrP)"/>')
    b.append(text(640, 22, "试验数据 → ROM 在线再标定", 11.5, C["purple"]))
    stages = [("MIL", "Simulink + 孪生 FMU"), ("SIL", "生成代码 / FMU 联合仿真"), ("HIL", "测试台泵阀 + 实时控制器")]
    sx = 150
    for k, (t, s) in enumerate(stages):
        b.append(rect(sx, 334, 230, 32, fill=C["bg3"], stroke=C["purple"], rx=16, sw=1.2))
        b.append(text(sx + 115, 355, f"{t} · {s}", 12, C["purple"], weight="bold"))
        if k < 2:
            b.append(arrow(sx + 232, 350, sx + 268, 350, C["purple"], mk="arrP"))
        sx += 270
    return svg_wrap(W, H, "".join(b), "数字孪生在环控制回路")


# ---------- 图：链式流程（沉淀 / 分步循环） ----------
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
            b.append(text(x + bw / 2, yy, ln, 12.5 if j == 0 else 11, col if j == 0 else C["grey"],
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


def svg_govern():
    items = [("步骤产出", C["navy"]), ("用户验证\n通过 / 修改", C["navy"]), ("候选登记\ncandidate", C["orange"]),
             ("人工闸门\n① 技能 / ② 记忆", C["red"]), ("入库\nsemantic / skill", C["teal"]),
             ("继承筛选\n≥0.6 · 未过期", C["teal"]), ("GC 标记\nexpired", C["grey"])]
    return svg_chain(items, "", (1, "不通过 → 只留 episodic 或丢弃"), "技能与记忆沉淀流程")


def svg_steploop():
    items = [("用户指令\n执行 S<x.y>", C["navy"]), ("AI 执行\n只写候选区", C["navy"]), ("产出\n报告 + 证据等级", C["navy"]),
             ("用户验证\n通过/修改/退回/暂停", C["orange"]), ("沉淀候选\nskill / memory", C["orange"]),
             ("闸门确认入库\n字段齐全", C["red"]), ("提交建议\n人执行 push", C["teal"])]
    return svg_chain(items, "下一条指令", (3, "修改 / 退回 → 同一步重做或撤回"), "按指令分步实施循环")


# ---------- 图：甘特 ----------
PHASE_COL = {"P0": "#5d6b78", "P1": "#0e8a7a", "P2": "#2f7fb8", "P3": "#c56a12", "P4": "#8a6d1d",
             "P5": "#b23a3a", "P6": "#6b4fa0", "P7": "#3d5a80"}


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
    wsf = (sf - W1).days / 7.0
    xs = lab + wsf * wk
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
            b.append(f'<rect x="{x:.1f}" y="{y + 7}" width="{d * wk:.1f}" height="{rh - 14}" rx="3" fill="{col}" fill-opacity="0.38" stroke="{col}" stroke-width="1"/>')
        else:
            b.append(text(22, y + 16, "◆ " + name, 11, "#8a4b08", anchor="start", weight="bold"))
            cx = lab + s * wk
            cy = y + rh / 2
            b.append(f'<polygon points="{cx:.1f},{cy - 8} {cx + 8:.1f},{cy} {cx:.1f},{cy + 8} {cx - 8:.1f},{cy}" fill="#f2b33d" stroke="#8a4b08" stroke-width="1.2"/>')
            b.append(text(cx + 11, cy + 4, f"W{s}", 9.5, "#8a4b08", anchor="start"))
        b.append(f'<line x1="8" y1="{y + rh}" x2="{W - 8}" y2="{y + rh}" stroke="#eef1f4" stroke-width="1"/>')
    end = W1 + dt.timedelta(weeks=weeks) - dt.timedelta(days=1)
    b.append(text(10, H - 10, f"W1 = {W1.isoformat()}（周一），W{weeks} 结束于 {end.isoformat()}。条形为阶段，浅色为子任务，菱形为门控。", 11, C["grey"], anchor="start"))
    return svg_wrap(int(W), int(H), "".join(b), "甘特图")


FIGS = {"flow": svg_flow, "arch": svg_arch, "twin": svg_twin, "govern": svg_govern, "steploop": svg_steploop}


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
.doc{max-width:1180px;margin:0 auto;background:#fff;border:1px solid var(--line);border-radius:10px;padding:34px 46px 50px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
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
@media print{#sidebar,#tocToggle,#toTop,#progress{display:none}main{margin:0;padding:0}.doc{border:0;box-shadow:none;max-width:none}h2{break-after:avoid}figure,table{break-inside:avoid}}
"""

JS = r"""
(function () {
  "use strict";
  var body = document.body;
  var toc = document.getElementById("toc");
  var toggle = document.getElementById("tocToggle");
  var filter = document.getElementById("tocFilter");
  var mobile = function () { return window.matchMedia("(max-width:980px)").matches; };
  var KEY = "planTocHidden";

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
<div class="foot">由 planning/build_plan.py 从同名 md 生成 · 单文件自包含，离线可用 · md 为正文唯一来源</div>
</article></main>
<button type="button" id="toTop" title="回到顶部">↑</button>
<script>{JS}</script>
</body>
</html>
"""


def main() -> int:
    for name in DOCS:
        src = HERE / name
        md_text = src.read_text(encoding="utf-8")
        title = re.search(r"^# (.+)$", md_text, flags=re.M).group(1).strip()
        body, tokens = convert(md_text)
        short = title.split("·")[-1].strip()
        meta = ["cp-design", "2026-10-02", short, "规划草案 · 待评审"]
        out = src.with_suffix(".html")
        out.write_text(page(title, "AIDCtms · coolingplate · practice01_0926", body, toc_html(tokens), meta),
                       encoding="utf-8")
        print(f"{out.name}  {out.stat().st_size / 1024:.1f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
