# -*- coding: utf-8 -*-
"""Measure first-cell sizes from the writer (same topology as msh). Not y+."""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from write_cht_circle_msh import (  # noqa: E402
    C_CORE,
    LEVELS,
    R,
    S_FR,
    XL,
    Z_CU_BOT,
    Z_IMP,
    Z_LID,
    Z_RIB,
    Z_TIM_BOT,
    build_xy,
    count_bl_layers,
    z_axis,
)


def first_at_circle(xy, tol=3e-4):
    ds = []
    for n0, n1, n2, n3 in xy.quads:
        pts = [xy.xy[n] for n in (n0, n1, n2, n3)]
        on = [abs(math.hypot(p[0], p[1]) - R) < tol for p in pts]
        if sum(on) < 2:
            continue
        for p, q in zip(pts, pts[1:] + pts[:1]):
            po = abs(math.hypot(p[0], p[1]) - R) < tol
            qo = abs(math.hypot(q[0], q[1]) - R) < tol
            if po != qo:
                a, b = (p, q) if po else (q, p)
                ds.append(math.hypot(a[0] - b[0], a[1] - b[1]))
    return (min(ds), max(ds), sum(ds) / len(ds), len(ds)) if ds else None


def wall_first_1d(coords, wall, inward_positive=True, band=0.08):
    xs = sorted(set(round(x, 10) for x in coords))
    near = [x for x in xs if abs(x - wall) < band]
    if len(near) < 2:
        return None
    near.sort(key=lambda x: abs(x - wall))
    d1 = abs(near[1] - near[0])
    # count clustered layers: steps < 3*d1 until jump
    layers = 1
    for a, b in zip(near, near[1:]):
        if abs(b - a) <= 3.0 * d1 * 1.25:
            layers += 1
        else:
            break
    return d1, layers, near[0]


def z_layers(z, a, b):
    zs = [x for x in z if a - 1e-9 <= x <= b + 1e-9]
    if len(zs) < 2:
        return 0, None, None
    dz = [zs[i + 1] - zs[i] for i in range(len(zs) - 1)]
    return len(zs) - 1, min(dz), max(dz)


def audit(name):
    lv = LEVELS[name]
    os.environ["UC01B_MESH"] = name
    xy = build_xy(lv)
    z = z_axis(lv)
    print("====", name, "quads", len(xy.quads), "nz", len(z) - 1)
    circ = first_at_circle(xy)
    print("  orifice_lip_radial_mm min/avg/max/n", circ)
    ys = sorted(set(round(p[1], 10) for p in xy.xy))
    xs = sorted(set(round(p[0], 10) for p in xy.xy))
    for w in (-1.00, -0.60, -0.20, 0.20, 0.60, 1.00):
        print("  slot_y", w, wall_first_1d(ys, w))
    if hasattr(xy, "ys"):
        for wall, sign, tag in ((-0.20, +1, "center-"), (0.20, -1, "center+")):
            nlay, d1 = count_bl_layers(xy.ys, wall, sign)
            print(f"  {tag} first_mm={d1} n_bl={nlay}  S_FR={S_FR}")
    for w in (XL, -XL):
        print("  slit_x", w, wall_first_1d(xs, w))
    print("  TIM layers", z_layers(z, Z_TIM_BOT, Z_CU_BOT))
    print("  Cu base layers", z_layers(z, Z_CU_BOT, Z_IMP))
    print("  fin/slot z layers", z_layers(z, Z_IMP, Z_RIB))
    print("  lid z layers", z_layers(z, Z_LID, Z_LID + 2.5))
    print("  first_imp", next((z[i + 1] - z[i] for i, a in enumerate(z[:-1]) if abs(a - Z_IMP) < 1e-12), None))
    print("  h_orif_target", lv["h_orif"], "first", lv["first"], "n_bl", lv["n_bl"])
    core = [p for p in xy.xy if abs(p[0]) < C_CORE and abs(p[1]) < C_CORE]
    if len(core) > 8:
        xs_c = sorted(set(round(p[0], 10) for p in core))
        dx = [xs_c[i + 1] - xs_c[i] for i in range(len(xs_c) - 1) if xs_c[i + 1] - xs_c[i] > 1e-9]
        print("  jet_core_dx_mm min/avg", min(dx), sum(dx) / len(dx))


if __name__ == "__main__":
    audit("medium")
    audit("fine")
