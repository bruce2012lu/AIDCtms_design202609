# -*- coding: utf-8 -*-
"""详细设计图纸（2D / 3D / 爆炸），1 SVG 单位 = 1 mm。"""
import math
import model as M
from svg import (Canvas, iso, iso_box, INK, BLUE, TEAL, ORANGE, RED, GREY,
                 CU, CU_D, WATER, FIN)

G = M.GEO
PW, PH, PT = G["plate_L"], G["plate_W"], G["plate_T"]
HBM_Y = [G["hbm_y0"] + i * G["hbm_dy"] for i in range(4)]


def Y(y):
    """工程 Y 向上 -> SVG Y 向下"""
    return PH - y


def _jet_xy():
    """两 die 的 9×12 孔中心。X 节距 3.0 mm，Y 节距 2.4 mm。"""
    out = []
    for ax in (G["jet_a_x"], G["jet_a_x"] + G["die_w"] + G["hbi"]):
        for i in range(G["n_jet_x"]):
            for j in range(G["n_jet_y"]):
                out.append((ax + i * G["S_jet_x"],
                            G["jet_a_y"] + j * G["S_jet_y"]))
    return out


# ============================================================
# F8 · 分区顶视（布置基准）
# ============================================================
def fig_layout():
    c = Canvas((-20, -16, 138, 112),
               aria="95x75 mm cold plate top view zoning")
    hot = c.grad("hotA", [("0%", "#e53e3e"), ("55%", "#ed8936"),
                          ("100%", "#f6e05e")], radial=True)

    # 外形与压装让位
    c.rect(0, Y(PH), PW, PH, "#f7fafc", INK, 0.5)
    c.rect(3, Y(PH - 3), PW - 6, PH - 6, "none", GREY, 0.15,
           extra='stroke-dasharray="1.2 0.8"')

    # 歧管带
    c.rect(G["man_x"], Y(G["man_in_y"] + G["man_h"]), G["man_w"], G["man_h"],
           WATER, BLUE, 0.25)
    c.rect(G["man_x"], Y(G["man_out_y"] + G["man_h"]), G["man_w"], G["man_h"],
           "#fbd38d", ORANGE, 0.25)

    # 隔离肋
    for rx in (G["rib_x_l"], G["rib_x_r"]):
        c.rect(rx, Y(G["rib_y0"] + G["rib_len"]), G["rib"], G["rib_len"],
               INK, INK, 0.1)
    for ry in (21.5, 51.5):
        c.rect(G["die_a_x"], Y(ry + G["rib"]), 57, G["rib"], "#1a365d",
               "#1a365d", 0.1)

    # HBM
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        for hy in HBM_Y:
            c.rect(hx, Y(hy + G["hbm_h"]), G["hbm_w"], G["hbm_h"],
                   "#c6f6d5", "#276749", 0.25)

    # die + HBI
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        c.rect(dx, Y(G["die_a_y"] + G["die_h"]), G["die_w"], G["die_h"],
               hot, INK, 0.35)
    c.rect(G["die_a_x"] + G["die_w"], Y(G["die_a_y"] + G["die_h"]), G["hbi"],
           G["die_h"], TEAL, TEAL, 0.2)

    # 射流落点
    for x, y in _jet_xy():
        c.circle(x, Y(y), 0.36, TEAL, "none", 0)

    # 流向
    c.arrow(47.5, Y(PH + 2), 47.5, Y(PH - 5.5), BLUE, 0.7)
    for x in (32.5, 62.5):
        c.arrow(x, Y(65.5), x, Y(53.5), BLUE, 0.55)
        c.arrow(x, Y(21.5), x, Y(10), ORANGE, 0.55)
    for x in (10.5, 84.5):
        c.arrow(x, Y(63), x, Y(12), TEAL, 0.4)
    c.arrow(47.5, Y(5.5), 47.5, Y(-3), ORANGE, 0.7)

    # 标注
    c.dim_h(0, PW, Y(PH) - 9, "95", 3.1)
    c.dim_v(Y(0), Y(PH), PW + 5, "75", 3.1)
    c.text(50.5, Y(PH + 1.5), "IN", 2.8, BLUE)
    c.text(50.5, Y(-4.5), "OUT", 2.8, ORANGE)
    for x, t in ((32.5, "Die-A"), (62.5, "Die-B")):
        c.text(x, Y(37.5) + 0.9, t, 2.6, INK, "middle", weight="bold")
    c.text(47.5, Y(39.5), "HBI", 1.7, "#fff", "middle")
    for x in (10.5, 84.5):
        c.text(x, Y(57) + 0.8, "HBM", 2.2, "#276749", "middle")
    c.leader(G["rib_x_l"] + G["rib"] / 2, Y(30), -19, Y(28),
             "隔离肋 2×（宽 2）", 2.2, INK, "start")

    # 比例尺
    c.line(0, Y(-12), 20, Y(-12), INK, 0.7)
    for x in (0, 20):
        c.line(x, Y(-10.6), x, Y(-13.4), INK, 0.4)
    c.text(10, Y(-16), "20 mm", 2.6, INK, "middle")
    c.text(0, Y(-20), "原点左下（工程 Y 向上）· 候选外形 · 待 ICD",
           2.3, GREY, cn=True)
    return c.render()


