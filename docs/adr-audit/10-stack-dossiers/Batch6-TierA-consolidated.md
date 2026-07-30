# Batch 6 — Tier A Consolidated Audit Dossier (ADR-0251 to ADR-0265)

**Verified against:** `main` @ `cbfc8ccb` | **Date:** 2026-07-29  
**Audit Scope:** Batch 6 Tier A Stacks (A6.1 to A6.2, 15 ADRs total)  
**Rigor Level:** Consolidated pass under 2026-07-29 cost correction protocol (bounded investigation depth, code/test inspection only, concise per-axis scoring).

---

## Stack A6.1 — Master Convergence & Reliability License Bands

**Members:** ADR-0256, ADR-0257, ADR-0258, ADR-0259, ADR-0260, ADR-0261, ADR-0262, ADR-0263, ADR-0264, ADR-0265 (10 ADRs)  
**Zone:** `M3-comprehension-reasoning` / `M4-expression-serving` / `master-convergence-reliability` | **Tier:** A  
**Prior Evidence:** `chat/deduction_surface.py`, `chat/curriculum_surface.py`, `chat/deduction_serve_license.py`, `chat/curriculum_serve_license.py`, `core/ratified_ledger.py`, `generate/graph_planner.py`

### 0. Why this is one stack
Phased mega-family establishing deduction serving under earned reliability licenses across Bands v2-EN through v6-EX, curriculum-grounded serving, ratified-ledger bridges, negative curriculum, and proposition-graph negation representation.

### 1. Stack-level claim
Deductive and curriculum reasoning surfaces must be served under strict, evidence-backed reliability licenses (`wrong=0` across all splits) backed by unified ratified ledgers, explicit negative curriculum refutations, and structurally complete denial representation in proposition graphs.

### 2. Member ADR Cards

