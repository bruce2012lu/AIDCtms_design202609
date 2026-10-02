# -*- coding: utf-8 -*-
"""UC-01b hex + boundary CQUAD4 Nastran for IcedNastran -> fluent6.

PID map (IcedNastran families ET3D1 / ET2D2...):
  1 volume FLUID
  2 INLET_JET  3 RETURN_SLOT  4 WALL_IMP  5 WALL_LID
  6 WALL_ORIFICE  7 FIN  8 SYM
"""
from __future__ import annotations

import os
import sys
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from write_hex_msh import (  # noqa: E402
    FIRST, SLOT_YS, SO2, X0, X1, XL, XR, Y0, Y1,
    Z_IMP, Z_IN, Z_LID, Z_LIDTOP, Z_RIB,
    _xminus_zone, _xplus_zone, _zminus_zone, _zplus_zone,
    geo_seg, merge_axis,
)

PID = {
    "inlet_jet": 2,
    "return_slot": 3,
    "wall_imp": 4,
    "wall_lid": 5,
    "wall_orifice": 6,
    "fin": 7,
    "SYM": 8,
}


def build():
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
        return any(a <= yc <= b for a, b in SLOT_YS)

    def is_fluid(i, j, k):
        xc = 0.5 * (x[i] + x[i + 1])
        yc = 0.5 * (y[j] + y[j + 1])
        zc = 0.5 * (z[k] + z[k + 1])
        slit = xc < XL - 1e-12 or xc > XR + 1e-12
        in_orif = abs(xc) <= SO2 + 1e-12 and abs(yc) <= SO2 + 1e-12
        if zc < Z_RIB - 1e-12:
            return slit or (not slit and in_slot_y(yc))
        if zc < Z_LID - 1e-12:
            return True
        if zc < Z_LIDTOP + 1e-12:
            return slit or in_orif
        return in_orif

    fluid = set()
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if is_fluid(i, j, k):
                    fluid.add((i, j, k))
    need = set()
    for i, j, k in fluid:
        for di in (0, 1):
            for dj in (0, 1):
                for dk in (0, 1):
                    need.add((i + di, j + dj, k + dk))
    nodes, coords = {}, []
    for key in sorted(need):
        nodes[key] = len(coords) + 1
        ii, jj, kk = key
        coords.append((x[ii] * 1e-3, y[jj] * 1e-3, z[kk] * 1e-3))

    def nid(i, j, k):
        return nodes[(i, j, k)]

    hexes = []
    for i, j, k in sorted(fluid):
        hexes.append((
            nid(i, j, k), nid(i + 1, j, k), nid(i + 1, j + 1, k), nid(i, j + 1, k),
            nid(i, j, k + 1), nid(i + 1, j, k + 1), nid(i + 1, j + 1, k + 1), nid(i, j + 1, k + 1),
        ))

    def occupied(i, j, k):
        return (i, j, k) in fluid

    bounds = defaultdict(list)
    for i in range(nx + 1):
        for j in range(ny):
            for k in range(nz):
                L, R = occupied(i - 1, j, k), occupied(i, j, k)
                if L == R:
                    continue
                nids = (nid(i, j, k), nid(i, j + 1, k), nid(i, j + 1, k + 1), nid(i, j, k + 1))
                if R and not L:
                    zname = _xminus_zone(x, i, j, k, y, z, XL, XR, X0, SO2, Z_LID, Z_LIDTOP, Z_IN)
                else:
                    zname = _xplus_zone(x, i, j, k, y, z, XL, XR, X1, SO2, Z_LID, Z_LIDTOP, Z_IN)
                bounds[zname].append(nids)
    for j in range(ny + 1):
        for i in range(nx):
            for k in range(nz):
                B, F = occupied(i, j - 1, k), occupied(i, j, k)
                if B == F:
                    continue
                nids = (nid(i, j, k), nid(i + 1, j, k), nid(i + 1, j, k + 1), nid(i, j, k + 1))
                yc = y[j]
                if F and not B:
                    zname = "SYM" if abs(yc - Y0) < 1e-9 else "fin"
                else:
                    zname = "SYM" if abs(yc - Y1) < 1e-9 else "fin"
                bounds[zname].append(nids)
    for k in range(nz + 1):
        for i in range(nx):
            for j in range(ny):
                D, U = occupied(i, j, k - 1), occupied(i, j, k)
                if D == U:
                    continue
                nids = (nid(i, j, k), nid(i + 1, j, k), nid(i + 1, j + 1, k), nid(i, j + 1, k))
                if U and not D:
                    zname = _zminus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_IMP, Z_RIB, Z_LID, Z_LIDTOP)
                else:
                    zname = _zplus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_LID, Z_LIDTOP, Z_IN)
                bounds[zname].append(nids)
    return coords, hexes, bounds


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    icem = os.path.normpath(os.path.join(here, "..", "icem"))
    os.makedirs(icem, exist_ok=True)
    coords, hexes, bounds = build()
    path = os.path.join(icem, "uc01b_bc.nas")
    lines = [
        "$ UC-01b hex + BC quads (meters) for IcedNastran / fluent6",
        "BEGIN BULK",
        "PSOLID,1,1",
        "MAT1,1,1.0,0.3,1000.0",
    ]
    for pid in range(2, 9):
        lines.append(f"PSHELL,{pid},1,0.0")
    for i, (x, y, z) in enumerate(coords, 1):
        lines.append(f"GRID,{i},,{x:.10e},{y:.10e},{z:.10e}")
    eid = 1
    for n1, n2, n3, n4, n5, n6, n7, n8 in hexes:
        lines.append(f"CHEXA,{eid},1,{n1},{n2},{n3},{n4},{n5},{n6},")
        lines.append(f",{n7},{n8}")
        eid += 1
    counts = {}
    for zname, faces in bounds.items():
        pid = PID[zname]
        counts[zname] = len(faces)
        for n1, n2, n3, n4 in faces:
            lines.append(f"CQUAD4,{eid},{pid},{n1},{n2},{n3},{n4}")
            eid += 1
    lines.append("ENDDATA")
    with open(path, "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(f"WROTE {path}")
    print(f"hex={len(hexes)} nodes={len(coords)} quads={sum(counts.values())} {counts}")


if __name__ == "__main__":
    main()
