# -*- coding: utf-8 -*-
"""行业液冷产品对标分析 PPT v2.0
结构：结论先行 -> 四章递进（为什么 / 规范怎么说 / 产品能否达标 / 怎么选）
图片：两份 2025-08 原文页，已去厂家铭牌
"""
import os
from lxml import etree
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.oxml.ns import qn
from PIL import Image

NAVY = RGBColor(0x0B, 0x27, 0x48)
DEEP = RGBColor(0x14, 0x3A, 0x62)
BLUE = RGBColor(0x17, 0x69, 0xE0)
TEAL = RGBColor(0x00, 0x8B, 0x7A)
INK = RGBColor(0x18, 0x25, 0x36)
MUTED = RGBColor(0x60, 0x70, 0x86)
LINE = RGBColor(0xD7, 0xE0, 0xEC)
SOFT = RGBColor(0xF6, 0xF9, 0xFC)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
RED = RGBColor(0xB4, 0x23, 0x18)
AMBER = RGBColor(0xA6, 0x5B, 0x00)
PALE_B = RGBColor(0xEE, 0xF5, 0xFF)
PALE_A = RGBColor(0xFF, 0xF8, 0xE8)
PALE_R = RGBColor(0xFF, 0xF4, 0xF3)
PALE_T = RGBColor(0xE9, 0xF7, 0xF4)
SKY = RGBColor(0x9B, 0xC4, 0xE8)

W, H = Inches(13.333), Inches(7.5)
FONT = "Microsoft YaHei"
BASE = r"d:\agents2026\agents2026\agents\AIDCtms\solutions\assets\src_pdf_pages\scrub"
AI = os.path.join(BASE, "ai_ready")
CC = os.path.join(BASE, "coolchip")

prs = Presentation()
prs.slide_width, prs.slide_height = W, H
BLANK = prs.slide_layouts[6]
_pages = []          # 章节路标
TOTAL = 27


# ---------------- primitives ----------------
def set_run(run, text, size, bold, color):
    run.text = text
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.color.rgb = color
    f.name = FONT
    rPr = run._r.get_or_add_rPr()
    ea = rPr.find(qn("a:ea"))
    if ea is None:
        ea = etree.SubElement(rPr, qn("a:ea"))
    ea.set("typeface", FONT)


def _first_run(p):
    return p.runs[0] if p.runs else p.add_run()


def tb(slide, l, t, w, h, text, size=16, bold=False, color=INK,
       align=PP_ALIGN.LEFT, mid=False, spacing=1.0):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    if mid:
        tf._txBody.bodyPr.set("anchor", "ctr")
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    set_run(_first_run(p), text, size, bold, color)
    return box


def bullets(slide, l, t, w, h, items, size=15, color=INK, gap=9, spacing=1.15):
    box = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.04)
    tf.margin_top = tf.margin_bottom = 0
    first = True
    for it in items:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.space_after = Pt(gap)
        p.space_before = Pt(0)
        p.line_spacing = spacing
        bold = it.startswith("*")
        set_run(_first_run(p), ("· " + it.lstrip("*")), size, bold,
                TEAL if bold else color)
    return box


def rect(slide, l, t, w, h, fill, line=None, lw=1.0):
    sh = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(lw)
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh


def card(slide, l, t, w, h, fill=SOFT, line=LINE):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(1.0)
    sh.adjustments[0] = 0.06
    sh.shadow.inherit = False
    sh.text_frame.text = ""
    return sh


def pic(slide, path, l, t, max_w, max_h):
    iw, ih = Image.open(path).size
    k = min(max_w / iw, max_h / ih)
    pw, ph = iw * k, ih * k
    slide.shapes.add_picture(path, Inches(l + (max_w - pw) / 2), Inches(t + (max_h - ph) / 2),
                             Inches(pw), Inches(ph))


def chrome(slide, ch, title, n):
    """章节色带 + 结论式标题 + 页脚"""
    rect(slide, 0, 0, 13.333, 1.02, NAVY)
    rect(slide, 0, 1.02, 13.333, 0.045, TEAL)
    tb(slide, 0.42, 0.10, 11.6, 0.28, ch, 11, False, SKY)
    tb(slide, 0.42, 0.36, 12.5, 0.58, title, 23, True, WHITE, mid=True)
    rect(slide, 0, 7.2, 13.333, 0.3, NAVY)
    tb(slide, 0.42, 7.2, 10.4, 0.3,
       "行业液冷产品对标分析 v2.0  ·  原图已去厂家铭牌  ·  对标解读，不替代 OEM ICD 与厂家选型单",
       9.5, False, RGBColor(0xC6, 0xD6, 0xE4), mid=True)
    tb(slide, 11.4, 7.2, 1.5, 0.3, f"{n} / {TOTAL}", 9.5, False, RGBColor(0xC6, 0xD6, 0xE4),
       PP_ALIGN.RIGHT, mid=True)


def takeaway(slide, text, tone="b"):
    """底部一句话结论"""
    fill, edge, txt = {
        "b": (PALE_B, BLUE, INK),
        "t": (PALE_T, TEAL, INK),
        "a": (PALE_A, AMBER, INK),
        "r": (PALE_R, RED, INK),
    }[tone]
    card(slide, 0.42, 6.42, 12.5, 0.66, fill, edge)
    rect(slide, 0.42, 6.42, 0.09, 0.66, edge)
    tb(slide, 0.68, 6.42, 12.1, 0.66, text, 14.5, False, txt, mid=True)


def figure_slide(ch, title, n, img, notes, src, tone="b", take=None):
    s = prs.slides.add_slide(BLANK)
    chrome(s, ch, title, n)
    card(s, 0.42, 1.2, 7.95, 5.05, WHITE, LINE)
    pic(s, img, 0.52, 1.28, 7.75, 4.6)
    tb(s, 0.55, 5.93, 7.7, 0.26, src, 9.5, False, MUTED)
    card(s, 8.6, 1.2, 4.32, 5.05, SOFT, LINE)
    rect(s, 8.6, 1.2, 4.32, 0.42, DEEP)
    tb(s, 8.78, 1.2, 4.0, 0.42, "读图要点", 13, True, WHITE, mid=True)
    bullets(s, 8.78, 1.78, 3.96, 4.35, notes, 14.5)
    if take:
        takeaway(s, take, tone)
    return s


