# -*- coding: utf-8 -*-
"""Rewrite fine_hex faces so the right-hand normal points toward c0.

Fluent 26.1 Fill_Domain (tiny_fluent6.msh, face 1 2 3 4 c0=1) uses that
rule. The hex file is closed (every cell has 6 faces, node ids in range)
but many faces point away from c0, which fails as
'no face with given nodes' on thread 2 cell 417850.
Does not launch Fluent. Does not overwrite fine.msh or fine_hex.msh.
"""
from __future__ import annotations

import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "uc01b_cht_fine_hex.msh")
DST = os.path.join(HERE, "uc01b_cht_fine_v2.msh")
NNODE = 4547658
NCELL = 4472280
NFACE = 13491762


def main():
    coords = np.empty((NNODE, 3), dtype=np.float64)
    faces = np.empty((NFACE, 6), dtype=np.int32)
    ni = 0
    fi = 0
    print("read", flush=True)
    with open(SRC, "r", encoding="ascii", newline="\n") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in "(#":
                continue
            parts = s.split()
            if len(parts) == 3 and ni < NNODE and "." in s:
                coords[ni, 0] = float(parts[0])
                coords[ni, 1] = float(parts[1])
                coords[ni, 2] = float(parts[2])
                ni += 1
                continue
            if len(parts) == 6:
                try:
                    nums = [int(p, 16) for p in parts]
                except ValueError:
                    continue
                if fi >= NFACE:
                    raise SystemExit("too many faces")
                faces[fi] = nums
                fi += 1
                if fi % 2000000 == 0:
                    print(f"faces {fi}", flush=True)
    print(f"nodes {ni} faces {fi}", flush=True)
    if ni != NNODE or fi != NFACE:
        raise SystemExit(f"count mismatch nodes {ni} faces {fi}")
    if faces[:, :4].min() < 1 or faces[:, :4].max() > NNODE:
        raise SystemExit("face node id out of range")

    acc = np.zeros((NCELL + 1, 3), dtype=np.float64)
    print("centroids", flush=True)
    c0 = faces[:, 4]
    c1 = faces[:, 5]
    nface_cell = (
        np.bincount(c0, minlength=NCELL + 1) + np.bincount(c1, minlength=NCELL + 1)
    ).astype(np.int32)
    for k in range(4):
        xyz = coords[faces[:, k] - 1]
        for a in range(3):
            acc[:, a] += np.bincount(c0, weights=xyz[:, a], minlength=NCELL + 1)
            acc[:, a] += np.bincount(c1, weights=xyz[:, a], minlength=NCELL + 1)
    if not np.all(nface_cell[1:] == 6):
        bad = int(np.sum(nface_cell[1:] != 6))
        raise SystemExit(f"cells without 6 faces: {bad}")
    cent = acc[1:] / 24.0

    print("orient", flush=True)
    n = faces[:, :4]
    p0 = coords[n[:, 0] - 1]
    p1 = coords[n[:, 1] - 1]
    p2 = coords[n[:, 2] - 1]
    p3 = coords[n[:, 3] - 1]
    u = p1 - p0
    v = p2 - p0
    nor = np.cross(u, v)
    fc = 0.25 * (p0 + p1 + p2 + p3)
    c0 = faces[:, 4]
    toward = cent[c0 - 1] - fc
    dot = np.einsum("ij,ij->i", nor, toward)
    # fallback triangle 0-1-3 when 0-1-2 is degenerate
    weak = np.abs(dot) < 1e-30
    if np.any(weak):
        v3 = p3 - p0
        nor3 = np.cross(u, v3)
        dot3 = np.einsum("ij,ij->i", nor3, toward)
        dot = np.where(weak, dot3, dot)
    flip = dot < 0.0
    n_flip = int(np.sum(flip))
    n_zero = int(np.sum(np.abs(dot) < 1e-30))
    print(f"flip {n_flip} keep {fi - n_flip} near_zero {n_zero}", flush=True)
    if n_zero:
        raise SystemExit("zero-area face normal; not writing v2")
    # (n0,n1,n2,n3) -> (n0,n3,n2,n1)
    n1s = faces[flip, 1].copy()
    faces[flip, 1] = faces[flip, 3]
    faces[flip, 3] = n1s

    p1 = coords[faces[:, 1] - 1]
    p3 = coords[faces[:, 3] - 1]
    u = p1 - p0
    v = coords[faces[:, 2] - 1] - p0
    nor = np.cross(u, v)
    fc = 0.25 * (p0 + p1 + coords[faces[:, 2] - 1] + p3)
    toward = cent[c0 - 1] - fc
    dot2 = np.einsum("ij,ij->i", nor, toward)
    n_bad = int(np.sum(dot2 <= 0.0))
    print(f"after_orient nonpositive {n_bad} min_dot {float(dot2.min())}", flush=True)
    if n_bad:
        raise SystemExit("orientation check failed")

    # cell 417850 (the Fill_Domain cell): all incident faces must point at it
    tgt = 417850
    m = (faces[:, 4] == tgt) | (faces[:, 5] == tgt)
    print(f"cell {tgt} faces {int(m.sum())}", flush=True)

    print("write", flush=True)
    fi = 0
    with open(SRC, "r", encoding="ascii", newline="\n") as fin, open(
        DST, "w", encoding="ascii", newline="\n", buffering=8 * 1024 * 1024
    ) as fout:
        first = True
        for line in fin:
            s = line.strip()
            parts = s.split()
            is_face = False
            if len(parts) == 6 and s and s[0] not in "(#":
                try:
                    int(parts[0], 16)
                    int(parts[5], 16)
                    is_face = "." not in s
                except ValueError:
                    is_face = False
            if is_face:
                row = faces[fi]
                fi += 1
                fout.write(
                    f"{row[0]:x} {row[1]:x} {row[2]:x} {row[3]:x} {row[4]:x} {row[5]:x}\n"
                )
            else:
                if first and s.startswith("(0 "):
                    fout.write(
                        '(0 "UC-01b CHT fine v2: hex indices, RH normal toward c0")\n'
                    )
                    first = False
                fout.write(line)
    if fi != NFACE:
        raise SystemExit(f"wrote {fi} faces, expected {NFACE}")
    print("FACE_CHECK_PASS")
    print(f"cells {NCELL} nodes {NNODE} faces {NFACE} flipped {n_flip}")
    print(DST)


if __name__ == "__main__":
    main()
