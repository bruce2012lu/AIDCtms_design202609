# -*- coding: utf-8 -*-
"""CP-GRACE-MC-01 LPDDR cooling-region structured hex mesh.

ICEM blocking parameters for one memory pitch, then the 6-channel window
if that pitch stays under 1e6 cells. Geometry is millimetres here; the
Fluent mesh is metres.

This is a Cartesian multiblock hex with the same edge bunching an ICEM
blocking would carry. It is not an ICEM GUI quality-signed export.
"""
from __future__ import annotations

import math
import os
import sys
from array import array

# --- frozen from CP-GRACE-MC-01 (report v1.0, 2026-09-26) ---
WIN_X0, WIN_Y0 = 14.0, 25.0          # plate mm, left LPDDR window
WIN_W, WIN_L = 50.0, 70.0             # candidate window
N_CH = 6
CH_W, CH_D = 1.20, 0.80               # width x depth
PITCH = WIN_W / N_CH                  # 8.333... mm, freeze of "约 8 mm"
FLOOR_T = 2.0                         # z 0–2 copper under the grooves
CAP_T = 0.40                          # z 2.8–3.2 roof; CPU layer is 1.20, memory is 0.80
Z_FLOOR = 2.0
Z_CAP = 2.8                           # Z_FLOOR + CH_D
Z_TOP = 3.2                           # parting plane
CAP_T = Z_TOP - Z_CAP

# Water 40 C, report §5. Copper C11000 / TU1.
RHO, MU, K_W = 992.0, 6.53e-4, 0.632
K_CU = 385.0
V_TABLE = 0.11                        # m/s, table rounding
Q_SIDE_LMIN = 0.036
Q_ENV_OVER_DESIGN = 0.70 / 0.55

# Fluid-solid coupling gates. Wall-normal only.
H1 = 0.012                            # mm, 12 um
R_FLUID = 1.20
R_SOLID = 1.25
N_HALF_MIN = 10
HMAX_LAND = 0.45                      # mm, keeps copper cells from going flat
Y_OUT = 0.20                          # mm, first cell at outlet
Y_IN = 0.080                          # mm, first cell at inlet
R_STREAM = 1.10
HMAX_Y = 0.40
SHEAR_FACTOR = 1.50                   # laminar rectangle, max/mean tau estimate
CELL_CAP = 1_000_000

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MESH = os.path.join(ROOT, "mesh")
ICEM = os.path.join(ROOT, "icem")


def fanning_re(alpha: float) -> float:
    """Shah & London rectangular duct, f = Fanning, alpha = short/long."""
    a = alpha
    poly = (
        1.0
        - 1.3553 * a
        + 1.9467 * a * a
        - 1.7012 * a ** 3
        + 0.9564 * a ** 4
        - 0.2537 * a ** 5
    )
    return 24.0 * poly


def solve_ratio(length: float, h1: float, n: int) -> float:
    """h1 * (r**n - 1) / (r - 1) = length, r >= 1."""
    if n < 1:
        raise ValueError("n")
    target = length
    if abs(n * h1 - target) <= 1e-9 * target:
        return 1.0
    if n * h1 > target * (1.0 + 1e-9):
        raise ValueError(f"h1={h1} * n={n} exceeds {target}")

    def sm(r: float) -> float:
        return h1 * (r ** n - 1.0) / (r - 1.0)

    lo, hi = 1.0000001, 1.5
    guard = 0
    while sm(hi) < target:
        hi *= 2.0
        guard += 1
        if guard > 30:
            raise ValueError("ratio did not bracket")
    for _ in range(70):
        mid = 0.5 * (lo + hi)
        if sm(mid) < target:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def geom_sizes(length: float, h1: float, n: int, ratio: float) -> list[float]:
    sizes = []
    h = h1
    for i in range(n):
        sizes.append(h if i < n - 1 else h)
        h *= ratio
    sizes[-1] += length - sum(sizes)
    return sizes


def both_walls(length: float, h1: float, r_max: float, n_half_min: int) -> tuple[list[float], float]:
    """Cluster both ends. Returns sizes and the ratio actually used."""
    half = 0.5 * length
    n = n_half_min
    ratio = solve_ratio(half, h1, n)
    while ratio > r_max + 1e-6:
        n += 1
        if n > 40:
            raise ValueError("cannot keep fluid growth under the gate")
        ratio = solve_ratio(half, h1, n)
    left = geom_sizes(half, h1, n, ratio)
    return left + list(reversed(left)), ratio


def one_sided(length: float, h1: float, r_max: float) -> tuple[list[float], float]:
    """Geometric from the wall. First cell is h1. Fewest cells with ratio <= r_max."""
    h = h1
    acc = 0.0
    n = 0
    while acc < length - 1e-9:
        acc += h
        h *= r_max
        n += 1
        if n > 100:
            raise ValueError(f"no one-sided distribution for L={length}")
    ratio = solve_ratio(length, h1, n)
    if ratio > r_max + 1e-5:
        raise ValueError(f"ratio {ratio} exceeds {r_max}")
    return geom_sizes(length, h1, n, ratio), ratio


