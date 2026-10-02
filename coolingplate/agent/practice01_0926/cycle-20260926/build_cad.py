# -*- coding: utf-8 -*-
"""按 model.py 的一维几何写出单孔胞和三件冷板。不修改 cad/params。"""
from __future__ import annotations

import sys
from pathlib import Path

from build123d import Align, Box, Compound, Cylinder, Pos, export_step

CYCLE = Path(__file__).resolve().parent
sys.path.insert(0, str(CYCLE.parents[3] / "design" / "calc"))
import model as M  # noqa: E402

OUT = CYCLE / "out" / "cad"
MIN3 = (Align.MIN, Align.MIN, Align.MIN)
OVER = 1.0
G = M.GEO


def cut_batched(solid, cutters, batch=24):
    for i in range(0, len(cutters), batch):
        solid -= Compound(cutters[i:i + batch])
    return solid


def unit_cell(diameter: float):
    sx, sy = G["S_jet_x"], G["S_jet_y"]
    base_h = G["base_cu"] + G["ch_h"]
    base = Box(sx, sy, base_h, align=MIN3)
    slot_h = G["ch_h"] + OVER
    z = G["base_cu"] + slot_h / 2.0
    slots = []
    span = 3 * G["ch_w"] + 2 * (G["ch_p"] - G["ch_w"])
    y0 = (sy - span) / 2.0 + G["ch_w"] / 2.0
    for k in range(3):
        slots.append(Pos(sx / 2.0, y0 + k * G["ch_p"], z) * Box(sx + OVER, G["ch_w"], slot_h))
    base = cut_batched(base, slots)
    lid_h = G["t_lid"]
    lid = Box(sx, sy, lid_h, align=MIN3)
    lid -= Pos(sx / 2.0, sy / 2.0, lid_h / 2.0) * Cylinder(diameter / 2.0, lid_h * 2.0)
    gap = G["H_jet"]
    asm = Compound(children=[
        Pos(0, 0, 0) * base,
        Pos(0, 0, base_h + gap) * lid,
    ])
    return base, lid, asm


def grooves_for_die(ox, oy):
    die_w, die_h = G["die_w"], G["die_h"]
    gw, gd, pitch = G["ch_w"], G["ch_h"], G["ch_p"]
    n = M.N_CH_DIE
    span = (n - 1) * pitch + gw
    y_start = oy + (die_h - span) / 2.0 + gw / 2.0
    land, seg = 1.0, 6.0
    xs = [ox + i * (seg + land) + seg / 2.0 for i in range(4)]
    return [(x, y_start + k * pitch) for k in range(n) for x in xs], seg, gw, gd


def plate():
    pw, ph = G["plate_L"], G["plate_W"]
    base_t = G["t_base"]
    remaining = G["base_cu"]
    base = Box(pw, ph, base_t, align=MIN3)
    cutters = []
    gd = G["ch_h"]
    cut_h = gd + OVER
    z_mid = remaining + cut_h / 2.0
    for i in range(2):
        ox = G["die_a_x"] + i * (G["die_w"] + G["hbi"])
        slots, seg, gw, _gd = grooves_for_die(ox, G["die_a_y"])
        for x, y in slots:
            cutters.append(Pos(x, y, z_mid) * Box(seg, gw, cut_h))
    hw, hh = G["hbm_w"], G["hbm_h"]
    ch_w, ch_d, ch_p, n_side = 0.60, 1.50, 1.30, 8
    span = (n_side - 1) * ch_p + ch_w
    col_lo = G["hbm_y0"]
    col_hi = G["hbm_y0"] + 3 * G["hbm_dy"] + hh
    col_mid = (col_lo + col_hi) / 2.0
    col_len = col_hi - col_lo
    hcut = ch_d + OVER
    for col_x in (G["hbm_x_l"], G["hbm_x_r"]):
        start = col_x + (hw - span) / 2.0 + ch_w / 2.0
        for k in range(n_side):
            cutters.append(Pos(start + k * ch_p, col_mid, remaining + hcut / 2.0)
                           * Box(ch_w, col_len, hcut))
    base = cut_batched(base, cutters)
    rib_h = G["H_jet"] + OVER
    ribs = [Pos(rx, 0.0, base_t - OVER) * Box(G["rib"], ph, rib_h, align=MIN3)
            for rx in (G["rib_x_l"], G["rib_x_r"])]
    base = base + Compound(ribs)

    t = G["t_lid"]
    nozzle = Box(pw, ph, t, align=MIN3)
    holes = []
    through = t * 2.0
    for i in range(2):
        jx = G["jet_a_x"] + i * (G["die_w"] + G["hbi"])
        jy = G["jet_a_y"]
        for ix in range(G["n_jet_x"]):
            for iy in range(G["n_jet_y"]):
                holes.append(Pos(jx + ix * G["S_jet_x"], jy + iy * G["S_jet_y"], t / 2.0)
                             * Cylinder(G["D_jet"] / 2.0, through))
    nozzle = cut_batched(nozzle, holes)

    seam = G["t_braze"]
    frame = Box(pw, ph, seam, align=MIN3)
    inner = Pos(G["rib"], G["rib"], -seam) * Box(pw - 2 * G["rib"], ph - 2 * G["rib"], seam * 3, align=MIN3)
    frame = frame - inner

    asm = Compound(children=[
        Pos(0, 0, 0) * base,
        Pos(0, 0, base_t + G["H_jet"]) * nozzle,
        Pos(0, 0, base_t + G["H_jet"] + t) * frame,
    ], label="CP-B300-JM-01")
    return base, nozzle, frame, asm


def save(name, shape) -> None:
    path = OUT / name
    export_step(shape, str(path))
    print(path.name, path.stat().st_size)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for diameter, tag in ((0.50, "d050"), (0.40, "d040")):
        base, lid, asm = unit_cell(diameter)
        save(f"cell_{tag}_base.step", base)
        save(f"cell_{tag}_lid.step", lid)
        save(f"cell_{tag}_assembly.step", asm)
    base, nozzle, frame, asm = plate()
    save("plate_base.step", base)
    save("plate_nozzle.step", nozzle)
    save("plate_seal.step", frame)
    save("plate_assembly.step", asm)


if __name__ == "__main__":
    main()