#### ADR-0256 — Deduction Serve Earned License
- **Content summary:** Establishes earned reliability license gate for deduction serving (`deduction_serve_v1`) over six deduction shape bands.
- **Build axis:** `full` — Implemented in `chat/deduction_serve_license.py`, `chat/deduction_surface.py`, and `chat/data/deduction_serve_ledger.json`.
- **Liveness axis:** `live` — Active on the live serving path (`chat/runtime.py:470`) and verified in `tests/test_deduction_surface.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and wrong=0 discipline by requiring committed evidence volume (`N >= 657`) for SERVE status.
- **Build fidelity:** `matches` — R-13 re-count (2026-07-28) demoted 21 of 25 bands to disclosure serving when distinct evidence counting was enforced, leaving 4 bands with earned SERVE licenses.
- **Continuity:** `clean` — Integrates with response governance (`core/response_governance/policy.py`) and ratified ledger (`core/ratified_ledger.py`).
- **Necessity/generality:** `irreducible` — Mandatory reliability license gate governing deduction serving.
- **Fitness/value:** Ensures deduction outputs serve only when backed by verified pipeline reliability.

#### ADR-0257 — English Clause Argument Band (v2-EN)
- **Content summary:** Implements natural English propositional argument parsing over opaque terms in `chat/deduction_surface.py`.
- **Build axis:** `full` — Implemented in `chat/deduction_surface.py` (`_try_read_band_v2_en`).
- **Liveness axis:** `live` — Active in deduction surface resolution fallback chain.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by enforcing strict English clause structure rules without ungrounded guessing.
- **Build fidelity:** `matches` — Text reader handles natural-English clause syntax over opaque terms as specified.
- **Continuity:** `clean` — Operates as Band v2-EN within the deduction serving architecture.
- **Necessity/generality:** `irreducible` — Primary English clause parser for deduction.
- **Fitness/value:** Enables exact propositional deduction over arbitrary natural English clauses.

#### ADR-0258 — Member Chain Band (v3-MEM)
- **Content summary:** Implements singular-membership argument parsing with universal constraints in `chat/deduction_surface.py`.
- **Build axis:** `full` — Implemented in `chat/deduction_surface.py` (`_try_read_band_v3_mem`).
- **Liveness axis:** `live` — Consumed by deduction surface dispatch.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Pillar II (Semantic Rigor) through exact membership set relations.
- **Build fidelity:** `matches` — Parses singular membership premises paired with universal constraints.
- **Continuity:** `clean` — Extends deduction surface bands to set-membership reasoning.
- **Necessity/generality:** `irreducible` — Core membership argument band for deduction.
- **Fitness/value:** Correctly handles transitive set-membership deduction chains.

#### ADR-0259 — Conditional Membership Fusion Band (v4-CM)
- **Content summary:** Implements conditional-membership argument parsing and fusion rules in `chat/deduction_surface.py`.
- **Build axis:** `full` — Implemented in `chat/deduction_surface.py` (`_try_read_band_v4_cm`).
- **Liveness axis:** `live` — Active in deduction surface resolution.
- **Design fidelity:** Honors Axiom 3 (Propagation-over-Mutation) by propagating conditional constraints across fusion points.
- **Build fidelity:** `matches` — Fuses conditional and membership premises into canonical ROBDD inputs.
- **Continuity:** `clean` — Connects conditional reasoning to membership bands.
- **Necessity/generality:** `irreducible` — Essential fusion band for conditional-membership deduction.
- **Fitness/value:** Solves multi-premise conditional fusion problems without stochastic fallback.

#### ADR-0260 — Verb Predicate Band (v5-VP)
- **Content summary:** Implements verb-predicate argument parsing ("All X verb Y") in `chat/deduction_surface.py`.
- **Build axis:** `full` — Implemented in `chat/deduction_surface.py` (`_try_read_band_v5_vp`).
- **Liveness axis:** `live` — Consumed by deduction surface resolution and curriculum surface matching.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) by standardizing relational verb-predicate syntax.
- **Build fidelity:** `matches` — Handles subject-verb-object predicate structures with singular/plural agreement.
- **Continuity:** `clean` — Shared by deduction and curriculum surface layers.
- **Necessity/generality:** `irreducible` — Core relational verb band.
- **Fitness/value:** Enables exact deductive reasoning over action and property verbs.

#### ADR-0261 — Existential Witness Band (v6-EX)
- **Content summary:** Implements existential witness argument parsing ("Some X are Y") in `chat/deduction_surface.py`.
- **Build axis:** `full` — Implemented in `chat/deduction_surface.py` (`_try_read_band_v6_ex`).
- **Liveness axis:** `live` — Active in deduction surface resolution.
- **Design fidelity:** Honors Pillar III (Third Door) and wrong=0 discipline by enforcing sound existential witness bounds.
- **Build fidelity:** `matches` — Number allocation resolves prior Master Blueprint reservation ambiguity (`AA-73`, `AA-80`).
- **Continuity:** `clean` — Discharges Band v6-EX implementation; supercedes prior unallocated Rust SIMD reservation.
- **Necessity/generality:** `irreducible` — Mandatory existential argument band.
- **Fitness/value:** Solves existential syllogisms with exact witness bounds.

#### ADR-0262 — Curriculum Grounded Serving
- **Content summary:** Serves exam questions grounded exclusively in ratified chain corpora with anti-recall probes.
- **Build axis:** `full` — Implemented in `chat/curriculum_surface.py` and `chat/curriculum_serve_license.py`.
- **Liveness axis:** `live` — Active on the live serving path (`chat/runtime.py:1872`).
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and wrong=0 discipline by returning UNKNOWN for untaught facts.
- **Build fidelity:** `matches` — Serves from ratified curriculum chains while enforcing anti-recall probe checks.
- **Continuity:** `clean` — Extends deduction serving principles to domain curriculum.
- **Necessity/generality:** `irreducible` — Core curriculum-grounded serving engine.
- **Fitness/value:** Prevents hallucinations on domain exam questions by enforcing explicit curriculum grounding.

#### ADR-0263 — Ratified Ledger Bridge
- **Content summary:** Provides unified load, verification, and manifest state checking across serve licenses.
- **Build axis:** `full` — Implemented in `core/ratified_ledger.py`.
- **Liveness axis:** `live` — Consumed by `chat/deduction_serve_license.py` and `chat/curriculum_serve_license.py`.
- **Design fidelity:** Honors Pillar I (Mechanical Sympathy) and Pillar II (Semantic Rigor) by standardizing ledger verification.
- **Build fidelity:** `matches` — Unified bridge rules govern ledger loading and hash verification.
- **Continuity:** `clean` — Consolidates serve license ledger access.
- **Necessity/generality:** `generalization-candidate` — Unified ratified ledger interface across domain licenses.
- **Fitness/value:** Eliminates duplicate ledger verification code across serving modules.

#### ADR-0264 — Negative Curriculum and Premise Scope
- **Content summary:** Ratifies explicitly taught refutations (`negative`) and user-visible family premise count reporting.
- **Build axis:** `full` — Implemented in `chat/curriculum_surface.py` and `core/cli_proposal_queue.py`.
- **Liveness axis:** `live` — Validated in `tests/test_curriculum_surface.py` and CLI proposal queue commands.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and wrong=0 discipline by distinguishing taught refutations from unknown facts.
- **Build fidelity:** `matches` — Enforces R1–R9 rules for negative curriculum and volume honesty.
- **Continuity:** `clean` — Refines ADR-0262 curriculum serving semantics.
- **Necessity/generality:** `irreducible` — Mandatory for sound negative answer handling in curriculum serving.
- **Fitness/value:** Prevents false open-world inferences on explicitly refuted curriculum claims.

#### ADR-0265 — Negation in the Proposition Graph
- **Content summary:** Threads `GraphNode.negated` through intent, graph, step, and surface to represent denial.
- **Build axis:** `full` — Implemented in `generate/graph_planner.py`, `generate/semantic_templates.py`, `generate/realizer.py`, and `generate/intent_bridge.py`.
- **Liveness axis:** `live` — Active in proposition graph planning and surface realization.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 7 (Reality-over-Inheritance) by representing denial natively in graph structure.
- **Build fidelity:** `matches` — Fixes live defect where affirmative and negative surfaces rendered byte-identically under `realizer_grounded_authority`.
- **Continuity:** `clean` — Resolves realizer grounded authority denial bug surfaced during ADR-0088 testing.
- **Necessity/generality:** `irreducible` — Fundamental graph representation for logical denial.
- **Fitness/value:** Eliminates byte-identical surface collisions between true and negated propositions.

### 3. Stack Findings Rollup
- **`AA-424` 🟢** **ADR-0256** — Deduction Serve Earned License establishes reliability license gates in `chat/deduction_serve_license.py` with R-13 re-count enforcing distinct evidence thresholds (4 bands SERVE, 21 disclosure).
- **`AA-425` 🟢** **ADR-0257** — English Clause Argument Band (v2-EN) implements natural English propositional argument parsing over opaque terms in `chat/deduction_surface.py`.
- **`AA-426` 🟢** **ADR-0258** — Member Chain Band (v3-MEM) implements singular-membership argument parsing with universal constraints in `chat/deduction_surface.py`.
- **`AA-427` 🟢** **ADR-0259** — Conditional Membership Fusion Band (v4-CM) implements conditional-membership argument parsing in `chat/deduction_surface.py`.
- **`AA-428` 🟢** **ADR-0260** — Verb Predicate Band (v5-VP) implements verb-predicate argument parsing in `chat/deduction_surface.py`.
- **`AA-429` 🟡** **ADR-0261** — Existential Witness Band (v6-EX) implements existential argument parsing in `chat/deduction_surface.py`; allocated number resolves prior Master Blueprint reservation ambiguity (`AA-73`, `AA-80`).
- **`AA-430` 🟢** **ADR-0262** — Curriculum Grounded Serving implements exam-question answering over ratified chain corpora with anti-recall refusal probes in `chat/curriculum_surface.py`.
- **`AA-431` 🟢** **ADR-0263** — Ratified Ledger Bridge unifies license load, verification, and manifest state checking in `core/ratified_ledger.py`.
- **`AA-432` 🟢** **ADR-0264** — Negative Curriculum and Premise Scope ratifies explicitly taught refutations and family-size premise count visibility in `chat/curriculum_surface.py`.
- **`AA-433` 🟢** **ADR-0265** — Negation in the Proposition Graph threads `GraphNode.negated` to eliminate byte-identical affirmative/negative surface collisions.

---

## Stack A6.2 — Reader Arc Recalibration & Master Blueprint Governance

**Members:** ADR-0251, ADR-0252, ADR-0253, ADR-0254, ADR-0255 (5 ADRs)  
**Zone:** `M3-comprehension-reasoning` / `M4-expression-serving` / `master-blueprint-governance` | **Tier:** A  
**Prior Evidence:** `docs/adr/ADR-0251-*`, `docs/adr/ADR-0252-*`, `docs/adr/ADR-0253-*`, `tests/test_pack_draft_serve_boundary.py`, `core/cognition/surface_resolution.py`, `engine_state/__init__.py`

### 0. Why this is one stack
Phased family recalibrating the reader arc away from bespoke per-case regexes, consolidating the core problem-solving paradigm (expert structure-mapping), resolving Master Blueprint ADR number collisions, establishing the INV-33 dual-pack serve boundary, wiring grounded-open hedge arms, and baseline telemetry for candidate discovery yield.

### 1. Stack-level claim
The comprehension reader must reset to a clean base of expert relational structure-mapping on predictive processing, ID history must remain immutable under Blueprint governance while enforcing draft vs. runtime pack boundaries (INV-33), and surface resolution must hedge non-authoritative pack answers fail-closed.

### 2. Member ADR Cards

#### ADR-0251 — Reader-Arc Recalibration
- **Content summary:** Halts bespoke per-case regex work, resets `main` to a clean base, and proposes geometric surface-to-canonical normalization.
- **Build axis:** `full` (recalibration decision executed); `scaffolded` (§5 proposal rejected by ADR-0252).
- **Liveness axis:** `live` — Governs math reader development discipline on `main`.
- **Design fidelity:** Honors Pillar III (Third Door) and wrong=0 discipline by refusing brittle regex overfitting.
- **Build fidelity:** `matches` — Eradicated PR #80 debt and reset `main` to clean tip (`cbfc8ccb`).
- **Continuity:** `clean` — Re-anchored reader arc on sound `#77`–`#79` foundations.
- **Necessity/generality:** `irreducible` — Crucial governance pivot halting technical debt accumulation.
- **Fitness/value:** Protected `wrong=0` guarantees from being degraded by fail-open regex widenings.

