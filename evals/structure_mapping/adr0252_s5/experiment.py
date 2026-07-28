"""§5.3 the three decisive measurements, §5.4 the verdict — as executable rule.

The criterion is code, not prose, and it is committed **before** the run
(``docs/research/sme-experiment-preregistration-2026-07-28.md`` records the
same thresholds and the commit that carried them). A criterion chosen after
seeing results is the failure mode this experiment has already suffered twice;
putting the thresholds in a module that the run imports is the cheapest
available guard against choosing them a third time.

Run:  ``uv run python -m evals.structure_mapping.adr0252_s5.experiment``
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Sequence

import numpy as np

from core.physics.dynamic_manifold import conformal_procrustes
from evals.structure_mapping.adr0252_s5 import corpus as corpus_mod
from evals.structure_mapping.adr0252_s5 import embedding as emb

# ---------------------------------------------------------------------------
# The pre-registered thresholds. Changing one of these invalidates the verdict.
# ---------------------------------------------------------------------------

#: (a) separability — ROC AUC of residual as a "different structure" score.
AUC_FLOOR: Final[float] = 0.90
#: (a) a single threshold τ must classify both sides at this rate.
CLASSIFY_FLOOR: Final[float] = 0.95
#: (b) attribute-variant residuals must sit under τ, and their median must be
#: no more than this fraction of the cross-structure median.
INVARIANCE_RATIO_CEILING: Final[float] = 0.25
#: Non-convergence budget. Above this the run is VOID, not NO-GO — an
#: instrument that refuses to answer has not answered.
NONCONVERGENCE_CEILING: Final[float] = 0.05

VARIANTS: Final[dict[str, float]] = {
    "RS-A": emb.ATTR_SCALE_STRUCTURE_ONLY,
    "RS-B": emb.ATTR_SCALE_ATTRIBUTE_BEARING,
}


@dataclass(frozen=True)
class PairResidual:
    left: str
    right: str
    residual: float | None  # None == the aligner raised


def residual(a: np.ndarray, b: np.ndarray) -> float | None:
    try:
        _, res = conformal_procrustes(a, b)
    except Exception:  # noqa: BLE001 — recorded as non-convergence, never as distance
        return None
    value = float(res)
    if not np.isfinite(value):
        return None
    return value


def roc_auc(same: Sequence[float], cross: Sequence[float]) -> float:
    """P(cross residual > same residual), ties counted as half."""
    if not same or not cross:
        return float("nan")
    wins = 0.0
    for s in same:
        for c in cross:
            if c > s:
                wins += 1.0
            elif c == s:
                wins += 0.5
    return wins / (len(same) * len(cross))


def best_threshold(same: Sequence[float], cross: Sequence[float]) -> tuple[float, float, float]:
    """τ maximising min(same-below-rate, cross-above-rate); returns (τ, below, above)."""
    if not same or not cross:
        return (float("nan"),) * 3
    candidates = sorted(set(list(same) + list(cross)))
    midpoints = [
        (candidates[i] + candidates[i + 1]) / 2.0 for i in range(len(candidates) - 1)
    ] or [candidates[0]]
    best = (float("nan"), 0.0, 0.0)
    best_score = -1.0
    for tau in midpoints:
        below = sum(1 for s in same if s < tau) / len(same)
        above = sum(1 for c in cross if c > tau) / len(cross)
        score = min(below, above)
        if score > best_score:
            best_score, best = score, (tau, below, above)
    return best


def run_variant(name: str, attr_scale: float) -> dict[str, Any]:
    cases, labels = corpus_mod.build_corpus()

    # --- blind stage: labels are not read below this line until scoring ---
    clouds: dict[str, np.ndarray] = {c.case_id: emb.embed(c.graph, attr_scale=attr_scale) for c in cases}
    ids = [c.case_id for c in cases]
    pairs: list[PairResidual] = []
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            pairs.append(PairResidual(ids[i], ids[j], residual(clouds[ids[i]], clouds[ids[j]])))
    # --- scoring stage: labels enter here and nowhere earlier ---

    nonconverged = [p for p in pairs if p.residual is None]
    converged = [p for p in pairs if p.residual is not None]
    noncon_rate = len(nonconverged) / len(pairs) if pairs else 0.0

    same = [p.residual for p in converged if labels[p.left] == labels[p.right]]
    cross = [p.residual for p in converged if labels[p.left] != labels[p.right]]

    auc = roc_auc(same, cross)
    tau, below, above = best_threshold(same, cross)
    margin = (min(cross) - max(same)) if same and cross else float("nan")
    separable = (
        noncon_rate <= NONCONVERGENCE_CEILING
        and auc >= AUC_FLOOR
        and below >= CLASSIFY_FLOOR
        and above >= CLASSIFY_FLOOR
    )

    # (b) attribute-invariance
    inv_rows = []
    for kind, left, right in corpus_mod.invariance_pairs():
        r = residual(emb.embed(left.graph, attr_scale=attr_scale), emb.embed(right.graph, attr_scale=attr_scale))
        inv_rows.append({"perturbation": kind, "left": left.case_id, "right": right.case_id, "residual": r})
    inv_values = [row["residual"] for row in inv_rows if row["residual"] is not None]
    cross_median = statistics.median(cross) if cross else float("nan")
    inv_median = statistics.median(inv_values) if inv_values else float("nan")
    invariant = (
        len(inv_values) == len(inv_rows)
        and all(v < tau for v in inv_values)
        and (inv_median <= INVARIANCE_RATIO_CEILING * cross_median)
    )

    # (c) structure-sensitivity
    sens_rows = []
    for kind, left, right in corpus_mod.sensitivity_pairs():
        r = residual(emb.embed(left.graph, attr_scale=attr_scale), emb.embed(right.graph, attr_scale=attr_scale))
        sens_rows.append({"minimal_pair": kind, "left": left.case_id, "right": right.case_id, "residual": r})
    sens_values = [row["residual"] for row in sens_rows if row["residual"] is not None]
    sensitive = len(sens_values) == len(sens_rows) and all(v > tau for v in sens_values)

    # (d) systematicity — reported, not gating (§5.4 names only a, b, c)
    syst_rows = []
    for kind, left, right in corpus_mod.systematicity_pairs():
        r = residual(emb.embed(left.graph, attr_scale=attr_scale), emb.embed(right.graph, attr_scale=attr_scale))
        syst_rows.append({"comparison": kind, "left": left.case_id, "right": right.case_id, "residual": r})

    verdict = "GO" if (separable and invariant and sensitive) else "NO-GO"
    if noncon_rate > NONCONVERGENCE_CEILING:
        verdict = "VOID"

    return {
        "variant": name,
        "attr_scale": attr_scale,
        "n_cases": len(cases),
        "n_pairs": len(pairs),
        "nonconvergence_rate": noncon_rate,
        "separability": {
            "auc": auc,
            "threshold": tau,
            "same_below_rate": below,
            "cross_above_rate": above,
            "same_median": statistics.median(same) if same else None,
            "cross_median": cross_median,
            "margin_min_cross_minus_max_same": margin,
            "n_same_pairs": len(same),
            "n_cross_pairs": len(cross),
            "pass": separable,
        },
        "attribute_invariance": {
            "rows": inv_rows,
            "median": inv_median,
            "ratio_to_cross_median": (inv_median / cross_median) if cross_median else None,
            "pass": invariant,
        },
        "structure_sensitivity": {"rows": sens_rows, "pass": sensitive},
        "systematicity": {"rows": syst_rows},
        "verdict": verdict,
    }


#: Diagnostic sweep. Added AFTER the run, and it touches no threshold above —
#: it exists to answer "is the verdict an artifact of ATTR_SCALE=0.02?" with a
#: curve instead of an opinion. The criterion constants are unchanged; `git log
#: -p` on this file shows the only post-run edit is this block.
SWEEP_SCALES: Final[tuple[float, ...]] = (0.0, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1)


def sweep() -> list[dict[str, Any]]:
    """Re-run (a), (b) and (c) across ATTR_SCALE, under the same thresholds."""
    cases, labels = corpus_mod.build_corpus()
    inv_pairs = corpus_mod.invariance_pairs()
    sens = corpus_mod.sensitivity_pairs()
    rows: list[dict[str, Any]] = []
    for scale in SWEEP_SCALES:
        clouds = {c.case_id: emb.embed(c.graph, attr_scale=scale) for c in cases}
        ids = [c.case_id for c in cases]
        same: list[float] = []
        cross: list[float] = []
        for i in range(len(ids)):
            for j in range(i + 1, len(ids)):
                r = residual(clouds[ids[i]], clouds[ids[j]])
                if r is None:
                    continue
                (same if labels[ids[i]] == labels[ids[j]] else cross).append(r)
        auc = roc_auc(same, cross)
        tau, below, above = best_threshold(same, cross)
        inv_values = [
            residual(emb.embed(left.graph, attr_scale=scale), emb.embed(right.graph, attr_scale=scale))
            for _, left, right in inv_pairs
        ]
        rescale_values = [
            v for (kind, _, _), v in zip(inv_pairs, inv_values) if kind == "rescale" and v is not None
        ]
        sens_values = {
            kind: residual(emb.embed(left.graph, attr_scale=scale), emb.embed(right.graph, attr_scale=scale))
            for kind, left, right in sens
        }
        clean_inv = [v for v in inv_values if v is not None]
        cross_median = statistics.median(cross) if cross else float("nan")
        rows.append(
            {
                "attr_scale": scale,
                "auc": auc,
                "threshold": tau,
                "same_below_rate": below,
                "cross_above_rate": above,
                "invariance_median": statistics.median(clean_inv) if clean_inv else None,
                "rescale_median": statistics.median(rescale_values) if rescale_values else None,
                "cross_median": cross_median,
                "minimal_pairs": sens_values,
                "separability_pass": auc >= AUC_FLOOR
                and below >= CLASSIFY_FLOOR
                and above >= CLASSIFY_FLOOR,
                "invariance_pass": len(clean_inv) == len(inv_values)
                and all(v < tau for v in clean_inv)
                and statistics.median(clean_inv) <= INVARIANCE_RATIO_CEILING * cross_median,
                "sensitivity_pass": all(
                    v is not None and v > tau for v in sens_values.values()
                ),
            }
        )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=None, help="write the JSON report here")
    args = parser.parse_args(argv)

    report: dict[str, Any] = {
        "experiment": "ADR-0252 §5 structure-mapping acceptance gate",
        "criterion": {
            "auc_floor": AUC_FLOOR,
            "classify_floor": CLASSIFY_FLOOR,
            "invariance_ratio_ceiling": INVARIANCE_RATIO_CEILING,
            "nonconvergence_ceiling": NONCONVERGENCE_CEILING,
            "verdict_rule": "GO iff separability AND attribute-invariance AND structure-sensitivity on the same variant",
        },
        "variants": [run_variant(name, scale) for name, scale in VARIANTS.items()],
        "diagnostic_sweep": sweep(),
    }
    verdicts = {v["variant"]: v["verdict"] for v in report["variants"]}
    report["verdict_by_variant"] = verdicts
    report["overall_verdict"] = "GO" if "GO" in verdicts.values() else "NO-GO"

    payload = json.dumps(report, indent=2, sort_keys=True, default=float)
    report["deterministic_digest"] = hashlib.sha256(payload.encode()).hexdigest()
    text = json.dumps(report, indent=2, sort_keys=True, default=float)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
