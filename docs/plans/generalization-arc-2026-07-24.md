# Generalization Arc — GSM8K-Level Capability Across Core Subjects

**Date:** 2026-07-24 · **Status:** ACTIVE · **Base:** main @ `5224b5e0` (post ADR-0259 / Band v4-CM)

This is the ratified plan of record for the arc that takes CORE from "one
fully-closed cognitive lifecycle (deduction-serve)" to "the same lifecycle
running across core subjects at GSM8K-exam level" — articulated answers,
problem solving, comprehension, all under wrong=0 discipline.

Execution is **risk-tiered across three operators** (§6): Fable 5 does the
high-risk design + build, Opus 5 the medium tier, Sonnet 5 the low tier.
Handoff briefs live in `docs/handoff/generalization-2026-07/`.

---

## 1. Ground truth at arc start

- Exactly one lifecycle is closed end-to-end: **deduction-serve**
  (comprehend → 5 band readers → ROBDD decide → sealed practice arena,
  17 bands × 720, θ_SERVE=0.99 → SHA-verified ratified ledger → license
  gate → render → register chain). Dark behind
  `deduction_serving_enabled=False`, awaiting ratification.
- Cross-subject substrate exists but is idle: 16 unmounted domain seed
  packs, 5 domain chain corpora, 6 OOD fluency lanes, five-layer
  teaching-order doctrine (`docs/teaching_order.md`), capability index.
- Learning-loop organs exist but are write-only or dark: 19 default-off
  flags; proposal/contemplation/promotion paths emit into review sinks
  with no runtime consumer. Three real ratified-artifact consumers exist
  (deduction ledger, estimation license, recognizer registry) — the
  pattern to generalize.
- Math is reader-gated, not solver-gated: compiler holds 50/50 wrong=0 on
  dev-1 but the reader parses ~1% of real GSM8K; the ~30-band bet was
  falsified; standing ruling #77 selects **seeding-sentence injection**
  as the next math move.
- ADR-0246 §3.7 identity calibration is explicitly OFF this critical
  path (blocked on §11 research evidence; doctrine order:
  capability → practice → calibration → serve).

## 2. Phases

### Phase 0 — Truth-substrate hygiene + first live serve *(Small)*
- **0.1** Root-cause the 3-lane pin drift (`miner_loop_closure`,
  `curriculum_loop_closure`, `demo_composition`). Classify: determinism
  bug (stop-the-line) vs stale pins vs local/CI byte divergence.
  Re-pin surgically only after root-cause. Findings doc in
  `docs/research/`.
