"""#21 B — ADR-DAG conformal embedding Ψ(M) (R&D §2.4)."""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import grade_project
from core.adr.validator import (
    AdrDagValidationError,
    embed_adr_markdown,
    master_architecture_blade,
    proposal_drift,
    simple_bivector_project,
    validate_proposal_against_master,
)


def test_embed_deterministic_replay():
    m = "# ADR-TEST\n\nBody of the decision.\n"
    a = embed_adr_markdown(m)
    b = embed_adr_markdown(m)
    assert np.array_equal(a, b)
    assert a.shape == (32,)


def test_embed_differs_for_different_markdown():
    a = embed_adr_markdown("# ADR-A\nfoo")
    b = embed_adr_markdown("# ADR-B\nbar")
    assert not np.allclose(a, b)


def test_embed_is_grade2_supported():
    B = embed_adr_markdown("# ADR-G2\ncontent")
    # After simple project: only grade-2 (and zeros elsewhere)
    for g in (0, 1, 3, 4, 5):
        assert float(np.linalg.norm(grade_project(B, g))) < 1e-12
    assert float(np.linalg.norm(grade_project(B, 2))) > 0.0


def test_simple_bivector_project_collapses_multiplane():
    B = np.zeros(32, dtype=np.float64)
    B[6] = 0.9
    B[7] = 0.8
    B[8] = 0.1
    S = simple_bivector_project(B)
    # Dominant plane kept
    assert abs(S[6] - 0.9) < 1e-12 or abs(S[7] - 0.8) < 1e-12
    # At most one plane nonzero after collapse when multiplane non-simple
    n_planes = sum(1 for i in range(6, 16) if abs(S[i]) > 1e-12)
    assert n_planes == 1


def test_master_blade_refuses_empty():
    with pytest.raises(AdrDagValidationError, match="empty"):
        master_architecture_blade([])


def test_master_blade_from_two_adrs():
    e1 = embed_adr_markdown("# ADR-0003\nCoordinate dissolution.")
    e2 = embed_adr_markdown("# ADR-0006\nField energy.")
    A = master_architecture_blade([e1, e2])
    assert A.shape == (32,)
    assert float(np.linalg.norm(A)) > 0.0


def test_proposal_drift_nonneg_and_deterministic():
    masters = [
        embed_adr_markdown("# M1\none"),
        embed_adr_markdown("# M2\ntwo"),
    ]
    A = master_architecture_blade(masters)
    Bp = embed_adr_markdown("# Proposal\nnew idea")
    d1 = proposal_drift(Bp, A)
    d2 = proposal_drift(Bp, A)
    assert d1 == d2
    assert d1 >= 0.0


def test_validate_proposal_returns_ok_flag():
    masters_md = ["# ADR-A\nalpha", "# ADR-B\nbeta"]
    ok, drift, Bp, A = validate_proposal_against_master(
        "# Proposal\ngamma", masters_md, max_drift=1e9
    )
    assert ok is True
    assert drift >= 0.0
    assert Bp.shape == (32,)
    assert A.shape == (32,)


def test_validate_proposal_tight_max_drift_can_fail():
    masters_md = ["# ADR-A\nalpha", "# ADR-B\nbeta"]
    ok, drift, _Bp, _A = validate_proposal_against_master(
        "# Proposal\nentirely different body xyz", masters_md, max_drift=-1.0
    )
    # max_drift < 0 forces fail unless drift is negative (impossible)
    assert ok is False
    assert drift >= 0.0
