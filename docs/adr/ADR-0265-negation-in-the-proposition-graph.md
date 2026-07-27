# ADR-0265 — Negation belongs in the proposition graph, and clause grammar has one owner

- **Status:** Accepted — ratified by Joshua Shay 2026-07-27. **This ADR changes
  served output.** It fixes a truth defect on a serving path; it flips no flag
  and changes no default. Implemented and merged to `main` in the same unit
  that proposed it, because the defect it removes was live behind a shipped
  flag rather than latent.
- **Date:** 2026-07-27 · **Ratified:** 2026-07-27
- **Implemented by:** #137. Enforcement pins:
  `tests/test_negation_survives_articulation.py` (registered in the `smoke`
  pre-push gate in the same PR).
- **Arc:** grammar-unification Phase 5
  (`docs/plans/grammar-unification-2026-07-26.md`), following Phase 4 (#135, #136).
- **Governs:** `GraphNode.negated`, `graph_from_intent`, `ground_graph`,
  `plan_articulation` (`generate/graph_planner.py`),
  `generate/intent_bridge.py`, the depth-enrichment rebuild in
  `core/cognition/pipeline.py`, and the division of labour between
  `generate/semantic_templates.py` (discourse framing) and
  `generate/templates.py` (clause grammar).
- **Supersedes:** the implicit claim in
  `core/cognition/surface_resolution.py` that the `realize_semantic` path,
  "granted supremacy by the Shadow Coherence Gate", was safe to grant supremacy
  *to*. It was not, on any turn carrying a denial.
- **Builds on:** ADR-0261 §5.1 (refuse, don't drop) — this is the same failure
  in a different organ.

## 1. Context

Phase 4 (#136) recorded that `render_semantic` has no `negated` parameter and
pinned the consequence as a defect. That pin was correct and incomplete. The
defect is not one missing parameter; it is **two independent drops in series**,
and the first one is in the graph.

`generate/intent.py` has always recovered denial from the user's text
(`intent.negated`, set from the `does|do|did not` group of
`_DECLARATIVE_RELATION_RE`). Downstream, every stage discarded it:

| stage | what it did with the denial |
|---|---|
| `graph_from_intent` | dropped it — `GraphNode` had **no field** for it |
| `ground_graph` | rebuilt nodes field-by-field; nothing to carry |
| pipeline depth enrichment | rebuilt nodes field-by-field; nothing to carry |
| `plan_articulation` | could not carry what the node did not hold |
| `realize_semantic` | never read `step.negated` |
| `render_semantic` | had no parameter for it |

Measured on `main` @ `536d6e55`, with `realizer_grounded_authority=True`:

```
"evidence does not support truth"  -> 'Evidence is verified: what supports truth.'
"evidence supports truth"          -> 'Evidence is verified: what supports truth.'
```

Byte-identical. **CORE affirmed what the user denied.**

### 1.1 Why every existing gate was green

On the default config the realizer runs on an ungrounded graph, emits `...`,
and `_is_useful_surface` rejects it — so the runtime's echo wins the resolver,
and the echo happens to contain the user's own "does not". The truth path was
correct **by accident**. ADR-0088 Phase B removes the accident by grounding the
graph before realizing, which is precisely when the realizer's surface becomes
useful enough to win.

So the defect sat behind a shipped flag, invisible to every property-of-one-
surface test, because no test compared a denial to its assertion. The failure
mode is [[feedback-ask-what-if-the-thing-were-absent]] in its purest form: the
measurement would have looked identical with the mechanism removed, because the
mechanism was never there.

## 2. Decision

**R1 — A proposition graph must be able to represent denial.**
`GraphNode` gains `negated: bool = False`, threaded from `intent.negated`
through `graph_from_intent`, `ground_graph`, the pipeline's depth enrichment,
`intent_bridge`, and into `ArticulationStep` via `plan_articulation`.

Serialized **only when True**, so every pre-existing `as_dict` — and every
`trace_hash` folded from one — stays byte-identical. This is why the change
lands without touching a lane pin.

**R2 — Clause grammar has exactly one owner.**
Four of the eight intent "templates" were never frames; they were plain clauses
(`{subject} {predicate_h} {obj}`, optionally with a pinned predicate or a
prefix). Those now delegate to `generate.templates.render_step`, the single
owner of English clause grammar.

Writing a second copy of negation into `semantic_templates.py` was the
tempting fix and is rejected: Phase 2A spent a whole unit giving every
linguistic fact one owner, and a second negation implementation rebuilds that
disease one level up. The rejected design would have grown quantifier
agreement, then tense, then aspect, until `semantic_templates.py` was a second
grammar.

The delegation is **provably output-preserving**: 192 of 192 surfaces are
byte-identical across all four delegated intents × every predicate in
`PREDICATE_DISPLAY` (plus an unknown one) × every object sentinel. The only
surfaces this ADR moves are ones that were wrong.

**R3 — A frame that cannot deny must not pretend to assert.**
Frames retaining a finite verb (VERIFICATION, PROCEDURE, COMPARISON) get an
explicit negated form. RECALL — a speech act, with no proposition in it to deny
— falls back to the clause path rather than emit a frame that silently drops
the denial. Losing the framing is the correct trade against asserting the
opposite of the graph (ADR-0261 §5.1).

**R4 — An intent with no frame of its own falls back to the UNKNOWN *clause*,
not the UNKNOWN *template*.**
The old default sent unframed intents to a format string that cannot say "not".
Five live intents were sitting on it — TRANSITIVE_QUERY, FRAME_TRANSFER,
NARRATIVE, EXAMPLE, DEDUCTION — each serving a denial as its own assertion.
They were found by the exhaustive control in R5, not by inspection. The default
must be the capable path so the next intent added inherits correctness.

**R5 — The pins assert a difference, and one of them is structural.**
- The load-bearing test compares a denial's served surface to its assertion's,
  end to end through the real pipeline under `realizer_grounded_authority`.
  Asserting a *difference* is the only shape that catches a writer collapsing a
  distinction; every property-of-one-surface test was green throughout.
- An exhaustive control requires **every** `IntentTag` to distinguish the two.
- A structural invariant requires every `GraphNode(...)` construction in
  serving code to name `negated` explicitly or be recorded in an allowlist with
  a reason. The defect was five separate constructors each defaulting to
  `False`; a per-site test must be written per site, and a site added without
  one is invisible. Only `recognition/connector.py` is exempt, because an
  `EpistemicNode` has no polarity to carry.

## 3. Consequences

**What changes for a user.** On turns where the realizer's surface wins the
resolver and the input carried a denial, CORE now says "not". Previously it
said the opposite. No other turn changes: lane pins are 11/11 byte-identical
and smoke/deductive counts move only by the new tests.

**What this does not do.** `quantifier`, `tense` and `aspect` remain
unexpressed on the serving path. That is deliberate, not an oversight: **no
producer sets them.** `plan_articulation` has no source for them, and no parser
populates them, so threading them now would be speculative machinery with no
caller — the honest-placeholder discipline. They are expressible the moment a
producer exists, because the clause owner already handles all three.

**What it costs.** `render_semantic` now imports `render_step`, so
`semantic_templates` depends on `templates`. That is the correct direction:
framing composes grammar, not the reverse.

**Thesis check** (`decoding, not generating`): a graph that cannot represent
denial cannot *decode* a denial — it can only generate an affirmative that
resembles the input. Carrying polarity through the graph makes the articulation
a function of what was understood. This ADR strengthens the thesis rather than
straining it.

## 4. Alternatives rejected

**Add negation handling to `semantic_templates.py` directly.** Smallest diff,
and it rebuilds the two-grammar disease Phase 2A removed. Rejected under R2.

**Promote `realize_target` wholesale to the serving path** (Phase 4 option (a)
in its raw form). Maximum hash churn, and it *loses* the intent framing and
depth notes that `realize_semantic` genuinely has. The delegation gets the
grammar without discarding the framing. Rejected as strictly worse.

**Leave it pinned as a defect** (the Phase 4 resting state). A documented truth
defect with a green test beside it is exactly the comfortable state this arc
exists to make uncomfortable. Rejected once the exposure was measured as live
rather than latent.

**Fail closed — refuse to realize a step carrying a denial.** Consistent with
ADR-0261, and strictly worse here: the clause owner can already *express* the
denial correctly, so refusing would discard information CORE holds and
understands. Refusal is right when expression is impossible, not when it is one
delegation away.
