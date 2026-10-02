# -*- coding: utf-8 -*-
"""UC-01b CONJUGATE hex: fluid + solid_cu + solid_tim2 → Fluent .msh (m).

Frozen TIM2 (preferred method):
  t_TIM = 80 μm (typical TIM2 bond line, in 50–100 μm)
  A_2DIE = 27×28×2 = 1512 mm²
  k_eff = t / (R_TIM2 * A_2DIE) so 1D R_TIM2 is recovered.
  Default R_TIM2 = 0.006 °C/W → k_eff = 8.8183 W/mK
  Also report k_eff at R=0.004 and 0.008.
  k_eff lumps bond-line conduction + contact resistance; not a brand catalog k.

Equal-area square orifice s = D*sqrt(pi/4) = 0.3545 mm (circle D=0.40
remains the official geom). First fluid layer 3 μm on Cu–fluid walls.
Package lid solid is NOT built (would add little for R_conv).
"""
from __future__ import annotations

import math
import os
from collections import defaultdict

# ---- geometry (mm) then *1e-3 on write ----
SX, SY = 3.0, 2.4
D = 0.40
H_GAP, CH_H, T_LID, H_PLEN = 2.0, 1.50, 2.5, 2.0
SLIT_H = 0.40
BASE_CU = 2.0
T_TIM_MM = 0.080  # 80 μm frozen
S_ORIF = D * math.sqrt(math.pi / 4.0)
FIRST = 0.003  # mm = 3 μm

A_2DIE = 27.0 * 28.0 * 2.0 * 1e-6  # m2
T_TIM_M = T_TIM_MM * 1e-3
R_TIM2_LO, R_TIM2_MID, R_TIM2_HI = 0.004, 0.006, 0.008
K_EFF_LO = T_TIM_M / (R_TIM2_LO * A_2DIE)
K_EFF_MID = T_TIM_M / (R_TIM2_MID * A_2DIE)
K_EFF_HI = T_TIM_M / (R_TIM2_HI * A_2DIE)
K_CU = 390.0
Q_FLUX = 1100.0 * 0.39 / (27.0 * 28.0 * 1e-6)  # 567460.317... W/m2
P_CELL = Q_FLUX * (SX * SY * 1e-6)

X0, X1 = -SX / 2.0, SX / 2.0
Y0, Y1 = -SY / 2.0, SY / 2.0
XL, XR = X0 + SLIT_H, X1 - SLIT_H
SO2 = S_ORIF / 2.0

Z_TIM_BOT = -(BASE_CU + T_TIM_MM)  # -2.080
Z_CU_BOT = -BASE_CU                 # -2.000  TIM–Cu
Z_IMP = 0.0                         # Cu–fluid slot floor
Z_RIB = CH_H                        # 1.50
Z_LID = CH_H + H_GAP                # 3.50
Z_LIDTOP = CH_H + H_GAP + T_LID     # 6.00
Z_IN = CH_H + H_GAP + T_LID + H_PLEN  # 8.00

SLOT_YS = ((-1.00, -0.60), (-0.20, 0.20), (0.60, 1.00))

FLUID, CU, TIM = "fluid", "solid_cu", "solid_tim2"


def geo_seg(a, b, n, first=None, last=None):
    if n < 1:
        return [a, b]
    L = b - a
    if first is None and last is None:
        return [a + L * i / n for i in range(n + 1)]
    if first is not None and last is None:
        if first * n >= L * 0.98:
            return [a + L * i / n for i in range(n + 1)]
        r = _growth(L, n, first)
        xs = [a]
        h = first
        for _ in range(n):
            xs.append(xs[-1] + h)
            h *= r
        xs[-1] = b
        return xs
    if last is not None and first is None:
        xs = geo_seg(0.0, L, n, first=last)
        return [b - x for x in reversed(xs)]
    if n < 4:
        return [a + L * i / n for i in range(n + 1)]
    n1 = n // 2
    n2 = n - n1
    left = geo_seg(a, (a + b) / 2.0, n1, first=first)
    right = geo_seg((a + b) / 2.0, b, n2, last=last)
    return left[:-1] + right


