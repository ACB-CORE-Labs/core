# Deduction-serve lane contract (v1)

## What this lane scores

The **production serving decider** — the exact pipeline
`chat/deduction_surface.py::deduction_grounded_surface` runs on a
`core chat` turn: `looks_like_deductive_argument` (commit gate) →
`comprehend` (reader) → `to_deductive_logic` (projector) →
`evaluate_entailment_with_trace` (the ROBDD engine, ADR-0201/ADR-0218).
`evals/deduction_serve/runner.py::decide` calls these functions directly
(typed outcome, not rendered prose) — the same production decision the
composer makes, without re-deriving the presentation step
(`generate.proof_chain.render.render_entailment`), so this lane's pinned
bytes stay stable against wording-only changes.

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

## Known Band v1 boundaries this corpus documents

Discovered while authoring v1 (each is a genuine reader-grammar limit,
not a lane bug):

- **Nested negation inside `if/then`** — `generate/meaning_graph/reader.py`'s
  `_parse_propositional` accepts `not P` only as a top-level clause;
  `"if not q then not p"` fails `_chunk`'s reserved-word guard (`not` is in
  `_RESERVED`) when it appears *inside* an if/then slot. `ds-v1-0006`
  documents this (`out_of_band_nested_negation`).
- **Multi-word English propositions** — `ds-v1-0025`
  (`out_of_band_multiword_conditional`), matching the Phase 0 baseline's
  band-boundary finding.
- **Categorical/syllogism shapes** — `ds-v1-0023/0024/0026`
  (`out_of_band_categorical`); Band v1b (a production categorical decider)
  is deferred.

## Reproduce

```bash
uv run python -m evals.deduction_serve.runner                              # human-facing
uv run python -m evals.deduction_serve.runner --report evals/deduction_serve/report.json  # pinned artifact
```

Pinned in `scripts/verify_lane_shas.py` as lane id `deduction_serve_v1`.
`core test --suite deductive` runs `tests/test_deduction_serve_lane.py`,
which asserts `wrong == 0` and `all_cases_correct is True` against the
committed corpus.
