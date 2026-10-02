"""Replace the ten embedded vector figures in the 600-step report."""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_600step.html")
FIGDIR = os.path.join(ROOT, "figs12cells", "i600")
FIG = re.compile(
    r'(<figure><img src="data:image/png;base64,)([^"]+)(" alt=""><figcaption>(.*?)</figcaption></figure>)',
    re.S,
)
STATIONS = (
    ("X=0 竖直切面", "x0"),
    ("X=0.566", "xmid"),
    ("X=1.300", "x13"),
    ("X=0.400", "x04"),
    ("X=1.100", "x11"),
)


def station_of(caption):
    if "速度矢量" not in caption:
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
    return name, base64.b64encode(raw).decode("ascii"), os.path.getmtime(path)


def main():
    html = open(REPORT, encoding="utf-8").read()
    used = []

    def repl(match):
        found = station_of(match.group(4))
        if not found:
            return match.group(0)
        name, data, mtime = picture(*found)
        used.append((name, mtime))
        return match.group(1) + data + match.group(3)

    updated = FIG.sub(repl, html)
    if len(used) != 10 or len({name for name, _ in used}) != 10:
        raise SystemExit("expected 10 vector figures, got %s" % [name for name, _ in used])
    if updated.count("data:image/png;base64,") != html.count("data:image/png;base64,"):
        raise SystemExit("image count changed")
    open(REPORT, "w", encoding="utf-8", newline="\n").write(updated)
    print("replaced", len(used))
    for name, mtime in used:
        print(name)


if __name__ == "__main__":
    main()
