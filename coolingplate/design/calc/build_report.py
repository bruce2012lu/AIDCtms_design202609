# -*- coding: utf-8 -*-
"""装配并输出设计报告 HTML。
用法: python build_report.py
"""
import os
import model as M
import report_a as RA
import report_b as RB

A = M.solve("DP-A")
B = M.solve("DP-B")
G = M.GEO

DOC_NO = "AIDC-B300-CP-HYB-002"
VER = "v2.0"
DATE = "2026-09-14"
MODEL = "CP-B300-JM-01"
OUT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    f"NVIDIA_B300_微通道冲击换热冷板设计报告_{VER}_20260914.html")

CSS = """
:root{
  --navy:#0b2748;--blue:#1769e0;--teal:#008b7a;--ink:#182536;
  --muted:#5d6b80;--line:#d7e0ec;--bg:#eef3f8;--soft:#f7fafd;
  --warn:#a65b00;--red:#b42318;--good:#1f7a4d;--cu:#b97a45;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:70px}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14.5px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
.page{max-width:1240px;margin:auto;background:#fff;
  box-shadow:0 8px 34px #102a4c1f}

/* ---------- 封面 ---------- */
header{padding:52px 62px 36px;background:linear-gradient(145deg,#0b2748,#123a68);
  color:#fff}
header .kicker{font-size:12px;letter-spacing:.16em;color:#93b2d6;
  text-transform:uppercase}
header h1{font-size:33px;line-height:1.26;margin:12px 0 12px;font-weight:700}
header .sub{font-size:15.5px;color:#d7e6f5;max-width:940px;line-height:1.75}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:22px}
.pill{border:1px solid #ffffff4d;border-radius:14px;padding:4px 11px;
  font-size:12px;background:#ffffff12}
.pill.hot{background:#b4231833;border-color:#ff9f9a80;color:#ffd9d6}
.pill.ok2{background:#008b7a33;border-color:#7fd8cb80;color:#d3f5ef}
.docbar{display:grid;grid-template-columns:repeat(4,1fr);gap:0;
  margin-top:26px;border-top:1px solid #ffffff2e;padding-top:16px}
.docbar div{font-size:12px;color:#9db6d4}
.docbar div b{display:block;font-size:14px;color:#fff;margin-top:3px;
  font-weight:600}

/* ---------- 导航 ---------- */
nav{padding:11px 62px;background:var(--soft);border-bottom:1px solid var(--line);
  position:sticky;top:0;z-index:20;display:flex;flex-wrap:wrap;gap:2px 4px}
nav a{color:#17518f;text-decoration:none;font-size:12.5px;padding:3px 8px;
  border-radius:5px;white-space:nowrap}
nav a:hover{background:#e3edf9;color:var(--blue)}

main{padding:26px 62px 60px}
section{margin-bottom:8px}

/* ---------- 标题 ---------- */
h2{font-size:23px;color:var(--navy);border-bottom:2.5px solid var(--navy);
  padding-bottom:8px;margin:44px 0 16px;font-weight:700}
h2:first-of-type{margin-top:12px}
h3{font-size:17.5px;color:#14507f;margin:28px 0 10px;font-weight:600;
  padding-left:11px;border-left:4px solid var(--teal)}
h4{font-size:15px;color:#1b3d66;margin:18px 0 7px;font-weight:600}
p{margin:9px 0}

/* ---------- 文本块 ---------- */
.lead{border-left:5px solid var(--blue);background:#eff6ff;padding:15px 19px;
  border-radius:8px;margin:14px 0 18px}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:13px 17px;
  border-radius:8px;margin:14px 0}
.note.risk{border-color:#eab4b0;background:#fff6f5}
.note.ok{border-color:#a8dcca;background:#f2fbf7}
ul.tight,ol.tight{margin:10px 0 14px 1.4em;padding:0}
ul.tight li,ol.tight li{margin:6px 0}
ol.tight{counter-reset:none}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;
  font-family:Consolas,"Courier New",monospace;font-size:12.5px;
  color:#1f3a5f}

/* ---------- 指标卡 ---------- */
.grid{display:grid;gap:11px;margin:16px 0}
.g4{grid-template-columns:repeat(4,1fr)}
.g3{grid-template-columns:repeat(3,1fr)}
.g2{grid-template-columns:repeat(2,1fr)}
.card{border:1px solid var(--line);border-top:4px solid var(--teal);
  border-radius:8px;padding:13px 14px;background:var(--soft)}
.card b{display:block;font-size:23px;color:var(--navy);line-height:1.2;
  margin-bottom:4px}
.card{font-size:12.5px;color:var(--muted)}
.card.blue{border-top-color:var(--blue)}
.card.warn{border-top-color:var(--warn)}
.card.red{border-top-color:var(--red)}
.card.ok{border-top-color:var(--good)}

/* ---------- 表格 ---------- */
table{width:100%;border-collapse:collapse;margin:14px 0 20px;font-size:13px}
th,td{border:1px solid var(--line);padding:8px 10px;vertical-align:top;
  text-align:left;line-height:1.6}
th{background:var(--navy);color:#fff;font-weight:600;font-size:12.5px}
tbody tr:nth-child(even) td{background:#fafcfe}
tr.grp td{background:#e8eef6 !important;font-weight:700;color:var(--navy);
  font-size:12.5px;letter-spacing:.04em}
td strong{color:var(--navy)}

/* ---------- 状态标记 ---------- */
.tag{display:inline-block;padding:1px 7px;border-radius:4px;font-size:11px;
  background:#e6f6f2;color:var(--teal);font-weight:700;white-space:nowrap}
.tag.tagw{background:#fff3d6;color:var(--warn)}
.tag.tagr{background:#fde8e6;color:var(--red)}
.tag.tagb{background:#e7f0fb;color:var(--blue)}
.good{color:var(--good);font-weight:700}
.bad{color:var(--red);font-weight:700}
.warn2{color:var(--warn);font-weight:700}

/* ---------- 公式 ---------- */
.formula{background:#f7fafd;border:1px solid var(--line);border-left:4px solid
  var(--blue);border-radius:7px;padding:12px 16px;margin:13px 0}
.formula code{background:none;padding:0;font-size:14px;color:#123a68;
  font-weight:600;display:block;line-height:1.85}
.formula .fres{display:block;margin-top:7px;color:var(--teal);
  font-weight:700;font-size:14px}
.formula .fnote{display:block;margin-top:6px;color:var(--muted);
  font-size:12.5px;line-height:1.65}

/* ---------- 图 ---------- */
figure{margin:18px 0 22px;border:1px solid var(--line);border-radius:10px;
  padding:14px 16px 10px;background:#fff}
figure.svgbox{background:#fcfdff}
svg.svgfig{display:block;width:100%;height:auto;margin:14px 0 0}
figure svg.svgfig{margin:0}
figure.pfig img{display:block;max-width:100%;height:auto;margin:0 auto;
  border-radius:5px}
figcaption{margin-top:10px;font-size:12.5px;color:var(--muted);
  line-height:1.65}
figcaption strong{color:var(--navy)}
figcaption .cap{display:block;margin-top:3px}
.figcap{color:var(--muted);font-size:12.5px;line-height:1.65;
  margin:8px 2px 22px}
.figcap strong{color:var(--navy)}
.papergrid{display:grid;grid-template-columns:1fr 1fr;gap:14px;margin:14px 0}
.papergrid figure{margin:0}

footer{padding:24px 62px;background:var(--navy);color:#c9d8e8;font-size:12.5px;
  line-height:1.8}
footer b{color:#fff}

/* ---------- 响应 ---------- */
@media(max-width:1000px){
  header,nav,main,footer{padding-left:24px;padding-right:24px}
  .g4,.g3,.g2,.papergrid{grid-template-columns:1fr}
  .docbar{grid-template-columns:1fr 1fr}
  table{font-size:12px}
}
@media print{
  body{background:#fff;font-size:10.5pt}
  .page{box-shadow:none;max-width:none}
  nav{display:none}
  header{padding:24px 0}
  main{padding:0}
  h2{page-break-after:avoid;margin-top:22px}
  h3,h4{page-break-after:avoid}
  table,figure,.card,.note,.lead,.formula{page-break-inside:avoid}
  tr{page-break-inside:avoid}
  @page{size:A4;margin:13mm}
}
"""

