"""Deterministic tune / measure split of the official holdout_dev/v1 (ADR-0250 reader arc).

Pinned **before any grammar work** (compare increment plan §5, AMENDMENT 3): the reader grammar
family is developed against the **tune** split only; every increment's coverage delta is measured on
the disjoint **measure** split only. The assignment is a pure function of the case id, so it is
reproducible and cannot drift — disjointness is enforced by construction, not by discipline.

Rule (fixed 2026-07-18, never re-seeded): a case is ``measure`` iff ``sha256(id)`` is even, else
``tune`` (≈ 50 / 50). `wrong=0` is verified across the **full 500** regardless of split; only the
*coverage delta* is attributed to the measure split.
"""
from __future__ import annotations

import hashlib

__all__ = ["split_of", "TUNE", "MEASURE"]

TUNE = "tune"
MEASURE = "measure"


def split_of(case_id: str) -> str:
    """Return ``"tune"`` or ``"measure"`` for ``case_id`` — deterministic, id-only."""
    digest = int(hashlib.sha256(case_id.encode("utf-8")).hexdigest(), 16)
    return MEASURE if digest % 2 == 0 else TUNE
