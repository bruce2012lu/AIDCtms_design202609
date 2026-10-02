# -*- coding: utf-8 -*-
"""All current-result contours from uc01b_cht_v2_n216_q105. Does not write v2cur_*."""
import os
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import Normalize
import plot_v2_scales as p

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p.CAS = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105.cas.h5")
p.DAT = os.path.join(ROOT, "fluent", "uc01b_cht_v2_n216_q105.dat.h5")
p.NOTE = "iter 8587  n216_q105"

KEEP = {"n216_i8587_wall_heat_T", "n216_i8587_ztim_mid_T"}
_save = p.save
_plot = p.plot_scalar_plane


def save(fig, stem):
    if stem.startswith("v2cur_"):
        stem = "n216_i8587_" + stem[len("v2cur_"):]
    if stem in KEEP:
        plt.close(fig)
        print("KEEP", stem)
        return None
    return _save(fig, stem)


def plot_scalar_plane(stem, title, xlabel, ylabel, groups, caption_bits):
    title = "iter 8587  " + title
    for g in groups:
        vals = g.get("values")
        if vals is None or getattr(vals, "size", 0) == 0:
            continue
        lo = float(np.nanmin(vals))
        hi = float(np.nanmax(vals))
        if hi - lo < 1.0 and lo > 250:
            mid = 0.5 * (lo + hi)
            g["norm"] = Normalize(mid - 1.0, mid + 1.0)
            g["step"] = 0.5
            g["label"] = g.get("label", "T (K)") + "  绝对"
    if caption_bits:
        caption_bits = "iter 8587 n216_q105。 " + caption_bits
    return _plot(stem, title, xlabel, ylabel, groups, caption_bits)


p.save = save
p.plot_scalar_plane = plot_scalar_plane

mdot = 1.2249382716049385e-4
rho = 992.2
mu = 6.53e-4
D = 0.40e-3
area = np.pi * D * D / 4.0
U = mdot / (rho * area)
Re = rho * U * D / mu
print("U", U, "Re_D", Re)

p.main()
