# -*- coding: utf-8 -*-
"""
GB300 NVL72 液冷系统综合汇报 PPT 生成脚本（幂等，可重复运行）

输入依据：GB300_NVL72液冷系统综合研究报告_v1.0_20260905.html（六份源报告的综合）
输出：
  1) ppt_assets/*.png      —— matplotlib 生成的全部图表
  2) GB300_NVL72液冷系统综合汇报_v1.0_20260905.pptx

运行： python _make_gb300_total_ppt.py
"""

import math
import os
import sys
from pathlib import Path

try:  # Windows 控制台默认 GBK，强制 UTF-8 以免自检报告报错
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.ns import qn
from pptx.util import Emu, Inches, Pt
from lxml import etree

# ---------------------------------------------------------------- 全局常量

BASE = Path(__file__).resolve().parent
ASSETS = BASE / "ppt_assets"
OUT_PPTX = BASE / "GB300_NVL72液冷系统综合汇报_v1.0_20260905.pptx"

FONT = "微软雅黑"
DOC_NAME = "GB300 NVL72 液冷系统综合汇报 v1.0 · 2026-09-05"

NAVY = RGBColor(0x0B, 0x27, 0x48)
BLUE = RGBColor(0x17, 0x69, 0xE0)
DEEPBLUE = RGBColor(0x17, 0x4F, 0x83)
TEAL = RGBColor(0x00, 0x8B, 0x7A)
ORANGE = RGBColor(0xA6, 0x5B, 0x00)
RED = RGBColor(0xB4, 0x23, 0x18)
SOFT = RGBColor(0xF6, 0xF9, 0xFC)
LINE = RGBColor(0xD7, 0xE0, 0xEC)
INK = RGBColor(0x18, 0x25, 0x36)
MUTED = RGBColor(0x60, 0x70, 0x86)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
PALE_BLUE = RGBColor(0xEE, 0xF5, 0xFF)
PALE_TEAL = RGBColor(0xE6, 0xF6, 0xF2)
PALE_RED = RGBColor(0xFD, 0xE8, 0xE6)
PALE_ORG = RGBColor(0xFF, 0xF3, 0xD6)

SW, SH = 13.333, 7.5
MARG = 0.62
CW = SW - 2 * MARG          # 12.093 内容宽度
BODY_TOP = 1.78
BODY_BOT = 6.72
BODY_H = BODY_BOT - BODY_TOP

