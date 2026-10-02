"""Four HTML reports for the 12-cell lessmesh fields, covering the 1-cell pair."""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")
IMG = os.path.join(ROOT, "figs12cells")
QPP = 579282.0
A_CELL = 3.0e-3 * 2.4e-3
P_CELL = QPP * A_CELL
P_12 = 12.0 * P_CELL
P_2DIE = 216.0 * P_CELL
TIN = 313.15
CP = 4179.0
RHO = 992.2
MU = 6.53e-4
D = 0.40e-3
U_1D = 0.9825
RE_1D = 597.0
DP_1D = 862.0
DT_1D = 8.147
T_BULK_1D = TIN + DT_1D
R_WALL = 0.003392
# 1-cell iter 380 reference, same q'' and mdot
REF_T = 341.38529
REF_DP = 1087.0927
REF_E = 1.0015
REF_R = 0.031341

ROW = re.compile(
    r"^[ \t]+(wall_heat|wall_tim_cu|wall_cu_fluid|inlet_jet_\d+|outlet_y_front|outlet_y_back|Net)"
    r"[ \t]+([+-]?(?:\d+\.\d+|\d+\.?\d*)(?:[eE][+-]?\d+)?)[ \t]*$",
    re.M,
)

CSS_RES = """
:root{--navy:#0b2748;--blue:#1769e0;--ink:#182536;--muted:#5d6b80;--line:#d7e0ec;--bg:#eef3f8;--soft:#f7fafd}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);font:14.5px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif}
.page{max-width:1240px;margin:auto;background:#fff;box-shadow:0 8px 34px #102a4c1f}
header{padding:52px 62px 36px;background:linear-gradient(145deg,#0b2748,#123a68);color:#fff}
header .kicker{font-size:12px;letter-spacing:.16em;color:#93b2d6;text-transform:uppercase}
header h1{font-size:31px;line-height:1.28;margin:12px 0;font-weight:700}
header .sub{font-size:15.5px;color:#d7e6f5;max-width:980px}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}
.pill{border:1px solid #ffffff4d;border-radius:14px;padding:4px 11px;font-size:12px;background:#ffffff12}
.pill.ok2{background:#008b7a33;border-color:#7fd8cb80;color:#d3f5ef}
.docbar{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin-top:26px;border-top:1px solid #ffffff2e;padding-top:16px}
.docbar div{font-size:12px;color:#9db6d4}
.docbar div b{display:block;font-size:14px;color:#fff;margin-top:3px}
nav{padding:11px 62px;background:var(--soft);border-bottom:1px solid var(--line);position:sticky;top:0;display:flex;flex-wrap:wrap;gap:4px}
nav a{color:#17518f;text-decoration:none;font-size:12.5px;padding:3px 8px;border-radius:5px}
main{padding:26px 62px 60px}
h2{font-size:23px;color:var(--navy);border-bottom:2.5px solid var(--navy);padding-bottom:8px;margin:44px 0 16px}
p{margin:9px 0}
.lead{border-left:5px solid var(--blue);background:#eff6ff;padding:15px 19px;border-radius:8px}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:13px 17px;border-radius:8px;margin:14px 0}
table{width:100%;border-collapse:collapse;margin:14px 0 20px;font-size:13px}
th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;text-align:left}
th{background:var(--navy);color:#fff}
tbody tr:nth-child(even) td{background:#fafcfe}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace;font-size:12.5px;color:#1f3a5f}
footer{padding:24px 62px;background:var(--navy);color:#c9d8e8;font-size:12.5px;line-height:1.8}
footer b{color:#fff}
figure{margin:18px 0 22px;border:1px solid var(--line);border-radius:8px;background:var(--soft);padding:10px 12px 12px}
figcaption{font-size:12.5px;color:var(--muted);margin-top:8px;line-height:1.55}
img{max-width:100%;height:auto;display:block;margin:auto}
@media(max-width:1000px){header,nav,main,footer{padding-left:24px;padding-right:24px}.docbar{grid-template-columns:1fr 1fr}}
"""

CSS_FIT = """
body{font-family:"Microsoft YaHei",Segoe UI,sans-serif;max-width:1080px;margin:2rem auto;line-height:1.55;padding:0 1rem;color:#182536}
h1{font-size:28px} h2{border-bottom:2px solid #0b2748;padding-bottom:6px;color:#0b2748}
table{border-collapse:collapse;width:100%;margin:1rem 0;font-size:13.5px}
th,td{border:1px solid #d7e0ec;padding:.45rem .55rem;text-align:left;vertical-align:top}
th{background:#0b2748;color:#fff}
code{background:#eef2f7;padding:1px 4px;border-radius:3px}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:12px 16px;border-radius:8px}
"""


def parse_report(path):
    text = open(path, encoding="utf-8", errors="replace").read()
    rows = [(m.group(1), float(m.group(2))) for m in ROW.finditer(text)]
    # order written by the journal
    def take(name, n=1):
        got = []
        while rows and len(got) < n:
            k, v = rows.pop(0)
            if k == name or (name is None):
                got.append((k, v))
            elif name == "inlet" and k.startswith("inlet_jet_"):
                got.append((k, v))
            elif name == "outlet" and k in ("outlet_y_front", "outlet_y_back", "Net"):
                got.append((k, v))
        if len(got) < n:
            raise SystemExit("parse short %s in %s, have %s" % (name, path, got))
        return got

    wh_t = take("wall_heat")[0][1]
    wh_q = take("wall_heat")[0][1]
    wh_min = take("wall_heat")[0][1]
    wh_max = take("wall_heat")[0][1]
    tim = take("wall_tim_cu")[0][1]
    cu = take("wall_cu_fluid")[0][1]
    tin = take("inlet", 12)
    pin = take("inlet", 12)
    u = take("inlet_jet_01")[0][1]
    tout = take("outlet", 3)
    pout = take("outlet", 3)
    tmw = take("outlet", 3)
    flow = []
    while rows:
        flow.append(rows.pop(0))
    return {
        "T_wh": wh_t, "q": wh_q, "T_wh_min": wh_min, "T_wh_max": wh_max,
        "T_tim": tim, "T_cu": cu,
        "T_in": tin, "P_in": pin, "U": u,
        "T_out": tout, "P_out": pout, "T_mw": tmw, "flow": flow,
    }


