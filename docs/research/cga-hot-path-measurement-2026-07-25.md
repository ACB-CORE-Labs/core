# Where the per-turn CGA cost actually is — measured, 2026-07-25

**Result:** the substrate-performance premise in circulation (mine and an
external hardware blueprint's) was wrong. `versor_condition` is **0.22%** of a
turn. The real cost is `cga_inner` → `geometric_product` at **33,986 calls per
turn, ~73% of turn time**, driven by nearest-neighbour and salience search.
The obvious algebraic shortcut is **not** bit-safe and must not ship. A
different, already-ratified pattern in this repo **is** bit-exact and is the
correct target.

## 1. What was claimed

Two claims were in play going into this measurement, and both were reasoned
from microbenchmarks rather than from a turn:

1. An external Apple-Silicon blueprint proposed custom `.metal` Cl(4,1)
   kernels, SoA layouts, MLX kernel-fusion of the versor invariant, and
   bfloat16 routing — arguing the CPU is the bottleneck.
2. My own assessment claimed `versor_condition` is the hot spot: three calls
   per turn × the benchmark report's `p50 = 0.536 ms` ≈ 1.6 ms/turn, "~10× the
   entire proof latency."

Claim 2 is **wrong**, and it is worth naming the error precisely because it is
easy to repeat: it multiplies an *isolated microbenchmark* by a call count and
compares the product against `FrameVerdict` TTFV (0.151 ms) — which is the
latency of a single proof verdict, not of a turn. Those are not comparable
quantities. The correct denominator is the turn.

## 2. Direct measurement

`versor_condition` wrapped in a counter, three real `ChatRuntime.chat()` turns:

```
turns                  : 3
versor_condition calls : 9   (3.0 per turn)
time inside it         : 1.34 ms total (0.448 ms/turn)
total chat() wall      : 601.5 ms (200.5 ms/turn)
share of turn          : 0.22%
```

The call count (3/turn) was right. The cost conclusion was not. **Switching the
Rust backend on would recover 0.22% of a turn through this path.** That is not
a reason to do it, and it removes the only quantified justification the
substrate track had.

## 3. Where the time actually goes

`cProfile`, three turns, post-warmup:

| calls | tottime | cumtime | function |
|---:|---:|---:|---|
| 3 | 0.001 | 2.242 | `chat/runtime.py::chat` |
| **33,986** | **1.631** | 1.656 | **`algebra/cl41.py::geometric_product`** |
| 16,418 | 0.029 | 1.608 | `algebra/cga.py::cga_inner` |
| 24 | 0.009 | 1.156 | `generate/proposition.py::_nearest_by_cga` |
| 3 | 0.023 | 0.626 | `generate/salience.py::compute` |
| 4,577 | 0.003 | 0.458 | `algebra/backend.py::cga_inner` |

So the CGA algebra **is** the dominant per-turn cost — roughly 73% — but
through `cga_inner` in nearest-neighbour and salience search, not through the
versor invariant. Both documents aimed at the wrong function.

The multiplier is structural. `algebra/cga.py::cga_inner` is:

```python
XY = geometric_product(X, Y)
YX = geometric_product(Y, X)
return 0.5 * scalar_part(XY + YX)
```

Two full 32×32 products — ~2,048 multiply-adds — to read **one scalar**. At
16,418 calls per turn that is the entire profile.

## 4. The tempting shortcut, and why it must not ship

`algebra/backend.py` already documents the closed form: for Cl(p,q) basis
blades `e_i * e_j` is scalar only when `i == j`, so

```
cga_inner(X, Y) == sum_i metric[i] * X[i] * Y[i]
```

32 multiply-adds instead of 2,048. Tested against the scalar path, 4,000 random
pairs per dtype, using `np.sum`:

```
float32: bit-exact  954/4000   worst-rel 1.037e-04
float64: bit-exact  929/4000   worst-rel 2.283e-13
```

**Not bit-exact.** A 1e-4 relative divergence in f32 would move surfaces that
`trace_hash` folds, break the committed lane SHA pins, and violate the
Rust/Python parity contract (`core-rs/tests/test_crdt_hash_parity.rs`). This is
the same class of error as proposing bfloat16 against a `1e-6` versor gate:
mathematically identical, numerically not.

## 5. The pattern that *is* exact

The divergence above is not the identity's fault — it is the *reduction order*.
`np.sum` reduces pairwise. `algebra/backend.py::vault_recall` folds serially in
component order:

```python
scores = np.zeros(M.shape[0], dtype=np.float32)
for i in range(M.shape[1]):
    scores += (_CGA_INNER_METRIC[i] * M[:, i]) * q[i]
```

Its docstring claims this is "bit-identical to the scalar `cga_inner` path
because the per-versor sum is folded in the same serial component order
(ADR-0019 Stage 1)". Tested directly, 3,000 random f32 pairs:

```
serial-fold vs scalar cga_inner (f32): bit-exact 3000/3000  worst-rel 0.000e+00
```

**The claim holds exactly.** So this repo already contains a proven, ratified,
bit-exact vectorization of the very operation that dominates the profile —
scoring one query against N versors without a Python-level product loop.

## 6. The actual next step

Apply the `vault_recall` serial-fold pattern to the nearest-neighbour search
paths that dominate the profile — `generate/proposition.py::_nearest_by_cga`
and `generate/salience.py::compute` — which today call scalar `cga_inner` in a
Python loop over candidates.

Why this is the right target:

- **No GPU, no Metal, no MLX, no Rust, no new numerics.** Nothing in the
  determinism doctrine has to move.
- **The exactness is proven, not assumed** (§5), and the acceptance test is
  falsifiable and cheap: N turns before/after must produce byte-identical
  surfaces and identical `trace_hash` values.
- It attacks 73% of turn time rather than 0.22%.

**Not done in this session, deliberately.** These functions feed articulation,
and the local-first merge bar is the full suite; this session could run curated
suites only (see §7). The measurement and the exactness proof are the expensive
parts and they are done — the change itself should land where it can be gated
properly.

## 7. What could not be verified here, and why

`cargo test` in `core-rs/` **could not run**: the sandbox network policy denies
`static.crates.io` (the proxy's `noProxy` list covers `index.crates.io`, so the
sparse index resolves but crate tarballs 403 at the gateway). No crates are
cached. So:

- **"Does `core_rs` still hold bit-exact parity?"** — the question the plan put
  first, and the one the hardware blueprint skipped — remains **open**. It is
  still the right question; §2 just removes the urgency the performance
  argument was supplying.
- **The Rust typestate lane (`UnverifiedClaim` → `VersorClaim`)** was not
  written. It is still the strongest of the blueprint's five proposals — the
  only one with no determinism cost, and it needs no GPU — but shipping Rust
  that cannot be compiled or tested in the session that wrote it is not
  something to do. It carries forward unchanged.

Python measurements above ran on a scratch venv at 3.12.11; the repo pins
`==3.12.13`, which `uv` cannot fetch for linux-x86_64. The pin was left
untouched.

## 8. Standing verdicts on the blueprint's five items

Unchanged by this measurement except where noted.

| Proposal | Verdict |
|---|---|
| Rust typestate | **Adopt** — carried forward, blocked only on a build. |
| SoA layouts | **Resequence** — and now further down: the copy boundary is not what the profile shows. |
| Custom sparse `.metal` Cl(4,1) kernel | **Premature**, and now *doubly* so: there is a bit-exact CPU win (§5–6) available before any GPU question is live. |
| MLX lazy kernel fusion of the versor invariant | **Rejected on target selection**, additionally to the doctrine objection: the function it fuses is 0.22% of a turn. |
| bfloat16 asymmetric precision | **Reject** — §4 is the empirical form of the same argument at a *much* coarser epsilon. |

Relates to [[project-generalization-arc]].
