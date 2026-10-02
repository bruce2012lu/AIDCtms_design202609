# -*- coding: utf-8 -*-
"""UC-01b CHT hex with CIRCULAR jet D=0.40 mm (O-grid). Not a square hole.

Official orifice: circle r=0.20 mm. Nodes lie on the circle (ICEM-style
O-grid: inner H + 4 blocks to the circle + 4 blocks to a square frame).
TIM2 t=80 um, k_eff=8.818 W/mK (R=0.006 on A_2DIE). Copper k=390.
"""
from __future__ import annotations

import math
import os
from collections import defaultdict

SX, SY = 3.0, 2.4
D = 0.40
R = D / 2.0  # 0.20 mm  CIRCLE — not 0.3545 square, not D=0.50
H_GAP, CH_H, T_LID, H_PLEN = 2.0, 1.50, 2.5, 2.0
SLIT_H = 0.40
BASE_CU = 2.0
T_TIM_MM = 0.080
GROWTH_MAX = 1.2
# BL / size levels vs 116k Cartesian coupon (fluid-only).
# coarse ≈ coupon scale; medium = half characteristic (baseline);
# fine ≈ 1.5× medium in jet/BL (not 8× full-hex, too heavy).
LEVELS = {
    "coarse": dict(
        first=0.003, n_bl=10, n_side=8, n_ri=8, n_ro=4,
        nx_slit=6, nx_mid=10, nx_trans=6, ny_half=3, ny_slot=6, ny_rib=4,
        nz_tim=4, nz_cu=8, nz_orif=8, nz_pl=5, n_core_z=8,
        h_orif=0.012,
    ),
    "medium": dict(
        first=0.0025, n_bl=12, n_side=12, n_ri=10, n_ro=5,
        nx_slit=10, nx_mid=16, nx_trans=10, ny_half=5, ny_slot=10, ny_rib=6,
        nz_tim=4, nz_cu=10, nz_orif=10, nz_pl=6, n_core_z=10,
        h_orif=0.008,
    ),
    # fine: orifice BL + transition + ALL three slot walls (incl. center) + slits
    "fine": dict(
        first=0.0025, n_bl=10, n_side=24, n_ri=14, n_ro=12,
        nx_slit=14, nx_mid=14, nx_trans=16, ny_half=6, ny_slot=16, ny_rib=8,
        nz_tim=6, nz_cu=14, nz_orif=16, nz_pl=8, n_core_z=12,
        h_orif=0.003,
    ),
}

A_2DIE = 27.0 * 28.0 * 2.0 * 1e-6
T_TIM_M = T_TIM_MM * 1e-3
R_TIM2_LO, R_TIM2_MID, R_TIM2_HI = 0.004, 0.006, 0.008
K_EFF_LO = T_TIM_M / (R_TIM2_LO * A_2DIE)
K_EFF_MID = T_TIM_M / (R_TIM2_MID * A_2DIE)
K_EFF_HI = T_TIM_M / (R_TIM2_HI * A_2DIE)
Q_FLUX = 1100.0 * 0.39 / (27.0 * 28.0 * 1e-6)
P_CELL = Q_FLUX * (SX * SY * 1e-6)

X0, X1 = -SX / 2.0, SX / 2.0
Y0, Y1 = -SY / 2.0, SY / 2.0
XL, XR = X0 + SLIT_H, X1 - SLIT_H

C_CORE = 0.070   # inner H half-side mm
S_FR = 0.380     # O-grid outer square; >R so rings fit; <slot-pitch so Cartesian owns most of the slot
T_ANN = 0.85     # Cartesian transition out to ~0.85 mm (wall-jet / shear)

Z_TIM_BOT = -(BASE_CU + T_TIM_MM)
Z_CU_BOT = -BASE_CU
Z_IMP = 0.0
Z_RIB = CH_H
Z_LID = CH_H + H_GAP
Z_LIDTOP = CH_H + H_GAP + T_LID
Z_IN = CH_H + H_GAP + T_LID + H_PLEN
SLOT_YS = ((-1.00, -0.60), (-0.20, 0.20), (0.60, 1.00))
FLUID, CU, TIM = "fluid", "solid_cu", "solid_tim2"


