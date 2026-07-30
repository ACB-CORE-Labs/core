# Phase 4 — Alignment Matrix (Batch 1: ADR-0001–0050)

One row per ADR. **Build**, **Liveness**, and **Necessity/generality** are the three axes every dossier/card scored with a clean single-token verdict for every member ADR — reproduced here directly. **Design fidelity**, **Build fidelity**, and **Fitness/value** are per-pillar/per-axiom and often mixed within one ADR (e.g. "matches on 3 axioms, tension on 1") — rather than force those into a lossy single token, this matrix carries a **Continuity** flag (derived from `21-drift-report.md`: does this ADR appear as an unreconciled contradiction) and a **Headline finding** column pointing at the `AA-N` IDs that carry the full nuance; open the linked card/dossier for the complete 7-axis breakdown. **Verified against:** `main` @ `cbfc8ccb`.

| ADR | Title | Build | Liveness | Necessity/Generality | Continuity | Headline finding(s) | Full card |
|---|---|---|---|---|---|---|---|
| 0001 | VocabManifold Versor Invariant | full | live | irreducible | clean (invariant itself), but its guard cannot see a downstream defect | `AA-1` 🔴 nearest() near-constant · `AA-2` 🔴 stores unit versors, not null points | A1 |
| 0002 | Ingest Layer Architecture | full | wired-but-unreached | irreducible | clean | `AA-118` 🟢 zero-drift LLM-rejection decision, confirmed | B1 |
| 0003 | Coordinate System Dissolution | partial | wired-but-unreached | generalization-candidate | contradicted by child ADR-0004 | `AA-7` 🟡 watch-item recurred one layer up · `AA-13` 🟡 | A1 |
| 0004 | Rotor as Operator, Not Vocabulary Property | full | live | **irreducible — the stack's general mechanism** | clean | `AA-5`,`AA-6`,`AA-15` 🔵 four+ sites bypass it | A1 |
| 0005 | Language Pack Contract | scaffolded | live-but-harmful | reducible-to-L0-algebra-ops | **FA-1 DEFECTIVE**, unreconciled | `AA-41` 🔴 8 gates → 1 boolean · `AA-42` 🔴 | A3 |
| 0006 | Field Energy Operator | full | live | irreducible | invisible in governing disposition table | `AA-27` 🟢 absent from §1.1 despite being load-bearing | A2 |
| 0007 | The Valence Layer | partial | wired-but-unreached | generalization-candidate (→ merge with 0006) | unregistered orphan | `AA-16`,`AA-17` 🟡 no consumer of 5 channels · `AA-28` 🔵 | A2 |
| 0008 | Allocation Physics | partial | live (salience) / dead (blueprint trio) | generalization-candidate | disposition table itself stale | `AA-20` 🟡 revises adopted evidence (InhibitionMask exists) | A2 |
| 0009 | Compositional Physics | partial | wired-but-unreached (3 of 4 dead) | reducible-to-proposition-graph | **no supersession marker**, unreconciled | `AA-32` 🟡 | A2 |
| 0010 | Identity Physics | full | live (identity) / dead (drive) | reducible-to-ADR-0244 | clean (correctly superseded, just not retired) | `AA-19` 🟡 revises adopted evidence · `AA-25` 🟡 unbuilt bias/fatigue | A2 |
| 0011 | Renderer Layer Contract | **ghost** | dead | reducible-to-`generate/realizer.py` | **reversed by drift**, unreconciled | `AA-37`,`AA-38` 🟡 no owning ADR for the real renderer | A2 |
| 0012 | `core_ingest` Governance Layer | full | wired-but-unreached | generalization-candidate | clean | `AA-123` 🔵 pairs with ADR-0021 | B1 |
| 0013 | `sensorium/` Multimodal Protocol Layer | partial | wired-but-unreached | generalization-candidate | own status table understates what's built | `AA-121` 🟡 record/reality divergence (conservative direction) | B1 |
| 0014 | `train/` Learning Loop | **ghost** | dead | reducible-to-M5-teaching-formation | never contradicted, never reconciled — silent divergence since 2026-05-13 | `AA-124`,`AA-125` 🟡 module doesn't exist anywhere | B2 |
| 0015 | Language Packs as Compiled Linguistic Manifolds | partial | schema-live / proof-ghost | reducible-to-L0-algebra-ops | **FA-1 DEFECTIVE** (self-documented amendment) | `AA-51` 🔴 closure deleted · `AA-52` 🔴 retired claim live in docstring | A3 |
| 0016 | Capability Roadmap and Eval Methodology | partial | live (mechanism) | irreducible (governance) | its own tracked artifact (`docs/PROGRESS.md`) stale since 2026-05-26 | `AA-133` 🟡 60/129 eval dirs carry mandated contract | B3 |
| 0017 | Agency Scope: Responsive-with-Axiology | partial | wired-but-unreached (axiology clause) | irreducible | independently confirmed by `docs/PROGRESS.md`'s own finding | `AA-127` 🟡 | B2 |
| 0018 | Tool Use Scope: Typed Deterministic Operators | partial | live (+ 1 dead operator) | irreducible | clean | `AA-128` 🟡 `path_recall` built, unreached, wrong substrate | B2 |
| 0019 | Exact Vault Recall Acceleration | full (Stage 1) | live | irreducible | clean | measured ~4,000–5,000× speedup, bit-identical | B2 |
| 0020 | Phase 5 / Rust Parity Sequencing | full | wired-but-unreached | generalization-candidate | urgency rationale refuted by later measurement | `AA-136` 🟡 hot path bypasses dispatch entirely | B3 |
| 0021 | Epistemic Grade Policy | full | live | irreducible (disconnected from runtime surface) | clean design, disconnected in practice | `AA-59` 🔴 `AlignmentEdge` carries no `epistemic_status` | A3 |
| 0022 | Forward Semantic Control | full | wired-but-unreached (region) / live (ratifier) | generalization-candidate | ratified-inert per ADR-0058 | `AA-102` 🔴 honest-refusal doctrine violated by the code path that runs · `AA-86` 🟡 zero ops on default path | A4 |
| 0023 | Forward Semantic Control: Proof Evidence | full | live (recording a constant) | irreducible | clean | best-designed evidence layer in the stack | A4 |
| 0024 | Inner-Loop Per-Rotor Admissibility | full | wired-but-unreached | generalization-candidate (→0026) | clean | `AA-93` 🟡 claims to gate production, does not | A4 |
| 0025 | Rotor / Frame Admissibility | full | **scaffolded** (no producer outside tests) | irreducible | clean | `AA-91` 🟡 structurally unreachable, not just flag-gated | A4 |
| 0026 | Ranked Admissibility with Margin | full | wired-but-unreached | irreducible | clean | strongest member; `δ=0.4` is the repo's derivation exemplar | A4 |
| 0027 | Identity Packs — Load-Bearing, Swappable, Ratified | full | live | irreducible (loader = generalization-candidate) | clean | `AA-115` 🟡 `core pulse --identity` doesn't exist | A5 |
| 0028 | Identity Surface Wiring | full | live | generalization-candidate | clean | consolidates cleanly with 0030/0031 | B4 |
| 0029 | Safety Packs — Always-Loaded, Never-Replaceable | full | live | irreducible | clean | **sabotage test passed** — genuinely fail-closed | A5 |
| 0030 | Depth-Language Hedge Wiring | full | live | irreducible | clean | clean extension of `_apply_hedge` | B4 |
| 0031 | Score-Decomposition Surface | full | live | irreducible | clean | re-ratification SHAs independently verified | B4 |
| 0032 | SafetyCheck | full | live surface, 4 of 5 predicates unreachable | reducible-to-{versor halt, teaching review, INV-34} | clean | `AA-104`–`AA-106` 🟡 3 of 5 boundaries can't fail | A5 |
| 0033 | Ethics Packs — Swappable Domain Commitments | full | live | generalization-candidate | clean | `AA-107` 🔴 unratified pack → silent zero-refusal fallback | A5 |
| 0034 | EthicsCheck | full | live-but-inconsequential | generalization-candidate | clean | `AA-110` 🔵 one mechanism with SafetyCheck, built twice | A5 |
| 0035 | Turn-Loop Verdict Surfacing | full | live | irreducible | clean | matches design; strongest B5 member | B5 |
| 0036 | Safety-Only Typed Refusal Policy | full | live (1 reachable trigger) | irreducible | clean | never observed firing outside unit tests | A5 |
| 0037 | Per-Predicate Ethics Refusal Opt-In | full | inert under 4 of 5 shipping packs | irreducible | clean | premised on empirical rates that don't exist | A5 |
| 0038 | Hedge Injection as a Runtime-Level Affordance | full | live-but-narrow (CLI-unreachable) | generalization-candidate | clean (on its own terms) | `AA-142` 🔵 second independent hedge mechanism | B4 |
| 0039 | Audit Completeness — `TurnVerdicts` Bundle | full | live | irreducible | clean | stub-path fully discharged, not residual | B5 |
| 0040 | Structured-Logging Sink for Turn-Event Audit | full | live | irreducible | doc table stale vs. running serializer | `AA-148` 🟡 `schema_version` open in 2 ADRs, closed in 0 | B5 |
| 0041 | `core chat --show-verdicts` + Sink Fan-Out | full | live | irreducible | clean | confirmed live via direct CLI execution | B5 |
| 0042 | Audit Tour Demo | full | live | irreducible | clean | confirmed live, `all_claims_supported: true` | B5 |
| 0043 | Phase-2 pack measurements | full (Tier C) | live (artifact existence) | not assessed (Tier C) | clean | all 5 claimed artifacts exist | Triage §12 |
| 0044 | Medical/clinical ethics pack | full (Tier C) | live (artifact existence) | not assessed (Tier C) | clean | all 4 claimed artifacts exist | Triage §12 |
| 0045 | Long-context recall vs. transformer baselines | full (Tier C) | live (artifact existence) | not assessed (Tier C) | 🟢 one broken cross-reference | `AA-159` 🟢 dead link to nonexistent ADR-0001 filename | Triage §12 |
| 0046 | PropositionGraph as Forward Admissibility Constraint | full | wired-but-unreached (ratified inert) | generalization-candidate | undocumented second role, inverts ADR-0009 lineage | `AA-94` 🔵 feeds CR-1 ruling | A4 |
| 0047 | Wire the Forward Graph Constraint into the Chat Hot Path | full | wired-but-unreached (flag off) | generalization-candidate | clean | code path real; production reality is the flag | B6 |
| 0048 | Pack-Grounded Surface for Cold-Start DEFINITION/RECALL | full | live | irreducible (anchor of shared dispatcher) | clean | `AA-153` 🟡 eval results stale, missed own ≥0.80 bar | B6 |
| 0049 | Intent Classifier Head-Noun Subject Extraction | full | live | irreducible (narrower role than title) | clean | lemma-cleaner, not the router (that's ADR-0018) | B6 |
| 0050 | Pack-Grounded Surface for Cold-Start COMPARISON | full | live | generalization-candidate | clean | `AA-157` 🔵 shares dispatcher, one small gap remains | B6 |

## Batch 1 rollup

- **Build:** 2 ghost (0011, 0014) · 1 scaffolded-critical (0005) + 1 scaffolded-narrow (0025) · 10 partial · 36 full.
- **Liveness:** 2 dead · 2 scaffolded · ~19 wired-but-unreached · ~27 live (several ADRs split across sub-mechanisms — see Notes).
- **Necessity:** 3 confirmed irreducible-general-mechanism (0004, 0019, 0029 — the three strongest members of their respective stacks) · ~20 generalization-candidates · ~4 reducible-to-named-alternative · 3 not assessed (Tier C).
- **Continuity:** 43 clean · **7 unreconciled contradictions** (0003/0004 parent-child, 0005, 0009, 0011, 0015, plus the FA-1 cascade's 19 dependents outside Batch 1 — see `21-drift-report.md`).
- **🔴 Block-severity ADRs** (carry at least one 🔴 finding): 0001, 0005, 0015, 0021, 0022, 0033 — 6 of 50 (plus four cascade-dependent ADRs outside Batch 1's numeric range: 0073/0073a, 0102/0103, 0180, 0240 — see `21-drift-report.md` §1). All six in-batch entries sit in stacks A1, A3, A4, or A5 — concentrated in the foundational/semantic-ground/admissibility/safety layers, consistent with the plan's bottom-up prioritization actually surfacing the highest-stakes material first.

## Batch 2 (ADR-0051–0100) Summary

- **Total ADRs:** 52 (21 Tier A across 6 dossiers, 30 Tier B across 7 zone-cards, 1 Tier C triage row).
- **Findings Registered:** 171 findings (`AA-160`–`AA-330`: 19 🔴 Block, 71 🟡 Repair, 22 🔵 Consolidate, 59 🟢 Monitor).
- **Key 🔴 Block ADRs:** ADR-0061 (`AA-250` holdout leak), ADR-0087 (`AA-293` zero consumers), ADR-0091 (`AA-233` no eval result consulted), ADR-0093 (`AA-219` unimplemented promotion invariant), ADR-0094 (`AA-308` reviewer reg unwired), ADR-0095 (`AA-234` grammar-only coverage, `AA-310` no-op replay pre-gate), ADR-0096 (`AA-231` failing lane), ADR-0097 (`AA-232` unsaved demotion bypass), ADR-0113-context (`AA-220` false context claim).

## Batch 3 (ADR-0101–0150) Summary

- **Total ADRs:** 91 (53 Tier A across 7 stacks, 35 Tier B across 6 zones, 3 Tier C triage rows).
- **Findings Registered:** 21 findings (`AA-331`–`AA-351`: 0 🔴 Block, 12 🟡 Repair, 1 🔵 Consolidate, 8 🟢 Monitor).
- **Key Findings:**
  - **FA-1 Cascade (`AA-75`):** ADR-0101 (`AA-345`) & ADR-0102 (`AA-332`) inherit the defective cross-language holonomy claim.
  - **Unbuilt Design Spikes:** ADR-0138 (`AA-348`), ADR-0139 (`AA-349`), ADR-0140~2 (`AA-350`), ADR-0141 (`AA-351`) remain unbuilt versor arithmetic design spikes.
  - **Proposed Status Headers:** ADR-0114 (`AA-336`), ADR-0119 (`AA-338`), ADR-0131 (`AA-340`) headers remain `Proposed` while underlying code/gates are fully built and tested.
  - **Clean Architectural Milestones:** Sealed holdouts via `age` (ADR-0105 / `AA-337`), Audit-Passed Domain Contract (ADR-0106–0113 / `AA-333`), Anti-Overfitting Obligations (ADR-0114a / `AA-335`), Composite Math Gate (ADR-0131 / `AA-339`), Semantic-Symbolic Binding Graph (ADR-0132–0135 / `AA-343`).

## Batch 4 (ADR-0151–0200) Summary

- **Total ADRs:** 56 (44 Tier A across 6 stacks, 10 Tier B across 3 zones, 2 Tier C triage rows).
- **Findings Registered:** 26 findings (`AA-352`–`AA-377`: 1 🔴 Block, 2 🟡 Repair, 2 🔵 Consolidate, 21 🟢 Monitor).
- **Key Findings:**
  - **FA-1 Cascade (`AA-64`):** ADR-0180 (`AA-361` 🔴 Block) rests Delta-CRDT sharded substrate premise on retired Holonomy Resonance claim. Audio & Vision compilers (ADR-0181, 0197 / `AA-362` 🟡) inherit premise.
  - **Motor Efferent Decoder (`AA-373` 🟡):** ADR-0198 implemented fail-closed efferent gate (`sensorium/efferent.py`) while physical decoding remains deferred to ADR-0216.
  - **Clean Architectural Milestones:** Auto-proposal pipeline & atomic checkpointing (ADR-0151–0159 / `AA-352`), Incremental Comprehension Reader (ADR-0164 / `AA-354`), FrameClaim/CompositionClaim architecture (ADR-0167–0172 / `AA-356`), Compositional Structure & Extraction Richness (ADR-0174–0179 / `AA-358`), CORE Workbench v1 (ADR-0160–0162, 0173 / `AA-368`–`AA-371`), Native Substrate Language Doctrine (ADR-0196 / `AA-372`), Cross-Domain Learning Arena (ADR-0199 / `AA-374`), Expert-Claim Reconciliation (ADR-0200 / `AA-375`).

## Batch 5 (ADR-0201–0250) Summary

- **Total ADRs:** 50 (35 Tier A across 5 stacks, 15 Tier B across 3 zones, 0 Tier C triage rows).
- **Findings Registered:** 46 findings (`AA-378`–`AA-423`: 1 🔴 Block, 0 🟡 Repair, 0 🔵 Consolidate, 45 🟢 Monitor).
- **Key Findings:**
  - **FA-1 Cascade (`AA-68`):** Biography Holonomy Blade (ADR-0240 / `AA-395` 🔴 Block) rests on deleted `holonomy_encode` closure.
  - **Clean Architectural Milestones:** ROBDD Propositional Canonicalizer & Proof Chain (`ADR-0201`–`ADR-0205`, `ADR-0218` / `AA-378`–`AA-382`), Wave-Field Cognitive Lifecycle & Hyperbolic Atlas (`ADR-0241`–`ADR-0250` / `AA-383`–`AA-392`), GoldTether Autonomy & Conformal Procrustes (`ADR-0238`, `ADR-0239` / `AA-393`, `AA-394`), Environmental Sensorium & Motor Lowering (`ADR-0208`, `ADR-0209`, `ADR-0216` / `AA-396`–`AA-398`), Conformal Falsification & Practice Envelopes (`ADR-0211`, `ADR-0226`–`ADR-0234` / `AA-399`–`AA-408`), Substrate Hardening & Governance (`ADR-0206`–`ADR-0237` / `AA-409`–`AA-423`).

## Batch 6 (ADR-0251–0265) Summary

- **Total ADRs:** 15 (15 Tier A across 2 stacks, 0 Tier B across 0 zones, 0 Tier C triage rows).
- **Findings Registered:** 15 findings (`AA-424`–`AA-438`: 0 🔴 Block, 1 🟡 Repair, 1 🔵 Consolidate, 13 🟢 Monitor).
- **Key Findings:**
  - **Master Convergence & Reliability Bands (`AA-424`–`AA-433`):** Earned reliability license governing deduction serving (`ADR-0256`), Bands v2-EN through v6-EX (`ADR-0257`–`ADR-0261`), curriculum-grounded serving (`ADR-0262`), ratified-ledger bridge (`ADR-0263`), negative curriculum (`ADR-0264`), and proposition-graph negation (`ADR-0265`).
  - **Master Blueprint Governance (`AA-434`–`AA-438`):** Reader-arc recalibration (`ADR-0251`), problem-solving paradigm consolidation (`ADR-0252`), Master Blueprint ADR collision resolution & INV-33 dual-pack serve boundary (`ADR-0253`), grounded-open hedge arm (`ADR-0254`), and discovery-yield baseline telemetry (`ADR-0255`).




