# -*- coding: utf-8 -*-
"""Y-mirror average of iter-529 cells. New dat only; source files untouched."""
import os
import shutil
import numpy as np
import h5py
import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.cas.h5")
SRC = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105_sym.dat.h5")
DST = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_sym2_init.dat.h5")
p.CAS = CAS
p.DAT = SRC

print("copy", flush=True)
shutil.copy2(SRC, DST)

with h5py.File(CAS, "r") as fc:
    coords = np.asarray(fc["meshes/1/nodes/coords/1"][:], np.float64)
    fn = np.asarray(fc["meshes/1/faces/nodes/1/nodes"][:], np.uint32).reshape(-1, 4).astype(np.int64) - 1
    c0 = np.asarray(fc["meshes/1/faces/c0/1"][:], np.int64)
    c1raw = np.asarray(fc["meshes/1/faces/c1/1"][:], np.int64)

nface = fn.shape[0]
ncell = 4472280
acc = np.zeros((ncell, 3), np.float64)
cnt = np.zeros(ncell, np.int32)
step = 400000
for a in range(0, nface, step):
    b = min(a + step, nface)
    idx = np.arange(a, b)
    fc = coords[fn[a:b]].mean(axis=1)
    id0 = c0[a:b]
    m = (id0 >= 1) & (id0 <= ncell)
    np.add.at(acc, id0[m] - 1, fc[m])
    np.add.at(cnt, id0[m] - 1, 1)
    id1 = p.c1_of(idx, c1raw)
    m = (id1 >= 1) & (id1 <= ncell)
    np.add.at(acc, id1[m] - 1, fc[m])
    np.add.at(cnt, id1[m] - 1, 1)
    print("faces", b, flush=True)
ok = cnt > 0
cent = np.zeros_like(acc)
cent[ok] = acc[ok] / cnt[ok, None]
print("cells_with_cent", int(ok.sum()), flush=True)

key = np.round(cent / 2e-6).astype(np.int64)
lookup = {}
for i in np.flatnonzero(ok):
    lookup[(int(key[i, 0]), int(key[i, 1]), int(key[i, 2]))] = int(i)

pairs = []
for i in np.flatnonzero(ok & (cent[:, 1] > 5e-5)):
    mk = (int(key[i, 0]), int(-key[i, 1]), int(key[i, 2]))
    j = lookup.get(mk)
    if j is None or j == i:
        continue
    if abs(cent[j, 1] + cent[i, 1]) > 5e-6:
        continue
    if abs(cent[j, 0] - cent[i, 0]) > 5e-6 or abs(cent[j, 2] - cent[i, 2]) > 5e-6:
        continue
    pairs.append((i, j))
print("pairs", len(pairs), flush=True)

pi = np.array([a for a, _ in pairs], np.int64)
pj = np.array([b for _, b in pairs], np.int64)

with h5py.File(DST, "r+") as fd:
    cells = fd["results/1/phase-1/cells"]

    def even(name, n):
        g = cells[name]["1"]
        a = np.asarray(g[:])
        ii, jj = pi[pi < n], pj[pj < n]
        # pairs are stored with i having +Y; both must be in range
        m = (pi < n) & (pj < n)
        ii, jj = pi[m], pj[m]
        avg = 0.5 * (a[ii] + a[jj])
        a[ii] = avg
        a[jj] = avg
        g[:] = a
        print(name, "even", int(m.sum()), flush=True)
        return a

    def odd_v():
        g = cells["SV_V"]["1"]
        a = np.asarray(g[:])
        n = a.shape[0]
        m = (pi < n) & (pj < n)
        ii, jj = pi[m], pj[m]
        vp = 0.5 * (a[ii] - a[jj])
        a[ii] = vp
        a[jj] = -vp
        # cells on the plane
        plane = np.flatnonzero(ok[:n] & (np.abs(cent[:n, 1]) <= 5e-5))
        a[plane] = 0.0
        g[:] = a
        print("SV_V odd", int(m.sum()), "plane0", int(plane.size), flush=True)

    even("SV_T", 4472280)
    for name in ("SV_U", "SV_W", "SV_P", "SV_K", "SV_O"):
        even(name, 2760804)
    odd_v()

print("WROTE", DST)
