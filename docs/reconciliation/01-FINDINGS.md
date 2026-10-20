# 01 · Findings Ledger: CORE Restoration Assessment

**Status:** ACTIVE  
**Document Identity:** `docs/reconciliation/01-FINDINGS.md`  
**Assessment Branch:** `reconciliation/intentional-design-restoration`  
**Working Repository:** `ACB-CORE-Labs/core`  
**Base Revision:** `069ceb55c55e066f4773ef186ba54e410164743a`  
**Document Date:** 2026-10-20  

---

## 1. Governance and Ledger Discipline

This findings ledger records observations and facts directly established during the assessment of `ACB-CORE-Labs/core`.

**Discipline Rules:**
1. **Direct Establishment Only:** Only findings directly verified on disk or through evidence during this assessment are recorded as confirmed findings.
2. **No Inherited Conflation:** Conclusions copied from earlier audit summaries (such as `docs/adr-audit/20-finding-register.md` or `docs/assessment/30-gap-register.md`) are not admitted as established facts; they are indexed as historical claims requiring independent verification.
3. **No Parallel Ledgers:** This is the single, canonical findings ledger for the restoration assessment. No agent-specific or auxiliary finding lists are permitted.
4. **Defect Discovery ≠ Authorization to Repair:** Recording a defect here does not authorize modifying runtime code, tests, or historical documents.

---

## 2. Established Findings Register

### FIND-0001: ADR Numbering Collisions in `docs/adr/`

- **Original obligation:** Under `ADR-0225` ("ADR Corpus Hygiene"), every Architectural Decision Record must possess a unique top-level sequence number, and "repository history wins for IDs."
- **Subsequent change:** 12 distinct ADR numbering collisions exist on disk across 27 files in `docs/adr/`:
  - `ADR-0078`: `ADR-0078-phase1-implementation-note.md` and `ADR-0078-composer-graph-atom-equivalence.md`
  - `ADR-0120`: `ADR-0120-expert-promotion-contract.md`, `ADR-0120-math-expert-ledger-flip.md`, and `ADR-0120-math-expert-promotion-wireup.md`
  - `ADR-0122`: `ADR-0122-parser-rate-per-unit.md` and `ADR-0122-systems-software-audit-passed-deferred.md`
  - `ADR-0123`: `ADR-0123-parser-comparison-phrasing.md` and `ADR-0123-symbolic-logic-shape-remap.md` (in addition to `ADR-0123a-inference-shape-synonym.md`)
  - `ADR-0127`: `ADR-0127-0128-RESULTS.md` and `ADR-0127-units-pack-and-units-aware-parser.md`
  - `ADR-0136.S3`: `ADR-0136.S3-compound-initial-mutation.md` and `ADR-0136.S3-post-rescan.md`
  - `ADR-0140`: `ADR-0140-core-trace-protocol-v0.md` and `ADR-0140-subtract-and-additive-group-closure.md`
  - `ADR-0163`: `ADR-0163-F2-confuser-corpus-spec.md` and `ADR-0163-gsm8k-path-to-mastery.md`
  - `ADR-0178`: `ADR-0178-GB3b-referent-accumulation-scope.md` and `ADR-0178-compositional-structure.md`
  - `ADR-0184`: `ADR-0184-distinct-unit-product-rule.md` and `ADR-0184-scoped-semantic-state-transitions.md`
  - `ADR-0225`: `ADR-0225-adr-corpus-hygiene.md` and `ADR-0225-contract-residual-read-model.md`
  - `ADR-0226`: `ADR-0226-gsm8k-math-eval-corpus.md`, `ADR-0226-ratification.md`, and `ADR-0226-residual-gated-practice-loop-v1.md`
- **Stated reason:** Historical concurrent agent workstreams authored decisions with colliding sequence numbers without synchronizing a centralized registry.
- **Implementation sites and consumers:** Files located in `docs/adr/`; referenced across `docs/adr-audit/01-adr-census.md`, `docs/adr/INDEX-by-domain.md`, and `docs/adr/README.md`.
- **Evidence and its scope:** Mechanically confirmed via filesystem walk of `docs/adr/ADR-*.md` in commit `069ceb55c55e066f4773ef186ba54e410164743a`.
- **Classification:** Defect (Governance & Document Hygiene).
- **Architectural consequence:** Citations to these ADR numbers in code, commit messages, and other ADRs are ambiguous unless qualified by full filename.
- **Proposed disposition:** Disambiguate in `docs/reconciliation/source-index.csv` using audit suffixes (`~1`, `~2`, `~3`); do not rename files during this assessment phase. Defer any renames to a dedicated, owner-approved governance pass under ADR-0225 rules.
- **Verification status:** Confirmed directly on disk.
- **Unresolved questions:** Which specific colliding files represent accepted vs proposed decisions in production practice?

