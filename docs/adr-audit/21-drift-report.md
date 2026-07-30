# Phase 4 — Drift Report

Every unreconciled contradiction found in Batch 1's Continuity axis: ADR-vs-code, ADR-vs-ADR, ADR-vs-Whitepaper/axiom, and record-vs-reality divergence in governing non-ADR documents (`docs/assessment/`). Full finding text: `20-finding-register.md`. **Verified against:** `main` @ `cbfc8ccb`.

## 1. The FA-1 cascade — the headline result of Batch 1

FA-1 (`docs/plans/2026-07-28-foundations-audit.md`) ruled ADR-0005/ADR-0015's cross-language holonomy-closure claim `DEFECTIVE` on 2026-07-28. Stack A3's charter-mandated job was to walk the citation graph and find every other ADR that inherits this now-retired claim. It found **19 dependent ADRs** (`AA-64`…`AA-82`) plus **2 non-ADR governing records** citing the same retired claim, none of which carry any note of the retirement:

| ADR | Dependency type | Severity |
|---|---|---|
| ADR-0180 | premise — Holonomy Resonance asserted as "the supreme architectural invariant of `core`" in cross-modal form; justifies the CRDT sharding design's mechanical cost | 🔴 |
| ADR-0240 | implementation — Biography Holonomy Blade's "reconstructible via `holonomy_encode`" rests on a deleted closure; `biography.py:94` steers an inert `alpha` | 🔴 |
| ADR-0073 + ADR-0073a | mechanism — cross-language binding via shared `semantic_domains` atoms **is** the dominant collapse site (34 of 37 lost coordinates); the prescribed remedy is unreachable by construction | 🔴 |
| ADR-0102 + ADR-0103 | ratification/fitness — a live `reasoning-capable` ledger license rests on four packs whose alignment is destructive on one half, zero-resolving on the other | 🔴 |
| ADR-0013, ADR-0181, ADR-0197 | premise / inherited premise — the Logos-recovery boundary's "nothing to fuse" conclusion rests on the AUC-0.557 claim | 🟡 |
| ADR-0243, ADR-0241, ADR-0239 | implementation / downstream — "non-lossy reconstruction," "topologically protected wisdom," and the biography-holonomy acceptance chain | 🟡 |
| ADR-0007, ADR-0006 | interface — both name `readback_rules.py` and the `el` pack id directly; neither exists / is superseded | 🟡 |
| ADR-0253 | boundary freeze — correct ruling, frozen around a now-known-destructive compiler; also custodian of the ADR-0261 reservation | 🟡 |
| ADR-0027, ADR-0030 | analogy / deferred option | 🟢 |
| ADR-0244 + ADR-0246 | boundary assertion — quarantine is correct but assumes a well-defined quarantined object | 🟢 |
| ADR-0261 (reserved, unallocated) | reserved intent — must not be allocated without a NO-GO annotation, or a Rust/SIMD kernel would harden the retired mechanism | 🔵 |
| `SESSION-2026-05-12-language-packs-addendum.md`, `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` | companion / mapping — restate the retired claim; need an annotation | 🟢 |

**Recommended action (for ruling, not executed here):** every 🔴/🟡 row above needs its own re-verdict pass — this audit found *that* they depend on the retired claim, not what each dependent ADR's status should become once corrected. That re-verdict work is a natural Batch-2+ carry-forward item regardless of which numeric batch each ADR falls in (several — 0073, 0102, 0103, 0180, 0240 — are in later batches; flag them now so Batch 3/5's stack taxonomy routes them to Tier A on arrival rather than rediscovering the dependency cold).

**Independent corroboration, found by a different stack auditing a different ADR family:** stack A1 (Algebra & Geometry Foundations) measured — from the algebra layer, with no knowledge of A3's work — that `VocabManifold.nearest()` is a near-constant function (300/300 random queries collapse to one word) and independently reproduced FA-1's exact 53-coordinate-collision count via its own coordinate-frame analysis (`AA-1`). A3's arc-level finding `AA-84` ties the two together explicitly: *"the L2 semantic-ground layer built two narrower, worse versions of L0 operators that already shipped — alignment vs. `rotor_power`/`word_transition_rotor`, and 'holonomy' vs. `geometric_product` — and imported neither."* Two independently-dispatched audits, working from opposite ends of the stack (raw algebra vs. semantic-ground claims), converged on the same root cause. This is the strongest single piece of evidence Batch 1 produced.

