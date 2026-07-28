"""R-8 (ruled C) / G-10 — the curriculum outcome-mix rule, and what it measures.

**The rule.** Committing to an entailment and correctly declining to commit are
different capabilities. They are licensed on different evidence and may not be
pooled. ``core.ratified_ledger.CAPABILITY_LEDGERS`` declares them as two entries;
this module measures them.

**Why the rule was needed, in one number.** Pooled, the four leading bands reach
660 committed decisions and ``conservative_floor(660, 660) = 0.990046``, clearing
θ_SERVE=0.99 — by a margin of **0.000046**. Split, the same bands hold **652–653
correct UNKNOWNs** and **7–8 entailments**. Neither half clears. The licence was
manufactured entirely by counting correct refusals and correct commitments as one
kind of evidence.

**This overturns the plan's own prediction.** N-5 recorded that *"four bands would
earn SERVE the moment a ledger is sealed."* That is true on the pooled basis and
false on the ruled one. Sealing under R-8 C licenses **nothing** — which is exactly
why the plan blocked PR-14 on this ruling rather than sealing first and ruling
after. A ledger sealed on the pooled basis would have granted four licences that the
mix rule then had to revoke, and revoking a granted licence is the expensive
direction (see R-13 and the 21 deduction bands).

**The shortfall is small and exact, and that is the useful part.** Unknown-serving
needs **four to five** more distinct query atoms per band (657 − 653 for two bands,
657 − 652 for the other two). Entailed-serving needs roughly **648** more. Those are
content tasks of wildly different size, and before the split nobody could see that —
the pooled number hid a four-case gap behind a 648-case one.

This module deliberately does **not** seal a ledger. Under the rule there is nothing
to license, and an artifact asserting zero licences is a file whose only content is
its own emptiness; the registered ``missing_ok=True`` absence already says it, once.
"""

from __future__ import annotations

import pytest

from core.ratified_ledger import CAPABILITY_LEDGERS
from core.reliability_gate import conservative_floor
from core.reliability_gate.evidence import SERVE_VOLUME_AT_THETA_099

THETA_SERVE = 0.99


@pytest.fixture(scope="module")
def mix() -> dict[str, dict[str, int]]:
    """Per-band ``{'entailed': n, 'unknown': n}`` from the practice producer."""
    from evals.curriculum_serve.practice.runner import run

    report = run()
    return {band: dict(c["gold_mix"]) for band, c in report["classes"].items()}


def test_both_capabilities_are_registered() -> None:
    """The split is declared in the manifest, not asserted at a call site.

    ADR-0263 rule 5. If this fails, the outcome-mix rule exists only in prose —
    which is the state R-8 was raised to end.
    """
    assert "curriculum_serve" in CAPABILITY_LEDGERS
    assert "curriculum_serve_entailed" in CAPABILITY_LEDGERS
    assert CAPABILITY_LEDGERS["curriculum_serve_entailed"].missing_ok is True, (
        "absent must mean 'nothing licensed' for the entailed capability — a "
        "missing_ok=False entry would turn an honest absence into a broken deployment"
    )


def test_the_mix_is_not_vacuous(mix: dict[str, dict[str, int]]) -> None:
    """Guard the measurement before asserting anything about it."""
    assert len(mix) >= 10, f"parsed only {len(mix)} bands from the producer"
    assert any(m.get("entailed", 0) for m in mix.values()), "no entailed cases parsed"
    assert any(m.get("unknown", 0) for m in mix.values()), "no unknown cases parsed"


def test_no_band_licenses_entailed_serving(mix: dict[str, dict[str, int]]) -> None:
    """The committing capability, on its own evidence: nothing qualifies.

    ``conservative_floor(9, 9) == 0.0`` — the Wilson lower bound at nine trials is
    not merely below θ, it is zero. This is the assertion that stops an entailment
    licence being granted on a handful of cases, which is what pooling did.
    """
    offenders = {
        band: n
        for band, m in mix.items()
        if (n := m.get("entailed", 0)) and conservative_floor(n, n) >= THETA_SERVE
    }
    assert not offenders, (
        f"these bands now hold enough entailed evidence to license: {offenders}. "
        "That is good news and a reviewed decision — seal the entailed ledger and "
        "move this pin."
    )
    best = max(m.get("entailed", 0) for m in mix.values())
    assert best < SERVE_VOLUME_AT_THETA_099, (
        f"max entailed evidence is {best}, at or above the {SERVE_VOLUME_AT_THETA_099} "
        "θ_SERVE requires — the entailed capability is now earnable"
    )


def test_no_band_licenses_unknown_serving_either(mix: dict[str, dict[str, int]]) -> None:
    """The declining capability, on its OWN evidence: also nothing — the finding.

    This is the assertion that contradicts N-5. The four bands everyone expected to
    license hold 652–653 correct UNKNOWNs against a 657 requirement: **four to five
    short**.
    They only ever cleared because 7–8 entailments were pooled in to reach 660.
    """
    licensed = {
        band: n
        for band, m in mix.items()
        if (n := m.get("unknown", 0)) and conservative_floor(n, n) >= THETA_SERVE
    }
    assert not licensed, (
        f"these bands now license unknown-serving on distinct non-commitments: "
        f"{licensed}. Expected under the ruling once curriculum volume grows — seal "
        "the ledger and move this pin, in the same change."
    )


def test_pooling_would_have_licensed_four_bands(mix: dict[str, dict[str, int]]) -> None:
    """Pin the counterfactual, because it is the whole justification for the rule.

    If this ever fails it means pooling no longer manufactures a licence, and the
    mix rule has become free rather than load-bearing — worth knowing either way. It
    is asserted rather than written in prose so the number cannot quietly drift away
    from the argument that rests on it.
    """
    pooled = {
        band: total
        for band, m in mix.items()
        if conservative_floor(total := sum(m.values()), total) >= THETA_SERVE
    }
    assert len(pooled) == 4, (
        f"pooled evidence licenses {len(pooled)} bands, not the 4 recorded when R-8 "
        f"was ruled: {sorted(pooled)}"
    )
    for band, total in pooled.items():
        entailed = mix[band].get("entailed", 0)
        unknown = mix[band].get("unknown", 0)
        assert conservative_floor(unknown, unknown) < THETA_SERVE, band
        assert entailed < 10, (band, entailed)
        assert total >= SERVE_VOLUME_AT_THETA_099, (band, total)


def test_the_shortfall_is_recorded_exactly(mix: dict[str, dict[str, int]]) -> None:
    """Four or five cases, not "more volume" — the gap is small, and its size is the point.

    Before the split, the unknown shortfall (4-5) was hidden behind the entailed one
    (~648). A single pooled figure could not distinguish "almost there" from
    "two orders of magnitude away," and those call for completely different work.
    """
    best_unknown = max(m.get("unknown", 0) for m in mix.values())
    best_entailed = max(m.get("entailed", 0) for m in mix.values())
    assert SERVE_VOLUME_AT_THETA_099 - best_unknown == 4, (
        f"the unknown-serving shortfall moved: best band has {best_unknown} distinct "
        f"non-commitments against {SERVE_VOLUME_AT_THETA_099} required"
    )
    assert SERVE_VOLUME_AT_THETA_099 - best_entailed > 600, (
        f"the entailed shortfall is now {SERVE_VOLUME_AT_THETA_099 - best_entailed}; "
        "if it has closed to within a few hundred, the entailed capability is worth "
        "re-planning rather than deferring"
    )
