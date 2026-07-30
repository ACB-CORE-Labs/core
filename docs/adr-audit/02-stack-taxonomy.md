# Phase 2 — Stack Taxonomy

Primary axis: `docs/assessment/02-layer-taxonomy.md`'s 7 macro layers (M0–M6) + 2 cross-cuts (MG, MV) over 33 zones. Secondary axis: the 11 phased sub-decision families from `01-adr-census.md` §2. Populated per batch — see `MANIFEST.md`.

## ⚠ Numbering-scheme disambiguation (read before assigning any ADR)

Two *different* layer-numbering schemes are both live in this repository and share the `L0`–`L5` prefix with different referents. Do not conflate them:

1. **Foundations Audit numbering** (`docs/plans/2026-07-28-foundations-audit.md`): `L0` algebra kernel → `L1` physics/field → `L2` semantic ground/logos → `L3` perception → `L4` cognition → `L5` serving, plus cross-cutting `X` (teaching/governance). This is what FA-1's verdict means when it says "L2 is DEFECTIVE" — the cross-language semantic-ground layer, governed by ADR-0005/0015.
2. **`docs/assessment` zone codes**: `L0-algebra`, `L1-field`, `L2-vault`, `L3-packs`, `L4-recognition`, `L5-cognition`, `L6-chat-runtime`, `L7-teaching`, `L8-memory-contemplation`, `L9-epistemic-verdicts`, `L10-11-runtime-identity` — 11 of the 33 zones happen to carry `L`-numbers as part of their zone name, grouped under macro layers M0–M6. Critically, **zone `L2-vault` is exact-recall memory, not the FA sense of "L2 semantic ground."** The FA sense of L2 corresponds to the `vocab-manifold` / `L3-packs` / `alignment-resonance` zones (under macro layer M1), not `L2-vault`.

**Convention used in this audit:** the stack tables below use `docs/assessment`'s zone codes and macro-layer letters (M0–M6, MG, MV) as primary, since that's the taxonomy Phase 2 committed to reusing. Foundations Audit layer numbers (`L0`…`L5`+`X`) are cited only when explicitly discussing an FA verdict, always spelled out as "FA-layer L2" to avoid ambiguity with zone `L2-vault`.

---

## Batch 1 (ADR-0001–0050) — Tier A stacks

| Stack | Macro layer(s) / zone(s) | Members | Why Tier A | Dossier |
|---|---|---|---|---|
| **A1 — Algebra & Geometry Foundations** | M0 · `L0-algebra` | 0001, 0003, 0004 | Foundational substrate — the versor invariant, coordinate-system dissolution, and the rotor-as-operator decision. ADR-0004 is the leading candidate for "the general mechanism" in the necessity/generality pass — flag every later ADR that builds a bespoke rotation/transform against it. | `10-stack-dossiers/A1-algebra-geometry-foundations.md` |
| **A2 — Mind-Physics Blueprint Family** | M0/M1 · `L1-field` + Candidate Register CR-1/CR-2 | 0006, 0007, 0008, 0009, 0010, 0011 | These six are *already partially adjudicated* by `docs/assessment/02-layer-taxonomy.md` §1.1 (the mind-physics-blueprint disposition table) — adopt, don't re-derive: **ADR-0008** (Allocation Physics) → "never landed as a layer... see CR-1"; **ADR-0009** (Compositional Physics) → "superseded — landed as the proposition-graph lineage"; **ADR-0010** (Identity Physics) → "superseded by stronger implementations" (ADR-0244 §3, INV-32); **ADR-0011** (Renderer) → "stale line — retire, `generate/realizer.py` has been the shipping renderer for months." ADR-0006/0007 (Field Energy, Valence) have no existing disposition and need a fresh read. | `10-stack-dossiers/A2-mind-physics-blueprint-family.md` |
| **A3 — Semantic Ground & Epistemic Status** | M1 · `vocab-manifold`, `L3-packs`, `alignment-resonance` | 0005, 0015, 0021 | **Urgent.** ADR-0005/0015 together are the pair FA-1 ruled `DEFECTIVE` (2026-07-28) — the cross-language holonomy-closure claim measured at AUC 0.557 against a required 0.80. This dossier's first job is the cascade-check: walk the citation graph for every *other* ADR (in any batch) that cites or structurally depends on this claim, and flag each for re-verdict. ADR-0021 (Epistemic Grade Policy) governs the SPECULATIVE/COHERENT status regime this stack's outputs are graded under — read together. | `10-stack-dossiers/A3-semantic-ground-epistemic-status.md` |
| **A4 — Forward Semantic Control & Admissibility** | M3 · `L4-recognition`; ties to Candidate Register **CR-1** (attention/allocation — "the hottest path in the system... no owner, no card, no governance") | 0022, 0023, 0024, 0025, 0026, 0046 | Admissibility is named explicitly in the Tier-A criterion. CR-1 already cites ADR-0024/0025/0026 by number as the *only* partial existence it found for attention/allocation — this stack is directly load-bearing for an open Candidate-Register ruling, not just its own content. | `10-stack-dossiers/A4-forward-semantic-control-admissibility.md` |
| **A5 — Identity/Safety/Ethics Packs & Checks** | MG (cross-cutting) · `governance-identity-safety` | 0027, 0029, 0032, 0033, 0034, 0036, 0037 | Safety/ethics boundaries, explicit Tier-A criterion. `AGENTS.md`'s INV-21…34 regime and the fail-closed identity/safety doctrine live here. | `10-stack-dossiers/A5-identity-safety-ethics-packs.md` |

