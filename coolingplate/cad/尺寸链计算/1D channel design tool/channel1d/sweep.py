# -*- coding: utf-8 -*-
"""Sweep width and rib inside the column chain and the velocity cap.

For each count, width, and rib, the land is the value that closes
``2*land + n*width + (n-1)*rib = column width``. That land is then checked
against the land floor. A candidate below the floor is dropped. It is not
reported as a closed chain.
"""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from channel1d.bulk import evaluate
from channel1d.chain import ChainLimits, land_to_close, limit_failures
from channel1d.solver import ColumnDesign, solve


def sweep(
    template: ColumnDesign,
    *,
    scheme: str = "center",
    counts: range | list[int] | None = None,
    widths_m: np.ndarray | None = None,
    ribs_m: np.ndarray | None = None,
    ny: int = 25,
    iters: int = 80,
    limits: ChainLimits | None = None,
    max_land_m: float = 1.20e-3,
) -> list[dict]:
    """Return feasible candidates sorted by convection drop, then field span."""
    lim = limits or ChainLimits()
    count_values = list(counts) if counts is not None else list(range(6, 13))
    width_values = widths_m if widths_m is not None else np.round(np.arange(0.40e-3, 1.21e-3, 0.05e-3), 6)
    rib_values = ribs_m if ribs_m is not None else np.round(np.arange(0.30e-3, 1.21e-3, 0.05e-3), 6)
    rows: list[dict] = []
    for n in count_values:
        for width in width_values:
            for rib in rib_values:
                land = land_to_close(n, float(width), float(rib), template.column_width_m)
                if land > max_land_m:
                    continue
                design = replace(template, n=n, width_m=float(width), rib_m=float(rib), land_m=float(land))
                bulk = evaluate(
                    design.fluid,
                    n=n,
                    width_m=float(width),
                    rib_m=float(rib),
                    height_m=design.channel_height_m,
                    heated_length_m=design.heated_length_m,
                    column_length_m=design.column_length_m,
                    flow_lpm=design.flow_lpm,
                    power_w=design.power_w,
                    k_copper=design.k_copper,
                )
                failed = limit_failures(
                    land_m=land,
                    n=n,
                    width_m=float(width),
                    rib_m=float(rib),
                    height_m=design.channel_height_m,
                    column_width_m=design.column_width_m,
                    velocity_m_s=bulk["V"],
                    limits=lim,
                )
                if failed:
                    continue
                field = solve(design, scheme, ny=ny, iters=iters, couple=True)
                rows.append(
                    {
                        "n": n,
                        "width_mm": float(width) * 1e3,
                        "rib_mm": float(rib) * 1e3,
                        "land_mm": land * 1e3,
                        "V": bulk["V"],
                        "dTconv": bulk["dTconv"],
                        "dP_Pa": bulk["dP_Pa"],
                        "dT": field["dT"],
                        "dT_stacks": field["dT_stacks"],
                        "Tmean": field["Tmean"],
                        "scheme": scheme,
                        "ny": ny,
                        "iters": iters,
                    }
                )
    rows.sort(key=lambda row: (row["dTconv"], row["dT"], row["Tmean"]))
    return rows