def _growth(L, n, h1):
    lo, hi = 1.01, 2.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        s = h1 * (mid ** n - 1.0) / (mid - 1.0)
        if s < L:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def merge_axis(segments):
    xs = []
    for seg in segments:
        if not xs:
            xs = list(seg)
        else:
            xs.extend(seg[1:])
    out = [xs[0]]
    for x in xs[1:]:
        if x - out[-1] > 1e-12:
            out.append(x)
    return out


def build_axes():
    medium = os.environ.get("UC01B_MESH", "run")
    if medium == "fine":
        nx_slit, nx_core, nx_orif = 10, 22, 12
        ny_half, ny_slot, ny_rib = 6, 12, 10
        nz_slot, nz_gap, nz_orif, nz_pl = 24, 20, 12, 8
        nz_cu, nz_tim = 12, 5
    else:
        nx_slit, nx_core, nx_orif = 8, 16, 10
        ny_half, ny_slot, ny_rib = 4, 10, 8
        nz_slot, nz_gap, nz_orif, nz_pl = 20, 16, 10, 6
        nz_cu, nz_tim = 10, 4
    x = merge_axis([
        geo_seg(X0, XL, nx_slit),
        geo_seg(XL, -SO2, nx_core, last=min(0.02, (-SO2 - XL) / max(nx_core, 1))),
        geo_seg(-SO2, SO2, nx_orif),
        geo_seg(SO2, XR, nx_core, first=min(0.02, (XR - SO2) / max(nx_core, 1))),
        geo_seg(XR, X1, nx_slit),
    ])
    y = merge_axis([
        geo_seg(Y0, -1.00, ny_half),
        geo_seg(-1.00, -0.60, ny_slot, first=0.02, last=0.02),
        geo_seg(-0.60, -0.20, ny_rib),
        geo_seg(-0.20, -SO2, max(3, ny_slot // 3)),
        geo_seg(-SO2, SO2, nx_orif),
        geo_seg(SO2, 0.20, max(3, ny_slot // 3)),
        geo_seg(0.20, 0.60, ny_rib),
        geo_seg(0.60, 1.00, ny_slot, first=0.02, last=0.02),
        geo_seg(1.00, Y1, ny_half),
    ])
    z = merge_axis([
        geo_seg(Z_TIM_BOT, Z_CU_BOT, nz_tim),
        geo_seg(Z_CU_BOT, Z_IMP, nz_cu, first=0.04, last=FIRST),
        geo_seg(Z_IMP, Z_RIB, nz_slot, first=FIRST, last=FIRST),
        geo_seg(Z_RIB, Z_LID, nz_gap, first=FIRST, last=FIRST),
        geo_seg(Z_LID, Z_LIDTOP, nz_orif),
        geo_seg(Z_LIDTOP, Z_IN, nz_pl),
    ])
    return x, y, z, medium, (nz_cu, nz_tim)


def in_slot_y(yc):
    return any(a <= yc <= b for a, b in SLOT_YS)


def zone_of(xc, yc, zc):
    slit = xc < XL - 1e-12 or xc > XR + 1e-12
    in_orif = (abs(xc) <= SO2 + 1e-12) and (abs(yc) <= SO2 + 1e-12)
    if zc < Z_CU_BOT - 1e-12:
        return TIM
    if zc < Z_IMP - 1e-12:
        return CU
    if zc < Z_RIB - 1e-12:
        if slit or in_slot_y(yc):
            return FLUID
        return CU
    if zc < Z_LID - 1e-12:
        return FLUID
    if zc < Z_LIDTOP + 1e-12:
        return FLUID if (slit or in_orif) else None
    return FLUID if in_orif else None


def _iface_name(a, b):
    pair = {a, b}
    if pair == {FLUID, CU}:
        return "wall_cu_fluid"
    if pair == {CU, TIM}:
        return "wall_tim_cu"
    return "wall_other"


def _x_bound(xc, zc):
    if abs(xc - X0) < 1e-9 or abs(xc - X1) < 1e-9:
        return "SYM"
    if Z_LID - 1e-12 < zc < Z_LIDTOP + 1e-12 and abs(abs(xc) - SO2) < 1e-6:
        return "wall_orifice"
    return "wall_lid"


def _z_minus_bound(zc, xc, yc):
    if abs(zc - Z_TIM_BOT) < 1e-9:
        return "wall_heat"
    if abs(zc - Z_IMP) < 1e-9:
        return "wall_cu_fluid"
    if abs(zc - Z_CU_BOT) < 1e-9:
        return "wall_tim_cu"
    if abs(zc - Z_LID) < 1e-9:
        if abs(xc) <= SO2 + 1e-9 and abs(yc) <= SO2 + 1e-9:
            return "wall_orifice"
        return "wall_lid"
    if abs(zc - Z_RIB) < 1e-9:
        return "wall_cu_fluid"
    return "wall_lid"


def _z_plus_bound(zc, xc):
    if abs(zc - Z_IN) < 1e-9:
        return "inlet_jet"
    if abs(zc - Z_LIDTOP) < 1e-9:
        slit = xc < XL - 1e-12 or xc > XR + 1e-12
        if slit:
            return "return_slot"
        return "inlet_jet"
    if abs(zc - Z_LID) < 1e-9:
        return "wall_lid"
    return "wall_lid"


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "uc01b_cht.msh")
    x, y, z, medium, (nz_cu, nz_tim) = build_axes()
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1

    kind = {}
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                xc = 0.5 * (x[i] + x[i + 1])
                yc = 0.5 * (y[j] + y[j + 1])
                zc = 0.5 * (z[k] + z[k + 1])
                zn = zone_of(xc, yc, zc)
                if zn:
                    kind[(i, j, k)] = zn

    # cell ids: fluid, then cu, then tim (consecutive)
    cells = {}
    counts = {FLUID: 0, CU: 0, TIM: 0}
    cid = 0
    for name in (FLUID, CU, TIM):
        keys = sorted(ijk for ijk, zn in kind.items() if zn == name)
        for ijk in keys:
            cid += 1
            cells[ijk] = cid
            counts[name] += 1
    n_fluid, n_cu, n_tim = counts[FLUID], counts[CU], counts[TIM]
    n_cells = cid
    id_fluid = (1, n_fluid)
    id_cu = (n_fluid + 1, n_fluid + n_cu)
    id_tim = (n_fluid + n_cu + 1, n_cells)

    need = set()
    for i, j, k in kind:
        for di in (0, 1):
            for dj in (0, 1):
                for dk in (0, 1):
                    need.add((i + di, j + dj, k + dk))
    nodes = {}
    coords = []
    for key in sorted(need):
        nid = len(coords) + 1
        nodes[key] = nid
        ii, jj, kk = key
        coords.append((x[ii] * 1e-3, y[jj] * 1e-3, z[kk] * 1e-3))

    def nd(i, j, k):
        return nodes[(i, j, k)]

    def cell_at(i, j, k):
        return cells.get((i, j, k))

    def kind_at(i, j, k):
        return kind.get((i, j, k))

    interiors = defaultdict(list)
    bounds = defaultdict(list)

    def add_pair(nids, c0, c1, z0, z1):
        if z0 == z1:
            interiors["interior"].append((nids, c0, c1))
        else:
            bounds[_iface_name(z0, z1)].append((nids, c0, c1))

    # i-faces +x
    for i in range(nx + 1):
        for j in range(ny):
            for k in range(nz):
                L = cell_at(i - 1, j, k)
                R = cell_at(i, j, k)
                if L is None and R is None:
                    continue
                nids = (nd(i, j, k), nd(i, j + 1, k), nd(i, j + 1, k + 1), nd(i, j, k + 1))
                zc = 0.5 * (z[k] + z[min(k + 1, len(z) - 1)])
                if L and R:
                    add_pair(nids, L, R, kind_at(i - 1, j, k), kind_at(i, j, k))
                elif R:
                    zone = _x_bound(x[i], zc)
                    bounds[zone].append((nids, R, 0))
                else:
                    zone = _x_bound(x[i], zc)
                    bounds[zone].append((nids, L, 0))

    # j-faces +y
    for j in range(ny + 1):
        for i in range(nx):
            for k in range(nz):
                B = cell_at(i, j - 1, k)
                F = cell_at(i, j, k)
                if B is None and F is None:
                    continue
                nids = (nd(i, j, k), nd(i + 1, j, k), nd(i + 1, j, k + 1), nd(i, j, k + 1))
                yc = y[j]
                if B and F:
                    add_pair(nids, B, F, kind_at(i, j - 1, k), kind_at(i, j, k))
                else:
                    zone = "SYM" if (abs(yc - Y0) < 1e-9 or abs(yc - Y1) < 1e-9) else "wall_lid"
                    owner = F if F else B
                    bounds[zone].append((nids, owner, 0))

    # k-faces +z
    for k in range(nz + 1):
        for i in range(nx):
            for j in range(ny):
                Dwn = cell_at(i, j, k - 1)
                Up = cell_at(i, j, k)
                if Dwn is None and Up is None:
                    continue
                nids = (nd(i, j, k), nd(i + 1, j, k), nd(i + 1, j + 1, k), nd(i, j + 1, k))
                xc = 0.5 * (x[i] + x[i + 1])
                yc = 0.5 * (y[j] + y[j + 1])
                if Dwn and Up:
                    add_pair(nids, Dwn, Up, kind_at(i, j, k - 1), kind_at(i, j, k))
                elif Up:
                    zone = _z_minus_bound(z[k], xc, yc)
                    bounds[zone].append((nids, Up, 0))
                else:
                    zone = _z_plus_bound(z[k], xc)
                    bounds[zone].append((nids, Dwn, 0))

    bc_code = {
        "interior": 2,
        "inlet_jet": 10,
        "return_slot": 5,
        "wall_heat": 3,
        "wall_lid": 3,
        "wall_orifice": 3,
        "wall_cu_fluid": 3,
        "wall_tim_cu": 3,
        "wall_other": 3,
        "SYM": 7,
    }
    face_groups = [("interior", 2, interiors["interior"])]
    for zname in (
        "inlet_jet", "return_slot", "wall_heat", "wall_lid", "wall_orifice",
        "wall_cu_fluid", "wall_tim_cu", "wall_other", "SYM",
    ):
        fs = bounds.get(zname, [])
        if fs:
            face_groups.append((zname, bc_code[zname], fs))
    face_groups = [(n_, c, fs) for n_, c, fs in face_groups if fs]
    n_faces = sum(len(fs) for _, _, fs in face_groups)
    n_nodes = len(coords)

    zone_ids = {}
    fid = 5  # 2=fluid 3=cu 4=tim
    for name, _, _ in face_groups:
        zone_ids[name] = fid
        fid += 1

    lines = []
    w = lines.append
    w('(0 "UC-01b CHT hex fluid+Cu+TIM2; t_TIM=80um k_eff=8.818 W/mK; square orifice")')
    w("(2 3)")
    w(f"(10 (0 1 {n_nodes} 0 3))")
    w(f"(12 (0 1 {n_cells} 0 0))")
    w(f"(13 (0 1 {n_faces} 0 0))")
    w(f"(10 (1 1 {n_nodes} 1 3)")
    w("(")
    for xx, yy, zz in coords:
        w(f"{xx:.10e} {yy:.10e} {zz:.10e}")
    w(")")
    w(")")
    w(f"(12 (2 {id_fluid[0]} {id_fluid[1]} 1 4))")
    w(f"(12 (3 {id_cu[0]} {id_cu[1]} 1 4))")
    w(f"(12 (4 {id_tim[0]} {id_tim[1]} 1 4))")

    fstart = 1
    for name, bcc, fs in face_groups:
        fend = fstart + len(fs) - 1
        zid = zone_ids[name]
        w(f"(13 ({zid} {fstart} {fend} {bcc} 4)")
        w("(")
        for nids, c0, c1 in fs:
            w(f"{nids[0]} {nids[1]} {nids[2]} {nids[3]} {c0} {c1}")
        w(")")
        w(")")
        fstart = fend + 1

    w("(45 (2 fluid fluid)())")
    w("(45 (3 solid solid_cu)())")
    w("(45 (4 solid solid_tim2)())")
    kind_map = {
        2: "interior",
        3: "wall",
        5: "pressure-outlet",
        7: "symmetry",
        10: "mass-flow-inlet",
    }
    for name, bcc, fs in face_groups:
        zid = zone_ids[name]
        w(f"(45 ({zid} {kind_map[bcc]} {name})())")

    text = "\n".join(lines) + "\n"
    with open(out, "w", encoding="ascii", newline="\n") as f:
        f.write(text)

    # first TIM layer
    dz_tim = (z[1] - z[0]) if z[0] == Z_TIM_BOT else T_TIM_MM / 4.0
    # find first fluid layer above z=0
    dz_fluid = None
    for a, b in zip(z, z[1:]):
        if abs(a - Z_IMP) < 1e-12:
            dz_fluid = b - a
            break
    meta = os.path.join(here, "cht_mesh_info.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write(f"cells_total {n_cells}\n")
        f.write(f"cells_fluid {n_fluid}\n")
        f.write(f"cells_solid_cu {n_cu}\n")
        f.write(f"cells_solid_tim2 {n_tim}\n")
        f.write(f"nodes {n_nodes}\n")
        f.write(f"faces {n_faces}\n")
        f.write(f"nx ny nz {nx} {ny} {nz}\n")
        f.write(f"nz_cu {nz_cu}\n")
        f.write(f"nz_tim {nz_tim}\n")
        f.write(f"t_tim_um {T_TIM_MM * 1000:.1f}\n")
        f.write(f"k_eff_R004 {K_EFF_LO:.6f}\n")
        f.write(f"k_eff_R006 {K_EFF_MID:.6f}\n")
        f.write(f"k_eff_R008 {K_EFF_HI:.6f}\n")
        f.write(f"A_2DIE_m2 {A_2DIE:.6e}\n")
        f.write(f"q_flux_Wm2 {Q_FLUX:.6f}\n")
        f.write(f"P_cell_W {P_CELL:.6f}\n")
        f.write(f"first_fluid_z_mm {dz_fluid if dz_fluid else -1:.6f}\n")
        f.write(f"tim_layer_mm {dz_tim:.6f}\n")
        f.write(f"orifice_square_mm {S_ORIF:.5f}\n")
        f.write(f"circle_D_mm {D}\n")
        f.write(f"level {medium}\n")
        f.write(f"z_tim_bot_mm {Z_TIM_BOT:.6f}\n")
        f.write(f"z_cu_bot_mm {Z_CU_BOT:.6f}\n")
        f.write(f"msh {out}\n")
        f.write("note CHT hex; square orifice; package solid omitted\n")
        for name, _, fs in face_groups:
            f.write(f"zone {name} {len(fs)}\n")
    print(f"WROTE {out}")
    print(f"fluid={n_fluid} cu={n_cu} tim={n_tim} total={n_cells}")
    print(f"nodes={n_nodes} faces={n_faces}")
    print(f"t_TIM={T_TIM_MM*1000:.0f} um  k_eff(R=0.006)={K_EFF_MID:.4f} W/mK")
    print(f"k_eff(0.004)={K_EFF_LO:.4f}  k_eff(0.008)={K_EFF_HI:.4f}")
    print(f"q''={Q_FLUX:.2f} W/m2  P_cell={P_CELL:.4f} W")


if __name__ == "__main__":
    main()
