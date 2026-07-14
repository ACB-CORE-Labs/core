"""
algebra/rotor.py — Rotor construction operators for Cl(4,1).

Rotors are operators. They live here, in algebra/, not in vocab/.
A rotor between two word-versors is a contextual, field-level concern:
it describes a transformation being applied, not a property of the vocabulary.
"""

import numpy as np

from .cl41 import N_COMPONENTS, geometric_product, grade_project, reverse, scalar_part
from .versor import unitize_versor, versor_condition

_TRANSITION_CONDITION_TOL = 1e-4
_NEAR_ZERO_TOL = 1e-12
_SAME_POINT_TOL = 1e-6
_STRICT_RESIDUE_TOL = 1e-2
# A rotor is SIMPLE iff its grade-4 part vanishes (<R>_4 == 0 <=> R = R1 with a
# single invariant plane). Above this, the rotor needs the invariant split.
_SIMPLE_GRADE4_TOL = 1e-10
# After the invariant (bivector) split, each factor is *approximately* simple;
# B² higher-grade residual is float dust, not a true multi-plane bivector.
# 1e-6 was too tight (raised on live word-transition / stream weights ≈ 1e-6..1e-3).
# Refuse only residuals that are clearly structural non-simplicity.
_SIMPLE_BSQ_HIGHER_TOL = 1e-3
# |discriminant| below this => the two invariant eigenvalues coincide (isoclinic).
_DEGEN_TOL = 1e-9


def _identity(dtype: np.dtype) -> np.ndarray:
    rotor = np.zeros(N_COMPONENTS, dtype=dtype)
    rotor[0] = 1.0
    return rotor


def _result_dtype(*arrays: np.ndarray) -> np.dtype:
    dtype = np.result_type(*arrays)
    return dtype if dtype in (np.dtype(np.float32), np.dtype(np.float64)) else np.dtype(np.float32)


def _strict_unitize_versor(v: np.ndarray, dtype: np.dtype) -> np.ndarray:
    """Unitize only already-closed versor candidates.

    ``unitize_versor`` intentionally supports dense construction seeds for
    ingest/compiler boundaries. Transition construction is not such a boundary:
    if the product candidate is not already a closed versor, fabricating a
    deterministic fallback rotor would sever the transition from its source and
    target. This helper therefore fails closed instead of using construction
    seed fallback semantics.
    """
    arr = np.asarray(v, dtype=np.float64)
    input_norm = float(np.linalg.norm(arr))
    if input_norm < _NEAR_ZERO_TOL:
        raise ValueError("word_transition_rotor: near_zero candidate")

    product = geometric_product(arr, reverse(arr)).astype(np.float64)
    scalar_sq = float(product[0])
    residue = product.copy()
    residue[0] = 0.0
    residue_norm = float(np.linalg.norm(residue))
    if residue_norm >= _STRICT_RESIDUE_TOL:
        raise ValueError(
            "word_transition_rotor: non_closed candidate; "
            f"residue_norm={residue_norm:.6e}"
        )
    if scalar_sq <= 0.0:
        raise ValueError(
            "word_transition_rotor: non_positive candidate; "
            f"scalar_sq={scalar_sq:.6e}"
        )
    return (arr * (1.0 / np.sqrt(scalar_sq))).astype(dtype)


def make_rotor_from_angle(angle: float, bivector_idx: int = 6) -> np.ndarray:
    """Construct a scalar+bivector unit rotor from an angle."""
    if not 0 <= int(bivector_idx) < N_COMPONENTS:
        raise ValueError(f"bivector_idx out of range: {bivector_idx!r}")
    rotor = np.zeros(N_COMPONENTS, dtype=np.float64)
    half_angle = float(angle) / 2.0
    rotor[0] = np.cos(half_angle)
    rotor[int(bivector_idx)] = np.sin(half_angle)
    return unitize_versor(rotor)


