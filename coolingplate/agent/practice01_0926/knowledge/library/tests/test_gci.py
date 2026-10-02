"""gci.py 测试。参考值为 Celik et al. 2008 Table 1 第 1 列（二维算例，φ 为无量纲再附着长度）：
N = 18000 / 8000 / 4500，φ = 6.063 / 5.972 / 5.863，
r21 = 1.5，r32 = 1.333，p = 1.53，φ_ext21 = 6.1685，e_a21 = 1.5 %，e_ext21 = 1.7 %，GCI_fine21 = 2.2 %。
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import gci  # noqa: E402


def test_celik_table1_column1() -> None:
    hs = [gci.rep_h(n, dim=2) for n in (18000, 8000, 4500)]
    r21, r32 = hs[1] / hs[0], hs[2] / hs[1]
    assert r21 == pytest.approx(1.5, abs=0.01)
    assert r32 == pytest.approx(1.333, abs=0.01)
    res = gci.gci3(6.063, 5.972, 5.863, r21, r32)
    assert res["p"] == pytest.approx(1.53, abs=0.02)
    assert res["phi_ext21"] == pytest.approx(6.1685, abs=0.002)
    assert res["ea21"] * 100 == pytest.approx(1.5, abs=0.05)
    assert res["eext21"] * 100 == pytest.approx(1.7, abs=0.05)
    assert res["gci_fine21"] * 100 == pytest.approx(2.2, abs=0.05)
    assert res["oscillatory"] is False


@pytest.mark.parametrize("phi, r, p, ext, ea, eext, g, osc", [
    ((10.7880, 10.7250, 10.6050), (2.0, 2.143), 0.75, 10.8801, 0.6, 0.9, 1.1, False),
    ((6.0042, 5.9624, 6.0909), (2.0, 2.143), 1.51, 6.0269, 0.7, 0.4, 0.5, True),
])
def test_celik_table1_columns2_3(phi, r, p, ext, ea, eext, g, osc) -> None:
    """Celik 2008 p.9 Table 1 第 2 列（p < 1）与第 3 列（振荡收敛）。原表百分数保留一位小数。"""
    res = gci.gci3(*phi, *r)
    assert res["p"] == pytest.approx(p, abs=0.02)
    assert res["phi_ext21"] == pytest.approx(ext, abs=0.002)
    assert res["ea21"] * 100 == pytest.approx(ea, abs=0.06)
    assert res["eext21"] * 100 == pytest.approx(eext, abs=0.06)
    assert res["gci_fine21"] * 100 == pytest.approx(g, abs=0.06)
    assert res["oscillatory"] is osc


def test_exact_second_order_recovers_p2_and_limit() -> None:
    exact, c = 10.0, 0.4
    h = [1.0, 2.0, 4.0]
    phi = [exact + c * x ** 2 for x in h]
    res = gci.gci3(*phi, 2.0, 2.0)
    assert res["p"] == pytest.approx(2.0, abs=1e-6)
    assert res["phi_ext21"] == pytest.approx(exact, abs=1e-9)
    assert res["asymptotic_ratio"] == pytest.approx(1.0, abs=1e-6)


def test_oscillatory_flag() -> None:
    res = gci.gci3(1.00, 1.02, 0.99, 1.5, 1.5)
    assert res["oscillatory"] is True


def test_identical_meshes_raise() -> None:
    with pytest.raises(ValueError):
        gci.gci3(1.0, 1.0, 1.1, 1.5, 1.5)


def test_two_grid_conservative() -> None:
    res = gci.gci2(341.385, 342.096, 1.3, 2.0)
    expected = 3.0 * abs((341.385 - 342.096) / 341.385) / (1.3 ** 2 - 1)
    assert math.isclose(res["gci_fine21"], expected)
    assert "warning" in res
