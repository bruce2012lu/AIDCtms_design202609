# -*- coding: utf-8 -*-
"""Y-mirror average of the iter-529 cell field. Writes a new dat only."""
import os
import shutil
import numpy as np
import h5py

ROOT = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0"
CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
SRC = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")
DST = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_sym2_init.dat.h5")

with h5py.File(CAS, "r") as fc, h5py.File(SRC, "r") as fd:
    coords = np.asarray(fc["meshes/1/nodes/coords/1"][:], np.float64)
    fn = np.asarray(fc["meshes/1/faces/nodes/1/nodes"][:], np.uint32).reshape(-1, 4) - 1
    c0 = np.asarray(fc["meshes/1/faces/c0/1"][:], np.int64)
    cells = fd["results/1/phase-1/cells"]
    print("CELL_KEYS", list(cells.keys()))
    for name in ("SV_T", "SV_U", "SV_V", "SV_W", "SV_P", "SV_K", "SV_O"):
        g = cells[name]
        for k in g.keys():
            a = g[k]
            print(name, k, a.shape, a.dtype)

ncell = int(max(c0.max(), 1))
print("ncell_from_c0", ncell, "nodes", coords.shape[0], "faces", fn.shape[0])