def section(no, title, sub, n):
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, 13.333, 7.5, NAVY)
    rect(s, 0, 0, 0.18, 7.5, TEAL)
    tb(s, 0.9, 2.35, 3.0, 1.1, f"第 {no} 章", 22, False, SKY)
    tb(s, 0.9, 3.0, 11.5, 1.0, title, 40, True, WHITE)
    tb(s, 0.9, 4.15, 11.0, 0.6, sub, 17, False, RGBColor(0xD7, 0xE6, 0xF5))
    # 路标
    for i, (num, name) in enumerate(_pages):
        x = 0.9 + i * 3.05
        on = num == no
        card(s, x, 5.5, 2.85, 0.72, TEAL if on else RGBColor(0x1A, 0x3E, 0x66), None)
        tb(s, x + 0.16, 5.5, 2.55, 0.72, f"{num}  {name}", 13, on, WHITE, mid=True)
    tb(s, 11.4, 7.15, 1.5, 0.3, f"{n} / {TOTAL}", 9.5, False, SKY, PP_ALIGN.RIGHT)
    return s


_pages = [(1, "为什么重做"), (2, "规范怎么说"), (3, "产品能否达标"), (4, "怎么选")]

CH1 = "第 1 章 · 为什么必须重做底座"
CH2 = "第 2 章 · 行业规范怎么说"
CH3 = "第 3 章 · 产品能否达标"
CH4 = "第 4 章 · 怎么选"


# ================= 1 封面 =================
s = prs.slides.add_slide(BLANK)
rect(s, 0, 0, 13.333, 7.5, NAVY)
rect(s, 0, 0, 0.18, 7.5, TEAL)
tb(s, 0.85, 1.15, 11.5, 0.32, "AIDC  ·  冷板液冷底座  ·  产品对标", 13, False, SKY)
tb(s, 0.85, 1.62, 11.5, 1.15, "行业液冷产品对标分析", 42, True, WHITE)
tb(s, 0.85, 2.92, 11.5, 0.5, "从 GB300 的硬约束出发，用 ASHRAE / OCP 做中立标尺，再看产品够不够",
   18, False, RGBColor(0xD7, 0xE6, 0xF5))
for i, (num, name, desc) in enumerate([
    ("1", "为什么重做", "功率代际 · 90 秒失冷"),
    ("2", "规范怎么说", "ASHRAE W 类 · OCP 2 MW"),
    ("3", "产品能否达标", "原图 · 铭牌 · 竞品"),
    ("4", "怎么选", "场景 · 校核 · 禁止事项"),
]):
    x = 0.85 + i * 3.05
    card(s, x, 3.95, 2.85, 1.5, DEEP, None)
    rect(s, x, 3.95, 2.85, 0.08, TEAL)
    tb(s, x + 0.2, 4.14, 2.5, 0.36, num, 20, True, TEAL)
    tb(s, x + 0.2, 4.52, 2.5, 0.34, name, 16, True, WHITE)
    tb(s, x + 0.2, 4.9, 2.5, 0.44, desc, 12, False, SKY)
tb(s, 0.85, 6.05, 11.5, 0.34,
   "材料：AI 算力工厂液冷底座（17 页）+ CoolChip CDU 方案册（8 页），均 2025-08-08", 13, False, SKY)
tb(s, 0.85, 6.45, 11.5, 0.34,
   "刷新：2026-09 公开数据表与官方新闻  ·  图内厂家铭牌 / Logo 已去除", 13, False, SKY)
tb(s, 0.85, 6.9, 11.5, 0.34, "v2.0  ·  2026-09-05", 12, False, RGBColor(0x7F, 0xA6, 0xC9))

# ================= 2 执行摘要 =================
s = prs.slides.add_slide(BLANK)
chrome(s, "执行摘要", "五条结论：底座能力够，颗粒有空档，口径必须分层", 2)
concl = [
    ("01", "风冷已被甩开", "单柜 41 → 132 → 142/155 → 200+ kW。GB300 液冷是架构强制，无风冷版本。", TEAL),
    ("02", "口径必须分层", "液气比出现 70/30、72/28、90/10 三套；比流量出现 1.0–1.5 与 0.39–1.18 两套。", RED),
    ("03", "标尺用中立件", "ASHRAE W45 定水温语义，OCP Deschutes 定 CDU 硬指标，厂商彩页只作能力证据。", BLUE),
    ("04", "产品有空档", "中国册 121 与 450 kW 之间无行级 SKU，而 GB300 单柜正落在 150 kW 档。", AMBER),
    ("05", "可用性决定胜负", "GPU 失冷容忍约 90 秒，远短于传统 30 分钟到场；N+1、环网隔离、FAT 比铭牌 kW 更关键。", TEAL),
]
y = 1.25
for no, t, d, col in concl:
    card(s, 0.42, y, 12.5, 1.0, SOFT, LINE)
    rect(s, 0.42, y, 0.1, 1.0, col)
    tb(s, 0.68, y, 0.85, 1.0, no, 22, True, col, mid=True)
    tb(s, 1.6, y + 0.13, 2.65, 0.75, t, 17, True, NAVY, mid=True)
    tb(s, 4.35, y + 0.13, 8.35, 0.75, d, 14.5, False, INK, mid=True)
    y += 1.07
takeaway(s, "本文件是对标解读：可用于选型判据与招标条款草拟，不替代 OEM ICD、厂家选型单与现场 FAT 报告。", "b")

