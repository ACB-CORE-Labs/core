"""Pins for the construction-inventory lane (grammar-unification Phase 5, item 1).

Three kinds of test live here, and the difference matters:

**Measurements** record what the two inventories currently share. ``overlap`` is
ratcheted *upward* — that is the number Phase 5 exists to raise.

**Defect pins** record something that is wrong. Each says so in its docstring and
states which direction it may be revised. ``w2r_fabricating`` may only be
revised *downward*; raising it to accommodate a new fabrication would be
recording a regression as progress.

**Structural guards** are AST-keyed so the tables cannot rot. A table of "what
the reader reads" that someone must remember to update is worth nothing — the
guards make forgetting fail loudly.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from generate.graph_planner import RhetoricalMove
from generate.meaning_graph.reader import Refusal, comprehend
from generate.templates import render_step

from evals.construction_inventory.corpora import COUNT_FILLERS, MASS_FILLER, SECONDARY
from evals.construction_inventory.reader_space import (
    READER_CONSTRUCTIONS,
    READER_MINT_SITES,
    render_instance,
)
from evals.construction_inventory.runner import run_lane
from evals.construction_inventory.skeleton import skeleton
from evals.construction_inventory.writer_space import WRITER_ASPECTS, WRITER_TENSES

_REPO = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------- #
# Measurements
# --------------------------------------------------------------------------- #

def test_overlap_is_six_constructions() -> None:
    """The headline. Phase 5 item 1 raises this; it may be revised UPWARD only.

    Six constructions are shared: ``X is a Y``, ``the X is a Y``, and the four
    categoricals (``all`` / ``no`` / ``some`` / ``some ... not``). All six are
    set-theoretic. The writer cannot express a single ordering, propositional or
    interrogative construction, and the reader has no template for the bare
    transitive clause that is the writer's entire default output.
    """
    metrics = run_lane().metrics
    assert metrics["overlap_constructions"] == 6
    assert metrics["w2r_faithful"] == 6
    assert metrics["r2w_expressible"] == 6


def test_the_overlap_is_the_same_six_seen_from_both_sides() -> None:
    """Internal consistency: the two directions must name the same set.

    ``w2r_faithful`` counts writer constructions the reader reads truly;
    ``r2w_expressible`` counts reader constructions the writer can emit. These
    are computed by different code over different corpora, and if they ever
    disagree, one of the two inventories is measuring something else.
    """
    report = run_lane()
    faithful = {
        d["skeleton"] for d in report.case_details
        if d.get("kind") == "writer_construction" and d["bucket"] == "faithful"
    }
    expressible = {
        d["skeleton"] for d in report.case_details
        if d.get("kind") == "reader_construction" and d["writer_can_emit"]
    }
    assert faithful == expressible


def test_reader_side_rate_is_pinned() -> None:
    """The reader's own inventory is 19 constructions; the writer reaches 6."""
    metrics = run_lane().metrics
    assert metrics["reader_constructions"] == 19
    assert metrics["r2w_rate"] == 0.315789


def test_the_shared_six_do_not_depend_on_vocabulary() -> None:
    """Morphology control: the overlap must be the same under every filler.

    If a construction reads for ``dogs`` but not for ``wolves`` or ``children``,
    the lane would be reporting a morphology gap as a construction gap. Zero
    filler-dependence is what licenses calling this a *construction* count.
    """
    assert run_lane().metrics["w2r_filler_dependent"] == 0


# --------------------------------------------------------------------------- #
# Defect pins
# --------------------------------------------------------------------------- #

def test_reader_fabricates_on_twenty_two_writer_constructions() -> None:
    """DEFECT PIN. Revise DOWNWARD only — never up to admit a new fabrication.

    On these the reader neither reads nor refuses: it accepts the surface and
    mints an argument the writer never wrote. That breaks the reader's own
    stated contract ("a fabricated reading is the only failure") and it is on a
    serving path, so it is a ``wrong=0`` hazard, not a cosmetic one.
    """
    metrics = run_lane().metrics
    assert metrics["w2r_fabricating"] == 22
    assert metrics["cells_fabricating"] == 150