---

### FIND-0002: Incomplete and Divergent ADR Indexes

- **Original obligation:** Documentation indexes must accurately reflect the contents of the repository.
- **Subsequent change:** `docs/adr/README.md` is a 28-line stub that addresses only the Master Blueprint ADR-0240–0253 collision and does not index the 314 ADRs. `docs/adr/INDEX-by-domain.md` states "312 files" while 314 ADR files exist on disk.
- **Stated reason:** Rapid addition of ADRs in late July 2026 without running an index verification ratchet.
- **Implementation sites and consumers:** `docs/adr/README.md`, `docs/adr/INDEX-by-domain.md`.
- **Evidence and its scope:** Direct inspection of file counts and contents in `docs/adr/` at commit `069ceb55c55e066f4773ef186ba54e410164743a`.
- **Classification:** Defect (Documentation Freshness & Discoverability).
- **Architectural consequence:** New contributors and agents cannot rely on the top-level ADR index to discover active decisions.
- **Proposed disposition:** Establish `docs/reconciliation/source-index.csv` as the unified source inventory for this assessment; queue an index synchronization pass for owner review.
- **Verification status:** Confirmed directly on disk.
- **Unresolved questions:** None.

---

### FIND-0003: Multi-Repository Lineage Conflation and Successor Narrative Drift

