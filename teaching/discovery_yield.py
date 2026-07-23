"""discovery-yield-per-served-turn telemetry (2026-07-23 directive).

Scoped exactly as ruled: "candidates proposed per served turn on clean,
post-reset traffic." CORE has no always-on PROCESS ([[project-core-is-one-
continuous-life]]), so "per served turn" can only mean per user-invoked
turn — there is no live/background rate to measure yet. This module
computes that number; it does not invent a clock-time one.

Reads two engine_state manifest fields:
  - ``turn_count`` — the live, monotonic served-turn counter
    (``chat.runtime.ChatRuntime._turn_count``).
  - ``turn_count_baseline`` — the ``turn_count`` value stamped at the last
    clean reset of the discovery-candidate ledger (see
    ``scripts/ops/reset_candidate_corpus_t11_20260722.py`` and its
    2026-07-23 baseline-stamp follow-up). Additive-optional on the
    manifest; a manifest that never had a baseline stamped has none.

Determinism contract: ``compute_discovery_yield`` is a pure function of
the store's committed state. No clock reads, no LLM, no stochastic
sampling. Fail-closed: a missing baseline returns ``None`` rather than
fabricating a denominator against an un-marked epoch (Absolute
Provenance — we do not confabulate telemetry).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from engine_state import EngineStateStore


@dataclass(frozen=True, slots=True)
class DiscoveryYield:
    """A single, deterministic snapshot of post-reset discovery yield."""

    turn_count: int
    turn_count_baseline: int
    served_turns_since_reset: int
    candidates_since_reset: int
    yield_rate: float | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "turn_count": self.turn_count,
            "turn_count_baseline": self.turn_count_baseline,
            "served_turns_since_reset": self.served_turns_since_reset,
            "candidates_since_reset": self.candidates_since_reset,
            "yield_rate": self.yield_rate,
        }


def compute_discovery_yield(store: EngineStateStore) -> DiscoveryYield | None:
    """Compute candidates-proposed-per-served-turn since the last reset.

    Returns ``None`` when no committed checkpoint exists yet, or when the
    committed manifest has no ``turn_count_baseline`` stamped — both are
    "no clean epoch to measure against", not "zero yield".
    """
    manifest = store.load_manifest()
    if manifest is None:
        return None
    baseline = manifest.get("turn_count_baseline")
    if baseline is None:
        return None

    turn_count = int(manifest["turn_count"])
    turn_count_baseline = int(baseline)
    served_turns_since_reset = turn_count - turn_count_baseline
    candidates_since_reset = len(store.load_discovery_candidates())
    yield_rate = (
        candidates_since_reset / served_turns_since_reset
        if served_turns_since_reset > 0
        else None
    )
    return DiscoveryYield(
        turn_count=turn_count,
        turn_count_baseline=turn_count_baseline,
        served_turns_since_reset=served_turns_since_reset,
        candidates_since_reset=candidates_since_reset,
        yield_rate=yield_rate,
    )
