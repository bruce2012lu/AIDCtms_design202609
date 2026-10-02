# Python Script, API Version = V261
import traceback

ROOT = r"D:\agents2026\agents2026\agents\AIDCtms\coolingplate\design\out\grace"
LOG = ROOT + r"\sc_grace_log.txt"
DONE = ROOT + r"\sc_grace_done.txt"
STEP = ROOT + r"\step"

def logln(msg):
    f = open(LOG, "a")
    try:
        f.write(msg + "\n")
    finally:
        f.close()

def main():
    open(LOG, "w").close()
    logln("start")
    import clr
    clr.AddReference("System.Drawing")
    from System.Drawing import Color as DColor
    import SpaceClaim.Api.V261 as api
    import SpaceClaim.Api.V261.Geometry as geom
    Component = api.Component
    Document = api.Document
    InteractionMode = api.InteractionMode
    Window = api.Window
    WindowExportFormat = api.WindowExportFormat
    Direction = geom.Direction
    Frame = geom.Frame
    Point = geom.Point
    vh = globals().get("ViewHelper")
    if vh is not None:
        hits = [n for n in dir(vh) if ("Origin" in n or "Triad" in n or "Axis" in n)]
        logln("ViewHelper " + ", ".join(hits))
        for name in ("SetWorldOriginVisibility", "ShowWorldOrigin"):
            fn = getattr(vh, name, None)
            if fn is None:
                continue
            try:
                fn(False)
                logln("called " + name)
            except Exception as exc:
                logln(name + " failed " + str(exc))

    def paint(part, color, seen):
        key = part.GetHashCode()
        if key in seen:
            return
        seen.add(key)
        for db in part.Bodies:
            db.SetColor(None, color)
        for comp in part.Components:
            paint(comp.Template, color, seen)

    def add(root, filename, color):
        logln("import " + filename)
        comp = Component.CreateFromFile(root, STEP + "\\" + filename, None)
        paint(comp.Template, color, set())

    def maximize():
        try:
            clr.AddReference("System.Windows.Forms")
            from System.Windows.Forms import Application, FormWindowState
            for form in Application.OpenForms:
                form.WindowState = FormWindowState.Maximized
        except Exception:
            logln("maximize failed\n" + traceback.format_exc())

    def view_frame(cx, cy, cz, to_cam):
        dx, dy, dz = to_cam
        mag = (dx * dx + dy * dy + dz * dz) ** 0.5
        dzv = (dx / mag, dy / mag, dz / mag)
        forward = (-dzv[0], -dzv[1], -dzv[2])
        rx, ry, rz = forward[1], -forward[0], 0.0
        rm = (rx * rx + ry * ry + rz * rz) ** 0.5
        right = (rx / rm, ry / rm, rz / rm)
        ux = dzv[1] * right[2] - dzv[2] * right[1]
        uy = dzv[2] * right[0] - dzv[0] * right[2]
        uz = dzv[0] * right[1] - dzv[1] * right[0]
        return Frame.Create(
            Point.Create(cx, cy, cz),
            Direction.Create(right[0], right[1], right[2]),
            Direction.Create(ux, uy, uz),
        )

    def window_for(doc):
        win = None
        for w in Window.GetWindows(doc):
            win = w
            break
        Window.ActiveWindow = win
        win.InteractionMode = InteractionMode.Solid
        return win

    def shoot(win, path, frame, view_size):
        win.SetProjection(frame, view_size)
        win.RefreshRendering()
        win.Export(WindowExportFormat.Png, path)
        logln("exported " + path)

    cu = DColor.FromArgb(184, 112, 52)
    cu_dark = DColor.FromArgb(148, 86, 40)
    die = DColor.FromArgb(120, 42, 36)
    mem = DColor.FromArgb(196, 164, 84)
    pkg = DColor.FromArgb(42, 92, 64)
    blue = DColor.FromArgb(32, 104, 176)
    red = DColor.FromArgb(176, 52, 44)
    fin = DColor.FromArgb(212, 146, 78)

    doc = Document.Create()
    root = doc.MainPart
    add(root, "ov_pkg.stp", pkg)
    add(root, "ov_die.stp", die)
    add(root, "ov_mem.stp", mem)
    add(root, "ov_base.stp", cu)
    add(root, "ov_cpu.stp", fin)
    add(root, "ov_memrib.stp", mem)
    add(root, "ov_supply.stp", blue)
    add(root, "ov_return.stp", red)
    add(root, "ov_lid.stp", cu_dark)
    maximize()
    win = window_for(doc)
    shoot(win, ROOT + r"\fig_grace_iso_raw.png",
          view_frame(0.10, 0.06, 0.0, (-1.05, -1.25, 0.85)), 0.34)

    doc = Document.Create()
    root = doc.MainPart
    add(root, "pl_base.stp", cu)
    add(root, "pl_cpu.stp", fin)
    add(root, "pl_memrib.stp", mem)
    add(root, "pl_supply.stp", blue)
    add(root, "pl_return.stp", red)
    maximize()
    win = window_for(doc)
    top = Frame.Create(Point.Create(0.10, 0.06, 0.004), Direction.DirX, Direction.DirY)
    shoot(win, ROOT + r"\fig_grace_top_raw.png", top, 0.26)

    doc = Document.Create()
    root = doc.MainPart
    add(root, "cu_floor.stp", cu)
    add(root, "cu_fins.stp", fin)
    maximize()
    win = window_for(doc)
    shoot(win, ROOT + r"\fig_grace_channels_raw.png",
          view_frame(0.023, 0.020, 0.002, (-1.1, -0.7, 0.85)), 0.055)
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
