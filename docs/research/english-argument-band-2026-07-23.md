# English-clause argument band (Band v2-EN) — natural-language deduction serving, 2026-07-23

**Base:** `main` @ `1a6ccaf9`. **Branch:** `feat/english-argument-band`. **ADR:** `docs/adr/ADR-0257-english-clause-argument-band.md`.

## The gain, stated as transcripts

Everything below **declined yesterday**. It is decided today — same sound engine, wrong=0 discipline intact, licenses earned not granted:

```
> If it rains then the ground is wet. It rains. Therefore the ground is wet.
Given: if it rains then the ground is wet; it rains. Your premises entail: the ground is wet.

> If the alarm is armed then the light is on. The light is not on. Therefore the alarm is not armed.
Given: if the alarm is armed then the light is on; the light is not on. Your premises entail: the alarm is not armed.

> Either the door is open or the window is open. The door isn't open. Therefore the window is open.
Given: either the door is open or the window is open; the door is not open. Your premises entail: the window is open.

> If the pump runs then the tank fills. If the valve opens then the tank fills. The pump runs or the valve opens. Therefore the tank fills.
Given: …. Your premises entail: the tank fills.        (constructive dilemma)

> If p then q. Therefore if not q then not p.
Given: if p then q. Your premises entail: if not q then not p.   (contraposition — the other former boundary case)
```

The two texts ADR-0256's completion doc recorded as "the future acceptance tests" (`out_of_band_multiword_conditional`, `out_of_band_nested_negation`) are both now decided — their eval-lane gold updated from `declined` to `entailed` accordingly.

## What was built

| Piece | File | Role |
|---|---|---|
| English argument reader | `generate/proof_chain/english.py` (new) | Closed function-word grammar over OPAQUE clause-atoms; minted atom ids; typed refusals; caps |
| English renderer | `generate/proof_chain/render.py::render_entailment_english` | Verdicts over the user's own clauses; UNKNOWN explicitly scoped to the opaque reading |
| Band constants | `generate/proof_chain/shape.py` | `en_conditional_single/chain`, `en_disjunctive`, `en_atomic`; `ALL_SHAPE_BANDS` |
| Composer fallback tier | `chat/deduction_surface.py::_english_band_surface` | Tried strictly AFTER v1/v1b — monotone widening, byte-identical on everything previously served |
| Arena extension | `evals/deduction_serve/practice/gold.py` | 4 en-bands × 720 synthetic copular-clause cases; gold by construction, oracle-checked with NO reader in the loop |
| Sealed ledger (9 bands) | `chat/data/deduction_serve_ledger.json` | All 9 bands wrong=0 at n=720 → reliability 0.99087 ≥ θ_SERVE=0.99 → SERVE earned |
| Real-English eval lane | `evals/deduction_serve/v2_en/cases.jsonl` (26 cases) | Hand-authored natural prose, content disjoint from the synthetic lexicon — anti-overfit guard |
| Tests | `tests/test_english_argument_reader.py` (new, 33 asserts across 20 tests) + extensions | Reader contract, guards, surfaces, license hedging, e2e through `ChatRuntime` |

## Why it is sound (the one theorem the design leans on)

Propositional entailment is closed under uniform substitution. So ENTAILED / REFUTED / inconsistent verdicts over opaque clause-atoms stay true under ANY deeper reading of the clauses — those serve at full strength. UNKNOWN is the one non-substitution-safe verdict, so it (a) renders with an explicitly scoped phrasing ("Reading each clause as one indivisible claim…"), and (b) is protected by structural guards: quantifier-led categorical clauses, `is a/an` membership clauses, and unnormalizable negation all refuse OUT of the opaque band (typed reasons), so a real syllogism can never be flattened into a misleading "doesn't follow". Ambiguous scope (`and`+`or` mixed, nested conditionals) refuses rather than guesses.

## Earned, not granted

The `en_*` bands ride the exact ADR-0256 license machinery: absent from the ledger ⇒ hedged automatically (tested); present with wrong=0 at volume ⇒ authoritative. The arena run that sealed them: 9 bands × 720 = 6,480 cases, wrong=0 everywhere, in ~1.8s. Strip the ledger and every answer above still comes back — sound but DISCLOSED. That remains the difference between a flagged capability and an earned one.

## Tri-language posture (per direction, recorded in ADR §5)

The atom table, soundness argument, caps, refusal discipline, license machinery, and engine are language-neutral; only the structural lexicon + clause-order conventions are English. A `grc_*`/`he_*` sibling band is a reader module + its own earned licenses through pack ratification (ADR-0253 boundary respected) — NOT a premature lexicon parameter (ἄρα is postpositive; a lexicon swap alone cannot read real Greek; recorded so we don't build a hollow abstraction). The en-band refusal telemetry (`internal_negation_unread`, `ambiguous_and_or`) is the instrumented trigger: it marks exactly where English is the bottleneck and the explicit-morphology languages would read clean.

## Honest scope-outs

1. **`member_chain` band** ("Socrates is a man. All men are mortal. Therefore Socrates is mortal.") — guarded out with a typed reason; the designed next band (per-individual propositional lowering, same pattern as `categorical.py`).
2. **Verb-phrase negation** ("doesn't start") — refuses; de-conjugation is real morphology work (or the tri-language path).
3. **Proof-step recap** — verdicts only, unchanged scope-out.
4. **Flag** — still `deduction_serving_enabled=False` default; no new flag; flip remains ratification.

## [Verification]

```
uv run core test --suite deductive -q     # 83 passed
uv run core test --suite smoke -q          # (pre-push gate — run in worktree)
uv run core test --suite cognition -q      # (regression: shared reader untouched)
uv run python -m evals.deduction_serve.practice.runner        # 9 bands SERVE, wrong=0
uv run python -m evals.deduction_serve.runner                 # v1 28/28, v2_en 26/26
# ledger self-verifies content_sha256; lane report re-pinned (verify_lane_shas.py)
```
