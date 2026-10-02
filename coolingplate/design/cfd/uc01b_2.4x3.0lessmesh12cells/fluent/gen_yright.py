"""Put the copper-layer cut back with +Y to the right, and fill the frame."""
import build_report_jou as b

Z = -0.00198
FULL = b.OUT_PARENT + "/i600/ztimcu_temperature.png"


def resolution(x_px, y_px):
    return [
        "/display/set/picture/use-window-resolution?",
        "no",
        "/display/set/picture/x-resolution",
        str(x_px),
        "/display/set/picture/y-resolution",
        str(y_px),
    ]


lines = ['(display "ZCU-YRIGHT")']
lines += resolution(5600, 640)
lines += b.annotation_lines("z=-1.98 mm")
lines += ["/display/objects/display", "zcu1t"]
lines += [
    "/display/views/camera/projection",
    "orthographic",
    "/display/views/camera/position",
    "0",
    "0",
    "%.8g" % (Z + 0.05),
    "/display/views/camera/target",
    "0",
    "0",
    "%.8g" % Z,
    "/display/views/camera/up-vector",
    "-1",
    "0",
    "0",
    "/display/views/auto-scale",
    "/display/views/camera/zoom-camera",
    "0.85",
    "/display/views/camera/roll-camera",
    "-0.13",
]
lines += b.save_lines(FULL)
lines += resolution(2400, 720)
lines.append('(display "ZCU-YRIGHT-DONE")')
b.write_jou(b.CASE + "/zcu_yright.jou", lines)
