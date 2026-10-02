"""Journals that follow fluent-gui-capture: per-surface range, face values, one variable per file."""
import os
import re

import make_capture_jou as m

ROOT = m.ROOT
CASE = m.CASE
OUT_PARENT = ROOT + "/figs12cells"


def mm_text(value):
    mm = float(value) * 1000.0
    text = ("%.4f" % mm).rstrip("0").rstrip(".")
    if text in ("-0", ""):
        return "0"
    return text


def place_text(stem):
    base = m.base_of(stem)
    orient, value, kind, zone = m.SPEC[base]
    mm = mm_text(value)
    if zone == "wall_heat":
        place = "z=%s mm 底面" % mm
    elif zone == "outlet_y_front" or zone == "outlet_y_back":
        place = "Y=%s mm 出口" % mm
    elif zone == "return_slot":
        place = "z=%s mm 顶面" % mm
    elif orient == "xy":
        place = "z=%s mm" % mm
    elif orient == "yz":
        place = "x=%s mm" % mm
    else:
        place = "Y=%s mm" % mm
    if stem.endswith("_center"):
        place += " 中部单元"
    return place


def var_text(field):
    return "温度" if field == "temperature" else "速度"


def surf_name(orient, value):
    um = int(round(float(value) * 1e6))
    sign = "m" if um < 0 else "p"
    return "%s%s%d" % (orient, sign, abs(um))


ZONE_CLIP = {
    "wall_heat": "whc",
    "outlet_y_front": "oyfc",
    "outlet_y_back": "oybc",
    "return_slot": "rsc",
}


def save_lines(path):
    path = path.replace("\\", "/")
    lines = ["/display/save-picture", path]
    if os.path.exists(path):
        lines.append("yes")
    return lines


def create_obj(name, field, surfaces, boundary):
    lines = [
        "/display/objects/create",
        "contour",
        name,
        "field",
        field,
        "surfaces-list",
    ]
    lines.extend(surfaces)
    lines += [
        "()",
        "coloring",
        "smooth",
        "node-values?",
        "no" if boundary else "yes",
    ]
    if boundary:
        lines += ["boundary-values?", "yes"]
    lines += [
        "range-option",
        "auto-range-on",
        "global-range?",
        "no",
        "quit",
        "annotations-list",
        "1",
        "text-0",
        "quit",
        "/display/objects/display",
        name,
    ]
    return lines


def write_jou(path, lines):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # Fluent on this Chinese Windows reads journals as GBK. UTF-8 Chinese breaks the string.
    with open(path, "w", newline="\n", encoding="gbk") as handle:
        handle.write("\n".join(lines) + "\n")
    print(path, "lines", len(lines))


def annotation_text(stem):
    """ASCII only. Han in this annotation draws as boxes, including with Microsoft YaHei."""
    base = m.base_of(stem)
    orient, value, kind, zone = m.SPEC[base]
    mm = mm_text(value)
    if orient == "yz":
        place = "x=%s mm" % mm
    elif orient == "zx":
        place = "Y=%s mm" % mm
    else:
        place = "z=%s mm" % mm
    if stem.endswith("_center"):
        place += " center"
    return place


def annotation_lines(text):
    if '"' in text:
        raise SystemExit("annotation text contains a quote")
    return [
        "/display/annotation/edit",
        "text-0",
        "text",
        '"%s"' % text,
        "quit",
    ]


def font24():
    return [
        "/display/annotation/edit",
        "text-0",
        "font-name",
        '"Microsoft YaHei"',
        "font-size",
        '"24"',
        "quit",
    ]


def place_fresh_annotation():
    """After a case read the old annotation is gone. One real mouse drag finishes annotate."""
    return [
        '(display "ANNO-PICK")',
        "/display/annotation/annotate",
        '"x=0 mm"',
        '"None"',
        '(display "ANNO-PLACED")',
        "/display/annotation/edit",
        "text-0",
        "font-size",
        '"24"',
        "quit",
        '(display "FONT24-DONE")',
    ]


def read_case(step, discard):
    name = "uc01b_cht_less_12y_%s.cas.h5" % step
    lines = ["/file/read-case-data", CASE + "/" + name]
    if discard:
        lines.append("yes")
    lines.append('(display "CASE-%s-LOADED")' % step.upper())
    return lines


def preferences():
    return [
        "/preferences/graphics/colormap-settings/number-format-type",
        "general",
        "/preferences/graphics/colormap-settings/number-format-precision",
        "5",
    ]


def picture_setup():
    return [
        "/display/set/picture/use-window-resolution?",
        "no",
        "/display/set/picture/x-resolution",
        "2400",
        "/display/set/picture/y-resolution",
        "720",
        '(display "RES-OK")',
    ]


