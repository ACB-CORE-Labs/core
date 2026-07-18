# ADR-0250 — Acceptance Evidence

> **ERRATA (2026-07-18):** "real GSM8K dev holdout" in this doc = **CORE-authored GSM8K-style corpus
> (ADR-0119.2)**, the mechanism-correctness instrument — not real GSM8K. Mechanism results (wrong=0,
> full-holdout 50/50) stand; only the corpus label is corrected. Measured real-GSM8K reach: reader
> 5/500, corridor 0/500 (reader-gated). See ADR-0250 §ERRATA + `docs/research/dev2-frontier-measurement-spike-2026-07-18.md`.

**Status**: RATIFIED — ADR-0250 Accepted 2026-07-18 by Joshua Shay
**Date**: 2026-07-18
**ADR**: `docs/adr/ADR-0250-tier2-multi-entity-arithmetic.md`
**Design record**: `docs/research/tier2-multi-entity-arithmetic-spike-2026-07-18.md`

Tier-2 extends the reader→Hamiltonian compiler (ADR-0249) to multi-entity arithmetic. With it,
the corridor solves the **entire** real GSM8K dev holdout. Built in smoke-gated phases, each
merged under its own PR off `forgejo/main`.

## Phases merged

| Phase | PR | Merge commit | What landed |
|---|---|---|---|
| Design spike | #71 | `97b2f8b7` | multi-register model, atomicity, chain-of-custody design; probe of the 24 refused cases |
| T2a executor | #72 | `efd5335e` | `evals/multi_register_program.py` — multi-register + transfers + conservation; 18/18 single-entity |
| 2b summation | #73 | `3c3dcdbe` | certified summation turn + `operand_source_digest`; full holdout 50/50 |
| Instrument + ADR | this PR | — | `arithmetic-chain` domain routes Tier-2; ADR-0250 + this evidence |

Smoke (`uv run core test --suite smoke -q`) green at every phase (176 passed).

## Load-bearing result

**Real GSM8K dev holdout (sealed, 50 cases):**

| Tier | Cases | Corridor |
|---|---|---|
| Tier-1 single-accumulator (ADR-0249) | 26 | correct, wrong=0 |
| T2a single-entity multi-register | 18 | correct, wrong=0 |
| 2b certified summation ("altogether") | 6 | correct, wrong=0 |
| **Total** | **50 / 50** | **wrong = 0** |

Corridor vs symbolic fold of the same compiled program: **PARITY** (delta 0) — the field matches
arithmetic, it does not beat it. The instrument's `arithmetic-chain` domain now records 50/50
coverage, 0 refused.

## Verified in-tree

- **Transfer conservation + per-register exactness**: Ruth 36→31, Sara 19→24, sum conserved;
  200 random transfers exact + conserving to ~6e-11.
- **Relative conservation pin**: `gma-050` (chains to 222) tripped an absolute 1e-6 tolerance;
  the relative check `|Δ| ≤ rtol·max(1,|before|)` fixes it and still catches real violations.
- **Chain of custody**: summation records carry `operand_source_digest`; tamper on any non-terminal
  record breaks the successor link (`verify_multi_register_chain`).

## Design decisions applied (honest register)

- **Atomicity via immutability**: prepare→validate→commit; no partial-mutation window, no rollback.
- **Summation stays in the substrate** (ruling #1): each addition is a certified turn, never a
  Python `sum()`; the total is grounded in `RelaxationCertificate`s.
- **The summation signal is the typed `unknown.entity is None`**, not an inferred op pattern.

## What remains open (not claimed here)

- Derived-operand transfers ("half of X") — designed + guarded, 0 on this holdout.
- Non-affine kinds (rate/comparison/fraction/partition) — 0 on this holdout, refused.
- >5-atom deduction via ROBDD-partitioned turn programs — future arc.
- ADR-0246 §3.7 admission-policy calibration — unchanged; no gate activated.
