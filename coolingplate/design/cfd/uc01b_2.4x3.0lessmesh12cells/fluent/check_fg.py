import ctypes
from ctypes import wintypes
import os
import time

user32 = ctypes.windll.user32
user32.GetWindowTextLengthW.argtypes = [wintypes.HWND]
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
fg = user32.GetForegroundWindow()
n = user32.GetWindowTextLengthW(fg)
buf = ctypes.create_unicode_buffer(n + 1)
user32.GetWindowTextW(fg, buf, n + 1)
print("fg", fg, buf.value)
for name in ("ztimcu_temperature.png", "ztimcu_center_temperature.png"):
    path = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600\\" + name
    print(name, time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path))), os.path.getsize(path))
