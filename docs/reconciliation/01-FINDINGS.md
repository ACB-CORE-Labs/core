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
5. **Single Canonical Ledger and Question Register:** This is the single canonical findings ledger and question register for the restoration assessment. Parallel agent-specific ledgers or question lists are prohibited.
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
  - **Category C: Phased Sub-Decision Families (Sequential Chains):** 60 files across 11 base numbers in historical census indexing (`docs/adr-audit/01-adr-census.md` §2: `0073` [5 files: 1 base + 4 variants], `0114` [7 files: 1 base + 6 variants], `0118` [2 files: 1 base + 1 variant], `0119` [9 files: 1 base + 8 variants], `0131` [16 files: 1 base + 15 variants], `0136` [7 files: 1 base + 6 variants], `0164` [5 files: 1 base + 4 variants], `0168` [2 files: 1 base + 1 variant], `0169` [2 files: 1 base + 1 variant], `0189` [2 files: 1 base + 1 variant], `0201` [2 files: 1 base + 1 variant]; total: 11 base files + 48 unique variants + 1 collision in 0136.S3 = 60 files). On disk, base `0123` also carries a suffixed variant (`ADR-0123a-inference-shape-synonym.md`), yielding 49 suffixed variant files across 12 base numbers. All 314 ADR files are tracked in `source-index.csv` with unique source IDs.
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
- **Proposed disposition:** Maintain [`docs/reconciliation/source-index.csv`](source-index.csv) as the bounded source inventory for this assessment; queue an index synchronization pass for owner review.
- **Verification status:** Confirmed directly on disk.
- **Unresolved questions:** None.

---

### FIND-0003: Multi-Repository Distinctions and Current Assessment Boundary

