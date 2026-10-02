# -*- coding: utf-8 -*-
"""
用本机 PowerPoint 将演示稿导出为 PNG，用于抽查中文渲染与文字溢出。
输出到 assets/ppt/_preview/（仅用于验证，可随时删除）。
运行： python export_preview.py
"""
import os
import shutil
import win32com.client

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.2_演示版_20260905.pptx")
OUT = os.path.join(HERE, "_preview")

if os.path.isdir(OUT):
    shutil.rmtree(OUT)
os.makedirs(OUT, exist_ok=True)

app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(PPTX, WithWindow=False)
try:
    pres.Export(OUT, "PNG", 1600, 900)
finally:
    pres.Close()
    app.Quit()

files = sorted(os.listdir(OUT))
print(f"exported {len(files)} images -> {OUT}")
for f in files[:5]:
    print(" ", f)
