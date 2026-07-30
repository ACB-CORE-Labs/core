# Batch 6 — Tier A/B Audit (ADR-0251–0265) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct — not a subagent) | **Date:** 2026-07-29
Replaces the retracted `Batch6-TierA-consolidated.md` (see `20-finding-register.md` retraction notice). Reduced-rigor bounds per charter amendment: code/test inspection only, terse cards. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Stack A6.1 — Deduction-Serve Band Family (0256–0261)

**Members:** ADR-0256 (earned license), 0257 (v2-EN clause), 0258 (v3-MEM), 0259 (v4-CM), 0260 (v5-VP), 0261 (v6-EX). Engine: `generate/proof_chain/entail.py` (ROBDD).

**Stack claim:** deduction serving is governed by an *earned* Wilson-floor license (θ_SERVE=0.99, ADR-0175 regime) per shape-band, `wrong=0` preserved.

**Verified:** all six governs-files exist (`chat/deduction_serve_license.py`, `chat/data/deduction_serve_ledger.json`, `generate/proof_chain/{english,categorical,cond_member,verb,exist,entail}.py`). Ledger read directly: 25 classes, `wrong=0` on every row. Wilson lower bounds recomputed independently (z=1.96): EN-clause and two verb classes clear θ=0.99; **all** `en_member_*` (≤0.9398), `en_condmem_*` (≤0.9398), `en_exist_*` (≤0.9229) classes fall below the floor at current n. Matches the assessment's 25→4-ish licensed re-count direction.

**Per-ADR (terse):**
- **0256** — build full / live / irreducible (the license mechanism itself) / continuity clean. License file's own header confirms "engine READS this artifact; never writes it" — no self-promotion path, honoring ADR-0175's "an engine cannot raise its own bar."
- **0257** — build full / live-and-licensed / irreducible / clean.
- **0258, 0259, 0261** — build full / **wired-but-gated** (below Wilson floor at current n — honest, by design, not a defect) / irreducible / clean. `AA-507`.
- **0260** — build full / split (en_verb_fact & _universal licensed at 0.9942; en_verb_chain/_negative at 0.9877 below floor) / irreducible / clean.
- **0261** — additionally carries the number ADR-0253 reserved for the Blueprint's SIMD-holonomy intent — see `AA-508`/`AA-509`.

## Stack A6.2 — Curriculum Serving, Ledger Bridge & Negation (0262–0265)

- **0262** (curriculum-grounded serving) — build full (`chat/curriculum_surface.py`, `chat/curriculum_serve_license.py`, `evals/curriculum_serve/runner.py` all exist) / live / irreducible. Continuity: **exemplary** — its §5 volume conclusion is amended by 0264 §4.1 with explicit bidirectional cross-references (verified in both files and INDEX). `AA-510`.
- **0263** (ratified ledger bridge) — build full (`core/ratified_ledger.py`) / live (extracted from three prior instances — a *completed* consolidation of exactly the kind `22-consolidation-report.md` recommends elsewhere; positive necessity exemplar) / irreducible.
- **0264** (negative curriculum + premise scope) — build full (`teaching/curriculum_premises.py`, ratification, oracle) / live / irreducible. §4.1's `MAX_PREMISE_SENTENCES=16` cap and its "no curriculum band can earn SERVE until scoping lands" blocker verified present, with a later `R5` note at line ~274 engaging §4.1's reasoning — live amendment trail, not silent drift.
- **0265** (negation in the proposition graph) — build full: `GraphNode.negated` at `generate/graph_planner.py:74`, serialized-only-when-True guard at `:102` (preserving `trace_hash` stability exactly as decided) / live / irreducible / clean. Fixes a real truth defect (denial vs. assertion served byte-identical surfaces).

## Stack A6.3 — Governance & Recalibration (0251–0253)

