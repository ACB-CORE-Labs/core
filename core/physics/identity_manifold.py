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

# Grade-1 basis-vector slots in the 32-component Cl(4,1) layout. The spatial block
# is e1/e2/e3 (indices 1/2/3) — the default value-axis support; e4/e5 (indices 4/5)
# are the extra grade-1 directions a versor tilts (e4, null/conformal) or boosts
# (e5) a value axis toward. Pinned against ``algebra.cl41.basis_vector`` in tests
# (ADR-0246 §3.6 fixed blade map).
SPATIAL_GRADE1_INDICES: tuple[int, int, int] = (1, 2, 3)
E4_GRADE1_INDEX: int = 4
E5_GRADE1_INDEX: int = 5


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


class MalformedVersorError(ValueError):
    """Raised when a versor handed to an ADR-0246 primitive is not a well-formed
    ``N_COMPONENTS``-vector of finite floats.

    Fail-closed at the primitive boundary (ADR-0246 §6.1 "Malformed F → typed
    error"): a NaN/inf or wrong-shape field must raise, never propagate a silent
    NaN into an induced action or a residual-channel split.
    """


def _validate_versor(versor: np.ndarray) -> np.ndarray:
    """Coerce to a finite float64 ``(N_COMPONENTS,)`` array or fail closed."""
    array = np.asarray(versor, dtype=np.float64)
    if array.shape != (N_COMPONENTS,):
        raise MalformedVersorError(
            f"versor must have shape ({N_COMPONENTS},), got {array.shape}"
        )
    if not np.all(np.isfinite(array)):
        raise MalformedVersorError("versor has non-finite (NaN/inf) components")
    return array


