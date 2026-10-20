# 00 · Assessment Scope and Governance Record: CORE Restoration

**Status:** ACTIVE  
**Document Identity:** `docs/reconciliation/00-SCOPE.md`  
**Assessment Branch:** `reconciliation/intentional-design-restoration`  
**Working Repository:** `ACB-CORE-Labs/core`  
**Agreed Reference Revision (Starting Point):** `069ceb55c55e066f4773ef186ba54e410164743a` (Preserves a review starting point; does not designate a historical restoration baseline)  
**Document Date:** 2026-10-20  

---

## 1. Objective and Mandate

This document establishes the starting state, boundary constraints, governance rules, and review protocol for an evidence-grounded assessment of the **`ACB-CORE-Labs/core`** repository.

The intended continuation of this assignment is the **restoration and resumption of `ACB-CORE-Labs/core`** as a deterministic, inspectable, replayable cognitive engine on Conformal Geometric Algebra $\text{Cl}(4,1)$.

- This assignment establishes the starting state, scope, bounded inventory, and initial findings.
- It **does not authorize** runtime cleanup, code modification, component rewiring, a language migration (e.g. C++23, Rust, or Zig), or the selection of a historical restoration baseline.
- It **must not** be reinterpreted as a fresh rebuild in `core-iii` or any other successor or sibling workspace.

---

## 2. Verified Repository Distinctions vs. Assessment Boundaries

To ensure rigorous factual separation, repository distinctions are established based strictly on primary documentary and git evidence, separating verified facts from unproven narrative assertions and defining current assessment boundaries:

| Repository / Workspace | Verified Identity & Evidence | Assessment Role & Boundary | Narrative Assertions vs. Assessment Boundary |
|---|---|---|---|
| **`ACB-CORE-Labs/core`** | Active working repository. Primary work since 2026-05-13 reset (`docs/sessions/2026-05-13.md`: "*`core` is the primary work. `core-ai` is the archive*"). Contains existing Python $\text{Cl}(4,1)$ implementation (completeness remains under assessment), 314 ADR files, and full test suites. | **The Primary System Under Assessment.** Its existing implementation is to be preserved while we understand it. No code or tests are altered during assessment. | External narrative claims asserting that `core` was an "assembly failure" or that work on it was abandoned are unverified claims requiring investigation against code reality. |
| **`ACB-CORE-Labs/coreai`** | Distinct remote and workspace (`git@github.com:ACB-CORE-Labs/coreai.git`). Pinned commit anchor `47d0004e` (2026-10-08); merged DISTILL-1 chain (#289–#302) ending at `93234bd1`. Contains experimental ablation records (`LOGOS-ABLATION-1`). | **External Comparison Evidence.** Supplies later corrections, experiments, and comparison reference artifacts (`REF-1`). Does not substitute for `core`. | Any claim that `coreai` branches automatically invalidate or replace `core` architecture is unproven. |
| **Historical `core-ai` (`AssetOverflow/core-ai`)** | Predecessor repository (pre-May-2026) using $\text{Cl}(3,0)$ Pauli isomorphism. Source of original Whitepaper and Yellowpaper (ported in commit `4ca2431e`). | **Predecessor Archive.** Reference material for design intent; not a source of direct patterns unless validated against the seven axioms. | Definitive remote location, access standing, and complete commit history remain to be verified. |
| **`core-iii` (`acbcore-labs/core-iii`)** | Sibling workspace containing exploratory C++23 architectural distillation drafts (`docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `NON-INHERITANCE.md`). | **Reference Preparation Material Only.** Supplies analytical notes. Does not bind workspace assumptions and is not a predetermined replacement architecture. Not edited during this pass. | **Assessment Boundary:** No C++23 migration is authorized by this assessment. Questions of replacement architecture or historical migration authority are outside this assessment's mandate; `core-iii` is strictly reference preparation material. |

---

## 3. The Owner's Design Evaluation Frame

All assessment observations, findings, and trade-offs are evaluated against the owner's established engineering philosophy (`docs/Whitepaper.md` §III–§IV, `docs/conceptualizing_engineering_mastery.md`, `README.md`, and `AGENTS.md`):

### The Three Engineering Pillars (`docs/Whitepaper.md` §IV)
1. **Mechanical Sympathy:** Software must understand the machine it runs on, aligning harmoniously with the computational substrate without fighting it.
2. **Semantic Rigor:** Every term, requirement, and constraint has one precise, mathematically defined meaning. Assumptions are scrubbed; no loose thresholds are tuned for "good enough."
3. **The Third Door:** When faced with a false dichotomy between two suboptimal compromises, do not split the difference. Formulate Path C—a fundamental structural redesign that dissolves the trade-off.

### The Universal Execution Algorithm (`docs/conceptualizing_engineering_mastery.md`)
1. **Scrub and Validate:** If a constraint cannot be traced to fundamental mathematical or physical law, it is just a suggestion.
2. **Eradicate the Part or Process:** The best component is no component. Deletion precedes optimization.
3. **Simplify and Optimize:** Never optimize what should not exist.
4. **Accelerate Cycle Time:** Shorten the loop between design, testing, and evidence.
5. **Automate:** Lock in proven efficiency only after the structure is minimal, verified, and stable.

### The Seven Axioms (`docs/Whitepaper.md` §III)

The Seven Axioms are established in `docs/Whitepaper.md` §III as foundational principles. To evaluate the system without prejudging the outcome, this assessment strictly separates the **general axiomatic principles** (restored verbatim from the Whitepaper) from the **historical realization statements** (specific design assertions to trace in code, not governing assumptions of this assessment), qualifying tensions by reference to the canonical review question register:

1. **Geometry-First** — *Every problem has an intrinsic space, and the first task is to find that space before choosing data structures, algorithms, or equations.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"CORE chose Cl(4,1) because it is the intrinsic space of conformal geometry in three dimensions — the space where Euclidean motions, inversions, and distances are all algebraic products."*  
   - **Review Qualification:** How Cl(4,1) representation is structured across runtime subsystems and projection heads is held for investigation during substantive review (see [`REV-Q-006`](01-FINDINGS.md#rev-q-006-sensory-modality-recovery-boundary)).

2. **Field-State** — *The native form of state is a field, distribution, or relational structure over a space, not a heap of isolated objects.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"The CORE field state is a single multivector in Cl(4,1), not a list of embeddings."*  
   - **Review Qualification:** Whether live field state operates as a single multivector or through multi-component structures without destructive interference is held for investigation (see [`REV-Q-005`](01-FINDINGS.md#rev-q-005-epistemic-transitions-and-drift-repair-boundary) and [`REV-Q-006`](01-FINDINGS.md#rev-q-006-sensory-modality-recovery-boundary)).

3. **Propagation-over-Mutation** — *The primary mode of computation is propagation through a structured medium, not stepwise mutation of flat records.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"Every generation step is a versor product: `F ← V · F · reverse(V)`. Nothing is mutated in place."*  
   - **Review Qualification:** Finite-precision propagation and operator composition across live turns are held for investigation (see [`REV-Q-001`](01-FINDINGS.md#rev-q-001-algebraic-tolerance-threshold) and [`REV-Q-005`](01-FINDINGS.md#rev-q-005-epistemic-transitions-and-drift-repair-boundary)).

4. **Dual-Correction** — *Every meaningful forward operator should have a corrective, conjugate, adjoint, or opposing counterpart that restores coherence or reduces distortion.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"The versor's reverse is its correction: `reverse(V)` is the conjugate of `V` that closes the sandwich product and enforces closure on the manifold."*  
   - **Review Qualification:** Manifold closure and numerical tolerance floors across finite float operations are held for investigation (see [`REV-Q-001`](01-FINDINGS.md#rev-q-001-algebraic-tolerance-threshold)).

5. **Reconstruction-over-Storage** — *What matters is not storing every detail explicitly, but encoding enough structured state to reconstruct what is needed at the right moment.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"The vault stores versors — not tokens, not full context windows. Recall is reconstruction via the CGA inner product, not retrieval of a stored string."*  
   - **Review Qualification:** Conformal vocabulary point representation, unit versor storage, and exact recall fidelity are held for investigation (see [`REV-Q-002`](01-FINDINGS.md#rev-q-002-vocabulary-representation-on-the-conformal-manifold), [`REV-Q-003`](01-FINDINGS.md#rev-q-003-geometric-custody-vs-relational-lookup), and [`REV-Q-004`](01-FINDINGS.md#rev-q-004-role-of-geometry-in-semantic-determination-and-tested-outcomes)).

6. **Compilation-Last** — *Loops, tensors, tables, classes, and kernels are implementation targets chosen after the deeper representation is defined, not before.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"The algebra was defined first. The Rust kernels, MLX tensors, and Python dataclasses were written to serve it."*  
   - **Review Qualification:** Toolchain requirements and implementation boundaries across Python 3.12, C++, and Rust remain strictly under assessment (see [`FIND-0003`](01-FINDINGS.md#find-0003-multi-repository-distinctions-and-current-assessment-boundary) and [`FIND-0004`](01-FINDINGS.md#find-0004-python-toolchain-environment-and-local-ci-contract)).

7. **Reality-over-Inheritance** — *No abstraction is sacred because it is old, standard, or well-established; it survives only if it faithfully serves structure, insight, and generative power.*  
   - **Historical Whitepaper Realization Statement (Design assertion to trace; not an assessment assumption):** *"This axiom is the reason we deleted the spectral normalization monitor, the grade guard, the drift correction timer, the ANN index, and the pseudoscalar accumulation check. None of them survived contact with the algebra."*  
   - **Review Qualification:** Distinguishing semantic anchoring from prohibited drift repair is held for investigation (see [`REV-Q-005`](01-FINDINGS.md#rev-q-005-epistemic-transitions-and-drift-repair-boundary)).  
   - **Operational Boundary Override:** As established in the explicit notice below, all deletion guidance is strictly subordinated to the No-Cleanup Boundary during this restoration assessment.

### The North Star
$$\text{listen} \longrightarrow \text{comprehend} \longrightarrow \text{recall} \longrightarrow \text{think} \longrightarrow \text{articulate} \longrightarrow \text{learn from reviewed correction} \longrightarrow \text{replay deterministically}$$

---

> [!IMPORTANT]
> ### Explicit Subordination of Deletion Guidance to the No-Cleanup Boundary
> The owner's engineering framework emphasizes aggressive deletion in normal active engineering cycles (Execution Algorithm Step 2: *"Eradicate the Part or Process: The best component is no component"*; Whitepaper Axiom 7: *"Reality-over-Inheritance"*; `AGENTS.md` Standing Philosophy #1: *"Less is more... prefer removing to adding"*).  
> **However, for the duration of this restoration assessment assignment, all deletion and pruning guidance is strictly subordinated to the No-Cleanup Boundary.**  
> Discovering an unused, disconnected, redundant, failing, or poorly-factored component, test, or document does **not** authorize deleting, disconnecting, pruning, or altering it. No code, test, documentation, or historical artifact may be removed or refactored during this assessment. Cleanup belongs exclusively to future resumption phases under explicit owner approval.

---

## 4. Disputed Invariants and Historical Claims

In adherence to assessment discipline, discovering an apparent discrepancy or defect does not authorize an immediate architectural verdict or premature repair. Key tensions across historical documents, code implementations, and external experiments are held as **Formal Review Questions** rather than declared as verdicts.

To prevent divergent or parallel registers, all review questions are maintained in a single canonical register:  
👉 **[Canonical Question Register in `docs/reconciliation/01-FINDINGS.md` §3](01-FINDINGS.md#3-canonical-question-register-disputed-invariants--historical-claims)**

The questions currently registered for substantive review are:
- [**`REV-Q-001`**](01-FINDINGS.md#rev-q-001-algebraic-tolerance-threshold): Algebraic Tolerance Threshold (`versor_condition(F) < 1e-6` vs `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5`, claim `AA-4`)
- [**`REV-Q-002`**](01-FINDINGS.md#rev-q-002-vocabulary-representation-on-the-conformal-manifold): Vocabulary Representation on the Conformal Manifold (Null points $X \cdot X = 0$ vs unit versors $V \widetilde{V} = 1$, claim `AA-2`)
- [**`REV-Q-003`**](01-FINDINGS.md#rev-q-003-geometric-custody-vs-relational-lookup): Geometric Custody vs Relational Lookup (`VocabManifold.nearest()` behavior & exact CGA recall, claim `AA-1`)
- [**`REV-Q-004`**](01-FINDINGS.md#rev-q-004-role-of-geometry-in-semantic-determination-and-tested-outcomes): Role of Geometry in Semantic Determination and Tested Outcomes (`coreai` PR #291 `LOGOS-ABLATION-1`)
- [**`REV-Q-005`**](01-FINDINGS.md#rev-q-005-epistemic-transitions-and-drift-repair-boundary): Epistemic Transitions and Drift-Repair Boundary (Enforcing `INV-21`..`INV-30` without prohibited hot-path normalization)
- [**`REV-Q-006`**](01-FINDINGS.md#rev-q-006-sensory-modality-recovery-boundary): Sensory Modality Recovery Boundary (ADR-0013 and `sensorium/` projection to Cl(4,1) multivectors)
- [**`REV-Q-007`**](01-FINDINGS.md#rev-q-007-historical-predecessor-lineage-and-commit-integrity): Historical Predecessor Lineage and Commit Integrity (Git blob `aa80bce` and historical `core-ai` remote provenance)

---

## 5. Bounded Inventory Scope Definition

The source inventory ([`docs/reconciliation/source-index.csv`](source-index.csv)) represents a **bounded inventory** of exactly **757 sources** established for restoration planning, not an exhaustive census of every byte in the repository.

### Exact Inventory Composition (757 Sources):
1. **Foundational Papers (3 sources):**
   - `docs/Whitepaper.md`, `docs/Yellowpaper.md`, `docs/position_paper.md`.
2. **Architectural Decision Records in `docs/adr/` (314 sources):**
   - All 314 `ADR-*.md` files (representing 252 base numbers, 11 Category A base collision sets [24 files], 1 Category B sub-suffix collision [2 files], and the phased sub-decision families).
   - **Phased Sub-Decision Families Roster Reconciliation:**
     The historical ADR census (`docs/adr-audit/01-adr-census.md` §2) indexed phased sub-decision families under the heading *"11 base numbers, 60 files"*. Direct machine recalculation against the disk files reveals the exact mathematical derivation of that historical figure and its relationship to in-repo files:
     - The census counted both the base document AND all suffixed variants across 11 base numbers:
       | Base # | Base Title | Family Count | Files (Base + Suffixed Variants) |
       |---|---|:---:|---|
       | `0073` | Anchor lens: substrate variation | 5 | 1 base (`ADR-0073`) + 4 variants (`a`, `b`, `c`, `d`) |
       | `0114` | Expert capability roadmap | 7 | 1 base (`ADR-0114`) + 6 variants (`a`, `a.2`, `a.5`, `a.6`, `a.8`, `a.10`) |
       | `0118` | Stepped realizer | 2 | 1 base (`ADR-0118`) + 1 variant (`a`) |
       | `0119` | GSM8K eval lane roadmap | 9 | 1 base (`ADR-0119`) + 8 variants (`.1`, `.2`, `.3`, `.4`, `.5`, `.6`, `.7`, `.8`) |
       | `0131` | Re-target math expert benchmarks | 16 | 1 base (`ADR-0131`) + 15 variants (`.1.F`, `.1.S`, `.2`, `.2.B`, `.3`, `.4`, `.5`, `.G`, `.G.0`, `.G.1`, `.G.2`, `.G.3`, `.G.3.1`, `.G.4`, `.G.5`) |
       | `0136` | Statement-layer corridor | 7 | 1 base (`ADR-0136`) + 6 variants (`.S.1`, `.S.2`, `.S.4`, `.S2`, `.S3~1`, `.S3~2`) |
       | `0164` | Incremental comprehension reader | 5 | 1 base (`ADR-0164`) + 4 variants (`.1`, `.2`, `.3`, `.4`) |
       | `0168` | FrameClaim ratification | 2 | 1 base (`ADR-0168`) + 1 variant (`.1`) |
       | `0169` | CompositionClaim ratification | 2 | 1 base (`ADR-0169`) + 1 variant (`.1`) |
       | `0189` | Comparative reading | 2 | 1 base (`ADR-0189`) + 1 variant (`a`) |
       | `0201` | Propositional canonicalizer | 2 | 1 base (`ADR-0201`) + 1 variant (`.1`) |
       | **Total** | **Census Family Sum** | **60** | **11 base files + 48 unique variants + 1 collision in 0136.S3 = 60 files** |
     - **In-Repo Roster Reality:** In addition to the 11 families in the census table, base `0123` also carries a suffixed variant file (`ADR-0123a-inference-shape-synonym.md`). Counting strictly the suffixed variant files across the entire repository yields exactly **49 suffixed variant files** across **12 base numbers**. In `source-index.csv`, all 314 ADR files are fully inventoried with unique source IDs.
3. **ADR Companion Notes, Briefs, and Indexes in `docs/adr/` (19 sources):**
   - Companion notes including `README.md`, `INDEX-by-domain.md`, session notes, briefs, and scopes.
4. **Session Records in `docs/sessions/` (22 sources):**
   - All 22 markdown session files in `docs/sessions/` (7 additional session files located in `docs/adr/` are indexed under ADR companions, yielding 29 session records in total across the repository).
5. **Curated Design Notes, Plans, and Briefs (224 sources):**
   - `docs/plans/` (20 files)
   - `docs/architecture/` (9 files)
   - `docs/analysis/` (117 files)
   - `docs/handoffs/` (67 top-level files)
   - `docs/briefs/` (8 top-level files)
   - `docs/specs/` (3 top-level files)
6. **Assessment and Audit Dossiers (82 sources):**
   - `docs/assessment/` (12 top-level files)
   - `docs/audit/` (14 markdown reports)
   - `docs/adr-audit/` (56 files: 15 top-level audit records, 24 stack dossiers in `10-stack-dossiers/`, 17 ADR cards in `11-adr-cards/`)
7. **Research and Experiment Reports (56 sources):**
   - `docs/research/` (56 markdown dossiers and experiment verdicts)
8. **Core Runtime Component Entrypoints (17 sources):**
   - 17 load-bearing modules across `algebra/`, `field/`, `vault/`, `core/`, `generate/`, `ingest/`, `sensorium/`, `session/`, `teaching/`, and `packs/`.
9. **Core Test, Invariant, and Toolchain Gates (13 sources):**
   - 13 primary enforcement files including `AGENTS.md`, `Makefile`, `CLAIMS.md`, `pyproject.toml`, `.python-version`, and runner scripts.
10. **Cross-Repository Anchors (7 sources):**
    - 7 reference commits, PRs, and documents from `coreai`, `core-iii`, and historical `core-ai`.

$$\text{Total Sources} = 3 + 314 + 19 + 22 + 224 + 82 + 56 + 17 + 13 + 7 = 757$$

### Explicitly Excluded from Initial Boundary:
- Subdirectory files omitted from this initial pass: `docs/briefs/parallel-2026-05-23/` (19 files), `docs/assessment/10-layer-cards/` (9 files), `docs/assessment/20-component-cards/` (8 files), `docs/specs/foundational-families/` (5 files), `docs/handoffs/legacy/` and `phase-3b-4-skeleton` (3 files).
- Non-entrypoint internal modules within runtime packages (internal helpers in `algebra/`, `field/`, `vault/`, etc.).
- The ~800 individual test files tracked in [`tests/full_only_baseline.txt`](file:///Users/kaizenpro/Projects/acbcore-labs/core/tests/full_only_baseline.txt) outside the curated invariant and membership suites.
- Raw benchmark runners and results in `benchmarks/`.
- Raw JSON evaluation datasets and samples in `evals/`.
- Binary media files, diagrams, and images (`docs/handoffs/assets/`, `docs/assets/`).
- Cache, transient state, and scratch directories (`.data/`, `workbench_data/`, `engine_state/`).

### Status Extraction vs. Substantive Review Distinction:
- Sources marked `header_extracted` in the inventory have had their metadata (date, full multiline declared status string) extracted by automated inspection of frontmatter/headers. Their substantive content has not yet been audited.
- Sources marked `document_read` have been analyzed in full during this assessment.

### Declared Metadata vs. Verified Operational Authority:
In `docs/reconciliation/source-index.csv`, the column `declared_status_or_unknown` records the **verbatim textual status declared within the document's header block** at the agreed reference revision (`069ceb55`).
- **Declared status is not verified authority:** A document declaring `Status: Accepted` records only what the document declares; it does not constitute verified proof that the decision was reviewed, ratified by the owner, or is currently active in production code.
- **Proposed status is not an absence of mechanism:** A document declaring `Status: Proposed` records an unpromoted or unratified status in the document text; it does not prove that code corresponding to the proposal was never written or merged.
All operational verification and reconciliation of authority are deferred to substantive review.

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
