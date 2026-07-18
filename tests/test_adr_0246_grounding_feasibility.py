"""ADR-0246 §11 grounding-feasibility study pins.

Pins the recovery-control sanity checks (the method must find structure when it
genuinely exists, and must not hallucinate structure from noise), the
bivector-proxy machinery, and the honest-verdict logic on injected cohorts — no
live runtime required. A separate live smoke test (marked slow) exercises the
real collectors.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from evals.adr_0246_grounding_feasibility import (
    BIVECTOR_DIM,
    build_feasibility_report,
    bivector_coefficients,
    cross_cohort_top_pc_cosine_similarity,
    precision_pair_delta,
    run_recovery_controls,
    subspace_residual_fraction,
)
from evals.adr_0246_mismatch_diagnostic import IDX_E12, IDX_E13, IDX_E14


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def test_bivector_coefficients_extract_the_right_slots():
    v = _rotor(IDX_E12, 0.6)
    coeffs = bivector_coefficients(v)
    assert coeffs.shape == (BIVECTOR_DIM,)
    assert coeffs[0] == pytest.approx(v[IDX_E12])
    assert np.count_nonzero(coeffs) == 1  # only e12 is populated


def test_recovery_controls_validate_the_method():
    # sample-size-calibrated: two independent cohorts sharing a TRUE rank-2
    # subspace must show cross-cohort cosine similarity far above what two
    # independent pure-noise cohorts of the SAME size produce by chance.
    result = run_recovery_controls(13)
    assert result["positive_control_cross_cohort_cosine"] > 0.8
    assert result["positive_control_percentile_in_null"] > 0.95
    assert result["method_recovers_true_structure"] is True
    # the null distribution itself should be well below the positive signal
    assert result["null_distribution"]["p95"] < result["positive_control_cross_cohort_cosine"]


def test_cross_cohort_cosine_detects_shared_structure():
    # both cohorts confined to the SAME e12/e13 plane pair -> high cosine
    cohort_a = [_rotor(IDX_E12, 0.1 * i + 0.05) for i in range(6)]
    cohort_b = [_rotor(IDX_E13, 0.1 * i + 0.05) for i in range(6)]
    # mix e12/e13 in both cohorts so both share a 2-plane subspace
    mixed_a = cohort_a + [_rotor(IDX_E13, 0.05 * i) for i in range(6)]
    mixed_b = cohort_b + [_rotor(IDX_E12, 0.05 * i) for i in range(6)]
    cosine = cross_cohort_top_pc_cosine_similarity(mixed_a, mixed_b, k=2)
    assert cosine > 0.5  # shared 2-plane structure should show real overlap


def test_cross_cohort_cosine_detects_unrelated_structure():
    cohort_a = [_rotor(IDX_E12, 0.1 * i + 0.05) for i in range(10)]
    # cohort_b lives entirely in an orthogonal plane (e.g. e35, far from e12)
    from evals.adr_0246_mismatch_diagnostic import IDX_E35
    cohort_b = [_rotor(IDX_E35, 0.1 * i + 0.05) for i in range(10)]
    cosine = cross_cohort_top_pc_cosine_similarity(cohort_a, cohort_b, k=1)
    assert cosine < 0.3  # unrelated single-plane structure -> low overlap


def test_subspace_residual_fraction_zero_inside_span():
    v = _rotor(IDX_E12, 0.5)
    coeffs = bivector_coefficients(v)
    basis = np.zeros((BIVECTOR_DIM, 1))
    basis[0, 0] = 1.0  # e12 direction (index 0 in BIVECTOR_INDICES)
    assert subspace_residual_fraction(coeffs, basis) < 1e-9


def test_precision_pair_delta_is_tiny():
    for versor in (_rotor(IDX_E12, 0.5), _rotor(IDX_E14, 1.3)):
        assert precision_pair_delta(versor) < 1e-4


def test_feasibility_report_null_on_unrelated_cohorts():
    # TRAIN and HELD-OUT confined to unrelated planes -> expect a NULL verdict
    train = [_rotor(IDX_E12, 0.1 * i + 0.05) for i in range(10)]
    from evals.adr_0246_mismatch_diagnostic import IDX_E35, IDX_E45
    held_out = [_rotor(IDX_E45, 0.1 * i + 0.05) for i in range(10)]
    adversarial = [_rotor(IDX_E14, 1.5), _rotor(IDX_E35, 1.2)]
    report = build_feasibility_report(train, held_out, adversarial)
    assert report["verdict"]["recovery_method_validated"] is True
    assert report["verdict"]["held_out_stable_structure_found"] is False
    assert "NULL" in report["verdict"]["honest_finding"]


def test_feasibility_report_positive_on_shared_plane_cohorts():
    # TRAIN and HELD-OUT share the same 2-plane structure (e12/e13); adversarial
    # lives elsewhere entirely (e14/e35/e45) -> expect the structure to be found
    # AND to discriminate against the adversarial cohort.
    from evals.adr_0246_mismatch_diagnostic import IDX_E35, IDX_E45
    rng = np.random.default_rng(7)
    def shared_plane_versor():
        theta12 = rng.normal(0, 0.3)
        theta13 = rng.normal(0, 0.3)
        v = np.zeros(N_COMPONENTS, dtype=np.float64)
        v[0] = 1.0
        v[IDX_E12] = theta12
        v[IDX_E13] = theta13
        return v
    train = [shared_plane_versor() for _ in range(15)]
    held_out = [shared_plane_versor() for _ in range(15)]
    adversarial = [_rotor(IDX_E14, 1.5), _rotor(IDX_E35, 1.3), _rotor(IDX_E45, 1.1)]
    report = build_feasibility_report(train, held_out, adversarial)
    assert report["cross_cohort_top2_cosine_similarity"] > 0.7
    assert "POSITIVE" in report["verdict"]["honest_finding"]


def test_report_schema_shape():
    train = [_rotor(IDX_E12, 0.1 * i + 0.05) for i in range(10)]
    held_out = [_rotor(IDX_E13, 0.1 * i + 0.05) for i in range(10)]
    adversarial = [_rotor(IDX_E14, 1.5)]
    report = build_feasibility_report(train, held_out, adversarial)
    assert report["schema_version"] == "adr_0246_grounding_feasibility_v1"
    assert set(report["cohorts"]) == {"train_n", "held_out_n", "adversarial_n"}
    assert "honest_finding" in report["verdict"]


def test_module_is_pure_offserving():
    import evals.adr_0246_grounding_feasibility as mod

    assert mod.__file__ is not None
    with open(mod.__file__, encoding="utf-8") as fh:
        src = fh.read()
    assert "import chat" not in src and "from chat" not in src
