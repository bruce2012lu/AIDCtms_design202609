# -*- coding: utf-8 -*-
"""Cell-count sweep for a coarser less boundary layer. No mesh written."""
import os
import sys

SRC = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh\mesh"
sys.path.insert(0, SRC)
os.environ["UC01B_MESH"] = "less"
import write_cht_circle_msh as M

_cu = M.cluster_uniform


def cluster_uniform(a, b, h_a, h_b, h_mid, r=M.GROWTH_MAX):
    span = abs(b - a)
    y_end = abs(span - 0.20) < 1e-9 and (
        (abs(a - M.Y0) < 1e-9 and abs(b + 1.0) < 1e-9)
        or (abs(a - 1.0) < 1e-9 and abs(b - M.Y1) < 1e-9)
    )
    if y_end:
        return [a + (b - a) * i / 4 for i in range(5)]
    return _cu(a, b, h_a, h_b, h_mid, r)


M.cluster_uniform = cluster_uniform
BASE = dict(M.LEVELS["less"])


def count(lv):
    xy = M.build_xy(lv)
    z = M.z_axis(lv)
    nz = len(z) - 1
    n = nfl = ncu = nt = 0
    for iq, (n0, n1, n2, n3) in enumerate(xy.quads):
        p0, p1, p2, p3 = xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3]
        xc = 0.25 * (p0[0] + p1[0] + p2[0] + p3[0])
        yc = 0.25 * (p0[1] + p1[1] + p2[1] + p3[1])
        for k in range(nz):
            zn = M.zone_of(xc, yc, 0.5 * (z[k] + z[k + 1]))
            if zn:
                n += 1
                if zn == M.FLUID:
                    nfl += 1
                elif zn == M.CU:
                    ncu += 1
                else:
                    nt += 1
    print(
        "n_bl=%s first=%s quads=%d nz=%d one=%d x12=%d fl=%d cu=%d tim=%d"
        % (lv["n_bl"], lv["first"], len(xy.quads), nz, n, n * 12, nfl, ncu, nt),
        flush=True,
    )


if __name__ == "__main__":
    for nbl, first in (
        (10, 0.0025),
        (8, 0.0025),
        (7, 0.0025),
        (6, 0.0025),
        (5, 0.0025),
        (6, 0.005),
        (5, 0.005),
        (4, 0.005),
        (5, 0.008),
    ):
        lv = dict(BASE)
        lv["n_bl"] = nbl
        lv["first"] = first
        count(lv)
