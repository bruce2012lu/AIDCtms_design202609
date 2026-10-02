from PIL import Image

root = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600"
for name in ("ztimcu_temperature.png", "wall_heat_temperature.png", "z0_temperature.png"):
    im = Image.open(root + "\\" + name)
    w, h = im.size
    im.crop((w - 220, h - 180, w, h)).resize((440, 360), Image.Resampling.NEAREST).save(
        r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent\_triad_"
        + name
    )
    print(name, im.size)
