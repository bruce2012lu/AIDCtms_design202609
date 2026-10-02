# -*- coding: utf-8 -*-
"""Rewrite a decimal-index Fluent msh to hexadecimal indices.

Fluent 26.1 reads section 10/12/13 indices and face connectivity as hex
(see mesh/uc01b_fluent6.msh). A decimal header such as 4547658 is parsed
as 0x4547658, so the reader runs past the node block.

Node coordinates stay decimal. Section 39/45 zone ids stay decimal.
"""
from __future__ import annotations

import re
import sys

FACE_RE = re.compile(r"^\d+(?: \d+){5}$")
INT_RE = re.compile(r"\d+")


def hexify_header(line: str) -> str:
    """Hex-encode integers inside the inner (...) only. Section id stays decimal."""
    b = line.find("(", line.find("(") + 1)
    c = line.find(")", b + 1)
    if b < 0 or c < 0:
        raise ValueError(line)
    inner = INT_RE.sub(lambda m: format(int(m.group(0)), "x"), line[b + 1 : c])
    return line[: b + 1] + inner + line[c:]


def convert(src: str, dst: str) -> None:
    n_nodes = None
    n_coords = 0
    n_faces = 0
    state = "idle"
    with open(src, "r", encoding="ascii", newline="\n") as fin, open(
        dst, "w", encoding="ascii", newline="\n", buffering=8 * 1024 * 1024
    ) as fout:
        for i, line in enumerate(fin, 1):
            s = line.strip()
            if state == "node_open":
                if s != "(":
                    raise SystemExit(f"expected node '(' at line {i}: {s[:80]}")
                state = "nodes"
                fout.write(line)
            elif state == "nodes":
                if s == ")":
                    state = "idle"
                    fout.write(line)
                else:
                    n_coords += 1
                    fout.write(line)
            elif s.startswith("(10 (0 "):
                parts = s.replace("(", " ").replace(")", " ").split()
                n_nodes = int(parts[3])
                fout.write(hexify_header(s) + "\n")
            elif s.startswith("(10 (") or s.startswith("(12 (") or s.startswith("(13 ("):
                fout.write(hexify_header(s) + "\n")
                if s.startswith("(10 (") and not s.endswith("))"):
                    state = "node_open"
            elif FACE_RE.match(s):
                n_faces += 1
                fout.write(" ".join(format(int(p), "x") for p in s.split()) + "\n")
            elif s.startswith("(45 "):
                fout.write(s.replace("(45 ", "(39 ", 1) + "\n")
            else:
                fout.write(line)
            if i % 2000000 == 0:
                print(f"lines {i} coords {n_coords} faces {n_faces}", flush=True)
    print(f"declared_nodes {n_nodes}")
    print(f"coord_lines {n_coords}")
    print(f"face_lines {n_faces}")
    if n_nodes != n_coords:
        raise SystemExit(f"node count mismatch: header {n_nodes} coords {n_coords}")
    print("HEX_OK")


if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
