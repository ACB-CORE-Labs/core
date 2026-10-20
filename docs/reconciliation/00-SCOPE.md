# 00 · Assessment Scope and Governance Record: CORE Restoration

**Status:** ACTIVE  
**Document Identity:** `docs/reconciliation/00-SCOPE.md`  
**Assessment Branch:** `reconciliation/intentional-design-restoration`  
**Working Repository:** `ACB-CORE-Labs/core`  
**Base Revision:** `069ceb55c55e066f4773ef186ba54e410164743a`  
**Document Date:** 2026-10-20  

---

## 1. Objective and Mandate

This document establishes the starting state, boundary constraints, governance rules, and review protocol for an evidence-grounded assessment of the **`ACB-CORE-Labs/core`** repository.

The intended continuation of this assignment is the **restoration and resumption of `ACB-CORE-Labs/core`** as a deterministic, inspectable, replayable cognitive engine on Conformal Geometric Algebra $\text{Cl}(4,1)$.

- This assignment establishes the starting state, scope, bounded inventory, and initial findings.
- It **does not authorize** runtime cleanup, code modification, component rewiring, a language migration (e.g. C++23, Rust, or Zig), or the selection of a historical restoration baseline.
- It **must not** be reinterpreted as a fresh rebuild in `core-iii` or any other successor or sibling workspace.

---

## 2. Verified Repository Distinctions vs. Unproven Claims

To ensure rigorous factual separation, verified repository distinctions are established based strictly on primary documentary and git evidence, separating verified facts from unproven narrative assertions:

