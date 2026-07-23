# ADR-0257 — English-clause argument band (Band v2-EN): opaque-atom propositional serving

- **Status:** Proposed
- **Date:** 2026-07-23
- **Relates to:** ADR-0256 (deduction-serve earned license), ADR-0201 (ROBDD
  keystone), ADR-0218 (proof-carrying substrate), ADR-0175/0199 (calibrated
  learning / arena), ADR-0253 (dual-pack serve boundary — grc/he)

## 1. Context

ADR-0256 shipped the first end-to-end reasoning workflow: `core chat` decides
propositional and categorical arguments, flag-gated, behind an earned per-band
SERVE license. Its two documented boundary cases were natural-English inputs:

- `"If it rains then the ground is wet. It rains. Therefore the ground is wet."`
  → declined (`reserved_word_in_np`);
- `"If p then q. Therefore if not q then not p."` (contraposition)
  → declined (nested negation).

Both declines came from the SHARED comprehension reader
(`generate/meaning_graph/reader.py`), whose single-token atom floor and
reserved-word guard are load-bearing for seven other lanes' wrong=0. The
deductive engine itself (`generate/proof_chain/entail.py`) never was the
limit: it is sound+complete over arbitrary propositional structure with
opaque atoms. The gap was purely a *reading* band.

## 2. Decision

Add a dedicated **English-clause argument reader**
(`generate/proof_chain/english.py`) used ONLY by the deduction serving path,
as a fallback tier after Band v1 (propositional) and v1b (categorical):

- Whole English clauses become **opaque atoms**: one minted id (`a0`, `a1`, …)
  per distinct normalized clause; identity is normalized exact text. Clause
  *content* is never interpreted — only quoted back in the surface.
- Structure is recognized by a **closed function-word grammar**:
  `if <A> then <B>` (junctions allowed on both sides), `[either] <A> or <B>`
  (n-ary), top-level `and` (premise splits / conjunctive conclusions), and
  three negation forms — leading `not`, sentential `it is not the case that`,
  and copular `<L> is|are|was|were not <R>` (normalized to `~atom(<L> is <R>)`,
  contractions `isn't`/`aren't`/… expanded).
- The same verified ROBDD engine decides; deterministic templates render the
  verdict over the user's own clause text
  (`generate/proof_chain/render.py::render_entailment_english`).
- Four new shape-bands — `en_conditional_single`, `en_conditional_chain`,
  `en_disjunctive`, `en_atomic` — each **earning its own SERVE license**
  through the ADR-0199 arena at n=720/band, wrong=0 (sealed into the same
  ratified ledger; unlicensed ⇒ automatically hedged, per ADR-0256).

The shared reader is untouched. The composer tries v1/v1b first, so every
previously-served argument is served byte-identically; this band only widens.

## 3. Why the opaque reading is sound (the load-bearing argument)

Propositional entailment is **closed under uniform substitution** of formulas
for atoms. Therefore, for verdicts computed over opaque clause-atoms:

- **ENTAILED**, **REFUTED**, and **inconsistent-premises** verdicts remain
  true under ANY deeper reading of the clauses — refine a clause into internal
  structure, or identify two clauses we kept distinct, and the verdict stands.
  These are served at full strength.
- **UNKNOWN** ("doesn't settle") is the ONE verdict that is *not*
  substitution-safe: internal clause structure this band did not read could
  settle the argument. Two mitigations, both mandatory:
  1. **Scoped phrasing** — the UNKNOWN surface states its reading explicitly:
     *"Reading each clause as one indivisible claim, your premises don't
     settle whether …"*. True of the reading, disclosed as such.
  2. **Structural guards** — clauses whose surface form ANNOUNCES structure
     this band cannot read refuse out of the band entirely (typed):
     quantifier-led categorical clauses (`all/no/some/every/…` — a valid
     syllogism must never flatten into a misleading "doesn't follow"),
     `is a|an` membership clauses (reserved for a future `member_chain`
     band), and unnormalizable negation (`never`, `cannot`, `doesn't`, … —
     a negation must never hide inside an opaque atom).

Genuinely ambiguous English (mixed top-level `and`+`or`, nested conditionals)
refuses rather than guessing a scope. Honesty caps (16 premises, 24 atoms)
refuse rather than truncate.

## 4. What the earned licenses certify

Per ADR-0256, a band's license certifies READER fidelity per shape — hence the
`en_` namespace: same engine, different reader, so the English reader earns its
own record. The arena corpus is synthetic copular clauses ON PURPOSE (the
reader is content-blind; the license certifies structural fidelity); the eval
lane (`evals/deduction_serve/v2_en/`, 26 hand-authored REAL-English cases,
content disjoint from the synthetic lexicon) keeps that claim honest against
natural prose — the synthetic-corpus-overfit lesson applied in design.

Corpus gold is authored **by construction** and cross-checked against the
independent truth-table oracle with NO reader in the loop (the template's
intended logical form is checked directly) — stronger independence than the
v1 path, INV-25 preserved.

## 5. Tri-language extension contract (grc / he)

CORE's three foundational languages are a capability asset precisely where
English is structurally weak, and this band is built to receive them:

- **What is language-neutral** (reused as-is): the opaque-atom table, the
  substitution-soundness argument (§3), the caps, the refusal discipline, the
  license machinery, the engine. None of it knows English.
- **What is language-specific** (the thin layer a sibling band replaces): the
  structural lexicon (`if/then/or/and/not/either/therefore`, copulas,
  contractions, quantifier leads) and the clause-order conventions.
- **Honest wrinkle, recorded so we don't build a hollow abstraction:** a pure
  lexicon swap does NOT read real Greek — ἄρα is postpositive (second
  position), and case-driven word order changes clause segmentation. A `grc_*`
  / `he_*` band is a sibling reader module + its own earned licenses, entering
  through pack ratification (ADR-0253: draft he/grc trees are not serve
  imports). No premature parameterization is introduced now.
- **The trigger** (per the ratified pack-expansion doctrine): when en-band
  refusal telemetry shifts from *mechanism* (`ambiguous_and_or` — English
  genuinely ambiguous) to *coverage*, that is the evidence that the
  morphologically explicit languages pay — they read cleanly exactly where
  English refuses.

## 6. Scope-outs (deliberate)

1. **`member_chain` band** (membership + quantified premises — "Socrates is a
   man. All men are mortal. Therefore Socrates is mortal."): guarded out
   (`membership_shape_out_of_band`), reserved as the next band; needs a
   per-individual propositional lowering (same pattern as
   `generate/proof_chain/categorical.py`).
2. **Verb-phrase negation de-conjugation** ("doesn't start" → "starts"):
   refuses today (`internal_negation_unread`); English morphology work, or the
   tri-language path (§5).
3. **Proof-step recap** in the surface: unchanged from ADR-0256 scope-out.
4. **Flag posture unchanged:** the band rides `deduction_serving_enabled`
   (default off); no new flag.

## 7. Verification

- `uv run core test --suite deductive -q` — 83 passed (reader contract,
  surfaces, license, both lane splits, e2e through `ChatRuntime`).
- Practice arena: 9 bands × 720 = 6,480 cases, wrong=0, every band
  reliability 0.99087 ≥ θ_SERVE=0.99 → SERVE licensed; ledger re-sealed
  (`chat/data/deduction_serve_ledger.json`, self-verifying `content_sha256`).
- Eval lane: v1 28/28 (the two former boundary declines now decided —
  entailed), v2_en 26/26, wrong=0; report re-pinned
  (`scripts/verify_lane_shas.py::deduction_serve_v1`).
