# -*- coding: utf-8 -*-
"""生成四块冷板的结构布局、结构尺寸、尺寸链报告和尺寸核实2工作簿。

尺寸只取本目录设计报告里写明的数。没有写出的公差、铜岛、坐标不补。
GPU 与 HBM 是 CP-B300-JM-01 上的两个区。CPU 与 LPDDR 是 CP-GRACE-MC-01 上的两个区。
"""
from __future__ import annotations

import math
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.workbook.properties import CalcProperties

OUT = Path(__file__).resolve().parent

# --- 名义尺寸（mm）。注释标明报告出处，计算在下面用这些名字完成。 ---
G = {
    "plate_x": 95.0,
    "plate_y": 75.0,
    "plate_z": 8.5,
    "braze": 0.5,
    "base": 2.0,
    "gpu_groove_d": 1.5,
    "gap_h": 2.0,
    "nozzle_t": 2.5,
    "margin_x": 5.0,
    "hbm_w": 11.0,
    "hbm_h": 11.0,
    "gap_rib": 0.5,
    "rib_w": 2.0,
    "die_x": 27.0,
    "die_y": 28.0,
    "hbi": 3.0,
    "die_a_x": 19.0,
    "die_y0": 23.5,
    "hbm_x0": 5.0,
    "hbm_x1": 79.0,
    "hbm_y0": 12.5,
    "hbm_pitch_y": 13.0,
    "hbm_n": 4,
    "hbm_gap_y": 2.0,
    "col_len": 50.0,
    "jet_nx": 9,
    "jet_ny": 12,
    "jet_px": 3.0,
    "jet_py": 2.4,
    "jet_d": 0.50,
    "jet_a_x": 20.5,
    "jet_a_y": 24.3,
    "jet_b_x": 50.5,
    "groove_w": 0.40,
    "groove_pitch": 0.80,
    "groove_n": 35,
    "groove_tol": 0.03,
    "hole_tol_plus": 0.03,
    "h_tol": 0.10,
    "outline_tol": 0.15,
    "thick_tol": 0.10,
    "align_tol": 0.20,
    "hole_pos_tol": 0.10,
    "manifold_x": 8.0,
    "manifold_w": 79.0,
    "manifold_h": 7.0,
    "in_y": 66.0,
    "out_y": 2.0,
    "hole_d": 3.4,
    "hole_edge": 4.5,
    "rib_s_y": 21.5,
    "rib_n_y": 51.5,
    "rib_die_x": 19.0,
    "rib_die_w": 57.0,
    "rib_side_y": 12.5,
    "rib_side_l": 50.0,
    "env_extra": 1.2,
}
H = {
    "ch_w": 0.80,
    "ch_d": 2.00,
    "rib": 0.80,
    "n": 7,
    "shore": 0.30,
    "n_even": 4,
    "n_odd": 3,
    "base": 2.0,
    "top": 4.0,
    "port_h": 1.0,
    "man_h": 3.0,
    "old_w": 0.60,
    "old_d": 1.50,
    "old_pitch": 1.30,
    "old_n": 8,
}
C = {
    "plate_x": 200.0,
    "plate_y": 120.0,
    "plate_z": 8.0,
    "seal": 6.0,
    "base": 2.0,
    "ch_layer": 1.2,
    "parting": 0.3,
    "cavity": 2.5,
    "lid": 2.0,
    "cpu_x0": 80.0,
    "cpu_x1": 120.0,
    "cpu_y0": 44.0,
    "cpu_y1": 76.0,
    "cpu_n": 48,
    "cpu_rib_n": 49,
    "cpu_w": 0.40,
    "cpu_d": 1.20,
    "cpu_p": 0.80,
    "field": 38.8,
    "land": 0.6,
    "wet": 40.0,
    "port_l": 1.6,
    "wall": 0.8,
    "gap_heat": 1.2,
    "y_front_wall": 38.0,
    "mem_x0": 14.0,
    "mem_x1": 64.0,
    "mem_xr0": 136.0,
    "mem_xr1": 186.0,
    "mem_y0": 25.0,
    "mem_y1": 95.0,
    "mem_n": 6,
    "mem_w": 1.20,
    "mem_d": 0.80,
    "mem_p": 8.0,
    "mem_wet": 78.0,
    "mem_win": 50.0,
    "slit_w": 0.80,
    "slit_d": 1.20,
    "slit_l": 12.0,
    "rail_x0": 6.5,
    "rail_w": 7.0,
    "rail_y0": 18.0,
    "rail_y1": 102.0,
    "rail_z0": 1.0,
    "rail_z1": 6.0,
    "gal_f0": 8.0,
    "gal_f1": 16.0,
    "gal_r0": 103.0,
    "gal_r1": 112.0,
    "cavity_y0": 6.0,
    "cavity_y1": 114.0,
    "fit_y": 60.0,
    "fit_od": 8.0,
    "fit_id": 6.0,
    "orifice_n": 4,
    "orifice_d": 1.04,
    "orifice_eq_stated": 2.09,
    "mem_front_wall": 19.0,
    "mem_rear_end": 101.0,
}


def _css() -> str:
    return """
:root{--navy:#0b2748;--blue:#1769e0;--teal:#008b7a;--ink:#182536;--muted:#607086;--line:#d7e0ec;--bg:#eef3f8;--soft:#f6f9fc;--warn:#a65b00;--red:#b42318}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.7 "Microsoft YaHei","PingFang SC",Arial,sans-serif}
.page{max-width:1100px;margin:auto;background:#fff;box-shadow:0 8px 30px #102a4c18}
header{padding:36px 48px 28px;background:var(--navy);color:#fff}
header .kicker{font-size:12px;letter-spacing:.08em;color:#9db6d4}
header h1{font-size:28px;line-height:1.3;margin:8px 0}
.sub{color:#d7e6f5}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.pill{border:1px solid #ffffff55;border-radius:16px;padding:3px 10px;font-size:12px}
main{padding:28px 48px 48px}
h2{font-size:20px;color:var(--navy);border-bottom:2px solid var(--line);padding-bottom:6px;margin:28px 0 12px}
h3{font-size:16px;color:#174f83;margin:18px 0 8px}
p{margin:8px 0 12px}
.lead{border-left:5px solid var(--blue);background:#eef5ff;padding:12px 16px;border-radius:7px}
.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:12px 0}
.card{border:1px solid var(--line);border-top:4px solid var(--teal);border-radius:8px;padding:10px 12px;background:var(--soft)}
.card b{display:block;font-size:18px;color:var(--navy)}
.card.warn{border-top-color:var(--warn)}
.card.bad{border-top-color:var(--red)}
table{width:100%;border-collapse:collapse;margin:10px 0 16px;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 8px;vertical-align:top;text-align:left}
th{background:var(--navy);color:#fff}
tr:nth-child(even) td{background:#f8fafc}
.note{border:1px solid #e3ca8d;background:#fff9e9;padding:12px 14px;border-radius:7px;margin:12px 0}
.ok{border-color:#b7e0d4;background:#f3fbf8}
.bad{border-color:#f0c2bc;background:#fdf4f3}
.tag{display:inline-block;padding:1px 6px;border-radius:4px;font-size:11px;background:#e6f6f2;color:var(--teal);font-weight:700}
.tagw{background:#fff3d6;color:var(--warn)}
.tagr{background:#fde8e6;color:var(--red)}
.small{color:var(--muted);font-size:12px}
.svgbox{border:1px dashed var(--line);border-radius:8px;padding:8px;background:#fff;margin:8px 0}
.svgbox svg{width:100%;height:auto;display:block}
.figcap{color:var(--muted);font-size:12px;margin:0 0 14px}
code{font-family:Consolas,monospace;font-size:12px}
footer{padding:16px 48px 28px;color:var(--muted);font-size:12px}
@media(max-width:800px){header,main,footer{padding-left:18px;padding-right:18px}.grid{grid-template-columns:1fr 1fr}}
"""


def page(title: str, kicker: str, subtitle: str, pills: list[str], body: str) -> str:
    pill = "".join(f'<span class="pill">{p}</span>' for p in pills)
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>{_css()}</style>
</head>
<body>
<div class="page">
<header>
  <div class="kicker">{kicker}</div>
  <h1>{title}</h1>
  <div class="sub">{subtitle}</div>
  <div class="meta">{pill}</div>
</header>
<main>
{body}
</main>
<footer>数值来自本目录五份 HTML。asm_0921 的 12.5 mm / 128 孔、UC01b 的孔径 0.40 mm、v1 参数集的段间铜岛，都不进入封闭环。平面坐标在盖板图到达前仍是候选。</footer>
</div>
</body>
</html>
"""


def fmt(v: float, nd: int = 2) -> str:
    s = f"{v:.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    return s


def judge_row(name: str, expr: str, result: float, expect: float, note: str = "") -> str:
    err = result - expect
    ok = abs(err) < 1e-6
    tag = '<span class="tag">闭合</span>' if ok else '<span class="tagr">不闭合</span>'
    return (
        f"<tr><td>{name}</td><td><code>{expr}</code></td>"
        f"<td>{fmt(result, 3)}</td><td>{fmt(expect, 3)}</td>"
        f"<td>{fmt(err, 3)}</td><td>{tag}</td><td>{note}</td></tr>"
    )


def compute() -> dict:
    g, h, c = G, H, C
    x_links = [
        g["margin_x"], g["hbm_w"], g["gap_rib"], g["rib_w"], g["gap_rib"],
        g["die_x"], g["hbi"], g["die_x"], g["gap_rib"], g["rib_w"],
        g["gap_rib"], g["hbm_w"], g["margin_x"],
    ]
    x_sum = sum(x_links)
    y_hbm = g["hbm_y0"] + g["col_len"] + (g["plate_y"] - g["hbm_y0"] - g["col_len"])
    # 12.5 + 50 + 12.5
    y_top = g["plate_y"] - (g["hbm_y0"] + g["col_len"])
    assert abs(y_top - 12.5) < 1e-9
    stacks = g["hbm_n"] * g["hbm_h"] + (g["hbm_n"] - 1) * g["hbm_gap_y"]
    cavity = g["base"] + g["gpu_groove_d"] + g["gap_h"] + g["nozzle_t"]
    outline_z = cavity + g["braze"]
    span_x = (g["jet_nx"] - 1) * g["jet_px"]
    span_y = (g["jet_ny"] - 1) * g["jet_py"]
    cover_x = g["jet_nx"] * g["jet_px"]
    cover_y = g["jet_ny"] * g["jet_py"]
    jet_count = 2 * g["jet_nx"] * g["jet_ny"]
    groove_field = g["groove_n"] * g["groove_pitch"]
    end_land = (g["groove_pitch"] - g["groove_w"]) / 2
    # 35 格：两端各半个肋宽，中间 34 个整肋
    groove_rebuild = (
        2 * end_land + g["groove_n"] * g["groove_w"] + (g["groove_n"] - 1) * g["groove_w"]
    )
    # 肋宽 = 节距 - 槽宽 = 0.40，与槽宽相同，所以上式用 groove_w 当肋宽
    rib_g = g["groove_pitch"] - g["groove_w"]
    groove_rebuild = 2 * end_land + g["groove_n"] * g["groove_w"] + (g["groove_n"] - 1) * rib_g

    die_cx = g["die_a_x"] + g["die_x"] / 2
    die_cy = g["die_y0"] + g["die_y"] / 2
    arr_cx = g["jet_a_x"] + span_x / 2
    arr_cy = g["jet_a_y"] + span_y / 2
    cover_y0 = g["jet_a_y"] - g["jet_py"] / 2
    cover_y1 = g["jet_a_y"] + span_y + g["jet_py"] / 2
    die_y1 = g["die_y0"] + g["die_y"]
    overhang_y = (g["die_y0"] - cover_y0) + (cover_y1 - die_y1)
    env = g["die_y"] + g["env_extra"]
    env_margin = env - cover_y

    # 坐标走查
    stations_x = [0.0]
    for w in x_links:
        stations_x.append(stations_x[-1] + w)
    declared_x = {
        1: g["hbm_x0"],          # 5
        5: g["die_a_x"],         # 19
        7: g["die_a_x"] + g["die_x"] + g["hbi"],  # 49
        11: g["hbm_x1"],         # 79
        13: g["plate_x"],
    }
    # 隔离肋
    rib_l = g["hbm_x0"] + g["hbm_w"] + g["gap_rib"]
    rib_r = g["die_a_x"] + g["die_x"] + g["hbi"] + g["die_x"] + g["gap_rib"]

    hbm_w_chain = 2 * h["shore"] + h["n"] * h["ch_w"] + (h["n"] - 1) * h["rib"]
    hbm_z = h["base"] + h["ch_d"] + h["top"]
    hbm_top_split = h["port_h"] + h["man_h"]
    old_span = (h["old_n"] - 1) * h["old_pitch"] + h["old_w"]
    old_shore = (g["hbm_w"] - old_span) / 2

    # 歧管 Y
    y_walk = (
        g["out_y"] + g["manifold_h"] + (g["hbm_y0"] - (g["out_y"] + g["manifold_h"]))
        + g["col_len"]
        + (g["in_y"] - (g["hbm_y0"] + g["col_len"]))
        + g["manifold_h"]
        + (g["plate_y"] - (g["in_y"] + g["manifold_h"]))
    )

    # Grace
    x_grace = [
        c["rail_x0"], c["rail_w"], c["mem_x0"] - (c["rail_x0"] + c["rail_w"]),
        c["mem_x1"] - c["mem_x0"], c["cpu_x0"] - c["mem_x1"],
        c["cpu_x1"] - c["cpu_x0"], c["mem_xr0"] - c["cpu_x1"],
        c["mem_xr1"] - c["mem_xr0"],
        (c["plate_x"] - c["rail_x0"] - c["rail_w"]) - c["mem_xr1"],
        c["rail_w"], c["rail_x0"],
    ]
    # 右干管起点 = 200 - 6.5 - 7 = 186.5，与内存右缘 186 的缝 = 0.5
    cpu_field = c["cpu_rib_n"] * c["cpu_w"] + c["cpu_n"] * c["cpu_w"]
    cpu_land = ( (c["cpu_x1"] - c["cpu_x0"]) - cpu_field ) / 2
    z_grace = c["base"] + c["ch_layer"] + c["parting"] + c["cavity"] + c["lid"]
    # 内存口带
    mem_ports = [0.8, 1.6, 0.8, 1.6, 1.2, 70.0, 1.2, 1.6, 0.8, 1.6, 0.8]
    cpu_ports = [0.8, 1.6, 0.8, 1.6, 1.2, 32.0, 1.2, 1.6, 0.8, 1.6, 0.8]
    mem_pitch_span = (c["mem_n"] - 1) * c["mem_p"] + c["mem_w"]
    mem_side = (c["mem_win"] - mem_pitch_span) / 2
    mem_rib = c["mem_p"] - c["mem_w"]
    deq = c["orifice_d"] * math.sqrt(c["orifice_n"])
    # Y 整板：下密封带到内存前端墙，再内存场，再上密封带
    y_below = c["mem_front_wall"]  # 19 = 6+2+8+3
    y_field = c["mem_rear_end"] - c["mem_front_wall"]
    y_above = c["plate_y"] - c["mem_rear_end"]
    rail_remain = c["rail_z0"]
    rail_depth = c["rail_z1"] - c["rail_z0"]
    rail_stack = rail_remain + rail_depth + c["lid"]

    # 射流覆盖相对槽场
    jet_vs_groove = cover_y - groove_field

    out = {
        "x_sum": x_sum,
        "x_links": x_links,
        "y_top": y_top,
        "stacks": stacks,
        "cavity": cavity,
        "outline_z": outline_z,
        "span_x": span_x,
        "span_y": span_y,
        "cover_x": cover_x,
        "cover_y": cover_y,
        "jet_count": jet_count,
        "groove_field": groove_field,
        "end_land": end_land,
        "rib_g": rib_g,
        "groove_rebuild": groove_rebuild,
        "die_cx": die_cx,
        "die_cy": die_cy,
        "arr_cx": arr_cx,
        "arr_cy": arr_cy,
        "overhang_y": overhang_y,
        "env": env,
        "env_margin": env_margin,
        "cover_y0": cover_y0,
        "cover_y1": cover_y1,
        "rib_l": rib_l,
        "rib_r": rib_r,
        "stations_x": stations_x,
        "hbm_w_chain": hbm_w_chain,
        "hbm_z": hbm_z,
        "hbm_top_split": hbm_top_split,
        "old_span": old_span,
        "old_shore": old_shore,
        "y_walk": y_walk,
        "x_grace": x_grace,
        "x_grace_sum": sum(x_grace),
        "cpu_field": cpu_field,
        "cpu_land": cpu_land,
        "z_grace": z_grace,
        "mem_ports_sum": sum(mem_ports),
        "cpu_ports_sum": sum(cpu_ports),
        "mem_pitch_span": mem_pitch_span,
        "mem_side": mem_side,
        "mem_rib": mem_rib,
        "deq": deq,
        "y_below": y_below,
        "y_field": y_field,
        "y_above": y_above,
        "rail_stack": rail_stack,
        "jet_vs_groove": jet_vs_groove,
        "hole_area": jet_count * math.pi * (g["jet_d"] / 2) ** 2,
        "rib_min": rib_g - g["groove_tol"],
        "aspect_max": g["gpu_groove_d"] / (g["groove_w"] - g["groove_tol"]),
        "hd_min": (g["gap_h"] - g["h_tol"]) / (g["jet_d"] + g["hole_tol_plus"]),
        "hd_max": (g["gap_h"] + g["h_tol"]) / g["jet_d"],
        "align_x_left": 0.0 - g["align_tol"],  # X 覆盖与 die 等宽，负值表示露出
        "align_y_left": (overhang_y / 2) - g["align_tol"],
    }
    assert abs(out["x_sum"] - 95) < 1e-9
    assert abs(out["stacks"] - 50) < 1e-9
    assert abs(out["cavity"] - 8) < 1e-9
    assert abs(out["outline_z"] - 8.5) < 1e-9
    assert abs(out["span_x"] - 24) < 1e-9
    assert abs(out["span_y"] - 26.4) < 1e-9
    assert abs(out["cover_x"] - 27) < 1e-9
    assert abs(out["cover_y"] - 28.8) < 1e-9
    assert abs(out["overhang_y"] - 0.8) < 1e-9
    assert abs(out["env_margin"] - 0.4) < 1e-9
    assert abs(out["die_cx"] - out["arr_cx"]) < 1e-9
    assert abs(out["die_cy"] - out["arr_cy"]) < 1e-9
    assert abs(out["rib_l"] - 16.5) < 1e-9
    assert abs(out["rib_r"] - 76.5) < 1e-9
    assert abs(out["groove_field"] - 28) < 1e-9
    assert abs(out["groove_rebuild"] - 28) < 1e-9
    assert abs(out["hbm_w_chain"] - 11) < 1e-9
    assert abs(out["hbm_z"] - 8) < 1e-9
    assert abs(out["hbm_top_split"] - 4) < 1e-9
    assert abs(out["y_walk"] - 75) < 1e-9
    assert abs(out["x_grace_sum"] - 200) < 1e-9
    assert abs(out["cpu_field"] - 38.8) < 1e-9
    assert abs(out["cpu_land"] - 0.6) < 1e-9
    assert abs(out["z_grace"] - 8) < 1e-9
    assert abs(out["mem_ports_sum"] - 82) < 1e-9
    assert abs(out["cpu_ports_sum"] - 44) < 1e-9
    assert abs(out["y_below"] + out["y_field"] + out["y_above"] - 120) < 1e-9
    assert abs(out["rail_stack"] - 8) < 1e-9
    assert abs(out["mem_pitch_span"] + 2 * out["mem_side"] - 50) < 1e-9
    assert out["jet_count"] == 216
    assert abs(out["deq"] - 2.08) < 1e-9
    return out


R = compute()


def gpu_layout() -> str:
    body = f"""
