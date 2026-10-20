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
1. **Direct Establishment Only:** Only findings directly verified on disk, in git history, or through validated toolchain execution during this assessment are recorded as confirmed findings.
2. **No Unsupported Causal Explanations:** Explanations of *why* an anomaly exists must come strictly from explicit source statements. Where no reason is recorded in the source, it is marked `Unstated in source`. Speculative attributions of developer intent or agent behavior are excluded.
3. **No Inherited Conflation:** Conclusions copied from earlier audit summaries (such as `docs/adr-audit/20-finding-register.md` or `docs/assessment/30-gap-register.md`) are not admitted as established facts; they are indexed as historical claims requiring independent verification.
4. **Preserve Full Source Status Text:** Status fields must record the complete, untruncated string as declared in document headers, including all conditional and amendatory clauses.
5. **No Parallel Ledgers:** This is the single canonical findings ledger for the restoration assessment.
6. **Defect Discovery ≠ Authorization to Repair:** Recording a defect here does not authorize modifying runtime code, tests, or historical documents.

---

## 2. Established Findings Register

### FIND-0001: ADR Numbering Collisions in `docs/adr/`

- **Original obligation:** Under `ADR-0225` ("ADR Corpus Hygiene"), every Architectural Decision Record must possess a unique top-level sequence number, and "repository history wins for IDs."
- **Subsequent change:** Across the 314 `ADR-*.md` files in `docs/adr/`, 12 distinct collision sets exist under explicit definitions:
  - **Category A: Base Number Collisions (True Unsuffixed Collisions):** Exactly 11 base numbers, comprising 24 files that share the exact same 4-digit integer prefix without a distinguishing letter or dot suffix:
    1. `ADR-0078` (2 files): `ADR-0078-composer-graph-atom-equivalence.md`, `ADR-0078-phase1-implementation-note.md`
    2. `ADR-0120` (3 files): `ADR-0120-expert-promotion-contract.md`, `ADR-0120-math-expert-ledger-flip.md`, `ADR-0120-math-expert-promotion-wireup.md`
    3. `ADR-0122` (2 files): `ADR-0122-parser-rate-per-unit.md`, `ADR-0122-systems-software-audit-passed-deferred.md`
    4. `ADR-0123` (2 files): `ADR-0123-parser-comparison-phrasing.md`, `ADR-0123-symbolic-logic-shape-remap.md` *(Note: `ADR-0123a` is a suffixed variant belonging to the phased family)*
    5. `ADR-0127` (2 files): `ADR-0127-0128-RESULTS.md`, `ADR-0127-units-pack-and-units-aware-parser.md`
    6. `ADR-0140` (2 files): `ADR-0140-core-trace-protocol-v0.md`, `ADR-0140-subtract-and-additive-group-closure.md`
    7. `ADR-0163` (2 files): `ADR-0163-F2-confuser-corpus-spec.md`, `ADR-0163-gsm8k-path-to-mastery.md`
    8. `ADR-0178` (2 files): `ADR-0178-GB3b-referent-accumulation-scope.md`, `ADR-0178-compositional-structure.md`
    9. `ADR-0184` (2 files): `ADR-0184-distinct-unit-product-rule.md`, `ADR-0184-scoped-semantic-state-transitions.md`
    10. `ADR-0225` (2 files): `ADR-0225-adr-corpus-hygiene.md`, `ADR-0225-contract-residual-read-model.md`
    11. `ADR-0226` (3 files): `ADR-0226-gsm8k-math-eval-corpus.md`, `ADR-0226-ratification.md`, `ADR-0226-residual-gated-practice-loop-v1.md`
  - **Category B: Phased Sub-suffix Collisions:** Exactly 1 collision within a phased sub-decision family:
    - `ADR-0136.S3` (2 files): `ADR-0136.S3-compound-initial-mutation.md` and `ADR-0136.S3-post-rescan.md`
  - **Category C: Phased Sub-Decision Families (Non-Colliding Sequential Chains):** 60 files across 11 base numbers (0073, 0114, 0118, 0119, 0121, 0123, 0124, 0131, 0136, 0148, 0160, 0174) that carry explicit letter or dot suffixes representing sequential multi-part decision chains.
