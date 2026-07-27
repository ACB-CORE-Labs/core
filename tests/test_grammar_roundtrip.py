"""Tests for the grammar round-trip lane.

The load-bearing tests here are the *mutation* tests.  This lane exists because
``evals/deterministic_fluency`` reports 1.00 on all six predicates while
accepting ``"banana does the."`` — a pin that cannot fail is worthless.  So
every guarantee this lane makes is paired with a test proving the guarantee can
be broken.
"""

from __future__ import annotations

import pytest

from evals.grammar_roundtrip import runner as rt_runner
from evals.grammar_roundtrip.corpora import (
    negative_surface_cases,
    positive_graph_cases,
    positive_surface_cases,
)
from evals.grammar_roundtrip.projection import (
    CanonicalProposition,
    compare,
    from_meaning_graph,
    from_proposition_graph,
    quantifier_predicate,
)
from evals.grammar_roundtrip.runner import run_lane
from generate.graph_planner import (
    ArticulationStep,
    ArticulationTarget,
    GraphNode,
    PropositionGraph,
    RhetoricalMove,
)
from generate.intent import IntentTag
from generate.meaning_graph.model import (
    Entity,
    MeaningGraph,
    MeaningSpan,
    Relation,
)
from generate.meaning_graph.reader import Comprehension, Refusal, comprehend


# The three strings that pass every content predicate of
# evals/deterministic_fluency.  This lane's rejection of them is the concrete,
# recorded improvement over that lane.
_FLUENCY_LANE_FALSE_POSITIVES = (
    "banana does the.",
    "wet ground rains the is.",
    "is is is is.",
)


@pytest.fixture(scope="module")
def report():
    return run_lane()


# --------------------------------------------------------------------------- #
# The negative corpus: the guarantee, and proof it can fail
# --------------------------------------------------------------------------- #


def test_negative_corpus_is_fully_rejected(report):
    """Word salad must never be comprehended into propositions."""
    assert report.metrics["reject_rate"] == 1.0
    assert report.metrics["negative_cases"] >= 16


def test_the_fluency_lanes_false_positives_are_rejected():
    """The exact strings deterministic_fluency passes must be refused here."""
    for surface in _FLUENCY_LANE_FALSE_POSITIVES:
        result = comprehend(surface, source_id="t")
        if isinstance(result, Refusal):
            continue
        assert not from_meaning_graph(result.meaning_graph), (
            f"{surface!r} was comprehended into propositions; the negative "
            "corpus guarantee is broken"
        )


def test_reject_rate_goes_red_when_the_reader_accepts_everything(monkeypatch):
    """MUTATION: an accept-everything reader must drive reject_rate to 0.

    Without this test ``reject_rate == 1.0`` would be unfalsifiable — exactly
    the defect that makes the existing fluency lane decoration.
    """
    span = MeaningSpan(source_id="t", start=0, end=1, text="x")
    graph = MeaningGraph(
        entities=(
            Entity(entity_id="a", name="a", span=span),
            Entity(entity_id="b", name="b", span=span),
        ),
        relations=(Relation(predicate="subset", arguments=("a", "b"), span=span),),
    )
    monkeypatch.setattr(
        rt_runner, "comprehend", lambda text, source_id="input": Comprehension(meaning_graph=graph)
    )
    mutated = run_lane()
    assert mutated.metrics["reject_rate"] == 0.0, (
        "an accept-everything reader still scored a perfect reject_rate — the "
        "negative corpus is not actually gating"
    )


def test_shuffled_negatives_reuse_positive_vocabulary():
    """Shuffles must be lexically identical to a positive, order destroyed.

    A lane that rejects only hand-authored salad could be checking vocabulary
    rather than grammar.  The shuffles remove that escape.
    """
    positives = {
        frozenset(c.surface.rstrip(".").lower().split()) for c in positive_surface_cases()
    }
    shuffles = [c for c in negative_surface_cases() if c.case_id.startswith("neg-shuf-")]
    assert shuffles, "no shuffled negatives were generated"
    for case in shuffles:
        tokens = frozenset(case.surface.rstrip(".").lower().split())
        assert tokens in positives, (
            f"{case.case_id} does not reuse a positive case's exact vocabulary"
        )


