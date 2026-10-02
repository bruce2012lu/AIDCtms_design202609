import os
from datetime import datetime

import console_paste
import make_capture_jou as m

root = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\figs12cells\i600"
v = console_paste.console_value(console_paste.console_edit())
i = v.rfind("i600_smooth.jou")
part = v[i:] if i >= 0 else v
print("smooth marker", part.count("I600-SMOOTH-DONE"))
print("errors", part.count("Error:"))
print("interrupted", part.count("Interrupted"))
print("shots", part.count("SHOT i600"))

stems = m.html_stems()
expected = []
for stem in stems:
    expected.append(m.picture_name(stem, "temperature"))
    if m.needs_v(stem):
        expected.append(m.picture_name(stem, "velocity-magnitude"))
print("expected", len(expected))
missing = []
old = []
for name in expected:
    path = os.path.join(root, name)
    if not os.path.isfile(path):
        missing.append(name)
        continue
    stamp = datetime.fromtimestamp(os.path.getmtime(path))
    if stamp < datetime(2026, 9, 27, 17, 45):
        old.append((name, stamp.strftime("%H:%M:%S")))
print("missing", len(missing))
print("stale", len(old))
if missing[:8]:
    print("missing names", missing[:8])
if old[:8]:
    print("stale names", old[:8])
newest = max(datetime.fromtimestamp(os.path.getmtime(os.path.join(root, n))) for n in expected if os.path.isfile(os.path.join(root, n)))
oldest = min(datetime.fromtimestamp(os.path.getmtime(os.path.join(root, n))) for n in expected if os.path.isfile(os.path.join(root, n)))
print("span", oldest.strftime("%H:%M:%S"), newest.strftime("%H:%M:%S"))
