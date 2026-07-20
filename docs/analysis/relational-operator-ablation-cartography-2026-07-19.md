# Relational Operator Ablation — Cartography Ledger & Go/No-Go

**Date:** 2026-07-19  
**Branch:** `feat/deterministic-relational-operator-ablation`  
**Worktree:** `../core-relational-operator-ablation`  
**Authority commit:** `d8d62b8e` (main tip at branch creation)  
**Status:** Evidence ledger for Phase 1–2; implementation of the narrow GO slice is companion code under `generate/relational_operator_ablation.py` and `evals/relational_operator_ablation/`.

**Related:** HE/GRC broader capability is **not** authorized by this ledger. See `docs/analysis/hebrew-koine-greek-logos-pack-capability-roadmap-2026-07-19.md` (verdict: READY ONLY FOR PREREQUISITE WIRING OR MIGRATION).

---

## 1. Executive decision (closed)

**Verdict for this work product:** **IMPLEMENTED AND MEASURED** (narrow slice only).

| Scope | Decision |
|-------|----------|
| Full hypothesis: ancient morphology automatically improves GSM8K arithmetic | **NO-GO** (scientific precondition: no valid English→depth mapping; anti-circularity) |
| Narrow fraction_decrease relational-operator ablation | **GO** — family already LIVE with ProblemFrame + VersorBinding + A2k |
| Depth as *executable* math contribution on English word problems | **NO-GO for implementation of new mapping** — metadata-only control proves inert |

**Relation family chosen from live evidence:** `proportional_change.decrease_to_fraction` / organ `fraction_decrease`  
(`generate/construction_affordances.py` `_SERVING_AUTHORIZED_FAMILIES`; `generate/derivation/fraction_decrease.py`; Gate A2k in `generate/math_candidate_graph.py`).

### Decision criteria checklist

| Criterion | Pass/Fail | Evidence |
|-----------|-----------|----------|
| Canonical relation seam exists | **Pass** | `BoundRelation(relation_type="decrease_to_fraction")`, roles via `problem_frame_bound_relations` |
| Deterministic reconstructable operator | **Pass** | `VersorBinding` + CGA dilation; same text → same answer |
| Correction/readback or native integrity | **Pass (native)** | Self-verify + span provenance + `versor_condition < 1e-6`; no fabricated dual-adjoint |
| Testable eval lane | **Pass** | Sealed `evals/relational_operator_ablation/v1` + existing train_sample organ tests |
| Baseline vs operator vs depth vs metadata-only | **Pass** | Ablation conditions in harness |
| Fail-closed | **Pass** | Missing/ambiguous/hazard → refuse |
| Narrow non-claim scope | **Pass** | No full GSM8K claim; no EN→HE/GRC translation |

---

## 2. Live-path maps

### A. Text/chat — LIVE (not math serving)

```text
text → CognitiveTurnPipeline.run (core/cognition/pipeline.py)
     → tokenize / resolve_token_depths (chat/pack_resolver.py)
     → recognize (recognition/anti_unifier.py; root-canonical for he/grc)
     → ChatRuntime.chat (chat/runtime.py)
     → ingest.gate → FieldState
     → PropositionGraph (generate/graph_planner.py)
     → realizer / gates / refusal
     → CognitiveTurnResult.node_depths
```

`contract_assessment=None` at `resolve_surface` — ProblemFrame **DISCONNECTED** from chat spine.

### B. Language packs — dual layer

| Layer | Path | Status |
|-------|------|--------|
| Source ADR-0005 | `packs/{en,he,grc,el}/` status=draft, gates false | **DRAFT / DISCONNECTED** from compiler |
| Compiled | `packs/data/*` → `packs.compiler.load_pack` → `_apply_morphology` | **LIVE** |
| Depth IDs | `DEPTH_PACK_IDS` = he_core_cognition_v1, he_logos_micro_v1, grc_logos_* | **LIVE** |

### C. Problem-frame / math

```text
text → build_problem_frame (generate/problem_frame_builder.py)  [DIAGNOSTIC IR + A2k input]
     → proposals / BoundRelation / BoundQuestionTarget
     → assess_fraction_decrease / assess_geometric_proposals
     → VersorBinding dilation
     → resolve_promotable_fraction_decrease (generate/derivation/fraction_decrease.py)
     → answer  [LIVE Gate A2k]

parse_and_solve (generate/math_candidate_graph.py)  [LIVE GSM8K serving orchestrator]
```

| Family | serving_allowed | Status |
|--------|-----------------|--------|
| fraction_decrease | **True** | **LIVE** A2k |
| percent_partition | False catalog; live prose A2l | **LIVE but DISCONNECTED** from frame |
| quantity_entity | False | **DIAGNOSTIC** |
| unary_delta | False | **DIAGNOSTIC** (no derivation organ) |