# ================= 3 论证路线 =================
s = prs.slides.add_slide(BLANK)
chrome(s, "论证路线", "四步：先定约束，再定标尺，然后验产品，最后落选型", 3)
steps = [
    ("1", "为什么重做底座", ["单柜功率代际跳变", "GB300 硬约束：142/155、90/10、W45", "失冷窗口约 90 秒"], TEAL),
    ("2", "行业规范怎么说", ["ASHRAE W17–W+ 水温语义", "OCP Deschutes 2 MW CDU 硬指标", "三套液气比与两套比流量分层"], BLUE),
    ("3", "产品能否达标", ["架构树与五项设计输入", "L2A / L2L 铭牌与二次侧实物", "能力阶梯 · 竞品 · 市场位置"], DEEP),
    ("4", "怎么选", ["按场景选形态", "GB300 适配校核", "风险、禁止事项与待补"], AMBER),
]
for i, (no, t, items, col) in enumerate(steps):
    x = 0.42 + i * 3.16
    card(s, x, 1.3, 2.98, 4.85, SOFT, LINE)
    rect(s, x, 1.3, 2.98, 0.68, col)
    tb(s, x + 0.18, 1.3, 2.6, 0.68, f"{no}   {t}", 15, True, WHITE, mid=True)
    bullets(s, x + 0.2, 2.15, 2.6, 3.8, items, 14, INK, 12)
    if i < 3:
        tb(s, x + 2.92, 3.3, 0.3, 0.5, "▸", 20, True, MUTED, PP_ALIGN.CENTER)
takeaway(s, "每一章的结论都写在页标题上；页面底部条是该页唯一需要带走的判断。", "t")

# ================= 4 章节页 1 =================
section(1, "为什么必须重做底座", "功率、混合冷却比例、失冷窗口——三个都不可谈判", 4)

# ================= 5 功率代际 =================
figure_slide(
    CH1, "单柜功率按代际跳变，风冷路线已经没有延长线", 5,
    os.path.join(AI, "ai_ready_p01.png"),
    ["*芯片：A100≈400 W → H100≈700 W → B200≈1000 W → Feynman 宣称 4400 W",
     "*单柜：H100 41 kW → GB200 NVL72 132 kW → Rubin NVL144 200+ kW → Ultra 600 kW → Feynman 1000 kW",
     "GB300 公开 142、OEM 峰值 155，正落在 132 与 200+ 之间",
     "图注来源为 Omdia / NVIDIA / SemiAnalysis，是趋势判断，不是订单承诺"],
    "原图：液冷底座 p.2「芯片升级，散热如何变化？」（页脚品牌已去除）",
    "t", "底座要按代际选：今天满足 155 kW，还得留出到 200 kW 级的接口与冷源余量。")

# ================= 6 GB300 硬约束 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH1, "GB300 的约束是架构级的，不是配置项", 6)
tb(s, 0.42, 1.2, 12.5, 0.32, "2026-09 公开资料交叉核对（NVIDIA ERA / Lenovo LP2357 / HPE QuickSpecs / ModulEdge 汇总）",
   12, False, MUTED)
kpi = [
    ("132–142 kW", "标称单柜", "NVIDIA ERA 写 up to 142；HPE 132；Lenovo 135"),
    ("~155 kW", "EDP 峰值", "按峰值包络做冷却与母线，不按标称"),
    ("90 / 10", "液 / 气", "CPU+GPU+NVSwitch 走液，其余约 10% 仍需风"),
    ("W45", "设施水等级", "供水 2–50℃；MGX 全系按 45℃ 温水设计"),
]
for i, (v, k, d) in enumerate(kpi):
    x = 0.42 + i * 3.16
    card(s, x, 1.62, 2.98, 1.95, DEEP, None)
    tb(s, x + 0.16, 1.78, 2.66, 0.62, v, 25, True, WHITE, mid=True)
    tb(s, x + 0.16, 2.42, 2.66, 0.3, k, 14, True, TEAL)
    tb(s, x + 0.16, 2.76, 2.66, 0.7, d, 11.5, False, SKY)
rows = [
    ("流量随水温查表", "25℃ 约 59 L/min，45℃ 约 177 L/min", "温度与流量必须成对取用，不能各取一半"),
    ("负载秒级摆动", "Uptime 记录机柜 60 → 150 kW 在 1–2 秒内完成", "控制要按动态负载设计，N+1 之外考虑 N+2"),
    ("母线预留", "HPE 建议按 192 kW provision 母线", "电与冷同步留余量，否则下一代必须停机改造"),
    ("无风冷版本", "NVL72 不存在纯风冷配置", "「全液冷可取消 CRAH」是错的，10% 风侧必须留"),
]
y = 3.78
for a, b, c in rows:
    card(s, 0.42, y, 12.5, 0.6, SOFT, LINE)
    tb(s, 0.6, y, 2.5, 0.6, a, 14, True, NAVY, mid=True)
    tb(s, 3.2, y, 4.55, 0.6, b, 13.5, False, INK, mid=True)
    tb(s, 7.9, y, 4.85, 0.6, c, 13, False, MUTED, mid=True)
    y += 0.66
takeaway(s, "设计基线取 155 kW 峰值 + 90/10 + W45；任何厂商宣传区间都不得替换这三个数。", "r")

# ================= 7 90 秒 =================
figure_slide(
    CH1, "失冷容忍约 90 秒，传统 30 分钟到场机制直接失效", 7,
    os.path.join(AI, "ai_ready_p15.png"),
    ["*左：传统机房中断恢复标准 = 30 分钟（响应 5 + 恢复 25）",
     "*右：GPU 对液冷中断容忍 ≈ 90 秒",
     "泵停/断流 30–60 s；气阻 30–90 s；供液超温 60–120 s；滤芯瞬堵 30–60 s",
     "漏液联锁为立即停机，没有缓冲",
     "此页是维谛原图口径，不是 NVIDIA 官方秒级值"],
    "原图：液冷底座 p.16「从液冷视角评估 AIDC 对中断恢复的容忍度」",
    "r", "90 秒意味着恢复必须自动化：备泵自投、旁通、蓄冷惯量与联锁，全靠人工调度必然超时。")

# ================= 8 章节页 2 =================
section(2, "行业规范怎么说", "先用中立标准立尺，再拿厂商彩页当证据", 8)

# ================= 9 ASHRAE W 类 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH2, "水温先说清 W 类语义，再谈能不能省掉冷机", 9)
tb(s, 0.42, 1.2, 12.5, 0.34,
   "ASHRAE 第 5 版把液冷等级按上限温度重命名：所有 W 类下限统一 2℃，编号即供液上限（℃）", 14, False, INK)
