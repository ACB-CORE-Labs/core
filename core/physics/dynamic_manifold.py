"""
core/physics/dynamic_manifold.py

Signature-aware PCA + Conformal Procrustes + Cartan-Iwasawa extraction
ADR-0239

Geometry-first, dual-corrected, null-vector safe.
Wired to live algebra/* (no scipy, no placeholder-only path).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Sequence, Tuple, Union

import numpy as np

from algebra.cga import is_null
from algebra.cl41 import N_COMPONENTS, geometric_product, grade_project, reverse
from algebra.null_point import (
    NullPointRecoveryError,
    dilator,
    recover_dilation,
    recover_translation,
    translator,
)
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import versor_condition

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_NULL_TOL = 1e-9
_PROCRUSTES_WEIGHT_TOL = 1e-8
_CONJUGACY_RES_TOL = 1e-5
_CONJUGACY_MAX_STEPS = 48
# Grade-2 blade indices (e1∧e2 … spanning the 10-plane bivector of Cl(4,1)).
_BIVECTOR_PLANES = tuple(range(6, 16))

# Cl(4,1) metric on Euclidean+conformal R^5
_ETA5 = np.diag([1.0, 1.0, 1.0, 1.0, -1.0]).astype(np.float64)


class AxisClassification(str, Enum):
    SPACELIKE = "spacelike"
    TIMELIKE = "timelike"
    NULL = "null"
    DEGENERATE = "degenerate"


@dataclass(frozen=True, slots=True)
class PrincipalAxis:
    vector: tuple[float, ...]
    eigenvalue: float
    classification: AxisClassification
    metric_quadratic: float


@dataclass(frozen=True, slots=True)
class SignatureAwarePCAResult:
    axes: tuple[PrincipalAxis, ...]
    basis_matrix: np.ndarray  # shape (5, n) or (32, n)
    n_null: int
    n_spacelike: int
    n_timelike: int
    n_degenerate: int


@dataclass(frozen=True, slots=True)
class ConformalProcrustesResult:
    versor: np.ndarray
    residual_norm: float
    n_pairs: int
    pair_residuals: tuple[float, ...]


@dataclass(frozen=True, slots=True)
class CartanIwasawaFactors:
    """Rotor · Translator · Dilator (K/A/N style factors on the multivector)."""

    R: np.ndarray
    T: np.ndarray
    D: np.ndarray
    reconstruction_residual: float


def _identity32() -> np.ndarray:
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    out[0] = 1.0
    return out


def _strict_close_versor(V: np.ndarray, *, name: str) -> np.ndarray:
    """Rescale a true versor to unit weight; never seed-fabricate a rotor.

    A versor satisfies ``V·rev(V) = scalar``. If the product is not scalar, or
    the scalar is non-positive, raise ``ValueError`` (fail-closed). This is the
    construction-boundary closer for Cartan–Iwasawa — distinct from
    :func:`unitize_versor`, which may map dense seeds onto the manifold.
    """
    arr = np.asarray(V, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name}: expected shape ({N_COMPONENTS},), got {arr.shape}")
    product = geometric_product(arr, reverse(arr)).astype(np.float64)
    scalar_sq = float(product[0])
    residue = product.copy()
    residue[0] = 0.0
    residue_norm = float(np.linalg.norm(residue))
    if residue_norm >= 1e-2 or scalar_sq <= 0.0:
        raise ValueError(
            f"{name}: input not a versor "
            f"(residue_norm={residue_norm:.3e}, scalar_sq={scalar_sq:.3e})"
        )
    return (arr * (1.0 / np.sqrt(scalar_sq))).astype(np.float64)


def _identity5() -> np.ndarray:
    return np.eye(5, dtype=np.float64)


def signature_aware_pca(
    X: np.ndarray,
    target_grade: int = 3,
) -> np.ndarray:
    """
    Metric-preserving principal axes on the Cl(4,1) null cone.

    X: shape (5, K) of conformal (null) vectors.
    Returns: shape (5, target_grade) real, pseudo-orthogonal basis.

    CRITICAL FIX (Terra + Grok mastery): genuine null vectors are CLASSIFIED
    and retained. They are never silently skipped.
    """
    X_arr = np.asarray(X, dtype=np.float64)
    if X_arr.ndim != 2 or X_arr.shape[0] != 5:
        raise ValueError("signature_aware_pca expects X with shape (5, K)")
    K = X_arr.shape[1]
    A = (X_arr @ X_arr.T) / max(K, 1)
    M = _ETA5 @ A
    eigenvalues, eigenvectors = np.linalg.eig(M)
    real_idx = np.argsort(np.real(eigenvalues))[::-1]
    sorted_vecs = np.real(eigenvectors[:, real_idx])

    basis: list[np.ndarray] = []
    for i in range(sorted_vecs.shape[1]):
        v = sorted_vecs[:, i].copy()
        for u in basis:
            denom = float(u @ (_ETA5 @ u)) + 1e-12
            proj = float(v @ (_ETA5 @ u)) / denom
            v = v - proj * u
        nrm2 = float(v @ (_ETA5 @ v))
        if abs(nrm2) < _NULL_TOL:
            # GENUINE NULL VECTOR — keep as-is (the fix)
            if float(np.linalg.norm(v)) > _NEAR_ZERO:
                basis.append(v)
        else:
            nrm = float(np.sqrt(abs(nrm2)))
            if nrm > _NEAR_ZERO:
                basis.append(v / nrm)
        if len(basis) == int(target_grade):
            break
    if not basis:
        raise ValueError("signature_aware_pca produced empty basis")
    return np.column_stack(basis)


def signature_aware_pca_report(
    X: np.ndarray,
    target_grade: int = 3,
) -> SignatureAwarePCAResult:
    """PCA with explicit null/spacelike/timelike classification counts."""
    basis = signature_aware_pca(X, target_grade=target_grade)
    axes: list[PrincipalAxis] = []
    counts = {c: 0 for c in AxisClassification}
    for j in range(basis.shape[1]):
        v = basis[:, j]
        q = float(v @ (_ETA5 @ v))
        if float(np.linalg.norm(v)) < _NEAR_ZERO:
            cls = AxisClassification.DEGENERATE
        elif abs(q) < _NULL_TOL:
            cls = AxisClassification.NULL
        elif q > 0.0:
            cls = AxisClassification.SPACELIKE
        else:
            cls = AxisClassification.TIMELIKE
        counts[cls] += 1
        axes.append(
            PrincipalAxis(
                vector=tuple(float(x) for x in v),
                eigenvalue=q,
                classification=cls,
                metric_quadratic=q,
            )
        )
    return SignatureAwarePCAResult(
        axes=tuple(axes),
        basis_matrix=basis,
        n_null=counts[AxisClassification.NULL],
        n_spacelike=counts[AxisClassification.SPACELIKE],
        n_timelike=counts[AxisClassification.TIMELIKE],
        n_degenerate=counts[AxisClassification.DEGENERATE],
    )


def procrustes_residual(
    source: np.ndarray,
    target: np.ndarray,
    versor: np.ndarray,
) -> float:
    """Dedicated Procrustes residual: sandwich for 32-vecs, linear map for 5-vecs."""
    s = np.asarray(source, dtype=np.float64)
    t = np.asarray(target, dtype=np.float64)
    V = np.asarray(versor, dtype=np.float64)
    if s.shape == (N_COMPONENTS,) and V.shape == (N_COMPONENTS,):
        # Raw sandwich — not versor_apply (that unitizes non-null images).
        mapped = _raw_sandwich(V, s)
        return float(np.linalg.norm(mapped - t))
    # 5-vector conformal points: Frobenius after linear map if V is 5x5
    if s.shape == (5,) and V.shape == (5, 5):
        return float(np.linalg.norm(V @ s - t))
    if s.ndim == 2 and s.shape[0] == 5 and V.shape == (5, 5) and s.shape == t.shape:
        return _projective_cloud_residual(V @ s, t)
    return float(np.linalg.norm(s - t))


def so3_matrix_to_rotor(R3: np.ndarray) -> np.ndarray:
    """SO(3) matrix → Cl(4,1) rotor whose sandwich acts as ``R3`` on e1..e3.

    Shepperd quaternion extraction, then even-grade embed::

        rotor[0]  = q0
        rotor[10] = q1   # e2∧e3
        rotor[7]  = -q2  # -e1∧e3
        rotor[6]  = q3   # e1∧e2

    Unitize once at this construction boundary. Shepperd is applied to ``R3.T``
    so the sandwich product of this algebra implements active ``R3`` (the raw
    Shepperd(R) quaternion sandwiches as ``R.T`` under Cl(4,1) GP convention).
    """
    R = np.asarray(R3, dtype=np.float64)
    if R.shape != (3, 3) or not np.all(np.isfinite(R)):
        raise ValueError(f"so3_matrix_to_rotor expects finite (3,3), got {R.shape}")
    q0, q1, q2, q3 = _shepperd_quaternion(R.T)
    rotor = np.zeros(N_COMPONENTS, dtype=np.float64)
    rotor[0] = q0
    rotor[10] = q1  # e2∧e3
    rotor[7] = -q2  # -e1∧e3
    rotor[6] = q3   # e1∧e2
    return _strict_close_versor(rotor, name="so3_matrix_to_rotor")


def _shepperd_quaternion(R: np.ndarray) -> tuple[float, float, float, float]:
    """Shepperd's method: robust SO(3) → unit quaternion (q0, q1, q2, q3)."""
    R = np.asarray(R, dtype=np.float64)
    tr = float(R[0, 0] + R[1, 1] + R[2, 2])
    if tr > 0.0:
        S = np.sqrt(tr + 1.0) * 2.0
        q0 = 0.25 * S
        q1 = (R[2, 1] - R[1, 2]) / S
        q2 = (R[0, 2] - R[2, 0]) / S
        q3 = (R[1, 0] - R[0, 1]) / S
    elif R[0, 0] > R[1, 1] and R[0, 0] > R[2, 2]:
        S = np.sqrt(1.0 + R[0, 0] - R[1, 1] - R[2, 2]) * 2.0
        q0 = (R[2, 1] - R[1, 2]) / S
        q1 = 0.25 * S
        q2 = (R[0, 1] + R[1, 0]) / S
        q3 = (R[0, 2] + R[2, 0]) / S
    elif R[1, 1] > R[2, 2]:
        S = np.sqrt(1.0 + R[1, 1] - R[0, 0] - R[2, 2]) * 2.0
        q0 = (R[0, 2] - R[2, 0]) / S
        q1 = (R[0, 1] + R[1, 0]) / S
        q2 = 0.25 * S
        q3 = (R[1, 2] + R[2, 1]) / S
    else:
        S = np.sqrt(1.0 + R[2, 2] - R[0, 0] - R[1, 1]) * 2.0
        q0 = (R[1, 0] - R[0, 1]) / S
        q1 = (R[0, 2] + R[2, 0]) / S
        q2 = (R[1, 2] + R[2, 1]) / S
        q3 = 0.25 * S
    return float(q0), float(q1), float(q2), float(q3)


