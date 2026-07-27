"""CORE must not serve the affirmative of a proposition the user denied.

The defect
----------
The intent parser has always recovered negation from the user's text
(``intent.negated``, ``generate/intent.py``). Everything downstream threw it
away: ``GraphNode`` had no slot for it, so ``plan_articulation`` could not
carry it, so ``realize_semantic`` never saw it — and ``render_semantic`` had no
parameter for it in any case. Two independent drops in series.

Measured on ``main`` @ 536d6e55 with ``realizer_grounded_authority=True``::

    "evidence does not support truth" -> 'Evidence is verified: what supports truth.'
    "evidence supports truth"         -> 'Evidence is verified: what supports truth.'

Byte-identical. CORE affirmed what the user denied.

Why it was invisible
--------------------
On the default config the realizer's ungrounded surface contains ``...``,
``_is_useful_surface`` rejects it, and the runtime's echo wins the resolver —
which happens to preserve the user's own "does not". The truth path was
correct **by accident**, and grounding the graph (ADR-0088 Phase B) removes the
accident. So every pre-existing test passed while the defect sat live behind a
shipped flag.

That is why the load-bearing test here is
``test_a_denial_and_its_assertion_do_not_serve_the_same_surface``: it asserts a
DIFFERENCE between two turns rather than a property of one, which is the only
shape that can catch a writer collapsing a distinction.
"""

from __future__ import annotations

import pytest

from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline
from core.config import RuntimeConfig
from generate.graph_planner import (
    GraphNode,
    RhetoricalMove,
    graph_from_intent,
    ground_graph,
    plan_articulation,
)
from generate.intent import IntentTag, classify_intent
from generate.lexicon import PREDICATE_DISPLAY
from generate.realizer import realize_semantic
from generate.semantic_templates import render_semantic
from generate.templates import render_step


#: Inputs the declarative parser recognises as denials. It requires do-support
#: plus one of its relation verbs ("X does not support Y"), which is why these
#: are phrased the way they are rather than "X is not Y".
_DENIAL_PAIRS = [
    ("evidence does not support truth", "evidence supports truth"),
    ("wisdom does not require knowledge", "wisdom requires knowledge"),
    ("knowledge does not ground belief", "knowledge grounds belief"),
]


# --------------------------------------------------------------------------- #
# THE CONTROL — a denial must not serve as its own assertion
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(("denial", "assertion"), _DENIAL_PAIRS)
def test_a_denial_and_its_assertion_do_not_serve_the_same_surface(
    denial: str, assertion: str
) -> None:
    """The regression test for the defect itself, end to end through the real
    pipeline under the flag that makes the realizer's surface authoritative.

    Asserting a *difference* is the point. Every property-of-one-surface test
    passed while these two were byte-identical.
    """
    served = []
    for text in (denial, assertion):
        runtime = ChatRuntime(config=RuntimeConfig(realizer_grounded_authority=True))
        served.append(CognitiveTurnPipeline(runtime=runtime).run(text, max_tokens=6).surface)

    assert served[0] != served[1], (
        f"CORE served the same surface for {denial!r} and {assertion!r}: {served[0]!r}"
    )
    assert " not " in served[0], f"the denial lost its negation: {served[0]!r}"
    assert " not " not in served[1], f"the assertion gained one: {served[1]!r}"


@pytest.mark.parametrize(("denial", "assertion"), _DENIAL_PAIRS)
def test_the_whole_chain_carries_the_denial(denial: str, assertion: str) -> None:
    """intent.negated -> GraphNode.negated -> ArticulationStep.negated.

    Pinned link by link: before Phase 5 the first arrow existed and the second
    did not, so a green ``intent.negated`` proved nothing about what shipped.
    """
    intent = classify_intent(denial)
    assert intent.negated is True, "the parser stopped recognising this denial"

    graph = graph_from_intent(intent)
    assert graph.nodes[0].negated is True, "the graph dropped the denial"

    target = plan_articulation(graph)
    assert target.steps[0].negated is True, "the articulation target dropped the denial"

    assert "not" in realize_semantic(target, graph).surface

    # And the affirmative stays clean at every link.
    pos = classify_intent(assertion)
    assert pos.negated is False
    assert graph_from_intent(pos).nodes[0].negated is False


