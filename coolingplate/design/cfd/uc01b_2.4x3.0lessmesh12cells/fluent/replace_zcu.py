import base64
import os
import re
from pathlib import Path

root = Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells")
report = root / "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html"
html = report.read_text(encoding="utf-8")
fig = re.compile(
    r'(<figure><img src="data:image/png;base64,)([^"]+)(" alt=""><figcaption>)(.*?)(</figcaption></figure>)',
    re.S,
)
files = {
    False: root / "figs12cells" / "i600" / "ztimcu_temperature.png",
    True: root / "figs12cells" / "i600" / "ztimcu_center_temperature.png",
}
caps = {
    False: "铜侧第一层网格，z=−1.98 mm。界面在 z=−2.00 mm，这一层节点在界面上方 0.020 mm。全长 12 格，Y 从 −14.4 mm 到 +14.4 mm。336.71–336.87 K",
    True: "铜侧第一层网格，z=−1.98 mm，中部单元 Y=0–2.4 mm。界面在 z=−2.00 mm，这一层节点在界面上方 0.020 mm。336.76–336.81 K",
}
n = 0

def repl(match):
    global n
    caption = match.group(4)
    if not caption.startswith("TIM–Cu"):
        return match.group(0)
    center = "中部单元" in caption
    raw = files[center].read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not png")
    data = base64.b64encode(raw).decode("ascii")
    n += 1
    return match.group(1) + data + match.group(3) + caps[center] + match.group(5)

updated = fig.sub(repl, html)
if n != 2:
    raise SystemExit("replaced %s" % n)
if updated.count("data:image/png;base64,") != html.count("data:image/png;base64,"):
    raise SystemExit("image count changed")
report.write_text(updated, encoding="utf-8", newline="\n")
print("updated", n)
