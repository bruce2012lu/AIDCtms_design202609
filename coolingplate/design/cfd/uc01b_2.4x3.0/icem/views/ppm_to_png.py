# -*- coding: utf-8 -*-
"""Convert ICEM PPM screenshots to PNG. Uses Pillow if present, else stdlib zlib PNG."""
from __future__ import annotations

import os
import struct
import sys
import zlib


def read_ppm(path):
    with open(path, "rb") as f:
        magic = f.readline().strip()
        if magic not in (b"P3", b"P6"):
            raise ValueError(f"not a PPM: {path}")
        def tok():
            while True:
                line = f.readline()
                if not line:
                    raise ValueError("truncated PPM")
                if line.startswith(b"#"):
                    continue
                for p in line.split():
                    yield p
        g = tok()
        w = int(next(g))
        h = int(next(g))
        maxv = int(next(g))
        if magic == b"P6":
            raw = f.read()
            if maxv > 255:
                raise ValueError("16-bit PPM not supported")
            if len(raw) < w * h * 3:
                raise ValueError("short P6")
            return w, h, raw[: w * h * 3]
        # P3
        nums = [int(next(g))]
        for t in g:
            nums.append(int(t))
        return w, h, bytes(nums[: w * h * 3])


def write_png(path, w, h, rgb):
    def chunk(tag, data):
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    raw = b"".join(b"\x00" + rgb[i * w * 3 : (i + 1) * w * 3] for i in range(h))
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    with open(path, "wb") as f:
        f.write(b"\x89PNG\r\n\x1a\n")
        f.write(chunk(b"IHDR", ihdr))
        f.write(chunk(b"IDAT", zlib.compress(raw, 9)))
        f.write(chunk(b"IEND", b""))


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    n = 0
    for name in os.listdir(here):
        if not name.lower().endswith(".ppm"):
            continue
        ppm = os.path.join(here, name)
        png = os.path.splitext(ppm)[0] + ".png"
        try:
            w, h, rgb = read_ppm(ppm)
            write_png(png, w, h, rgb)
            print(f"PNG {png} {w}x{h}")
            n += 1
        except Exception as e:
            print(f"SKIP {ppm}: {e}")
    if n == 0:
        print("no PPM converted")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
