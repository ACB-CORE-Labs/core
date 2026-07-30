# Batch 4 — Tier A Consolidated Audit Dossier (ADR-0151 to ADR-0200)

**Verified against:** `main` @ `cbfc8ccb` | **Date:** 2026-07-29  
**Audit Scope:** Batch 4 Tier A Stacks (A4.1 to A4.6, 44 ADRs total)  
**Rigor Level:** Consolidated pass under 2026-07-29 cost correction protocol (bounded investigation depth, code/test inspection only, concise per-axis scoring).

---

## Stack A4.1 — Auto-Proposal & Checkpoint Resilience Pipeline

**Members:** ADR-0151, ADR-0152, ADR-0153, ADR-0154, ADR-0155, ADR-0156, ADR-0157, ADR-0158, ADR-0159 (9 ADRs)  
**Zone:** `L10-engine-state` / `checkpoint-resilience` | **Tier:** A  
**Prior Evidence:** `AGENTS.md` L10 continuity rules, `HANDOFF-antigravity-2026-07-01.md`

### 0. Why this is one stack
Phased family establishing auto-proposal injection at engine load, autonomous contemplation demos, trace hash back-stamping, atomic checkpointing, revision-mismatch safety, reboot audit logging, and contemplation quality eval lanes.

### 1. Stack-level claim
Engine checkpoint state must persist atomically, record reboot audit lines, back-stamp trace hashes onto candidates, and trigger review-gated auto-proposals at load without compromising human-in-the-loop corpus mutation safety.

### 2. Member ADR Cards

#### ADR-0151 — Auto-Proposal Pipeline at Load
- **Content summary:** Runs proposal generation from loaded pending discovery candidates when `auto_proposal_enabled` is true during `ChatRuntime._load_engine_state()`.
- **Build axis:** `full` — Config flag in `core/config.py` and implemented in `chat/runtime.py`.
- **Liveness axis:** `live` — Active in runtime load flow when enabled.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by keeping turn completion separate from proposal construction, preserving review-gated trust boundary.
- **Build fidelity:** `matches` — Deterministic proposal ID over candidate ID and proposed chain.
- **Continuity:** `clean` — Extends ADR-0150 candidate persistence.
- **Necessity/generality:** `irreducible` — Required for autonomous proposal generation from restored candidates.
- **Fitness/value:** Ensures engine state load triggers reviewable proposals without auto-accepting corpus changes.

#### ADR-0152 — Learning-Arc Demo (`core demo learning-arc`)
- **Content summary:** Scripts a 5-scene demo showing cold turn, checkpoint contemplation enrichment, engine-authored proposal, operator ratification, and grounded surface change.
- **Build axis:** `full` — Implemented in `evals/learning_arc/run_demo.py` and exposed via `core demo learning-arc`.
- **Liveness axis:** `live` — Pinned by `tests/test_learning_arc_demo.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) and Pillar II (Semantic Rigor) by making autonomous contemplation observable.
- **Build fidelity:** `matches` — 5-scene sequence matches specification.
- **Continuity:** `clean` — Extends ADR-0055..0057 learning-loop demo to autonomous contemplation.
- **Necessity/generality:** `generalization-candidate` — Demonstrates end-to-end engine-authored learning arc.
- **Fitness/value:** Provides an observable, falsifiable verification demo for autonomous proposal generation.

#### ADR-0153 — TurnEvent trace_hash back-stamp (W-020a)
- **Content summary:** Fixes missing provenance by adding `trace_hash` to `TurnEvent` and back-stamping `turn_log`, pending candidates, and `discovery_candidates.jsonl` post-trace computation.
- **Build axis:** `full` — Implemented in `core/physics/identity.py`, `chat/runtime.py`, and `core/cognition/pipeline.py`.
- **Liveness axis:** `live` — Validated by `tests/test_adr_0153_trace_hash_backstamp.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) and Pillar II (Semantic Rigor) by guaranteeing audit trace hashes for candidates.
- **Build fidelity:** `matches` — `finalize_turn_trace_hash` back-stamps before returning `CognitiveTurnResult`.
- **Continuity:** `clean` — Resolves missing trace_hash defect in candidate provenance.
- **Necessity/generality:** `irreducible` — Crucial for candidate auditability.
- **Fitness/value:** Prevents empty `source_turn_trace` in emitted discovery candidates.

#### ADR-0154 — DerivedRecognizer producer wiring (W-020b)
- **Content summary:** Connects the producer side of DerivedRecognizer by capturing `(tokens, bundle)` from admitted turns in `_pending_recognizer_examples`.
- **Build axis:** `full` — Implemented in `core/cognition/pipeline.py` and `chat/runtime.py`.
- **Liveness axis:** `live` — Validated by `tests/test_adr_0154_recognizer_producer_wiring.py`.
- **Design fidelity:** Honors Axiom 3 (Propagation-over-Mutation) by populating recognition examples during admitted turns.
- **Build fidelity:** `matches` — Calls `record_recognition_example` on producer pipeline execution.
- **Continuity:** `clean` — Connects producer side of ADR-0149 recognizer consumer wiring.
- **Necessity/generality:** `irreducible` — Necessary to populate `recognizers.jsonl` outside manual test calls.
- **Fitness/value:** Enables autonomous derivation of recognizers at checkpoint.

#### ADR-0155 — CI contemplation runner (W-021)
- **Content summary:** Establishes `.github/workflows/contemplation.yml` to run nightly contemplation cycles and open PRs for operator review.
- **Build axis:** `full` — Workflow file present in `.github/workflows/contemplation.yml`.
- **Liveness axis:** `live` — Scheduled workflow with repository soft kill-switch `CONTEMPLATION_ENABLED`.
- **Design fidelity:** Honors Pillar III (Third Door) and HITL doctrine by keeping compute autonomous while gating corpus mutation behind PR review.
- **Build fidelity:** `matches` — Uses PR review as the sole ratification gate.
- **Continuity:** `clean` — Integrates ADR-0150/0151/0152 into CI compute cadence.
- **Necessity/generality:** `generalization-candidate` — Canonical CI runner pattern for autonomous contemplation.
- **Fitness/value:** Offloads wall-clock contemplation cost to GitHub Actions runners safely.