# ============================================================
# A0 · 外形三视图 + 标题栏
# ============================================================
def fig_3view():
    W, H = 250, 190
    c = Canvas((0, 0, W, H), aria="Three view drawing of CP-B300-JM-01")
    # 图框
    c.rect(3, 3, W - 6, H - 6, "none", INK, 0.6)
    c.rect(6, 6, W - 12, H - 12, "none", INK, 0.25)

    # ---- 俯视图 ----
    ox, oy = 22, 16
    c.text(ox, oy - 4, "俯视图  TOP  1:1", 3.4, INK, cn=True, weight="bold")
    g = lambda x, y: (ox + x, oy + (PH - y))
    c.rect(ox, oy, PW, PH, "#f7fafc", INK, 0.5)
    c.rect(ox + G["man_x"], oy + (PH - G["man_in_y"] - G["man_h"]),
           G["man_w"], G["man_h"], WATER, BLUE, 0.22)
    c.rect(ox + G["man_x"], oy + (PH - G["man_out_y"] - G["man_h"]),
           G["man_w"], G["man_h"], "#fbd38d", ORANGE, 0.22)
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        c.rect(ox + dx, oy + (PH - G["die_a_y"] - G["die_h"]), G["die_w"],
               G["die_h"], "none", INK, 0.3,
               extra='stroke-dasharray="2 1"')
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        for hy in HBM_Y:
            c.rect(ox + hx, oy + (PH - hy - G["hbm_h"]), G["hbm_w"],
                   G["hbm_h"], "none", "#276749", 0.22,
                   extra='stroke-dasharray="1.4 0.9"')
    # 安装孔 4x M3 沉台
    holes = [(4.5, 4.5), (PW - 4.5, 4.5), (4.5, PH - 4.5), (PW - 4.5, PH - 4.5)]
    for hx, hy in holes:
        cx, cy = g(hx, hy)
        c.circle(cx, cy, 1.6, "#fff", INK, 0.25)
        c.centermark(cx, cy, 3.0)
    # 水嘴中心
    for yy, col in ((G["man_in_y"] + 3.5, BLUE),
                    (G["man_out_y"] + 3.5, ORANGE)):
        cx, cy = g(47.5, yy)
        c.circle(cx, cy, 3.2, "none", col, 0.3)
        c.centermark(cx, cy, 5.0, col)
    # 尺寸
    c.dim_h(ox, ox + PW, oy - 9, "95", 3.0)
    c.dim_v(oy, oy + PH, ox + PW + 8, "75", 3.0)
    c.dim_h(ox, ox + 4.5, oy + PH + 6, "4.5", 2.4, below=True)
    c.dim_h(ox, ox + 47.5, oy + PH + 13, "47.5 (水嘴中心)", 2.4, below=True)
    c.dim_v(oy + PH - 4.5, oy + PH, ox - 8, "4.5", 2.4, left=True)
    c.leader(ox + 4.5, oy + PH - 4.5, ox - 6, oy + PH + 22,
             "4× ⌀3.4 沉孔（压装螺钉，待 ICD）", 2.3, INK, "start")
    c.section_mark(ox - 4, oy + (PH - 37.5), 1, "A")
    c.section_mark(ox + PW + 4, oy + (PH - 37.5), -1, "A")
    c.section_mark(ox - 4, oy + (PH - 57), 1, "B")
    c.section_mark(ox + PW + 4, oy + (PH - 57), -1, "B")

    # ---- 主视图 ----
    fy = oy + PH + 34
    c.text(ox, fy - 4, "主视图  FRONT  1:1", 3.4, INK, cn=True, weight="bold")
    c.rect(ox, fy, PW, PT, CU, INK, 0.5)
    c.line(ox, fy + G["t_lid"], ox + PW, fy + G["t_lid"], GREY, 0.2,
           'stroke-dasharray="1.6 1"')
    c.line(ox, fy + PT - G["t_base"], ox + PW, fy + PT - G["t_base"], GREY,
           0.2, 'stroke-dasharray="1.6 1"')
    # 水嘴
    c.rect(ox + 40, fy - 7, 7, 7, "#cbd5e0", INK, 0.35)
    c.rect(ox + 48, fy - 7, 7, 7, "#cbd5e0", INK, 0.35)
    c.text(ox + 43.5, fy - 8.6, "IN", 2.4, BLUE, "middle")
    c.text(ox + 51.5, fy - 8.6, "OUT", 2.4, ORANGE, "middle")
    c.dim_v(fy, fy + PT, ox + PW + 8, "8.5", 3.0)
    c.dim_v(fy - 7, fy, ox + PW + 20, "7", 2.4)
    c.leader(ox + 20, fy + G["t_lid"], ox + 8, fy + 22,
             "喷嘴盖板 t2.5", 2.3, INK)
    c.leader(ox + 70, fy + PT - 1, ox + 74, fy + 22, "换热底板 t3.5",
             2.3, INK)

    # ---- 左视图 ----
    sx = ox + PW + 34
    c.text(sx, fy - 4, "左视图  SIDE  1:1", 3.4, INK, cn=True, weight="bold")
    c.rect(sx, fy, PH, PT, CU, INK, 0.5)
    c.line(sx, fy + G["t_lid"], sx + PH, fy + G["t_lid"], GREY, 0.2,
           'stroke-dasharray="1.6 1"')
    c.dim_h(sx, sx + PH, fy + PT + 7, "75", 3.0, below=True)
    c.dim_v(fy, fy + PT, sx + PH + 7, "8.5", 3.0)

    # ---- 标题栏 ----
    tx, ty, tw, th = W - 105, H - 40, 99, 34
    c.rect(tx, ty, tw, th, "#f6f9fc", INK, 0.45)
    rows = [
        ("图号 DWG NO.", "JM01-A0"),
        ("名称 TITLE", "冷板外形三视图 / CP-B300-JM-01"),
        ("材料 MATL", "C110 紫铜（本体）"),
        ("比例 SCALE", "1:1"),
        ("单位 UNIT", "mm"),
        ("状态 STATUS", "候选 CANDIDATE · 待 ICD 冻结"),
    ]
    rh = th / len(rows)
    for i, (k, v) in enumerate(rows):
        yy = ty + i * rh
        c.line(tx, yy, tx + tw, yy, INK, 0.2)
        c.line(tx + 30, yy, tx + 30, yy + rh, INK, 0.2)
        c.text(tx + 1.5, yy + rh * 0.68, k, 2.4, GREY, cn=True)
        c.text(tx + 31.5, yy + rh * 0.68, v, 2.5, INK, cn=True)
    c.line(tx + 30, ty, tx + 30, ty + th, INK, 0.2)

    c.text(10, H - 10, "公差未注：线性 ±0.1｜接触面平面度 0.05｜Ra ≤0.8 μm"
                        "｜第三视角投影", 2.6, GREY, cn=True)
    return c.render()


