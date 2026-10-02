# -*- coding: utf-8 -*-
"""生成 UC-01b 壁面射流与三槽流路说明（单页 HTML）。"""
import os
import sys

import fig_walljet as W
import model as M
from rhtml import fig, lead, note, p, ul

G = M.GEO
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "UC01_壁面射流与三槽流路说明.html")

CSS = """
:root{
  --navy:#0b2748;--blue:#1769e0;--teal:#008b7a;--ink:#182536;
  --muted:#5d6b80;--line:#d7e0ec;--bg:#eef3f8;--soft:#f7fafd;
  --warn:#a65b00;--red:#b42318;--good:#1f7a4d;
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:14.5px/1.72 "Microsoft YaHei","PingFang SC","Segoe UI",Arial,sans-serif}
.page{max-width:1080px;margin:auto;background:#fff;
  box-shadow:0 8px 34px #102a4c1f}
header{padding:36px 44px 26px;background:linear-gradient(145deg,#0b2748,#123a68);
  color:#fff}
header .kicker{font-size:12px;letter-spacing:.16em;color:#93b2d6}
header h1{font-size:26px;line-height:1.3;margin:10px 0 8px;font-weight:700}
header .sub{font-size:14.5px;color:#d7e6f5;max-width:880px}
.meta{display:flex;gap:8px;flex-wrap:wrap;margin-top:16px}
.pill{border:1px solid #ffffff4d;border-radius:14px;padding:3px 10px;
  font-size:12px;background:#ffffff12}
main{padding:22px 44px 48px}
h2{font-size:20px;color:var(--navy);border-bottom:2px solid var(--navy);
  padding-bottom:6px;margin:28px 0 12px}
h3{font-size:16px;color:#14507f;margin:20px 0 8px;padding-left:10px;
  border-left:4px solid var(--teal)}
p{margin:8px 0}
.lead{border-left:5px solid var(--blue);background:#eff6ff;padding:13px 16px;
  border-radius:8px;margin:12px 0 16px}
.note{border:1px solid #e3ca8d;background:#fffcf2;padding:12px 15px;
  border-radius:8px;margin:12px 0}
.note.ok{border-color:#a8dcca;background:#f2fbf7}
.note.risk{border-color:#eab4b0;background:#fff6f5}
ul.tight{margin:8px 0 12px 1.3em;padding:0}
ul.tight li{margin:5px 0}
code{background:#eef2f7;padding:1px 5px;border-radius:4px;
  font-family:Consolas,"Courier New",monospace;font-size:12.5px;color:#1f3a5f}
table{width:100%;border-collapse:collapse;margin:12px 0 16px;font-size:13px}
th,td{border:1px solid var(--line);padding:7px 9px;text-align:left}
th{background:var(--navy);color:#fff}
tbody tr:nth-child(even) td{background:#fafcfe}
.grid{display:grid;gap:12px;margin:12px 0}
.g2{grid-template-columns:1fr 1fr}
figure{margin:14px 0 8px;border:1px solid var(--line);border-radius:10px;
  padding:12px 14px 8px;background:#fcfdff}
figure svg.svgfig{display:block;width:100%;height:auto;margin:0}
figure.wide{max-width:780px;margin-left:auto;margin-right:auto}
figcaption{margin-top:8px;font-size:12.5px;color:var(--muted);line-height:1.65}
figcaption strong{color:var(--navy)}
figcaption .cap{display:block;margin-top:3px}
.legend{display:flex;flex-wrap:wrap;gap:8px 16px;font-size:12.5px;
  color:var(--muted);margin:6px 0 10px}
.legend i{display:inline-block;width:12px;height:12px;border-radius:2px;
  margin-right:5px;vertical-align:-1px}
footer{padding:16px 44px;background:var(--navy);color:#c9d8e8;font-size:12px}
@media(max-width:800px){
  header,main,footer{padding-left:18px;padding-right:18px}
  .g2{grid-template-columns:1fr}
}
"""


