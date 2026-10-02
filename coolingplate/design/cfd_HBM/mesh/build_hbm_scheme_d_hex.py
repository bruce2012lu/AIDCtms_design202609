# -*- coding: utf-8 -*-
"""HBM scheme D conjugate hex: cross channels, slit inlets, one plenum.

Eleven channels, 0.45 x 2.00 mm, run along X. Each channel is fed by one
0.40 x 1.00 mm slit at x = 5-6 mm. A 4 mm plenum (z = 3-7) covers the
whole column and is fed at mid-column, y = 24-26 mm, z = 8 mm. Each die
has a 4 mm collector beyond x = 0 and beyond x = 11. The eleven channels
open into that collector. The pressure outlet is the outer face of the
collector, not the channel mouth.
"""
from __future__ import annotations

import sys
from pathlib import Path

import build_hbm_cht_hex as H
import build_hbm_counterflow_hex as CF
import build_hbm_scheme_c_hex as C

HERE = Path(__file__).resolve().parent

Z_CH = 2.0
Z_PLATE = 3.0
Z_PLEN = 7.0
Z_TOP = 8.0
DIES = ((0.0, 11.0), (13.0, 24.0), (26.0, 37.0), (39.0, 50.0))
GAPS = ((11.0, 13.0), (24.0, 26.0), (37.0, 39.0))
X_DIE = (0.0, 11.0)
COL_L = 4.0
SLIT_X = (5.0, 6.0)
SLIT_W = 0.40
INLET_Y = (24.0, 26.0)
RHO_PG = 1022.5
Q_LPM = 0.60
SHOULDER = (C.CH_W - SLIT_W) / 2.0
# Channel top/bottom were 0.008 mm and too fine for Re ~ 60.
# Slit side walls, slit top and plenum floor share this first cell.
H1_CH_Z = 0.030
H1_SLIT = 0.030
GR_BL = 1.20


def in_spans(v, spans):
    return any(CF.in_span(v, a, b) for a, b in spans)


def build_x():
    # Legs stay coarse in the core. The cell against each slit side wall
    # matches the slit boundary layer. The collector starts at the same
    # 0.20 mm cell as the channel end.
    col = H.sizes_one_side(COL_L, 0.20, 1.45, 1.00)
    col_lo = H.coords_of(X_DIE[0] - COL_L, X_DIE[0], list(reversed(col)))
    leg_lo = H.coords_of(X_DIE[0], SLIT_X[0], H.sizes_both(SLIT_X[0], 0.20, 1.40, 1.00, H1_SLIT))
    slit = H.coords_of(
        SLIT_X[0], SLIT_X[1],
        H.sizes_both(SLIT_X[1] - SLIT_X[0], H1_SLIT, GR_BL, 0.12),
    )
    leg_hi = H.coords_of(SLIT_X[1], X_DIE[1], H.sizes_both(X_DIE[1] - SLIT_X[1], H1_SLIT, 1.40, 1.00, 0.20))
    col_hi = H.coords_of(X_DIE[1], X_DIE[1] + COL_L, col)
    return H.cat([col_lo, leg_lo, slit, leg_hi, col_hi])


def build_y():
    """0.45 mm channels. The center 0.40 mm of each channel is the slit."""
    fluid_y = []
    slits = []
    parts = []
    h1, gr = H.H1_F, H.GR_F
    land_s = H.sizes_both(C.LAND, h1, gr, H.HMAX_F)
    fin_s = H.sizes_both(C.FIN_W, h1, gr, H.HMAX_F)
    for n, (die0, _die1) in enumerate(DIES):
        y0 = die0
        parts.append(H.coords_of(y0, y0 + C.LAND, land_s))
        y0 += C.LAND
        for i in range(C.N_CH):
            shoulder = H.sizes_one_side(SHOULDER, h1, gr, 0.012)
            h_in = shoulder[-1]
            mid = H.sizes_both(SLIT_W, h_in, gr, 0.10)
            left = H.coords_of(y0, y0 + SHOULDER, shoulder)
            centre = H.coords_of(y0 + SHOULDER, y0 + SHOULDER + SLIT_W, mid)
            right = H.coords_of(y0 + SHOULDER + SLIT_W, y0 + C.CH_W, list(reversed(shoulder)))
            parts.append(H.cat([left, centre, right]))
            fluid_y.append((y0, y0 + C.CH_W))
            slits.append((y0 + SHOULDER, y0 + SHOULDER + SLIT_W))
            y0 += C.CH_W
            if i < C.N_CH - 1:
                parts.append(H.coords_of(y0, y0 + C.FIN_W, fin_s))
                y0 += C.FIN_W
        parts.append(H.coords_of(y0, y0 + C.LAND, list(reversed(land_s))))
        if n < len(GAPS):
            g0, g1 = GAPS[n]
            parts.append(H.coords_of(g0, g1, H.sizes_both(g1 - g0, h1, 1.30, 0.70)))
    y = H.cat(parts)
    for u, v in zip(y, y[1:]):
        if v <= u + 1e-9:
            raise RuntimeError("y not monotonic: %s -> %s" % (u, v))
    if abs(y[0]) > 1e-6 or abs(y[-1] - 50.0) > 1e-6:
        raise RuntimeError("y span %s .. %s" % (y[0], y[-1]))
    return y, fluid_y, slits


