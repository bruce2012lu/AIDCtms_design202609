# -*- coding: utf-8 -*-
"""Rewrite Fluent-26 msh (paren on its own line) to classic attached-paren msh for ICEM readfluent."""
from __future__ import annotations

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "uc01b.msh")
DST = os.path.join(HERE, "uc01b_classic.msh")


def main():
    with open(SRC, "r", encoding="ascii") as f:
        text = f.read()
    # (10 (zid ...)NEWLINE(  -> (10 (zid ...)(
    text = re.sub(r"(\((?:10|13) \([^)]+\))\r?\n\(", r"\1(", text)
    # closing )NEWLINE) after a data block -> ))
    # only when the ) is a lone line
    text = re.sub(r"\r?\n\)\r?\n\)", "\n))", text)
    with open(DST, "w", encoding="ascii", newline="\n") as f:
        f.write(text)
    print(f"WROTE {DST} bytes={os.path.getsize(DST)}")


if __name__ == "__main__":
    main()