def build():
    xz = W.fig_section_xz()
    xy = W.fig_plan_xy()
    yz = W.fig_end_yz()
    rg = W.fig_three_regions()
    d = W.D
    hd = G["H_jet"] / d
    sd = G["S_jet"] / d
    hd0 = G["H_jet"] / G["D_jet"]
    sd0 = G["S_jet"] / G["D_jet"]

    parts = [
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<title>UC-01b 壁面射流与三槽流路</title>",
        f"<style>{CSS}</style></head><body><div class='page'>",
        "<header><div class='kicker'>CP-B300-JM-01 · 单元胞说明 · 不是整板报告</div>",
        "<h1>壁面射流是什么，水在 UC-01b 里怎么走</h1>",
        "<p class='sub'>用本设计的「一孔 + 三短槽 + 两端回液缝」把冲击三区说清楚："
        "自由射流打到铜壁之后转 90°，贴着壁面刮过去的那一层才叫壁面射流。"
        "侧槽并不对着孔，但仍能换热，主要就是靠它。</p>",
        "<div class='meta'>",
        "<span class='pill'>UC-01b 带槽流体</span>",
        f"<span class='pill'>S = {G['S_jet']:.1f} mm</span>",
        f"<span class='pill'>D = {d:.2f} mm（代码默认 {G['D_jet']:.2f}）</span>",
        f"<span class='pill'>H = {G['H_jet']:.1f} · 盖板 t = {G['t_lid']:.1f}</span>",
        "<span class='pill'>三槽 0.40×1.50 · 节距 0.80</span>",
        "<span class='pill'>回液缝 0.80 · 上抽</span>",
        "</div></header><main>",

        lead(
            "<strong>一句话：</strong>孔里射下来的是<strong>自由射流</strong>；"
            "正对孔、打在壁上的是<strong>驻点</strong>；"
            "转过弯、贴着铜壁往外刮的薄高速层才是<strong>壁面射流</strong>。"
            "它不是槽底深处的导管流，也不是还没撞壁的那股竖直流。"
        ),

        "<h2>什么是壁面射流</h2>",
        p("冲击射流打到固体壁上之后，会依次经过三个区（Martin 1977；"
          "Hussain 等论文里的 free-jet / stagnation / wall-jet）："),
        ul([
            "<strong>① 自由射流</strong>——还在孔口和铜壁之间，方向朝下。"
            f"本格 H = {G['H_jet']:.1f} mm，用 ⌀{d:.2f} 时 H/D = {hd:.1f}"
            f"（代码默认 ⌀{G['D_jet']:.2f} 则为 {hd0:.1f}）。",
            "<strong>② 驻点</strong>——射流轴打到壁面，动量从轴向变成径向，"
            "边界层被压到最薄，局部换热系数 h 最高。UC-01b 里只有<strong>中槽</strong>正对这个核。",
            "<strong>③ 壁面射流</strong>——流体已经转过 90°，变成贴壁的薄剪切层，"
            "沿径向 / 沿 ±X 往外跑。侧槽就处在这层扫过的路上。",
        ]),
        note(
            "<strong>不是壁面射流的两样东西：</strong>"
            "（1）孔里射下来、还没撞壁的竖直射流；"
            "（2）已经掉进 1.50 mm 深槽、按矩形管流往前走的那部分。"
            "壁面射流指的是<strong>贴着肋顶 / 槽口附近壁面</strong>的那一层。"
            "侧槽虽然不在孔正下方，仍能看到大约驻点 <strong>0.4–0.7</strong> 的 h，"
            "原因就是这层壁面射流还扫得到 Y = ±0.80 mm（约 r/D = 2）。",
            "ok"),

        "<h3>本格几何（来自 model.py GEO）</h3>",
        "<table><thead><tr><th>量</th><th>UC-01b 本图</th><th>代码默认</th>"
        "<th>备注</th></tr></thead><tbody>",
        f"<tr><td>单元节距 S</td><td>{G['S_jet']:.1f} mm</td><td>同左</td>"
        f"<td>周期盒</td></tr>",
        f"<tr><td>孔径 D</td><td>{d:.2f} mm</td><td>{G['D_jet']:.2f} mm</td>"
        f"<td>用户最近取 0.40；GEO 仍是 0.50</td></tr>",
        f"<tr><td>H / D</td><td>{hd:.1f}</td><td>{hd0:.1f}</td>"
        f"<td>间隙 H = {G['H_jet']:.1f} mm</td></tr>",
        f"<tr><td>S / D</td><td>{sd:.1f}</td><td>{sd0:.1f}</td><td></td></tr>",
        f"<tr><td>盖板厚</td><td>{G['t_lid']:.1f} mm</td><td>同左</td><td></td></tr>",
        f"<tr><td>短槽</td><td>0.40 × 1.50，节距 0.80</td><td>同左</td>"
        f"<td>中槽在孔下，侧槽在 Y = ±0.80</td></tr>",
        f"<tr><td>回液缝</td><td>0.80 mm，±X 端，向上</td><td>同左</td>"
        f"<td>周期缝本胞各见一半</td></tr>",
        "</tbody></table>",

        "<div class='legend'>",
        "<span><i style='background:#2b6cb0'></i>自由射流 / 水</span>",
        "<span><i style='background:#c53030'></i>驻点</span>",
        "<span><i style='background:#c05621'></i>壁面射流 / 回液</span>",
        "<span><i style='background:#38b2ac'></i>槽腔（导管流）</span>",
        "<span><i style='background:#d9a06b'></i>铜</span>",
        "</div>",

        "<h2>流体怎么走（四个方向）</h2>",
        p("路径固定为："
          "<strong>孔口自由射流 → 底面驻点 → 壁面射流沿径向 / ±X → "
          "扫入侧槽并沿间隙走 → ±X 端回液缝向上抽走</strong>。"
          "必须尽快抽走，否则壁面射流会变成交叉流，把下一孔的驻点吹歪。"),

        "<div class='grid g2'>",
        fig(xz, "图 1", "过孔纵剖面（Y = 0，沿槽长）",
            "竖蓝箭：自由射流。红点：驻点。橙横箭：贴肋顶的壁面射流。"
            "两端橙竖箭：回液缝上抽。槽底青箭是导管流，不要和壁面射流当成一回事。",
            "svgbox wide"),
        fig(yz, "图 3", "沿槽端视（X = 0，看三槽）",
            "同一股壁面射流贴着肋顶向 ±Y 刮，探进两侧槽口。"
            "水缝里的 ⊗ / ⊙ 是去 ±X 回液；槽腔里的青圈也是沿槽走出图面，不是往下钻。",
            "svgbox wide"),
        "</div>",
        "<div class='grid g2'>",
        fig(xy, "图 2", "单元顶视（看流线与 r/D）",
            "中槽正对孔；侧槽带大约在 r/D = 2。"
            "橙线从驻点散开，沿槽口折向左右回液缝。这就是侧槽仍有对流的几何原因。"),
        fig(rg, "图 4", "冲击三区示意",
            "经典分区画在本格的 H = 2.0、D = 0.40 上。"
            "记住：壁面射流是撞壁之后的贴壁层，不是孔里那一竖，也不是槽深里的管流。"),
        "</div>",

        note(
            "<strong>读图顺序建议：</strong>先看图 4 建立三区，"
            "再看图 1 看 ±X 回液，再看图 3 看侧槽为什么能分到对流，"
            "最后用图 2 把 r/D 和三条槽对上号。",
            ""),

        "<h2>尺寸出处</h2>",
        p(f"S、H、盖板厚、槽宽/深/节距、回液缝宽均取 <code>calc/model.py</code> 的 "
          f"<code>GEO</code>。"
          f"孔径本图按 UC-01b 常用值 <strong>{d:.2f} mm</strong> 绘制，"
          f"并在图上注明代码默认 <strong>{G['D_jet']:.2f} mm</strong>。"
          f"余铜厚 {G['base_cu']:.1f} mm。图按真比例，viewBox 为 autofit，不裁切。"),
        "</main>",
        "<footer>AIDCtms / coolingplate / design · UC-01b 说明页 · "
        "不替代设计报告 · 请勿当作整板图纸</footer>",
        "</div></body></html>",
    ]
    html = "".join(parts)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(html)
    return OUT, html


if __name__ == "__main__":
    path, html = build()
    bad, rows = W.overflow_report()
    print("OUT", path)
    print("HTML_BYTES", len(html.encode("utf-8")))
    print(f"{'fig':22s} {'viewBox':>28s} {'bbox':>28s}  overflow")
    for name, vb, bb, tag in rows:
        print(f"{name:22s} {str(tuple(round(x,1) for x in vb)):>28s} "
              f"{str(tuple(round(x,1) for x in bb)):>28s}  {tag or 'ok'}")
    if bad:
        print("OVERFLOW", bad)
        sys.exit(1)
    if "<svg" not in html:
        print("NO_SVG")
        sys.exit(1)
    print("OK")
