# Stack dossier — A1 · Algebra & Geometry Foundations

**Zone(s):** M0 · `L0-algebra` (per `docs/assessment/02-layer-taxonomy.md`; spills structurally into `L1-field` and M1 `vocab-manifold`/`L3-packs` — see §3) | **Tier:** A
**Member ADRs:** ADR-0001 (VocabManifold Versor Invariant), ADR-0003 (Coordinate System Dissolution), ADR-0004 (Rotor as Operator, Not Vocabulary Property) — read in that order, which is also their dependency order (0004 `Implements:` 0003; 0003 §Consequences delegates its own back-door risk to 0001)
**Dossier author:** Opus 5 (ADR Audit, Batch 1 Tier A) | **`verified_at` SHA:** `cbfc8ccb`
**Prior evidence adopted, not re-derived:**
- `docs/assessment/10-layer-cards/M0-substrate.md` (`verified_at` `8927c563`) — M0 `live-serving` / `fit`; the 1e-6 closure gate; the `versor_condition` 0.22% vs `cga_inner`/`geometric_product` ~73% profile; the Rust-parity open question. **Adopted.**
- `docs/assessment/30-gap-register.md` **G-25** (upgraded + RULED 2026-07-28) — `packs.compiler._blend_feature_versors` ignores its `strength` argument; the cure (`rotor_power` + `word_transition_rotor`) shipped in `algebra/rotor.py` from the algebra layer's first commit and was never called. **Adopted verbatim; independently re-verified at `cbfc8ccb` (still unrepaired in production).**
- `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` — FA-1 **NO-GO**; §5.4 records that R1 (geodesic blending) removes **53 coordinate collisions** from the six-pack mount and 37 from the trilingual one. **Adopted as a settled ruling and used as fitness evidence for ADR-0004.** My own §1 measurement reproduces the 53 exactly (353 surfaces → 300 distinct), which cross-validates both.
- `docs/assessment/31-hindrance-audit.md` — "Pure-Python-by-default algebra … measured as the correct posture". **Adopted; not re-opened.**
- `docs/census/cbfc8ccb…/stale-references.jsonl`, `docstring-drift.jsonl`, `param-no-effect.jsonl`, `silent-drop.jsonl` — consulted; see AA-A1-9 and AA-A1-12.
- `docs/audit/substrate-liveness-registry.md` — **adopted with caveat only**; it is a retired instrument (superseded by the gap register per R-7) and its L0 symbol-consumer table is stale (AA-A1-10).
- No `20-component-cards/` entry exists for M0 / `L0-algebra` (the eight component cards cover the four zero-subsystem zones, always-on, derivation organs, surface selection, attention). Recorded as absent, not skipped.

---

## 0. Why this is one stack

All three ADRs were decided in a single session on 2026-05-12 (`docs/adr/SESSION-2026-05-12.md`, 20:39 → 20:51) and shipped in one atomic commit `bd423e4`. They are one decision expressed three ways:

- **ADR-0003** states the architectural position: the system needs *no explicit coordinate system*, because the field-state model dissolves the need for one. Rotors survive as **operators**, not as a frame.
- **ADR-0003 §Consequences** names the one place that position could fail — "`vocab/` is the most likely place for the coordinate frame to quietly re-emerge" — and delegates the guard to **ADR-0001**, which installs an algebraic admission test at `VocabManifold.add()`.
- **ADR-0004** removes the counter-example the session found while auditing that guard: `VocabManifold.edge_rotor()`, an operator constructor living on the vocabulary. It relocates operator construction to `algebra/rotor.py::word_transition_rotor` and fixes the layer contract: *vocab stores points, algebra builds operators*.

So the stack is: **one claim (no frame), one guard (the versor invariant), one layer contract (operators live in algebra)**. None of the three is assessable alone — ADR-0001's invariant is only meaningful as ADR-0003's enforcement, and ADR-0004's layer split is only meaningful as ADR-0003's "rotors are operators, not a frame" made structural. This is exactly the case the Tier A dossier format exists for: §3 finds a defect that is invisible in any of the three cards taken singly.

Not a phased family — three distinct ADRs, no `a/b/c` suffixes, no supersession among them.

## 1. Stack-level claim

> **CORE's vocabulary stores algebraically-valid Cl(4,1) versors and nothing else; meaning is located by a relational CGA inner-product lookup rather than by position in any coordinate frame; and every transformation between such states is constructed by a general rotor operator owned by `algebra/`.**

Two parts of that sentence are falsifiable in the FA-1 sense. Both were measured in this audit.

### Claim A — the lookup is relational, not positional (ADR-0003 §Decision)

- **Pre-registered criterion.** Stated here *before* the measurement was run in this session, and deliberately the **weakest** test ADR-0003's own language implies — not a bar invented to fail it. If `nearest()` is a relational proximity operator over stored word-versors, then at minimum:
  1. **Identity recall.** `nearest(v_k)` must return `k` for a stored surface `v_k` — a lookup that cannot find a word from its own coordinate is not locating anything.
  2. **Query dependence.** The returned index must *vary* with the query field state. A constant function is not a lookup.
- **Measurement performed.** Fresh, this session, at `cbfc8ccb`, against the real compiled six-pack mount (`evals.logos.repaired_ground.LOGOS_MOUNT`, 353 surfaces, loaded through the production `packs.compiler.load_mounted_packs`, unrepaired):

  | Probe | Result |
  |---|---|
  | Identity recall, all 353 stored surfaces | **350 of 353 return a different word**; 23 distinct winners total; index 346 wins 201 of 353 |
  | 300 independent random closed unit-versor field states, full mount | **1 distinct winner in 300 queries** — always `καρδία` (idx 346) |
  | 300 independent random field states, English-restricted (`indices_for_language('en')`, 279 candidates — the exact call `generate/articulation.py:42` makes on the live path) | **1 distinct winner in 300 queries** — always `thought` (idx 210) |
  | Why | `cga_inner(v_i, v_i)` over stored surfaces ranges **−2.011 … 17.739**. The winner is exactly `argmax_i cga_inner(v_i, v_i)`: 346 = `καρδία` (17.739) globally, 210 = `thought` (14.362) among English. `argmax_i cga_inner(F, v_i)` is dominated by the entry's own metric self-norm, not by its relation to `F`. |
  | Control — is the ADR-0001 invariant itself broken? | **No.** Stored unit-versor residual across all 353: max `9.572e-07`, mean `1.121e-07`. Zero surfaces exceed even the stricter 1e-6 figure. The invariant holds perfectly. |

- **Verdict: NO-GO.** The lookup ADR-0003 offers as the replacement for a coordinate frame is, on the real serving manifold, a **constant function of the query**. It is not relational, not positional, and not a proximity measure of any kind — it is `argmax` of an indefinite bilinear form whose spread across entries (−2.01 … 17.74) swamps the query term entirely. Crucially, **this is not an ADR-0001 failure** (the invariant is exactly satisfied) — it is the seam *between* ADR-0001 and ADR-0003, which §3 develops.

  **Honest scope of the NO-GO.** On the `generate/stream.py` path `nearest` is called with `candidate_indices` narrowed by the ADR-0022/0024 admissibility region, which masks the effect where the region is small. On the `generate/articulation.py` → `chat/runtime.py` path the only narrowing is *the whole output language*, so the effect is unmasked on live serving. Either way the sabotage reading is the same and is worse than "decoration": if the admissibility region is doing the selecting, the geometry contributes nothing; if it is not, the geometry returns one word.

### Claim B — the rotor is the general transformation operator (ADR-0004)