- **Original obligation:** In `docs/sessions/2026-05-13.md`, the primary repository boundary was ratified: "*`core` is the primary work. `core-ai` is the archive*."
- **Subsequent change:** Cross-repository documentary records reveal distinct repository roles alongside external narrative drift:
  - **Verified Repository Distinctions:**
    1. `ACB-CORE-Labs/core` is the primary, active Cl(4,1) implementation containing 314 ADRs and 800+ test files.
    2. Historical `core-ai` is an archived Cl(3,0) codebase from which foundational papers were ported in commit `4ca2431e`.
    3. `ACB-CORE-Labs/coreai` is a distinct remote and branch lineage containing DISTILL-1 PRs #289–#302 and empirical ablation records (`LOGOS-ABLATION-1`).
    4. `acbcore-labs/core-iii` is an exploratory C++23 workspace containing analytical drafts (`docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `NON-INHERITANCE.md`).
  - **Narrative Assertions vs. Current Assessment Boundary:**
    1. External documentation in `core-iii` framed `core` as an "assembly failure" and declared `core-iii` as a native C++23 successor architecture. Under the current assessment boundary, `ACB-CORE-Labs/core` is the sole system under restoration assessment; `core-iii` provides reference preparation material only and does not bind architecture.
    2. Historical authorization of past directions or rewrites is not adjudicated here; the present assessment authorizes no migration. A scope boundary defines the operational mandate of this assignment, not a historical finding on past intent. Under this mandate, **no C++23 migration is authorized by this assessment**, and the existing implementation of `core` is preserved while we understand it.
- **Stated reason:** Unstated in source.
- **Implementation sites and consumers:** `docs/sessions/2026-05-13.md`, `docs/reconciliation/00-SCOPE.md`, `acbcore-labs/core-iii/docs/00-MASTER-DISTILLATION-AND-ARCHITECTURE.md`, `ACB-CORE-Labs/coreai`.
- **Evidence and its scope:** Direct comparison of commit histories, `4ca2431e` ("port Whitepaper.md and Yellowpaper.md from core-ai"), `docs/sessions/2026-05-13.md`, and `core-iii` documentation.
- **Classification:** Architectural Governance & Boundary Definition.
- **Architectural consequence:** Risk of conflating reference material with binding architecture.
- **Proposed disposition:** Formally enforce current assessment boundaries in `docs/reconciliation/00-SCOPE.md`: `ACB-CORE-Labs/core` is the sole system under restoration assessment; external repositories provide comparison evidence and reference material only. No language migration or replacement baseline is authorized.
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
  - **Host Environment Reality:** The macOS host's system default `/usr/bin/python3` is `3.9.6`, which cannot parse modern Python syntax. Execution of repository validation or runner logic requires an explicit suitable Python 3.12 interpreter (e.g. matching `pyproject.toml` and `.python-version`), without authorizing environment provisioning, virtual environment creation, or dependency installation during this assessment.
  - A local virtual environment (`.venv`) is currently absent in the repository root.
- **Stated reason:** Stated in `pyproject.toml` lines 5–16: `requires-python` was relaxed from `"==3.12.13"` to `">=3.12,<3.13"` on 2026-07-25 because the exact patch pin made local gates unrunnable on platforms where `3.12.13` was not pre-published (e.g. linux-x86_64).
- **Implementation sites and consumers:** `.python-version`, `pyproject.toml`, `scripts/ci/local-ci.sh`.
- **Evidence and its scope:** Direct inspection of `.python-version` (specifies `3.12`), `pyproject.toml` (declares `requires-python = ">=3.12,<3.13"`), and `scripts/ci/local-ci.sh` (lines 86–94 dynamic reading logic); verified live interpreter resolution via `uv python find "3.12"`.
- **Classification:** Toolchain Environment & Contract Verification.
- **Architectural consequence:** Toolchain specification across `.python-version`, `pyproject.toml`, and `local-ci.sh` is aligned on `3.12`. Invoking commands with the macOS system default `/usr/bin/python3` (3.9.6) fails; execution requires an explicit suitable Python 3.12 interpreter matching project requirements, while preserving the no-install boundary during this assessment.
- **Proposed disposition:** Document toolchain alignment in setup records; preserve read-only state without installing a virtual environment during this phase.
- **Verification status:** Confirmed via static file inspection and interpreter resolution.
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

### FIND-0006: Component Entrypoint Path Substitutions and Subsystem Mapping Uncertainty

- **Original obligation:** The source inventory must index the primary component entrypoints of the system at their verified paths in `ACB-CORE-Labs/core` at the agreed reference revision (`069ceb55`).
- **Subsequent change:** In the initial inventory draft, five component entrypoints were recorded using conceptual paths that do not exist on disk at `069ceb55`. These paths were corrected in the inventory via the following explicit mappings:
  1. `SRC-COMP-CORE-RUNTIME`: Draft path `core/runtime.py` $\longrightarrow$ Mapped to `chat/runtime.py`.
     - *Evidence:* `chat/runtime.py` defines `class ChatRuntime` (line 599), which orchestrates conversational turn execution, pack grounding, and session lifecycle.
     - *Uncertainty:* Whether `chat/runtime.py` represents the complete cognitive runtime or only the chat-specific interaction envelope, while core cognitive cycle orchestration resides in `core/cognition/pipeline.py` and `core/physics/cognitive_lifecycle.py`.
  2. `SRC-COMP-CORE-PIPELINE`: Draft path `core/pipeline.py` $\longrightarrow$ Mapped to `core/cognition/pipeline.py`.
     - *Evidence:* `core/cognition/pipeline.py` defines `class CognitiveTurnPipeline` (line 115), implementing the live cognition pipeline from input tokens to PropositionGraph and ArticulationTarget.
     - *Uncertainty:* The exact runtime coupling between `CognitiveTurnPipeline`, `chat/runtime.py`, and `session/context.py` remains under assessment.
  3. `SRC-COMP-CORE-FAIL-CLOSED`: Draft path `core/fail_closed.py` $\longrightarrow$ Mapped to `core/cognition/fail_closed.py`.
     - *Evidence:* `core/cognition/fail_closed.py` defines typed failure contracts, `ContractAssessment`, and fail-closed violation handlers enforcing invariant `INV-34` as documented in `AGENTS.md`.
     - *Uncertainty:* Whether fail-closed enforcement is active across all gates or gated behind dormant flags (e.g. `identity_wave_gate`).
  4. `SRC-COMP-SENSORIUM-MULTIMODAL`: Draft path `sensorium/multimodal.py` $\longrightarrow$ Mapped to `sensorium/protocol.py`.
     - *Evidence:* `sensorium/protocol.py` defines the core protocol boundary declarations cited by ADR-0013, including `ProjectionHead` (line 50), `SurfaceDecoder` (line 68), `ModalityVocabulary` (line 136), and `ModalityPack` (line 184).
     - *Uncertainty:* `sensorium/protocol.py` defines protocol interfaces and container data structures rather than concrete sensory encoders or compilers (which reside in subpackages such as `sensorium/vision/`, `sensorium/audio/`, and `sensorium/sensorimotor/`). The question of which concrete implementations fulfill the intended sensorium mission across modalities remains an open question for substantive review; mapping this path to `protocol.py` establishes the protocol entrypoint but does not imply that the full multimodal subsystem is integrated or complete.
  5. `SRC-COMP-TEACHING-LOOP`: Draft path `teaching/loop.py` $\longrightarrow$ Mapped to `teaching/review.py`.
     - *Evidence:* `teaching/review.py` implements the reviewed teaching review gate (`validate_admissible`, deterministic SHA-256 review hashing, identity override rejection) enforcing `AGENTS.md` durable mutation contracts.
     - *Uncertainty:* The teaching subsystem is distributed across `teaching/review.py`, `teaching/queue.py`, and `teaching/ratification.py`; `review.py` represents the review boundary but does not execute autonomous loop cycling.
- **Stated reason:** Conceptual naming in early scoping notes without prior verification of directory structures.
- **Implementation sites and consumers:** `docs/reconciliation/source-index.csv`, `chat/runtime.py`, `core/cognition/pipeline.py`, `core/cognition/fail_closed.py`, `sensorium/protocol.py`, `teaching/review.py`.
- **Evidence and its scope:** Verified module definitions, class declarations, and import sites at commit `069ceb55`.
- **Classification:** Inventory Verification & Module Mapping.
- **Architectural consequence:** Prevents inventory breakage and missing-file failures while documenting the exact functional boundaries and architectural uncertainties of these entrypoints.
- **Proposed disposition:** Retain the verified paths in `docs/reconciliation/source-index.csv`, annotate each row with the substitution mapping, evidence, and uncertainty, and audit the full subsystem boundaries in Phase 2 substantive review.
- **Verification status:** Confirmed via static file inspection and class definitions at commit `069ceb55`.
- **Unresolved questions:** Are there alternative entrypoints that more directly represent the intended subsystem roots?

---

### FIND-0007: Contradiction Between Conformal Point Embedding (Null Vectors) and VocabManifold Insertion Invariant (Unit Versors)

- **Original obligation:**
  - `docs/Whitepaper.md` §V (Invariants II & III) and `docs/Yellowpaper.md` §I.1, §III, and §V specify:
    1. Euclidean point $p = (x, y, z)$ embeds as a null vector on the conformal horosphere: $P = p + \frac{1}{2}|p|^2 \infty + o$, satisfying $P \cdot P = 0$.
    2. Vocabulary manifold elements are stored as null vectors ($v_w \cdot v_w = 0$).
    3. The CGA inner product between null vectors yields exact conformal distance: $X \cdot Y = -\frac{1}{2} d(X, Y)^2$.
    4. Token projection selects $\arg\max_w (F_{\text{current}} \cdot v_w)$, minimizing CGA distance to the field state.
- **Subsequent change:**
  - `docs/adr/ADR-0001-vocab-layer-invariants.md` and `vocab/manifold.py` enforce:
    1. All vocabulary entries must be unit versors. ADR-0001 originally enforced a scalar-only check on the signed scalar part: $\langle V \widetilde{V} \rangle_0 \approx \pm 1$ (specified as `float(geometric_product(v, reverse(v))[0])` between 0.95 and 1.05). In contrast, the implemented `vocab/manifold.py::add()` and `update()` enforce the full multivector unit residual $\|V \widetilde{V} \mp 1\|_F \le 10^{-5}$ (`_MANIFOLD_RESIDUAL_TOLERANCE`), rejecting non-scalar residue as well as scalar deviation.
    2. Any vector failing this check raises `ValueError`.
  - **Mathematical Reality:**
    1. In Clifford algebra $\text{Cl}(4,1)$, for any grade-1 vector $X$, the reverse is $\widetilde{X} = X$.
    2. Therefore, $X \widetilde{X} = X^2 = X \cdot X + X \wedge X = X \cdot X$.
    3. For a null vector $X$, $X \cdot X = 0$, which implies $X \widetilde{X} = 0$.
    4. The unit versor residual is $\|0 \mp 1\| = 1.0 \gg 10^{-5}$ (under both positive and negative unit branches).
    5. Consequently, any genuine conformal null vector produced by `algebra/cga.py::embed_point(x)` is strictly rejected by `VocabManifold.add()`.
  - Yet `VocabManifold.nearest(F)` continues to state in its docstring:
    `cga_inner(X, Y) = -d^2 / 2 for null vectors: maximizing = minimizing distance.`
    while calculating `cga_inner` against stored unit versors ($V \widetilde{V} \approx \pm 1$), not null vectors.
- **Stated reason:** ADR-0001 states the grade-norm condition was introduced to prevent callers from inserting raw Euclidean coordinate arrays or external embeddings ("back door problem") without lifting through the algebra. The algebraic conflict between a null point ($X^2 = 0$) and a unit versor ($V \widetilde{V} = 1$) is unstated in source.
- **Implementation sites and consumers:** `vocab/manifold.py` (lines 40–66, 110–112), `algebra/cga.py` (lines 11–15, 69–76, 99–120), `docs/Whitepaper.md` §V, `docs/Yellowpaper.md` §V, `docs/adr/ADR-0001-vocab-layer-invariants.md`.
- **Evidence and its scope:** Algebraic and source-inspection evidence (deductive derivation from $\text{Cl}(4,1)$ grade-1 null vector definitions and static code inspection of `_assert_manifold_versor` in `vocab/manifold.py`), not reproduced runtime execution.
- **Classification:** Formal Contradiction (Algebraic Specification vs. Runtime Invariant).
- **Architectural consequence:** Vocabulary elements cannot simultaneously satisfy the Whitepaper null-cone invariant and the ADR-0001 manifold versor invariant. If vocabulary elements are unit versors, `cga_inner(F, v_w)` does not compute $-\frac{1}{2} d(F, v_w)^2$ in the Euclidean metric sense, but rather the scalar part of the geometric product between field and vocabulary operators.
- **Proposed disposition:** Record in Canonical Question Register as formal verification of `REV-Q-002`. Preserve both implementations during assessment for Phase 2 mathematical reconciliation without altering runtime code.
- **Verification status:** Confirmed directly from source text and algebra implementations.
- **Unresolved questions:** Was the vocabulary intended to store conformal points (geometric targets) or transformation versors (operators on the Spin manifold), or does a dual mapping exist that was left unrecorded?

---

### FIND-0008: Deletion and Divergence of ADR-0011 Renderer Contract (`generate/render.py` Absent on Disk)

- **Original obligation:** ADR-0011 ("Renderer Layer Contract", 2026-05-13) established a thin renderer interface: `class Renderer(Protocol)` with `def render(self, tokens: Iterable[VocabEntry]) -> str | bytes`. It declared that the default implementation would be `generate/render.py` (`TextRenderer`), joining tokens by language-appropriate separators.
- **Subsequent change:**
  - `generate/render.py` was created in commit `0fbc2e92`.
  - The audit record is dated May 24, 2026; removal of `generate/render.py` was committed in `050b2f92` on May 25, 2026 UTC. The recorded rationale was dormancy: zero live production imports, test imports, and references.
  - `docs/adr/ADR-0011-renderer.md` was never amended or marked superseded; it remains on disk at `069ceb55` declaring `Status: Accepted` and describing `generate/render.py` as active.
  - Other modules producing surface strings exist in the tree (`generate/realizer.py`, `core/cognition/surface_resolution.py`). No explicit replacement or supersession decision was identified in the sources reviewed for this unit. Whether one exists elsewhere in the ADR, session, or commit history remains unresolved.
- **Stated reason:** Explicitly stated in commit `050b2f92` and `docs/audit/substrate-liveness-registry.md` L5 audit: `generate/render.py` was deleted as dormant cleanup.
- **Implementation sites and consumers:** `docs/adr/ADR-0011-renderer.md`, `generate/render.py` (deleted), `docs/audit/substrate-liveness-registry.md`, `generate/realizer.py`, `core/cognition/surface_resolution.py`.
- **Evidence and its scope:** Git log history of `generate/render.py` (`0fbc2e92` creation, `050b2f92` deletion) and direct filesystem verification confirming `generate/render.py` does not exist on disk at `069ceb55` or HEAD.
- **Classification:** Divergence (Documented Decision vs. Working Tree Reality).
- **Architectural consequence:** ADR-0011 misrepresents the current repository contents. Readers consulting ADR-0011 search for a nonexistent `generate/render.py`. Whether surface realization in `realizer.py` or `surface_resolution.py` fulfills or alters ADR-0011's architectural role remains unestablished in this review.
- **Proposed disposition:** Document the historical deletion; present proposed documentation amendment to ADR-0011 for owner review during a future governance pass without asserting equivalent replacement.
- **Verification status:** Confirmed directly from git commit history and disk inspection.
- **Unresolved questions:** Was the renderer obligation superseded, relocated, left as an external caller responsibility, or removed without a corresponding design update?

---

### FIND-0009: Separation of Algebraic Operator Ownership (ADR-0004) and Metadata Stores in `VocabManifold`

- **Original obligation:** ADR-0004 ("Rotor as Operator, Not Vocabulary Property", 2026-05-12) mandated:
  1. Remove `edge_rotor()` from `VocabManifold`.
  2. Relocate transition operator construction to free functions in `algebra/rotor.py` (`word_transition_rotor(A, B)`).
  3. `VocabManifold` contract is strictly: store word-versor pairs, support relational lookup by CGA inner product, and construct no operators or transformations.
- **Subsequent change:**
  - The separation of operator construction into `algebra/rotor.py` was maintained: `VocabManifold` contains zero methods constructing rotors or versor products.
  - In addition to word-versor storage, `VocabManifold` maintains dictionary mappings for associated metadata:
    - `_morphology_by_word`: `dict[str, MorphologyEntry]`
    - `_language_by_word`: `dict[str, str]`
    - `_energy_by_word`: `dict[str, EnergyProfile]` (ADR-0006)
    - `_valence_by_word`: `dict[str, ValenceBundle]` (ADR-0007)
    - `_epistemic_state_by_word`: `dict[str, str]` (ADR-0142)
    - `_transient_words`: `set[str]`
    - `_unknown_token_log`: `list[dict[str, object]]`
- **Stated reason:** ADR-0004 states operators belong in `algebra/` because they describe transformations applied in the field, not properties of the vocabulary. Subsequent ADRs (ADR-0006, ADR-0007, ADR-0142) attached linguistic, energetic, and epistemic metadata to lexical entries.
- **Implementation sites and consumers:** `vocab/manifold.py` (lines 68–79, 114–127, 223–259), `algebra/rotor.py` (lines 285–317), `docs/adr/ADR-0004-rotor-as-operator-not-property.md`.
- **Evidence and its scope:** Direct inspection of `vocab/manifold.py` and `algebra/rotor.py`.
- **Classification:** Architectural Preservation with Layer Observation.
- **Architectural consequence:** The structural boundary of ADR-0004 (no operator synthesis in `VocabManifold`) holds in code. `VocabManifold` holds linguistic, physical, and epistemic metadata mappings alongside its versor arrays.
- **Proposed disposition:** Acknowledge that ADR-0004's operator boundary is preserved; note metadata mappings for Phase 2 language pack review.
- **Verification status:** Confirmed directly from source code.
- **Unresolved questions:** None.

---

### FIND-0010: Recorded Amendment of ADR-0005 Language Pack Alignment Gate

- **Original obligation:** ADR-0005 ("Language Pack Contract", 2026-05-12) defined an 8-gate activation sequence for language packs (`en`, `he`, `el`/`grc`):
  1. Schema gate
  2. Lexical gate
  3. Morphology gate
  4. Lift gate
  5. Readback gate
  6. Determinism gate
  7. Alignment gate (publishes anchor records verifiable against trilingual template)
  8. Coverage gate
- **Subsequent change:**
  - An explicit amendment dated 2026-07-28 is recorded directly in `docs/adr/ADR-0005-language-pack-contract.md` lines 94–111.
  - **Recorded Historical Measurements (Documented in Source, Not Independently Reproduced Here):**
    1. Measured at commit `472fc0a8`, the alignment mechanism behind Gate 7 was reported to destroy what it claimed to align: `packs.compiler._blend_feature_versors` ignored its strength argument and returned the target verbatim, overwriting Hebrew tokens with Greek/English coordinates and deleting 37 distinct coordinates (`docs/analysis/logos-substrate-collapse-2026-07-28.md`).
    2. The eight gates were not implemented as an executable sequence in the loader; `gate_engaged` was recorded as a single boolean flag in pack manifests.
    3. Gate 7's stronger theoretical premise—that alignment resonance validates semantic truth (ADR-0015 Crown Proof)—was reported as measured and refused (`docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`).
    4. The amendment affirmed that alignment must be interpolation on the versor group (`algebra/rotor.py::rotor_power`), never replacement, and that cross-language anchor data stands without asserting that alignment proves semantic resonance.
- **Stated reason:** Explicitly stated in the 2026-07-28 amendment to ADR-0005 and cited analysis documents.
- **Implementation sites and consumers:** `docs/adr/ADR-0005-language-pack-contract.md`, `packs/compiler.py`, `docs/analysis/logos-substrate-collapse-2026-07-28.md`, `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`.
- **Evidence and its scope:** Source-referenced summary of the amendment in `docs/adr/ADR-0005-language-pack-contract.md` and its cited analysis documents. The historical measurements have not been independently reproduced in this assessment.
- **Classification:** Historical Defect & Documented Empirical Amendment.
- **Architectural consequence:** The Language Pack Contract cannot be assumed to function as originally written in May 2026; the 2026-07-28 amendment documents structural failure of naive alignment blending and the lack of an active 8-gate runner.
- **Proposed disposition:** Maintain the historical amendment as documented evidence; evaluate current `packs/compiler.py` implementation in Phase 2 against the versor interpolation requirement.
- **Verification status:** Confirmed directly from ADR-0005 source text.
- **Unresolved questions:** Has `packs.compiler._blend_feature_versors` been updated to use geodesic versor interpolation (`rotor_power`), or does coordinate overwrite persist in any loader paths?

---

### FIND-0011: Documented Runtime/Durable Ingestion Split and Unresolved Relationship to the Broader Pre-Gate Design

- **Original obligation:** Whitepaper §VIII and ADR-0012 ("`core_ingest` Governance Layer", 2026-05-13) establish `core_ingest/` as the pre-gate governance boundary wrapping *upstream* of `ingest/gate.py`. Every piece of incoming information is intended to be lifted into an immutable `CandidateGeometricPressure` envelope, categorized by `DeterminismClass` (D0–D4), validated through the three-gate sequence (`ProvenanceGate` → `SemanticGate` → `GovernanceGate`), and indexed in `SegmentManifold` before entering the field.
- **Observed reality in code:**
  The codebase explicitly defines two distinct ingestion pathways, documented in `core_ingest/__init__.py:9-16`:
  1. **Runtime path:** Transient working pressure for active cognition (`short-circuit: bypasses governance, feeds ingest/gate.py directly`). In the interactive execution paths (`core/cognition/pipeline.py:1011` and `chat/runtime.py:112`), input text is tokenized via regular expression `\w+` and passed directly to `ingest/gate.py::inject(token_list, vocab)`. This route does not construct `CandidateGeometricPressure`, apply `StructuralSegmenter` D0 carving, run the three gates, or index in `SegmentManifold`.
  2. **Durable path:** Validated candidate pressure for learning and update paths (`full three-gate IngestCompiler pipeline`). This route is implemented in `core_ingest/` (`pipeline.py`, `compiler.py`, `manifold.py`), executed via `core/cli_ingest.py` (`core ingest <file>`), and verified by dedicated tests (`tests/test_core_ingest.py`, `tests/test_compiler.py`).
  3. Furthermore, `core_ingest/__init__.py:15-16` explicitly states: *"The gate (ingest/gate.py) is NEVER imported or modified from this package. This package is upstream of the gate, not a replacement for it."*
- **Implementation sites and consumers:** `core_ingest/` (`__init__.py`, `pipeline.py`, `compiler.py`, `types.py`), `core/cli_ingest.py`, `ingest/gate.py:408-429`, `core/cognition/pipeline.py:1000-1019`, `chat/runtime.py:112-120`.
- **Evidence and its scope:** Direct inspection of `core_ingest/__init__.py`, call graphs, and import bindings across `core_ingest/`, `ingest/gate.py`, and interactive pipelines at revision `069ceb55`.
- **Classification:** Documented Route Bifurcation & Architectural Relationship Under Review.
- **Architectural consequence:** The repository maintains two intentionally distinct pathways for input processing: transient interactive turns take the direct `ingest/gate.py` injection route, while durable corpus ingestion traverses the three-gate `core_ingest` compiler. While the package documentation explicitly records this runtime short-circuit, the overarching design documents (Whitepaper §VIII, ADR-0012) frame pre-gate governance as an all-encompassing envelope for all incoming information. Whether this separation represents an authorized operational refinement for low-latency interactive cognition, an incomplete integration of pre-gate governance into the interactive pipeline, or an architectural divergence remains unresolved.
- **Proposed disposition:** Record the documented split between transient runtime pressure and durable candidate admission without proposing structural repairs or lightweight envelopes during this assessment phase. Evaluate in subsequent review how governance applies across interactive and durable input boundaries.
- **Verification status:** Confirmed directly from source documentation and code inspection.
- **Unresolved questions:** Does the documented runtime short-circuit satisfy the determinism and provenance invariants intended by Whitepaper §VIII, or was an interactive governance envelope intended to wrap live turn inputs?

---

### FIND-0012: SemanticGate Scope Restricted to Syntactic and Container Validation Without Semantic Analysis

- **Original obligation:** Whitepaper §VIII, Yellowpaper §VII, and ADR-0012 describe `SemanticGate` as the middle gate of `IngestCompiler` that enforces span completeness and structural validity. ADR-0012 explicitly scopes ingestion validation to input form integrity, noting that semantic interpretation belongs inside the field rather than at the extraction boundary.
- **Observed reality in code:**
  Direct inspection of `core_ingest/compiler.py::SemanticGate.check()` (lines 77–133) and helper functions confirms that the gate performs syntactic, delimiter, and schema validation:
  1. Verifies that `payload_json` is not empty or `"{}"`.
  2. If `energy_class_hint` is present in the payload, verifies that it parses to a valid `EnergyClass` enum string.
  3. If `valence` is present in the payload, validates dictionary schema (`_validate_valence_payload`): checks for required channel keys (`affective`, `force`, `emphasis`, `polarity`, `orientation`), requiring `affective` to be a list, and loops over `emphasis`, `polarity`, and `orientation` requiring each to be a dict (the `force` key is verified present in `required` but is not checked in the dict-type loop).
  4. For `Modality.TEXT` and `Modality.SCRIPTURE`: checks that `packet.lemma` is a non-empty string.
  5. For `Modality.CODE`: verifies balanced delimiter nesting (`{}`, `[]`, `()`, `<>`) in `packet.lemma`.
  6. Enforces combined span length $\sum (\text{byte\_end} - \text{byte\_start}) \ge 1$.
  The gate does not evaluate natural-language understanding, propositional truth, ontological consistency, or semantic validity against field state.
  Additionally, convergent-evidence detection is implemented outside `SemanticGate.check()`: in `IngestCompiler.compile()` (lines 276–284), a batch-local counter (`semantic_counts[sk] += 1`) checks whether a packet's `semantic_key` has appeared previously within the compilation run, attaching a warning (`semantic_convergence:<N>_prior_sources`) if prior occurrences exist. A repeated semantic key within a batch produces a warning about prior occurrences; it does not, by itself, establish verified corroboration from independent sources.
- **Implementation sites and consumers:** `core_ingest/compiler.py:77-133, 177-190, 276-284`, `core_ingest/types.py:87-113`.
- **Evidence and its scope:** Direct source code analysis of `SemanticGate.check()` and `IngestCompiler.compile()` at revision `069ceb55`.
- **Classification:** Mechanism Scope Clarification.
- **Architectural consequence:** The gate's operation aligns with ADR-0012's explicit scoping of pre-gate checks to container completeness and syntactic integrity, leaving semantic interpretation to downstream field operations. The gate enforces structural formatting, non-empty lemmas, delimiter balancing, and JSON schema conformity; it does not perform natural-language comprehension or claim verification, nor does its batch-local semantic counter verify independent evidential corroboration.
- **Proposed disposition:** Retain this finding as a scope clarification of the gate's implemented responsibilities — not as evidence that semantic comprehension should be added to the ingestion boundary.
- **Verification status:** Confirmed directly from source inspection.
- **Unresolved questions:** How is multi-source corroboration evaluated across independent ingestion batches and distinct provenance records, and which downstream component performs semantic determination on admitted propositions?

---

### FIND-0013: Non-Text Projection Implementations, Default Activation Policy, and Reviewed Runtime Integration

- **Original obligation:** Whitepaper §IX and ADR-0013 ("`sensorium/` Multimodal Protocol Layer", 2026-05-13) define the Sensorium as the Logos-recovery boundary where every surface signal $S$ is converted to a canonical `(32,)` Cl(4,1) multivector by a `ProjectionHead[S]`. Once projected, the field operates in a single conformal geometric representation.
- **Observed reality in code:**
  Inspection of `sensorium/` reveals a layered architecture with distinct factory defaults, registry activation conditions, direct projection capabilities, and runtime turn integration:
  1. **Protocol Declarations:** `sensorium/protocol.py` defines `ProjectionHead[S]`, `SurfaceDecoder[S]`, `ModalityVocabulary[S]`, and `ModalityPack[S]`.
  2. **Factory Defaults:** Concrete projection heads exist for vision (`VisionProjectionHead`), audio (`AudioProjectionHead`), sensorimotor (`SensorimotorProjectionHead`), and event-vision (`EventVisionProjectionHead`). In their respective factory functions (`make_vision_pack`, `make_audio_pack`, `make_sensorimotor_pack`, `make_event_vision_pack`), the parameters default to `gate_engaged: bool = False, checksum_verified: bool = False`. For text (`sensorium/adapters/text.py`), the general constructor `make_text_pack` defaults to `gate_engaged=True, checksum_verified=True`. Its default language pack constructors provide: `english_pack` with `gate_engaged=True, checksum_verified=True`, and `hebrew_pack` and `koine_greek_pack` with `gate_engaged=False, checksum_verified=True`.
  3. **Caller-Configurable Activation:** The factory functions expose `gate_engaged` and `checksum_verified` as caller-configurable arguments. Callers can instantiate packs with `gate_engaged=True, checksum_verified=True` when authorized. Furthermore, `ProjectionHead` instances can be invoked directly (`head.project(signal)`) to produce `(32,)` float32 multivectors without passing through `ModalityRegistry`.
  4. **Registry Activation Conditions:** When using `ModalityRegistry.project(pack_id, signal)` (lines 102–107), the registry checks `if not pack.gate_engaged:` and raises `RuntimeError("Pack '...' gate is not engaged. Complete the Supervised Seeding Epoch before using this pack.")`. In `ModalityPack.__post_init__`, setting `gate_engaged=True` requires `checksum_verified=True`.
  5. **Mount-Time Unitarity Verification:** `ModalityRegistry.mount(pack, sample)` conditionally executes `pack.projection.verify_unitarity(probe)` only when `pack.projection is not None` and `pack.checksum_verified is False`. If `checksum_verified is True`, or if no probe sample can be resolved, mount-time verification is bypassed. It does not unconditionally remeasure every mounted pack.
  6. **Reviewed Runtime Pipeline Integration:** Neither `chat/runtime.py` nor `core/cognition/pipeline.py` instantiates, mounts, or queries `ModalityRegistry`. Furthermore, interactive cognition does not utilize `sensorium/adapters/text.py`; token injection in `ingest/gate.py::inject()` bypasses the sensorium text adapter completely.
  7. **Perception-Only vs Decoding Asymmetry:** Non-text modality packs configure `decoder=None` (afferent/perception-only). `TextSurfaceDecoder.decode()` is implemented in `sensorium/adapters/text.py:107-131`, but uses Euclidean distance ($\|q - p\|_2$) across registered token coordinates rather than conformal geometric inner products.
- **Implementation sites and consumers:** `sensorium/protocol.py`, `sensorium/registry.py:57-79, 94-120`, `sensorium/adapters/*.py`, `chat/runtime.py`, `core/cognition/pipeline.py`.
- **Evidence and its scope:** Direct static inspection of `sensorium/` and interactive pipeline modules at revision `069ceb55`.
- **Classification:** Implementation Status & Runtime Integration Boundary.
- **Architectural consequence:** Direct static inspection confirms that multimodal Cl(4,1) projection heads, concrete compilers, and protocol definitions exist across `sensorium/`, but non-text packs are configured default-closed (`gate_engaged=False`), requiring explicit caller configuration and checksum verification to project through `ModalityRegistry`. The reviewed interactive turn pipeline operates without `ModalityRegistry` and bypasses the sensorium text adapter in favor of direct `ingest/gate.py` injection.
- **Proposed disposition:** Document the distinction between factory defaults, registry activation gates, direct projection head execution, and interactive pipeline wiring; maintain `REV-Q-006` to track multimodal gating requirements.
- **Verification status:** Confirmed directly from source inspection.
- **Unresolved questions:** What verification criteria govern transitioning a pack from factory-default closed status (`gate_engaged=False`) to active status (`gate_engaged=True`), and how will multimodal inputs integrate with `ingest/gate.py`?

---

### FIND-0014: LearningArtifact Export Seam and Status of train/ Downstream Consumer

- **Original obligation:** ADR-0012, ADR-0014 ("`train/` Learning Loop", 2026-05-13), and Yellowpaper §VII describe a continuous learning loop where candidate pressure accepted by `IngestCompiler` is exported as `LearningArtifact` objects to downstream training machinery to produce closed algebraic updates (rotor updates, vocabulary manifold additions, and attractor seeding without backpropagation).
- **Observed reality in code:**
  1. **Artifact Production and Provenance Registration:** `core_ingest/compiler.py:348` constructs `LearningArtifact(packet=packet, result=result)` for every accepted packet. When a `SegmentManifold` is supplied to `IngestCompiler.compile()`, accepted packets are automatically registered in the manifold (`manifold.register(...)`), indexing `semantic_key -> SourceSpan` for exact provenance recovery.
  2. **Reporting Consumer:** `core/cli_ingest.py` (lines 66–122) receives `artifacts: list[LearningArtifact]` from the pipeline, extracts packet metadata (`pressure_id`, `semantic_key`, `kind`, `modality`, `review_level`, `lemma`, `spans`), and serializes them into the structured JSON/text validation report.
  3. **No Algebraic Learning Consumer Identified:** No `train/` implementation package exists in the repository. ADR-0014 is explicitly designated in its header as `"Accepted (Stub)"` dated 2026-05-13, documenting that `train/` is an unbuilt layer. No downstream consumer was identified in the paths reviewed for this unit that consumes `LearningArtifact` objects to perform algebraic weight updates, rotor optimization, or vocabulary expansion.
  4. **Scope Limitation:** This observation specifically concerns the `LearningArtifact` export seam and the unbuilt `train/` package. It does not establish that all learning in CORE is absent; other learning, teaching, and memory mechanisms (such as session memory, reviewed teaching capture in `teaching/`, and speculative consolidation governed by `INV-21`..`INV-30`) require their own dedicated review.
- **Implementation sites and consumers:** `core_ingest/compiler.py:222-237, 348`, `core_ingest/manifold.py`, `core/cli_ingest.py:66-122`, `docs/adr/ADR-0014-train-learning-loop.md`.
- **Evidence and its scope:** Direct code and ADR inspection at revision `069ceb55`.
- **Classification:** Implementation Boundary & Downstream Consumer Qualification.
- **Architectural consequence:** Artifact production, report serialization, and provenance registration in `SegmentManifold` are implemented. No artifact-to-algebraic-learning consumer was identified within the paths reviewed for this unit.
- **Proposed disposition:** Record that artifact production, reporting, and provenance indexing are implemented, while noting the absence of an artifact-to-algebraic-learning consumer in the reviewed paths. Defer broader evaluation of learning mechanisms to dedicated review units.
- **Verification status:** Confirmed directly from source code and ADR text.
- **Unresolved questions:** How will `LearningArtifact` instances be consumed when algebraic training is implemented, and how will those updates be reconciled with the strict epistemic promotion gate (`INV-21`..`INV-30`)?

---

### FIND-0015: `FieldState` Construction Boundary, Dtype Handling, and Invariant Checking Policy

- **Original obligation:** Whitepaper §V (Invariant I) and `AGENTS.md` (Non-negotiable Field Invariant) mandate that every runtime field state $F$ must satisfy $\text{versor\_condition}(F) < 1\text{e-}6$.
- **Subsequent change:** Static code inspection of `field/state.py` at revision `069ceb55` reveals the construction boundary and invariant checking policy:
  - `FieldState` is defined as a `@dataclass(frozen=True, slots=True)` in `field/state.py:123-150`.
  - In `__post_init__`, it executes:
    1. **Dtype Handling:** `f_dtype` is inspected via `np.asarray(self.F).dtype`. If not `np.float32` or `np.float64`, it defaults to `np.float32`.
    2. **Defensive Isolation:** It executes `F = np.array(self.F, dtype=f_dtype).copy()`. This defensive copy provides memory isolation from the supplied array; however, a frozen dataclass wrapper does not, by itself, make the buffer of an enclosed NumPy array immutable.
    3. **Shape Validation:** It checks `F.shape == (32,)`, raising `ValueError` on mismatch. Identical defensive copying, dtype fallback, and shape checking apply to `holonomy` when non-None.
    4. **Invariant Checking Policy:** `FieldState.__post_init__` does not evaluate `versor_condition(F)`. A `FieldState` instance can be instantiated with arbitrary multivector components without validation of the versor condition.
  - Ingestion gate and boundary enforcement:
    - At the interactive ingestion boundary, `ingest/gate.py:422-427` evaluates `cond = versor_condition(F)` and checks `if cond > 1e-6: raise RuntimeError(...)`. Under this literal predicate, equality (`cond == 1e-6`) passes. The gate strictly rejects candidates with `cond > 1e-6`, but this check alone does not guarantee rejection of every non-versor numerical edge case.
    - Non-null sandwich results are routed through the downstream closure mechanisms described in `FIND-0016`.
- **Implementation sites and consumers:** `field/state.py:123-150`, `ingest/gate.py:422-427`, `field/propagate.py:47-72`.
- **Evidence and its scope:** Direct static code inspection of `field/state.py` and `ingest/gate.py` at revision `069ceb55`.
- **Classification:** Implementation Boundary & Invariant Placement.
- **Architectural consequence:** `FieldState` operates as a structural data container rather than a self-validating algebraic boundary. Protection of the non-negotiable field invariant relies entirely on caller discipline and explicit gateway evaluations (`ingest/gate.py`, `algebra/versor.py`).
- **Proposed disposition:** Document the division of responsibility: `FieldState` provides defensive isolation, shape validation, and dtype standardization, while algebra modules and ingestion gates own manifold invariants.
- **Verification status:** Confirmed directly from source code.
- **Unresolved questions:** None.

---

### FIND-0016: Propagation Kinematics, Backend Dispatch Fallback, and Synthetic Rotor Substitution

- **Original obligation:** Whitepaper §V and ADR-0004 specify propagation as group action on the Spin manifold, preserving the versor condition without ad-hoc drift repairs.
- **Subsequent change:** Static code inspection of `field/propagate.py`, `algebra/backend.py`, and `algebra/versor.py` at revision `069ceb55` reveals the execution kinematics:
  - **Propagation Step:** `propagate_step(state, V)` in `field/propagate.py:47-72` computes `new_F = versor_apply(V, state.F)`.
  - **Backend Dispatch and Fallback Policy:** `algebra/backend.py:122-132` dispatches to Rust (`core_rs`) if available and enabled by `CORE_BACKEND`, but wraps execution in `try ... except (AttributeError, TypeError, ValueError, Exception): pass`, silently falling back to pure Python. Static inspection confirms this dispatch and fallback policy, but does not determine which backend executed in historical runs.
  - **Five Distinct Field Operations:** Inspection of propagation and field evolution paths delineates five distinct operations with differing preservation properties:
    1. *Raw Transport (Null Inputs):* In `algebra/versor.py:160-176`, `versor_apply(V, F)` evaluates `_input_is_null(F)` via `abs(float(cga_inner(F, F))) < 1e-5`. For inputs satisfying `abs(float(cga_inner(F, F))) < 1e-5`, it returns the raw float64 sandwich without invoking the non-null closure path. This predicate does not establish that the input is a grade-1 conformal point, validate the operator, or measure the output’s null residual.
    2. *Algebraic Normalization:* `_unitize_closed(v)` in `algebra/versor.py:30-50` rescales magnitude by $1/\sqrt{\langle v \widetilde{v} \rangle_0}$ when non-scalar residue $< 10^{-2}$ and scalar square $> 0$.
    3. *Deterministic Seed-Derived Replacement:* `_seed_to_rotor(v)` in `algebra/versor.py:52-68` replaces the candidate with a rotor synthesized from selected input coefficients and the input coefficient norm; preservation of the candidate's geometric meaning is not established. This is a deterministic seed-derived replacement, not rejection of the transition.
    4. *Energy Refresh:* `propagate_step` updates energy conditionally (only when `state.energy is not None`), incrementing `activation_count`, advancing `current_cycle`, and passing `coherence_residual = 0.0` as an assigned policy constant argument.
    5. *Turn-Finalization Anchoring:* `session/context.py:182-240, 268-270` executes inside `finalize_turn` before graph/state/vault publication, applying hemisphere sign checks and `_session_anchor_pull`. It calls the same null-bypass / non-null closure boundary; calling this function alone does not establish unmodified sandwich transport or universal strict closure.
  - **Substitution Call Hierarchy in `algebra/versor.py`:**
    - `_close_applied_versor(v)` tries `_runtime_closed(v)`; on caught `ValueError`, it attempts `_seed_to_rotor(v)`.
    - `_runtime_closed(v)` calls `unitize_versor(v)` at `float64`. If `versor_condition(candidate) < 1e-6`, it returns the candidate; otherwise it invokes `_seed_to_rotor(v)`.
    - `unitize_versor(v)` tries `_unitize_closed(v)`. If a `ValueError` containing `"bad_residue"` is caught and support has at least eight components with `abs(component) > 1e-12` (`_DENSE_SEED_MIN_COMPONENTS = 8`, `_NEAR_ZERO_TOLERANCE = 1e-12`), it falls back to `_seed_to_rotor(v)`.
- **Implementation sites and consumers:** `field/propagate.py:47-72`, `algebra/backend.py:122-132`, `algebra/versor.py:30-82, 122-180`.
- **Evidence and its scope:** Static code inspection at revision `069ceb55`.
- **Classification:** Kinematics Implementation & Boundary Closure.
- **Architectural consequence:** In the non-null regime, `versor_apply` routes the raw sandwich result through unitization and, on the documented failure paths, deterministic seed-derived replacement. Static inspection establishes these mechanisms, not universal strict closure or preservation of the candidate’s geometric meaning for every input.
- **Proposed disposition:** Record the precise mechanics of `versor_apply`, distinguishing raw transport (null inputs), algebraic scaling (`_unitize_closed`), and deterministic replacement (`_seed_to_rotor`).
- **Verification status:** Confirmed directly from source code.
- **Unresolved questions:** None.

---

### FIND-0017: Field Energy Operator Policy and Constant Parameter Assignment in Propagation

- **Original obligation:** ADR-0006 defines the Field Energy Operator $H: \text{FieldState} \to \mathbb{R}_{\ge 0}$ as a Hamiltonian companion scalar computed from convergence density, recency, coherence residual, and aspect-class weight.
- **Subsequent change:** Inspection of `docs/adr/ADR-0006-field-energy-operator.md`, `core/physics/energy.py`, and `field/propagate.py` at revision `069ceb55` reveals:
  - `FieldEnergyOperator.compute()` in `core/physics/energy.py:75-107` computes raw energy from four weighted terms: `raw = 0.35 * convergence + 0.25 * recency + 0.20 * residual + 0.20 * aspect`.
  - **Conditional Execution:** In `field/propagate.py:50-64`, energy recomputation occurs only when `state.energy is not None`. If `state.energy` is None, `new_energy` remains None.
  - **Propagation Step Parameters:** When `state.energy is not None`:
    - `activation_count` increments by 1.
    - `current_cycle` updates to `new_step`.
    - `convergence_density`, `last_activation_cycle`, `anchor_adjacent`, and `aspect_weight` are inherited from the prior `EnergyProfile`.
    - `coherence_residual = 0.0` is passed as an assigned constant argument (based on the design assumption in ADR-0006 that propagation is not a corrective pass), not as an empirical measurement of zero residual or zero field tension.
- **Implementation sites and consumers:** `docs/adr/ADR-0006-field-energy-operator.md`, `core/physics/energy.py`, `field/propagate.py:50-64`.
- **Evidence and its scope:** Complete substantive reading of ADR-0006 and static tracing of `field/propagate.py` and `core/physics/energy.py` at revision `069ceb55`.
- **Classification:** Operator Implementation & State Evolution.
- **Architectural consequence:** During propagation steps, coherence residual does not reflect dynamic geometric deformation or field tension; it is clamped to zero by constant parameter assignment. The recency contribution combines capped activation count with exponential age decay; advancing a propagation step does not, by itself, establish monotonically decreasing total energy.
- **Proposed disposition:** Document that propagation steps update the energy profile conditionally and set `coherence_residual = 0.0` as an assigned policy constant.
- **Verification status:** Confirmed directly from source code and ADR text.
- **Unresolved questions:** None.

---

### FIND-0018: Semantic Anchoring Kinematic Discrepancy, Historical Docstring Evidence, and Unresolved Operator Mismatch

- **Original obligation:** `AGENTS.md` permits session-scoped semantic anchoring of the field toward the session concept-attractor in `session/context.py` only because every such operation is intended to preserve `versor_condition` by construction and carry semantic meaning in the cognitive model (nudging the field toward the anchor).
- **Subsequent change:** Static code inspection of `session/context.py:182-240, 268-270`, `algebra/rotor.py:285-305`, and `algebra/versor.py:160-180` reveals:
  - **Turn-Finalization Anchoring:** Inside `finalize_turn`, before graph, state, and vault publication:
    1. `_hemisphere_consistent_field` flips field sign if $\text{cga\_inner}(F, \text{Anchor}) < 0.0$.
    2. `_session_anchor_pull` calls $R = \text{word\_transition\_rotor}(F, \text{Anchor})$, scales it via $R^\alpha = \text{rotor\_power}(R, 0.05)$, and executes `pulled_F = versor_apply(R_step, field_state.F)`.
  - **Operator Construction vs. Application Kinematics:**
    - `word_transition_rotor(A, B)` in `algebra/rotor.py:289` computes $R = B \widetilde{A}$. For normalized invertible versors with $\widetilde{A} A = 1$, under left multiplication $R$ satisfies the endpoint identity:
      $$R A = (B \widetilde{A}) A = B (\widetilde{A} A) = B.$$
    - However, `_session_anchor_pull` applies the fractional operator $R^\alpha$ via `versor_apply`, which performs a sandwich transformation:
      $$F' = R^\alpha F \widetilde{R^\alpha}.$$
    - At full power ($\alpha = 1$), for normalized invertible versors with $\widetilde{A} A = 1$, and $R = B \widetilde{A}$:
      $$R A \widetilde{R} = (B \widetilde{A}) A (A \widetilde{B}) = B A \widetilde{B}.$$
    - This evaluates to $B A \widetilde{B}$, which need not equal $B$. The relative operator's left-action endpoint identity ($R A = B$) does not imply $R A \widetilde{R} = B$, nor does it establish that sandwiching $A$ by $R^\alpha$ moves it toward $B$.
    - The endpoint identity for $R^\alpha A$ does not, by itself, establish a particular metric, principal-power domain, or geodesic interpretation.
  - **Invariant and Closure Characterization:**
    - `session/context.py:231` passes $R^\alpha$ and $F$ to `versor_apply`, which calls the same null-bypass / non-null closure boundary described in `FIND-0016`. Calling this function alone does not establish unmodified sandwich transport or universal strict closure.
    - The docstring in `session/context.py:216` citing a "100k-step measurement" is historical docstring and design testimony from earlier project phases; it was not re-run or pinned to an active test lane in this assessment unit.
  - **State Representation Context:**
    - ADR-0241 §2 discusses representations, noting a distinction between sandwich transport for multivectors ($\psi' = R \psi \widetilde{R}$) and left multiplication for spinors ($\psi' = R \psi$). However, that distinction is relevant context and does not constitute a decision or authorization to alter the session field representation.
  - **Central Conclusion:**
    - The relative operator's left-action endpoint identity does not establish the claimed attractor-directed behavior under the sandwich action used by this caller. The intended state representation, action, trajectory, and applicable invariant require reconciliation.
- **Implementation sites and consumers:** `session/context.py:182-240, 268-270`, `algebra/rotor.py:285-305`, `algebra/versor.py:160-180`.
- **Evidence and its scope:** Direct static code inspection at revision `069ceb55`.
- **Classification:** Kinematic Discrepancy & Documentation Reconciliation.
- **Architectural consequence:** `finalize_turn` invokes hemisphere consistency and the anchor-pull helper before graph/state/vault publication. The helper can return the input unchanged when no anchor exists or when transition construction or rotor-power evaluation raises `ValueError`. If the sandwich action of $R^\alpha$ does not direct $F$ toward the anchor on the manifold, the semantic pull does not realize its stated cognitive function.
- **Proposed disposition:** Register `REV-Q-008` as an unresolved formal review question. Do not modify runtime code, adjust tolerances, or preselect a repair.
- **Verification status:** Call structure and algebraic action distinction confirmed by static inspection; attractor-directed behavior remains unresolved in `REV-Q-008`.
- **Unresolved questions:** Addressed in `REV-Q-008`.

---

## 3. Canonical Question Register: Disputed Invariants & Historical Claims

The following tensions across historical documents, code implementations, and external experiments are held as **Formal Review Questions** rather than premature architectural verdicts. This register is the single canonical question roster for the restoration assessment.

| Question ID | Topic | Source Reference | Historical Claim / Tension | Formal Review Question | Verification Plan |
|---|---|---|---|---|---|
| [**`REV-Q-001`**](#rev-q-001-algebraic-tolerance-thresholds-and-boundary-regimes) | Algebraic Tolerance | `docs/Whitepaper.md` §V, `algebra/versor.py`, `vocab/manifold.py` | Tolerance locations and regimes differ: Whitepaper & `AGENTS.md` specify runtime closure `< 1e-6` (enforced in `algebra/versor.py` at float64), whereas `vocab/manifold.py` defines `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` for vocabulary admission (float32 storage, float64 diagnostics, `allow_negative=True`), and `algebra/versor.py` defines `_NULL_INNER_TOL = 1e-5` for null routing. | What are the mathematically and mechanically justified tolerances for each boundary (vocabulary admission, runtime closure, construction residue, null-input routing), and how do normalization and `_seed_to_rotor` substitution interact? | Trace `algebra/versor.py`, `vocab/manifold.py`, and `algebra/rotor.py` across dtypes and sign branches in Phase 2. |
| [**`REV-Q-002`**](#rev-q-002-vocabulary-representation-on-the-conformal-manifold) | Vocab Representation | `docs/adr-audit/20-finding-register.md` (`AA-2`) | `VocabManifold.add()` stores unit versors ($V \widetilde{V} = 1$), rejecting conformal null points ($X \cdot X = 0$), conflicting with Whitepaper Invariants II & III. | What is the lawful algebraic relationship between conformal point representations and operator versors in the Logos vocabulary manifold? | Review `algebra/cga.py` point embedding formulas against `VocabManifold.add()` in Phase 2. |
| [**`REV-Q-003`**](#rev-q-003-geometric-custody-vs-relational-lookup) | Relational Lookup | `docs/adr-audit/20-finding-register.md` (`AA-1`) | `VocabManifold.nearest()` returns single word on production mount; 350/353 stored surfaces fail identity recall. | Does standard conformal inner product support relational lookup, or is nearest-neighbor search an inherited abstraction that conflicts with Cl(4,1) rotor geometry? | Trace `generate/articulation.py` and evaluate retrieval behavior in Phase 2. |
| [**`REV-Q-004`**](#rev-q-004-role-of-geometry-in-semantic-determination-and-tested-outcomes) | Geometry & Outcomes | `coreai` PR #291 (`LOGOS-ABLATION-1`) | Historical PR #291 report concluded geometric operations failed to perform semantic determination on WA1 test workload. | What role was geometry intended to play, which mechanism actually determined the tested outcomes, and what does the experiment establish within its specific implementation and workload? | Examine PR #291 diff, test data, and ablation scripts in Phase 3. |
| [**`REV-Q-005`**](#rev-q-005-epistemic-transitions-and-drift-repair-boundary) | Drift Repair Boundary | `AGENTS.md` (`INV-21`..`INV-30`) | `AGENTS.md` strictly prohibits watchdog normalization or drift repair in hot paths, restricting closure to `algebra/versor.py`. | How do live session field updates and memory consolidation operations maintain the versor condition by construction without triggering drift-repair violations? | Audit `session/context.py` and `vault/store.py` against `_close_applied_versor` in Phase 2. |
| [**`REV-Q-006`**](#rev-q-006-sensory-modality-recovery-boundary) | Modality Recovery | ADR-0013, `sensorium/protocol.py`, `sensorium/adapters/` | ADR-0013 specifies projection heads as the Logos-recovery boundary into `(32,)` Cl(4,1) multivectors. Unit 2 verified protocol types and non-text compilers exist, but non-text packs default to closed gates (`gate_engaged=False`) and the runtime turn pipeline bypasses `sensorium/` for direct token injection. | What evaluation gates and seeding epochs govern engaging modality gates (`gate_engaged=True`), and how are multimodal multivectors admitted into field state without bypassing versor coherence? | Trace modality compiler versors and eval gates against ADR-0013/ADR-0181/ADR-0197 in Phase 2. |
| [**`REV-Q-007`**](#rev-q-007-historical-predecessor-lineage-and-commit-integrity) | Object Provenance | `core-iii/docs/NON-INHERITANCE.md` §2.1 | Git blob `aa80bce` is missing from `coreai` repository history. | Does blob `aa80bce` or its referenced commit exist in `core`'s git object database, and does it affect any live provenance seals? | Search `core` git object database via `git cat-file -e aa80bce` in Phase 3. |
| [**`REV-Q-008`**](#rev-q-008-semantic-anchoring-kinematics-and-operator-action) | Semantic Anchoring Kinematics | `session/context.py:197-240`, `algebra/rotor.py:285-305`, `algebra/versor.py:160-180`, `AGENTS.md` | `_session_anchor_pull` claims to perform a mild rotor-geodesic pull toward the session concept-attractor via $R = B \widetilde{A}$, $R^\alpha = \text{rotor\_power}(R, 0.05)$, and `versor_apply(R_step, F)`. But $R = B \widetilde{A}$ is a left-multiplication operator ($R A = B$), whereas `versor_apply` executes a sandwich transformation ($R^\alpha A \widetilde{R^\alpha}$), evaluating at $\alpha=1$ to $B A \widetilde{B}$, which need not equal $B$. | What representation and group action are intended at the session-anchor boundary? Under those contracts, what does $R^\alpha A\widetilde{R^\alpha}$, with $R=B\widetilde A$, preserve, and what establishes movement toward the anchor? If distance reduction is required, which explicitly defined distance and domain apply? | Trace group action contracts across `session/context.py`, `algebra/rotor.py`, and ADR-0241 §2, evaluating trajectory behavior and manifold distance metrics under both left-action and sandwich formulations without mutating runtime code. |

---

### Detailed Question Records

#### REV-Q-001: Algebraic Tolerance Thresholds and Boundary Regimes
- **Topic:** Algebraic closure condition, numerical tolerance locations, and operator substitution.
- **Source References:** `docs/Whitepaper.md` §V (Invariant I), `AGENTS.md` (Non-negotiable Field Invariant), `algebra/versor.py` (lines 13–15, 146), `vocab/manifold.py` (line 40), `docs/adr-audit/20-finding-register.md` claim `AA-4`.
- **Context & Tension:** Tolerances are distributed across distinct functional boundaries and numeric regimes, rather than a single global constant:
  1. **Runtime Closure:** `algebra/versor.py` line 14 defines `_RUNTIME_CLOSURE_TOLERANCE = 1e-6`, matching Whitepaper Invariant I and `AGENTS.md` (`versor_condition(F) < 1e-6`). Enforced in `float64` via `_runtime_closed`, `_close_applied_versor`, and `normalize_to_versor`. Calls `versor_condition` with `allow_negative=False`, strictly requiring positive unit $+1.0$.
  2. **Vocabulary Admission:** `vocab/manifold.py` line 40 defines `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5`. Enforced on `add()` and `update()` via `_assert_manifold_versor`. Storage is in `float32`, but residual diagnostics evaluate in `float64` via `versor_unit_residual(v, allow_negative=True)`, admitting both positive ($\approx +1$) and negative ($\approx -1$) unit versors.
  3. **Construction Residue:** `algebra/versor.py` line 13 defines `_CONSTRUCTION_RESIDUE_TOLERANCE = 1e-2`. Used in `_unitize_closed` at `float64` to admit non-scalar residue before scaling by $1/\sqrt{\text{scalar\_sq}}$ (requires $\text{scalar\_sq} > 0.0$).
  4. **Null-Input Routing:** `algebra/versor.py` line 146 defines `_NULL_INNER_TOL = 1e-5` (evaluated at `float64`), routing null vectors ($|F \cdot F| < 10^{-5}$) around `_close_applied_versor` in `versor_apply` to preserve conformal point geometry.
  5. **Normalization vs. Synthetic Rotor Substitution:** `algebra/versor.py` distinguishes algebraic normalization (`_unitize_closed`, which rescales an existing versor candidate by $1/\sqrt{\text{scalar\_sq}}$) from synthetic rotor substitution (`_seed_to_rotor`). In `unitize_versor`, substitution triggers only when `bad_residue` is encountered AND support is sufficient (`support >= _DENSE_SEED_MIN_COMPONENTS`, i.e. $\ge 8$). Other paths invoke substitution after closure failure (e.g. in `normalize_to_versor` or `_runtime_closed` when `versor_condition >= _RUNTIME_CLOSURE_TOLERANCE`) or caught `ValueError`. When invoked, `_seed_to_rotor` does not simply extract bivector coefficients; it samples the seed through the indexed expression `seed[(blade + step) % 32] / scale` across six fixed bivectors `_SEED_BIVECTORS = (6, 7, 8, 10, 11, 13)` and composes a newly synthesized, closed rotor via $\cos(\theta) + \sin(\theta) e_{\text{blade}}$ factors where $\theta = 0.5 \tanh(\text{source})$.
  6. **Attribution Correction:** An earlier draft of this restoration assessment incorrectly located `_MANIFOLD_RESIDUAL_TOLERANCE` in `algebra/versor.py` and treated distinct boundary predicates as one regime. This record corrects that assessment error. Historical AA-4 separately reports a discrepancy between vocabulary admission tolerance and the documented invariant; its interpretation remains under review.
- **Formal Review Question:** What are the mathematically and mechanically justified tolerances for each distinct boundary (vocabulary admission, runtime field closure, construction residue, null routing), and what is the empirical residual distribution across dtypes and sign branches on live mounts?
- **Verification Plan:** In Phase 2, trace all tolerance sites across `algebra/versor.py`, `vocab/manifold.py`, and `algebra/rotor.py`, evaluate numerical accumulation in `_close_applied_versor`, and verify positive/negative unit handling without modifying runtime code.

#### REV-Q-002: Vocabulary Representation on the Conformal Manifold
- **Topic:** Conformal embedding geometry of vocabulary items.
- **Source References:** `docs/Whitepaper.md` §V (Invariants II & III), `algebra/cga.py`, `docs/adr-audit/20-finding-register.md` claim `AA-2`.
- **Context & Tension:** Whitepaper Invariant II specifies that vocabulary items are represented as null vectors on the conformal horosphere ($X \cdot X = 0$). In contrast, `VocabManifold.add()` enforces a unit versor condition ($V \widetilde{V} = 1$), which rejects genuine conformal null points. Historical claim `AA-2` asserts this is an algebraic contradiction.
- **Formal Review Question:** What is the lawful algebraic relationship between conformal null point representations ($X \in \mathcal{H}$) and operator versors ($V \in \text{Spin}(4,1)$) in the Logos vocabulary manifold?
- **Verification Plan:** In Phase 2, trace `algebra/cga.py` embedding functions against `VocabManifold` storage and retrieval contracts.

#### REV-Q-003: Geometric Custody vs Relational Lookup
- **Topic:** Retrieval mechanics and associative lookup on the manifold.
- **Source References:** `generate/articulation.py`, `docs/adr-audit/20-finding-register.md` claim `AA-1`, `AGENTS.md` (Exact Recall Invariant).
- **Context & Tension:** Historical audit finding `AA-1` asserted that `VocabManifold.nearest()` collapsed to a single token in production tests, with 350 of 353 stored surfaces failing identity recall. Furthermore, `AGENTS.md` forbids approximate nearest neighbor (ANN/HNSW) algorithms in favor of exact CGA recall primitives.
- **Formal Review Question:** Does the standard conformal inner product support direct relational lookup among embedded vocabulary items, or is nearest-neighbor search an inherited vector-space abstraction that conflicts with Clifford rotor geometry?
- **Verification Plan:** In Phase 2, trace `generate/articulation.py` and inspect retrieval fidelity on verified corpus entries.

#### REV-Q-004: Role of Geometry in Semantic Determination and Tested Outcomes
- **Topic:** Role of geometry in semantic determination and interpretation of experimental test outcomes.
- **Source References:** `coreai` PR #291 (`LOGOS-ABLATION-1`), `core-iii/docs/NON-INHERITANCE.md` §2.4.
- **Context & Tension:** In historical reporting from `coreai` PR #291 (`LOGOS-ABLATION-1`), the author concluded that geometric algebra operations failed to perform semantic determination on the WA1 possession-polar test workload (reporting verdict FAIL). This assessment treats that historical conclusion as an external, unverified claim specific to that implementation and test workload; it has not been independently reproduced here, and must not be generalized to the entire architecture. Furthermore, it is not assumed that the complete intended Logos mechanism was present in the tested execution path, nor is it assumed that completing that mechanism would necessarily alter the result.
- **Formal Review Question:** What role was geometry intended to play, which mechanism actually determined the tested outcomes, and what does the experiment establish within its specific implementation and workload?
- **Verification Plan:** In Phase 3, examine PR #291 code diffs, golden test corpora, and ablation logs in `ACB-CORE-Labs/coreai` without adopting external conclusions as unverified premises.

#### REV-Q-005: Epistemic Transitions and Drift-Repair Boundary
- **Topic:** Epistemic status enforcement and normalization boundaries.
- **Source References:** `AGENTS.md` (`INV-21`..`INV-30`), `algebra/versor.py`, `vault/store.py`, `session/context.py`.
- **Context & Tension:** `AGENTS.md` establishes a bright line between *semantic anchoring* (allowed at explicit boundaries) and *drift repair* (strictly forbidden in hot paths and memory operations). It restricts closure of field transitions solely to `algebra/versor.py` (`_close_applied_versor`).
- **Formal Review Question:** How do live session field updates and memory consolidation operations maintain the versor condition by construction without triggering drift-repair violations?
- **Verification Plan:** In Phase 2, audit `session/context.py` and `vault/store.py` against `_close_applied_versor` invocation paths.

#### REV-Q-006: Sensory Modality Recovery Boundary
- **Topic:** Multimodal input projection, protocol boundary, and runtime gate engagement.
- **Source References:** `docs/adr/ADR-0013-sensorium-multimodal-protocol.md`, `docs/adr/ADR-0181-audio-compiler-delta-crdt.md`, `docs/adr/ADR-0197-vision-compiler-delta-crdt.md`, `sensorium/protocol.py`, `sensorium/registry.py`, `sensorium/adapters/*.py`.
- **Context & Tension:** ADR-0013 defines projection heads as the "Logos-recovery boundary" converting any surface signal into a canonical `(32,)` Cl(4,1) multivector before reaching the versor field. Review Unit 2 established that while protocol declarations (`ProjectionHead`, `SurfaceDecoder`, `ModalityVocabulary`, `ModalityPack`) and concrete compilers (`VisionCompiler`, `AudioCompiler`, `SensorimotorCompiler`, `EventVisionCompiler`) exist and produce `(32,)` float32 multivectors, non-text pack factory functions default to `gate_engaged=False, checksum_verified=False`. `ModalityRegistry.project()` enforces gate activation, refusing projection when `gate_engaged` is False. The inspected interactive turn pipeline (`chat/runtime.py` and `core/cognition/pipeline.py`) does not instantiate or mount `ModalityRegistry`, and bypasses the sensorium text adapter to call `ingest/gate.py::inject()` directly. Furthermore, non-text modalities configure `decoder=None` (afferent/perception-only), and `TextSurfaceDecoder.decode()` uses Euclidean $L_2$ distance across registered token coordinates rather than conformal geometric inner products.
- **Formal Review Question:** What evaluation criteria and seeding epochs govern transitioning modality packs from factory-default closed status (`gate_engaged=False`) to active status (`gate_engaged=True`), and how are multimodal multivectors intended to be admitted into field state alongside `ingest/gate.py` injection?
- **Verification Plan:** In Phase 2, trace non-text compiler mathematics (`sensorium/vision/`, `sensorium/audio/`, `sensorium/sensorimotor/`) and evaluate the gating criteria in ADR-0181 §2.5 and ADR-0197 against the unified Cl(4,1) field state.

#### REV-Q-007: Historical Predecessor Lineage and Commit Integrity
- **Topic:** Provenance of ported historical artifacts and missing git objects.
- **Source References:** `core-iii/docs/NON-INHERITANCE.md` §2.1, git commit `4ca2431e`.
- **Context & Tension:** `core-iii` documentation reported that git blob `aa80bce` was missing from `coreai` repository history, triggering provenance refusals.
- **Formal Review Question:** Does blob `aa80bce` or its referenced commit exist in `core`'s git object database, and does it affect any live provenance seals?
- **Verification Plan:** In Phase 3, query the `core` git object database via `git cat-file -e aa80bce` and trace its origin.

#### REV-Q-008: Semantic Anchoring Kinematics and Operator Action
- **Topic:** Operator action mismatch in session semantic anchoring.
- **Source References:** `session/context.py:197-240, 268-270`, `algebra/rotor.py:285-305`, `algebra/versor.py:160-180`, `AGENTS.md` (Allowed Normalization Boundaries).
- **Context & Tension:** `_session_anchor_pull` is documented as a semantic anchoring site that nudges the field toward the session concept-attractor. It constructs $R = \text{word\_transition\_rotor}(F, \text{Anchor}) = B \widetilde{A}$. While $R A = B$ holds for left multiplication, `versor_apply` applies $R^\alpha$ via sandwich conjugation: $F' = R^\alpha A \widetilde{R^\alpha}$. For normalized invertible versors with $\widetilde{A} A = 1$, at $\alpha = 1$ this yields $R A \widetilde{R} = (B \widetilde{A}) A (A \widetilde{B}) = B A \widetilde{B}$, which need not equal $B$. Thus, the left-action endpoint identity does not establish movement toward $B$ under the sandwich action. Furthermore, `versor_apply` routes through the null-bypass / non-null closure boundary (`_close_applied_versor`), where closure failure can trigger deterministic seed-derived rotor substitution.
- **Formal Review Question:** What representation and group action are intended at the session-anchor boundary? Under those contracts, what does $R^\alpha A\widetilde{R^\alpha}$, with $R=B\widetilde A$, preserve, and what establishes movement toward the anchor? If distance reduction is required, which explicitly defined distance and domain apply?
- **Verification Plan:** In Phase 2, trace group action semantics and manifold metric definitions across `session/context.py`, `algebra/rotor.py`, and related ADRs to reconcile the intended state representation and operator action without code modifications.
