"""ADR-0246 slice 0 — pins for the mismatch-diagnostic instruments.

Ground-truth expectations from the preflight brief §6.1: each synthetic
construction must land in the correct mechanism class, the induced action must
be exact on known rotors, typed residual channels must fire on the right blade,
and the diagnostic must remain eval-only (no serving imports, no flag changes).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, basis_vector
from evals.adr_0246_mismatch_diagnostic import (
    IDX_E4,
    IDX_E5,
    IDX_E12,
    IDX_E14,
    IDX_E15,
    build_evidence_packet,
    d_orth,
    d_stab,
    decompose_trace,
    default_geometry,
    induced_action,
    path_accumulation_analysis,
    semantic_coupling_analysis,
    synthetic_traces,
    typed_residual_channels,
    versor_plane_occupancy,
)
from evals.adr_0244_gamma_calibration import _boost, _rotor


@pytest.fixture(scope="module")
def geometry():
    return default_geometry()


def test_blade_index_pins():
    """The channel map depends on the cl41 layout; pin it against the algebra."""
    for k, expected_idx in ((0, 1), (1, 2), (2, 3), (3, IDX_E4), (4, IDX_E5)):
        vec = basis_vector(k)
        assert vec[expected_idx] == 1.0
        assert np.count_nonzero(vec) == 1


def test_identity_versor_action_is_identity(geometry):
    identity = np.zeros(N_COMPONENTS, dtype=np.float64)
    identity[0] = 1.0
    action = induced_action(geometry, identity)
    assert np.allclose(action, np.eye(3), atol=1e-12)
    assert d_orth(geometry, action) < 1e-12
    assert d_stab(geometry, action) < 1e-12


def test_inplane_rotation_action_is_exact_rotation_matrix(geometry):
    theta = 0.3
    action = induced_action(geometry, _rotor(IDX_E12, theta))
    expected = np.eye(3)
    expected[0, 0] = expected[1, 1] = np.cos(theta)
    # e12 rotor sandwich rotates the e1/e2 plane by theta.
    expected[1, 0] = np.sin(theta)
    expected[0, 1] = -np.sin(theta)
    assert np.allclose(np.abs(action), np.abs(expected), atol=1e-6)
    assert d_orth(geometry, action) < 1e-6  # rotation is a G-isometry
    assert d_stab(geometry, action) > 0.05  # but NOT the identity action


def test_permutation_and_inversion_are_in_span_unlawful(geometry):
    for versor in (_rotor(IDX_E12, np.pi / 2.0), _rotor(IDX_E12, np.pi)):
        d = decompose_trace("t", "synthetic", versor, geometry)
        assert d.leakage_rms < 1e-6  # invisible to leakage
        assert d.d_stab > 0.05  # visible to the stabilizer distance
        assert d.mechanism == "in_span_unlawful"


def test_tilt_fires_e4_channel_only(geometry):
    channels = typed_residual_channels(geometry, _rotor(IDX_E14, 1.5))
    assert channels["null_or_conformal"] > 0.1
    assert channels["boost_like"] == pytest.approx(0.0, abs=1e-12)
    assert channels["unclassified"] < 1e-9
    d = decompose_trace("t", "synthetic", _rotor(IDX_E14, 1.5), geometry)
    assert d.mechanism == "foreign_leakage"
    assert "null_or_conformal" in d.mechanism_detail


def test_boost_fires_e5_channel_and_d_orth(geometry):
    versor = _boost(IDX_E15, 1.2)
    channels = typed_residual_channels(geometry, versor)
    assert channels["boost_like"] > 0.1
    assert channels["null_or_conformal"] == pytest.approx(0.0, abs=1e-12)
    action = induced_action(geometry, versor)
    assert d_orth(geometry, action) > 0.05  # boost is not a G-isometry
    d = decompose_trace("t", "synthetic", versor, geometry)
    assert d.mechanism == "foreign_leakage"
    assert "boost_like" in d.mechanism_detail


def test_synthetic_suite_classification_ground_truth(geometry):
    expected = {
        "identity_versor": "lawful_in_span",
        "rot_e12_0.3": "in_span_unlawful",
        "rot_e12_halfpi_permutation": "in_span_unlawful",
        "rot_e12_pi_inversion": "in_span_unlawful",
        "tilt_e14_1.5": "foreign_leakage",
        "tilt_e24_0.6": "foreign_leakage",
        "boost_e15_1.2": "foreign_leakage",
        "boost_e25_0.8": "foreign_leakage",
        "mild_inplane_drift_0.02": "lawful_in_span",
    }
    for label, versor in synthetic_traces():
        d = decompose_trace(label, "synthetic", versor, geometry)
        assert d.mechanism == expected[label], label


def test_plane_occupancy_localizes_the_mechanism():
    occ = versor_plane_occupancy(_rotor(IDX_E12, 0.5))
    assert occ["in_span_planes"] == pytest.approx(1.0)
    assert occ["e4_mixing_planes"] == 0.0
    occ = versor_plane_occupancy(_rotor(IDX_E14, 0.5))
    assert occ["e4_mixing_planes"] == pytest.approx(1.0)
    occ = versor_plane_occupancy(_boost(IDX_E15, 0.5))
    assert occ["e5_mixing_planes"] == pytest.approx(1.0)


def test_path_accumulation_detects_compounding_small_drift(geometry):
    # 30 mild in-plane steps, each individually inside D_STAB_TOL, compound
    # past it — exactly the brief §3.4 slow-drift failure mode.
    steps = [
        decompose_trace(f"s{i}", "synthetic", _rotor(IDX_E12, 0.02), geometry)
        for i in range(30)
    ]
    report = path_accumulation_analysis(steps)
    assert report["lawful_chain_exists"] is True  # each step ≈ I
    assert report["per_turn_d_stab_max"] <= 0.05
    assert report["raw_path_d_stab_curve"][-1] > 0.05
    assert report["accumulation_is_the_mechanism"] is True


def test_path_accumulation_not_blamed_when_per_turn_already_large(geometry):
    steps = [
        decompose_trace(f"s{i}", "synthetic", _rotor(IDX_E14, 1.5), geometry)
        for i in range(3)
    ]
    report = path_accumulation_analysis(steps)
    assert report["lawful_chain_exists"] is False
    assert report["accumulation_is_the_mechanism"] is False


def test_semantic_coupling_detects_a_preserving_ensemble(geometry):
    # Versors that DO preserve the declared frame: coupling analysis must
    # report the frame as preferentially preserved (leakage 0 < any control).
    versors = [(f"v{i}", _rotor(IDX_E12, 0.1 * (i + 1))) for i in range(5)]
    report = semantic_coupling_analysis(versors)
    assert report["declared_frame_mean_leakage"] < 1e-9
    assert report["declared_frame_preferentially_preserved"] is True


def test_semantic_coupling_detects_an_uncoupled_ensemble(geometry):
    # Versors tilting/boosting out of span: the declared frame should NOT
    # stand out against the random-frame control ensemble.
    versors = [
        ("t1", _rotor(IDX_E14, 1.5)),
        ("t2", _rotor(IDX_E14, 0.9)),
        ("b1", _boost(IDX_E15, 1.2)),
        ("b2", _boost(IDX_E15, 0.7)),
    ]
    report = semantic_coupling_analysis(versors)
    assert report["declared_frame_preferentially_preserved"] is False


def test_f32_transport_is_not_the_mechanism(geometry):
    # The f64→f32→f64 round-trip of any reference versor moves the induced
    # action by machine-epsilon scale — orders below the observed mismatch.
    for label, versor in synthetic_traces():
        d = decompose_trace(label, "synthetic", versor, geometry)
        assert d.f32_transport_delta < 1e-4, label


def test_packet_verdict_shape_offline():
    # Offline packet with synthetic stand-ins for the live suites: the packet
    # must assemble, count mechanisms, and emit the verdict block.
    benign = [("b0", _rotor(IDX_E14, 1.0)), ("b1", _boost(IDX_E15, 0.9))]
    paraphrase = [("p0", _rotor(IDX_E14, 1.1))]
    packet = build_evidence_packet(benign, paraphrase)
    assert packet["schema_version"] == "adr_0246_slice0_diagnostic_v1"
    verdict = packet["verdict"]
    assert verdict["dominant_benign_mechanism"] == "foreign_leakage"
    assert verdict["precision_transport_is_the_cause"] is False
    assert set(packet["suites"]) == {
        "synthetic",
        "adversarial",
        "benign",
        "paraphrase",
    }


def test_diagnostic_is_not_imported_by_serving():
    """A-04: chat/runtime.py must never import this eval package."""
    with open("chat/runtime.py", encoding="utf-8") as fh:
        source = fh.read()
    assert "adr_0246_mismatch_diagnostic" not in source


def test_gate_flag_and_bound_untouched():
    """Slice 0 changes no gate surface: flag default off, bound value pinned."""
    from core.config import RuntimeConfig
    from core.physics import identity

    assert RuntimeConfig().identity_wave_gate is False
    assert identity._WAVE_LEAKAGE_BOUND == 0.2126624458513829
