# -*- coding: utf-8 -*-
"""四块冷板的结构布局、结构尺寸、尺寸链报告和尺寸核实2工作簿。

名义尺寸来自本目录五份源文件，不另给公差带。蓝色单元格是输入，
尺寸链页全部用公式重加。源文件没有线性公差，本核实不做极值或统计公差。
"""
from __future__ import annotations

import html
from pathlib import Path

from openpyxl import Workbook
from openpyxl.formatting.rule import FormulaRule
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

ROOT = Path(__file__).resolve().parent
DATE = "2026-09-29"

CSS = """
:root { --ink:#1c2430; --muted:#5c6b7a; --line:#d5dde6; --navy:#0e3a5d; --ok:#0d6b3a; --bad:#9d1c1c; --wait:#8a5a00; --paper:#f6f4ef; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); background:var(--paper); font:16px/1.65 "Microsoft YaHei","PingFang SC",sans-serif; }
main { max-width:980px; margin:0 auto; padding:32px 28px 72px; background:#fff; }
h1 { font-size:28px; line-height:1.3; margin:0 0 8px; color:var(--navy); }
h2 { font-size:20px; margin:32px 0 10px; padding-top:8px; border-top:2px solid var(--navy); color:var(--navy); }
h3 { font-size:17px; margin:22px 0 8px; }
.sub { color:var(--muted); margin-bottom:18px; }
.meta { display:flex; flex-wrap:wrap; gap:8px 18px; font-size:13px; color:var(--muted); margin:8px 0 18px; }
.lead { background:#f3f7fb; border-left:4px solid var(--navy); padding:12px 14px; }
table { width:100%; border-collapse:collapse; margin:10px 0 16px; font-size:14px; }
th, td { border:1px solid var(--line); padding:6px 8px; vertical-align:top; text-align:left; }
th { background:#eef3f8; }
.num { text-align:right; font-variant-numeric:tabular-nums; white-space:nowrap; }
.ok { color:var(--ok); font-weight:700; }
.bad { color:var(--bad); font-weight:700; }
.wait { color:var(--wait); font-weight:700; }
.src { font-size:13px; color:var(--muted); }
.fig { margin:12px 0; overflow-x:auto; }
.figcap { font-size:13px; color:var(--muted); margin-top:4px; }
code { font-family:Consolas,monospace; font-size:13px; }
ul { margin:8px 0 8px 1.2em; }
footer { margin-top:36px; font-size:13px; color:var(--muted); }
"""


def E(text) -> str:
    return html.escape(str(text), quote=True)


def page(title, doc_no, subtitle, body) -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>{E(title)}</title>
<style>{CSS}</style>
</head>
<body>
<main>
<h1>{title}</h1>
<p class="sub">{subtitle}</p>
<div class="meta"><span>{E(doc_no)}</span><span>日期 {DATE}</span><span>状态：名义尺寸闭合，线性公差未给</span></div>
{body}
<footer>生成脚本 build_dimchain_reports.py。改尺寸时改工作簿里的蓝色输入格，或改脚本后重跑。本页与同名尺寸核实2工作簿用同一组输入。</footer>
</main>
</body>
</html>
"""


def table(headers, rows) -> str:
    th = "".join(f"<th>{E(h)}</th>" for h in headers)
    body = []
    for row in rows:
        tds = []
        for i, cell in enumerate(row):
            cls = "num" if isinstance(cell, float) else ""
            text = f"{cell:.3f}" if isinstance(cell, float) else str(cell)
            if text in ("闭合", "恒等闭合"):
                text = f'<span class="ok">{text}</span>'
            elif text == "不闭合":
                text = f'<span class="bad">{text}</span>'
            elif text.startswith("待"):
                text = f'<span class="wait">{E(text)}</span>'
            else:
                text = E(text) if not text.startswith("<") else text
            tds.append(f'<td class="{cls}">{text}</td>')
        body.append("<tr>" + "".join(tds) + "</tr>")
    return "<table><thead><tr>" + th + "</tr></thead><tbody>" + "".join(body) + "</tbody></table>"


def eval_expr(expr: str, params: dict) -> float:
    return float(eval(expr, {"__builtins__": {}}, params))


class Chain:
    def __init__(self, cid, title, segments, target, note, adopted=True):
        self.cid = cid
        self.title = title
        self.segments = segments  # (name, expr, note)
        self.target = target      # expr
        self.note = note
        self.adopted = adopted

    def values(self, params):
        vals = [eval_expr(e, params) for _, e, _ in self.segments]
        return vals, sum(vals), eval_expr(self.target, params)

    def closed(self, params, tol=1e-6):
        _, total, want = self.values(params)
        return abs(total - want) <= tol


def svg_wrap(inner, w, h, caption):
    return (
        f'<div class="fig"><svg viewBox="0 0 {w} {h}" width="{w}" xmlns="http://www.w3.org/2000/svg">'
        f'<rect width="{w}" height="{h}" fill="#fbfaf7"/>{inner}</svg>'
        f'<p class="figcap">{caption}</p></div>'
    )


def R(x, y, w, h, fill, stroke="#33404d", sw=1):
    return f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'


def T(x, y, text, size=12, fill="#1c2430", anchor="start"):
    return (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-family="Microsoft YaHei,Arial">{E(text)}</text>'
    )


# ---------------------------------------------------------------------------
# GPU
# ---------------------------------------------------------------------------

GPU = dict(
    plate_L=95.0, plate_W=75.0, plate_T=8.5, cav_t=8.0,
    margin_x=5.0, hbm_w=11.0, gap_rib=0.5, rib_w=2.0, die_w=27.0, hbi=3.0,
    die_h=28.0, die_ax=19.0, die_ay=23.5, die_bx=49.0,
    y_end=12.5, col_len=50.0, hbm_xr=79.0,
    base_cu=2.0, groove_h=1.5, jet_h=2.0, lid_t=2.5, braze=0.5,
    n_jx=9, n_jy=12, pitch_x=3.0, pitch_y=2.4, cov_y=28.8, oh_y=0.8,
    env_allow=1.2, env_y=29.2, env_rem=0.4,
    ch_w=0.40, ch_p=0.80, n_ch_die=35, n_slot=3,
    land_cell=0.20, slot_w=0.40, slot_rib=0.40, slit=0.40,
    D_jet=0.40, D_rpt=0.50,
    hole_in=4.5, hole_span_x=86.0, hole_span_y=66.0,
    stack_h=11.0, gap_stack=2.0,
)

GPU_CHAINS = [
    Chain("X板宽", "X 向板宽", [
        ("左边距", "margin_x", "板边到左列 HBM"),
        ("左列 HBM 宽", "hbm_w", "11 mm 列"),
        ("左列到左肋", "gap_rib", "缝"),
        ("左隔离肋", "rib_w", ""),
        ("左肋到 Die-A", "gap_rib", "缝"),
        ("Die-A", "die_w", ""),
        ("NV-HBI", "hbi", "缝上不打密孔"),
        ("Die-B", "die_w", ""),
        ("Die-B 到右肋", "gap_rib", "缝"),
        ("右隔离肋", "rib_w", ""),
        ("右肋到右列", "gap_rib", "缝"),
        ("右列 HBM 宽", "hbm_w", ""),
        ("右边距", "margin_x", "与左边距同一输入"),
    ], "plate_L", "5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5。右边距与左边距用同一个数，左右对称是输入约定。"),
    Chain("Y板长", "Y 向板长", [
        ("下边距", "y_end", "板边到隔离肋下端，也是首颗 HBM 的 y"),
        ("肋长 / 四颗 HBM 列长", "col_len", "12.5 到 62.5"),
        ("上边距", "y_end", ""),
    ], "plate_W", "12.5+50+12.5。"),
    Chain("DieA左缘", "Die-A 左缘坐标", [
        ("左边距", "margin_x", ""),
        ("左列", "hbm_w", ""),
        ("缝", "gap_rib", ""),
        ("肋", "rib_w", ""),
        ("缝", "gap_rib", ""),
    ], "die_ax", "分段相加应对上锁定坐标 19.0。"),
    Chain("DieB左缘", "Die-B 左缘坐标", [
        ("Die-A 左缘", "die_ax", ""),
        ("Die-A 宽", "die_w", ""),
        ("HBI", "hbi", ""),
    ], "die_bx", "19+27+3=49。"),
    Chain("右列起点", "右列 HBM 的 x", [
        ("板宽", "plate_L", ""),
        ("右边距（减）", "-margin_x", "减环"),
        ("列宽（减）", "-hbm_w", "减环"),
    ], "hbm_xr", "95−5−11=79，与锁定坐标对照。"),
    Chain("腔厚", "腔体厚度（不含钎缝）", [
        ("余铜", "base_cu", "接触面以上"),
        ("短槽深", "groove_h", ""),
        ("喷距", "jet_h", ""),
        ("喷嘴板", "lid_t", ""),
    ], "cav_t", "2.0+1.5+2.0+2.5=8.0。UC01b 在盖板之上另有 2.0 mm 进液延长，那是计算域，不进零件厚度。"),
    Chain("外形厚", "外形厚度", [
        ("余铜", "base_cu", ""),
        ("短槽深", "groove_h", ""),
        ("喷距", "jet_h", ""),
        ("喷嘴板", "lid_t", ""),
        ("周边钎缝 / 水嘴台阶", "braze", ""),
    ], "plate_T", "8.0+0.5=8.5。"),
    Chain("覆盖X", "单 die 射流覆盖长度 X", [
        ("9 格 × X 节距", "n_jx*pitch_x", "格数与节距分开输入"),
    ], "die_w", "9×3.0=27.0，与 die 宽一致，X 向没有余量也没有超出。"),
    Chain("覆盖Y", "单 die 射流覆盖长度 Y", [
        ("12 格 × Y 节距", "n_jy*pitch_y", ""),
    ], "cov_y", "12×2.4=28.8。封闭环是报告写出的覆盖长度，不是 die 高。"),
    Chain("超出Y", "Y 向覆盖超出 die", [
        ("覆盖长度", "cov_y", ""),
        ("die 高（减）", "-die_h", ""),
    ], "oh_y", "28.8−28=0.8。这是报告写明的外包络，孔本身仍在 die 投影内。"),
    Chain("外包络", "Y 向板外包络", [
        ("die 高", "die_h", ""),
        ("外包络余量定额", "env_allow", "报告取 1.2 mm"),
    ], "env_y", "28+1.2=29.2。"),
    Chain("包络余", "覆盖放进外包络后的余量", [
        ("外包络", "env_y", ""),
        ("覆盖长度（减）", "-cov_y", ""),
    ], "env_rem", "29.2−28.8=0.4。"),
    Chain("槽覆盖", "die 高度上的槽节距数", [
        ("35 × 槽节距", "n_ch_die*ch_p", "die 高 28 mm 内容得下的节距数"),
    ], "die_h", "35×0.80=28.0。12 个胞×每胞 3 槽=36 个节距，多出的 1 个节距就是上面的 0.8 mm。"),
    Chain("单胞Y", "一个射流胞的 Y 向", [
        ("胞边半肋", "land_cell", "网格：胞边到第一条槽 0.20"),
        ("槽 1", "slot_w", "0.40"),
        ("肋", "slot_rib", "0.40"),
        ("槽 2", "slot_w", ""),
        ("肋", "slot_rib", ""),
        ("槽 3", "slot_w", ""),
        ("胞边半肋", "land_cell", ""),
    ], "pitch_y", "0.20+0.40+0.40+0.40+0.40+0.40+0.20=2.40。槽位置来自 UC01b 网格，节距来自 v2.0。"),
    Chain("孔X", "安装孔中心距，X", [
        ("左边孔中心到板边", "hole_in", "中心在 4.5"),
        ("两孔中心距", "hole_span_x", "90.5−4.5"),
        ("右边孔中心到板边", "hole_in", "中心在 90.5"),
    ], "plate_L", "4.5+86+4.5=95。孔径 3.4 不进这条中心距链。"),
    Chain("孔Y", "安装孔中心距，Y", [
        ("下边", "hole_in", "中心 4.5"),
        ("两孔中心距", "hole_span_y", "70.5−4.5"),
        ("上边", "hole_in", "中心 70.5"),
    ], "plate_W", "4.5+66+4.5=75。"),
    Chain("四颗Y", "四颗 HBM 的列长", [
        ("第 1 颗", "stack_h", "y 12.5–23.5"),
        ("间隙", "gap_stack", "不加热"),
        ("第 2 颗", "stack_h", "25.5–36.5"),
        ("间隙", "gap_stack", ""),
        ("第 3 颗", "stack_h", "38.5–49.5"),
        ("间隙", "gap_stack", ""),
        ("第 4 颗", "stack_h", "51.5–62.5"),
    ], "col_len", "4×11+3×2=50。加热段合计 44 mm。"),
]


def gpu_svg():
    s, ox, oy = 5.6, 36, 28
    H = 75

    def X(v):
        return ox + v * s

    def Y(v):
        return oy + (H - v) * s

    def box(x, y, w, h, fill, stroke="#33404d"):
        return R(X(x), Y(y + h), w * s, h * s, fill, stroke)

    parts = [R(8, 8, 620, 470, "#fbfaf7", "#fbfaf7", 0)]
    parts.append(box(0, 0, 95, 75, "#f4e0cf", "#5c3a17"))
    for x in (5, 79):
        for y in (12.5, 25.5, 38.5, 51.5):
            parts.append(box(x, y, 11, 11, "#d9efe4", "#1d6b45"))
    parts.append(box(16.5, 12.5, 2, 50, "#1e4d78", "#1e4d78"))
    parts.append(box(76.5, 12.5, 2, 50, "#1e4d78", "#1e4d78"))
    parts.append(box(19, 23.5, 27, 28, "#f0c2b4", "#9d1c1c"))
    parts.append(box(49, 23.5, 27, 28, "#f0c2b4", "#9d1c1c"))
    parts.append(box(46, 23.5, 3, 28, "#f7f1c8", "#8a5a00"))
    parts.append(box(8, 66, 79, 7, "#d9e9f7", "#1f6fb2"))
    parts.append(box(8, 2, 79, 7, "#f6dcd8", "#9d1c1c"))
    # jets: first centers
    for origin in (20.5, 50.5):
        for i in range(9):
            for j in range(12):
                cx, cy = origin + i * 3.0, 24.3 + j * 2.4
                parts.append(
                    f'<circle cx="{X(cx):.1f}" cy="{Y(cy):.1f}" r="1.3" fill="#0e3a5d"/>'
                )
    parts.append(T(X(32.5), Y(37), "Die-A", 13, "#9d1c1c", "middle"))
    parts.append(T(X(62.5), Y(37), "Die-B", 13, "#9d1c1c", "middle"))
    parts.append(T(X(10.5), Y(18), "HBM", 11, "#1d6b45", "middle"))
    parts.append(T(X(84.5), Y(18), "HBM", 11, "#1d6b45", "middle"))
    parts.append(T(X(47.5), Y(70), "进液", 12, "#1f6fb2", "middle"))
    parts.append(T(X(47.5), Y(5.5), "出液", 12, "#9d1c1c", "middle"))
    parts.append(T(X(47.5), Y(-2), "+X  95 mm", 12, "#33404d", "middle"))
    parts.append(T(18, Y(37), "+Y", 12, "#33404d", "middle"))
    return svg_wrap("".join(parts), 640, 490,
                    "图 1 · GPU 冷板平面，1 格约 5.6 px/mm，原点在左下角。点是 9×12 射流中心。青绿是 HBM 足迹，深蓝竖条是隔离肋。")


def gpu_layout():
    body = f"""
