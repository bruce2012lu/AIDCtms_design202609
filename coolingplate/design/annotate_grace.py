# -*- coding: utf-8 -*-
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent / "out" / "grace"
FONT = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 26)
FONT_S = ImageFont.truetype(r"C:\Windows\Fonts\msyh.ttc", 20)


def crop(im, pad=24):
    gray = im.convert("L")
    mask = gray.point(lambda p: 255 if p < 248 else 0)
    box = mask.getbbox()
    if not box:
        return im
    x0, y0, x1, y1 = box
    return im.crop((
        max(0, x0 - pad),
        max(0, y0 - pad),
        min(im.width, x1 + pad),
        min(im.height, y1 + pad),
    ))


def legend(im, title, items):
    head, row_h = 52, 34
    canvas = Image.new("RGB", (max(im.width, 980), im.height + head + 16 + row_h * 2), "white")
    canvas.paste(im, ((canvas.width - im.width) // 2, head))
    draw = ImageDraw.Draw(canvas)
    draw.text((20, 12), title, fill=(11, 39, 72), font=FONT)
    x, y = 20, head + im.height + 10
    for color, text in items:
        draw.rectangle((x, y + 4, x + 18, y + 22), fill=color, outline=(40, 40, 40))
        draw.text((x + 26, y), text, fill=(24, 37, 54), font=FONT_S)
        x += 26 + int(draw.textlength(text, font=FONT_S)) + 22
        if x > canvas.width - 220:
            x = 20
            y += row_h
    return canvas


def main():
    iso = crop(Image.open(OUT / "fig_grace_iso_raw.png").convert("RGB"))
    top = crop(Image.open(OUT / "fig_grace_top_raw.png").convert("RGB"))
    ch = crop(Image.open(OUT / "fig_grace_channels_raw.png").convert("RGB"))
    legend(iso, "图 3    爆炸概念（Ansys SpaceClaim）", [
        ((42, 92, 64), "模组足迹"),
        ((120, 42, 36), "CPU"),
        ((196, 164, 84), "LPDDR"),
        ((184, 112, 52), "底板"),
        ((148, 86, 40), "盖板"),
        ((32, 104, 176), "进液"),
        ((176, 52, 44), "出液"),
    ]).save(OUT / "fig_grace_iso.png")
    legend(top, "图 4    揭盖俯视（Ansys SpaceClaim，上方为后面板）", [
        ((212, 146, 78), "CPU 槽，图中加粗"),
        ((196, 164, 84), "内存槽"),
        ((32, 104, 176), "进液腔与左接头"),
        ((176, 52, 44), "出液腔与右接头"),
    ]).save(OUT / "fig_grace_top.png")
    legend(ch, "图 5    CPU 槽局部（Ansys SpaceClaim，真实 0.40 mm / 0.80 mm）", [
        ((184, 112, 52), "底板"),
        ((212, 146, 78), "48 条通道之间的肋"),
    ]).save(OUT / "fig_grace_channels.png")
    print("annotated")


if __name__ == "__main__":
    main()