<p class="lead">GPU 射流区在冷板 <strong>CP-B300-JM-01</strong> 中部，盖住两颗 27 × 28 mm 计算 die。它和两侧 HBM 区是同一块铜，不是另一块板。外形 95 × 75 × 8.5 mm。射流只打在 die 上：每颗 die 9 × 12 共 108 孔，两颗 216 孔，孔径 0.50 mm。HBM 区不开孔。</p>
<div class="grid">
  <div class="card"><b>95 × 75 × 8.5</b>整板外形 mm</div>
  <div class="card"><b>216 × Ø0.50</b>两颗 die 的射流孔</div>
  <div class="card"><b>3.0 × 2.4</b>孔距 mm，X × Y</div>
  <div class="card"><b>0.40 × 1.50</b>短槽，节距 0.80，35 条/die</div>
</div>
<h2>1. 坐标和在板上的位置</h2>
<p>原点在冷板左下角，X 向右，Y 向上，Z 从贴芯片的一面向上。图的上方是 +Y，进液歧管在上沿，出液歧管在下沿。</p>
<div class="svgbox">
<svg viewBox="0 0 860 700" xmlns="http://www.w3.org/2000/svg">
  <rect x="40" y="40" width="760" height="600" fill="#f4e0cf" stroke="#5c3a17" stroke-width="2"/>
  <rect x="104" y="140" width="632" height="56" fill="#d9e9f7" stroke="#1f6fb2"/>
  <rect x="104" y="504" width="632" height="56" fill="#f6dcd8" stroke="#c0392b"/>
  <rect x="80" y="140" width="88" height="400" fill="#efe6c9" stroke="#8a6a12"/>
  <rect x="672" y="140" width="88" height="400" fill="#efe6c9" stroke="#8a6a12"/>
  <rect x="172" y="140" width="16" height="400" fill="#1f4e79"/>
  <rect x="652" y="140" width="16" height="400" fill="#1f4e79"/>
  <rect x="192" y="228" width="216" height="224" fill="#f0c2b4" stroke="#b42318"/>
  <rect x="432" y="228" width="216" height="224" fill="#f0c2b4" stroke="#b42318"/>
  <rect x="192" y="212" width="456" height="16" fill="#1f4e79"/>
  <rect x="192" y="452" width="456" height="16" fill="#1f4e79"/>
  <text x="300" y="348" text-anchor="middle" font-size="16" fill="#b42318" font-family="Microsoft YaHei">Die-A 射流 9×12</text>
  <text x="540" y="348" text-anchor="middle" font-size="16" fill="#b42318" font-family="Microsoft YaHei">Die-B 射流 9×12</text>
  <text x="124" y="350" text-anchor="middle" font-size="13" fill="#8a6a12" font-family="Microsoft YaHei">HBM</text>
  <text x="716" y="350" text-anchor="middle" font-size="13" fill="#8a6a12" font-family="Microsoft YaHei">HBM</text>
  <text x="420" y="174" text-anchor="middle" font-size="14" fill="#1f6fb2" font-family="Microsoft YaHei">进液歧管 Y 66–73</text>
  <text x="420" y="538" text-anchor="middle" font-size="14" fill="#c0392b" font-family="Microsoft YaHei">出液歧管 Y 2–9</text>
  <text x="420" y="670" text-anchor="middle" font-size="13" fill="#33404d" font-family="Microsoft YaHei">+X 95 mm</text>
</svg>
</div>
<p class="figcap">图 1. 俯视，1 mm 图上约 8 px。浅红是 die，浅黄是 HBM 列，深蓝是隔离肋。射流孔只落在两块浅红里。HBM 的槽不在这张图里展开，见 HBM 文件。</p>
<p>Die-A 占 X 19–46、Y 23.5–51.5。Die-B 占 X 49–76，Y 与 Die-A 相同。中间 X 46–49 是 3 mm 的 NV-HBI 缝，不打密孔。左右隔离肋在 X 16.5–18.5 和 X 76.5–78.5，Y 12.5–62.5，把 GPU 腔和 HBM 腔隔开。die 上下各有一条 X 19–76、高 2 mm 的肋，下肋 Y 21.5–23.5，上肋 Y 51.5–53.5，正好贴着 die 的上下边。</p>
<h2>2. 厚度方向</h2>
<p>从贴芯片的一面数：余铜 2.0，短槽 1.5，射流间隙 2.0，喷嘴板 2.5。这四层是腔体 8.0 mm。外形再加周边钎缝 0.5 mm，到 8.5 mm。喷嘴是直孔，孔长等于喷嘴板厚 2.5 mm。冷却液在间隙里冲击槽顶一侧的铜，再进入短槽。</p>
<p>HBM 加热段在 2026-09-28 修订后不再留这道 2.0 mm 通长水缝，上铜板改成 4.0 mm。两区腔体都是 8.0 mm，内部分配不同。GPU 文件只封闭 GPU 这一侧的 2.0 + 1.5 + 2.0 + 2.5。</p>
<h2>3. 孔阵和短槽怎么摆</h2>
<p>Die-A 首孔中心 (20.5, 24.3)，X 向 9 孔、节距 3.0，Y 向 12 孔、节距 2.4。Die-B 首孔 (50.5, 24.3)，节距相同。孔阵中心与 die 中心重合，都在 (32.5, 37.5) 和 (62.5, 37.5)。</p>
<p>短槽沿 X，在 Y 向排 35 条，节距 0.80 mm，槽宽 0.40 mm，深 1.50 mm。35 个节距格铺满 die 的 28 mm 高度。报告把槽内流程写成 3.0 mm，与 X 向孔距相同，上限 8 mm。段间铜岛和抽吸孔径在 v2 正文里没有可相加的尺寸，这里不补。</p>
<h2>4. 不放进这条布局的几何</h2>
<div class="note">
<p><code>asm_0921.stp</code> 是 95 × 75 × 12.5 mm 的三层铜，128 个 Ø0.50 孔。它是另一条厚度链。UC01b 网格把孔径做成 0.40 mm，用来看换热，不替换图纸上的 0.50 mm。v1 参数集里每 die 8 × 8 孔、段间 1.0 mm 铜岛，也不进入 v2 的布置。</p>
</div>
<p class="small">来源：B300 设计报告 v2.0 §5.2、§6.2、§8.1。HBM 修订只用来说明邻区上盖不同，不改 GPU 孔位。</p>
"""
    return page(
        "GPU 射流冲击微通道冷板 · 结构布局说明",
        "CP-B300-JM-01 · GPU 区 · 2026-09-29",
        "两颗 die 上的 216 孔射流和 35 条短槽。与 HBM 同板不同区。",
        ["候选几何", "图纸基准 Ø0.50", "216 孔", "待盖板图"],
        body,
    )


def gpu_dims() -> str:
    body = f"""
