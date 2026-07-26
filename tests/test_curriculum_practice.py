"""Phase C — the curriculum practice producer (ADR-0262 solver, ADR-0264 R9 sizing).

Four things are pinned here, in decreasing order of how quietly they would fail:

1. **The ledger is not committed, and a band would earn SERVE if it were.** The
   producer works; that is exactly why the artifact is a ratification. Pinned so
   the reasoning cannot be lost and re-derived wrongly later.
2. **`then` / `therefore` collide with the argument reader's grammar.** Two taught
   `philosophy_theology` lemmas are the reader's own control words, so 164 routable
   atoms refuse `compiled_premises_unreadable`. Coverage misses, never wrongs — but
   in the band Phase F retargets to.
3. **`committed == distinct` by construction**, not by discipline.
4. **wrong=0** over the capped corpus, per band.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chat.curriculum_surface import band_for, decide_curriculum_question
from core.ratified_ledger import CAPABILITY_LEDGERS, load_sealed_ledger
from core.reliability_gate import Action, Ceilings, license_for
from core.reliability_gate.evidence import audit_bands
from evals.curriculum_serve.practice.generator import (
    CASES_PER_BAND,
    DuplicateAtom,
    QueryAtom,
    all_gold_problems,
    assert_practice_atoms_distinct,
    band_cases,
    practice_bands,
    routable_atoms,
    taught_atoms,
)
from evals.curriculum_serve.practice.runner import (
    build_ledger,
    build_mix,
    build_sealed_artifact,
    run,
    seal_ledger,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
THETA_SERVE = 0.99

#: The 11 bands the ratified corpora populate, and each one's FULL routable atom
#: space. Pinned in both directions: a rise means new curriculum (welcome, update
#: deliberately), a fall means a band lost reachable questions.
#:
#: These supersede ADR-0264 §4.2's table, which sized bands from per-TERM
#: exclusivity. That bound is strictly tighter than the router's per-PAIR
#: predicate, so it under-counted — `systems_software_causal` reads as 630 there
#: and is really 720, which flips it from "cannot reach 657" to "can".
BAND_ATOM_SPACE: dict[str, int] = {
    "curriculum_mathematics_logic_contrast": 240,
    "curriculum_mathematics_logic_evidential": 240,
    "curriculum_mathematics_logic_modal": 480,
    "curriculum_mathematics_logic_sequence": 240,
    "curriculum_philosophy_theology_contrast": 22650,
    "curriculum_philosophy_theology_modal": 45300,
    "curriculum_physics_causal": 720,
    "curriculum_physics_modal": 480,
    "curriculum_systems_software_causal": 720,
    "curriculum_systems_software_modal": 480,
    "curriculum_systems_software_sequence": 240,
}

#: Bands whose space reaches the 657 a perfect record needs. Derived below, never
#: restated: these are the four that WOULD earn SERVE the moment a ledger is sealed.
_CAN_REACH_FLOOR = {
    band for band, space in BAND_ATOM_SPACE.items() if space >= 657
}

#: The reader-grammar collision, exact. Both lemmas are taught by
#: `philosophy_theology`'s packs AND are control words of the argument reader:
#: `therefore` is literally the conclusion marker `". Therefore <x>."`, and `then`
#: is the conditional consequent marker. An atom using either as a term compiles an
#: argument the reader cannot parse back.
RESERVED_WORD_LEMMAS = ("then", "therefore")


@pytest.fixture(scope="module")
def report() -> dict:
    return run()


@pytest.fixture(scope="module")
def ledger() -> dict:
    return build_ledger()


@pytest.fixture(scope="module")
def mix() -> dict:
    return build_mix()


@pytest.fixture(scope="module")
def problems() -> tuple:
    return all_gold_problems()


# ---------------------------------------------------------------------------
# 1. The artifact is uncommitted, and that is a decision with a reason.
# ---------------------------------------------------------------------------

def test_curriculum_ledger_is_not_committed() -> None:
    """Phase C builds the writer; committing the artifact is a ratification.

    The plan of record's exit criterion asked for a ledger that is "real
    (still-unearned)". That state is unreachable: every band with >=657 routable
    atoms clears theta_SERVE on correct NON-COMMITMENTS alone. So a committed
    ledger is necessarily an earning one, and this asserts nobody committed it as
    housekeeping.
    """
    path = CAPABILITY_LEDGERS["curriculum_serve"].path
    assert not path.exists(), (
        f"{path.name} exists. If that was deliberate ratification, update this "
        "test and ADR-0262 §5 together — a curriculum ledger licenses bands whose "
        "committed evidence is ~99% non-entailed."
    )
    assert CAPABILITY_LEDGERS["curriculum_serve"].missing_ok, (
        "an absent curriculum ledger must stay legitimately absent (serves disclosed)"
    )


def test_sealing_would_license_exactly_the_bands_that_reach_the_floor(
    ledger: dict,
) -> None:
    """The consequence of sealing, measured rather than asserted in prose.

    This is the finding Phase C exists to produce: the license is reachable today
    and it is reachable on the UNKNOWN class. If this ever reports a different set,
    the corpus moved and the ADR-0262 §5 discussion needs revisiting.
    """
    ceilings = Ceilings.default()
    licensed = {
        band
        for band, tally in ledger.items()
        if license_for(tally, Action.SERVE, ceilings).licensed
    }
    assert licensed == _CAN_REACH_FLOOR
    assert len(licensed) == 4


def test_a_licensed_band_is_licensed_on_non_commitments(report: dict) -> None:
    """The mix behind the license — the number `ClassTally` structurally cannot see.

    `ClassTally` carries correct/wrong/refused and no verdict axis, so a correct
    UNKNOWN counts exactly like a correct ENTAILED. Every band that would earn
    SERVE does so with an entailed share under 5%, which is what ADR-0262 §5.1
    rules unacceptable and what the open outcome-mix ruling has to settle.
    """
    for band in sorted(_CAN_REACH_FLOOR):
        entry = report["classes"][band]
        assert entry["serve_licensed"] is True
        assert entry["gold_mix"].get("entailed", 0) <= 9
        assert entry["entailed_share"] < 0.05, (
            f"{band}: entailed share {entry['entailed_share']:.4%} — if a band ever "
            "earns SERVE on a genuine mix, that is the ADR-0262 §5.1 bar being met "
            "and this pin should be revisited, not relaxed"
        )


def test_seal_ledger_writes_a_verifying_artifact(tmp_path: Path) -> None:
    """The writer `chat/curriculum_serve_license.py` names must actually work.

    Written to a tmp path, never to `chat/data/` — the point of the test is that
    the mechanism is real, not that the repository gains a ledger.
    """
    path = tmp_path / "curriculum_serve_ledger.json"
    artifact = seal_ledger(path)
    assert path.exists()
    assert artifact["provenance"] == "evals.curriculum_serve.practice.runner.seal_ledger"
    assert artifact["schema"] == "curriculum_serve_ledger_v1"
    # Round-trips through the same verifier the serving reader uses.
    tallies = load_sealed_ledger(path)
    assert set(tallies) == set(BAND_ATOM_SPACE)
    assert all(t.wrong == 0 for t in tallies.values())


def test_sealed_artifact_is_byte_identical_across_runs() -> None:
    """Determinism (ADR-0199 L-4): no clock, no RNG, so re-sealing must not move it.

    Two independent computations are the minimum that proves this and the maximum
    worth paying for — each is a full fold over the corpus.
    """
    first = build_sealed_artifact()
    second = build_sealed_artifact()
    assert json.dumps(first, indent=2, sort_keys=True) == json.dumps(
        second, indent=2, sort_keys=True
    )
    assert first["content_sha256"] == second["content_sha256"]


# ---------------------------------------------------------------------------
# 2. The reader-grammar collision — in the band Phase F retargets to.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("lemma", RESERVED_WORD_LEMMAS)
def test_reserved_reader_words_are_taught_curriculum_lemmas(lemma: str) -> None:
    """The precondition of the collision: these really are taught terms."""
    from teaching.curriculum_premises import load_curriculum

    assert lemma in load_curriculum("philosophy_theology").vocabulary


@pytest.mark.parametrize("lemma", RESERVED_WORD_LEMMAS)
def test_reserved_word_atoms_refuse_rather_than_answer(lemma: str) -> None:
    """A control word as a TERM refuses typed — it never answers wrongly.

    This is the honest failure: `compiled_premises_unreadable` is a coverage miss
    excluded from reliability's denominator (ADR-0175 §4), not a confabulation. The
    hazard is that the vocabulary boundary and the reader's grammar are not screened
    against each other, so a future pack teaching "and"/"or"/"if" would open a much
    larger hole silently. Recorded, not fixed — out of Phase C's scope
    (DIVISION-OF-WORK §6.5).
    """
    decision = decide_curriculum_question(f"Does knowledge requires {lemma}?")
    assert decision.verdict == "declined"
    assert decision.reason == "compiled_premises_unreadable"


def test_the_collision_is_bounded_to_two_lemmas() -> None:
    """Every refusal in the whole 69,666-atom space traces to `then`/`therefore`.

    Pinned as a bound, so the day a third reserved word enters the curriculum this
    fails instead of quietly enlarging the gap.
    """
    offenders: set[str] = set()
    checked = 0
    for domain, family in practice_bands():
        for atom in routable_atoms(domain, family):
            reserved = {atom.subject, atom.obj} & set(RESERVED_WORD_LEMMAS)
            if not reserved:
                continue
            checked += 1
            if decide_curriculum_question(atom.text).verdict == "declined":
                offenders |= reserved
    assert checked > 0, "no reserved-word atoms found — the sweep is not exercising anything"
    assert offenders == set(RESERVED_WORD_LEMMAS)


# ---------------------------------------------------------------------------
# 3. Distinct evidence, structurally.
# ---------------------------------------------------------------------------

def test_committed_equals_distinct_for_every_band(problems: tuple) -> None:
    """ADR-0264 R9 holds by construction: case identity IS the decision key."""
    by_band: dict[str, list] = {}
    for problem in problems:
        by_band.setdefault(problem.class_name, []).append(problem.payload.key)
    audits = audit_bands(by_band)
    assert audits
    for audit in audits:
        assert audit.committed == audit.distinct
        assert audit.inflation == 1.0
        assert audit.max_repeat == 1


def test_distinctness_guard_fails_under_mutation() -> None:
    """The R9 producer guard must be able to fail, or it is worthless.

    Same discipline as `tests/test_volume_honesty.py::test_audit_detects_padding`:
    a pin that cannot go red proves nothing. Feeds the guard a corpus with one
    atom repeated and asserts it refuses.
    """
    atom = QueryAtom("physics", "causal", "force", "causes", "acceleration")
    assert atom.key == ("physics", "force", "causes", "acceleration")

    import evals.curriculum_serve.practice.generator as gen

    original = gen.all_gold_problems
    from core.learning_arena.protocols import Problem

    def padded(cap: int = CASES_PER_BAND) -> tuple[Problem, ...]:
        return (
            Problem("a", "curriculum_physics_causal", atom),
            Problem("b", "curriculum_physics_causal", atom),
        )

    gen.all_gold_problems = padded  # type: ignore[assignment]
    try:
        with pytest.raises(DuplicateAtom, match="committed twice"):
            gen.assert_practice_atoms_distinct()
    finally:
        gen.all_gold_problems = original  # type: ignore[assignment]

    assert_practice_atoms_distinct()  # the real corpus still passes


# ---------------------------------------------------------------------------
# 4. The corpus itself: shape, determinism, wrong=0.
# ---------------------------------------------------------------------------

def test_band_atom_spaces_are_exactly_as_recorded() -> None:
    measured = {
        band_for(d, f): len(routable_atoms(d, f)) for d, f in practice_bands()
    }
    assert measured == BAND_ATOM_SPACE


def test_every_band_is_a_populated_family() -> None:
    """A family with no chains is not a band with zero volume — it is not a band."""
    from teaching.curriculum_premises import load_curriculum

    for domain, family in practice_bands():
        assert load_curriculum(domain).family(family)
    assert len(practice_bands()) == len(BAND_ATOM_SPACE)


def test_cap_selects_taught_edges_first() -> None:
    """Taught edges are the only committed-POSITIVE evidence; a sample that
    dropped them would report reliability while exercising no curriculum."""
    for domain, family in practice_bands():
        space = len(routable_atoms(domain, family))
        cases = band_cases(domain, family)
        assert len(cases) == min(space, CASES_PER_BAND)
        taught = taught_atoms(domain, family)
        assert taught <= {c.key for c in cases}, f"{domain}/{family} dropped a taught edge"


def test_corpus_is_deterministic(problems: tuple) -> None:
    assert [p.problem_id for p in all_gold_problems()] == [p.problem_id for p in problems]


def test_wrong_is_zero_for_every_band(report: dict) -> None:
    """The serving path and the independent oracle agree on every committed atom."""
    assert report["wrong_is_zero"] is True
    for band, entry in report["classes"].items():
        assert entry["wrong"] == 0, f"{band}: {entry}"
    assert set(report["classes"]) == set(BAND_ATOM_SPACE)


def test_gold_mix_has_no_refuted_class(report: dict) -> None:
    """No corpus row can express a negative yet (ADR-0264 R1-R4 unimplemented), so
    `refuted` is unreachable and the mix is entailed/unknown only. Pinned so the
    polarity unit has a red test to turn green."""
    for band, entry in report["classes"].items():
        assert "refuted" not in entry["gold_mix"], f"{band} produced refuted — polarity landed?"
        assert set(entry["gold_mix"]) <= {"entailed", "unknown", "declined"}


def test_mix_totals_reconcile_with_the_ledger(
    ledger: dict, report: dict, mix: dict
) -> None:
    """The mix is counted over the same corpus the ledger tallies, not a second one."""
    for band, tally in ledger.items():
        assert sum(mix[band].values()) == tally.attempted
        assert report["classes"][band]["committed"] == tally.committed
