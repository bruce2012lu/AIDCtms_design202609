# -*- coding: utf-8 -*-
"""把 plan/ 下两份 Markdown 转成单文件 HTML（内联 CSS / JS / SVG，离线可读）。

Markdown 是唯一正文来源。Mermaid 代码块前若有 <!-- FIG:name --> 标记，
HTML 里换成同名内联 SVG，Mermaid 源码放进折叠的文本版。

    python plan/build_plan_html.py
"""
from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent

DOCS = {
    "项目规划_液冷设计平台_v1.0_20261002": {
        "kicker": "PROJECT PLAN · LIQUID-COOLING DESIGN PLATFORM",
        "sub": "B300 微通道冲击冷板与 Grace 平行微通道冷板 · 七阶段门控 + 双回路迭代 · AI 编排 + 可审计工具 + 人工闸门",
        "pills": ["AIDC-CP-PLAT-PLAN-001", "v1.0 · 2026-10-02", "规划草案 · 待评审", "cp-design 智能体", "非订单 ICD"],
    },
    "实施计划_液冷设计平台_v1.0_20261002": {
        "kicker": "IMPLEMENTATION PLAN · STEP BY STEP",
        "sub": "46 个可按指令执行的步骤（S01–S46）· 每步含目标、输入、动作、产出、验收、闸门、工时、依赖与环境标记",
        "pills": ["AIDC-CP-PLAT-IMPL-001", "v1.0 · 2026-10-02", "首批 S01–S05", "按指令逐步执行"],
    },
}

TAGS = {
    "[直接]": "t-ok", "[MATLAB]": "t-mat", "[ANSYS]": "t-ans",
    "[商业CAD]": "t-cad", "[实物]": "t-phy", "[人工]": "t-hum",
}

CAPTIONS = {
    "arch": "图 2-1　LCDP 分层架构。L3 适配层统一所有求解器入口；右侧为贯穿各层的人工闸门。",
    "flow": "图 3-1　七阶段门控流程与两条强制迭代回路。绿色为 v2.0 已完成，橙色为部分完成，灰色为未开始。",
    "dataflow": "图 4-1　数据流与工件链。每一步产物写入 runs/<ts>/ 并带 manifest；两条回路都回到一维模型。",
    "twin": "图 5-1　数字孪生与 AI 在环控制架构。控制器只作用于孪生；到实物的指令须经人工闸门。",
    "gantt": "图 8-1　里程碑与阶段时间线（估算，许可与样件到位为前提）。红色虚线为今天 2026-10-02。",
}

# ---------------------------------------------------------------- SVG

FONT = 'font-family="Microsoft YaHei, PingFang SC, Segoe UI, sans-serif"'


def _t(x, y, s, size=12, weight=400, fill="#182536", anchor="middle"):
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}">{html.escape(s)}</text>')


def _box(x, y, w, h, title, sub="", stroke="#1769e0", fill="#ffffff", dash=False, tsize=12.5):
    d = ' stroke-dasharray="5 4"' if dash else ""
    out = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" '
           f'fill="{fill}" stroke="{stroke}" stroke-width="1.4"{d}/>']
    if sub:
        out.append(_t(x + w / 2, y + h / 2 - 4, title, tsize, 700))
        out.append(_t(x + w / 2, y + h / 2 + 13, sub, 10.5, 400, "#5d6b80"))
    else:
        out.append(_t(x + w / 2, y + h / 2 + 4, title, tsize, 700))
    return "".join(out)


def _svg(w, h, body, label):
    defs = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" '
            'markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#5d6b80"/></marker>'
            '<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#b42318"/></marker></defs>')
    return (f'<svg class="svgfig" viewBox="0 0 {w} {h}" role="img" aria-label="{html.escape(label)}" '
            f'xmlns="http://www.w3.org/2000/svg" {FONT}>{defs}{body}</svg>')


