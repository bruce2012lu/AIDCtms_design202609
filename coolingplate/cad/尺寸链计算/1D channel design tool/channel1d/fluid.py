# -*- coding: utf-8 -*-
"""Coolant properties for the rectangular-channel screen.

The HBM preset uses liquid water at 40 C. Properties are inputs, not a
property library.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Fluid:
    """Constant-property liquid."""

    rho: float
    cp: float
    mu: float
    k: float

    def prandtl(self) -> float:
        """Pr = mu * cp / k."""
        return self.mu * self.cp / self.k

    def mass_flow(self, flow_lpm: float) -> float:
        """Convert L/min to kg/s with this density."""
        return self.rho * flow_lpm / 60000.0