<p class="lead">这块板是 B300 上的 GPU 射流冲击微通道冷板，型号沿用 CP-B300-JM-01。一块板盖一颗 B300：两颗计算 die 走射流和短槽，左右两列 HBM 只在图上标出足迹，槽本身见 HBM 冷板那一份。计算托盘上共四块，进液边朝后面板。</p>
<h2>1　坐标</h2>
<p>原点在冷板左下角。X 沿 95 mm 板宽向右，Y 沿 75 mm 板长向上，芯片面是 z 的小端。进液歧管在 Y 大的一边，出液歧管在 Y 小的一边。</p>
{gpu_svg()}
<h2>2　平面怎么分</h2>
<p>从左到右是一条对称链：边距、HBM 列、缝、隔离肋、缝、Die-A、3 mm 的 NV-HBI、Die-B，然后镜像到右边缘。隔离肋把 GPU 短槽和 HBM 列隔开，HBI 缝上不打密孔。</p>
<p>每颗 die 上是 9×12 个射流胞。胞的 X 是 3.0 mm，沿短槽；Y 是 2.4 mm，沿出流方向。孔打在胞心。X 向 9 格刚好等于 27 mm die 宽。Y 向 12 格覆盖 28.8 mm，比 28 mm 的 die 高出 0.8 mm，两端各约 0.4 mm。孔半径 0.20 mm，孔缘仍落在 die 投影里面。</p>
<p>一个胞在 Y 向切出 3 条 0.40 mm 短槽，槽间肋 0.40 mm，胞边各留 0.20 mm 半肋。短槽沿 X，长度不超过一个胞的 3.0 mm 量级，废液从胞两侧的回液缝抽走。</p>
<h2>3　厚度方向</h2>
<p>从芯片面往上：余铜 2.0、短槽 1.5、喷距 2.0、喷嘴板 2.5，腔体 8.0 mm。外形再加周边钎缝 0.5 mm，为 8.5 mm。网格在喷嘴板外面还接了 2.0 mm 进液段，用来给定入口，不计入这块铜的外形。</p>
<h2>4　流路</h2>
<p>水从 Y=66–73 mm 的进液带进入，经喷嘴板的孔冲击余铜顶面，再进入短槽，汇到 Y=2–9 mm 的出液带。左右 HBM 列不设喷嘴。四角安装孔中心在 (4.5, 4.5)、(90.5, 4.5)、(4.5, 70.5)、(90.5, 70.5)，孔径 3.4 mm。</p>
<h2>5　本说明用的口径</h2>
<ul>
<li>板级坐标、9×12 阵列、节距 3.0×2.4、厚度栈：设计报告 v2.0。</li>
<li>孔径和胞内三条槽的切分：本目录 UC01b，孔径 0.40 mm。设计报告正文仍写 0.50 mm，孔位链与孔径无关，两个直径都留在尺寸表里。</li>
<li>asm_0921 是 128 孔、孔径 0.50 mm、总厚 12.5 mm 的三层静压箱结构。那一版阵列已被 9×12 取代，本尺寸链不把它加进 8.5 mm 的厚度里。</li>
</ul>
"""
    return page("GPU 射流冲击微通道冷板 · 结构布局说明", "DC-GPU-LAY-01",
                "CP-B300-JM-01 的 GPU 区。平面按 v2.0，孔径按 UC01b。", body)


def dim_page(title, doc, subtitle, intro, groups):
    parts = [f"<p class='lead'>{intro}</p>"]
    for head, rows in groups:
        parts.append(f"<h2>{E(head)}</h2>")
        parts.append(table(["项目", "尺寸 / mm", "来源与说明"], rows))
    return page(title, doc, subtitle, "".join(parts))


def gpu_dims():
    g = GPU
    groups = [
        ("外形", [
            ["板宽 X", g["plate_L"], "v2.0 外形"],
            ["板长 Y", g["plate_W"], "v2.0 外形"],
            ["板厚", g["plate_T"], "含钎缝 0.5"],
            ["腔体厚度", g["cav_t"], "不含钎缝"],
            ["安装孔中心边距", g["hole_in"], "四角"],
            ["安装孔 X 向中心距", g["hole_span_x"], "90.5−4.5"],
            ["安装孔 Y 向中心距", g["hole_span_y"], "70.5−4.5"],
            ["安装孔径", 3.4, "不进入中心距链"],
        ]),
        ("分区", [
            ["左右边距", g["margin_x"], ""],
            ["HBM 列宽 × 单颗高", f'{g["hbm_w"]:.3f} × {g["stack_h"]:.3f}', "列内四颗"],
            ["HBM 列长", g["col_len"], "含三处 2 mm 间隙"],
            ["颗间间隙", g["gap_stack"], "不加热"],
            ["隔离肋宽 × 长", f'{g["rib_w"]:.3f} × {g["col_len"]:.3f}', "左右各一"],
            ["肋与列、肋与 die 的缝", g["gap_rib"], "每侧两道"],
            ["Die 宽 × 高", f'{g["die_w"]:.3f} × {g["die_h"]:.3f}', "两颗"],
            ["Die-A 左下角", f'{g["die_ax"]:.3f} , {g["die_ay"]:.3f}', "锁定坐标"],
            ["Die-B 左缘", g["die_bx"], ""],
            ["NV-HBI", g["hbi"], ""],
            ["右列 HBM 的 x", g["hbm_xr"], ""],
            ["下边距 / 首颗 y", g["y_end"], ""],
        ]),
        ("射流与短槽", [
            ["X 向格数 × 节距", f'{g["n_jx"]} × {g["pitch_x"]:.3f}', "覆盖 27 mm"],
            ["Y 向格数 × 节距", f'{g["n_jy"]} × {g["pitch_y"]:.3f}', "覆盖 28.8 mm"],
            ["Y 向超出 die", g["oh_y"], "两端合计"],
            ["Y 向外包络", g["env_y"], "28+1.2"],
            ["外包络余量", g["env_rem"], "29.2−28.8"],
            ["孔径，UC01b", g["D_jet"], "本目录计算口径"],
            ["孔径，设计报告正文", g["D_rpt"], "与孔位链无关"],
            ["喷距", g["jet_h"], ""],
            ["短槽宽 × 深", f'{g["ch_w"]:.3f} × {g["groove_h"]:.3f}', ""],
            ["短槽节距", g["ch_p"], "肋宽 0.40"],
            ["die 高度内的节距数", float(g["n_ch_die"]), "35×0.80=28"],
            ["每胞槽数", float(g["n_slot"]), "12 胞共 36 个节距"],
            ["胞边半肋", g["land_cell"], "UC01b"],
            ["胞侧回液缝", g["slit"], "两侧各一，中间剩余 2.20"],
        ]),
        ("厚度栈", [
            ["余铜", g["base_cu"], ""],
            ["短槽深", g["groove_h"], ""],
            ["喷距", g["jet_h"], ""],
            ["喷嘴板", g["lid_t"], ""],
            ["钎缝", g["braze"], ""],
        ]),
    ]
    return dim_page(
        "GPU 射流冲击微通道冷板 · 结构尺寸说明", "DC-GPU-DIM-01",
        "单位 mm。同一项目只保留一个采用值，对照值单独成行。",
        "下表是尺寸链的输入，不是从板宽反推出来的余量。右边距与左边距用同一个 5 mm。",
        groups,
    )


def chain_html(title, doc, subtitle, intro, params, chains, extra=""):
    parts = [f"<p class='lead'>{intro}</p>", extra, "<h2>逐条尺寸链</h2>"]
    for ch in chains:
        vals, total, want = ch.values(params)
        flag = "闭合" if ch.closed(params) else "不闭合"
        if not ch.adopted and ch.closed(params):
            flag = "闭合"
        parts.append(f"<h3>{E(ch.title)}</h3>")
        parts.append(f"<p>{E(ch.note)}</p>")
        rows = []
        for (name, expr, note), val in zip(ch.segments, vals):
            rows.append([name, val, expr, note])
        rows.append(["组成环之和", total, "工作簿中为 SUM", ""])
        rows.append(["封闭环", want, ch.target, ""])
        rows.append(["差值", total - want, "和 − 封闭环", flag if ch.adopted or True else flag])
        use = "采用" if ch.adopted else "对照，不作为本板出图尺寸"
        rows.append(["用途", use, "", ""])
        parts.append(table(["组成环", "计算值 / mm", "输入名", "说明"], rows))
    return page(title, doc, subtitle, "".join(parts))


def gpu_chain():
    intro = (
        "五条板级链与 v2.0 的校核式相同，并补上孔距、单胞槽和四颗 HBM 列长。"
        "全部采用链闭合。孔径 0.40 与 0.50 不进入这些加法。"
        "源文件没有给出孔距、槽宽的线性公差，本报告只核名义尺寸。"
    )
    return chain_html(
        "GPU 射流冲击微通道冷板 · 尺寸链计算报告", "DC-GPU-CHN-01",
        "封闭环是外形或报告中另写的名义值。组成环是分区尺寸。",
        intro, GPU, GPU_CHAINS,
    )


# ---------------------------------------------------------------------------
# HBM
# ---------------------------------------------------------------------------

HBM = dict(
    col_w=11.0, ch_w=0.80, ch_h=2.00, fin_w=0.80, n_ch=7, land=0.30,
    col_len=50.0, stack_h=11.0, gap_stack=2.0, n_stack=4, heat_len=44.0,
    base=2.0, lid=4.0, plate_hbm=8.0, tim=0.080,
    land65=0.65, ch60=0.60, fin70=0.70, n8=8,
    plate_L=95.0, plate_W=75.0, margin_x=5.0, gap_rib=0.5, rib_w=2.0,
    die_w=27.0, hbi=3.0, y_end=12.5, hbm_xr=79.0, die_ax=19.0,
)

HBM_CHAINS = [
    Chain("列宽", "HBM 列宽（采用 0.80×2.00，7 槽）", [
        ("左岸", "land", "0.30"),
        ("7 条槽", "n_ch*ch_w", ""),
        ("6 条肋", "(n_ch-1)*fin_w", "肋宽 0.80，节距 1.60"),
        ("右岸", "land", ""),
    ], "col_w", "0.30+5.60+4.80+0.30=11.00。这是本目录 w08h20 报告的截面。"),
    Chain("列长", "列长（四颗加三处间隙）", [
        ("四颗高度", "n_stack*stack_h", ""),
        ("三处间隙", "(n_stack-1)*gap_stack", ""),
    ], "col_len", "44+6=50。"),
    Chain("加热长", "加热长度", [
        ("四颗高度", "n_stack*stack_h", "间隙不加热"),
    ], "heat_len", "4×11=44，与一维模型的受热长度一致。"),
    Chain("厚度", "HBM 区铜厚", [
        ("底铜", "base", ""),
        ("槽深", "ch_h", "槽顶封死"),
        ("上铜板", "lid", "4.0 mm，留给端部腔的厚度在这块板上"),
    ], "plate_hbm", "2+2+4=8.0。TIM 0.080 在铜板之外，不进板厚。"),
    Chain("对照截面", "对照：v2.0 表内的 0.60 mm 八槽", [
        ("左岸", "land65", "0.65"),
        ("8 条槽", "n8*ch60", "0.60"),
        ("7 条肋", "(n8-1)*fin70", "节距 1.30，肋 0.70"),
        ("右岸", "land65", ""),
    ], "col_w", "0.65+4.80+4.90+0.65=11.00。这套也能合成 11 mm，但是槽数、肋宽、岸宽都和 w08h20 不同。",
       adopted=False),
    Chain("在板上的X", "左列在 GPU 板上的 X 位置链", [
        ("左边距", "margin_x", ""),
        ("列宽", "col_w", ""),
        ("缝", "gap_rib", ""),
        ("肋", "rib_w", ""),
        ("缝", "gap_rib", ""),
    ], "die_ax", "5+11+0.5+2+0.5=19，接到 Die-A。右列 x=79 见 GPU 报告同一条链。"),
    Chain("在板上的Y", "列在板上的 Y", [
        ("下边距", "y_end", ""),
        ("列长", "col_len", ""),
        ("上边距", "y_end", ""),
    ], "plate_W", "12.5+50+12.5=75。"),
]


def hbm_svg():
    s = 28
    ox, oy = 80, 36

    def X(v):
        return ox + v * s

    def Y(v):
        return oy + (6.2 - v) * s * 0.72

    parts = []
    # cross section x 0-11, z 0-8
    def sec(x, z, w, h, fill, stroke="#33404d"):
        return R(X(x), 40 + (8 - z - h) * 22, w * s, h * 22, fill, stroke)

    parts.append(sec(0, 0, 11, 2.0, "#e7c8a4"))
    x = 0.30
    for i in range(7):
        parts.append(sec(x, 2.0, 0.80, 2.0, "#d9e9f7", "#1f6fb2"))
        x += 0.80
        if i < 6:
            parts.append(sec(x, 2.0, 0.80, 2.0, "#e7c8a4"))
            x += 0.80
    parts.append(sec(0, 4.0, 11, 4.0, "#e7c8a4"))
    parts.append(T(X(5.5), 28, "上铜板 4.0", 13, "#5c3a17", "middle"))
    parts.append(T(X(5.5), 250, "底铜 2.0    列宽 11", 13, "#5c3a17", "middle"))
    parts.append(T(40, 140, "槽 0.80×2.00，肋 0.80，两岸 0.30", 13, "#1f6fb2"))
    return svg_wrap("".join(parts), 520, 280,
                    "图 1 · 单侧一列的横截面。蓝色是水，其余是铜。槽顶封死，加热段没有通长水缝。")


def hbm_layout():
    body = f"""
