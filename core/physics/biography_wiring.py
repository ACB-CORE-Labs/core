"""core.physics.biography_wiring — ADR-0240 PASS → biography integration (ADR-0243 §2.5).

First live caller of :func:`core.physics.biography.integrate_biography`.
Gates on a validation report's report-level PASS signal (``report.wrong == 0``
— the harness has no literal PASS type; ``wrong == 0`` is its acceptance
criterion) and re-asserts the I-01 closure invariant at this call site,
failing closed with a typed error.

Ruling (Shay, 2026-07-17, Lane C open question): this wiring is a *direct*
integration, not a proposal-gated mutation — ``integrate_biography`` is a pure
recompute (reconstruction-over-storage; the blade is derived state, never
persisted), so D-5/I-03 proposal-only discipline does not attach here. The
ruling is structurally pinned: this module must import no vault store and no
``evals`` package (guarded by tests/test_adr_0243_biography_wiring.py). Any
future durable blade storage or trajectory auto-sealing breaks that pin and
reopens the mutation-vs-proposal question.

Report-level granularity is deliberate: ADR-0243 §2.5 integrates a validated
*sequence*, and wrong=0 doctrine forbids cherry-picking correct transfers out
of a session that also produced wrongs. Refusals do not block (the harness's
own ``all_correct_or_refused`` semantics), but a session with zero correct
transfers has validated nothing and is refused — no confabulated wisdom.

The report carries no versors (scalar evidence only) and the harness is
consumed as-is, so the caller supplies the lived trajectory alongside the
report; the provenance record binds the two by content hash.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Protocol, Sequence

import numpy as np

from algebra.backend import versor_condition
from core.physics.biography import BiographyHolonomyBlade, integrate_biography
from core.physics.chiral_gate import ChiralOrientationError, ChiralOrientationGate

_CLOSURE = 1e-6
_PROVENANCE_SCHEMA = "biography_provenance_v2"
_ADR_REFS = ("ADR-0240", "ADR-0241", "ADR-0243")


class BiographyIntegrationError(ValueError):
    """Fail-closed refusal from :func:`integrate_validated_biography`.

    Subclasses ``ValueError`` so a caller that fail-closes on ``ValueError``
    records it as a refusal rather than crashing (same contract as
    :class:`core.physics.surprise.SurpriseResidualError`).
    """

    def __init__(self, reason: str, **disclosure) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"biography integration refused [{reason}]: {self.disclosure}")


class TransferCaseResult(Protocol):
    """Per-case slice of the ADR-0240 report this wiring consumes."""

    case_id: str
    residual: float
    correct: bool
    refused: bool
    reason: str


class ValidationReportLike(Protocol):
    """Structural view of ``evals.analogical_transfer.harness.AnalogicalTransferReport``.

    Typed structurally so core.physics does not import ``evals`` (layering:
    evals composes core, never the reverse). Any validated-experience source
    exposing this shape can drive biography integration.
    """

    results: Sequence[TransferCaseResult]
    counts: Mapping[str, int]
    max_residual: float
    wrong: int


@dataclass(frozen=True, slots=True)
class BiographyProvenanceRecord:
    """Append-only audit record binding a PASS report to a biography integration.

    An evidence record, not a proposal — nothing awaits ratification (the blade
    is derived state; see module docstring ruling). Closure-proof discipline
    modeled on :class:`core.physics.self_authorship.AuthorshipProposal`; the
    append-only audit role mirrors :class:`core.physics.identity.TurnEvent`.
    """

    record_id: str
    schema_version: str
    n_cases: int
    counts: Mapping[str, int]
    wrong: int
    max_residual: float
    case_outcomes: tuple[tuple[str, str], ...]  # (case_id, reason), report order
    trajectory_hash: str
    n_steps: int
    alpha: float
    closure_proof: Mapping[str, float]
    chiral_proof: Mapping[str, Any]
    adr_refs: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "record_id": self.record_id,
            "schema_version": self.schema_version,
            "n_cases": self.n_cases,
            "counts": dict(self.counts),
            "wrong": self.wrong,
            "max_residual": self.max_residual,
            "case_outcomes": [list(pair) for pair in self.case_outcomes],
            "trajectory_hash": self.trajectory_hash,
            "n_steps": self.n_steps,
            "alpha": self.alpha,
            "closure_proof": dict(self.closure_proof),
            "chiral_proof": {
                k: (list(v) if isinstance(v, tuple) else v)
                for k, v in self.chiral_proof.items()
            },
            "adr_refs": list(self.adr_refs),
        }


def _content_id(payload: Mapping[str, Any]) -> str:
    # Full 256-bit digest (64 hex); no ``default=str`` — non-serializable
    # payload elements fail closed with a typed ``TypeError`` (ADR-0244 §2.7).
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def chiral_conservation_precondition(
    trajectory: Sequence[np.ndarray],
) -> tuple[ChiralOrientationGate, tuple[str, ...]]:
    """§S2 composition (ADR-0241 §2.4C): sgn(Q_top) conservation over the trajectory.

    Runs BEFORE versor validation, so the gate is live against raw non-versor
    trajectories carrying material pseudoscalar charge — a mirror-flipped
    sequence refuses here, before any blade is computed.

    Honesty theorem (pinned in tests/test_adr_0243_biography_wiring.py): I₅ is
    central in odd-dimensional Cl(4,1), so every CLOSED versor has
    Q = ⟨ψ I₅ ψ̃⟩₀ = ±⟨I₅⟩₀ = 0 exactly. On admissible trajectories (closed
    versors, enforced downstream by ``integrate_biography``) every observation
    is therefore ``vacuous`` and the latch never arms — the same documented
    inertness contract as chiral_gate's GoldTetherMonitor wiring. The
    provenance record discloses the verdicts rather than implying enforcement.
    """
    gate = ChiralOrientationGate()
    verdicts: list[str] = []
    for i, v in enumerate(trajectory):
        try:
            verdicts.append(gate.observe(np.asarray(v, dtype=np.float64)).verdict)
        except ChiralOrientationError as exc:
            raise BiographyIntegrationError(
                "chiral_orientation_violation", stage=f"trajectory[{i}]", **exc.disclosure
            ) from exc
        except ValueError as exc:
            raise BiographyIntegrationError(
                "trajectory_rejected", detail=str(exc), stage=f"trajectory[{i}]"
            ) from exc
    return gate, tuple(verdicts)


def biography_provenance_record(
    report: ValidationReportLike,
    blade: BiographyHolonomyBlade,
    *,
    alpha: float,
    chiral_proof: Mapping[str, Any],
) -> BiographyProvenanceRecord:
    """Build the append-only provenance record for one validated integration."""
    counts = {k: int(v) for k, v in sorted(report.counts.items())}
    case_outcomes = tuple((r.case_id, r.reason) for r in report.results)
    closure_proof = {
        "blade_closure": float(blade.closure),
        "blade_versor_condition": float(versor_condition(blade.blade)),
        "closure_tol": _CLOSURE,
    }
    chiral_body = {
        k: (list(v) if isinstance(v, tuple) else v) for k, v in sorted(chiral_proof.items())
    }
    body = {
        "schema_version": _PROVENANCE_SCHEMA,
        "n_cases": len(report.results),
        "counts": counts,
        "wrong": int(report.wrong),
        "max_residual": float(report.max_residual),
        "case_outcomes": [list(pair) for pair in case_outcomes],
        "trajectory_hash": blade.trajectory_hash,
        "n_steps": int(blade.n_steps),
        "alpha": float(alpha),
        "closure_proof": closure_proof,
        "chiral_proof": chiral_body,
        "adr_refs": list(_ADR_REFS),
    }
    return BiographyProvenanceRecord(
        record_id=f"bioprov-{_content_id(body)}",
        schema_version=_PROVENANCE_SCHEMA,
        n_cases=len(report.results),
        counts=counts,
        wrong=int(report.wrong),
        max_residual=float(report.max_residual),
        case_outcomes=case_outcomes,
        trajectory_hash=blade.trajectory_hash,
        n_steps=int(blade.n_steps),
        alpha=float(alpha),
        closure_proof=closure_proof,
        chiral_proof=dict(chiral_proof),
        adr_refs=_ADR_REFS,
    )


def integrate_validated_biography(
    report: ValidationReportLike,
    trajectory: Sequence[np.ndarray],
    *,
    alpha: float = 0.5,
) -> tuple[BiographyHolonomyBlade, BiographyProvenanceRecord]:
    """Integrate a lived trajectory into biography, gated on report-level PASS.

    Refuses (typed, fail-closed) unless the report validated at least one
    transfer with zero wrongs. Re-asserts I-01 closure on the returned blade at
    this call site (modeled on tests/test_third_door_cohesion.py I-01) rather
    than trusting the callee's internal checks.
    """
    n_cases = len(report.results)
    if n_cases == 0:
        raise BiographyIntegrationError("empty_report")
    if int(report.wrong) != 0:
        raise BiographyIntegrationError(
            "report_not_pass",
            wrong=int(report.wrong),
            counts={k: int(v) for k, v in sorted(report.counts.items())},
        )
    n_correct = sum(1 for r in report.results if r.correct)
    if n_correct == 0:
        # wrong == 0 with everything refused validates nothing (ADR-0243 §2.5
        # integrates a *validated* sequence) — refuse, no confabulated wisdom.
        raise BiographyIntegrationError(
            "no_validated_transfers",
            n_cases=n_cases,
            refused=sum(1 for r in report.results if r.refused),
        )

    # §S2 strict precondition (ADR-0241 §2.4C): sgn(Q_top) conservation over the
    # raw trajectory, before any blade computation. See
    # chiral_conservation_precondition for the honesty theorem (vacuous on
    # closed versors by I₅ centrality; live against raw non-versor input).
    gate, trajectory_verdicts = chiral_conservation_precondition(trajectory)

    try:
        blade = integrate_biography(trajectory, alpha=alpha)
    except ValueError as exc:
        raise BiographyIntegrationError("trajectory_rejected", detail=str(exc)) from exc

    cond = float(versor_condition(blade.blade))
    if blade.closure >= _CLOSURE or cond >= _CLOSURE:
        raise BiographyIntegrationError(
            "i01_closure_violation",
            closure=float(blade.closure),
            versor_condition=cond,
            closure_tol=_CLOSURE,
        )

    # Post-condition: the integrated blade must hold the same orientation latch.
    try:
        blade_verdict = gate.observe(blade.blade).verdict
    except ChiralOrientationError as exc:
        raise BiographyIntegrationError(
            "chiral_orientation_violation", stage="blade", **exc.disclosure
        ) from exc
    chiral_proof: dict[str, Any] = {
        "latched_sign": int(gate.latched_sign),
        "q_floor": float(gate.q_floor),
        "trajectory_verdicts": trajectory_verdicts,
        "blade_verdict": blade_verdict,
    }

    record = biography_provenance_record(report, blade, alpha=alpha, chiral_proof=chiral_proof)
    return blade, record
