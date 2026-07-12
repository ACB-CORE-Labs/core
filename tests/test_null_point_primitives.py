"""Pin tests for the conformal null-point primitives.

These lock the CGA null geometry that the shared #17 (Kabsch / conformal
Procrustes) and #16 (Cartan–Iwasawa) recovery helpers stand on:

  * the frozen ``N_O`` / ``N_INF`` constants agree exactly with the vectors
    ``embed_point`` builds inline, and
  * the sign convention is ``n_o = 0.5 * (e5 - e4)`` (NOT ``e4 - e5`` — the old
    module-header docstring had that backwards).

The inner-product identities are exact (0.5 / 1.0 are representable), so the
tolerances are tight.
"""

import numpy as np
import pytest

from algebra.cga import N_INF, N_O, cga_inner, embed_point, read_scalar_e1
from algebra.cl41 import basis_vector, geometric_product, reverse, scalar_part
from algebra.null_point import (
    NullPointRecoveryError,
    dilator,
    recover_dilation,
    recover_translation,
    translator,
    _E_DILATION,
)
from algebra.rotor import make_rotor_from_angle


def _sandwich(V, X):
    V = np.asarray(V, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    return geometric_product(geometric_product(V, X), reverse(V))


def test_n_o_sign_convention_matches_basis_vectors():
    """n_o = 0.5 * (e5 - e4); basis_vector is 0-indexed so e4=bv(3), e5=bv(4)."""
    n_o = 0.5 * (basis_vector(4) - basis_vector(3))
    assert np.allclose(N_O, n_o), "frozen N_O disagrees with 0.5*(e5 - e4)"


def test_n_inf_matches_basis_vectors():
    n_inf = basis_vector(3) + basis_vector(4)  # e4 + e5
    assert np.allclose(N_INF, n_inf), "frozen N_INF disagrees with e4 + e5"


def test_null_cone_invariants():
    """N_O and N_INF both lie on the null cone: X . X = 0."""
    assert abs(cga_inner(N_O, N_O)) < 1e-12
    assert abs(cga_inner(N_INF, N_INF)) < 1e-12


def test_no_ninf_pairing_is_minus_one():
    """N_O . N_INF = -1 exactly. Parenthesis is INSIDE abs: abs(x + 1), not abs(x) + 1."""
    assert abs(cga_inner(N_O, N_INF) + 1.0) < 1e-12


def test_embed_origin_is_n_o():
    """The Euclidean origin embeds to n_o: e4 coeff = -0.5, e5 coeff = +0.5."""
    x0 = embed_point(np.zeros(3), dtype=np.float64)
    assert np.allclose(x0[4:6], [-0.5, 0.5])
    # ...and the whole embedding equals N_O (origin has zero Euclidean part).
    assert np.allclose(x0, N_O)


def test_constants_are_read_only():
    """The module constants must not be mutable in place."""
    for const in (N_O, N_INF):
        assert const.flags.writeable is False


# ---------------------------------------------------------------------------
# Recovery primitives: constructors, round-trips, composed peel, fail-closed.
# ---------------------------------------------------------------------------


def test_E_dilation_squares_to_one():
    """The dilation bivector E = n_o ^ n_inf lives at index 15 and E^2 = +1."""
    assert _E_DILATION[15] == -1.0
    assert np.count_nonzero(_E_DILATION) == 1
    e_sq = geometric_product(_E_DILATION, _E_DILATION)
    assert abs(scalar_part(e_sq) - 1.0) < 1e-12
    assert np.linalg.norm(e_sq[1:]) < 1e-12  # pure scalar


def test_dilator_scales_euclidean_lengths():
    """dilator(s) scales the Euclidean coordinate of a point by s."""
    X = embed_point(np.array([3.0, 0.0, 0.0]), dtype=np.float64)
    for s in (2.0, 0.5, 4.0):
        Y = _sandwich(dilator(s), X)
        assert abs(read_scalar_e1(Y) - s * 3.0) < 1e-9


def test_translator_maps_origin_to_point():
    """translator(a) carries the origin exactly to embed_point(a)."""
    for a in ([1.0, 0.0, 0.0], [2.0, -1.0, 0.5]):
        a = np.array(a)
        image = _sandwich(translator(a), N_O)
        assert np.allclose(image, embed_point(a, dtype=np.float64), atol=1e-9)


@pytest.mark.parametrize("scale", [2.5, 0.4, 1.0, 7.0, 0.125])
def test_recover_dilation_round_trip(scale):
    rec_scale, D = recover_dilation(dilator(scale))
    assert abs(rec_scale - scale) < 1e-9
    assert np.allclose(D, dilator(scale), atol=1e-12)


@pytest.mark.parametrize("a", [[1.5, -0.5, 2.0], [-3.0, 1.0, 0.0], [0.0, 0.0, 0.0]])
def test_recover_translation_round_trip(a):
    a = np.array(a)
    rec_a, T = recover_translation(translator(a))
    assert np.allclose(rec_a, a, atol=1e-9)
    assert np.allclose(T, translator(a), atol=1e-12)


@pytest.mark.parametrize(
    "scale,a,angle",
    [(2.5, [1.5, -0.5, 2.0], 0.7), (0.4, [-3.0, 1.0, 0.0], 1.9), (3.0, [0.2, 0.2, 0.2], -1.1)],
)
def test_recover_from_composed_similarity(scale, a, angle):
    """V = T . D . R : dilation and translation peel out exactly, rotation and
    each other's presence notwithstanding."""
    a = np.array(a)
    R = make_rotor_from_angle(angle, bivector_idx=6).astype(np.float64)
    V = geometric_product(geometric_product(translator(a), dilator(scale)), R)
    rec_scale, _ = recover_dilation(V)
    rec_a, _ = recover_translation(V)
    assert abs(rec_scale - scale) < 1e-8
    assert np.allclose(rec_a, a, atol=1e-8)


@pytest.mark.parametrize("k", [3.0, 0.5, 10.0])
def test_recover_dilation_is_versor_weight_invariant(k):
    """Regression: the raw n_inf coefficient scales with the versor weight; the
    recovered scale must NOT. recover_dilation(k*V) == recover_dilation(V)."""
    V = geometric_product(translator(np.array([1.0, 2.0, -1.0])), dilator(2.5))
    base, _ = recover_dilation(V)
    scaled, _ = recover_dilation(k * V)
    assert abs(base - 2.5) < 1e-9
    assert abs(scaled - base) < 1e-9


def test_recover_translation_is_weight_invariant():
    V = geometric_product(translator(np.array([1.0, 2.0, -1.0])), dilator(2.5))
    a0, _ = recover_translation(V)
    a1, _ = recover_translation(3.0 * V)
    assert np.allclose(a0, [1.0, 2.0, -1.0], atol=1e-9)
    assert np.allclose(a1, a0, atol=1e-9)


def test_recover_dilation_refuses_transversion():
    """A transversion (special conformal) does NOT fix infinity -> not_similarity."""
    b = np.zeros(32)
    b[1] = 0.3
    K = np.zeros(32)
    K[0] = 1.0
    K = K - 0.5 * geometric_product(b, N_O)  # transversion = 1 - 0.5 b n_o
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_dilation(K)
    assert exc.value.reason == "not_similarity"


def test_recover_dilation_refuses_non_versor():
    """A mixed-grade multivector is not a versor -> not_a_versor."""
    bad = np.zeros(32)
    bad[0] = 1.0
    bad[1] = 1.0
    bad[6] = 1.0  # scalar + vector + bivector: V rev(V) not scalar
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_dilation(bad)
    assert exc.value.reason == "not_a_versor"


def test_recover_translation_refuses_inversion_as_not_similarity():
    """Unit-sphere inversion sigma = n_o - 0.5 n_inf swaps the null directions, so
    it is not a similarity (does not fix infinity). The shared similarity gate
    refuses it as not_similarity — the fundamental cause. (It also sends the origin
    to infinity; origin_at_infinity remains a defensive division guard, subsumed
    here for genuine inversions.)"""
    sigma = N_O - 0.5 * N_INF  # sigma^2 = 1, an honest inversion reflector
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_translation(sigma)
    assert exc.value.reason == "not_similarity"


def test_recover_translation_refuses_transversion():
    """Symmetric with recover_dilation: a transversion IS a versor and fixes the
    origin, so without the similarity gate it silently returned a plausible
    a=[0,0,0]. The gate must refuse it (it does not fix infinity) -> not_similarity."""
    b = np.zeros(32)
    b[1] = 0.3
    K = np.zeros(32)
    K[0] = 1.0
    K = K - 0.5 * geometric_product(b, N_O)  # transversion = 1 - 0.5 b n_o
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_translation(K)
    assert exc.value.reason == "not_similarity"


def test_recover_translation_refuses_non_versor():
    """A mixed-grade multivector is not a versor -> not_a_versor (symmetric with
    recover_dilation; previously recover_translation accepted it and returned a
    silent value)."""
    bad = np.zeros(32)
    bad[0] = 1.0
    bad[1] = 1.0
    bad[6] = 1.0  # scalar + vector + bivector: V rev(V) not scalar
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_translation(bad)
    assert exc.value.reason == "not_a_versor"


def _reflection_similarity(a, scale):
    """T . D . (e1-reflection): an orientation-reversing (det=-1) similarity, what a
    raw Kabsch/SVD fit yields before it strips the reflection."""
    return geometric_product(
        geometric_product(translator(np.array(a)), dilator(scale)), basis_vector(0)
    )


def test_recover_dilation_refuses_reflection_as_improper():
    """A reflection (improper rotation, det=-1) is refused as improper_versor, NOT
    degenerate_scale: its scale magnitude is a clean, well-conditioned number, and
    the distinct reason lets a consumer route 'strip the reflection' vs 'broken'."""
    V = _reflection_similarity([1.0, 0.5, -0.3], 2.0)
    with pytest.raises(NullPointRecoveryError) as exc:
        recover_dilation(V)
    assert exc.value.reason == "improper_versor"


def test_recover_translation_accepts_reflection():
    """Asymmetry by design: the origin image is well defined under a reflection, so
    recover_translation SUCCEEDS on the very versor recover_dilation refuses."""
    V = _reflection_similarity([1.0, 0.5, -0.3], 2.0)
    rec_a, _ = recover_translation(V)
    assert np.allclose(rec_a, [1.0, 0.5, -0.3], atol=1e-9)


def test_dilator_rejects_nonpositive_scale():
    for bad in (0.0, -1.0, float("inf"), float("nan")):
        with pytest.raises(NullPointRecoveryError) as exc:
            dilator(bad)
        assert exc.value.reason == "nonpositive_scale"


def test_translator_rejects_bad_vector():
    with pytest.raises(NullPointRecoveryError):
        translator(np.array([1.0, 2.0]))  # wrong shape
    with pytest.raises(NullPointRecoveryError):
        translator(np.array([1.0, np.nan, 0.0]))  # non-finite
