# -*- coding: utf-8 -*-
"""Crop SpaceClaim renders and add a Chinese legend."""
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "out" / "asm0921"
FONT = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 28)
FONT_S = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 22)


def _primary(rgb):
    r, g, b = rgb[:3]
    if r > 210 and g < 90 and b < 90:
        return True
    if g > 190 and r < 110 and b < 110:
        return True
    if b > 190 and r < 90 and g < 140:
        return True
    return False


def hide_triad(im):
    """Cover the SpaceClaim axis widget. It is a few saturated RGB pixels, not the pipes."""
    pix = im.load()
    w, h = im.size
    pts = []
    for y in range(h):
        for x in range(w):
            if _primary(pix[x, y]):
                pts.append((x, y))
    if len(pts) < 8 or len(pts) > 400:
        return im
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    # Only the compact widget. Large red/blue pipes are not this sparse.
    if max(xs) - min(xs) > 180 or max(ys) - min(ys) > 180:
        return im
    m = 10
    x0, y0 = max(0, min(xs) - m), max(0, min(ys) - m)
    x1, y1 = min(w - 1, max(xs) + m), min(h - 1, max(ys) + m)
    # sample a ring just outside the box
    ring = []
    for x in range(x0, x1 + 1):
        for y in (max(0, y0 - 6), min(h - 1, y1 + 6)):
            ring.append(pix[x, y][:3])
    for y in range(y0, y1 + 1):
        for x in (max(0, x0 - 6), min(w - 1, x1 + 6)):
            ring.append(pix[x, y][:3])
    near_white = sum(1 for r, g, b in ring if r > 245 and g > 245 and b > 245)
    if near_white < len(ring) * 0.6:
        return im
    draw = ImageDraw.Draw(im)
    draw.rectangle((x0, y0, x1, y1), fill=(255, 255, 255))
    return im


def crop(im, pad=28):
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p < 250 else 0)
    box = mask.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    x0 = max(0, x0 - pad)
    y0 = max(0, y0 - pad)
    x1 = min(im.width, x1 + pad)
    y1 = min(im.height, y1 + pad)
    return im.crop((x0, y0, x1, y1))


def legend(im, title, items):
    row_h = 36
    head = 56
    foot = 24 + row_h * len(items)
    canvas = Image.new("RGB", (im.width, im.height + head + foot), "white")
    canvas.paste(im, (0, head))
    draw = ImageDraw.Draw(canvas)
    draw.text((24, 14), title, fill=(11, 39, 72), font=FONT)
    y = head + im.height + 12
    x = 24
    for color, text in items:
        draw.rectangle((x, y + 6, x + 22, y + 28), fill=color, outline=(40, 40, 40))
        draw.text((x + 30, y), text, fill=(24, 37, 54), font=FONT_S)
        x += 30 + draw.textlength(text, font=FONT_S) + 28
        if x > im.width - 180:
            x = 24
            y += row_h
    return canvas


def main():
    plate = crop(hide_triad(Image.open(OUT / "fig11_plate3d_raw.png").convert("RGB")))
    board = crop(hide_triad(Image.open(OUT / "fig12_board3d_raw.png").convert("RGB")))
    tray = crop(hide_triad(Image.open(OUT / "fig13_tray_top_raw.png").convert("RGB")))
    legend(
        plate,
        "图 11    单颗 B300 冷板三维布局（Ansys SpaceClaim）",
        [
            ((42, 92, 64), "封装足迹"),
            ((120, 42, 36), "计算 die ×2"),
            ((196, 164, 84), "HBM ×8"),
            ((176, 98, 42), "当前冷板，芯片面朝下"),
            ((32, 104, 176), "进液，朝后面板"),
            ((176, 52, 44), "盖顶回液，折返到后面板"),
        ],
    ).save(OUT / "fig11_plate3d.png")
    legend(
        board,
        "图 12    一块托盘上两块 NVL2 的三维布局（Ansys SpaceClaim）",
        [
            ((42, 92, 64), "PCB"),
            ((92, 78, 68), "Grace CPU 冷板"),
            ((196, 122, 64), "当前 GPU 冷板 ×4"),
            ((32, 104, 176), "供液"),
            ((176, 52, 44), "回液"),
            ((70, 78, 88), "后面板"),
        ],
    ).save(OUT / "fig12_board3d.png")
    legend(
        tray,
        "图 13    整托盘 PCB 俯视：冷板位置与流道走向（Ansys SpaceClaim）",
        [
            ((42, 92, 64), "PCB，前侧在下"),
            ((92, 78, 68), "Grace CPU 冷板 ×2"),
            ((196, 122, 64), "当前 GPU 冷板 ×4"),
            ((32, 104, 176), "供液，从后面板进入"),
            ((176, 52, 44), "回液，回到后面板"),
            ((70, 78, 88), "后面板"),
        ],
    ).save(OUT / "fig13_tray_top.png")
    print("annotated")


if __name__ == "__main__":
    main()
