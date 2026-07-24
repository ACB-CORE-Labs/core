# Band v3-MEM: the Socrates syllogism, decided (ADR-0258)

**Date:** 2026-07-23 · **Arc:** deduction-serve, band 4 of the cascade
**ADR:** ADR-0258 (Proposed) · **Flag:** `deduction_serving_enabled` (default off, unchanged)

## What CORE serves now (flag-on transcripts)

Decided, from the real `core chat` spine, rendered over the user's own
sentences — none of these were decidable yesterday:

> **Socrates is a man. All men are mortal. Therefore Socrates is mortal.**
> → Given: socrates is a man; all men are mortal. Your premises entail: socrates is mortal.

> **Tweety is a canary. All canaries are birds. No birds are reptiles.
> Therefore Tweety is not a reptile.**
> → …Your premises entail: tweety is not a reptile.

> **Socrates is mortal. All men are mortal. Therefore Socrates is a man.**
> → …Reading each name as one individual and each class word at face value,
> your premises don't settle whether socrates is a man — it holds in some
> cases and fails in others.

`ds-en-0022` — the eval-lane case pinned as `declined` purely for want of a
reading band — is promoted to decided (`entailed`), exactly as ADR-0257 §6.1
reserved.

## Mechanism (one new module, everything else reused)

`generate/proof_chain/member.py` — closed sentence grammar (singular
`<NAME> is [not] [a|an] <CLASS>` facts; `all|every|each`/`no` universals) +
**per-individual propositional lowering**: one opaque minted atom per
*(individual, class)* pair; every universal instantiates at every named
individual; the SAME verified ROBDD engine decides. Composer tier strictly
after v1 → v1b → v2-EN: monotone widening, previously-served arguments
byte-identical (v1 lane 28/28 unchanged).

**Soundness (ADR-0258 §3):** universal instantiation is truth-preserving in
every first-order model ⇒ ENTAILED/REFUTED/inconsistent served at full
strength (they even survive co-reference of distinct names — added premises,
monotone entailment). For this fragment (singular literals + A/E universals,
singular conclusion, Boolean reading) the lowering is also **complete**: a
propositional countermodel lifts to a first-order countermodel over exactly
the named individuals, so UNKNOWN is genuinely "not forced" — and its surface
still scopes itself to the disclosed reading.

**Number linking — the one semantic identification:** "all men" must bind "a
man". Two *attested* class forms identify iff related by a closed morphology
table (irregular + invariant rows consulted first — table membership makes it
the sole authority, killing specie/species and new/news over-links) then
three regular suffix rules. Under-linking costs coverage, never soundness.
This is CORE's first morphology table — the artifact class the tri-language
doctrine routes through pack ratification when grc/he siblings land.

**Refusal-first:** existential quantifiers and quantifier pronouns
(`some/everyone/nobody`), bare plurals ("Dogs are loyal"), definite
descriptions ("is the philosopher"), relative clauses, tense, mixed
connectives, universal conclusions — all typed refusals, never guesses.

## Earned, not flagged (ADR-0256 discipline)

- Four new shape-bands — `en_member_single/chain/negative/atomic` — each
  earned SERVE at the arena: **13 bands × 720 = 9,360 cases, wrong=0**,
  reliability 0.99087 ≥ θ_SERVE=0.99; ledger re-sealed
  (`chat/data/deduction_serve_ledger.json`, 13 bands, self-verifying sha).
- Arena gold is by-construction and cross-checked against the truth-table
  oracle over each template's INTENDED instantiated formulas — no reader in
  the loop (INV-25). The synthetic class lexicon deliberately exercises every
  number-table row-type, so the license certifies the linking relation too.
- New hand-authored real-English lane `evals/deduction_serve/v2_member/`
  (26 cases, content-disjoint): **26/26**, alongside v1 **28/28** and v2_en
  **26/26** (wrong=0 everywhere); report re-pinned.

## Verification

- `core test --suite deductive`: **127 passed** (41-test reader contract new).
- Practice arena: `all_bands_serve_licensed=True wrong_is_zero=True` (13 bands).
- Lane splits: v1 28/28 · v2_en 26/26 · v2_member 26/26.
- Smoke suite: green (pre-push gate).

## Scope-outs (deliberate, ADR-0258 §6)

Conditional–membership fusion; existential premises; tense + verb predicates
("Socrates runs"); identity/definite descriptions/co-reference. Each refuses
typed today — refusal telemetry marks which band pays next.
