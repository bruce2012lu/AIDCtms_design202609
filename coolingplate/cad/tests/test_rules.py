"""规则引擎回归：正样本对账 + 负样本必须被拦住。

负样本是这套能力的重点。AI 改参数时最危险的不是画不出来，而是画得出来、
看着还挺合理，但钻头做不出、过滤挡不住、压装会压裂 HBM。
"""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

from coldplate import load_spec, validate
from coldplate.model import Spec

PARAMS = Path(__file__).resolve().parent.parent / "params" / "cp_b300_jm01.yaml"


@pytest.fixture
def raw() -> dict:
    return copy.deepcopy(load_spec(PARAMS).raw)


def codes(spec: Spec, level: str) -> set[str]:
    return {f.code for f in validate(spec) if f.level == level}


# --- 正样本 ---------------------------------------------------------------

def test_frozen_set_is_clean():
    spec = load_spec(PARAMS)
    findings = validate(spec)
    assert not [f for f in findings if f.level == "ERROR"]
    assert not [f for f in findings if f.level == "WARN"]


def test_reference_cross_check_matches_report():
    """12 项派生量必须与设计报告 v1.0 公布的数字一致。"""
    spec = load_spec(PARAMS)
    infos = [f for f in validate(spec) if f.level == "INFO"]
    assert len(infos) == 12
    assert all(c.startswith("REF_") for c in {f.code for f in infos})


def test_derived_physics_reproduces_report():
    d = load_spec(PARAMS).derive()
    assert d.jet_count == 128
    assert d.groove_count_total == 60
    assert d.jet_velocity_m_s == pytest.approx(1.06, abs=0.01)
    assert d.jet_reynolds == pytest.approx(810, abs=10)
    assert d.groove_velocity_m_s == pytest.approx(0.74, abs=0.01)
    assert d.groove_reynolds == pytest.approx(710, abs=5)
    assert d.hbm_channel_velocity_m_s == pytest.approx(0.46, abs=0.01)
    assert d.fluid_temp_rise_k == pytest.approx(7.9, abs=0.1)
    assert d.cavity_thickness == pytest.approx(8.0)
    assert d.x_budget == pytest.approx(95.0)
    assert d.groove_segment_length <= 8.0


# --- 负样本：工艺 ---------------------------------------------------------

def test_jet_below_drill_limit_rejected(raw):
    raw["jets"]["diameter"] = 0.20
    assert "DRILL_DIA" in codes(Spec(raw), "ERROR")


def test_groove_rib_too_thin_rejected(raw):
    raw["gpu_grooves"]["pitch"] = 0.50   # 齿壁只剩 0.10
    assert "GROOVE_RIB" in codes(Spec(raw), "ERROR")


def test_groove_aspect_too_high_rejected(raw):
    raw["gpu_grooves"]["width"] = 0.20   # 深宽比 7.5，铲齿会倒齿
    assert "GROOVE_ASPECT" in codes(Spec(raw), "ERROR")


def test_filtration_coarser_than_tenth_of_hole_rejected(raw):
    raw["hydraulics"]["filtration_um"] = 100.0
    assert "FILTRATION" in codes(Spec(raw), "ERROR")


def test_base_remaining_below_floor_rejected(raw):
    raw["plate"]["base_remaining"] = 1.5
    raw["plate"]["base_plate_t"] = 3.0   # 保持底板厚度自洽，只留余铜违规
    assert "BASE_REMAINING" in codes(Spec(raw), "ERROR")


# --- 负样本：尺寸链 -------------------------------------------------------

def test_thickness_stack_must_close(raw):
    raw["plate"]["thickness"] = 9.0      # 腔 8.0 + 钎缝 0.5 != 9.0
    assert "Z_STACK" in codes(Spec(raw), "ERROR")


def test_x_budget_must_close(raw):
    raw["plate"]["width"] = 100.0
    assert "X_BUDGET" in codes(Spec(raw), "ERROR")


