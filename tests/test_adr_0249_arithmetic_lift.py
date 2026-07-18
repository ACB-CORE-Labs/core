"""ADR-0249 P5 — arithmetic-chain lift domain on the real GSM8K holdout.

Wires the turn-program executor into the generalized-lift instrument and
measures it against the *real* GSM8K dev holdout (never the templated cases),
with a symbolic fold of the same compiled program as the honest baseline. The
expected, honest outcome is PARITY with wrong=0 on the Tier-1 affine subset,
with the multi-entity remainder recorded — not a manufactured lift.
"""
from __future__ import annotations

import json

import pytest

from evals.generalized_lift_instrument import (
    run_arithmetic_chain_domain,
    run_generalized_lift_instrument,
)


@pytest.fixture(scope="module")
def domain():
    return run_arithmetic_chain_domain()


def test_domain_solves_real_gsm8k_wrong_zero(domain) -> None:
    assert domain.domain_id == "arithmetic-chain"
    assert domain.corridor_wrong == 0  # wrong=0 on real GSM8K, not just templates
    assert domain.corridor_correct > 0  # the corridor ingests and solves real problems
    # Tier-2 (ADR-0250) closed the multi-entity frontier: the full holdout ingests now.
    assert domain.corridor_refused == 0


def test_every_ingested_case_is_correct(domain) -> None:
    # The load-bearing claim: on real problems the corridor CAN ingest, it is
    # exactly right — refusals, never wrong answers.
    for row in domain.cases:
        if row["ingested"]:
            assert row["corridor_ok"] is True


def test_parity_with_symbolic_fold_honest_null(domain) -> None:
    # The field matches arithmetic on the same compiled program; it does not
    # beat it. PARITY is the honest verdict here, never an inflated lift.
    assert domain.corridor_correct == domain.baseline_correct
    assert domain.verdict == "PARITY"
    assert domain.delta_correct == 0


def test_coverage_is_recorded_not_dropped(domain) -> None:
    ingested = domain.corridor_correct + domain.corridor_wrong
    assert ingested + domain.corridor_refused == domain.n_cases
    assert domain.n_cases > 0
    # Coverage tracker against the sealed dev holdout: Tier-1 (26) + Tier-2 (24) = 50/50.
    assert domain.corridor_correct == 50
    assert domain.corridor_refused == 0
    assert any("Tier-2" in note for note in domain.notes)


def test_domain_joins_full_report_and_scope_corrected() -> None:
    report = run_generalized_lift_instrument()
    ids = [o.domain_id for o in report.outcomes]
    assert "arithmetic-chain" in ids
    assert report.wrong_zero_guard_held  # deductive + arithmetic both wrong=0
    # The scope note reflects the full-holdout closure; the stale "no compiler" line is gone.
    joined = " ".join(report.scope_limitations)
    assert "FULL real GSM8K dev holdout" in joined
    assert "no reader-to-Hamiltonian compiler exists" not in joined
    json.dumps(report.as_dict())  # JSON-safe artifact
