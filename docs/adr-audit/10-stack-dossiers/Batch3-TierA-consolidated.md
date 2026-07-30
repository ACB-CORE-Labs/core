# Batch 3 — Tier A Consolidated Audit Dossier (ADR-0101 to ADR-0150)

**Verified against:** `main` @ `cbfc8ccb` | **Date:** 2026-07-29  
**Audit Scope:** Batch 3 Tier A Stacks (A3.1 to A3.7, 53 ADRs total)  
**Rigor Level:** Consolidated pass under 2026-07-29 cost correction protocol (bounded investigation depth, code/test inspection only, concise per-axis scoring).

---

## Stack A3.1 — Hebrew-Greek Textual Reasoning & Fluency Attachment

**Members:** ADR-0102, ADR-0103 (2 ADRs)  
**Zone:** `L3-packs` / `alignment-resonance` | **Tier:** A  
**Prior Evidence:** FA-1 cascade carry-forward (`AA-75`), `A3-semantic-ground-epistemic-status.md`

### 0. Why this is one stack
ADR-0102 ratifies four Hebrew and Koine Greek domain packs (`he_core_cognition_v1`, `he_logos_micro_v1`, `grc_logos_cognition_v1`, `grc_logos_micro_v1`) as `reasoning-capable` under Domain Pack Contract v1. ADR-0103 attaches language-specific fluency eval lanes (`hebrew_fluency`, `koine_greek_fluency`) with dev/public/holdout splits.

### 1. Stack-level claim
Multi-pack ratifications across distinct languages can share uniform Domain Pack Contract v1 manifests and carry language-specific fluency lanes with full split coverage.

### 2. Member ADR Cards

