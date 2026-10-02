# -*- coding: utf-8 -*-
"""可追溯工质物性库。

每个工质给出 ρ、cp、μ、k 随温度的函数、适用温度范围、出处条目与可信度等级。
越出适用范围时不静默外推：返回结果带 range_ok=False 与警告，strict=True 时直接报错。
公式与出处见 THEORY.md §1，引用条目见 citations.json（C-P01…C-P07）。
"""
from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

# ---------------------------------------------------------------- 数据表
# NIST Chemistry WebBook 水 1 atm 等压线（C-P01，L1）：T °C → ρ kg/m3, cp J/kgK, μ Pa·s, k W/mK
_NIST_WATER = {
    20.0: (998.207, 4184.05, 1.00160e-3, 0.598012),
    25.0: (997.048, 4181.31, 8.90022e-4, 0.606516),
    30.0: (995.649, 4179.82, 7.97222e-4, 0.614392),
    35.0: (994.033, 4179.26, 7.19126e-4, 0.621700),
    40.0: (992.216, 4179.41, 6.52729e-4, 0.628486),
    45.0: (990.213, 4180.14, 5.95769e-4, 0.634783),
    50.0: (988.035, 4181.34, 5.46516e-4, 0.640621),
    55.0: (985.693, 4182.96, 5.03625e-4, 0.646021),
    60.0: (983.196, 4184.95, 4.66035e-4, 0.651000),
    65.0: (980.551, 4187.32, 4.32903e-4, 0.655575),
    70.0: (977.765, 4190.07, 4.03548e-4, 0.659758),
}

# CoolProp INCOMP::MPG（Melinder 2010，C-P05）系数：行 (T-Tbase)^i，列 (x-xbase)^j，x 为质量分数
_MPG_TBASE, _MPG_XBASE = 305.8583, 0.307031
_MPG = {
    "rho": [[1018.0, 76.04, -24.98, -155.0, -113.1, 234.2],
            [-0.5406, -0.945, 0.27, 2.829, -2.221, 0.0],
            [-0.002666, 0.005541, -0.004018, -0.007175, 0.0, 0.0],
            [1.347e-05, -1.343e-05, 3.376e-05, 0.0, 0.0, 0.0]],
    "cp": [[3882.0, -1304.0, -1598.0, 353.9, 5000.0, -4959.0],
           [2.699, 5.07, 0.9534, 31.02, -71.35, 0.0],
           [-0.001659, -0.004752, 0.1167, -0.295, 0.0, 0.0],
           [-1.032e-05, 0.0001522, -0.000487, 0.0, 0.0, 0.0]],
    "k": [[0.4513, -0.4795, 0.2076, -0.09083, -0.05952, 0.2104],
          [0.0007955, -0.001678, 0.001563, -0.002518, -0.003605, 0.0],
          [3.482e-08, 8.941e-06, -4.615e-05, 6.543e-05, 0.0, 0.0],
          [-5.966e-09, 1.493e-08, 9.897e-08, 0.0, 0.0, 0.0]],
    "lnmu": [[-6.224055, 3.328, 0.5453, -3.9, -1.587, 35.64],
             [-0.03045, -0.03984, -0.00086, 0.1054, 0.04475, 0.0],
             [0.0002525, 0.0004332, -0.0001593, -0.001589, 0.0, 0.0],
             [-1.399e-06, -1.86e-06, -4.465e-07, 0.0, 0.0, 0.0]],
}


@dataclass
class FluidState:
    fluid_id: str
    name: str
    T_C: float
    rho: float      # kg/m3
    cp: float       # J/(kg K)
    mu: float       # Pa s
    k: float        # W/(m K)
    Pr: float
    T_range_C: tuple
    range_ok: bool
    source: str
    trust: str
    status: str
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["T_range_C"] = list(self.T_range_C)
        return d