| Repository / Workspace | Verified Identity & Evidence | Assessment Role & Boundary | Unproven / Disputed Assertions (Separated Out) |
|---|---|---|---|
| **`ACB-CORE-Labs/core`** | Active working repository. Primary work since 2026-05-13 reset (`docs/sessions/2026-05-13.md`: "*`core` is the primary work. `core-ai` is the archive*"). Contains complete Python $\text{Cl}(4,1)$ implementation, 314 ADR files, and full test suites. | **The Primary System Under Assessment.** Its existing implementation is to be preserved while we understand it. No code or tests are altered during assessment. | Narrative characterizations in external documents asserting that `core` was an "assembly failure" or that its working tree was abandoned are unverified claims requiring investigation against code reality. |
| **`ACB-CORE-Labs/coreai`** | Distinct remote and workspace (`git@github.com:ACB-CORE-Labs/coreai.git`). Pinned commit anchor `47d0004e` (2026-10-08); merged DISTILL-1 chain (#289–#302) ending at `93234bd1`. Contains experimental ablation records (`LOGOS-ABLATION-1`). | **External Comparison Evidence.** Supplies later corrections, experiments, and comparison reference artifacts (`REF-1`). Does not substitute for `core`. | Any claim that `coreai` branches automatically invalidate or replace `core` architecture is unproven. |
| **Historical `core-ai` (`AssetOverflow/core-ai`)** | Predecessor repository (pre-May-2026) using $\text{Cl}(3,0)$ Pauli isomorphism. Source of original Whitepaper and Yellowpaper (ported in commit `4ca2431e`). | **Predecessor Archive.** Reference material for design intent; not a source of direct patterns unless validated against the seven axioms. | Definitive remote location, access standing, and complete commit history remain to be verified. |
| **`core-iii` (`acbcore-labs/core-iii`)** | Sibling workspace containing exploratory C++23 architectural distillation drafts (`docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `NON-INHERITANCE.md`). | **Reference Preparation Material Only.** Supplies analytical notes. Does not bind workspace assumptions and is not a predetermined replacement architecture. Not edited during this pass. | Narrative claims in `core-iii` asserting that a C++23 migration is authorized or mandated for CORE are unratified and rejected for this assessment. |

---

## 3. The Owner's Design Evaluation Frame

All assessment observations, findings, and trade-offs are evaluated against the owner's established engineering philosophy (`docs/conceptualizing_engineering_mastery.md`, `README.md`, `docs/Whitepaper.md` §III, and `AGENTS.md`):

### The Three Engineering Pillars
1. **Mechanical Sympathy:** Software must understand the machine it runs on, aligning harmoniously with the computational substrate without fighting it.
2. **Semantic Rigor:** Every term, requirement, and constraint has one precise, mathematically defined meaning. Assumptions are scrubbed; no loose thresholds are tuned for "good enough."
3. **The Third Door:** When faced with a false dichotomy between two suboptimal compromises, do not split the difference. Formulate Path C—a fundamental structural redesign that dissolves the trade-off.

### The Universal Execution Algorithm
1. **Scrub and Validate:** If a constraint cannot be traced to fundamental mathematical or physical law, it is just a suggestion.
2. **Eradicate the Part or Process:** The best component is no component. Deletion precedes optimization.
3. **Simplify and Optimize:** Never optimize what should not exist.
4. **Accelerate Cycle Time:** Shorten the loop between design, testing, and evidence.
5. **Automate:** Lock in proven efficiency only after the structure is minimal, verified, and stable.

### The Seven Axioms (`docs/Whitepaper.md` §III)
1. **Geometry-First:** Find the intrinsic representation space before choosing data structures.
2. **Field-State:** System state is a continuous distribution/field over the manifold, not isolated objects.
3. **Propagation-over-Mutation:** Propagate continuous state through structured operators rather than stepwise in-place mutation.
4. **Dual-Correction:** Every forward operator must possess a conjugate/corrective counterpart.
5. **Reconstruction-over-Storage:** Encode sufficient structural invariants to reconstruct states rather than storing raw traces.
6. **Compilation-Last:** Concrete classes, loops, and tables are decided last.
7. **Reality-over-Inheritance:** No abstraction is sacred; every component survives on demonstrated structural merit alone.

### The North Star
$$\text{listen} \longrightarrow \text{comprehend} \longrightarrow \text{recall} \longrightarrow \text{think} \longrightarrow \text{articulate} \longrightarrow \text{learn from reviewed correction} \longrightarrow \text{replay deterministically}$$

---

## 4. Disputed Invariants as Formal Review Questions

In adherence to assessment discipline, discovering an apparent discrepancy or defect does not authorize an immediate architectural verdict or premature repair. Key tensions across historical documents, code implementations, and external experiments are held as **Formal Review Questions**:

- **Review Question 1 (Algebraic Tolerance Threshold):**  
  *Context:* Whitepaper Invariant I and `AGENTS.md` specify `versor_condition(F) < 1e-6`, while `algebra/versor.py` defines `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` (noted in historical claim `AA-4`).  
  *Question:* What is the mathematically and mechanically justified tolerance for Cl(4,1) multivector closure across IEEE 754 float32 operations, and what is the exact empirical margin on live mounts?

- **Review Question 2 (Vocabulary Representation on the Conformal Manifold):**  
  *Context:* Whitepaper Invariants II and III specify that vocabulary items are null points on the conformal horosphere ($X \cdot X = 0$), whereas `VocabManifold.add()` enforces a unit versor condition ($V \widetilde{V} = 1$), which rejects genuine conformal null points (`AA-2`).  
  *Question:* What is the lawful algebraic relationship between conformal point representations and operator versors in the Logos vocabulary manifold?

- **Review Question 3 (Role of Geometry in Semantic Determination vs. Custody):**  
  *Context:* `coreai` PR #291 (`LOGOS-ABLATION-1`) reported that geometric Clifford products and conformal distance failed to perform semantic determination on the WA1 possession-polar vertical, while functioning reliably for exact identity and token custody (`core-iii/docs/NON-INHERITANCE.md` §2.4).  
  *Question:* Which cognitive functions in CORE are strictly geometric (representation, custody, invariant verification) versus propositional/logical (ROBDD, typed contract validation)?

- **Review Question 4 (Epistemic Transitions and Drift-Repair Boundary):**  
  *Context:* `AGENTS.md` strictly prohibits watchdog normalization, post-hoc drift repair, or hidden unitization in hot paths, restricting closure to `algebra/versor.py` (`_close_applied_versor`).  
  *Question:* How do live session field updates and memory consolidation operations maintain the versor condition by construction without triggering drift-repair violations?

- **Review Question 5 (Sensory Modality Recovery Boundary):**  
  *Context:* ADR-0013 and `sensorium/` define projection heads as the "Logos-recovery boundary" converting any surface signal into a `(32,)` Cl(4,1) multivector.  
  *Question:* How faithfully does the current implementation of `sensorium/` isolate modality-specific heuristics from entering the engine field state?

---

## 5. Bounded Inventory Scope Definition

The source inventory ([docs/reconciliation/source-index.csv](source-index.csv)) represents a **bounded inventory** established for restoration planning, not an exhaustive census of every byte in the repository.

### Boundary Specification:
1. **Included in Initial Inventory (757 Sources):**
   - Foundational papers: Whitepaper, Yellowpaper, Position Paper.
   - All 314 `ADR-*.md` files and 19 companion notes/indexes in `docs/adr/`.
   - All 24 session records in `docs/sessions/` and `docs/adr/`.
   - Curated design notes, plans, and briefs: `docs/plans/` (20), `docs/handoffs/` (79), `docs/briefs/` (27), `docs/architecture/` (9), `docs/specs/` (8), `docs/analysis/` (119).
   - Assessment and audit dossiers: `docs/assessment/` (29), `docs/audit/` (21), `docs/adr-audit/` (19).
   - Research and experiment reports: `docs/research/` (59).
   - Core runtime component entrypoints: 17 load-bearing modules across algebra, field, vault, core, generate, ingest, sensorium, teaching, and packs.
   - Core test, invariant, and toolchain gates: 13 primary enforcement files.
   - Cross-repository anchors: 7 reference commits and documents from `coreai`, `core-iii`, and historical `core-ai`.

2. **Explicitly Excluded from Current Boundary:**
   - Non-entrypoint internal modules within runtime packages (e.g. internal helpers in `algebra/`, `field/`, `vault/`).
   - The ~800 individual test files tracked in [tests/full_only_baseline.txt](file:///Users/kaizenpro/Projects/acbcore-labs/core/tests/full_only_baseline.txt) outside the curated invariant and membership suites.
   - Raw benchmark runners and results in `benchmarks/`.
   - Raw JSON evaluation datasets and samples in `evals/`.
   - Binary media files, diagrams, and images (`docs/handoffs/assets/`, `docs/assets/`).
   - Cache, transient state, and scratch directories (`.data/`, `workbench_data/`, `engine_state/`).

3. **Status Extraction vs. Substantive Review Distinction:**
   - Sources marked `header_extracted` in the inventory have had their metadata (date, declared status string) extracted by automated inspection of frontmatter/headers. Their substantive content has not yet been audited.
   - Sources marked `document_read` have been analyzed in full during this assessment.

---

## 6. Prohibited Work and Operational Rules

During this assessment phase:
- Preserve existing code, tests, and configuration without modification.
- No dependency installation, virtual environment mutation, or toolchain upgrades.
- No execution of runtime applications, migrations, or state-writing demos.
- No execution of the full test suite.
- No invariant or numerical tolerance modifications.
- No editing or renumbering of historical ADRs, papers, or session notes.
- No rollback point or restoration baseline selection without explicit owner ruling.
- No remote write operations without prior presentation and explicit approval.
