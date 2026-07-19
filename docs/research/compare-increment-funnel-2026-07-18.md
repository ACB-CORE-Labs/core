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

---

## MEASURED OUTCOME — the reader half (frame-anchored recognizer)

> **STATUS: BUILT + MEASURED, then DEFERRED out of increment 1 (PR #77 ruling).** The code change
> (`c3aed13b`, frame-anchored recognizer) was reverted from the merged increment; only the compiler
> tier + this finding land. Frame-anchoring is now an **open design task owned by the rate-frame
> increment** — see *Deferral ruling* below. This section is the on-record measurement that motivated
> the split.

### What was built and measured
Per the construction constraint (anchor on the comparative FRAME, not verb-whitelist growth), the two
multiplicative-frame regexes (`_COMPARE_MULT_ANCHOR_RE`, `_COMPARE_MULT_NTIMES_RE`) were re-anchored:
the closed-class frame — `<factor> as many/much <unit> as <REF>` — is the gate, the verb slot became a
verb-free bounded connector, and `as much` joined `as many`. `_comparison_anchor_verb()` (the whitelist)
is left in place for the ADDITIVE / NESTED frames (out of scope). Both frame regexes remain `$`-anchored,
so multi-clause / nested surfaces stay refused by construction.

### The polarity refutation — the real lesson
Pure verb-free anchoring is **not** wrong=0-safe: a polarity-inverting / depletion verb inside the frame
("Alice **lost** twice as many apples as Bob") makes the compared quantity a loss, so
`actor = factor × reference` reads the relation backwards → wrong>0. The frame does NOT disambiguate this
(pinned by `test_adr_0131_G2a…::test_polarity_inverting_verb_not_admitted`, `…spend…`,
`test_recognizer_comparative_inject…[Alice lost…]`). The prototype fix was a closed-class polarity
**blocklist** the connector may not span — but the ruling named the deeper problem this exposes, and it
is decisive: **the verb carries a polarity bit that must be positively determined, not
assumed-safe-unless-blocklisted.** A blocklist is fail-*open* — it admits every unenumerated verb, so a
depletion verb nobody listed reaches a *complete* frame as a coherent-but-inverted graph: a **wrong** on
the run-once sealed arbiter (the round-trip net guards parse consistency, not gold-correctness). The
fail-closed doctrine never takes that trade — least of all for the **zero** measured benefit below. So
the wrong=0-safe resolution is genuine design work: frame **plus positive polarity determination** (a
neutral-polarity *allowlist*, or a small polarity classifier), exercised end-to-end where it earns its
keep — the rate-frame increment — not bolted on here.

### Footprint — provable, tiny, safe
Develop-on-tune / measure-once discipline held. A new-vs-old frame-fire diff over all 500 official cases:

| Split | cases | divergent frame-fires | wrong | PARSED delta |
| :--- | ---: | ---: | ---: | ---: |
| tune | 261 | **0** (byte-identical histogram) | 0 | 0 |
| measure | 239 | **1** — `0441` "Zig **wrote** four times as many books as Flo." | 0 | 0 |

`0441` is the exact archetype (verb-blocked-only, single-clause, frame-at-end). Post-change its frame
fires correctly — and the case **still refuses**, one layer downstream: *"no admissible candidate for
question: 'how many books did they write altogether?'"*. It advanced frame-refusal → **question-refusal**
(the pre-registered sanctioned delta), confirming the frame now reads but the binding wall is the
**shared summation-question** layer. Same wall killed `0228` ("…how many boxes in both warehouses
combined?"). Smoke gate: **176 passed**.

### X = 15 — MISSED, delta = 0 (and why it's a shared-layer miss, not a family-exhaustion miss)
The 38 tune compare-family cases, classified by their **actual** structural blocker (not the noisy
surface histogram): 16 multiclause / nested (`…as Emily, who has…`, `…as Shawna, but 3 fewer…`),
10 single-clause-frame-no-match (multi-word "the X Y" references, `than` vs `as`, decimal factors,
unit-ellipsis "as much as", subject-is-comparison), 5 "times the number/amount of" (self-referential /
possessive references), 5 "as ADJ as" (attribute register), 2 "double what / triple". End-to-end traces
of the cleanest candidates (`0228`, `0274`, `0491`, `0165`, `0299`) show **every one dies at a
non-compare layer**: summation-question reading, seeding-sentence injection (shared discrete-count),
additive-compare, attribute registers, simultaneous equations. Even the cleanest compare-family frame
extension (multi-word reference) converts **0** cases end-to-end — and introduces an actor-misbinding
hazard — so it was reverted.

**Ruling per the pre-committed funnel-conditioned escalation rule:** the mass is dying in **shared
layers**, not compare-specific logic ⇒ the next increment is a **shared-layer design increment**, NOT a
practice-lane escalation, and NOT more compare-family frame surgery. **Shay's ruling (#77): next =
seeding-sentence injection** — the 135/261 "no injection (discrete_count)" wall, the dominant shared
bucket that gates every family (production/possession verbs like *made/baked/grew/wrote* that don't
inject an initial state). The compare-specific unblock (summation-question reader + **inverse compare** —
known=actor, solve reference; `0441` needs both) stays queued behind it. X is re-applied *after* the
shared layer lands.

### Triple report
- **correct**: measure new-correct = **0**. The compiler tier solves the compare cases the reader can
  already reach (`0101` "double what", `0108` "times the number of", `0411`) — all **pre-existing**, not
  new from the frame-anchoring.
- **refused-by-reason (traps broken out)**: polarity-inverting (lost/spent) → refused fail-closed by the
  `_comparison_anchor_verb()` whitelist (the merged state, after the frame-anchoring revert; the
  blocklist prototype that would have admitted-then-guarded them is deferred with the frame change).
  Family funnel: 16 multiclause/nested, 10 frame-no-match, 5 number/amount-of, 5 as-ADJ, 2 double-what —
  all refuse-and-record.
- **wrong = 0**: held on tune (261) **and** measure (239) **and** smoke (176). No over-admission from
  the verb-free widening; no branch-disagreement regression (0 tune divergences).

### Deferral ruling (#77) — the split
Increment 1 merges the **compiler tier + this finding**; the **frame-anchoring reader change is held
out** (`c3aed13b` reverted from the PR). Three compounding reasons, on record:

1. **Zero measured benefit today** — 0 conversions across all 500 official cases.
2. **Its consumer is a later increment** — frame-anchoring exists to serve rate-frame admission
   (increment 2). The *next* increment is seeding-sentence injection, a shared layer that does not touch
   it. Nothing on the critical path needs it now.
3. **Fail-open surface at the sealed test for that zero benefit** — the polarity blocklist admits every
   unenumerated verb; an unlisted depletion verb in a complete frame is a coherent-but-inverted graph =
   a wrong on the run-once arbiter. The fail-closed doctrine never risks that, least of all for no gain.

Verified before merge: with the whitelist reader restored, the 5 real compare parses are **non-divergent**
— `test_real_compare_cases_solved_wrong_zero` still sees **5, solves 5, wrong 0** (corridor real-reach
`0→5/500` preserved). The tier keeps its win without the frame change.

### OPEN DESIGN TASK (owned by the rate-frame increment)
**Frame-anchored comparative admission with wrong=0-safe polarity determination.** The frame is the right
gate; the open problem is the verb's polarity bit. It must be **positively determined**, not
assumed-safe-unless-blocklisted:

- a **neutral-polarity allowlist** (fail-closed: only verbs affirmatively known non-inverting admit), or
- a small **polarity classifier / lexicon** (possession/production/acquisition = neutral → `factor×ref`;
  depletion/transfer/loss = inverting → refuse or model as a delta).

Deliverable when the rate-frame increment lands it: exercised end-to-end on rate frames, measured on the
disjoint split, wrong=0 preserved on the sealed arbiter. Until then the reader stays on the
`_comparison_anchor_verb()` whitelist (fail-closed) for all comparative frames.
