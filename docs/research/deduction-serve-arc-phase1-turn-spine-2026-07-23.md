# Deduction-serve arc — Phase 1 (deduction turn spine), 2026-07-23

**Base:** `main` @ `6a54d27a` (same base as Phase 0). **Branch:** `feat/deduction-serve-phase1`.
**Depends on:** Phase 0 baseline (`docs/research/deduction-serve-arc-phase0-baseline-2026-07-23.md`).

## What shipped

`core chat` now decides propositional-argument questions with the verified
ROBDD entailment engine, behind a default-off flag. The workflow the arc set
out to prove is real end-to-end:

```
$ core chat
> If p then q. p. Therefore q.
Given: p implies q; p. Your premises entail: q.
```

Flag off, the exact same input still returns the pre-arc pack-token-gloss
surface, byte-for-byte — nothing changes for any existing deployment until
the flag is explicitly turned on.

## New files

- **`chat/deduction_surface.py`** — the DEDUCTION composer, sibling to
  `chat/oov_surface.py` / `narrative_surface.py` / `example_surface.py` (same
  established pattern: a pure `<name>_grounded_surface(text) -> str | None`
  function `chat/runtime.py` calls into). Owns the commit-gate
  (`looks_like_deductive_argument`) and the fail-closed decision tree:
  reader refusal → typed decline, out-of-band shape → typed decline,
  otherwise decide via the engine and render.
- **`generate/proof_chain/render.py`** — `render_entailment(trace, premises, query)`,
  a sibling to `generate/determine/render.py`'s `render_determination` but for
  `EntailmentTrace` instead of `Determined`. Four deterministic templates
  (ENTAILED / REFUTED / UNKNOWN / REFUSED), no LLM, no synthesis — every
  visible token is either fixed prose or a literal formula string the
  projector produced from the user's own text.
- **`tests/test_deduction_surface.py`** — 15 tests: pure-function contract,
  flag-off byte-identity, flag-on single-turn behavior, and an end-to-end
  regression that decides the **full propositional gold corpus through the
  real `ChatRuntime.chat()` path** across one multi-turn session (not just
  the isolated comprehend→project→oracle lane) — wrong=0.

## Changed files (small, surgical)

- **`core/config.py`** — `RuntimeConfig.deduction_serving_enabled: bool = False`.
- **`generate/intent.py`** — `IntentTag.DEDUCTION` added. Additive only:
  `classify_intent` / `classify_compound_intent` never produce it — the
  DEDUCTION composer runs *before* generic intent classification is even
  invoked (see "Design decisions" below), and only stamps this tag onto
  `self._last_intent` for `/explain` observability fidelity on a turn it
  actually commits to.
- **`chat/runtime.py`** — one flag-gated block inside
  `_maybe_pack_grounded_surface` (the existing pack/teaching/partial/oov
  dispatcher) plus a `grounding_source` docstring update. No other lines
  touched.

## Design decisions (and why)

**1. A shape-check + direct composer, not `IntentTag`-routed classification.**
The plan called for "IntentTag.DEDUCTION + classification." Tracing
`classify_intent`'s call sites first surfaced a real hazard: if the core
classifier itself started returning `DEDUCTION` for "therefore"-shaped text
*unconditionally* (regardless of the flag), previously-`UNKNOWN` prompts
would silently stop reaching the pack-token-gloss branch even with the flag
off — a byte-identity violation. The fix: `classify_intent`'s own rule table
is untouched; a separate, flag-gated pre-check
(`looks_like_deductive_argument`) intercepts *before* generic classification
runs at all. Flag off, the new code path is never entered — provably
byte-identical (verified: see tests + manual probe below).

