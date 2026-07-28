"""FA-1's verdict, pinned as a tripwire (G-25, L2, the CORE-Logos validation-gate claim).

Measured 2026-07-28 against the criterion registered at `94f05ba8`: on a semantic ground with
**zero** coordinate collisions and a genuinely closed loop, cross-language holonomy separates
aligned clauses from meaning-breaking ones at **AUC 0.557** — a chance floor is 0.500. The
design's own word-order test holds only **64.4%** of the time. **NO-GO.**

Full result and diagnosis: `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`.

This pin exists for the reason the 2026-06-14 holonomy finding gave for its own tripwires: a
negative result that nothing checks decays into folklore, and the *interesting* failure mode
is the good one — a future encoding that makes the gate real, landing silently while four
documents still say it was measured and refused. If any of these assertions goes red because
the numbers improved, that is not a regression: replace the guard with a proof, amend the ADRs
back, and update the verdict document in the same commit.

Both directions are pinned. The verdict may not silently become GO, and the measured values
may not silently drift either — the gate is deterministic, so any movement means the ground,
the encoder, or the corpus changed, and each of those is a decision someone should be making
on purpose.

Cost: ~16s. Paid deliberately for the tripwire on the system's central design claim, the way
the daemon pin's 9.4s was paid — stated here rather than estimated.
"""

from __future__ import annotations

import pytest

from evals.logos.fa1_gate import G1_AUC, G2_AUC, G3_ORDER_SENSITIVITY, run

#: Measured 2026-07-28 at `94f05ba8`+1, deterministic and re-run bit-identical.
RECORDED = {
    "G1_separation": 0.5570894467955959,
    "G2_cross_pair": 0.6641552204384346,
    "G3_word_order": 0.6444881889763779,
    "G4_no_collapse": 0,
}
RECORDED_ALIGNED_PAIRS = 1016
RECORDED_CONCEPTS = 24
RECORDED_UNRESOLVED_EDGES = 24  # every one of them into the unloadable collapse-anchor pack


@pytest.fixture(scope="module")
def verdict() -> dict:
    return run()


def test_the_repairs_still_work(verdict: dict) -> None:
    """G4 and the controls. If these fail, the NO-GO below is uninterpretable.

    This is the half of the result that SUCCEEDED: the geodesic blend keeps every distinction
    (0 lost coordinates where the shipped compiler loses 53 on this mount), and the closed loop
    reports closure on a self-pair. A null result measured with a broken instrument constrains
    nothing, which is exactly why the June measurement had to be re-run.
    """
    assert verdict["ground_after_repair"]["coordinates_lost"] == 0, (
        "G4 FAILED: the repaired ground now collapses coordinates. Every discrimination number "
        "in this file is measured on a different ground than the verdict document describes."
    )
    assert verdict["controls"]["max_self_loop_deviation"] < 1e-4, (
        "the loop no longer closes on a self-pair — the metric is broken, not the hypothesis"
    )
    assert verdict["controls"]["aligned_pairs"] == RECORDED_ALIGNED_PAIRS, (
        f"corpus changed: {verdict['controls']['aligned_pairs']} aligned pairs vs "
        f"{RECORDED_ALIGNED_PAIRS} recorded — re-baseline deliberately, in the verdict doc too"
    )


def test_the_verdict_is_still_no_go(verdict: dict) -> None:
    """The tripwire. Red here means the design became real — go read the failure message."""
    assert verdict["VERDICT"] == "NO-GO", (
        "FA-1's holonomy gate now PASSES. This is good news and it is not a test failure to "
        "silence: replace this guard with a proof, amend ADR-0005/0015 back (they were amended "
        "to record the negative), and rewrite "
        "docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md in the same commit."
    )
    criterion = verdict["criterion"]
    assert not criterion["G1_separation"]["pass"], f"G1 now passes at {criterion['G1_separation']['observed']}"
    assert not criterion["G2_cross_pair"]["pass"], f"G2 now passes at {criterion['G2_cross_pair']['observed']}"
    assert not criterion["G3_word_order"]["pass"], f"G3 now passes at {criterion['G3_word_order']['observed']}"


def test_the_recorded_numbers_have_not_drifted(verdict: dict) -> None:
    """Deterministic gate, exact record. Movement in either direction is a reviewed decision."""
    for gate, expected in RECORDED.items():
        observed = verdict["criterion"][gate]["observed"]
        assert observed == pytest.approx(expected, abs=1e-9), (
            f"{gate} moved: {observed} vs {expected} recorded. The gate is deterministic, so "
            "the ground, the encoder, or the corpus changed. Update this constant and the "
            "verdict document together — two records that disagree is the G-22 disease."
        )
    assert verdict["corpus"]["concepts"] == RECORDED_CONCEPTS
    assert verdict["corpus"]["edges_unresolved_under_R3"] == RECORDED_UNRESOLVED_EDGES, (
        "the unresolved-edge count moved. All 24 point into en_collapse_anchors_v1, which "
        "cannot load because its manifest declares role='collapse_anchor' and that is not a "
        "member of packs.schema.LanguageRole. If this dropped to 0 the enum was widened — good; "
        "record it, because those edges then join the corpus and every number above moves."
    )


def test_the_gate_is_not_vacuous(verdict: dict) -> None:
    """A criterion that cannot pass proves nothing (R-11's lesson, PR-12's hollow guard).

    The thresholds must be reachable and the classes must be ordered by meaning-distance —
    otherwise "NO-GO" would be an artefact of an impossible bar rather than a measurement.
    """
    assert 0.5 <= G1_AUC <= 1.0 and 0.5 <= G2_AUC <= 1.0 and 0.5 <= G3_ORDER_SENSITIVITY <= 1.0, (
        "a threshold outside [0.5, 1.0] would be unreachable or trivially met by chance"
    )
    measurements = verdict["measurements"]
    assert measurements["median_aligned"] < measurements["median_negative"], (
        "aligned pairs no longer close tighter than negatives — the signal reversed sign, which "
        "is a different (and larger) finding than the recorded weak-but-correct-direction one"
    )
    # The classes order themselves by distance from the original meaning. This is the part of
    # the design that DID hold, and it is what makes the null a measurement rather than noise.
    assert (
        measurements["median_lexical"] < measurements["median_word_order"] < measurements["median_cross_pair"]
    ), (
        "the negative classes no longer order by meaning-distance "
        f"(lexical={measurements['median_lexical']}, order={measurements['median_word_order']}, "
        f"cross={measurements['median_cross_pair']}) — re-diagnose before trusting the verdict"
    )
    assert verdict["controls"]["negatives_generated"]["cross_pair"] > 0, "no negatives generated"
