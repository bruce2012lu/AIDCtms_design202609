# -*- coding: utf-8 -*-
"""Scheme D screening: all channels parallel, each HBM center-in / both-ends-out.

Four HBM on one column, 0.15 L/min each (0.60 L/min total), PG25 at 40 C.
Section stays the scheme C chain: 11 x 0.45 mm, rib 0.50 mm, land 0.525 mm, h 2.00 mm.
Does not rewrite hbm_1d_schemes_20260929.py.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

# DOWFROST LC 25 (25 vol% propylene glycol) at 40 C.
# Density, conductivity and viscosity from the 40 C row.
# Specific heat is listed as 3.9 kJ/kgK at 40 C.
RHO = 1022.5
CP = 3900.0
MU = 1.58e-3
K_F = 0.476
K_CU = 390.0
TIN = 40.0
Q_LPM = 0.60  # 0.15 L/min on each of the four HBM dies
POWER = 99.22
COL_W = 11.0e-3
COL_L = 50.0e-3
H_CH = 2.0e-3
T_BASE = 2.0e-3
N = 11
W = 0.45e-3
RIB = 0.50e-3
LAND = 0.525e-3
L_HEAT = 44.0e-3
Q_FLUX = POWER / (COL_W * L_HEAT)
SLOT = 1.0e-3
K_SPLIT = 1.5
T_TIM = 0.080e-3
K_TIM = 8.818342
V_CAP = 0.80
DY = 0.5e-3
NY = int(round(COL_L / DY))
STACKS = ((0.000, 0.011), (0.013, 0.024), (0.026, 0.037), (0.039, 0.050))


def dh_of(w=W, h=H_CH):
    return 2.0 * w * h / (w + h)


def fre_fanning(w=W, h=H_CH):
    a = min(w, h) / max(w, h)
    return 24.0 * (
        1.0
        - 1.3553 * a
        + 1.9467 * a ** 2
        - 1.7012 * a ** 3
        + 0.9564 * a ** 4
        - 0.2537 * a ** 5
    )


def dp_shah(fre, length, vel, dh):
    return fre * MU * length * vel / (2.0 * dh ** 2)


def fin_eta(h, rib=RIB, height=H_CH):
    m = math.sqrt(2.0 * h / (K_CU * rib))
    ml = m * height
    if ml < 1e-8:
        return 1.0
    return math.tanh(ml) / ml


def mass_flow():
    return RHO * Q_LPM / 60000.0


def cell_widths():
    widths = np.empty(N)
    widths[0] = LAND + W + RIB / 2.0
    widths[-1] = LAND + W + RIB / 2.0
    widths[1:-1] = W + RIB
    return widths


def die_layout(dy=DY):
    """Slot cells and the two outward legs of each die, in cell index."""
    dies = []
    for a, b in STACKS:
        mid = 0.5 * (a + b)
        slot0 = mid - 0.5 * SLOT
        slot1 = mid + 0.5 * SLOT
        j0 = int(round(a / dy))
        j1 = int(round(b / dy))
        s0 = int(round(slot0 / dy))
        s1 = int(round(slot1 / dy))
        left = list(range(s0 - 1, j0 - 1, -1))
        right = list(range(s1, j1))
        dies.append(
            {
                "y0": a,
                "y1": b,
                "mid": mid,
                "slot": list(range(s0, s1)),
                "left": left,
                "right": right,
            }
        )
    return dies


def bulk():
    mdot = mass_flow()
    m_leg = mdot / (8.0 * N)
    area = W * H_CH
    vel = m_leg / (RHO * area)
    dh = dh_of()
    re = RHO * vel * dh / MU
    pr = MU * CP / K_F
    length = 0.5 * (0.011 - SLOT)
    gz = dh / length * re * pr
    nu = max(4.0, 1.86 * gz ** (1.0 / 3.0))
    h = nu * K_F / dh
    eta = fin_eta(h)
    a_per_m = 2.0 * W + 2.0 * H_CH * eta
    ua = N * h * a_per_m * L_HEAT
    dtf = POWER / (mdot * CP)
    dtconv = POWER / ua
    fre = fre_fanning()
    dp = dp_shah(fre, length, vel, dh)
    dp_k = K_SPLIT * RHO * vel ** 2 / 2.0
    return {
        "mdot": mdot,
        "V_leg": vel,
        "Re": re,
        "Dh_mm": dh * 1e3,
        "Pr": pr,
        "Gz": gz,
        "Nu": nu,
        "h": h,
        "eta": eta,
        "dTf": dtf,
        "dTconv": dtconv,
        "dTwall": dtconv + dtf,
        "L_leg_mm": length * 1e3,
        "fRe": fre,
        "dP_leg_Pa": dp,
        "dP_split_Pa": dp_k,
        "dP_branch_Pa": dp + dp_k,
        "q_die_Lpm": Q_LPM / 4.0,
        "q_leg_Lpm": Q_LPM / 8.0,
    }


def solve(iters=6400, relax_new=0.45):
    dy = DY
    ny = NY
    dies = die_layout(dy)
    m_leg = mass_flow() / (8.0 * N)
    dh = dh_of()
    pr = MU * CP / K_F
    area = W * H_CH
    vel = m_leg / (RHO * area)
    re = RHO * vel * dh / MU
    widths = cell_widths()
    y0 = np.arange(ny) * dy
    y1 = y0 + dy
    mask = np.zeros(ny, dtype=bool)
    slot = np.zeros(ny, dtype=bool)
    for die in dies:
        mask |= (y1 > die["y0"] + 1e-12) & (y0 < die["y1"] - 1e-12)
        for j in die["slot"]:
            slot[j] = True
    dist = W + RIB
    g_lat = (K_CU * T_BASE * dy / dist) + (K_CU * H_CH * dy / RIB)
    a_ax = T_BASE * widths.copy() + H_CH * (RIB / 2.0)
    g_ax = K_CU * a_ax / dy

    def nu_h(x):
        x = max(x, 0.5 * dy)
        gz = dh / x * re * pr
        nu = max(4.0, 1.86 * gz ** (1.0 / 3.0))
        h = nu * K_F / dh
        return h, fin_eta(h)

    h_arr = np.zeros(ny)
    aw = np.zeros(ny)
    for die in dies:
        edge = die["mid"] - 0.5 * SLOT
        for j in die["left"]:
            x = edge - (j + 0.5) * dy
            h, eta = nu_h(x)
            h_arr[j] = h
            aw[j] = (2.0 * W + 2.0 * H_CH * eta) * dy
        edge = die["mid"] + 0.5 * SLOT
        for j in die["right"]:
            x = (j + 0.5) * dy - edge
            h, eta = nu_h(x)
            h_arr[j] = h
            aw[j] = (2.0 * W + 2.0 * H_CH * eta) * dy
        for j in die["slot"]:
            h, eta = nu_h(0.5 * dy)
            h_arr[j] = h
            aw[j] = (2.0 * W + 2.0 * H_CH * eta) * dy

    tw = np.full((N, ny), TIN + 12.0)
    tf = np.full((N, ny), TIN)

    def heat_seg(tin_seg, m, j, tw_j):
        ua = h_arr[j] * aw[j]
        denom = m * CP + 0.5 * ua
        tout = (tin_seg * (m * CP - 0.5 * ua) + ua * tw_j) / denom
        return 0.5 * (tin_seg + tout), tout

    exits = np.zeros((N, 8))

    def march():
        out = np.full((N, ny), TIN)
        for i in range(N):
            k = 0
            for die in dies:
                tin_seg = TIN
                m_slot = 2.0 * m_leg
                for j in die["slot"]:
                    tbar, tin_seg = heat_seg(tin_seg, m_slot, j, tw[i, j])
                    out[i, j] = tbar
                tin_leg = tin_seg
                for order in (die["left"], die["right"]):
                    tin_seg = tin_leg
                    for j in order:
                        tbar, tin_seg = heat_seg(tin_seg, m_leg, j, tw[i, j])
                        out[i, j] = tbar
                    exits[i, k] = tin_seg
                    k += 1
        return out

    prev = None
    for _ in range(iters):
        tf = march()
        tw_new = tw.copy()
        for j in range(ny):
            a = np.zeros(N)
            b = np.zeros(N)
            c = np.zeros(N)
            d = np.zeros(N)
            for i in range(N):
                ua = h_arr[j] * aw[j] if mask[j] else 0.0
                gl = g_lat if i > 0 else 0.0
                gr = g_lat if i < N - 1 else 0.0
                gap = g_ax[i] if j > 0 else 0.0
                gan = g_ax[i] if j < ny - 1 else 0.0
                b[i] = gl + gr + gap + gan + ua
                if i > 0:
                    a[i] = -gl
                if i < N - 1:
                    c[i] = -gr
                q = Q_FLUX * widths[i] * dy if mask[j] else 0.0
                d[i] = q + ua * tf[i, j]
                if j > 0:
                    d[i] += gap * tw_new[i, j - 1]
                if j < ny - 1:
                    d[i] += gan * tw[i, j + 1]
            for i in range(1, N):
                mcoef = a[i] / b[i - 1]
                b[i] -= mcoef * c[i - 1]
                d[i] -= mcoef * d[i - 1]
            tw_new[-1, j] = d[-1] / b[-1]
            for i in range(N - 2, -1, -1):
                tw_new[i, j] = (d[i] - c[i] * tw_new[i + 1, j]) / b[i]
        tw = relax_new * tw_new + (1.0 - relax_new) * tw
        mean_now = float(tw[:, mask].mean())
        if prev is not None and abs(mean_now - prev) < 1e-6:
            break
        prev = mean_now
    tf = march()
    q_out = float(m_leg * CP * np.sum(exits - TIN))

    wts = np.where(mask[None, :], widths[:, None], 0.0)
    heated = tw[:, mask]
    stacks = []
    for die in dies:
        sel = (y1 > die["y0"] + 1e-12) & (y0 < die["y1"] - 1e-12)
        ww = np.where(sel[None, :], widths[:, None], 0.0)
        stacks.append(
            {
                "Tmin": float(tw[:, sel].min()),
                "Tmean": float((tw * ww).sum() / ww.sum()),
                "Tmax": float(tw[:, sel].max()),
            }
        )
    tf_out = [float(v) for v in exits.reshape(-1)]
    return {
        "Tmin": float(heated.min()),
        "Tmean": float((tw * wts).sum() / wts.sum()),
        "Tmax": float(heated.max()),
        "dT": float(heated.max() - heated.min()),
        "dT_x": float(tw.max(axis=0)[mask].max() - tw.min(axis=0)[mask].min()) if False else float(heated.max() - heated.min()),
        "dT_channel": float(tw[:, mask].max() - tw[:, mask].min()),
        "lateral": float(tw.max() - tw.min()) - float(heated.max() - heated.min()),
        "stacks": stacks,
        "Tf_out": tf_out,
        "Tf_out_max": max(tf_out),
        "Tf_out_min": min(tf_out),
        "Q_out_W": q_out,
        "dies": [
            {
                "mid_mm": die["mid"] * 1e3,
                "slot_mm": [die["slot"][0] * DY * 1e3, (die["slot"][-1] + 1) * DY * 1e3],
                "n_left": len(die["left"]),
                "n_right": len(die["right"]),
            }
            for die in dies
        ],
    }


def main():
    b = bulk()
    r1 = solve(3200)
    r2 = solve(6400)
    dt_tim = Q_FLUX * T_TIM / K_TIM
    chain = 2 * LAND + N * W + (N - 1) * RIB
    out = {
        "bulk": b,
        "i3200": {k: v for k, v in r1.items() if k != "dies"},
        "i6400": r2,
        "dT_tim": dt_tim,
        "chain_mm": chain * 1e3,
        "drift_dT": abs(r2["dT"] - r1["dT"]),
        "drift_Tmean": abs(r2["Tmean"] - r1["Tmean"]),
    }
    dest = Path(__file__).resolve().parent / "_hbm_scheme_d.json"
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("chain_mm", round(chain * 1e3, 4))
    print("mdot", b["mdot"])
    print("V_leg", round(b["V_leg"], 4), "Re", round(b["Re"], 2), "Pr", round(b["Pr"], 3))
    print("Nu", round(b["Nu"], 3), "h", round(b["h"], 1), "eta", round(b["eta"], 4))
    print("dTf", round(b["dTf"], 3), "dTconv", round(b["dTconv"], 3), "dP", round(b["dP_branch_Pa"], 2))
    print("T", round(r2["Tmin"], 3), round(r2["Tmean"], 3), round(r2["Tmax"], 3), "dT", round(r2["dT"], 3))
    print("drift", out["drift_Tmean"], out["drift_dT"])
    print(
        "Tf_out",
        round(min(r2["Tf_out"]), 3),
        round(max(r2["Tf_out"]), 3),
        "Q_out",
        round(r2["Q_out_W"], 3),
    )
    for i, s in enumerate(r2["stacks"], 1):
        print(i, {k: round(v, 3) for k, v in s.items()})
    print("dies", r2["dies"])
    print("dTtim", round(dt_tim, 3))


if __name__ == "__main__":
    main()
