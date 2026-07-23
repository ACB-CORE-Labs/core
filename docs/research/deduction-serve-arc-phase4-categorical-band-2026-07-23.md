# Deduction-serve arc — Phase 4 (Band v1b: categorical/syllogism serving), 2026-07-23

**Base:** `main` @ `6a54d27a`. **Branch:** `feat/deduction-serve-phase2` (stacked on Phase 1–3).
**ADR:** `docs/adr/ADR-0256` (updated — Band v1b now built).
**Depends on:** Phase 1 (composer), Phase 2 (lane), Phase 3 (arena + license).

## What shipped

`core chat` now decides **categorical syllogisms** end-to-end, closing the exact gap Phase 0's fork identified:

```
> All mammals are animals. All whales are mammals. Therefore all whales are animals.
Given: all mammal are animal; all whale are mammal. That's valid — all whale are animal follows.

> All cats are animals. All dogs are animals. Therefore all dogs are cats.
Given: all cat are animal; all dog are animal. That doesn't follow — all dog are cat isn't guaranteed by those premises.
```

The propositional bands (Phase 1–3) are unchanged. This is the marquee "basic logical work" widening — the Aristotelian syllogism.

## The Phase-0 fork, resolved

Phase 0 found the only categorical decider in the tree was `evals/syllogism/oracle.py` — the sealed independence oracle the comprehension lane scores against, which serving must never import (INV-25). Building a **production** decider was the fork's deferred half. Resolution: **`generate/proof_chain/categorical.py`** — a fresh decider that lowers a categorical argument to the propositional regime and rides the already-verified ROBDD engine. No new decision procedure; soundness inherits from the flagship engine.

### Why the lowering is sound AND complete (not "big enough domain")

A k-term categorical argument's model is fully determined by which of the `2^k` term-membership *profiles* are occupied. One Boolean atom `occ_j` per profile, and A/E/I/O become propositional formulas over those atoms (all S are P ≡ ⋀_{profiles with S but not P} ¬occ_j, etc.). Validity is then exactly propositional entailment — decided by the ROBDD engine. Because the profile atoms range over *all* occupancy patterns, this is sound and complete for the modern/Boolean reading (universals without existential import), with no reliance on a lucky domain size. Darapti and the other existential-import-only forms are correctly ruled INVALID.

### Independence (INV-25) preserved and proven

The decider shares no code with `evals/syllogism/oracle.py`. Their agreement — **case-for-case across the entire syllogism gold lane, and with the committed gold** — is the soundness evidence: two disjoint mechanisms (ROBDD-over-profiles vs. brute-force finite-model enumeration) converging (`tests/test_categorical_decider.py`).

## New / changed files

- **`generate/proof_chain/categorical.py`** (new) — the profile-lowering categorical decider (`decide_syllogism`, `lower_syllogism`, `syllogism_is_valid`); malformed input refuses (`CategoricalError`).
- **`generate/proof_chain/shape.py`** — `CATEGORICAL` band added (5 bands total).
- **`generate/proof_chain/render.py`** — `render_syllogism` (deterministic valid/invalid/inconsistent templates over the argument's own clauses).
- **`chat/deduction_surface.py`** — categorical branch (Band v1b): propositional path first, then `to_syllogism → decide_syllogism → render_syllogism`, license-gated through the shared `_license_gate` helper. Propositional behavior byte-identical.
- **`evals/deduction_serve/practice/gold.py`** — categorical band added to the arena: syllogism templates (4 valid Aristotelian forms + 2 invalid) with by-construction gold cross-checked against the independent syllogism oracle; `DeductionSolver` gains the dual (propositional + categorical) path, in lock-step with the composer.
- **`chat/data/deduction_serve_ledger.json`** — re-sealed: 5 bands, `categorical` earns SERVE at reliability 0.99087, wrong=0.
- **`evals/deduction_serve/runner.py`** + **`v1/cases.jsonl`** — the Phase-2 lane's `decide()` mirrors the composer's dual path; the 3 categorical cases (previously gold `declined`) reclassified to their true `valid`/`invalid` verdicts + 1 invalid case added (n: 27 → 28). Report + SHA pin regenerated (`b23234b4…`).
- **`tests/test_categorical_decider.py`** (new, 8 tests) + updates to `test_deduction_surface.py` / `test_deduction_serve_lane.py`.

## Honest wrinkles

- **Irregular plurals decline.** "All birds are animals. All **fish** are animals…" declines with `unknown_morphology` — the reader can't singularize "fish". Correctly a decline, not a wrong; a reader-morphology limit, documented, not worked around (the invalid-case corpus uses regular plurals like cats/dogs).
- **Surfaces read in singularized terms** ("all whale are animal") — grammatically rough but honest: those are the exact class ids the engine reasoned over. The deterministic-template honesty bar (no LLM) means no cosmetic re-pluralization that could drift from what was decided.

## Verification

```
uv run python -m pytest tests/test_categorical_decider.py -q            # 8 passed
uv run python -m evals.deduction_serve.practice.runner                   # 5 bands all SERVE, wrong=0
uv run python -m evals.deduction_serve.runner                            # 28/28, wrong=0
uv run core test --suite deductive -q                                     # 45 passed
uv run core test --suite smoke -q                                         # 180 passed
uv run core test --suite cognition -q                                      # 122 passed, 1 skipped
# deduction_serve lane SHA regenerates to the committed pin b23234b4…
```

## Verdict

Phase 4 complete. Categorical syllogism serving is live, sound+complete, independent-of-the-eval-oracle, earned through the same license machinery as the propositional bands. The serving band now spans propositional arguments and Aristotelian syllogisms — the core of "basic logical work". Remaining Phase-4 ideas (multi-word English proposition reader relaxation; multi-step proof recap) are documented as scoped-out in Phase 5, deferred deliberately rather than rushed against wrong=0.
