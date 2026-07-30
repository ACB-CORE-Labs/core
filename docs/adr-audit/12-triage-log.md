# Tier C — Rapid Triage Log

One row per Tier C ADR (true singletons, non-ADR scope/session docs, `docs/decisions/` redirects). Automated cross-reference (file existence + a spot-check) rather than a full 7-axis card — promoted to Tier B if a check below turns up something contradictory or orphaned. Per batch, appended below.

## Batch 1 (ADR-0043–0045)

### ADR-0043 — Phase-2 pack measurements: claims → numbers

**Verified against:** `main` @ `cbfc8ccb`. All 5 claimed artifacts exist on disk: `evals/identity_divergence/pack_runner.py`, `evals/refusal_calibration/pack_runner.py`, `scripts/publish_pack_measurements.py`, `tests/test_pack_measurements_phase2.py`, `evals/results/phase2_pack_measurements.json`. **Not run** (would require `PYTHONPATH=. python3 -m pytest tests/test_pack_measurements_phase2.py -q` — deferred to a future batch pass that actually executes suites; this triage is existence-only, per Tier C scope). **Disposition:** built, not orphaned, no action. **Build:** full (by existence) — pending execution confirmation. **Necessity/generality:** not assessed at Tier C depth.

### ADR-0044 — Medical / clinical ethics pack (worked-example domain pack)

**Verified against:** `main` @ `cbfc8ccb`. All 4 claimed artifacts exist: `packs/ethics/medical_clinical_ethics_v1.json`, `packs/ethics/medical_clinical_ethics_v1.mastery_report.json`, `scripts/ratify_ethics_pack.py`, `tests/test_medical_clinical_ethics_pack.py`. **Not run.** **Disposition:** built, not orphaned, no action. This is a worked-example domain pack (single instance, not a mechanism) — correctly scoped as Tier C, not a candidate for promotion.

### ADR-0045 — Long-context recall: CORE vs transformer baselines

**Verified against:** `main` @ `cbfc8ccb`. All 3 claimed artifacts exist: `evals/long_context_cost/comparison_runner.py`, `evals/long_context_cost/baselines/transformer_long_context.json`, `tests/test_long_context_comparison.py`. **Not run.**

**Finding `AA-159` (🟢 Monitor, cheap to fix):** ADR-0045's "Related" section links `[ADR-0001](ADR-0001-deterministic-cognitive-engine.md)` — this file does not exist. The actual ADR-0001 file is `docs/adr/ADR-0001-vocab-layer-invariants.md` ("VocabManifold Versor Invariant"). Checked `docs/census/<sha>/stale-references.jsonl` (the mechanical dead-reference sweep pinned at the same SHA) — it does **not** catch this, so this is a genuinely new finding from this audit, not a duplicate; the census sweep appears scoped to code references rather than markdown-to-markdown ADR links. No other file in `docs/adr/` references this broken filename (checked via `grep -rl`), so this is an isolated, single-site drift, not a corpus-wide pattern — low blast radius, one-line fix (correct the filename in the link target; the ADR number `0001` itself is plausibly still the intended target, since versor-invariant enforcement is a precondition for the exact-recall guarantee this ADR discusses, but that thematic connection was not independently re-verified here).

**Disposition:** built, not orphaned, one findable low-severity record/reality divergence (a broken doc-to-doc link). Logged as `AA-159`, routed to the finding register at rollup.

## Batch 2 (ADR-0078 variant)

### ADR-0078 — Phase 1 — Pre-Implementation Planning Note (audit ID `0078~2`, filename `ADR-0078-phase1-implementation-note.md`)

**Verified against:** `main` @ `cbfc8ccb`. Not a ratified decision record — no Status field, no Decision/Consequences section; it is a 6-point pre-implementation scoping memo (composer-atom provenance sourcing, telemetry hook placement, why register variation shouldn't perturb atom hashes, why anchor-lens engagement legitimately can). Correctly excluded from Tier A/B — it documents *intent* for what became the real ADR-0078 (`ADR-0078-composer-graph-atom-equivalence.md`, audited at Tier B in `11-adr-cards/B2.2-cognition-lane-correction-telemetry.md`). **Disposition:** in-scope as context for its Tier-B sibling, not independently scored. No action.

## Batch 3 (ADR-0101–0150)

### ADR-0127~1 — ADR-0127 + ADR-0128 Results (`ADR-0127-0128-RESULTS.md`)

**Verified against:** `main` @ `cbfc8ccb`. Empirical results companion document recording GSM8K-math arc results. **Disposition:** in-scope context / results document, not a decision record. No action.

### ADR-0129 — Spaced Reviewed-Correction Replay (Deferred Proposal)

**Verified against:** `main` @ `cbfc8ccb`. Document status: `Proposed — Deferred`. Backlog proposal for spaced reviewed-correction replay; no runtime code or test suite landed. **Disposition:** deferred proposal, no code, no action.

### ADR-0130 — Pre-Articulation Calibration Logging (Deferred Proposal)

**Verified against:** `main` @ `cbfc8ccb`. Document status: `Proposed — Deferred`. Backlog proposal for pre-articulation calibration logging; no runtime code or test suite landed. **Disposition:** deferred proposal, no code, no action.

## Batch 4 (ADR-0151–0200)

### ADR-0163 — F2 Confuser Corpus Specification (`ADR-0163-F2-confuser-corpus-spec.md`)

**Verified against:** `main` @ `cbfc8ccb`. Specification document defining a discrimination probe for candidate parsers. **Disposition:** spec-only probe design, no standalone runtime module. No action.

### ADR-0163-gsm8k — Path to GSM8K Mastery (`ADR-0163-gsm8k-path-to-mastery.md`)

**Verified against:** `main` @ `cbfc8ccb`. Prescriptive roadmap proposal superseded by ADR-0207 substrate ratification. **Disposition:** superseded roadmap document, no action.


