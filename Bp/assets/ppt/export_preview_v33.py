# -*- coding: utf-8 -*-
"""
v3.3 演示版 —— 关键页抽查导出（加速交付版，只导 9 页，不做 39 页全量导出）

导出页：1 封面 / 2 一页结论 / 14 液冷占比三分母 / 15 三分母嵌套饼图（2026-09-06 页面修订新增）
       31 单位经济（改写）/ 32–34 商业篇新增三页 / 38 结论与下一步
（第 15 页新增后，原 30/31–33/37 顺延为 31/32–34/38）
输出到 assets/ppt/_preview_v33/，不覆盖 v3.2 的 _preview/。
运行： python export_preview_v33.py
"""
import os
import shutil
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.3_演示版_20260906.pptx")
OUT = os.path.join(HERE, "_preview_v33")

PAGES = [1, 2, 14, 15, 31, 32, 33, 34, 38]

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(PPTX, WithWindow=False)
try:
    for n in PAGES:
        pres.Slides(n).Export(os.path.join(OUT, f"p{n:02d}.png"), "PNG", 1600, 900)
finally:
    pres.Close()
    app.Quit()

files = sorted(os.listdir(OUT))
print(f"exported {len(files)} / {len(PAGES)} images -> {OUT}")
for f in files:
    print(" ", f)
