# Reader → Hamiltonian Compiler — Design Spike

**Status**: COMPLETE — design ready for review; all bindings verified against the live tree,
algebra claims verified in-tree. Implementation (P1–P5) starts after the §8 rulings.
**Date**: 2026-07-18
**Base**: `forgejo/main @ 6ff73aa7` (intelligence-loop arc merged; ADR-0246/0247/0248 Accepted)
**Branch**: `feat/reader-hamiltonian-compiler`
**Provenance**: Next-arc candidate #1 from `docs/handoff/ADR-0246-Acceptance-Evidence.md`; the
generalized-lift instrument recorded GSM8K/NL non-ingestibility as the composition frontier —
this spike designs the mechanism that crosses it.

---

## 1. Problem statement

The corridor can solve what it can ingest, and it can ingest almost nothing. Today's compilable
domains are (a) propositional entailment over ≤5 atoms and (b) quadratic wells around a known
target versor. Real problems — GSM8K arithmetic, multi-step deduction — have no path onto the
substrate. The measurement harness (Phase 4 instrument) is built and waiting; the compiler is
the missing feeder. This is the recorded composition wall from the GSM8K learning history
finally getting its mechanism.

**Done-when (spike)**: a ratifiable design that (1) compiles real reader output into corridor
Hamiltonians deterministically, (2) provably encodes *relations, not answers* (anti-hollow
invariant, §4.1), (3) reuses the merged Ring-1/2/3 machinery for composition, and (4) names its
governing ADR obligations line-by-line. Implementation phases follow only after the design is
reviewed.

## 2. Design thesis: composition = certified turn sequences

The wall is COMPOSITION (ADR-0191/0192/0193 lesson: single-layer widening is metric-inert).
The freshly merged arc supplies exactly the composition machinery: per-turn
RelaxationCertificates, egress routing, the Ring-2 residual protocol's replay-verified path
ledger, Ring-3 handoff, and the S3 tether. Therefore:

> **The compiler does not compile a problem into one big Hamiltonian. It compiles a problem
> into a *turn program* — an ordered DAG of small relation-Hamiltonians, each solvable in one
> lifecycle turn, chained through the Ring-2 path ledger.**

- Each turn's H is ≤ the substrate's native 32-dim space (the ≤5-atom limit *is* 2⁵ = 32 —
  the truth-table basis saturates the Cl(4,1) blade basis; this is a feature to design around,
  not an accident).
- Composition depth lives in the *certified chain*, not in matrix size. Multi-step problems
  become multi-turn programs whose end-to-end integrity is the path ledger's job — the same
  ledger that already discriminates `port:identity:d_stab>epsilon_turn`.
- This unifies the two flagship domains under one design: arithmetic chains (each step = one
  relation well) and >5-atom deduction (ROBDD-partitioned ≤5-atom slices per turn).

## 3. Substrate-native quantity encoding (the standing hand)

Numbers must live on the field before arithmetic relations can be field constraints. The
CGA-native choice — no bespoke machinery — is the conformal embedding of the real line:

