# Deterministic Relational Operator Ablation — Final Engineering Dossier

**Branch:** `feat/deterministic-relational-operator-ablation`  
**Worktree:** `/Users/kaizenpro/Projects/core-relational-operator-ablation`  
**Date:** 2026-07-19

**Document set on this branch:**

| Doc | Role |
|-----|------|
| `docs/analysis/relational-operator-ablation-cartography-2026-07-19.md` | Phase 1 cartography, design-truth matrix, go/no-go |
| `docs/analysis/relational-operator-ablation-dossier-2026-07-19.md` | This file — ablation implementation + measurement |
| `docs/analysis/hebrew-koine-greek-logos-pack-capability-roadmap-2026-07-19.md` | Separate HE/GRC Logos audit (planning only; no pack build) |

---

## Executive verdict

**IMPLEMENTED AND MEASURED**

Narrow vertical slice only: family `proportional_change.decrease_to_fraction` / organ `fraction_decrease`.  
Ancient-language → GSM8K arithmetic is **not** claimed and is **not** implemented (scientific NO-GO under anti-circularity).

**Depth on English-only cases was intentionally inert** (no observed-morphology basis). That does not test observed Hebrew/Greek input or the broader Logos-pack thesis — see the HE/GRC roadmap for the audited next path (`feat/observed-he-morph-constraint-v0`).

---

## Ground-truth corrections

| Prior claim | Classification | Evidence |
|-------------|----------------|----------|
| EN articulation / HE depth-root / GRC depth-relation | Partially confirmed | ADR-0005/0015; LIVE `packs/data/he_*`, `grc_*`; draft `packs/he\|grc` |
| ADR-0005/0015 architecture | Confirmed | Accepted ADRs; compiler path `packs.compiler._apply_morphology` |
| Source packs draft + morph compiler | Confirmed (split) | Source DISCONNECTED; compiled LIVE |
| Ordered morph composition | Confirmed LIVE | `MorphologyEntry`; tests holonomy/registry |
| depth_canonical / enrich | Confirmed; enrich=decoration | `recognition/depth_canonical.py`; math inert |
| ProblemFrame symbols | Confirmed | `generate/problem_frame*.py` |
| All `serving_allowed=False` | **False** | fraction_decrease **True** in `construction_affordances.py` |
| EN→Greek case/Hebrew binyan math path | **Absent** | No imports in math organs |
| GSM8K all refused | Split-dependent | Sealed **0/0/1319**; train_sample **30/0/20**; holdout_dev **5/0/495** (correct/wrong/refused) |
| FGL / ADR-0248 as Logos | **Absent / miscited** | ADR-0248 = integrity handoffs |
| ADR-0196 ancient packs | **False** | Python/Rust/Zig doctrine |

---

## Architecture map

See `docs/analysis/relational-operator-ablation-cartography-2026-07-19.md`.

Summary:

- **Chat path LIVE**; ProblemFrame **DISCONNECTED** (`contract_assessment=None`).
- **Math serving LIVE** via `parse_and_solve`; Gate A2k uses ProblemFrame + VersorBinding.
- **Depth LIVE** for he/grc recognition; **inert** for English math answers.

---

## Implemented mechanism

| Layer | Mechanism |
|-------|-----------|
| Canonical relation | `BoundRelation(relation_type="decrease_to_fraction")` with roles base_quantity, scale, state_entity, transition, unit |
| Baseline operator | Pure rational `base * (1 - scale)` from grounded frame roles + shared organ hazard refuse gates |
| Geometric operator | Live `resolve_promotable_fraction_decrease` → CGA dilation `VersorBinding` |
| Depth-derived mapping | **None executable** on English; recorded `inactive_no_mapping` with rule id |
| Metadata-only | `assess_contracts(..., depth=)` appends `[root:…]`; must not change answer |
| Provenance | Spans, scale surface, roles, mapping_rule_id, pack ids (empty when inactive) |
| Readback | `RelationReadback` reconstructs roles, scale, missing bindings, versor_error |
| Fail-closed | Missing/hazard/adversarial → refuse; wrong=0 on sealed fixture |

Axioms: geometry-first (CGA dilation), field/structured IR (ProblemFrame), propagation via versor_apply, native integrity (not invented dual-adjoint), reconstruction via readback, compilation-last (no new ontology), reality-over-inheritance (depth inert proven).

