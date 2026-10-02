# -*- coding: utf-8 -*-
"""CP-GRACE-MC-01 CPU pair, counterflow along plate Y.

Report axes: origin at the cold-plate lower-left corner, X along the
tray width, Y toward the rear panel and the GPU, chip face z = 0.

Even channel (local x 0.20-0.60) flows +Y, from the front toward the rear.
Odd channel (local x 1.00-1.40) flows -Y, from the rear toward the front.
Each end is closed in Y. Fluid enters horizontally into a gallery,
hits that wall, and drops in Z into the channel. The return path
does the reverse.

One pair is 1.60 mm in X. Twenty-four pairs are the 48-channel field.
Local y = 0 is plate Y = 44; local y = 32 is plate Y = 76.
Units here are millimetres. The msh is metres.
"""
from __future__ import annotations

import math
import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from write_grace_cpu_hex import both_ends, cum, geometric, symmetric, uniform

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DX = 0.40
H1_CH = 0.0025
R_CH = 1.20
H1_CU = 0.020
R_CU = 1.50

# Planes that must exist. Channel end walls are the four Y-blocks.
# Local y = 0 is the front edge of the heated window (plate Y = 44).
Y_ODD_OUT = -8.0
Y_ODD_WL = -5.5
Y_EVEN_IN = -4.0
Y_EVEN_WL = -2.5
Y_EVEN_GAL = -1.0
Y0 = 0.0
Y1 = 32.0
Y_ODD_GAL = 33.0
Y_ODD_WR = 34.5
Y_ODD_IN = 36.0
Y_EVEN_WR = 37.5
Y_EVEN_OUT = 40.0

Z_TIM0 = -0.080
Z_CH0 = 2.0
Z_CH1 = 3.2
Z_GAL0 = 4.3
Z_GAL1 = 5.6
Z_TOP = 6.6

RHO = 992.0
Q_CPU_LMIN = 0.47
N_PAIR = 24
N_CH = 48
Q_FLUX = 260.0 / (0.040 * 0.032)
K_TIM = 8.818


def stack_from(h0, hmax, ratio, limit):
    hs = []
    h = h0
    used = 0.0
    while used + h <= limit + 1e-9 and h <= hmax * 1.001:
        hs.append(h)
        used += h
        nxt = h * ratio
        if nxt > hmax * 1.001:
            break
        h = nxt
    return hs


def fill_segment(length, h_left, h_right):
    """Sizes summing to length. h_* None means that end is not clustered."""
    def ratio_of(h):
        return R_CH if h and h <= H1_CH * 1.01 else R_CU

    left = stack_from(h_left, DX, ratio_of(h_left), length * 0.5) if h_left else []
    right = stack_from(h_right, DX, ratio_of(h_right), length * 0.5) if h_right else []
    while left and right and sum(left) + sum(right) > length - 1e-8:
        if left[-1] >= right[-1]:
            left.pop()
        else:
            right.pop()
    rem = length - sum(left) - sum(right)
    if left and right and 0 < rem <= left[-1] + right[-1]:
        left[-1] += rem * 0.5
        right[-1] += rem * 0.5
        rem = 0.0
    elif left and 0 < rem < left[-1]:
        left[-1] += rem
        rem = 0.0
    elif right and 0 < rem < right[-1]:
        right[-1] += rem
        rem = 0.0
    sizes = list(left)
    if rem > 1e-8:
        n = max(1, int(round(rem / DX)))
        h_u = rem / n
        grow = ratio_of(h_left)
        guard = 0
        while left and h_u > left[-1] * grow * 1.02 and guard < 50:
            n += 1
            h_u = rem / n
            guard += 1
        grow_r = ratio_of(h_right)
        while right and h_u > right[-1] * grow_r * 1.02 and guard < 100:
            n += 1
            h_u = rem / n
            guard += 1
        sizes.extend([h_u] * n)
    sizes.extend(reversed(right))
    scale = length / sum(sizes)
    sizes = [s * scale for s in sizes]
    return sizes