# ============================================================
# A1 · 底板流道平面图
# ============================================================
def fig_base_plan():
    c = Canvas((-22, -18, 142, 118), aria="Base plate channel plan")
    c.rect(0, Y(PH), PW, PH, "#fffaf3", INK, 0.5)

    # HBM 区通道（沿 Y 长边）
    for hx in (G["hbm_x_l"] - 1, G["hbm_x_r"] - 1):
        n = 8
        for i in range(n):
            x = hx + 0.7 + i * 1.6
            c.rect(x, Y(62.5), G["hbm_ch_w"], 50, FIN, "none", 0)
    # GPU 区短槽（沿 X，节距 0.8）
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        for k in range(M.N_CH_DIE):
            y = G["die_a_y"] + k * G["ch_p"]
            c.rect(dx, Y(y + G["ch_w"]), G["die_w"], G["ch_w"],
                   "#2c7a7b", "none", 0)
    # 回液缝（盖板投影，虚线）
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        for xo in (0, 13.5, 27):
            c.line(dx + xo, Y(G["die_a_y"]), dx + xo,
                   Y(G["die_a_y"] + G["die_h"]), ORANGE, 0.3,
                   'stroke-dasharray="1.5 1"')
    # 隔离肋
    for rx in (G["rib_x_l"], G["rib_x_r"]):
        c.rect(rx, Y(G["rib_y0"] + G["rib_len"]), G["rib"], G["rib_len"],
               INK, INK, 0.1)
    for ry in (21.5, 51.5):
        c.rect(G["die_a_x"], Y(ry + G["rib"]), 57, G["rib"], "#1a365d",
               "#1a365d", 0.1)
    # die 轮廓
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        c.rect(dx, Y(G["die_a_y"] + G["die_h"]), G["die_w"], G["die_h"],
               "none", RED, 0.3, extra='stroke-dasharray="2.2 1.2"')

    # 尺寸链
    c.dim_h(0, PW, Y(PH) - 10, "95", 3.0)
    c.dim_v(Y(0), Y(PH), PW + 6, "75", 3.0)
    c.dim_h(G["hbm_x_l"], G["hbm_x_l"] + G["hbm_w"], Y(64.5), "11", 2.2)
    c.dim_h(G["rib_x_l"], G["rib_x_l"] + G["rib"], Y(68), "2", 2.2)
    c.dim_h(G["die_a_x"], G["die_a_x"] + G["die_w"], Y(64.5), "27", 2.4)
    c.dim_h(46, 49, Y(68), "3", 2.2)
    c.dim_v(Y(G["die_a_y"]), Y(G["die_a_y"] + G["die_h"]), -6, "28", 2.4,
            left=True)
    c.dim_v(Y(G["rib_y0"]), Y(G["rib_y0"] + G["rib_len"]), -14, "50", 2.4,
            left=True)
    c.dim_h(0, G["die_a_x"], Y(-6), "19", 2.2, below=True)
    c.dim_h(0, G["hbm_x_l"], Y(-12), "5", 2.2, below=True)

    c.leader(G["die_a_x"] + 8, Y(G["die_a_y"] + 10), 30, Y(-14),
             "GPU 短槽 0.40 宽 × 1.50 深 · 节距 0.80 · 35 条/die",
             2.4, "#2c7a7b")
    c.leader(G["hbm_x_l"] + 3, Y(40), -18, Y(78),
             "HBM 槽 0.60×1.50 · 无喷嘴", 2.4, TEAL)
    c.leader(G["die_a_x"] + 13.5, Y(G["die_a_y"] + 24), 62, Y(80),
             "盖板回液缝（投影）· 槽内流程 ≤ 8", 2.4, ORANGE)
    c.text(0, Y(-20), "图号 JM01-A1 · 底板流道平面 · 1:1 · "
                      "槽/肋为示意密度，实际条数见表", 2.4, GREY, cn=True)
    return c.render()