def svg_arch():
    bands = [
        ("L0 交互层", "#e7f0fb", "#1769e0", [
            ("设计台 HTML", "ui/ · 127.0.0.1:8765"), ("Cursor / Claude 对话", "MCP stdio"),
            ("报告 HTML", "plan/ · cycle-* · DR 报告"), ("闸门看板（拟增）", "DR0–DR4 状态")]),
        ("L1 编排层", "#e6f6f2", "#008b7a", [
            ("cp-design 智能体", "agent.md · 证据等级"), ("platform Orchestrator", "拆解 · 路由 · 汇总"),
            ("协作智能体", "ai-matlab · librarian"), ("人工确认点", "confirm=true · 闸门")]),
        ("L2 技能层", "#fff7e6", "#a65b00", [
            ("design-loop", "已有"), ("cad-loop", "已有"), ("cfd-loop / gui-capture", "已有"),
            ("候选：oned-sweep 等", "mesh · cfd-matrix · fea"), ("候选：drawing 等", "vv · rom-twin · ail")]),
        ("L3 适配层 MCP", "#f3ecfb", "#6941c6", [
            ("cp-design MCP（已有）", "oned · hbm · grace · cad_*"), ("cp-design MCP（拟增）", "cfd_job · fea_job · report · twin"),
            ("user-matlab MCP", "Simscape · MPC · RL"), ("PyAnsys（待批准）", "PyFluent · PyMAPDL")]),
        ("L4 求解器层", "#fdecea", "#b42318", [
            ("Python 1D", "model.py · oned · zones"), ("MATLAB R2025b", "Simscape Fluids"),
            ("build123d / OCP", "+ SpaceClaim"), ("ICEM · Fluent", "2026 R1 · RTX 4090"),
            ("Mechanical", "APDL 承压 / 压装"), ("ROM / 孪生", "TwinAI · FMU")]),
        ("L5 数据与记忆层", "#eef2f7", "#0b2748", [
            ("设计口径登记册", "DB-*（拟增）"), ("runs/<ts>/", "manifest · 冻结只读"),
            ("memory/", "semantic · episodic"), ("knowledge/", "轨道 · 缺口 · 目录"),
            ("references/", "v2.0 / v2.1 / Grace"), ("git", "提交建议 · 人 push")]),
    ]
    out = []
    y = 16
    bh, gap = 78, 10
    x0, x1 = 122, 902
    for name, bg, stroke, boxes in bands:
        out.append(f'<rect x="8" y="{y}" width="{x1 - 8 + 4}" height="{bh}" rx="8" fill="{bg}" stroke="none"/>')
        out.append(f'<rect x="8" y="{y}" width="106" height="{bh}" rx="8" fill="{stroke}"/>')
        out.append(_t(61, y + bh / 2 + 4, name, 12.5, 700, "#ffffff"))
        n = len(boxes)
        w = (x1 - x0 - (n - 1) * 10) / n
        for i, (title, sub) in enumerate(boxes):
            dash = "拟增" in title or "候选" in title or "待批准" in title
            out.append(_box(x0 + i * (w + 10), y + 12, w, bh - 24, title, sub, stroke, "#ffffff", dash, 11.8))
        if name != "L5 数据与记忆层":
            out.append(f'<line x1="512" y1="{y + bh}" x2="512" y2="{y + bh + gap}" stroke="#5d6b80" '
                       f'stroke-width="1.4" marker-end="url(#ah)"/>')
        y += bh + gap
    top, bot = 16, y - gap
    out.append(f'<rect x="914" y="{top}" width="78" height="{bot - top}" rx="8" fill="#fff6f5" stroke="#b42318" stroke-dasharray="5 4"/>')
    lines = ["人工闸门", "", "① 技能安装", "② 记忆继承", "③ 资金 / 实物", "", "几何导出", "confirm=true", "", "求解提交", "确认", "", "DR0–DR4", "签字", "", "git push", "由人执行"]
    for i, s in enumerate(lines):
        out.append(_t(953, top + 30 + i * 28.5, s, 11.5 if i else 13, 700 if i == 0 else 400, "#b42318" if i == 0 else "#182536"))
    return _svg(1000, y + 4, "".join(out), "LCDP 分层架构")


