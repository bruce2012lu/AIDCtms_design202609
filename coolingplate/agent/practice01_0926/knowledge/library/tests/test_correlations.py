"""correlations.py 测试。参考值是按原文公式逐项手算的结果（计算过程写在用例里），
用来防止转写错误；关联式本身的精度见原文（Wei ±30 %）。"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import correlations as c  # noqa: E402


def test_wei_eq19_hand_value() -> None:
    a, hl, re = 0.3, 0.33, 1024.0
    pre = 5.64 * 0.09 + 0.031 * 0.3 - 0.000632
    expected = pre * 0.33 ** -0.29 * 1024 ** (0.48 * 0.3 ** -0.16)
    assert c.wei2021_nu(a, hl, re) == pytest.approx(expected, rel=1e-12)
    assert expected == pytest.approx(40.2, abs=0.3)


def test_wei_range_flags_for_project_geometry() -> None:
    res = c.wei2021(D_mm=0.5, L_mm=math.sqrt(3.0 * 2.4), H_mm=2.0, Re=478, Pr=4.34, k=0.6285)
    flags = {x["param"]: x["in_range"] for x in res["checks"]}
    assert flags == {"d_i/L": True, "H/L": False, "Re_d": True, "H/d_i": True}
    assert res["all_in_range"] is False
    assert res["Nu_f_water"] == pytest.approx(10.5, abs=0.2)
    assert res["Pr_correction"] < 1.0
    assert res["h_W_m2K"] == pytest.approx(res["Nu_f"] * 0.6285 / 0.0005)


def test_wei_in_range_case_and_pr_flag() -> None:
    res = c.wei2021(D_mm=0.3, L_mm=1.0, H_mm=0.33, Re=1000)
    assert res["all_in_range"] is True
    res_pr = c.wei2021(D_mm=0.3, L_mm=1.0, H_mm=0.33, Re=1000, Pr=7.56)
    assert res_pr["Pr_correction"] == pytest.approx(1.0) and res_pr["all_in_range"] is True
    assert c.wei2021(D_mm=0.3, L_mm=1.0, H_mm=0.33, Re=1000, Pr=10.0)["all_in_range"] is False


def test_robinson_schnitzler_hand_value_and_flags() -> None:
    res = c.robinson_schnitzler(D_mm=1.0, S_mm=5.0, H_mm=2.0, Re=2000, Pr=5.0)
    expected = 23.39 * 2000 ** 0.46 * 5 ** -0.442 * 2 ** -0.00716 * 5 ** 0.4
    assert res["Nu_L"] == pytest.approx(expected, rel=1e-12)
    assert res["all_in_range"] is True
    low = c.robinson_schnitzler(D_mm=0.5, S_mm=2.68, H_mm=2.0, Re=478, Pr=4.34)
    assert {x["param"]: x["in_range"] for x in low["checks"]} == {"Re_d": False, "S/d": True, "H/d": False}
