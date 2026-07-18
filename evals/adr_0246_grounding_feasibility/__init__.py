"""ADR-0246 §11 grounding-feasibility study (research, off-serving, evidence-only).

The brief's §11 defers "semantic axis grounding" as a later workstream because
"instruments ≠ meaning." Slice 0 and the §6.3 discrimination report both showed
that NO fixed spatial 3-frame (declared or random) is dynamically preserved by
benign cognition. This study asks the prior, narrower, and answerable question:

    Does *any* held-out-stable, low-dimensional structure exist in what the
    live versor's generator actually does — independent of which frame we
    declare — and if so, does it discriminate benign traffic from adversarial
    geometric attacks?

This is explicitly a FEASIBILITY STUDY, not an implementation. Per the Opus
handoff (§4c item 4) it is "the only path to a gate that discriminates"; the
brief's own instruction (research-question authority, not this module) is that
only a positive, held-out-stable, safety-relevant finding here would justify
drafting a revised ADR-0246 implementation contract. This module does not
draft one — it reports what the data shows, honestly, including a null result.

**Method (fixed cohort splits, no resampling of the same pool):**

  * TRAIN  — benign versors from ``LIVE_PROBE_SEQUENCE`` (D4 Phase 3 / slice-0's
    pinned probe set), n≈13.
  * HELD-OUT — versors from ``PARAPHRASE_PROBE_SEQUENCE`` (independently worded,
    same semantic register), n≈12. A genuine generalization test: any structure
    found on TRAIN must ALSO appear on HELD-OUT, not merely be re-discovered by
    refitting the same pool.
  * ADVERSARIAL — the existing crafted geometric-attack cohort (tilts, boosts,
    inversions, permutations), n=8, reused from ``evals.adr_0246_discrimination``.

**Generator proxy (no scipy; numpy-only per the routing instruction).** Rather
than a matrix logarithm, this study uses the versor's own GRADE-2 (bivector)
coefficient vector (Cl(4,1) indices 6..15, 10 dims) as the generator proxy: for
a versor close to a simple exponential ``F = exp(B/2)``, the bivector block of
``F`` is proportional to ``B`` to leading order, and it is EXACT for the single-
plane simple rotors/boosts used throughout D4/ADR-0246 (this is the same
quantity ``versor_plane_occupancy`` already groups by plane in the slice-0
diagnostic). This is an approximation for compound multi-generator turns and is
documented as such — not a claim of an exact Lie-algebra recovery.

**Honesty constraint (same as §6.3):** with n≈13 samples in a 10-dimensional
proxy space, a covariance fit on TRAIN alone is not evidence of structure —
almost any small sample admits a low-rank-looking in-sample fit purely from
degrees of freedom. The only evidence this study credits is CROSS-COHORT
agreement: does the dominant direction found on TRAIN also explain variance on
the independently-collected HELD-OUT cohort? A held-out-stable finding is
reported only if it does; a null finding is reported plainly otherwise.

Off-serving; deterministic (fixed RNG seed for synthetic controls; live cohorts
via the existing lazy ``chat.runtime`` collectors — never imported by serve).
"""

from __future__ import annotations

from typing import Any, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from evals.adr_0246_discrimination import (
    _auc_bootstrap_ci,
    _roc_auc,
    adversarial_cohort,
)
from evals.adr_0246_mismatch_diagnostic import (
    IDX_E12,
    IDX_E13,
    IDX_E14,
    IDX_E15,
    IDX_E23,
    IDX_E24,
    IDX_E25,
    IDX_E34,
    IDX_E35,
    IDX_E45,
    PARAPHRASE_PROBE_SEQUENCE,
    collect_live_versors,
)
from evals.adr_0244_gamma_calibration import LIVE_PROBE_SEQUENCE

# Bivector (grade-2) block: 10 planes, indices 6..15 in the 32-component layout.
BIVECTOR_INDICES: tuple[int, ...] = (
    IDX_E12, IDX_E13, IDX_E14, IDX_E15, IDX_E23, IDX_E24, IDX_E25, IDX_E34,
    IDX_E35, IDX_E45,
)
BIVECTOR_DIM = len(BIVECTOR_INDICES)  # 10
_PLANE_NAMES = ("e12", "e13", "e14", "e15", "e23", "e24", "e25", "e34", "e35", "e45")

