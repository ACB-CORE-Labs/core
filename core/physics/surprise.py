"""
core/physics/surprise.py

Surprise Residual Operator + Dual with Conformal Procrustes
ADR-0239

S(x) = x - proj_B_union(x)
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.versor import versor_condition
from core.physics.dynamic_manifold import conformal_procrustes, procrustes_residual

_ETA5 = np.diag([1.0, 1.0, 1.0, 1.0, -1.0]).astype(np.float64)
_NEAR_ZERO = 1e-12
_CLOSURE_TOL = 1e-6


def surprise_residual(
    x: np.ndarray,
    basis: np.ndarray,
    eta: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, float]:
    """
    Project x onto the current admissible blade span and return residual.

    basis: columns are the current basis blades (from signature_aware_pca
           or the live admissibility region).
    For 5-vectors: Minkowski-aware projection with eta = diag(+,+,+,+,-).
    For 32-vectors: Euclidean coefficient projection onto orthonormalized columns.
    Returns (residual_vector, residual_norm).
    """
    x_arr = np.asarray(x, dtype=np.float64)
    B = np.asarray(basis, dtype=np.float64)
    if B.ndim == 1:
        B = B.reshape(-1, 1)

    if x_arr.shape[0] == 5 and B.shape[0] == 5:
        if eta is None:
            eta = _ETA5
        coeffs = []
        for i in range(B.shape[1]):
            b = B[:, i]
            denom = float(b @ (eta @ b)) + 1e-12
            c = float(x_arr @ (eta @ b)) / denom
            coeffs.append(c)
        proj = B @ np.array(coeffs, dtype=np.float64)
        residual = x_arr - proj
        return residual, float(np.linalg.norm(residual))

    if x_arr.shape[0] == N_COMPONENTS:
        # Gram-Schmidt on columns of B (or rows if shape is (k, 32))
        if B.shape[0] == N_COMPONENTS:
            cols = [B[:, i] for i in range(B.shape[1])]
        elif B.shape[1] == N_COMPONENTS:
            cols = [B[i, :] for i in range(B.shape[0])]
        else:
            raise ValueError("basis must align with 32-component multivectors")
        ortho: list[np.ndarray] = []
        for v in cols:
            w = v.copy()
            for u in ortho:
                w = w - float(np.dot(w, u)) * u
            n = float(np.linalg.norm(w))
            if n > _NEAR_ZERO:
                ortho.append(w / n)
        if not ortho:
            return x_arr.copy(), float(np.linalg.norm(x_arr))
        proj = np.zeros(N_COMPONENTS, dtype=np.float64)
        for u in ortho:
            proj = proj + float(np.dot(x_arr, u)) * u
        residual = x_arr - proj
        return residual, float(np.linalg.norm(residual))

    raise ValueError("surprise_residual expects 5-vector or 32-vector x")


def dual_procrustes_surprise(
    P: np.ndarray,
    Q: np.ndarray,
    current_basis: np.ndarray,
) -> dict:
    """
    The dual operator: run Procrustes and Surprise together.
    Returns a full audit dictionary.
    """
    V, proc_residual = conformal_procrustes(P, Q)
    Q_arr = np.asarray(Q, dtype=np.float64)
    if Q_arr.ndim == 2 and Q_arr.shape[0] == 5:
        probe = Q_arr.mean(axis=1)
    elif Q_arr.shape == (N_COMPONENTS,):
        probe = Q_arr
    elif Q_arr.ndim == 2 and Q_arr.shape[1] == N_COMPONENTS:
        probe = Q_arr.mean(axis=0)
    else:
        probe = np.asarray(Q_arr, dtype=np.float64).ravel()
        if probe.shape[0] not in (5, N_COMPONENTS):
            # fall back: surprise of zeros
            probe = np.zeros(5 if current_basis.shape[0] == 5 else N_COMPONENTS)

    sur_vec, sur_norm = surprise_residual(probe, current_basis)
    closed = True
    if np.asarray(V).shape == (N_COMPONENTS,):
        closed = versor_condition(V) < _CLOSURE_TOL

    return {
        "versor": V,
        "procrustes_residual": float(proc_residual),
        "surprise_vector": sur_vec,
        "surprise_norm": float(sur_norm),
        "transfer_accepted": bool(
            proc_residual < 1e-5 and sur_norm < 1e-4 and closed
        ),
        "versor_closed": bool(closed),
    }


# --- Aliases used by extended harness / biography path ---

def dual_operator(
    x: np.ndarray,
    basis: Union[np.ndarray, Sequence[np.ndarray]],
    analogs: Sequence[Tuple[str, np.ndarray, np.ndarray]],
    *,
    kappa: float = 1.0,
    productive_threshold: float = 0.35,
) -> dict:
    """Extended dual for multivector analogy seeds (ADR-0240 harness)."""
    if isinstance(basis, np.ndarray):
        B = basis
    else:
        cols = [np.asarray(b, dtype=np.float64).ravel() for b in basis]
        B = np.column_stack(cols) if cols else np.zeros((N_COMPONENTS, 0))
    sur_vec, sur_norm = surprise_residual(np.asarray(x, dtype=np.float64), B)
    if not analogs:
        return {
            "surprise_norm": sur_norm,
            "procrustes_residual": float("inf"),
            "productive": False,
            "kappa": float(kappa),
            "selected_analog_id": None,
            "versor": None,
        }
    aid, src, tgt = analogs[0]
    V, proc_r = conformal_procrustes(src, tgt)
    thr = float(productive_threshold) / max(float(kappa), 1e-12)
    productive = proc_r <= thr and sur_norm >= 0.0
    return {
        "surprise_norm": sur_norm,
        "procrustes_residual": float(proc_r),
        "productive": bool(productive),
        "kappa": float(kappa),
        "selected_analog_id": aid,
        "versor": V,
        "surprise_vector": sur_vec,
    }
