# -*- coding: utf-8 -*-
"""Count one ribtop unit at the 20M-class spacing. No mesh file written."""
import os
import sys

SRC = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh_ribtop\mesh"
sys.path.insert(0, SRC)
os.environ["UC01B_MESH"] = "m20"
import write_cht_circle_msh_ribtop as M

M.LEVELS["m20"] = dict(
    first=0.0025, n_bl=7, n_bl_center=4, n_side=7, n_ri=4, n_ro=3,
    nx_slit=4, nx_mid=4, nx_trans=4, ny_half=2, ny_slot=5, ny_rib=3,
    nz_tim=3, nz_cu=4, nz_orif=4, nz_pl=3, n_core_z=3,
    h_orif=0.006, h_core_max=0.32,
    n_core_slot=5, n_core_center=4, n_core_rib=4, n_core_slit=3,
    h_x_mid=0.0225, h_x_trans=0.04,
    n_lid_bl=4, n_lid_core=3,
    y_join_uniform=1, n_y_join=4,
)
_, lv = M.active_level()
xy = M.build_xy(lv)
z = M.z_axis(lv)
nz = len(z) - 1
n = n_fl = n_cu = n_tim = 0
for iq, (n0, n1, n2, n3) in enumerate(xy.quads):
    p0, p1, p2, p3 = xy.xy[n0], xy.xy[n1], xy.xy[n2], xy.xy[n3]
    xc = 0.25 * (p0[0] + p1[0] + p2[0] + p3[0])
    yc = 0.25 * (p0[1] + p1[1] + p2[1] + p3[1])
    for k in range(nz):
        zc = 0.5 * (z[k] + z[k + 1])
        zn = M.zone_of(xc, yc, zc)
        if zn:
            n += 1
            if zn == M.FLUID:
                n_fl += 1
            elif zn == M.CU:
                n_cu += 1
            else:
                n_tim += 1
print(f"quads {len(xy.quads)} nz {nz} one {n} fl {n_fl} cu {n_cu} tim {n_tim} cells_12 {n * 12}", flush=True)