class FluidModel:
    """一种工质的物性模型。"""

    def __init__(self, fluid_id, name, func, T_range, source, trust, status="active", note=""):
        self.fluid_id = fluid_id
        self.name = name
        self._func = func
        self.T_range = T_range
        self.source = source
        self.trust = trust
        self.status = status
        self.note = note

    def state(self, T_C: float, strict: bool = False) -> FluidState:
        lo, hi = self.T_range
        ok = lo - 1e-9 <= T_C <= hi + 1e-9
        warns = []
        if not ok:
            msg = f"{self.fluid_id}: T={T_C:.2f} °C 超出适用范围 {lo}–{hi} °C"
            if strict:
                raise ValueError(msg)
            warns.append(msg + "，结果为外推")
        if self.status == "deprecated":
            warns.append(f"{self.fluid_id} 已停用，仅供复现旧报告")
        rho, cp, mu, k = self._func(T_C)
        return FluidState(self.fluid_id, self.name, T_C, rho, cp, mu, k, mu * cp / k,
                          self.T_range, ok, self.source, self.trust, self.status, warns)


def _interp_table(tab: dict, T: float):
    ts = sorted(tab)
    T_c = min(max(T, ts[0]), ts[-1])
    for a, b in zip(ts, ts[1:]):
        if a <= T_c <= b:
            w = (T_c - a) / (b - a)
            ra, rb = tab[a], tab[b]
            rho = ra[0] + w * (rb[0] - ra[0])
            cp = ra[1] + w * (rb[1] - ra[1])
            mu = math.exp(math.log(ra[2]) + w * (math.log(rb[2]) - math.log(ra[2])))
            k = ra[3] + w * (rb[3] - ra[3])
            return rho, cp, mu, k
    raise ValueError(T)


def _water_nist(T):
    return _interp_table(_NIST_WATER, T)


def _const(rho, cp, mu, k):
    return lambda T: (rho, cp, mu, k)


def _pg25_tds(T):
    """DOWFROST LC 25 TDS 拟合（C-P02），PG25物性溯源 §4.4。"""
    rho = 1041.1375 - 0.379167 * T - 0.002167 * T * T
    cp = 3820.714 + 2.381 * T
    k = 0.430196 + 1.43452e-3 * T - 6.9e-6 * T * T
    mu = math.exp(-2.01892 + 257.257 / (T + 64.0)) * 1e-3
    return rho, cp, mu, k


def _pg25_guide(T):
    """Dow LC 工程与操作指南表 2 拟合（C-P03）；cp、k 与 TDS 相同。"""
    rho = 1041.0071 - 0.316667 * T - 0.002476 * T * T
    cp = 3820.714 + 2.381 * T
    k = 0.430196 + 1.43452e-3 * T - 6.9e-6 * T * T
    mu = math.exp(-3.52641 + 592.158 / (T + 113.5)) * 1e-3
    return rho, cp, mu, k


def _mpg_poly(c, T, x):
    dt, dx = T + 273.15 - _MPG_TBASE, x - _MPG_XBASE
    return sum(c[i][j] * dt ** i * dx ** j for i in range(len(c)) for j in range(len(c[0])))


def mpg_props(T: float, x_mass: float):
    """CoolProp INCOMP::MPG 多项式（Melinder 2010）。优先调用已安装的 CoolProp，否则按系数手算。"""
    try:  # pragma: no cover - 本机未安装 CoolProp 时走手算
        from CoolProp.CoolProp import PropsSI  # type: ignore
        fl = f"INCOMP::MPG[{x_mass}]"
        Tk = T + 273.15
        return (PropsSI("D", "T", Tk, "P", 2e5, fl), PropsSI("C", "T", Tk, "P", 2e5, fl),
                PropsSI("V", "T", Tk, "P", 2e5, fl), PropsSI("L", "T", Tk, "P", 2e5, fl))
    except Exception:
        return (_mpg_poly(_MPG["rho"], T, x_mass), _mpg_poly(_MPG["cp"], T, x_mass),
                math.exp(_mpg_poly(_MPG["lnmu"], T, x_mass)), _mpg_poly(_MPG["k"], T, x_mass))


