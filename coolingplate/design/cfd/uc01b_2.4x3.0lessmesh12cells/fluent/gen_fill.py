import build_report_jou as b

Z = -0.00198
FULL = b.OUT_PARENT + "/i600/ztimcu_temperature.png"
lines = ['(display "ZCU-FILL")']
lines += [
    "/display/set/picture/use-window-resolution?",
    "no",
    "/display/set/picture/x-resolution",
    "4200",
    "/display/set/picture/y-resolution",
    "620",
    "/display/annotation/edit",
    "text-0",
    "text",
    '"z=-1.98 mm"',
    "quit",
    "/display/objects/display",
    "zcu1t",
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
    "0.9",
    "/display/views/camera/roll-camera",
    "0",
]
lines += b.save_lines(FULL)
lines += [
    "/display/set/picture/x-resolution",
    "2400",
    "/display/set/picture/y-resolution",
    "720",
]
lines.append('(display "ZCU-FILL-DONE")')
b.write_jou(b.CASE + "/zcu_fill.jou", lines)
open("read_zcu_fill.txt", "w", encoding="ascii", newline="\n").write(
    "/file/read-journal\n"
    "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0lessmesh12cells/fluent/zcu_fill.jou\n"
    "()\n"
)
print("ready")
