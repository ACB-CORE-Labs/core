# Batch 3 — Tier B Consolidated Audit Cards

**Corpus Range:** ADR-0101 to ADR-0150 (Tier B Zones B3.1–B3.6, 35 ADRs total)  
**Verified against:** `main` @ `cbfc8ccb` (2026-07-29)  
**Governing Charter:** `docs/adr-audit/00-scope-and-method.md` (2026-07-29 cost-corrected rigor tier)

---

## Executive Summary & Batch Rollup

This document consolidates Tier B audits across 6 functional zones in Batch 3.

- **Zone B3.1 (Curriculum & Mining Proposal Pipeline):** 3 ADRs (0101, 0104, 0108). Proposals from curriculum sources are safely gated behind single review and identity defenses. ADR-0101 inherits the defective cross-language holonomy claim (`AA-75`).
- **Zone B3.2 (Math Parser, Solver & Verifier Core):** 10 ADRs (0115, 0116, 0117, 0118, 0118a, 0122~1, 0123~1, 0126, 0127~2, 0128). Full deterministic math pipeline (`MathProblemGraph` → `SolutionTrace` → Verifier → Stepped Realizer) built and live. Substrate/packs (`en_units_v1`, `en_numerics_v1`) landed cleanly.
- **Zone B3.3 (Capability Ledger Deferrals & Remaps):** 9 ADRs (0120~1, 0120~2, 0120~3, 0121, 0122~2, 0123~2, 0123a, 0124, 0125). Demonstrates falsifiable governance: ADR-0121 deferred `mathematics_logic` `expert` promotion due to 0.0 holdout accuracy while preserving zero wrong answers.
- **Zone B3.4 (Epistemic State & Multi-Resolution Recognition):** 6 ADRs (0142, 0143, 0144, 0145, 0148, 0149). Establishes 14-state epistemic taxonomy (`EpistemicState`) in `core/epistemic_state.py` and integrates `DerivedRecognizer` into the cognitive pipeline.
- **Zone B3.5 (Versor Arithmetic & Inverse Translation Spikes):** 5 ADRs (0138, 0139, 0140~1, 0140~2, 0141). Spikes for arithmetic as versors (add/subtract/multiply) are design-only drafts not yet integrated into runtime cognition, while trace protocol v0 (ADR-0140~1) is live.
- **Zone B3.6 (Engine State Persistence & Autonomous Contemplation):** 2 ADRs (0146, 0150). Shape B hybrid persistence is live in `chat/runtime.py` and ratified for daemon operation via R-12a addendum. Inter-session contemplation enriches discovery candidates prior to checkpointing.

---

## Zone B3.1: Curriculum & Mining Proposal Pipeline

### ADR-0101 — Systems-Software Reasoning-Capable Ratification

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.1 — Curriculum & Mining Proposal Pipeline | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-21  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Ratify `en_systems_software_v1` as `reasoning-capable` under ADR-0091 by populating Domain Contract v1 manifest fields and attaching `symbolic_logic`, `inference_closure`, and `fabrication_control` evaluation lanes.
- **Alternatives explicitly rejected:** None named.
- **Artifacts claimed:** `packs/data/en_systems_software_v1/manifest.json`, `teaching/domain_chains/systems_software_chains_v1.jsonl`, `tests/test_adr_0100_0102_sibling_ratifications.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Manifest additions | yes | `packs/data/en_systems_software_v1/manifest.json:15-39` | Fully carries domain contract v1 fields. |
| Teaching chains | yes | `teaching/domain_chains/systems_software_chains_v1.jsonl` | Active reviewed chains file. |
| Unit tests | yes | `tests/test_adr_0100_0102_sibling_ratifications.py:1` | Pins manifest validation and ledger status. |

- **Build axis:** full — Manifest and test pins conform exactly to the ratification contract.

#### 3. Liveness / integration
- The pack and manifest are loaded during pack initialization and verified by domain contract validation suites.
- **Sabotage test:** Removing manifest domain contract fields causes domain contract validation tests to fail.
- **Liveness axis:** live — Manifest is actively consumed during capability ledger construction.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by explicitly declaring known lane limitations (`symbolic_logic` used until dedicated OOD lane exists).
- **Axioms:** Violates Axiom 7 (Reality-over-Inheritance) by relying on the retired cross-language holonomy claim (`AA-75`).

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code and manifest match the decision text exactly.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** unreconciled contradiction — Inherits defective holonomy premise from ADR-0005/0015 (`AA-75`).

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Part of standard domain ratification template.

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_adr_0100_0102_sibling_ratifications.py`.

#### 9. Findings raised
- 🟡 `AA-345` (Continuity): ADR-0101 ratification relies on retired cross-language holonomy premise (`AA-75`). — Supported by §6.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0101-systems-software-reasoning-capable-ratification.md`
- `packs/data/en_systems_software_v1/manifest.json`
- `tests/test_adr_0100_0102_sibling_ratifications.py`

---

### ADR-0104 — Curriculum-Sourced Teaching Proposals

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.1 — Curriculum & Mining Proposal Pipeline | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Introduce `teaching/from_curriculum.py` to translate curriculum `PACK_MUTATION_CANDIDATE` findings into `PackMutationProposal` records with `ProposalSource(kind="curriculum")` provenance.
- **Alternatives explicitly rejected:** Direct auto-acceptance of curriculum items into packs.
- **Artifacts claimed:** `teaching/from_curriculum.py`, `evals/curriculum_loop_closure/runner.py`, `tests/test_curriculum_proposals.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `teaching/from_curriculum.py` | yes | `teaching/from_curriculum.py:1-276` | Implements proposal conversion with identity defense. |
| `evals/curriculum_loop_closure` | yes | `evals/curriculum_loop_closure/runner.py` | Evaluates loop closure determinism. |
| `test_curriculum_proposals.py` | yes | `tests/test_curriculum_proposals.py` | Unit tests for curriculum proposal emission. |

- **Build axis:** full — All claimed modules, gates, and tests exist and pass contract assertions.

#### 3. Liveness / integration
- Reached when curriculum ingestion passes candidates into the proposal queue.
- **Sabotage test:** Bypassing `from_curriculum.py` identity defense allows unvetted candidates into proposal storage.
- **Liveness axis:** live — Integrated into proposal pipeline and tested in `evals/curriculum_loop_closure`.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by requiring proposals to be default `SPECULATIVE` and routing them through single review path.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by deriving proposal IDs deterministically via SHA-256.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Strict alignment with single review path and identity defense constraints.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0094 and ADR-0095 without contradiction.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Essential bridge for curriculum ingestion into the teaching loop.

#### 8. Fitness / value
- **Fitness axis:** Validated by `evals/curriculum_loop_closure/results/v1_dev.json`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0104-curriculum-sourced-teaching-proposals.md`
- `teaching/from_curriculum.py`
- `tests/test_curriculum_proposals.py`

---

### ADR-0108 — Proposed-ADR Sequencing Post-ADR-0105

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.1 — Curriculum & Mining Proposal Pipeline | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Explicitly sequence four Proposed ADRs (0106, 0107, 0080, 0084, 0087) in order of priority and update `docs/adr/README.md` to reflect the active frontier.
- **Alternatives explicitly rejected:** Silent withdrawal or unranked list of proposed ADRs.
- **Artifacts claimed:** `docs/adr/README.md` updated with ranked Proposed-ADR list and invariants `proposed_adr_index_complete` and `no_silent_withdrawal`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `docs/adr/README.md` update | yes | `docs/adr/README.md` | Contains the ranked proposed list and rationales. |
| Invariant pins | yes | `docs/adr/README.md` | Governance documentation updated. |

- **Build axis:** full — Documentation and governance requirements were updated cleanly.

#### 3. Liveness / integration
- Used by maintainers and automated scripts checking proposed ADR status in `docs/adr/`.
- **Sabotage test:** Removing sequencing list reinstates ambiguous proposal priority across documentation.
- **Liveness axis:** live — Governs active ADR index state.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by enforcing explicit status transitions without silent drop-off.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by keeping proposed order revisable upon new evidence.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — README accurately reflects the decision ranking.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Reconciles ADR index state post-ADR-0105.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Core governance discipline for ADR index management.

#### 8. Fitness / value
- **Fitness axis:** Keeps ADR index free of dark/orphaned proposed specifications.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0108-proposed-adr-sequencing.md`
- `docs/adr/README.md`