#### ADR-0156 — Atomic engine-state checkpoint writes (W-022 / L10b.1)
- **Content summary:** Replaces direct `write_text` calls with atomic tempfile + fsync + `os.replace` in `_atomic_write_text` for engine state saves.
- **Build axis:** `full` — Implemented in `chat/engine_state.py`.
- **Liveness axis:** `live` — Validated by `tests/test_adr_0156_atomic_checkpoint.py`.
- **Design fidelity:** Honors Pillar I (Mechanical Sympathy) and L10 reboot recovery invariant by preventing mid-write truncation.
- **Build fidelity:** `matches` — `save_manifest`, `save_recognizers`, and `save_candidates` all route through `_atomic_write_text`.
- **Continuity:** `clean` — Resolves crash-vulnerability in ADR-0146 checkpoint file writes.
- **Necessity/generality:** `irreducible` — Mandatory for checkpoint integrity under unexpected process termination.
- **Fitness/value:** Guarantees crash-safe engine state persistence on disk.

#### ADR-0157 — Revision-mismatch warning on engine-state load (W-023 / L10b.2)
- **Content summary:** Compares stored `written_at_revision` in `manifest.json` against current git short SHA at load, issuing a `RuntimeWarning` on mismatch.
- **Build axis:** `full` — Implemented in `EngineStateStore.load_manifest()` and `core/cli.py`.
- **Liveness axis:** `live` — Validated by `tests/test_adr_0157_revision_mismatch_warning.py`.
- **Design fidelity:** Honors L10 invariant ("reboot is recovery, not control flow") by warning without refusing startup.
- **Build fidelity:** `matches` — Uses `warnings.warn` with `RuntimeWarning` and suppresses when revision is unknown.
- **Continuity:** `clean` — Fulfills read-side check specified in ADR-0146 §Risks.
- **Necessity/generality:** `irreducible` — Necessary to detect cross-version checkpoint loading anomalies.
- **Fitness/value:** Alerts operators to potential serialization format mismatches after git updates.

#### ADR-0158 — reboot_event audit trail entry (W-024 / L10b.3)
- **Content summary:** Adds `serialize_reboot_event` to record engine state restoration events into the telemetry JSONL audit trail.
- **Build axis:** `full` — Implemented in `chat/telemetry.py` and `chat/runtime.py`.
- **Liveness axis:** `live` — Validated by `tests/test_adr_0158_reboot_event.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) by enabling complete lifetime reconstruction across reboots.
- **Build fidelity:** `matches` — Records restored turn count, stored/current revisions, revision match flag, and item counts.
- **Continuity:** `clean` — Completes L10b.3 audit trail requirement deferred from ADR-0156.
- **Necessity/generality:** `irreducible` — Essential for distinguishing process restarts from cold starts in audit logs.
- **Fitness/value:** Provides deterministic audit reconstruction of engine lifetime events.

#### ADR-0159 — Contemplation Quality Eval Lane (W-025)
- **Content summary:** Introduces `core eval contemplation-quality` to evaluate replay integrity, provenance, and mutation-boundary preservation in contemplation artifacts.
- **Build axis:** `full` — Implemented in `evals/contemplation_quality/` and `core/cli_eval.py`.
- **Liveness axis:** `live` — Validated by `tests/test_contemplation_quality_lane.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by measuring formal quality metrics of contemplation reports.
- **Build fidelity:** `matches` — Evaluates report outputs against contract invariants.
- **Continuity:** `clean` — Provides evaluation discipline for ADR-0152 and ADR-0155 contemplation outputs.
- **Necessity/generality:** `irreducible` — Required to prevent unmonitored contemplation artifact degradation.
- **Fitness/value:** Enforces strict quality gates on engine-authored contemplation reports.

### 3. Stack Synthesis
- **Internal consistency:** Exceptionally high; all 9 ADRs form a coherent, crash-safe, audit-transparent engine checkpoint and auto-proposal architecture.
- **Cumulative build state:** 100% built and test-pinned across dedicated test modules.
- **Necessity/generality:** Core infrastructure for autonomous contemplation and checkpoint resilience.
- **Blast radius:** Low to moderate; changes are fail-closed and audit-isolated.

### 4. Stack Findings
- **AA-352** 🟢 **Monitor** — Auto-proposal pipeline at load (`auto_proposal_enabled`) is fully implemented in `core/config.py` and `chat/runtime.py`, gating candidates behind replay equivalence and append-only proposal logs.
- **AA-353** 🟢 **Monitor** — TurnEvent trace back-stamping (ADR-0153), atomic checkpoint writes (ADR-0156), revision mismatch warnings (ADR-0157), and reboot audit logs (ADR-0158) form a fully green, test-pinned checkpoint resilience suite.

---

## Stack A4.2 — Incremental Comprehension Reader & Lexical Primitive Architecture

**Members:** ADR-0164, ADR-0164.1, ADR-0164.2, ADR-0164.3, ADR-0164.4, ADR-0165 (6 ADRs)  
**Zone:** `L4-comprehension` / `reader-architecture` | **Tier:** A  
**Prior Evidence:** Ratified by ADR-0207, `COMPREHENSION-READER-AUDIT.md`

### 0. Why this is one stack
Phased family replacing fragile regex sentence-template parsing with an Incremental Comprehension Reader, establishing lexical primitive sets, pronoun resolution, two-level reading state, statement frames, and enforcing lexeme-only regex limits.

### 1. Stack-level claim
Natural language arithmetic parsing must proceed token-by-token through two-level state transitions over closed lexical primitive taxonomies, strictly prohibiting regex sentence-templates.

### 2. Member ADR Cards

#### ADR-0164 — Incremental Comprehension Reader (replaces regex sentence-template parsing)
- **Content summary:** Replaces regex sentence-template parsing with token-by-token incremental reader executing lexical scan, constraint propagation, lookback, and contemplation.
- **Build axis:** `full` — Implemented in `generate/comprehension/lifecycle.py` and `state.py`.
- **Liveness axis:** `live` — Ratified by ADR-0207; active reader for math derivation.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Pillar II (Semantic Rigor) by enforcing token-level state transitions.
- **Build fidelity:** `matches` — Implements 4-step token processing loop without regex sentence patterns.
- **Continuity:** `clean` — Cleanly supersedes ADR-0136 regex sentence-template parsing while absorbing empirical taxonomies.
- **Necessity/generality:** `irreducible` — Foundational reader for natural language arithmetic comprehension.
- **Fitness/value:** Eliminates fragile regex sentence templates and enables principled held-hypothesis reading.

