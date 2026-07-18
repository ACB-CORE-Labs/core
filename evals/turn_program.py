"""evals.turn_program — multi-step arithmetic as a certified turn program (ADR-0249 P4).

The composition frontier: a multi-step arithmetic problem is compiled from a
``MathProblemGraph`` into an ordered *turn program* — one affine relation-well
per step — and executed as a chain of certified relaxation turns. The
accumulator flows turn-to-turn as a field STATE and is decoded only once, at the
end (anti-hollow, spike §2/§4.1): the substrate performs every step, and the
composition depth lives in the certified chain, not in matrix size.

Ring-2 relationship (spike §4.6 follow-up, verified in-tree): the residual
protocol (``core.ports.residual_protocol.run_residual_protocol``) is
*zero-bound / non-mutating* — its stage-5 recertification refuses if the witness
moved — so it certifies the admissibility of a *fixed* state, not a state
*transition*. Arithmetic turns mutate. So the per-turn certificate is the
relaxation's own ``RelaxationCertificate``, and the tamper-evident *sequence* is
recorded here with the Ring-2 chain-integrity *pattern* (content-addressed,
``GENESIS_DIGEST``-linked, ``verify_turn_chain`` mirroring ``verify_replay_chain``)
rather than by forcing mutating turns through the zero-bound protocol.

Tier-1 scope (ruling #1): a single-accumulator chain over add / subtract /
multiply / divide with constant ``Quantity`` operands and positive scale.
Everything else (multi-entity, transfer, rate, comparison, fraction, partition,
non-positive scale, unit mismatch) is refused and recorded, never silently
dropped. Off-serving (A-04): bridges the generate-side graph to the corridor;
never imported by chat/runtime.py.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass

import numpy as np

from core.physics.cognitive_lifecycle import compile_quadratic_well, relax_to_ground
from core.physics.quantity_kernel import (
    decode_quantity,
    dilate_quantity,
    embed_quantity,
    translate_quantity,
)
from core.ports.residual_protocol import GENESIS_DIGEST
from generate.math_problem_graph import MathProblemGraph, Operation, Quantity

__all__ = [
    "TurnProgramError",
    "AffineStep",
    "TurnProgram",
    "TurnRecord",
    "TurnProgramOutcome",
    "compile_turn_program",
    "execute_turn_program",
    "verify_turn_chain",
]

_AFFINE_KINDS = frozenset({"add", "subtract", "multiply", "divide"})


class TurnProgramError(ValueError):
    """Typed, fail-closed refusal for turn-program compilation."""

    def __init__(self, reason: str, **disclosure: object) -> None:
        self.reason = reason
        self.disclosure = disclosure
        detail = ", ".join(f"{k}={v!r}" for k, v in disclosure.items())
        super().__init__(f"{reason}({detail})" if detail else reason)


def _digest(payload: dict) -> str:
    """Full SHA-256 over canonical JSON (ADR-0245 §2.3; no ``default=str``)."""
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class AffineStep:
    """One relation `output = scale·input + offset`, with source provenance."""

    scale: float
    offset: float
    kind: str
    operand: float


@dataclass(frozen=True, slots=True)
class TurnProgram:
    """A compiled single-accumulator arithmetic program (no answer inside)."""

    seed: float
    steps: tuple[AffineStep, ...]
    answer_unit: str


@dataclass(frozen=True, slots=True)
class TurnRecord:
    """One content-addressed, GENESIS-linked record of a certified turn.

    Carries the turn's ``RelaxationCertificate`` id and the step provenance —
    never a decoded value. Any tamper changes ``record_digest`` and breaks the
    chain from that point (``verify_turn_chain``).
    """

    sequence_index: int
    certificate_id: str
    converged: bool
    step: tuple[str, float, float]  # (kind, scale, offset)
    prev_record_digest: str

    def _payload(self) -> dict:
        return {
            "sequence_index": int(self.sequence_index),
            "certificate_id": self.certificate_id,
            "converged": bool(self.converged),
            "step": [self.step[0], repr(float(self.step[1])), repr(float(self.step[2]))],
            "prev_record_digest": self.prev_record_digest,
        }

    def record_digest(self) -> str:
        return _digest(self._payload())


@dataclass(frozen=True, slots=True)
class TurnProgramOutcome:
    """Decoded answer + the certified, tamper-evident turn chain."""

    answer: float
    answer_unit: str
    records: tuple[TurnRecord, ...]
    certified: bool


def _quantity_operand(op: Operation) -> Quantity:
    if not isinstance(op.operand, Quantity):
        raise TurnProgramError(
            "operand_not_constant_quantity", kind=op.kind, operand_type=type(op.operand).__name__
        )
    return op.operand


def compile_turn_program(graph: MathProblemGraph) -> TurnProgram:
    """Compile a single-accumulator affine ``MathProblemGraph`` into a turn program.

    Fail-closed on anything outside the Tier-1 envelope; the refused shapes are
    the recorded composition frontier, not silent drops.
    """
    if len(graph.initial_state) != 1:
        raise TurnProgramError(
            "not_single_accumulator", possessions=len(graph.initial_state)
        )
    seed_possession = graph.initial_state[0]
    accumulator = seed_possession.entity
    current_unit = seed_possession.quantity.unit
    seed = float(seed_possession.quantity.value)

    steps: list[AffineStep] = []
    for op in graph.operations:
        if op.actor != accumulator:
            raise TurnProgramError("multi_actor_operation", actor=op.actor)
        if op.target is not None:
            raise TurnProgramError("multi_entity_operation", kind=op.kind, target=op.target)
        if op.kind not in _AFFINE_KINDS:
            raise TurnProgramError("operation_kind_out_of_affine_scope", kind=op.kind)
        operand = _quantity_operand(op)
        value = float(operand.value)
        if not math.isfinite(value):
            raise TurnProgramError("operand_not_finite", kind=op.kind)
        if op.kind == "add":
            if operand.unit != current_unit:
                raise TurnProgramError("unit_mismatch", expected=current_unit, got=operand.unit)
            steps.append(AffineStep(scale=1.0, offset=value, kind="add", operand=value))
        elif op.kind == "subtract":
            if operand.unit != current_unit:
                raise TurnProgramError("unit_mismatch", expected=current_unit, got=operand.unit)
            steps.append(AffineStep(scale=1.0, offset=-value, kind="subtract", operand=value))
        elif op.kind == "multiply":
            if value <= 0.0:
                raise TurnProgramError("non_positive_scale", kind="multiply", value=value)
            steps.append(AffineStep(scale=value, offset=0.0, kind="multiply", operand=value))
        else:  # divide
            if value <= 0.0:
                raise TurnProgramError("non_positive_scale", kind="divide", value=value)
            steps.append(AffineStep(scale=1.0 / value, offset=0.0, kind="divide", operand=value))

    return TurnProgram(seed=seed, steps=tuple(steps), answer_unit=graph.unknown.unit)


def _unit(vector: np.ndarray) -> np.ndarray:
    return (vector / np.linalg.norm(vector)).astype(np.float64)


def execute_turn_program(program: TurnProgram) -> TurnProgramOutcome:
    """Chain the turns: relax step by step, decode only the final state.

    The accumulator state flows without being decoded mid-chain (anti-hollow).
    Each turn contributes its real ``RelaxationCertificate`` to a content-addressed
    chain; ``certified`` holds iff every turn converged and the chain is intact.
    """
    psi = _unit(embed_quantity(program.seed))
    records: list[TurnRecord] = []
    prev = GENESIS_DIGEST
    all_converged = True

    for index, step in enumerate(program.steps):
        # Transport the STATE (not a decoded value) by the step's structure.
        target = _unit(translate_quantity(dilate_quantity(psi, -math.log(step.scale)), step.offset))
        hamiltonian = compile_quadratic_well(target)
        result = relax_to_ground(psi, hamiltonian, require_converged=False)
        psi = result.psi_steady
        certificate = result.certificate
        all_converged = all_converged and bool(certificate.converged)
        record = TurnRecord(
            sequence_index=index,
            certificate_id=certificate.certificate_id,
            converged=bool(certificate.converged),
            step=(step.kind, step.scale, step.offset),
            prev_record_digest=prev,
        )
        prev = record.record_digest()
        records.append(record)

    answer = decode_quantity(psi)
    chain = tuple(records)
    return TurnProgramOutcome(
        answer=answer,
        answer_unit=program.answer_unit,
        records=chain,
        certified=all_converged and verify_turn_chain(chain),
    )


def verify_turn_chain(records: "list[TurnRecord] | tuple[TurnRecord, ...]") -> bool:
    """True iff indices are contiguous from 0 and every ``prev_record_digest``
    equals the recomputed digest of its predecessor (genesis for the first).
    Mirrors ``residual_protocol.verify_replay_chain`` for the turn ledger."""
    for i, record in enumerate(records):
        if record.sequence_index != i:
            return False
        expected_prev = GENESIS_DIGEST if i == 0 else records[i - 1].record_digest()
        if record.prev_record_digest != expected_prev:
            return False
    return True
