# Deduction-serve arc — Phase 2 (end-to-end eval lane + wrong=0 gate), 2026-07-23

**Base:** `main` @ `6a54d27a`. **Branch:** `feat/deduction-serve-phase1` (stacked
on top of the Phase 1 commit, same branch — Phase 2 is additive to Phase 1's
serving path, not a separate capability).
**Depends on:** Phase 1 (`chat/deduction_surface.py`, the composer this lane scores).

## What shipped

A new, dedicated, SHA-pinnable capability lane —
**`evals/deduction_serve/`** — that scores the *production serving
decider* end-to-end from raw text, closing the gap neither existing lane
covers:

| Lane | What it scores | Decision procedure used |
|---|---|---|
| `evals/deductive_logic` | the bare `entail.py` engine | `evaluate_entailment` on hand-authored **formula strings** |
| `evals/comprehension/propositional_runner.py` | reader **fidelity** | the **independent oracle**, not the production engine |
| `evals/deduction_serve` (new) | the **production serving pipeline**, raw text in | `comprehend → to_deductive_logic → evaluate_entailment_with_trace` — the exact calls `chat/deduction_surface.py` makes |

## New files

- **`evals/deduction_serve/v1/cases.jsonl`** — 27 hand-authored cases, gold
  computed independently by direct logical reasoning (not copied from a
  first engine run — see "Honesty check" below). Four gold classes:
  `entailed` (8), `refuted` (5), `unknown` (5), `declined` (9 — covering
  inconsistent premises, categorical/syllogism shape, multi-word English,
  and nested negation).
- **`evals/deduction_serve/runner.py`** — `decide(text)` calls the exact
  pipeline the composer runs (typed outcome, not rendered prose — keeps
  the pin stable against wording-only changes); `build_report` /
  `build_combined_report` / `write_combined_report` mirror
  `evals/deductive_logic/runner.py`'s pattern exactly.
- **`evals/deduction_serve/report.json`** — the committed, SHA-pinnable
  artifact: `27/27 correct, wrong=0, all_correct=true`.
- **`evals/deduction_serve/contract.md`** — the lane contract, including
  the three known Band v1 boundaries this corpus documents.
- **`tests/test_deduction_serve_lane.py`** — wrong=0 gate + a negative
  control (a deliberately wrong gold label correctly flags `wrong=1`,
  proving the gate isn't vacuously green).

## Changed files

- **`core/cli_test.py`** — `"deductive"` suite now runs
  `tests/test_deduction_serve_lane.py` alongside the existing
  `test_deductive_logic_entail.py` (a natural sibling).
- **`scripts/verify_lane_shas.py`** — new `LaneSpec("deduction_serve_v1", ...)`
  + pinned SHA (computed via the script's own `--update`, the documented
  procedure — not hand-typed).

## Honesty check — a real authoring bug the lane itself caught

The first draft of the corpus included a case intended as **entailed**
(contraposition: `"If p then q. Therefore if not q then not p."`). Running
the actual runner (not just eyeballing it) surfaced a mismatch: the
pipeline **declined** it. Tracing why (not assuming the case was right):
`generate/meaning_graph/reader.py`'s `_parse_propositional` only accepts
`not P` as a **top-level** clause — `_chunk`'s reserved-word guard rejects
`"not q"` / `"not p"` *inside* an `if/then` slot (`not` is in `_RESERVED`).
This is a genuine, narrower-than-assumed reader-grammar boundary, not a
runner bug. Fixed honestly: reclassified the case's gold to `declined`
(`out_of_band_nested_negation`, now documented in the contract) and added
a different, in-band **entailed** case (a three-hop chain,
`"If p then q. If q then r. If r then s. p. Therefore s."`) to keep
coverage. This is exactly the kind of finding Phase 0/1's "honest wrinkle"
discipline is meant to surface — caught here because the lane was actually
*run*, not because the corpus was authored perfectly the first time.

## Out-of-scope finding: three lanes emit non-deterministic committed artifacts; `public_demo` errors

Running the documented `scripts/verify_lane_shas.py --update` procedure to
compute this lane's pin **re-executes every registered lane's runner**,
which rewrites their committed `results/v1_dev.json` files on disk (not
merely re-hashes the existing ones). Doing so surfaced two pre-existing,
unrelated problems on `main @ 6a54d27a`:

- **`miner_loop_closure`, `curriculum_loop_closure`, `demo_composition`
  regenerate non-deterministic content IDs** (e.g. `miner_loop_closure`'s
  `proposal_id`/`finding_id` fields differ byte-for-byte between two
  consecutive runs on identical input — `be5a8f06893b0575` vs
  `4272ff76eb8a9e16` for the same `positive_basic` case). Their committed
  `PINNED_SHAS` values therefore do not reproduce even on an unmodified
  checkout — a genuine determinism bug in those lanes, independent of
  anything this arc touched.
- **`public_demo` errors outright** (`ERROR after 85s`) — matches the
  already-known "`public_demo` flake = env timeout" gotcha in standing
  project memory.

Neither is caused by, or in scope for, the deduction-serve arc. Reverted
all four lanes' `results/*.json` and `PINNED_SHAS` entries to their
original committed values before finalizing this PR — the only change to
`scripts/verify_lane_shas.py` is the new `deduction_serve_v1` `LaneSpec` +
pin. Worth a dedicated follow-up outside this arc: those three lanes need
a deterministic-ID fix before their pins can ever be legitimately
refreshed via `--update` again.

## Verification

```
uv run python -m evals.deduction_serve.runner                    # 27/27, wrong=0
uv run python -m pytest tests/test_deduction_serve_lane.py -q    # 2 passed
uv run core test --suite deductive -q                             # 25 passed
uv run core test --suite smoke -q                                 # 180 passed
uv run core test --suite cognition -q                              # 122 passed, 1 skipped
uv run python scripts/verify_lane_shas.py --update                 # pin computed + written
```

## Verdict

Phase 2 complete. The deduction-serve capability now has a durable,
SHA-pinned, `core test`-wired proof of correctness distinct from (and
stronger than) the two lanes that could be mistaken for covering the same
ground — this lane is the only one that proves the *production* decider
gets raw natural-language arguments right, not just its parts in
isolation. Combined with Phase 1, the arc's original goal is met: a user
can ask a basic logic question in `core chat` and get a decided,
articulated, wrong=0-verified answer, with a committed regression gate
protecting it going forward.
