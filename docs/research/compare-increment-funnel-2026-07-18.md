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

## The "no injection" is intentional — the reader was waiting on the compiler

Code archaeology (before treating "no injection" as a defect) found the cause is a **deliberate
narrowing**, not broken code. In `generate/recognizer_anchor_inject.py`, the discrete-count injector
carries explicit fail-closed guards for comparative surfaces:

- Line ~324: *"…it is an incomplete comparative-multiplicative clause. Letting this through as an
  initial … defeats the ADR-0191 completeness guard. **Refuse here until a real compare_multiplicative
  operation can be emitted.**"*
- `_count_token_followed_by_times` (~460): *"it only suppresses the malformed initial candidate and
  **does not create any new admitting path**."*

This is the **lockstep thesis of the arc written into the code's own history**: the reader
deliberately *refused* compare shapes — to protect `wrong=0` and completeness — because nothing
downstream could compile them. **The compiler tier this increment just shipped is exactly that
"real compare_multiplicative operation."** So the fix is not repairing injection; it is **lifting a
now-obsolete guard whose reason has shipped** — turning the deliberate suppression into a compare
emission — which is a cleaner, safer change than patching around it.

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

## Shared-layer reality — the whole-tune refusal histogram (pinned baseline)

Across ALL 261 tune cases (not just compare-marked), the reader's refusal-reason histogram — pinned
**before** any shared-layer edit, asserted **stable-or-explained** after:

| Refusal reason | Cases |
| :--- | ---: |
| **no injection** | **196** |
| no admissible candidate for statement | 48 |
| expected exactly one question | 9 |
| no admissible candidate for question | 4 |
| **PARSED** (all compare) | **3** |
| no branch produced a solvable | 1 |

**"no injection" is 196/261 (75%) — a *shared* bottleneck across every family, not a compare defect.**
The reader recognizes statements but can't inject candidates for three-quarters of real GSM8K. A
guard-lift that silently changed *why* other cases refuse would corrupt the practice-lane curriculum
even with zero parse breakage, so the histogram is pinned; the only sanctioned post-edit delta is
compare cases moving from "no injection" → PARSED (or to a downstream layer), disclosed explicitly.

## Funnel-conditioned escalation rule (PRE-COMMITTED, before the number exists)

X = 15 was ratified assuming *family capability* was the wall. The baseline shows the wall may be the
**shared pipeline** (injection / enumeration / admissibility / round-trip) that every family crosses.
So a miss on X is read through the funnel:

- **Mass dying in compare-specific logic** → the family's design well is dry → **practice-lane ruling**
  (as designed).
- **Mass dying in a shared layer** → the next increment is a **shared-layer design increment**, *not*
  a practice escalation. X is re-applied after the shared layer is fixed.

Load-bearing reason: **the practice lane cannot learn past a deterministic wall.** A practice loop
generates better parse *candidates*, but they cross the same enumeration/admissibility/round-trip
pipeline; if a hard-coded shared layer refuses everything, practice fails identically — escalating into
a mechanism that can't help. Shared-layer bottlenecks are design work regardless of what X says.

## Reframe (recorded)

Compare is the **first slice of a much larger reader project**: the reader parses ~1% of real GSM8K
(3/261 tune), and "no injection" (75%) is a shared wall in front of every family. This is not scope
creep — it is the arc seeing its true size. The increments stay small and measured *precisely because*
the project is large.