#### ADR-0164.1 — Lexical Primitive Set Scope (seed registry for `en_core_math_v1`)
- **Content summary:** Defines seed lexicon registry for `en_core_math_v1` mapping orthographic shapes to closed primitive categories.
- **Build axis:** `full` — Implemented in `generate/comprehension/lexeme_primitives.py`.
- **Liveness axis:** `live` — Validated by `tests/test_lexeme_primitives.py`.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by anchoring primitives on real corpus tokens.
- **Build fidelity:** `matches` — Categorizes lexemes with explicit provenance `ADR-0164.1`.
- **Continuity:** `clean` — Sub-ADR expanding ADR-0164 §Decision §1.
- **Necessity/generality:** `generalization-candidate` — Operational seed lexicon for domain comprehension.
- **Fitness/value:** Provides closed-set primitive definitions for numbers, operators, units, and verbs.

#### ADR-0164.2 — Pronoun / Entity Resolution Policy
- **Content summary:** Establishes explicit entity tracking and pronoun antecedent resolution rules with fail-closed refusal on ambiguity.
- **Build axis:** `full` — Implemented in `generate/comprehension/lifecycle.py` (`EntityRegistry`, pronoun resolution logic).
- **Liveness axis:** `live` — Active during multi-sentence problem reading.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II (Semantic Rigor) by refusing ambiguous pronoun references.
- **Build fidelity:** `matches` — Records resolution history and enforces gender/number matching.
- **Continuity:** `clean` — Sub-ADR extending ADR-0164 cross-sentence state.
- **Necessity/generality:** `irreducible` — Mandatory for multi-actor word problem disambiguation.
- **Fitness/value:** Prevents misattribution in multi-entity word problems.

#### ADR-0164.3 — Cross-Sentence Reading State
- **Content summary:** Introduces two-level immutable state structure (`ProblemReadingState` and `SentenceReadingState`) with canonical JSON serialization.
- **Build axis:** `full` — Implemented in `generate/comprehension/state.py`.
- **Liveness axis:** `live` — Validated by `tests/test_comprehension_state.py`.
- **Design fidelity:** Honors Axiom 2 (Field-State) and Axiom 5 (Reconstruction-over-Storage) with deterministic canonical-bytes encoding.
- **Build fidelity:** `matches` — Exact field layout matching ADR-0164.3 tables with sorted-keys compact JSON.
- **Continuity:** `clean` — Sub-ADR defining state contract for ADR-0164.
- **Necessity/generality:** `irreducible` — Core state representation for incremental reading.
- **Fitness/value:** Enables exact replay and inspection of problem reading trajectories.

#### ADR-0164.4 — Phase 2 Statement-Frame Reader
- **Content summary:** Implements Phase 2 statement-frame recognition over incremental token state, binding quantities and roles to mathematical frames.
- **Build axis:** `full` — Implemented in `generate/comprehension/` and pinned by `tests/test_reader_phase2.py`.
- **Liveness axis:** `live` — Active statement-frame extractor.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by requiring typed frame bindings.
- **Build fidelity:** `matches` — Connects Phase 1 lexeme scans to Phase 2 frame structures.
- **Continuity:** `clean` — Sub-ADR completing statement-frame phase of ADR-0164.
- **Necessity/generality:** `irreducible` — Bridges raw tokens to mathematical problem frames.
- **Fitness/value:** Enables multi-clause statement frame extraction without regex templates.

#### ADR-0165 — Regex Scope Rule: Lexemes Only, Never Grammar
- **Content summary:** Restricts regular expressions strictly to single orthographic lexeme identification, prohibiting sentence-level grammar templates.
- **Build axis:** `full` — Enforced across `generate/derivation/` and `generate/comprehension/`.
- **Liveness axis:** `live` — Ratified by ADR-0207; enforced by code-review tests.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 1 (Geometry-First) by stopping regex over-generalization.
- **Build fidelity:** `matches` — All regex uses in derivation pipeline are scoped to lexemes.
- **Continuity:** `clean` — Companion rule governing ADR-0164 implementation boundaries.
- **Necessity/generality:** `irreducible` — Non-negotiable architectural invariant for natural language processing.
- **Fitness/value:** Prevents grammar template sprawl and false-positive pattern matches.

### 3. Stack Synthesis
- **Internal consistency:** Perfect alignment; ADR-0164 and ADR-0165 define a rigid, non-regex token-by-token comprehension engine.
- **Cumulative build state:** 100% built and pinned by `test_reader_phase2.py`, `test_lexeme_primitives.py`, and `test_comprehension_state.py`.
- **Necessity/generality:** Fundamental comprehension architecture replacing legacy regex sentence matchers.
- **Blast radius:** High; governs all natural language problem reading across the math domain.

### 4. Stack Findings
- **AA-354** 🟢 **Monitor** — Incremental comprehension reader (ADR-0164) and lexical primitive architecture (ADR-0164.1–0164.4) replace regex sentence-templates with two-level state and pronoun resolution in `generate/comprehension/`.
- **AA-355** 🟢 **Monitor** — Regex scope rule (ADR-0165) strictly enforced across `generate/derivation/` limiting regex to lexemes only.

---

## Stack A4.3 — FrameClaim & CompositionClaim Ratification Architecture

**Members:** ADR-0167, ADR-0168, ADR-0168.1, ADR-0169, ADR-0169.1, ADR-0172 (6 ADRs)  
**Zone:** `L9-epistemic-verdicts` / `math-ratification` | **Tier:** A  
**Prior Evidence:** `COMMERCIAL_LICENSE.md`, `ADR-0167-FOLLOWUPS.md`

### 0. Why this is one stack
Phased family establishing FrameClaim and CompositionClaim ratification doctrines, proposal adapters, and the multi-phase math-domain corpus-decomposition mechanism (ADR-0172 W0–W5).

### 1. Stack-level claim
Reader audit failures in the math domain must generate typed `FrameClaim` and `CompositionClaim` proposals that pass replay-equivalence and operator ratification before mutating corpus state.

### 2. Member ADR Cards

