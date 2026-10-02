# -*- coding: utf-8 -*-
"""Plot T / |V| from Fluent ASCII surface exports. Real data only."""
from __future__ import annotations

import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.tri import Triangulation

for _fn in ("Microsoft YaHei", "SimHei", "Source Han Sans CN"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIGS = os.path.join(ROOT, "figs")


def _block_floats(text, name):
    m = re.search(r"\(" + re.escape(name) + r"\s+([\s\S]*?)\)", text)
    if not m:
        return None
    return np.fromstring(m.group(1), sep=" ")


def load_fluent_ascii(path):
    """Return x,y,z,T,V (m, K, m/s) from Fluent write-profile or ASCII."""
    if not os.path.isfile(path):
        return None
    raw = open(path, encoding="utf-8", errors="replace").read()
    if raw.lstrip().startswith("(("):
        x = _block_floats(raw, "x")
        y = _block_floats(raw, "y")
        z = _block_floats(raw, "z")
        t = _block_floats(raw, "temperature")
        v = _block_floats(raw, "velocity-magnitude")
        if x is None or t is None or len(x) < 8 or len(x) != len(t):
            return None
        if v is None:
            v = np.zeros_like(t)
        return x, y, z, t, v
    xs, ys, zs, ts, vs = [], [], [], [], []
    for line in raw.splitlines():
        s = line.strip()
        if not s or s[0] in "()":
            continue
        if re.search(r"[A-Za-z]", s) and not re.match(r"^[eE\d.+-]", s):
            continue
        parts = s.replace(",", " ").split()
        try:
            nums = [float(p) for p in parts]
        except ValueError:
            continue
        if len(nums) < 5:
            continue
        xs.append(nums[0])
        ys.append(nums[1])
        zs.append(nums[2])
        ts.append(nums[3])
        vs.append(nums[4])
    if len(xs) < 8:
        return None
    return np.array(xs), np.array(ys), np.array(zs), np.array(ts), np.array(vs)


def contour2(xa, ya, val, title, clabel, out, cmap):
    fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=140)
    try:
        tri = Triangulation(xa * 1e3, ya * 1e3)
        tcf = ax.tricontourf(tri, val, levels=18, cmap=cmap)
    except Exception:
        tcf = ax.tripcolor(xa * 1e3, ya * 1e3, val, cmap=cmap, shading="gouraud")
    cb = fig.colorbar(tcf, ax=ax, shrink=0.86)
    cb.set_label(clabel)
    ax.set_aspect("equal")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", out, "n=", len(val), "min", float(np.min(val)), "max", float(np.max(val)))


def plot_one(stem, plane, case_note):
    path = None
    for cand in (stem, stem + ".prof", stem + ".dat", stem + ".txt"):
        p = os.path.join(FIGS, cand)
        if os.path.isfile(p):
            path = p
            break
    if path is None:
        print("MISSING", stem)
        return
    data = load_fluent_ascii(path)
    if data is None:
        print("PARSE_FAIL", path, "bytes", os.path.getsize(path))
        return
    x, y, z, t, v = data
    if plane == "x0":
        a, b, al, bl = y, z, "Y mm", "Z mm"
    elif plane == "y0":
        a, b, al, bl = x, z, "X mm", "Z mm"
    else:
        a, b, al, bl = x, y, "X mm", "Y mm"
    for kind, arr, cmap, unit in (
        ("T", t, "inferno", "T (K)"),
        ("V", v, "viridis", "|V| (m/s)"),
    ):
        out = os.path.join(FIGS, f"cfd_{stem.split('.')[0]}_{kind}.png")
        titles = {
            ("pl_x0", "T"): "X=0  温度  uc01b_R  水40C  q=56.75 W/cm2",
            ("pl_x0", "V"): "X=0  速度模  uc01b_R  水40C  q=56.75 W/cm2",
            ("pl_y0", "T"): "Y=0  温度  uc01b_R  水40C  q=56.75 W/cm2",
            ("pl_y0", "V"): "Y=0  速度模  uc01b_R  水40C  q=56.75 W/cm2",
            ("pl_z075", "T"): "Z=0.75 mm  温度  uc01b_R  水40C  q=56.75 W/cm2",
            ("pl_z075", "V"): "Z=0.75 mm  速度模  uc01b_R  水40C  q=56.75 W/cm2",
            ("wall_imp", "T"): "Z=0 冲击壁  温度  uc01b_R  水40C  q=56.75 W/cm2",
            ("wall_imp", "V"): "Z=0 冲击壁  速度模  (壁面应为 0)",
        }
        title = titles.get((stem.split(".")[0], kind), f"{case_note} {plane} {kind}")
        fig, ax = plt.subplots(figsize=(8.4, 6.6), dpi=140)
        xa = a * 1e3
        ya = b * 1e3
        try:
            tri = Triangulation(xa, ya)
            t = tri.triangles
            p = np.stack([xa, ya], axis=1)
            e1 = np.linalg.norm(p[t[:, 0]] - p[t[:, 1]], axis=1)
            e2 = np.linalg.norm(p[t[:, 1]] - p[t[:, 2]], axis=1)
            e3 = np.linalg.norm(p[t[:, 2]] - p[t[:, 0]], axis=1)
            tri.set_mask((e1 > 0.28) | (e2 > 0.28) | (e3 > 0.28))
            tcf = ax.tricontourf(tri, arr, levels=18, cmap=cmap)
        except Exception:
            tcf = ax.tripcolor(xa, ya, arr, cmap=cmap, shading="gouraud")
        cb = fig.colorbar(tcf, ax=ax, shrink=0.86)
        cb.set_label(unit)
        ax.set_xlabel(al)
        ax.set_ylabel(bl)
        ax.set_aspect("equal")
        ax.set_title(title)
        fig.tight_layout()
        fig.savefig(out, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print("WROTE", out, "n=", len(arr), "min", float(np.min(arr)), "max", float(np.max(arr)))


def main():
    note = "uc01b_R  水 40 C   q''=56.75 W/cm2"
    jobs = (
        ("pl_x0", "x0"),
        ("pl_y0", "y0"),
        ("pl_z075", "z075"),
        ("wall_imp", "z0"),
    )
    for stem, plane in jobs:
        plot_one(stem, plane, note)


if __name__ == "__main__":
    main()
