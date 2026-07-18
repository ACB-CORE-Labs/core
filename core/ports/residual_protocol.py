"""core.ports.residual_protocol — Ring 2 shared control grammar (ADR-0247).

The seven-stage residual protocol the ADR-0246 preflight §9 fixes for Ring 2:

    witness → typed residual decomposition → permitted operator selection
      → bounded operation or abstention → re-certification
      → articulation/action decision → append-only replay record

Design commitments (the engineering pillars, applied):

* **Port-agnostic grammar, port-native geometry.** The protocol never
  interprets a port's measurements — Identity speaks grade-1 frame
  preservation, Precision speaks f32 cast transport, a future Atlas port
  speaks packing residuals. The grammar only sequences the stages and records
  the evidence. There is NO port registry and NO unified scheduler (preflight
  §7 non-goal #2): callers invoke the protocol per port, per subject.
* **Abstain-or-proceed v1.** The only operators permitted are zero-bound
  (``proceed_unmodified`` / ``abstain``). A nonzero-bound operator — anything
  that would *modify* the subject to green a metric — fails closed with a
  typed error until a dedicated ADR ratifies a bounded corrector
  (no-silent-correction doctrine; mirrors ADR-0244/0246 admit-or-abstain).
* **Fail-closed on unaccounted residual.** Energy the port's typed channels
  cannot account for forces abstention; no correction policy ever attaches to
  the unclassified remainder (ADR-0246 §3.6 doctrine, generalized).
* **Re-certification.** After the (zero-bound) operation the witness is
  re-measured; any drift means the port mutated state during a supposedly
  non-mutating pass — a protocol violation, not a policy question — and
  raises rather than recording a corrupted replay.
* **Append-only, content-addressed replay.** Every run appends exactly one
  ``ReplayRecord`` whose full-SHA-256 digest chains to its predecessor
  (ADR-0245 §2.3 semantic rigor: canonical JSON, no ``default=str``, no
  truncation). ``verify_replay_chain`` re-derives the chain from content.

Pure, deterministic, off-serving. No wall-clock, no randomness.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Protocol, Sequence

GENESIS_DIGEST: str = "0" * 64

ACTION_PROCEED: str = "proceed"
ACTION_ABSTAIN: str = "abstain"

OPERATOR_PROCEED_ID: str = "proceed_unmodified"
OPERATOR_ABSTAIN_ID: str = "abstain"


class ResidualProtocolError(ValueError):
    """Typed protocol violation — always fail-closed, never a warning."""


def _canonical(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _digest(payload: Any) -> str:
    return hashlib.sha256(_canonical(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PortWitness:
    """Stage 1 — a port's raw, typed measurement of its subject.

    ``measurements`` is a tuple of ``(name, value)`` pairs, canonicalized to
    lexicographic order at construction so two witnesses of the same physical
    measurement are digest-identical regardless of emission order.
    """

    port_id: str
    schema_version: str
    measurements: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        canonical = tuple(
            sorted((str(k), float(v)) for k, v in self.measurements)
        )
        object.__setattr__(self, "measurements", canonical)
        if not self.port_id:
            raise ResidualProtocolError("witness requires a port_id")

    def as_dict(self) -> dict[str, Any]:
        return {
            "port_id": self.port_id,
            "schema_version": self.schema_version,
            "measurements": [[k, v] for k, v in self.measurements],
        }

    def digest(self) -> str:
        return _digest(self.as_dict())


@dataclass(frozen=True)
class ResidualDecomposition:
    """Stage 2 — the witness re-expressed on the port's typed channels.

    ``unaccounted`` is the residual energy the typed channels cannot explain;
    above ``unaccounted_tol`` the protocol abstains (fail-closed — the
    generalized "no correction policy on the unclassified channel").
    """

    port_id: str
    channels: tuple[tuple[str, float], ...]
    unaccounted: float
    unaccounted_tol: float

    def __post_init__(self) -> None:
        canonical = tuple(sorted((str(k), float(v)) for k, v in self.channels))
        object.__setattr__(self, "channels", canonical)

    @property
    def fail_closed(self) -> bool:
        return float(self.unaccounted) > float(self.unaccounted_tol)

    def as_dict(self) -> dict[str, Any]:
        return {
            "port_id": self.port_id,
            "channels": [[k, v] for k, v in self.channels],
            "unaccounted": float(self.unaccounted),
            "unaccounted_tol": float(self.unaccounted_tol),
        }


@dataclass(frozen=True)
class PermittedOperator:
    """Stage 3 element — an operator a port's policy permits.

    ``bound`` is the maximum magnitude of the operation. v1 accepts ONLY
    ``bound == 0.0`` (non-mutating): any nonzero bound requires a future
    dedicated ADR (bounded-corrector), and the protocol fails closed on it.
    """

    operator_id: str
    bound: float = 0.0

    def as_dict(self) -> dict[str, Any]:
        return {"operator_id": self.operator_id, "bound": float(self.bound)}


_DEFAULT_OPERATORS: tuple[PermittedOperator, ...] = (
    PermittedOperator(operator_id=OPERATOR_PROCEED_ID, bound=0.0),
    PermittedOperator(operator_id=OPERATOR_ABSTAIN_ID, bound=0.0),
)


@dataclass(frozen=True)
class ActionDecision:
    """Stage 6 — the articulation/action decision handed to the caller."""

    action: str  # ACTION_PROCEED | ACTION_ABSTAIN
    reasons: tuple[str, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        return {"action": self.action, "reasons": list(self.reasons)}


class ResidualPort(Protocol):
    """The structural contract a port must satisfy (no registry — duck-typed).

    Ports keep their native geometry: the grammar calls these hooks and never
    interprets the measurements beyond the fail-closed ``unaccounted`` check.
    ``permitted_operators`` is optional; absent, the v1 default
    (proceed_unmodified / abstain) applies.
    """

    port_id: str
    schema_version: str

    def witness(self, subject: Any) -> PortWitness: ...
    def decompose(self, witness: PortWitness) -> ResidualDecomposition: ...
    def admit(
        self, subject: Any, decomposition: ResidualDecomposition
    ) -> tuple[bool, tuple[str, ...]]: ...


@dataclass(frozen=True)
class ReplayRecord:
    """Stage 7 — one append-only, content-addressed record of a protocol run.

    ``record_digest()`` covers every stage payload plus the predecessor's
    digest, so any tamper anywhere breaks the chain from that point forward.
    """

    sequence_index: int
    port_id: str
    schema_version: str
    witness: dict[str, Any]
    decomposition: dict[str, Any]
    operator: dict[str, Any]
    recertified: bool
    action: str
    reasons: tuple[str, ...]
    prev_record_digest: str

    def _payload(self) -> dict[str, Any]:
        return {
            "sequence_index": int(self.sequence_index),
            "port_id": self.port_id,
            "schema_version": self.schema_version,
            "witness": self.witness,
            "decomposition": self.decomposition,
            "operator": self.operator,
            "recertified": bool(self.recertified),
            "action": self.action,
            "reasons": list(self.reasons),
            "prev_record_digest": self.prev_record_digest,
        }

    def record_digest(self) -> str:
        return _digest(self._payload())

    def as_dict(self) -> dict[str, Any]:
        out = self._payload()
        out["record_digest"] = self.record_digest()
        return out


def run_residual_protocol(
    port: ResidualPort,
    subject: Any,
    chain: Sequence[ReplayRecord],
) -> tuple[tuple[ReplayRecord, ...], ActionDecision]:
    """Run the seven-stage grammar for one port over one subject.

    Returns ``(chain + one new record, decision)``. Deterministic; the chain is
    never mutated (a new tuple is returned). Raises
    :class:`ResidualProtocolError` on protocol violations (nonzero-bound
    operator; witness drift across a zero-bound operation; port_id mismatch) —
    violations are never recorded as if they were decisions.
    """
    # Stage 1 — witness
    witness = port.witness(subject)
    if witness.port_id != port.port_id:
        raise ResidualProtocolError(
            f"witness port_id {witness.port_id!r} != port {port.port_id!r}"
        )
    # Stage 2 — typed residual decomposition
    decomposition = port.decompose(witness)
    if decomposition.port_id != port.port_id:
        raise ResidualProtocolError(
            f"decomposition port_id {decomposition.port_id!r} != port {port.port_id!r}"
        )
    # Stage 3 — permitted operator selection (v1: zero-bound only)
    permitted_hook = getattr(port, "permitted_operators", None)
    operators = (
        tuple(permitted_hook(decomposition)) if permitted_hook is not None
        else _DEFAULT_OPERATORS
    )
    for op in operators:
        if float(op.bound) != 0.0:
            raise ResidualProtocolError(
                f"nonzero_bound_operator_not_ratified: {op.operator_id!r} "
                f"(bound={op.bound}) — bounded correctors require a dedicated ADR"
            )
    # Stage 4 — bounded operation OR abstention (v1 operators are non-mutating)
    reasons: list[str] = []
    if decomposition.fail_closed:
        admitted = False
        reasons.append(
            f"unaccounted_residual_exceeds_tol:{decomposition.unaccounted:.6g}"
            f">{decomposition.unaccounted_tol:.6g}"
        )
    else:
        admitted, admit_reasons = port.admit(subject, decomposition)
        reasons.extend(admit_reasons)
    proceed_permitted = any(op.operator_id == OPERATOR_PROCEED_ID for op in operators)
    if admitted and proceed_permitted:
        selected = next(op for op in operators if op.operator_id == OPERATOR_PROCEED_ID)
        action = ACTION_PROCEED
    else:
        selected = next(
            (op for op in operators if op.operator_id == OPERATOR_ABSTAIN_ID),
            PermittedOperator(operator_id=OPERATOR_ABSTAIN_ID, bound=0.0),
        )
        action = ACTION_ABSTAIN
        if admitted and not proceed_permitted:
            reasons.append("proceed_not_in_permitted_operators")
    # Stage 5 — re-certification: a zero-bound operation must not move the witness
    recheck = port.witness(subject)
    if recheck.digest() != witness.digest():
        raise ResidualProtocolError(
            "recertification_witness_changed: port mutated state during a "
            "zero-bound operation — protocol violation, refusing to record"
        )
    # Stage 6 — action decision
    decision = ActionDecision(action=action, reasons=tuple(reasons))
    # Stage 7 — append-only replay record
    prev = chain[-1].record_digest() if chain else GENESIS_DIGEST
    record = ReplayRecord(
        sequence_index=len(chain),
        port_id=port.port_id,
        schema_version=port.schema_version,
        witness=witness.as_dict(),
        decomposition=decomposition.as_dict(),
        operator=selected.as_dict(),
        recertified=True,
        action=action,
        reasons=tuple(reasons),
        prev_record_digest=prev,
    )
    return tuple(chain) + (record,), decision


def verify_replay_chain(records: Sequence[ReplayRecord]) -> bool:
    """True iff the chain is intact: indices contiguous from 0 and every
    ``prev_record_digest`` equals the recomputed digest of its predecessor
    (genesis for the first). Any payload tamper changes a recomputed digest and
    breaks the link that stored the original."""
    for i, record in enumerate(records):
        if record.sequence_index != i:
            return False
        expected_prev = GENESIS_DIGEST if i == 0 else records[i - 1].record_digest()
        if record.prev_record_digest != expected_prev:
            return False
    return True
