# attention-allocation — the live CR-1 mechanism

**Kind:** component (mechanism spanning `generate/salience.py`, `generate/attention.py`, `core/physics/{salience,attention,inhibition}.py`, `generate/stream.py`) · **Parent:** unowned (CR-1) — de facto M3 · **Assessor:** Fable 5 (Phase 3)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-serving` (default ON) · **Fitness:** `strained` — sound mechanism, absent governance · **Topology role:** runtime boundary

> The mechanism that decides what CORE is allowed to consider at each generation step. It gates every token walk, owns the measured hot path (~73% of turn time through `cga_inner`), and is the only default-ON serving mechanism in the tree with no owning ADR, no zone, and no stage in any ratified articulation. This card gives it the identity it has been operating without.

## What it is / What it does (372 lines total, all read)

**`generate/salience.py` (62)** — `SalienceOperator.compute(field, vocab, top_k=16) → SalienceMap{indices, scores, budget}`. The docstring states the lineage plainly: "generation-facing salience from **ADR-0008 field curvature**… the score is now a local curvature magnitude from `core.physics.salience` rather than normalized proximity to the query field." So the mind-physics blueprint's Allocation Physics **did land**, mutated: the physics curvature kernel (`core/physics/salience.py`, 139 lines) is *composed* — imported as `CurvatureSalienceOperator` — by a thin generation-facing adapter. Not a duplicate (Phase 2's correction, confirmed by read).

**`generate/attention.py` (43)** — `AttentionOperator(inhibition_threshold).plan(salience, vocab) → allowed_indices`. Inhibition is a **scalar threshold** (default 0.3), not the blueprint's mask.

**Wiring (`generate/stream.py:255–331`)** — `_attention_candidates` runs salience→attention when `use_salience` (default **True**); the walk intersects `language_candidates ∩ salience_candidates` (`:329`), and when language candidates are absent, salience candidates alone gate the step (`:331`). At `:637` the salience `budget` is fed back as the next `salience_top_k` — attention narrows itself as the walk proceeds.

**The decoration:** `core/physics/inhibition.py` (54 lines, `InhibitionOperator`/`InhibitionMask`) is imported only by `core/physics/__init__.py` and one parity test. No serving or eval path constructs a mask. By the sabotage test: **decoration** — the blueprint's third operator exists as an exported symbol and nothing more.

## Contract & evidence

- Live and load-bearing — code-read + config — `use_salience=True` default (`core/config.py:35`); deleting `_attention_candidates` would change every walk's candidate set — would-fail-if-absent: **yes**.
- Deterministic — pure functions of field state and vocab; parity-pinned (`tests/test_salience_vectorize_parity.py` pins the vectorized rewrite against the original nested loop).
- Behavioral pin — `tests/test_salience.py` exercises compute+plan; suite membership not individually confirmed (flagged, like most non-lane pins in this assessment).
- Interaction contract with admissibility: salience/attention prune *candidates*; admissibility (threshold/margin/rotor, ADR-0024/0025/0026) then judges them. Two allocation stages, only the second governed by ADRs.

## Judgment

**Fitness: `strained` — the gap is governance, and it is now fully characterized.** Mechanism: sound, deterministic, composed cleanly over the physics kernel. Governance: ADR-0008 is a *draft blueprint's* operator spec, never ratified as owning this serving behavior; no ratified articulation names an attention stage; the config knobs (`salience_top_k=16`, `inhibition_threshold=0.3`) are tuned constants with no recorded derivation — precisely the "threshold tuned for good-enough" the mastery framework's Pillar I forbids, sitting at the semantic center of generation.

**Honest wrinkles:**
- The budget feedback loop (`:637`) means attention is *self-narrowing* across a walk — a real cognitive-model property (fatiguing focus? commitment?) that no document names, let alone justifies.
- The hot-path cost (~73% of turn time) is this mechanism's nearest-neighbour/salience search — so CORE's compute profile is dominated by a mechanism whose parameters no decision governs.
- CR-1's ruling question is now precise: not "is attention a layer" in the abstract, but **who owns `use_salience`, the two constants, the budget feedback, and the InhibitionMask disposition** (ratify the mask's deletion, or build it). A one-page ADR closes all four.

**Open questions:** the CR-1 ADR (→ ruling); derive or empirically justify `top_k=16` / `threshold=0.3` (→ Phase 4); delete or build `InhibitionMask` (→ ruling; deletion is the mastery-framework default).
