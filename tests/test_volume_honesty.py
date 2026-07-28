"""The volume-honesty invariant — practice volume must be distinct evidence.

ADR-0264 R9. `conservative_floor` is a one-sided Wilson lower bound, and Wilson
assumes independent trials. CORE's pipeline is deterministic, so replaying an
identical case is not a second trial — it is the same trial with a guaranteed
outcome. A ledger's ``committed`` count is therefore an upper bound on its
evidence, and the honest figure is its distinct-decision count.

This file is the specification of that invariant, written before the curriculum
practice producer exists (Phase C). It is also the audit instrument, because the
exposure S6 predicted in the abstract
(`docs/research/curriculum-volume-quantification-2026-07-24.md` §1) turned out to
be live and measurable in the deduction ledger — see
:data:`DEDUCTION_DISTINCT_EVIDENCE` and
`docs/research/distinct-evidence-audit-2026-07-25.md`.

Three producers back the three entries in `core.ratified_ledger.CAPABILITY_LEDGERS`:

- **estimation** (ADR-0175) — clean. 660 committed, 660 distinct, inflation 1.0.
  ``CASES_PER_CLASS = 660`` was evidently chosen just above the 657 a perfect
  record needs, on distinct cases. This is the standard the other producers are
  measured against, and it is why the deduction finding is a regression from an
  established practice rather than a gap nobody had thought about.
- **deduction_serve** (ADR-0256) — 21 of 25 bands did not clear θ_SERVE on
  distinct evidence; the worst three inflated 28 distinct cases to 720 committed.
  For three days this was recorded, pinned, and deliberately NOT repaired, because
  the ledger is SHA-sealed, ratified, and gates a live flag — changing it was Shay's
  ratification, not a test's. **That ratification is R-13 (2026-07-28), and it has
  been applied:** the ledger is re-sealed on distinct evidence, the 21 are demoted
  and decide with disclosure, four hold earned licences, and the producer now
  REFUSES to seal a padded ledger at all. The audit below no longer measures an
  exposure; it pins the repair.
- **curriculum_serve** (ADR-0262/0264) — clean, and clean *structurally*: the
  producer's case identity IS the query atom, so ``committed == distinct`` cannot
  drift apart the way it did for deduction, where case identity was a quota index.
  Its ledger is deliberately uncommitted — see
  ``evals/curriculum_serve/practice/runner.py``.

Deliberately narrow. This pins evidence *distinctness*. It does not pin outcome
mix — whether each verdict class needs its own volume is an open ruling recorded
in the research note, and imposing it here would retroactively fail all 25
deduction bands on a criterion no ADR has ratified.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Hashable
from pathlib import Path

import pytest

from core.ratified_ledger import CAPABILITY_LEDGERS
from core.reliability_gate import conservative_floor
from core.reliability_gate.evidence import (
    SERVE_VOLUME_AT_THETA_099,
    EvidenceAudit,
    audit_band,
    audit_bands,
    below_floor,
    format_report,
    volume_for_theta,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

#: θ the sealed-practice ledgers are gated at (both ledger notes state it).
THETA_SERVE = 0.99


# ---------------------------------------------------------------------------
# Audit sources, one per licensed-ledger capability.
#
# Keyed by the SAME capability names as `CAPABILITY_LEDGERS` and checked against
# it below, so a new capability cannot be added to the manifest without either an
# audit source or an explicit declaration that its producer does not exist yet.
# A hand-copied list here would fall behind the manifest exactly the way the
# workbench grounding whitelist fell behind `GROUNDING_SOURCES`.
# ---------------------------------------------------------------------------

def _deduction_keys() -> dict[str, list[Hashable]]:
    """Decision keys per band for the deduction practice corpus.

    The key is the case TEXT. Two cases with identical text are indisputably the
    same decision, so text-identity *under*-reports inflation (a tighter key —
    the normalized atom tuple — would collapse spelling variants and report
    more). Under-reporting is the correct direction: the measured gap is a floor
    on the real gap.
    """
    from evals.deduction_serve.practice.gold import all_gold_problems

    out: dict[str, list[Hashable]] = {}
    for problem in all_gold_problems():
        out.setdefault(problem.class_name, []).append(problem.payload["text"])
    return out


def _estimation_keys() -> dict[str, list[Hashable]]:
    from evals.determination_estimation import all_gold_problems

    out: dict[str, list[Hashable]] = {}
    for problem in all_gold_problems():
        payload = problem.payload
        key = repr(sorted(payload.items())) if isinstance(payload, dict) else repr(payload)
        out.setdefault(problem.class_name, []).append(key)
    return out


def _curriculum_keys() -> dict[str, list[Hashable]]:
    """Decision keys per band for the curriculum practice corpus (Phase C).

    The key is the query ATOM, which is also the producer's case identity — so
    this audit can only ever report inflation 1.0 while the producer is correct,
    and reports the real figure the moment it is not. Contrast the deduction
    source above, where the key had to be recovered from case text because the
    producer's identity was a quota index.
    """
    from evals.curriculum_serve.practice import all_gold_problems

    out: dict[str, list[Hashable]] = {}
    for problem in all_gold_problems():
        out.setdefault(problem.class_name, []).append(problem.payload.key)
    return out


def _curriculum_entailed_keys() -> dict[str, list[Hashable]]:
    """Decision keys for the ENTAILED half of the curriculum corpus (R-8, ruled C).

    R-8 split the curriculum earning basis: committing to an entailment and
    correctly declining to commit are different capabilities, licensed on different
    evidence. This is the audit source for the committing half — the query atoms
    whose oracle verdict is ``entailed``.

    It exists so the split cannot be declared in the manifest and left unmeasured.
    The numbers it reports are small on purpose: 3-9 per band, against the 657 that
    theta_SERVE=0.99 requires. That gap IS the finding.
    """
    from evals.curriculum_serve.practice import all_gold_problems
    from evals.curriculum_serve.practice.generator import CurriculumOracleTether

    tether = CurriculumOracleTether()
    out: dict[str, list[Hashable]] = {}
    for problem in all_gold_problems():
        if tether.gold_answer(problem) == "entailed":
            out.setdefault(problem.class_name, []).append(problem.payload.key)
    return out


#: capability -> keys provider, or ``None`` when the producer is not built.
#: ``None`` is a declaration, not an omission: :func:`test_every_licensed_capability_has_an_audit_source`
#: accepts it only while the capability's ledger is genuinely absent.
AUDIT_SOURCES: dict[str, Callable[[], dict[str, list[Hashable]]] | None] = {
    "estimation": _estimation_keys,
    "deduction_serve": _deduction_keys,
    "curriculum_serve": _curriculum_keys,
    "curriculum_serve_entailed": _curriculum_entailed_keys,
}


#: Distinct-evidence counts per band. Measured 2026-07-25 at main @ `6ada6f7a`,
#: when every band was 720 committed and this was an EXPOSURE INVENTORY: 21 of 25
#: did not clear θ_SERVE=0.99 on the evidence below.
#:
#: **APPLIED 2026-07-28 (R-13).** It is no longer an exposure. The sealed ledger is
#: re-counted on exactly these numbers — committed == distinct — so the 21 are
#: demoted and decide with disclosure, and four hold earned licences. This list is
#: now the *expected* shape of the ledger rather than a measurement of a gap, and
#: `test_deduction_sealed_ledger_matches_the_producer_it_names` pins that equality.
DEDUCTION_DISTINCT_EVIDENCE: dict[str, int] = {
    "atomic": 98,
    "categorical": 294,
    "conditional_chain": 294,
    "conditional_single": 294,
    "disjunctive": 294,
    "en_atomic": 474,
    "en_conditional_chain": 720,
    "en_conditional_single": 474,
    "en_condmem_chain": 52,
    "en_condmem_conditional": 60,
    "en_condmem_disjunctive": 28,
    "en_condmem_fused": 60,
    "en_disjunctive": 720,
    "en_exist_chain": 28,
    "en_exist_negative": 28,
    "en_exist_universal": 46,
    "en_exist_witness": 35,
    "en_member_atomic": 60,
    "en_member_chain": 52,
    "en_member_negative": 52,
    "en_member_single": 60,
    "en_verb_chain": 308,
    "en_verb_fact": 660,
    "en_verb_negative": 308,
    "en_verb_universal": 660,
}

#: The four that DO clear on distinct evidence. Derived below, not restated.
_EXPECTED_CLEAN = {"en_conditional_chain", "en_disjunctive", "en_verb_fact", "en_verb_universal"}


@pytest.fixture(scope="module")
def deduction_audits() -> tuple[EvidenceAudit, ...]:
    return audit_bands(_deduction_keys())


@pytest.fixture(scope="module")
def estimation_audits() -> tuple[EvidenceAudit, ...]:
    return audit_bands(_estimation_keys())


# ---------------------------------------------------------------------------
# 1. The instrument itself must be correct, and must fail under mutation.
# ---------------------------------------------------------------------------

def test_serve_volume_is_derived_from_the_pinned_floor() -> None:
    """657 must be computed, never trusted as a literal.

    If `WILSON_Z` ever moves, a hard-coded 657 becomes silently wrong in every
    doc and test that repeats it. This asserts the derivation and the boundary.
    """
    assert volume_for_theta(THETA_SERVE) == SERVE_VOLUME_AT_THETA_099 == 657
    n = SERVE_VOLUME_AT_THETA_099
    assert conservative_floor(n, n) >= THETA_SERVE
    assert conservative_floor(n - 1, n - 1) < THETA_SERVE, (
        "657 must be the SMALLEST perfect-record volume clearing theta"
    )


def test_audit_detects_padding() -> None:
    """The mutation check. Pad a corpus and the instrument must catch it.

    Both corpora below commit exactly 720 cases with a perfect record, so
    `conservative_floor` returns the *same passing number* for each and the gate
    as it stands cannot tell them apart. One exercised 720 decisions; the other
    exercised 28. That gap is the whole point.
    """
    honest = audit_band("honest", [f"case-{i}" for i in range(720)])
    padded = audit_band("padded", [f"case-{i % 28}" for i in range(720)])

    assert honest.committed == padded.committed == 720
    assert honest.claimed == padded.claimed >= THETA_SERVE, (
        "the existing gate must be shown to see these as identical"
    )

    assert honest.distinct == 720
    assert honest.inflation == 1.0
    assert honest.max_repeat == 1
    assert honest.clears(THETA_SERVE)

    assert padded.distinct == 28
    assert padded.inflation > 25
    assert padded.max_repeat > 25
    assert not padded.clears(THETA_SERVE)
    assert padded.honest < 0.81


def test_a_single_repeat_is_enough_to_move_the_honest_floor() -> None:
    """No dead zone: one duplicate in an otherwise-exact-threshold corpus drops it."""
    exact = audit_band("exact", [f"c-{i}" for i in range(657)])
    assert exact.clears(THETA_SERVE)
    # Replace one distinct case with a duplicate: same committed, 656 distinct.
    padded = audit_band("padded", [f"c-{i}" for i in range(656)] + ["c-0"])
    assert padded.committed == 657
    assert padded.distinct == 656
    assert not padded.clears(THETA_SERVE)


def test_tighter_keys_can_only_report_more_inflation() -> None:
    """Key choice is safe in one direction only, and that is the direction used.

    A coarser key (case text) merges fewer cases than a finer one (normalized
    atom). So an audit over text is a lower bound on the audit over atoms, and a
    finding built on it cannot be an exaggeration.
    """
    coarse = ["Does a require b?", "Does a requires b?", "Does c require d?"]
    fine = ["(a,requires,b)", "(a,requires,b)", "(c,requires,d)"]
    assert audit_band("coarse", coarse).inflation <= audit_band("fine", fine).inflation


def test_audit_rejects_impossible_counts() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        EvidenceAudit(band="b", committed=5, distinct=6, max_repeat=1)
    with pytest.raises(ValueError, match="no distinct keys"):
        EvidenceAudit(band="b", committed=5, distinct=0, max_repeat=0)


# ---------------------------------------------------------------------------
# 2. Every licensed capability must be audited — the anti-silence guard.
# ---------------------------------------------------------------------------

def test_every_licensed_capability_has_an_audit_source() -> None:
    """Derived from `CAPABILITY_LEDGERS`, so a new capability cannot slip past.

    This was the forcing function for Phase C, and it worked: a ``None`` audit
    source stops being an honest declaration the moment the capability's ledger
    exists. All three producers now carry one, so the guard is holding the line
    for the NEXT capability rather than for curriculum.
    """
    assert set(AUDIT_SOURCES) == set(CAPABILITY_LEDGERS), (
        "AUDIT_SOURCES and CAPABILITY_LEDGERS disagree — a licensed capability is "
        "unaudited, or an audit source names a capability that is not licensed"
    )
    for capability, source in sorted(AUDIT_SOURCES.items()):
        if source is not None:
            continue
        ledger_path = CAPABILITY_LEDGERS[capability].path
        assert not ledger_path.exists(), (
            f"{capability}: ledger {ledger_path.name} now exists but has no audit "
            f"source. Register one in AUDIT_SOURCES — a sealed ledger whose "
            f"distinct evidence is unmeasured is exactly the ADR-0264 R9 exposure."
        )


@pytest.mark.parametrize("capability", sorted(c for c, s in AUDIT_SOURCES.items() if s))
def test_audited_capability_bands_are_non_degenerate(capability: str) -> None:
    """Whatever a producer emits, it must be auditable and non-empty."""
    audits = audit_bands(AUDIT_SOURCES[capability]())  # type: ignore[misc]
    assert audits, f"{capability}: producer yielded no bands"
    for audit in audits:
        assert audit.committed > 0
        assert audit.distinct > 0
        assert audit.inflation >= 1.0


# ---------------------------------------------------------------------------
# 3. The estimation producer — the clean standard the invariant is calibrated to.
# ---------------------------------------------------------------------------

def test_estimation_producer_has_no_inflation(
    estimation_audits: tuple[EvidenceAudit, ...],
) -> None:
    """ADR-0175's producer commits distinct cases only, just above the threshold.

    Recorded as a test because it is the existence proof that the invariant is
    satisfiable and was in fact satisfied before ADR-0256's producer: 660
    distinct cases against the 657 a perfect record needs.
    """
    assert [a.band for a in estimation_audits] == [
        "converse:parent_of",
        "converse:sibling_of",
    ]
    for audit in estimation_audits:
        assert audit.committed == audit.distinct == 660, format_report(
            estimation_audits, THETA_SERVE
        )
        assert audit.max_repeat == 1
        assert audit.clears(THETA_SERVE)
    assert below_floor(estimation_audits, THETA_SERVE) == ()


# ---------------------------------------------------------------------------
# 3b. The curriculum producer — clean, and clean by construction (Phase C).
# ---------------------------------------------------------------------------

def test_curriculum_producer_has_no_inflation() -> None:
    """The second producer that satisfies the invariant, and the first that
    satisfies it STRUCTURALLY.

    Its case identity is the query atom, so ``committed == distinct`` is not a
    property the generator has to maintain — it is the same fact twice. Pinned here
    beside the estimation standard because this file is where a reader looks to ask
    "which producers are honest about volume?".
    """
    audits = audit_bands(_curriculum_keys())
    assert audits, "curriculum producer yielded no bands"
    assert len(audits) == 11, f"expected 11 populated bands, found {len(audits)}"
    for audit in audits:
        assert audit.committed == audit.distinct, format_report(audits, THETA_SERVE)
        assert audit.inflation == 1.0
        assert audit.max_repeat == 1
    assert {a.band for a in below_floor(audits, THETA_SERVE)} == {
        a.band for a in audits if a.distinct < SERVE_VOLUME_AT_THETA_099
    }, "a band below the floor must be below it for lack of VOLUME, never inflation"


# ---------------------------------------------------------------------------
# 4. The deduction producer — the measured exposure, pinned in both directions.
# ---------------------------------------------------------------------------

def test_deduction_distinct_evidence_matches_the_recorded_exposure(
    deduction_audits: tuple[EvidenceAudit, ...],
) -> None:
    """Pins the exact inventory, so the exposure can neither grow nor drift.

    Fails if a band's distinct count changes in EITHER direction. A drop is the
    exposure worsening. A rise means someone improved a band — welcome, and the
    inventory must then be updated deliberately rather than by a silently
    loosening test.
    """
    measured = {a.band: a.distinct for a in deduction_audits}
    assert measured == DEDUCTION_DISTINCT_EVIDENCE, format_report(
        deduction_audits, THETA_SERVE
    )
    for audit in deduction_audits:
        assert audit.committed == 720, "CASES_PER_BAND changed — re-audit the ledger"


def test_deduction_exposure_membership_is_exactly_as_recorded(
    deduction_audits: tuple[EvidenceAudit, ...],
) -> None:
    """Which bands fail is derived from the floor, not restated alongside it."""
    failing = {a.band for a in below_floor(deduction_audits, THETA_SERVE)}
    clean = {a.band for a in deduction_audits} - failing
    assert clean == _EXPECTED_CLEAN, format_report(deduction_audits, THETA_SERVE)
    assert len(failing) == 21, (
        f"expected 21 bands below the distinct-evidence floor, found {len(failing)}"
    )


def test_deduction_sealed_ledger_matches_the_producer_it_names(
    deduction_audits: tuple[EvidenceAudit, ...],
) -> None:
    """The exposure is in the shipped artifact, not only in the generator.

    Without this the finding could be dismissed as being about a generator that
    the sealed ledger does not reflect. The ledger's committed counts are the
    producer's committed counts, band for band.
    """
    path = CAPABILITY_LEDGERS["deduction_serve"].path
    ledger = json.loads(path.read_text(encoding="utf-8"))
    classes = ledger["classes"]
    assert ledger["provenance"] == "evals.deduction_serve.practice.runner.seal_ledger"
    # R-13 (2026-07-28): the sealed ledger now counts DISTINCT evidence, so this
    # invariant is strictly stronger than it was. Before the re-count it compared the
    # sealed committed counts to the producer's committed counts and both were the
    # inflated 720 — the assertion held perfectly while the number it agreed on was
    # the wrong number. Two records agreeing is not evidence that either is right.
    # It now pins what the re-count actually guarantees: committed == distinct.
    produced_distinct = {a.band: a.distinct for a in deduction_audits}
    produced_raw = {a.band: a.committed for a in deduction_audits}
    sealed = {name: tally["correct"] + tally["wrong"] for name, tally in classes.items()}
    assert sealed == produced_distinct, (
        "sealed ledger committed counts diverge from the producer's DISTINCT counts "
        "— either the seal is stale, or build_ledger stopped folding the "
        "de-duplicated corpus and replays are being counted as evidence again"
    )
    inflated = sorted(b for b in sealed if produced_raw[b] != produced_distinct[b])
    assert inflated, (
        "no band shows any raw-vs-distinct gap, so this assertion proves nothing "
        "about de-duplication. Either the corpus lost its replays, or the audit has "
        "gone blind — check before assuming the good news."
    )
    assert all(tally["wrong"] == 0 for tally in classes.values()), "wrong=0 must hold"


def test_recorded_exposure_is_declared_in_a_decision_record() -> None:
    """A pinned exposure with no decision record behind it is just a stale test.

    Ties this file to the ADR that rules on it, so the inventory above cannot
    outlive the reasoning that justified leaving it in place.
    """
    adr = REPO_ROOT / "docs" / "adr" / "ADR-0264-negative-curriculum-and-premise-scope.md"
    assert adr.exists(), "ADR-0264 governs this invariant and must be present"
    text = adr.read_text(encoding="utf-8")
    assert "R9" in text, "ADR-0264 must state the R9 volume-honesty rule"
    research = REPO_ROOT / "docs" / "research" / "distinct-evidence-audit-2026-07-25.md"
    assert research.exists(), (
        "the measured audit must stay written down — a 21-band exposure recorded "
        "only in a test's data structure is not a finding anyone will read"
    )
