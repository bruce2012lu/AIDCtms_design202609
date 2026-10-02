# -*- coding: utf-8 -*-
"""Write icem/uc01b_cht_fine.tin (millimetres) for the open ICEM GUI."""
import math
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "icem", "uc01b_cht_fine.tin")
pts = []
coord = {}


def pt(name, x, y, z, fam="POINT"):
    coord[name] = (x, y, z)
    pts.append(f"prescribed_point {x:.8g} {y:.8g} {z:.8g} family {fam} name {name}")


def crv(name, a, b):
    xa, ya, za = coord[a]
    xb, yb, zb = coord[b]
    return (
        f"define_curve family CRV tetra_size 1e+10 name {name} vertex1 {a} vertex2 {b}\n"
        f"bspline\n2,2,0\n0,0,1,1\n"
        f"{xa:.8g},{ya:.8g},{za:.8g}\n{xb:.8g},{yb:.8g},{zb:.8g}\n"
    )


zs = [("t", -2.08), ("u", -2.0), ("i", 0.0), ("r", 1.5), ("l", 3.5), ("d", 6.0), ("n", 8.0)]
corners = [("00", -1.5, -1.2), ("10", 1.5, -1.2), ("11", 1.5, 1.2), ("01", -1.5, 1.2)]
for tag, z in zs:
    for c, x, y in corners:
        pt(f"{tag}{c}", x, y, z)
pt("p_tim", 0, 0, -2.04, "SOLID_TIM2")
pt("p_cu", 0, 0, -1.0, "SOLID_CU")
pt("p_fluid", 0, 0, 0.75, "FLUID")
for zi, z in (("L", 3.5), ("D", 6.0), ("N", 8.0)):
    for i in range(8):
        a = math.pi * i / 4.0
        pt(f"o{zi}{i}", 0.20 * math.cos(a), 0.20 * math.sin(a), z, "WALL_ORIFICE")
for name, y in (
    ("ym20", -0.20), ("yp20", 0.20), ("ym60", -0.60),
    ("yp60", 0.60), ("ym100", -1.00), ("yp100", 1.00),
):
    pt(f"s0{name}", -1.5, y, 0.0)
    pt(f"s1{name}", 1.5, y, 0.0)

curves = []
order = ["00", "10", "11", "01"]
for tag, _z in zs:
    for i in range(4):
        curves.append(crv(f"e{tag}{i}", tag + order[i], tag + order[(i + 1) % 4]))
for i, c in enumerate(order):
    curves.append(crv(f"v{i}", "t" + c, "n" + c))
for zi in ("L", "D", "N"):
    for i in range(8):
        curves.append(crv(f"c{zi}{i}", f"o{zi}{i}", f"o{zi}{(i + 1) % 8}"))
for name, _y in (
    ("ym20", -0.20), ("yp20", 0.20), ("ym60", -0.60),
    ("yp60", 0.60), ("ym100", -1.00), ("yp100", 1.00),
):
    curves.append(crv(f"sl{name}", f"s0{name}", f"s1{name}"))

text = """// tetin file version 1.1
// UC-01b CHT fine coupon, MILLIMETRES. Circle D=0.40. Geometry, not the volume mesh.
set_triangulation_tolerance 0.001
define_family FLUID color 12109107
define_family SOLID_CU color 16763904
define_family SOLID_TIM2 color 16711680
define_family INLET_JET color 4652601
define_family WALL_ORIFICE color 16663101
define_family SYM color 15434803
define_family GEOM color 16663866
define_family POINT color 14392627
define_family CRV color 3362046
"""
text += "\n".join(pts) + "\n" + "".join(curves)
text += "affix 0\ndefine_model 1e+10 reference_size 1\nreturn\n"
path = os.path.abspath(OUT)
with open(path, "w", encoding="ascii", newline="\n") as f:
    f.write(text)
print(path, "points", len(pts), "curves", len(curves))
