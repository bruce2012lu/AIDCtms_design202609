# -*- coding: utf-8 -*-
"""Concept solids for CP-GRACE-MC-01, Y-staggered channels.

Report axes: +X left fitting to right fitting, +Y toward the rear panel.
Odd channels flow +Y, even channels flow -Y. Y-ends are walled; the
cover solids are the Z-port feeders, not axial plenums.

Overview fins are widened so the channel field reads at plate scale.
The close-up uses the report pitch: 48 grooves, 0.40 mm wide, 0.80 mm pitch.
"""
from pathlib import Path

from build123d import Box, Compound, Pos, export_step

OUT = Path(__file__).resolve().parent / "out" / "grace" / "step"


def block(x, y, z, dx, dy, dz):
    return Pos(x + dx / 2.0, y + dy / 2.0, z + dz / 2.0) * Box(dx, dy, dz)


def save(name, shapes):
    path = OUT / name
    export_step(Compound(children=list(shapes)), str(path))
    print(name, len(shapes))


def ribs(x0, y0, z, n, pitch, width, length, height):
    return [
        block(x0 + i * pitch, y0, z, width, length, height)
        for i in range(n)
    ]


def overview():
    """Exploded plate. Fins widened for the picture; captions say so."""
    pkg = [block(0, 0, -30, 200, 120, 2)]
    die = [block(80, 44, -28, 40, 32, 1.4)]
    mem = [block(14, 25, -28, 50, 70, 1.2), block(136, 25, -28, 50, 70, 1.2)]
    base = [block(0, 0, 0, 200, 120, 2.0)]
    # 16 ribs across 40 mm so the CPU field is visible. Real design is 48 x 0.40.
    cpu = ribs(80.4, 44, 2.0, 16, 2.40, 1.15, 32, 1.2)
    mem_r = ribs(18, 25, 2.0, 6, 7.0, 1.6, 70, 0.8)
    mem_r += ribs(140, 25, 2.0, 6, 7.0, 1.6, 70, 0.8)
    # Cover feeders float between base and lid.
    # Supply: left rail, front band (odd / +Y), rear band (even / -Y), rear artery.
    supply = [block(6.5, 18, 8.2, 7, 84, 4)]
    supply += [block(-28, 48, 8.2, 36, 16, 5)]
    supply += [block(14, 103, 8.5, 172, 9, 2.2)]
    supply += [block(80, 41, 8.6, 40, 8, 2.0)]
    supply += [block(80, 70, 8.6, 40, 8, 2.0)]
    supply += [block(16, 22, 8.6, 48, 6, 2.0)]
    supply += [block(136, 22, 8.6, 50, 6, 2.0)]
    supply += [block(16, 90, 8.6, 48, 8, 2.0)]
    supply += [block(136, 90, 8.6, 50, 8, 2.0)]
    # Return: right rail, front band (even), rear band (odd), front artery.
    ret = [block(186.5, 18, 8.2, 7, 84, 4)]
    ret += [block(192, 48, 8.2, 36, 16, 5)]
    ret += [block(14, 8, 8.5, 172, 8, 2.2)]
    ret += [block(80, 31, 8.6, 40, 8, 2.0)]
    ret += [block(80, 79, 8.6, 40, 8, 2.0)]
    ret += [block(16, 16, 8.6, 48, 6, 2.0)]
    ret += [block(136, 16, 8.6, 50, 6, 2.0)]
    ret += [block(16, 98, 8.6, 48, 6, 2.0)]
    ret += [block(136, 98, 8.6, 50, 6, 2.0)]
    lid = [block(0, 0, 16, 200, 120, 2.0)]
    save("ov_pkg.stp", pkg)
    save("ov_die.stp", die)
    save("ov_mem.stp", mem)
    save("ov_base.stp", base)
    save("ov_cpu.stp", cpu)
    save("ov_memrib.stp", mem_r)
    save("ov_supply.stp", supply)
    save("ov_return.stp", ret)
    save("ov_lid.stp", lid)


def plan_view():
    """Cover off, true plan. Zones and plenums, fins still widened."""
    base = [block(0, 0, 0, 200, 120, 2.0)]
    cpu = ribs(80.4, 44, 2.0, 16, 2.40, 1.15, 32, 1.2)
    mem_r = ribs(18, 25, 2.0, 6, 7.0, 1.6, 70, 0.8)
    mem_r += ribs(140, 25, 2.0, 6, 7.0, 1.6, 70, 0.8)
    supply = [block(6.5, 18, 3.2, 7, 84, 3)]
    supply += [block(14, 103, 3.4, 172, 9, 2.0)]
    supply += [block(80, 41, 3.5, 40, 8, 1.8)]
    supply += [block(80, 70, 3.5, 40, 8, 1.8)]
    ret = [block(186.5, 18, 3.2, 7, 84, 3)]
    ret += [block(14, 8, 3.4, 172, 8, 2.0)]
    ret += [block(80, 31, 3.5, 40, 8, 1.8)]
    ret += [block(80, 79, 3.5, 40, 8, 1.8)]
    save("pl_base.stp", base)
    save("pl_cpu.stp", cpu)
    save("pl_memrib.stp", mem_r)
    save("pl_supply.stp", supply)
    save("pl_return.stp", ret)


def closeup():
    """Real 0.40 mm x 0.80 mm pitch, 48 channels, 32 mm along Y.

    Channel i (0-based, small X first) is odd in the report count when i is even:
    report channel 1 flows +Y. Tabs mark the Z-port end, not a through-cut.
    """
    floor = [block(0, 0, 0, 46, 44, 2.0)]
    fins = ribs(3.2, 6.0, 2.0, 49, 0.80, 0.40, 32, 1.2)
    ports = []
    for i in range(48):
        x = 3.6 + i * 0.80
        if i % 2 == 0:
            ports.append(block(x, 4.2, 3.2, 0.40, 1.6, 0.6))
            ports.append(block(x, 38.2, 3.2, 0.40, 1.6, 0.6))
        else:
            ports.append(block(x, 2.4, 3.2, 0.40, 1.6, 0.6))
            ports.append(block(x, 36.4, 3.2, 0.40, 1.6, 0.6))
    save("cu_floor.stp", floor)
    save("cu_fins.stp", fins)
    save("cu_ports.stp", ports)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    overview()
    plan_view()
    closeup()
    print("ok")


if __name__ == "__main__":
    main()
