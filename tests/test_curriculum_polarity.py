"""ADR-0264 R1-R4 + R8 — explicitly-taught curriculum negatives.

Before this, `polarity` was read by NOTHING. `CurriculumChain.sentence` was
unconditionally affirmative, so a row authored to REFUTE an atom compiled to a
premise asserting it, and the question came back `entailed`. The independent
oracle ignored the field too — so **gold agreed and `wrong=0` stayed green.**
That is the shape of defect no gate in this repository can catch, which is why
the epistemology was settled in an ADR before any code moved.

The five rules, and what each one is defending against:

- **R1** polarity is a ROW-LEVEL field; absent ⇒ affirmative. Not an `intent`
  value, not a new `operator_family`: bands key on the connective-derived family,
  so `modal_negative` would open a fresh band at n=0 instead of adding refuted
  volume to the band it belongs to.
- **R2** a negative row compiles under the sentential-negation prefix the argument
  reader already parses.
- **R3** a negative row MUST reuse the affirmative connective, so it mints the
  SAME propositional atom. A negated paraphrase mints a different atom and the
  query returns UNKNOWN — a taught refutation that silently fails to refute.
- **R4** one atom cannot hold both polarities; the contradiction is rejected at
  ratification, not discovered at serve time as a band that stopped answering.
- **R8** the oracle learns polarity INDEPENDENTLY (its own constants, its own
  reader) and excludes negatives from the reachability adjacency.

The end-to-end tests write a temporary row into the committed corpus and restore
it, asserting **byte-identity** on the way out. No negative row is committed:
authoring curriculum is Phase F and Shay's.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterator

import pytest

from chat.curriculum_surface import decide_curriculum_question
from evals.curriculum_serve.oracle import oracle_answer, taught_edges
from generate.proof_chain.entail import Entailment, evaluate_entailment_with_trace
from generate.proof_chain.verb import VerbArgument, read_verb_argument
from teaching.curriculum_premises import (
    AFFIRMATIVE,
    NEGATION_PREFIX,
    NEGATIVE,
    POLARITIES,
    CurriculumChain,
    compile_premises,
    load_curriculum,
)
from teaching.ratification import (
    ChainRecord,
    RatificationError,
    build_chain_record,
    validate_admissible,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
_PHYSICS_CORPUS = REPO_ROOT / "teaching" / "domain_chains" / "physics_chains_v1.jsonl"

#: An atom physics does NOT teach, in taught vocabulary, so it routes and is
#: UNKNOWN today — the clean slot to plant a negative in.
_UNTAUGHT_ATOM = ("mass", "causes", "charge")


def _chain(polarity: str = AFFIRMATIVE) -> CurriculumChain:
    return CurriculumChain(
        chain_id="x-causal-001",
        subject="force",
        connective="causes",
        obj="acceleration",
        family="causal",
        polarity=polarity,
    )


# ---------------------------------------------------------------------------
# R1 — the field, and its default.
# ---------------------------------------------------------------------------

def test_r1_polarity_defaults_to_affirmative() -> None:
    """An absent field must read as affirmative, or every committed row changes
    meaning the moment the field exists."""
    bare = CurriculumChain("i", "force", "causes", "acceleration", "causal")
    assert bare.polarity == AFFIRMATIVE
    assert bare.negated is False
    assert bare.sentence == "force causes acceleration"


def test_r1_committed_corpora_carry_no_polarity_field_and_still_load() -> None:
    """The migration is a no-op on disk: nothing was rewritten."""
    rows = [
        json.loads(line)
        for line in _PHYSICS_CORPUS.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert rows
    assert not any("polarity" in row for row in rows), (
        "no committed row should carry polarity yet — Phase F authors those"
    )
    for chain in load_curriculum("physics").chains:
        assert chain.polarity == AFFIRMATIVE


def test_r1_unrecognized_polarity_is_dropped_not_guessed() -> None:
    """Reading an unknown token as affirmative would turn a row someone wrote to
    refute into a row that asserts — the one direction of error that matters."""
    assert set(POLARITIES) == {AFFIRMATIVE, NEGATIVE}
    with pytest.raises(RatificationError, match="polarity"):
        build_chain_record(
            domain="physics", subject="mass", connective="causes", obj="charge",
            reviewer="t", rationale="t", polarity="maybe",
        )


def test_r1_polarity_is_not_a_new_operator_family() -> None:
    """Bands key on the connective-derived family; a negative row keeps its band."""
    from chat.curriculum_surface import band_for

    neg = _chain(NEGATIVE)
    assert neg.family == "causal"
    assert band_for("physics", neg.family) == "curriculum_physics_causal"


# ---------------------------------------------------------------------------
# R2 — the compiled form, and that the reader accepts it.
# ---------------------------------------------------------------------------

def test_r2_negative_row_compiles_under_the_negation_prefix() -> None:
    neg = _chain(NEGATIVE)
    assert neg.sentence == f"{NEGATION_PREFIX}force causes acceleration"
    assert neg.negated is True


def test_r2_the_reader_actually_parses_that_form() -> None:
    """The prefix is not decorative — the verb band must read it as a negation
    of the atom, or R2 compiles premises nothing can decide."""
    argument = f"{_chain(NEGATIVE).sentence}. Therefore force causes acceleration."
    arg = read_verb_argument(argument)
    assert isinstance(arg, VerbArgument), f"reader refused: {arg}"
    trace = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula)
    assert trace.outcome is Entailment.REFUTED
    assert trace.reason == "tautological_refutation"


def test_r2_affirmative_control_still_entails() -> None:
    argument = f"{_chain().sentence}. Therefore force causes acceleration."
    arg = read_verb_argument(argument)
    assert isinstance(arg, VerbArgument)
    trace = evaluate_entailment_with_trace(arg.premise_formulas, arg.query_formula)
    assert trace.outcome is Entailment.ENTAILED


# ---------------------------------------------------------------------------
# R3 — the same atom. This is the silent-failure rule.
# ---------------------------------------------------------------------------

def test_r3_negative_reuses_the_affirmative_atom() -> None:
    """`atom_sentence` is polarity-independent — that IS R3."""
    assert _chain().atom_sentence == _chain(NEGATIVE).atom_sentence
    assert _chain(NEGATIVE).sentence.endswith(_chain(NEGATIVE).atom_sentence)


def test_r3_a_different_connective_would_silently_fail_to_refute() -> None:
    """Why R3 is a rule and not a style note.

    A negative row spelled with a DIFFERENT relation word mints a different
    propositional atom, so it cannot contradict the query. The result is UNKNOWN
    — the curriculum was taught a refutation and answers "I don't know". Nothing
    goes red. This is the mechanism, demonstrated.
    """
    same_atom = f"{NEGATION_PREFIX}force causes acceleration. Therefore force causes acceleration."
    other_atom = f"{NEGATION_PREFIX}force enables acceleration. Therefore force causes acceleration."

    a = read_verb_argument(same_atom)
    b = read_verb_argument(other_atom)
    assert isinstance(a, VerbArgument) and isinstance(b, VerbArgument)
    assert evaluate_entailment_with_trace(a.premise_formulas, a.query_formula).outcome is Entailment.REFUTED
    assert evaluate_entailment_with_trace(b.premise_formulas, b.query_formula).outcome is Entailment.UNKNOWN, (
        "a negated paraphrase must be shown NOT to refute — that is the hazard R3 forbids"
    )


def test_r3_ratification_refuses_a_connective_outside_the_closed_set() -> None:
    with pytest.raises(RatificationError, match="ADR-0264 R3"):
        build_chain_record(
            domain="physics", subject="mass", connective="does not cause",
            obj="charge", reviewer="t", rationale="t", polarity=NEGATIVE,
        )


# ---------------------------------------------------------------------------
# R4 — contradiction rejected at ratification.
# ---------------------------------------------------------------------------

def _record(polarity: str, subject: str = "force", obj: str = "acceleration") -> ChainRecord:
    return ChainRecord(
        chain_id="physics-causal-900", domain="physics", operator_family="causal",
        subject=subject, intent="cause", connective="causes", object=obj,
        subject_pack_id="en_physics_v1", object_pack_id="en_physics_v1",
        review_status="reviewed", provenance="test", polarity=polarity,
    )


def test_r4_negating_an_already_taught_atom_is_rejected() -> None:
    """physics-causal-001 teaches `force causes acceleration` affirmatively."""
    with pytest.raises(RatificationError, match="contradiction"):
        validate_admissible(_record(NEGATIVE))


def test_r4_the_refusal_names_both_polarities_and_the_consequence() -> None:
    with pytest.raises(RatificationError) as exc:
        validate_admissible(_record(NEGATIVE))
    message = str(exc.value)
    assert AFFIRMATIVE in message and NEGATIVE in message
    assert "ADR-0264 R4" in message
    assert "inconsistent" in message


def test_r4_same_polarity_duplicate_is_still_a_duplicate_not_a_contradiction() -> None:
    """The two failures are different and must stay distinguishable."""
    with pytest.raises(RatificationError, match="duplicate edge"):
        validate_admissible(_record(AFFIRMATIVE))


def test_r4_an_untaught_atom_admits_either_polarity() -> None:
    """R4 forbids contradiction, not negatives."""
    subject, _connective, obj = _UNTAUGHT_ATOM
    validate_admissible(_record(NEGATIVE, subject=subject, obj=obj))
    validate_admissible(_record(AFFIRMATIVE, subject=subject, obj=obj))


# ---------------------------------------------------------------------------
# R8 — the oracle, independently.
# ---------------------------------------------------------------------------

def test_r8_oracle_does_not_import_the_compiler_s_polarity_vocabulary() -> None:
    """Code-level independence is the whole evidentiary value.

    If the oracle imported the compiler's polarity constants or helper, agreement
    would only prove the compiler agrees with itself and a polarity bug would be
    invisible on both sides at once.
    """
    import inspect

    import evals.curriculum_serve.oracle as oracle

    source = inspect.getsource(oracle)
    assert "from teaching.curriculum_premises import" not in source
    assert "teaching.curriculum_premises" not in source
    # It has its own constants.
    assert oracle._AFFIRMATIVE == "affirmative"
    assert oracle._NEGATIVE == "negative"


def test_r8_taught_edges_exposes_polarity() -> None:
    edges = taught_edges("physics")
    assert edges
    for _s, _c, _o, _id, polarity in edges:
        assert polarity == AFFIRMATIVE


# ---------------------------------------------------------------------------
# End to end, against a temporary corpus row. Restored byte-identically.
# ---------------------------------------------------------------------------

def _plant(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, *, polarity: str, chain_id: str
) -> tuple[str, str, str]:
    """Repoint BOTH loaders at a temp corpus carrying one extra row.

    The committed corpus is never written. An earlier version of this fixture
    appended to `teaching/domain_chains/physics_chains_v1.jsonl` and restored it;
    that is safe under `smoke`/`deductive` (serial) but NOT under `full`, which
    injects `-n auto` — a parallel worker reading the corpus mid-mutation would
    see a row that is not committed, and the failure would look like a corpus
    problem rather than a test-isolation one.

    Each loader is still redirected SEPARATELY, at its own module constant, and
    each still parses with its own code. Only the corpus LOCATION is shared; the
    ADR-0264 R8 independence being tested is untouched.
    """
    import evals.curriculum_serve.oracle as oracle
    import teaching.curriculum_premises as premises

    subject, connective, obj = _UNTAUGHT_ATOM
    row = {
        "chain_id": chain_id,
        "domain": "physics",
        "operator_family": "causal",
        "subject": subject,
        "intent": "cause",
        "connective": connective,
        "object": obj,
        "subject_pack_id": "en_physics_v1",
        "object_pack_id": "en_physics_v1",
        "review_status": "reviewed",
        "provenance": "test:polarity",
    }
    if polarity != AFFIRMATIVE:
        row["polarity"] = polarity

    chain_dir = tmp_path / "teaching" / "domain_chains"
    chain_dir.mkdir(parents=True)
    for src in (REPO_ROOT / "teaching" / "domain_chains").glob("*.jsonl"):
        text = src.read_text(encoding="utf-8")
        if not text.endswith("\n"):
            text += "\n"
        if src.name == _PHYSICS_CORPUS.name:
            text += json.dumps(row, separators=(",", ":")) + "\n"
        (chain_dir / src.name).write_text(text, encoding="utf-8")
    # The compiler resolves corpora AND packs from its repo root, so the temp
    # tree needs the real packs visible under the same name.
    (tmp_path / "packs").symlink_to(REPO_ROOT / "packs")

    monkeypatch.setattr(premises, "_REPO_ROOT", tmp_path)
    monkeypatch.setattr(oracle, "_CHAIN_DIR", chain_dir)
    premises.load_curriculum.cache_clear()
    premises._pack_lemmas.cache_clear()
    monkeypatch.setattr(
        premises.load_curriculum, "cache_clear", premises.load_curriculum.cache_clear
    )
    return subject, connective, obj


@pytest.fixture
def negative_row(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Iterator[tuple[str, str, str]]:
    """A TAUGHT NEGATIVE for an atom physics does not otherwise teach."""
    atom = _plant(monkeypatch, tmp_path, polarity=NEGATIVE, chain_id="physics-causal-999")
    yield atom
    load_curriculum.cache_clear()


def test_e2e_a_taught_negative_serves_refuted(negative_row: tuple[str, str, str]) -> None:
    """The whole point: `polarity` now changes the answer.

    Before this unit the same row served a confident `entailed` — a taught
    refutation answering "yes".
    """
    subject, connective, obj = negative_row
    decision = decide_curriculum_question(f"Does {subject} {connective} {obj}?")
    assert decision.verdict == "refuted", decision
    assert decision.band == "curriculum_physics_causal"


def test_e2e_the_independent_oracle_agrees(negative_row: tuple[str, str, str]) -> None:
    """Two independently-written procedures must reach the same verdict, or the
    lane's `wrong=0` is measuring agreement with itself."""
    subject, connective, obj = negative_row
    gold = oracle_answer("physics", subject, connective, obj)
    served = decide_curriculum_question(f"Does {subject} {connective} {obj}?")
    assert gold.verdict == "refuted"
    assert gold.depth == 1, "a taught negative is a depth-1 statement, not a composition"
    assert served.verdict == gold.verdict


