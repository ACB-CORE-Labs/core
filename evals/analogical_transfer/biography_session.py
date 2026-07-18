"""ADR-0243 §2.5 — harness-driven biography session (seam S2's first real caller).

Runs the ADR-0240 analogical-transfer harness and, on report-level PASS,
integrates the session's lived trajectory into the Biography Holonomy Blade
via the PASS-gated wiring (:func:`integrate_validated_biography`; direct
integration per the 2026-07-17 ruling — the blade is derived state, a pure
recompute, never persisted).

The lived trajectory is the sequence of transfer versors the session actually
underwent: the report carries scalar evidence only (by design), so the
versors are RECOMPUTED here from the validated cases' point clouds via
:func:`conformal_procrustes` — reconstruction-over-storage, deterministic,
bound to the report by the provenance record's content hashes.

Eval-tier (A-04): lives under ``evals/``; never imported by serving. Failure
at any stage is the wiring's typed :class:`BiographyIntegrationError` — a
session with wrongs, or with nothing validated, integrates nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from core.physics.biography import BiographyHolonomyBlade
from core.physics.biography_wiring import (
    BiographyProvenanceRecord,
    integrate_validated_biography,
)
from core.physics.dynamic_manifold import conformal_procrustes
from core.physics.goldtether import GoldTetherMonitor
from evals.analogical_transfer.harness import (
    AnalogicalTransferReport,
    TransferCase,
    run_analogical_transfer,
)

__all__ = [
    "BiographySessionArtifact",
    "run_biography_session",
    "session_trajectory",
]


@dataclass(frozen=True, slots=True)
class BiographySessionArtifact:
    """One validated session: report, integrated blade, provenance, lineage."""

    report: AnalogicalTransferReport
    blade: BiographyHolonomyBlade
    record: BiographyProvenanceRecord
    trajectory_case_ids: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "record": self.record.as_dict(),
            "trajectory_case_ids": list(self.trajectory_case_ids),
            "blade_n_steps": int(self.blade.n_steps),
            "blade_closure": float(self.blade.closure),
            "trajectory_hash": self.blade.trajectory_hash,
        }


def session_trajectory(
    cases: Sequence[TransferCase], report: AnalogicalTransferReport
) -> tuple[tuple, tuple[str, ...]]:
    """Recompute the lived trajectory: one recovered versor per CORRECT case.

    Report order is preserved (order is load-bearing for holonomy). Refused and
    wrong cases contribute nothing — wrong=0 gating happens in the wiring.
    """
    by_id = {c.case_id: c for c in cases}
    versors = []
    case_ids: list[str] = []
    for result in report.results:
        if not result.correct:
            continue
        case = by_id[result.case_id]
        versor, _residual = conformal_procrustes(case.source, case.target)
        versors.append(versor)
        case_ids.append(result.case_id)
    return tuple(versors), tuple(case_ids)


def run_biography_session(
    cases: Sequence[TransferCase],
    *,
    residual_threshold: float = 0.35,
    alpha: float = 0.5,
    goldtether: GoldTetherMonitor | None = None,
) -> BiographySessionArtifact:
    """Validate → recompute lived trajectory → integrate (PASS-gated, typed refusals)."""
    report = run_analogical_transfer(
        cases, residual_threshold=residual_threshold, goldtether=goldtether
    )
    trajectory, case_ids = session_trajectory(cases, report)
    blade, record = integrate_validated_biography(report, trajectory, alpha=alpha)
    return BiographySessionArtifact(
        report=report, blade=blade, record=record, trajectory_case_ids=case_ids
    )
