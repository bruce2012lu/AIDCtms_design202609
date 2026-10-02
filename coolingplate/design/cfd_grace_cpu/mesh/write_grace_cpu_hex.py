# -*- coding: utf-8 -*-
"""CP-GRACE-MC-01 CPU-region all-hex mesh.

Single interior pitch (symmetry on rib mid-planes) is written as a Fluent msh.
The 48-channel array uses the same wall-normal law; this script prints its
cell budget and does not write the array file.

Units inside this file are millimetres. The msh is metres.
Basis: NVIDIA_Grace_GB300 cold-plate report v1.0 (2026-09-26),
CP-GRACE-MC-01_calc.py, make_grace_concept.py closeup().
"""
from __future__ import annotations

import math
import os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# Geometry locked to the Grace report. Plate origin is the cold-plate
# lower-left corner; chip face is z = 0. The single-channel mesh uses a
# local frame: x = 0 and x = pitch are rib mid-planes, y = 0 is the
# upstream end of the inlet extension, flow is +y.
PITCH = 0.80
CH_W = 0.40
CH_H = 1.20
CH_L = 32.0
EXT = 6.0  # 10 * Dh, Dh = 0.60 mm
FLOOR = 2.0
LID = 1.0  # z 3.2 -> 4.2; includes the 0.30 mm parting skin
TIM = 0.080
N_CH = 48
N_RIB = 49
MARGIN = 0.60  # (40 - 38.8) / 2 inside the 40 mm window
SHOULDER = 2.0  # unheated copper outside the window, for lateral spread
DY = 0.20

H1_FLUID = 0.0025
R_FLUID = 1.20
H1_SOLID = 0.020
R_SOLID = 1.50
N_TIM = 4

RHO = 992.0
MU = 6.53e-4
K_W = 0.632
CP = 4179.0
V_CH = 0.34  # m/s at the 0.47 L/min CPU share
Q_CPU = 0.47  # L/min
Q_FLUX = 260.0 / (0.040 * 0.032)  # W/m^2 on the 40 x 32 mm window
K_TIM = 8.818  # placeholder, same numeric layer as the B300 CHT coupon
T_IN = 313.15