<p class="lead">下表是 GPU 区用来画图和做尺寸链的名义尺寸。状态按报告原话：封装坐标待冻结，厚度和孔槽是本方案的图纸基准。公差只列报告写了的。</p>
<h2>1. 整板和 die</h2>
<table>
<thead><tr><th>特征</th><th>名义</th><th>公差</th><th>状态</th></tr></thead>
<tbody>
<tr><td>外形</td><td>95 × 75 × 8.5 mm</td><td>长宽 ±0.15，总厚 ±0.10</td><td><span class="tagw">候选，待冻结</span></td></tr>
<tr><td>Die-A</td><td>原点 (19, 23.5)，27 × 28</td><td>与孔阵对位 ±0.20</td><td><span class="tagw">候选</span></td></tr>
<tr><td>NV-HBI</td><td>X 46–49，宽 3，高 28</td><td>未给</td><td><span class="tagw">候选</span></td></tr>
<tr><td>Die-B</td><td>原点 (49, 23.5)，27 × 28</td><td>同 Die-A</td><td><span class="tagw">候选</span></td></tr>
<tr><td>左右隔离肋</td><td>X 16.5 与 76.5，2.0 × 50，Y 从 12.5 起</td><td>未给</td><td>方案</td></tr>
<tr><td>上下隔离肋</td><td>X 19，宽 57，高 2；Y 21.5 与 51.5</td><td>未给</td><td>方案</td></tr>
<tr><td>进液歧管</td><td>X 8，Y 66，79 × 7</td><td>未给</td><td>方案</td></tr>
<tr><td>出液歧管</td><td>X 8，Y 2，79 × 7</td><td>未给</td><td>方案</td></tr>
<tr><td>安装孔</td><td>中心距边 4.5，Ø3.4，四角</td><td>未给</td><td><span class="tagw">待冻结</span></td></tr>
</tbody>
</table>
<h2>2. 厚度</h2>
<table>
<thead><tr><th>层</th><th>厚度 mm</th><th>Z 范围（贴芯片面为 0）</th><th>公差</th></tr></thead>
<tbody>
<tr><td>接触面余铜</td><td>2.0</td><td>0 – 2.0</td><td>未单列；总厚 ±0.10</td></tr>
<tr><td>短槽</td><td>1.5</td><td>2.0 – 3.5</td><td>槽宽另有公差，槽深未单列</td></tr>
<tr><td>射流间隙 H</td><td>2.0</td><td>3.5 – 5.5</td><td>±0.10，平行度 0.05</td></tr>
<tr><td>喷嘴板</td><td>2.5</td><td>5.5 – 8.0</td><td>未单列</td></tr>
<tr><td>腔体</td><td>8.0</td><td>0 – 8.0</td><td>—</td></tr>
<tr><td>周边钎缝</td><td>0.5</td><td>8.0 – 8.5</td><td>未单列</td></tr>
<tr><td>外形总厚</td><td>8.5</td><td>0 – 8.5</td><td>±0.10</td></tr>
</tbody>
</table>
<h2>3. 射流孔</h2>
<table>
<thead><tr><th>特征</th><th>名义</th><th>公差</th></tr></thead>
<tbody>
<tr><td>孔径</td><td>Ø0.50 mm</td><td>+0.03 / 0，轴线垂直度 0.05</td></tr>
<tr><td>每 die 个数</td><td>9 × 12 = 108，两 die 216</td><td>—</td></tr>
<tr><td>节距</td><td>X 3.0，Y 2.4</td><td>孔位加工 ±0.10；与 die 对位 ±0.20</td></tr>
<tr><td>中心距</td><td>X 24.0，Y 26.4</td><td>—</td></tr>
<tr><td>Die-A 首孔</td><td>(20.5, 24.3)</td><td>—</td></tr>
<tr><td>Die-B 首孔</td><td>(50.5, 24.3)</td><td>—</td></tr>
<tr><td>覆盖</td><td>X 27.0（与 die 等宽），Y 28.8（比 die 宽 0.8）</td><td>见尺寸链报告的对位核算</td></tr>
<tr><td>孔长</td><td>2.5，等于喷嘴板厚</td><td>—</td></tr>
<tr><td>无量纲</td><td>H/D = 4.0；Sx/D = 6.0；Sy/D = 4.8</td><td>H 与 D 的公差见核实表</td></tr>
</tbody>
</table>
<p>孔总面积 216 × π × 0.25² = {fmt(R['hole_area'], 2)} mm²，与报告 42.41 mm² 一致。这是面积复核，不是尺寸环。</p>
<h2>4. 短槽</h2>
<table>
<thead><tr><th>特征</th><th>名义</th><th>公差</th></tr></thead>
<tbody>
<tr><td>截面</td><td>宽 0.40 × 深 1.50</td><td>宽 ±0.03；深未单列</td></tr>
<tr><td>节距 / 肋</td><td>0.80 / 0.40</td><td>节距未单列</td></tr>
<tr><td>条数</td><td>35 条/die，两 die 70 条</td><td>—</td></tr>
<tr><td>Y 向槽场</td><td>35 × 0.80 = 28.0，等于 die 高</td><td>—</td></tr>
<tr><td>流程</td><td>设计值 3.0，上限 8</td><td>段间铜岛未给</td></tr>
</tbody>
</table>
<div class="note">
<p>槽宽收到 0.43 mm 时，肋变为 0.37 mm，仍高于工艺下限 0.30 mm。槽深 / 最小槽宽 = {fmt(R['aspect_max'], 2)}，低于报告所用的倒齿上限 5。</p>
</div>
<p class="small">来源：B300 设计报告 v2.0 §6.2、§6.5、§8.1。工艺下限 0.30 mm 见同目录 CAD 规则，只用于和公差后的肋宽比较。</p>
"""
    return page(
        "GPU 射流冲击微通道冷板 · 结构尺寸说明",
        "CP-B300-JM-01 · GPU 区 · 2026-09-29",
        "名义尺寸、报告中的公差，以及没有给出公差的项。",
        ["单位 mm", "公差只录报告原文", "孔径基准 0.50"],
        body,
    )


def gpu_chain() -> str:
    rows = "".join([
        judge_row("X 向整板", "5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5", R["x_sum"], 95, "边–HBM–缝–肋–缝–die–HBI–die–缝–肋–缝–HBM–边"),
        judge_row("Y 向 HBM 列所占高度", "12.5+50+12.5", 75, 75, "射流区上下肋不在这一条里"),
        judge_row("四颗堆叠加缝", "4×11+3×2", R["stacks"], 50, "列长"),
        judge_row("歧管展开的 Y 向", "2+7+3.5+50+3.5+7+2", R["y_walk"], 75, "核实2：把 12.5 拆开"),
        judge_row("腔体厚度", "2.0+1.5+2.0+2.5", R["cavity"], 8, "不含钎缝"),
        judge_row("外形总厚", "8.0+0.5", R["outline_z"], 8.5, "周边钎缝"),
        judge_row("射流中心距 X", "(9−1)×3.0", R["span_x"], 24, ""),
        judge_row("射流中心距 Y", "(12−1)×2.4", R["span_y"], 26.4, ""),
        judge_row("覆盖长度 X", "9×3.0", R["cover_x"], 27, "与 die 宽相等"),
        judge_row("覆盖长度 Y", "12×2.4", R["cover_y"], 28.8, ""),
        judge_row("Y 向超出 die", "28.8−28", R["overhang_y"], 0.8, "两侧各 0.4"),
        judge_row("Y 向板外包络", "28+1.2", R["env"], 29.2, "报告原式"),
        judge_row("外包络余量", "29.2−28.8", R["env_margin"], 0.4, "两侧各 0.2"),
        judge_row("单 die 槽场", "35×0.80", R["groove_field"], 28, "等于 die 高"),
        judge_row("槽场按肋槽重加", "2×0.20+35×0.40+34×0.40", R["groove_rebuild"], 28, "核实2"),
        judge_row("孔数", "2×9×12", R["jet_count"], 216, ""),
        judge_row("左隔离肋 X", "5+11+0.5", R["rib_l"], 16.5, "与 §8.1 坐标一致"),
        judge_row("右隔离肋 X", "49+27+0.5", R["rib_r"], 76.5, ""),
        judge_row("孔阵与 die 中心", "首孔+中心距/2", R["arr_cx"], R["die_cx"], "X。Y 同为 37.5"),
        judge_row("上下肋跨两 die", "27+3+27", 57, 57, "肋宽 57，X 19 到 76"),
    ])
    body = f"""
<p class="lead">封闭环用增环相加，和报告里的期望值比较。差的绝对值小于 0.001 mm 记为闭合。另一路核实不重写这条加法，而是从原点累加，看中间站是否落到 §8.1 的坐标上。两路都在 Excel 里用公式重算。</p>
<h2>1. 名义尺寸链</h2>
<table>
<thead><tr><th>链</th><th>算式</th><th>结果</th><th>期望</th><th>差</th><th>判定</th><th>说明</th></tr></thead>
<tbody>
{rows}
</tbody>
</table>
<h2>2. 核实2：从左边累加到图纸坐标</h2>
<p>X 向每一站的累计值：0，5（左 HBM 起点），16（HBM 右缘），16.5（左肋），18.5，19（Die-A），46（HBI），49（Die-B），76，76.5（右肋），78.5，79（右 HBM），90，95。这些站和报告坐标一致，最后一站等于板宽。</p>
<p>Die-A 首孔 20.5 比 die 左缘 19 大 1.5，正好是半个 X 向节距。覆盖因此从 19 铺到 46，X 向没有多出来的边。Y 向半节距是 1.2，覆盖从 23.1 到 51.9，die 是 23.5 到 51.5，每侧多 0.4 mm。</p>
<h2>3. 公差落在哪一条链上</h2>
<table>
<thead><tr><th>项目</th><th>核算</th><th>结果</th></tr></thead>
<tbody>
<tr><td>X 向覆盖对 die</td><td>名义余量 0。对位公差 ±0.20</td><td><span class="tagr">公差下 die 边缘最多露出 0.20 mm</span></td></tr>
<tr><td>Y 向覆盖对 die</td><td>每侧名义 0.40，减去 0.20</td><td><span class="tag">仍盖住，每侧剩 0.20</span></td></tr>
<tr><td>Y 向覆盖对 29.2 外包络</td><td>每侧名义 0.20，减去对位 0.20</td><td><span class="tagw">余量被对位公差用尽，贴边</span></td></tr>
<tr><td>H/D</td><td>H = 1.90–2.10，D = 0.50–0.53</td><td>{fmt(R['hd_min'], 2)} – {fmt(R['hd_max'], 2)}，仍在 2–6</td></tr>
<tr><td>肋宽</td><td>节距按基本尺寸 0.80，槽宽 0.37–0.43</td><td>肋 0.37–0.43，高于 0.30</td></tr>
<tr><td>整板 X、Y 各段</td><td>5、11、0.5、2、27 等没有分段公差</td><td>只做名义闭合。外形 ±0.15 是封闭环公差，不能反写成各段公差</td></tr>
</tbody>
</table>
<div class="note bad">
<p><strong>要单独记住的一件事：</strong>X 向射流覆盖和 die 等宽，名义链是闭合的，公差链并不保证 die 整面落在孔阵覆盖里。Y 向有 0.4 mm/侧，能吃掉 ±0.20 的对位公差。若要 X 向也留下同样的 0.20 mm，覆盖得比 die 宽，那就要改节距或孔数，本文件不改图纸。</p>
</div>
<h2>4. 和“短槽必须短”有关、但链上没有的数</h2>
<p>流程设计值 3.0 mm 与 X 向节距相同，9 × 3.0 又等于 die 宽。若 9 段各自长 3.0 且首尾贴着 die，段与段之间就没有宽度可分配给铜岛。v2 没有另给铜岛尺寸。名义覆盖是闭合的；“每 3 mm 用一道墙切断交叉流”还缺这道墙的宽度。v1 参数集里的 1.0 mm 铜岛加回去，就不能同时满足 9 段、每段 3.0、总长 27。</p>
<p class="small">Excel <code>GPU_射流冲击微通道冷板_尺寸核实2计算.xlsx</code> 的“尺寸链”和“核实2”两个表用输入格重算上表。改输入格后，闭合差会跟着变。</p>
"""
    return page(
        "GPU 射流冲击微通道冷板 · 尺寸链计算报告",
        "CP-B300-JM-01 · GPU 区 · 2026-09-29",
        "名义链全部闭合。X 向覆盖没有公差余量。",
        ["名义闭合", "X 向对位无余量", "段间铜岛未给"],
        body,
    )


def hbm_layout() -> str:
    body = """
<p class="lead">HBM 微通道在同一块 CP-B300-JM-01 的左右两侧，各一列 4 颗 11 × 11 mm 堆叠。现行槽截面取 2026-09-28 修订和 <code>HBM_w08h20</code> 网格：0.80 × 2.00 mm，肋 0.80 mm，每侧 7 条。加热段槽顶封死，没有通长水缝，也没有喷嘴。</p>
<div class="grid">
  <div class="card"><b>左右各 4 颗</b>11 × 11，列长 50</div>
  <div class="card"><b>7 条 / 侧</b>0.80 槽 + 0.80 肋</div>
  <div class="card"><b>岸 0.30 × 2</b>加起来等于 11</div>
  <div class="card warn"><b>槽深 2.0</b>深于 GPU 槽的 1.5</div>
</div>
<h2>1. 在 95 × 75 板上的位置</h2>
<p>左列原点 X = 5，右列 X = 79。四颗的 Y 为 12.5、25.5、38.5、51.5，颗与颗之间空 2 mm。末颗顶边在 62.5，列长 50，上下各剩 12.5，板高 75。</p>
<p>靠 die 的一侧是 2 mm 隔离肋：左肋 X 16.5–18.5，右肋 X 76.5–78.5，Y 12.5–62.5。肋的外侧离 HBM 外缘 0.5 mm，内侧离 die 也是 0.5 mm。HBM 区盖板不开射流孔。</p>
<div class="svgbox">
<svg viewBox="0 0 860 280" xmlns="http://www.w3.org/2000/svg">
  <rect x="40" y="40" width="760" height="180" fill="#f6f1e4" stroke="#5c3a17"/>
  <g fill="#c9a227">
    <rect x="70" y="70" width="70" height="28"/><rect x="70" y="112" width="70" height="28"/>
    <rect x="70" y="154" width="70" height="28"/><rect x="70" y="196" width="70" height="8"/>
  </g>
  <text x="250" y="80" font-size="14" fill="#182536" font-family="Microsoft YaHei">单侧 11 mm 宽，自下而上四颗。下图是其中一颗的槽，按宽度比例。</text>
  <rect x="250" y="110" width="440" height="70" fill="#f4e0cf" stroke="#5c3a17"/>
  <g fill="#1f6fb2">
    <rect x="262" y="118" width="32" height="54"/>
    <rect x="326" y="118" width="32" height="54"/>
    <rect x="390" y="118" width="32" height="54"/>
    <rect x="454" y="118" width="32" height="54"/>
    <rect x="518" y="118" width="32" height="54"/>
    <rect x="582" y="118" width="32" height="54"/>
    <rect x="646" y="118" width="32" height="54"/>
  </g>
  <text x="470" y="210" text-anchor="middle" font-size="13" fill="#33404d" font-family="Microsoft YaHei">7 条槽。奇数 3 条一个流向，偶数 4 条反向。两岸各 0.30 mm。</text>
