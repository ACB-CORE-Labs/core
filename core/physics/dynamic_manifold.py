"""core.physics.dynamic_manifold — Conformal manifold operators (ADR-0239).

Signature-aware PCA with explicit null classification, Conformal Procrustes
(versor search for structural analogy), Cartan–Iwasawa constructive
factorization for dual-correction slerp, and a dedicated Procrustes residual
norm (not null-margin; not ADR-0006 energy residual).

All operators are pure and deterministic. Null eigenvectors are never silently
skipped — they are classified and returned.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Sequence

import numpy as np

from algebra.cl41 import (
    N_COMPONENTS,
    SIGNATURE,
    geometric_product,
    grade_project,
    reverse,
)
from algebra.rotor import word_transition_rotor
from algebra.versor import unitize_versor, versor_apply, versor_condition

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_NULL_TOL = 1e-8
_METRIC = np.ones(N_COMPONENTS, dtype=np.float64)
# Grade-1 components (indices 1..5) carry Cl(4,1) signature (+,+,+,+,-).
_METRIC[1:6] = SIGNATURE.astype(np.float64)


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
    mean: tuple[float, ...]
    explained: tuple[float, ...]
    n_points: int
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
    """Constructive K · A · N factorization for dual-correction surfaces.

    K — compact (rotation-like, B² < 0 planes)
    A — abelian (boost-like, B² > 0 planes)
    N — nilpotent / residual (null + higher-grade remainder, unitized if needed)
    """

    K: np.ndarray
    A: np.ndarray
    N: np.ndarray
    reconstruction_residual: float


def _as_points(points: Sequence[np.ndarray]) -> np.ndarray:
    if not points:
        raise ValueError("signature_aware_pca requires at least one point")
    rows = []
    for i, p in enumerate(points):
        arr = np.asarray(p, dtype=np.float64)
        if arr.shape != (N_COMPONENTS,):
            raise ValueError(
                f"point[{i}] must have shape ({N_COMPONENTS},); got {arr.shape}"
            )
        rows.append(arr)
    return np.stack(rows, axis=0)


def _metric_quadratic_form(v: np.ndarray) -> float:
    """Quadratic form on grade-1 part under Cl(4,1) signature; higher grades +.

    Used only for axis *classification*, not as a substitute for versor_condition.
    """
    g1 = v[1:6]
    q = float(np.dot(g1 * _METRIC[1:6], g1))
    higher = float(np.dot(v[6:], v[6:]))
    scalar = float(v[0] * v[0])
    return q + higher + scalar


def _classify_axis(v: np.ndarray) -> tuple[AxisClassification, float]:
    nrm = float(np.linalg.norm(v))
    if nrm < _NEAR_ZERO:
        return AxisClassification.DEGENERATE, 0.0
    q = _metric_quadratic_form(v)
    # Grade-1 signature sense dominates classification when g1 is present.
    g1 = v[1:6]
    g1_q = float(np.dot(g1 * _METRIC[1:6], g1))
    g1_n = float(np.linalg.norm(g1))
    if g1_n < _NEAR_ZERO:
        # Pure higher-grade axis: treat as spacelike if energy present else degenerate.
        if nrm < _NULL_TOL:
            return AxisClassification.DEGENERATE, q
        return AxisClassification.SPACELIKE, q
    if abs(g1_q) < _NULL_TOL:
        return AxisClassification.NULL, g1_q
    if g1_q > 0.0:
        return AxisClassification.SPACELIKE, g1_q
    return AxisClassification.TIMELIKE, g1_q


def signature_aware_pca(
    points: Sequence[np.ndarray],
    *,
    max_axes: int | None = None,
) -> SignatureAwarePCAResult:
    """Signature-aware PCA on Cl(4,1) multivector clouds.

    1. Center the cloud in coefficient space.
    2. Form the metric-rescaled covariance (whitening by √|G| on coords).
    3. Eigen-decompose symmetrically (deterministic via numpy eigh).
    4. Classify every axis — null axes are returned, never dropped.
    """
    X = _as_points(points)
    n = X.shape[0]
    mean = X.mean(axis=0)
    Xc = X - mean

    # Metric rescaling: multiply each coordinate by sqrt(|g_ii|)*sign-preserving weight.
    # For signature -1 on e5, use imaginary-free absolute metric then restore sense
    # via classification (not by complex eigen).
    scale = np.sqrt(np.abs(_METRIC))
    scale = np.where(scale < _NEAR_ZERO, 1.0, scale)
    Y = Xc * scale  # broadcast

    # Covariance of rescaled coordinates.
    if n == 1:
        cov = np.zeros((N_COMPONENTS, N_COMPONENTS), dtype=np.float64)
    else:
        cov = (Y.T @ Y) / float(n)

    # Symmetric eigh → ascending eigenvalues; reverse for explained variance order.
    evals, evecs = np.linalg.eigh(cov)
    order = np.argsort(evals)[::-1]
    evals = evals[order]
    evecs = evecs[:, order]

    k = N_COMPONENTS if max_axes is None else min(int(max_axes), N_COMPONENTS)
    total = float(np.sum(np.clip(evals, 0.0, None)))
    axes: list[PrincipalAxis] = []
    counts = {
        AxisClassification.NULL: 0,
        AxisClassification.SPACELIKE: 0,
        AxisClassification.TIMELIKE: 0,
        AxisClassification.DEGENERATE: 0,
    }
    explained_list: list[float] = []

    for i in range(k):
        # Map eigenvector back from metric-rescaled coords.
        v_scaled = evecs[:, i]
        v = v_scaled / scale
        nrm = float(np.linalg.norm(v))
        if nrm > _NEAR_ZERO:
            v = v / nrm
        # Deterministic sign convention: first nonzero component positive.
        for c in v:
            if abs(c) > _NEAR_ZERO:
                if c < 0.0:
                    v = -v
                break
        cls, mq = _classify_axis(v)
        counts[cls] = counts.get(cls, 0) + 1
        ev = float(max(0.0, evals[i]))
        frac = float(ev / total) if total > _NEAR_ZERO else 0.0
        explained_list.append(frac)
        axes.append(
            PrincipalAxis(
                vector=tuple(float(x) for x in v),
                eigenvalue=ev,
                classification=cls,
                metric_quadratic=float(mq),
            )
        )

    return SignatureAwarePCAResult(
        axes=tuple(axes),
        mean=tuple(float(x) for x in mean),
        explained=tuple(explained_list),
        n_points=n,
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
    """Dedicated Procrustes residual: || V * s * reverse(V) - t ||_F.

    Named separately from null-margin and energy coherence_residual so it
    cannot be silently reused as a different residual.
    """
    s = np.asarray(source, dtype=np.float64)
    t = np.asarray(target, dtype=np.float64)
    V = np.asarray(versor, dtype=np.float64)
    mapped = versor_apply(V, s)
    return float(np.linalg.norm(mapped - t))


def conformal_procrustes(
    sources: Sequence[np.ndarray] | np.ndarray,
    targets: Sequence[np.ndarray] | np.ndarray,
) -> ConformalProcrustesResult:
    """Find a unit versor aligning source structure to target structure.

    Single pair: closed transition rotor.
    Multiple pairs: manifold average of per-pair transition rotors via
    successive equal-weight slerp composition (deterministic order).
    """
    if isinstance(sources, np.ndarray) and sources.ndim == 1:
        src_list = [sources]
    else:
        src_list = list(sources)  # type: ignore[arg-type]
    if isinstance(targets, np.ndarray) and targets.ndim == 1:
        tgt_list = [targets]
    else:
        tgt_list = list(targets)  # type: ignore[arg-type]

    if len(src_list) != len(tgt_list):
        raise ValueError("sources and targets must have equal length")
    if not src_list:
        raise ValueError("conformal_procrustes requires at least one pair")

    rotors: list[np.ndarray] = []
    for i, (s, t) in enumerate(zip(src_list, tgt_list)):
        s_arr = np.asarray(s, dtype=np.float64)
        t_arr = np.asarray(t, dtype=np.float64)
        if s_arr.shape != (N_COMPONENTS,) or t_arr.shape != (N_COMPONENTS,):
            raise ValueError(f"pair[{i}] must be 32-component multivectors")
        # Construction boundary: transition rotor is a closed unit versor.
        R = word_transition_rotor(s_arr, t_arr)
        rotors.append(np.asarray(R, dtype=np.float64))

    # Manifold average: sequential geodesic midpoints in pair order.
    V = rotors[0].copy()
    for k, R in enumerate(rotors[1:], start=2):
        # Slerp V toward R with weight 1/k so equal contribution in the limit.
        try:
            T = word_transition_rotor(V, R)
            from algebra.rotor import rotor_power

            T_a = rotor_power(T, 1.0 / float(k))
            V = geometric_product(geometric_product(T_a, V), reverse(T_a)).astype(
                np.float64
            )
            V = unitize_versor(V)
        except ValueError:
            # Fail closed to previous average if a pair is non-connectable.
            continue

    cond = versor_condition(V)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"Procrustes versor not closed: condition={cond:.3e}")

    pair_res = tuple(
        procrustes_residual(s, t, V) for s, t in zip(src_list, tgt_list)
    )
    residual_norm = float(np.sqrt(sum(r * r for r in pair_res) / len(pair_res)))
    return ConformalProcrustesResult(
        versor=V.astype(np.float64, copy=False),
        residual_norm=residual_norm,
        n_pairs=len(src_list),
        pair_residuals=pair_res,
    )


def _identity_mv() -> np.ndarray:
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    out[0] = 1.0
    return out


def cartan_iwasawa_factorize(V: np.ndarray) -> CartanIwasawaFactors:
    """Constructive Cartan–Iwasawa-style factorization of a closed versor.

    For simple scalar+bivector rotors:
    - If B² < 0 → pure K (rotation)
    - If B² > 0 → pure A (boost)
    - If B² ≈ 0 and B ≠ 0 → pure N (null)
    - Mixed: split bivector energy by sign of B² contribution and leave residual N.

    Reconstruction: K * A * N; residual measured in coefficient space.
    """
    V_arr = np.asarray(V, dtype=np.float64)
    if V_arr.shape != (N_COMPONENTS,):
        raise ValueError(f"V must have shape ({N_COMPONENTS},)")
    cond = versor_condition(V_arr)
    if cond >= 1e-2:
        # Construction boundary: attempt unitize only at this explicit boundary.
        V_arr = unitize_versor(V_arr)
        cond = versor_condition(V_arr)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"cartan_iwasawa_factorize: input not closed ({cond:.3e})")

    scalar = float(V_arr[0])
    B = grade_project(V_arr, 2)
    higher = V_arr.copy()
    higher[0] = 0.0
    higher[6:16] = 0.0  # clear grade-2; keep 1,3,4,5

    B_sq = geometric_product(B, B).astype(np.float64)
    bsq_scalar = float(B_sq[0])
    B_sq_res = B_sq.copy()
    B_sq_res[0] = 0.0
    simple = float(np.linalg.norm(B_sq_res)) < 1e-6
    b_norm = float(np.linalg.norm(B))

    I = _identity_mv()
    K = I.copy()
    A = I.copy()
    N = I.copy()

    if b_norm < _NEAR_ZERO and float(np.linalg.norm(higher)) < _NEAR_ZERO:
        # Near-identity
        K = V_arr.copy()
    elif simple and bsq_scalar < 0.0:
        K = V_arr.copy()
        # Zero out non-scalar/bivector if any residual grades present.
        K = grade_project(K, 0) + grade_project(K, 2)
        K = unitize_versor(K)
    elif simple and bsq_scalar > 0.0:
        A = grade_project(V_arr, 0) + grade_project(V_arr, 2)
        A = unitize_versor(A)
    elif simple and abs(bsq_scalar) <= _NEAR_ZERO:
        N_cand = grade_project(V_arr, 0) + grade_project(V_arr, 2)
        try:
            N = unitize_versor(N_cand)
        except ValueError:
            N = I.copy()
            N[0] = scalar if abs(scalar) > _NEAR_ZERO else 1.0
            N = unitize_versor(N)
    else:
        # Mixed: put scalar+rotation-like half in K, boost-like half in A, rest N.
        # Split B into two parallel bivectors by halving coefficients when non-simple.
        half = B * 0.5
        K = grade_project(V_arr, 0) * 0.0
        K[0] = abs(scalar) ** 0.5 if abs(scalar) > _NEAR_ZERO else 1.0
        K = K + half
        try:
            K = unitize_versor(K)
        except ValueError:
            K = I.copy()
        A = I.copy()
        A[0] = abs(scalar) ** 0.5 if abs(scalar) > _NEAR_ZERO else 1.0
        A = A + half
        try:
            A = unitize_versor(A)
        except ValueError:
            A = I.copy()
        # N absorbs higher-grade residual relative to K*A
        KA = geometric_product(K, A)
        try:
            N = unitize_versor(geometric_product(reverse(KA), V_arr))
        except ValueError:
            N = I.copy()

    recon = geometric_product(geometric_product(K, A), N)
    recon_res = float(np.linalg.norm(recon - V_arr))

    for name, factor in (("K", K), ("A", A), ("N", N)):
        c = versor_condition(factor)
        if c >= _CLOSURE_TOL:
            raise ValueError(f"Cartan–Iwasawa factor {name} not closed: {c:.3e}")

    return CartanIwasawaFactors(
        K=K.astype(np.float64, copy=False),
        A=A.astype(np.float64, copy=False),
        N=N.astype(np.float64, copy=False),
        reconstruction_residual=recon_res,
    )


def dual_correction_slerp(
    source: np.ndarray,
    target: np.ndarray,
    alpha: float,
) -> np.ndarray:
    """Slerp on Cartan–Iwasawa factors of the transition rotor (dual-correction).

    Factors are powered independently then recomposed as left action on source:

        R = target * reverse(source) = K A N
        out = (K^α A^α N^α) * source

    α=0 → source; α=1 → target for unit versors. Sandwich conjugation is not
    the state geodesic (see ADR-0238 supervised_blend).
    """
    from algebra.rotor import rotor_power

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
        R = word_transition_rotor(src, tgt)
        factors = cartan_iwasawa_factorize(R)
        K_a = rotor_power(factors.K, a)
        A_a = rotor_power(factors.A, a)
        N_a = rotor_power(factors.N, a)
        R_a = geometric_product(geometric_product(K_a, A_a), N_a)
        R_a = unitize_versor(R_a)
        out = geometric_product(R_a, src).astype(np.float64)
    cond = versor_condition(out)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"dual_correction_slerp broke closure: {cond:.3e}")
    return out
