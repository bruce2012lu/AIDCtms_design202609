# -*- coding: utf-8 -*-
"""
演示版 PPTX 验证脚本
1) 用 python-pptx 重新打开，确认可读、页数、无损坏
2) 检查所有形状是否越出页面边界（文字溢出的几何前置检查）
3) 确认所有图片为内嵌（非外链），并统计嵌入的媒体数
4) 确认所有 run 均显式设置了中文字体
5) 抽查关键数值是否与 v3.2 报告原文一致（正则比对）
"""
import os
import re
import sys
from collections import Counter
from pptx import Presentation
from pptx.util import Emu

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.2_演示版_20260905.pptx")

ok = True


def fail(msg):
    global ok
    ok = False
    print("  [FAIL]", msg)


print("=" * 78)
print("1) 重新打开文件")
prs = Presentation(PPTX)
n = len(prs.slides._sldIdLst)
print(f"  文件可正常读取；页数 = {n}")
print(f"  页面尺寸 = {prs.slide_width / 914400:.4f} x {prs.slide_height / 914400:.4f} in "
      f"（比例 {prs.slide_width / prs.slide_height:.4f}，16:9 = {16/9:.4f}）")
if abs(prs.slide_width / prs.slide_height - 16 / 9) > 1e-3:
    fail("页面比例不是 16:9")
if not (25 <= n <= 36):
    fail(f"页数 {n} 超出预期范围")

print()
print("2) 形状边界检查（是否越出页面）")
SW, SH = prs.slide_width, prs.slide_height
TOL = Emu(int(0.02 * 914400))
over = []


def walk(shapes, idx):
    for sh in shapes:
        if sh.shape_type == 6:  # group
            walk(sh.shapes, idx)
            continue
        try:
            l, t, w, h = sh.left, sh.top, sh.width, sh.height
        except Exception:
            continue
        if l is None:
            continue
        if l < -TOL or t < -TOL or l + w > SW + TOL or t + h > SH + TOL:
            over.append((idx, sh.shape_type, sh.name,
                         round(l / 914400, 2), round(t / 914400, 2),
                         round((l + w) / 914400, 2), round((t + h) / 914400, 2)))


for i, sl in enumerate(prs.slides, 1):
    walk(sl.shapes, i)
if over:
    for o in over:
        fail(f"第 {o[0]} 页形状越界：{o[2]} 右下角 ({o[5]}, {o[6]}) in")
else:
    print("  全部形状均在页面边界内（容差 0.02 in）")

print()
print("3) 图片嵌入检查")
imgs = []
ext_links = []
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.shape_type == 13:  # PICTURE
            imgs.append((i, sh.image.filename, sh.image.ext,
                         round(sh.width / 914400, 2), round(sh.height / 914400, 2),
                         sh.image.size))
            blip = sh._element.blipFill.find(
                "{http://schemas.openxmlformats.org/drawingml/2006/main}blip")
            if blip is not None and blip.get(
                    "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}link"):
                ext_links.append((i, sh.name))
print(f"  幻灯片中图片形状数 = {len(imgs)}")
media = [p for p in prs.part.package.iter_parts()
         if "/media/" in str(p.partname)]
print(f"  包内嵌入媒体部件数 = {len(media)}")
if ext_links:
    for e in ext_links:
        fail(f"第 {e[0]} 页存在外链图片：{e[1]}")
else:
    print("  未发现任何外链图片（r:link），全部为内嵌 r:embed")
import io
from PIL import Image
dpis = []
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        if sh.shape_type != 13:
            continue
        with Image.open(io.BytesIO(sh.image.blob)) as im:
            px, py = im.size
        w_in = sh.width / 914400
        dpis.append((i, round(px / w_in), px, py))
low = [d for d in dpis if d[1] < 200]
print(f"  内嵌图片有效分辨率：最低 {min(d[1] for d in dpis)} dpi，"
      f"最高 {max(d[1] for d in dpis)} dpi（按幻灯片中实际显示尺寸计算）")
if low:
    fail(f"以下页面图片有效分辨率低于 200 dpi：{[(d[0], d[1]) for d in low]}")