def _raw_sandwich(V: np.ndarray, X: np.ndarray) -> np.ndarray:
    """Raw f64 sandwich ``V X rev(V)`` — no unitize (construction / adjoint path)."""
    V = np.asarray(V, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    return geometric_product(geometric_product(V, X), reverse(V))


def grade1_sandwich_adjoint(V32: np.ndarray) -> np.ndarray:
    """5×5 matrix of the grade-1 sandwich outermorphism of unit versor ``V32``.

    Column ``j`` is the grade-1 part of ``V e_{j+1} rev(V)`` (basis e1..e5).
    Built via raw sandwich — never ``versor_apply`` on non-null basis vectors.
    """
    V = np.asarray(V32, dtype=np.float64)
    if V.shape != (N_COMPONENTS,):
        raise ValueError(f"grade1_sandwich_adjoint expects 32-vector, got {V.shape}")
    M = np.zeros((5, 5), dtype=np.float64)
    for j in range(5):
        ej = np.zeros(N_COMPONENTS, dtype=np.float64)
        ej[j + 1] = 1.0
        out = _raw_sandwich(V, ej)
        M[:, j] = out[1:6]
    return M


def _dehomogenize_cloud(
    P: np.ndarray,
    *,
    tol: float = _PROCRUSTES_WEIGHT_TOL,
) -> tuple[np.ndarray, np.ndarray]:
    """Projective dehomogenization of (5,K) conformal columns → (3,K') Euclidean.

    ``x = P[0:3] / w`` with ``w = P[4] - P[3]`` (e5 − e4). Columns with
    ``|w| < tol`` are dropped. Returns ``(X_3xKprime, keep_mask)``.
    """
    P = np.asarray(P, dtype=np.float64)
    if P.ndim != 2 or P.shape[0] != 5:
        raise ValueError(f"dehomogenize expects (5,K), got {P.shape}")
    w = P[4, :] - P[3, :]
    keep = np.abs(w) >= tol
    if not np.any(keep):
        raise ValueError(
            "conformal_procrustes: all points have degenerate conformal weight "
            f"(|e5-e4| < {tol:g})"
        )
    X = P[:3, keep] / w[keep]
    return X, keep


def _projective_cloud_residual(mapped: np.ndarray, Q: np.ndarray) -> float:
    """Weight-normalized Frobenius residual on (5,K) clouds, mean over K.

    Dilation changes homogeneous weight, so raw ``||M@P − Q||`` is large even
    when dehomogenized Euclidean images match. Normalize each column by its
    n_o weight ``w = e5 − e4`` before comparing.
    """
    mapped = np.asarray(mapped, dtype=np.float64)
    Q = np.asarray(Q, dtype=np.float64)
    K = mapped.shape[1]
    if K == 0:
        return 0.0
    wm = mapped[4, :] - mapped[3, :]
    wq = Q[4, :] - Q[3, :]
    acc = 0.0
    n = 0
    for k in range(K):
        if abs(wm[k]) < _PROCRUSTES_WEIGHT_TOL or abs(wq[k]) < _PROCRUSTES_WEIGHT_TOL:
            continue
        diff = mapped[:, k] / wm[k] - Q[:, k] / wq[k]
        acc += float(np.dot(diff, diff))
        n += 1
    if n == 0:
        raise ValueError("conformal_procrustes: no finite-weight columns for residual")
    return float(np.sqrt(acc) / n)


def _kabsch_similarity(
    X: np.ndarray,
    Y: np.ndarray,
    *,
    tol: float = _PROCRUSTES_WEIGHT_TOL,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Umeyama/Kabsch similarity: ``Y ≈ s R X + t`` with ``det(R)=+1``.

    Returns ``(s, R3, t)``. Source-degenerate scale → ``s=1``.
    """
    X = np.asarray(X, dtype=np.float64)
    Y = np.asarray(Y, dtype=np.float64)
    if X.shape != Y.shape or X.ndim != 2 or X.shape[0] != 3:
        raise ValueError(f"Kabsch expects matching (3,K) clouds, got {X.shape}/{Y.shape}")
    K = X.shape[1]
    if K == 0:
        raise ValueError("Kabsch requires at least one point")
    mu_x = X.mean(axis=1)
    mu_y = Y.mean(axis=1)
    Xc = X - mu_x[:, None]
    Yc = Y - mu_y[:, None]
    sig_x2 = float(np.sum(Xc * Xc))
    sig_y2 = float(np.sum(Yc * Yc))
    if sig_x2 <= tol:
        s = 1.0
    else:
        s = float(np.sqrt(sig_y2 / sig_x2))
    H = Xc @ Yc.T
    U, _S, Vt = np.linalg.svd(H)
    R3 = Vt.T @ U.T
    if np.linalg.det(R3) < 0.0:
        # Strip reflection (force proper rotation).
        Vt = Vt.copy()
        Vt[-1, :] *= -1.0
        R3 = Vt.T @ U.T
    t = mu_y - s * (R3 @ mu_x)
    return s, R3, t


def _assemble_similarity_versor(
    s: float,
    R3: np.ndarray,
    t: np.ndarray,
) -> np.ndarray:
    """Assemble ``V = T(t) * D(s) * R`` (Euclidean similarity ``x ↦ s R x + t``)."""
    s = float(s)
    if not np.isfinite(s) or s <= 0.0:
        raise ValueError(f"conformal_procrustes: non-positive scale {s}")
    R_mv = so3_matrix_to_rotor(R3)
    D = dilator(s) if abs(s - 1.0) > _NEAR_ZERO else _identity32()
    T = translator(np.asarray(t, dtype=np.float64))
    V = geometric_product(geometric_product(T, D), R_mv)
    # Construction-boundary strict close (no seed-to-rotor fabrication).
    return _strict_close_versor(V, name="assemble_similarity_versor")


def _kabsch_conformal_from_5clouds(
    P: np.ndarray,
    Q: np.ndarray,
    *,
    tol: float = _PROCRUSTES_WEIGHT_TOL,
) -> tuple[np.ndarray, np.ndarray, float]:
    """Full Kabsch-conformal on (5,K) clouds → ``(V32, M5x5, residual)``."""
    P = np.asarray(P, dtype=np.float64)
    Q = np.asarray(Q, dtype=np.float64)
    if P.shape != Q.shape or P.ndim != 2 or P.shape[0] != 5:
        raise ValueError(f"expected matching (5,K) clouds, got {P.shape}/{Q.shape}")
    K = P.shape[1]
    if K == 0:
        V = _identity32()
        return V, grade1_sandwich_adjoint(V), 0.0
    X, keep_p = _dehomogenize_cloud(P, tol=tol)
    Y, keep_q = _dehomogenize_cloud(Q, tol=tol)
    keep = keep_p & keep_q
    if not np.any(keep):
        raise ValueError("conformal_procrustes: no paired finite-weight columns")
    # Re-dehomogenize with joint mask (weights already gated).
    wP = P[4, keep] - P[3, keep]
    wQ = Q[4, keep] - Q[3, keep]
    X = P[:3, keep] / wP
    Y = Q[:3, keep] / wQ
    s, R3, t = _kabsch_similarity(X, Y, tol=tol)
    V32 = _assemble_similarity_versor(s, R3, t)
    cond = versor_condition(V32)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"conformal_procrustes: assembled versor not closed ({cond:.3e})")
    M = grade1_sandwich_adjoint(V32)
    residual = _projective_cloud_residual(M @ P, Q)
    return V32, M, residual


def _is_grade1_null(mv: np.ndarray, *, tol: float = 1e-6) -> bool:
    """True iff ``mv`` is (numerically) a grade-1 null vector (CGA point)."""
    mv = np.asarray(mv, dtype=np.float64)
    if mv.shape != (N_COMPONENTS,):
        return False
    off_g1 = float(np.linalg.norm(mv) - np.linalg.norm(mv[1:6]))
    # Cheaper: non-grade-1 mass.
    g1 = grade_project(mv, 1)
    if float(np.linalg.norm(mv - g1)) > tol * max(1.0, float(np.linalg.norm(mv))):
        return False
    if float(np.linalg.norm(g1)) < _NEAR_ZERO:
        return False
    return bool(is_null(mv, tol=tol))


def _mv_to_5(mv: np.ndarray) -> np.ndarray:
    return np.asarray(mv, dtype=np.float64)[1:6].copy()


def _left_gp_matrix(A: np.ndarray) -> np.ndarray:
    """Matrix L with ``L @ vec(B) = vec(A * B)``."""
    A = np.asarray(A, dtype=np.float64)
    L = np.zeros((N_COMPONENTS, N_COMPONENTS), dtype=np.float64)
    for j in range(N_COMPONENTS):
        ej = np.zeros(N_COMPONENTS, dtype=np.float64)
        ej[j] = 1.0
        L[:, j] = geometric_product(A, ej)
    return L


def _right_gp_matrix(A: np.ndarray) -> np.ndarray:
    """Matrix R with ``R @ vec(B) = vec(B * A)``."""
    A = np.asarray(A, dtype=np.float64)
    R = np.zeros((N_COMPONENTS, N_COMPONENTS), dtype=np.float64)
    for j in range(N_COMPONENTS):
        ej = np.zeros(N_COMPONENTS, dtype=np.float64)
        ej[j] = 1.0
        R[:, j] = geometric_product(ej, A)
    return R


def _strict_unitize_candidate(v: np.ndarray, *, tol: float = 1e-5) -> Optional[np.ndarray]:
    """Unitize only if ``v·rev(v)`` is already a positive scalar (no seed fallback)."""
    v = np.asarray(v, dtype=np.float64)
    if float(np.linalg.norm(v)) < _NEAR_ZERO:
        return None
    vv = geometric_product(v, reverse(v))
    off = float(np.linalg.norm(vv[1:]))
    sc = float(vv[0])
    if off > tol * max(1.0, abs(sc)) or sc <= 0.0:
        return None
    return (v / np.sqrt(sc)).astype(np.float64)


def _exp_bivector(B: np.ndarray) -> np.ndarray:
    """``exp(B)`` series for a pure bivector (construction path); strict-close at end."""
    B = np.asarray(B, dtype=np.float64)
    term = _identity32()
    out = term.copy()
    for k in range(1, 48):
        term = geometric_product(term, B) / float(k)
        out = out + term
        if float(np.linalg.norm(term)) < 1e-18:
            break
    return _strict_close_versor(out, name="exp_bivector")


def _field_conjugacy_versor(
    sources: Sequence[np.ndarray],
    targets: Sequence[np.ndarray],
    *,
    max_steps: int = _CONJUGACY_MAX_STEPS,
    tol: float = _CONJUGACY_RES_TOL,
) -> tuple[np.ndarray, float]:
    """Recover unit versor ``W`` with raw sandwich ``W·F_A·rev(W) ≈ F_B``.

    1. Build stacked linear conjugacy constraints ``W F_A − F_B W = 0``; the
       nullspace contains all conjugators (plus centralizer junk).
    2. Try strict-unitize of ± null singular vectors as candidates.
    3. Multiplicative Lie-algebra Gauss–Newton on Spin (left updates
       ``W ← exp(B) W``) minimizing mean raw-sandwich residual.

    Returns the best closed versor with an **honest residual** (may stay large
    when no conjugator exists, e.g. sandwich cannot map ``I → non-I``). Callers
    gate on residual — residual-honest, not raise-on-failure. Never left-
    composition via ``word_transition_rotor``; never ``versor_apply`` (which
    unitizes non-null images).
    """
    pairs = [
        (np.asarray(s, dtype=np.float64), np.asarray(t, dtype=np.float64))
        for s, t in zip(sources, targets)
    ]
    for i, (s, t) in enumerate(pairs):
        if s.shape != (N_COMPONENTS,) or t.shape != (N_COMPONENTS,):
            raise ValueError(f"pair[{i}] must be 32-component multivectors")

    # Linear conjugacy nullspace (design step); used for candidates + audit.
    blocks = [_right_gp_matrix(s) - _left_gp_matrix(t) for s, t in pairs]
    Mat = np.vstack(blocks)
    _u, svals, vh = np.linalg.svd(Mat, full_matrices=True)
    null_dim = int(np.sum(svals < 1e-8))
    candidates: list[np.ndarray] = [_identity32()]
    if null_dim > 0:
        for row in vh[-null_dim:]:
            for sgn in (1.0, -1.0):
                u = _strict_unitize_candidate(sgn * row)
                if u is not None:
                    candidates.append(u)

    def _mean_sandwich(W: np.ndarray) -> float:
        acc = 0.0
        for s, t in pairs:
            acc += float(np.linalg.norm(_raw_sandwich(W, s) - t) ** 2)
        return float(np.sqrt(acc / len(pairs)))

    best_W = candidates[0]
    best_r = _mean_sandwich(best_W)
    for c in candidates[1:]:
        r = _mean_sandwich(c)
        if r < best_r:
            best_r = r
            best_W = c
    if best_r < tol:
        cond = versor_condition(best_W)
        if cond >= _CLOSURE_TOL:
            raise ValueError(f"field conjugacy versor not closed: {cond:.3e}")
        return best_W, best_r

    # Multiplicative GN on Spin from best candidate (usually identity).
    W = best_W.copy()
    n = len(pairs)
    for _step in range(max_steps):
        rvec = np.zeros(N_COMPONENTS * n, dtype=np.float64)
        J = np.zeros((N_COMPONENTS * n, 10), dtype=np.float64)
        for i, (Fa, Fb) in enumerate(pairs):
            cur = _raw_sandwich(W, Fa)
            delta = Fb - cur
            rvec[N_COMPONENTS * i : N_COMPONENTS * (i + 1)] = delta
            for j, plane in enumerate(_BIVECTOR_PLANES):
                B = np.zeros(N_COMPONENTS, dtype=np.float64)
                B[plane] = 1.0
                # d/dε Ad_{exp(ε E_j) W} Fa |₀ ≈ [E_j, cur]
                J[N_COMPONENTS * i : N_COMPONENTS * (i + 1), j] = (
                    geometric_product(B, cur) - geometric_product(cur, B)
                )
        r = float(np.linalg.norm(rvec) / np.sqrt(n))
        if r < tol:
            best_W, best_r = W, r
            break
        b, _res, _rank, _sv = np.linalg.lstsq(J, rvec, rcond=None)
        alpha = 1.0
        improved = False
        for _ls in range(12):
            B = np.zeros(N_COMPONENTS, dtype=np.float64)
            B[6:16] = alpha * b
            try:
                E = _exp_bivector(B)
                W_try = _strict_close_versor(
                    geometric_product(E, W), name="conjugacy_GN"
                )
            except ValueError:
                alpha *= 0.5
                continue
            r_try = _mean_sandwich(W_try)
            if r_try < r:
                W = W_try
                best_W, best_r = W_try, r_try
                improved = True
                break
            alpha *= 0.5
        if not improved:
            break
        if best_r < tol:
            break

    cond = versor_condition(best_W)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"field conjugacy versor not closed: {cond:.3e}")
    # Return best closed versor with honest sandwich residual (may be large when
    # no conjugator exists — e.g. sandwich cannot map I → non-I). Callers gate
    # on residual; do not fabricate a low residual or raise as "success".
    return best_W, best_r


def conformal_procrustes(
    P: np.ndarray,
    Q: np.ndarray,
    max_iter: int = 32,
    tol: float = 1e-8,
) -> Tuple[np.ndarray, float]:
    """
    Kabsch-conformal Procrustes / field conjugacy (Super-Blueprint §3.1).

    Find best versor (or its grade-1 sandwich adjoint) mapping source ``P``
    onto target ``Q`` under the **sandwich** ``V·X·rev(V)``.

    Accepts:
      - ``P,Q`` shape ``(5, K)`` conformal vectors → returns ``(M_5x5, residual)``
        where ``M`` is the grade-1 sandwich adjoint of the assembled similarity
        versor ``V = T(t)·D(s)·R`` (Kabsch + Umeyama scale, det R = +1).
      - ``P,Q`` shape ``(32,)`` or sequences of 32-vectors:
          * all grade-1 null (CGA points) → Kabsch on extracted (5,K), returns
            **V32** (not 5×5) with sandwich residual;
          * otherwise field conjugacy ``W F_A = F_B W`` + sandwich residual,
            returns **V32**.

    Residual is always a sandwich / projective match residual (never a
    left-composition ``word_transition_rotor`` average). Off-serving geometry;
    not wired into chat/runtime.

    Returns ``(V, residual)`` matching the package contract.
    """
    weight_tol = float(tol) if tol is not None else _PROCRUSTES_WEIGHT_TOL
    _ = max_iter  # reserved; conjugacy uses its own step budget

    # Multivector sequence
    if isinstance(P, (list, tuple)):
        src_list = [np.asarray(p, dtype=np.float64) for p in P]
        tgt_list = [np.asarray(q, dtype=np.float64) for q in Q]
        if not isinstance(Q, (list, tuple)):
            raise ValueError("Q must be a sequence when P is a sequence")
        result = _procrustes_multivector_pairs(src_list, tgt_list, tol=weight_tol)
        return result.versor, result.residual_norm

    P_arr = np.asarray(P, dtype=np.float64)
    Q_arr = np.asarray(Q, dtype=np.float64)

    if P_arr.shape == (N_COMPONENTS,) and Q_arr.shape == (N_COMPONENTS,):
        result = _procrustes_multivector_pairs([P_arr], [Q_arr], tol=weight_tol)
        return result.versor, result.residual_norm

    if P_arr.ndim == 2 and P_arr.shape[0] == 5 and P_arr.shape == Q_arr.shape:
        _V32, M, residual = _kabsch_conformal_from_5clouds(P_arr, Q_arr, tol=weight_tol)
        return M, residual

    raise ValueError(
        "conformal_procrustes expects (5,K) point clouds, 32-vectors, or sequences thereof"
    )


def _procrustes_multivector_pairs(
    sources: Sequence[np.ndarray],
    targets: Sequence[np.ndarray],
    *,
    tol: float = _PROCRUSTES_WEIGHT_TOL,
) -> ConformalProcrustesResult:
    """32-vector Procrustes: Kabsch on null-point lists, else field conjugacy.

    Deletes the old ``word_transition_rotor`` averaging path (left composition).
    Residual is always raw sandwich residual (never left-composition).
    """
    if len(sources) != len(targets) or not sources:
        raise ValueError("sources/targets must be non-empty and equal length")
    src_list = [np.asarray(s, dtype=np.float64) for s in sources]
    tgt_list = [np.asarray(t, dtype=np.float64) for t in targets]
    for i, (s, t) in enumerate(zip(src_list, tgt_list)):
        if s.shape != (N_COMPONENTS,) or t.shape != (N_COMPONENTS,):
            raise ValueError(f"pair[{i}] must be 32-component multivectors")

    # Null-point cloud path: extract (5,K), Kabsch, return V32.
    if all(_is_grade1_null(s) and _is_grade1_null(t) for s, t in zip(src_list, tgt_list)):
        P = np.column_stack([_mv_to_5(s) for s in src_list])
        Q = np.column_stack([_mv_to_5(t) for t in tgt_list])
        V32, _M, _proj_r = _kabsch_conformal_from_5clouds(P, Q, tol=tol)
        pair_res = tuple(procrustes_residual(s, t, V32) for s, t in zip(src_list, tgt_list))
        residual_norm = float(np.sqrt(sum(r * r for r in pair_res) / len(pair_res)))
        cond = versor_condition(V32)
        if cond >= _CLOSURE_TOL:
            raise ValueError(f"Procrustes versor not closed: condition={cond:.3e}")
        return ConformalProcrustesResult(
            versor=V32,
            residual_norm=residual_norm,
            n_pairs=len(src_list),
            pair_residuals=pair_res,
        )

    # Field conjugacy / wave polar (ADR-0241 Slice 2–3): all non-null field paths
    # go through WaveManifold (single-pair polar; multi-pair thin conjugacy wrap).
    # Null-point clouds already returned above (Kabsch point-cloud path).
    from core.physics.wave_manifold import WaveManifold

    wave = WaveManifold()
    if len(src_list) == 1:
        V = wave.wave_analogical_polar(src_list[0], tgt_list[0])
    else:
        V, _engine_r = wave.wave_field_conjugacy(src_list, tgt_list)
    pair_res = tuple(
        procrustes_residual(s, t, V) for s, t in zip(src_list, tgt_list)
    )
    residual_norm = float(np.sqrt(sum(r * r for r in pair_res) / len(pair_res)))
    return ConformalProcrustesResult(
        versor=V,
        residual_norm=residual_norm,
        n_pairs=len(src_list),
        pair_residuals=pair_res,
    )


def cartan_iwasawa_extract(
    V: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Factor a conformal versor into Rotor · Translator · Dilator
    via explicit Cartan-Iwasawa (BCH-free).

    Returns (R, T, D).

    For 32-component unit versors: factors live in Cl(4,1) multivector space.
    5×5 sandwich-adjoint matrices are **not** supported (fail-closed) — pass the
    assembled 32-versor from Kabsch, not the grade-1 adjoint alone.
    """
    V_arr = np.asarray(V, dtype=np.float64)
    if V_arr.shape == (5, 5):
        raise ValueError(
            "cartan_iwasawa_extract: 5x5 adjoint path not supported; "
            "pass the assembled 32-component versor (V32)"
        )

    if V_arr.shape != (N_COMPONENTS,):
        raise ValueError(f"V must be 32-vector; got {V_arr.shape}")

    factors = cartan_iwasawa_factorize(V_arr)
    return factors.R, factors.T, factors.D


def cartan_iwasawa_factorize(V: np.ndarray) -> CartanIwasawaFactors:
    """Factor a closed conformal versor into Rotor · Translator · Dilator.

    Super-Blueprint §2.2 (null-point peel) for similarities, plus an honest
    remainder-as-rotor path for general Spin(4,1) elements that do not fix
    infinity (multi-plane rotors that are not Euclidean similarities).

    Algorithm
    ---------
    1. Validate V is a 32-vector; at this construction boundary, unitize once
       when the input is salvageably open (existing soft threshold); require
       final ``versor_condition < 1e-6`` or raise (fail-closed).
    2. **Similarity path** — peel via null-point recovery (right-to-left for
       reconstruction order ``R * T * D``)::

           s, D = recover_dilation(V)
           V1   = unitize(V * reverse(D))
           a, T = recover_translation(V1)
           R    = unitize(V1 * reverse(T))

       Any :class:`~algebra.null_point.NullPointRecoveryError` (or a unitize
       failure after a partial peel) falls through to the general path — never
       fabricate broken R/D seeds.
    3. **General Spin path** — not a similarity / peel failed: ``R = V``,
       ``T = I``, ``D = I`` (perfect reconstruction; R carries the full motion).
    4. Assert each factor is closed; return residual ``‖R·T·D − V‖``.

    Off-serving geometry only: not wired into chat/runtime.
    """
    V_arr = np.asarray(V, dtype=np.float64)
    if V_arr.shape != (N_COMPONENTS,):
        raise ValueError(f"V must have shape ({N_COMPONENTS},)")
    # Strict construction-boundary close: rescale only when V·rev(V) is already
    # scalar (a true versor up to weight). Never seed-to-rotor fabrications.
    V_arr = _strict_close_versor(V_arr, name="cartan_iwasawa_factorize")

    I = _identity32()
    used_peel = False
    try:
        # Similarity path: Super §2.2 null-point peel (right-peel D then T).
        _s, D = recover_dilation(V_arr)
        V1 = _strict_close_versor(
            geometric_product(V_arr, reverse(D)), name="cartan_peel_D"
        )
        _a, T = recover_translation(V1)
        R = _strict_close_versor(
            geometric_product(V1, reverse(T)), name="cartan_peel_T"
        )
        used_peel = True
    except (NullPointRecoveryError, ValueError):
        # General Spin(4,1): remainder-as-rotor — honest, exact reconstruction.
        R, T, D = V_arr.copy(), I.copy(), I.copy()

    recon = geometric_product(geometric_product(R, T), D)
    recon_res = float(np.linalg.norm(recon - V_arr))
    if used_peel and recon_res >= _CLOSURE_TOL:
        # Peel produced closed factors that do not reconstruct — fall back to
        # honest Spin remainder rather than hand a wrong factorization downstream.
        R, T, D = V_arr.copy(), I.copy(), I.copy()
        recon = geometric_product(geometric_product(R, T), D)
        recon_res = float(np.linalg.norm(recon - V_arr))
    for name, f in (("R", R), ("T", T), ("D", D)):
        c = versor_condition(f)
        if c >= _CLOSURE_TOL:
            # Fail-closed: never return a broken R/T/D seed.
            raise ValueError(f"Cartan–Iwasawa factor {name} not closed: {c:.3e}")
    return CartanIwasawaFactors(
        R=R, T=T, D=D, reconstruction_residual=recon_res
    )


def dual_correction_slerp(
    source: np.ndarray,
    target: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Slerp on Cartan–Iwasawa factors via left composition."""
    a = float(alpha)
    if a < 0.0 or a > 1.0:
        raise ValueError("alpha must be in [0, 1]")
    src = np.asarray(source, dtype=np.float64)
    tgt = np.asarray(target, dtype=np.float64)
    if a <= _NEAR_ZERO:
        out = src.copy()
    elif a >= 1.0 - _NEAR_ZERO:
        out = tgt.copy()
    else:
        V = word_transition_rotor(src, tgt)
        fac = cartan_iwasawa_factorize(V)
        R_a = rotor_power(fac.R, a)
        T_a = rotor_power(fac.T, a)
        D_a = rotor_power(fac.D, a)
        V_a = geometric_product(geometric_product(R_a, T_a), D_a)
        V_a = _strict_close_versor(V_a, name="dual_correction_slerp")
        out = geometric_product(V_a, src).astype(np.float64)
    if versor_condition(out) >= _CLOSURE_TOL:
        raise ValueError("dual_correction_slerp broke closure")
    return out
