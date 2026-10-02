# -*- coding: utf-8 -*-
"""Remaining Fluent pictures for the 2 mm HBM report. text-0 already exists."""
from pathlib import Path

BASE = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd_HBM/figs/i200"
FIG = Path(__file__).resolve().parents[1] / "figs" / "i200"
XC, YC, ZC = 0.0055, 0.025, 0.002
Y0, Y1 = 0.013, 0.024


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


def anno(text):
    return ["/display/annotation/edit", "text-0", "text", '"%s"' % text, "quit"]


def create_contour(name, field, surfaces, boundary):
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
    ]
    return lines


def create_vector(name, surf, scale):
    return [
        "/display/objects/create",
        "vector",
        name,
        "vector-field",
        "velocity",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        surf,
        "()",
        "vector-opt",
        "in-plane?",
        "yes",
        "fixed-length?",
        "yes",
        "quit",
        "scale",
        "auto-scale?",
        "no",
        "scale-f",
        scale,
        "quit",
        "skip",
        "24",
        "range-option",
        "auto-range-on",
        "global-range?",
        "no",
        "quit",
        "annotations-list",
        "1",
        "text-0",
        "quit",
    ]


def save(name):
    path = BASE + "/" + name
    lines = ["/display/save-picture", path]
    if (FIG / name).exists():
        lines.append("yes")
    return lines


def shot_contour(lines, text, obj, field, surfaces, boundary, orient, value, png):
    lines += anno(text)
    lines += create_contour(obj, field, surfaces, boundary)
    lines += ["/display/objects/display", obj]
    lines += camera(orient, value)
    lines += save(png)
    lines.append('(display "SAVED %s")' % png)


def main():
    lines = [
        "; Remaining HBM i200 pictures. Do not solve. Do not exit.",
        '(display "BATCH-BEGIN")',
        "/surface/plane-surface zm1992 xy -0.001992",
        "/surface/plane-surface zm1000 xy -0.001",
        "/surface/plane-surface zm008 xy -0.000008",
        "/surface/plane-surface z1000 xy 0.001",
        "/surface/plane-surface z4000 xy 0.004",
        "/surface/plane-surface x630 yz 0.0063",
        "/surface/iso-clip",
        "y-coordinate",
        "whc",
        "wall_heat",
        "0.013",
        "0.024",
        "/surface/iso-clip",
        "y-coordinate",
        "x550c",
        "x550",
        "0.013",
        "0.024",
        "/surface/iso-clip",
        "y-coordinate",
        "z1000c",
        "z1000",
        "0.013",
        "0.024",
        "/surface/iso-clip",
        "y-coordinate",
        "zm1992c",
        "zm1992",
        "0.013",
        "0.024",
    ]
    shots = [
        ("z=-2.08 mm center", "whct", "temperature", ["whc"], True, "xy", -0.00208,
         "wall_heat_center_temperature.png"),
        ("z=-1.992 mm", "zm1992t", "temperature", ["zm1992"], False, "xy", -0.001992,
         "zm1992_temperature.png"),
        ("z=-1.992 mm center", "zm1992ct", "temperature", ["zm1992c"], False, "xy", -0.001992,
         "zm1992_center_temperature.png"),
        ("z=-1 mm", "zm1000t", "temperature", ["zm1000"], False, "xy", -0.001,
         "zm1000_temperature.png"),
        ("z=-0.008 mm", "zm008t", "temperature", ["zm008"], False, "xy", -0.000008,
         "zm008_temperature.png"),
        ("z=1 mm", "z1000t", "temperature", ["z1000"], False, "xy", 0.001,
         "z1000_temperature.png"),
        ("z=1 mm", "z1000v", "velocity-magnitude", ["z1000"], False, "xy", 0.001,
         "z1000_velocity.png"),
        ("z=1 mm center", "z1000ct", "temperature", ["z1000c"], False, "xy", 0.001,
         "z1000_center_temperature.png"),
        ("z=1 mm center", "z1000cv", "velocity-magnitude", ["z1000c"], False, "xy", 0.001,
         "z1000_center_velocity.png"),
        ("z=4 mm", "z4000t", "temperature", ["z4000"], False, "xy", 0.004,
         "z4000_temperature.png"),
        ("x=5.5 mm", "x550v", "velocity-magnitude", ["x550"], False, "yz", 0.0055,
         "x550_velocity.png"),
        ("x=5.5 mm center", "x550ct", "temperature", ["x550c"], False, "yz", 0.0055,
         "x550_center_temperature.png"),
        ("x=5.5 mm center", "x550cv", "velocity-magnitude", ["x550c"], False, "yz", 0.0055,
         "x550_center_velocity.png"),
        ("x=6.3 mm", "x630t", "temperature", ["x630"], False, "yz", 0.0063,
         "x630_temperature.png"),
        ("Y=18.5 mm", "y185v", "velocity-magnitude", ["y185"], False, "zx", 0.0185,
         "y185_velocity.png"),
        ("Y=61.43 mm", "inlett", "temperature", ["inlet"], False, "zx", 0.061428571,
         "inlet_temperature.png"),
        ("Y=61.43 mm", "inletv", "velocity-magnitude", ["inlet"], False, "zx", 0.061428571,
         "inlet_velocity.png"),
        ("Y=-11.43 mm", "outlett", "temperature", ["outlet"], False, "zx", -0.011428571,
         "outlet_temperature.png"),
        ("Y=-11.43 mm", "outletv", "velocity-magnitude", ["outlet"], False, "zx", -0.011428571,
         "outlet_velocity.png"),
    ]
    for item in shots:
        shot_contour(lines, *item)

    lines += anno("x=5.5 mm")
    lines += create_vector("vx550", "x550", "0.004")
    lines += ["/display/objects/display", "x550v", "/display/objects/add-to-graphics", "vx550"]
    lines += camera("yz", 0.0055)
    lines += save("x550_velocity_vector.png")
    lines.append('(display "SAVED x550_velocity_vector.png")')

    lines += anno("x=5.5 mm center")
    lines += create_vector("vx550c", "x550c", "0.0012")
    lines += ["/display/objects/display", "x550cv", "/display/objects/add-to-graphics", "vx550c"]
    lines += camera("yz", 0.0055)
    lines += save("x550_center_velocity_vector.png")
    lines.append('(display "SAVED x550_center_velocity_vector.png")')
    lines.append('(display "CAPTURE-DONE")')
    out = Path(__file__).with_name("batch_w08h20.jou")
    out.write_bytes(("\n".join(lines) + "\n").encode("ascii"))
    print(out, len(lines))


if __name__ == "__main__":
    main()
