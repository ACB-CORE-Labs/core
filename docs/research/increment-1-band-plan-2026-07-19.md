# Increment-1 Band Plan — reader arc (RULED — APPROVED TO BUILD)

## RULING (Josh, PR #79, 2026-07-19) — approved to build under these

- **Q1 depletion → REFUSE, confirmed.** Count depletion-containing band cases as *expected haircut*, not bugs.
- **Q2 existential → admit CONTAINER-BOUND only, refuse container-less, confirmed.** If tune surfaces a
  container-bound case that is actually a partitioned total, refuse that sub-form too.
- **Q3 q:difference → DEFER the capability, CLOSE the hazard now.** Its 23 cases likely strand on
  `multi-compound` (increment 2), so building the direction driver now is risk without in-band yield —
  defer to where its cases convert, and **verify the co-occurrence to confirm**. BUT make the existing
  partial Pattern-B ("how many more") path **fail-closed immediately**: if it can emit a guessed-direction
  difference today, that is a latent wrong=0 hazard to close regardless. **Increment 1 then carries EXACTLY
  ONE wrong=0 driver (#78).**
- **Sharpening 1** — allowlist-miss refusals are recorded as **curriculum** (unknown-verb refusals feed the
  practice/coverage backlog, not treated as failures).
- **Sharpening 2** — the sha256 tune/measure split stays **FIXED across increments 1–3** (the ~40 bar is
  cumulative; `evals/gsm8k_math/holdout_dev/v1/split.py` is frozen).
- **Sharpening 3** — the **haircut factor** ships with the triple in the final report.

The §3/§4/§6 design below is unchanged EXCEPT: q:difference (item 4) becomes *hazard-close only*, not a
built capability; increment 1 carries one wrong=0 driver (#78), not two.

**Status**: RULED — approved to build (measure-once). Design-first gate cleared (same gate as PR #76).

---

## BUILD OUTCOME (2026-07-19) — band-solve=0; the ~30-band bet is FALSIFIED

The headline stays band-solve=0. The two foundations are **built and verified**; they are the banked
byproduct, **not** a success against increment 1's conversion goal.

### Shipped (verified, wrong=0-safe)
The **#78 positive-polarity allowlist substrate** — `NEUTRAL_COUNT_VERBS` (`math_roundtrip.py`, extends
`ADD_VERBS` with curated neutral production verbs), shared by the seed matcher (acquisition path) and the
comparison `_comparison_anchor_verb()`. Depletion/transfer verbs refuse by **positive determination**
(not a blocklist). Verified: production injects / depletion refuses; **71 pinned comparative tests pass**;
**full-500 wrong=0** (tune 261 + measure 239); PARSED unchanged (tune 3, measure 2 — no regression, no
conversion); **smoke 176 green**. Merge gate met: full-500 wrong=0 + refusal histogram stable-or-explained.

### band-solve = 0, measured FOUR ways
yield harness, band map, band oracle (rewrite-and-run), capability histogram — all agree: the scoped band
`{seed + forward-comparison + q:simple/summation}` converts **0** tune cases. Its otherwise-in-band cases
**strand on capabilities outside the band**: 25 need multi-compound, 17 need compare-additive. §5 named
this exact risk; it landed.

### Minimal-convertible-band measurement (Josh's option-3 spec)
- **No small band converts.** The band oracle converts 0 with `{seed + comparison + q}`.
- **Taxonomy is NOT at bedrock.** The refined atomic classifier's "smallest tractable set" `{seed, q:simple}`
  (4 cases) dissolved on inspection — every one actually needs rate / compare / currency / copula
  (e.g. "James **spends 30 minutes twice a day** on meditation" = rate + temporal + unit-conversion in ONE
  sentence). **Real GSM8K statements are individually multi-capability**; the conjunction recurs *within*
  a sentence, so a capability list keeps fragmenting.
- **multi-compound is the single highest-leverage capability** — on the critical path for **70/106 (66%)**
  of tractable needed-sets — but insufficient alone (its cases also need rate/currency/etc.).
- **q:complex is the biggest intractable wall** (~35+ cases gated on it: 3 size-1, 18+14 size-2 needed-sets).
- **Closest cases** (0000/0001/0148/0082) all need complex compare forms (chained / mass-noun entities /
  "than" + aggregate reference) + summation/difference — still multi-capability.

### Implication for increment 2 (the first-conversion increment) — CASE-FIRST, not capability-first
Because the taxonomy fragments, no small capability band is a real floor. The path to the first conversion
is **case-first**: pick 2–3 specific closest tune cases, hand-enumerate their *exact* end-to-end needs
(however many capabilities), build precisely that, convert them, measure. The "minimal convertible band" is
not a small capability set — it is whatever a chosen handful of real cases need, built end-to-end. This is
the recommendation carried to Josh with the foundations PR.
**Date**: 2026-07-19
**Base**: `forgejo/main @ e1eb2a5c` (worktree `core-wt-seed`, branch `feat/seeding-injection` → to be
repurposed to the band).
**Model context**: unit of work = case-BAND (coverage is a per-case conjunction; see
`compare-increment-funnel-2026-07-18.md` MEASURED OUTCOME + the band map). Done-when = band-solve wrong=0,
NOT injection coverage.

---

## §1 The band (approved)

**`{ seed-simple + comparison (#78 polarity) + question-arithmetic (simple / summation / difference) }`**

The tractable spine's *foundational core* — the two capabilities every future band reuses
(question-arithmetic + #78 polarity) plus the two most common statement types (seed, comparison), adding
**zero new hard capabilities beyond #78** (which is already scoped). Band-map upper bound ≈ **30 cases**
(size 3–4). Deliberately the ~30 band, not the 42 band — see §5.

## §2 What EXISTS today (grounding — increment 1 EXTENDS, does not rebuild)

- **Compare COMPILER**: merged (PR #77) — `compare_multiplicative` executes wrong=0 (27/27). The reader
  frame was reverted to the `_comparison_anchor_verb()` whitelist (issue #78 open).
- **Question layer, PARTIALLY built** (`generate/math_candidate_parser.py`, `CandidateUnknown`):
  - `q:summation` — aggregate-cue vocab {in total, altogether, combined, together, in all} → `entity=None`
    → the 2b summation compiler. **Works today** (0101 solved via compare + summation).
  - `q:simple` — "How many `<unit>` does `<Entity>` have?" → single-register decode. Works.
  - `q:difference` — PARTIAL: "how many more `<X>`" Pattern-B sets `peer_count`; **direction is not yet a
    positively-determined, fail-closed decision** (§4 driver 2).
  - `extract_conditional_op_question_candidates` exists (some q:complex conditional forms).
- **Seed injector** (`inject_discrete_count_statement` + `_try_extract_discrete_count_anchor`): whitelists
  possession {has/have/had} → `CandidateInitial`, acquisition {collected/received/bought/got} →
  `CandidateOperation(add)`; **refuses every other verb and all existential "There are N X"** (fail-closed).

So the question-arithmetic *foundation largely exists*; increment 1 **completes** it (q:difference
direction) and adds the **seed + comparison** statement readers on the shared **#78 polarity substrate**.

## §3 The gap increment 1 builds

1. **#78 polarity substrate (the shared foundation).** Positive polarity determination = a
   **neutral-polarity ALLOWLIST**, fail-closed (NOT the reverted fail-open blocklist):
   - `_NEUTRAL_SEED_VERBS` (production/possession/acquisition: made/makes, baked, grew, scored, wrote,
     caught, taught, built, planted, picked, earned, harvested, found, drew, cooked, produced, + existing
     has/have/had/collected/received/bought/got) → seed (`InitialPossession` or from-zero `add`).
   - `_DEPLETION_VERBS` (lost/spent/gave/sold/used/donated/ate/dropped/paid/lent) → **refuse** in increment 1
     (a depletion is a delta over prior state, not a seed; modelling it is out of scope — fail-closed).
   - **Unknown verb → refuse.** Allowlist, positively determined. This *closes issue #78* for both seed
     and comparison, built once.
2. **Seed-simple injection** — extend the base injector via the substrate + a new **existential** path
   ("There are `N` `X` [in/on the `C`]" → `InitialPossession(entity=C-or-collective, N X)`; zero polarity risk).
3. **Comparison frame-anchoring** — re-land the verb-free frame (the reverted `c3aed13b`), but the verb
   slot is gated by the **same `_NEUTRAL_SEED_VERBS` allowlist** (fail-closed) rather than a blocklist.
   Depletion/unknown verb in a frame → refuse. Reuses the merged compare compiler.
4. **q:difference direction (§4 driver 2)** — complete the Pattern-B path: "how many **more** A than B" →
   signed `A − B`; "how many **fewer/less**" → `B − A`; **ambiguous/unsupplied direction → refuse**.
5. **q:simple / q:summation** — verify coverage on the band's cases; extend minimally only where a target
   case needs it (measured on tune).

## §4 The TWO wrong=0 direction drivers (Josh point 4 — positively determined, fail-closed)

- **Driver 1 — statement polarity (#78):** neutral-seed allowlist vs depletion. Seed vs deplete decided
  by verb class, fail-closed on unknown.
- **Driver 2 — question q:difference direction:** "more…than" → `A−B`, "fewer…than" → `B−A`, ambiguous →
  **refuse**. Same discipline as #78 and the inverse-compare lesson resurfacing in the question layer. A
  wrong direction here is a coherent-but-inverted answer on the run-once arbiter — the exact fail-open
  hazard we refused to ship in #77.

## §5 Deliberate smaller-band rationale (Josh point 1 — recorded so it is NOT read as under-ambition)

The map says a "real bar" needs size-4/~42; this band is the ~30, size-3–4 one, **by design**:

- **Increment 1's job is the FIRST end-to-end reader conversion the arc has ever landed.** Corridor
  real-reach is still 5/500 — *all* from the compiler tier; **no reader increment has converted a single
  case.** The bar for increment 1 is crossing zero, on foundations.
- It ships the **two foundations every future band reuses** (question-arithmetic completion + #78 polarity)
  and adds **zero new hard capabilities beyond #78** (already scoped).
- The 42 band adds **multi-compound** — a *new* hard capability. Stacking a new hard capability onto the
  first-ever conversion attempt raises the odds increment 1 *also* lands ~0. **Smaller-but-foundational
  maximizes the probability of the critical first win**, and every capability it ships is reused, never
  redone.

## §6 Done-when (Josh point 2 — reset for the band model; X=15-per-layer retired)

Increment 1 is DONE when:
1. **band-solve > 0 wrong=0** on the disjoint measure split — the first real reader conversion; AND
2. both foundations **validated and reuse-ready**: #78 polarity allowlist (fail-closed, wrong=0 on the
   depletion confusers) + q:difference direction (fail-closed on ambiguity); AND
3. wrong=0 held on tune + measure + smoke; cross-family parses stable-or-explained.

The **~40 "real bar" is CUMULATIVE across increments 1–3** (foundation → +multi-compound ≈ 42 →
+currency/rate ≈ 63), NOT increment 1 alone. Forcing one increment to clear a bar the map says needs five
capabilities would recreate the unsatisfiable-threshold problem at band scale.

## §7 Measurement (Josh point 3 + discipline)

- **Develop-on-tune / measure-once.** wrong=0 verified on tune throughout; measure split run ONCE at the end.
- **HAIRCUT FACTOR = a named increment-1 output**: `real band-solve ÷ ~30 upper bound`. This ratio — the
  single most valuable number beyond the conversions themselves — recalibrates the projected yield of every
  future band. Reported explicitly with the triple.
- Funnel re-run after each layer; refusal-histogram pinned + asserted stable-or-explained; cross-family
  parses unchanged-or-better; the depletion-confuser suite proves the polarity allowlist fail-closed.

## §8 Out of scope + roadmap boundary

- **Intractable-now (52%, 135/258):** `q:complex` (101 — conditional/averaging/multi-step), percent,
  simultaneous-equations, fraction/partitive. Explicitly OUT.
- **Increment 2–3 (the cumulative bar):** `multi-compound` (→42), `currency/rate` (→63).
- Tractable holdout ceiling ≈ **48%** until the q:complex decomposition (§9) revises it.

## §9 Scheduled NEXT (not increment-1 scope — Josh's forward directive)

**Decompose `q:complex` (101 cases) by sub-type BEFORE treating 48% as a fixed ceiling.** Hypothesis:
"averaging" = sum-over-count and "simple multi-step" = a turn program — both may be **corridor-tractable
with the compiler we already have**, hiding inside the "intractable" 101. If even 30–40 are reachable, the
ceiling moves materially. Measure before planning around 48% as fixed. Does NOT touch increment-1 scope.

Roadmap boundary to rule on in principle: when the tractable bands are exhausted (~48% reached), the
serve / practice / tackle-intractable fork opens. The conjunction structure is a wall for the practice lane
*too* (reward = full-conjunction case-solve is near-zero until a closure happens by luck), so the ceiling
argues for **continued design-first**, not switching.

## §10 Open questions for the ruling

- **Q1 — depletion verbs: refuse vs model-as-subtract in increment 1?** Plan says refuse (fail-closed,
  smallest scope). Modelling "X had M, lost N" needs prior-state + subtract-operation wiring — proposed
  for a later increment. Confirm refuse-only for now.
- **Q2 — existential entity binding.** "There are N X in the C" → entity = C (container). Container-less
  ("There are N X") → collective entity from the noun, or refuse? Plan leans refuse when no container/subject
  grounds the register (fail-closed), admit only container-bound. Confirm.
- **Q3 — is q:difference in-scope for increment 1, or deferred to keep the band at seed+comparison+q:simple/summation?**
  Plan includes it (23 cases, and it completes the question-arithmetic foundation), but it adds the 2nd
  polarity driver. If you'd rather minimize the first-conversion risk surface, q:difference can drop to
  increment 1.5. Recommend keeping it (foundational, and its cases are otherwise stranded).