RECOVERY_CONTROL_SEED = 20260717
POSITIVE_CONTROL_TRUE_RANK = 2
POSITIVE_CONTROL_NOISE_SIGMA = 0.03
N_NULL_TRIALS = 200
# "Held-out stable" requires the real train-vs-held-out cross-cohort cosine to
# exceed this percentile of the SAME-SAMPLE-SIZE null distribution (two
# independent pure-noise cohorts) — i.e. p < 0.05 one-sided that the observed
# agreement arose by chance alone — AND the discrimination AUC-CI lower bound
# to clear chance (reusing evals.adr_0246_discrimination's own 0.6 bar).
HELD_OUT_STABILITY_NULL_PERCENTILE_FLOOR = 0.95
DISCRIMINATION_AUC_CI_FLOOR = 0.6


def bivector_coefficients(versor: np.ndarray) -> np.ndarray:
    """The 10-dim bivector-block generator proxy of a versor (Cl(4,1) indices 6..15)."""
    versor = np.asarray(versor, dtype=np.float64)
    return np.array([versor[i] for i in BIVECTOR_INDICES], dtype=np.float64)


def bivector_covariance(versors: Sequence[np.ndarray]) -> np.ndarray:
    """Sample covariance of the bivector-proxy vectors (numpy-only, no scipy)."""
    coeffs = np.array([bivector_coefficients(v) for v in versors], dtype=np.float64)
    if coeffs.shape[0] < 2:
        raise ValueError("covariance requires at least 2 samples")
    return np.cov(coeffs, rowvar=False)


