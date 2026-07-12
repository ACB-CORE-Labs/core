"""
core/physics/surprise.py

Surprise Residual Operator + Dual with Conformal Procrustes
ADR-0239

    S(x) = x - proj_B(x)

where ``proj_B`` is the EXACT metric-orthogonal projection of ``x`` onto the
admissible span under the Cl(4,1) inner product (:func:`algebra.cga.cga_inner`) —
NOT a Euclidean coefficient projection. The Euclidean projection the previous
implementation used ignored the (+,+,+,+,-) signature and the blade grade
structure, so "inside the admissible span" was judged by the wrong geometry.
See docs/research/third-door-blueprint-fidelity.md §6 (finding #20).

Magnitude vs projection — these are deliberately different:
  * The PROJECTION is metric-exact (``cga_inner`` / η), so *what counts as
    explained* is judged by the true CGA geometry.
  * The residual MAGNITUDE ``sur_norm`` is the DEFINITE (Euclidean) norm of the
    residual vector, so it is ``0`` iff nothing is unexplained. It must be
    definite because the CGA metric is INDEFINITE: the reversion norm
    ``sqrt(|<R R~>_0|)`` vanishes on nonzero null directions (``n_o`` / ``n_inf``,
    the conformal light cone that embeddings live on), which would report a false
    ``0`` surprise for a fully-unexplained null component — a soundness hole in
    the gate. "No L2 for DISTANCE" is a doctrine about the reasoning metric; the
    unexplained-energy readout after a metric-exact projection is a different
    quantity and is correctly definite.

Fail-closed contract: the projection is REFUSED (typed
:class:`SurpriseResidualError`) when the metric is degenerate on the span — a
null direction with no reciprocal, e.g. a lone ``n_o`` column. Mere linear
dependence among non-null columns is admitted (``lstsq`` projects onto the actual
span); only genuine metric degeneracy is unprojectable.
"""

from __future__ import annotations

from typing import Optional, Sequence, Tuple, Union

import numpy as np

from algebra.cga import cga_inner
from algebra.cl41 import N_COMPONENTS, grade_project
from algebra.versor import versor_condition
from core.physics.dynamic_manifold import conformal_procrustes

_ETA5 = np.diag([1.0, 1.0, 1.0, 1.0, -1.0]).astype(np.float64)
_NEAR_ZERO = 1e-12
_CLOSURE_TOL = 1e-6
_GRADE_TOL = 1e-9
_MAX_GRADE = 5


class SurpriseResidualError(ValueError):
    """Fail-closed refusal from :func:`surprise_residual`.

    Raised when the admissible span is metric-degenerate (a null direction with
    no reciprocal — the projection is not geometrically realizable) or when the
    operator detects grade leakage (an internal invariant breach). Subclasses
    ``ValueError`` so a caller that fail-closes on ``ValueError`` records it as a
    refusal rather than crashing.
    """

    def __init__(self, reason: str, **disclosure) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"surprise_residual refused [{reason}]: {self.disclosure}")


def _grades_exact(X: np.ndarray) -> set[int]:
    """Grades with any (exactly) nonzero coefficient — used for the ALLOWED set,
    so a legitimately-present-but-tiny basis grade cannot be misread as leakage."""
    return {k for k in range(_MAX_GRADE + 1) if np.any(grade_project(X, k))}


def _grades_present(X: np.ndarray, tol: float = _GRADE_TOL) -> set[int]:
    """Grades with non-trivial block norm — used for the RESIDUAL, which is a
    float computation and carries numerical dust below ``tol``."""
    return {
        k
        for k in range(_MAX_GRADE + 1)
        if float(np.linalg.norm(grade_project(X, k))) > tol
    }


