# realize-phase — `generate/realize/` (and the reader that feeds it)

**Kind:** zone→component descent · **Parent:** M3 · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-internal`, flag-gated (**demoted** from the map's `live-serving`) · **Fitness:** `fit` (the phase) — with its *feeder* under held fabrication findings · **Topology role:** runtime boundary

> REALIZE — "integrate comprehended structure into the held self" (roadmap Step 3). If M1 is knowledge at rest and DETERMINE is answering from it, REALIZE is the moment comprehension becomes *held*: a reading of the user's words is written into session memory as a typed, SPECULATIVE, as-told record. It is the exact point where a misreading becomes a belief — which is why the fabrication findings matter most here.

## Disambiguation (a naming trap, recorded permanently)

`generate/realize/` (**knowledge** realization — this card) and `generate/realizer.py` (**surface** realization — the articulation renderer, M4) are unrelated mechanisms with confusable names. The map's `realize-phase` zone is the former. Any future search for "realizer" work must state which one it means.

## What it is / What it does

Four modules, 645 lines: `realize.py` (425 — `realize_comprehension`, `realize_derived`, `Realized`/`NotRealized`/`RealizedRecord`, `Derivation`), `quantitative.py` (135 — `realize_quantitative`), `recall.py` (62 — `recall_realized`, DETERMINE's read path), `__init__.py`. Writes go through the INV-21-allowlisted vault writer; records carry `epistemic_status="speculative"` and derived records carry full `Derivation` provenance so replay re-derives and re-verifies.

Call graph (verified): `chat/runtime.py:1367` `_accrue_in_turn` → `realize_comprehension` (gate: `accrue_realized_knowledge=False` default, **not** daemon-forced); `generate/determine/consolidate.py:44` → `realize_derived` (gate: `consolidate_determinations`, daemon-forced); `derived_close_proposals.py:25` → `recall_realized`. Same demotion as determine-phase: no default serving turn reaches this package.

## The feeder — where the fabrication findings live

`_accrue_in_turn` comprehends via `generate/meaning_graph/reader.py::comprehend` and `generate/meaning_graph/relational.py::comprehend_relational` — **this is the two-grammars reader**: 19 constructions against the writer's 1739, overlap 6, and **fabricates on 22 more** (`every dog is a mammal` → `member(every_dog, mammal)`; `Given: furthermore; p implies q; p.` → `asserted(furthermore)` recited back as a served premise). Those findings are **measured and pinned in PR #138, held for ADR + ratification** — recorded here because REALIZE is where a fabricated reading would become a held belief, *not* re-discovered, *not* fixed.

The architecture note that follows from this placement: REALIZE itself is sound — it faithfully holds whatever the reader hands it, at honest SPECULATIVE standing. The truth defect class is entirely upstream (the reading), which is consistent with the project's fix-upstream doctrine and with holding the fixes for a serving-truth ADR.

## Contract & evidence

- INV-21 (allowlisted writer), INV-22/23 (SPECULATIVE default), INV-29 (only `vault/store.py` transitions status) — pins: `tests/test_architectural_invariants.py`.
- Inline realization behavior — `tests/test_inline_realization.py` ("comprehensible declarative accrues; question determines; off-by-default leaves the turn untouched").
- Predicate-generality — `relational.py:8`: the spine consumes relational comprehension unchanged; `realize_comprehension` is predicate-general (no per-predicate special case in the writer).

## Judgment

**Fitness: `fit`.** Small, typed, provenance-complete, honestly gated. The one structural risk is inherited, not local: the phase will hold whatever it is fed, so its integrity ceiling *is* the reader's fidelity — 19-wide today, fabricating on 22.

**Honest wrinkles:** as with determine-phase, the most life-like capability in the system defaults dark. `realize_quantitative` was not traced to a live caller in this pass (likely lane-side); unverified — Phase 4 should not count it live without a pointer.

**Open questions:** when the #138 fabrication ADR lands, should REALIZE gain a defensive assertion (refuse to hold a reading whose construction is outside the reader's verified inventory)? That would convert reader-inventory truth into a mechanical gate at the holding boundary. (→ Phase 4 / the fabrication ADR)