def test_base_plate_thickness_must_match_sum(raw):
    raw["plate"]["base_plate_t"] = 4.0
    assert "BASE_PLATE" in codes(Spec(raw), "ERROR")


def test_asymmetric_hbm_columns_rejected(raw):
    raw["hbm"]["columns_x"] = [5.0, 77.0]   # 右列内移 2 mm，压装会偏载
    assert "X_SYMMETRY" in codes(Spec(raw), "ERROR")


def test_x_budget_is_not_tautological(raw):
    """尺寸链累加必须独立于声明板宽，否则这条校核形同虚设。"""
    from coldplate.model import _x_budget
    before = _x_budget(Spec(raw))
    raw["plate"]["width"] = 120.0
    assert _x_budget(Spec(raw)) == before


# --- 负样本：版图 ---------------------------------------------------------

def test_jet_array_off_die_rejected(raw):
    raw["jets"]["array_origin"]["Die-A"] = [10.0, 27.0]  # 阵面跑出 die 投影
    assert "JET_ARRAY_OFF_DIE" in codes(Spec(raw), "ERROR")


def test_denser_array_overflowing_die_rejected(raw):
    raw["jets"]["count_x"] = 12          # (12-1)*3 = 33 > die 宽 27
    assert "JET_ARRAY_OFF_DIE" in codes(Spec(raw), "ERROR")


def test_groove_bank_wider_than_die_rejected(raw):
    raw["gpu_grooves"]["count_per_die"] = 60   # 跨度 47.6 > die 高 28
    assert "GROOVE_SPAN" in codes(Spec(raw), "ERROR")


def test_hbm_channel_bank_wider_than_stack_rejected(raw):
    raw["hbm"]["channels_per_side"] = 16       # 跨度 20.1 > HBM 宽 11
    assert "HBM_CHANNEL_SPAN" in codes(Spec(raw), "ERROR")


def test_hbi_gap_inconsistency_rejected(raw):
    raw["dies"]["hbi_gap"] = 5.0               # 与两 die 实际间距 3.0 不符
    assert "HBI_GAP" in codes(Spec(raw), "ERROR")


# --- 负样本：热工水力 -----------------------------------------------------

def test_flow_split_must_sum(raw):
    raw["hydraulics"]["split"]["hbm"] = 0.60
    assert "FLOW_SPLIT" in codes(Spec(raw), "ERROR")


def test_power_split_must_sum(raw):
    raw["thermal"]["power_split_dp_a"]["io_other"] = 100.0
    assert "POWER_SPLIT" in codes(Spec(raw), "ERROR")


def test_hbm_erosion_cap_enforced(raw):
    """把 HBM 槽数砍半，流速翻倍越过冲蚀帽。"""
    raw["hbm"]["channels_per_side"] = 4
    assert "HBM_EROSION" in codes(Spec(raw), "ERROR")


def test_sd_ratio_outside_literature_window_warns(raw):
    raw["jets"]["pitch"] = 6.0           # S/D = 12，超出 4-8
    assert "SD_RATIO" in codes(Spec(raw), "WARN")


def test_hd_ratio_outside_literature_window_warns(raw):
    raw["plate"]["jet_standoff"] = 5.0   # H/D = 10，超出 2-6
    assert "HD_RATIO" in codes(Spec(raw), "WARN")


def test_dp_window_must_be_monotonic(raw):
    raw["hydraulics"]["dp_sample_target"] = 25.0   # 超过上限 20
    assert "DP_WINDOW" in codes(Spec(raw), "ERROR")


# --- 参数漂移必须报警 -----------------------------------------------------

def test_drift_from_report_raises_warning(raw):
    """改了流量但没更新报告 —— 对账项必须变 WARN，而不是静默通过。"""
    raw["hydraulics"]["flow_total"] = 3.0
    raw["hydraulics"]["split"]["gpu"] = 2.4
    raw["hydraulics"]["split"]["hbm"] = 0.6
    warns = codes(Spec(raw), "WARN")
    assert "REF_JET_VELOCITY_M_S" in warns
    assert "REF_FLUID_TEMP_RISE_K" in warns