def geo_seg(a, b, n, first=None, last=None):
    if n < 1:
        return [a, b]
    L = b - a
    if first is None and last is None:
        return [a + L * i / n for i in range(n + 1)]
    if first is not None and last is None:
        if first * n >= abs(L) * 0.98:
            return [a + L * i / n for i in range(n + 1)]
        r = _growth(abs(L), n, first)
        xs = [a]
        h = math.copysign(first, L)
        for _ in range(n):
            xs.append(xs[-1] + h)
            h *= r
        xs[-1] = b
        return xs
    if last is not None and first is None:
        xs = geo_seg(0.0, abs(L), n, first=last)
        return [b - math.copysign(x, L) for x in reversed(xs)]
    n1 = n // 2
    n2 = n - n1
    mid = 0.5 * (a + b)
    return geo_seg(a, mid, n1, first=first)[:-1] + geo_seg(mid, b, n2, last=last)


def _growth(L, n, h1):
    lo, hi = 1.01, GROWTH_MAX
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        s = h1 * (mid ** n - 1.0) / (mid - 1.0)
        if s < L:
            lo = mid
        else:
            hi = mid
    return min(GROWTH_MAX, 0.5 * (lo + hi))


def bl_both(a, b, h1, n_bl, n_core, r=GROWTH_MAX):
    """Two-sided BL: n_bl layers each wall (growth<=1.2) + core. Units = a,b."""
    L = b - a
    hs = [h1 * (r ** i) for i in range(n_bl)]
    s_bl = sum(hs)
    if 2.0 * s_bl >= 0.90 * L:
        n = max(2 * n_bl, n_core)
        return geo_seg(a, b, n, first=h1, last=h1)
    rem = L - 2.0 * s_bl
    h_core = min(0.08, max(hs[-1], rem / float(n_core)))
    n_c = max(n_core, int(math.ceil(rem / max(h_core, 1e-6))))
    hc = rem / n_c
    xs = [a]
    for h in hs:
        xs.append(xs[-1] + h)
    for _ in range(n_c):
        xs.append(xs[-1] + hc)
    for h in reversed(hs):
        xs.append(xs[-1] + h)
    xs[-1] = b
    return xs


def insert_val(xs, v, tol=1e-12):
    if any(abs(x - v) < tol for x in xs):
        return list(xs)
    out = list(xs)
    for i, x in enumerate(out):
        if x > v:
            out.insert(i, v)
            return out
    out.append(v)
    return out


def clip_coords(coords, a, b, tol=1e-12):
    out = [x for x in coords if a - tol <= x <= b + tol]
    if not out:
        return [a, b]
    if abs(out[0] - a) > tol:
        out = [a] + [x for x in out if x > a + tol]
    if abs(out[-1] - b) > tol:
        out = [x for x in out if x < b - tol] + [b]
    return out


def count_bl_layers(coords, wall, sign, r=GROWTH_MAX, n_max=24):
    """Layers walking away from wall. sign=+1 → increasing coord."""
    xs = sorted(set(round(x, 10) for x in coords))
    if sign > 0:
        near = [x for x in xs if x >= wall - 1e-12]
        near.sort()
    else:
        near = [x for x in xs if x <= wall + 1e-12]
        near.sort(reverse=True)
    if len(near) < 2:
        return 0, None
    d1 = abs(near[1] - near[0])
    n = 1
    prev = d1
    for a, b in zip(near[1:], near[2:]):
        d = abs(b - a)
        if d <= prev * r * 1.08 + 1e-12 and n < n_max:
            n += 1
            prev = d
        else:
            break
    return n, d1


def line_geo(a, b, n, first=None, last=None):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy) or 1.0
    ss = geo_seg(0.0, L, n, first=first, last=last)
    return [(a[0] + dx * s / L, a[1] + dy * s / L) for s in ss]


def active_level():
    name = os.environ.get("UC01B_MESH", "medium").strip().lower()
    if name not in LEVELS:
        name = "medium"
    return name, LEVELS[name]


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vscale(a, s):
    return (a[0] * s, a[1] * s)


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def line_pts(a, b, n):
    return [lerp(a, b, i / n) for i in range(n + 1)]


def arc_pts(r, t0, t1, n):
    return [(r * math.cos(t0 + (t1 - t0) * i / n),
             r * math.sin(t0 + (t1 - t0) * i / n)) for i in range(n + 1)]