<p class="lead">HBM 微通道冷板在这里指 B300 冷板左右两列的冷却区，不是另一块外形 95×75 的铜板。截面按本目录 w08h20 结果报告：单侧 7 条封闭槽，0.80 mm × 2.00 mm。列的位置仍用 v2.0 的锁定坐标。</p>
<h2>1　平面</h2>
<p>左列占 X 5–16，右列占 X 79–90。每列 Y 向从 12.5 到 62.5，长 50 mm，里面四颗 11 mm 高的堆叠，颗与颗之间 2 mm 不加热。四颗的 y 是 12.5、25.5、38.5、51.5。列和 GPU die 之间是 0.5 mm 缝、2.0 mm 隔离肋、再 0.5 mm 缝。</p>
<p>水沿列的长向走。7 条槽并排，节距 1.60 mm，两岸各 0.30 mm。偶数槽和奇数槽在交错流方案里反向，汇流腔做在端部上铜板里。那些腔是流路，列的外形仍是 11×50 mm。</p>
{hbm_svg()}
<h2>2　厚度</h2>
<p>底铜 2.0 mm，槽高 2.0 mm，上铜板 4.0 mm，铜厚 8.0 mm。槽顶在加热段是封的，肋从槽底接到上铜板。TIM 0.080 mm 贴在底铜之下，不算板厚。</p>
<p>GPU 区的外形是 8.5 mm，并且带 1.5 mm 开槽和 2.0 mm 喷距。HBM 区这套是 8.0 mm 封闭深槽。两套各自加得拢，还没有合成同一块铜的一个厚度栈。出图前要先定共用底板的 z，不能把 0.60 mm 八槽和 0.80 mm 七槽铣在同一列里。</p>
<h2>3　对照截面</h2>
<p>v2.0 计算表里的 HBM 槽是 0.60×1.50 mm、节距 1.30 mm、单侧 8 条、岸 0.65 mm。那一套加起来也是 11.00 mm。尺寸链报告里把它列为对照链：算术闭合，但不作为本 HBM 冷板的出图截面。</p>
"""
    return page("HBM 微通道冷板 · 结构布局说明", "DC-HBM-LAY-01",
                "单侧一列。截面 w08h20，足迹 v2.0。", body)


def hbm_dims():
    p = HBM
    groups = [
        ("采用截面 w08h20", [
            ["列宽", p["col_w"], "左右列相同"],
            ["槽宽 × 深", f'{p["ch_w"]:.3f} × {p["ch_h"]:.3f}', "封闭槽"],
            ["肋宽", p["fin_w"], "节距 1.600"],
            ["条数", float(p["n_ch"]), "单侧"],
            ["岸", p["land"], "两侧各一"],
            ["列长", p["col_len"], ""],
            ["单颗高", p["stack_h"], "四颗"],
            ["颗间间隙", p["gap_stack"], "三处"],
            ["加热长度", p["heat_len"], "四颗之和"],
            ["底铜", p["base"], ""],
            ["上铜板", p["lid"], ""],
            ["铜厚", p["plate_hbm"], "不含 TIM"],
            ["TIM", p["tim"], "不进板厚"],
        ]),
        ("在 95×75 板上的位置", [
            ["左列 x", p["margin_x"], "5–16"],
            ["右列 x", p["hbm_xr"], "79–90"],
            ["列到肋的缝", p["gap_rib"], ""],
            ["隔离肋", p["rib_w"], ""],
            ["下边距", p["y_end"], ""],
            ["板宽 / 板长", f'{p["plate_L"]:.3f} × {p["plate_W"]:.3f}', "GPU 板外形，HBM 区嵌在里面"],
        ]),
        ("对照截面（不采用）", [
            ["岸", p["land65"], "v2.0"],
            ["槽宽", p["ch60"], "v2.0"],
            ["肋宽", p["fin70"], "节距 1.30"],
            ["条数", float(p["n8"]), "单侧 8，两侧合计 16"],
        ]),
    ]
    return dim_page(
        "HBM 微通道冷板 · 结构尺寸说明", "DC-HBM-DIM-01",
        "采用行可以相加。对照行单独成组，不和采用行加在一起。",
        "列宽 11 mm 有两套都能闭合的填法。本说明采用 7×0.80 mm。",
        groups,
    )


def hbm_chain():
    return chain_html(
        "HBM 微通道冷板 · 尺寸链计算报告", "DC-HBM-CHN-01",
        "采用链全部闭合。对照的八槽链也闭合，两套不能混加。",
        "封闭环是列宽 11、列长 50、加热长 44、铜厚 8，以及这块区域接到 Die-A 和板长的位置。",
        HBM, HBM_CHAINS,
        extra="<p>GPU 外形 8.5 mm 与本区铜厚 8.0 mm 不是同一条厚度链。差 0.5 mm，数值上等于 GPU 报告里的钎缝，但 HBM 上铜板 4.0 mm 已经是另一种盖法。这项记为待确认，不判成某一条链的不闭合。</p>",
    )


# ---------------------------------------------------------------------------
# Grace CPU and LPDDR share one plate
# ---------------------------------------------------------------------------

GRACE = dict(
    plate_L=200.0, plate_W=120.0, plate_T=8.0, cavity_y=108.0,
    seal=6.0, to_rail=0.5, rail_w=7.0, rail_gap=0.5,
    mem_w=50.0, gap_zone=16.0, cpu_w=40.0, cpu_x0=80.0, cpu_x1_margin=80.0,
    base=2.0, cpu_h=1.20, z_seal=0.30, z_cav=2.50, z_lid=2.0, z_part=3.2,
    n_ch=48, n_rib=49, ch_w=0.40, rib_thk=0.40, field=38.8, shore=0.6,
    y0=38.0, y1=82.0, wall=0.8, port=1.6, neck=1.2, heat=32.0,
    wet=40.0, rear_m=38.0,
    mem_y0=19.0, mem_y1=101.0, mem_heat=70.0, mem_wet=78.0, mem_margin=19.0,
    mem_ch_w=1.20, mem_ch_h=0.80, mem_cap=0.40, mem_n=6,
    pitch=50.0 / 6.0, pitch8=8.0, mem_win=50.0,
    slit_w=0.80, slit_h=1.20, slit_L=12.0,
)


def _y_pieces(heat_name):
    return [
        ("前端墙", "wall", "0.8"),
        ("前侧回液口", "port", "1.6，偶数槽"),
        ("隔墙", "wall", "0.8"),
        ("前侧供液口", "port", "1.6，奇数槽"),
        ("口与窗口间的实铜", "neck", "坐标相减 1.2，原表未单独命名"),
        ("受热窗", heat_name, ""),
        ("口与窗口间的实铜", "neck", "后侧同样 1.2"),
        ("后侧供液口", "port", "1.6，偶数槽入口"),
        ("隔墙", "wall", "0.8"),
        ("后侧回液口", "port", "1.6，奇数槽出口"),
        ("后端墙", "wall", "0.8"),
    ]


CPU_CHAINS = [
    Chain("外形X", "板宽", [
        ("左密封边", "seal", "空腔从 x=6 开始"),
        ("密封边到干管", "to_rail", "6 到 6.5"),
        ("左干管", "rail_w", "6.5–13.5"),
        ("干管到左内存窗", "rail_gap", "13.5–14"),
        ("左内存窗", "mem_w", "14–64"),
        ("内存到 CPU", "gap_zone", "64–80"),
        ("CPU 窗", "cpu_w", "80–120"),
        ("CPU 到右内存", "gap_zone", "120–136"),
        ("右内存窗", "mem_w", "136–186"),
        ("右内存到干管", "rail_gap", "186–186.5"),
        ("右干管", "rail_w", "186.5–193.5"),
        ("干管到密封边", "to_rail", "193.5–194"),
        ("右密封边", "seal", "194–200"),
    ], "plate_L", "逐项都是报告里的坐标差。左右干管、左右内存窗各用自己的输入，这里左右数值相同。"),
    Chain("外形Y密封", "Y 向密封边", [
        ("前密封", "seal", "空腔从 y=6"),
        ("空腔净长", "cavity_y", "6 到 114，按坐标单独输入 108"),
        ("后密封", "seal", ""),
    ], "plate_W", "6+108+6=120。"),
    Chain("厚度", "整板厚度", [
        ("底板", "base", "z 0–2.0"),
        ("CPU 槽深", "cpu_h", "z 2.0–3.2"),
        ("分型密封", "z_seal", "z 3.2–3.5"),
        ("盖板内腔", "z_cav", "z 3.5–6.0"),
        ("盖板顶", "z_lid", "z 6.0–8.0"),
    ], "plate_T", "2.0+1.2+0.3+2.5+2.0=8.0。"),
    Chain("CPU窗位", "CPU 窗在板上的 X", [
        ("窗左缘", "cpu_x0", "80"),
        ("窗宽", "cpu_w", "40"),
        ("窗右到板边", "cpu_x1_margin", "80，与左缘分开输入"),
    ], "plate_L", "80+40+80=200，窗口居中。"),
    Chain("肋场", "CPU 肋场宽度", [
        ("49 根肋", "n_rib*rib_thk", "肋厚 0.40"),
        ("48 条槽", "n_ch*ch_w", "槽宽 0.40"),
    ], "field", "19.6+19.2=38.8，对上报告写的肋场宽。"),
    Chain("窗内岸", "CPU 窗内的左右岸", [
        ("左岸", "shore", "80.6−80"),
        ("肋场", "field", ""),
        ("右岸", "shore", "120−119.4"),
    ], "cpu_w", "0.6+38.8+0.6=40。肋场起点 X 80.6，终点 119.4。"),
    Chain("Y口带", "CPU 口带，补上两段未命名实铜", _y_pieces("heat"),
          "y1-y0", "原表从 42.8 跳到 44、从 76 跳到 77.2。两段各 1.2 mm。补上后 38 到 82 等于 44。"),
    Chain("Y全长", "CPU 口带加上前后边距", [
        ("前边距", "y0", "0 到前端墙 38"),
        ("口带跨度", "y1-y0", "44"),
        ("后边距", "rear_m", "82 到 120，与前边距分开输入"),
    ], "plate_W", "38+44+38=120。口带中心在 Y=60。"),
    Chain("润湿奇", "奇数槽润湿长度", [
        ("前供液口", "port", "41.2 起"),
        ("前实铜", "neck", ""),
        ("受热", "heat", ""),
        ("后实铜", "neck", ""),
        ("后侧偶数槽的供液口区", "port", "奇数槽此段槽顶封，槽长仍在"),
        ("隔墙", "wall", ""),
        ("后回液口", "port", "到 81.2"),
    ], "wet", "41.2 到 81.2 等于报告的 40 mm。"),
    Chain("润湿偶", "偶数槽润湿长度", [
        ("前回液口", "port", "38.8 起"),
        ("隔墙", "wall", ""),
        ("前供液口区", "port", "偶数槽此段槽顶封"),
        ("前实铜", "neck", ""),
        ("受热", "heat", ""),
        ("后实铜", "neck", ""),
        ("后供液口", "port", "到 78.8"),
    ], "wet", "38.8 到 78.8 等于 40 mm。"),
]


LPD_CHAINS = [
    Chain("外形X", "板宽（与 CPU 同一块铜）", CPU_CHAINS[0].segments, "plate_L",
          "LLDDRAM 区不是单独的外形。左右窗是这条链里的两个 50 mm。"),
    Chain("厚度对齐", "内存槽接到分型面", [
        ("底板", "base", ""),
        ("内存槽深", "mem_ch_h", "只铣 0.80"),
        ("槽顶铜", "mem_cap", "0.40，补到 z=3.2"),
    ], "z_part", "2.0+0.80+0.40=3.2，与 CPU 槽 2.0+1.2 齐平。"),
    Chain("CPU对照厚", "CPU 槽接到同一分型面", [
        ("底板", "base", ""),
        ("CPU 槽深", "cpu_h", ""),
    ], "z_part", "用来确认两区在 z=3.2 相遇。"),
    Chain("整板厚", "分型面以上加到外形", [
        ("分型面高度", "z_part", ""),
        ("分型密封", "z_seal", ""),
        ("内腔", "z_cav", ""),
        ("盖顶", "z_lid", ""),
    ], "plate_T", "3.2+0.3+2.5+2.0=8.0。"),
    Chain("节距采用", "左窗（右窗同宽）按均分节距", [
        ("左岸，半肋", "(pitch-mem_ch_w)/2", "节距取 50/6"),
        ("6 条槽", "mem_n*mem_ch_w", "宽 1.20"),
        ("5 条肋", "(mem_n-1)*(pitch-mem_ch_w)", ""),
        ("右岸，半肋", "(pitch-mem_ch_w)/2", ""),
    ], "mem_win", "和等于 6×节距。节距是独立输入 50/6，不是在格子里写 =50/6 再去减窗口。"),
    Chain("节距8", "若节距按 8.00 mm、岸仍取半肋", [
        ("左岸", "(pitch8-mem_ch_w)/2", ""),
        ("6 条槽", "mem_n*mem_ch_w", ""),
        ("5 条肋", "(mem_n-1)*(pitch8-mem_ch_w)", ""),
        ("右岸", "(pitch8-mem_ch_w)/2", ""),
    ], "mem_win", "6×8.00=48.00，窗口 50.00，差 2.00 mm。不能按“约 8 mm”出图。",
          adopted=False),
    Chain("Y口带", "单侧内存口带，补上两段 1.2 mm", _y_pieces("mem_heat"),
          "mem_y1-mem_y0", "19 到 101 的跨度是 82。原表同样少写两段 1.2 mm。"),
    Chain("Y全长", "内存口带加前后边距", [
        ("前边距", "mem_y0", "前端墙起于 19"),
        ("口带跨度", "mem_y1-mem_y0", "82"),
        ("后边距", "mem_margin", "101 到 120"),
    ], "plate_W", "19+82+19=120。"),
    Chain("润湿", "单侧奇数槽润湿长度", [
        ("前供液口", "port", "22.2 起"),
        ("前实铜", "neck", ""),
        ("受热 70", "mem_heat", ""),
        ("后实铜", "neck", ""),
        ("后侧供液口区", "port", ""),
        ("隔墙", "wall", ""),
        ("后回液口", "port", "到 100.2"),
    ], "mem_wet", "22.2 到 100.2 等于 78 mm。偶数槽 19.8 到 97.8 同长。"),
]


def grace_svg(kind):
    s, ox, oy = 3.15, 30, 24

    def X(v):
        return ox + v * s

    def Y(v):
        return oy + (120 - v) * s

    def box(x, y, w, h, fill, stroke="#5c3a17"):
        return R(X(x), Y(y + h), w * s, h * s, fill, stroke)

    parts = [box(0, 0, 200, 120, "#f4e0cf")]
    parts.append(box(14, 25, 50, 70, "#efe6c9", "#8a6a12"))
    parts.append(box(136, 25, 50, 70, "#efe6c9", "#8a6a12"))
    parts.append(box(80, 44, 40, 32, "#f0c2b4", "#9d1c1c"))
    parts.append(box(6.5, 18, 7, 84, "#d9e9f7", "#1f6fb2"))
    parts.append(box(186.5, 18, 7, 84, "#f6dcd8", "#9d1c1c"))
    hi = "#9d1c1c" if kind == "cpu" else "#8a6a12"
    if kind == "cpu":
        parts.append(box(80.6, 44, 38.8, 32, "#f7d4cb", hi))
        parts.append(T(X(100), Y(58), "CPU 48 槽", 13, hi, "middle"))
    else:
        parts.append(box(14, 25, 50, 70, "#f3e7b5", hi))
        parts.append(box(136, 25, 50, 70, "#f3e7b5", hi))
        parts.append(T(X(39), Y(60), "LPDDR ×6", 13, hi, "middle"))
        parts.append(T(X(161), Y(60), "LPDDR ×6", 13, hi, "middle"))
    parts.append(T(X(100), Y(-6), "+X  200 mm", 12, "#33404d", "middle"))
    parts.append(T(12, Y(60), "+Y", 12, "#33404d"))
    cap = "图 1 · 同一块 200×120 冷板。本页强调 CPU 窗。" if kind == "cpu" else "图 1 · 同一块冷板上的左右 LPDDR 窗，各 50×70。"
    return svg_wrap("".join(parts), 700, 430, cap)


def cpu_layout():
    body = f"""
