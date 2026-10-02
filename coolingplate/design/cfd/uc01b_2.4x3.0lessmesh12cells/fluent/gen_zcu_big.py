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


def camera_tall(z):
    return [
        "/display/views/camera/projection",
        "orthographic",
        "/display/views/camera/position",
        "0",
        "0",
        "%.8g" % (z + 0.05),
        "/display/views/camera/target",
        "0",
        "0",
        "%.8g" % z,
        "/display/views/camera/up-vector",
        "0",
        "1",
        "0",
        "/display/views/auto-scale",
        "/display/views/camera/zoom-camera",
        "0.82",
        "/display/views/camera/roll-camera",
        "0",
    ]


lines = ['(display "ZCU-BIG")']
lines += resolution(1100, 5200)
lines += b.annotation_lines("z=-1.98 mm")
lines += ["/display/objects/display", "zcu1t"]
lines += camera_tall(Z)
lines += b.save_lines(FULL)
lines += resolution(2400, 720)
lines.append('(display "ZCU-BIG-DONE")')
b.write_jou(b.CASE + "/zcu_big.jou", lines)
print("wrote", len(lines))
