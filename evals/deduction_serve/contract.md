# Deduction-serve lane contract

## What this lane scores

The **production serving decider** — the exact pipeline
`chat/deduction_surface.py::deduction_grounded_surface` runs on a
`core chat` turn: `looks_like_deductive_argument` (commit gate) →
`comprehend` (reader) → the band cascade — `to_deductive_logic` (Band v1)
→ `to_syllogism` + the categorical decider (Band v1b, ADR-0256) →
`read_english_argument` (Band v2-EN, ADR-0257) → `read_member_argument`
(Band v3-MEM, ADR-0258) → `read_cond_member_argument` (Band v4-CM,
ADR-0259) → `read_verb_argument` (Band v5-VP, ADR-0260) →
`read_exist_argument` (Band v6-EX, ADR-0261) — with
`evaluate_entailment_with_trace` (the ROBDD engine,
ADR-0201/ADR-0218) deciding every band.
`evals/deduction_serve/runner.py::decide` calls these functions directly
(typed outcome, not rendered prose) — the same production decision the
composer makes, without re-deriving the presentation step
(`generate.proof_chain.render`), so this lane's pinned bytes stay stable
against wording-only changes.

## Splits

- `v1/` — the original corpus (single-token propositional + categorical).
- `v2_en/` — hand-authored REAL-English clause arguments (ADR-0257);
  content disjoint from the synthetic practice lexicon.
- `v2_member/` — hand-authored membership/universal arguments (ADR-0258),
  incl. real nouns across every number-link row-type.
