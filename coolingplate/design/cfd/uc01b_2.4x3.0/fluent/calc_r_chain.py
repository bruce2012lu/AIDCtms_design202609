# -*- coding: utf-8 -*-
"""UC-01b resistance chain from Fluent prints + model.py."""
from __future__ import annotations

import sys

sys.path.insert(0, r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\calc")
import model as M  # noqa: E402

SX, SY = 3.0e-3, 2.4e-3
A_CELL = SX * SY
A = M.solve("DP-A")
QPP = A["q_die"] * 1e4
P_CELL = QPP * A_CELL
SCALE = A_CELL / M.A_2DIE
R_WALL_CELL = (M.GEO["base_cu"] * 1e-3) / (M.K_CU * A_CELL)

T_IN, T_OUT, T_W, T_C = 313.15, 316.30993, 354.34595, 357.27701
H_PRINT, QPP_PRINT = 15021.532, 569029.3
P_IN, P_OUT = 2462.5898, 0.0


def main():
    dT_cu = T_C - T_W
    dT_conv = T_W - T_IN
    Tf_bulk = 0.5 * (T_IN + T_OUT)
    R_conv_cell = dT_conv / P_CELL
    R_conv_2die = R_conv_cell * SCALE
    R_conv_b_cell = (T_W - Tf_bulk) / P_CELL
    R_conv_b_2die = R_conv_b_cell * SCALE
    print(f"q''={QPP:.6f} W/m2 = {A['q_die']:.6f} W/cm2  P_cell={P_CELL:.6f} W")
    print(f"scale A_cell/A_2DIE={SCALE:.6f}  Neq={1/SCALE:.1f}")
    print(f"T_in={T_IN} T_out={T_OUT} T_w={T_W} T_c={T_C} dT_cu={dT_cu:.4f}")
    print(f"R_conv_cell (Tw-Tin)/P={R_conv_cell:.6f}  2die={R_conv_2die:.6f}")
    print(f"R_conv_cell (Tw-Tfbulk)/P={R_conv_b_cell:.6f}  2die={R_conv_b_2die:.6f}")
    print(f"dP={P_IN-P_OUT:.4f} Pa  h={H_PRINT}  q''_print={QPP_PRINT}")
    for tag, rtim, rpkg in (("lo", M.R_TIM2[0], M.R_PKG[0]), ("hi", M.R_TIM2[1], M.R_PKG[1])):
        T_j = T_C + QPP * (rtim + rpkg) * M.A_2DIE
        rcin = rtim + M.R_WALL + R_conv_2die
        rjin = rpkg + rcin
        print(f" {tag}: T_j={T_j:.4f} R_c-in_2die={rcin:.6f} R_j-in_2die={rjin:.6f}")


if __name__ == "__main__":
    main()
