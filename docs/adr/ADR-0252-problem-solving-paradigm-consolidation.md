# ADR-0252: The CORE Problem-Solving Paradigm — Expert Structure-Mapping on a Predictive-Processing Substrate

**Status**: **Accepted** — ratified 2026-07-19 by Joshua Shay. Consolidates and supersedes the six prior paradigm formulations (per the reader-arc recalibration, ADR-0251). Ratification adopts the paradigm (§2), the mapping (§3), and the conformance bar (§4), and authorizes the §5 experiment. It does **not** authorize the §6 build, which stays gated on §5 returning GO under a separate ruling.
**Date**: 2026-07-19
**Deciders**: Joshua Shay (ruling authority) + Claude (synthesis)
**Grounding**: *"The Ontogeny of Human Cognition: From Core Knowledge to Expert Problem-Solving Paradigms"* (2026-07-19) — Spelke/Carey (core knowledge), Quine/Carey (bootstrapping), Siegler (overlapping waves), Friston (predictive processing / free energy), Gopnik (causal Bayes nets), Gentner/Forbus (structure-mapping / SME), Newell/Simon (means-ends), Gigerenzer (fast-and-frugal), Chi/Feltovich/Glaser (novice→expert; surface vs deep structure).

**Supersedes (retire — see Section 9 / ADR-0251 archive):** semantic-substrate problem-solving master plan (2026-06-20); semantic-state-transition blueprint; semantic-symbolic binding-graph proposal; core-problem-solving-capability roadmap v2; the gsm8k-capability-paradigm sprint series (5–12). **Supersedes-in-place:** ADR-0164 (incremental comprehension reader), ADR-0174 (held-hypothesis comprehension).

**Preserves (governing, unchanged):** the discipline layer — `wrong=0`, refuse-don't-guess, decode-don't-generate, sealed-vs-practice separation, measure-on-real-GSM8K; the solving corridor — ADR-0243 (wave-field lifecycle), ADR-0249/0250 (reader→Hamiltonian compiler); the #77/#78 foundations.

---

## 1. The core claim

CORE was built as geometric / wave cognition. Cognitive science's most unifying account shows that geometric / wave cognition **is** the physical substrate of human problem-solving: perception-and-reasoning as free-energy minimization on a predictive manifold (Friston), generalization as relational structure-alignment (Gentner), founded on geometric and numerical core-knowledge primitives (Spelke/Carey). Therefore **CORE's substrate already instantiates the human problem-solving paradigm** — the founding bet is vindicated. The project's single architectural error was to build a **novice** comprehender (34† bespoke surface organs) bolted onto an **expert** substrate it never used for comprehension.

This ADR ratifies the paradigm CORE already embodies and reorients the reader from novice (surface features) to expert (deep relational structure). It is the single governing source of truth; the six retired formulations were each a partial groping toward one of its layers.

> † **Basis note — 2026-07-28.** The figure "34" has no reproducible derivation. The reproducible count of surface entry organs is **18** `resolve_promotable_*` functions, **all** in `generate/derivation/` and none anywhere else, at this ADR's ratification commit and re-verified unchanged at `ca5e614e`; the derivation package holds **exactly 32 modules**, which is the likeliest origin of the number. The diagnosis, the supersession plan, and the §4 conformance bar are unaffected — none of them depends on the count. Later text saying "the 34 surface organs" (§2, §6, §9) should be read as "the surface organs."
>
> *Ruled R-12b, option A, 2026-07-28 by Joshua Shay. Option B — replacing every "34" with "18" — was rejected: it rewrites a ratified document's prose, where recording the correction where a reader meets the number is all that is owed.*

## 2. The paradigm — five stages and the governing law

