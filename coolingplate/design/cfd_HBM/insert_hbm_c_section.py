# -*- coding: utf-8 -*-
from pathlib import Path

path = Path(__file__).resolve().parent / "NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914.html"
text = path.read_text(encoding="utf-8")
needle = "</section>\n<section id=\"exec\">"
section = """</section>
<section id="hbm-c">
<h2>HBM 方案 C · 2026-09-29</h2>
<p class="lead">一维筛选采用方案 C：11 条槽，槽宽 0.45 mm，肋宽 0.50 mm，两岸各 0.525 mm，槽高仍是 2.00 mm。中间三槽从列中点进水，两侧四槽保持对冲。本节之前的七槽交错流不再作为当前算例。</p>
<table>
<tr><th>项</th><th>当前单侧 HBM</th></tr>
<tr><td>截面</td><td>0.525 + 11×0.45 + 10×0.50 + 0.525 = 11.000 mm。深宽比 4.44。底铜 2.0 mm，槽 2.0 mm，上铜板 4.0 mm。加热段槽顶封死。</td></tr>
<tr><td>流向</td><td>从低 X 侧数：1、3、9、11 自高 Y 流向低 Y；2、4、8、10 自低 Y 流向高 Y；5、6、7 在 Y=24 mm 水平进入列中点间隙，向两端分流。</td></tr>
<tr><td>汇流</td><td>低 Y 腔收 1、3、9、11 以及中间三槽的低 Y 支。高 Y 腔收 2、4、8、10 以及中间三槽的高 Y 支。压力出口仍在 z=6 mm。中间进水腔在 Y=24–26 mm、z=2–6 mm，只盖住第 5–7 槽，不和两侧槽短路。</td></tr>
<tr><td>流量</td><td>单侧仍是 0.20 L/min。两侧进口各 4/11，中间进口 3/11。满槽速度约 0.337 m/s。网格 mesh/hbm_c_w045h20.msh。</td></tr>
<tr><td>和一维的关系</td><td>一维场温差 1.34 °C 是筛选读数，不是这套 CFD 的结果。计算至少跑到 200 步，连续性未到 10⁻⁴ 之前不写成收敛。</td></tr>
</table>
</section>
<section id="exec">"""
if 'id="hbm-c"' in text:
    print("already")
elif needle not in text:
    raise SystemExit("needle missing")
else:
    path.write_text(text.replace(needle, section, 1), encoding="utf-8")
    print("inserted")
