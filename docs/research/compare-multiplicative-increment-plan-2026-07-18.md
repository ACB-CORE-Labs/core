# Increment Plan — `compare_multiplicative` (reader arc, increment 1)

**Status**: PLAN — design-first, for ruling before any build
**Date**: 2026-07-18
**Base**: `forgejo/main @ dd1e4670` (dev2 spike + errata merged, #75)
**Branch**: `feat/compare-mult-increment-plan`
**Arc**: reader, design-first — per-family increments in lockstep
(`docs/research/dev2-frontier-measurement-spike-2026-07-18.md` §7). This is increment 1;
`compare_multiplicative` jumps the queue because the reader already emits real parses for it.

---

## 1. The increment (both halves, one PR)

Per §7.1 the increment lands a **grammar family in Reader A + its matching compiler tier, in
lockstep**, as one smoke-gated PR carrying a measured `holdout_dev` delta, `wrong=0` held, sealed test
untouched. The two halves cannot move separately — proof below: the 5 real compare parses exist today
and die at the compiler (corridor 0/500).

## 2. Ground truth — the 5 real compare parses (holdout_dev)

Every one has the same shape: **one entity seeded, the other *defined* by the comparison, unknown =
total.**

| id | shape | gold |
| :--- | :--- | :--- |
| 0101 | Eduardo=3; Frankie = 2×Eduardo; total | 9 |
| 0108 | Newport=22; Dana = 4×Newport; total | 110 |
| 0411 | female=13; male = 3×female; total | 52 |
| 0453 | dad=7; Olaf = 3×dad; total | 28 |
| 0268 | Bruce=4; Michael = 3×Bruce; total | 16 |

`compare_multiplicative` op carries `Comparison(reference_actor, factor, direction ∈ {times,fraction})`:
**`actor_quantity = factor × reference_actor_quantity`** (ADR-0123). All 5 have `unknown.entity = None`
→ the existing **certified summation turn** (ADR-0250 2b) closes them once the compare op is solvable.

## 3. Compiler tier — `compare_multiplicative` (evals/multi_register_program.py)

A **cross-register affine definition**: `actor := factor × reference`. Reuses the quantity kernel and
the multi-register framework; two things are new and must be designed explicitly:

- **Reads one register, writes another.** Today's per-register ops read+write the same register.
  Compile the op to: transport the **reference register's field STATE** by a dilator
  (`dilate(ref_state, −ln factor)`), relax to it, and write the result into the **actor** register.
  Anti-hollow: transport the reference *state*, never a decoded value.
- **The actor is *defined*, not seeded.** In all 5, the actor has no `initial_state` possession — the
  comparison introduces the register. The executor must admit a register first written by a compare op
  (today it seeds only from `initial_state`).
- **No conservation pin.** A transfer *moves* quantity (Σ conserved, hard-reject); a comparison
  *creates* a related quantity (Σ is not conserved by design). The conservation pin applies to
  transfers only; compare ops are exempt — stated, not silently skipped.
- `direction='fraction'` (factor < 1, "half as many as") is the same dilator with `factor < 1` — folded
  in. `compare_additive` (`more`/`fewer`, a translator) is a **later** increment (frequency order §7.2).

This is the whole compiler half: a new op branch that dilates a reference register into an actor
register, plus admitting compare-defined registers. The certified record chain and the existing
summation turn carry the rest unchanged. Expected immediate effect: **corridor real-reach 0/500 → the
compare parses that already exist** — the §7.2 "loop works end-to-end on official data" proof.

## 4. Reader grammar family — broaden `compare_multiplicative` parsing

Today the reader emits `compare_multiplicative` for ~5/500 — narrow phrasings only ("double what",
"four times the number of", "three times as many/more"). Frontier incidence (spike §3) puts
`compare_multiplicative` markers in **~20% of official problems (~100/500)**, so the reader captures
~5% of the compare surface. The grammar family broadens the compare templates (e.g. "twice as … as",
"N times as much/many as", "N times the number/amount of", "half/a third as many as") — measured by how
many more official problems parse to a correct compare graph. Reader work lives in the
`generate/math_candidate_*` parser; this half is where most of the coverage delta comes from.

**Honest scope:** this increment solves problems whose only frontier kind is `compare_multiplicative`
(plus basic ops + summation). Multi-frontier problems (spike §3: 16/100 carry ≥2 markers) wait for their
other families' increments — recorded, not counted here.

## 5. Measurement protocol (§7.5 constraints, verbatim)

- **Signal = official `holdout_dev` only** — never the authored corpus.
- **`wrong=0` is the floor** — a compare parse counts only if `compile → execute → gold` agrees.
- **Sealed test (1,319) untouched.**
- **Disjoint split:** the reader grammar is tuned against one `holdout_dev` sub-split and the increment's
  delta is measured on a **held-out disjoint** sub-split — "better" can only mean "generalizes."
- **Delta reported** = new-correct on the measured split; the increment must clear **X = 15** (spike
  §7.3, pending Shay's ruling) or it triggers a practice-lane ruling. Compare incidence (~20%) means a
  paying reader family should convert well above 15.

## 6. Risks / open decisions

1. **"N times more than"** is linguistically ambiguous (N× vs (N+1)×); the reader currently reads it as
   N× and gold agreed on the sampled 5, but the grammar family must pin one reading and measure, not
   assume.
2. **Garbled entity spans** (0268's actor is a run-on string) — cosmetic today (answer still correct),
   but the reader family should tighten entity extraction; a wrong *entity binding* could mis-route a
   compare in a 3-entity problem.
3. **Compare-then-op ordering** — if a defined register is later transferred/scaled, the compare must
   resolve first; the executor already runs ops in story order, so this is a test to pin, not new code.
4. **Register-introduced-by-compare** interacts with the total summation (which sums all registers) —
   confirm the defined register is included in the sum (it must be).

## 7. Increment PR (what actually ships, after this plan is ruled on)

One smoke-gated PR: the compiler tier (§3) + the reader grammar family (§4) + tests
(the 5 real parses solved end-to-end wrong=0; compare-defines-register; no-conservation-on-compare;
fraction direction; the disjoint-split holdout delta) + the measured `holdout_dev` delta recorded
against X. Nothing else in it.