def rotor_power(R: np.ndarray, alpha: float) -> np.ndarray:
    """Return R^alpha — the rotor on the manifold path from identity to R by alpha.

    EXACT for ANY closed unit rotor in Cl(4,1), simple or not. A general rotor
    factors (invariant / bivector decomposition) into two commuting SIMPLE
    rotors ``R = R1 R2`` with distinct invariant planes; then, because they
    commute, ``R^α = R1^α R2^α`` and each factor uses the simple closed form
    below. The isoclinic case (coincident invariant planes) has its own closed
    form. There is no iteration, no approximation, and no external library —
    the split is built from the Cl(4,1) geometric product alone.

    Simple factor ``R_i = a + B`` (scalar + simple bivector):

    - rotation plane (``B² < 0``):  ``R^α = cos(α·θ/2) + (sin(α·θ/2)/|B|) · B``
      where ``θ/2 = atan2(|B|, a)``.
    - boost plane (``B² > 0``):     ``R^α = cosh(α·η/2) + (sinh(α·η/2)/|B|) · B``
      where ``η/2 = atanh(|B|/a)``.

    The result stays on the rotor manifold by construction, so
    ``versor_condition(rotor_power(R, α)) < 1e-6`` for any α whenever ``R`` is a
    closed unit rotor. (Historically this returned the *identity* for non-simple
    rotors — an approximation where exactness was available, which silently
    collapsed geodesic interpolation to a no-op. That corner is now closed.)
    """
    R_arr = np.asarray(R, dtype=np.float64)
    if R_arr.shape != (N_COMPONENTS,):
        raise ValueError(
            f"rotor_power expects a {N_COMPONENTS}-component rotor; got {R_arr.shape}."
        )
    dtype = _result_dtype(R_arr)
    a = float(alpha)
    # Endpoints by continuity: R^0 = 1, R^1 = R. Stream weights can be denormal
    # tiny; never run the invariant split on α≈0 (smoke / generate.stream path).
    if abs(a) <= _NEAR_ZERO_TOL:
        return _identity(dtype)
    if abs(a - 1.0) <= _NEAR_ZERO_TOL:
        return R_arr.astype(dtype, copy=True)
    # <R>_4 == 0  <=>  R is a single simple rotor. Otherwise take the split path.
    if float(np.linalg.norm(grade_project(R_arr, 4))) >= _SIMPLE_GRADE4_TOL:
        return _general_rotor_power(R_arr, a, dtype)
    return _simple_rotor_power(R_arr, a, dtype)