#### ADR-0252 — Problem-Solving Paradigm Consolidation
- **Content summary:** Establishes expert structure-mapping over predictive-processing substrate; supersedes 6 prior paradigm docs.
- **Build axis:** `full` (paradigm consolidation ratified); `scaffolded` (§5 experiment pre-registered and executed).
- **Liveness axis:** `live` — Governing paradigm for comprehension and reasoning architecture.
- **Design fidelity:** Honors Axiom 1 (Geometry-First) and Pillar I (Mechanical Sympathy) by grounding cognition in free-energy minimization.
- **Build fidelity:** `matches` — §5 experiment returned pre-registered NO-GO (2026-07-28), cleanly stopping un-gated build authorization.
- **Continuity:** `superseded-cleanly` — Replaces six prior unratified paradigm documents while preserving core solving corridor.
- **Necessity/generality:** `irreducible` — Single governing paradigm document for CORE problem solving.
- **Fitness/value:** Aligns CORE architecture with expert cognitive science models while stopping un-promising SME builds.

#### ADR-0253 — Master Blueprint ADR Collision Resolution & Dual-Pack Boundary
- **Content summary:** Freezes ID history, maps Blueprint to `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`, and enforces INV-33 dual-pack boundary.
- **Build axis:** `full` — Implemented in `docs/adr/MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` and `tests/test_pack_draft_serve_boundary.py`.
- **Liveness axis:** `live` — Enforced by CI architecture test (`test_pack_draft_serve_boundary.py`) under INV-33.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and INV-33 by isolating runtime serve paths from draft source trees.
- **Build fidelity:** `matches` — Prohibits draft `packs/he` and `packs/grc` package imports on serve paths.
- **Continuity:** `clean` — Resolves Master Blueprint ID collision and clarifies language pack serving authority.
- **Necessity/generality:** `irreducible` — Mandatory governance freeze and architectural boundary guard.
- **Fitness/value:** Prevents un-compiled draft language pack data from leaking into production serving paths.