def insert_planes(xs, planes):
    xs = list(xs)
    protected = (Y_ODD_OUT, Y_ODD_WL, Y_EVEN_WL, Y_ODD_WR, Y_EVEN_WR, Y_EVEN_OUT)

    def locked(v):
        return any(abs(v - q) < 1e-4 for q in protected)

    for p in planes:
        if any(abs(v - p) < 1e-6 for v in xs):
            continue
        for i in range(len(xs) - 1):
            if xs[i] < p < xs[i + 1]:
                nearer_left = (p - xs[i]) <= (xs[i + 1] - p)
                if nearer_left and not locked(xs[i]) and (p - xs[i]) < 0.20:
                    xs[i] = p
                elif (not nearer_left) and not locked(xs[i + 1]) and (xs[i + 1] - p) < 0.20:
                    xs[i + 1] = p
                else:
                    xs.insert(i + 1, p)
                break
    return xs


def build_x():
    """Pitch across the pair. Symmetry at the rib mid-planes x = 0 and 1.60."""
    half, _ = geometric(0.20, H1_CU, R_CU, 6)
    chan, _ = symmetric(0.40, H1_CH, R_CH)
    full = half + list(reversed(half))
    sizes = list(reversed(half)) + chan + full + chan + half
    return cum(0.0, sizes)


def build_y():
    # Both sides of every channel end wall are 2.5 um, so the global Y line
    # stays smooth inside each channel. Gallery planes are inserted afterwards.
    spans = [
        (Y_ODD_OUT, Y_ODD_WL, None, H1_CH),
        (Y_ODD_WL, Y_EVEN_WL, H1_CH, H1_CH),
        (Y_EVEN_WL, Y_ODD_WR, H1_CH, H1_CH),
        (Y_ODD_WR, Y_EVEN_WR, H1_CH, H1_CH),
        (Y_EVEN_WR, Y_EVEN_OUT, H1_CH, None),
    ]
    ys = [spans[0][0]]
    for a, b, hl, hr in spans:
        for h in fill_segment(b - a, hl, hr):
            ys.append(ys[-1] + h)
        ys[-1] = b
    return insert_planes(ys, [Y_EVEN_IN, Y_EVEN_GAL, Y0, Y1, Y_ODD_GAL, Y_ODD_IN])


def build_z():
    z_tim = cum(Z_TIM0, uniform(0.080, 4))
    floor, _ = both_ends(2.0, H1_CU, R_CU, 6)
    chan, _ = symmetric(1.20, H1_CH, R_CH)
    riser, _ = geometric(Z_GAL0 - Z_CH1, H1_CU, R_CU, 6)
    gal, _ = both_ends(Z_GAL1 - Z_GAL0, H1_CU, R_CU, 6)
    cap, _ = geometric(Z_TOP - Z_GAL1, 0.080, R_CU, 4)
    z = z_tim[:-1] + cum(0.0, floor)
    z = z[:-1] + cum(Z_CH0, chan)
    z = z[:-1] + cum(Z_CH1, riser)
    z = z[:-1] + cum(Z_GAL0, gal)
    z = z[:-1] + cum(Z_GAL1, cap)
    return z


def even_x(xc):
    return 0.20 < xc < 0.60


def odd_x(xc):
    return 1.00 < xc < 1.40


def even_pitch(xc):
    return 0.0 < xc < 0.80


def odd_pitch(xc):
    return 0.80 < xc < 1.60


def in_gallery_z(zc):
    return Z_GAL0 < zc < Z_GAL1


def in_riser_z(zc):
    return Z_CH1 < zc < Z_GAL0


def in_chan_z(zc):
    return Z_CH0 < zc < Z_CH1


