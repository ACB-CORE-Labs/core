# ADR-0259 — Conditional-membership fusion band (Band v4-CM)

- **Status:** Accepted — ratified by Joshua Shay via the PR #109 merge (`5224b5e0`, 2026-07-24)
- **Date:** 2026-07-23
- **Relates to:** ADR-0258 (Band v3-MEM — this is its scope-out #1), ADR-0257
  (Band v2-EN — the connective grammar this band reuses), ADR-0256 (earned
  license), ADR-0201 (ROBDD keystone), ADR-0175/0199 (calibrated learning /
  arena)

## 1. Context

ADR-0258 §6.1 reserved conditional–membership fusion as a future band:

> "If Socrates is a man then Socrates is mortal. Socrates is a man.
> Therefore Socrates is mortal."

Band v3-MEM refuses this — `mixed_structure_out_of_band` — because its
per-sentence grammar treats a connective token (`if`/`then`/`or`/`and`/
`either`) anywhere in a sentence as announcing structure that band does not
compose. Band v2-EN refuses the same text for the complementary reason:
its opaque-atom minter explicitly rejects `is [a|an]` clauses
(`membership_shape_out_of_band`) rather than flattening membership
structure it cannot read. Each band is individually sound and, by design,
refuses exactly what the other reads — the gap is the composition, not
either reader's engine.

## 2. Decision

Add `generate/proof_chain/cond_member.py` — a third reader, tried strictly
AFTER Bands v1 / v1b / v2-EN / v3-MEM (a fallback tier; every previously
served argument stays byte-identical) — that composes v2-EN's connective
grammar (`if/then`, `or`, `and`, `either` sugar, top-level `and`-splitting)
with v3-MEM's singular membership sentence reading, over the SAME
per-individual atom space:

- **Sentence dispatch** (closed, ordered): a bare top-level `X and Y`
  premise (no `if`/`or` anywhere) splits into independent singular
  records, exactly as v2-EN does — semantically conjoining, keeping the
  connective inventory the shape-bands classify over uncluttered. Any
  OTHER sentence containing a connective token is parsed by the ported
  junction/conditional grammar below. A universal-lead (`all|every|each|
  no`) sentence with NO connective token is a bare universal, read
  UNCHANGED by v3-MEM's own `_parse_universal`. Everything else is a bare
  singular fact, read UNCHANGED by v3-MEM's own `_parse_singular` (which
  already normalizes every negation form this band needs — leading `not`,
  the sentential `it is not the case that` prefix, and copular `is not`).
  Checking for a connective token BEFORE the universal-lead dispatch (not
  after) is load-bearing: it is what stops a connective token from ever
  silently leaking into an opaque name/class run.
- **Connective grammar over membership leaves:** `if <A> then <B>` and
  `<A> or <B>` / `<A> and <B>` (with `either` as sugar, mixed `and`+`or` at
  one level refused as `ambiguous_and_or`, a conditional nested inside
  another refused as `nested_conditional` — identical restrictions to
  v2-EN, ported verbatim) build a small formula tree (`_Lit` / `_And` /
  `_Or` / `_Implies`) whose LEAVES are v3-MEM singular facts, not opaque
  atoms. Because `_parse_singular` is negation-aware on its own, this
  band's grammar needs no separate negation layer — v2-EN needs one only
  because ITS leaf-miller (`_AtomTable.mint`) is negation-blind.
- **A conclusion stays a single singular fact** (optionally negated),
  matching v3-MEM's existing discipline exactly: a universal or
  connective-shaped conclusion refuses
  (`universal_conclusion_out_of_band` / new `compound_conclusion_out_of_band`)
  rather than attempting a compound render.
- **One shared per-individual atom space:** every singular fact — whether
  a bare sentence, an and-split part, or a leaf nested inside a connective
  tree — contributes to the SAME two-pass lowering v3-MEM already performs
  (collect named individuals and closed-morphology class-groups first,
  THEN mint one opaque atom per attested `(individual, class)` pair, THEN
  instantiate every bare universal at every named individual). A bare
  universal may now instantiate at an individual named ONLY inside a
  connective's leaf, and a connective's leaf atom may now UNIFY with an
  atom a bare universal's instantiation also produced — this atom-sharing
  across the two mechanisms is the fusion the band is named for, and nothing
  about it is a new soundness claim: it is the same per-individual
  instantiation ADR-0258 §3 already proved sound, applied to a strictly
  larger set of premise formulas.