def tfi(west, east, south, north):
    ni, nj = len(south) - 1, len(west) - 1
    grid = [[(0.0, 0.0)] * (nj + 1) for _ in range(ni + 1)]
    sw, se, nw, ne = west[0], east[0], west[-1], east[-1]
    for i in range(ni + 1):
        xi = i / ni
        for j in range(nj + 1):
            eta = j / nj
            p = vadd(vadd(vscale(west[j], 1 - xi), vscale(east[j], xi)),
                     vadd(vscale(south[i], 1 - eta), vscale(north[i], eta)))
            corner = vadd(
                vadd(vscale(sw, (1 - xi) * (1 - eta)), vscale(se, xi * (1 - eta))),
                vadd(vscale(nw, (1 - xi) * eta), vscale(ne, xi * eta)),
            )
            grid[i][j] = (p[0] - corner[0], p[1] - corner[1])
    return grid


class XY:
    def __init__(self):
        self.pts = {}  # (rx,ry) -> id 0-based
        self.xy = []
        self.quads = []  # (n0,n1,n2,n3) CCW

    def nid(self, p):
        k = (round(p[0], 10), round(p[1], 10))
        if k in self.pts:
            return self.pts[k]
        i = len(self.xy)
        self.pts[k] = i
        self.xy.append(p)
        return i

    def add_grid(self, grid):
        ni, nj = len(grid) - 1, len(grid[0]) - 1
        ids = [[self.nid(grid[i][j]) for j in range(nj + 1)] for i in range(ni + 1)]
        for i in range(ni):
            for j in range(nj):
                self.quads.append((ids[i][j], ids[i + 1][j], ids[i + 1][j + 1], ids[i][j + 1]))