- **Quantity**: `q ↦ P(q) = e_o + q·e₁ + ½q²·e_∞` (null point on the line's horosphere).
- **Addition by a known constant**: translator versor `T_a = 1 − ½ a e₁e_∞`;
  `T_a P(b) T̃_a = P(a + b)` — exact, versor-native.
- **Scaling by a known constant**: dilator versor `D_s`; `D_s P(b) D̃_s = P(s·b)` — exact.
- **Subtraction / division**: inverse versors of the above.
- **Relation as constraint**: "x = a·y + b" compiles to a quadratic well whose minimum is the
  versor-transported target — i.e. the *existing* quadratic-well machinery centered on
  `(T_b D_a) ψ_y (T_b D_a)~`, never on a precomputed number.
- **Weight honesty**: versor transport of null points is exact up to conformal weight (dilators
  rescale the point's overall factor), and the corridor requires unit-norm states
  (`compile_quadratic_well` refuses `target_not_unit` at 1e-9). The compiler therefore
  normalizes transported targets, and quantity *decode is projective* — `q` is recovered from
  coefficient ratios (e₁-coefficient over e_o-coefficient), which are scale-invariant, so
  normalization loses nothing.

Scope honesty (Tier 1): products of two *unknowns* are not versor operations. Tier-1 scope is
**affine DAGs** — each step multiplies/divides by problem-text constants and adds/subtracts
known or previously-certified quantities. This covers the dominant GSM8K step shape; the
non-affine remainder is recorded, not silently capped (§6 risks).

**Verified in-tree (2026-07-18)**: all four algebra claims checked numerically against
`algebra/cl41.py`'s own multiplication table (signature `(+,+,+,+,−)`, basis e1..e5;
`n_∞ = e4+e5`, `n_o = ½(e5−e4)`), 200 random cases, q ∈ [−50, 50]:
nullity `|P(q)²| < 3e-10`; translator exactness `|T_a P(b) T̃_a − P(a+b)| < 2e-10` (f64
rounding only — the identity is algebraically exact, translators preserve weight); dilator
`D = exp(+α/2·e4e5)` scales `s = e^{−α}` (sign convention pinned here) with conformal weight
rescale confirmed (w ≈ 2.01 ≠ 1 at α=0.7 — normalization required); projective decode
`q = e1c/(e5c − e4c)` scale-invariant to < 1e-9.

## 4. Design invariants (pins before code)

### 4.1 Relation-not-answer (anti-hollow)
The compiler must never evaluate the arithmetic or logic it encodes. If the compiler computes
`a+b` to center a well, the corridor confirms rather than solves — a hollow instrument.
Enforcement: (i) purity pin — no arithmetic on problem quantities in the compiler module
beyond versor construction; (ii) property test — compiled artifacts for a relation are
invariant to which variable is designated unknown; (iii) ablation test — corrupting the
relaxation changes the answer while compiler output is bit-identical.

### 4.2 Determinism + content addressing
Compiled Hamiltonians are frozen, content-addressed per ADR-0245 §2.3/§2.4 (full SHA-256,
canonical JSON, explicit `<f8` LE bytes; `_cached_eigh` keying unchanged). Same parse ⇒ same
`hamiltonian_id`, byte-identical.

### 4.3 Fail-closed compilation
Unsupported relation shapes, unparseable steps, or out-of-scope structures refuse with typed
errors in the *existing* `HamiltonianCompileError` family (`cognitive_lifecycle.py` already
carries the taxonomy: `bad_shape`, `not_symmetric`, `target_not_unit`, `atom_count_out_of_range`,
…) — extend that family upstream rather than inventing a parallel one. Never a guessed or
partial Hamiltonian.

### 4.4 Reader boundary (fix upstream)
The compiler consumes the existing readers' *typed* output only. If a reader's output shape is
insufficient, extend the reader's typed surface upstream — the compiler never parses raw text.

### 4.5 Governance
Evals-quarantined (A-04): the compiler and turn-program executor live off-serving; serving
consumes nothing from this arc. Sealed practice vs serving split per ADR-0175; wrong=0 guard
held on the deductive flagship; honest-NULL protocol on the instrument; proposal-only learning
(I-03) untouched.

### 4.6 Byte-identity & cross-hardware reproducibility (three tiers, honestly bounded)
The determinism claim splits into three tiers; only the first two are unconditionally
achievable, and the design says so rather than promising universal bit-identity.

- **Tier 1 — content address: SOLVED, unconditional.** `hamiltonian_id` = SHA-256 over
  canonical JSON + explicit `<f8` LE matrix bytes (ADR-0244 §2.7). Endianness — the one real
  architecture variable in hashing — is already coerced. Same matrix ⇒ same id on any machine.
- **Tier 2 — matrix construction: ACHIEVABLE, enforced in P1.** `algebra.cl41.geometric_product`
  (`:108-125`) is a fixed-order scatter-add (`result[idx] += sign·aᵢ·bⱼ`, canonical i,j order),
  no BLAS / `dot` / reduction ⇒ IEEE-754 correctly-rounded and hardware-deterministic. The
  translator/dilator identities have integer/half-integer coefficients, so well *centers* are
  bit-clean (verified §3). **Trap:** `geometric_product` and `reverse` silently fall back to
  **float32** unless handed f64 arrays (`:110-112`, `:134-135`). P1 constructs every versor and
  sandwich in explicit f64, and pins the result with **golden-bytes tests** — the frozen
  SHA-256 of a canonical compiled-Hamiltonian set as literal constants, so any numpy / toolchain
  / hardware drift in the last bit fails the test loudly (same discipline as the biography
  `<f8` hash pin and the `_cached_eigh` memoization tests).
- **Tier 3 — eigensolve → answer: GENUINELY hardware-bounded; do not overclaim.** The affine
  well `H = c(Id − ψψᵀ)` is dense, so `relax_to_ground` takes the LAPACK branch
  (`cognitive_lifecycle.py:590-593`). Its excited eigenspace is **31-fold degenerate** (all at
  energy c), and LAPACK fills that basis arbitrarily per build ⇒ `evecs`/`propagator` **bytes
  are not cross-hardware identical**. Mitigation, in order:
  1. **Analytic ground recovery.** The compiler *constructs* the target ψ (versor transport),
     so the corridor's job is to *confirm* relaxation reaches span(ψ), not to discover it. The
     converged steady state projects onto the unique 1-D ground space, so the degenerate-basis
     arbitrariness cancels in the limit; pin the **basis-invariant** `phase_correlation/2`
     agreement to ψ, never the propagator bytes.
  2. Where a future non-affine tier yields a genuinely dense non-degenerate H, record
     cross-hardware eigen-reproducibility as an explicit limitation (no-silent-caps) and pin
     the **decision** (`_certified` already uses tolerances, not bit-equality), not the bytes.

## 5. In-tree inventory (survey bindings)

### 5.1 Hamiltonian construction contract (verified)

- `ProblemHamiltonian` (`core/physics/cognitive_lifecycle.py:262-302`): frozen 32×32
  real-symmetric f64; refuses `bad_shape` / `non_finite_matrix` / `not_symmetric` (≤1e-12,
  never symmetrized); `hamiltonian_id` = SHA-256 of canonical JSON over domain + LE-f64 matrix
  bytes + stringified metadata; `is_diagonal` auto-derived → diagonal compilers get the
  no-LAPACK fast path for free (`relax_to_ground` :581-588).
- `compile_quadratic_well` (`:305-319`): `H = curvature·(Id − ψ₀ψ₀ᵀ)`; refuses
  `target_not_unit` (1e-9) — hence §3's normalize-then-projective-decode.
- `compile_propositional` (`:382-401`) + `PropositionalProblem` (`:326-361`, `_MAX_ATOMS = 5`
  at `:84`): diagonal falsification-count H over the 2⁵ = 32 assignment↔blade bijection
  derived through real geometric products (`_build_subset_component_map` `:183-203`).
  `propositional_entails` (`:714-750`) reads exact integer ground energies — no eigensolve.
- `_cached_eigh` (`:512-530`): LRU keyed `(hamiltonian_id, matrix bytes)`; ADR-0245 §3 perf
  gate (0 allocations / 0 LAPACK on repeated static H) binds compiler emissions.
- Sensorium compilers emit unit-versor *field states*, never Hamiltonians; the only H built
  from sensorium data is a quadratic well on the compiled percept
  (`evals/adr_0243_cognitive_lifecycle/__init__.py:114`).

### 5.2 Governing authorities (cite in the ADR)

- **ADR-0243 §2.2** — the definition this compiler implements: problem constraints formulated
  as potential wells in H_problem; "zero room for intermediate fabrication". §2.4/§4.2 —
  one-mutation-path; speculative H changes quarantined in `evals/` until signed certificate.
- **ADR-0244 §2.5/§2.7/§2.8** — f64 relaxation, full-SHA content addressing, frozen H.
- **ADR-0245 §2.2–2.4, §3** — serving-boundary cast, `_cached_eigh`, perf gate.
- **ADR-0012** — deterministic ingest governance; an LLM/D3 oracle upstream of the gate is
  explicitly rejected → the compiler's text side must ride the existing deterministic readers.
- **ADR-0247 §1 props 3–6** — purity/fail-closed/replay obligations when compiler outputs
  flow through ports. ADR-0246/0247/0248 are otherwise silent on problem-domain expansion
  (no conflict). AGENTS.md:99 — no stochastic generation inside the deterministic path.
- **ADR-0175 / 0191 / 0192 / 0193** — eval-entry law: sealed-practice vs serving split;
  completeness obligation (every source quantity consumed or refuse); class-not-list firewall;
  composition wall (single-layer widening is metric-inert). "ADR-0190" is citation-only —
  no such file exists; cite the instrument-before-consumption lesson via ADR-0193.
- Numbering: next free ADR number is **0249** (0240–0248 collision-free; re-check at landing).

### 5.3 Prior art this arc builds ON (reconciliation required)

- **ADR-0217 R2 finite-integer constraint compiler (RATIFIED, BUILT, off-serving)** —
  `problem text → entities → quantities → relations → CONSTRAINTS → goal → solver → verifier`.
  The reader→Hamiltonian compiler should be designed as a **constraint-IR → Hamiltonian
  backend** behind this ratified front-end, not a new text parser (§4.4 fix-upstream).
- **`docs/research/field-reasoner-wedge-selection.md`** — standing two-compiler independence
  design: §6 symbolic compiler, §7 field compiler MUST NOT import the symbolic one, §5 oracle
  imports neither, §10 GSM8K re-entry rule, §13 stop conditions; chosen wedge =
  ratio/proportion; state: 0A–0C green, 0D+W next. This arc must either continue that wedge
  or explicitly absorb it — not silently fork it (§8 decision).
- **`docs/research/independent-comprehension-agreement-gate.md` §3/§7** — two independent
  readers must construct the same canonical structure before any field-backed promotion.
  Resolution honoring both constraints: the Hamiltonian backend consumes the *post-agreement
  canonical structure*, so reader independence lives upstream of it and the backend imports
  neither reader.

### 5.4 Reader stack bindings (verified)

- **Arithmetic IR (Tier-1 input)**: Reader A — `generate/math_candidate_graph.py:589`
  `parse_and_solve` → `MathProblemGraph` (`generate/math_problem_graph.py:449`:
  `entities / initial_state / operations / unknown`, typed `Operation` kinds, canonical
  bytes). This is the affine DAG §3 compiles. **Reader B (`generate/derivation/pool.py:69`
  `resolve_pooled`) is sealed-practice only and MUST NOT feed the compiler** (standing
  two-reader disjointness; no bridge without sealed wrong=0).
- **Deduction IR (Tier-1 input)**: `generate/meaning_graph/reader.py:330` `comprehend`
  (NL prose, refusal-first) → `projectors.py:153` `to_deductive_logic` → `(premises, query)`
  formula strings. The corridor side consumes `PropositionalProblem` (CNF tuples, ≤5 atoms).
  **The only missing piece on this leg is a structural formula→CNF converter** —
  syntax-directed distribution over the restricted grammar with typed budget/atom-count
  refusals, never truth-table construction (which would evaluate, not translate). Today the
  bridge exists only ad hoc and in reverse (`evals/adr_0243_cognitive_lifecycle/
  propositional_falsifier.py`, CNF → formula strings).
- **In-tree precedent for §3's mechanism**: the field wedge's
  `generate/relational_field_reader.py:125` already reads relational problems into CGA
  *translator versors* (import-disjoint from its symbolic control arm, INV-27). The quantity
  kernel generalizes this proven mechanism into the corridor; the wedge's own 0D+W trajectory
  continues unaffected, and any future merge is an explicit ADR decision, not silent
  absorption.
- Every reader in the tree is refusal-first with typed refusal vocabularies and frozen-slots
  canonical outputs — the compiler inherits a uniform, well-typed upstream surface.

## 6. Risks (honest register)

| Risk | Level | Handling |
| :--- | :--- | :--- |
| Turn-program chaining exposes drift the single-turn arc never exercised | Medium — this is *the point* | The path ledger + tether are the instruments; failures here are findings, not embarrassments |
| Tier-1 affine scope covers less of GSM8K than expected | Medium | Coverage measured on the real holdout slice and RECORDED (no silent caps); non-affine remainder scopes Tier 2 |
| Anti-hollow invariant leaks (compiler smuggles evaluation) | High-harm if missed | §4.1 triple enforcement: purity pin + invariance property + ablation test |
| Quantity decode needs vocab the manifold lacks | Low | Quantity readback decodes null points geometrically, not via word vocab; word-level articulation of results remains gated by vocab coverage (separate arc) |
| Instrument shows corridor NULL vs symbolic evaluator baseline | High-likelihood, low-harm | Honest NULL recorded; the instrument exists to make this decidable |

## 7. Phase plan (post-review)

- **P1 — Quantity kernel** (`core/physics/`): line embedding `P(q)`, translator/dilator
  construction, normalize + projective decode; property tests for exactness (§3's verified
  claims become pinned tests), weight-rescale honesty, refusals on non-finite q.
- **P2 — Relation compiler v0**: affine relation → versor-transported, normalized
  quadratic-well `ProblemHamiltonian` (reusing `compile_quadratic_well`); typed refusals in
  the `HamiltonianCompileError` family for non-affine/out-of-scope relations.
- **P3 — Formula→CNF converter** (deduction leg): syntax-directed CNF over the restricted
  grammar → `PropositionalProblem`; typed refusals `atom_count_out_of_range` (>5) /
  clause-budget; closes the prose → `comprehend` → `to_deductive_logic` → CNF → corridor path.
- **P4 — Turn-program compiler + executor** (evals quarantine): `MathProblemGraph` → ordered
  turn program (one relation well per step, previously-certified quantities as transported
  targets); executor chains lifecycle turns through the Ring-2 residual protocol (per-turn
  certificates, replay-verified path ledger); tether readings per §S3.
- **P5 — Instrument integration**: arithmetic-chain domain added to the generalized-lift
  instrument; **real GSM8K holdout slice, never the 150 templated cases**; baseline = the
  symbolic evaluator over the same `MathProblemGraph`; honest-NULL protocol; Tier-1 affine
  coverage of the slice measured and RECORDED.
- **P6 (next arc, not this one)** — >5-atom deduction via ROBDD-partitioned turn programs.

Each phase: own PR, smoke-gated, TDD-first. New machinery ⇒ **ADR-0249** (Proposed;
re-verify number at landing), acceptance evidence assembled as in the intelligence-loop arc;
no self-Accept.

## 8. Rulings (RESOLVED 2026-07-18)

All four APPROVED by Shay:
1. **Tier-1 = affine-only.** Unknown×unknown deferred; keep the versor story exact.
2. **>5-atom deduction = next arc**, via ROBDD-partitioned turn programs. NOTE the honest
   reason: this is a *sequencing* choice (one capability per arc), **not** a claim that
   >5-atom deduction is impossible or needs probabilistic approximation — composition handles
   it deterministically and exactly. The 32-blade ceiling only forbids doing it *natively in
   one Hamiltonian*; the certified turn chain crosses it losslessly.
3. **One ADR (0249)** for quantity kernel + relation compiler + CNF converter + turn programs.
4. **Field wedge continues independently** (0D+W); this arc generalizes the same versor
   mechanism into the corridor; compiler imports neither wedge arm (INV-27 intact); any merge
   is a later explicit ADR.
