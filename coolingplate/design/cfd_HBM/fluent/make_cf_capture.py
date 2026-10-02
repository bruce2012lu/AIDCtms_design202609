# -*- coding: utf-8 -*-
"""Build the counterflow iter-200 picture journal. ASCII only."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "figs" / "cf_i200"
FIG.mkdir(parents=True, exist_ok=True)

out = []


def add(*xs):
    out.extend(xs)


def contour(name, field, surface, wall=False):
    add(
        "/display/objects/create",
        "contour",
        name,
        "field",
        field,
        "surfaces-list",
        surface,
        "()",
        "coloring",
        "smooth",
        "node-values?",
        "no" if wall else "yes",
    )
    if wall:
        add("boundary-values?", "yes")
    add(
        "range-option",
        "auto-range-on",
        "global-range?",
        "no",
        "quit",
        "annotations-list",
        "1",
        "text-0",
        "quit",
    )


def title(text):
    add("/display/annotation/edit", "text-0", "text", '"%s"' % text, "quit")


def res(w, h):
    add(
        "/display/set/picture/x-resolution",
        str(w),
        "/display/set/picture/y-resolution",
        str(h),
    )


def fit():
    add(
        "/display/views/auto-scale",
        "/display/views/camera/zoom-camera",
        "0.72",
        "/display/views/camera/roll-camera",
        "-0.13",
    )


def cam_xy(z, y="0.025", x="0.0055"):
    add(
        "/display/views/camera/projection",
        "orthographic",
        "/display/views/camera/position",
        x,
        y,
        "%.6f" % (z + 0.05),
        "/display/views/camera/target",
        x,
        y,
        "%.6f" % z,
        "/display/views/camera/up-vector",
        "-1",
        "0",
        "0",
    )
    fit()


def cam_x(x, y="0.025", z="0.002"):
    add(
        "/display/views/camera/projection",
        "orthographic",
        "/display/views/camera/position",
        "%.6f" % (x + 0.08),
        y,
        z,
        "/display/views/camera/target",
        "%.6f" % x,
        y,
        z,
        "/display/views/camera/up-vector",
        "0",
        "0",
        "1",
    )
    fit()


def cam_y(y, x="0.0055", z="0.002"):
    add(
        "/display/views/camera/projection",
        "orthographic",
        "/display/views/camera/position",
        x,
        "%.6f" % (y + 0.05),
        z,
        "/display/views/camera/target",
        x,
        "%.6f" % y,
        z,
        "/display/views/camera/up-vector",
        "0",
        "0",
        "1",
    )
    fit()


def show(name):
    add("/display/objects/display", name)


def save(name):
    add(
        "/display/save-picture",
        FIG.as_posix() + "/" + name,
        '(display "SAVED %s")' % name,
    )


def shot(label, obj, name, cam, w, h):
    title(label)
    show(obj)
    res(w, h)
    cam()
    save(name)


def main():
    add("; Counterflow iter 200 pictures. Do not solve. Do not exit.")
    add("/file/set-batch-options yes no no")
    add("/file/confirm-overwrite yes")
    add("/file/start-transcript", (ROOT / "logs" / "hbm_cf_capture.log").as_posix())
    add("/preferences/graphics/graphics-effects/grid-plane-enabled", "no")
    add("/preferences/graphics/colormap-settings/number-format-type", "general")
    add("/preferences/graphics/colormap-settings/number-format-precision", "5")
    add("/display/set/picture/use-window-resolution?", "no")
    add("/surface/plane-surface zm1992 xy -0.001992")
    add("/surface/plane-surface zm1000 xy -0.001")
    add("/surface/plane-surface zm008 xy -0.000008")
    add("/surface/plane-surface z1000 xy 0.001")
    add("/surface/plane-surface z4000 xy 0.004")
    add("/surface/plane-surface x550 yz 0.0055")
    add("/surface/plane-surface x630 yz 0.0063")
    add("/surface/plane-surface y185 zx 0.0185")
    for src, new in (("wall_heat", "whc"), ("x550", "x550c"), ("z1000", "z1000c"), ("zm1992", "zm1992c")):
        add("/surface/iso-clip", "y-coordinate", new, src, "0.013", "0.024")
    add('(display "ANNO-PICK")')
    add("/display/annotation/annotate", '"z=-2.08 mm"', '"None"')
    add(
        "/display/annotation/edit",
        "text-0",
        "font-name",
        '"Microsoft YaHei"',
        "font-size",
        '"24"',
        "quit",
    )
    contour("wallheat", "temperature", "wall_heat", True)
    shot("z=-2.08 mm", "wallheat", "wall_heat_temperature.png", lambda: cam_xy(-0.00208), 2400, 560)
    contour("whct", "temperature", "whc", True)
    shot("z=-2.08 mm center", "whct", "wall_heat_center_temperature.png", lambda: cam_xy(-0.00208, "0.0185"), 1600, 700)
    contour("zm1992t", "temperature", "zm1992")
    shot("z=-1.992 mm", "zm1992t", "zm1992_temperature.png", lambda: cam_xy(-0.001992), 2400, 560)
    contour("zm1992ct", "temperature", "zm1992c")
    shot("z=-1.992 mm center", "zm1992ct", "zm1992_center_temperature.png", lambda: cam_xy(-0.001992, "0.0185"), 1600, 700)
    contour("zm1000t", "temperature", "zm1000")
    shot("z=-1 mm", "zm1000t", "zm1000_temperature.png", lambda: cam_xy(-0.001), 2400, 560)
    contour("zm008t", "temperature", "zm008")
    shot("z=-0.008 mm", "zm008t", "zm008_temperature.png", lambda: cam_xy(-0.000008), 2400, 560)
    contour("z1000t", "temperature", "z1000")
    shot("z=1 mm", "z1000t", "z1000_temperature.png", lambda: cam_xy(0.001), 2400, 560)
    contour("z1000v", "velocity-magnitude", "z1000")
    shot("z=1 mm", "z1000v", "z1000_velocity.png", lambda: cam_xy(0.001), 2400, 560)
    contour("z1000ct", "temperature", "z1000c")
    shot("z=1 mm center", "z1000ct", "z1000_center_temperature.png", lambda: cam_xy(0.001, "0.0185"), 1600, 700)
    contour("z1000cv", "velocity-magnitude", "z1000c")
    shot("z=1 mm center", "z1000cv", "z1000_center_velocity.png", lambda: cam_xy(0.001, "0.0185"), 1600, 700)
    contour("z4000t", "temperature", "z4000")
    shot("z=4 mm", "z4000t", "z4000_temperature.png", lambda: cam_xy(0.004), 2400, 560)
    contour("x550t", "temperature", "x550")
    shot("x=5.5 mm", "x550t", "x550_temperature.png", lambda: cam_x(0.0055), 2400, 480)
    contour("x550v", "velocity-magnitude", "x550")
    shot("x=5.5 mm", "x550v", "x550_velocity.png", lambda: cam_x(0.0055), 2400, 480)
    title("x=5.5 mm")
    add(
        "/display/objects/create",
        "vector",
        "vx550",
        "vector-field",
        "velocity",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "x550",
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
        "0.004",
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
    )
    show("x550v")
    add("/display/objects/add-to-graphics", "vx550")
    res(2400, 480)
    cam_x(0.0055)
    save("x550_velocity_vector.png")
    contour("x550ct", "temperature", "x550c")
    shot("x=5.5 mm center", "x550ct", "x550_center_temperature.png", lambda: cam_x(0.0055, "0.0185"), 1400, 1100)
    contour("x550cv", "velocity-magnitude", "x550c")
    shot("x=5.5 mm center", "x550cv", "x550_center_velocity.png", lambda: cam_x(0.0055, "0.0185"), 1400, 1100)
    title("x=5.5 mm center")
    add(
        "/display/objects/create",
        "vector",
        "vx550c",
        "vector-field",
        "velocity",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        "x550c",
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
        "0.0012",
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
    )
    show("x550cv")
    add("/display/objects/add-to-graphics", "vx550c")
    res(1400, 1100)
    cam_x(0.0055, "0.0185")
    save("x550_center_velocity_vector.png")
    contour("x630t", "temperature", "x630")
    shot("x=6.3 mm", "x630t", "x630_temperature.png", lambda: cam_x(0.0063), 2400, 480)
    contour("y185t", "temperature", "y185")
    shot("Y=18.5 mm", "y185t", "y185_temperature.png", lambda: cam_y(0.0185), 1400, 1200)
    contour("y185v", "velocity-magnitude", "y185")
    shot("Y=18.5 mm", "y185v", "y185_velocity.png", lambda: cam_y(0.0185), 1400, 1200)
    contour("inhit", "temperature", "inlet_hi", True)
    shot("Y=51.5 mm", "inhit", "inlet_hi_temperature.png", lambda: cam_y(0.0515, z="0.001"), 1600, 500)
    contour("inhiv", "velocity-magnitude", "inlet_hi", True)
    shot("Y=51.5 mm", "inhiv", "inlet_hi_velocity.png", lambda: cam_y(0.0515, z="0.001"), 1600, 500)
    contour("inlot", "temperature", "inlet_lo", True)
    shot("Y=-1.5 mm", "inlot", "inlet_lo_temperature.png", lambda: cam_y(-0.0015, z="0.001"), 1600, 500)
    contour("inlov", "velocity-magnitude", "inlet_lo", True)
    shot("Y=-1.5 mm", "inlov", "inlet_lo_velocity.png", lambda: cam_y(-0.0015, z="0.001"), 1600, 500)
    contour("outlot", "temperature", "outlet_lo", True)
    shot("z=6 mm lo", "outlot", "outlet_lo_temperature.png", lambda: cam_xy(0.006, "-0.0055"), 1400, 700)
    contour("outlov", "velocity-magnitude", "outlet_lo", True)
    shot("z=6 mm lo", "outlov", "outlet_lo_velocity.png", lambda: cam_xy(0.006, "-0.0055"), 1400, 700)
    contour("outhit", "temperature", "outlet_hi", True)
    shot("z=6 mm hi", "outhit", "outlet_hi_temperature.png", lambda: cam_xy(0.006, "0.0555"), 1400, 700)
    contour("outhiv", "velocity-magnitude", "outlet_hi", True)
    shot("z=6 mm hi", "outhiv", "outlet_hi_velocity.png", lambda: cam_xy(0.006, "0.0555"), 1400, 700)
    add('(display "CAPTURE-DONE")')
    add("/file/stop-transcript")
    path = ROOT / "fluent" / "hbm_cf_capture.jou"
    path.write_text("\n".join(out) + "\n", encoding="ascii")
    print("lines", len(out))


if __name__ == "__main__":
    main()