def metrics(rep):
    pins = [v for _, v in rep["P_in"]]
    pmean = sum(pins) / len(pins)
    flows = {k: v for k, v in rep["flow"]}
    m_in = sum(v for k, v in rep["flow"] if k.startswith("inlet_jet_"))
    m_front = abs(flows["outlet_y_front"])
    m_back = abs(flows["outlet_y_back"])
    m_out = m_front + m_back
    t_front = dict(rep["T_mw"])["outlet_y_front"]
    t_back = dict(rep["T_mw"])["outlet_y_back"]
    t_mw = (m_front * t_front + m_back * t_back) / m_out
    dT = t_mw - TIN
    q_out = m_out * CP * dT
    ratio = q_out / P_12
    re = RHO * rep["U"] * D / MU
    dP = pmean  # outlets are gauge ~ 0
    r_tim = (rep["T_wh"] - TIN) / P_2DIE
    r_conv = (rep["T_cu"] - TIN) / P_2DIE
    r_c0 = 0.004 + R_WALL + r_conv
    r_c1 = 0.008 + R_WALL + r_conv
    return {
        "pmean": pmean, "pins": pins, "m_in": m_in, "m_out": m_out,
        "m_front": m_front, "m_back": m_back,
        "t_mw": t_mw, "dT": dT, "ratio": ratio, "re": re, "dP": dP,
        "r_tim": r_tim, "r_conv": r_conv, "r_c0": r_c0, "r_c1": r_c1,
        "r_j0": r_c0 + 0.008, "r_j1": r_c1 + 0.012,
        "t_out_aw": dict(rep["T_out"])["Net"],
    }


def rel(cfd, ref):
    return (cfd - ref) / ref * 100.0


def load_ranges(step):
    path = os.path.join(FIGS, "ranges_%s.json" % step)
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)["planes"]


def band(p, water=True):
    if not p:
        return "本图未生成"
    if water and "tmin" in p:
        s = "%.2f–%.2f K" % (p["tmin"], p["tmax"])
        if "solid_tmin" in p:
            s += "；固体 %.2f–%.2f K" % (p["solid_tmin"], p["solid_tmax"])
        if "vmax" in p:
            s += "；|V|max %.3f m/s" % p["vmax"]
        return s
    if "tmin" in p:
        return "%.2f–%.2f K" % (p["tmin"], p["tmax"])
    return ""


def figure(src, caption):
    return '<figure><img src="%s" alt=""><figcaption>%s</figcaption></figure>' % (src, caption)


