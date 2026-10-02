# -*- coding: utf-8 -*-
"""Slice real quad faces out of mesh/uc01b_cht_v2.msh. No invented fields."""
from __future__ import annotations

import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import font_manager
from matplotlib.collections import PolyCollection

for _fn in ("Microsoft YaHei", "SimHei"):
    if any(f.name == _fn for f in font_manager.fontManager.ttflist):
        plt.rcParams["font.sans-serif"] = [_fn, "DejaVu Sans"]
        break
plt.rcParams["axes.unicode_minus"] = False

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MSH = os.path.join(HERE, "uc01b_cht_v2.msh")
OUT = os.path.join(ROOT, "figs")
os.makedirs(OUT, exist_ok=True)

FACE_NAME = {
    5: "interior",
    6: "inlet_jet",
    7: "return_slot",
    8: "wall_heat",
    9: "wall_orifice",
    10: "wall_cu_fluid",
    11: "wall_tim_cu",
    12: "SYM",
}
# filled from (12) headers
CELL_END = {}  # zone_id -> last cell index


def _hdr_ints(line: str):
    inner = line.split("(", 2)[2]
    inner = inner.split(")", 1)[0]
    return [int(p, 16) for p in inner.split()]


def load_nodes(path):
    xs, ys, zs = [], [], []
    with open(path, "r", encoding="ascii", errors="replace") as f:
        state = "seek"
        for line in f:
            s = line.strip()
            if state == "seek":
                if s.startswith("(10 (") and not s.startswith("(10 (0 "):
                    state = "open"
                continue
            if state == "open":
                if s != "(":
                    raise SystemExit("node block missing '('")
                state = "nodes"
                continue
            if s == ")":
                break
            a, b, c = s.split()
            xs.append(float(a))
            ys.append(float(b))
            zs.append(float(c))
            if len(xs) % 1000000 == 0:
                print("nodes", len(xs), flush=True)
    x = np.asarray(xs, np.float64)
    y = np.asarray(ys, np.float64)
    z = np.asarray(zs, np.float64)
    print("nodes_done", x.size, flush=True)
    return x, y, z


def nearest(vals, target):
    v = np.asarray(vals, np.float64)
    return float(v[np.argmin(np.abs(v - target))])


def collect(path, x, y, z, planes):
    """planes: name -> (axis, value_m). axis 0=x, 1=y, 2=z."""
    n = x.size
    # 1-based index
    X = np.empty(n + 1, np.float64)
    Y = np.empty(n + 1, np.float64)
    Z = np.empty(n + 1, np.float64)
    X[1:] = x
    Y[1:] = y
    Z[1:] = z
    # cell zone ends
    fluid_end = cu_end = tim_end = 0
    buckets = {k: [] for k in planes}
    buckets["return_slot"] = []
    buckets["wall_heat"] = []
    tol = 1e-9
    n_face = 0
    with open(path, "r", encoding="ascii", errors="replace") as f:
        state = "seek"
        zone = 0
        for line in f:
            s = line.strip()
            if state == "seek":
                if s.startswith("(12 (") and not s.startswith("(12 (0 "):
                    hid = _hdr_ints(s)
                    # zone, first, last, type, etype
                    zid, _a, last = hid[0], hid[1], hid[2]
                    if zid == 2:
                        fluid_end = last
                    elif zid == 3:
                        cu_end = last
                    elif zid == 4:
                        tim_end = last
                    continue
                if s.startswith("(13 (") and not s.startswith("(13 (0 "):
                    hid = _hdr_ints(s)
                    zone = hid[0]
                    state = "fopen"
                continue
            if state == "fopen":
                if s != "(":
                    raise SystemExit("face block missing '(' zone %s" % zone)
                state = "faces"
                continue
            if s == ")":
                state = "seek"
                print("zone_done", zone, FACE_NAME.get(zone, zone), "faces", n_face, flush=True)
                continue
            n_face += 1
            if n_face % 2000000 == 0:
                print("faces", n_face, flush=True)
            p = s.split()
            if len(p) < 4:
                continue
            i0 = int(p[0], 16)
            i1 = int(p[1], 16)
            i2 = int(p[2], 16)
            i3 = int(p[3], 16)
            c0 = int(p[4], 16) if len(p) > 4 else 0
            if c0 <= 0:
                mat = 0
            elif c0 <= fluid_end:
                mat = 1
            elif c0 <= cu_end:
                mat = 2
            elif c0 <= tim_end:
                mat = 3
            else:
                mat = 0
            # boundary zone color overrides interior material tag for named walls
            tag = FACE_NAME.get(zone, "")
            if tag == "return_slot":
                buckets["return_slot"].append((i0, i1, i2, i3, 4))
            elif tag == "wall_heat":
                buckets["wall_heat"].append((i0, i1, i2, i3, 3))
            xs = (X[i0], X[i1], X[i2], X[i3])
            ys = (Y[i0], Y[i1], Y[i2], Y[i3])
            zs = (Z[i0], Z[i1], Z[i2], Z[i3])
            dx = max(xs) - min(xs)
            dy = max(ys) - min(ys)
            dz = max(zs) - min(zs)
            col = mat if tag == "interior" else {1: 1, 2: 2, 3: 3}.get(mat, mat)
            if tag == "wall_cu_fluid":
                col = 2
            elif tag == "wall_tim_cu":
                col = 5
            elif tag == "wall_orifice":
                col = 6
            elif tag == "return_slot":
                col = 4
            elif tag == "wall_heat":
                col = 3
            for name, (axis, val) in planes.items():
                if axis == 0 and dx < tol and abs(xs[0] - val) < tol:
                    buckets[name].append((i0, i1, i2, i3, col))
                elif axis == 1 and dy < tol and abs(ys[0] - val) < tol:
                    buckets[name].append((i0, i1, i2, i3, col))
                elif axis == 2 and dz < tol and abs(zs[0] - val) < tol:
                    buckets[name].append((i0, i1, i2, i3, col))
    print("fluid_end", fluid_end, "cu_end", cu_end, "tim_end", tim_end, flush=True)
    return buckets, X, Y, Z


