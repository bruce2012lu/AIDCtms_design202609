import base64
import re
from pathlib import Path

root = Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells")
report = root / "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html"
html = report.read_text(encoding="utf-8")
raw = (root / "figs12cells" / "i600" / "ztimcu_temperature.png").read_bytes()
if raw[:8] != b"\x89PNG\r\n\x1a\n":
    raise SystemExit("not png")
data = base64.b64encode(raw).decode("ascii")
fig = re.compile(
    r'(<figure><img src="data:image/png;base64,)([^"]+)(" alt=""><figcaption>)(铜侧第一层网格，z=−1\.98 mm。.*?)(</figcaption></figure>)',
    re.S,
)
updated, n = fig.subn(lambda m: m.group(1) + data + m.group(3) + m.group(4) + m.group(5), html, count=1)
if n != 1:
    raise SystemExit("matches %s" % n)
report.write_text(updated, encoding="utf-8", newline="\n")
print("embedded")