def test_reader_invents_propositions_from_ordinary_english() -> None:
    """DEFECT PIN. These are user-typable sentences, not writer artefacts.

    ``every``/``each`` are not in ``_RESERVED``, so they are chunked into the
    entity id and the asserted fact is about an entity that does not exist. A
    later query about ``dog`` then answers UNKNOWN even though the user said it.
    """
    reading = comprehend("every dog is a mammal")
    assert not isinstance(reading, Refusal)
    assert [tuple(r.arguments) for r in reading.meaning_graph.relations] == [
        ("every_dog", "mammal")
    ]

    reading = comprehend("each metal is a conductor")
    assert not isinstance(reading, Refusal)
    assert [tuple(r.arguments) for r in reading.meaning_graph.relations] == [
        ("each_metal", "conductor")
    ]


def test_reader_promotes_a_discourse_connective_to_a_proposition() -> None:
    """DEFECT PIN. ``_parse_propositional`` accepts ANY single token as a fact.

    ``_split_clauses`` splits on commas and strips only a leading ``and``/``or``,
    so a one-word discourse opener becomes its own clause, and the bare-atom rule
    mints it. CORE then recites it back to the user as a premise — see
    ``test_fabricated_premise_reaches_a_served_deduction_surface``.
    """
    reading = comprehend("furthermore, all dogs are mammals")
    assert not isinstance(reading, Refusal)
    minted = [(r.predicate, tuple(r.arguments)) for r in reading.meaning_graph.relations]
    assert ("asserted", ("furthermore",)) in minted


def test_fabricated_premise_reaches_a_served_deduction_surface() -> None:
    """DEFECT PIN — this is the one that shows the hazard is not theoretical.

    The verdict is unaffected here, but the *recital* is: CORE tells the user
    they said ``furthermore``. Revise only by removing the fabrication.
    """
    from chat.deduction_surface import deduction_grounded_surface

    clean = deduction_grounded_surface("if p then q. p. therefore q.")
    leaked = deduction_grounded_surface("furthermore, if p then q. p. therefore q.")

    assert clean == "Given: p implies q; p. Your premises entail: q."
    assert leaked == "Given: furthermore; p implies q; p. Your premises entail: q."


def test_aspect_arms_drop_negation() -> None:
    """DEFECT PIN — ADR-0265's defect class, surviving in the module ADR-0265
    named as the single owner of clause grammar.

    The four aspect arms of ``_inflect_predicate`` match on ``(aspect, ...)``
    with ``negated`` bound to a wildcard and never consult it, so a denial is
    rendered as its own assertion. ADR-0265's invariant is *structural* — it
    checks that ``negated`` is threaded to each call — and cannot see an arm that
    receives the flag and ignores it. This pin is behavioural and can.

    Not reachable today: no producer sets ``aspect`` on the serving path (only
    ``generate/realizer.py`` forwards ``step.aspect``, which is always None). It
    is a loaded gun, not a casualty — the distinction ADR-0265 got wrong once
    already, so it is stated explicitly rather than assumed.

    Revise DOWNWARD only; ``0`` is the fixed state.
    """
    assert run_lane().metrics["negation_collapsed_points"] == 10530

    for aspect in ("perfective", "imperfective"):
        affirmed = render_step(
            RhetoricalMove.ASSERT, "dog", "is_defined_as", "mammal",
            negated=False, aspect=aspect,
        )
        denied = render_step(
            RhetoricalMove.ASSERT, "dog", "is_defined_as", "mammal",
            negated=True, aspect=aspect,
        )
        assert affirmed == denied, f"aspect={aspect} now distinguishes polarity — revise DOWN"


# --------------------------------------------------------------------------- #
# Structural guards
# --------------------------------------------------------------------------- #

