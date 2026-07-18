"""core.physics.quantity_kernel — conformal quantity encoding (ADR-0249 P1).

Substrate-native representation of real quantities as null points on the
Cl(4,1) conformal line, with affine transport (add/scale by known constants)
realized as versor sandwiches. This is the standing hand the reader→Hamiltonian
compiler builds on: numbers live on the field before arithmetic relations can
become field constraints.

Encoding (spike §3, verified against algebra/cl41.py):
    n_inf = e4 + e5,  n_o = ½(e5 − e4)          (null basis of the line)
    P(q)  = n_o + q·e1 + ½q²·n_inf              (null point at coordinate q)

Transport (exact, versor-native):
    translate by a:  T_a = 1 − ½ a·e1·n_inf,    T_a P(b) T̃_a = P(a+b)
    scale by e^{−α}: D_α = exp(+½ α·e4e5),      D_α P(b) D̃_α = w·P(e^{−α}·b)

Dilation carries a conformal weight w ≠ 1, so transported targets are decoded
*projectively* — q = e1-coeff / (e5-coeff − e4-coeff) — which is scale-invariant.
The corridor requires unit-norm states, so relation compilation (P2) normalizes
before building the well; projective decode makes that lossless.

Reproducibility (spike §4.6, Tier 2): every construction is explicit float64.
`algebra.cl41.geometric_product` silently truncates to float32 unless handed
f64 arrays; this module never lets that happen. Serve-quarantined (A-04):
`core/physics/` is never imported by `chat/runtime.py`.
"""
from __future__ import annotations

import math

import numpy as np

from algebra import cl41 as cl

__all__ = [
    "QuantityKernelError",
    "embed_quantity",
    "translate_quantity",
    "dilate_quantity",
    "decode_quantity",
]

# Grade-1 component indices (e1..e5 occupy indices 1..5 in the blade ordering).
_E1, _E4, _E5 = 1, 4, 5

# Minimum |conformal weight| below which projective decode is undefined.
_MIN_WEIGHT = 1e-9


class QuantityKernelError(ValueError):
    """Typed, fail-closed refusal for the quantity kernel (no guessed values)."""


def _e(i: int) -> np.ndarray:
    """i-th basis vector (0-indexed e1..e5) as an f64 multivector."""
    return cl.basis_vector(i).astype(np.float64)


# Null basis of the conformal line, built once in f64.
_N_INF = _e(3) + _e(4)  # e4 + e5
_N_O = 0.5 * (_e(4) - _e(3))  # ½(e5 − e4)
_E1_NINF = cl.geometric_product(_e(0), _N_INF)  # e1·n_inf, for the translator
_E4E5 = cl.geometric_product(_e(3), _e(4))  # e4e5, generator of the dilator


def _f64(value: float, *, what: str) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise QuantityKernelError(f"{what}_not_finite")
    return v


def _sandwich(versor: np.ndarray, point: np.ndarray) -> np.ndarray:
    """versor · point · reverse(versor), all in f64."""
    v = np.asarray(versor, dtype=np.float64)
    p = np.asarray(point, dtype=np.float64)
    return cl.geometric_product(cl.geometric_product(v, p), cl.reverse(v))


def embed_quantity(q: float) -> np.ndarray:
    """Null point P(q) = n_o + q·e1 + ½q²·n_inf as an f64 (32,) multivector."""
    qf = _f64(q, what="quantity")
    return (_N_O + qf * _e(0) + 0.5 * qf * qf * _N_INF).astype(np.float64)


def translate_quantity(point: np.ndarray, shift: float) -> np.ndarray:
    """Add a known constant: T_a P(b) T̃_a = P(a+b), exact and weight-preserving."""
    a = _f64(shift, what="shift")
    translator = np.zeros(cl.N_COMPONENTS, dtype=np.float64)
    translator[0] = 1.0
    translator = translator - 0.5 * a * _E1_NINF
    return _sandwich(translator, point).astype(np.float64)


def dilate_quantity(point: np.ndarray, alpha: float) -> np.ndarray:
    """Scale by e^{−α}: D_α = exp(+½α·e4e5). Carries a conformal weight (decode projectively)."""
    a = _f64(alpha, what="alpha")
    half = 0.5 * a
    dilator = np.zeros(cl.N_COMPONENTS, dtype=np.float64)
    dilator[0] = math.cosh(half)
    dilator = dilator + math.sinh(half) * _E4E5
    return _sandwich(dilator, point).astype(np.float64)


def decode_quantity(point: np.ndarray) -> float:
    """Projective (scale-invariant) recovery of q from a null point.

    q = e1-coeff / (e5-coeff − e4-coeff). Refuses when the conformal weight is
    degenerate — an unweighted direction has no finite line coordinate.
    """
    arr = np.asarray(point, dtype=np.float64)
    if arr.shape != (cl.N_COMPONENTS,):
        raise QuantityKernelError("point_bad_shape")
    if not np.all(np.isfinite(arr)):
        raise QuantityKernelError("point_not_finite")
    weight = float(arr[_E5]) - float(arr[_E4])
    if abs(weight) < _MIN_WEIGHT:
        raise QuantityKernelError("degenerate_conformal_weight")
    return float(arr[_E1]) / weight