<p class="lead">Grace 的 CPU 冷板是 CP-GRACE-MC-01 的中部窗口，不是第二块铜。外形 200×120×8 mm 与两侧 LPDDR 共用。本页只把 CPU 的 48 条槽和它的口带闭合。</p>
<h2>1　平面</h2>
<p>原点在左下角，+X 从左接头到右接头，+Y 朝后面板。CPU 窗 X 80–120、Y 44–76，即 40×32 mm，两个方向都居中。肋场 38.8 mm 放在窗内，左右各余 0.6 mm，所以肋场是 X 80.6–119.4。从左数第 1 条是奇数槽。</p>
{grace_svg("cpu")}
<h2>2　流向</h2>
<p>槽沿 Y。奇数槽在前侧进液、流向 +Y，偶数槽在后侧进液、流向 −Y。Y 向两端用 0.8 mm 铜墙封死，水从槽顶的 Z 向口进出。前侧两个口带中间再隔 0.8 mm，后侧同样。受热段槽顶封死。</p>
<p>报告的口带表在前侧供液口（止于 42.8）和受热窗（起于 44）之间，以及受热窗（止于 76）和后侧供液口（起于 77.2）之间，各有 1.2 mm 没有单独起名。尺寸链把这两段补成实铜环之后，38 到 82 的跨度才是 44 mm。</p>
<h2>3　厚度与整板的水</h2>
<p>z 0–2.0 底板，2.0–3.2 是 CPU 槽，3.2–3.5 分型面，3.5–6.0 盖板内腔，6.0–8.0 盖顶。左右干管在 X 6.5–13.5 和 186.5–193.5，局部加深。接头中心 Y=60。入口孔板 4×1.04 mm 在接头里，不参与外形链。</p>
"""
    return page("Grace CPU 冷板 · 结构布局说明", "DC-CPU-LAY-01",
                "CP-GRACE-MC-01 的 CPU 区。与 LPDDR 同一块铜。", body)


def cpu_dims():
    p = GRACE
    groups = [
        ("共用外形", [
            ["长 × 宽 × 厚", f'{p["plate_L"]:.3f} × {p["plate_W"]:.3f} × {p["plate_T"]:.3f}', "平面仍是候选"],
            ["密封边", p["seal"], "四周"],
            ["干管宽", p["rail_w"], "左右各一，深 5，z 1–6"],
            ["内存窗宽", p["mem_w"], "本页只作为板宽链的一环"],
            ["区间间隙", p["gap_zone"], "内存窗与 CPU 窗之间"],
        ]),
        ("CPU 区", [
            ["窗", f'{p["cpu_w"]:.3f} × {p["heat"]:.3f}', "X 80–120，Y 44–76"],
            ["条数", float(p["n_ch"]), "奇偶各 24"],
            ["肋数", float(p["n_rib"]), ""],
            ["槽宽 × 深", f'{p["ch_w"]:.3f} × {p["cpu_h"]:.3f}', ""],
            ["肋厚", p["rib_thk"], "节距 0.80"],
            ["肋场宽", p["field"], ""],
            ["窗内岸", p["shore"], "两侧"],
            ["润湿长度", p["wet"], "含端口"],
            ["端墙 / 隔墙", p["wall"], "Y 向"],
            ["Z 向口沿 Y", p["port"], "沿 X 等于槽宽 0.40"],
            ["口与窗之间的实铜", p["neck"], "原表未命名"],
            ["口带起点 / 终点", f'{p["y0"]:.3f} / {p["y1"]:.3f}', "前端墙外缘到后端墙外缘"],
        ]),
        ("厚度", [
            ["底板", p["base"], ""],
            ["槽深", p["cpu_h"], ""],
            ["分型密封", p["z_seal"], ""],
            ["内腔", p["z_cav"], ""],
            ["盖顶", p["z_lid"], ""],
        ]),
    ]
    return dim_page("Grace CPU 冷板 · 结构尺寸说明", "DC-CPU-DIM-01",
                    "CPU 区尺寸。板宽链里的内存窗见 LLDDRAM 那一份的细部。",
                    "肋场 38.8 mm 与 49×0.40+48×0.40 分开存放，核实页用公式核对二者。",
                    groups)


def cpu_chain():
    return chain_html(
        "Grace CPU 冷板 · 尺寸链计算报告", "DC-CPU-CHN-01",
        "采用链闭合。口带链必须补上两段 1.2 mm，否则 38 到 82 会短 2.4 mm。",
        "板宽、板厚、肋场、窗内岸、补环后的口带、以及两条润湿长度，都与报告里的另一个数一致。",
        GRACE, CPU_CHAINS,
    )


def lpd_layout():
    body = f"""
