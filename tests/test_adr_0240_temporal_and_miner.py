"""ADR-0240 — temporal gate + self-authorship miner."""

from __future__ import annotations

import inspect

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


def test_temporal_not_yet():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(TemporalContext(step=1, min_step=5, claim_id="c1"))
    assert d.verdict is TemporalVerdict.NOT_YET


def test_temporal_admit():
    gate = TemporalAdmissibilityGate()
    d = gate.evaluate(
        TemporalContext(
            step=10,
            min_step=0,
            required_evidence_count=1,
            evidence_count=1,
            claim_id="c2",
        )
    )
    assert d.verdict is TemporalVerdict.ADMIT


def test_miner_speculative_ordered():
    miner = SelfAuthorshipMiner(residual_threshold=0.0)
    props = miner.mine_from_trajectory(make_rotor_from_angle(0.8), _id())
    ids = [p.proposal_id for p in props]
    assert ids == sorted(ids)
    for p in props:
        assert p.epistemic_status == "SPECULATIVE"


def test_miner_replay():
    miner = SelfAuthorshipMiner(residual_threshold=0.0)
    a = miner.mine_from_trajectory(make_rotor_from_angle(0.5), _id())
    b = miner.mine_from_trajectory(make_rotor_from_angle(0.5), _id())
    assert [p.as_dict() for p in a] == [p.as_dict() for p in b]


def test_miner_no_vault_store():
    import core.physics.self_authorship as mod

    src = inspect.getsource(mod)
    assert "VaultStore" not in src
