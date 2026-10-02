from PIL import Image

full = Image.open(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
)
center = Image.open(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_center_temperature.png"
)
print("full", full.size, "center", center.size)
im = full.convert("RGB")
w, h = im.size
px = im.load()
# find the colored band, ignore left colorbar
ys = []
for y in range(h):
    n = 0
    for x in range(900, w - 100, 4):
        r, g, b = px[x, y]
        if r < 240 or g < 240 or b < 240:
            n += 1
    if n > 30:
        ys.append(y)
print("band y", ys[0], ys[-1], "thick", ys[-1] - ys[0] if ys else None)
if ys:
    im.crop((800, max(0, ys[0] - 10), w - 20, ys[-1] + 10)).save(
        r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent\_z2_newband.png"
    )
# colorbar area
im.crop((0, 0, 420, h)).save(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent\_z2_cbar.png"
)
