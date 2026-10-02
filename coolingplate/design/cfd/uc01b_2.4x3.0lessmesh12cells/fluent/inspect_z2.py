from PIL import Image

path = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
im = Image.open(path).convert("RGB")
w, h = im.size
px = im.load()
# rows with nonwhite content in the model area (skip colorbar x<400)
rows = []
for y in range(h):
    n = 0
    for x in range(400, w - 80, 2):
        r, g, b = px[x, y]
        if r < 245 or g < 245 or b < 245:
            n += 1
    if n > 20:
        rows.append(y)
print("size", w, h, "content rows", rows[0] if rows else None, rows[-1] if rows else None, "count", len(rows))
if rows:
    band = im.crop((400, rows[0] - 4, w - 40, rows[-1] + 4))
    band = band.resize((band.width * 2, max(80, band.height * 4)), Image.Resampling.NEAREST)
    band.save(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent\_z2_band.png")
    print("band", band.size)