wc = [
    ("W17", "17", RGBColor(0x2E, 0x6F, 0xC4), "多数时段需冷冻水"),
    ("W27", "27", RGBColor(0x2A, 0x86, 0xB8), "中等水温"),
    ("W32", "32", RGBColor(0x24, 0x96, 0x9E), "自然冷时长明显增加"),
    ("W40", "40", RGBColor(0x2E, 0x9E, 0x74), "第 5 版新增等级"),
    ("W45", "45", TEAL, "塔 / 干冷全年排热，多数气候可免冷机"),
    ("W+", ">45", AMBER, "开放等级，超过 45℃"),
]
base_y, max_h = 4.62, 2.6
for i, (name, temp, col, note) in enumerate(wc):
    x = 0.75 + i * 2.05
    val = 45.0 if name == "W+" else float(temp)
    h = max_h * (val / 48.0)
    rect(s, x, base_y - h, 1.5, h, col)
    tb(s, x, base_y - h - 0.42, 1.5, 0.38, name, 17, True, col, PP_ALIGN.CENTER)
    tb(s, x, base_y + 0.06, 1.5, 0.3, f"上限 {temp}℃", 12.5, True, INK, PP_ALIGN.CENTER)
    tb(s, x - 0.12, 4.98, 1.74, 0.95, note, 11.5, False, MUTED, PP_ALIGN.CENTER)
rect(s, 0.6, base_y, 12.2, 0.02, LINE)
card(s, 0.42, 5.62, 6.15, 0.68, PALE_A, AMBER)
tb(s, 0.62, 5.62, 5.8, 0.68, "合规新定义：在该等级全温域内「不降频满性能」运行，才算符合该 W 类。",
   13.5, False, INK, mid=True)
card(s, 6.77, 5.62, 6.15, 0.68, PALE_T, TEAL)
tb(s, 6.97, 5.62, 5.8, 0.68, "GB300 属 W45（2–50℃ 供水）；维谛二次侧产品窗 10–45℃ 可覆盖。",
   13.5, False, INK, mid=True)
takeaway(s, "设施侧按 W45 设计即可免冷机；但 10℃ 不是 GB300 运行点，产品窗宽 ≠ 保证点。", "t")

# ================= 10 OCP 标尺 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH2, "CDU 该怎么评，OCP Deschutes 已经把硬指标写死", 10)
tb(s, 0.42, 1.2, 12.5, 0.34,
   "OCP 公开的 2 MW CDU 规格（Project Deschutes，2025-09 发布 / v1.0 2026-02）；已有多家厂商公开对标该规格",
   12.5, False, MUTED)
left = [
    ("容量 / 端温差", "2000 kW @ 3℃ ATD"),
    ("二次流量 / 压差", "约 500 GPM，二次可用约 80–90 psi"),
    ("泵冗余", "N+1（泵及附件），无密封泵"),
    ("电源", "至少 1N 冗余，期望 2N；每泵回路独立"),
    ("热插拔", "冗余部件须在连续运行中可换"),
]
right = [
    ("过滤", "主过滤 25–44 μm + 旁流 0.2 μm（约 3 GPM）"),
    ("漏液", "漏液绳 + PLC，分 3 区"),
    ("排气 / 定压", "Spirovent 气水分离 + 直流式膨胀罐"),
    ("压力", "工作 0–130 psi，130 psi 泄压"),
    ("工质 / 水质", "DI 水与 PG25；在线 pH 与电导率"),
]
for col_i, (title, data, tone) in enumerate([
    ("交付能力项", left, DEEP), ("流体完整性项", right, TEAL)
]):
    x = 0.42 + col_i * 6.4
    card(s, x, 1.66, 6.1, 3.9, SOFT, LINE)
    rect(s, x, 1.66, 6.1, 0.5, tone)
    tb(s, x + 0.2, 1.66, 5.7, 0.5, title, 15, True, WHITE, mid=True)
    yy = 2.3
    for a, b in data:
        tb(s, x + 0.22, yy, 1.95, 0.55, a, 13.5, True, NAVY, mid=True)
        tb(s, x + 2.25, yy, 3.7, 0.55, b, 13, False, INK, mid=True)
        rect(s, x + 0.22, yy + 0.58, 5.66, 0.01, LINE)
        yy += 0.62
card(s, 0.42, 5.68, 12.5, 0.62, PALE_B, BLUE)
tb(s, 0.62, 5.68, 12.1, 0.62,
   "招标可直接引用的六项：ATD、二次可用压差、泵与电源冗余、两级过滤、漏液分区、在线水质。厂家彩页往往只给冷量 kW。",
   13.5, False, INK, mid=True)
takeaway(s, "把 OCP 这张表当评标模板：同一 600 kW，3℃ 与 8℃ ATD、25 psi 与 80 psi 压差不是同一台机器。", "b")

# ================= 11 口径分层 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH2, "三套液气比、两套比流量：分层引用，禁止拼接", 11)
tri = [
    ("70 / 30", "底座 p.3 通用链路", "内存与 SSD 走风，CPU/GPU 走液；液侧 XDU 60–1350 kW。行业示意。", AMBER),
    ("72 / 28", "底座 p.11 SuperPOD 案", "每 POD 液 832 kW + 风 320 kW；130 kW 算力柜。参考设计。", TEAL),
    ("90 / 10", "GB300 OEM 口径", "本项目冻结基线。不得据此取消 CRAH，也不得与前两套叠加。", RED),
]
for i, (v, src, note, col) in enumerate(tri):
    x = 0.42 + i * 4.22
    card(s, x, 1.28, 4.04, 2.9, SOFT, LINE)
    rect(s, x, 1.28, 4.04, 1.02, col)
    tb(s, x, 1.28, 4.04, 1.02, v, 30, True, WHITE, PP_ALIGN.CENTER, mid=True)
    tb(s, x + 0.2, 2.42, 3.64, 0.34, src, 14, True, NAVY)
    tb(s, x + 0.2, 2.8, 3.64, 1.25, note, 13.5, False, INK)