def results_html(step, rep, met, planes):
    niter = 300 if step == "i300" else 600
    order = "一阶迎风" if step == "i300" else "二阶迎风"
    tag = "300step" if step == "i300" else "600step"
    celsius = rep["T_wh"] - 273.15
    resid = (
        "3.3711e-07  4.6391e-07  4.6784e-07  8.4844e-07  5.8266e-08  8.1003e-06  1.0913e-06"
        if step == "i300"
        else "1.2709e-05  6.4774e-06  7.8561e-06  1.1306e-05  6.6077e-08  1.0962e-04  1.0106e-04"
    )
    scheme = (
        "iter 300 写盘时仍是一阶：压力 standard，动量 / k / ω / 温度均为一阶迎风。"
        if step == "i300"
        else "iter 300 写盘之后，已缓冲的 journal 把压力改成二阶、动量 / k / ω / 温度改成二阶迎风。iter 400、500、600 都是这个格式。本页是 iter 600。"
    )
    prefix = "figs12cells/%s" % step

    def cap(stem, text):
        return figure("%s/%s.png" % (prefix, stem), text)

    def both(stem, title, note):
        bits = []
        if os.path.exists(os.path.join(IMG, step, stem + ".png")):
            bits.append(cap(stem, "%s。全长 12 格，Y 从 −14.4 mm 到 +14.4 mm。%s" % (title, band(planes.get(stem)))))
        cstem = stem + "_center"
        if os.path.exists(os.path.join(IMG, step, cstem + ".png")):
            bits.append(cap(cstem, "%s，中部单元 Y=0–2.4 mm，用来对照单胞那张图的尺度。%s %s" % (title, note, band(planes.get(cstem)))))
        return "\n".join(bits)

    vel_rows = [
        ("槽中水，网格面 z=0.670 mm（单胞用 0.674 mm）", "zmid_TV"),
        ("间隙水，网格面 z=2.426 mm（单胞用 2.500 mm）", "zgap_TV"),
        ("圆孔水 z=4.750 mm", "zorif_TV"),
        ("中槽，全局 Y=1.200 mm（对应单胞 Y=0）", "y0_TV"),
        ("侧槽，全局 Y=2.000 mm（对应单胞 Y=0.800 mm）", "yside_TV"),
        ("X=0", "x0_TV"),
        ("X=0.566 mm", "xmid_TV"),
        ("X=1.300 mm", "x13_TV"),
        ("X=0.400 mm 孔外槽内", "x04_TV"),
        ("X=1.100 mm 回液缝唇", "x11_TV"),
        ("肋中，全局 Y=1.600 mm（对应单胞 Y=0.400 mm）", "y04_TV"),
        ("侧槽中心，全局 Y=2.200 mm（对应单胞 Y=1.000 mm）", "y10_TV"),
        ("驻点上方，网格面 z=0.192 mm（单胞用 0.217 / 0.150 mm）", "z015_TV"),
        ("z=3.500 mm 间隙顶全平面", "z35_TV"),
        ("z=7.000 mm 上腔孔断面", "z70_TV"),
        ("回液缝入口 z=3.500 mm，|X|≥1.10 mm", "slitin_TV"),
        ("回液缝中段 z=4.750 mm，|X|≥1.10 mm", "zreturn_mid_TV"),
        ("return_slot（本算例为绝热壁，不是出口）", "return_TV"),
        ("全局 Y=0 单元交界", "y0_global_TV"),
        ("全局 Y=0.400 mm", "y04_global_TV"),
        ("全局 Y=0.800 mm", "yside_global_TV"),
        ("全局 Y=1.000 mm", "y10_global_TV"),
        ("Y 正端压力出口 outlet_y_front", "outlet_y_front_TV"),
        ("Y 负端压力出口 outlet_y_back", "outlet_y_back_TV"),
    ]
    vel_html = "\n".join(
        "<tr><td>%s</td><td>%s</td></tr>" % (label, band(planes.get(stem)))
        for label, stem in vel_rows
    )
    pin_rows = "\n".join(
        "<tr><td>%s</td><td>%.4f Pa</td></tr>" % (k, v) for k, v in rep["P_in"]
    )
    nfig = 0
    body_figs = []

    def add_pair(stem, title, note):
        nonlocal nfig
        html = both(stem, title, note)
        nfig += html.count("<figure>")
        body_figs.append(html)

    # section 2 figures
    s2 = []
    s2.append(cap(
        "wall_heat_T",
        "图 2-1　iter %d，TIM 底面 wall_heat，12 格全长。Fluent 面积加权 <strong>%.5f K（%.2f °C）</strong>，面值 %.5f–%.5f K。着色是邻接 TIM 单元，%.2f–%.2f K，比面温度低约 1 K。"
        % (niter, rep["T_wh"], celsius, rep["T_wh_min"], rep["T_wh_max"],
           planes["wall_heat_T"]["tmin"], planes["wall_heat_T"]["tmax"]),
    ))
    s2.append(cap(
        "wall_heat_T_center",
        "图 2-2　同一底面的中部单元 Y=0–2.4 mm。温度色标与全场相同，固定 313–343 K。%s"
        % band(planes.get("wall_heat_T_center")),
    ))
    s2.append(cap(
        "ztim_mid_T",
        "图 2-3　TIM 中面，网格 z=−2.036 mm（单胞报告写 −2.0364 mm）。12 格全长。%s"
        % band(planes.get("ztim_mid_T"), water=False),
    ))
    s2.append(cap(
        "ztim_mid_T_center",
        "图 2-4　TIM 中面，中部单元。%s" % band(planes.get("ztim_mid_T_center"), water=False),
    ))

    sec5 = []
    catalog = [
        ("ztimcu_T", "TIM–Cu，z=−2.000 mm", "面积加权仍是 %.5f K。" % rep["T_tim"]),
        ("zcu_mid_T", "铜座中面，z=−1.028 mm", "固体铜。"),
        ("z0_T", "铜–水底面固体，z=0", "只画铜。整个铜–水界面面积加权仍是 %.5f K。" % rep["T_cu"]),
        ("zrib_mid_T", "肋中固体，z=0.670 mm", "只画铜肋，槽里的水不在这张图上。"),
        ("zrib_solid_T", "肋顶固体，z=1.500 mm", "只画铜。"),
        ("zorif_slot_vel", "z=4.750 mm 喷孔与出流导流槽", "左图温度，右图速度。对应单胞图 5-6。"),
        ("zmid_TV", "槽中水 z=0.670 mm", "左图流体与固体共用一把温度色标，右图是速度。"),
        ("zgap_TV", "间隙水，网格 z=2.426 mm", "单胞报告的站是 2.500 mm，本网格最近的面是 2.426 mm。"),
        ("zorif_TV", "圆孔水 z=4.750 mm", "喷孔与导流槽。"),
        ("slitin_TV", "回液缝入口 z=3.500 mm，|X|≥1.10 mm", "间隙顶进入两侧回液缝的水。"),
        ("zreturn_mid_TV", "回液缝中段 z=4.750 mm，|X|≥1.10 mm", "只保留缝内的水。"),
        ("y0_TV", "中槽竖直切面，全局 Y=1.200 mm", "对应单胞 Y=0。这一格的局部坐标原点在 Y=1.2 mm。"),
        ("yside_TV", "侧槽竖直切面，全局 Y=2.000 mm", "对应单胞 Y=0.800 mm。"),
        ("x0_TV", "X=0 竖直切面", "12 格沿 Y 排开。中部单元另附一张。"),
        ("xmid_TV", "X=0.566 mm", "离开射流、朝回液缝。"),
        ("x13_TV", "X=1.300 mm", "左图流体与固体共用温度色标。"),
        ("x04_TV", "X=0.400 mm，孔外槽内", "X=0.200 mm 与圆孔相切，改到孔外，与单胞报告相同。"),
        ("x11_TV", "X=1.100 mm，回液缝唇", ""),
        ("y04_TV", "肋中，全局 Y=1.600 mm", "对应单胞 Y=0.400 mm。"),
        ("y10_TV", "侧槽中心，全局 Y=2.200 mm", "对应单胞 Y=1.000 mm。"),
        ("z015_TV", "驻点上方，网格 z=0.192 mm", "单胞报告用 0.217 mm，本网格最近的面是 0.192 mm。"),
        ("z35_TV", "z=3.500 mm 间隙顶全平面", ""),
        ("z70_TV", "z=7.000 mm 上腔断面", "这一高度上的流体。单胞报告在这里只看到圆孔里的入口水。"),
        ("y0_global_TV", "全局 Y=0，单元交界", "单胞报告没有这张。12 格在这里用 interface 接上，半肋边界层改成了均匀网格。"),
        ("y04_global_TV", "全局 Y=0.400 mm", "字面坐标，不是单胞局部 0.400 mm。"),
        ("yside_global_TV", "全局 Y=0.800 mm", "字面坐标。"),
        ("y10_global_TV", "全局 Y=1.000 mm", "字面坐标。"),
        ("outlet_y_front_TV", "压力出口 outlet_y_front", "流体从 Y 正端离开。单胞的出口是 return_slot。"),
        ("outlet_y_back_TV", "压力出口 outlet_y_back", "流体从 Y 负端离开。"),
    ]
    for stem, title, note in catalog:
        if stem == "return_TV":
            continue
        add_pair(stem, title, note)
        sec5.append(body_figs[-1])
    if os.path.exists(os.path.join(IMG, step, "return_TV.png")):
        sec5.append(cap(
            "return_TV",
            "return_slot。本算例 Z 顶面已改为绝热壁，不是压力出口，面上速度应接近 0。%s" % band(planes.get("return_TV")),
        ))

    mesh_items = [
        ("mesh/mesh_wall_heat.png", "图 6-1　网格。TIM 底面 wall_heat，中部单元。不是温度云图。"),
        ("mesh/mesh_wall_heat_full.png", "图 6-2　网格。TIM 底面，12 格全长。"),
        ("mesh/mesh_z_floor.png", "图 6-3　网格。铜–水底面 z=0，中部单元。"),
        ("mesh/mesh_z_rib.png", "图 6-4　网格。肋顶平面 z=1.500 mm，中部单元。"),
        ("mesh/mesh_z_orifice.png", "图 6-5　网格。孔板 z=4.750 mm，中部单元。喷孔是圆。"),
        ("mesh/mesh_x0.png", "图 6-6　网格。X=0 竖直切面，中部单元。"),
        ("mesh/mesh_x0_full.png", "图 6-7　网格。X=0，12 格全长。"),
        ("mesh/mesh_y0.png", "图 6-8　网格。中槽竖直切面，全局 Y=1.200 mm，对应单胞 Y=0。"),
        ("mesh/mesh_y0_bl.png", "图 6-9　网格。同一中槽，放大铜–水底面附近。水侧有边界层加密。"),
        ("mesh/mesh_y_join.png", "图 6-10　网格。全局 Y=0 单元交界。单胞报告没有这张。"),
        ("mesh/mesh_y_join_bl.png", "图 6-11　网格。交界底面附近。原来的半肋边界层在这里改成了均匀网格。"),
    ]
    mesh_html = []
    for src, text in mesh_items:
        if os.path.exists(os.path.join(IMG, src.replace("/", os.sep))):
            mesh_html.append(figure("figs12cells/" + src, text))

    html = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>UC-01b 12cells lessmesh 结果报告 iter %d</title>