def _mint_sites(path: Path) -> list[tuple[str, int]]:
    """Every ``relations.append`` / ``queries.append`` in *path*."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "append"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in ("relations", "queries")
        ):
            found.append((node.func.value.id, node.lineno))
    return found


def test_reader_inventory_covers_every_mint_site() -> None:
    """STRUCTURAL GUARD. A new reader template must be entered in the table.

    A ``Comprehension`` can only be populated through a ``relations.append`` or
    ``queries.append`` call, so the count of those calls bounds the number of
    constructions. When someone adds a template, this goes red until
    ``READER_CONSTRUCTIONS`` names its mint site — which is the only thing
    keeping the overlap number honest as the reader grows.
    """
    sites = _mint_sites(_REPO / "generate" / "meaning_graph" / "reader.py")
    assert len(sites) == 10, f"reader mint sites changed: {sites}"
    assert len(READER_MINT_SITES) == 10


def test_every_reader_construction_is_read_by_the_reader() -> None:
    """STRUCTURAL GUARD. The table must describe the reader, not an aspiration.

    A construction the reader refuses would inflate ``reader_constructions`` and
    depress ``r2w_rate`` for a reason that has nothing to do with the writer.
    """
    for construction in READER_CONSTRUCTIONS:
        for filler in COUNT_FILLERS:
            instance = render_instance(construction, filler)
            reading = comprehend(instance)
            assert not isinstance(reading, Refusal), (
                f"{construction.construction_id} under {filler.name}: "
                f"{instance!r} -> {reading}"
            )


def _match_arm_literals(path: Path, function: str) -> set[str]:
    """String literals appearing in *function*'s ``match`` case PATTERNS."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    literals: set[str] = set()
    for node in ast.walk(tree):
        if not (isinstance(node, ast.FunctionDef) and node.name == function):
            continue
        for stmt in ast.walk(node):
            if not isinstance(stmt, ast.Match):
                continue
            for case in stmt.cases:
                for pat in ast.walk(case.pattern):
                    if isinstance(pat, ast.MatchValue) and isinstance(pat.value, ast.Constant):
                        if isinstance(pat.value.value, str):
                            literals.add(pat.value.value)
    return literals


def test_declared_writer_axes_cover_the_inflection_arms() -> None:
    """STRUCTURAL GUARD. The sweep must not miss a tense or aspect.

    ``WRITER_TENSES`` / ``WRITER_ASPECTS`` are declared for readability, so they
    are pinned against the arms of ``_inflect_predicate``. A new aspect added to
    the writer without being added to the sweep would silently shrink the space
    this lane claims to measure.
    """
    literals = _match_arm_literals(_REPO / "generate" / "templates.py", "_inflect_predicate")
    declared = {v for v in (*WRITER_TENSES, *WRITER_ASPECTS) if v is not None}
    assert literals - declared == set(), f"undeclared inflection axis values: {literals - declared}"


def test_committed_corpus_matches_the_fillers_in_use() -> None:
    """STRUCTURAL GUARD. The reviewable corpus must be the one that ran.

    ``corpora.py`` holds the fillers as typed objects and ``public/v1/cases.jsonl``
    is what a reviewer reads. Two copies of one fact is how this codebase got two
    grammars; since the runner cannot import a JSON file as a dataclass without
    losing the typing, they stay separate and this guard keeps them identical.
    """
    path = _REPO / "evals" / "construction_inventory" / "public" / "v1" / "cases.jsonl"
    committed = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]

    in_use = [
        {
            "id": f"filler-{f.name.replace('_', '-')}",
            "kind": "count_filler" if f in COUNT_FILLERS else "mass_filler",
            "x": f.x, "y": f.y,
            "plural_x": f.plural_x, "plural_y": f.plural_y,
            "secondary": SECONDARY[f.name],
        }
        for f in (*COUNT_FILLERS, MASS_FILLER)
    ]
    assert [{k: v for k, v in row.items() if k != "note"} for row in committed] == in_use


def test_writer_emits_no_interrogative_construction() -> None:
    """STRUCTURAL GUARD. Three reader query templates are unreachable BY SHAPE.

    ``member_query`` and ``subset_query`` need a ``?``; no writer template
    contains one, so no amount of vocabulary work reaches them. Recording this
    as a shape fact keeps Phase 5 from trying to close that gap with corpora.
    """
    report = run_lane()
    writer_skeletons = {
        d["skeleton"] for d in report.case_details if d.get("kind") == "writer_construction"
    }
    assert not any("?" in sk for sk in writer_skeletons)

    interrogative = [c for c in READER_CONSTRUCTIONS if c.interrogative]
    assert len(interrogative) == 2
    for construction in interrogative:
        instance = render_instance(construction, COUNT_FILLERS[0])
        assert skeleton(instance) not in writer_skeletons
