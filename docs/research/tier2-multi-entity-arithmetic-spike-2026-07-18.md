# Tier-2 Multi-Entity Arithmetic — Design Spike

**Status**: DESIGN — for review before implementation
**Date**: 2026-07-18
**Base**: `forgejo/main @ ebfdc8b4` (ADR-0249 Accepted; reader→Hamiltonian compiler shipped)
**Branch**: `feat/adr-0250-tier2-multi-entity`
**Provenance**: Next arc selected by Shay after ADR-0249. Extends Tier-1 (single-accumulator
affine) to multi-entity arithmetic — the 24 GSM8K dev-holdout cases ADR-0249 recorded as the
Tier-2 frontier.
**Next ADR number**: 0250 (re-verify at landing).

---

## 1. Objective (done-when)

Convert the recorded Tier-2 frontier — multi-entity arithmetic — into certified corridor turns
with the same honest-by-construction rigor as Tier-1: **wrong = 0 on what is ingested, typed
refusal on what is not, real-holdout coverage measured and recorded.** No serving change, no
gate activated, no manifold mutation.

## 2. Action-2 finding — the frontier is entirely 2a (verified on real data)

Probe over the 24 refused GSM8K dev-holdout cases (each via its `ground_truth_graph`):

| Category | Count |
| :--- | :--- |
| Refused (all `not_single_accumulator`) | 24 / 24 |
| **2a-eligible** (multi-entity, every op affine-or-transfer with a **constant** `Quantity` operand) | **24 / 24** |
| 2b (derived operand: rate / comparison / fraction / partition) | **0 / 24** |
| …of which contain a `transfer` op | 20 / 24 |

