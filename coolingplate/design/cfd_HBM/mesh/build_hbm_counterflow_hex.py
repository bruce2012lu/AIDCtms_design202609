# -*- coding: utf-8 -*-
"""HBM 交错流共轭六面体。

列长方向相邻槽反向。偶数槽从高 Y 水平进入，低 Y 端封死，向上翻进汇流腔。
奇数槽从低 Y 水平进入，高 Y 端封死，向上翻进另一侧汇流腔。
汇流腔在上铜板内（z = 3–6 mm），顶面 z = 6 mm 为压力出口。
槽 0.80 x 2.00 mm，肋 0.80 mm，单侧 7 条。图上的长向温差就是这个列长。
"""
from __future__ import annotations

import sys
from pathlib import Path

import build_hbm_cht_hex as H

HERE = Path(__file__).resolve().parent

# 低 Y 汇流腔收偶数槽；高 Y 汇流腔收奇数槽。进口面在腔和加热段之间。
Y_LO0, Y_LO1 = -7.0, -4.0
Y_ODD_IN = -1.5
Y_EVEN_IN = 51.5
Y_HI0, Y_HI1 = 54.0, 57.0
Z_CH = 2.0
Z_RISER = 3.0
Z_GAL = 4.0
Z_TOP = 6.0


def build_z():
    z_tim0 = -(H.T_BASE + H.T_TIM)
    z_cu0 = -H.T_BASE
    tim = H.uniform(z_tim0, z_cu0, H.T_TIM / H.N_TIM)
    base = H.coords_of(z_cu0, 0.0, H.sizes_both(H.T_BASE, H.H1_S, H.GR_S, H.HMAX_S))
    groove = H.coords_of(0.0, Z_CH, H.sizes_both(H.CH_H, H.H1_F, H.GR_F, H.HMAX_F))
    riser = H.coords_of(Z_CH, Z_RISER, H.sizes_both(Z_RISER - Z_CH, H.H1_F, H.GR_F, 0.12))
    gallery = H.coords_of(Z_RISER, Z_GAL, H.sizes_both(Z_GAL - Z_RISER, H.H1_F, H.GR_F, 0.15))
    chimney = H.coords_of(Z_GAL, Z_TOP, H.sizes_one_side(Z_TOP - Z_GAL, H.H1_F, H.GR_F, 0.30))
    return H.cat([tim, base, groove, riser, gallery, chimney])


def coords_down(b, a, sizes):
    xs = [b]
    for h in sizes:
        xs.append(xs[-1] - h)
    xs[-1] = a
    return list(reversed(xs))


def _end(xs):
    return xs[-1] - xs[-2]


def _start(xs):
    return xs[1] - xs[0]


def build_y():
    col = [v for v in H.build_y() if -1e-6 <= v <= H.COL_L + 1e-6]
    h0 = col[1] - col[0]
    h50 = col[-1] - col[-2]
    near0 = coords_down(0.0, Y_ODD_IN, H.sizes_one_side(0.0 - Y_ODD_IN, h0, H.GR_Y, 0.55))
    mid_lo = coords_down(Y_ODD_IN, Y_LO1, H.sizes_one_side(Y_ODD_IN - Y_LO1, _start(near0), H.GR_Y, 0.55))
    far_lo = coords_down(Y_LO1, Y_LO0, H.sizes_one_side(Y_LO1 - Y_LO0, _start(mid_lo), H.GR_Y, 0.55))
    up_in = H.coords_of(H.COL_L, Y_EVEN_IN, H.sizes_one_side(Y_EVEN_IN - H.COL_L, h50, H.GR_Y, 0.55))
    up_mid = H.coords_of(Y_EVEN_IN, Y_HI0, H.sizes_one_side(Y_HI0 - Y_EVEN_IN, _end(up_in), H.GR_Y, 0.55))
    up_hi = H.coords_of(Y_HI0, Y_HI1, H.sizes_one_side(Y_HI1 - Y_HI0, _end(up_mid), H.GR_Y, 0.55))
    low = H.cat([far_lo, mid_lo, near0])
    high = H.cat([up_in, up_mid, up_hi])
    y = H.cat([low, col, high])
    for a, b in zip(y, y[1:]):
        if b <= a + 1e-9:
            raise RuntimeError("y 不单调: %s -> %s" % (a, b))
    return y