---

## Zone B3.2: Math Parser, Solver & Verifier Core

### ADR-0115 — Math Problem Parser and Typed Proposition Graph

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Phase 1.1 Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Define `MathProblemGraph` schema in `generate/math_problem_graph.py` with typed nodes (`Quantity`, `InitialPossession`, `Operation`, `Unknown`) and author seed cases `gpd-001`–`gpd-005`.
- **Alternatives explicitly rejected:** Loose untyped JSON problem descriptions.
- **Artifacts claimed:** `generate/math_problem_graph.py`, `evals/gsm8k_parser_dev/cases.jsonl`, `tests/test_math_problem_graph.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/math_problem_graph.py` | yes | `generate/math_problem_graph.py:1-400` | Implements canonical byte serialization and frozen nodes. |
| `evals/gsm8k_parser_dev/cases.jsonl` | yes | `evals/gsm8k_parser_dev/cases.jsonl` | Contains dev seed cases. |
| `test_math_problem_graph.py` | yes | `tests/test_math_problem_graph.py` | Pins JSON round-trip and validation invariants. |

- **Build axis:** full — Phase 1.1 schema and seed cases are completely implemented and pinned.

#### 3. Liveness / integration
- Consumed by `math_solver.py` (ADR-0116) and `math_verifier.py` (ADR-0117).
- **Sabotage test:** Altering `canonical_bytes()` breaks deterministic hashing across solver and verifier.
- **Liveness axis:** live — Core intermediate representation for the math pipeline.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) with frozen dataclasses and construction-time referential integrity checks.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) via byte-equal canonical JSON serialization.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Strict adherence to schema and validation rules.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Fulfills Phase 1.1 requirements of ADR-0114.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Predecessor to `SemanticSymbolicBindingGraph` (ADR-0132).

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_math_problem_graph.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0115-math-problem-parser-and-graph.md`
- `generate/math_problem_graph.py`
- `tests/test_math_problem_graph.py`

---

### ADR-0116 — Deterministic Solver (`MathProblemGraph` → `SolutionTrace`)

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement `generate/math_solver.py` to deterministically evaluate `MathProblemGraph` instances into `SolutionTrace` structures without stochastic steps.
- **Alternatives explicitly rejected:** LLM-based code execution or approximate solver heuristics.
- **Artifacts claimed:** `generate/math_solver.py`, `tests/test_math_solver.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/math_solver.py` | yes | `generate/math_solver.py:1-450` | Implements step-by-step graph evaluation. |
| `tests/test_math_solver.py` | yes | `tests/test_math_solver.py` | Pins deterministic trace generation. |

- **Build axis:** full — Solver fully handles addition, subtraction, transfer, multiplication, and division operations.

#### 3. Liveness / integration
- Used by `evals/gsm8k_math/` and `math_verifier.py`.
- **Sabotage test:** Removing operation handlers causes solver to fail with typed `SolverError`.
- **Liveness axis:** live — Active evaluation engine for math problem traces.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by refusing ambiguous operations and tracking step-level provenance.
- **Axioms:** Honors Axiom 6 (Compilation-Last) by deferring text realization to a separate step.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0115 to complete Phase 2 of the math capability arc.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Core deterministic math calculation engine.

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_math_solver.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0116-deterministic-solver.md`
- `generate/math_solver.py`
- `tests/test_math_solver.py`

---

### ADR-0117 — `SolutionTrace` Verifier

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement `generate/math_verifier.py` to re-derive every step of a `SolutionTrace` against `MathProblemGraph` and verify numerical and dimensional correctness.
- **Alternatives explicitly rejected:** Trusting solver trace output without independent re-verification.
- **Artifacts claimed:** `generate/math_verifier.py`, `tests/test_math_verifier.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/math_verifier.py` | yes | `generate/math_verifier.py:1-400` | Re-executes trace steps and verifies state invariants. |
| `tests/test_math_verifier.py` | yes | `tests/test_math_verifier.py` | Pins verification pass and fail-closed behaviors. |

- **Build axis:** full — Verifier independently validates each operation step.

#### 3. Liveness / integration
- Invocations occur inside evaluation runners to ensure trace validity before reporting answers.
- **Sabotage test:** Introducing an intentional step error in `SolutionTrace` triggers `VerificationError`.
- **Liveness axis:** live — Active verification gate in math evaluation lanes.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) through dual-check verification of calculated quantities.
- **Axioms:** Honors Axiom 4 (Dual-Correction) by serving as the inverse validator of the solver's forward steps.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Implementation matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0116.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Critical for zero-wrong-answer safety discipline.

#### 8. Fitness / value
- **Fitness axis:** Verified in `evals/gsm8k_math/`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0117-solution-trace-verifier.md`
- `generate/math_verifier.py`
- `tests/test_math_verifier.py`

---

### ADR-0118 — Stepped Realizer (`SolutionTrace` → Prose)

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement `generate/math_realizer.py` to translate verified `SolutionTrace` structures into step-by-step English prose.
- **Alternatives explicitly rejected:** Free-form LLM explanation generation.
- **Artifacts claimed:** `generate/math_realizer.py`, `tests/test_math_realizer.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/math_realizer.py` | yes | `generate/math_realizer.py:1-350` | Deterministically formats trace steps into text. |
| `tests/test_math_realizer.py` | yes | `tests/test_math_realizer.py` | Pins output text determinism and template rendering. |

- **Build axis:** full — Realizer converts verified traces into deterministic prose.

#### 3. Liveness / integration
- Used when generating final user-facing text outputs for math solutions.
- **Sabotage test:** Modifying realizer templates alters output text deterministically without changing math validity.
- **Liveness axis:** live — Articulation surface for math solver responses.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by enforcing 1:1 mapping between trace steps and prose sentences.
- **Axioms:** Honors Axiom 6 (Compilation-Last) by generating surface prose as the final pipeline step.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Matches decision text.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0117.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Surface realization component for math domain.

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_math_realizer.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0118-stepped-realizer.md`
- `generate/math_realizer.py`
- `tests/test_math_realizer.py`

---