NAVITEMS = [
    ("exec", "0 摘要"), ("goals", "1 设计目标"), ("chip", "2 芯片规格"),
    ("inputs", "3 设计输入"), ("process", "4 设计流程"),
    ("perf", "5 性能设计"), ("mech", "6 机械设计"), ("schem", "7 原理图"),
    ("dwg", "8 详细设计图纸"), ("calc", "9 一维计算"),
    ("cfd", "10 三维仿真需求"), ("test", "11 试验验收"),
    ("risk", "12 风险"), ("open", "13 开放项"), ("refs", "14 来源"),
    ("appx", "附录"),
]


def build():
    nav = "".join(f'<a href="#{a}">{t}</a>' for a, t in NAVITEMS)

    head = f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NVIDIA B300 微通道+冲击换热冷板设计报告 {VER} · {DATE}</title>
<meta name="description" content="CP-B300-JM-01 冷板详细设计报告：设计目标、
GB300/B300 芯片规格、设计输入、设计流程、性能设计、机械设计、原理图、
CAD 2D/3D/爆炸图、一维性能计算、三维仿真需求">
<style>{CSS}</style>
</head>
<body>
<div class="page">
<header>
  <div class="kicker">Cold Plate Detailed Design Report · B300 Blackwell Ultra</div>
  <h1>NVIDIA B300 微通道 + 冲击换热<br>冷板设计报告</h1>
  <div class="sub">
    型号 {MODEL}。按 <strong>设计目标 → 芯片规格 → 设计输入 → 设计流程 →
    性能设计 → 机械设计 → 原理图 → 详细设计（2D/3D/爆炸）→ 一维计算 →
    三维仿真需求</strong> 组织。全文数值由 <code>calc/</code> 下脚本生成，
    工程图为按毫米真比例的矢量图。
  </div>
  <div class="meta">
    <span class="pill">文档 {DOC_NO}</span>
    <span class="pill">版本 {VER}</span>
    <span class="pill">{DATE}</span>
    <span class="pill">单相水基 · 紫铜冷板</span>
    <span class="pill ok2">水力达标</span>
    <span class="pill hot">热性能待证（区间跨目标线）</span>
    <span class="pill">非订单 ICD</span>
  </div>
  <div class="docbar">
    <div>保证点 DP-A<b>{A['P']:.0f} W @ {A['Q']:.1f} L/min</b></div>
    <div>包络 DP-B<b>{B['P']:.0f} W @ {B['Q']:.1f} L/min</b></div>
    <div>壳–进液热阻（实算区间）
        <b>{A['R_lo']:.4f} – {A['R_hi']:.4f} °C/W</b></div>
    <div>板内压降<b>{A['dp']['total'][0]/1000:.1f} –
        {A['dp']['total'][1]/1000:.1f} kPa（上限 {G['dP_limit']:.0f}）</b></div>
  </div>