def channel_index(xc, fluid_x):
    for n, (a, b) in enumerate(fluid_x):
        if a - 1e-9 <= xc <= b + 1e-9:
            return n
    return None


def in_span(yc, a, b):
    return a - 1e-8 <= yc <= b + 1e-8


def kind_at(xc, yc, zc, fluid_x):
    if zc < -H.T_BASE - 1e-9:
        return "tim"
    ch = channel_index(xc, fluid_x)
    even = ch is not None and ch % 2 == 0
    odd = ch is not None and ch % 2 == 1
    lo = in_span(yc, Y_LO0, Y_LO1)
    hi = in_span(yc, Y_HI0, Y_HI1)
    if zc >= Z_RISER - 1e-9 and (lo or hi):
        return "fluid"
    if Z_CH - 1e-9 <= zc < Z_RISER - 1e-9:
        if lo and even:
            return "fluid"
        if hi and odd:
            return "fluid"
        return "cu"
    if -1e-9 <= zc < Z_CH - 1e-9:
        # 槽道伸进汇流腔正下方，才能和 z=2–3 mm 的竖孔共用一个面。
        if even and in_span(yc, Y_LO0, Y_EVEN_IN):
            return "fluid"
        if odd and in_span(yc, Y_ODD_IN, Y_HI1):
            return "fluid"
        return "cu"
    return "cu"


def build_kinds(x, y, z, fluid_x):
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    kinds = []
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        plane = []
        for j in range(ny):
            yc = 0.5 * (y[j] + y[j + 1])
            plane.append([kind_at(0.5 * (x[i] + x[i + 1]), yc, zc, fluid_x) for i in range(nx)])
        kinds.append(plane)
    return kinds


def number_cells(kinds, heat):
    nz = len(kinds)
    ny = len(kinds[0])
    nx = len(kinds[0][0])
    n_f = n_c = n_t = 0
    for j in range(ny):
        for k in range(nz):
            for i in range(nx):
                name = kinds[k][j][i]
                if name == "tim" and not heat[j]:
                    continue
                if name == "fluid":
                    n_f += 1
                elif name == "cu":
                    n_c += 1
                elif name == "tim":
                    n_t += 1
    ids = [[[0] * nx for _ in range(ny)] for _ in range(nz)]
    c_f = c_c = c_t = 0
    for j in range(ny):
        hot = heat[j]
        for k in range(nz):
            for i in range(nx):
                name = kinds[k][j][i]
                if name == "tim" and not hot:
                    continue
                if name == "fluid":
                    c_f += 1
                    ids[k][j][i] = c_f
                elif name == "cu":
                    c_c += 1
                    ids[k][j][i] = n_f + c_c
                elif name == "tim":
                    c_t += 1
                    ids[k][j][i] = n_f + n_c + c_t
    return ids, n_f, n_c, n_t


def make_bnd(x, y, z, fluid_x):
    def bnd(axis, i, j, k, material):
        if material != "fluid":
            return "wall_adiabat"
        xc = 0.5 * (x[i] + x[i + 1])
        ch = channel_index(xc, fluid_x)
        if axis == "y":
            zc = 0.5 * (z[k] + z[k + 1])
            yf = y[j]
            if ch is not None and ch % 2 == 0 and abs(yf - Y_EVEN_IN) < 1e-6 and -1e-9 <= zc < Z_CH:
                return "inlet_hi"
            if ch is not None and ch % 2 == 1 and abs(yf - Y_ODD_IN) < 1e-6 and -1e-9 <= zc < Z_CH:
                return "inlet_lo"
            return "wall_adiabat"
        if axis == "z" and abs(z[k] - Z_TOP) < 1e-6:
            yc = 0.5 * (y[j] + y[j + 1])
            if in_span(yc, Y_LO0, Y_LO1):
                return "outlet_lo"
            if in_span(yc, Y_HI0, Y_HI1):
                return "outlet_hi"
        return "wall_adiabat"
    return bnd