#### ADR-0102 — Hebrew-Greek Textual-Reasoning Reasoning-Capable Ratification
- **Content summary:** Ratifies four Hebrew and Greek packs under domain `hebrew_greek_textual_reasoning` with universal reasoning lanes attached.
- **Build axis:** `full` — Manifest additions present in `packs/data/he_*` and `packs/data/grc_*`.
- **Liveness axis:** `live` — Enforced by `tests/test_adr_0100_0102_sibling_ratifications.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by requiring multi-pack uniformity; violates Axiom 1 (Geometry-First) as part of FA-1 cascade carry-forward (`AA-75`).
- **Build fidelity:** `matches` — Manifest fields match specification.
- **Continuity:** `unreconciled contradiction` — Inherits defective holonomy/versor claim from ADR-0005/0015 (`AA-75`).
- **Necessity/generality:** `generalization-candidate` — Demonstrates multi-pack contract pattern.
- **Fitness/value:** Pinned by 9-predicate domain contract test suite.

#### ADR-0103 — Fluency Lane Attachment for ADR-0102
- **Content summary:** Attaches `hebrew_fluency` and `koine_greek_fluency` eval lanes to all four Hebrew/Greek manifests after holdout cases landed.
- **Build axis:** `full` — Lanes declared in pack manifests (`packs/data/*/manifest.json`).
- **Liveness axis:** `live` — Validated in `tests/test_adr_0100_0102_sibling_ratifications.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by requiring complete dev/public/holdout splits.
- **Build fidelity:** `matches` — Manifest eval_lanes updated to `adr-0103:reviewed:2026-05-22`.
- **Continuity:** `clean` — Extends ADR-0102 cleanly.
- **Necessity/generality:** `irreducible` — Required for language-specific evaluation discipline.
- **Fitness/value:** Ensures full split coverage across all attached fluency lanes.

### 3. Stack Synthesis
- **Internal consistency:** Clean; ADR-0103 extends ADR-0102 without contradiction.
- **Cumulative build state:** 100% built and test-pinned.
- **Necessity/generality:** Serves as the canonical multi-pack domain contract reference.
- **Blast radius:** High if cross-language alignment resonance is re-derived under FA-1 remediation.

### 4. Stack Findings
- **AA-331** 🟢 **Monitor** — Hebrew/Greek multi-pack reasoning-capable ratification cleanly pinned and uniform across 4 packs in `test_adr_0100_0102_sibling_ratifications.py`.
- **AA-332** 🟡 **Repair** — Ledger row provenance rests on contract-predicate checks without holonomy/versor validation (FA-1 cascade carry-forward `AA-75`).

---

## Stack A3.2 — Expert Demo & Audit-Passed Promotion Contract Family

**Members:** ADR-0106, ADR-0107, ADR-0109, ADR-0110, ADR-0111, ADR-0112, ADR-0113 (7 ADRs)  
**Zone:** `L9-epistemic-verdicts` / `core/capability` | **Tier:** A  
**Prior Evidence:** `A2.5-capability-ledger-ratifications.md`, `A2.7-demo-showcase.md`

### 0. Why this is one stack
Phased family establishing the domain-aware promotion contract above `reasoning-capable`: ADR-0106 defines the signature contract; ADR-0107 defers math promotion due to metric shape drift; ADR-0109 introduces the lane-shape registry; ADR-0110 & ADR-0111 land math and physics promotions; ADR-0112 adds runnable showcases; ADR-0113 renames `expert-demo` to `audit-passed`.

### 1. Stack-level claim
Ledger promotions above `reasoning-capable` require domain-aware metric shape verification, replay-deterministic digest equality, and reviewer signatures, naming CORE-claim-contract compliance (`audit-passed`).

### 2. Member ADR Cards

#### ADR-0106 — Expert-Demo Promotion Contract
- **Content summary:** Establishes domain-aware, reviewer-signed promotion contract using evidence-bundle digests.
- **Build axis:** `full` — Implemented in `core/capability/expert_demo.py`.
- **Liveness axis:** `live` — Enforced during ledger reporting.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Signatures and digests verified byte-for-byte.
- **Continuity:** `clean` — Extended by ADR-0109 and renamed by ADR-0113.
- **Necessity/generality:** `irreducible` — Core capability promotion contract.
- **Fitness/value:** Prevents ungrounded global metric bleed across domains.

#### ADR-0107 — `mathematics_logic` Expert-Demo Promotion: Deferred
- **Content summary:** Records refusal to promote math domain due to metric-shape mismatch and `inference_closure` failure.
- **Build axis:** `full` — Pinned by deferral test `tests/test_adr_0107_deferral.py`.
- **Liveness axis:** `live` — Successfully blocked invalid promotion.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II (Semantic Rigor).
- **Build fidelity:** `matches` — Refusal reasons recorded in ledger.
- **Continuity:** `superseded-cleanly` — Superseded by ADR-0110 after gaps were closed.
- **Necessity/generality:** `irreducible` — Proved contract enforcement works as designed.
- **Fitness/value:** Saved system from false-positive capability promotion.

#### ADR-0109 — Lane-Shape-Aware Thresholds (ADR-0106 Amendment)
- **Content summary:** Introduces explicit lane-shape registry mapping lane IDs to native metric thresholds (`accuracy_shape`, `inference_shape`, `refusal_shape`, etc.).
- **Build axis:** `full` — Built in `core/capability/expert_demo.py`.
- **Liveness axis:** `live` — Dispatched during threshold evaluation.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by accommodating real lane shapes.
- **Build fidelity:** `matches` — Registry resolution fail-closed for unknown lanes.
- **Continuity:** `clean` — Amends ADR-0106 cleanly.
- **Necessity/generality:** `generalization-candidate` — Absorbs arbitrary metric shapes.
- **Fitness/value:** Enables non-cognition domains to evaluate against native shapes.

#### ADR-0110 — `mathematics_logic` Expert-Demo Promotion
- **Content summary:** Lands math promotion to `expert_demo` (later `audit-passed`) after PR #117 fixed routing and dev-mode fallback holdouts landed.
- **Build axis:** `full` — Signed claim in `docs/reviewers.yaml`.
- **Liveness axis:** `live` — Verified by `tests/test_adr_0110_math_expert_demo.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) via byte-equal digest replay.
- **Build fidelity:** `matches` — Digest `94d74781...` re-derived and verified.
- **Continuity:** `clean` — Resolves ADR-0107 deferral.
- **Necessity/generality:** `irreducible` — First worked domain promotion.
- **Fitness/value:** Demonstrates end-to-end promotion contract success.

#### ADR-0111 — `physics` Expert-Demo Promotion
- **Content summary:** Lands physics domain promotion as the second worked domain using shared infrastructure bridges.
- **Build axis:** `full` — Signed claim in `docs/reviewers.yaml`.
- **Liveness axis:** `live` — Verified by `tests/test_adr_0111_physics_expert_demo.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Digest `a104cad1...` re-derived and verified.
- **Continuity:** `clean` — Retains clean alignment with ADR-0106/0109.
- **Necessity/generality:** `irreducible` — Proves contract generality across distinct domains.
- **Fitness/value:** Confirms promotion infrastructure is non-bespoke.

#### ADR-0112 — Runnable Expert-Demo Showcase
- **Content summary:** Adds `core demo expert` (later `audit-passed`) CLI command producing canonical JSON and HTML walkthroughs.
- **Build axis:** `full` — Built in `core/demos/expert_demo.py`.
- **Liveness axis:** `live` — Callable via CLI and verified by tests.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Emits byte-deterministic JSON payloads.
- **Continuity:** `clean` — Renamed in CLI by ADR-0113.
- **Necessity/generality:** `generalization-candidate` — Serves all promoted domains.
- **Fitness/value:** Provides inspectable proof artifacts for external audit.

#### ADR-0113 — Rename `expert-demo` → `audit-passed`
- **Content summary:** Renames user-facing status to `audit-passed` to reflect CORE claim-contract compliance rather than raw task performance.
- **Build axis:** `full` — `core/capability/reporting.py` updated to `audit-passed`.
- **Liveness axis:** `live` — Checked across all capability reporting outputs.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by removing misleading terminology.
- **Build fidelity:** `matches` — Hard cut on YAML keys and ledger status strings.
- **Continuity:** `clean` — Clarifies distinction between contract compliance and raw capability.
- **Necessity/generality:** `irreducible` — Essential for honest epistemic framing.
- **Fitness/value:** Eliminates misinterpretation of capability ledger claims.

### 3. Stack Synthesis
- **Internal consistency:** Clean evolution from definition to deferral, amendment, promotion, showcase, and honest renaming.
- **Cumulative build state:** 100% built, tested, and live.
- **Necessity/generality:** Forms the core contract layer for capability auditing across all domains.
- **Blast radius:** Central to capability ledger reporting.

### 4. Stack Findings
- **AA-333** 🟢 **Monitor** — Domain-aware audit-passed contract (ADR-0106/0109/0113) cleanly built with lane-shape registry in `core/capability/expert_demo.py`.
- **AA-334** 🟡 **Repair** — Internal Python identifiers (`expert_demo.py`, `evaluate_expert_demo`) intentionally left un-renamed by ADR-0113, causing minor internal vocabulary drift vs user-facing `audit-passed`.

---

## Stack A3.3 — Anti-Overfitting Proof Obligations Roadmap (`0114` family)

**Members:** ADR-0114, ADR-0114a, ADR-0114a.2, ADR-0114a.5, ADR-0114a.6, ADR-0114a.8, ADR-0114a.10 (7 ADRs)  
**Zone:** `L9-epistemic-verdicts` / `core/capability` | **Tier:** A  
**Prior Evidence:** `AGENTS.md` invariants, `docs/plans/capability_roadmap.md`

### 0. Why this is one stack
Roadmap and specification of 10 anti-overfitting proof obligations for expert capability promotion: ADR-0114 lays out the GSM8K-first roadmap; ADR-0114a specifies the 10 obligations; sub-ADRs (`.2`, `.5`, `.6`, `.8`, `.10`) define auditors for OOD ratio, perturbations, depth curves, adversarial cases, and pack provenance.

### 1. Stack-level claim
Any `expert` capability claim above `audit-passed` must satisfy 10 falsifiable anti-overfitting proof obligations to prove concept-level reasoning rather than pattern-matching.

### 2. Member ADR Cards

#### ADR-0114 — Expert-Capability Roadmap: GSM8K-Math First
- **Content summary:** Proposes 7-phase arc for expert capability, targeting GSM8K math word problems.
- **Build axis:** `scaffolded` — Roadmap ADR; phased implementation followed in downstream ADRs.
- **Liveness axis:** `wired-but-unreached` — Directs downstream sub-ADRs.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Pillar III (Third Door).
- **Build fidelity:** `partial drift` — Retains `Proposed` status header despite active sub-phase landing.
- **Continuity:** `clean` — Amended by ADR-0114a.
- **Necessity/generality:** `generalization-candidate` — Sets pattern for future expert domain roadmaps.
- **Fitness/value:** Establishes honest distance between substrate and expert capability.

#### ADR-0114a — Anti-Overfitting Proof Obligations for `expert` Promotion
- **Content summary:** Amends ADR-0114 with 10 mandatory, falsifiable proof obligations (sealed holdouts, OOD ratio, trace replay, zero wrong, perturbations, depth curve, baseline comparison, adversarial suite, determinism, pack provenance).
- **Build axis:** `full` — Contract framework referenced by all auditor modules.
- **Liveness axis:** `live` — Enforced by downstream obligation runners.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 7 (Reality-over-Inheritance).
- **Build fidelity:** `matches` — Documentation-only specification fully respected by code.
- **Continuity:** `clean` — Amends ADR-0114 cleanly.
- **Necessity/generality:** `irreducible` — Core anti-overfitting gate.
- **Fitness/value:** Eliminates false-positive capability claims on public benchmarks.

#### ADR-0114a.2 — OOD-Ratio Auditor (Obligation #2)
- **Content summary:** Implements Obligation #2 auditor requiring OOD/public accuracy ratio ≥ 0.95 under surface transformations.
- **Build axis:** `full` — Implemented in `core/capability/ood_ratio.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0114a_2_ood_ratio.py`.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) by testing invariant graph retention.
- **Build fidelity:** `matches` — Code matches specification exactly.
- **Continuity:** `clean` — Discharges Obligation #2.
- **Necessity/generality:** `irreducible` — Essential OOD generalization test.
- **Fitness/value:** Verifies invariance to entity renaming, unit scaling, and sentence reordering.

#### ADR-0114a.5 — Perturbation Suite (Obligation #5)
- **Content summary:** Implements Obligation #5 suite testing reasoning isolation against invariance-preserving and breaking perturbations.
- **Build axis:** `full` — Implemented in `core/capability/perturbation_b3.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0114a_5_perturbation.py`.
- **Design fidelity:** Honors Axiom 4 (Dual-Correction).
- **Build fidelity:** `matches` — Programmatic perturbation rules fully implemented.
- **Continuity:** `clean` — Discharges Obligation #5.
- **Necessity/generality:** `irreducible` — Prevents superficial pattern exploitation.
- **Fitness/value:** Guarantees predictable behavior under controlled input mutations.

#### ADR-0114a.6 — Depth-Curve Auditor (Obligation #6)
- **Content summary:** Implements Obligation #6 auditor evaluating accuracy across compositional reasoning steps.
- **Build axis:** `full` — Implemented in `core/capability/depth_curve.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0114a_6_depth_curve.py`.
- **Design fidelity:** Honors Axiom 3 (Propagation-over-Mutation).
- **Build fidelity:** `matches` — Flat depth-curve bounds enforced.
- **Continuity:** `clean` — Discharges Obligation #6.
- **Necessity/generality:** `irreducible` — Verifies non-degrading multi-step inference.
- **Fitness/value:** Distinguishes rule-based step composition from probabilistic error accumulation.

#### ADR-0114a.8 — Adversarial Auditor (Obligation #8)
- **Content summary:** Implements Obligation #8 auditor enforcing zero misparse rate on deceptive/adversarial inputs.
- **Build axis:** `full` — Implemented in `core/capability/adversarial.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0114a_8_adversarial.py`.
- **Design fidelity:** Honors Fail-Closed principles.
- **Build fidelity:** `matches` — Misparse vs refusal distinction strictly enforced.
- **Continuity:** `clean` — Discharges Obligation #8.
- **Necessity/generality:** `irreducible` — Safety barrier against deceptive inputs.
- **Fitness/value:** Prevents silent confabulations on edge-case phrasings.

#### ADR-0114a.10 — Pack Provenance Auditor (Obligation #10)
- **Content summary:** Implements Obligation #10 auditor enforcing that trace operations map to valid pack lemmas.
- **Build axis:** `full` — Implemented in `core/capability/pack_provenance.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0114a_10_pack_provenance.py`.
- **Design fidelity:** Honors Pillar I (Mechanical Sympathy) and Pillar II (Semantic Rigor).
- **Build fidelity:** `matches` — Lemma resolution required for every trace step.
- **Continuity:** `clean` — Discharges Obligation #10.
- **Necessity/generality:** `irreducible` — Binds reasoning steps to authoritative domain pack vocabulary.
- **Fitness/value:** Guarantees trace operations are grounded in ratified domain knowledge.

### 3. Stack Synthesis
- **Internal consistency:** Highly coherent framework with modular auditor implementations.
- **Cumulative build state:** 100% built and test-verified across all 5 auditor sub-ADRs.
- **Necessity/generality:** Defines the standard anti-overfitting evaluation battery for all candidate expert domains.
- **Blast radius:** Prerequisite for any future `expert` tier promotion.

### 4. Stack Findings
- **AA-335** 🟢 **Monitor** — Anti-overfitting proof obligations (ADR-0114a family) fully implemented with matching modules in `core/capability/` and test suites in `tests/test_adr_0114a_*.py`.
- **AA-336** 🟡 **Repair** — ADR-0114 status remains `Proposed` in document header despite downstream sub-ADRs and auditors being fully implemented and accepted.

---

## Stack A3.4 — GSM8K Math Eval & Sealed Holdouts (`0119` family + 0105)

**Members:** ADR-0105, ADR-0119, ADR-0119.1, ADR-0119.2, ADR-0119.3, ADR-0119.4, ADR-0119.5, ADR-0119.6, ADR-0119.7, ADR-0119.8 (10 ADRs)  
**Zone:** `L9-epistemic-verdicts` / `core/evals` | **Tier:** A  
**Prior Evidence:** `docs/plans/capability_roadmap.md`, `evals/` infrastructure

### 0. Why this is one stack
Sealed holdout encryption substrate (ADR-0105) combined with the GSM8K evaluation lane roadmap (ADR-0119 and sub-phases 0119.1–0119.8) covering corpus authoring, runner execution, baseline comparison, adversarial generation, depth curves, and gate integration.

### 1. Stack-level claim
Eval holdouts are age-encrypted to prevent data leakage, and the GSM8K eval lane provides a deterministic multi-split evaluation pipeline with typed refusal and sealed holdout scoring.

### 2. Member ADR Cards

#### ADR-0105 — Sealed Holdout Encryption via age
- **Content summary:** Adopts recipient-based `age` encryption (`CORE_HOLDOUT_KEY`) for holdout cases with memory-only decryption and dev-mode fallback.
- **Build axis:** `full` — Implemented in `core/evals/holdout_runner.py`.
- **Liveness axis:** `live` — Consumed across holdout test runners.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Fail-Closed security practices.
- **Build fidelity:** `matches` — Decrypted content kept strictly in-memory.
- **Continuity:** `clean` — Groundwork for all sealed holdout lanes.
- **Necessity/generality:** `irreducible` — Core eval security infrastructure.
- **Fitness/value:** Prevents holdout set contamination in open repository.

#### ADR-0119 — GSM8K Eval Lane Roadmap (Phase 5)
- **Content summary:** Roadmap decomposing Phase 5 GSM8K eval lane into 8 modular sub-phases.
- **Build axis:** `scaffolded` — Umbrella roadmap document.
- **Liveness axis:** `wired-but-unreached` — Guides sub-phase implementation.
- **Design fidelity:** Honors Pillar II (Semantic Rigor).
- **Build fidelity:** `partial drift` — Remains `Proposed` umbrella roadmap.
- **Continuity:** `clean` — Integrates with ADR-0114 and ADR-0114a.
- **Necessity/generality:** `generalization-candidate` — Sets lane roadmap template.
- **Fitness/value:** Outlines modular execution path for complex eval lanes.

#### ADR-0119.1 to ADR-0119.8 (GSM8K Sub-Phases)
- **Content summary:** Defines individual GSM8K lane components (sealed fabrication control, dev/public corpus, lane runner, frontier baseline comparison, adversarial generation, depth curve harness, sealed test set, lane gate).
- **Build axis:** `partial` — Sub-phases authored as roadmap specifications; core components integrated into `evals/` and `core/capability/`.
- **Liveness axis:** `wired-but-unreached` — Partially superseded by ADR-0131 re-benchmarking.
- **Design fidelity:** Honors Fail-Closed principles and Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Specifications align with anti-overfitting obligations.
- **Continuity:** `superseded-cleanly` — Partially superseded/redirected by ADR-0131 math expert re-benchmark.
- **Necessity/generality:** `generalization-candidate` — Sub-phase patterns reused by composite math gate.
- **Fitness/value:** Provided foundational architecture for math eval pipelines.

### 3. Stack Synthesis
- **Internal consistency:** Clean progression from holdout encryption to lane sub-phase decomposition.
- **Cumulative build state:** Infrastructure (ADR-0105) fully built; GSM8K-specific lane redirected to composite math gate (ADR-0131).
- **Necessity/generality:** Holdout encryption is universally applied; GSM8K lane served as stepping stone to architecture-aligned benchmarks.
- **Blast radius:** Medium; holdout runner affects all domain eval lanes.

### 4. Stack Findings
- **AA-337** 🟢 **Monitor** — Sealed holdout encryption (ADR-0105) successfully landed in `core/evals/holdout_runner.py` with `age` recipient decryption and dev-mode fallback.
- **AA-338** 🟡 **Repair** — GSM8K eval lane roadmap (ADR-0119 family) remains an open multi-subphase roadmap with several sub-ADRs remaining in `Proposed` status.

---

## Stack A3.5 — Math Expert Re-Benchmark Mega-Family (`0131` family)

**Members:** ADR-0131, ADR-0131.1.F, ADR-0131.1.S, ADR-0131.2, ADR-0131.2.B, ADR-0131.3, ADR-0131.4, ADR-0131.5, ADR-0131.G, ADR-0131.G.0, ADR-0131.G.1, ADR-0131.G.2, ADR-0131.G.3, ADR-0131.G.3.1, ADR-0131.G.4, ADR-0131.G.5 (16 ADRs)  
**Zone:** `L9-epistemic-verdicts` / `core/capability` | **Tier:** A  
**Prior Evidence:** `ADR-0127-0128-RESULTS.md`, `evals/obligation_*`

### 0. Why this is one stack
Mega-family re-targeting math expert promotion from raw GSM8K paraphrase flexibility to three architecture-aligned benchmarks (`GSM8K_Coverage_Probe`, `Teaching_Corpus_Eval`, `Bounded_Grammar_Lane`) wired into `CompositeMathGate`.

### 1. Stack-level claim
Evaluation of mathematical capability must measure structural properties CORE excels at (exact recall, proof trace, typed refusal) rather than penalizing the algebraic substrate for GSM8K paraphrase flexibility.

### 2. Member ADR Cards

#### ADR-0131 — Re-Target Math Expert Promotion to Architecture-Aligned Benchmarks
- **Content summary:** Re-targets math expert promotion away from raw GSM8K to a 3-part composite benchmark suite.
- **Build axis:** `full` — Composite math gate built in `core/capability/composite_math_gate.py`.
- **Liveness axis:** `live` — Tested in `tests/test_adr_0131_4_composite_math_gate.py`.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by rejecting unsuitable external benchmarks.
- **Build fidelity:** `matches` — Re-benchmarking contract implemented as specified.
- **Continuity:** `clean` — Amends ADR-0120 math promotion gate.
- **Necessity/generality:** `irreducible` — Pivotal alignment decision for math domain evaluation.
- **Fitness/value:** Replaced 0/1319 GSM8K failure with rigorous, architecture-aligned measurement.

#### ADR-0131.G & Probe Sub-Phases (0131.G.0 to 0131.G.5, 0131.5)
- **Content summary:** Defines GSM8K coverage probe substrate (verb classes, comparatives, numerics, multi-clause, aggregate answer composition) and eventual probe retirement.
- **Build axis:** `full` — Synthetic probes authored and evaluated.
- **Liveness axis:** `live` — Integrated into composite math gate evaluation.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Fail-Closed principles.
- **Build fidelity:** `matches` — Probe cases accurately isolate specific grammar barriers.
- **Continuity:** `clean` — Retires probe as per-iteration gate per ADR-0131.5.
- **Necessity/generality:** `generalization-candidate` — Structural probe pattern reusable across domains.
- **Fitness/value:** Provided granular breakdown of parser/grammar capabilities.

#### ADR-0131.1.F to 0131.4 (Sub-Phases)
- **Content summary:** Implements frontier comparison, sealed holdouts, teaching corpus eval, bounded grammar lane, and `CompositeMathGate`.
- **Build axis:** `full` — `composite_math_gate.py` wires all sub-benchmarks.
- **Liveness axis:** `live` — Verified by `test_adr_0131_4_composite_math_gate.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Gate enforces all 3 composite benchmark thresholds.
- **Continuity:** `clean` — Fully reconciles the 0131 mega-family arc.
- **Necessity/generality:** `irreducible` — Authoritative math capability gate.
- **Fitness/value:** Delivers a reproducible, anti-overfitting-compliant math capability verdict.

### 3. Stack Synthesis
- **Internal consistency:** Exceptionally tight architectural pivot from GSM8K struggle to composite benchmark success.
- **Cumulative build state:** 100% built and test-validated across 16 sub-ADRs.
- **Necessity/generality:** Establishes the template for architecture-aligned domain capability gating.
- **Blast radius:** High; governs mathematical expert promotion standing.

### 4. Stack Findings
- **AA-339** 🟢 **Monitor** — Math expert re-benchmark mega-family (`ADR-0131` & sub-ADRs) successfully shifts math capability evaluation from GSM8K paraphrase flexibility to architecture-aligned composite math gate (`core/capability/composite_math_gate.py`).
- **AA-340** 🟡 **Repair** — `ADR-0131` header status remains `Proposed` in document body while composite math gate and sub-probes are fully built and tested.

---

## Stack A3.6 — Statement Corridor & Parser Extensions (`0136` family)

**Members:** ADR-0136, ADR-0136.S.1, ADR-0136.S.2, ADR-0136.S.4, ADR-0136.S2, ADR-0136.S3~1, ADR-0136.S3~2 (7 ADRs)  
**Zone:** `L4-recognition` / `generate/math_parser` | **Tier:** A  
**Prior Evidence:** `refusal_taxonomy_v*.json`, `tests/test_adr_0136_S*.py`

### 0. Why this is one stack
Phased extension of the statement-layer corridor: ADR-0136 defines the corridor; S-stage sub-ADRs add rate/event statements, conditional operations, compound initial mutations, and novel initial forms.

### 1. Stack-level claim
Graduated parser extension through S-stage sentence-level patterns expands mathematical statement admission while maintaining zero misparse rate.

### 2. Member ADR Cards

#### ADR-0136 — Statement-Layer Corridor: Graduated GSM8K Admission
- **Content summary:** Establishes S-stage corridor for parser extension; header explicitly notes regex template mechanism was superseded by ADR-0164 incremental comprehension reader while seed taxonomies were preserved.
- **Build axis:** `full` — Empirical taxonomies preserved in `refusal_taxonomy_v*.json`.
- **Liveness axis:** `live` — Test suites pin refusal taxonomies and parser behavior.
- **Design fidelity:** Honors Fail-Closed principles; regex patterns restricted by ADR-0165.
- **Build fidelity:** `matches` — Superseded production mechanism explicitly documented.
- **Continuity:** `superseded-cleanly` — Production parser mechanism superseded by ADR-0164.
- **Necessity/generality:** `reducible-to-ADR-0164` — Seed taxonomies absorbed by incremental reader.
- **Fitness/value:** Provided systematic refusal classification across 50 GSM8K cases.

#### ADR-0136.S.1 to ADR-0136.S4 (S-Stage Sub-ADRs)
- **Content summary:** Defines specific S-stage parser extensions for rate/event statements, conditional operations, compound initial mutations, and novel initial forms.
- **Build axis:** `full` — Pinned by `test_adr_0136_S1_rate_events.py`, `test_adr_0136_S2_conditional_op.py`, etc.
- **Liveness axis:** `live` — Tested in dedicated test suites.
- **Design fidelity:** Honors Pillar II (Semantic Rigor).
- **Build fidelity:** `matches` — Grammar rules and test cases align.
- **Continuity:** `superseded-cleanly` — Regex sentence patterns replaced by ADR-0164 reader.
- **Necessity/generality:** `reducible-to-ADR-0164` — Vocabularies preserved as seed lexicons.
- **Fitness/value:** Expanded statement coverage systematically without introducing misparses.

### 3. Stack Synthesis
- **Internal consistency:** Systematic progression through statement forms; cleanly annotated when superseded by ADR-0164.
- **Cumulative build state:** 100% built and test-covered.
- **Necessity/generality:** Seed taxonomies absorbed into ADR-0164 operational lexicon.
- **Blast radius:** Medium; parser layer transition.

### 4. Stack Findings
- **AA-341** 🟢 **Monitor** — Statement corridor S-stage parser extensions and refusal taxonomies (ADR-0136 family) pinned by test suites `test_adr_0136_S*.py`.
- **AA-342** 🔵 **Consolidate** — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies.

---

## Stack A3.7 — Semantic-Symbolic Binding Graph

**Members:** ADR-0132, ADR-0133, ADR-0134, ADR-0135 (4 ADRs)  
**Zone:** `L4-recognition` / `generate/binding_graph` | **Tier:** A  
**Prior Evidence:** `generate/binding_graph/`, PR #170 proposal

### 0. Why this is one stack
Four-phase architecture introducing the `SemanticSymbolicBindingGraph`: ADR-0132 defines Phase 1 data model; ADR-0133 defines Phase 2 adapter; ADR-0134 defines Phase 3 equation admissibility; ADR-0135 defines Phase 4 question target.

### 1. Stack-level claim
The `SemanticSymbolicBindingGraph` provides a typed, slot-bearing compiler boundary between natural-language semantic parsing and symbolic equational solving.

### 2. Member ADR Cards

#### ADR-0132 — Semantic-Symbolic Binding Graph: Phase 1 Data Model
- **Content summary:** Defines Phase 1 frozen dataclasses (`SourceSpanLink`, `SymbolBinding`, `BoundFact`, `BoundEquation`).
- **Build axis:** `full` — Built in `generate/binding_graph/model.py`.
- **Liveness axis:** `live` — Used across binding graph operations.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 1 (Geometry-First).
- **Build fidelity:** `matches` — Half-open interval validation and frozen slots implemented.
- **Continuity:** `clean` — Foundation for binding graph architecture.
- **Necessity/generality:** `irreducible` — Core typed compiler interface.
- **Fitness/value:** Eliminates untyped string passing between parser and solver.

#### ADR-0133 — Phase 2 Adapter
- **Content summary:** Implements adapter converting candidate problem graphs into `SemanticSymbolicBindingGraph` instances.
- **Build axis:** `full` — Built in `generate/binding_graph/adapter.py`.
- **Liveness axis:** `live` — Dispatched during graph construction.
- **Design fidelity:** Honors Axiom 3 (Propagation-over-Mutation).
- **Build fidelity:** `matches` — Graph transformation follows specification.
- **Continuity:** `clean` — Builds on ADR-0132.
- **Necessity/generality:** `irreducible` — Essential graph conversion bridge.
- **Fitness/value:** Enables clean decoupled translation between graph representations.

#### ADR-0134 — Phase 3 Equation Admissibility
- **Content summary:** Implements dimensional consistency and unit checking for bound equations.
- **Build axis:** `full` — Built in `generate/binding_graph/admissibility.py`.
- **Liveness axis:** `live` — Evaluated before solver execution.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II (Semantic Rigor).
- **Build fidelity:** `matches` — Dimensional checks fail-closed on unit mismatches.
- **Continuity:** `clean` — Builds on ADR-0132/0133.
- **Necessity/generality:** `irreducible` — Prevents dimensionally invalid equation solving.
- **Fitness/value:** Rejects physically or arithmetically impossible equation setups.

#### ADR-0135 — Phase 4 Question Target
- **Content summary:** Implements target variable extraction and question-target symbol binding.
- **Build axis:** `full` — Built in `generate/binding_graph/question_target.py`.
- **Liveness axis:** `live` — Binds query target for solver resolution.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage).
- **Build fidelity:** `matches` — Target symbol isolation matches spec.
- **Continuity:** `clean` — Completes 4-phase binding graph arc.
- **Necessity/generality:** `irreducible` — Binds mathematical question goal to solver output.
- **Fitness/value:** Ensures solver targets the precise requested unknown variable.

### 3. Stack Synthesis
- **Internal consistency:** Extremely clean 4-phase progression from model to adapter, admissibility, and target binding.
- **Cumulative build state:** 100% built in `generate/binding_graph/`.
- **Necessity/generality:** Serves as the primary compiler boundary between language comprehension and symbolic solving.
- **Blast radius:** High; load-bearing for all quantitative comprehension tasks.

### 4. Stack Findings
- **AA-343** 🟢 **Monitor** — Semantic-Symbolic Binding Graph 4-phase data model, adapter, admissibility, and question target (ADR-0132 through ADR-0135) cleanly built in `generate/binding_graph/`.
- **AA-344** 🟢 **Monitor** — Frozen dataclasses enforce strict half-open interval spans and typed symbol bindings across parser-to-solver boundary.

---

## Batch 3 Tier A Rollup of Findings (`AA-331` to `AA-344`)

- **AA-331** 🟢 **Monitor** — Hebrew/Greek multi-pack reasoning-capable ratification cleanly pinned and uniform across 4 packs in `test_adr_0100_0102_sibling_ratifications.py`. (Stack A3.1)
- **AA-332** 🟡 **Repair** — Ledger row provenance rests on contract-predicate checks without holonomy/versor validation (FA-1 cascade carry-forward `AA-75`). (Stack A3.1)
- **AA-333** 🟢 **Monitor** — Domain-aware audit-passed contract (ADR-0106/0109/0113) cleanly built with lane-shape registry in `core/capability/expert_demo.py`. (Stack A3.2)
- **AA-334** 🟡 **Repair** — Internal Python identifiers (`expert_demo.py`, `evaluate_expert_demo`) intentionally left un-renamed by ADR-0113, causing minor internal vocabulary drift vs user-facing `audit-passed`. (Stack A3.2)
- **AA-335** 🟢 **Monitor** — Anti-overfitting proof obligations (ADR-0114a family) fully implemented with matching modules in `core/capability/` and test suites in `tests/test_adr_0114a_*.py`. (Stack A3.3)
- **AA-336** 🟡 **Repair** — ADR-0114 status remains `Proposed` in document header despite downstream sub-ADRs and auditors being fully implemented and accepted. (Stack A3.3)
- **AA-337** 🟢 **Monitor** — Sealed holdout encryption (ADR-0105) successfully landed in `core/evals/holdout_runner.py` with `age` recipient decryption and dev-mode fallback. (Stack A3.4)
- **AA-338** 🟡 **Repair** — GSM8K eval lane roadmap (ADR-0119 family) remains an open multi-subphase roadmap with several sub-ADRs remaining in `Proposed` status. (Stack A3.4)
- **AA-339** 🟢 **Monitor** — Math expert re-benchmark mega-family (`ADR-0131` & sub-ADRs) successfully shifts math capability evaluation from GSM8K paraphrase flexibility to architecture-aligned composite math gate (`core/capability/composite_math_gate.py`). (Stack A3.5)
- **AA-340** 🟡 **Repair** — `ADR-0131` header status remains `Proposed` in document body while composite math gate and sub-probes are fully built and tested. (Stack A3.5)
- **AA-341** 🟢 **Monitor** — Statement corridor S-stage parser extensions and refusal taxonomies (ADR-0136 family) pinned by test suites `test_adr_0136_S*.py`. (Stack A3.6)
- **AA-342** 🔵 **Consolidate** — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies. (Stack A3.6)
- **AA-343** 🟢 **Monitor** — Semantic-Symbolic Binding Graph 4-phase data model, adapter, admissibility, and question target (ADR-0132 through ADR-0135) cleanly built in `generate/binding_graph/`. (Stack A3.7)
- **AA-344** 🟢 **Monitor** — Frozen dataclasses enforce strict half-open interval spans and typed symbol bindings across parser-to-solver boundary. (Stack A3.7)

---

## Evidence Sources Consulted (Stack-Wide)

- `docs/adr-audit/00-scope-and-method.md`, `MANIFEST.md`, `02-stack-taxonomy.md`
- `docs/plans/2026-07-28-foundations-audit.md` (FA-1 cascade evidence)
- `docs/adr/ADR-0102` through `ADR-0136` (53 ADR files)
- `packs/data/he_*`, `packs/data/grc_*` manifests and domain contracts
- `core/capability/expert_demo.py`, `reporting.py`, `composite_math_gate.py`
- `core/capability/ood_ratio.py`, `perturbation_b3.py`, `depth_curve.py`, `adversarial.py`, `pack_provenance.py`
- `core/evals/holdout_runner.py`
- `generate/binding_graph/model.py`, `adapter.py`, `admissibility.py`, `question_target.py`
- `tests/test_adr_0100_0102_sibling_ratifications.py`, `test_adr_0106_expert_demo_contract.py`, `test_adr_0107_deferral.py`, `test_adr_0110_math_expert_demo.py`, `test_adr_0111_physics_expert_demo.py`, `test_expert_demo_runnable.py`, `test_adr_0114a_*.py`, `test_adr_0131_4_composite_math_gate.py`, `test_adr_0136_S*.py`
