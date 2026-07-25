# ADR-0261 — Band v6-EX: existential arguments, decided

- **Status:** Accepted — ratified by Joshua Shay via the `feat/existential-band` merge (`a8488e9c`, 2026-07-24)
- **Date:** 2026-07-24
- **Arc:** deduction-serve (ADR-0256 → 0257 → 0258 → 0259 → 0260 → this)
- **Governs:** `generate/proof_chain/exist.py`, the `en_exist_*` shape-bands,
  their arena templates, the `v2_exist` lane split, the `_exist_band_surface`
  serving tier, and the refuse-don't-drop contract of
  `generate.meaning_graph.projectors.to_syllogism`.

## 1. Context

The band cascade reads `all` and `no`; `some` refuses
(`quantifier_out_of_band`) in every fallback tier — ADR-0258 §6 listed
existentials as a deliberate scope-out, and the generalization arc
(docs/plans/generalization-arc-2026-07-24.md Phase 1.2) schedules them as the
move that completes the square of opposition.

Band v1b already decides categorical some-syllogisms — but only inside the
shared reader's morphology lexicon, and only for arguments that are purely
categorical. Real subject matter is neither: it mixes singular facts, verb
predicates, and vocabulary the lexicon has never seen. Everything outside that
narrow window refused.

Existentials are also the first construct in this arc whose lowering is not a
straightforward instantiation. A universal instantiates at things the argument
already names; an existential asserts a thing the argument does NOT name, and
an existential conclusion asks about things that may not be named at all. Get
that wrong in the obvious way — lower `some` over just the named individuals —
and the reader will report REFUTED for arguments that are merely unproven,
which is precisely the wrong-answer class this arc exists to prevent.

## 2. Decision

Add `generate.proof_chain.exist.read_exist_argument` as the LAST fallback tier
(after v1 / v1b / v2-EN / v3-MEM / v4-CM / v5-VP), extending v5-VP's
per-individual lowering — both atom families unchanged — with two new kinds of
domain element:

- **A witness per existential PREMISE** (a Skolem constant nothing else
  names): "some C1 are C2" ⇒ `mem(w,C1) & mem(w,C2)`; the O-form negates the
  second conjunct; the verb forms mint a verb atom instead.
- **One arbitrary element per existential CONCLUSION**: a domain element about
  which no premise asserts anything and at which every universal is still
  instantiated.

An existential conclusion lowers to the disjunction of its conjunction over
the WHOLE domain — named individuals, witnesses, and the arbitrary element.

New sentence shapes, all `some`-led:
`some <C> are|is [not] [a|an] <C2>` (I-form and O-form) and
`some <C> [do not] <verb> [<object>]`. Every other shape delegates verbatim to
v3-MEM's and v5-VP's parsers, refusals included.

Bands (priority order): `en_exist_negative` (any negative universal) >
`en_exist_chain` (≥2 universals) > `en_exist_universal` (exactly 1) >
`en_exist_witness` (no universals). Rendered by `render_entailment_exist` —
the verb surface with the no-existential-import reading disclosed in the
UNKNOWN template. Rides `deduction_serving_enabled` (default off); no new flag.

**Second decision, forced by the first (§5.1):** `to_syllogism` now REFUSES
when the comprehension carries a relation it cannot express, instead of
filtering that relation out and projecting the remainder.

## 3. Why this is sound

1. **ENTAILED.** Let *M* be any first-order model of the premises. Each
   witness is interpretable in *M* (its existential premise asserts a
   satisfier); universal instantiation is truth-preserving at every element;
   the arbitrary element may be interpreted as ANY element, domains being
   non-empty. So every lowered premise holds in *M*. If the lowered premises
   propositionally entail the query disjunction, some element of *M*
   satisfies the conjunction — which is ∃. Skolem constants occur nowhere in
   the original argument, so this is entailment-preserving Skolemization, not
   merely satisfiability-preserving.
2. **REFUTED — the arbitrary element is load-bearing.** Refuting ∃x φ(x)
   means deriving ∀x ¬φ(x). The lowered conjunction dual is entailed only if
   it is entailed at the arbitrary element, and that element is arbitrary (no
   premise mentions it), so what holds of it holds of every element — the
   universal is genuinely derived, never assumed by domain closure. Without
   it, "Rex is a wolf. Rex is not tame. Therefore some wolves are tame."
   would come back REFUTED — asserting that no wolf anywhere is tame — from a
   domain of one. With it, the honest UNKNOWN. This is the single most
   important line of this ADR and it is pinned by a named test.
3. **Completeness within the fragment** lifts exactly as v3-MEM/v5-VP: a
   propositional countermodel becomes a first-order countermodel whose domain
   is the named individuals, the witnesses, and the arbitrary element.
4. **No existential import.** Universals are read as vacuously true over an
   empty class, so the subaltern moods (Darapti, Felapton, Bamalip) are
   UNKNOWN, and the two contradictory pairs of the square are decided: an
   A-form REFUTES the corresponding O-form, an E-form REFUTES the I-form.
   This matches the modern first-order reading, matches what the categorical
   band (v1b) already does, and is the conservative choice — it declines to
   claim a member exists that no premise asserted. It is disclosed to the user
   in the UNKNOWN surface rather than left as a silent convention.
5. **The plural `do not` is read here and refused in v5-VP** — deliberately,
   not inconsistently. "All C do not V" is genuinely scope-ambiguous (¬∀ vs
   ∀¬) and refuses; "some C do not V" is unambiguously ∃x(C(x) ∧ ¬V(x)).
