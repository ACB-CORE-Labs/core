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
    from evals.deduction_serve.practice.gold import assert_corpus_sound

    assert_corpus_sound()  # raises AssertionError on any mis-stated gold


def test_every_band_earns_serve_wrong_zero() -> None:
    from evals.deduction_serve.practice.runner import run

    report = run()
    assert report["wrong_is_zero"] is True
    assert report["all_bands_serve_licensed"] is True
    assert set(report["classes"]) == set(ALL_SHAPE_BANDS)
    for band, c in report["classes"].items():
        assert c["wrong"] == 0, band
        assert c["serve_licensed"] is True, band
        assert c["reliability"] >= 0.99, (band, c["reliability"])


# ---------------------------------------------------------------------------
# Committed sealed ledger — tamper-evidence
# ---------------------------------------------------------------------------


def test_committed_ledger_verifies_and_earns_serve() -> None:
    ledger = load_ratified_ledger()
    assert set(ledger) == set(ALL_SHAPE_BANDS)
    ceilings = Ceilings.default()
    for band, tally in ledger.items():
        assert tally.wrong == 0, band
        assert license_for(tally, Action.SERVE, ceilings).licensed is True, band


def test_serve_license_returns_none_for_unknown_band() -> None:
    assert deduction_serve_license("nonexistent_band") is None


def test_tampered_ledger_is_rejected(tmp_path, monkeypatch) -> None:
    """A hand-edited ledger (counts inflated, sha not recomputed) must be
    rejected on load — only the sealed-practice output is trusted."""
    import chat.deduction_serve_license as mod

    original = json.loads(mod._LEDGER_PATH.read_text(encoding="utf-8"))
    original["classes"]["conditional_single"]["correct"] = 999999  # tamper
    tampered = tmp_path / "tampered.json"
    tampered.write_text(json.dumps(original), encoding="utf-8")
    monkeypatch.setattr(mod, "_LEDGER_PATH", tampered)
    load_ratified_ledger.cache_clear()
    with pytest.raises(RatifiedLedgerError):
        load_ratified_ledger()
    load_ratified_ledger.cache_clear()  # restore cache for other tests


# ---------------------------------------------------------------------------
# Serving composer — the gate genuinely governs posture
# ---------------------------------------------------------------------------


def test_earned_band_serves_authoritatively() -> None:
    """With the committed (earned) ledger, an in-band argument is served
    plainly — no hedge (Phase 1 behavior preserved)."""
    surface = deduction_grounded_surface("If p then q. p. Therefore q.")
    assert surface is not None
    assert surface.startswith("Given:")
    assert _UNVERIFIED_SHAPE_DISCLOSURE not in surface


def test_unearned_band_is_disclosed_not_committed() -> None:
    """Strip the ledger (inject an empty lookup) and the SAME sound answer is
    served DISCLOSED — proving the capability is earned, not merely flagged."""
    surface = deduction_grounded_surface(
        "If p then q. p. Therefore q.", license_lookup=lambda band: None,
    )
    assert surface is not None
    assert surface.startswith(_UNVERIFIED_SHAPE_DISCLOSURE)
    assert "Your premises entail: q" in surface  # the sound answer still served
