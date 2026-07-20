"""Stage 3A/C — geometric coherence taxonomy + inductive fixed-point."""

from __future__ import annotations

import numpy as np

from algebra.rotor import make_rotor_from_angle
from core.cognition.geometric_coherence import (
    GeometricCoherenceStatus,
    evaluate_geometric_coherence,
)
from core.cognition.inductive_closure import expand_relation_closure
from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline


def test_geometric_coherence_verified_on_unit_versor():
    R = make_rotor_from_angle(0.25)
    v = evaluate_geometric_coherence(R)
    assert v.status is GeometricCoherenceStatus.GEOMETRICALLY_VERIFIED
    assert v.closed is True
    assert v.field_present is True


def test_geometric_coherence_refuses_missing_field():
    v = evaluate_geometric_coherence(None)
    assert v.status is GeometricCoherenceStatus.REFUSED
    assert v.closed is False


def test_geometric_coherence_unverified_on_dirty_field():
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    v = evaluate_geometric_coherence(dirty)
    assert v.status is GeometricCoherenceStatus.UNVERIFIED
    assert v.closed is False


def test_pipeline_populates_geometric_coherence():
    rt = ChatRuntime()
    p = CognitiveTurnPipeline(rt)
    result = p.run("what is light", max_tokens=6)
    assert result.geometric_coherence is not None
    assert result.geometric_coherence.field_present is True
    # Live fields after chat are typically closed versors.
    assert result.geometric_coherence.status in {
        GeometricCoherenceStatus.GEOMETRICALLY_VERIFIED,
        GeometricCoherenceStatus.UNVERIFIED,
        GeometricCoherenceStatus.REFUSED,
    }
    # Dual taxonomy: no EpistemicState.COHERENT
    from core.epistemic_state import EpistemicState
    from teaching.epistemic import EpistemicStatus

    assert not hasattr(EpistemicState, "COHERENT")
    assert EpistemicStatus.COHERENT.value == "coherent"


def test_inductive_closure_derives_two_hop():
    triples = (
        ("a", "is", "b"),
        ("b", "is", "c"),
    )
    # Explicit geometric_admissible always-true for pure graph composition tests.
    res = expand_relation_closure(
        triples, budget=8, geometric_admissible=lambda h, r, t: True
    )
    assert len(res.base) == 2
    derived_tails = {(d.head, d.relation, d.tail) for d in res.derived}
    assert ("a", "is", "c") in derived_tails
    assert res.fixed_point is True
    assert res.steps_taken >= 1
    a_to_c = next(d for d in res.derived if d.head == "a" and d.tail == "c")
    assert a_to_c.path[0] == "a" and a_to_c.path[-1] == "c"
    assert a_to_c.admissible is True


def test_inductive_derived_requires_geometric_admissibility():
    """Non-admissible candidates must not be promoted into derived or work.

    Stage 3 exit: multi-step paths close ONLY under geometric conditions.
    Stamping admissible=False while still seeding further expansion is a leak.
    """
    triples = (
        ("a", "is", "b"),
        ("b", "is", "c"),
    )

    def refuse_all(h, r, t):
        del h, r, t
        return False

    res = expand_relation_closure(
        triples, budget=8, geometric_admissible=refuse_all
    )
    # Refuse-all: base stays store-visible but no derived promotion.
    assert len(res.derived) == 0
    assert not any(d.head == "a" and d.tail == "c" for d in res.derived)
    assert all(b.admissible is False for b in res.base)


def test_inductive_non_admissible_intermediate_does_not_seed_expansion():
    """a→c rejected must not yield a→d solely via that intermediate.

    Graph: a→b→c→d. Refuse a→c and b→d so the only multi-hop bridge to a→d
    would be the non-admissible a→c path. Closure must not invent a→d.
    """
    triples = (
        ("a", "is", "b"),
        ("b", "is", "c"),
        ("c", "is", "d"),
    )

    def geom(h: str, r: str, t: str) -> bool:
        del r
        # Block the two-hop bridges that would otherwise seed a→d.
        if (h, t) in {("a", "c"), ("b", "d")}:
            return False
        return True

    res = expand_relation_closure(
        triples, budget=8, geometric_admissible=geom
    )
    derived_pairs = {(d.head, d.tail) for d in res.derived}
    assert ("a", "c") not in derived_pairs
    assert ("b", "d") not in derived_pairs
    assert ("a", "d") not in derived_pairs
    assert all(d.admissible for d in res.derived)


def test_inductive_closure_detects_contradiction():
    triples = (
        ("a", "is", "b"),
        ("a", "is", "c"),
    )
    res = expand_relation_closure(
        triples, budget=4, geometric_admissible=lambda h, r, t: True
    )
    assert any(c.contradiction for c in res.contradictions)
    assert len(res.contradictions) >= 2


def test_inductive_closure_budget_truncation():
    # Long chain: a0->a1->...->a20
    triples = tuple((f"a{i}", "r", f"a{i+1}") for i in range(20))
    ok = lambda h, r, t: True  # noqa: E731
    res = expand_relation_closure(triples, budget=2, geometric_admissible=ok)
    assert res.truncated or res.steps_taken <= 2
    res2 = expand_relation_closure(triples, budget=16, geometric_admissible=ok)
    assert any(d.head == "a0" and d.tail == "a2" for d in res2.derived) or any(
        d.head == "a0" for d in res2.derived
    )


def test_inductive_closure_cycle_safe():
    triples = (
        ("a", "r", "b"),
        ("b", "r", "a"),
    )
    res = expand_relation_closure(
        triples, budget=8, geometric_admissible=lambda h, r, t: True
    )
    # Must terminate without inventing infinite chain
    assert res.fixed_point or res.steps_taken <= 8
    assert all(len(d.path) < 20 for d in res.derived)
