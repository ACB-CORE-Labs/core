"""core.physics.identity_manifold — metric-exact operator-preservation identity geometry.

ADR-0244 §2.1 / §4a (operator-preservation reframe, governance annotation item 12).

The identity manifold is a fixed geometric subspace ``I = span(axis_1, …, axis_n)``
of the Cl(4,1) state space, encoding CORE's value axes. The live identity
trajectory is ``final_state.F``, whose class invariant is
``versor_condition(F) < 1e-6`` — i.e. **F is a versor: an even-grade operator
(grades 0,2,4) with zero grade-1 content.** Projecting such an operator onto the
grade-1 value subspace is vacuous (``P_I(F) = 0`` identically). The geometrically
correct question for an *operator* against a *subspace* is whether the operator
**preserves** the subspace — evaluated by its action on the axes via the sandwich
product ``F aᵢ F̃``:

  * **subspace leakage** ``‖F aᵢ F̃ − P_I(F aᵢ F̃)‖₂`` — the out-of-subspace
    component of each rotated axis; catches a versor tilting a value axis toward
    an alien dimension (e4/e5). The magnitude is the positive-definite Euclidean
    coefficient norm — NOT the indefinite Cl(4,1) inner product ``⟨S, S̃⟩₀``,
    which signature (+,+,+,+,−) permits to vanish (or go negative for an e5/boost
    component) for nonzero leakage, silently hiding a breach.
  * **signed self-alignment** ``⟨aᵢ, F aᵢ F̃⟩₀`` — the signed overlap of an axis
    with its own rotated image; catches an in-subspace *inversion*
    (``e1 → −e1``: leakage 0 but self-alignment −1). Never ``abs()``'d, so
    anti-alignment (opposition) stays distinguishable from orthogonality.

Both measures are required and non-redundant.

Value axes are lifted from the pack's R³ ``direction`` to grade-1 Cl(4,1)
multivectors at the e1/e2/e3 slots (``algebra.cl41.basis_vector(0..2)``), so
``I`` lives in the spatial grade-1 block where ``⟨·,·⟩₀`` coincides with the
Euclidean inner product and the Gram matrix is positive-definite.

This module is pure (depends only on ``algebra.cl41``), deterministic, and
float64 throughout — the offline precision domain. The f64→f32 serving cast
(ADR-0244 §2.5 / ADR-0245 §2.2) applies only to the live per-turn versor at the
Phase-2 gate boundary, not to this axis construction. Off-serve until ADR-0244
D4 Phase 2 wires it into ``core.physics.identity``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from algebra.cl41 import (
    N_COMPONENTS,
    basis_vector,
    geometric_product,
    reverse,
    scalar_part,
)

# Gram condition-number ceiling above which axis modes are too near-degenerate
# to resolve without mode-aliasing (ADR-0244 §2.1).
CONDITION_BOUND: float = 1e5


class ManifoldConditioningError(ValueError):
    """Raised when the value-axis Gram matrix is too ill-conditioned.

    A condition number above :data:`CONDITION_BOUND` means two or more value
    axes are near-degenerate (nearly parallel), so the metric-exact projection
    onto their span cannot be resolved without mode-aliasing. Fail closed rather
    than return an unreliable projection.
    """


def _inner0(a: np.ndarray, b: np.ndarray) -> float:
    """The Cl(4,1) metric inner product ⟨a, b⟩₀ = scalar_part(a · reverse(b)).

    Symmetric in ``a`` and ``b``. Indefinite in general (signature (+,+,+,+,−)),
    but positive-definite when restricted to the spatial grade-1 block the value
    axes occupy.
    """
    return scalar_part(geometric_product(a, reverse(b)))


def lift_axis(direction: Sequence[float]) -> np.ndarray:
    """Lift a value-axis ``direction`` (R³) to a grade-1 Cl(4,1) multivector.

    Places the three components at the e1/e2/e3 grade-1 slots via
    :func:`algebra.cl41.basis_vector`. NOT :func:`algebra.cga.embed_point`,
    which maps to null-cone points and would make the Gram matrix a distance
    table rather than a metric inner product. Returns a float64 (32,) array.
    """
    direction = tuple(float(x) for x in direction)
    if len(direction) != 3:
        raise ValueError(
            f"value-axis direction must have length 3, got {len(direction)}"
        )
    psi = np.zeros(N_COMPONENTS, dtype=np.float64)
    for k, component in enumerate(direction):
        psi = psi + component * basis_vector(k).astype(np.float64)
    return psi


def gram_matrix(axes_psi: Sequence[np.ndarray]) -> np.ndarray:
    """Symmetric metric-restricted Gram matrix ``G_ij = ⟨axis_i, axis_j⟩₀``.

    Raises :class:`ManifoldConditioningError` when ``cond(G) > CONDITION_BOUND``.
    """
    n = len(axes_psi)
    if n == 0:
        raise ValueError("identity manifold requires at least one value axis")
    G = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            G[i, j] = _inner0(axes_psi[i], axes_psi[j])
    condition = float(np.linalg.cond(G))
    if condition > CONDITION_BOUND:
        raise ManifoldConditioningError(
            f"value-axis Gram condition number {condition:.3e} exceeds "
            f"{CONDITION_BOUND:.0e}: axes are near-degenerate"
        )
    return G


def subspace_project(
    x: np.ndarray, axes_psi: Sequence[np.ndarray], gram_inv: np.ndarray
) -> np.ndarray:
    """Metric-orthogonal projection of ``x`` onto ``I = span(axes_psi)``.

    ``P_I(x) = Σ_ij axis_i · (G⁻¹)_ij · ⟨axis_j, x⟩₀``. The overlap coefficients
    are SIGNED (never ``abs()``'d) so orientation is preserved.
    """
    coeffs_raw = np.array(
        [_inner0(a, x) for a in axes_psi], dtype=np.float64
    )
    coeffs = gram_inv @ coeffs_raw
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    for weight, axis in zip(coeffs, axes_psi):
        out = out + weight * axis
    return out


def sandwich(versor: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Versor action ``R x R̃``. For a versor ``R`` this preserves grade and
    norm, so a grade-1 axis maps to a grade-1 vector of the same magnitude."""
    return geometric_product(geometric_product(versor, x), reverse(versor))


def euclidean_norm(s: np.ndarray) -> float:
    """Positive-definite coefficient-Euclidean norm ``‖s‖₂``.

    Used for the leakage *magnitude* — deliberately NOT the indefinite Cl(4,1)
    norm ``⟨s, s̃⟩₀``, which can vanish or go negative for a nonzero leakage
    (e.g. an e5/boost component), silently hiding a breach.
    """
    return float(np.linalg.norm(np.asarray(s, dtype=np.float64), ord=2))


@dataclass(frozen=True)
class IdentityManifoldGeometry:
    """Frozen operator-preservation geometry for a set of value axes.

    Constructed once at manifold/pack load and never mutated within a session
    (ADR-0244 governance annotation item 8 — the identity subspace is inalienable
    by construction). ``axes_psi`` are the grade-1 lifts; ``gram`` / ``gram_inv``
    the metric-restricted Gram matrix and its inverse.
    """

    axes_psi: tuple[np.ndarray, ...]
    gram: np.ndarray
    gram_inv: np.ndarray

    @classmethod
    def from_directions(
        cls, directions: Sequence[Sequence[float]]
    ) -> "IdentityManifoldGeometry":
        """Build the geometry from pack value-axis directions (R³ each).

        Raises :class:`ManifoldConditioningError` if the axes are near-degenerate.
        """
        axes = tuple(lift_axis(d) for d in directions)
        gram = gram_matrix(axes)
        gram_inv = np.linalg.inv(gram)
        return cls(axes_psi=axes, gram=gram, gram_inv=gram_inv)

    def project(self, x: np.ndarray) -> np.ndarray:
        """Metric-orthogonal projection of ``x`` onto the value subspace."""
        return subspace_project(x, self.axes_psi, self.gram_inv)

    def axis_response(
        self, versor: np.ndarray
    ) -> tuple[list[float], list[float]]:
        """Per-axis operator-preservation measures for ``versor``.

        Returns ``(leakage, self_align)`` — parallel lists over the value axes:

          * ``leakage[i]`` = ``‖R aᵢ R̃ − P_I(R aᵢ R̃)‖₂`` (subspace departure;
            catches tilt toward alien dimensions e4/e5).
          * ``self_align[i]`` = ``⟨aᵢ, R aᵢ R̃⟩₀`` (signed orientation; catches
            in-subspace inversion — ``e1 → −e1`` gives leakage 0 but −1 here).
        """
        versor = np.asarray(versor, dtype=np.float64)
        leakage: list[float] = []
        self_align: list[float] = []
        for axis in self.axes_psi:
            rotated = sandwich(versor, axis)
            rejection = rotated - subspace_project(
                rotated, self.axes_psi, self.gram_inv
            )
            leakage.append(euclidean_norm(rejection))
            self_align.append(_inner0(axis, rotated))
        return leakage, self_align

    def leakage_rms(self, versor: np.ndarray) -> float:
        """Root-mean-square subspace leakage over all axes.

        Each rotated axis is unit-norm (a versor preserves norm), so this is the
        aggregate subspace-departure fraction in ``[0, 1]``; the Phase-2 gate's
        ``score`` is ``1 − leakage_rms``.
        """
        leakage, _ = self.axis_response(versor)
        return float((sum(value * value for value in leakage) / len(leakage)) ** 0.5)