COLORS = {
    1: ("#8ec8e8", "#1a5276"),  # fluid
    2: ("#e0c15a", "#7d6608"),  # Cu
    3: ("#d4655a", "#7b241c"),  # TIM
    4: ("#f5cba7", "#a04000"),  # return
    5: ("#f5b7b1", "#7b241c"),  # tim-cu
    6: ("#d7bde2", "#6c3483"),  # orifice wall
    0: ("#d5d8dc", "#2c3e50"),
}
LABELS = {1: "water", 2: "Cu", 3: "TIM", 4: "return_slot", 5: "TIM-Cu", 6: "orifice wall", 0: "other"}


def _polys(ids, X, Y, Z, axis):
    # drop the constant axis
    if axis == 2:
        A, B = X, Y
        xlab, ylab = "X mm", "Y mm"
    elif axis == 0:
        A, B = Y, Z
        xlab, ylab = "Y mm", "Z mm"
    else:
        A, B = X, Z
        xlab, ylab = "X mm", "Z mm"
    out = {}
    for i0, i1, i2, i3, col in ids:
        out.setdefault(col, []).append(
            [(A[i0] * 1e3, B[i0] * 1e3), (A[i1] * 1e3, B[i1] * 1e3),
             (A[i2] * 1e3, B[i2] * 1e3), (A[i3] * 1e3, B[i3] * 1e3)]
        )
    return out, xlab, ylab