- **0251** (reader-arc halt + reset; §5 spike Proposed) — §§1–4 executed-and-verified per its own status line; **§5 remains "Proposed — awaiting ruling" while the 2026-07-28 Foundations Audit / Perception Arc adjudicated the adjacent hypothesis family** (three prior negatives for relations-as-geometric-operators, ADR-0252 §5 NO-GO among them). The §5 normalization spike is related-but-distinct; its status line is 10 days stale against a moved landscape and needs an explicit disposition or supersession note. `AA-511` 🟡.
- **0252** (problem-solving paradigm) — the corpus's best-maintained record: §5 NO-GO verdict banner, §6 retirement-condition amendment, and the R-12b basis-note correction ("34 organs" → reproducible 18, correction recorded in place rather than rewriting ratified prose) all present in the live text. Liveness: adopted as the governing competence model by the assessment taxonomy (D1). `AA-512` 🟢 (positive exemplar).
- **0253** (blueprint collision + dual-pack boundary) — build full: `tests/test_pack_draft_serve_boundary.py` exists; mapping file linked from `docs/adr/README.md`. Continuity: **stale in one load-bearing clause** — see `AA-508`.

## Tier B pair (0254, 0255)

- **0254** (grounded-open hedge arm) — build full: allowlist literally `frozenset({"versor_condition","goldtether_residual"})` at `core/cognition/surface_resolution.py:50`, wired at `:336`, test exists. Liveness live. §4 **explicitly acknowledges** non-unification with ADR-0038's hedge and defers it — extends consolidation Cluster 5 with a third, *documented* member (contrast B4's finding that the first two never acknowledged each other). `AA-513`.
- **0255** (discovery-yield baseline) — build full: `compute_discovery_yield` in `teaching/discovery_yield.py` + CLI; `turn_count_baseline` (4 references) in `engine_state/__init__.py`; test exists. Fail-closed on missing baseline verified in the decision text and code shape — never fabricates a denominator. Liveness live. Clean. `AA-514`.

## Findings rollup

- **`AA-508` 🟡** — `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` reserves numbers 0254–0261 for eight Blueprint gap-intents ("not materialised until the owning stage implements them," line 59); **all eight numbers have since been minted as unrelated deduction/serving-arc ADRs** and neither the mapping nor ADR-0253 clause 3 ("reserved as ADR-0261 if implemented later") was amended. A reader following the mapping today is misdirected in 8 of 8 reserved rows.
- **`AA-509` 🟢** — Batch 1's `AA-73` risk (SIMD-holonomy hardened under reserved 0261 without a NO-GO note) is dissolved *by accident* — the number is taken — but the BP-0253 holonomy-SIMD intent now has no reserved home and still no NO-GO annotation anywhere; `AA-82`'s requested mapping-row annotation remains owed and is now more urgent, not less.
- **`AA-507` 🟢** — Bands v3-MEM/v4-CM/v6-EX (0258/0259/0261) are built with `wrong=0` but below θ_SERVE=0.99 at current sample sizes (Wilson lower bounds ≤0.9398/≤0.9398/≤0.9229, recomputed independently) — the earned-license regime withholding capability honestly; recorded so nobody mistakes "unlicensed" for "broken."
- **`AA-513` 🟢** — ADR-0254 adds hedge site #3 with an explicit in-text deferral of unification (extends `AA-142`/Cluster 5; the deferral is documented, unlike the 0028/0038 pair's silence).
- **`AA-512` 🟢** — ADR-0252 is the corpus's record-maintenance exemplar (ruled in-place corrections, verdict banners); cite it as the model when drafting the remediation guidance for the ~20 stale-status ADRs found in Batches 1–2.
- **`AA-511` 🟡** — ADR-0251 §5 (geometric-normalization spike) still reads "Proposed — awaiting ruling" while the 2026-07-28 Foundations Audit/Perception Arc adjudicated the adjacent hypothesis family; needs an explicit disposition note either way.
- **`AA-514` 🟢** — ADR-0255 clean; fail-closed baseline discipline verified.
- **`AA-510` 🟢** — ADR-0262↔0264 amendment chain is bidirectional and explicit; clean.

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 6 🟢.** Note against the calibration warning in the charter: this batch is genuinely the corpus's healthiest — 12 of 15 ADRs date from the last 10 days of disciplined, ruling-gated work (the 2026-07-19→28 arc that the assessment itself governed), and 4 of the 8 findings are explicitly *positive* exemplars. The near-zero critical rate here is evidenced (every band's ledger read, every governs-file checked, Wilson bounds recomputed), not assumed — the contrast with the retracted pass is that this one shows its work.
