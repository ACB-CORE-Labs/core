# determine-phase — `generate/determine/`

**Kind:** zone→component descent · **Parent:** M3 (serve seam → M4) · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal`, flag-gated (**demoted** from the map's `live-serving`) · **Fitness:** `fit` · **Topology role:** runtime boundary

> The open-world DETERMINE gear: answer a question *from what the engine has realized in this conversation*, affirmatively or not at all. INV-30 is its constitution — it constructs only `Determined(answer=True)` or refuses; absence never refutes. It is the closest thing CORE has to "thinking with what it just learned," and it is off by default.

## What it is / What it does

Eight modules, 1071 lines: `determine.py` (the gear), `consolidate.py` (Step D — one semi-naive layer of member/subset closure per idle tick, every hop verified by the proof_chain ROBDD before `realize_derived` writes it back; `member ∘ member` structurally unreachable; four declared strict-order predicates in `TRANSITIVE_PREDICATES`), `estimate.py` + `estimation_license.py` (Step E — converse-guess under an earned SERVE license, always disclosed `[approximate]`), `derived_close_proposals.py` (PR-2 bridge — eligible derived facts emitted as proposal-only artifacts), `render.py` (42 — honest rendering: SPECULATIVE grounds read "as I was told", never "verified").

## The gating map (all call sites verified)

| Entry | Caller | Gate | Default | Daemon forces? |
|---|---|---|---|---|
| `determine()` / `render_determination` | `chat/runtime.py:1364,1303` via `_accrue_in_turn` / `_surface_determination` | `accrue_realized_knowledge` | **False** | **No** |
| `consolidate_once` | `chat/runtime.py:1041` via `idle_tick` | `consolidate_determinations` | False | **Yes** |
| `estimate_converse` + `serve_license` | `chat/runtime.py:1420` | `estimation_enabled` | False | No |
| derived-close proposal emission | `chat/runtime.py:1054` via `idle_tick` | `review_derived_close_proposals` | False | No |

A default-config serving turn **never** reaches this package. The map's `live-serving` label is wrong at this SHA: `live-internal`, flag-gated, exercised by lanes (`evals/close_derived_climb`, `evals/determination_closure`, `evals/determination_estimation`).

## Two discrepancies this table surfaces

1. **The daemon enables the consolidator but not the accruer.** `CONTINUOUS_LIFE_CONFIG_FLAGS` forces `consolidate_determinations=True` but leaves `accrue_realized_knowledge=False` — yet `realize_comprehension` (the only turn-path writer of realized facts) sits behind the *accrual* flag. Under the continuous-life config as coded, the idle consolidator may have nothing to consolidate unless realized facts arrive some other way. Either the flag set is incomplete, or consolidation under the daemon is deliberately dormant-until-seeded. **Unresolved; needs a ruling or a test that seeds through the lived path.**
2. **A prior verification document is contradicted at this SHA.** `docs/research/architecture-assessment-verification-2026-07-25.md` §2 states `accrue_realized_knowledge` "is enabled by the production L10 process." The daemon's flag set does not include it. Either the doc anticipated a change that never landed, or the flag was later removed. Doc/code discrepancy — record, don't guess.

## Contract & evidence

- INV-30 (True-or-refuse; three visible `Determined` construction sites; typed rejection of forged `ClosedFrame`) — pin: `tests/test_architectural_invariants.py`.
- Derived facts stay SPECULATIVE (sound inference never upgrades premise standing); replayable `Derivation` provenance (premise `structure_key`s + rule + `entailed` verdict) — contract: `runtime_contracts.md` §Idle consolidation.
- wrong=0 by proof-gating: only `ENTAILED` conclusions are written — lane: `evals/close_derived_climb` (fixed-point climb, monotone, saturated tick consolidates 0).

## Judgment

**Fitness: `fit`.** The gear is small, typed, proof-gated, and honestly rendered. The INV-30/INV-31 firewall against closed-world machinery is among the cleanest boundaries in the repository.

**Honest wrinkles:** the entire "think with what you learned this session" capability — arguably the most *alive*-feeling behavior CORE has — is dark on every default path and only partially lit by the daemon. The `_accrue_in_turn` docstring calls DETERMINE and the readers "total (typed results, no raises)" while wrapping them in a broad defensive guard; the guard is honest backstop, but any exception it eats disappears silently into a no-op accrual (`_last_turn_accrual=None`) with no telemetry of the swallow. Flagged for Phase 4 as a small silent-failure surface inside an otherwise typed layer.

**Open questions:** the daemon flag-set completeness (→ ruling); should accrual-swallowed exceptions be counted in telemetry? (→ Phase 4)
