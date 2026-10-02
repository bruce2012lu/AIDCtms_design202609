import os
import time
import console_paste

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("ZM002")
chunk = value[start:] if start >= 0 else value[-400:]
print("errors", chunk.count("Error:"))
print(chunk[-700:])
root = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600"
for name in ("zm002_temperature.png", "zm002_center_temperature.png"):
    path = os.path.join(root, name)
    print(name, os.path.isfile(path), end=" ")
    if os.path.isfile(path):
        print(time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path))), os.path.getsize(path))
    else:
        print()