</svg>
</div>
<p class="figcap">图 1. 上图只示意列的分段，不是板的全宽。下图 7 条槽等宽，肋与槽同宽，两岸留白。</p>
<h2>2. 流向</h2>
<p>列的长边是流动方向。7 条里偶数 4 条从一个端头进，奇数 3 条从另一端进。出流不从槽的远端水平离开：远端用铜封住，流体从槽顶的竖向口翻进上铜板里的汇流腔。低 Y 腔只收偶数槽，高 Y 腔只收奇数槽。同一端的进流槽没有这只竖向口，进出因此不串腔。</p>
<h2>3. 厚度和 GPU 区的差别</h2>
<p>加热段自芯片面起：底铜 2.0，槽高 2.0，上铜板 4.0，合计 8.0 mm，与整板腔体相同。上铜板内部是竖向口 1.0 mm 加上汇流腔 3.0 mm。外形仍写 8.5 mm，多出的 0.5 mm 是周边钎缝，不在这段加热网格里。</p>
<p>GPU 区是余铜 2.0、槽 1.5、开口间隙 2.0、喷嘴板 2.5。HBM 把槽加深 0.5 mm，取消开口间隙，上板加厚到 4.0 mm。两套加法都等于 8.0，所以不能用一把槽深把整块底板铣完。</p>
<div class="note">
<p>修订前的正文仍写 0.60 × 1.50 mm、每侧 8 条、节距 1.30 mm。那一组也能在 11 mm 里闭合（两岸各 0.65 mm），但已被文首修订和 w08h20 网格替换。尺寸链以 0.80 × 2.00、7 条为准。旧链留在 Excel 的“不采用”表，不参与判定。</p>
</div>
<p class="small">来源：B300 报告文首“HBM 交错流修订 · 2026-09-28”，以及同目录 HBM_w08h20 结果报告所用网格。堆叠坐标仍用 §8.1。</p>
"""
    return page(
        "HBM 微通道冷板 · 结构布局说明",
        "CP-B300-JM-01 · HBM 区 · 2026-09-29",
        "左右两列、每列四颗。槽顶封死，相邻槽反向。",
        ["现行截面 0.80×2.00", "每侧 7 槽", "无喷嘴"],
        body,
    )


def hbm_dims() -> str:
    body = f"""
<p class="lead">堆叠在板上的位置沿用 §8.1。槽的宽、深、条数和上盖沿用 2026-09-28 修订。修订没有给槽宽公差，表中写“未给”。</p>
<h2>1. 堆叠位置</h2>
<table>
<thead><tr><th>特征</th><th>名义 mm</th><th>状态</th></tr></thead>
<tbody>
<tr><td>单颗</td><td>11 × 11</td><td><span class="tagw">候选</span></td></tr>
<tr><td>左列 X</td><td>5 – 16</td><td><span class="tagw">候选</span></td></tr>
<tr><td>右列 X</td><td>79 – 90</td><td><span class="tagw">候选</span></td></tr>
<tr><td>Y</td><td>12.5，25.5，38.5，51.5</td><td><span class="tagw">候选</span></td></tr>
<tr><td>颗间</td><td>2</td><td>由相邻原点相减</td></tr>
<tr><td>列长</td><td>50，Y 12.5 – 62.5</td><td>方案</td></tr>
<tr><td>靠 die 的隔离肋</td><td>宽 2，长 50；X 16.5 与 76.5</td><td>方案</td></tr>
<tr><td>肋与 HBM、肋与 die</td><td>各 0.5</td><td>方案</td></tr>
</tbody>
</table>
<h2>2. 现行槽</h2>
<table>
<thead><tr><th>特征</th><th>名义 mm</th><th>公差</th></tr></thead>
<tbody>
<tr><td>槽</td><td>宽 0.80 × 深 2.00</td><td>未给</td></tr>
<tr><td>肋</td><td>0.80</td><td>未给</td></tr>
<tr><td>每侧条数</td><td>7。偶数 4 条，奇数 3 条</td><td>—</td></tr>
<tr><td>岸</td><td>每侧 0.30，两岸 0.60</td><td>未给</td></tr>
<tr><td>底铜</td><td>2.0</td><td>未给</td></tr>
<tr><td>上铜板</td><td>4.0。其中竖向口高 1.0，汇流腔高 3.0</td><td>未给</td></tr>
<tr><td>加热段总厚</td><td>8.0（不含 0.5 钎缝）</td><td>整板总厚仍 ±0.10，未分到本区</td></tr>
</tbody>
</table>
<h2>3. 和 GPU 槽并放时要分开标注的尺寸</h2>
<table>
<thead><tr><th></th><th>GPU 区</th><th>HBM 区现行</th></tr></thead>
<tbody>
<tr><td>槽深</td><td>1.5</td><td>2.0</td></tr>
<tr><td>槽顶以上</td><td>开口间隙 2.0 + 喷嘴板 2.5</td><td>上铜板 4.0，加热段槽顶封死</td></tr>
<tr><td>底铜</td><td>2.0</td><td>2.0</td></tr>
<tr><td>合计到腔体顶</td><td>8.0</td><td>8.0</td></tr>
<tr><td>喷嘴</td><td>216 × Ø0.50</td><td>无</td></tr>
</tbody>
</table>
<p class="small">旧截面 0.60 × 1.50、节距 1.30、每侧 8 条、岸 0.65，只作为被替换的记录，不作为加工尺寸。</p>
"""
    return page(
        "HBM 微通道冷板 · 结构尺寸说明",
        "CP-B300-JM-01 · HBM 区 · 2026-09-29",
        "位置来自 §8.1，截面来自 2026-09-28 修订。",
        ["单位 mm", "7 × 0.80", "槽深与 GPU 不同"],
        body,
    )


def hbm_chain() -> str:
    rows = "".join([
        judge_row("单侧槽场宽", "0.30+7×0.80+6×0.80+0.30", R["hbm_w_chain"], 11, "两岸 + 槽 + 肋"),
        judge_row("条数", "4+3", 7, 7, "偶数与奇数"),
        judge_row("四颗加三道缝", "4×11+3×2", R["stacks"], 50, ""),
        judge_row("列在板高中的位置", "12.5+50+12.5", 75, 75, ""),
        judge_row("左列右缘到左肋", "16.5−16", 0.5, 0.5, ""),
        judge_row("左肋右缘到 Die-A", "19−18.5", 0.5, 0.5, ""),
        judge_row("加热段厚度", "2.0+2.0+4.0", R["hbm_z"], 8, "等于腔体，不含钎缝"),
        judge_row("上铜板内部分配", "1.0+3.0", R["hbm_top_split"], 4, "竖向口 + 汇流腔"),
        judge_row("与 GPU 腔体对比", "2+1.5+2+2.5", R["cavity"], 8, "总数相同，槽深不同"),
        judge_row("整板 X（与 GPU 同一条）", "5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5", R["x_sum"], 95, ""),
        judge_row("旧 8 槽宽度（不采用）", "0.65×2+7×1.30+0.60", R["old_span"] + 2 * R["old_shore"], 11, "能闭合，但不是现行截面"),
    ])
    body = f"""
<p class="lead">HBM 区有三条必须同时成立的链：11 mm 里排下 7 条槽，50 mm 里排下 4 颗堆叠，加热段厚度等于整板腔体 8.0 mm。三条名义链都闭合。槽深和 GPU 区不一致，这是结构事实，不是加法错误。</p>
<h2>1. 名义尺寸链</h2>
<table>
<thead><tr><th>链</th><th>算式</th><th>结果</th><th>期望</th><th>差</th><th>判定</th><th>说明</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<h2>2. 核实2</h2>
<p>左列从 X = 5 加到 16，加 0.5 到肋的 16.5，再加肋宽 2 到 18.5，再加 0.5 到 die 的 19。右列从板宽倒推：95 − 5 − 11 = 79，与右列原点一致。</p>
<p>Y 向从 12.5 起，每加 11 再加 2，得到 25.5、38.5、51.5。51.5 + 11 = 62.5。62.5 + 12.5 = 75。颗间 2 mm 是后一颗原点减前一颗顶边，不是另设的一条肋宽。</p>
<p>宽度重加：岸 0.30，然后槽、肋交替。7 个槽是 5.60，6 个肋是 4.80，两岸 0.60，合计 11.00。没有剩余，也没有负值。</p>
<h2>3. 不能做的公差叠加</h2>
<p>0.80、0.30、2.00、4.0 都没有公差。名义闭合不能外推成极值闭合。整板外形 ±0.15、总厚 ±0.10 写在 GPU 尺寸说明里，没有分配到 HBM 的岸和肋上。</p>
<div class="note">
<p>加工时槽深要分区：GPU 1.5 mm，HBM 2.0 mm。若误用同一槽深，要么 HBM 的 2.0 mm 链被破坏，要么 GPU 的射流间隙被铣深。两条厚度链各自等于 8.0，合不到同一个槽深上。</p>
</div>
<p class="small">Excel：<code>HBM_微通道冷板_尺寸核实2计算.xlsx</code>。</p>
"""
    return page(
        "HBM 微通道冷板 · 尺寸链计算报告",
        "CP-B300-JM-01 · HBM 区 · 2026-09-29",
        "11 mm、50 mm、8.0 mm 三条名义链闭合。槽深与 GPU 区不同。",
        ["名义闭合", "槽深分区", "旧 8 槽不采用"],
        body,
    )


def cpu_layout() -> str:
    body = """
<p class="lead">Grace 的 CPU 冷板是 <strong>CP-GRACE-MC-01</strong> 中部的槽区，不是单独一块铜。整板 200 × 120 × 8.0 mm，左右还带着 LPDDR 窗口。CPU 窗口 X 80–120、Y 44–76，即 40 × 32 mm。48 条槽沿 Y，节距沿 X。奇数槽流向 +Y，偶数槽流向 −Y。没有微射流。</p>
<div class="grid">
  <div class="card"><b>40 × 32</b>CPU 窗口 mm，候选</div>
  <div class="card"><b>48 槽</b>0.40 × 1.20，节距 0.80</div>
  <div class="card"><b>38.8</b>肋场宽，窗内两侧各余 0.6</div>
  <div class="card"><b>8.0</b>整板厚，两层铜</div>
</div>
<h2>1. 坐标</h2>
<p>原点在冷板左下角。X 从左接头到右接头，Y 朝后面板，芯片面 z = 0。进液在左侧干管，出液在右侧干管。接头中心 Y = 60，放在前后两套口的中点。</p>
<div class="svgbox">
<svg viewBox="0 0 760 460" xmlns="http://www.w3.org/2000/svg">
  <rect x="40" y="40" width="640" height="384" fill="#f4e0cf" stroke="#5c3a17" stroke-width="2"/>
  <rect x="85" y="88" width="160" height="224" fill="#efe6c9" stroke="#8a6a12"/>
  <rect x="475" y="88" width="160" height="224" fill="#efe6c9" stroke="#8a6a12"/>
  <rect x="296" y="147" width="128" height="102" fill="#f0c2b4" stroke="#b42318"/>
  <rect x="61" y="70" width="22" height="300" fill="#d9e9f7" stroke="#1f6fb2"/>
  <rect x="637" y="70" width="22" height="300" fill="#f6dcd8" stroke="#c0392b"/>
  <text x="360" y="205" text-anchor="middle" font-size="14" fill="#b42318" font-family="Microsoft YaHei">CPU 48 槽</text>
  <text x="165" y="200" text-anchor="middle" font-size="14" fill="#8a6a12" font-family="Microsoft YaHei">LPDDR 左</text>
  <text x="555" y="200" text-anchor="middle" font-size="14" fill="#8a6a12" font-family="Microsoft YaHei">LPDDR 右</text>
  <text x="360" y="450" text-anchor="middle" font-size="13" fill="#33404d" font-family="Microsoft YaHei">+X 200 mm。CPU 窗在正中。</text>
</svg>
</div>
<p class="figcap">图 1. 俯视比例。CPU 肋场比窗口窄，两侧各 0.6 mm。左右浅黄是内存窗，尺寸见 LPDDR 文件。蓝条、红条是左右干管。</p>
<h2>2. 槽和口</h2>
<p>从左数，第 1、3、5… 条在前侧进液，流向 +Y，在后侧出。第 2、4、6… 条在后侧进液，流向 −Y，在前侧出。槽的 Y 向两端是 0.8 mm 铜墙，水不能沿 Y 冲进前后大腔。该进或该出的一端，盖板上有一个与槽同宽、长 1.6 mm 的 Z 向口。邻槽在同一个 Y 上槽顶是封的。</p>
<p>前侧从外到内是：端墙、偶数槽回液口、隔墙、奇数槽供液口，然后才是受热窗。后侧把供液和回液对调。两个流向的润湿长度都是 40 mm。</p>
<h2>3. 厚度</h2>
<p>z 0–2.0 底板，2.0–3.2 通道，3.2–3.5 分型面，3.5–6.0 盖板内腔，6.0–8.0 盖板顶。左右干管把底板局部铣到 z = 1.0，干管深 5 mm，占到 z = 6.0。干管处底板只剩 1.0 mm。</p>
<p class="small">来源：Grace 冷板详细设计报告 v1.0（2026-09-28 流路修订）§4。外形和窗口是候选。</p>
"""
    return page(
        "Grace CPU 冷板 · 结构布局说明",
        "CP-GRACE-MC-01 · CPU 区 · 2026-09-29",
        "中部 48 条沿 Y 的交错槽。左右内存区见 LPDDR 文件。",
        ["候选平面", "无射流", "奇 +Y / 偶 −Y"],
        body,
    )


def cpu_dims() -> str:
    body = """
