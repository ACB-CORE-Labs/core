# ADR-0249: Reader→Hamiltonian Compiler — the Composition Frontier

**Status**: **Proposed**
**Date**: 2026-07-18
**Authors**: Joshua Shay + multi-model R&D (implemented Fable 5)
**Depends on**: ADR-0243 (cognitive lifecycle — `relax_to_ground`, `ProblemHamiltonian`), ADR-0244/0245 (content-addressing, f64 relaxation, `_cached_eigh`), ADR-0217 (R2 finite-integer constraint compiler — front-end precedent), ADR-0175/0191–0193 (calibrated-learning / composition-wall doctrine)
**Design record**: `docs/research/reader-hamiltonian-compiler-spike-2026-07-18.md`
**Acceptance evidence**: `docs/handoff/ADR-0249-Acceptance-Evidence.md`

---

## 1. What this ADR is — and the thesis

The generalized-lift instrument (ADR-0246 seam S4) recorded a single blocking
scope limitation: *no reader→Hamiltonian compiler existed beyond ≤5-atom
propositional problems and quadratic wells, so real problems (GSM8K arithmetic,
NL deduction) could not be ingested by the corridor at all.* This ADR builds
that compiler and nothing more — it does not touch serving, does not activate
any gate, and does not claim the corridor now beats symbolic solvers.

**Thesis — composition = certified turn sequences.** The corridor's native
space is 32-dimensional (the Cl(4,1) blade basis; `_MAX_ATOMS = 5` is exactly
2⁵ = 32, structural not incidental). A problem is therefore *not* compiled into
one large Hamiltonian. It is compiled into a **turn program** — an ordered
sequence of small relation-wells, each solved in one certified relaxation turn,
with the working state flowing turn-to-turn on the field. Composition depth
lives in the certified chain, not in matrix size. This is the "wall is
COMPOSITION" lesson (ADR-0193) finally getting its mechanism.

## 2. Components (five phases, each merged under its own PR)

| Phase | Module | What it does |
|---|---|---|
| P1 | `core/physics/quantity_kernel.py` | Quantities as null points on the Cl(4,1) conformal line; add/scale by constants as translator/dilator versor sandwiches; projective scale-invariant decode. |
| P2 | `core/physics/relation_compiler.py` | `output = scale·input + offset` → quadratic-well `ProblemHamiltonian` via versor transport (reuses `compile_quadratic_well`). |
| P3 | `evals/logic_cnf_compiler.py` | Structural formula→CNF (reuses `logic_canonical` parser; eliminate iff/implies → NNF → distribute) → `PropositionalProblem` + query `Clause`. |
| P4 | `evals/turn_program.py` | `MathProblemGraph` → ordered turn program; chained-relaxation executor; content-addressed tamper-evident turn ledger. |
| P5 | `evals/generalized_lift_instrument.py` | `arithmetic-chain` domain: corridor vs symbolic fold on the real GSM8K dev holdout; honest coverage recorded. |

## 3. Anti-hollow discipline (load-bearing)

The compiler must never *evaluate* the arithmetic or logic it encodes — else the
corridor confirms a precomputed answer rather than solving, and the instrument
is hollow. Enforcement:

- The relation/turn compilers apply the problem's **structure** as versor
  operators (dilator for scale, translator for offset); the substrate's
  geometric product performs the arithmetic. No Python `scale·input+offset`.
- Compiled wells are **bare projectors** — metadata `{curvature, target_digest}`
  only; they carry no answer and no coefficients.
- In a turn chain the accumulator flows as a **field state and is decoded exactly
  once, at the end**; intermediate values are never decoded to drive the next
  turn.
- Ablation pins confirm the answer is produced by relaxation (the start state
  decodes to the input, only the relaxed state to the answer, with byte-identical
  Hamiltonians).

## 4. The Ring-2 correction (verified in-tree)

