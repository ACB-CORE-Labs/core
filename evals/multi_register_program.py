"""evals.multi_register_program — Tier-2a multi-entity arithmetic (ADR-0250).

Multi-entity arithmetic as a **product of independent conformal lines**: each
entity is its own register (its own null point / its own relaxation). Per-register
ops (add/subtract/multiply/divide by a constant) reuse the Tier-1 transport; a
transfer is a **coupled pair of translators** — `T₋ₖ` on the actor, `T₊ₖ` on the
target — acting on disjoint registers, so exactness across the independent null
points is inherited from Tier-1 (ADR-0249 P1).

**Transactional atomicity.** Registers are an immutable snapshot. A transfer
runs prepare → validate → commit: both candidate states are relaxed into locals,
then validated (both converged AND the conservation pin), then — only on full
success — a *new* register mapping is produced. A failure anywhere means the new
mapping is never built, so the original stands untouched: no partial-mutation
window, no rollback. Any abort raises a typed `MultiRegisterError` and aborts the
whole program (fail-closed — a partial answer is never emitted, preserving
wrong=0).

**Conservation pin (hard-reject, relative).** A transfer must satisfy
`Σ decode(after) ≡ Σ decode(before)` within a *relative* tolerance
(`|Δ| ≤ rtol·max(1,|before|)`) — decoded-quantity error scales with magnitude, so
an absolute tolerance is wrong for large chains; a genuine non-conserving transfer
is off by a whole `k` and is still caught. Failure is an algebraic failure, not a
scope miss: fail closed.

Tier-2a scope: single-accumulator-per-entity affine + constant-operand transfers,
positive scale, matching units on add/subtract. A total-like unknown
(`unknown.entity is None`) is refused here — it needs the certified summation turn
(2b). Derived operands (rate/comparison/fraction/partition) are refused. Records
are content-addressed and GENESIS-linked (the Ring-2 chain-integrity pattern),
carrying the entity + certificate id + step, never a decoded value. Off-serving
(A-04); never imported by `chat/runtime.py`.
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
from generate.math_problem_graph import MathProblemGraph, Quantity

__all__ = [
    "MultiRegisterError",
    "RegisterTurn",
    "MultiRegisterProgram",
    "MultiRegisterRecord",
    "MultiRegisterOutcome",
    "compile_multi_register_program",
    "execute_multi_register_program",
    "verify_multi_register_chain",
]

_AFFINE = frozenset({"add", "subtract", "multiply", "divide"})
_CONSERVATION_RTOL = 1e-6


class MultiRegisterError(ValueError):
    """Typed, fail-closed refusal for multi-register compilation/execution."""

    def __init__(self, reason: str, **disclosure: object) -> None:
        self.reason = reason
        self.disclosure = disclosure
        detail = ", ".join(f"{k}={v!r}" for k, v in disclosure.items())
        super().__init__(f"{reason}({detail})" if detail else reason)


def _digest(payload: dict) -> str:
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class RegisterTurn:
    """One program step: a per-register affine op or a coupled transfer."""

    kind: str
    actor: str
    scale: float
    offset: float
    operand: float
    target: str | None = None


@dataclass(frozen=True, slots=True)
class MultiRegisterProgram:
    seeds: tuple[tuple[str, float], ...]  # (entity, seed) in graph order
    turns: tuple[RegisterTurn, ...]
    answer_entity: str
    answer_unit: str


@dataclass(frozen=True, slots=True)
class MultiRegisterRecord:
    """Content-addressed, GENESIS-linked record of one certified register turn."""

    sequence_index: int
    entity: str
    certificate_id: str
    converged: bool
    step: tuple[str, float, float]  # (kind, scale, offset)
    prev_record_digest: str

    def _payload(self) -> dict:
        return {
            "sequence_index": int(self.sequence_index),
            "entity": self.entity,
            "certificate_id": self.certificate_id,
            "converged": bool(self.converged),
            "step": [self.step[0], repr(float(self.step[1])), repr(float(self.step[2]))],
            "prev_record_digest": self.prev_record_digest,
        }

    def record_digest(self) -> str:
        return _digest(self._payload())


@dataclass(frozen=True, slots=True)
class MultiRegisterOutcome:
    answer: float
    answer_unit: str
    records: tuple[MultiRegisterRecord, ...]
    certified: bool


def _quantity(op) -> Quantity:
    if not isinstance(op.operand, Quantity):
        raise MultiRegisterError(
            "operand_not_constant_quantity", kind=op.kind, operand_type=type(op.operand).__name__
        )
    return op.operand


def compile_multi_register_program(graph: MathProblemGraph) -> MultiRegisterProgram:
    """Compile a multi-entity affine `MathProblemGraph` into a register program.

    Fail-closed outside Tier-2a: total-like unknown (needs the summation turn),
    derived operands, non-affine/non-transfer kinds, non-positive scale, unit
    mismatch, unknown transfer endpoints.
    """
    if not graph.initial_state:
        raise MultiRegisterError("no_initial_state")
    seeds: list[tuple[str, float]] = []
    units: dict[str, str] = {}
    for possession in graph.initial_state:
        entity = possession.entity
        if entity in units:
            raise MultiRegisterError("duplicate_initial_entity", entity=entity)
        units[entity] = possession.quantity.unit
        seeds.append((entity, float(possession.quantity.value)))

    answer_entity = graph.unknown.entity
    if answer_entity is None:
        raise MultiRegisterError("total_unknown_requires_summation")
    if answer_entity not in units:
        raise MultiRegisterError("unknown_entity_not_a_register", entity=answer_entity)

    turns: list[RegisterTurn] = []
    for op in graph.operations:
        if op.actor not in units:
            raise MultiRegisterError("actor_not_a_register", actor=op.actor)
        if op.kind == "transfer":
            if op.target not in units:
                raise MultiRegisterError("transfer_target_not_a_register", target=op.target)
            operand = _quantity(op)
            value = float(operand.value)
            if not math.isfinite(value):
                raise MultiRegisterError("operand_not_finite", kind="transfer")
            turns.append(
                RegisterTurn("transfer", op.actor, 1.0, -value, value, target=op.target)
            )
            continue
        if op.kind not in _AFFINE:
            raise MultiRegisterError("operation_kind_out_of_scope", kind=op.kind)
        if op.target is not None:
            raise MultiRegisterError("affine_op_has_target", kind=op.kind, target=op.target)
        operand = _quantity(op)
        value = float(operand.value)
        if not math.isfinite(value):
            raise MultiRegisterError("operand_not_finite", kind=op.kind)
        if op.kind in ("add", "subtract"):
            if operand.unit != units[op.actor]:
                raise MultiRegisterError(
                    "unit_mismatch", entity=op.actor, expected=units[op.actor], got=operand.unit
                )
            offset = value if op.kind == "add" else -value
            turns.append(RegisterTurn(op.kind, op.actor, 1.0, offset, value))
        elif op.kind == "multiply":
            if value <= 0.0:
                raise MultiRegisterError("non_positive_scale", kind="multiply", value=value)
            turns.append(RegisterTurn("multiply", op.actor, value, 0.0, value))
        else:  # divide
            if value <= 0.0:
                raise MultiRegisterError("non_positive_scale", kind="divide", value=value)
            turns.append(RegisterTurn("divide", op.actor, 1.0 / value, 0.0, value))

    return MultiRegisterProgram(
        seeds=tuple(seeds),
        turns=tuple(turns),
        answer_entity=answer_entity,
        answer_unit=graph.unknown.unit,
    )


def _unit(vector: np.ndarray) -> np.ndarray:
    return (vector / np.linalg.norm(vector)).astype(np.float64)


def _relax_to(state: np.ndarray, target: np.ndarray):
    result = relax_to_ground(state, compile_quadratic_well(_unit(target)), require_converged=False)
    return result.psi_steady, result.certificate


def execute_multi_register_program(program: MultiRegisterProgram) -> MultiRegisterOutcome:
    """Thread an immutable register mapping through the turns; decode once.

    Fail-closed: a non-converged relaxation or a conservation violation raises
    and aborts the whole program — no partial-mutation, no partial answer.
    """
    registers = {entity: _unit(embed_quantity(seed)) for entity, seed in program.seeds}
    records: list[MultiRegisterRecord] = []
    prev = GENESIS_DIGEST
    index = 0

    for turn in program.turns:
        if turn.kind == "transfer":
            target_entity = turn.target
            if target_entity is None:  # invariant: compile sets a target for transfers
                raise MultiRegisterError("transfer_missing_target", actor=turn.actor)
            # PREPARE — candidate states into locals; registers untouched.
            actor_target = translate_quantity(registers[turn.actor], -turn.operand)
            target_target = translate_quantity(registers[target_entity], +turn.operand)
            actor_new, actor_cert = _relax_to(registers[turn.actor], actor_target)
            target_new, target_cert = _relax_to(registers[target_entity], target_target)
            # VALIDATE — both certified, then conservation (relative, hard-reject).
            if not (actor_cert.converged and target_cert.converged):
                raise MultiRegisterError(
                    "transfer_nonconverged", actor=turn.actor, target=target_entity
                )
            before = decode_quantity(registers[turn.actor]) + decode_quantity(registers[target_entity])
            after = decode_quantity(actor_new) + decode_quantity(target_new)
            if abs(after - before) > _CONSERVATION_RTOL * max(1.0, abs(before)):
                raise MultiRegisterError(
                    "conservation_violation", before=before, after=after
                )
            # COMMIT — new mapping + two coupled records, atomically.
            registers = {**registers, turn.actor: actor_new, target_entity: target_new}
            for entity, cert, signed in (
                (turn.actor, actor_cert, -turn.operand),
                (target_entity, target_cert, +turn.operand),
            ):
                record = MultiRegisterRecord(
                    index, entity, cert.certificate_id, cert.converged, ("transfer", 1.0, signed), prev
                )
                prev = record.record_digest()
                records.append(record)
                index += 1
        else:
            target = _unit(
                translate_quantity(
                    dilate_quantity(registers[turn.actor], -math.log(turn.scale)), turn.offset
                )
            )
            new_state, cert = _relax_to(registers[turn.actor], target)
            if not cert.converged:
                raise MultiRegisterError("turn_nonconverged", entity=turn.actor, kind=turn.kind)
            registers = {**registers, turn.actor: new_state}
            record = MultiRegisterRecord(
                index, turn.actor, cert.certificate_id, cert.converged,
                (turn.kind, turn.scale, turn.offset), prev,
            )
            prev = record.record_digest()
            records.append(record)
            index += 1

    answer = decode_quantity(registers[program.answer_entity])
    chain = tuple(records)
    return MultiRegisterOutcome(
        answer=answer,
        answer_unit=program.answer_unit,
        records=chain,
        certified=verify_multi_register_chain(chain),
    )


def verify_multi_register_chain(
    records: "list[MultiRegisterRecord] | tuple[MultiRegisterRecord, ...]",
) -> bool:
    """Contiguous indices from 0 and every ``prev_record_digest`` = predecessor's
    recomputed digest (genesis for the first). Mirrors ``verify_turn_chain``."""
    for i, record in enumerate(records):
        if record.sequence_index != i:
            return False
        expected_prev = GENESIS_DIGEST if i == 0 else records[i - 1].record_digest()
        if record.prev_record_digest != expected_prev:
            return False
    return True
