# -*- coding: utf-8 -*-
"""UC-01b emergency Cartesian hex → Fluent .msh (meters).

Equal-area square orifice s = D*sqrt(pi/4) = 0.3545 mm (circle D=0.40
remains the ICEM target). First layer 3 um on wall_imp. Not ICEM-QA'd.
"""
from __future__ import annotations

import math
import os
from collections import defaultdict

# ---- frozen geometry (mm) then *1e-3 ----
SX, SY = 3.0, 2.4
D = 0.40
H_GAP, CH_H, T_LID, H_PLEN = 2.0, 1.50, 2.5, 2.0
SLIT_H = 0.40
S_ORIF = D * math.sqrt(math.pi / 4.0)  # 0.35449 mm
FIRST = 0.003  # mm = 3 um

X0, X1 = -SX / 2.0, SX / 2.0
Y0, Y1 = -SY / 2.0, SY / 2.0
XL, XR = X0 + SLIT_H, X1 - SLIT_H
SO2 = S_ORIF / 2.0

Z_IMP, Z_RIB, Z_LID, Z_LIDTOP, Z_IN = 0.0, CH_H, CH_H + H_GAP, CH_H + H_GAP + T_LID, CH_H + H_GAP + T_LID + H_PLEN

SLOT_YS = ((-1.00, -0.60), (-0.20, 0.20), (0.60, 1.00))


def geo_seg(a, b, n, first=None, last=None):
    """n cells from a to b; optional first-layer size at left and/or right (same units)."""
    if n < 1:
        return [a, b]
    L = b - a
    if first is None and last is None:
        return [a + L * i / n for i in range(n + 1)]
    if first is not None and last is None:
        # geometric: first cell = first, n cells
        if first * n >= L * 0.98:
            return [a + L * i / n for i in range(n + 1)]
        r = _growth(L, n, first)
        xs = [a]
        h = first
        for _ in range(n):
            xs.append(xs[-1] + h)
            h *= r
        xs[-1] = b
        return xs
    if last is not None and first is None:
        xs = geo_seg(0.0, L, n, first=last)
        return [b - x for x in reversed(xs)]
    # both ends
    if n < 4:
        return [a + L * i / n for i in range(n + 1)]
    n1 = n // 2
    n2 = n - n1
    left = geo_seg(a, (a + b) / 2.0, n1, first=first)
    right = geo_seg((a + b) / 2.0, b, n2, last=last)
    return left[:-1] + right