def _simple_rotor_power(R_arr: np.ndarray, alpha: float, dtype: np.dtype) -> np.ndarray:
    """R^alpha for a SIMPLE rotor (scalar + one simple bivector). Exact closed form.

    Behaviour is unchanged from the original ``rotor_power`` on simple inputs.
    """
    a = float(R_arr[0])
    B = R_arr.copy()
    B[0] = 0.0

    # A simple rotor's bivector squares to a scalar (B² is grade-0 only).
    # Higher-grade residual above _SIMPLE_BSQ_HIGHER_TOL is structural non-simplicity
    # (fail closed). Below that, treat as float dust from the invariant split and
    # use only the scalar part of B² (closed form still exact on the simple plane).
    B_sq_full = geometric_product(B, B).astype(np.float64)
    bsq_scalar = float(B_sq_full[0])
    B_sq_higher = B_sq_full.copy()
    B_sq_higher[0] = 0.0
    higher_norm = float(np.linalg.norm(B_sq_higher))
    if higher_norm > _SIMPLE_BSQ_HIGHER_TOL:
        # Not a simple bivector under the simple dispatch — fail closed, never
        # silently return identity (that zeros motion without a signal).
        raise ValueError(
            "rotor_power: non-simple bivector under simple dispatch "
            f"(B² higher-grade residual {higher_norm:.3e})"
        )

    # Near-identity: nothing to scale.
    bivector_norm = float(np.linalg.norm(B))
    if bivector_norm < _NEAR_ZERO_TOL:
        return _identity(dtype)

    if bsq_scalar < 0.0:
        # Rotation plane. B² = -|B|² under signature, so the effective
        # magnitude is the Euclidean norm of the bivector coefficients.
        b_mag = float(np.sqrt(-bsq_scalar))
        theta_half = float(np.arctan2(b_mag, a))
        new_a = float(np.cos(alpha * theta_half))
        new_b_mag = float(np.sin(alpha * theta_half))
    elif bsq_scalar > 0.0:
        # Boost plane. Domain of atanh requires |b_mag/a| < 1 and a > 0.
        b_mag = float(np.sqrt(bsq_scalar))
        if a <= 0.0 or abs(b_mag / a) >= 1.0 - 1e-12:
            raise ValueError(
                f"rotor_power: boost plane outside unit-rotor domain "
                f"(a={a:.6g}, |B|/a={abs(b_mag / a) if a != 0.0 else float('inf'):.6g})"
            )
        eta_half = float(np.arctanh(b_mag / a))
        new_a = float(np.cosh(alpha * eta_half))
        new_b_mag = float(np.sinh(alpha * eta_half))
    else:
        # B² = 0: null bivector (translator generators in CGA). Exact binomial:
        # (a + B)^α = a^α + α a^{α-1} B  (higher powers of B vanish).
        # Unit translators have a = 1 ⇒ T^α = 1 + α B = translator(α·a_eucl).
        # Historically this returned identity — a silent zeroing of the Cartan
        # translation leg in dual_correction_slerp (fidelity #16 follow-up).
        if abs(a) < _NEAR_ZERO_TOL:
            return _identity(dtype)
        result = np.zeros(N_COMPONENTS, dtype=np.float64)
        result[0] = float(a) ** float(alpha) if a > 0.0 else float(np.sign(a) * (abs(a) ** float(alpha)))
        # Prefer real power for a>0; for a<0 (rare for unit translators) use |a|^α · sgn.
        scale_B = float(alpha) * (float(a) ** (float(alpha) - 1.0)) if a > 0.0 else float(alpha) * (abs(a) ** (float(alpha) - 1.0)) * float(np.sign(a))
        result = result + scale_B * B
        return result.astype(dtype, copy=False)

    result = np.zeros(N_COMPONENTS, dtype=np.float64)
    result[0] = new_a
    if b_mag > _NEAR_ZERO_TOL:
        result += (new_b_mag / b_mag) * B
    return result.astype(dtype, copy=False)


def _isoclinic_power_coeffs(x: float, alpha: float) -> tuple[float, float, float]:
    """Power coefficients ``(A, f, c)`` for one of two identical (isoclinic) simple
    factors with ``c² = x``: ``R_i^α = A + f · G_i``. Handles rotation, boost, and
    the null limit uniformly.
    """
    gsq = x - 1.0
    c = float(np.sqrt(max(x, 0.0)))
    if gsq < -1e-15:                        # rotation: c = cos(theta)
        theta = float(np.arccos(min(1.0, max(-1.0, c))))
        slin = float(np.sin(theta))
        A = float(np.cos(alpha * theta))
        f = float(np.sin(alpha * theta) / slin) if slin > 1e-300 else float(alpha)
    elif gsq > 1e-15:                       # boost: c = cosh(eta)
        eta = float(np.arccosh(max(1.0, c)))
        slin = float(np.sinh(eta))
        A = float(np.cosh(alpha * eta))
        f = float(np.sinh(alpha * eta) / slin) if slin > 1e-300 else float(alpha)
    else:                                   # null / parabolic limit
        A, f = 1.0, float(alpha)
    return A, f, c