def draw(ids, X, Y, Z, axis, title, fname, xlim=None, ylim=None):
    groups, xlab, ylab = _polys(ids, X, Y, Z, axis)
    fig, ax = plt.subplots(figsize=(8.2, 6.8), dpi=130)
    n = 0
    handles = []
    for col, polys in groups.items():
        n += len(polys)
        fc, ec = COLORS.get(col, COLORS[0])
        ax.add_collection(PolyCollection(polys, facecolors=fc, edgecolors=ec, linewidths=0.12))
        handles.append(plt.Line2D([0], [0], color=ec, lw=2, label=LABELS.get(col, str(col))))
    ax.autoscale_view()
    ax.set_aspect("equal")
    if xlim:
        ax.set_xlim(*xlim)
    if ylim:
        ax.set_ylim(*ylim)
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title(title + f"\n{n} quads from uc01b_cht_v2.msh  4472280 HEXA  mm  NOT CFD")
    ax.legend(handles=handles, loc="upper right", fontsize=8)
    fig.tight_layout()
    path = os.path.join(OUT, fname)
    fig.savefig(path, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("WROTE", path, n, flush=True)
    return n


def main():
    x, y, z = load_nodes(MSH)
    uz = np.unique(np.round(z, 9))
    ux = np.unique(np.round(x, 9))
    uy = np.unique(np.round(y, 9))
    z_tim = float(uz.min())
    z_floor = nearest(uz, 0.0)
    z_rib = nearest(uz, 1.5e-3)
    z_mid = nearest(uz, 0.75e-3)
    z_orif = nearest(uz, 4.75e-3)
    x0 = nearest(ux, 0.0)
    y0 = nearest(uy, 0.0)
    y_side = nearest(uy, 0.80e-3)
    planes = {
        "z_tim": (2, z_tim),
        "z_floor": (2, z_floor),
        "z_rib": (2, z_rib),
        "z_mid": (2, z_mid),
        "z_orif": (2, z_orif),
        "x0": (0, x0),
        "y0": (1, y0),
        "y_side": (1, y_side),
    }
    print("PLANES", {k: (ax, round(v * 1e3, 6)) for k, (ax, v) in planes.items()}, flush=True)
    buckets, X, Y, Z = collect(MSH, x, y, z, planes)
    info = os.path.join(OUT, "n216_mesh_planes.txt")
    lines = ["source mesh/uc01b_cht_v2.msh", "nodes %d" % x.size, "unit m in file, mm on figures"]
    for k, (ax, v) in planes.items():
        lines.append(f"{k} axis={ax} value_mm={v*1e3:.6f} n={len(buckets[k])}")
    # return slot bbox
    if buckets["return_slot"]:
        ids = [t[0] for t in buckets["return_slot"]]
        zz = Z[np.array([t[0] for t in buckets["return_slot"]] + [t[1] for t in buckets["return_slot"]])]
        lines.append(
            "return_slot_n %d z_mm %.6f .. %.6f" % (
                len(buckets["return_slot"]), float(zz.min()) * 1e3, float(zz.max()) * 1e3)
        )
    lines.append("wall_heat_n %d" % len(buckets["wall_heat"]))
    open(info, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines), flush=True)

    draw(buckets["z_tim"], X, Y, Z, 2,
         f"v2 mesh  TIM bottom  z={z_tim*1e3:.4f} mm  (min z, wall_heat + coplanar quads)",
         "n216_mesh_z_tim.png")
    draw(buckets["wall_heat"], X, Y, Z, 2,
         f"v2 mesh  zone wall_heat  TIM bottom faces",
         "n216_mesh_wall_heat.png")
    draw(buckets["z_floor"], X, Y, Z, 2,
         f"v2 mesh  Cu–water floor  z={z_floor*1e3:.4f} mm",
         "n216_mesh_z_floor.png")
    draw(buckets["z_rib"], X, Y, Z, 2,
         f"v2 mesh  rib top plane  z={z_rib*1e3:.4f} mm",
         "n216_mesh_z_rib.png")
    draw(buckets["z_mid"], X, Y, Z, 2,
         f"v2 mesh  mid-slot  z={z_mid*1e3:.4f} mm",
         "n216_mesh_z_mid.png")
    draw(buckets["z_mid"], X, Y, Z, 2,
         f"v2 mesh  center-slot zoom  z={z_mid*1e3:.4f} mm",
         "n216_mesh_center_zoom.png", xlim=(0.40, 1.15), ylim=(-0.62, 0.62))
    draw(buckets["z_orif"], X, Y, Z, 2,
         f"v2 mesh  orifice / lid  z={z_orif*1e3:.4f} mm",
         "n216_mesh_z_orifice.png")
    draw(buckets["x0"], X, Y, Z, 0,
         f"v2 mesh  X={x0*1e3:.4f} mm",
         "n216_mesh_x0.png")
    draw(buckets["y0"], X, Y, Z, 1,
         f"v2 mesh  Y={y0*1e3:.4f} mm  center slot",
         "n216_mesh_y0.png")
    draw(buckets["y0"], X, Y, Z, 1,
         f"v2 mesh  Y={y0*1e3:.4f} mm  boundary-layer zoom near Cu floor",
         "n216_mesh_y0_bl.png", xlim=(-0.45, 0.45), ylim=(-0.15, 0.70))
    draw(buckets["y_side"], X, Y, Z, 1,
         f"v2 mesh  Y={y_side*1e3:.4f} mm  side slot",
         "n216_mesh_y_side.png")
    if buckets["return_slot"]:
        # plot in XY if the faces are flat in z, else XZ
        ids = buckets["return_slot"]
        zs = []
        for i0, i1, i2, i3, _c in ids[:20]:
            zs.append(max(Z[i0], Z[i1], Z[i2], Z[i3]) - min(Z[i0], Z[i1], Z[i2], Z[i3]))
        axis = 2 if max(zs) < 1e-8 else 0
        draw(ids, X, Y, Z, axis,
             "v2 mesh  zone return_slot  (real boundary faces)",
             "n216_mesh_return_slot.png")
    print("SLICE_DONE", flush=True)


if __name__ == "__main__":
    main()