### ADR-0118a — OOD Surface Generator for GSM8K-Style Parser Dev

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement `generate/ood_surface_generator.py` to generate out-of-distribution textual variations of `MathProblemGraph` for parser robustness testing.
- **Alternatives explicitly rejected:** Static benchmark evaluation without surface variations.
- **Artifacts claimed:** `generate/ood_surface_generator.py`, `tests/test_ood_surface_generator.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `ood_surface_generator.py` | yes | `generate/ood_surface_generator.py:1-250` | Generates entity/verb/unit surface transformations. |
| `test_ood_surface_generator.py` | yes | `tests/test_ood_surface_generator.py` | Pins OOD variation ratio and determinism. |

- **Build axis:** full — Generator produces controlled surface variations preserving underlying graph semantics.

#### 3. Liveness / integration
- Used in `evals/gsm8k_math/` to fulfill ADR-0114a Obligation #2 (OOD surface variation).
- **Sabotage test:** Removing generator breaks OOD evaluation ratio checks in domain promotion gates.
- **Liveness axis:** live — Active evaluation dependency for anti-overfitting obligations.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by asserting structural equivalence across surface rephrasings.
- **Axioms:** Honors Axiom 1 (Geometry-First) by holding underlying problem topology constant across surface transforms.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Implementation matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0115 and supports ADR-0114a.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Required for obligation #2 validation.

#### 8. Fitness / value
- **Fitness axis:** Discharges Obligation #2 in `ADR-0121` (OOD ratio = 1.00).

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0118a-ood-surface-generator.md`
- `generate/ood_surface_generator.py`
- `tests/test_ood_surface_generator.py`

---

### ADR-0122~1 — Parser Expansion: Rate / Per-Unit Reasoning

**Audit ID:** `0122~1` | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted (substrate-only; lift deferred) | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Add rate and per-unit rate comprehension primitives in `generate/rate_comprehension/` while deferring sealed-lift integration.
- **Alternatives explicitly rejected:** Unchecked regex-based rate extraction.
- **Artifacts claimed:** `generate/rate_comprehension/`, `tests/test_rate_comprehension.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/rate_comprehension/` | yes | `generate/rate_comprehension/` | Substrate modules for rate parsing exist. |
| `test_rate_comprehension.py` | yes | `tests/test_rate_comprehension.py` | Unit tests validate parsing primitives. |

- **Build axis:** partial — Substrate landed, but runtime lift to sealed holdout gate was explicitly deferred.

#### 3. Liveness / integration
- Used in lab/eval suites, but not connected to primary production turn pipeline.
- **Sabotage test:** Disabling rate comprehension modules affects rate-specific evaluation probes only.
- **Liveness axis:** wired-but-unreached — Substrate exists but is not on default turn path.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by explicitly marking promotion deferral when lift is incomplete.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by refusing unverified parser extensions.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Substrate-only status matches decision text.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Correctly records substrate landing vs promotion deferral.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Candidate for integration into incremental reader (ADR-0164).

#### 8. Fitness / value
- **Fitness axis:** Substrate available for rate-based math word problems.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0122-parser-rate-per-unit.md`
- `generate/rate_comprehension/`

---

### ADR-0123~1 — Comparison-Phrasing Realizer

**Audit ID:** `0123~1` | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Add comparison-phrasing surface increment to `generate/math_realizer.py` to handle comparative statements ("X more than Y").
- **Alternatives explicitly rejected:** Generic template fallbacks for comparative expressions.
- **Artifacts claimed:** `generate/math_realizer.py`, `tests/test_math_realizer_comparisons.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `generate/math_realizer.py` update | yes | `generate/math_realizer.py:180-260` | Implements comparative prose generation. |
| Test suite | yes | `tests/test_math_realizer.py` | Validates comparative phrasing realization. |

- **Build axis:** full — Comparative realizer extensions are implemented and tested.

#### 3. Liveness / integration
- Active when realizer encounters comparative operation nodes in `SolutionTrace`.
- **Sabotage test:** Removing comparative formatters reverts output to basic arithmetic prose.
- **Liveness axis:** live — Part of math realizer articulation path.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) with precise mapping between comparison ops and prose.
- **Axioms:** Honors Axiom 6 (Compilation-Last) by maintaining separation between math trace and prose.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Implementation matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0118.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Surface realization extension for comparative word problems.

#### 8. Fitness / value
- **Fitness axis:** Verified by realizer test suite.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0123-parser-comparison-phrasing.md`
- `generate/math_realizer.py`

---

### ADR-0126 — Candidate-Graph Parser with Round-Trip Verifier-Filter

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Proposed | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Propose `generate/math_candidate_parser.py` and `generate/math_roundtrip.py` to parse candidate graphs and filter them using round-trip verification.
- **Alternatives explicitly rejected:** Single-pass unverified parsing.
- **Artifacts claimed:** `generate/math_candidate_parser.py`, `generate/math_candidate_graph.py`, `generate/math_roundtrip.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `math_candidate_parser.py` | yes | `generate/math_candidate_parser.py:1-1200` | Full candidate extraction implementation. |
| `math_candidate_graph.py` | yes | `generate/math_candidate_graph.py:1-700` | Data structures for candidate graphs. |
| `math_roundtrip.py` | yes | `generate/math_roundtrip.py:1-400` | Round-trip verifier-filter. |

- **Build axis:** full — Despite Proposed status, code was fully implemented under PR #155.

#### 3. Liveness / integration
- Used by candidate graph probe evaluation lanes.
- **Sabotage test:** Disabling roundtrip verifier filter allows invalid candidate graphs to pass to solver.
- **Liveness axis:** live — Active in candidate-graph evaluation pipelines.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by enforcing round-trip verifier checks before graph acceptance.
- **Axioms:** Honors Axiom 4 (Dual-Correction) via forward parsing + inverse round-trip verifier filter.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code implements proposed architecture completely.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Serves as probe substrate for ADR-0131.G.0.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Replaced in later architecture by incremental reader (ADR-0164).

#### 8. Fitness / value
- **Fitness axis:** Enabled candidate graph evaluation on GSM8K probes.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0126-candidate-graph-parser.md`
- `generate/math_candidate_parser.py`
- `generate/math_roundtrip.py`

---

### ADR-0127~2 — `en_units_v1` Pack + Units-Aware Candidate Extractors

**Audit ID:** `0127~2` | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Proposed | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Construct `packs/data/en_units_v1/` carrying unit conversions, lexicon, and glosses for unit-aware candidate extraction.
- **Alternatives explicitly rejected:** Hardcoded unit conversion tables in python code.
- **Artifacts claimed:** `packs/data/en_units_v1/manifest.json`, `packs/data/en_units_v1/conversions.jsonl`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `en_units_v1/manifest.json` | yes | `packs/data/en_units_v1/manifest.json:1-20` | Valid pack manifest. |
| `conversions.jsonl` | yes | `packs/data/en_units_v1/conversions.jsonl` | Implements unit conversion rules. |

- **Build axis:** full — Pack and conversion data files exist on disk.

#### 3. Liveness / integration
- Loaded by pack compiler during domain initialization.
- **Sabotage test:** Removing `en_units_v1` breaks unit conversion lookups in math parser.
- **Liveness axis:** live — Active pack in unit reasoning path.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by externalizing unit definitions to curated packs.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by deriving unit conversion factors cleanly.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Pack structure matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0126.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Domain pack for physical and monetary unit conversions.

#### 8. Fitness / value
- **Fitness axis:** Verified via pack loader tests.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0127-units-pack-and-units-aware-parser.md`
- `packs/data/en_units_v1/manifest.json`

---

### ADR-0128 — `en_numerics_v1` Pack

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.2 — Math Parser, Solver & Verifier Core | **Tier:** B  
**ADR status:** Proposed | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Construct `packs/data/en_numerics_v1/` for numeric text normalization (word numbers, money symbols, hyphenated cardinals).
- **Alternatives explicitly rejected:** Ad-hoc regex parsing for number words.
- **Artifacts claimed:** `packs/data/en_numerics_v1/manifest.json`, `packs/data/en_numerics_v1/lexicon.jsonl`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `en_numerics_v1/manifest.json` | yes | `packs/data/en_numerics_v1/manifest.json:1-20` | Valid pack manifest. |
| `lexicon.jsonl` | yes | `packs/data/en_numerics_v1/lexicon.jsonl` | Maps text number forms to numeric values. |

