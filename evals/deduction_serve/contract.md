# Deduction-serve lane contract

## What this lane scores

The **production serving decider** — the exact pipeline
`chat/deduction_surface.py::deduction_grounded_surface` runs on a
`core chat` turn: `looks_like_deductive_argument` (commit gate) →
`comprehend` (reader) → the band cascade — `to_deductive_logic` (Band v1)
→ `to_syllogism` + the categorical decider (Band v1b, ADR-0256) →
`read_english_argument` (Band v2-EN, ADR-0257) → `read_member_argument`
(Band v3-MEM, ADR-0258) — with `evaluate_entailment_with_trace` (the
ROBDD engine, ADR-0201/ADR-0218) deciding every band.
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
`…_formerly_out_of_band`):

- **Nested negation inside `if/then`** — a shared-reader grammar limit
  (`not` is reserved inside if/then slots); `ds-v1-0006` declined until
  Band v2-EN decided it (promoted, ADR-0257).
- **Multi-word English propositions** — `ds-v1-0025` declined until Band
  v2-EN (promoted, ADR-0257).
- **Categorical/syllogism shapes** — `ds-v1-0023/0024/0026`, decided by
  Band v1b since ADR-0256.
- **`is a` membership** — `ds-en-0022` declined until Band v3-MEM decided
  it (promoted, ADR-0258).
- **Still-open declines** (honest, typed): verb-phrase negation
  (`ds-en-0023/0024`), ambiguous `and`/`or` scope (`ds-en-0025`), nested
  conditionals (`ds-en-0026`), existential quantifiers / bare plurals /
  definite descriptions / relative clauses / tense (`ds-mem-0020…0026`).

## Reproduce

```bash
uv run python -m evals.deduction_serve.runner                              # human-facing
uv run python -m evals.deduction_serve.runner --report evals/deduction_serve/report.json  # pinned artifact
```

Pinned in `scripts/verify_lane_shas.py` as lane id `deduction_serve_v1`.
`core test --suite deductive` runs `tests/test_deduction_serve_lane.py`,
which asserts `wrong == 0` and `all_cases_correct is True` against the
committed corpus.
