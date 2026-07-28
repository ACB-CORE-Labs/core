"""Deduction-serve arc, Phase 3 (ADR-0256) — earned SERVE license tests.

Pins:
  - the shared shape-band classifier is deterministic + exhaustive;
  - the synthetic practice corpus is sound against the INDEPENDENT oracle
    (a mis-stated gold can never seal the ledger) and earns SERVE per band
    at the θ_SERVE=0.99 Wilson floor with wrong=0;
  - the committed sealed ledger's content_sha256 verifies on load (tamper-
    evidence), and a tampered ledger is rejected;
  - the serving composer serves AUTHORITATIVELY only for earned bands and
    DISCLOSES (hedges) an unearned band — the gate genuinely governs the
    serving posture, so the capability is earned, not merely flagged.
"""

from __future__ import annotations

import json

import pytest

from chat.deduction_serve_license import (
    RatifiedLedgerError,
    deduction_serve_license,
    load_ratified_ledger,
)
from chat.deduction_surface import (
    _UNVERIFIED_SHAPE_DISCLOSURE,
    deduction_grounded_surface,
)
from core.reliability_gate import Action, Ceilings, license_for
from generate.proof_chain.shape import (
    ALL_SHAPE_BANDS,
    ATOMIC,
    CONDITIONAL_CHAIN,
    CONDITIONAL_SINGLE,
    DISJUNCTIVE,
    SHAPE_BANDS,
    classify_deduction_shape,
)


# ---------------------------------------------------------------------------
# Shape classifier
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("premises,query,expected", [
    (("p implies q", "p"), "q", CONDITIONAL_SINGLE),
    (("p implies q", "q implies r", "p"), "r", CONDITIONAL_CHAIN),
    (("p or q", "not p"), "q", DISJUNCTIVE),
    (("p",), "p", ATOMIC),
    (("not p",), "p", ATOMIC),
])
def test_classify_deduction_shape(premises, query, expected) -> None:
    assert classify_deduction_shape(premises, query) == expected


def test_shape_bands_are_exhaustive_for_the_projector() -> None:
    """Every band the classifier can emit is a declared SHAPE_BAND (so the
    ledger's key space and the serving key space cannot drift)."""
    for premises, query in [
        (("a or b", "not a"), "b"),
        (("a implies b", "b implies c"), "a implies c"),
        (("a implies b", "a"), "b"),
        (("a",), "a"),
    ]:
        assert classify_deduction_shape(premises, query) in SHAPE_BANDS


# ---------------------------------------------------------------------------
# Practice corpus + arena ledger
# ---------------------------------------------------------------------------


def test_corpus_is_sound_against_independent_oracle() -> None:
    from evals.deduction_serve.practice.gold import assert_practice_gold_sound

    assert_practice_gold_sound()  # raises AssertionError on any mis-stated gold


#: The four bands whose DISTINCT evidence clears theta_SERVE=0.99 after the R-13
#: re-count. Derived from the audit, not chosen: they are the only bands whose
#: corpus contains enough *independent* cases. The other 21 held licences that
#: replay volume manufactured — 720 committed from as few as 28 distinct cases.
SERVE_LICENSED_BANDS = frozenset(
    {"en_conditional_chain", "en_disjunctive", "en_verb_fact", "en_verb_universal"}
)


def test_practice_is_wrong_zero_on_distinct_evidence() -> None:
    """``wrong=0`` survives the re-count — it was never the thing at issue.

    R-13 demoted 21 of 25 bands, and it is worth being exact about what that did
    and did not mean: **no answer changed and no answer became wrong.** The engine
    is exactly as correct as it was. What changed is the *claim* the ledger makes
    about how much independent evidence backs each band, and therefore which bands
    may answer authoritatively rather than with disclosure.
    """
    from evals.deduction_serve.practice.runner import run

    report = run()
    assert report["wrong_is_zero"] is True
    assert set(report["classes"]) == set(ALL_SHAPE_BANDS)
    for band, c in report["classes"].items():
        assert c["wrong"] == 0, band


def test_only_bands_with_distinct_evidence_earn_serve() -> None:
    """The demotion, pinned in BOTH directions (R-13).

    Down: a band outside :data:`SERVE_LICENSED_BANDS` must not be licensed — that is
    the exposure this ruling closed. Up: a band inside it must stay licensed — so a
    future change cannot quietly revoke earned capability either.
    """
    from evals.deduction_serve.practice.runner import run

    report = run()
    licensed = {b for b, c in report["classes"].items() if c["serve_licensed"]}
    assert licensed == set(SERVE_LICENSED_BANDS), (
        "the SERVE-licensed set moved. Down = capability lost; up = a band earned a "
        f"licence. Either is a reviewed decision.\n  now: {sorted(licensed)}\n"
        f"  pinned: {sorted(SERVE_LICENSED_BANDS)}"
    )
    assert report["all_bands_serve_licensed"] is False, (
        "all 25 bands are licensed again — the producer is counting replays as "
        "independent trials, which is exactly what R-13 removed"
    )
    for band, c in report["classes"].items():
        expected = band in SERVE_LICENSED_BANDS
        assert c["serve_licensed"] is expected, (band, c["reliability"])
        if expected:
            assert c["reliability"] >= 0.99, (band, c["reliability"])
        else:
            assert c["reliability"] < 0.99, (band, c["reliability"])


# ---------------------------------------------------------------------------
# Committed sealed ledger — tamper-evidence
# ---------------------------------------------------------------------------


