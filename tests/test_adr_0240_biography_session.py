"""ADR-0243 §2.5 — harness-driven biography session pins (seam S2 closure).

The first real caller of the PASS-gated biography wiring: run the ADR-0240
transfer harness, recompute the lived trajectory (recovered transfer versors
of the CORRECT cases — reconstruction-over-storage), integrate, and prove
I-01 reboot-invariance: the same session recomputes the identical blade and
provenance record from scratch.
"""

from __future__ import annotations

import dataclasses
import json

import numpy as np
import pytest

from core.physics.biography_wiring import BiographyIntegrationError
from evals.analogical_transfer.biography_session import (
    run_biography_session,
    session_trajectory,
)
from evals.analogical_transfer.harness import make_fixture_pair, run_analogical_transfer

_CLOSURE = 1e-6


def test_pass_session_integrates_lived_trajectory():
    case = make_fixture_pair()
    artifact = run_biography_session([case])
    assert artifact.report.wrong == 0
    assert artifact.trajectory_case_ids == (case.case_id,)
    assert artifact.blade.n_steps == 1
    assert artifact.blade.closure < _CLOSURE
    assert artifact.record.schema_version == "biography_provenance_v2"
    assert artifact.record.chiral_proof["blade_verdict"] == "vacuous"
    json.dumps(artifact.as_dict())  # JSON-safe session artifact


def test_session_reboot_invariance_i01():
    """Same cases → bit-identical blade, trajectory hash, and record id.
    Reconstruction-over-storage: nothing was persisted between the two runs.
    (Bit-identity is the honest I-01 claim; holonomy_similarity is not a
    normalized self-overlap and would be a weaker, misleading assert.)"""
    cases = [make_fixture_pair()]
    a = run_biography_session(cases)
    b = run_biography_session(cases)
    assert np.array_equal(a.blade.blade, b.blade.blade)
    assert a.blade.trajectory_hash == b.blade.trajectory_hash
    assert a.record.record_id == b.record.record_id


def test_session_trajectory_recomputes_only_correct_cases():
    cases = [make_fixture_pair()]
    report = run_analogical_transfer(cases)
    versors, ids = session_trajectory(cases, report)
    assert len(versors) == 1 and ids == (cases[0].case_id,)


def test_failing_session_integrates_nothing():
    """A session with wrongs refuses (typed) — no confabulated wisdom.

    The clean fixture recovers its transfer to machine precision (residual
    ~1e-16), so failure is induced honestly: a corrupted expected_novel makes
    the transfer WRONG, and the wiring must refuse the whole session."""
    case = make_fixture_pair()
    corrupted = dataclasses.replace(case, expected_novel=np.roll(case.expected_novel, 1))
    with pytest.raises(BiographyIntegrationError) as exc_info:
        run_biography_session([corrupted])
    assert exc_info.value.reason == "report_not_pass"
