# -*- coding: utf-8 -*-
"""HBM scheme C conjugate hex.

11 channels, 0.45 mm wide, 0.50 mm fins, 0.525 mm banks, 2.00 mm high.
From the low-X side: channels 1,3,9,11 run high Y to low Y; 2,4,8,10 run
low Y to high Y; 5,6,7 enter at the Y=24 mm face of the center gap and
leave through both end headers.
"""
from __future__ import annotations

import sys
from pathlib import Path

import build_hbm_cht_hex as H
import build_hbm_counterflow_hex as CF

HERE = Path(__file__).resolve().parent

CH_W = 0.45
FIN_W = 0.50
N_CH = 11
LAND = 0.525
# 1-based channel numbers
HI_TO_LO = {1, 3, 9, 11}
LO_TO_HI = {2, 4, 8, 10}
CENTER = {5, 6, 7}
Y_MID0, Y_MID1 = 24.0, 26.0


def x_nodes():
    pieces = []
    fluid_x = []
    x0 = 0.0
    land_s = H.sizes_both(LAND, H.H1_F, H.GR_F, H.HMAX_F)
    ch_s = H.sizes_both(CH_W, H.H1_F, H.GR_F, H.HMAX_F)
    fin_s = H.sizes_both(FIN_W, H.H1_F, H.GR_F, H.HMAX_F)
    pieces.append(H.coords_of(x0, x0 + LAND, land_s))
    x0 += LAND
    for i in range(N_CH):
        pieces.append(H.coords_of(x0, x0 + CH_W, ch_s))
        fluid_x.append((x0, x0 + CH_W))
        x0 += CH_W
        if i < N_CH - 1:
            pieces.append(H.coords_of(x0, x0 + FIN_W, fin_s))
            x0 += FIN_W
    pieces.append(H.coords_of(x0, x0 + LAND, list(reversed(land_s))))
    x0 += LAND
    if abs(x0 - 11.0) > 1e-6:
        raise RuntimeError("width %s != 11" % x0)
    return H.cat(pieces), fluid_x


def group_of(ch):
    n = None if ch is None else ch + 1
    if n in HI_TO_LO:
        return "hi_to_lo"
    if n in LO_TO_HI:
        return "lo_to_hi"
    if n in CENTER:
        return "center"
    return None


def in_center_x(xc, x0, x1):
    return x0 - 1e-9 <= xc <= x1 + 1e-9


def kind_at(xc, yc, zc, fluid_x, x0, x1):
    if zc < -H.T_BASE - 1e-9:
        return "tim"
    ch = CF.channel_index(xc, fluid_x)
    group = group_of(ch)
    lo = CF.in_span(yc, CF.Y_LO0, CF.Y_LO1)
    hi = CF.in_span(yc, CF.Y_HI0, CF.Y_HI1)
    mid = CF.in_span(yc, Y_MID0, Y_MID1)
    if zc >= CF.Z_RISER - 1e-9 and (lo or hi or (mid and in_center_x(xc, x0, x1))):
        return "fluid"
    if CF.Z_CH - 1e-9 <= zc < CF.Z_RISER - 1e-9:
        if lo and group in ("hi_to_lo", "center"):
            return "fluid"
        if hi and group in ("lo_to_hi", "center"):
            return "fluid"
        if mid and group == "center":
            return "fluid"
        return "cu"
    if -1e-9 <= zc < CF.Z_CH - 1e-9:
        if group == "hi_to_lo" and CF.in_span(yc, CF.Y_LO0, CF.Y_EVEN_IN):
            return "fluid"
        if group == "lo_to_hi" and CF.in_span(yc, CF.Y_ODD_IN, CF.Y_HI1):
            return "fluid"
        if group == "center" and CF.in_span(yc, CF.Y_LO0, CF.Y_HI1):
            return "fluid"
        return "cu"
    return "cu"


def build_kinds(x, y, z, fluid_x, x0, x1):
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    kinds = []
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        plane = []
        for j in range(ny):
            yc = 0.5 * (y[j] + y[j + 1])
            plane.append([
                kind_at(0.5 * (x[i] + x[i + 1]), yc, zc, fluid_x, x0, x1)
                for i in range(nx)
            ])
        kinds.append(plane)
    return kinds


def make_bnd(x, y, z, fluid_x, x0, x1):
    def bnd(axis, i, j, k, material):
        if material != "fluid":
            return "wall_adiabat"
        xc = 0.5 * (x[i] + x[i + 1])
        ch = CF.channel_index(xc, fluid_x)
        group = group_of(ch)
        if axis == "y":
            zc = 0.5 * (z[k] + z[k + 1])
            yf = y[j]
            if group == "hi_to_lo" and abs(yf - CF.Y_EVEN_IN) < 1e-6 and -1e-9 <= zc < CF.Z_CH:
                return "inlet_hi"
            if group == "lo_to_hi" and abs(yf - CF.Y_ODD_IN) < 1e-6 and -1e-9 <= zc < CF.Z_CH:
                return "inlet_lo"
            if abs(yf - Y_MID0) < 1e-6 and CF.Z_CH - 1e-9 <= zc < CF.Z_TOP and in_center_x(xc, x0, x1):
                return "inlet_mid"
            return "wall_adiabat"
        if axis == "z" and abs(z[k] - CF.Z_TOP) < 1e-6:
            yc = 0.5 * (y[j] + y[j + 1])
            if CF.in_span(yc, CF.Y_LO0, CF.Y_LO1):
                return "outlet_lo"
            if CF.in_span(yc, CF.Y_HI0, CF.Y_HI1):
                return "outlet_hi"
        return "wall_adiabat"
    return bnd


