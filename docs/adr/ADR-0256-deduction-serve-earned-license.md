# ADR-0256: Deduction Serving Governed by an Earned Reliability License

**Status:** Proposed (deduction-serve arc, Phase 3 — ratify-on-merge)
**Date:** 2026-07-23
**Deciders:** Joshua Shay (ruling authority) + Claude (implementation)
**Companion docs:** [`docs/research/deduction-serve-arc-phase0-baseline-2026-07-23.md`](../research/deduction-serve-arc-phase0-baseline-2026-07-23.md), [`docs/research/deduction-serve-arc-phase1-turn-spine-2026-07-23.md`](../research/deduction-serve-arc-phase1-turn-spine-2026-07-23.md), [`docs/research/deduction-serve-arc-phase2-eval-lane-2026-07-23.md`](../research/deduction-serve-arc-phase2-eval-lane-2026-07-23.md), [`docs/adr/ADR-0175-...`](.) (calibrated learning), [`docs/adr/ADR-0199-...`](.) (cross-domain arena), [`docs/adr/ADR-0206-...`](.) (response-governance bridge)

---

## 1. Context

Phases 1–2 of the deduction-serve arc gave `core chat` the ability to decide propositional-argument questions with the verified ROBDD entailment engine (`generate/proof_chain`, 716/716 wrong=0), behind a bare `deduction_serving_enabled` flag. That flag is a **direct-serve switch**: flip it and CORE speaks authoritatively on every propositional argument, with nothing between the capability and the user but a boolean.

CORE already has the machinery to do better. ADR-0175's reliability gate (`core/reliability_gate/`) and ADR-0199's cross-domain learning arena (`core/learning_arena/`) exist precisely to make a served capability **earned** — measured over sealed practice against independent gold, licensed per capability-class only when a committed track record clears the human-set ceiling (θ_SERVE=0.99). Until now that machinery had exactly one consumer (GSM8K estimation, ADR-0206 Step E) and its own docstring admitted it was "NOT wired into the serving path" for anything else.

The ruling (endorsed by Shay in the arc plan): deduction serving must be **earned-license via the reliability gate**, not a direct-serve flag.

### What the license actually certifies (the non-circular part)

The ROBDD engine is sound **and** complete over the propositional regime — it is never wrong on the problem it is handed. So a license cannot, and does not, certify the engine. The **fallible** component is the reader/projector: `generate/meaning_graph/reader.py` is a template-based comprehension reader that can misparse a natural-language argument and hand the engine the *wrong* problem, which it then soundly decides — a wrong served answer. The reliability license certifies the **full serving pipeline** (reader → projector → engine) per argument shape: it answers "does CORE reliably *read and decide* arguments of this shape at volume?", which is exactly the failure mode the engine's soundness does not cover.

## 2. Decision

Make deduction serving an earned capability gated by a committed, SHA-sealed reliability ledger.

