# -*- coding: utf-8 -*-
"""检查每张图的内容包围盒是否超出 viewBox（裁切自检）。"""
import re
import sys
import figures as F1
import figures2 as F2

figs = []
for mod in (F1, F2):
    for n in sorted(dir(mod)):
        if n.startswith("fig_"):
            figs.append((n, getattr(mod, n)))

bad = []
print(f"{'图':18s} {'viewBox':>30s} {'内容bbox':>30s}  {'超出':>26s}")
print("-" * 112)
for name, fn in figs:
    svg = fn()
    vb = [float(v) for v in
          re.search(r'viewBox="([^"]+)"', svg).group(1).split()]
    # 重新绘制一次以取 bbox（Canvas 在 render 时已记录）
    import svg as S
    cap = {}
    orig = S.Canvas.render

    def hook(self, cls="svgfig", _c=cap, _o=orig):
        _c["bb"] = self.bbox()
        _c["vb"] = self.vb
        return _o(self, cls)

    S.Canvas.render = hook
    fn()
    S.Canvas.render = orig
    bb, vb = cap["bb"], cap["vb"]
    if bb is None:
        continue
    x0, y0, w, h = vb
    x1, y1 = x0 + w, y0 + h
    ov = (max(0, x0 - bb[0]), max(0, y0 - bb[1]),
          max(0, bb[2] - x1), max(0, bb[3] - y1))
    tag = ""
    if max(ov) > 0.5:
        tag = f"L{ov[0]:.0f} T{ov[1]:.0f} R{ov[2]:.0f} B{ov[3]:.0f}"
        bad.append((name, tag))
    print(f"{name:18s} "
          f"{f'{x0:.0f},{y0:.0f} {w:.0f}x{h:.0f}':>30s} "
          f"{f'{bb[0]:.0f},{bb[1]:.0f}..{bb[2]:.0f},{bb[3]:.0f}':>30s}  "
          f"{tag:>26s}")

print()
if bad:
    print(f"{len(bad)} 张图内容超出画布：")
    for n, t in bad:
        print(f"  - {n}: {t}")
    sys.exit(1)
print("全部 %d 张图内容均在画布内。" % len(figs))