- **Stated reason:** Unstated in source.
- **Implementation sites and consumers:** Files located in `docs/adr/`; referenced across `docs/adr-audit/01-adr-census.md`, `docs/adr/INDEX-by-domain.md`, and `docs/adr/README.md`.
- **Evidence and its scope:** Mechanically verified via filesystem walk of `docs/adr/ADR-*.md` in commit `069ceb55c55e066f4773ef186ba54e410164743a`.
- **Classification:** Defect (Governance & Document Hygiene).
- **Architectural consequence:** Citations to these ADR numbers in code, commit messages, and other ADRs are ambiguous unless qualified by full filename.
- **Proposed disposition:** Disambiguate in `docs/reconciliation/source-index.csv` using audit suffixes (`~1`, `~2`, `~3`); do not rename files during this assessment phase. Defer any renames to a dedicated, owner-approved governance pass under ADR-0225 rules.
- **Verification status:** Confirmed directly on disk.
- **Unresolved questions:** Which specific colliding files represent accepted vs proposed decisions in production practice?

---

### FIND-0002: Incomplete and Divergent ADR Indexes

- **Original obligation:** Documentation indexes must accurately reflect the contents of the repository.
- **Subsequent change:** `docs/adr/README.md` is a 28-line stub that discusses only the Master Blueprint ADR-0240–0253 collision mapping and does not index any of the 314 ADR files. `docs/adr/INDEX-by-domain.md` states "312 files" while 314 ADR files exist on disk.
- **Stated reason:** Unstated in source.
- **Implementation sites and consumers:** `docs/adr/README.md`, `docs/adr/INDEX-by-domain.md`.
- **Evidence and its scope:** Direct inspection of file counts and contents in `docs/adr/` at commit `069ceb55c55e066f4773ef186ba54e410164743a`.
- **Classification:** Defect (Documentation Freshness & Discoverability).
- **Architectural consequence:** Developers and agents relying on `docs/adr/README.md` or `INDEX-by-domain.md` receive incomplete or outdated decision rosters.
- **Proposed disposition:** Maintain [docs/reconciliation/source-index.csv](source-index.csv) as the bounded source inventory for this assessment; queue an index synchronization pass for owner review.
- **Verification status:** Confirmed directly on disk.
- **Unresolved questions:** None.

---

### FIND-0003: Multi-Repository Distinctions and Cross-Repository Narrative Drift

