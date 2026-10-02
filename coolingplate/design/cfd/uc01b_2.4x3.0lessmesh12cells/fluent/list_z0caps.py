import re
from pathlib import Path

text = Path(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html"
).read_text(encoding="utf-8")
caps = re.findall(r"<figcaption>(.*?)</figcaption>", text)
lines = []
for i, c in enumerate(caps, 1):
    if "z=0" in c or "z=−0" in c or "铜" in c[:12] or c.startswith("z="):
        lines.append("%03d %s" % (i, c[:160]))
Path("z0_caps.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