def _growth(L, n, h1):
    # sum h1*(r^n-1)/(r-1) = L
    lo, hi = 1.01, 2.5
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        s = h1 * (mid ** n - 1.0) / (mid - 1.0)
        if s < L:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def merge_axis(segments):
    xs = []
    for seg in segments:
        if not xs:
            xs = list(seg)
        else:
            xs.extend(seg[1:])
    # unique monotonic
    out = [xs[0]]
    for x in xs[1:]:
        if x - out[-1] > 1e-12:
            out.append(x)
    return out


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "uc01b.msh")
    medium = os.environ.get("UC01B_MESH", "run")  # run | fine

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
        geo_seg(XL, -SO2, nx_core, last=min(0.02, ( -SO2 - XL) / max(nx_core, 1))),
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
            return True  # full gap (slits + core)
        if zc < Z_LIDTOP + 1e-12:
            return slit or in_orif_xy  # lid: slits through + orifice
        return in_orif_xy  # plenum above orifice only

    fluid = set()
    for i in range(nx):
        for j in range(ny):
            for k in range(nz):
                if is_fluid(i, j, k):
                    fluid.add((i, j, k))

    # node ids for used corners only
    need = set()
    for i, j, k in fluid:
        for di in (0, 1):
            for dj in (0, 1):
                for dk in (0, 1):
                    need.add((i + di, j + dj, k + dk))
    nodes = {}
    coords = []
    for key in sorted(need):
        nid = len(coords) + 1
        nodes[key] = nid
        ii, jj, kk = key
        coords.append((x[ii] * 1e-3, y[jj] * 1e-3, z[kk] * 1e-3))

    def n(i, j, k):
        return nodes[(i, j, k)]

    cells = {}
    cid = 0
    for ijk in sorted(fluid):
        cid += 1
        cells[ijk] = cid

    # faces: (nodes_tuple, c0, c1, zone)
    # zone names
    interiors = []
    bounds = defaultdict(list)

    def add_face(nids, owner, neigh, zone):
        if neigh is not None:
            interiors.append((nids, owner, neigh))
        else:
            bounds[zone].append((nids, owner, 0))

    def cell_at(i, j, k):
        return cells.get((i, j, k))

    # i-faces (normal +x): nodes (i,j,k),(i,j+1,k),(i,j+1,k+1),(i,j,k+1)
    for i in range(nx + 1):
        for j in range(ny):
            for k in range(nz):
                L = cell_at(i - 1, j, k)
                R = cell_at(i, j, k)
                if L is None and R is None:
                    continue
                nids = (n(i, j, k), n(i, j + 1, k), n(i, j + 1, k + 1), n(i, j, k + 1))
                if L and R:
                    add_face(nids, L, R, None)
                elif R:
                    zone = _xminus_zone(x, i, j, k, y, z, XL, XR, X0, SO2, Z_LID, Z_LIDTOP, Z_IN)
                    add_face(nids[::-1], R, None, zone)  # flip so normal out of R? keep simple
                    # actually store as-is; Fluent accepts either if c1=0
                    bounds[zone][-1] = (nids, R, 0)
                else:
                    zone = _xplus_zone(x, i, j, k, y, z, XL, XR, X1, SO2, Z_LID, Z_LIDTOP, Z_IN)
                    add_face(nids, L, None, zone)

    # j-faces (normal +y)
    for j in range(ny + 1):
        for i in range(nx):
            for k in range(nz):
                B = cell_at(i, j - 1, k)
                F = cell_at(i, j, k)
                if B is None and F is None:
                    continue
                nids = (n(i, j, k), n(i + 1, j, k), n(i + 1, j, k + 1), n(i, j, k + 1))
                if B and F:
                    add_face(nids, B, F, None)
                elif F:
                    yc = y[j]
                    zone = "SYM" if abs(yc - Y0) < 1e-9 else "fin"
                    add_face(nids, F, None, zone)
                else:
                    yc = y[j]
                    zone = "SYM" if abs(yc - Y1) < 1e-9 else "fin"
                    add_face(nids, B, None, zone)

    # k-faces (normal +z)
    for k in range(nz + 1):
        for i in range(nx):
            for j in range(ny):
                Dwn = cell_at(i, j, k - 1)
                Up = cell_at(i, j, k)
                if Dwn is None and Up is None:
                    continue
                nids = (n(i, j, k), n(i + 1, j, k), n(i + 1, j + 1, k), n(i, j + 1, k))
                if Dwn and Up:
                    add_face(nids, Dwn, Up, None)
                elif Up:
                    zone = _zminus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_IMP, Z_RIB, Z_LID, Z_LIDTOP)
                    add_face(nids, Up, None, zone)
                else:
                    zone = _zplus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_LID, Z_LIDTOP, Z_IN)
                    add_face(nids, Dwn, None, zone)

    # write msh
    n_nodes = len(coords)
    n_cells = len(cells)
    face_groups = [("interior", 2, interiors)]
    bc_code = {
        "inlet_jet": 10,
        "return_slot": 5,
        "wall_imp": 3,
        "wall_lid": 3,
        "wall_orifice": 3,
        "fin": 3,
        "SYM": 7,
    }
    for zname in ("inlet_jet", "return_slot", "wall_imp", "wall_lid", "wall_orifice", "fin", "SYM"):
        face_groups.append((zname, bc_code[zname], bounds.get(zname, [])))

    # drop empty
    face_groups = [(n_, c, fs) for n_, c, fs in face_groups if fs]
    n_faces = sum(len(fs) for _, _, fs in face_groups)

    zone_ids = {}
    # fluid cells zone 2; faces start 3
    fid = 3
    for name, _, _ in face_groups:
        zone_ids[name] = fid
        fid += 1
    z_coords = z

    lines = []
    w = lines.append
    # Fluent 26.1 needs the data-block '(' on its own line, not ")(".
    w('(0 "UC-01b hex coupon D=0.40 eq-area square orifice; NOT ICEM QA")')
    w("(2 3)")
    w(f"(10 (0 1 {n_nodes} 0 3))")
    w(f"(12 (0 1 {n_cells} 0 0))")
    w(f"(13 (0 1 {n_faces} 0 0))")
    w(f"(10 (1 1 {n_nodes} 1 3)")
    w("(")
    for xx, yy, zz in coords:
        w(f"{xx:.10e} {yy:.10e} {zz:.10e}")
    w(")")
    w(")")
    w(f"(12 (2 1 {n_cells} 1 4))")

    fstart = 1
    for name, bcc, fs in face_groups:
        fend = fstart + len(fs) - 1
        zid = zone_ids[name]
        w(f"(13 ({zid} {fstart} {fend} {bcc} 4)")
        w("(")
        for nids, c0, c1 in fs:
            w(f"{nids[0]} {nids[1]} {nids[2]} {nids[3]} {c0} {c1}")
        w(")")
        w(")")
        fstart = fend + 1

    w("(45 (2 fluid fluid)())")
    for name, bcc, fs in face_groups:
        zid = zone_ids[name]
        kind = {
            2: "interior",
            3: "wall",
            5: "pressure-outlet",
            7: "symmetry",
            10: "velocity-inlet",
        }[bcc]
        w(f"(45 ({zid} {kind} {name})())")

    text = "\n".join(lines) + "\n"
    with open(out, "w", encoding="ascii", newline="\n") as f:
        f.write(text)

    # first-layer check
    dz0 = z_coords[1] - z_coords[0]
    meta = os.path.join(here, "mesh_info.txt")
    with open(meta, "w", encoding="utf-8") as f:
        f.write(f"cells {n_cells}\n")
        f.write(f"nodes {n_nodes}\n")
        f.write(f"faces {n_faces}\n")
        f.write(f"nx ny nz {nx} {ny} {nz}\n")
        f.write(f"first_layer_z_mm {dz0:.6f}\n")
        f.write(f"orifice_square_mm {S_ORIF:.5f}\n")
        f.write(f"circle_D_mm {D}\n")
        f.write(f"level {medium}\n")
        f.write("note equal-area square orifice; ICEM circle is the official geom\n")
        for name, _, fs in face_groups:
            f.write(f"zone {name} {len(fs)}\n")
    print(f"WROTE {out}")
    print(f"cells={n_cells} nodes={n_nodes} faces={n_faces} first_z={dz0:.4f} mm")


