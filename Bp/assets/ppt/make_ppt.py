# -*- coding: utf-8 -*-
"""
算力冷却商业调研报告 v3.2 演示版 —— PPTX 生成脚本
数据来源：《算力冷却商业调研报告_v3.2_20260822.html》（唯一数据源，不得增改）
        《算力冷却系统新业务BP_v2.1_20260822.html》（商业口径参照）
图片：同目录 c01–c26 PNG，由 make_charts.py 生成，全部以内嵌方式写入 pptx。
运行： python make_charts.py && python make_ppt.py
"""
import os
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
BP_DIR = os.path.dirname(os.path.dirname(HERE))
OUT_PPTX = os.path.join(BP_DIR, "算力冷却商业调研报告_v3.2_演示版_20260905.pptx")

# ---------- 主色系（延续报告 #0b2239 / #175cd3 / #087a70） ----------
NAVY = RGBColor(0x0B, 0x22, 0x39)
BLUE = RGBColor(0x17, 0x5C, 0xD3)
TEAL = RGBColor(0x08, 0x7A, 0x70)
RED = RGBColor(0xB4, 0x23, 0x18)
AMBER = RGBColor(0x9A, 0x67, 0x00)
GREY = RGBColor(0x5D, 0x68, 0x7A)
DARKTX = RGBColor(0x33, 0x41, 0x5A)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LINE = RGBColor(0xD8, 0xDF, 0xE8)
BGBLUE = RGBColor(0xEA, 0xF1, 0xFD)
BGTEAL = RGBColor(0xF2, 0xFB, 0xF7)
BGRED = RGBColor(0xFF, 0xF7, 0xF6)
BGAMBER = RGBColor(0xFF, 0xF7, 0xE8)
BGGREY = RGBColor(0xF6, 0xF8, 0xFA)

FONT = "Microsoft YaHei"

SW, SH = 13.3333, 7.5
ML, MR = 0.55, 0.55
CW = SW - ML - MR          # 12.2333
TITLE_Y = 0.36
RULE_Y = 1.08
BODY_Y = 1.20
BODY_H = 5.78
FOOT_Y = 7.06

VERSION = "v3.2 Evidence-led"
CUTOFF = "数据截止 2026-08-22"
CONF = "机密 · 仅供董事会与核心团队"

prs = Presentation()
prs.slide_width = Inches(SW)
prs.slide_height = Inches(SH)
BLANK = prs.slide_layouts[6]

_page = [0]


# ---------------- 基础工具 ----------------
def tb(slide, x, y, w, h, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP):
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.NONE
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    tf.vertical_anchor = anchor
    tf.paragraphs[0].alignment = align
    return box, tf


def para(tf, text, size=12, color=DARKTX, bold=False, align=PP_ALIGN.LEFT,
         space_after=4, space_before=0, first=False, line=1.25, italic=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.space_before = Pt(space_before)
    p.line_spacing = line
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.bold = bold
    r.font.italic = italic
    r.font.color.rgb = color
    r.font.name = FONT
    return p


def rect(slide, x, y, w, h, fill=None, linec=None, lw=1.0, shape=MSO_SHAPE.RECTANGLE):
    s = slide.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
    if fill is None:
        s.fill.background()
    else:
        s.fill.solid()
        s.fill.fore_color.rgb = fill
    if linec is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = linec
        s.line.width = Pt(lw)
    s.shadow.inherit = False
    s.text_frame.word_wrap = True
    s.text_frame.margin_left = Inches(0.10)
    s.text_frame.margin_right = Inches(0.10)
    s.text_frame.margin_top = Inches(0.06)
    s.text_frame.margin_bottom = Inches(0.06)
    return s


def hline(slide, x, y, w, color=LINE, lw=1.0):
    s = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(x), Inches(y),
                               Inches(w), Pt(lw))
    s.fill.solid()
    s.fill.fore_color.rgb = color
    s.line.fill.background()
    s.shadow.inherit = False
    return s


def footer(slide, n):
    _, tf = tb(slide, ML, FOOT_Y, CW * 0.42, 0.26)
    para(tf, f"算力冷却商业调研报告 · {VERSION} · {CUTOFF}", 8, GREY, first=True)
    _, tf = tb(slide, ML + CW * 0.42, FOOT_Y, CW * 0.34, 0.26, align=PP_ALIGN.CENTER)
    para(tf, CONF, 8, RED, first=True, align=PP_ALIGN.CENTER)
    _, tf = tb(slide, ML + CW * 0.78, FOOT_Y, CW * 0.22, 0.26, align=PP_ALIGN.RIGHT)
    para(tf, f"{n}", 9, GREY, bold=True, first=True, align=PP_ALIGN.RIGHT)


def _title_size(title, avail_pt=CW * 72, base=21.0):
    """估算标题宽度（CJK 计 1 个字宽、ASCII 计 0.55），必要时逐级缩小以保证单行。"""
    units = sum(1.0 if ord(c) > 0x2E7F else 0.55 for c in title)
    for size in (base, 19.5, 18.0, 16.5):
        if units * size <= avail_pt * 0.985:
            return size
    return 16.5


def new_slide(eyebrow, title, title_color=NAVY):
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    if eyebrow:
        _, tf = tb(s, ML, 0.16, CW, 0.22)
        para(tf, eyebrow, 9.5, BLUE, bold=True, first=True)
    _, tf = tb(s, ML, TITLE_Y, CW, 0.66)
    para(tf, title, _title_size(title), title_color, bold=True, first=True, line=1.12)
    hline(s, ML, RULE_Y, CW, LINE, 1.2)
    hline(s, ML, RULE_Y, 1.5, BLUE, 2.4)
    footer(s, _page[0])
    return s


def add_image(slide, fname, top, max_h, max_w=CW, left=None):
    """按比例缩放并居中嵌入 PNG（嵌入而非外链）。返回实际高度。"""
    path = os.path.join(HERE, fname)
    with Image.open(path) as im:
        iw, ih = im.size
    ratio = iw / ih
    h = max_h
    w = h * ratio
    if w > max_w:
        w = max_w
        h = w / ratio
    x = left if left is not None else (SW - w) / 2
    slide.shapes.add_picture(path, Inches(x), Inches(top), Inches(w), Inches(h))
    return w, h


def takeaway(slide, y, lines, color=BLUE, bg=BGBLUE, h=None):
    """标题下方的要点条：正文 ≤ 5 行。"""
    n = len(lines)
    hh = h if h else 0.16 + n * 0.235
    box = rect(slide, ML, y, CW, hh, bg, None)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    tf.margin_top = Inches(0.07)
    for i, t in enumerate(lines):
        para(tf, t, 11.5, DARKTX if i else color, bold=(i == 0), first=(i == 0),
             space_after=2, line=1.2)
    return y + hh


