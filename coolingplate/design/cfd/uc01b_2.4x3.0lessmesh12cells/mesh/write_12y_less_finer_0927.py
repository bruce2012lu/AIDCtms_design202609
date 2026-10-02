# -*- coding: utf-8 -*-
"""12 less units, Z scheme finer_0927.

Copper base (z=-2..0, the only full-copper slab) is 10 uniform
0.20 mm layers: no wall clustering. Fluid Z bands keep the less
boundary layer (n_bl=7, first=0.0025 mm) and double the non-BL
core. Ribs and the orifice plate share those Z stations.
TIM is unchanged. XY is the less 12y mesh.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import write_12y_less as L
import write_12y as W

M = W.M
N_CU_BASE = 10  # 2.00 mm / 0.20 mm
EXPECT_CELLS = 29026560


def z_axis(lv=None):
    if lv is None:
        _, lv = M.active_level()
    h1, nbl, nc = lv["first"], lv["n_bl"], lv["n_core_z"]
    hcap = lv.get("h_core_max", 0.08) / 2.0
    h_tim_cu = min(0.010, max(0.006, (M.Z_CU_BOT - M.Z_TIM_BOT) / max(lv["nz_tim"], 4)))
    n_lid_bl = max(6, nbl - 2)
    n_lid_core = max(4, lv["nz_orif"] // 2) if "h_core_max" in lv else max(6, lv["nz_orif"] // 2)
    z_cu = [M.Z_CU_BOT + (M.Z_IMP - M.Z_CU_BOT) * i / N_CU_BASE for i in range(N_CU_BASE + 1)]

    def core(a, b, n_bl, n_core):
        return M.bl_both(a, b, h1, n_bl, n_core * 2, h_core_max=hcap)

    return (
        M.geo_seg(M.Z_TIM_BOT, M.Z_CU_BOT, lv["nz_tim"], last=h_tim_cu)
        + z_cu[1:]
        + core(M.Z_IMP, M.Z_RIB, nbl, nc)[1:]
        + core(M.Z_RIB, M.Z_LID, nbl, nc)[1:]
        + core(M.Z_LID, M.Z_LIDTOP, n_lid_bl, n_lid_core)[1:]
        + M.geo_seg(M.Z_LIDTOP, M.Z_IN, lv["nz_pl"] * 2)[1:]
    )


def _expect_layers(z):
    edges = (
        ("tim", M.Z_TIM_BOT, M.Z_CU_BOT),
        ("cu_base", M.Z_CU_BOT, M.Z_IMP),
        ("channel", M.Z_IMP, M.Z_RIB),
        ("gap", M.Z_RIB, M.Z_LID),
        ("lid", M.Z_LID, M.Z_LIDTOP),
        ("plenum", M.Z_LIDTOP, M.Z_IN),
    )
    got = {}
    for name, a, b in edges:
        n = 0
        for k in range(len(z) - 1):
            zc = 0.5 * (z[k] + z[k + 1])
            if a - 1e-9 <= zc < b - 1e-12 or (name == "plenum" and a - 1e-9 <= zc <= b + 1e-9):
                n += 1
        got[name] = n
    return got


M.z_axis = z_axis
W.OUT = os.path.join(HERE, "uc01b_cht_less_12y_finer_0927.msh")
W.FACE_DIR = "_faces_12y_finer_0927"
W.META = os.path.join(HERE, "cht_mesh_info_less_12y_finer_0927.txt")
W.HEADER = (
    "UC-01b CHT less x12 finer_0927; n_bl=7 first=0.0025 mm; "
    "fluid non-BL Z x2; Cu base 10 x 0.20 mm uniform; "
    "Y-join uniform 0.05 mm; outer Y fluid=pressure-outlet solid=wall"
)
W.NOTE = (
    "12 connected less jet units along Y; finer_0927; "
    "boundary layer 7 layers, first cell 0.0025 mm; "
    "fluid non-BL Z spacing halved (channel, gap, lid, plenum); "
    "copper base z=-2..0 is 10 uniform 0.20 mm cells, no boundary layer; "
    "Y joins are interface pairs (fluid/copper/tim); "
    "each inlet_jet_XX is one hole; "
    "half-ribs at each Y join are 4 uniform 0.05 mm cells"
)


def _check():
    L._check_y_ends()
    _, lv = M.active_level()
    z = M.z_axis(lv)
    got = _expect_layers(z)
    want = {"tim": 4, "cu_base": 10, "channel": 32, "gap": 39, "lid": 43, "plenum": 16}
    if got != want:
        raise SystemExit(f"Z layers {got} != {want}")
    cu = [v for v in z if -2.0 - 1e-9 <= v <= 1e-9]
    dz = [cu[i + 1] - cu[i] for i in range(len(cu) - 1)]
    if len(dz) != N_CU_BASE or any(abs(d - 0.20) > 1e-9 for d in dz):
        raise SystemExit(f"Cu base is not 10 x 0.20 mm: {dz[:4]} .. {dz[-4:]}")
    print(f"Z layers {got} nz={len(z) - 1} expect cells {EXPECT_CELLS}", flush=True)


if __name__ == "__main__":
    os.environ["UC01B_MESH"] = "less"
    _check()
    W.main()
