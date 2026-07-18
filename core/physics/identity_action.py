"""core.physics.identity_action — lawful identity action policy (ADR-0246 §3.2–§3.3).

Where :mod:`core.physics.identity_manifold` measures *what a versor does* to the
value frame (the induced action ``A(F)``, its orthogonality defect ``d_orth``, and
typed leakage), this module measures *whether that action is lawful* — how far the
induced action sits from the explicitly permitted identity actions ``H_id``.

The two diagnostics are deliberately never collapsed (ADR-0246 §3.2):

  * ``d_orth`` (in identity_manifold) — detects non-isometric / numerically
    corrupt action on the subspace. A conditioning check, NOT an authorization.
  * ``d_stab`` (here) — ``min_{H ∈ H_id} ‖A(F) − H‖_G`` — detects departure from
    the explicitly *permitted* identity action. This is the lawfulness measure.

**Locked stabilizer (ADR-0246 §3.3).** For the default identity pack

    H_id = { I }

the singleton containing only the identity matrix in the axis basis. Algebraic
cleanliness ≠ identity lawfulness, so ``-I`` (global inversion), axis
permutations, continuous rotations, and arbitrary reweightings are **excluded**.
Under a singleton stabilizer there is no continuous projection that "invents" a
lawful action: ``d_stab`` is a pass/fail distance, and callers must NOT soft-project
``A`` onto ``I`` and then compose the projection as if the turn were lawful.
Enlarging ``H_id`` is a future, explicit, reviewed pack/policy change — never an
implicit convenience here.

Pure (numpy + identity_manifold only), deterministic, float64, off-serving. The
lawful-only path composition and hard-break ledger (§3.4/§3.5) are a separate,
later unit; this module provides only the per-turn stabilizer defect.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.physics.identity_manifold import IdentityManifoldGeometry

# Below this the axis Gram is treated as the identity matrix and the G-weighted
# norm collapses to the plain Frobenius norm (exact for the default pack).
_IDENTITY_GRAM_TOL: float = 1e-9


@dataclass(frozen=True)
class IdentityStabilizer:
    """The permitted identity actions ``H_id`` in the axis basis.

    ``members`` are the allowed action matrices. The default (and only ratified)
    policy is the singleton ``{ I }`` — see module docstring / ADR-0246 §3.3.
    Constructing a non-singleton stabilizer is possible for research/analysis but
    is NOT a ratified live policy; enlarging ``H_id`` for serving requires an
    explicit reviewed change.
    """

    members: tuple[np.ndarray, ...]

    @classmethod
    def singleton(cls, dimension: int) -> "IdentityStabilizer":
        """The locked default ``H_id = { I_dimension }``."""
        return cls(members=(np.eye(int(dimension), dtype=np.float64),))

    @property
    def is_singleton_identity(self) -> bool:
        """True iff this is exactly the locked default ``{ I }``."""
        return len(self.members) == 1 and bool(
            np.allclose(self.members[0], np.eye(self.members[0].shape[0]))
        )


def _matrix_sqrt_spd(gram: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """``(G^{1/2}, G^{-1/2})`` for a symmetric positive-definite Gram via eigh."""
    eigvals, eigvecs = np.linalg.eigh(gram)
    if float(eigvals.min()) <= 0.0:
        raise ValueError("stabilizer defect requires a positive-definite Gram")
    root = eigvecs @ np.diag(np.sqrt(eigvals)) @ eigvecs.T
    inv_root = eigvecs @ np.diag(1.0 / np.sqrt(eigvals)) @ eigvecs.T
    return root, inv_root


def _g_weighted_frobenius(matrix: np.ndarray, gram: np.ndarray) -> float:
    """Metric-consistent matrix norm ``‖M‖_G`` (ADR-0246 §3.2).

    Measured in a ``G``-orthonormal frame: ``‖M‖_G = ‖G^{1/2} M G^{-1/2}‖_F``.
    Reduces exactly to the plain Frobenius norm when ``G = I`` (the default pack),
    and is invariant to the metric-preserving change of axis coordinates. The
    convention is fixed here for the value packs in use; a broader-pack review may
    revisit it (ADR-0246 §3.2 leaves general-pack ``‖·‖_G`` to ADR-0246 proper).
    """
    if np.allclose(gram, np.eye(gram.shape[0]), atol=_IDENTITY_GRAM_TOL):
        return float(np.linalg.norm(matrix, ord="fro"))
    root, inv_root = _matrix_sqrt_spd(gram)
    return float(np.linalg.norm(root @ matrix @ inv_root, ord="fro"))


def stabilizer_defect(
    action: np.ndarray,
    gram: np.ndarray,
    stabilizer: IdentityStabilizer,
) -> float:
    """``d_stab = min_{H ∈ H_id} ‖A − H‖_G`` (ADR-0246 §3.2–§3.3).

    The lawfulness distance of an induced action ``A`` from the permitted identity
    actions. Zero iff ``A`` equals a permitted action. Under the locked singleton
    ``H_id = { I }`` this is exactly ``‖A − I‖_G`` — a pass/fail distance, not a
    corrector.
    """
    action = np.asarray(action, dtype=np.float64)
    gram = np.asarray(gram, dtype=np.float64)
    if not stabilizer.members:
        raise ValueError("stabilizer must contain at least one permitted action")
    return min(
        _g_weighted_frobenius(action - np.asarray(H, dtype=np.float64), gram)
        for H in stabilizer.members
    )


def stabilizer_defect_for_versor(
    geometry: IdentityManifoldGeometry,
    versor: np.ndarray,
    stabilizer: IdentityStabilizer | None = None,
) -> float:
    """``d_stab`` for a versor's induced action against ``geometry``.

    Defaults to the locked singleton ``H_id = { I }`` sized to the value frame.
    """
    action = geometry.induced_action(versor)
    if stabilizer is None:
        stabilizer = IdentityStabilizer.singleton(action.shape[0])
    return stabilizer_defect(action, geometry.gram, stabilizer)
