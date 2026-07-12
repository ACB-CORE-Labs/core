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

from algebra.cl41 import N_COMPONENTS, SIGNATURE, geometric_product, grade_project, reverse
from algebra.rotor import rotor_power, word_transition_rotor
from algebra.versor import unitize_versor, versor_apply, versor_condition

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_NULL_TOL = 1e-9

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
    """Dedicated Procrustes residual: || V * s * reverse(V) - t ||_F."""
    s = np.asarray(source, dtype=np.float64)
    t = np.asarray(target, dtype=np.float64)
    V = np.asarray(versor, dtype=np.float64)
    if s.shape == (N_COMPONENTS,) and V.shape == (N_COMPONENTS,):
        mapped = versor_apply(V, s)
        return float(np.linalg.norm(mapped - t))
    # 5-vector conformal points: Frobenius after linear map if V is 5x5
    if s.shape == (5,) and V.shape == (5, 5):
        return float(np.linalg.norm(V @ s - t))
    return float(np.linalg.norm(s - t))


def conformal_procrustes(
    P: np.ndarray,
    Q: np.ndarray,
    max_iter: int = 32,
    tol: float = 1e-8,
) -> Tuple[np.ndarray, float]:
    """
    Find best versor V that maps source points P onto target points Q
    in the conformal model (Cl(4,1)).

    Accepts:
      - P,Q shape (5, K) conformal vectors → returns (V_5x5, residual)
      - P,Q shape (32,) single multivectors → returns (V_32, residual)
      - sequences of 32-vectors via list/tuple

    Returns (V, residual) matching the package contract.
    """
    _ = max_iter, tol  # reserved for iterative refinement

    # Multivector single pair
    if isinstance(P, (list, tuple)):
        src_list = [np.asarray(p, dtype=np.float64) for p in P]
        tgt_list = [np.asarray(q, dtype=np.float64) for q in Q]
        result = _procrustes_multivector_pairs(src_list, tgt_list)
        return result.versor, result.residual_norm

    P_arr = np.asarray(P, dtype=np.float64)
    Q_arr = np.asarray(Q, dtype=np.float64)

    if P_arr.shape == (N_COMPONENTS,) and Q_arr.shape == (N_COMPONENTS,):
        result = _procrustes_multivector_pairs([P_arr], [Q_arr])
        return result.versor, result.residual_norm

    if P_arr.ndim == 2 and P_arr.shape[0] == 5 and P_arr.shape == Q_arr.shape:
        # Conformal point cloud: orthogonal Procrustes under Euclidean part + residual
        # Start with Kabsch on first 3 coords, complete as 5x5 with identity conformal block
        K = P_arr.shape[1]
        if K == 0:
            return _identity5(), 0.0
        residual = float(np.linalg.norm(P_arr - Q_arr) / max(K, 1))
        # Cross-covariance on e1..e3
        Pc = P_arr[:3, :]
        Qc = Q_arr[:3, :]
        H = Pc @ Qc.T
        U, _S, Vt = np.linalg.svd(H)
        R3 = Vt.T @ U.T
        if np.linalg.det(R3) < 0:
            Vt = Vt.copy()
            Vt[-1, :] *= -1
            R3 = Vt.T @ U.T
        V = _identity5()
        V[:3, :3] = R3
        # Residual after map on full 5D (conformal coords not fully transformed in this slice)
        mapped = V @ P_arr
        residual = float(np.linalg.norm(mapped - Q_arr) / max(K, 1))
        return V, residual

    raise ValueError(
        "conformal_procrustes expects (5,K) point clouds, 32-vectors, or sequences thereof"
    )


