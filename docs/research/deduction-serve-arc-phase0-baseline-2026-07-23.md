# Deduction-serve arc — Phase 0 baseline (2026-07-23)

**Goal of the arc.** Ship CORE's first serious end-to-end reasoning workflow:

```text
user asks a simple logic question in `core chat`
  -> comprehend the question into typed premises + query
  -> decide it with the verified propositional/syllogism engine (wrong=0)
  -> articulate the verdict as a grounded, deterministic, provenance-tagged answer
  -> replayable, telemetered, governed by an EARNED serve license
```

**Base SHA:** `6a54d27a` (main == forgejo/main). Pinned numbers: `deduction-serve-phase0-baseline.json` (sibling).

This document is the evidence base the rest of the arc rests on. Phase 1 depends on it.

---

## The central finding (proven, not asserted)

**Every organ this workflow needs already exists and is verified wrong=0 — none of them are connected to each other on the serving path.** The arc is *wiring + earned licensing*, not new cognition machinery.

Demonstrated empirically (probe: `comprehend() -> projector -> independent oracle` vs `ChatRuntime.chat()` on the *same* text):

| Input | Organs in isolation | Serving path (`ChatRuntime.chat`) today |
|---|---|---|
| `If p then q. p. Therefore q.` | `to_deductive_logic` → ROBDD oracle → **entailed** | `grounding_source='pack'`, token-gloss surface, `refusal_reason=''` |
| `All mammals are animals. All whales are mammals. Therefore all whales are animals.` | `to_syllogism` → oracle → **valid=True** | `grounding_source='pack'`, token-gloss surface |

The serving surface for a decidable logic argument is literally *"Pack-resident tokens — pack-grounded (en_core_cognition_v1): then (relation.sequence.after; temporal.sequence), therefore (relation.consequence; logic.derivation). No session evidence yet."* — the deductive engine is bypassed entirely; the argument is treated as a bag of vocabulary tokens to gloss, not a problem to decide. It is not even an honest refusal (empty `refusal_reason`).

This is the disconnection the arc closes.

---

## Baseline lane numbers (all wrong=0)

Comprehension reader lanes (`prose -> comprehend() -> projector -> independent oracle vs gold`):

| Lane | total | correct | wrong | refused | Band v1? |
|---|---:|---:|---:|---:|:--:|
| propositional | 12 | 12 | **0** | 0 | ✅ |
| syllogism | 8 | 7 | **0** | 1 | ✅ |
| set_membership | 8 | 8 | **0** | 0 | — |
| total_ordering | 8 | 7 | **0** | 1 | — |
| relational_metric | 15 | 15 | **0** | 0 | — |
| relational_predicate | 18 | 18 | **0** | 0 | — |
| relational_inference | 13 | 13 | **0** | 0 | — |

Deductive engine lane (`evals/deductive_logic/report.json`, independent truth-table oracle, INV-25):

| split | n | correct | wrong | refused |
|---|---:|---:|---:|---:|
| dev | 200 | 200 | **0** | 0 |
| holdout_v1 | 500 | 500 | **0** | 0 |
| external_v1 | 16 | 16 | **0** | 0 |
| **combined** | **716** | **716** | **0** | **0** |

`all_correct=true`, `wrong_is_zero=true`.

ProofWriter-OWA refusal floor (`determine()` soundness): 19 total, 9 correct, **0 wrong**, 10 refused (acceptable coverage misses), 0 coverage gaps.

Smoke suite (in worktree, cold venv): **180 passed, 0 failed** (133s).

> Read the numbers honestly: these are small **curated gold corpora** (8–18 cases per comprehension lane), not a large real corpus. wrong=0 proves the organs are *sound on what they read*; the counts show the band is *narrow*. **Reader coverage is the wall, not the engine** — consistent with the standing project note that coverage is corpus-bound, not architecture-bound.

---

## Band v1 — precise input boundary (the key scoping result)

Band v1 = the two endorsed projectors: **propositional** (`to_deductive_logic`) + **syllogism** (`to_syllogism`). Their *natural-language input contract today* is narrower than the plan's illustrative example assumed, and the boundary is worth stating exactly, because it decides Phase 1 scope and Phase 4 widening.

The reader (`generate/meaning_graph/reader.py`) canonicalizes each noun-phrase slot via `_chunk` (lines 174–190). Its `_RESERVED` set (lines 109–120: `is, are, than, with, not, all, no, some, therefore, the, and, or, …`) makes `_chunk` **refuse any multi-token NP that contains a function word** — a parse-leak guard that refuses rather than chunk junk.