- **Pre-registered criterion.** If `algebra/rotor.py` genuinely owns transformation construction, then every site in the codebase that moves one versor toward another should route through it, and no site should carry its own narrower version.
- **Measurement performed / already available.** Adopted from G-25 and re-verified by fresh `rg` at `cbfc8ccb`; extended by this audit to two further sites (AA-A1-5).
- **Verdict: partial NO-GO.** `word_transition_rotor` (the ADR's named artifact) is genuinely general and genuinely used everywhere — five independent production consumers. Its *fractional* companion `rotor_power`, which is the operator three of the four duplicate sites actually needed, is used by four production sites and reinvented (badly, and in one case destructively) at three others. See §7 of the ADR-0004 card.

---

## 2. Per-ADR sections

### ADR-0001 — VocabManifold Versor Invariant

**Audit ID (if a numbering collision):** none | **Family (if phased):** n/a
**Zone / stack:** M0 `L0-algebra` (enforced in M1 `vocab-manifold`) / stack A1 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12 (commit `bd423e4`)
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** enforce the Cl(4,1) versor grade-norm condition at insertion time in `VocabManifold.add()` — the scalar part of `V · reverse(V)` must be within `0.95 ≤ |·| ≤ 1.05`, raising `ValueError` otherwise — so that no raw coordinate vector from an external embedding model can enter the vocabulary through the back door.
- **Alternatives explicitly rejected:** (a) soft warning instead of hard raise — "a warning that can be ignored is not an invariant"; (b) silent normalization on insert — "hides the documentation at the point of failure".
- **Artifacts the ADR claims will exist:**
  - `VocabManifold` storing word representations as Cl(4,1) multivectors
  - `VocabManifold.add()` performing the check at insertion
  - the literal check `grade_norm = float(geometric_product(v, reverse(v))[0])` with band `0.95 ≤ |grade_norm| ≤ 1.05`
  - `normalize_to_versor()` as the caller-facing lift for external representations
  - `VocabManifold.nearest()` returning only valid CGA points
  - "exact CGA inner product nearest lookup … without approximate nearest neighbor drift" (§Governance)
  - `versor_condition(F) < 1e-6` "for all vocabulary representations" (§Governance)
  - governance link to `ADR-0225-adr-corpus-hygiene.md`

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `VocabManifold` class | yes | `vocab/manifold.py:68` | 301 lines, single class, stores `list[str]` + `list[np.ndarray]` shape (32,) |
| check at insertion in `add()` | yes | `vocab/manifold.py:111` → `_assert_manifold_versor` at `vocab/manifold.py:53-65` | Also enforced on `update()` (`:193`) — a *strengthening* the ADR never mentions |
| literal `[0]`-scalar check, band 0.95–1.05 | **no** | — | Replaced by `versor_unit_residual(v, allow_negative=True) > 1e-5` (`vocab/manifold.py:49,55`; definition `algebra/versor.py:189-199`). The full multivector residual, not the scalar; tolerance 5e-2 → 1e-5. **Strictly stronger, and the ADR text was never amended.** |
| `normalize_to_versor()` as the caller lift | **contradicted** | `algebra/versor.py:84`; doctrine at `vocab/manifold.py:100` and `tests/test_architectural_invariants.py:44-49,192-235` | Ratified doctrine INV-02 now makes `normalize_to_versor` **gate-only** (`ingest/gate.py` alone, AST-pinned); construction sites must use `unitize_versor`. The module docstring says so explicitly: *"Do not call `normalize_to_versor()` directly; that function is reserved for the injection gate."* ADR-0001 instructs the opposite. |
| `nearest()` returns valid CGA points | **no** | `vocab/manifold.py:261-298` | Stored entries are unit versors, which are **never** null CGA points. Measured: `is_null(v)=False`, `cga_inner(v,v)=4.45` for a compiled surface; a genuine `embed_point([1,2,3])` has `versor_condition = 1.0` and would be **rejected** by `add()`. See AA-A1-2. |
| exact CGA nearest lookup, no ANN | yes (no ANN) / **no** (not a lookup) | `vocab/manifold.py:289-298`, `algebra/backend.py:146` | No ANN index exists — that half is true and pinned (`tests/test_doctrine_prohibitions.py`). But the scan is `argmax cga_inner`, measured query-independent (§1). |
| `versor_condition(F) < 1e-6` for vocabulary | **partial** | `vocab/manifold.py:40` `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` | Ten times looser than the figure the ADR's own §Governance, `README.md:15` and Whitepaper Invariant I all call non-negotiable. Observed max on the real mount is `9.572e-07` — inside 1e-6, but with only 4% margin, and the gate would admit ten times worse. See AA-A1-4. |
| `ADR-0225-adr-corpus-hygiene.md` | yes | `docs/adr/ADR-0225-adr-corpus-hygiene.md` | The census `stale-references` hit on this link (line 1083) is a **false positive** — the file exists. (Note there are two ADR-0225 files; a numbering collision, out of scope here.) |

**Build axis: full** — every structural artifact exists, is exercised on the live path, and the guard is *stronger* than specified. The `no` rows are drift in the ADR's prose and in one downstream consequence claim, not missing code. Decided by rows 1–3.

#### 3. Liveness / integration

- **Serving path.** `VocabManifold.add()` is called by `packs/compiler.py:350` (per-pack compile), `:399` (`_clone_manifold`) and `:552` (mounted compile) — the path `chat/runtime.py:640` takes to build the serving vocabulary. `update()` is called at `:327`, `:429`, `:617`. `insert_transient()` (`vocab/manifold.py:128`) routes through `add()`, so session-local OOV grounding is guarded too. No caller catches the `ValueError` — it is fail-closed at every callsite (verified by reading each).
- **Sabotage test.** If `_assert_manifold_versor` were stubbed to a no-op, three things would change, all observable:
  1. `tests/test_vocab_manifold_invariants.py` (4 tests, run green this session) fails — two of them exist precisely to prove the *scalar-only* check is insufficient.
  2. `packs.compiler._blend_feature_versors` would not need to exist. Per G-25 and `evals/logos/repaired_ground.py:60-79`, the overwrite *is* the escape from this guard: "a linear combination of two versors is not a versor … which is why `VocabManifold.update()` refuses one, and why returning the target verbatim became the escape."
  3. The `en_seeder` lift would be unnecessary.
  This is the rare case where the sabotage test comes back unambiguously positive: **the guard bites, and we can name what it bit.**
- **Liveness axis: live** — enforced on the production compile path, fail-closed, pinned by a running test, and with a documented instance of downstream code contorting itself to satisfy it.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | n/a | The ADR makes no hardware claim. (Cost measured elsewhere: M0 card — `versor_condition` is 0.22% of turn time.) |
| II. Semantic Rigor | **Tension** | §Consequences: "Any word returned by `nearest()` is **guaranteed to be a valid CGA point**." Pillar II: "A versor is a versor — not an approximation of one." The ADR uses *versor* and *CGA point* interchangeably; they are disjoint classes (`V·rev(V)=±1` vs `X·X=0`). Measured, not inferred — see §2 row 5. |
| III. Third Door | **Honors** | Both named alternatives are the two visible doors (warn-and-continue; normalize-silently); the ADR refuses both and installs a type-level construction contract instead. Textbook Third Door. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | §Rationale: "everything entering the vocabulary must live in that space by algebraic proof, not by convention." |
| 2. Field-State | n/a | The ADR governs admission to a store, not the form of state. |
| 3. Propagation-over-Mutation | **Honors** (weakly) | By forbidding in-place normalization the ADR keeps `add()` a pure admission test. Code goes further: `update()` is also guarded. |
| 4. Dual-Correction | **Honors** | The invariant is stated on `V · reverse(V)` — the conjugate pairing Whitepaper Axiom 4 names as the archetype. |
| 5. Reconstruction-over-Storage | **Tension** | §Governance claims the ADR "stores normalized Cl(4,1) versor points rather than raw embedding vectors." True of the object; but `algebra/versor.py::_seed_to_rotor` (the only lift for a raw array) maps a 32-component seed through **six blade angles plus the global norm** — measured: two seeds differing in 25 of 32 coordinates but agreeing on those six produce outputs differing by 4.2e-4, and every output occupies only 8 of 32 components. What is stored is not "enough structured state to reconstruct" the input; it is a rank-≈7 shadow of it. See AA-A1-8. |
| 6. Compilation-Last | **Honors** | The invariant is algebraic; the `1e-5` float tolerance is the compilation detail chosen after it. |
| 7. Reality-over-Inheritance | **Honors** | §Rationale states it directly: "governance is not a policy added later; it is a type-level contract enforced at construction." The subsequent strengthening of the check past the ADR's own text is this axiom operating correctly on the ADR itself. |

#### 5. Build fidelity — does the code match the decision?

Two divergences, in opposite directions.

- **Strengthened, unamended.** The shipped check is `versor_unit_residual(v, allow_negative=True) ≤ 1e-5` over the *full multivector*, not `0.95 ≤ |scalar| ≤ 1.05`. `tests/test_vocab_manifold_invariants.py:38` exists specifically to prove the ADR's own formula is inadequate ("Scalar grade-norm near one is insufficient when residue is non-scalar"). `update()` is guarded too, which the ADR does not mention. This is correct engineering and a stale record. Under AGENTS.md Standing Philosophy #5 — "when a record and reality diverge, that is a defect with the same severity as a wrong answer" — the record is the defect.
- **Contradicted, unamended.** §Consequences instructs callers to lift via `normalize_to_versor()`. Ratified doctrine INV-02 (AST-pinned, `tests/test_architectural_invariants.py:192`) makes that call a violation everywhere except `ingest/gate.py`. A reader following ADR-0001 literally would write code that fails the architectural-invariant suite.
- **Tolerance.** `1e-5` vs the `1e-6` the ADR's own §Governance asserts. No ADR records the relaxation.

**Build-fidelity axis: partial drift** — the mechanism is built and stronger than specified; three specific clauses of the ADR text (the check formula, the `normalize_to_versor` instruction, the 1e-6 figure) no longer describe the code, and one consequence claim ("valid CGA point") was never true of it.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** **Yes — Invariant III** ("The vocabulary manifold is a set of null vectors on the conformal horosphere") and **Invariant II** (`X · Y = -d(X,Y)²/2`, "the exact conformal distance"). ADR-0001's invariant makes null storage *impossible*: a null vector has `V·rev(V) = 0`, residual 1.0, and `add()` rejects it (verified: `versor_condition(embed_point([1,2,3])) = 1.0` ≫ 1e-5). The Whitepaper and the ADR describe two different manifolds and the code implements the ADR's. Whitepaper Invariant I (`F·reverse(F) = ±1`) is honored exactly.
- **Contradicts `Yellowpaper.md`?** No. The Yellowpaper is the formal Cl(4,1) specification and defers to the Whitepaper for axioms; nothing in it is violated.
- **Other ADRs.** No supersession. ADR-0003 §Consequences names ADR-0001 as its enforcement — consistent, and the code honors it. ADR-0004 §Consequences ("`vocab/` now imports from `algebra/` for algebraic primitives only (grade-norm check)") is accurate: `vocab/manifold.py:32-34` imports exactly `cga_inner`, `geometric_product`, `reverse`, `versor_unit_residual`. Silent overlap with the ratified normalization doctrine INV-02/INV-02b, which post-dates ADR-0001 and reverses its `normalize_to_versor` instruction without amending it.
- **Continuity axis: unreconciled contradiction** — with Whitepaper Invariants II/III on the nature of stored vocabulary objects, and with INV-02 on the caller-facing lift. Neither is a code defect; both are records that will mislead the next reasoner, which is the failure class AGENTS.md #5 names.

#### 7. Necessity / generality

1. **Necessity.** **Irreducible.** This is the strongest necessity case in the stack. Without an admission test, every downstream exactness claim (`versor_apply` closure, the 1e-6 gate, bit-exact replay) becomes conditional on caller discipline. The sabotage test (§3) returns a named, ratified consequence — the compiler's overwrite exists *because* this guard cannot be bypassed. A guard that provably deformed downstream code is the opposite of decoration.
2. **Reducibility.** Partly reducible in form, not in placement. The predicate is `algebra/versor.py::versor_unit_residual` — already an L0 primitive — and `vocab/manifold.py:43-65` adds only diagnostics and a tolerance. `algebra/rotor.py::_strict_unitize_versor` (`:41-71`) is a *third* spelling of the same fail-closed admission test with its own tolerances (`_STRICT_RESIDUE_TOL = 1e-2`). Three tolerances (`1e-5` vocab, `1e-6` runtime, `1e-2` construction/transition) for one invariant, none cross-referenced. A single `algebra.versor.assert_unit_versor(v, tol, context)` would absorb all three without changing behavior. Minor consolidation candidate.
3. **Extensibility.** The generalization already latent here is **"admission gates as algebraic predicates at named construction boundaries"** — the same shape as `ingest/gate.py:420-427` and `_close_applied_versor`. AGENTS.md's *semantic anchoring vs drift repair* bright line is the doctrine that governs all of them. Candidate pairing for `22-consolidation-report.md`: ADR-0001's vocab gate + the ADR-0243/GoldTether closure gates + `ingest/gate.py`'s post-condition, as one "algebraic admission boundary" family.

**Necessity/generality axis: irreducible** — the mechanism is load-bearing and provably bites; only its *spelling* (three tolerance constants across three modules) is a consolidation candidate, not the decision.

#### 8. Fitness / value

- **M0 layer card** (`10-layer-cards/M0-substrate.md`): closure enforced, algebra suite of 15 files running, "would-fail-if-absent: **yes**". Adopted.
- **Direct measurement, this session:** all 353 surfaces of the real six-pack mount satisfy the invariant with max residual `9.572e-07`. The guard is not merely present, it is *met* by the production compiler — meaning the compiler was written to satisfy it, which is the value.
- **G-25 (ratified):** the guard's refusal of a linear blend is what forced the compiler's escape into an overwrite — evidence the guard has teeth strong enough to shape the layer above it, and simultaneously evidence that a guard without a *sanctioned* alternative operation invites a worse one.
- **Tests:** `tests/test_vocab_manifold_invariants.py` (4), `tests/test_versor_closure.py`, `tests/test_architectural_invariants.py` INV-02/INV-02b/INV-03. Run green this session (66 passed across the stack's five files).
- **No evidence found** that ADR-0001's *stated purpose* — keeping external embeddings out — was ever achieved: `packs/en_seeder.py` lifts GloVe-6B-50d through `construction_seed_versor` and satisfies the invariant (AA-A1-8).

**Fitness axis: fit, with a named purpose gap** — the invariant is enforced, measured, pinned, and demonstrably load-bearing (`10-layer-cards/M0-substrate.md`; direct measurement at `cbfc8ccb`; `tests/test_vocab_manifold_invariants.py`); its stated anti-embedding purpose is not achieved (`packs/en_seeder.py:44,224,240`).

#### 9. Findings raised

- **AA-A1-1** 🔴 — `nearest()` is query-independent on the real serving manifold (300/300 random field states → one word), and 350/353 stored surfaces fail identity recall; the ADR's §Consequences claim "trust in the vocabulary is absolute" does not survive it. Supported by §1 and §2 row 5.
- **AA-A1-2** 🔴 — vocabulary entries are unit versors, not null CGA points; ADR-0001 §Consequences and Whitepaper Invariants II/III both assert otherwise, and a genuine CGA point would be *rejected* by `add()`. Supported by §2 row 5, §6.
- **AA-A1-3** 🟡 — ADR-0001's decision code block and its `normalize_to_versor()` instruction are both stale against the shipped code and against ratified doctrine INV-02. Supported by §2 rows 3–4, §5.
- **AA-A1-4** 🟡 — vocab tolerance is `1e-5`, ten times looser than the `<1e-6` invariant asserted in the ADR's own §Governance, `README.md:15` and Whitepaper Invariant I; observed max is `9.572e-07`, 4% of margin. Supported by §2 row 7.
- **AA-A1-8** 🟡 — `packs/en_seeder.py` lifts GloVe embeddings into the manifold, satisfying ADR-0001's letter and defeating its stated purpose; the lift's own docstring describes a projection the code does not build, and the seed map is a rank-≈7 bottleneck. Supported by §4 (Axiom 5), §8.

#### 10. Evidence sources actually consulted

Read in full: `docs/adr/ADR-0001-vocab-layer-invariants.md`, `vocab/manifold.py` (301 lines), `algebra/versor.py` (204 lines), `tests/test_vocab_manifold_invariants.py`. Read in part: `algebra/cga.py`, `algebra/backend.py`, `packs/compiler.py`, `packs/en_seeder.py`, `ingest/gate.py:403-428`, `tests/test_architectural_invariants.py:14-70,192-235`, `docs/Whitepaper.md` §III/§V, `README.md`. Greps: `VocabManifold`, `normalize_to_versor`, `unitize_versor`, `construction_seed_versor`, `versor_unit_residual`, `manifold.add|update`, `cosine`. Executed: `pytest` over five stack test files (66 passed); five Python probes against the live compiled manifold (residual census, null test, self-inner spread, identity recall, random-query recall). Registers: `30-gap-register.md`, `31-hindrance-audit.md`, `10-layer-cards/M0-substrate.md`, `docs/census/cbfc8ccb…/*.jsonl`.

---

### ADR-0003 — Coordinate System Dissolution

**Audit ID (if a numbering collision):** none | **Family (if phased):** n/a
**Zone / stack:** M0 `L0-algebra` (claim ranges over M1 `vocab-manifold` and `L1-field`) / stack A1 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** the architecture **dissolves the need for an explicit coordinate system** through the field-state model rather than by adopting a better coordinate system. Words are stored as versors, but meaning is a "pressure pattern across a relational field", the `FieldState` is "a distribution, not a point", lookup is "CGA inner product (relational), not distance in a coordinate frame (positional)", and rotors survive as operators in `algebra/rotor.py` applied *to* field states rather than as the frame that defines where things are.
- **Alternatives explicitly rejected:** (a) keep the rotor frame and improve numerical stability — "the frame is the wrong abstraction, not just an unstable one"; (b) hyperbolic/Poincaré embedding — "still a coordinate system"; (c) pure transformer-style embedding with cosine similarity — "precisely what the field-state model supersedes".
- **Artifacts the ADR claims will exist:**
  - `VocabManifold` storing versors in Cl(4,1)
  - `field/gate.py` producing a `FieldState`
  - `FieldState` as a distribution rather than a point
  - lookup by CGA inner product, no cosine, no Euclidean distance, no frame
  - `algebra/rotor.py` holding rotors as operators applied to field states
  - "No component outside `algebra/` needs to know about rotor composition or frame maintenance"
  - §Consequences watch item: `vocab/` must not store flat positional vectors (delegated to ADR-0001)

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `VocabManifold` storing Cl(4,1) versors | yes | `vocab/manifold.py:68-71` | Verified; see ADR-0001 card |
| `field/gate.py` | **no** | — | Never existed in this repo. The gate is `ingest/gate.py:403`. Confirmed by census `stale-references.jsonl:1165` (and `:1116` for the same error in `SESSION-2026-05-12.md`). |
| `FieldState` is "a distribution, not a point" | **no** | `field/state.py:109-116` | `FieldState` is `F: np.ndarray` shape (32,) — a single point on the versor manifold — plus `node: int`, commented *"current node index in the vocabulary manifold"*. A scalar index into the vocabulary is a position. Whitepaper Axiom 2 concedes the object: "The CORE field state is a **single multivector** in Cl(4,1)". |
| lookup by CGA inner product, no cosine/ANN | yes (prohibition) / **no** (as a lookup) | `vocab/manifold.py:289-298`; `algebra/cga.py:69-76`; pins in `tests/test_doctrine_prohibitions.py` | The prohibition is real, pinned and honored — no cosine ranker, no ANN, AST-enforced. The *positive* claim fails: measured query-independent (§1). |
| relational, not "distance in a coordinate frame" | **no** | `vocab/manifold.py:271-272` | The module's own docstring collapses the distinction the ADR draws: *"`cga_inner(X, Y) = -d^2 / 2` for null vectors: maximizing = minimizing distance."* And the identity does not even hold here, because stored entries are not null (ADR-0001 card §2 row 5). |
| `algebra/rotor.py` with rotors as operators | yes | `algebra/rotor.py` (318 lines) | `word_transition_rotor`, `rotor_power`, `make_rotor_from_angle`. See ADR-0004 card. |
| "no component outside `algebra/` needs to know rotor composition" | **no** | `session/context.py:14,221,228`; `generate/stream.py:20,180,212`; `core/physics/goldtether.py:28,568`; `core/physics/dynamic_manifold.py:29,862`; `core/physics/cognitive_lifecycle.py:72,366` | Five production modules outside `algebra/` construct and compose rotors. Note ADR-0004 §Consequences *explicitly blesses* this ("`algebra.word_transition_rotor(A, B)` at a callsite in `field/` or `generate/`"), so the two ADRs disagree — see §3 of this dossier. |
| `vocab/` must not become a coordinate frame | **defeated one layer up** | `packs/compiler.py:228` `_entry_to_coordinate`; `:71` `_FEATURE_COMPONENTS = (6, 7, 9, 10, 12, 14)` | Each surface is built as a product of rotors in **six fixed bivector planes**, plane and sign chosen by SHA-256 of the feature name (`_hash_to_blade`, `_feature_sign`). Measured on the 353-surface mount: **8 of 32 components ever non-zero** — `[0, 6, 7, 9, 10, 12, 14, 27]`. That is a six-axis coordinate system with hash-assigned axes. |

**Build axis: partial** — the *negative* half of the decision (no cosine, no ANN, no external frame library, rotors relocated to `algebra/`) is fully built and AST-pinned. The *positive* half (field-as-distribution, relational lookup, no frame) is not: `FieldState` is a point plus an index, the lookup is a constant function, and a six-plane hash-addressed frame was rebuilt one layer above `vocab/`. Decided by rows 3, 5, 8.

#### 3. Liveness / integration

- **Serving path.** The claim is architectural, so liveness means: is the *lookup rule* the ADR names as the frame's replacement actually the thing deciding? Traced: `chat/runtime.py:104` → `generate/articulation.py:42` `_resolve_slot` → `vocab.nearest(versor, candidate_indices=indices_for_language(lang))`, and `generate/stream.py:66,104,113` → `vocab.nearest(F_voiced, candidate_indices=<admissibility region>)`. Both are live. So the mechanism is reached.
- **Sabotage test.** Two sabotages, and the pair is the finding:
  - *Remove the CGA inner product and pick the largest-self-norm candidate in the region.* **Nothing would change** on the articulation path — measured: 300/300 random field states already return the argmax-self-norm word (`thought` among English candidates). The query term is inert.
  - *Remove `cga_inner` entirely and pick the first admissible candidate.* On `generate/stream.py`, output would change — but only because `nearest`'s tie-break ordering is load-bearing (`vocab/manifold.py:286-288` documents that ADR-0024 depends on it). That is iteration order deciding, not geometry.
  Under the charter's own rule — "if it would look identical, the claim is decoration" — the relational-lookup claim is **decoration on the articulation path**, and on the stream path the deciding structure is the admissibility region, not the field state.
- **Liveness axis: wired-but-unreached** — the code path executes on every turn, and the *decision it is supposed to make* is made elsewhere. This is the precise label for a mechanism that runs and does not decide. (Consistent with, and an independent instance of, `30-gap-register.md` G-24's "geometry participates in exactly two cognitive mechanisms … both stranded".)

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | n/a | No hardware claim. (The M0 card notes the resulting `cga_inner` scan is ~73% of turn time at ~33,986 calls/turn — a cost this decision creates but does not discuss.) |
| II. Semantic Rigor | **Violates** | §Decision: "The `FieldState` … is a distribution, not a point." Pillar II: "Every term used in this system has one precise, non-negotiable meaning." A single 32-component multivector is called a *distribution* in the ADR and a *single multivector* in Whitepaper Axiom 2, and `field/state.py:111` carries an explicit `node` index. The same clause also opposes "relational" to "distance" while the implementing module's docstring equates them (`vocab/manifold.py:271`). Two terms, two meanings each, in the load-bearing sentence of the ADR. |
| III. Third Door | **Honors** | Three doors named and refused (better frame, hyperbolic frame, transformer embedding); the ADR takes none. The refusals are honored in code and AST-pinned (`tests/test_doctrine_prohibitions.py`, `tests/test_adr_0241_sensorium_wave_feed.py:161-196`). Whatever else is true, CORE did not take the offered doors. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** (as written) | §Rationale: "the intrinsic space is Cl(4,1) with CGA metric. The geometry is *algebraic*, not *coordinatized*." Consistent with Axiom 1's text. Contradicted by build, not by design. |
| 2. Field-State | **Tension** | §Rationale claims Field-State. Whitepaper Axiom 2 itself calls the field state "a single multivector … not a list of embeddings", so the ADR is not inventing the usage — but "distribution, not a point" is a stronger claim than the Whitepaper makes, and the code supports the Whitepaper's version. |
| 3. Propagation-over-Mutation | **Honors** | "Propagation through field defines relationships" (§Rationale table). Implemented: `field/propagate.py`, `versor_apply` sandwich only. |
| 4. Dual-Correction | n/a | Not addressed by this ADR (ADR-0004 picks it up). |
| 5. Reconstruction-over-Storage | **Honors** | Storing versors and reconstructing proximity relationally is the axiom's shape, whatever the measured outcome. |
| 6. Compilation-Last | **Honors** | §Rationale: "rotors are implementation targets chosen after the representation is defined, not the frame the representation is built on." Honored: `algebra/backend.py` chooses Python/Rust after the algebra is fixed. |
| 7. Reality-over-Inheritance | **Honors, and now applies to itself** | The ADR retires the predecessor's rotor-vocabulary frame on structural merit. The same axiom is what makes §1's NO-GO a legitimate reopening rather than an attack: "no abstraction is sacred". |

#### 5. Build fidelity — does the code match the decision?

Divergences, in decreasing order of consequence:

1. **The frame was rebuilt one layer up.** ADR-0003 §Consequences predicted the failure mode ("`vocab/` is the most likely place for the coordinate frame to quietly re-emerge") and guarded `vocab/`. It re-emerged in `packs/`, which *writes* `vocab/`: `_entry_to_coordinate` (the function name is the confession) composes rotors in six hash-selected bivector planes. Measured occupancy: 8 of 32 components on the real mount. Every entry passes ADR-0001's gate, so the guard cannot see it — the guard tests *algebraic validity*, not *frame-freedom*, and those are different properties.
2. **The lookup does not do what the decision says it does.** §1: query-independent.
3. **`FieldState` is a point with an index**, not a distribution (`field/state.py:110-111`).
4. **Two stale paths in the ADR text** — `field/gate.py` and `core_logos/rotor_vocabulary.py` (the latter is a predecessor-repo path; acceptable as history, but the census flags it and a reader cannot tell which of the two is which).
5. **The "no component outside `algebra/`" consequence is false** and was superseded by ADR-0004 without either ADR noting it.

**Build-fidelity axis: contradicts** — not on the prohibitions (those hold exactly), but on the decision's positive content. The build satisfies "we did not use anyone else's coordinate system" and fails "there is no coordinate system."

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** **Tension, not contradiction, on Axiom 2** — the Whitepaper's own gloss ("a single multivector … not a list of embeddings") supports the code, so the divergence is ADR-0003 over-claiming relative to its own charter rather than defying it. **Contradicts Invariants II and III** in the same way ADR-0001 does: both presuppose null vectors on the conformal horosphere and the exact identity `X·Y = −d²/2`, which does not hold for the objects `VocabManifold` stores. Invariant III's `next_token = argmin_w d_CGA(F, v_w)` is the sentence §1 measured as a constant function.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs.** ADR-0004 `Implements:` ADR-0003 and is the direct child — but ADR-0004 §Consequences blesses operator construction at callsites in `field/` and `generate/`, which contradicts ADR-0003 §Consequences ("No component outside `algebra/` needs to know about rotor composition"). Neither amends the other; the code follows ADR-0004. ADR-0001 is named by ADR-0003 as its enforcement and does enforce — but enforces a different property than the one ADR-0003 needs (§3 of this dossier). Downstream, ADR-0022/0024/0025 (admissibility) build the machinery that in practice decides what `nearest` was supposed to decide — a silent overlap worth a cascade-check.
- **Continuity axis: unreconciled contradiction** — with Whitepaper Invariants II/III, and internally with ADR-0004 on the "outside `algebra/`" clause.

#### 7. Necessity / generality

1. **Necessity.** The *prohibitions* are irreducible and are the ADR's real content: no cosine, no ANN, no external embedding frame, no Poincaré ball. They are AST-pinned, they hold, and removing them would immediately change the system's class. The *positive* mechanism (relational lookup as the frame's replacement) is, as measured, something the system could lose today without losing capability — because the admissibility region and the reader are already deciding. That is the honest split.
2. **Reducibility.** ADR-0003 introduces no operator of its own; it is a *constraint document*. Everything it points at (`cga_inner`, `VocabManifold`, `algebra/rotor.py`) already exists at L0. So it is not reducible to another operator — it is reducible to a **policy**, and the policy is the durable part. This is a genuine and slightly unusual result: the ADR's value is entirely in what it forbids.
3. **Extensibility.** The generalizable object here is the **prohibition register itself** — "no cosine / no ANN / no external frame" is already enforced by `tests/test_doctrine_prohibitions.py` and duplicated in at least four module docstrings (`algebra/cga.py:18`, `vocab/manifold.py:5`, `core/physics/linguistic_readback.py:14`, `core/physics/sensorium_wave_feed.py:113`) and in `workbench-ui/src/app/RightInspector.tsx:591`. Candidate pairing for `22-consolidation-report.md`: ADR-0003's prohibitions + ADR-0019 (exact vault recall) + ADR-0241's sensorium bans, as one "exactness prohibitions" family with a single register and a single pin.

**Necessity/generality axis: generalization-candidate** — the prohibition half should be lifted into a single enforced register; the positive half (relational lookup as the frame replacement) is a **falsified design claim** (§1), not a mechanism to consolidate.

#### 8. Fitness / value

- **Negative, and ratified.** `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` §6 records the standing register of geometric-substrate verdicts: field wedge **C3-decoration**; relational-operator ablation **identical-to-baseline**; ADR-0252 §5 **NO-GO**; cross-language holonomy **NO-GO on a clean ground**. Its own reading: *"this substrate's value has not been demonstrated in reasoning — while its value in representation (exact recall, versor conditioning, determinism) is measured and holds."* ADR-0003 is the ADR that stakes the *representation* claim, so that sentence is half in its favour and half against.
- **G-24** (`30-gap-register.md`): "geometry participates in exactly two cognitive mechanisms — salience→attention (bypassed by every licensed lane) and `relation_compiler`'s Hamiltonian ground-state solver (off-serving)". Independent corroboration of the `wired-but-unreached` call in §3.
- **This session's measurement** adds the sharpest single data point available: on the live articulation path the CGA inner product's query term is inert.
- **Positive:** the prohibitions are real, held for fourteen months of repository history, and are pinned. No ANN index, no cosine ranker, no embedding backbone exists anywhere in the tree — verified by grep and by `tests/test_doctrine_prohibitions.py:95-119`, which specifically catches a *hand-rolled* cosine function, not just the library import.

**Fitness axis: mixed — the prohibition half is fit and pinned (`tests/test_doctrine_prohibitions.py`); the positive half has no supporting evidence and one direct refutation** (§1 measurement at `cbfc8ccb`; corroborated by G-24 and the FA-1 verdict's four-negative register).

#### 9. Findings raised

- **AA-A1-1** 🔴 (shared with ADR-0001) — the relational lookup is a constant function of the query on the live articulation path. Supported by §1, §3.
- **AA-A1-2** 🔴 (shared) — Whitepaper Invariants II/III presuppose null CGA points; the vocabulary stores unit versors, so `X·Y = −d²/2` never applies. Supported by §6.
- **AA-A1-7** 🟡 — ADR-0003's own watch item came true one layer above the layer it guarded: `packs/compiler.py::_entry_to_coordinate` builds a six-axis, SHA-256-addressed coordinate frame; the mounted manifold occupies 8 of 32 components. Supported by §2 row 8, §5.1.
- **AA-A1-9** 🟢 — two stale paths inside ADR-0003 (`field/gate.py` never existed; `core_logos/rotor_vocabulary.py` is a predecessor-repo path not marked as such). Supported by §2 row 2, census `stale-references.jsonl:1164-1165`.
- **AA-A1-13** 🟡 — ADR-0003 §Consequences ("no component outside `algebra/` needs to know about rotor composition") is contradicted by its own child ADR-0004 §Consequences and by five production modules; neither ADR reconciles it. Supported by §2 row 7, §6.

#### 10. Evidence sources actually consulted

Read in full: `docs/adr/ADR-0003-coordinate-system-dissolution.md`, `docs/adr/SESSION-2026-05-12.md` §20:39–20:51, `algebra/rotor.py`, `field/state.py:1-170`. Read in part: `algebra/cga.py:1-95`, `field/operators.py:1-175`, `packs/compiler.py:95-145,228-290,411-432`, `generate/articulation.py:21-47`, `generate/stream.py:60-120`, `docs/Whitepaper.md` §III/§V, `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` §§1,5,6. Greps: `cosine`, `slerp|lerp|blend|interpolat`, `geometric_product(geometric_product(`, `np.cos(`, `.nearest(`, `field.operators`, `FieldState`. Executed: five probes against the live compiled manifold (component occupancy, null test, self-inner spread, identity recall, 300-query random-field recall, both full-mount and English-restricted). Registers: `30-gap-register.md` G-24/G-25, `31-hindrance-audit.md`, `docs/census/cbfc8ccb…/stale-references.jsonl`.

---

### ADR-0004 — Rotor as Operator, Not Vocabulary Property

**Audit ID (if a numbering collision):** none | **Family (if phased):** n/a
**Zone / stack:** M0 `L0-algebra` / stack A1 | **Tier:** A
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-12 (commit `bd423e4`, `Implements:` ADR-0003)
**Card author:** Opus 5 | **`verified_at` SHA:** `cbfc8ccb`

#### 1. Content summary

- **Decision made:** (1) remove `edge_rotor()` from `VocabManifold`; (2) create `algebra/rotor.py` with `word_transition_rotor(A, B)` as a free function; (3) export it from `algebra/__init__.py`. `VocabManifold`'s contract becomes strictly "store word-versor pairs, support relational lookup by CGA inner product. Nothing else."
- **Alternatives explicitly rejected:** (a) keep `edge_rotor()` with a deprecation warning — "convenience methods that violate layer contracts tend to be the ones that get used"; (b) move the operators to a `VocabOps` class inside `vocab/` — "the layer boundary is the constraint, not the class boundary".
- **Artifacts the ADR claims will exist:**
  - `edge_rotor()` **absent** from `VocabManifold`
  - `algebra/rotor.py`
  - `word_transition_rotor(A, B)` as a free function
  - export from `algebra/__init__.py`
  - `vocab/` importing from `algebra/` for algebraic primitives only, never constructing operators
  - **Forbidden:** any method on `VocabManifold` constructing a rotor, versor product, or transformation

#### 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `edge_rotor()` absent from `VocabManifold` | yes | — | Zero occurrences anywhere in the tree outside `docs/adr/ADR-0004…` and `docs/adr/SESSION-2026-05-12.md`. Cleanly removed, not deprecated. |
| `algebra/rotor.py` | yes | `algebra/rotor.py` (318 lines) | Grew well past the ADR: also `make_rotor_from_angle` (`:74`), `rotor_power` (`:85`) with the exact invariant-split general case (`:257`), `_strict_unitize_versor` (`:41`) |
| `word_transition_rotor(A, B)` free function | yes | `algebra/rotor.py:285-317` | `R = B · reverse(A)`, fail-closed on near-zero, non-closed, non-positive, and `condition > 1e-4`. Explicitly refuses to synthesize a fallback rotor. |
| export from `algebra/__init__.py` | yes | `algebra/__init__.py:19` | `from .rotor import word_transition_rotor` — note `rotor_power` and `make_rotor_from_angle` are **not** exported there; consumers import from `algebra.rotor` directly |
| `vocab/` imports algebraic primitives only | yes | `vocab/manifold.py:32-34` | `cga_inner`, `geometric_product`, `reverse`, `versor_unit_residual`. No operator construction. The module docstring (`:16-18`) restates the contract and points callers at `algebra.rotor.word_transition_rotor`. |
| Forbidden: rotor construction on `VocabManifold` | yes (state) / **no** (enforcement) | `vocab/manifold.py` | Compliant today, verified by reading all 301 lines. **No pin enforces it** — contrast INV-02/INV-02b, which AST-walk the tree for `normalize_to_versor`/`unitize_versor`. See AA-A1-11. |
| — *beyond the ADR:* production consumers of `word_transition_rotor` | yes, 5 | `session/context.py:221`, `generate/stream.py:180,200,453,532,620`, `core/physics/goldtether.py:568`, `core/physics/dynamic_manifold.py:862`, `core/physics/cognitive_lifecycle.py:366` | Plus tests: `test_transition_rotor.py`, `test_versor_closure.py`, `test_rotor_admissibility.py`, `test_rotor_power.py`, `test_stage2_physics_hardening.py`, `test_adr_0242_topological_quarantine.py` |

**Build axis: full** — all three decision items shipped, the removal is total, and the module outgrew its brief in the right direction. Decided by rows 1–4.

#### 3. Liveness / integration

- **Serving path.** `generate/stream.py:620` `V = word_transition_rotor(A, B)` is the per-token transition on the generation path; `:212` `rotor_power(V, weight)` scales it. `session/context.py:221-231` `_anchor_pull` runs on every turn. `core/physics/cognitive_lifecycle.py:366` is the ADR-0243 modality-transition path. All live.
- **Sabotage test.** Stub `word_transition_rotor` to return the identity and generation stops moving — `generate/stream.py:5` states the loop is *"F ← versor_apply(V, F) where V = word_transition_rotor(A, B)"*, so the field would never advance and every step would return the same word. Stub `rotor_power` to return `R` and the session anchor pull becomes a hard jump to the anchor (`session/context.py:210` documents that the α=0.05 mildness is the point), and `generate/stream.py:212`'s weighting collapses. Neither is decoration; both would be immediately observable.
- **A stronger form of the test is already in the record.** `algebra/rotor.py:104-107` documents that `rotor_power` *used* to return the identity for non-simple rotors — "an approximation where exactness was available, which silently collapsed geodesic interpolation to a no-op. That corner is now closed." The sabotage was accidentally performed, observed, and repaired. That is the best possible liveness evidence.
- **Liveness axis: live** — reached on generation, session, and physics paths; multiple independent consumers; a historical accidental-sabotage event with a recorded observable consequence.

#### 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | n/a | No hardware claim. (`rotor_power`'s closed forms avoid iteration entirely — arguably sympathetic, but not the ADR's argument.) |
| II. Semantic Rigor | **Honors** | §Rationale draws the map/territory line precisely: "A rotor between two words is not a property of those words in isolation — it is a description of a *transformation being applied at a moment in the field*." One term, one meaning. The implementation extends the rigor: `word_transition_rotor` fails loudly rather than fabricating a fallback (`algebra/rotor.py:41-50, 292-294`). |
| III. Third Door | **Honors** | Both offered doors — deprecate-in-place, and relocate-the-class-not-the-layer — are named and refused for a stated structural reason. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | **Honors** | The relocation is justified by what a rotor *is* in the algebra, not by code organization taste. |
| 2. Field-State | **Honors** | §Rationale: "operators live in `algebra/`; relational structure lives in `field/`; the vocabulary is a lookup structure, not an operator store." |
| 3. Propagation-over-Mutation | **Honors** | The rotor is the propagation operator; `generate/stream.py:5` makes it the only field transition. |
| 4. Dual-Correction | **Honors** | §Rationale invokes it by name — forward operator and corrective counterpart "should both originate in `algebra/`". Built: `reverse` is co-located, and `rotor_power(R, α)` + `rotor_power(R, 1−α)` compose exactly. |
| 5. Reconstruction-over-Storage | **Honors** | The rotor is *constructed on demand* from the two endpoints rather than stored as an edge — the axiom's exact shape, and the reason removing `edge_rotor()` was right on more than layering grounds. |
| 6. Compilation-Last | **Honors** | The closed forms (`_simple_rotor_power`, `_general_rotor_power`) are derived from the algebra, "no iteration, no approximation, and no external library" (`:93-94`). |
| 7. Reality-over-Inheritance | **Honors** | A working, mathematically-correct method was deleted rather than deprecated because it sat in the wrong layer. This is the axiom's cleanest instance in the corpus. |

**This is the only ADR in the stack with no design-fidelity tension anywhere.**

#### 5. Build fidelity — does the code match the decision?

Matches, and exceeds. Three notes:

- **Exceeds:** `rotor_power` implements the exact fractional operator on the full Spin(4,1) group — the simple case in closed form, the non-simple case via the invariant/bivector decomposition into two commuting simple factors, and the isoclinic degenerate case separately (`algebra/rotor.py:85-282`). This is materially more general than ADR-0004 decided and is the single most reusable object in the stack.
- **Exceeds:** `word_transition_rotor` is fail-closed where the ADR's original `edge_rotor()` snippet was not (the original did `R[0] += 1.0; return normalize_to_versor(R)` — a fabricated fallback and a gate-primitive call at a construction site, both now forbidden by INV-02).
- **Under-exports:** `algebra/__init__.py:19` exports only `word_transition_rotor`. `rotor_power` and `make_rotor_from_angle` — the two operators most often reinvented downstream (§7) — are reachable only via `from algebra.rotor import …`. A discoverability gap that plausibly contributed to every duplicate in §7.

**Build-fidelity axis: matches** — the decision is implemented exactly, and the additions are in the decision's own direction.

#### 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- **Contradicts `Whitepaper.md`?** No. Whitepaper Invariant I (`F_new = V·F·reverse(V)`, "coherence is algebraically closed") is exactly what `word_transition_rotor` + `versor_apply` implement, and `rotor_power`'s docstring guarantee (`versor_condition(rotor_power(R, α)) < 1e-6` for any α) is Invariant I extended to fractional transformations.
- **Contradicts `Yellowpaper.md`?** No.
- **Other ADRs.** `Implements:` ADR-0003 — and contradicts ADR-0003 §Consequences on the "no component outside `algebra/`" clause (see ADR-0003 card §6; the contradiction is ADR-0003's error, since ADR-0004's position is the coherent one and is what shipped). ADR-0025 (rotor/frame admissibility) builds on it explicitly and correctly: `generate/rotor_admissibility.py:59` states *"Rotor construction lives in `algebra.rotor.word_transition_rotor`"* — the layer contract cited by a downstream module, which is what a healthy ADR looks like fourteen months later. ADR-0242's topological quarantine test asserts the symbol is importable and callable (`tests/test_adr_0242_topological_quarantine.py:76-79`). No supersession.
- **Continuity axis: clean** — the one contradiction in its neighbourhood is the parent ADR's, not this one's.

#### 7. Necessity / generality

**This is the stack's designated "one general mechanism" question, and the answer is: yes, and it is under-used.**

1. **Necessity.** **Irreducible.** The rotor is the only transformation Cl(4,1) admits that preserves the versor condition by construction — Whitepaper Invariant I is a statement about rotors. Removing it does not cost a feature; it costs the algebra's closure, and with it every exactness and replay guarantee above M0.
2. **Reducibility.** Nothing at L0/L1 does this under another name. `versor_apply` *applies* a rotor and does not construct one; `unitize_versor` *closes* a candidate and does not relate two states. The pair (`word_transition_rotor`, `rotor_power`) is the minimal complete construction basis: "the transformation from A to B" and "a fraction of that transformation".
3. **Extensibility — four narrower reinventions found, none of which needed to exist.** Every one implements "move `source` a fraction `strength` toward `target`", which is exactly `geometric_product(rotor_power(word_transition_rotor(source, target), strength), source)`:

   | Site | Form | State | Why it is narrower |
   |---|---|---|---|
   | `session/context.py:221-231` `_anchor_pull` | `rotor_power ∘ word_transition_rotor` + `versor_apply` | **live, correct — the reference implementation** | none; it *replaced* a `_slerp_toward` that "interpolated on S³¹ rather than on the Spin sub-manifold and required a post-hoc `unitize_versor`" (`:209-211`). The migration precedent already exists in-repo. |
   | `packs/compiler.py:129-133` `_blend_feature_versors` | `strength ≤ 0 → source; else → target` | **live, destructive** | Ignores `strength` entirely. G-25 (ratified): 53 coordinate collisions on the six-pack mount, 37 on the trilingual one; nine English question words collapsed onto one point; `דבר`/`λόγος`/`דברים`/`word` made bit-identical. Independently reproduced this session: 353 surfaces → **300 distinct coordinates**, matching FA-1's 53 exactly. |
   | `packs/compiler.py:264-285` `_alignment_nudge_rotor` | `arccos(⟨R⟩₀)` → scale θ → rebuild `cos/sin` | **dead — zero callers** | This is `_simple_rotor_power` re-derived by hand, and it is *wrong for non-simple rotors*: it flattens a two-plane rotation onto one plane with no simplicity check. `rotor_power` handles that case exactly via the invariant split (`algebra/rotor.py:257-282`). Written, superseded by the overwrite, never deleted. |
   | `field/operators.py:121-146` `_incremental_correction_rotor` | `(1−rate)·current + rate·target`, then `_unitize_f32` | **live via `core pulse`** | A linear blend leaves the versor group; the re-unitize is a repair, not a construction. Its own docstring shows the author knew `word_transition_rotor` existed ("Rather than computing the full transition rotor, which would jump … all the way to the target") and did not know `rotor_power` supplies the fraction. `GraphDiffusionOperator.forward` (`:169`) has the same blend-then-unitize shape. |

   A fifth, narrower duplicate: `packs/compiler.py:113-119` `_feature_rotor` builds `rotor[0]=cos θ; rotor[idx]=sin θ` — **exactly `algebra.rotor.make_rotor_from_angle(2θ, bivector_idx=idx)`** modulo the half-angle convention, minus the range check and the `unitize_versor`. `packs/compiler.py` imports `geometric_product`, `reverse` and `unitize_versor` from `algebra` but never `algebra.rotor`.

   A sixth pattern, lower severity: four production sites hand-roll the raw sandwich `V X rev(V)` to deliberately bypass `versor_apply`'s closure (`algebra/null_point.py:84`, `core/physics/dynamic_manifold.py:287`, `core/physics/identity_manifold.py:150`, `core/physics/cognitive_lifecycle.py:272`). Each documents its reason and each is defensible; there is simply no shared `algebra.versor.raw_sandwich` for them to call.

**Necessity/generality axis: irreducible — and the stack's confirmed general mechanism.** ADR-0004 established the layer contract for *one* operator (`word_transition_rotor`) and it held perfectly. The contract was never extended to `rotor_power`, and that is exactly where four duplicates grew — one dead, one destructive and ratified as a defect, one live in a pulse path, one a trivial duplicate of `make_rotor_from_angle`. **Consolidation cluster for `22-consolidation-report.md`:** `{algebra.rotor.rotor_power ∘ word_transition_rotor}` absorbs `packs/compiler.py::_blend_feature_versors`, `packs/compiler.py::_alignment_nudge_rotor`, `field/operators.py::_incremental_correction_rotor`, `field/operators.py::GraphDiffusionOperator.forward`; `{algebra.rotor.make_rotor_from_angle}` absorbs `packs/compiler.py::_feature_rotor`. The exact repair for the first is already written and tested at `evals/logos/repaired_ground.py:60-79` — as an eval-time monkeypatch, not in production.

#### 8. Fitness / value

- **The strongest positive fitness evidence in this stack, and it is ratified.** `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` §5.4: *"R1 (geodesic blending) removes 53 coordinate collisions from the six-pack mount and 37 from the trilingual one … A ground that keeps its distinctions is worth having whether or not holonomy is its gate."* R1 *is* ADR-0004's operator used correctly (`rotor_power ∘ word_transition_rotor`). Measured, pre-registered, and the repair is recommended independently of the NO-GO it was built to enable.
- **Reproduced this session:** the unrepaired production mount yields 300 distinct coordinates from 353 surfaces — the 53 collisions, exactly.
- **Instrumented and gated:** `evals/logos/manifold_collapse.py` + `tests/test_manifold_collapse_floor.py` (smoke suite, both directions, bit-exact).
- **Historical:** `session/context.py:209-216` records that the `rotor_power` form replaced a `_slerp_toward` requiring post-hoc closure repair, and that closure is now "preserved by construction (verified by a 100k-step measurement)" — a second independent measured win for the same operator.
- **Tests:** `tests/test_transition_rotor.py`, `tests/test_rotor_power.py`, `tests/test_rotor_power_general.py`, `tests/test_rotor_admissibility.py`, `tests/test_versor_closure.py`. Run green this session.
- **M0 layer card:** `fit`, `live-serving`. Adopted.

**Fitness axis: fit — with the clearest measured value in the stack** (FA-1 verdict §5.4: 53 + 37 coordinate collisions removed; `session/context.py`'s 100k-step closure measurement; `tests/test_manifold_collapse_floor.py` on the smoke gate).

#### 9. Findings raised

- **AA-A1-5** 🔵 — consolidation cluster: four sites reimplement "move source a fraction toward target" instead of `rotor_power ∘ word_transition_rotor`; one is dead, one is a ratified defect (G-25), one is live on the pulse path. Supported by §7.3.
- **AA-A1-6** 🔵 — `packs/compiler.py::_feature_rotor` duplicates `algebra.rotor.make_rotor_from_angle` exactly; `packs/compiler.py` imports from `algebra` but never from `algebra.rotor`. Supported by §7.3.
- **AA-A1-11** 🟡 — ADR-0004's "Forbidden: any method on `VocabManifold` that constructs a rotor" has no enforcing pin; compliance today rests on nothing, in contrast to the AST-pinned INV-02/INV-02b next door. Supported by §2 row 6.
- **AA-A1-14** 🟢 — `algebra/__init__.py` exports only `word_transition_rotor`; `rotor_power` and `make_rotor_from_angle` — the two most-reinvented operators — are not exported, a plausible contributing cause of AA-A1-5/6. Supported by §5.
- **AA-A1-15** 🔵 — four production sites hand-roll the raw sandwich `V X rev(V)` to bypass `versor_apply` closure, each with a valid documented reason and no shared primitive to call. Low-severity consolidation candidate (`algebra.versor.raw_sandwich`). Supported by §7.3.

#### 10. Evidence sources actually consulted

Read in full: `docs/adr/ADR-0004-rotor-as-operator-not-property.md`, `algebra/rotor.py` (318 lines), `algebra/__init__.py`, `evals/logos/repaired_ground.py:33-115`. Read in part: `field/operators.py:28-175`, `packs/compiler.py:95-145,228-290,411-432`, `session/context.py:205-240`, `generate/stream.py:1-30,160-220,600-625`, `core/physics/dynamic_manifold.py:275-300,525-545,855-870`, `core/physics/cognitive_lifecycle.py:260-280,325-370`, `core/physics/identity_manifold.py:140-160`, `core/physics/goldtether.py:555-572`, `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` §§1,5,6. Greps: `edge_rotor` (whole tree), `word_transition_rotor`, `rotor_power`, `make_rotor_from_angle`, `_blend_feature_versors`, `_alignment_nudge_rotor`, `_incremental_correction_rotor`, `geometric_product(geometric_product(`, `slerp|lerp|blend|interpolat`, `np.cos(`. Executed: `pytest tests/test_transition_rotor.py tests/test_rotor_power.py tests/test_versor_closure.py tests/test_manifold_collapse_floor.py tests/test_vocab_manifold_invariants.py` (66 passed); distinct-coordinate census on the production mount. Registers: `30-gap-register.md` G-25, `docs/audit/substrate-liveness-registry.md` (stale — AA-A1-10).

---

## 3. Stack-level synthesis

### Internal consistency

Two disagreements, one trivial and one structural.

**Trivial and explicit.** ADR-0003 §Consequences: *"No component outside `algebra/` needs to know about rotor composition or frame maintenance."* ADR-0004 §Consequences: *"`algebra.word_transition_rotor(A, B)` at a callsite in `field/` or `generate/` is self-documenting."* The child contradicts the parent it declares it `Implements:`. The code follows ADR-0004 (five production modules outside `algebra/` compose rotors), which is the right answer; neither ADR was amended. Recorded as AA-A1-13.

**Structural, and the reason this stack is Tier A.** ADR-0003 delegates its central risk to ADR-0001: *"`vocab/` is the most likely place for the coordinate frame to quietly re-emerge … ADR-0001 closes this specifically."* ADR-0001 accepts that job and installs `V · reverse(V) ≈ ±1`.

**The invariant ADR-0001 enforces does not bound the quantity ADR-0003's lookup depends on.** `V·rev(V) = ±1` is a statement about the *versor product* — it constrains `V` to the Spin group. `cga_inner(V, V)` is a different bilinear form (the metric-weighted self-inner), and it is *unbounded* by the versor condition. Measured on the real six-pack mount: every surface satisfies the invariant (max residual `9.572e-07`) while `cga_inner(v,v)` ranges **−2.011 … 17.739**. Because `nearest` is `argmax_i cga_inner(F, v_i)`, that 20-unit spread swamps the query term, and the lookup degenerates to `argmax_i cga_inner(v_i, v_i)` — a constant. 300 of 300 random field states return `καρδία`; 300 of 300 English-restricted return `thought`; 350 of 353 stored surfaces cannot recall themselves.

Neither ADR is wrong on its own terms. ADR-0001's guard works perfectly and guards exactly what it says. ADR-0003's lookup rule is coherent for the objects the Whitepaper describes (null vectors on the horosphere, where `X·Y = −d²/2` and `X·X = 0` uniformly). The defect is in the **seam**: the objects ADR-0001 admits are not the objects ADR-0003's rule requires, and no document notices because each ADR is internally consistent. **This is invisible in any single card and is the specific value of auditing the three as a stack.**

The missing invariant is nameable in one line: *a vocabulary entry must be normalized in the CGA metric, not only in the versor product* — i.e. `cga_inner(v,v)` must be constant across entries (or `nearest` must divide by it). Recorded as AA-A1-1; the repair belongs to a ruling, not to this audit.

### Cumulative build state

| ADR | Build | Liveness | Design fidelity | Build fidelity | Continuity | Necessity | Fitness |
|---|---|---|---|---|---|---|---|
| 0001 | full | live | 1 tension (Pillar II), 1 tension (Ax 5) | partial drift | unreconciled contradiction | irreducible | fit, purpose gap |
| 0003 | partial | wired-but-unreached | 1 violation (Pillar II), 1 tension (Ax 2) | contradicts | unreconciled contradiction | generalization-candidate | mixed |
| 0004 | full | live | clean | matches | clean | irreducible | fit |

**The arc did not stall — it split.** Everything ADR-0004 decided is built, live, correct and load-bearing. Everything ADR-0001 decided is built and enforced, with a stale record. What did not land is ADR-0003's *positive* content — the claim that a relational lookup replaces a coordinate frame. Roughly: **2.3 of 3 ADRs fully built; the missing 0.7 is one clause of one ADR, and it is the clause the other two exist to serve.**

A second pattern worth naming: **each ADR's prohibitions outperformed its constructions.** "No `edge_rotor` on the vocabulary" (total, permanent), "no raw arrays in the manifold" (enforced, pinned, bites), "no cosine, no ANN, no external frame" (AST-pinned, held fourteen months) — all three hold exactly. The affirmative claims are where the drift is. For a corpus governed by Axiom 7, that is a useful prior: CORE's ADRs are most reliable where they say *no*.

### Cumulative necessity/generality read

**One coherent generalizable mechanism, plus one policy, plus a seam.**

- **The mechanism is the rotor pair** `{word_transition_rotor, rotor_power}` — irreducible, general over the full Spin(4,1) group including the non-simple and isoclinic cases, closure-preserving by construction, and measurably valuable (53 + 37 collisions removed). ADR-0004's layer contract held for `word_transition_rotor` and was never extended to `rotor_power`; every one of the four duplicates in §7.3 needed the fraction, not the transition. **The consolidation opportunity is not to build anything — it is to route four existing callsites through an operator that already exists, is already tested, and whose replacement text is already written at `evals/logos/repaired_ground.py:60-79`.**
- **The policy is ADR-0003's prohibition register** — no cosine, no ANN, no external embedding frame. Duplicated across five module docstrings and one TypeScript file; enforced by one test. Candidate for a single register + single pin, pairing with ADR-0019 and ADR-0241.
- **The seam is not consolidatable** — AA-A1-1 needs a missing invariant, not a merged operator.

**As a stack, A1 is itself the natural top-level consolidation cluster for `22-consolidation-report.md`:** it is the L0 substrate that every later ADR's transform should reduce to. The audit instruction to "flag every later ADR that builds a bespoke rotation/transform against ADR-0004" already has four confirmed hits inside this batch's own reach, none of which is in an ADR — they are in `packs/` and `field/`, layers whose ADRs never restated the contract. **The generalizable lesson for the remaining stacks: the bespoke transforms are not where the ADRs are; they are in the modules whose ADRs are silent about the algebra.**

### Blast radius if this stack's central claim is wrong

Cascade-check performed explicitly, per the charter's requirement for every Tier A stack.

**If AA-A1-1 stands (the CGA-inner lookup does not locate), the following need re-verdicting:**

1. **Whitepaper Invariants II and III** — both are stated in terms of null vectors on the horosphere and the exact identity `X·Y = −d²/2`. Neither holds for the objects the vocabulary stores. Invariant III's `next_token = argmin_w d_CGA(F, v_w)` is the sentence measured as a constant. This is a **charter-level** correction, not an ADR-level one, and it is the highest-leverage item in this dossier. It should be routed to the same authority that amended ADR-0005/0015 after FA-1.
2. **`L2-vault` / ADR-0019 (exact vault recall)** — vault entries *are* stored as null vectors (`vault/store.py` uses `embed_point`/`is_null`/`null_project`), so `X·Y = −d²/2` genuinely applies there and the recall claim is likely **safe**. But the two stores are described in identical language throughout the corpus and the M0 card, so the distinction must be made explicit or the vault's correctness will be read as evidence for the vocabulary's. **Priority cascade-check: verify `vault/store.py` normalization independently before this dossier's finding is generalized to it.**
3. **ADR-0022 / 0024 / 0025 / 0026 (the admissibility chain)** — if `nearest` does not discriminate, the admissibility region is doing the selecting, which promotes those ADRs from "constraints on a geometric choice" to "the chooser". Their liveness verdicts stay; their *necessity* verdicts change sign, and `generate/rotor_admissibility.py`'s separation from algebra closure (ADR-0025's design note) becomes load-bearing in a way its ADR does not claim.
4. **G-24's diagnosis is strengthened, not contradicted** — "no served byte is geometric" gains a second, independent mechanism: not only is the reader a template parser, but the one geometric selection step downstream of it does not select. The perception arc's remediation plan should absorb this.
5. **M0 layer card `fitness: fit`** — survives, correctly. M0's contract is closure, exactness and replayability, all of which hold and are measured. The failure is at the M0/M1 seam (what `L0-algebra` guarantees vs what `vocab-manifold` needs), which no single card owns. Recommend the finding be mirrored into the assessment's `G`-register as a system-level gap, per the charter's mirroring rule — it is not document fidelity.
6. **FA-1's own conclusion is untouched and independently confirmed.** FA-1 measured on the *repaired* ground (geodesic blending, zero collisions) and still returned NO-GO. This dossier measures the *unrepaired* production ground and finds a distinct, upstream defect. The two are complementary, not competing: FA-1 says the encoding does not discriminate meaning; A1 says the lookup over the ground does not discriminate at all.

**If AA-A1-1 falls** (e.g. the admissibility region is always small enough that the effect never materializes on any licensed lane): AA-A1-2 (null-vs-versor), AA-A1-3, AA-A1-4, AA-A1-7 and the whole AA-A1-5 consolidation cluster stand unchanged — none depends on it.

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the parallel-audit numbering discipline; to be renumbered into the real `AA-N` sequence at rollup.

- **AA-A1-1** 🔴 **Block** — `VocabManifold.nearest()` does not locate: on the production six-pack mount, 300/300 random field states return one word (`καρδία`; `thought` when restricted to English as `generate/articulation.py:42` does), and 350/353 stored surfaces fail identity recall, because `cga_inner(v,v)` spans −2.011…17.739 while ADR-0001's invariant constrains only `V·rev(V)`. Falsifies ADR-0003 §Decision's relational-lookup claim and ADR-0001 §Consequences' "trust is absolute". Mirror into the assessment `G`-register: system-level gap, not document fidelity. *(§1, §3)*
- **AA-A1-2** 🔴 **Block** — the vocabulary stores unit versors, which are never null CGA points; ADR-0001 §Consequences ("guaranteed to be a valid CGA point"), Whitepaper Invariant II (`X·Y = −d²/2`) and Invariant III ("a set of null vectors on the conformal horosphere") all assert otherwise, and a genuine `embed_point` would be **rejected** by `add()` (`versor_condition = 1.0`). Charter-level correction. *(ADR-0001 §2/§6, ADR-0003 §6)*
- **AA-A1-3** 🟡 **Repair** — ADR-0001's decision code block (scalar-only, band 0.95–1.05) and its instruction to lift via `normalize_to_versor()` are both stale: the code enforces the full multivector residual at 1e-5, and INV-02 makes `normalize_to_versor` gate-only. A reader following ADR-0001 literally writes code that fails the architectural-invariant suite. *(ADR-0001 §2/§5)*
- **AA-A1-4** 🟡 **Repair** — `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` is ten times looser than the `<1e-6` figure asserted by ADR-0001 §Governance, `README.md:15` and Whitepaper Invariant I; observed max on the real mount is `9.572e-07`, leaving 4% margin against a gate that would admit 10×. No ADR records the relaxation. *(ADR-0001 §2)*
- **AA-A1-5** 🔵 **Consolidate** — four sites reimplement "move source a fraction toward target" instead of `rotor_power ∘ word_transition_rotor`: `packs/compiler.py::_blend_feature_versors` (live, ignores `strength`, ratified defect G-25), `packs/compiler.py::_alignment_nudge_rotor` (dead, and mathematically wrong for non-simple rotors), `field/operators.py::_incremental_correction_rotor` and `GraphDiffusionOperator.forward` (live via `core pulse`, lerp-then-repair). The correct replacement is written and tested at `evals/logos/repaired_ground.py:60-79` and lives only as an eval monkeypatch. *(ADR-0004 §7)*
- **AA-A1-6** 🔵 **Consolidate** — `packs/compiler.py::_feature_rotor` duplicates `algebra.rotor.make_rotor_from_angle` exactly (modulo half-angle), minus the range check and unitization; `packs/compiler.py` imports from `algebra` but never from `algebra.rotor`. *(ADR-0004 §7)*
- **AA-A1-7** 🟡 **Repair** — ADR-0003's own watch item came true one layer above the layer it guarded: `packs/compiler.py::_entry_to_coordinate` (the name is the confession) builds each surface from rotors in six SHA-256-selected bivector planes (`_FEATURE_COMPONENTS = (6,7,9,10,12,14)`); the 353-surface mount occupies **8 of 32 components**. ADR-0001's gate cannot see this because algebraic validity and frame-freedom are different properties. *(ADR-0003 §2/§5)*
- **AA-A1-8** 🟡 **Repair** — `packs/en_seeder.py` lifts GloVe-6B-50d into the manifold — the exact artifact ADR-0001 §Context names as the back door and ADR-0003 rejects as "the design we are replacing" — satisfying ADR-0001's letter via `construction_seed_versor` and defeating its purpose. Two supporting defects: the module docstring describes a DFT-based distance-preserving projection that `_build_projection_matrix` does not build (it is a random-Gaussian QR), and `_seed_to_rotor` passes the 32-component seed through only six blade angles plus the global norm, so the claimed monotone reflection of GloVe distance cannot hold. Off the chat serving path (reached only by `scripts/run_pulse.py`); the module's own `__main__` self-probe asserts "nearest to self should be self", which AA-A1-1 shows it is not. *(ADR-0001 §4/§8)*
- **AA-A1-9** 🟢 **Monitor** — two stale paths inside ADR-0003 (`field/gate.py`, which never existed here — the gate is `ingest/gate.py`; and `core_logos/rotor_vocabulary.py`, a predecessor-repo path not marked as historical). Confirmed by census `stale-references.jsonl:1164-1165`. The census's third hit in this stack (ADR-0001 → `ADR-0225-adr-corpus-hygiene.md`) is a **false positive** — that file exists. *(ADR-0003 §2)*
- **AA-A1-10** 🟢 **Monitor** — `docs/audit/substrate-liveness-registry.md`'s L0 symbol-consumer table is stale in three of three rows checked (claims `word_transition_rotor`/`make_rotor_from_angle` consumed by `field/operators.py` and `generate/intent_ratifier.py`, and `normalize_to_versor` by `generate/intent_ratifier.py`/`generate/admissibility.py`; **none of those symbols appear in any of those files**). Already superseded per R-7 — recorded so no later auditor adopts it as evidence. *(ADR-0004 §10)*
- **AA-A1-11** 🟡 **Repair** — ADR-0004's "Forbidden: any method on `VocabManifold` that constructs a rotor, versor product, or transformation" has **no enforcing pin**. The code complies today (verified by full read), but the guarantee rests on nothing, in direct contrast to INV-02/INV-02b next door, which AST-walk the tree for exactly this class of violation. *(ADR-0004 §2)*
- **AA-A1-12** 🟢 **Monitor** — the `docs/census/` `param-no-effect` sweep produced **no** entry for `_blend_feature_versors`'s inert `strength` argument, though that is the sweep's exact target class and the defect is ratified in G-25. Instrument gap in the census, not an ADR gap. *(§2, ADR-0004 §7)*
- **AA-A1-13** 🟡 **Repair** — ADR-0003 §Consequences ("no component outside `algebra/` needs to know about rotor composition") is contradicted by its own child ADR-0004 §Consequences and by five production modules; the child is right and neither ADR reconciles it. *(§3, ADR-0003 §2/§6)*
- **AA-A1-14** 🟢 **Monitor** — `algebra/__init__.py` exports only `word_transition_rotor`; `rotor_power` and `make_rotor_from_angle` — the two most-reinvented operators in AA-A1-5/6 — are reachable only via direct submodule import. Plausible contributing cause, cheap to fix. *(ADR-0004 §5)*
- **AA-A1-15** 🔵 **Consolidate** — four production sites hand-roll the raw sandwich `V X rev(V)` to deliberately bypass `versor_apply`'s closure (`algebra/null_point.py:84`, `core/physics/dynamic_manifold.py:287`, `core/physics/identity_manifold.py:150`, `core/physics/cognitive_lifecycle.py:272`). Each documents a valid reason; there is simply no shared `algebra.versor.raw_sandwich` primitive. Low severity. *(ADR-0004 §7)*

**Severity roll-up:** 2 🔴 Block · 6 🟡 Repair · 3 🔵 Consolidate · 4 🟢 Monitor. Both 🔴 entries concern the same seam (§3) and should be ruled together.

## 5. Evidence sources actually consulted (stack-wide)

**Charter and templates:** `docs/adr-audit/00-scope-and-method.md`, `TEMPLATE-stack-dossier.md`, `TEMPLATE-adr-card.md`, `MANIFEST.md`, `02-stack-taxonomy.md` (A1 row).

**ADRs read in full:** `ADR-0001-vocab-layer-invariants.md`, `ADR-0003-coordinate-system-dissolution.md`, `ADR-0004-rotor-as-operator-not-property.md`, plus `docs/adr/SESSION-2026-05-12.md` §§20:39–20:51 (the decision session for all three).

**Prior assessment evidence (checked before any fresh grep, per the charter's evidence order):** `docs/assessment/README.md`, `10-layer-cards/M0-substrate.md`, `30-gap-register.md` (G-21…G-25 read; G-24/G-25 adopted), `31-hindrance-audit.md`, `02-layer-taxonomy.md`. Confirmed **no** `20-component-cards/` entry exists for M0 / `L0-algebra`.

**Foundations Audit / analysis:** `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` (§§1, 5, 6), `docs/analysis/logos-substrate-collapse-2026-07-28.md` (via G-25), `docs/analysis/L10-runtime-scoping-2026-06-05.md` §3, `docs/plans/2026-07-28-foundations-audit.md`.

**Census sweeps at `cbfc8ccb`:** `stale-references.jsonl` (3 hits in this stack; 1 false positive), `docstring-drift.jsonl` (17 hits across the stack's modules — reviewed, almost all math-symbol noise), `param-no-effect.jsonl` (0 hits — AA-A1-12), `silent-drop.jsonl` (0 hits), `magic-numbers.jsonl` (`en_seeder` constants).

**Formal anchors:** `docs/Whitepaper.md` §III (seven axioms), §IV (three pillars), §V (Invariants I–III); `README.md:15,86` (core invariant, semantic-rigor pillar); `AGENTS.md` INV-21…INV-34 and Standing Philosophy #5/#10.

**Code read (full):** `vocab/manifold.py` (301), `algebra/rotor.py` (318), `algebra/versor.py` (204), `algebra/__init__.py`, `tests/test_vocab_manifold_invariants.py`.
**Code read (partial):** `algebra/cga.py`, `algebra/backend.py`, `algebra/holonomy.py`, `field/state.py`, `field/operators.py`, `ingest/gate.py`, `packs/compiler.py`, `packs/en_seeder.py`, `generate/articulation.py`, `generate/stream.py`, `generate/rotor_admissibility.py`, `session/context.py`, `core/physics/{dynamic_manifold,cognitive_lifecycle,identity_manifold,goldtether}.py`, `scripts/run_pulse.py`, `evals/logos/repaired_ground.py`, `tests/test_architectural_invariants.py`, `tests/test_doctrine_prohibitions.py`, `tests/test_third_door_cohesion.py`.

**Greps run (whole tree unless noted):** `edge_rotor`, `word_transition_rotor`, `rotor_power`, `make_rotor_from_angle`, `_blend_feature_versors`, `_alignment_nudge_rotor`, `_incremental_correction_rotor`, `_feature_rotor`, `_unitize_f32`, `VocabManifold`, `normalize_to_versor`, `unitize_versor`, `construction_seed_versor`, `versor_unit_residual`, `cosine|cos_sim|cosine_similarity`, `slerp|lerp|blend|interpolat`, `geometric_product(geometric_product(`, `np.cos(`, `.nearest(`, `manifold.add|update`, `field.operators`, `en_seeder|seed_english_manifold`.

**Executed (read-only, this session, at `cbfc8ccb`):**
- `uv run pytest -q tests/test_vocab_manifold_invariants.py tests/test_transition_rotor.py tests/test_rotor_power.py tests/test_versor_closure.py tests/test_manifold_collapse_floor.py` → **66 passed**.
- Probes against the live compiled manifold via the production `packs.compiler.load_pack` / `load_mounted_packs`: unit-versor residual census (353 surfaces, max `9.572e-07`); component-occupancy census (8 of 32); `is_null` / `cga_inner(v,v)` on stored vs `embed_point` objects; self-inner spread (−2.011…17.739); identity-recall sweep (350/353 misses, 3 packs cross-checked); 300-query random-field recall, full mount and English-restricted (1 distinct winner each); distinct-coordinate census (353 → 300, reproducing FA-1's 53 collisions); `construction_seed_versor` sensitivity probe (6 blade angles + global norm; output occupies 8 of 32 components).

**Discipline note.** Every "found / not found" row in §2 of every card came from `rg` against the tree or from executing the code, never from an ADR's own prose. Where a claim could only be sourced to a document, it is labelled as such (the M0 card, the FA-1 verdict, G-25). Settled rulings — FA-1's NO-GO, G-25's diagnosis, R-7's supersession of the substrate-liveness registry, the INV-02 normalization doctrine — entered as given constraints and were not re-litigated. **This audit decides nothing.**