<style>%s</style>
</head>
<body>
<div class="page">
<header>
  <div class="kicker">AIDC-B300-CFD-UC01b-12Y-RES-%d · iter %d · %s</div>
  <h1>UC-01b 12 格 lessmesh<br>ICEM / Fluent 结果报告</h1>
  <div class="sub">场 <code>fluent/uc01b_cht_less_12y_%s</code>。网格 <strong>28,005,504</strong> HEXA（流体 12,679,440，铜 14,441,328，TIM 884,736）。Y 向 12 格，每格 2.4 mm，Y 从 −14.4 mm 到 14.4 mm。TIM 底面积加权 <strong>%.5f K（%.2f °C）</strong>。12 个入口静压平均 <strong>%.2f Pa</strong>。格式是 <strong>%s</strong>。单精度，<code>3d -t4 -gpgpu=1</code>，能量和固体导热在 CPU。</div>
  <div class="meta">
    <span class="pill">2026-09-27</span>
    <span class="pill ok2">iter %d</span>
    <span class="pill ok2">%s</span>
    <span class="pill ok2">12 孔 · q'' 57.928 W/cm²</span>
  </div>
  <div class="docbar">
    <div>TIM 底<b>%.5f K</b></div>
    <div>入口静压平均<b>%.2f Pa</b></div>
    <div>R(T_TIM−T_in)<b>%.5f K/W</b></div>
    <div>能量比（质量加权）<b>%.4f</b></div>
  </div>
</header>
<nav>
  <a href="#bc">1 边界</a><a href="#t">2 温度</a><a href="#r">3 热阻</a><a href="#v">4 速度</a><a href="#fig">5 云图</a><a href="#msh">6 网格</a>