def sided_then_uniform(length: float, h1: float, ratio: float, hmax: float) -> list[float]:
    """Wall-clustered sizes, then a uniform run that does not break `ratio`."""
    geo = _grow_capped(h1, ratio, hmax, length)
    rem = length - sum(geo)
    if rem < -1e-6:
        raise ValueError("capped growth overshot")
    if rem <= 1e-8:
        geo[-1] += rem
        return geo
    for _ in range(4):
        prev = geo[-1]
        s_hi = min(hmax, prev * ratio)
        s_lo = prev / ratio
        n = max(1, math.ceil(rem / s_hi - 1e-9))
        s = rem / n
        if s_lo - 1e-6 <= s <= s_hi + 1e-6:
            geo.extend([s] * n)
            geo[-1] += length - sum(geo)
            return geo
        if len(geo) < 2:
            break
        rem += geo.pop()
    raise ValueError(f"could not fill {length} at ratio {ratio}")


def _grow_capped(h1: float, ratio: float, hmax: float, limit: float) -> list[float]:
    sizes = []
    h = h1
    used = 0.0
    while h <= hmax + 1e-9 and used + h <= limit + 1e-9:
        sizes.append(h)
        used += h
        h *= ratio
    if not sizes:
        raise ValueError("empty capped growth")
    return sizes


def two_ends(length: float, h_a: float, h_b: float, ratio: float, hmax: float) -> list[float]:
    """h_a is the cell at the start, h_b the cell at the end. Core is uniform."""
    left = _grow_capped(h_a, ratio, hmax, length * 0.45)
    right = _grow_capped(h_b, ratio, hmax, length * 0.45)
    for _ in range(4):
        rem = length - (sum(left) + sum(right))
        prev = max(left[-1], right[-1])
        s_lo = prev / ratio
        n = max(1, math.ceil(rem / hmax - 1e-9))
        s = rem / n
        if s + 1e-8 >= s_lo and s <= hmax + 1e-8:
            if s <= left[-1] * ratio + 1e-6 and s <= right[-1] * ratio + 1e-6:
                sizes = left + [s] * n + list(reversed(right))
                err = length - sum(sizes)
                if abs(err) > 1e-6:
                    raise ValueError(f"streamwise sum error {err}")
                # absorb roundoff into the first core cell
                sizes[len(left)] += err
                return sizes
        # Pull the larger end's last cell back into the core and try again.
        if left[-1] >= right[-1] and len(left) > 1:
            left.pop()
        elif len(right) > 1:
            right.pop()
        else:
            break
    raise ValueError("streamwise bunching could not keep the growth ratio")


def cum(sizes: list[float], origin: float = 0.0) -> list[float]:
    xs = [origin]
    acc = origin
    for h in sizes:
        acc += h
        xs.append(acc)
    xs[-1] = origin + sum(sizes)  # exact end
    # rebuild end exactly from the intended length of the caller: keep nodes consistent
    return xs


def max_growth(sizes: list[float]) -> float:
    g = 1.0
    for a, b in zip(sizes, sizes[1:]):
        if a <= 0 or b <= 0:
            continue
        g = max(g, b / a, a / b)
    return g


def assert_close(name: str, got: float, want: float, tol: float = 1e-6) -> None:
    if abs(got - want) > tol:
        raise SystemExit(f"{name}: {got} != {want}")


def build_axes(n_ch: int) -> dict:
    half_land = 0.5 * (PITCH - CH_W)
    land = sided_then_uniform(half_land, H1, R_SOLID, HMAX_LAND)
    r_land = max_growth(land)
    chan, r_x = both_walls(CH_W, H1, R_FLUID, N_HALF_MIN)
    if abs(land[0] - H1) > 1e-6:
        raise SystemExit("land first cell lost the wall spacing")
    x_sizes: list[float] = []
    x_fluid: list[bool] = []
    for _ in range(n_ch):
        left = list(reversed(land))
        x_sizes.extend(left)
        x_fluid.extend([False] * len(left))
        x_sizes.extend(chan)
        x_fluid.extend([True] * len(chan))
        x_sizes.extend(land)
        x_fluid.extend([False] * len(land))
    y_sizes = two_ends(WIN_L, Y_OUT, Y_IN, R_STREAM, HMAX_Y)
    floor, r_floor = one_sided(FLOOR_T, H1, R_SOLID)
    chan_z, r_z = both_walls(CH_D, H1, R_FLUID, N_HALF_MIN)
    cap, r_cap = one_sided(CAP_T, H1, R_FLUID)
    z_sizes = list(reversed(floor)) + chan_z + cap
    k0 = len(floor)
    k1 = k0 + len(chan_z)
    x = cum(x_sizes, 0.0)
    y = cum(y_sizes, 0.0)
    z = cum(z_sizes, 0.0)
    x[-1] = n_ch * PITCH
    y[-1] = WIN_L
    z[-1] = Z_TOP
    # interface stations
    z[k0] = Z_FLOOR
    z[k1] = Z_CAP
    return {
        "x": x,
        "y": y,
        "z": z,
        "x_fluid": x_fluid,
        "x_sizes": x_sizes,
        "y_sizes": y_sizes,
        "z_sizes": z_sizes,
        "k0": k0,
        "k1": k1,
        "land": land,
        "chan": chan,
        "floor": floor,
        "chan_z": chan_z,
        "cap": cap,
        "r_x": r_x,
        "r_z": r_z,
        "r_land": r_land,
        "r_floor": r_floor,
        "r_cap": r_cap,
        "n_ch": n_ch,
        "half_land": half_land,
    }


