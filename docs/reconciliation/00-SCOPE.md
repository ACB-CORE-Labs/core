# 00 · Assessment Scope and Governance Record: CORE Restoration

**Status:** ACTIVE  
**Document Identity:** `docs/reconciliation/00-SCOPE.md`  
**Assessment Branch:** `reconciliation/intentional-design-restoration`  
**Working Repository:** `ACB-CORE-Labs/core`  
**Base Revision:** `069ceb55c55e066f4773ef186ba54e410164743a`  
**Document Date:** 2026-10-20  

---

## 1. Objective and Mandate

This document establishes the starting state, scope, governance boundaries, and source inventory protocol for an evidence-grounded assessment of the **`ACB-CORE-Labs/core`** repository.

The intended continuation of this effort is the **restoration and resumption of `ACB-CORE-Labs/core`** as an inspectable, replayable, evidence-governed, deterministic cognitive engine on Cl(4,1) Conformal Geometric Algebra.

This assignment establishes the starting state, scope, and source inventory.
- It **does not** authorize cleanup, runtime implementation, language migrations, or selection of a historical restoration baseline.
- It **must not** be reinterpreted as a fresh rebuild in `core-iii` or any other successor or sibling workspace.

---

## 2. Core Repository Relationships and Lineage

To prevent historical confusion, the following repository identities and roles are formally defined and enforced:

| Repository / Entity | Role in this Assessment | Governing Boundary |
|---|---|---|
| **`ACB-CORE-Labs/core`** | **The Primary System Under Assessment.** The working repository being assessed for restoration and resumption. | Its existing Cl(4,1) Python implementation, test suites, and documentation are to be preserved intact while we understand them. No code is modified, deleted, or rewired during assessment. |
| **`coreai` (`ACB-CORE-Labs/coreai`)** | **External Evidence & Comparison Source.** | Supplies later corrections, experiments, ablation verdicts (e.g. `LOGOS-ABLATION-1`), and comparison evidence (e.g. DISTILL-1 PRs #289–#302, `REF-1` reference corpora). Does not replace `core`. |
| **Historical `core-ai` (`AssetOverflow/core-ai`)** | **Predecessor Archive.** | The pre-May-2026 Cl(3,0) Pauli-isomorphism implementation where early papers (Whitepaper, Yellowpaper) and initial subsystem concepts (`core_logos`, `core_sensorium`, `core_ingest`) originated. Its exact historical location and relevant commit history remain a distinct source whose status must be verified rather than assumed. |
| **`core-iii` (`acbcore-labs/core-iii`)** | **Preparation & Distillation Reference Material.** | Supplies analysis and reference documentation (e.g., master distillation notes, mathematical analyses). It does **not** represent a predetermined replacement architecture or binding workspace. No files in `core-iii` are edited during this pass. |

---

## 3. Strict Operating Invariants and Prohibitions

During this assessment phase, the following operational prohibitions are in effect without exception:

1. **Preservation of Existing Implementation:** The existing implementation of `ACB-CORE-Labs/core` is to be preserved while we understand it. No components, runtime paths, tests, dependencies, or build configurations may be modified or deleted.
2. **No Premature Rollback or Baseline Selection:** No historical revision is yet designated as “known good.” Selecting a rollback point or declaring a restoration baseline is explicitly prohibited until evidence is assembled.
3. **No Language Migration:** No C++23 (or Rust/Zig) migration is authorized by this assessment. CORE's deterministic Python substrate on Cl(4,1) is the subject of assessment.
4. **Defect Discovery ≠ Authorization to Repair:** Discovering a defect (drift, collision, missing file, or broken invariant) authorizes recording it in the findings ledger, not repairing it.
5. **No Runtime Execution or Test Mutation:** Do not run applications, background daemons, migrations, or state-writing demos. Do not launch the full test suite.
6. **No Invariant or Tolerance Relaxation:** Do not change architectural invariants, numerical tolerances (e.g., `versor_condition(F) < 1e-6`), or gate thresholds.
7. **No Historical Document Alteration:** Do not reword or overwrite historical ADRs, session notes, whitepapers, or yellowpapers. Duplicate ADR IDs and rotted paths are recorded as findings, not rewritten.
8. **No Parallel Memory or Repair Layers:** In accordance with `AGENTS.md`, do not introduce drift-repair layers, watchdog normalization, or stochastic fallback mechanisms.
9. **Gate Integrity:** The larger review and cleanup gates remain intact. All findings, classifications, and proposed review units require human review and approval.
10. **Remote Write Guard:** No remote push, branch deletion, force-push, or modification of `main` is permitted. Any proposed remote interaction requires prior explicit approval.

---

## 4. Assessment Deliverables and Ledger Architecture

The assessment process produces a unified, evidence-grounded record organized into dedicated files:

1. **`docs/reconciliation/00-SCOPE.md` (This Document):** Ground rules, repo boundaries, prohibitions, and working definitions.
2. **`docs/reconciliation/source-index.csv`:** An exhaustive, typed inventory of all source materials across eight distinct source families, distinguishing verbatim records from derived summaries, recording declared statuses literally, and tracking review levels (`inventoried`, `read`, `traced into code`, `independently reproduced`).
3. **`docs/reconciliation/01-FINDINGS.md`:** The single, canonical findings ledger recording directly established observations with full attribution (original obligation, subsequent change, stated reason, implementation sites, evidence scope, classification, architectural consequence, proposed disposition, verification status, and unresolved questions).
   - No conclusions copied from earlier unverified summaries are entered as established fact.
   - Inherited measurements and prior audit findings are indexed as historical claims requiring verification.
   - No parallel agent-specific findings ledgers are permitted.

---

## 5. Review Phases and Next Steps

The assessment proceeds in structured phases:
- **Phase 0 (Current):** Setup, repository verification, scope definition, source indexing, and initial established findings.
- **Phase 1:** Reading and verifying foundational documents (Whitepaper, Yellowpaper, foundational ADRs, and initial session notes).
- **Phase 2:** Tracing core architectural paths (algebra, field state propagation, vault storage, deterministic perception/reader, turn loop, and realizer).
- **Phase 3:** Cross-referencing against external evidence (`coreai` distillation/ablation results, historical `core-ai` origins) and resolving contradictions.
- **Phase 4:** Submitting the integrated assessment and proposed first connected decision chain for substantive owner review and restoration baseline determination.
