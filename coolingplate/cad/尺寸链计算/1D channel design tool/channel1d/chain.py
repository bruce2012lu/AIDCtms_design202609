# -*- coding: utf-8 -*-
"""Column-width identity for a rectangular channel row.

The chain is an identity of independent inputs::

    2 * land + n * width + (n - 1) * rib = column_width

Land is not derived in order to hide a chain that misses the column width.
``land_to_close`` exists only for a sweep: it proposes the land that would
close the chain, and the caller must still reject that land when it sits
below the manufacturing floor.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChainLimits:
    """Manufacturing floors used by the HBM cold-plate rules."""

    min_rib_m: float = 0.30e-3
    min_width_m: float = 0.40e-3
    min_land_m: float = 0.30e-3
    max_aspect: float = 5.0
    velocity_cap_m_s: float = 0.80


def chain_sum(land_m: float, n: int, width_m: float, rib_m: float) -> float:
    """Return 2*land + n*width + (n-1)*rib, in metres."""
    return 2.0 * land_m + n * width_m + (n - 1) * rib_m


def chain_closes(
    land_m: float,
    n: int,
    width_m: float,
    rib_m: float,
    column_width_m: float,
    tol_m: float = 1e-9,
) -> bool:
    """True when the independent inputs sum to the column width."""
    return abs(chain_sum(land_m, n, width_m, rib_m) - column_width_m) <= tol_m


def land_to_close(n: int, width_m: float, rib_m: float, column_width_m: float) -> float:
    """Land that would close the chain. Check it against ``ChainLimits`` before use."""
    return (column_width_m - n * width_m - (n - 1) * rib_m) / 2.0


def aspect_ratio(height_m: float, width_m: float) -> float:
    """Groove depth / groove width."""
    return height_m / width_m


def limit_failures(
    *,
    land_m: float,
    n: int,
    width_m: float,
    rib_m: float,
    height_m: float,
    column_width_m: float,
    velocity_m_s: float | None = None,
    limits: ChainLimits | None = None,
) -> list[str]:
    """Names of floors the candidate misses. Empty means the candidate is allowed."""
    lim = limits or ChainLimits()
    failed: list[str] = []
    if n < 1:
        failed.append("channel_count")
    if not chain_closes(land_m, n, width_m, rib_m, column_width_m):
        failed.append("chain")
    if rib_m < lim.min_rib_m - 1e-12:
        failed.append("rib")
    if width_m < lim.min_width_m - 1e-12:
        failed.append("width")
    if land_m < lim.min_land_m - 1e-12:
        failed.append("land")
    if aspect_ratio(height_m, width_m) > lim.max_aspect + 1e-9:
        failed.append("aspect")
    if velocity_m_s is not None and velocity_m_s > lim.velocity_cap_m_s + 1e-12:
        failed.append("velocity")
    return failed
