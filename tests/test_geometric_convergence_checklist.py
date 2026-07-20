"""Binary geometric-convergence checklist pins (ADRs 0241–0244 + sovereignty).

Keeps the objective validation items executable and local-first.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cga import N_INF, N_O, cga_inner, embed_point, is_null
from algebra.cl41 import geometric_product, reverse, scalar_part
from algebra.versor import versor_condition
from core.physics.goldtether import (
    GoldTetherViolationError,
    coherence_residual,
    require_unitary,
)
from core.physics.identity import IdentityCheck, MissingWaveStateError
from core.physics.identity_manifold import (
    CONDITION_BOUND,
    ManifoldConditioningError,
    gram_matrix,
    lift_axis,
)
from core.physics.wave_manifold import WaveManifold, multivector_content_digest
from field.state import FieldState


def test_null_basis_invariants():
    assert abs(cga_inner(N_INF, N_INF)) < 1e-12
    assert abs(cga_inner(N_O, N_O)) < 1e-12
    assert abs(cga_inner(N_O, N_INF) + 1.0) < 1e-12


def test_horosphere_lift_is_null():
    x = np.array([1.0, -2.0, 0.5], dtype=np.float64)
    X = embed_point(x, dtype=np.float64)
    assert is_null(X, tol=1e-9)
    # X² scalar part ≈ 0 on the null cone
    xx = geometric_product(X, X)
    assert abs(float(scalar_part(xx))) < 1e-9


def test_exp_bivector_step_unit_versor():
    from core.physics import wave_manifold as wm

    B = np.zeros(32, dtype=np.float64)
    B[6] = 0.35  # e12 plane
    R = wm._exp_bivector_generator(B, 0.5)
    assert float(versor_condition(R)) < 1e-12
    # Explicit unit versor: R · rev(R) ≈ 1 within 1e-12
    prod = geometric_product(R, reverse(R))
    assert abs(float(prod[0]) - 1.0) < 1e-12
    residue = prod.copy()
    residue[0] = 0.0
    assert float(np.linalg.norm(residue)) < 1e-12


def test_gram_conditioning_guard():
    axes = [lift_axis((1.0, 0.0, 0.0)), lift_axis((1.0, 1e-12, 0.0))]
    with pytest.raises(ManifoldConditioningError):
        gram_matrix(axes)
    assert CONDITION_BOUND == 1e5


def test_missing_wave_state_error():
    class _T:
        trajectory_id = "t"
        frames = ()
        total_coherence_delta = 0.0

    from core.physics.identity import IdentityManifold, ValueAxis

    manifold = IdentityManifold(
        value_axes=(ValueAxis(name="truth", direction=(1.0, 0.0, 0.0)),)
    )
    with pytest.raises(MissingWaveStateError):
        IdentityCheck().check(_T(), manifold)


def test_goldtether_fail_closed():
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    assert coherence_residual(dirty) > 1e-6
    with pytest.raises(GoldTetherViolationError):
        require_unitary(dirty, epsilon=1e-6)


def test_field_and_wave_content_digests():
    F = np.zeros(32, dtype=np.float64)
    F[0] = 1.0
    d1 = multivector_content_digest(F)
    d2 = FieldState(F=F).content_digest()
    assert d1 == d2
    assert len(d1) == 64
    assert all(c in "0123456789abcdef" for c in d1)


def test_modality_transition_sandwich_goldtether():
    """Lifecycle modality transitions are versor sandwiches with GoldTether."""
    from algebra.rotor import make_rotor_from_angle
    from core.physics.cognitive_lifecycle import modality_transition_sandwich
    from core.physics.goldtether import GoldTetherViolationError

    psi = np.zeros(32, dtype=np.float64)
    psi[0] = 1.0
    R = make_rotor_from_angle(0.3)
    out, tr = modality_transition_sandwich(
        psi, R, source_modality="vision", target_modality="language"
    )
    assert out.shape == (32,)
    assert len(tr.psi_out_digest) == 64
    assert tr.goldtether_residual <= 1e-6
    dirty = np.zeros(32, dtype=np.float64)
    dirty[0] = 0.5
    dirty[1] = 0.5
    with pytest.raises(GoldTetherViolationError):
        modality_transition_sandwich(psi, dirty)


def test_vocab_nearest_ranks_by_cga_inner_behaviorally():
    """Drive VocabManifold.nearest: selected word is argmax of cga_inner scores.

    Cl(4,1) cga_inner is indefinite — self-inner need not be maximal — so we
    pin ranking fidelity, not Euclidean nearest-neighbor intuition.
    """
    from algebra.versor import unitize_versor
    from vocab.manifold import VocabManifold

    rng = np.random.default_rng(7)
    m = VocabManifold()
    words = ("alpha", "beta", "gamma")
    for w in words:
        raw = rng.standard_normal(32).astype(np.float64)
        m.add(w, unitize_versor(raw))
    # Query slightly off the beta versor so ranking is non-trivial
    query = unitize_versor(
        m.get_versor("beta").astype(np.float64) + 0.05 * rng.standard_normal(32)
    )
    word, idx = m.nearest(query)
    scores = [float(cga_inner(query, m.get_versor_at(i))) for i in range(len(m))]
    best = int(np.argmax(scores))
    assert idx == best
    assert word == m.get_word_at(best)
    assert scores[idx] == max(scores)
    # Distinct scores → unique winner determined solely by cga_inner ranking
    assert len({round(s, 9) for s in scores}) == len(scores)
    # Cosine on raw coefficients must not be treated as the ranking oracle:
    # if it disagrees with cga_inner, nearest still follows cga_inner.
    def _cos(a: np.ndarray, b: np.ndarray) -> float:
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-30))

    cos_scores = [_cos(query, m.get_versor_at(i)) for i in range(len(m))]
    cos_best = int(np.argmax(cos_scores))
    if cos_best != best:
        assert idx == best  # still cga_inner winner
