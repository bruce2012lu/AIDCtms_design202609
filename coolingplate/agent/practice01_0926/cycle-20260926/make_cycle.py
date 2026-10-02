# -*- coding: utf-8 -*-
"""2026-09-26 设计循环：一维计算、示意图、三份 HTML。

数值只来自 design/calc/model.py 和已读过的 Fluent 转录。
不启动第二套 Fluent。CAD 实体由同目录 build_cad.py 另写。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

CYCLE = Path(__file__).resolve().parent
CALC = CYCLE.parents[3] / "design" / "calc"
OUT = CYCLE / "out"
sys.path.insert(0, str(CALC))

import model as M  # noqa: E402

plt.rcParams["font.sans-serif"] = ["Microsoft YaHei", "SimHei", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


def _num(v):
    if isinstance(v, tuple):
        return [_num(x) for x in v]
    if isinstance(v, float):
        return round(v, 6)
    return v


def pack(name: str) -> dict:
    s = M.solve(name)
    j40 = M.jet_state(M.WATER40, s["Qg"], D=0.40, N=M.N_JET)
    return {
        "name": name,
        "role": s["role"],
        "P": s["P"],
        "Q": s["Q"],
        "Qg": s["Qg"],
        "Tin": s["Tin"],
        "target": s["target"],
        "dTf": s["dTf"],
        "R_lo": s["R_lo"],
        "R_hi": s["R_hi"],
        "pass_lo": s["pass_lo"],
        "pass_hi": s["pass_hi"],
        "martin": s["martin_applied"],
        "jet": s["jet"],
        "jet_d040": j40,
        "q_die": s["q_die"],
        "q_cell": s["q_cell"],
        "q_bc": s["q_bc"],
        "q_bc_si": s["q_bc_si"],
        "mdot_hole": s["mdot_hole"],
        "p_die": s["p_die"],
        "p_gpu": s["p_gpu"],
        "p_cell": s["p_cell"],
        "p_hbm": s["p_hbm"],
        "p_other": s["p_other"],
        "con_R": s["con"]["R"],
        "con_h": s["con"]["h_eff"],
        "opt_R": s["opt"]["R"],
        "ch_V": s["ch"]["V"],
        "ch_dP": s["ch"]["dP"],
        "hbm_V": s["hbm"]["V"],
        "hbm_ok": s["hbm"]["ok"],
        "dp_orifice": s["dp"]["orifice"],
        "dp_channel": s["dp"]["channel"],
        "dp_hbm": s["dp"]["hbm"],
        "dp_total": s["dp"]["total"],
        "Tc": s["Tc"],
        "Tj": s["Tj"],
    }


def cfd_point() -> dict:
    """m425 是 216 孔、热流 579282 W/m² 的细网格收敛场。孔径在网格里是 0.40 mm。"""
    q = 579282.0
    a_cell = 3.0 * 2.4 * 1e-6
    p_cell = q * a_cell
    n = 216
    p_2die = p_cell * n
    t_in = 313.15
    t_tim = 341.38529
    t_cu = 326.59968
    t_out = 320.90984
    dp = 1087.0927
    d = 0.40e-3
    mdot = M.mass_flow(M.WATER40, 1.60) / n
    area = 3.141592653589793 / 4 * d * d
    vel = mdot / (M.WATER40.rho * area)
    re = M.WATER40.rho * vel * d / M.WATER40.mu
    return {
        "case": "uc01b_cht_less_m425",
        "iter": 380,
        "cells": 4259680,
        "q": q,
        "p_cell": p_cell,
        "p_2die": p_2die,
        "t_in": t_in,
        "t_tim": t_tim,
        "t_cu": t_cu,
        "t_out": t_out,
        "dp": dp,
        "mdot": mdot,
        "vel": vel,
        "re": re,
        "r_tim": (t_tim - t_in) / p_2die,
        "r_conv": (t_cu - t_in) / p_2die,
        "bc216_dp": 1091.5061,
        "bc216_t": 342.09574,
        "bc216_iter": 421,
        "bc216_cells": 2115436,
        "source": "design/cfd/uc01b_2.4x3.0lessmesh/logs/fluent_cht_less_m425_gpu.log",
    }


def draw(data: dict, cfd: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    g = M.GEO
    fig, ax = plt.subplots(figsize=(8.2, 6.6))
    ax.add_patch(Rectangle((0, 0), g["plate_L"], g["plate_W"], fill=False, lw=1.2, ec="#1c1915"))
    for i, ox in enumerate((g["die_a_x"], g["die_a_x"] + g["die_w"] + g["hbi"])):
        ax.add_patch(Rectangle((ox, g["die_a_y"]), g["die_w"], g["die_h"], fc="#f3d2b3", ec="#8c4a24", lw=0.8))
        jx = g["jet_a_x"] + i * (g["die_w"] + g["hbi"])
        for ix in range(g["n_jet_x"]):
            for iy in range(g["n_jet_y"]):
                ax.add_patch(Circle((jx + ix * g["S_jet_x"], g["jet_a_y"] + iy * g["S_jet_y"]),
                                    g["D_jet"] / 2, fc="#1f4e79", ec="none"))
    for x in g["hbm_x_l"], g["hbm_x_r"]:
        y = g["hbm_y0"]
        for _ in range(4):
            ax.add_patch(Rectangle((x, y), g["hbm_w"], g["hbm_h"], fc="#d9e4f2", ec="#1f4e79", lw=0.6))
            y += g["hbm_dy"]
    ax.set_aspect("equal")
    ax.set_xlim(-2, 98)
    ax.set_ylim(-2, 78)
    ax.set_xlabel("X / mm")
    ax.set_ylabel("Y / mm")
    ax.set_title("CP-B300-JM-01 俯视 · 一维几何 216 孔 D0.50")
    fig.tight_layout()
    fig.savefig(OUT / "fig_layout.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    layers = [
        (0.0, 2.0, "#c47b4a", "余铜 2.0"),
        (2.0, 1.5, "#e6b089", "短槽 1.5"),
        (3.5, 2.0, "#d6e6f5", "喷距 2.0"),
        (5.5, 2.5, "#8c4a24", "喷嘴板 2.5"),
        (8.0, 0.5, "#6b6258", "钎缝 0.5"),
    ]
    for z, h, color, label in layers:
        ax.add_patch(FancyBboxPatch((0.4, z), 6.2, h, boxstyle="square,pad=0", fc=color, ec="white"))
        ax.text(3.5, z + h / 2, label, ha="center", va="center", color="white", fontsize=10)
    ax.set_xlim(0, 7)
    ax.set_ylim(0, 9)
    ax.set_ylabel("Z / mm")
    ax.set_xticks([])
    ax.set_title("厚度栈 · 腔 8.0 + 钎缝 0.5 = 外形 8.5 mm")
    fig.tight_layout()
    fig.savefig(OUT / "fig_stack.png", dpi=140)
    plt.close()

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    ax.add_patch(Rectangle((0, 0), 3.0, 2.0, fc="#c47b4a", ec="#1c1915"))
    for yc, in ((0.4,), (1.2,), (2.0,)):
        ax.add_patch(Rectangle((0, yc - 0.2), 3.0, 0.4, fc="#d6e6f5", ec="#1f4e79"))
    ax.add_patch(Rectangle((0, 3.5), 3.0, 2.5, fc="#8c4a24", ec="#1c1915"))
    ax.add_patch(Rectangle((1.25, 3.5), 0.5, 2.5, fc="#d6e6f5", ec="#1f4e79"))
    ax.set_aspect("equal")
    ax.set_xlim(-0.3, 3.6)
    ax.set_ylim(-0.3, 6.4)
    ax.set_xlabel("X / mm（胞长 3.0）")
    ax.set_title("单孔胞剖面 · 槽 3×0.40，孔 D0.50，喷距 2.0")
    fig.tight_layout()
    fig.savefig(OUT / "fig_cell.png", dpi=140)
    plt.close()

    a = data["DP-A"]
    fig, ax = plt.subplots(figsize=(6.4, 3.4))
    ax.bar(["一维下限", "一维上限", "目标 0.028", "CFD 壳侧"],
           [a["R_lo"], a["R_hi"], 0.028, cfd["r_tim"]],
           color=["#1f6b45", "#8d2b2b", "#8a5a00", "#1f4e79"])
    ax.set_ylabel("°C/W")
    ax.set_title("DP-A 热阻 · 一维区间与单孔 CFD")
    fig.tight_layout()
    fig.savefig(OUT / "fig_r.png", dpi=140)
    plt.close()


CSS = """
body{margin:0;font-family:"Segoe UI","Microsoft YaHei",sans-serif;background:#f4efe6;color:#1c1915}
header{background:#241c16;color:#f3eadf;padding:22px 28px}
header a{color:#f3eadf;margin-right:14px;font-size:14px}
main{padding:22px 28px 48px;max-width:980px}
h1{margin:0 0 6px;font-size:22px} h2{margin:22px 0 8px;font-size:18px}
p{line-height:1.55} table{border-collapse:collapse;width:100%;background:#fff;margin:8px 0 16px}
th,td{border-bottom:1px solid #e2d9cc;padding:7px 9px;text-align:left;font-size:14px;vertical-align:top}
th{color:#5c564c;font-size:12px} img{max-width:100%;background:#fff;border:1px solid #e2d9cc}
.note{background:#fff;border-left:4px solid #8c4a24;padding:10px 14px}
code{font-family:Consolas,monospace;font-size:13px}
"""


def page(title: str, body: str) -> str:
    nav = (
        '<a href="index.html">流程</a>'
        '<a href="01_一维设计.html">1 一维</a>'
        '<a href="02_三维CAD.html">2 三维 CAD</a>'
        '<a href="03_单孔CFD仿真分析.html">3 单孔 CFD</a>'
        '<a href="04_结构工艺装配.html">4 结构工艺装配</a>'
    )
    return (
        "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        f"<title>{title}</title><style>{CSS}</style></head><body>"
        f"<header><div>{nav}</div><h1>{title}</h1>"
        "<p>CP-B300-JM-01 · 设计循环 2026-09-26 · 一维来自 design/calc/model.py</p>"
        f"</header><main>{body}</main></body></html>"
    )


def cad_files() -> str:
    cad = OUT / "cad"
    if not cad.exists():
        return "<p>实体尚未写出。运行 <code>build_cad.py</code> 后刷新本页。</p>"
    rows = []
    for p in sorted(cad.glob("*")):
        if p.is_file():
            rows.append(f"<tr><td><code>{p.name}</code></td><td>{p.stat().st_size/1024:.0f} KB</td></tr>")
    if not rows:
        return "<p>cad 目录是空的。</p>"
    return "<table><tr><th>文件</th><th>大小</th></tr>" + "".join(rows) + "</table>"


def write_html(data: dict, cfd: dict, mech: dict, checks: list) -> None:
    a, b = data["DP-A"], data["DP-B"]
    g = M.GEO
    check_rows = "".join(
        f"<tr><td>{n}</td><td>{expr}</td><td>{got:.3f}</td><td>{exp:.3f}</td></tr>"
        for n, expr, got, exp in checks
    )
    mech_rows = "".join(
        f"<tr><td>{name}</td><td>{sigma/1e6:.2f}</td><td>{w*1e6:.3f}</td><td>{n:.0f}</td></tr>"
        for name, sigma, w, n in mech["cases"]
    )
    (CYCLE / "index.html").write_text(page("冷板设计循环", f"""
<p>这一轮从一维模型重新计算，再按该几何做三维零件，并用已经收敛的单孔共轭场做仿真分析。结构、工艺和装配用同一套厚度栈和解析承压校核。</p>
<div class="note">本机已有 4 个 Fluent MPI 进程在算 12 层网格续算，这一轮没有再启动求解器。单孔结论取 2026-09-25 已收敛的 m425 场。</div>
<h2>五步</h2>
<table>
<tr><th>步骤</th><th>结果</th></tr>
<tr><td>1D 设计</td><td>DP-A {a['P']:.0f} W @ {a['Q']:.1f} L/min，216 孔，壳–进液 {a['R_lo']:.4f}–{a['R_hi']:.4f} °C/W</td></tr>
<tr><td>3D CAD</td><td>一维几何 D0.50、Sx3.0、Sy2.4 的单孔胞和三件冷板，见 CAD 页</td></tr>
<tr><td>单孔 CFD</td><td>m425，4,259,680 HEXA，iter 380 收敛，压降 {cfd['dp']:.1f} Pa，TIM 底 {cfd['t_tim']:.2f} K</td></tr>
<tr><td>仿真分析</td><td>CFD 壳侧热阻 {cfd['r_tim']:.4f} °C/W，落在一维区间附近，Martin 不适用</td></tr>
<tr><td>结构工艺装配</td><td>3 bar 板条校核、紫铜工艺路线、三件装配顺序</td></tr>
</table>
<p>孔径还没有收成一个数：<code>model.py</code> 的 GEO 是 D=0.50 mm，已收敛网格是 D=0.40 mm。两页报告都按这个差别写，没有把其中一个改成另一个。</p>
"""), encoding="utf-8")

    (CYCLE / "01_一维设计.html").write_text(page("1 · 一维设计", f"""
<p>计算书由 <code>make_cycle.py</code> 调用 <code>model.solve</code> 生成。几何冻结在 model.py：板 {g['plate_L']:.0f}×{g['plate_W']:.0f}×{g['plate_T']:.1f} mm，
每 die {g['n_jet_x']}×{g['n_jet_y']}，两 die 共 {M.N_JET} 孔，D={g['D_jet']:.2f} mm，Sx={g['S_jet_x']:.1f}，Sy={g['S_jet_y']:.1f}，H={g['H_jet']:.1f}。</p>
<img src="out/fig_layout.png" alt="俯视">
<img src="out/fig_stack.png" alt="厚度栈">
<h2>设计点</h2>
<table>
<tr><th></th><th>DP-A 保证点</th><th>DP-B 包络</th></tr>
<tr><td>功率 / 流量 / 进液</td><td>{a['P']:.0f} W · {a['Q']:.1f} L/min · {a['Tin']:.0f} °C</td><td>{b['P']:.0f} W · {b['Q']:.1f} L/min · {b['Tin']:.0f} °C</td></tr>
<tr><td>die / HBM / 其他</td><td>{a['p_die']:.1f} W×2 · {a['p_hbm']:.2f} W×8 · {a['p_other']:.1f} W</td><td>{b['p_die']:.1f} W×2 · {b['p_hbm']:.2f} W×8 · {b['p_other']:.1f} W</td></tr>
<tr><td>混合温升</td><td>{a['dTf']:.2f} K</td><td>{b['dTf']:.2f} K</td></tr>
<tr><td>孔速 / Re / 孔口压降（D=0.50）</td><td>{a['jet']['V']:.3f} m/s · {a['jet']['Re']:.0f} · {a['jet']['dP']/1000:.2f} kPa</td><td>{b['jet']['V']:.3f} m/s · {b['jet']['Re']:.0f} · {b['jet']['dP']/1000:.2f} kPa</td></tr>
<tr><td>同一流量若孔径改为 0.40</td><td>{a['jet_d040']['V']:.3f} m/s · Re {a['jet_d040']['Re']:.0f}</td><td>{b['jet_d040']['V']:.3f} m/s · Re {b['jet_d040']['Re']:.0f}</td></tr>
<tr><td>壳–进液热阻</td><td>{a['R_lo']:.4f}–{a['R_hi']:.4f} °C/W</td><td>{b['R_lo']:.4f}–{b['R_hi']:.4f} °C/W</td></tr>
<tr><td>和目标比</td><td>下限 {a['R_lo']:.4f}，上限 {a['R_hi']:.4f}，目标 {a['target']}</td><td>下限 {b['R_lo']:.4f}，上限 {b['R_hi']:.4f}，目标 {b['target']}</td></tr>
<tr><td>板内压降区间</td><td>{a['dp_total'][0]/1000:.2f}–{a['dp_total'][1]/1000:.2f} kPa</td><td>{b['dp_total'][0]/1000:.2f}–{b['dp_total'][1]/1000:.2f} kPa</td></tr>
<tr><td>HBM 槽速</td><td>{a['hbm_V']:.3f} m/s</td><td>{b['hbm_V']:.3f} m/s</td></tr>
</table>
<p>Re 低于 2000，Martin 阵列式在 DP-A 上{'采用' if a['martin'] else '不采用'}。热阻上限来自短槽肋模型加 TIM2 = 0.008 °C/W。DP-A 施加到单孔 CFD 的热流是名义胞热流的 1.05 倍：{a['q_bc']:.3f} W/cm²（{a['q_bc_si']:.0f} W/m²），流量不乘这 5%。</p>
<img src="out/fig_r.png" alt="热阻">
<h2>几何校核</h2>
<table><tr><th>项</th><th>式</th><th>计算</th><th>预期</th></tr>{check_rows}</table>
<p>Y 向射流覆盖比 die 高 0.8 mm，两侧各约 0.4 mm，孔本身仍落在 die 投影内。这是 model.py 写明的外包络，不是尺寸链错误。</p>
"""), encoding="utf-8")

    (CYCLE / "02_三维CAD.html").write_text(page("2 · 三维 CAD", f"""
<p>参数化内核 <code>cad/coldplate</code> 只有一个节距，建不出 Sx=3.0、Sy=2.4。这一轮的实体由 <code>build_cad.py</code> 按 model.py 直接生成，不改冻结的 v1.0 yaml（128 孔、节距 3.0）。</p>
<img src="out/fig_cell.png" alt="单孔胞">
<h2>零件</h2>
<table>
<tr><th>零件</th><th>内容</th></tr>
<tr><td>底板</td><td>本体 95×75×3.5 mm，余铜 2.0。导出的 STEP 含隔离肋，包围盒高度因此是 5.5 mm。每 die 短槽沿 Y 共 {M.N_CH_DIE} 条、宽 0.40、深 1.5、节距 0.80，沿 X 分成 4 段。两侧 HBM 各 8 条 0.60 mm 平槽。</td></tr>
<tr><td>喷嘴板</td><td>厚 2.5 mm。216 个 D0.50 直孔。不打抽吸孔，一维模型没有这个直径。</td></tr>
<tr><td>钎缝框</td><td>周边 0.5 mm，把外形收到 8.5 mm。</td></tr>
<tr><td>单孔胞</td><td>3.0×2.4 mm。一版 D0.50，对应一维；一版 D0.40，对应已收敛网格的孔径。</td></tr>
</table>
<h2>文件</h2>
{cad_files()}
<p>STEP 回读核对：总装包围盒 95.000 × 75.000 × 8.500 mm，体积 41848 mm³。喷嘴板比同外形实心板少约 106 mm³，与 216 个 D0.50、深 2.5 mm 的孔体积一致。两个单孔胞装配高度都是 8.0 mm（不含 0.5 mm 钎缝）。</p>
<p>装配顺序在结构页。OCC 若段错误，脚本会重试；冻结 yaml 和 <code>cad/out</code> 不写入。</p>
"""), encoding="utf-8")

    (CYCLE / "03_单孔CFD仿真分析.html").write_text(page("3 · 单孔 CFD 仿真分析", f"""
<p>对象是一个射流胞，不是 95×75 整板。设计点边界与一维 DP-A 的 216 孔分配一致：GPU 1.60 L/min，单孔质量流 {cfd['mdot']:.6e} kg/s，壁面热流 {cfd['q']:.0f} W/m²，入口 313.15 K。网格孔径是 <strong>D=0.40 mm</strong> 圆孔，胞 2.4×3.0 mm。</p>
<div class="note">主场 <code>{cfd['source']}</code>，iter {cfd['iter']}，转录写明 solution is converged。更粗的 bc216（{cfd['bc216_cells']:,} HEXA，iter {cfd['bc216_iter']}）压降 {cfd['bc216_dp']:.1f} Pa、TIM 底 {cfd['bc216_t']:.2f} K，用来看网格变化，不另作一个设计点。</div>
<h2>m425 面平均</h2>
<table>
<tr><th>量</th><th>值</th></tr>
<tr><td>网格</td><td>{cfd['cells']:,} HEXA，底壁边界层首层 2.5 μm</td></tr>
<tr><td>入口 / 出口温度</td><td>{cfd['t_in']:.2f} K / {cfd['t_out']:.2f} K</td></tr>
<tr><td>TIM 底 / 铜–水 / TIM–铜</td><td>{cfd['t_tim']:.3f} K / {cfd['t_cu']:.3f} K / 336.130 K</td></tr>
<tr><td>热流回读</td><td>{cfd['q']:.0f} W/m²</td></tr>
<tr><td>静压降</td><td>{cfd['dp']:.2f} Pa（出口表压 0）</td></tr>
<tr><td>两 die 加热</td><td>{cfd['p_2die']:.2f} W（单胞 {cfd['p_cell']:.4f} W × 216）</td></tr>
<tr><td>孔速 / Re_D</td><td>{cfd['vel']:.3f} m/s · {cfd['re']:.0f}</td></tr>
<tr><td>R(T_TIM−T_in)</td><td>{cfd['r_tim']:.5f} °C/W</td></tr>
<tr><td>R_conv(T_铜水−T_in)</td><td>{cfd['r_conv']:.5f} °C/W</td></tr>
</table>
<img src="out/fig_r.png" alt="热阻对比">
<h2>和一维怎么并读</h2>
<table>
<tr><th></th><th>一维 DP-A，GEO D=0.50</th><th>CFD 单孔，网格 D=0.40</th></tr>
<tr><td>孔速 / Re</td><td>{a['jet']['V']:.3f} m/s · {a['jet']['Re']:.0f}</td><td>{cfd['vel']:.3f} m/s · {cfd['re']:.0f}</td></tr>
<tr><td>壳–进液</td><td>{a['R_lo']:.4f}–{a['R_hi']:.4f} °C/W</td><td>{cfd['r_tim']:.4f} °C/W（含 TIM 与铜，不含封装）</td></tr>
<tr><td>对流热阻</td><td>短槽模型 {a['con_R']:.4f} °C/W</td><td>{cfd['r_conv']:.4f} °C/W</td></tr>
<tr><td>孔口压降</td><td>一维局部阻力 {a['dp_orifice']/1000:.2f} kPa</td><td>胞内静压降 {cfd['dp']/1000:.3f} kPa</td></tr>
</table>
<p>CFD 壳侧 {cfd['r_tim']:.4f} °C/W 落在一维下限 {a['R_lo']:.4f} 与上限 {a['R_hi']:.4f} 之间，靠近下限。Re≈{cfd['re']:.0f}，仍低于 Martin 1977 的 2000，不用阵列关联式外推整板。胞压降远小于 20 kPa 的板内上限，但它不含歧管和 216 孔分配不均。</p>
<p>能量闭合、y+ 和整板模型这一页没有新数字。12 层网格续算仍在进行，不写入本结论。</p>
"""), encoding="utf-8")

    (CYCLE / "04_结构工艺装配.html").write_text(page("4 · 三维结构、工艺与装配", f"""
<p>结构分析用 model.mech_checks：3 bar 表压下的两端固支板条，退火铜屈服取 70 MPa，弹性模量 110 GPa。这是送样前的解析筛选，不是 Mechanical 全场应力。</p>
<img src="out/fig_stack.png" alt="厚度栈">
<h2>承压</h2>
<table>
<tr><th>板条</th><th>应力 / MPa</th><th>挠度 / μm</th><th>屈服安全系数</th></tr>
{mech_rows}
</table>
<p>估算铜质量约 {mech['mass']*1000:.0f} g（包络体积填充率 {mech['fill']:.0%}，密度 8900 kg/m³）。盖板跨射流阵的跨距取阵面较大边，偏保守。</p>
<h2>工艺</h2>
<table>
<tr><th>零件</th><th>路线</th></tr>
<tr><td>底板</td><td>紫铜 C11000 / TU1。余铜和外形 CNC。GPU 槽以铲齿或铣槽，深宽比 1.5/0.40 = 3.75，低于倒齿上限 5。齿壁 0.40 mm。</td></tr>
<tr><td>喷嘴板</td><td>机械微钻 D0.50，高于 0.30 mm 下限。系统过滤按最小孔径的 1/10，即不粗于 50 μm；现参数集写的是 25 μm。</td></tr>
<tr><td>钎缝</td><td>量产真空钎焊。焊前设阻流，焊后精铣接触面。平面度目标 0.05 mm，接触面 Ra 0.8 μm。</td></tr>
<tr><td>送样</td><td>螺接加密封圈，便于拆开看流道。内部隔肋贴合要单独做分区流阻，只测整板压降看不出内部短路。</td></tr>
</table>
<p>激光焊或摩擦焊只能封外圈，封不到隔离肋，不能单独作为密封方案。整板金属打印不是出货路线。</p>
<h2>装配</h2>
<table>
<tr><th>顺序</th><th>Z / mm</th><th>件</th></tr>
<tr><td>1</td><td>0–3.5</td><td>底板，芯片面在 z=0</td></tr>
<tr><td>2</td><td>3.5–5.5</td><td>喷距空腔。隔离肋在此高度把 GPU 横流隔开，并填到喷嘴板</td></tr>
<tr><td>3</td><td>5.5–8.0</td><td>喷嘴板。216 孔对准两颗 die</td></tr>
<tr><td>4</td><td>8.0–8.5</td><td>周边钎缝框</td></tr>
</table>
<p>总装目标包围盒 95 × 75 × 8.5 mm。水嘴、UQD 和盖板静压箱不在这套实体里，装机前要另做接口。芯片朝下时，进液边朝托盘后面板；四块 GPU 冷板的串并联仍等水力 ICD。</p>
<p>和实测 asm_0921（12.5 mm 三层、128×D0.50、带静压箱）不是同一套结构。asm_0921 继续只作结构证据，不覆盖本轮一维几何。</p>
"""), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    data = {"DP-A": pack("DP-A"), "DP-B": pack("DP-B")}
    cfd = cfd_point()
    mech = M.mech_checks()
    checks = [(n, e, float(g), float(x)) for n, e, g, x in M.geometry_checks()]
    payload = {"design": data, "cfd": cfd, "geo": {k: M.GEO[k] for k in (
        "D_jet", "S_jet_x", "S_jet_y", "H_jet", "n_jet_x", "n_jet_y", "plate_L", "plate_W", "plate_T"
    )}, "n_jet": M.N_JET}
    (OUT / "cycle.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, default=_num), encoding="utf-8")
    draw(data, cfd)
    write_html(data, cfd, mech, checks)
    print("wrote", CYCLE)


if __name__ == "__main__":
    main()