<p class="lead">LLDDRAM 冷板按本目录和 Grace 报告的命名，指的是 CP-GRACE-MC-01 上两侧的 LPDDR5X 窗口，不是一块独立外形。左右各 50×70 mm，各 6 条宽槽。任务名 LLDDRAM 与报告中的 LPDDR5X 是同一区域。</p>
<h2>1　平面</h2>
<p>左窗 X 14–64，右窗 X 136–186，Y 都是 25–95。条数是偶数，奇数槽流向 +Y，偶数槽流向 −Y，规则与 CPU 相同。Z 向口的 Y 向尺寸仍是 1.6 mm，口宽等于槽宽 1.20 mm。</p>
{grace_svg("lpd")}
<p>报告写节距“约 8 mm”。若按 8.00 mm 并且两岸仍各取半个肋，六条槽只占 48 mm，50 mm 窗口还剩 2 mm，没有第三种岸去接。能闭合的填法是节距 50/6 = 8.333 mm，岸为半肋 3.567 mm，肋净宽 7.133 mm。网格方案已经按这个节距铺满窗口。</p>
<h2>2　厚度</h2>
<p>内存槽只深 0.80 mm。上面留 0.40 mm 铜，把槽顶抬到 z=3.2，与 CPU 的 1.20 mm 深槽齐平。再向上的 0.3+2.5+2.0 与 CPU 共用，外形 8.0 mm。</p>
<h2>3　限流缝</h2>
<p>每侧一条 0.80×1.20 mm、长 12 mm 的缝，放在该侧供液分成前后两路之前。三个尺寸有来源，平面坐标没有给出，所以不进入闭合链。</p>
"""
    return page("LLDDRAM 冷板 · 结构布局说明", "DC-LPD-LAY-01",
                "LPDDR5X 左右窗。节距按 8.333 mm 才能铺满 50 mm。", body)


def lpd_dims():
    p = GRACE
    groups = [
        ("窗口", [
            ["左窗 X", "14–64", "宽 50"],
            ["右窗 X", "136–186", "宽 50"],
            ["Y", "25–95", "高 70，受热长度"],
            ["条数", float(p["mem_n"]), "每侧，奇偶各 3"],
            ["槽宽 × 深", f'{p["mem_ch_w"]:.3f} × {p["mem_ch_h"]:.3f}', ""],
            ["槽顶铜", p["mem_cap"], "z 2.8–3.2"],
            ["采用节距", round(p["pitch"], 6), "50/6"],
            ["半肋岸", round((p["pitch"] - p["mem_ch_w"]) / 2, 6), "两侧"],
            ["肋净宽", round(p["pitch"] - p["mem_ch_w"], 6), ""],
            ["若用 8.00 的占位", 48.0, "与窗口差 2 mm，不采用"],
            ["润湿长度", p["mem_wet"], "含端口"],
            ["限流缝", f'{p["slit_w"]:.3f} × {p["slit_h"]:.3f} × {p["slit_L"]:.3f}', "位置待冻结"],
        ]),
        ("口带", [
            ["前端墙外缘", p["mem_y0"], "19"],
            ["后端墙外缘", p["mem_y1"], "101"],
            ["端墙 / 隔墙", p["wall"], ""],
            ["口长", p["port"], ""],
            ["未命名实铜", p["neck"], "两处"],
            ["前后边距", p["mem_margin"], "各 19"],
        ]),
    ]
    return dim_page("LLDDRAM 冷板 · 结构尺寸说明", "DC-LPD-DIM-01",
                    "与 CPU 共用 200×120×8。此处只列内存窗。",
                    "节距保留 6 位小数。工作簿里用 50/6 的浮点值作为输入，六倍之后回到 50。",
                    groups)


def lpd_chain():
    return chain_html(
        "LLDDRAM 冷板 · 尺寸链计算报告", "DC-LPD-CHN-01",
        "采用节距 8.333 mm 的链闭合。节距 8.00 mm 的对照链不闭合，差 2 mm。",
        "内存区与 CPU 区在 z=3.2 对齐，外形 8.0 mm 闭合。口带同样要补两段 1.2 mm。",
        GRACE, LPD_CHAINS,
    )


# ---------------------------------------------------------------------------
# Excel
# ---------------------------------------------------------------------------

THIN = Border(
    left=Side(style="thin", color="D5DDE6"),
    right=Side(style="thin", color="D5DDE6"),
    top=Side(style="thin", color="D5DDE6"),
    bottom=Side(style="thin", color="D5DDE6"),
)
FILL_IN = PatternFill("solid", fgColor="D6E6F5")
FILL_HD = PatternFill("solid", fgColor="0E3A5D")
FILL_SUM = PatternFill("solid", fgColor="EEF3F8")
FILL_NO = PatternFill("solid", fgColor="F8E8C8")
FONT_HD = Font(name="微软雅黑", color="FFFFFF", bold=True, size=11)
FONT = Font(name="微软雅黑", size=11)
FONT_B = Font(name="微软雅黑", size=11, bold=True)
FONT_IN = Font(name="微软雅黑", size=11, color="0B3A66")


def _apply_widths(ws, widths):
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.page_setup.paperSize = ws.PAPERSIZE_A4
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddHeader.left.text = ws.title
    ws.oddFooter.right.text = "尺寸核实2  ·  " + DATE
    ws.page_setup.horizontalCentered = True
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 110
    ws.page_margins.left = 0.5
    ws.page_margins.right = 0.5
    ws.page_margins.top = 0.7
    ws.page_margins.bottom = 0.6
    ws.sheet_properties.tabColor = "0E3A5D"


def write_book(path, doc, title, params, param_notes, chains, layout_rows, dim_rows):
    wb = Workbook()
    cover = wb.active
    cover.title = "封面"

    src = wb.create_sheet("输入参数", 1)
    lay = wb.create_sheet("结构布局", 2)
    dim = wb.create_sheet("结构尺寸", 3)
    chn = wb.create_sheet("尺寸核实2", 4)

    for ws in (cover, src, lay, dim, chn):
        ws.sheet_view.showGridLines = False
        ws.page_setup.paperSize = ws.PAPERSIZE_A4
        ws.page_setup.fitToPage = True
        ws.page_setup.fitToWidth = 1
        ws.page_setup.fitToHeight = 0
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.horizontalCentered = True
        ws.oddFooter.center.text = "AIDCtms 冷却板  ·  尺寸核实2  ·  " + DATE
        ws.oddFooter.right.text = "第 &P 页"

    cover["A1"] = title
    cover["A1"].font = Font(name="微软雅黑", size=20, bold=True, color="0E3A5D")
    cover.merge_cells("A1:B1")
    lines = [
        ("文件", doc),
        ("日期", DATE),
        ("核实内容", "结构布局坐标、结构尺寸、名义尺寸链"),
        ("输入", "工作表「输入参数」中的蓝字。改蓝字后，尺寸核实2 的判定跟着变。"),
        ("公式", "尺寸核实2 的和、差、判定都是公式，不要在那些格子里改数字。"),
        ("公差", "源文件没有线性公差。本表只核名义尺寸是否相加等于封闭环。"),
        ("打印", "各表已按 A4 横向设置。直接打印或导出 PDF，不必再改列宽。"),
    ]
    for i, (k, v) in enumerate(lines, 3):
        cover.cell(i, 1, k).font = FONT_B
        cover.cell(i, 2, v).font = FONT
        cover.cell(i, 2).alignment = Alignment(wrap_text=True)
        cover.row_dimensions[i].height = 32
    cover.row_dimensions[1].height = 36
    cover.column_dimensions["A"].width = 18
    cover.column_dimensions["B"].width = 88
    cover.page_setup.orientation = "portrait"
    cover.page_setup.fitToWidth = 1
    cover.page_setup.fitToHeight = 1
    cover.print_title_rows = "1:1"
    cover.oddHeader.left.text = title
    cover.sheet_properties.tabColor = "0E3A5D"

    src["A1"] = "输入参数（蓝字可改）"
    src["A1"].font = Font(name="微软雅黑", size=16, bold=True, color="0E3A5D")
    src.merge_cells("A1:D1")
    src.row_dimensions[1].height = 24
    for col, h in enumerate(["名称", "符号", "数值 / mm", "说明"], 1):
        cell = src.cell(3, col, h)
        cell.font = FONT_HD
        cell.fill = FILL_HD
        cell.alignment = Alignment(horizontal="center")
    row = 4
    for key, val in params.items():
        src.cell(row, 1, param_notes.get(key, key)).font = FONT
        src.cell(row, 2, key).font = Font(name="Consolas", size=10)
        cell = src.cell(row, 3, float(val))
        cell.font = FONT_IN
        cell.fill = FILL_IN
        cell.number_format = "0.000000"
        cell.alignment = Alignment(horizontal="center")
        src.cell(row, 4, "输入").font = FONT
        for c in range(1, 5):
            src.cell(row, c).border = THIN
            src.cell(row, c).alignment = Alignment(wrap_text=True, vertical="center",
                                                   horizontal="center" if c > 1 else "left")
        src.row_dimensions[row].height = 20
        wb.defined_names.add(DefinedName(name=key, attr_text=f"'输入参数'!$C${row}"))
        row += 1
    src.freeze_panes = "A4"
    src.auto_filter.ref = f"A3:D{row-1}"
    src.print_title_rows = "1:3"
    src.page_setup.orientation = "landscape"
    src.oddHeader.left.text = title + "  ·  输入参数"
    _apply_widths(src, [42, 22, 18, 36])
    src.row_dimensions[3].height = 22

    lay["A1"] = "结构布局（与布局说明同一坐标）"
    lay["A1"].font = Font(name="微软雅黑", size=16, bold=True, color="0E3A5D")
    lay.merge_cells("A1:C1")
    for col, h in enumerate(["项目", "坐标或关系", "说明"], 1):
        cell = lay.cell(3, col, h)
        cell.font = FONT_HD
        cell.fill = FILL_HD
        cell.alignment = Alignment(horizontal="center", vertical="center")
    for i, rec in enumerate(layout_rows, 4):
        for c, val in enumerate(rec, 1):
            cell = lay.cell(i, c, val)
            cell.font = FONT
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            cell.border = THIN
        lay.row_dimensions[i].height = 32
    lay.freeze_panes = "A4"
    lay.print_title_rows = "1:3"
    lay.page_setup.orientation = "landscape"
    lay.oddHeader.left.text = title + "  ·  结构布局"
    lay.auto_filter.ref = f"A3:C{3+len(layout_rows)}"
    _apply_widths(lay, [28, 42, 55])
    lay.row_dimensions[1].height = 24
    lay.row_dimensions[3].height = 22

    dim["A1"] = "结构尺寸"
    dim["A1"].font = Font(name="微软雅黑", size=16, bold=True, color="0E3A5D")
    dim.merge_cells("A1:D1")
    for col, h in enumerate(["分组", "项目", "尺寸", "说明"], 1):
        cell = dim.cell(3, col, h)
        cell.font = FONT_HD
        cell.fill = FILL_HD
        cell.alignment = Alignment(horizontal="center")
    for i, rec in enumerate(dim_rows, 4):
        for c, val in enumerate(rec, 1):
            cell = dim.cell(i, c, val if not isinstance(val, float) else val)
            cell.font = FONT
            cell.border = THIN
            cell.alignment = Alignment(wrap_text=True, vertical="center")
            if isinstance(val, float):
                cell.number_format = "0.000"
                cell.alignment = Alignment(horizontal="center", vertical="center")
        dim.row_dimensions[i].height = 22
    dim.freeze_panes = "A4"
    dim.print_title_rows = "1:3"
    dim.page_setup.orientation = "landscape"
    dim.oddHeader.left.text = title + "  ·  结构尺寸"
    dim.auto_filter.ref = f"A3:D{3+len(dim_rows)}"
    _apply_widths(dim, [24, 36, 22, 48])
    dim.row_dimensions[1].height = 24
    dim.row_dimensions[3].height = 22

    chn["A1"] = "尺寸核实2 · 组成环重新相加"
    chn["A1"].font = Font(name="微软雅黑", size=16, bold=True, color="0E3A5D")
    chn.merge_cells("A1:G1")
    chn["A2"] = "蓝字来自输入参数。黑色数字是公式。判定公差 0.001 mm，只用于浮点，不是制图公差。"
    chn["A2"].font = FONT
    chn.merge_cells("A2:G2")
    headers = ["链", "序号", "组成环", "计算式", "数值 / mm", "采用", "说明"]
    r = 4
    judge_cells = []
    for ch in chains:
        chn.merge_cells(start_row=r, start_column=1, end_row=r, end_column=7)
        head = chn.cell(r, 1, ch.title)
        head.font = FONT_HD
        head.fill = FILL_HD
        chn.row_dimensions[r].height = 22
        r += 1
        for c, h in enumerate(headers, 1):
            cell = chn.cell(r, c, h)
            cell.font = FONT_B
            cell.fill = FILL_SUM
            cell.border = THIN
            cell.alignment = Alignment(horizontal="center")
        r += 1
        first = r
        for i, (name, expr, note) in enumerate(ch.segments, 1):
            chn.cell(r, 1, ch.cid).font = FONT
            chn.cell(r, 2, i).font = FONT
            chn.cell(r, 2).alignment = Alignment(horizontal="center")
            chn.cell(r, 3, name).font = FONT
            chn.cell(r, 4, expr).font = Font(name="Consolas", size=10)
            cell = chn.cell(r, 5, f"={expr}")
            cell.font = FONT
            cell.number_format = "0.000"
            cell.alignment = Alignment(horizontal="center")
            chn.cell(r, 6, "是" if ch.adopted else "否").font = FONT
            chn.cell(r, 6).alignment = Alignment(horizontal="center")
            if not ch.adopted:
                chn.cell(r, 6).fill = FILL_NO
            chn.cell(r, 7, note).font = FONT
            for c in range(1, 8):
                chn.cell(r, c).border = THIN
                chn.cell(r, c).alignment = Alignment(wrap_text=True, vertical="center",
                                                     horizontal="center" if c in (2, 5, 6) else "left")
            chn.row_dimensions[r].height = 20
            r += 1
        last = r - 1
        chn.cell(r, 3, "组成环之和").font = FONT_B
        sum_cell = chn.cell(r, 5, f"=SUM(E{first}:E{last})")
        sum_cell.font = FONT_B
        sum_cell.number_format = "0.000"
        sum_cell.fill = FILL_SUM
        sum_cell.alignment = Alignment(horizontal="center")
        for c in range(1, 8):
            chn.cell(r, c).border = THIN
            chn.cell(r, c).fill = FILL_SUM
        sum_row = r
        r += 1
        chn.cell(r, 3, "封闭环").font = FONT_B
        tgt = chn.cell(r, 5, f"={ch.target}")
        tgt.font = FONT_B
        tgt.number_format = "0.000"
        tgt.alignment = Alignment(horizontal="center")
        for c in range(1, 8):
            chn.cell(r, c).border = THIN
        tgt_row = r
        r += 1
        chn.cell(r, 3, "差值（和 − 封闭环）").font = FONT
        diff = chn.cell(r, 5, f"=E{sum_row}-E{tgt_row}")
        diff.number_format = "0.000"
        diff.font = FONT
        diff.alignment = Alignment(horizontal="center")
        for c in range(1, 8):
            chn.cell(r, c).border = THIN
        r += 1
        chn.cell(r, 3, "判定").font = FONT_B
        judge = chn.cell(r, 5, f'=IF(ABS(E{sum_row}-E{tgt_row})<0.001,"闭合","不闭合")')
        judge.font = FONT_B
        judge.alignment = Alignment(horizontal="center")
        for c in range(1, 8):
            chn.cell(r, c).border = THIN
        judge_cells.append(judge.coordinate)
        chn.row_dimensions[r].height = 22
        r += 2

    green = PatternFill("solid", fgColor="C6EFCE")
    red = PatternFill("solid", fgColor="F4C7C3")
    for coord in judge_cells:
        chn.conditional_formatting.add(coord, FormulaRule(formula=[f'{coord}="闭合"'], fill=green))
        chn.conditional_formatting.add(coord, FormulaRule(formula=[f'{coord}="不闭合"'], fill=red))

    chn.freeze_panes = "A4"
    chn.print_title_rows = "1:2"
    chn.page_setup.orientation = "landscape"
    chn.page_setup.fitToWidth = 1
    chn.page_setup.fitToHeight = 0
    chn.oddHeader.left.text = title + "  ·  尺寸核实2"
    chn.page_setup.paperSize = chn.PAPERSIZE_A4
    chn.sheet_properties.pageSetUpPr.fitToPage = True
    _apply_widths(chn, [16, 8, 32, 28, 16, 10, 42])
    chn.row_dimensions[1].height = 24
    chn.row_dimensions[2].height = 22

    wb.save(path)


def notes_of(params, text):
    return {k: text.get(k, k) for k in params}


def main():
    books = []

    def check(name, params, chains):
        bad = []
        for ch in chains:
            ok = ch.closed(params)
            _, total, want = ch.values(params)
            if ch.adopted and not ok:
                bad.append(f"{name}/{ch.cid}: {total} vs {want}")
            if ch.cid == "节距8" and ok:
                bad.append("8 mm 节距不应闭合")
            if ch.cid == "对照截面" and not ok:
                bad.append(f"对照截面应闭合: {total} vs {want}")
            print(f"  {name} {ch.cid}: {total:.6f} / {want:.6f} {'闭合' if ok else '不闭合'}")
        if bad:
            raise SystemExit("\n".join(bad))

    check("GPU", GPU, GPU_CHAINS)
    check("HBM", HBM, HBM_CHAINS)
    check("CPU", GRACE, CPU_CHAINS)
    check("LPD", GRACE, LPD_CHAINS)

    files = {
        "GPU射流冲击微通道冷板_结构布局说明.html": gpu_layout(),
        "GPU射流冲击微通道冷板_结构尺寸说明.html": gpu_dims(),
        "GPU射流冲击微通道冷板_尺寸链计算报告.html": gpu_chain(),
        "HBM微通道冷板_结构布局说明.html": hbm_layout(),
        "HBM微通道冷板_结构尺寸说明.html": hbm_dims(),
        "HBM微通道冷板_尺寸链计算报告.html": hbm_chain(),
        "GraceCPU冷板_结构布局说明.html": cpu_layout(),
        "GraceCPU冷板_结构尺寸说明.html": cpu_dims(),
        "GraceCPU冷板_尺寸链计算报告.html": cpu_chain(),
        "LLDDRAM冷板_结构布局说明.html": lpd_layout(),
        "LLDDRAM冷板_结构尺寸说明.html": lpd_dims(),
        "LLDDRAM冷板_尺寸链计算报告.html": lpd_chain(),
    }
    for name, text in files.items():
        (ROOT / name).write_text(text, encoding="utf-8")
        print("html", name)

    gpu_notes = {
        "plate_L": "板宽", "plate_W": "板长", "plate_T": "外形厚", "cav_t": "腔体厚",
        "margin_x": "左右边距", "hbm_w": "HBM 列宽", "gap_rib": "肋侧缝", "rib_w": "隔离肋宽",
        "die_w": "die 宽", "hbi": "HBI", "die_h": "die 高", "die_ax": "Die-A 左缘",
        "die_ay": "Die-A 下缘", "die_bx": "Die-B 左缘", "y_end": "Y 边距", "col_len": "列长",
        "hbm_xr": "右列 x", "base_cu": "余铜", "groove_h": "槽深", "jet_h": "喷距",
        "lid_t": "喷嘴板", "braze": "钎缝", "n_jx": "X 格数", "n_jy": "Y 格数",
        "pitch_x": "X 节距", "pitch_y": "Y 节距", "cov_y": "Y 覆盖", "oh_y": "Y 超出",
        "env_allow": "外包络定额", "env_y": "外包络", "env_rem": "外包络余量",
        "ch_w": "槽宽", "ch_p": "槽节距", "n_ch_die": "die 内节距数", "n_slot": "每胞槽数",
        "land_cell": "胞边半肋", "slot_w": "胞内槽宽", "slot_rib": "胞内肋", "slit": "回液缝",
        "D_jet": "孔径 UC01b", "D_rpt": "孔径 报告正文", "hole_in": "孔中心边距",
        "hole_span_x": "孔距 X", "hole_span_y": "孔距 Y", "stack_h": "HBM 单颗高",
        "gap_stack": "颗间间隙",
    }
    write_book(
        ROOT / "GPU射流冲击微通道冷板_尺寸核实2.xlsx",
        "DC-GPU-VER2", "GPU 射流冲击微通道冷板",
        GPU, gpu_notes, GPU_CHAINS,
        [
            ["原点", "左下角", "X 向右 95 mm，Y 向上 75 mm，芯片面在 z 小端"],
            ["Die-A", "x 19–46，y 23.5–51.5", "27×28，射流 9×12"],
            ["NV-HBI", "x 46–49", "3 mm，缝上不打密孔"],
            ["Die-B", "x 49–76，y 23.5–51.5", "与 Die-A 同尺寸"],
            ["左 HBM 列", "x 5–16，y 12.5–62.5", "四颗 11 mm，间隙 2 mm"],
            ["右 HBM 列", "x 79–90，y 12.5–62.5", "与左列对称"],
            ["隔离肋", "x 16.5–18.5 与 76.5–78.5", "宽 2，长 50"],
            ["射流胞", "3.0 × 2.4", "孔在胞心，采用孔径 0.40"],
            ["短槽", "沿 X，节距沿 Y 0.80", "每胞 3 条，宽 0.40，深 1.50"],
            ["进液带", "y 66–73，x 8，宽 79", "板上沿"],
            ["出液带", "y 2–9，x 8，宽 79", "板下沿"],
            ["安装孔", "中心 4.5/90.5 与 4.5/70.5", "孔径 3.4，不进中心距链"],
            ["厚度", "余铜 2 + 槽 1.5 + 喷距 2 + 喷嘴板 2.5 + 钎缝 0.5", "外形 8.5"],
        ],
        [
            ["外形", "板宽", 95.0, "X"],
            ["外形", "板长", 75.0, "Y"],
            ["外形", "板厚", 8.5, "含钎缝 0.5"],
            ["外形", "腔体厚", 8.0, "不含钎缝"],
            ["分区", "边距", 5.0, "左右相同"],
            ["分区", "HBM 列宽", 11.0, ""],
            ["分区", "单颗高", 11.0, "四颗"],
            ["分区", "颗间间隙", 2.0, "三处，不加热"],
            ["分区", "隔离肋", 2.0, "长 50"],
            ["分区", "肋侧缝", 0.5, "每侧两道"],
            ["分区", "die 宽", 27.0, ""],
            ["分区", "die 高", 28.0, ""],
            ["分区", "HBI", 3.0, ""],
            ["射流", "X 节距", 3.0, "9 格"],
            ["射流", "Y 节距", 2.4, "12 格，覆盖 28.8"],
            ["射流", "孔径，采用", 0.40, "UC01b"],
            ["射流", "孔径，对照", 0.50, "设计报告正文，不进孔位链"],
            ["射流", "喷距", 2.0, ""],
            ["短槽", "槽宽", 0.40, ""],
            ["短槽", "槽深", 1.50, ""],
            ["短槽", "节距", 0.80, "肋 0.40"],
            ["厚度", "余铜", 2.0, ""],
            ["厚度", "喷嘴板", 2.5, ""],
            ["厚度", "钎缝", 0.5, ""],
            ["安装", "孔中心边距", 4.5, ""],
            ["安装", "孔距 X", 86.0, ""],
            ["安装", "孔距 Y", 66.0, ""],
        ],
    )
    print("xlsx GPU")

    hbm_notes = {k: k for k in HBM}
    hbm_notes.update({
        "col_w": "列宽", "ch_w": "槽宽", "ch_h": "槽深", "fin_w": "肋宽", "n_ch": "槽数",
        "land": "岸", "col_len": "列长", "stack_h": "单颗高", "gap_stack": "间隙",
        "n_stack": "颗数", "heat_len": "加热长", "base": "底铜", "lid": "上铜板",
        "plate_hbm": "铜厚", "tim": "TIM", "land65": "对照岸", "ch60": "对照槽宽",
        "fin70": "对照肋", "n8": "对照槽数", "plate_L": "板宽", "plate_W": "板长",
        "margin_x": "左边距", "gap_rib": "缝", "rib_w": "肋", "die_w": "die 宽",
        "hbi": "HBI", "y_end": "Y 边距", "hbm_xr": "右列 x", "die_ax": "Die-A 左缘",
    })
    write_book(
        ROOT / "HBM微通道冷板_尺寸核实2.xlsx",
        "DC-HBM-VER2", "HBM 微通道冷板",
        HBM, hbm_notes, HBM_CHAINS,
        [
            ["左列", "x 5–16，y 12.5–62.5", "宽 11，长 50"],
            ["右列", "x 79–90，y 12.5–62.5", "与左列同一截面"],
            ["四颗", "y 12.5 / 25.5 / 38.5 / 51.5", "各高 11，间隙 2，加热合计 44"],
            ["与 die 的关系", "列外 0.5 缝 + 2.0 肋 + 0.5 缝", "接到 Die-A 的 x=19"],
            ["采用截面", "7 条 0.80×2.00，肋 0.80，岸 0.30", "w08h20，槽顶封死"],
            ["厚度", "底铜 2 + 槽 2 + 上铜板 4", "铜厚 8，TIM 0.080 不进板厚"],
            ["对照截面", "8 条 0.60，肋 0.70，岸 0.65", "也能合成 11 mm，本板不采用"],
        ],
        [
            ["采用", "列宽", 11.0, ""],
            ["采用", "槽宽", 0.80, ""],
            ["采用", "槽深", 2.00, "封闭"],
            ["采用", "肋宽", 0.80, "节距 1.60"],
            ["采用", "条数", 7.0, "单侧"],
            ["采用", "岸", 0.30, "两侧"],
            ["采用", "列长", 50.0, ""],
            ["采用", "加热长", 44.0, "四颗"],
            ["采用", "底铜", 2.0, ""],
            ["采用", "上铜板", 4.0, ""],
            ["采用", "铜厚", 8.0, "不含 TIM"],
            ["采用", "TIM", 0.080, "不进板厚"],
            ["位置", "左列 x", 5.0, ""],
            ["位置", "右列 x", 79.0, ""],
            ["对照", "槽宽", 0.60, "不采用"],
            ["对照", "肋宽", 0.70, "不采用"],
            ["对照", "岸", 0.65, "不采用"],
            ["对照", "条数", 8.0, "不采用"],
        ],
    )
    print("xlsx HBM")

    gnotes = {k: k for k in GRACE}
    gnotes.update({
        "plate_L": "板宽", "plate_W": "板长", "plate_T": "板厚", "cavity_y": "Y 向空腔净长",
        "seal": "密封边",
        "to_rail": "边到干管", "rail_w": "干管宽", "rail_gap": "干管到窗",
        "mem_w": "内存窗宽", "gap_zone": "窗间间隙", "cpu_w": "CPU 窗宽",
        "cpu_x0": "CPU 左缘", "cpu_x1_margin": "CPU 右侧到板边",
        "base": "底板", "cpu_h": "CPU 槽深", "z_seal": "分型密封", "z_cav": "内腔",
        "z_lid": "盖顶", "z_part": "分型面 z", "n_ch": "CPU 槽数", "n_rib": "CPU 肋数",
        "ch_w": "CPU 槽宽", "rib_thk": "CPU 肋厚", "field": "肋场宽", "shore": "窗内岸",
        "y0": "CPU 口带起点", "y1": "CPU 口带终点", "wall": "端墙", "port": "口长",
        "neck": "未命名实铜", "heat": "CPU 受热长", "wet": "CPU 润湿长", "rear_m": "CPU 后边距",
        "mem_y0": "内存口带起点", "mem_y1": "内存口带终点", "mem_heat": "内存受热长",
        "mem_wet": "内存润湿长", "mem_margin": "内存后边距", "mem_ch_w": "内存槽宽",
        "mem_ch_h": "内存槽深", "mem_cap": "槽顶铜", "mem_n": "每侧条数",
        "pitch": "采用节距 50/6", "pitch8": "对照节距", "mem_win": "内存窗宽封闭环",
        "slit_w": "缝宽", "slit_h": "缝高", "slit_L": "缝长",
    })
    cpu_dim_rows = [
        ["外形", "板宽", 200.0, ""],
        ["外形", "板长", 120.0, ""],
        ["外形", "板厚", 8.0, ""],
        ["CPU", "窗宽", 40.0, "X 80–120"],
        ["CPU", "肋场", 38.8, "49×0.40+48×0.40"],
        ["CPU", "润湿长", 40.0, ""],
    ]
    lpd_dim_rows = [
        ["窗口", "宽", 50.0, "左右各一"],
        ["窗口", "受热长", 70.0, ""],
        ["槽", "宽", 1.20, ""],
        ["槽", "深", 0.80, ""],
        ["槽", "顶铜", 0.40, ""],
        ["节距", "采用", round(50 / 6, 6), ""],
        ["节距", "对照 8 mm 的占位", 48.0, "不闭合"],
        ["缝", "长", 12.0, "坐标未给"],
    ]
    write_book(
        ROOT / "GraceCPU冷板_尺寸核实2.xlsx",
        "DC-CPU-VER2", "Grace CPU 冷板",
        GRACE, gnotes, CPU_CHAINS,
        [
            ["外形", "200×120×8", "与 LPDDR 同一块"],
            ["CPU 窗", "X 80–120，Y 44–76", "居中"],
            ["肋场", "X 80.6–119.4", "宽 38.8"],
            ["奇数槽", "前侧进，+Y", "润湿 Y 41.2–81.2"],
            ["偶数槽", "后侧进，−Y", "润湿 Y 38.8–78.8"],
            ["未命名实铜", "42.8–44 与 76–77.2", "各 1.2 mm"],
        ],
        cpu_dim_rows,
    )
    write_book(
        ROOT / "LLDDRAM冷板_尺寸核实2.xlsx",
        "DC-LPD-VER2", "LLDDRAM 冷板（LPDDR5X）",
        GRACE, gnotes, LPD_CHAINS,
        [
            ["左窗", "X 14–64，Y 25–95", "50×70"],
            ["右窗", "X 136–186，Y 25–95", "同一套槽"],
            ["节距", "8.333 mm", "50/6；8.00 mm 不能铺满"],
            ["厚度", "槽 0.80 + 顶铜 0.40", "与 CPU 在 z=3.2 齐平"],
            ["口带", "Y 19–101", "补两段 1.2 mm 后跨度 82"],
            ["限流缝", "0.80×1.20×12", "平面位置未给"],
        ],
        lpd_dim_rows,
    )
    print("xlsx CPU LPD")
    print("ok", ROOT)


if __name__ == "__main__":
    main()