def test_committed_ledger_verifies_and_matches_the_recount() -> None:
    """The committed artifact must agree with the re-counted licence set.

    All 25 bands stay *in* the ledger — a demoted band is not a deleted band. It
    keeps its evidence on the record and serves with disclosure, which is a
    stronger honesty position than vanishing: the reader can see exactly how much
    evidence the band has and why it is not enough.
    """
    ledger = load_ratified_ledger()
    assert set(ledger) == set(ALL_SHAPE_BANDS)
    ceilings = Ceilings.default()
    licensed = set()
    for band, tally in ledger.items():
        assert tally.wrong == 0, band
        if license_for(tally, Action.SERVE, ceilings).licensed:
            licensed.add(band)
    assert licensed == set(SERVE_LICENSED_BANDS), sorted(licensed)


def test_serve_license_returns_none_for_unknown_band() -> None:
    assert deduction_serve_license("nonexistent_band") is None


def test_tampered_ledger_is_rejected(tmp_path, monkeypatch) -> None:
    """A hand-edited ledger (counts inflated, sha not recomputed) must be
    rejected on load — only the sealed-practice output is trusted."""
    import chat.deduction_serve_license as mod

    from dataclasses import replace

    from core.ratified_ledger import CAPABILITY_LEDGERS

    original = json.loads(mod._LEDGER_PATH.read_text(encoding="utf-8"))
    original["classes"]["conditional_single"]["correct"] = 999999  # tamper
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(original), encoding="utf-8")
    # Redirect at the manifest, which owns the path since ADR-0263 rule 5 —
    # patching the module constant would no longer reach the load.
    monkeypatch.setitem(
        CAPABILITY_LEDGERS,
        mod._LEDGER_CAPABILITY,
        replace(CAPABILITY_LEDGERS[mod._LEDGER_CAPABILITY], path=tampered),
    )
    load_ratified_ledger.cache_clear()
    with pytest.raises(RatifiedLedgerError):
        load_ratified_ledger()
    load_ratified_ledger.cache_clear()  # restore cache for other tests


# ---------------------------------------------------------------------------
# Serving composer — the gate genuinely governs posture
# ---------------------------------------------------------------------------


def test_earned_band_serves_authoritatively() -> None:
    """An band that DID earn its licence on distinct evidence still serves plainly.

    ``en_conditional_chain`` is one of the four survivors (720 committed, 720
    distinct — no inflation at all). This is the direction that proves R-13 removed
    unearned licences rather than simply breaking authoritative serving.
    """
    surface = deduction_grounded_surface(
        "If the kettle boils then the whistle sounds. "
        "If the whistle sounds then the cat wakes. "
        "The kettle boils. Therefore the cat wakes."
    )
    assert surface is not None
    assert surface.startswith("Given:")
    assert _UNVERIFIED_SHAPE_DISCLOSURE not in surface


def test_demoted_band_still_answers_but_discloses() -> None:
    """The demotion changes the CLAIM, not the answer — the load-bearing half of R-13.

    ``conditional_single`` was licensed on 720 committed decisions drawn from 294
    distinct cases. After the re-count it is not licensed, and the same sound
    conclusion is served with the unverified-shape disclosure. The reasoning did not
    get worse; the boast did.
    """
    surface = deduction_grounded_surface("If p then q. p. Therefore q.")
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: q" in surface


def test_unearned_band_is_disclosed_not_committed() -> None:
    """Strip the ledger (inject an empty lookup) and the SAME sound answer is
    served DISCLOSED — proving the capability is earned, not merely flagged."""
    surface = deduction_grounded_surface(
        "If p then q. p. Therefore q.", license_lookup=lambda band: None,
    )
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: q" in surface  # the sound answer still served


# ---------------------------------------------------------------------------
# R-13 — the seal-time guard that makes the re-count unrepeatable
# ---------------------------------------------------------------------------


def test_sealer_refuses_a_ledger_that_counts_replays() -> None:
    """A padded ledger can never be sealed again (R-13 / ADR-0264 R9).

    The re-count fixed the artifact. This fixes the *producer*, which is the half
    that stops it recurring: ``seal_ledger`` refuses before writing anything.

    Worth recording how this assertion came to exist. The first version of the guard
    compared ``all_gold_problems()`` with ``distinct_gold_problems()`` — two functions
    that agree by construction and neither of which is what ``build_ledger`` folds.
    Reverting ``build_ledger`` to the raw corpus walked straight past it and re-sealed
    the inflated artifact. It was caught only because the guard was sabotage-tested
    instead of trusted, which is why the guard now takes the **built ledger** as input:
    the invariant is about the artifact, so the artifact is what it reads.
    """
    from core.reliability_gate import ClassTally
    from evals.deduction_serve.practice.runner import assert_sealed_evidence_distinct

    from evals.deduction_serve.practice.runner import build_ledger

    honest = build_ledger()
    assert_sealed_evidence_distinct(honest)  # the real ledger passes

    padded = dict(honest)
    band = "atomic"
    padded[band] = ClassTally(
        class_name=band,
        correct=720,
        wrong=0,
        refused=honest[band].refused,
        t2_verified=honest[band].t2_verified,
        t2_agrees_gold=honest[band].t2_agrees_gold,
    )
    with pytest.raises(ValueError, match="counts replays as independent trials"):
        assert_sealed_evidence_distinct(padded)
