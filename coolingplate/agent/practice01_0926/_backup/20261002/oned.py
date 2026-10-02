# -*- coding: utf-8 -*-
"""一维设计：Martin 阵列式与低雷诺数准则分开采用。

数值来自 design/calc/model.py。Re、开孔率 f、H/D 三项都落在 Martin 1977
有效域内，才把 Martin 面平均换热写进保证值下限。否则保证值走短槽层流
发展段加驻点核，Martin 只保留为外推对照。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

CALC = Path(__file__).resolve().parents[2] / "design" / "calc"
sys.path.insert(0, str(CALC))

import model as M  # noqa: E402

MARTIN_RE = (2000.0, 1.0e5)
MARTIN_F = (0.004, 0.04)
MARTIN_HD = (2.0, 12.0)
SD_WINDOW = (4.0, 8.0)
MIN_DRILL_MM = 0.30
DP_LIMIT_KPA = 20.0


def _round(value):
    if isinstance(value, float):
        return round(value, 6)
    return value


def _in(value, window) -> bool:
    return window[0] <= value <= window[1]


def design(payload: dict | None = None) -> dict:
    raw = payload or {}
    point = str(raw.get("point") or "DP-A")
    if point not in M.DESIGN_POINTS:
        raise ValueError("设计点只接受 DP-A 或 DP-B")
    spec = M.DESIGN_POINTS[point]
    g = M.GEO
    D = float(raw.get("D_mm", g["D_jet"]))
    Q = float(raw.get("Q_lpm", spec["Q_lpm"]))
    N = int(raw.get("N", M.N_JET))
    H = float(raw.get("H_mm", g["H_jet"]))
    Sx = float(raw.get("Sx_mm", g["S_jet_x"]))
    Sy = float(raw.get("Sy_mm", g["S_jet_y"]))
    if min(D, Q, N, H, Sx, Sy) <= 0:
        raise ValueError("孔径、流量、孔数、喷距和节距都要大于 0")

    fl = M.WATER40
    P = float(spec["P"])
    Qg = Q * M.SPLIT_GPU
    js = M.jet_state(fl, Qg, D=D, N=N)
    f_open = (math.pi / 4.0 * D * D) / (Sx * Sy)
    hd = H / D
    sd_x, sd_y = Sx / D, Sy / D

    re_ok = _in(js["Re"], MARTIN_RE)
    f_ok = _in(f_open, MARTIN_F)
    hd_ok = _in(hd, MARTIN_HD)
    martin_applied = re_ok and f_ok and hd_ok

    Nu_m, K_m = M.nu_martin(js["Re"], fl.Pr, f=f_open, hd=hd)
    h_m = Nu_m * fl.k / (D * 1e-3)
    a_cov = N * Sx * Sy * 1e-6
    r_martin = 1.0 / (h_m * a_cov)

    low = _low_re(fl, Qg, D, N, Sx, Sy, js["Re"])
    r_conv = r_martin if martin_applied else low["R_conv"]
    r_lo = M.r_chain(r_conv, M.R_TIM2[0])
    r_hi = M.r_chain(low["R_conv"], M.R_TIM2[1])
    target = float(spec["target_R"])

    d_re = _diameter_for_re(fl, Qg, N, MARTIN_RE[0])
    f_at = (math.pi / 4.0 * d_re * d_re) / (Sx * Sy)
    hd_at = H / d_re
    drill_conflict = d_re < MIN_DRILL_MM

    hbm = M.hbm_state(fl, Q)
    ch = _channel(fl, Qg, N, Sy)
    dp_lo = (js["dP"] + ch["dP"] + hbm["dP"] + 3000.0) / 1000.0
    dp_hi = (js["dP"] + ch["dP"] + hbm["dP"] + 5000.0) / 1000.0
    filt_um = D / 10.0 * 1000.0

    criteria = [
        _crit("MARTIN_RE", re_ok, "ok" if re_ok else "warn",
              f"Re_D = {js['Re']:.0f}。Martin 1977 有效域 {MARTIN_RE[0]:.0f}–{MARTIN_RE[1]:.0g}。"),
        _crit("MARTIN_F", f_ok, "ok" if f_ok else "warn",
              f"开孔率 f = {f_open:.4f}。Martin 有效域 {MARTIN_F[0]}–{MARTIN_F[1]}。"),
        _crit("MARTIN_HD", hd_ok, "ok" if hd_ok else "warn",
              f"H/D = {hd:.2f}。Martin 有效域 {MARTIN_HD[0]:.0f}–{MARTIN_HD[1]:.0f}。"),
        _crit("LOWRE_MODEL", True, "ok",
              "Re 低于 2000 时，保证值用短槽层流发展段 Nu = max(4, 1.86·Gz^1/3)，"
              "再叠加驻点核 Nu0 = 0.5·Re^0.5·Pr^0.4。驻点式不代表整胞平均。"),
        _crit("FRICTION", True, "ok",
              f"矩形槽摩擦用 Shah & London，f·Re = {M.FRE_CH:.2f}，f = (f·Re)/Re_ch。"),
        _crit("HBM_VELOCITY", bool(hbm["ok"]), "ok" if hbm["ok"] else "bad",
              f"HBM 槽速 {hbm['V']:.3f} m/s，帽值 {g['V_cap_hbm']:.2f} m/s。"),
        _crit("DRILL", D >= MIN_DRILL_MM, "ok" if D >= MIN_DRILL_MM else "bad",
              f"孔径 {D:.3f} mm，微钻下限 {MIN_DRILL_MM:.2f} mm。"),
        _crit("FILTRATION", True, "ok",
              f"过滤不粗于孔径的 1/10，即 {filt_um:.0f} μm。"),
        _crit("SD_X", _in(sd_x, SD_WINDOW), "ok" if _in(sd_x, SD_WINDOW) else "warn",
              f"Sx/D = {sd_x:.2f}，文献推荐窗 {SD_WINDOW[0]:.0f}–{SD_WINDOW[1]:.0f}。"),
        _crit("SD_Y", _in(sd_y, SD_WINDOW), "ok" if _in(sd_y, SD_WINDOW) else "warn",
              f"Sy/D = {sd_y:.2f}，文献推荐窗 {SD_WINDOW[0]:.0f}–{SD_WINDOW[1]:.0f}。"),
        _crit("DP_LIMIT", dp_hi <= DP_LIMIT_KPA, "ok" if dp_hi <= DP_LIMIT_KPA else "bad",
              f"板内压降估算 {dp_lo:.2f}–{dp_hi:.2f} kPa，上限 {DP_LIMIT_KPA:.0f} kPa。"),
    ]
    if not martin_applied:
        criteria.append(_crit(
            "MARTIN_ENTRY", (not drill_conflict) and _in(f_at, MARTIN_F) and _in(hd_at, MARTIN_HD),
            "warn",
            _entry_text(d_re, f_at, hd_at, drill_conflict),
        ))

    regime = "martin" if martin_applied else "low-re"
    headline = (
        "三项都在 Martin 1977 有效域内，保证值下限采用阵列面平均换热。"
        if martin_applied else
        "未进入 Martin 有效域。保证值按低雷诺数准则：短槽层流加驻点核。Martin 数只作外推对照。"
    )
    return {
        "point": point,
        "role": spec["role"],
        "regime": regime,
        "headline": headline,
        "inputs": {
            "P_W": P, "Q_lpm": Q, "Qg_lpm": round(Qg, 4), "N": N,
            "D_mm": D, "H_mm": H, "Sx_mm": Sx, "Sy_mm": Sy, "Tin_C": spec["Tin"],
        },
        "target_R": target,
        "jet": {"V": _round(js["V"]), "Re": _round(js["Re"]), "dP_Pa": _round(js["dP"])},
        "open_area_f": _round(f_open),
        "HD": _round(hd),
        "martin": {
            "applied": martin_applied,
            "Nu": _round(Nu_m), "K": _round(K_m),
            "h": _round(h_m), "R_conv": _round(r_martin),
        },
        "low_re": {k: _round(v) for k, v in low.items()},
        "adopted": {
            "name": "Martin 阵列面平均" if martin_applied else "低 Re：短槽层流 + 驻点核",
            "R_lo": _round(r_lo),
            "R_hi": _round(r_hi),
            "meets_target_lo": r_lo < target,
            "meets_target_hi": r_hi < target,
        },
        "dTf_K": _round(M.delta_tf(fl, Q, P)),
        "hbm_V": _round(hbm["V"]),
        "dp_kPa": {"lo": _round(dp_lo), "hi": _round(dp_hi)},
        "lever": {
            "D_re2000_mm": _round(d_re),
            "f_at_D": _round(f_at),
            "HD_at_D": _round(hd_at),
            "drill_conflict": drill_conflict,
        },
        "criteria": criteria,
    }


def _channel(fl, Qg, N, Sy):
    q = Qg / 60000.0
    ch_per = Sy / M.GEO["ch_p"]
    area = N * ch_per * M.A_CH * 2.0
    V = q / area
    Re = fl.rho * V * M.DH_CH / fl.mu
    fr = M.FRE_CH / Re
    length = M.GEO["L_flow"] * 1e-3
    dP = fr * (length / M.DH_CH) * fl.rho * V * V / 2.0
    return dict(V=V, Re=Re, dP=dP, ch_per=ch_per)


def _low_re(fl, Qg, D, N, Sx, Sy, Re_jet):
    ch = _channel(fl, Qg, N, Sy)
    Nu = M.nu_duct_developing(ch["Re"], fl.Pr, M.DH_CH, M.GEO["L_flow"] * 1e-3)
    h_ch = Nu * fl.k / M.DH_CH
    eta, _m = M.fin_efficiency(h_ch, M.GEO["ch_w"] * 1e-3, M.GEO["ch_h"] * 1e-3)
    h_stag = M.nu_stagnation(Re_jet, fl.Pr) * fl.k / (D * 1e-3)
    ch_per = ch["ch_per"]
    a_fin = ch_per * 2.0 * (M.GEO["ch_h"] * 1e-3) * (Sx * 1e-3)
    a_bot = ch_per * (M.GEO["ch_w"] * 1e-3) * (Sx * 1e-3)
    a_stag = N * math.pi / 4.0 * (2.0 * D * 1e-3) ** 2
    hA = h_ch * (a_fin * eta + a_bot) * N + max(0.0, h_stag - h_ch) * a_stag
    a_cov = N * Sx * Sy * 1e-6
    return dict(
        Nu_ch=Nu, h_ch=h_ch, eta=eta, h_stag=h_stag,
        Re_ch=ch["Re"], V_ch=ch["V"], h_eff=hA / a_cov, R_conv=1.0 / hA,
    )


def _diameter_for_re(fl, Qg, N, Re):
    q = Qg / 60000.0
    return (fl.rho * q) / (fl.mu * N * (math.pi / 4.0) * Re) * 1e3


def _entry_text(d_re, f_at, hd_at, drill_conflict) -> str:
    base = (f"在当前流量和孔数下，Re 提到 2000 需要孔径约 {d_re:.3f} mm。"
            f"该孔径的 f = {f_at:.4f}，H/D = {hd_at:.2f}。")
    if drill_conflict:
        return base + (
            f" 该孔径低于微钻下限 {MIN_DRILL_MM:.2f} mm，不能靠缩孔进入 Martin 域。"
            "低 Re 准则是本几何的设计依据。"
        )
    return base + " 缩孔后还要再核 f 与 H/D 是否仍在 Martin 域内。"


def _crit(code, ok, level, message) -> dict:
    return {"code": code, "ok": bool(ok), "level": level, "message": message}
