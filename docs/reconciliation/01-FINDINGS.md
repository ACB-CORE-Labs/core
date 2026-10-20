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

## 3. Canonical Question Register: Disputed Invariants & Historical Claims

The following tensions across historical documents, code implementations, and external experiments are held as **Formal Review Questions** rather than premature architectural verdicts. This register is the single canonical question roster for the restoration assessment.

| Question ID | Topic | Source Reference | Historical Claim / Tension | Formal Review Question | Verification Plan |
|---|---|---|---|---|---|
| [**`REV-Q-001`**](#rev-q-001-algebraic-tolerance-thresholds-and-boundary-regimes) | Algebraic Tolerance | `docs/Whitepaper.md` §V, `algebra/versor.py`, `vocab/manifold.py` | Tolerance locations and regimes differ: Whitepaper & `AGENTS.md` specify runtime closure `< 1e-6` (enforced in `algebra/versor.py` at float64), whereas `vocab/manifold.py` defines `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` for vocabulary admission (float32 storage, float64 diagnostics, `allow_negative=True`), and `algebra/versor.py` defines `_NULL_INNER_TOL = 1e-5` for null routing. | What are the mathematically and mechanically justified tolerances for each boundary (vocabulary admission, runtime closure, construction residue, null-input routing), and how do normalization and `_seed_to_rotor` substitution interact? | Trace `algebra/versor.py`, `vocab/manifold.py`, and `algebra/rotor.py` across dtypes and sign branches in Phase 2. |
| [**`REV-Q-002`**](#rev-q-002-vocabulary-representation-on-the-conformal-manifold) | Vocab Representation | `docs/adr-audit/20-finding-register.md` (`AA-2`) | `VocabManifold.add()` stores unit versors ($V \widetilde{V} = 1$), rejecting conformal null points ($X \cdot X = 0$), conflicting with Whitepaper Invariants II & III. | What is the lawful algebraic relationship between conformal point representations and operator versors in the Logos vocabulary manifold? | Review `algebra/cga.py` point embedding formulas against `VocabManifold.add()` in Phase 2. |
| [**`REV-Q-003`**](#rev-q-003-geometric-custody-vs-relational-lookup) | Relational Lookup | `docs/adr-audit/20-finding-register.md` (`AA-1`) | `VocabManifold.nearest()` returns single word on production mount; 350/353 stored surfaces fail identity recall. | Does standard conformal inner product support relational lookup, or is nearest-neighbor search an inherited abstraction that conflicts with Cl(4,1) rotor geometry? | Trace `generate/articulation.py` and evaluate retrieval behavior in Phase 2. |
| [**`REV-Q-004`**](#rev-q-004-role-of-geometry-in-semantic-determination-and-tested-outcomes) | Geometry & Outcomes | `coreai` PR #291 (`LOGOS-ABLATION-1`) | Historical PR #291 report concluded geometric operations failed to perform semantic determination on WA1 test workload. | What role was geometry intended to play, which mechanism actually determined the tested outcomes, and what does the experiment establish within its specific implementation and workload? | Examine PR #291 diff, test data, and ablation scripts in Phase 3. |
| [**`REV-Q-005`**](#rev-q-005-epistemic-transitions-and-drift-repair-boundary) | Drift Repair Boundary | `AGENTS.md` (`INV-21`..`INV-30`) | `AGENTS.md` strictly prohibits watchdog normalization or drift repair in hot paths, restricting closure to `algebra/versor.py`. | How do live session field updates and memory consolidation operations maintain the versor condition by construction without triggering drift-repair violations? | Audit `session/context.py` and `vault/store.py` against `_close_applied_versor` in Phase 2. |
| [**`REV-Q-006`**](#rev-q-006-sensory-modality-recovery-boundary) | Modality Recovery | ADR-0013, `sensorium/protocol.py` | ADR-0013 defines projection heads as the "Logos-recovery boundary" converting any surface signal into a `(32,)` Cl(4,1) multivector. | How faithfully does the current implementation of `sensorium/` isolate modality-specific heuristics from entering the engine field state? | Trace `sensorium/` implementations against ADR-0013 in Phase 2. |
| [**`REV-Q-007`**](#rev-q-007-historical-predecessor-lineage-and-commit-integrity) | Object Provenance | `core-iii/docs/NON-INHERITANCE.md` §2.1 | Git blob `aa80bce` is missing from `coreai` repository history. | Does blob `aa80bce` or its referenced commit exist in `core`'s git object database, and does it affect any live provenance seals? | Search `core` git object database via `git cat-file -e aa80bce` in Phase 3. |

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
- **Topic:** Multimodal input projection and protocol boundary vs concrete compilers.
- **Source References:** `docs/adr/ADR-0013-sensorium-multimodal-protocol.md`, `sensorium/protocol.py`.
- **Context & Tension:** ADR-0013 defines projection heads as the "Logos-recovery boundary" converting surface signals into `(32,)` Cl(4,1) multivectors. While `sensorium/protocol.py` defines the protocol interfaces (`ProjectionHead`, `SurfaceDecoder`, `ModalityVocabulary`, `ModalityPack`), concrete modality encoders and compilers reside in subpackages, leaving open which paths fulfill the intended sensorium mission.
- **Formal Review Question:** How faithfully does the current implementation of `sensorium/` isolate modality-specific heuristics from entering the engine field state, and which concrete compilers fulfill the intended protocol boundary?
- **Verification Plan:** In Phase 2, trace `sensorium/` implementations and subpackages against ADR-0013 specifications.

#### REV-Q-007: Historical Predecessor Lineage and Commit Integrity
- **Topic:** Provenance of ported historical artifacts and missing git objects.
- **Source References:** `core-iii/docs/NON-INHERITANCE.md` §2.1, git commit `4ca2431e`.
- **Context & Tension:** `core-iii` documentation reported that git blob `aa80bce` was missing from `coreai` repository history, triggering provenance refusals.
- **Formal Review Question:** Does blob `aa80bce` or its referenced commit exist in `core`'s git object database, and does it affect any live provenance seals?
- **Verification Plan:** In Phase 3, query the `core` git object database via `git cat-file -e aa80bce` and trace its origin.