def test_e2e_the_negative_premise_is_actually_compiled(
    negative_row: tuple[str, str, str],
) -> None:
    subject, connective, obj = negative_row
    curriculum = load_curriculum("physics")
    premises, chain_ids = compile_premises(
        curriculum, "causal", query=(subject, connective, obj)
    )
    assert "physics-causal-999" in chain_ids
    assert any(p.startswith(NEGATION_PREFIX) for p in premises), premises


def test_e2e_the_atom_was_unknown_before_the_negative_row() -> None:
    """Without the fixture the same question is UNKNOWN — so the test above is
    measuring the row, not a pre-existing verdict."""
    subject, connective, obj = _UNTAUGHT_ATOM
    load_curriculum.cache_clear()
    decision = decide_curriculum_question(f"Does {subject} {connective} {obj}?")
    assert decision.verdict == "unknown", decision
    assert oracle_answer("physics", subject, connective, obj).verdict == "unknown"


def test_e2e_negatives_are_excluded_from_reachability(
    negative_row: tuple[str, str, str],
) -> None:
    """R8 — a denial supplies no step, demonstrated on a path it would complete.

    The fixture plants `mass does not cause charge`, and physics already teaches
    `charge causes field` (physics-causal-004). So if negatives entered the
    adjacency, `(mass, causes, field)` would report a 2-hop path built out of a
    DENIAL. `mass` has no other outgoing causal edge, so depth must stay 0.

    Constructed this way on purpose: the assertion distinguishes the correct
    behaviour from the specific wrong one, rather than merely observing UNKNOWN
    (which both would produce).
    """
    subject, _connective, obj = negative_row
    assert (obj, "causes", "field") in {
        (c.subject, c.connective, c.obj) for c in load_curriculum("physics").family("causal")
    }, "fixture premise moved: physics must still teach `charge causes field`"

    verdict = oracle_answer("physics", subject, "causes", "field")
    assert verdict.verdict == "unknown"
    assert verdict.depth == 0, (
        f"reachability composed a {verdict.depth}-hop path through a denial "
        f"({subject} -/-> {obj} -> field) — ADR-0264 R8 excludes negatives from "
        "the adjacency precisely so this cannot happen"
    )


def test_e2e_an_affirmative_row_in_the_same_slot_WOULD_create_that_path(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """The control for the test above: the path is real when the row is positive.

    Without this, `depth == 0` could just mean the oracle never finds 2-hop paths
    at all, and the R8 assertion would be vacuous. Same slot, same terms, only the
    polarity differs — so the two tests isolate polarity and nothing else.
    """
    subject, _connective, _obj = _plant(
        monkeypatch, tmp_path, polarity=AFFIRMATIVE, chain_id="physics-causal-998"
    )
    verdict = oracle_answer("physics", subject, "causes", "field")
    assert verdict.verdict == "unknown", "a 2-hop path must not be ENTAILED"
    assert verdict.depth == 2, (
        f"expected the affirmative row to open a 2-hop path, got {verdict}"
    )
    load_curriculum.cache_clear()
