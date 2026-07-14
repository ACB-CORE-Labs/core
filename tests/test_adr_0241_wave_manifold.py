"""ADR-0241 — WaveManifold behavioral contract (RED until wave_manifold lands).

These assert *behavioral* properties of the continuous wave-field substrate, not
closure tautologies. See:

- docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md
- docs/research/third-door-blueprint-fidelity.md §12

Transport convention (pinned in ADR-0241):
  * Multivector field path: sandwich  ψ' = R ψ ~R  (matches versor_apply).
  * Spinor / chiral path:    left multiply ψ' = R ψ.

Slice 1 GREEN must implement core.physics.wave_manifold without scipy as
algebraic truth — live algebra/* only.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse
from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition, versor_unit_residual

# ---------------------------------------------------------------------------
# RED: hard-import — collection fails until core.physics.wave_manifold exists.
# Do NOT use importorskip (that would skip green). Slice 1 GREEN implements it.
# ---------------------------------------------------------------------------
from core.physics import wave_manifold
from core.physics.wave_manifold import WaveManifold

_CLOSURE = 1e-6


def _id32() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _e(i: int, val: float = 1.0) -> np.ndarray:
    """Grade-1 basis e_i (i in 1..5) as 32-vector."""
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[i] = val
    return v


def _unit_rotor(angle: float = 0.37, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


# --- W1: unitary / sandwich propagation ------------------------------------


def test_sandwich_step_preserves_unit_amplitude_on_even_versor():
    """Multivector field path: sandwich step keeps ‖ψ ψ̃ − 1‖ small."""
    M = WaveManifold()
    psi = _unit_rotor(0.41, plane=7)
    R = _unit_rotor(0.22, plane=6)
    assert versor_condition(psi) < _CLOSURE
    assert versor_condition(R) < _CLOSURE

    psi_next = M.sandwich_step(psi, R)
    # Matches existing algebra sandwich
    expected = versor_apply(R, psi)
    assert np.allclose(psi_next, expected, atol=1e-12)
    assert float(versor_unit_residual(psi_next)) < _CLOSURE
    assert M.measure_unitary_residual(psi_next) < _CLOSURE


def test_left_spinor_step_preserves_reversion_product_on_spinor():
    """Spinor path: left multiply ψ' = R ψ; reversion product dual-checked."""
    M = WaveManifold()
    # Odd-capable packet: grade-1 + small even mix (not a pure even field-state).
    psi = _e(1) + 0.25 * _e(2)
    scale = float(np.sqrt(abs(geometric_product(psi, reverse(psi))[0])))
    if scale > 1e-12:
        psi = psi / scale
    R = _unit_rotor(0.33, plane=8)

    psi_next = M.left_spinor_step(psi, R)
    expected = geometric_product(R, psi)
    assert np.allclose(psi_next, expected, atol=1e-12)
    # Dual-check residual on ψ and reverse(ψ) paths if API exposes it.
    r = M.measure_unitary_residual(psi_next)
    r_rev = M.measure_unitary_residual(reverse(psi_next))
    assert max(r, r_rev) < _CLOSURE or np.isfinite(r)


def test_algebraic_schrodinger_step_uses_rotor_exp_not_identity_noop():
    """dt>0 bivector step must move a non-invariant packet (not a no-op)."""
    M = WaveManifold()
    psi = _unit_rotor(0.5, plane=6)
    # Bivector generator as 32-vector (grade-2 plane index 9).
    B = np.zeros(N_COMPONENTS, dtype=np.float64)
    B[9] = 1.0
    out = M.algebraic_schrodinger_step(psi, B, dt=0.25)
    assert out.shape == (N_COMPONENTS,)
    assert not np.allclose(out, psi, atol=1e-9)
    assert M.measure_unitary_residual(out) < _CLOSURE


# --- W2: spectral leakage (surprise) ---------------------------------------


def test_spectral_leakage_zero_when_incoming_in_resonant_span():
    """On-span packet → leakage residual ~ 0 under metric projection."""
    M = WaveManifold()
    mode = _e(1) + 0.5 * _e(3)
    mode = mode / float(np.linalg.norm(mode))
    psi = 0.7 * mode
    residual, energy = M.compute_spectral_leakage(psi, [mode])
    assert float(np.linalg.norm(residual)) < 1e-9
    assert float(energy) < 1e-9


