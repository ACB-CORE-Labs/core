"""Third-Door blueprint-fidelity ledger.

The ADR-0239 geometry suite (``test_adr_0239_dynamic_manifold.py``) only ever
exercises the *identity + single-plane rotor* regime — the one input class where
``rotor_power`` does not hit its non-simple-bivector identity fallback, and where
several assertions are tautologies (``residual >= 0``, ``reconstruction_residual
>= 0``). This file exercises the operators on realistic *composed* conformal
versors (products of rotations on distinct planes — what a real field state
looks like) and encodes the properties the Super-Blueprint / R&D-Revised
blueprints actually REQUIRE.

The blueprints are the rigorous artifact. Spec-property tests here are
behavioral (composed multi-plane inputs, residual < ε, peel-content pins).
Historical findings:
  #1  [RESOLVED by #23] supervised_blend no-op on composed versors.
  #2  [RESOLVED by #16] Cartan–Iwasawa null-point peel + Spin remainder.
  #3  [RESOLVED by #17] Kabsch-conformal Procrustes + field conjugacy.

See docs/research/third-door-blueprint-fidelity.md for the living scorecard.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import geometric_product, reverse
from algebra.null_point import dilator, translator
from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_apply, versor_condition
from core.physics.dynamic_manifold import cartan_iwasawa_factorize, conformal_procrustes
from core.physics.goldtether import GoldTetherMonitor


def _identity() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _composed_versor(planes: tuple[int, ...], seed: float) -> np.ndarray:
    """A realistic multi-plane conformal versor.

    The product of >=3 rotations on distinct bivector planes is a *non-simple*
    even versor (its grade-2 part squares to more than a scalar). This is the
    generic case for any field state built from a sequence of word-versors —
    and the case the ADR-0239 tests never cover.
    """
    v = _identity()
    for k, idx in enumerate(planes):
        angle = 0.3 + 0.13 * k + 0.05 * seed
        v = geometric_product(v, make_rotor_from_angle(angle, bivector_idx=idx))
    return v


# --- Finding #1: supervised_blend geodesic ----------------------------------
def test_supervised_blend_should_interpolate_composed_versors():
    a = _composed_versor((6, 7, 8, 10, 11), seed=1.0)
    b = _composed_versor((6, 7, 8, 10, 11), seed=2.0)
    mid = GoldTetherMonitor().supervised_blend(a, b, 0.5)
    # Spec: a midpoint interpolation is strictly between the endpoints.
    assert float(np.linalg.norm(mid - a)) > 1e-9, "mid collapsed onto source"
    assert float(np.linalg.norm(mid - b)) > 1e-9, "mid collapsed onto target"


# --- Finding #2: Cartan-Iwasawa decomposition -------------------------------

def test_cartan_iwasawa_should_reconstruct_composed_motion():
    """Super §2.2: multi-plane non-similarity factors without raise; residual < 1e-6.

    Planes (6,7,8) include e1∧e4 (blade 8) — not a pure Euclidean similarity —
    so the null-point peel falls through to remainder-as-rotor (R=V, T=I, D=I).
    """
    v = _composed_versor((6, 7, 8), seed=0.0)
    fac = cartan_iwasawa_factorize(v)  # must not raise
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    residual = float(np.linalg.norm(recon - v))
    assert residual < 1e-6, f"reconstruction residual {residual:.3e}"
    assert fac.reconstruction_residual < 1e-6
    for f in (fac.R, fac.T, fac.D):
        assert versor_condition(f) < 1e-6


def test_cartan_iwasawa_random_multiplane_never_raises():
    """50 fixed-seed random 3–4 plane products: closed factors, residual < 1e-6."""
    rng = np.random.default_rng(20260713)
    max_residual = 0.0
    for _ in range(50):
        n = int(rng.integers(3, 5))  # 3 or 4 planes
        planes = tuple(int(x) for x in rng.choice(np.arange(6, 16), size=n, replace=False))
        angles = rng.uniform(0.1, 1.0, size=n)
        v = _identity()
        for ang, p in zip(angles, planes):
            v = geometric_product(v, make_rotor_from_angle(float(ang), bivector_idx=int(p)))
        fac = cartan_iwasawa_factorize(v)
        for f in (fac.R, fac.T, fac.D):
            assert versor_condition(f) < 1e-6
        recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
        residual = float(np.linalg.norm(recon - v))
        assert residual < 1e-6
        assert fac.reconstruction_residual < 1e-6
        max_residual = max(max_residual, residual)
    assert max_residual < 1e-6


def test_cartan_iwasawa_pure_similarity_peel():
    """V = R*T*D with Euclidean R (planes 6,7,10), nontrivial T and D.

    Pins peel *content* (not residual alone — Spin remainder also has residual 0).
    """
    from algebra.null_point import recover_dilation, recover_translation

    R_e = geometric_product(
        make_rotor_from_angle(0.4, bivector_idx=6),
        make_rotor_from_angle(0.3, bivector_idx=7),
    )
    R_e = geometric_product(R_e, make_rotor_from_angle(0.25, bivector_idx=10))
    t_vec = np.array([0.5, -0.2, 0.1], dtype=np.float64)
    T = translator(t_vec)
    D = dilator(1.7)
    V = geometric_product(geometric_product(R_e, T), D)
    fac = cartan_iwasawa_factorize(V)
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    residual = float(np.linalg.norm(recon - V))
    assert residual < 1e-6, f"similarity peel residual {residual:.3e}"
    assert fac.reconstruction_residual < 1e-6
    for f in (fac.R, fac.T, fac.D):
        assert versor_condition(f) < 1e-6
    I = _identity()
    # Must have taken the peel path — not silent Spin remainder.
    assert float(np.linalg.norm(fac.D - I)) > 1e-3
    assert float(np.linalg.norm(fac.T - I)) > 1e-3
    s_rec, _ = recover_dilation(fac.D)
    assert abs(s_rec - 1.7) < 1e-6
    # Translation content: a is the origin image under R·T (R conjugates the
    # Euclidean displacement). Assert nontrivial finite translation, not a==t.
    a_rec, _ = recover_translation(fac.T)
    assert float(np.linalg.norm(a_rec)) > 1e-3
    assert np.isfinite(a_rec).all()
    # R·T must recover the de-dilated motion (peel identity).
    RT = geometric_product(fac.R, fac.T)
    V1 = geometric_product(V, reverse(fac.D))
    assert float(np.linalg.norm(RT - V1)) < 1e-6


def test_cartan_iwasawa_pure_dilator_round_trip():
    from algebra.null_point import recover_dilation

    V = dilator(2.5)
    fac = cartan_iwasawa_factorize(V)
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    assert float(np.linalg.norm(recon - V)) < 1e-6
    assert fac.reconstruction_residual < 1e-6
    for f in (fac.R, fac.T, fac.D):
        assert versor_condition(f) < 1e-6
    I = _identity()
    assert float(np.linalg.norm(fac.R - I)) < 1e-9
    assert float(np.linalg.norm(fac.T - I)) < 1e-9
    s_rec, _ = recover_dilation(fac.D)
    assert abs(s_rec - 2.5) < 1e-6


def test_cartan_iwasawa_pure_translator_round_trip():
    from algebra.null_point import recover_translation

    t_vec = np.array([1.0, -0.5, 0.25], dtype=np.float64)
    V = translator(t_vec)
    fac = cartan_iwasawa_factorize(V)
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    assert float(np.linalg.norm(recon - V)) < 1e-6
    assert fac.reconstruction_residual < 1e-6
    for f in (fac.R, fac.T, fac.D):
        assert versor_condition(f) < 1e-6
    I = _identity()
    assert float(np.linalg.norm(fac.R - I)) < 1e-9
    assert float(np.linalg.norm(fac.D - I)) < 1e-9
    a_rec, _ = recover_translation(fac.T)
    assert np.allclose(a_rec, t_vec, atol=1e-6)


def test_cartan_iwasawa_identity_factors_cleanly():
    V = _identity()
    fac = cartan_iwasawa_factorize(V)
    assert float(np.linalg.norm(fac.R - V)) < 1e-12 or fac.reconstruction_residual < 1e-12
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    assert float(np.linalg.norm(recon - V)) < 1e-12
    assert fac.reconstruction_residual < 1e-12
    for f in (fac.R, fac.T, fac.D):
        assert versor_condition(f) < 1e-6


def test_cartan_iwasawa_rejects_non_versor():
    bad = np.ones(32, dtype=np.float64)
    with pytest.raises(ValueError):
        cartan_iwasawa_factorize(bad)


# --- Finding #3 / gap #17: Kabsch-conformal Procrustes field conjugacy --------

def test_conformal_procrustes_field_conjugacy_nontrivial():
    """#17: non-trivial multiplane F_A, F_B = sandwich(W, F_A); sandwich residual < 1e-5.

    Behavioral pin: residual is measured under ``versor_apply`` (sandwich), not
    left-composition via ``word_transition_rotor``. Identity→identity is excluded.
    """
    F_A = _composed_versor((6, 7, 10, 11), seed=1.5)
    W = geometric_product(
        geometric_product(
            make_rotor_from_angle(0.55, bivector_idx=6),
            make_rotor_from_angle(0.4, bivector_idx=7),
        ),
        make_rotor_from_angle(0.3, bivector_idx=10),
    )
    F_B = versor_apply(W, F_A)
    assert float(np.linalg.norm(F_A - _identity())) > 1e-3
    assert float(np.linalg.norm(F_B - F_A)) > 1e-3

    V, residual = conformal_procrustes(F_A, F_B)
    assert V.shape == (32,)
    assert versor_condition(V) < 1e-6
    assert residual < 1e-5, f"sandwich residual {residual:.3e}"
    sand = float(np.linalg.norm(versor_apply(V, F_A) - F_B))
    assert sand < 1e-5, f"versor_apply residual {sand:.3e}"