def yplus_table() -> dict:
    alpha = min(CH_W, CH_D) / max(CH_W, CH_D)
    fre = fanning_re(alpha)          # Fanning
    fre_d = 4.0 * fre                 # Darcy
    nu = MU / RHO
    dh = 2.0 * (CH_W * CH_D) / (CH_W + CH_D) * 1e-3
    area = (CH_W * CH_D) * 1e-6
    q_side = Q_SIDE_LMIN * 1e-3 / 60.0
    v_split = (q_side / N_CH) / area
    out = {}
    for name, v in (
        ("split", v_split),
        ("table", V_TABLE),
        ("envelope", V_TABLE * Q_ENV_OVER_DESIGN),
    ):
        re = RHO * v * dh / MU
        fd = fre_d / re
        ut = v * math.sqrt(fd / 8.0)
        y1 = nu / ut
        out[name] = {
            "V": v,
            "Re": re,
            "y1_m": y1,
            "yplus_h1": (H1 * 1e-3) / y1,
            "yplus_max_est": SHEAR_FACTOR * (H1 * 1e-3) / y1,
        }
    out["alpha"] = alpha
    out["fRe_fanning"] = fre
    out["fRe_darcy"] = fre_d
    out["Dh_mm"] = dh * 1e3
    out["mdot_channel"] = (q_side / N_CH) * RHO
    out["mdot_side"] = q_side * RHO
    out["qflux"] = 20.0 / (0.050 * 0.070)
    return out


def quality(ax: dict) -> dict:
    xf = ax["x_fluid"]
    k0, k1 = ax["k0"], ax["k1"]
    dx, dy, dz = ax["x_sizes"], ax["y_sizes"], ax["z_sizes"]
    g_x = max_growth(dx)
    g_y = max_growth(dy)
    g_z = max_growth(dz)
    # fluid-only wall-normal growth: channel x sizes, and z inside the channel band
    ch = ax["chan"]
    g_fluid_x = max_growth(ch)
    g_fluid_z = max_growth(ax["chan_z"])
    ar_f = 1.0
    ar_s = 1.0
    min_edge = min(dx + dy + dz)
    n_fluid = 0
    n_solid = 0
    for i, is_f in enumerate(xf):
        for j in range(len(dy)):
            for k in range(len(dz)):
                fluid = is_f and k0 <= k < k1
                edges = (dx[i], dy[j], dz[k])
                ar = max(edges) / min(edges)
                if fluid:
                    n_fluid += 1
                    ar_f = max(ar_f, ar)
                else:
                    n_solid += 1
                    ar_s = max(ar_s, ar)
    return {
        "g_x": g_x,
        "g_y": g_y,
        "g_z": g_z,
        "g_fluid_x": g_fluid_x,
        "g_fluid_z": g_fluid_z,
        "aspect": max(ar_f, ar_s),
        "aspect_fluid": ar_f,
        "aspect_solid": ar_s,
        "min_edge_mm": min_edge,
        "n_fluid": n_fluid,
        "n_solid": n_solid,
        "n_cells": n_fluid + n_solid,
        "nx": len(dx),
        "ny": len(dy),
        "nz": len(dz),
        "first_x_fluid_mm": ch[0],
        "first_z_fluid_mm": ax["chan_z"][0],
        "first_y_inlet_mm": dy[-1],
        "first_y_outlet_mm": dy[0],
        "first_land_mm": ax["land"][0],
        "first_floor_mm": ax["floor"][0],
        "first_cap_mm": ax["cap"][0],
    }