<p class="lead">CPU 区尺寸都来自 Grace 报告 §4。报告没有给槽宽、节距、窗口的公差，表中不填写假定值。</p>
<h2>1. 窗口和肋场</h2>
<table>
<thead><tr><th>特征</th><th>名义 mm</th><th>状态</th></tr></thead>
<tbody>
<tr><td>整板</td><td>200 × 120 × 8.0</td><td><span class="tagw">平面候选</span></td></tr>
<tr><td>CPU 窗口</td><td>X 80–120，Y 44–76，即 40 × 32</td><td><span class="tagw">候选</span></td></tr>
<tr><td>密封边</td><td>四周 6。空腔 X 6–194，Y 6–114</td><td>方案</td></tr>
<tr><td>槽数</td><td>48。奇数 24 条 +Y，偶数 24 条 −Y</td><td>方案</td></tr>
<tr><td>肋数</td><td>49，槽的两端都有肋</td><td>方案</td></tr>
<tr><td>槽</td><td>0.40 × 1.20</td><td>方案</td></tr>
<tr><td>节距</td><td>0.80，沿 X</td><td>方案</td></tr>
<tr><td>肋场</td><td>38.8，位于 X 80.6–119.4</td><td>方案</td></tr>
<tr><td>窗内边铜</td><td>每侧 0.6</td><td>由 40 与 38.8 相减</td></tr>
<tr><td>受热长度</td><td>32，Y 44–76</td><td><span class="tagw">候选</span></td></tr>
<tr><td>润湿长度</td><td>40，含两端的口</td><td>方案</td></tr>
<tr><td>Z 向口</td><td>0.40 × 1.6</td><td>方案</td></tr>
<tr><td>端墙、隔墙</td><td>沿 Y 0.8</td><td>方案</td></tr>
</tbody>
</table>
<h2>2. 口的 Y 向位置</h2>
<table>
<thead><tr><th>位置</th><th>Y mm</th><th>哪一条通</th></tr></thead>
<tbody>
<tr><td>前端墙</td><td>38.0 – 38.8</td><td>偶数槽到此为止</td></tr>
<tr><td>前侧回液口</td><td>38.8 – 40.4</td><td>偶数槽出口</td></tr>
<tr><td>隔墙</td><td>40.4 – 41.2</td><td>两腔不相通</td></tr>
<tr><td>前侧供液口</td><td>41.2 – 42.8</td><td>奇数槽入口</td></tr>
<tr><td>到受热窗的间隔</td><td>42.8 – 44.0</td><td>1.2</td></tr>
<tr><td>受热窗</td><td>44 – 76</td><td>槽顶封死</td></tr>
<tr><td>后侧间隔</td><td>76.0 – 77.2</td><td>1.2</td></tr>
<tr><td>后侧供液口</td><td>77.2 – 78.8</td><td>偶数槽入口</td></tr>
<tr><td>隔墙</td><td>78.8 – 79.6</td><td></td></tr>
<tr><td>后侧回液口</td><td>79.6 – 81.2</td><td>奇数槽出口</td></tr>
<tr><td>后端墙</td><td>81.2 – 82.0</td><td>奇数槽到此为止</td></tr>
</tbody>
</table>
<h2>3. 厚度和干管</h2>
<table>
<thead><tr><th>层</th><th>mm</th><th>z</th></tr></thead>
<tbody>
<tr><td>底板</td><td>2.0</td><td>0 – 2.0。干管处铣到 1.0</td></tr>
<tr><td>通道</td><td>1.2</td><td>2.0 – 3.2</td></tr>
<tr><td>分型</td><td>0.3</td><td>3.2 – 3.5，只在 Z 向口打开</td></tr>
<tr><td>盖板内腔</td><td>2.5</td><td>3.5 – 6.0</td></tr>
<tr><td>盖顶</td><td>2.0</td><td>6.0 – 8.0</td></tr>
<tr><td>左干管</td><td>X 6.5–13.5，Y 18–102，z 1.0–6.0</td><td>宽 7，深 5</td></tr>
<tr><td>右干管</td><td>X 186.5–193.5，同样断面</td><td>与左干管对称</td></tr>
<tr><td>接头</td><td>外径 8，内径 6，中心 Y = 60</td><td>方案</td></tr>
<tr><td>入口孔板</td><td>4 × Ø1.04，在进液接头里</td><td>配平计算值，托盘实测后冻结</td></tr>
</tbody>
</table>
<p>孔板四孔的面积等效直径是 1.04 × √4 = 2.08 mm。报告写 2.09 mm，差 0.01 mm，按四舍五入，不单列尺寸环。</p>
"""
    return page(
        "Grace CPU 冷板 · 结构尺寸说明",
        "CP-GRACE-MC-01 · CPU 区 · 2026-09-29",
        "窗口、48 条槽、口带和 8.0 mm 厚度。公差报告未给。",
        ["单位 mm", "候选窗口", "未给槽公差"],
        body,
    )


def cpu_chain() -> str:
    rows = "".join([
        judge_row("整板 X", "6.5+7+0.5+50+16+40+16+50+0.5+7+6.5", R["x_grace_sum"], 200, "干管、内存窗、CPU 窗"),
        judge_row("肋场", "49×0.40+48×0.40", R["cpu_field"], 38.8, "两端有肋"),
        judge_row("窗内边铜", "(40−38.8)/2", R["cpu_land"], 0.6, "X 80.6 与 119.4"),
        judge_row("口带到板边的对称", "38+44+38", 120, 120, "槽场 Y 38–82 居中"),
        judge_row("口带各段", "0.8+1.6+0.8+1.6+1.2+32+1.2+1.6+0.8+1.6+0.8", R["cpu_ports_sum"], 44, "38 到 82"),
        judge_row("奇数槽润湿", "81.2−41.2", 40, 40, "供液口起点到回液口终点"),
        judge_row("偶数槽润湿", "78.8−38.8", 40, 40, "回液口起点到供液口终点"),
        judge_row("厚度", "2.0+1.2+0.3+2.5+2.0", R["z_grace"], 8, ""),
        judge_row("干管处局部", "1.0+5.0+2.0", R["rail_stack"], 8, "余铜 + 干管 + 盖顶"),
        judge_row("接头对两套供液口", "(42.0+78.0)/2", 60, 60, "前供液口中心 42，后供液口中心 78"),
        judge_row("孔板等效直径", "1.04×√4", R["deq"], 2.08, "报告写 2.09，差 0.01"),
    ])
    body = f"""
<p class="lead">CPU 区的链分三层：整板 200 × 120 × 8 是否被窗口和厚度层加满，48 条槽是否放进 40 mm 窗口，两套口是否都给出 40 mm 润湿长度。名义计算全部闭合。报告没有槽公差，没有极值尺寸链。</p>
<h2>1. 名义尺寸链</h2>
<table>
<thead><tr><th>链</th><th>算式</th><th>结果</th><th>期望</th><th>差</th><th>判定</th><th>说明</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<h2>2. 核实2</h2>
<p>肋场从窗口左边加起：80 + 0.6 = 80.6，80.6 + 38.8 = 119.4，119.4 + 0.6 = 120。与报告“居中于 X 80–120”一致。</p>
<p>奇数槽的流体从 Y 41.2 进入，到 Y 81.2 离开，长度 40。偶数槽从 Y 78.8 进入、到 Y 38.8 离开，长度也是 40。口带从 38 到 82 共 44 mm，比润湿长度多 4 mm。这 4 mm 是前端墙 0.8、前侧另一流向的口 1.6、前隔墙 0.8 和后端墙 0.8，不是四道墙（四道墙只有 3.2 mm）。按各流向自己的起止点计算，润湿长度闭合。</p>
<p>厚度从 z = 0 加到 z = 8：2.0、3.2、3.5、6.0、8.0，五层相接，没有缝也没有重叠。干管把 z 1–6 铣空之后，剩下的 1.0 与 2.0 盖顶仍加回 8.0。</p>
<div class="note">
<p>干管底部余铜 1.0 mm 比 B300 冷板要求的 1.8 mm 薄。这是 Grace 报告已经标出的刚度问题，算术上厚度链仍然闭合。内存槽深 0.80 mm 小于通道层 1.20 mm，那 0.40 mm 的差在 LPDDR 文件里说明，不放进 CPU 槽深。</p>
</div>
<p class="small">Excel：<code>Grace_CPU冷板_尺寸核实2计算.xlsx</code>。内存窗的 50 mm 和 6 条槽在 LPDDR 工作簿里。</p>
"""
    return page(
        "Grace CPU 冷板 · 尺寸链计算报告",
        "CP-GRACE-MC-01 · CPU 区 · 2026-09-29",
        "200、38.8、44、40、8.0 各条名义链闭合。未给公差。",
        ["名义闭合", "干管余铜 1.0", "孔板等效差 0.01"],
        body,
    )


def lp_layout() -> str:
    body = f"""
<p class="lead">LPDDR 冷板是 CP-GRACE-MC-01 左右两个内存窗里的槽，也就是所问的 LLDDRAM 冷板。它和 CPU 共用一块 200 × 120 × 8.0 mm 的铜，共用左右干管和前后廊。每侧 6 条槽，截面 1.20 × 0.80 mm，奇数 3 条流向 +Y，偶数 3 条流向 −Y。</p>
<div class="grid">
  <div class="card"><b>50 × 70</b>每侧窗口，候选</div>
  <div class="card"><b>6 槽 / 侧</b>1.20 × 0.80</div>
  <div class="card"><b>节距 8</b>报告写“约 8”，核实按 8.00</div>
  <div class="card"><b>两侧各 4.40</b>按 8.00 居中后的边距</div>
</div>
<h2>1. 窗口</h2>
<p>左窗 X 14–64，右窗 X 136–186，Y 都是 25–95。两窗关于板中心 X = 100 对称：14 到 100 的距离是 86，100 到 186 也是 86。CPU 窗在 X 80–120，左窗右缘 64 到 CPU 左缘 80 有 16 mm 铜，右侧同样 16 mm。</p>
<p>槽沿 Y。节距沿 X，铺在 50 mm 窗内。报告写节距约 8 mm，没有更细的数。核实计算把节距取为 8.00 mm，6 条槽居中。这 8.00 是核实取值，窗口一旦按盖板图移动，节距规则不变，边距会跟着变。</p>
<h2>2. 流向和限流缝</h2>
<p>奇偶规则与 CPU 相同，口的 Y 向位置不同。每侧在供液分成前后两路之前有一条缝，断面 0.80 × 1.20 mm，长 12 mm。缝比槽窄，深度用满通道层的 1.20 mm。报告没有给缝的 X、Y 坐标，布局只确定它在分叉之前，尺寸链不给它一个编造的位置。</p>
<h2>3. 和 CPU 槽深的差别</h2>
<p>通道层是 z 2.0–3.2，深 1.2 mm，CPU 槽把这一层铣满。内存槽深只有 0.80 mm。从分型面 z = 3.2 向下铣 0.80，槽底在 z = 2.4，其下到 z = 2.0 仍有 0.40 mm 铜。若从 z = 2.0 向上只做 0.80 高的肋，槽顶就到不了分型面。两种读法报告都没有画成剖面。尺寸说明采用前一种：从分型面向下铣，因为 CPU 槽就是这样铣满 1.20 mm 的。这一条在尺寸链里单独标成读法，不和 1.20 的通道层加在一起。</p>
<p class="small">来源：Grace 报告 §4.1–§4.4。功率分工（内存合计 40 W）不进入尺寸链。</p>
"""
    return page(
        "LPDDR5X 内存冷板 · 结构布局说明",
        "CP-GRACE-MC-01 · 内存区 · 即 LLDDRAM · 2026-09-29",
        "左右各一个 50 × 70 mm 窗口，每侧 6 条交错槽。",
        ["与 CPU 同板", "节距约 8 mm", "每侧一条限流缝"],
        body,
    )


def lp_dims() -> str:
    body = f"""
<p class="lead">窗口坐标是候选。节距在报告里是“约 8 mm”。下表把核实用的 8.00 mm 和由此算出的边距分开写，避免把推算值写成已经冻结的图纸尺寸。</p>
<table>
<thead><tr><th>特征</th><th>名义 mm</th><th>状态</th></tr></thead>
<tbody>
<tr><td>左窗</td><td>X 14–64，Y 25–95，50 × 70</td><td><span class="tagw">候选</span></td></tr>
<tr><td>右窗</td><td>X 136–186，Y 25–95</td><td><span class="tagw">候选</span></td></tr>
<tr><td>每侧条数</td><td>6。奇数 3 条 +Y，偶数 3 条 −Y</td><td>方案</td></tr>
<tr><td>槽</td><td>宽 1.20 × 深 0.80</td><td>方案。深小于通道层 1.20</td></tr>
<tr><td>节距</td><td>约 8。核实取值 8.00</td><td><span class="tagw">未冻结到 0.01</span></td></tr>
<tr><td>肋（按节距 8.00）</td><td>{fmt(R['mem_rib'], 2)}</td><td>8.00 − 1.20，推算</td></tr>
<tr><td>槽场外宽（按 8.00）</td><td>{fmt(R['mem_pitch_span'], 2)}</td><td>5×8.00+1.20</td></tr>
<tr><td>窗内每侧边距</td><td>{fmt(R['mem_side'], 2)}</td><td>居中推算，不是报告原句</td></tr>
<tr><td>受热长度</td><td>70，Y 25–95</td><td><span class="tagw">候选</span></td></tr>
<tr><td>润湿长度</td><td>78</td><td>方案</td></tr>
<tr><td>Z 向口</td><td>1.20 × 1.6</td><td>方案</td></tr>
<tr><td>端墙、隔墙</td><td>0.8</td><td>方案</td></tr>
<tr><td>限流缝</td><td>0.80 × 1.20，长 12，每侧一条</td><td>位置未给坐标</td></tr>
</tbody>
</table>
<h3>口的 Y 向位置</h3>
<table>
<thead><tr><th>位置</th><th>Y mm</th><th>通哪一条</th></tr></thead>
<tbody>
<tr><td>前端墙</td><td>19.0 – 19.8</td><td>偶数槽终端</td></tr>
<tr><td>前侧回液口</td><td>19.8 – 21.4</td><td>偶数槽</td></tr>
<tr><td>隔墙</td><td>21.4 – 22.2</td><td></td></tr>
<tr><td>前侧供液口</td><td>22.2 – 23.8</td><td>奇数槽</td></tr>
<tr><td>间隔</td><td>23.8 – 25.0</td><td>1.2</td></tr>
<tr><td>受热窗</td><td>25 – 95</td><td></td></tr>
<tr><td>间隔</td><td>95.0 – 96.2</td><td>1.2</td></tr>
<tr><td>后侧供液口</td><td>96.2 – 97.8</td><td>偶数槽</td></tr>
<tr><td>隔墙</td><td>97.8 – 98.6</td><td></td></tr>
<tr><td>后侧回液口</td><td>98.6 – 100.2</td><td>奇数槽</td></tr>
<tr><td>后端墙</td><td>100.2 – 101.0</td><td>奇数槽终端</td></tr>
</tbody>
</table>
<p>后供液廊 Y 103–112，高 9。前回液廊 Y 8–16，高 8。两廊不等高，尺寸说明照录，不改成对称。</p>
"""
    return page(
        "LPDDR5X 内存冷板 · 结构尺寸说明",
        "CP-GRACE-MC-01 · 内存区 · 2026-09-29",
        "窗口、6 条槽、口带。节距 8.00 mm 是核实取值。",
        ["单位 mm", "边距 4.40 为推算", "缝的坐标未给"],
        body,
    )


def lp_chain() -> str:
    rows = "".join([
        judge_row("整板 X（与 CPU 同一条）", "6.5+7+0.5+50+16+40+16+50+0.5+7+6.5", R["x_grace_sum"], 200, ""),
        judge_row("左右窗对称", "100−14 与 186−100", 86, 86, "右窗外缘对板中心"),
        judge_row("窗间铜", "80−64", 16, 16, "右侧 136−120 同样是 16"),
        judge_row("槽场放入 50 mm 窗", f"{fmt(R['mem_pitch_span'],2)}+2×{fmt(R['mem_side'],2)}", 50, 50, "节距取 8.00 才有这组边距"),
        judge_row("6 槽与 5 段肋", f"6×1.20+5×{fmt(R['mem_rib'],2)}+2×{fmt(R['mem_side'],2)}", 50, 50, "核实2 展开"),
        judge_row("口带", "0.8+1.6+0.8+1.6+1.2+70+1.2+1.6+0.8+1.6+0.8", R["mem_ports_sum"], 82, "Y 19 到 101"),
        judge_row("奇数槽润湿", "100.2−22.2", 78, 78, ""),
        judge_row("偶数槽润湿", "97.8−19.8", 78, 78, ""),
        judge_row("内存场加上下边带", "19+82+19", 120, 120, "前端墙在 19，后端墙止于 101"),
        judge_row("下边带拆开", "6+2+8+3", 19, 19, "密封、到廊、廊高 8、到端墙"),
        judge_row("上边带拆开", "2+9+2+6", 19, 19, "到廊、廊高 9、到腔顶、密封"),
        judge_row("接头对内存供液口", "(23+97)/2", 60, 60, "前口中心 23，后口中心 97"),
        judge_row("槽深与通道层", "1.20−0.80", 0.4, 0.4, "差 0.40，不并成一条槽深"),
    ])
    body = f"""