**2. `grounding_source="deduction"` is NOT registered in
`core.epistemic_state.GroundingSource`.** That `Literal` is a closed,
cross-stack contract — mirrored in `workbench/schemas.py`, a TypeScript union
in `workbench-ui/src/types/api.ts`, a badge-metadata table, and a build-time
`enumCoverage.test.ts` snapshot test. Extending it properly means touching
Python *and* TypeScript *and* regenerating a UI enum snapshot — real scope,
not a one-line addition. Since `core chat` REPL turns never flow through
Workbench's `CognitivePipelineRecord` path (confirmed: no `TurnEvent` import
anywhere under `workbench/`), the extension is inert for this arc's actual
consumer. `ChatResponse.grounding_source` itself is typed as plain `str` (not
the `Literal`), so nothing breaks at runtime — `epistemic_state_for_grounding_source("deduction")`
falls through to the honest `EPISTEMIC_STATE_NEEDED` default. Registering
"deduction" as a first-class `GroundingSource` + Workbench badge is deferred
to a follow-up if/when that visibility is actually needed — documented
in-line at both the flag and the field.

**3. The dispatch-order bug an early manual probe caught.** First
implementation placed the deduction check *after* the existing
`if not allow_warm and gate_source != "empty_vault": return None` early-out
(matching the literal insertion point I'd scoped). Running the full
propositional gold corpus through one live multi-turn session caught it
immediately: turn 12 fell through silently once the vault was no longer
"empty" (`gate_source` had changed), because that early-out returns *before*
reaching any composer. Pack/teaching/partial/oov are legitimately
cold-start-only fallbacks — but deduction serving isn't: a user should be
able to ask a logic question at any point in a conversation. Fix: moved the
deduction check to run *before* that gate (it depends only on input text, no
vault/field state). Re-running the full corpus confirmed 12/12 correct, 0
wrong, 0 declined, 0 mis-routed, across the same session.

**4. Band v1 stays propositional-only, exactly as scoped in Phase 0.**
Categorical/syllogism "therefore" arguments *commit* (they're
argument-shaped) but are honestly declined as out-of-band
(`"...not categorical 'all/no/some' ones yet"`) rather than silently
mis-served or falling through to the old gloss. `evals.syllogism.oracle` is
never imported anywhere in the new code — the sealed independence oracle
stays sealed (INV-25 intact). A production categorical decider is Band v1b,
deferred per the Phase 0 fork analysis.

## Verification

```
uv run python -m pytest tests/test_deduction_surface.py -q   # 15 passed
uv run core test --suite smoke -q                             # 180 passed
uv run core test --suite cognition -q                          # 122 passed, 1 skipped
uv run python -m pytest tests/test_dispatch_trace.py tests/test_oov_surface.py -q  # 26 passed
uv run python -m pytest tests/test_intent*.py -q                # 145 passed
```

Manual end-to-end probe (flag on) — the exact workflow the arc targeted:

```
If p then q. p. Therefore q.
  -> Given: p implies q; p. Your premises entail: q.
p or q. Not p. Therefore q.
  -> Given: p or q; not p. Your premises entail: q.
p. Not p. Therefore q.
  -> Given: p; not p. Those premises are inconsistent — they can't all be
     true, so I won't assert anything from them.
p or q. Therefore p.
  -> Given: p or q. Your premises don't settle whether p — it holds in
     some cases and fails in others.
All mammals are animals. All whales are mammals. Therefore all whales are animals.
  -> That reads as an argument, but right now I can only decide plain
     propositional arguments (not categorical 'all/no/some' ones yet).
If it rains then the ground is wet. It rains. Therefore the ground is wet.
  -> That reads as an argument, but I can't parse it precisely enough to
     decide it yet (reserved_word_in_np).
```

Flag off, the same six inputs return byte-identical pre-arc surfaces
(`grounding_source="pack"`, the token-gloss text) — confirmed directly, not
merely assumed.

## Verdict

Phase 1 complete. The `core chat` REPL genuinely decides basic propositional
logic questions end-to-end, deterministically, with wrong=0 held across the
full gold corpus and a multi-turn session. Proceed to Phase 2 (a formal,
SHA-pinned serving-path eval lane, scoring the production decider itself —
not the isolated comprehend→project→oracle chain the Phase 0 lanes already
cover).
