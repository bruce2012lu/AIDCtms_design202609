# -*- coding: utf-8 -*-
"""Temperature contours and velocity vectors from uc01b_R profiles.

Fluid region is the Cartesian hex of write_hex_msh.py (the 116320-cell
uc01b_R mesh): rectangular slots, not a long-edge chevron mask.
"""
from __future__ import annotations

import math
import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.tri import Triangulation

for _fn in ("Microsoft YaHei", "SimHei"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")

# write_hex_msh.py frozen geometry, millimetres
D = 0.40
SO2 = D * math.sqrt(math.pi / 4.0) / 2.0
XL, XR = -1.10, 1.10
Z_RIB, Z_LID, Z_LIDTOP = 1.50, 3.50, 6.0
SLOTS = ((-1.00, -0.60), (-0.20, 0.20), (0.60, 1.00))
NOTE = "旧流体算例 uc01b_R，未收敛，连续性约 0.30；不是正在跑的 v2 共轭"


def in_fluid(x, y, z):
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    z = np.asarray(z, float)
    slit = (x < XL) | (x > XR)
    in_slot = np.zeros(np.shape(x), dtype=bool)
    for a, b in SLOTS:
        in_slot |= (y >= a) & (y <= b)
    in_orif = (np.abs(x) <= SO2) & (np.abs(y) <= SO2)
    out = np.zeros(np.shape(x), dtype=bool)
    m = z < Z_RIB
    out[m] = slit[m] | in_slot[m]
    m = (z >= Z_RIB) & (z < Z_LID)
    out[m] = True
    m = (z >= Z_LID) & (z <= Z_LIDTOP + 1e-6)
    out[m] = slit[m] | in_orif[m]
    m = z > Z_LIDTOP + 1e-6
    out[m] = in_orif[m]
    return out


def load_prof(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    names = re.findall(r"\(([A-Za-z0-9_.-]+)\s", raw)
    blocks = {}
    for m in re.finditer(r"\(([A-Za-z0-9_.-]+)\s+([\s\S]*?)\)", raw):
        key = m.group(1)
        if key in ("x", "y", "z", "temperature", "x-velocity", "y-velocity", "z-velocity", "velocity-magnitude"):
            blocks[key] = np.fromstring(m.group(2), sep=" ")
    need = ("x", "y", "z", "temperature")
    if any(k not in blocks for k in need):
        raise SystemExit("missing fields in %s: %s" % (path, sorted(blocks)))
    n = len(blocks["x"])
    for k, v in blocks.items():
        if len(v) != n:
            raise SystemExit("%s %s len %d != %d" % (path, k, len(v), n))
    return blocks


def mask_tri(tri, a, b, plane):
    t = tri.triangles
    ca = a[t].mean(axis=1)
    cb = b[t].mean(axis=1)
    if plane[0] == "x":
        ok = in_fluid(np.full_like(ca, plane[1]), ca, cb)
    elif plane[0] == "y":
        ok = in_fluid(ca, np.full_like(ca, plane[1]), cb)
    else:
        ok = in_fluid(ca, cb, np.full_like(ca, plane[1]))
    tri.set_mask(~ok)
    return int(np.count_nonzero(~ok)), int(ok.size)


def decimate(a, b, u, v, nu=28, nv=22):
    a = np.asarray(a)
    b = np.asarray(b)
    if a.size < 8:
        return a, b, u, v
    ae = np.linspace(a.min(), a.max(), nu + 1)
    be = np.linspace(b.min(), b.max(), nv + 1)
    ai = np.clip(np.digitize(a, ae) - 1, 0, nu - 1)
    bi = np.clip(np.digitize(b, be) - 1, 0, nv - 1)
    acc_u = np.zeros((nv, nu))
    acc_v = np.zeros((nv, nu))
    cnt = np.zeros((nv, nu))
    for i, j, uu, vv in zip(ai, bi, u, v):
        acc_u[j, i] += uu
        acc_v[j, i] += vv
        cnt[j, i] += 1
    jj, ii = np.nonzero(cnt)
    if ii.size == 0:
        return a, b, u, v
    aa = 0.5 * (ae[ii] + ae[ii + 1])
    bb = 0.5 * (be[jj] + be[jj + 1])
    return aa, bb, acc_u[jj, ii] / cnt[jj, ii], acc_v[jj, ii] / cnt[jj, ii]


def plot_one(path, plane, vec, stem, title):
    d = load_prof(path)
    x = d["x"] * 1e3
    y = d["y"] * 1e3
    z = d["z"] * 1e3
    t = d["temperature"]
    if plane[0] == "x":
        a, b = y, z
        xlab, ylab = "Y mm", "Z mm"
        u = d[vec[0]]
        v = d[vec[1]]
        keep = in_fluid(np.full_like(y, plane[1]), y, z)
    elif plane[0] == "y":
        a, b = x, z
        xlab, ylab = "X mm", "Z mm"
        u = d[vec[0]]
        v = d[vec[1]]
        keep = in_fluid(x, np.full_like(x, plane[1]), z)
    else:
        a, b = x, y
        xlab, ylab = "X mm", "Y mm"
        u = d[vec[0]]
        v = d[vec[1]]
        keep = in_fluid(x, y, np.full_like(x, plane[1]))
    a, b, t, u, v = a[keep], b[keep], t[keep], u[keep], v[keep]
    if a.size < 8:
        print("TOO_FEW", path, a.size)
        return None
    fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=140)
    tri = Triangulation(a, b)
    nbad, nall = mask_tri(tri, a, b, plane)
    tcf = ax.tricontourf(tri, t, levels=18, cmap="inferno")
    cb = fig.colorbar(tcf, ax=ax, shrink=0.86)
    cb.set_label("T (K)")
    aa, bb, uu, vv = decimate(a, b, u, v)
    sp = np.hypot(uu, vv)
    ax.quiver(aa, bb, uu, vv, color="k", angles="xy", scale_units="xy",
              scale=None, width=0.003, headwidth=3.2)
    ax.set_aspect("equal")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title + "\n" + NOTE + "\n箭头 = 剖面内速度分量，来自 uc01b_R.cas.h5 / .dat.h5")
    fig.tight_layout()
    out = os.path.join(FIGS, stem + ".png")
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", out, "n", a.size, "T", float(t.min()), float(t.max()),
          "|Vplane|", float(sp.max()), "masked_tri", nbad, "/", nall)
    return out