def chart_slide(eyebrow, title, img, lines, note=None, color=BLUE, bg=BGBLUE):
    s = new_slide(eyebrow, title)
    y = takeaway(s, BODY_Y, lines, color, bg)
    extra = 0.30 if note else 0.0
    _, h = add_image(s, img, y + 0.12, BODY_Y + BODY_H - y - 0.16 - extra)
    if note:
        _, tf = tb(s, ML, BODY_Y + BODY_H - 0.26, CW, 0.24, align=PP_ALIGN.CENTER)
        para(tf, note, 9, RED, bold=True, first=True, align=PP_ALIGN.CENTER)
    return s


def make_table(slide, x, y, w, col_w, rows, font=9.5, hdr_font=10,
               row_h=0.40, hdr_h=0.36, hdr_fill=NAVY):
    """rows[0] 为表头。最多 6 行 × 5 列。"""
    nr, nc = len(rows), len(rows[0])
    shp = slide.shapes.add_table(nr, nc, Inches(x), Inches(y), Inches(w),
                                 Inches(hdr_h + (nr - 1) * row_h))
    tbl = shp.table
    tbl.first_row = True
    tbl.horz_banding = False
    total = sum(col_w)
    for j, cwj in enumerate(col_w):
        tbl.columns[j].width = Inches(w * cwj / total)
    tbl.rows[0].height = Inches(hdr_h)
    for i in range(1, nr):
        tbl.rows[i].height = Inches(row_h)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cell = tbl.cell(i, j)
            cell.margin_left = Inches(0.08)
            cell.margin_right = Inches(0.06)
            cell.margin_top = Inches(0.04)
            cell.margin_bottom = Inches(0.04)
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.fill.solid()
            if i == 0:
                cell.fill.fore_color.rgb = hdr_fill
            else:
                cell.fill.fore_color.rgb = WHITE if i % 2 else BGGREY
            tf = cell.text_frame
            tf.word_wrap = True
            tf.margin_left = tf.margin_right = Emu(0)
            txt, col, bold = val, DARKTX, False
            if isinstance(val, tuple):
                txt, col = val[0], val[1]
                bold = val[2] if len(val) > 2 else False
            p = tf.paragraphs[0]
            p.line_spacing = 1.14
            r = p.add_run()
            r.text = str(txt)
            r.font.size = Pt(hdr_font if i == 0 else font)
            r.font.bold = True if i == 0 else bold
            r.font.color.rgb = WHITE if i == 0 else col
            r.font.name = FONT
    return shp


