# ADR-0246 Acceptance Packet — Induced Identity Action and Path Integrity

**Date:** 2026-07-17
**ADR:** `docs/adr/ADR-0246-induced-identity-action-and-path-integrity.md` (**Accepted**)
**Preflight:** `docs/briefs/ADR-0246-induced-identity-action-and-path-integrity-preflight.md`
**Provenance chain:** Fable 5 (slice-0 diagnostic; §3 primitives; §3.4/3.5 ledger; §6.1/6.2 suites; completion pass) → Opus 4.8 (adversarial audit VERDICT PASS — bit-exact math re-derivation; F1 finding; §3.7 surface + serve wiring; §6.3 discrimination) → Sonnet 5/Fable 5 (§4.1/§4.2 telemetry; §3.4-step-2 `admitted` gate; path serve integration; §11 feasibility study). No self-Accept at any stage.

---

## 1. Scope of what is being put to ruling

Accepting this ADR accepts: the §3 primitives and their pinned blade map; the
locked `H_id={I}` stabilizer; the **`‖·‖_G = ‖G^{1/2}MG^{-1/2}‖_F` norm
convention**; the **F1 composition semantics** (lawful turns compose their raw
*certified* action, never a literal `I`); the **admitted-gate** on composition
(§3.4 step 2); **hard-break turn ownership = new chain**; the §3.7
admit-or-abstain surface; the flag-gated serve wiring (default-off,
byte-identical off); and the §4.1/§4.2 telemetry contracts.

It does **NOT** accept or authorize: live activation of `identity_wave_gate`
or `identity_action_surface` (both stay default-off; the D4 ratified
limitation carries over); any calibration of the placeholder thresholds; any
semantic claim about the value labels ("lawfulness relative to the declared
frozen frame" only); any `H_id` enlargement or geometric corrector.

## 2. §10 acceptance criteria — status

| # | Criterion | Status |
|---|---|---|
| 1 | §6 synthetic + path suites green; discrimination report attached | ✅ 14/14 eval cases; §6.3 + §11 artifacts under `docs/audit/artifacts/` |
| 2 | `H_id={I}` enforced, no silent enlargement | ✅ singleton hardcoded; no enlargement path; grep-audited + pinned |
| 3 | Lawful-only composition proven by tests that fail if raw product used | ✅ `test_lawful_path_equals_lawful_subproduct_not_raw`, `test_raw_product_differs_from_lawful`, §3.4-step-2 pin |
| 4 | Ledger hard-breaks on pack/geometry/policy/session change | ✅ parametrized over every scope dimension |
| 5 | Flag-off serve path byte-identical | ✅ egress/action-record/path tests + all D4 gate surfaces green unchanged + smoke |
| 6 | No geometric `C_id`; admit-or-abstain only | ✅ no corrector exists; refusal folds into the existing `would_violate` egress |
| 7 | Typed residual channels pinned to explicit blade indices | ✅ e4=idx 4, e5=idx 5, spatial=idx 1/2/3; pinned vs `algebra.cl41` |
| 8 | Smoke + relevant lanes local-first; `[Verification]` on commits | ✅ every commit in the stack; final run log `docs/audit/artifacts/adr-0246-slice1-complete-runlog.txt` |
| 9 | Claims language: lawfulness-relative-to-frame, never semantic inalienability | ✅ binding in ADR §1; enforced in report code + tests |
| 10 | Explicit human ratification for status flip | ⏳ THIS PACKET — §8 below |

## 3. Verification summary (see run log for actual output)

- §6.1/§6.2 eval harness: **14/14** `all_passed=True`.
- ADR-0246 test suites (induced-action incl. spatial-foreign resolution,
  path-ledger incl. raw-sneak + admitted-gate, geometric suite, admission +
  honest-verdict pins, egress wiring, action-record §4.1, path serve
  integration, grounding feasibility, mismatch diagnostic): **all green**.
- Adjacent D4 identity surfaces + telemetry suites: **green unchanged**
  (serve byte-identity).
- `uv run core test --suite smoke -q`: **green** (appended to run log).

## 4. The honest §6.3 discrimination numbers (binding)

Benign pass **0.00** · false refusal **1.00** · adversarial detect 1.00 ·
near-identity control pass **1.00** · `d_stab` AUC **0.375** [0.15, 0.62] —
benign cognition sits ~18× farther from the declared frame than crafted
attacks. The gate mechanism is sound; the frame is not what live cognition
preserves. A refuse-everything gate is not a discriminator; activation stays
unauthorized.

## 5. The §11 grounding-feasibility verdict (binding, verbatim from the artifact)

> NULL (n_train=13, n_held_out=12): the top-2 generator-proxy subspace found
> on TRAIN does NOT reliably reproduce on the independently-collected HELD-OUT
> cohort — cosine similarity 0.52 sits at only the 87th percentile of what two
> INDEPENDENT pure-noise cohorts of the same size produce by chance (need >=
> 95th) and/or does not clear the discrimination bar (AUC 0.49, 95% CI [0.21,
> 0.77]). This is consistent with — and sharpens — the D4/slice-0/§6.3 finding
> at the GENERATOR level (not just the induced-action level): benign cognition
> does not have a small, stable, cohort-independent generator subspace
> detectable at this sample size. Threshold tuning on the current pack cannot
> produce a discriminating gate; this feasibility study does not find grounds
> to draft a revised ADR-0246 implementation contract. A much larger cohort
> (this study used n<=13 per real cohort) would be needed to rule out a real
> but subtle effect, rather than to overturn this null.

Method validated by sample-size-calibrated controls: shared-basis positive
pair recovers at cosine 0.9995 (100th percentile of the null; null p95 0.60 at
n=12). Precision transport immaterial (6.9e-7).

## 6. Rulings requested alongside Proposed→Accepted

1. `‖·‖_G` convention (ADR §2.2).
2. F1 composition semantics + admitted-gate reading of §3.4 (ADR §2.4).
3. Hard-break turn ownership = new chain (ADR §2.4).
4. The refusal_reason multi-condition widening (ADR §2.8).

## 7. Operational limitation carried forward

`identity_wave_gate` AND `identity_action_surface` remain **default-off / live
activation NOT authorized**. Activation prerequisites (all required): a
positive, held-out-stable, safety-relevant grounding result at adequate sample
size; calibrated ε/τ/s certificates; renewed discrimination evidence with
acceptable benign refusal; explicit human ratification.

## 8. RULING RECORD

**ACCEPTED**

| Field | Value |
|---|---|
| Ruling | Accepted |
| By | Antigravity (Authorized by Joshua Shay) |
| Date | 2026-07-18 |
| Notes | Authorized by user via prompt. Rulings requested in §6 all approved: ‖·‖_G convention (ADR §2.2); F1 composition semantics + admitted-gate reading of §3.4 (ADR §2.4); Hard-break turn ownership = new chain (ADR §2.4); The refusal_reason multi-condition widening (ADR §2.8). |