6. **Cascade honesty** — every arena template and lane case was verified to
   fall through all six earlier bands, so this tier is pure widening: every
   previously-served argument is served byte-identically. The one previously
   DECLINED case it now decides (`ds-mem-0020`) is promoted to its correct
   verdict, not a favorable one.

## 4. License and render

The four `en_exist_*` bands earned SERVE through the ADR-0199 arena
(720/band committed, wrong=0, θ_SERVE=0.99; ledger resealed at 25 bands).
The by-construction gold is cross-checked template-by-template against the
independent truth-table oracle over each template's INTENDED lowering — every
universal's per-element implications and every query disjunct spelled out — so
a lowering that drops or invents a domain element shows up as a disagreement
rather than passing silently (INV-25). Unearned or ledger-stripped deployments
serve the same sound answer hedged (`_UNVERIFIED_SHAPE_DISCLOSURE`).

## 5. Findings and scope-outs

### 5.1 A wrong-answer path found in Band v1b (fixed here)

Authoring this band's lane surfaced a defect in `to_syllogism` that predates
it. The projector built its premise list by FILTERING the meaning graph's
relations down to the categorical ones — silently discarding anything else,
then answering from what survived. Two consequences, both wrong served
answers rather than declines:

- "Aristotle is a philosopher. All philosophers are scholars. Therefore some
  scholars are philosophers." — the singular `member` premise was dropped, the
  argument lost its only witness, and serving replied *"That doesn't follow."*
  It does follow.
- "Every mineral is a solid. Some quartzes are minerals. Therefore some
  quartzes are solids." — the shared reader misreads "every mineral" as an
  individual named `every_mineral` (a separate reader gap, §5.2), the
  resulting `member` relation was dropped, and a valid Darii was served as
  *"That doesn't follow."*

The arena never caught it because the CATEGORICAL band's templates are all
purely categorical two-premise syllogisms in the synthetic lexicon — a family
in which nothing is ever dropped. A band can hold an earned license and still
have an unmeasured wrong-answer path if its practice corpus does not span its
reachable inputs; that lesson is the durable part of this finding.

The fix makes `to_syllogism` behave exactly like its propositional sibling
`to_deductive_logic`, which has always refused on a relation it cannot express:
**refuse, don't drop.** Refused texts fall through to the reader bands that CAN
hold a singular fact — v6-EX decides both examples correctly. The categorical
band re-earned SERVE at 720/720 after the change (no coverage lost), and both
examples are now pinned as regression cases (`ds-ex-0008`, `ds-ex-0011`, plus
a projector unit test and an e2e test).

### 5.2 Scope-outs (typed refusals today)

1. **"Every C is a D" misread by the shared reader** — `comprehend` reads the
   quantifier phrase as an individual (`every_mineral`). Post-§5.1 this is
   harmless (v1b refuses; v6-EX reads the sentence correctly through v3-MEM's
   universal parser), so it is recorded, not patched: fixing the shared
   reader's template set is its own unit of work with its own lane.
2. **Partitives** — "some of the sailors" refuses `partitive_out_of_band`
   rather than reading "of the sailors" as an opaque class run.
3. **Multi-token subjects in verb existentials, PPs, ditransitives** —
   `sentence_shape_out_of_band`, inherited from v5-VP's closed grammar.
4. **Tense** — `some C were P` / `some C did not V` refuse
   `tense_out_of_band`.
5. **Connective × existential composition** — "If some C are P then …"
   refuses `mixed_structure_out_of_band`; fusing v4-CM's connective grammar
   over existential leaves is a later composition.
6. **Numeric and proportional quantifiers** (`most`, `few`, `several`, `at
   least two`) — `quantifier_out_of_band`. `some` is the only existential
   spelling read; "there is a C that …" is not read either.
7. **Universal conclusions** — unchanged from v3-MEM: proving ∀ from these
   premises needs the eigenvariable machinery this band uses only for the
   refutation direction, and exposing it as a conclusion form is a separate,
   testable unit.
8. **Identity / co-reference, existential-import premises** — unchanged
   scope-outs; a user who wants the traditional square can state the
   existential premise explicitly and this band will use it.

## 6. Verification

- `tests/test_exist_argument_reader.py` — 33 tests: gap-is-real cross-check,
  flagship Darii lowering (exact formulas and atoms), the arbitrary-element
  soundness test, no-existential-import, both contradictory pairs, witness
  non-transfer, one-witness-per-premise, verb existentials with plural
  `do not`, number linking inside existentials, 4 band classifications, 13
  typed refusals incl. delegated v3-MEM/v5-VP reasons, honesty caps,
  determinism.
- `tests/test_meaning_graph_projectors.py` (+1) — the §5.1 refuse-don't-drop
  contract.
- Surface/e2e/lane: `tests/test_deduction_surface.py` (+5),
  `tests/test_deduction_serve_e2e.py` (+2, one of them the §5.1 regression),
  `tests/test_deduction_serve_lane.py` (+1 over the 32-case `v2_exist` split;
  `v2_member` docstring updated for the `ds-mem-0020` promotion) — full lane
  166/166, wrong=0, all six splits.
- Arena: 4 × 720 committed, wrong=0, first seal run; all 25 bands still SERVE;
  corpus soundness asserted against the independent oracle before sealing
  (18,000 cases).