def build_z():
    z_tim0 = -(H.T_BASE + H.T_TIM)
    z_cu0 = -H.T_BASE
    tim = H.uniform(z_tim0, z_cu0, H.T_TIM / H.N_TIM)
    # First cells at the TIM and the channel floor stay 0.016 mm.
    # The copper core is coarser so the collector trim fits under 9 million.
    base = H.coords_of(z_cu0, 0.0, H.sizes_both(H.T_BASE, H.H1_S, 2.5, 1.00))
    groove = H.coords_of(0.0, Z_CH, H.sizes_both(H.CH_H, H1_CH_Z, GR_BL, 0.20))
    plate = H.coords_of(Z_CH, Z_PLATE, H.sizes_both(Z_PLATE - Z_CH, H1_CH_Z, 1.8, 0.50))
    plen_s = H.sizes_one_side(Z_PLEN - Z_PLATE, H1_SLIT, 1.35, 0.90)
    plen = H.coords_of(Z_PLATE, Z_PLEN, plen_s)
    cover = H.coords_of(Z_PLEN, Z_TOP, H.sizes_one_side(Z_TOP - Z_PLEN, plen_s[-1], 1.30, 0.50))
    return H.cat([tim, base, groove, plate, plen, cover])


def in_die_x(xc):
    return X_DIE[0] - 1e-9 <= xc <= X_DIE[1] + 1e-9


def in_header(xc):
    lo = X_DIE[0] - COL_L - 1e-9 <= xc < X_DIE[0] - 1e-9
    hi = X_DIE[1] + 1e-9 < xc <= X_DIE[1] + COL_L + 1e-9
    return lo or hi


def in_slit(xc, yc, slits):
    if not (SLIT_X[0] - 1e-9 <= xc <= SLIT_X[1] + 1e-9):
        return False
    return in_spans(yc, slits)


def kind_at(xc, yc, zc, fluid_y, slits):
    on_die = in_die_x(xc)
    on_hdr = in_header(xc)
    if zc < -H.T_BASE - 1e-9:
        return "tim" if on_die else ""
    # Collector duct only. Copper beside the inlet, under the slot,
    # above it, and around the outlet face is not meshed.
    if on_hdr:
        if -1e-9 <= zc < Z_CH and in_spans(yc, DIES):
            return "fluid"
        return ""
    if not on_die:
        return ""
    if -1e-9 <= zc < Z_CH:
        if CF.channel_index(yc, fluid_y) is not None:
            return "fluid"
        return "cu"
    if Z_CH - 1e-9 <= zc < Z_PLATE:
        if in_slit(xc, yc, slits):
            return "fluid"
        return "cu"
    if Z_PLATE - 1e-9 <= zc < Z_PLEN:
        return "fluid"
    if Z_PLEN - 1e-9 <= zc < Z_TOP:
        if INLET_Y[0] - 1e-9 <= yc <= INLET_Y[1] + 1e-9:
            return "fluid"
        return "cu"
    return "cu"


def build_kinds(x, y, z, fluid_y, slits):
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    kinds = []
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        plane = []
        for j in range(ny):
            yc = 0.5 * (y[j] + y[j + 1])
            plane.append([
                kind_at(0.5 * (x[i] + x[i + 1]), yc, zc, fluid_y, slits)
                for i in range(nx)
            ])
        kinds.append(plane)
    return kinds


def make_bnd(x, y, z, fluid_y):
    def bnd(axis, i, j, k, material):
        if material != "fluid":
            return "wall_adiabat"
        if axis == "y":
            return "wall_adiabat"
        if axis == "x" and (i == 0 or i == len(x) - 1):
            yc = 0.5 * (y[j] + y[j + 1])
            zc = 0.5 * (z[k] + z[k + 1])
            if -1e-9 <= zc < Z_CH and in_spans(yc, DIES):
                return "outlet"
        if axis == "z" and abs(z[k] - Z_TOP) < 1e-6:
            yc = 0.5 * (y[j] + y[j + 1])
            if INLET_Y[0] - 1e-9 <= yc <= INLET_Y[1] + 1e-9:
                return "inlet"
        return "wall_adiabat"
    return bnd