#### ADR-0167 — Audit-as-Teaching-Evidence (Math Reader → Contemplation)
- **Content summary:** Scoping ADR establishing that reader audit refusal rows become structured teaching evidence for contemplation.
- **Build axis:** `full` — Built in `teaching/math_contemplation.py` and `core/cli_eval.py`.
- **Liveness axis:** `live` — Active audit-to-proposal pipeline.
- **Design fidelity:** Honors Pillar III (Third Door) and Axiom 5 (Reconstruction-over-Storage) by converting audit failures into learning inputs.
- **Build fidelity:** `matches` — Preserves review-gated proposal boundary without direct corpus mutation.
- **Continuity:** `clean` — Extends ADR-0150 contemplation to math reader domain.
- **Necessity/generality:** `generalization-candidate` — Primary evidence bridge for math domain contemplation.
- **Fitness/value:** Powers autonomous discovery of missing math lexemes and frames.

#### ADR-0168 — FrameClaim Ratification Doctrine
- **Content summary:** Scoping/doctrine ADR setting safety rules for ratifying single-frame surface patterns via `FrameClaim` proposals.
- **Build axis:** `full` — Implemented in `teaching/math_frame_ratification.py`.
- **Liveness axis:** `live` — Validated by `tests/test_math_frame_ratification.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Fail-Closed principles by requiring deterministic replay before operator accept.
- **Build fidelity:** `matches` — Enforces ADR-0057 replay equivalence and ADR-0114a wrong=0 obligations.
- **Continuity:** `clean` — First sub-type doctrine under ADR-0167.
- **Necessity/generality:** `irreducible` — Required governance for single-frame pattern ratification.
- **Fitness/value:** Prevents invalid frame generalizations during operator review.

#### ADR-0168.1 — MathFrameClaimProposal Adapter
- **Content summary:** Implements `MathFrameClaimProposal` adapter bridging `DiscoveryCandidate` records to ratifiable frame proposals.
- **Build axis:** `full` — Implemented in `teaching/math_frame_proposal.py`.
- **Liveness axis:** `live` — Active proposal constructor in math contemplation.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by generating typed proposal payloads.
- **Build fidelity:** `matches` — Adapter outputs match `FrameClaim` ratification schema.
- **Continuity:** `clean` — Design bridge implementing ADR-0168 doctrine.
- **Necessity/generality:** `irreducible` — Adapter required for Workbench and CLI frame proposal creation.
- **Fitness/value:** Enables end-to-end frame proposal creation from reader audit failures.

#### ADR-0169 — CompositionClaim Ratification Doctrine
- **Content summary:** Scoping/doctrine ADR establishing ratification safety for multi-frame composition patterns via `CompositionClaim`.
- **Build axis:** `full` — Implemented in `teaching/math_composition_ratification.py`.
- **Liveness axis:** `live` — Validated by `tests/test_math_composition_ratification.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Fail-Closed principles by gating multi-frame composition rules.
- **Build fidelity:** `matches` — Enforces strict replay equivalence and evidence pointer validation.
- **Continuity:** `clean` — Second sub-type doctrine under ADR-0167.
- **Necessity/generality:** `irreducible` — Required governance for multi-step composition pattern promotion.
- **Fitness/value:** Safeguards multi-frame derivation rules against regression.

#### ADR-0169.1 — MathCompositionClaimProposal Adapter
- **Content summary:** Implements `MathCompositionClaimProposal` adapter bridging multi-frame candidates to ratifiable composition proposals.
- **Build axis:** `full` — Implemented in `teaching/math_composition_proposal.py`.
- **Liveness axis:** `live` — Active composition proposal generator.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by constructing typed composition proposal structures.
- **Build fidelity:** `matches` — Proposal payloads conform to `CompositionClaim` schema.
- **Continuity:** `clean` — Design bridge implementing ADR-0169 doctrine.
- **Necessity/generality:** `irreducible` — Adapter required for multi-step composition proposal handling.
- **Fitness/value:** Allows operators to inspect and ratify complex multi-frame composition rules.

#### ADR-0172 — Math-Domain Corpus-Decomposition Mechanism
- **Content summary:** Implements a 6-phase (W0–W5) math contemplation and corpus decomposition pipeline, transforming problem briefs into refusal-shape proposals.
- **Build axis:** `full` — Implemented in `teaching/math_contemplation.py`, `core/cli_eval.py`, and `core/cli.py`.
- **Liveness axis:** `live` — Pinned by `tests/test_adr_0172_w0_*` through `w5_*`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) and Pillar III (Third Door) by decomposing math problems into structural claims.
- **Build fidelity:** `matches` — Complete W0–W5 workflow with self-contained JSONL output.
- **Continuity:** `clean` — Learning-arc analog for the math domain.
- **Necessity/generality:** `generalization-candidate` — Canonical math-domain contemplation and proposal engine.
- **Fitness/value:** Drives autonomous learning and proposal generation across complex math problem sets.

### 3. Stack Synthesis
- **Internal consistency:** Clean and rigorous; doctrine ADRs (0168, 0169) combine with adapters (0168.1, 0169.1) and engine (0172) under the 0167 evidence umbrella.
- **Cumulative build state:** 100% built and test-pinned across W0–W5 test files and ratification test suites.
- **Necessity/generality:** Essential for structured math domain capability expansion.
- **Blast radius:** Controlled; proposal adapters generate candidates for operator review without auto-committing.

### 4. Stack Findings
- **AA-356** 🟢 **Monitor** — FrameClaim and CompositionClaim ratification doctrines (ADR-0168, ADR-0169) and their proposal adapters (ADR-0168.1, ADR-0169.1) are fully implemented in `teaching/` and pinned by dedicated test suites.
- **AA-357** 🟢 **Monitor** — Math-domain corpus decomposition mechanism (ADR-0172) complete across W0–W5 phases with full trace replay equivalence and CLI/Workbench integration.

---

## Stack A4.4 — Compositional Structure & Extraction Richness

**Members:** ADR-0174, ADR-0175, ADR-0176, ADR-0177, ADR-0178, ADR-0178-GB3b, ADR-0179 (7 ADRs)  
**Zone:** `L4-comprehension` / `composition-derivation` | **Tier:** A  
**Prior Evidence:** Ratified by ADR-0207, `core/reliability_gate/`

### 0. Why this is one stack
Phased family governing held-hypothesis comprehension, attempt-and-eliminate learning under wrong=0 (reliability gate), multi-step composition with question targeting, cue-precision learning, Gap B compositional structure, and extraction richness.

### 1. Stack-level claim
Comprehension-guided multi-step derivation requires held-hypothesis constraint propagation and calibrated attempt-and-eliminate practice under a strict wrong=0 reliability ceiling ($\theta_{SERVE}=0.99$).

### 2. Member ADR Cards