pair = [
    ("比流量", "底座 p.10 写 1.0–1.5 L/min·kW", "Lenovo Table 27 为 0.39–1.18，且须与 25–45℃ 成对", "以 OEM 表为准"),
    ("过滤精度", "底座 p.10 写 <50 μm；全球页 50 / 25 μm", "OCP 主过滤 25–44 μm + 旁流 0.2 μm", "冷板项目取严 25 μm"),
    ("失冷窗口", "底座 p.16 写约 90 秒", "NVIDIA 未发布官方秒级值", "作设计裕量，不写成认证值"),
]
y = 4.38
for a, b, c, d in pair:
    card(s, 0.42, y, 12.5, 0.6, SOFT, LINE)
    tb(s, 0.6, y, 1.5, 0.6, a, 14, True, NAVY, mid=True)
    tb(s, 2.15, y, 4.2, 0.6, b, 13, False, INK, mid=True)
    tb(s, 6.45, y, 4.35, 0.6, c, 13, False, INK, mid=True)
    tb(s, 10.9, y, 1.9, 0.6, d, 13, True, TEAL, mid=True)
    y += 0.66
takeaway(s, "同一份 P&ID 里只能出现一套口径。混用宣传区间与 OEM 查表值，是最常见的评审退回原因。", "r")

# ================= 12 章节页 3 =================
section(3, "产品能否达标", "先看架构与输入条件，再看铭牌、二次侧与工厂能力", 12)

# ================= 13 通用链路 =================
figure_slide(
    CH3, "通用链路给出层级，但液气比是 70/30，不是 GB300 口径", 13,
    os.path.join(AI, "ai_ready_p02.png"),
    ["*机柜：液冷 70% + 风冷 30%",
     "机房：风侧房间 / 列间 / 背板 / 风墙；液侧液液 XDU 60–1350 kW",
     "室外：高温走冷却塔或干冷器，低温走冷机",
     "CDU 在图上正好是 TCS 与 FWS 的分界，本身不是冷源"],
    "原图：液冷底座 p.3「数据中心制冷链路」",
    "a", "这张图适合讲层级与产品覆盖；讲 GB300 保证点时必须换成 90/10。")

# ================= 14 架构树 + 高低温 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH3, "架构先分同源 / 非同源，再决定高温自然冷还是低温冷机", 14)
card(s, 0.42, 1.2, 6.15, 4.35, WHITE, LINE)
pic(s, os.path.join(AI, "ai_ready_p05.png"), 0.5, 1.28, 5.99, 4.05)
tb(s, 0.52, 5.36, 5.95, 0.24, "原图：底座 p.6「冷板液冷系统架构：设计」", 9.5, False, MUTED)
card(s, 6.77, 1.2, 6.15, 4.35, WHITE, LINE)
pic(s, os.path.join(AI, "ai_ready_p06.png"), 6.85, 1.28, 5.99, 4.05)
tb(s, 6.87, 5.36, 5.95, 0.24, "原图：底座 p.7「高温—低温转换」", 9.5, False, MUTED)
four = [
    ("同源高温", "干冷器 / 冷却塔 + 双冷源 + 液液 CDU", TEAL),
    ("同源低温", "冷机 20–28℃ 配冷冻水末端；30–38℃ 配水冷末端", BLUE),
    ("无水路线", "风冷冷凝器 + 风机盘管 + 氟液 CDU", AMBER),
    ("非同源", "液冷与风冷各走一套冷源，自由组合", DEEP),
]
for i, (t, d, col) in enumerate(four):
    x = 0.42 + i * 3.16
    card(s, x, 5.66, 2.98, 0.66, SOFT, LINE)
    rect(s, x, 5.66, 0.08, 0.66, col)
    tb(s, x + 0.18, 5.66, 0.95, 0.66, t, 12.5, True, col, mid=True)
    tb(s, x + 1.15, 5.66, 1.72, 0.66, d, 10.5, False, INK, mid=True)
takeaway(s, "GB300 生产基线走液液 CDU；氟液无水是另一产品线，右图「二次侧加小冷机」是升级路径不是现状。", "b")

# ================= 15 五项输入 =================
figure_slide(
    CH3, "五项设计输入是厂商门槛，OEM 查表值优先级更高", 15,
    os.path.join(AI, "ai_ready_p09.png"),
    ["*过滤 <50 μm；流体 25–45℃；比流量 1.0–1.5 L/min·kW",
     "工质选择决定冲洗、检测与排气难度",
     "故障维护强调预防与检测，而非事后抢修",
     "热管理链：芯片 → 机柜集热 → 列间集热 → 室外散热",
     "对照：OEM 表 0.39–1.18 L/min·kW；OCP 主过滤 25–44 μm"],
    "原图：液冷底座 p.10「设计输入条件」",
    "a", "这五项适合做厂商准入清单；具体数值以 OEM ICD 与 OCP 指标为准。")

# ================= 16 全链路实物 =================
figure_slide(
    CH3, "对手卖的是链路：从冷源到柜内歧管都有产品件", 16,
    os.path.join(CC, "coolchip_p03.png"),
    ["*风液共存机房：通用微模块 + 算力微模块 + 浸没试点",
     "链路：冷机 / 冷塔 → 泵 → CDU（集中或分布、风液或液液）",
     "→ 列间不锈钢环管 SFN → 液冷机柜（手插或盲插）",
     "柜内：机柜 + PDU 或直流母排 + In-Rack Manifold",
     "评价这类供应商不能只比 CDU 铭牌 kW"],
    "原图：CoolChip 方案册 p.3–4 跨页（品牌与产品名已去除）",
    "t", "链路完整度是真实竞争力：缺环管、缺换液工装的方案，SAT 阶段才会暴露。")

# ================= 17 L2A / L2L =================
figure_slide(
    CH3, "铭牌能核：L2A 一档 70 kW，L2L 从 4U 直接跳到半柜", 17,
    os.path.join(CC, "coolchip_p05.png"),
    ["*L2A 70 kW：进风 25℃、供液 42℃，改造与试点用",
     "*L2L：30 / 121 为矮机架，450 / 600 / 1350 为立柜（1350 三泵）",
     "全系一次 5–40℃、二次 10–45℃；DI 水或 PG25",
     "接口 1″ 到 4″ 卫生卡盘，自动补液",
     "照片上就能看出 121 与 450 之间没有中间机型"],
    "原图：CoolChip 方案册 p.7–8（柜门标识已遮盖）",
    "a", "GB300 单柜按 150 kW 选型：121 kW 偏紧，450 kW 浪费，正好落在产品空档里。")

