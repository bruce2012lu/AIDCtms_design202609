# -*- coding: utf-8 -*-
"""UC-01b as Plot3D multi-block (meters). Structured hex regions only."""
from __future__ import annotations
import math
import os

SX, SY = 3.0e-3, 2.4e-3
H_GAP, CH_H, T_LID, H_PL = 2.0e-3, 1.50e-3, 2.5e-3, 2.0e-3
SLIT = 0.40e-3
S_OR = 0.40e-3 * math.sqrt(math.pi / 4.0)
FIRST = 3e-6

X0, X1 = -SX / 2, SX / 2
Y0, Y1 = -SY / 2, SY / 2
XL, XR = X0 + SLIT, X1 - SLIT
Z0, Z1, Z2, Z3, Z4 = 0.0, CH_H, CH_H + H_GAP, CH_H + H_GAP + T_LID, CH_H + H_GAP + T_LID + H_PL


def geo(a, b, n, h1=None):
    if n < 2:
        return [a, b]
    if not h1 or h1 * (n - 1) >= (b - a) * 0.9:
        return [a + (b - a) * i / (n - 1) for i in range(n)]
    # geometric from a
    rlo, rhi = 1.01, 2.4
    for _ in range(40):
        r = 0.5 * (rlo + rhi)
        s = h1 * (r ** (n - 1) - 1) / (r - 1)
        if s < (b - a):
            rlo = r
        else:
            rhi = r
    r = 0.5 * (rlo + rhi)
    xs = [a]
    h = h1
    for _ in range(n - 2):
        xs.append(xs[-1] + h)
        h *= r
    xs.append(b)
    return xs


def block(xs, ys, zs):
    ni, nj, nk = len(xs), len(ys), len(zs)
    xyz = [[], [], []]
    for k in range(nk):
        for j in range(nj):
            for i in range(ni):
                xyz[0].append(xs[i])
                xyz[1].append(ys[j])
                xyz[2].append(zs[k])
    return (ni, nj, nk, xyz)


def main():
    nx_s, ny, nz_s = 9, 21, 16
    xs_slit_l = geo(X0, XL, nx_s)
    xs_slit_r = geo(XR, X1, nx_s)
    xs_core = geo(XL, XR, 25)
    ys = geo(Y0, Y1, ny)
    zs_slot = geo(Z0, Z1, nz_s, FIRST)
    zs_gap = geo(Z1, Z2, 14, FIRST)
    zs_orif = geo(Z2, Z3, 10)
    zs_pl = geo(Z3, Z4, 7)
    zs_slit = zs_slot[:-1] + zs_gap[:-1] + zs_orif  # 0 -> lid top

    # slot Y bands
    ys_m = [y for y in ys if -0.20e-3 - 1e-9 <= y <= 0.20e-3 + 1e-9]
    ys_n = [y for y in ys if -1.00e-3 - 1e-9 <= y <= -0.60e-3 + 1e-9]
    ys_p = [y for y in ys if 0.60e-3 - 1e-9 <= y <= 1.00e-3 + 1e-9]
    if len(ys_m) < 2:
        ys_m = geo(-0.20e-3, 0.20e-3, 8)
    if len(ys_n) < 2:
        ys_n = geo(-1.00e-3, -0.60e-3, 8)
    if len(ys_p) < 2:
        ys_p = geo(0.60e-3, 1.00e-3, 8)

    xo = geo(-S_OR / 2, S_OR / 2, 9)
    yo = geo(-S_OR / 2, S_OR / 2, 9)

    blocks = [
        block(xs_slit_l, ys, zs_slit),          # -X slit
        block(xs_slit_r, ys, zs_slit),          # +X slit
        block(xs_core, ys_n, zs_slot),          # side slot -
        block(xs_core, ys_m, zs_slot),          # center slot
        block(xs_core, ys_p, zs_slot),          # side slot +
        block(xs_core, ys, zs_gap),             # gap
        block(xo, yo, zs_orif),                 # orifice
        block(xo, yo, zs_pl),                   # plenum
    ]

    here = os.path.dirname(os.path.abspath(__file__))
    xyzp = os.path.join(here, "uc01b.xyz")
    with open(xyzp, "w", encoding="ascii", newline="\n") as f:
        f.write(f"{len(blocks)}\n")
        for ni, nj, nk, _ in blocks:
            f.write(f"{ni} {nj} {nk}\n")
        for ni, nj, nk, xyz in blocks:
            n = ni * nj * nk
            for c in range(3):
                for i, v in enumerate(xyz[c]):
                    f.write(f"{v:16.8e}")
                    if (i + 1) % 4 == 0 or i + 1 == n:
                        f.write("\n")
                    else:
                        f.write(" ")
    ncell = sum((b[0] - 1) * (b[1] - 1) * (b[2] - 1) for b in blocks)
    print("WROTE", xyzp, "blocks", len(blocks), "hex_cells", ncell)


if __name__ == "__main__":
    main()
