import base64
import os
import re

root = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells"
path = os.path.join(root, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html")
text = open(path, encoding="utf-8").read()
print("external src", len(re.findall(r'src="figs', text)))
print("embedded", text.count("data:image/png;base64,"))
print("left-right", "左图" in text, "fixed scale", "固定为 313" in text)
print("face sentence", "四边形着色" in text, "node interp", "节点插值" in text)
print("mesh caption", "图 6-1" in text, "fig 2-1", "图 2-1" in text)
blob = re.search(r"data:image/png;base64,([A-Za-z0-9+/=]{80})", text).group(1)
raw = base64.b64decode(blob + "==")
print("png magic", raw[:8])
old300 = open(os.path.join(root, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_300step.html"), encoding="utf-8").read()
print("300 still external", "src=\"figs12cells/i300/" in old300, "300 embedded", "data:image/png" in old300)
one = os.path.join(root, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0.html")
print("1cell exists", os.path.isfile(one))
# one split example
for cap in re.findall(r"<figcaption>(.*?)</figcaption>", text):
    if cap.startswith("X=0"):
        print("CAP", cap[:220])
