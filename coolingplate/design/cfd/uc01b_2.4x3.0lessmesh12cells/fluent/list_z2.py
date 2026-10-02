import re
from pathlib import Path

text = Path(
    r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells\UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html"
).read_text(encoding="utf-8")
caps = re.findall(r"<figcaption>(.*?)</figcaption>", text)
lines = []
for i, caption in enumerate(caps, 1):
    if "-2" in caption or "−2" in caption or "TIM" in caption[:20]:
        lines.append("%03d %s" % (i, caption))
Path("z2_caps.txt").write_text("\n".join(lines), encoding="utf-8")
print(len(lines))