# ================= 18 二次侧 =================
figure_slide(
    CH3, "可用性做在二次侧：歧管、环管、故障半径与换液", 18,
    os.path.join(CC, "coolchip_p06.png"),
    ["*歧管：304 方管，6 / 12 / 18 口，UQD08 / UQD04 / UQDB04",
     "*环管 SFN：流量均分、定位漏检、单机柜故障半径、模块预制",
     "机柜：手插 600×1200/1400×2000；盲插整柜 600×1200×2200",
     "移动换液车：在线排 / 充 / 过滤，失压与过压保护",
     "Lenovo GB300 公开 UQDB04，接头族可对，口数仍须 ICD"],
    "原图：CoolChip 方案册 p.9–10（页眉页脚品牌已去除）",
    "t", "CDU 冗余只解决单点；故障半径由环管阀门与漏检分区决定，这才是停机范围。")

# ================= 19 7MW 参考设计 =================
figure_slide(
    CH3, "参考设计已到 7 MW：液气 72/28，单柜 130 kW", 19,
    os.path.join(AI, "ai_ready_p10.png"),
    ["*6×1.2 MW SuperPOD，总 IT 6912 kW，冷却 N+1",
     "*每 POD 1152 kW：液 832 kW（72%）+ 风 320 kW（28%）",
     "48 台 130 kW 算力柜 + 48 台 14 kW 配套柜",
     "CDU 用 1350 级；风侧列间；冷机独立；冷却 UPS 240 kVA 2N",
     "供电 4 取 3，算力柜 8 台 33 kVA 电源架"],
    "原图：液冷底座 p.11「关注 2：成熟的设计方案」（型号标识保留于表内）",
    "b", "这是 130 kW 柜的方案，不是 155 kW 柜的方案：搬到 GB300 必须重算台数与 N+1。")

# ================= 20 交付与 FAT =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH3, "工厂能力：预制到 48 英尺，厂验按 1:1 复制现场", 20)
card(s, 0.42, 1.2, 6.15, 4.4, WHITE, LINE)
pic(s, os.path.join(AI, "ai_ready_p11.png"), 0.5, 1.28, 5.99, 4.1)
tb(s, 0.52, 5.42, 5.95, 0.24, "原图：底座 p.12「关注 3：快速可靠交付」", 9.5, False, MUTED)
card(s, 6.77, 1.2, 6.15, 4.4, WHITE, LINE)
pic(s, os.path.join(AI, "ai_ready_p13.png"), 6.85, 1.28, 5.99, 4.1)
tb(s, 6.87, 5.42, 5.95, 0.24, "原图：底座 p.14「实战案例：液冷 SuperPod 项目」", 9.5, False, MUTED)
facts = [
    ("预制单元", "结构 2400×2000 → 单元 3500×2000 → 48 英尺整段", TEAL),
    ("周期", "50 MW / 20 POD 宣称 80–120 天，对比行业平均 6 个月", BLUE),
    ("厂验", "1.6 MW SuperPOD 1:1 FAT；含缓冲、膨胀、冲洗、减振套件", DEEP),
]
for i, (t, d, col) in enumerate(facts):
    x = 0.42 + i * 4.22
    card(s, x, 5.72, 4.04, 0.6, SOFT, LINE)
    rect(s, x, 5.72, 0.08, 0.6, col)
    tb(s, x + 0.18, 5.72, 1.15, 0.6, t, 13, True, col, mid=True)
    tb(s, x + 1.4, 5.72, 2.5, 0.6, d, 11, False, INK, mid=True)
takeaway(s, "缓冲罐、膨胀罐、冲洗套件在彩页上不出现，却决定 90 秒窗口与 SAT 能否通过——按 FAT 原图列清单。", "t")

# ================= 21 能力阶梯 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH3, "颗粒分布：单柜 150–250 kW 是全行业最薄的一段", 21)
tb(s, 0.42, 1.2, 12.5, 0.3, "公开铭牌冷量（未统一端温差，仅示意数量级）", 12.5, False, MUTED)
bars = [
    ("70", 70, "L2A", MUTED), ("121", 121, "矮机架", MUTED),
    ("150", 150, "GB300 单柜", RED), ("200", 200, "CHx200 4U", TEAL),
    ("450", 453, "立柜", MUTED), ("600", 600, "立柜", MUTED),
    ("800", 800, "行级", MUTED), ("1350", 1368, "行级", MUTED),
    ("2000", 2000, "OCP 2 MW", BLUE), ("2300", 2300, "顶档", MUTED),
    ("2500", 2500, "超大", AMBER),
]
base_y, max_h = 5.05, 3.0
import math
for i, (label, val, note, col) in enumerate(bars):
    x = 0.62 + i * 1.13
    h = max_h * (math.log10(val) - 1.6) / (math.log10(2500) - 1.6)
    h = max(0.25, h)
    rect(s, x, base_y - h, 0.78, h, col)
    tb(s, x - 0.1, base_y - h - 0.38, 0.98, 0.34, label, 13, True, col, PP_ALIGN.CENTER)
    tb(s, x - 0.18, base_y + 0.08, 1.14, 0.6, note, 10.5, False, MUTED, PP_ALIGN.CENTER)
rect(s, 0.55, base_y, 12.3, 0.02, LINE)
card(s, 0.42, 5.62, 6.15, 0.68, PALE_R, RED)
tb(s, 0.62, 5.62, 5.8, 0.68, "空档：中国册 121 → 450，中间无行级 SKU；GB300 单柜正在此段。",
   13.5, False, INK, mid=True)
card(s, 6.77, 5.62, 6.15, 0.68, PALE_T, TEAL)
tb(s, 6.97, 5.62, 5.8, 0.68, "补位者：CoolIT CHx200（200 kW / 4U）、柜内 250 kW 路线。",
   13.5, False, INK, mid=True)
takeaway(s, "选型别被两头的大数字带走：工厂颗粒已到 2–2.5 MW，真正缺的是单柜 200 kW 级成熟机型。", "r")

