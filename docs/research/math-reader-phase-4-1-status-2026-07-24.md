# Math reader Phase 4.1 — measured status: the increment is already built, and it converts nothing

**Date:** 2026-07-24 · **Arc:** generalization Phase 4.1 (Tier O, O4) · **Result:** null, by measurement

## What was asked

The generalization plan §2/Phase 4.1 and the Opus brief item O4 both name
"seeding-sentence injection (standing ruling #77 — the 75% 'no injection'
wall)" as the next math move, with wrong=0 on the full 500 as the gate and
parse-rate gain as the goal.

## What is actually in the tree

Seeding-sentence injection **is built and merged**. The reader arc's increment
1 shipped it as the #78 positive-polarity substrate:

- `generate/math_roundtrip.py::NEUTRAL_COUNT_VERBS` — the curated
  production/possession/acquisition allowlist,
- consumed by the seed matcher's `inject_discrete_count_statement` path and by
  `generate/math_candidate_parser.py::_COMPARISON_ANCHOR_VERBS`,
- depletion/transfer verbs refuse by positive determination (an allowlist, not
  a blocklist — the fail-open blocklist was reverted),
- documented in `docs/research/increment-1-band-plan-2026-07-19.md` §BUILD
  OUTCOME.

Its measured yield when it shipped: **PARSED unchanged — tune 3, measure 2, no
conversion.** The scoped band `{seed + forward-comparison + q:simple/summation}`
converted **0** tune cases, measured four independent ways (yield harness, band
map, band oracle, capability histogram).

## Re-measured today, on the frozen split

```
uv run python evals/gsm8k_math/holdout_dev/v1/runner.py
holdout_dev: correct=5 wrong=0 refused=495 (n=500)
```

Five correct is exactly the tune-3 + measure-2 the increment-1 report recorded.
**No drift in five days of unrelated arc work, and wrong=0 still holds.** The
tune/measure split (`evals/gsm8k_math/holdout_dev/v1/split.py`) is frozen and
was not touched.

## Why the honest move is to stop rather than extend

The arc's own evidence says the wall is not where 4.1 aims:

1. **The ~30-band bet was falsified.** In-band cases strand on capabilities
   *outside* the band — 25 need multi-compound, 17 need compare-additive.
   Adding more seed verbs cannot convert a case that also needs rate,
   currency, and unit conversion in the same sentence.
2. **The taxonomy is not at bedrock.** The "smallest tractable set"
   `{seed, q:simple}` dissolved on inspection: every one of its four cases
   really needs rate / compare / currency / copula. Real GSM8K statements are
   individually multi-capability — the conjunction recurs *within* a sentence,
   so a capability list keeps fragmenting rather than converging.
3. **Growing the allowlist is the forbidden move.** ADR-0251 and
   `docs/research/reader-arc-overfit-inventory-2026-07-19.md` exist because
   per-case pattern growth previously produced overfit "lift" that committed
   *wrong* answers on the real exam. An extension whose only evidence is "it
   parses more tune cases" is the exact shape of that failure.

## The live next move (unchanged, and it is not 4.1)

The reader arc's own recommendation, carried to Shay with the increment-1
foundations, is **case-first, not capability-first**: pick 2–3 specific closest
tune cases, hand-enumerate their *exact* end-to-end needs however many
capabilities that is, build precisely that, convert them, measure. The closest
cases are already identified — `0000`, `0001`, `0148`, `0082` — all needing
complex compare forms (chained / mass-noun entities / "than" + aggregate
reference) plus summation or difference.

`multi-compound` is the single highest-leverage capability (on the critical
path for 70/106 = 66% of tractable needed-sets) but is insufficient alone.
`q:complex` remains the largest intractable wall (~35+ cases).

## Recommendation for the plan

Phase 4.1 should be marked **complete-with-null-yield** rather than pending,
and Phase 4 re-pointed at the increment-2 case-first work. The measurement
above is the evidence; nothing in this session's arc work moved it either way,
which is itself the useful signal — the math lane is genuinely orthogonal to
the reading/curriculum work, exactly as the plan's §3 dependency table assumed.

Phase 4.2 (compare unblock) and 4.3 (q:complex decomposition study) are
untouched by this and remain queued behind the case-first increment.
