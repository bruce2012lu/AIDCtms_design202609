# -*- coding: utf-8 -*-
"""HBM 平槽区与 Grace 平行微通道区的一维设计。

HBM 跟 design/calc/model.py：不设喷嘴，Martin 不适用，流速帽 0.80 m/s。
Grace 跟 design/CP-GRACE-MC-01_calc.py：无微射流，Nu=4.8 是三面受热假设。
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

CALC = Path(__file__).resolve().parents[2] / "design" / "calc"
sys.path.insert(0, str(CALC))

import model as M  # noqa: E402

MIN_RIB = 0.30
MAX_ASPECT = 5.0
HBM_W = 11.0


def _r(value):
    return round(value, 6) if isinstance(value, float) else value


def _crit(code, ok, level, message):
    return {"code": code, "ok": bool(ok), "level": level, "message": message}


def hbm_design(payload: dict | None = None) -> dict:
    raw = payload or {}
    point = str(raw.get("point") or "DP-A")
    if point not in M.DESIGN_POINTS:
        raise ValueError("设计点只接受 DP-A 或 DP-B")
    spec = M.DESIGN_POINTS[point]
    P = float(spec["P"])
    Q = float(raw.get("Q_lpm", spec["Q_lpm"]))
    q_lpm = float(raw.get("Q_hbm_lpm", Q * (1.0 - M.SPLIT_GPU)))
    n_per = int(raw.get("n_per_side", 8))
    w = float(raw.get("w_mm", M.GEO["hbm_ch_w"]))
    depth = float(raw.get("d_mm", M.GEO["hbm_ch_h"]))
    pitch = float(raw.get("pitch_mm", 1.30))
    length = float(raw.get("L_mm", M.GEO["rib_len"]))
    v_cap = float(raw.get("V_cap", M.GEO["V_cap_hbm"]))
    p_hbm = float(raw.get("P_hbm_W", P * M.FRAC["hbm_total"]))
    if min(Q, q_lpm, n_per, w, depth, pitch, length, p_hbm) <= 0:
        raise ValueError("流量、条数和槽尺寸都要大于 0")

    fl = M.WATER40
    n = n_per * 2
    dh_mm = 2.0 * w * depth / (w + depth)
    dh = dh_mm * 1e-3
    area = n * w * depth * 1e-6
    q = q_lpm / 60000.0
    V = q / area
    Re = fl.rho * V * dh / fl.mu
    fre = M.f_re_rect(min(w, depth) / max(w, depth))
    f = fre / Re
    L = length * 1e-3
    dP = f * (L / dh) * fl.rho * V * V / 2.0
    Nu = M.nu_duct_developing(Re, fl.Pr, dh, L)
    h = Nu * fl.k / dh
    awet = n * L * (w + 2.0 * depth) * 1e-3
    R = 1.0 / (h * awet)
    rib = pitch - w
    aspect = depth / w
    span = (n_per - 1) * pitch + w
    qflux = p_hbm / M.GEO["n_hbm"] / (M.A_HBM * 1e4)
    ref = M.hbm_state(fl, spec["Q_lpm"])

    criteria = [
        _crit("NO_JET", True, "ok",
              "HBM 区不设喷嘴。没有射流雷诺数，Martin 1977 不用于这一区。"),
        _crit("LOW_RE", Re < 2000.0, "ok" if Re < 2000.0 else "warn",
              f"槽 Re = {Re:.0f}。低于 2000 时用层流发展段 Nu = max(4, 1.86·Gz^1/3)。"),
        _crit("V_CAP", V <= v_cap, "ok" if V <= v_cap else "bad",
              f"近壁流速 {V:.3f} m/s，冲蚀帽 {v_cap:.2f} m/s。"),
        _crit("RIB", rib >= MIN_RIB, "ok" if rib >= MIN_RIB else "bad",
              f"齿壁 {rib:.3f} mm（节距 {pitch:.2f} − 槽宽 {w:.2f}），下限 {MIN_RIB:.2f} mm。"),
        _crit("ASPECT", aspect <= MAX_ASPECT, "ok" if aspect <= MAX_ASPECT else "bad",
              f"深宽比 {aspect:.2f}，铲齿上限 {MAX_ASPECT:.1f}。"),
        _crit("SPAN", span <= HBM_W + 1e-9, "ok" if span <= HBM_W + 1e-9 else "bad",
              f"单侧槽组宽 {span:.2f} mm，HBM 宽 {HBM_W:.0f} mm。"),
    ]
    return {
        "zone": "HBM",
        "point": point,
        "headline": "八颗 HBM 只走两侧平槽，无喷嘴。保证换热用低雷诺数槽道，流速单独限在冲蚀帽以下。",
        "inputs": {
            "P_W": P, "P_hbm_W": p_hbm, "Q_lpm": Q, "Q_hbm_lpm": q_lpm,
            "n_per_side": n_per, "n": n, "w_mm": w, "d_mm": depth,
            "pitch_mm": pitch, "L_mm": length,
        },
        "flow": {
            "V": _r(V), "Re": _r(Re), "Dh_mm": _r(dh_mm),
            "dP_kPa": _r(dP / 1000.0), "q_W_cm2": _r(qflux),
        },
        "thermal": {
            "Nu": _r(Nu), "h": _r(h), "R_conv": _r(R), "dT_conv_K": _r(p_hbm * R),
        },
        "reference_dp_a_V": _r(ref["V"]),
        "criteria": criteria,
    }


def grace_design(payload: dict | None = None) -> dict:
    """复算 CP-GRACE-MC-01_calc.py。默认流量由 300 W、8 K 温升闭合。"""
    raw = payload or {}
    rho, cp, mu, k = 992.0, 4179.0, 6.53e-4, 0.632
    P = float(raw.get("P_W", 300.0))
    p_cpu = float(raw.get("P_cpu_W", 260.0))
    p_mem = float(raw.get("P_mem_W", 40.0))
    dT_spec = float(raw.get("dT_K", 8.0))
    q_energy = (P / (cp * dT_spec)) / rho * 60.0 * 1000.0
    Q = float(raw.get("Q_lpm", q_energy))
    n_cpu = int(raw.get("n_cpu", 48))
    w_cpu = float(raw.get("w_cpu_mm", 0.40))
    d_cpu = float(raw.get("d_cpu_mm", 1.20))
    L_cpu = float(raw.get("L_cpu_mm", 32.0))
    pitch = float(raw.get("pitch_cpu_mm", 0.80))
    n_mem = int(raw.get("n_mem_side", 6))
    w_mem = float(raw.get("w_mem_mm", 1.20))
    d_mem = float(raw.get("d_mem_mm", 0.80))
    L_mem = float(raw.get("L_mem_mm", 70.0))
    if min(P, p_cpu, Q, n_cpu, w_cpu, d_cpu, L_cpu, pitch, n_mem, w_mem, d_mem, L_mem) <= 0:
        raise ValueError("功率、流量和槽尺寸都要大于 0")
    if abs((p_cpu + p_mem) - P) > 0.05:
        raise ValueError("CPU 功率与内存功率之和要等于总功率")

    cpu = _grace_branch(rho, mu, k, Q, P, p_cpu, n_cpu, w_cpu, d_cpu, L_cpu)
    mem = _grace_branch(rho, mu, k, Q, P, p_mem / 2.0, n_mem, w_mem, d_mem, L_mem)
    dP_target = 10000.0
    dP_orif = dP_target - cpu["dP_Pa"]
    q_m3s = Q / 1000.0 / 60.0
    cd = 0.62
    a_eq = q_m3s / (cd * math.sqrt(2.0 * dP_orif / rho))
    d_eq = math.sqrt(4.0 * a_eq / math.pi) * 1000.0
    d_hole = d_eq / math.sqrt(4.0)
    rib = pitch - w_cpu
    aspect = d_cpu / w_cpu
    span = (n_cpu - 1) * pitch + w_cpu
    r_target = 0.080

    criteria = [
        _crit("NO_JET", True, "ok",
              "Grace 是平行微通道，不设微射流，不用 Martin 阵列式。"),
        _crit("NU_ASSUMPTION", True, "ok",
              "Nu = 4.8 是三面受热矩形槽的假设，不是拟合关联式，也不是 CFD。"),
        _crit("CPU_RE", cpu["Re"] < 2000.0, "ok" if cpu["Re"] < 2000.0 else "warn",
              f"CPU 槽 Re = {cpu['Re']:.0f}，按层流 f = 64/Re 加进出口局部阻力 1.31。"),
        _crit("MEM_RE", mem["Re"] < 2000.0, "ok" if mem["Re"] < 2000.0 else "warn",
              f"单侧内存槽 Re = {mem['Re']:.0f}。宽槽用来压低流速。"),
        _crit("RIB", rib >= MIN_RIB, "ok" if rib >= MIN_RIB else "bad",
              f"CPU 齿壁 {rib:.3f} mm，下限 {MIN_RIB:.2f} mm。"),
        _crit("ASPECT", aspect <= MAX_ASPECT, "ok" if aspect <= MAX_ASPECT else "bad",
              f"CPU 深宽比 {aspect:.2f}，上限 {MAX_ASPECT:.1f}。"),
        _crit("SPAN", span <= 40.0, "ok" if span <= 40.0 else "warn",
              f"CPU 槽组宽 {span:.2f} mm，候选发热窗约 40 mm。"),
        _crit("R_TARGET", cpu["R"] < r_target, "ok" if cpu["R"] < r_target else "warn",
              f"CPU 对流热阻 {cpu['R']:.4f} °C/W。壳–进液目标 < {r_target:.3f} °C/W 还含 TIM 余量，不是这个对流数。"),
        _crit("FLOW_ENVELOPE", Q <= 0.70 + 1e-9, "ok" if Q <= 0.70 + 1e-9 else "warn",
              f"流量 {Q:.3f} L/min。能量闭合约 {q_energy:.3f} L/min，包络 0.70 L/min。"),
    ]
    return {
        "zone": "Grace",
        "model": "CP-GRACE-MC-01",
        "headline": "两层铜、平行微通道、无微射流。CPU 260 W，内存合计 40 W。左进右出，只做一种手性。",
        "inputs": {
            "P_W": P, "P_cpu_W": p_cpu, "P_mem_W": p_mem, "Q_lpm": _r(Q),
            "Q_energy_lpm": _r(q_energy), "n_cpu": n_cpu,
            "w_cpu_mm": w_cpu, "d_cpu_mm": d_cpu, "L_cpu_mm": L_cpu,
        },
        "cpu": {k: _r(v) if isinstance(v, float) else v for k, v in cpu.items()},
        "mem_one_side": {k: _r(v) if isinstance(v, float) else v for k, v in mem.items()},
        "orifice": {
            "dP_kPa": _r(dP_orif / 1000.0),
            "equivalent_mm": _r(d_eq),
            "four_hole_mm": _r(d_hole),
            "target_branch_kPa": 10.0,
        },
        "q_cpu_W_cm2": _r(p_cpu / (40.0 * 32.0 / 100.0)),
        "q_mem_W_cm2": _r((p_mem / 2.0) / (50.0 * 70.0 / 100.0)),
        "criteria": criteria,
    }


def _grace_branch(rho, mu, k, Q_lpm, P, power, n, w_mm, d_mm, L_mm):
    q = Q_lpm * (power / P) / 1000.0 / 60.0
    w, d, L = w_mm * 1e-3, d_mm * 1e-3, L_mm * 1e-3
    Dh = 2.0 * w * d / (w + d)
    V = q / (n * w * d)
    Re = rho * V * Dh / mu
    f = 64.0 / Re
    dP = (f * (L / Dh) + 0.5 + 0.81) * rho * V * V / 2.0
    Nu = 4.8
    h = Nu * k / Dh
    awet = n * L * (w + 2.0 * d)
    R = 1.0 / (h * awet)
    return {
        "Q_lpm": q * 60.0 * 1000.0,
        "V": V, "Re": Re, "Dh_mm": Dh * 1000.0,
        "dP_kPa": dP / 1000.0, "dP_Pa": dP,
        "h": h, "R": R, "dT_K": power * R, "Nu": Nu,
    }
