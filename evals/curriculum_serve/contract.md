# Curriculum-serve lane contract

## What this lane scores

The **production curriculum-grounded answering path** — the exact pipeline
`chat/curriculum_surface.py::decide_curriculum_question` runs on a `core chat`
turn when `curriculum_serving_enabled` is on:

```
Does <term> <relation> <term>?      (closed exam-question grammar)
  → subject routing        (the domain whose ratified vocabulary holds BOTH terms)
  → relation family        (the connective, normalized by ADR-0260 agreement)
  → premise compilation    (that family's RATIFIED chains, and nothing else)
  → the argument bands     (ADR-0260 verb reading → ADR-0261 existential)
  → the ROBDD engine       (ADR-0201/0218)
```

There is no subject-specific decision code anywhere in the path. Physics
differs from philosophy only in which curriculum rows load — which is the
property that makes "add a subject" a data operation.

## Gold vocabulary

Three classes are reachable: `entailed`, `unknown`, `declined`.

`refuted` is **unreachable from a purely positive curriculum** and that is not
an omission. The curriculum is read OPEN-world: a relation it does not state
is UNKNOWN, never "no". Refuting would require the curriculum to teach a
negative ("no X causes Y"), which no ratified corpus does yet. See ADR-0262 §5.

## The three lane guards (all run before any case is scored)

Failing a guard is a **lane** failure, not a case miss — the lane is unsound,
not merely under-covered.

1. **Provenance** (plan §4.3) — every chain id a case pins must resolve in the
   subject's ratified curriculum. A case whose curriculum moved under it
   breaks loudly rather than quietly answering from what remains.
2. **Corpus soundness** (§4.4) — the INDEPENDENT oracle
   (`evals/curriculum_serve/oracle.py`, sharing no code with the serving path:
   own loader, own ratification predicate, own family table, own agreement
   normalization, own verdict rule) must re-derive every committed gold.
3. **Anti-recall coverage** (§4.7) — the split must carry ≥3 probes whose
   answer is true in the world and absent from the curriculum, and no probe
   may carry a committed gold. Without them the lane cannot show the system
   decodes rather than recalls, and it must not ship.

## Splits

- `physics/` — 32 hand-authored cases over `physics_chains_v1`: 13 taught
  edges (both connectives of each family, incl. the row whose declared
  `operator_family` disagrees with its connective), 5 untaught compositions at
  depth 2–3, 4 reverse-direction and cross-relation near-misses, 5 anti-recall
  probes (3 with untaught vocabulary — *gravity*, *current*, *pressure* — and
  2 with taught vocabulary but untaught relations), and 5 typed refusals.

## wrong=0 discipline

Identical to the deduction-serve lane: `wrong` (a committed verdict that
disagrees with gold) MUST stay 0; a decline where gold expected a verdict is a
coverage miss, tracked in `counts.declined`, never conflated with a
confabulation. The runner requires `correct == n`.

## What the lane deliberately does NOT do

- **It does not compose chains.** `force causes acceleration` and
  `acceleration causes motion` are both taught; `force causes motion` is
  UNKNOWN. Causal transitivity is a substantive claim about the world, and no
  ratified corpus teaches it. The oracle reports the shortest path length
  alongside its verdict precisely so the lane can assert that a reachable pair
  is still answered UNKNOWN — composition is provably not happening.
- **It does not read the corpus's `operator_family` field.** The family comes
  from the CONNECTIVE, because a question carries a relation word and nothing
  else; deriving the family from a field the question cannot carry would let
  premise compilation and question routing disagree, and a taught edge could
  go missing from the premises compiled to decide it.

## Reproduce

```bash
uv run python -m evals.curriculum_serve.runner                                    # human-facing
uv run python -m evals.curriculum_serve.runner --report evals/curriculum_serve/report.json
```

Pinned in `scripts/verify_lane_shas.py` as lane id `curriculum_serve_v1`.
`core test --suite deductive` runs `tests/test_curriculum_serve.py`.
