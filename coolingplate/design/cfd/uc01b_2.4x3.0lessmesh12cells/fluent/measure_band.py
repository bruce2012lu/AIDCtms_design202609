from PIL import Image

im = Image.open(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
).convert("RGB")
w, h = im.size
px = im.load()
ys = []
xs = []
for y in range(h):
    n = 0
    for x in range(800, w - 80, 6):
        r, g, b = px[x, y]
        if r < 235 or g < 235 or b < 235:
            n += 1
    if n > 40:
        ys.append(y)
print("size", w, h, "band y", (ys[0], ys[-1], ys[-1] - ys[0]) if ys else None)
