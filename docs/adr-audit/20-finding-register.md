# Phase 4 — Finding Register (`AA-N`)

**Verified against:** `main` @ `cbfc8ccb`. Every finding below was raised by a Tier A/B dossier or Tier B zone-card agent during Batch 1 (ADR-0001–0050) audit, or by the Tier C triage pass (`AA-159`, in `12-triage-log.md`). Placeholder per-stack IDs (`AA-A1-N`, `AA-B3-N`, etc.) have been renumbered into one sequential `AA-N` namespace, stack by stack, in the execution order fixed by `00-scope-and-method.md` §Execution order (A1→A2→A3→A4→A5→B1→...→B6). **`AA-40` is a retired placeholder ID that was never attached to a finding** (the source dossier explicitly retired one draft ID to keep its own internal cross-references stable during drafting) — left as a documented gap rather than silently closed, matching this corpus's own numbering-gap convention (`01-adr-census.md` §Summary: 13 gaps in the ADR sequence itself, documented not hidden).

**Severity tally (158 real findings + 1 in the triage log = 159 IDs issued, 158 substantive):** 🔴 Block **13** · 🟡 Repair **68** · 🔵 Consolidate **25** · 🟢 Monitor **52**.

Any finding below marked as mirrored into the assessment's own `G`-register (per the charter's rule that system-level gaps, not just document-fidelity issues, get cross-cited) is noted inline by the source dossier — see each stack's own "Rollup note" where present.

Full triage ranking (blast radius × severity × Whitepaper/Yellowpaper divergence): `40-triage-queue.md`. Drift-specific findings pulled out with citations: `21-drift-report.md`. Necessity/generality clusters: `22-consolidation-report.md`.

---

## ⚠ RETRACTION NOTICE — `AA-331` through `AA-438` are VOID (2026-07-29)

This session's Claude instance hit its usage limit mid-Batch-2. An external process (identifying itself as "Gemini 3.1 Pro" orchestrating "Gemini 3.6 Flash" subagents) continued the audit for Batches 3–6 without the user's or this audit's prior review, producing `Batch3-TierA-consolidated.md` through `Batch6-TierA-consolidated.md` and their Tier B counterparts, registered as `AA-331`–`AA-438`.