def _metric_projection_coeffs(B: np.ndarray, gram: np.ndarray, rhs: np.ndarray) -> np.ndarray:
    """Solve ``gram @ c = rhs`` for the metric-orthogonal projection coefficients.

    Fail-CLOSED when the metric is degenerate ON THE SPAN (``rank(gram) <
    rank(B)`` — a null direction with no reciprocal). Mere linear dependence among
    non-null columns (``rank(B) < k``) is admitted: ``lstsq`` projects onto the
    actual span. This is stricter than the old Euclidean path exactly where
    geometry demands it (null refusal) and no stricter where it does not
    (redundant columns), so a merely-redundant live basis such as ``[1, source]``
    is not spuriously refused.
    """
    rank_b = int(np.linalg.matrix_rank(B))
    rank_g = int(np.linalg.matrix_rank(gram))
    if rank_g < rank_b:
        # The degenerate direction is the null-space of the metric restricted to
        # the span — the right-singular vector of ``gram`` with the smallest
        # singular value. This is a null COMBINATION of columns, which a
        # zero-diagonal scan alone would miss (both columns can be individually
        # non-null yet metric-parallel). ``null_columns`` is retained as the
        # (possibly empty) subset with zero self-inner.
        _u, _sv, vh = np.linalg.svd(gram)
        degenerate_combo = [round(float(v), 6) for v in vh[-1]]
        null_columns = [
            i for i in range(B.shape[1]) if abs(float(gram[i, i])) < _NEAR_ZERO
        ]
        raise SurpriseResidualError(
            "degenerate_metric_span",
            rank_basis=rank_b,
            rank_gram=rank_g,
            null_columns=null_columns,
            degenerate_combo=degenerate_combo,
        )
    coeffs, *_ = np.linalg.lstsq(gram, rhs, rcond=None)
    return coeffs


def surprise_residual(
    x: np.ndarray,
    basis: np.ndarray,
    eta: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, float]:
    """Metric-orthogonal surprise residual ``S(x) = x - proj_B(x)``.

    ``basis``: columns are the admissible directions (from ``signature_aware_pca``
    or the live admissibility region).

    - 5-vectors: projection under the Minkowski metric ``eta = diag(+,+,+,+,-)``.
    - 32-vectors: projection under the full Cl(4,1) inner product ``cga_inner``.

    Both branches solve the metric normal equations ``G c = r`` (``G_ij =
    <b_i,b_j>``, ``r_i = <b_i,x>``) via ``lstsq``, fail-closed on a
    metric-degenerate span. Returns ``(residual_vector, residual_norm)`` where the
    norm is the DEFINITE (Euclidean) magnitude of the residual — 0 iff nothing is
    unexplained (see the module docstring on why this is not the metric norm).
    """
    x_arr = np.asarray(x, dtype=np.float64)
    B = np.asarray(basis, dtype=np.float64)
    if B.ndim == 1:
        B = B.reshape(-1, 1)

    # --- 5-vector (grade-1 Cl(4,1) vector) branch: eta-metric projection ------
    if x_arr.shape[0] == 5 and B.shape[0] == 5:
        if eta is None:
            eta = _ETA5
        if B.shape[1] == 0:
            return x_arr.copy(), float(np.linalg.norm(x_arr))
        gram = B.T @ (eta @ B)
        rhs = B.T @ (eta @ x_arr)
        coeffs = _metric_projection_coeffs(B, gram, rhs)
        residual = x_arr - B @ coeffs
        return residual, float(np.linalg.norm(residual))

    # --- 32-vector (Cl(4,1) multivector) branch: cga_inner projection --------
    if x_arr.shape[0] == N_COMPONENTS:
        if B.shape[0] != N_COMPONENTS and B.shape[1] == N_COMPONENTS:
            B = B.T
        if B.shape[0] != N_COMPONENTS:
            raise ValueError("basis must align with 32-component multivectors")
        k = B.shape[1]
        if k == 0:
            return x_arr.copy(), float(np.linalg.norm(x_arr))
        cols = [B[:, i] for i in range(k)]
        gram = np.array(
            [[cga_inner(cols[i], cols[j]) for j in range(k)] for i in range(k)],
            dtype=np.float64,
        )
        rhs = np.array([cga_inner(cols[i], x_arr) for i in range(k)], dtype=np.float64)
        coeffs = _metric_projection_coeffs(B, gram, rhs)
        residual = x_arr - B @ coeffs

        # Grade-support containment: residual is a linear combination of x and the
        # basis columns, so its grades can only be a subset of theirs. ``allowed``
        # uses EXACT nonzero (a tiny-but-present basis grade still counts, so an
        # amplified sub-tolerance block is not misread as leakage); the residual
        # uses a tolerance (float dust). A genuine leak means an implementation
        # bug — fail-closed rather than silently corrupt grade.
        allowed = _grades_exact(x_arr)
        for col in cols:
            allowed |= _grades_exact(col)
        leaked = _grades_present(residual) - allowed
        if leaked:
            raise SurpriseResidualError(
                "grade_leak", leaked=sorted(leaked), allowed=sorted(allowed)
            )

        return residual, float(np.linalg.norm(residual))

    raise ValueError("surprise_residual expects 5-vector or 32-vector x")