def test_grounding_does_not_launder_the_denial_away() -> None:
    """``ground_graph`` rebuilds every node field-by-field, and grounding is
    precisely the path (ADR-0088 Phase B) on which the realizer's surface stops
    being rejected and starts reaching users. Dropping the flag here would
    restore the defect on the only turns where it is visible."""
    intent = classify_intent("evidence does not support truth")
    graph = graph_from_intent(intent)
    grounded = ground_graph(graph, ("reality",))

    assert grounded.nodes[0].obj == "reality", "fixture no longer grounds anything"
    assert grounded.nodes[0].negated is True


# --------------------------------------------------------------------------- #
# The delegation is output-preserving — the churn budget
# --------------------------------------------------------------------------- #


_DELEGATED = {
    IntentTag.UNKNOWN: (None, RhetoricalMove.ASSERT),
    IntentTag.CORRECTION: (None, RhetoricalMove.CORRECT),
    IntentTag.DEFINITION: ("is_defined_as", RhetoricalMove.ASSERT),
    IntentTag.CAUSE: ("is_grounded_in", RhetoricalMove.ASSERT),
}


@pytest.mark.parametrize("intent", sorted(_DELEGATED, key=lambda i: i.name))
def test_delegating_the_clause_changes_no_affirmative_surface(intent: IntentTag) -> None:
    """Four intent templates were never frames — they were plain clauses. They
    now route through ``render_step``, the single owner of clause grammar,
    rather than a second copy of it here.

    This pins that the move is byte-identical on every affirmative input, so
    the only surfaces the change moves are ones that were WRONG. If this goes
    red, the unification has started rewriting correct output and the diff
    needs re-reading, not re-pinning.
    """
    override, move = _DELEGATED[intent]
    predicates = [*sorted(PREDICATE_DISPLAY)[:14], "is_verified_as", "unknown_pred_xyz"]
    for predicate in predicates:
        for obj in ("truth", "<pending>", "<prior>"):
            expected = render_step(
                move,
                "evidence",
                override or predicate,
                obj if obj not in ("<pending>", "<prior>") else "...",
            )
            assert render_semantic(intent, "evidence", predicate, obj) == expected


def test_serialisation_is_byte_identical_while_the_flag_is_false() -> None:
    """``negated`` is emitted only when True, so every pre-existing
    ``as_dict`` — and every ``trace_hash`` folded from one — is unchanged.
    This is what let the change land without touching a single lane pin."""
    node = GraphNode("p0", "evidence", "supports", "truth", IntentTag.UNKNOWN)
    assert "negated" not in node.as_dict()

    denied = GraphNode("p0", "evidence", "supports", "truth", IntentTag.UNKNOWN, negated=True)
    assert denied.as_dict()["negated"] is True


# --------------------------------------------------------------------------- #
# Frames deny inside themselves; the one that cannot, falls back
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    ("intent", "expected"),
    [
        (IntentTag.VERIFICATION, "evidence is not verified: truth"),
        (IntentTag.DEFINITION, "evidence is not defined as truth"),
        (IntentTag.CAUSE, "evidence is not grounded in truth"),
    ],
)
def test_a_frame_with_a_finite_verb_denies_inside_itself(
    intent: IntentTag, expected: str
) -> None:
    assert render_semantic(intent, "evidence", "supports", "truth", negated=True) == expected


def test_recall_has_no_proposition_to_deny_so_it_falls_back_to_a_clause() -> None:
    """"recalling X: Y" is a speech act, not an assertion — there is nothing in
    it to negate. Emitting the frame anyway would silently drop the denial,
    which is the defect. Losing the framing is the correct trade
    (ADR-0261 §5.1, refuse-don't-drop)."""
    affirmative = render_semantic(IntentTag.RECALL, "evidence", "supports", "truth")
    assert affirmative == "recalling evidence: truth"

    denied = render_semantic(IntentTag.RECALL, "evidence", "supports", "truth", negated=True)
    assert "not" in denied, "a negated RECALL silently dropped the denial"
    assert denied != affirmative


