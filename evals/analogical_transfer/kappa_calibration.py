"""ADR-0242 §5-P1 — live κ line-search caller (calibration pipeline only).

`core.physics.goldtether.propose_kappa_line_search` and its internal
`kappa_search_event` telemetry emission were fully implemented and pinned
(`tests/test_adr_0242_carry_seams.py`) but had zero live call sites.  This
module is the live caller, confined to the ADR-0240 analogical-transfer
calibration pipeline per the master plan's R-04 mitigation ("trace
generation ... limited strictly to the calibration and training-loop
pipelines" — never a hot/serve path; `chat/runtime.py` must never import
this package).

What is calibrated: in `core.physics.surprise.dual_operator` the
productive-transfer threshold is κ-scaled (``thr = productive_threshold /
κ``).  The objective below proposes the in-bounds κ whose scaled threshold
sits closest to the worst measured Procrustes residual of the calibration
corpus — i.e. κ is tuned so the acceptance bar tracks the corpus's actual
structural-residual scale.  The result is PROPOSAL-ONLY: nothing here
mutates `GoldTetherMonitor` state, COHERENT standing, or serve autonomy;
failures fall back to baseline κ = 1.0 inside the search itself.
"""

from __future__ import annotations

import math
from typing import Any, Sequence, cast

import numpy as np

from core.physics.dynamic_manifold import conformal_procrustes
from core.physics.goldtether import kappa_search_event, propose_kappa_line_search
from evals.analogical_transfer.harness import TransferCase, make_fixture_pair


def calibrate_transfer_kappa(
    cases: Sequence[TransferCase] | None = None,
    *,
    productive_threshold: float = 0.35,
    lower: float = 0.1,
    upper: float = 2.0,
    evaluation_budget: int = 16,
    sink: Any | None = None,
) -> dict[str, Any]:
    """Propose a κ for the transfer corridor via Fibonacci section search.

    Per-case Procrustes residuals are measured ONCE, outside the search
    loop, so the κ objective is cheap arithmetic (R-04: bounded
    calibration cost).  Cases whose residual is not measurable
    (Procrustes refusal or non-finite residual) are excluded and counted;
    if none remain the calibration refuses (typed ``ValueError``) rather
    than proposing κ from nothing.

    When ``sink`` is provided (any ``emit(line: str)`` object), the
    §5-P1 ``kappa_search_event`` fires exactly once from inside
    :func:`core.physics.goldtether.propose_kappa_line_search`.
    """
    corpus = tuple(cases) if cases is not None else (make_fixture_pair(),)
    if not corpus:
        raise ValueError("calibrate_transfer_kappa: cases must be non-empty")
    threshold = float(productive_threshold)
    if not math.isfinite(threshold) or threshold <= 0.0:
        raise ValueError("productive_threshold must be finite and > 0")

    residuals: list[float] = []
    refused = 0
    for case in corpus:
        try:
            # conformal_procrustes accepts sequences of 32-vectors (same call
            # shape as the harness); its annotation is narrower than runtime.
            proc_residual = float(
                conformal_procrustes(
                    cast(np.ndarray, case.source),
                    cast(np.ndarray, case.target),
                )[1]
            )
        except ValueError:
            refused += 1
            continue
        if not math.isfinite(proc_residual):
            refused += 1
            continue
        residuals.append(proc_residual)
    if not residuals:
        raise ValueError(
            "calibrate_transfer_kappa refused: no admissible cases "
            f"({refused} of {len(corpus)} procrustes-refused or non-finite)"
        )

    # Worst measured structural residual is the binding acceptance constraint.
    r_star = max(residuals)

    def residual_fn(kappa: float) -> float:
        return (threshold / float(kappa) - r_star) ** 2

    proposed_kappa, outcome = propose_kappa_line_search(
        residual_fn,
        lower=float(lower),
        upper=float(upper),
        evaluation_budget=int(evaluation_budget),
        objective_id="analogical_transfer_kappa",
        objective_version="v1",
        sink=sink,
    )
    return {
        "kind": "analogical_transfer_kappa_calibration",
        "proposed_kappa": float(proposed_kappa),
        "productive_threshold": threshold,
        "max_procrustes_residual": r_star,
        "case_count": len(residuals),
        "refused_case_count": refused,
        "event": kappa_search_event(proposed_kappa, outcome),
    }


__all__ = ["calibrate_transfer_kappa"]