def report_text(single: dict, q1: dict, yp: dict, qn: dict | None) -> str:
    lines = []
    w = lines.append
    w("CP-GRACE-MC-01 LPDDR cooling region — ICEM blocking budget")
    w(f"pitch_mm {PITCH:.6f}  channels {N_CH}  window {WIN_W} x {WIN_L} mm")
    w(f"channel_mm {CH_W} x {CH_D} x {WIN_L}  floor {FLOOR_T}  cap {CAP_T}")
    w(f"z 0 / {Z_FLOOR} / {Z_CAP} / {Z_TOP}")
    w(f"Dh_mm {yp['Dh_mm']:.4f}  fRe_Fanning {yp['fRe_fanning']:.3f}  fRe_Darcy {yp['fRe_darcy']:.3f}")
    w(f"qflux_W_m2 {yp['qflux']:.4f}")
    w(f"mdot_channel_kg_s {yp['mdot_channel']:.6e}  mdot_side_kg_s {yp['mdot_side']:.6e}")
    for name in ("split", "table", "envelope"):
        d = yp[name]
        w(
            f"yplus {name} V {d['V']:.4f} Re {d['Re']:.2f} "
            f"y1_um {d['y1_m']*1e6:.2f} y+_h1 {d['yplus_h1']:.3f} "
            f"y+_max_est {d['yplus_max_est']:.3f}"
        )
    w(
        f"SINGLE cells {q1['n_cells']} fluid {q1['n_fluid']} solid {q1['n_solid']} "
        f"nx {q1['nx']} ny {q1['ny']} nz {q1['nz']}"
    )
    w(
        f"SINGLE growth fluid_x {q1['g_fluid_x']:.4f} fluid_z {q1['g_fluid_z']:.4f} "
        f"all_x {q1['g_x']:.4f} y {q1['g_y']:.4f} z {q1['g_z']:.4f} "
        f"aspect_fluid {q1['aspect_fluid']:.2f} aspect_solid {q1['aspect_solid']:.2f} "
        f"min_edge_um {q1['min_edge_mm']*1000:.2f}"
    )
    w(
        f"SINGLE first_um fluid_x {q1['first_x_fluid_mm']*1000:.2f} "
        f"fluid_z {q1['first_z_fluid_mm']*1000:.2f} "
        f"land {q1['first_land_mm']*1000:.2f} floor {q1['first_floor_mm']*1000:.2f} "
        f"cap {q1['first_cap_mm']*1000:.2f} "
        f"y_in {q1['first_y_inlet_mm']*1000:.2f} y_out {q1['first_y_outlet_mm']*1000:.2f}"
    )
    w(f"ratio_x {single['r_x']:.4f} ratio_z {single['r_z']:.4f}")
    w(f"land_cells_half {len(single['land'])} chan_x {len(single['chan'])} "
      f"floor {len(single['floor'])} chan_z {len(single['chan_z'])} cap {len(single['cap'])}")
    if qn:
        w(
            f"ARRAY cells {qn['n_cells']} fluid {qn['n_fluid']} solid {qn['n_solid']} "
            f"nx {qn['nx']} ny {qn['ny']} nz {qn['nz']} "
            f"aspect_fluid {qn['aspect_fluid']:.2f} aspect_solid {qn['aspect_solid']:.2f}"
        )
    w("gates: fluid wall-normal growth <= 1.20, first layer 12 um, y+_max_est(envelope) < 1,")
    w("      >= 10 cells wall-to-center, conformal hex, single pitch < 1e6")
    return "\n".join(lines) + "\n"