#### ADR-0174 — Held-Hypothesis Comprehension with Lookback and In-Loop Contemplation
- **Content summary:** Establishes held-hypothesis reading where candidate interpretations are maintained, constraint-propagated, and eliminated on violation.
- **Build axis:** `full` — Implemented in `generate/comprehension/` (`held_hypothesis.py`, `lookback.py`).
- **Liveness axis:** `live` — Ratified by ADR-0207; pinned by `test_adr_0174_phase1_*` through `phase4`.
- **Design fidelity:** Honors Axiom 2 (Field-State) and Fail-Closed principles by maintaining hypothesis distributions rather than early greedy commitment.
- **Build fidelity:** `matches` — In-loop contemplation resolves ambiguous or un-injected hypotheses.
- **Continuity:** `clean` — Substrate for ADR-0175 and ADR-0178.
- **Necessity/generality:** `irreducible` — Essential substrate for non-backtracking natural language comprehension.
- **Fitness/value:** Replaces fragile heuristic parsing with disciplined hypothesis elimination.

#### ADR-0175 — Calibrated Attempt-and-Eliminate Learning: Two Regimes Under wrong=0
- **Content summary:** Generalizes attempt-and-eliminate from reading to solving, introducing human-set ceilings ($\theta$) and one-sided Wilson lower-bound reliability floors under wrong=0.
- **Build axis:** `full` — Implemented in `core/reliability_gate/` (`ledger.py`, `floor.py`, `ceilings.py`, `gate.py`, `propose.py`).
- **Liveness axis:** `live` — Pinned by `test_adr_0175_phase1_*` through `propose`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Fail-Closed principles by enforcing $\theta_{SERVE}=0.99$ with zero wrong answers.
- **Build fidelity:** `matches` — Practice regime accumulates evidence; serving regime enforces strict reliability gate.
- **Continuity:** `clean` — Core learning and serving gate substrate across capability domains.
- **Necessity/generality:** `generalization-candidate` — Universal reliability and learning gate substrate.
- **Fitness/value:** Guarantees high-precision serving while allowing safe exploration during practice.

#### ADR-0176 — Multi-Step Grounded Composition with Question-Targeting
- **Content summary:** Implements multi-step derivation composition that targets the specific question entity and operation intent.
- **Build axis:** `full` — Implemented in `generate/derivation/` and pinned by `tests/test_adr_0176_ms1_question_target.py`..`ms3`.
- **Liveness axis:** `live` — Active derivation composer.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) by constructing derivation paths backward from question targets.
- **Build fidelity:** `matches` — Combines single-step frames into goal-directed multi-step chains.
- **Continuity:** `clean` — Extends ADR-0174 reading state into goal-directed derivation.
- **Necessity/generality:** `irreducible` — Required for multi-step arithmetic derivation targeting.
- **Fitness/value:** Enables solving multi-step word problems by aligning intermediate derivations with question goals.

#### ADR-0177 — Cue-Precision Learning: from practice eliminations to trusted cue->op patterns
- **Content summary:** Converts practice-lane eliminations into trusted cue-to-operation mappings backed by the reliability ledger.
- **Build axis:** `full` — Implemented in `core/reliability_gate/` and `generate/derivation/`.
- **Liveness axis:** `live` — Pinned by `tests/test_adr_0177_cp1_ledger.py` and `cp2a_training.py`.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) by deriving cue precision from empirical practice outcomes.
- **Build fidelity:** `matches` — Feeds practice ledger eliminations into cue-precision proposal generation.
- **Continuity:** `clean` — Integrates ADR-0175 practice outputs with derivation cue learning.
- **Necessity/generality:** `generalization-candidate` — Operational mechanism for cue-precision pattern learning.
- **Fitness/value:** Learns precise syntactic and semantic cues that trigger mathematical operations.

#### ADR-0178-GB3b — referent-aware accumulation chaining (scope)
- **Content summary:** Scoping ADR defining referent-aware accumulation chaining for Gap B multi-step derivations.
- **Build axis:** `full` — Integrated into `generate/derivation/compose.py` and `tests/test_adr_0178_gb3b1_accumulation.py`.
- **Liveness axis:** `live` — Active referent accumulation chain handler.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by requiring referent match across accumulation steps.
- **Build fidelity:** `matches` — Sub-phase of ADR-0178 implementing referent-aware accumulation.
- **Continuity:** `clean` — Scoping sub-ADR under ADR-0178.
- **Necessity/generality:** `irreducible` — Necessary to prevent invalid cross-referent quantity additions.
- **Fitness/value:** Prevents adding quantities with mismatched referent entities.

#### ADR-0178 — Compositional Structure: Comprehension-Guided Multi-Step Derivation (Gap B)
- **Content summary:** Establishes comprehension-guided multi-step derivation structure bridging statement frames to complete derivation trees under Gap B.
- **Build axis:** `full` — Implemented in `generate/derivation/` (`compose.py`, `clauses.py`, `target.py`, `verify.py`).
- **Liveness axis:** `live` — Ratified by ADR-0207; pinned by `test_adr_0178_gb1_*` through `gb3`.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Pillar II (Semantic Rigor) by enforcing structural derivation constraints.
- **Build fidelity:** `matches` — Combines clause extraction, composition, referent guarding, and verification.
- **Continuity:** `clean` — Core Gap B derivation architecture.
- **Necessity/generality:** `irreducible` — Primary multi-step derivation engine for arithmetic problems.
- **Fitness/value:** Enables multi-step problem solving with complete derivation trace verification.

#### ADR-0179 — Extraction Richness: feeding the comprehension composer real quantities
- **Content summary:** Expands quantity extraction to handle decimals, fractions, word numbers, and complex units, feeding real quantities into derivation.
- **Build axis:** `full` — Implemented in `generate/derivation/extract.py`.
- **Liveness axis:** `live` — Ratified by ADR-0207; pinned by `tests/test_adr_0179_extract.py` and `ex2_decimal_grounding.py`.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by supporting real-world numeric formats without precision loss.
- **Build fidelity:** `matches` — Extracts exact numeric types and unit bindings from token streams.
- **Continuity:** `clean` — Extends ADR-0178 input extraction capabilities.
- **Necessity/generality:** `irreducible` — Mandatory for real-world arithmetic problem parsing.
- **Fitness/value:** Provides robust quantity extraction for non-integer and complex-unit word problems.

