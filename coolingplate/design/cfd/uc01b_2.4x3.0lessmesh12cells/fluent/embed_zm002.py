import base64
import re
from pathlib import Path

root = Path(r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells")
report = root / "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html"
html = report.read_text(encoding="utf-8")
if "z=−0.02 mm" in html:
    raise SystemExit("already inserted")

def figure(name, caption):
    raw = (root / "figs12cells" / "i600" / name).read_bytes()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not png " + name)
    data = base64.b64encode(raw).decode("ascii")
    return (
        '<figure><img src="data:image/png;base64,%s" alt=""><figcaption>%s</figcaption></figure>'
        % (data, caption)
    )

full = figure(
    "zm002_temperature.png",
    "铜内，z=−0.02 mm，铜–水底面以下 0.02 mm。全长 12 格，Y 从 −14.4 mm 到 +14.4 mm。333.15–334.46 K",
)
center = figure(
    "zm002_center_temperature.png",
    "铜内，z=−0.02 mm，中部单元 Y=0–2.4 mm。铜–水底面以下 0.02 mm。333.24–334.27 K",
)
needle = "<figcaption>铜–水底面固体，z=0。"
idx = html.find(needle)
if idx < 0:
    raise SystemExit("anchor missing")
fig_start = html.rfind("<figure>", 0, idx)
if fig_start < 0:
    raise SystemExit("figure start missing")
html = html[:fig_start] + full + "\n" + center + "\n" + html[fig_start:]
report.write_text(html, encoding="utf-8", newline="\n")
print("images", html.count("data:image/png;base64,"))
