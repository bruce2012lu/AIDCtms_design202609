# -*- coding: utf-8 -*-
"""Offline audit of uc01b_cht_fine_hex.msh face closure. Does not launch Fluent."""
from __future__ import annotations

import array
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MSH = os.path.join(HERE, "uc01b_cht_fine_hex.msh")
NNODE = 4547658
NCELL = 4472280
TARGET = 417850


def main():
    counts = array.array("B", bytes(NCELL + 1))
    node_hi = 0
    node_lo = 10**9
    bad_node = 0
    degen = 0
    self_cell = 0
    dup_keys = 0
    seen = {}
    target_faces = []
    n_face = 0
    with open(MSH, "r", encoding="ascii", newline="\n") as f:
        for line in f:
            s = line.strip()
            if not s or s[0] in "(#)":
                continue
            parts = s.split()
            if len(parts) != 6:
                continue
            try:
                nums = [int(p, 16) for p in parts]
            except ValueError:
                continue
            n0, n1, n2, n3, c0, c1 = nums
            n_face += 1
            for n in (n0, n1, n2, n3):
                if n < node_lo:
                    node_lo = n
                if n > node_hi:
                    node_hi = n
                if n < 1 or n > NNODE:
                    bad_node += 1
            if len({n0, n1, n2, n3}) < 4:
                degen += 1
            if c0 and c0 == c1:
                self_cell += 1
            for c in (c0, c1):
                if 1 <= c <= NCELL:
                    if counts[c] < 255:
                        counts[c] += 1
            key = tuple(sorted((n0, n1, n2, n3)))
            if key in seen:
                dup_keys += 1
            else:
                seen[key] = 1
            if c0 == TARGET or c1 == TARGET:
                target_faces.append((n0, n1, n2, n3, c0, c1))
            if n_face % 2000000 == 0:
                print(f"faces {n_face}", flush=True)
    hist = collections.Counter(counts[c] for c in range(1, NCELL + 1))
    print(f"face_lines {n_face}")
    print(f"node_id_range {node_lo} {node_hi}")
    print(f"bad_node_refs {bad_node}")
    print(f"degenerate_faces {degen}")
    print(f"self_cell_faces {self_cell}")
    print(f"duplicate_nodekeys {dup_keys}")
    print("faces_per_cell", dict(sorted(hist.items())))
    zero = [c for c in range(1, NCELL + 1) if counts[c] == 0]
    print(f"cells_with_0_faces {len(zero)} first {zero[:5]}")
    odd = [c for c in range(1, min(NCELL, 500000) + 1) if counts[c] != 6]
    # full list of non-6 is large; count only
    n_bad = sum(v for k, v in hist.items() if k != 6)
    print(f"cells_not_6_faces {n_bad}")
    print(f"target {TARGET} nfaces {counts[TARGET]}")
    for fa in target_faces:
        print("TARGET", fa)


if __name__ == "__main__":
    main()
