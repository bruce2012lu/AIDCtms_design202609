# -*- coding: utf-8 -*-
"""UC-01b 壁面射流与三槽流路：多视图 SVG（1 用户单位 = 0.1 mm，SC=10）。"""
import math
import model as M
from svg import (Canvas, INK, BLUE, TEAL, ORANGE, RED, GREY,
                 CU, CU_D, WATER, FIN)

G = M.GEO
S = G["S_jet"]            # 3.0
H = G["H_jet"]            # 2.0
T_LID = G["t_lid"]        # 2.5
T_BASE = G["base_cu"]     # 2.0
CH_W = G["ch_w"]          # 0.40
CH_H = G["ch_h"]          # 1.50
CH_P = G["ch_p"]          # 0.80
D_GEO = G["D_jet"]        # 0.50 代码默认
D = 0.40                  # UC-01b（用户最近孔径）
SLIT = 0.80               # 回液缝全宽；周期缝落在 ±X 端，本胞各见一半
SLOT_YS = (-CH_P, 0.0, CH_P)
SC = 10.0


def mm(v):
    return v * SC


def flow(c, pts, color=BLUE, sw=0.45):
    """折线流线，末段带箭头；保证包围盒计入全部点。"""
    if len(pts) < 2:
        return
    c._t(*pts)
    if len(pts) == 2:
        c.arrow(pts[0][0], pts[0][1], pts[1][0], pts[1][1], color, sw)
        return
    c.polyline(pts[:-1], color, sw)
    c.arrow(pts[-2][0], pts[-2][1], pts[-1][0], pts[-1][1], color, sw)


def _stack_y():
    y_lid = 0.0
    y_gap = mm(T_LID)
    y_ch = y_gap + mm(H)
    y_bot = y_ch + mm(CH_H)
    y_end = y_bot + mm(T_BASE)
    return y_lid, y_gap, y_ch, y_bot, y_end


def _copper_block(c, x, y, w, h, pid):
    hatch = c.hatch(pid, CU_D, 0.20, 1.0, 45)
    c.rect(x, y, w, h, CU, INK, 0.28)
    c.rect(x, y, w, h, hatch, "none", 0)
    c.rect(x, y, w, h, "none", INK, 0.22)


