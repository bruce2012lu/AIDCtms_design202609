"""Embed the ten X-normal velocity-vector pictures into the 600-step report."""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html")
FIGDIR = os.path.join(ROOT, "figs12cells", "i600")
FIG = re.compile(
    r'<figure><img src="data:image/png;base64,[^"]+" alt=""><figcaption>(.*?)</figcaption></figure>',
    re.S,
)
STATIONS = (
    ("X=0 竖直切面", "x0"),
    ("X=0.566", "xmid"),
    ("X=1.300", "x13"),
    ("X=0.400", "x04"),
    ("X=1.100", "x11"),
)
NOTE = "X 为法向的速度云图后面另附切面内速度矢量，颜色为速度大小。"
CLOUD = "所以图比单胞报告多。"


def station_of(caption):
    if "速度色标" not in caption or "速度矢量" in caption:
        return None
    for prefix, key in STATIONS:
        if caption.startswith(prefix):
            return key, "中部单元" in caption
    return None


def picture(key, center):
    name = "%s%s_velocity_vector.png" % (key, "_center" if center else "")
    path = os.path.join(FIGDIR, name)
    raw = open(path, "rb").read()
    if raw[:8] != b"\x89PNG\r\n\x1a\n":
        raise SystemExit("not a png: " + name)
    return name, base64.b64encode(raw).decode("ascii")


def main():
    html = open(REPORT, encoding="utf-8").read()
    before = html.count("data:image/png;base64,")
    parts = []
    last = 0
    used = []
    for match in FIG.finditer(html):
        parts.append(html[last:match.end()])
        last = match.end()
        found = station_of(match.group(1))
        if not found:
            continue
        name, data = picture(*found)
        loc = match.group(1).split("。")[0] + "。"
        caption = loc + "速度矢量，切面内，颜色为速度大小。"
        parts.append(
            '\n<figure><img src="data:image/png;base64,%s" alt=""><figcaption>%s</figcaption></figure>'
            % (data, caption)
        )
        used.append(name)
    parts.append(html[last:])
    updated = "".join(parts)
    if updated.count(CLOUD) != 1:
        raise SystemExit("cloud sentence count %s" % updated.count(CLOUD))
    if NOTE not in updated:
        updated = updated.replace(CLOUD, CLOUD + NOTE, 1)
    if len(used) != 10 or len(set(used)) != 10:
        raise SystemExit("expected 10 vector figures, got %s" % used)
    after = updated.count("data:image/png;base64,")
    if after != before + 10:
        raise SystemExit("image count %s -> %s" % (before, after))
    if 'src="figs' in updated:
        raise SystemExit("external image link remains")
    open(REPORT, "w", encoding="utf-8", newline="\n").write(updated)
    print("inserted", len(used))
    print("images", after, "bytes", os.path.getsize(REPORT))
    for name in used:
        print(name)


if __name__ == "__main__":
    main()