**25 ADRs at Tier A**, grouped into 5 dossiers (not 25 files) — each dossier is one parallel-agent unit of work.

## Batch 1 — Tier B stacks (standard card)

| Zone card | Macro layer(s) | Members |
|---|---|---|
| B1 — Ingest & Multimodal Boundary | M2 | 0002, 0012, 0013 |
| B2 — Agency, Tool Use, Learning Loop & Vault | M3/M5/M1 | 0014, 0017, 0018, 0019 |
| B3 — Roadmap & Rust Parity | MV / M0 (cross-cutting infra) | 0016, 0020 |
| B4 — Identity/Hedge Surface Wiring | M4/MG | 0028, 0030, 0031, 0038 |
| B5 — Turn-Loop Verdict Surfacing & Audit Telemetry | MV/M4 | 0035, 0039, 0040, 0041, 0042 |
| B6 — Pack-Grounded Cold-Start Surfaces & Intent | M3/M1 | 0047, 0048, 0049, 0050 |

**22 ADRs at Tier B**, 6 zone-card files.

## Batch 1 — Tier C (rapid triage)

| ADR | Why Tier C |
|---|---|
| 0043 | Phase-2 pack measurements — a results/measurement doc, not an architectural decision |
| 0044 | Medical/clinical ethics pack — one worked-example domain-pack instance, not a mechanism |
| 0045 | Long-context recall benchmark comparison doc |

**3 ADRs**, logged in `12-triage-log.md`.

**Batch 1 total: 25 (A) + 22 (B) + 3 (C) = 50.** Matches `01-adr-census.md`'s Batch 1 row count.

---

## Batch 2 (ADR-0051–0100) — Tier A stacks