# ============================================================
# 图 1 · 过孔纵剖面（Y=0，沿槽长 / ±X）
# ============================================================
def fig_section_xz():
    c = Canvas((0, 0, 10, 10),
               aria="UC-01b 过孔纵剖面 Y=0：自由射流、驻点、壁面射流、回液上抽",
               label="xz")
    y_lid, y_gap, y_ch, y_bot, y_end = _stack_y()
    xl, xr = -mm(S / 2), mm(S / 2)
    w = xr - xl
    slit_in = mm(SLIT / 2)          # 本胞可见的半缝 0.40

    _copper_block(c, xl, y_lid, w, mm(T_LID), "wjcu1a")
    c.rect(xl, y_gap, w, mm(H), WATER, BLUE, 0.22)
    _copper_block(c, xl, y_ch, w, mm(CH_H), "wjcu1b")
    _copper_block(c, xl, y_bot, w, mm(T_BASE), "wjcu1c")

    # 中槽：本剖面切在槽心，整段都是槽腔
    c.rect(xl, y_ch, w, mm(CH_H), FIN, TEAL, 0.18)
    # 喷嘴 + 略展开的射流柱（便于看见，不是把孔径画大）
    c.rect(-mm(D) / 2, y_lid, mm(D), mm(T_LID), WATER, BLUE, 0.22)
    c.poly([(-mm(D) / 2, y_gap), (mm(D) / 2, y_gap),
            (mm(D) * 0.85, y_ch), (-mm(D) * 0.85, y_ch)],
           "#90cdf4", BLUE, 0.16)
    # 回液缝（盖板 + 间隙，两端）
    for x0 in (xl, xr - slit_in):
        c.rect(x0, y_lid, slit_in, mm(T_LID) + mm(H), "#f6ad55", ORANGE, 0.28)

    # 壁面射流薄层：画在肋顶标高（间隙底），不是槽底导管流
    band = 1.6
    c.rect(xl + slit_in, y_ch - band, w - 2 * slit_in, band,
           "#f6ad55", "none", 0)

    # 流线
    flow(c, [(0, y_lid + 0.6), (0, y_bot - 1.2)], BLUE, 0.55)
    c.circle(0, y_bot - 0.7, 1.15, RED, "none", 0)
    flow(c, [(1.2, y_ch - 0.55), (xl + slit_in + 1.4, y_ch - 0.55)],
         ORANGE, 0.55)
    flow(c, [(-1.2, y_ch - 0.55), (xr - slit_in - 1.4, y_ch - 0.55)],
         ORANGE, 0.55)
    # 槽底导管流（对比：不是壁面射流）
    flow(c, [(2.0, y_ch + mm(CH_H) * 0.62),
             (xl + slit_in + 2.0, y_ch + mm(CH_H) * 0.62)],
         TEAL, 0.28)
    flow(c, [(-2.0, y_ch + mm(CH_H) * 0.62),
             (xr - slit_in - 2.0, y_ch + mm(CH_H) * 0.62)],
         TEAL, 0.28)
    # 回液上抽
    flow(c, [(xl + slit_in * 0.5, y_ch - 0.4),
             (xl + slit_in * 0.5, y_lid - 4.2)], ORANGE, 0.50)
    flow(c, [(xr - slit_in * 0.5, y_ch - 0.4),
             (xr - slit_in * 0.5, y_lid - 4.2)], ORANGE, 0.50)

    # 尺寸
    xd = xr + 5.5
    c.dim_v(y_lid, y_gap, xd, "t=2.5", 2.0, ext=0.9, sw=0.14)
    c.dim_v(y_gap, y_ch, xd, "H=2.0", 2.0, ext=0.9, color=BLUE, sw=0.14)
    c.dim_v(y_ch, y_bot, xd, "1.50", 2.0, ext=0.9, sw=0.14)
    c.dim_v(y_bot, y_end, xd, "2.0", 2.0, ext=0.9, sw=0.14)
    c.dim_h(xl, xr, y_end + 5.2, "S = 3.0", 2.1, ext=0.9, below=True, sw=0.14)
    c.dim_h(-mm(D) / 2, mm(D) / 2, y_lid - 7.6, "⌀0.40", 1.9, ext=0.7,
            color=BLUE, sw=0.14)

    c.leader(0, y_lid + mm(T_LID) * 0.45, -28, y_lid - 2.2,
             "喷嘴（自由射流）", 2.05, BLUE, "end", sw=0.14)
    c.leader(0, y_bot - 0.7, 22, y_end + 1.6,
             "② 驻点（槽底）", 2.05, RED, "start", sw=0.14)
    c.leader(mm(0.55), y_ch - 0.55, 24, y_gap + 3.2,
             "③ 壁面射流（贴肋顶）", 2.05, ORANGE, "start", sw=0.14)
    c.leader(xl + 6, y_ch + mm(CH_H) * 0.62, -26, y_ch + 11,
             "槽内导管流 ≠ 壁面射流", 1.95, TEAL, "end", sw=0.14)
    c.leader(xl + slit_in * 0.5, y_lid + 2.0, -26, y_lid - 10.5,
             "回液缝 0.80 上抽", 2.05, ORANGE, "end", sw=0.14)
    c.text(0, y_end + 9.4, "Y=0 只切到中槽；侧槽在图面前后 Y=±0.80，见图 2 / 图 3",
           1.85, GREY, "middle", cn=True)
    c.text(0, y_end + 12.2, "代码默认 ⌀0.50（H/D=4，S/D=6）；本图 UC-01b ⌀0.40（H/D=5，S/D=7.5）",
           1.75, GREY, "middle", cn=True)
    return c.autofit(5.0).render()


