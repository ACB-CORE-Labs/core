"""Null-point recovery primitives for CGA conformal versors.

Shared substrate for the conformal-Procrustes (#17) and Cartan–Iwasawa (#16)
decompositions. Given a *similarity* versor V (rotation · dilation · translation,
in any order), these peel off the translation it applies to the origin and the
uniform dilation it applies to lengths, using only the exact CGA sandwich
``V·X·rev(V)`` on the two null directions ``N_O`` / ``N_INF`` (see algebra/cga.py:
``n_o = 0.5(e5 - e4)``, ``n_inf = e4 + e5``).

Empirically pinned (f64-exact; probes reproduced in the test module):

  * ``V n_inf rev(V) = scale · n_inf``  — a similarity FIXES the point at
    infinity, so its n_inf image is a *pure* positive multiple of n_inf whose
    coefficient is the dilation factor. Anything else — a transversion / special
    conformal versor — leaves an off-n_inf residual and is REFUSED.
  * ``V n_o rev(V) = w_o·n_o + scale^-1·a + …``  — the origin's image is a
    conformal point; ``a = euclidean_part / w_o`` recovers the translation by
    projective dehomogenization (the weight divides out the dilation, and
    rotation fixes the origin, so ``a`` is exact regardless of V's rotation or
    scale content — the same trick as :func:`algebra.cga.read_scalar_e1`).

Conventions — both constructors round-trip through the recoverers:
  ``dilator(scale)``  scales Euclidean lengths by ``scale`` (> 0);
    ``recover_dilation(dilator(s)) == s``.
  ``translator(a)``   maps the origin to Euclidean point ``a`` (3-vector);
    ``recover_translation(translator(a)) == a``.

Fail-closed discipline (the wrong=0 rule): every recovery raises
:class:`NullPointRecoveryError` on a degenerate, non-versor, or non-similarity
input rather than returning a silently wrong value — ``recover_dilation`` and
``recover_translation`` share one versor+similarity gate
(:func:`_require_similarity`), so neither accepts what the other refuses. Guards
are scale-relative so a versor with non-unit weight (e.g. one assembled from a
Kabsch/SVD point cloud) is judged by its *shape*, not its magnitude.

Tolerance: the default ``tol=1e-9`` matches the f64-exact recovery of a cleanly
assembled versor (an SVD-orthogonal rotation composed with an exact
dilator/translator round-trips to ~1e-14). A caller whose versor carries larger
numerical noise — e.g. an iteratively refined Procrustes fit — must pass a ``tol``
at least as large as that residual, or a valid similarity may be refused as
``not_a_versor`` / ``not_similarity`` (fail-closed: it is never *accepted* with a
wrong value). ``core.physics.conformal_procrustes`` uses ``tol=1e-8`` by convention.
"""

from __future__ import annotations

import numpy as np

from .cga import N_INF, N_O, cga_inner, graded_wedge
from .cl41 import N_COMPONENTS, geometric_product, reverse

# e4 / e5 component indices inside the grade-1 block (mirror of algebra.cga; kept
# local to avoid importing a private name across modules).
_E4_IDX = 4
_E5_IDX = 5

# The dilation bivector E = n_o ^ n_inf. E^2 = +1 (boost-like), so the dilator is
# a hyperbolic exponential cosh + sinh·E. Frozen f64; never mutated.
_E_DILATION = graded_wedge(N_O, N_INF).astype(np.float64)
_E_DILATION.setflags(write=False)


class NullPointRecoveryError(ValueError):
    """A versor is degenerate or not a similarity transform.

    Carries a machine-readable ``reason`` for callers that route on the failure
    mode (e.g. #17 margin reporting) rather than only surfacing the message.
    """

    def __init__(self, message: str, *, reason: str) -> None:
        super().__init__(message)
        self.reason = reason


