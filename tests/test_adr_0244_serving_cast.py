"""ADR-0244 §2.5 / ADR-0245 §2.2 — governed f64→f32 serving-boundary cast.

Pins the single explicit down-cast at the certified lifecycle egress: it casts
only a certified, admitted, digest-matched state; keeps f64 as the source of
truth (the digest chain is untouched); is precision-checked (fails closed on an
f32 cliff) and deterministic.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.cognitive_lifecycle import (
    RelaxationResult,
    ServingCastError,
    ServingState,
    compile_quadratic_well,
    egress_gate,
    relax_to_ground,
    serving_cast,
)


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


def _onehot(i: int) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[i] = 1.0
    return v


def _certified_outcome():
    target = _unit(_onehot(1) + _onehot(6))
    ham = compile_quadratic_well(target, curvature=1.0)
    result = relax_to_ground(_unit(_onehot(1) + 0.3 * _onehot(6)), ham)
    verdict = egress_gate(result.psi_steady, result.certificate)
    assert verdict.admitted is True
    return result, verdict


def test_cast_of_certified_state_is_f32_and_within_tolerance():
    result, verdict = _certified_outcome()
    state = serving_cast(result.psi_steady, result.certificate, verdict)
    assert isinstance(state, ServingState)
    assert state.psi_f32.dtype == np.dtype("<f4")
    assert state.psi_f32.shape == (N_COMPONENTS,)
    assert state.cast_error < 1e-6  # documented f32 parity tolerance
    assert abs(state.unit_norm_f32 - 1.0) < 1e-6
    # provenance links back to the f64 certificate
    assert state.source_psi_digest == result.certificate.psi_digest
    assert state.certificate_id == result.certificate.certificate_id


def test_f64_remains_the_source_of_truth():
    result, verdict = _certified_outcome()
    digest_before = result.certificate.psi_digest
    serving_cast(result.psi_steady, result.certificate, verdict)
    # neither the state nor its certificate/digest is mutated by the cast
    assert result.psi_steady.dtype == np.float64
    assert result.certificate.psi_digest == digest_before


def test_cast_is_deterministic():
    result, verdict = _certified_outcome()
    a = serving_cast(result.psi_steady, result.certificate, verdict)
    b = serving_cast(result.psi_steady, result.certificate, verdict)
    assert np.array_equal(a.psi_f32, b.psi_f32)
    assert a.cast_error == b.cast_error and a.unit_norm_f32 == b.unit_norm_f32


def test_uncertified_verdict_is_never_served():
    result, _ = _certified_outcome()

    class _Refused:
        admitted = False
        reason = "relaxation_not_certified"

    with pytest.raises(ServingCastError, match="uncertified_state_not_served"):
        serving_cast(result.psi_steady, result.certificate, _Refused())


def test_digest_mismatch_refuses():
    result, verdict = _certified_outcome()
    ham = compile_quadratic_well(_unit(_onehot(2) + _onehot(6)), curvature=1.0)
    other = relax_to_ground(_unit(_onehot(2) + 0.2 * _onehot(6)), ham)
    # a state that is not the one the certificate addresses must not be served
    with pytest.raises(ServingCastError, match="certificate_state_mismatch"):
        serving_cast(other.psi_steady, result.certificate, verdict)


def test_malformed_state_refuses_before_casting():
    result, verdict = _certified_outcome()
    with pytest.raises(ServingCastError, match="bad_shape"):
        serving_cast(np.zeros(16, dtype=np.float64), result.certificate, verdict)
    bad = np.array(result.psi_steady, dtype=np.float64, copy=True)
    bad[0] = np.nan
    with pytest.raises(ServingCastError, match="non_finite"):
        serving_cast(bad, result.certificate, verdict)


def test_precision_sufficiency_guard_is_enforced():
    # For a unit versor f32 is sufficient, so the guard passes in normal use.
    # Tightening tol below f32's own rounding proves the guard is live (fails
    # closed on a precision cliff) rather than decorative.
    result, verdict = _certified_outcome()
    with pytest.raises(ServingCastError, match="f32_precision_insufficient"):
        serving_cast(result.psi_steady, result.certificate, verdict, tol=0.0)


def test_serving_state_as_dict_is_audit_ready():
    result, verdict = _certified_outcome()
    d = serving_cast(result.psi_steady, result.certificate, verdict).as_dict()
    assert d["certificate_id"] == result.certificate.certificate_id
    assert d["source_psi_digest"] == result.certificate.psi_digest
    assert d["dtype"] == "float32"
    assert d["cast_error"] < 1e-6


def test_cast_never_imported_into_serve_hot_path():
    # A-04: cognitive_lifecycle stays off the chat serve path.
    import inspect

    import chat.runtime

    assert "serving_cast" not in inspect.getsource(chat.runtime)


def test_relaxation_result_type_is_unchanged():
    result, _ = _certified_outcome()
    assert isinstance(result, RelaxationResult)
    assert result.psi_steady.flags.writeable is False
