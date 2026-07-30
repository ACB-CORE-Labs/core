# Phase 1 — ADR Census

**Verified against:** `main` @ `cbfc8ccb` (full SHA `cbfc8ccbf7fe503ab31abe7aedbb1973ba7d7b4d`). **Generated:** mechanically, from `docs/adr/*.md` filenames and headers — this is a first-pass extraction, not a read of any ADR's substance (that's Phase 3). Re-run and re-diff against this file whenever the corpus moves.

Governed by [`00-scope-and-method.md`](00-scope-and-method.md). Feeds [`02-stack-taxonomy.md`](02-stack-taxonomy.md).

## Summary

- **314 ADR-numbered files**, **19 non-ADR files** co-located in `docs/adr/` (333 total).
- Numbering range **ADR-0001–ADR-0265**, **252 distinct top-level numbers**, **13 gaps**: 0079, 0081, 0086, 0137, 0147, 0171, 0187, 0188, 0190, 0212, 0213, 0214, 0215.
- **11 numbers carry true collisions** (≥2 unrelated files, no disambiguating suffix) — see §1.
- **11 numbers anchor phased sub-decision families** (letter/dot-suffixed) — see §2.
- **All 314 files carry an extractable Status field**, but only after normalizing across at least **4 distinct header conventions** in live use (`**Status:**` inline, plain `Status:` inline, table-row `| Status | value |`, and `## Status` heading-with-value-on-next-line) plus assorted bold/parenthetical variations within each. This formatting drift across the corpus is itself a first-class finding, logged as `AA-1` in the finding register (§4 of the plan) — not blocking, but a direct instance of the record-format inconsistency `AGENTS.md` names as a defect class.

This repairs the count in `docs/adr/INDEX-by-domain.md`, which states "312 files" — already two behind the live 314 at the time that index was last touched. Folded into the Phase 4 index repair.

## 1. True numbering collisions (11) — audit-internal disambiguation

These numbers carry ≥2 files with **no** letter/dot suffix distinguishing them — i.e., not a phased family, a genuine numbering accident. Per `ADR-0225` ("repository history wins for IDs") and this plan's non-goals, **no files are renamed**. The `Audit ID` column is bookkeeping-only, used nowhere except this audit's own cross-references, and uses a `~N` marker specifically so it can never be confused with a real corpus suffix (several of these numbers, e.g. `0123`, already have a *real* lettered variant elsewhere — `0123a` — so reusing letters here would create a second, worse collision).