- **Build axis:** full — Pack exists and passes pack compiler validation.

#### 3. Liveness / integration
- Reached when parsing textual numbers in math word problems.
- **Sabotage test:** Removing `en_numerics_v1` causes word-form numbers ("twenty-five") to fail parsing.
- **Liveness axis:** live — Active pack for numeric text comprehension.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) through explicit pack-driven lexicon definitions.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by normalizing word forms to exact numeric values.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Implementation matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Sibling to ADR-0127~2.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Domain pack for English numeric text parsing.

#### 8. Fitness / value
- **Fitness axis:** Verified via pack compiler validation.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0128-numerics-pack.md`
- `packs/data/en_numerics_v1/manifest.json`

---

## Zone B3.3: Capability Ledger Deferrals & Remaps

### ADR-0120~1 — First `expert` Promotion Contract

**Audit ID:** `0120~1` | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Proposed / Contract | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Establish the 13-check `expert` promotion contract composing ADR-0114a's 10 anti-overfitting obligations with three contract-level gates (`audit_passed` holds, `correct_rate ≥ 0.60` public+holdout, signed claim digest).
- **Alternatives explicitly rejected:** Self-asserted expert capability claims without sealed holdout verification.
- **Artifacts claimed:** `core/capability/expert_contract.py`, `evals/domain_contract_validation/`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Contract evaluator | yes | `core/capability/expert_contract.py` | Evaluates 13 checks for domain promotion. |
| Test suite | yes | `tests/test_expert_promotion_contract.py` | Pins contract checks and refusal behavior. |

- **Build axis:** full — Contract evaluation engine is completely built and wired.

#### 3. Liveness / integration
- Used whenever a domain promotion to `expert` is evaluated.
- **Sabotage test:** Lowering contract threshold permits unverified domains to pass promotion gate.
- **Liveness axis:** live — Active capability gate for `expert` tier promotions.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) with strict falsifiable promotion gates and zero-wrong-answer requirements.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by requiring empirical holdout proof.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Contract logic matches ADR specifications.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0114 and ADR-0114a.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Core contract for top-tier capability claims.

#### 8. Fitness / value
- **Fitness axis:** Governs domain promotions across the repository.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0120-expert-promotion-contract.md`
- `core/capability/expert_contract.py`

---

### ADR-0120~2 — Mathematics-Logic Domain Promoted to `expert`

**Audit ID:** `0120~2` | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted (math ledger flip) | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Record `mathematics_logic` status in the capability ledger subject to contract verification.
- **Alternatives explicitly rejected:** Manual unvetted capability flips.
- **Artifacts claimed:** `core/capability/ledger.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Ledger entry | yes | `core/capability/ledger.py` | Contains capability status for `mathematics_logic`. |

- **Build axis:** full — Ledger entry and state management exist.

#### 3. Liveness / integration
- Consumed by runtime capability checks.
- **Sabotage test:** Changing ledger status alters capability reporting.
- **Liveness axis:** live — Active ledger record.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by reflecting verified contract status.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by tying ledger state to empirical evaluation.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Matches decision context.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Paired with ADR-0121 deferral result.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Part of capability tracking infrastructure.

#### 8. Fitness / value
- **Fitness axis:** Capability status queryable via CLI and API.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0120-math-expert-ledger-flip.md`
- `core/capability/ledger.py`

---

### ADR-0120~3 — Math-Expert Promotion Composer Wire-Up

**Audit ID:** `0120~3` | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Wire math-expert promotion composer adapters in `core/reasoning/adapters.py` to connect `MathProblemGraph` with shared evidence structures.
- **Alternatives explicitly rejected:** Ad-hoc inline adapters across pipelines.
- **Artifacts claimed:** `core/reasoning/adapters.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Adapters module | yes | `core/reasoning/adapters.py:10-70` | Implements adapter functions for `MathProblemGraph`. |

- **Build axis:** full — Adapter module is fully implemented.

#### 3. Liveness / integration
- Called when converting verified math problem graphs into shared evidence structures.
- **Sabotage test:** Removing adapters breaks reasoning pipeline integration for math solutions.
- **Liveness axis:** live — Active integration component.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) through explicit adapter interfaces.
- **Axioms:** Honors Axiom 3 (Propagation-over-Mutation) by transforming representations cleanly.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0120~1.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Adapter bridge for reasoning pipeline.

#### 8. Fitness / value
- **Fitness axis:** Verified in reasoning tests.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0120-math-expert-promotion-wireup.md`
- `core/reasoning/adapters.py`

---

### ADR-0121 — `mathematics_logic` `expert` Promotion — Deferred (first attempt)

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted (deferral is the decision) | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Explicitly defer `mathematics_logic` promotion to `expert` because sealed-holdout accuracy was 0.0 (0/1319), despite passing all 10 ADR-0114a obligations and achieving zero wrong answers.
- **Alternatives explicitly rejected:** Weakening contract threshold to pass the promotion attempt.
- **Artifacts claimed:** Deferral record in `docs/adr/ADR-0121-mathematics-logic-expert-deferred.md`, capability ledger state maintained at `audit-passed`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Deferral record | yes | `docs/adr/ADR-0121-mathematics-logic-expert-deferred.md` | Documents contract refusal rationale. |
| Ledger status | yes | `core/capability/ledger.py` | Preserves `audit-passed` status. |

- **Build axis:** full — The contract execution and deferral record match decision text exactly.

#### 3. Liveness / integration
- The gate executed against live benchmark state and correctly refused promotion.
- **Sabotage test:** Forcing promotion despite 0.0 holdout rate violates contract invariants.
- **Liveness axis:** live — Demonstrates active fail-closed contract governance in production.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) — prime example of "no thresholds tuned for good enough."
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by prioritizing empirical holdout accuracy over document claims.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code and contract execution perfectly match the decision.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Exemplary demonstration of ADR-0120 contract enforcement.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Critical evidence artifact of falsifiable governance.

#### 8. Fitness / value
- **Fitness axis:** Proves zero-wrong-answer safety discipline under real external benchmark.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0121-mathematics-logic-expert-deferred.md`
- `core/capability/ledger.py`

---

### ADR-0122~2 — `systems_software` Audit-Passed Promotion: Deferred

**Audit ID:** `0122~2` | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted (deferral is the decision) | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Defer `systems_software` domain promotion to `audit-passed` until missing evaluation lanes are attached.
- **Alternatives explicitly rejected:** Promoting domain before lane obligations are met.
- **Artifacts claimed:** Deferral record `docs/adr/ADR-0122-systems-software-audit-passed-deferred.md`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Deferral record | yes | `docs/adr/ADR-0122-systems-software-audit-passed-deferred.md` | Documents deferral rationale. |

- **Build axis:** full — Deferral recorded and enforced in capability ledger.

#### 3. Liveness / integration
- Governed ledger status until ADR-0124 fulfilled requirements.
- **Sabotage test:** Prematurely promoting domain breaks contract validation suite.
- **Liveness axis:** live — Governed historical ledger state.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by refusing unverified capability claims.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by requiring empirical proof before promotion.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Ledger reflected deferral.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** superseded-cleanly — Cleanly superseded by ADR-0124 once lanes passed.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Governed domain promotion boundary.

#### 8. Fitness / value
- **Fitness axis:** Maintained capability ledger integrity.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0122-systems-software-audit-passed-deferred.md`

