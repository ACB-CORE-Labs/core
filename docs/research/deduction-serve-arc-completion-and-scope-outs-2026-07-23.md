# Deduction-serve arc — completion + honest scope-outs (Phase 5), 2026-07-23

**Base:** `main` @ `6a54d27a`. **Branches:** `docs/deduction-serve-phase0-baseline`, `feat/deduction-serve-phase1`, `feat/deduction-serve-phase2` (Phases 2–5, stacked).
**ADR:** `docs/adr/ADR-0256-deduction-serve-earned-license.md`.

## The goal, met

The arc set out to get CORE's cumulative reasoning organs firing as a real workflow:

> a user asks a simple logic question in `core chat` → CORE reasons → an articulated response comes back.

That workflow is live (behind a default-off, earned-license-gated flag):

```
> If p then q. p. Therefore q.
Given: p implies q; p. Your premises entail: q.

> p or q. Not p. Therefore q.
Given: p or q; not p. Your premises entail: q.

> All mammals are animals. All whales are mammals. Therefore all whales are animals.
Given: all mammal are animal; all whale are mammal. That's valid — all whale are animal follows.

> All cats are animals. All dogs are animals. Therefore all dogs are cats.
Given: all cat are animal; all dog are animal. That doesn't follow — all dog are cat isn't guaranteed by those premises.
```

Pinned end-to-end through the actual `ChatRuntime` spine (`tests/test_deduction_serve_e2e.py`), not just the composer in isolation.

## What each phase delivered

| Phase | Deliverable | Key artifact |
|---|---|---|
| 0 | Baseline: organs verified wrong=0, serving disconnection proven, Band v1 boundary pinned | `deduction-serve-arc-phase0-baseline` doc + JSON |
| 1 | Deduction turn spine (flag-gated propositional serving) | `chat/deduction_surface.py`, `generate/proof_chain/render.py` |
| 2 | End-to-end serving eval lane, SHA-pinned wrong=0 | `evals/deduction_serve/` |
| 3 | Earned SERVE license via the reliability gate (arena instance #2) | `chat/deduction_serve_license.py`, `chat/data/deduction_serve_ledger.json`, ADR-0256 |
| 4 | Band v1b: production categorical/syllogism decider | `generate/proof_chain/categorical.py` |
| 5 | End-to-end REPL-path proof + telemetry wiring + this doc | `tests/test_deduction_serve_e2e.py` |

The reliability substrate (ADR-0175/0199) gained its first non-estimation serving consumer; the deductive engine (ADR-0201/0218) got its first user-facing serving consumer; the comprehension reader's NL→logic projectors got their first live serving path. Five verified organs, wired into one workflow.

## Peripheral systems (Phase 5 checks)

- **Discovery-yield (ADR-0255).** Deduction turns are well-formed served turns: `turn_log` grows and `_context.turn` advances, so when the flag is enabled and real traffic flows, ADR-0255's `served_turns_since_reset` denominator counts them. Nothing to build — the counter is automatic; `yield_rate` stays `null` until the flag is on and turns are served, exactly as ADR-0255 specifies. Deduction turns do **not** emit discovery candidates (they produce a decided answer, not a "would-have-grounded" gap), so they lift the denominator without inflating the numerator — an honest yield signal.
- **Telemetry / observability.** Every deduction turn carries `grounding_source="deduction"` on both `ChatResponse` and `TurnEvent`, and a `DispatchAttempt(source="deduction", outcome="admitted", reason="deduction_composer_committed")` in the dispatch trace. Fully observable without new schema.

## Honest scope-outs (deliberately NOT done, with rationale)

These were considered and deferred — each is a real decision, not an oversight.

1. **Multi-word English propositions** (`"If it rains then the ground is wet…"`). Still declined (`reserved_word_in_np`). Relaxing `generate/meaning_graph/reader.py::_chunk`'s reserved-word guard would let natural conditionals in, but that guard is shared by every comprehension lane and is load-bearing for their wrong=0. It deserves its own careful pass with the comprehension lanes as the regression gate — not a rushed change inside this arc. **Deferred, with the two boundary cases (`out_of_band_multiword_conditional`, `out_of_band_nested_negation`) documented as the future acceptance tests.**
2. **Multi-step proof recap in the surface.** `render_entailment`/`render_syllogism` state the verdict, not the derivation chain. A real step-by-step recap would give `proof_chain/builder.py` + `modus_ponens` (currently zero live consumers) their first use. Additive, low-risk, but net-new articulation work — **deferred to a future articulation-depth pass** (the `generate/` "core_logos" arc, Phase 6 per the intelligence-loop plan).
3. **`accrue_realized_knowledge` default-on.** Left default-off. Composing "teach a fact across turns → ask a deduction over it" is valuable but couples this arc to the session-accrual path's own calibration; out of scope here.
4. **ADR-0246 §3.7 identity-wave calibration stays OFF.** Unchanged and untouched. It is blocked on §11 grounding *research evidence* (currently NULL; benign false-refusal 1.00), not on wiring, and is not on this workflow's critical path.
5. **Tier-2 two-reader convergence** waits for the field reader (Phase W); today's registered readers operate on disjoint domains and never co-decide. The deduction serving path registers no new Tier-2 reader.
6. **Reader→Hamiltonian compiler stays eval-side.** Its real-NL reach is 5/500; it is not this workflow's vehicle and was not wired into serving.
7. **`grounding_source="deduction"` not registered in the closed `GroundingSource` Literal.** Documented in Phase 1 — the closed enum is a cross-stack (Python + TypeScript + Workbench-badge) contract, and `core chat` REPL turns don't flow through Workbench's pipeline-record path, so registering it is inert for this arc's consumer. Deferred to a follow-up if/when Workbench visibility is wanted.

## Verification (whole arc, final)

```
uv run core test --suite deductive -q     # 50 passed (all arc tests)
uv run core test --suite smoke -q         # 180 passed
uv run core test --suite cognition -q      # 122 passed, 1 skipped
uv run core test --suite algebra -q        # (field invariants — unaffected, green)
# both eval lanes regenerate to their committed pins;
# the 5-band practice ledger self-verifies its content_sha256.
```

## Verdict

Deduction-serve arc complete (Phases 0–5). `core chat` decides propositional arguments and Aristotelian syllogisms end-to-end — sound, deterministic, wrong=0-verified, earned through the reliability gate, and fully telemetered — behind a default-off flag awaiting Shay's ratification to flip live. The remaining frontier (natural multi-word English, proof recap, cross-turn accrual) is documented and deferred deliberately, not left implicit.