def audit(x, y, z, kinds, fluid_y, slits):
    nx = len(x) - 1
    ny = len(y) - 1
    k_ch = CF._node_index(z, Z_CH)
    k_plate = CF._node_index(z, Z_PLATE)
    k_plen = CF._node_index(z, Z_PLEN)
    link_slit = link_plen = link_in = 0
    for j in range(ny):
        yc = 0.5 * (y[j] + y[j + 1])
        for i in range(nx):
            xc = 0.5 * (x[i] + x[i + 1])
            if in_slit(xc, yc, slits):
                if kinds[k_ch - 1][j][i] == "fluid" and kinds[k_ch][j][i] == "fluid":
                    link_slit += 1
                if kinds[k_plate - 1][j][i] == "fluid" and kinds[k_plate][j][i] == "fluid":
                    link_plen += 1
            if in_die_x(xc) and INLET_Y[0] - 1e-9 <= yc <= INLET_Y[1] + 1e-9:
                if kinds[k_plen - 1][j][i] == "fluid" and kinds[k_plen][j][i] == "fluid":
                    link_in += 1
    i_lo = x.index(0.0)
    i_hi = x.index(11.0)
    link_hdr = 0
    for j in range(ny):
        if CF.channel_index(0.5 * (y[j] + y[j + 1]), fluid_y) is None:
            continue
        for k in range(k_ch):
            if kinds[k][j][i_lo - 1] == "fluid" and kinds[k][j][i_lo] == "fluid":
                link_hdr += 1
            if kinds[k][j][i_hi - 1] == "fluid" and kinds[k][j][i_hi] == "fluid":
                link_hdr += 1
    print("link_slit %d link_plenum %d link_inlet %d link_header %d" % (
        link_slit, link_plen, link_in, link_hdr))
    outlet = 0
    for k in range(len(z) - 1):
        zc = 0.5 * (z[k] + z[k + 1])
        if not (-1e-9 <= zc < Z_CH):
            continue
        for j in range(ny):
            if not in_spans(0.5 * (y[j] + y[j + 1]), DIES):
                continue
            if kinds[k][j][0] == "fluid":
                outlet += 1
            if kinds[k][j][nx - 1] == "fluid":
                outlet += 1
    k_top = CF._node_index(z, Z_TOP)
    inlet = 0
    for j in range(ny):
        yc = 0.5 * (y[j] + y[j + 1])
        if not (INLET_Y[0] - 1e-9 <= yc <= INLET_Y[1] + 1e-9):
            continue
        for i in range(nx):
            if kinds[k_top - 1][j][i] == "fluid":
                inlet += 1
    print("inlet_faces %d outlet_faces %d" % (inlet, outlet))
    leak = 0
    for j in range(ny):
        yc = 0.5 * (y[j] + y[j + 1])
        if not in_spans(yc, GAPS):
            continue
        for k in range(len(z) - 1):
            zc = 0.5 * (z[k] + z[k + 1])
            if zc < 0.0 or zc >= Z_PLATE:
                continue
            for i in range(nx):
                if kinds[k][j][i] == "fluid":
                    leak += 1
    print("gap_below_plenum %d" % leak)
    hdr_above = 0
    for k in range(len(z) - 1):
        zc = 0.5 * (z[k] + z[k + 1])
        if zc < Z_CH:
            continue
        for j in range(ny):
            for i in range(nx):
                if in_header(0.5 * (x[i] + x[i + 1])) and kinds[k][j][i] == "fluid":
                    hdr_above += 1
    print("header_above_channel %d" % hdr_above)
    if min(link_slit, link_plen, link_in, link_hdr, inlet, outlet) == 0 or leak or hdr_above:
        raise RuntimeError("slit plenum header topology is not connected")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "count"
    x = build_x()
    y, fluid_y, slits = build_y()
    z = build_z()
    rx, _, _, _ = H.max_ratio(x)
    ry, _, _, _ = H.max_ratio(y)
    rz, _, _, _ = H.max_ratio(z)
    print("nx %d ny %d nz %d" % (len(x) - 1, len(y) - 1, len(z) - 1))
    print("ratio_x %.4f ratio_y %.4f ratio_z %.4f" % (rx, ry, rz))
    print("x %.4f .. %.4f   y %.4f .. %.4f   z %.4f .. %.4f" % (
        x[0], x[-1], y[0], y[-1], z[0], z[-1]))
    print("channels %d slits %d" % (len(fluid_y), len(slits)))
    print("classifying ...", flush=True)
    kinds = build_kinds(x, y, z, fluid_y, slits)
    audit(x, y, z, kinds, fluid_y, slits)
    print("numbering ...", flush=True)
    heat = H.heated_flags(y)
    ids, n_f, n_c, n_t = CF.number_cells(kinds, heat)
    print("cells_fluid %d" % n_f)
    print("cells_cu %d" % n_c)
    print("cells_tim %d" % n_t)
    print("cells_total %d" % (n_f + n_c + n_t))
    print("mdot_kg_s %.8e" % (RHO_PG * Q_LPM / 60000.0))
    if mode == "count":
        return
    if n_f + n_c + n_t >= 9000000:
        raise RuntimeError("mesh is not under 9 million cells")
    msh = HERE / "hbm_d_slit_lt9m.msh"
    print("writing %s ..." % msh, flush=True)
    n_nodes, n_faces, zones = H.write_msh(
        msh, x, y, z, kinds, heat, ids, n_f, n_c, n_t,
        "HBM scheme D; collectors without surrounding copper; under 9 million cells",
        "wall_side",
        bnd=make_bnd(x, y, z, fluid_y),
    )
    print("WROTE %s cells=%d nodes=%d faces=%d" % (msh, n_f + n_c + n_t, n_nodes, n_faces))
    for key, val in zones.items():
        print("zone %s %d" % (key, val))


if __name__ == "__main__":
    main()
