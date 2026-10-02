import os
import console_paste

v = console_paste.console_value(console_paste.console_edit())
i = v.rfind('VEC-BATCH')
part = v[i:]
print("done", part.count("VEC-BATCH-DONE"), "errors", part.count("Error:"))
root = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600"
names = [
    "x0_velocity_vector.png",
    "x0_center_velocity_vector.png",
    "xmid_velocity_vector.png",
    "xmid_center_velocity_vector.png",
    "x13_velocity_vector.png",
    "x13_center_velocity_vector.png",
    "x04_velocity_vector.png",
    "x04_center_velocity_vector.png",
    "x11_velocity_vector.png",
    "x11_center_velocity_vector.png",
]
for name in names:
    path = os.path.join(root, name)
    print(name, os.path.isfile(path), os.path.getsize(path) if os.path.isfile(path) else 0)