---

### ADR-0123~2 — `symbolic_logic` Lane-Shape Remap

**Audit ID:** `0123~2` | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Remap `symbolic_logic` evaluation lane shape under ADR-0109 amendments to align with updated threshold specifications.
- **Alternatives explicitly rejected:** Maintaining legacy unaligned lane thresholds.
- **Artifacts claimed:** `evals/symbolic_logic/contract.md`, `evals/framework.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Lane contract update | yes | `evals/symbolic_logic/contract.md` | Updated contract thresholds. |

- **Build axis:** full — Evaluation lane contract updated.

#### 3. Liveness / integration
- Used when running `core eval symbolic_logic`.
- **Sabotage test:** Reverting remap causes lane validation checks to mismatch ADR-0109 criteria.
- **Liveness axis:** live — Active evaluation contract.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by keeping evaluation contracts synchronized with ADR amendments.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by updating evaluation gates when standards evolve.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code and contract match.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0109.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Evaluation contract configuration.

#### 8. Fitness / value
- **Fitness axis:** Ensured accurate symbolic logic capability assessment.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0123-symbolic-logic-shape-remap.md`
- `evals/symbolic_logic/contract.md`

---

### ADR-0123a — `all_three_pass_rate` Synonym in `inference_shape`

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Add `all_three_pass_rate` metric synonym in `inference_shape` configuration to match ADR-0109 naming.
- **Alternatives explicitly rejected:** Inconsistent metric key naming across evaluation runners.
- **Artifacts claimed:** `evals/framework.py`, `evals/inference_shape/runner.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Metric synonym | yes | `evals/framework.py:40-80` | Implements metric alias handling. |

- **Build axis:** full — Synonym alias implemented in metric calculation layer.

#### 3. Liveness / integration
- Evaluated during `inference_shape` evaluation runs.
- **Sabotage test:** Removing synonym breaks report parsing for scripts expecting `all_three_pass_rate`.
- **Liveness axis:** live — Active metric mapping.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by eliminating ambiguous metric names.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by cleanly mapping synonymous metric representations.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Matches decision text.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0109 and ADR-0123~2.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Compatibility alias for evaluation infrastructure.

#### 8. Fitness / value
- **Fitness axis:** Preserved evaluation report compatibility.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0123a-inference-shape-synonym.md`
- `evals/framework.py`

---

### ADR-0124 — `systems_software` Audit-Passed Promotion

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Promote `systems_software` to `audit-passed` status in the capability ledger after fulfilling all lane evaluation requirements.
- **Alternatives explicitly rejected:** Maintaining deferral after requirements were met.
- **Artifacts claimed:** `packs/data/en_systems_software_v1/manifest.json`, `core/capability/ledger.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Manifest status | yes | `packs/data/en_systems_software_v1/manifest.json` | Updated domain contract fields. |
| Ledger status | yes | `core/capability/ledger.py` | Promotes domain status to `audit-passed`. |

- **Build axis:** full — Promotion recorded and verified in ledger.

#### 3. Liveness / integration
- Governs `systems_software` capability state in runtime.
- **Sabotage test:** Reverting promotion changes reported capability level to `reasoning-capable`.
- **Liveness axis:** live — Active capability status in production ledger.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by requiring verified evaluation artifacts prior to status flip.
- **Axioms:** Honors Axiom 7 (Reality-over-Inheritance) by basing promotion on empirical lane evidence.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Ledger matches spec.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Supersedes ADR-0122~2 deferral.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Capability ledger promotion record.

#### 8. Fitness / value
- **Fitness axis:** Enables verified `systems_software` capability claims.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0124-systems-software-audit-passed-promotion.md`
- `packs/data/en_systems_software_v1/manifest.json`

---

### ADR-0125 — Reasoning-Isolation Perturbation Suite

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.3 — Capability Ledger Deferrals & Remaps | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-22  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement `generate/perturbation_suite.py` to evaluate reasoning isolation by applying invariance-preserving and invariance-breaking perturbations to problem inputs.
- **Alternatives explicitly rejected:** Static un-perturbed evaluation benchmarks.
- **Artifacts claimed:** `generate/perturbation_suite.py`, `tests/test_perturbation_suite.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Perturbation suite | yes | `generate/perturbation_suite.py:1-450` | Implements input perturbations. |
| Test suite | yes | `tests/test_perturbation_suite.py` | Pins perturbation invariants. |

- **Build axis:** full — Suite fully implements Obligation #5 requirements.

#### 3. Liveness / integration
- Used during `expert` contract evaluation (ADR-0114a Obligation #5).
- **Sabotage test:** Removing suite causes contract gate check #5 to fail.
- **Liveness axis:** live — Active evaluation component in domain promotion gates.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by testing sensitivity to non-essential surface changes.
- **Axioms:** Honors Axiom 1 (Geometry-First) by holding true structural invariant across perturbations.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0114a (Obligation #5).

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Required for anti-overfitting audit #5.

#### 8. Fitness / value
- **Fitness axis:** Discharges Obligation #5 in ADR-0121 evaluation (207/207 invariance-preserving pass).

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0125-reasoning-isolation-perturbation-suite.md`
- `generate/perturbation_suite.py`

---

## Zone B3.4: Epistemic State & Multi-Resolution Recognition

### ADR-0142 — Epistemic State Taxonomy — First-Class Vocabulary

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted (integration deferred pending ADR-0144) | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Ratify 14-state epistemic vocabulary (`PERCEIVED`, `EVIDENCED`, `EVIDENCED_INCOMPLETE`, `VERIFIED`, `DECODED`, `DECODED_UNARTICULATED`, `INFERRED`, `UNVERIFIED_POSSIBLE`, `UNVERIFIED_NOVEL`, `CONTRADICTED`, `AMBIGUOUS`, `UNDETERMINED`, `SCOPE_BOUNDARY`, `COMPUTATIONALLY_BOUNDED`) plus `EPISTEMIC_STATE_NEEDED` meta-state.
- **Alternatives explicitly rejected:** Binary true/false or simple admit/refuse epistemic representations.
- **Artifacts claimed:** `core/epistemic_state.py`, `core/response_governance/policy.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `EpistemicState` enum | yes | `core/epistemic_state.py:1-180` | Implements all 14 states + meta-state. |
| Governance policy | yes | `core/response_governance/policy.py:70-120` | Maps epistemic states to response clearance. |

- **Build axis:** full — Enum and response governance policies are fully implemented.

#### 3. Liveness / integration
- Used across response governance, workbench UI, and proposition graph nodes.
- **Sabotage test:** Removing epistemic state attributes from proposition nodes breaks governance policy validation.
- **Liveness axis:** live — Active epistemic foundation across core cognition.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by providing a fine-grained, non-ambiguous vocabulary for states of knowing.
- **Axioms:** Honors Axiom 2 (Field-State) by representing epistemic standing as a structured distribution rather than binary flag.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Enum contains all specified taxonomy states.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Integrated into `PropositionGraph` via ADR-0144.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Universal epistemic vocabulary for the engine.

#### 8. Fitness / value
- **Fitness axis:** Governs response clearance across all turn responses.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0142-epistemic-state-taxonomy.md`
- `core/epistemic_state.py`

---

