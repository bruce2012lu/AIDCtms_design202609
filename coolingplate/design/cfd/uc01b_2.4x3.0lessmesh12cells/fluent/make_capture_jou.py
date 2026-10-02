"""Write Fluent journals that save every results-report contour."""
import os
import re

ROOT = "D:/agents2026/agents2026/agents/AIDCtms/coolingplate/design/cfd/uc01b_2.4x3.0lessmesh12cells"
CASE = ROOT + "/fluent"
HTML = ROOT + "/UC01b_lessmesh_ICEM_Fluent_结果报告_v1.0_12cells_300step.html"

# base stem -> orient, coordinate, kind
# kind: plane, zone, slit
SPEC = {
    "wall_heat_T": ("xy", -0.00208, "zone", "wall_heat"),
    "ztim_mid_T": ("xy", -0.0020364, "plane", None),
    "ztimcu_T": ("xy", -0.002, "plane", None),
    "zcu_mid_T": ("xy", -0.001028, "plane", None),
    "z0_T": ("xy", 0.0, "plane", None),
    "zrib_mid_T": ("xy", 0.00067, "plane", None),
    "zrib_solid_T": ("xy", 0.0015, "plane", None),
    "zorif_slot_vel": ("xy", 0.00475, "plane", None),
    "zmid_TV": ("xy", 0.00067, "plane", None),
    "zgap_TV": ("xy", 0.002426, "plane", None),
    "zorif_TV": ("xy", 0.00475, "plane", None),
    "slitin_TV": ("xy", 0.0035, "slit", None),
    "zreturn_mid_TV": ("xy", 0.00475, "slit", None),
    "y0_TV": ("zx", 0.0012, "plane", None),
    "yside_TV": ("zx", 0.0020, "plane", None),
    "x0_TV": ("yz", 0.0, "plane", None),
    "xmid_TV": ("yz", 0.000566, "plane", None),
    "x13_TV": ("yz", 0.0013, "plane", None),
    "x04_TV": ("yz", 0.0004, "plane", None),
    "x11_TV": ("yz", 0.0011, "plane", None),
    "y04_TV": ("zx", 0.0016, "plane", None),
    "y10_TV": ("zx", 0.0022, "plane", None),
    "z015_TV": ("xy", 0.000192, "plane", None),
    "z35_TV": ("xy", 0.0035, "plane", None),
    "z70_TV": ("xy", 0.007, "plane", None),
    "y0_global_TV": ("zx", 0.0, "plane", None),
    "y04_global_TV": ("zx", 0.0004, "plane", None),
    "yside_global_TV": ("zx", 0.0008, "plane", None),
    "y10_global_TV": ("zx", 0.0010, "plane", None),
    "outlet_y_front_TV": ("zx", 0.0144, "zone", "outlet_y_front"),
    "outlet_y_back_TV": ("zx", -0.0144, "zone", "outlet_y_back"),
    "return_TV": ("xy", 0.008, "zone", "return_slot"),
}

REUSE = {
    ("yz", 0.0): "cut-x0",
    ("zx", 0.0012): "slot-y",
    ("xy", 0.0): "p-z0",
    ("xy", 0.00067): "slot-z",
}


def key_of(orient, value):
    return (orient, round(float(value), 7))


def surf_name(orient, value):
    hit = REUSE.get(key_of(orient, value))
    if hit:
        return hit
    um = int(round(float(value) * 1e6))
    sign = "m" if um < 0 else ""
    return "s%s%s%d" % (orient, sign, abs(um))


def needs_v(stem):
    return stem.endswith("_TV") or stem.endswith("_TV_center") or stem.startswith("zorif_slot_vel")


def base_of(stem):
    if stem.endswith("_center"):
        return stem[: -len("_center")]
    return stem


def camera(orient, value):
    if orient == "yz":
        pos, tgt, up = (value + 0.08, 0, 0.003), (value, 0, 0.003), (0, 0, 1)
    elif orient == "zx":
        pos, tgt, up = (0, value + 0.05, 0.003), (0, value, 0.003), (0, 0, 1)
    else:
        pos, tgt, up = (0, 0, value + 0.05), (0, 0, value), (-1, 0, 0)
    lines = ["/display/views/camera/projection", "orthographic"]
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


def picture_name(stem, field):
    var = "temperature" if field == "temperature" else "velocity"
    center = stem.endswith("_center")
    base = stem[: -len("_center")] if center else stem
    for suffix in ("_TV", "_T"):
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            break
    if base == "zorif_slot_vel":
        base = "zorif_slot"
    mid = "_center" if center else ""
    return "%s%s_%s.png" % (base, mid, var)


def edit_range(name):
    return [
        "/display/objects/edit",
        name,
        "range-option",
        "auto-range-on",
        "global-range?",
        "no",
        "quit",
        "quit",
        "/display/objects/display",
        name,
    ]


