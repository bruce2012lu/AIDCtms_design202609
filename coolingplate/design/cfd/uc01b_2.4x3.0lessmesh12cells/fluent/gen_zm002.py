"""Temperature contours at z=-0.02 mm, Y positive to the right."""
import build_report_jou as b
import make_capture_jou as m

Z = -0.00002
FULL = b.OUT_PARENT + "/i600/zm002_temperature.png"
CENTER = b.OUT_PARENT + "/i600/zm002_center_temperature.png"


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


lines = ['(display "ZM002")']
lines += resolution(2400, 720)
lines += [
    "/surface/plane-surface zm002 xy %.8g" % Z,
    "/surface/iso-clip",
    "y-coordinate",
    "zm002c",
    "zm002",
    "0",
    "0.0024",
]
lines += b.annotation_lines("z=-0.02 mm")
lines += contour("zm002t", "zm002")
lines += ["/display/objects/display", "zm002t"]
lines += m.camera("xy", Z)
lines += b.save_lines(FULL)
lines += b.annotation_lines("z=-0.02 mm center")
lines += contour("zm002ct", "zm002c")
lines += ["/display/objects/display", "zm002ct"]
lines += m.camera("xy", Z)
lines += b.save_lines(CENTER)
lines.append('(display "ZM002-DONE")')
b.write_jou(b.CASE + "/zm002.jou", lines)
open("read_zm002.txt", "w", encoding="ascii", newline="\n").write(
    "/file/read-journal\n"
    + b.CASE
    + "/zm002.jou\n"
    "()\n"
)
print("lines", len(lines))
