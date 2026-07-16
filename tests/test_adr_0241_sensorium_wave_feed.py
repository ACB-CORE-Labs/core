"""D7 sensorium → ψ feed (I-04 boundary) pins.

ADR-0241 cohesion: modality packets compile to Cl(4,1) wave fields;
multimodal resonance uses WaveManifold.phase_correlation only.

Honest fake packets when real compilers are not under test.
No cosine / ANN / sklearn neighbors.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.sensorium_wave_feed import (
    ModalityPacket,
    compile_packet_to_psi,
    fake_deterministic_packet,
    packet_from_compilation_unit,
    packet_from_compiler_versor,
    phase_correlate,
    superpose_packets,
)
from core.physics.wave_manifold import WaveManifold

_ROOT = Path(__file__).resolve().parents[1]
_MODULE = _ROOT / "core/physics/sensorium_wave_feed.py"
_CLOSURE = 1e-6


def _closed(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


# --- compile / packet --------------------------------------------------------


def test_compile_packet_to_psi_from_modality_packet():
    coeffs = _closed(0.41, plane=7)
    packet = ModalityPacket(modality_id="vision", coefficients=coeffs)
    psi = compile_packet_to_psi(packet)
    assert psi.shape == (N_COMPONENTS,)
    assert psi.dtype == np.float64
    assert float(np.linalg.norm(psi - coeffs)) < 1e-15
    # Fresh copy — not the same buffer
    assert psi is not packet.coefficients


def test_compile_packet_to_psi_from_dict():
    coeffs = _closed(0.22, plane=8)
    psi = compile_packet_to_psi(
        {"modality_id": "audio", "coefficients": coeffs.tolist()}
    )
    assert psi.shape == (32,)
    assert float(np.linalg.norm(psi - coeffs)) < 1e-12


def test_compile_packet_accepts_modality_and_psi_keys():
    coeffs = _closed(0.15, plane=6)
    psi = compile_packet_to_psi({"modality": "text", "psi": coeffs})
    assert float(np.linalg.norm(psi - coeffs)) < 1e-15


def test_compile_packet_rejects_wrong_shape():
    with pytest.raises(ValueError, match="shape"):
        ModalityPacket(modality_id="x", coefficients=np.zeros(16))


def test_compile_packet_rejects_empty_modality_id():
    with pytest.raises(ValueError, match="modality_id"):
        ModalityPacket(modality_id="  ", coefficients=_closed())


def test_compile_packet_rejects_incomplete_dict():
    with pytest.raises(ValueError, match="modality_id"):
        compile_packet_to_psi({"coefficients": _closed()})


# --- superpose ---------------------------------------------------------------


def test_superpose_packets_is_sum_of_compiled():
    a = fake_deterministic_packet("audio", angle=0.2, plane=6)
    b = fake_deterministic_packet("vision", angle=0.55, plane=8)
    total = superpose_packets([a, b])
    expected = compile_packet_to_psi(a) + compile_packet_to_psi(b)
    assert float(np.linalg.norm(total - expected)) < 1e-15


def test_superpose_packets_empty_refused():
    with pytest.raises(ValueError, match="empty"):
        superpose_packets([])


# --- phase correlate (I-04) --------------------------------------------------


def test_phase_correlate_delegates_to_wave_manifold():
    a = _closed(0.2, plane=6)
    b = _closed(0.55, plane=8)
    M = WaveManifold()
    rho_direct = M.phase_correlation(a, b)
    rho_feed = phase_correlate(a, b, manifold=M)
    assert abs(rho_feed - rho_direct) < 1e-15


def test_phase_correlate_symmetric():
    a = compile_packet_to_psi(fake_deterministic_packet("text", angle=0.3, plane=6))
    b = compile_packet_to_psi(fake_deterministic_packet("audio", angle=0.7, plane=9))
    assert abs(phase_correlate(a, b) - phase_correlate(b, a)) < 1e-12
    assert phase_correlate(a, a) > 0.5


def test_cross_modal_fake_packets_phase_correlate():
    """I-04 feed path: two modalities → ψ → algebraic ρ (not cosine)."""
    audio = fake_deterministic_packet("audio", angle=0.25, plane=6)
    vision = fake_deterministic_packet("vision", angle=0.25, plane=6)
    # Same closed rotor → strong self-like correlation across modality tags
    rho_same = phase_correlate(
        compile_packet_to_psi(audio),
        compile_packet_to_psi(vision),
    )
    assert rho_same > 0.5

    other = fake_deterministic_packet("vision", angle=1.1, plane=10)
    rho_diff = phase_correlate(
        compile_packet_to_psi(audio),
        compile_packet_to_psi(other),
    )
    # Distinct planes/angles are not required to be lower, but path must run.
    assert isinstance(rho_diff, float)


# --- fake deterministic fixtures ---------------------------------------------


def test_fake_deterministic_packet_closed_and_stable():
    p1 = fake_deterministic_packet("sensorimotor", angle=0.4, plane=7)
    p2 = fake_deterministic_packet("sensorimotor", angle=0.4, plane=7)
    assert p1.modality_id == "sensorimotor"
    assert float(np.linalg.norm(p1.coefficients - p2.coefficients)) == 0.0
    assert versor_condition(p1.coefficients) < _CLOSURE


def test_fake_deterministic_matches_make_rotor():
    angle, plane = 0.37, 11
    packet = fake_deterministic_packet("motor", angle=angle, plane=plane)
    expected = make_rotor_from_angle(angle, bivector_idx=plane)
    assert float(np.linalg.norm(packet.coefficients - expected)) < 1e-15


# --- hygiene: no approx neighbors / cosine -----------------------------------


def test_module_forbids_approx_neighbor_and_cosine_imports():
    """I-04: no faiss / hnsw / annoy / sklearn / cosine_similarity stack."""
    src = _MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    banned_roots = {
        "faiss",
        "hnswlib",
        "annoy",
        "sklearn",
        "scipy",
        "sklearn.neighbors",
    }
    banned_names = {
        "cosine_similarity",
        "NearestNeighbors",
        "cosine",
        "cdist",
    }
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                assert root not in banned_roots, f"banned import {alias.name}"
                assert alias.name not in banned_roots
        if isinstance(node, ast.ImportFrom) and node.module:
            root = node.module.split(".")[0]
            assert root not in banned_roots, f"banned from {node.module}"
            assert node.module not in banned_roots
            for alias in node.names:
                assert alias.name not in banned_names
        if isinstance(node, ast.Attribute):
            assert node.attr not in banned_names
        if isinstance(node, ast.Name):
            assert node.id not in banned_names
    # Source-level ban on cosine similarity wording as implementation path
    assert "cosine_similarity" not in src
    assert "NearestNeighbors" not in src


def test_phase_correlate_source_only_calls_phase_correlation():
    """phase_correlate body must call WaveManifold.phase_correlation only."""
    src = _MODULE.read_text(encoding="utf-8")
    tree = ast.parse(src)
    func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "phase_correlate":
            func = node
            break
    assert func is not None, "phase_correlate not found"
    call_attrs: list[str] = []
    for node in ast.walk(func):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            call_attrs.append(node.func.attr)
    assert "phase_correlation" in call_attrs
    # No alternate resonance / similarity calls inside the function
    forbidden = {
        "cosine_similarity",
        "resonant_recall",
        "resonant_reconstruct",
        "dot",
        "norm",
    }
    for attr in call_attrs:
        assert attr not in forbidden, f"phase_correlate must not call .{attr}"


# --- Real modality compilers → ψ → ρ (I-04 close) ----------------------------


def test_real_audio_and_vision_compilers_feed_phase_correlate():
    """I-04: live audio + vision compilers → ModalityPacket → ψ → algebraic ρ.

    Not fake_deterministic_packet: exercises real sensorium/* compilers.
    """
    from sensorium.audio.compiler import AudioCompiler
    from sensorium.vision import VisionCompiler, canonicalize_image
    from sensorium.vision.grid import iter_tile_signals

    sr = 24_000
    n = int(sr * 0.35)
    t = np.arange(n, dtype=np.float64) / sr
    tone = (0.5 * np.sin(2 * np.pi * 160.0 * t)).astype(np.float32)
    audio_unit = AudioCompiler().compile(tone, sr)
    assert audio_unit.versor.shape == (N_COMPONENTS,)
    assert audio_unit.versor_condition < _CLOSURE

    # Vision tile from a deterministic synthetic image (same pattern as vision tests).
    x = np.linspace(0.0, 1.0, 32, dtype=np.float32)
    y = np.linspace(0.0, 1.0, 32, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    image = np.stack([xx, yy, 1.0 - xx], axis=2).astype(np.float32)
    tile = iter_tile_signals(canonicalize_image(image))[0]
    vision_unit = VisionCompiler().compile_tile(tile)
    assert vision_unit.versor.shape == (N_COMPONENTS,)
    assert vision_unit.versor_condition < _CLOSURE

    audio_pkt = packet_from_compilation_unit("audio", audio_unit)
    vision_pkt = packet_from_compiler_versor("vision", vision_unit.versor)
    psi_a = compile_packet_to_psi(audio_pkt)
    psi_v = compile_packet_to_psi(vision_pkt)
    assert psi_a.dtype == np.float64
    assert psi_v.dtype == np.float64
    assert versor_condition(psi_a) < _CLOSURE
    assert versor_condition(psi_v) < _CLOSURE

    total = superpose_packets([audio_pkt, vision_pkt])
    assert total.shape == (N_COMPONENTS,)
    assert float(np.linalg.norm(total - (psi_a + psi_v))) < 1e-12

    rho = phase_correlate(psi_a, psi_v)
    assert isinstance(rho, float)
    # Algebraic ρ = ⟨ψ_A ~ψ_B + ψ_B ~ψ_A⟩_0 (not cosine): unit rotors self-correlate ≈ 2.
    assert phase_correlate(psi_a, psi_a) > 1.5
    assert phase_correlate(psi_v, psi_v) > 1.5
    # Cross-modal path must run and return a finite float (no cosine/ANN).
    assert np.isfinite(rho)


def test_packet_from_compilation_unit_rejects_non_units():
    with pytest.raises(TypeError, match="versor"):
        packet_from_compilation_unit("audio", object())
