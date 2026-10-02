# -*- coding: utf-8 -*-
"""Build STEP groups for SpaceClaim layout renders.

GPU cold plates are copies of asm_0921.stp. Grace plates, PCB, manifolds
and the proposed lid return are schematic solids, not measured parts.
"""
from pathlib import Path

from build123d import Box, Compound, Pos, export_step, import_step

ROOT = Path(__file__).resolve().parent
STP = ROOT / "asm_0921.stp"
OUT = ROOT / "out" / "asm0921" / "step_layout"


def block(x, y, z, dx, dy, dz):
    return Pos(x + dx / 2.0, y + dy / 2.0, z + dz / 2.0) * Box(dx, dy, dz)


def arrow_y(x, y, z, dx, dy, dz, sign):
    """A shaft plus a wider head. sign > 0 points toward +Y."""
    head = dy * 0.38
    shaft = dy - head
    if sign > 0:
        return [
            block(x, y, z, dx, shaft, dz),
            block(x - dx * 0.45, y + shaft, z - dz * 0.35, dx * 1.9, head, dz * 1.7),
        ]
    return [
        block(x, y + head, z, dx, shaft, dz),
        block(x - dx * 0.45, y, z - dz * 0.35, dx * 1.9, head, dz * 1.7),
    ]


def save(name, shapes):
    path = OUT / name
    export_step(Compound(children=list(shapes)), str(path))
    print("wrote", path.name, len(shapes))


def load_plate():
    last = None
    for i in range(4):
        try:
            asm = import_step(str(STP))
            solids = sorted(asm.solids(), key=lambda s: s.bounding_box().min.Z)
            if len(solids) != 3:
                raise RuntimeError("expected 3 solids, got %s" % len(solids))
            return solids
        except Exception as exc:
            last = exc
            print("import retry", i, exc)
    raise last


def plate_scene(solids):
    """One cold plate, chip footprint exploded below, proposed ports on the lid."""
    pkg = [block(0, 0, -42, 95, 75, 2)]
    dies = [
        block(19, 23.5, -40, 27, 28, 1.6),
        block(49, 23.5, -40, 27, 28, 1.6),
    ]
    hbms = []
    for x in (5.0, 79.0):
        for y in (13.5, 25.5, 37.5, 49.5):
            hbms.append(block(x, y, -40, 11, 10, 1.6))

    # Inlet adapter on the Y=75 edge, then a tube toward the rear (+Y).
    supply = [block(34, 75, 6.5, 20, 14, 8)]
    supply += arrow_y(40, 89, 8.5, 8, 28, 6, +1)

    # Lid return along the die gap, then a higher tube also toward +Y.
    ret = [block(44, 2, 12.5, 8, 73, 6)]
    ret += arrow_y(52, 89, 14.5, 8, 28, 6, +1)
    save("plate_pkg.stp", pkg)
    save("plate_die.stp", dies)
    save("plate_hbm.stp", hbms)
    save("plate_cu.stp", solids)
    save("plate_supply.stp", supply)
    save("plate_return.stp", ret)


def tray_scene(solids):
    """Two NVL2 boards. +Y is the rear panel. GPU plates are the real STEP."""
    boards = (0.0, 310.0)
    pcb, grace, gpus = [], [], []
    supply, ret = [], []

    for bx in boards:
        pcb.append(block(bx, 0, 0, 250, 290, 2.0))
        # Grace / CPU cold plate: larger footprint toward the front. Size is schematic.
        grace.append(block(bx + 25, 18, 2.0, 200, 125, 9.0))
        for gx in (bx + 25, bx + 130):
            for s in solids:
                gpus.append(Pos(gx, 168, 2.0) * s)
            # Short GPU supply: rear edge of the plate (local y=75) into the header.
            supply.append(block(gx + 30, 245, 10, 14, 36, 7))
            supply += arrow_y(gx + 33, 228, 11, 8, 16, 5, -1)
            # Lid return rib + short tube up to the return header.
            ret.append(block(gx + 44, 172, 14.5, 8, 70, 5))
            ret.append(block(gx + 56, 245, 18, 8, 40, 6))
            ret += arrow_y(gx + 56, 268, 18.5, 7, 16, 5, +1)
        # Grace supply runs in the left margin, past the GPUs, from the rear header.
        supply.append(block(bx + 6, 80, 10, 8, 200, 7))
        supply.append(block(bx + 6, 143, 10, 40, 8, 7))
        supply += arrow_y(bx + 28, 130, 11, 8, 14, 5, -1)
        # Grace return runs in the right margin.
        ret.append(block(bx + 236, 80, 18, 8, 200, 6))
        ret.append(block(bx + 196, 143, 18, 48, 8, 6))
        ret += arrow_y(bx + 214, 151, 18.5, 8, 14, 5, +1)

    # Rear headers span both boards. Supply is the nearer bar, return is behind it.
    supply.append(block(-8, 286, 8, 636, 16, 12))
    ret.append(block(-8, 312, 16, 636, 14, 10))
    # Rear panel, inlet UQD above, outlet UQD below.
    rear = [block(-20, 334, 0, 660, 8, 42)]
    supply.append(block(300, 326, 26, 22, 16, 12))
    ret.append(block(300, 326, 6, 22, 16, 10))

    save("tray_pcb.stp", pcb)
    save("tray_grace.stp", grace)
    save("tray_gpu.stp", gpus)
    save("tray_supply.stp", supply)
    save("tray_return.stp", ret)
    save("tray_rear.stp", rear)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    solids = load_plate()
    plate_scene(solids)
    tray_scene(solids)
    print("ok")


if __name__ == "__main__":
    main()