<p class="lead">内存区与 CPU 共用整板的 200 mm 和 8.0 mm。本区自己要闭合的是 50 mm 窗口、82 mm 口带和 78 mm 润湿长度。节距按 8.00 mm 取值后，窗口链闭合。若节距只按“约 8”理解，边距 4.40 mm 就还不是图纸尺寸。</p>
<h2>1. 名义尺寸链</h2>
<table>
<thead><tr><th>链</th><th>算式</th><th>结果</th><th>期望</th><th>差</th><th>判定</th><th>说明</th></tr></thead>
<tbody>{rows}</tbody>
</table>
<h2>2. 核实2</h2>
<p>左窗从 X = 14 起。若边距 4.40，第一条槽的左缘在 18.40，中心在 19.00。此后每 8.00 mm 一条，第六条中心在 59.00，右缘在 59.60，再到窗口右缘 64 仍是 4.40。右窗是左窗加 122 mm：14 + 122 = 136，64 + 122 = 186。</p>
<p>Y 向口带从 19.0 加到 101.0，各段之和 82。奇数槽 22.2 到 100.2 为 78，偶数槽 19.8 到 97.8 为 78。前后廊一高 8、一高 9，上下边带却都是 19，板高仍是 120。廊不对称，整板链闭合。</p>
<div class="note">
<p>限流缝 0.80 × 1.20 × 12 没有坐标，不能放进窗口链。槽深 0.80 与通道层 1.20 相差 0.40，已按“从分型面向下铣”写入布局说明；在盖板图或剖面给出槽底 z 之前，这一读法保持为核实假设。</p>
</div>
<p class="small">Excel：<code>LPDDR5X_内存冷板_尺寸核实2计算.xlsx</code>。节距在输入格里，改掉 8.00 后边距和闭合差会重算。</p>
"""
    return page(
        "LPDDR5X 内存冷板 · 尺寸链计算报告",
        "CP-GRACE-MC-01 · 内存区 · 2026-09-29",
        "窗口链在节距 8.00 mm 下闭合。边距是推算值。",
        ["名义闭合", "节距为核实取值", "缝无坐标"],
        body,
    )


def index_html() -> str:
    body = """