def test_shuffles_are_byte_stable_across_calls():
    """The negative corpus must be reproducible — no PRNG, no clock."""
    first = tuple(c.surface for c in negative_surface_cases())
    second = tuple(c.surface for c in negative_surface_cases())
    assert first == second


# --------------------------------------------------------------------------- #
# Baselines — these pin DEFECTS and must be revised upward when fixed
# --------------------------------------------------------------------------- #


def test_g_roundtrip_baseline_is_zero(report):
    """BASELINE PIN (a defect, not a goal): CORE reads 0% of what it writes.

    Measured on main @ 9696443a. When the grammar is unified this must be
    revised **upward**; it must never be revised downward to accommodate a
    regression.
    """
    # 293, not the original 280: Phase 3 added 13 quantified-copular cases
    # (construction C14) to grammatical_coverage/public/v1, and this lane
    # harvests its graph corpus from the committed case files rather than
    # holding its own copy. An exact count is the point — a corpus that grows
    # or shrinks should require a deliberate edit here, not pass silently.
    assert report.metrics["graph_cases"] == 293
    assert report.metrics["g_write_rate"] == 1.0
    assert report.metrics["g_read_rate"] == 0.0
    assert report.metrics["g_exact_rate"] == 0.0


def test_s_roundtrip_closes_for_every_renderable_surface(report):
    """Phase 2A pinned this at **0.0** — nothing CORE read rendered back to its
    input, because the serving renderer interpolated singularized entity ids
    into plural templates ("all dog are animal").

    Phase 2B re-inflects at render time, and every surface the renderer can
    express now returns its input exactly. The two rates are equal on purpose:
    ``s_surface_match_rate == s_renderable_rate`` says the *only* remaining
    round-trip losses are surfaces the categorical renderer cannot express at
    all, which is a coverage gap in a later phase, not a grammar defect.

    Asserting equality rather than a literal keeps this honest if the corpus
    grows: adding an unrenderable positive lowers both numbers together, while
    reintroducing the plural defect lowers only the match rate.
    """
    assert report.metrics["s_read_rate"] == 1.0
    assert report.metrics["s_surface_match_rate"] == report.metrics["s_renderable_rate"]
    assert report.metrics["s_surface_match_rate"] > 0.0


def test_the_categorical_render_defect_is_fixed_concretely():
    """The 2A defect stated as an example rather than a rate, now inverted.

    Both sides matter: the graph still carries the SINGULAR canonical id
    (``dog``), so the fix is in the renderer's inflection and not in the
    comprehension it was built to preserve.
    """
    result = comprehend("All dogs are animals.", source_id="t")
    assert isinstance(result, Comprehension)
    props = sorted(from_meaning_graph(result.meaning_graph))
    assert props == [CanonicalProposition("subset", "dog", "animal", False)]
    rendered = rt_runner._render_categorical("subset", "dog", "animal")
    assert rendered == "all dogs are animals"


def test_irregular_plurals_survive_the_full_round_trip():
    """The reader and renderer now share one number table, so an irregular
    plural returns as itself. Before 2B this produced ``all wolve are
    mammals`` — the reader's bare ``-s`` strip leaking a corrupted id straight
    into served text."""
    cases = (
        ("All wolves are mammals.", "wolf", "all wolves are mammals"),
        ("All children are mammals.", "child", "all children are mammals"),
        ("All men are mammals.", "man", "all men are mammals"),
        ("All knives are tools.", "knife", "all knives are tools"),
    )
    for surface, singular, expected_clause in cases:
        result = comprehend(surface, source_id="t")
        assert isinstance(result, Comprehension), surface
        props = sorted(from_meaning_graph(result.meaning_graph))
        assert props[0].subject == singular, f"{surface} -> {props}"
        rendered = rt_runner._render_categorical("subset", singular, props[0].obj)
        assert rendered == expected_clause


