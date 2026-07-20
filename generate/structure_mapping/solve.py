"""Solve structure-mapped bindings through the certificate corridor.

Generalizes Increment 1's three-gate ``wrong=0`` pattern:
1. Map-time pure-family exact gate (in mapper)
2. Classical ``solve``+``verify`` AND multi-register certificate agreement
3. Original-graph answer agreement backstop when the original graph is supplied

Off-serving. Does not touch the live reader dispatch.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from evals.multi_register_program import (
    MultiRegisterError,
    compile_multi_register_program,
    execute_multi_register_program,
)
from generate.math_problem_graph import (
    Comparison,
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Rate,
    Unknown,
)
from generate.math_solver import SolveError, solve
from generate.math_verifier import VerificationError, verify
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import StructureMapRefuse, StructureMapResult
from generate.structure_mapping.role_predicate import RoleGraph
from generate.structure_mapping.selector import SelectorResult, select_structure


@dataclass(frozen=True, slots=True)
class SolveOutcome:
    """Emit or refuse for one structure-mapped problem."""

    emitted: bool
    answer: float | None
    refusal_reason: str | None
    binding: Mapping[str, object] | None
    derivation: str | None
    multi_register_certified: bool
    classical_verified: bool
    structure_id: str | None = None
    source_graph_hash: str | None = None


# Back-compat alias used by Increment 1 imports/tests.
S1SolveOutcome = SolveOutcome


def graph_from_s1_binding(binding: Mapping[str, object]) -> MathProblemGraph:
    """Rebuild a pure S1 :class:`MathProblemGraph` from a role binding."""
    a = str(binding["a"])
    b = str(binding["b"])
    k = float(binding["k"])  # type: ignore[arg-type]
    a_value = float(binding["a_value"])  # type: ignore[arg-type]
    unit = str(binding.get("unit") or "units")
    return MathProblemGraph(
        entities=(a, b),
        initial_state=(
            InitialPossession(entity=a, quantity=Quantity(value=a_value, unit=unit)),
        ),
        operations=(
            Operation(
                actor=b,
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor=a,
                    delta=None,
                    factor=k,
                    direction="times",
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit=unit),
    )


def graph_from_s2_binding(binding: Mapping[str, object]) -> MathProblemGraph:
    src = str(binding["src"])
    dst = str(binding["dst"])
    xfer = float(binding["xfer_qty"])  # type: ignore[arg-type]
    src_val = float(binding["src_value"])  # type: ignore[arg-type]
    dst_val = float(binding["dst_value"])  # type: ignore[arg-type]
    unit = str(binding.get("unit") or "units")
    query = str(binding.get("query_entity") or dst)
    return MathProblemGraph(
        entities=(src, dst),
        initial_state=(
            InitialPossession(entity=src, quantity=Quantity(value=src_val, unit=unit)),
            InitialPossession(entity=dst, quantity=Quantity(value=dst_val, unit=unit)),
        ),
        operations=(
            Operation(
                actor=src,
                kind="transfer",
                operand=Quantity(value=xfer, unit=unit),
                target=dst,
            ),
        ),
        unknown=Unknown(entity=query, unit=unit),
    )


def graph_from_s3_binding(binding: Mapping[str, object]) -> MathProblemGraph:
    rate_value = float(binding["rate_value"])  # type: ignore[arg-type]
    count = float(binding["count"])  # type: ignore[arg-type]
    unit = str(binding.get("unit") or "units")
    actor = str(binding.get("count_name") or "actor")
    return MathProblemGraph(
        entities=(actor,),
        initial_state=(
            InitialPossession(
                entity=actor, quantity=Quantity(value=count, unit="units")
            ),
        ),
        operations=(
            Operation(
                actor=actor,
                kind="apply_rate",
                operand=Rate(
                    value=rate_value,
                    numerator_unit=unit,
                    denominator_unit="units",
                ),
            ),
        ),
        unknown=Unknown(entity=actor, unit=unit),
    )


def graph_from_s4_binding(binding: Mapping[str, object]) -> MathProblemGraph:
    a = str(binding["a"])
    b = str(binding["b"])
    delta = float(binding["delta"])  # type: ignore[arg-type]
    a_value = float(binding["a_value"])  # type: ignore[arg-type]
    unit = str(binding.get("unit") or "units")
    direction = "more" if delta >= 0 else "fewer"
    abs_delta = abs(delta)
    return MathProblemGraph(
        entities=(a, b),
        initial_state=(
            InitialPossession(entity=a, quantity=Quantity(value=a_value, unit=unit)),
        ),
        operations=(
            Operation(
                actor=b,
                kind="compare_additive",
                operand=Comparison(
                    reference_actor=a,
                    delta=Quantity(value=abs_delta, unit=unit),
                    factor=None,
                    direction=direction,
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit=unit),
    )


def _graph_from_binding(
    structure_id: str, binding: Mapping[str, object]
) -> MathProblemGraph:
    if structure_id == "S1":
        return graph_from_s1_binding(binding)
    if structure_id == "S2":
        return graph_from_s2_binding(binding)
    if structure_id == "S3":
        return graph_from_s3_binding(binding)
    if structure_id == "S4":
        return graph_from_s4_binding(binding)
    raise ValueError(f"unknown structure_id for rebuild: {structure_id!r}")


def _derivation(structure_id: str, binding: Mapping[str, object]) -> str:
    if structure_id == "S1":
        a, b = binding["a"], binding["b"]
        k, a_value = float(binding["k"]), float(binding["a_value"])  # type: ignore[arg-type]
        total = a_value * (1.0 + k)
        return (
            f"S1: {b} = {k} × {a}; {a} = {a_value}; "
            f"total = {a} + {b} = {a_value} + {k}*{a_value} = {total}"
        )
    if structure_id == "S2":
        src, dst = binding["src"], binding["dst"]
        xfer = float(binding["xfer_qty"])  # type: ignore[arg-type]
        src_v, dst_v = float(binding["src_value"]), float(binding["dst_value"])  # type: ignore[arg-type]
        q = binding.get("query_entity") or dst
        post_src, post_dst = src_v - xfer, dst_v + xfer
        ans = post_dst if q == dst else post_src
        return (
            f"S2: transfer {xfer} {src}→{dst}; "
            f"pre ({src}={src_v}, {dst}={dst_v}); "
            f"post ({src}={post_src}, {dst}={post_dst}); query {q}={ans}"
        )
    if structure_id == "S3":
        r, c = float(binding["rate_value"]), float(binding["count"])  # type: ignore[arg-type]
        return f"S3: total = rate × count = {r} × {c} = {r * c}"
    if structure_id == "S4":
        a, b = binding["a"], binding["b"]
        d, a_value = float(binding["delta"]), float(binding["a_value"])  # type: ignore[arg-type]
        b_value = a_value + d
        total = a_value + b_value
        return (
            f"S4: {b} = {a} + {d}; {a} = {a_value}; {b} = {b_value}; "
            f"total = {a_value}+{b_value} = {total}"
        )
    return f"{structure_id}: (no derivation template)"


def solve_binding(
    structure_id: str, binding: Mapping[str, object]
) -> SolveOutcome:
    """Solve via multi-register + classical corridors; refuse if uncertified."""
    try:
        graph = _graph_from_binding(structure_id, binding)
    except (KeyError, TypeError, ValueError) as exc:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"binding_incomplete:{type(exc).__name__}:{exc}",
            binding=dict(binding),
            derivation=None,
            multi_register_certified=False,
            classical_verified=False,
            structure_id=structure_id,
        )

    derivation = _derivation(structure_id, binding)

    classical_verified = False
    classical_answer: float | None = None
    try:
        trace = solve(graph)
        verdict = verify(graph, trace)
        classical_verified = bool(verdict.passed)
        classical_answer = float(trace.answer_value)
    except (SolveError, VerificationError, ValueError) as exc:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"classical_solve_or_verify_failed:{type(exc).__name__}:{exc}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=False,
            structure_id=structure_id,
        )

    if not classical_verified:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="classical_verifier_rejected",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=False,
            structure_id=structure_id,
        )

    mr_certified = False
    mr_answer: float | None = None
    try:
        program = compile_multi_register_program(graph)
        outcome = execute_multi_register_program(program)
        mr_certified = bool(outcome.certified)
        mr_answer = float(outcome.answer)
    except MultiRegisterError as exc:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"multi_register_error:{exc.reason}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
            structure_id=structure_id,
        )
    except Exception as exc:  # noqa: BLE001 — refuse, never crash-as-signal
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"multi_register_unexpected:{type(exc).__name__}:{exc}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
            structure_id=structure_id,
        )

    if not mr_certified:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="multi_register_chain_not_certified",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
            structure_id=structure_id,
        )

    if classical_answer is None or mr_answer is None:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="missing_answer_after_cert",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=mr_certified,
            classical_verified=classical_verified,
            structure_id=structure_id,
        )

    if abs(classical_answer - mr_answer) > 1e-6 * max(1.0, abs(classical_answer)):
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=(
                f"corridor_disagreement:classical={classical_answer},mr={mr_answer}"
            ),
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=mr_certified,
            classical_verified=classical_verified,
            structure_id=structure_id,
        )

    return SolveOutcome(
        emitted=True,
        answer=classical_answer,
        refusal_reason=None,
        binding=dict(binding),
        derivation=derivation,
        multi_register_certified=True,
        classical_verified=True,
        structure_id=structure_id,
    )


def solve_s1_binding(binding: Mapping[str, object]) -> SolveOutcome:
    """Increment 1 API: solve an S1 binding."""
    return solve_binding("S1", binding)


def _original_graph_backstop(
    out: SolveOutcome,
    graph: MathProblemGraph,
    role_graph: RoleGraph,
) -> SolveOutcome:
    if not (out.emitted and out.answer is not None):
        return SolveOutcome(
            emitted=out.emitted,
            answer=out.answer,
            refusal_reason=out.refusal_reason,
            binding=out.binding,
            derivation=out.derivation,
            multi_register_certified=out.multi_register_certified,
            classical_verified=out.classical_verified,
            structure_id=out.structure_id,
            source_graph_hash=role_graph.source_graph_hash,
        )
    try:
        original_trace = solve(graph)
        original_verdict = verify(graph, original_trace)
    except (SolveError, VerificationError, ValueError) as exc:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"original_graph_solve_failed:{type(exc).__name__}:{exc}",
            binding=out.binding,
            derivation=out.derivation,
            multi_register_certified=out.multi_register_certified,
            classical_verified=False,
            structure_id=out.structure_id,
            source_graph_hash=role_graph.source_graph_hash,
        )
    if not original_verdict.passed:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="original_graph_verifier_rejected",
            binding=out.binding,
            derivation=out.derivation,
            multi_register_certified=out.multi_register_certified,
            classical_verified=False,
            structure_id=out.structure_id,
            source_graph_hash=role_graph.source_graph_hash,
        )
    orig_ans = float(original_trace.answer_value)
    if abs(orig_ans - float(out.answer)) > 1e-6 * max(1.0, abs(orig_ans)):
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=(
                f"original_graph_disagreement:original={orig_ans},"
                f"rebuild={out.answer}"
            ),
            binding=out.binding,
            derivation=out.derivation,
            multi_register_certified=out.multi_register_certified,
            classical_verified=out.classical_verified,
            structure_id=out.structure_id,
            source_graph_hash=role_graph.source_graph_hash,
        )
    return SolveOutcome(
        emitted=out.emitted,
        answer=out.answer,
        refusal_reason=out.refusal_reason,
        binding=out.binding,
        derivation=out.derivation,
        multi_register_certified=out.multi_register_certified,
        classical_verified=out.classical_verified,
        structure_id=out.structure_id,
        source_graph_hash=role_graph.source_graph_hash,
    )


def try_structure_map_and_solve(
    graph: MathProblemGraph | None = None,
    *,
    role_graph: RoleGraph | None = None,
    families: tuple[str, ...] = ("S1", "S2", "S3", "S4"),
) -> SolveOutcome:
    """Convert (if needed) → selector → solve corridor.

    Never takes a gold structure label. When the original graph is supplied,
    the original-graph integrity backstop runs after a successful emit.
    For S2, if the original graph's ``unknown.entity`` is set, it overrides
    the default query endpoint before solve.
    """
    if role_graph is None:
        if graph is None:
            return SolveOutcome(
                emitted=False,
                answer=None,
                refusal_reason="no_graph_provided",
                binding=None,
                derivation=None,
                multi_register_certified=False,
                classical_verified=False,
            )
        role_graph = graph_to_role_graph(graph)

    sel: SelectorResult = select_structure(role_graph, families=families)
    if sel.refused or sel.selected is None:
        return SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"structure_map_refuse:{sel.reason}",
            binding=None,
            derivation=None,
            multi_register_certified=False,
            classical_verified=False,
            source_graph_hash=role_graph.source_graph_hash,
        )

    mapped: StructureMapResult = sel.selected
    binding = dict(mapped.binding)

    # S2: prefer original unknown entity when present.
    if mapped.structure_id == "S2" and graph is not None and graph.unknown.entity:
        binding["query_entity"] = graph.unknown.entity

    out = solve_binding(mapped.structure_id, binding)

    if graph is not None:
        return _original_graph_backstop(out, graph, role_graph)

    return SolveOutcome(
        emitted=out.emitted,
        answer=out.answer,
        refusal_reason=out.refusal_reason,
        binding=out.binding,
        derivation=out.derivation,
        multi_register_certified=out.multi_register_certified,
        classical_verified=out.classical_verified,
        structure_id=out.structure_id,
        source_graph_hash=role_graph.source_graph_hash,
    )


def try_s1_structure_map_and_solve(
    graph: MathProblemGraph | None = None,
    *,
    role_graph: RoleGraph | None = None,
) -> SolveOutcome:
    """Increment 1 API: S1-only vertical slice (selector restricted to S1)."""
    return try_structure_map_and_solve(
        graph, role_graph=role_graph, families=("S1",)
    )