**Process finding (`AA-85`):** the correction was available all along. `docs/handoffs/ADR-0167-FOLLOWUPS.md` §6 pre-registered FA-1's exact finding, with acceptance criteria, months before FA-1 ran — but `packs/compiler.py:598` cites `docs/handoff/` (singular; a directory that also exists, with different, unrelated content), so the citation silently resolved to the wrong place and a ratified analysis doc concluded the pre-registration didn't exist. **Recommend:** a link-checker over code-comment doc citations, and adding `docs/handoffs/` explicitly to the audit charter's evidence-source order (§4 of `00-scope-and-method.md`) — done, see that file. Also: `packs/schema.py:181`'s `HolonomyAlignmentCase` docstring still asserts the retired Crown Proof verbatim in live code at HEAD (`AA-57`, from A3's ADR-0015 findings) — a direct instance of `AGENTS.md` philosophy #5 ("when a record and reality diverge, that is a defect with the same severity as a wrong answer").

## 2. ADR-vs-ADR contradictions (outside the FA-1 cascade)

- **`AA-13`** — ADR-0003 §Consequences ("no component outside `algebra/` needs to know about rotor composition") is directly contradicted by its own child ADR-0004 §Consequences and by five production modules that do exactly that. Neither ADR reconciles the conflict; the child (built later, and correct) silently overrides the parent with no supersession note.
- **`AA-32`** — ADR-0009 (Compositional Physics) still reads `Status: Accepted` with no supersession marker, despite being substantively superseded by the proposition-graph lineage that actually shipped. A reader working only from `docs/adr/` would implement the wrong pipeline.
- **`AA-37`** — Reversed-by-drift: what shipped (`generate/realizer.py` + `realizer_guard.py` + energy modulation + register surface) moves architecturally *toward* the `core_logos` subsystem shape that ADR-0011 explicitly rejected. The bet was reversed in practice; no record reverses it on paper.
- **`AA-38`** — The shipping renderer (`generate/realizer.py`, ~20 consumers) has no owning ADR at all, and the one ADR that claims its territory (ADR-0011) contradicts what it does. Same governance class as the existing gap-register's `G-14`/`CR-1` pattern — cited, not duplicated.
- **`AA-88`, `AA-93`, `AA-96`, `AA-97`, `AA-98`** (stack A4, per its own rollup note) — document-vs-reality drift across the admissibility chain: `RatificationOutcome.PASSTHROUGH` still specified in two ADRs after being excised by INV-34 (`AA-88`); a duplicated, inconsistent "Code impact" section within ADR-0022 itself (`AA-96`); `.json`-vs-`.jsonl` path rot in the load-bearing eval lane (`AA-97`); "deferred to a future ADR" wiring that landed without the amendment ever being written (`AA-98`); ADR-0026 and ADR-0024 each claim to gate production admissibility while neither actually gates anything, since `inner_loop_admissibility=False` in every reachable configuration (`AA-93`).
- **`AA-114`** — ADR-0032 and ADR-0034 both state "the turn loop does not auto-invoke [this check]"; ADR-0035 wired both in, and both now run on every turn via both runtime paths. Neither carries a supersession banner. The register's own `H-8` pattern, recurring on two safety-relevant documents.
- **`AA-19`, `AA-20`** — **the existing assessment's own governing taxonomy is itself stale in two places.** `docs/assessment/02-layer-taxonomy.md` §1.1 records `DriveGradientMap`/`ExertionMeter` as "never built" and CR-1 records `InhibitionMask` as "appears never to have been built" — both are built and reachable on the live turn path. The assessment's own later registers (`H-2`/`G-4`) already corrected this, but §1.1 itself was never amended, so one ratified document contradicts another ratified document from the same audit arc. Recorded here rather than silently fixed, per this audit's own non-goal of not editing other teams' artifacts — flagged for whoever owns `docs/assessment/` next.

## 3. ADR-vs-code contradictions (build fidelity, selected — full list in the finding register)

- **`AA-2`** (charter-level) — the vocabulary stores unit versors, never null CGA points, directly contradicting ADR-0001 §Consequences ("guaranteed to be a valid CGA point"), Whitepaper Invariant II, and Whitepaper Invariant III simultaneously. A genuine null-point embedding would be *rejected* by the code that supposedly guarantees it.
- **`AA-41`, `AA-42`** — ADR-0005's eight-gate activation sequence is one boolean, true on all four logos packs; `_blend_feature_versors` still returns the target verbatim (the exact defect FA-1's evidence chain names, ratified as `G-25`).
- **`AA-51`, `AA-52`** — `holonomy_encode`'s docstring describes a reverse walk and closure the code does not compute (unrepaired since commit `fca6216e`); the retired Crown Proof claim is still asserted verbatim in a live docstring at HEAD.
- **`AA-102`** — the admissibility stack's central doctrinal claim ("silent relaxation is the exact failure mode this ADR exists to eliminate") is violated by the code path that actually runs and honored only by the code path that never runs, in the same function, eight lines apart (`generate/stream.py:327-357`).
- **`AA-107`** (A5) — requesting an unratified domain ethics pack silently downgrades to the zero-refusal default with no log, warning, or telemetry — inside the exact layer whose own `no_silent_correction` boundary reports itself as continuously upheld.
- **`AA-121`** (B1) — ADR-0013's own status table, and the existing M2 assessment layer card, both *understate* what's built for vision/audio (`ProjectionHead`s exist, gate-closed) — drift in the conservative direction, still drift.
- **`AA-148`** (B5) — ADR-0040's documented wire-format field table is stale against the running serializer; `schema_version` was raised as an open question in two separate ADRs and closed in neither.