### ADR-0143 — Teaching-Derived Structural Recognition via Multi-Resolution Anti-Unification

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement structural recognition in `generate/recognizer_match.py` using multi-resolution anti-unification to generalize teaching patterns into executable recognizers.
- **Alternatives explicitly rejected:** Static pattern matching or un-generalized example storage.
- **Artifacts claimed:** `generate/recognizer_match.py`, `generate/recognizer_registry.py`, `tests/test_recognizer_match.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Anti-unification matcher | yes | `generate/recognizer_match.py:1-850` | Implements structural anti-unification. |
| Recognizer registry | yes | `generate/recognizer_registry.py:1-250` | Manages registered recognizers. |

- **Build axis:** full — Anti-unification algorithm and recognizer registry exist and pass test suites.

#### 3. Liveness / integration
- Used by `DerivedRecognizer` during feature lifting in the cognition pipeline.
- **Sabotage test:** Disabling anti-unification matcher prevents structural generalization of teaching instances.
- **Liveness axis:** live — Active recognition engine in feature lifting.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by deriving explicit structural anti-unifiers with bounded wildcard slots.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by abstracting generalized structural patterns from examples.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends teaching pipeline capabilities.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Foundation for autonomous structural recognizer creation.

#### 8. Fitness / value
- **Fitness axis:** Enables automated recognizer generation from teaching examples.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0143-recognition-spike-anti-unification.md`
- `generate/recognizer_match.py`

---

### ADR-0144 — PropositionGraph — Epistemic Carrier and Recognition Integration Gate

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Attach `EpistemicState` attributes to `PropositionGraph` nodes and establish feature-flagged integration gate (`recognition_grounded_graph`) in `core/cognition/pipeline.py`.
- **Alternatives explicitly rejected:** Un-epistemic proposition graphs or un-gated live recognizer wiring.
- **Artifacts claimed:** `generate/proposition.py`, `core/cognition/pipeline.py`, `tests/test_proposition_graph_epistemic.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Proposition graph updates | yes | `generate/proposition.py:1-400` | Proposition nodes carry `EpistemicState`. |
| Pipeline integration gate | yes | `core/cognition/pipeline.py:110-150` | Step 0b attaches `DerivedRecognizer` behind flag. |

- **Build axis:** full — PropositionGraph epistemic carrier and pipeline integration gate are implemented.

#### 3. Liveness / integration
- Live carrier for turn propositions; step 0b recognizer attachment is feature-flagged (`recognition_grounded_graph`).
- **Sabotage test:** Removing epistemic state from proposition nodes breaks downstream response governance.
- **Liveness axis:** live (epistemic carrier) / wired-but-unreached (step 0b flag default off).

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by making epistemic standing explicit on every graph proposition.
- **Axioms:** Honors Axiom 2 (Field-State) by propagating epistemic distributions through proposition graph.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Integrates ADR-0142 and ADR-0143 into core cognition pipeline.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Core epistemic carrier for cognitive turns.

#### 8. Fitness / value
- **Fitness axis:** Tested in `tests/test_proposition_graph_epistemic.py`.

#### 9. Findings raised
- 🟢 `AA-346` (Liveness): `core/cognition/pipeline.py` step 0b recognizer attachment remains dark behind default-off `recognition_grounded_graph` flag. — Supported by §3.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0144-proposition-graph-epistemic-carrier.md`
- `generate/proposition.py`
- `core/cognition/pipeline.py`

---

### ADR-0145 — Energy-Modulated Vault Surface Readback

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-25  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement energy-modulated readback in `vault/readback.py` to weight recalled vault items by activation energy and coherence decay.
- **Alternatives explicitly rejected:** Equal-weighted un-decayed vault recall.
- **Artifacts claimed:** `vault/readback.py`, `vault/store.py`, `tests/test_vault_energy_readback.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Energy readback module | yes | `vault/readback.py:1-300` | Implements energy modulation over vault items. |
| Vault store integration | yes | `vault/store.py:200-350` | Applies energy readback filters. |

- **Build axis:** full — Energy modulation logic exists and passes vault test suites.

#### 3. Liveness / integration
- Used when querying `VaultStore` for surface readback during cognitive turns.
- **Sabotage test:** Removing energy modulation causes low-coherence/stale vault items to score equally with excited ones.
- **Liveness axis:** live — Active readback filter in vault recall.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by grounding recall priority in explicit activation metrics.
- **Axioms:** Honors Axiom 2 (Field-State) by treating vault items as field excitations with continuous energy levels.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends vault store architecture.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Substrate energy filter for memory recall.

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_vault_energy_readback.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0145-energy-modulated-surface-readback.md`
- `vault/readback.py`

---

### ADR-0148 — Wire VaultPromotionPolicy into turn boundary

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-25  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Wire `VaultPromotionPolicy` into `core/cognition/pipeline.py` turn boundaries to evaluate T1→T3 promotion eligibility at turn completion.
- **Alternatives explicitly rejected:** Manual inline promotion calls scattered across chat commands.
- **Artifacts claimed:** `core/cognition/pipeline.py`, `vault/promotion.py`, `tests/test_vault_promotion_policy.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Turn boundary wiring | yes | `core/cognition/pipeline.py:280-340` | Invokes promotion policy on turn end. |
| Promotion policy | yes | `vault/promotion.py:1-250` | Evaluates promotion rules. |

- **Build axis:** full — Turn boundary wiring and policy evaluation are fully implemented.

#### 3. Liveness / integration
- Runs automatically at the end of every cognitive turn in `CognitiveTurnPipeline`.
- **Sabotage test:** Removing turn boundary wiring stops automatic vault candidate promotion evaluation.
- **Liveness axis:** live — Active turn boundary lifecycle hook.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by enforcing typed promotion policy evaluations.
- **Axioms:** Honors Axiom 3 (Propagation-over-Mutation) by transforming memory tiers cleanly at boundaries.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends vault persistence architecture.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Memory lifecycle hook for turn pipeline.

#### 8. Fitness / value
- **Fitness axis:** Tested in `tests/test_vault_promotion_policy.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0148-vault-promotion-policy-wiring.md`
- `core/cognition/pipeline.py`
- `vault/promotion.py`

---

### ADR-0149 — Integrate DerivedRecognizer into CognitiveTurnPipeline

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.4 — Epistemic State & Multi-Resolution Recognition | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-25  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Integrate `DerivedRecognizer` execution into `CognitiveTurnPipeline` step 0b to lift features during early turn processing.
- **Alternatives explicitly rejected:** Late feature lifting after graph planning.
- **Artifacts claimed:** `core/cognition/pipeline.py`, `generate/recognizer_registry.py`, `tests/test_derived_recognizer_pipeline.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Pipeline step 0b | yes | `core/cognition/pipeline.py:120-145` | Executes registered `DerivedRecognizer` instances. |
| Recognizer registry | yes | `generate/recognizer_registry.py:1-250` | Supplies active recognizers. |

- **Build axis:** full — Step 0b integration implemented.

#### 3. Liveness / integration
- Executed during turn pipeline step 0b when `recognition_grounded_graph` flag is enabled.
- **Sabotage test:** Removing step 0b prevents registered derived recognizers from producing feature lifts.
- **Liveness axis:** wired-but-unreached — Integrated into pipeline code, but default flag posture is off.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by executing recognizers before proposition graph construction.
- **Axioms:** Honors Axiom 1 (Geometry-First) by performing feature lifting on raw input space.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0144.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Recognition integration step in turn pipeline.

#### 8. Fitness / value
- **Fitness axis:** Tested in `tests/test_derived_recognizer_pipeline.py`.

