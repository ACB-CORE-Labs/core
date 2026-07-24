# ADR-0258 — Member-chain band (Band v3-MEM): singular membership + universal premises

- **Status:** Proposed
- **Date:** 2026-07-23
- **Relates to:** ADR-0257 (Band v2-EN — this is its scope-out #1), ADR-0256
  (earned license), ADR-0201 (ROBDD keystone), ADR-0175/0199 (calibrated
  learning / arena), ADR-0253 (dual-pack serve boundary — grc/he)

## 1. Context

ADR-0257 §6.1 reserved the classic instantiation syllogism as the next band:

> "Socrates is a man. All men are mortal. Therefore Socrates is mortal."

Band v2-EN refuses it (`membership_shape_out_of_band` — an `is a|an` clause
announces internal structure the opaque band must not flatten), Band v1b's
categorical decider has no notion of an *individual* (its terms are classes),
and the v1 propositional reader declines multi-word names. The eval lane pins
the gap: `ds-en-0022` is gold-`declined` purely for want of a reading band.
The engine underneath was never the limit.

## 2. Decision

Add a dedicated **member-argument reader + per-individual propositional
lowering** (`generate/proof_chain/member.py`), used ONLY by the deduction
serving path as a fallback tier strictly AFTER Bands v1 / v1b / v2-EN (so
every previously-served argument is byte-identical; this band only widens):

- **Closed sentence grammar** (function-word dispatch, refusal-first):
  - Singular fact — `<NAME> is [not] [a|an] <CLASS>` (contractions expanded,
    plus the sentential `it is not the case that <singular>` prefix). `<NAME>`
    and `<CLASS>` are opaque token runs; `is` only (no tense in v1).
  - Universal — `all|every|each <C1> are|is [a|an] <C2>` (affirmative A-form)
    and `no <C1> are|is [a|an] <C2>` (negative E-form).
  - Conclusion — final sentence, sole `therefore`-led, **singular form only**.
- **Per-individual propositional lowering:** collect the named individuals
  (subjects of singular sentences, conclusion included); mint one opaque atom
  per *(individual, class)* pair; each universal instantiates at EVERY named
  individual — `A(C1,C2)` ⇒ `mem(i,C1) -> mem(i,C2)`, `E(C1,C2)` ⇒
  `mem(i,C1) -> ~mem(i,C2)` for each `i`; singular facts are literals. The
  same verified ROBDD engine decides; deterministic templates render the
  verdict over the user's own sentences
  (`generate/proof_chain/render.py::render_entailment_member`).
- **Number linking (the one semantic identification this band performs):**
  a universal's class word is usually plural ("all men") while the singular
  fact uses the singular ("a man"). Two *attested* class tokens are identified
  iff related by a **closed morphology table** — a curated irregular/invariant
  table (men↔man, people↔person, children↔child, …; invariants like sheep,
  species, news map only to themselves) consulted FIRST, then the three
  regular suffix rules (`+s`, `+es` after sibilants, `y↔ies`). Table priority
  kills the over-link hazards (specie/species, new/news); anything the closed
  relation cannot relate stays distinct — under-linking costs coverage
  (honest UNKNOWN), never soundness. Linking is per-token, so multi-token
  classes ("guard dog"↔"guard dogs") link on the head noun.
- **Four new shape-bands** — `en_member_single` (exactly 1 universal),
  `en_member_chain` (≥2 universals), `en_member_negative` (any E-form),
  `en_member_atomic` (0 universals); priority negative > chain > single >
  atomic — each **earning its own SERVE license** through the ADR-0199 arena
  at n=720/band wrong=0, sealed into the same ratified ledger (unlicensed ⇒
  automatically hedged, per ADR-0256).

## 3. Why the lowering is sound (the load-bearing argument)

1. **Universal instantiation is sound.** Every first-order model of
   `∀x (C1(x) → C2(x))` satisfies its instantiation at each named individual,
   so any model of the premises is a model of the lowered premise set. An
   ENTAILED/REFUTED/inconsistent verdict over the lowered set therefore holds
   in every model of the original premises — served at full strength. Both
   verdicts survive even if two distinct names co-refer: adding equality
   facts only ADDS premises, and entailment is monotone.
2. **For this closed fragment the lowering is also complete.** With premises
   restricted to singular literals and A/E universals (Boolean reading, no
   existential import) and a singular conclusion, a propositional countermodel
   lifts to a first-order countermodel whose domain is exactly the named
   individuals — every universal holds because every element is a named
   individual whose instantiation holds. So UNKNOWN means genuinely not
   forced *within the disclosed reading* — it is never an artifact of
   instantiating too little.
3. **UNKNOWN is still the one guarded verdict.** Two readings could settle
   what the lowering leaves open: distinct names might co-refer, and class
   words the closed relation didn't link might be the same class. The UNKNOWN
   surface therefore scopes itself — *"Reading each name as one individual
   and each class word at face value…"* — same discipline as v2-EN's
   indivisible-clause scoping (ADR-0257 §3).
4. **Existential forms refuse out of band.** `some/most/any/…`-led sentences
   assert anonymous witnesses that per-individual lowering cannot represent —
   `quantifier_out_of_band`, typed. Pure categorical arguments stay with
   Band v1b (tried first, unchanged).

Structural guards (closed refusal vocabulary, all typed): `quantifier_out_of_band`,
`bare_plural_out_of_band` ("Dogs are loyal" — implicit genericity is a reading
this band refuses to guess), `definite_description_out_of_band` ("is the …" is
identity, not membership), `relative_clause_out_of_band` (`that/which/who`
inside a name or class), `universal_conclusion_out_of_band` (categorical
conclusions belong to v1b), `mixed_structure_out_of_band` (`if/or/either/and`
— conditional-membership fusion is a future band), `internal_negation_unread`,
`structural_leak`, `sentence_shape_out_of_band`, plus the v2-EN sentence
discipline (`question_sentence`, `no_conclusion`, `multiple_conclusions`,
`conclusion_not_last`, `no_premises`, `empty_side`, `empty`) and the honesty
caps (`too_many_premises` at 16, `too_many_atoms` at 24 minted pairs — refuse,
never truncate).

## 4. What the earned licenses certify

Same posture as ADR-0257 §4: the license certifies READER fidelity per shape
(the engine cannot be wrong; the reader can hand it the wrong problem). The
arena corpus is synthetic names × a class lexicon chosen to exercise every
row-type of the morphology table (irregular, invariant, `+s`, `+es`, `y↔ies`);
gold is authored by construction and cross-checked against the truth-table
oracle over the template's INTENDED instantiated formulas — no reader in the
loop (INV-25). The hand-authored real-English eval lane
(`evals/deduction_serve/v2_member/`, content disjoint from the synthetic
lexicon) keeps the structural-fidelity claim honest against natural prose,
including the promoted `ds-en-0022` (declined → entailed: this band's designed
acceptance case).

## 5. Tri-language posture

Unchanged from ADR-0257 §5 — with one addition: the number-linking table is
CORE's **first morphology table**, and it is exactly the artifact class the
tri-language doctrine says must eventually enter through pack ratification
(ADR-0253). English needs ~30 closed rows; Greek/Hebrew declension is where a
curated morphology pack stops being optional. When a `grc_*`/`he_*` member
band is built, the table moves from module constants to a ratified pack; no
premature parameterization now.

## 6. Scope-outs (deliberate)

1. **Conditional–membership fusion** ("If Socrates is a man then …") —
   refuses `mixed_structure_out_of_band`; a future band composes the v2-EN
   connective grammar with this band's sentence readings.
2. **Existential premises/conclusions** (`some …`) — needs witness semantics;
   pure categorical `some` stays with Band v1b.
3. **Tense** (`was/were`) and **verb predicates** ("Socrates runs") — refuse;
   verb morphology is ADR-0257 scope-out #2's territory.
4. **Identity / definite descriptions / co-reference** — refuse
   (`definite_description_out_of_band`); an equality-aware band is future work.
5. **Flag posture unchanged:** rides `deduction_serving_enabled` (default
   off); no new flag.

## 7. Verification

- `uv run core test --suite deductive -q` — reader contract, surfaces,
  license, all three lane splits, e2e through `ChatRuntime`.
- Practice arena: 13 bands × 720 = 9,360 cases, wrong=0 required for every
  band; ledger re-sealed (`chat/data/deduction_serve_ledger.json`).
- Eval lane: v1 28/28, v2_en 26/26 (ds-en-0022 promoted), v2_member new —
  wrong=0; report re-pinned (`scripts/verify_lane_shas.py`).