def svg_flow():
    stages = [
        ("① 需求与输入", ["芯片规格 / 热包络", "机柜水力表", "接口与标准"], "done", "完成（缺 C-01~03）", "DR0 输入冻结"),
        ("② 概念与选型", ["方案权衡矩阵", "分区策略", "专利 FTO 初筛"], "done", "完成", "DR1 方案选定"),
        ("③ 性能设计", ["热阻预算分配", "射流参数", "流量 / 压降预算"], "done", "完成（PG25 待重算）", "DR2 性能基线"),
        ("④ 一维计算", ["能量平衡", "水力与换热关联式", "敏感性与差距闭合"], "done", "有条件通过", "DR2 闸门"),
        ("⑤ 三维仿真", ["共轭 CFD", "网格无关性", "工况矩阵"], "part", "部分：UC-01b 单胞", "DR3 仿真评审"),
        ("⑥ 机械与图纸", ["层叠与公差", "承压 / 变形", "2D / 3D / 爆炸"], "part", "部分：概念 STEP", "DR3 闸门"),
        ("⑦ 样件与试验", ["TTV 热阻", "流阻曲线", "红外 / 氦检"], "todo", "未开始", "DR4 送样放行"),
    ]
    style = {"done": ("#eaf6f1", "#1f7a4d"), "part": ("#fff5e0", "#a65b00"), "todo": ("#f1f3f6", "#8a94a6")}
    ai = ["AI：参数抽取 · 冲突识别", "AI：矩阵 · FTO 草稿", "AI：预算重算 · 杠杆", "AI：计算书 · 回归",
          "AI：journal · 收敛判定", "AI：规则门 · FEA · 出图", "AI：大纲 · 偏差 · 回路2"]
    out = []
    out.append('<rect x="6" y="22" width="568" height="262" rx="10" fill="none" stroke="#008b7a" stroke-width="1.6" stroke-dasharray="7 5"/>')
    out.append(_t(290, 16, "v2.0 报告已完成 ①–④（DR2 有条件通过）", 12, 700, "#008b7a"))
    for i, (title, items, st, status, dr) in enumerate(stages):
        x = 16 + i * 140
        fill, stroke = style[st]
        out.append(f'<rect x="{x}" y="36" width="128" height="160" rx="7" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')
        out.append(_t(x + 64, 58, title, 13, 700))
        for k, s in enumerate(items):
            out.append(_t(x + 64, 82 + k * 18, "· " + s, 11, 400, "#3b4a5e"))
        out.append(f'<line x1="{x + 10}" y1="128" x2="{x + 118}" y2="128" stroke="{stroke}" stroke-opacity="0.35"/>')
        out.append(_t(x + 64, 146, ai[i], 9.8, 400, "#1769e0"))
        out.append(f'<rect x="{x + 8}" y="162" width="112" height="22" rx="11" fill="{stroke}"/>')
        out.append(_t(x + 64, 177, status, 10.5, 700, "#ffffff"))
        if i < 6:
            out.append(f'<line x1="{x + 128}" y1="110" x2="{x + 139}" y2="110" stroke="#5d6b80" stroke-width="1.6" marker-end="url(#ah)"/>')
        cx, cy = x + 64, 240
        out.append(f'<line x1="{cx}" y1="196" x2="{cx}" y2="218" stroke="#a65b00" stroke-width="1.2"/>')
        out.append(f'<polygon points="{cx},{cy - 22} {cx + 60},{cy} {cx},{cy + 22} {cx - 60},{cy}" fill="#fff7e6" stroke="#a65b00" stroke-width="1.4"/>')
        out.append(_t(cx, cy + 4, dr, 11, 700, "#7a4300"))
    out.append('<path d="M640,262 C640,344 430,344 430,264" fill="none" stroke="#b42318" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#ahr)"/>')
    out.append(_t(535, 348, "回路1：仿真不达标 → 回 ③ / ④ 改几何（孔径、阵列密度、TIM2）", 12, 700, "#b42318"))
    out.append('<path d="M920,262 C920,424 360,424 360,264" fill="none" stroke="#b42318" stroke-width="1.8" stroke-dasharray="6 4" marker-end="url(#ahr)"/>')
    out.append(_t(640, 418, "回路2：试验与仿真偏差 >15% → 修正模型并回 ③（V&V 闭环）", 12, 700, "#b42318"))
    out.append(_t(16, 300, "AI 角色写在每个阶段框内（蓝字）", 10.5, 400, "#5d6b80", "start"))
    return _svg(1000, 436, "".join(out), "七阶段门控流程")