def orthogonality_defect_of_action(action: np.ndarray, gram: np.ndarray) -> float:
    """``‖AᵀGA − G‖_F`` for a precomputed induced action ``A`` (ADR-0246 §3.2).

    Zero iff ``A`` is a ``G``-isometry of the value subspace. The single home for
    the d_orth definition, shared by :meth:`IdentityManifoldGeometry.orthogonality_defect`
    and the off-serving diagnostics.
    """
    action = np.asarray(action, dtype=np.float64)
    gram = np.asarray(gram, dtype=np.float64)
    return float(np.linalg.norm(action.T @ gram @ action - gram, ord="fro"))


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

        Returns ``(leakage, self_align)`` — parallel lists over the value axes,
        both **scale-invariant** (normalized by the rotated axis magnitude):

          * ``leakage[i]`` = ``‖R aᵢ R̃ − P_I(R aᵢ R̃)‖₂ / ‖R aᵢ R̃‖₂`` — the
            *fraction* of the rotated axis outside the value subspace, in
            ``[0, 1]``; catches tilt toward alien dimensions e4/e5.
          * ``self_align[i]`` = ``⟨aᵢ, R aᵢ R̃⟩₀ / (‖aᵢ‖₂ ‖R aᵢ R̃‖₂)`` — a signed
            cosine in ``[−1, 1]``; catches in-subspace inversion (``e1 → −e1``
            gives leakage 0 but −1 here).

        Normalization is load-bearing: a versor with a boost (e5) component does
        NOT preserve the Euclidean coefficient norm (``‖R aᵢ R̃‖₂`` can exceed 1
        even though ``R R̃ = 1`` in the Minkowski sense), so an un-normalized
        magnitude would be unbounded. For a norm-preserving spatial rotor the
        rotated axis is unit and normalization is a no-op.
        """
        versor = np.asarray(versor, dtype=np.float64)
        leakage: list[float] = []
        self_align: list[float] = []
        for axis in self.axes_psi:
            axis_norm = euclidean_norm(axis)
            rotated = sandwich(versor, axis)
            rot_norm = euclidean_norm(rotated)
            if rot_norm <= 0.0 or axis_norm <= 0.0:
                # Degenerate: the versor annihilated the axis — treat as full
                # leakage / zero alignment (fail-closed).
                leakage.append(1.0)
                self_align.append(0.0)
                continue
            rejection = rotated - subspace_project(
                rotated, self.axes_psi, self.gram_inv
            )
            leakage.append(euclidean_norm(rejection) / rot_norm)
            self_align.append(_inner0(axis, rotated) / (axis_norm * rot_norm))
        return leakage, self_align

    def leakage_rms(self, versor: np.ndarray) -> float:
        """Root-mean-square per-axis subspace-leakage fraction over all axes.

        Each per-axis leakage is a fraction in ``[0, 1]`` (see
        :meth:`axis_response`), so this aggregate is also in ``[0, 1]``; the
        Phase-2 gate's ``score`` is ``1 − leakage_rms``.
        """
        leakage, _ = self.axis_response(versor)
        return float((sum(value * value for value in leakage) / len(leakage)) ** 0.5)

    # -- ADR-0246 §3 induced-action primitives (pure, off-serving) --------------

    def induced_action(self, versor: np.ndarray) -> np.ndarray:
        """The induced action matrix ``A(F)`` of a versor on the value frame.

        ``A_kj = (G⁻¹)_{km} ⟨a_m, F a_j F̃⟩₀`` (ADR-0246 §3.1). Column ``j`` is the
        image of axis ``j`` (``F a_j F̃``) re-expressed in the axis basis. This
        captures ALL in-subspace action — including the permutations and rotations
        that per-axis leakage is blind to (a rotor rotating e1→e2 has zero leakage
        but a non-identity ``A``). It is RAW (unnormalized): a boost that stretches
        an axis shows up as a column norm > 1 and hence in :meth:`orthogonality_defect`,
        deliberately not hidden by normalization.

        When ``F`` preserves the subspace isometrically, ``A`` is ``G``-orthogonal
        (``AᵀGA = G``). Built only from existing primitives (Gram, signed inner
        product, sandwich); no new algebra.

        Raises :class:`MalformedVersorError` on a non-finite or wrong-shape versor
        (ADR-0246 §6.1 fail-closed on malformed F).
        """
        versor = _validate_versor(versor)
        n = len(self.axes_psi)
        overlaps = np.empty((n, n), dtype=np.float64)
        for j, axis_j in enumerate(self.axes_psi):
            image = sandwich(versor, axis_j)
            for k, axis_k in enumerate(self.axes_psi):
                overlaps[k, j] = _inner0(axis_k, image)
        return self.gram_inv @ overlaps

    def orthogonality_defect(self, versor: np.ndarray) -> float:
        """``d_orth(F) = ‖A(F)ᵀ G A(F) − G‖_F`` (ADR-0246 §3.2).

        Zero iff the induced action is a ``G``-isometry of the value subspace.
        Non-zero flags numerical failure or genuinely non-isometric action (a
        boost stretches the frame). It detects a DIFFERENT failure than
        :func:`~core.physics.identity_action.stabilizer_defect` and must never be
        read as a semantic authorization policy — it is a conditioning / isometry
        check only.
        """
        return orthogonality_defect_of_action(self.induced_action(versor), self.gram)

    def typed_residual_energy(self, versor: np.ndarray) -> dict[str, float]:
        """Typed decomposition of the out-of-subspace leakage (ADR-0246 §3.6).

        For each axis the rejection ``r = F a F̃ − P_I(F a F̃)`` is split by which
        grade-1 direction it leaks into, summed over axes, and returned as
        fractions of the total rotated-axis energy:

          * ``null_or_conformal`` — energy on e4 (index 4): conformal/null tilt.
          * ``boost_like``        — energy on e5 (index 5): noncompact/boost class.
          * ``spatial_foreign``   — energy on spatial grade-1 slots (e1/e2/e3) not
            in the value-axis span; structurally 0 for the default full-span pack.
          * ``unclassified``      — the remainder (higher-grade contamination after
            the sandwich, numerical junk). Fail-closed: no correction policy ever
            attaches to this channel. For a clean versor (grade-preserving sandwich)
            it is ~0.

        Retains the positive-definite Euclidean coefficient norm (never the
        indefinite ``⟨·,·⟩₀``) so a boost/e5 component cannot silently vanish.

        Raises :class:`MalformedVersorError` on a non-finite or wrong-shape versor
        (ADR-0246 §6.1 fail-closed on malformed F).
        """
        versor = _validate_versor(versor)
        e4_energy = e5_energy = spatial_foreign = unclassified = total = 0.0
        for axis in self.axes_psi:
            rotated = sandwich(versor, axis)
            rejection = rotated - self.project(rotated)
            total += euclidean_norm(rotated) ** 2
            e4_energy += float(rejection[E4_GRADE1_INDEX] ** 2)
            e5_energy += float(rejection[E5_GRADE1_INDEX] ** 2)
            spatial_foreign += float(
                sum(rejection[i] ** 2 for i in SPATIAL_GRADE1_INDICES)
            )
            rejection_energy = euclidean_norm(rejection) ** 2
            unclassified += max(
                0.0,
                rejection_energy
                - float(rejection[E4_GRADE1_INDEX] ** 2)
                - float(rejection[E5_GRADE1_INDEX] ** 2)
                - float(sum(rejection[i] ** 2 for i in SPATIAL_GRADE1_INDICES)),
            )
        if total <= 0.0:
            # Versor annihilated every axis — fail-closed as fully unaccounted.
            return {
                "null_or_conformal": 0.0,
                "boost_like": 0.0,
                "spatial_foreign": 0.0,
                "unclassified": 1.0,
            }
        return {
            "null_or_conformal": e4_energy / total,
            "boost_like": e5_energy / total,
            "spatial_foreign": spatial_foreign / total,
            "unclassified": unclassified / total,
        }
