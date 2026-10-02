# -*- coding: utf-8 -*-
"""ASCII journal: three sample cuts for the 2 mm HBM case."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figs" / "i200"
FIG.mkdir(parents=True, exist_ok=True)
BASE = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_HBM/figs/i200"
XC, YC, ZC = 0.0055, 0.025, 0.002


def camera(orient, value):
    if orient == "yz":
        pos, tgt, up = (value + 0.08, YC, ZC), (value, YC, ZC), (0, 0, 1)
        res = (2400, 560)
    elif orient == "zx":
        pos, tgt, up = (XC, value + 0.05, ZC), (XC, value, ZC), (0, 0, 1)
        res = (1400, 1200)
    else:
        pos, tgt, up = (XC, YC, value + 0.05), (XC, YC, value), (-1, 0, 0)
        res = (2400, 560)
    lines = [
        "/display/set/picture/x-resolution",
        str(res[0]),
        "/display/set/picture/y-resolution",
        str(res[1]),
        "/display/views/camera/projection",
        "orthographic",
    ]
    for label, triple in (("position", pos), ("target", tgt), ("up-vector", up)):
        lines.append("/display/views/camera/" + label)
        lines.extend("%.8g" % v for v in triple)
    lines += [
        "/display/views/auto-scale",
        "/display/views/camera/zoom-camera",
        "0.72",
        "/display/views/camera/roll-camera",
        "-0.13",
    ]
    return lines


def create_obj(name, field, surfaces, boundary):
    lines = [
        "/display/objects/create",
        "contour",
        name,
        "field",
        field,
        "surfaces-list",
    ]
    lines.extend(surfaces)
    lines += ["()", "coloring", "smooth", "node-values?", "no" if boundary else "yes"]
    if boundary:
        lines += ["boundary-values?", "yes"]
    lines += [
        "range-option",
        "auto-range-on",
        "global-range?",
        "no",
        "quit",
        "annotations-list",
        "1",
        "text-0",
        "quit",
        "/display/objects/display",
        name,
    ]
    return lines


def anno(text):
    return ["/display/annotation/edit", "text-0", "text", '"%s"' % text, "quit"]


def save(path):
    lines = ["/display/save-picture", path]
    if Path(path).exists():
        lines.append("yes")
    return lines


def main():
    lines = [
        "; HBM 2 mm sample: XY wall, YZ channel, ZX stack. Do not solve. Do not exit.",
        "/preferences/graphics/colormap-settings/number-format-type",
        "general",
        "/preferences/graphics/colormap-settings/number-format-precision",
        "5",
        "/preferences/graphics/graphics-effects/grid-plane-enabled",
        "no",
        "/display/set/picture/use-window-resolution?",
        "no",
        '(display "REPORT-BEGIN i200")',
        "/report/surface-integrals/area-weighted-avg",
        "wall_heat",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/facet-max",
        "wall_heat",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/facet-min",
        "wall_heat",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/area-weighted-avg",
        "wall_cu_fluid",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/area-weighted-avg",
        "outlet",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/mass-weighted-avg",
        "outlet",
        "()",
        "temperature",
        "no",
        "/report/surface-integrals/area-weighted-avg",
        "inlet",
        "()",
        "velocity-magnitude",
        "no",
        "/report/surface-integrals/area",
        "wall_heat",
        "()",
        "no",
        '(display "REPORT-END i200")',
        '(display "ANNO-PICK")',
        "/display/annotation/annotate",
        '"z=-2.08 mm"',
        '"None"',
        '(display "ANNO-PLACED")',
        "/display/annotation/edit",
        "text-0",
        "font-name",
        '"Microsoft YaHei"',
        "font-size",
        '"24"',
        "quit",
        "/surface/plane-surface x550 yz 0.0055",
        "/surface/plane-surface y185 zx 0.0185",
    ]
    shots = [
        ("z=-2.08 mm", "wallheat", "temperature", ["wall_heat"], True, "xy", -0.00208,
         BASE + "/wall_heat_temperature.png"),
        ("x=5.5 mm", "x550t", "temperature", ["x550"], False, "yz", 0.0055,
         BASE + "/x550_temperature.png"),
        ("Y=18.5 mm", "y185t", "temperature", ["y185"], False, "zx", 0.0185,
         BASE + "/y185_temperature.png"),
    ]
    for text, name, field, surfs, boundary, orient, value, path in shots:
        lines += anno(text)
        lines += create_obj(name, field, surfs, boundary)
        lines += camera(orient, value)
        lines += save(path)
        lines.append('(display "SAVED %s")' % Path(path).name)
    lines.append('(display "SAMPLE-DONE")')
    out = Path(__file__).with_name("sample_w08h20.jou")
    out.write_bytes(("\n".join(lines) + "\n").encode("ascii"))
    print(out, len(lines))


if __name__ == "__main__":
    main()