| Stack | Members | Why Tier A | Dossier |
|---|---|---|---|
| **A2.1 — Anchor Lens & Register Composition** | 0073, 0073a, 0073b, 0073c, 0073d, 0074 | Phased family (5 files) + **FA-1 cascade member**: `21-drift-report.md` §1 (`AA-74`) found this family's cross-language binding via shared `semantic_domains` atoms **is** the dominant collapse site (34 of 37 lost coordinates) behind FA-1's L2 verdict. ADR-0074 (orthogonality tour, a demo of anchor-lens × register composition) reads alongside it for full context. | `10-stack-dossiers/A2.1-anchor-lens-register-composition.md` |
| **A2.2 — Register Axis & Realizer Guard** | 0068, 0069, 0070, 0071, 0072, 0075, 0076, 0077 | Phased family (R1–R6 + the C1/C2 coherence-guard pair) already partially cited as load-bearing in `docs/adr/INDEX-by-domain.md`'s "Register axis and the realizer guard" section (0069, 0071, 0075, 0077 named directly). 8 members — largest single stack in Batch 2. | `10-stack-dossiers/A2.2-register-axis-realizer-guard.md` |
| **A2.3 — Trust Boundary & Admissibility Ratification** | 0051, 0058 | ADR-0058 is the ADR the entire Batch-1 admissibility stack (A4) cites as the formal ratification of its "engaged but inert" status (`AA-86`, `AA-93`, and others). Auditing it directly, rather than only through A4's citations, closes the loop. ADR-0051 (Trust-Boundary Hardening) is the adjacent MG-boundary decision from the same window. | `10-stack-dossiers/A2.3-trust-boundary-admissibility-ratification.md` |
| **A2.4 — Domain Pack Contract Generalization** | 0091, 0093 | Directly tests Batch 1's `AA-111` consolidation finding (five-plus pack loaders duplicating one skeleton) — this may be the generalized contract that should have subsumed them, or a sixth independent implementation of the same pattern. High-value cross-reference regardless of which it turns out to be. | `10-stack-dossiers/A2.4-domain-pack-contract-generalization.md` |
| **A2.5 — Capability Ledger Ratifications** | 0097, 0100 | `mathematics_logic` and `physics` reaching `audit-passed` (per `README.md`'s live capability table) are two of the most consequential events in the whole corpus — direct evidence for the fitness/value axis across many other stacks' claims. | `10-stack-dossiers/A2.5-capability-ledger-ratifications.md` |
| **A2.6 — Fabrication Control** | 0096 | Ties to the standing PR #138 fabrication findings that `docs/assessment/00-scope-and-method.md` records as "measured and pinned, held for ADR + ratification, never re-discovered, never fixed here." Check whether ADR-0096 is that held fix, a partial step toward it, or unrelated. | `10-stack-dossiers/A2.6-fabrication-control.md` |

**21 ADRs at Tier A**, 6 dossiers.

## Batch 2 — Tier B stacks

| Zone card | Members |
|---|---|
| B2.1 — Teaching/Pack-Grounded Surfaces (continuation of Batch 1's B6 territory) | 0052, 0061, 0062, 0063, 0064, 0066, 0067 |
| B2.2 — Cognition Lane, Correction & Telemetry | 0053, 0059, 0060, 0078 (composer/graph atom equivalence telemetry — the real ADR-0078, not the collision partner) |
| B2.3 — Memory, Contemplation & Vault Continuation | 0054 (Vault Recall Stage 2/3 — direct continuation of Batch 1's ADR-0019), 0055, 0056, 0057, 0080 |
| B2.4 — Lexicon, Composition & Style Extensions | 0065, 0083, 0084, 0085, 0087 |
| B2.5 — Audit-Finding Retries & Pipeline Dispatch | 0088, 0089, 0090 |
| B2.6 — Governance & Provenance | 0092, 0094, 0095 |
| B2.7 — Demo/Showcase & Frontier Adapters | 0082, 0098, 0099 |

**30 ADRs at Tier B**, 7 zone-cards. Note for whichever agent audits B2.3: ADR-0054 explicitly continues ADR-0019 (Batch 1, stack B2 — "Stage 1" shipped, Stages 2/3 correctly left untriggered per its own gating) — check whether 0054 is Stage 2, Stage 3, or both, and whether the gating condition that kept them untriggered in Batch 1 has since changed.

## Batch 2 — Tier C (rapid triage)

| ADR | Why Tier C |
|---|---|
| 0078 (phase1-implementation-note variant — audit ID `0078~2`) | A pre-implementation planning note, not a ratified decision (no Status field, no Decision section) |

**1 ADR**, logged in `12-triage-log.md`.

**Batch 2 total: 21 (A) + 30 (B) + 1 (C) = 52.** Verified against `01-adr-census.md`'s Batch 2 row count via script (no gaps, no duplicates).

## Batch 3 (ADR-0101–0150) — Tier A stacks

| Stack | Members | Why Tier A | Dossier Output |
|---|---|---|---|
| **A3.1 — FA-1 Cascade Carry-forwards & Textual Reasoning** | 0102, 0103 | FA-1 cascade carry-forward (`AA-75`): live ledger license resting on defective claim; Hebrew-Greek textual reasoning & fluency attachment. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.1 |
| **A3.2 — Expert Demo & Audit-Passed Promotion Contract Family** | 0106, 0107, 0109, 0110, 0111, 0112, 0113 | Phased family defining `expert-demo` / `audit-passed` vocabulary and thresholds across math and physics. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.2 |
| **A3.3 — Anti-Overfitting Proof Obligations Roadmap (`0114` family)** | 0114, 0114a, 0114a.2, 0114a.5, 0114a.6, 0114a.8, 0114a.10 | Phased mega-family (7 files) introducing 10 anti-overfitting proof obligations for expert promotion. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.3 |
| **A3.4 — GSM8K Math Eval Roadmap & Lane Runner (`0119` family + 0105)** | 0105, 0119, 0119.1, 0119.2, 0119.3, 0119.4, 0119.5, 0119.6, 0119.7, 0119.8 | Phased mega-family (10 files) establishing sealed holdouts (`age` encryption) and the `gsm8k_math` lane gate. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.4 |
| **A3.5 — Math Expert Re-Benchmark Mega-Family (`0131` family)** | 0131, 0131.1.F, 0131.1.S, 0131.2, 0131.2.B, 0131.3, 0131.4, 0131.5, 0131.G, 0131.G.0, 0131.G.1, 0131.G.2, 0131.G.3, 0131.G.3.1, 0131.G.4, 0131.G.5 | Phased mega-family (16 files) re-targeting math expert promotion to architecture-aligned benchmarks and probe axes. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.5 |
| **A3.6 — Statement Corridor & Parser Extensions (`0136` family)** | 0136, 0136.S.1, 0136.S.2, 0136.S.4, 0136.S2, 0136.S3~1, 0136.S3~2 | Phased family (7 files) covering statement-layer corridor, rate/event parsing, and compound initial mutation. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.6 |
| **A3.7 — Semantic-Symbolic Binding Graph** | 0132, 0133, 0134, 0135 | Phased family (4 files) establishing the 4-phase binding graph data model, adapter, equation admissibility, and question target. | `10-stack-dossiers/Batch3-TierA-consolidated.md` §A3.7 |

**53 ADRs at Tier A**, audited in one consolidated subagent pass (`10-stack-dossiers/Batch3-TierA-consolidated.md`).

## Batch 3 — Tier B stacks

| Zone card | Members | Card Output |
|---|---|---|
| B3.1 — Curriculum & Mining Proposal Pipeline | 0101, 0104, 0108 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.1 |
| B3.2 — Math Parser, Solver & Verifier Core | 0115, 0116, 0117, 0118, 0118a, 0122~1, 0123~1, 0126, 0127~2, 0128 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.2 |
| B3.3 — Capability Ledger Deferrals & Remaps | 0120~1, 0120~2, 0120~3, 0121, 0122~2, 0123~2, 0123a, 0124, 0125 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.3 |
| B3.4 — Epistemic State & Multi-Resolution Recognition | 0142, 0143, 0144, 0145, 0148, 0149 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.4 |
| B3.5 — Versor Arithmetic & Inverse Translation Spikes | 0138, 0139, 0140~1, 0140~2, 0141 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.5 |
| B3.6 — Engine State Persistence & Autonomous Contemplation | 0146, 0150 | `11-adr-cards/Batch3-TierB-consolidated.md` §B3.6 |

**35 ADRs at Tier B**, audited in one consolidated subagent pass (`11-adr-cards/Batch3-TierB-consolidated.md`).

## Batch 3 — Tier C (rapid triage)

| ADR | Why Tier C |
|---|---|
| 0127~1 (`ADR-0127-0128-RESULTS.md`) | Empirical results companion doc, not a decision record |
| 0129 (`ADR-0129-spaced-correction-replay-deferred.md`) | Deferred proposal backlog item, no code landed |
| 0130 (`ADR-0130-pre-articulation-calibration-deferred.md`) | Deferred proposal backlog item, no code landed |

**3 ADRs**, logged directly in `12-triage-log.md`.

## Batch 4 (ADR-0151–0200) — Tier A stacks

| Stack | Members | Why Tier A | Dossier Output |
|---|---|---|---|
| **A4.1 — Auto-Proposal & Checkpoint Resilience Pipeline** | 0151, 0152, 0153, 0154, 0155, 0156, 0157, 0158, 0159 | Phased family (9 files) establishing auto-proposal injection at load, contemplation quality evals, atomic checkpointing, and reboot audit trail. | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.1 |
| **A4.2 — Comprehension Reader & Lexical Primitive Architecture (`0164` family + 0165)** | 0164, 0164.1, 0164.2, 0164.3, 0164.4, 0165 | Phased family (6 files) replacing regex sentence-templates with Incremental Comprehension Reader and enforcing lexeme-only regex scope. | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.2 |
| **A4.3 — FrameClaim & CompositionClaim Ratification Architecture** | 0167, 0168, 0168.1, 0169, 0169.1, 0172 | Phased family (6 files) establishing FrameClaim & CompositionClaim ratification doctrines, adapters, and corpus decomposition mechanisms. | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.3 |
| **A4.4 — Compositional Structure & Extraction Richness (`0178` family + 0174–0177, 0179)** | 0174, 0175, 0176, 0177, 0178, 0178-GB3b, 0179 | Phased family (7 files) governing held-hypothesis comprehension, attempt-and-eliminate learning, multi-step composition, and extraction richness. | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.4 |
| **A4.5 — Multimodal Delta-CRDT Substrate & Compilers (`0180` family + 0181, 0183, 0197)** | 0180, 0181, 0183, 0197 | Phased family (4 files) establishing Delta-CRDT sharded substrate for multimodal concurrency, Audio compiler, and Vision compiler. Carries FA-1 cascade carry-forward (`AA-64`, `AA-66`, `AA-67`). | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.5 |
| **A4.6 — English Multi-Step & Comparative Grammar Expansion (`0184` family + 0182, 0185, 0186, 0189, 0189a, 0191–0195)** | 0182, 0184, 0184-scoped, 0185, 0186, 0189, 0189a, 0191, 0192, 0193, 0194, 0195 | Mega-family (12 files) covering distinct-unit product rules, comparative verb widening, discrete count open noun classes, product promotion bridges, and sealed candidate-graph injector lanes. | `10-stack-dossiers/Batch4-TierA-consolidated.md` §A4.6 |

**44 ADRs at Tier A**, audited in one consolidated subagent pass (`10-stack-dossiers/Batch4-TierA-consolidated.md`).

## Batch 4 — Tier B stacks

| Zone card | Members | Card Output |
|---|---|---|
| B4.1 — CORE Workbench UI & HITL Async Queue | 0160, 0161, 0162, 0173 | `11-adr-cards/Batch4-TierB-consolidated.md` §B4.1 |
| B4.2 — Learning Arena, Motor Efferent & Substrate Languages | 0196, 0198, 0199, 0200 | `11-adr-cards/Batch4-TierB-consolidated.md` §B4.2 |
| B4.3 — Measurement & Sequencing Governance | 0166, 0170 | `11-adr-cards/Batch4-TierB-consolidated.md` §B4.3 |

**10 ADRs at Tier B**, audited in one consolidated subagent pass (`11-adr-cards/Batch4-TierB-consolidated.md`).

## Batch 4 — Tier C (rapid triage)

| ADR | Why Tier C |
|---|---|
| 0163 (Confuser Corpus Spec) | Specification-only discrimination probe, no code landed |
| 0163-gsm8k (Path to GSM8K Mastery) | Prescriptive roadmap doc superseded by ADR-0207 |

**2 ADRs**, logged directly in `12-triage-log.md`.

## Batch 5 (ADR-0201–0250) — Tier A stacks

| Stack | Members | Why Tier A | Dossier Output |
|---|---|---|---|
| **A5.1 — Proof Chain Keystone & Proposition Canonicalizer** | 0201, 0201.1, 0202, 0203, 0204, 0205, 0218 | Phased family (7 files) establishing the `proof_chain` keystone, acyclicity invariant, modus ponens, and proof-carrying coherence promotion. | `10-stack-dossiers/Batch5-TierA-consolidated.md` §A5.1 |
| **A5.2 — Wave-Field Cognitive Lifecycle & Hyperbolic Atlas** | 0241, 0242, 0243, 0244, 0245, 0246, 0247, 0248, 0249, 0250 | Phased mega-family (10 files) establishing wave-field driven hyperbolic atlas, resonant cognition, identity manifold, multi-port residual protocol, and Tier-2 multi-entity arithmetic. Carries FA-1 cascade carry-forwards (`AA-70`, `AA-71`, `AA-72`). | `10-stack-dossiers/Batch5-TierA-consolidated.md` §A5.2 |
| **A5.3 — Analogical Search & Biography Holonomy** | 0238, 0239, 0240 | Phased family (3 files) covering GoldTether supervised autonomy, conformal procrustes search, and Biography Holonomy Blade. Carries FA-1 cascade 🔴 Block carry-forwards (`AA-68`, `AA-69`). | `10-stack-dossiers/Batch5-TierA-consolidated.md` §A5.3 |
| **A5.4 — Environmental Sensorium & Afferent Feedback Loop** | 0208, 0209, 0216 | Phased family (3 files) establishing environmental sensorium loop, afferent feedback contracts, and motor verdict lowering prerequisites. | `10-stack-dossiers/Batch5-TierA-consolidated.md` §A5.4 |
| **A5.5 — Conformal Falsification & Practice Envelopes (`0211` + 0226–0234)** | 0211, 0226, 0226-rat, 0226-prac, 0227, 0228, 0229, 0230, 0231, 0232, 0233, 0234 | Phased mega-family (12 files) covering conformal falsification, residual-gated practice loops, compute budget policies, sealed practice traces, and candidate operator boundaries. | `10-stack-dossiers/Batch5-TierA-consolidated.md` §A5.5 |

**35 ADRs at Tier A**, audited in one consolidated subagent pass (`10-stack-dossiers/Batch5-TierA-consolidated.md`).

## Batch 5 — Tier B stacks

| Zone card | Members | Card Output |
|---|---|---|
| B5.1 — Substrate Hardening, Atomicity & Codeowners Governance | 0206, 0207, 0210, 0217, 0219, 0220, 0221 | `11-adr-cards/Batch5-TierB-consolidated.md` §B5.1 |
| B5.2 — Substrate Readiness, Residual Read-Models & Hardware Acceleration | 0222, 0223, 0224, 0225, 0225-res, 0235, 0237 | `11-adr-cards/Batch5-TierB-consolidated.md` §B5.2 |
| B5.3 — Engineering Discipline & Masterful Cleanup | 0236 | `11-adr-cards/Batch5-TierB-consolidated.md` §B5.3 |

**15 ADRs at Tier B**, audited in one consolidated subagent pass (`11-adr-cards/Batch5-TierB-consolidated.md`).

## Batch 6 (ADR-0251–0265) — Tier A stacks

| Stack | Members | Why Tier A | Dossier Output |
|---|---|---|---|
| **A6.1 — Master Convergence & Earned Reliability License Bands** | 0256, 0257, 0258, 0259, 0260, 0261, 0262, 0263, 0264, 0265 | Phased mega-family (10 files) establishing deduction serving under earned reliability licenses across Bands v2-EN through v6-EX, curriculum-grounded serving, ratified-ledger bridges, negative curriculum, and proposition-graph negation. | `10-stack-dossiers/Batch6-TierA-consolidated.md` §A6.1 |
| **A6.2 — Reader Arc Recalibration & Master Blueprint Governance** | 0251, 0252, 0253, 0254, 0255 | Phased family (5 files) establishing reader arc recalibration, problem-solving paradigm consolidation, Master Blueprint ADR collision resolution (INV-33 dual-pack serve boundary), grounded-open hedge arms, and discovery-yield telemetry. | `10-stack-dossiers/Batch6-TierA-consolidated.md` §A6.2 |

**15 ADRs at Tier A**, audited in one consolidated subagent pass (`10-stack-dossiers/Batch6-TierA-consolidated.md`).

**Batch 6 total: 15 (A) + 0 (B) + 0 (C) = 15.** Verified against `01-adr-census.md`'s Batch 6 row count.