# ============================================================
# 图 2 · 单元顶视
# ============================================================
def fig_plan_xy():
    c = Canvas((0, 0, 10, 10),
               aria="UC-01b 单元顶视：壁面射流流线从驻点到两侧回液缝",
               label="xy")
    # 屏幕：X 右，Y 下（与工程 Y 相反，仅绘图）
    half = mm(S / 2)
    slit_in = mm(SLIT / 2)

    c.rect(-half, -half, mm(S), mm(S), "#f7fbff", INK, 0.30)
    # 回液缝带
    c.rect(-half, -half, slit_in, mm(S), "#fde6c8", ORANGE, 0.22)
    c.rect(half - slit_in, -half, slit_in, mm(S), "#fde6c8", ORANGE, 0.22)
    c.text(-half + slit_in / 2, 0.4, "回", 1.7, ORANGE, "middle", cn=True)
    c.text(-half + slit_in / 2, 2.5, "液", 1.7, ORANGE, "middle", cn=True)
    c.text(half - slit_in / 2, 0.4, "回", 1.7, ORANGE, "middle", cn=True)
    c.text(half - slit_in / 2, 2.5, "液", 1.7, ORANGE, "middle", cn=True)

    # 三槽（沿 X）
    for i, yc in enumerate(SLOT_YS):
        fill = "#4fd1c5" if yc == 0 else "#9ae6d8"
        c.rect(-half + slit_in, mm(yc) - mm(CH_W) / 2,
               mm(S) - 2 * slit_in, mm(CH_W), fill, TEAL, 0.20)
    c.text(0, mm(-CH_P) - 2.8, "侧槽  Y=−0.80", 1.7, TEAL, "middle", cn=True)
    c.text(mm(0.95), 0.55, "中槽", 1.7, "#0f4c4a", "start", cn=True)
    c.text(0, mm(CH_P) + 3.2, "侧槽  Y=+0.80", 1.7, TEAL, "middle", cn=True)

    # r/D 圆（标注放右侧图例，避免压在孔上）
    for k, col in ((1.0, RED), (2.0, ORANGE), (S / 2 / D, GREY)):
        c.circle(0, 0, mm(k * D), "none", col, 0.20,
                 extra='stroke-dasharray="1.2 0.7"')
    lgx, lgy = half + 9.5, -half + 2.2
    c.text(lgx, lgy - 3.4, "径向", 1.8, INK, "start", cn=True, weight="bold")
    for i, (lab, col) in enumerate((
            ("r/D=1  驻点核", RED),
            ("r/D=2  侧槽带", ORANGE),
            ("r/D=3.75  胞边", GREY))):
        yy = lgy + i * 3.4
        c.line(lgx, yy - 0.6, lgx + 4.2, yy - 0.6, col, 0.35,
               extra='stroke-dasharray="1.1 0.6"')
        c.text(lgx + 5.0, yy, lab, 1.7, col, "start", cn=True)

    c.circle(0, 0, mm(D) / 2, "#fff", BLUE, 0.35)
    c.centermark(0, 0, mm(D) * 1.8, GREY, 0.12)

    # 壁面射流流线：径向再折向 ±X 回液
    flow(c, [(mm(0.12), 0), (half - slit_in - 0.6, 0)], ORANGE, 0.42)
    flow(c, [(-mm(0.12), 0), (-half + slit_in + 0.6, 0)], ORANGE, 0.42)
    for sy, sx in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        pts = [(mm(0.08) * sx, mm(0.06) * sy),
               (mm(0.22) * sx, mm(0.42) * sy),
               (mm(0.55) * sx, mm(CH_P) * sy),
               ((half - slit_in - 0.7) * (1 if sx > 0 else -1),
                mm(CH_P) * sy)]
        flow(c, pts, ORANGE, 0.36)

    c.dim_h(-half, half, half + 6.2, "S = 3.0", 2.05, ext=0.9,
            below=True, sw=0.14)
    # S 的竖直尺寸改到左侧靠外，给右侧 r/D 图例留空
    c.dim_v(mm(-CH_P), mm(CH_P), -half - 6.8, "节距 0.80", 1.85,
            ext=0.8, left=True, sw=0.14)
    c.dim_h(-mm(CH_W) / 2, mm(CH_W) / 2, -half - 5.4, "槽宽 0.40",
            1.75, ext=0.7, color=TEAL, sw=0.14)
    c.leader(0, -mm(D) / 2, 18, -half - 9.2,
             "⌀0.40（默认 ⌀0.50）", 1.9, BLUE, "start", sw=0.14)
    c.leader(half - slit_in / 2, -mm(0.9), 22, half + 2.4,
             "回液缝 0.80（本胞见一半）↑", 1.85, ORANGE, "start", sw=0.14)
    c.text(0, half + 10.6, "橙线 = 壁面射流：驻点向外，沿间隙 / 槽口走向 ±X 回液缝",
           1.8, ORANGE, "middle", cn=True)
    return c.autofit(4.5).render()