def svg_dataflow():
    out = []
    w, h, g = 118, 56, 16
    row1 = [("references / ICD", "报告 · OEM 资料"), ("设计口径 DB-*", "水 / PG25"), ("1D 计算", "oned · zones · sweep"),
            ("候选 params.yaml", "agent-candidate"), ("规则门", "cad_inspect"), ("CAD STEP", "+ 流体域 · 命名面"),
            ("网格 .msh", "GPU 显存门")]
    row2 = [("CFD 求解", "journal / PyFluent"), ("结果", "Rθ · ΔP · 逐孔流量"), ("DR3 评审包", "符合性矩阵"),
            ("工程图", "JM01-A0…A6"), ("样件与试验", "TTV · 流阻 · 氦检"), ("V&V 比对", "偏差 ≤15%"), ("模型修正", "h_scale · K")]
    xs = [10 + i * (w + g) for i in range(7)]
    for i, (a, b) in enumerate(row1):
        out.append(_box(xs[i], 30, w, h, a, b, "#1769e0", "#eef5ff", False, 11.5))
        if i < 6:
            out.append(f'<line x1="{xs[i] + w}" y1="58" x2="{xs[i + 1] - 2}" y2="58" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    for i, (a, b) in enumerate(row2):
        x = xs[6 - i]
        out.append(_box(x, 172, w, h, a, b, "#008b7a", "#eefaf7", False, 11.5))
        if i < 6:
            out.append(f'<line x1="{x}" y1="200" x2="{xs[5 - i] + w + 2}" y2="200" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append(f'<line x1="{xs[6] + w / 2}" y1="86" x2="{xs[6] + w / 2}" y2="170" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    x1d = xs[2]
    out.append(f'<path d="M{xs[0] + w / 2},172 V120 H{x1d + 30} V88" fill="none" stroke="#b42318" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#ahr)"/>')
    out.append(_t(xs[0] + 70, 114, "回路2", 11.5, 700, "#b42318"))
    out.append(f'<path d="M{xs[5] + w / 2},172 V140 H{x1d + 88} V88" fill="none" stroke="#b42318" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#ahr)"/>')
    out.append(_t(xs[4] + 20, 134, "回路1", 11.5, 700, "#b42318"))
    row3 = [("DOE → ROM", "TwinAI / POD-GP"), ("孪生 FMU", "FMI 2.0 Co-Sim"), ("AI 在环 SIL", "PID · MPC · RL")]
    for i, (a, b) in enumerate(row3):
        x = xs[6 - i]
        out.append(_box(x, 272, w, h, a, b, "#6941c6", "#f6f1fd", False, 11.5))
        if i < 2:
            out.append(f'<line x1="{x}" y1="300" x2="{xs[5 - i] + w + 2}" y2="300" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append(f'<line x1="{xs[6] + w / 2}" y1="228" x2="{xs[6] + w / 2}" y2="270" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    band_r = xs[4] - 14
    out.append(f'<rect x="10" y="272" width="{band_r - 10}" height="{h}" rx="6" fill="#f7fafd" stroke="#0b2748" stroke-dasharray="5 4"/>')
    out.append(_t((10 + band_r) / 2, 296, "全部工件写入 runs/<ts>/ + manifest.json", 12, 700, "#0b2748"))
    out.append(_t((10 + band_r) / 2, 315, "证据等级 E0–E5 · 输入 sha256 · 冻结件只读 · 大文件只记路径与哈希 · git 由人 push", 10.5, 400, "#5d6b80"))
    return _svg(1000, 340, "".join(out), "数据流与工件链")


def svg_twin():
    out = []
    out.append(_t(115, 22, "物理侧（只读数据）", 12.5, 700, "#0b2748"))
    out.append(_box(20, 34, 190, 58, "TTV 试验台 / 流阻台", "两块 25×25 mm + 八块 HBM 加热块", "#0b2748", "#eef2f7"))
    out.append(_box(20, 108, 190, 58, "传感器", "T · P · Q · 红外 · 氦检", "#0b2748", "#eef2f7"))
    out.append(_box(20, 182, 190, 58, "托盘 / CDU 运行数据", "远期 · 需 OEM", "#0b2748", "#eef2f7", True))
    out.append(_box(238, 100, 124, 74, "数据同化", "标定 h、R_TIM2、K", "#a65b00", "#fff7e6"))
    out.append('<line x1="210" y1="137" x2="236" y2="137" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append(_t(510, 22, "孪生模型（分层）", 12.5, 700, "#008b7a"))
    layers = [("L0 一维解析", "oned · zones（E1）"), ("L1 RC 热网络 + 水力网络", "Python / Simscape Fluids"),
              ("L2 CFD 降阶模型", "TwinAI / Fluent ROM / POD-GP"), ("FMU 2.0 Co-Simulation", "输入 Q · Tin · P(t) → Tcase · ΔP")]
    for i, (a, b) in enumerate(layers):
        out.append(_box(390, 34 + i * 54, 240, 46, a, b, "#008b7a", "#eefaf7" if i < 3 else "#ffffff", i == 3, 12))
    out.append('<line x1="362" y1="137" x2="388" y2="137" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append(_t(830, 22, "控制与场景", 12.5, 700, "#6941c6"))
    out.append(_box(680, 34, 300, 58, "控制器", "PID 基线 · MPC 主推 · RL + 安全盾（仅仿真训练）", "#6941c6", "#f6f1fd"))
    out.append(_box(680, 108, 300, 58, "场景库", "功率阶跃 · 堵塞 20% · 进液 45 °C · 泵故障 · 失冷", "#6941c6", "#f6f1fd"))
    out.append(_box(680, 182, 300, 58, "KPI 与报告", "约束满足 · 相对 PID 改善 · 能耗", "#6941c6", "#f6f1fd"))
    out.append('<line x1="632" y1="63" x2="678" y2="63" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)" marker-start="url(#ah)"/>')
    out.append('<line x1="830" y1="108" x2="830" y2="94" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append('<line x1="830" y1="166" x2="830" y2="180" stroke="#5d6b80" stroke-width="1.4" marker-end="url(#ah)"/>')
    out.append('<path d="M980,63 H992 V300 H115 V242" fill="none" stroke="#b42318" stroke-width="1.6" stroke-dasharray="6 4" marker-end="url(#ahr)"/>')
    out.append('<rect x="395" y="284" width="250" height="32" rx="16" fill="#fff6f5" stroke="#b42318"/>')
    out.append(_t(520, 305, "人工闸门：仅 SIL / HIL 草案，不连接执行器", 11.5, 700, "#b42318"))
    return _svg(1000, 330, "".join(out), "数字孪生与 AI 在环控制架构")


def svg_gantt():
    d0, d1 = date(2026, 10, 1), date(2027, 4, 1)
    x0, x1 = 210, 985
    span = (d1 - d0).days

    def X(s):
        y, m, d = map(int, s.split("-"))
        return x0 + (date(y, m, d) - d0).days / span * (x1 - x0)

    rows = [
        ("P0 基线与治理", "2026-10-05", "2026-10-16", "#1769e0"),
        ("P1 一维扩展与系统模型", "2026-10-12", "2026-10-30", "#1769e0"),
        ("P2 CAD v2 与 CFD 前处理", "2026-10-19", "2026-11-13", "#008b7a"),
        ("P3 整板 CFD 与 FEA", "2026-11-09", "2026-12-18", "#008b7a"),
        ("P4 工程图", "2026-12-01", "2026-12-31", "#a65b00"),
        ("P5 样件与试验", "2027-01-04", "2027-03-12", "#b42318"),
        ("P6 数字孪生与 AI 在环", "2026-11-16", "2027-02-26", "#6941c6"),
        ("P7 平台与治理（持续）", "2026-10-05", "2027-03-26", "#5d6b80"),
    ]
    ms = [("M0", "2026-10-05"), ("M1", "2026-10-16"), ("M2", "2026-11-13"), ("M3", "2026-12-18"),
          ("M4", "2027-01-08"), ("M6", "2027-02-26"), ("M5", "2027-03-12")]
    out = []
    top, rh = 44, 30
    bottom = top + rh * len(rows) + 46
    months = ["2026-10", "2026-11", "2026-12", "2027-01", "2027-02", "2027-03", "2027-04"]
    for k, mth in enumerate(months):
        x = X(mth + "-01")
        out.append(f'<line x1="{x:.1f}" y1="{top - 10}" x2="{x:.1f}" y2="{bottom}" stroke="#d7e0ec"/>')
        if k < 6:
            out.append(_t(x + (X(months[k + 1] + "-01") - x) / 2, top - 18, mth, 11.5, 700, "#0b2748"))
    for i, (name, a, b, c) in enumerate(rows):
        y = top + i * rh
        if i % 2 == 0:
            out.append(f'<rect x="8" y="{y}" width="{x1 - 8}" height="{rh}" fill="#f7fafd"/>')
        out.append(_t(16, y + 19, name, 12, 600, "#182536", "start"))
        xa, xb = X(a), X(b)
        out.append(f'<rect x="{xa:.1f}" y="{y + 7}" width="{max(xb - xa, 4):.1f}" height="{rh - 14}" rx="4" fill="{c}" opacity="0.85"/>')
        label = f"{a[5:]} → {b[5:]}"
        if xb < x1 - 90:
            out.append(_t(xb + 4, y + 19, label, 10, 400, "#5d6b80", "start"))
        elif xa - 90 > x0:
            out.append(_t(xa - 4, y + 19, label, 10, 400, "#5d6b80", "end"))
        else:
            out.append(_t((xa + xb) / 2, y + 19, label, 10, 700, "#ffffff"))
    ym = top + rh * len(rows) + 18
    bottom += 14
    out.append(_t(16, ym + 4, "里程碑", 12, 700, "#a65b00", "start"))
    for k, (name, s) in enumerate(ms):
        x = X(s)
        out.append(f'<polygon points="{x:.1f},{ym - 9} {x + 8:.1f},{ym} {x:.1f},{ym + 9} {x - 8:.1f},{ym}" fill="#fff7e6" stroke="#a65b00" stroke-width="1.4"/>')
        out.append(_t(x, ym + 24 + (14 if k % 2 else 0), f"{name} {s[5:]}", 10, 700, "#7a4300"))
    xt = X("2026-10-02")
    out.append(f'<line x1="{xt:.1f}" y1="{top - 10}" x2="{xt:.1f}" y2="{ym - 12}" stroke="#b42318" stroke-width="1.4" stroke-dasharray="4 3"/>')
    out.append(_t(xt - 3, top - 2, "今天", 10, 700, "#b42318", "end"))
    return _svg(1000, bottom + 18, "".join(out), "里程碑时间线")


SVGS = {"arch": svg_arch, "flow": svg_flow, "dataflow": svg_dataflow, "twin": svg_twin, "gantt": svg_gantt}

# ---------------------------------------------------------------- Markdown

def inline(s: str) -> str:
    codes: list[str] = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", keep, s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2">\1</a>', s)
    for tok, cls in TAGS.items():
        s = s.replace(tok, f'<span class="tag {cls}">{tok[1:-1]}</span>')
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], s)


def plain(s: str) -> str:
    for tok in TAGS:
        s = s.replace(tok, "")
    return re.sub(r"[`*]", "", s).strip()


def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(md: str):
    lines = md.splitlines()
    out: list[str] = []
    heads: list[tuple[int, str, str]] = []
    title = ""
    para: list[str] = []
    fig = None
    i = 0

    def flush():
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para.clear()

    while i < len(lines):
        line = lines[i]
        st = line.strip()
        if not st:
            flush(); i += 1; continue
        m = re.match(r"<!--\s*FIG:(\w+)\s*-->", st)
        if m:
            flush(); fig = m.group(1); i += 1; continue
        if st.startswith("```"):
            flush()
            lang = st[3:].strip()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            src = html.escape("\n".join(buf))
            if lang == "mermaid" and fig in SVGS:
                out.append(f'<figure class="svgbox">{SVGS[fig]()}<figcaption>{html.escape(CAPTIONS.get(fig, ""))}'
                           f'</figcaption><details class="mmd"><summary>文本版（Mermaid 源码，离线可读）</summary>'
                           f'<pre>{src}</pre></details></figure>')
            else:
                out.append(f'<pre class="code">{src}</pre>')
            fig = None
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", st)
        if m:
            flush()
            level, text = len(m.group(1)), m.group(2).strip()
            if level == 1:
                title = text
            else:
                hid = f"h{len(heads) + 1}"
                heads.append((level, hid, plain(text)))
                out.append(f'<h{level} id="{hid}">{inline(text)}</h{level}>')
            i += 1
            continue
        if st.startswith("|") and i + 1 < len(lines) and re.match(r"^\|?\s*:?-{3,}", lines[i + 1].strip()):
            flush()
            head = split_row(st)
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i])); i += 1
            cls = ' class="kv"' if len(head) == 2 and head[0] in ("项", "字段") else ""
            t = [f'<div class="tw"><table{cls}><thead><tr>']
            t += [f"<th>{inline(c)}</th>" for c in head]
            t.append("</tr></thead><tbody>")
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table></div>")
            out.append("".join(t))
            continue
        if re.match(r"^(\s*)([-*]|\d+\.)\s+", line):
            flush()
            ordered = bool(re.match(r"^\s*\d+\.", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines) and re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]):
                items.append(re.sub(r"^(\s*)([-*]|\d+\.)\s+", "", lines[i])); i += 1
            out.append(f'<{tag} class="tight">' + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
            continue
        if st.startswith(">"):
            flush()
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].strip()); i += 1
            out.append('<div class="note">' + inline(" ".join(buf)) + "</div>")
            continue
        para.append(st)
        i += 1
    flush()
    return title, "\n".join(out), heads


