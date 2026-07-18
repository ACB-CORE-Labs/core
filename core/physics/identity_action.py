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

Pure (numpy + identity_manifold only), deterministic, float64, off-serving. This
module owns both the per-turn stabilizer defect (``d_stab``) and the lawful-only
path ledger (§3.4/§3.5): the identity path composes ONLY the induced actions of
turns certified lawful, refused turns insert break markers (never a soft-projected
``I``), and a scope change forces a hard break onto a new chain.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Sequence

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


# -- ADR-0246 §3.4/§3.5 lawful-only identity-path ledger -----------------------


@dataclass(frozen=True)
class PathBudget:
    """Two-level lawfulness budget (ADR-0246 §3.4).

    ``epsilon_turn`` bounds a single turn's ``d_stab`` (a large one-turn departure
    refuses immediately); ``epsilon_session`` bounds the composed lawful path's
    ``d_stab`` (slow accumulation of individually-lawful turns eventually refuses).
    """

    epsilon_turn: float
    epsilon_session: float


@dataclass(frozen=True)
class IdentityChainScope:
    """The scope that keys an identity-action chain (ADR-0246 §3.5).

    Any change to these forces a **hard break** — a new chain that does NOT
    continue the previous composed path. The frame, its geometry, the lawfulness
    policy, the session, and (when explicit) the biography epoch each redefine
    what "the path" means, so a path may only compose within a single scope.
    """

    pack_content_digest: str
    geometry_version: str
    policy_version: str
    session_id: str
    biography_epoch: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "pack_content_digest": self.pack_content_digest,
            "geometry_version": self.geometry_version,
            "policy_version": self.policy_version,
            "session_id": self.session_id,
            "biography_epoch": self.biography_epoch,
        }


def _chain_id(scope: IdentityChainScope, chain_index: int) -> str:
    """Deterministic full-SHA-256 chain id (ADR-0245 §2.3 — no truncation).

    Includes ``chain_index`` so a scope that recurs later in a session (e.g. a
    pack A → B → A cycle) still yields a distinct chain id.
    """
    payload = json.dumps(
        {**scope.as_dict(), "chain_index": int(chain_index)},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class IdentityPathLedger:
    """Immutable snapshot of the lawful-only identity path (ADR-0246 §4.2).

    ``a_path_lawful`` is the time-forward product of the induced actions of the
    turns certified lawful within this chain (``I`` for an empty chain). Refused
    turns are counted in ``break_count`` and excluded from the product — never
    composed as ``I`` (that would be the soft-projection §3.4 forbids).
    """

    chain_id: str
    scope: IdentityChainScope
    chain_index: int
    dimension: int
    a_path_lawful: np.ndarray
    d_stab_path: float
    composed_turn_count: int
    break_count: int
    session_admit: bool

    def ledger_digest(self) -> str:
        """Full-SHA-256 content id over the path state (LE f64 byte-order)."""
        digest = hashlib.sha256()
        digest.update(self.chain_id.encode("utf-8"))
        digest.update(
            np.ascontiguousarray(self.a_path_lawful, dtype=np.dtype("<f8")).tobytes()
        )
        digest.update(
            json.dumps(
                [self.chain_index, self.composed_turn_count, self.break_count],
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
        )
        return digest.hexdigest()

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "identity_path_v1",
            "chain_id": self.chain_id,
            "scope": self.scope.as_dict(),
            "chain_index": self.chain_index,
            "dimension": self.dimension,
            "a_path_lawful": [
                [float(x) for x in row] for row in self.a_path_lawful
            ],
            "d_stab_path": float(self.d_stab_path),
            "composed_turn_count": self.composed_turn_count,
            "break_count": self.break_count,
            "session_admit": self.session_admit,
            "ledger_digest": self.ledger_digest(),
        }


def advance_identity_path(
    ledger: IdentityPathLedger | None,
    scope: IdentityChainScope,
    action: np.ndarray,
    gram: np.ndarray,
    budget: PathBudget,
) -> tuple[IdentityPathLedger, dict[str, Any]]:
    """Fold one turn's raw induced action into the lawful-only path (§3.4/§3.5).

    Returns ``(new_ledger, turn_record)``. ``turn_record`` reports this turn's
    ``lawful`` / ``d_stab_turn`` / ``path_break`` / ``hard_break``. A turn is
    lawful iff ``d_stab(action) ≤ epsilon_turn`` under the locked singleton
    ``H_id={I}``; only lawful turns compose. A scope change (or an absent prior
    ledger) is a hard break that starts a fresh chain — the previous path is NOT
    continued. Immutable: ``ledger`` is never mutated.
    """
    action = np.asarray(action, dtype=np.float64)
    if action.ndim != 2 or action.shape[0] != action.shape[1]:
        raise ValueError(
            f"induced action must be a square matrix, got shape {action.shape}"
        )
    dimension = action.shape[0]
    stabilizer = IdentityStabilizer.singleton(dimension)
    d_stab_turn = stabilizer_defect(action, gram, stabilizer)
    lawful = d_stab_turn <= budget.epsilon_turn

    hard_break = ledger is None or ledger.scope != scope
    if hard_break:
        chain_index = 0 if ledger is None else ledger.chain_index + 1
        a_path = np.eye(dimension, dtype=np.float64)
        composed = 0
        breaks = 0
    else:
        assert ledger is not None  # not a hard break ⇒ prior ledger exists
        chain_index = ledger.chain_index
        a_path = ledger.a_path_lawful
        composed = ledger.composed_turn_count
        breaks = ledger.break_count

    if lawful:
        # time-forward: later turns act on the left of the accumulated frame action
        a_path = action @ a_path
        composed += 1
        path_break = False
    else:
        # break marker — excluded from the product; NOT composed as identity
        breaks += 1
        path_break = True

    d_stab_path = stabilizer_defect(a_path, gram, stabilizer)
    new_ledger = IdentityPathLedger(
        chain_id=_chain_id(scope, chain_index),
        scope=scope,
        chain_index=chain_index,
        dimension=dimension,
        a_path_lawful=a_path,
        d_stab_path=d_stab_path,
        composed_turn_count=composed,
        break_count=breaks,
        session_admit=(d_stab_path <= budget.epsilon_session),
    )
    turn_record = {
        "lawful": lawful,
        "d_stab_turn": d_stab_turn,
        "path_break": path_break,
        "hard_break": hard_break,
    }
    return new_ledger, turn_record


def raw_path_product(actions: Sequence[np.ndarray]) -> np.ndarray:
    """Time-forward product of ALL actions, lawful or not — **forensic only**.

    This is the category error §3.4 forbids for the live path (it mixes refused,
    ill-conditioned, and leaked actions into a fake "holonomy"). It exists solely
    so tests and forensics can demonstrate that the lawful-only product differs
    from the naive raw product. Never use it to admit a turn.
    """
    if not actions:
        raise ValueError("raw_path_product requires at least one action")
    result = np.eye(np.asarray(actions[0]).shape[0], dtype=np.float64)
    for action in actions:
        result = np.asarray(action, dtype=np.float64) @ result
    return result
