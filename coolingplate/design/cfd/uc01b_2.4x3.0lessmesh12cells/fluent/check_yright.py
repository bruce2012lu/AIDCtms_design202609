import os
import time
import console_paste
from PIL import Image

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("ZCU-YRIGHT")
chunk = value[start:] if start >= 0 else ""
print("errors", chunk.count("Error:"), "done", "ZCU-YRIGHT-DONE" in chunk)
path = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
print(time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path))))
im = Image.open(path)
print("size", im.size)
w, h = im.size
im.crop((w - 280, h - 220, w, h)).resize((560, 440), Image.Resampling.NEAREST).save(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\fluent\_triad_new.png"
)