def _xminus_zone(x, i, j, k, y, z, XL, XR, X0, SO2, Z_LID, Z_LIDTOP, Z_IN):
    xc = x[i]
    zc = 0.5 * (z[k] + z[min(k + 1, len(z) - 1)])
    if abs(xc - X0) < 1e-9:
        return "SYM"  # half-slit mid-plane (shared 0.80 mm return)
    if Z_LID - 1e-12 < zc < Z_LIDTOP + 1e-12 and abs(xc + SO2) < 1e-6:
        return "wall_orifice"
    return "fin"


def _xplus_zone(x, i, j, k, y, z, XL, XR, X1, SO2, Z_LID, Z_LIDTOP, Z_IN):
    xc = x[i]
    zc = 0.5 * (z[k] + z[min(k + 1, len(z) - 1)])
    if abs(xc - X1) < 1e-9:
        return "SYM"
    if Z_LID - 1e-12 < zc < Z_LIDTOP + 1e-12 and abs(xc - SO2) < 1e-6:
        return "wall_orifice"
    return "fin"


def _zminus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_IMP, Z_RIB, Z_LID, Z_LIDTOP):
    zc = z[k]
    xc = 0.5 * (x[i] + x[i + 1])
    yc = 0.5 * (y[j] + y[j + 1])
    if abs(zc - Z_IMP) < 1e-9:
        return "wall_imp"
    if abs(zc - Z_RIB) < 1e-9:
        # underside of gap on rib top, or top of slot already interior
        return "fin"
    if abs(zc - Z_LID) < 1e-9:
        if abs(xc) <= SO2 + 1e-9 and abs(yc) <= SO2 + 1e-9:
            return "wall_orifice"  # shouldn't happen if orifice continues
        return "wall_lid"
    return "fin"


def _zplus_zone(x, y, z, i, j, k, XL, XR, SO2, Z_LID, Z_LIDTOP, Z_IN):
    zc = z[k]
    xc = 0.5 * (x[i] + x[i + 1])
    if abs(zc - Z_IN) < 1e-9:
        return "inlet_jet"
    if abs(zc - Z_LIDTOP) < 1e-9:
        slit = xc < XL - 1e-12 or xc > XR + 1e-12
        if slit:
            return "return_slot"
        return "inlet_jet"  # orifice top = plenum bottom, should be interior if plenum exists
    if abs(zc - Z_LID) < 1e-9:
        return "wall_lid"
    return "fin"


if __name__ == "__main__":
    main()
