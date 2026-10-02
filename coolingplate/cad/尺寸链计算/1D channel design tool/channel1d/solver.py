# -*- coding: utf-8 -*-
"""Segmented copper / fluid march for one heated column.

The march is iterative. Copper rows are relaxed (0.45 new + 0.55 old) because
axial conduction uses the previous field. Publish a result only after Tmean
and the heated-wall span change by less than about 0.05 K between two
iteration counts. This screen runs cooler and flatter than a CFD face
temperature and is not a test result.

A center-fed channel is split at mid-length. Each leg receives half the
channel flow. Heat follows the local heated mask, which is symmetric about
mid-length for the HBM stack pattern, so the leg fluid rise stays equal to
the column fluid rise.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from channel1d.bulk import evaluate, fanning_f_re, fin_efficiency, hydraulic_diameter, shah_pressure_drop
from channel1d.fluid import Fluid
from channel1d.schemes import scheme_kinds


@dataclass(frozen=True)
class ColumnDesign:
    """One rectangular-channel column with an explicit land, width, and rib."""

    fluid: Fluid
    k_copper: float
    tin_c: float
    flow_lpm: float
    power_w: float
    column_width_m: float
    column_length_m: float
    heated_length_m: float
    channel_height_m: float
    base_m: float
    n: int
    width_m: float
    rib_m: float
    land_m: float
    stacks_m: tuple[tuple[float, float], ...]
    k_split: float = 1.5

    def flux(self) -> float:
        """Uniform flux on the heated footprint, W/m^2."""
        return self.power_w / (self.column_width_m * self.heated_length_m)


def cell_widths(design: ColumnDesign) -> np.ndarray:
    """Heat-share width of each channel, rib midplane to rib midplane."""
    n = design.n
    widths = np.empty(n)
    if n == 1:
        widths[0] = design.column_width_m
        return widths
    edge = design.land_m + design.width_m + design.rib_m / 2.0
    widths[0] = edge
    widths[-1] = edge
    if n > 2:
        widths[1:-1] = design.width_m + design.rib_m
    return widths


def heated_mask(design: ColumnDesign, ny: int) -> np.ndarray:
    """True on segments that overlap a heated stack."""
    dy = design.column_length_m / ny
    y0 = np.arange(ny) * dy
    y1 = y0 + dy
    mask = np.zeros(ny, dtype=bool)
    for start, stop in design.stacks_m:
        mask |= (y1 > start + 1e-12) & (y0 < stop - 1e-12)
    return mask


def solve(
    design: ColumnDesign,
    scheme: str,
    *,
    ny: int = 50,
    iters: int = 6400,
    couple: bool = True,
) -> dict:
    """March fluid and copper. ``iters`` is the under-relaxed iteration count."""
    fluid = design.fluid
    n = design.n
    width = design.width_m
    rib = design.rib_m
    height = design.channel_height_m
    kinds = scheme_kinds(n, scheme)
    widths = cell_widths(design)
    dy = design.column_length_m / ny
    mask = heated_mask(design, ny)
    mdot = fluid.mass_flow(design.flow_lpm)
    m_ch = mdot / n
    dh = hydraulic_diameter(width, height)
    prandtl = fluid.prandtl()
    area = width * height
    velocity = m_ch / (fluid.rho * area)
    reynolds = fluid.rho * velocity * dh / fluid.mu
    velocity_leg = 0.5 * velocity
    reynolds_leg = 0.5 * reynolds
    flux = design.flux()

    dist = width + rib
    g_lat = (design.k_copper * design.base_m * dy / dist) + (design.k_copper * height * dy / rib)
    if not couple:
        g_lat = 0.0
    a_ax = design.base_m * widths.copy() + height * (rib / 2.0)
    g_ax = design.k_copper * a_ax / dy

    def local_h(re_local: float, x_m: float) -> tuple[float, float]:
        x_use = max(x_m, 0.5 * dy)
        graetz = dh / x_use * re_local * prandtl
        nusselt = max(4.0, 1.86 * graetz ** (1.0 / 3.0))
        h_coef = nusselt * fluid.k / dh
        eta = fin_efficiency(h_coef, rib, height, design.k_copper)
        return h_coef, eta

    h_arr = np.zeros((n, ny))
    aw = np.zeros((n, ny))
    for i, kind in enumerate(kinds):
        for j in range(ny):
            yc = (j + 0.5) * dy
            if kind == "plus":
                x_m, re_local = yc, reynolds
            elif kind == "minus":
                x_m, re_local = design.column_length_m - yc, reynolds
            else:
                x_m, re_local = abs(yc - 0.5 * design.column_length_m), reynolds_leg
            h_coef, eta = local_h(re_local, x_m)
            h_arr[i, j] = h_coef
            aw[i, j] = (2.0 * width + 2.0 * height * eta) * dy

    tw = np.full((n, ny), design.tin_c + 15.0)
    tf = np.full((n, ny), design.tin_c + 3.0)

    def march_channel(i: int) -> np.ndarray:
        kind = kinds[i]
        if kind == "center":
            legs = (
                (list(range(ny // 2 - 1, -1, -1)), 0.5 * m_ch),
                (list(range(ny // 2, ny)), 0.5 * m_ch),
            )
        elif kind == "plus":
            legs = ((list(range(ny)), m_ch),)
        else:
            legs = ((list(range(ny - 1, -1, -1)), m_ch),)
        out = np.zeros(ny)
        for order, mass in legs:
            tin_seg = design.tin_c
            for j in order:
                ua = h_arr[i, j] * aw[i, j]
                denom = mass * fluid.cp + 0.5 * ua
                tout = (tin_seg * (mass * fluid.cp - 0.5 * ua) + ua * tw[i, j]) / denom
                out[j] = 0.5 * (tin_seg + tout)
                tin_seg = tout
        return out

    for _ in range(iters):
        for i in range(n):
            tf[i] = march_channel(i)
        tw_new = tw.copy()
        for j in range(ny):
            lower = np.zeros(n)
            diag = np.zeros(n)
            upper = np.zeros(n)
            rhs = np.zeros(n)
            for i in range(n):
                ua = h_arr[i, j] * aw[i, j]
                gl = g_lat if i > 0 else 0.0
                gr = g_lat if i < n - 1 else 0.0
                gap = g_ax[i] if j > 0 else 0.0
                gan = g_ax[i] if j < ny - 1 else 0.0
                diag[i] = gl + gr + gap + gan + ua
                if i > 0:
                    lower[i] = -gl
                if i < n - 1:
                    upper[i] = -gr
                heat = flux * widths[i] * dy if mask[j] else 0.0
                rhs[i] = heat + ua * tf[i, j]
                if j > 0:
                    rhs[i] += gap * tw[i, j - 1]
                if j < ny - 1:
                    rhs[i] += gan * tw[i, j + 1]
            for i in range(1, n):
                factor = lower[i] / diag[i - 1]
                diag[i] -= factor * upper[i - 1]
                rhs[i] -= factor * rhs[i - 1]
            tw_new[-1, j] = rhs[-1] / diag[-1]
            for i in range(n - 2, -1, -1):
                tw_new[i, j] = (rhs[i] - upper[i] * tw_new[i + 1, j]) / diag[i]
        tw = 0.45 * tw_new + 0.55 * tw

    weights = np.where(mask[None, :], widths[:, None], 0.0)
    tmean = float((tw * weights).sum() / weights.sum())
    heated = tw[:, mask]
    tmin = float(heated.min())
    tmax = float(heated.max())
    stacks = []
    y0 = np.arange(ny) * dy
    y1 = y0 + dy
    for start, stop in design.stacks_m:
        sel = (y1 > start + 1e-12) & (y0 < stop - 1e-12)
        ww = np.where(sel[None, :], widths[:, None], 0.0)
        stacks.append(
            {
                "Tmean": float((tw * ww).sum() / ww.sum()),
                "Tmin": float(tw[:, sel].min()),
                "Tmax": float(tw[:, sel].max()),
            }
        )
    stack_means = [item["Tmean"] for item in stacks]
    tf_out = []
    for i, kind in enumerate(kinds):
        if kind == "plus":
            tf_out.append(float(tf[i, -1]))
        elif kind == "minus":
            tf_out.append(float(tf[i, 0]))
        else:
            tf_out.append(float(max(tf[i, 0], tf[i, -1])))
    bulk = evaluate(
        fluid,
        n=n,
        width_m=width,
        rib_m=rib,
        height_m=height,
        heated_length_m=design.heated_length_m,
        column_length_m=design.column_length_m,
        flow_lpm=design.flow_lpm,
        power_w=design.power_w,
        k_copper=design.k_copper,
    )
    f_re = fanning_f_re(width, height)
    dp_slot = shah_pressure_drop(f_re, fluid.mu, design.column_length_m, velocity, dh)
    n_center = sum(kind == "center" for kind in kinds)
    if n_center:
        dp_leg = shah_pressure_drop(f_re, fluid.mu, 0.5 * design.column_length_m, velocity_leg, dh)
        dp_split = design.k_split * fluid.rho * velocity_leg ** 2 / 2.0
    else:
        dp_leg = 0.0
        dp_split = 0.0
    return {
        "scheme": scheme,
        "n": n,
        "ny": ny,
        "iters": iters,
        "kinds": kinds,
        "V_ch": velocity,
        "V_leg": velocity_leg,
        "Re": reynolds,
        "dP_slot_Pa": dp_slot,
        "dP_leg_Pa": dp_leg,
        "dP_split_Pa": dp_split,
        "dP_branch_Pa": max(dp_slot, dp_leg + dp_split),
        "k_split_assumed": design.k_split,
        "Tmin": tmin,
        "Tmean": tmean,
        "Tmax": tmax,
        "dT": tmax - tmin,
        "dT_stacks": max(stack_means) - min(stack_means),
        "stacks": stacks,
        "Tf_out_max": max(tf_out),
        "bulk": bulk,
        "couple": couple,
    }
