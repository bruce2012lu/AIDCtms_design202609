# -*- coding: utf-8 -*-
"""报告 HTML 自检：图片链接、标签配对、锚点、残留占位符、数值一致性。"""
import re
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
F = os.path.join(ROOT, "NVIDIA_B300_微通道冲击换热冷板设计报告_v2.0_20260914.html")

h = open(F, encoding="utf-8").read()
fails = []

print("=" * 70)
print("1. 图片链接")
print("=" * 70)
imgs = re.findall(r'<img[^>]*src="([^"]+)"', h)
miss = 0
for src in imgs:
    full = os.path.join(ROOT, src.replace("/", os.sep))
    ok = os.path.exists(full)
    if not ok:
        miss += 1
    print(("  OK   " if ok else "  MISS ") + src)
print(f"  共 {len(imgs)} 张，缺失 {miss}")
if miss:
    fails.append(f"{miss} 张图片链接失效")

print()
print("=" * 70)
print("2. 标签配对")
print("=" * 70)
for t in ["html", "head", "body", "header", "nav", "main", "footer",
          "section", "table", "thead", "tbody", "tr", "td", "th",
          "figure", "figcaption", "svg", "div", "p", "ul", "ol", "li",
          "dl", "h2", "h3", "h4", "code", "strong", "span", "defs",
          "text", "marker", "pattern", "g"]:
    o = len(re.findall(r"<" + t + r"[\s>]", h))
    c = len(re.findall(r"</" + t + r">", h))
    if o != c:
        print(f"  {t:12s} open={o:5d} close={c:5d}   <<< 不配对")
        fails.append(f"标签 <{t}> 不配对 ({o}/{c})")
    else:
        print(f"  {t:12s} open={o:5d} close={c:5d}")

print()
print("=" * 70)
print("3. 锚点")
print("=" * 70)
ids = set(re.findall(r'id="([^"]+)"', h))
broken = [a for a in re.findall(r'href="#([^"]+)"', h) if a not in ids]
if broken:
    print("  断链:", broken)
    fails.append(f"锚点断链 {broken}")
else:
    print(f"  全部 {len(set(re.findall(chr(39)+'href=\"#([^\"]+)\"'+chr(39), h)))} "
          f"个导航锚点均可达" if False else "  导航锚点全部可达")
print(f"  id 总数 {len(ids)}")

print()
print("=" * 70)
print("4. 残留占位符 / 异常值")
print("=" * 70)
text = re.sub(r"<style.*?</style>", "", h, flags=re.S)
text = re.sub(r"<svg.*?</svg>", "", text, flags=re.S)
clean = re.sub(r"<[^>]+>", " ", text)
for pat in ["TODO", "FIXME", "XXX", "None", "nan", "undefined",
            "Traceback", "0.0000 °C/W", "inf "]:
    n = clean.count(pat)
    if n:
        print(f"  发现 {pat!r} × {n}")
        fails.append(f"残留 {pat!r} × {n}")
if not fails:
    print("  无残留")

print()
print("=" * 70)
print("5. 关键数值一致性（与 model.py 对照）")
print("=" * 70)
sys.path.insert(0, HERE)
import model as M
A = M.solve("DP-A")
checks = [
    ("DP-A 功率", f"{A['P']:.0f} W"),
    ("壳-进液下界", f"{A['R_lo']:.4f}"),
    ("壳-进液上界", f"{A['R_hi']:.4f}"),
    ("流体温升", f"{A['dTf']:.2f}"),
    ("孔速", f"{A['jet']['V']:.3f}"),
    ("孔雷诺数", f"{A['jet']['Re']:.0f}"),
    ("HBM 流速", f"{A['hbm']['V']:.3f}"),
    ("面积放大", f"{M.AREA_GAIN:.2f}"),
    ("肋效率", f"{A['con']['eta']:.3f}"),
    ("R_wall", f"{M.R_WALL:.4f}"),
]
for name, val in checks:
    n = clean.count(val)
    ok = n > 0
    if not ok:
        fails.append(f"数值 {name}={val} 未出现在正文")
    print(f"  {name:14s} {val:>12s}  出现 {n} 次  "
          f"{'OK' if ok else '<<< 缺失'}")

print()
print("=" * 70)
print("6. 章节完整性")
print("=" * 70)
need = ["设计目标", "芯片规格数据", "设计输入", "设计流程", "性能设计",
        "机械设计", "原理图", "CAD 图纸", "一维性能计算",
        "三维仿真需求"]
for n in need:
    ok = n in clean
    if not ok:
        fails.append(f"缺章节 {n}")
    print(f"  {'OK  ' if ok else 'MISS'} {n}")

print()
print("=" * 70)
if fails:
    print(f"自检未通过，{len(fails)} 个问题：")
    for x in fails:
        print("  - " + x)
    sys.exit(1)
print(f"自检通过。文件 {os.path.basename(F)}，{len(h)/1024:.1f} KB")
print(f"内嵌 SVG {h.count('<svg')} 个，表格 {h.count('<table')} 个，"
      f"位图 {len(imgs)} 张")