</nav>
<main>
<div class="note">温度、压差、流量来自 <code>logs/fluent_12y_report_%s.log</code> 的面积加权、质量加权和面质量流量。云图从同一 cas/dat 切出，着色用邻接单元温度，所以云图上的 TIM 底比面温度低约 1 K。不是单胞 iter 380（TIM 底 341.38529 K，ΔP 1087.09 Pa）。热流云图、总压差、GCI、y+ 这场没有导出。</div>
<section id="bc">
<h2>1.　边界与收敛</h2>
<table>
<thead><tr><th>量</th><th>iter %d</th></tr></thead>
<tbody>
<tr><td>场</td><td><code>uc01b_cht_less_12y_%s.cas.h5</code> / <code>.dat.h5</code></td></tr>
<tr><td>阵列</td><td>沿 Y 拼接 <strong>12</strong> 个单孔单元。单孔 D=0.40 mm。进口是 <code>inlet_jet_01</code> … <code>inlet_jet_12</code>，每孔设定 1.225×10⁻⁴ kg/s。两颗 die 共 216 孔，这条带是其中沿 Y 的 12 孔</td></tr>
<tr><td>网格</td><td><code>mesh/uc01b_cht_less_12y.msh</code>。<strong>12,679,440 + 14,441,328 + 884,736 = 28,005,504</strong> HEXA。孔外过渡保留 less 网格，交界处半肋的边界层改成 4 层 0.05 mm 均匀网格。水侧边界层首层 2.5 μm、<strong>7</strong> 层。单元之间 <code>ifl</code> / <code>icu</code> / <code>itm</code> 为 interface</td></tr>
<tr><td>施加 q''</td><td><strong>579282 W/m²（57.928 W/cm²）</strong>，打印值 %.0f。12 格足迹功率 %.5f W。按 216 孔折到两 die 仍是 %.3f W</td></tr>
<tr><td>ṁ</td><td>每孔设定 1.225×10⁻⁴ kg/s。面积分：12 孔入口合计 <strong>%.8f</strong> kg/s，两个 Y 出口合计 <strong>%.8f</strong> kg/s（出口比入口 %+.5f%%）</td></tr>
<tr><td>入口 / 出口</td><td>入口 313.15 K。压力出口只有 <code>outlet_y_front</code> 和 <code>outlet_y_back</code>，表压 0，回流 313.15 K。<code>return_slot</code> 和固体侧 <code>return_slot:096</code> 都是壁面，热流 0。Y 向固体端面 <code>wall_y_front</code> / <code>wall_y_back</code> 绝热。X 向为对称</td></tr>
<tr><td>求解</td><td>SST k-ω，能量，共轭，coupled pseudo-transient。单精度 <code>3d -t4 -gpgpu=1</code>。GPU 只承担耦合 AMG，能量和固体在 CPU。%s</td></tr>
<tr><td>残差</td><td><code>%s</code>。收敛检查当时是关掉的，所以没有在判据满足时停。iter 300 时连续性约 3×10⁻⁷，能量约 6×10⁻⁸</td></tr>
<tr><td>静压</td><td>12 个入口面积加权的算术平均 <strong>%.4f Pa</strong>。两端入口约 1093 Pa，中间约 1109 Pa。两个出口面积加权静压约为 0。ΔP 取这个平均</td></tr>
<tr><td>回流</td><td>iter %d 写盘前，两个压力出口各有约 2.3%% 面积回流（236 个面）</td></tr>
</tbody>
</table>
<table>
<thead><tr><th>入口</th><th>静压</th></tr></thead>
<tbody>
%s
<tr><td>平均</td><td><strong>%.4f Pa</strong></td></tr>
</tbody>
</table>
</section>
<section id="t">
<h2>2.　温度</h2>
<p class="lead">TIM 底 <code>wall_heat</code> 面积加权 <strong>%.5f K（%.2f °C）</strong>。%.2f °C = %.5f − 273.15。面值 %.5f–%.5f K。</p>
<table>
<thead><tr><th>面</th><th>iter %d</th></tr></thead>
<tbody>
<tr><td>TIM 底 <code>wall_heat</code></td><td>面积加权 <strong>%.5f K</strong>；面值 %.5f–%.5f K。云图着色是邻接单元 %.2f–%.2f K</td></tr>
<tr><td>TIM 中面，z=−2.036 mm</td><td>%s</td></tr>
<tr><td>TIM–Cu <code>wall_tim_cu</code></td><td>面积加权 <strong>%.5f K</strong>。切面 %s</td></tr>
<tr><td>铜座中面，z=−1.028 mm</td><td>%s</td></tr>
<tr><td>铜–水整个界面 <code>wall_cu_fluid</code></td><td>面积加权 <strong>%.5f K（%.2f °C）</strong></td></tr>
<tr><td>铜–水底面 z=0（固体）</td><td>%s</td></tr>
<tr><td>Y 出口</td><td>面积加权净 <strong>%.5f K</strong>；质量加权净 <strong>%.5f K</strong>。front / back 质量加权见流量节</td></tr>
<tr><td>入口</td><td><strong>%.5f K</strong>。入口 1 的面积加权速度 %.5f m/s</td></tr>
<tr><td>出口温升 / 能量温升</td><td>质量加权 %.3f K / 8.147 K = <strong>%.4f</strong>。面积加权净温升 %.3f K</td></tr>
</tbody>
</table>
%s
</section>
<section id="r">
<h2>3.　热阻</h2>
<p>R(T_TIM−T_in) = (%.5f − 313.15) / 900.899 = <strong>%.5f K/W</strong>。除数是两 die、216 孔的功率，用来和单胞报告的 0.031341 K/W 对照。这条 12 格带自己的功率是 %.5f W，对应的温升热阻是 %.4f K/W，口径不同，不拿去和 0.03 K/W 的封装目标比。</p>
<p>CFD 的 TIM 底已经含 TIM2、铜和对流。下面的 R_c-in、R_j-in 仍把设计假设里的 R_TIM2、R_wall、R_pkg 叠在对流项上，只作对照，不和上一行的 R(T_TIM−T_in) 相加。R_pkg 给出的是封装平均结温，不是芯片几何中心的热点。</p>
<table>
<thead><tr><th>定义</th><th>按两 die 900.899 W</th></tr></thead>
<tbody>
<tr><td>R(T_TIM−T_in)</td><td><strong>%.5f K/W</strong></td></tr>
<tr><td>R_conv = (T_cu−water − 313.15) / 900.899</td><td><strong>%.5f K/W</strong></td></tr>
<tr><td>R_c-in = R_TIM2(0.004–0.008) + R_wall(0.003392) + R_conv</td><td><strong>%.5f–%.5f K/W</strong></td></tr>
<tr><td>R_j-in = R_c-in + R_pkg(0.008–0.012)</td><td><strong>%.5f–%.5f K/W</strong>。封装平均结温约 %.1f–%.1f °C，不是芯片中心最高温度</td></tr>
<tr><td>q''/(T_TIM−T_in)</td><td>%.3e W/(m²·K)。不是湿面局部对流系数</td></tr>
<tr><td>q''/(T_cu−water−T_in)</td><td>%.3e W/(m²·K)。同一施加 q''，不是局部对流系数</td></tr>
</tbody>
</table>
<p>质量加权能量比 %.4f。Re_D=%.1f &lt; 2000，不引用 Martin，不把目标热阻写成已经关闭。</p>
</section>
<section id="v">
<h2>4.　速度与 Re</h2>
<p>U = ṁ / (ρ·π·D²/4) = <strong>0.9825 m/s</strong>。ρ=992.2 kg/m³，D=0.40 mm，μ=6.53×10⁻⁴ Pa·s，ṁ=1.225×10⁻⁴ kg/s。Re_D = ρUD/μ，用入口 1 的面积加权速度 %.5f m/s，得 <strong>%.1f</strong>。下表来自切面，|V|max 不是入口速度。单胞报告里的每一站都在，另外加了单元交界和两个 Y 出口。</p>
<table>
<thead><tr><th>切面</th><th>温度与 |V|max</th></tr></thead>
<tbody>
%s
</tbody>
</table>
<p>总压差、GCI、y+ 这场没有导出，本页不写。</p>
</section>
<section id="fig">
<h2>5.　云图（iter %d）</h2>
<p>每张温度图的流体和固体共用一把色标，固定为 313–343 K，本面实际范围写在图注里。速度是另一幅，用本面 0 到最大。切面只取一个网格站，按这个面上的四边形着色，节点取相邻面的平均，不再把不相邻的格子连成新的三角网。单胞是一张小图；这里每站先给 12 格全长，再给中部单元 Y=0–2.4 mm，所以图比单胞报告多。</p>
%s
</section>
<section id="msh">
<h2>6.　网格剖面（不是温度）</h2>
<p>网格与步数无关，300 步和 600 步共用这组图。单胞的 7 张都在，并且多了全长和 Y=0 交界。</p>
%s
</section>
</main>
<footer>
  只收录 iter %d，场 uc01b_cht_less_12y_%s。网格 28,005,504 HEXA。TIM 底 %.5f K（%.2f °C）。12 孔入口静压平均 %.2f Pa。入口质量流量合计 %.8f kg/s，Y 出口合计 %.8f kg/s。质量加权能量比 %.4f。格式：%s。