- **0.2** Ratification packet for `deduction_serving_enabled` (evidence
  collation only; the flip is Shay's decision).

**Done when:** drift explained + resolved; packet delivered.

### Phase 1 — Reading generalization: verb predicates + existentials *(Large)*
The band cascade reads only copula sentences; every other subject states
facts as verb sentences. Ordered by leverage:

- **1.1 Band v5-VP — verb predicates**: predicate atoms keyed by
  (verb lemma, argument tuple); intransitive + transitive with
  named/classed arguments ONLY; closed morphology; typed refusal for
  everything else (voice, tense shifts, ditransitives, PP-arguments).
  This band gates Phase 2.
- **1.2 Band v6-EX — existential (`some`) witnesses**: completes the
  all/no/some square; witness-based lowering.
- Deferred (unchanged from ADR-0259 §5): universal-nested-in-connective
  (bound-variable tracking), identity/co-reference, tense.

Recipe per band (proven 3×): reader module → shape bands → arena
templates (≥720/band) → hand-authored lane split (content-disjoint from
practice lexicon) → ledger reseal → tests → ADR → research doc.

**Done when:** verb-predicate and existential arguments decided at SERVE
wrong=0; ledger resealed; promotion sweep of previously-declined cases
done honestly (promotion = *decided correctly*, not *decided favorably*).

### Phase 2 — Port the lifecycle to two non-math subjects *(Medium-Large)*
Physics and biology first (OOD lanes, seed packs, and domain chains
already exist). Implemented strictly to the **curriculum-entailment gold
contract** (§4 — the load-bearing design of this arc):

- Mount subject packs; wire domain chains through the teaching corridor
  per the five-layer order.
- Exam-shaped serve lanes: question → read (v5-VP reading) → decide
  **from ratified curriculum premises only** → licensed articulated
  answer.
- Per-subject band ledgers via the same arena; capability-index
  coverage entries; 3-domain anti-overfit panel discipline
  (independence must be in the READING).

**Done when:** two subjects serve wrong=0 on hand-authored exam-shaped
lanes with earned licenses, zero subject-specific engine code.

### Phase 3 — Close the discovery→learning loop *(Medium)*
- **3.1** Vocab-expansion trigger as code (the COMPREHENSION-READER-AUDIT
  §measurable-test, made a standing instrument: refusal histogram split
  mechanism-vs-coverage; admissions-per-lexicon-batch).
- **3.2** HITL proposal-queue surface (review CLI over the existing
  sinks).
- **3.3** Generic consumption bridge: extract the seal → ratify →
  SHA-verified license → serve-gate pattern (deduction ledger is the
  model; estimation license the second instance) into the ADR-0175
  Phase-5 bridge so each subject arena plugs in without bespoke wiring.
- **3.4** Feed discovery-yield with real traffic (post 0.2 flip).

**Done when:** a serve-time gap flows discovery → proposal →
ratification → runtime consumption with no manual file surgery.

### Phase 4 — Math problem-solving reader *(Medium-Large, parallel lane)*
Independent of Phases 1–3 (no shared files; production-line pattern):

- **4.1** Seeding-sentence injection (ruling #77; the 75% "no injection"
  wall).
- **4.2** Compare unblock (summation-question reader + inverse compare),
  queued behind 4.1 per the same ruling.
- **4.3** q:complex decomposition study (increment-1 band plan §9; 101
  cases behind one label).
- Guardrails pinned: `docs/research/reader-arc-overfit-inventory-2026-07-19.md`,
  ADR-0251 recalibration (no bespoke-per-case regex growth),
  ADR-0252.

**Done when:** real-GSM8K parse floor materially above ~1% with wrong=0
held on the full 500; ceiling revised with evidence.

### Phase 5 — Articulation depth (`generate/` "core_logos") *(trigger-gated)*
Not queued by order. Trigger: Phases 1–2 produce multi-step decided
content (proof chains, multi-fact answers) — the evidence of where
articulation quality binds that the intelligence-loop plan's Phase 6
deferral was waiting for. Scope the arc from that evidence.

## 3. Dependencies

- Phase 1.1 gates Phase 2. Phase 0 first.
- Phase 3.3 lands before the *second* subject arena (avoid copy-paste
  wiring). 3.1/3.2 interleave freely.
- Phase 4 fully parallel. Phase 5 trigger-gated on 1–2.
- §3.7 identity calibration stays downstream of the whole arc (its
  calibration data comes *from* this arc's practice volume).

## 4. Curriculum-entailment gold contract (Phase-2 design, decided here)

This section is the HIGH-risk design, fixed now so the medium tier can
implement without re-litigating epistemology.

1. **Verdict domain** — every exam item resolves to
   {entailed, refuted, unknown, declined}, identical to deduction-serve.
   UNKNOWN is the honest verdict for untaught facts. No open-world
   recall, ever.
2. **Two question shapes** — (a) self-contained arguments (premises in
   the text): already owned by bands v2–v6; (b) **curriculum-grounded
   questions** (the new Phase-2 shape): question text supplies only the
   query; the premise set is compiled from the RATIFIED domain chain
   corpus for that subject. Gold is a function of (curriculum, question)
   — never of case-local hidden text. This is the decoding-not-generating
   line in mechanical form.
3. **Premise provenance** — each lane case pins the chain IDs it draws
   on; the runner reconstructs premises from the ratified corpus and
   MUST fail the case if a pinned chain is absent or unratified.
4. **Independent oracle** — per subject, a closed-world reachability
   oracle over the chain corpus (sharing no code with the serving path)
   validates every gold verdict; the lane asserts corpus soundness
   before any case runs (the `assert_corpus_sound()` pattern — since #119 split
   into `assert_practice_gold_sound` / `assert_lane_cases_sound`).
5. **License granularity** — bands keyed by (subject × relation family ×
   chain depth), earned in the ADR-0199 arena: θ_SERVE=0.99, n≥720,
   wrong=0, sealed + SHA-verified ledger per subject.
6. **Typed refusals, lifecycle-mapped** — `untaught_vocabulary`,
   `unratified_chain`, `out_of_curriculum`, `ambiguous_reading`; the
   OOV refusal feeds the Phase-3 proposal queue (refusals become
   discovery, not dead ends).
7. **Anti-recall probes (mandatory per lane)** — cases whose answer is
   true in the world but absent from the curriculum; gold = UNKNOWN.
   A lane without these probes cannot prove the system decodes rather
   than recalls, and MUST NOT ship.

## 5. Risks

- **HIGH — subject-gold epistemology drift**: mitigated by §4 (contract
  fixed before implementation; anti-recall probes mandatory).
- **HIGH — v5-VP scope creep**: argument structure/voice/agreement are a
  real jump from copula. Mitigation: two argument shapes only, closed
  morphology, typed refusal for the rest — the same discipline that made
  v2–v4 land clean.
- **MEDIUM — arena scale**: 720/band × growing band count on local
  hardware; linear sealing time; watch, don't block.
- **MEDIUM — synthetic-overfit trap**: practice templates and lane cases
  stay content-disjoint per subject (standing doctrine).
- **MEDIUM — q:complex may not decompose**: nothing gates on Phase 4.
- **LOW — drift root-cause escalates**: if Phase 0.1 finds a determinism
  bug, the arc pauses until it is fixed (stop-the-line).

## 6. Risk-tiered operator assignment

Constraint set for every tier: wrong=0; flags stay default-off (flips
are Shay's ratification only); Forgejo-primary, no GitHub/`gh`; local
smoke + warmed_session gate before every push (pre-push hook); `uv`
always; branch + worktree per unit; no merge automation; one PR per
coherent solution; attribution disabled.

### Tier F — Fable 5 (HIGH risk; this session)
- F1: Phase 0.1 drift root-cause (+ surgical re-pin if benign).
- F2: this plan doc + handoff briefs.
- F3: §4 gold contract (done — it is this document).
- F4: Band v5-VP (Phase 1.1), full recipe, PR.

**Checkpoint F→O:** F1/F2/F4 PRs pushed with compare URLs; memory
updated; briefs current. Opus starts at O1 with no open design
questions.

### Tier O — Opus 5 (MEDIUM risk)
- O1: Band v6-EX existentials (Phase 1.2) — recipe + ADR-0257/0258/0259
  as references.
- O2: Phase 2 physics + biology serve lanes per §4 (mount packs, wire
  chains, arena, ledgers, lanes). Physics first; biology second only
  after the generic bridge (O3) lands.
- O3: Phase 3.3 generic consumption bridge.
- O4: Phase 4.1 seeding-sentence injection, then 4.2; 4.3 as analysis.
  Guardrail docs pinned in §2/Phase 4.

**Checkpoint O→S:** v6-EX merged; ≥1 subject lane serving wrong=0 with
earned licenses; bridge merged; math increment measured + documented
(whatever its outcome — a null result is a valid checkpoint).

### Tier S — Sonnet 5 (LOW risk)
- S1: Phase 0.2 ratification packet (evidence collation).
- S2: Post-fix lane re-pins; public_demo flake documentation.
- S3: Phase 3.1 vocab-trigger instrument (spec is pinned in
  `docs/handoffs/COMPREHENSION-READER-AUDIT.md` §measurable-test).
- S4: Phase 3.2 HITL proposal-queue CLI surface.
- S5: Promotion sweeps, capability-index entries, docs/memory
  housekeeping.

**Arc close:** all three tiers merged; Phase 5 trigger evaluated with
evidence in hand; next arc scoped from it.

## 7. Non-goals (this arc)

- ADR-0246 §3.7 / identity-gate calibration (evidence-blocked).
- `core/ports/` Ring-2/3 consumption (own future flag-gated units).
- Universal-nested-in-connective, co-reference, tense bands.
- Any serving-flag flip without explicit ratification.
- Zig substrate work.