def is_fluid(xc, yc, zc):
    if even_x(xc) and in_chan_z(zc) and Y_EVEN_WL < yc < Y_EVEN_WR:
        return True
    if even_x(xc) and in_riser_z(zc) and Y_EVEN_WL < yc < Y_EVEN_GAL:
        return True
    if even_pitch(xc) and in_gallery_z(zc) and Y_EVEN_IN < yc < Y_EVEN_GAL:
        return True
    if even_x(xc) and in_riser_z(zc) and Y_ODD_IN < yc < Y_EVEN_WR:
        return True
    if even_pitch(xc) and in_gallery_z(zc) and Y_ODD_IN < yc < Y_EVEN_OUT:
        return True
    if odd_x(xc) and in_chan_z(zc) and Y_ODD_WL < yc < Y_ODD_WR:
        return True
    if odd_x(xc) and in_riser_z(zc) and Y_ODD_WL < yc < Y_EVEN_IN:
        return True
    if odd_pitch(xc) and in_gallery_z(zc) and Y_ODD_OUT < yc < Y_EVEN_IN:
        return True
    if odd_x(xc) and in_riser_z(zc) and Y_ODD_GAL < yc < Y_ODD_WR:
        return True
    if odd_pitch(xc) and in_gallery_z(zc) and Y_ODD_GAL < yc < Y_ODD_IN:
        return True
    return False


def is_port_void(y0, y1, xc, zc):
    """Drop the copper cell outside each horizontal port so the face is a boundary."""
    if not in_gallery_z(zc):
        return False
    if abs(y1 - Y_EVEN_IN) < 1e-6 and even_pitch(xc):
        return True
    if abs(y0 - Y_ODD_IN) < 1e-6 and odd_pitch(xc):
        return True
    return False


def material(y0, y1, xc, z0, z1):
    yc = 0.5 * (y0 + y1)
    zc = 0.5 * (z0 + z1)
    if z1 <= 0.0 + 1e-9:
        if Y0 - 1e-9 <= y0 and y1 <= Y1 + 1e-9:
            return "tim"
        return None
    if is_port_void(y0, y1, xc, zc):
        return None
    if is_fluid(xc, yc, zc):
        return "fluid"
    return "cu"


def channel_side(xc):
    if xc < 0.80:
        return "even"
    if xc > 0.80:
        return "odd"
    return "mid"


def build_mesh(x, y, z):
    pending = {"fluid": [], "cu": [], "tim": []}
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    for i in range(nx):
        for j in range(ny):
            xc = 0.5 * (x[i] + x[i + 1])
            for k in range(nz):
                zone = material(y[j], y[j + 1], xc, z[k], z[k + 1])
                if zone:
                    pending[zone].append((i, j, k))
    counts = {name: len(pending[name]) for name in ("fluid", "cu", "tim")}
    counts["total"] = sum(counts.values())
    return pending, counts