1. **Perceive → core primitives.** Reduce surface text to the primitives the substrate represents: quantities (the Number core-system), entities (the Object core-system), and their **relational roles** — containment / transfer / accumulation / comparison (two-argument relational predicates). Not surface-slot regexes.
2. **Comprehend → Structure-Map (the expert move).** Build the problem's *relational structure* (a situation model as a role-predicate graph), **aggressively discard surface attributes**, and align it to the nearest known **canonical structure** by role, not resemblance, preferring systematic higher-order relations (Gentner's systematicity). Alignment is a conformal versor fit (SME).
3. **Reconstruct → Quinian bootstrap.** When a structure isn't directly solvable, build a new canonical form by *placeholder → structural-map → inductive leap* (e.g. "twice the total" → placeholder the total, map it to the sum relation, then the doubling relation).
4. **Solve → predictive processing / means-ends.** The canonical structure is the prior/goal; relaxation (active inference) minimizes prediction error to the ground state = the answer; organized as recursive difference-reduction toward the unknown (MEA).
5. **Select → overlapping waves.** Hold multiple candidate structure-mappings at once; adaptively choose by difficulty; **suppress the urge to rely on superficial similarity** (Siegler's Mapping dimension); execute frugally (search / stop / decision rules).

**Governing law:** *propose a structure-mapping → ground it in exact source spans → reconstruct if needed → relax to the answer → emit only if the precision certificate holds, else refuse.*

## 3. The mapping — CORE already is each layer

| Human-cognition paradigm | CORE component (already built) | Status |
|---|---|---|
| **Number** core-knowledge (abstract, combinable, ratio-dependent/Weber) | `core/physics/quantity_kernel.py` — magnitudes as null points; add/subtract = combinability; scale-invariant projective decode = Weber ratio-dependence | Live (eval corridor) |
| **Space** core-knowledge (geometric layout: distance/angle/direction) | Cl(4,1) conformal geometry (`algebra/`, `core/physics/`) | Live |
| **Predictive Processing** (free-energy / prediction-error minimization; prior; precision-weighting = attention) | `cognitive_lifecycle.relax_to_ground` on `compile_quadratic_well`; the well = the prior; `RelaxationCertificate` = precision/surprisal bound | Live (eval corridor) |
| **Structure-Mapping Engine** (align relations, discard attributes; *far less data than deep learning*) | `core/physics/dynamic_manifold.py::conformal_procrustes` | Built, off-serving, unwired to comprehension |
| **Relational predicates** (two-argument roles) | semantic roles — containment / transfer / accumulation / comparison ("depth-language" thesis) | Partially represented |
| **Overlapping Waves** (ranked competing strategies; suppress surface similarity) | ADR-0174 held-hypothesis reader (ranked open interpretations) | Built, deprecated — to revive |
| **Quinian Bootstrapping** (placeholder → structural-map → inductive leap) | reconstruction; CORE's own build of exact arithmetic on the quantity kernel is the bootstrapping case study | Latent |
| **Novice→Expert (surface→deep structure)** | the diagnosis: the 34 `resolve_promotable_*` organs are the novice's surface piles; the substrate is the expert engine | The correction |
| **Precision-weighting / refuse-if-unreliable** | `wrong=0`-or-refuse | Governing |

The fit is not analogy. `relax_to_ground` *is* Friston's principle in Clifford algebra; `conformal_procrustes` *is* a Structure-Mapping Engine; the quantity kernel *is* the Number core-system. CORE is an expert substrate that has been driven by a novice reader.

## 4. Conformance bar (how every future capability is judged)

- **The metric IS the paradigm.** A capability earns its place only if it grasps **deep structure** — one concept subsuming a whole *family* of problems that share a relational structure (the generalization ratio > 1, the expert grouping). One-case, one-pattern additions (ratio ≈ 1) are the novice surface pile and are refused as debt.
- **`wrong=0` is precision-weighting**, not a bolt-on: emit only when the structure is grounded and the certificate holds; otherwise refuse.
- **Doctrine, now cognitively grounded:** Structure-Mapping is the canonical proof that powerful generalization is achievable *without statistical learning* ("far less data than deep learning"). This settles the earlier fork decisively in favor of the geometric path — no learned NLP components; SME is the expert mechanism and it is deterministic.

## 5. The one unknown — resolved with a controlled experiment (the acceptance gate)

> ### §5 VERDICT — **NO-GO**, ratified 2026-07-28 by Joshua Shay
>
> Criterion **pre-registered at `299c92be`, before the run** (that commit carries the thresholds as importable constants and no results). Run at `forgejo/main` @ `797ebad5`. Artifact `evals/structure_mapping/adr0252_s5/results/report-797ebad5.json`, `deterministic_digest` `b3d9d27592e213104c51bcace7415fd819d722a1b06f7d0a5ca65bd5a234e4ec`. Reproduce with `uv run python -m evals.structure_mapping.adr0252_s5.experiment`. Full reasoning: `docs/research/sme-experiment-verdict-797ebad5.md`.
>
> **H1 is refuted for the embedding class tested.** Structure-sensitivity (§5.3c) fails at *every* attribute weight swept — it is not a knife-edge on a constant. The mechanism, measured rather than argued: **the similarity quotient that delivers attribute-invariance is the same quotient that annihilates structural contrast.** An `add`-vs-`subtract` minimal pair — one entity, identical numbers, one relation kind changed — aligns at residual exactly `0.0`, its two configurations being related by a proper rotation. Sweeping the attribute weight, every regime in which the SME property survives is a regime in which attributes contribute nothing (AUC 1.00 → 0.83 → 0.69 as they begin to matter).
>
> **Scope, deliberately narrow.** This refutes H1 for embeddings that encode role-structure as *point positions* aligned by `conformal_procrustes` **under similarity**. The argument is about the quotient, so it generalises across that class. It does **not** refute every Cl(4,1) representation, and it does not touch the symbolic structure-mapping lane already in `evals/structure_mapping/`.
>
> Per §5.4, *"a well-controlled NO-GO is a full-credit result."* This is that. **The §6 build is not authorized and cannot become authorized by this experiment** — see the §6 amendment.
>
> *Two findings the track produced that were on nobody's list.* (1) The experiment was **already run twice, returning GO twice, on unmerged branches** — `rnd/structure-mapping-experiment` @ `fc9d0c14` leaked the structure label into the embedding; `rnd/sme-experiment-v2` @ `96e5f468` counted a solver exception as a distance (`except ValueError: res = 1000.0`) and passed mixed versor/point sequences to the field-conjugacy branch, so its entire separability signal was that raise. Both are unsound and are voided by the verdict document; the plan, the gap register and this ADR had all read the same absence and called the item "unrun" for nine days (recorded as N-8 — *a branch tip is not a record*). (2) The math reader decides **5 of 500** `holdout_dev/v1` cases (1.0%), all carrying one relational skeleton, which is why §5.1's four-structure corpus was not extractable and is registered as **G-21**.

The paradigm is correct in principle. Exactly one empirical claim is load-bearing and unproven: **can CORE's Cl(4,1) geometry carry a problem's relational structure faithfully enough that `conformal_procrustes` (the SME) aligns same-deep-structure problems and separates different-structure ones — driven by *relations*, invariant to *surface attributes*?** If yes, Structure-Map (stage 2) is buildable on the existing substrate. If no, stage 2 needs a different representation, and we learn that cheaply.

Mastery here means isolating the exact SME property with **controls**, not eyeballing residuals.

**Hypothesis H1.** There exists a principled embedding of a problem's role-predicate structure into Cl(4,1) point-configurations such that conformal-Procrustes alignment residual is (a) low within a deep structure, (b) high across deep structures, (c) **invariant to surface-attribute change**, and (d) **sensitive to structure change**.

**Design.**
1. **Structure-labeled corpus.** Group problems by *known relational structure* (the role-predicate skeleton), each with multiple surface realizations. Minimum four structures with clean labels — e.g. S1 compare-multiplicative-then-total (the 0148 family), S2 transfer-then-query, S3 rate-application, S4 additive-comparison-then-total. Draw real cases from `holdout_dev/v1`; add controlled synthetic surface-variants only where needed for clean labels (marked as such).
2. **Relational embedding (the crux — derive from the paradigm, do not improvise).** Map a problem's structure to a geometric configuration: entities/quantities → conformal points (via `quantity_kernel` / `VocabManifold`); each role-relation (contain/transfer/compare/rate) → a geometric relation between its argument points. The configuration must encode **role-structure** (who plays which role in which relation), never surface words or literal values. State the scheme explicitly.
3. **The three decisive measurements**:
   - **(a) Separability** — within-structure `procrustes_residual` ≪ cross-structure, reported as a margin / ROC with a classifying threshold, not just means.
   - **(b) Attribute-invariance (the SME signature)** — hold structure fixed; rename entities, change numbers, swap synonyms → residual must stay low. If it moves with attributes, the embedding is novice/surface → **fail**.
   - **(c) Structure-sensitivity** — hold surface lexically similar; change the relational structure (e.g. a compare vs a transfer with near-identical words) → residual must jump. Proves alignment is driven by structure, not lexical overlap.
   - **(d) Systematicity** — chained/higher-order structures (A=2B, B=2C) align with same-chain problems.
4. **Verdict.** **GO** iff (a) separable with margin AND (b) attribute-invariant AND (c) structure-sensitive — the geometry carries relational structure the SME way. **NO-GO** if alignment tracks surface/attributes or fails to separate — which cleanly refutes geometric SME for comprehension and redirects stage 2 to a different representation. A well-controlled NO-GO is a full-credit result.
5. **If GO**, estimate the compression: how many holdout families collapse to how few canonical structures (the generalization ratio the expert grouping buys).
6. **Discipline.** Off-serving; `holdout_dev/v1` only; sealed test untouched; `wrong=0` not yet in play (no answers are emitted — this measures structure alignment); verify-don't-claim (every number backed by a command); honest NO-GO welcomed; STOP before productionizing.

## 6. What changes in code

- **Keep, recognized as paradigm layers:** `quantity_kernel` (Number), `cognitive_lifecycle/relax_to_ground` (predictive-processing inference), `conformal_procrustes` (SME), the corridor (`turn_program`/`multi_register` = solve), the certificate + `wrong=0` (precision gate).
- **Build (the missing expert-comprehension layer, gated on §5 GO):** a Structure-Map path — a role-predicate relational representation, a small library of canonical structures (base domains), and mapping a novel problem to the nearest canonical via `conformal_procrustes`. — **NOT AUTHORIZED. §5 returned NO-GO on 2026-07-28.** This bullet stands as the record of what a GO would have authorized. Stage 2 needs a different representation, and finding one is not scoped by this ADR.
- **Represent relationally:** treat `MathProblemGraph` (or a layer above it) as a graph of two-argument role predicates, not surface slots.
- **Revive + reframe:** ADR-0174's held-hypothesis reader as the overlapping-waves candidate-mapping selector.
- **Supersede, verification-gated, over time:** the surface organs† — kept serving until a structure-mapper proves out, then retired. — **AMENDED 2026-07-28 on the §5 NO-GO; see below.**

> ### §6 amendment — the retirement condition, on a NO-GO
>
> *Ratified 2026-07-28 by Joshua Shay, together with the §5 verdict.*
>
> As written, this bullet retires the surface organs on the strength of a replacement that **§5 has now tested and refuted**, and it names no replacement for the NO-GO branch. Left alone it would be a live instruction that can never fire — an authoritative-looking dead instrument, which is the exact failure class catalogued as H-9 in `docs/assessment/31-hindrance-audit.md`.
>
> **The surface organs are RETAINED. That is the operative state, not a pause in a transition.** The retirement condition is re-stated as: *a demonstrated replacement that passes the §5 criterion.* No such replacement exists, none is proposed by this ADR, and the one hypothesis that was proposed has been falsified for its embedding class.
>
> Retiring a working organ on the strength of a *hypothesis about* its replacement is backwards. The hypothesis has now been tested. This amendment records that the pre-condition failed, so that no later reader mistakes "verification-gated supersession" for a decision already taken and merely awaiting execution.
>
> *This changes no decision made at ratification. §8's ruling record already states: "The existing 34-organ† reader keeps serving until a proven replacement exists — nothing is torn out on ratification." The amendment makes the NO-GO branch of that same commitment explicit, because the §6 bullet carrying the condition read as though the replacement were coming.*

## 7. Non-goals

No Smith-chart algebra (ADR-0246 §6); no Fibonacci "dimensional cascade" (not in the repo); no learned / statistical / LLM components — SME generalizes without them, which is the entire point. This ADR authorizes no serving change; §6 "Build" is gated on the §5 experiment returning GO, under its own ruling.

## 8. Ruling record (Shay)

**RATIFIED — 2026-07-19, Joshua Shay (ruling authority).**

1. **Adopted.** This ADR is the single governing problem-solving paradigm for CORE. The paradigm (§2), the CORE-component mapping (§3), and the conformance bar (§4) are in force. Every future capability is judged by the §4 metric: it earns its place only if it grasps a deep relational structure that subsumes a *family* of problems (generalization ratio > 1). One-case surface additions are debt and are refused.

2. **Retired.** The six prior paradigm formulations named in the front-matter are retired; ADR-0164 and ADR-0174 are superseded-in-place. ADR-0251 (recalibration) archives them. No competing paradigm doc remains authoritative.

3. **Preserved (unchanged, still governing).** The discipline layer (`wrong=0`, refuse-don't-guess, decode-don't-generate, sealed-vs-practice separation, measure-on-real-GSM8K); the solving corridor (ADR-0243 wave-field lifecycle, ADR-0249/0250 reader→Hamiltonian compiler); the #77/#78 foundations. The existing 34-organ reader keeps serving until a proven replacement exists — nothing is torn out on ratification.

4. **Authorized.** The §5 controlled structure-mapping experiment is authorized to run: off-serving, `holdout_dev/v1` only, sealed test untouched, verify-don't-claim, a well-controlled NO-GO welcomed as full-credit. Its verdict (GO iff separable-with-margin AND attribute-invariant AND structure-sensitive) is the acceptance gate for §6.

5. **NOT authorized.** The §6 build (the structure-map comprehension layer and any serving change) is **not** authorized by this ratification. It is gated on §5 returning GO and will be ruled on separately, on the evidence. No serving behavior changes today.

_Ratification adopts the paradigm and the experiment; it does not pre-commit the build. The geometry must earn stage 2 empirically._

---

## 9. Retirement Record — six unratified paradigm documents

This section records the retirement and archiving of the six competing, unratified paradigm formulations consolidated under this decision:

1. **Semantic-substrate master plan** —
   `docs/analysis/semantic-substrate-problem-solving-master-plan-2026-06-20.md`
2. **Semantic state-transition blueprint** —
   `docs/handoffs/SEMANTIC-STATE-TRANSITION-BLUEPRINT.md`
3. **Semantic/symbolic binding-graph proposal** —
   `docs/implementation/semantic-symbolic-binding-graph-proposal.md`
4. **Problem-solving capability roadmap v2** —
   `docs/analysis/core-problem-solving-capability-roadmap-v2-2026-06-17.md`
5. **GSM8K capability-paradigm sprint lookbacks** (sprints 5–12 lookbacks) —
   `docs/analysis/gsm8k-capability-paradigm-sprint{5,6,7,8,9,10,11,12}-lookback-2026-06-17.md`
6. **ADR-0174's deprecated in-ADR dispatch prescription** — the per-category injector dispatch table and legacy-regex-parser fallback (superseded-in-place).

### Archiving and Status Heuristics

All files corresponding to formulations 1–5 have been moved to `docs/paradigm-archive/` with a `SUPERSEDED` warning header prepended to indicate they are historical and carry no governance weight. 

ADR-0164 and ADR-0174 have received a `**Superseded-by:** ADR-0252` header annotation and remain Accepted in-place as permanent records.
