"""ADR-0249 P1 — conformal quantity kernel pins.

Verifies the substrate-native encoding of quantities as null points on the
Cl(4,1) conformal line, and affine transport by translator/dilator versors.
Every claim here was first checked numerically against algebra/cl41.py's own
multiplication table in the design spike
(docs/research/reader-hamiltonian-compiler-spike-2026-07-18.md §3); these are
the pinned, permanent form.

Reproducibility discipline (spike §4.6):
- Tier 2 (matrix/versor construction) MUST be f64 and hardware-deterministic;
  the golden-bytes test is the cross-hardware canary.
"""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from algebra import cl41 as cl
from core.physics.quantity_kernel import (
    QuantityKernelError,
    decode_quantity,
    dilate_quantity,
    embed_quantity,
    translate_quantity,
)


def _null_defect(psi: np.ndarray) -> float:
    return abs(cl.scalar_part(cl.geometric_product(psi, psi)))


# --- Embedding: P(q) is a null point, in f64 ------------------------------


@pytest.mark.parametrize("q", [-50.0, -3.0, 0.0, 1.0, 7.5, 42.0])
def test_embedding_is_null(q: float) -> None:
    assert _null_defect(embed_quantity(q)) < 1e-9


def test_embedding_is_float64() -> None:
    # Guards the cl41 silent-f32 fallback (spike §4.6 Tier 2 trap).
    assert embed_quantity(3.0).dtype == np.dtype(np.float64)


def test_embedding_shape() -> None:
    assert embed_quantity(3.0).shape == (cl.N_COMPONENTS,)


# --- Translator: exact, weight-preserving (algebraic identity) ------------


@pytest.mark.parametrize(("a", "b"), [(3.0, 4.0), (-2.0, 9.0), (0.5, 0.5), (10.0, -10.0)])
def test_translate_is_exact_addition(a: float, b: float) -> None:
    got = translate_quantity(embed_quantity(b), a)
    want = embed_quantity(a + b)
    # Integer/half-integer coefficients ⇒ f64 rounding only.
    assert np.max(np.abs(got - want)) < 1e-9


def test_translate_stays_null() -> None:
    assert _null_defect(translate_quantity(embed_quantity(4.0), 3.0)) < 1e-9


def test_translate_output_is_float64() -> None:
    assert translate_quantity(embed_quantity(4.0), 3.0).dtype == np.dtype(np.float64)


# --- Dilator: scales by e^{-alpha} (SIGN PINNED, spike §3), weight != 1 ----


@pytest.mark.parametrize(("alpha", "b"), [(0.7, 3.0), (-1.1, 5.0), (2.0, -4.0)])
def test_dilate_scales_by_exp_minus_alpha(alpha: float, b: float) -> None:
    q_dec = decode_quantity(dilate_quantity(embed_quantity(b), alpha))
    assert abs(q_dec - np.exp(-alpha) * b) < 1e-6


def test_dilate_carries_conformal_weight() -> None:
    # Weight must genuinely differ from 1 → normalize-then-projective-decode is required.
    x = dilate_quantity(embed_quantity(3.0), 0.7)
    weight = float(x[5]) - float(x[4])
    assert abs(weight - 1.0) > 1e-3


# --- Decode: projective, scale-invariant, round-trips ---------------------


@pytest.mark.parametrize("q", [-50.0, -3.0, 0.0, 1.0, 7.5, 42.0])
def test_decode_round_trips_embedding(q: float) -> None:
    assert abs(decode_quantity(embed_quantity(q)) - q) < 1e-9


@pytest.mark.parametrize("scale", [0.1, 1.0, 3.3, 10.0])
def test_decode_is_scale_invariant(scale: float) -> None:
    psi = embed_quantity(7.5)
    assert abs(decode_quantity(scale * psi) - decode_quantity(psi)) < 1e-9


def test_affine_chain_composes(a_mul: float = 3.0, add: float = 5.0, y: float = 4.0) -> None:
    # "x = a*y + b" as versor transport. Dilation scales by e^{-alpha} (spike §3),
    # so multiplying by a_mul needs alpha = -ln(a_mul), then translate by b.
    psi = translate_quantity(dilate_quantity(embed_quantity(y), -np.log(a_mul)), add)
    assert abs(decode_quantity(psi) - (a_mul * y + add)) < 1e-6


# --- Fail-closed on non-finite input --------------------------------------


@pytest.mark.parametrize("bad", [np.inf, -np.inf, np.nan])
def test_embedding_refuses_non_finite(bad: float) -> None:
    with pytest.raises(QuantityKernelError):
        embed_quantity(bad)


def test_translate_refuses_non_finite_shift() -> None:
    with pytest.raises(QuantityKernelError):
        translate_quantity(embed_quantity(1.0), np.nan)


def test_decode_refuses_degenerate_weight() -> None:
    # A point with zero conformal weight cannot be projectively decoded.
    psi = np.zeros(cl.N_COMPONENTS, dtype=np.float64)
    psi[1] = 1.0  # e1 only: weight (e5c - e4c) = 0
    with pytest.raises(QuantityKernelError):
        decode_quantity(psi)


# --- Tier-2 cross-hardware reproducibility canary (golden bytes) ----------

# SHA-256 of embed_quantity(3.0).astype("<f8").tobytes(). Frozen from the first
# green run; a change means the substrate math or dtype drifted (spike §4.6).
_GOLDEN_EMBED_3 = "be50e6f65ebe0e528055912aaaa3ddc2af3eb363e00cdccc711aa26c32548719"


def test_embedding_golden_bytes_are_stable() -> None:
    digest = hashlib.sha256(embed_quantity(3.0).astype("<f8").tobytes()).hexdigest()
    assert digest == _GOLDEN_EMBED_3, f"substrate drift: got {digest}"