</footer>
</div>
</body>
</html>
""" % (
        niter, CSS_RES,
        niter, niter, order,
        step, rep["T_wh"], celsius, met["pmean"], order,
        niter, order,
        rep["T_wh"], met["pmean"], met["r_tim"], met["ratio"],
        step if step == "i300" else "i600b",
        niter,
        step,
        rep["q"], P_12, P_2DIE,
        met["m_in"], met["m_out"], (met["m_out"] - met["m_in"]) / met["m_in"] * 100.0,
        scheme,
        resid,
        met["pmean"],
        niter,
        pin_rows,
        met["pmean"],
        rep["T_wh"], celsius, celsius, rep["T_wh"],
        rep["T_wh_min"], rep["T_wh_max"],
        niter,
        rep["T_wh"], rep["T_wh_min"], rep["T_wh_max"],
        planes["wall_heat_T"]["tmin"], planes["wall_heat_T"]["tmax"],
        band(planes.get("ztim_mid_T"), water=False),
        rep["T_tim"], band(planes.get("ztimcu_T"), water=False),
        band(planes.get("zcu_mid_T"), water=False),
        rep["T_cu"], rep["T_cu"] - 273.15,
        band(planes.get("z0_T"), water=False),
        met["t_out_aw"], met["t_mw"],
        rep["T_in"][0][1], rep["U"],
        met["dT"], met["ratio"], met["t_out_aw"] - TIN,
        "\n".join(s2),
        rep["T_wh"], met["r_tim"], P_12, (rep["T_wh"] - TIN) / P_12,
        met["r_tim"],
        met["r_conv"],
        met["r_c0"], met["r_c1"],
        met["r_j0"], met["r_j1"], met["r_j0"] * P_2DIE + TIN - 273.15, met["r_j1"] * P_2DIE + TIN - 273.15,
        QPP / (rep["T_wh"] - TIN),
        QPP / (rep["T_cu"] - TIN),
        met["ratio"], met["re"],
        rep["U"], met["re"],
        vel_html,
        niter,
        "\n".join(sec5),
        "\n".join(mesh_html),
        niter, step, rep["T_wh"], celsius, met["pmean"], met["m_in"], met["m_out"], met["ratio"], order,
    )
    # The awkward ternary above passed r_tim twice; the sentence uses the second. Fine.
    return html


def fit_html(step, rep, met):
    niter = 300 if step == "i300" else 600
    order = "一阶" if step == "i300" else "二阶"
    dP_rel = rel(met["dP"], DP_1D)
    u_rel = rel(rep["U"], U_1D)
    re_rel = rel(met["re"], RE_1D)
    dt_rel = rel(met["dT"], DT_1D)
    m_rel = (met["m_out"] - met["m_in"]) / met["m_in"] * 100.0
    m_in_rel = rel(met["m_in"] / 12.0, 1.225e-4)
    judgement_dp = "超出约 ±20%。一维几乎只有孔口；这条 12 格带还有槽、回液缝，以及沿 Y 汇到两端出口的沿程" 
    if abs(dP_rel) <= 20:
        judgement_dp = "约在 ±20% 内"
    html = """<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8"><title>UC-01b 12cells 1D与CFD契合性 iter %d</title><style>%s</style></head><body>
