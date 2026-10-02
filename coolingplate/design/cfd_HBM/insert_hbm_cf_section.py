# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).with_name("NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914.html")
text = p.read_text(encoding="utf-8")
mark = '<section id="exec">'
sec = """<section id="hbm-cf">
<h2>HBM 交错流修订 · 2026-09-28</h2>
<p class="lead">同向七槽把列长两端拉成一冷一热。TIM 底面值 325.27–336.96 K，热端在出流侧。这一版把相邻槽改成反向流，出流端在流向上封死，流体只向上翻进上铜板里的汇流腔。</p>
<table>
<tr><th>项</th><th>修订后的单侧 HBM</th></tr>
<tr><td>槽</td><td>仍是 0.80 mm × 2.00 mm，肋 0.80 mm，7 条，两岸各 0.30 mm。底铜 2.0 mm，上铜板 4.0 mm，外顶面 z = 6 mm。加热段槽顶仍然封死，没有通长水缝。</td></tr>
<tr><td>流向</td><td>列长在网格里是 Y，也是云图里的水平长边。偶数槽（4 条）从高 Y 水平进入，流向低 Y。奇数槽（3 条）从低 Y 水平进入，流向高 Y。相邻槽反向，用来削掉同向流沿程的温差。</td></tr>
<tr><td>汇流</td><td>出流槽的端部在列长方向堵住，不从槽端水平流出。流体从 z = 2 mm 向上，经 z = 2–3 mm 的竖孔进入 z = 3–6 mm 的汇流腔，压力出口在 z = 6 mm。低 Y 腔只收偶数槽，高 Y 腔只收奇数槽。</td></tr>
<tr><td>不串腔</td><td>同一端的进流槽没有这个竖孔，z = 2–3 mm 仍是铜，把进流和汇流隔开。汇流腔沿槽宽连通，只连通同一组出流槽。</td></tr>
<tr><td>流量</td><td>单侧仍是 0.20 L/min。4 条与 3 条按条数分配，每条平均速度仍约 0.30 m/s。网格 mesh/hbm_cf_w08h20.msh。</td></tr>
<tr><td>和前文的关系</td><td>本节之前的一维表仍是同向直槽。那些压降和壁温不要当成这版交错流的结果。交错流以这次 CFD 为准，计算至少跑到 200 步，中途不因残差提前停止。</td></tr>
</table>
</section>
"""
if 'id="hbm-cf"' in text:
    print("already inserted")
elif mark not in text:
    raise SystemExit("mark missing")
else:
    p.write_text(text.replace(mark, sec + mark, 1), encoding="utf-8")
    print("inserted")