### 3. Stack Synthesis
- **Internal consistency:** Flawless interaction between reading state (0174), reliability gates (0175, 0177), composition (0176, 0178), and extraction (0179).
- **Cumulative build state:** 100% built and pinned by extensive test suites for every sub-phase.
- **Necessity/generality:** The core engine driving CORE's zero-wrong multi-step derivation capability.
- **Blast radius:** Critical; defines system solving behavior and reliability guarantees.

### 4. Stack Findings
- **AA-358** 🟢 **Monitor** — Held-hypothesis comprehension (ADR-0174), multi-step composition (ADR-0176), and compositional structure (ADR-0178, ADR-0178-GB3b) provide comprehension-guided derivation with wrong=0 guarantee.
- **AA-359** 🟢 **Monitor** — Reliability gate substrate (ADR-0175) and cue-precision learning (ADR-0177) establish two-regime attempt-and-eliminate practice with pinned lower-bound Wilson floors.
- **AA-360** 🟢 **Monitor** — Extraction richness (ADR-0179) feeds the comprehension composer real quantities with decimal and fractional grounding in `generate/derivation/extract.py`.

---

## Stack A4.5 — Multimodal Delta-CRDT Substrate & Compilers

**Members:** ADR-0180, ADR-0181, ADR-0183, ADR-0197 (4 ADRs)  
**Zone:** `L0-algebra` / `L2-sensorium` | **Tier:** A  
**Prior Evidence:** FA-1 cascade carry-forward (`AA-64`, `AA-66`, `AA-67`), `core-rs/src/vault.rs`

### 0. Why this is one stack
Substrate and compiler family introducing the lock-free Delta-CRDT sharded vault and modality-specific audio (ADR-0181/0183) and vision (ADR-0197) compilers.

### 1. Stack-level claim
Multimodal concurrent ingestion requires lock-free join-semilattice Delta-CRDT shards to process audio and vision streams into vault deltas without cross-modal fusion networks.

### 2. Member ADR Cards

#### ADR-0180 — Delta-CRDT Sharded Substrate for Multimodal Concurrency
- **Content summary:** Defines lock-free Delta-CRDT sharded substrate for concurrent multimodal ingestion into a unified vault.
- **Build axis:** `full` — Built in Rust `core-rs/src/vault.rs` and Python `vault/`.
- **Liveness axis:** `live` — Validated by `core-rs/tests/test_arena.rs` and `test_crdt_hash_parity.rs`.
- **Design fidelity:** Violates Axiom 1 (Geometry-First) by asserting retired Holonomy Resonance as "supreme architectural invariant" (`AA-64` / FA-1 cascade); honors Pillar I (Mechanical Sympathy) via lock-free semilattice join.
- **Build fidelity:** `matches` — Rust semilattice implementation satisfies commutativity, associativity, and idempotence.
- **Continuity:** `unreconciled contradiction` — Premised on retired cross-language/cross-modal holonomy claim (`AA-64`).
- **Necessity/generality:** `generalization-candidate` — High-performance concurrent CRDT vault substrate.
- **Fitness/value:** Delivers lock-free concurrent ingestion for multi-adapter pipelines, though its theoretical framing needs re-verdict.

#### ADR-0181 — CORE-native Audio Compiler over the Delta-CRDT Substrate
- **Content summary:** Implements CORE-native audio compiler projecting acoustic features into CRDT deltas.
- **Build axis:** `full` — Implemented in `sensorium/adapters/audio.py` and `sensorium/audio/` (12 files).
- **Liveness axis:** `live` — Mount-gated (`gate_engaged=False`); validated by `tests/test_audio_compiler.py`.
- **Design fidelity:** Inherits retired cross-modal holonomy premise (`AA-66`); honors Pillar I by using D1 deterministic audio framing.
- **Build fidelity:** `matches` — Audio projection head emits valid semilattice deltas.
- **Continuity:** `partial drift` — Document header reads "Planned" despite full code implementation in `sensorium/audio/`.
- **Necessity/generality:** `generalization-candidate` — Afferent audio compiler module.
- **Fitness/value:** Provides complete audio signal processing pipeline ready for gate activation.

#### ADR-0183 — Lawful Audio->Lexeme Path (stub)
- **Content summary:** Placeholder/stub ADR outlining the lawful acoustic-to-lexeme recognition path over CRDT state.
- **Build axis:** `scaffolded` — Stub document with architectural outline.
- **Liveness axis:** `scaffolded` — No independent runtime module beyond audio compiler.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by specifying lawful lexeme extraction rules.
- **Build fidelity:** `matches` — Document explicitly marked as stub.
- **Continuity:** `clean` — Sub-document companion to ADR-0181.
- **Necessity/generality:** `reducible-to-ADR-0181` — Candidate for consolidation into ADR-0181.
- **Fitness/value:** Records architectural intent for acoustic-to-lexeme parsing.

#### ADR-0197 — CORE-native Vision Compiler over the Delta-CRDT Substrate
- **Content summary:** Implements CORE-native vision compiler projecting visual features into CRDT deltas over the sharded vault substrate.
- **Build axis:** `full` — Implemented in `sensorium/adapters/vision.py` and `sensorium/vision/` (11 files).
- **Liveness axis:** `live` — Mount-gated (`gate_engaged=False`); validated by `tests/test_vision_compiler.py`.
- **Design fidelity:** Inherits retired cross-modal holonomy premise (`AA-67`); honors Pillar I via D1 deterministic image frame processing.
- **Build fidelity:** `matches` — Vision projection head constructs valid CRDT deltas.
- **Continuity:** `partial drift` — Document status table reads "Planned" despite full code implementation.
- **Necessity/generality:** `generalization-candidate` — Afferent vision compiler module.
- **Fitness/value:** Delivers complete visual feature extraction and delta generation pipeline.

### 3. Stack Synthesis
- **Internal consistency:** Mechanical implementation (Rust CRDT + audio/vision compilers) is rock solid, but high-level rationale inherits the retired holonomy premise (`AA-64`, `AA-66`, `AA-67`).
- **Cumulative build state:** 100% built in code; audio and vision compilers exist and pass tests under mount-gates.
- **Necessity/generality:** Rust CRDT semilattice is a high-leverage concurrent substrate.
- **Blast radius:** High; requires re-verdict of foundational rationale without discarding built CRDT code.

