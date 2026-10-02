# -*- coding: utf-8 -*-
"""One hex cube to probe Fluent 26.1 msh syntax."""
import os

here = os.path.dirname(os.path.abspath(__file__))
out = os.path.join(here, "tiny_cube.msh")
# unit cube 1 mm, nodes 1-8
nodes = [
    (0, 0, 0), (1e-3, 0, 0), (1e-3, 1e-3, 0), (0, 1e-3, 0),
    (0, 0, 1e-3), (1e-3, 0, 1e-3), (1e-3, 1e-3, 1e-3), (0, 1e-3, 1e-3),
]
# faces: n1 n2 n3 n4 c0 c1
faces = [
    # bottom k-, inlet
    ((1, 4, 3, 2), 1, 0, 10, "inlet_jet"),
    # top k+, outlet
    ((5, 6, 7, 8), 1, 0, 5, "return_slot"),
    # -x
    ((1, 5, 8, 4), 1, 0, 3, "wall_imp"),
    # +x
    ((2, 3, 7, 6), 1, 0, 3, "fin"),
    # -y
    ((1, 2, 6, 5), 1, 0, 3, "wall_lid"),
    # +y
    ((4, 8, 7, 3), 1, 0, 7, "SYM"),
]
lines = [
    '(0 "tiny cube")',
    "(2 3)",
    "(10 (0 1 8 0 3))",
    "(12 (0 1 1 0 0))",
    "(13 (0 1 6 0 0))",
    "(10 (1 1 8 1 3))",
    "(",
]
for x, y, z in nodes:
    lines.append(f"{x:.10e} {y:.10e} {z:.10e}")
lines += [")", ")", "(12 (2 1 1 1 4))"]
zid = 3
f0 = 1
for nids, c0, c1, bcc, name in faces:
    lines.append(f"(13 ({zid} {f0} {f0} {bcc} 4))")
    lines.append("(")
    lines.append(f"{nids[0]} {nids[1]} {nids[2]} {nids[3]} {c0} {c1}")
    lines.append(")")
    lines.append(")")
    f0 += 1
    zid += 1
lines.append("(45 (2 fluid fluid)())")
zid = 3
for nids, c0, c1, bcc, name in faces:
    kind = {10: "velocity-inlet", 5: "pressure-outlet", 3: "wall", 7: "symmetry"}[bcc]
    lines.append(f"(45 ({zid} {kind} {name})())")
    zid += 1
with open(out, "w", encoding="ascii", newline="\n") as f:
    f.write("\n".join(lines) + "\n")
print("WROTE", out)