def test_every_intent_distinguishes_denial_from_assertion() -> None:
    """The exhaustive form of the control: no IntentTag may render a denial and
    its assertion identically. A new intent added without a negated form fails
    here rather than shipping the defect again."""
    collisions = []
    for intent in IntentTag:
        affirmative = render_semantic(intent, "evidence", "supports", "truth")
        denied = render_semantic(intent, "evidence", "supports", "truth", negated=True)
        if affirmative == denied:
            collisions.append((intent.name, affirmative))
    assert not collisions, f"intents that serve a denial as its assertion: {collisions}"


# --------------------------------------------------------------------------- #
# STRUCTURAL INVARIANT — every GraphNode built on the serving path decides
# --------------------------------------------------------------------------- #
#
# The defect was not one bad line. It was FIVE separate constructors that each
# rebuilt a GraphNode field-by-field and each silently defaulted `negated` back
# to False: graph_from_intent (x3), ground_graph, the pipeline's depth
# enrichment, and intent_bridge (x3). A per-site test has to be written per
# site, and a site added without one is invisible — which is exactly how this
# survived in the first place.
#
# So the pin is structural, in the same shape as the tail-preservation
# invariant in #135: every GraphNode(...) construction in SERVING code must
# name `negated` explicitly, or be recorded below with a reason. Sites nobody
# has written yet are covered.

#: Serving-path constructors allowed to leave `negated` at its default, with
#: the reason. Adding a row is a decision with a diff, not a side effect.
_MAY_DEFAULT_NEGATED: dict[str, str] = {
    # An EpistemicNode is a recognition artefact — a measured observation with
    # no polarity to carry. There is no denial to lose here.
    "recognition/connector.py": "EpistemicNode has no negation concept",
}

_SERVING_ROOTS = ("generate", "core", "chat", "recognition")


def _graphnode_constructions() -> list[tuple[str, int, bool]]:
    """(relative path, line, names_negated) for every GraphNode(...) call in
    serving code. AST-based, so a call spanning lines or reordered kwargs is
    matched the same way."""
    import ast
    from pathlib import Path

    repo = Path(__file__).resolve().parents[1]
    found: list[tuple[str, int, bool]] = []
    for root in _SERVING_ROOTS:
        for path in sorted((repo / root).rglob("*.py")):
            rel = path.relative_to(repo).as_posix()
            try:
                tree = ast.parse(path.read_text())
            except SyntaxError:  # pragma: no cover - not our problem here
                continue
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                fn = node.func
                name = fn.id if isinstance(fn, ast.Name) else getattr(fn, "attr", None)
                if name != "GraphNode":
                    continue
                names_negated = any(kw.arg == "negated" for kw in node.keywords)
                found.append((rel, node.lineno, names_negated))
    return found


def test_every_serving_graphnode_decides_about_negation() -> None:
    """A GraphNode built without naming `negated` asserts the affirmative by
    default. On the serving path that default is a claim about truth, so it
    has to be made deliberately."""
    constructions = _graphnode_constructions()
    assert constructions, "the AST scan found no GraphNode constructions — it is broken"

    silent = [
        (path, line)
        for path, line, names_negated in constructions
        if not names_negated and path not in _MAY_DEFAULT_NEGATED
    ]
    assert not silent, (
        "GraphNode built on the serving path without deciding about negation "
        f"(add `negated=` or record it in _MAY_DEFAULT_NEGATED): {silent}"
    )


def test_the_recorded_exemptions_still_exist() -> None:
    """An allowlist that outlives its file silently widens. Same discipline as
    RECORDED_CONSUMERS in test_lexicon_single_source.py."""
    paths = {path for path, _, _ in _graphnode_constructions()}
    stale = sorted(set(_MAY_DEFAULT_NEGATED) - paths)
    assert not stale, f"recorded exemptions no longer construct a GraphNode: {stale}"