def write_msh(path, x, y, z, pending):
    nodes = {}
    coords = []

    def nid(i, j, k):
        key = (i, j, k)
        got = nodes.get(key)
        if got is None:
            got = len(coords) + 1
            nodes[key] = got
            coords.append((x[i] * 1e-3, y[j] * 1e-3, z[k] * 1e-3))
        return got

    cell_of = {}
    centers = {}
    cid = 0
    zone_range = {}
    for zone in ("fluid", "cu", "tim"):
        a = cid + 1
        for i, j, k in pending[zone]:
            cid += 1
            cell_of[(i, j, k)] = (cid, zone)
            centers[cid] = (
                0.5 * (x[i] + x[i + 1]) * 1e-3,
                0.5 * (y[j] + y[j + 1]) * 1e-3,
                0.5 * (z[k] + z[k + 1]) * 1e-3,
            )
        zone_range[zone] = (a, cid)

    seen = {}
    interiors = []
    bounds = defaultdict(list)
    shorts = [0]

    def classify(nids, c0, z0, xc0, c1, z1, xc1):
        if z0 == "fluid" and z1 == "fluid" and channel_side(xc0) != channel_side(xc1):
            shorts[0] += 1
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

    def push(nids, cid_, zone, xc):
        key = tuple(sorted(nids))
        prev = seen.get(key)
        if prev is None:
            seen[key] = (nids, cid_, zone, xc)
        else:
            n0, c0, z0, xc0 = seen.pop(key)
            classify(n0, c0, z0, xc0, cid_, zone, xc)

    order = ("fluid", "cu", "tim")
    done = 0
    for zone in order:
        for i, j, k in pending[zone]:
            cid_, _ = cell_of[(i, j, k)]
            xc = 0.5 * (x[i] + x[i + 1])
            n000 = nid(i, j, k)
            n100 = nid(i + 1, j, k)
            n110 = nid(i + 1, j + 1, k)
            n010 = nid(i, j + 1, k)
            n001 = nid(i, j, k + 1)
            n101 = nid(i + 1, j, k + 1)
            n111 = nid(i + 1, j + 1, k + 1)
            n011 = nid(i, j + 1, k + 1)
            push((n000, n100, n110, n010), cid_, zone, xc)
            push((n001, n101, n111, n011), cid_, zone, xc)
            push((n000, n100, n101, n001), cid_, zone, xc)
            push((n010, n110, n111, n011), cid_, zone, xc)
            push((n000, n010, n011, n001), cid_, zone, xc)
            push((n100, n110, n111, n101), cid_, zone, xc)
            done += 1
            if done % 400000 == 0:
                print("faces", done, flush=True)

    def bound_name(nids, zone):
        pts = [coords[i - 1] for i in nids]
        xs = [p[0] * 1e3 for p in pts]
        ys = [p[1] * 1e3 for p in pts]
        zs = [p[2] * 1e3 for p in pts]
        xc = sum(xs) / 4.0
        yc = sum(ys) / 4.0
        zc = sum(zs) / 4.0
        xspan = max(xs) - min(xs)
        yspan = max(ys) - min(ys)
        zspan = max(zs) - min(zs)
        if xspan < 1e-6 and (abs(xc) < 1e-6 or abs(xc - 1.60) < 1e-6):
            return "sym"
        if zone == "fluid" and yspan < 1e-6 and in_gallery_z(zc):
            if abs(yc - Y_EVEN_IN) < 1e-4 and even_pitch(xc):
                return "inlet_even"
            if abs(yc - Y_ODD_IN) < 1e-4 and odd_pitch(xc):
                return "inlet_odd"
            if abs(yc - Y_EVEN_OUT) < 1e-4 and even_pitch(xc):
                return "outlet_even"
            if abs(yc - Y_ODD_OUT) < 1e-4 and odd_pitch(xc):
                return "outlet_odd"
        if zspan < 1e-6 and abs(zc - Z_TIM0) < 1e-6:
            return "wall_heat"
        return "wall_adi"

    for nids, c0, zone, _yc in seen.values():
        bounds[bound_name(nids, zone)].append((nids, c0, 0))

    def toward(nids, c0):
        p0 = coords[nids[0] - 1]
        p1 = coords[nids[1] - 1]
        p2 = coords[nids[2] - 1]
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
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

    names = (
        ("interior", 2),
        ("inlet_even", 10),
        ("inlet_odd", 10),
        ("outlet_even", 5),
        ("outlet_odd", 5),
        ("wall_heat", 3),
        ("wall_cu_fluid", 3),
        ("wall_tim_cu", 3),
        ("wall_adi", 3),
        ("wall_other", 3),
        ("sym", 7),
    )
    groups = []
    for name, bc in names:
        if name == "interior":
            groups.append((name, bc, interiors))
        elif bounds.get(name):
            groups.append((name, bc, bounds[name]))

    def hx(n):
        return format(int(n), "x")

    def quad_area(nids):
        p = [coords[i - 1] for i in nids]
        ux, uy, uz = p[1][0] - p[0][0], p[1][1] - p[0][1], p[1][2] - p[0][2]
        vx, vy, vz = p[3][0] - p[0][0], p[3][1] - p[0][1], p[3][2] - p[0][2]
        cx = uy * vz - uz * vy
        cy = uz * vx - ux * vz
        cz = ux * vy - uy * vx
        return math.sqrt(cx * cx + cy * cy + cz * cz)

    zone_ids = {}
    fid = 5
    for name, _, _ in groups:
        zone_ids[name] = fid
        fid += 1
    n_nodes = len(coords)
    n_cells = cid
    n_faces = sum(len(fs) for _, _, fs in groups)

    with open(path, "w", encoding="ascii", newline="\n") as f:
        w = f.write
        w('(0 "CP-GRACE-MC-01 CPU counterflow pair; channels along Y; msh in metres")\n')
        w("(2 3)\n")
        w("(10 (0 1 %s 0 3))\n" % hx(n_nodes))
        w("(12 (0 1 %s 0 0))\n" % hx(n_cells))
        w("(13 (0 1 %s 0 0))\n" % hx(n_faces))
        w("(10 (1 1 %s 1 3)\n(\n" % hx(n_nodes))
        for xx, yy, zz in coords:
            w("%.10e %.10e %.10e\n" % (xx, yy, zz))
        w(")\n)\n")
        w("(12 (2 %s %s 1 4))\n" % (hx(zone_range["fluid"][0]), hx(zone_range["fluid"][1])))
        w("(12 (3 %s %s 1 4))\n" % (hx(zone_range["cu"][0]), hx(zone_range["cu"][1])))
        w("(12 (4 %s %s 1 4))\n" % (hx(zone_range["tim"][0]), hx(zone_range["tim"][1])))
        fstart = 1
        for name, bc, fs in groups:
            fend = fstart + len(fs) - 1
            w("(13 (%s %s %s %s 4)\n(\n" % (hx(zone_ids[name]), hx(fstart), hx(fend), hx(bc)))
            for nids, c0, c1 in fs:
                w("%s %s %s %s %s %s\n" % (
                    hx(nids[0]), hx(nids[1]), hx(nids[2]), hx(nids[3]), hx(c0), hx(c1)
                ))
            w(")\n)\n")
            fstart = fend + 1
        w("(39 (2 fluid fluid)())\n")
        w("(39 (3 solid solid_cu)())\n")
        w("(39 (4 solid solid_tim2)())\n")
        kind = {2: "interior", 3: "wall", 5: "pressure-outlet", 7: "symmetry", 10: "mass-flow-inlet"}
        for name, bc, _ in groups:
            w("(39 (%d %s %s)())\n" % (zone_ids[name], kind[bc], name))

    areas = {}
    for name, _, fs in groups:
        if name.startswith("inlet") or name.startswith("outlet") or name == "wall_heat":
            areas[name] = sum(quad_area(n) for n, _, _ in fs)

    def ny_of(nids):
        p0 = coords[nids[0] - 1]
        p1 = coords[nids[1] - 1]
        p2 = coords[nids[2] - 1]
        ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
        vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
        return uz * vx - ux * vz

    normals = {}
    for name, _, fs in groups:
        if name.startswith("inlet") or name.startswith("outlet"):
            signs = [1 if ny_of(n) > 0.0 else -1 for n, _, _ in fs]
            normals[name] = signs[0] if signs and len(set(signs)) == 1 else 0
    return {
        "nodes": n_nodes,
        "faces": n_faces,
        "cells": n_cells,
        "zones": {name: len(fs) for name, _, fs in groups},
        "areas": areas,
        "normals": normals,
        "shorts": shorts[0],
    }


