# ADR-0249 — Acceptance Evidence

**Status**: Evidence pack for Shay's ruling (no self-Accept)
**Date**: 2026-07-18
**ADR**: `docs/adr/ADR-0249-reader-hamiltonian-compiler-composition-frontier.md`
**Design record**: `docs/research/reader-hamiltonian-compiler-spike-2026-07-18.md`

The reader→Hamiltonian compiler closes the composition frontier the
generalized-lift instrument (ADR-0246 S4) was waiting to measure. Built in five
smoke-gated phases, each merged under its own PR off `forgejo/main`.

## Phases merged

| Phase | PR | Merge commit | Module | Pins |
|---|---|---|---|---|
| P1 quantity kernel | #66 | `aca98d85` | `core/physics/quantity_kernel.py` | 35/35 |
| P2 relation compiler | #67 | `2575d0d9` | `core/physics/relation_compiler.py` | 21/21 |
| P3 CNF converter | #68 | `309e0ef6` | `evals/logic_cnf_compiler.py` | 32/32 |
| P4 turn-program executor | #69 | `805752db` | `evals/turn_program.py` | 15/15 |
| P5 instrument integration | this PR | — | `evals/generalized_lift_instrument.py` | 10/10 |

Smoke (`uv run core test --suite smoke -q`) green at every phase boundary (176 passed).

## Load-bearing results

**Multi-step arithmetic by chained certified relaxation** (P4):
`((5+3)*2)-4 = 12`, `(10/2+7)*3 = 36`, `(100-40)/4 = 15` — every turn
`ground_state_certified`; accumulator flows as a field state, decoded once.

**Real GSM8K dev holdout** (P5, sealed 50 cases, `evals/gsm8k_math/dev`):

| Metric | Value |
|---|---|
| Tier-1 affine ingestible | 26 / 50 (52%) |
| Corridor correct on ingested | 26 / 26 — **wrong = 0** |
| Corridor vs symbolic fold | PARITY (delta = 0) |
| Refused (multi-entity) | 24 / 50 — recorded Tier-2 frontier |

The corridor solves real GSM8K problems it can ingest with zero wrong answers,
and honestly refuses the rest. It does not beat arithmetic at arithmetic
(PARITY is honest); the deliverable is real-data coverage + a decidable
measurement, per the honest-NULL protocol.

**Algebra verified in-tree** (P1): conformal line embedding + translator/dilator
exactness checked against `algebra/cl41.py`'s own multiplication table (nullity
< 3e-10; translator exact to f64 rounding; dilator sign convention pinned).

**CNF soundness proved** (P3): for a 14-formula panel, the compiled CNF has the
same ROBDD identity as the source (`canonicalize` oracle); end-to-end entailment
agrees with `evaluate_entailment` gold, wrong = 0 on consistent premises.

## Design corrections applied (honest register)

- **Ring-2 is non-mutating.** `run_residual_protocol` is zero-bound (stage-5
  recertification refuses a moved witness), so it certifies fixed-state
  admissibility, not transitions. The turn ledger reuses the chain-integrity
  *pattern* (`TurnRecord` / `verify_turn_chain`), not the admission protocol.
- **`cga_inner` is the wrong metric for versor states** — readback and quantity
  decode use `phase_correlation/2`, pinned in the P1 module.
- **Scope note corrected** — the instrument's stale "no compiler exists" line is
  replaced with measured Tier-1 coverage + the multi-entity frontier.

## What remains open (not claimed here)

- Multi-entity / non-affine GSM8K (transfer, rate, comparison, fraction) —
  Tier-2, refused and recorded.
- >5-atom deduction via ROBDD-partitioned turn programs — next arc.
- ADR-0246 §3.7 admission-policy calibration — unchanged; no gate activated.
- `generate/` ("core_logos") serve-path articulation upgrade — still deferred.