# --------------------------------------------------------------------------- #
# The projection itself
# --------------------------------------------------------------------------- #


def test_quantifier_map_matches_reader():
    """The lane's local quantifier map must track the reader's.

    The copy is deliberate — the lane must not import the thing it measures —
    so this test is what keeps the yardstick honest if the reader changes.
    """
    from generate.meaning_graph.reader import _QUANTIFIER_PREDICATE as reader_map

    for quantifier, predicate in reader_map.items():
        assert quantifier_predicate(quantifier) == predicate
    assert quantifier_predicate(None) is None
    assert quantifier_predicate("nonsense") is None


def test_proposition_graph_projection_folds_quantifier():
    """A writer graph's ``quantifier`` slot folds into the reading predicate."""
    node = GraphNode(
        node_id="n1", subject="dog", predicate="is_a", obj="animal",
        source_intent=IntentTag.UNKNOWN,
    )
    step = ArticulationStep(
        node_id="n1", move=RhetoricalMove.ASSERT, predicate="is_a",
        subject="dog", quantifier="all",
    )
    projected = from_proposition_graph(
        PropositionGraph(nodes=(node,)),
        ArticulationTarget(steps=(step,), source_intent=IntentTag.UNKNOWN),
    )
    assert projected == frozenset({CanonicalProposition("subset", "dog", "animal", False)})


def test_projection_drops_non_binary_relations():
    """Arity != 2 is dropped — the writing side cannot express it."""
    span = MeaningSpan(source_id="t", start=0, end=1, text="x")
    graph = MeaningGraph(
        entities=(
            Entity(entity_id="a", name="a", span=span),
            Entity(entity_id="b", name="b", span=span),
            Entity(entity_id="c", name="c", span=span),
        ),
        relations=(
            Relation(predicate="between", arguments=("a", "b", "c"), span=span),
            Relation(predicate="subset", arguments=("a", "b"), span=span),
        ),
    )
    assert from_meaning_graph(graph) == frozenset(
        {CanonicalProposition("subset", "a", "b", False)}
    )


def test_compare_decomposes_argument_and_predicate_agreement():
    """A predicate name only counts when it agrees on the SAME arguments."""
    expected = frozenset({CanonicalProposition("subset", "dog", "animal")})
    # right arguments, wrong predicate name
    args_only = frozenset({CanonicalProposition("member", "dog", "animal")})
    agreement = compare(expected, args_only)
    assert agreement.args_match == 1
    assert agreement.predicates_match == 0
    assert agreement.exact_match == 0

    # right predicate name, wrong arguments — must NOT count
    pred_elsewhere = frozenset({CanonicalProposition("subset", "cat", "plant")})
    agreement = compare(expected, pred_elsewhere)
    assert agreement.args_match == 0
    assert agreement.predicates_match == 0


def test_compare_exact_agreement():
    prop = CanonicalProposition("subset", "dog", "animal")
    agreement = compare(frozenset({prop}), frozenset({prop}))
    assert agreement.exact_rate == 1.0
    assert agreement.args_rate == 1.0
    assert agreement.predicates_rate == 1.0


# --------------------------------------------------------------------------- #
# Corpus integrity
# --------------------------------------------------------------------------- #


def test_positive_surfaces_are_all_inside_the_reader_envelope():
    """Every positive surface must actually be comprehended.

    A refused positive would silently measure the reader's coverage instead of
    the round-trip, and would make s_surface_match_rate uninterpretable.
    """
    for case in positive_surface_cases():
        result = comprehend(case.surface, source_id="t")
        assert isinstance(result, Comprehension), (
            f"{case.case_id} ({case.surface!r}) is refused; it does not belong "
            "in the positive corpus"
        )


def test_graph_corpus_is_harvested_from_committed_case_files():
    cases = positive_graph_cases()
    assert len(cases) == 293  # +13 C14 quantified-copular (Phase 3)
    assert all(c.nodes for c in cases)