REGISTRY = {
    "water-nist": FluidModel(
        "water-nist", "去离子水（NIST 1 atm）", _water_nist, (20.0, 70.0),
        "C-P01 NIST Chemistry WebBook 水 1 atm 等压线（dat-2023-nist-water-isobar-1atm），表行 20–70 °C", "L1"),
    "water-legacy-v20": FluidModel(
        "water-legacy-v20", "水 40 °C（v2.0 / model.py WATER40 常数）", _const(992.2, 4179.0, 6.53e-4, 0.631),
        (40.0, 40.0), "C-P06 design/calc/model.py:20 WATER40；与 NIST 40 °C 相差 ≤0.4%", "L5",
        status="regression-only"),
    "pg25-dowfrost-lc25-tds": FluidModel(
        "pg25-dowfrost-lc25-tds", "PG25 · DOWFROST LC 25 TDS（推荐基线）", _pg25_tds, (20.0, 55.0),
        "C-P02 Dow DOWFROST LC TDS『Physical Properties of DOWFROST LC 25』表；拟合见 PG25物性溯源 §4.4", "L3"),
    "pg25-dow-guide": FluidModel(
        "pg25-dow-guide", "PG25 · Dow LC 工程指南表 2（低粘度敏感性）", _pg25_guide, (20.0, 55.0),
        "C-P03 Dow DOWFROST LC Engineering & Operating Guide 表 2；拟合见 PG25物性溯源 §4.4", "L3"),
    "pg25-mpg-25.6wt": FluidModel(
        "pg25-mpg-25.6wt", "PG 25.6 wt%（≈25 vol%）· CoolProp MPG", lambda T: mpg_props(T, 0.256), (0.0, 100.0),
        "C-P05 CoolProp INCOMP::MPG，Melinder 2010（pap-2007-melinder-aqueous-secondary-fluids-thesis）", "L2"),
    "pg25-legacy-model": FluidModel(
        "pg25-legacy-model", "PG25 40 °C（model.py PG25_40，停用）", _const(1022.0, 3900.0, 1.15e-3, 0.452),
        (40.0, 40.0), "C-P07 design/calc/model.py:21 PG25_40；无出处、四项不自洽（PG25物性溯源 §3）", "L6",
        status="deprecated"),
}

ALIASES = {"water": "water-nist", "pg25": "pg25-dowfrost-lc25-tds", "pg25-tds": "pg25-dowfrost-lc25-tds",
           "pg25-guide": "pg25-dow-guide", "pg25-mpg": "pg25-mpg-25.6wt", "water40-legacy": "water-legacy-v20"}


def get(fluid_id: str) -> FluidModel:
    fid = ALIASES.get(fluid_id, fluid_id)
    if fid not in REGISTRY:
        raise KeyError(f"未知工质 {fluid_id}；可选 {sorted(REGISTRY)}")
    return REGISTRY[fid]


def state(fluid_id: str, T_C: float, strict: bool = False) -> FluidState:
    """在温度 T_C 下取物性。常物性条目（legacy）忽略温度但会标注。"""
    m = get(fluid_id)
    if m.T_range[0] == m.T_range[1]:
        st = m.state(m.T_range[0])
        if abs(T_C - m.T_range[0]) > 1e-9:
            st.warnings.append(f"{m.fluid_id} 为 {m.T_range[0]} °C 常物性，请求温度 {T_C} °C 被忽略")
        st.T_C = T_C
        return st
    return m.state(T_C, strict=strict)


def eval_temperature(T_supply: float, dT: float, mode="mean") -> float:
    """物性取值温度：mean = T_supply + ΔT/2（PG25物性溯源 §4.2）；supply = 供液温度；数值 = 指定温度。"""
    if isinstance(mode, (int, float)):
        return float(mode)
    if mode == "supply":
        return T_supply
    if mode == "mean":
        return T_supply + dT / 2.0
    raise ValueError(f"T_eval 只接受 mean / supply / 数值，收到 {mode}")


def table(fluid_id: str, temps=(20, 30, 40, 43, 45, 50)) -> list:
    return [state(fluid_id, float(t)).to_dict() for t in temps]