| Number | Audit ID | File | Status | Notes |
|---|---|---|---|---|
| 0078 | `0078~1` | `ADR-0078-composer-graph-atom-equivalence.md` | Ratified |  |
| 0078 | `0078~2` | `ADR-0078-phase1-implementation-note.md` | Note (no formal status field — pre-implementation planning note) |  |
| 0120 | `0120~1` | `ADR-0120-expert-promotion-contract.md` | Proposed (contract-only; no domain promoted with this ADR) |  |
| 0120 | `0120~2` | `ADR-0120-math-expert-ledger-flip.md` | Accepted — first `expert`-tier domain in the capability ledger |  |
| 0120 | `0120~3` | `ADR-0120-math-expert-promotion-wireup.md` | Accepted (technical pass on first evaluation; awaiting reviewer signature for ledger admission) |  |
| 0122 | `0122~1` | `ADR-0122-parser-rate-per-unit.md` | Accepted (substrate landed; sealed-lift gate deferred — the |  |
| 0122 | `0122~2` | `ADR-0122-systems-software-audit-passed-deferred.md` | Accepted (decision: defer promotion) |  |
| 0123 | `0123~1` | `ADR-0123-parser-comparison-phrasing.md` | Accepted (surface increment; substrate landed in PR #155) |  |
| 0123 | `0123~2` | `ADR-0123-symbolic-logic-shape-remap.md` | Accepted |  |
| 0123 | `0123~3` | `ADR-0123a-inference-shape-synonym.md` | Accepted |  |
| 0127 | `0127~1` | `ADR-0127-0128-RESULTS.md` | Empirical result; load-bearing for the GSM8K-math arc decision | results companion doc, not itself a decision record |
| 0127 | `0127~2` | `ADR-0127-units-pack-and-units-aware-parser.md` | Proposed (scope-only; implementation follow-up to ADR-0126) |  |
| 0140 | `0140~1` | `ADR-0140-core-trace-protocol-v0.md` | Proposed |  |
| 0140 | `0140~2` | `ADR-0140-subtract-and-additive-group-closure.md` | Draft |  |
| 0163 | `0163~1` | `ADR-0163-F2-confuser-corpus-spec.md` | Proposed (spec only — no code). Follow-on to ADR-0163 §F (the Track-B |  |
| 0163 | `0163~2` | `ADR-0163-gsm8k-path-to-mastery.md` | Proposed — *Phases B–E prescription superseded by [ADR-0164](./ADR-0164-incremental-comprehension-reader.md) (2026-05-26 |  |
| 0178 | `0178~1` | `ADR-0178-GB3b-referent-accumulation-scope.md` | Proposed (scope only — no code). Sub-phase of |  |
| 0178 | `0178~2` | `ADR-0178-compositional-structure.md` | Accepted (ratified by ADR-0207, 2026-06-03) |  |
| 0184 | `0184~1` | `ADR-0184-distinct-unit-product-rule.md` | Accepted / Implemented. Implementation refined the mechanism: the rule |  |
| 0184 | `0184~2` | `ADR-0184-scoped-semantic-state-transitions.md` | Proposed |  |
| 0225 | `0225~1` | `ADR-0225-adr-corpus-hygiene.md` | Accepted (2026-06-30) | the numbering-governance ADR itself is one of the two collisions at its own number |
| 0225 | `0225~2` | `ADR-0225-contract-residual-read-model.md` | Accepted |  |
| 0226 | `0226~1` | `ADR-0226-gsm8k-math-eval-corpus.md` | Accepted |  |
| 0226 | `0226~2` | `ADR-0226-ratification.md` | Accepted |  |
| 0226 | `0226~3` | `ADR-0226-residual-gated-practice-loop-v1.md` | Proposed |  |

Additionally, within the `0136` phased family, two files independently claim the same sub-suffix `.S3` (`ADR-0136.S3-compound-initial-mutation.md` and `ADR-0136.S3-post-rescan.md`) — a second-order collision inside an otherwise well-formed phased family. Audit IDs: `0136.S3~1` (compound-initial-mutation), `0136.S3~2` (post-rescan).

## 2. Phased sub-decision families (11 base numbers, 60 files)

Letter- or dot-suffixed variants of one base number are a **sequential decision chain**, not independent ADRs — Phase 2/3 treats each as one stack regardless of which zone it lands in.

| Base | Base title | Variant count | Suffixes |
|---|---|---|---|
| 0073 | Anchor lens: substrate-driven substantive variation | 5 | a, b, c, d |
| 0114 | Expert-Capability Roadmap: GSM8K-Math First | 7 | a, a.2, a.5, a.6, a.8, a.10 |
| 0118 | Stepped Realizer (`SolutionTrace` → Prose) | 2 | a |
| 0119 | GSM8K Eval Lane Roadmap (Phase 5) | 9 | .1, .2, .3, .4, .5, .6, .7, .8 |
| 0131 | Re-Target Math Expert Promotion to Architecture-Aligned Benchmarks | 16 | .2, .3, .4, .5, .G, .1.F, .1.S, .2.B, .G.0, .G.1, .G.2, .G.3, .G.4, .G.5, .G.3.1 |
| 0136 | Statement-Layer Corridor: Graduated GSM8K Admission via Parser Extensi | 7 | .S2, .S3, .S3, .S.1, .S.2, .S.4 |
| 0164 | Incremental Comprehension Reader (replaces regex sentence-template par | 5 | .1, .2, .3, .4 |
| 0168 | FrameClaim Ratification Doctrine | 2 | .1 |
| 0169 | CompositionClaim Ratification Doctrine | 2 | .1 |
| 0189 | Comparative reading: anchor-verb widening + multi-word units | 2 | a |
| 0201 | Propositional Canonicalizer (the `proof_chain` keystone) | 2 | .1 |

## 3. Non-ADR files co-located in `docs/adr/` (19)

| File | Classification |
|---|---|
| `BRIEF-11D-next-capability-proposal.md` | in-scope context (capability proposal brief, not a ratified ADR) |
| `INDEX-by-domain.md` | index file — target of Phase 4 index repair, not an audit unit |
| `L10-runtime-model-scope.md` | in-scope context (scope note) |
| `L11-hitl-async-queue-scope.md` | in-scope context (scope note) |
| `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` | governance reconciliation record — reference only, not an audit unit |
| `README.md` | index file — reference only |
| `SESSION-2026-05-12-b.md` | excluded — session journal |
| `SESSION-2026-05-12-language-packs-addendum.md` | excluded — session journal |
| `SESSION-2026-05-12.md` | excluded — session journal |
| `SESSION-2026-05-13.md` | excluded — session journal |
| `SESSION-2026-05-26-comprehension-reader.md` | excluded — session journal |
| `SESSION-2026-05-27-adr-0167-parallel-dispatch.md` | excluded — session journal |
| `SESSION-2026-05-27-tier3-sequencing.md` | excluded — session journal |
| `epistemic-state-taxonomy-scope.md` | in-scope context (scope note) |
| `epistemic-taxonomy-ownership-stage3.md` | BINDING — explicitly called out by docs/adr/README.md; treat as in-scope, audit alongside its governing stack |
| `proposition-graph-scope.md` | in-scope context (scope note) |
| `recognizer-storage-scope.md` | in-scope context (scope note) |
| `substrate-liveness-audit-scope.md` | in-scope context (scope note) |
| `teaching-derived-recognition-scope.md` | in-scope context (scope note) |

## 4. Full ADR table (314)

`Batch` is assigned in numeric-sequence blocks of ~25 for tracking (see `MANIFEST.md`); it is a scheduling label, not a priority ranking — Tier/priority is assigned per-stack in Phase 2/3 and can pull an ADR out of numeric order.

| # | Suffix | Status | Date | Title | File |
|---|---|---|---|---|---|
| 0001 | — | Accepted | 2026-05-12 | VocabManifold Versor Invariant | `ADR-0001-vocab-layer-invariants.md` |
| 0002 | — | Accepted | 2026-05-12 | Ingest Layer Architecture | `ADR-0002-ingest-layer-design.md` |
| 0003 | — | Accepted | 2026-05-12 | Coordinate System Dissolution | `ADR-0003-coordinate-system-dissolution.md` |
| 0004 | — | Accepted | 2026-05-12 | Rotor as Operator, Not Vocabulary Property | `ADR-0004-rotor-as-operator-not-property.md` |
| 0005 | — | Accepted | 2026-05-12 | Language Pack Contract | `ADR-0005-language-pack-contract.md` |
| 0006 | — | Implemented | 2026-05-12 | The Field Energy Operator (Hamiltonian Companion Field) | `ADR-0006-field-energy-operator.md` |
| 0007 | — | Accepted | 2026-05-12 | The Valence Layer | `ADR-0007-valence-layer.md` |
| 0008 | — | Accepted | 2026-05-12 | Allocation Physics | `ADR-0008-allocation-physics.md` |
| 0009 | — | Accepted | 2026-05-12 | Compositional Physics | `ADR-0009-compositional-physics.md` |
| 0010 | — | Accepted | 2026-05-12 | Identity Physics | `ADR-0010-identity-physics.md` |
| 0011 | — | Accepted | 2026-05-13 | Renderer Layer Contract | `ADR-0011-renderer.md` |
| 0012 | — | Accepted | 2026-05-13 | `core_ingest` Governance Layer | `ADR-0012-core-ingest-governance-layer.md` |
| 0013 | — | Accepted | 2026-05-13 | `sensorium/` Multimodal Protocol Layer | `ADR-0013-sensorium-multimodal-protocol.md` |
| 0014 | — | Accepted (Stub) | 2026-05-13 | `train/` Learning Loop | `ADR-0014-train-learning-loop.md` |
| 0015 | — | Accepted — **Crown Proof section AMENDED | 2026-05-13 | Language Packs as Compiled Linguistic Manifolds | `ADR-0015-language-packs-and-holonomy-resonance.md` |
| 0016 | — | Accepted | 2026-05-15 | Capability Roadmap and Eval Methodology | `ADR-0016-capability-roadmap.md` |
| 0017 | — | Accepted | 2026-05-16 | Agency Scope: Responsive-with-Axiology | `ADR-0017-agency-scope.md` |
| 0018 | — | Accepted | 2026-05-16 | Tool Use Scope: Typed Deterministic Operators | `ADR-0018-tool-use-scope.md` |
| 0019 | — | Accepted | 2026-05-16 | Exact Vault Recall Acceleration | `ADR-0019-exact-vault-recall-acceleration.md` |
| 0020 | — | Accepted (2026-05-16) | 2026-05-16 | Phase 5 / Rust Parity Sequencing | `ADR-0020-phase5-rust-parity-sequencing.md` |
| 0021 | — | Accepted | 2026-05-16 | Epistemic Grade Policy | `ADR-0021-epistemic-grade-policy.md` |
| 0022 | — | Accepted (2026-05-17 — all five TBDs add | 2026-05-17 | Forward Semantic Control | `ADR-0022-forward-semantic-control.md` |
| 0023 | — | Accepted | 2026-05-17 | Forward Semantic Control: Proof Evidence | `ADR-0023-forward-semantic-control-proof.md` |
| 0024 | — | Accepted | 2026-05-17 | Inner-Loop Per-Rotor Admissibility | `ADR-0024-inner-loop-admissibility.md` |
| 0025 | — | Accepted (2026-05-17) | 2026-05-17 | Rotor / Frame Admissibility | `ADR-0025-rotor-frame-admissibility-design-note.md` |
| 0026 | — | Accepted (2026-05-17) | — | Ranked Admissibility with Margin | `ADR-0026-ranked-admissibility-with-margin.md` |
| 0027 | — | Accepted (2026-05-17) — Phases 1–6 compl | — | Identity Packs — Load-Bearing, Swappable, Ratified | `ADR-0027-identity-packs.md` |
| 0028 | — | Accepted (2026-05-17) | — | Identity Surface Wiring — Pack-Driven Hedge & Claim Strength | `ADR-0028-identity-surface-wiring.md` |
| 0029 | — | Accepted (2026-05-17) | — | Safety Packs — Always-Loaded, Never-Replaceable Boundaries | `ADR-0029-safety-packs.md` |
| 0030 | — | Accepted (2026-05-17) | — | Depth-Language Hedge Wiring | `ADR-0030-depth-language-hedge.md` |
| 0031 | — | Accepted (2026-05-17) | — | Score-Decomposition Surface — Per-Axis Hedge Phrases | `ADR-0031-score-decomposition-surface.md` |
| 0032 | — | Accepted (2026-05-17) | — | SafetyCheck — Structural Surface for Safety-Pack Boundaries | `ADR-0032-safety-check-surface.md` |
| 0033 | — | Accepted (2026-05-17) | — | Ethics Packs — Swappable Domain Commitments | `ADR-0033-ethics-packs.md` |
| 0034 | — | Accepted (2026-05-17) | — | EthicsCheck — Structural Surface for Ethics-Pack Commitments | `ADR-0034-ethics-check-surface.md` |
| 0035 | — | Accepted (2026-05-17) | — | Turn-Loop Verdict Surfacing for SafetyCheck and EthicsCheck | `ADR-0035-turn-loop-verdict-surfacing.md` |
| 0036 | — | Accepted (2026-05-17) | — | Safety-Only Typed Refusal Policy | `ADR-0036-safety-refusal-policy.md` |
| 0037 | — | Accepted (2026-05-17) | — | Per-Predicate Ethics Refusal Opt-In | `ADR-0037-per-predicate-ethics-refusal.md` |
| 0038 | — | Accepted (2026-05-17) | — | Hedge Injection as a Runtime-Level Affordance | `ADR-0038-hedge-injection.md` |
| 0039 | — | Accepted (2026-05-17) | — | Audit Completeness — `TurnVerdicts` Bundle, Stub-Path `TurnEvent`, `hedge_inject | `ADR-0039-audit-completeness.md` |
| 0040 | — | Accepted (2026-05-17) | — | Structured-Logging Sink for Turn-Event Audit | `ADR-0040-telemetry-sink.md` |
| 0041 | — | Accepted (2026-05-17) | — | `core chat --show-verdicts` + Sink Fan-Out | `ADR-0041-cli-verdicts-and-fanout.md` |
| 0042 | — | Accepted (2026-05-17) | — | Audit Tour Demo — `core demo audit-tour` | `ADR-0042-audit-tour-demo.md` |
| 0043 | — | Accepted (2026-05-17) | — | Phase-2 pack measurements: claims → numbers | `ADR-0043-pack-measurements-phase2.md` |
| 0044 | — | Accepted (2026-05-17) | — | Medical / clinical ethics pack (worked-example domain pack) | `ADR-0044-medical-clinical-ethics-pack.md` |
| 0045 | — | Accepted (2026-05-17) | — | Long-context recall: CORE vs transformer baselines | `ADR-0045-long-context-recall-vs-transformer-baselines.md` |
| 0046 | — | Accepted | 2026-05-18 | PropositionGraph as Forward Admissibility Constraint | `ADR-0046-forward-graph-constraint.md` |
| 0047 | — | Accepted | 2026-05-18 | Wire the Forward Graph Constraint into the Chat Hot Path | `ADR-0047-wire-forward-graph-constraint.md` |
| 0048 | — | Accepted | 2026-05-18 | Pack-Grounded Surface for Cold-Start DEFINITION / RECALL | `ADR-0048-pack-grounded-surface.md` |
| 0049 | — | Accepted | 2026-05-18 | Intent Classifier Head-Noun Subject Extraction | `ADR-0049-intent-subject-extraction.md` |
| 0050 | — | Accepted | 2026-05-18 | Pack-Grounded Surface for Cold-Start COMPARISON | `ADR-0050-pack-grounded-comparison.md` |
| 0051 | — | Accepted | 2026-05-18 | Trust-Boundary Hardening Pass | `ADR-0051-trust-boundary-hardening.md` |
| 0052 | — | Accepted | 2026-05-18 | Teaching-Grounded Surface for Cold-Start CAUSE / VERIFICATION | `ADR-0052-teaching-grounded-surface.md` |
| 0053 | — | Accepted | 2026-05-18 | Cognition Lane Closure: Dev-Driven Corpus Expansion + CORRECTION Acknowledgement | `ADR-0053-cognition-lane-closure.md` |
| 0054 | — | Accepted | 2026-05-18 | Vault Recall: Matrix-Cache Indexing + Batched API; Holdout Split Wired | `ADR-0054-vault-recall-indexing-batching.md` |
| 0055 | — | Phase A + Phase B Accepted; Phase C Impl | 2026-05-18 | Inter-Session Memory: Reviewed Discovery Promotion | `ADR-0055-inter-session-memory-discovery-promotion.md` |
| 0056 | — | Accepted (implemented at `4eecf73`, 2026 | 2026-05-18 | Contemplation Loop: Question Decomposition + Polarity + Domain Typing (Phase C1) | `ADR-0056-contemplation-loop-c1.md` |
| 0057 | — | Accepted | 2026-05-18 | Teaching-Chain Proposal + Review + Replay-Equivalence Gate (Phase C2) | `ADR-0057-teaching-chain-proposal-review.md` |
| 0058 | — | Accepted | 2026-05-18 | `forward_graph_constraint`: Engaged but Inert on Today's Cognition Lane | `ADR-0058-forward-graph-constraint-status.md` |
| 0059 | — | Accepted | 2026-05-18 | Correction-Pass Telemetry Emission | `ADR-0059-correction-pass-telemetry.md` |
| 0060 | — | Accepted | 2026-05-18 | CORRECTION Acknowledgement Carries the Corrected-Topic Lemma | `ADR-0060-correction-acknowledgment-topic-lemma.md` |
| 0061 | — | Accepted | 2026-05-18 | PROCEDURE Intent Routes to Pack-Grounded Surface | `ADR-0061-procedure-intent-pack-grounded-surface.md` |
| 0062 | — | Accepted | 2026-05-18 | Composed Teaching-Grounded Surface (Chain-of-Chains) | `ADR-0062-composed-teaching-grounded-surface.md` |
| 0063 | — | Accepted | 2026-05-18 | Cross-pack surface resolver | `ADR-0063-cross-pack-surface-resolver.md` |
| 0064 | — | Accepted | 2026-05-18 | Cross-pack teaching chains | `ADR-0064-cross-pack-teaching-chains.md` |
| 0065 | — | Accepted | 2026-05-18 | OOV gradient + relations v2 (Plan Phase 2) | `ADR-0065-oov-gradient-and-relations-v2.md` |
| 0066 | — | Accepted | 2026-05-18 | Turn-level composition (Plan Phase 3) | `ADR-0066-turn-level-composition.md` |
| 0067 | — | Accepted | 2026-05-18 | Cross-pack teaching chains (Plan Phase 4) | `ADR-0067-cross-pack-teaching-chains.md` |
| 0068 | — | Accepted | 2026-05-19 | Register pack class (Plan Phase R1) | `ADR-0068-register-pack-class.md` |
| 0069 | — | Accepted (amended 2026-05-19) | 2026-05-19 | Realizer register parameter (Plan Phase R2) | `ADR-0069-realizer-register-parameter.md` |
| 0070 | — | Accepted | 2026-05-19 | Second ratified register pack: `terse_v1` (Plan Phase R3) | `ADR-0070-register-pack-terse-v1.md` |
| 0071 | — | Accepted | 2026-05-19 | Seeded surface variation + discourse markers (Plan Phase R4) | `ADR-0071-seeded-surface-variation.md` |
| 0072 | — | Accepted | 2026-05-19 | Register telemetry + operator surface (Plan Phase R5) | `ADR-0072-register-telemetry-operator-surface.md` |
| 0073 | — | Accepted (umbrella ratified; sub-ADRs L1 | 2026-05-19 | Anchor lens: substrate-driven substantive variation | `ADR-0073-anchor-lens-substrate.md` |
| 0073 | a | Accepted | 2026-05-19 | Anchor lens content phase (Plan Phase L1.1) | `ADR-0073a-anchor-lens-content-phase.md` |
| 0073 | b | Accepted | 2026-05-19 | Anchor lens class + loader (Plan Phase L1.2) | `ADR-0073b-anchor-lens-class-loader.md` |
| 0073 | c | Accepted | 2026-05-19 | First non-trivial lenses + composer wiring (Plan Phase L1.3) | `ADR-0073c-anchor-lens-composer-wiring.md` |
| 0073 | d | Accepted | 2026-05-19 | Anchor-lens telemetry, CLI, and tour demo (Plan Phase L1.4) | `ADR-0073d-anchor-lens-telemetry-tour.md` |
| 0074 | — | Accepted | 2026-05-19 | Orthogonality tour: anchor-lens × register composition demo | `ADR-0074-orthogonality-tour.md` |
| 0075 | — | Accepted | 2026-05-19 | Realizer slot-type guard (C1: coherence floor) | `ADR-0075-realizer-slot-type-guard.md` |
| 0076 | — | Accepted | 2026-05-20 | Confirmation-Tag Normalization (C2) | `ADR-0076-confirmation-tag-normalization.md` |
| 0077 | — | Ratified | 2026-05-19 | Substantive register knobs + register-tour gate strengthening (R6) | `ADR-0077-substantive-register-knobs.md` |
| 0078 | — | Ratified | 2026-05-20 | Composer/Graph atom equivalence telemetry | `ADR-0078-composer-graph-atom-equivalence.md` |
| 0078 | — | Note (no formal status field — pre-imple | — | ADR-0078 Phase 1 — Pre-Implementation Planning Note | `ADR-0078-phase1-implementation-note.md` |
| 0080 | — | Accepted | 2026-05-20 | Contemplation Loop: self-interrogation without self-ratification | `ADR-0080-contemplation-loop.md` |
| 0082 | — | Ratified | 2026-05-20 | Frontier Provider Adapters | `ADR-0082-frontier-provider-adapters.md` |
| 0083 | — | Accepted | 2026-05-20 | Transitive Chain Surface (Bounded Multi-Hop Composition) | `ADR-0083-transitive-chain-surface.md` |
| 0084 | — | Proposed | 2026-05-20 | Definitional Layer for Lexicon Packs | `ADR-0084-definitional-layer.md` |
| 0085 | — | Accepted | 2026-05-20 | Gloss-Aware CAUSE Composer | `ADR-0085-gloss-aware-cause.md` |
| 0087 | — | Proposed | 2026-05-20 | Rhetorical Style as Selection Axis (Pre-Work for Writing Curriculum) | `ADR-0087-rhetorical-style-axis.md` |
| 0088 | — | Proposed | 2026-05-20 | Realizer-Grounded Authority (Finding 2 retry) | `ADR-0088-realizer-grounded-authority.md` |
| 0089 | — | Proposed | 2026-05-20 | Compound-Intent Pipeline Dispatch (Finding 4) | `ADR-0089-compound-intent-pipeline-dispatch.md` |
| 0090 | — | Proposed | 2026-05-21 | Unified Ingest + Batched Recall (audit Findings 6 + 7) | `ADR-0090-unified-ingest-and-batched-recall.md` |
| 0091 | — | Accepted | 2026-05-21 | Domain Pack Contract v1 | `ADR-0091-domain-pack-contract-v1.md` |
| 0092 | — | Accepted | 2026-05-21 | Reviewer Registry v1 | `ADR-0092-reviewer-registry-v1.md` |
| 0093 | — | Accepted | 2026-05-21 | Domain Pack Contract v1 Implementation | `ADR-0093-domain-pack-contract-v1-implementation.md` |
| 0094 | — | Accepted | 2026-05-21 | Proposal Source Provenance | `ADR-0094-proposal-source-provenance.md` |
| 0095 | — | Accepted | 2026-05-21 | Miner-Sourced Teaching Proposals | `ADR-0095-miner-sourced-teaching-proposals.md` |
| 0096 | — | Accepted | 2026-05-21 | Fabrication-Control Eval Lane | `ADR-0096-fabrication-control-eval-lane.md` |
| 0097 | — | Accepted | 2026-05-21 | Mathematics-Logic Reasoning-Capable Ratification | `ADR-0097-mathematics-logic-reasoning-capable-ratification.md` |
| 0098 | — | Accepted | 2026-05-21 | Demo Composition Contract | `ADR-0098-demo-composition-contract.md` |
| 0099 | — | Accepted | 2026-05-21 | Public Showcase Demo | `ADR-0099-public-showcase-demo.md` |
| 0100 | — | Accepted | 2026-05-21 | Physics Reasoning-Capable Ratification | `ADR-0100-physics-reasoning-capable-ratification.md` |
| 0101 | — | Accepted | 2026-05-21 | Systems-Software Reasoning-Capable Ratification | `ADR-0101-systems-software-reasoning-capable-ratification.md` |
| 0102 | — | Accepted | 2026-05-21 | Hebrew-Greek Textual-Reasoning Reasoning-Capable Ratification | `ADR-0102-hebrew-greek-reasoning-capable-ratification.md` |
| 0103 | — | Accepted | 2026-05-22 | Fluency Lane Attachment for ADR-0102 | `ADR-0103-fluency-lane-attachment-for-adr-0102.md` |
| 0104 | — | Accepted | 2026-05-22 | Curriculum-Sourced Teaching Proposals | `ADR-0104-curriculum-sourced-teaching-proposals.md` |
| 0105 | — | Accepted (2026-05-22) | — | Sealed Holdout Encryption via age | `ADR-0105-sealed-holdout-encryption.md` |
| 0106 | — | Accepted | 2026-05-22 | Expert-Demo Promotion Contract | `ADR-0106-expert-demo-promotion-contract.md` |
| 0107 | — | Accepted (decision: defer promotion) | 2026-05-22 | `mathematics_logic` Expert-Demo Promotion: Deferred | `ADR-0107-mathematics-logic-expert-demo-deferred.md` |
| 0108 | — | Accepted | 2026-05-22 | Proposed-ADR Sequencing Post-ADR-0105 | `ADR-0108-proposed-adr-sequencing.md` |
| 0109 | — | Accepted | 2026-05-22 | Lane-Shape-Aware Thresholds (ADR-0106 Amendment) | `ADR-0109-lane-shape-aware-thresholds.md` |
| 0110 | — | Accepted | 2026-05-22 | `mathematics_logic` Expert-Demo Promotion | `ADR-0110-mathematics-logic-expert-demo-promotion.md` |
| 0111 | — | Accepted | 2026-05-22 | `physics` Expert-Demo Promotion | `ADR-0111-physics-expert-demo-promotion.md` |
| 0112 | — | Accepted | 2026-05-22 | Runnable Expert-Demo Showcase | `ADR-0112-runnable-expert-demo-showcase.md` |
| 0113 | — | Accepted | 2026-05-22 | Rename `expert-demo` → `audit-passed`; Reserve `expert` for Future Capability Ti | `ADR-0113-rename-expert-demo-to-audit-passed.md` |
| 0114 | — | Proposed | 2026-05-22 | Expert-Capability Roadmap: GSM8K-Math First | `ADR-0114-expert-capability-roadmap-gsm8k-first.md` |
| 0114 | a | Accepted (documentation-only; no code ch | 2026-05-22 | Anti-Overfitting Proof Obligations for `expert` Promotion | `ADR-0114a-anti-overfitting-proof-obligations.md` |
| 0114 | a.10 | Accepted | 2026-05-23 | Pack-Provenance Auditor (Obligation #10 wired for B3) | `ADR-0114a.10-pack-provenance-auditor.md` |
| 0114 | a.2 | Accepted | 2026-05-23 | OOD-Ratio Auditor (Obligation #2 wired for B3) | `ADR-0114a.2-ood-ratio-auditor.md` |
| 0114 | a.5 | Accepted | 2026-05-23 | Reasoning-Isolation Perturbation Suite (Obligation #5, B3) | `ADR-0114a.5-perturbation-suite.md` |
| 0114 | a.6 | Accepted (mechanism); coverage gap defer | 2026-05-23 | Compositional-Depth Curve Auditor (Obligation #6 wired for B3) | `ADR-0114a.6-depth-curve-auditor.md` |
| 0114 | a.8 | Accepted (obligation passes; surfaces 2  | 2026-05-23 | Adversarial Generation Auditor (Obligation #8 wired) | `ADR-0114a.8-adversarial-auditor.md` |
| 0115 | — | Phase 1.1 Accepted (schema + 5 seed case | 2026-05-22 | Math Problem Parser and Typed Proposition Graph | `ADR-0115-math-problem-parser-and-graph.md` |
| 0116 | — | Accepted | 2026-05-22 | Deterministic Solver (`MathProblemGraph` → `SolutionTrace`) | `ADR-0116-deterministic-solver.md` |
| 0117 | — | Accepted | 2026-05-22 | `SolutionTrace` Verifier | `ADR-0117-solution-trace-verifier.md` |
| 0118 | — | Accepted | 2026-05-22 | Stepped Realizer (`SolutionTrace` → Prose) | `ADR-0118-stepped-realizer.md` |
| 0118 | a | Accepted | 2026-05-22 | OOD Surface Generator for GSM8K-Style Parser Dev | `ADR-0118a-ood-surface-generator.md` |
| 0119 | — | Proposed (roadmap-only) | 2026-05-22 | GSM8K Eval Lane Roadmap (Phase 5) | `ADR-0119-gsm8k-eval-lane-roadmap.md` |
| 0119 | .1 | Accepted | 2026-05-23 | Seal fabrication_control Holdout (ADR-0105 Amendment) | `ADR-0119.1-sealed-holdout-fabrication-control.md` |
| 0119 | .2 | Accepted | 2026-05-22 | GSM8K Eval Corpus Dev/Public Splits | `ADR-0119.2-gsm8k-eval-corpus-dev-public.md` |
| 0119 | .3 | Accepted | 2026-05-22 | gsm8k_math Lane Runner (Phase 5.3) | `ADR-0119.3-lane-runner.md` |
| 0119 | .4 | Accepted | 2026-05-22 | GSM8K Math: Frontier-Baseline Comparison (ADR-0114a §Obligation #7) | `ADR-0119.4-frontier-baseline-comparison.md` |
| 0119 | .5 | Accepted | 2026-05-22 | Adversarial Generation (ADR-0114a Obligation #8) | `ADR-0119.5-adversarial-generation.md` |
| 0119 | .6 | Accepted | 2026-05-23 | GSM8K Math Depth-Curve Measurement Harness | `ADR-0119.6-depth-curve-harness.md` |
| 0119 | .7 | Accepted | 2026-05-23 | Sealed GSM8K Test Set as gsm8k_math Holdout | `ADR-0119.7-sealed-gsm8k-test.md` |
| 0119 | .8 | Accepted | 2026-05-23 | gsm8k_math Overall Lane Gate (`gsm8k_capability_shape`) | `ADR-0119.8-lane-gate.md` |
| 0120 | — | Proposed (contract-only; no domain promo | 2026-05-23 | First `expert` Promotion Contract | `ADR-0120-expert-promotion-contract.md` |
| 0120 | — | Accepted — first `expert`-tier domain in | 2026-05-23 | ADR-0120 (math, ledger flip) — Mathematics-Logic Domain Promoted to `expert` | `ADR-0120-math-expert-ledger-flip.md` |
| 0120 | — | Accepted (technical pass on first evalua | 2026-05-23 | ADR-0120 (math) — Math-Expert Promotion Composer Wire-Up | `ADR-0120-math-expert-promotion-wireup.md` |
| 0121 | — | Accepted (the deferral is the decision) | 2026-05-23 | `mathematics_logic` `expert` Promotion — Deferred (first attempt) | `ADR-0121-mathematics-logic-expert-deferred.md` |
| 0122 | — | Accepted (substrate landed; sealed-lift  | 2026-05-22 | Parser Expansion: Rate / Per-Unit Reasoning (substrate-only; lift deferred) | `ADR-0122-parser-rate-per-unit.md` |
| 0122 | — | Accepted (decision: defer promotion) | 2026-05-22 | `systems_software` Audit-Passed Promotion: Deferred | `ADR-0122-systems-software-audit-passed-deferred.md` |
| 0123 | — | Accepted (surface increment; substrate l | 2026-05-23 | Comparison-Phrasing Realizer (surface increment on the ADR-0123 substrate) | `ADR-0123-parser-comparison-phrasing.md` |
| 0123 | — | Accepted | 2026-05-22 | `symbolic_logic` Lane-Shape Remap (ADR-0109 Amendment) | `ADR-0123-symbolic-logic-shape-remap.md` |
| 0123 | a | Accepted | 2026-05-22 | `all_three_pass_rate` Synonym in `inference_shape` (ADR-0109 Amendment) | `ADR-0123a-inference-shape-synonym.md` |
| 0124 | — | Accepted | 2026-05-22 | `systems_software` Audit-Passed Promotion | `ADR-0124-systems-software-audit-passed-promotion.md` |
| 0125 | — | Accepted | 2026-05-22 | Reasoning-Isolation Perturbation Suite | `ADR-0125-reasoning-isolation-perturbation-suite.md` |
| 0126 | — | Proposed | 2026-05-23 | Candidate-Graph Parser with Round-Trip Verifier-Filter | `ADR-0126-candidate-graph-parser.md` |
| 0127 | — | Empirical result; load-bearing for the G | 2026-05-23 | ADR-0127 + ADR-0128 Results — Path-B Triggered | `ADR-0127-0128-RESULTS.md` |
| 0127 | — | Proposed (scope-only; implementation fol | 2026-05-23 | `en_units_v1` Pack + Units-Aware Candidate Extractors | `ADR-0127-units-pack-and-units-aware-parser.md` |
| 0128 | — | Proposed (scope-only; sibling to ADR-012 | 2026-05-23 | `en_numerics_v1` Pack | `ADR-0128-numerics-pack.md` |
| 0129 | — | Proposed — Deferred (backlog item; no im | 2026-05-23 | Spaced Reviewed-Correction Replay (Deferred Proposal) | `ADR-0129-spaced-correction-replay-deferred.md` |
| 0130 | — | Proposed — Deferred (backlog item; no im | 2026-05-23 | Pre-Articulation Calibration Logging (Deferred Proposal) | `ADR-0130-pre-articulation-calibration-deferred.md` |
| 0131 | — | Proposed | 2026-05-23 | Re-Target Math Expert Promotion to Architecture-Aligned Benchmarks | `ADR-0131-math-expert-rebench.md` |
| 0131 | .1.F | Proposed | 2026-05-23 | B1 Symbolic Equivalence: Frontier-Baseline Comparison | `ADR-0131.1.F-frontier-baseline-comparison.md` |
| 0131 | .1.S | Accepted | 2026-05-23 | Sealed Holdout for Benchmark 1 (Symbolic Equivalence v1) | `ADR-0131.1.S-sealed-holdout.md` |
| 0131 | .2 | Accepted | 2026-05-23 | Benchmark 2: CORE-native teaching-corpus eval (lane gate) | `ADR-0131.2-teaching-corpus-eval.md` |
| 0131 | .2.B | Accepted | 2026-05-23 | Benchmark 2: B2 teaching-corpus enrichment (load-bearing gate) | `ADR-0131.2.B-teaching-corpus-enrichment.md` |
| 0131 | .3 | Accepted | 2026-05-23 | Benchmark 3: Bounded-Grammar Word Problems | `ADR-0131.3-bounded-grammar.md` |
| 0131 | .4 | Accepted | 2026-05-23 | Composite Math-Expert Promotion Gate (wired) | `ADR-0131.4-composite-math-gate.md` |
| 0131 | .5 | Accepted | 2026-05-23 | GSM8K Coverage Probe: Retirement After G.x Axis Completion | `ADR-0131.5-gsm8k-probe-retirement.md` |
| 0131 | .G | Proposed | 2026-05-23 | GSM8K Coverage Probe: Honest Measurement Under the Safety Rail | `ADR-0131.G-gsm8k-coverage-probe.md` |
| 0131 | .G.0 | Proposed | 2026-05-23 | Probe Substrate: Candidate-Graph Pipeline | `ADR-0131.G.0-probe-substrate.md` |
| 0131 | .G.1 | Accepted | 2026-05-23 | Capability axis: state-introducing verb classes | `ADR-0131.G.1-verb-classes-initial-state.md` |
| 0131 | .G.2 | Proposed | 2026-05-23 | Capability axis: comparative operations (additive + multiplicative) | `ADR-0131.G.2-comparatives.md` |
| 0131 | .G.3 | Proposed | 2026-05-23 | Numeric Literals (money + hyphenated cardinals) | `ADR-0131.G.3-numerics.md` |
| 0131 | .G.3.1 | Proposed | 2026-05-23 | Numerics extensions (fractions + multi-currency + multi-token cardinals + word-n | `ADR-0131.G.3.1-numerics-extensions.md` |
| 0131 | .G.4 | Proposed | 2026-05-23 | Capability axis: multi-clause composition (conjoined subjects, conjoined objects | `ADR-0131.G.4-multi-clause.md` |
| 0131 | .G.5 | Accepted | 2026-05-23 | Aggregate Answer Composition | `ADR-0131.G.5-aggregate-answer-composition.md` |
| 0132 | — | Accepted (Phase 1 only; Phases 2–5 defer | 2026-05-23 | Semantic-Symbolic Binding Graph: Phase 1 data model | `ADR-0132-binding-graph-data-model.md` |
| 0133 | — | Accepted (Phase 2 only; Phases 3–5 defer | 2026-05-23 | Semantic-Symbolic Binding Graph: Phase 2 adapter from `MathProblemGraph` | `ADR-0133-binding-graph-adapter.md` |
| 0134 | — | accepted | 2026-05-23 | Binding Graph Phase 3: Unit-Aware Equation Admissibility | `ADR-0134-binding-graph-admissibility.md` |
| 0135 | — | Accepted. | — | Binding Graph Phase 4: question-target binding refinement | `ADR-0135-binding-graph-question-target.md` |
| 0136 | — | Active — *Regex sentence-template prescr | 2026-05-23 | Statement-Layer Corridor: Graduated GSM8K Admission via Parser Extension | `ADR-0136-statement-layer-corridor.md` |
| 0136 | .S.1 | Accepted — *regex patterns scheduled for | 2026-05-23 | Rate/Event Statement Parsing | `ADR-0136.S.1-rate-event-statements.md` |
| 0136 | .S.2 | Active — *regex patterns scheduled for r | 2026-05-23 | Conditional-Op Question (Statement-Layer Corridor) | `ADR-0136.S.2-conditional-op-question.md` |
| 0136 | .S.4 | Accepted — *regex patterns scheduled for | 2026-05-23 | Novel Initial-Form Subject-Slot Widenings | `ADR-0136.S.4-novel-initial-form.md` |
| 0136 | .S2 | Accepted | 2026-05-23 | post-rescan — Refusal Rescan v2: Barrier-Shift Ledger | `ADR-0136.S2-post-rescan.md` |
| 0136 | .S3 | Accepted — *regex patterns scheduled for | 2026-05-23 | Compound Initial-Mutation Extractor | `ADR-0136.S3-compound-initial-mutation.md` |
| 0136 | .S3 | Accepted | 2026-05-23 | post-rescan — Refusal Rescan v3: Barrier-Shift Ledger | `ADR-0136.S3-post-rescan.md` |
| 0138 | — | Draft (design-only) | 2026-05-23 | Comparative-Reference Layer | `ADR-0138-comparative-reference-layer.md` |
| 0139 | — | Draft | 2026-05-24 | Arithmetic-as-Versor Spike: `add` Only | `ADR-0139-arithmetic-as-versor-spike.md` |
| 0140 | — | Proposed | — | CORE Trace Protocol v0 | `ADR-0140-core-trace-protocol-v0.md` |
| 0140 | — | Draft | 2026-05-24 | `subtract` as Inverse Translator + Additive Group Closure | `ADR-0140-subtract-and-additive-group-closure.md` |
| 0141 | — | Draft | 2026-05-24 | `multiply` as Dilator (Positive Non-Zero Multipliers Only) | `ADR-0141-multiply-as-dilator-positive-nonzero.md` |
| 0142 | — | Accepted (integration deferred pending A | 2026-05-24 | Epistemic State Taxonomy — First-Class Vocabulary | `ADR-0142-epistemic-state-taxonomy.md` |
| 0143 | — | Accepted | 2026-05-24 | Teaching-Derived Structural Recognition via Multi-Resolution Anti-Unification | `ADR-0143-recognition-spike-anti-unification.md` |
| 0144 | — | Accepted | 2026-05-24 | PropositionGraph — Epistemic Carrier and Recognition Integration Gate | `ADR-0144-proposition-graph-epistemic-carrier.md` |
| 0145 | — | Accepted | 2026-05-25 | Energy-Modulated Vault Surface Readback | `ADR-0145-energy-modulated-surface-readback.md` |
| 0146 | — | Accepted | 2026-05-25 | L10 Shape B Hybrid Engine-State Persistence | `ADR-0146-l10-hybrid-engine-state-persistence.md` |
| 0148 | — | Accepted | 2026-05-25 | Wire VaultPromotionPolicy into turn boundary | `ADR-0148-vault-promotion-policy-wiring.md` |
| 0149 | — | Accepted | 2026-05-25 | Integrate DerivedRecognizer into CognitiveTurnPipeline | `ADR-0149-derived-recognizer-pipeline-wiring.md` |
| 0150 | — | Accepted | 2026-05-25 | Autonomous Inter-Session Contemplation | `ADR-0150-autonomous-inter-session-contemplation.md` |
| 0151 | — | Accepted | 2026-05-25 | Auto-Proposal Pipeline at Load | `ADR-0151-auto-proposal-pipeline.md` |
| 0152 | — | Accepted | — | Learning-Arc Demo (`core demo learning-arc`) | `ADR-0152-learning-arc-demo.md` |
| 0153 | — | accepted | 2026-05-25 | TurnEvent trace_hash back-stamp (W-020a) | `ADR-0153-turn-event-trace-hash-backstamp.md` |
| 0154 | — | accepted | 2026-05-25 | DerivedRecognizer producer wiring (W-020b) | `ADR-0154-recognizer-producer-wiring.md` |
| 0155 | — | scoping | 2026-05-25 | CI contemplation runner (W-021) | `ADR-0155-ci-contemplation-runner.md` |
| 0156 | — | accepted | 2026-05-25 | Atomic engine-state checkpoint writes (W-022 / L10b.1) | `ADR-0156-atomic-engine-state-checkpoint.md` |
| 0157 | — | accepted | 2026-05-26 | Revision-mismatch warning on engine-state load (W-023 / L10b.2) | `ADR-0157-revision-mismatch-warning.md` |
| 0158 | — | accepted | 2026-05-26 | reboot_event audit trail entry (W-024 / L10b.3) | `ADR-0158-reboot-event-audit.md` |
| 0159 | — | Accepted | — | Contemplation Quality Eval Lane (W-025) | `ADR-0159-contemplation-quality-eval.md` |
| 0160 | — | proposed | 2026-05-26 | CORE Workbench v1: operator/auditor UI before public chat | `ADR-0160-core-workbench-v1.md` |
| 0161 | — | Proposed | 2026-05-26 | HITL Async Queue (W-009, L11) | `ADR-0161-hitl-async-queue.md` |
| 0162 | — | Proposed | 2026-05-26 | Workbench Design System (v1) | `ADR-0162-workbench-design-system.md` |
| 0163 | — | Proposed (spec only — no code). Follow-o | — | F2 — Confuser Corpus: a discrimination probe, not a coverage target | `ADR-0163-F2-confuser-corpus-spec.md` |
| 0163 | — | Proposed — *Phases B–E prescription supe | 2026-05-26 | Path to GSM8K mastery: candidate-graph admissibility via the contemplation/HITL  | `ADR-0163-gsm8k-path-to-mastery.md` |
| 0164 | — | Accepted (ratified by ADR-0207, 2026-06- | 2026-05-26 | Incremental Comprehension Reader (replaces regex sentence-template parsing) | `ADR-0164-incremental-comprehension-reader.md` |
| 0164 | .1 | Proposed | 2026-05-26 | Lexical Primitive Set Scope (seed registry for `en_core_math_v1`) | `ADR-0164.1-lexical-primitive-scope.md` |
| 0164 | .2 | Proposed | 2026-05-26 | Pronoun / Entity Resolution Policy | `ADR-0164.2-pronoun-entity-resolution.md` |
| 0164 | .3 | Proposed | 2026-05-26 | Cross-Sentence Reading State | `ADR-0164.3-cross-sentence-state.md` |
| 0164 | .4 | Proposed | 2026-05-26 | Phase 2 Statement-Frame Reader | `ADR-0164.4-phase2-statement-frame-reader.md` |
| 0165 | — | Accepted (ratified by ADR-0207, 2026-06- | 2026-05-26 | Regex Scope Rule: Lexemes Only, Never Grammar | `ADR-0165-regex-scope-rule.md` |
| 0166 | — | Proposed | 2026-05-27 | Measurement-Capability Sequencing Discipline | `ADR-0166-measurement-capability-sequencing.md` |
| 0167 | — | Proposed (scoping ADR; no code in this P | 2026-05-27 | Audit-as-Teaching-Evidence (Math Reader → Contemplation) | `ADR-0167-audit-as-teaching-evidence.md` |
| 0168 | — | Proposed (doctrine/scoping ADR; no runti | 2026-05-27 | FrameClaim Ratification Doctrine | `ADR-0168-frameclaim-ratification.md` |
| 0168 | .1 | Proposed (design bridge; no runtime Fram | 2026-05-27 | MathFrameClaimProposal Adapter | `ADR-0168.1-math-frameclaim-proposal-adapter.md` |
| 0169 | — | Proposed (doctrine/scoping ADR; no runti | 2026-05-27 | CompositionClaim Ratification Doctrine | `ADR-0169-compositionclaim-ratification.md` |
| 0169 | .1 | Proposed (design bridge; no runtime Comp | 2026-05-27 | MathCompositionClaimProposal Adapter | `ADR-0169.1-math-compositionclaim-proposal-adapter.md` |
| 0170 | — | Accepted — W1 (type widening) + W2 (DCS- | 2026-05-27 | Recognizer Injector Contract Widening | `ADR-0170-injector-contract-widening.md` |
| 0172 | — | Proposed (scoping ADR; no runtime change | 2026-05-27 | Math-Domain Corpus-Decomposition Mechanism (Learning-Arc Analog) | `ADR-0172-math-corpus-decomposition-mechanism.md` |
| 0173 | — | Accepted (W0 of the workbench-UI wave; d | 2026-05-27 (proposed); 2026-05-29 (accepted) | Workbench Ratification Trust Boundary | `ADR-0173-workbench-ratification-trust-boundary.md` |
| 0174 | — | Accepted (ratified by ADR-0207, 2026-06- | 2026-05-28 | Held-Hypothesis Comprehension with Lookback and In-Loop Contemplation | `ADR-0174-held-hypothesis-comprehension.md` |
| 0175 | — | Proposed | 2026-05-28 | Calibrated Attempt-and-Eliminate Learning: Two Regimes Under wrong=0 | `ADR-0175-calibrated-attempt-and-eliminate-learning.md` |
| 0176 | — | Proposed | 2026-05-28 | Multi-Step Grounded Composition with Question-Targeting | `ADR-0176-multistep-composition-question-targeting.md` |
| 0177 | — | Proposed | 2026-05-28 | Cue-Precision Learning: from practice eliminations to trusted cue→op patterns | `ADR-0177-cue-precision-learning.md` |
| 0178 | — | Proposed (scope only — no code). Sub-pha | — | ADR-0178 GB-3b — referent-aware accumulation chaining (scope) | `ADR-0178-GB3b-referent-accumulation-scope.md` |
| 0178 | — | Accepted (ratified by ADR-0207, 2026-06- | 2026-05-28 | Compositional Structure: Comprehension-Guided Multi-Step Derivation (Gap B) | `ADR-0178-compositional-structure.md` |
| 0179 | — | Accepted (ratified by ADR-0207, 2026-06- | 2026-05-28 | Extraction Richness: feeding the comprehension composer real quantities | `ADR-0179-extraction-richness.md` |
| 0180 | — | Accepted (2026-05-31) — Delta-CRDT refer | 2026-05-29 (Proposed) · 2026-05-31 (Accepted) | Delta-CRDT Sharded Substrate for Multimodal Concurrency | `ADR-0180-crdt-sharded-vault-concurrency.md` |
| 0181 | — | Accepted (ratified 2026-06-03) — impleme | 2026-05-29 | CORE-native Audio Compiler over the Delta-CRDT Substrate | `ADR-0181-audio-compiler-delta-crdt.md` |
| 0182 | — | Accepted / Implemented (PRs #476, #480,  | — | Cross-composer disagreement pooling: refuse distractor-quantity confusers withou | `ADR-0182-cross-composer-disagreement-pooling.md` |
| 0183 | — | Proposed (stub — placeholder to record t | 2026-05-29 | Lawful Audio→Lexeme Path (stub) | `ADR-0183-lawful-audio-lexeme-path.md` |
| 0184 | — | Accepted / Implemented. Implementation r | — | Distinct-unit product rule: cut the product-of-all over-commit (the first lever  | `ADR-0184-distinct-unit-product-rule.md` |
| 0184 | — | Proposed | 2026-05-29 | Scoped Semantic State Transitions for English Multi-Step Reasoning | `ADR-0184-scoped-semantic-state-transitions.md` |
| 0185 | — | **Superseded by [ADR-0186](./ADR-0186-se | — | Division reading (rate / partition): the first genuine multi-step capability, el | `ADR-0185-division-reading.md` |
| 0186 | — | Proposed (scoping + seal-mechanism ADR;  | 2026-05-29 | Sealed candidate-graph injector lane: resume ADR-0170 W2–W5 under the ADR-0175 s | `ADR-0186-sealed-candidate-graph-injector-lane.md` |
| 0189 | — | Proposed (implemented in this PR). Exten | — | Comparative reading: anchor-verb widening + multi-word units | `ADR-0189-comparative-verb-unit-widening.md` |
| 0189 | a | Accepted (implemented). Builds on | — | First metric move: 3/47/0 → 4/46/0 (case 0024, comprehension-composed) | `ADR-0189a-day-enum-activity-first-flip.md` |
| 0191 | — | Proposed (implemented in this PR). Harde | — | Candidate-graph completeness guard (the missing wrong=0 leg) | `ADR-0191-candidate-graph-completeness-guard.md` |
| 0192 | — | Proposed (implemented in this PR). Widen | — | Open the discrete_count counted-noun class (firewall-backed) | `ADR-0192-discrete-count-open-noun-class.md` |
| 0193 | — | Proposed (implemented in this PR). | — | Aggregate total-across: the existential question frame | `ADR-0193-aggregate-existential-question-frame.md` |
| 0194 | — | Proposed (implemented in this PR). | — | Labeled-container subject entity shape | `ADR-0194-labeled-container-subject.md` |
| 0195 | — | Accepted / Implemented. | 2026-05-30. | Product Promotion Bridge | `ADR-0195-product-promotion-bridge.md` |
| 0196 | — | Accepted. | 2026-05-31. | Native Substrate Language Doctrine (Python / Rust / Zig) | `ADR-0196-native-substrate-language-doctrine.md` |
| 0197 | — | Accepted (ratified 2026-06-03) — impleme | 2026-05-31 | CORE-native Vision Compiler over the Delta-CRDT Substrate | `ADR-0197-vision-compiler-delta-crdt.md` |
| 0198 | — | Accepted (design spike) — Gap A protocol | 2026-05-31 | Motor as Efferent Modality — Protocol Gap & Governance (Design Spike) | `ADR-0198-motor-efferent-decoder-spike.md` |
| 0199 | — | Proposed | 2026-05-31 | Cross-Domain Learning Arena Contract | `ADR-0199-cross-domain-learning-arena-contract.md` |
| 0200 | — | Proposed (review-gated — every claim/tes | 2026-06-02 | Expert-Claim Reconciliation: Record the Fail-Closed Revert as Designed Behavior | `ADR-0200-expert-claim-reconciliation.md` |
| 0201 | — | Proposed (Phase 1 of `proof_chain`; stan | 2026-06-02 | Propositional Canonicalizer (the `proof_chain` keystone) | `ADR-0201-proposition-canonicalizer.md` |
| 0201 | .1 | Accepted (additive hardening of ADR-0201 | 2026-06-02 | Principled Out-of-Regime Detector (`out_of_decidable_regime`) | `ADR-0201.1-out-of-regime-detector.md` |
| 0202 | — | Accepted (normative contract — single so | 2026-06-02 | Proposition Representation Contract (`proof_chain`) | `ADR-0202-proposition-representation-contract.md` |
| 0203 | — | Accepted (proof_chain phase 2.1 — the is | 2026-06-02 | Binding-Graph Acyclicity Invariant (`circular_dependency` refusal) | `ADR-0203-binding-graph-acyclicity-invariant.md` |
| 0204 | — | Accepted (proof_chain phase 2.2 — struct | 2026-06-02 | Proof-Graph Builder (proof_chain's first binding-graph consumer) | `ADR-0204-proof-graph-builder.md` |
| 0205 | — | Accepted (proof_chain phase 2.3 — the fi | 2026-06-02 | modus_ponens + the Disagreement Rule (proof_chain's first inference rule) | `ADR-0205-modus-ponens-disagreement-rule.md` |
| 0206 | — | Accepted (scaffold step) — **cognition-p | 2026-06-03 (amended 2026-06-06) | Response Governance Bridge (scaffold) | `ADR-0206-response-governance-bridge.md` |
| 0207 | — | Accepted (ratified 2026-06-03) | 2026-06-03 | GSM8K Comprehension/Composition Substrate: Ratify · Freeze · Execute | `ADR-0207-gsm8k-substrate-ratification.md` |
| 0208 | — | Accepted (ratified 2026-06-03) — impleme | 2026-06-04 | Environmental Sensorium Loop | `ADR-0208-environmental-sensorium-loop.md` |
| 0209 | — | Accepted (ratified 2026-06-03) — impleme | 2026-06-04 | Sensorimotor Feedback Is Afferent | `ADR-0209-sensorimotor-feedback-contract.md` |
| 0210 | — | Proposed | 2026-06-05 | L10 finite grounding pack and adversarial wrong=0 fixtures | `ADR-0210-l10-grounding-pack.md` |
| 0211 | — | Accepted | 2026-06-06 | Conformal Falsification Bench | `ADR-0211-conformal-falsification-bench.md` |
| 0216 | — | Proposed | 2026-06-06 | Motor Verdict Lowering Prerequisite | `ADR-0216-motor-verdict-lowering.md` |
| 0217 | — | Accepted (ratified 2026-06-07) | 2026-06-07 | R2: Finite-Integer Linear-Constraint Setup Compiler (off-serving) | `ADR-0217-r2-finite-integer-constraint-compiler.md` |
| 0218 | — | Accepted (ratified 2026-06-11) — D1–D4 a | 2026-06-11 (proposed and ratified) | Proof-Carrying Coherence Promotion (logical arm of ADR-0021 v2) | `ADR-0218-proof-carrying-coherence-promotion.md` |
| 0219 | — | accepted | 2026-06-15 | Generation-dir atomic checkpoint (L10 continuity hardening) | `ADR-0219-generation-checkpoint-atomicity.md` |
| 0220 | — | Accepted (ratified 2026-06-15 by reposit | 2026-06-15 | Engine identity vs. build provenance (`code_revision` in the identity hash) | `ADR-0220-engine-identity-vs-build-provenance.md` |
| 0221 | — | accepted (applied 2026-06-15) | 2026-06-15 | Branch protection for a solo-maintainer public repo (required-checks-only) | `ADR-0221-codeowners-review-topology.md` |
| 0222 | — | Proposed (design-only). Implementation i | 2026-06-15 | FrameVerdict — Frame-General Closed-World Verdict | `ADR-0222-frame-verdict-closed-world.md` |
| 0223 | — | Proposed for architect ratification. Thi | 2026-06-19 | Semantic Substrate Affordance Audit and Foundation Alignment | `ADR-0223-semantic-substrate-affordance-audit.md` |
| 0224 | — | Proposed (docs-only until ratified; impl | 2026-06-20 | Foundational Subject Substrate Readiness and Cross-Domain Affordance Map | `ADR-0224-foundational-substrate-readiness-map.md` |
| 0225 | — | Accepted (2026-06-30) | — | ADR Corpus Hygiene, Numbering Policy, and Cross-Reference Governance | `ADR-0225-adr-corpus-hygiene.md` |
| 0225 | — | Accepted | 2026-06-22 | ContractResidual Read-Model | `ADR-0225-contract-residual-read-model.md` |
| 0226 | — | Accepted | — | ADR 0226: GSM8K Math Evaluation Corpus Generation | `ADR-0226-gsm8k-math-eval-corpus.md` |
| 0226 | — | Accepted | 2026-06-22 | ADR-0226 Ratification | `ADR-0226-ratification.md` |
| 0226 | — | Proposed | 2026-06-22 | Residual-Gated Practice Loop v1 | `ADR-0226-residual-gated-practice-loop-v1.md` |
| 0227 | — | Accepted | 2026-06-22 | ComputeBudgetPolicy Envelope | `ADR-0227-compute-budget-policy-envelope.md` |
| 0228 | — | Proposed | 2026-06-22 | Inert GeometricSearchRun Envelope | `ADR-0228-geometric-search-run-envelope.md` |
| 0229 | — | Proposed | 2026-06-22 | Contract/Proof Replay Adapter Boundary | `ADR-0229-contract-proof-replay-adapter-boundary.md` |
| 0230 | — | Proposed | 2026-06-22 | SealedPracticeTrace Boundary | `ADR-0230-sealed-practice-trace-boundary.md` |
| 0231 | — | Proposed | 2026-06-23 | First Candidate Operator Boundary | `ADR-0231-first-candidate-operator-boundary.md` |
| 0232 | — | Proposed | 2026-06-23 | CandidateAttempt Run-Binding Boundary | `ADR-0232-candidate-attempt-run-binding-boundary.md` |
| 0233 | — | Proposed | 2026-06-23 | Bound Practice Episode Sealing | `ADR-0233-bound-practice-episode-sealing.md` |
| 0234 | — | Proposed | 2026-06-23 | Second Candidate Operator Selection | `ADR-0234-second-candidate-operator-selection.md` |
| 0235 | — | Proposed | 2026-06-24 | Apple Silicon UMA Acceleration Lanes | `ADR-0235-apple-silicon-uma-acceleration-lanes.md` |
| 0236 | — | Proposed | 2026-06-25 | Engineering Principles for Masterful Cleanup | `ADR-0236-engineering-principles-for-masterful-cleanup.md` |
| 0237 | — | Draft | — | GeometricDelta ABI and Boundary Verification | `ADR-0237-geometricdelta-abi.md` |
| 0238 | — | Proposed (acceptance path: tests green + | 2026-07-11 | GoldTether-Modulated Supervised Autonomy | `ADR-0238-GoldTether-Modulated-Supervised-Autonomy.md` |
| 0239 | — | Proposed (acceptance path: tests green + | 2026-07-11 | Conformal Procrustes / Analogical Versor Search + Surprise Residual Dual | `ADR-0239-Conformal-Procrustes-Surprise-Dual-Operator.md` |
| 0240 | — | Proposed (acceptance path: tests green + | 2026-07-11 | Analogical Transfer Validation Harness + Biography Holonomy Blade | `ADR-0240-Analogical-Transfer-Validation-Harness-Biography-Holonomy.md` |
| 0241 | — | **Accepted** — ratified by Joshua Shay 2 | 2026-07-13 | Wave-Field Driven Hyperbolic Atlas and Resonant Algebraic Cognition | `ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md` |
| 0242 | — | **Accepted** — ratified by Joshua Shay 2 | 2026-07-13 (Drive authority); in-repo expansion 2026-07-15 | Deterministic Fibonacci Operators and Evidence-Gated Optimization | `ADR-0242-atlas-packing-and-fibonacci.md` |
| 0243 | — | Accepted — ratified by Joshua Shay 2026- | 2026-07-14 | Wave-Field Cognitive Lifecycle — Comprehension, Resonant Reasoning, and Lifelong | `ADR-0243-wave-field-cognitive-lifecycle-comprehension-reasoning-and-resonant-learning.md` |
| 0244 | — | **Accepted** — ratified by Joshua Shay o | 2026-07-17 | Wave-Field Identity Manifold and Inalienable Geometric Alignment | `ADR-0244-wave-field-identity-manifold-and-inalienable-geometric-alignment.md` |
| 0245 | — | **Accepted** — ratified by Joshua Shay o | 2026-07-17 | CGA Unification — Mechanical Sympathy, Boundary Rigor, and Eigendecomposition Me | `ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md` |
| 0246 | — | **Accepted** | 2026-07-18 | Induced Identity Action and Path Integrity | `ADR-0246-induced-identity-action-and-path-integrity.md` |
| 0247 | — | **Accepted** | 2026-07-18 | Multi-Port Residual Protocol — the Ring-2 Shared Control Grammar | `ADR-0247-multi-port-residual-protocol.md` |
| 0248 | — | **Accepted** | 2026-07-18 | Integrity-Coordinated Handoffs — the Ring-3 Coordination Seam | `ADR-0248-integrity-coordinated-handoffs.md` |
| 0249 | — | **Accepted** | 2026-07-18 | Reader→Hamiltonian Compiler — the Composition Frontier | `ADR-0249-reader-hamiltonian-compiler-composition-frontier.md` |
| 0250 | — | **Accepted** | 2026-07-18 | Tier-2 Multi-Entity Arithmetic — the Multi-Register Extension | `ADR-0250-tier2-multi-entity-arithmetic.md` |
| 0251 | — | §§1–4 (the recalibration decision — halt | 2026-07-19 | Reader-Arc Recalibration — Halt Bespoke-Per-Case Regex Work; Clean-Base Reset; P | `ADR-0251-reader-arc-recalibration-geometric-normalization-spike-proposal.md` |
| 0252 | — | **Accepted** — ratified 2026-07-19 by Jo | 2026-07-19 | The CORE Problem-Solving Paradigm — Expert Structure-Mapping on a Predictive-Pro | `ADR-0252-problem-solving-paradigm-consolidation.md` |
| 0253 | — | Accepted (Stage 1 governance freeze) | 2026-07-20 | Master Blueprint ADR Collision Resolution & Dual-Pack Boundary | `ADR-0253-master-blueprint-adr-collision-and-dual-pack-boundary.md` |
| 0254 | — | Accepted — ratified by Joshua Shay via t | 2026-07-23 | Grounded-Open Hedge Arm for the Shadow Coherence Gate | `ADR-0254-grounded-open-hedge-arm.md` |
| 0255 | — | Accepted (directive + framing ruled by J | 2026-07-23 | Discovery-Yield-Per-Served-Turn Baseline Telemetry | `ADR-0255-discovery-yield-baseline-telemetry.md` |
| 0256 | — | Accepted — ratified by Joshua Shay via t | 2026-07-23 | Deduction Serving Governed by an Earned Reliability License | `ADR-0256-deduction-serve-earned-license.md` |
| 0257 | — | Accepted — ratified by Joshua Shay via t | 2026-07-23 | English-clause argument band (Band v2-EN): opaque-atom propositional serving | `ADR-0257-english-clause-argument-band.md` |
| 0258 | — | Accepted — ratified by Joshua Shay via t | 2026-07-23 | Member-chain band (Band v3-MEM): singular membership + universal premises | `ADR-0258-member-chain-band.md` |
| 0259 | — | Accepted — ratified by Joshua Shay via t | 2026-07-23 | Conditional-membership fusion band (Band v4-CM) | `ADR-0259-conditional-membership-fusion-band.md` |
| 0260 | — | Accepted — ratified by Joshua Shay via t | 2026-07-24 | Band v5-VP: verb-predicate arguments, decided | `ADR-0260-verb-predicate-band.md` |
| 0261 | — | Accepted — ratified by Joshua Shay via t | 2026-07-24 | Band v6-EX: existential arguments, decided | `ADR-0261-existential-witness-band.md` |
| 0262 | — | Accepted — ratified by Joshua Shay via t | 2026-07-24 | Curriculum-grounded serving: exams answered from what was taught | `ADR-0262-curriculum-grounded-serving.md` |
| 0263 | — | Accepted — ratified by Joshua Shay via t | 2026-07-24 | The ratified-ledger bridge | `ADR-0263-ratified-ledger-bridge.md` |
| 0264 | — | Accepted — ratified by Joshua Shay 2026- | 2026-07-25 · **Ratified:** 2026-07-26 | Negative curriculum, premise scope, and what a curriculum band can earn | `ADR-0264-negative-curriculum-and-premise-scope.md` |
| 0265 | — | Accepted — ratified by Joshua Shay 2026- | 2026-07-27 · **Ratified:** 2026-07-27 | Negation belongs in the proposition graph, and clause grammar has one owner | `ADR-0265-negation-in-the-proposition-graph.md` |