def write_info(path, x, y, z, counts, meta):
    mdot = (Q_CPU_LMIN / N_CH) / 1000.0 / 60.0 * RHO
    lines = [
        "CP-GRACE-MC-01 CPU counterflow pair",
        "even channel +Y (front to rear), odd channel -Y (rear to front)",
        "pitch pair 1.60 mm in X, 24 pairs are the 48-channel field",
        "local y=0 is plate Y=44, local y=32 is plate Y=76",
        "channel 0.40 x 1.20 mm, heated length 32 mm",
        "Y ends blocked; horizontal gallery then Z riser",
        "cells_total %d" % counts["total"],
        "cells_fluid %d" % counts["fluid"],
        "cells_cu %d" % counts["cu"],
        "cells_tim %d" % counts["tim"],
        "nx %d ny %d nz %d" % (len(x) - 1, len(y) - 1, len(z) - 1),
        "mdot_each_inlet_kg_s %.8e" % mdot,
        "q_flux_W_m2 %.6f" % Q_FLUX,
        "pair_power_W %.4f" % (Q_FLUX * 0.0016 * 0.032),
        "shorts %d" % meta["shorts"],
    ]
    for name, area in sorted(meta["areas"].items()):
        lines.append("area_%s_m2 %.8e" % (name, area))
    for name, n in sorted(meta["zones"].items()):
        lines.append("zone %s %d" % (name, n))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def write_replay(path):
    pts = [
        ("o0", 0.80, Y_ODD_OUT, Z_GAL0), ("o1", 0.80, Y_EVEN_IN, Z_GAL0),
        ("e0", 0.40, Y_EVEN_IN, Z_GAL0), ("e1", 0.40, Y_EVEN_GAL, Z_GAL0),
        ("c0", 0.40, Y_EVEN_WL, Z_CH0), ("c1", 0.40, Y_EVEN_WR, Z_CH0),
        ("d0", 1.20, Y_ODD_WL, Z_CH0), ("d1", 1.20, Y_ODD_WR, Z_CH0),
        ("r0", 1.20, Y_ODD_IN, Z_GAL0), ("r1", 0.40, Y_EVEN_OUT, Z_GAL0),
    ]
    lines = [
        "# Counterflow pair skeleton, millimetres.",
        "# Local y=0 is plate Y=44. Even channel +Y. Odd channel -Y.",
        "# Y-blocked ends, Z turn into the gallery.",
        "set OUTDIR {D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_grace_cpu}",
        "file mkdir [file join $OUTDIR icem]",
        'puts "GRACE counterflow replay start"',
        "catch { ic_geo_delete_all }",
        "foreach fam {FLUID SOLID_CU INLET OUTLET WALL_HEAT SYM GEOM} {",
        "    catch { ic_geo_new_family $fam }",
        "}",
    ]
    for name, px, py, pz in pts:
        lines.append("catch { ic_point {} POINT %s %.3f,%.3f,%.3f }" % (name, px, py, pz))
    lines += [
        "catch { ic_curve point CRV even_chan [list c0 c1] }",
        "catch { ic_curve point CRV odd_chan [list d0 d1] }",
        "catch { ic_save_tetin [file join $OUTDIR icem grace_cpu_counterflow.tin] }",
        'puts "GRACE counterflow replay done"',
        "",
    ]
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))


