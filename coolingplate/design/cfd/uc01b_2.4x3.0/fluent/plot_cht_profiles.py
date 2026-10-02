# -*- coding: utf-8 -*-
"""Plot CHT field PNG from Fluent write-profile files. No invented data."""
from __future__ import annotations

import os
import re

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

for _fn in ("Microsoft YaHei", "SimHei", "Source Han Sans CN"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
FIGS = os.path.normpath(os.path.join(HERE, "..", "figs"))


def parse_prof(path):
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()
    # Fluent profile: (name n) then n numbers, or ((xy/key ...
    arrays = {}
    # try ((label ... ) (x v v v) (y ...) (temperature ...) )
    chunks = re.findall(r"\(([a-zA-Z0-9_./-]+)\s+((?:[-+eE0-9.\s]+))\)", text)
    if not chunks:
        # fallback: space columns after header
        lines = [ln.strip() for ln in text.splitlines() if ln.strip() and not ln.startswith("(")]
        return None
    for name, body in chunks:
        nums = [float(t) for t in body.split() if t]
        if nums:
            arrays[name.lower()] = np.array(nums, dtype=float)
    return arrays


def scatter_contour(x, y, v, title, fname, cmap, clabel):
    fig, ax = plt.subplots(figsize=(8.2, 6.6), dpi=130)
    x = np.asarray(x) * 1e3
    y = os_y = np.asarray(y) * 1e3
    # triangulate-like: hexbin if dense else tripcolor via tricontourf
    try:
        tcf = ax.tricontourf(x, y, v, levels=18, cmap=cmap)
        fig.colorbar(tcf, ax=ax, label=clabel)
    except Exception:
        sc = ax.scatter(x, y, c=v, s=8, cmap=cmap)
        fig.colorbar(sc, ax=ax, label=clabel)
    ax.set_aspect("equal")
    ax.set_title(title)
    ax.set_xlabel("mm")
    ax.set_ylabel("mm")
    fig.tight_layout()
    out = os.path.join(FIGS, fname)
    fig.savefig(out, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", out, "npts", len(v), "min", float(np.min(v)), "max", float(np.max(v)))
    return out


def pick_xy(d, plane):
    # plane: x0 -> YZ, y* -> XZ, z* -> XY
    keys = {k.lower(): k for k in d}
    def g(*names):
        for n in names:
            if n in d:
                return d[n]
            if n.lower() in keys:
                return d[keys[n.lower()]]
        return None
    T = g("temperature")
    V = g("velocity-magnitude", "velocity_magnitude")
    q = g("heat-flux", "total-surface-heat-flux", "wall-heat-flux")
    X, Y, Z = g("x"), g("y"), g("z")
    if plane.startswith("x"):
        return Y, Z, T, V, q, "Y", "Z"
    if plane.startswith("y"):
        return X, Z, T, V, q, "X", "Z"
    return X, Y, T, V, q, "X", "Y"


JOBS = [
    ("cht_pl_x0.prof", "x0", "X=0 过射流"),
    ("cht_pl_y0.prof", "y0", "Y=0 中槽"),
    ("cht_pl_yp08.prof", "y", "Y=+0.80 mm 侧槽"),
    ("cht_pl_ym08.prof", "y", "Y=−0.80 mm 侧槽"),
    ("cht_pl_z075.prof", "z", "Z=0.75 mm 槽中"),
    ("cht_pl_z250.prof", "z", "Z=2.50 mm 间隙"),
    ("cht_pl_ztimcu.prof", "z", "Z=−2.00 mm TIM/Cu"),
    ("cht_ztim.prof", "z", "Z=−2.04 mm TIM 内"),
]


def main():
    wrote = []
    for fn, plane, label in JOBS:
        path = os.path.join(FIGS, fn)
        if not os.path.isfile(path) or os.path.getsize(path) < 40:
            print("SKIP missing", path)
            continue
        d = parse_prof(path)
        if not d:
            print("SKIP parse", path)
            continue
        print("KEYS", fn, list(d)[:12])
        a, b, T, V, q, xa, ya = pick_xy(d, plane)
        if a is None or b is None:
            print("SKIP coords", fn)
            continue
        stem = fn.replace(".prof", "")
        if T is not None:
            wrote.append(scatter_contour(
                a, b, T, f"Fluent T  {label}  (profile)",
                f"{stem}_T.png", "inferno", "T K",
            ))
        if V is not None:
            wrote.append(scatter_contour(
                a, b, V, f"Fluent |V|  {label}  (profile)",
                f"{stem}_V.png", "viridis", "|V| m/s",
            ))
    wh = os.path.join(FIGS, "cht_wall_heat.prof")
    if os.path.isfile(wh) and os.path.getsize(wh) > 40:
        d = parse_prof(wh)
        if d:
            a, b, T, V, q, xa, ya = pick_xy(d, "z")
            if q is not None and a is not None:
                wrote.append(scatter_contour(
                    a, b, q, "Fluent wall heat flux  TIM bottom",
                    "cht_wall_heat_q.png", "coolwarm", "q W/m2",
                ))
            if T is not None and a is not None:
                wrote.append(scatter_contour(
                    a, b, T, "Fluent T  TIM bottom wall_heat",
                    "cht_wall_heat_T.png", "inferno", "T K",
                ))
    print("N_PNG", len(wrote))


if __name__ == "__main__":
    main()
