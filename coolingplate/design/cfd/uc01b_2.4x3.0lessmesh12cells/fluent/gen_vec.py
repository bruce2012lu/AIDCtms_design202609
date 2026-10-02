import build_report_jou as b
import make_capture_jou as m

# X-normal cuts already in the i600 session. vx0 exists.
JOBS = [
    ("vx0", "yzp0", "x0_TV", True),
    ("vx0c", "yzp0c", "x0_TV_center", False),
    ("vxm", "yzp566", "xmid_TV", False),
    ("vxmc", "yzp566c", "xmid_TV_center", False),
    ("vx13", "yzp1300", "x13_TV", False),
    ("vx13c", "yzp1300c", "x13_TV_center", False),
    ("vx04", "yzp400", "x04_TV", False),
    ("vx04c", "yzp400c", "x04_TV_center", False),
    ("vx11", "yzp1100", "x11_TV", False),
    ("vx11c", "yzp1100c", "x11_TV_center", False),
]


def create_vector(name, surf):
    return [
        "/display/objects/create",
        "vector",
        name,
        "vector-field",
        "velocity",
        "field",
        "velocity-magnitude",
        "surfaces-list",
        surf,
        "()",
        "vector-opt",
        "in-plane?",
        "yes",
        "quit",
        "skip",
        "12",
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


lines = ["(display \"VEC-BATCH\")"]
for name, surf, stem, exists in JOBS:
    lines.append('(display "SHOT %s")' % name)
    lines += b.annotation_lines(b.annotation_text(stem))
    if not exists:
        lines += create_vector(name, surf)
    lines += ["/display/objects/display", name]
    orient, value, kind, zone = m.SPEC[m.base_of(stem)]
    lines += m.camera(orient, value)
    png = b.OUT_PARENT + "/i600/" + m.base_of(stem).replace("_TV", "") 
    # picture name: x0_velocity_vector.png / x0_center_velocity_vector.png
    center = "_center" if stem.endswith("_center") else ""
    base = m.base_of(stem)
    base = base[:-3] if base.endswith("_TV") else base
    png = "%s/i600/%s%s_velocity_vector.png" % (b.OUT_PARENT, base, center)
    lines += b.save_lines(png)
lines.append('(display "VEC-BATCH-DONE")')
b.write_jou(b.CASE + "/vec_batch.jou", lines)
print("jobs", len(JOBS))
