# -*- coding: utf-8 -*-
"""Write UC-01b Cartesian hex as Nastran bulk so ICEM IcedNastran can make .uns.

Same geometry as write_hex_msh.py (meters). Not a new mesh — same cells/zones.
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from write_hex_msh import (  # noqa: E402
    FIRST,
    SLOT_YS,
    SO2,
    SX,
    SY,
    X0,
    X1,
    XL,
    XR,
    Y0,
    Y1,
    Z_IMP,
    Z_IN,
    Z_LID,
    Z_LIDTOP,
    Z_RIB,
    geo_seg,
    merge_axis,
)


def build():
    medium = os.environ.get("UC01B_MESH", "run")
    if medium == "fine":
        nx_slit, nx_core, nx_orif = 10, 22, 12
        ny_half, ny_slot, ny_rib = 6, 12, 10
        nz_slot, nz_gap, nz_orif, nz_pl = 24, 20, 12, 8
    else:
        nx_slit, nx_core, nx_orif = 8, 16, 10
        ny_half, ny_slot, ny_rib = 4, 10, 8
        nz_slot, nz_gap, nz_orif, nz_pl = 20, 16, 10, 6

    x = merge_axis([
        geo_seg(X0, XL, nx_slit),
        geo_seg(XL, -SO2, nx_core, last=min(0.02, (-SO2 - XL) / max(nx_core, 1))),
        geo_seg(-SO2, SO2, nx_orif),
        geo_seg(SO2, XR, nx_core, first=min(0.02, (XR - SO2) / max(nx_core, 1))),
        geo_seg(XR, X1, nx_slit),
    ])
    y = merge_axis([
        geo_seg(Y0, -1.00, ny_half),
        geo_seg(-1.00, -0.60, ny_slot, first=0.02, last=0.02),
        geo_seg(-0.60, -0.20, ny_rib),
        geo_seg(-0.20, -SO2, max(3, ny_slot // 3)),
        geo_seg(-SO2, SO2, nx_orif),
        geo_seg(SO2, 0.20, max(3, ny_slot // 3)),
        geo_seg(0.20, 0.60, ny_rib),
        geo_seg(0.60, 1.00, ny_slot, first=0.02, last=0.02),
        geo_seg(1.00, Y1, ny_half),
    ])
    z = merge_axis([
        geo_seg(Z_IMP, Z_RIB, nz_slot, first=FIRST, last=FIRST),
        geo_seg(Z_RIB, Z_LID, nz_gap, first=FIRST, last=FIRST),
        geo_seg(Z_LID, Z_LIDTOP, nz_orif),
        geo_seg(Z_LIDTOP, Z_IN, nz_pl),
    ])
    nx, ny, nz = len(x) - 1, len(y) - 1, len(z) - 1

    def in_slot_y(yc):
        return any(a + 1e-12 < yc < b - 1e-12 or (a <= yc <= b) for a, b in SLOT_YS)

    def is_fluid(i, j, k):
        xc = 0.5 * (x[i] + x[i + 1])
        yc = 0.5 * (y[j] + y[j + 1])
        zc = 0.5 * (z[k] + z[k + 1])
        slit = xc < XL - 1e-12 or xc > XR + 1e-12
        in_orif_xy = (abs(xc) <= SO2 + 1e-12) and (abs(yc) <= SO2 + 1e-12)
        if zc < Z_RIB - 1e-12:
            return slit or (not slit and in_slot_y(yc))
        if zc < Z_LID - 1e-12:
            return True
        if zc < Z_LIDTOP + 1e-12:
            return slit or in_orif_xy
        return in_orif_xy

    fluid = []
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if is_fluid(i, j, k):
                    fluid.append((i, j, k))

    need = set()
    for i, j, k in fluid:
        for di in (0, 1):
            for dj in (0, 1):
                for dk in (0, 1):
                    need.add((i + di, j + dj, k + dk))
    nodes = {}
    coords = []
    for key in sorted(need):
        nodes[key] = len(coords) + 1
        ii, jj, kk = key
        coords.append((x[ii] * 1e-3, y[jj] * 1e-3, z[kk] * 1e-3))

    def n(i, j, k):
        return nodes[(i, j, k)]

    cells = []
    for i, j, k in fluid:
        # Nastran CHEXA: bottom CCW then top CCW
        cells.append((
            n(i, j, k), n(i + 1, j, k), n(i + 1, j + 1, k), n(i, j + 1, k),
            n(i, j, k + 1), n(i + 1, j, k + 1), n(i + 1, j + 1, k + 1), n(i, j + 1, k + 1),
        ))
    return coords, cells, medium, (nx, ny, nz)


def write_nas(path, coords, cells):
    lines = [
        "$ UC-01b Cartesian hex (same as mesh/uc01b.msh) meters",
        "$ Python hex, not ICEM tetra. IcedNastran -> .uns",
        "BEGIN BULK",
        "PSOLID,1,1",
        "MAT1,1,1.0,0.3,1000.0",
    ]
    for i, (x, y, z) in enumerate(coords, 1):
        lines.append(f"GRID,{i},,{x:.10e},{y:.10e},{z:.10e}")
    eid = 1
    for n1, n2, n3, n4, n5, n6, n7, n8 in cells:
        lines.append(f"CHEXA,{eid},1,{n1},{n2},{n3},{n4},{n5},{n6},")
        lines.append(f",{n7},{n8}")
        eid += 1
    lines.append("ENDDATA")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    return eid - 1


def write_classic_fluent(path, coords, cells):
    """Older Fluent ASCII (attached parens) — ICEM readfluent may accept this."""
    n_nodes = len(coords)
    n_cells = len(cells)
    # no faces needed if we only test nodes+cells? readfluent wants faces.
    # skip — Nastran is the real path
    return n_nodes, n_cells


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    icem = os.path.normpath(os.path.join(here, "..", "icem"))
    os.makedirs(icem, exist_ok=True)
    coords, cells, medium, nxyz = build()
    nas = os.path.join(icem, "uc01b.nas")
    ncell = write_nas(nas, coords, cells)
    print(f"WROTE {nas}")
    print(f"cells={ncell} nodes={len(coords)} nxnynz={nxyz} level={medium}")


if __name__ == "__main__":
    main()