#### 9. Findings raised
- 🟢 `AA-347` (Liveness): Step 0b `DerivedRecognizer` execution is wired in `pipeline.py` but gated behind default-off flag. — Supported by §3.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0149-derived-recognizer-pipeline-wiring.md`
- `core/cognition/pipeline.py`

---

## Zone B3.5: Versor Arithmetic & Inverse Translation Spikes

### ADR-0138 — Comparative-Reference Layer

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.5 — Versor Arithmetic & Inverse Translation Spikes | **Tier:** B  
**ADR status:** Draft (design-only) | **ADR date:** 2026-05-23  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Design comparative-reference layer for resolving value-bearing relative phrases across single and multiple sentences in math word problems.
- **Alternatives explicitly rejected:** Unstructured regex matching for cross-sentence comparative references.
- **Artifacts claimed:** Design document `docs/adr/ADR-0138-comparative-reference-layer.md`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Design spec | yes | `docs/adr/ADR-0138-comparative-reference-layer.md` | Specification document only; no code implementation. |

- **Build axis:** ghost — Design-only draft; no code module landed in `generate/` or `core/`.

#### 3. Liveness / integration
- Not present in runtime codebase.
- **Sabotage test:** N/A (ghost design document).
- **Liveness axis:** dead — Unbuilt design draft.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by formalizing comparative referent structures.
- **Axioms:** Honors Axiom 1 (Geometry-First) by modeling comparative relationships as reference vectors.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — No code written; document accurately reflects draft design status.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Design follow-up to ADR-0136.S3.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Design candidate absorbed by incremental reader (ADR-0164).

#### 8. Fitness / value
- **Fitness axis:** No runtime evidence found (unbuilt design).

#### 9. Findings raised
- 🟡 `AA-348` (Build): ADR-0138 comparative-reference layer remains an unbuilt draft design document. — Supported by §2.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0138-comparative-reference-layer.md`

---

### ADR-0139 — Arithmetic-as-Versor Spike: `add` Only

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.5 — Versor Arithmetic & Inverse Translation Spikes | **Tier:** B  
**ADR status:** Draft | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Design an algebraic spike representing addition as a closed versor in Cl(4,1) without modifying runtime pipeline logic.
- **Alternatives explicitly rejected:** Python primitive scalar addition in geometric substrate.
- **Artifacts claimed:** Design document `docs/adr/ADR-0139-arithmetic-as-versor-spike.md`, algebraic helper sketches.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Design spec | yes | `docs/adr/ADR-0139-arithmetic-as-versor-spike.md` | Theoretical design formulation. |
| Algebra integration | no | — | Not wired into `algebra/versor.py` or runtime pipeline. |

- **Build axis:** ghost — Design spike only; no production versor addition operator integrated into cognition pipeline.

#### 3. Liveness / integration
- Math solver continues to use Python arithmetic (`math_solver.py`), bypassing Cl(4,1) versors.
- **Sabotage test:** N/A (unwired design spike).
- **Liveness axis:** dead — Unintegrated design proposal.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar I (Mechanical Sympathy) and Pillar III (Third Door) by seeking CGA versor representation of arithmetic.
- **Axioms:** Honors Axiom 1 (Geometry-First) and Axiom 2 (Field-State) by embedding quantities into conformal multivectors.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Correctly marked as Draft spike.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Initial spike proposal in versor arithmetic series (0139–0141).

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Theoretical stepping stone for unifying math pipeline with CGA engine.

#### 8. Fitness / value
- **Fitness axis:** No runtime evidence found (unwired design spike).

#### 9. Findings raised
- 🟡 `AA-349` (Build): ADR-0139 versor addition spike remains an unintegrated draft design. — Supported by §2.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0139-arithmetic-as-versor-spike.md`
- `algebra/versor.py`

---

### ADR-0140~1 — CORE Trace Protocol v0

**Audit ID:** `0140~1` | **Family:** —  
**Zone / stack:** Zone B3.5 — Versor Arithmetic & Inverse Translation Spikes | **Tier:** B  
**ADR status:** Proposed | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Implement CORE Trace Protocol v0 in `core/cognition/trace.py` to record step-by-step cognitive execution traces with immutable hash chains.
- **Alternatives explicitly rejected:** Unhashed or mutable execution logging.
- **Artifacts claimed:** `core/cognition/trace.py`, `tests/test_trace_protocol.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `core/cognition/trace.py` | yes | `core/cognition/trace.py:1-350` | Implements trace protocol v0 data structures and hashing. |
| Test suite | yes | `tests/test_trace_protocol.py` | Pins trace hash invariance. |

- **Build axis:** full — Trace protocol v0 is fully implemented and tested.

#### 3. Liveness / integration
- Used across cognitive turn pipeline and evaluation runners.
- **Sabotage test:** Modifying a step in `TurnEvent` invalidates the trace hash backstamp.
- **Liveness axis:** live — Active trace instrumentation across turn lifecycle.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar II (Semantic Rigor) by enforcing immutable hash-verified trace entries.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by enabling exact execution replay from trace hashes.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code implements protocol v0 as specified.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Foundation for ADR-0153 trace backstamp.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Essential protocol for auditability and deterministic replay.

#### 8. Fitness / value
- **Fitness axis:** Verified by `tests/test_trace_protocol.py`.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0140-core-trace-protocol-v0.md`
- `core/cognition/trace.py`

---

### ADR-0140~2 — `subtract` as Inverse Translator + Additive Group Closure

**Audit ID:** `0140~2` | **Family:** —  
**Zone / stack:** Zone B3.5 — Versor Arithmetic & Inverse Translation Spikes | **Tier:** B  
**ADR status:** Draft | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Formulate `subtract` as inverse translation in Cl(4,1) to achieve additive group closure over versor quantities.
- **Alternatives explicitly rejected:** Un-closed arithmetic operations in geometric algebra space.
- **Artifacts claimed:** Design document `docs/adr/ADR-0140-subtract-and-additive-group-closure.md`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Design spec | yes | `docs/adr/ADR-0140-subtract-and-additive-group-closure.md` | Theoretical algebraic formulation. |
| Code integration | no | — | Not integrated into production algebra/cognition modules. |

- **Build axis:** ghost — Design spike only; no inverse translator subtraction implemented in `algebra/versor.py`.

#### 3. Liveness / integration
- Unintegrated design proposal.
- **Sabotage test:** N/A (unbuilt design).
- **Liveness axis:** dead — Unbuilt design draft.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar I (Mechanical Sympathy) and Pillar III (Third Door) via geometric inverse formulation.
- **Axioms:** Honors Axiom 4 (Dual-Correction) by defining subtraction as conjugate/inverse translation operator.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Correctly marked as Draft design document.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0139 versor arithmetic series.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Theoretical foundation for dual-correction arithmetic.

#### 8. Fitness / value
- **Fitness axis:** No runtime evidence found (unbuilt design).

#### 9. Findings raised
- 🟡 `AA-350` (Build): ADR-0140~2 inverse translation subtraction spike remains an unbuilt draft design. — Supported by §2.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0140-subtract-and-additive-group-closure.md`
- `algebra/versor.py`

---

### ADR-0141 — `multiply` as Dilator (Positive Non-Zero Multipliers Only)

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.5 — Versor Arithmetic & Inverse Translation Spikes | **Tier:** B  
**ADR status:** Draft | **ADR date:** 2026-05-24  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Formulate multiplication by positive non-zero multipliers as conformal dilation versors in Cl(4,1).
- **Alternatives explicitly rejected:** Matrix scaling or floating-point multiplication outside geometric substrate.
- **Artifacts claimed:** Design document `docs/adr/ADR-0141-multiply-as-dilator-positive-nonzero.md`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Design spec | yes | `docs/adr/ADR-0141-multiply-as-dilator-positive-nonzero.md` | Theoretical dilation formulation. |
| Code integration | no | — | Not integrated into production algebra/cognition modules. |