def gates_ok(q1: dict, yp: dict) -> list[str]:
    bad = []
    if q1["n_cells"] >= CELL_CAP:
        bad.append(f"single channel cells {q1['n_cells']} >= {CELL_CAP}")
    if q1["g_fluid_x"] > R_FLUID + 0.02:
        bad.append(f"fluid x growth {q1['g_fluid_x']:.3f}")
    if q1["g_fluid_z"] > R_FLUID + 0.02:
        bad.append(f"fluid z growth {q1['g_fluid_z']:.3f}")
    if q1["g_y"] > R_STREAM + 0.02:
        bad.append(f"streamwise growth {q1['g_y']:.3f}")
    if q1["g_x"] > R_SOLID + 0.02 or q1["g_z"] > R_SOLID + 0.02:
        bad.append(f"solid growth x {q1['g_x']:.3f} z {q1['g_z']:.3f}")
    if abs(q1["first_x_fluid_mm"] - H1) > 1e-6 or abs(q1["first_z_fluid_mm"] - H1) > 1e-6:
        bad.append("fluid first layer is not 12 um")
    if yp["envelope"]["yplus_max_est"] >= 1.0:
        bad.append(f"envelope y+ estimate {yp['envelope']['yplus_max_est']:.3f}")
    if len(q1) and q1["aspect"] > 80:
        bad.append(f"aspect {q1['aspect']:.1f}")
    half_x = len([1 for _ in range(len(build_axes(1)["chan"]) // 2)])
    if half_x < N_HALF_MIN:
        bad.append("fewer than 10 cells from wall to centerline")
    return bad


def write_rpl(path: str, ax: dict, title: str) -> None:
    """Geometry-only ICEM replay. Volume mesh is the Fluent hex from this file."""
    x, y, z = ax["x"], ax["y"], ax["z"]
    k0, k1 = ax["k0"], ax["k1"]
    # one fluid brick: first channel
    i_fluid = [i for i, f in enumerate(ax["x_fluid"]) if f]
    i0, i1 = i_fluid[0], i_fluid[-1] + 1
    fx0, fx1 = x[i0], x[i1]
    lines = [
        f"# {title}",
        "# Units: millimetres. Replay builds the tin. It does not claim a meshed blocking.",
        "# Edge bunching that the Fluent hex already uses is listed at the bottom.",
        f"# Plate map, left window: X = {WIN_X0} + x, Y = {WIN_Y0} + y, z = z.",
        "# Inlet is y = 70 (plate Y = 95). Outlet is y = 0 (plate Y = 25).",
        f"set OUTDIR {{{ROOT.replace(chr(92), '/')}}}",
        "set ICEMDIR [file join $OUTDIR icem]",
        "file mkdir $ICEMDIR",
        f"puts \"{title}: start\"",
        "catch { ic_uns_new }",
        "catch { ic_geo_delete_all }",
        "catch { ic_hex_unload_blocking }",
        "foreach fam {FLUID SOLID INLET OUTLET WALL_HEAT WALL_CAP WALL_END WALL_SIDE SYM WALL_CU_FLUID} {",
        "    catch { ic_geo_new_family $fam }",
        "}",
    ]

    def pt(name: str, px, py, pz) -> None:
        lines.append(f"catch {{ ic_point {{}} POINT {name} {px:.6f},{py:.6f},{pz:.6f} }}")

    def box(prefix: str, xa, xb, ya, yb, za, zb, fam_faces: dict) -> None:
        names = {
            "000": (xa, ya, za), "100": (xb, ya, za), "110": (xb, yb, za), "010": (xa, yb, za),
            "001": (xa, ya, zb), "101": (xb, ya, zb), "111": (xb, yb, zb), "011": (xa, yb, zb),
        }
        for sfx, coords in names.items():
            pt(prefix + sfx, *coords)
        curves = [
            ("c1", "000", "100"), ("c2", "100", "110"), ("c3", "110", "010"), ("c4", "010", "000"),
            ("c5", "001", "101"), ("c6", "101", "111"), ("c7", "111", "011"), ("c8", "011", "001"),
            ("c9", "000", "001"), ("c10", "100", "101"), ("c11", "110", "111"), ("c12", "010", "011"),
        ]
        for cn, a, b in curves:
            lines.append(
                f"catch {{ ic_curve point CRV {prefix}{cn} [list {prefix}{a} {prefix}{b}] }}"
            )
        surfs = [
            ("sbot", "c1", "c2", "c3", "c4", fam_faces["bot"]),
            ("stop", "c5", "c6", "c7", "c8", fam_faces["top"]),
            ("sx0", "c4", "c12", "c8", "c9", fam_faces["x0"]),
            ("sx1", "c2", "c10", "c6", "c11", fam_faces["x1"]),
            ("sy0", "c1", "c10", "c5", "c9", fam_faces["y0"]),
            ("sy1", "c3", "c11", "c7", "c12", fam_faces["y1"]),
        ]
        for sn, a, b, c, d, fam in surfs:
            lines.append(
                f"catch {{ ic_surface 4-pt SRFS {prefix}{sn} "
                f"[list {prefix}{a} {prefix}{b} {prefix}{c} {prefix}{d}] }}"
            )
            lines.append(f"catch {{ ic_geo_set_part surface {prefix}{sn} {fam} 0 }}")

    side = "SYM" if ax["n_ch"] == 1 else "WALL_SIDE"
    box(
        "o",
        x[0], x[-1], y[0], y[-1], z[0], z[-1],
        {"bot": "WALL_HEAT", "top": "WALL_CAP", "x0": side, "x1": side, "y0": "WALL_END", "y1": "WALL_END"},
    )
    box(
        "f",
        fx0, fx1, y[0], y[-1], z[k0], z[k1],
        {
            "bot": "WALL_CU_FLUID", "top": "WALL_CU_FLUID",
            "x0": "WALL_CU_FLUID", "x1": "WALL_CU_FLUID",
            "y0": "OUTLET", "y1": "INLET",
        },
    )
    cx = 0.5 * (fx0 + fx1)
    cy = 0.5 * (y[0] + y[-1])
    lines.append(f"catch {{ ic_point {{}} POINT p_fluid {cx:.6f},{cy:.6f},{(z[k0]+z[k1])*0.5:.6f} }}")
    lines.append("catch { ic_geo_set_part point p_fluid FLUID 0 }")
    lines.append(f"catch {{ ic_point {{}} POINT p_solid {cx:.6f},{cy:.6f},{Z_FLOOR*0.5:.6f} }}")
    lines.append("catch { ic_geo_set_part point p_solid SOLID 0 }")
    tin = "lpddr_channel.tin" if ax["n_ch"] == 1 else "lpddr_array.tin"
    lines.append(f"catch {{ ic_save_tetin [file join $ICEMDIR {tin}] }}")
    lines.append(f"puts \"saved [file join $ICEMDIR {tin}]\"")
    lines.append("# --- edge params the hex writer already applied (mm) ---")
    lines.append(f"# fluid width {CH_W}: nodes {len(ax['chan'])+1}, spacing1 {H1}, ratio1 {ax['r_x']:.4f}, spacing2 {H1}, ratio2 {ax['r_x']:.4f}")
    lines.append(f"# fluid depth {CH_D}: nodes {len(ax['chan_z'])+1}, spacing1 {H1}, ratio1 {ax['r_z']:.4f}, spacing2 {H1}, ratio2 {ax['r_z']:.4f}")
    lines.append(f"# half land {ax['half_land']:.4f}: nodes {len(ax['land'])+1}, wall spacing {H1}, ratio {ax['r_land']:.4f}")
    lines.append(f"# floor {FLOOR_T}: nodes {len(ax['floor'])+1}, wall spacing {H1} at z=2, ratio {ax['r_floor']:.4f}")
    lines.append(f"# cap {CAP_T:.2f}: nodes {len(ax['cap'])+1}, wall spacing {H1} at z=2.8, ratio {ax['r_cap']:.4f}")
    lines.append(f"# streamwise {WIN_L}: nodes {len(ax['y_sizes'])+1}, outlet spacing {Y_OUT}, inlet spacing {Y_IN}, ratio {R_STREAM}, max {HMAX_Y}")
    lines.append(f"puts \"{title}: geometry done\"")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")


def write_msh(path: str, ax: dict, comment: str) -> None:
    x, y, z = ax["x"], ax["y"], ax["z"]
    xf = ax["x_fluid"]
    k0, k1 = ax["k0"], ax["k1"]
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1
    nxy = nx * ny
    ncell = nx * ny * nz
    fluid_flag = array("B", bytes(ncell))
    for i, is_f in enumerate(xf):
        if not is_f:
            continue
        for j in range(ny):
            base = i + nx * j
            for k in range(k0, k1):
                fluid_flag[base + nxy * k] = 1
    n_fluid = sum(fluid_flag)
    n_solid = ncell - n_fluid
    cell_id = array("I", bytes(4 * ncell))
    fid = 0
    sid = n_fluid
    for idx in range(ncell):
        if fluid_flag[idx]:
            fid += 1
            cell_id[idx] = fid
        else:
            sid += 1
            cell_id[idx] = sid

    def cid(i: int, j: int, k: int) -> int:
        if i < 0 or j < 0 or k < 0 or i >= nx or j >= ny or k >= nz:
            return 0
        return cell_id[i + nx * j + nxy * k]

    def is_fluid_cell(i: int, j: int, k: int) -> bool:
        if i < 0 or j < 0 or k < 0 or i >= nx or j >= ny or k >= nz:
            return False
        return bool(fluid_flag[i + nx * j + nxy * k])

    side_name = "sym" if ax["n_ch"] == 1 else "wall_side"
    # count faces
    counts = {
        "interior": 0,
        "wall_cu_fluid": 0,
        "inlet": 0,
        "outlet": 0,
        "wall_heat": 0,
        "wall_cap": 0,
        "wall_end": 0,
        side_name: 0,
    }

    def add_count(name: str) -> None:
        counts[name] += 1

    def classify_pair(c0: int, c1: int, i0, j0, k0_, i1, j1, k1_) -> str:
        f0 = is_fluid_cell(i0, j0, k0_)
        f1 = is_fluid_cell(i1, j1, k1_)
        if f0 == f1:
            return "interior"
        return "wall_cu_fluid"

    for i in range(nx + 1):
        for j in range(ny):
            for k in range(nz):
                if 0 < i < nx:
                    add_count(classify_pair(1, 1, i - 1, j, k, i, j, k))
                else:
                    add_count(side_name)
    for j in range(ny + 1):
        for i in range(nx):
            for k in range(nz):
                if 0 < j < ny:
                    add_count("interior")
                elif j == 0:
                    add_count("outlet" if is_fluid_cell(i, 0, k) else "wall_end")
                else:
                    add_count("inlet" if is_fluid_cell(i, ny - 1, k) else "wall_end")
    for k in range(nz + 1):
        for i in range(nx):
            for j in range(ny):
                if 0 < k < nz:
                    add_count(classify_pair(1, 1, i, j, k - 1, i, j, k))
                elif k == 0:
                    add_count("wall_heat")
                else:
                    add_count("wall_cap")

    order = [
        "interior", "wall_cu_fluid", "inlet", "outlet",
        "wall_heat", "wall_cap", "wall_end", side_name,
    ]
    bc_code = {
        "interior": 2,
        "wall_cu_fluid": 3,
        "inlet": 20,
        "outlet": 5,
        "wall_heat": 3,
        "wall_cap": 3,
        "wall_end": 3,
        "wall_side": 3,
        "sym": 7,
    }
    kind_map = {
        2: "interior",
        3: "wall",
        5: "pressure-outlet",
        7: "symmetry",
        20: "mass-flow-inlet",
    }
    n_faces = sum(counts[n] for n in order)
    nx1, ny1, nz1 = nx + 1, ny + 1, nz + 1
    n_nodes = nx1 * ny1 * nz1

    def nid(i: int, j: int, k: int) -> int:
        return 1 + i + nx1 * (j + ny1 * k)

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="ascii", newline="\n", buffering=1024 * 1024) as f:
        f.write(f'(0 "{comment}")\n')
        f.write("(2 3)\n")
        f.write(f"(10 (0 1 {n_nodes} 0 3))\n")
        f.write(f"(12 (0 1 {ncell} 0 0))\n")
        f.write(f"(13 (0 1 {n_faces} 0 0))\n")
        f.write(f"(10 (1 1 {n_nodes} 1 3)\n(\n")
        for k in range(nz1):
            zk = z[k] * 1e-3
            for j in range(ny1):
                yj = y[j] * 1e-3
                for i in range(nx1):
                    f.write(f"{x[i]*1e-3:.8e} {yj:.8e} {zk:.8e}\n")
        f.write(")\n)\n")
        f.write(f"(12 (2 1 {n_fluid} 1 4))\n")
        f.write(f"(12 (3 {n_fluid+1} {ncell} 1 4))\n")

        # zone ids: 2 fluid, 3 solid, faces from 4
        zid = {}
        nxt = 4
        for name in order:
            zid[name] = nxt
            nxt += 1
        # We need per-zone start/end. Write each zone fully.
        # Second conceptual pass is inlined per zone to keep RAM flat.
        # Precompute ranges
        start = 1
        ranges = {}
        for name in order:
            ranges[name] = (start, start + counts[name] - 1, zid[name])
            start += counts[name]

        tmp_dir = path + ".zones"
        if os.path.isdir(tmp_dir):
            for old in os.listdir(tmp_dir):
                os.remove(os.path.join(tmp_dir, old))
            os.rmdir(tmp_dir)
        os.makedirs(tmp_dir)
        handles = {}
        written = {name: 0 for name in order}
        for name in order:
            handles[name] = open(
                os.path.join(tmp_dir, name + ".txt"),
                "w", encoding="ascii", newline="\n", buffering=1024 * 1024,
            )

        def emit(name, nids, c0, c1):
            written[name] += 1
            handles[name].write(f"{nids[0]} {nids[1]} {nids[2]} {nids[3]} {c0} {c1}\n")

        for i in range(nx + 1):
            for j in range(ny):
                for k in range(nz):
                    nids = (nid(i, j, k), nid(i, j + 1, k), nid(i, j + 1, k + 1), nid(i, j, k + 1))
                    if 0 < i < nx:
                        cL, cR = cid(i - 1, j, k), cid(i, j, k)
                        name = classify_pair(cL, cR, i - 1, j, k, i, j, k)
                        emit(name, nids, cL, cR)
                    elif i == 0:
                        emit(side_name, tuple(reversed(nids)), cid(0, j, k), 0)
                    else:
                        emit(side_name, nids, cid(nx - 1, j, k), 0)
        # +y normal: (i,j,k) (i,j,k+1) (i+1,j,k+1) (i+1,j,k)
        for j in range(ny + 1):
            for i in range(nx):
                for k in range(nz):
                    nids = (nid(i, j, k), nid(i, j, k + 1), nid(i + 1, j, k + 1), nid(i + 1, j, k))
                    if 0 < j < ny:
                        emit("interior", nids, cid(i, j - 1, k), cid(i, j, k))
                    elif j == 0:
                        owner = cid(i, 0, k)
                        name = "outlet" if is_fluid_cell(i, 0, k) else "wall_end"
                        emit(name, tuple(reversed(nids)), owner, 0)
                    else:
                        owner = cid(i, ny - 1, k)
                        name = "inlet" if is_fluid_cell(i, ny - 1, k) else "wall_end"
                        emit(name, nids, owner, 0)
        # +z normal
        for k in range(nz + 1):
            for i in range(nx):
                for j in range(ny):
                    nids = (nid(i, j, k), nid(i + 1, j, k), nid(i + 1, j + 1, k), nid(i, j + 1, k))
                    if 0 < k < nz:
                        cD, cU = cid(i, j, k - 1), cid(i, j, k)
                        name = classify_pair(cD, cU, i, j, k - 1, i, j, k)
                        emit(name, nids, cD, cU)
                    elif k == 0:
                        emit("wall_heat", tuple(reversed(nids)), cid(i, j, 0), 0)
                    else:
                        emit("wall_cap", nids, cid(i, j, nz - 1), 0)

        for h in handles.values():
            h.close()
        for name in order:
            if written[name] != counts[name]:
                raise SystemExit(f"{name} wrote {written[name]} faces, counted {counts[name]}")

        for name in order:
            a, b, zone = ranges[name]
            f.write(f"(13 ({zone} {a} {b} {bc_code[name]} 4)\n(\n")
            src = os.path.join(tmp_dir, name + ".txt")
            with open(src, "r", encoding="ascii", newline="\n") as srcf:
                while True:
                    chunk = srcf.read(8 * 1024 * 1024)
                    if not chunk:
                        break
                    f.write(chunk)
            f.write(")\n)\n")
            os.remove(src)
        os.rmdir(tmp_dir)

        f.write("(45 (2 fluid fluid)())\n")
        f.write("(45 (3 solid solid_cu)())\n")
        for name in order:
            f.write(f"(45 ({zid[name]} {kind_map[bc_code[name]]} {name})())\n")

    info = os.path.splitext(path)[0] + "_info.txt"
    with open(info, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"file {path}\n")
        f.write(f"cells {ncell}\nfluid {n_fluid}\nsolid {n_solid}\n")
        f.write(f"nodes {n_nodes}\nfaces {n_faces}\n")
        f.write(f"nx {nx} ny {ny} nz {nz}\n")
        for name in order:
            f.write(f"zone {name} {counts[name]}\n")
        f.write("units metres\n")
        f.write("hex axis-aligned; orthogonal quality 1; not ICEM-GUI signed\n")
    print(f"WROTE {path} cells={ncell} fluid={n_fluid} solid={n_solid} faces={n_faces}")


def check_axes(ax: dict, n_ch: int) -> None:
    assert_close("x_end", ax["x"][-1], n_ch * PITCH, 1e-6)
    assert_close("y_end", ax["y"][-1], WIN_L, 1e-6)
    assert_close("z_top", ax["z"][-1], Z_TOP, 1e-6)
    assert_close("z_floor", ax["z"][ax["k0"]], Z_FLOOR, 1e-6)
    assert_close("z_cap", ax["z"][ax["k1"]], Z_CAP, 1e-6)
    assert_close("chan0", ax["chan"][0], H1, 1e-8)
    assert_close("chan_end", ax["chan"][-1], H1, 1e-6)
    assert_close("chanz0", ax["chan_z"][0], H1, 1e-8)
    assert_close("land0", ax["land"][0], H1, 1e-6)
    assert_close("floor0", ax["floor"][0], H1, 1e-6)
    assert_close("cap0", ax["cap"][0], H1, 1e-6)
    assert_close("yin", ax["y_sizes"][-1], Y_IN, 1e-6)
    assert_close("yout", ax["y_sizes"][0], Y_OUT, 1e-6)
    limits = (
        ("channel x", ax["chan"], R_FLUID),
        ("channel z", ax["chan_z"], R_FLUID),
        ("cap", ax["cap"], R_FLUID),
        ("land", ax["land"], R_SOLID),
        ("floor", ax["floor"], R_SOLID),
        ("streamwise", ax["y_sizes"], R_STREAM),
    )
    for name, sizes, limit in limits:
        g = max_growth(sizes)
        if g > limit + 0.02:
            raise SystemExit(f"{name} growth {g:.4f} > {limit}")
    if len(ax["chan"]) // 2 < N_HALF_MIN or len(ax["chan_z"]) // 2 < N_HALF_MIN:
        raise SystemExit("wall-to-centerline count below 10")
    # monotonic nodes
    for name, arr_ in (("x", ax["x"]), ("y", ax["y"]), ("z", ax["z"])):
        for a, b in zip(arr_, arr_[1:]):
            if b <= a:
                raise SystemExit(f"non-increasing {name}")


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "info"
    os.makedirs(MESH, exist_ok=True)
    os.makedirs(ICEM, exist_ok=True)
    single = build_axes(1)
    check_axes(single, 1)
    q1 = quality(single)
    yp = yplus_table()
    bad = gates_ok(q1, yp)
    array_ax = None
    qn = None
    if not bad and q1["n_cells"] < CELL_CAP:
        array_ax = build_axes(N_CH)
        check_axes(array_ax, N_CH)
        qn = quality(array_ax)
    text = report_text(single, q1, yp, qn)
    if bad:
        text += "GATES FAILED\n" + "\n".join(bad) + "\n"
    else:
        text += "GATES PASSED\n"
        text += "array designed because single pitch is under 1e6 cells\n"
    report = os.path.join(MESH, "sizing_report.txt")
    with open(report, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    print(text)
    write_rpl(os.path.join(ICEM, "build_lpddr_channel.rpl"), single, "LPDDR single pitch")
    if array_ax is not None:
        write_rpl(os.path.join(ICEM, "build_lpddr_array.rpl"), array_ax, "LPDDR six-channel array")
    if bad:
        raise SystemExit(1)
    if mode == "info":
        return
    if mode in ("channel", "all"):
        write_msh(
            os.path.join(MESH, "lpddr_channel_cht.msh"),
            single,
            "CP-GRACE-MC-01 LPDDR one pitch CHT hex; ICEM edge params; metres",
        )
    if mode in ("array", "all") and array_ax is not None:
        write_msh(
            os.path.join(MESH, "lpddr_array_cht.msh"),
            array_ax,
            "CP-GRACE-MC-01 LPDDR six-channel window CHT hex; ICEM edge params; metres",
        )


if __name__ == "__main__":
    main()
