"""X=0 pictures from the saved field, drawn like the Fluent GUI.

Real mesh faces only. Node values are the mean of the faces that meet
at that node, then Gouraud-shaded. Temperature uses 313–342 K. Velocity
uses 0 to the plane maximum, formatted the way Fluent writes the legend.
Solid faces are omitted on the velocity picture so the ribs stay blank.
"""
import os
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
import numpy as np
from matplotlib.colors import Normalize
from matplotlib.ticker import FormatStrFormatter, FixedLocator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plot_12y_sections as P

OUT = os.path.join(P.ROOT, "figs12cells", "fluent_native")
BG = "#e6e6ea"
CMAP = "jet"


def mesh_shade(verts, values):
    v = np.asarray(values, np.float64)
    pts = np.ascontiguousarray(verts.reshape(-1, 2))
    key = np.round(pts, 4)
    order = np.lexsort((key[:, 1], key[:, 0]))
    key_s = key[order]
    change = np.ones(len(key_s), dtype=bool)
    change[1:] = np.any(key_s[1:] != key_s[:-1], axis=1)
    gid_s = np.cumsum(change) - 1
    gid = np.empty(len(pts), dtype=np.int64)
    gid[order] = gid_s
    nnode = int(gid_s[-1]) + 1
    first = np.flatnonzero(change)
    xy = pts[order[first]]
    acc = np.zeros(nnode)
    cnt = np.zeros(nnode)
    np.add.at(acc, gid, np.repeat(v, 4))
    np.add.at(cnt, gid, 1.0)
    node_v = acc / np.maximum(cnt, 1.0)
    corners = gid.reshape(-1, 4)
    tris = np.empty((corners.shape[0] * 2, 3), np.int32)
    tris[0::2] = corners[:, [0, 1, 2]]
    tris[1::2] = corners[:, [0, 2, 3]]
    area = (
        (xy[tris[:, 1], 0] - xy[tris[:, 0], 0]) * (xy[tris[:, 2], 1] - xy[tris[:, 0], 1])
        - (xy[tris[:, 1], 1] - xy[tris[:, 0], 1]) * (xy[tris[:, 2], 0] - xy[tris[:, 0], 0])
    )
    keep = np.abs(area) > 1e-12
    tri = mtri.Triangulation(xy[:, 0], xy[:, 1], tris[keep])
    return tri, node_v


def render(path, title, unit, verts, values, vmin, vmax):
    from matplotlib.collections import PolyCollection

    finite = np.isfinite(values)
    verts, values = verts[finite], values[finite]
    y0, y1 = float(verts[:, :, 0].min()), float(verts[:, :, 0].max())
    z0, z1 = float(verts[:, :, 1].min()), float(verts[:, :, 1].max())
    span_y = max(y1 - y0, 0.1)
    span_z = max(z1 - z0, 0.1)
    # Median face on this cut is about 0.004 mm. Two pixels per face,
    # and the file is kept at that size.
    dpi = 80
    px_per_mm = 500.0
    field_w = span_y * px_per_mm / dpi
    field_h = span_z * px_per_mm / dpi
    fig_w = field_w + 4.2
    fig_h = field_h + 0.8
    fig = plt.figure(figsize=(fig_w, fig_h), dpi=dpi, facecolor=BG)
    left = 3.3 / fig_w
    bottom = 0.25 / fig_h
    ax = fig.add_axes([left, bottom, field_w / fig_w, field_h / fig_h])
    ax.set_facecolor("#ffffff")
    norm = Normalize(vmin, vmax)
    ax.add_collection(PolyCollection(
        verts, array=np.asarray(values, np.float64), cmap=CMAP, norm=norm,
        edgecolors="none", linewidths=0, antialiaseds=False, rasterized=True,
    ))
    pad_y = 0.008 * span_y
    pad_z = 0.012 * span_z
    ax.set_xlim(y0 - pad_y, y1 + pad_y)
    ax.set_ylim(z0 - pad_z, z1 + pad_z)
    ax.set_aspect("equal")
    ax.set_axis_off()
    cax = fig.add_axes([0.012, bottom, 0.008, field_h / fig_h])
    sm = plt.cm.ScalarMappable(norm=norm, cmap=CMAP)
    cb = fig.colorbar(sm, cax=cax)
    ticks = np.linspace(vmin, vmax, 11)
    cb.locator = FixedLocator(ticks)
    cb.formatter = FormatStrFormatter("%.2e")
    cb.update_ticks()
    cb.ax.tick_params(labelsize=22, length=8, width=1.4)
    fig.text(0.012, bottom + field_h / fig_h + 0.004, title + "\n" + unit, fontsize=26, ha="left", va="bottom", color="black")
    os.makedirs(OUT, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=fig.get_facecolor())
    plt.close(fig)
    print(
        "WROTE", path,
        "px/mm", px_per_mm,
        "field_px", int(span_y * px_per_mm), int(span_z * px_per_mm),
        "faces", int(values.size),
        flush=True,
    )


def main():
    coords, fn, c0, c1a, c1b = P.load_geometry()
    x = coords[:, 0]
    # x=0 is a mesh station. Snap to the node plane nearest 0.
    near = np.abs(x) < 5e-5
    station = float(np.median(x[near])) if np.any(near) else 0.0
    print("x station", station, flush=True)
    planes = P.collect_planes(fn, x, [station], tol=1e-6)
    idx = planes[station]
    fields = P.load_fields("i300")
    xyz, t, u, v, w, kind = P.pack_faces(idx, coords, fn, c0, c1a, c1b, fields)
    z = xyz.mean(axis=1)[:, 2] * 1e3
    y = xyz.mean(axis=1)[:, 1] * 1e3
    print(
        "faces", idx.size,
        "Y", float(y.min()), float(y.max()),
        "Z", float(z.min()), float(z.max()),
        "fluid", int((kind == 1).sum()),
        "cu", int((kind == 2).sum()),
        "tim", int((kind == 3).sum()),
        flush=True,
    )
    both = kind >= 1
    fluid = kind == 1
    verts_t = P.poly_mm(xyz[both], (1, 2))
    render(
        os.path.join(OUT, "i300_x0_T.png"),
        "Static Temperature",
        "[ K ]",
        verts_t,
        t[both],
        313.0,
        342.0,
    )
    speed = np.sqrt(u[fluid] ** 2 + v[fluid] ** 2 + w[fluid] ** 2)
    vmax = float(speed.max())
    print("velocity max", vmax, flush=True)
    verts_v = P.poly_mm(xyz[fluid], (1, 2))
    render(
        os.path.join(OUT, "i300_x0_V.png"),
        "Velocity Magnitude",
        "[ m/s ]",
        verts_v,
        speed,
        0.0,
        vmax,
    )
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