def toc_html(heads):
    root: list = []
    stack: list = [(1, root)]
    for level, hid, text in heads:
        node = {"level": level, "id": hid, "text": text, "kids": []}
        while stack[-1][0] >= level:
            stack.pop()
        stack[-1][1].append(node)
        stack.append((level, node["kids"]))

    def render(nodes):
        parts = ["<ul>"]
        for n in nodes:
            has = bool(n["kids"])
            cls = f'lv{n["level"]}' + (" has" if has else "") + (" collapsed" if has and n["level"] >= 3 else "")
            caret = '<span class="caret" aria-hidden="true"></span>' if has else '<span class="caret none"></span>'
            parts.append(f'<li class="{cls}"><div class="row">{caret}<a href="#{n["id"]}" data-id="{n["id"]}">'
                         f'{html.escape(n["text"])}</a></div>')
            if has:
                parts.append(render(n["kids"]))
            parts.append("</li>")
        parts.append("</ul>")
        return "".join(parts)

    return render(root)


CSS = r"""
:root{--navy:#0b2748;--blue:#1769e0;--teal:#008b7a;--ink:#182536;--muted:#5d6b80;--line:#d7e0ec;
--bg:#eef3f8;--soft:#f7fafd;--warn:#a65b00;--red:#b42318;--good:#1f7a4d;--side:300px}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:16px}
body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;-webkit-font-smoothing:antialiased}
aside#side{position:fixed;left:0;top:0;bottom:0;width:var(--side);background:#0f2a4a;color:#dbe6f3;display:flex;flex-direction:column;z-index:30;transition:transform .2s ease;box-shadow:2px 0 14px #0b274833}
.side-head{padding:16px 16px 10px;border-bottom:1px solid #ffffff1f}
.side-head .ttl{font-size:13px;color:#fff;font-weight:700;letter-spacing:.06em}
.side-head .doc{font-size:11.5px;color:#93b2d6;margin-top:3px;line-height:1.5}
.side-btns{display:flex;gap:6px;margin-top:10px}
.side-btns button{flex:1;background:#ffffff14;border:1px solid #ffffff2e;color:#dbe6f3;border-radius:5px;padding:4px 0;font:inherit;font-size:12px;cursor:pointer}
.side-btns button:hover{background:#ffffff26}
#tocFilter{width:100%;margin-top:8px;padding:6px 9px;border-radius:5px;border:1px solid #ffffff2e;background:#ffffff10;color:#fff;font:inherit;font-size:12.5px}
#tocFilter::placeholder{color:#93b2d6}
nav#toc{overflow:auto;padding:8px 6px 40px 6px;flex:1}
nav#toc ul{list-style:none;margin:0;padding:0}
nav#toc li ul{padding-left:14px}
nav#toc li.collapsed>ul{display:none}
nav#toc .row{display:flex;align-items:flex-start;gap:2px}
nav#toc .caret{width:16px;min-width:16px;height:22px;cursor:pointer;position:relative}
nav#toc .caret:before{content:"";position:absolute;left:4px;top:8px;border:5px solid transparent;border-top-color:#93b2d6;transition:transform .15s}
nav#toc li.collapsed>.row .caret:before{transform:rotate(-90deg);left:3px;top:6px}
nav#toc .caret.none{cursor:default}
nav#toc .caret.none:before{display:none}
nav#toc a{display:block;flex:1;color:#dbe6f3;text-decoration:none;padding:2px 6px;border-radius:4px;font-size:12.8px;line-height:1.5}
nav#toc li.lv2>.row a{font-weight:700;color:#fff;font-size:13.2px;margin-top:4px}
nav#toc li.lv4>.row a{font-size:12.2px;color:#b9cbe0}
nav#toc a:hover{background:#ffffff1a}
nav#toc a.active{background:var(--teal);color:#fff}
nav#toc li.hidden{display:none}
#sideToggle{position:fixed;top:12px;left:calc(var(--side) + 10px);z-index:40;width:34px;height:34px;border-radius:7px;border:1px solid var(--line);background:#fff;color:var(--navy);font-size:17px;cursor:pointer;box-shadow:0 2px 8px #0b274826;transition:left .2s ease}
body.side-off aside#side{transform:translateX(-100%)}
body.side-off #sideToggle{left:10px}
body.side-off #wrap{margin-left:0}
#wrap{margin-left:var(--side);transition:margin-left .2s ease}
.page{max-width:1240px;margin:0 auto;background:#fff;box-shadow:0 8px 34px #102a4c1f}
header.cover{padding:48px 62px 34px 70px;background:linear-gradient(145deg,#0b2748,#123a68);color:#fff}
header .kicker{font-size:12px;letter-spacing:.16em;color:#93b2d6;text-transform:uppercase}
header h1{font-size:31px;line-height:1.28;margin:12px 0;font-weight:700}
header .sub{font-size:15px;color:#d7e6f5;max-width:960px;line-height:1.75}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:20px}
.pill{border:1px solid #ffffff4d;border-radius:14px;padding:4px 11px;font-size:12px;background:#ffffff12}
main{padding:22px 62px 60px}
h2{font-size:23px;color:var(--navy);border-bottom:2.5px solid var(--navy);padding-bottom:8px;margin:44px 0 16px;font-weight:700}
h3{font-size:17.5px;color:#14507f;margin:28px 0 10px;font-weight:600;padding-left:11px;border-left:4px solid var(--teal)}
h4{font-size:15px;color:#fff;background:var(--navy);margin:26px 0 0;font-weight:600;padding:8px 12px;border-radius:8px 8px 0 0}
h4+.tw{margin-top:0}
p{margin:9px 0}
ul.tight,ol.tight{margin:10px 0 14px 1.4em;padding:0}
ul.tight li,ol.tight li{margin:5px 0}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-family:Consolas,"Courier New",monospace;font-size:12.5px;color:#1f3a5f}
strong{color:var(--navy)}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:13px 17px;border-radius:8px;margin:14px 0}
.tw{overflow-x:auto;margin:14px 0 20px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 10px;vertical-align:top;text-align:left;line-height:1.6}
th{background:var(--navy);color:#fff;font-weight:600;font-size:12.5px;white-space:nowrap}
tbody tr:nth-child(even) td{background:#fafcfe}
tbody tr:hover td{background:#eef6ff}
table.kv td:first-child{width:110px;font-weight:700;color:var(--navy);background:#f2f6fb;white-space:nowrap}
h4+.tw table.kv thead{display:none}
.tag{display:inline-block;padding:0 7px;border-radius:4px;font-size:11px;font-weight:700;white-space:nowrap;vertical-align:1px;margin:0 1px}
.t-ok{background:#e3f5ec;color:var(--good)}
.t-mat{background:#e7f0fb;color:var(--blue)}
.t-ans{background:#fff3d6;color:var(--warn)}
.t-cad{background:#efe8fb;color:#6941c6}
.t-phy{background:#fde8e6;color:var(--red)}
.t-hum{background:#e9edf3;color:#334155}
h4 .tag{background:#ffffff26;color:#fff}
figure{margin:18px 0 22px;border:1px solid var(--line);border-radius:10px;padding:14px 16px 10px;background:#fcfdff}
svg.svgfig{display:block;width:100%;height:auto}
figcaption{margin-top:10px;font-size:12.5px;color:var(--muted)}
details.mmd{margin-top:8px;font-size:12px;color:var(--muted)}
details.mmd summary{cursor:pointer}
details.mmd pre,pre.code{background:#f3f6fa;border:1px solid var(--line);border-radius:6px;padding:10px 12px;overflow:auto;font:12px/1.55 Consolas,monospace;color:#1f3a5f;white-space:pre}
footer{padding:22px 62px;background:var(--navy);color:#c9d8e8;font-size:12.5px;line-height:1.8}
footer b{color:#fff}
@media(max-width:1000px){:root{--side:270px}main,footer{padding-left:22px;padding-right:22px}header.cover{padding:40px 22px 26px 56px}body:not(.side-on) aside#side{transform:translateX(-100%)}body:not(.side-on) #wrap{margin-left:0}body:not(.side-on) #sideToggle{left:10px}}
@media print{aside#side,#sideToggle{display:none}#wrap{margin-left:0}.page{box-shadow:none;max-width:none}body{background:#fff;font-size:10.5pt}h2,h3,h4{page-break-after:avoid}table,figure{page-break-inside:avoid}details.mmd{display:none}@page{size:A4;margin:13mm}}
"""