# ============================================================
# 图 3 · 沿槽看（X 法向，过孔 X=0）
# ============================================================
def fig_end_yz():
    c = Canvas((0, 0, 10, 10),
               aria="UC-01b 沿槽端视：壁面射流扫入侧槽，废液沿 ±X 走出图面后上抽",
               label="yz")
    y_lid, y_gap, y_ch, y_bot, y_end = _stack_y()
    yl, yr = -mm(S / 2), mm(S / 2)
    w = yr - yl

    _copper_block(c, yl, y_lid, w, mm(T_LID), "wjcu3a")
    c.rect(yl, y_gap, w, mm(H), WATER, BLUE, 0.22)
    _copper_block(c, yl, y_ch, w, mm(CH_H), "wjcu3b")
    _copper_block(c, yl, y_bot, w, mm(T_BASE), "wjcu3c")

    # 三条槽
    for yc in SLOT_YS:
        fill = "#2f9e94" if yc == 0 else FIN
        c.rect(mm(yc) - mm(CH_W) / 2, y_ch, mm(CH_W), mm(CH_H),
               fill, TEAL, 0.18)
    c.rect(-mm(D) / 2, y_lid, mm(D), mm(T_LID), WATER, BLUE, 0.22)
    c.poly([(-mm(D) / 2, y_gap), (mm(D) / 2, y_gap),
            (mm(D) * 0.85, y_ch), (-mm(D) * 0.85, y_ch)],
           "#90cdf4", BLUE, 0.16)

    # 壁面射流薄层贴在四条肋顶（槽口本身不涂）
    rib_spans = (
        (-S / 2, -CH_P - CH_W / 2),
        (-CH_P + CH_W / 2, -CH_W / 2),
        (CH_W / 2, CH_P - CH_W / 2),
        (CH_P + CH_W / 2, S / 2),
    )
    for a, b in rib_spans:
        if b - a > 0.05:
            c.rect(mm(a), y_ch - 1.6, mm(b - a), 1.6, "#f6ad55", "none", 0)

    flow(c, [(0, y_lid + 0.5), (0, y_bot - 1.3)], BLUE, 0.55)
    c.circle(0, y_bot - 0.75, 1.1, RED, "none", 0)
    # 壁面射流扫向两侧槽口（贴肋顶，再探入槽口）
    flow(c, [(1.3, y_ch - 0.55),
             (mm(CH_P) - mm(CH_W) / 2 - 0.15, y_ch - 0.55),
             (mm(CH_P), y_ch + 2.2)], ORANGE, 0.50)
    flow(c, [(-1.3, y_ch - 0.55),
             (-mm(CH_P) + mm(CH_W) / 2 + 0.15, y_ch - 0.55),
             (-mm(CH_P), y_ch + 2.2)], ORANGE, 0.50)
    # 槽内导管流：沿 ±X 走出图面（不是往槽底钻）
    for yc in SLOT_YS:
        c.circle(mm(yc), y_ch + mm(CH_H) * 0.58, 1.05, "none", TEAL, 0.28)
        c.circle(mm(yc), y_ch + mm(CH_H) * 0.58, 0.28, TEAL, "none", 0)

    # 走出图面：沿 ±X 去回液缝
    def _io(x, y, lab, dy=-3.6):
        c.circle(x, y, 1.35, "none", ORANGE, 0.28)
        c.circle(x, y, 0.35, ORANGE, "none", 0)
        c.text(x, y + dy, lab, 1.7, ORANGE, "middle", cn=True)
        c._t((x - 2.2, y - 2.2), (x + 2.2, y + 2.2))

    _io(mm(-1.15), y_gap + mm(H) * 0.42, "⊗ −X 去回液")
    _io(mm(1.15), y_gap + mm(H) * 0.42, "⊙ +X 去回液")

    xd = yr + 5.2
    c.dim_v(y_lid, y_gap, xd, "2.5", 1.9, ext=0.8, sw=0.14)
    c.dim_v(y_gap, y_ch, xd, "H=2.0", 1.9, ext=0.8, color=BLUE, sw=0.14)
    c.dim_v(y_ch, y_bot, xd, "1.50", 1.9, ext=0.8, sw=0.14)
    c.dim_h(mm(-CH_P) - mm(CH_W) / 2, mm(-CH_P) + mm(CH_W) / 2,
            y_end + 4.8, "0.40", 1.7, ext=0.7, below=True, sw=0.14)
    c.dim_h(mm(-CH_P), mm(CH_P), y_end + 8.8, "±0.80", 1.85,
            ext=0.7, below=True, sw=0.14)
    c.dim_h(yl, yr, y_end + 13.0, "S = 3.0", 2.0, ext=0.8, below=True, sw=0.14)

    c.leader(0, y_lid + 3.0, -24, y_lid - 3.4, "① 自由射流 ⌀0.40",
             2.0, BLUE, "end", sw=0.14)
    c.leader(0, y_bot - 0.7, 20, y_end + 1.2, "② 驻点",
             2.0, RED, "start", sw=0.14)
    c.leader(mm(0.35), y_ch - 0.55, 22, y_gap + 2.4,
             "③ 壁面射流扫入侧槽", 2.0, ORANGE, "start", sw=0.14)
    c.leader(mm(CH_P), y_ch + mm(CH_H) * 0.58, 24, y_bot + 6.5,
             "槽内 ⊗ 管流 ≠ 壁面射流", 1.85, TEAL, "start", sw=0.14)
    c.text(0, y_end + 16.6, "回液上抽在 ±X 端（图面前后），本视只看见进出纸面",
           1.8, GREY, "middle", cn=True)
    return c.autofit(5.0).render()