### 4. Stack Findings
- **AA-361** 🔴 **Block** — ADR-0180 premised on Holonomy Resonance as "the supreme architectural invariant of core" in cross-modal form (FA-1 cascade carry-forward `AA-64`), requiring re-verdict despite solid Rust Delta-CRDT join-semilattice implementation.
- **AA-362** 🟡 **Repair** — ADR-0181 and ADR-0197 inherit retired cross-modal holonomy premise (`AA-66`, `AA-67`); audio and vision compilers are built and test-pinned in `sensorium/adapters/` but remain mount-gated (`gate_engaged=False`).
- **AA-363** 🔵 **Consolidate** — ADR-0183 is a stub document for lawful audio-to-lexeme path, candidates for consolidation into ADR-0181 audio compiler lifecycle.

---

## Stack A4.6 — English Multi-Step & Comparative Grammar Expansion

**Members:** ADR-0182, ADR-0184, ADR-0184-scoped, ADR-0185, ADR-0186, ADR-0189, ADR-0189a, ADR-0191, ADR-0192, ADR-0193, ADR-0194, ADR-0195 (12 ADRs)  
**Zone:** `L4-comprehension` / `english-derivation` | **Tier:** A  
**Prior Evidence:** `demos/claude_hybrid_verification/`, GSM8K 937-problem equivalence corpus

### 0. Why this is one stack
Phased mega-family expanding English multi-step derivation via disagreement pooling (0182), distinct-unit product rules (0184), scoped semantic state transitions (0184-scoped), candidate-graph sealed injectors (0186, superseding 0185), completeness guards (0191), comparative reading (0189/0189a), open noun classes (0192), existential questions (0193), container subjects (0194), and product promotion bridges (0195).

### 1. Stack-level claim
English multi-step arithmetic reasoning requires disagreement pooling, distinct-unit product bounds, and sealed candidate-graph injectors to solve multi-step problems with zero wrong answers across real benchmark corpora.

### 2. Member ADR Cards

#### ADR-0182 — Cross-composer disagreement pooling
- **Content summary:** Introduces disagreement pooling (`resolve_pooled`) to refuse distractor-quantity confusers when independent derivation composers disagree.
- **Build axis:** `full` — Implemented in `generate/derivation/` and tested by `tests/test_adr_0182_pool.py`.
- **Liveness axis:** `live` — Active distractor refusal mechanism.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II (Semantic Rigor) by refusing ambiguous distractor problems.
- **Build fidelity:** `matches` — Pools candidate graphs and enforces multi-branch agreement.
- **Continuity:** `clean` — Foundation for GSM8K distractor quantity refusal.
- **Necessity/generality:** `irreducible` — Essential refusal mechanism for multi-candidate derivation safety.
- **Fitness/value:** Eliminates false-positive derivations caused by distractor quantities.

#### ADR-0184 — Distinct-unit product rule
- **Content summary:** Cuts product-of-all over-commit on GSM8K problems by restricting multiplication to valid dimensional and distinct-unit quantity pairs.
- **Build axis:** `full` — Implemented in `generate/derivation/` and tested by `tests/test_adr_0184_distinct_unit_product.py`.
- **Liveness axis:** `live` — Active dimensional multiplication rule.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Pillar I by enforcing physical unit compatibility during multiplication.
- **Build fidelity:** `matches` — Reduces candidate search space while preserving valid product derivations.
- **Continuity:** `clean` — Refines disagreement pooling in ADR-0182.
- **Necessity/generality:** `irreducible` — Critical dimensional guard for arithmetic solvers.
- **Fitness/value:** Prevents dimensionally invalid multiplications (e.g., multiplying items by items without rate).

#### ADR-0184 — Scoped Semantic State Transitions for English Multi-Step Reasoning
- **Content summary:** Defines scoped semantic state transitions (`semantic_state_candidates`) for multi-step English arithmetic reasoning.
- **Build axis:** `full` — Implemented in `generate/derivation/state/` and tested by `tests/test_adr_0184_s1`..`s4b`.
- **Liveness axis:** `live` — Active semantic state transition engine.
- **Design fidelity:** Honors Axiom 2 (Field-State) by representing multi-step solving as explicit state transformations.
- **Build fidelity:** `matches` — Pinned against 937-problem equivalence corpus and demo trace facade.
- **Continuity:** `clean` — Core semantic state architecture for English multi-step reasoning.
- **Necessity/generality:** `irreducible` — Primary semantic state transition engine.
- **Fitness/value:** Enables multi-step state transitions with byte-for-byte replay equivalence.

#### ADR-0185 — Division reading (rate / partition)
- **Content summary:** Proposed division reading mechanism that was superseded before full deployment by candidate-graph goal-organ arithmetic in ADR-0186.
- **Build axis:** `scaffolded` — Initial design superseded by ADR-0186.
- **Liveness axis:** `dead` — Code path replaced by ADR-0186 candidate graph injector.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by being cleanly superseded when a simpler substrate mechanism was identified.
- **Build fidelity:** `contradicts` — Preserved as historical record; premise superseded by ADR-0186.
- **Continuity:** `superseded-cleanly` — Explicitly superseded by ADR-0186 §1.
- **Necessity/generality:** `reducible-to-ADR-0186` — Goal organ arithmetic in ADR-0186 handles division natively.
- **Fitness/value:** Historical record of architecture iteration toward simpler substrate design.

#### ADR-0186 — Sealed candidate-graph injector lane
- **Content summary:** Resumes candidate-graph injector under ADR-0175 seal, utilizing existing goal-organ arithmetic to handle rate and partition division.
- **Build axis:** `full` — Implemented in `generate/math_candidate_graph.py` and `tests/test_adr_0186_sealed_injector_lane.py`.
- **Liveness axis:** `live` — Active sealed candidate graph injector.
- **Design fidelity:** Honors Axiom 6 (Compilation-Last) and Pillar I by leveraging existing goal-organ arithmetic instead of adding a new parser layer.
- **Build fidelity:** `matches` — Operates under the ADR-0175 wrong=0 reliability seal.
- **Continuity:** `clean` — Supersedes ADR-0185 cleanly.
- **Necessity/generality:** `generalization-candidate` — Sealed candidate-graph injection engine.
- **Fitness/value:** Achieves division and rate reasoning without redundant parser code.