## 4. Pattern across all of Batch 1

`AA-83` (A3, arc-level) names the pattern most precisely: **every forward operator this batch found was built, and its conjugate was not** — `readback_rules.py` (semantic-ground gate 5), the reverse walk in `holonomy_encode` (L2 closure), and (per A5) `SafetyCheck`/`EthicsCheck`'s enforcement half sitting off the pre-push gate while their loader half is fully enforced. This is Axiom 4 (Dual-Correction) failing in the same shape at three different layers, independently discovered by three different stacks. Recommend this pattern — not any single instance of it — as the top candidate for a cross-batch synthesis finding once Batches 2–6 land, since three-for-three on the first batch alone suggests it is systemic rather than local.

## 5. Batch 2 & Batch 3 Drift Summary

- **`AA-219` / `AA-220`** (Batch 2) — ADR-0093 promotion path invariant unimplemented (`evaluate_domain_contract` has zero production callers); ADR-0113 claim ("audit-passed gate verifies all 9 ADR-0091 predicates pass") is false in code.
- **`AA-231` / `AA-233`** (Batch 2) — Capability reporting reads newest stored file (unsaved failing runs cannot demote ratified rows); `reasoning_capable` predicate consults no eval result.
- **`AA-250`** (Batch 2) — Sealed `fabrication_control` holdout leaked in plaintext in `results/v1_holdout.json`.
- **`AA-308` / `AA-310`** (Batch 2) — Reviewer registry not wired into proposal review pipeline; replay-equivalence pre-gate is no-op (`NoOpReplayChecker` always passes).
- **`AA-332` / `AA-345`** (Batch 3) — `hebrew_greek_textual_reasoning` (ADR-0102) and `systems_software` (ADR-0101) ratifications inherit the defective cross-language holonomy claim (`AA-75`).
- **`AA-334`** (Batch 3) — Internal Python identifiers (`expert_demo.py`, `evaluate_expert_demo`) intentionally left un-renamed by ADR-0113, causing minor internal vocabulary drift vs user-facing `audit-passed`.
- **`AA-336` / `AA-338` / `AA-340`** (Batch 3) — ADR headers (ADR-0114, ADR-0119, ADR-0131) remain `Status: Proposed` in document bodies while downstream code, composite gates, and auditors are fully implemented and tested.
- **`AA-342`** (Batch 3) — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies.
- **`AA-348`–`AA-351`** (Batch 3) — Versor arithmetic and inverse translation spikes (ADR-0138, ADR-0139, ADR-0140~2, ADR-0141) remain unbuilt draft design documents.
- **`AA-361` / `AA-362`** (Batch 4) — ADR-0180 Delta-CRDT sharded substrate, Audio compiler (ADR-0181), and Vision compiler (ADR-0197) inherit the retired Holonomy Resonance premise (`AA-64`, `AA-66`, `AA-67`).
- **`AA-373`** (Batch 4) — Motor Efferent Decoder Spike (ADR-0198) implemented fail-closed efferent gate while physical motor decoding remains deferred to ADR-0216.
- **`AA-395`** (Batch 5) — Biography Holonomy Blade (ADR-0240) rests on deleted `holonomy_encode` closure (`AA-68`, FA-1 cascade carry-forward).
- **`AA-429`** (Batch 6) — Existential witness band v6-EX (ADR-0261) reserved slot requires explicit NO-GO annotation until witness resolution is built.





---

# Batches 3–6 additions (2026-07-29 redo, `AA-439`–`AA-514`)

Appended after the Batch 3–6 redo. The Batch-1 record above is unchanged; this section carries what later batches confirmed, refined, or newly found. Full text: `20-finding-register.md`. Corpus-level patterns: `50-cross-batch-synthesis.md`.

## 5. The FA-1 cascade, re-verified downstream

