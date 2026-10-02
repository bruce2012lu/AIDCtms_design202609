# -*- coding: utf-8 -*-
"""12 less units along Y.

Y-end half-ribs (Y0..-1 and +1..Y1, 0.20 mm) become 4 uniform
0.05 mm cells, matching the join treatment in the ribtop 12y meshes.
Slot BL and the center-slot core stay on the less distribution.
Shared Y faces are conformal interior. Outer Y fluid faces are
pressure outlets; outer Y solid faces are walls.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import write_12y as W

_cu = W.M.cluster_uniform


def cluster_uniform(a, b, h_a, h_b, h_mid, r=W.M.GROWTH_MAX):
    span = abs(b - a)
    y_end = abs(span - 0.20) < 1e-9 and (
        (abs(a - W.M.Y0) < 1e-9 and abs(b + 1.0) < 1e-9)
        or (abs(a - 1.0) < 1e-9 and abs(b - W.M.Y1) < 1e-9)
    )
    if y_end:
        n = 4
        return [a + (b - a) * i / n for i in range(n + 1)]
    return _cu(a, b, h_a, h_b, h_mid, r)


W.M.cluster_uniform = cluster_uniform
# 10 -> 7 BL layers, first cell unchanged. Probe: 28,005,504 cells.
W.M.LEVELS["less"]["n_bl"] = 7
W.JOIN_INTERFACE = True
W.SPLIT_INLETS = True
W.OUT = os.path.join(HERE, "uc01b_cht_less_12y.msh")
W.HEADER = (
    "UC-01b CHT less x12 along Y; n_bl=7 first=0.0025 mm; "
    "Y-join uniform 0.05 mm; outer Y fluid=pressure-outlet solid=wall"
)
W.NOTE = (
    "12 connected less jet units along Y; "
    "boundary layer 7 layers, first cell 0.0025 mm; "
    "Y joins are interface pairs (fluid/copper/tim); "
    "each inlet_jet_XX is one hole; "
    "half-ribs at each Y join are 4 uniform 0.05 mm cells"
)


def _check_y_ends():
    _, lv = W.M.active_level()
    if lv is None or "h_core_max" not in lv:
        raise SystemExit("UC01B_MESH is not the less level")
    ys = W.M.build_xy(lv).ys
    ends = [round(y, 5) for y in ys if y <= -1.0 + 1e-9]
    head = [round(y, 5) for y in ys if y >= 1.0 - 1e-9]
    expect_lo = [-1.2, -1.15, -1.1, -1.05, -1.0]
    expect_hi = [1.0, 1.05, 1.1, 1.15, 1.2]
    if ends[:5] != expect_lo or head[-5:] != expect_hi:
        raise SystemExit(f"Y-end spacing not uniform: {ends[:8]} ... {head[-8:]}")
    print(f"Y stations {len(ys)} ends {ends[:5]} .. {head[-5:]}", flush=True)


if __name__ == "__main__":
    os.environ["UC01B_MESH"] = "less"
    _check_y_ends()
    W.main()