def audit(y, z, x, kinds, fluid_x, x0, x1):
    ny = len(y) - 1
    nx = len(kinds[0][0])
    k2 = CF._node_index(z, CF.Z_CH)
    j_hi = CF._node_index(y, CF.Y_EVEN_IN)
    j_lo = CF._node_index(y, CF.Y_ODD_IN)
    j_mid = CF._node_index(y, Y_MID0)
    link_lo = link_hi = link_mid = 0
    inlet_hi = inlet_lo = inlet_mid = 0
    for j in range(ny):
        yc = 0.5 * (y[j] + y[j + 1])
        lo = CF.in_span(yc, CF.Y_LO0, CF.Y_LO1)
        hi = CF.in_span(yc, CF.Y_HI0, CF.Y_HI1)
        mid = CF.in_span(yc, Y_MID0, Y_MID1)
        if not lo and not hi and not mid:
            continue
        for i in range(nx):
            if kinds[k2 - 1][j][i] == "fluid" and kinds[k2][j][i] == "fluid":
                if lo:
                    link_lo += 1
                if hi:
                    link_hi += 1
                if mid:
                    link_mid += 1
    for k in range(len(z) - 1):
        zc = 0.5 * (z[k] + z[k + 1])
        for i in range(nx):
            xc = 0.5 * (x[i] + x[i + 1])
            if -1e-9 <= zc < CF.Z_CH:
                if kinds[k][j_hi - 1][i] == "fluid" and kinds[k][j_hi][i] != "fluid":
                    inlet_hi += 1
                if kinds[k][j_lo][i] == "fluid" and kinds[k][j_lo - 1][i] != "fluid":
                    inlet_lo += 1
            if CF.Z_CH - 1e-9 <= zc < CF.Z_TOP and in_center_x(xc, x0, x1):
                if kinds[k][j_mid][i] == "fluid" and kinds[k][j_mid - 1][i] != "fluid":
                    inlet_mid += 1
    print("link_lo %d link_hi %d link_mid %d" % (link_lo, link_hi, link_mid))
    print("inlet_hi %d inlet_lo %d inlet_mid %d" % (inlet_hi, inlet_lo, inlet_mid))
    if min(link_lo, link_hi, link_mid, inlet_hi, inlet_lo, inlet_mid) == 0:
        raise RuntimeError("scheme C topology is not connected")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    x, fluid_x = x_nodes()
    x0 = fluid_x[4][0]
    x1 = fluid_x[6][1]
    y = CF.build_y()
    z = CF.build_z()
    rx, _, _, _ = H.max_ratio(x)
    ry, _, _, _ = H.max_ratio(y)
    rz, _, _, _ = H.max_ratio(z)
    print("nx %d ny %d nz %d" % (len(x) - 1, len(y) - 1, len(z) - 1))
    print("ratio_x %.4f ratio_y %.4f ratio_z %.4f" % (rx, ry, rz))
    print("x_mid %.4f .. %.4f" % (x0, x1))
    print("y %.4f .. %.4f   z %.4f .. %.4f" % (y[0], y[-1], z[0], z[-1]))
    width = 2 * LAND + N_CH * CH_W + (N_CH - 1) * FIN_W
    print("width_mm %.6f" % width)
    heat = H.heated_flags(y)
    print("classifying ...", flush=True)
    kinds = build_kinds(x, y, z, fluid_x, x0, x1)
    audit(y, z, x, kinds, fluid_x, x0, x1)
    print("numbering ...", flush=True)
    ids, n_f, n_c, n_t = CF.number_cells(kinds, heat)
    print("cells_fluid %d" % n_f)
    print("cells_cu %d" % n_c)
    print("cells_tim %d" % n_t)
    print("cells_total %d" % (n_f + n_c + n_t))
    mdot = H.RHO * 0.20 / 60000.0
    print("mdot_hi_kg_s %.8e" % (mdot * 4 / N_CH))
    print("mdot_lo_kg_s %.8e" % (mdot * 4 / N_CH))
    print("mdot_mid_kg_s %.8e" % (mdot * 3 / N_CH))
    if mode == "count":
        return
    msh = HERE / "hbm_c_w045h20.msh"
    print("writing %s ..." % msh, flush=True)
    n_nodes, n_faces, zones = H.write_msh(
        msh, x, y, z, kinds, heat, ids, n_f, n_c, n_t,
        "HBM scheme C hex; 0.45x2.00; 11 ch; center inlet",
        "wall_side",
        bnd=make_bnd(x, y, z, fluid_x, x0, x1),
    )
    print("WROTE %s cells=%d nodes=%d faces=%d" % (msh, n_f + n_c + n_t, n_nodes, n_faces))
    for key, val in zones.items():
        print("zone %s %d" % (key, val))


if __name__ == "__main__":
    main()