<p class="lead">四块冷板其实是两块铜上的四个区。GPU 与 HBM 在 CP-B300-JM-01（95 × 75 × 8.5）。CPU 与 LPDDR 在 CP-GRACE-MC-01（200 × 120 × 8.0）。每个区三份 HTML，外加一份用公式重算的尺寸核实2工作簿。</p>
<table>
<thead><tr><th>区</th><th>布局</th><th>尺寸</th><th>尺寸链</th><th>核实2</th></tr></thead>
<tbody>
<tr><td>GPU 射流</td><td><a href="GPU_射流冲击微通道冷板_结构布局说明.html">布局</a></td><td><a href="GPU_射流冲击微通道冷板_结构尺寸说明.html">尺寸</a></td><td><a href="GPU_射流冲击微通道冷板_尺寸链计算报告.html">尺寸链</a></td><td>GPU_射流冲击微通道冷板_尺寸核实2计算.xlsx</td></tr>
<tr><td>HBM</td><td><a href="HBM_微通道冷板_结构布局说明.html">布局</a></td><td><a href="HBM_微通道冷板_结构尺寸说明.html">尺寸</a></td><td><a href="HBM_微通道冷板_尺寸链计算报告.html">尺寸链</a></td><td>HBM_微通道冷板_尺寸核实2计算.xlsx</td></tr>
<tr><td>Grace CPU</td><td><a href="Grace_CPU冷板_结构布局说明.html">布局</a></td><td><a href="Grace_CPU冷板_结构尺寸说明.html">尺寸</a></td><td><a href="Grace_CPU冷板_尺寸链计算报告.html">尺寸链</a></td><td>Grace_CPU冷板_尺寸核实2计算.xlsx</td></tr>
<tr><td>LPDDR5X</td><td><a href="LPDDR5X_内存冷板_结构布局说明.html">布局</a></td><td><a href="LPDDR5X_内存冷板_结构尺寸说明.html">尺寸</a></td><td><a href="LPDDR5X_内存冷板_尺寸链计算报告.html">尺寸链</a></td><td>LPDDR5X_内存冷板_尺寸核实2计算.xlsx</td></tr>
</tbody>
</table>
<h2>计算时采纳的口径</h2>
<table>
<thead><tr><th>对象</th><th>采纳</th><th>不采纳</th></tr></thead>
<tbody>
<tr><td>GPU</td><td>v2.0 图纸：216 孔，Ø0.50，节距 3.0 × 2.4，槽 0.40 × 1.50，35 条/die，腔体 8.0，外形 8.5</td><td>asm_0921 的 12.5 mm 与 128 孔；UC01b 的 Ø0.40；v1 的 8×8 孔和 1 mm 铜岛</td></tr>
<tr><td>HBM</td><td>2026-09-28：0.80 × 2.00，肋 0.80，每侧 7 条，岸 0.30，上板 4.0。堆叠坐标仍用 §8.1</td><td>正文旧值 0.60 × 1.50、每侧 8 条</td></tr>
<tr><td>CPU</td><td>Grace 报告 §4：48 × 0.40 × 1.20，节距 0.80，肋场 38.8，厚度 8.0</td><td>不把 B300 的射流孔和 8.5 mm 厚度搬过来</td></tr>
<tr><td>LPDDR</td><td>每侧 6 × 1.20 × 0.80。节距核实取值 8.00，边距由此算出</td><td>不把“约 8 mm”写成已经冻结的唯一值</td></tr>
</tbody>
</table>
<div class="note">
<p>名义链是闭合的。两件不能靠加法消掉：GPU 射流在 X 向与 die 等宽，±0.20 mm 对位会使 die 边缘露出；HBM 槽深 2.0 mm，GPU 槽深 1.5 mm，同一块底板要分区铣。</p>
</div>
"""
    return page(
        "冷板尺寸链文件索引",
        "尺寸链计算 · 2026-09-29",
        "GPU、HBM、Grace CPU、LPDDR5X 四套说明与核实表。",
        ["两块铜", "四个区", "核实2 为 Excel 公式"],
        body,
    )


# ---------- Excel ----------

NAVY = "0B2748"
THIN = Border(
    left=Side(style="thin", color="D7E0EC"),
    right=Side(style="thin", color="D7E0EC"),
    top=Side(style="thin", color="D7E0EC"),
    bottom=Side(style="thin", color="D7E0EC"),
)
FILL_H = PatternFill("solid", fgColor=NAVY)
FILL_IN = PatternFill("solid", fgColor="EEF5FF")
FILL_OK = PatternFill("solid", fgColor="E5F6F1")
FONT_H = Font(color="FFFFFF", bold=True, name="Microsoft YaHei", size=11)
FONT = Font(name="Microsoft YaHei", size=11)
FONT_B = Font(name="Microsoft YaHei", size=11, bold=True)


def _wb() -> Workbook:
    wb = Workbook()
    wb.calculation = CalcProperties(calcMode="auto", fullCalcOnLoad=True)
    return wb


def _head(ws, headers: list[str]) -> None:
    for i, h in enumerate(headers, 1):
        cell = ws.cell(1, i, h)
        cell.fill = FILL_H
        cell.font = FONT_H
        cell.alignment = Alignment(wrap_text=True, vertical="center")
        cell.border = THIN
    ws.row_dimensions[1].height = 22
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(headers))}1"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToPage = True
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.oddHeader.left.text = ws.title
    ws.oddFooter.right.text = "尺寸核实2 · 公式重算"


def _widths(ws, widths: list[float]) -> None:
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _write_inputs(ws, rows: list[tuple]) -> dict[str, str]:
    """rows: (key, value, unit, source, note). Return key -> cell."""
    _head(ws, ["代号", "数值", "单位", "来源", "备注"])
    _widths(ws, [28, 14, 10, 42, 55])
    loc = {}
    for i, (key, val, unit, src, note) in enumerate(rows, 2):
        ws.cell(i, 1, key).font = FONT_B
        c = ws.cell(i, 2, val)
        c.font = FONT
        c.fill = FILL_IN
        c.number_format = "0.000"
        c.border = THIN
        ws.cell(i, 3, unit).font = FONT
        ws.cell(i, 4, src).font = FONT
        ws.cell(i, 5, note).font = FONT
        for col in range(1, 6):
            ws.cell(i, col).alignment = Alignment(wrap_text=True, vertical="center")
            ws.cell(i, col).border = THIN
        loc[key] = f"输入!B{i}"
    ws.auto_filter.ref = f"A1:E{len(rows)+1}"
    return loc


def _chain_sheet(wb, items: list[dict]) -> None:
    ws = wb.create_sheet("尺寸链")
    _head(ws, ["链", "算式（公式）", "结果", "期望", "差", "判定", "说明"])
    _widths(ws, [28, 55, 14, 14, 12, 12, 45])
    for i, it in enumerate(items, 2):
        ws.cell(i, 1, it["name"]).font = FONT
        ws.cell(i, 2, it["expr_text"]).font = Font(name="Consolas", size=10)
        ws.cell(i, 3, it["formula"]).font = FONT
        ws.cell(i, 3).number_format = "0.000"
        ws.cell(i, 4, it["expect"]).font = FONT
        ws.cell(i, 4).number_format = "0.000"
        ws.cell(i, 5, f"=C{i}-D{i}").font = FONT
        ws.cell(i, 5).number_format = "0.000"
        ws.cell(i, 6, f'=IF(ABS(E{i})<0.001,"闭合","不闭合")').font = FONT_B
        ws.cell(i, 7, it.get("note", "")).font = FONT
        for col in range(1, 8):
            ws.cell(i, col).alignment = Alignment(wrap_text=True, vertical="center")
            ws.cell(i, col).border = THIN
        ws.row_dimensions[i].height = 32


def _walk_sheet(wb, title_rows: list[dict]) -> None:
    ws = wb.create_sheet("核实2")
    _head(ws, ["站", "增量", "累计", "图纸坐标", "差", "判定", "说明"])
    _widths(ws, [32, 14, 14, 14, 12, 12, 40])
    for i, it in enumerate(title_rows, 2):
        ws.cell(i, 1, it["name"]).font = FONT
        if i == 2:
            ws.cell(i, 2, it["inc"]).font = FONT
            ws.cell(i, 3, f"=B{i}").font = FONT
        else:
            ws.cell(i, 2, it["inc"]).font = FONT
            ws.cell(i, 3, f"=C{i-1}+B{i}").font = FONT
        ws.cell(i, 2).number_format = "0.000"
        ws.cell(i, 3).number_format = "0.000"
        ws.cell(i, 4, it["declared"]).font = FONT
        ws.cell(i, 4).number_format = "0.000"
        ws.cell(i, 5, f"=C{i}-D{i}").font = FONT
        ws.cell(i, 5).number_format = "0.000"
        ws.cell(i, 6, f'=IF(ABS(E{i})<0.001,"一致","偏差")').font = FONT_B
        ws.cell(i, 7, it.get("note", "")).font = FONT
        for col in range(1, 8):
            ws.cell(i, col).border = THIN
            ws.cell(i, col).alignment = Alignment(wrap_text=True, vertical="center")


def _note_sheet(wb, lines: list[str]) -> None:
    ws = wb.create_sheet("不采用与说明")
    ws.column_dimensions["A"].width = 120
    for i, line in enumerate(lines, 1):
        ws.cell(i, 1, line).font = FONT
        ws.cell(i, 1).alignment = Alignment(wrap_text=True, vertical="center")
        ws.row_dimensions[i].height = 36


def build_gpu_xlsx() -> None:
    g = G
    loc_rows = [
        ("边距X", g["margin_x"], "mm", "§8.1 X 向链首项", "左右对称"),
        ("HBM宽", g["hbm_w"], "mm", "§8.1", ""),
        ("肋缝", g["gap_rib"], "mm", "§8.1", "肋与 HBM、肋与 die"),
        ("隔离肋宽", g["rib_w"], "mm", "§8.1", ""),
        ("die宽", g["die_x"], "mm", "§8.1", ""),
        ("die高", g["die_y"], "mm", "§8.1", ""),
        ("HBI", g["hbi"], "mm", "§8.1", ""),
        ("余铜", g["base"], "mm", "§6.2", ""),
        ("槽深", g["gpu_groove_d"], "mm", "§6.2", "仅 GPU 区"),
        ("喷距H", g["gap_h"], "mm", "§6.2", "公差 ±0.10 不写进本格"),
        ("喷嘴板厚", g["nozzle_t"], "mm", "§6.2", ""),
        ("钎缝", g["braze"], "mm", "§6.2", ""),
        ("孔数X", g["jet_nx"], "个", "§8.1", "每 die"),
        ("孔数Y", g["jet_ny"], "个", "§8.1", "每 die"),
        ("节距X", g["jet_px"], "mm", "§8.1", ""),
        ("节距Y", g["jet_py"], "mm", "§8.1", ""),
        ("孔径", g["jet_d"], "mm", "§5.4 / §6.5", "图纸基准，不是 UC01b 的 0.40"),
        ("槽宽", g["groove_w"], "mm", "§5.2", ""),
        ("槽节距", g["groove_pitch"], "mm", "§5.2", ""),
        ("槽数", g["groove_n"], "条", "§8.1", "每 die"),
        ("对位公差", g["align_tol"], "mm", "§6.5", "±"),
        ("槽宽公差", g["groove_tol"], "mm", "§6.5", "±"),
        ("孔径上偏差", g["hole_tol_plus"], "mm", "§6.5", "下偏差 0"),
        ("H公差", g["h_tol"], "mm", "§6.5", "±"),
        ("列长", g["col_len"], "mm", "§8.1", "Y 向链用"),
        ("下边", g["hbm_y0"], "mm", "§8.1", "HBM 列起点，也是 Y 向链的下余量"),
    ]
    wb = _wb()
    ws = wb.active
    ws.title = "输入"
    loc = _write_inputs(ws, loc_rows)
    L = loc

    def sm(*keys: str) -> str:
        return "=" + "+".join(L[k] for k in keys)

    items = [
        {"name": "X向整板", "expr_text": "边+HBM+缝+肋+缝+die+HBI+die+缝+肋+缝+HBM+边",
         "formula": "=" + "+".join([
             L["边距X"], L["HBM宽"], L["肋缝"], L["隔离肋宽"], L["肋缝"], L["die宽"], L["HBI"],
             L["die宽"], L["肋缝"], L["隔离肋宽"], L["肋缝"], L["HBM宽"], L["边距X"]]),
         "expect": 95, "note": "期望 95"},
        {"name": "Y向", "expr_text": "下边+列长+下边",
         "formula": f"={L['下边']}+{L['列长']}+{L['下边']}", "expect": 75, "note": "上下余量相等"},
        {"name": "腔体", "expr_text": "余铜+槽深+H+喷嘴板",
         "formula": f"={L['余铜']}+{L['槽深']}+{L['喷距H']}+{L['喷嘴板厚']}", "expect": 8, "note": ""},
        {"name": "外形总厚", "expr_text": "腔体+钎缝",
         "formula": f"={L['余铜']}+{L['槽深']}+{L['喷距H']}+{L['喷嘴板厚']}+{L['钎缝']}",
         "expect": 8.5, "note": ""},
        {"name": "中心距X", "expr_text": "(孔数X-1)×节距X",
         "formula": f"=({L['孔数X']}-1)*{L['节距X']}", "expect": 24, "note": ""},
        {"name": "中心距Y", "expr_text": "(孔数Y-1)×节距Y",
         "formula": f"=({L['孔数Y']}-1)*{L['节距Y']}", "expect": 26.4, "note": ""},
        {"name": "覆盖X", "expr_text": "孔数X×节距X",
         "formula": f"={L['孔数X']}*{L['节距X']}", "expect": 27, "note": "等于 die 宽"},
        {"name": "覆盖Y", "expr_text": "孔数Y×节距Y",
         "formula": f"={L['孔数Y']}*{L['节距Y']}", "expect": 28.8, "note": ""},
        {"name": "Y超出die", "expr_text": "覆盖Y-die高",
         "formula": f"={L['孔数Y']}*{L['节距Y']}-{L['die高']}", "expect": 0.8, "note": ""},
        {"name": "槽场", "expr_text": "槽数×槽节距",
         "formula": f"={L['槽数']}*{L['槽节距']}", "expect": 28, "note": "等于 die 高"},
        {"name": "孔数", "expr_text": "2×孔数X×孔数Y",
         "formula": f"=2*{L['孔数X']}*{L['孔数Y']}", "expect": 216, "note": ""},
        {"name": "肋最小", "expr_text": "槽节距-槽宽-槽宽公差",
         "formula": f"={L['槽节距']}-{L['槽宽']}-{L['槽宽公差']}", "expect": 0.37, "note": "工艺下限 0.30，本链期望按公差下限"},
        {"name": "Y向对位后单侧余量", "expr_text": "(覆盖Y-die高)/2-对位公差",
         "formula": f"=({L['孔数Y']}*{L['节距Y']}-{L['die高']})/2-{L['对位公差']}",
         "expect": 0.2, "note": "仍为正"},
        {"name": "X向对位后单侧余量", "expr_text": "(覆盖X-die宽)/2-对位公差",
         "formula": f"=({L['孔数X']}*{L['节距X']}-{L['die宽']})/2-{L['对位公差']}",
         "expect": 0, "note": "结果为 −0.20。相对 0 判为不闭合，表示 die 边缘露出"},
    ]
    _chain_sheet(wb, items)

    # 核实2 X 走查。增量引用输入。
    # 0, +边, +HBM, +缝, +肋, +缝, +die, +HBI, +die, +缝, +肋, +缝, +HBM, +边
    incs = [
        ("板左缘", 0, 0, "原点"),
        ("左HBM起点", f"={L['边距X']}", 5, "§8.1 X=5"),
        ("左HBM右缘", f"={L['HBM宽']}", 16, ""),
        ("左肋起点", f"={L['肋缝']}", 16.5, ""),
        ("左肋右缘", f"={L['隔离肋宽']}", 18.5, ""),
        ("Die-A起点", f"={L['肋缝']}", 19, ""),
        ("Die-A右缘 / HBI起点", f"={L['die宽']}", 46, ""),
        ("Die-B起点", f"={L['HBI']}", 49, ""),
        ("Die-B右缘", f"={L['die宽']}", 76, ""),
        ("右肋起点", f"={L['肋缝']}", 76.5, ""),
        ("右肋右缘", f"={L['隔离肋宽']}", 78.5, ""),
        ("右HBM起点", f"={L['肋缝']}", 79, ""),
        ("右HBM右缘", f"={L['HBM宽']}", 90, ""),
        ("板右缘", f"={L['边距X']}", 95, "应等于 95"),
    ]
    _walk_sheet(wb, [{"name": n, "inc": inc, "declared": d, "note": note} for n, inc, d, note in incs])
    _note_sheet(wb, [
        "不采用：asm_0921 外形厚 12.5 mm，喷嘴 128 × Ø0.50。那是另一条厚度链。",
        "不采用：UC01b 网格孔径 0.40 mm。只说明若改孔径，H/D 会从 4 变为 5，X/Y 位置链不变。图纸基准仍是 0.50。",
        "不采用：v1 参数集每 die 8×8 孔、段间铜岛 1.0 mm。与 v2 的 9×12、流程 3.0 mm 不能同时成立。",
        "X 向覆盖链名义闭合。尺寸链最后一行把对位后的单侧余量与 0 比较，结果 −0.20 mm，判定为不闭合，表示 die 边缘会露出。",
        "段间铜岛宽度报告未给，工作簿不设这个输入。",
    ])
    wb.save(OUT / "GPU_射流冲击微通道冷板_尺寸核实2计算.xlsx")


def build_hbm_xlsx() -> None:
    rows = [
        ("岸", H["shore"], "mm", "2026-09-28 修订", "单侧"),
        ("槽宽", H["ch_w"], "mm", "修订 / w08h20", ""),
        ("槽深", H["ch_d"], "mm", "修订", "深于 GPU 的 1.5"),
        ("肋", H["rib"], "mm", "修订", ""),
        ("条数", H["n"], "条", "修订", "每侧"),
        ("偶数条", H["n_even"], "条", "修订", ""),
        ("奇数条", H["n_odd"], "条", "修订", ""),
        ("底铜", H["base"], "mm", "修订", ""),
        ("上铜板", H["top"], "mm", "修订", ""),
        ("竖向口高", H["port_h"], "mm", "修订 z 2–3", ""),
        ("汇流腔高", H["man_h"], "mm", "修订 z 3–6", ""),
        ("堆叠边", G["hbm_h"], "mm", "§8.1", "11"),
        ("颗数", G["hbm_n"], "颗", "§8.1", "每列"),
        ("颗间", G["hbm_gap_y"], "mm", "§8.1 原点差", ""),
        ("板高", G["plate_y"], "mm", "§8.1", ""),
        ("列起点Y", G["hbm_y0"], "mm", "§8.1", ""),
        ("GPU槽深", G["gpu_groove_d"], "mm", "§6.2", "对照"),
        ("喷距", G["gap_h"], "mm", "§6.2", "HBM 加热段不用"),
        ("喷嘴板", G["nozzle_t"], "mm", "§6.2", "对照"),
    ]
    wb = _wb()
    ws = wb.active
    ws.title = "输入"
    L = _write_inputs(ws, rows)
    items = [
        {"name": "单侧宽", "expr_text": "2×岸+条数×槽宽+(条数-1)×肋",
         "formula": f"=2*{L['岸']}+{L['条数']}*{L['槽宽']}+({L['条数']}-1)*{L['肋']}",
         "expect": 11, "note": ""},
        {"name": "奇偶条数", "expr_text": "偶数+奇数",
         "formula": f"={L['偶数条']}+{L['奇数条']}", "expect": 7, "note": "应等于条数"},
        {"name": "条数一致", "expr_text": "偶数+奇数-条数",
         "formula": f"={L['偶数条']}+{L['奇数条']}-{L['条数']}", "expect": 0, "note": "差为 0 即一致"},
        {"name": "列长", "expr_text": "颗数×堆叠边+(颗数-1)×颗间",
         "formula": f"={L['颗数']}*{L['堆叠边']}+({L['颗数']}-1)*{L['颗间']}",
         "expect": 50, "note": ""},
        {"name": "板高", "expr_text": "列起点+列长+列起点",
         "formula": f"={L['列起点Y']}+{L['颗数']}*{L['堆叠边']}+({L['颗数']}-1)*{L['颗间']}+{L['列起点Y']}",
         "expect": 75, "note": "上下余量都取列起点 12.5"},
        {"name": "加热段厚", "expr_text": "底铜+槽深+上铜板",
         "formula": f"={L['底铜']}+{L['槽深']}+{L['上铜板']}", "expect": 8, "note": ""},
        {"name": "上板拆分", "expr_text": "竖向口+汇流腔",
         "formula": f"={L['竖向口高']}+{L['汇流腔高']}", "expect": 4, "note": "应等于上铜板"},
        {"name": "上板差", "expr_text": "竖向口+汇流腔-上铜板",
         "formula": f"={L['竖向口高']}+{L['汇流腔高']}-{L['上铜板']}", "expect": 0, "note": ""},
        {"name": "GPU腔体对照", "expr_text": "底铜+GPU槽深+喷距+喷嘴板",
         "formula": f"={L['底铜']}+{L['GPU槽深']}+{L['喷距']}+{L['喷嘴板']}",
         "expect": 8, "note": "总数同为 8，槽深不同"},
        {"name": "槽深差", "expr_text": "HBM槽深-GPU槽深",
         "formula": f"={L['槽深']}-{L['GPU槽深']}", "expect": 0.5, "note": "必须分区铣。期望 0.5 表示差被明确算出来"},
    ]
    _chain_sheet(wb, items)
    # 累计是列内坐标。图纸 Y = 列内 + 12.5，写在说明里。
    incs = [
        ("列底", 0, 0, "列内 0，板上 Y=12.5"),
        ("第1颗顶", f"={L['堆叠边']}", 11, "板上 23.5"),
        ("第2颗底", f"={L['颗间']}", 13, "板上 25.5"),
        ("第2颗顶", f"={L['堆叠边']}", 24, "板上 36.5"),
        ("第3颗底", f"={L['颗间']}", 26, "板上 38.5"),
        ("第3颗顶", f"={L['堆叠边']}", 37, "板上 49.5"),
        ("第4颗底", f"={L['颗间']}", 39, "板上 51.5"),
        ("第4颗顶 / 列长", f"={L['堆叠边']}", 50, "板上 62.5，列长 50"),
    ]
    _walk_sheet(wb, [{"name": n, "inc": inc, "declared": d, "note": note} for n, inc, d, note in incs])
    _note_sheet(wb, [
        "现行截面：0.80 × 2.00，肋 0.80，每侧 7 条，岸 0.30。来自 B300 报告文首 2026-09-28 修订和 HBM_w08h20 网格。",
        "不采用：正文旧值 0.60 × 1.50、节距 1.30、每侧 8 条、岸 0.65。该组加总也是 11 mm，但不是现行加工尺寸。",
        "槽深差一行的期望是 0.5 mm。判定为闭合表示差被算成 0.5，不是表示两区槽深相同。",
        "条数一致、上板差两行的期望是 0。",
        "堆叠 X、Y 仍是候选坐标，公差未给，本表只核名义值。",
    ])
    wb.save(OUT / "HBM_微通道冷板_尺寸核实2计算.xlsx")


def build_cpu_xlsx() -> None:
    c = C
    rows = [
        ("板宽", c["plate_x"], "mm", "§4.1", "候选"),
        ("板高", c["plate_y"], "mm", "§4.1", "候选"),
        ("底板", c["base"], "mm", "§4.1", ""),
        ("通道层", c["ch_layer"], "mm", "§4.1", "CPU 槽铣满"),
        ("分型", c["parting"], "mm", "§4.1", ""),
        ("内腔", c["cavity"], "mm", "§4.1", ""),
        ("盖顶", c["lid"], "mm", "§4.1", ""),
        ("窗宽", c["cpu_x1"] - c["cpu_x0"], "mm", "§4.1", "40"),
        ("窗高", c["cpu_y1"] - c["cpu_y0"], "mm", "§4.1", "32"),
        ("槽数", c["cpu_n"], "条", "§4.2", ""),
        ("肋数", c["cpu_rib_n"], "条", "§4.2", ""),
        ("槽宽", c["cpu_w"], "mm", "§4.2", "肋宽与槽宽相同"),
        ("槽深", c["cpu_d"], "mm", "§4.2", ""),
        ("墙", c["wall"], "mm", "§4.3", "0.8"),
        ("口长", c["port_l"], "mm", "§4.2", "1.6"),
        ("间隔", c["gap_heat"], "mm", "§4.3", "1.2"),
        ("干管余铜", c["rail_z0"], "mm", "§4.1", "局部"),
        ("干管深", c["rail_z1"] - c["rail_z0"], "mm", "§4.4", "z 1–6"),
        ("孔板孔径", c["orifice_d"], "mm", "§4.4", ""),
        ("孔板孔数", c["orifice_n"], "个", "§4.4", ""),
        ("左干管起点", c["rail_x0"], "mm", "§4.4", "6.5"),
        ("干管宽", c["rail_w"], "mm", "§4.4", ""),
        ("内存窗宽", c["mem_win"], "mm", "§4.1", "整板 X 链用"),
        ("窗间铜", c["cpu_x0"] - c["mem_x1"], "mm", "坐标相减", "16"),
        ("干管到内存", 0.5, "mm", "13.5 到 14", "右侧同样"),
    ]
    wb = _wb()
    ws = wb.active
    ws.title = "输入"
    L = _write_inputs(ws, rows)
    items = [
        {"name": "厚度", "expr_text": "底板+通道层+分型+内腔+盖顶",
         "formula": f"={L['底板']}+{L['通道层']}+{L['分型']}+{L['内腔']}+{L['盖顶']}",
         "expect": 8, "note": ""},
        {"name": "肋场", "expr_text": "肋数×槽宽+槽数×槽宽",
         "formula": f"={L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}",
         "expect": 38.8, "note": ""},
        {"name": "边铜", "expr_text": "(窗宽-肋场)/2",
         "formula": f"=({L['窗宽']}-({L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}))/2",
         "expect": 0.6, "note": ""},
        {"name": "口带高", "expr_text": "4×墙+4×口长+2×间隔+窗高",
         "formula": f"=4*{L['墙']}+4*{L['口长']}+2*{L['间隔']}+{L['窗高']}",
         "expect": 44, "note": "Y 38 到 82"},
        {"name": "润湿", "expr_text": "口带高-(3×墙+1个另一流向的口)",
         "formula": f"=4*{L['墙']}+4*{L['口长']}+2*{L['间隔']}+{L['窗高']}-(3*{L['墙']}+{L['口长']})",
         "expect": 40, "note": "44 里去掉前端墙、前隔墙、后端墙和另一流向的口，共 4 mm"},
        {"name": "Y居中", "expr_text": "(板高-口带高)/2",
         "formula": f"=({L['板高']}-(4*{L['墙']}+4*{L['口长']}+2*{L['间隔']}+{L['窗高']}))/2",
         "expect": 38, "note": "下边应等于 38，槽场从 38 起"},
        {"name": "干管局部厚", "expr_text": "干管余铜+干管深+盖顶",
         "formula": f"={L['干管余铜']}+{L['干管深']}+{L['盖顶']}",
         "expect": 8, "note": ""},
        {"name": "整板X", "expr_text": "2×(干管起点+干管宽+缝+内存窗宽+窗间铜)+窗宽",
         "formula": f"=2*({L['左干管起点']}+{L['干管宽']}+{L['干管到内存']}+{L['内存窗宽']}+{L['窗间铜']})+{L['窗宽']}",
         "expect": 200, "note": "左右对称"},
        {"name": "孔板等效直径", "expr_text": "孔径×SQRT(孔数)",
         "formula": f"={L['孔板孔径']}*SQRT({L['孔板孔数']})",
         "expect": 2.08, "note": "报告写 2.09。本行期望 2.08，闭合表示按四孔面积"},
    ]
    _chain_sheet(wb, items)
    # X of rib field inside window: 0, land, field, land = window
    incs = [
        ("窗口左缘 X80", "0", 80, "图纸"),
        ("肋场起点", f"=({L['窗宽']}-({L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}))/2", 80.6, "80.6"),
        ("肋场终点", f"={L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}", 119.4, ""),
        ("窗口右缘", f"=({L['窗宽']}-({L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}))/2", 120, "绝对坐标在说明里；本列累计是从 80 起还是从 0？"),
    ]
    # The walk accumulates increments. Start at 80 by putting 80 as first increment and declared 80.
    incs = [
        ("窗口左缘", 80, 80, "图纸 X=80"),
        ("肋场起点", f"=({L['窗宽']}-({L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}))/2", 80.6, ""),
        ("肋场终点", f"={L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}", 119.4, ""),
        ("窗口右缘", f"=({L['窗宽']}-({L['肋数']}*{L['槽宽']}+{L['槽数']}*{L['槽宽']}))/2", 120, ""),
    ]
    _walk_sheet(wb, [{"name": n, "inc": i, "declared": d, "note": note} for n, i, d, note in incs])
    _note_sheet(wb, [
        "润湿长度：口带 44 mm 减去前端墙、前隔墙、后端墙和另一流向的口（3×0.8+1.6=4），得到 40 mm。奇数槽 81.2−41.2、偶数槽 78.8−38.8 是同一结果。",
        "孔板等效直径按 1.04×√4 = 2.08。报告写 2.09，差 0.01 mm，不另设尺寸环。",
        "干管余铜 1.0 mm 使局部厚度链仍等于 8，但低于 B300 冷板 1.8 mm 的余铜下限。这是刚度问题，不是加法错误。",
        "内存 6 槽和节距不在本工作簿。见 LPDDR5X_内存冷板_尺寸核实2计算.xlsx。",
        "报告未给 CPU 槽公差，本表没有极值列。",
    ])
    wb.save(OUT / "Grace_CPU冷板_尺寸核实2计算.xlsx")


def build_lp_xlsx() -> None:
    c = C
    rows = [
        ("节距", c["mem_p"], "mm", "§4.2 约 8 mm", "核实取值，可改"),
        ("槽宽", c["mem_w"], "mm", "§4.2", ""),
        ("槽深", c["mem_d"], "mm", "§4.2", ""),
        ("条数", c["mem_n"], "条", "§4.2", "每侧"),
        ("窗宽", c["mem_win"], "mm", "§4.1", "50"),
        ("受热长", c["mem_y1"] - c["mem_y0"], "mm", "§4.2", "70"),
        ("墙", c["wall"], "mm", "§4.3", ""),
        ("口长", c["port_l"], "mm", "§4.2", ""),
        ("间隔", c["gap_heat"], "mm", "§4.3", ""),
        ("通道层", c["ch_layer"], "mm", "§4.1", "1.2"),
        ("板高", c["plate_y"], "mm", "§4.1", ""),
        ("前端墙", c["mem_front_wall"], "mm", "§4.3", "19"),
        ("下密封", c["seal"], "mm", "§4.1", ""),
        ("密封到前廊", 2.0, "mm", "Y 6 到 8", ""),
        ("前廊高", c["gal_f1"] - c["gal_f0"], "mm", "§4.4", "8"),
        ("前廊到端墙", 3.0, "mm", "Y 16 到 19", ""),
        ("端墙到后廊", 2.0, "mm", "Y 101 到 103", ""),
        ("后廊高", c["gal_r1"] - c["gal_r0"], "mm", "§4.4", "9"),
        ("后廊到腔顶", 2.0, "mm", "Y 112 到 114", ""),
        ("缝宽", c["slit_w"], "mm", "§4.4", "坐标未给"),
        ("缝深", c["slit_d"], "mm", "§4.4", ""),
        ("缝长", c["slit_l"], "mm", "§4.4", ""),
    ]
    wb = _wb()
    ws = wb.active
    ws.title = "输入"
    L = _write_inputs(ws, rows)
    items = [
        {"name": "槽场外宽", "expr_text": "(条数-1)×节距+槽宽",
         "formula": f"=({L['条数']}-1)*{L['节距']}+{L['槽宽']}",
         "expect": 41.2, "note": "节距 8 时"},
        {"name": "单侧边距", "expr_text": "(窗宽-槽场外宽)/2",
         "formula": f"=({L['窗宽']}-(({L['条数']}-1)*{L['节距']}+{L['槽宽']}))/2",
         "expect": 4.4, "note": "推算，不是报告原句"},
        {"name": "窗口链", "expr_text": "槽场外宽+2×边距",
         "formula": f"=({L['条数']}-1)*{L['节距']}+{L['槽宽']}+2*(({L['窗宽']}-(({L['条数']}-1)*{L['节距']}+{L['槽宽']}))/2)",
         "expect": 50, "note": "恒等于窗宽。改节距后若边距为负，下一行会不闭合"},
        {"name": "边距不为负", "expr_text": "单侧边距",
         "formula": f"=({L['窗宽']}-(({L['条数']}-1)*{L['节距']}+{L['槽宽']}))/2",
         "expect": 4.4, "note": "节距过大时结果为负，判定转为不闭合（相对 4.4）。看数值本身是否≥0"},
        {"name": "口带", "expr_text": "4×墙+4×口长+2×间隔+受热长",
         "formula": f"=4*{L['墙']}+4*{L['口长']}+2*{L['间隔']}+{L['受热长']}",
         "expect": 82, "note": "Y 19 到 101"},
        {"name": "润湿", "expr_text": "口带-4×墙",
         "formula": f"=4*{L['口长']}+2*{L['间隔']}+{L['受热长']}",
         "expect": 78, "note": ""},
        {"name": "下边带", "expr_text": "下密封+到廊+前廊+到端墙",
         "formula": f"={L['下密封']}+{L['密封到前廊']}+{L['前廊高']}+{L['前廊到端墙']}",
         "expect": 19, "note": ""},
        {"name": "上边带", "expr_text": "到后廊+后廊+到腔顶+下密封",
         "formula": f"={L['端墙到后廊']}+{L['后廊高']}+{L['后廊到腔顶']}+{L['下密封']}",
         "expect": 19, "note": "后廊 9，前廊 8，边带仍相等"},
        {"name": "板高", "expr_text": "下边带+口带+上边带",
         "formula": f"={L['下密封']}+{L['密封到前廊']}+{L['前廊高']}+{L['前廊到端墙']}+4*{L['墙']}+4*{L['口长']}+2*{L['间隔']}+{L['受热长']}+{L['端墙到后廊']}+{L['后廊高']}+{L['后廊到腔顶']}+{L['下密封']}",
         "expect": 120, "note": ""},
        {"name": "槽深差", "expr_text": "通道层-槽深",
         "formula": f"={L['通道层']}-{L['槽深']}",
         "expect": 0.4, "note": "从分型面向下铣时，槽底以上多 0.40 铜到通道层底"},
        {"name": "缝与槽深不同", "expr_text": "缝深-槽深",
         "formula": f"={L['缝深']}-{L['槽深']}",
         "expect": 0.4, "note": "缝用满 1.20，槽只 0.80"},
    ]
    _chain_sheet(wb, items)
    incs = [
        ("左窗左缘", 14, 14, "图纸"),
        ("第1槽左缘", f"=({L['窗宽']}-(({L['条数']}-1)*{L['节距']}+{L['槽宽']}))/2", 18.4, "边距"),
        ("第1槽右缘", f"={L['槽宽']}", 19.6, ""),
        ("第6槽右缘", f"=5*{L['节距']}", 59.6, "中间 5 个节距，从第1槽右缘到第6槽右缘"),
        ("左窗右缘", f"=({L['窗宽']}-(({L['条数']}-1)*{L['节距']}+{L['槽宽']}))/2", 64, ""),
    ]
    # Check: 14+4.4=18.4, +1.2=19.6, +5*8=59.6, +4.4=64. Yes.
    # From first right edge to sixth right edge is 5 pitches. Good.
    _walk_sheet(wb, [{"name": n, "inc": i, "declared": d, "note": note} for n, i, d, note in incs])
    _note_sheet(wb, [
        "节距输入格默认 8.00 mm，对应报告“约 8 mm”。边距 4.40 mm 由窗口宽度反算，改节距后边距跟着变。",
        "窗口链一行在代数上恒等于窗宽，所以它总是闭合。判断节距是否放得下，要看“单侧边距”是否大于等于 0。",
        "第6槽右缘的增量是 5 个节距：从第 1 条右缘到第 6 条右缘。",
        "限流缝有断面和长度，没有坐标，没有放进走查。",
        "前后廊高度 8 与 9 不相等。上下边带各 19 mm，板高链仍然闭合。",
        "右窗 = 左窗 + 122 mm（14→136，64→186）。工作簿没有重复右窗的同一条链。",
    ])
    wb.save(OUT / "LPDDR5X_内存冷板_尺寸核实2计算.xlsx")


def main() -> None:
    files = {
        "GPU_射流冲击微通道冷板_结构布局说明.html": gpu_layout(),
        "GPU_射流冲击微通道冷板_结构尺寸说明.html": gpu_dims(),
        "GPU_射流冲击微通道冷板_尺寸链计算报告.html": gpu_chain(),
        "HBM_微通道冷板_结构布局说明.html": hbm_layout(),
        "HBM_微通道冷板_结构尺寸说明.html": hbm_dims(),
        "HBM_微通道冷板_尺寸链计算报告.html": hbm_chain(),
        "Grace_CPU冷板_结构布局说明.html": cpu_layout(),
        "Grace_CPU冷板_结构尺寸说明.html": cpu_dims(),
        "Grace_CPU冷板_尺寸链计算报告.html": cpu_chain(),
        "LPDDR5X_内存冷板_结构布局说明.html": lp_layout(),
        "LPDDR5X_内存冷板_结构尺寸说明.html": lp_dims(),
        "LPDDR5X_内存冷板_尺寸链计算报告.html": lp_chain(),
        "00_尺寸链文件索引.html": index_html(),
    }
    for name, text in files.items():
        (OUT / name).write_text(text, encoding="utf-8")
        print("html", name)
    build_gpu_xlsx()
    build_hbm_xlsx()
    build_cpu_xlsx()
    build_lp_xlsx()
    print("xlsx ok")


if __name__ == "__main__":
    main()
