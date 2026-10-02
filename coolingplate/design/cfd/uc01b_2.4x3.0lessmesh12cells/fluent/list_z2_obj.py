from pathlib import Path

lines = Path("i600_smooth.jou").read_text(encoding="utf-8", errors="replace").splitlines()
want = ("ztimcu_temperature.png", "ztimcu_center_temperature.png")
out = []
for i, line in enumerate(lines):
    hit = next((w for w in want if w in line and "SHOT" in line), None)
    if not hit:
        continue
    name = surf = None
    for j in range(i, min(len(lines), i + 30)):
        if lines[j] == "contour":
            name = lines[j + 1]
        if lines[j] == "surfaces-list" and surf is None:
            surf = lines[j + 1]
    out.append("%s %s %s" % (hit, name, surf))
print("\n".join(out))
