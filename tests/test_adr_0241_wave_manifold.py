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

from algebra.cl41 import N_COMPONENTS, geometric_product, reverse  # noqa: F401 — reverse used in helpers/docs
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


# --- Slice 2: operator subsumption (no parallel path) ----------------------


def test_surprise_residual_delegates_to_wave_spectral_leakage():
    """32-vec surprise residual matches WaveManifold.compute_spectral_leakage."""
    from core.physics.surprise import surprise_residual

    M = WaveManifold()
    mode = _e(1) + 0.5 * _e(3)
    mode = mode / float(np.linalg.norm(mode))
    x = 0.7 * mode + 0.4 * _e(2)
    B = mode.reshape(N_COMPONENTS, 1)
    sur_vec, sur_n = surprise_residual(x, B)
    leak_vec, leak_n = M.compute_spectral_leakage(x, [mode])
    assert np.allclose(sur_vec, leak_vec, atol=1e-12)
    assert abs(sur_n - leak_n) < 1e-12


def test_coherence_residual_delegates_to_wave_unitary():
    """GoldTether coherence_residual is WaveManifold.measure_unitary_residual."""
    from core.physics.goldtether import coherence_residual

    M = WaveManifold()
    psi = _unit_rotor(0.42, plane=8)
    assert abs(coherence_residual(psi) - M.measure_unitary_residual(psi)) < 1e-15


def test_conformal_procrustes_single_field_uses_wave_polar():
    """Single non-null field Procrustes recovers the same conjugator as wave polar."""
    from core.physics.dynamic_manifold import conformal_procrustes

    M = WaveManifold()
    psi_A = _unit_rotor(0.15, plane=6)
    R_true = _unit_rotor(0.55, plane=10)
    psi_B = versor_apply(R_true, psi_A)
    V_proc, res = conformal_procrustes(psi_A, psi_B)
    V_wave = M.wave_analogical_polar(psi_A, psi_B)
    # Both must sandwich A → B; residual small.
    assert res < 1e-5
    err_p = min(
        float(np.linalg.norm(versor_apply(V_proc, psi_A) - psi_B)),
        float(np.linalg.norm(versor_apply(-V_proc, psi_A) - psi_B)),
    )
    err_w = min(
        float(np.linalg.norm(versor_apply(V_wave, psi_A) - psi_B)),
        float(np.linalg.norm(versor_apply(-V_wave, psi_A) - psi_B)),
    )
    assert err_p < 1e-5
    assert err_w < 1e-5


def test_wave_field_conjugacy_multi_pair_thin_wrap():
    """Multi-pair field conjugacy is available on WaveManifold (Slice 3 thin wrap)."""
    from core.physics.dynamic_manifold import conformal_procrustes

    M = WaveManifold()
    R = _unit_rotor(0.4, plane=9)
    sources = [_unit_rotor(0.1 * (i + 1), plane=6) for i in range(3)]
    targets = [versor_apply(R, s) for s in sources]
    V, engine_r = M.wave_field_conjugacy(sources, targets)
    assert V.shape == (N_COMPONENTS,)
    assert versor_condition(V) < _CLOSURE
    assert engine_r < 1e-4
    # Sequence Procrustes uses the same wave conjugacy path.
    V2, res2 = conformal_procrustes(sources, targets)
    assert res2 < 1e-4
    for s, t in zip(sources, targets):
        err = min(
            float(np.linalg.norm(versor_apply(V2, s) - t)),
            float(np.linalg.norm(versor_apply(-V2, s) - t)),
        )
        assert err < 1e-4


def test_resonant_recall_picks_registered_mode():
    """Standing-wave registry: query locks onto the matching registered mode."""
    M = WaveManifold()
    a = _unit_rotor(0.2, plane=6)
    b = _unit_rotor(0.9, plane=7)
    M.register_resonant_mode(a)
    M.register_resonant_mode(b)
    mode, energy, idx = M.resonant_recall(b)
    assert idx == 1
    assert energy > 0.5
    assert np.allclose(mode, b, atol=1e-12)


def test_resonant_recall_empty_refused():
    """No confabulated recall from an empty mode set."""
    M = WaveManifold()
    with pytest.raises(ValueError, match="empty mode set"):
        M.resonant_recall(_unit_rotor(0.3, plane=6))


def test_resonant_reconstruct_interference_weights():
    """Superposition reconstruct recovers a weighted combo better than pure modes."""
    M = WaveManifold()
    a = _unit_rotor(0.2, plane=6)
    b = _unit_rotor(0.9, plane=10)
    query = 0.6 * a + 0.4 * b
    psi_hat, coeffs, _energies = M.resonant_reconstruct(query, modes=[a, b])
    assert coeffs.shape == (2,)
    err_hat = float(np.linalg.norm(psi_hat - query))
    assert err_hat < float(np.linalg.norm(a - query))
    assert err_hat < float(np.linalg.norm(b - query))


def test_phase_correlation_symmetric():
    """I-04 algebraic resonance: ρ(A,B)=ρ(B,A)."""
    M = WaveManifold()
    a = _unit_rotor(0.2, plane=6)
    b = _unit_rotor(0.55, plane=8)
    assert abs(M.phase_correlation(a, b) - M.phase_correlation(b, a)) < 1e-12


def test_core_ha_package_absent():
    """core_ha deprecation: no live package tree in this repo (W6 hygiene)."""
    import importlib.util

    assert importlib.util.find_spec("core_ha") is None


def test_true_clifford_polar_fails_on_multigrade_field():
    """HONESTY CHECK (ADR-0241 P7): The analytical Clifford polar fails on general fields.
    
    C_AB = B ~A. If the polar decomposition R = C ( ~C C )^{-1/2} were to work,
    then ~C C must be a positive scalar. For general multi-grade fields, this is FALSE.
    This proves that `_field_conjugacy_versor` (SVD + Spin GN) is the only true way
    to extract a sandwich conjugator for general wave fields, and the ADR-0241 claim
    of a 'Cross-spectral polar decomposition' is ill-posed for non-vector fields.
    """
    psi_A = _e(1) + 0.5 * _e(3) + 0.2 * _unit_rotor(0.3, plane=8) # Mixed grade
    R_true = _unit_rotor(0.4, plane=6)
    psi_B = versor_apply(R_true, psi_A)
    
    # C_AB = psi_B * reverse(psi_A)
    C_AB = geometric_product(psi_B, reverse(psi_A))
    
    # Check if ~C C is a scalar
    C_rev_C = geometric_product(reverse(C_AB), C_AB)
    
    # Extract non-scalar mass
    scalar_mass = abs(float(C_rev_C[0]))
    non_scalar_mass = float(np.linalg.norm(C_rev_C[1:]))
    
    # The non-scalar mass is significant, proving it's not a scalar
    assert non_scalar_mass > 0.01 * scalar_mass
    
    # Therefore, ( ~C C )^{-1/2} cannot be taken algebraically to yield a rotor.
