"""ADR-0246 §4.1/§4.3 — per-turn IdentityActionRecord telemetry pins.

Pins the pure record builder (`build_identity_action_record`), its full-SHA-256
digests (§4.3 — no truncation, no `default=str`), the conditional-population
discipline (never built unless the wave/action surface actually ran), the
minimal serve wiring (IdentityScore.action_record, populated only when
admission_policy is supplied), and the telemetry serializer's conditional
emission (wave_mode_active AND action_surface_active both required — flag-off
wire format is provably unchanged).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.identity import IdentityCheck, IdentityManifold, ValueAxis
from core.physics.identity_action import (
    AdmissionPolicy,
    build_identity_action_record,
)
from core.physics.identity_manifold import IdentityManifoldGeometry
from chat.telemetry import serialize_turn_event

_E14 = 8


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
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


def _manifold():
    return IdentityManifold(
        value_axes=(
            ValueAxis(name="truthfulness", direction=(1.0, 0.0, 0.0)),
            ValueAxis(name="coherence", direction=(0.0, 1.0, 0.0)),
            ValueAxis(name="reverence", direction=(0.0, 0.0, 1.0)),
        )
    )


class _Trajectory:
    trajectory_id = "record_test"
    total_coherence_delta = 0.0
    frames = ()


# --- pure builder pins ---------------------------------------------------------


def test_record_schema_and_shape(geometry):
    policy = AdmissionPolicy.placeholder_default()
    record = build_identity_action_record(
        geometry, _identity_versor(), policy, trajectory_id="t1", turn_id=3,
    )
    d = record.as_dict()
    assert d["schema_version"] == "identity_action_v1"
    assert d["turn_id"] == 3 and d["trajectory_id"] == "t1"
    assert set(d["typed_residual_energy"]) == {
        "spatial_foreign", "boost_like", "null_or_conformal", "unclassified",
    }
    assert len(d["A_raw"]) == 3 and len(d["A_raw"][0]) == 3
    assert d["admitted"] is True and d["refusal_reason"] is None
    assert d["lawful_action"] == "I"
    assert d["path_break"] is False


def test_record_refusal_reason_and_lawful_action_on_attack(geometry):
    policy = AdmissionPolicy.placeholder_default()
    record = build_identity_action_record(geometry, _rotor(_E14, 1.5), policy)
    assert record.admitted is False
    assert record.refusal_reason is not None
    assert ">" in record.refusal_reason  # e.g. "d_orth>orth_tol;..."
    assert record.lawful_action == "none"


def test_record_digests_are_full_sha256_and_deterministic(geometry):
    policy = AdmissionPolicy.placeholder_default()
    r1 = build_identity_action_record(geometry, _identity_versor(), policy)
    r2 = build_identity_action_record(geometry, _identity_versor(), policy)
    assert len(r1.field_digest) == 64 and len(r1.record_digest()) == 64
    int(r1.field_digest, 16)
    int(r1.record_digest(), 16)
    assert r1.field_digest == r2.field_digest
    assert r1.record_digest() == r2.record_digest()


def test_record_digest_changes_with_content(geometry):
    policy = AdmissionPolicy.placeholder_default()
    r_id = build_identity_action_record(geometry, _identity_versor(), policy)
    r_atk = build_identity_action_record(geometry, _rotor(_E14, 1.5), policy)
    assert r_id.record_digest() != r_atk.record_digest()
    assert r_id.field_digest != r_atk.field_digest


def test_policy_version_id_is_full_sha256_and_reflects_calibration_state(geometry):
    p1 = AdmissionPolicy.placeholder_default()
    assert len(p1.version_id()) == 64
    int(p1.version_id(), 16)
    p2 = AdmissionPolicy.placeholder_default()
    assert p1.version_id() == p2.version_id()  # deterministic
    from dataclasses import replace
    p3 = replace(p1, gamma_id=0.5)
    assert p3.version_id() != p1.version_id()  # threshold change -> new version


def test_manifold_content_digest_changes_on_axis_change():
    from core.physics.identity import manifold_content_digest
    m1 = _manifold()
    m2 = IdentityManifold(value_axes=_manifold().value_axes[:2])
    d1 = manifold_content_digest(m1)
    d2 = manifold_content_digest(m2)
    assert len(d1) == 64 and d1 != d2
    assert manifold_content_digest(m1) == d1  # deterministic


# --- serve wiring: IdentityScore.action_record ---------------------------------


def test_flag_off_action_record_is_none():
    check = IdentityCheck()
    score = check.check(_Trajectory(), _manifold(), wave_field=_identity_versor())
    assert score.action_record is None


def test_flag_on_populates_action_record():
    check = IdentityCheck()
    score = check.check(
        _Trajectory(), _manifold(), wave_field=_identity_versor(),
        admission_policy=AdmissionPolicy.placeholder_default(),
    )
    assert score.action_record is not None
    assert score.action_record.trajectory_id == "record_test"
    assert score.action_record.admitted is True


# --- telemetry serialization: conditional emission -----------------------------


class _Event:
    turn = 1
    identity_score = None


def test_telemetry_flag_off_has_no_action_fields():
    check = IdentityCheck()
    ev = _Event()
    ev.identity_score = check.check(
        _Trajectory(), _manifold(), wave_field=_identity_versor()
    )
    payload = serialize_turn_event(ev)
    assert "identity_action_admitted" not in payload
    assert "identity_d_orth" not in payload
    assert "identity_d_stab" not in payload


def test_telemetry_flag_on_emits_action_surface_fields():
    check = IdentityCheck()
    ev = _Event()
    ev.identity_score = check.check(
        _Trajectory(), _manifold(), wave_field=_rotor(_E14, 1.5),
        admission_policy=AdmissionPolicy.placeholder_default(),
    )
    payload = serialize_turn_event(ev)
    assert payload["identity_action_admitted"] is False
    assert isinstance(payload["identity_d_orth"], float)
    assert isinstance(payload["identity_d_stab"], float)
    assert "identity_action_record_digest" in payload
    assert len(payload["identity_action_record_digest"]) == 64