# ============================================================
# 图 4 · 冲击三区示意
# ============================================================
def fig_three_regions():
    c = Canvas((0, 0, 10, 10),
               aria="冲击射流三区：自由射流、驻点、壁面射流",
               label="reg")
    ox, oy, W, gap = 6.0, 10.0, 78.0, 22.0
    lid_h, h_h, base_h = 10.0, 28.0, 11.0
    c.rect(ox, oy, W, lid_h, "#e8b97f", INK, 0.35)
    hole_w = 5.2
    c.rect(ox + W / 2 - hole_w / 2, oy, hole_w, lid_h, WATER, BLUE, 0.3)
    c.rect(ox, oy + lid_h, W, gap, "#eaf6fd", BLUE, 0.3)
    c.rect(ox, oy + lid_h + gap, W, base_h, CU, INK, 0.35)

    # 射流柱 + 势核
    mid = ox + W / 2
    c.poly([(mid - 2.4, oy + lid_h), (mid + 2.4, oy + lid_h),
            (mid + 6.5, oy + lid_h + gap), (mid - 6.5, oy + lid_h + gap)],
           "#90cdf4", BLUE, 0.28)
    c.poly([(mid - 1.5, oy + lid_h), (mid + 1.5, oy + lid_h),
            (mid + 1.9, oy + lid_h + 14), (mid - 1.9, oy + lid_h + 14)],
           "#2b6cb0", "none", 0)
    c.arrow(mid, oy + lid_h + 1.5, mid, oy + lid_h + gap - 2.2, BLUE, 0.7)
    c.circle(mid, oy + lid_h + gap - 1.2, 2.1, RED, "none", 0)
    c.arrow(mid - 3.2, oy + lid_h + gap + 1.6, ox + 6, oy + lid_h + gap + 1.6,
            ORANGE, 0.7)
    c.arrow(mid + 3.2, oy + lid_h + gap + 1.6, ox + W - 6,
            oy + lid_h + gap + 1.6, ORANGE, 0.7)

    # 三区色带
    c.rect(ox + 1.2, oy + lid_h + 1.2, 14, gap - 2.4, "#bee3f8", "none", 0,
           extra='opacity="0.35"')
    c.rect(mid - 8, oy + lid_h + gap - 7.5, 16, 9.5, "#feb2b2", "none", 0,
           extra='opacity="0.40"')
    c.rect(ox + 4, oy + lid_h + gap + 0.3, W - 8, 5.2, "#fbd38d", "none", 0,
           extra='opacity="0.45"')

    c.text(ox + 10, oy + lid_h + 13, "①", 3.4, BLUE, "middle", weight="bold")
    c.text(mid + 6.8, oy + lid_h + gap + 7.2, "②", 3.4, RED, "middle",
           weight="bold")
    c.text(ox + 18, oy + lid_h + gap + 8.8, "③", 3.2, ORANGE, "middle",
           weight="bold")
    c.text(mid, oy + 7.2, "D = 0.40（默认 0.50）", 2.15, BLUE, "middle", cn=True)
    c.dim_v(oy + lid_h, oy + lid_h + gap, ox - 2.2, "H=2.0", 2.0,
            ext=1.1, left=True, color=BLUE, sw=0.16)

    rows = [
        (BLUE, "① 自由射流", "孔口到铜壁之间的竖直射流。势核尚未散尽；H/D≈5（若用默认 ⌀0.50 则 =4）。它还不是壁面射流。"),
        (RED, "② 驻点", "打到壁上，轴向动量转成径向。边界层最薄，局部 h 最高。只有中槽正对这个核。"),
        (ORANGE, "③ 壁面射流", "转过 90° 后贴壁刮过去的薄高速剪切层。侧槽的对流主要靠它，h 大约是驻点的 0.4–0.7。"),
    ]
    y = oy + lid_h + gap + base_h + 8
    for col, t, s in rows:
        c.rect(ox, y - 3.6, 3.2, 8.6, col, "none", 0, rx=0.6)
        c.text(ox + 5.2, y, t, 2.45, col, "start", cn=True, weight="bold")
        c.text(ox + 5.2, y + 3.6, s, 1.95, GREY, "start", cn=True)
        y += 11.2

    y += 1.5
    c.rect(ox, y - 3.4, 3.2, 10.2, TEAL, "none", 0, rx=0.6)
    c.text(ox + 5.2, y, "不是壁面射流", 2.45, TEAL, "start", cn=True,
           weight="bold")
    c.text(ox + 5.2, y + 3.6,
           "竖直射流本身不是；槽深 1.50 mm 里已经转成导管流的那部分也不是。",
           1.95, GREY, "start", cn=True)
    c._t((ox + W + 8, y + 8))
    return c.autofit(4.5).render()