# =====================================================================
# 1 封面
# =====================================================================
def slide_cover():
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY, None)
    rect(s, 0, 0, 0.22, SH, BLUE, None)
    rect(s, 0, SH - 0.10, SW, 0.10, TEAL, None)

    _, tf = tb(s, 1.0, 0.85, 11.0, 0.34)
    para(tf, "Commercial Research Report · 演示版 / 20260905", 12, RGBColor(0x8F,
         0xB4, 0xE8), bold=True, first=True)

    _, tf = tb(s, 1.0, 1.30, 11.4, 1.15)
    para(tf, "算力冷却商业调研报告", 44, WHITE, bold=True, first=True, line=1.05)

    _, tf = tb(s, 1.0, 2.50, 11.4, 0.80)
    para(tf, "高密 AI 基础设施液冷：需求、算力基建投资、液冷占比、", 15.5,
         RGBColor(0xC9, 0xD8, 0xFF), first=True, line=1.35)
    para(tf, "工程边界、竞争、准入、项目池与验证期权", 15.5,
         RGBColor(0xC9, 0xD8, 0xFF), line=1.35)

    hline(s, 1.0, 3.52, 11.3, RGBColor(0x2A, 0x47, 0x66), 1.2)

    kpis = [
        ("接近 30 → 约 70 亿美元", "Dell'Oro 全球液冷设备制造商收入\n2025 机构估计 → 2029 机构预测；TAM 主锚"),
        ("0.3%–0.9% ／ 5%–11%", "液冷设备收入占算力基建总投资 ／ 占 DCPI 设备市场\n2025–2032；分母不同则量级完全不同"),
        ("SAM 24m = 无数据", "公开项目尚未同时闭环电力、融资、开工、\n平台、服务与有效价格"),
    ]
    for i, (big, sub) in enumerate(kpis):
        x = 1.0 + i * 3.83
        rect(s, x, 3.75, 3.55, 1.30, RGBColor(0x10, 0x2A, 0x4C), None)
        _, tf = tb(s, x + 0.18, 3.90, 3.20, 0.42)
        para(tf, big, 16, RGBColor(0x7E, 0xC8, 0xBE) if i == 2 else WHITE,
             bold=True, first=True)
        _, tf = tb(s, x + 0.18, 4.36, 3.22, 0.62)
        para(tf, sub, 9, RGBColor(0x9F, 0xB3, 0xCC), first=True, line=1.35)

    meta = [("版本", VERSION), ("数据截止日", "2026-08-22"),
            ("演示日期", "2026-09-05"), ("研究范围", "中国、东南亚、中东及全球对标"),
            ("主边界", "液冷设备制造商收入 / 项目级 CDU"),
            ("配套 BP", "《算力冷却系统新业务BP》v2.1_20260822")]
    for i, (k, v) in enumerate(meta):
        x = 1.0 + (i % 3) * 3.83
        y = 5.25 + (i // 3) * 0.42
        _, tf = tb(s, x, y, 3.55, 0.36)
        p = tf.paragraphs[0]
        p.line_spacing = 1.2
        r = p.add_run(); r.text = k + "："
        r.font.size = Pt(10); r.font.color.rgb = RGBColor(0x6E, 0x86, 0xA6)
        r.font.name = FONT
        r = p.add_run(); r.text = v
        r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = WHITE
        r.font.name = FONT

    rect(s, 1.0, 6.28, 4.05, 0.42, RGBColor(0x5B, 0x14, 0x0E), None)
    _, tf = tb(s, 1.16, 6.37, 3.85, 0.28)
    para(tf, "机密 · 仅供董事会与核心团队讨论", 11, RGBColor(0xFF, 0xC9, 0xC4),
         bold=True, first=True)
    _, tf = tb(s, 5.35, 6.30, 7.0, 0.60)
    para(tf, "本报告不构成证券投资建议、产品认证或采购承诺。总体结论 valid_until 2026-11-30；",
         9, RGBColor(0x8F, 0xA4, 0xBE), first=True, line=1.35)
    para(tf, "第 2.6 / 2.7 章（投资与占比）valid_until 2027-02-28。本演示稿不修改任何既有报告与 BP 文件。",
         9, RGBColor(0x8F, 0xA4, 0xBE), line=1.35)


# =====================================================================
# 2 一页结论
# =====================================================================
def slide_conclusions():
    s = new_slide("结论先行", "需求方向成立，但可得份额、价格、责任与现金回报尚未验证")
    y = takeaway(s, BODY_Y, [
        "当前证据只支持「受客户、工程、责任与现金门禁约束的小规模验证期权」，不支持按行业 CAGR 批准量产扩张。",
        "报告第一层结论共六条，每条均标注置信度与失效条件；下方为原文裁决，未作增补或改写。",
    ], NAVY, BGBLUE)

    items = [
        ("1", "需求方向强，口径不可相加", "设备、整机、宽产业是不同分母，任何两项不得相加",
         "0.92 / 2027-01-31", BLUE),
        ("2", "工程壁垒是平台级适配", "铭牌冷量不能证明平台兼容；水力、材料、冗余与故障态共同决定可用性",
         "0.94 / 2026-11-30", BLUE),
        ("3", "竞争全栈化，增长不保证高毛利", "全球服务、流体管理与责任承担成为壁垒；扩产爬坡与标准化压缩利润",
         "0.90 / 2026-11-15", TEAL),
        ("4", "公开招标不能验证单位经济", "无合格裸机成交价、四 SKU BOM 或故障成本：ASP、毛利、ROIC 均为无数据",
         "0.96 / 正式合同发布即复核", TEAL),
        ("5", "液冷在算力投资中价值占比极低，且高度依赖分母", "占总投资长期不到 1%，占设施侧约 1%–6%，占 DCPI 约 5%–11%",
         "相对量级 0.80；任一点值 0.35 / 2027-02-28", AMBER),
        ("6", "最优策略是验证期权", "只对已获电在建项目、付费 PoC 与可封顶责任释放资金，可限制下行损失",
         "0.88 / 2026-12-31", RED),
    ]
    cw = (CW - 0.30) / 2
    ch = 1.42
    for i, (num, head, body, conf, col) in enumerate(items):
        x = ML + (i % 2) * (cw + 0.30)
        yy = y + 0.16 + (i // 2) * (ch + 0.18)
        rect(s, x, yy, cw, ch, RGBColor(0xFA, 0xFC, 0xFF), LINE, 0.75)
        rect(s, x, yy, 0.055, ch, col, None)
        _, tf = tb(s, x + 0.20, yy + 0.11, 0.34, 0.30)
        para(tf, num, 15, col, bold=True, first=True)
        _, tf = tb(s, x + 0.58, yy + 0.11, cw - 0.78, 0.62)
        para(tf, head, 12.5, NAVY, bold=True, first=True, line=1.18)
        _, tf = tb(s, x + 0.58, yy + 0.66, cw - 0.78, 0.44)
        para(tf, body, 9.8, DARKTX, first=True, line=1.28)
        _, tf = tb(s, x + 0.58, yy + 1.11, cw - 0.78, 0.24)
        para(tf, "置信度 / valid_until：" + conf, 9, col, bold=True, first=True)


# =====================================================================
# 4 口径纪律
# =====================================================================
def slide_discipline():
    s = new_slide("阅读须知（二）", "口径纪律：不同分母不可相加、不可相减、不可用于计算份额")
    y = takeaway(s, BODY_Y, [
        "五层口径互不重叠，包含关系为：液冷设备市场 ⊂ DCPI 热管理 ⊂ DCPI ⊂ L1 ⊂ L3；L2 ⊂ L3；L1 ∩ L2 = ∅。",
        "投资层级 L1 / L2 / L3 自 v3.2 起专指算力基建投资分层，与来源等级（一级/二级/三级）是两套独立编号。",
    ], NAVY, BGBLUE)

    rows = [
        ["口径", "定义", "用途", "禁止事项"],
        [("设备 TAM", NAVY, True), "冷板、CDU、歧管、快接、浸没、RDHx 等制造商收入",
         "全球市场主锚", ("不得与服务器整机或宽产业相加", RED)],
        [("算力基建投资 L1／L2／L3", NAVY, True), "设施侧 CapEx／IT 设备投资／两者之和",
         "液冷占比的分母分层", ("不得与设备 TAM 相加；不得换算为公司收入", RED)],
        [("项目池 SAM", NAVY, True), "24 个月内、五道项目门均闭环且可服务的项目收入",
         "公司可服务市场", ("不得以公告 MW 或服务器台数代替", RED)],
        [("SOM", NAVY, True), "合格项目中经 qualification、订单、交付、服务与回款约束后的可获收入",
         "公司预算", ("不得用 TAM × 目标份额", RED)],
        [("单位经济", NAVY, True), "从净收入扣除完全项目成本并考虑现金占用",
         "量产门禁", ("无报价、合同和试制数据时不得填点值", RED)],
    ]
    make_table(s, ML, y + 0.16, CW, [1.5, 3.4, 1.5, 3.0], rows,
               font=9.5, hdr_font=10.5, row_h=0.56, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.56 + 0.22
    cols = [
        ("① 不可相加", "设备制造商收入、服务器整机、宽产业、总用电、容量 GW 是不同分母", RED, BGRED),
        ("② 不可相减", "需求 219 GW 与供给 200 GW 之差、全液冷 70 亿与 DLC 58 亿之差都不是可交付订单或路线规模", RED, BGRED),
        ("③ 不可算份额", "任何「公司收入 ÷ 上述某一行」得到的比例都不具备可比性，不得进入董事会材料", RED, BGRED),
    ]
    w = (CW - 0.30) / 3
    for i, (h, d, c, bg) in enumerate(cols):
        x = ML + i * (w + 0.15)
        rect(s, x, yy, w, 0.86, bg, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
        _, tf = tb(s, x + 0.14, yy + 0.10, w - 0.28, 0.26)
        para(tf, h, 11.5, c, bold=True, first=True)
        _, tf = tb(s, x + 0.14, yy + 0.38, w - 0.28, 0.44)
        para(tf, d, 9.2, DARKTX, first=True, line=1.3)


# =====================================================================
# 16 三组分母适用场景
# =====================================================================
def slide_denominator_usage():
    s = new_slide("市场篇（十二）", "三组占比各自回答不同的问题 —— 只有组③ 可以谈「份额」")
    y = takeaway(s, BODY_Y, [
        "引用任何一个占比时必须同时写出分母层级与发布版本，否则读者会把两个正确数字当成互相矛盾。",
        "占比高低与新进入者的可得份额之间没有因果关系；分母是全球所有制造商的收入。",
    ], NAVY, BGBLUE)

    rows = [
        ["组 / 分母", "结果", "适用：回答什么问题", "不适用：不能回答什么"],
        [("① L3 算力基建总投资（最宽）", TEAL, True), ("0.3%–0.9%", TEAL, True),
         "在整个 AI 算力投资盘子里，独立液冷设备的价值占多少。适用于向董事会解释「AI 投资巨大」与「液冷可得收入有限」之间的落差",
         ("不适用于评估液冷业务的相对增长性或竞争地位：分母中约 75%–85% 是 IT 设备，与液冷供应商无任何竞争或替代关系", RED)],
        [("② L1 设施侧 CapEx（中等）", BLUE, True), ("1.3%–5.6%", BLUE, True),
         "在数据中心设施建设的每一元里，液冷设备制造商拿到多少。适用于与 EPC、机电总包、配电、UPS 等设施侧品类做相对规模比较",
         ("不适用于推导单个项目的液冷成本占比：L1 是全球混合平均，含大量风冷与非 AI 项目；单个高密 AI 项目的液冷占比远高于此", RED)],
        [("③ DCPI 设备市场（最窄、最可比）", NAVY, True), ("5%–11%", NAVY, True),
         "液冷在物理基础设施设备制造商收入中的结构性权重与趋势。同一机构、同一收入确认规则，液冷是 DCPI 热管理的子集，是三组中唯一可以谈「份额」的分母",
         ("不适用于推导公司可得份额：分母已被 Ecolab/CoolIT、Eaton/Boyd、Schneider/Motivair、Vertiv、Modine 及各 OEM 自供占据", RED)],
    ]
    make_table(s, ML, y + 0.16, CW, [1.9, 1.0, 4.2, 4.2], rows,
               font=9.3, hdr_font=10.5, row_h=1.16, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 3 * 1.16 + 0.20
    box = rect(s, ML, yy, CW, 0.56, BGRED, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "极差约 30 倍：2032 年 0.4%（组①下界）对 11%（组③上界）；2025 年 0.3% 对 9%。",
         11, RED, bold=True, first=True, line=1.22)
    para(tf, "用组③ 的量级去论证组① 的商业空间，会把可得市场高估一个量级以上。",
         10, DARKTX, line=1.22)


# =====================================================================
# 21 平台工程基线
# =====================================================================
def slide_platform_matrix():
    s = new_slide("技术与格局篇（二）", "平台工程基线：铭牌冷量不能证明兼容，五项参数必须同时校核")
    y = takeaway(s, BODY_Y, [
        "只记录同一版本、同一回路可比较的数据；公开未披露即写「无数据」，不得用其他 OEM 参数替代。",
        "选型须同时校核：IT 功率 · HCR/液体热负荷 · TCS/FWS 温度与工质 · Q–ΔP · 冗余与故障态。",
    ], NAVY, BGBLUE)

    rows = [
        ["平台 / 版本", "IT 功率", "液体负荷 / HCR", "TCS 温度 / 工质", "工程裁决"],
        [("Lenovo GB300 NVL72\n2026-08-13 update", NAVY, True), "135 kW TDP\n155 kW peak",
         "约 90%；121.5–139.5 kW\n为本报告推导", "供液 25–45℃；DI water\n或 PG25；回液无数据",
         "当前最完整的一柜曲线；\n项目须确认曲线对应工质"],
        [("Lenovo N1380 / SC750 V4", NAVY, True), "54 kW / enclosure\n三套 162 kW DC",
         ("量热保证无数据；公开架构\n称接近全水冷", RED), "供液 27/32/40/45℃；\n处理洁净水；回液无数据",
         "流量可加，支路压降不可\n相加；HCR 保留条件"],
        [("Huawei Atlas 900 A3", NAVY, True), "计算柜最大 66 kW",
         "约 70%，随配置；46.2 kW\n仅为本报告粗算", "液冷门供液 5–32℃；\n纯水或 EG50；回液无数据",
         ("液冷门回路与计算柜 D2C\n回路不得拼接", RED)],
        [("HPE GB200 NVL72 v4", NAVY, True), "132 kW / rack",
         "115 kW liquid + 17 kW air", ("公开摘要无数据", RED),
         "液体负荷可用，水力须取\nsite readiness 包"],
        [("Dell IR7000 + XE8712", NAVY, True), "特定配置最高\n264 kW / rack",
         ("HCR / 液体 kW 无数据", RED), "28/32/36/40℃；\nDell validated PG25",
         "504 kW 是供电/busbar 生态\n能力，非本配置液体负荷"],
    ]
    make_table(s, ML, y + 0.16, CW, [2.3, 1.6, 2.4, 2.4, 2.6], rows,
               font=8.8, hdr_font=10, row_h=0.63, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.63 + 0.18
    _, tf = tb(s, ML, yy, CW, 0.52)
    para(tf, "NVIDIA DGX GB200（约 120 kW/rack）、Supermicro DLC-2（方案能力最高 250 kW，非固定 IT 铭牌）与 NVIDIA Rubin（原厂路线称 100% 液冷，固定 rack kW 未披露）三项关键字段为无数据，不承诺任何容量档覆盖柜数。",
         9.2, GREY, first=True, line=1.3)
    para(tf, "来源：Lenovo GB300 Product Guide Table 27；N1380 Configuration Guide Tables 1–4；Atlas 900 A3 技术规格；Dell Rack-Scale DLC Guidelines pp.4–5, 18–19。报告表 3.1。",
         9.2, GREY, line=1.3)


# =====================================================================
# 31 单位经济
# =====================================================================
def slide_unit_economics():
    s = new_slide("商业篇（四）", "单位经济现在是一张空模型：填实它需要的是书面证据，不是更好的估计")
    y = takeaway(s, BODY_Y, [
        "100 / 200 / 300 / 450 kW 四个 SKU 的额定工况、ASP、贡献毛利、ROIC 与盈亏平衡当前全部为「无数据」。",
        "「无数据」不得改成 0，不得用二手区间填空，不得用容量在四个 SKU 之间线性插值生成 ASP、BOM 或毛利。",
    ], RED, BGRED)

    rows = [
        ["字段", "四个容量档（100 / 200 / 300 / 450 kW）当前状态", "解锁所需证据"],
        [("额定工况 / 流量 / 压差 / 工质 / 冗余", NAVY, True), ("无数据", RED, True),
         "客户 RFQ + 样机性能矩阵"],
        [("CDU 净 ASP", NAVY, True), ("变量 ASP100 / ASP200 / ASP300 / ASP450", AMBER, True),
         "同边界书面报价或订单；至少两个可比样本"],
        [("BOM（泵、板换、阀、过滤/脱气、PLC/VFD、传感、钣金、管件、工质）", NAVY, True),
         ("询价中", AMBER, True), "每类至少两家书面报价，含 MOQ / 交期 / 质保 / 付款"],
        [("制造与测试（装配、清洗、压力、气密、FAT、良率、返工）", NAVY, True),
         ("待实测", AMBER, True), "至少三批试制工时、一次通过率与返修记录"],
        [("贡献毛利 / ROIC / 盈亏平衡", NAVY, True), ("无数据", RED, True),
         "以上字段全部解锁后才计算"],
    ]
    make_table(s, ML, y + 0.16, CW, [3.4, 4.0, 4.6], rows,
               font=9.5, hdr_font=10.5, row_h=0.56, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.56 + 0.20
    w = (CW - 0.20) / 2
    box = rect(s, ML, yy, w, 0.94, BGGREY, LINE, 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "两条公式（报告 12.2）", 10.5, NAVY, bold=True, first=True)
    para(tf, "CM_i = 净收入 − BOM − 制造/FAT − 安装/SAT − 物流/税/保险 − 渠道/EPC − 质保 − 坏账/LD",
         9.2, DARKTX, line=1.32)
    para(tf, "现金调整后贡献 = CM_i − 保函融资费用 − 营运资金成本", 9.2, DARKTX, line=1.32)

    box = rect(s, ML + w + 0.20, yy, w, 0.94, BGRED, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "隔离条款", 10.5, RED, bold=True, first=True)
    para(tf, "2.6 / 2.7 章的每 MW 投资强度是设施与 IT 的宏观造价包络，不得当作 CDU ASP 或部件价值。",
         9.2, DARKTX, line=1.32)
    para(tf, "现金模型按周计算，传统 CCC 只作摘要，不能替代里程碑现金流。", 9.2, DARKTX, line=1.32)


# =====================================================================
# 33 反命题
# =====================================================================
def slide_counterarguments():
    s = new_slide("风险与结论（一）", "五条反命题决定这笔投资是否成立 —— 每条都配有先行指标与自动动作")
    y = takeaway(s, BODY_Y, [
        "内部阈值是管理门禁，不代表行业事实，须由董事会、客户合同与试制数据持续校准。",
    ], RED, BGRED)

    rows = [
        ["风险 / 反命题", "概率 / 影响", "先行指标", "内部阈值与自动动作"],
        [("并网 / 施工延期", NAVY, True), ("高 / 高", RED, True),
         "接电协议、NTP、施工里程碑",
         "缺电力、开工、平台任两项：移出 24 个月 SAM"],
        [("Hyperscaler CapEx 放缓", NAVY, True), ("中 / 高", AMBER, True),
         "四大云厂商指引与资产减值；IDC AI 基础设施季度修正方向",
         "连续两季显著下修：冻结二期扩产，并把 2.6 章情景切换到 A-基准 / A-受限"],
        [("OEM 指定 / 垂直整合", NAVY, True), ("高 / 高", RED, True),
         "RFQ 中指定 CDU 或 AVL 的比例",
         "多数目标项目排除独立供应商：转 ODM、部件或服务"],
        [("价格降幅快于成本", NAVY, True), ("高 / 高", RED, True),
         "同工况 RFQ / 合同价、完全成本",
         "现金调整后贡献持续为负：停止扩产并重定价"],
        [("重大漏液 / 失流", NAVY, True), ("中 / 极高", RED, True),
         "FAT/SAT 缺陷、现场告警、质保索赔",
         "重大事件：停发货、隔离批次、8D 与保险通知"],
    ]
    make_table(s, ML, y + 0.16, CW, [2.2, 1.2, 3.6, 5.2], rows,
               font=9.5, hdr_font=10.5, row_h=0.62, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.62 + 0.20
    _, tf = tb(s, ML, yy, CW, 0.66)
    para(tf, "另有五条同等重要的反命题（报告第 11 章）：算力投资融资条件收紧、回款与营运资金、GPU 许可 / 项目合规、水 / PFAS / F-gas 约束、来源口径与版本漂移。",
         10, DARKTX, first=True, line=1.35)
    para(tf, "六条核心结论各自的 invalidate_if 与本表互为补充：结论 5 的失效条件为 IDC 连续两季下修 AI 支出、Dell'Oro 再次重划 DCPI 边界、JLL 单位建设成本转降。",
         10, GREY, line=1.35)


# =====================================================================
# 34 季度跟踪
# =====================================================================
def slide_tracking():
    s = new_slide("风险与结论（二）", "季度跟踪清单：先行指标一旦触发，模型与资金动作是预先约定的")
    y = takeaway(s, BODY_Y, [
        "跟踪的目的是让模型失效可被提前发现，而不是事后解释。新版发布即复核，禁止跨版本拼接序列。",
    ], NAVY, BGBLUE)

    rows = [
        ["跟踪对象", "先行指标", "频率", "触发的模型 / 管理动作"],
        [("投运晚于管线", NAVY, True), "获电、NTP、施工、延迟率、并网周期", ("季度", BLUE, True),
         "下调新增投运与改造；不把 announced MW 计入 SAM"],
        [("AI 份额 / 密度偏低", NAVY, True), "AI 服务器与整柜出货、平均液冷 kW、推理占比",
         ("季度 / 平台代际", BLUE, True), "下调采用率与价值 / MW"],
        [("价格与垂直整合", NAVY, True), "同工况报价、OEM 指定率、制造商收入 ÷ 液冷 MW",
         ("半年", BLUE, True), "区分瓦数增长与收入增长"],
        [("来源边界漂移", NAVY, True), "Dell'Oro、JLL、IEA、IDC、McKinsey 新版定义",
         ("新版即复核", RED, True), "禁止跨版本拼序列，重设端点并重估三组占比"],
        [("公司侧证据", NAVY, True), "付费 PoC、同边界合同价、试制批次、DSO / 峰值资金",
         ("月度 / 每周现金", BLUE, True), "达标才解锁阶段 2/3；未达自动冻结招聘与非关键 CapEx"],
    ]
    make_table(s, ML, y + 0.16, CW, [2.2, 4.2, 1.6, 4.2], rows,
               font=9.5, hdr_font=10.5, row_h=0.60, hdr_h=0.34)

    yy = y + 0.16 + 0.34 + 5 * 0.60 + 0.22
    w = (CW - 0.20) / 2
    box = rect(s, ML, yy, w, 0.94, BGBLUE, RGBColor(0xC9, 0xD8, 0xFF), 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "有效期与复核触发", 10.5, BLUE, bold=True, first=True)
    para(tf, "总体结论 valid_until 2026-11-30；2.6 / 2.7 章 valid_until 2027-02-28。",
         9.4, DARKTX, line=1.32)
    para(tf, "并购方新季报、平台新 revision、正式招标合同、项目状态变化或重大可靠性事故将提前触发复核。",
         9.4, DARKTX, line=1.32)

    box = rect(s, ML + w + 0.20, yy, w, 0.94, BGAMBER, RGBColor(0xF0, 0xD9, 0xA8), 0.75)
    tf = box.text_frame
    tf.margin_left = Inches(0.16)
    para(tf, "研究充分性", 10.5, AMBER, bold=True, first=True)
    para(tf, "SUFFICIENT WITH LIMITATIONS —— 足以重写报告，不等于商业参数或量产可行性已验证。",
         9.4, DARKTX, line=1.32)
    para(tf, "继续泛搜不替代管理层线下取证。", 9.4, DARKTX, line=1.32)


# =====================================================================
# 35 结论与下一步
# =====================================================================
def slide_next_steps():
    s = new_slide("风险与结论（三）", "下一步不是扩大研究，而是取得七类线下书面证据 —— 在此之前保持无数据")
    y = takeaway(s, BODY_Y, [
        "本轮可批准：阶段 1 上限 800 万元内的架构、样机、付费 PoC、供应链 / NPI、软件 / IP 与责任验证。",
        "本轮不可批准：无订单扩产、无 NRE 开发冷板专线、无限责任项目、按 TAM 份额倒推收入。",
    ], NAVY, BGBLUE)

    w = (CW - 0.24) / 2
    yy = y + 0.18

    box = rect(s, ML, yy, w, 4.16, RGBColor(0xFA, 0xFC, 0xFF), LINE, 0.75)
    rect(s, ML, yy, w, 0.42, NAVY, None)
    _, tf = tb(s, ML + 0.16, yy + 0.09, w - 0.32, 0.26)
    para(tf, "待线下取得的证据清单（报告 12.3）", 11.5, WHITE, bold=True, first=True)
    _, tf = tb(s, ML + 0.16, yy + 0.62, w - 0.32, 3.44)
    todos = [
        ("价格", "至少两个同工况、同冗余、同质保的正式分项中标或合同价；预算与限价不替代"),
        ("BOM", "四 SKU 的泵、板换、UQD、PLC/VFD、阀件、过滤/脱气、钣金与工质，每类至少两家书面报价"),
        ("客户", "至少两个 OEM/客户项目 qualification 包，确认 PoC 收费、周期、转量产、平台边界与独立 CDU 准入"),
        ("合同", "至少一份 CDU/EPC 分包合同，含验收、付款、漏液/停机/数据损失、责任上限、保险、PBG 与质保"),
        ("项目池", "逐项目补齐接电、融资、NTP、平台/BOM、柜数、投运批次与本地服务"),
        ("试制", "至少三批工时、良率、FAT 一次通过率、返修、现场故障与质保成本数据"),
        ("投资口径", "取得 Dell'Oro DCPI 与液冷付费报告的逐年表与边界说明、IDC 分项、JLL 地区/密度拆分"),
    ]
    for i, (k, v) in enumerate(todos):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.24
        p.space_after = Pt(4)
        r = p.add_run(); r.text = f"{i+1}. {k}　"
        r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = BLUE
        r.font.name = FONT
        r = p.add_run(); r.text = v
        r.font.size = Pt(9.6); r.font.color.rgb = DARKTX; r.font.name = FONT

    x2 = ML + w + 0.24
    box = rect(s, x2, yy, w, 2.00, BGTEAL, RGBColor(0xB6, 0xE4, 0xD2), 0.75)
    rect(s, x2, yy, w, 0.42, TEAL, None)
    _, tf = tb(s, x2 + 0.16, yy + 0.09, w - 0.32, 0.26)
    para(tf, "90 / 180 / 365 日行动（BP v2.1 第 14 章）", 11.5, WHITE, bold=True, first=True)
    _, tf = tb(s, x2 + 0.16, yy + 0.62, w - 0.32, 1.30)
    for k, v in [("0–90 日", "冻结阶段 1 URS、架构、BSW 边界、DVP 与 100/200 kW 样机计划；发四 SKU 统一 RFQ；G0 包"),
                 ("91–180 日", "工程样机、MIL/SIL/HIL、性能矩阵、故障注入；制造商 NPI/FAI；至少一个付费 PoC"),
                 ("181–365 日", "两台代表样机可靠性与客户 SAT；≥2 付费验证；两个同边界合同价；G1 决策")]:
        p = tf.paragraphs[0] if k.startswith("0") else tf.add_paragraph()
        p.line_spacing = 1.22
        p.space_after = Pt(3)
        r = p.add_run(); r.text = f"{k}　"
        r.font.size = Pt(10); r.font.bold = True; r.font.color.rgb = TEAL
        r.font.name = FONT
        r = p.add_run(); r.text = v
        r.font.size = Pt(9.4); r.font.color.rgb = DARKTX; r.font.name = FONT

    box = rect(s, x2, yy + 2.14, w, 2.02, BGRED, RGBColor(0xF6, 0xC8, 0xC5), 0.75)
    rect(s, x2, yy + 2.14, w, 0.42, RED, None)
    _, tf = tb(s, x2 + 0.16, yy + 2.23, w - 0.32, 0.26)
    para(tf, "在 PPT 中保持「无数据」的项目", 11.5, WHITE, bold=True, first=True)
    _, tf = tb(s, x2 + 0.16, yy + 2.76, w - 0.32, 1.32)
    para(tf, "SAM 24m · SOM · CDU 净 ASP · 四 SKU BOM 与毛利 · 贡献毛利 / ROIC / 盈亏平衡 · CDU 有效能力矩阵（四档 × 四工况）· 现金跑道",
         9.6, DARKTX, first=True, line=1.34)
    para(tf, "已删除且不予恢复：市场份额、前五集中度、部件价值占比、通用毛利率、CDU 静态 ASP、SAM/SOM 亿元点值、固定 PUE 区间、MTBF 与「零外漏」。",
         9.6, RED, line=1.34)

    _, tf = tb(s, ML, yy + 4.32, CW, 0.30, align=PP_ALIGN.CENTER)
    para(tf, "最终裁决：购买一个「下行封顶、证据逐步解锁」的验证期权，而不是按行业 CAGR 批准量产扩张。",
         12, NAVY, bold=True, first=True, align=PP_ALIGN.CENTER)


# =====================================================================
# 封底
# =====================================================================
def slide_back():
    _page[0] += 1
    s = prs.slides.add_slide(BLANK)
    rect(s, 0, 0, SW, SH, NAVY, None)
    rect(s, 0, 0, SW, 0.10, TEAL, None)
    _, tf = tb(s, 1.2, 2.35, 11.0, 0.70)
    para(tf, "算力冷却商业调研报告 · v3.2 Evidence-led", 28, WHITE, bold=True, first=True)
    _, tf = tb(s, 1.2, 3.12, 11.0, 0.40)
    para(tf, "演示版 / 20260905　·　数据截止 2026-08-22　·　配套《算力冷却系统新业务BP》v2.1_20260822",
         13, RGBColor(0xC9, 0xD8, 0xFF), first=True)
    hline(s, 1.2, 3.75, 10.9, RGBColor(0x2A, 0x47, 0x66), 1.2)
    _, tf = tb(s, 1.2, 3.98, 11.0, 1.60)
    for t in ["本演示稿由《算力冷却商业调研报告 v3.2》整理而成，全部数据取自该报告正文，未引入报告中没有的数字，",
              "未恢复报告已删除的伪精确点值。所有图表为本演示稿自绘（matplotlib + python-pptx），不含任何来源不明的外部图片。",
              "本材料不构成证券投资建议、产品认证或采购承诺。总体结论 valid_until 2026-11-30；投资与占比章节 valid_until 2027-02-28。"]:
        para(tf, t, 11, RGBColor(0x9F, 0xB3, 0xCC), first=(t.startswith("本演示稿由")),
             line=1.6)
    rect(s, 1.2, 5.80, 4.4, 0.44, RGBColor(0x5B, 0x14, 0x0E), None)
    _, tf = tb(s, 1.38, 5.90, 4.2, 0.28)
    para(tf, "机密 · 仅供董事会与核心团队讨论", 11.5, RGBColor(0xFF, 0xC9, 0xC4),
         bold=True, first=True)
    _, tf = tb(s, SW - 2.2, 5.90, 1.6, 0.28, align=PP_ALIGN.RIGHT)
    para(tf, f"{_page[0]}", 11, RGBColor(0x6E, 0x86, 0xA6), bold=True, first=True,
         align=PP_ALIGN.RIGHT)


# =====================================================================
# 组装
# =====================================================================
def build():
    slide_cover()
    slide_conclusions()

    chart_slide("阅读须知（一）", "两套独立标签体系：来源等级决定证据力，数据性质决定这个数字是什么",
                "c20_evidence_pyramid.png",
                ["全文每个数字都同时带来源等级与数据性质；机构端点、本报告桥接与本报告情景必须能被一眼区分。",
                 "「无数据」是一种裁决结果，不是遗漏 —— 报告中共有 SAM/SOM、ASP、毛利、ROIC、CDU 能力矩阵等多处保持无数据。"])

    slide_discipline()

    chart_slide("市场篇（一）", "需求方向没有争议：用电五年翻倍、容量需求五年增 1.7 倍，但三条曲线分母不同",
                "c01_power_capacity.png",
                ["2025 → 2030 机构端点：用电 485 → 950 TWh（IEA）；关键 IT 需求 82 → 219 GW（McKinsey）；设施供给 103 → 200 GW（JLL）。",
                 "需求 219 GW 高于供给 200 GW 不等于订单缺口：两者定义、基准、时点、占用与可交付性不同，不可相减。"])

    chart_slide("市场篇（二）", "机柜功率密度在一代内从 66 kW 跃到 264 kW —— 风冷延寿空间被物理压缩",
                "c02_rack_power.png",
                ["Dell'Oro 称「1 MW 机柜正在临近」；NVIDIA Rubin 路线称 100% 液冷，Vera Rubin 计算托盘取消风扇。",
                 "但铭牌功率不是采购依据：Supermicro 250 kW 与 Dell 264 kW 分别是方案移热能力与特定配置最高值，口径不同。"])

    chart_slide("市场篇（三）", "真正约束液冷需求的不是规划容量，而是每年实际投运的 10–28 GW",
                "c03_new_commissioned.png",
                ["JLL：2025 年 57% 项目延迟至少 3 个月，主要市场并网平均等待超过 4 年；C&W：全球大负荷平均供电周期 4.4 年。",
                 "管理动作：在建与规划 pipeline 不计入当年投运，也不计入任何 SAM；项目预算只跟随已获电、已开工、平台已冻结的批次。"],
                note="逐年投运量无任何机构发布 —— 全部为本报告由 JLL 累计端点桥接的模型值。")

    chart_slide("市场篇（四）", "AI 占存量容量约 25% → 50%，但占新增容量高达 76% —— 两个分母差一倍",
                "c04_ai_share.png",
                ["v3.1 曾把存量份额当作新增份额使用；v3.2 已在表 2.5.2 列名中标明「存量口径」，并单列 65%–82% 的新增份额序列。",
                 "这一区分直接决定自下而上模型的 IT 腿：用错分母会把液冷相关容量低估近一半。"])

    chart_slide("市场篇（五）", "算力基建总投资 2025 年约 6,500–8,050 亿美元，2030 年约 1.64–2.05 万亿美元",
                "c05_capex_layers.png",
                ["先分层再谈占比：不同机构所称的「数据中心投资」相差十倍以上，主因是层级不同而非数据冲突。",
                 "使用边界（强制）：本序列仅用于外部市场锚定与情景分析，不得换算为公司收入预算、SAM/SOM、产能规划、ASP 或毛利率。"],
                note="confidence 0.72 / valid_until 2027-02-28　·　机构只发布累计口径，全部年度序列为本报告模型")

    chart_slide("市场篇（六）", "两条独立路径交叉验证后的裁决：McKinsey 6.7 万亿基准情景已过时，改用加速情景",
                "c06_path_ab.png",
                ["路径 B 的 IT 腿自下而上低估约 36%（容量法 2,040 亿 vs IDC 实测 3,180 亿），四项原因逐条披露，不取平均掩盖。",
                 "处置：L1 以路径 B 为主锚（设施侧有 JLL、Epoch AI、Turner & Townsend 三个独立每 MW 证据），L2 以 IDC 实测为主锚。"],
                note="反向风险：加速情景依赖 AI 投资回报持续被市场接受；若 2027 年融资收紧，实际路径可能快速回落到 A-基准甚至 A-受限。")

    chart_slide("市场篇（七）", "四大厂商 CapEx 只作旁证：它证伪了基准情景，但不能除以 L3 得「份额」",
                "c14_hyperscaler_capex.png",
                ["四家使用三种不同 CapEx 定义，含办公、网络骨干、自研芯片预付等非数据中心支出，与全球 L3 口径不同。",
                 "四家之外还有 Oracle、xAI、CoreWeave、字节、阿里、腾讯与主权 AI 项目等大量投资主体，因此该表不得相加进 L3。"],
                color=AMBER, bg=BGAMBER)

    chart_slide("市场篇（八）", "液冷设备市场：2029 年约 70 亿美元合理，但整条曲线只有两个机构端点",
                "c07_lc_scenarios.png",
                ["三重合理性校验（宏观占比、容量强度、机柜强度）均通过量级检查，但都不能独立闭环 —— 只能作异常检查。",
                 "董事会外部 TAM 采用 2032 年 90–140 亿美元（本报告模型），Base 约 115 亿；不是机构预测、不是 CDU SAM/SOM、不是公司可得收入。"],
                note="invalidate_if：Dell'Oro 新版偏离 2029 年 60–80 亿美元；2027–2028 已获电投运或 AI 液冷采用显著落后；设备价格年降幅 >15% 且瓦数/配置不能抵消。")

    chart_slide("市场篇（九）", "Dell'Oro 的四个版本必须隔离：70 − 58 = 12 不是浸没与 RDHx 的规模",
                "c08_delloro_versions.png",
                ["这是本报告最关键的方法论纪律之一：三个数字分属三个发布版本、三个边界，底层逐年表与方法为付费内容，不可见。",
                 "禁止：母子精确拆分、跨版本相减、连成连续年度曲线、拼成一条占比序列。新版发布即重设端点。"],
                color=RED, bg=BGRED)

    chart_slide("市场篇（十）", "液冷占比取决于分母，同一年三个比例相差约 30 倍",
                "c09_three_denominators.png",
                ["同一个分子（液冷设备制造商收入），换三个分母：占 L3 约 0.3%–0.9%，占 L1 约 1.3%–5.6%，占 DCPI 约 5%–11%。",
                 "任何引用必须同时写出分母层级与来源版本。只写「液冷约占 10%」或「液冷不到 1%」都是误导。"],
                color=RED, bg=BGRED,
                note="相对量级 confidence 0.80；任一年份的任一点值 confidence 0.35 —— 禁止点值引用。")

    chart_slide("市场篇（十一）", "同一个分子、同一年，换 Dell'Oro 的版本就从 10%–13% 变成 5%–8%",
                "c10_version_sensitivity.png",
                ["变化几乎全部来自 Dell'Oro 扩大 DCPI 边界并上调预测，不是液冷竞争地位下降。",
                 "v3.1 正文的「2029 液冷约占旧版 DCPI 631 亿美元的 10%–13%」仍然正确 —— 但只在旧版口径下正确。"],
                color=AMBER, bg=BGAMBER)

    slide_denominator_usage()

    chart_slide("市场篇（十三）", "设施侧「液冷投入」是设备制造商收入的 5–6 倍 —— 差额被 EPC 与安装截留",
                "c11_facility_vs_manufacturer.png",
                ["这解释了工程口径与市场口径的表面矛盾：「液冷占 AI 机房造价 15%–33%」是项目造价科目，与本报告的 1%–6% 不在同一分母。",
                 "对本业务的含义：能进入独立设备供应商可争夺池子的，只有右侧那一段。"])

    chart_slide("市场篇（十四）", "占比不是稳定参数：四项推高、四项压低、一项方向不确定",
                "c25_share_drivers.png",
                ["2030 年组①、组② 同时出现台阶，主要来自 Dell'Oro 新版 DLC「超过 80 亿美元」造成的预测版本跳点，不解释为有机改善。",
                 "其中「OEM/ODM 垂直整合」与「设施侧 EPC 吃掉价值」两项对独立供应商的杀伤最直接。"])

    chart_slide("技术与格局篇（一）", "技术路线按成熟度三分：只有第一层已产品化，后两层不给性能点值",
                "c23_tech_routes.png",
                ["主边界是冷板式直接液冷（CDU、冷板、Manifold、UQD、工质、二次管路、控制、安装调试与流体运维）。",
                 "浸没、两相与设施侧冷源只作相邻路线比较，不进入本报告的收入分母。"])

    slide_platform_matrix()

    chart_slide("技术与格局篇（三）", "供液温度从 25℃ 升到 45℃：流量约 3 倍，压降约 8 倍",
                "c12_qdp_curve.png",
                ["这是当前公开资料中最完整的一柜 Q–ΔP 曲线，也是「铭牌冷量不能证明兼容」最直观的证据。",
                 "项目必须确认曲线对应的工质（DI water 或 PG25）；不同 OEM 的流量与压降不可互相套用，支路压降不可相加。"])

    chart_slide("技术与格局篇（四）", "CDU 卖的是可验证系统与责任闭环，不是铭牌 kW",
                "c17_cdu_schematic.png",
                ["有效冷量随 ATD、供回液温度、工质、泵故障态、海拔与污堵变化，必须以矩阵而非单点表述。",
                 "控制层（应用控制算法、状态机、故障降级、BMS/DCIM 接口、远程诊断）是本业务自留的高附加值环节。"])

    chart_slide("技术与格局篇（五）", "容量档不是兼容承诺：四档 × 四类工况的有效能力当前全部为无数据",
                "c26_cdu_matrix_na.png",
                ["这不是资料收集不足，而是尚无样机热性能与 PQ 矩阵；解锁条件是客户 RFQ 加样机实测，不是更多公开检索。",
                 "在矩阵填实之前，任何「我们的 300 kW CDU 支持某平台」的表述都不成立。"],
                color=RED, bg=BGRED)

    chart_slide("技术与格局篇（六）", "竞争已全栈化：三笔并购把液冷装进了水处理、电力与预制模块的全栈组合里",
                "c24_competition.png",
                ["壁垒已从设备转向全球服务、流体管理与责任承担；新进入者要面对的是组合方案，不是单机比价。",
                 "所有可比数字必须按四层严格分列，不以集团收入或集团毛利冒充液冷收入或毛利。"])

    chart_slide("技术与格局篇（七）", "唯一可用的纯液冷毛利实绩：冷板 10.36%，与浸没 36.49% 相差三倍",
                "c13_margin_evidence.png",
                ["这是报告中仅有的、口径较纯的历史可比毛利证据，也是「增长不保证高毛利」的直接支撑。",
                 "不得据此推导任何其他公司的 CDU 毛利率：报告已删除通用毛利率点值，且公开证据不足以恢复。"],
                color=AMBER, bg=BGAMBER)

    chart_slide("技术与格局篇（八）", "不存在公开可验证的统一 CDU 认证 —— 准入是逐项目的九步 qualification",
                "c21_qualification_chain.png",
                ["NPN 是伙伴计划，NVIDIA-Certified Systems 面向整机；华为有公司级供应商体系，但未公开 Atlas CDU 完整名录。",
                 "营销材料只可写具体项目、具体平台、具体版本的 qualification 状态，不得写「已获大厂认证」。"],
                color=RED, bg=BGRED)

    chart_slide("商业篇（一）", "把资本压在微笑曲线两端：中段的器件、基础软件与制造交给受控供应商",
                "c16_smile_curve.png",
                ["自留七项价值控制点：需求权、架构权、版本权、变更权、放行权、数据权、客户权。",
                 "外协不转移最终责任：ISO 9001 外部过程控制原则与产品质量法都要求本公司保留最终放行、品牌与客户责任。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（二）", "商业三步走：2027 启动，800 / 1,200 / 1,500 万元是阶段上限而非承诺额度",
                "c18_roadmap.png",
                ["阶段 2、3 是条件期权。只有订单、贡献、回款、可靠性与现金跑道同时达标才解锁，缺一即冻结。",
                 "外部投资增速与液冷占比上升均不构成解锁条件 —— 这是市场章节与资金章节之间的硬隔离。"],
                color=TEAL, bg=BGTEAL)

    chart_slide("商业篇（三）", "行业 TAM 增长推导不出公司收入：中间横着五道项目门和六个断点",
                "c19_tam_sam_som.png",
                ["六个断点：分母、可交付、准入、价格、现金、模型。任何一个都足以让「TAM × 目标份额」失效。",
                 "SAM 24m 与 SOM 当前均为无数据 —— 不是 0，而是公开可核验的合格项目尚未闭环。"],
                color=RED, bg=BGRED)

    slide_unit_economics()

    chart_slide("商业篇（五）", "资金门禁 G0–G3：证据不到位，钱就不出去",
                "c22_gates.png",
                ["每道门同时约束工程、商业、质量、责任、现金与组织六个维度，任一硬门未达即自动冻结。",
                 "阶段上限与外部 TAM 无关，不因市场情景上修而调整。"],
                color=TEAL, bg=BGTEAL)

    slide_counterarguments()
    slide_tracking()
    slide_next_steps()
    slide_back()

    prs.save(OUT_PPTX)
    print("saved:", OUT_PPTX)
    print("slides:", len(prs.slides.__iter__.__self__._sldIdLst))


if __name__ == "__main__":
    build()