# ============================================================
# A2 / A3 · 剖面
# ============================================================
def _stack_section(c, x0, w, jets=True, label_dims=True):
    """通用铜层叠剖面。返回各层 y 坐标"""
    y_lid = 0.0
    y_gap = y_lid + G["t_lid"]
    y_ch = y_gap + G["H_jet"]
    y_bot = y_ch + G["ch_h"]
    y_end = y_bot + G["base_cu"]
    hatch = c.hatch("cuh", CU_D, 0.06, 0.7, 45)

    # 盖板
    c.rect(x0, y_lid, w, G["t_lid"], hatch, INK, 0.1)
    c.rect(x0, y_lid, w, G["t_lid"], "none", INK, 0.12)
    # 射流间隙
    c.rect(x0, y_gap, w, G["H_jet"], WATER, BLUE, 0.08)
    # 槽层
    c.rect(x0, y_ch, w, G["ch_h"], hatch, INK, 0.1)
    c.rect(x0, y_ch, w, G["ch_h"], "none", INK, 0.12)
    # 余铜
    c.rect(x0, y_bot, w, G["base_cu"], hatch, INK, 0.1)
    c.rect(x0, y_bot, w, G["base_cu"], "none", INK, 0.12)
    return y_lid, y_gap, y_ch, y_bot, y_end


def fig_section_gpu():
    w = 30.0
    c = Canvas((-9, -7, 56, 26), aria="Section A-A through GPU jet zone")
    y_lid, y_gap, y_ch, y_bot, y_end = _stack_section(c, 0, w)

    # 喷嘴孔 + 射流
    xs = [1.5 + i * G["S_jet_x"] for i in range(10)]
    for x in xs:
        c.rect(x - G["D_jet"] / 2, y_lid, G["D_jet"], G["t_lid"], WATER,
               BLUE, 0.05)
        c.arrow(x, y_lid + 0.2, x, y_ch + G["ch_h"] - 0.25, BLUE, 0.12)
        c.circle(x, y_bot - 0.08, 0.14, RED, "none", 0)
    # 槽（沿剖面看到的是肋端面）
    for i in range(int(w / G["ch_p"])):
        x = 0.2 + i * G["ch_p"]
        c.rect(x, y_ch, G["ch_w"], G["ch_h"], FIN, "none", 0)
    # 回液缝
    for x in (0.0, 13.5, 27.0):
        c.rect(x, y_gap, 0.8, G["H_jet"], "#fbd38d", ORANGE, 0.06)
        c.arrow(x + 0.4, y_ch + 0.2, x + 0.4, y_lid - 1.6, ORANGE, 0.14)
    # TIM2 / 盖 / TIM1 / 硅
    c.rect(0, y_end, w, 0.10, "#f6e05e", "none", 0)
    c.rect(0, y_end + 0.10, w, 1.0, "#cbd5e0", GREY, 0.06)
    c.rect(0, y_end + 1.10, w, 0.05, "#f6e05e", "none", 0)
    c.rect(2, y_end + 1.15, w - 4, 0.8, "#4a5568", "none", 0)

    # 尺寸链
    xd = w + 3.5
    c.dim_v(y_lid, y_gap, xd, "2.5", 1.0, ext=0.5)
    c.dim_v(y_gap, y_ch, xd, "H=2.0", 1.0, ext=0.5, color=BLUE)
    c.dim_v(y_ch, y_bot, xd, "1.5", 1.0, ext=0.5)
    c.dim_v(y_bot, y_end, xd, "2.0", 1.0, ext=0.5)
    c.dim_v(y_lid, y_end, xd + 8.5, "8.0 腔", 1.1, ext=0.5)
    c.dim_h(1.5, 4.5, -2.2, "S=3.0", 1.0, ext=0.4)
    c.leader(1.5, y_lid + 1.2, -8, -4.2, "⌀0.50 喷嘴", 1.1, BLUE)
    c.leader(13.9, y_gap + 1.0, 16, -4.2, "回液缝 0.8", 1.1, ORANGE)
    c.leader(6.0, y_ch + 0.8, 34, -4.2, "短槽 0.40×1.50", 1.1, "#2c7a7b")
    c.text(0, y_end + 3.6, "下方薄层：TIM2 0.10 / 封装盖 1.0 / TIM1 0.05 / 硅"
                            "（非本供货）", 1.05, GREY, cn=True)
    c.text(0, y_end + 5.2, "图号 JM01-A2 · 剖面 A-A（过 Die-A 中心）· 1:1 真比例"
                            "· 水缝不得画得比余铜厚", 1.05, GREY, cn=True)
    return c.render()