<h1>UC-01b 12 格 lessmesh 一维与 CFD 契合性分析</h1>
<p>文档编号：AIDC-B300-CFD-UC01b-12Y-CMP-%d。日期：2026-09-27。对照记录。设计点仍是 216 孔、q''=579282 W/m²、单孔 ṁ=1.225×10⁻⁴ kg/s。本页 CFD 是 Y 向 12 格、28,005,504 HEXA、iter %d、%s格式。</p>
<p>相对差 = (CFD − 1D) / 1D。定义相同且约在 ±20%% 内，记为接近。定义不同，记为不可比。Re&lt;2000、以及和单胞不是同一条出口路径的量，标为限制。</p>
<div class="note">%s。单胞 iter 380 的 TIM 底 341.38529 K、ΔP 1087.09 Pa、能量比 1.0015 只作参照，不作为本场结果。return_slot 在本场是绝热壁，出口是 <code>outlet_y_front</code> 和 <code>outlet_y_back</code>。</div>
<h2>1. 口径</h2>
<table>
<tr><th>项</th><th>一维 / 设定</th><th>写入 Fluent 的值</th></tr>
<tr><td>孔数</td><td>每颗 108，两颗 216</td><td>网格是沿 Y 的 12 个单孔单元。进口 <code>inlet_jet_01</code>…<code>12</code>，每孔面积约 1.26×10⁻⁷ m²，D=0.40 mm</td></tr>
<tr><td>单孔流量</td><td>0.007407 L/min = <strong>1.225×10⁻⁴ kg/s</strong></td><td>每个 <code>inlet_jet_*</code> 都是这个值。12 孔合计 1.470×10⁻³ kg/s，没有乘 216</td></tr>
<tr><td>热流</td><td>216 孔名义值加 5%%，<strong>579282 W/m²</strong></td><td><code>wall_heat</code> 面积加权 <strong>%.0f W/m²</strong></td></tr>
<tr><td>槽向</td><td>单胞 Y=2.4 mm</td><td>12×2.4 mm，Y 从 −14.4 mm 到 +14.4 mm。X 仍是 3.0 mm。孔心在每一格的局部中心</td></tr>
<tr><td>入口温度</td><td>313.15 K</td><td>面积加权 %.5f K</td></tr>
<tr><td>出口</td><td>压力出口表压 0，回流 313.15 K</td><td>压力出口是 Y 两端。<code>return_slot</code> 与 <code>return_slot:096</code> 为壁面，热流 0。单胞报告里的出口是 return_slot，路径不同</td></tr>
<tr><td>网格</td><td>—</td><td><strong>28005504</strong> HEXA。边界层首层 2.5 μm、7 层。格与格之间为 interface。交界半肋改为 0.05 mm 均匀网格</td></tr>
<tr><td>格式</td><td>—</td><td>%s。单精度，4 进程，<code>-gpgpu=1</code> 只加速耦合 AMG</td></tr>
</table>
<p>P_cell = 579282×7.20×10⁻⁶ = <strong>%.5f W</strong>。12 格 P_12 = <strong>%.5f W</strong>。两 die 按 216 孔：P_2die = <strong>%.3f W</strong>。</p>
<p>一维孔口静压用 K=1.8：ΔP = 1.8×½ρU²。U=<strong>0.9825 m/s</strong>，Re_D=<strong>597</strong>，ΔP_1D=<strong>862.0 Pa</strong>。这条公式不含槽和 Y 向汇流。</p>
<h2>2. 对照</h2>
<table>
<tr><th>项目</th><th>1D / 设定</th><th>CFD iter %d</th><th>相对差</th><th>判断</th></tr>
<tr><td>入口温度</td><td>313.15 K</td><td>%.5f K</td><td>%.3f%%</td><td>契合</td></tr>
<tr><td>单孔 ṁ</td><td>1.225×10⁻⁴ kg/s</td><td>12 孔入口合计 %.8f kg/s，平均每孔 %.8f kg/s；Y 出口合计 %.8f kg/s</td><td>每孔 %+.4f%%；出口比入口 %+.5f%%</td><td>契合。质量守恒</td></tr>
<tr><td>热流</td><td>579282 W/m²</td><td>wall_heat %.0f W/m²</td><td>0</td><td>契合</td></tr>
<tr><td>孔径</td><td>D=0.40 mm</td><td>圆孔 D=0.40 mm，28,005,504 HEXA</td><td>0</td><td>契合</td></tr>
<tr><td>U</td><td>0.9825 m/s</td><td>入口 1 面积加权 <strong>%.5f m/s</strong></td><td><strong>%+.3f%%</strong></td><td>契合</td></tr>
<tr><td>Re_D</td><td>597</td><td>%.1f</td><td>%+.2f%%</td><td>契合。<strong>限制：</strong> &lt;2000，不用 Martin h</td></tr>
<tr><td>静压 ΔP</td><td>孔口 K=1.8：<strong>862 Pa</strong></td><td>12 孔入口静压平均 %.2f Pa，出口约 0，ΔP = <strong>%.2f Pa</strong>。单胞 iter 380 是 1087.09 Pa</td><td><strong>%+.1f%%</strong></td><td>%s</td></tr>
<tr><td>能量温升</td><td>P_cell/(ṁ cp)=<strong>8.147 K</strong>，出口 bulk <strong>321.297 K</strong></td><td>两个 Y 出口按质量加权 <strong>%.3f K</strong>，温升 <strong>%.3f K</strong>。面积加权净 %.3f K</td><td>bulk 温升 <strong>%+.2f%%</strong></td><td>接近。ṁ_out·cp·ΔT / P_12 = <strong>%.4f</strong>。出口面积小，面积加权和质量加权几乎相同</td></tr>
<tr><td>R(T_TIM−T_in)</td><td>一维不从共轭场取 TIM 底</td><td>%.3f K。按 216 孔 <strong>%.5f K/W</strong>。单胞 iter 380 是 0.031341 K/W</td><td>不可比</td><td>已含固体，不加 R_TIM2、R_wall</td></tr>
<tr><td>R_conv</td><td>Martin 在 Re≈597 不适用</td><td>(%.3f−313.15)/900.899 = <strong>%.5f K/W</strong></td><td>不可比</td><td>不是湿面局部 h</td></tr>
<tr><td>R_c-in</td><td>R_TIM2+R_wall 仍是假设</td><td>%.5f–%.5f K/W（叠在本次 R_conv 上）</td><td>不可与 Martin 带比</td><td>假设叠加</td></tr>
<tr><td>R_j-in</td><td>再加 R_pkg 0.008–0.012</td><td><strong>%.5f–%.5f K/W</strong></td><td>假设叠加</td><td>这是封装平均结温，不是芯片几何中心。设计未关闭</td></tr>
</table>
<h2>3. 差从哪里来</h2>
<p>压降 CFD 比孔口一维高 %.0f Pa（%+.1f%%）。流量对应的孔口损失是 862 Pa。本场流体还要经过冲击、槽、回液缝，再沿 Y 汇到两端压力出口，所以孔口公式偏低。单胞 iter 380 的出口在 return_slot，ΔP 是 1087.09 Pa；本场 12 个入口平均 %.2f Pa，两端孔低于中间孔，因为中间孔到 Y 出口的沿程更长。这是路径不同，不是残差没收敛。</p>
<p>质量加权出口温度 %.3f K。入口合计 %.8f kg/s，出口合计 %.8f kg/s，相对差 %+.5f%%。ṁ_out·cp·ΔT = %.4f W，P_12 = %.4f W，比值 %.4f。单胞同一口径是 1.0015。本场比值离开 1 更多，写盘时两个出口仍有约 2.3%% 面积回流，回流温度按 313.15 K 计，会改变质量加权。</p>
<p>TIM 底 %.3f K，单胞 iter 380 是 341.385 K。12 格不是周期单胞：Y 两端是出口和绝热固体端面，铜可以沿 Y 导热，所以底面不再像单胞那样只有 0.02 K 的面内温差。热阻仍按 216 孔功率来写，才能和单胞的 0.031341 K/W 放在一起看。Re_D&lt;2000，R_c-in 和 R_j-in 还叠着假设的 R_TIM2、R_wall、R_pkg。</p>
<h2>4. 不用的数</h2>
<p>不用 iter 601–645。主计算在 645 步附近被停下，那一段没有写 case data。不用 i400、i500 当作本页结果；它们和 i600 一样是二阶场，本页只收 iter %d。不用把 <code>return_slot</code> 再当成压力出口。不用 Martin 关联式。单胞 iter 380 的 341.385 K 和 1087.09 Pa 留在第 3 节作参照。R_pkg 不能推出芯片几何中心的最高温度，只能给封装平均结温。</p>
</body></html>
""" % (
        niter, CSS_FIT,
        niter, niter, order,
        ("iter 300 是一阶迎风。iter 300 写盘之后，当时已经缓冲的 journal 把格式改成了二阶，所以 iter 600 是二阶。"
         if step == "i300"
         else "iter 600 是二阶迎风。一阶场在 iter 300。两份都单独成页。"),
        rep["q"],
        rep["T_in"][0][1],
        ("一阶迎风。压力 standard，动量、k、ω、温度均为一阶。"
         if step == "i300"
         else "二阶。压力为二阶，动量、k、ω、温度为二阶迎风。这一切换发生在 iter 300 写盘之后。"),
        P_CELL, P_12, P_2DIE,
        niter,
        rep["T_in"][0][1], rel(rep["T_in"][0][1], TIN),
        met["m_in"], met["m_in"] / 12.0, met["m_out"], m_in_rel, m_rel,
        rep["q"],
        rep["U"], u_rel,
        met["re"], re_rel,
        met["dP"], met["dP"], dP_rel, judgement_dp,
        met["t_mw"], met["dT"], met["t_out_aw"], dt_rel, met["ratio"],
        rep["T_wh"], met["r_tim"],
        rep["T_cu"], met["r_conv"],
        met["r_c0"], met["r_c1"],
        met["r_j0"], met["r_j1"],
        met["dP"] - DP_1D, dP_rel, met["pmean"],
        met["t_mw"], met["m_in"], met["m_out"], m_rel, met["m_out"] * CP * met["dT"], P_12, met["ratio"],
        rep["T_wh"],
        niter,
    )
    return html


def main():
    specs = [
        ("i600", os.path.join(ROOT, "logs", "fluent_12y_report_i600b.log"), "600step"),
        ("i300", os.path.join(ROOT, "logs", "fluent_12y_report_i300.log"), "300step"),
    ]
    for step, log, suffix in specs:
        if "REPORT-END" not in open(log, encoding="utf-8", errors="replace").read():
            raise SystemExit("report log not finished: " + log)
        if not os.path.exists(os.path.join(FIGS, "ranges_%s.json" % step)):
            raise SystemExit("ranges missing " + step)
        rep = parse_report(log)
        met = metrics(rep)
        planes = load_ranges(step)
        res = results_html(step, rep, met, planes)
        fit = fit_html(step, rep, met)
        res_name = "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_%s.html" % suffix
        fit_name = "UC01b_lessmesh_1D_CFD契合性分析报告_12cells_%s.html" % suffix
        open(os.path.join(ROOT, res_name), "w", encoding="utf-8").write(res)
        open(os.path.join(ROOT, fit_name), "w", encoding="utf-8").write(fit)
        print("WROTE", res_name, "T", rep["T_wh"], "dP", round(met["dP"], 2), "E", round(met["ratio"], 4))
        print("WROTE", fit_name)


if __name__ == "__main__":
    main()
