"""ADR-0242 V2 fixed-replay multi-scale energy comparison (research evidence).

Does **not** promote Fibonacci (or log/dyadic) into production energy defaults.
Joshua gate required before any production promotion.
"""

from __future__ import annotations

from core.physics.multi_scale_energy import (
    comparative_three_way,
    fixed_replay_compare_artifact,
)

__all__ = [
    "comparative_three_way",
    "fixed_replay_compare_artifact",
    "run_fixed_replay",
]


def run_fixed_replay(
    *,
    e0: float = 1.0,
    ages: tuple[float, ...] = (0.0, 1.0, 3.0, 8.0),
    tau0: float = 1.0,
    levels: int = 8,
) -> dict:
    """Entry point for the fixed-replay comparative eval (deterministic)."""
    return fixed_replay_compare_artifact(
        e0=e0, ages=ages, tau0=tau0, levels=levels
    )
