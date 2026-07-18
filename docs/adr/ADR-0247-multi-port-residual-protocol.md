# ADR-0247: Multi-Port Residual Protocol — the Ring-2 Shared Control Grammar

**Status**: **Accepted**
**Date**: 2026-07-18
**Authors**: Joshua Shay + multi-model R&D (implemented Fable 5)
**Depends on**: ADR-0244/0245 (Accepted), ADR-0246 (Proposed — first port consumer)
**Preflight authority**: ADR-0246 preflight brief §9 (Ring 2), §7 non-goal #2

---

## 1. Decision

Implement Ring 2 exactly as the preflight bounds it — a **shared control
grammar only** — as the pure package `core/ports/`:

```text
witness → typed residual decomposition → permitted operator selection
  → bounded operation or abstention → re-certification
  → articulation/action decision → append-only replay record
```

(`core/ports/residual_protocol.py`; note `core/protocol/` was already taken by
the CORE Trace Protocol v0 wire format — checked before naming, no collision.)

Key properties, each pinned by tests (`tests/test_ring2_residual_protocol.py`):

1. **Port-agnostic grammar, port-native geometry.** The grammar never
   interprets a port's measurements; there is **no port registry and no
   unified scheduler** (preflight §7 non-goal #2 honored — callers invoke the
   protocol per port, per subject). A synthetic third port runs with zero
   grammar changes.
2. **Abstain-or-proceed v1.** Only zero-bound operators exist
   (`proceed_unmodified` / `abstain`). A **nonzero-bound operator fails
   closed** with a typed error — bounded correctors require their own future
   ADR (no-silent-correction doctrine, inherited from ADR-0244/0246).
3. **Fail-closed on unaccounted residual** — energy the port's typed channels
   cannot account for forces abstention (ADR-0246 §3.6 doctrine generalized);
   no correction policy ever attaches to it.
4. **Re-certification** — the witness is re-measured after the zero-bound
   operation; drift means the port mutated state mid-pass and **raises**
   rather than recording a corrupted replay.
5. **Append-only, content-addressed replay** — full-SHA-256 record digests
   chained from a genesis digest (ADR-0245 §2.3: canonical JSON, no
   `default=str`, no truncation); `verify_replay_chain` re-derives everything
   from content, and any tamper breaks verification (pinned).
6. **Deterministic and pure** — no wall-clock, no randomness, no serve import
   (A-04 pinned).

## 2. Shipped ports (two genuinely non-identical native geometries)

| Port | Native geometry | Witness | Admit source of truth |
|---|---|---|---|
| `IdentityPort` (`core/ports/adapters.py`) | ADR-0246 grade-1 frame preservation | §3.7 scalars + §3.6 typed channel energies (channels live IN the witness so `decompose` is a pure re-shaping — no hidden adapter state to corrupt a replay) | `evaluate_admission` (ADR-0246; the adapter adds no policy) |
| `PrecisionPort` | ADR-0244 §2.5 / 0245 §2.2 f64→f32 cast transport | measured `cast_error` + f32 unit-norm deviation (subject from a certified `ServingState`) | both within caller tolerance |

Future adapters (Atlas, Evidence, Temporal/causal, Articulation, Action) plug
in identically; the interconnect grammar — not a second physics — is the whole
Ring-2 deliverable, exactly as §9 words it ("Smith/conformal language is the
interconnect grammar").

## 3. Non-goals (unchanged from the preflight)

No unified scheduler; no serve wiring (nothing imports this at serve — future
consumption is its own flag-gated unit); no bounded correctors; no new
algebra; no port semantics invented for organs that do not exist yet.

## 4. Consequences

Every organ that can measure a typed residual can now speak one auditable
decision grammar with abstain-or-proceed semantics and tamper-evident replay —
without surrendering its native geometry or gaining a central controller.
