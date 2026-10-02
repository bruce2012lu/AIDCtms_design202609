# -*- coding: utf-8 -*-
"""Flow direction of each channel in one column.

``plus`` flows from low Y to high Y.
``minus`` flows from high Y to low Y.
``center`` is fed at mid-length and leaves at both ends.

Cross-flow puts even indexes on ``minus`` and odd indexes on ``plus``.
For seven channels that is four streams from high Y and three from low Y.
Center-feed keeps that side pattern and marks the middle three channels
(two when the count is even) as ``center``.
"""
from __future__ import annotations


def scheme_kinds(n: int, scheme: str) -> list[str]:
    """Return one kind per channel, ordered from the low-X side."""
    if n < 1:
        raise ValueError("n must be positive")
    if scheme == "coflow":
        return ["plus"] * n
    if scheme == "cross":
        return ["minus" if i % 2 == 0 else "plus" for i in range(n)]
    if scheme == "center":
        n_mid = 3 if n % 2 else 2
        if n < n_mid + 2:
            n_mid = max(1, n - 2)
        i0 = (n - n_mid) // 2
        kinds: list[str] = []
        for i in range(n):
            if i0 <= i < i0 + n_mid:
                kinds.append("center")
            else:
                kinds.append("minus" if i % 2 == 0 else "plus")
        return kinds
    raise ValueError(f"unknown scheme: {scheme}")