def build_xy(lv=None):
    if lv is None:
        _, lv = active_level()
    g = XY()
    c, s = C_CORE, S_FR
    nri, nro = lv["n_ri"], lv["n_ro"]
    h_orif = lv["h_orif"]
    h1 = lv["first"]
    nbl = lv["n_bl"]
    nx_slit, nx_mid = lv["nx_slit"], lv["nx_mid"]
    nx_trans = lv.get("nx_trans", max(8, nx_mid // 2))
    ny_half = lv["ny_half"]
    n_core_slot = max(6, lv["ny_slot"] // 3)
    n_core_rib = max(4, lv["ny_rib"] // 2)
    n_core_slit = max(4, nx_slit // 3)

    def join(*parts):
        out = []
        for p in parts:
            if not out:
                out = list(p)
            else:
                out.extend(p[1:])
        return out

    def cart_block(xs, yv):
        grid = [[(xs[i], yv[j]) for j in range(len(yv))] for i in range(len(xs))]
        g.add_grid(grid)

    # Y: half-rib | side slot | rib | CENTER slot | rib | side slot | half-rib
    # Center slot walls y=±0.20 get the same two-sided BL as the side slots.
    ys = join(
        geo_seg(Y0, -1.00, ny_half, last=h1),
        bl_both(-1.00, -0.60, h1, nbl, n_core_slot),
        bl_both(-0.60, -0.20, h1, nbl, n_core_rib),
        bl_both(-0.20, 0.20, h1, nbl, n_core_slot),
        bl_both(0.20, 0.60, h1, nbl, n_core_rib),
        bl_both(0.60, 1.00, h1, nbl, n_core_slot),
        geo_seg(1.00, Y1, ny_half, first=h1),
    )
    ys = insert_val(ys, -s)
    ys = insert_val(ys, s)

    h_trans = min(0.020, max(0.008, h_orif * (GROWTH_MAX ** 6)))
    xs_slit_l = bl_both(X0, XL, h1, nbl, n_core_slit)
    xs_slit_r = bl_both(XR, X1, h1, nbl, n_core_slit)
    if XL < -T_ANN < -s:
        xs_mid_l = join(
            geo_seg(XL, -T_ANN, nx_mid, first=h1),
            geo_seg(-T_ANN, -s, nx_trans, last=h_trans),
        )
        xs_mid_r = join(
            geo_seg(s, T_ANN, nx_trans, first=h_trans),
            geo_seg(T_ANN, XR, nx_mid, last=h1),
        )
    else:
        xs_mid_l = geo_seg(XL, -s, nx_mid + nx_trans, first=h1, last=h_trans)
        xs_mid_r = geo_seg(s, XR, nx_mid + nx_trans, first=h_trans, last=h1)

    ys_og = clip_coords(ys, -s, s)
    n_e = max(8, len(ys_og) - 1)
    xs_og = geo_seg(-s, s, n_e)
    n_n = len(xs_og) - 1

    # O-grid core: n_n in X, n_e in Y (matches square sides → conformal)
    xs_c = [-c + 2.0 * c * i / n_n for i in range(n_n + 1)]
    ys_c = [-c + 2.0 * c * j / n_e for j in range(n_e + 1)]
    g.add_grid([[(xs_c[i], ys_c[j]) for j in range(n_e + 1)] for i in range(n_n + 1)])

    n_ring = max(10, min(nri, 12))
    hs, acc, h = [], 0.0, h_orif
    room_in = 0.80 * (R - c)
    for _ in range(n_ring):
        if acc + h > room_in:
            break
        hs.append(h)
        acc += h
        h = min(h * GROWTH_MAX, 0.04)
    if len(hs) < 10:
        hs = [h_orif * min(GROWTH_MAX, 1.08) ** i for i in range(10)]
        acc = sum(hs)
        hs = [x * min(1.0, room_in / acc) for x in hs]
        hs[0] = h_orif

    def rings_from_wall(sign):
        rs = [R]
        r = R
        for hh in hs:
            r = r + sign * hh
            if sign < 0 and r <= c * 1.05:
                break
            if sign > 0 and r >= s * 0.92:
                break
            rs.append(r)
        return rs

    rs_in = rings_from_wall(-1.0)
    rs_out = rings_from_wall(+1.0)

    # inner O-blocks: core → circle. n_e on E/W, n_n on N/S.
    inner_def = (
        ("e", -math.pi / 4, math.pi / 4, [(c, y) for y in ys_c], n_e),
        ("n", math.pi / 4, 3 * math.pi / 4, [(x, c) for x in reversed(xs_c)], n_n),
        ("w", 3 * math.pi / 4, 5 * math.pi / 4, [(-c, y) for y in reversed(ys_c)], n_e),
        ("s", 5 * math.pi / 4, 7 * math.pi / 4, [(x, -c) for x in xs_c], n_n),
    )
    for _nm, t0, t1, core_side, nq in inner_def:
        arcs = [arc_pts(rr, t0, t1, nq) for rr in rs_in]
        g.add_grid(list(reversed(arcs)))
        inner = core_side
        outer = arcs[-1]
        n_rest = max(4, nri - (len(rs_in) - 1))
        rad_w = line_geo(inner[0], outer[0], n_rest)
        rad_e = line_geo(inner[-1], outer[-1], n_rest)
        g.add_grid(tfi(rad_w, rad_e, inner, outer))

    # outer O-blocks: circle → square. Square E/W uses clustered ys (center-slot BL).
    outer_sq = (
        ("e", -math.pi / 4, math.pi / 4, [(s, y) for y in ys_og], n_e),
        ("n", math.pi / 4, 3 * math.pi / 4, [(x, s) for x in reversed(xs_og)], n_n),
        ("w", 3 * math.pi / 4, 5 * math.pi / 4, [(-s, y) for y in reversed(ys_og)], n_e),
        ("s", 5 * math.pi / 4, 7 * math.pi / 4, [(x, -s) for x in xs_og], n_n),
    )
    for _nm, t0, t1, sq_side, nq in outer_sq:
        arcs = [arc_pts(rr, t0, t1, nq) for rr in rs_out]
        g.add_grid(arcs)
        inner = arcs[-1]
        outer = sq_side
        n_rest = max(3, nro)
        rad_w = line_geo(inner[0], outer[0], n_rest)
        rad_e = line_geo(inner[-1], outer[-1], n_rest)
        g.add_grid(tfi(rad_w, rad_e, inner, outer))

    cart_block(xs_slit_l, ys)
    cart_block(xs_mid_l, ys)
    cart_block(xs_mid_r, ys)
    cart_block(xs_slit_r, ys)
    cart_block(xs_og, clip_coords(ys, Y0, -s))
    cart_block(xs_og, clip_coords(ys, s, Y1))

    g.ys = ys
    g.xs_og = xs_og
    g.n_e = n_e
    g.n_n = n_n
    return g


def z_axis(lv=None):
    if lv is None:
        _, lv = active_level()
    h1, nbl, nc = lv["first"], lv["n_bl"], lv["n_core_z"]
    # TIM: ≥4 layers, bias toward TIM–Cu (z=-2.00)
    # Cu base: ≥6 layers, bias TIM–Cu (first) and Cu–fluid (last=h1)
    # fins / gap: two-sided fluid BL
    # lid / orifice plate 2.5 mm: two-sided (underside + hole exit); ≥6 through thickness
    h_tim_cu = min(0.010, max(0.006, (Z_CU_BOT - Z_TIM_BOT) / max(lv["nz_tim"], 4)))
    return (
        geo_seg(Z_TIM_BOT, Z_CU_BOT, lv["nz_tim"], last=h_tim_cu)
        + geo_seg(Z_CU_BOT, Z_IMP, lv["nz_cu"], first=0.020, last=h1)[1:]
        + bl_both(Z_IMP, Z_RIB, h1, nbl, nc)[1:]
        + bl_both(Z_RIB, Z_LID, h1, nbl, nc)[1:]
        + bl_both(Z_LID, Z_LIDTOP, h1, max(6, nbl - 2), max(6, lv["nz_orif"] // 2))[1:]
        + geo_seg(Z_LIDTOP, Z_IN, lv["nz_pl"])[1:]
    )


def in_slot_y(yc):
    return any(a <= yc <= b for a, b in SLOT_YS)


def zone_of(xc, yc, zc):
    slit = xc < XL - 1e-12 or xc > XR + 1e-12
    in_circ = (xc * xc + yc * yc) <= (R * R + 1e-10)
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
        # hole + return slits = fluid; rest of lid = Cu orifice plate
        return FLUID if (slit or in_circ) else CU
    return FLUID if in_circ else None


def on_circle(x, y, tol=2e-4):
    return abs(math.hypot(x, y) - R) < tol


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    level, lv = active_level()
    out = os.path.join(here, f"uc01b_cht_{level}.msh")
    xy = build_xy(lv)
    z = z_axis(lv)
    nz = len(z) - 1
    dz0 = z[1] - z[0] if abs(z[0] - Z_TIM_BOT) < 1e-12 else None
    # first fluid layer above z=0
    dz_imp = None
    for a, b in zip(z, z[1:]):
        if abs(a - Z_IMP) < 1e-12:
            dz_imp = b - a
            break
    print(f"level={level} xy_nodes={len(xy.xy)} quads={len(xy.quads)} nz={nz} dz_imp={dz_imp}")

    # 3D cells
    kind = {}  # (q,k) -> zone
    for iq, (n0, n1, n2, n3) in enumerate(xy.quads):
        p0, p1, p2, p3 = xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3]
        xc = 0.25 * (p0[0] + p1[0] + p2[0] + p3[0])
        yc = 0.25 * (p0[1] + p1[1] + p2[1] + p3[1])
        for k in range(nz):
            zc = 0.5 * (z[k] + z[k + 1])
            zn = zone_of(xc, yc, zc)
            if zn:
                kind[(iq, k)] = zn

    cells = {}
    counts = {FLUID: 0, CU: 0, TIM: 0}
    cid = 0
    for name in (FLUID, CU, TIM):
        keys = sorted(qk for qk, zn in kind.items() if zn == name)
        for qk in keys:
            cid += 1
            cells[qk] = cid
            counts[name] += 1
    n_fluid, n_cu, n_tim = counts[FLUID], counts[CU], counts[TIM]
    n_cells = cid

    # 3D nodes: only corners of used cells
    need = set()
    for (iq, k) in kind:
        n0, n1, n2, n3 = xy.quads[iq]
        for qn in (n0, n1, n2, n3):
            need.add((qn, k))
            need.add((qn, k + 1))
    nodes = {}
    coords = []
    for key in sorted(need):
        nid = len(coords) + 1
        nodes[key] = nid
        qn, kk = key
        xx, yy = xy.xy[qn]
        coords.append((xx * 1e-3, yy * 1e-3, z[kk] * 1e-3))

    def nd(qn, kk):
        return nodes[(qn, kk)]

    interiors = []
    bounds = defaultdict(list)

    # face map: (sorted_nids) -> (c0, z0) first visit; second visit pairs
    seen = {}

    def push_face(nids, cid_, zn, bname):
        key = tuple(sorted(nids))
        if key in seen:
            c0, z0, nids0 = seen.pop(key)
            if z0 == zn:
                interiors.append((nids0, c0, cid_))
            else:
                pair = {z0, zn}
                nm = "wall_cu_fluid" if pair == {FLUID, CU} else (
                    "wall_tim_cu" if pair == {CU, TIM} else "wall_other")
                bounds[nm].append((nids0, c0, cid_))
        else:
            seen[key] = (cid_, zn, nids)

    for (iq, k), zn in kind.items():
        cid_ = cells[(iq, k)]
        a, b, c, d = xy.quads[iq]
        # bottom k, top k+1, and 4 sides
        bot = (nd(a, k), nd(b, k), nd(c, k), nd(d, k))
        top = (nd(a, k + 1), nd(b, k + 1), nd(c, k + 1), nd(d, k + 1))
        push_face(bot, cid_, zn, None)
        push_face(top, cid_, zn, None)
        # sides: a-b, b-c, c-d, d-a
        for q1, q2 in ((a, b), (b, c), (c, d), (d, a)):
            nids = (nd(q1, k), nd(q2, k), nd(q2, k + 1), nd(q1, k + 1))
            push_face(nids, cid_, zn, None)

    # leftover = boundary
    for key, (cid_, zn, nids) in seen.items():
        xs = [coords[i - 1][0] * 1e3 for i in nids]
        ys = [coords[i - 1][1] * 1e3 for i in nids]
        zs = [coords[i - 1][2] * 1e3 for i in nids]
        xc, yc, zc = sum(xs) / 4, sum(ys) / 4, sum(zs) / 4
        name = _bound_name(xc, yc, zc, xs, ys, zs)
        bounds[name].append((nids, cid_, 0))

    def _orient_toward_c0(nids, cid_):
        """Right-hand normal points toward c0 (Fluent 26.1 / fluent6.msh)."""
        p0, p1, p2 = (coords[nids[0] - 1], coords[nids[1] - 1], coords[nids[2] - 1])
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx, ny, nz_ = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        if nx * nx + ny * ny + nz_ * nz_ < 1e-30:
            p3 = coords[nids[3] - 1]
            vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
            nx, ny, nz_ = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
        fc = tuple(sum(coords[i - 1][a] for i in nids) / 4.0 for a in range(3))
        gx, gy, gz = centroids[cid_]
        if nx * (gx - fc[0]) + ny * (gy - fc[1]) + nz_ * (gz - fc[2]) < 0.0:
            return (nids[0], nids[3], nids[2], nids[1])
        return nids

    centroids = {}
    for (iq, k), cid_ in cells.items():
        qa, qb, qc, qd = xy.quads[iq]
        ids8 = [nd(q, kk) for kk in (k, k + 1) for q in (qa, qb, qc, qd)]
        centroids[cid_] = tuple(sum(coords[i - 1][a] for i in ids8) / 8.0 for a in range(3))
    interiors = [(_orient_toward_c0(nids, c0), c0, c1) for nids, c0, c1 in interiors]
    for _nm in list(bounds):
        bounds[_nm] = [(_orient_toward_c0(nids, c0), c0, c1) for nids, c0, c1 in bounds[_nm]]

    bc_code = {
        "interior": 2, "inlet_jet": 10, "return_slot": 5,
        "wall_heat": 3, "wall_lid": 3, "wall_orifice": 3,
        "wall_cu_fluid": 3, "wall_tim_cu": 3, "wall_other": 3, "SYM": 7,
    }
    face_groups = [("interior", 2, interiors)]
    for zname in (
        "inlet_jet", "return_slot", "wall_heat", "wall_lid", "wall_orifice",
        "wall_cu_fluid", "wall_tim_cu", "wall_other", "SYM",
    ):
        fs = bounds.get(zname, [])
        if fs:
            face_groups.append((zname, bc_code[zname], fs))
    n_faces = sum(len(fs) for _, _, fs in face_groups)
    n_nodes = len(coords)
    id_fluid = (1, n_fluid)
    id_cu = (n_fluid + 1, n_fluid + n_cu)
    id_tim = (n_fluid + n_cu + 1, n_cells)

    zone_ids = {}
    fid = 5
    for name, _, _ in face_groups:
        zone_ids[name] = fid
        fid += 1

    # Fluent ASCII indices are hexadecimal (see mesh/uc01b_fluent6.msh).
    # Decimal headers are read as hex, so 4547658 becomes 0x4547658 and the
    # reader walks off the node block ("Unable to read coordinates of node N").
    def _hx(n):
        return format(int(n), "x")

    with open(out, "w", encoding="ascii", newline="\n") as f:
        w = f.write
        w(f'(0 "UC-01b CHT CIRCLE D=0.40 O-grid level={level}; TIM 80um k_eff=8.818")\n')
        w("(2 3)\n")
        w(f"(10 (0 1 {_hx(n_nodes)} 0 3))\n")
        w(f"(12 (0 1 {_hx(n_cells)} 0 0))\n")
        w(f"(13 (0 1 {_hx(n_faces)} 0 0))\n")
        w(f"(10 (1 1 {_hx(n_nodes)} 1 3)\n(\n")
        for xx, yy, zz in coords:
            w(f"{xx:.10e} {yy:.10e} {zz:.10e}\n")
        w(")\n)\n")
        w(f"(12 (2 {_hx(id_fluid[0])} {_hx(id_fluid[1])} 1 4))\n")
        w(f"(12 (3 {_hx(id_cu[0])} {_hx(id_cu[1])} 1 4))\n")
        w(f"(12 (4 {_hx(id_tim[0])} {_hx(id_tim[1])} 1 4))\n")
        fstart = 1
        for name, bcc, fs in face_groups:
            fend = fstart + len(fs) - 1
            zid = zone_ids[name]
            w(f"(13 ({_hx(zid)} {_hx(fstart)} {_hx(fend)} {_hx(bcc)} 4)\n(\n")
            for nids, c0, c1 in fs:
                w(
                    f"{_hx(nids[0])} {_hx(nids[1])} {_hx(nids[2])} {_hx(nids[3])} "
                    f"{_hx(c0)} {_hx(c1)}\n"
                )
            w(")\n)\n")
            fstart = fend + 1
        w("(39 (2 fluid fluid)())\n")
        w("(39 (3 solid solid_cu)())\n")
        w("(39 (4 solid solid_tim2)())\n")
        kind_map = {2: "interior", 3: "wall", 5: "pressure-outlet", 7: "symmetry", 10: "mass-flow-inlet"}
        for name, bcc, _fs in face_groups:
            w(f"(39 ({zone_ids[name]} {kind_map[bcc]} {name})())\n")

    # circle QA: nodes intended on circle
    rc = [math.hypot(p[0], p[1]) for p in xy.xy]
    on_r = [abs(r - R) for r in rc if abs(r - R) < 2e-4]
    # y+ estimate (theory, not CFD): Re_D~1008, V=1.66 m/s, nu=6.58e-7
    v_jet, nu = 1.66, 6.53e-4 / 992.2
    u_tau_lam = v_jet * math.sqrt(0.664 / math.sqrt(1008) / 2.0)
    yplus = (u_tau_lam * (lv["first"] * 1e-3)) / nu
    meta = os.path.join(here, f"cht_mesh_info_{level}.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write("orifice CIRCLE D=0.40 mm (O-grid). NOT square 0.3545, NOT D=0.50\n")
        f.write(f"level {level}\n")
        f.write(f"cells_total {n_cells}\n")
        f.write(f"cells_fluid {n_fluid}\n")
        f.write(f"cells_solid_cu {n_cu}\n")
        f.write(f"cells_solid_tim2 {n_tim}\n")
        f.write(f"nodes {n_nodes}\n")
        f.write(f"faces {n_faces}\n")
        f.write(f"xy_nodes {len(xy.xy)}\n")
        f.write(f"xy_quads {len(xy.quads)}\n")
        f.write(f"nz {nz}\n")
        f.write(f"first_imp_mm {dz_imp}\n")
        f.write(f"h_orif_mm {lv['h_orif']}\n")
        f.write(f"n_bl {lv['n_bl']}\n")
        f.write(f"growth_max {GROWTH_MAX}\n")
        f.write(f"n_ri {lv['n_ri']}\n")
        f.write(f"n_side {lv['n_side']}\n")
        f.write(f"nz_tim {lv['nz_tim']}\n")
        f.write(f"nz_cu {lv['nz_cu']}\n")
        n_core_x = getattr(xy, "n_n", lv["n_side"])
        f.write(f"jet_core_dx_mm {2.0 * C_CORE / float(n_core_x)}\n")
        f.write(f"slot_dy_mm {0.40 / lv['ny_slot']}\n")
        f.write(f"delta_orif_est_mm {lv['h_orif'] * (GROWTH_MAX ** lv['n_ri'] - 1.0) / (GROWTH_MAX - 1.0)}\n")
        f.write(f"slot_slit_first_mm {lv['first']}\n")
        f.write(f"slot_slit_n_bl {lv['n_bl']}\n")
        f.write("slot_slit_bl  two-sided on ALL three 0.40 mm slots and return slits\n")
        ys_m = getattr(xy, "ys", None)
        if ys_m:
            for wall, sign, tag in (
                (-0.20, +1, "center_slot_ym20"),
                (0.20, -1, "center_slot_yp20"),
                (-1.00, +1, "south_slot_ym100"),
                (1.00, -1, "north_slot_yp100"),
            ):
                nlay, d1 = count_bl_layers(ys_m, wall, sign)
                f.write(f"{tag}_first_mm {d1}\n")
                f.write(f"{tag}_n_bl {nlay}\n")
            n_imp, d_imp = count_bl_layers(z, Z_IMP, +1)
            n_ceil, d_ceil = count_bl_layers(z, Z_RIB, -1)
            f.write(f"center_slot_floor_first_mm {d_imp}\n")
            f.write(f"center_slot_floor_n_bl {n_imp}\n")
            f.write(f"center_slot_ceil_first_mm {d_ceil}\n")
            f.write(f"center_slot_ceil_n_bl {n_ceil}\n")
        f.write(f"S_FR_mm {S_FR}\n")
        f.write(f"T_ANN_mm {T_ANN}\n")
        f.write("lid_solid 1  (orifice plate = solid_cu, hole+slits = fluid)\n")
        f.write("yplus_est is laminar theory only; not a Fluent u_tau print\n")
        f.write(f"yplus_est_laminar {yplus:.3f}\n")
        f.write(f"circle_R_mm {R}\n")
        f.write(f"circle_nodes {len(on_r)}\n")
        if on_r:
            f.write(f"circle_r_err_max_mm {max(on_r):.6e}\n")
        f.write(f"t_tim_um 80\n")
        f.write(f"k_eff_R006 {K_EFF_MID:.6f}\n")
        f.write(f"q_flux_Wm2 {Q_FLUX:.6f}\n")
        f.write(f"P_cell_W {P_CELL:.6f}\n")
        f.write(f"msh {out}\n")
        for name, _, fs in face_groups:
            f.write(f"zone {name} {len(fs)}\n")
    if level == "medium":
        import shutil
        shutil.copyfile(out, os.path.join(here, "uc01b_cht.msh"))
        shutil.copyfile(meta, os.path.join(here, "cht_mesh_info.txt"))
    print(f"WROTE {out}")
    print(f"fluid={n_fluid} cu={n_cu} tim={n_tim} total={n_cells}")
    print(f"circle nodes~{len(on_r)} max|r-R|={max(on_r) if on_r else 'n/a'}")
    print(f"D={D} first={lv['first']} um-mm y+est={yplus:.2f}")


def _bound_name(xc, yc, zc, xs, ys, zs):
    if abs(zc - Z_TIM_BOT) < 1e-4 and max(zs) - min(zs) < 1e-6:
        return "wall_heat"
    if abs(zc - Z_IN) < 1e-4 and max(zs) - min(zs) < 1e-6:
        return "inlet_jet"
    if abs(zc - Z_LIDTOP) < 1e-4 and max(zs) - min(zs) < 1e-6:
        if abs(xc) > XL - 1e-6:
            return "return_slot"
        if (xc * xc + yc * yc) <= (R * R + 1e-8):
            return "inlet_jet"
        return "wall_lid"
    if abs(xc - X0) < 1e-4 or abs(xc - X1) < 1e-4 or abs(yc - Y0) < 1e-4 or abs(yc - Y1) < 1e-4:
        return "SYM"
    if max(zs) - min(zs) > 1e-6 and all(on_circle(x, y) for x, y in zip(xs, ys)):
        return "wall_orifice"
    if abs(zc - Z_LID) < 1e-3 and max(zs) - min(zs) < 1e-5:
        return "wall_lid"
    # vertical faces in lid/plenum not on circle → orifice or lid
    if zc > Z_LID - 1e-3:
        if all(abs(math.hypot(x, y) - R) < 0.05 for x, y in zip(xs, ys)):
            return "wall_orifice"
        return "wall_lid"
    return "wall_lid"


if __name__ == "__main__":
    main()
