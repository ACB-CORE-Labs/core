# Rust backend parity — measured, and why the instructed method cannot fail

**Date:** 2026-07-26 · **Arc:** curriculum-license-loop-2026-07 · **Unit:** plan §6A
**Instruction:** "`PYO3_PYTHON=/opt/homebrew/bin/python3.12`, `cargo test` in
`core-rs/`, then rerun the hash-pinned lanes under `CORE_BACKEND=rust`. **Report the
measurement; do not act on it.**" (`DIVISION-OF-WORK.md` §4)

Both halves ran. The first is a real signal. **The second is vacuous, and this note
exists mostly to say so** — run as instructed it produces "11/11 lanes match, parity
holds", which is true, and which would be read as evidence about the Rust kernels
when it is not evidence about them at all.

---

## 1. `cargo test` — 43 passed, 0 failed

```
PYO3_PYTHON=/opt/homebrew/bin/python3.12 cargo test --offline
```

| suite | tests |
|---|---:|
| unit (`src/`) | 7 |
| `test_arena.rs` | 10 |
| `test_cga.rs` | 5 |
| `test_cl41.rs` | 7 |
| `test_crdt_hash_parity.rs` | 6 |
| `test_vault.rs` | 4 |
| `test_versor.rs` | 4 |
| **total** | **43 passed / 0 failed** |

The plan's read was correct: cargo 1.97.1 and the registry cache are present
locally, and the cloud session was blocked only by sandbox network policy.
`--offline` needed no downloads. This half is genuine evidence — in particular
`test_crdt_hash_parity.rs` includes `parity_permutation_invariant_matches_python`
and `parity_signed_zero_distinct`.

## 2. Lane parity — 11/11 both ways, and the number means nothing

```
uv run python scripts/verify_lane_shas.py                    # lanes: 11/11 match
CORE_BACKEND=rust uv run python scripts/verify_lane_shas.py   # lanes: 11/11 match
```

Identical, byte for byte, every lane. Then the check that matters:

> **Sabotaged every `core_rs` callable to raise, re-ran under `CORE_BACKEND=rust`:
> `lanes: 11/11 match pinned SHAs`, exit 0.**

A measurement that passes with the entire Rust backend replaced by exceptions is
not measuring the Rust backend. Three independent reasons, each sufficient:

**(a) The hot path bypasses the dispatch.** `algebra/backend.py` is the only place
that consults `CORE_BACKEND`, and `algebra.cga.cga_inner is not
algebra.backend.cga_inner`. Counting call sites for the hot functions:

| import route | call sites |
|---|---:|
| `from algebra.cga import …` / `from algebra.cl41 import …` (**bypasses** dispatch) | **69** |
| `from algebra.backend import …` (uses dispatch) | 24 |

So the ~34k `cga_inner` → `geometric_product` calls per turn that plan §6C
identifies as ~73% of turn time do not reach the dispatch at all.

**(b) The dtype gates reject the runtime workload.** `versor_condition`,
`cga_inner` and the f32 arm of `geometric_product` require
`_is_f32_workload(...)`. `core/cognition/pipeline.py:24` imports
`versor_condition` from `algebra.backend` — the dispatch IS consulted there — and
still falls through, because the wave-field workload is f64.

**(c) Every dispatch arm swallows every exception.** Each Rust branch is wrapped in
`except (AttributeError, TypeError, ValueError, Exception): pass`. A Rust kernel
that raises, returns garbage of the wrong type, or is missing entirely produces a
**silent** fallback to Python. That is what makes (a) and (b) unfalsifiable by lane
hashes: Python answers, the hash matches, the lane is green.

Instrumented call counts under `CORE_BACKEND=rust`, wrapping every `core_rs`
callable:

| workload | Rust kernel calls |
|---|---|
| `deductive_logic_v1` lane (whole lane) | **none** — the lane is pure ROBDD, no CGA |
| one full `CognitiveTurnPipeline.run` turn | **1** (`versor_apply_with_closure_f64`) |

