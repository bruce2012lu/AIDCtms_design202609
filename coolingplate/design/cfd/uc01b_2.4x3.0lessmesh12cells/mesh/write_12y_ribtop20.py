# -*- coding: utf-8 -*-
"""12-unit ribtop mesh, about 21.2 million cells. Does not replace older msh files."""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import write_12y as W

RIB = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh_ribtop\mesh"
sys.path.insert(0, RIB)
import write_cht_circle_msh_ribtop as R

R.LEVELS["ribtop20"] = dict(
    first=0.0025, n_bl=7, n_bl_center=4, n_side=7, n_ri=4, n_ro=3,
    nx_slit=4, nx_mid=4, nx_trans=4, ny_half=2, ny_slot=5, ny_rib=3,
    nz_tim=3, nz_cu=4, nz_orif=4, nz_pl=3, n_core_z=3,
    h_orif=0.006, h_core_max=0.32,
    n_core_slot=5, n_core_center=4, n_core_rib=4, n_core_slit=3,
    h_x_mid=0.0225, h_x_trans=0.04,
    n_lid_bl=4, n_lid_core=3,
    y_join_uniform=1, n_y_join=4,
)
os.environ["UC01B_MESH"] = "ribtop20"
W.M = R
W.OUT = os.path.join(HERE, "uc01b_cht_less_ribtop_12y_ch2.msh")
W.main()