#### ADR-0254 — Grounded-Open Hedge Arm for the Shadow Coherence Gate
- **Content summary:** Adds a grounded-open hedge arm (`authoritative=False`, `grounded_open_hedge`) for pack-grounded surfaces with open geometric residuals.
- **Build axis:** `full` — Implemented in `core/cognition/surface_resolution.py`.
- **Liveness axis:** `live` — Active in shadow coherence gate surface resolution (`resolve_surface`).
- **Design fidelity:** Honors Pillar III (Third Door) and wrong=0 discipline by hedging non-authoritative pack definitions instead of false hard refusal.
- **Build fidelity:** `matches` — Uses structural grounding provenance and geometric token allowlist without question text parsing.
- **Continuity:** `unreconciled contradiction` — Introduces a third independent hedge mechanism alongside ADR-0028 and ADR-0038 (`AA-142` cluster).
- **Necessity/generality:** `reducible-to-unified-hedge-operator` — Candidate for consolidation with ADR-0028/0038 hedge operators.
- **Fitness/value:** Resolves false refusals on pack-grounded definitions while preserving fail-closed safety.

#### ADR-0255 — Discovery-Yield-Per-Served-Turn Baseline Telemetry
- **Content summary:** Tracks candidate proposal yield rates against a `turn_count_baseline` post-T11 ledger reset.
- **Build axis:** `full` — Implemented in `engine_state/__init__.py`, `core/cli_teaching.py`, and `tests/test_discovery_yield.py`.
- **Liveness axis:** `live` — Consumed by `core teaching discovery-yield` CLI.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Absolute Provenance by failing closed when baseline is un-stamped.
- **Build fidelity:** `matches` — Additive manifest field and pure yield rate calculation match design.
- **Continuity:** `clean` — Extends engine state manifest and teaching CLI.
- **Necessity/generality:** `irreducible` — Essential telemetry for clean post-reset candidate yield monitoring.
- **Fitness/value:** Prevents pre-reset traffic from corrupting post-reset candidate discovery yield metrics.

### 3. Stack Findings Rollup
- **`AA-434` 🟢** **ADR-0251** — Reader-Arc Recalibration halts bespoke per-case regex overfitting and resets `main` to a clean base while preserving `#77`–`#79` foundations.
- **`AA-435` 🟢** **ADR-0252** — Problem-Solving Paradigm Consolidation establishes expert structure-mapping over predictive processing substrate; §5 experiment returned pre-registered NO-GO.
- **`AA-436` 🟢** **ADR-0253** — Master Blueprint Collision Resolution & Dual-Pack Boundary enforces ID immutability and pins INV-33 dual-pack boundary (`packs/data/` serve-only authority).
- **`AA-437` 🔵** **ADR-0254** — Grounded-Open Hedge Arm implements a third independent hedge mechanism in `core/cognition/surface_resolution.py`, consolidating with `AA-142` hedge fragmentation cluster.
- **`AA-438` 🟢** **ADR-0255** — Discovery-Yield Baseline Telemetry adds fail-closed `turn_count_baseline` tracking to `engine_state` for post-reset candidate yield monitoring.
