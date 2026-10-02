import ctypes
import console_paste
from PIL import Image

user32 = ctypes.windll.user32
value = console_paste.console_value(console_paste.console_edit())
print("done", "ZCU-FILL-DONE" in value[-2500:], "errors", value[-2500:].count("Error:"))
path = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
im = Image.open(path).convert("RGB")
w, h = im.size
px = im.load()
ys = [y for y in range(h) if sum(1 for x in range(600, w - 40, 8) if px[x, y][2] < 230 or px[x, y][0] < 230) > 30]
print("size", im.size, "band", (ys[0], ys[-1], ys[-1] - ys[0]) if ys else None)
user32.ShowWindow(1511948, 3)
print("maximized", user32.IsZoomed(1511948))