One call per turn. `CORE_BACKEND=rust` is, today, a one-call switch.

## 3. What this means for the plan

- **§6A is answered narrowly.** `cargo test` is green, and the one dispatched f64
  path a turn actually takes (`versor_apply_with_closure_f64`) is bit-identical —
  lane hashes are unchanged with it live. Nothing broader was established.
- **§6B ("if parity holds: consider Rust default") rests on a measurement that
  cannot fail.** Flipping the default today would change one call per turn and gain
  approximately nothing, because the hot path does not route through the dispatch.
  The premise needs to be re-earned before the decision is worth making.
- **§6C is the actual blocker, and it is upstream of the backend.** Accelerating
  `cga_inner`/`geometric_product` requires routing their 69 call sites through
  `algebra.backend` and giving the f64 workload a bit-identical f64 kernel. That is
  a real change to a determinism-critical path, and it is exactly the kind of change
  the lane pins exist to gate — but only once the pins can actually see it.

**Not acted on** — the instruction is report-only, and §6.4 is explicit that a
parity or determinism finding is escalated rather than fixed. Three things a future
unit should consider, in dependency order:

1. **Make the dispatch fail loudly.** Replace the blanket `except … Exception: pass`
   with a narrow catch plus a one-time warning, or a strict mode that raises. While
   fallback is silent, no parity measurement over lanes can be trusted, and this
   note's conclusion would have to be re-derived by hand every time.
2. **A parity test that fails when the Rust path is not taken.** Assert a nonzero
   Rust call count under `CORE_BACKEND=rust`, so "parity holds" cannot be satisfied
   by never invoking Rust. Without it, §6A's exit criterion is unfalsifiable.
3. Only then: route the hot path through the dispatch (§6C).

## 4. One defect found and fixed here

`core rust build` — the documented activation path, named by
`print_rust_status()`'s own `activation: run \`core rust build\`` hint — raised
`TypeError: _run() got an unexpected keyword argument 'env'` on **every**
invocation. `core/cli.py::_run` is injected into `cli_rust.cmd_rust_build`, which
passes `env=rust_build_env()` to carry
`PYO3_USE_ABI3_FORWARD_COMPATIBILITY` (PyO3 0.21 supports Python through 3.12).
`_run` had no `env` parameter, while the `CommandRunner` Protocol both call sites
are typed against does.

Fixed (one keyword) and pinned by `tests/test_cli_runner_contract.py`, which
derives the expected keywords **from the Protocol** rather than from a hand-written
list, so the two cannot drift apart again. The build had to be driven with
`python -m maturin develop --release` directly to take the measurements above.

## 5. Reproduction

```bash
# 1. Rust unit + parity suites
cd core-rs && PYO3_PYTHON=/opt/homebrew/bin/python3.12 cargo test --offline

# 2. install the extension (needs the §4 fix, or call maturin directly)
PYO3_PYTHON=/opt/homebrew/bin/python3.12 uv run core rust build

# 3. activation is opt-in: importable is NOT active
uv run python -c "from core.cli_rust import print_rust_status; print_rust_status()"
#   -> rust backend  : inactive
CORE_BACKEND=rust uv run python -c "from core.cli_rust import print_rust_status; print_rust_status()"
#   -> rust backend  : active

# 4. lane hashes, both backends
uv run python scripts/verify_lane_shas.py
CORE_BACKEND=rust uv run python scripts/verify_lane_shas.py

# 5. the check that shows 4 proves nothing: sabotage every kernel, rerun 4.
#    Still 11/11.
```

Installing `core_rs` does **not** activate it — `_ALLOW_RUST` requires
`CORE_BACKEND` in `{rust, core_rs, rs}`, so a stray local build cannot silently
change default behaviour. Verified: with the extension installed and no env var,
`rust backend : inactive`.