**Unknown-resolution split (probe on the 24 refused).** 18 have a **single-entity** unknown
(decode one register — pure 2a); **6 are total-like** (`unknown.entity is None`, "how many
altogether" → a certified **summation over registers**).

**Consequence.** Tier-2a (multi-register + constant-operand transfers, single-entity decode)
closes **18** → coverage 26/50 → 44/50. The **6 total-like** need a certified summation turn,
and summing registers *is* certified-decode staging (decode a certified register, use it as a
translator operand) — so **2b's certified-decode machinery is exercised on real data by these 6
cases**, not purely synthetic. Together T2a + summation potentially close all 24 → 50/50. The
narrower **derived-operand transfer** subcase ("gives half her apples", "as many as Y has")
remains **0-on-this-holdout** — designed + guarded, measured only on synthetic fixtures.
Recorded honestly — no silent claim.

## 3. Action-1 — the multi-register model + conservation invariant

**Representation: a product of independent conformal lines.** Multi-entity state is a tuple of
null points `(ψ_e1, …, ψ_eN)`, one register per entity, each its own 32-dim multivector / its
own relaxation. This respects the Cl(4,1) boundary exactly — no dimensional inflation (no
`Cl(8,2)` to pack two points into one multivector), so the f64 rounding floor (~6e-11) stays the
only residual and every operation is a native, exact versor action on a pure state.

**Constant-operand transfer = a coupled pair of translators.** "actor gives `k` to target" (the
ADR-0116 decomposition: subtract-from-actor + add-to-target) is `T₋ₖ` on the actor register,
`T₊ₖ` on the target register. Exactness across the independent null points is guaranteed because
the two translators act on **disjoint registers** — no cross-register interference; each is the
Tier-1 single-line transport already proven exact (ADR-0249 P1).

**Verified in-tree (2026-07-18).** Ruth 36 → 31, Sara 19 → 24, sum conserved at 55 (error
5e-13); 200 random two-entity transfers: worst per-register error 6e-11, worst conservation
error 6e-11 (f64 rounding only).

**Conservation as a load-bearing gate.** Because both translators use the same `k` with opposite
sign, `Σ decode(after) ≡ Σ decode(before)` exactly. This is a falsifiable **transfer-conservation
pin** (the arithmetic analogue of the chiral charge-conservation latch): a transfer that fails it
is rejected. It forces honesty by construction — hallucinated arithmetic across decoupled
registers cannot conserve. Non-transfer per-register ops (add/subtract/multiply/divide, rate as a
constant dilation, fraction as a constant dilation) reuse the Tier-1 primitives unchanged.

**Answer resolution.** The problem's `unknown.entity` selects which register's final decode is
the answer (or a total = sum of registers, for "how many altogether"). This is a compile-time
routing decision from the graph, decoded once at the end (anti-hollow preserved).

## 4. Tier-2b design — certified-decode staging + chain of custody

2b handles **derived operands** — "gives half her apples", "gives as many as Bob has" — where
the amount moved is itself a field quantity. Adding one register's value to another is not a
single translator (a translator adds a scalar *constant*; building `T_v` from a state needs
`v`'s scalar). The no-hollow resolution is **certified-decode staging**: relax a sub-turn to a
*certified scalar*, then use it as the constant operand for the target's translator turn.

### 4.1 The chain-of-custody question (Shay)

*How is the intermediate decoded scalar bound into the `TurnRecord` ledger so the chain of
custody proves the Python layer did not tamper with the value between turns?*

Three layers, no trusted-Python assumption:

1. **Certificate anchor.** The decode sub-turn produces state `ψ_v` with a
   `RelaxationCertificate` `C_v` whose `psi_digest = digest(ψ_v)`. Per ADR-0243, *convergence
   evidence cannot be borrowed* — the egress gate refuses `C_v` presented with any other state.
   So `C_v` cryptographically commits to the exact `ψ_v`.
2. **Operand provenance in the record.** The target turn's `TurnRecord` (extended for 2b) carries
   `operand_certificate_id = C_v.certificate_id` alongside the step's scale/offset (which encodes
   `v`, and is covered by `record_digest`). The record thus commits to *both* "operand = v" *and*
   "operand came from the certified state `ψ_v` via `C_v`".
3. **Deterministic re-execution + live gate.** Relaxation and decode are deterministic and pure,
   so verification re-executes the decode sub-turn → reproduces `ψ_v` → `digest(ψ_v)` must equal
   `C_v.psi_digest` → `decode_quantity(ψ_v)` must equal the recorded operand. A Python-layer
   tamper on the intermediate `v` makes the recorded operand disagree with the re-derived
   `decode(ψ_v)` → mismatch → rejected. In addition, a live `verify_derived_operand(record,
   C_v, ψ_v)` fails closed at execution time (`|decode(ψ_v) − operand| < tol` *and*
   `digest(ψ_v) == C_v.psi_digest`). The chain's `prev_record_digest` links keep the
   decode-turn → target-turn *sequence* tamper-evident (`verify_turn_chain`).

The Python layer cannot produce a `v` that is simultaneously recorded in the target turn *and*
equal to `decode(state pinned by the referenced certificate)` unless it is the honest value.

## 5. Phase plan (post-review)

**Transactional atomicity (Shay's Q — §5.1).** Registers are an **immutable snapshot**; a
transfer computes both candidate states into locals (prepare), validates (both certified +
conservation), and only then produces a **new** register set (commit). A failure anywhere means
the new set is never constructed → the original is untouched → no partial-mutation window, no
rollback needed. Records append only on commit; an abort surfaces a typed refusal and appends
nothing. Any aborted transaction aborts the whole program (fail-closed, preserves wrong=0).

- **T2a — multi-register executor + conservation pin + single-entity decode** (closes 18):
  compile a multi-entity `MathProblemGraph` into an immutable register set + per-register turn
  programs + coupled transfer transactions; enforce the transfer-conservation pin (hard-reject);
  decode the `unknown` register. Measure on the 18 single-entity refused dev cases.
- **T2b — certified-decode staging** (§4 chain of custody) → powers the **certified summation
  turn** for the 6 total-like cases (REAL data) and the derived-operand transfer (SYNTHETIC
  fixtures, 0 real). Coverage recorded per-subcase honestly.
- **T-instrument** — extend the `arithmetic-chain` domain to the multi-entity subset; honest
  coverage + wrong=0; symbolic-fold baseline over the same multi-register program.

Each phase: own PR, smoke-gated, TDD-first. New machinery ⇒ ADR-0250 (Proposed), acceptance
evidence assembled as in ADR-0249; no self-Accept.

## 6. Anti-hollow + governance (unchanged doctrine)

Registers flow as field states; decode happens once at the end (2a) or via a *certified*
sub-turn (2b) — never a compiler-side Python decode of a working quantity. Off-serving (A-04);
no gate activated; I-03 untouched; ratified contracts reused (`compile_quadratic_well`,
`quantity_kernel`, the Ring-2 chain pattern, `RelaxationCertificate`).

## 7. Rulings (RESOLVED 2026-07-18 — Shay)

All three APPROVED:
1. **"Altogether" = certified summation turn** in the substrate — never a compile-time Python
   total. Summation is certified-decode staging over registers; the total is grounded in a
   `RelaxationCertificate`, byte-identically traced.
2. **T2b ships this arc, designed + guarded.** The chain-of-custody machinery is the valuable
   infrastructure; exercised on real data by the 6 summation cases and on synthetic fixtures for
   derived-operand transfers; real-world derived-operand-transfer coverage logged 0-on-holdout.
3. **Conservation pin = hard-reject.** A transfer that fails `Σ decode(after) ≡ Σ decode(before)`
   is an algebraic failure, not a scope miss — fail closed, hard-reject, keeps the engine
   accountable and replayable.
