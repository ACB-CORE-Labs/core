# Band v4-CM: conditional-membership fusion, decided (ADR-0259)

**Date:** 2026-07-23 · **Arc:** deduction-serve, band 5 of the cascade
**ADR:** ADR-0259 (Proposed) · **Flag:** `deduction_serving_enabled` (default off, unchanged)

## What CORE serves now (flag-on transcripts)

Decided, from the real `core chat` spine, over the user's own sentences —
the exact gap ADR-0258 §6.1 reserved:

> **If Socrates is a man then Socrates is mortal. Socrates is a man.
> Therefore Socrates is mortal.**
> → Given: if socrates is a man then socrates is mortal; socrates is a man.
> Your premises entail: socrates is mortal.

The genuine fusion case — a bare universal's instantiated atom UNIFYING
with a connective leaf's atom, something neither v2-EN nor v3-MEM alone can
decide:

> **All men are mortal. If Socrates is a philosopher then Socrates is a
> man. Socrates is a philosopher. Therefore Socrates is mortal.**
> → …Your premises entail: socrates is mortal.

> **If Socrates is a man then Socrates is mortal. Therefore Socrates is
> mortal.** *(the antecedent is never asserted)*
> → …Reading each name as one individual and each class word at face
> value, your premises don't settle whether socrates is mortal — it holds
> in some cases and fails in others.

That last one is `ds-mem-0024` — the eval-lane case pinned `declined`
purely for want of a reading band, now promoted. It is the **first
promotion in this corpus that does not land on `entailed`**: the band now
reads the text, and the honest answer for THAT specific text is UNKNOWN
(no premise ever asserts the antecedent). Promotion means "now decided
correctly," not "now decided favorably."

## Mechanism (one new module, everything else reused)

`generate/proof_chain/cond_member.py` composes v2-EN's connective grammar
(`if/then`, `or`, `and`, `either`) with v3-MEM's singular-membership
sentence reading, over ONE shared per-individual atom space. Concretely:
a sentence is checked for a connective token BEFORE the universal-lead
check (so a stray connective can never leak into an opaque universal/
singular name run); a bare top-level `and` premise still splits into
independent facts (v2-EN's own discipline); everything else containing
`if`/`then`/`or`/`either` builds a small formula tree (`Lit`/`And`/`Or`/
`Implies`) whose LEAVES are v3-MEM singular facts — parsed by v3-MEM's own
`_parse_singular`, reused verbatim, which is already negation-aware (unlike
v2-EN's opaque-atom minter, so this band needs no separate negation layer).
The SAME two-pass lowering v3-MEM already performs — collect named
individuals and closed-morphology class-groups, THEN mint atoms, THEN
instantiate every bare universal at every named individual — now also
scans leaves nested inside connective trees, which is what lets a
universal instantiate at an individual named only inside an `if`-clause,
and lets a connective leaf's atom unify with one a universal's
instantiation also produced.

**Soundness (ADR-0259 §3):** nothing here is a new inference rule — every
connective is standard propositional structure the ROBDD engine already
decides; every leaf is minted and linked by the IDENTICAL closed
morphology relation ADR-0258 §3 already proved sound and, for this
fragment, complete. Universal instantiation stays sound regardless of
WHERE a named individual's name appears in the argument; composing
connectives over already-Boolean membership atoms does not change what
"every element is a named individual" needs to guarantee for completeness.
UNKNOWN is rendered by `render_entailment_member` UNCHANGED — no new
render function; its scoping is exactly as accurate here.

## Earned, not flagged (ADR-0256 discipline)

- Four new shape-bands — `en_condmem_fused/disjunctive/chain/conditional`
  — each earned SERVE at the arena: **17 bands × 720 = 12,240 cases,
  wrong=0**, reliability 0.99087 ≥ θ_SERVE=0.99; ledger re-sealed
  (`chat/data/deduction_serve_ledger.json`, 17 bands, sha `6285a423…`).
  Priority order fused > disjunctive > chain > conditional; a successfully-
  decided argument in this band always contains ≥1 connective sentence (any
  other refusal reason v3-MEM would hit, this band hits identically, via
  the SAME reused guards), so no fifth "atomic" band is needed.
- Arena gold is by-construction and cross-checked against the truth-table
  oracle over each template's INTENDED formulas — no reader in the loop
  (INV-25). The FUSED templates specifically encode the cross-mechanism
  unification (verified by hand-trace against the real reader before
  writing gold, then confirmed by the independent oracle).
- New hand-authored real-English lane `evals/deduction_serve/v2_condmem/`
  (26 cases, content-disjoint): **26/26**, alongside v1 **28/28**, v2_en
  **26/26**, and v2_member **26/26** (wrong=0 everywhere; the promoted
  `ds-mem-0024` now scores against its corrected `unknown` gold).

## Verification

- `uv run core test --suite deductive -q`: **160 passed** (31-test reader
  contract new: flagship, modus tollens, both disjunctive spellings, the
  and-split-is-not-a-connective case, two-hop chains, the fusion mechanism
  itself — including a no-leak-across-individuals check — band
  classification, the full refusal vocabulary, both honesty caps,
  determinism).
- Practice arena: `all_bands_serve_licensed=True wrong_is_zero=True` (17
  bands).
- Lane splits: v1 28/28 · v2_en 26/26 · v2_member 26/26 (post-promotion) ·
  v2_condmem 26/26.
- Smoke suite: **180 passed**. Warmed-session lane: **10 passed**.

## A wrinkle worth surfacing

`scripts/verify_lane_shas.py --update` was run once to re-pin
`deduction_serve_v1` and, because the flag updates every lane in one pass,
it also silently rewrote `miner_loop_closure`, `curriculum_loop_closure`,
and `demo_composition`'s pins and DROPPED `public_demo`'s pin entirely
(that lane errored — `all_claims_supported=False` — a known flake). Those
three rewrites were reverted; **only** the `deduction_serve_v1` line was
hand-edited to the freshly-computed SHA. The three lanes' drift is
real, pre-existing, and unrelated to this arc (this worktree branched
directly off the just-merged main) — it is reported here, not fixed, since
diagnosing it is outside this band's scope and blind re-pinning is exactly
what the tool's own remediation text warns against.

## Scope-outs (deliberate, ADR-0259 §5)

A universal clause cannot be nested inside a connective (only a bare
top-level universal instantiates) — composing a quantified antecedent/
consequent would need bound-variable tracking across clauses, a larger
question left for a future band if a real case needs it. Existential
premises, tense, verb predicates, identity/definite descriptions remain
out of band, inherited unchanged from ADR-0258.
