"""Redraw X-normal vectors: fixed length, half the previous scale, half the density, on the velocity contour."""
import build_report_jou as b
import make_capture_jou as m

# scale-f 0.001 was still too long. skip 12 was too dense.
SCALE = "0.0005"
SKIP = "24"
JOBS = [
    ("vx0", "f044v", "x0_TV"),
    ("vx0c", "f046v", "x0_TV_center"),
    ("vxm", "f048v", "xmid_TV"),
    ("vxmc", "f050v", "xmid_TV_center"),
    ("vx13", "f052v", "x13_TV"),
    ("vx13c", "f054v", "x13_TV_center"),
    ("vx04", "f056v", "x04_TV"),
    ("vx04c", "f058v", "x04_TV_center"),
    ("vx11", "f060v", "x11_TV"),
    ("vx11c", "f062v", "x11_TV_center"),
]


def edit_vector(name):
    return [
        "/display/objects/edit",
        name,
        "vector-opt",
        "fixed-length?",
        "yes",
        "quit",
        "scale",
        "auto-scale?",
        "no",
        "scale-f",
        SCALE,
        "quit",
        "skip",
        SKIP,
        "quit",
    ]


lines = ['(display "VEC-SPARSE")']
for name, contour, stem in JOBS:
    orient, value, kind, zone = m.SPEC[m.base_of(stem)]
    center = "_center" if stem.endswith("_center") else ""
    base = m.base_of(stem)
    if base.endswith("_TV"):
        base = base[:-3]
    png = "%s/i600/%s%s_velocity_vector.png" % (b.OUT_PARENT, base, center)
    lines.append('(display "SHOT %s")' % name)
    lines += b.annotation_lines(b.annotation_text(stem))
    lines += edit_vector(name)
    lines += ["/display/objects/display", contour, "/display/objects/add-to-graphics", name]
    lines += m.camera(orient, value)
    lines += b.save_lines(png)
lines.append('(display "VEC-SPARSE-DONE")')
b.write_jou(b.CASE + "/vec_sparse.jou", lines)
print("jobs", len(JOBS), "scale", SCALE, "skip", SKIP)