---

## Files changed

| Path | Purpose | Key symbols |
|------|---------|-------------|
| `docs/analysis/relational-operator-ablation-cartography-2026-07-19.md` | Evidence ledger + go/no-go | — |
| `docs/analysis/relational-operator-ablation-dossier-2026-07-19.md` | This dossier | — |
| `generate/relational_operator_ablation.py` | Condition runners | `run_baseline`, `run_operator`, `run_depth`, `run_metadata_only`, `run_invalid` |
| `evals/relational_operator_ablation/` | Sealed lane | `v1/cases.jsonl`, `v1/runner.py`, `v1/report.json` |
| `tests/test_relational_operator_ablation.py` | Unit/integration/adversarial proofs | 20 tests |

---

## Proof and test matrix

| Command | Result |
|---------|--------|
| `PYTHONPATH=. python3 -m evals.relational_operator_ablation.v1.runner` | passed; report_sha256 `53df6d17…` |
| `PYTHONPATH=. python3 -m pytest -q tests/test_relational_operator_ablation.py` | **20 passed** |
| `uv run core test --suite smoke -q` | **176 passed** (~132s) |

Key tests:

- baseline rational / operator geometric / metadata inert / depth inactive
- sealed gold correct; adversarial refuse not wrong
- preexisting scale>1 A2k gap isolated (not masked)
- determinism, no input mutation, readback provenance

---

## Ablation results (n=8 sealed)

Order: **correct / wrong / refused**

| Condition | correct | wrong | refused | coverage | Notes |
|-----------|---------|-------|---------|----------|-------|
| baseline | 2 | 0 | 6 | 2/8 | Frame roles + rational math |
| operator | 2 | 0 | 6 | 2/8 | Live VersorBinding path |
| depth | 2 | 0 | 6 | 2/8 | = operator; mapping inactive |
| metadata_only | 2 | 0 | 6 | 2/8 | Root notes present; answers match operator |
| invalid (adversarial subset n=6) | 0 | 0 | 6 | 0/6 | Prefer refuse over wrong |

**Findings:** metadata_only inert ✓; depth inactive equals operator ✓; wrong=0 ✓; deterministic ✓.

**Limitations:** n=8; not GSM8K-wide; depth executable unproven for English; chat spine still disconnected from ProblemFrame; pre-existing A2k scale>1 gap documented separately.

**Scientific conclusion:** Canonical relation operators (baseline scalar vs geometric) agree when both commit; depth **metadata does not improve arithmetic** on this English slice; executable depth mapping was correctly refused as inactive rather than fabricated.

---

## Remaining gaps

| Kind | Item |
|------|------|
| Engineering | Wire ProblemFrame into CognitiveTurnPipeline backpressure |
| Engineering | Unify percent_partition prose organ with frame contracts |
| Engineering | Fix A2k scale>1 admit (pre-existing; isolated test) |
| Scientific | Whether observed he/grc morphology can constrain bilingual math |
| Deferred | Expand draft source packs / holonomy crown proof |
| Rejected | Invent Greek case / Hebrew binyan from English GSM8K |

---

## PR-ready summary

**Branch:** `feat/deterministic-relational-operator-ablation`  
**Title:** `feat(eval): deterministic relational operator ablation (fraction_decrease)`

**Description:**
Evidence-led cartography of language packs, depth spine, and ProblemFrame/math paths. Implements a narrow sealed ablation for `fraction_decrease` comparing math-frame baseline, geometric operator, inactive depth contribution, metadata-only control, and adversarial refuse. Proves depth metadata is inert on English arithmetic; does not invent ancient-language role mapping.

`[Verification]: Smoke suite passed locally (176 passed, ~132s); ablation tests 20 passed; ablation runner passed (n=8, wrong=0).`

**Risks:** Imports private hazard helpers from fraction_decrease for shared refuse gates; scale>1 organ gap remains.  
**Rollback:** Revert branch commits; no serving flag changes.  
**Reviewer checklist:**
- [ ] Cartography matrix rows cite live paths
- [ ] No English→case/binyan mapping introduced
- [ ] Metadata-only inert invariant holds
- [ ] wrong=0 on sealed fixture
- [ ] Preexisting A2k gap not masked
