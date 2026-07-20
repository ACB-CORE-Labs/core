from __future__ import annotations

from core.cognition.surface_resolution import (
    _conjugate_coherence_ok,
    _forward_surface_ok,
    _substrate_supreme,
    resolve_surface,
)
from generate.graph_planner import GraphNode, PropositionGraph
from generate.intent import IntentTag
from generate.problem_frame_contracts import ContractAssessment


def _closed_assessment() -> ContractAssessment:
    """Geometric contract closed: no missing bindings / hazards."""
    return ContractAssessment(
        candidate_organ="shadow_coherence_gate",
        missing_bindings=(),
        unresolved_hazards=(),
        runnable=True,
        explanation="versor_condition=0; R_GoldTether=0",
    )


def _open_assessment() -> ContractAssessment:
    return ContractAssessment(
        candidate_organ="shadow_coherence_gate",
        missing_bindings=("versor_condition",),
        unresolved_hazards=("goldtether_residual",),
        runnable=False,
        explanation="open geometric contract",
    )


def test_runtime_canonical_surface_has_base_precedence() -> None:
    resolved = resolve_surface(
        canonical_surface="canonical",
        pre_decoration_surface="pre-decoration",
        response_surface="runtime",
        response_articulation_surface="articulation",
    )

    assert resolved.surface == "canonical"
    assert resolved.articulation_surface == "articulation"
    assert resolved.authority == "runtime_canonical"
    assert resolved.fold_sources == ()


def test_useful_realizer_requires_conjugate_coherence() -> None:
    """Realizer shim only when conjugate geometric contract is closed."""
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime articulation",
        realized_surface="realizer",
        realizer_useful=True,
        gate_fired=False,
        contract_assessment=_closed_assessment(),
        # No fully grounded graph → forward fails; conjugate ok → realizer shim
    )

    assert resolved.surface == "realizer"
    assert resolved.articulation_surface == "realizer"
    assert resolved.authority == "realizer"


def test_realizer_shim_refused_when_conjugate_open() -> None:
    """Failed geometric residual must not fall back to realizer authority."""
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime articulation",
        realized_surface="realizer",
        realizer_useful=True,
        gate_fired=False,
        contract_assessment=_open_assessment(),
    )
    assert resolved.authority == "runtime"
    assert resolved.surface == "runtime"


def test_gate_fired_keeps_runtime_surface_even_when_realizer_is_useful() -> None:
    resolved = resolve_surface(
        response_surface="runtime refusal",
        response_articulation_surface="runtime refusal articulation",
        realized_surface="realizer noise",
        realizer_useful=True,
        gate_fired=True,
        contract_assessment=_closed_assessment(),
    )

    assert resolved.surface == "runtime refusal"
    assert resolved.articulation_surface == "runtime refusal articulation"
    assert resolved.authority == "runtime"


def test_useless_realizer_keeps_runtime_surface() -> None:
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime articulation",
        realized_surface="Truth is defined as ...",
        realizer_useful=False,
        contract_assessment=_closed_assessment(),
    )

    assert resolved.surface == "runtime"
    assert resolved.articulation_surface == "runtime articulation"
    assert resolved.authority == "runtime"


def test_walk_and_compose_fold_after_selected_authority() -> None:
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime articulation",
        realized_surface="realizer",
        realizer_useful=True,
        walk_surface="walk chain",
        compose_surface="compose transfer",
        contract_assessment=_closed_assessment(),
    )

    assert resolved.surface == "realizer — walk chain — compose transfer"
    assert resolved.articulation_surface == "realizer — walk chain — compose transfer"
    assert resolved.authority == "realizer"
    assert resolved.fold_sources == ("walk", "compose")


def test_folds_stand_alone_when_base_surface_is_empty() -> None:
    resolved = resolve_surface(walk_surface="walk chain", compose_surface="compose transfer")

    assert resolved.surface == "walk chain — compose transfer"
    assert resolved.articulation_surface == "walk chain — compose transfer"
    assert resolved.authority == "runtime"
    assert resolved.fold_sources == ("walk", "compose")


# --- Dual-competing Shadow Coherence Gate ---

def _mk_grounded_graph() -> PropositionGraph:
    n = GraphNode(
        node_id="n0",
        subject="Evidence",
        predicate="supports",
        obj="Hypothesis",
        source_intent=IntentTag.DEFINITION,
    )
    return PropositionGraph(nodes=(n,), edges=())


def _mk_pending_graph() -> PropositionGraph:
    n = GraphNode(
        node_id="n0",
        subject="Evidence",
        predicate="supports",
        obj="<pending>",
        source_intent=IntentTag.DEFINITION,
    )
    return PropositionGraph(nodes=(n,), edges=())


def test_substrate_supreme_requires_forward_and_conjugate() -> None:
    """Dual gate: grounded graph + closed geometric assessment."""
    g = _mk_grounded_graph()
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime art",
        realized_surface="The evidence supports the hypothesis.",
        realizer_useful=True,
        gate_fired=False,
        proposition_graph=g,
        contract_assessment=_closed_assessment(),
    )
    assert resolved.authority == "substrate_realizer"
    assert resolved.surface == "The evidence supports the hypothesis."


def test_substrate_refused_without_assessment() -> None:
    """Assessment=None fails conjugate competitor (fail-closed)."""
    g = _mk_grounded_graph()
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime art",
        realized_surface="The evidence supports the hypothesis.",
        realizer_useful=True,
        gate_fired=False,
        proposition_graph=g,
        contract_assessment=None,
    )
    assert resolved.authority == "runtime"


def test_pending_graph_withholds_substrate_even_if_conjugate_ok() -> None:
    g = _mk_pending_graph()
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime art",
        realized_surface="Evidence supports ...",
        realizer_useful=True,
        gate_fired=False,
        proposition_graph=g,
        contract_assessment=_closed_assessment(),
    )
    # Forward fails (pending); conjugate ok → transitional realizer only
    assert resolved.authority == "realizer"


def test_open_geometric_contract_refuses_substrate_and_realizer() -> None:
    g = _mk_grounded_graph()
    resolved = resolve_surface(
        response_surface="runtime",
        response_articulation_surface="runtime art",
        realized_surface="The evidence supports the hypothesis.",
        realizer_useful=True,
        gate_fired=False,
        proposition_graph=g,
        contract_assessment=_open_assessment(),
    )
    assert resolved.authority == "runtime"
    assert resolved.surface == "runtime"


def test_gate_fired_still_blocks_substrate_even_for_grounded_graph() -> None:
    g = _mk_grounded_graph()
    resolved = resolve_surface(
        response_surface="I don't have field coordinates for that yet.",
        response_articulation_surface="...",
        realized_surface="The evidence supports the hypothesis.",
        realizer_useful=True,
        gate_fired=True,
        proposition_graph=g,
        contract_assessment=_closed_assessment(),
    )
    assert resolved.authority == "runtime"
    assert resolved.surface == "I don't have field coordinates for that yet."


def test_dual_competitors_helpers() -> None:
    g = _mk_grounded_graph()
    closed = _closed_assessment()
    open_a = _open_assessment()
    assert _forward_surface_ok(g, closed) is True
    assert _conjugate_coherence_ok(closed) is True
    assert _substrate_supreme(g, closed) is True
    assert _conjugate_coherence_ok(None) is False
    assert _conjugate_coherence_ok(open_a) is False
    assert _substrate_supreme(g, open_a) is False
    assert _forward_surface_ok(_mk_pending_graph(), closed) is False
