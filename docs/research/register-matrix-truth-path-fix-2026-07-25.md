# The register matrix was red on main for 99 registers — and the invariant was fine

**Result:** `801 passed, 0 failed` across all 99 ratified register packs, from
99 failures on clean `main`. No behaviour changed; a field was made observable.

## 1. What was red, and what was not

`tests/test_cognition_eval_register_matrix.py` had **99 failures on pristine
`main`** (confirmed in a worktree at `origin/main`), every one of them
`test_register_matrix_canonical_surface_byte_identical`.

`test_register_matrix_trace_hash_invariant` — the load-bearing ADR-0072
truth-path-isolation claim — **passed throughout**. That is the decisive fact:
`trace_hash` folds `hash_surface`, so a genuine leak into the truth path would
have moved it. It never did. The seals, `wrong=0`, and the register-invariance
guarantee were never compromised.

## 2. Why the test was wrong

Its docstring asserted that `CognitiveTurnResult.surface` is *"the pre-decoration
/ canonical composer output (the truth-path field `compute_trace_hash`
consumes)"*.

That stopped being true on 2026-07-23. Phase 0 flipped `resolve_surface` to
response-first precedence and introduced `SurfaceResolution.hash_surface` as the
register-invariant capture. After it:

- `core/cognition/pipeline.py` folds **`hash_surface`** into `compute_trace_hash`
- `core/cognition/result.py:59` documents `surface` as *"final voiced surface
  (what the user sees)"*

So the test demanded that registers **not** differ on the served surface — the
opposite of what the register axis exists for, and a direct contradiction of
`tests/test_register_substantive_consumption.py`, which pins that they **do**
differ and is green in `smoke`. Two tests on `main` asserting opposite things
about the same bytes.

Measured at the seam:

```
register=None         surface = 'Truth is what is true. pack-grounded (…).'
                 hash_surface = 'Truth is what is true. pack-grounded (…).'
register=socratic_v1  surface = 'Consider the question: Truth is what is true…'
                 hash_surface = 'Truth is what is true. pack-grounded (…).'
```

`surface` varies. `hash_surface` does not. Exactly the contract.

## 3. Root cause: the invariant was unobservable

`hash_surface` was **pipeline-local**. Nothing downstream could see the field
that actually carries the guarantee, so the test reached for the nearest visible
surface and drifted the moment their contracts diverged. The fix is to expose it:

- `CognitiveTurnResult.hash_surface` — new field, from the value the pipeline
  already computed
- `evals/metrics.py::CaseResult.hash_surface` — carried through the eval harness
- the test asserts byte-identity on `hash_surface`

No stored baseline to regenerate; the fixture computes it live.

## 4. Why it stayed red

This file is in neither `smoke` nor `deductive`. Nothing local ran it, and CI
does not exist — GitHub Actions are billing-locked dead signals and the Forgejo
host cannot run workflows. It was only findable by running the whole tree, which
until `scripts/ci/local-ci.sh` nothing made easy.

Fourth silent-red of this arc, after the stale exact-tuple pin (S5), the lane
roster, and the proposal-sink leak.

## 5. A wrong turn worth recording

The first attempt added the field to `evals/cognition/runner.py::CaseResult`.
The test imports `run_eval` from `evals/run_cognition_eval.py`, which builds
`evals/metrics.py::CaseResult` — a different class of the same name. **Thirteen
files in this repo define a `CaseResult`.** Matching on the class name instead
of following the import produced `AttributeError` inside `_diff_rows` and took
the count from 99 to 100. Follow the import.

## 6. Verification

```
tests/test_cognition_eval_register_matrix.py   801 passed, 0 failed  (17m50s)
  — including test_register_matrix_trace_hash_invariant across all 99 registers
capability index + eval harness                 23 passed
```

`evals/metrics.py::CaseResult` gained a **defaulted** field; its only other
consumers (`calibration/tune.py`, `calibration/replay.py`) read it and never
construct it, so no constructor breaks.

Run on Python 3.12.11. Re-run on 3.12.13 for canonical evidence.

Relates to [[project-generalization-arc]].
