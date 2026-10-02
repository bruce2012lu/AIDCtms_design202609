"""Place Fluent GUI captures into the report figure folders.

Temperature-only figures are copied. Temperature/velocity figures are placed
side by side, temperature on the left.
"""
import os
import re
import shutil
from PIL import Image

ROOT = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\cfd\uc01b_2.4x3.0lessmesh12cells"


def needs_v(stem):
    return stem.endswith("_TV") or stem.endswith("_TV_center") or stem.startswith("zorif_slot_vel")


def compose(step):
    html = os.path.join(ROOT, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_%s.html" % ("300step" if step == "i300" else "600step"))
    text = open(html, encoding="utf-8").read()
    stems = [s[:-4] for s in re.findall(r'src="figs12cells/%s/([^"]+\.png)"' % step, text)]
    src_dir = os.path.join(ROOT, "figs12cells", "fluent_native", step)
    dst_dir = os.path.join(ROOT, "figs12cells", step)
    backup = os.path.join(ROOT, "figs12cells", step + "_py")
    if not os.path.isdir(backup):
        os.makedirs(backup)
        for name in os.listdir(dst_dir):
            if name.lower().endswith(".png"):
                shutil.copy2(os.path.join(dst_dir, name), os.path.join(backup, name))
    missing = []
    for stem in stems:
        t_path = os.path.join(src_dir, stem + "_T.png")
        out = os.path.join(dst_dir, stem + ".png")
        if not os.path.isfile(t_path):
            missing.append(stem + "_T")
            continue
        if needs_v(stem):
            v_path = os.path.join(src_dir, stem + "_V.png")
            if not os.path.isfile(v_path):
                missing.append(stem + "_V")
                continue
            left = Image.open(t_path).convert("RGB")
            right = Image.open(v_path).convert("RGB")
            gap = 12
            canvas = Image.new("RGB", (left.width + gap + right.width, max(left.height, right.height)), (255, 255, 255))
            canvas.paste(left, (0, 0))
            canvas.paste(right, (left.width + gap, 0))
            canvas.save(out)
        else:
            shutil.copy2(t_path, out)
    print(step, "wrote", len(stems) - len(missing), "missing", missing)
    return missing


if __name__ == "__main__":
    import sys
    compose(sys.argv[1] if len(sys.argv) > 1 else "i300")
