# -*- coding: utf-8 -*-
"""关联式库。每个函数对应 THEORY.md 中一条编号公式，并返回适用域检查。

约定：
  - 摩擦因子一律区分 Fanning（f_F）与 Darcy（f_D = 4 f_F）。压降 Δp = f_D (L/Dh) ρV²/2。
  - check() 返回 {"param", "value", "range", "in_range"}；越界不抛错，由调用方汇总成适用域标志。
"""
from __future__ import annotations

import math


def check(name: str, value: float, lo: float, hi: float) -> dict:
    return {"param": name, "value": round(float(value), 6), "range": [lo, hi],
            "in_range": bool(lo <= value <= hi)}


# ---------------------------------------------------------------- 管内层流（矩形通道）
def fRe_rect_fanning(alpha: float) -> float:
    """式 (T2-1) Shah & London 1978 矩形通道充分发展层流 Fanning f·Re，α = 短边/长边（0–1）。
    来源 C-K01：Shah & London, Laminar Flow Forced Convection in Ducts, 1978, Ch.VII Rectangular Ducts（pp.196–222，KB 元数据）；
    式号未本地核对（原书付费），数值以 Incropera 6th 表 8.1 交叉核验（tests/test_benchmarks.py）。"""
    a = min(max(alpha, 0.0), 1.0)
    return 24.0 * (1 - 1.3553 * a + 1.9467 * a ** 2 - 1.7012 * a ** 3 + 0.9564 * a ** 4 - 0.2537 * a ** 5)


def fRe_rect_darcy(alpha: float) -> float:
    """式 (T2-2) Darcy f·Re = 4 × Fanning f·Re。"""
    return 4.0 * fRe_rect_fanning(alpha)


def nu_rect_T(alpha: float) -> float:
    """式 (T2-3) Shah & London 1978 矩形通道充分发展层流 Nu_T（四壁等温）。C-K01 Ch.VII（式号未核）；表值交叉核验 Incropera 6th 表 8.1。"""
    a = min(max(alpha, 0.0), 1.0)
    return 7.541 * (1 - 2.610 * a + 4.970 * a ** 2 - 5.119 * a ** 3 + 2.702 * a ** 4 - 0.548 * a ** 5)


def nu_rect_H1(alpha: float) -> float:
    """式 (T2-4) Shah & London 1978 矩形通道充分发展层流 Nu_H1（轴向恒热流、周向等温）。C-K01 Ch.VII（式号未核）；表值交叉核验 Incropera 6th 表 8.1。"""
    a = min(max(alpha, 0.0), 1.0)
    return 8.235 * (1 - 2.0421 * a + 3.0853 * a ** 2 - 2.4765 * a ** 3 + 1.0578 * a ** 4 - 0.1861 * a ** 5)


def nu_developing_legacy(Re: float, Pr: float, Dh: float, L: float) -> tuple:
    """式 (T2-5) 层流发展段：Nu = max(4, 1.86·Gz^(1/3))，Gz = Re·Pr·Dh/L。
    1.86 Gz^(1/3) 为 Sieder–Tate 1936 组合入口式（C-K02：转引 Çengel & Ghajar《Heat and Mass Transfer》
    第 5 版 式 (8-63)，p.510–511），
    原式含 (μ/μs)^0.14，此处取 1；下限 4.0 为内部约定（L5，model.py:161）。
    适用：0.48 < Pr < 16700，Gz^(1/3) ≥ 2/1.86（即 Nu ≥ 2），圆管等壁温。"""
    Gz = Re * Pr * Dh / L
    nu = max(4.0, 1.86 * Gz ** (1.0 / 3.0))
    checks = [check("Pr", Pr, 0.48, 16700.0), check("Re_laminar", Re, 0.0, 2300.0),
              check("Gz", Gz, (2.0 / 1.86) ** 3, 1e9)]
    return nu, Gz, checks