- `v2_condmem/` — hand-authored conditional-membership arguments
  (ADR-0259): v2-EN's connective grammar composed over v3-MEM's singular-
  membership sentence reading, incl. genuine universal+connective fusion
  cases (a bare universal's instantiated atom unifying with a connective
  leaf's atom).
- `v2_verb/` — hand-authored verb-predicate arguments (ADR-0260): verb
  universals discharged by membership facts across every closed agreement
  rule (+s, +es, y↔ies, irregular go/goes), transitive objects at face
  value, and eight typed decline shapes.
- `v2_exist/` — hand-authored existential arguments (ADR-0261): the square
  of opposition (Darii, Ferio, both contradictory pairs, the
  no-existential-import subaltern), witnesses that never transfer to a
  named individual, the arbitrary element that keeps an existential
  conclusion's domain open, and eleven typed decline shapes.

This is **distinct** from two existing lanes that sound similar:

- `evals/deductive_logic` scores the bare `entail.py` engine against
  hand-authored **formula strings** — it never touches the reader.
- `evals/comprehension/propositional_runner.py` scores **reader fidelity**
  by running the reader's projection through the **independent oracle**
  (`evals.deductive_logic.oracle`) as the decision procedure.

This lane is the only one that scores the **production ROBDD engine**
(`entail.py`, not the oracle) end-to-end from raw text — proving the
capability `core chat` actually serves, not just its parts in isolation.

## Gold vocabulary

Four classes: `entailed`, `refuted`, `unknown`, `declined`.

`declined` covers every honest non-commitment: inconsistent premises
(REFUSED), an out-of-band shape (categorical/syllogism, multi-word
English propositions, nested negation inside an `if/then` clause — see
"Known Band v1 boundaries" below), or a shape that doesn't even commit
the turn (`looks_like_deductive_argument` false — not exercised by this
corpus, since every committed case reads as an argument by design).

## wrong=0 discipline

- **`wrong`** — the pipeline committed to a definite `entailed`/`refuted`/
  `unknown` verdict that disagrees with gold. **Must stay 0.**
- **`declined` (mismatch)** — the pipeline declined on a case gold expected
  a definite verdict for. Not a `wrong` (never a confabulation), but not a
  pass either — the runner requires `correct == n` (every case's outcome
  class matches gold exactly, including declines matching `declined` gold).
- A case that gold marks `declined` and the pipeline also declines is
  `correct` — the lane rewards honest recognition of the boundary, not
  just committed accuracy.

## Band-boundary history this corpus documents

Boundaries are DISCOVERED as declines, then PROMOTED to decided gold when
a later band earns the shape (the corpus keeps the case, renamed
`…_formerly_out_of_band`). Promotion does not always mean "→ entailed":
the promoted gold is whatever the newly-earned band actually, honestly
decides for that exact text.

- **Nested negation inside `if/then`** — a shared-reader grammar limit
  (`not` is reserved inside if/then slots); `ds-v1-0006` declined until
  Band v2-EN decided it (promoted, ADR-0257).
- **Multi-word English propositions** — `ds-v1-0025` declined until Band
  v2-EN (promoted, ADR-0257).
- **Categorical/syllogism shapes** — `ds-v1-0023/0024/0026`, decided by
  Band v1b since ADR-0256.
- **`is a` membership** — `ds-en-0022` declined until Band v3-MEM decided
  it (promoted, ADR-0258).
- **A bare conditional over membership clauses** — `ds-mem-0024`
  (`"If Socrates is a man then Socrates is mortal. Therefore Socrates is
  mortal."`) declined (`mixed_structure_out_of_band`) until Band v4-CM
  landed (ADR-0259), which reads it — but the antecedent is never
  asserted, so its honest verdict is **UNKNOWN**, not entailed. Promoted
  declined → unknown, renamed `conditional_no_anchor_formerly_out_of_band`
  — the first promotion in this corpus that does not land on `entailed`,
  because the promoted band's own correct answer for THIS text is a
  non-commitment, not a new capability to showcase.
- **Verb predicates** — refused by every band until Band v5-VP (ADR-0260)
  decided them (`v2_verb/`). NO existing case promoted: every remaining
  decline in the older splits uses contraction negation ("doesn't" — not
  in the shared tokenizer's expansion table, so v5's `n't` guard refuses
  identically) or structure v5 also guards out; the full lane's prior
  splits stayed byte-stable.
- **Existential quantifiers** — refused by every band until Band v6-EX
  (ADR-0261) decided them (`v2_exist/`). ONE case promoted: `ds-mem-0020`
  (`"Some men are wise. Socrates is a man. Therefore Socrates is wise."`),
  declined (`quantifier_out_of_band`) since ADR-0258, is now read — and its
  honest verdict is **UNKNOWN**, since an anonymous witness never transfers
  to a named individual. Promoted declined → unknown, renamed
  `exist_witness_does_not_transfer`. The other splits stayed byte-stable.
- **Band boundary with v1b** — a purely categorical some-syllogism whose
  every term is in the shared reader's morphology lexicon is decided by the
  CATEGORICAL band, which is tried first and answers in its own
  `valid`/`invalid` vocabulary; v6-EX's territory is everything else
  (unknown vocabulary, singular facts, verb predicates, >3 terms). The
  `v2_exist/` corpus is authored on that fall-through path deliberately, so
  the split measures the band it names. Related: `to_syllogism` now REFUSES
  rather than dropping a premise it cannot express (ADR-0261 §5.1) — before
  that fix it answered a strictly weaker argument than the user wrote, which
  is how a wrong served verdict got past a licensed band.
- **Still-open declines** (honest, typed): verb-phrase contraction
  negation (`ds-en-0023/0024`), ambiguous `and`/`or` scope (`ds-en-0025`),
  nested conditionals (`ds-en-0026`), bare plurals / definite descriptions /
  relative clauses / tense (`ds-mem-0021…0023/0025/0026`), a universal
  clause nested inside a connective, compound conclusions
  (`ds-cm-0020…0026`), the verb band's own scope-outs — `did not` tense,
  multi-token subjects, prepositional/ditransitive shapes, connective×verb
  composition (`ds-vb-0021…0028`) — and the existential band's:
  partitives, singular agreement under a plural subject,
  connective×existential composition, proportional quantifiers, universal
  conclusions (`ds-ex-0022…0032`).

## Reproduce

```bash
uv run python -m evals.deduction_serve.runner                              # human-facing
uv run python -m evals.deduction_serve.runner --report evals/deduction_serve/report.json  # pinned artifact
```

Pinned in `scripts/verify_lane_shas.py` as lane id `deduction_serve_v1`.
`core test --suite deductive` runs `tests/test_deduction_serve_lane.py`,
which asserts `wrong == 0` and `all_cases_correct is True` against the
committed corpus.