def solve_r(length, h1, n):
    """Ratio r>1 whose n-term geometric series equals length. None if n*h1>length."""
    if n * h1 > length * (1.0 + 1e-9):
        return None
    if abs(n * h1 - length) <= 1e-9 * length:
        return 1.0
    target = length / h1

    def series(r):
        return (r ** n - 1.0) / (r - 1.0)

    lo, hi = 1.0 + 1e-12, 3.0
    if series(hi) < target:
        return None
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if series(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def geometric(length, h1, r_max, n_min):
    """One-sided geometric fill. First size is h1 (then a <1e-6 scale)."""
    n = n_min
    r = None
    while n < 80:
        r = solve_r(length, h1, n)
        if r is not None and r <= r_max + 1e-9:
            break
        n += 1
    else:
        raise RuntimeError("geometric fill failed for L=%s h1=%s" % (length, h1))
    sizes = [h1 * (r ** i) for i in range(n)]
    scale = length / sum(sizes)
    return [s * scale for s in sizes], r


def symmetric(length, h1, r_max):
    """Cluster both walls. Each half is a geometric series, r<=r_max, first=h1."""
    half = 0.5 * length
    n = 1
    r = None
    while n < 80:
        r = solve_r(half, h1, n)
        if r is not None and r <= r_max + 1e-9:
            break
        n += 1
    else:
        raise RuntimeError("symmetric fill failed")
    left = [h1 * (r ** i) for i in range(n)]
    left = [s * half / sum(left) for s in left]
    return left + list(reversed(left)), r


def both_ends(length, h1, r_max, n_min):
    """Solid slab clustered at both faces, growth <= r_max, at least n_min cells."""
    half = 0.5 * length
    n = max(1, (n_min + 1) // 2)
    r = None
    while n < 60:
        r = solve_r(half, h1, n)
        if r is not None and r <= r_max + 1e-9 and 2 * n >= n_min:
            break
        n += 1
    else:
        raise RuntimeError("both-ends fill failed")
    left = [h1 * (r ** i) for i in range(n)]
    left = [s * half / sum(left) for s in left]
    return left + list(reversed(left)), r


def uniform(length, n):
    h = length / float(n)
    return [h] * n


def cum(origin, sizes):
    xs = [origin]
    for h in sizes:
        xs.append(xs[-1] + h)
    xs[-1] = origin + sum(sizes)
    return xs


def max_ratio(sizes):
    m = 1.0
    for a, b in zip(sizes, sizes[1:]):
        m = max(m, a / b, b / a)
    return m


def y_nodes():
    n_ext = int(round(EXT / DY))
    n_ch = int(round(CH_L / DY))
    if abs(n_ext * DY - EXT) > 1e-9 or abs(n_ch * DY - CH_L) > 1e-9:
        raise RuntimeError("DY does not divide the channel or the extension")
    return cum(0.0, uniform(EXT, n_ext) + uniform(CH_L, n_ch) + uniform(EXT, n_ext))


def fluid_axes():
    sx, rx = symmetric(CH_W, H1_FLUID, R_FLUID)
    sz, rz = symmetric(CH_H, H1_FLUID, R_FLUID)
    return sx, rx, sz, rz


def solid_axes():
    rib, r_rib = geometric(PITCH / 4.0, H1_SOLID, R_SOLID, 6)  # half-rib 0.20, wall at the channel
    # geometric() clusters at the START of the list. For the left half-rib the
    # wall is at x = 0.20, so the sizes run large-to-small in +x.
    floor, r_floor = both_ends(FLOOR, H1_SOLID, R_SOLID, 6)
    lid, r_lid = geometric(LID, H1_SOLID, R_SOLID, 6)
    return rib, r_rib, floor, r_floor, lid, r_lid


def single_xyz():
    """Node coordinates for one pitch. x=0 and x=pitch are rib mid-planes."""
    sx, _, sz, _ = fluid_axes()
    rib, _, floor, _, lid, _ = solid_axes()
    x_left = cum(0.0, list(reversed(rib)))  # coarse at symmetry, fine at the wall
    x_fluid = cum(x_left[-1], sx)
    x_right = cum(x_fluid[-1], rib)  # fine at the wall, coarse at symmetry
    x = x_left + x_fluid[1:] + x_right[1:]
    y = y_nodes()
    z_tim = cum(-TIM, uniform(TIM, N_TIM))
    z_floor = cum(0.0, floor)
    z_chan = cum(FLOOR, sz)
    z_lid = cum(FLOOR + CH_H, lid)
    return {
        "x": x,
        "x_wall_l": x_left[-1],
        "x_wall_r": x_fluid[-1],
        "y": y,
        "y_heat0": EXT,
        "y_heat1": EXT + CH_L,
        "z_tim": z_tim,
        "z_floor": z_floor,
        "z_chan": z_chan,
        "z_lid": z_lid,
        "z_top": z_lid[-1],
    }


def array_x():
    """Plate-X node list for 49 ribs + 48 channels + window margins + shoulders.

    Local x = 0 at plate X = 80 - SHOULDER. Finned field is centered on
    X 80-120: width 49*0.40 + 48*0.40 = 38.8 mm, inset 0.60 mm.
    """
    sx, _, _, _ = fluid_axes()
    rib_half, _, _, _, _, _ = solid_axes()
    rib_full = rib_half + list(reversed(rib_half))
    outer, _ = geometric(CH_W, H1_SOLID, R_SOLID, 6)  # 0.40 mm, fine at the fluid face
    # Left outer rib: fluid face is on the right, so reverse.
    margin, _ = geometric(MARGIN, H1_SOLID, R_SOLID, 4)
    shoulder = uniform(SHOULDER, 10)
    parts = [shoulder, list(reversed(margin)), list(reversed(outer))]
    for i in range(N_CH):
        parts.append(sx)
        if i < N_CH - 1:
            parts.append(rib_full)
    parts.append(outer)  # right outer rib, fine at its left (fluid) face
    parts.append(margin)
    parts.append(shoulder)
    x = [0.0]
    for sizes in parts:
        x.extend(cum(x[-1], sizes)[1:])
    return x, parts


def cell_counts(ax):
    def n(a):
        return len(a) - 1

    nx = n(ax["x"])
    ny = n(ax["y"])
    ny_h = sum(1 for a, b in zip(ax["y"], ax["y"][1:]) if a >= ax["y_heat0"] - 1e-9 and b <= ax["y_heat1"] + 1e-9)
    nz_f = n(ax["z_floor"])
    nz_c = n(ax["z_chan"])
    nz_l = n(ax["z_lid"])
    i0 = next(i for i, v in enumerate(ax["x"]) if abs(v - ax["x_wall_l"]) < 1e-8)
    i1 = next(i for i, v in enumerate(ax["x"]) if abs(v - ax["x_wall_r"]) < 1e-8)
    nx_f = i1 - i0
    nx_rib = nx - nx_f
    fluid = nx_f * ny * nz_c
    rib = nx_rib * ny * nz_c
    floor = nx * ny * nz_f
    lid = nx * ny * nz_l
    tim = nx * ny_h * N_TIM
    return {
        "nx": nx,
        "ny": ny,
        "ny_heat": ny_h,
        "nx_fluid": nx_f,
        "nx_rib": nx_rib,
        "nz_floor": nz_f,
        "nz_chan": nz_c,
        "nz_lid": nz_l,
        "nz_tim": N_TIM,
        "fluid": fluid,
        "rib": rib,
        "floor": floor,
        "lid": lid,
        "tim": tim,
        "total": fluid + rib + floor + lid + tim,
    }


def array_budget():
    x, parts = array_x()
    _, _, sz, _ = fluid_axes()
    _, _, floor, _, lid, _ = solid_axes()
    y = y_nodes()
    ny = len(y) - 1
    ny_h = int(round(CH_L / DY))
    nz_c = len(sz)
    nz_f = len(floor)
    nz_l = len(lid)
    # parts: shoulder, margin, outer, then (channel, rib)*47, channel, outer, margin, shoulder
    n_shoulder = len(parts[0])
    n_margin = len(parts[1])
    n_outer = len(parts[2])
    n_fluid_one = len(parts[3])
    n_rib_one = len(parts[4])
    nx = len(x) - 1
    nx_fluid = N_CH * n_fluid_one
    nx_rib = (N_CH - 1) * n_rib_one + 2 * n_outer
    nx_side = 2 * (n_shoulder + n_margin)
    if nx_fluid + nx_rib + nx_side != nx:
        raise RuntimeError("array x split %s+%s+%s != %s" % (nx_fluid, nx_rib, nx_side, nx))
    fluid = nx_fluid * ny * nz_c
    rib = nx_rib * ny * nz_c
    side = nx_side * ny * nz_c  # shoulder + margin occupy the channel band as copper
    # TIM and heat cover the 40 mm window, not the shoulders.
    nx_window = nx - 2 * n_shoulder
    floor_c = nx * ny * nz_f
    lid_c = nx * ny * nz_l
    tim = nx_window * ny_h * N_TIM
    cu = rib + side + floor_c + lid_c
    return {
        "nx": nx,
        "ny": ny,
        "nx_fluid": nx_fluid,
        "nx_rib": nx_rib,
        "nx_side": nx_side,
        "nx_window": nx_window,
        "width_mm": x[-1],
        "plate_x0": 80.0 - SHOULDER,
        "fluid": fluid,
        "cu": cu,
        "tim": tim,
        "total": fluid + cu + tim,
        "nz_chan": nz_c,
        "nz_floor": nz_f,
        "nz_lid": nz_l,
    }


def yplus(y_m, v=V_CH):
    """Fully developed rectangular-duct estimate. Not a Fluent wall y+."""
    alpha = CH_W / CH_H
    p = 24.0 * (
        1.0
        - 1.3553 * alpha
        + 1.9467 * alpha ** 2
        - 1.7012 * alpha ** 3
        + 0.9564 * alpha ** 4
        - 0.2537 * alpha ** 5
    )
    dh = 2.0 * (CH_W * CH_H) * 1e-6 / ((CH_W + CH_H) * 1e-3)
    re = RHO * v * dh / MU
    tau = (p / re) * RHO * v * v / 2.0
    nu = MU / RHO
    return y_m * math.sqrt(tau / RHO) / nu, re, tau, p


def check_laws(ax):
    sx, rx, sz, rz = fluid_axes()
    rib, r_rib, floor, r_floor, lid, r_lid = solid_axes()
    problems = []
    if sx[0] > 0.003 + 1e-6 or sz[0] > 0.003 + 1e-6:
        problems.append("fluid first layer > 3 um")
    if max_ratio(sx) > R_FLUID + 0.01 or max_ratio(sz) > R_FLUID + 0.01:
        problems.append("fluid growth > 1.2")
    if len(sx) < 8 or len(sz) < 12:
        problems.append("channel cross-section below 8 x 12")
    if len(floor) < 6 or len(rib) < 6 or len(lid) < 6:
        problems.append("solid through-thickness below 6")
    if EXT < 10.0 * 0.60 - 1e-9:
        problems.append("extension shorter than 10 Dh")
    yp, re, _, _ = yplus(sx[0] * 1e-3)
    if yp >= 1.0 or yp * math.sqrt(5.0) >= 1.0:
        problems.append("y+ estimate is not < 1")
    counts = cell_counts(ax)
    if counts["total"] >= 1_000_000:
        problems.append("single channel has %s cells" % counts["total"])
    return problems, counts, (rx, rz, r_rib, r_floor, r_lid, yp, re)


def write_msh(path, ax):
    x = ax["x"]
    y = ax["y"]
    i_wl = next(i for i, v in enumerate(x) if abs(v - ax["x_wall_l"]) < 1e-8)
    i_wr = next(i for i, v in enumerate(x) if abs(v - ax["x_wall_r"]) < 1e-8)
    j0 = next(j for j, v in enumerate(y) if abs(v - ax["y_heat0"]) < 1e-8)
    j1 = next(j for j, v in enumerate(y) if abs(v - ax["y_heat1"]) < 1e-8)

    # Blocks: (zone, i0, i1, j0, j1, z_nodes). Indices are node indices on x/y.
    blocks = []
    blocks.append(("tim", 0, len(x) - 1, j0, j1, ax["z_tim"]))
    blocks.append(("cu", 0, len(x) - 1, 0, len(y) - 1, ax["z_floor"]))
    blocks.append(("cu", 0, i_wl, 0, len(y) - 1, ax["z_chan"]))
    blocks.append(("fluid", i_wl, i_wr, 0, len(y) - 1, ax["z_chan"]))
    blocks.append(("cu", i_wr, len(x) - 1, 0, len(y) - 1, ax["z_chan"]))
    blocks.append(("cu", 0, len(x) - 1, 0, len(y) - 1, ax["z_lid"]))

    nodes = {}
    coords = []

    def nid(px, py, pz):
        key = (round(px, 7), round(py, 7), round(pz, 7))
        got = nodes.get(key)
        if got is None:
            got = len(coords) + 1
            nodes[key] = got
            coords.append((px * 1e-3, py * 1e-3, pz * 1e-3))
        return got

    # cell id per zone, contiguous: fluid, cu, tim
    pending = {name: [] for name in ("fluid", "cu", "tim")}
    for zone, ia, ib, ja, jb, z in blocks:
        for i in range(ia, ib):
            for j in range(ja, jb):
                for k in range(len(z) - 1):
                    pending[zone].append((i, j, k, z))

    cell_of = {}
    cid = 0
    zone_range = {}
    for zone in ("fluid", "cu", "tim"):
        a = cid + 1
        for i, j, k, z in pending[zone]:
            cid += 1
            cell_of[(zone, i, j, k, z[0], z[-1])] = cid
        zone_range[zone] = (a, cid)
    n_cells = cid

    # Face key -> (nids, c0, zone0). Second visit classifies.
    seen = {}
    interiors = []
    bounds = defaultdict(list)

    def classify(nids, c0, z0, c1, z1):
        if z0 == z1:
            interiors.append((nids, c0, c1))
            return
        pair = {z0, z1}
        if pair == {"fluid", "cu"}:
            name = "wall_cu_fluid"
        elif pair == {"cu", "tim"}:
            name = "wall_tim_cu"
        else:
            name = "wall_other"
        bounds[name].append((nids, c0, c1))

    def push(nids, cid_, zone):
        key = tuple(sorted(nids))
        prev = seen.get(key)
        if prev is None:
            seen[key] = (nids, cid_, zone)
        else:
            n0, c0, z0 = seen.pop(key)
            classify(n0, c0, z0, cid_, zone)

    def emit_block(zone, ia, ib, ja, jb, z):
        for i in range(ia, ib):
            x0, x1 = x[i], x[i + 1]
            for j in range(ja, jb):
                y0, y1 = y[j], y[j + 1]
                for k in range(len(z) - 1):
                    z0, z1 = z[k], z[k + 1]
                    cid_ = cell_of[(zone, i, j, k, z[0], z[-1])]
                    n000 = nid(x0, y0, z0)
                    n100 = nid(x1, y0, z0)
                    n110 = nid(x1, y1, z0)
                    n010 = nid(x0, y1, z0)
                    n001 = nid(x0, y0, z1)
                    n101 = nid(x1, y0, z1)
                    n111 = nid(x1, y1, z1)
                    n011 = nid(x0, y1, z1)
                    push((n000, n100, n110, n010), cid_, zone)
                    push((n001, n101, n111, n011), cid_, zone)
                    push((n000, n100, n101, n001), cid_, zone)
                    push((n010, n110, n111, n011), cid_, zone)
                    push((n000, n010, n011, n001), cid_, zone)
                    push((n100, n110, n111, n101), cid_, zone)

    for zone, ia, ib, ja, jb, z in blocks:
        emit_block(zone, ia, ib, ja, jb, z)

    x0 = x[0]
    x1 = x[-1]
    y0 = y[0]
    y1 = y[-1]
    z_bot = ax["z_tim"][0]
    z_top = ax["z_top"]
    z_chan0 = FLOOR
    z_chan1 = FLOOR + CH_H

    def bound_name(nids):
        pts = [coords[i - 1] for i in nids]
        xs = [p[0] * 1e3 for p in pts]
        ys = [p[1] * 1e3 for p in pts]
        zs = [p[2] * 1e3 for p in pts]
        xc = sum(xs) / 4.0
        yc = sum(ys) / 4.0
        zc = sum(zs) / 4.0
        if max(xs) - min(xs) < 1e-6:
            if abs(xc - x0) < 1e-6 or abs(xc - x1) < 1e-6:
                return "sym"
        if max(ys) - min(ys) < 1e-6:
            in_fluid = ax["x_wall_l"] - 1e-6 < xc < ax["x_wall_r"] + 1e-6 and z_chan0 - 1e-6 < zc < z_chan1 + 1e-6
            if abs(yc - y0) < 1e-6 and in_fluid:
                return "inlet"
            if abs(yc - y1) < 1e-6 and in_fluid:
                return "outlet"
        if max(zs) - min(zs) < 1e-6 and abs(zc - z_bot) < 1e-6:
            return "wall_heat"
        return "wall_adi"

    for nids, c0, _zone in seen.values():
        bounds[bound_name(nids)].append((nids, c0, 0))

    def orient(nids, c0):
        p0, p1, p2 = (coords[nids[0] - 1], coords[nids[1] - 1], coords[nids[2] - 1])
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        if nx * nx + ny * ny + nz * nz < 1e-30:
            p3 = coords[nids[3] - 1]
            vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
        fc = tuple(sum(coords[i - 1][a] for i in nids) / 4.0 for a in range(3))
        gx = gy = gz = 0.0
        # cell center from the eight nodes is not stored; use c0's block center
        # reconstructed as the average of this face plus a step toward c0.
        # The cell id map is enough: look up any stored center via face-adjacent
        # node average is wrong. Store centers below.
        return nids, (nx, ny, nz), fc

    centers = {}
    for zone, ia, ib, ja, jb, z in blocks:
        for i in range(ia, ib):
            for j in range(ja, jb):
                for k in range(len(z) - 1):
                    cid_ = cell_of[(zone, i, j, k, z[0], z[-1])]
                    centers[cid_] = (
                        0.5 * (x[i] + x[i + 1]) * 1e-3,
                        0.5 * (y[j] + y[j + 1]) * 1e-3,
                        0.5 * (z[k] + z[k + 1]) * 1e-3,
                    )

    def toward(nids, c0):
        p0, p1, p2 = (coords[nids[0] - 1], coords[nids[1] - 1], coords[nids[2] - 1])
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        nx = uy * vz - uz * vy
        ny = uz * vx - ux * vz
        nz = ux * vy - uy * vx
        if nx * nx + ny * ny + nz * nz < 1e-30:
            p3 = coords[nids[3] - 1]
            vx, vy, vz = p3[0] - p0[0], p3[1] - p0[1], p3[2] - p0[2]
            nx = uy * vz - uz * vy
            ny = uz * vx - ux * vz
            nz = ux * vy - uy * vx
        fc = tuple(sum(coords[i - 1][a] for i in nids) / 4.0 for a in range(3))
        gx, gy, gz = centers[c0]
        if nx * (gx - fc[0]) + ny * (gy - fc[1]) + nz * (gz - fc[2]) < 0.0:
            return (nids[0], nids[3], nids[2], nids[1])
        return nids

    interiors = [(toward(n, c0), c0, c1) for n, c0, c1 in interiors]
    for name in list(bounds):
        bounds[name] = [(toward(n, c0), c0, c1) for n, c0, c1 in bounds[name]]

    order = (
        ("interior", 2),
        ("inlet", 10),
        ("outlet", 5),
        ("wall_heat", 3),
        ("wall_cu_fluid", 3),
        ("wall_tim_cu", 3),
        ("wall_adi", 3),
        ("wall_other", 3),
        ("sym", 7),
    )
    groups = []
    for name, bc in order:
        if name == "interior":
            groups.append((name, bc, interiors))
        elif bounds.get(name):
            groups.append((name, bc, bounds[name]))
    n_faces = sum(len(fs) for _, _, fs in groups)
    n_nodes = len(coords)

    def hx(n):
        return format(int(n), "x")

    zone_ids = {}
    fid = 5
    for name, _, _ in groups:
        zone_ids[name] = fid
        fid += 1
    id_fluid = zone_range["fluid"]
    id_cu = zone_range["cu"]
    id_tim = zone_range["tim"]

    with open(path, "w", encoding="ascii", newline="\n") as f:
        w = f.write
        w('(0 "CP-GRACE-MC-01 CPU single pitch CHT hex; mm design, msh in metres; first 2.5 um")\n')
        w("(2 3)\n")
        w("(10 (0 1 %s 0 3))\n" % hx(n_nodes))
        w("(12 (0 1 %s 0 0))\n" % hx(n_cells))
        w("(13 (0 1 %s 0 0))\n" % hx(n_faces))
        w("(10 (1 1 %s 1 3)\n(\n" % hx(n_nodes))
        for xx, yy, zz in coords:
            w("%.10e %.10e %.10e\n" % (xx, yy, zz))
        w(")\n)\n")
        w("(12 (2 %s %s 1 4))\n" % (hx(id_fluid[0]), hx(id_fluid[1])))
        w("(12 (3 %s %s 1 4))\n" % (hx(id_cu[0]), hx(id_cu[1])))
        w("(12 (4 %s %s 1 4))\n" % (hx(id_tim[0]), hx(id_tim[1])))
        fstart = 1
        for name, bc, fs in groups:
            fend = fstart + len(fs) - 1
            w("(13 (%s %s %s %s 4)\n(\n" % (hx(zone_ids[name]), hx(fstart), hx(fend), hx(bc)))
            for nids, c0, c1 in fs:
                w("%s %s %s %s %s %s\n" % (hx(nids[0]), hx(nids[1]), hx(nids[2]), hx(nids[3]), hx(c0), hx(c1)))
            w(")\n)\n")
            fstart = fend + 1
        w("(39 (2 fluid fluid)())\n")
        w("(39 (3 solid solid_cu)())\n")
        w("(39 (4 solid solid_tim2)())\n")
        kind = {2: "interior", 3: "wall", 5: "pressure-outlet", 7: "symmetry", 10: "mass-flow-inlet"}
        for name, bc, _ in groups:
            w("(39 (%d %s %s)())\n" % (zone_ids[name], kind[bc], name))

    inlet_area = 0.0
    for nids, _, _ in bounds["inlet"]:
        p = [coords[i - 1] for i in nids]
        # quad area, planar
        axu = p[1][0] - p[0][0], p[1][1] - p[0][1], p[1][2] - p[0][2]
        axv = p[3][0] - p[0][0], p[3][1] - p[0][1], p[3][2] - p[0][2]
        cx = axu[1] * axv[2] - axu[2] * axv[1]
        cy = axu[2] * axv[0] - axu[0] * axv[2]
        cz = axu[0] * axv[1] - axu[1] * axv[0]
        inlet_area += math.sqrt(cx * cx + cy * cy + cz * cz)
    return {
        "nodes": n_nodes,
        "faces": n_faces,
        "cells": n_cells,
        "zones": {name: len(fs) for name, _, fs in groups},
        "inlet_area_m2": inlet_area,
        "id_fluid": id_fluid,
        "id_cu": id_cu,
        "id_tim": id_tim,
    }


def write_replay(path, ax):
    """ICEM Tcl: blocking skeleton in millimetres. Replay in an open ICEM."""
    xs = sorted({round(v, 6) for v in (
        ax["x"][0], ax["x_wall_l"], ax["x_wall_r"], ax["x"][-1]
    )})
    ys = [0.0, ax["y_heat0"], ax["y_heat1"], ax["y"][-1]]
    zs = [ax["z_tim"][0], 0.0, FLOOR, FLOOR + CH_H, ax["z_top"]]
    sx, rx, sz, rz = fluid_axes()
    rib, r_rib, floor, r_floor, lid, r_lid = solid_axes()
    lines = [
        "# CP-GRACE-MC-01 CPU single pitch. Units: MILLIMETRES.",
        "# File -> Replay Scripts -> Replay. Do not start a second icemcfd.",
        "# This builds the block corners and saves a tetin. Edge node counts",
        "# are printed for Hexa blocking. The Fluent msh written beside this",
        "# replay uses these same distributions.",
        "set OUTDIR {D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_grace_cpu}",
        "set ICEMDIR [file join $OUTDIR icem]",
        "file mkdir $ICEMDIR",
        'puts "GRACE-CPU channel replay (mm): start"',
        "catch { ic_uns_new }",
        "catch { ic_geo_delete_all }",
        "catch { ic_hex_unload_blocking }",
        "foreach fam {FLUID SOLID_CU SOLID_TIM INLET OUTLET WALL_HEAT WALL_ADI SYM GEOM} {",
        "    catch { ic_geo_new_family $fam }",
        "}",
    ]
    nx, ny, nz = len(xs), len(ys), len(zs)

    def pid(ix, iy, iz):
        return (iz * ny + iy) * nx + ix

    for iz, z in enumerate(zs):
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                lines.append(
                    "catch { ic_point {} POINT p%03d %.6f,%.6f,%.6f }" % (pid(ix, iy, iz), x, y, z)
                )
    ci = 0
    for iz in range(nz):
        for iy in range(ny):
            for ix in range(nx):
                if ix + 1 < nx:
                    lines.append(
                        "catch { ic_curve point CRV e%03d [list p%03d p%03d] }"
                        % (ci, pid(ix, iy, iz), pid(ix + 1, iy, iz))
                    )
                    ci += 1
                if iy + 1 < ny:
                    lines.append(
                        "catch { ic_curve point CRV e%03d [list p%03d p%03d] }"
                        % (ci, pid(ix, iy, iz), pid(ix, iy + 1, iz))
                    )
                    ci += 1
                if iz + 1 < nz:
                    lines.append(
                        "catch { ic_curve point CRV e%03d [list p%03d p%03d] }"
                        % (ci, pid(ix, iy, iz), pid(ix, iy, iz + 1))
                    )
                    ci += 1
    lines += [
        'puts "points %d curves %d"' % (nx * ny * nz, ci),
        'puts "EDGE fluid-x cells %d first_mm %.6f ratio %.4f"' % (len(sx), sx[0], rx),
        'puts "EDGE fluid-z cells %d first_mm %.6f ratio %.4f"' % (len(sz), sz[0], rz),
        'puts "EDGE half-rib-x cells %d first_mm %.6f ratio %.4f (fine at the fluid wall)"' % (len(rib), rib[0], r_rib),
        'puts "EDGE floor-z cells %d first_mm %.6f ratio %.4f"' % (len(floor), floor[0], r_floor),
        'puts "EDGE lid-z cells %d first_mm %.6f ratio %.4f"' % (len(lid), lid[0], r_lid),
        'puts "EDGE streamwise dy_mm %.3f n_ext %d n_heat %d"' % (DY, int(round(EXT / DY)), int(round(CH_L / DY))),
        "set tin [file join $ICEMDIR grace_cpu_channel.tin]",
        "catch { ic_save_tetin $tin }",
        'puts "saved $tin"',
        'puts "GRACE-CPU channel replay: done"',
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def write_info(path, ax, mesh_meta, problems, ratios, budget):
    sx, rx, sz, rz = fluid_axes()
    rib, r_rib, floor, r_floor, lid, r_lid = solid_axes()
    counts = cell_counts(ax)
    rx_, rz_, r_rib_, r_floor_, r_lid_, yp, re = ratios
    yp5 = yp * math.sqrt(5.0)
    mdot = (Q_CPU / 1000.0 / 60.0) / N_CH * RHO
    area = CH_W * CH_H * 1e-6
    lines = [
        "CP-GRACE-MC-01 CPU cooling region, single interior pitch",
        "basis: Grace cold-plate report v1.0, section 4. CPU window X 80-120, Y 44-76",
        "channel 0.40 x 1.20 mm, pitch 0.80 mm, heated length 32 mm along Y",
        "local frame: x=0 and x=0.80 rib mid-planes; y=0 upstream end; flow +y",
        "plate map: channel inlet (local y=6) is plate Y=76; outlet (local y=38) is plate Y=44",
        "plate map: local y_plate = 82 - y_local",
        "extensions %.3f mm each end = 10 Dh, Dh=0.60 mm, same 0.40 x 1.20 section" % EXT,
        "solids: floor z 0-2.0, ribs, lid cap z 3.2-%.3f (parting skin 0.30 mm included)" % ax["z_top"],
        "TIM z -0.080-0 on the heated 32 mm only. Thickness is not in the Grace ICD.",
        "k_tim %.3f W/mK is the B300 coupon number, not a Grace measurement." % K_TIM,
        "lid above z=%.3f is omitted; cut face is adiabatic." % ax["z_top"],
        "",
        "cells_total %d" % counts["total"],
        "cells_fluid %d" % counts["fluid"],
        "cells_rib %d" % counts["rib"],
        "cells_floor %d" % counts["floor"],
        "cells_lid %d" % counts["lid"],
        "cells_tim %d" % counts["tim"],
        "nx %d nx_fluid %d nx_rib %d" % (counts["nx"], counts["nx_fluid"], counts["nx_rib"]),
        "ny %d ny_heat %d" % (counts["ny"], counts["ny_heat"]),
        "nz_floor %d nz_chan %d nz_lid %d nz_tim %d" % (
            counts["nz_floor"], counts["nz_chan"], counts["nz_lid"], counts["nz_tim"]
        ),
        "fluid_x_first_mm %.6f fluid_x_ratio %.4f fluid_x_cells %d max_ratio %.4f" % (
            sx[0], rx, len(sx), max_ratio(sx)
        ),
        "fluid_z_first_mm %.6f fluid_z_ratio %.4f fluid_z_cells %d max_ratio %.4f" % (
            sz[0], rz, len(sz), max_ratio(sz)
        ),
        "rib_half_first_mm %.6f rib_ratio %.4f rib_cells %d" % (rib[0], r_rib, len(rib)),
        "floor_first_mm %.6f floor_ratio %.4f floor_cells %d" % (floor[0], r_floor, len(floor)),
        "lid_first_mm %.6f lid_ratio %.4f lid_cells %d" % (lid[0], r_lid, len(lid)),
        "dy_mm %.3f" % DY,
        "Re_Dh %.2f" % re,
        "yplus_fd %.4f" % yp,
        "yplus_if_tau_x5 %.4f" % yp5,
        "yplus_note fully developed Shah-London rectangular duct; x5 is an entrance bound, not a Fluent print",
        "q_flux_W_m2 %.6f" % Q_FLUX,
        "mdot_channel_kg_s %.8e" % mdot,
        "V_m_s %.4f" % V_CH,
        "pitch_power_W %.4f" % (Q_FLUX * (PITCH * CH_L) * 1e-6),
        "",
    ]
    if mesh_meta:
        lines += [
            "msh_nodes %d" % mesh_meta["nodes"],
            "msh_faces %d" % mesh_meta["faces"],
            "msh_cells %d" % mesh_meta["cells"],
            "inlet_area_m2 %.8e" % mesh_meta["inlet_area_m2"],
            "inlet_area_expect_m2 %.8e" % area,
            "inlet_area_rel_err %.3e" % (abs(mesh_meta["inlet_area_m2"] - area) / area),
        ]
        for name, n in sorted(mesh_meta["zones"].items()):
            lines.append("zone %s %d" % (name, n))
    lines += [
        "",
        "ARRAY 48 channels, 49 ribs, finned width 38.8 mm centered in X 80-120",
        "ARRAY shoulders %.2f mm unheated copper outside the window, each side" % SHOULDER,
        "ARRAY same fluid first layer, same growth, same dy",
        "ARRAY cells_fluid %d" % budget["fluid"],
        "ARRAY cells_cu %d" % budget["cu"],
        "ARRAY cells_tim %d" % budget["tim"],
        "ARRAY cells_total %d" % budget["total"],
        "ARRAY nx %d ny %d width_mm %.3f plate_x0 %.3f" % (
            budget["nx"], budget["ny"], budget["width_mm"], budget["plate_x0"]
        ),
        "ARRAY file not written; total is above a single-workstation ASCII msh",
        "",
        "problems %d" % len(problems),
    ]
    for p in problems:
        lines.append("PROBLEM %s" % p)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def write_array_replay(path, budget):
    """Array skeleton: one streamwise line on every block face. Millimetres."""
    walls = [0.0, SHOULDER, SHOULDER + MARGIN, SHOULDER + MARGIN + CH_W]
    cursor = walls[-1]
    for i in range(N_CH):
        walls.append(round(cursor, 6))
        cursor += CH_W
        walls.append(round(cursor, 6))
        if i < N_CH - 1:
            cursor += CH_W
    cursor = walls[-1] + CH_W + MARGIN + SHOULDER
    walls.append(round(walls[-1] + CH_W, 6))
    walls.append(round(walls[-1] + MARGIN, 6))
    walls.append(round(cursor, 6))
    # Drop the duplicated left-outer-rib station (index 2 and the first channel wall).
    cleaned = []
    for value in walls:
        if not cleaned or abs(value - cleaned[-1]) > 1e-6:
            cleaned.append(value)
    walls = cleaned
    if abs(walls[-1] - budget["width_mm"]) > 1e-6:
        raise RuntimeError("array skeleton width %.6f != %.6f" % (walls[-1], budget["width_mm"]))
    y1 = EXT + CH_L + EXT
    lines = [
        "# CP-GRACE-MC-01 CPU channel array. Units: MILLIMETRES.",
        "# 48 channels, 49 ribs, finned width 38.8 mm, centered in the 40 mm window.",
        "# Local x=0 is plate X=%.1f. Channel walls are the curves named wall_*." % (80.0 - SHOULDER),
        "# Fluid wall-normal law matches the single-pitch mesh: first 0.0025 mm, growth <= 1.20.",
        "# Cell budget is icem/array_budget.txt. This replay does not mesh the %.2f M cells." % (budget["total"] / 1e6),
        "set OUTDIR {D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_grace_cpu}",
        "set ICEMDIR [file join $OUTDIR icem]",
        "file mkdir $ICEMDIR",
        'puts "GRACE-CPU array replay (mm): start"',
        "catch { ic_geo_delete_all }",
        "foreach fam {FLUID SOLID_CU SOLID_TIM INLET OUTLET WALL_HEAT WALL_ADI GEOM} {",
        "    catch { ic_geo_new_family $fam }",
        "}",
    ]
    for i, xw in enumerate(walls):
        lines.append("catch { ic_point {} POINT a%03d %.6f,%.6f,%.6f }" % (i, xw, 0.0, FLOOR))
        lines.append("catch { ic_point {} POINT b%03d %.6f,%.6f,%.6f }" % (i, xw, y1, FLOOR))
        lines.append("catch { ic_curve point CRV wall_%03d [list a%03d b%03d] }" % (i, i, i))
    lines += [
        'puts "channel-wall curves %d  width_mm %.3f  cells %d"' % (len(walls), walls[-1], budget["total"]),
        "set tin [file join $ICEMDIR grace_cpu_array.tin]",
        "catch { ic_save_tetin $tin }",
        'puts "saved $tin"',
        'puts "GRACE-CPU array replay: done"',
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    os.makedirs(os.path.join(ROOT, "icem"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "fluent"), exist_ok=True)
    os.makedirs(HERE, exist_ok=True)
    ax = single_xyz()
    problems, counts, ratios = check_laws(ax)
    budget = array_budget()
    print("single", counts["total"], "fluid", counts["fluid"], "x", counts["nx_fluid"], "z", counts["nz_chan"])
    print("array", budget["total"], "fluid", budget["fluid"], "width", round(budget["width_mm"], 3))
    yp = ratios[5]
    print("yplus_fd", round(yp, 4), "yplus_x5", round(yp * math.sqrt(5.0), 4))
    if problems:
        for p in problems:
            print("PROBLEM", p)
        raise SystemExit(1)
    msh = os.path.join(HERE, "grace_cpu_channel.msh")
    print("writing", msh)
    meta = write_msh(msh, ax)
    print("wrote cells", meta["cells"], "zones", meta["zones"], "inlet_mm2", meta["inlet_area_m2"] * 1e6)
    rel = abs(meta["inlet_area_m2"] - CH_W * CH_H * 1e-6) / (CH_W * CH_H * 1e-6)
    if rel > 1e-6:
        raise SystemExit("inlet area error %s" % rel)
    write_replay(os.path.join(ROOT, "icem", "build_grace_cpu_channel.rpl"), ax)
    write_array_replay(os.path.join(ROOT, "icem", "build_grace_cpu_array.rpl"), budget)
    write_info(os.path.join(HERE, "grace_cpu_channel_info.txt"), ax, meta, problems, ratios, budget)
    # Edge law for the array, same fluid distribution.
    with open(os.path.join(ROOT, "icem", "array_budget.txt"), "w", encoding="utf-8", newline="\n") as f:
        for k in (
            "width_mm", "plate_x0", "nx", "ny", "nx_fluid", "nx_rib", "nx_side",
            "nz_chan", "nz_floor", "nz_lid", "fluid", "cu", "tim", "total",
        ):
            f.write("%s %s\n" % (k, budget[k]))
    print("info ok")


if __name__ == "__main__":
    main()
