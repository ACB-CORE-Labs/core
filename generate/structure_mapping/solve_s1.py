"""Back-compat re-exports for Increment 1 import paths.

Implementation lives in ``generate.structure_mapping.solve`` (generalized
S1–S4 corridor). This module preserves the Increment 1 public names.
"""

from __future__ import annotations

from generate.structure_mapping.solve import (
    S1SolveOutcome,
    SolveOutcome,
    graph_from_s1_binding,
    solve_s1_binding,
    try_s1_structure_map_and_solve,
)

__all__ = [
    "S1SolveOutcome",
    "SolveOutcome",
    "graph_from_s1_binding",
    "solve_s1_binding",
    "try_s1_structure_map_and_solve",
]
