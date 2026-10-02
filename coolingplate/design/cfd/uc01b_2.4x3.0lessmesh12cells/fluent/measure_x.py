from PIL import Image

im = Image.open(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
).convert("RGB")
w, h = im.size
px = im.load()
xs = []
for x in range(w):
    for y in range(200, 450, 4):
        r, g, b = px[x, y]
        if r < 230 or g < 230 or b < 230:
            xs.append(x)
            break
print("x", xs[0], xs[-1], "span", xs[-1] - xs[0], "of", w)