def create_obj(name, field, surfaces):
    lines = [
        "/display/objects/create",
        "contour",
        name,
        "field",
        field,
        "surfaces-list",
    ]
    lines.extend(surfaces)
    lines += ["()", "quit", "/display/objects/display", name]
    return lines


def save(path):
    path = path.replace("\\", "/")
    lines = ["/display/save-picture", path]
    if os.path.exists(path):
        lines.append("yes")
    return lines


def html_stems():
    text = open(HTML, encoding="utf-8").read()
    srcs = re.findall(r'src="figs12cells/i300/([^"]+\.png)"', text)
    return [s[:-4] for s in srcs]


def build(step):
    out = ROOT + "/figs12cells/fluent_native/" + step
    stems = html_stems()
    missing = [s for s in stems if base_of(s) not in SPEC]
    if missing:
        raise SystemExit("no geometry for " + ", ".join(missing))
    lines = [
        "; %s contours. One new object per picture so Auto Range follows that surface." % step,
        "/preferences/graphics/colormap-settings/number-format-type",
        "general",
        "/preferences/graphics/colormap-settings/number-format-precision",
        "5",
        "/display/set/contours/auto-range",
        "yes",
    ]
    made = set()
    clips = set()

    def ensure_plane(orient, value):
        nonlocal lines
        name = surf_name(orient, value)
        if name in made or name in REUSE.values():
            made.add(name)
            return name
        lines.append("/surface/plane-surface %s %s %.8g" % (name, orient, value))
        made.add(name)
        return name

    def ensure_clip(src):
        nonlocal lines
        name = "c" + src
        if name in clips:
            return name
        lines += ["/surface/iso-clip", "y-coordinate", name, src, "0", "0.0024"]
        clips.add(name)
        return name

    def ensure_slit(parent, center):
        nonlocal lines
        src = ensure_clip(parent) if center else parent
        tag = src + "p", src + "n"
        for name, a, b in ((tag[0], 0.0011, 0.0015), (tag[1], -0.0015, -0.0011)):
            if name not in clips:
                lines += ["/surface/iso-clip", "x-coordinate", name, src, "%.8g" % a, "%.8g" % b]
                clips.add(name)
        return [tag[0], tag[1]]

    # Create every surface before the first picture, so a later display error
    # still leaves the surfaces for a resume journal.
    for base, (orient, value, kind, zone) in SPEC.items():
        if kind == "zone":
            continue
        parent = ensure_plane(orient, value)
        if kind == "slit":
            ensure_slit(parent, False)
            ensure_slit(parent, True)
        else:
            ensure_clip(parent)
    for base, (orient, value, kind, zone) in SPEC.items():
        if kind == "zone":
            ensure_clip(zone)
    lines.append('(display "SURFACES-DONE")')

    n = 0
    for stem in stems:
        base = base_of(stem)
        orient, value, kind, zone = SPEC[base]
        center = stem.endswith("_center")
        if kind == "zone":
            surfaces = [ensure_clip(zone) if center else zone]
        elif kind == "slit":
            parent = surf_name(orient, value)
            surfaces = ensure_slit(parent, center)
        else:
            parent = surf_name(orient, value)
            surfaces = [ensure_clip(parent) if center else parent]
        fields = ["temperature"]
        if needs_v(stem):
            fields.append("velocity-magnitude")
        for field in fields:
            n += 1
            obj = "p%03d%s" % (n, "t" if field == "temperature" else "v")
            suffix = "_T" if field == "temperature" else "_V"
            lines.append('(display "SHOT %s%s")' % (stem, suffix))
            lines += create_obj(obj, field, surfaces)
            lines += camera(orient, value)
            lines += save(out + "/" + stem + suffix + ".png")
    lines.append('(display "CAPTURE-%s-DONE")' % step.upper())
    path = os.path.join(CASE, "capture_%s.jou" % step)
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(path, "commands", len(lines), "pictures", n)
    return path


def build_local(step):
    """Resave existing objects with per-surface range and explicit filenames."""
    out = ROOT + "/figs12cells/" + step
    stems = html_stems()
    lines = [
        "; %s resave. Auto Range on, Global Range off, one variable per file." % step,
    ]
    n = 0
    for stem in stems:
        base = base_of(stem)
        orient, value, kind, zone = SPEC[base]
        fields = ["temperature"]
        if needs_v(stem):
            fields.append("velocity-magnitude")
        for field in fields:
            n += 1
            obj = "p%03d%s" % (n, "t" if field == "temperature" else "v")
            png = picture_name(stem, field)
            lines.append('(display "LOCAL %s")' % png)
            lines += edit_range(obj)
            lines += camera(orient, value)
            lines += save(out + "/" + png)
    lines.append('(display "CAPTURE-%s-LOCAL-DONE")' % step.upper())
    path = os.path.join(CASE, "capture_%s_local.jou" % step)
    with open(path, "w", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print(path, "commands", len(lines), "pictures", n)
    return path


if __name__ == "__main__":
    build_local("i300")