</header>
<nav>{nav}</nav>
<main>
"""

    body = "".join([
        RA.ch0_summary(),
        RA.ch1_goals(),
        RA.ch2_chip(),
        RA.ch3_inputs(),
        RA.ch4_process(),
        RA.ch5_performance(),
        RB.ch6_mech(),
        RB.ch7_schematic(),
        RB.ch8_drawings(),
        RB.ch9_calc(),
        RB.ch10_cfd(),
        RB.ch11_test(),
        RB.ch12_risk(),
        RB.ch13_open(),
        RB.ch14_refs(),
        RB.appendix(),
    ])

    foot = f"""
</main>
<footer>
  <b>{DOC_NO} · NVIDIA B300 微通道+冲击换热冷板设计报告 {VER} · {DATE}</b><br>
  型号 {MODEL}　|　保证点 DP-A {A['P']:.0f} W　|　包络 DP-B {B['P']:.0f} W　|　
  与 GB300 NVL72 总体设计 v2.2 水力口径一致<br>
  本文件为内部设计评审文档，<b>非 NVIDIA / Lenovo 订单 ICD，非 FAT 保证书</b>。
  几何与性能结论在 C-01～C-03、C-07 关闭前均为候选。<br>
  数值可复算：<code>design/calc/cp_b300_1d.py</code>；
  报告可再生成：<code>design/calc/build_report.py</code>。
</footer>
</div>
</body>
</html>
"""
    return head + body + foot


if __name__ == "__main__":
    html = build()
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"已写出: {OUT}")
    print(f"大小: {len(html)/1024:.1f} KB")
    print(f"章节数: {html.count('<section')}　表格数: {html.count('<table')}"
          f"　内嵌 SVG: {html.count('<svg')}　位图: {html.count('<img')}")