def _sandwich(V: np.ndarray, X: np.ndarray) -> np.ndarray:
    """The raw f64 sandwich ``V X rev(V)`` — no closure, no unitisation.

    (Deliberately not :func:`algebra.versor.versor_apply`: that path unitises
    non-null inputs and coerces to the runtime field dtype. Null-point recovery
    needs the exact algebraic image in f64.)
    """
    V = np.asarray(V, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    return geometric_product(geometric_product(V, X), reverse(V))


def dilator(scale: float) -> np.ndarray:
    """Uniform-scale versor that scales Euclidean lengths by ``scale`` (> 0).

    ``D = exp(0.5·ln(scale)·E) = cosh(h) + sinh(h)·E`` with ``h = 0.5·ln(scale)``
    and ``E = n_o ^ n_inf`` (``E^2 = +1``). Acts as
    ``D n_inf rev(D) = scale·n_inf`` and ``D n_o rev(D) = scale^-1·n_o``.
    """
    scale = float(scale)
    if not np.isfinite(scale) or scale <= 0.0:
        raise NullPointRecoveryError(
            f"dilator scale must be finite and positive, got {scale}",
            reason="nonpositive_scale",
        )
    half = 0.5 * np.log(scale)
    D = np.zeros(N_COMPONENTS, dtype=np.float64)
    D[0] = np.cosh(half)
    D = D + np.sinh(half) * _E_DILATION
    return D


def translator(a: np.ndarray) -> np.ndarray:
    """Translator versor that maps the origin to Euclidean point ``a`` (3-vector).

    ``T = 1 - 0.5·a·n_inf`` (a embedded on e1..e3). ``T n_o rev(T)`` equals the
    conformal embedding of ``a`` (== :func:`algebra.cga.embed_point`).
    """
    a = np.asarray(a, dtype=np.float64)
    if a.shape != (3,) or not np.all(np.isfinite(a)):
        raise NullPointRecoveryError(
            f"translator expects a finite 3-vector, got shape {a.shape}",
            reason="bad_translation_vector",
        )
    a_mv = np.zeros(N_COMPONENTS, dtype=np.float64)
    a_mv[1:4] = a
    T = np.zeros(N_COMPONENTS, dtype=np.float64)
    T[0] = 1.0
    T = T - 0.5 * geometric_product(a_mv, N_INF)
    return T


def _versor_scalar_weight(V: np.ndarray, tol: float) -> float:
    """Return ``scalar_part(V·rev(V))`` after checking ``V`` is a versor.

    A versor satisfies ``V·rev(V) = scalar``; a non-versor multivector leaves an
    off-scalar residual. Raises :class:`NullPointRecoveryError` (``not_a_versor``
    / ``degenerate_weight``) otherwise. The weight is what makes
    :func:`recover_dilation` weight-invariant — the raw ``n_inf`` coefficient
    scales with this weight, so the true dilation is the coefficient divided by it.
    """
    V = np.asarray(V, dtype=np.float64)
    vv = geometric_product(V, reverse(V))
    w = float(vv[0])
    off_scalar = float(np.linalg.norm(vv[1:]))
    ref = max(1.0, abs(w))
    if off_scalar > tol * ref:
        raise NullPointRecoveryError(
            f"V·rev(V) is not scalar (off-scalar residual {off_scalar / ref:.3e}); "
            "not a versor",
            reason="not_a_versor",
        )
    if abs(w) <= tol:
        raise NullPointRecoveryError(
            f"degenerate versor weight {w:.3e}", reason="degenerate_weight",
        )
    return w


def _require_similarity(V: np.ndarray, tol: float) -> tuple[float, float]:
    """Gate ``V`` as a similarity versor; return ``(weight, signed_scale)``.

    A similarity (rotation · dilation · translation, in any order) is the only
    class both recoverers accept: it is a versor (``V·rev(V)`` scalar) *and* it
    fixes infinity (``V n_inf rev(V)`` is a pure multiple of ``n_inf``). The
    returned ``signed_scale = c_inf / weight`` is positive for a proper similarity
    and negative for an orientation-reversing (improper / reflection) one; sign
    and degeneracy classification is left to the caller, so
    :func:`recover_translation` can accept a reflection — whose origin image is
    still well defined — while :func:`recover_dilation` refuses it.

    Raises :class:`NullPointRecoveryError` with ``not_a_versor`` /
    ``degenerate_weight`` (from :func:`_versor_scalar_weight`) or ``not_similarity``.
    """
    weight = _versor_scalar_weight(V, tol)
    W = _sandwich(V, N_INF)
    c_inf = 0.5 * (float(W[_E4_IDX]) + float(W[_E5_IDX]))

    resid = W.copy()
    resid[_E4_IDX] -= c_inf
    resid[_E5_IDX] -= c_inf
    resid_norm = float(np.linalg.norm(resid))
    ref = max(1.0, float(np.linalg.norm(W)))
    if resid_norm > tol * ref:
        raise NullPointRecoveryError(
            f"versor does not fix infinity (off-n_inf residual "
            f"{resid_norm / ref:.3e} > {tol:.1e}); not a similarity transform",
            reason="not_similarity",
        )
    return weight, c_inf / weight


def recover_dilation(V: np.ndarray, *, tol: float = 1e-9) -> tuple[float, np.ndarray]:
    """Recover the uniform scale a similarity versor ``V`` applies to lengths.

    Returns ``(scale, D)`` with ``D == dilator(scale)`` and ``scale > 0``. Reads
    the image of the point at infinity ``W = V n_inf rev(V)`` (for a similarity a
    pure multiple of ``n_inf``) and normalises its coefficient by the versor weight
    ``V·rev(V)`` — the sandwich scales with that weight, so a non-unit versor still
    yields the true scale (verified against ``V -> kV``).

    Raises :class:`NullPointRecoveryError` when
      * ``V`` is not a versor (``not_a_versor`` / ``degenerate_weight``) or does
        not fix infinity, i.e. is not a similarity (``not_similarity`` — e.g. a
        transversion);
      * ``V`` is orientation-reversing — a reflection / improper rotation, the
        ``det = -1`` case a raw Kabsch/SVD fit produces before it strips the
        reflection (``core.physics.conformal_procrustes`` does strip it). Its
        signed scale is a clean negative, refused as ``improper_versor``, kept
        distinct from true degeneracy so a caller can tell "flip a singular
        vector" from "numerically broken". :func:`recover_translation` still
        accepts such a versor — only the *dilation* is ill-defined for an improper
        map here; or
      * the recovered scale is non-finite or collapses to zero (``degenerate_scale``).
    """
    _, scale = _require_similarity(V, tol)
    # Preserve the original accept-set exactly (finite *positive* scale, any
    # magnitude); split the negative case out to a distinct, honest reason.
    if not np.isfinite(scale):
        raise NullPointRecoveryError(
            f"degenerate dilation coefficient {scale}",
            reason="degenerate_scale",
        )
    if scale < 0.0:
        raise NullPointRecoveryError(
            f"orientation-reversing versor (signed scale {scale:.6g}); an improper "
            "similarity has no positive dilation — strip the reflection first",
            reason="improper_versor",
        )
    if scale == 0.0:
        raise NullPointRecoveryError(
            "degenerate dilation coefficient 0.0 (versor collapses n_inf)",
            reason="degenerate_scale",
        )
    return scale, dilator(scale)


def recover_translation(V: np.ndarray, *, tol: float = 1e-9) -> tuple[np.ndarray, np.ndarray]:
    """Recover the translation a similarity versor ``V`` applies to the origin.

    Returns ``(a, T)`` with ``a`` the Euclidean image of the origin (3-vector)
    and ``T == translator(a)``. Reads ``W = V n_o rev(V)`` and dehomogenizes
    projectively: ``a = W[e1:e3+1] / w_o`` where ``w_o = W[e5] - W[e4]``. The
    weight divides out any dilation, and rotation — proper *or* a reflection —
    fixes the origin, so ``a`` is exact regardless of ``V``'s rotation/scale
    content. An improper (reflection) similarity is therefore accepted here even
    though :func:`recover_dilation` refuses it: the origin image is well defined,
    only the positive dilation is not.

    Gates ``V`` as a similarity versor first (the same :func:`_require_similarity`
    gate as :func:`recover_dilation`), so a non-versor or a non-similarity — e.g. a
    transversion, which fixes the origin and would otherwise return a plausible
    ``a`` silently — fails closed rather than returning a wrong value.

    Raises :class:`NullPointRecoveryError` when
      * ``V`` is not a versor (``not_a_versor`` / ``degenerate_weight``) or does
        not fix infinity (``not_similarity``);
      * the origin maps to infinity (``origin_at_infinity`` — ``|w_o|`` at/below
        ``tol``; guards the projective division, subsumed by the similarity gate
        for genuine inversions); or
      * the origin image leaves the null cone (``non_null_image`` — scale-relative
        defect > ``tol``), so ``W`` is not a conformal point.
    """
    _require_similarity(V, tol)
    W = _sandwich(V, N_O)
    w_o = float(W[_E5_IDX] - W[_E4_IDX])
    if abs(w_o) <= tol:
        raise NullPointRecoveryError(
            f"origin maps to infinity (n_o weight {w_o:.3e}); no finite translation",
            reason="origin_at_infinity",
        )
    null_defect = abs(cga_inner(W, W))
    ref = max(1.0, float(np.dot(W, W)))
    if null_defect > tol * ref:
        raise NullPointRecoveryError(
            f"origin image leaves the null cone (defect {null_defect / ref:.3e}); "
            "not a conformal point",
            reason="non_null_image",
        )
    a = np.asarray(W[1:4], dtype=np.float64) / w_o
    return a, translator(a)
