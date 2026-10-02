"""Recapture z=-2 mm so the section fills the picture."""
import build_report_jou as b
import make_capture_jou as m

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


lines = ['(display "Z2-RECAP")']
lines += resolution(4800, 560)
lines += b.annotation_lines("z=-2 mm")
lines += ["/display/objects/display", "f005t"]
lines += m.camera("xy", -0.002)
lines += b.save_lines(FULL)
lines += resolution(1100, 1280)
lines += b.annotation_lines("z=-2 mm center")
lines += ["/display/objects/display", "f006t"]
lines += m.camera("xy", -0.002)
lines += b.save_lines(CENTER)
lines += resolution(2400, 720)
lines.append('(display "Z2-RECAP-DONE")')
b.write_jou(b.CASE + "/z2_recap.jou", lines)