def fapp_Re_shah1978(x_plus: float) -> float:
    """式 (T2-6) Shah 1978 圆管层流入口段表观 Fanning f_app·Re，x+ = L/(D·Re)。
    C-K03：Shah, R.K., J. Fluids Eng. 100 (1978) 177–179，式 (1)；含入口动量通量变化与发展段附加阻力。"""
    xp = max(x_plus, 1e-9)
    s = math.sqrt(xp)
    return 3.44 / s + (16.0 + 1.25 / (4.0 * xp) - 3.44 / s) / (1.0 + 0.00021 / xp ** 2)


def fin_efficiency(h: float, k_fin: float, t: float, H: float) -> float:
    """式 (T2-7) 直肋效率（绝热肋尖）η = tanh(mH)/(mH)，m = sqrt(2h/(k t))。C-K02 Incropera §3.6 直肋绝热肋尖解。"""
    m = math.sqrt(2.0 * h / (k_fin * t))
    mH = m * H
    return math.tanh(mH) / mH if mH > 1e-12 else 1.0


# ---------------------------------------------------------------- 射流
MARTIN_RE = (2000.0, 1.0e5)
MARTIN_F = (0.004, 0.04)
MARTIN_HD = (2.0, 12.0)


def nu_martin_array(Re: float, Pr: float, f: float, hd: float) -> tuple:
    """式 (T3-1) Martin 1977 圆孔阵列面平均 Nu（C-J01 原文付费；式形已用 C-J02 两份公开转引逐项核对：
    Wiley CRFSFS 2023 综述表 1 式 (11)(15)；Ansys Innovation Space 讲义 S1LT4C2L4，引 Incropera 第 7 章）：
        Nu / Pr^0.42 = 0.5 · K · G · Re^(2/3)
        K = [1 + ((H/D)/(0.6/√f))^6]^(-0.05)
        G = 2√f (1 − 2.2√f) / (1 + 0.2 (H/D − 6) √f)
    适用 2000 ≤ Re ≤ 1e5，0.004 ≤ f ≤ 0.04，2 ≤ H/D ≤ 12；原式为气体，Pr^0.42 外推液体属 L6 假设。"""
    sf = math.sqrt(f)
    K = (1.0 + (hd / (0.6 / sf)) ** 6) ** -0.05
    G = 2.0 * sf * (1.0 - 2.2 * sf) / (1.0 + 0.2 * (hd - 6.0) * sf)
    nu = 0.5 * K * G * Re ** (2.0 / 3.0) * Pr ** 0.42
    checks = [check("Re", Re, *MARTIN_RE), check("f", f, *MARTIN_F), check("H/D", hd, *MARTIN_HD)]
    return nu, K, G, checks


def nu_martin_legacy_modelpy(Re: float, Pr: float, f: float, hd: float) -> float:
    """model.py:149 的实现（G 写成 √f(2 − 2.2√f)，且缺 0.5 系数），仅用于回归与缺陷说明。
    与式 (T3-1) 之比 = (2 − 2.2√f)/(1 − 2.2√f)，f = 0.0273 时约 2.57。"""
    sf = math.sqrt(f)
    K = ((1 + (hd / (0.6 / sf)) ** 6) ** -0.05) * sf * (2 - 2.2 * sf) / (1 + 0.2 * (hd - 6) * sf)
    return K * Re ** (2.0 / 3.0) * Pr ** 0.42


def nu_stagnation_legacy(Re: float, Pr: float) -> float:
    """式 (T3-2) 驻点核量级式 Nu0 = 0.5 Re^0.5 Pr^0.4（model.py:144，内部估算 L6，无文献出处；
    只用于驻点圆 2D 直径内的强化叠加，不代表整胞平均）。"""
    return 0.5 * Re ** 0.5 * Pr ** 0.4


WEI_PR = 7.56


