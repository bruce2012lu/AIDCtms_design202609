# Python Script, API Version = V261
# IronPython inside SpaceClaim. Keep this file Python 2.7 compatible.
import traceback

LOG = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\cad\out\asm0921\sc_layout_log.txt"
DONE = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\cad\out\asm0921\sc_layout_done.txt"
STEP = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\cad\out\asm0921\step_layout"
PNG = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\cad\out\asm0921"

def logln(msg):
    f = open(LOG, "a")
    try:
        f.write(msg + "\n")
    finally:
        f.close()

def main():
    open(LOG, "w").close()
    logln("start")
    names = sorted(n for n in globals() if n[:1].isupper())
    logln("globals " + ", ".join(names[:80]))
    import clr
    clr.AddReference("System.Drawing")
    from System.Drawing import Color as DColor
    import SpaceClaim.Api.V261 as api
    import SpaceClaim.Api.V261.Geometry as geom
    Component = api.Component
    Document = api.Document
    InteractionMode = api.InteractionMode
    Options = api.Options
    Window = api.Window
    WindowExportFormat = api.WindowExportFormat
    Direction = geom.Direction
    Frame = geom.Frame
    Matrix = geom.Matrix
    Point = geom.Point
    logln("Point " + ", ".join(n for n in dir(Point) if not n.startswith("_")))
    logln("Direction " + ", ".join(n for n in dir(Direction) if not n.startswith("_")))
    logln("name hits " + ", ".join(n for n in globals() if ("Opt" in n or "Origin" in n or "ViewHelper" in n)))

    def paint(part, color, seen):
        key = part.GetHashCode()
        if key in seen:
            return
        seen.add(key)
        for db in part.Bodies:
            db.SetColor(None, color)
            logln("  body " + str(db.Name))
        for comp in part.Components:
            paint(comp.Template, color, seen)

    def add(root, filename, color):
        path = STEP + "\\" + filename
        logln("import " + path)
        comp = Component.CreateFromFile(root, path, None)
        paint(comp.Template, color, set())
        logln("imported " + filename)

    def maximize():
        try:
            import clr
            clr.AddReference("System.Windows.Forms")
            from System.Windows.Forms import Application, FormWindowState
            n = 0
            for form in Application.OpenForms:
                form.WindowState = FormWindowState.Maximized
                n += 1
            logln("maximized forms " + str(n))
        except Exception:
            logln("maximize failed\n" + traceback.format_exc())

    def view_frame(cx, cy, cz, to_cam):
        dx, dy, dz = to_cam
        mag = (dx * dx + dy * dy + dz * dz) ** 0.5
        dzv = (dx / mag, dy / mag, dz / mag)
        forward = (-dzv[0], -dzv[1], -dzv[2])
        # right = forward × world_up
        rx = forward[1] * 0 - forward[2] * 1
        ry = forward[2] * 0 - forward[0] * 0
        rz = forward[0] * 1 - forward[1] * 0
        # world up is (0,0,1): cross(forward, up) = (fy*0 - fz*1, fz*0 - fx*0, fx*1 - fy*0)
        # wait I used cross(forward, up)=(fy*uz - fz*uy, fz*ux - fx*uz, fx*uy - fy*ux)
        # up=(0,0,1): (fy*1 - fz*0, fz*0 - fx*1, fx*0 - fy*0) = (fy, -fx, 0)
        rx, ry, rz = forward[1], -forward[0], 0.0
        rm = (rx * rx + ry * ry + rz * rz) ** 0.5
        right = (rx / rm, ry / rm, rz / rm)
        # DirY = DirZ × DirX
        ux = dzv[1] * right[2] - dzv[2] * right[1]
        uy = dzv[2] * right[0] - dzv[0] * right[2]
        uz = dzv[0] * right[1] - dzv[1] * right[0]
        return Frame.Create(
            Point.Create(cx, cy, cz),
            Direction.Create(right[0], right[1], right[2]),
            Direction.Create(ux, uy, uz),
        )

    def shoot(win, path, frame, view_size):
        win.InteractionMode = InteractionMode.Solid
        win.SetProjection(frame, view_size)
        win.RefreshRendering()
        win.Export(WindowExportFormat.Png, path)
        logln("exported " + path)

    cu = DColor.FromArgb(176, 98, 42)
    cu2 = DColor.FromArgb(196, 122, 64)
    die = DColor.FromArgb(120, 42, 36)
    hbm = DColor.FromArgb(196, 164, 84)
    pcb = DColor.FromArgb(42, 92, 64)
    grace = DColor.FromArgb(92, 78, 68)
    blue = DColor.FromArgb(32, 104, 176)
    red = DColor.FromArgb(176, 52, 44)
    panel = DColor.FromArgb(70, 78, 88)

    try:
        t = api.Options.GetType()
        t.GetProperty("BackgroundColor").SetValue(None, DColor.White, None)
        t.GetProperty("ShowWorldOrigin").SetValue(None, False, None)
        logln("options set")
    except Exception:
        logln("options failed\n" + traceback.format_exc())

    # --- plate ---
    doc = Document.Create()
    root = doc.MainPart
    add(root, "plate_pkg.stp", pcb)
    add(root, "plate_die.stp", die)
    add(root, "plate_hbm.stp", hbm)
    add(root, "plate_cu.stp", cu)
    add(root, "plate_supply.stp", blue)
    add(root, "plate_return.stp", red)
    maximize()
    win = None
    for w in Window.GetWindows(doc):
        win = w
        break
    Window.ActiveWindow = win
    logln("window size " + str(win.Size))
    # meters. Plate center roughly (0.047, 0.05, 0.0)
    shoot(
        win,
        PNG + r"\fig11_plate3d_raw.png",
        view_frame(0.048, 0.050, -0.008, (-0.9, -1.45, 0.72)),
        0.145,
    )
    # --- tray iso and top ---
    doc = Document.Create()
    root = doc.MainPart
    add(root, "tray_pcb.stp", pcb)
    add(root, "tray_grace.stp", grace)
    add(root, "tray_gpu.stp", cu2)
    add(root, "tray_supply.stp", blue)
    add(root, "tray_return.stp", red)
    add(root, "tray_rear.stp", panel)
    maximize()
    win = None
    for w in Window.GetWindows(doc):
        win = w
        break
    Window.ActiveWindow = win
    # scene about x 0..0.62, y 0..0.34, z 0..0.04
    shoot(
        win,
        PNG + r"\fig12_board3d_raw.png",
        view_frame(0.30, 0.17, 0.015, (-1.2, -0.85, 0.95)),
        0.62,
    )
    top = Frame.Create(
        Point.Create(0.30, 0.17, 0.02),
        Direction.DirX,
        Direction.DirY,
    )
    shoot(win, PNG + r"\fig13_tray_top_raw.png", top, 0.42)
    open(DONE, "w").write("ok\n")
    logln("done")

try:
    main()
except Exception:
    logln(traceback.format_exc())
    try:
        open(DONE, "w").write("fail\n")
    except Exception:
        pass
