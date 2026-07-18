# Increment Plan — `compare_multiplicative` (reader arc, increment 1)

**Status**: APPROVED with four amendments (PR #76 ruling, folded below); **X = 15 ratified** as the
arc's escalation threshold. Build proceeds under this ruling — no separate re-ruling.
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

Expected immediate effect: **corridor real-reach 0/500 → the compare parses that already exist** — the
§7.2 "loop works end-to-end on official data" proof. Two amendments (PR #76) make this correct rather
than "unchanged":

### 3.1 Summation becomes registers-driven (AMENDMENT 1 — new code, not a confirmation)
The certified summation turn today orders by `program.seeds`, which come from `initial_state`. A
compare-**defined** register has **no seed**, so as currently coded it would be **silently excluded
from the total** — and all 5 real cases are totals. Fix: the summation sums **all registers present at
solve time**, in a **deterministically pinned order** (seed order, then definition order). Compile-side
validation must admit **defined entities as answer targets** (a total or a concrete unknown may be a
compare-defined register), with **unit propagation from the reference** (the defined register inherits
the reference's unit). Pin test: a compare-defined register appears in the certified sum.

### 3.2 The compare record (AMENDMENT 2 — specify before build)
Cross-register provenance must live in the chain so deterministic re-verification can reconstruct
**which register fed the dilation from records alone** (same reasoning as the summation-ruling). The
`compare_multiplicative` record: identifies the **reference entity**, and binds the **reference state's
digest** via the existing conditional `operand_source_digest` (present only on cross-register records,
so non-compare/non-summation record digests stay byte-identical). Verification re-derives the source
register from the record and checks the dilation reproduces.

## 4. Reader grammar family — broaden `compare_multiplicative` parsing

Today the reader emits `compare_multiplicative` for ~5/500 — narrow phrasings only ("double what",
"four times the number of", "three times as many/more"). Frontier incidence (spike §3) puts
`compare_multiplicative` markers in **~20% of official problems (~100/500)**, so the reader captures
~5% of the compare surface. The grammar family broadens the compare templates (e.g. "twice as … as",
"N times as much/many as", "N times the number/amount of", "half/a third as many as") — measured by how
many more official problems parse to a correct compare graph. Reader work lives in the
`generate/math_candidate_*` parser; this half is where most of the coverage delta comes from.

**"N times more than" — pinned convention (AMENDMENT 4).** The grammar family reads "N times more
than X" as **N×X** (not (N+1)×X), fixed as an **explicit disclosed convention** — the ambiguity is
real, so the reading is a stated choice, not an assumption. Every gold mismatch attributable to this
reading is **tracked as a recorded finding** (never a silent wrong); if the corpus systematically means
(N+1)×, the record will show it and the convention flips on evidence.

**Honest scope:** this increment solves problems whose only frontier kind is `compare_multiplicative`
(plus basic ops + summation). Multi-frontier problems (spike §3: 16/100 carry ≥2 markers) wait for their
other families' increments — recorded, not counted here.

## 5. Measurement protocol (§7.5 constraints, verbatim)

- **Signal = official `holdout_dev` only** — never the authored corpus.
- **`wrong=0` is the floor** — a compare parse counts only if `compile → execute → gold` agrees.
- **Sealed test (1,319) untouched.**
- **Disjoint split, pinned deterministically FIRST (AMENDMENT 3).** Before any grammar work, the 500
  `holdout_dev` cases are partitioned by a **deterministic protocol** — `sha256(id)`-ordered assignment
  (e.g. even/odd rank → tune / measure), documented in the plan and **fixed in advance**. The reader
  grammar is tuned only against the *tune* split; the increment's delta is measured only on the disjoint
  *measure* split. Disjointness is only as strong as its enforcement, so it is committed before a line of
  grammar changes — "better" can only mean "generalizes."
- **Delta reported** = new-correct on the measured split; the increment must clear **X = 15** (ratified,
  spike §7.3) or it triggers a practice-lane ruling. Compare incidence (~20%) means a paying reader
  family should convert well above 15.

## 6. Risks / open decisions (post-amendment)

1. **"N times more than"** — resolved to a pinned N× convention with tracked mismatches (§4, AMENDMENT 4).
2. **Garbled entity spans** (0268's actor is a run-on string) — cosmetic today (answer still correct),
   but the reader family should tighten entity extraction; a wrong *entity binding* could mis-route a
   compare in a 3-entity problem. Remaining open risk.
3. **Compare-then-op ordering** — if a defined register is later transferred/scaled, the compare must
   resolve first; the executor already runs ops in story order, so this is a test to pin, not new code.
4. **Register-introduced-by-compare in the total** — reclassified: this is **new code**, not a
   confirmation (§3.1, AMENDMENT 1). Summation is registers-driven with a pinned order; a defined
   register that is the answer target propagates its unit from the reference.

## 7. Increment PR (what ships next, under this ruling)

One smoke-gated PR: the compiler tier (§3, including §3.1 registers-driven summation + §3.2 compare
record) + the reader grammar family (§4) + tests + the measured delta. Test set:
- the 5 real parses solved end-to-end, `wrong=0`;
- **compare-defined register appears in the certified sum** (§3.1 pin);
- defined-entity answer target with unit propagated from the reference (§3.1);
- **compare record re-verification** — source register reconstructed from records alone (§3.2);
- no-conservation-on-compare; `fraction` direction;
- N× convention pinned, mismatches surfaced as findings (§4);
- the deterministic tune/measure split fixed before grammar work (§5, AMENDMENT 3);
- the measured `holdout_dev` **measure-split** delta recorded against **X = 15**.

Nothing else in it. Build proceeds now under this ruling.