- **Shape-band capability axis** (`generate/proof_chain/shape.py`) — a deterministic, structural classification of an argument into one of five exhaustive bands: the four propositional bands `disjunctive` / `conditional_chain` / `conditional_single` / `atomic` (assigned by `classify_deduction_shape` over the projected `(premises, query)`), plus `categorical` (Band v1b, Phase 4 — assigned directly to any syllogism projected by `to_syllogism`). Computed identically by the practice arena and the serving composer (no drift). Coarse on purpose: each band mixes entailed/refuted/unknown (or valid/invalid) gold, so a band's reliability measures decision correctness across outcomes, not just how many entailments pass through.
- **Band v1b — production categorical decider** (`generate/proof_chain/categorical.py`) — the piece Phase 0's fork identified as missing. Serving cannot import `evals/syllogism/oracle.py` (the sealed independence oracle; INV-25), so this is a fresh production decider that lowers a categorical argument to the propositional regime (one Boolean atom per term-membership *profile*) and rides the already-verified ROBDD engine. Sound AND complete for the modern/Boolean reading; independent of the eval oracle by mechanism (ROBDD over a profile encoding vs. brute-force subset enumeration), verified by case-for-case agreement with it across the syllogism gold lane. Serving projects a syllogism via `to_syllogism` and decides it here (ENTAILED ⇒ valid; UNKNOWN/REFUTED ⇒ invalid; REFUSED ⇒ inconsistent).
- **Deduction practice arena** (`evals/deduction_serve/practice/`) — the **second** concrete instance of the ADR-0199 arena (GSM8K math is the first). A deterministic, synthetic, indexed corpus (`gold.py`, no clock/RNG) of propositional arguments per shape-band, each with **by-construction gold** (the generating template's logical form, independent of the reader — ADR-0199 L-2). `DeductionSolver` runs the exact serving pipeline; `ConstructionGoldTether` scores the committed outcome against the by-construction gold; a misread is caught as `wrong`. Sized to the SERVE volume floor (≥657 committed for a perfect record to clear θ_SERVE=0.99; `CASES_PER_BAND=720`).
- **Construction-time soundness check** (`gold.py::assert_corpus_sound`) — every generated case's by-construction gold is cross-checked against the **independent truth-table oracle** (`evals.deductive_logic.oracle`, INV-25 — shares no code with the ROBDD engine) before the ledger can seal. A mis-stated template gold can never silently inflate the ledger.
- **Sealed, SHA-verified committed ledger** (`chat/data/deduction_serve_ledger.json`, produced by `evals/deduction_serve/practice/runner.py::seal_ledger`) — the per-band `ClassTally`, self-sealed by `content_sha256`. The engine READS it; only the sealed-practice runner WRITES it. Mirrors the estimation ledger topology exactly (`generate/determine/data/estimation_ledger.json`).
- **Serving-side license reader** (`chat/deduction_serve_license.py::deduction_serve_license`) — loads + SHA-verifies the committed ledger and returns the `Action.SERVE` `LicenseDecision` per band under the safe **default** ceilings (θ_SERVE=0.99). A tampered ledger is rejected on load; a band absent from the ledger returns `None` (never licensed). The engine never raises its own ceiling (ADR-0175 invariant #4).
- **Composer gate** (`chat/deduction_surface.py::deduction_grounded_surface`) — after the engine decides an in-band argument, the composer classifies its shape-band and consults the license:
  - **earned SERVE** → the answer is served **authoritatively** (the plain Phase-1 surface).
  - **not earned** (a band absent from the ledger, or any deployment whose ledger is stripped/unverified) → the same sound answer is served **disclosed/hedged** (`"(reasoned, but I haven't yet earned a verified track record on arguments of this shape) …"`), never presented as a verified capability.

  This is what makes deduction serving an *earned* capability rather than a flagged one: strip the committed ledger and CORE still reasons soundly, but stops claiming verified authority it has not demonstrated.

### 2a. ADR-numbering collision note (the "resolve ADR-0206" obligation)

`generate/proof_chain/entail.py` historically carried an "ADR-0206" attribution, and `evals/deductive_logic/report.json` still stamps `"adr": "ADR-0206"`. This is a documented three-way collision (see the `entail.py` module docstring and ADR-0253's collision-handling precedent): committed **ADR-0206** is the response-governance bridge; the entailment operator's real home is **ADR-0218** (Proof-Carrying Coherence Promotion); and deduction *serving* is now **ADR-0256** (this document). This ADR does **not** rewrite `report.json`'s `adr` field — that is a SHA-pinned artifact whose bytes are a separate concern (rewriting it would cascade the pinned lane SHA for no capability change). It records the correct homes so no future reader trusts the stale `ADR-0206` pointer.

## 3. Non-goals

- **Not a new soundness mechanism.** wrong=0 on the propositional regime is owned by the ROBDD engine (ADR-0201/0218), unchanged. This ADR adds an *earned-trust posture* on top, it does not touch the decision procedure.
- **Not autonomous ratification.** The committed ledger is sealed by an explicit, reviewable practice run and committed as data; the engine consumes it read-only. Regenerating it is a deliberate `--seal` operator action, not a runtime write. No autonomous promotion (ADR-0175 invariant #1 discipline preserved: the arena writes only its own artifact; serving reads it).
- **Not a widening past gold.** Unlike ADR-0206 Step E (which discloses an *estimate* past what is grounded), every deduction answer here is a sound entailment verdict; the license governs whether it is stated *authoritatively* vs *disclosed*, never whether an unsound guess is surfaced.
- **Does not change the default flag posture.** `deduction_serving_enabled` remains default-off (ADR-0256 layers the license *inside* the enabled path). Flag-off is byte-identical to pre-arc dispatch.

## 4. Consequences

- Deduction serving is now governed: with the committed ledger (all four bands earned at reliability 0.99087, wrong=0), in-band arguments serve authoritatively — Phase-1 behavior preserved byte-for-byte. Without an earned ledger, the same reasoning is served honestly disclosed.
- The ADR-0175/0199 reliability substrate gains its **second** real consumer and its **first** non-estimation serving consumer — a concrete step against the standing "designed, not wired" critique of that zone.
- The `deduction_serving_enabled` flag stops being a direct-serve switch and becomes an enable for an *earned* path; authority now rests on committed, tamper-evident evidence, not a boolean.

## 5. Validation

- **Arena / ledger (`tests/test_deduction_serve_license.py`):** corpus soundness vs the independent oracle; every band earns SERVE at reliability ≥ 0.99 with wrong=0; committed-ledger `content_sha256` verifies on load; a tampered ledger is rejected; `deduction_serve_license` returns `None` for an unknown band.
- **Composer gate (same file):** an earned band serves authoritatively (no hedge, Phase-1 surface preserved); an injected empty ledger forces the disclosed hedge on the SAME sound answer — proving the gate genuinely governs posture.
- **Regression:** Phase-1 (`test_deduction_surface.py`) and Phase-2 (`test_deduction_serve_lane.py`) suites stay green; smoke + cognition green (see PR `[Verification]`).
