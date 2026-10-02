"""Cut the first copper node plane above the TIM-copper wall and save both pictures."""
import build_report_jou as b
import make_capture_jou as m

Z = -0.00198
FULL = b.OUT_PARENT + "/i600/ztimcu_temperature.png"
CENTER = b.OUT_PARENT + "/i600/ztimcu_center_temperature.png"


def resolution(x_px, y_px):
    return [
        "/display/set/picture/use-window-resolution?",
        "no",
        "/display/set/picture/x-resolution",
        str(x_px),
        "/display/set/picture/y-resolution",
        str(y_px),
    ]


def contour(name, surface):
    return [
        "/display/objects/create",
        "contour",
        name,
        "field",
        "temperature",
        "surfaces-list",
        surface,
        "()",
        "coloring",
        "smooth",
        "node-values?",
        "yes",
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


lines = ['(display "ZCU-LAYER")']
lines += [
    "/surface/plane-surface zcu1 xy %.8g" % Z,
    "/surface/iso-clip",
    "y-coordinate",
    "zcu1c",
    "zcu1",
    "0",
    "0.0024",
]
lines += resolution(4800, 720)
lines += b.annotation_lines("z=-1.98 mm")
lines += contour("zcu1t", "zcu1")
lines += ["/display/objects/display", "zcu1t"]
lines += m.camera("xy", Z)
lines += b.save_lines(FULL)
lines += resolution(1600, 1400)
lines += b.annotation_lines("z=-1.98 mm center")
lines += contour("zcu1ct", "zcu1c")
lines += ["/display/objects/display", "zcu1ct"]
lines += m.camera("xy", Z)
lines += b.save_lines(CENTER)
lines += resolution(2400, 720)
lines.append('(display "ZCU-LAYER-DONE")')
b.write_jou(b.CASE + "/zcu_layer.jou", lines)