# ================= 22 竞品 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH3, "竞品各占一段：单柜、行级、超大与国产总包", 22)
peers = [
    ("链路最全", "CoolChip 系列", "L2A 70；L2L 100/121/450/600/1350/2300（4℃ ATD）。柜、歧管、环管、换液、补冷同族。",
     "Modbus 为主，Redfish 需网关", TEAL),
    ("单柜补位", "CoolIT CHx", "CHx200 200 kW / 4U；CHx1500 1364 kW；CHx2000 2000 kW @5℃ ATD、750×1200。",
     "宣称单台带 12×GB300，仍须 N+1", BLUE),
    ("超大颗粒", "Schneider · Motivair", "MCDU-70 单台 2.5 MW，六台 4+2 可撑 10 MW；线宽 105 kW–2.5 MW。",
     "不补单柜 200 kW 空档", DEEP),
    ("国产全链", "英维克", "机架 15–115 kW、机柜 50–1800 kW；漏检 0.1 mL/min；NVIDIA NPN Tier1；2 MW 对标 OCP。",
     "份额与认证以厂商披露为准", AMBER),
    ("国产总包", "申菱 · 华为", "申菱 CDU300 支持 150 kW 柜；华为 L450MA 450/360 kW、二次 270 目、扬程 250/180 kPa。",
     "华为二次侧常用 EG，与 PG25 不同表", MUTED),
]
y = 1.25
for tag, name, spec, warn, col in peers:
    card(s, 0.42, y, 12.5, 1.0, SOFT, LINE)
    rect(s, 0.42, y, 0.09, 1.0, col)
    tb(s, 0.62, y, 1.5, 1.0, tag, 14, True, col, mid=True)
    tb(s, 2.2, y + 0.1, 2.15, 0.8, name, 15, True, NAVY, mid=True)
    tb(s, 4.45, y + 0.08, 5.35, 0.85, spec, 12.5, False, INK, mid=True)
    tb(s, 10.0, y + 0.08, 2.75, 0.85, warn, 11.5, False, MUTED, mid=True)
    y += 1.07
takeaway(s, "横比前先统一四项：端温差、工质、两侧流量与压差、过滤精度。裸 kW 对比没有意义。", "b")

# ================= 23 市场位置 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH3, "市场结构：头部集中，价值量集中在冷板、快接头与 CDU", 23)
tb(s, 0.42, 1.2, 12.5, 0.3,
   "以下为第三方研究与财经媒体口径（2025–2026），非审计数据，用于判断供应格局，不作商务依据", 12, False, MUTED)
share = [("CDU 全球第一梯队", "约 29.6%", "CDU 细分份额，2025 口径", TEAL),
         ("国产 CDU 龙头", "约 9.5%", "全球 CDU 份额，已获 NPN Tier1", BLUE),
         ("前五厂商合计", "近 90%", "全球数据中心 CDU 集中度", DEEP),
         ("国内智算 CDU", "排名第一", "赛迪 2024 中国液冷数据中心口径", AMBER)]
for i, (k, v, d, col) in enumerate(share):
    x = 0.42 + i * 3.16
    card(s, x, 1.6, 2.98, 1.75, SOFT, LINE)
    rect(s, x, 1.6, 2.98, 0.06, col)
    tb(s, x + 0.18, 1.76, 2.62, 0.3, k, 12.5, True, NAVY)
    tb(s, x + 0.18, 2.1, 2.62, 0.55, v, 24, True, col, mid=True)
    tb(s, x + 0.18, 2.72, 2.62, 0.55, d, 11, False, MUTED)
tb(s, 0.42, 3.62, 12.5, 0.32, "冷板液冷系统成本结构（研究口径）", 14, True, NAVY)
cost = [("冷板", 32, TEAL), ("快接头", 28, BLUE), ("CDU", 25, DEEP), ("管阀件", 10, MUTED), ("冷却液", 5, AMBER)]
x0 = 0.42
for name, pct, col in cost:
    w = 12.5 * pct / 100.0
    rect(s, x0, 4.02, w, 0.72, col)
    tb(s, x0, 4.02, w, 0.72, f"{name} {pct}%", 13, True, WHITE, PP_ALIGN.CENTER, mid=True)
    x0 += w
notes = [
    "CDU 只占系统价值约四分之一，冷板与快接头合计 60%——只谈 CDU 品牌会漏掉一半风险。",
    "头部集中意味着交付档期与产能优先级本身就是选型变量，不只是价格。",
    "国产厂商已从部件走向系统总包，并出现对标 OCP 2 MW 的机型，可作双源策略备选。",
]
bullets(s, 0.5, 4.95, 12.3, 1.35, notes, 13.5, INK, 7)
takeaway(s, "供应策略与技术选型同权：单柜级选成熟机型，工厂级留双源，接头与冷板要单独立规。", "b")

# ================= 24 章节页 4 =================
section(4, "怎么选", "按场景定形态，按 OEM 校核，按禁止事项守住底线", 24)

# ================= 25 场景选型 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH4, "按场景选形态，不按品牌口号", 25)
sel = [
    ("实验室 / 风改液 / 无一次水", "L2A 列间或侧车", "70 kW 级", "不得用 L2A 承诺满配训练"),
    ("单柜或 1+1 生产柜", "200–250 kW L2L", "CHx200、柜内 250 kW 路线", "不得用 121 kW 硬扛 155 kW 峰值"),
    ("单列 2–4 柜", "450–800 kW 列间 + N+1", "450 / 600 / 800 级", "不得一台 450 带 4 柜且无备机"),
    ("SuperPOD 约 8 柜", "1.3–2.5 MW 行级 + 群控", "1350 / 2000 / 2300 / 2500", "不得用「一台带 8 柜」替代 N+1 计算"),
    ("国内设计院出图", "上述硬件 + GB 50174 A 级 + 行标", "均流 ≤10%、换热 95%", "不得只贴英文页，须给国标条款"),
]
rect(s, 0.42, 1.28, 12.5, 0.56, DEEP)
for a, b, c, d in [("场景", "推荐形态", "公开颗粒", "禁止事项")]:
    tb(s, 0.6, 1.28, 3.3, 0.56, a, 14, True, WHITE, mid=True)
    tb(s, 4.0, 1.28, 2.9, 0.56, b, 14, True, WHITE, mid=True)
    tb(s, 7.0, 1.28, 2.5, 0.56, c, 14, True, WHITE, mid=True)
    tb(s, 9.6, 1.28, 3.15, 0.56, d, 14, True, WHITE, mid=True)