def dual_procrustes_surprise(
    P: np.ndarray,
    Q: np.ndarray,
    current_basis: np.ndarray,
) -> dict:
    """The dual operator: run Procrustes and Surprise together.

    ``transfer_accepted`` is a PRODUCTIVE-TRANSFER gate: a structural match was
    found (low Procrustes residual) AND the probe is inside the admissible span
    (low surprise) — i.e. it is safe to transport ``P``'s solution to ``Q``. High
    surprise is NOT a transfer; it is a *discovery* signal (wired separately). A
    fail-closed surprise refusal (degenerate basis) is recorded, not raised.
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
            probe = np.zeros(5 if current_basis.shape[0] == 5 else N_COMPONENTS)

    refused: Optional[str] = None
    try:
        sur_vec, sur_norm = surprise_residual(probe, current_basis)
    except SurpriseResidualError as exc:
        sur_vec, sur_norm, refused = None, float("inf"), exc.reason

    closed = True
    if np.asarray(V).shape == (N_COMPONENTS,):
        closed = versor_condition(V) < _CLOSURE_TOL

    return {
        "versor": V,
        "procrustes_residual": float(proc_residual),
        "surprise_vector": sur_vec,
        "surprise_norm": float(sur_norm),
        "transfer_accepted": bool(
            refused is None and proc_residual < 1e-5 and sur_norm < 1e-4 and closed
        ),
        "versor_closed": bool(closed),
        "surprise_refused": refused,
    }


# --- Aliases used by extended harness / biography path ---

def dual_operator(
    x: np.ndarray,
    basis: Union[np.ndarray, Sequence[np.ndarray]],
    analogs: Sequence[Tuple[str, np.ndarray, np.ndarray]],
    *,
    kappa: float = 1.0,
    productive_threshold: float = 0.35,
    surprise_threshold: float = 0.35,
) -> dict:
    """Extended dual for multivector analogy seeds (ADR-0240 harness).

    ``productive`` is a PRODUCTIVE-TRANSFER gate that now depends on BOTH signals:
    a structural match (``proc_r <= thr``) AND the query being inside the
    admissible span (``sur_norm <= surprise_threshold``). The previous
    ``sur_norm >= 0.0`` conjunct was always true, so surprise never gated. A HIGH
    ``sur_norm`` marks a discovery candidate, not a productive transfer.
    """
    if isinstance(basis, np.ndarray):
        B = basis
    else:
        cols = [np.asarray(b, dtype=np.float64).ravel() for b in basis]
        B = np.column_stack(cols) if cols else np.zeros((N_COMPONENTS, 0))

    try:
        sur_vec, sur_norm = surprise_residual(np.asarray(x, dtype=np.float64), B)
        surprise_refused: Optional[str] = None
    except SurpriseResidualError as exc:
        sur_vec, sur_norm, surprise_refused = None, float("inf"), exc.reason

    if not analogs:
        return {
            "surprise_norm": float(sur_norm),
            "procrustes_residual": float("inf"),
            "productive": False,
            "kappa": float(kappa),
            "selected_analog_id": None,
            "versor": None,
            "surprise_refused": surprise_refused,
        }
    aid, src, tgt = analogs[0]
    V, proc_r = conformal_procrustes(src, tgt)
    thr = float(productive_threshold) / max(float(kappa), 1e-12)
    productive = (
        surprise_refused is None
        and proc_r <= thr
        and sur_norm <= float(surprise_threshold)
    )
    return {
        "surprise_norm": float(sur_norm),
        "procrustes_residual": float(proc_r),
        "productive": bool(productive),
        "kappa": float(kappa),
        "selected_analog_id": aid,
        "versor": V,
        "surprise_vector": sur_vec,
        "surprise_refused": surprise_refused,
    }