JS = r"""
(function(){
  var body=document.body, toc=document.getElementById('toc');
  var narrow=function(){return window.matchMedia('(max-width:1000px)').matches;};
  document.getElementById('sideToggle').addEventListener('click',function(){
    if(narrow()){body.classList.toggle('side-on');}else{body.classList.toggle('side-off');}
  });
  toc.addEventListener('click',function(e){
    var c=e.target.closest('.caret');
    if(c&&!c.classList.contains('none')){c.closest('li').classList.toggle('collapsed');return;}
    if(e.target.tagName==='A'&&narrow()){body.classList.remove('side-on');}
  });
  document.getElementById('expAll').onclick=function(){toc.querySelectorAll('li.has').forEach(function(li){li.classList.remove('collapsed');});};
  document.getElementById('colAll').onclick=function(){toc.querySelectorAll('li.has').forEach(function(li){li.classList.add('collapsed');});};
  var filter=document.getElementById('tocFilter');
  filter.addEventListener('input',function(){
    var q=filter.value.trim().toLowerCase(), lis=toc.querySelectorAll('li');
    lis.forEach(function(li){li.classList.remove('hidden');});
    if(!q)return;
    lis.forEach(function(li){
      var hit=li.textContent.toLowerCase().indexOf(q)>=0;
      if(!hit){li.classList.add('hidden');}else if(li.classList.contains('has')){li.classList.remove('collapsed');}
    });
  });
  var links={}; toc.querySelectorAll('a[data-id]').forEach(function(a){links[a.dataset.id]=a;});
  var heads=Array.prototype.slice.call(document.querySelectorAll('main h2[id],main h3[id],main h4[id]'));
  var current=null, ticking=false;
  function update(){
    ticking=false;
    var pos=window.scrollY+90, act=heads[0];
    for(var k=0;k<heads.length;k++){if(heads[k].offsetTop<=pos){act=heads[k];}else{break;}}
    if(!act||act===current)return;
    if(current&&links[current.id])links[current.id].classList.remove('active');
    current=act; var a=links[act.id]; if(!a)return;
    a.classList.add('active');
    var li=a.closest('li');
    while(li){ if(li.classList.contains('has')&&li!==a.closest('li'))li.classList.remove('collapsed'); li=li.parentElement.closest('li'); }
    var r=a.getBoundingClientRect(), tr=toc.getBoundingClientRect();
    if(r.top<tr.top+40||r.bottom>tr.bottom-40){toc.scrollTop+=r.top-tr.top-tr.height/3;}
  }
  window.addEventListener('scroll',function(){if(!ticking){ticking=true;requestAnimationFrame(update);}},{passive:true});
  update();
})();
"""


