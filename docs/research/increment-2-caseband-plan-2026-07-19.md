# Increment-2 Plan — CASE-FIRST first-conversion band (DESIGN-FIRST, for ruling)

**Status**: DESIGN-FIRST — ruling before any build (usual terms).
**Date**: 2026-07-19
**Base**: `forgejo/main @ 854ce023` (worktree `core-wt-inc2`, branch `feat/reader-inc2-caseband`).
**Context**: increment 1 shipped the #78 foundations (PR #79), band-solve=0. Per the fragmentation finding
(taxonomy not at bedrock; statements are per-sentence multi-capability), increment 2 is **case-first**:
target specific closest cases, build their exact end-to-end needs, convert them with a
correct-for-the-right-reason proof. This is the increment that crosses zero on the reader side.

## §1 Target cases — the 0148 / 0001 cluster (0000 deferred)

| Case | exp | decomposition |
| :--- | ---: | :--- |
| **0148** | 1500 | first-day = 2 × second-day; second-day = 500 (in "If"); total = 1000+500 |
| **0001** | 480 | Hooper = 2 × (two other harbors combined); each other = 80 → combined 160; total = 320+160 |

**0000 deferred** (fast-follow): needs chained compare ("…who has twice…as Spencer") + compound-subject
summation ("how many do Aria and Emily have") + question-arithmetic ("**twice** the total") — three extra
capabilities beyond the cluster spine.

## §2 The spine is PROVEN to work (grounding, not assumption)

Canonical rewrites — each target's compare statement rewritten to the plain "A has N times as many X as B"
form and its seed moved to a statement — **both solve wrong=0 today**:
- 0148 canonical → **1500** ✓  · 0001 canonical → **480** ✓  · a fresh forward-compare+total → 20 ✓

So forward multiplicative compare + statement-seed + summation all work (compare compiler merged #77, #78
substrate, 2b summation). **The gap is exactly the surface forms below — nothing in the solver.**

## §3 The gap increment 2 builds (the isolated delta)

1. **Conditional-seed-in-question** — parse `If <REF> <has|is|have> <N> [each], <question>` and seed
   `REF = N` (or `REF = N × count` for "each") from the question clause. Shared by all three cluster cases.
   *(The reader has `extract_conditional_op_question_candidates`; increment 2 extends/*verifies* it for the
   seed-a-reference form.)*
2. **Compare reference-form extensions** (the per-case differ):
   - **0001**: `than` accepted alongside `as`; aggregate reference "the two other harbors combined"
     (an explicit sum of the two seeded peers) + "each" distribution.
   - **0148**: mass-noun temporal entities ("the number of people counted on the first/second day") +
     the "`<A> was twice the total number counted on <B>`" copula-compare frame.
3. **(already works)** summation over registers for these two cases (verified in §2).

## §4 wrong=0 drivers (positively determined, fail-closed — the review focus)

Each new surface is a wrong=0 driver; each must bind correctly or refuse:
- **Conditional-seed binding** — `If <REF> has <N>` must seed the *named* REF, never a nearest/other
  entity. Ambiguous or unmatched reference → **refuse** (no guessed binding).
- **Aggregate reference** ("the two other harbors combined") — must sum *exactly* the two seeded peers,
  never more/fewer; if the peer count isn't unambiguous, **refuse**.
- **"each" distribution** — "80 each" × (peer count) must use the count the text grounds; ambiguous → refuse.
- **`than` surface** — admit only where it is provably the multiplicative-comparison surface (factor +
  explicit reference present), same frame gate as `as`; otherwise refuse.
- Compare *direction* itself is already covered (#78 allowlist + the compiler's inverse-refusal); no new
  direction driver is introduced (the seeds make these FORWARD compares).

## §5 Done-when (band model)

1. **band-solve ≥ 1 wrong=0** (target both 0148 + 0001) — the first real reader conversions of the arc; AND
2. **correct-for-the-right-reason proof** for each conversion (the 3-part standard): every statement injects
   the semantically correct graph element; the question reads to the right target/op; end-to-end == gold —
   NOT answer-matches; AND
3. full-500 wrong=0; mis-injection sweep clean (any new mis-injection → fix-to-refuse, not a conversion);
   refusal histogram stable-or-explained; smoke green.

## §6 Measurement / discipline

Develop-on-tune / measure-once. Funnel re-run after each surface. **Haircut factor** reported with the
triple. The mis-injection sweep (per the #79 caution) runs again — the new surfaces widen admission, so
verify no statement mis-injects. Single measure run at the end.

## §7 Out of scope

0000 (chained + compound-summation + question-arithmetic); multi-compound (highest-leverage but its own
increment); currency / rate / percent / fraction / simultaneous; q:complex (the ~48% ceiling, pending the
scheduled decomposition). q:difference stays deferred + fail-closed (locked by
`test_adr_0250_q_difference_failclosed.py`).

## §8 Open questions for the ruling

- **Q1** — target both 0148 + 0001 (two reference forms), or just one for the very first conversion and the
  other as fast-follow? (Plan: both — they share the spine + conditional-seed; the reference forms are small
  and independent. Recommend both, but one is a clean minimum.)
- **Q2** — conditional-seed-in-question: extend the existing `extract_conditional_op_question_candidates`,
  or a dedicated narrow extractor? (Plan: verify the existing path first; add narrow only if it can't bind a
  seeded reference fail-closed.)
- **Q3** — aggregate "the two other harbors combined": model as an explicit 2-peer sum bound to the "each"
  count, or refuse aggregates in increment 2 and drop 0001 to a later increment? (Plan: attempt the 2-peer
  sum fail-closed; if it can't be made unambiguous, 0148 alone is the first conversion.)