- **Original obligation:** `ACB-CORE-Labs/core` is the primary, authoritative repository for the Cl(4,1) Versor Engine (ratified in `docs/sessions/2026-05-13.md`: "`core` is the primary work. `core-ai` is the archive").
- **Subsequent change:** External documentation in sibling repositories (e.g., `core-iii/docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`) characterized `core` as an "assembly failure" and declared `core-iii` as a native C++23 rewrite. Simultaneously, `coreai` was operated as an offshoot repository for distillation and ablation experiments, leading to narrative confusion where historical `core-ai` (pre-May-2026 Cl(3,0) code) and `coreai` (post-July-2026 distillation) were conflated in discussions.
- **Stated reason:** Lack of explicit cross-repository governance boundaries during parallel exploratory work.
- **Implementation sites and consumers:** `docs/sessions/2026-05-13.md`, `docs/reconciliation/00-SCOPE.md`, `acbcore-labs/core-iii/docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `ACB-CORE-Labs/coreai`.
- **Evidence and its scope:** Direct comparison of commit histories, `4ca2431e` ("port Whitepaper.md and Yellowpaper.md from core-ai"), `docs/sessions/2026-05-13.md`, and `core-iii` documentation.
- **Classification:** Divergence (Architectural Governance & Scope Boundaries).
- **Architectural consequence:** Premature abandonment of `core`'s working Cl(4,1) Python substrate and 800+ test suites in favor of an unauthorized and unverified C++23 rewrite.
- **Proposed disposition:** Formally bound the repository roles in `docs/reconciliation/00-SCOPE.md`: `ACB-CORE-Labs/core` is the sole system under restoration; `coreai` is external evidence; historical `core-ai` is an archive; `core-iii` is reference material only. No language migration is authorized.
- **Verification status:** Confirmed directly from git metadata and repository documents.
- **Unresolved questions:** Where is the definitive upstream remote location and complete git history for historical `core-ai`?

---

### FIND-0004: Host Python Toolchain Discrepancy with `pyproject.toml`

- **Original obligation:** High-fidelity determinism requires an exact Python version pin (`requires-python = "==3.12.13"`).
- **Subsequent change:** `pyproject.toml` relaxed the requirement to `requires-python = ">=3.12,<3.13"`. The current developer host environment has system default `Python 3.9.6`, Homebrew `cpython-3.12.15`, and no active `.venv` directory in the repository root.
- **Stated reason:** Relaxation was introduced on 2026-07-25 because the exact patch pin made local gates unrunnable on platforms where `3.12.13` was not pre-published.
- **Implementation sites and consumers:** `pyproject.toml`, `scripts/ci/local-ci.sh`, `Makefile`.
- **Evidence and its scope:** `uv python list`, `python3 --version`, `pyproject.toml` lines 5–16, `ls -la .venv` (returned non-zero).
- **Classification:** Observation / Environmental Constraint (Toolchain Reproducibility).
- **Architectural consequence:** Shell commands executed with bare `python3` invoke Python 3.9.6 and fail syntax/typing checks. Any authorized test execution in future phases must use `uv run` and explicitly record whether it ran in canonical (3.12.13) or non-canonical fallback (3.12.15) mode per `scripts/ci/local-ci.sh`.
- **Proposed disposition:** Document in setup record; do not install or mutate virtual environments during this read-only assessment phase.
- **Verification status:** Confirmed directly in host environment.
- **Unresolved questions:** Does Python 3.12.15 reproduce the exact hash-pinned test outputs established under 3.12.13?

---

### FIND-0005: Unverified External Subagent Assertions in Prior Audit Register (`AA-331`–`AA-438`)

- **Original obligation:** All findings and claims in repository registers must be verified against real code and producible artifacts (`AGENTS.md` Standing Philosophy #5: "Prefer a record that contradicts nothing to a record that impresses").
- **Subsequent change:** Prior automated audit passes in late July 2026 introduced 108 findings (`AA-331` through `AA-438` in `docs/adr-audit/20-finding-register.md`) that asserted the existence of artifacts that do not exist (e.g. `core/evals/holdout_runner.py`, `core/capability/expert_contract.py`, `core/capability/ledger.py`).
- **Stated reason:** External unconstrained agent execution during batch processing without human review or verification checks.
- **Implementation sites and consumers:** `docs/adr-audit/20-finding-register.md` lines 13–35.
- **Evidence and its scope:** The formal retraction notice in `docs/adr-audit/20-finding-register.md` and direct filesystem check showing `core/evals/` does not exist on disk (the real path is `evals/holdout_runner.py`).
- **Classification:** Predecessor Defect / Precedent (Audit Integrity).
- **Architectural consequence:** Inherited audit registers cannot be taken as authoritative without direct re-verification against code.
- **Proposed disposition:** Strictly enforce Rule 5 of the Agent Brief: only record directly established findings; treat inherited historical findings as claims requiring independent verification.
- **Verification status:** Confirmed directly in `docs/adr-audit/20-finding-register.md`.
- **Unresolved questions:** How many findings in Batches 1–2 of `docs/adr-audit/20-finding-register.md` remain unverified against live code?

---

## 3. Historical Claims Register (Indexed for Future Verification)

The following claims are inherited from historical audit documents and are indexed here strictly as **claims requiring verification**, not verified findings:

| Claim ID | Historical Source | Claimed Assertion | Status | Verification Plan |
|---|---|---|---|---|
| `CLAIM-HIST-001` | `docs/adr-audit/20-finding-register.md` (`AA-1`) | `VocabManifold.nearest()` returns single word on production mount; 350/353 stored surfaces fail identity recall. | UNVERIFIED CLAIM | Trace `algebra/cga.py` and `generate/articulation.py` in Phase 2. |
| `CLAIM-HIST-002` | `docs/adr-audit/20-finding-register.md` (`AA-2`) | Vocabulary stores unit versors, which are not null CGA points, conflicting with Whitepaper Invariant II. | UNVERIFIED CLAIM | Inspect `VocabManifold.add` and point embedding math in Phase 2. |
| `CLAIM-HIST-003` | `docs/adr-audit/20-finding-register.md` (`AA-4`) | `_MANIFOLD_RESIDUAL_TOLERANCE` is `1e-5`, ten times looser than `<1e-6` in Whitepaper Invariant I. | UNVERIFIED CLAIM | Verify constant in `algebra/versor.py` and call sites. |
| `CLAIM-HIST-004` | `coreai` PR #291 (`LOGOS-ABLATION-1`) | Geometric algebra operations fail to perform semantic determination on WA1 possession-polar vertical. | UNVERIFIED CLAIM | Review PR #291 diff and experimental test results in Phase 3. |
| `CLAIM-HIST-005` | `core-iii/docs/NON-INHERITANCE.md` §2.1 | Git blob `aa80bce25953c001de645bfd26b3bec3acf821ec` is missing in `coreai` git history. | UNVERIFIED CLAIM | Check whether this blob or related commit exists in `core` history. |