- **Original obligation:** In `docs/sessions/2026-05-13.md`, the primary repository boundary was ratified: "*`core` is the primary work. `core-ai` is the archive*."
- **Subsequent change:** Cross-repository documentary records reveal distinct repository roles alongside unverified narrative drift:
  - **Verified Repository Distinctions:**
    1. `ACB-CORE-Labs/core` is the primary, active Cl(4,1) implementation containing 314 ADRs and 800+ test files.
    2. Historical `core-ai` is an archived Cl(3,0) codebase from which foundational papers were ported in commit `4ca2431e`.
    3. `ACB-CORE-Labs/coreai` is a distinct remote and branch lineage containing DISTILL-1 PRs #289–#302 and empirical ablation records (`LOGOS-ABLATION-1`).
    4. `acbcore-labs/core-iii` is an exploratory C++23 workspace containing analytical drafts (`docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `NON-INHERITANCE.md`).
  - **Unverified Narrative Assertions (Separated Out):**
    1. External documentation in `core-iii` framed `core` as an "assembly failure" and declared `core-iii` as a native C++23 successor. This characterization is an unverified external narrative assertion, not an owner-ratified conclusion in `core`.
    2. Dialogue assuming that work on `core` was abandoned or that a C++23 rewrite is authorized lacks owner ratification in `ACB-CORE-Labs/core`.
- **Stated reason:** Unstated in source.
- **Implementation sites and consumers:** `docs/sessions/2026-05-13.md`, `docs/reconciliation/00-SCOPE.md`, `acbcore-labs/core-iii/docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `ACB-CORE-Labs/coreai`.
- **Evidence and its scope:** Direct comparison of commit histories, `4ca2431e` ("port Whitepaper.md and Yellowpaper.md from core-ai"), `docs/sessions/2026-05-13.md`, and `core-iii` documentation.
- **Classification:** Divergence (Architectural Governance & Scope Boundaries).
- **Architectural consequence:** Risk of conflating reference material with binding architecture.
- **Proposed disposition:** Formally enforce repository roles in `docs/reconciliation/00-SCOPE.md`: `ACB-CORE-Labs/core` is the sole system under restoration; external repositories provide comparison evidence and reference material only.
- **Verification status:** Confirmed directly from git metadata and repository documents.
- **Unresolved questions:** What is the definitive upstream remote location and complete git history for historical `core-ai`?

---

### FIND-0004: Python Toolchain Environment and Local-CI Contract

- **Original obligation:** `pyproject.toml` defines the project's supported Python versions, and `.python-version` pins the target interpreter version.
- **Subsequent change:** Inspection of configuration files and executable runner logic reveals:
  - `.python-version` explicitly specifies `3.12`.
  - `pyproject.toml` declares `requires-python = ">=3.12,<3.13"`.
  - `scripts/ci/local-ci.sh` lines 86–94 read `.python-version` dynamically:
    ```sh
    pinned="$(cat .python-version 2>/dev/null || echo '')"
    [ -n "${pinned}" ] || pinned="3.12.13"
    ```
    Because `.python-version` is `3.12`, the script queries `uv python find "3.12"`, which on this host resolves `/opt/homebrew/opt/python@3.12/bin/python3.12` and declares:
    `[local-ci] interpreter: 3.12 (CANONICAL — matches the repo pin)`.
  - The previous draft of FIND-0004 erroneously asserted an interpreter discrepancy based on historical commentary and fallback strings in `local-ci.sh` (`pinned="3.12.13"`) rather than testing the actual live files and executable logic.
  - **Host Environment Reality:** The macOS host's system default `/usr/bin/python3` is `3.9.6`, which cannot parse modern Python syntax. All command executions must use `uv run` to target Python 3.12.
  - A local virtual environment (`.venv`) is currently absent in the repository root.
- **Stated reason:** Stated in `pyproject.toml` lines 5–16: `requires-python` was relaxed from `"==3.12.13"` to `">=3.12,<3.13"` on 2026-07-25 because the exact patch pin made local gates unrunnable on platforms where `3.12.13` was not pre-published (e.g. linux-x86_64).
- **Implementation sites and consumers:** `.python-version`, `pyproject.toml`, `scripts/ci/local-ci.sh`.
- **Evidence and its scope:** Direct execution of `cat .python-version`, `uv python find "3.12"`, `sh scripts/ci/local-ci.sh --list`, and inspection of `pyproject.toml`.
- **Classification:** Toolchain Environment & Contract Verification.
- **Architectural consequence:** Toolchain specification across `.python-version`, `pyproject.toml`, and `local-ci.sh` is aligned on `3.12`. Running commands with bare `python3` fails due to macOS system default (3.9.6); `uv run` must be used.
- **Proposed disposition:** Document toolchain alignment in setup records; preserve read-only state without installing a virtual environment during this phase.
- **Verification status:** Confirmed via live command execution.
- **Unresolved questions:** None.

---

### FIND-0005: Prior Retraction of Automated Audit Register (`AA-331`–`AA-438`)

- **Original obligation:** Under `AGENTS.md` Standing Philosophy #5 ("Prefer a record that contradicts nothing to a record that impresses"), all entries in finding registers must be grounded in real, verifiable code.
- **Subsequent change:** In `docs/adr-audit/20-finding-register.md` lines 13–35, findings `AA-331` through `AA-438` (representing Batches 3–6 of the prior ADR audit) carry a formal **RETRACTION NOTICE (2026-07-29)** declaring them void.
- **Stated reason:** Stated explicitly in `docs/adr-audit/20-finding-register.md`:
  1. Direct, verified contradiction with already-established evidence (`AA-250` [🔴] vs `AA-337` [🟢]).
  2. Downgrade of previously registered 🔴 `AA-75` to mild 🟡 `AA-332` without new evidence.
  3. Statistically implausible severity distribution (Batches 1–2 produced 32 🔴; Batches 3–6 produced only 3 🔴).
  4. Asserted existence of fabricated artifacts that do not exist on disk (`core/evals/holdout_runner.py`, `core/capability/expert_contract.py`, `core/capability/ledger.py`).
- **Implementation sites and consumers:** `docs/adr-audit/20-finding-register.md`.
- **Evidence and its scope:** Verified text in `docs/adr-audit/20-finding-register.md` and direct filesystem check confirming `core/evals/` does not exist on disk (the real path is top-level `evals/holdout_runner.py`).
- **Classification:** Precedent & Audit Integrity Record.
- **Architectural consequence:** Inherited finding registers cannot be accepted without re-verification; unverified claims must not be populated into the findings ledger.
- **Proposed disposition:** Enforce strict verification discipline: only record directly established findings; treat inherited historical findings as unverified claims requiring independent verification.
- **Verification status:** Confirmed directly from source text.
- **Unresolved questions:** How many findings in Batches 1–2 of `docs/adr-audit/20-finding-register.md` carry verified code citations vs unverified assertions?

---

## 3. Disputed Invariants & Historical Claims (Held as Review Questions)

The following claims are inherited from historical audit documents and external PRs. Per the owner's design evaluation frame, they are held as **Formal Review Questions** rather than substantive architectural verdicts:

| Question / Claim ID | Source Reference | Stated Historical Claim | Formal Review Question | Verification Plan |
|---|---|---|---|---|
| **`REV-Q-001`** (`AA-4`) | `docs/adr-audit/20-finding-register.md` | `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` is 10× looser than `< 1e-6` in Whitepaper Invariant I. | What is the mathematically and mechanically justified tolerance for Cl(4,1) multivector closure across IEEE 754 operations, and what is the exact empirical margin on live mounts? | Trace `algebra/versor.py` and inspect residual distribution on live states in Phase 2. |
| **`REV-Q-002`** (`AA-2`) | `docs/adr-audit/20-finding-register.md` | `VocabManifold.add()` stores unit versors ($V \widetilde{V} = 1$), rejecting conformal null points ($X \cdot X = 0$), conflicting with Whitepaper Invariants II & III. | What is the lawful algebraic relationship between conformal point representations and operator versors in the Logos vocabulary manifold? | Review `algebra/cga.py` point embedding formulas against `VocabManifold.add()` in Phase 2. |
| **`REV-Q-003`** (`AA-1`) | `docs/adr-audit/20-finding-register.md` | `VocabManifold.nearest()` returns single word on production mount; 350/353 stored surfaces fail identity recall. | Does standard conformal inner product support relational lookup, or is nearest-neighbor search an inherited abstraction that conflicts with Cl(4,1) rotor geometry? | Trace `generate/articulation.py` and evaluate retrieval behavior in Phase 2. |
| **`REV-Q-004`** | `coreai` PR #291 (`LOGOS-ABLATION-1`) | Geometric algebra operations fail to perform semantic determination on WA1 possession-polar vertical (verdict FAIL). | What is the precise boundary between exact geometric custody and semantic determination across CORE's cognitive pipeline? | Examine PR #291 diff, test data, and ablation scripts in Phase 3. |
| **`REV-Q-005`** | `core-iii/docs/NON-INHERITANCE.md` §2.1 | Git blob `aa80bce` is missing from `coreai` repository history. | Does blob `aa80bce` or its referenced commit exist in `core`'s git object database, and does it affect any live provenance seals? | Search `core` git object database via `git cat-file -e aa80bce` in Phase 3. |