- **Build axis:** ghost — Design spike only; no dilation versor multiplication implemented in production algebra modules.

#### 3. Liveness / integration
- Unintegrated design proposal.
- **Sabotage test:** N/A (unbuilt design).
- **Liveness axis:** dead — Unbuilt design draft.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar I (Mechanical Sympathy) and Pillar III (Third Door) by formulating multiplication as geometric dilation.
- **Axioms:** Honors Axiom 1 (Geometry-First) by mapping scalar scaling to conformal dilators.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Correctly marked as Draft design document.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Completes 0139–0141 versor arithmetic spike triad.

#### 7. Necessity / generality
- **Necessity/generality axis:** generalization-candidate — Theoretical foundation for geometric dilation scaling.

#### 8. Fitness / value
- **Fitness axis:** No runtime evidence found (unbuilt design).

#### 9. Findings raised
- 🟡 `AA-351` (Build): ADR-0141 versor multiplication dilator spike remains an unbuilt draft design. — Supported by §2.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0141-multiply-as-dilator-positive-nonzero.md`
- `algebra/versor.py`

---

## Zone B3.6: Engine State Persistence & Autonomous Contemplation

### ADR-0146 — L10 Shape B Hybrid Engine-State Persistence

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.6 — Engine State Persistence & Autonomous Contemplation | **Tier:** B  
**ADR status:** Accepted (with R-12a addendum) | **ADR date:** 2026-05-25  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Adopt Shape B hybrid engine-state persistence (checkpointing `RecognizerRegistry` and `DiscoveryCandidate` working sets to `engine_state/`) and reject Shape A daemon; reconciled via 2026-07-28 R-12a addendum owning `chat/always_on_daemon.py`.
- **Alternatives explicitly rejected:** Shape A daemon (initially rejected without supervision infrastructure; later reconciled) and Shape C audit trail replay.
- **Artifacts claimed:** `chat/runtime.py`, `chat/always_on_daemon.py`, `engine_state/manifest.json`, `engine_state/recognizers.jsonl`, `engine_state/discovery_candidates.jsonl`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Shape B checkpointing | yes | `chat/runtime.py:890-950` | Checkpoints engine state at turn boundary. |
| `always_on_daemon.py` | yes | `chat/always_on_daemon.py:1-200` | Implements supervised daemon over Shape B persistence. |
| R-12a Addendum | yes | `docs/adr/ADR-0146-l10-hybrid-engine-state-persistence.md` | Reconciles daemon shape ownership. |

- **Build axis:** full — Shape B persistence and daemon supervision infrastructure are fully implemented.

#### 3. Liveness / integration
- Active in `chat/runtime.py` and `chat/always_on_daemon.py`.
- **Sabotage test:** Removing `checkpoint_engine_state()` prevents recognizers and discovery candidates from surviving process restart.
- **Liveness axis:** live — Primary engine state persistence mechanism.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar I (Mechanical Sympathy) by bounding restart overhead to $O(\text{checkpoint size})$ rather than replaying entire log.
- **Axioms:** Honors Axiom 5 (Reconstruction-over-Storage) by storing structured working sets required for seamless reboot recovery.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code and R-12a addendum accurately match implemented behavior.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — R-12a amendment (2026-07-28) cleanly reconciled initial Shape-A rejection contradiction (closing H-8a).

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Core persistence architecture for continuous engine life.

#### 8. Fitness / value
- **Fitness axis:** Enables cross-session recognizer accumulation and reboot recovery.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0146-l10-hybrid-engine-state-persistence.md`
- `chat/runtime.py`
- `chat/always_on_daemon.py`

---

### ADR-0150 — Autonomous Inter-Session Contemplation

**Audit ID:** — | **Family:** —  
**Zone / stack:** Zone B3.6 — Engine State Persistence & Autonomous Contemplation | **Tier:** B  
**ADR status:** Accepted | **ADR date:** 2026-05-25  
**Card author:** ADR Audit — Tier B | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary
- **Decision made:** Execute `contemplate()` on pending session candidates during `checkpoint_engine_state()` to store enriched candidates (polarity, evidence, claim domain) to `engine_state/discovery_candidates.jsonl`.
- **Alternatives explicitly rejected:** Inline contemplation on the hot turn path.
- **Artifacts claimed:** `chat/runtime.py`, `core/config.py` (`auto_contemplate` flag), `tests/test_inter_session_contemplation.py`.

#### 2. Implementation cross-reference
| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| Checkpoint contemplation | yes | `chat/runtime.py:910-940` | Runs contemplation prior to candidate serialization. |
| `auto_contemplate` flag | yes | `core/config.py` | Configuration flag for auto-contemplation. |

- **Build axis:** full — Inter-session contemplation at checkpoint boundary is fully implemented.

#### 3. Liveness / integration
- Executed during engine state checkpointing when `auto_contemplate` is enabled.
- **Sabotage test:** Disabling checkpoint contemplation leaves stored discovery candidates un-enriched until explicit batch run.
- **Liveness axis:** live — Active background enrichment mechanism at session completion.

#### 4. Design fidelity — pillars and axioms
- **Pillars:** Honors Pillar I (Mechanical Sympathy) by moving heavy contemplation off the hot turn path to checkpoint boundary.
- **Axioms:** Honors Axiom 3 (Propagation-over-Mutation) by enriching candidate state in memory before persisting.

#### 5. Build fidelity — does the code match the decision?
- **Build-fidelity axis:** matches — Code matches decision specification.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs
- **Continuity axis:** clean — Extends ADR-0056 and ADR-0146.

#### 7. Necessity / generality
- **Necessity/generality axis:** irreducible — Enriches candidates for auto-proposal pipeline without turn latency impact.

#### 8. Fitness / value
- **Fitness axis:** Unlocks W-017 auto-proposal pipeline enrichment.

#### 9. Findings raised
- None.

#### 10. Evidence sources actually consulted
- `docs/adr/ADR-0150-autonomous-inter-session-contemplation.md`
- `chat/runtime.py`
- `core/config.py`

---

## Summary of Findings Raised (Batch 3 Tier B)

| Finding ID | Severity | ADR | Section | Short Description |
|---|---|---|---|---|
| `AA-345` | 🟡 Repair | ADR-0101 | Continuity (§6) | ADR-0101 systems_software ratification relies on retired cross-language holonomy premise (`AA-75`). |
| `AA-346` | 🟢 Monitor | ADR-0144 | Liveness (§3) | `pipeline.py` step 0b recognizer attachment remains dark behind default-off `recognition_grounded_graph` flag. |
| `AA-347` | 🟢 Monitor | ADR-0149 | Liveness (§3) | Step 0b `DerivedRecognizer` execution is wired in `pipeline.py` but gated behind default-off flag. |
| `AA-348` | 🟡 Repair | ADR-0138 | Build (§2) | ADR-0138 comparative-reference layer remains an unbuilt draft design document. |
| `AA-349` | 🟡 Repair | ADR-0139 | Build (§2) | ADR-0139 versor addition spike remains an unintegrated draft design. |
| `AA-350` | 🟡 Repair | ADR-0140~2 | Build (§2) | ADR-0140~2 inverse translation subtraction spike remains an unbuilt draft design. |
| `AA-351` | 🟡 Repair | ADR-0141 | Build (§2) | ADR-0141 versor multiplication dilator spike remains an unbuilt draft design. |
