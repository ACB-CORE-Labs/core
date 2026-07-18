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
from generate.math_problem_graph import Comparison, MathProblemGraph, Quantity

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
_COMPARE_MULT = "compare_multiply"  # internal turn kind for actor := factor × reference


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


# Pseudo-entity for certified-summation accumulator records.
_TOTAL = "__total__"


def _state_digest(psi: np.ndarray) -> str:
    """Byte digest of a state (explicit ``<f8`` LE) — the same convention as
    ``RelaxationCertificate.psi_digest``, so a summation operand binds to the
    exact certified state it was decoded from."""
    return hashlib.sha256(
        np.ascontiguousarray(np.asarray(psi, dtype=np.dtype("<f8"))).tobytes()
    ).hexdigest()


@dataclass(frozen=True, slots=True)
class RegisterTurn:
    """One program step: a per-register affine op, a coupled transfer, or a
    cross-register comparison (``actor := factor × reference``)."""

    kind: str
    actor: str
    scale: float
    offset: float
    operand: float
    target: str | None = None
    reference: str | None = None  # compare_multiply: the source register read from


@dataclass(frozen=True, slots=True)
class MultiRegisterProgram:
    seeds: tuple[tuple[str, float], ...]  # (entity, seed) in graph order
    turns: tuple[RegisterTurn, ...]
    answer_entity: str | None  # None ⇒ certified summation over all registers
    answer_unit: str
    # Deterministic register order for summation: seed order, then compare-defined order.
    register_order: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class MultiRegisterRecord:
    """Content-addressed, GENESIS-linked record of one certified register turn."""

    sequence_index: int
    entity: str
    certificate_id: str
    converged: bool
    step: tuple[str, float, float]  # (kind, scale, offset)
    prev_record_digest: str
    operand_source_digest: str = ""  # summation/compare: binds the operand to its source state
    source_entity: str = ""  # compare only: the reference register the dilation read from

    def _payload(self) -> dict:
        payload = {
            "sequence_index": int(self.sequence_index),
            "entity": self.entity,
            "certificate_id": self.certificate_id,
            "converged": bool(self.converged),
            "step": [self.step[0], repr(float(self.step[1])), repr(float(self.step[2]))],
            "prev_record_digest": self.prev_record_digest,
        }
        # Each field is present only when set, so affine/transfer/summation record
        # digests are byte-identical to before compare landed.
        if self.operand_source_digest:
            payload["operand_source_digest"] = self.operand_source_digest
        if self.source_entity:
            payload["source_entity"] = self.source_entity
        return payload

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
    order: list[str] = []  # deterministic register order: seeds first, defined later
    for possession in graph.initial_state:
        entity = possession.entity
        if entity in units:
            raise MultiRegisterError("duplicate_initial_entity", entity=entity)
        units[entity] = possession.quantity.unit
        order.append(entity)
        seeds.append((entity, float(possession.quantity.value)))

    turns: list[RegisterTurn] = []
    for op in graph.operations:
        if op.kind == "compare_multiplicative":
            # actor := factor × reference — a cross-register definition (AMENDMENT 1/2).
            comparison = op.operand
            if not isinstance(comparison, Comparison):
                raise MultiRegisterError("compare_operand_not_comparison", kind=op.kind)
            if comparison.direction not in ("times", "fraction"):
                raise MultiRegisterError("compare_additive_out_of_scope", direction=comparison.direction)
            reference = comparison.reference_actor
            if reference not in units:
                raise MultiRegisterError("compare_reference_not_a_register", reference=reference)
            if comparison.factor is None:  # invariant: times/fraction carry a factor
                raise MultiRegisterError("compare_missing_factor", direction=comparison.direction)
            factor = float(comparison.factor)
            if not math.isfinite(factor) or factor <= 0.0:
                raise MultiRegisterError("compare_factor_not_positive", factor=factor)
            if op.actor == reference:
                raise MultiRegisterError("compare_self_reference", actor=op.actor)
            if op.actor not in units:  # the comparison DEFINES the actor register
                units[op.actor] = units[reference]  # unit propagation from the reference
                order.append(op.actor)
            turns.append(
                RegisterTurn(_COMPARE_MULT, op.actor, factor, 0.0, factor, reference=reference)
            )
            continue
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

    # Validate the answer target AFTER ops, so compare-defined entities count
    # (a concrete unknown may be a compare-defined register). None ⇒ summation.
    answer_entity = graph.unknown.entity
    if answer_entity is not None and answer_entity not in units:
        raise MultiRegisterError("unknown_entity_not_a_register", entity=answer_entity)

    return MultiRegisterProgram(
        seeds=tuple(seeds),
        turns=tuple(turns),
        answer_entity=answer_entity,
        answer_unit=graph.unknown.unit,
        register_order=tuple(order),
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
        elif turn.kind == _COMPARE_MULT:
            # actor := factor × reference. Read the reference register's STATE,
            # dilate, write the actor (a definition, not a transfer — no
            # conservation pin). The record binds the reference entity + its state
            # digest so re-verification reconstructs the source from records alone.
            reference = turn.reference
            if reference is None:  # invariant: compile sets a reference for compare
                raise MultiRegisterError("compare_missing_reference", actor=turn.actor)
            reference_state = registers[reference]
            target = _unit(dilate_quantity(reference_state, -math.log(turn.scale)))
            new_state, cert = _relax_to(reference_state, target)
            if not cert.converged:
                raise MultiRegisterError("compare_nonconverged", actor=turn.actor, reference=reference)
            registers = {**registers, turn.actor: new_state}
            record = MultiRegisterRecord(
                index, turn.actor, cert.certificate_id, cert.converged,
                (_COMPARE_MULT, turn.scale, 0.0), prev,
                operand_source_digest=_state_digest(reference_state),
                source_entity=reference,
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

    if program.answer_entity is None:
        # Certified summation over all registers (ruling #1: summation stays in
        # the substrate). Each addition is a certified turn; the operand is the
        # decode of a certified register state, bound by ``operand_source_digest``
        # (= that state's psi_digest) — deterministic re-execution reproduces it,
        # so the Python layer cannot tamper with the intermediate value.
        # Registers-driven (AMENDMENT 1): sum ALL registers — seeds AND
        # compare-defined — in the pinned deterministic order, so a defined
        # register is never silently dropped from a total.
        order = list(program.register_order)
        accumulator = registers[order[0]]
        for entity in order[1:]:
            source_state = registers[entity]
            operand = decode_quantity(source_state)
            target = _unit(translate_quantity(accumulator, operand))
            accumulator, cert = _relax_to(accumulator, target)
            if not cert.converged:
                raise MultiRegisterError("summation_nonconverged", entity=entity)
            record = MultiRegisterRecord(
                index, _TOTAL, cert.certificate_id, cert.converged,
                ("sum_add", 1.0, operand), prev,
                operand_source_digest=_state_digest(source_state),
            )
            prev = record.record_digest()
            records.append(record)
            index += 1
        answer = decode_quantity(accumulator)
    else:
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
