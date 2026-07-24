# Band v5-VP — verb-predicate arguments, decided (ADR-0260)

**Date:** 2026-07-24 · **Branch:** `feat/verb-predicate-band` (stacked on
`feat/generalization-phase0`) · **Arc:** generalization
(docs/plans/generalization-arc-2026-07-24.md, Phase 1.1 — Tier F)

## What CORE can now do

```
> All philosophers teach. Socrates is a philosopher. Therefore Socrates teaches.
Given: all philosophers teach; socrates is a philosopher.
Your premises entail: socrates teaches.
```

Verb sentences — the shape in which every non-logic subject states its
rules — now read and decide. The cascade's earlier bands each guard this
territory out (v2-EN refuses quantifier leads / is-a clauses / `does not`;
v3-MEM and v4-CM refuse copula-free sentences), so the tier is pure
widening on the fall-through path.

## Mechanism (ADR-0260 §2)

v3-MEM's per-individual lowering, extended with a second atom family in ONE
shared space: membership atoms *(individual, class-group)* — minted by
v3-MEM's own parsers reused verbatim — plus verb atoms *(individual,
verb-lemma-group, object-term)*. A verb universal instantiates at every
named individual as `mem(i,C) -> [~]verb(i)`, so a copula-minted membership
fact discharges a verb rule. The ONE new semantic identification is 3sg
agreement: a closed verb relation (irregular table has/goes/does first, then
+s / +es-after-sibilant / y↔ies) links "teach"↔"teaches". The noun table is
deliberately NOT reused — it would misroute "lives" (noun: life; verb:
live). Everything the relation cannot relate stays distinct: under-linking
costs coverage, never soundness.

Segmentation is scope-tight: single-token name/class/verb/object shapes
only (`<name> <verb> [<obj>]`, `does not`, sentential-not, `all|every|each|
no [the] <class> <verb> [<obj>]`); anything longer refuses typed — without a
lexicon there is no sound split of an arbitrary copula-free run.

## Earned licenses

Four new bands — `en_verb_universal`, `en_verb_chain`, `en_verb_negative`,
`en_verb_fact` — each 720/720 committed, wrong=0, first seal run; ledger
resealed at **21 bands** (12,240 + 2,880 committed). The synthetic verb pool
exercises every rule of the closed agreement relation, so the license
certifies the linking itself. Corpus soundness asserted case-by-case against
the independent truth-table oracle over each template's INTENDED lowering
(no reader in the loop, INV-25) before sealing.

Lane: `evals/deduction_serve/v2_verb` — 28 hand-authored real-English cases
(11 entailed / 4 refuted / 5 unknown / 8 declined), 28/28 first run; full
lane now 134/134 wrong=0 across five splits. Gates: verb reader tests 34,
deduction battery 86, smoke + warmed_session via pre-push.

## Wrinkles worth surfacing

1. **Adverb-as-object misreading (disclosed, not fixed):** "Lena runs
   quickly" parses as verb+object ("quickly" an opaque term). Never unsound
   — worst case an over-scoped UNKNOWN — but it is a real misreading the
   3-token shape cannot detect without a lexicon. ADR-0260 §5.2 documents
   it; the vocab-boundary instrument (plan Phase 3.1) is where a principled
   fix would come from.
2. **Arity subsumption stays UNKNOWN:** "teaches" ⊬ "teaches logic" and
   conversely — the face-value posture v2-EN already takes, now visible on
   verbs. A human reads the intransitive as subsuming; the scoped UNKNOWN
   phrasing carries the honesty.
3. **Plural verb-fact subjects read as individuals:** "dogs bark" is an
   individual named "dogs" in this fragment (no copula ⇒ no plural signal in
   the closed grammar). The membership analogue stays refused by v3-MEM's
   bare-plural guard.
4. **`doesn't` is not expanded** by the shared tokenizer's contraction
   table (only isn't/aren't/wasn't/weren't are) — so "The engine doesn't
   start" still refuses via the `n't` guard, preserving the e2e
   out-of-regime test byte-for-byte. Adding verb contractions is a
   deliberate non-goal until the tense scope-out is faced whole.

## Stacking note

This branch stacks on `feat/generalization-phase0` (merge that PR first):
both touch `scripts/verify_lane_shas.py` / `CLAIMS.md`, and the claims
generator's `_LANE_ADR` fix lands there.

## Next (per the plan's tier assignment)

Tier O (Opus): Band v6-EX existential witnesses (Phase 1.2), then the
Phase-2 physics lane against the §4 curriculum-entailment contract — for
which this band was the gate.