def fig_section_hbm():
    w = 30.0
    c = Canvas((-9, -7, 56, 26), aria="Section B-B through HBM zone, no jets")
    hatch = c.hatch("cuh2", CU_D, 0.06, 0.7, 45)
    y_lid = 0.0
    y_gap = y_lid + G["t_lid"]
    y_ch = y_gap + G["H_jet"]
    y_bot = y_ch + G["hbm_ch_h"]
    y_end = y_bot + G["base_cu"]

    c.rect(0, y_lid, w, G["t_lid"], hatch, INK, 0.1)
    c.rect(0, y_lid, w, G["t_lid"], "none", INK, 0.12)
    c.rect(0, y_gap, w, G["H_jet"], WATER, BLUE, 0.08)
    c.rect(0, y_ch, w, G["hbm_ch_h"], hatch, INK, 0.1)
    c.rect(0, y_ch, w, G["hbm_ch_h"], "none", INK, 0.12)
    c.rect(0, y_bot, w, G["base_cu"], hatch, INK, 0.1)
    c.rect(0, y_bot, w, G["base_cu"], "none", INK, 0.12)

    # 宽槽
    for i in range(int(w / 1.6)):
        x = 0.3 + i * 1.6
        c.rect(x, y_ch, G["hbm_ch_w"], G["hbm_ch_h"], FIN, "none", 0)
    # 平流（垂直纸面，用点表示）
    for i in range(int(w / 1.6)):
        x = 0.3 + i * 1.6 + G["hbm_ch_w"] / 2
        c.circle(x, y_ch + G["hbm_ch_h"] / 2, 0.16, "#fff", TEAL, 0.06)
        c.circle(x, y_ch + G["hbm_ch_h"] / 2, 0.06, TEAL, "none", 0)
    c.text(w / 2, y_gap + 1.3, "盖板此区无喷嘴（权项必要特征）", 1.15, RED,
           "middle", cn=True, weight="bold")

    c.rect(0, y_end, w, 0.10, "#f6e05e", "none", 0)
    c.rect(0, y_end + 0.10, w, 1.0, "#cbd5e0", GREY, 0.06)
    c.rect(3, y_end + 1.15, 8, 0.9, "#276749", "none", 0)
    c.rect(15, y_end + 1.15, 8, 0.9, "#276749", "none", 0)
    c.text(w / 2, y_end + 3.4, "下方：TIM2 / 封装盖 / HBM 12-Hi 堆叠（绿）",
           1.05, GREY, "middle", cn=True)

    xd = w + 3.5
    c.dim_v(y_lid, y_gap, xd, "2.5", 1.0, ext=0.5)
    c.dim_v(y_gap, y_ch, xd, "2.0", 1.0, ext=0.5, color=BLUE)
    c.dim_v(y_ch, y_bot, xd, "1.5", 1.0, ext=0.5)
    c.dim_v(y_bot, y_end, xd, "2.0", 1.0, ext=0.5)
    c.dim_h(0.3, 1.9, -2.2, "1.6 节距", 1.0, ext=0.4)
    c.leader(0.6, y_ch + 0.75, -8, -4.2, "槽宽 0.60", 1.1, "#2c7a7b")
    c.text(0, y_end + 5.0, "图号 JM01-A3 · 剖面 B-B（过 HBM 列）· 1:1 · "
                            "近壁 V ≤ 0.80 m/s", 1.05, GREY, cn=True)
    return c.render()


# ============================================================
# A4 · 射流单元详图
# ============================================================
def fig_unit_cell():
    c = Canvas((-4.5, -3.5, 17, 16), aria="Jet unit cell detail to scale")
    hatch = c.hatch("cuh3", CU_D, 0.05, 0.5, 45)
    S = G["S_jet_x"]
    y_lid, y_gap = 0.0, G["t_lid"]
    y_ch = y_gap + G["H_jet"]
    y_bot = y_ch + G["ch_h"]
    y_end = y_bot + G["base_cu"]

    c.rect(0, y_lid, S, G["t_lid"], hatch, INK, 0.06)
    c.rect(0, y_lid, S, G["t_lid"], "none", INK, 0.07)
    c.rect(S / 2 - G["D_jet"] / 2, y_lid, G["D_jet"], G["t_lid"], WATER,
           BLUE, 0.04)
    c.rect(0, y_gap, S, G["H_jet"], WATER, BLUE, 0.05)
    c.rect(0, y_ch, S, G["ch_h"], hatch, INK, 0.06)
    c.rect(0, y_ch, S, G["ch_h"], "none", INK, 0.07)
    c.rect(0, y_bot, S, G["base_cu"], hatch, INK, 0.06)
    c.rect(0, y_bot, S, G["base_cu"], "none", INK, 0.07)
    c.rect(0, y_ch, G["ch_w"], G["ch_h"], FIN, "none", 0)
    c.rect(S - G["ch_w"], y_ch, G["ch_w"], G["ch_h"], "#f6ad55", "none", 0)

    c.arrow(S / 2, y_lid + 0.1, S / 2, y_bot - 0.12, BLUE, 0.08)
    c.circle(S / 2, y_bot - 0.06, 0.12, RED, "none", 0)
    c.line(S / 2, y_bot - 0.1, 0.3, y_bot - 0.1, ORANGE, 0.07)
    c.line(S / 2, y_bot - 0.1, S - 0.3, y_bot - 0.1, ORANGE, 0.07)
    c.arrow(0.2, y_bot - 0.3, 0.2, y_lid + 0.2, ORANGE, 0.07)
    c.arrow(S - 0.2, y_bot - 0.3, S - 0.2, y_lid + 0.2, ORANGE, 0.07)

    xd = S + 1.0
    c.dim_v(y_lid, y_gap, xd, "2.5", 0.5, ext=0.22, sw=0.05)
    c.dim_v(y_gap, y_ch, xd, "H 2.0", 0.5, ext=0.22, color=BLUE, sw=0.05)
    c.dim_v(y_ch, y_bot, xd, "1.5", 0.5, ext=0.22, sw=0.05)
    c.dim_v(y_bot, y_end, xd, "2.0", 0.5, ext=0.22, sw=0.05)
    c.dim_h(0, S, y_end + 1.1, "S = 3.0", 0.55, ext=0.22, below=True,
            sw=0.05)
    # ⌀0.50 太小，用引出标注而非尺寸线
    c.leader(S / 2, y_lid + G["t_lid"] * 0.4, -3.6, -1.4, "⌀0.50 喷嘴",
             0.5, BLUE, "start", sw=0.05)
    c.text(S / 2, y_end + 3.0, "H/D = 4 · S/D = 6 · 驻点 → 壁面射流 → "
                                "两侧上抽", 0.52, GREY, "middle", cn=True)
    c.text(S / 2, y_end + 4.0, "图号 JM01-A4 · 射流单元 · 每 die 重复 8×8",
           0.52, GREY, "middle", cn=True)
    return c.render()


