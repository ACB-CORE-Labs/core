# compare_multiplicative Increment — Per-Layer Attrition Funnel (diagnostic artifact)

**Status**: DIAGNOSTIC — instrument-first, decides the fix order (PR #76 ruling)
**Date**: 2026-07-18
**Scope**: the 61 compare-multiplicative-marked cases in the **tune** split of official `holdout_dev/v1`
(measure split untouched). Signals are the reader's own: `branches_enumerated`, `refusal_reason`,
`selected_graph`, then the corridor compiler.

---

## The funnel

Reader pipeline stages: recognizer-match → **injection** → enumeration → admissibility → graph → solve.

| Layer | Cases (of 61) |
| :--- | ---: |
| Died **pre-enumeration** | **57** |
| Enumerated | 4 |
| …enumerated but no graph | 1 |
| …graph has a compare op | 3 |
| **Solved today** | **3** |

Pre-enumeration refusal reasons (the 57):

| Reason | Cases |
| :--- | ---: |
| **"recognizer matched but produced no injection"** | **45** |
| "no admissible candidate for statement" | 8 |
| "expected exactly one question sentence" | 3 |
| "no admissible candidate for question" | 1 |

## The finding

**The leverage is the injection layer: 45 / 61.** The recognizer already *matches* these compare
statements (e.g. 0000: "Aria has twice as many … as Emily, who has twice the number … as Spencer");
the **injection** step then produces no candidate — the multi-clause / compare shapes don't inject.
This is where the mass is — not the candidate regexes (they fire on clean clauses but the real
sentences never reach them), and not segmentation writ large.

## Consequence for the fix (emitter-fix, not gate-loosening)

Injection is an **emitter** (it produces candidates), not a validator — so making it inject
compare candidates for statements the recognizer already matches is the sanctioned kind of change
(fix emitters; never loosen the round-trip gate). The remaining piles are secondary and sequenced
after: "no admissible candidate for statement" (8), the one-question-sentence constraint (3).

Fix order, by measured mass: **injection (45) → statement-admissibility (8) → question-sentence (3)**.
Each fix is developed against tune only, to `wrong=0` on tune; the measure split gets its single run
at the end. Refusal-by-reason on the measure split (frequency / nested / anaphora / temporal /
inverse-undeterminable) is reported with the delta as the fail-closed evidence + the practice-lane
curriculum.
