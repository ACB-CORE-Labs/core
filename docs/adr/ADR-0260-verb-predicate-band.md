# ADR-0260 — Band v5-VP: verb-predicate arguments, decided

- **Status:** Accepted — ratified by Joshua Shay via the PR #111 merge (`2a82c8a3`, 2026-07-24)
- **Date:** 2026-07-24
- **Arc:** deduction-serve (ADR-0256 → 0257 → 0258 → 0259 → this)
- **Governs:** `generate/proof_chain/verb.py`, the `en_verb_*` shape-bands,
  their arena templates, the `v2_verb` lane split, and the
  `_verb_band_surface` serving tier.

## 1. Context

ADR-0258 §6.3 scoped verb predicates out of the member band: v3-MEM reads
only copula sentences, so "All philosophers teach. Socrates is a
philosopher. Therefore Socrates teaches." refused — despite being the plain
English shape in which most non-logic subject matter states its rules
(physics, biology, and every other domain speak in verb sentences, not is-a
chains). The generalization arc (docs/plans/generalization-arc-2026-07-24.md
Phase 1.1) makes this the single highest-leverage reading unlock: Phase 2's
curriculum-entailment serving is gated on it.

The earlier bands each guard this territory out rather than misreading it:
v2-EN refuses quantifier-led sentences (`categorical_shape_out_of_band`),
is-a clauses (`membership_shape_out_of_band`), and unnormalized negation
(`internal_negation_unread`); v3-MEM/v4-CM refuse copula-free sentences
(`sentence_shape_out_of_band`). Pure verb-fact restatements with none of
those triggers are ALREADY decided soundly by v2-EN as opaque clause-atoms —
so this band's genuine territory is exactly the fall-through: arguments
mixing verb sentences with quantified rules, membership facts, or `does not`
negation.

## 2. Decision

Add `generate.proof_chain.verb.read_verb_argument` as the next fallback tier
(after v1 / v1b / v2-EN / v3-MEM / v4-CM), extending v3-MEM's
per-individual propositional lowering with a SECOND atom family in one
shared space:

- **Membership atoms** *(individual, class-group)* — minted by v3-MEM's own
  `_parse_singular` / `_parse_universal`, reused verbatim (copula sentences
  keep their exact v3-MEM reading, refusals included).
- **Verb atoms** *(individual, verb-lemma-group, object-term)* — minted from
  verb facts (`<name> <verb3sg> [<object>]`, `does not` negation, the
  sentential-not prefix) and verb universals
  (`all|every|each|no [the] <class> <verb> [<object>]`).

A verb universal instantiates at every named individual as
`mem(i, C) -> [~]verb(i)` — so a membership fact minted by a copula sentence
discharges a verb rule. The same verified ROBDD engine decides.

Bands (priority order): `en_verb_negative` (any negative universal, either
kind) > `en_verb_chain` (≥2 universals) > `en_verb_universal` (exactly 1) >
`en_verb_fact` (facts only). Rendered by `render_entailment_verb` — the
member surface with the UNKNOWN scoping extended to the verb reading. Rides
`deduction_serving_enabled` (default off); no new flag.

## 3. Why this is sound

1. **Instantiation** — identical to ADR-0258 §3: universal instantiation at
   named individuals is truth-preserving in every first-order model, and
   each *(verb-group, object-term)* pair is one opaque unary predicate over
   the same named-individual domain. ENTAILED / REFUTED / inconsistent
   verdicts over the lowered premises hold in every model of the original
   argument; completeness within the fragment lifts the same way (a
   propositional countermodel's domain is exactly the named individuals).
2. **Agreement is the ONE new identification** — a universal's base form
   ("teach") and a singular fact's 3sg form ("teaches") are identified iff
   related by a CLOSED relation: a verb-specific irregular table (has/have,
   goes/go, does/do; consulted first, sole authority for its tokens) else
   the three regular suffix rules (+s, +es after sibilants, y↔ies). The noun
   table is deliberately NOT reused — it would misroute verb forms like
   "lives" (noun: life; verb: live). Under-linking costs coverage, never
   soundness. Object terms link by exact token identity only.
3. **Scope-tight segmentation** — without a lexicon, an arbitrary
   copula-free token run cannot be soundly split into subject/verb/object;
   the band reads single-token name/class/verb/object shapes ONLY, and
   refuses everything longer, typed. A three-token sentence read as
   (subject, verb, object) is a disclosed reading, restated verbatim in the
   surface's "Given:" line.
4. **Cascade honesty** — every text this band decides was verified to be
   REFUSED by all four earlier bands (the arena templates and lane cases
   are constructed on the fall-through path serving actually uses), so this
   tier is pure widening: every previously-served argument is served
   byte-identically.

## 4. License and render

The four `en_verb_*` bands earned SERVE through the ADR-0199 arena
(720/band committed, wrong=0, θ_SERVE=0.99; ledger resealed at 21 bands).
The arena's by-construction gold is cross-checked template-by-template
against the independent truth-table oracle over each template's INTENDED
per-individual lowering, with no reader in the loop (INV-25). Unearned or
ledger-stripped deployments serve the same sound answer hedged
(`_UNVERIFIED_SHAPE_DISCLOSURE`), exactly as every earlier band.

## 5. Scope-outs (typed refusals today, future bands' territory)

1. **Connective × verb composition** — "If Socrates teaches then …"
   refuses `mixed_structure_out_of_band`; fusing v4-CM's connective grammar
   over verb leaves is the natural next composition.
2. **Multi-token subjects/objects, PPs, adverbs, ditransitives** —
   `sentence_shape_out_of_band`. Note one disclosed misreading inside the
   3-token shape: an adverb in object position ("Lena runs quickly") is
   read as an object TERM — never unsound (worst case an over-scoped
   UNKNOWN), documented here rather than guessed at.
3. **Tense** — `did not` refuses `tense_out_of_band`; bare past forms
   ("taught") are indistinguishable from lemmas without a lexicon and read
   as distinct opaque lemmas (under-linking, sound).
4. **Arity/subsumption** — "teaches" does not entail "teaches logic" (nor
   vice versa) under the face-value reading; both directions stay UNKNOWN,
   scoped. Same posture v2-EN already takes for opaque clauses.
5. **Plural/bare subjects in verb facts** ("dogs bark") — read as an
   individual named "dogs" (disclosed in the UNKNOWN scoping); the copula
   analogue is refused by v3-MEM's bare-plural guard, but no copula means no
   plural signal in the closed grammar.
6. Existential (`some`) witnesses, identity/co-reference — unchanged
   scope-outs inherited from ADR-0258 §6 (existentials are the
   generalization arc's Phase 1.2, assigned to the Opus tier).

## 6. Verification

- `tests/test_verb_argument_reader.py` — 34 tests: gap-is-real cross-check,
  flagship lowering, every agreement rule, object-in-atom-key, chain
  discharge, cross-individual non-leakage, family separation
  (teacher/teaches), 14 typed refusals incl. delegated v3-MEM reasons,
  honesty caps, determinism.
- Surface/e2e/lane: `tests/test_deduction_surface.py` (+5),
  `tests/test_deduction_serve_e2e.py` (+1),
  `tests/test_deduction_serve_lane.py` (+1 over the 28-case `v2_verb`
  split) — full lane 134/134, wrong=0, all five splits.
- Arena: 4 × 720 committed, wrong=0, first seal run; corpus soundness
  asserted against the independent oracle before sealing (15,120 cases).