# matplotlib 中文
plt.rcParams["font.sans-serif"] = ["Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["figure.dpi"] = 170
plt.rcParams["savefig.dpi"] = 170

HEX = lambda c: "#%02X%02X%02X" % (c[0], c[1], c[2])
C_NAVY, C_BLUE, C_TEAL = "#0B2748", "#1769E0", "#008B7A"
C_ORG, C_RED, C_LINE = "#A65B00", "#B42318", "#D7E0EC"
C_MUTED, C_SOFT = "#607086", "#F6F9FC"

_overflow_notes = []


# ---------------------------------------------------------------- 字体工具

def set_font(run, size=14, bold=False, color=INK, font=FONT, italic=False):
    """同时设置 latin / ea / cs 字体，避免中文回退成方框或宋体。"""
    f = run.font
    f.size = Pt(size)
    f.bold = bold
    f.italic = italic
    f.color.rgb = color
    f.name = font
    rPr = run._r.get_or_add_rPr()
    latin = rPr.find(qn("a:latin"))
    if latin is None:
        latin = etree.SubElement(rPr, qn("a:latin"))
    latin.set("typeface", font)
    for tag in ("a:ea", "a:cs"):
        el = rPr.find(qn(tag))
        if el is None:
            el = etree.Element(qn(tag))
            latin.addnext(el) if tag == "a:ea" else rPr.append(el)
        el.set("typeface", font)


def textbox(slide, l, t, w, h, anchor=MSO_ANCHOR.TOP):
    tb = slide.shapes.add_textbox(Inches(l), Inches(t), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Emu(0)
    tf.margin_top = tf.margin_bottom = Emu(0)
    return tb, tf


def put(tf, text, size=14, bold=False, color=INK, align=PP_ALIGN.LEFT,
        space_before=0, space_after=4, line_spacing=1.28, first=False):
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_before = Pt(space_before)
    p.space_after = Pt(space_after)
    p.line_spacing = line_spacing
    r = p.add_run()
    r.text = text
    set_font(r, size, bold, color)
    return p


def put_rich(tf, chunks, size=14, align=PP_ALIGN.LEFT, space_after=4,
             line_spacing=1.28, first=False):
    """chunks = [(text, bold, color, size_override or None), ...]"""
    p = tf.paragraphs[0] if first else tf.add_paragraph()
    p.alignment = align
    p.space_after = Pt(space_after)
    p.line_spacing = line_spacing
    for txt, bold, color, sz in chunks:
        r = p.add_run()
        r.text = txt
        set_font(r, sz or size, bold, color)
    return p


def no_shadow(sh):
    try:
        sh.shadow.inherit = False
    except Exception:
        spPr = sh._element.spPr
        el = etree.SubElement(spPr, qn("a:effectLst"))
    return sh


def rrect(slide, l, t, w, h, fill=None, line=None, line_w=1.0, radius=0.10,
          shape=MSO_SHAPE.ROUNDED_RECTANGLE):
    sh = slide.shapes.add_shape(shape, Inches(l), Inches(t), Inches(w), Inches(h))
    if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
        try:
            sh.adjustments[0] = radius
        except Exception:
            pass
    if fill is None:
        sh.fill.background()
    else:
        sh.fill.solid()
        sh.fill.fore_color.rgb = fill
    if line is None:
        sh.line.fill.background()
    else:
        sh.line.color.rgb = line
        sh.line.width = Pt(line_w)
    no_shadow(sh)
    tf = sh.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = Inches(0.10)
    tf.margin_top = tf.margin_bottom = Inches(0.05)
    tf.vertical_anchor = MSO_ANCHOR.MIDDLE
    return sh


def sq(slide, l, t, w, h, fill, line=None, line_w=1.0):
    return rrect(slide, l, t, w, h, fill, line, line_w, shape=MSO_SHAPE.RECTANGLE)


def arrow(slide, l, t, w, h, color=RED, direction="right"):
    shp = MSO_SHAPE.RIGHT_ARROW if direction == "right" else MSO_SHAPE.DOWN_ARROW
    sh = slide.shapes.add_shape(shp, Inches(l), Inches(t), Inches(w), Inches(h))
    sh.fill.solid()
    sh.fill.fore_color.rgb = color
    sh.line.fill.background()
    no_shadow(sh)
    return sh


# ---------------------------------------------------------------- 版式骨架

class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width = Inches(SW)
        self.prs.slide_height = Inches(SH)
        self.blank = self.prs.slide_layouts[6]
        self.n = 0

    def new(self, footer=True):
        s = self.prs.slides.add_slide(self.blank)
        self.n += 1
        if footer:
            self.add_footer(s)
        return s

    def add_footer(self, slide):
        sq(slide, MARG, 6.86, CW, 0.012, LINE)
        _, tf = textbox(slide, MARG, 6.96, 8.0, 0.3)
        put(tf, DOC_NAME, 10, False, MUTED, first=True, space_after=0)
        _, tf2 = textbox(slide, SW - MARG - 2.0, 6.96, 2.0, 0.3)
        put(tf2, "%02d" % self.n, 10.5, True, NAVY, align=PP_ALIGN.RIGHT,
            first=True, space_after=0)

    def header(self, slide, kicker, title, accent=BLUE):
        """页面标题 = 这一页的结论句。"""
        sq(slide, MARG, 0.46, 0.075, 0.90, accent)
        _, tf = textbox(slide, MARG + 0.22, 0.44, CW - 0.3, 0.28)
        put(tf, kicker, 11, True, accent, first=True, space_after=0)
        size = 27 if len(title) <= 26 else (24 if len(title) <= 34 else 21)
        _, tf2 = textbox(slide, MARG + 0.22, 0.74, CW - 0.3, 0.66)
        put(tf2, title, size, True, NAVY, first=True, space_after=0,
            line_spacing=1.16)
        sq(slide, MARG, 1.54, CW, 0.012, LINE)

    def note(self, slide, text, color=MUTED, top=None, icon=None):
        top = top if top is not None else 6.34
        _, tf = textbox(slide, MARG, top, CW, 0.40)
        put(tf, text, 10.5, False, color, first=True, space_after=0,
            line_spacing=1.28)


DECK = Deck()


# ---------------------------------------------------------------- 内容组件

def add_title_slide(title, subtitle, pills, meta):
    s = DECK.new(footer=False)
    DECK.n = 1
    sq(s, 0, 0, SW, SH, NAVY)
    sq(s, 0, 0, SW, 0.10, BLUE)
    _, tf = textbox(s, 1.05, 1.42, 11.0, 0.32)
    put(tf, "INTEGRATED SYSTEM STUDY  ·  GB300 NVL72 LIQUID COOLING", 12,
        True, RGBColor(0x8F, 0xB6, 0xE6), first=True, space_after=0)
    _, tf = textbox(s, 1.05, 1.92, 11.2, 1.5)
    put(tf, title, 40, True, WHITE, first=True, space_after=0, line_spacing=1.18)
    sq(s, 1.05, 3.42, 1.6, 0.05, TEAL)
    _, tf = textbox(s, 1.05, 3.70, 10.8, 1.0)
    put(tf, subtitle, 16.5, False, RGBColor(0xD7, 0xE6, 0xF5), first=True,
        space_after=0, line_spacing=1.42)
    x = 1.05
    for p in pills:
        w = 0.20 + len(p) * 0.135
        sh = rrect(s, x, 4.86, w, 0.40, None, RGBColor(0x5E, 0x87, 0xB8), 1.0, 0.5)
        put(sh.text_frame, p, 11.5, False, RGBColor(0xD7, 0xE6, 0xF5),
            align=PP_ALIGN.CENTER, first=True, space_after=0)
        x += w + 0.16
    _, tf = textbox(s, 1.05, 5.72, 11.0, 0.9)
    for i, m in enumerate(meta):
        put(tf, m, 12.5, i == 0, RGBColor(0x9F, 0xC2, 0xE8) if i else WHITE,
            first=(i == 0), space_after=3)
    return s


def add_kpi_slide(kicker, title, kpis, bullets=None, note=None, accent=BLUE):
    """kpis = [(value, unit, label, color), ...] 2~4 个；正文可选。"""
    s = DECK.new()
    DECK.header(s, kicker, title, accent)
    n = len(kpis)
    gap = 0.26
    w = (CW - gap * (n - 1)) / n
    h = 2.20 if bullets else 2.85
    top = BODY_TOP + (0.05 if bullets else 0.55)
    for i, (val, unit, label, col) in enumerate(kpis):
        x = MARG + i * (w + gap)
        rrect(s, x, top, w, h, SOFT, LINE, 1.0, 0.06)
        sq(s, x, top, w, 0.075, col)
        vsize = 46 if len(val) <= 4 else (38 if len(val) <= 7 else 31)
        _, tf = textbox(s, x + 0.16, top + 0.42, w - 0.32, 0.95)
        put_rich(tf, [(val, True, col, vsize),
                      ("  " + unit if unit else "", True, col, 16)],
                 first=True, space_after=0, line_spacing=1.0)
        _, tf = textbox(s, x + 0.16, top + 1.34 if not bullets else top + 1.30,
                        w - 0.32, h - 1.42)
        for j, ln in enumerate(label if isinstance(label, list) else [label]):
            put(tf, ln, 13, j == 0, NAVY if j == 0 else MUTED, first=(j == 0),
                space_after=3, line_spacing=1.30)
    if bullets:
        add_point_cards(s, bullets, top=top + h + 0.24,
                        bottom=BODY_BOT - (0.30 if note else 0.0))
    if note:
        DECK.note(s, note)
    return s


def add_point_cards(slide, items, top=BODY_TOP, bottom=BODY_BOT, cols=1,
                    lead_size=15, body_size=13.2, colors=None):
    """items = [(lead, body)] 或 [lead]。每卡 1~2 行，最多 6 张。"""
    items = [(it, "") if isinstance(it, str) else it for it in items]
    n = len(items)
    rows = math.ceil(n / cols)
    gap = 0.16
    w = (CW - gap * (cols - 1)) / cols
    h = min(1.15, (bottom - top - gap * (rows - 1)) / rows)
    # 卡片偏矮时自动收字号，保证「每点不超过 2 行」且不溢出卡片
    if h < 0.70:
        lead_size, body_size = 13.0, 11.4
    elif h < 0.80:
        lead_size, body_size = 13.8, 12.0
    elif h < 0.92:
        lead_size, body_size = 14.4, 12.6
    pal = colors or [BLUE, TEAL, ORANGE, DEEPBLUE, RED, NAVY]
    for i, (lead, body) in enumerate(items):
        r, c = divmod(i, cols)
        x = MARG + c * (w + gap)
        y = top + r * (h + gap)
        col = pal[i % len(pal)]
        rrect(slide, x, y, w, h, SOFT, LINE, 1.0, 0.06)
        sq(slide, x, y, 0.065, h, col)
        _, tf = textbox(slide, x + 0.24, y + 0.11, w - 0.42, h - 0.18)
        put(tf, lead, lead_size, True, NAVY, first=True, space_after=2,
            line_spacing=1.20)
        if body:
            put(tf, body, body_size, False, MUTED, space_after=0,
                line_spacing=1.26)
    return top + rows * (h + gap) - gap


def add_bullet_slide(kicker, title, items, note=None, accent=BLUE, cols=1,
                     colors=None):
    s = DECK.new()
    DECK.header(s, kicker, title, accent)
    bottom = BODY_BOT - (0.34 if note else 0.0)
    add_point_cards(s, items, BODY_TOP + 0.10, bottom, cols=cols, colors=colors)
    if note:
        DECK.note(s, note)
    return s


def place_image(slide, png, left, top, max_w, max_h):
    """按可用框等比缩放并居中，避免压到页脚。"""
    from PIL import Image
    pw, ph = Image.open(str(png)).size
    ar = ph / pw
    w = max_w
    h = w * ar
    if h > max_h:
        h = max_h
        w = h / ar
    slide.shapes.add_picture(str(png), Inches(left + (max_w - w) / 2),
                             Inches(top + (max_h - h) / 2),
                             width=Inches(w), height=Inches(h))
    return w, h


def add_chart_slide(kicker, title, png, side=None, note=None, accent=BLUE,
                    img_w=None, img_box_h=None):
    """图优先：整幅图 + 右侧要点条（可选）。"""
    s = DECK.new()
    DECK.header(s, kicker, title, accent)
    bottom = BODY_BOT - (0.36 if note else 0.0)
    if img_box_h:
        bottom = min(bottom, BODY_TOP + 0.02 + img_box_h)
    if side:
        iw = img_w or 8.55
        place_image(s, png, MARG, BODY_TOP + 0.02, iw,
                    bottom - BODY_TOP - 0.04)
        sx = MARG + iw + 0.24
        sw = SW - MARG - sx
        n = len(side)
        gap = 0.16
        ch = min(1.30, (bottom - BODY_TOP - gap * (n - 1)) / n)
        pal = [RED, BLUE, TEAL, ORANGE]
        for i, (lead, body) in enumerate(side):
            y = BODY_TOP + i * (ch + gap)
            col = pal[i % len(pal)]
            rrect(s, sx, y, sw, ch, SOFT, LINE, 1.0, 0.08)
            sq(s, sx, y, sw, 0.055, col)
            _, tf = textbox(s, sx + 0.16, y + 0.19, sw - 0.32, ch - 0.28)
            put(tf, lead, 13.5, True, col, first=True, space_after=3,
                line_spacing=1.20)
            if body:
                put(tf, body, 11.8, False, INK, space_after=0, line_spacing=1.28)
    else:
        place_image(s, png, MARG, BODY_TOP + 0.02, CW,
                    bottom - BODY_TOP - 0.04)
    if note:
        DECK.note(s, note)
    return s


def add_table_slide(kicker, title, headers, rows, col_w=None, note=None,
                    accent=BLUE, cell_colors=None, fs=12.5, top_extra=0.0):
    """列数 ≤5、数据行 ≤8。"""
    assert len(headers) <= 5, "列数必须 ≤5"
    assert len(rows) <= 8, "数据行必须 ≤8"
    s = DECK.new()
    DECK.header(s, kicker, title, accent)
    top = BODY_TOP + 0.16 + top_extra
    bottom = BODY_BOT - (0.36 if note else 0.0)
    nr, nc = len(rows) + 1, len(headers)
    h = min(bottom - top, 0.52 + 0.60 * len(rows))
    gf = s.shapes.add_table(nr, nc, Inches(MARG), Inches(top), Inches(CW),
                            Inches(h))
    tbl = gf.table
    tbl.first_row = True
    tbl.horz_banding = False
    if col_w:
        tot = sum(col_w)
        for i, cwv in enumerate(col_w):
            tbl.columns[i].width = Emu(int(Inches(CW) * cwv / tot))
    hrow = 0.50
    tbl.rows[0].height = Inches(hrow)
    for r in range(1, nr):
        tbl.rows[r].height = Inches((h - hrow) / len(rows))
    for c, htxt in enumerate(headers):
        cell = tbl.cell(0, c)
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        cell.vertical_anchor = MSO_ANCHOR.MIDDLE
        cell.margin_left = cell.margin_right = Inches(0.09)
        tf = cell.text_frame
        tf.word_wrap = True
        put(tf, htxt, fs, True, WHITE, first=True, space_after=0)
    for r, row in enumerate(rows, start=1):
        for c, val in enumerate(row):
            cell = tbl.cell(r, c)
            cell.fill.solid()
            cell.fill.fore_color.rgb = WHITE if r % 2 else SOFT
            cell.vertical_anchor = MSO_ANCHOR.MIDDLE
            cell.margin_left = cell.margin_right = Inches(0.09)
            cell.margin_top = cell.margin_bottom = Inches(0.04)
            tf = cell.text_frame
            tf.word_wrap = True
            col = INK
            bold = (c == 0)
            if cell_colors:
                cc = cell_colors.get((r - 1, c))
                if cc:
                    col, bold = cc, True
            put(tf, str(val), fs, bold, col, first=True, space_after=0,
                line_spacing=1.20)
    if note:
        DECK.note(s, note)
    return s


def add_closing_slide(headline, lines, limits):
    s = DECK.new(footer=False)
    sq(s, 0, 0, SW, SH, NAVY)
    sq(s, 0, 0, SW, 0.10, TEAL)
    _, tf = textbox(s, 0.95, 0.92, 11.4, 0.32)
    put(tf, "结论 · CONCLUSION", 12, True, RGBColor(0x8F, 0xB6, 0xE6),
        first=True, space_after=0)
    _, tf = textbox(s, 0.95, 1.34, 11.4, 1.30)
    put(tf, headline, 29, True, WHITE, first=True, space_after=0,
        line_spacing=1.26)
    sq(s, 0.95, 2.78, 1.4, 0.05, TEAL)
    x = 0.95
    w = (11.44 - 0.24 * 2) / 3
    for i, (lead, body) in enumerate(lines):
        rrect(s, x + i * (w + 0.24), 3.06, w, 1.16,
              RGBColor(0x14, 0x35, 0x5C), RGBColor(0x2E, 0x53, 0x7E), 1.0, 0.08)
        _, tf = textbox(s, x + i * (w + 0.24) + 0.20, 3.24, w - 0.40, 0.86)
        put(tf, lead, 15, True, RGBColor(0x6E, 0xD8, 0xC4), first=True,
            space_after=4)
        put(tf, body, 12, False, RGBColor(0xD7, 0xE6, 0xF5), space_after=0,
            line_spacing=1.30)
    rrect(s, 0.95, 4.48, 11.44, 1.86, RGBColor(0x10, 0x2E, 0x50),
          RGBColor(0x2E, 0x53, 0x7E), 1.0, 0.05)
    _, tf = textbox(s, 1.18, 4.66, 11.0, 1.55)
    put(tf, "使用限制", 13.5, True, RGBColor(0xFF, 0xC7, 0x7A), first=True,
        space_after=6)
    for ln in limits:
        put(tf, "· " + ln, 11.5, False, RGBColor(0xD7, 0xE6, 0xF5),
            space_after=3, line_spacing=1.30)
    _, tf = textbox(s, 0.95, 6.86, 11.44, 0.3)
    put(tf, DOC_NAME + "　·　文档编号 AIDC-LC-TOTAL-001", 10.5, False,
        RGBColor(0x7E, 0xA3, 0xCC), first=True, space_after=0)
    return s


# ---------------------------------------------------------------- 图表生成

def _finish(fig, name, tight=True):
    ASSETS.mkdir(exist_ok=True)
    p = ASSETS / name
    if tight:
        fig.tight_layout()
    fig.savefig(p, facecolor="white", bbox_inches="tight", pad_inches=0.14)
    plt.close(fig)
    return p


def chart_table27():
    fig, ax = plt.subplots(figsize=(11.9, 4.55))
    t = ["25 ℃", "30 ℃", "35 ℃", "40 ℃", "45 ℃"]
    flow = [59, 71, 89, 119, 177]
    dp = [15.9, 22.1, 33.8, 58.6, 126.9]
    x = np.arange(5)
    cols = [C_BLUE] * 4 + [C_RED]
    ax.bar(x, flow, width=0.52, color=cols, zorder=3)
    for i, v in enumerate(flow):
        ax.text(i, v + 4, f"{v}", ha="center", va="bottom", fontsize=13,
                fontweight="bold", color=cols[i])
    m3 = ["3.54", "4.26", "5.34", "7.14", "10.62"]
    ax.set_ylim(0, 215)
    ax.set_ylabel("机柜所需流量  L/min", fontsize=12, color=C_BLUE,
                  fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["%s\n%s m³/h" % (a, b) for a, b in zip(t, m3)],
                       fontsize=12.5, fontweight="bold", color=C_NAVY)
    ax.set_xlabel("机柜入口温度（TCS 供液）", fontsize=11.5, color=C_MUTED)
    ax.tick_params(axis="y", colors=C_BLUE, labelsize=10.5)
    ax.grid(axis="y", color=C_LINE, lw=0.8, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(C_LINE)
    ax.spines["bottom"].set_color(C_LINE)

    ax2 = ax.twinx()
    ax2.plot(x, dp, "--o", color=C_ORG, lw=2.6, ms=8, zorder=4)
    for i, v in enumerate(dp):
        off, ha = ((0, -21), "center") if i < 4 else ((-14, -6), "right")
        ax2.annotate(f"{v}", (i, v), textcoords="offset points",
                     xytext=off, ha=ha, fontsize=11.5,
                     fontweight="bold", color=C_ORG,
                     bbox=dict(boxstyle="round,pad=0.22", fc="white",
                               ec=C_ORG, lw=0.8, alpha=0.95))
    ax2.set_ylim(0, 158)
    ax2.set_ylabel("机柜压降  kPa", fontsize=12, color=C_ORG, fontweight="bold")
    ax2.tick_params(axis="y", colors=C_ORG, labelsize=10.5)
    for sp in ("top", "left"):
        ax2.spines[sp].set_visible(False)
    ax2.spines["right"].set_color(C_LINE)

    ax.text(0.62, 200, "入口温度 25→45 ℃：流量 ×3.0，压降 ×8.0",
            fontsize=13.5, fontweight="bold", color=C_RED, va="top")
    ax.text(0.62, 184, "最后 5 ℃ 贡献了一半以上的压降增量 —— 曲线的形状本身"
                       "就是「不得外推」的证据", fontsize=10.5, color=C_MUTED,
            va="top")
    ax.legend(handles=[Patch(color=C_BLUE, label="柱 = 所需流量 L/min"),
                       Patch(color=C_ORG, label="虚线 = 机柜压降 kPa")],
              loc="upper left", fontsize=11, frameon=False,
              bbox_to_anchor=(-0.005, 1.02))
    return _finish(fig, "01_table27.png")


def chart_cost_layers():
    fig, ax = plt.subplots(figsize=(11.9, 4.5))
    labels = ["L1 托盘 / IT 侧", "L2 二次侧\n共享 CDU", "L2 专用 2×200 kW\n（本项目·海外）",
              "柜外设施热管理\nBernstein（另表）"]
    base = [49860, 107400, 151000, 211000]
    extra = [0, 0, 38000, 0]
    cols = [C_NAVY, "#174F83", C_BLUE, C_TEAL]
    x = np.arange(4)
    ax.bar(x, base, 0.5, color=cols, zorder=3)
    ax.bar(x, extra, 0.5, bottom=base, color="#8DB8EE", zorder=3,
           label="专用方案区间上限")
    txt = ["$49,860", "$107,400", r"\$151k – \$189k", "$211,000"]
    ypos = [49860, 107400, 189000, 211000]
    for i in range(4):
        ax.text(i, ypos[i] + 5500, txt[i], ha="center", fontsize=14,
                fontweight="bold", color=cols[i])
    sub = ["357 $/kW\n@ 液冷 139.5 kW", "716 $/kW\n@ 液冷选型 150 kW",
           "1,007–1,260 $/kW\n国内另为 82–104 万元", "1,249 $/kW\n@ 设施 169 kW/柜"]
    for i in range(4):
        ax.text(i, base[i] * 0.42 if i else base[i] * 0.30, sub[i], ha="center",
                va="center", fontsize=10.5, color="white", fontweight="bold")
    ax.set_ylim(0, 250000)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12, fontweight="bold", color=C_NAVY)
    ax.set_yticks([0, 50000, 100000, 150000, 200000, 250000])
    ax.set_yticklabels(["0", "5 万", "10 万", "15 万", "20 万", "25 万"],
                       fontsize=10.5, color=C_MUTED)
    ax.set_ylabel("单柜热管理成本（美元 / 柜）", fontsize=12, color=C_NAVY)
    ax.grid(axis="y", color=C_LINE, lw=0.8, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(C_LINE)
    ax.spines["bottom"].set_color(C_LINE)
    ax.set_title("前三柱为项目液冷口径；末柱为 Bernstein 柜外设施口径，不可相加或横比　·　工作汇率 1 USD = 7.2 CNY",
                 fontsize=11.5, color=C_MUTED, loc="left", pad=12)
    ax.legend(fontsize=10.5, frameon=False, loc="upper left")
    return _finish(fig, "02_cost_layers.png")


def chart_l2_pie():
    fig, ax = plt.subplots(figsize=(7.5, 4.9))
    vals = [40700, 22000, 22000, 13500, 9200]
    names = ["冷板 / Compute Tray\n$40,700", "UQD 快接头\n$22,000",
             "CDU 分摊（共享）\n$22,000", "Manifold + 柜内主管\n$13,500",
             "Switch Tray 冷却\n$9,200"]
    cols = [C_BLUE, C_TEAL, C_NAVY, "#174F83", C_ORG]
    ex = [0.06, 0.06, 0, 0, 0]
    pct = iter(["38%", "21%", "20%", "13%", "9%"])  # 与报告表 7-2 一致
    w, t, a = ax.pie(vals, labels=names, colors=cols, explode=ex,
                     autopct=lambda _: next(pct), startangle=104,
                     counterclock=False, pctdistance=0.72, labeldistance=1.09,
                     wedgeprops=dict(width=0.52, edgecolor="white", lw=2))
    for x in t:
        x.set_fontsize(11)
        x.set_color(C_NAVY)
        x.set_fontweight("bold")
    for x in a:
        x.set_fontsize(12.5)
        x.set_color("white")
        x.set_fontweight("bold")
    ax.text(0, 0.10, "$107,400", ha="center", fontsize=19, fontweight="bold",
            color=C_NAVY)
    ax.text(0, -0.16, "L2 共享 CDU 口径", ha="center", fontsize=11,
            color=C_MUTED)
    ax.set_title("冷板 + UQD 合计 59%，CDU 只占 20%　——　议价重点不在 CDU",
                 fontsize=12.5, color=C_RED, fontweight="bold", pad=6)
    return _finish(fig, "03_l2_pie.png")


def chart_l3_stack():
    fig, ax = plt.subplots(figsize=(11.9, 3.4))
    ax.barh([1], [51], height=0.46, color=C_BLUE, zorder=3)
    ax.text(25.5, 1, "柜内液冷 5.1 万", ha="center", va="center",
            fontsize=12, color="white", fontweight="bold")
    seg = [(110, "设施级风冷系统 11.0 万", C_ORG),
           (44, "柜外液冷 4.4 万", "#174F83"),
           (57, "配套基础设施 5.7 万", C_TEAL)]
    left = 0
    for v, lab, c in seg:
        ax.barh([0], [v], left=left, height=0.46, color=c, zorder=3)
        ax.text(left + v / 2, 0, lab, ha="center", va="center", fontsize=11.5,
                color="white", fontweight="bold")
        left += v
    ax.set_xlim(0, 230)
    ax.set_ylim(-0.62, 1.62)
    ax.axis("off")
    ax.text(0, 1.38, "机柜 BOM 表（独立口径，不计入下方 21.1 万）",
            fontsize=12, color=C_BLUE, fontweight="bold")
    ax.text(0, 0.38, "柜外设施热管理表：21.1 = 11.0 + 4.4 + 5.7（万美元/柜）",
            fontsize=12, color=C_NAVY, fontweight="bold")
    ax.text(0, -0.48, "11.0 万是设施级风冷系统分摊，不是本项目 25 kW 残余风冷；13 亿美元/GW 与 1,249 $/kW 仅作换算校验",
            fontsize=11.5, color=C_RED, fontweight="bold")
    return _finish(fig, "04_l3_stack.png")


def chart_capacity_ladder():
    fig, ax = plt.subplots(figsize=(11.9, 4.2))
    ax.axvspan(121, 450, color="#FDE8E6", zorder=0)
    ax.plot([28, 2600], [0, 0], color=C_NAVY, lw=2.4, zorder=2)
    vertiv = [(30, "30"), (70, "70*"), (121, "121"), (450, "450"),
              (600, "600"), (1350, "1350"), (2300, "2300")]
    comp = [(80, "英维克 80"), (100, "nVent 100"), (250, "Supermicro 250"),
            (800, "nVent 800"), (1800, "Supermicro 1.8M"),
            (2500, "Motivair 2.5M")]
    for v, lab in vertiv:
        ax.plot([v], [0], "o", ms=11, color=C_BLUE, zorder=4)
        ax.text(v, 0.16, lab, ha="center", fontsize=11.5, color=C_BLUE,
                fontweight="bold")
    for i, (v, lab) in enumerate(comp):
        ax.plot([v], [0], "o", ms=8, color=C_TEAL, zorder=4)
        ax.text(v, -0.22 if i % 2 == 0 else -0.38, lab, ha="center",
                fontsize=10, color=C_TEAL)
    ax.plot([200], [0], "o", ms=17, color=C_RED, zorder=5)
    ax.annotate("本项目 200 kW × 2（1 用 1 备）", xy=(200, 0.03), xytext=(200, 0.62),
                ha="center", fontsize=13, fontweight="bold", color="white",
                bbox=dict(boxstyle="round,pad=0.42", fc=C_RED, ec="none"),
                arrowprops=dict(arrowstyle="-", color=C_RED, lw=2.4), zorder=6)
    ax.annotate("GB300 单柜液冷需求 150 kW", xy=(150, 0.02), xytext=(148, 0.38),
                ha="right", fontsize=11, fontweight="bold", color=C_ORG,
                arrowprops=dict(arrowstyle="->", color=C_ORG, lw=1.6, ls="--"))
    ax.text(28.5, 0.98, "红色区间 = Vertiv 行级空档：121 kW 与 450 kW 之间无行级 SKU",
            fontsize=12.5, color=C_RED, fontweight="bold", ha="left",
            va="top")
    ax.text(200, -0.60, "CoolIT CHx200 同档", ha="center", fontsize=10.5,
            color=C_RED, fontweight="bold")
    ax.set_xscale("log")
    ax.set_xlim(26, 3400)
    ax.set_ylim(-0.80, 1.12)
    ax.set_yticks([])
    ax.set_xticks([30, 70, 121, 200, 450, 800, 1350, 2500])
    ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax.tick_params(axis="x", labelsize=11, colors=C_MUTED)
    ax.set_xlabel("公开标称冷量 kW（对数刻度）", fontsize=11.5, color=C_MUTED)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(C_LINE)
    ax.legend(handles=[Patch(color=C_BLUE, label="Vertiv CoolChip（*70 kW 为 L2A，不作生产基线）"),
                       Patch(color=C_TEAL, label="主要竞品"),
                       Patch(color=C_RED, label="本项目定位")],
              loc="lower right", fontsize=10.5, frameon=False, ncol=1,
              bbox_to_anchor=(1.0, -0.03))
    return _finish(fig, "05_capacity_ladder.png")


def chart_price_path():
    fig, ax = plt.subplots(figsize=(11.9, 4.4))
    yrs = [2026, 2027, 2028, 2029, 2030, 2031]
    cn = [1100, 1018, 943, 873, 808, 750]
    ov = [220, 212, 204, 196, 189, 182]
    ax.plot(yrs, cn, "-o", color=C_BLUE, lw=3, ms=9, zorder=4,
            label="国内 CDU  元/kW（年降 6–10%）")
    for xx, yy in zip(yrs, cn):
        ax.annotate(f"{yy}", (xx, yy), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=11,
                    fontweight="bold", color=C_BLUE)
    ax.set_ylim(620, 1190)
    ax.set_ylabel("国内 CDU  元 / kW", fontsize=12, color=C_BLUE,
                  fontweight="bold")
    ax.tick_params(axis="y", colors=C_BLUE, labelsize=10.5)
    ax.set_xticks(yrs)
    ax.tick_params(axis="x", labelsize=12, colors=C_NAVY)
    ax.grid(axis="y", color=C_LINE, lw=0.8, zorder=0)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(C_LINE)
    ax.spines["bottom"].set_color(C_LINE)

    ax2 = ax.twinx()
    ax2.plot(yrs, ov, "--s", color=C_ORG, lw=3, ms=8, zorder=4,
             label="海外认证 CDU  $/kW（年降 2–5%）")
    for xx, yy in zip(yrs, ov):
        ax2.annotate(f"{yy}", (xx, yy), textcoords="offset points",
                     xytext=(0, -21), ha="center", fontsize=11,
                     fontweight="bold", color=C_ORG)
    ax2.set_ylim(160, 335)
    ax2.set_ylabel("海外认证 CDU  美元 / kW", fontsize=12, color=C_ORG,
                   fontweight="bold")
    ax2.tick_params(axis="y", colors=C_ORG, labelsize=10.5)
    for sp in ("top", "left"):
        ax2.spines[sp].set_visible(False)
    ax2.spines["right"].set_color(C_LINE)

    h1, l1 = ax.get_legend_handles_labels()
    h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc="lower left", fontsize=11.5, frameon=False)
    ax.set_title("国内降得快、海外降得慢 —— 两条曲线不可用汇率互相换算；"
                 "单柜全栈基准路径同期在 21.0–23.0 万美元震荡",
                 fontsize=11.5, color=C_MUTED, loc="left", pad=12)
    return _finish(fig, "06_price_path.png")


def chart_maturity():
    fig, ax = plt.subplots(figsize=(11.9, 4.3))
    items = [("接口冻结", 1, C_RED), ("行业对标", 2, C_BLUE),
             ("成本与商业", 2, C_BLUE), ("CDU 热工水力", 2, C_BLUE),
             ("电控与安全", 3, C_TEAL), ("系统架构", 3, C_TEAL),
             ("需求与口径", 3, C_TEAL)]
    y = np.arange(len(items))
    ax.barh(y, [i[1] for i in items], height=0.56,
            color=[i[2] for i in items], zorder=3)
    lab = {1: "低", 2: "较高", 3: "高"}
    note = {"接口冻结": "11 条 ICD 未冻结 + 电控 5 项阻塞（需求口径）—— 当前唯一瓶颈",
            "行业对标": "200 kW 空档结论成立；待补各厂授权数据表",
            "成本与商业": "三层边界与双市场扎实；缺各厂真实 $/kW",
            "CDU 热工水力": "三套 FAT 完整；耐温与低温点两项待闭环",
            "电控与安全": "硬接线安全链独立于软件，架构判断正确",
            "系统架构": "L0–L5 六层清晰，混合冷却立场坚定",
            "需求与口径": "四套功率口径与 Table 27 处理形成方法论"}
    for i, (name, v, c) in enumerate(items):
        ax.text(v - 0.10, i, lab[v], va="center", ha="right", fontsize=15,
                fontweight="bold", color="white")
        ax.text(3.28, i, note[name], va="center", fontsize=11.5,
                color=c if v == 1 else C_MUTED,
                fontweight="bold" if v == 1 else "normal")
    ax.set_yticks(y)
    ax.set_yticklabels([i[0] for i in items], fontsize=13, fontweight="bold",
                       color=C_NAVY)
    ax.axvline(3.18, color=C_LINE, lw=1.2)
    ax.set_xlim(0, 9.9)
    ax.set_xticks([])
    for sp in ("top", "right", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.spines["left"].set_color(C_LINE)
    ax.set_title("六个维度已达「高 / 较高」，只有接口冻结停在「低」",
                 fontsize=13, color=C_NAVY, fontweight="bold", loc="left",
                 pad=12)
    return _finish(fig, "07_maturity.png")


def chart_pressure_budget():
    fig, ax = plt.subplots(figsize=(11.9, 3.1))
    seg = [(126.9, "机柜 126.9\n（OEM 给定，不可压缩）", C_RED),
           (20, "外管\n≤20", "#174F83"),
           (25, "过滤终阻\n25", C_ORG),
           (40, "板换二次侧\n40", C_BLUE),
           (15, "阀件仪表\n15", C_TEAL)]
    left = 0
    for v, lab, c in seg:
        ax.barh([0], [v], left=left, height=0.46, color=c, zorder=3)
        ax.text(left + v / 2, 0, lab, ha="center", va="center", fontsize=10.5,
                color="white", fontweight="bold")
        left += v
    ax.barh([0], [250 - left], left=left, height=0.46, color="#C9E3DB",
            zorder=3)
    ax.text(left + (250 - left) / 2, 0, "裕量\n23", ha="center", va="center",
            fontsize=10.5, color=C_RED, fontweight="bold")
    ax.axvline(250, color=C_NAVY, lw=2.4, ls="--", zorder=4)
    ax.text(252, 0.42, "候选泵总差压 250 kPa @ 19 m³/h", fontsize=12,
            color=C_NAVY, fontweight="bold", va="center")
    ax.text(0, 0.42, "45 ℃ 最不利点：合计需求 ≈ 227 kPa", fontsize=12.5,
            color=C_NAVY, fontweight="bold")
    ax.annotate("", xy=(0, -0.36), xytext=(170, -0.36),
                arrowprops=dict(arrowstyle="<->", color=C_TEAL, lw=2))
    ax.text(85, -0.52, "机外可用余压 ≈ 170 kPa —— 招标与合同必须写这个数，不是 250",
            ha="center", fontsize=11.5, color=C_TEAL, fontweight="bold")
    ax.set_xlim(0, 320)
    ax.set_ylim(-0.66, 0.62)
    ax.axis("off")
    return _finish(fig, "08_pressure_budget.png")


def chart_loss_window():
    fig, ax = plt.subplots(figsize=(11.9, 3.6))
    rows = [("漏液", 0, 1, C_RED, "立即停机"),
            ("滤芯瞬时堵塞", 30, 60, C_ORG, "30–60 s"),
            ("泵停 / 断流", 30, 60, C_ORG, "30–60 s"),
            ("气阻", 30, 90, C_BLUE, "30–90 s"),
            ("供液超温", 60, 120, C_BLUE, "60–120 s")]
    for i, (name, a, b, c, lab) in enumerate(rows):
        ax.barh([i], [max(b - a, 2.5)], left=a, height=0.50, color=c, zorder=3)
        ax.text(b + 4, i, lab, va="center", fontsize=11.5, color=c,
                fontweight="bold")
    ax.axvline(90, color=C_RED, lw=2.4, ls="--", zorder=4)
    ax.text(92, 4.62, "Vertiv 材料口径 ≈ 90 s", fontsize=12, color=C_RED,
            fontweight="bold")
    ax.axvline(15, color=C_TEAL, lw=2.0, ls=":", zorder=4)
    ax.text(17, -0.86, "泵切换目标 ≤15 s", fontsize=11, color=C_TEAL,
            fontweight="bold")
    ax.set_yticks(range(5))
    ax.set_yticklabels([r[0] for r in rows], fontsize=12.5, fontweight="bold",
                       color=C_NAVY)
    ax.set_xlim(0, 175)
    ax.set_ylim(-1.05, 5.0)
    ax.set_xlabel("失冷可用窗口（秒）　—　传统机房 30 分钟标准 = 1,800 s，不在本图刻度内",
                  fontsize=11, color=C_MUTED)
    ax.grid(axis="x", color=C_LINE, lw=0.8, zorder=0)
    for sp in ("top", "right", "left"):
        ax.spines[sp].set_visible(False)
    ax.spines["bottom"].set_color(C_LINE)
    return _finish(fig, "09_loss_window.png")


def chart_risk_matrix():
    fig, ax = plt.subplots(figsize=(11.9, 4.65))
    cats = ["商务", "网络 / 电气", "系统 / 供应", "水力 / 热工", "控制 / 安全",
            "接口", "设计"]
    risks = [("R1 接液件耐温临界", 3, "设计"),
             ("R2 ICD 未冻结", 3, "接口"),
             ("R3 三重限幅无限值", 3, "控制 / 安全"),
             ("R4 漏液端到端未实测", 2, "控制 / 安全"),
             ("R5 低温入口点不可行", 2, "水力 / 热工"),
             ("R6 泵余压口径混淆", 2, "水力 / 热工"),
             ("R11 板换 3 K 难保证", 1, "系统 / 供应"),
             ("R12 残余风冷被取消", 1, "系统 / 供应"),
             ("R7 UPS 容量未定", 1, "网络 / 电气"),
             ("R8 协议无认证加密", 1, "网络 / 电气"),
             ("R9 宣传口径污染采购", 1, "商务"),
             ("R10 成本口径混层", 1, "商务")]
    colmap = {3: C_RED, 2: C_ORG, 1: "#B8860B"}
    fillmap = {3: "#FDE8E6", 2: "#FFF3D6", 1: "#F6F9FC"}
    for lv in (1, 2, 3):
        ax.axvspan(lv - 0.5, lv + 0.5, color=fillmap[lv], zorder=0)
    groups = {}
    for name, lv, cat in risks:
        groups.setdefault((lv, cats.index(cat)), []).append(name)
    for (lv, yi), names in groups.items():
        k = len(names)
        for j, name in enumerate(names):
            yy = yi + (j - (k - 1) / 2.0) * 0.42
            ax.text(lv, yy, name, ha="center", va="center", fontsize=10.5,
                    fontweight="bold", color="white",
                    bbox=dict(boxstyle="round,pad=0.34", fc=colmap[lv],
                              ec="none"))
    ax.set_xlim(0.5, 3.5)
    ax.set_ylim(-0.8, len(cats) - 0.2)
    ax.set_xticks([1, 2, 3])
    ax.set_xticklabels(["中", "中高", "高"], fontsize=14, fontweight="bold",
                       color=C_NAVY)
    ax.set_yticks(range(len(cats)))
    ax.set_yticklabels(cats, fontsize=12, fontweight="bold", color=C_NAVY)
    ax.set_xlabel("风险等级", fontsize=12, color=C_MUTED)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.grid(axis="y", color=C_LINE, lw=0.8, zorder=1)
    ax.set_title("三条高风险全部指向同一件事：OEM 接口信息还没到手",
                 fontsize=13, color=C_RED, fontweight="bold", loc="left",
                 pad=12)
    return _finish(fig, "10_risk_matrix.png")


def build_charts():
    return {
        "t27": chart_table27(),
        "cost": chart_cost_layers(),
        "pie": chart_l2_pie(),
        "l3": chart_l3_stack(),
        "ladder": chart_capacity_ladder(),
        "price": chart_price_path(),
        "maturity": chart_maturity(),
        "dp": chart_pressure_budget(),
        "loss": chart_loss_window(),
        "risk": chart_risk_matrix(),
    }


# ---------------------------------------------------------------- 示意图页

def add_agenda_slide():
    s = DECK.new()
    DECK.header(s, "汇报逻辑", "八步走：从需求怎么来，一直讲到明天该做什么", NAVY)
    steps = [("1  需求", "155 kW 包络 · 90/10 · Table 27", BLUE),
             ("2  架构", "L0–L5 六层链路 · L2L 选型", DEEPBLUE),
             ("3  设备", "2×200 kW CDU · 三套 FAT", TEAL),
             ("4  电控", "安全链并列 · 漏液三级", TEAL),
             ("5  成本", "项目液冷 / Bernstein 设施分表", ORANGE),
             ("6  对标", "121↔450 kW 空档", ORANGE),
             ("7  风险", "12 条风险 · 冻结看板", RED),
             ("8  行动", "P0 三项并行关闭", RED)]
    gap = 0.22
    w = (CW - gap * 3) / 4
    h = 1.42
    for i, (t1, t2, col) in enumerate(steps):
        r, c = divmod(i, 4)
        x = MARG + c * (w + gap)
        y = BODY_TOP + 0.30 + r * (h + 0.42)
        rrect(s, x, y, w, h, SOFT, LINE, 1.0, 0.07)
        sq(s, x, y, w, 0.075, col)
        _, tf = textbox(s, x + 0.20, y + 0.32, w - 0.40, 0.92)
        put(tf, t1, 19, True, col, first=True, space_after=6)
        put(tf, t2, 12, False, MUTED, space_after=0, line_spacing=1.28)
        if c < 3:
            arrow(s, x + w + 0.03, y + h / 2 - 0.09, 0.16, 0.18, LINE)
    DECK.note(s, "叙事主线：需求是被 OEM 文件定死的 → 架构与设备是对需求的回应 → "
                 "成本与对标回答「值不值、买不买得到」 → 最后落到 11 条待冻结接口上。")
    return s


def add_research_chain_slide():
    s = DECK.new()
    DECK.header(s, "研究链条", "六份报告不是六个专题，是同一条工程链上的六个切面", NAVY)
    rrect(s, MARG, 1.84, CW, 0.76, PALE_BLUE, RGBColor(0xB9, 0xD3, 0xF5), 1.0, 0.10)
    _, tf = textbox(s, MARG + 0.24, 1.96, CW - 0.5, 0.56)
    put(tf, "外部权威输入（只能引用，不能改写）", 13, True, BLUE, first=True,
        space_after=3)
    put(tf, "NVIDIA RA · Lenovo LP2357 / DS0207（Table 27）· Schneider RD110 · "
            "Vertiv CoolChip · OCP / ASHRAE · GB 50174 / GB/T 48023",
        11.5, False, INK, space_after=0)
    arrow(s, SW / 2 - 0.11, 2.64, 0.22, 0.20, BLUE, "down")
    rrect(s, 3.30, 2.88, 6.73, 0.86, NAVY, None, 1.0, 0.08)
    _, tf = textbox(s, 3.52, 2.98, 6.3, 0.68)
    put(tf, "① 冷却系统总体设计 v2.2　·　唯一的需求冻结点", 15, True, WHITE,
        align=PP_ALIGN.CENTER, first=True, space_after=4)
    put(tf, "155 kW 包络　·　90/10 液气　·　Table 27　·　2×200 kW　·　FAT-A/B　·　国标分层",
        11.5, False, RGBColor(0xD7, 0xE6, 0xF5), align=PP_ALIGN.CENTER,
        space_after=0)
    gap = 0.26
    w = (CW - gap * 2) / 3
    mid = [("② CDU 系统设计 v1.19", "200 kW 平台 · 19 m³/h · 250 kPa · UA≥66.7",
            "回答：设备是什么", DEEPBLUE),
           ("③ CDU 电控详细设计 v1.0", "五层架构 · 独立硬接线安全链 · 漏液三级",
            "回答：它怎么不出事", BLUE),
           ("④ 零部件成本分析", "柜内 BOM 5.1 万 / 柜外设施热管理 21.1 万美元",
            "回答：值多少钱", TEAL)]
    for i, (t1, t2, t3, col) in enumerate(mid):
        x = MARG + i * (w + gap)
        arrow(s, x + w / 2 - 0.10, 3.80, 0.20, 0.20, col, "down")
        rrect(s, x, 4.04, w, 1.20, col, None, 1.0, 0.08)
        _, tf = textbox(s, x + 0.18, 4.18, w - 0.36, 0.96)
        put(tf, t1, 14, True, WHITE, align=PP_ALIGN.CENTER, first=True,
            space_after=4)
        put(tf, t2, 11, False, RGBColor(0xDB, 0xE9, 0xFB), align=PP_ALIGN.CENTER,
            space_after=4, line_spacing=1.22)
        put(tf, t3, 11, True, RGBColor(0xBF, 0xF0, 0xE4), align=PP_ALIGN.CENTER,
            space_after=0)
    arrow(s, SW / 2 - 0.11, 5.30, 0.22, 0.20, ORANGE, "down")
    rrect(s, MARG, 5.54, CW, 0.78, WHITE, ORANGE, 2.0, 0.09)
    _, tf = textbox(s, MARG + 0.24, 5.66, CW - 0.5, 0.56)
    put(tf, "⑤ 行业液冷产品对标分析　·　外部校验层", 13.5, True, ORANGE,
        align=PP_ALIGN.CENTER, first=True, space_after=3)
    put(tf, "结论：Vertiv 在 121 kW 与 450 kW 之间无行级 SKU，本项目 200 kW 正落在这个空档里",
        12, True, RED, align=PP_ALIGN.CENTER, space_after=0)
    DECK.note(s, "方向性很重要：任何下游文档与总体设计 v2.2 冲突，以 v2.2 为准；"
                 "v2.2 与订单 OEM 受控文件冲突，以 OEM 为准。")
    return s


def _discipline_page(kicker, title, rows, forbid, foot, accent):
    """口径纪律页：左侧数值堆叠 + 右侧禁止事项。"""
    s = DECK.new()
    DECK.header(s, kicker, title, accent)
    lw = 7.05
    n = len(rows)
    h = 0.66
    gap = 0.16
    top = BODY_TOP + 0.16
    for i, (val, txt, col, fill, strong) in enumerate(rows):
        y = top + i * (h + gap)
        rrect(s, MARG, y, lw, h, fill, col if strong else LINE,
              2.0 if strong else 1.0, 0.10)
        _, tf = textbox(s, MARG + 0.24, y + 0.12, 1.85, 0.44)
        put(tf, val, 20, True, col, first=True, space_after=0)
        _, tf = textbox(s, MARG + 2.16, y + 0.14, lw - 2.42, 0.44)
        put(tf, txt, 13, strong, col if strong else INK, first=True,
            space_after=0, line_spacing=1.20)
    rx = MARG + lw + 0.28
    rw = SW - MARG - rx
    rrect(s, rx, top, rw, 2.30, PALE_RED, RGBColor(0xEF, 0xB5, 0xB2), 1.5, 0.06)
    _, tf = textbox(s, rx + 0.22, top + 0.18, rw - 0.44, 1.98)
    put(tf, "不能这么用", 14, True, RED, first=True, space_after=8)
    for f in forbid:
        put(tf, "✗  " + f, 12.5, True, RED, space_after=7, line_spacing=1.26)
    rrect(s, rx, top + 2.46, rw, 1.62, PALE_TEAL, RGBColor(0xA8, 0xD8, 0xCD),
          1.5, 0.06)
    _, tf = textbox(s, rx + 0.22, top + 2.62, rw - 0.44, 1.36)
    put(tf, "正确做法", 14, True, TEAL, first=True, space_after=8)
    put(tf, foot, 12.5, False, INK, space_after=0, line_spacing=1.34)
    return s


def add_six_layer_slide():
    s = DECK.new()
    DECK.header(s, "系统架构", "从芯片到大气，热量要过六层；缺一层，CDU 再好也交付不了", NAVY)
    layers = [("L0", "芯片 / Tray", "72×B300 · 36×Grace\n冷板 · Tray 级漏检", NAVY),
              ("L1", "机柜歧管", "304L/316L Manifold\nUQDB04 盲插 · 30 psi", DEEPBLUE),
              ("L2", "CDU", "2×200 kW L2L · N+1\n板换 UA≥66.7 · DN65", BLUE),
              ("L3", "二次侧网络", "预制环管 · 均流 ≤10%\n决定单柜故障半径", RGBColor(0x00, 0x78, 0x6A)),
              ("L4", "一次冷源", "塔 / 干冷器 / 冷机\nFWS 27/37 或 37/47 ℃", TEAL),
              ("L5", "交付与服务", "冲洗 · 注液 · 换液\n化验 · FAT / SAT", RGBColor(0x5B, 0x3D, 0x1A))]
    gap = 0.22
    w = (CW - gap * 5) / 6
    y = BODY_TOP + 0.22
    h = 1.72
    for i, (tag, name, desc, col) in enumerate(layers):
        x = MARG + i * (w + gap)
        rrect(s, x, y, w, h, col, None, 1.0, 0.08)
        _, tf = textbox(s, x + 0.12, y + 0.16, w - 0.24, 1.44)
        put(tf, tag, 20, True, RGBColor(0x9F, 0xD8, 0xF5), align=PP_ALIGN.CENTER,
            first=True, space_after=2)
        put(tf, name, 13.5, True, WHITE, align=PP_ALIGN.CENTER, space_after=6)
        put(tf, desc, 10.5, False, RGBColor(0xDD, 0xEA, 0xF6),
            align=PP_ALIGN.CENTER, space_after=0, line_spacing=1.26)
        if i < 5:
            arrow(s, x + w + 0.02, y + h / 2 - 0.10, 0.18, 0.20, RED)
    _, tf = textbox(s, MARG, y + h + 0.12, CW, 0.3)
    put(tf, "红箭头 = 热流方向：芯片 → 冷板 → 歧管 → CDU 板换 → 冷源 → 大气",
        11.5, True, RED, align=PP_ALIGN.CENTER, first=True, space_after=0)
    cards = [("最常见的失败不是 CDU 选小了，而是某一层没人负责",
              "L3 环管决定单机柜故障半径，比 CDU 铭牌更决定可用性；L5 流体服务在彩页上不出现，却是 SAT 的前提。"),
             ("招标只锁 L2 的 CDU 参数，L1 / L3 / L5 会在现场变成签证与工期",
              "验收按层做，不按设备做：每一层都要有明确的责任方与关闭标志。")]
    add_point_cards(s, cards, top=y + h + 0.52, bottom=BODY_BOT,
                    colors=[RED, ORANGE])
    return s


def add_heat_split_slide():
    s = DECK.new()
    DECK.header(s, "热量去向", "155 kW 里约 90% 走液、10% 走风，风冷不能取消", BLUE)
    y = BODY_TOP + 0.42
    total_w = CW
    lw = total_w * 0.885
    rrect(s, MARG, y, lw, 1.10, BLUE, None, 1.0, 0.04)
    _, tf = textbox(s, MARG + 0.3, y + 0.18, lw - 0.6, 0.78)
    put(tf, "液冷路径 ≈ 139.5 kW（155 × 90%）", 20, True, WHITE,
        align=PP_ALIGN.CENTER, first=True, space_after=4)
    put(tf, "CPU / GPU / HBM / NVSwitch 冷板　·　液冷设备按 150 kW 选型",
        12.5, False, RGBColor(0xDB, 0xE9, 0xFB), align=PP_ALIGN.CENTER,
        space_after=0)
    rrect(s, MARG + lw + 0.06, y, total_w - lw - 0.06, 1.10, ORANGE, None, 1.0, 0.04)
    _, tf = textbox(s, MARG + lw + 0.08, y + 0.26, total_w - lw - 0.10, 0.64)
    put(tf, "≈15.5 kW", 14.5, True, WHITE, align=PP_ALIGN.CENTER, first=True,
        space_after=3)
    put(tf, "风侧选型 25 kW", 10, False, PALE_ORG, align=PP_ALIGN.CENTER,
        space_after=0)
    cards = [("残余风冷承担 OSFP 光模块、存储与 PDB 的热量",
              "保留 CRAH / RDHx 是强制项。「fully liquid-cooled」是营销表述，不是设施设计依据。"),
             ("150 + 25 + 200 不等于机柜实际热量",
              "三者分别是液冷选型、风侧选型与设备额定，坐标不同，任何材料里都不得相加。"),
             ("液气比只认 GB300 OEM 的 90/10",
              "用 70/30 采购风侧会超配三倍；用「全液冷」取消 CRAH 会让残余热量失控。")]
    add_point_cards(s, cards, top=y + 1.42, bottom=BODY_BOT,
                    colors=[ORANGE, RED, TEAL])
    return s


def add_liquid_path_slide():
    s = DECK.new()
    DECK.header(s, "液路顺序", "过滤在泵之前、补液接泵吸入侧 —— 顺序本身就是工程含义", TEAL)
    boxes = [("机柜热回液", "≈ 56–62 ℃", RED, WHITE),
             ("双联过滤 25 μm", "在线切换 · 无直通旁路", WHITE, NAVY),
             ("2 × 100% 变频泵", "无轴封 · 4.0 kW 初选", WHITE, NAVY),
             ("可拆式逆流板换", "UA≥66.7 · 面积 ≥22 m²", WHITE, BLUE),
             ("冷供液出 CDU", "DN65 · 316L", TEAL, WHITE)]
    gap = 0.30
    w = (CW - gap * 4) / 5
    y = BODY_TOP + 0.20
    h = 1.02
    for i, (t1, t2, fill, fg) in enumerate(boxes):
        x = MARG + i * (w + gap)
        rrect(s, x, y, w, h, fill, NAVY if fill == WHITE else None,
              1.5, 0.09)
        _, tf = textbox(s, x + 0.12, y + 0.20, w - 0.24, 0.68)
        put(tf, t1, 13.5, True, fg, align=PP_ALIGN.CENTER, first=True,
            space_after=4)
        put(tf, t2, 10.5, False, MUTED if fill == WHITE else RGBColor(0xE4, 0xF3, 0xEF),
            align=PP_ALIGN.CENTER, space_after=0)
        if i < 4:
            arrow(s, x + w + 0.05, y + h / 2 - 0.09, 0.20, 0.18, RED)
    _, tf = textbox(s, MARG, y + h + 0.14, CW, 0.32)
    put(tf, "→ 机柜供液（查 Table 27：25–45 ℃ / 3.54–10.62 m³/h / 16–127 kPa）→ 冷板 → 回液",
        12, True, TEAL, align=PP_ALIGN.CENTER, first=True, space_after=0)
    cards = [("过滤器放在泵前，保护叶轮与板换",
              "双联可在线切换，但不设未过滤直通旁路 —— 这是彩页方案与能过 SAT 的 P&ID 的分界线。"),
             ("膨胀 / 补液 / 脱气接在泵吸入侧",
              "保证 NPSH 并避免补液冲击；补液次数与补液量要当作泄漏诊断，频繁补液必须报警。"),
             ("排气、排污与 PSV 泄放全部接封闭收集",
              "不得就地排放。一次侧 TCV-101 调节 + 100 μm 前置粗滤，DN65 / PN10。")]
    add_point_cards(s, cards, top=y + h + 0.52, bottom=BODY_BOT,
                    colors=[BLUE, TEAL, ORANGE])
    return s


def add_control_arch_slide():
    s = DECK.new()
    DECK.header(s, "电控架构", "安全链和主控是并列的，不是串在它后面", RED)
    y = BODY_TOP + 0.10
    rrect(s, MARG, y, CW, 0.62, PALE_BLUE, RGBColor(0xB9, 0xD3, 0xF5), 1.0, 0.10)
    _, tf = textbox(s, MARG + 0.22, y + 0.09, CW - 0.44, 0.46)
    put(tf, "L4 上位与管理面", 12.5, True, BLUE, first=True, space_after=2)
    put(tf, "设施 BMS / DCIM（Modbus TCP · SNMPv3 · MQTT）　|　IT 管理面 RMC / BMC（Redfish）"
            "　|　ETH-BMS 与 ETH-IT 物理分离，网关不做二层桥接",
        11, False, INK, space_after=0)
    y2 = y + 0.72
    rrect(s, MARG, y2, CW, 0.50, SOFT, LINE, 1.0, 0.12)
    _, tf = textbox(s, MARG + 0.22, y2 + 0.11, CW - 0.44, 0.32)
    put(tf, "L3 网关与网络分区　·　GW-201 协议网关 · 白名单与只读化（Modbus/BACnet 无认证加密，靠分区补偿）",
        11.5, True, DEEPBLUE, first=True, space_after=0)
    y3 = y2 + 0.60
    h3 = 1.34
    w1, w2, w3 = 4.35, 4.35, 2.50
    rrect(s, MARG, y3, w1, h3, BLUE, None, 1.0, 0.07)
    _, tf = textbox(s, MARG + 0.18, y3 + 0.18, w1 - 0.36, 1.06)
    put(tf, "CP-201 主控制器", 15, True, WHITE, align=PP_ALIGN.CENTER,
        first=True, space_after=5)
    put(tf, "工业控制板 + 自研 CDU 算法\nI/O 基线 RTD 8 · AI 22 · DI 40 · AO 10 · DO 28（含 ≥20% 预留）",
        11, False, RGBColor(0xDB, 0xE9, 0xFB), align=PP_ALIGN.CENTER,
        space_after=0, line_spacing=1.30)
    _, tf = textbox(s, MARG + w1 + 0.02, y3 + 0.50, 0.60, 0.4)
    put(tf, "并列", 14, True, MUTED, align=PP_ALIGN.CENTER, first=True,
        space_after=0)
    x2 = MARG + w1 + 0.64
    rrect(s, x2, y3, w2, h3, RED, None, 1.0, 0.07)
    _, tf = textbox(s, x2 + 0.18, y3 + 0.18, w2 - 0.36, 1.06)
    put(tf, "SR-201 硬接线安全链", 15, True, WHITE, align=PP_ALIGN.CENTER,
        first=True, space_after=5)
    put(tf, "双通道 · 强制导向触点 · 复位监控 · 断线报警\n独立于 CP-201，失电即安全侧",
        11, True, RGBColor(0xFF, 0xD9, 0xD5), align=PP_ALIGN.CENTER,
        space_after=0, line_spacing=1.30)
    x3 = x2 + w2 + 0.24
    rrect(s, x3, y3, w3, h3, PALE_ORG, RGBColor(0xE3, 0xCA, 0x8D), 1.5, 0.10)
    _, tf = textbox(s, x3 + 0.16, y3 + 0.24, w3 - 0.32, 0.96)
    put(tf, "HMI 本地", 14, True, ORANGE, align=PP_ALIGN.CENTER, first=True,
        space_after=5)
    put(tf, "网关与上位全失效时\n仍可独立显示与操作", 11, False, ORANGE,
        align=PP_ALIGN.CENTER, space_after=0, line_spacing=1.28)
    y4 = y3 + h3 + 0.16
    rrect(s, MARG, y4, CW, 0.56, SOFT, LINE, 1.0, 0.11)
    _, tf = textbox(s, MARG + 0.22, y4 + 0.13, CW - 0.44, 0.34)
    put(tf, "L1 现场总线　FB-1 仪表段 / FB-2 VFD 专用段（RS-485，另留 4–20 mA 硬线备份给定，总线失效不失控）"
            "　　L0 现场设备　FT / TT / PT / LT / 露点 · 漏液 LD-201…205 + OEM Tray / Rack 干接点",
        11.5, True, DEEPBLUE, first=True, space_after=0, line_spacing=1.26)
    y5 = y4 + 0.68
    rrect(s, MARG, y5, CW, 0.78, PALE_RED, RED, 2.0, 0.08)
    _, tf = textbox(s, MARG + 0.24, y5 + 0.11, CW - 0.48, 0.60)
    put(tf, "设计红线：严禁把应用软件作为漏液的唯一切断手段", 14, True, RED,
        first=True, space_after=3)
    put(tf, "安全链动作直接撤销泵与阀使能 —— 经 VFD 的 STO 输入 + 主接触器双断，绕过 PLC 与应用软件；"
            "主控死机、程序异常或通信中断时仍能独立动作。", 11.5, False, INK,
        space_after=0, line_spacing=1.26)
    return s


def add_leak_slide():
    s = DECK.new()
    DECK.header(s, "漏液响应", "漏液分三级，只有第一级允许交给软件", RED)
    lv = [("一级", "慢漏 / 可疑", "软件告警 + 定位 + 提高采样频率 + 限制补液 + 请求业务迁移",
           "执行路径：应用软件 ASW", ORANGE),
          ("二级", "严重漏液", "立即撤销泵 / 阀使能。传感器响应 <5 s，端到端目标 ≤200 ms（待实测）",
           "执行路径：硬接线安全链，绕过软件", RED),
          ("三级", "外部急停 / OEM Tray、Rack 硬触点", "双通道安全回路动作，失电即安全侧",
           "执行路径：双通道 + 强制导向触点", NAVY)]
    gap = 0.26
    w = (CW - gap * 2) / 3
    y = BODY_TOP + 0.12
    h = 2.30
    for i, (a, b, c, d, col) in enumerate(lv):
        x = MARG + i * (w + gap)
        rrect(s, x, y, w, h, SOFT, LINE, 1.0, 0.06)
        sq(s, x, y, w, 0.075, col)
        _, tf = textbox(s, x + 0.20, y + 0.24, w - 0.40, 1.94)
        put(tf, a, 22, True, col, first=True, space_after=4)
        put(tf, b, 13.5, True, NAVY, space_after=8, line_spacing=1.22)
        put(tf, c, 12, False, INK, space_after=8, line_spacing=1.30)
        put(tf, d, 11.5, True, col, space_after=0, line_spacing=1.24)
    cards = [("复位必须人工授权，四个条件全满足才允许",
              "修复完成、干燥、保压合格、漏液回路测试通过 —— 任何一项没做完都不得复位。"),
             ("联锁演练必须真实注水，不得只做信号短接",
              "短接只验证了电路，没有验证传感器布置是否覆盖真实泄漏路径。"),
             ("凝露误报要与真实漏液分开：供液温度建议 ≥露点 + 3 K，硬限 ≥露点 + 2 K",
              "按 LD-201…205 分区定位，结合露点裕量与趋势判别；接液盘凝水单独处理。")]
    add_point_cards(s, cards, top=y + h + 0.24, bottom=BODY_BOT,
                    colors=[RED, RED, BLUE])
    return s


def add_freeze_board_slide():
    s = DECK.new()
    DECK.header(s, "冻结状态", "27 条 CDU 接口定了 16 条，剩下的 11 条卡住了采购", ORANGE)
    y = BODY_TOP + 0.16
    bars = [("CDU 侧 ICD 共 27 条（机械 9 / 电气 5 / 控制 7 / 通信 6）", 16, 27,
             "16 条已冻结", "11 条待冻结"),
            ("电控专项 ICD 共 31 条　·　电控需求 71 条中 52 条已冻结", 18, 31,
             "18 条已冻结", "13 条待冻结（含 4 条阻塞 · 电控 ICD 口径）")]
    for i, (title, done, tot, l1, l2) in enumerate(bars):
        yy = y + i * 0.86
        _, tf = textbox(s, MARG, yy, CW, 0.26)
        put(tf, title, 12.5, True, NAVY, first=True, space_after=0)
        bw = CW
        dw = bw * done / tot
        sq(s, MARG, yy + 0.30, dw, 0.34, TEAL)
        sq(s, MARG + dw, yy + 0.30, bw - dw, 0.34, ORANGE)
        _, tf = textbox(s, MARG, yy + 0.36, dw, 0.24)
        put(tf, l1, 12, True, WHITE, align=PP_ALIGN.CENTER, first=True,
            space_after=0)
        _, tf = textbox(s, MARG + dw, yy + 0.36, bw - dw, 0.24)
        put(tf, l2, 12, True, WHITE, align=PP_ALIGN.CENTER, first=True,
            space_after=0)
    y2 = y + 1.86
    _, tf = textbox(s, MARG, y2, CW, 0.28)
    put(tf, "制造 / FAT 前必须关闭的阻塞项（CDU 侧与电控侧合并列示）", 13.5, True, RED, first=True,
        space_after=0)
    blocks = [("M-01 / M-02", "TCS 供回机械接口", "未关闭不得下达板换与泵采购", RED),
              ("M-04 / M-05", "最大允许绝压 · UQD", "直接卡住三重限幅的具体限值", RED),
              ("C-02 / EC-C-02", "漏液信号电气形式", "干接点还是总线，决定安全链接线", RED),
              ("C-06 / N-02", "功率封顶请求协议", "依赖 NVIDIA / OEM 受控接口", RED),
              ("CR-S-07 / CR-E-04…06", "TCV 失效位 · 认证范围", "依赖 HAZOP 与目标市场确定", ORANGE)]
    gap = 0.20
    w = (CW - gap * 4) / 5
    for i, (a, b, c, col) in enumerate(blocks):
        x = MARG + i * (w + gap)
        rrect(s, x, y2 + 0.34, w, 1.52,
              PALE_RED if col == RED else PALE_ORG, col, 1.5, 0.08)
        _, tf = textbox(s, x + 0.12, y2 + 0.48, w - 0.24, 1.26)
        put(tf, a, 12, True, col, align=PP_ALIGN.CENTER, first=True,
            space_after=5)
        put(tf, b, 11, True, NAVY, align=PP_ALIGN.CENTER, space_after=5,
            line_spacing=1.22)
        put(tf, c, 10.5, False, MUTED, align=PP_ALIGN.CENTER, space_after=0,
            line_spacing=1.24)
    DECK.note(s, "硬性约束：阻塞项未关闭前，不得下达板换与泵的最终采购、不得下达控制器最终硬件采购、"
                 "不得连接正式 GB300 机柜。功能安全口径为「SIL-informed, not SIL-certified」，"
                 "主路径推荐 ISO 13849 PL，由 HAZOP + LOPA 定级。", top=5.80)
    DECK.note(s, "按电控需求口径统计为 5 项，多出的 CR-E-04…06 认证范围属需求级条目，"
                 "不计入 ICD。引用时须标明口径。", top=6.32)
    return s


def add_p0_slide():
    s = DECK.new()
    DECK.header(s, "行动清单 P0", "三件事并行推进，全部关闭才能进入采购与联机", RED)
    items = [("① 向订单 OEM 澄清四个机械口径", "商务 + OEM",
              ["机柜入口最大允许绝压（M-04）", "UQD 的 Cv 与数量",
               "顶进水还是底进水", "满配湿重"],
              "关闭标志：M-01 / M-02 / M-04 / M-05 转为已冻结"),
             ("② 确认漏液信号的电气形式", "商务 + OEM",
              ["Tray 级与 Rack 级信号是干接点还是总线", "触点常开还是常闭",
               "信号响应时间（C-02）"],
              "关闭标志：安全链接线方案定稿"),
             ("③ 解决接液件耐温临界", "设计 + OEM",
              ["把泵 / 垫片 / 板换规格提到 ≥65 ℃", "或取得各入口温度点的实际同时负荷",
               "回液 56–62 ℃ vs 现规格 60 ℃"],
              "关闭标志：板换与泵可下达最终采购")]
    gap = 0.28
    w = (CW - gap * 2) / 3
    y = BODY_TOP + 0.14
    h = 4.30
    for i, (title, owner, pts, close) in enumerate(items):
        x = MARG + i * (w + gap)
        rrect(s, x, y, w, h, SOFT, LINE, 1.0, 0.05)
        sq(s, x, y, w, 0.09, RED)
        _, tf = textbox(s, x + 0.20, y + 0.28, w - 0.40, 0.80)
        put(tf, title, 15.5, True, NAVY, first=True, space_after=6,
            line_spacing=1.20)
        rrect(s, x + 0.20, y + 1.14, 1.75, 0.32, PALE_RED, None, 1.0, 0.35)
        _, tf = textbox(s, x + 0.20, y + 1.19, 1.75, 0.24)
        put(tf, owner, 11.5, True, RED, align=PP_ALIGN.CENTER, first=True,
            space_after=0)
        _, tf = textbox(s, x + 0.20, y + 1.62, w - 0.40, 1.70)
        for j, p in enumerate(pts):
            put(tf, "· " + p, 12.5, False, INK, first=(j == 0), space_after=8,
                line_spacing=1.28)
        rrect(s, x + 0.16, y + h - 0.92, w - 0.32, 0.72, PALE_TEAL,
              RGBColor(0xA8, 0xD8, 0xCD), 1.0, 0.10)
        _, tf = textbox(s, x + 0.30, y + h - 0.80, w - 0.60, 0.52)
        put(tf, close, 11.5, True, TEAL, first=True, space_after=0,
            line_spacing=1.26)
    DECK.note(s, "P0 三项互相独立，可并行推进。真正的瓶颈不是设计算得够不够细，而是这些信息拿到手的速度。")
    return s


# ---------------------------------------------------------------- 组装

def build(charts):
    # 01 封面
    add_title_slide(
        "NVIDIA GB300 NVL72\n液冷系统综合汇报",
        "需求 · 架构 · 设备 · 电控 · 成本 · 对标　全链贯通",
        ["综合六份源报告", "155 kW 峰值包络", "2×200 kW L2L · N+1",
         "Table 27 为水力唯一依据", "液 / 气 ≈ 90 / 10"],
        ["v1.0　·　2026-09-05　·　文档编号 AIDC-LC-TOTAL-001",
         "综合自：总体设计 v2.2 · CDU 系统设计 v1.19 · CDU 电控详细设计 v1.0 · "
         "零部件成本分析 · 行业产品对标"])

    # 02 一页速览
    add_kpi_slide(
        "一页速览", "设计侧已经收敛，真正卡住项目的是 11 条没谈下来的接口",
        [("155", "kW", ["项目是什么", "GB300 NVL72 单柜液冷，按 Lenovo EDP 峰值包络设计"], BLUE),
         ("2×200", "kW", ["配置是什么", "L2L 液液型 CDU，1 用 1 备整机 N+1"], TEAL),
         ("6 / 7", "", ["当前状态", "六个维度已达高或较高，只有接口冻结停在低"], DEEPBLUE),
         ("11", "条", ["最大风险", "CDU 侧 ICD 待冻结；电控另有 4 条阻塞（ICD 口径）"], RED)],
        bullets=[("液冷负荷 139.5 kW（155 × 90%），设备按 150 kW 选型，风侧另按 25 kW 选型",
                  "四个功率数字属于四个坐标系，任何材料里都不得相加。"),
                 ("头号技术风险：机柜回液 56–62 ℃，接液件现规格只有 60 ℃，处于临界",
                  "未解决前不得下达板换与泵的最终采购。")],
        note="结论先行：建议把资源从「继续算得更细」转向「把 11 条 ICD 谈下来」。")

    # 03 目录
    add_agenda_slide()

    # 04 研究链条
    add_research_chain_slide()

    # 05-07 执行摘要
    add_bullet_slide(
        "执行摘要 1 / 3", "需求侧已经收敛，口径纪律是这套文档最大的资产",
        [("四套功率口径并存，谁也不能覆盖谁",
          "NVIDIA RA 142 kW、Lenovo TDP 135 kW、Lenovo EDP 峰值 155 kW、本项目液冷选型 150 kW —— 描述的是不同产品、不同配置、不同参考设计。"),
         ("三套液气比在市面上流传，本项目只认 GB300 OEM 的 90/10",
          "Vertiv 宣传 50–95%、通用材料 70/30、SuperPOD 72/28 都不是 GB300 的口径。"),
         ("水力唯一合法依据是 Lenovo Table 27，不是热平衡反算",
          "行业初筛用的 1.0–1.5 L/min·kW 比流量，与 OEM 表实际隐含的 0.39–1.18 相差近三倍。"),
         ("证据分级 L1–L6：低级别不得覆盖高级别",
          "订单 OEM 受控文件最高，宣传彩页与媒体转述不得作为任何工程或商务保证点。")],
        note="这三条纪律覆盖了跨报告比对时发现的绝大多数潜在错误。",
        accent=BLUE)

    add_bullet_slide(
        "执行摘要 2 / 3", "设备与安全：最贵的一项由最恶劣工况决定，最险的一项刚被逐点校核逼出来",
        [("200 kW 这个档位是被市场空档定义出来的，不是某家的现成型号",
          "Vertiv 在 121 kW 与 450 kW 之间没有行级 SKU，而 GB300 单柜需求正落在中间。"),
         ("板式换热器由 FAT-B 控制，不是由额定工况控制",
          "暖水 3 K 端温差下要求污堵 UA ≥ 66.7 kW/K、面积 ≥22 m²，是整台设备最贵最难保证的一项。"),
         ("逐点校核暴露接液件耐温临界：回液 56–62 ℃，现规格 60 ℃",
          "要么把规格提到 ≥65 ℃，要么由 ICD 给出各点实际同时负荷。这是纸面复核逼出来的结论。"),
         ("安全核心红线：软件不得作为漏液的唯一切断手段",
          "严重漏液由独立于主控的硬接线安全链撤销泵与阀使能，经 VFD 的 STO + 主接触器双断。"),
         ("失冷容忍窗口约 90 秒，与传统机房的 30 分钟差一个数量级",
          "这就是为什么 RD110 要求 CDU 与设施泵由 UPS 供电、冷却续航 5 min、冷却 UPS 按 2N 配置。")],
        accent=TEAL)

    add_bullet_slide(
        "执行摘要 3 / 3", "钱与市场：公开数字打架，是因为它们在量不同的层",
        [("成本必须先分表再分层，混表是公开数字打架的根源",
          "柜内液冷 5.1 万美元来自机柜 BOM；柜外设施热管理 21.1 万来自另一表，等于风冷 11.0 + 柜外液冷 4.4 + 配套基础设施 5.7。"),
         ("国内与海外是两套价格体系，不是同一商品的折扣关系",
          "海外溢价买的是认证名录、现场数据与漏液责任承担，不能用汇率直接换算再横向比价。"),
         ("专用 CDU 的代价要在立项文件里写明",
          "按 1 MW 折算，专用 1+1 的 capex 效率比共享行级差 3–5 倍；买的是故障域隔离，不是成本最优。"),
         ("项目状态：设计基本收敛、接口尚未关闭",
          "CDU 侧 27 条 ICD 中 11 条待冻结，电控侧另有 4 条阻塞（电控 ICD 口径，需求口径为 5 项）—— 这是当前唯一的瓶颈。")],
        note="明确不采用的口径：「GB300 液冷 38 万美元、占机架 42%」与三层边界全部冲突。",
        accent=ORANGE)

    # 08-10 口径纪律
    _discipline_page(
        "口径纪律 ①", "四个功率数字，四个坐标系，相加就是错",
        [("142 kW", "NVIDIA RA 公开参考上限", BLUE, PALE_BLUE, False),
         ("135 kW", "Lenovo TDP（持续功耗）", BLUE, PALE_BLUE, False),
         ("155 kW", "Lenovo EDP 峰值　←　本项目设计包络", RED, PALE_RED, True),
         ("150 kW", "液冷设备选型负荷", TEAL, PALE_TEAL, False),
         ("25 kW", "风侧选型负荷", ORANGE, PALE_ORG, False)],
        ["150 + 25 + 200 ≠ 机柜实际热量",
         "把 142 kW 与 155 kW 当作同一产品的两个保证点",
         "把 CDU 额定 200 kW 与风侧能力相加，宣称「整柜处理能力」"],
        "任何进入合同、招标或对外材料的数字，都必须能回答三个问题：哪个口径、哪个分母、哪一级证据。"
        "答不出来就不要写进去。",
        NAVY)

    _discipline_page(
        "口径纪律 ②", "液气比有四个版本在流传，本项目只认 90/10",
        [("50–95%", "Vertiv 彩页宣传区间", MUTED, SOFT, False),
         ("70 / 30", "「AI ready」通用示意材料", MUTED, SOFT, False),
         ("72 / 28", "Blackwell SuperPOD 参考设计", MUTED, SOFT, False),
         ("90 / 10", "GB300 OEM 实际　←　唯一采用", TEAL, PALE_TEAL, True)],
        ["用 70/30 采购风侧 = 风冷超配三倍",
         "用「全液冷」取消 CRAH = 残余热量失控",
         "把不同参考设计的比例混在同一页 PPT 里"],
        "峰值液冷负荷 = 155 × 90% ≈ 139.5 kW；液冷设备按 150 kW 选型，风侧按 25 kW 选型，"
        "两者分别选型、分别验收。",
        DEEPBLUE)

    _discipline_page(
        "口径纪律 ③", "说千瓦价之前，先说清楚分母是哪一个",
        [("分母 ①", "设备额定冷量 —— CDU 200 / 600 kW", NAVY, SOFT, False),
         ("分母 ②", "机柜排热 —— 液冷 139.5 或选型 150 kW", NAVY, SOFT, False),
         ("分母 ③", "设施口径 —— Bernstein 169 kW/柜，1 GW ≈ 5,929 柜", NAVY, SOFT, False),
         ("1 : 7.2", "工作汇率 USD : CNY，仅用于换算，不用于比价", TEAL, PALE_TEAL, True)],
        ["把铭牌 kW 当成单柜发热量",
         "把国内元/kW 与海外 $/kW 用汇率直接互换",
         "把项目 L1 / L2 与 Bernstein 柜外设施表放在一起横比"],
        "同一句「多少元每千瓦」，换个分母能差三倍。每个金额都要同时标注：属于哪一层、哪个市场、"
        "除以了哪个功率。",
        TEAL)

    # 11-14 需求基线
    add_kpi_slide(
        "需求基线", "GB300 NVL72 的边界：155 kW 峰值、九成走液、混合冷却",
        [("139.5", "kW", ["峰值液冷负荷", "155 kW × 90%，CDU 裕量计算基准"], BLUE),
         ("8 × 33", "kW", ["供电架构", "8 个电源架，每架 6 × 5.5 kW PSU"], DEEPBLUE),
         ("W45", "", ["NVSwitch Tray 水温等级", "工作水温 2–50 ℃，整柜运行仍查 Table 27"], TEAL),
         ("Tier 3", "", ["可用性目标", "并发可维护、无单点故障"], ORANGE)],
        bullets=[("计算配置：72 × B300 GPU、36 × Grace CPU、18 个 Compute Tray、9 个 NVSwitch Tray",
                  "机柜 600 × 2294 × 1068 mm，空柜 185 kg；满配湿重待 ICD 给出。"),
                 ("NVIDIA 产品页写「fully liquid-cooled」，Lenovo 与 SuperPOD 明确写 hybrid",
                  "本项目按混合冷却设计，保留 CRAH / RDHx；漏液检测为 Tray 级 + Rack 级双级。")],
        note="2026-09-05 复核 NVIDIA RA 仍为 142 kW、液冷、8×33 kW，无新增单柜水力数字。")

    add_chart_slide(
        "水力基线", "入口温度升 20 K，流量涨 3 倍，压降涨 8 倍",
        charts["t27"],
        note="Lenovo LP2357 Table 27 是本项目唯一具 L1 级效力的水力数据，形式是温度—流量—压降三元成对表，"
             "不是可以外推的公式。禁止用固定 10 K 温升反算流量：30 ℃ 点偏差达 205%。")

    add_bullet_slide(
        "工质与洁净度", "洁净度门槛按 25 μm 定，比行业常写的 50 μm 更严",
        [("工质只用 DI 水或 PG25，两者是两套独立数据集",
          "订单选项，不可混用。华为常用的乙二醇 EG 与本项目不是一张表，其压差流量数据只作对照。"),
         ("TCS 过滤 25 μm 双联可在线切换，且不设未过滤直通旁路",
          "OCP 要求投运 ≤25 μm、稳态有文献写 ≤10 μm；本项目取 25 μm，匹配冷板微通道与 UQD 敏感度。"),
         ("FWS 侧 100 μm 前置粗滤；询价时目数与微米必须统一单位",
          "Vertiv 一次侧厂配 500 μm，华为写一次 50 目、二次 270 目 —— 目数与微米不可直接互换。"),
         ("TCS 与 FWS 分表管理，在线测电导率 / pH / 浊度，季度取样化验",
          "禁止使用汽车防冻液与任何未经验证的混液。"),
         ("接液材料 TCS 用 316L，按工质选 EPDM 或 FKM 密封",
          "供应商须提供完整的材料兼容矩阵；快接头族为 UQDB04 盲插，Cv 与数量待 ICD 冻结。")],
        accent=TEAL)

    add_chart_slide(
        "可用性", "GPU 能扛住的失冷时间大约 90 秒，不是 30 分钟",
        charts["loss"],
        side=[("90 秒不是 NVIDIA 官方指标",
               "出自 Vertiv 材料原图。第三方估计 10–60 s 更严苛。当作设计裕量参照，不作合同保证值。"),
              ("双泵切换必须重叠进行",
               "禁止先停后启；判定 2 s + 备泵升速 8 s + 主泵斜坡停 5 s，目标 ≤15 s。"),
              ("RD110 的要求已向供电看齐",
               "CDU 与 FWS 泵由 UPS 供电、冷却续航 ≥5 min、冷却 UPS 按 2N；国内 A 级另有 15 min 蓄冷口径。")],
        img_w=8.15,
        note="传统机房的 30 分钟中断恢复标准在液冷场景下完全不适用 —— 差一个数量级。")

    # 15-17 系统架构
    add_six_layer_slide()
    add_heat_split_slide()

    add_bullet_slide(
        "型式选择", "L2A 排给空气、L2L 排给冷源，生产柜只能选 L2L",
        [("本项目采用 L2L 液液型：经板换把热量交给室外冷源",
          "TCS 与 FWS 物理隔离，适合 100 kW 以上高密新建。Vertiv 全系印刷值为一次侧 5–40 ℃、二次侧 10–45 ℃。"),
         ("L2A 风液型不适用于 GB300 生产柜，三个条件同时不成立",
          "冷量不够、传热对象是机房空气、与 90/10 的残余风冷冲突。代表产品 Vertiv CDU 70、LITEON 约 140 kW 侧车。"),
         ("L2A 的合理场景是实验室、风改液与无一次水的边缘机房",
          "初投资低、零冷塔、零架高地板 —— 但不能用它承诺 GB300 满配训练负荷。"),
         ("产品窗能罩住，不等于每个点都能运行",
          "10 ℃ 并非 GB300 的运行点；低 FWS 温度下部分高温入口点会出现温度交叉，必须逐点校核。")],
        accent=BLUE)

    # 18-23 CDU 平台
    add_kpi_slide(
        "CDU 平台", "200 kW 平台，2 台 1 用 1 备，对选型负荷留 33% 裕量",
        [("200", "kW", ["单台额定换热量", "10%–100% 连续调节"], BLUE),
         ("+33", "%", ["对 150 kW 选型负荷的裕量", "对 139.5 kW 峰值液冷为 +43%"], TEAL),
         ("19", "m³/h", ["平台最大校核流量", "统一覆盖 DI 水与 PG25 两种配方"], DEEPBLUE),
         ("1–8", "台", ["群控能力", "任一台整机退出不中断机柜冷却"], ORANGE)],
        bullets=[("整机 N+1 是买来的故障域隔离：单机双泵不能替代整机冗余",
                  "任一台可隔离维护而不中断机柜冷却；公共母管须可隔离并设止回。"),
                 ("控制器按订单 ICD 调用工况表，不把某个固定工况写死进设备",
                  "OEM 运行包络：入口 25–45 ℃、流量 3.54–10.62 m³/h、机柜压降 16–127 kPa，实施流量/差压/绝压三重限幅。")],
        note="柜式 L2L，600×1200×2000 mm 级，IP54；接口 DN65 初选，TCS 316L，FWS PN10。")

    add_table_slide(
        "工况矩阵", "板换选型由最恶劣的 FAT-B 决定，不是由额定工况决定",
        ["工况", "负荷 / 工质", "四温与流量", "验证目标", "对设计的控制作用"],
        [["FAT-A", "200 kW / DI 水", "TCS 32/42 ℃　FWS 27/37 ℃\nTCS ≈ 17.3 m³/h（1.44 L/min·kW）",
          "5 K 端温差下的平台性能", "验证用，不等同于 OEM 机柜运行点"],
         ["FAT-B", "200 kW / DI 水", "TCS 40/50 ℃　FWS 37/47 ℃\nLMTD = 3 K",
          "暖水污堵 UA ≥ 66.7 kW/K\n有效面积 ≥22 m²，两侧压降 ≤40 kPa",
          "选型控制点：板换选型、阀全开压降与极端环境能力由此决定"],
         ["FAT-PG25", "200 kW / PG25", "10 K 温升约 18.6 m³/h\nρ≈1025、cp≈3.78",
          "丙二醇配方下的流量与压降", "最终流量按供应商实际物性修正"]],
        col_w=[1.0, 1.4, 2.6, 2.4, 3.0],
        cell_colors={(1, 0): RED, (1, 4): RED},
        note="17.3 m³/h 是 CDU 侧 FAT 流量，不是机柜运行流量 —— 机柜侧查 Table 27，最大 10.62 m³/h。"
             "暖水工况把换热温差压到 3 K，这是整台设备最贵、最难保证的一项。",
        accent=RED)

    add_liquid_path_slide()

    add_chart_slide(
        "水力闭合", "泵有 250 kPa，但机外只剩 170 kPa，裕量只有一成",
        charts["dp"],
        note="这张图说明两件事：①「250 kPa 泵」与「机外 170 kPa 可用余压」是两个数，招标与合同必须写后者；"
             "② 过滤器终阻、板换污堵与外管走向三者中任意一项超预算，45 ℃ 工况点就失去水力可行性。"
             "泵选型从「候选」推进到「冻结」之前，必须先闭合这笔账。",
        accent=ORANGE)

    add_table_slide(
        "逐点校核", "能不能跑到某个入口温度，取决于一次水给到多少度",
        ["机柜入口", "所需流量", "机柜压降", "FWS 27 ℃（FAT-A 冷源）", "FWS 37 ℃（RD110 冷源）"],
        [["25 ℃", "3.54 m³/h", "15.9 kPa", "温度交叉 −2 K，不可行", "不可行"],
         ["30 ℃", "4.26 m³/h", "22.1 kPa", "临界：端温差恰 3 K", "不可行"],
         ["35 ℃", "5.34 m³/h", "33.8 kPa", "可行，UA ≈ 10.7 kW/K", "不可行"],
         ["40 ℃", "7.14 m³/h", "58.6 kPa", "可行，UA ≈ 8.9 kW/K", "临界：端温差恰 3 K"],
         ["45 ℃", "10.62 m³/h", "126.9 kPa", "可行，UA ≈ 7.9 kW/K", "可行，UA ≈ 16.6 kW/K"]],
        col_w=[1.4, 1.9, 1.8, 3.6, 3.4],
        cell_colors={(0, 3): RED, (0, 4): RED, (1, 4): RED, (2, 4): RED,
                     (1, 3): ORANGE, (3, 4): ORANGE,
                     (2, 3): TEAL, (3, 3): TEAL, (4, 3): TEAL, (4, 4): TEAL},
        note="核心结论：工况表必须按 FWS 温度分段声明可达点，不能笼统承诺「覆盖 25–45 ℃ 全部五点」。"
             "各点所需 UA 在 7.9–24.1 kW/K，都远低于 FAT-B 的 66.7 —— 板换选型仍由 FAT-B 控制。",
        accent=RED)

    add_kpi_slide(
        "头号风险", "机柜回液比想象的热：56–62 ℃，而现规格只到 60 ℃",
        [("56–62", "℃", ["按 Table 27 反算的回液温度", "随入口温度变化不大"], RED),
         ("≥65", "℃", ["接液件应有的许用液温", "泵、垫片、板换三者都要满足"], ORANGE),
         ("60", "℃", ["当前部件规格", "处于临界，未留裕量"], RED),
         ("停止", "采购", ["硬性约束", "关闭前不得下达板换与泵的最终采购"], NAVY)],
        bullets=[("两条出路：把部件规格提到 ≥65 ℃，或由 ICD 给出各温度点的实际同时负荷",
                  "如果实际同时负荷低于满载，回液温度可以相应下降 —— 但这需要 OEM 给数，不能自己假设。"),
                 ("这是纯纸面逐点复核逼出来的结论，单点设计根本看不见",
                  "入口温度升高时流量同步加大，回液温度反而趋于稳定，所以五个点的回液都落在 56–62 ℃。")],
        note="定压与蓄冷另有一条红线：膨胀罐选型 80 L，续冷水量需 ≥1,154 L —— 相差近 15 倍，"
             "膨胀罐不得兼任蓄冷。", accent=RED)

    # 24-27 电控与安全
    add_control_arch_slide()
    add_leak_slide()

    add_kpi_slide(
        "时间预算", "90 秒的窗口要落成一组能实测的秒级指标",
        [("≤200", "ms", ["严重漏液到执行器失能", "端到端目标，架构已冻结、时间待实测"], RED),
         ("≤15", "s", ["单泵 A→B 重叠切换", "硬限 30 s，禁止先停后启"], ORANGE),
         ("≤30", "s", ["整机 N+1 群控切换", "硬限 60 s，待 FAT 验证"], BLUE),
         ("30", "s", ["BMS 心跳丢失转本地自治", "通信中断不停冷"], TEAL)],
        bullets=[("泵切换 15 s 与失冷窗口 30–60 s 之间只有 2–4 倍余量",
                  "这就是为什么切换必须重叠进行，且不能依赖上位系统仲裁。"),
                 ("供液超温 60 s 内完成联动：TCV 全开 + 泵提速 + 一次侧加速 + 请求 IT 降载",
                  "降载请求 30 s 未确认则升级告警；主控任务周期 ≤20 ms，安全监视 ≤10 ms，SOE 分辨率 ≤1 ms。"),
                 ("FAT 稳态温控判据 ±0.5 ℃，负荷点 0 / 25 / 50 / 75 / 100%；SAT 连续 72 h",
                  "泵切换、断电续冷、漏液联锁、传感器故障、通信中断五项必须全部通过。")],
        accent=ORANGE)

    add_bullet_slide(
        "通信与接口", "一个需要向上游反馈的发现：NVIDIA 运维侧其实是 MQTT",
        [("必选三通道：Modbus TCP 171 点、SNMPv3 145 遥测、MQTT over TLS",
          "Modbus 点表构成为 67 输入寄存器 + 70 离散输入 + 24 保持寄存器 + 10 线圈。"),
         ("选配：BACnet/IP 175 对象、OPC UA 171 Variable、Redfish over HTTPS",
          "与 Modbus 同源映射；NVIDIA RA 要求 BMC 支持 Redfish 1.4 或以上。"),
         ("NVIDIA 运维侧实际走 MQTT（BCM broker），IT 侧才是 Redfish",
          "Modbus 与 SNMP 并非 NVIDIA 官方 CDU 接口，需经网关转译。要接入 Mission Control 生态，网关的 MQTT 能力是必需项。"),
         ("Modbus TCP 与 BACnet/IP 本身无认证与加密，这是协议固有限制",
          "靠网络分区、白名单与只读化补偿，并须在项目安全方案中书面说明。"),
         ("ETH-BMS 与 ETH-IT 物理分离，网关不做二层桥接",
          "刷新率要求：快变量 ≤1 s、常规 ≤5 s、告警变化即报 ≤1 s；协议一致性与互操作测试报告随机交付。")],
        note="供电基线：双路 400/230 VAC 3P+N+PE，经 PSU-201A/B 各 24 VDC / 20 A 至 ORing 冗余母线，"
             "任一路失电不停机、不重启；柜体 IP54、HMI 前面板 IP65。",
        accent=BLUE)

    # 28-32 成本
    add_chart_slide(
        "成本边界", "柜内 BOM 与柜外设施热管理是两张表，不能混加",
        charts["cost"],
        note="互相印证：Morgan Stanley 的托盘冷却 49,860 美元与 Bernstein 的柜内液冷 5.1 万美元高度吻合。"
             "Bernstein 的 21.1 万美元属于柜外设施热管理表，不包含 5.1 万；13 亿美元/GW 与 1,249 $/kW 只作换算校验。",
        accent=TEAL)

    s = add_chart_slide(
        "L2 构成", "议价重点是冷板和快接头，不是 CDU", charts["pie"],
        side=[("冷板 $40,700 —— $2,260/盘 × 18 盘",
               "GB300 相对 GB200 从 $37,800 升到 $40,700。"),
              ("UQD $22,000 —— 单价腰斩，总量翻倍",
               "用量约 252 对；单只从 $70–80 降到 $40–50，但总额从 $12,000 涨到 $22,000。"),
              ("专用方案会让这个结论翻转",
               "共享时 CDU 分摊 $1.5–2.2 万，专用 1+1 约 $5.6–10 万/柜 —— CDU 反而成为最大单项。"),
              ("按 1 MW 折算，专用比共享贵 3–5 倍",
               "买的是单柜级整机 N+1 与故障域隔离，不是成本最优。这个取舍要写进立项文件。")],
        img_w=6.15, accent=TEAL)

    add_chart_slide(
        "Bernstein 两表口径", "5.1 万柜内 BOM 不包含在 21.1 万柜外设施热管理内",
        charts["l3"], accent=ORANGE, img_box_h=2.40)
    # Bernstein 两表口径页补充要点
    last = DECK.prs.slides[-1]
    add_point_cards(last,
                    [("柜外设施热管理 21.1 万 = 设施级风冷 11.0 + 柜外液冷 4.4 + 配套基础设施 5.7",
                      "三项同属 Bernstein 设施热管理表；4.4 万覆盖柜外液冷设施，不等同于本项目专用 CDU 报价。"),
                     ("5.1 万来自另一张机柜 BOM 表",
                      "它可与 Morgan Stanley 49,860 美元交叉验证，但不包含在 21.1 万内；若跨表相加为 26.2 万，必须明确标注“作者跨表加总”。"),
                     ("换算值不是拆分来源",
                      "13 亿美元/GW 与 1,249 $/kW 只校验 21.1 万的量级；11.0 万不是本项目 25 kW 残余风冷成本。")],
                    top=4.36, bottom=BODY_BOT, colors=[TEAL, BLUE, RED])

    add_table_slide(
        "双市场", "国内和海外是两套价格体系，不是同一商品的折扣关系",
        ["项目", "国内", "海外", "价差买到了什么"],
        [["二次侧工程包", "3,000–5,000 元/kW", "高出 50%–100%", "CDU 约占二次侧一半"],
         ["CDU", "1,000–1,100 元/kW\n200 kW 机约 20–22 万元",
          "200–240 $/kW\n单机 $40,000–48,000", "海外溢价约 40%–70%"],
         ["认证快接头 UQD", "约 600 元/对", "约 1,300 元/对", "量产成本仅 30–50 元/只，认证溢价是主要成分"],
         ["整柜液冷", "5,000–8,000 元/kW", "8,000–12,000 元/kW", "认证名录、现场数据积累"],
         ["L2 专用 2×200 kW", "82–104 万元", "$151k–189k", "漏液责任承担一并转移"]],
        col_w=[2.1, 2.7, 2.7, 4.6],
        note="82–104 万元不是 15.1–18.9 万美元的汇率换算结果，两者是两套独立的市场报价。"
             "因此不能简单以「国产替代可省 40%」作结论 —— 责任边界一起换了人。",
        accent=TEAL)

    add_chart_slide(
        "五年展望", "国内 CDU 五年降三成，海外认证件只降一成七",
        charts["price"],
        note="本项目 CDU 产品自身的经济性为概念级（置信度 C−，不可用于合同保证）：外采 BOM 目标 18.40 万元、"
             "COGS 29.40 万元/台、建议售价 39.8 / 34.8 / 30.8 万元。冗余乘数 1.8–2.0× 与认证乘数 1.3–2.0× "
             "是液冷 CDU 定价的两个主导因子。",
        accent=BLUE)

    # 33-35 行业对标
    add_chart_slide(
        "能力阶梯", "200 kW 不是型号，是被市场空档定义出来的档位",
        charts["ladder"],
        note="GB300 单柜液冷需求约 150 kW、峰值包络 155 kW，而 Vertiv 在 121 kW 与 450 kW 之间没有产品："
             "121 kW 扛不住峰值，450 kW 严重浪费。真正覆盖此段的只有 CoolIT CHx200 与 Supermicro 柜内 250 kW。",
        accent=RED)

    add_table_slide(
        "竞品矩阵", "同一个 600 kW，4 ℃ 端温差和 8 ℃ 端温差不是同一台机器",
        ["厂商 / 系列", "代表冷量", "冗余与控制", "对 GB300 单柜的适配判断"],
        [["Vertiv CoolChip", "L2A 70；L2L 30 / 121 / 450 / 600 / 1350 / 2300 kW",
          "双泵（1350 三泵）±1 ℃\nModbus · 50/25 μm", "121 偏紧、450 浪费；70 是 L2A，不能作生产基线"],
         ["CoolIT CHx", "CHx200：200 kW / 4U\nCHx2000：2000 kW @ 5 ℃ ATD",
          "N+1 热插拔 · 25 μm\n群控 20 台 · Redfish", "与本项目同档；「单台带 12 柜」仍须按 N+1 重算"],
         ["Schneider + Motivair", "RD110 参考设计 142 kW/柜\nMCDU-70 单台 2.5 MW",
          "CDU N+1；冷却 UPS 2N\n续航 5 min", "强在工厂参考设计与超大颗粒，不补单柜空档"],
         ["华为 FusionCol600-L", "L450MA：450 / 360 kW\n二次 40/50、一次 37/45",
          "双泵轮巡 / 加减载\niCooling 不直控物理设备", "二次侧常用乙二醇，与 DI / PG25 不是一张表，只作对照"],
         ["nVent RackChiller", "CDU100：100 kW @ 6 K\nCDU800：800 kW @ 4 K",
          "N+1 泵电\nSNMPv3 / Modbus", "100 kW 不够单柜 150；800 kW 走多柜"],
         ["Supermicro / LITEON", "柜内 250 kW；行级 1.8 MW\nLITEON 侧车约 140 kW",
          "柜内泵 N+1", "柜内 250 是另一条技术路线；侧车 140 kW 扛不住 155 峰值"],
         ["英维克 / 申菱", "英维克 80 kW / 4U\n申菱 200–1800 kW",
          "全变频泵 · 冗余泵\n漏液 · 自动补液", "80 kW 不够；申菱宣称支持柜功率 ≤140 kW，须核端温差"]],
        col_w=[2.0, 3.1, 2.6, 4.4], fs=11,
        note="招标必须锁死七项：工质、四温（TCS 供回 + FWS 供回）、两侧流量、压降、过滤精度、泵冗余、群控台数。"
             "只写「600 kW」的招标条款没有约束力。",
        accent=NAVY)

    add_bullet_slide(
        "场景选型", "选型先看场景，再看铭牌 —— 四类场景四种答案",
        [("实验室 / 风改液 / 无一次水　→　L2A 列间或侧车",
          "Vertiv 70、Supermicro 与 LITEON 侧车。不要做的事：用 L2A 承诺 GB300 满配训练。"),
         ("单柜或 1+1 生产柜（本项目）　→　200–250 kW L2L",
          "CoolIT CHx200、Supermicro 柜内 250；Vertiv 无此 SKU。不要做的事：用 121 kW 硬扛 155 kW 峰值。"),
         ("单列 2–4 柜　→　450–800 kW 列间 N+1",
          "Vertiv 450/600、nVent 800、华为 450。不要做的事：一台 450 带 4 柜且不配备机。"),
         ("SuperPOD SU 约 8 柜　→　1.3–2.5 MW 行级 / 周边 + 群控",
          "Vertiv 1350/2300、CoolIT 1500/2000、Motivair 2.5 MW。不要做的事：用宣传「1 台带 8 柜」替代 N+1 计算。"),
         ("国内设计院出图　→　上述硬件 + GB 50174 A 级 + GB/T 48023 + YD/T 6358",
          "支路均流 ≤10%、换热 95% 是国内合规底线。不要做的事：只贴 NVIDIA / ASHRAE 的英文页。")],
        accent=ORANGE)

    # 36-38 风险与冻结
    add_chart_slide(
        "风险登记册", "十二条风险，三条是高 —— 而且都指向同一个源头",
        charts["risk"],
        note="R1 接液件耐温、R3 三重限幅无限值、R5 低温入口点不可行、R6 泵余压口径混淆，"
             "是本次横向比对新识别或强化的四项。缓解措施已逐条落到行动清单。",
        accent=RED)

    add_freeze_board_slide()

    add_chart_slide(
        "成熟度", "六个维度已经站得住，只有接口冻结停在「低」",
        charts["maturity"],
        note="结论：设计侧已基本收敛，项目进度实际取决于 OEM 接口澄清的速度，而不取决于还能不能算得更细。",
        accent=NAVY)

    # 39-40 行动
    add_p0_slide()

    add_table_slide(
        "行动清单 P1–P3", "P0 之后的八件事：把水力、安全、商务三条线分别收口",
        ["优先", "动作", "责任面", "关闭标志"],
        [["P1", "完成 HAZOP / LOPA，确定 TCV-101 失效位与安全链定级", "设计 + 安全",
          "CR-S-07 关闭，SIL 论证归档"],
         ["P1", "板换厂家按 FAT-B（3 K / UA ≥66.7）复核选型", "供应链",
          "DI 水与 PG25 分别出具选型书 + 压降校核"],
         ["P1", "泵水力闭合：扣除 CDU 内部损失，单独冻结机外可用余压", "设计",
          "水力计算书签署，含关死点与 NPSH"],
         ["P1", "按 FWS 温度分段重写工况表，声明各段可达的入口温度点", "设计",
          "工况表 v2 发布"],
         ["P2", "确定目标市场与认证范围", "商务", "认证清单冻结，控制器硬件可下单"],
         ["P2", "冻结通信协议范围，安排一致性与互操作测试", "电控", "协议清单 + 测试计划"],
         ["P2", "向 Vertiv / CoolIT / 华为索取授权数据表", "市场", "对标报告待补项关闭"],
         ["P3", "编制招标技术条款模板，锁定七项", "商务", "模板评审通过"]],
        col_w=[0.8, 6.4, 1.9, 3.4], fs=11.5,
        cell_colors={(i, 0): ORANGE for i in range(4)},
        accent=ORANGE)

    # 41 收尾
    add_closing_slide(
        "技术方案已经站得住，制约不在设计能力，\n而在 OEM 接口信息的获取速度",
        [("方案有对标依据", "2×200 kW L2L + 整机 N+1，正好填补 121–450 kW 的行级空档。"),
         ("数据有一手支撑", "热工水力以 Lenovo Table 27 逐点校核为准，安全架构把切断动作独立于软件。"),
         ("建议的资源转向", "从「继续算得更细」转向「把 11 条 ICD 谈下来」，三项 P0 并行推进。")],
        ["本材料为综合与决策用途，不替代源报告的工程效力，也不替代 OEM 受控文件、厂家选型单与 ICD。",
         "所有数字均绑定其口径与分母，不得跨口径相加或横向比价。",
         "水力保证点以订单 OEM 的温度—流量—压降表为唯一依据。",
         "标注「待冻结 / 待实测 / 概念级」的条目不得写入合同。"])


# ---------------------------------------------------------------- 自检

def self_check(path):
    prs = Presentation(str(path))
    n_slides = len(prs.slides)
    n_pics = 0
    n_tables = 0
    n_shapes_total = 0
    warns = []
    edge = []
    EMU = 914400.0
    print("\n" + "=" * 74)
    print("自检报告  ·  %s" % path.name)
    print("=" * 74)
    print("总页数：%d 页（要求 32–42）  %s"
          % (n_slides, "OK" if 32 <= n_slides <= 42 else "！超出范围"))
    print("-" * 74)
    print("%-5s %-8s %-7s %-7s %s" % ("页", "形状数", "图片", "表格", "标题（截断 34 字）"))
    print("-" * 74)
    for i, slide in enumerate(prs.slides, 1):
        pics = tables = 0
        title = ""
        shapes = list(slide.shapes)
        n_shapes_total += len(shapes)
        for sh in shapes:
            # 留白检查：整版底色（封面 / 收尾页）除外
            l0, t0 = sh.left / EMU, sh.top / EMU
            r0, b0 = l0 + sh.width / EMU, t0 + sh.height / EMU
            fullbleed = (sh.width / EMU > 13.0 and sh.height / EMU > 7.0)
            footer_el = t0 > 6.80
            if not fullbleed and not footer_el and sh.height / EMU > 0.15:
                if l0 < 0.50 - 1e-6 or t0 < 0.40 - 1e-6 or r0 > SW - 0.50 + 1e-6 \
                        or b0 > 6.80 + 1e-6:
                    edge.append("  第 %02d 页：形状越界 L%.2f T%.2f R%.2f B%.2f"
                                % (i, l0, t0, r0, b0))
            if sh.shape_type == 13 or sh.__class__.__name__ == "Picture":
                pics += 1
            if getattr(sh, "has_table", False):
                tables += 1
            if sh.has_text_frame:
                tf = sh.text_frame
                # 标题识别：字号最大的粗体段落
                for p in tf.paragraphs:
                    for r in p.runs:
                        if r.font.size and r.font.size.pt >= 21 and r.font.bold:
                            if len(r.text) > len(title):
                                title = r.text
                # 溢出估算
                w_in = sh.width / 914400.0
                h_in = sh.height / 914400.0
                if w_in <= 0.2 or h_in <= 0.2:
                    continue
                need = 0.0
                avail_pt = max(w_in * 72.0 - 14, 20)
                for p in tf.paragraphs:
                    chars = [(c, r.font.size.pt if r.font.size else 14)
                             for r in p.runs for c in r.text]
                    if not chars:
                        continue
                    sz = max(s for _, s in chars)
                    # 按硬换行分段，段内按累计宽度估算折行数
                    lines = 0
                    cur, seg_lines = 0.0, 1
                    for c, s in chars:
                        if c == "\n":
                            lines += seg_lines
                            cur, seg_lines = 0.0, 1
                            continue
                        # 中文全角≈1 em，西文/数字≈0.56 em
                        cur += s * (1.0 if ord(c) > 0x2E80 else 0.56)
                        if cur > avail_pt:
                            seg_lines += 1
                            cur = 0.0
                    lines += seg_lines
                    need += lines * sz * 1.32 / 72.0 + 0.04
                if need > h_in + 0.14:
                    warns.append("  第 %02d 页：文本框 %.2f×%.2f in 估算需要 %.2f in  「%s…」"
                                 % (i, w_in, h_in, need,
                                    ("".join(r.text for p in tf.paragraphs
                                             for r in p.runs))[:22]))
        n_pics += pics
        n_tables += tables
        print("%-5d %-8d %-7d %-7d %s"
              % (i, len(shapes), pics, tables, title[:34]))
    print("-" * 74)
    print("形状总数 %d　·　嵌入图片 %d 张　·　表格 %d 个" % (n_shapes_total, n_pics, n_tables))
    pngs = sorted(p.name for p in ASSETS.glob("*.png"))
    print("生成图表 %d 张：%s" % (len(pngs), "、".join(pngs)))
    missing = [p for p in pngs if not (ASSETS / p).exists()]
    print("图片文件缺失：%s" % (missing or "无"))
    if warns:
        print("\n文本溢出风险（估算，仅供复核）：%d 处" % len(warns))
        for w in warns:
            print(w)
    else:
        print("\n文本溢出风险：未发现")
    if edge:
        print("\n留白检查（要求四边 ≥0.5 in、正文不压页脚）：%d 处越界" % len(edge))
        for e in edge:
            print(e)
    else:
        print("留白检查：全部页面四边留白 ≥0.5 in，正文未压到页脚")
    print("=" * 74 + "\n")
    return n_slides, n_pics, n_tables, len(warns)


# ---------------------------------------------------------------- main

def main():
    ASSETS.mkdir(exist_ok=True)
    for old in ASSETS.glob("*.png"):
        old.unlink()
    print("正在生成图表 …")
    charts = build_charts()
    for k, v in charts.items():
        print("  ✓ %-9s → %s" % (k, v.name))
    print("正在生成幻灯片 …")
    build(charts)
    if OUT_PPTX.exists():
        OUT_PPTX.unlink()
    DECK.prs.save(str(OUT_PPTX))
    print("已保存：%s" % OUT_PPTX)
    self_check(OUT_PPTX)


if __name__ == "__main__":
    main()
