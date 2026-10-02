# -*- coding: utf-8 -*-
"""HBM column 1D screening: co-flow, retained cross-flow, center-inlet hybrid.

Nominal geometry only. Water at 40 C. One side, 0.20 L/min, 99.22 W.
Dimension chain: 2*land + n*w + (n-1)*rib = 11 mm.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

RHO = 992.2
CP = 4179.0
MU = 6.53e-4
K_F = 0.631
K_CU = 390.0
TIN = 40.0  # C
Q_LPM = 0.20
POWER = 99.22  # W, one side
COL_W = 11.0e-3  # m
COL_L = 50.0e-3
H_CH = 2.0e-3
T_BASE = 2.0e-3
T_LID = 4.0e-3
L_HEAT = 44.0e-3
Q_FLUX = POWER / (COL_W * L_HEAT)  # 205000 W/m^2
NY = 50
DY = COL_L / NY
V_CAP = 0.80
MIN_RIB = 0.30e-3
MIN_W = 0.40e-3
MIN_LAND = 0.30e-3
MAX_ASPECT = 5.0
K_SPLIT = 1.5  # assumed tee / split loss, not a measured K

# stacks on the 50 mm column, metres
STACKS = ((0.000, 0.011), (0.013, 0.024), (0.026, 0.037), (0.039, 0.050))


def prandtl():
    return MU * CP / K_F


def mass_flow(q_lpm=Q_LPM):
    return RHO * q_lpm / 60000.0


def dh_of(w, h=H_CH):
    return 2.0 * w * h / (w + h)


def fre_fanning(w, h=H_CH):
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


def fin_eta(h, rib, height=H_CH):
    m = math.sqrt(2.0 * h / (K_CU * rib))
    ml = m * height
    if ml < 1e-8:
        return 1.0
    return math.tanh(ml) / ml


def bulk_channel(w, rib, n, q_lpm=Q_LPM, power=POWER):
    """Same closed-form 1D as hbm_1d_w08h20 case A, for any section."""
    mdot = mass_flow(q_lpm)
    m_ch = mdot / n
    area = w * H_CH
    vel = m_ch / (RHO * area)
    dh = dh_of(w)
    re = RHO * vel * dh / MU
    pr = prandtl()
    gz = dh / L_HEAT * re * pr
    nu = max(4.0, 1.86 * gz ** (1.0 / 3.0))
    h = nu * K_F / dh
    eta = fin_eta(h, rib)
    # lid + floor + two rib faces
    a_per_m = 2.0 * w + 2.0 * H_CH * eta
    ua = n * h * a_per_m * L_HEAT
    dtf = power / (mdot * CP)
    dtconv = power / ua
    fre = fre_fanning(w)
    dp = dp_shah(fre, COL_L, vel, dh)
    return {
        "V": vel,
        "Re": re,
        "Dh_mm": dh * 1e3,
        "Nu": nu,
        "h": h,
        "eta": eta,
        "dTf": dtf,
        "dTconv": dtconv,
        "dTwall": dtconv + dtf,
        "dP_Pa": dp,
        "fRe": fre,
        "Pr": pr,
    }


def land_of(n, w, rib):
    return (COL_W - n * w - (n - 1) * rib) / 2.0


def chain_ok(n, w, rib, land=None):
    if land is None:
        land = land_of(n, w, rib)
    total = 2 * land + n * w + (n - 1) * rib
    return abs(total - COL_W) < 1e-9 and land >= MIN_LAND - 1e-12 and rib >= MIN_RIB - 1e-12 and w >= MIN_W - 1e-12 and (H_CH / w) <= MAX_ASPECT + 1e-9


def heated_mask(ny=NY, dy=None):
    if dy is None:
        dy = COL_L / ny
    y0 = np.arange(ny) * dy
    y1 = y0 + dy
    mask = np.zeros(ny, dtype=bool)
    for a, b in STACKS:
        mask |= (y1 > a + 1e-12) & (y0 < b - 1e-12)
    return mask


def cell_widths(n, w, rib, land):
    """Heat-share width of each channel, rib midplane to rib midplane. Sum = 11 mm."""
    widths = np.empty(n)
    if n == 1:
        widths[0] = COL_W
        return widths
    widths[0] = land + w + rib / 2.0
    widths[-1] = land + w + rib / 2.0
    if n > 2:
        widths[1:-1] = w + rib
    return widths


def scheme_spec(n, scheme):
    """Return kind per channel: 'plus', 'minus', 'center'."""
    kind = ["plus"] * n
    if scheme == "coflow":
        return kind
    if scheme == "cross":
        # even count from high Y (minus), odd count from low Y (plus): 4 and 3 when n=7
        for i in range(n):
            kind[i] = "minus" if i % 2 == 0 else "plus"
        return kind
    if scheme == "center":
        # Middle three channels (two when n is even) are center-fed.
        # Every other channel stays cross-flow, adjacent slots opposite.
        n_mid = 3 if n % 2 else 2
        if n < n_mid + 2:
            n_mid = max(1, n - 2)
        i0 = (n - n_mid) // 2
        for i in range(n):
            if i0 <= i < i0 + n_mid:
                kind[i] = "center"
            else:
                kind[i] = "minus" if i % 2 == 0 else "plus"
        return kind
    raise ValueError(scheme)


def solve(n, w, rib, scheme, q_lpm=Q_LPM, power=POWER, ny=NY, iters=250, couple=True):
    land = land_of(n, w, rib)
    mdot = mass_flow(q_lpm)
    m_ch = mdot / n
    dh = dh_of(w)
    pr = prandtl()
    area = w * H_CH
    kind = scheme_spec(n, scheme)
    widths = cell_widths(n, w, rib, land)
    dy = COL_L / ny
    mask = heated_mask(ny, dy)
    q_line = Q_FLUX * (power / POWER)  # keep flux consistent if power overridden
    # local heat uses the same flux; total then scales with power/POWER
    dist = w + rib  # centre to centre across one rib
    g_lat = (K_CU * T_BASE * dy / dist) + (K_CU * H_CH * dy / rib)
    if not couple:
        g_lat = 0.0
    a_ax = T_BASE * widths + H_CH * rib * 0.5
    # edge lands add their copper into the edge cells; rib copper split to both sides
    a_ax = T_BASE * widths.copy()
    a_ax += H_CH * (rib / 2.0)
    a_ax[0] += H_CH * 0.0
    g_ax = K_CU * a_ax / dy

    # velocity and Re per stream
    vel_ch = m_ch / (RHO * area)
    re_ch = RHO * vel_ch * dh / MU
    # center legs carry half the channel flow
    vel_leg = 0.5 * vel_ch
    re_leg = 0.5 * re_ch

    def nu_h_eta(re, x):
        x = max(x, 0.5 * dy)
        gz = dh / x * re * pr
        nu = max(4.0, 1.86 * gz ** (1.0 / 3.0))
        h = nu * K_F / dh
        eta = fin_eta(h, rib)
        return h, eta

    # precompute h and wet area
    h_arr = np.zeros((n, ny))
    aw = np.zeros((n, ny))  # m^2 per segment
    x_arr = np.zeros((n, ny))
    for i, kd in enumerate(kind):
        for j in range(ny):
            yc = (j + 0.5) * dy
            if kd == "plus":
                x = yc
                re = re_ch
            elif kd == "minus":
                x = COL_L - yc
                re = re_ch
            else:
                x = abs(yc - 0.5 * COL_L)
                re = re_leg
            x_arr[i, j] = x
            h, eta = nu_h_eta(re, x)
            h_arr[i, j] = h
            aw[i, j] = (2.0 * w + 2.0 * H_CH * eta) * dy

    tw = np.full((n, ny), TIN + 15.0)
    tf = np.full((n, ny), TIN + 3.0)

    def march_channel(i):
        kd = kind[i]
        if kd == "center":
            order_left = list(range(ny // 2 - 1, -1, -1))
            order_right = list(range(ny // 2, ny))
            legs = ((order_left, 0.5 * m_ch), (order_right, 0.5 * m_ch))
        elif kd == "plus":
            legs = ((list(range(ny)), m_ch),)
        else:
            legs = ((list(range(ny - 1, -1, -1)), m_ch),)
        out = np.zeros(ny)
        for order, m in legs:
            tin_seg = TIN
            for j in order:
                ua = h_arr[i, j] * aw[i, j]
                denom = m * CP + 0.5 * ua
                tout = (tin_seg * (m * CP - 0.5 * ua) + ua * tw[i, j]) / denom
                out[j] = 0.5 * (tin_seg + tout)
                tin_seg = tout
        return out

    for _ in range(iters):
        for i in range(n):
            tf[i] = march_channel(i)
        tw_new = tw.copy()
        for j in range(ny):
            # Thomas solve
            a = np.zeros(n)
            b = np.zeros(n)
            c = np.zeros(n)
            d = np.zeros(n)
            for i in range(n):
                ua = h_arr[i, j] * aw[i, j]
                gl = g_lat if i > 0 else 0.0
                gr = g_lat if i < n - 1 else 0.0
                gap = g_ax[i] if j > 0 else 0.0
                gan = g_ax[i] if j < ny - 1 else 0.0
                b[i] = gl + gr + gap + gan + ua
                if i > 0:
                    a[i] = -gl
                if i < n - 1:
                    c[i] = -gr
                q = q_line * widths[i] * dy if mask[j] else 0.0
                d[i] = q + ua * tf[i, j]
                if j > 0:
                    d[i] += gap * tw[i, j - 1]
                if j < ny - 1:
                    d[i] += gan * tw[i, j + 1]
            # Thomas
            for i in range(1, n):
                m = a[i] / b[i - 1]
                b[i] -= m * c[i - 1]
                d[i] -= m * d[i - 1]
            tw_new[-1, j] = d[-1] / b[-1]
            for i in range(n - 2, -1, -1):
                tw_new[i, j] = (d[i] - c[i] * tw_new[i + 1, j]) / b[i]
        tw = 0.45 * tw_new + 0.55 * tw

    # heated-node stats, width-weighted
    wts = np.where(mask[None, :], widths[:, None], 0.0)
    wsum = wts.sum()
    tmean = float((tw * wts).sum() / wsum)
    heated_vals = tw[:, mask]
    tmin = float(heated_vals.min())
    tmax = float(heated_vals.max())
    # per stack
    stacks = []
    y0 = np.arange(ny) * dy
    y1 = y0 + dy
    for a, b in STACKS:
        sel = (y1 > a + 1e-12) & (y0 < b - 1e-12)
        ww = np.where(sel[None, :], widths[:, None], 0.0)
        stacks.append(
            {
                "Tmean": float((tw * ww).sum() / ww.sum()),
                "Tmin": float(tw[:, sel].min()),
                "Tmax": float(tw[:, sel].max()),
            }
        )
    stack_means = [s["Tmean"] for s in stacks]
    # outlet fluid
    tf_out = []
    for i, kd in enumerate(kind):
        if kd == "plus":
            tf_out.append(float(tf[i, -1]))
        elif kd == "minus":
            tf_out.append(float(tf[i, 0]))
        else:
            tf_out.append(float(max(tf[i, 0], tf[i, -1])))
    bulk = bulk_channel(w, rib, n, q_lpm, power)
    vel_max = vel_ch  # legs are slower
    fre = fre_fanning(w)
    dp_slot = dp_shah(fre, COL_L, vel_ch, dh)
    # center legs are half length and half velocity; side channels full length
    n_center = sum(kd == "center" for kd in kind)
    n_side = n - n_center
    dp_leg = dp_shah(fre, 0.5 * COL_L, vel_leg, dh) if n_center else 0.0
    dp_split = K_SPLIT * RHO * vel_leg ** 2 / 2.0 if n_center else 0.0
    # parallel branches: report the higher of side-slot and (leg + split)
    dp_branch = max(dp_slot, dp_leg + dp_split)
    return {
        "scheme": scheme,
        "n": n,
        "w_mm": w * 1e3,
        "rib_mm": rib * 1e3,
        "land_mm": land * 1e3,
        "chain_mm": (2 * land + n * w + (n - 1) * rib) * 1e3,
        "kinds": kind,
        "V_ch": vel_ch,
        "V_leg": vel_leg,
        "V_max": vel_max,
        "Re": re_ch,
        "dP_slot_Pa": dp_slot,
        "dP_branch_Pa": dp_branch,
        "Tmean": tmean,
        "Tmin": tmin,
        "Tmax": tmax,
        "dT": tmax - tmin,
        "dT_stacks": max(stack_means) - min(stack_means),
        "stacks": stacks,
        "Tf_out_max": max(tf_out),
        "bulk": bulk,
        "couple": couple,
        "q_flux": q_line,
    }


def round_result(r, nd=3):
    out = {
        "scheme": r["scheme"],
        "n": r["n"],
        "w_mm": round(r["w_mm"], 3),
        "rib_mm": round(r["rib_mm"], 3),
        "land_mm": round(r["land_mm"], 3),
        "chain_mm": round(r["chain_mm"], 4),
        "kinds": r["kinds"],
        "V_ch": round(r["V_ch"], 4),
        "V_leg": round(r["V_leg"], 4),
        "Re": round(r["Re"], 2),
        "dP_slot_Pa": round(r["dP_slot_Pa"], 2),
        "dP_branch_Pa": round(r["dP_branch_Pa"], 2),
        "Tmean": round(r["Tmean"], 3),
        "Tmin": round(r["Tmin"], 3),
        "Tmax": round(r["Tmax"], 3),
        "dT": round(r["dT"], 3),
        "dT_stacks": round(r["dT_stacks"], 3),
        "stacks": [
            {k: round(v, 3) for k, v in s.items()} for s in r["stacks"]
        ],
        "Tf_out_max": round(r["Tf_out_max"], 3),
        "couple": r["couple"],
        "bulk": {k: round(v, 4) if isinstance(v, float) else v for k, v in r["bulk"].items()},
    }
    return out


def sweep():
    best = []
    ws = np.round(np.arange(0.40, 1.21, 0.05), 2)
    ribs = np.round(np.arange(0.30, 1.21, 0.05), 2)
    for n in range(6, 12):
        for w_mm in ws:
            for rib_mm in ribs:
                w = w_mm / 1000.0
                rib = rib_mm / 1000.0
                land = land_of(n, w, rib)
                if not chain_ok(n, w, rib, land):
                    continue
                if land > 1.50e-3:
                    continue
                b = bulk_channel(w, rib, n)
                if b["V"] > V_CAP:
                    continue
                # coarse screen
                r = solve(n, w, rib, "center", ny=25, iters=80)
                best.append((r["dT"], r["Tmean"], n, w, rib, r["dT_stacks"], b["dTconv"], b["V"]))
    best.sort()
    return best[:25]


def search_eff():
    """Minimize bulk convection drop with the center-fed scheme still under the 5 C screen."""
    rows = []
    ws = np.round(np.arange(0.40, 1.21, 0.05), 2)
    ribs = np.round(np.arange(0.30, 1.21, 0.05), 2)
    for n in range(6, 13):
        for w_mm in ws:
            for rib_mm in ribs:
                w = float(w_mm) / 1000.0
                rib = float(rib_mm) / 1000.0
                land = land_of(n, w, rib)
                if not chain_ok(n, w, rib, land) or land > 1.20e-3:
                    continue
                b = bulk_channel(w, rib, n)
                if b["V"] > V_CAP:
                    continue
                r = solve(n, w, rib, "center", ny=25, iters=70)
                rows.append(
                    (
                        round(b["dTconv"], 3),
                        round(r["dT"], 3),
                        round(r["dT_stacks"], 3),
                        round(r["Tmean"], 3),
                        n,
                        float(w_mm),
                        float(rib_mm),
                        round(land * 1e3, 3),
                        round(b["V"], 4),
                        round(b["eta"], 4),
                        round(b["dP_Pa"], 1),
                    )
                )
    rows.sort()
    kept = [t for t in rows if t[1] <= 2.70]
    dest = Path(__file__).resolve().parent / "_hbm_1d_eff.json"
    dest.write_text(
        json.dumps({"pass_dt": kept[:40], "best_conv_any": rows[:15]}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("n_pass", len(kept), "n_all", len(rows))
    for t in kept[:12]:
        print("conv", t[0], "dT", t[1], "st", t[2], "n", t[4], "w", t[5], "rib", t[6], "land", t[7], "V", t[8])


def main():
    out_dir = Path(__file__).resolve().parent
    base_bulk = bulk_channel(0.80e-3, 0.80e-3, 7)
    cases = []
    for scheme in ("coflow", "cross", "center"):
        for couple in (True, False):
            r = solve(7, 0.80e-3, 0.80e-3, scheme, ny=50, iters=300, couple=couple)
            cases.append(round_result(r))
    # a few explicit geometry candidates on the center scheme, refined
    candidates = [
        (7, 0.80, 0.80),
        (7, 0.70, 0.90),
        (7, 0.60, 1.00),
        (8, 0.70, 0.60),
        (8, 0.65, 0.65),
        (9, 0.60, 0.50),
        (9, 0.55, 0.55),
        (8, 0.60, 0.70),
        (6, 0.90, 0.90),
        (10, 0.50, 0.45),
        (11, 0.45, 0.40),
    ]
    refined = []
    for n, wmm, rmm in candidates:
        w, rib = wmm / 1000.0, rmm / 1000.0
        land = land_of(n, w, rib)
        if not chain_ok(n, w, rib, land):
            refined.append({"n": n, "w_mm": wmm, "rib_mm": rmm, "land_mm": land * 1e3, "ok": False})
            continue
        b = bulk_channel(w, rib, n)
        if b["V"] > V_CAP:
            refined.append({"n": n, "w_mm": wmm, "rib_mm": rmm, "V": b["V"], "ok": False, "reason": "velocity"})
            continue
        row = {"ok": True, "bulk_V": round(b["V"], 4), "bulk_dTconv": round(b["dTconv"], 3), "bulk_eta": round(b["eta"], 4)}
        for scheme in ("cross", "center"):
            r = solve(n, w, rib, scheme, ny=50, iters=300, couple=True)
            row[scheme] = round_result(r)
        refined.append(row)
    top = sweep()
    payload = {
        "bulk_w08h20": {k: round(v, 4) if isinstance(v, float) else v for k, v in base_bulk.items()},
        "q_flux": Q_FLUX,
        "cases": cases,
        "refined": refined,
        "sweep_top": [
            {
                "dT": round(t[0], 3),
                "Tmean": round(t[1], 3),
                "n": t[2],
                "w_mm": round(t[3] * 1e3, 2),
                "rib_mm": round(t[4] * 1e3, 2),
                "dT_stacks": round(t[5], 3),
                "dTconv": round(t[6], 3),
                "V": round(t[7], 4),
            }
            for t in top
        ],
    }
    dest = out_dir / "_hbm_1d_scan.json"
    dest.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print("wrote", dest.name)
    print("bulk", payload["bulk_w08h20"])
    for c in cases:
        print(c["scheme"], "couple", c["couple"] if "couple" in c else "", "dT", c["dT"], "stacks", c["dT_stacks"], "T", c["Tmin"], c["Tmean"], c["Tmax"])


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "eff":
        search_eff()
    else:
        main()
