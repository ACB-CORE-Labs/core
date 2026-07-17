"""ADR-0243 §3 reference-prototype sketch-defect pins (SD-A, SD-B, SD-C).

Authority: docs/plans/adr-0243-implementation-plan.md §3 (sketch-defect ledger).
Precedent: PR #52 sketch-defect pins for the rejected Drive-draft re-implementation.

The ADR-0243 §3 Python prototype (``CognitiveLifecycleEngine``) contains
mathematical defects that make a verbatim port worthless or misleading. These
pins prove each defect with a deterministic counterexample so the sketch can
never be re-landed as-is:

SD-A  The sketch egress gate computes ``drift = |psi^T I^T psi - 1|`` with an
      antisymmetric ``I``. The quadratic form of an antisymmetric matrix is
      identically zero, so drift == 1 for EVERY state and the gate rejects
      everything — valid and invalid alike. A fail-always gate is the inverse
      of a hollow gate and equally worthless. The real residual is
      ``WaveManifold.measure_unitary_residual`` / ``goldtether.coherence_residual``.

SD-B  The sketch "relaxation" loop iterates ``R = expm(H @ I * dt)`` with
      renormalization. The generator's spectrum is (block-wise) purely
      imaginary, so iterates oscillate and nothing dissipates: the loop never
      settles into the minimum-energy eigenmode of H. Honest deterministic
      relaxation is the dissipative (imaginary-time) semigroup
      ``psi <- normalize(exp(-H dt) psi)`` — power iteration whose convergence
      rate is the spectral gap of H.

SD-C  The sketch's block matrix "I" ("central pseudoscalar proxy") is NOT the
      Cl(4,1) pseudoscalar action: it shares I^2 = -Id but is a different
      operator from left-multiplication by e0 e1 e2 e3 e4 in the real algebra.
      All algebra goes through ``algebra/`` — no component-shuffling proxies.

Deterministic fixtures only — no random spinors as truth.
"""

from __future__ import annotations

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product


def _sketch_proxy_i() -> np.ndarray:
    """The ADR-0243 §3 prototype's 'central pseudoscalar proxy' matrix."""
    proxy = np.zeros((N_COMPONENTS, N_COMPONENTS), dtype=np.float64)
    for i in range(N_COMPONENTS // 2):
        proxy[2 * i, 2 * i + 1] = 1.0
        proxy[2 * i + 1, 2 * i] = -1.0
    return proxy


def _expm_series(M: np.ndarray, terms: int = 60) -> np.ndarray:
    """Deterministic truncated-series matrix exponential (no scipy)."""
    out = np.eye(M.shape[0], dtype=np.float64)
    term = np.eye(M.shape[0], dtype=np.float64)
    for k in range(1, terms):
        term = term @ M / float(k)
        out = out + term
    return out


def _onehot(i: int) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[i] = 1.0
    return v


# --- SD-A: the sketch egress gate rejects every state -------------------------


def test_sd_a_sketch_egress_gate_rejects_every_state():
    proxy = _sketch_proxy_i()
    mixed = np.arange(1, N_COMPONENTS + 1, dtype=np.float64)
    mixed /= np.linalg.norm(mixed)
    candidates = [_onehot(0), _onehot(5), _onehot(31), mixed]

    for psi in candidates:
        # Exactly the sketch's egress computation.
        psi_rev = proxy.T @ psi
        norm_product = psi @ psi_rev
        drift = abs(norm_product - 1.0)
        # Antisymmetric quadratic form vanishes identically...
        assert abs(norm_product) < 1e-12
        # ...so the sketch gate rejects EVERYTHING, unit-norm states included.
        assert drift > 1e-6  # sketch epsilon_drift
        assert abs(drift - 1.0) < 1e-12


# --- SD-B: the sketch loop cannot relax; imaginary time can -------------------


def test_sd_b_sketch_loop_oscillates_while_imaginary_time_relaxes():
    energies = np.linspace(0.5, 4.0, N_COMPONENTS)
    hamiltonian = np.diag(energies)  # ground state = component 0
    psi0 = np.ones(N_COMPONENTS, dtype=np.float64)
    psi0 /= np.linalg.norm(psi0)

    # Exactly the sketch's relaxation loop: R = expm(H @ I * dt), 100 steps.
    propagator = _expm_series(hamiltonian @ _sketch_proxy_i() * 0.01)
    psi = psi0.copy()
    for _ in range(100):
        psi = propagator @ psi
        norm = np.linalg.norm(psi)
        if norm > 1e-12:
            psi /= norm
    sketch_ground_overlap = abs(psi[0])

    # Honest dissipative semigroup: psi <- normalize(exp(-H dt) psi).
    decay = np.exp(-energies * 0.5)
    phi = psi0.copy()
    for _ in range(200):
        phi = decay * phi
        phi /= np.linalg.norm(phi)
    imaginary_time_ground_overlap = abs(phi[0])

    # The sketch never concentrates on the ground state...
    assert sketch_ground_overlap < 0.9
    # ...while imaginary time converges to it (rate = spectral gap).
    assert imaginary_time_ground_overlap > 1.0 - 1e-8


# --- SD-C: the proxy matrix is not the Cl(4,1) pseudoscalar action ------------


def test_sd_c_proxy_matrix_is_not_the_pseudoscalar_action():
    # Real pseudoscalar e0 e1 e2 e3 e4 (0-indexed basis vectors, f64).
    pseudoscalar = _onehot(1)  # e0 lives at component 1
    for i in range(1, 5):
        pseudoscalar = geometric_product(pseudoscalar, _onehot(1 + i))

    # Left-multiplication-by-pseudoscalar as a 32x32 matrix.
    action = np.zeros((N_COMPONENTS, N_COMPONENTS), dtype=np.float64)
    for j in range(N_COMPONENTS):
        action[:, j] = geometric_product(pseudoscalar, _onehot(j))

    proxy = _sketch_proxy_i()
    identity = np.eye(N_COMPONENTS)
    # Both square to -Id (I5^2 = -1 in Cl(4,1)) — the proxy mimics the square...
    assert np.allclose(action @ action, -identity, atol=1e-12)
    assert np.allclose(proxy @ proxy, -identity, atol=1e-12)
    # ...but is a DIFFERENT operator: the actions disagree outright.
    assert float(np.max(np.abs(action - proxy))) > 0.5