The design spike proposed "chain turns through the Ring-2 residual protocol."
Grounding against the code corrected this: `run_residual_protocol`
(`core/ports/residual_protocol.py:222`) is **zero-bound / non-mutating** — its
stage-5 recertification re-witnesses the subject and raises
`recertification_witness_changed` if it moved. Arithmetic turns *mutate*. The
protocol therefore certifies a *fixed* state's admissibility, not a state
*transition*, and cannot be the vehicle for the mutating turn.

Resolution (no hollow integration): the per-turn certificate is the relaxation's
own `RelaxationCertificate`; the tamper-evident *sequence* is recorded with the
Ring-2 chain-integrity **pattern** — a content-addressed `TurnRecord`,
`GENESIS_DIGEST`-linked, with `verify_turn_chain` mirroring `verify_replay_chain`.

## 5. Reproducibility — three tiers, honestly bounded (spike §4.6)

- **Tier 1 (content address): solved.** SHA-256 over explicit `<f8` LE bytes.
- **Tier 2 (matrix construction): enforced.** `geometric_product` is a
  fixed-order scatter-add (no BLAS/reduction) ⇒ IEEE-754 hardware-deterministic;
  it silently truncates to f32 unless handed f64, so every construction is
  explicit f64 and pinned with golden-bytes canaries.
- **Tier 3 (eigensolve): bounded, not overclaimed.** The affine well
  `H = c(Id − ψψᵀ)` has a 31-fold-degenerate excited eigenspace whose LAPACK
  basis is build-dependent; propagator bytes are not cross-hardware identical.
  Mitigation: the ground state is analytic (the target is constructed), so the
  basis-invariant `phase_correlation/2` agreement is pinned, never the bytes.

## 6. Tier-1 scope + recorded frontier

Tier-1 is the **affine single-accumulator** envelope: add / subtract / multiply /
divide with constant `Quantity` operands and positive scale; propositional
deduction over ≤5 atoms. Everything else — multi-entity, transfer, rate,
comparison, fraction, partition, non-positive scale, >5-atom deduction, unknown×
unknown — is **refused with a typed error and recorded**, never silently dropped
(no-silent-caps). >5-atom deduction via ROBDD-partitioned turn programs is the
next arc, not this one (a sequencing choice, not an impossibility).

## 7. Honest measurement (the done-when)

On the sealed real GSM8K dev holdout (50 cases): **26 are Tier-1 ingestible and
solved wrong=0**; the corridor matches the symbolic fold on every one (PARITY,
delta = 0 — the field matches arithmetic, it does not beat it); the 24 refused
are all multi-entity, the recorded Tier-2 frontier. This is the honest-NULL
protocol working as designed: the deliverable is a *decidable measurement* and
*recorded real-data coverage*, not an inflated lift claim. The recognition
domain's genuine +9 lift stands separately; arithmetic is honestly PARITY.

## 8. Governance

Off-serving (A-04): every module lives in `core/physics/` or `evals/` and is
never imported by `chat/runtime.py`. No gate is activated; no manifold is
mutated (I-03). Reuses ratified contracts (`compile_quadratic_well`,
`HamiltonianCompileError`, `logic_canonical`, the Ring-2 chain pattern) rather
than forking them. Local-first CI: smoke green in-worktree at every phase.

## 9. What this ADR does NOT claim (honest register)

- Not a serving change; the symbolic `generate/` path remains the serve path.
- Not a lift over symbolic solvers on arithmetic (PARITY is the honest result).
- Not full GSM8K coverage — 52% of the dev holdout is Tier-1; the rest is the
  recorded frontier.
- Not an activation of any admission gate (ADR-0246 §3.7 stays uncalibrated).

## 10. Ruling record (§8 — Shay)

_Awaiting ratification._ The four design rulings (affine-only Tier-1; >5-atom
deduction deferred; single ADR; field wedge independent) are recorded RESOLVED
in the spike; acceptance of this ADR is Shay's alone (no self-Accept).