def principal_directions(cov: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Eigenvalues (descending) and eigenvectors of a covariance matrix via
    ``np.linalg.eigh`` (exact for real-symmetric; no scipy dependency)."""
    eigvals, eigvecs = np.linalg.eigh(cov)
    order = np.argsort(eigvals)[::-1]
    return eigvals[order], eigvecs[:, order]


def variance_explained(eigvals: np.ndarray, k: int) -> float:
    total = float(np.sum(eigvals))
    if total <= 0.0:
        return 0.0
    return float(np.sum(eigvals[:k])) / total


def subspace_residual_fraction(vec: np.ndarray, top_eigvecs: np.ndarray) -> float:
    """Fraction of ``vec``'s energy OUTSIDE span(top_eigvecs) — 0 = fully inside."""
    total = float(np.dot(vec, vec))
    if total <= 0.0:
        return 0.0
    projection = top_eigvecs @ (top_eigvecs.T @ vec)
    residual = vec - projection
    return float(np.dot(residual, residual)) / total


def cross_cohort_top_pc_cosine_similarity(
    train_versors: Sequence[np.ndarray], test_versors: Sequence[np.ndarray], *, k: int = 1
) -> float:
    """|cosine similarity| between the top-``k`` principal directions of two
    INDEPENDENTLY collected cohorts — the actual generalization signal.

    A high value means the dominant generator direction found on one cohort
    also explains the other's covariance structure (real, cohort-independent
    structure). A value near 0 means the two cohorts' dominant directions are
    unrelated (no stable structure — matches the D4/slice-0 finding at the
    generator level rather than the induced-action level).
    """
    _, train_vecs = principal_directions(bivector_covariance(train_versors))
    _, test_vecs = principal_directions(bivector_covariance(test_versors))
    # top-k subspace overlap via singular values of the k x k Gram of top directions
    a = train_vecs[:, :k]
    b = test_vecs[:, :k]
    overlap = a.T @ b
    if k == 1:
        return float(abs(overlap[0, 0]))
    singular_values = np.linalg.svd(overlap, compute_uv=False)
    return float(np.mean(singular_values))  # mean principal angle cosine


# --- synthetic recovery controls ------------------------------------------------


def synthetic_recovery_positive_cohort(
    rng: np.random.Generator, n: int, basis: np.ndarray | None = None
) -> list[np.ndarray]:
    """POSITIVE control: bivector coefficients confined to a low-rank subspace
    + small noise.

    ``basis`` is the true subspace. Pass the SAME basis to generate two
    independent cohorts sharing one true structure (the cross-cohort recovery
    control); omitting it draws a fresh random subspace — two cohorts built
    with separate fresh bases share NOTHING and must never be compared as a
    positive pair (that was a real bug caught RED in the test suite: the
    "positive" pair scored 0.53, indistinguishable from noise, because each
    call invented its own subspace).
    """
    if basis is None:
        basis = np.linalg.qr(
            rng.standard_normal((BIVECTOR_DIM, POSITIVE_CONTROL_TRUE_RANK))
        )[0]
    coeffs = []
    for _ in range(n):
        weights = rng.standard_normal(POSITIVE_CONTROL_TRUE_RANK)
        vec = basis @ weights + POSITIVE_CONTROL_NOISE_SIGMA * rng.standard_normal(BIVECTOR_DIM)
        coeffs.append(_embed_bivector(vec))
    return coeffs


def synthetic_recovery_negative_cohort(
    rng: np.random.Generator, n: int
) -> list[np.ndarray]:
    """NEGATIVE control: isotropic random bivector coefficients (no structure).
    The eigen-analysis MUST NOT report a dominant low-rank subspace — a false
    positive here would mean the method hallucinates structure from noise."""
    coeffs = [
        _embed_bivector(rng.standard_normal(BIVECTOR_DIM)) for _ in range(n)
    ]
    return coeffs


def _embed_bivector(bivector_coeffs: np.ndarray) -> np.ndarray:
    """Embed a 10-dim bivector-coefficient vector into a full 32-dim versor-shaped
    array (scalar part fixed at 1.0) purely so it round-trips through
    ``bivector_coefficients`` identically — these are SYNTHETIC generator-proxy
    vectors for the recovery controls, not claims of being valid versors."""
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    for idx, coeff in zip(BIVECTOR_INDICES, bivector_coeffs):
        v[idx] = coeff
    return v


def null_cross_cohort_cosine_distribution(
    n: int, *, n_trials: int = N_NULL_TRIALS, seed: int = RECOVERY_CONTROL_SEED, k: int = 2
) -> np.ndarray:
    """The NULL distribution of ``cross_cohort_top_pc_cosine_similarity`` between
    two INDEPENDENT isotropic-noise (no-true-structure) cohorts of size ``n`` —
    calibrated to the ACTUAL sample size under study, not a generic asymptotic
    threshold.

    This matters because at small ``n`` (comparable to the 10-dim generator-proxy
    space), a sample covariance from PURE NOISE still shows an inflated top-k
    "variance explained" from finite-sample fluctuation alone (verified
    empirically: at n=20 an isotropic negative control showed ~0.44, not the
    asymptotic 0.20 chance level for k=2/10). Comparing a real result against a
    fixed threshold derived from large-sample asymptotics would be dishonestly
    optimistic. Instead every real finding here is judged against a null
    distribution generated at the SAME ``n``.
    """
    rng = np.random.default_rng(seed)
    cosines = np.empty(n_trials, dtype=np.float64)
    for i in range(n_trials):
        cohort_a = synthetic_recovery_negative_cohort(rng, n)
        cohort_b = synthetic_recovery_negative_cohort(rng, n)
        cosines[i] = cross_cohort_top_pc_cosine_similarity(cohort_a, cohort_b, k=k)
    return cosines


def empirical_percentile(value: float, null_distribution: np.ndarray) -> float:
    """Fraction of the null distribution at or below ``value`` — a one-sided
    empirical p-value complement (0.95 ⇒ value exceeds 95% of pure-noise draws
    at the same sample size, i.e. p < 0.05 one-sided)."""
    return float(np.mean(null_distribution <= value))


def run_recovery_controls(
    n: int, *, seed: int = RECOVERY_CONTROL_SEED, n_trials: int = N_NULL_TRIALS
) -> dict[str, Any]:
    """Sample-size-calibrated recovery sanity check (see module docstring).

    Two independent cohorts drawn from the SAME true rank-2 subspace (+ noise)
    at size ``n`` each MUST show high cross-cohort cosine similarity, and that
    similarity must clear the NULL distribution (two independent noise cohorts
    at the same ``n``) — confirming the method can detect real shared structure
    at this exact sample size, not merely at a generously large one.
    """
    rng = np.random.default_rng(seed)
    # ONE shared true subspace; two INDEPENDENT cohorts drawn from it.
    shared_basis = np.linalg.qr(
        rng.standard_normal((BIVECTOR_DIM, POSITIVE_CONTROL_TRUE_RANK))
    )[0]
    positive_a = synthetic_recovery_positive_cohort(rng, n, basis=shared_basis)
    positive_b = synthetic_recovery_positive_cohort(rng, n, basis=shared_basis)
    positive_cosine = cross_cohort_top_pc_cosine_similarity(
        positive_a, positive_b, k=POSITIVE_CONTROL_TRUE_RANK
    )
    null_dist = null_cross_cohort_cosine_distribution(
        n, n_trials=n_trials, seed=seed + 1, k=POSITIVE_CONTROL_TRUE_RANK
    )
    positive_percentile = empirical_percentile(positive_cosine, null_dist)
    return {
        "sample_size": n,
        "positive_control_cross_cohort_cosine": round(positive_cosine, 6),
        "null_distribution": {
            "n_trials": n_trials,
            "mean": round(float(np.mean(null_dist)), 6),
            "p50": round(float(np.percentile(null_dist, 50)), 6),
            "p95": round(float(np.percentile(null_dist, 95)), 6),
        },
        "positive_control_percentile_in_null": round(positive_percentile, 6),
        "method_recovers_true_structure": bool(positive_percentile > 0.95),
    }


# --- precision pairs -------------------------------------------------------------


def precision_pair_delta(versor: np.ndarray) -> float:
    """Max abs delta of the bivector-proxy coefficients under an f64->f32->f64
    round-trip of the whole versor (same style as the slice-0 transport probe)."""
    versor64 = np.asarray(versor, dtype=np.float64)
    versor_roundtrip = versor64.astype(np.float32).astype(np.float64)
    return float(
        np.max(
            np.abs(bivector_coefficients(versor64) - bivector_coefficients(versor_roundtrip))
        )
    )


# --- plane occupancy (typed e4/e5 generator analysis) ---------------------------


def mean_plane_energy_fractions(versors: Sequence[np.ndarray]) -> dict[str, float]:
    """Mean fraction of bivector energy in each of the 10 individual planes,
    across a cohort — the "typed e4/e5 generator analysis": does the generator
    concentrate in specific e4/e5-mixing planes, or spread evenly?"""
    fractions = np.zeros(BIVECTOR_DIM, dtype=np.float64)
    for versor in versors:
        coeffs = bivector_coefficients(versor)
        total = float(np.dot(coeffs, coeffs))
        if total > 0.0:
            fractions += (coeffs ** 2) / total
    fractions /= max(len(versors), 1)
    return {name: round(float(f), 6) for name, f in zip(_PLANE_NAMES, fractions)}


# --- cohort collection -----------------------------------------------------------


def collect_train_cohort() -> list[np.ndarray]:
    """TRAIN: benign versors from the D4/slice-0 pinned probe sequence."""
    return [v for _, v in collect_live_versors(LIVE_PROBE_SEQUENCE)]


def collect_held_out_cohort() -> list[np.ndarray]:
    """HELD-OUT: independently-worded paraphrase versors (genuine generalization test)."""
    return [v for _, v in collect_live_versors(PARAPHRASE_PROBE_SEQUENCE)]


def collect_adversarial_cohort() -> list[np.ndarray]:
    """The existing crafted geometric-attack cohort, reused for consistency."""
    return [v for _, v in adversarial_cohort()]


# --- full study -------------------------------------------------------------------


def build_feasibility_report(
    train: Sequence[np.ndarray] | None = None,
    held_out: Sequence[np.ndarray] | None = None,
    adversarial: Sequence[np.ndarray] | None = None,
) -> dict[str, Any]:
    """Run the full §11 feasibility study and report an honest verdict.

    ``train``/``held_out``/``adversarial`` default to the live/synthetic cohorts
    described in the module docstring; pass explicit cohorts for a fast/offline
    run (as the test suite does).
    """
    train = list(train) if train is not None else collect_train_cohort()
    held_out = list(held_out) if held_out is not None else collect_held_out_cohort()
    adversarial = list(adversarial) if adversarial is not None else collect_adversarial_cohort()

    # Null calibration uses the SMALLER of the two real cohort sizes — the more
    # conservative (harder-to-clear) choice when the sizes differ.
    calibration_n = max(min(len(train), len(held_out)), 3)
    recovery = run_recovery_controls(calibration_n)

    train_eigvals, train_eigvecs = principal_directions(bivector_covariance(train))
    held_out_eigvals, _ = principal_directions(bivector_covariance(held_out))
    top_k = 2
    cross_cohort_cosine = cross_cohort_top_pc_cosine_similarity(train, held_out, k=top_k)
    null_dist = null_cross_cohort_cosine_distribution(calibration_n, k=top_k)
    real_percentile = empirical_percentile(cross_cohort_cosine, null_dist)

    top_eigvecs = train_eigvecs[:, :top_k]
    train_residuals = [subspace_residual_fraction(bivector_coefficients(v), top_eigvecs) for v in train]
    held_out_residuals = [subspace_residual_fraction(bivector_coefficients(v), top_eigvecs) for v in held_out]
    adversarial_residuals = [subspace_residual_fraction(bivector_coefficients(v), top_eigvecs) for v in adversarial]

    auc = _roc_auc(adversarial_residuals, held_out_residuals)
    auc_ci = _auc_bootstrap_ci(adversarial_residuals, held_out_residuals)

    precision_deltas = [precision_pair_delta(v) for v in train + held_out]
    plane_energy_train = mean_plane_energy_fractions(train)
    plane_energy_held_out = mean_plane_energy_fractions(held_out)

    held_out_stable = bool(
        real_percentile >= HELD_OUT_STABILITY_NULL_PERCENTILE_FLOOR
        and np.isfinite(auc_ci[0])
        and auc_ci[0] > DISCRIMINATION_AUC_CI_FLOOR
    )

    report = {
        "schema_version": "adr_0246_grounding_feasibility_v1",
        "method": {
            "generator_proxy": "bivector (grade-2) coefficient block, 10 planes",
            "note": "approximates the Lie generator to first order; exact for "
                    "single-plane simple rotors/boosts, approximate for compound "
                    "multi-generator turns; no scipy / matrix-log dependency",
        },
        "cohorts": {"train_n": len(train), "held_out_n": len(held_out), "adversarial_n": len(adversarial)},
        "null_calibration_sample_size": calibration_n,
        "recovery_controls": recovery,
        "train_eigenvalues": [round(float(x), 6) for x in train_eigvals],
        "held_out_eigenvalues": [round(float(x), 6) for x in held_out_eigvals],
        "train_variance_explained_top_2": round(variance_explained(train_eigvals, top_k), 6),
        "held_out_variance_explained_top_2": round(variance_explained(held_out_eigvals, top_k), 6),
        "cross_cohort_top2_cosine_similarity": round(cross_cohort_cosine, 6),
        "cross_cohort_cosine_null_distribution": {
            "n_trials": N_NULL_TRIALS,
            "mean": round(float(np.mean(null_dist)), 6),
            "p95": round(float(np.percentile(null_dist, 95)), 6),
        },
        "cross_cohort_cosine_percentile_in_null": round(real_percentile, 6),
        "held_out_stability_null_percentile_floor": HELD_OUT_STABILITY_NULL_PERCENTILE_FLOOR,
        "residual_from_train_top2_subspace": {
            "train": {"mean": round(float(np.mean(train_residuals)), 6)},
            "held_out": {"mean": round(float(np.mean(held_out_residuals)), 6)},
            "adversarial": {"mean": round(float(np.mean(adversarial_residuals)), 6)},
        },
        "discrimination_auc_adversarial_vs_heldout": round(auc, 6) if np.isfinite(auc) else None,
        "discrimination_auc_ci95": [
            round(x, 6) if np.isfinite(x) else None for x in auc_ci
        ],
        "precision_transport": {
            "max_bivector_delta": round(max(precision_deltas), 9) if precision_deltas else 0.0,
            "significant": bool(precision_deltas and max(precision_deltas) > 1e-4),
        },
        "plane_energy_fractions": {"train": plane_energy_train, "held_out": plane_energy_held_out},
        "verdict": {
            "recovery_method_validated": bool(recovery["method_recovers_true_structure"]),
            "held_out_stable_structure_found": held_out_stable,
            "safety_relevant": bool(held_out_stable and auc > 0.5),
        },
    }
    report["verdict"]["honest_finding"] = _honest_finding(report)
    return report


def _honest_finding(report: dict[str, Any]) -> str:
    v = report["verdict"]
    cos = report["cross_cohort_top2_cosine_similarity"]
    pct = report["cross_cohort_cosine_percentile_in_null"]
    auc = report["discrimination_auc_adversarial_vs_heldout"]
    ci = report["discrimination_auc_ci95"]
    n = report["cohorts"]
    if not v["recovery_method_validated"]:
        return (
            "INCONCLUSIVE: the recovery-control sanity check failed — at this "
            "sample size the method cannot reliably distinguish a real shared "
            "structure from chance agreement between two noise cohorts, "
            "independent of the real cohorts' outcome. Do not draw a conclusion "
            "from the real-cohort numbers below."
        )
    if v["held_out_stable_structure_found"]:
        return (
            f"POSITIVE (n_train={n['train_n']}, n_held_out={n['held_out_n']}): the "
            f"top-2 generator-proxy subspace found on TRAIN cosine-agrees with the "
            f"independently-collected HELD-OUT cohort at {cos:.2f} — the "
            f"{pct * 100:.0f}th percentile of the SAME-SAMPLE-SIZE null distribution "
            f"(two independent pure-noise cohorts), i.e. this agreement is unlikely "
            f"to have arisen by chance alone. It also discriminates the adversarial "
            f"cohort from held-out benign at AUC {auc:.2f} (95% CI [{ci[0]:.2f}, "
            f"{ci[1]:.2f}], clears chance). This is evidence — NOT proof at this "
            f"sample size — that a held-out-stable, safety-relevant structure may "
            f"exist. A larger, pre-registered cohort study is required before "
            f"drafting an ADR-0246 implementation contract on this basis."
        )
    return (
        f"NULL (n_train={n['train_n']}, n_held_out={n['held_out_n']}): the top-2 "
        f"generator-proxy subspace found on TRAIN does NOT reliably reproduce on "
        f"the independently-collected HELD-OUT cohort — cosine similarity {cos:.2f} "
        f"sits at only the {pct * 100:.0f}th percentile of what two INDEPENDENT "
        f"pure-noise cohorts of the same size produce by chance (need >= 95th) "
        f"and/or does not clear the discrimination bar (AUC {auc:.2f}, 95% CI "
        f"[{ci[0]:.2f}, {ci[1]:.2f}]). This is consistent with — and sharpens — the "
        f"D4/slice-0/§6.3 finding at the GENERATOR level (not just the induced-action "
        f"level): benign cognition does not have a small, stable, cohort-independent "
        f"generator subspace detectable at this sample size. Threshold tuning on the "
        f"current pack cannot produce a discriminating gate; this feasibility study "
        f"does not find grounds to draft a revised ADR-0246 implementation contract. "
        f"A much larger cohort (this study used n<=13 per real cohort) would be "
        f"needed to rule out a real but subtle effect, rather than to overturn this null."
    )