def main():
    jobs = (
        ("rvec_z075.prof", ("z", 0.75), ("x-velocity", "y-velocity"),
         "r_z075_TV", "Z=0.75 mm 槽中  温度 + 速度矢量"),
        ("rvec_z01.prof", ("z", 0.10), ("x-velocity", "y-velocity"),
         "r_z01_TV", "Z=0.10 mm 近冲击底  温度 + 速度矢量"),
        ("rvec_x0.prof", ("x", 0.0), ("y-velocity", "z-velocity"),
         "r_x0_TV", "X=0  温度 + 速度矢量"),
        ("rvec_y0.prof", ("y", 0.0), ("x-velocity", "z-velocity"),
         "r_y0_TV", "Y=0  温度 + 速度矢量"),
        ("rvec_xslit.prof", ("x", -1.30), ("y-velocity", "z-velocity"),
         "r_xslit_TV", "X=−1.30 mm 回液缝  温度 + 速度矢量"),
        ("rvec_wall.prof", ("z", 0.0), ("x-velocity", "y-velocity"),
         "r_wall_T", "Z=0 冲击壁 et2d4  温度"),
    )
    for fn, plane, vec, stem, title in jobs:
        path = os.path.join(FIGS, fn)
        if not os.path.isfile(path):
            print("MISSING", path)
            continue
        if stem == "r_wall_T":
            # wall: temperature only if velocity is ~0; still draw arrows from the file
            plot_one(path, plane, vec, stem, title)
        else:
            plot_one(path, plane, vec, stem, title)


if __name__ == "__main__":
    main()