y = 1.9
for a, b, c, d in sel:
    card(s, 0.42, y, 12.5, 0.85, SOFT, LINE)
    tb(s, 0.6, y, 3.3, 0.85, a, 13.5, True, NAVY, mid=True)
    tb(s, 4.0, y, 2.9, 0.85, b, 13.5, False, INK, mid=True)
    tb(s, 7.0, y, 2.5, 0.85, c, 13, False, MUTED, mid=True)
    tb(s, 9.6, y, 3.15, 0.85, d, 12.5, False, RED, mid=True)
    y += 0.9
takeaway(s, "先确定场景与故障域，再挑颗粒：同一 kW 在不同场景里对应完全不同的冗余与管网做法。", "t")

# ================= 26 GB300 校核 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH4, "对 GB300 逐项校核：能力对得上，颗粒与口径要换", 26)
chk = [
    ("单柜功率", "155 kW 峰值包络", "L2L 支持 100 kW+；121 偏紧、450 浪费", "换颗粒", RED),
    ("液 / 气", "90 / 10，风侧必留", "冷板 50–95% + 补冷三组合", "换口径", RED),
    ("水温与流量", "25–45℃ 成对查表", "二次侧产品窗 10–45℃ 可覆盖", "对齐", TEAL),
    ("工质", "DI 或 PG25", "DI、25% 丙二醇及兼容液", "对齐", TEAL),
    ("漏液联锁", "Tray + Rack 触点", "柜 + CDU + 环管全路径监测", "需硬接线", AMBER),
    ("接头", "盲插 UQDB04", "UQD08 / UQD04 / UQDB04 可选", "口数待 ICD", AMBER),
    ("可用性", "A 级 / Tier 3", "双泵双电源 + 环管单柜故障半径", "补 CDU 列 N+1", AMBER),
]
rect(s, 0.42, 1.24, 12.5, 0.52, DEEP)
for a, b, c, d in [("校核项", "GB300 冻结口径", "产品族能力", "结论")]:
    tb(s, 0.6, 1.24, 2.0, 0.52, a, 13.5, True, WHITE, mid=True)
    tb(s, 2.7, 1.24, 3.3, 0.52, b, 13.5, True, WHITE, mid=True)
    tb(s, 6.1, 1.24, 4.6, 0.52, c, 13.5, True, WHITE, mid=True)
    tb(s, 10.8, 1.24, 1.95, 0.52, d, 13.5, True, WHITE, mid=True)
y = 1.82
for a, b, c, d, col in chk:
    card(s, 0.42, y, 12.5, 0.64, SOFT, LINE)
    tb(s, 0.6, y, 2.0, 0.64, a, 13.5, True, NAVY, mid=True)
    tb(s, 2.7, y, 3.3, 0.64, b, 13, False, INK, mid=True)
    tb(s, 6.1, y, 4.6, 0.64, c, 13, False, INK, mid=True)
    tb(s, 10.8, y, 1.95, 0.64, d, 13, True, col, mid=True)
    y += 0.69
takeaway(s, "七项里四项要动作：换颗粒、换口径、硬接联锁、补列级冗余。能力不是问题，配置是。", "b")

# ================= 27 风险与行动 =================
s = prs.slides.add_slide(BLANK)
chrome(s, CH4, "四条禁止事项 + 四项待办，收口", 27)
tb(s, 0.42, 1.22, 6.15, 0.34, "禁止事项", 16, True, RED)
forb = [
    "把宣传冷量相加，或用裸 kW 横比不同 ATD 的机型",
    "用 70/30 或 72/28 替换 GB300 的 90/10，据此取消风侧",
    "用 1.0–1.5 L/min·kW 反代 OEM Table 27 的查表流量",
    "把「一台 CDU 带 8 或 12 柜」的宣传当作 N+1 结论",
]
card(s, 0.42, 1.6, 6.15, 2.45, PALE_R, RED)
bullets(s, 0.62, 1.78, 5.75, 2.15, forb, 13.5, INK, 9)
tb(s, 6.77, 1.22, 6.15, 0.34, "待办与待补", 16, True, TEAL)
todo = [
    "取授权数据表：二次扬程、精确过滤目数、群控点数",
    "按 OCP 六项写评标模板，锁 ATD 与压差工况",
    "单柜 200 kW 级做双源比对，含国产对标机型",
    "把缓冲、膨胀、冲洗、换液口写进 P&ID 与 FAT 清单",
]
card(s, 6.77, 1.6, 6.15, 2.45, PALE_T, TEAL)
bullets(s, 6.97, 1.78, 5.75, 2.15, todo, 13.5, INK, 9)
tb(s, 0.42, 4.2, 12.5, 0.34, "材料与置信度", 16, True, NAVY)
conf = [
    ("高", "两份原图（按页渲染核对）、OCP Deschutes 规格、ASHRAE W 类定义、Lenovo LP2357、厂商数据表", TEAL),
    ("中高", "官方新闻稿与官网产品页（口径随时间变动，须按发布日引用）", BLUE),
    ("中", "媒体转述的份额、成本结构与「单台带 N 柜」类表述，仅作格局判断", AMBER),
]
y = 4.6
for lv, d, col in conf:
    card(s, 0.42, y, 12.5, 0.56, SOFT, LINE)
    tb(s, 0.6, y, 1.0, 0.56, lv, 14, True, col, mid=True)
    tb(s, 1.7, y, 11.0, 0.56, d, 13, False, INK, mid=True)
    y += 0.6
takeaway(s, "结论可直接进选型评审；进采购保证前，须由 OEM ICD 与厂家授权数据表逐项复核。", "b")

out = r"d:\agents2026\agents2026\agents\AIDCtms\solutions\行业液冷产品对标分析_v2.0_20260905.pptx"
prs.save(out)
print("saved", out, "slides", len(prs.slides))