def nu_wei2021(D_mm: float, L_mm: float, H_mm: float, Re: float, Pr: float, pr_exp: float = 0.44) -> tuple:
    """式 (T3-3) Wei et al. 2021 IJHMT 182:121865 式 (19)，p.11（C-J03，L2），交替进/排液微射流阵列：
        Nu_f = (5.64 a² + 0.031 a − 0.000632) · (H/L)^(−0.29) · Re^(0.48 a^(−0.16)) · (Pr/7.56)^n
        a = d/L；Nu_f = q d / ((T_s − T_in) k)，q 按单元胞面积；含流体温升（以入口温度为参考）。
    适用 0.01 ≤ a ≤ 0.4，0.01 ≤ H/L ≤ 0.4，32 ≤ Re ≤ 2048，0.05 ≤ H/d ≤ 20，水 Pr=7.56；
    Pr 修正指数 n=0.44 取自 Li & Garimella 2001（外推，L6）。误差带 ±30%。"""
    a = D_mm / L_mm
    hl = H_mm / L_mm
    nu_w = (5.64 * a ** 2 + 0.031 * a - 0.000632) * hl ** -0.29 * Re ** (0.48 * a ** -0.16)
    nu = nu_w * (Pr / WEI_PR) ** pr_exp
    checks = [check("d/L", a, 0.01, 0.4), check("H/L", hl, 0.01, 0.4), check("Re", Re, 32.0, 2048.0),
              check("H/d", H_mm / D_mm, 0.05, 20.0), check("Pr(=7.56 原式)", Pr, 7.56 * 0.999, 7.56 * 1.001)]
    return nu, nu_w, checks


def nu_robinson_schnitzler2007(Re: float, Pr: float, S_over_d: float, H_over_d: float) -> tuple:
    """式 (T3-4) Robinson & Schnitzler 2007（C-J04，转引 Whelan & Robinson 2009 式 (2) p.10，L2）：
        Nu_L / Pr^0.4 = 23.39 Re^0.46 (S/d)^(−0.442) (H/d)^(−0.00716)，Nu_L 以加热面边长 L=15.75 mm 为特征长度。
    适用 650 ≤ Re ≤ 6500，3 ≤ S/d ≤ 7，2 ≤ H/d ≤ 3，淹没水射流阵列、边缘排液。"""
    nu = 23.39 * Re ** 0.46 * S_over_d ** -0.442 * H_over_d ** -0.00716 * Pr ** 0.4
    checks = [check("Re", Re, 650.0, 6500.0), check("S/d", S_over_d, 3.0, 7.0), check("H/d", H_over_d, 2.0, 3.0)]
    return nu, checks


# ---------------------------------------------------------------- 局部阻力
def dp_orifice_legacy(rho: float, V: float, K: float = 1.8) -> float:
    """式 (T4-1) 孔口 Δp = K ρV²/2，K=1.8（v2.0 内部取值，L5）。"""
    return K * rho * V * V / 2.0


def dp_orifice_physics(rho: float, mu: float, V: float, D: float, t: float,
                       K_in: float = 0.5, K_out: float = 1.0) -> tuple:
    """式 (T4-2) 短管孔口：Δp = [K_in + 4 f_app (t/D) + K_out] ρV²/2，f_app 由式 (T2-6)。
    K_in = 0.5（锐边入口）、K_out = 1.0（射流动压全部耗散），为通用教科书取值（C-K04 Idelchik 手册类，页码未本地核对）。"""
    Re = rho * V * D / mu
    xp = t / (D * Re)
    fapp = fapp_Re_shah1978(xp) / Re
    K = K_in + 4.0 * fapp * t / D + K_out
    return K * rho * V * V / 2.0, K, Re, xp


def dp_duct_darcy(rho: float, mu: float, V: float, Dh: float, L: float, alpha: float) -> tuple:
    """式 (T2-8) 矩形槽充分发展层流 Δp = f_D (L/Dh) ρV²/2 = 2 (f_F Re) μ L V / Dh²。"""
    Re = rho * V * Dh / mu
    fD = fRe_rect_darcy(alpha) / Re
    return fD * (L / Dh) * rho * V * V / 2.0, Re, fD


def dp_duct_legacy(rho: float, mu: float, V: float, Dh: float, L: float, alpha: float) -> float:
    """model.py:206 / HBM 1D 报告的写法：f = (f_F Re)/Re 当 Darcy 用，比式 (T2-8) 低 4 倍。仅回归用。"""
    Re = rho * V * Dh / mu
    f = fRe_rect_fanning(alpha) / Re
    return f * (L / Dh) * rho * V * V / 2.0
