import os
import time
import console_paste
from PIL import Image

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("ZCU-BIG")
chunk = value[start:] if start >= 0 else value[-400:]
print("errors", chunk.count("Error:"))
print(chunk[-500:])
path = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\ztimcu_temperature.png"
print("mtime", time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path))), os.path.getsize(path))
im = Image.open(path)
print("size", im.size)
