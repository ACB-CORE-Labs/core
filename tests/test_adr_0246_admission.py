"""ADR-0246 §3.7 admit-surface + §6.3 discrimination-report pins.

Pins the pure admit surface (`evaluate_admission`, locked `H_id={I}`, placeholder
thresholds) and the honest discrimination verdict: on the declared placeholder
frame the gate refuses benign and adversarial alike and does NOT separate them —
a result that must be reported plainly, never framed as a working detector.
Offline/deterministic: cohorts are injected, so no runtime is spun up here.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics import identity
from core.physics.identity_manifold import IdentityManifoldGeometry, MalformedVersorError
from core.physics.identity_action import (
    AdmissionPolicy,
    CERTIFIED_GAMMA_ID,
    evaluate_admission,
)
from evals.adr_0246_discrimination import build_discrimination_report

_E12, _E14, _E15 = 6, 8, 9


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _boost(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cosh(theta / 2.0)
    r[biv] = np.sinh(theta / 2.0)
    return r


def _identity_versor():
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


@pytest.fixture(scope="module")
def geometry():
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


def test_certified_gamma_id_matches_d4_bound_no_drift():
    # the one certified threshold must equal the D4-pinned serve bound
    assert CERTIFIED_GAMMA_ID == identity._WAVE_LEAKAGE_BOUND


def test_placeholder_policy_is_flagged_uncalibrated():
    assert AdmissionPolicy.placeholder_default().calibrated is False


def test_identity_versor_is_admitted(geometry):
    result = evaluate_admission(geometry, _identity_versor(), AdmissionPolicy.placeholder_default())
    assert result.admitted is True
    assert result.refusal_reasons == ()
    assert result.d_orth < 1e-9 and result.d_stab < 1e-9


@pytest.mark.parametrize("versor", [_rotor(_E14, 1.5), _boost(_E15, 1.2), _rotor(_E12, np.pi)])
def test_attacks_are_refused_with_reasons(geometry, versor):
    result = evaluate_admission(geometry, versor, AdmissionPolicy.placeholder_default())
    assert result.admitted is False
    assert len(result.refusal_reasons) >= 1


def test_admission_is_admit_or_abstain_never_corrects(geometry):
    # evaluate_admission returns a verdict + measurements; it never returns a
    # modified versor/action (no corrector surface exists)
    result = evaluate_admission(geometry, _rotor(_E14, 1.0), AdmissionPolicy.placeholder_default())
    assert set(result.as_dict()) == {
        "admitted", "refusal_reasons", "d_orth", "d_stab",
        "leakage_rms", "max_leakage", "min_self_alignment", "typed_channels",
    }


def test_malformed_versor_raises_for_failclosed_serve(geometry):
    bad = _identity_versor()
    bad[3] = np.nan
    with pytest.raises(MalformedVersorError):
        evaluate_admission(geometry, bad, AdmissionPolicy.placeholder_default())


def test_discrimination_report_reports_honest_non_separation(geometry):
    # inject a benign cohort that mimics REAL benign traffic (far from the frame,
    # per D4/slice-0) so the honest verdict is pinned without a live runtime.
    benign = [
        ("benign_like_boost", _boost(_E15, 1.1)),
        ("benign_like_boost2", _boost(9, 1.3)),
        ("benign_like_tilt", _rotor(_E14, 1.2)),
        ("benign_like_big", _rotor(_E12, 2.5)),
    ]
    report = build_discrimination_report(benign, geometry=geometry)
    assert report["policy"]["calibrated"] is False
    # benign mass-refused; a refuse-all "detects" all attacks but does not discriminate
    assert report["rates"]["benign_pass_rate"] == 0.0
    assert report["rates"]["false_refusal_rate"] == 1.0
    assert report["rates"]["adversarial_detection_rate"] == 1.0
    assert report["verdict"]["gate_discriminates_benign_from_adversarial"] is False
    assert report["verdict"]["benign_usable_at_this_policy"] is False
    # the honest claims language must be present and must NOT oversell
    claims = report["verdict"]["claims_language"].lower()
    assert "lawfulness relative to the declared frozen frame" in claims
    assert "inalienab" in claims  # explicitly names what it is NOT


def test_discrimination_control_admits_true_near_identity(geometry):
    # the synthetic-near-identity control passing confirms the gate MECHANISM is
    # sound — the benign failure is the frame, not a broken gate.
    report = build_discrimination_report(
        [("benign_like", _boost(_E15, 1.1))], geometry=geometry
    )
    assert report["rates"]["synthetic_near_identity_pass_rate"] == 1.0