- **Four new shape-bands**, priority order first-match: `en_condmem_fused`
  (a bare universal coexists with a connective sentence — the mechanism
  above genuinely fires), `en_condmem_disjunctive` (an `or` appears
  anywhere in any connective sentence), `en_condmem_chain` (two or more
  connective sentences, no universal, no `or`), `en_condmem_conditional`
  (the base case — exactly one `if/then`, no universal, no `or`). A
  successfully-decided argument in this band always contains at least one
  connective sentence — every other reason v3-MEM would refuse also makes
  THIS reader refuse identically (it reuses v3-MEM's own
  `_parse_universal`/`_parse_singular`, guards included), so there is no
  connective-free case this band could newly decide; no fifth "atomic"
  band is needed.

## 3. Why the composition is sound (the load-bearing argument)

1. **Nothing here is a new inference rule.** Every connective (`&`, `|`,
   `->`) is standard propositional structure the ROBDD engine already
   decides; every leaf is a v3-MEM singular-membership atom, minted and
   linked by the IDENTICAL closed morphology relation ADR-0258 §3 already
   proved sound and (for this fragment) complete. Composing them is
   substitution of one sound reading's atoms into another sound reading's
   connective positions — the propositional engine's soundness does not
   care which reader supplied which formula string.
2. **Universal instantiation stays sound when the instantiated individual
   is named only inside a connective.** ADR-0258 §3's argument — every
   first-order model of `∀x(C1(x)→C2(x))` satisfies the instantiation at
   every domain element, so at every NAMED individual in particular — does
   not depend on WHERE in the argument that individual's name appears. An
   individual introduced solely as the subject of an `if`-clause leaf is
   still a named individual; instantiating a bare universal at it is still
   a sound consequence of the universal, exactly as if it had appeared in
   its own bare sentence.
3. **Completeness is preserved for the same closed fragment.** The
   fragment is unchanged from ADR-0258 (singular literals + A/E
   universals, Boolean reading, no existential import) with one syntactic
   widening: singular literals may now be combined by `&`/`|`/`->` before
   appearing as a premise or antecedent/consequent. A propositional
   countermodel still lifts to a first-order countermodel over exactly
   the named individuals, by the identical argument — connectives among
   already-Boolean atoms do not change what "every element is a named
   individual" needs to guarantee. UNKNOWN therefore still means genuinely
   not forced within the disclosed reading, and the surface still scopes
   itself exactly as v3-MEM's does (reused verbatim — see §4).
4. **The refusal vocabulary stays a strict superset of v3-MEM's, plus
   v2-EN's connective-shape guards.** `nested_conditional` and
   `ambiguous_and_or` are v2-EN's own restrictions, ported unchanged
   (English `and`/`or` scope genuinely is ambiguous when mixed; a
   conditional nested inside another is refused rather than guessed at,
   in both bands identically). `compound_conclusion_out_of_band` is new
   and narrow: it exists only to keep the conclusion a single renderable
   fact, not to hide any inference.

## 4. What the earned licenses certify; rendering

Same posture as ADR-0258 §4: the license certifies reader fidelity, not
engine soundness. `render_entailment_member` (ADR-0258) is reused
UNCHANGED for this band's surface — its UNKNOWN scoping ("reading each
name as one individual and each class word at face value…") is exactly as
accurate here, since every clause in this band's arguments is read all the
way down to individual+class; connectives introduce no additional hidden
structure the surface would need to disclose. No new render function is
added.

## 5. Scope-outs (deliberate)

1. **A universal clause cannot be nested inside a connective** — only a
   bare top-level universal sentence instantiates; `if all men are
   mortal then …` refuses (typed, via the same connective-shape-first
   dispatch that protects bare universals from silent corruption).
   Composing a QUANTIFIED antecedent/consequent is a larger, separate
   question (it would need bound-variable tracking across clauses, not
   just shared individuals) and is left for a future band if a real case
   ever needs it.
2. **Existential premises, tense, verb predicates, identity/definite
   descriptions** — unchanged scope-outs, inherited from ADR-0258 §6
   via the reused `_parse_singular`/`_parse_universal`.
3. **Flag posture unchanged:** rides `deduction_serving_enabled` (default
   off); no new flag.

## 6. Verification

- `uv run core test --suite deductive -q` — reader contract, surfaces,
  license, all four lane splits, e2e through `ChatRuntime`.
- Practice arena: 17 bands × 720 = 12,240 cases, wrong=0 required for every
  band; ledger re-sealed (`chat/data/deduction_serve_ledger.json`).
- Eval lane: v1 28/28, v2_en 26/26, v2_member 26/26, v2_condmem new —
  wrong=0; report re-pinned (`scripts/verify_lane_shas.py`).
