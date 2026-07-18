"""Seam S4/S5 pins — generalized-lift instrument + ports/handoff evidence.

The instrument is the arbiter of "generalized lift, no overfitting": identical
compiled problems for corridor and baseline, independent truth-table gold,
wrong=0 guard on the propositional (flagship-regime) domain, and an
honest-NULL protocol. The handoff evidence pins that Ring-2/Ring-3 machinery
DISCRIMINATES (proceed on the lawful identity-action turn, typed abstain on a
frame-rotating turn) — off-serving, flags untouched.
"""

from __future__ import annotations

import json

import pytest

from evals.generalized_lift_instrument import (
    run_generalized_lift_instrument,
)
from evals.lift_evidence_handoff import run_lift_evidence_handoff


@pytest.fixture(scope="module")
def report():
    return run_generalized_lift_instrument()


def test_propositional_domain_wrong_zero_and_gold_agreement(report):
    prop = report.outcomes[0]
    assert prop.domain_id == "propositional"
    assert prop.corridor_wrong == 0  # the flagship-regime guard
    assert prop.baseline_wrong == 0
    for row in prop.cases:
        assert row["corridor_entailed"] == row["gold_entailed"]
        assert row["baseline_entailed"] == row["gold_entailed"]
    assert prop.verdict == "PARITY"  # honest expected outcome: both exact


def test_recognition_domain_shows_relax_readback_lift(report):
    rec = report.outcomes[1]
    assert rec.domain_id == "constrained-recognition"
    assert rec.corridor_correct == rec.n_cases  # relax+readback recovers every mode
    assert rec.corridor_wrong == 0 and rec.corridor_refused == 0
    assert rec.baseline_correct < rec.n_cases  # constraint-blind argmax fails
    assert rec.delta_correct > 0 and rec.verdict == "LIFT"
    for row in rec.cases:
        assert row["roundtrip_agreement"] > 0.99  # hearing ourselves think


def test_multimodal_domain_recorded_honestly(report):
    multi = report.outcomes[2]
    assert multi.domain_id == "multimodal-completion"
    assert multi.n_cases == 1
    assert multi.corridor_wrong == 0
    assert multi.verdict in ("LIFT", "PARITY")  # measured, never assumed


def test_report_flags_and_scope_limitations(report):
    assert report.wrong_zero_guard_held
    assert isinstance(report.honest_null, bool)
    assert any("GSM8K" in note for note in report.scope_limitations)
    json.dumps(report.as_dict())  # JSON-safe artifact


def test_handoff_evidence_discriminates():
    artifact = run_lift_evidence_handoff()
    lawful = artifact["turns"]["identity-action"]
    rotated = artifact["turns"]["frame-rotating"]

    assert lawful["chain_verified"] and rotated["chain_verified"]
    assert lawful["identity_action"]["action"] == "proceed"
    assert lawful["precision_action"]["action"] == "proceed"
    assert lawful["handoff"]["handoff"] == "proceed"

    assert rotated["identity_action"]["action"] == "abstain"
    assert "d_stab>epsilon_turn" in rotated["identity_action"]["reasons"]
    assert rotated["handoff"]["handoff"] == "abstain"
    assert any(r.startswith("port:identity:") for r in rotated["handoff"]["reasons"])

    json.dumps(artifact)  # JSON-safe acceptance-evidence artifact