def main():
    x = build_x()
    y = build_y()
    z = build_z()
    gaps = [b - a for a, b in zip(y, y[1:])]
    ratio = max(max(gaps[i], gaps[i + 1]) / min(gaps[i], gaps[i + 1]) for i in range(len(gaps) - 1))
    print("grid", len(x) - 1, len(y) - 1, len(z) - 1, "y_ratio", round(ratio, 3), "y_min", min(gaps), flush=True)
    pending, counts = build_mesh(x, y, z)
    print("cells", counts, flush=True)
    if "--count" in sys.argv:
        return
    if counts["total"] > 3_200_000:
        raise SystemExit("cell count %s is too high to write" % counts["total"])
    msh = os.path.join(HERE, "grace_cpu_counterflow_pair.msh")
    print("writing", msh, flush=True)
    meta = write_msh(msh, x, y, z, pending)
    print("zones", meta["zones"], "shorts", meta["shorts"], flush=True)
    print("areas", meta["areas"], flush=True)
    if meta["shorts"]:
        raise SystemExit("even and odd fluid are connected")
    expect = 0.80e-3 * (Z_GAL1 - Z_GAL0) * 1e-3
    for name in ("inlet_even", "inlet_odd", "outlet_even", "outlet_odd"):
        area = meta["areas"].get(name, 0.0)
        if abs(area - expect) / expect > 1e-6:
            raise SystemExit("%s area %s expect %s" % (name, area, expect))
    heat = meta["areas"].get("wall_heat", 0.0)
    heat_expect = 0.032 * 0.0016
    if abs(heat - heat_expect) / heat_expect > 1e-6:
        raise SystemExit("heat area %s" % heat)
    expect_ny = {"inlet_even": 1, "inlet_odd": -1, "outlet_even": -1, "outlet_odd": 1}
    for name, sign in expect_ny.items():
        if meta["normals"].get(name) != sign:
            raise SystemExit("normal %s got %s" % (name, meta["normals"].get(name)))
    write_info(os.path.join(HERE, "grace_cpu_counterflow_info.txt"), x, y, z, counts, meta)
    write_replay(os.path.join(ROOT, "icem", "build_grace_cpu_counterflow.rpl"))
    print("info ok", flush=True)


if __name__ == "__main__":
    main()