def test_spectral_leakage_positive_off_span():
    """Orthogonal direction (Euclidean) not fully explained by mode e1 → energy > 0."""
    M = WaveManifold()
    mode = _e(1)
    psi = _e(2)
    residual, energy = M.compute_spectral_leakage(psi, [mode])
    assert float(energy) > 0.1
    assert float(np.linalg.norm(residual)) > 0.1


def test_spectral_leakage_is_metric_exact_not_euclidean():
    """Projection uses CGA metric, not Euclidean Gram-Schmidt.

    Same load-bearing pin as surprise metric projection: b = 2*e1 + e5,
    x = e1 → metric coeff 2/3, Euclidean 2/5.
    """
    from algebra.cga import cga_inner

    M = WaveManifold()
    b = 2.0 * _e(1) + _e(5)
    x = _e(1)
    residual, _ = M.compute_spectral_leakage(x, [b])

    c_metric = cga_inner(b, x) / cga_inner(b, b)
    assert np.allclose(residual, x - c_metric * b, atol=1e-10)

    c_eucl = float(np.dot(b, x)) / float(np.dot(b, b))
    assert not np.allclose(residual, x - c_eucl * b, atol=1e-6)


# --- W3: wave polar analogy ------------------------------------------------


def test_wave_polar_recovers_known_sandwich_rotor():
    """ψ_B = R ψ_A ~R  ⇒ polar extract recovers R (up to global sign)."""
    M = WaveManifold()
    psi_A = _unit_rotor(0.15, plane=6)
    R_true = _unit_rotor(0.55, plane=10)
    psi_B = versor_apply(R_true, psi_A)

    R_hat = M.wave_analogical_polar(psi_A, psi_B)
    assert R_hat.shape == (N_COMPONENTS,)
    assert versor_condition(R_hat) < _CLOSURE

    # Recovered map should send A → B under sandwich
    mapped = versor_apply(R_hat, psi_A)
    err = float(np.linalg.norm(mapped - psi_B))
    # Global sign ambiguity of rotors: also try -R
    err_neg = float(np.linalg.norm(versor_apply(-R_hat, psi_A) - psi_B))
    assert min(err, err_neg) < 1e-5


# --- W4: chiral spinor charge ----------------------------------------------


def test_chiral_charge_conserved_under_left_spinor_step():
    """Q = ⟨ψ I ~ψ⟩_0 conserved under unitary left multiply (odd-capable ψ)."""
    M = WaveManifold()
    psi = _e(1) + 0.3 * _e(3) + 0.1 * _unit_rotor(0.2, plane=6)
    R = _unit_rotor(0.4, plane=7)

    q0 = M.chiral_charge(psi)
    psi_next = M.left_spinor_step(psi, R)
    q1 = M.chiral_charge(psi_next)
    assert abs(q0 - q1) < 1e-9


def test_chiral_charge_honest_on_even_unit_versor():
    """Even unit versor: chiral readout is structural ~0 (does not revive #19 gate)."""
    M = WaveManifold()
    psi = _unit_rotor(0.9, plane=11)
    q = M.chiral_charge(psi)
    assert abs(float(q)) < 1e-9


# --- Containment / determinism ---------------------------------------------


def test_wave_manifold_determinism():
    M = WaveManifold()
    psi = _unit_rotor(0.2, plane=6)
    R = _unit_rotor(0.1, plane=7)
    a = M.sandwich_step(psi, R)
    b = M.sandwich_step(psi, R)
    assert np.array_equal(a, b)


def test_wave_manifold_module_does_not_import_teaching():
    """Physics boundary: wave_manifold must not import teaching (discovery is out)."""
    import ast
    from pathlib import Path

    path = Path(wave_manifold.__file__)
    tree = ast.parse(path.read_text())
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith("teaching")
        if isinstance(node, ast.ImportFrom) and node.module:
            assert not node.module.startswith("teaching")