**Propositional band.** Reads an argument in `P1. P2. Therefore C.` declarative form where **each proposition/atom is a single content token** (`p`, `q`, `r`, or a one-word proposition). It **refuses**:
- multi-word English propositions like `the ground is wet` → `Refusal('reserved_word_in_np')` (contains `the`, `is`);
- interrogative propositional `Is q true?` → `Refusal('unreadable_member_query')` (the interrogative-propositional path is not wired; only the syllogism reader handles interrogatives).

**Syllogism band.** Reads `All/No/Some X are Y` categorical premises with **single-word class terms** (`mammals`, `whales`, `animals`), in **both** the declarative `Therefore all X are Y` form **and** the interrogative `Are all X Y?` form. The syllogism reader is the more natural-language-ready of the two.

**Consequence for the arc:** "natural-English conditionals" (`If it rains then the ground is wet…`) are **out of Band v1** — they need the multi-word-proposition relaxation, which is Phase 4 widening (relaxing `_chunk`'s reserved-word guard *without* breaking wrong=0), not Phase 1. Band v1 ships the forms that already read: single-token propositional arguments and single-word-term categorical syllogisms.

---

## Serving-path seams Phase 1 must touch (verified file:line)

- **REPL driver:** `core/cli.py::cmd_chat` constructs `ChatRuntime` only (not `CognitiveTurnPipeline`); the turn is `ChatRuntime.chat(text)`. Phase 1 wiring lives in `chat/runtime.py`, the real `core chat` path.
- **Live comprehension already on the turn path:** `chat/runtime.py:1342` calls `comprehend(text)` / `comprehend_relational(...)`, routing to `determine(...)` or `realize_comprehension(...)` — but **never** calls `to_deductive_logic` / `to_syllogism`. That is the missing edge.
- **Intent:** `generate/intent.py` `IntentTag` has 12 members; none catches conditional/syllogistic argument shape. A logic argument currently classifies `UNKNOWN` (or is dispatched to the pack token-gloss composer, as observed). Phase 1 adds `IntentTag.DEDUCTION` + deterministic classification, field-ratified like every tag.
- **Renderer:** `generate/determine/render.py::render_determination` is the sibling pattern; Phase 1 adds a deduction renderer for ENTAILED / REFUTED / UNKNOWN / REFUSED (deterministic templates, no LLM — honesty bar endorsed).
- **Surface precedence:** `docs/specs/runtime_contracts.md` "Current selection policy" gains `deduction_surface`; contract tests updated in the same PR. Trace-hash folds only-when-non-empty so legacy hashes stay byte-identical.
- **Fail-closed (INV-34):** reader `Refusal` → typed refusal surface; projector `None` / oracle `REFUSED` → honest `out_of_decidable_regime`; never a fluent-but-ungrounded surface.
- **Flag:** all Phase 1 behavior behind `deduction_serve` (default off), byte-identical when off.

## What Phase 0 confirms is already handled (no work needed)

- **W-012 is fixed:** `chat/runtime.py:2692-2705` catches `InnerLoopExhaustion` and materializes a typed `refusal_reason`. (The zone card's "still lacking except" note is stale.)
- **Engine is telemetry-wired but surface-inert:** `pipeline.py:1203` runs `evaluate_entailment_with_trace` on precise VERIFICATION triples, folded into `operator_invocation` only — never the surface. Confirms the engine is trusted evidence, just not a decider on the serving path.

## Scope-outs (documented, not on this arc's critical path)

- **ADR-0246 §3.7 identity-wave calibration stays OFF** — blocked on §11 grounding *research evidence* (currently NULL; benign false-refusal 1.00; no benign/adversarial separation), not wiring.
- **Tier-2 two-reader convergence** waits for the field reader (Phase W); today's two registered readers operate on disjoint domains and never co-decide.
- **Reader→Hamiltonian compiler** stays eval-side (its real-NL reach is 5/500); it is not this workflow's vehicle.

---

## Verdict

Phase 0 complete. Baseline pinned, all lanes wrong=0, smoke green, Band v1 boundary defined precisely, the crux disconnection proven with a runnable probe. **Proceed to Phase 1** (deduction turn spine behind `deduction_serve`), scoped to the two forms that already read: single-token propositional arguments and single-word-term categorical syllogisms.
