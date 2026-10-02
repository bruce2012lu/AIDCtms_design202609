# -*- coding: utf-8 -*-
"""Cover manufacturer logos / nameplates. Keep technical content."""
import os
from PIL import Image, ImageDraw

SRC = r"d:\agents2026\agents2026\agents\AIDCtms\solutions\assets\src_pdf_pages"
DST = os.path.join(SRC, "scrub")
DARK = (10, 14, 24)
WHITE = (255, 255, 255)
PEACH = (247, 241, 232)
GRAY = (48, 52, 56)


def paint(draw, boxes, fill, radius=5):
    for b in boxes:
        draw.rounded_rectangle(b, radius=radius, fill=fill)


def scrub_ai(path, name):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size
    # standard dark footer: logo left, copyright right
    paint(d, [
        (8, 745, 260, h - 2),
        (w - 390, 745, w - 4, h - 2),
    ], DARK, 3)
    extra = {
        "ai_ready_p10.png": [
            ((18, 210, 95, 280), GRAY),   # CDU door logo in 3D
        ],
        "ai_ready_p13.png": [
            ((int(w * 0.52), int(h * 0.38), int(w * 0.62), int(h * 0.48)), GRAY),
        ],
    }.get(name, [])
    for box, fill in extra:
        paint(d, [box], fill, 4)
    return im


def scrub_cc(path, name):
    im = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(im)
    w, h = im.size
    if name == "coolchip_p01.png":
        paint(d, [
            (20, 145, 820, 250),                # Vertiv CoolChip + 中文方案名
            (210, 350, 330, 470),               # tall cabinet V
            (400, 380, 560, 520),               # short cabinet nameplate
            (480, 990, w - 8, h - 6),           # footer wordmark
        ], WHITE, 6)
        return im

    # two-page spreads + back cover
    paint(d, [
        (10, 6, 720, 70),                       # header product line
        (w - 280, 4, w - 6, 70),                # header logo
        (8, h - 40, 340, h - 3),                # footer left company
        (w - 400, h - 40, w - 6, h - 3),        # footer right
    ], WHITE, 3)

    if name == "coolchip_p02.png":
        paint(d, [(int(w * 0.70), 8, w - 8, 70)], WHITE, 4)
    if name == "coolchip_p05.png":
        # L2A cabinet thumbnail (left page lower-right of table)
        paint(d, [
            (620, 860, 820, 1040),
            # L2L rack + cabinet door logos
            (900, 960, 1180, 1088),
            (1200, 900, 1680, 1088),
        ], WHITE, 4)
    if name == "coolchip_p03.png":
        paint(d, [
            (int(w * 0.58), int(h * 0.22), int(w * 0.72), int(h * 0.32)),
        ], GRAY, 4)
    return im


def main():
    n = 0
    mapping = (("ai_ready", scrub_ai), ("coolchip", scrub_cc))
    for folder, fn in mapping:
        src_dir = os.path.join(SRC, folder)
        dst_dir = os.path.join(DST, folder)
        os.makedirs(dst_dir, exist_ok=True)
        for name in sorted(os.listdir(src_dir)):
            if not name.lower().endswith(".png"):
                continue
            im = fn(os.path.join(src_dir, name), name)
            im.save(os.path.join(dst_dir, name), optimize=True)
            n += 1
    print("done", n)


if __name__ == "__main__":
    main()