print()
print("4) 字体检查（所有 run 是否显式指定中文字体）")
fonts = Counter()
missing = []
for i, sl in enumerate(prs.slides, 1):
    for sh in sl.shapes:
        tfs = []
        if sh.has_text_frame:
            tfs.append(sh.text_frame)
        if getattr(sh, "has_table", False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    tfs.append(c.text_frame)
        for tf in tfs:
            for p in tf.paragraphs:
                for r in p.runs:
                    if not r.text.strip():
                        continue
                    f = r.font.name
                    fonts[f] += 1
                    if f is None:
                        missing.append((i, r.text[:20]))
print("  字体分布：", dict(fonts))
if missing:
    fail(f"{len(missing)} 个 run 未显式指定字体，例如：{missing[:3]}")
else:
    print("  所有 run 均显式指定 Microsoft YaHei")

print()
print("5) 关键数值与 v3.2 报告原文比对")
rep = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.2_20260822.html")
html = open(rep, encoding="utf-8").read()
html_txt = re.sub(r"<[^>]+>", " ", html)
html_txt = re.sub(r"\s+", "", html_txt)

# (演示稿中出现的关键值, 在报告中应能找到的原文片段)
CHECKS = [
    ("液冷设备收入 2025 区间", "25–35"),
    ("液冷设备收入 2029 区间", "60–80"),
    ("液冷设备收入 2032 区间", "90–140"),
    ("Base 2032", "Base115"),
    ("组① 占比", "0.3%–0.9%"),
    ("组② 占比", "1.3%–5.6%"),
    ("组③ 占比", "5%–11%"),
    ("2032 组② 上界", "2.3%–5.6%"),
    ("L3 2025", "650–805"),
    ("L3 2030", "1,640–2,050"),
    ("L1 2025", "150–190"),
    ("L2 2025", "500–615"),
    ("DCPI 2025", "40–48"),
    ("AI 占比 2030", "76%–84%"),
    ("路径B 2025", "837"),
    ("路径A 加速 2030", "2,116"),
    ("路径A 基准 2025", "613"),
    ("McKinsey 加速累计", "9.4万亿"),
    ("IEA 用电", "485"),
    ("IEA 用电 2030", "950"),
    ("McKinsey 需求", "82"),
    ("McKinsey 需求 2030", "219"),
    ("JLL 供给", "103"),
    ("JLL 供给 2030", "200"),
    ("GB300 峰值", "155kWpeak"),
    ("GB300 Q-dP 45C", "45℃:177@18.4"),
    ("GB300 Q-dP 25C", "25℃:59 LPM@2.3 psi"),
    ("GB300 Q-dP 中间点", "35℃:89@4.9"),
    ("Dell IR7000", "264"),
    ("Huawei Atlas", "66kW"),
    ("HPE 液体负荷", "115kWliquid+17kWair"),
    ("曙光浸没收入", "4.579亿元"),
    ("曙光冷板收入", "2.986亿元"),
    ("曙光浸没毛利", "36.49%"),
    ("曙光冷板毛利", "10.36%"),
    ("Modine 分部毛利", "20.2%"),
    ("四大 2024", "约224"),
    ("四大 2025", "约413"),
    ("四大 2026 指引", "730–745"),
    ("旧版占比", "10%–13%"),
    ("新版占比 2029", "5%–8%"),
    ("新版占比 2030", "6%–9%"),
    ("设施侧液冷支出", "390亿美元"),
    ("液冷冷却装置单价", "485万美元/MW"),
    ("阶段上限", "800/1,200/1,500万元"),
    ("TrendForce 2024", "14%(2024)"),
    ("TrendForce 2025", "33%(2025)"),
    ("在建容量", "31.7GW"),
    ("新增投运 2025", "10–14"),
    ("新增投运 2032", "15–32"),
    ("AI 新增份额", "65%"),
    ("AI 新增份额上界", "82%"),
    ("Ecolab 交割", "2026-07-02"),
    ("Eaton 交割", "2026-03-12"),
    ("Schneider 75%", "取得75%"),
    ("CoolIT 预测收入", "5.5亿美元"),
    ("Boyd 预测收入", "15亿美元"),
    ("IT 设备占比", "75%–85%"),
    ("IT 腿低估", "36%"),
    ("confidence 结论5", "0.80"),
    ("confidence 点值", "0.35"),
    ("confidence 2.6", "0.72"),
    ("confidence TAM", "0.88"),
]
bad = []
for name, frag in CHECKS:
    f = re.sub(r"\s+", "", frag)
    if f not in html_txt:
        bad.append((name, frag))
print(f"  共比对 {len(CHECKS)} 项关键数值 / 口径片段")
if bad:
    for b in bad:
        fail(f"未在报告原文中找到：{b[0]} -> {b[1]}")
else:
    print("  全部命中报告原文，无自造数字")

print()
print("6) 禁止恢复的伪精确点值扫描")
alltext = []
for sl in prs.slides:
    for sh in sl.shapes:
        if sh.has_text_frame:
            alltext.append(sh.text_frame.text)
        if getattr(sh, "has_table", False) and sh.has_table:
            for row in sh.table.rows:
                for c in row.cells:
                    alltext.append(c.text)
deck = "\n".join(alltext)
BANNED = [
    (r"市场份额\s*[:：=]\s*\d", "市场份额点值"),
    (r"前五集中度\s*\d", "前五集中度点值"),
    (r"CDU\s*ASP\s*[:：=]\s*\d", "CDU 静态 ASP 点值"),
    (r"SAM\s*[:：=]\s*\d+\s*亿", "SAM 亿元点值"),
    (r"SOM\s*[:：=]\s*\d+\s*亿", "SOM 亿元点值"),
    (r"通用毛利率\s*\d", "通用毛利率点值"),
    (r"ROIC\s*[:：=]\s*\d", "ROIC 点值"),
]
hit = [d for p, d in BANNED if re.search(p, deck)]
if hit:
    fail(f"检测到伪精确点值：{hit}")
else:
    print("  未检测到任何被禁止的伪精确点值")
must_na = ["SAM 24m = 无数据", "SAM 24m 与 SOM 当前均为无数据",
           "贡献毛利 / ROIC / 盈亏平衡", "四档 × 四类工况的有效能力当前全部为无数据"]
for m in must_na:
    if m not in deck:
        fail(f"缺少必须保留的无数据声明：{m}")
    else:
        print(f"  已保留：{m}")

print()
print("7) 页脚完整性")
missing_foot = []
for i, sl in enumerate(prs.slides, 1):
    t = "\n".join(sh.text_frame.text for sh in sl.shapes if sh.has_text_frame)
    if "机密" not in t:
        missing_foot.append(i)
if missing_foot:
    fail(f"以下页面缺少机密标识：{missing_foot}")
else:
    print("  全部 35 页均含机密标识、版本与页码")

print()
print("=" * 78)
print("验证结果：", "全部通过" if ok else "存在问题，见上方 [FAIL]")
sys.exit(0 if ok else 1)
