"""冷板参数模型：加载冻结参数集，反算热工水力派生量。

几何的唯一数据源是 params/*.yaml。本模块只做加载、单位换算和派生量计算，
不做任何设计判断——判断集中在 rules.py，建模集中在 geometry.py。

这样拆是为了让 AI 生成的候选参数集能先过 rules，再进 CAD：
几何一旦画出来就很难看出 0.35 mm 的孔到底能不能钻。
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

LPM_TO_M3S = 1.0e-3 / 60.0
MM2_TO_M2 = 1.0e-6
MM_TO_M = 1.0e-3


class SpecError(ValueError):
    """参数集结构性错误（缺键、类型不对），在任何计算之前抛出。"""


@dataclass(frozen=True)
class Derived:
    """由参数集反算出的热工水力量。

    这些值不写进 yaml，避免和几何脱同步——改了孔径就必须重算孔速。
    """

    jet_count: int
    jet_area_total_mm2: float
    jet_velocity_m_s: float
    jet_reynolds: float
    jet_array_span: tuple[float, float]

    groove_count_total: int
    groove_velocity_m_s: float
    groove_dh_mm: float
    groove_reynolds: float
    groove_segments: int
    groove_segment_length: float

    hbm_channel_velocity_m_s: float
    hbm_channel_span: float

    fluid_temp_rise_k: float
    outlet_temp_c: float

    cavity_thickness: float
    x_budget: float


class Spec:
    """冻结参数集的只读视图。"""

    def __init__(self, raw: dict[str, Any], source: Path | None = None) -> None:
        self.raw = raw
        self.source = source
        for key in ("meta", "material", "plate", "dies", "jets",
                    "gpu_grooves", "hbm", "rib", "hydraulics", "thermal"):
            if key not in raw:
                raise SpecError(f"参数集缺少顶层段: {key}")

    # --- 便捷访问 ---------------------------------------------------------

    @property
    def model(self) -> str:
        return self.raw["meta"]["model"]

    @property
    def plate(self) -> dict[str, Any]:
        return self.raw["plate"]

    @property
    def dies(self) -> list[dict[str, Any]]:
        return self.raw["dies"]["items"]

    @property
    def jets(self) -> dict[str, Any]:
        return self.raw["jets"]

    @property
    def grooves(self) -> dict[str, Any]:
        return self.raw["gpu_grooves"]

    @property
    def hbm(self) -> dict[str, Any]:
        return self.raw["hbm"]

    @property
    def coolant(self) -> dict[str, Any]:
        return self.raw["material"]["coolant"]

    def jet_origin(self, die_id: str) -> tuple[float, float]:
        origins = self.jets["array_origin"]
        if die_id not in origins:
            raise SpecError(f"die {die_id} 没有对应的射流阵首孔坐标")
        x, y = origins[die_id]
        return float(x), float(y)

    def hbm_origins(self) -> list[tuple[float, float]]:
        """八颗 HBM 的左下角坐标，左列自下而上，然后右列。"""
        return [(float(x), float(y))
                for x in self.hbm["columns_x"]
                for y in self.hbm["rows_y"]]

    # --- 派生量 -----------------------------------------------------------

    def derive(self) -> Derived:
        return _derive(self)


def load_spec(path: str | Path) -> Spec:
    p = Path(path)
    with p.open(encoding="utf-8") as fh:
        raw = yaml.safe_load(fh)
    if not isinstance(raw, dict):
        raise SpecError(f"{p} 不是一个 mapping")
    return Spec(raw, source=p)


def _hydraulic_diameter(width: float, depth: float) -> float:
    """矩形流道水力直径 4A/P。"""
    return 4.0 * (width * depth) / (2.0 * (width + depth))


def _segment_grooves(die_x: float, max_len: float, land: float) -> tuple[int, float]:
    """把短槽沿 X 切成 <=max_len 的等长段，段间留铜岛做抽吸位。

    返回 (段数, 单段长度)。段数取最小的能满足 max_len 的整数，
    避免把 27 mm 硬切成一堆 2 mm 碎槽。
    """
    n = max(1, math.ceil((die_x + land) / (max_len + land)))
    seg = (die_x - (n - 1) * land) / n
    while seg > max_len:
        n += 1
        seg = (die_x - (n - 1) * land) / n
    return n, seg


def _derive(spec: Spec) -> Derived:
    plate = spec.plate
    jets = spec.jets
    grooves = spec.grooves
    hbm = spec.hbm
    coolant = spec.coolant
    hyd = spec.raw["hydraulics"]

    rho = float(coolant["density_kg_m3"])
    mu = float(coolant["viscosity_pa_s"])
    cp = float(coolant["cp_j_kgk"])

    n_dies = len(spec.dies)

    # 射流：孔口是限流元件，孔速直接决定驻点换热系数
    d = float(jets["diameter"])
    jet_count = n_dies * int(jets["count_x"]) * int(jets["count_y"])
    hole_area_mm2 = math.pi * (d / 2.0) ** 2
    jet_area_total = jet_count * hole_area_mm2
    q_gpu = float(hyd["split"]["gpu"]) * LPM_TO_M3S
    v_jet = q_gpu / (jet_area_total * MM2_TO_M2)
    re_jet = rho * v_jet * (d * MM_TO_M) / mu

    pitch = float(jets["pitch"])
    span = ((int(jets["count_x"]) - 1) * pitch, (int(jets["count_y"]) - 1) * pitch)

    # GPU 短槽：全部并联，废液必须在 max_length 内离开驻点
    die_x, _die_y = (float(v) for v in spec.raw["dies"]["size"])
    n_seg, seg_len = _segment_grooves(
        die_x, float(grooves["max_length"]), float(grooves["segment_land"])
    )
    g_w, g_d = float(grooves["width"]), float(grooves["depth"])
    groove_count = int(grooves["count_per_die"]) * n_dies
    groove_area_mm2 = g_w * g_d
    v_groove = q_gpu / (groove_count * groove_area_mm2 * MM2_TO_M2)
    dh_groove = _hydraulic_diameter(g_w, g_d)
    re_groove = rho * v_groove * (dh_groove * MM_TO_M) / mu

    # HBM：两侧对称分流，速度必须压在冲蚀帽以下
    n_sides = len(hbm["columns_x"])
    q_hbm_side = float(hyd["split"]["hbm"]) * LPM_TO_M3S / n_sides
    h_w, h_d = float(hbm["channel_width"]), float(hbm["channel_depth"])
    n_ch = int(hbm["channels_per_side"])
    v_hbm = q_hbm_side / (n_ch * h_w * h_d * MM2_TO_M2)
    hbm_span = (n_ch - 1) * float(hbm["channel_pitch"]) + h_w

    # 混合温升是 0 维 P/(m_dot cp)，不是壁温也不是结温
    m_dot = rho * float(hyd["flow_total"]) * LPM_TO_M3S
    power = float(spec.raw["thermal"]["dp_a_guarantee_w"])
    dt = power / (m_dot * cp)

    cavity = (float(plate["base_remaining"]) + g_d
              + float(plate["jet_standoff"]) + float(plate["nozzle_plate_t"]))

    return Derived(
        jet_count=jet_count,
        jet_area_total_mm2=jet_area_total,
        jet_velocity_m_s=v_jet,
        jet_reynolds=re_jet,
        jet_array_span=span,
        groove_count_total=groove_count,
        groove_velocity_m_s=v_groove,
        groove_dh_mm=dh_groove,
        groove_reynolds=re_groove,
        groove_segments=n_seg,
        groove_segment_length=seg_len,
        hbm_channel_velocity_m_s=v_hbm,
        hbm_channel_span=hbm_span,
        fluid_temp_rise_k=dt,
        outlet_temp_c=float(coolant["inlet_temp_c"]) + dt,
        cavity_thickness=cavity,
        x_budget=_x_budget(spec),
    )


def _x_budget(spec: Spec) -> float:
    """沿 X 把边距 / HBM / 缝 / 肋 / die 逐段加起来，与声明板宽比对。

    报告的校核式：5+11+0.5+2+0.5+27+3+27+0.5+2+0.5+11+5 = 95

    右边距按左右对称推出，**不从板宽反推**——反推会让这个校核变成同义反复，
    改了板宽也永远算得通。
    """
    hbm_w = float(spec.hbm["size"][0])
    die_w = float(spec.raw["dies"]["size"][0])
    rib = float(spec.raw["rib"]["width"])
    margin = float(spec.hbm["columns_x"][0])

    die_a_x = float(spec.dies[0]["origin"][0])
    # HBM 右缘到 die 左缘之间是 缝 + 肋 + 缝
    gap_pair = die_a_x - (margin + hbm_w) - rib

    half = margin + hbm_w + gap_pair / 2 + rib + gap_pair / 2 + die_w
    return 2 * half + float(spec.raw["dies"]["hbi_gap"])


def x_symmetry_error(spec: Spec) -> float:
    """右 HBM 列声明位置与左右对称位置之差，用于抓非对称版图。"""
    hbm_w = float(spec.hbm["size"][0])
    margin = float(spec.hbm["columns_x"][0])
    expected = float(spec.plate["width"]) - margin - hbm_w
    return float(spec.hbm["columns_x"][-1]) - expected