### D. Evaluation

| Split | N | correct / wrong / refused | Scorer |
|-------|---|---------------------------|--------|
| Sealed GSM8K test (recorded) | 1319 | **0 / 0 / 1319** | operator-only holdout |
| train_sample report.json | 50 | **30 / 0 / 20** | `_score_one_candidate_graph` |
| holdout_dev report.json | 500 | **5 / 0 / 495** | same |
| CORE public synthetic | 150 | **150 / 0 / 0** | classic `_score_one` |

**Note:** Order is always **correct / wrong / refused**. Prior prose that wrote `30/20/0` swapped wrong/refused.

---

## 3. Design truth matrix

| Claim | Spec | Implementation | Runtime | Tests | Status |
|-------|------|----------------|---------|-------|--------|
| Hebrew root morphology | ADR-0015 | `MorphologyEntry.root`; `_apply_morphology` | LIVE manifold + resolver | `test_morphology_registry`, holonomy | **LIVE (sparse)** |
| Hebrew binyan | ADR-0005 | Inflection tag only | geometric tag | sparse data | **Partial** |
| Greek case/aspect/voice | ADR-0015 | Compiled inflection tags | LIVE tags | morphology_registry | **Partial** |
| Anchor lens | pack inventory | `packs/anchor_lens/` | LIVE overlay | inventory | **LIVE** |
| PropGraph / depth | 3lang plan | `depth_canonical`, pipeline | LIVE he/grc input | `test_3lang_depth_capability` | **LIVE spine** |
| Depth → math answer | — | `enrich_assessments_with_depth` explanation only | decoration | same | **Inert on math** |
| Canonical math roles | kernel substrate | BoundRelation roles | A2k + diagnostic | problem_frame tests | **LIVE fraction** |
| VersorBinding | CGA construction boundary | dilation payload | LIVE A2k | fraction + 3lang tests | **LIVE** |
| Readback / integrity | organ self-verify | spans + verified derivation | LIVE | fraction_decrease | **Partial (native)** |
| GSM8K eval | ADR-0119+ | train_sample/holdout/sealed | LIVE open | runners | **LIVE** |
| serving_allowed all False | prior claim | one True family | — | construction_affordances | **Contradicted** |
| FGL | prior claim | — | — | — | **ABSENT** |
| ADR-0248 as Logos | prior claim | integrity handoffs | observe-only | ring3 | **Miscited** |
| ADR-0196 ancient packs | prior claim | Python/Rust/Zig | — | ADR text | **False** |
| EN GSM8K → GRC case / HE binyan | prior claim | — | — | — | **ABSENT** |

---

## 4. Claim corrections (prior synthesis)

1. **EN/HE/GRC roles** — Partially confirmed (ADRs + LIVE compiled packs; source packs draft).  
2. **ADR-0005/0015** — Confirmed as architecture; implementation is `packs/data` compiler path.  
3. **packs/he, packs/grc draft + compiler** — Confirmed split: draft source vs LIVE compiled.  
4. **Ordered morph composition** — Confirmed LIVE+tested in `packs/compiler._apply_morphology`.  
5. **depth_canonical / enrich** — Confirmed; enrich is **decoration**; recognize is **matching**.  
6. **ProblemFrame symbols** — Confirmed under `generate/`.  
7. **All serving_allowed=False** — **False**; fraction_decrease is True.  
8. **No EN→case/binyan math path** — Confirmed absent.  
9. **GSM8K all refused** — Sealed test **0/0/1319** recorded; train_sample **30/0/20**; holdout_dev **5/0/495**. claims_ledger C **7/43/0** is **stale**.  
10. **FGL / ADR-0248 Logos** — FGL absent; ADR-0248 = integrity handoffs.  
11. **ADR-0196** — Python/Rust/Zig, not ancient packs.

---

## 5. Implementation plan (narrow GO)

1. Pure condition runners: baseline scalar from frame roles; operator geometric; metadata-only depth; invalid refuse.  
2. No new depth→role mapping from English.  
3. Sealed fixture v1 (fraction_decrease + confusers).  
4. Measurement report + tests.  
5. Smoke gate.

---

## 6. Remaining gaps (not in this slice)

- Engineering: wire ProblemFrame into CognitiveTurnPipeline (optional future).  
- Engineering: unify percent_partition prose organ with frame contracts.  
- Scientific: whether *observed* he/grc morphology can constrain math on bilingual inputs (unproven; not this PR).  
- Rejected: inventing Greek cases for English GSM8K.  
- Deferred: expanding draft `packs/he|grc` gates.
