# -*- coding: utf-8 -*-
"""
v3.5 演示版 —— 关键页抽查导出（加速交付，不超过 10 页）

导出：1 封面 / 2 一页结论 / 15 三分母嵌套饼图 /
      21–25 新增 3A 页（架构、七量、平台矩阵、Q–ΔP 不导、形态、冷板）
      实际按 build() 页序：工程篇二至九中抽 5 张 3A + G0.5 + 结论
输出到 assets/ppt/_preview_v35/，不覆盖 v3.3 的 _preview_v33/。
运行： python export_preview_v35.py
"""
import os
import shutil
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.5_演示版_20260906.pptx")
OUT = os.path.join(HERE, "_preview_v35")

# 1 封面 / 2 一页结论 / 15 三分母饼图 /
# 21 架构 c31 / 22 七量 c32 / 25 形态 c33 / 27 冷板 c34 / 28 标准 c35 /
# 38 G0.5 / 42 下一步（共 10 页；软件栈第 29 页与平台矩阵第 23 页本次不导出）
PAGES = [1, 2, 15, 21, 22, 25, 27, 28, 38, 42]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(PPTX, WithWindow=False)
try:
    nslides = pres.Slides.Count
    print(f"opened {nslides} slides")
    for n in PAGES:
        if n > nslides:
            print(f"  skip p{n:02d} (out of range)")
            continue
        pres.Slides(n).Export(os.path.join(OUT, f"p{n:02d}.png"), "PNG", 1600, 900)
finally:
    pres.Close()
    app.Quit()

files = sorted(os.listdir(OUT))
print(f"exported {len(files)} / {len(PAGES)} images -> {OUT}")
for f in files:
    print(" ", f)
