"""Solve an S1 binding through the existing multi-register certificate corridor.

Reuses ``evals.multi_register_program`` (ADR-0249/0250 Hamiltonian path):
compile graph → execute with ``relax_to_ground`` → require ``certified``.
Emit only when the certificate chain verifies; else refuse.

Also cross-checks classical ``math_solver.solve`` + ``math_verifier.verify``
so derivation is independently replayable (right-for-right-reason).

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
    Unknown,
)
from generate.math_solver import SolveError, solve
from generate.math_verifier import VerificationError, verify
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
)
from generate.structure_mapping.role_predicate import RoleGraph


@dataclass(frozen=True, slots=True)
class S1SolveOutcome:
    """Emit or refuse for one S1-mapped problem."""

    emitted: bool
    answer: float | None
    refusal_reason: str | None
    binding: Mapping[str, object] | None
    derivation: str | None
    """Human-readable derivation for right-reason audits."""
    multi_register_certified: bool
    classical_verified: bool
    source_graph_hash: str | None = None


def graph_from_s1_binding(binding: Mapping[str, object]) -> MathProblemGraph:
    """Rebuild a pure S1 :class:`MathProblemGraph` from a role binding.

    Shape: contain(a)=a_value; compare_multiplicative b = k×a; unknown total.
    """
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


def solve_s1_binding(binding: Mapping[str, object]) -> S1SolveOutcome:
    """Solve via multi-register certificate corridor; refuse if uncertified."""
    required = ("a", "b", "k", "a_value")
    missing = [k for k in required if k not in binding]
    if missing:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"binding_incomplete:{','.join(missing)}",
            binding=dict(binding),
            derivation=None,
            multi_register_certified=False,
            classical_verified=False,
        )

    graph = graph_from_s1_binding(binding)
    a = str(binding["a"])
    b = str(binding["b"])
    k = float(binding["k"])  # type: ignore[arg-type]
    a_value = float(binding["a_value"])  # type: ignore[arg-type]
    expected_formula = a_value * (1.0 + k)
    derivation = (
        f"S1: {b} = {k} × {a}; {a} = {a_value}; "
        f"total = {a} + {b} = {a_value} + {k}*{a_value} = {expected_formula}"
    )

    # Classical solve + independent verify (replay certificate).
    classical_verified = False
    classical_answer: float | None = None
    try:
        trace = solve(graph)
        verdict = verify(graph, trace)
        classical_verified = bool(verdict.passed)
        classical_answer = float(trace.answer_value)
    except (SolveError, VerificationError, ValueError) as exc:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"classical_solve_or_verify_failed:{type(exc).__name__}:{exc}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=False,
        )

    if not classical_verified:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="classical_verifier_rejected",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=False,
        )

    # Hamiltonian multi-register corridor (ADR-0250).
    mr_certified = False
    mr_answer: float | None = None
    try:
        program = compile_multi_register_program(graph)
        outcome = execute_multi_register_program(program)
        mr_certified = bool(outcome.certified)
        mr_answer = float(outcome.answer)
    except MultiRegisterError as exc:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"multi_register_error:{exc.reason}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
        )
    except Exception as exc:  # noqa: BLE001 — refuse, never crash-as-signal
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"multi_register_unexpected:{type(exc).__name__}:{exc}",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
        )

    if not mr_certified:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="multi_register_chain_not_certified",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=False,
            classical_verified=True,
        )

    # Agreement gate: classical and multi-register must agree (wrong=0).
    if classical_answer is None or mr_answer is None:
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason="missing_answer_after_cert",
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=mr_certified,
            classical_verified=classical_verified,
        )

    if abs(classical_answer - mr_answer) > 1e-6 * max(1.0, abs(classical_answer)):
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=(
                f"corridor_disagreement:classical={classical_answer},mr={mr_answer}"
            ),
            binding=dict(binding),
            derivation=derivation,
            multi_register_certified=mr_certified,
            classical_verified=classical_verified,
        )

    # Emit the classically verified scalar once the multi-register chain is
    # certified and both corridors agree within relative 1e-6. Geometric
    # relaxation leaves ~1e-8 relative float noise on the MR decode; the
    # classical solver answer is the exact integer arithmetic of the binding
    # and is independently replay-verified. Refusing to emit the noisier MR
    # float is not a shortcut around the certificate — ``mr_certified`` must
    # still be True.
    return S1SolveOutcome(
        emitted=True,
        answer=classical_answer,
        refusal_reason=None,
        binding=dict(binding),
        derivation=derivation,
        multi_register_certified=True,
        classical_verified=True,
        source_graph_hash=None,
    )


def try_s1_structure_map_and_solve(
    graph: MathProblemGraph | None = None,
    *,
    role_graph: RoleGraph | None = None,
) -> S1SolveOutcome:
    """Convert (if needed) → map_to_s1 → solve corridor. Full S1 vertical slice.

    Accepts either a surface graph or a prebuilt role graph. Never takes a
    gold structure label.
    """
    if role_graph is None:
        if graph is None:
            return S1SolveOutcome(
                emitted=False,
                answer=None,
                refusal_reason="no_graph_provided",
                binding=None,
                derivation=None,
                multi_register_certified=False,
                classical_verified=False,
            )
        role_graph = graph_to_role_graph(graph)

    mapped = map_to_s1(role_graph)
    if isinstance(mapped, StructureMapRefuse):
        return S1SolveOutcome(
            emitted=False,
            answer=None,
            refusal_reason=f"structure_map_refuse:{mapped.reason}",
            binding=None,
            derivation=None,
            multi_register_certified=False,
            classical_verified=False,
            source_graph_hash=role_graph.source_graph_hash,
        )
    assert isinstance(mapped, StructureMapResult)
    out = solve_s1_binding(mapped.binding)
    return S1SolveOutcome(
        emitted=out.emitted,
        answer=out.answer,
        refusal_reason=out.refusal_reason,
        binding=out.binding,
        derivation=out.derivation,
        multi_register_certified=out.multi_register_certified,
        classical_verified=out.classical_verified,
        source_graph_hash=role_graph.source_graph_hash,
    )
