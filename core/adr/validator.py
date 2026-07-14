"""
core/adr/validator.py

ADR-DAG conformal embedding Ψ(M) (R&D-Revised §2.4 / #21).

  SHA-256(M) → 10×3-byte segments → c_k ∈ [−1, 1]
  → 10 basis bivectors (planes 6..15) → simple-bivector projection
  → master blade = successive wedge of load-bearing ADR embeddings
  → proposal drift = ‖B_p ∧ A_master‖

Cross-check: does **not** reimplement GeometricDelta ABI validation
(``core/abi/geometric_delta_validator.py``). This module embeds ADR text into
geometry; that module validates GeometricDelta envelopes.
"""

from __future__ import annotations

import hashlib
from typing import Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product, grade_project

_BIVECTOR_PLANES = tuple(range(6, 16))  # 10 planes
_NEAR_ZERO = 1e-12
_SIMPLE_G4_TOL = 1e-9


class AdrDagValidationError(ValueError):
    """Fail-closed refusal from ADR-DAG embedding / drift checks."""

    def __init__(self, reason: str, **disclosure) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"adr_dag refused [{reason}]: {self.disclosure}")


def _grade_mass(v: np.ndarray) -> int:
    for g in range(5, -1, -1):
        if float(np.linalg.norm(grade_project(v, g))) > _NEAR_ZERO:
            return g
    return 0


def multivector_wedge(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Grade-raising wedge approximation: grade-project of geometric product.

    For pure blades this matches the outer product grade. Used for master-blade
    assembly and drift (B_p ∧ A_master).
    """
    a = np.asarray(A, dtype=np.float64)
    b = np.asarray(B, dtype=np.float64)
    ga, gb = _grade_mass(a), _grade_mass(b)
    target = min(5, ga + gb)
    if target == 0:
        return grade_project(geometric_product(a, b), 0)
    return grade_project(geometric_product(a, b), target).astype(np.float64)


def simple_bivector_project(B: np.ndarray) -> np.ndarray:
    """Project a multivector generator onto a simple bivector.

    Spec intent: pure grade-2 support that is *simple* (single plane). Pure
    multiplane grade-2 has nontrivial ``⟨B B⟩₄``; we always collapse to the
    dominant plane when more than one plane is occupied (deterministic).
    """
    arr = np.asarray(B, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise AdrDagValidationError("bad_shape", shape=tuple(arr.shape))
    B2 = grade_project(arr, 2).astype(np.float64)
    occupied = [i for i in _BIVECTOR_PLANES if abs(float(B2[i])) > _NEAR_ZERO]
    if len(occupied) <= 1:
        return B2
    # Multiplane → dominant-plane collapse (simple by construction).
    best_i = max(occupied, key=lambda i: abs(float(B2[i])))
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    out[best_i] = float(B2[best_i])
    return out


def embed_adr_markdown(markdown: str) -> np.ndarray:
    """Ψ(M): deterministic SHA-256 → 10 bivector coefficients → simple project.

    Identical markdown ⇒ identical 32-vector (replay pin).
    """
    if not isinstance(markdown, str):
        raise AdrDagValidationError("not_str", type=type(markdown).__name__)
    # Empty markdown is a valid document identity (still deterministic).
    digest = hashlib.sha256(markdown.encode("utf-8")).digest()  # 32 bytes
    B = np.zeros(N_COMPONENTS, dtype=np.float64)
    for k, plane in enumerate(_BIVECTOR_PLANES):
        # 3-byte segments; last 2 hash bytes unused (spec: 10×3=30).
        chunk = digest[k * 3 : k * 3 + 3]
        u = int.from_bytes(chunk, "big")  # 0 .. 2^24-1
        c = (u / float(0xFFFFFF)) * 2.0 - 1.0  # [-1, 1]
        B[plane] = c
    return simple_bivector_project(B)


def master_architecture_blade(
    embeddings: Sequence[np.ndarray],
) -> np.ndarray:
    """Assemble load-bearing ADR embeddings into a master architecture blade.

    Prefer successive wedge when non-degenerate; if a wedge step vanishes
    (parallel simple planes after projection), fall back to algebraic sum of
    simple bivectors so the master never fabricates a zero blade.
    """
    if not embeddings:
        raise AdrDagValidationError("empty_master_set")
    simples = [
        simple_bivector_project(np.asarray(e, dtype=np.float64))
        for e in embeddings
    ]
    wedge = simples[0].copy()
    for i, e in enumerate(simples[1:], start=1):
        w = multivector_wedge(wedge, e)
        if float(np.linalg.norm(w)) > _NEAR_ZERO:
            wedge = w
        # else: parallel/collinear under wedge — keep prior wedge, continue
    if float(np.linalg.norm(wedge)) > _NEAR_ZERO:
        return wedge.astype(np.float64)
    # Full wedge chain degenerate: superposition master (still deterministic).
    acc = np.zeros(N_COMPONENTS, dtype=np.float64)
    for e in simples:
        acc = acc + e
    if float(np.linalg.norm(acc)) < _NEAR_ZERO:
        raise AdrDagValidationError("degenerate_master_blade", at_index=0)
    return simple_bivector_project(acc)


def proposal_drift(B_proposal: np.ndarray, A_master: np.ndarray) -> float:
    """Drift = ‖B_p ∧ A_master‖ (Euclidean coeff norm of the wedge)."""
    Bp = simple_bivector_project(np.asarray(B_proposal, dtype=np.float64))
    Am = np.asarray(A_master, dtype=np.float64)
    if Am.shape != (N_COMPONENTS,):
        raise AdrDagValidationError("bad_master_shape", shape=tuple(Am.shape))
    w = multivector_wedge(Bp, Am)
    return float(np.linalg.norm(w))


def validate_proposal_against_master(
    proposal_markdown: str,
    master_markdowns: Sequence[str],
    *,
    max_drift: float = 1.0,
) -> tuple[bool, float, np.ndarray, np.ndarray]:
    """Embed proposal + masters; return (ok, drift, B_p, A_master)."""
    if not master_markdowns:
        raise AdrDagValidationError("empty_master_set")
    masters = [embed_adr_markdown(m) for m in master_markdowns]
    A = master_architecture_blade(masters)
    Bp = embed_adr_markdown(proposal_markdown)
    d = proposal_drift(Bp, A)
    ok = bool(d <= float(max_drift) + _NEAR_ZERO)
    return ok, d, Bp, A


__all__ = [
    "AdrDagValidationError",
    "embed_adr_markdown",
    "master_architecture_blade",
    "multivector_wedge",
    "proposal_drift",
    "simple_bivector_project",
    "validate_proposal_against_master",
]
