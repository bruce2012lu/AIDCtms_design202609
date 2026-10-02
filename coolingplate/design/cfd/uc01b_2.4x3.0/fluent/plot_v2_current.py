# -*- coding: utf-8 -*-
"""Temperature contours and velocity vectors from the v2 intermediate export.

Points come from Fluent iso-surfaces on uc01b_cht_v2_current (circular
orifice mesh). No square-hole mask from the retired uc01b_R mesh.
"""
from __future__ import annotations

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
NOTE = "当前中间结果，不是收敛解"


def load_prof(path):
    raw = open(path, encoding="utf-8", errors="replace").read()
    blocks = {}
    for m in re.finditer(r"\(([A-Za-z0-9_.-]+)\s+([\s\S]*?)\)", raw):
        key = m.group(1)
        if key in ("x", "y", "z", "temperature", "x-velocity", "y-velocity", "z-velocity"):
            blocks[key] = np.fromstring(m.group(2), sep=" ")
    need = ("x", "y", "z", "temperature")
    if any(k not in blocks for k in need):
        raise SystemExit("missing fields in %s: %s" % (path, sorted(blocks)))
    n = len(blocks["x"])
    for k, v in blocks.items():
        if len(v) != n:
            raise SystemExit("%s %s len %d != %d" % (path, k, len(v), n))
    return blocks


def mask_long_edges(tri, a, b):
    t = tri.triangles
    pa = np.column_stack((a, b))
    e01 = np.linalg.norm(pa[t[:, 0]] - pa[t[:, 1]], axis=1)
    e12 = np.linalg.norm(pa[t[:, 1]] - pa[t[:, 2]], axis=1)
    e20 = np.linalg.norm(pa[t[:, 2]] - pa[t[:, 0]], axis=1)
    longest = np.maximum(np.maximum(e01, e12), e20)
    # Keep triangles at the scale of neighbouring mesh nodes.
    # A random subset of nearest distances sets the cutoff.
    n_s = min(800, a.size)
    idx = np.linspace(0, a.size - 1, n_s).astype(int)
    sample = pa[idx]
    if sample.shape[0] > 2:
        dist = np.linalg.norm(sample[:, None, :] - sample[None, :, :], axis=2)
        np.fill_diagonal(dist, np.inf)
        med = float(np.median(dist.min(axis=1)))
    else:
        med = float(np.median(longest))
    cutoff = max(med * 12.0, 0.20)
    tri.set_mask(longest > cutoff)
    return int(np.count_nonzero(~tri.mask)), int(tri.mask.size), cutoff


def decimate(a, b, u, v, nu=36, nv=28):
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


def plot_one(path, plane, vec, stem, title, arrows):
    d = load_prof(path)
    x = d["x"] * 1e3
    y = d["y"] * 1e3
    z = d["z"] * 1e3
    t = d["temperature"]
    has_v = all(k in d for k in ("x-velocity", "y-velocity", "z-velocity"))
    if plane[0] == "x":
        a, b = y, z
        xlab, ylab = "Y mm", "Z mm"
        u = d[vec[0]] if has_v else np.zeros_like(t)
        v = d[vec[1]] if has_v else np.zeros_like(t)
    elif plane[0] == "y":
        a, b = x, z
        xlab, ylab = "X mm", "Z mm"
        u = d[vec[0]] if has_v else np.zeros_like(t)
        v = d[vec[1]] if has_v else np.zeros_like(t)
    else:
        a, b = x, y
        xlab, ylab = "X mm", "Y mm"
        u = d[vec[0]] if has_v else np.zeros_like(t)
        v = d[vec[1]] if has_v else np.zeros_like(t)
    if a.size < 8:
        print("TOO_FEW", path, a.size)
        return None
    fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=140)
    tri = Triangulation(a, b)
    nkeep, nall, cutoff = mask_long_edges(tri, a, b)
    tcf = ax.tricontourf(tri, t, levels=18, cmap="inferno")
    cb = fig.colorbar(tcf, ax=ax, shrink=0.86)
    cb.set_label("T (K)")
    sp = np.hypot(u, v)
    n_arrow = 0
    if arrows and has_v and float(sp.max()) > 1e-4:
        moving = sp > 1e-4
        aa, bb, uu, vv = decimate(a[moving], b[moving], u[moving], v[moving])
        ax.quiver(aa, bb, uu, vv, color="k", angles="xy", scale_units="xy",
                  scale=None, width=0.003, headwidth=3.2)
        n_arrow = int(aa.size)
    ax.set_aspect("equal")
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title + "\n" + NOTE)
    fig.tight_layout()
    out = os.path.join(FIGS, stem + ".png")
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(
        "WROTE", out,
        "n", int(a.size),
        "Tmin", float(t.min()),
        "Tmax", float(t.max()),
        "Tmean", float(t.mean()),
        "Vplane_max", float(sp.max()) if has_v else 0.0,
        "arrows", n_arrow,
        "tri", nkeep, "/", nall,
        "edge_mm", cutoff,
    )
    return out


def main():
    jobs = (
        ("v2cur_zmid.prof", ("z", 0.75), ("x-velocity", "y-velocity"),
         "v2cur_zmid_TV", "z = 0.750 mm 槽中切面  温度 + 速度矢量", True),
        ("v2cur_zorif.prof", ("z", 4.711008), ("x-velocity", "y-velocity"),
         "v2cur_zorif_TV", "z = 4.711 mm 孔板切面  温度 + 速度矢量", True),
        ("v2cur_y0.prof", ("y", 0.0), ("x-velocity", "z-velocity"),
         "v2cur_y0_TV", "Y = 0  温度 + 速度矢量", True),
        ("v2cur_x0.prof", ("x", 0.0), ("y-velocity", "z-velocity"),
         "v2cur_x0_TV", "X = 0  温度 + 速度矢量", True),
        ("v2cur_ztim.prof", ("z", -2.08), ("x-velocity", "y-velocity"),
         "v2cur_ztim_T", "z = −2.080 mm TIM 底面  温度", False),
        ("v2cur_z0.prof", ("z", 0.0), ("x-velocity", "y-velocity"),
         "v2cur_z0_T", "z = 0 铜–水底面  温度", False),
        ("v2cur_zrib.prof", ("z", 1.5), ("x-velocity", "y-velocity"),
         "v2cur_zrib_T", "z = 1.500 mm 肋顶平面  温度", False),
        ("v2cur_wall_heat.prof", ("z", -2.08), ("x-velocity", "y-velocity"),
         "v2cur_wall_heat_T", "wall_heat（TIM 受热底面）温度", False),
    )
    for fn, plane, vec, stem, title, arrows in jobs:
        path = os.path.join(FIGS, fn)
        if not os.path.isfile(path):
            print("MISSING", path)
            continue
        plot_one(path, plane, vec, stem, title, arrows)


if __name__ == "__main__":
    main()