class Surfaces(object):
    def __init__(self, emit=True):
        self.emit = emit
        self.lines = []
        self.made = set()
        self.clips = set()

    def plane(self, orient, value):
        name = surf_name(orient, value)
        if name not in self.made:
            if self.emit:
                self.lines.append(
                    "/surface/plane-surface %s %s %.8g" % (name, orient, value)
                )
            self.made.add(name)
        return name

    def yclip(self, src):
        name = src + "c"
        if name not in self.clips:
            if self.emit:
                self.lines += ["/surface/iso-clip", "y-coordinate", name, src, "0", "0.0024"]
            self.clips.add(name)
        return name

    def slit(self, parent, center):
        src = self.yclip(parent) if center else parent
        names = []
        for tag, lo, hi in ((src + "p", 0.0011, 0.0015), (src + "n", -0.0015, -0.0011)):
            if tag not in self.clips:
                if self.emit:
                    self.lines += [
                        "/surface/iso-clip",
                        "x-coordinate",
                        tag,
                        src,
                        "%.8g" % lo,
                        "%.8g" % hi,
                    ]
                self.clips.add(tag)
            names.append(tag)
        return names

    def zone_clip(self, zone):
        return self.yclip(ZONE_CLIP.get(zone, "c" + zone.replace("_", ""))) if False else self._zone(zone)

    def _zone(self, zone):
        name = ZONE_CLIP[zone]
        if name not in self.clips:
            if self.emit:
                self.lines += ["/surface/iso-clip", "y-coordinate", name, zone, "0", "0.0024"]
            self.clips.add(name)
        return name


def surfaces_for(builder, stem):
    base = m.base_of(stem)
    orient, value, kind, zone = m.SPEC[base]
    center = stem.endswith("_center")
    if kind == "zone":
        return [builder._zone(zone) if center else zone], True
    parent = builder.plane(orient, value)
    if kind == "slit":
        return builder.slit(parent, center), False
    if center:
        return [builder.yclip(parent)], False
    return [parent], False


def picture_block(builder, step, stem, field, obj, boundary, surfaces):
    orient, value, kind, zone = m.SPEC[m.base_of(stem)]
    png = OUT_PARENT + "/" + step + "/" + m.picture_name(stem, field)
    lines = ['(display "SHOT %s %s")' % (step, os.path.basename(png))]
    lines += annotation_lines(annotation_text(stem))
    lines += create_obj(obj, field, surfaces, boundary)
    lines += m.camera(orient, value)
    lines += save_lines(png)
    return lines


def all_pictures(step, prefix, emit_surfaces=True):
    stems = m.html_stems()
    missing = [stem for stem in stems if m.base_of(stem) not in m.SPEC]
    if missing:
        raise SystemExit("no geometry for " + ", ".join(missing))
    builder = Surfaces(emit=emit_surfaces)
    # Create surfaces before pictures so a later object error still leaves them.
    planned = []
    for stem in stems:
        surfaces, boundary = surfaces_for(builder, stem)
        fields = ["temperature"]
        if m.needs_v(stem):
            fields.append("velocity-magnitude")
        for field in fields:
            planned.append((stem, field, surfaces, boundary))
    lines = list(builder.lines)
    lines.append('(display "SURFACES-%s-DONE")' % step.upper())
    n = 0
    for stem, field, surfaces, boundary in planned:
        n += 1
        obj = "%s%03d%s" % (prefix, n, "t" if field == "temperature" else "v")
        lines += picture_block(builder, step, stem, field, obj, boundary, surfaces)
    lines.append('(display "CAPTURE-%s-DONE")' % step.upper())
    return lines, n


def build_fix():
    """Continue in the already loaded i300 session. coloring stays in its own submenu."""
    lines = []
    lines += create_obj("wallface", "temperature", ["wall_heat"], True)
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i300/wall_heat_temperature.png")
    lines.append('(display "WALL-SAVED")')
    lines += picture_setup()
    lines += ["/display/objects/display", "wallface"]
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i300/wall_heat_temperature.png")
    lines.append('(display "WALL-RESAVED")')
    lines.append("/surface/plane-surface yzp0 yz 0")
    lines += create_obj("x0temp", "temperature", ["yzp0"], False)
    lines += m.camera("yz", 0.0)
    lines += save_lines(OUT_PARENT + "/i300/x0_temperature.png")
    lines += create_obj("x0vel", "velocity-magnitude", ["yzp0"], False)
    lines += m.camera("yz", 0.0)
    lines += save_lines(OUT_PARENT + "/i300/x0_velocity.png")
    lines.append('(display "SAMPLE-DONE")')
    write_jou(os.path.join(CASE, "sample_fix.jou"), lines)


