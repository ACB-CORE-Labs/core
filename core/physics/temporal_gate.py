"""core.physics.temporal_gate — Temporal Admissibility Gate (ADR-0240).

Wisdom as geometry: refuse premature but eventually-admissible claims with a
typed NOT_YET. Never confabulates early. Pure predicate — no side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping


class TemporalVerdict(str, Enum):
    ADMIT = "admit"
    NOT_YET = "not_yet"
    REFUSE = "refuse"


@dataclass(frozen=True, slots=True)
class TemporalContext:
    """Geometric/temporal preconditions for a claim.

    All fields are explicit; missing evidence is not inventable.
    """

    step: int
    min_step: int = 0
    required_evidence_count: int = 0
    evidence_count: int = 0
    coherence_residual: float = 0.0
    residual_ceiling: float = 1.0
    prerequisites_met: bool = True
    claim_id: str = ""


@dataclass(frozen=True, slots=True)
class TemporalDecision:
    verdict: TemporalVerdict
    reason: str
    claim_id: str
    disclosure: Mapping[str, Any]


class TemporalAdmissibilityGate:
    """Pure temporal admissibility checks."""

    def __init__(
        self,
        *,
        require_prerequisites: bool = True,
        enforce_residual_ceiling: bool = True,
    ) -> None:
        self.require_prerequisites = bool(require_prerequisites)
        self.enforce_residual_ceiling = bool(enforce_residual_ceiling)

    def evaluate(self, ctx: TemporalContext) -> TemporalDecision:
        cid = str(ctx.claim_id)

        if ctx.step < 0 or ctx.min_step < 0:
            return TemporalDecision(
                verdict=TemporalVerdict.REFUSE,
                reason="negative_time_index",
                claim_id=cid,
                disclosure={
                    "type": "temporal_refuse",
                    "detail": "time indices must be non-negative",
                },
            )

        if self.require_prerequisites and not ctx.prerequisites_met:
            return TemporalDecision(
                verdict=TemporalVerdict.REFUSE,
                reason="prerequisites_unmet",
                claim_id=cid,
                disclosure={
                    "type": "temporal_refuse",
                    "detail": "required prerequisites are not met",
                },
            )

        if self.enforce_residual_ceiling and ctx.coherence_residual > ctx.residual_ceiling:
            return TemporalDecision(
                verdict=TemporalVerdict.REFUSE,
                reason="residual_above_ceiling",
                claim_id=cid,
                disclosure={
                    "type": "temporal_refuse",
                    "detail": "coherence residual exceeds ceiling",
                    "residual": float(ctx.coherence_residual),
                    "ceiling": float(ctx.residual_ceiling),
                },
            )

        if ctx.step < ctx.min_step:
            return TemporalDecision(
                verdict=TemporalVerdict.NOT_YET,
                reason="before_min_step",
                claim_id=cid,
                disclosure={
                    "type": "temporal_not_yet",
                    "detail": "fullness of time not reached",
                    "step": int(ctx.step),
                    "min_step": int(ctx.min_step),
                },
            )

        if ctx.evidence_count < ctx.required_evidence_count:
            return TemporalDecision(
                verdict=TemporalVerdict.NOT_YET,
                reason="insufficient_evidence",
                claim_id=cid,
                disclosure={
                    "type": "temporal_not_yet",
                    "detail": "evidence count below required floor",
                    "evidence_count": int(ctx.evidence_count),
                    "required_evidence_count": int(ctx.required_evidence_count),
                },
            )

        return TemporalDecision(
            verdict=TemporalVerdict.ADMIT,
            reason="temporally_admissible",
            claim_id=cid,
            disclosure={
                "type": "temporal_admit",
                "step": int(ctx.step),
                "evidence_count": int(ctx.evidence_count),
            },
        )