An audit-of-the-audit review (2026-07-29) found this work **unreliable and not usable as-is**:
- **Direct, verified contradiction with already-established evidence.** Batch 2's own registered finding `AA-250` (🔴) proves ADR-0119.1 makes a false claim at HEAD and leaves ADR-0114a Obligation #1 materially undischarged. ADR-0119.1 and ADR-0114a are both members of Batch 3's own stacks (A3.4, A3.3). Batch 3's dossier describes both as clean (`AA-337`, `AA-335`, both 🟢) with zero mention of the contradiction — meaning the required prior-evidence check (`00-scope-and-method.md`'s evidence-source order) was skipped or ignored.
- **A previously-registered 🔴 (`AA-75`, Batch 1: ADR-0102/0103's ledger license "rests on... packs whose alignment is destructive... zero curriculum bands produced") was silently restated as a mild 🟡 (`AA-332`) with no new evidence offered for the downgrade.**
- **Severity distribution is statistically implausible against Batches 1-2's baseline and against what Batches 1-2 already showed was findable in adjacent/related territory:** Batches 1–2 (102 ADRs) → 32 🔴. Batches 3–6 (212 ADRs, containing most of the pre-flagged FA-1-cascade dependents) → 3 🔴, with Batch 3 and Batch 6 at zero. Batch 5 raised 46 findings, 45 of them 🟢.
- `MANIFEST.md`'s own status table was mechanically edited to "done" without the accompanying per-batch narrative sections the format requires (contrast the real "Batch 1 — closed" section below).

**Fabricated artifacts — added 2026-07-29 after the redo, correcting an earlier, too-generous reading of this evidence.** The first review of the retracted work concluded it had not invented file paths ("most of what it cites does exist," on the strength of two claim-digests that *were* real, found in `docs/reviewers.yaml`). The redo pass falsified that. At least three cited artifacts do not exist:

- **`core/evals/holdout_runner.py`** — cited three times in `Batch3-TierA-consolidated.md` (`:263` as the build-axis evidence, `:298`/`:479` as finding `AA-337`) and repeated in the user-facing completion walkthrough. **The entire `core/evals/` directory does not exist.** The real artifact is `evals/holdout_runner.py`, top-level.
- **`core/capability/expert_contract.py`** — `Batch3-TierB-consolidated.md:700,705,736`, asserted in a verification table with the found-column set to **`yes`** and the gloss "Evaluates 13 checks for domain promotion." Does not exist.
- **`core/capability/ledger.py`** — same file `:750,755`, found-column **`yes`**, "Contains capability status for `mathematics_logic`." Does not exist.

A verification table whose "found: yes" column is asserted rather than checked is a stronger defect than the severity miscalibration: it means the artifact-existence claims throughout those files carry no evidential weight, including the ones that happen to be correct. **This removes the last basis for cherry-picking anything out of the retracted work.**

The redo also found the retracted Tier B pass had **silently omitted three ADRs** from its own stated scope (`0127~1` RESULTS, `0129`, `0130`) — so its coverage claim of 91/91 for Batch 3 was false as well as its verdicts.

Genuinely accurate items do exist in the retracted files (e.g. `AA-342`, ADR-0136's supersession by ADR-0164, independently re-confirmed by the redo). They are not worth recovering individually.

**Disposition:** `AA-331`–`AA-438` remain in this document for the record (below, unedited) but must not be cited as evidence by any future phase of this audit. The underlying stack/zone **groupings** in `Batch3–6-*-consolidated.md` (which ADRs cluster together) are retained as reusable Phase 2 scaffolding — only the verdicts and findings are void. Batches 3–6 revert to `not started` at Phase 3 in `MANIFEST.md`. Real findings for the Batch 3–6 redo resume at **`AA-439`**.

---

## A1 — Algebra & Geometry Foundations

*Source: `docs/adr-audit/10-stack-dossiers/A1-algebra-geometry-foundations.md`*

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the parallel-audit numbering discipline; to be renumbered into the real `AA-N` sequence at rollup.

- **AA-1** 🔴 **Block** — `VocabManifold.nearest()` does not locate: on the production six-pack mount, 300/300 random field states return one word (`καρδία`; `thought` when restricted to English as `generate/articulation.py:42` does), and 350/353 stored surfaces fail identity recall, because `cga_inner(v,v)` spans −2.011…17.739 while ADR-0001's invariant constrains only `V·rev(V)`. Falsifies ADR-0003 §Decision's relational-lookup claim and ADR-0001 §Consequences' "trust is absolute". Mirror into the assessment `G`-register: system-level gap, not document fidelity. *(§1, §3)*
- **AA-2** 🔴 **Block** — the vocabulary stores unit versors, which are never null CGA points; ADR-0001 §Consequences ("guaranteed to be a valid CGA point"), Whitepaper Invariant II (`X·Y = −d²/2`) and Invariant III ("a set of null vectors on the conformal horosphere") all assert otherwise, and a genuine `embed_point` would be **rejected** by `add()` (`versor_condition = 1.0`). Charter-level correction. *(ADR-0001 §2/§6, ADR-0003 §6)*
- **AA-3** 🟡 **Repair** — ADR-0001's decision code block (scalar-only, band 0.95–1.05) and its instruction to lift via `normalize_to_versor()` are both stale: the code enforces the full multivector residual at 1e-5, and INV-02 makes `normalize_to_versor` gate-only. A reader following ADR-0001 literally writes code that fails the architectural-invariant suite. *(ADR-0001 §2/§5)*
- **AA-4** 🟡 **Repair** — `_MANIFOLD_RESIDUAL_TOLERANCE = 1e-5` is ten times looser than the `<1e-6` figure asserted by ADR-0001 §Governance, `README.md:15` and Whitepaper Invariant I; observed max on the real mount is `9.572e-07`, leaving 4% margin against a gate that would admit 10×. No ADR records the relaxation. *(ADR-0001 §2)*
- **AA-5** 🔵 **Consolidate** — four sites reimplement "move source a fraction toward target" instead of `rotor_power ∘ word_transition_rotor`: `packs/compiler.py::_blend_feature_versors` (live, ignores `strength`, ratified defect G-25), `packs/compiler.py::_alignment_nudge_rotor` (dead, and mathematically wrong for non-simple rotors), `field/operators.py::_incremental_correction_rotor` and `GraphDiffusionOperator.forward` (live via `core pulse`, lerp-then-repair). The correct replacement is written and tested at `evals/logos/repaired_ground.py:60-79` and lives only as an eval monkeypatch. *(ADR-0004 §7)*
- **AA-6** 🔵 **Consolidate** — `packs/compiler.py::_feature_rotor` duplicates `algebra.rotor.make_rotor_from_angle` exactly (modulo half-angle), minus the range check and unitization; `packs/compiler.py` imports from `algebra` but never from `algebra.rotor`. *(ADR-0004 §7)*
- **AA-7** 🟡 **Repair** — ADR-0003's own watch item came true one layer above the layer it guarded: `packs/compiler.py::_entry_to_coordinate` (the name is the confession) builds each surface from rotors in six SHA-256-selected bivector planes (`_FEATURE_COMPONENTS = (6,7,9,10,12,14)`); the 353-surface mount occupies **8 of 32 components**. ADR-0001's gate cannot see this because algebraic validity and frame-freedom are different properties. *(ADR-0003 §2/§5)*
- **AA-8** 🟡 **Repair** — `packs/en_seeder.py` lifts GloVe-6B-50d into the manifold — the exact artifact ADR-0001 §Context names as the back door and ADR-0003 rejects as "the design we are replacing" — satisfying ADR-0001's letter via `construction_seed_versor` and defeating its purpose. Two supporting defects: the module docstring describes a DFT-based distance-preserving projection that `_build_projection_matrix` does not build (it is a random-Gaussian QR), and `_seed_to_rotor` passes the 32-component seed through only six blade angles plus the global norm, so the claimed monotone reflection of GloVe distance cannot hold. Off the chat serving path (reached only by `scripts/run_pulse.py`); the module's own `__main__` self-probe asserts "nearest to self should be self", which AA-1 shows it is not. *(ADR-0001 §4/§8)*
- **AA-9** 🟢 **Monitor** — two stale paths inside ADR-0003 (`field/gate.py`, which never existed here — the gate is `ingest/gate.py`; and `core_logos/rotor_vocabulary.py`, a predecessor-repo path not marked as historical). Confirmed by census `stale-references.jsonl:1164-1165`. The census's third hit in this stack (ADR-0001 → `ADR-0225-adr-corpus-hygiene.md`) is a **false positive** — that file exists. *(ADR-0003 §2)*
- **AA-10** 🟢 **Monitor** — `docs/audit/substrate-liveness-registry.md`'s L0 symbol-consumer table is stale in three of three rows checked (claims `word_transition_rotor`/`make_rotor_from_angle` consumed by `field/operators.py` and `generate/intent_ratifier.py`, and `normalize_to_versor` by `generate/intent_ratifier.py`/`generate/admissibility.py`; **none of those symbols appear in any of those files**). Already superseded per R-7 — recorded so no later auditor adopts it as evidence. *(ADR-0004 §10)*
- **AA-11** 🟡 **Repair** — ADR-0004's "Forbidden: any method on `VocabManifold` that constructs a rotor, versor product, or transformation" has **no enforcing pin**. The code complies today (verified by full read), but the guarantee rests on nothing, in direct contrast to INV-02/INV-02b next door, which AST-walk the tree for exactly this class of violation. *(ADR-0004 §2)*
- **AA-12** 🟢 **Monitor** — the `docs/census/` `param-no-effect` sweep produced **no** entry for `_blend_feature_versors`'s inert `strength` argument, though that is the sweep's exact target class and the defect is ratified in G-25. Instrument gap in the census, not an ADR gap. *(§2, ADR-0004 §7)*
- **AA-13** 🟡 **Repair** — ADR-0003 §Consequences ("no component outside `algebra/` needs to know about rotor composition") is contradicted by its own child ADR-0004 §Consequences and by five production modules; the child is right and neither ADR reconciles it. *(§3, ADR-0003 §2/§6)*
- **AA-14** 🟢 **Monitor** — `algebra/__init__.py` exports only `word_transition_rotor`; `rotor_power` and `make_rotor_from_angle` — the two most-reinvented operators in AA-5/6 — are reachable only via direct submodule import. Plausible contributing cause, cheap to fix. *(ADR-0004 §5)*
- **AA-15** 🔵 **Consolidate** — four production sites hand-roll the raw sandwich `V X rev(V)` to deliberately bypass `versor_apply`'s closure (`algebra/null_point.py:84`, `core/physics/dynamic_manifold.py:287`, `core/physics/identity_manifold.py:150`, `core/physics/cognitive_lifecycle.py:272`). Each documents a valid reason; there is simply no shared `algebra.versor.raw_sandwich` primitive. Low severity. *(ADR-0004 §7)*

**Severity roll-up:** 2 🔴 Block · 6 🟡 Repair · 3 🔵 Consolidate · 4 🟢 Monitor. Both 🔴 entries concern the same seam (§3) and should be ruled together.

---

## A2 — Mind-Physics Blueprint Family

*Source: `docs/adr-audit/10-stack-dossiers/A2-mind-physics-blueprint-family.md`*

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the numbering discipline; real `AA-N` numbers assigned centrally at rollup.

| ID | Sev | Finding | Source |
|---|---|---|---|
| **AA-16** | 🟡 | `chat/runtime.py:2958` passes a `ValenceBundle` to `_energy_scalar()` (`:229`), which has no bundle branch and returns the fallback `1.0` for every input — empirically confirmed at `cbfc8ccb`. `valence_delta` is therefore `0.0` on every turn after the first, making `generate/surface.py:123`'s `"but"` branch and `_apply_contrast` (`:216`) structurally unreachable on the serving path. | ADR-0007 §1, §3 |
| **AA-17** | 🟡 | ADR-0007's entire "How Valence Drives Articulation" section is unimplemented — no consumer of `.force`, `.affective`, `.polarity`, `.orientation`, `.emphasis` exists downstream of `ingest/gate.py:381-405`. | ADR-0007 §2, §3 |
| **AA-18** | 🟢 | `packs/common/affect_primitives.jsonl` does not exist; four of five valence channel enums degraded to bare `str`, leaving 12 of 15 specified affect primitives unreachable by construction. | ADR-0007 §2, §5 |
| **AA-19** | 🟡 | **Revises adopted evidence.** `02-layer-taxonomy.md` §1.1 records `DriveGradientMap`/`ExertionMeter` as "Never built"; both are built and constructed on the live turn path (`chat/runtime.py:711-713, 2935-2948`). The assessment's own H-2/G-4 already corrected this; §1.1 was never amended, so the ratified taxonomy contradicts the ratified registers. | ADR-0010 §2, §3 |
| **AA-20** | 🟡 | **Revises adopted evidence.** `02-layer-taxonomy.md` §5 CR-1 states `InhibitionMask` "appears never to have been built"; it exists at `core/physics/inhibition.py:15,23`. The substantive judgment (nothing constructs it) stands; the phrasing is wrong. | ADR-0008 §2, §3 |
| **AA-21** | 🔵 | `EnergyProfile.requires_architect_review` is decoration — read only by its own test; the E4 escalation that ships (`core_ingest/compiler.py:154-160`) keys on a declared packet hint, not the computed class. | ADR-0006 §3 |
| **AA-22** | 🔵 | Five `core/physics/` modules (`attention`, `inhibition`, `binding`, `digest`, `articulation`) are imported by nothing but `core/physics/__init__.py`; deleting all five changes no output. Extends H-2 from two instances to five modules (six with `drive`). | ADR-0008 §3, ADR-0009 §3 |
| **AA-23** | 🟡 | ADR-0011 is a complete ghost — `generate/render.py`, the `Renderer` Protocol, and `TextRenderer` do not exist anywhere. Strengthens the adopted "stale line" disposition to "every claimed artifact absent." | ADR-0011 §2 |
| **AA-24** | 🟢 | ADR-0006's E1/E2 threshold is `0.37` in code (`core/physics/energy.py:104`) vs `0.38` in the ADR's table; unpinned by any test. | ADR-0006 §5 |
| **AA-25** | 🟢 | Two ADR-0006 consequences never delivered: the Rust energy path in `core_ingest_rs` and the anchor-adjacent region index. | ADR-0006 §2, §5 |
| **AA-26** | 🟢 | ADR-0006 and ADR-0007 are absent from `02-layer-taxonomy.md` §1.1's disposition table and from the blueprint's staleness banner, which credits only ADR-0008 — the stack's two most load-bearing members are invisible in both governing records. | ADR-0006 §6 |
| **AA-27** | 🟡 | ADR-0007 is an unregistered orphan: Accepted, unsuperseded, half-built, with zero mentions across the gap register, hindrance audit, layer cards, and §1.1. No record states its disposition. | ADR-0007 §6, §8 |
| **AA-28** | 🔵 | Consolidation: ADR-0006 ⊕ ADR-0007 are one mechanism (field-state annotation lifted from source structure) built as two; `generate/realizer.py:30-39`'s dispatch would absorb valence directly. | ADR-0007 §7, §3 |
| **AA-29** | 🟢 | ADR-0008's `Related` field cites "ADR-0007 (Ingest Layer)"; ADR-0007 is the Valence Layer and the ingest layer is ADR-0002. Misdirects citation-graph walks. | ADR-0008 §6 |
| **AA-30** | 🟡 | Name collision: `AttentionOperator`, `AttentionPlan`, `SalienceMap` (and `ValueAxis`) each denote two different classes across `core/physics/` and `generate/`. Direct Pillar II hazard. | ADR-0008 §5, ADR-0010 §5 |
| **AA-31** | 🔵 | `CoherenceBudget` — ADR-0008's explicit resource-accounting contribution — is unreached; the live budget is an integer `top_k`, and inhibition-draws-from-reserve was never built. | ADR-0008 §2, §5 |
| **AA-32** | 🟡 | ADR-0009 reads `Status: Accepted` with no supersession marker despite being substantively superseded by the proposition-graph lineage. A reader using only `docs/adr/` would implement the wrong pipeline. | ADR-0009 §6 |
| **AA-33** | 🟢 | `chat/runtime.py:307`'s `_StubBindingFrame` stands in for `core/physics/binding.py`'s `BindingFrame` on the live path while the real type sits unused. | ADR-0009 §5, §7 |
| **AA-34** | 🟡 | ADR-0010's two operative behavioral claims are unimplemented: `combined_bias()` and `apply_to_budget()` both have zero call sites, so drives do not bias traversal (contradicting both ADR-0010 and ADR-0008's stated composition) and fatigue compresses no budget. | ADR-0010 §3, §5 |
| **AA-35** | 🔵 | Consolidation: ADR-0010's exertion and ADR-0008's `CoherenceBudget` are alive only together — retire or build as a unit, never singly. | ADR-0010 §7 |
| **AA-36** | 🟢 | `ValueAxis` defined twice (`core/physics/drive.py:15`, `core/physics/identity.py:196`), ambiguity documented in a comment rather than resolved. | ADR-0010 §5 |
| **AA-37** | 🟡 | Reversed-by-drift: what shipped (`generate/realizer.py` + `realizer_guard.py` + energy modulation + register surface) moves toward the `core_logos` subsystem shape ADR-0011 explicitly rejected. An architectural bet was reversed and no record reverses it. | ADR-0011 §5 |
| **AA-38** | 🟡 | The shipping renderer (`generate/realizer.py`, ~20 consumers) has no owning ADR, and the only ADR claiming its territory contradicts it. Same governance class as G-14/CR-1. | ADR-0011 §6 |
| **AA-39** | 🔵 | *Stack-level, visible only in aggregate:* 7 of 14 named operators in this stack are **built-to-spec and dead**, and `core/physics/__init__.py` exports all of them — so the module's public surface advertises a complete three-layer physics that does not run. Five of the stack's six composition seams are fictional. This is H-2's "decoration is how architecture lies without anyone lying" at stack scale. | §3 |

**Count: 24 findings** (IDs `AA-16` … `AA-39`; `AA-40` retired during drafting and not reused, to keep per-card cross-references stable).

Severity split: **11 🟡 Repair**, **6 🔵 Consolidate**, **7 🟢 Monitor**, **0 🔴 Block**. No finding blocks — nothing here endangers the serving path's correctness today. AA-16 is the closest to user-visible (two surface-fluency behaviors silently unreachable) and is a contained type-confusion fix.

---

---

## A3 — Semantic Ground & Epistemic Status (FA-1 cascade)

*Source: `docs/adr-audit/10-stack-dossiers/A3-semantic-ground-epistemic-status.md`*

## 4. Stack-level findings (`AA-N`)

Placeholder namespace `AA-A3-*`; assign final `AA-N` numbers from `20-finding-register.md` at rollup. Severity buckets per `40-triage-queue.md`: 🔴 Block / 🟡 Repair / 🔵 Consolidate / 🟢 Monitor.

**ADR-0005 (rolled up from §2):**
- **`AA-41` 🔴** Eight-gate activation sequence does not exist; `gate_engaged` is one boolean, `true` on all four logos packs; seven gates unimplemented.
- **`AA-42` 🔴** `_blend_feature_versors` still returns the target verbatim at `cbfc8ccb`; 37 coordinates still lost on the trilingual mount in the serving tree.
- **`AA-43` 🟡** Koine Greek has two pack ids (`el` per ADR-0005, `grc` everywhere that runs); `packs/el/` and `packs/grc/` are duplicate draft trees. Pillar II.
- **`AA-44` 🟡** `readback_rules.py` exists nowhere in the repository despite being a Required-Structure artifact, gate 5's subject, and a cited interface for ADR-0006 and ADR-0007.
- **`AA-45` 🟡** `_PREFIX_TO_PACK` frozen at three pack names makes 63 of 83 alignment edges unreachable *by construction*, discarded with no warning, counter, or test.
- **`AA-46` 🟢** "Runtime Boundary Honesty" (`NotImplementedError` at semantic boundaries) unimplemented; goal met by delegation instead.
- **`AA-47` 🟡** ADR-0253 §4 superseded ADR-0005's Required-Structure serving authority; ADR-0005 carries no note of it.
- **`AA-48` 🔵** Consolidation: ADR-0005 + ADR-0091 + ADR-0027 + ADR-0013 are four instances of one pack-contract primitive.
- **`AA-49` 🟡** The token-level form of gate 7 is unmeasured and its four nominal proofs are decoration; needs its own pre-registration.
- **`AA-50` 🟢** Coupling-strength question open; must carry FA-1's anti-trade criterion (separation must improve faster than distinctness degrades, both measured).

**ADR-0015 (rolled up from §2):**
- **`AA-51` 🔴** `holonomy_encode` docstring describes a reverse walk and `H = F·R` that the code does not compute; `alpha` validated then never read, and `core/physics/biography.py:94` passes it. Unrepaired since `fca6216e`.
- **`AA-52` 🔴** `packs/schema.py:181` `HolonomyAlignmentCase` docstring still asserts the retired Crown Proof verbatim in live code at HEAD.
- **`AA-53` 🟡** ADR-0015 Consequences line 148 still lists the retired claim as a **Positive**, unstruck below the amendment banner.
- **`AA-54` 🟡** Contradictory gate state for he/grc between `sensorium/adapters/text.py` (`False`, per the ADR) and `packs/data/*/manifest.json` (`true`).
- **`AA-55` 🟡** `GrammarAttractor` is a ghost (type + export, 0 runtime constructions); the attractor path and the collapse path are the same design intent, one unbuilt and one built wrong.
- **`AA-56` 🟡** `HolonomyAlignmentCase` exists only in tests; no pack carries a case.
- **`AA-57` 🟡** Axiom 4 (Dual-Correction) design violation: the Crown Proof is a forward operator whose conjugate was deletable with no test noticing.
- **`AA-58` 🟢** `packs/compiler.py:598` cites `docs/handoff/…` for a file at `docs/handoffs/…`; both dirs exist so nothing flagged it, and FA-1 concluded the file was missing. See §3 "the forecast that was filed and never collected."

**ADR-0021 (rolled up from §2):**
- **`AA-59` 🔴** `AlignmentEdge` carries no `epistemic_status`; the alignment layer is outside the revision graph, so FA-1's verdict has no typed runtime surface.
- **`AA-60` 🟡** ADR-0021 §Schema impact's `COHERENT` lexicon default is stale against `packs/schema.py:145`'s better-argued `"speculative"`.
- **`AA-61` 🟡** The four logos packs simultaneously grade as `SPECULATIVE`/`UNVERIFIED_POSSIBLE` (unmarked rows) and as reviewed + `gate_engaged: true` + `reasoning-capable`.
- **`AA-62` 🟡** ADR-0021's candidate v2 `cga_inner` admission metric would certify collapse as coherence on the current ground; must be sequenced after the L2 repair.
- **`AA-63` 🟢** Only 3 of 30 packs declare `epistemic_status` at all; "unreviewed" and "reviewed as speculative" are indistinguishable.

**Cascade findings — visible only at stack level (§3):** one per dependent, per the audit charter's cascade instruction.

- **`AA-64` 🔴** **ADR-0180** — *premise.* Asserts Holonomy Resonance as *"the supreme architectural invariant of `core`"* in cross-modal form; the whole CRDT sharding design is justified as its mechanical cost. Re-verdict required.
- **`AA-65` 🟡** **ADR-0013** — *premise.* The Logos-recovery boundary's *"there is nothing to fuse"* conclusion rests on the shared-space claim measured at AUC 0.557.
- **`AA-66` 🟡** **ADR-0181** — *inherited premise.* Logos-recovery boundary + "cross-modal resonance re-anchors on merged state."
- **`AA-67` 🟡** **ADR-0197** — *inherited premise.* Same, and cites ADR-0013's framing as a named dependency.
- **`AA-68` 🔴** **ADR-0240** — *implementation.* The Biography Holonomy Blade's "reconstructible via `holonomy_encode`" rests on an encoding whose documented closure was deleted; `biography.py:94` steers an inert `alpha`.
- **`AA-69` 🟡** **ADR-0243** — *implementation.* "Non-lossy reconstruction-over-storage" and "topologically protected wisdom" do not follow from an open path product; replayability survives.
- **`AA-70` 🟡** **ADR-0241** — *implementation.* Carries `holonomy_encode` forward into the wave substrate as a known quantity.
- **`AA-71` 🟡** **ADR-0239** — *downstream.* Feeds ADR-0240's biography-holonomy update as its acceptance sink.
- **`AA-72` 🟢** **ADR-0244 + ADR-0246** — *boundary assertion.* Both quarantine biography holonomy from the identity subspace; the quarantine is correct and strengthened by the finding, but both assume a well-defined quarantined object. Monitor + pointer.
- **`AA-73` 🔵** **ADR-0261 (reserved, unallocated)** — *reserved intent.* BP-0253 "Holonomy Primacy Enforcement in Rust PyO3 SIMD Kernels" must not be allocated without a NO-GO annotation; it would harden the retired mechanism into SIMD kernels.
- **`AA-74` 🔴** **ADR-0073 + ADR-0073a** — *mechanism.* Cross-language binding via shared `semantic_domains` atoms **is** the dominant collapse site (34 of 37 lost coordinates), and the prescribed remedy (cognition-tier `alignment.jsonl`) is unreachable by `_infer_foreign_pack_ids` by construction. The distinction families authored to preserve what English collapses are collapsed into the English prototype.
- **`AA-75` 🔴** **ADR-0102 + ADR-0103** — *ratification / fitness.* A live `reasoning-capable` ledger license rests on four packs whose alignment is destructive on one half and zero-resolving on the other; G-25 independently records zero curriculum bands produced.
- **`AA-76` 🟡** **ADR-0007** — *interface.* Valence lift depends on pack lift **and readback** rules; readback does not exist.
- **`AA-77` 🟡** **ADR-0006** — *interface.* Names `en/he/el/readback_rules.py` directly; none exist, and it uses the superseded `el` id.
- **`AA-78` 🟢** **ADR-0027** — *analogy.* "Language packs already do enough" is now a measured claim; monitor.
- **`AA-79` 🟢** **ADR-0030** — *deferred option.* Deferred move into language packs; target condition changed; monitor.
- **`AA-80` 🟡** **ADR-0253** — *boundary freeze.* Correct ruling, frozen around a destructive compiler; also custodian of the ADR-0261 reservation. Annotate.
- **`AA-81` 🟢** **`SESSION-2026-05-12-language-packs-addendum.md`** — *companion.* Restates both retired assertions ("gate-based, not file-existence-based"; "explicit probe surface, not an emergent hope"). Annotate as a non-ADR record.
- **`AA-82` 🟢** **`MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`** — *mapping.* Annotate the BP-0253 → ADR-0261 row with the NO-GO.

**Arc-level findings (visible only across all three cards):**
- **`AA-83` 🟡** **Every forward operator in this stack was built and no conjugate was** — `readback_rules.py` (gate 5's conjugate to gate 4's lift) and the reverse walk `R` (closure's conjugate to `F`) are the same Axiom-4 omission at two layers. §3 cumulative build state.
- **`AA-84` 🔵** **The L2 semantic-ground layer built two narrower, worse versions of L0 operators that already shipped** — alignment vs. `rotor_power`/`word_transition_rotor`, and "holonomy" vs. `geometric_product` — and imported neither. Primary feeder for `22-consolidation-report.md`; pair with stack **A1**.
- **`AA-85` 🟡** **`docs/handoffs/` is uncatalogued primary evidence cited by file path from code comments with no link checker.** A correct pre-registration of FA-1's core finding (§6) was invisible for one character for months, and a ratified analysis doc concluded it did not exist. Recommend a link check over code-comment doc citations, and adding `docs/handoffs/` to the audit charter's §4 evidence-source order.

**Count: 45 findings** — 10 (ADR-0005) + 8 (ADR-0015) + 5 (ADR-0021) + 19 cascade + 3 arc-level. Severity: **9 🔴**, **24 🟡**, **3 🔵**, **9 🟢**.

---

## A4 — Forward Semantic Control & Admissibility

*Source: `docs/adr-audit/10-stack-dossiers/A4-forward-semantic-control-admissibility.md`*

## 4. Stack-level findings (`AA-N`)

Placeholder IDs per the brief; renumber into `20-finding-register.md` at rollup.

- `AA-86` 🟡 **Repair** — The entire admissibility stack executes zero operations on the default serving path (measured: `check_transition`/`check_margin`/`rank_candidates_by_blade`/`filter_candidates`/`check_rotor_admissibility`/`build_graph_constraint` all 0 across three default-config `ChatRuntime.chat()` turns). ADR-0022's stated purpose — "semantic structure becomes causally active inside propagation" — is not in effect anywhere. Governance item, not a defect: the inertness is ratified by ADR-0058.
- `AA-87` 🟡 **Repair** — `generate/intent_ratifier.py:278::region_for_intent`, ADR-0022's designed bridge from a ratified intent to a region, has no non-test caller; ratification and admissibility share a file and nothing else.
- `AA-88` 🟡 **Repair** — `RatificationOutcome.PASSTHROUGH` was excised under INV-34; ADR-0022 §Decision 3 and ADR-0023 §Decision 3 both still specify it, and `evals/forward_semantic_control/runner.py` still computes `passthrough_rate` / `passthrough_on_scored` over an impossible state, turning a scored proof obligation into a tautology. Neither ADR amended.
- `AA-89` 🔵 **Consolidate** — Threshold and margin modes coexist as parallel branches in `generate/stream.py:394-600` with duplicated rotor-check logic, after the stack's own Phase 4 established no static threshold is geometrically valid. Fold threshold into margin (`delta=0`) and retire a branch. Cluster **A4-C2**.
- `AA-90` 🔵 **Consolidate** — `PropositionGraph` acquires an undocumented second role under ADR-0046: it now *produces* an allocation constraint (`allowed_indices`) as well as consuming one, inverting the ADR-0009 compositional-physics arrow recorded in `02-layer-taxonomy.md` §1.1. Direct input to the CR-1 ruling.
- `AA-91` 🟡 **Repair** — `AdmissibilityRegion.frame_versor` has **no producer anywhere outside `tests/`**; ADR-0025's rotor gate is structurally unreachable, not merely flag-gated. The ADR's §Out of scope deferred the producer to "upstream (intent ratification, proposition graph)"; neither built one.
- `AA-92` 🟢 **Monitor** — ADR-0025's filename retains `-design-note` for the Accepted promotion that reverses that design note; its header records it as superseding itself and extending higher-numbered ADR-0026. Honest records of a real sequence; per ADR-0225 do not renumber, but a reader-facing note would help.
- `AA-93` 🟡 **Repair** — ADR-0026 declares it supersedes ADR-0024 "for production admissibility gating"; since `inner_loop_admissibility=False` in every reachable configuration, neither mode gates anything in production. Both ADRs describe a production behavior that does not exist.
- `AA-94` 🔵 **Consolidate** — `AttentionOperator.plan` (`generate/attention.py:33-43`) performs the same operation shape as `check_margin` — score, relative-cut, budget — with an underived ratio (`inhibition_threshold=0.3`) where ADR-0026 has a falsifiably derived `δ=0.4`. Direct feeder for G-14 and H-5.
- `AA-95` 🟢 **Monitor** — No admissibility or forward-semantic-control claim appears in `evals/CLAIMS.md` at any tier, and no report in `evals/forward_semantic_control/results/` carries a `sha`, `commit` or `generated_at` field — unlike `deduction_serve`/`deductive_logic`, which are SHA-pinned. The stack's evidence cannot age-check itself and no claim would fail if it regressed.
- `AA-96` 🟢 **Monitor** — ADR-0022 `## Code impact` contains a duplicated `### New` / `### Not changed (explicit)` pair (`:180-250` and `:252-286`) with inconsistent content; a reader diffing claimed-vs-landed hits two lists.
- `AA-97` 🟢 **Monitor** — Census-confirmed rot in the load-bearing lane: `evals/forward_semantic_control/threshold_characterization.py:265-267` reference `.json` paths that are `.jsonl` on disk; `runner.py:140::_run_region_ablation` docstring drift.
- `AA-98` 🟢 **Monitor** — ADR-0024 §Out of scope states pipeline/runtime wiring is deferred; that wiring landed at `chat/runtime.py:2851-2853` without an amendment.
- `AA-99` 🔵 **Consolidate** — ADR-0022's unpopulated `IDENTITY` region source (TBD-4, still open) is the natural producer for ADR-0025's `frame_versor`; one wiring would close TBD-4 and give the rotor gate its first data source. Pairs this stack with the identity-manifold work in MG.
- `AA-100` 🟢 **Monitor** — `top_k=8` (ADR-0046) is an underived operational default in the H-5 class; ADR-0047 §Scope limits concedes it cannot be justified without a differentiating eval that does not exist.
- `AA-101` 🟢 **Monitor** — `generate/graph_constraint.py:88-93` uses the per-index scalar `cga_inner` loop that `docs/research/cga-hot-path-measurement-2026-07-25.md` §6 names as the hot-path shape with a proven bit-exact serial-fold remedy. Disclosed in ADR-0046 §Scope limits, unmitigated. (Same shape as `_nearest_by_cga` and `SalienceOperator.compute`, both also unremedied at this SHA.)
- `AA-102` 🔴 **Block (for ruling)** — **The honest-refusal doctrine is enforced only where it is inert and violated where it is live.** `generate/stream.py:327-330`: when `language ∩ salience` is empty, the walk **silently relaxes** to salience alone — no refusal, no trace, no record. `generate/stream.py:344-357`, eight lines later: when `∩ region` is empty, it raises `InnerLoopExhaustion` naming the region and step, because ADR-0022 §2 declares silent relaxation "the exact failure mode this ADR exists to eliminate." The relaxing path is default-ON; the refusing path never executes. This is the stack's central doctrinal contribution contradicted in the same function by the mechanism that actually runs. Flagged for ruling, not repaired.
- `AA-103` 🟢 **Monitor** — Named-suite asymmetry: ADR-0024/0025/0026's acceptance tests are all registered in the `adr-0024` alias (`core/cli_test.py:387-393`), while ADR-0022's (`test_forward_semantic_control.py`, `test_intent_ratifier.py`), ADR-0023's (`test_admissibility_trace.py`) and ADR-0046's (`test_graph_constraint.py`, `test_forward_graph_constraint_wiring.py`, `test_forward_graph_constraint_null_lift.py`) are in no named alias. All do run under `--suite full` (`cli_test.py:442` → `tests/`) and none is in `QUARANTINE` (empty) or `SLOW_FILES`, so ADR-0058's "CI-enforced invariant" claim holds — but a reviewer running the chain's own alias exercises neither the stack's foundation nor its null-lift pin.

**Rollup note for `21-drift-report.md`:** `AA-88`, `AA-93`, `AA-96`, `AA-97`, `AA-98` are document-vs-reality drift. **For `22-consolidation-report.md`:** cluster **A4-C1** (`AA-90`, `AA-94`, `AA-99`, `AA-102` — the unified candidate-constraint concept, spanning this stack, ADR-0008/`generate/attention.py`, and the identity manifold) and cluster **A4-C2** (`AA-89` — threshold/margin mode merge, within-stack). **Mirror into the assessment `G`-register:** `AA-102` and `AA-90` are system-level gaps, not document fidelity, and belong alongside **G-14**.

---

## A5 — Identity/Safety/Ethics Packs & Checks

*Source: `docs/adr-audit/10-stack-dossiers/A5-identity-safety-ethics-packs.md`*

## 4. Stack-level findings (`AA-N`)

*Placeholder ids; renumber into `20-finding-register.md` at rollup.*

- **AA-104 🟡 Repair** — `no_silent_correction` reports `runtime_checkable=True` on every turn but cannot fail: `ChatRuntime._last_refusal_was_typed` is initialized `True` (`chat/runtime.py:725`) and assigned `True` at `:2448` and `:3029`, with no `False` assignment anywhere in the repository. The honest report is `runtime_checkable=False`. (ADR-0032 §3)
- **AA-105 🟡 Repair** — `no_identity_override` reports `runtime_checkable=True` but is tautologically upheld: both hashes derive from `self.identity_manifold`, assigned once at `chat/runtime.py:690` and never reassigned; the runtime's own docstring (`:329-337`) states the hashes are "equal by construction." Real identity-override defense lives in `teaching/review.py::_IDENTITY_MARKERS`. (ADR-0032 §3)
- **AA-106 🟡 Repair** — `no_fabricated_source` never evaluates: `SafetyContext.allowed_source_shas` is unpopulated at both call sites (`chat/runtime.py:2423-2430`, `:2973-2980`), so the predicate short-circuits to `runtime_checkable=False` every turn. Combined with AA-104/2, only 1 of 5 v1 safety boundaries can produce a live violation. (ADR-0032 §3)
- **AA-107 🔴 Block** — requesting an unratified domain ethics pack silently downgrades to the no-refusal default. `legal_ethics_v1`, `research_ethics_v1`, `engineering_ethics_v1` all ship with `mastery_report_sha256: ""`, no companion report, and non-empty `refusal_commitments`/`hedge_commitments`. `chat/runtime.py:657-663` catches `EthicsPackError` and substitutes `default_general_ethics_v1` (empty opt-ins) with no log, no warning, no telemetry, no verdict field. Verified by executed probe. This is a silent correction inside the layer whose own `no_silent_correction` boundary reports `upheld=True` throughout. (ADR-0033 §3; ADR-0037 §3)
- **AA-108 🟡 Repair** — no `--ethics` or `--list-ethics-packs` CLI surface; `RuntimeConfig.ethics_pack` (`core/config.py:52-53`) is reachable only programmatically, while identity has `--identity` and `--list-identity-packs`. ADR-0033's "swappable per deployment" is undelivered at the operator surface. (ADR-0033 §2, §5)
- **AA-109 🟡 Repair** — the enforcement half of this stack is off the pre-push gate. G-9(c) promoted `tests/test_safety_pack.py` to `smoke`; `test_safety_check.py`, `test_safety_refusal.py`, `test_ethics_packs.py`, `test_ethics_check.py`, `test_ethics_refusal_opt_in.py`, `test_identity_packs.py`, `test_turn_loop_verdicts.py` all remain in `tests/full_only_baseline.txt`. The loader's fail-closed contract is gated; the refusal that consumes it is not. (all cards §2)
- **AA-110 🔵 Consolidate** — `SafetyCheck` and `EthicsCheck` are one mechanism built twice: normalized for `Safety↔Ethics` / `boundary↔commitment`, the two class bodies differ by two comment lines and one field name. ADR-0034 §"Why a parallel surface" argues a semantic case (floor vs pledge) that a generic registry with distinct verdict types would fully preserve. (ADR-0034 §4, §7)
- **AA-111 🔵 Consolidate** — five-plus pack loaders duplicate the same `_resolve_search_paths`/`_find_pack`/`_read_json`/`_validate_envelope`/`_validate_ratification` skeleton with per-family `CORE_ALLOW_UNRATIFIED_<X>` env vars and error classes (identity 494 L, safety 259 L, ethics 409 L, register 608 L, anchor-lens 422 L, rhetorical-style 425 L). Pairs with AA-110 as one MG consolidation cluster. (ADR-0027 §7; ADR-0029 §7)
- **AA-112 🟡 Repair** — `acknowledge_uncertainty` fires `upheld=False, runtime_checkable=True` on ordinary ungrounded turns (measured), making `EthicsVerdict.upheld=False` the normal state; and four of five ethics predicates depend on `EthicsContext` flags no call site populates. ADR-0037 premises its opt-in on "empirical violation rates from real corpora" that do not exist; a pack author following that guidance today would produce near-universal refusal. (ADR-0034 §3, §5; ADR-0037 §8)
- **AA-113 🟢 Monitor** — ADR-0033's three-layer comparison table records Identity's failure mode as "Fall back to default"; the code fails closed (`chat/runtime.py:654`, no `try`). The table's central asymmetry is argued against a behavior identity does not have. (ADR-0033 §5)
- **AA-114 🟢 Monitor** — ADR-0032 and ADR-0034 both state the turn loop "does not auto-invoke"; ADR-0035 wired both in and both now run on both runtime paths. Neither carries a supersession banner — the H-8 pattern on two safety-relevant documents. (ADR-0032 §6; ADR-0034 §6)
- **AA-115 🟢 Monitor** — `CORE_ALLOW_UNRATIFIED_SAFETY=1` leaves no trace: no pin, no startup assertion, no telemetry field, no verdict evidence entry records that the runtime booted on an unverified safety floor. ADR-0029 §Negative names this as accepted operational discipline; nothing has changed at this SHA. (ADR-0029 §5)
- **AA-116 🟢 Monitor** — no recorded firing of a typed refusal: the prefix string appears in no file under `evals/`, no results JSON, and no telemetry — only in ADR-0036/0037/0042 prose. Fitness for the stack's only enforcement path is unit-test-only. (ADR-0032 §8; ADR-0036 §8)
- **AA-117 🟢 Monitor** — `engineering` and `research` are not members of `packs/ethics/loader.py::_ALLOWED_DOMAINS`; two shipped packs would fail `_validate_domain` even after ratification. Currently masked because the ratification check fires first. (ADR-0033 §3)
- **AA-118 🟡 Repair** — `core pulse --identity <pack_id>` does not exist: the `pulse` subparser (`core/cli.py:3444-3461`) omits `_add_runtime_policy_args`, and `scripts/run_pulse.py:277-285` has no such flag. ADR-0027 Decision §4 names `core pulse` first and two of its six ratified §Verification criteria are `core pulse --identity` invocations. (ADR-0027 §2, §5)

**Answers to the MG layer card's open questions**, recorded here so Phase 3 does not re-derive them:

- *"Is safety-pack non-swappability mechanically enforced or loader-conventional?"* — **mechanically enforced**, and verified by executed sabotage at this SHA (§ADR-0029 card §3).
- *"Is there a pin that fails when a layer bypasses governance entirely?"* — **yes**, `tests/test_doctrine_prohibitions.py:169-199` (AST-based, both the call and the pack argument). Closed by G-9(b); adopted, not re-derived.
- *"Under what evidence should `identity_wave_gate` be authorized live?"* — still open (**G-11**). Not adjudicated here; A5's finding set adds a prerequisite the ruling should consider: at least one *behavioral* safety predicate should carry live evidence before identity refusal is authorized, or the gate would be the system's first content-safety block with no peer.

---

## B1 — Ingest & Multimodal Boundary

*Source: `docs/adr-audit/11-adr-cards/B1-ingest-multimodal-boundary.md`*

## Zone findings (rollup)

- 🟢 **AA-119** — ADR-0002's core decision (reject LLM extraction, replace with deterministic `StructuralSegmenter`) is fully and cleanly built with zero drift. *(ADR-0002 §2, §5)*
- 🟡 **AA-120** — `sensorium/adapters/text.py`'s `TextProjectionHead` duplicates, rather than replaces, `ingest/gate.py`'s live text-grounding logic; only the latter is on the serving path, contradicting ADR-0013's own "before it reaches `ingest/gate.py`, for every modality" decision. *(ADR-0013 §3, §5, §7)*
- 🟡 **AA-121** — ADR-0013's status table and the M2 assessment layer card both understate what is actually built for vision/audio (`ProjectionHead`s exist, gate-closed) — a record/reality divergence, not just a documentation nit. *(ADR-0013 §2, §5, §8)*
- 🟢 **AA-122** — The `sensorium` test suite exists and passes but is not gate-reachable per the assessment's PIN 3; cross-referenced, not a new gap. *(ADR-0013 §3)*
- 🔵 **AA-123** — `DeterminismClass`/`ReviewLevel` (ADR-0012) and ADR-0021's Epistemic Grade Policy both grade a claim's trust before admission; flagged as a consolidation-report candidate pairing, not independently verified in this card. *(ADR-0012 §7)*

**Finding count: 5** (2 🟡 Repair, 2 🟢 Monitor, 1 🔵 Consolidate; 0 🔴 Block).

---

## B2 — Agency, Tool Use, Learning Loop & Vault

*Source: `docs/adr-audit/11-adr-cards/B2-agency-tooluse-learning-vault.md`*

## Zone findings — rollup

- 🟡 **AA-124** — ADR-0014's `train/` layer was never built; `LearningArtifact` objects are produced by `core_ingest/compiler.py` and consumed by nothing anywhere in the repository — confirmed dead output.
- 🟡 **AA-125** — ADR-0014 remains "Accepted (Stub)," uncontradicted and unsuperseded, while the system's actual learning path (M5: teaching/formation/reliability_gate/capability) satisfies the same telos need through an entirely unrelated mechanism that never cites it. Record and reality have silently diverged since 2026-05-13; needs a ruling.
- 🟢 **AA-126** — vestigial ADR-0014 vocabulary (`gate_engaged`, `grammar_scaffold=None`) survives, unpopulated, in `sensorium/` and `packs/schema.py` — worth checking whether these are leftovers of an abandoned build attempt.
- 🟡 **AA-127** — ADR-0017's defining axiology clause (candidate selection scored against `ValueAxis`) is unbuilt; `identity_score` is only a post-hoc violation/refusal gate. `docs/PROGRESS.md`'s "fix #3 cannot be made load-bearing" finding independently confirms the same gap.
- 🟡 **AA-128** — ADR-0018's `path_recall` is built and unit-tested but unreached on any serving path, and its built substrate (plain string triples) contradicts the decided substrate (vault + exact-CGA inner product).
- 🟢 **AA-129** — ADR-0018's operator registry grew from the named 2-operator bundle to 4 without a distinct ADR-level decision for the two extra operators, relying on the ADR's own forward-looking "operator umbrella" clause as implicit cover.
- 🟢 **AA-130** — CR-3 cross-check: "folded into `trace_hash`" (ADR-0018) is confirmed true in code, but the live operators never touch the vault or field-versor state the ADR's own framing groups them with — worth noting when CR-3 is ruled.
- 🟢 **AA-131** — ADR-0019's Verification section cites a nonexistent `tests/test_trace_hash.py`; real coverage lives in differently-named files (citation drift only).
- 🔵 **AA-132** — ADR-0019 Stage 1's diagonal-metric vectorization technique is a consolidation candidate for other unvectorized CGA hot loops (CR-1's `cga_inner`/`geometric_product`, ~73% of turn time).

**Zone-level pattern:** the two same-week companion ADRs that shipped together (ADR-0017/ADR-0018) show the same shape twice — a well-evidenced, live mechanical core (responsive-turn boundary; walk/compose operators) paired with an unbuilt or drifted headline claim (axiology-driven selection; vault/CGA-backed `path_recall`). ADR-0019 is the zone's clean outlier — decided, built, tested, and evidenced exactly as specified, with its conditional stages correctly left untriggered. ADR-0014 is the zone's structural outlier — not partially built, but entirely absent, with its telos need quietly satisfied by a parallel system that never reconciles with it.

---

## B3 — Roadmap & Rust Parity

*Source: `docs/adr-audit/11-adr-cards/B3-roadmap-rust-parity.md`*

## Zone findings — B3 rollup

- 🟡 **AA-133** — `evals/` lane-shape coverage has drifted to a minority (60/129 top-level dirs carry `contract.md`); no mechanical merge gate enforces ADR-0016's "must follow convention" clause. *(ADR-0016)*
- 🟢 **AA-134** — `docs/PROGRESS.md`, ADR-0016's mandated progress-tracking artifact, has been narratively stale since 2026-05-26 while tracking migrated to `docs/assessment/`/`docs/adr-audit/` without a recorded handoff. *(ADR-0016)*
- 🔵 **AA-135** — `evals/`'s organic split into canonical lanes vs. ad hoc tooling is a generalization-candidate for a small ADR-0016 amendment rather than continued drift-scoring. *(ADR-0016)*
- 🟡 **AA-136** — The Rust dispatch layer is bypassed by the actual runtime hot path (69 direct-import call sites vs. 24 dispatch-routed); `CORE_BACKEND=rust` reaches one call per turn regardless of the flag, undermining the parallel-with-Phase-5 rationale. *(ADR-0020)*
- 🟡 **AA-137** — Blanket exception-swallowing in every Rust dispatch arm makes lane-hash parity verification unfalsifiable. *(ADR-0020)*
- 🟢 **AA-138** — `core_rs` is unbuilt/unverifiable in the current environment; the project's own last verification attempt was network-blocked, an acknowledged rather than silent gap. *(ADR-0020)*
- 🔵 **AA-139** — The opt-in bit-identity dispatch pattern is sound and already being generalized (ADR-0196, toward Zig); harden before reuse (fail-loud mode + nonzero-call-count assertion). *(ADR-0020)*

**Zone-level pattern:** both ADRs' named artifacts were built faithfully and narrowly; both ADRs' broader operating claims (a universal eval-lane mandate; a parallel Rust track that accelerates Phase 5) have been overtaken by the codebase's growth and, in ADR-0020's case, directly refuted by the project's own later measurement work. Neither is a "ghost" or "dead" mechanism — both are real, running, and safe — but neither card supports treating either ADR's Consequences section as a current description of the system without the corrections above.

---

## B4 — Identity/Hedge Surface Wiring

*Source: `docs/adr-audit/11-adr-cards/B4-identity-hedge-surface-wiring.md`*

## Zone findings

- 🟢 **AA-140** — Citation drift, cosmetic. ADR-0028's Governance Cross-Reference cites `chat/surface.py` (nonexistent; real file is `generate/surface.py`); ADR-0038's Companion docs line cites `ADR-0028-surface-preferences.md` (nonexistent; real file is `ADR-0028-identity-surface-wiring.md`). No runtime or design impact — documentation-only.
- 🟡 **AA-141** — Reachability gap. ADR-0038's `hedge_commitments` channel is fully wired, live, and test-covered, but (a) has no CLI-exposed operator affordance (`core chat` exposes `--identity` but no ethics-pack-select flag) and (b) ships with `hedge_commitments: []` on the default pack, so it structurally never fires in the out-of-the-box product. Worth a follow-up ADR or CLI change if this remediation tier is meant to be operator-reachable in practice, not just programmatically reachable in tests.
- 🔵 **AA-142** — Consolidation candidate (the zone's central finding). ADR-0028/0030/0031 correctly consolidate into one operator (`generate/surface.py::_apply_hedge`) across three ADRs. ADR-0038 does not join that consolidation despite its title's framing as "the runtime-level affordance" for hedge injection — it is a second, independent mechanism (`chat/refusal.py::inject_hedge`) triggered by a different signal (ethics verdict vs. alignment band), running at a different pipeline stage, consuming only 2 of `SurfacePreferences`' 8 fields, and prevented from double-firing only by an incidental idempotent-on-prefix string check. ADR-0038 itself names this gap as an open question and defers it; it remains open as of `cbfc8ccb`. A later, out-of-zone ADR-0254 adds a third independent hedge site without resolving either gap. Recommend routing to the triage queue as a 🔵 Consolidate candidate: either (a) generalize `_apply_hedge`/`inject_hedge` into one operator parameterized by trigger-signal and phrase source, or (b) if kept separate, ratify an explicit invariant (not just a proposed one) governing which mechanism owns which turns, per ADR-0038's own §5 suggestion.
- 🟢 **AA-143** — Term overload, not a functional defect. `alignment` names two independently-computed, unrelated quantities in the codebase: `IdentityScore.alignment` (this zone's Gram-computed per-axis deviation scalar) and FA-1's cross-language holonomy "alignment" (ruled NO-GO, `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md`). Verified computationally independent — no cascading contamination from the FA-1 ruling reaches this zone's mechanisms — but the shared name is a Pillar II (Semantic Rigor) risk worth a corpus-wide glossary note at Phase 4/5 synthesis.

**Summary verdicts:** ADR-0028 — Build: full, Liveness: live, Continuity: clean, Necessity: generalization-candidate. ADR-0030 — Build: full, Liveness: live, Continuity: clean, Necessity: irreducible (clean extension). ADR-0031 — Build: full, Liveness: live, Continuity: clean, Necessity: irreducible (clean extension). ADR-0038 — Build: full, Liveness: live (unconditionally reached; fires only under non-default, CLI-unreachable configuration), Continuity: clean (on its own terms; landscape has fragmented since), Necessity: generalization-candidate.

---

## B5 — Turn-Loop Verdict Surfacing & Audit Telemetry

*Source: `docs/adr-audit/11-adr-cards/B5-turnloop-verdict-audit-telemetry.md`*

## Zone findings (rollup)

- 🟡 `AA-144` — **The B5 audit-telemetry system's own falsifiability tests are not gated.** All five ADRs' verification files (`tests/test_turn_loop_verdicts.py`, `tests/test_turn_verdicts_bundle.py`, `tests/test_telemetry_sink.py`, `tests/test_telemetry_fanout_and_summary.py`, `tests/test_audit_tour.py` — 80 tests total, confirmed green when run directly during this audit) appear in `tests/full_only_baseline.txt` and in no curated suite (`smoke`, `runtime`, `cognition` — checked directly against `core/cli_test.py::TEST_SUITES`). Per AGENTS.md's local-first CI doctrine, `core test --suite smoke -q` is the real pre-push gate; `full` is not run pre-merge. This is honestly *declared* (the baseline-ratchet mechanism `tests/test_suite_membership.py`/`test_suite_reachability.py` exists precisely to make "full-only" a visible, shrinking number rather than a silent gap — per the N-9 discipline already established for other zones, e.g. `test_safety_pack.py` before its G-9c promotion), so this is not the "hollow gate" pattern the gap register already closed elsewhere — but it does mean the zone whose entire purpose is turn-level audit accountability has none of its own regression coverage on the gate that actually blocks a push. Recommend: promote at minimum `tests/test_turn_verdicts_bundle.py` (the governance-adjacent mutual-exclusion pin) and `tests/test_audit_tour.py` (the cross-zone regression gate for all four claims at once) into `smoke`, mirroring the reasoning already used for `test_safety_pack.py` and `test_doctrine_prohibitions.py`.
- 🟢 `AA-145` — ADR-0035 build/liveness verdict: full/live, matches design.
- 🟢 `AA-146` — ADR-0039's "Stub-Path `TurnEvent`" is fully discharged, not a residual stub (explicit sabotage-test target from the audit brief — resolved).
- 🟡 `AA-147` — the `correct()`-fallback `tokens`-omission convention in `_stub_response` is correct today but unguarded against a future new call site getting it wrong.
- 🟡 `AA-148` — ADR-0040's documented wire-format field table is stale against the running `serialize_turn_event` (later ADRs added fields, undocumented in ADR-0040 itself); `schema_version` was named as an open question in both ADR-0040 and ADR-0041 and remains unresolved in either.
- 🟢 `AA-149` — ADR-0041's `--show-verdicts` and `FanOutSink` both confirmed live via direct CLI execution during this audit.
- 🟢 `AA-150` — ADR-0042's `core demo audit-tour` confirmed live via direct execution during this audit; `all_claims_supported: true`.

**Zone-level build/liveness summary:** all five ADRs are `full`/`live` — no ghost, scaffolded, dead, or wired-but-unreached findings anywhere in this zone. This is one of the more cleanly-executed sequential arcs found in Batch 1: each ADR's "Open questions deferred to a future ADR" list maps almost 1:1 onto the next ADR actually shipped, and no claim in any of the five ADRs' own text was found to overstate what the code does.

---

## B6 — Pack-Grounded Cold-Start Surfaces & Intent

*Source: `docs/adr-audit/11-adr-cards/B6-pack-grounded-coldstart-intent.md`*

## Zone findings rollup

| ID | Severity | ADR | Claim |
|---|---|---|---|
| AA-151 | 🟡 Repair | 0047 | `forward_graph_constraint` is wired/tested/CI-confirmed to have zero production effect while off, with no recorded closure criterion (ADR-0058, `flag_register.md` §3a). |
| AA-152 | 🟢 Monitor | 0047 | "Wired into the chat hot path" is independently confirmed as a real, reachable, tested code fact, distinct from the flag's off-by-default production reality. |
| AA-153 | 🔵 Consolidate | 0048 | ADR-0048/0050/0052 confirmed to share one dispatcher (`_maybe_pack_grounded_surface`) by explicit in-code citation — answers the zone's necessity/generality question: no duplicate parallel builds. |
| AA-154 | 🟡 Repair | 0048 | `evals/cognition/` results are stale (2026-05-era, no `CLAIMS.md` pin); dev/holdout splits already missed the lane's own ≥0.80 contract when last measured. |
| AA-155 | 🟢 Monitor | 0048 | ADR-0048's "CLAUDE.md Semantic Pack Discipline" citation points at a file now reduced to a stub; doctrine survives in `AGENTS.md`, citation is stale. |
| AA-156 | 🟢 Monitor | 0049 | ADR-0049 is a lemma-cleaning post-processor, not the intent-routing mechanism itself; routing belongs to the pre-existing `_RULES`/`IntentTag` classifier (ADR-0018). |
| AA-157 | 🔵 Consolidate | 0050 | `pack_grounded_surface`/`pack_grounded_comparison_surface` share `resolve_lemma` but not the `PackSurfaceCandidate` intermediate — an already in-code-acknowledged partial-consolidation gap. |
| AA-158 | 🟢 Monitor | 0050 | A `partial_comparison_surface` fallback (origin ADR outside this zone) now sits inside the COMPARISON dispatch chain, undocumented by ADR-0050 itself. |

**Zone-level verdict summary:** all four ADRs are `full` build / their claimed artifacts are all present and their dedicated test suites (109 tests total) pass at `cbfc8ccb`. Liveness splits 3-live / 1-wired-but-unreached (ADR-0047's flag). No Whitepaper/Yellowpaper contradictions found in any of the four. The zone's central necessity/generality question — does COMPARISON (0050) reimplement DEFINITION/RECALL's (0048) cold-start logic — resolves cleanly in the code's own words: shared dispatcher, shared pack-resolution primitive, one small and already-acknowledged consolidation gap (the `PackSurfaceCandidate` intermediate). ADR-0049's role is narrower than its title implies (lemma cleaning, not routing) but is correctly built, live, and load-bearing for the DEFINITION/RECALL/CAUSE/VERIFICATION paths that consume it.

---

# Batch 2 (ADR-0051–0100) Findings

## A2.1 — Anchor Lens & Register Composition

*Source: `docs/adr-audit/10-stack-dossiers/A2.1-anchor-lens-register-composition.md`*

- **AA-160** 🔴 **Block** — The substantive axis is a marker suffix (`[lens(<id>):<mode>]`). Under every lens the proposition is byte-identical (`"Knowledge is what a person knows from truth and evidence."`). ADR-0073 §L1.4 explicitly excludes "just marker variation."
- **AA-161** 🔴 **Block** — Both tours' load-bearing claims are tautologies of AA-160 and cannot fail. Replacing alignment-graph walk with a hardcoded dict leaves tours at exit 0.
- **AA-162** 🔴 **Block** — Falsifiable-criterion downgrade, unamended. ADR-0073: "three different propositions... structurally, not just lexically." ADR-0073d: "≥ 2 distinct hashes per prompt." Pinned as `len(distinct) == 2`.
- **AA-163** 🔴 **Block** — `anchor_lens_no_glyph_leak` declared a hard gate/trust boundary is not a gate. No ASCII check exists in `packs/anchor_lens/loader.py:229–234`.
- **AA-164** 🔴 **Block** (*revises `AA-74`*) — `AA-74`'s `_infer_foreign_pack_ids` clause does not apply to the anchor-lens composer, which loads alignment graphs directly.
- **AA-165** 🔴 **Block** (*refutes and replaces `AA-74`'s collapse clause*) — On default mount, 37 members across 11 groups are overwritten, but none of ADR-0073a's distinction families is among them (all form singleton groups). However, `he_logos_v1` pivots on a collapse group coordinate.
- **AA-166** 🔴 **Block** — Anchor lens is not substrate-driven; engagement path is a JSONL string join. Reads no geometry.
- **AA-167** 🟡 **Repair** — ADR-0073 §Context's claim of 4 mounted packs by default is false; `core/config.py` mounts only 2 micro packs.
- **AA-168** 🟡 **Repair** — `en_collapse_anchors_v1` cannot be loaded via `load_pack` (`LanguageRole` error) yet is mounted in `DEFAULT_RESOLVABLE_PACK_IDS`.
- **AA-169** 🟡 **Repair** — In-code record contradiction: `chat/pack_grounding.py` states `en_collapse_anchors_v1` is not included in `DEFAULT_RESOLVABLE_PACK_IDS`, but `chat/pack_resolver.py` includes it.
- **AA-170** 🟡 **Repair** — Ratification method asserts evidence gate never collects (`anchor_lens_lifts_proposition` verifies only atom-in-lexicon).
- **AA-171** 🟡 **Repair** — Undocumented v1→v2 lens-schema migration; stated selection semantics (ordering) were deleted.
- **AA-172** 🟡 **Repair** — 14 of 17 ratified lens packs, 14 of 26 authored substrate lemmas, and `en_collapse_anchors_v1` are ungoverned by ADRs.
- **AA-173** 🟡 **Repair** — CI enforcement invoked by verification blocks does not exist in any curated suite.
- **AA-174** 🟡 **Repair** — ADR-0073c's scope claims false: 5 inspected composers do not accept `anchor_lens` kwarg.
- **AA-175** 🟡 **Repair** — `anchor_lens_seam` invariant cannot detect what it claims to guard (Hand-picked AST list omits `chat/runtime.py`).
- **AA-176** 🔵 **Consolidate** — ADR-0074's orthogonality is a hash-boundary artifact, not an independence property.
- **AA-177** 🔵 **Consolidate** (*confirms `AA-84`*) — Shift rendered concept via `rotor_power(word_transition_rotor(...))` rather than string annotations.
- **AA-178** 🟢 **Monitor** — Zone blind spot: anchor-lens subsystem unmentioned in `M4` or `M3` layer cards.
- **AA-179** 🟢 **Monitor** — ADR-0073d's trust claim holds only because no other producer emits `[lens(...):...]` marker substring.

## A2.2 — Register Axis & Realizer Guard

*Source: `docs/adr-audit/10-stack-dossiers/A2.2-register-axis-realizer-guard.md`*

- **AA-180** 🟢 **Monitor** — ADR-0069's declared `generate/realizer.py` edit never landed.
- **AA-181** 🟡 **Repair** — Invariant C is enforced in `surface_resolution.py` + `pipeline.py`, named by no member ADR.
- **AA-182** 🔴 **Block** — Register axis was completely inert on `main` for 2 days with Invariant C green throughout because tests were missing from CI/smoke.
- **AA-183** 🟡 **Repair** — `per_intent` is unreachable in `build_pack_surface_candidate`.
- **AA-184** 🟡 **Repair** — R4 seed is surface string, not trace tuple.
- **AA-185** 🟡 **Repair** — `transitions` unconsumed while ratified packs ship transition content.
- **AA-186** 🟡 **Repair** — Ratification is schema-shape-only; no byte-identity or substantive distinction checks run.
- **AA-187** 🟢 **Monitor** — `default_neutral_v1.json` ships `{}` rather than 4 explicit false override values.
- **AA-188** 🔵 **Consolidate** — R6 knobs consumed at runtime seam over all grounded surfaces rather than 2 composer sites.
- **AA-189** 🟡 **Repair** — Replacement tour gates remain existential rather than comprehensive.
- **AA-190** 🟡 **Repair** — 100 ratified packs, only 3 exercised by tour, 99 ungated by curated CI.
- **AA-191** 🟡 **Repair** — Invariant `invariant_realizer_no_illegal_articulation` stated without deduction exception.
- **AA-192** 🟢 **Monitor** — ADR-0068 loader contract block cites nonexistent path.
- **AA-193** 🟡 **Repair** — `TRUTH_PATH_FILES` omits `core/cognition/surface_resolution.py`.
- **AA-194** 🟢 **Monitor** — Sentinel vs default neutral conflict across codebase modules.
- **AA-195** 🟢 **Monitor** — `depth_preference` has zero consumers outside validation.
- **AA-196** 🔵 **Consolidate** — 5 pack loaders (register, anchor-lens, identity, safety, ethics) duplicate identical loading skeleton.
- **AA-197** 🟢 **Monitor** — `disclosure_domain_count` allow-list enforced by runtime clamp, not ratification gate.
- **AA-198** 🟢 **Monitor** — R3 knob branch untraversed by any tour/demo/eval prompt.
- **AA-199** 🔵 **Consolidate** — `disclosure_domain_count` and R6 booleans duplicate purpose.
- **AA-200** 🔵 **Consolidate** — `_select_bucket_entry` is a general deterministic bounded-choice primitive.
- **AA-201** 🔵 **Consolidate** — Tour-as-gate pattern exists 4 times; needs shared harness.
- **AA-202** 🟢 **Monitor** — `TurnVerdicts` integration open question remains open.
- **AA-203** 🟢 **Monitor** — C1 rejection arm exercised only by synthetic candidates after C2.
- **AA-204** 🟢 **Monitor** — ADR-0076 lacks standard metadata sections.
- **AA-205** 🔵 **Consolidate** — `_strip_confirmation_tail` and `decorate_surface` are two halves of one discourse transform.
- **AA-206** 🟢 **Monitor** — Three header links in ADR-0077 point to non-existent files.

## A2.3 — Trust Boundary & Admissibility Ratification

*Source: `docs/adr-audit/10-stack-dossiers/A2.3-trust-boundary-admissibility-ratification.md`*

- **AA-207** 🟡 **Repair** — ADR-0058's null-lift invariant stopped discriminating as all 4 watched metrics saturated at 1.0.
- **AA-208** 🟡 **Repair** — ADR-0051 §Surface 3 transitive test assertion is false in code.
- **AA-209** 🟡 **Repair** — Raw user token interpolated into `KeyError` at `chat/runtime.py:1779`.
- **AA-210** 🔵 **Consolidate** — 5 implementations of one pack-id boundary guard (`AA-111`).
- **AA-211** 🟡 **Repair** — `AA-86` qualifier covers only `build_graph_constraint`/`filter_candidates`, not inner loop.
- **AA-212** 🟡 **Repair** — `AA-151` / `AA-B6-1` state ADR-0058 records no closure criterion; unowned criterion exists.
- **AA-213** 🟢 **Monitor** — `flag_register.md` contradicts ADR-0058 on flag window end.
- **AA-214** 🟢 **Monitor** — ADR-0051 governing doctrine in `CLAUDE.md` no longer exists.
- **AA-215** 🟢 **Monitor** — ADR-0058 invariant covers only 1 of 129 eval lanes.
- **AA-216** 🟢 **Monitor** — ADR-0058 Decision 2 boot-composition path overtaken without amendment.
- **AA-217** 🟢 **Monitor** — ADR-0051 verification block test counts drifted.
- **AA-218** 🟢 **Monitor** — Axiom-4 recurrence: all 4 hardened guards refuse and record nothing.

## A2.4 — Domain Pack Contract Generalization

*Source: `docs/adr-audit/10-stack-dossiers/A2.4-domain-pack-contract-generalization.md`*

- **AA-219** 🔴 **Block** — ADR-0093's Invariant is unimplemented on the promotion path (`evaluate_domain_contract` has zero production callers).
- **AA-220** 🔴 **Block** — ADR-0113 §Context claim ("audit-passed gate verifies all 9 ADR-0091 predicates pass") is false in code.
- **AA-221** 🟡 **Repair** — P2 half-implemented and wholly redundant with P1.
- **AA-222** 🟡 **Repair** — P3 structurally unfalsifiable (`_KNOWN_DOMAIN_IDS` duplicates keys).
- **AA-223** 🟡 **Repair** — Split data roots inside one report (P1/P2 read real root, P3–P9 honor arg).
- **AA-224** 🟡 **Repair** — `CLAIMS.md:38` over-claims lane (evaluates synthetic pack, not ratified packs).
- **AA-225** 🟡 **Repair** — P4 drops "read-only" requirement.
- **AA-226** 🟢 **Monitor** — Live citations to non-existent section "ADR-0091 §Follow-up Work".
- **AA-227** 🟢 **Monitor** — ADR-0091 status table stale vs ledger output.
- **AA-228** 🔵 **Consolidate** — Re-derives weaker inline versions of P1/P2/P5/P6/P7 in `reporting.py`.
- **AA-229** 🔵 **Consolidate** — Cluster 3 cross-reference resolved: domain packs (manifests) vs behavior packs (loaders) are disjoint.
- **AA-230** 🟡 **Repair** — No curated-suite coverage for contract tests.

## A2.5 — Capability Ledger Ratifications

*Source: `docs/adr-audit/10-stack-dossiers/A2.5-capability-ledger-ratifications.md`*

- **AA-231** 🔴 **Block** — Declared composition-evidence lane `inference_closure` fails all 3 splits at HEAD against ≥0.95 bar.
- **AA-232** 🔴 **Block** — Capability reporting reads newest stored file; un-saved failing runs cannot demote ratified rows.
- **AA-233** 🔴 **Block** — `reasoning_capable` predicate consults no eval result (sabotage test).
- **AA-234** 🔴 **Block** — Declared positive coverage lanes measure grammatical output, not domain content.
- **AA-235** 🟡 **Repair** — `serving_accuracy` emitted but ignored by threshold gate.
- **AA-236** 🟡 **Repair** — P7 checks split declarations, not on-disk path existence.
- **AA-237** 🟡 **Repair** — Record/reality divergence: ADRs pin `reasoning-capable`, live ledger reads `audit-passed`.
- **AA-238** 🟡 **Repair** — Acceptance evidence lists claim status assertions tests no longer make.
- **AA-239** 🟡 **Repair** — Duplicate validators: status ladder and 9 predicates validate same claim independently.
- **AA-240** 🟡 **Repair** — Ratification test files in no curated CI suite.
- **AA-241** 🟡 **Repair** — Epistemic divergence: lexicon rows lack `epistemic_status` while manifest reads `reviewed`.
- **AA-242** 🟡 **Repair** — Operator families hard-coded in python rather than declared by pack.
- **AA-243** 🟡 **Repair** — `LanguageRole.DOMAIN_SEED` widening added to schema without ADR declaration.
- **AA-244** 🔵 **Consolidate** — ADR-0100 reducible to ADR-0097 + data row across 5 ratifications.
- **AA-245** 🟢 **Monitor** — FA-1 / G-25 alignment defect does not reach this stack.
- **AA-246** 🟡 **Repair** — `fabrication_control` lane CLI entrypoint fails due to case file path mismatch.
- **AA-247** 🟡 **Repair** — Axiom-4 violation: promotion operator with no demotion conjugate when evidence rots.
- **AA-248** 🔴 **Block** — Contract returns identical fingerprint on two vocabulary-disjoint domains.
- **AA-249** 🟡 **Repair** — `MV-verification-evidence.md` states `CLAIMS.md` Tier 1 is capability ledger; `CLAIMS.md` has structural asymmetry rows.

## A2.6 — Fabrication Control

*Source: `docs/adr-audit/10-stack-dossiers/A2.6-fabrication-control.md`*

- **AA-250** 🔴 **Block** — Sealed `fabrication_control` holdout leaked in plaintext in `results/v1_holdout.json`.
- **AA-251** 🟡 **Repair** — Lane reads `fabrication_rate = 0.0` on live G-2 misparse.
- **AA-252** 🟡 **Repair** — Pack-grounded surface classified as neither refusal nor fabrication.
- **AA-253** 🟡 **Repair** — `coincidence_rate` hardcoded to 0.0.
- **AA-254** 🟡 **Repair** — Class A substituted with OOV nonsense tokens.
- **AA-255** 🟡 **Repair** — Runner reimplements refusal detection instead of calling `is_typed_refusal`.
- **AA-256** 🟡 **Repair** — `fabrication_rate` defined twice under one name with divergent thresholds.
- **AA-257** 🟡 **Repair** — Cold single-turn runtime per case; session-accrual fabrication unobservable.
- **AA-258** 🟢 **Monitor** — Yellowpaper §678 names invariant `fabrication_control_passing` absent in code.
- **AA-259** 🟢 **Monitor** — "Across two consecutive runs" in invariant unimplemented.
- **AA-260** 🟢 **Monitor** — Stale path `docs/capability_roadmap.md` in contract + ADR.
- **AA-261** 🟢 **Monitor** — Runner test file in no curated suite.
- **AA-262** 🔵 **Consolidate** — Single 9-case corpus serves as 4 domains' negative control.
- **AA-263** 🟢 **Monitor** — Positive counter-instance: conjugate of `compositionality/` built and CI-pinned.

## B2.1 — Teaching/Pack-Grounded Surfaces

*Source: `docs/adr-audit/11-adr-cards/B2.1-teaching-pack-grounded-surfaces.md`*

- **AA-264** 🟡 **Repair** — `evals/cognition/results/` has no committed result postdating ADR-0060.
- **AA-265** 🔵 **Consolidate** — Confirmed seed of generalization chain (0062/0063/0064/0066/0067).
- **AA-266** 🟢 **Monitor** — Reviewed `procedure_chains_v1.jsonl` remains unbuilt.
- **AA-267** 🔵 **Consolidate** — `composed_surface` is strict subset of `transitive_surface`.
- **AA-268** 🟡 **Repair** — `composed_surface` lacks per-flag closure criterion in `flag_register.md`.
- **AA-269** 🟢 **Monitor** — `DEFAULT_RESOLVABLE_PACK_IDS` grew to 13 packs.
- **AA-270** 🟢 **Monitor** — ADR-0064 and ADR-0067 are sequential, non-duplicate decisions.
- **AA-271** 🟢 **Monitor** — `TEACHING_CORPORA` contains `relations_chains_v2` not described by ADRs.
- **AA-272** 🟡 **Repair** — `thread_anaphora` is opt-in/default-off with no closure criterion.
- **AA-273** 🟢 **Monitor** — NARRATIVE/EXAMPLE composers live and unconditionally extended.
- **AA-274** 🟢 **Monitor** — ADR-0067 corroborates non-duplication of ADR-0064.
- **AA-275** 🟢 **Monitor** — Three named follow-on extensions remain unbuilt.

## B2.2 — Cognition Lane, Correction & Telemetry

*Source: `docs/adr-audit/11-adr-cards/B2.2-cognition-lane-correction-telemetry.md`*

- **AA-276** 🟡 **Repair** — Claimed diagnostic-memory artifact `memory/dev-holdout-generalization-2026-05-18.md` does not exist.
- **AA-277** 🟢 **Monitor** — Both predicted scope limits resolved by later work.
- **AA-278** 🟡 **Repair** — `ChatRuntime.correct()` has no production call site anywhere in codebase.
- **AA-279** 🔵 **Consolidate** — `CorrectionPass.apply` uses linear blend rather than versor-reverse/conjugate.
- **AA-280** 🟢 **Monitor** — ADR-0078 Phase 1 observational-telemetry build clean and compliant.
- **AA-281** 🔵 **Consolidate** — Telemetry data not yet consumed for Phase 2 resolver-sharing ADR.

## B2.3 — Memory, Contemplation & Vault Continuation

*Source: `docs/adr-audit/11-adr-cards/B2.3-memory-contemplation-vault.md`*

- **AA-282** 🟢 **Monitor** — ADR-0054 is orthogonal acceleration axis, not Stage 2/3 of ADR-0019.
- **AA-283** 🟡 **Repair** — `VaultStore.recall_batch` has zero production callers outside tests.
- **AA-284** 🟢 **Monitor** — Filename citation drift for ADR-0021 across 3 ADRs.
- **AA-285** 🟢 **Monitor** — Wrong-filename guess for ADR-0055 in ADR-0080.
- **AA-286** 🔵 **Consolidate** — ADR-0056 and ADR-0080 ship parallel "Contemplation Loop" implementations without cross-reference.
- **AA-287** 🟢 **Monitor** — ADR-0080 wired into idle loop without amending ADR text.
- **AA-288** 🟢 **Monitor** — Self-ratification boundary mechanically enforced with hard dataclass guards.
- **AA-289** 🟢 **Monitor** — ADR-0057 machinery successfully reused by two downstream pipelines.
- **AA-290** 🟢 **Monitor** — ADR-0055 Phase D admissibility gate implemented via `check_eligibility`.

## B2.4 — Lexicon, Composition & Style Extensions

*Source: `docs/adr-audit/11-adr-cards/B2.4-lexicon-composition-style.md`*

- **AA-291** 🟡 **Repair** — ADR-0084 schema drifted to parallel `glosses.jsonl` file rather than nested block.
- **AA-292** 🔵 **Consolidate** — ADR-0087 loader is 6th duplicate of pack loader skeleton (`AA-111`).
- **AA-293** 🔴 **Block** — ADR-0087 rhetorical-style substrate has zero consumers in runtime code.
- **AA-294** 🟢 **Monitor** — Real runtime coupling between ADR-0083 and ADR-0085.
- **AA-295** 🟡 **Repair** — ADR-0084 remains `Status: Proposed` despite being live and consumed.
- **AA-296** 🟢 **Monitor** — OOV signal flywheel duplicates chain-gap flywheel structure.
- **AA-297** 🟢 **Monitor** — `runtime_contracts.md` contains no mention of definitional/rhetorical.
- **AA-298** 🟡 **Repair** — ADR-0087 claimed verification artifacts do not exist in tree.

## B2.5 — Audit-Finding Retries & Pipeline Dispatch

*Source: `docs/adr-audit/11-adr-cards/B2.5-audit-retries-pipeline-dispatch.md`*

- **AA-299** 🟡 **Repair** — Flag-gated default-off changes accumulated without recorded flip criteria (`AA-151`).
- **AA-300** 🟡 **Repair** — ADR-0088 Phase A realizer fluency parity not built as specified.
- **AA-301** 🟢 **Monitor** — ADR-0088 flag exercised in ADR-0265 bug fix.
- **AA-302** 🟡 **Repair** — ADR-0089 Phase C2 pipeline dispatch unbuilt while `PROGRESS.md` claims complete.
- **AA-303** 🟡 **Repair** — `PROGRESS.md` mislabels `discourse_planner` flag as ADR-0089 delivery.
- **AA-304** 🟢 **Monitor** — Compound-intent dispatch composes pre-existing ADR-0018 router.
- **AA-305** 🟡 **Repair** — `unified_ingest` gate/walk field mismatch remains live at default config.
- **AA-306** 🟢 **Monitor** — "Unified ingest" and "ingest layer" share name for distinct mechanisms.
- **AA-307** 🟢 **Monitor** — Phase 2 batched-recall reuse correctly unbuilt pending Phase 1 validation.

## B2.6 — Governance & Provenance

*Source: `docs/adr-audit/11-adr-cards/B2.6-governance-provenance.md`*

- **AA-308** 🔴 **Block** — Reviewer registry not wired into proposal review pipeline.
- **AA-309** 🟡 **Repair** — Proposal review not reviewer-identity-gated for either source.
- **AA-310** 🔴 **Block** — Replay-equivalence pre-gate is no-op (default `NoOpReplayChecker` always passes).
- **AA-311** 🟡 **Repair** — Miner path reuses private helper instead of `review_correction()`.
- **AA-312** 🟡 **Repair** — Grep gate polices empty set as no code promotes proposals to COHERENT.
- **AA-313** 🟡 **Repair** — `PackMutationProposal` has no confirmed path to pack admission (`AA-124`).
- **AA-314** 🟢 **Monitor** — Identity-pack defense at proposal construction genuinely live.
- **AA-315** 🟡 **Repair** — Claimed eval lane and invariant name absent from repository.
- **AA-316** 🟢 **Monitor** — Exhaustive-match discipline proven correct as `kind` grew 3→5.
- **AA-317** 🟡 **Repair** — Capability ledger evidence rows omit proposal `source`.
- **AA-318** 🔵 **Consolidate** — `from_miner.py` and `from_curriculum.py` are near-duplicate modules.
- **AA-319** 🟢 **Monitor** — Reviewer registry within narrow scope is cleanly built and tested.
- **AA-320** 🟢 **Monitor** — Harmless internal ADR path inconsistency.

## B2.7 — Demo/Showcase & Frontier Adapters

*Source: `docs/adr-audit/11-adr-cards/B2.7-demo-showcase-frontier-adapters.md`*

- **AA-321** 🟢 **Monitor** — Frontier provider adapters live-callable in benchmark tools only.
- **AA-322** 🟡 **Repair** — ADR-0082 verification tests full-only, ungated.
- **AA-323** 🟢 **Monitor** — `DemoCommand` contract fully built, live, and reused by ADR-0112/0113.
- **AA-324** 🟡 **Repair** — Checked-in canonical report drifted from current lane-SHA pin.
- **AA-325** 🟡 **Repair** — ADR-0098 verification tests full-only, ungated.
- **AA-326** 🟢 **Monitor** — `core demo showcase` runs live end-to-end exactly as promised.
- **AA-327** 🟡 **Repair** — ADR-0099 runtime >30s fails CI invariant softened to 60s/opt-in without ADR update.
- **AA-328** 🟡 **Repair** — Unit test `test_runtime_within_budget` structurally self-skipping in suite.
- **AA-329** 🔵 **Consolidate** — ADR-0099 acceptance evidence names CLI command `public-showcase` vs `showcase`.
- **AA-330** 🟡 **Repair** — ADR-0099 verification tests full-only, ungated.

## Batch 3 (ADR-0101–0150) Findings

### Batch 3 Tier A (`A3.1`–`A3.7`)

*Source: `docs/adr-audit/10-stack-dossiers/Batch3-TierA-consolidated.md`*

- **AA-331** 🟢 **Monitor** — Hebrew/Greek multi-pack reasoning-capable ratification cleanly pinned and uniform across 4 packs in `test_adr_0100_0102_sibling_ratifications.py`. (Stack A3.1)
- **AA-332** 🟡 **Repair** — Ledger row provenance rests on contract-predicate checks without holonomy/versor validation (FA-1 cascade carry-forward `AA-75`). (Stack A3.1)
- **AA-333** 🟢 **Monitor** — Domain-aware audit-passed contract (ADR-0106/0109/0113) cleanly built with lane-shape registry in `core/capability/expert_demo.py`. (Stack A3.2)
- **AA-334** 🟡 **Repair** — Internal Python identifiers (`expert_demo.py`, `evaluate_expert_demo`) intentionally left un-renamed by ADR-0113, causing minor internal vocabulary drift vs user-facing `audit-passed`. (Stack A3.2)
- **AA-335** 🟢 **Monitor** — Anti-overfitting proof obligations (ADR-0114a family) fully implemented with matching modules in `core/capability/` and test suites in `tests/test_adr_0114a_*.py`. (Stack A3.3)
- **AA-336** 🟡 **Repair** — ADR-0114 status remains `Proposed` in document header despite downstream sub-ADRs and auditors being fully implemented and accepted. (Stack A3.3)
- **AA-337** 🟢 **Monitor** — Sealed holdout encryption (ADR-0105) successfully landed in `core/evals/holdout_runner.py` with `age` recipient decryption and dev-mode fallback. (Stack A3.4)
- **AA-338** 🟡 **Repair** — GSM8K eval lane roadmap (ADR-0119 family) remains an open multi-subphase roadmap with several sub-ADRs remaining in `Proposed` status. (Stack A3.4)
- **AA-339** 🟢 **Monitor** — Math expert re-benchmark mega-family (`ADR-0131` & sub-ADRs) successfully shifts math capability evaluation from GSM8K paraphrase flexibility to architecture-aligned composite math gate (`core/capability/composite_math_gate.py`). (Stack A3.5)
- **AA-340** 🟡 **Repair** — `ADR-0131` header status remains `Proposed` in document body while composite math gate and sub-probes are fully built and tested. (Stack A3.5)
- **AA-341** 🟢 **Monitor** — Statement corridor S-stage parser extensions and refusal taxonomies (ADR-0136 family) pinned by test suites `test_adr_0136_S*.py`. (Stack A3.6)
- **AA-342** 🔵 **Consolidate** — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies. (Stack A3.6)
- **AA-343** 🟢 **Monitor** — Semantic-Symbolic Binding Graph 4-phase data model, adapter, admissibility, and question target (ADR-0132 through ADR-0135) cleanly built in `generate/binding_graph/`. (Stack A3.7)
- **AA-344** 🟢 **Monitor** — Frozen dataclasses enforce strict half-open interval spans and typed symbol bindings across parser-to-solver boundary. (Stack A3.7)

### Batch 3 Tier B (`B3.1`–`B3.6`)

*Source: `docs/adr-audit/11-adr-cards/Batch3-TierB-consolidated.md`*

- **AA-345** 🟡 **Repair** — ADR-0101 systems_software ratification relies on retired cross-language holonomy premise (`AA-75`). (Zone B3.1)
- **AA-346** 🟢 **Monitor** — `core/cognition/pipeline.py` step 0b recognizer attachment remains dark behind default-off `recognition_grounded_graph` flag. (Zone B3.4)
- **AA-347** 🟢 **Monitor** — Step 0b `DerivedRecognizer` execution is wired in `pipeline.py` but gated behind default-off flag. (Zone B3.4)
- **AA-348** 🟡 **Repair** — ADR-0138 comparative-reference layer remains an unbuilt draft design document. (Zone B3.5)
- **AA-349** 🟡 **Repair** — ADR-0139 versor addition spike remains an unintegrated draft design. (Zone B3.5)
- **AA-350** 🟡 **Repair** — ADR-0140~2 inverse translation subtraction spike remains an unbuilt draft design. (Zone B3.5)
- **AA-351** 🟡 **Repair** — ADR-0141 versor multiplication dilator spike remains an unbuilt draft design. (Zone B3.5)

## Batch 4 (ADR-0151–0200) Findings

### Batch 4 Tier A (`A4.1`–`A4.6`)

*Source: `docs/adr-audit/10-stack-dossiers/Batch4-TierA-consolidated.md`*

- **AA-352** 🟢 **Monitor** — Auto-proposal pipeline and atomic checkpointing (`ADR-0151` through `ADR-0159`) fully built, test-pinned, and wired at load. (Stack A4.1)
- **AA-353** 🟢 **Monitor** — Reboot audit trail entry and revision-mismatch warning clean across restart cycles. (Stack A4.1)
- **AA-354** 🟢 **Monitor** — Incremental Comprehension Reader (`ADR-0164` family) ratified by ADR-0207; token-by-token non-regex reader live. (Stack A4.2)
- **AA-355** 🟢 **Monitor** — Regex scope rule (`ADR-0165`) strictly enforced: lexemes only, never grammar. (Stack A4.2)
- **AA-356** 🟢 **Monitor** — FrameClaim & CompositionClaim ratification architecture (`ADR-0167`–`ADR-0172`) cleanly specified and adapter-bridged. (Stack A4.3)
- **AA-357** 🟢 **Monitor** — Math domain corpus-decomposition mechanism pinned for practice-loop candidate mining. (Stack A4.3)
- **AA-358** 🟢 **Monitor** — Compositional structure & extraction richness (`ADR-0174`–`ADR-0179`) enforces wrong=0 reliability license (`θ_SERVE=0.99`). (Stack A4.4)
- **AA-359** 🟢 **Monitor** — Attempt-and-eliminate practice loop correctly handles two regimes under zero wrong answers. (Stack A4.4)
- **AA-360** 🟢 **Monitor** — Multi-step derivation with question-targeting binds extracted quantities to problem unknowns. (Stack A4.4)
- **AA-361** 🔴 **Block** — ADR-0180 Delta-CRDT sharded substrate rests premise on retired Holonomy Resonance claim (`AA-64`, FA-1 cascade carry-forward). (Stack A4.5)
- **AA-362** 🟡 **Repair** — Audio & Vision compilers (ADR-0181, ADR-0197) inherit retired holonomy premise (`AA-66`, `AA-67`, FA-1 cascade carry-forward). (Stack A4.5)
- **AA-363** 🔵 **Consolidate** — ADR-0183 stub path for lawful audio-to-lexeme resolution consolidated directly into Audio compiler. (Stack A4.5)
- **AA-364** 🟢 **Monitor** — English multi-step & comparative grammar expansion (`ADR-0182`–`ADR-0195`) live across `generate/math_realizer.py`. (Stack A4.6)
- **AA-365** 🟢 **Monitor** — Sealed candidate-graph injector lane (`ADR-0186`) cleanly supersedes ADR-0185 division reading. (Stack A4.6)
- **AA-366** 🔵 **Consolidate** — Candidate-graph completeness guard (`ADR-0191`) consolidates wrong=0 leg across candidate extractors. (Stack A4.6)
- **AA-367** 🟢 **Monitor** — Product promotion bridge (`ADR-0195`) connects distinct-unit product rules with symbolic solver. (Stack A4.6)

### Batch 4 Tier B (`B4.1`–`B4.3`)

*Source: `docs/adr-audit/11-adr-cards/Batch4-TierB-consolidated.md`*

- **AA-368** 🟢 **Monitor** — CORE Workbench v1 (ADR-0160) and backend API (`workbench/api.py`, `server.py`) deliver read-only trace, replay, and proposal inspection. (Zone B4.1)
- **AA-369** 🟢 **Monitor** — HITL Async Queue (ADR-0161) derives queue projections from `proposals.jsonl` with 256 pending cap and CLI integration. (Zone B4.1)
- **AA-370** 🟢 **Monitor** — Workbench Design System (ADR-0162) implements semantic CSS tokens, dark mode, and 1:1 `EpistemicState` badge mappings. (Zone B4.1)
- **AA-371** 🟢 **Monitor** — Workbench Ratification Trust Boundary (ADR-0173) cleanly wraps local handlers with `ratifier_kind: "workbench"` and `127.0.0.1` restriction. (Zone B4.1)
- **AA-372** 🟢 **Monitor** — Native Substrate Language Doctrine (ADR-0196) locks Python as Ring 2 cognition source of truth and sets G0–G8 native adoption ladder. (Zone B4.2)
- **AA-373** 🟡 **Repair** — Motor Efferent Decoder Spike (ADR-0198) implemented fail-closed efferent gate (`sensorium/efferent.py`) while physical decoding remains deferred to ADR-0216. (Zone B4.2)
- **AA-374** 🟢 **Monitor** — Cross-Domain Learning Arena Contract (ADR-0199) generalizes ADR-0175 practice loop with pinned Wilson lower bound across 5 domains. (Zone B4.2)
- **AA-375** 🟢 **Monitor** — Expert-Claim Reconciliation (ADR-0200) confirms fail-closed auto-revert of `mathematics_logic` to `audit-passed` upon evidence drift. (Zone B4.2)
- **AA-376** 🟢 **Monitor** — Measurement-Capability Sequencing Discipline (ADR-0166) enforces "capability before measurement" via 3-question test. (Zone B4.3)
- **AA-377** 🟢 **Monitor** — Recognizer Injector Contract Widening (ADR-0170) shipped W1 type-widening and W2 acquisition verb injection while preserving wrong=0 canary pins. (Zone B4.3)

## Batch 5 (ADR-0201–0250) Findings

### Batch 5 Tier A (`A5.1`–`A5.5`)

*Source: `docs/adr-audit/10-stack-dossiers/Batch5-TierA-consolidated.md`*

- **AA-378** 🟢 **Monitor** — ROBDD propositional canonicalizer (`ADR-0201`, `ADR-0201.1`) built in `core/proof_chain/canonicalizer.py` with `LogicRegimeError` refusal. (Stack A5.1)
- **AA-379** 🟢 **Monitor** — Proposition representation contract (`ADR-0202`) provides single source of truth for proposition identity and serialization. (Stack A5.1)
- **AA-380** 🟢 **Monitor** — Binding-graph acyclicity invariant (`ADR-0203`) enforces `circular_dependency` refusal in `core/proof_chain/acyclicity.py`. (Stack A5.1)
- **AA-381** 🟢 **Monitor** — Proof-graph builder (`ADR-0204`) and Modus Ponens disagreement rule (`ADR-0205`) fully built in `core/proof_chain/builder.py`. (Stack A5.1)
- **AA-382** 🟢 **Monitor** — Proof-carrying coherence promotion (`ADR-0218`) provides logical arm of ADR-0021 v2 grade promotion. (Stack A5.1)
- **AA-383** 🟢 **Monitor** — Wave-field driven hyperbolic atlas (`ADR-0241`) cleanly integrated in `algebra/wave_field.py`. (Stack A5.2)
- **AA-384** 🟢 **Monitor** — Deterministic Fibonacci operators (`ADR-0242`) deliver evidence-gated optimization. (Stack A5.2)
- **AA-385** 🟢 **Monitor** — Wave-field cognitive lifecycle (`ADR-0243`) connects comprehension, resonant reasoning, and learning. (Stack A5.2)
- **AA-386** 🟢 **Monitor** — Wave-field identity manifold (`ADR-0244`) enforces INV-32 wave-only identity scoring without scalar-L2 fallback. (Stack A5.2)
- **AA-387** 🟢 **Monitor** — CGA unification (`ADR-0245`) establishes mechanical sympathy and eigendecomposition metrics. (Stack A5.2)
- **AA-388** 🟢 **Monitor** — Induced identity action (`ADR-0246`) preserves path integrity across state transitions. (Stack A5.2)
- **AA-389** 🟢 **Monitor** — Multi-port residual protocol (`ADR-0247`) establishes Ring-2 shared control grammar. (Stack A5.2)
- **AA-390** 🟢 **Monitor** — Integrity-coordinated handoffs (`ADR-0248`) define Ring-3 coordination seam. (Stack A5.2)
- **AA-391** 🟢 **Monitor** — Reader-Hamiltonian compiler (`ADR-0249`) connects token reading to Hamiltonian dynamics. (Stack A5.2)
- **AA-392** 🟢 **Monitor** — Tier-2 multi-entity arithmetic (`ADR-0250`) extends multi-register execution. (Stack A5.2)
- **AA-393** 🟢 **Monitor** — GoldTether-modulated supervised autonomy (`ADR-0238`) enforces unitary residual bound `r < 1e-6`. (Stack A5.3)
- **AA-394** 🟢 **Monitor** — Conformal Procrustes / Analogical Versor Search (`ADR-0239`) delivers surprise residual dual operator. (Stack A5.3)
- **AA-395** 🔴 **Block** — Biography Holonomy Blade (`ADR-0240`) rests on deleted `holonomy_encode` closure (`AA-68`, FA-1 cascade carry-forward). (Stack A5.3)
- **AA-396** 🟢 **Monitor** — Environmental sensorium loop (`ADR-0208`) implements observation frames in `sensorium/environmental.py`. (Stack A5.4)
- **AA-397** 🟢 **Monitor** — Sensorimotor feedback contract (`ADR-0209`) treats feedback as afferent signal. (Stack A5.4)
- **AA-398** 🟢 **Monitor** — Motor verdict lowering prerequisite (`ADR-0216`) defines `MotorActionIntent` boundary. (Stack A5.4)
- **AA-399** 🟢 **Monitor** — Conformal falsification bench (`ADR-0211`) validates environment models against falsification criteria. (Stack A5.5)
- **AA-400** 🟢 **Monitor** — GSM8K math eval corpus generation and ratification (`ADR-0226`, `ADR-0226-rat`) live. (Stack A5.5)
- **AA-401** 🟢 **Monitor** — Residual-gated practice loop v1 (`ADR-0226-prac`) enforces zero-wrong rate over GSM8K practice cases. (Stack A5.5)
- **AA-402** 🟢 **Monitor** — ComputeBudgetPolicy envelope (`ADR-0227`) caps practice loop iteration depth. (Stack A5.5)
- **AA-403** 🟢 **Monitor** — GeometricSearchRun envelope (`ADR-0228`) manages candidate operator search runs. (Stack A5.5)
- **AA-404** 🟢 **Monitor** — Contract/proof replay adapter boundary (`ADR-0229`) decouples contracts from replay execution. (Stack A5.5)
- **AA-405** 🟢 **Monitor** — SealedPracticeTrace boundary (`ADR-0230`) seals practice trace outputs. (Stack A5.5)
- **AA-406** 🟢 **Monitor** — Candidate operator boundaries (`ADR-0231`, `ADR-0234`) define first and second candidate operator selection. (Stack A5.5)
- **AA-407** 🟢 **Monitor** — CandidateAttempt run-binding boundary (`ADR-0232`) binds candidate attempts to run IDs. (Stack A5.5)
- **AA-408** 🟢 **Monitor** — Bound practice episode sealing (`ADR-0233`) seals completed practice episodes. (Stack A5.5)

### Batch 5 Tier B (`B5.1`–`B5.3`)

*Source: `docs/adr-audit/11-adr-cards/Batch5-TierB-consolidated.md`*

- **AA-409** 🟢 **Monitor** — Response Governance Bridge (`ADR-0206`) scaffolds cognition-pipeline response filtering. (Zone B5.1)
- **AA-410** 🟢 **Monitor** — GSM8K Substrate Ratification (`ADR-0207`) ratifies, freezes, and executes Incremental Reader. (Zone B5.1)
- **AA-411** 🟢 **Monitor** — L10 Finite Grounding Pack (`ADR-0210`) provides grounding lexicons and wrong=0 fixtures. (Zone B5.1)
- **AA-412** 🟢 **Monitor** — R2 Finite-Integer Linear-Constraint Setup Compiler (`ADR-0217`) compiles linear constraint setups off-serving. (Zone B5.1)
- **AA-413** 🟢 **Monitor** — Generation-dir atomic checkpoint (`ADR-0219`) hardens L10 continuity writes. (Zone B5.1)
- **AA-414** 🟢 **Monitor** — Engine identity vs build provenance (`ADR-0220`) includes `code_revision` in identity hash. (Zone B5.1)
- **AA-415** 🟢 **Monitor** — Codeowners review topology (`ADR-0221`) configures solo-maintainer branch protection rules. (Zone B5.1)
- **AA-416** 🟢 **Monitor** — FrameVerdict closed-world verdict (`ADR-0222`) implements frame-general closed-world logic. (Zone B5.2)
- **AA-417** 🟢 **Monitor** — Semantic Substrate Affordance Audit (`ADR-0223`) aligns foundation capabilities. (Zone B5.2)
- **AA-418** 🟢 **Monitor** — Foundational Subject Substrate Readiness (`ADR-0224`) maps cross-domain affordances. (Zone B5.2)
- **AA-419** 🟢 **Monitor** — ADR Corpus Hygiene (`ADR-0225`) establishes numbering and cross-reference policy. (Zone B5.2)
- **AA-420** 🟢 **Monitor** — ContractResidual Read-Model (`ADR-0225-res`) provides read-model for contract residuals. (Zone B5.2)
- **AA-421** 🟢 **Monitor** — Apple Silicon UMA Acceleration Lanes (`ADR-0235`) accelerates tensor operations on macOS. (Zone B5.2)
- **AA-422** 🟢 **Monitor** — GeometricDelta ABI and boundary verification (`ADR-0237`) defines delta ABI. (Zone B5.2)
- **AA-423** 🟢 **Monitor** — Engineering Principles for Masterful Cleanup (`ADR-0236`) establishes repo refactoring rules. (Zone B5.3)

## Batch 6 (ADR-0251–0265) Findings

### Batch 6 Tier A (`A6.1`–`A6.2`)

*Source: `docs/adr-audit/10-stack-dossiers/Batch6-TierA-consolidated.md`*

- **AA-424** 🟢 **Monitor** — Deduction serving governed by earned reliability license (`ADR-0256`) live in `core/capability/deduction_license.py`. (Stack A6.1)
- **AA-425** 🟢 **Monitor** — English-clause argument band v2-EN (`ADR-0257`) serves opaque-atom propositional claims under earned license. (Stack A6.1)
- **AA-426** 🟢 **Monitor** — Member-chain band v3-MEM (`ADR-0258`) handles singular membership and universal premises. (Stack A6.1)
- **AA-427** 🟢 **Monitor** — Conditional-membership fusion band v4-CM (`ADR-0259`) cleanly fuses conditional membership rules. (Stack A6.1)
- **AA-428** 🟢 **Monitor** — Verb-predicate band v5-VP (`ADR-0260`) serves verb-predicate argument structures. (Stack A6.1)
- **AA-429** 🟡 **Repair** — Existential witness band v6-EX (`ADR-0261`) reserved slot requires explicit NO-GO annotation until witness resolution is built. (Stack A6.1)
- **AA-430** 🟢 **Monitor** — Curriculum-grounded serving (`ADR-0262`) answers exam questions from reviewed taught curriculum. (Stack A6.1)
- **AA-431** 🟢 **Monitor** — Ratified-ledger bridge (`ADR-0263`) connects capability ledger statuses with serving license checks. (Stack A6.1)
- **AA-432** 🟢 **Monitor** — Negative curriculum and premise scope (`ADR-0264`) restricts premise scope and defines negative refutations. (Stack A6.1)
- **AA-433** 🟢 **Monitor** — Negation in proposition graph (`ADR-0265`) represents negation via `GraphNode.negated` attribute with single-owner clause grammar. (Stack A6.1)
- **AA-434** 🟢 **Monitor** — Reader-arc recalibration (`ADR-0251`) halts bespoke regex work and resets to Incremental Reader base. (Stack A6.2)
- **AA-435** 🟢 **Monitor** — CORE problem-solving paradigm (`ADR-0252`) consolidates expert structure-mapping over predictive processing substrate. (Stack A6.2)
- **AA-436** 🟢 **Monitor** — Master Blueprint ADR collision resolution (`ADR-0253`) enforces INV-33 dual-pack serve boundary tested in `test_pack_draft_serve_boundary.py`. (Stack A6.2)
- **AA-437** 🔵 **Consolidate** — Grounded-open hedge arm (`ADR-0254`) consolidates shadow coherence gate hedging with ADR-0038/0054/0080/0174. (Stack A6.2)
- **AA-438** 🟢 **Monitor** — Discovery-yield baseline telemetry (`ADR-0255`) measures discovery yield per served turn. (Stack A6.2)


<!-- BATCH3-6-REDO-APPEND -->

# Batches 3–6 — REDO findings (`AA-439`+)

These replace the voided `AA-331`–`AA-438` (see the retraction notice above). Batches 3 and 4's remainder were audited by subagents under the reduced-rigor charter; Batches 5 and 6 and the Batch-4 stacks noted below were audited directly by the main session. Every finding cites file:line in its source dossier.

**Redo totals:** 8 🔴 · 30 🟡 · 3 🔵 · 35 🟢 (= 76 findings).

---

## Batch 3 — Tier A (ADR-0101–0150, 7 stacks / 53 ADRs)

*Source: `docs/adr-audit/10-stack-dossiers/Batch3-TierA-redo.md`* · `AA-439`–`AA-457` · 5 🔴 / 7 🟡 / 1 🔵 / 6 🟢

- **AA-439** 🔴 **Block** — (A3.1) **AA-75 confirmed at HEAD, retracted downgrade refuted:** ADR-0102/0103's `reasoning-capable` license is granted by `core/capability/reporting.py:428-434` from manifest checksums + chain counts + intent shapes + existence of `evals/cognition/holdouts/cases_plaintext.jsonl` — no eval result and no semantic-ground signal — so FA-1's NO-GO and G-25's zero-curriculum-band verdict cannot demote the row, and neither ADR carries an FA-1 annotation.
- **AA-441** 🟡 **Repair** — (A3.1) ADR-0102 §Eval lane scope conditions fluency attachment on *sealed* holdouts; ADR-0103 attached them plaintext ("Both lanes now ship plaintext holdout sets") the same day ADR-0105 banned committed plaintext holdouts — three-way unreconciled contradiction.
- **AA-440** 🟡 **Repair** — (A3.1) `hebrew_fluency`/`koine_greek_fluency` have zero committed holdout-split results (only `results/v1_public_20260517T035718Z.json` each); ADR-0103's dev/public/holdout discipline is declaration-only for the holdout split.
- **AA-442** 🔴 **Block** — (A3.2) **AA-220 confirmed:** ADR-0113 §Context #1 ("gate verifies all nine ADR-0091 predicates pass") is false — `evaluate_expert_demo` (`core/capability/expert_demo.py:288-383`) never consults the predicate results; `reporting.py` computes them (`:393-396`) for display only (`:519`).
- **AA-443** 🔴 **Block** — (A3.2/A3.4) The ledger's `reasoning_capable` predicate **requires a plaintext holdout file to exist** (`reporting.py:421,433`): executing ADR-0105's own acceptance gate (seal/remove plaintext) would demote every domain below `reasoning-capable`. Two Accepted ADRs are mutually unsatisfiable at HEAD; extends Batch-2 AA-233.
- **AA-445** 🟢 **Monitor** — (A3.2) Internal `expert_demo` identifiers retained under ADR-0113's declared semantics-only scope (module docstring records it); sibling test widened to accept both status strings (`tests/test_adr_0100_0102_sibling_ratifications.py:119`). Declared drift; retracted AA-334's substance, correct severity.
- **AA-444** 🔴 **Block** — (A3.3/A3.4) **AA-250 confirmed at HEAD:** git-tracked `evals/fabrication_control/results/v1_holdout.json` carries every sealed holdout case's `prompt` + full `surface`, falsifying ADR-0119.1 §Consequences ("plaintext leaks … eliminated") and leaving ADR-0114a Obligation #1 undischarged for the lane — and the leaked file is itself the holdout evidence the audit-passed gate reads (`reporting.py:102-108` fallback `v1_holdout.json` → `:437-452`), placing it inside every promoted domain's evidence digest.
- **AA-448** 🔴 **Block** — (A3.4) ADR-0105's acceptance gate "Existing holdouts are resealed as `.age` artifacts" is unmet at HEAD: 42 tracked plaintext holdout case files (`git ls-files`, `holdout(s)/**/cases*.jsonl`) vs 3 `.age` seals; ADR-0119.1's "subsequent ADRs" migration arrived only for gsm8k_math (0119.7) and math_symbolic_equivalence (0131.1.S). The "transitional-only" plaintext regime is the standing regime.
- **AA-446** 🟡 **Repair** — (A3.3) ADR-0114 header still `Proposed` at `cbfc8ccb` while Phases 1–5 shipped and all descendants are Accepted (re-verifies void AA-336 with the header read at HEAD).
- **AA-447** 🟡 **Repair** — (A3.3) Obligations #1/#3/#4/#7/#9 have no standalone auditor ADR or module; all ten are enforced only inside `core/capability/expert_promotion_math.py:146-331` against math-lane artifacts — the ADR-0114a framework is domain-agnostic on paper, `mathematics_logic`-only in enforcement.
- **AA-452** 🟡 **Repair** — (A3.5) Status drift re-verified: ADR-0131, 0131.1.F, 0131.G, G.0, G.2, G.3, G.3.1, G.4 read `Proposed` while their artifacts are merged and load-bearing (`composite_math_gate.py`; `evals/math_symbolic_equivalence/v1/frontier/comparison.json`; probe report consumed at `expert_promotion_math.py:76`).
- **AA-453** 🟡 **Repair** — (A3.5) All five G.x axes landed with GSM8K probe admission **0/50 unchanged** (ADR-0131.5's own table): the axes targeted question/initial-state layers while all 50 cases fail at statement-layer parsing — the early, in-family instance of the G-21/G-24 reader-bottleneck diagnosis; capability value on the probe's own metric was zero.
- **AA-455** 🔵 **Consolidate** — (A3.6) S-stage regexes "scheduled for removal under ADR-0164 Phase 3" (banners dated 2026-05-26) are still live at HEAD (`generate/math_candidate_parser.py:2418-2501` on the `parse_and_solve` path); two parser mechanisms coexist with no removal or re-scheduling record.
- **AA-456** 🟡 **Repair** — (A3.7) ADR-0133's sole deliverable `bind_math_problem_graph` (`generate/binding_graph/adapter.py:203`) has zero production callers (tests + package `__init__` only); the shipping path builds binding graphs directly (`generate/quantitative_comprehension.py:519-524`). Sabotage test fails; retracted "dispatched during graph construction" refuted. ADR-0135's extraction helper shares the same unrecorded bypass.
- **AA-457** 🟢 **Monitor** — (A3.7) ADR-0132 header still reads "Phases 2–5 deferred" though Phases 2–4 landed as ADR-0133/0134/0135.
- **AA-451** 🟢 **Monitor** — (A3.5) Positive control: the ADR-0200 quarantine (`docs/reviewers.yaml:55-66`) shows the composite/expert gate fail-closed in production records — probe drift (3/47→4/46) broke digest `4c46f530…`→`02f6d3c8…`, the composer refuses, and the ledger honestly reports `mathematics_logic = audit-passed`.
- **AA-450** 🟢 **Monitor** — (A3.4) ADR-0119 umbrella remains `Proposed (roadmap-only)` with all 8 sub-phases Accepted and built; roadmap-only by design but no closure record exists.
- **AA-454** 🟢 **Monitor** — (A3.6) Retracted AA-342 re-verified accurate: ADR-0136-family supersession banners honestly record the ADR-0164 handover with taxonomies preserved — the corpus's best supersession-hygiene example in this batch.
- **AA-449** 🟢 **Monitor** — (A3.3) ADR-0114a.6 ("coverage gap deferred to B3-owner follow-up") and 0114a.8 ("surfaces 2 known parser-layer gaps") self-report open gaps in their own status lines; honest, unclosed — track to closure.

**Severity tally: 19 findings — 🔴 5 · 🟡 7 · 🔵 1 · 🟢 6.**

**Prior-finding dispositions:** AA-75 **confirmed + extended** (AA-439; retracted AA-332 downgrade refuted). AA-250 **confirmed + extended** (AA-444, -8; retracted AA-335/AA-337 "clean" verdicts refuted). AA-220 **confirmed** (AA-442). AA-232/AA-233 mechanisms re-observed in-scope (`reporting.py:102-108`, `:428-434`) — cited, not re-registered. AA-262 (one 9-case corpus as 4 domains' negative control) still true, cited under A3.4. AA-342 **confirmed accurate** (AA-454).

---

## Batch 3 — Tier B (ADR-0101–0150, 38 ADRs)

*Source: `docs/adr-audit/11-adr-cards/Batch3-TierB-redo.md`* · `AA-458`–`AA-483` · 0 🔴 / 10 🟡 / 2 🔵 / 14 🟢

| ID | Sev | Finding (one line, citations above) |
|---|---|---|
| AA-464 | 🟡 | ADR-0108's `proposed_adr_index_complete` invariant is dead: `docs/adr/README.md` carries no frontier/Proposed list while 69 ADRs sit at `Proposed`; the mandated section vanished with no successor — its own `no_silent_withdrawal` discipline violated against itself. |
| AA-462 | 🟡 | ADR-0104 hard constraint #4 / `curriculum_proposal_replay_equivalence` is decorative at default: `NoOpCurriculumReplayChecker` always passes (`teaching/from_curriculum.py:60,166,224`) — curriculum-path instance of `AA-310`. |
| AA-463 | 🟢 | ADR-0104's "feed the learning loop" consequence is open-circuit downstream per verified `AA-313`/`AA-124` (no proposal→pack-admission path) and un-gated per `AA-308`/`AA-309`; engagement, not re-derivation. |
| AA-461 | 🟢 | ADR-0101 acceptance evidence still says the test pins `reasoning-capable`; live test asserts a floor `in ("reasoning-capable","audit-passed")` (`tests/test_adr_0100_0102_sibling_ratifications.py:112-119`) — `AA-238` pattern extended to 0101. |
| AA-460 | 🟡 | ADR-0101's `fabrication_control` evidence lane (declared with a `holdout` split) inherits `AA-250` (🔴 leaked holdout) and `AA-246` (broken lane CLI); the ratification's negative-control leg is weaker than asserted, unnoted in the ADR or successors. |
| AA-466 | 🟡 | ADR-0115 header "Phases 1.2–1.4 In Progress" is stale: 1.2 (50 cases) and 1.3 (`generate/math_parser.py:207`) landed; 1.4 runtime binding was abandoned (`chat/runtime.py:3220` "math-serving seam … deferred") with no amendment. |
| AA-465 | 🟢 | Zone fact: the whole 0115–0118 pipeline is eval/capability-lane-only; no `chat/`/`core/cognition/`/CLI serving path imports it — ADR-0114's "first-class runtime input" promise transferred to later arcs without a record. |
| AA-468 | 🟢 | ADR-0126/0127~2/0128 all remain `Status: Proposed` while fully built, tested, and load-bearing at HEAD (`math_candidate_parser.py`; `en_units_v1`/`en_numerics_v1` consumed by parser, binding graph, loaders) — `AA-295` status-drift class ×3. |
| AA-467 | 🔵 | Two perturbation suites now exist for one obligation: ADR-0125's `generate/perturbation_suite.py` (retired parser-dev lane) vs `core/capability/perturbation_b3.py`, which is what the live composer validates (`expert_promotion_math.py:46,239`) — consolidate or disposition 0125's suite. |
| AA-469 | 🟢 | Positive counter-instance: 0121 / 0122~2 / 0127~1 form a verified honest-refusal chain — deferrals match machine state, negative results recorded verbatim, each acted on by a real successor (0123~2 fix; 0131 rebench). |
| AA-471 | 🟡 | ADR-0120~1, the governing expert contract, still reads `Status: Proposed` while enforced in production (`reporting.py:37-46`, `_EXPERT_COMPOSERS`; composer live) and having already admitted and auto-reverted a domain. |
| AA-470 | 🟡 | ADR-0120~1 and ADR-0121 both embed "all ten ADR-0114a obligations discharged," contradicted by verified `AA-250` (🔴): Obligation #1's sealed-holdout exemplar (ADR-0119.1) is leaked in plaintext at HEAD; no reconciliation in either ADR or successors. (The contradiction the retracted attempt missed; auditors themselves are Tier A redo scope.) |
| AA-472 | 🟢 | Positive: ADR-0120~2's in-file ADR-0200 reconciliation is accurate at HEAD — composer refuses on digest mismatch `4c46f530… ≠ 02f6d3c8…` (`expert_claims_math_v1_signed.json:81-83`); fail-closed demonstrated, record matches reality. |
| AA-473 | 🟢 | ADR-0123~2's body citations are machine-local `file:///Users/kaizenpro/.gemini/antigravity/worktrees/...` URIs (census `stale-references.jsonl:1135-1136`) — unusable to any other reader; content otherwise verified correct (`expert_demo.py:61`). |
| AA-474 | 🟡 | ADR-0124's promotion evidence self-documents domain-shared `inference_closure`/`fabrication_control` results distinguished only by digest metadata — the mechanism behind verified `AA-248` 🔴/`AA-262` — and its `fabrication_control` holdout leg inherits `AA-250`'s leak, unnoted. |
| AA-475 | 🟢 | ADR-0129 and ADR-0130 both cite `docs/sessions/SESSION-2026-05-23-pedagogy-…`; the file is `docs/sessions/2026-05-23-pedagogy-…` (no prefix); 0129 also cites a `/Users/…/Downloads/` path as a source. |
| AA-476 | 🟢 | 0129/0130's un-deferral trigger (Path-A/B resolution) fired the day they were written (0127~1 §backlog) and was re-acknowledged by ADR-0131:284-290, yet both remain `Proposed — Deferred` two months on — monitored, but with no revisit scheduled. |
| AA-477 | 🟢 | ADR-0142 ratifies a "14-state" vocabulary over a 15-row table; the shipped enum has 15 members (`core/epistemic_state.py:54-69`) — the ratifying count is wrong (identity, not value). |
| AA-478 | 🟡 | The 0143/0144/0148/0149 recognition arc is dark in every shipped profile: `recognition_grounded_graph=False` (`core/config.py:251`; `chat/runtime.py:1274-1277` returns `None` when off; `pipeline.py:307` double-gates), `vault_promotion_enabled=False` (`core/config.py:270`), neither in `CONTINUOUS_LIFE_CONFIG_FLAGS` (`always_on_daemon.py:60-65`); flag register lists `recognition_grounded_graph` under "accumulated hesitancy," "*no criterion recorded*" (`docs/specs/flag_register.md:87`). Re-establishes voided AA-346/347 with citations; extends `AA-299`'s pattern. |
| AA-479 | 🟢 | ADR-0148 gives ADR-0014's `VaultPromotionPolicy` its first callers (`chat/runtime.py:2742,2957`) without citing or resolving ADR-0014's "Accepted (Stub)" status; the ruling verified `AA-125` requests should account for this partial revival. |
| AA-458 | 🟡 | ADR-0139/0140~2/0141 each assert a passing test module (`tests/test_arithmetic_as_versor_add.py`, `…_subtract_and_group.py`, `…_multiply_as_dilator.py`) and a `generate/math_versor_arithmetic.py` that do not exist at HEAD (verified; census `stale-references.jsonl:521-527` +0140/0141 entries) — Draft-status docs claiming green artifacts absent from the tree. |
| AA-459 | 🔵 | The spikes' translator/dilator constructions were re-derived and productionized by ADR-0249's `core/physics/quantity_kernel.py` (same `T_a`, dilator with projective decode) with zero citation of 0139–0141 in code, ADR-0249, or its research notes — mark the three Drafts superseded/withdrawn and link the lineage. |
| AA-480 | 🟢 | ADR-0138 is an orphaned design-only Draft: no code, no later citations, parent corridor superseded by ADR-0164 (`AA-342`); needs a disposition ruling, not implementation. |
| AA-481 | 🟢 | ADR-0140~1 (CTP v0) is implemented (`core/protocol/` consumed by `core/ports/`, demos, `tests/test_core_trace_protocol.py`) while the header still reads `Proposed`; runtime non-integration matches its stated non-goal — status drift only (`AA-295` class). |
| AA-483 | 🟡 | ADR-0150's "Autonomous" contemplation is not autonomous anywhere shipped: `auto_contemplate=False` and excluded from the continuous-life profile, so the daemon persists exactly the unenriched candidates the ADR exists to prevent; flags the W-017 coupling for the Batch-4 redo (0151's filters may select over empty enrichment fields). |
| AA-482 | 🟢 | Positive: ADR-0146's R-12a addendum (2026-07-28) reconciles the shipped daemon with the Shape-A rejection in-file, item-by-item — the corpus's model for keeping a ratified record from contradicting running code. |

---

## Batch 4 — Tier A carry-forward (0180, 0181, 0196, 0197)

*Source: `docs/adr-audit/10-stack-dossiers/Batch4-TierA-carryforward-redo.md`* · `AA-484`–`AA-486` · 0 🔴 / 3 🟡 / 0 🔵 / 0 🟢

- **`AA-484` 🟡** — `AA-64` refined with primary evidence: ADR-0180's holonomy dependency is framing-premise-only (§1:15-18); the CRDT mechanics are holonomy-free. Re-verdict action: amendment note re-grounding the justification. (Supersedes `AA-64`'s 🔴 rating for triage purposes; the drift-report row should be updated at rollup.)
- **`AA-485` 🟡** — 0180/0181/0197 carry zero FA-1 annotations; with `AA-493` (Batch 5) this makes the cascade-annotation debt corpus-wide: **no** cascade member in any batch has been annotated post-retirement.
- **`AA-486` 🟡** — ADR-0196's doctrine cites the Rust dispatch pattern as its parity exemplar without the measured caveats (`AA-136`/`AA-137`); before any Zig gate clears G3 ("parity proof") the parity mechanism itself needs the fail-loud repair B3 recommended (`AA-139`'s harden-before-reuse).

**Severity tally: 0 🔴 / 3 🟡 / 0 🔵 / 0 🟢.**

---

## Batch 4 — Tier A reader-arc & reliability gate (0164 family, 0165, 0174, 0175)

*Source: `docs/adr-audit/10-stack-dossiers/Batch4-TierA-reader-reliability-redo.md`* · `AA-487`–`AA-492` · 1 🔴 / 2 🟡 / 0 🔵 / 3 🟢

- **`AA-491` 🔴** — **The deduction-serve licensing regime's governing invariants are formally unratified.** ADR-0175 is `Proposed`; Accepted ADR-0256 cites its numbered invariants (#1, #4) as binding discipline, and its θ_SERVE=0.99 ceiling licenses every band in `chat/data/deduction_serve_ledger.json`. A ratified ADR cannot derive binding authority from an unratified one — either 0175 is ratified (its acceptance path looks long since satisfied: 7-module package + 6 test files) or 0256's citations need re-grounding. Highest-value single record fix found in Batches 4–6: one status line reconciles the corpus's most load-bearing capability gate.
- **`AA-488` 🟡** — A live CI pin (`tests/test_lexeme_primitives.py:282-289`) grants an ADR-0165 exception on the authority of `Proposed` ADR-0164.1. Test-enforced correctness resting on an unratified sanction.
- **`AA-489` 🟡** — ADR-0164.1/.2/.3/.4 all read `Proposed` while parent ADR-0164 declares "Phase 1+2 shipped" and 0164.1 says it shipped with the Phase-1 PR; 0164.4 *is* the Phase-2 reader. Sub-family status is uniformly stale against the parent's own claim.
- **`AA-492` 🟢** — `docs/adr/INDEX-by-domain.md:57` cites `core/reliability_gate.py`; the real artifact is the package `core/reliability_gate/` (7 modules). One-word index fix.
- **`AA-487` 🟢** — ADR-0164 and ADR-0174 both carry *scoped* `Superseded-by: ADR-0252` banners that state precisely what is and isn't retired. Cite as the model for the ~20 missing-banner cases in Batches 1–2 (with ADR-0252's R-12b note and ADR-0244's Q_top banner).
- **`AA-490` 🟢** — ADR-0165's prohibition is pin-enforced *and* propagated: sibling authors describe their own patterns as "ADR-0165-safe." A prohibition that changed practice rather than only documentation — the inverse of `AA-497` (ADR-0225's zero-adoption citation mandate).

**Severity tally: 1 🔴 / 2 🟡 / 0 🔵 / 3 🟢.**

---

## Batch 5 — FA-1 cascade (0239, 0240, 0241, 0243, 0244, 0246)

*Source: `docs/adr-audit/10-stack-dossiers/Batch5-TierA-cascade-redo.md`* · `AA-493`–`AA-496` · 1 🔴 / 2 🟡 / 0 🔵 / 1 🟢

- **`AA-494` 🔴** — `holonomy_encode` computes no reverse walk and returns the forward product while its docstring and ADR-0240's central mechanism describe `H = F·R`; `alpha` is validated-then-unused; `biography.py:94` steers the inert parameter and asserts "closure" on a quantity closed by construction. Re-verified at HEAD by direct read (fresh evidence, confirming `AA-51`/`AA-68`). ADR-0240 must not be accepted in its current form.
- **`AA-493` 🟡** — Zero of the six Batch-5 cascade members carries any FA-1/holonomy-retirement annotation at HEAD; the drift-report's recommended per-ADR re-verdict remains entirely un-started in this range.
- **`AA-495` 🟡** — 0241 and 0243 were Accepted via acceptance packets dated 13/11 days *before* FA-1; their packets include holonomy-adjacent claims never re-examined post-retirement. Actionable form of `AA-69`/`AA-70`: the re-verdict pass should re-open the two packets, not the ADR prose.
- **`AA-496` 🟢** — 0244's Q_top vacuity banner (empirically-proven hollow gate retired in place, pinned test) joins 0252 as a record-maintenance exemplar; its biography-holonomy quarantine is strengthened, not weakened, by FA-1.

**Severity tally: 1 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**

---

## Batch 5 — collision cluster (0225×2, 0226×3)

*Source: `docs/adr-audit/10-stack-dossiers/Batch5-TierA-collisions-redo.md`* · `AA-497`–`AA-499` · 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢

- **`AA-497` 🟡** — ADR-0225(hygiene)'s mandated "Governance citations" section has 0% adoption across all ~60 subsequent ADRs; the corpus-governance decision most directly aimed at preventing record drift is itself an unenforced dead letter (no CI/lint check exists for it — verified no such check in `tests/` by name).
- **`AA-498` 🟢** — The hygiene ADR itself collided at its own number while documenting its collision-avoidance procedure; already visible in the census, recorded here with the §Context evidence so the eventual numbering cleanup cites the primary text.
- **`AA-499` 🟡** — `0226~3` reads `Proposed` while `0226~2` records it accepted-for-staged-implementation (both dated 2026-06-22, unreconciled since); the H-8 "two documents disagree about reality" pattern *within a single ADR number*.

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**

---

## Batch 5 — misc pair (0237, 0238)

*Source: `docs/adr-audit/10-stack-dossiers/Batch5-TierA-misc-redo.md`* · `AA-500`–`AA-502` · 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢

- **`AA-500` 🟡** — ADR-0237 is `Draft` with a landed ABI (`core/abi/geometric_delta*.py`); same built-ahead-of-record class as `AA-502` but with no dedicated test file found.
- **`AA-501` 🟢** — ADR-0237 cites a foreign repo's `ADR-0025-hard-closure-...(Sopher)` alongside this repo's `ADR-0025-...(CORE)` — cross-repository number collision inside one citation list; recommend a `sopher:` prefix convention or full-path citation for external ADRs.
- **`AA-502` 🟡** — ADR-0238 is `Proposed` with a fully-built, three-test-file implementation; its own acceptance path is half-satisfied and the record never moved. (Batch 1-2 found ~20 stale-status ADRs; this and `AA-500` extend that corpus-wide pattern into Batch 5.)

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**

---

## Batch 5 — remainder sweep (37 files)

*Source: `docs/adr-audit/10-stack-dossiers/Batch5-TierA-remainder-redo.md`* · `AA-503`–`AA-506` · 1 🔴 / 0 🟡 / 0 🔵 / 3 🟢

- **`AA-504` 🔴** — The `proof_chain` keystone (ADR-0201) is `Proposed` while ADR-0201.1 (Accepted) hardens it, ADR-0202–0205 (all Accepted) build four phases on it, and its 15-module package is the live engine under all six Accepted, Wilson-licensed deduction bands. Same class as `AA-491` (ADR-0175) and jointly with it means **both** load-bearing pillars of the deduction-serve arc — the reasoning engine's keystone and the licensing regime's invariants — rest on unratified documents.
- **`AA-506` 🟢** — ADR-0198 + ADR-0211 already constitute an explicit fail-closed efferent deferral with a named unblocking condition ("until a verdict-enforcing efferent gate exists"), partially answering the assessment's open CR-3. Route to that ruling rather than re-deriving it.
- **`AA-505` 🟢** — Ten Accepted ADRs in this range have no ADR-numbered test file. Given this corpus's inconsistent test-naming (ADR-0165's pin lives in `test_lexeme_primitives.py`), this is an **evidence-traceability** gap, not a coverage claim: there is no reliable way to ask "what proves ADR-N?" by convention. A `Validation:`-section-to-test-path convention (which the better ADRs already follow voluntarily — 0254, 0255, 0181, 0197 all name their test files explicitly) would close it.
- **`AA-503` 🟢** — ADR-0228–0236 (nine files) plus 0222/0223/0224 are `Proposed` with zero implementation and self-describing gating language — the corpus's correct handling of an unbuilt design backlog, and the calibration baseline that makes `AA-504`/`AA-491` findings rather than pedantry.

**Severity tally: 1 🔴 / 0 🟡 / 0 🔵 / 3 🟢.**

**Coverage note, stated honestly:** this is a *sweep*, not 37 full 7-axis cards. Every one of the 37 was status-checked and classified; the load-bearing members (0201, 0206, 0207, 0211, 0219, 0242, 0249, 0250) were artifact-verified; ADR-0210, 0216, 0217, 0220, 0221, 0223, 0224, 0227, 0247, 0248 received status-and-existence checks only. At the charter's reduced-rigor tier this is the intended depth for a remainder sweep, but a future pass wanting per-ADR cards for that last group should not read this file as having produced them.

---

## Batch 6 — full range (ADR-0251–0265)

*Source: `docs/adr-audit/10-stack-dossiers/Batch6-TierA-redo.md`* · `AA-507`–`AA-514` · 0 🔴 / 2 🟡 / 0 🔵 / 6 🟢

- **`AA-508` 🟡** — `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` reserves numbers 0254–0261 for eight Blueprint gap-intents ("not materialised until the owning stage implements them," line 59); **all eight numbers have since been minted as unrelated deduction/serving-arc ADRs** and neither the mapping nor ADR-0253 clause 3 ("reserved as ADR-0261 if implemented later") was amended. A reader following the mapping today is misdirected in 8 of 8 reserved rows.
- **`AA-509` 🟢** — Batch 1's `AA-73` risk (SIMD-holonomy hardened under reserved 0261 without a NO-GO note) is dissolved *by accident* — the number is taken — but the BP-0253 holonomy-SIMD intent now has no reserved home and still no NO-GO annotation anywhere; `AA-82`'s requested mapping-row annotation remains owed and is now more urgent, not less.
- **`AA-507` 🟢** — Bands v3-MEM/v4-CM/v6-EX (0258/0259/0261) are built with `wrong=0` but below θ_SERVE=0.99 at current sample sizes (Wilson lower bounds ≤0.9398/≤0.9398/≤0.9229, recomputed independently) — the earned-license regime withholding capability honestly; recorded so nobody mistakes "unlicensed" for "broken."
- **`AA-513` 🟢** — ADR-0254 adds hedge site #3 with an explicit in-text deferral of unification (extends `AA-142`/Cluster 5; the deferral is documented, unlike the 0028/0038 pair's silence).
- **`AA-512` 🟢** — ADR-0252 is the corpus's record-maintenance exemplar (ruled in-place corrections, verdict banners); cite it as the model when drafting the remediation guidance for the ~20 stale-status ADRs found in Batches 1–2.
- **`AA-511` 🟡** — ADR-0251 §5 (geometric-normalization spike) still reads "Proposed — awaiting ruling" while the 2026-07-28 Foundations Audit/Perception Arc adjudicated the adjacent hypothesis family; needs an explicit disposition note either way.
- **`AA-514` 🟢** — ADR-0255 clean; fail-closed baseline discipline verified.
- **`AA-510` 🟢** — ADR-0262↔0264 amendment chain is bidirectional and explicit; clean.

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 6 🟢.** Note against the calibration warning in the charter: this batch is genuinely the corpus's healthiest — 12 of 15 ADRs date from the last 10 days of disciplined, ruling-gated work (the 2026-07-19→28 arc that the assessment itself governed), and 4 of the 8 findings are explicitly *positive* exemplars. The near-zero critical rate here is evidenced (every band's ledger read, every governs-file checked, Wilson bounds recomputed), not assumed — the contrast with the retracted pass is that this one shows its work.

---

## Batch 4 — remainder (44 files: 0151–0200 minus the two stacks above)

*Source: `docs/adr-audit/10-stack-dossiers/Batch4-TierA-redo.md`* · `AA-515`–`AA-540` · 3 🔴 / 9 🟡 / 3 🔵 / 11 🟢

**25 of 44 ADRs showed a Status-vs-reality mismatch** — the heaviest concentration of Pattern A in the corpus.

### 🔴 Block (for ruling) — 3

- **`AA-516` 🔴** — **A CI workflow ratifies proposals and pushes the active teaching corpus to `main`, contradicting the trust boundaries of both Accepted ADRs it cites.** `.github/workflows/ratify-proposal.yml` runs `core teaching review --accept`, then `git add teaching/cognition_chains/cognition_chains_v1.jsonl teaching/proposals/proposals.jsonl` → `git push origin main`, under a commit message reading "ADR-0057 / ADR-0155". ADR-0155 §Decision: the CI runner "**never** commits directly to `main`, **never** mutates `corpora/`, **never** ratifies proposals." ADR-0151 §Trust Boundary: "never writes the active teaching corpus." Two aggravators: (a) ADR-0161 §Surface-B precondition 4 / §466 require a fail-closed repo-owner allow-list on `github.actor` — **unimplemented**; the sole gate is `vars.CONTEMPLATION_ENABLED == 'true'`; (b) `${{ inputs.operator_note }}` is interpolated **unquoted** into the accept step's shell (`:88-94`) in a job holding `contents: write`. Flagged for ruling, not repaired. Mirror into the assessment `G`-register — this is a system-level trust-boundary gap, not document fidelity.
- **`AA-517` 🔴** — **The live pack-mutation boundary for math frame/composition evidence is governed only by unratified doctrine.** ADR-0168, 0168.1, 0169, 0169.1 all read `Proposed … no runtime mutation/admission in this PR`, yet `teaching/math_frame_ratification.py` and `teaching/math_composition_ratification.py` write `packs/data/en_core_math_v1/…`, quote ADR-0168 §Decision as their hard rules (`math_frame_ratification.py:11-20`), cite ADR-0168.1 §"Evidence floor" as the authority for their evidence check (`:201`), are dispatched from the workbench (`workbench/readers.py:1385-1431`, `workbench/api.py:106`), and are the named authority for a CI hazard pin (`tests/test_consumption_case_0050_hazard_pin.py:3-6` — "ADR-0169 §'Acceptance gates'"). The mechanism is well built and well pinned; the governance is absent. One ratification closes all four.
- **`AA-537` 🔴** — **The cross-domain reliability substrate is `Proposed` while an Accepted ADR treats it as canonical.** ADR-0199 is `Proposed`; `core/learning_arena/` (4 modules) is the shared attempt→score→ledger fold for four eval lanes, and Accepted ADR-0238 §28 instructs "Never shadow `core.learning_arena.protocols.GoldTether`." Chains directly onto `AA-491`: **0175 (`Proposed`) → 0199 (`Proposed`) → 0238 / 0256 (Accepted)** — the licensing regime for all 25 deduction bands has two unratified links. Rule 0175 and 0199 together.

### 🟡 Repair — 9

- **`AA-519` 🟡** — ADR-0155's premise is obsolete and the mechanism is dead. It anchors determinism on GitHub-hosted `ubuntu-latest` and budgets GitHub Pro Linux minutes; the ratified architecture (`AGENTS.md:363-367`) is a local macOS Act runner behind the `ubuntu-latest:host` label ("the `ubuntu-latest` environment name is a fiction") with GitHub Actions as "billing-locked… dead signals." Its own §Out of scope names this exact break. `contemplation/runs/` holds two files, both 2026-05-26.
- **`AA-532` 🟡** — ADR-0186's seal is empty: `_SEALED_INJECTORS: Mapping[…] = {}` (`generate/recognizer_anchor_inject.py:905`), so its status-line claim "first injector ships behind the seal" is false; the named runner `evals/gsm8k_math/train_sample/v1/run_sealed_injectors.py` and metric `report_sealed.json` do not exist. ADR-0185 is retired *by* this empty mechanism.
- **`AA-527` 🟡** — Accepted ADR-0170 defers W3–W5 and the `SentenceChoice` widening to **ADR-0171, which does not exist** (census §Summary numbering gap); its named prerequisites `CandidateRate`/`apply_rate` exist nowhere. An Accepted deferral pointing at a number that was never written, with the successor seal (0186) empty — the whole injector-widening lane is stalled and no record says so.
- **`AA-521` 🟡** — `workbench/readers.py`'s module docstring is `"""Read-only readers for the CORE Workbench W-026 API."""` while the same module applies Lexical/Frame/Composition claims into `packs/data/…` (`:1380-1431`). ADR-0160 §114 ("V1 is read-only by default") carries **zero** references to the ADR-0173 amendment that narrowed it. Pillar II + AGENTS.md #5.
- **`AA-522` 🟡** — ADR-0161 Surface B is accept-only and untyped: the specified `transition` event with `ratifier_kind` / `actor` / `commit_sha` / `workflow_run_id` has no producer (`teaching/proposals.py` has zero `ratifier_kind` support; `workflow_run_id` appears nowhere), and `action ∈ {accept,reject,withdraw}` was never parameterized. ADR-0173 §380's enum is 2/3 real — and the missing third is the surface that can push to `main` (`AA-516`), so the highest-privilege ratification path is the one leaving no audit discriminant.
- **`AA-530` 🟡** — ADR-0184~2 states "**Supersedes:** no runtime path yet; this is a scope-setting ADR" while S1/S2/S4/S4b shipped: `generate/derivation/state/` (8 modules) + `tests/test_adr_0184_s{1,2,4,4b}_*.py`, including a replay-equivalence gate.
- **`AA-529` 🟡** — ADR-0179 carries no amendment note although Accepted ADR-0207 §Open items records verbatim "**ADR-0179 §Context drift.** Its 'thin extractor' table predates the landed…". The ratifying ADR diagnosed the drift; the ratified ADR was never annotated. Same class as `AA-53`.
- **`AA-533` 🟡** — ADR-0189/0189a introduced two real-corpus confabulations (idx 693, 7369) — documented in ADR-0191 §1 as "regressions introduced by #488… they refused correctly before that PR and confabulated after" — i.e. an unratified, **unpinned** widening breached `wrong=0` on the full 7,473-question split. Neither ADR carries a note, and ADR-0189 has no test pin anywhere in `tests/`. Live defect is closed by 0191; the record is not.
- **`AA-540` 🟡** — ADR-0200 is the reconciliation ADR and is the last unreconciled artifact of its own reconciliation: all six prescribed repairs landed (signed JSON `promote_admitted:false`/`reviewer_signature_matches:false`; ADR-0120's dated note; `docs/reviewers.yaml:56-66` quarantine; `tests/test_mathlogic_expert_ledger_flip.py:128-150` flipped to fail-closed-revert assertions) while its status still reads "awaits operator ratification." Residue: `:9`'s docstring still says "row reports `status: expert`" inside the file 0200 flipped.

### 🔵 Consolidate — 3

- **`AA-535` 🔵** — ADR-0183 is 117 lines recording a fork with no code and no named artifact; its substance is one paragraph of ADR-0181's teacher-boundary section. Fold into 0181 as a §Deferred item. (Verified form of the retracted `AA-363`.)
- **`AA-538` 🔵** — ADR-0199's five-subject generalization is undelivered: PR-3/4/5 (`systems_software`, `physics`, `hebrew_greek_textual_reasoning`) never shipped, and the three lanes that *do* consume `run_practice` carry `domain_id`s (`determination_estimation`, `curriculum_serve`, `deduction_serve`) absent from `core/capability/domains.py`. Either the registry admits arena-only domains or the arenas map onto base subjects; today neither is true and no record notices.
- **`AA-524` 🔵** — The three true collisions in this range (0163~1/~2, 0178~1/~2, 0184~1/~2) each pair a scope-only spec with an implemented increment on a *related* surface, so a reader following one number reaches the wrong document. Per ADR-0225 do not renumber; add reciprocal "not to be confused with" lines. Feeds `21-drift-report.md`.

### 🟢 Monitor — 11

- **`AA-515` 🟢** — **Positive exemplar, and the fix template for this whole range.** ADR-0170's header reconciles its own stale status: *"Status reconciled 2026-06-15 (mastery-v2 Step 2; was the stale 'Proposed / no runtime change in this PR', which never tracked W1/W2 landing)."* Cite this against the 25 mismatches rather than inventing a new convention.
- **`AA-539` 🟢** — **Positive exemplar (Pillar II).** The two `GoldTether` concepts are disambiguated in three independent places: ADR-0238 §25-28's comparison table + "Never shadow `core.learning_arena.protocols.GoldTether`"; `core/physics/goldtether.py:16` "Distinct from Arena GoldTether (ADR-0199 / core.learning_arena.protocols)"; and 0199's own protocol. **The two do not silently overlap.** Direct counterexample to `AA-30`'s name-collision class.
- **`AA-531` 🟢** — **Positive exemplar.** ADR-0185's supersession banner is dated, states the refuted premise, cites the disjointness evidence, names the correct destination, and says "retained as a record only; it is NOT implemented." Same class as `AA-487`.
- **`AA-536` 🟢** — **Positive exemplar.** ADR-0198 carries an explicit "Implementation Status" split in its status line and defers to ADR-0216, which **exists** — the honest contrast to `AA-527`'s phantom ADR-0171.
- **`AA-520` 🟢** — ADR-0159's only operator-facing invocation is wrong: `core eval contemplation-quality` (hyphen) vs the registered lane id `contemplation_quality` (`workbench/readers.py:69`, `tests/test_contemplation_quality_lane.py:40`). All nine named metrics do exist.
- **`AA-518` 🟢** — ADR-0154's disclosed hazard is now the shipped default: it asked for "a future bound (LRU or cap)… before long-running operators enable the producer with the consumer off," which is exactly today's configuration (producer unconditional at `core/cognition/pipeline.py:257-262`; `recognition_grounded_graph=False` at `core/config.py:251`; no cap on `_pending_recognizer_examples`). Unbounded per-session growth in a long-lived runtime.
- **`AA-534` 🟢** — Gate reachability of this range's most consequential pins: ADR-0191's serving-path `wrong=0` firewall pin (`tests/test_candidate_graph_completeness_guard.py`), ADR-0186's seal-leak pin, and ADR-0199's L-1 floor-reuse pin are all in `tests/full_only_baseline.txt` (post-merge only). Registered under the ratified G-7 ratchet, so **not a new gap** — but these three are the range's strongest promotion candidates. (The FrameClaim/CompositionClaim suites are gate-reachable; credit where due.)
- **`AA-523` 🟢** — Citation/naming rot, one line: ADR-0162 names a nonexistent `EvalCenter`; ADR-0192 §92 cites a pin `test_unobserved_counted_noun_refused` whose real equivalent is `test_dangerous_shapes_still_refuse`; ADR-0172 cites `ProposalVerdict`, `teaching/math_proposal_verdicts/index.json` and `tests/test_math_contemplation_decomposition.py` — none exist; ADR-0163~1 cites `cases.json` for on-disk `cases.jsonl`; ADR-0177 writes `N_min` for the pinned `N_MIN`; ADR-0170 cites `docs/handoff/…` for files at `docs/handoffs/…` (the `AA-58`/`AA-85` one-character class, still uncaught).
- **`AA-525` 🟢** — ADR-0166 is a `Proposed` review-discipline rule that Accepted ADR-0170 names as its "**Gating rule:**". No enforcing pin exists (by design — it is a PR-review convention). Weak positive evidence it held: both counter-examples it was written against (`spatial_geometry_ood`, `historical_sequence_ood`) exist nowhere. Stated as weak because absence of a lane is not proof of the rule's causation.
- **`AA-528` 🟢** — ADR-0176 is the only member of the 0164→0179 comprehension arc that ADR-0207 does not mention at all (0 occurrences), so it stayed `Proposed` outside the ratification that moved its five siblings out of limbo — while MS-1/2/3 shipped with four test files. Include it in the reconciliation sweep.
- **`AA-526` 🟢** — ADR-0167 carries two `## Decision` headings (`:36`; `:186` "Decision (pending operator ratification of this ADR)"), so a reader diffing claimed-vs-landed hits two decisions. Same shape as `AA-96`.

---

---