**The annotation debt is total.** Checked directly across both cascade ranges: **not one** cascade member in any batch carries a post-retirement note. Batch 5's six members (0239/0240/0241/0243/0244/0246) return zero hits for FA-1/holonomy-retirement (`AA-493`); Batch 4's three (0180/0181/0197) likewise (`AA-485`). The per-ADR re-verdict §1 recommended is entirely un-started.

**One 🔴 re-confirmed with fresh primary evidence (`AA-494`).** `algebra/holonomy.py:52-92`: the docstring documents *"Reverse walk: R = (1-alpha)·reverse(wn)…; Holonomy: H = F·R"*; the body validates `alpha ∈ [0,1]` at `:69-70`, computes **only the forward walk**, and returns `_word_versor(F)`. `core/physics/biography.py:94` passes the inert `alpha`, then asserts `versor_condition(blade) < _CLOSURE_TOL` and raises *"biography blade not closed"* — on a quantity closed by construction of `_word_versor`, not a holonomy. Independently re-derived at HEAD, confirming `AA-51`/`AA-68`. **ADR-0240 must not be accepted in its current form.**

**One 🔴 refined downward, with the evidence stated (`AA-484`).** `AA-64` rated ADR-0180's holonomy dependency structural. Reading §1:15-18 directly shows it is a *framing premise* ("supreme architectural invariant… Holonomy Resonance") justifying the design's mechanical cost — the shard/merge mechanics compute no holonomy and stand on ordinary concurrency merits. Corrected action: an amendment note re-grounding §1's justification, not a mechanism change. Severity for triage: framing-🟡. Per the register's rule, this downgrade carries new evidence — unlike the retracted pass's silent softening of `AA-75`.

**Acceptance packets, not ADR prose, are the right repair surface (`AA-495`).** ADR-0241 was Accepted 2026-07-15 and ADR-0243 on 2026-07-17 — 13 and 11 days *before* FA-1 — each via a `docs/audit/` acceptance packet containing holonomy-adjacent claims never re-examined. The re-verdict should re-open the two packets.

**Dissolved-by-accident, still owed (`AA-508`, `AA-509`).** `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md:59` reserves numbers 0254–0261 for eight Blueprint gap-intents "not materialised until the owning stage implements them." **All eight have since been minted as unrelated deduction/serving-arc ADRs**, and neither the mapping nor ADR-0253 clause 3 was amended — a reader following the mapping is misdirected in 8 of 8 rows. Side effect: Batch 1's `AA-73` risk (holonomy-SIMD hardened under a reserved 0261) is dissolved because the number is taken, but the BP-0253 intent now has no reserved home and still no NO-GO annotation. `AA-82`'s requested annotation is more urgent, not less.

## 6. New contradiction classes found in the redo

- **A gate that punishes compliance with its own governing ADR** — `core/capability/reporting.py:421` gates `reasoning_capable` on the existence of the git-tracked plaintext `evals/cognition/holdouts/cases_plaintext.jsonl`, while ADR-0105 calls plaintext holdouts a trust-split violation and orders them resealed. Complying would flip every domain to `reasoning_capable=false`. Repo-wide: **3 `.age` vs 32 plaintext** holdout artifacts. Full write-up: `50-cross-batch-synthesis.md` §Pattern C-bis.
- **Ratified authority derived from unratified documents** — ADR-0175 (`Proposed`) supplies the invariants Accepted ADR-0256 cites by number and the θ_SERVE ceiling licensing all 25 deduction bands (`AA-491` 🔴); ADR-0201 (`Proposed`) is the `proof_chain` keystone that Accepted ADR-0201.1 "hardens" and Accepted 0202–0205 build four phases on (`AA-504` 🔴). Measured scale: 61 of 314 ADRs are `Proposed`/`Draft`, ≥16 of them test-pinned. See `50-cross-batch-synthesis.md` §Pattern A.
- **Intra-number record contradiction** — `0226~3` reads `Proposed` while its own sibling `0226~2` ratification record says accepted-for-staged-implementation, both dated 2026-06-22 (`AA-499`). The `H-8` pattern inside a single ADR number.
- **A governance mandate with zero adopters** — ADR-0225's required "Governance citations" section appears in **none** of the ~60 subsequent ADRs, and no lint check exists (`AA-497`). Contrast ADR-0165, whose prohibition is pin-enforced *and* propagated into unrelated authors' test files (`AA-490` 🟢) — same corpus, same era, opposite outcomes.
- **Cross-repository citation collision** — ADR-0237 cites a foreign repo's `ADR-0025-hard-closure-and-master-substrate.md (Sopher)` on the line above this repo's own `ADR-0025 (CORE)` (`AA-501`); bare number reuse across repositories is a trap for any number-resolving tooling.
