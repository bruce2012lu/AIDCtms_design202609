import os
import time
import console_paste

value = console_paste.console_value(console_paste.console_edit())
start = value.rfind("ZCU-LAYER")
print("len", len(value), "start", start)
chunk = value[start:] if start >= 0 else value[-500:]
print("errors", chunk.count("Error:"))
print(chunk[-900:])
for name in ("ztimcu_temperature.png", "ztimcu_center_temperature.png"):
    path = os.path.join(
        r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600",
        name,
    )
    print(name, time.strftime("%H:%M:%S", time.localtime(os.path.getmtime(path))), os.path.getsize(path))
