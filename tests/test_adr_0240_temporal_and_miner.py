"""ADR-0240 — temporal gate + self-authorship miner (proposal-only)."""

from __future__ import annotations

import numpy as np

from algebra.rotor import make_rotor_from_angle
from core.physics.self_authorship import SelfAuthorshipMiner
from core.physics.temporal_gate import (
    TemporalAdmissibilityGate,
    TemporalContext,
    TemporalVerdict,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def test_temporal_not_yet_before_min_step():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(
        TemporalContext(step=2, min_step=5, claim_id="c1", prerequisites_met=True)
    )
    assert d.verdict is TemporalVerdict.NOT_YET
    assert d.disclosure["type"] == "temporal_not_yet"


def test_temporal_not_yet_insufficient_evidence():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(
        TemporalContext(
            step=10,
            min_step=0,
            required_evidence_count=3,
            evidence_count=1,
            claim_id="c2",
        )
    )
    assert d.verdict is TemporalVerdict.NOT_YET


def test_temporal_admit():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(
        TemporalContext(
            step=10,
            min_step=3,
            required_evidence_count=2,
            evidence_count=2,
            coherence_residual=0.1,
            residual_ceiling=0.5,
            claim_id="c3",
        )
    )
    assert d.verdict is TemporalVerdict.ADMIT


def test_temporal_refuse_prerequisites():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(
        TemporalContext(step=10, min_step=0, prerequisites_met=False, claim_id="c4")
    )
    assert d.verdict is TemporalVerdict.REFUSE


def test_miner_proposals_speculative_and_ordered():
    miner = SelfAuthorshipMiner(residual_threshold=0.0)
    ref = _id()
    cur = make_rotor_from_angle(0.8)
    proposals = miner.mine_from_trajectory(cur, ref, notes="test")
    # May be empty or non-empty depending on residual; all must be SPECULATIVE
    ids = [p.proposal_id for p in proposals]
    assert ids == sorted(ids)
    for p in proposals:
        assert p.epistemic_status == "SPECULATIVE"
        assert "versor_condition_current" in p.closure_proof
        assert p.proposal_id.startswith("selfauth-")


def test_miner_replay_deterministic():
    miner = SelfAuthorshipMiner(residual_threshold=0.0)
    ref = _id()
    cur = make_rotor_from_angle(0.5)
    a = miner.mine_from_trajectory(cur, ref, basis=[_id()], analogs=[("x", ref, cur)])
    b = miner.mine_from_trajectory(cur, ref, basis=[_id()], analogs=[("x", ref, cur)])
    assert [p.as_dict() for p in a] == [p.as_dict() for p in b]


def test_miner_does_not_import_vault_store():
    import core.physics.self_authorship as mod
    import inspect

    src = inspect.getsource(mod)
    assert "VaultStore" not in src
    assert "vault.store" not in src