def build_sample():
    lines = []
    lines += read_case("i300", False)
    lines += preferences()
    lines += create_obj("wallheat", "temperature", ["wall_heat"], True)
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i300/wall_heat_temperature.png")
    lines.append('(display "WALL-SAVED")')
    lines += picture_setup()
    lines += ["/display/objects/display", "wallheat"]
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i300/wall_heat_temperature.png")
    lines.append('(display "WALL-RESAVED")')
    lines.append("/surface/plane-surface yzp0 yz 0")
    lines += create_obj("x0temp", "temperature", ["yzp0"], False)
    lines += m.camera("yz", 0.0)
    lines += save_lines(OUT_PARENT + "/i300/x0_temperature.png")
    lines += create_obj("x0vel", "velocity-magnitude", ["yzp0"], False)
    lines += m.camera("yz", 0.0)
    lines += save_lines(OUT_PARENT + "/i300/x0_velocity.png")
    lines.append('(display "SAMPLE-DONE")')
    write_jou(os.path.join(CASE, "sample_capture.jou"), lines)


def build_anno_trial():
    """YaHei on the object that already lists text-0. Do not create annochk again."""
    lines = ['(display "ANNO-TRIAL")']
    lines += font24()
    lines += annotation_lines(annotation_text("wall_heat_T"))
    lines += ["/display/objects/display", "annochk"]
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i300/anno_check.png")
    lines.append('(display "ANNO-TRIAL-DONE")')
    write_jou(os.path.join(CASE, "anno_trial.jou"), lines)


def build_resume():
    """i300 is already loaded and its surfaces exist. i600 is read after those pictures."""
    lines = ["; i300 pictures on the open case, then i600. Annotation text-0, font 24."]
    lines += font24()
    pic, n300 = all_pictures("i300", "c", emit_surfaces=False)
    lines += pic
    lines += read_case("i600", True)
    lines += preferences()
    lines += picture_setup()
    surfaces = Surfaces(emit=True)
    stems = m.html_stems()
    planned = []
    for stem in stems:
        surfs, boundary = surfaces_for(surfaces, stem)
        fields = ["temperature"]
        if m.needs_v(stem):
            fields.append("velocity-magnitude")
        for field in fields:
            planned.append((stem, field, surfs, boundary))
    lines += surfaces.lines
    lines.append('(display "SURFACES-I600-DONE")')
    lines += place_fresh_annotation()
    n600 = 0
    for stem, field, surfs, boundary in planned:
        n600 += 1
        obj = "d%03d%s" % (n600, "t" if field == "temperature" else "v")
        lines += picture_block(surfaces, "i600", stem, field, obj, boundary, surfs)
    lines.append('(display "CAPTURE-I600-DONE")')
    lines.append('(display "CAPTURE-ALL-DONE")')
    write_jou(os.path.join(CASE, "report_resume.jou"), lines)
    print("pictures", n300, n600)


def build_smooth_probe():
    """Two i600 pictures. Confirm smooth does not need quit, then the full set can run."""
    lines = ['(display "SMOOTH-PROBE")']
    lines += annotation_lines("z=-2.08 mm")
    lines += create_obj("pwall", "temperature", ["wall_heat"], True)
    lines += m.camera("xy", -0.00208)
    lines += save_lines(OUT_PARENT + "/i600/probe_wall_temperature.png")
    lines += annotation_lines("x=0 mm")
    lines += create_obj("px0t", "temperature", ["yzp0"], False)
    lines += m.camera("yz", 0.0)
    lines += save_lines(OUT_PARENT + "/i600/probe_x0_temperature.png")
    lines.append('(display "SMOOTH-PROBE-DONE")')
    write_jou(os.path.join(CASE, "smooth_probe.jou"), lines)


def build_i600_smooth():
    """i600 is already loaded. Smooth cuts, face values on walls. Do not touch i300 pictures."""
    lines = ["; i600 only. smooth coloring, node values on cuts, face values on walls."]
    lines += [
        "/preferences/graphics/graphics-effects/grid-plane-enabled",
        "no",
    ]
    lines += font24()
    pic, n600 = all_pictures("i600", "f", emit_surfaces=False)
    lines += pic
    lines.append('(display "I600-SMOOTH-DONE")')
    write_jou(os.path.join(CASE, "i600_smooth.jou"), lines)
    print("i600 pictures", n600)


def build_batch():
    lines = ["; i300 then i600. Per-surface range, face values on boundaries, one variable per file."]
    lines += read_case("i300", True)
    lines += preferences()
    lines += picture_setup()
    pic, n300 = all_pictures("i300", "a")
    lines += pic
    lines += read_case("i600", True)
    lines += preferences()
    pic, n600 = all_pictures("i600", "b")
    lines += pic
    lines.append('(display "CAPTURE-ALL-DONE")')
    write_jou(os.path.join(CASE, "report_capture.jou"), lines)
    print("pictures", n300, n600)


if __name__ == "__main__":
    build_sample()
    build_fix()
    build_batch()
