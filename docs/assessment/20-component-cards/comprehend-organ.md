# comprehend-organ — `core/comprehension_attempt/`

**Kind:** zone→component descent · **Parent:** M3 · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal` (**demoted** from the map's `live-serving`) · **Fitness:** `fit`, misleadingly named · **Topology role:** runtime boundary (off the chat serving path)

> The deterministic multi-organ setup router (N3): when several comprehension organs each attempt a problem setup, admit a setup only when exactly one organ produced an admissible one — or the admitting organs agree by signature. Never pick among disagreeing readings. Its philosophical role is refusal-preserving arbitration: routing must not become a place where a guess can hide.

## What it is / What it does

Six modules, 754 lines: `router.py` (77 — the N3 router), `classify.py` (159 — `classify_cmb/r1/r2/r3`), `failure_family.py` (250), `proposal.py` (148 — comprehension-failure proposals), `model.py` (63 — `ComprehensionAttempt`), `__init__.py`. Routing rule, verbatim from the module doc: exactly one `setup_correct` → routed; zero → `all_refused` (classified downstream); ≥2 agreeing signatures → routed; ≥2 differing → `ambiguous` (refuse — never pick). Cross-organ signatures are produced by different functions and never coincide, so two admitting organs resolve to `ambiguous` in practice. The router never solves and never emits `setup_wrong` — that is an eval-only outcome.

## The liveness demotion, with evidence

`comprehension_attempt` is imported by **neither** `chat/runtime.py` nor `core/cognition/pipeline.py`. Its non-test callers are `core/epistemic_disclosure/limitation.py` (→ `chat/ask_runtime.py`, behind `ask_serving_enabled=False`), `core/proposal_review/queue.py`, `core/epistemic_questions/delivery.py`, and `evals/constraint_oracle/verified_producer.py`. Nothing on the default serving path reaches it. The map's `live-serving` label is therefore wrong at this SHA: **`live-internal`** (eval lanes + flag-gated ask path + proposal machinery).

## Contract & evidence

- Refuse-on-ambiguity is the load-bearing invariant — pins: router tests (`tests/test_cmb_router_contemplation.py`, `tests/test_failure_family.py`, `tests/test_failure_proposal.py`) — present in the tree; suite membership not individually confirmed.
- wrong=0 posture: against gold the routed setup must match; the router structurally cannot emit a wrong setup, only a refusal or a routed one.

## Judgment

**Fitness: `fit` — but the zone name is a trap.** This is a *math setup* router over the GSM8K-era R1/R2/CMB organs, not "the comprehension organ" of the chat path. Chat comprehension lives in `generate/meaning_graph/reader.py` (see the realize-phase card). A future reader who greps "comprehend-organ" expecting the thing that reads user English will land in the wrong subsystem. Recommend the zone be renamed (e.g. `setup-router`) or its card carry this disambiguation permanently.

**Honest wrinkles:** the design is deliberately boring and correct — no dynamic scoring, no priority heuristics. Its consumers are all flag-gated or eval-side, so this machinery currently arbitrates for paths that mostly do not serve.

**Open questions:** should `epistemic_questions`/`disclosure` consumers ever reach serving, the router becomes serving-path arbitration — does it then need a suite-pinned invariant? (→ Phase 4)