# ============================================================
# A5 · 盖板孔位图
# ============================================================
def fig_lid_holes():
    c = Canvas((-20, -16, 138, 116), aria="Lid orifice pattern")
    c.rect(0, Y(PH), PW, PH, "#fbfdff", INK, 0.5)
    c.rect(G["man_x"], Y(G["man_in_y"] + G["man_h"]), G["man_w"], G["man_h"],
           WATER, BLUE, 0.25)
    c.rect(G["man_x"], Y(G["man_out_y"] + G["man_h"]), G["man_w"], G["man_h"],
           "#fbd38d", ORANGE, 0.25)
    # 孔
    for x, y in _jet_xy():
        c.circle(x, Y(y), G["D_jet"] / 2 * 2.6, "#fff", BLUE, 0.14)
    # 阵列框与基准
    for ax in (G["jet_a_x"], G["jet_a_x"] + G["die_w"] + G["hbi"]):
        c.rect(ax - 1.5, Y(G["jet_a_y"] + G["jet_span"] + 1.5),
               G["jet_span"] + 3, G["jet_span"] + 3, "none", GREY, 0.2,
               extra='stroke-dasharray="1.6 1"')
        c.centermark(ax + G["jet_span"] / 2, Y(G["jet_a_y"] +
                     G["jet_span"] / 2), 13, GREY, 0.12)
    # HBM 区明确无孔
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        c.rect(hx, Y(G["rib_y0"] + G["rib_len"]), G["hbm_w"], G["rib_len"],
               "#f0fff4", "#276749", 0.2,
               extra='stroke-dasharray="2 1.2"')
        c.text(hx + G["hbm_w"] / 2, Y(37), "无", 4.0, "#276749", "middle",
               cn=True, weight="bold")
        c.text(hx + G["hbm_w"] / 2, Y(31), "喷嘴", 2.4, "#276749", "middle",
               cn=True)
    # 回液缝
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        for xo in (0, 13.5, 27):
            c.rect(dx + xo - 0.4, Y(G["die_a_y"] + G["die_h"]), 0.8,
                   G["die_h"], "#fbd38d", ORANGE, 0.12)

    c.dim_h(0, G["jet_a_x"], Y(-7), f"{G['jet_a_x']:.1f}", 2.3, below=True)
    c.dim_h(G["jet_a_x"], G["jet_a_x"] + G["jet_span_x"], Y(64.5),
            f"{G['jet_span_x']:.1f} = 8×3.0", 2.3)
    c.dim_h(G["jet_a_x"], G["jet_a_x"] + G["S_jet_x"], Y(69), "3.0", 2.2)
    c.dim_v(Y(0), Y(G["jet_a_y"]), -6, f"{G['jet_a_y']:.1f}", 2.3, left=True)
    c.dim_v(Y(G["jet_a_y"]), Y(G["jet_a_y"] + G["jet_span_y"]), -14,
            f"{G['jet_span_y']:.1f} = 11×2.4", 2.3, left=True)
    c.dim_h(0, PW, Y(PH) - 10, "95", 3.0)
    c.leader(G["jet_a_x"], Y(G["jet_a_y"]), 20, Y(-14),
             f"{M.N_JET}× ⌀0.50 +0.03/0 · 9×12 / die", 2.4, BLUE)
    c.text(0, Y(-21), "图号 JM01-A5 · 喷嘴盖板孔位 · 1:1 · 孔按真位置绘制"
                      "（图示直径放大 2.6× 以便看清）", 2.3, GREY, cn=True)
    return c.render()