def all_figs():
    return [
        ("fig_section_xz", fig_section_xz),
        ("fig_plan_xy", fig_plan_xy),
        ("fig_end_yz", fig_end_yz),
        ("fig_three_regions", fig_three_regions),
    ]


def overflow_report():
    """返回 [(name, overflow_tag)]，空列表表示全部未裁切。"""
    import svg as S
    bad = []
    rows = []
    orig = S.Canvas.render
    for name, fn in all_figs():
        cap = {}

        def hook(self, cls="svgfig", _c=cap, _o=orig):
            _c["bb"] = self.bbox()
            _c["vb"] = self.vb
            return _o(self, cls)

        S.Canvas.render = hook
        fn()
        S.Canvas.render = orig
        bb, vb = cap.get("bb"), cap.get("vb")
        if not bb or not vb:
            bad.append((name, "no-bbox"))
            continue
        x0, y0, w, h = vb
        ov = (max(0.0, x0 - bb[0]), max(0.0, y0 - bb[1]),
              max(0.0, bb[2] - (x0 + w)), max(0.0, bb[3] - (y0 + h)))
        tag = ""
        if max(ov) > 0.35:
            tag = f"L{ov[0]:.1f} T{ov[1]:.1f} R{ov[2]:.1f} B{ov[3]:.1f}"
            bad.append((name, tag))
        rows.append((name, vb, bb, tag))
    return bad, rows