def _split_commuting_simple(
    P: float, H: np.ndarray, W: np.ndarray, h0: float, disc: float
) -> tuple[np.ndarray, np.ndarray]:
    """Invariant decomposition of a non-simple rotor into two commuting SIMPLE
    unit rotors ``R = R1 R2`` (distinct-eigenvalue branch).

    With ``P = <R>_0``, ``H = <R>_2``, ``W = <R>_4``: the squared scalars of the
    two simple factors are ``x_i = c_i²`` — the roots of ``t² − (2P²−h0) t + P²``
    — and each simple bivector ``G_i`` is recovered by the linear system in
    ``{H, HW}``. Returns ``(R1, R2)`` as 32-component rotors.
    """
    b = 2.0 * P * P - h0
    sq = float(np.sqrt(disc))
    x1 = 0.5 * (b + sq)
    x2 = 0.5 * (b - sq)
    c1 = float(np.sqrt(max(x1, 0.0)))
    c2 = float(np.sqrt(max(x2, 0.0)))
    if P < 0.0:
        c2 = -c2                            # fix product sign so c1·c2 == <R>_0
    g1sq = x1 - 1.0
    g2sq = x2 - 1.0
    HW = grade_project(geometric_product(H, W), 2).astype(np.float64)
    det = c2 * c2 * g1sq - c1 * c1 * g2sq
    if abs(det) < _NEAR_ZERO_TOL:
        raise ValueError(
            "rotor_power: singular invariant split (unexpected for distinct eigenvalues)"
        )
    G1 = (c2 * g1sq * H - c1 * HW) / det
    G2 = (c2 * HW - c1 * g2sq * H) / det
    R1 = G1.copy()
    R1[0] = c1
    R2 = G2.copy()
    R2[0] = c2
    return R1, R2


def _general_rotor_power(R_arr: np.ndarray, alpha: float, dtype: np.dtype) -> np.ndarray:
    """R^alpha for a NON-simple rotor via the invariant (bivector) decomposition."""
    P = float(R_arr[0])
    H = grade_project(R_arr, 2).astype(np.float64)
    W = grade_project(R_arr, 4).astype(np.float64)
    h0 = float(scalar_part(geometric_product(H, H)))
    b = 2.0 * P * P - h0
    disc = b * b - 4.0 * P * P
    if disc <= _DEGEN_TOL:
        # Isoclinic: coincident invariant planes (x1 == x2 == b/2). The result
        # depends only on the symmetric functions H and W, so no per-plane split
        # is needed: R^α = A² + (A·f/c)·H + f²·W.
        A, f, c = _isoclinic_power_coeffs(0.5 * b, alpha)
        if c < _NEAR_ZERO_TOL:
            raise ValueError(
                "rotor_power: isoclinic rotor at theta~pi/2 has no principal power"
            )
        out = (A * f / c) * H + (f * f) * W
        out[0] += A * A
        return out.astype(dtype, copy=False)
    R1, R2 = _split_commuting_simple(P, H, W, h0, disc)
    out = geometric_product(
        _simple_rotor_power(R1, alpha, np.dtype(np.float64)),
        _simple_rotor_power(R2, alpha, np.dtype(np.float64)),
    )
    return out.astype(dtype, copy=False)


def word_transition_rotor(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Compute the closed transition operator from source versor A to target B.

        R = B * reverse(A)

    Vocabulary coordinates are expected to already be grade-normalized versors.
    The transition between two such states is their closed product. This path
    must never synthesize an unrelated fallback rotor from target components;
    invalid inputs fail loudly so generation can preserve its field invariant.
    """
    dtype = _result_dtype(A, B)
    source = np.asarray(A, dtype=dtype)
    target = np.asarray(B, dtype=dtype)
    if source.shape != (N_COMPONENTS,) or target.shape != (N_COMPONENTS,):
        raise ValueError(
            "word_transition_rotor expects two 32-component multivectors; "
            f"got {source.shape} and {target.shape}."
        )
    if float(np.linalg.norm(source)) < _NEAR_ZERO_TOL or float(np.linalg.norm(target)) < _NEAR_ZERO_TOL:
        raise ValueError("word_transition_rotor: near_zero input")
    if float(np.linalg.norm(target - source)) < _SAME_POINT_TOL:
        return _identity(dtype)

    candidate = geometric_product(target, reverse(source)).astype(dtype)
    rotor = _strict_unitize_versor(candidate, dtype)
    condition = versor_condition(rotor)
    if condition > _TRANSITION_CONDITION_TOL:
        raise ValueError(
            "word_transition_rotor: transition rotor is not a unit versor; "
            f"condition={condition:.3e}"
        )
    return rotor.astype(dtype, copy=False)