# ============================================================
# 3D 等轴测装配
# ============================================================
def fig_iso():
    SC = 2.1
    c = Canvas((-135, -125, 290, 215), aria="Isometric assembly view")
    P = lambda x, y, z: iso(x, y, z, SC)

    # 底板本体
    iso_box(c, 0, 0, 0, PW, PH, G["t_base"], CU, CU_D, "#a5683c",
            INK, 0.35, SC)
    # 盖板
    iso_box(c, 0, 0, G["t_base"] + 0.6, PW, PH, G["t_lid"], "#e8b97f",
            "#c98d57", "#b07b48", INK, 0.35, SC)

    # 顶面纹理：两片射流区 + HBM 列
    for ax in (G["jet_a_x"], G["jet_a_x"] + G["die_w"] + G["hbi"]):
        pts = [P(ax, G["jet_a_y"], G["t_base"] + 0.6 + G["t_lid"]),
               P(ax + G["jet_span"], G["jet_a_y"],
                 G["t_base"] + 0.6 + G["t_lid"]),
               P(ax + G["jet_span"], G["jet_a_y"] + G["jet_span"],
                 G["t_base"] + 0.6 + G["t_lid"]),
               P(ax, G["jet_a_y"] + G["jet_span"],
                 G["t_base"] + 0.6 + G["t_lid"])]
        c.poly(pts, "#2b6cb022", BLUE, 0.4)
        for i in range(8):
            for j in range(8):
                sx, sy = P(ax + i * 3, G["jet_a_y"] + j * 3,
                           G["t_base"] + 0.6 + G["t_lid"])
                c.circle(sx, sy, 0.7, "#fff", BLUE, 0.25)
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        pts = [P(hx, G["rib_y0"], G["t_base"] + 0.6 + G["t_lid"]),
               P(hx + G["hbm_w"], G["rib_y0"],
                 G["t_base"] + 0.6 + G["t_lid"]),
               P(hx + G["hbm_w"], G["rib_y0"] + G["rib_len"],
                 G["t_base"] + 0.6 + G["t_lid"]),
               P(hx, G["rib_y0"] + G["rib_len"],
                 G["t_base"] + 0.6 + G["t_lid"])]
        c.poly(pts, "#c6f6d544", "#276749", 0.4)

    # 水嘴
    for xx, col, tag in ((36, BLUE, "IN"), (54, ORANGE, "OUT")):
        iso_box(c, xx, PH - 9, G["t_base"] + 0.6 + G["t_lid"], 7, 7, 9,
                "#e2e8f0", "#cbd5e0", "#b6c2d2", INK, 0.3, SC)
        sx, sy = P(xx + 3.5, PH - 5.5, G["t_base"] + 0.6 + G["t_lid"] + 9)
        c.circle(sx, sy, 2.0, "#fff", col, 0.5)
        c.text(sx, sy - 5.5, tag, 6.0, col, "middle", weight="bold")

    # 流向
    ain = P(39.5, PH - 5.5, G["t_base"] + G["t_lid"] + 24)
    ain2 = P(39.5, PH - 5.5, G["t_base"] + G["t_lid"] + 11)
    c.arrow(ain[0], ain[1], ain2[0], ain2[1], BLUE, 1.4)
    aout = P(57.5, PH - 5.5, G["t_base"] + G["t_lid"] + 11)
    aout2 = P(57.5, PH - 5.5, G["t_base"] + G["t_lid"] + 24)
    c.arrow(aout[0], aout[1], aout2[0], aout2[1], ORANGE, 1.4)

    # 坐标轴
    o = P(-16, -6, 0)
    for dx, dy, dz, lab, col in ((16, 0, 0, "X", INK), (0, 16, 0, "Y", INK),
                                 (0, 0, 14, "Z", INK)):
        e = P(-16 + dx, -6 + dy, dz)
        c.arrow(o[0], o[1], e[0], e[1], col, 0.7)
        c.text(e[0] + 2, e[1] + 1, lab, 5.5, col, weight="bold")

    # 尺寸引出
    p1 = P(0, 0, 0)
    p2 = P(PW, 0, 0)
    c.text((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 9, "95", 6.0, INK,
           "middle")
    p3 = P(PW, PH, 0)
    c.text((p2[0] + p3[0]) / 2 + 8, (p2[1] + p3[1]) / 2 + 5, "75", 6.0, INK,
           "middle")

    y0 = c.bbox()[3] + 12
    c.text(-130, y0, "图号 JM01-3D · 等轴测装配（CP-B300-JM-01）· 外形 "
                     "95×75×8.5 mm，水嘴另计", 6.0, GREY, cn=True)
    c.text(-130, y0 + 10, "顶面蓝框 = 两处 8×8 射流阵；绿框 = HBM 微通道区"
                          "（盖板无孔）", 6.0, GREY, cn=True)
    return c.autofit(8).render()


# ============================================================
# 爆炸图
# ============================================================
def fig_exploded():
    SC = 1.95
    c = Canvas((-140, -175, 300, 300), aria="Exploded assembly view")
    P = lambda x, y, z: iso(x, y, z, SC)
    GAP = 26.0

    layers = [
        ("JM01-320/310　进出水嘴 ×2", 3 * GAP + 12, None),
        ("JM01-200　喷嘴盖板 t2.5", 2 * GAP, "lid"),
        ("JM01-400　钎料框 t0.5", 1 * GAP, "frame"),
        ("JM01-100　换热底板 t3.5", 0.0, "base"),
    ]

    # 装配中心线（最先画，压在零件之下）
    top = P(PW / 2, PH / 2, layers[0][1] + 26)
    bot = P(PW / 2, PH / 2, -10)
    c.line(top[0], top[1], bot[0], bot[1], GREY, 0.5,
           'stroke-dasharray="6 3 1.5 3"')

    # 由下而上绘制（等轴测遮挡顺序：先远后近）
    # 盖板
    z = layers[1][1]
    iso_box(c, 0, 0, z, PW, PH, G["t_lid"], "#e8b97f", "#c98d57", "#b07b48",
            INK, 0.32, SC)
    for ax in (G["jet_a_x"], G["jet_a_x"] + G["die_w"] + G["hbi"]):
        for i in range(8):
            for j in range(8):
                sx, sy = P(ax + i * 3, G["jet_a_y"] + j * 3, z + G["t_lid"])
                c.circle(sx, sy, 0.62, "#2b6cb0", BLUE, 0.2)
        for xo in (0, 13.5, 27):
            a = P(ax - 1.5 + xo, G["jet_a_y"] - 1.5, z + G["t_lid"])
            b = P(ax - 1.5 + xo, G["jet_a_y"] + G["jet_span"] + 1.5,
                  z + G["t_lid"])
            c.line(a[0], a[1], b[0], b[1], ORANGE, 1.1)
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        pts = [P(hx, G["rib_y0"], z + G["t_lid"]),
               P(hx + G["hbm_w"], G["rib_y0"], z + G["t_lid"]),
               P(hx + G["hbm_w"], G["rib_y0"] + G["rib_len"], z + G["t_lid"]),
               P(hx, G["rib_y0"] + G["rib_len"], z + G["t_lid"])]
        c.poly(pts, "#c6f6d566", "#276749", 0.35)

    # 钎焊框
    z = layers[2][1]
    fr = 4.0
    iso_box(c, 0, 0, z, PW, fr, G["t_braze"], "#f6e05e", "#d9c236",
            "#c4ae2c", INK, 0.28, SC)
    iso_box(c, 0, PH - fr, z, PW, fr, G["t_braze"], "#f6e05e", "#d9c236",
            "#c4ae2c", INK, 0.28, SC)
    iso_box(c, 0, fr, z, fr, PH - 2 * fr, G["t_braze"], "#f6e05e", "#d9c236",
            "#c4ae2c", INK, 0.28, SC)
    iso_box(c, PW - fr, fr, z, fr, PH - 2 * fr, G["t_braze"], "#f6e05e",
            "#d9c236", "#c4ae2c", INK, 0.28, SC)

    # 底板
    z = layers[3][1]
    iso_box(c, 0, 0, z, PW, PH, G["t_base"], CU, CU_D, "#a5683c", INK,
            0.35, SC)
    for dx in (G["die_a_x"], G["die_a_x"] + G["die_w"] + G["hbi"]):
        for k in range(0, M.N_CH_DIE, 2):
            yy = G["die_a_y"] + k * G["ch_p"]
            a = P(dx, yy, z + G["t_base"])
            b = P(dx + G["die_w"], yy, z + G["t_base"])
            c.line(a[0], a[1], b[0], b[1], "#2c7a7b", 0.5)
    for hx in (G["hbm_x_l"], G["hbm_x_r"]):
        for i in range(7):
            xx = hx + 0.7 + i * 1.6
            a = P(xx, G["rib_y0"], z + G["t_base"])
            b = P(xx, G["rib_y0"] + G["rib_len"], z + G["t_base"])
            c.line(a[0], a[1], b[0], b[1], FIN, 0.5)
    for rx in (G["rib_x_l"], G["rib_x_r"]):
        iso_box(c, rx, G["rib_y0"], z + G["t_base"], G["rib"], G["rib_len"],
                0.9, "#1a365d", "#12294a", "#0d1f39", INK, 0.2, SC)

    # 水嘴（最高件，最后画以免被盖板遮挡）
    z = layers[0][1]
    for xx, col, tag in ((40, BLUE, "IN"), (50, ORANGE, "OUT")):
        iso_box(c, xx, PH - 9, z, 7, 7, 8, "#e2e8f0", "#cbd5e0", "#b6c2d2",
                INK, 0.3, SC)
        sx, sy = P(xx + 3.5, PH - 5.5, z + 8)
        c.circle(sx, sy, 1.8, "#fff", col, 0.5)
        c.text(sx, sy - 4.0, tag, 5.5, col, "middle", weight="bold")

    lx = c.bbox()[2] + 14
    for name, zz, _ in layers:
        a = P(PW, PH * 0.1, zz + 1.5)
        c.leader(a[0], a[1], lx, a[1] - 10, name, 6.0, INK, "start")

    # 件号说明（放右侧标签下方，避免压住图形）
    x0, y0 = -136, c.bbox()[3] + 14
    for i, s in enumerate([
        "图号 JM01-A6 · 爆炸装配图（三件 + 水嘴）· 总装厚度 8.5 mm"
        "（含周边钎缝 0.5）",
        "JM01-100 换热底板 t3.5：GPU 短槽 0.40×1.50 + HBM 宽槽 + 隔离肋；"
        "JM01-200 喷嘴盖板 t2.5：128×⌀0.50 + 回液缝 + 静压箱",
        "JM01-400 钎料框 t0.5：空心框，钎料不得流入 0.40 槽",
        "装配顺序：底板开槽 → 清洗 → 铺钎料框 → 盖板对位（±0.20）→ "
        "真空钎焊 → 接触面精铣 → 氦检",
        "爆炸间隙仅为显示，非实际间隙；焊后为一体件，喷嘴盖不可现场拆卸"
        "（方案 B 才可拆）",
    ]):
        c.text(x0, y0 + i * 11, s, 6.2, GREY, cn=True)
    return c.autofit(8).render()
