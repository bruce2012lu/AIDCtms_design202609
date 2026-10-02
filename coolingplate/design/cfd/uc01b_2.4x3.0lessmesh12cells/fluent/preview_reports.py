import os
import re

import update_reports as u

ROOT = u.ROOT
for name in u.REPORTS:
    path = os.path.join(ROOT, name)
    text = open(path, encoding="utf-8").read()
    updated = u.retarget(text)
    srcs = re.findall(r'src="(figs12cells/[^"]+)"', updated)
    missing = [s for s in srcs if not os.path.isfile(os.path.join(ROOT, s.replace("/", os.sep)))]
    mesh = [s for s in srcs if "/mesh/" in s]
    print(name)
    print("  figures old", len(u.FIG.findall(text)), "new src", len(srcs), "mesh", len(mesh), "missing", len(missing))
    print("  scale", u.NEW_SCALE in updated, "old scale left", u.OLD_SCALE in updated)
    if missing:
        print("  ", missing[:8])
    # show two rewritten captions
    caps = re.findall(r"<figcaption>(.*?)</figcaption>", updated)
    for cap in caps:
        if "x=0" in cap or "X=0" in cap or "wall_heat" in cap or "底面" in cap:
            print(" ", cap[:180])
            break
