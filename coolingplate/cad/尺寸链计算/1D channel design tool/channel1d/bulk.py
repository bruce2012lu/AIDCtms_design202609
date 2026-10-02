# -*- coding: utf-8 -*-
"""Closed-form hydraulics and heat transfer for one rectangular-channel column.

Nusselt number is the Hausen developing-flow expression with a floor of 4,
using the heated length. Pressure drop is the Shah-London fully developed
Fanning friction on the full column length at the full-channel velocity.
"""
from __future__ import annotations

import math

from channel1d.fluid import Fluid


def hydraulic_diameter(width_m: float, height_m: float) -> float:
    """Dh = 2*w*h/(w+h)."""
    return 2.0 * width_m * height_m / (width_m + height_m)


def fanning_f_re(width_m: float, height_m: float) -> float:
    """Shah-London polynomial for the Fanning f*Re of a rectangular duct."""
    aspect = min(width_m, height_m) / max(width_m, height_m)
    return 24.0 * (
        1.0
        - 1.3553 * aspect
        + 1.9467 * aspect ** 2
        - 1.7012 * aspect ** 3
        + 0.9564 * aspect ** 4
        - 0.2537 * aspect ** 5
    )


def shah_pressure_drop(f_re: float, mu: float, length_m: float, velocity_m_s: float, dh_m: float) -> float:
    """Delta-p = fRe * mu * L * V / (2 * Dh^2), pascals."""
    return f_re * mu * length_m * velocity_m_s / (2.0 * dh_m ** 2)


def fin_efficiency(h_coef: float, rib_m: float, height_m: float, k_copper: float) -> float:
    """Straight-fin efficiency, tanh(mH)/(mH), with m = sqrt(2h/(k*rib))."""
    em = math.sqrt(2.0 * h_coef / (k_copper * rib_m))
    ml = em * height_m
    if ml < 1e-8:
        return 1.0
    return math.tanh(ml) / ml


def hausen_nusselt(dh_m: float, length_m: float, reynolds: float, prandtl: float) -> float:
    """Nu = max(4, 1.86 * Gz^(1/3)), Gz = Dh/L*Re*Pr."""
    graetz = dh_m / length_m * reynolds * prandtl
    return max(4.0, 1.86 * graetz ** (1.0 / 3.0))


def evaluate(
    fluid: Fluid,
    *,
    n: int,
    width_m: float,
    rib_m: float,
    height_m: float,
    heated_length_m: float,
    column_length_m: float,
    flow_lpm: float,
    power_w: float,
    k_copper: float,
) -> dict[str, float]:
    """Bulk screen for every channel carrying an equal share of flow and heat.

    Center-feed does not change these column totals. Each center-fed leg
    carries half the channel flow and half the channel heat, so the leg
    fluid rise equals ``dTf``.
    """
    mdot = fluid.mass_flow(flow_lpm)
    area = width_m * height_m
    velocity = (mdot / n) / (fluid.rho * area)
    dh = hydraulic_diameter(width_m, height_m)
    reynolds = fluid.rho * velocity * dh / fluid.mu
    prandtl = fluid.prandtl()
    nusselt = hausen_nusselt(dh, heated_length_m, reynolds, prandtl)
    h_coef = nusselt * fluid.k / dh
    eta = fin_efficiency(h_coef, rib_m, height_m, k_copper)
    length_per_m = 2.0 * width_m + 2.0 * height_m * eta
    ua = n * h_coef * length_per_m * heated_length_m
    dtf = power_w / (mdot * fluid.cp)
    dtconv = power_w / ua
    f_re = fanning_f_re(width_m, height_m)
    dp = shah_pressure_drop(f_re, fluid.mu, column_length_m, velocity, dh)
    leg_velocity = 0.5 * velocity
    leg_flow = 0.5 * (mdot / n)
    leg_power = 0.5 * (power_w / n)
    dtf_leg = leg_power / (leg_flow * fluid.cp)
    return {
        "V": velocity,
        "V_leg": leg_velocity,
        "Re": reynolds,
        "Dh_m": dh,
        "Dh_mm": dh * 1e3,
        "Pr": prandtl,
        "Nu": nusselt,
        "h": h_coef,
        "eta": eta,
        "dTf": dtf,
        "dTf_leg": dtf_leg,
        "dTconv": dtconv,
        "dTwall": dtconv + dtf,
        "dP_Pa": dp,
        "fRe": f_re,
        "mdot": mdot,
    }