def build(stem: str, meta: dict) -> Path:
    md = (HERE / f"{stem}.md").read_text(encoding="utf-8")
    title, body, heads = convert(md)
    pills = "".join(f'<span class="pill">{html.escape(p)}</span>' for p in meta["pills"])
    page = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
<aside id="side">
  <div class="side-head">
    <div class="ttl">目录</div>
    <div class="doc">{html.escape(title)}</div>
    <div class="side-btns"><button id="expAll" type="button">全部展开</button><button id="colAll" type="button">全部折叠</button></div>
    <input id="tocFilter" type="search" placeholder="筛选章节 / 步骤，如 S05、CFD">
  </div>
  <nav id="toc">{toc_html(heads)}</nav>
</aside>
<button id="sideToggle" type="button" title="收起 / 展开目录" aria-label="收起或展开目录">&#9776;</button>
<div id="wrap"><div class="page">
<header class="cover">
  <div class="kicker">{html.escape(meta["kicker"])}</div>
  <h1>{html.escape(title)}</h1>
  <div class="sub">{html.escape(meta["sub"])}</div>
  <div class="meta">{pills}</div>
</header>
<main>
{body}
</main>
<footer><b>{html.escape(title)}</b><br>由同名 Markdown 生成（plan/build_plan_html.py），单文件自包含、离线可读。
规划与计划不构成订单 ICD、FAT 保证或 FTO 法律意见；新增技能、记忆与代码改动均待用户确认后执行。</footer>
</div></div>
<script>{JS}</script>
</body>
</html>
"""
    out = HERE / f"{stem}.html"
    out.write_text(page, encoding="utf-8")
    return out


def main() -> None:
    for stem, meta in DOCS.items():
        p = build(stem, meta)
        print(p.name, p.stat().st_size)


if __name__ == "__main__":
    main()