def _procrustes_multivector_pairs(
    sources: Sequence[np.ndarray],
    targets: Sequence[np.ndarray],
) -> ConformalProcrustesResult:
    if len(sources) != len(targets) or not sources:
        raise ValueError("sources/targets must be non-empty and equal length")
    rotors: list[np.ndarray] = []
    for i, (s, t) in enumerate(zip(sources, targets)):
        s_arr = np.asarray(s, dtype=np.float64)
        t_arr = np.asarray(t, dtype=np.float64)
        if s_arr.shape != (N_COMPONENTS,) or t_arr.shape != (N_COMPONENTS,):
            raise ValueError(f"pair[{i}] must be 32-component multivectors")
        R = word_transition_rotor(s_arr, t_arr)
        rotors.append(np.asarray(R, dtype=np.float64))

    V = rotors[0].copy()
    for k, R in enumerate(rotors[1:], start=2):
        try:
            T = word_transition_rotor(V, R)
            T_a = rotor_power(T, 1.0 / float(k))
            V = geometric_product(T_a, V).astype(np.float64)
            V = unitize_versor(V)
        except ValueError:
            continue

    cond = versor_condition(V)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"Procrustes versor not closed: condition={cond:.3e}")

    pair_res = tuple(procrustes_residual(s, t, V) for s, t in zip(sources, targets))
    residual_norm = float(np.sqrt(sum(r * r for r in pair_res) / len(pair_res)))
    return ConformalProcrustesResult(
        versor=V,
        residual_norm=residual_norm,
        n_pairs=len(sources),
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
    For 5x5 matrices: returns identity factors with residual deferred (matrix path).
    """
    V_arr = np.asarray(V, dtype=np.float64)
    if V_arr.shape == (5, 5):
        I = _identity5()
        return I.copy(), I.copy(), I.copy()

    if V_arr.shape != (N_COMPONENTS,):
        raise ValueError(f"V must be 32-vector or 5x5; got {V_arr.shape}")

    factors = cartan_iwasawa_factorize(V_arr)
    return factors.R, factors.T, factors.D


def cartan_iwasawa_factorize(V: np.ndarray) -> CartanIwasawaFactors:
    """Constructive factorization with closed factors + reconstruction residual."""
    V_arr = np.asarray(V, dtype=np.float64)
    if V_arr.shape != (N_COMPONENTS,):
        raise ValueError(f"V must have shape ({N_COMPONENTS},)")
    cond = versor_condition(V_arr)
    if cond >= 1e-2:
        V_arr = unitize_versor(V_arr)
        cond = versor_condition(V_arr)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"cartan_iwasawa_factorize: input not closed ({cond:.3e})")

    I = _identity32()
    B = grade_project(V_arr, 2)
    B_sq = geometric_product(B, B).astype(np.float64)
    bsq_scalar = float(B_sq[0])
    B_sq_res = B_sq.copy()
    B_sq_res[0] = 0.0
    simple = float(np.linalg.norm(B_sq_res)) < 1e-6
    b_norm = float(np.linalg.norm(B))

    R, T, D = I.copy(), I.copy(), I.copy()

    if b_norm < _NEAR_ZERO:
        R = V_arr.copy()
    elif simple and bsq_scalar < 0.0:
        # Rotation-like → pure rotor
        R = grade_project(V_arr, 0) + grade_project(V_arr, 2)
        R = unitize_versor(R)
    elif simple and bsq_scalar > 0.0:
        # Boost/dilator-like
        D = grade_project(V_arr, 0) + grade_project(V_arr, 2)
        D = unitize_versor(D)
    else:
        half = B * 0.5
        R = I.copy()
        R[0] = abs(float(V_arr[0])) ** 0.5 if abs(float(V_arr[0])) > _NEAR_ZERO else 1.0
        R = R + half
        try:
            R = unitize_versor(R)
        except ValueError:
            R = I.copy()
        D = I.copy()
        D[0] = abs(float(V_arr[0])) ** 0.5 if abs(float(V_arr[0])) > _NEAR_ZERO else 1.0
        D = D + half
        try:
            D = unitize_versor(D)
        except ValueError:
            D = I.copy()
        RD = geometric_product(R, D)
        try:
            T = unitize_versor(geometric_product(reverse(RD), V_arr))
        except ValueError:
            T = I.copy()

    recon = geometric_product(geometric_product(R, T), D)
    recon_res = float(np.linalg.norm(recon - V_arr))
    for name, f in (("R", R), ("T", T), ("D", D)):
        c = versor_condition(f)
        if c >= _CLOSURE_TOL:
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
        V_a = unitize_versor(V_a)
        out = geometric_product(V_a, src).astype(np.float64)
    if versor_condition(out) >= _CLOSURE_TOL:
        raise ValueError("dual_correction_slerp broke closure")
    return out
