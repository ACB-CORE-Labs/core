"""Third-Door blueprint-fidelity ledger.

The ADR-0239 geometry suite (``test_adr_0239_dynamic_manifold.py``) only ever
exercises the *identity + single-plane rotor* regime — the one input class where
``rotor_power`` does not hit its non-simple-bivector identity fallback, and where
several assertions are tautologies (``residual >= 0``, ``reconstruction_residual
>= 0``). This file exercises the operators on realistic *composed* conformal
versors (products of rotations on distinct planes — what a real field state
looks like) and encodes the properties the Super-Blueprint / R&D-Revised
blueprints actually REQUIRE.

The blueprints are the rigorous artifact; the landed code substitutes heuristics.
So the spec-property tests here are marked ``xfail(strict=True)`` with reasons
citing the blueprint section + audit finding. When an operator is implemented to
spec, its xfail flips to xpass (strict) and CI forces the marker's removal.

Empirical findings (2026-07-11 audit, reproduced deterministically below):
  #1  [RESOLVED by #23] supervised_blend was a no-op for interior alpha on
      composed versors (rotor_power returned identity for the non-simple
      transition rotor). Exact fractional powers now implemented.
  #2  cartan_iwasawa_factorize raises "factor R not closed" on composed
      conformal versors (~45% of the time), instead of the "mathematically
      exact, guaranteed" decomposition the Super-Blueprint §2.2 specifies.

See PR description and the fidelity table for the full spec-vs-impl ledger.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import geometric_product
from algebra.rotor import make_rotor_from_angle
from core.physics.dynamic_manifold import cartan_iwasawa_factorize
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

def test_cartan_iwasawa_currently_raises_on_composed_versor():
    """CHARACTERIZATION of finding #2 — locks the current (defective) behaviour.

    Deterministic composed versor that the heuristic factorizer cannot close.
    PASSES today (asserts the raise). Delete when the spec algorithm lands.
    """
    v = _composed_versor((6, 7, 8), seed=0.0)
    with pytest.raises(ValueError, match="not closed"):
        cartan_iwasawa_factorize(v)


@pytest.mark.xfail(
    reason=(
        "Finding #2 / Super-Blueprint §2.2: cartan_iwasawa_factorize is specified as a "
        "'mathematically exact, non-iterative' decomposition that 'guarantees perfect "
        "decomposition' via the action of V on n_o / n_inf. The landed grade-projection "
        "heuristic instead raises 'factor R not closed' on composed conformal versors "
        "(~45% at 3-4 planes). Spec: factorization must succeed and R*T*D must "
        "reconstruct V to < 1e-6."
    ),
    strict=True,
)
def test_cartan_iwasawa_should_reconstruct_composed_motion():
    v = _composed_versor((6, 7, 8), seed=0.0)
    fac = cartan_iwasawa_factorize(v)  # spec: must not raise
    recon = geometric_product(geometric_product(fac.R, fac.T), fac.D)
    assert float(np.linalg.norm(recon - v)) < 1e-6