def _node_index(xs, value):
    for n, v in enumerate(xs):
        if abs(v - value) < 1e-6:
            return n
    raise RuntimeError("missing node %s" % value)


def audit(y, z, kinds):
    ny = len(y) - 1
    nx = len(kinds[0][0])
    k2 = _node_index(z, Z_CH)
    j_hi = _node_index(y, Y_EVEN_IN)
    j_lo = _node_index(y, Y_ODD_IN)
    link_lo = link_hi = inlet_hi = inlet_lo = 0
    for j in range(ny):
        yc = 0.5 * (y[j] + y[j + 1])
        lo = in_span(yc, Y_LO0, Y_LO1)
        hi = in_span(yc, Y_HI0, Y_HI1)
        if not lo and not hi:
            continue
        for i in range(nx):
            if kinds[k2 - 1][j][i] == "fluid" and kinds[k2][j][i] == "fluid":
                if lo:
                    link_lo += 1
                if hi:
                    link_hi += 1
    for k in range(len(z) - 1):
        zc = 0.5 * (z[k] + z[k + 1])
        if not (-1e-9 <= zc < Z_CH):
            continue
        for i in range(nx):
            if kinds[k][j_hi - 1][i] == "fluid" and kinds[k][j_hi][i] != "fluid":
                inlet_hi += 1
            if kinds[k][j_lo][i] == "fluid" and kinds[k][j_lo - 1][i] != "fluid":
                inlet_lo += 1
    print("link_lo %d link_hi %d inlet_hi %d inlet_lo %d" % (link_lo, link_hi, inlet_hi, inlet_lo))
    if link_lo == 0 or link_hi == 0 or inlet_hi == 0 or inlet_lo == 0:
        raise RuntimeError("counterflow topology is not connected")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    x, fluid_x, width = H.x_nodes_array()
    y = build_y()
    z = build_z()
    rx, _, _, _ = H.max_ratio(x)
    ry, _, _, _ = H.max_ratio(y)
    rz, _, _, _ = H.max_ratio(z)
    print("nx %d ny %d nz %d" % (len(x) - 1, len(y) - 1, len(z) - 1))
    print("ratio_x %.4f ratio_y %.4f ratio_z %.4f" % (rx, ry, rz))
    print("y %.4f .. %.4f   z %.4f .. %.4f" % (y[0], y[-1], z[0], z[-1]))
    heat = H.heated_flags(y)
    print("classifying ...", flush=True)
    kinds = build_kinds(x, y, z, fluid_x)
    audit(y, z, kinds)
    print("numbering ...", flush=True)
    ids, n_f, n_c, n_t = number_cells(kinds, heat)
    print("cells_fluid %d" % n_f)
    print("cells_cu %d" % n_c)
    print("cells_tim %d" % n_t)
    print("cells_total %d" % (n_f + n_c + n_t))
    mdot = H.RHO * 0.20 / 60000.0
    n_even = sum(1 for n in range(H.N_CH) if n % 2 == 0)
    n_odd = H.N_CH - n_even
    print("mdot_hi_kg_s %.8e" % (mdot * n_even / H.N_CH))
    print("mdot_lo_kg_s %.8e" % (mdot * n_odd / H.N_CH))
    print("n_even %d n_odd %d" % (n_even, n_odd))
    if mode == "count":
        return
    msh = HERE / "hbm_cf_w08h20.msh"
    print("writing %s ..." % msh, flush=True)
    n_nodes, n_faces, zones = H.write_msh(
        msh, x, y, z, kinds, heat, ids, n_f, n_c, n_t,
        "HBM counterflow hex; 0.80x2.00; 7 ch; Z headers",
        "wall_side",
        bnd=make_bnd(x, y, z, fluid_x),
    )
    print("WROTE %s cells=%d nodes=%d faces=%d" % (msh, n_f + n_c + n_t, n_nodes, n_faces))
    for key, val in zones.items():
        print("zone %s %d" % (key, val))


if __name__ == "__main__":
    main()
