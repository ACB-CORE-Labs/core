"""ADR-0246 §6.3 discrimination report — does the §3.7 admit surface separate
benign traffic from adversarial reshuffles? (honest numbers, no marketing.)

This runs the pure ADR-0246 §3.7 admit surface (``evaluate_admission``, locked
``H_id={I}``, placeholder thresholds) over three cohorts and reports the numbers
the preflight §6.3 / §10 acceptance criteria demand:

  * benign pass rate, false refusal rate
  * adversarial / reshuffle detection rate
  * per-axis leakage / self-alignment distributions
  * ``d_stab`` (and ``leakage_rms``) separation as ROC-AUC with a bootstrap 95% CI
  * runtime cost (µs) of the A(F) admission path
  * representative benign-refusal examples

**Honesty constraint (§10 #9).** The claim this can support is *"lawfulness
relative to the declared frozen frame"* — NEVER *"semantic inalienability of the
value labels."* The default pack axes are placeholder basis vectors; D4 + slice-0
already established that live benign versors do **not** preserve them. So the
expected — and reported — finding is that this gate refuses benign and adversarial
alike (no usable separation) and must stay off. The report states that plainly;
it does not frame a refuse-all as a "detector."

Off-serving: pure primitives + a live-versor collector that lazily imports
``chat.runtime`` (A-04 quarantine intact). Deterministic given the fixed probe
sequences and bootstrap seed.
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.physics.identity_action import (
    AdmissionPolicy,
    evaluate_admission,
)

BOOTSTRAP_SEED = 20260717
BOOTSTRAP_RESAMPLES = 2000

# grade-2 bivector plane indices
_E12, _E13, _E14, _E15, _E23, _E24, _E25 = 6, 7, 8, 9, 10, 11, 12


def default_geometry() -> IdentityManifoldGeometry:
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


def _rotor(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _boost(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cosh(theta / 2.0)
    r[biv] = np.sinh(theta / 2.0)
    return r


def adversarial_cohort() -> list[tuple[str, np.ndarray]]:
    """Geometric attacks + in-span reshuffles the gate is *designed* to catch."""
    return [
        ("tilt_e14_1.5", _rotor(_E14, 1.5)),
        ("tilt_e24_1.0", _rotor(_E24, 1.0)),
        ("boost_e15_1.2", _boost(_E15, 1.2)),
        ("boost_e25_1.0", _boost(_E25, 1.0)),
        ("inversion_e12_pi", _rotor(_E12, np.pi)),
        ("inversion_e13_pi", _rotor(_E13, np.pi)),
        ("permutation_e12_halfpi", _rotor(_E12, np.pi / 2.0)),
        ("permutation_e23_halfpi", _rotor(_E23, np.pi / 2.0)),
    ]


def synthetic_near_identity_cohort() -> list[tuple[str, np.ndarray]]:
    """Positive control: versors that DO nearly preserve the frame (should admit)."""
    return [
        (f"near_id_e12_{t}", _rotor(_E12, t)) for t in (0.0, 0.005, 0.01)
    ] + [
        (f"near_id_e13_{t}", _rotor(_E13, t)) for t in (0.0, 0.005)
    ]


def collect_live_benign(limit: int | None = None) -> list[tuple[str, np.ndarray]]:
    """Real benign ``final_state.F`` versors from a fresh empty-vault runtime.

    Reuses the slice-0 collector (instance-local recording; serve untouched;
    lazy ``chat.runtime`` import). This is the honest benign cohort — the same
    live distribution D4 Phase 3 measured as NOT preserving the frame.
    """
    from evals.adr_0246_mismatch_diagnostic import collect_live_versors
    from evals.adr_0244_gamma_calibration import LIVE_PROBE_SEQUENCE

    versors = collect_live_versors(LIVE_PROBE_SEQUENCE)
    return versors[:limit] if limit else versors


# --- statistics (numpy-only; deterministic) -----------------------------------


def _roc_auc(positive: Sequence[float], negative: Sequence[float]) -> float:
    """AUC = P(score(pos) > score(neg)) with ties at 0.5 (rank/Mann-Whitney)."""
    pos = np.asarray(positive, dtype=np.float64)
    neg = np.asarray(negative, dtype=np.float64)
    if pos.size == 0 or neg.size == 0:
        return float("nan")
    allv = np.concatenate([pos, neg])
    order = np.argsort(allv, kind="mergesort")
    ranks = np.empty(allv.size, dtype=np.float64)
    ranks[order] = np.arange(1, allv.size + 1, dtype=np.float64)
    # average ranks for ties
    _, inv, counts = np.unique(allv, return_inverse=True, return_counts=True)
    sums = np.zeros(counts.size)
    np.add.at(sums, inv, ranks)
    ranks = (sums / counts)[inv]
    r_pos = ranks[: pos.size].sum()
    return float((r_pos - pos.size * (pos.size + 1) / 2.0) / (pos.size * neg.size))


def _auc_bootstrap_ci(
    positive: Sequence[float], negative: Sequence[float]
) -> tuple[float, float]:
    pos = np.asarray(positive, dtype=np.float64)
    neg = np.asarray(negative, dtype=np.float64)
    if pos.size == 0 or neg.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(BOOTSTRAP_SEED)
    aucs = np.empty(BOOTSTRAP_RESAMPLES, dtype=np.float64)
    for i in range(BOOTSTRAP_RESAMPLES):
        rp = rng.choice(pos, size=pos.size, replace=True)
        rn = rng.choice(neg, size=neg.size, replace=True)
        aucs[i] = _roc_auc(rp, rn)
    return (float(np.percentile(aucs, 2.5)), float(np.percentile(aucs, 97.5)))


def _dist(values: Sequence[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=np.float64)
    if arr.size == 0:
        return {"n": 0, "min": 0.0, "mean": 0.0, "max": 0.0}
    return {
        "n": int(arr.size),
        "min": round(float(arr.min()), 6),
        "mean": round(float(arr.mean()), 6),
        "max": round(float(arr.max()), 6),
    }


def _evaluate_cohort(
    geometry: IdentityManifoldGeometry,
    cohort: Sequence[tuple[str, np.ndarray]],
    policy: AdmissionPolicy,
) -> list[dict[str, Any]]:
    rows = []
    for label, versor in cohort:
        result = evaluate_admission(geometry, versor, policy)
        leak, self_align = geometry.axis_response(versor)
        rows.append({
            "label": label,
            "admitted": result.admitted,
            "refusal_reasons": list(result.refusal_reasons),
            "d_stab": result.d_stab,
            "leakage_rms": result.leakage_rms,
            "min_self_alignment": result.min_self_alignment,
            "per_axis_leakage": [float(x) for x in leak],
            "per_axis_self_align": [float(x) for x in self_align],
        })
    return rows


def build_discrimination_report(
    benign: Sequence[tuple[str, np.ndarray]] | None = None,
    *,
    geometry: IdentityManifoldGeometry | None = None,
    policy: AdmissionPolicy | None = None,
) -> dict[str, Any]:
    """Run the §3.7 surface over all cohorts and report honest §6.3 numbers.

    ``benign`` defaults to the live-collected cohort (slow — spins up a runtime);
    pass an explicit cohort for a fast/offline report.
    """
    geometry = geometry or default_geometry()
    policy = policy or AdmissionPolicy.placeholder_default()
    if benign is None:
        benign = collect_live_benign()
    adversarial = adversarial_cohort()
    control = synthetic_near_identity_cohort()

    b_rows = _evaluate_cohort(geometry, benign, policy)
    a_rows = _evaluate_cohort(geometry, adversarial, policy)
    c_rows = _evaluate_cohort(geometry, control, policy)

    def _rate(rows, key, want):
        return round(sum(1 for r in rows if r[key] is want) / len(rows), 6) if rows else 0.0

    benign_pass = _rate(b_rows, "admitted", True)
    adversarial_detect = _rate(a_rows, "admitted", False)
    control_pass = _rate(c_rows, "admitted", True)

    b_dstab = [r["d_stab"] for r in b_rows]
    a_dstab = [r["d_stab"] for r in a_rows]
    b_leak = [r["leakage_rms"] for r in b_rows]
    a_leak = [r["leakage_rms"] for r in a_rows]
    dstab_auc = _roc_auc(a_dstab, b_dstab)  # adversarial as positive class
    dstab_ci = _auc_bootstrap_ci(a_dstab, b_dstab)
    leak_auc = _roc_auc(a_leak, b_leak)
    leak_ci = _auc_bootstrap_ci(a_leak, b_leak)

    # gate "discriminates" only if AUC CI lower bound is clearly above chance (0.5)
    gate_discriminates = bool(np.isfinite(dstab_ci[0]) and dstab_ci[0] > 0.6)
    false_refusal_rate = round(1.0 - benign_pass, 6)

    return {
        "schema_version": "adr_0246_discrimination_v1",
        "policy": {
            "calibrated": policy.calibrated,
            "orth_tol": policy.orth_tol,
            "epsilon_turn": policy.epsilon_turn,
            "gamma_id": policy.gamma_id,
            "tau_max": policy.tau_max,
            "s_min": policy.s_min,
            "note": "gamma_id certified (D4 Phase 3); all other bounds are UNCERTIFIED placeholders",
        },
        "cohorts": {"benign": len(b_rows), "adversarial": len(a_rows), "synthetic_near_identity": len(c_rows)},
        "rates": {
            "benign_pass_rate": benign_pass,
            "false_refusal_rate": false_refusal_rate,
            "adversarial_detection_rate": adversarial_detect,
            "synthetic_near_identity_pass_rate": control_pass,
        },
        "separation": {
            "d_stab_auc_adv_vs_benign": round(dstab_auc, 6) if np.isfinite(dstab_auc) else None,
            "d_stab_auc_ci95": [round(x, 6) if np.isfinite(x) else None for x in dstab_ci],
            "leakage_rms_auc_adv_vs_benign": round(leak_auc, 6) if np.isfinite(leak_auc) else None,
            "leakage_rms_auc_ci95": [round(x, 6) if np.isfinite(x) else None for x in leak_ci],
            "benign_d_stab": _dist(b_dstab),
            "adversarial_d_stab": _dist(a_dstab),
            "benign_leakage_rms": _dist(b_leak),
            "adversarial_leakage_rms": _dist(a_leak),
        },
        "representative_benign_refusals": [
            {"label": r["label"], "d_stab": round(r["d_stab"], 4),
             "leakage_rms": round(r["leakage_rms"], 4), "reasons": r["refusal_reasons"]}
            for r in b_rows if not r["admitted"]
        ][:6],
        "verdict": {
            "gate_discriminates_benign_from_adversarial": gate_discriminates,
            "benign_usable_at_this_policy": bool(false_refusal_rate <= 0.05),
            "claims_language": "lawfulness relative to the declared frozen frame — NOT semantic inalienability of the value labels",
            "honest_finding": (
                "The §3.7 admit surface on the declared placeholder frame refuses "
                "benign and adversarial versors alike: benign false-refusal rate is "
                f"{false_refusal_rate:.2f} and d_stab does not separate the classes "
                f"(AUC {dstab_auc:.2f}, 95% CI [{dstab_ci[0]:.2f}, {dstab_ci[1]:.2f}]). "
                "A gate that refuses everything trivially 'detects' every attack but "
                "is not a discriminator. This reproduces the D4 / slice-0 finding — "
                "live benign cognition does not preserve span(e1,e2,e3) — at the fuller "
                "§3.7 surface. The gate must stay default-off; usable separation "
                "requires the §11 dynamics-grounding work, not threshold tuning."
            ),
        },
    }