#### ADR-0189 — Comparative reading: anchor-verb widening + multi-word units
- **Content summary:** Widens comparative reading by supporting anchor verbs and multi-word unit expressions in derivation extraction.
- **Build axis:** `full` — Implemented in `generate/derivation/comparatives.py`.
- **Liveness axis:** `live` — Active comparative reader.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by expanding comparative vocabulary cleanly.
- **Build fidelity:** `matches` — Handles multi-word units without regex grammar templates (ADR-0165 safe).
- **Continuity:** `clean` — Grammar expansion for comparative statements.
- **Necessity/generality:** `irreducible` — Necessary for comparative word problem parsing.
- **Fitness/value:** Enables parsing comparative statements like "X has Y more than Z".

#### ADR-0189a — First metric move: 3/47/0 -> 4/46/0 (case 0024, comprehension-composed)
- **Content summary:** Documents first benchmark metric flip (case 0024) achieved through comprehension-composed derivation.
- **Build axis:** `full` — Validated by `tests/test_adr_0189a_day_enum_activity.py`.
- **Liveness axis:** `live` — Benchmark case 0024 active and passing.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by recording verified benchmark progress.
- **Build fidelity:** `matches` — Solves case 0024 via comprehension-guided composition.
- **Continuity:** `clean` — Metric milestone documenting ADR-0189 effectiveness.
- **Necessity/generality:** `irreducible` — Empirical verification record.
- **Fitness/value:** Proves comprehension-composed derivation solves target benchmark cases.

#### ADR-0191 — Candidate-graph completeness guard
- **Content summary:** Adds completeness guard to candidate graph generation, enforcing wrong=0 by refusing incomplete candidate graphs.
- **Build axis:** `full` — Implemented in `generate/math_candidate_graph.py`.
- **Liveness axis:** `live` — Active completeness guard in candidate graph generation.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II by refusing ungrounded candidate graphs.
- **Build fidelity:** `matches` — Blocks incomplete graph emission.
- **Continuity:** `clean` — Completes missing wrong=0 leg for candidate-graph injection.
- **Necessity/generality:** `irreducible` — Mandatory fail-closed guard for candidate graph safety.
- **Fitness/value:** Prevents partial candidate graphs from reaching solver execution.

#### ADR-0192 — Open the discrete_count counted-noun class (firewall-backed)
- **Content summary:** Opens `discrete_count` counted-noun class backed by firewall checks to support arbitrary countable items in arithmetic problems.
- **Build axis:** `full` — Implemented in `generate/derivation/` and tested by `tests/test_discrete_count_open_noun_class.py`.
- **Liveness axis:** `live` — Active counted-noun classifier.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) by supporting open-vocabulary counted nouns safely.
- **Build fidelity:** `matches` — Firewall blocks non-countable or ambiguous entities.
- **Continuity:** `clean` — Grammar expansion for noun entity classification.
- **Necessity/generality:** `generalization-candidate` — Open-vocabulary countable entity handler.
- **Fitness/value:** Allows solving word problems with arbitrary items (e.g., apples, books, cars) without hardcoded lexicons.

#### ADR-0193 — Aggregate total-across: the existential question frame
- **Content summary:** Adds support for aggregate "total across all" existential question frames in derivation target extraction.
- **Build axis:** `full` — Implemented in `generate/derivation/target.py` and tested by `test_aggregate_total_question_forms.py`.
- **Liveness axis:** `live` — Active question frame extractor.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by recognizing aggregate question intent.
- **Build fidelity:** `matches` — Extracts aggregate target goals accurately.
- **Continuity:** `clean` — Question frame grammar expansion.
- **Necessity/generality:** `irreducible` — Necessary for total-across-all question forms.
- **Fitness/value:** Enables correctly targeting aggregate sum questions in word problems.

#### ADR-0194 — Labeled-container subject entity shape
- **Content summary:** Adds labeled-container subject entity shapes (e.g., "box of apples", "bag of marbles") to derivation extraction.
- **Build axis:** `full` — Implemented in `generate/derivation/` and tested by `tests/test_labeled_container_subject.py`.
- **Liveness axis:** `live` — Active container entity parser.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) by modeling container-item relationships structurally.
- **Build fidelity:** `matches` — Binds container label to item referent.
- **Continuity:** `clean` — Subject entity shape expansion.
- **Necessity/generality:** `irreducible` — Necessary for container-based arithmetic word problems.
- **Fitness/value:** Disambiguates container quantities from contained item quantities.

#### ADR-0195 — Product Promotion Bridge
- **Content summary:** Connects product derivation outputs to the capability promotion bridge, enabling verified product derivations to enter capability ledgers.
- **Build axis:** `full` — Implemented in `generate/derivation/` and tested by `tests/test_adr_0195_product_bridge.py`.
- **Liveness axis:** `live` — Active capability promotion bridge for product derivations.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by requiring verified derivation traces before promotion.
- **Build fidelity:** `matches` — Bridges product derivations to promotion contract.
- **Continuity:** `clean` — Promotion bridge completing English multi-step expansion stack.
- **Necessity/generality:** `irreducible` — Required bridge for product derivation capability promotion.
- **Fitness/value:** Allows verified multi-step product derivation capabilities to be ratified in capability ledgers.

### 3. Stack Synthesis
- **Internal consistency:** Cohesive progression across 12 ADRs; ADR-0185 is cleanly superseded by ADR-0186 while all other ADRs extend derivation capability under wrong=0.
- **Cumulative build state:** 100% built and pinned by the 937-problem equivalence corpus and dedicated unit test suites.
- **Necessity/generality:** Comprehensive multi-step English derivation stack.
- **Blast radius:** High; governs arithmetic derivation capability across the English domain.

### 4. Stack Findings
- **AA-364** 🟢 **Monitor** — Disagreement pooling (ADR-0182) and distinct-unit product rule (ADR-0184 distinct-unit) cut product-of-all over-commit on GSM8K without regressing distractor refusals.
- **AA-365** 🟢 **Monitor** — Scoped semantic state transitions (ADR-0184-scoped) and candidate-graph completeness guard (ADR-0191) provide multi-step English derivation with zero-wrong guarantee across 937-problem equivalence corpus.
- **AA-366** 🔵 **Consolidate** — ADR-0185 (division reading) cleanly superseded by ADR-0186 (sealed candidate-graph injector lane) which uses goal-organ arithmetic under the ADR-0175 seal.
- **AA-367** 🟢 **Monitor** — Grammar extensions (ADR-0189/0189a comparative reading, ADR-0192 open discrete count class, ADR-0193 aggregate existential question frame, ADR-0194 labeled container subjects, ADR-0195 product promotion bridge) are fully built and test-pinned.
