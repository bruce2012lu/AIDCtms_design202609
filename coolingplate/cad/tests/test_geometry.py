"""几何回归：体积与包围盒必须等于解析值。

体积是最省的正确性探针 —— 少切一排槽或多钻一圈孔，体积立刻对不上，
而肉眼看渲染图基本看不出来。
"""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from coldplate import geometry, load_spec

PARAMS = Path(__file__).resolve().parent.parent / "params" / "cp_b300_jm01.yaml"


@pytest.fixture(scope="module")
def built():
    spec = load_spec(PARAMS)
    d = spec.derive()
    return spec, d, geometry.build(spec, d)


def test_base_plate_volume_matches_analytic(built):
    spec, d, res = built
    pw, ph = float(spec.plate["width"]), float(spec.plate["height"])
    base_t = float(spec.plate["base_plate_t"])
    g = spec.grooves

    solid = pw * ph * base_t
    gpu_grooves = (len(spec.dies) * int(g["count_per_die"]) * d.groove_segments
                   * d.groove_segment_length * float(g["width"]) * float(g["depth"]))

    hbm = spec.hbm
    col_len = float(hbm["rows_y"][-1]) + float(hbm["size"][1]) - float(hbm["rows_y"][0])
    hbm_channels = (len(hbm["columns_x"]) * int(hbm["channels_per_side"])
                    * float(hbm["channel_width"]) * col_len
                    * float(hbm["channel_depth"]))

    ribs = 2 * float(spec.raw["rib"]["width"]) * ph * float(spec.plate["jet_standoff"])

    expected = solid - gpu_grooves - hbm_channels + ribs
    assert res.base_plate.volume == pytest.approx(expected, rel=1e-9)


def test_nozzle_plate_volume_matches_analytic(built):
    spec, d, res = built
    pw, ph = float(spec.plate["width"]), float(spec.plate["height"])
    t = float(spec.plate["nozzle_plate_t"])
    jets = spec.jets
    nx, ny = int(jets["count_x"]), int(jets["count_y"])

    jet_vol = d.jet_count * math.pi * (float(jets["diameter"]) / 2) ** 2 * t
    n_suction = len(spec.dies) * (nx - 1) * (ny - 1)
    suction_vol = n_suction * math.pi * (float(jets["suction_diameter"]) / 2) ** 2 * t

    expected = pw * ph * t - jet_vol - suction_vol
    assert res.nozzle_plate.volume == pytest.approx(expected, rel=1e-6)
    assert n_suction == 98


def test_seal_frame_volume_matches_analytic(built):
    spec, _d, res = built
    pw, ph = float(spec.plate["width"]), float(spec.plate["height"])
    t = float(spec.plate["braze_seam"])
    rib = float(spec.raw["rib"]["width"])
    expected = pw * ph * t - (pw - 2 * rib) * (ph - 2 * rib) * t
    assert res.seal_frame.volume == pytest.approx(expected, rel=1e-9)


def test_assembly_bbox_equals_declared_envelope(built):
    spec, _d, res = built
    bb = geometry.assemble(spec, res).bounding_box()
    assert bb.size.X == pytest.approx(float(spec.plate["width"]), abs=1e-6)
    assert bb.size.Y == pytest.approx(float(spec.plate["height"]), abs=1e-6)
    assert bb.size.Z == pytest.approx(float(spec.plate["thickness"]), abs=1e-6)
    assert bb.min.X == pytest.approx(0.0, abs=1e-6)
    assert bb.min.Y == pytest.approx(0.0, abs=1e-6)
    assert bb.min.Z == pytest.approx(0.0, abs=1e-6)


def test_parts_still_exportable_after_assembly(built):
    """assemble() 必须是非破坏性的，否则单零件 STEP 导出会失败。"""
    spec, _d, res = built
    geometry.assemble(spec, res)
    for part in res.parts.values():
        assert part.parent is None


def test_groove_segments_respect_max_length(built):
    spec, d, _res = built
    assert d.groove_segment_length <= float(spec.grooves["max_length"]) + 1e-9
    total = (d.groove_segments * d.groove_segment_length
             + (d.groove_segments - 1) * float(spec.grooves["segment_land"]))
    assert total == pytest.approx(float(spec.raw["dies"]["size"][0]), abs=1e-9)
