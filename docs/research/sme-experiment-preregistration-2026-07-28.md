# ADR-0252 §5 — pre-registration of the structure-mapping acceptance gate

**Date:** 2026-07-28 · **Author:** Opus 5 (Track A, `50-execution-plan.md` §6)
**Base:** `forgejo/main` @ `797ebad5`
**Status:** written and committed **before** the run. The commit that carries this
file also carries the experiment code and carries **no results**. Any later change
to a threshold below invalidates the verdict rather than adjusting it.

---

## 0. Why a pre-registration exists for this experiment specifically

Track A's protocol requires the GO/NO-GO criterion be stated in writing before
running — *"the ADR's §5 conformance bar, not a criterion chosen after seeing
results."* That requirement is not ceremonial here. The experiment has been run
twice, and both runs returned GO on a criterion that was not binding:

- **Attempt 1** (`rnd/structure-mapping-experiment` @ `fc9d0c14`) is disowned by
  its own successor: the S1–S4 label entered the embedding coordinates through
  hand-typed "canonical" matrices, so every case of a structure had an identical
  byte-array and Procrustes on identical matrices is trivially zero.
- **Attempt 2** (`rnd/sme-experiment-v2` @ `96e5f468`) fixed the leak and then
  measured separability with `except ValueError: res = 1000.0`. Its GO test
  (`cross_mean > same_mean * 2 and same_mean < 1.0`) is satisfied by that
  sentinel alone. A solver exception is not a distance.

Both defects are invisible unless the decision rule is fixed in advance. So the
rule below is committed as *code* — `experiment.py`'s module constants — and the
run imports it.

## 1. What is being tested (ADR-0252 §5, H1)

> There exists a principled embedding of a problem's role-predicate structure
> into Cl(4,1) point-configurations such that conformal-Procrustes alignment
> residual is (a) low within a deep structure, (b) high across deep structures,
> (c) invariant to surface-attribute change, and (d) sensitive to structure change.

## 2. The instrument, characterised before use

`conformal_procrustes` has two branches, and they are not interchangeable:

| Input form | Branch | Behaviour |
|---|---|---|
| `(5,K)` grade-1 point cloud | Kabsch + Umeyama | never raises; residual invariant to rotation, translation **and uniform scale** |
| mixed versor/point sequence | field conjugacy `W F W⁻¹` | **raises** `field conjugacy versor not closed` on unlike inputs |

Measured on dummy clouds at `797ebad5`, before any corpus was embedded:
identical `1.8e-16`, rotated `7.8e-16`, translated `3.9e-15`, uniformly scaled
×2.5 `1.4e-14`, non-similar z-stretch `5.9e-1`, unrelated cloud `1.1e0`.

Attempt 2 used the second branch. This experiment uses the first, and treats a
raise as **non-convergence** — excluded from the statistics, reported as a rate,
never counted as evidence of separation.

## 3. Corpus (§5.1), and the coverage fact that forced its shape

§5.1 asks for ≥4 structures with clean labels drawn from `holdout_dev/v1`.
**Measured at `797ebad5`: the serving reader returns a selected graph for 5 of
the 500 holdout cases (1.0%), and all five carry the same skeleton**
(`compare_multiplicative` — they are exactly the organ cohort already recorded
in `evals/structure_mapping/scoring/labels.py`). The corpus §5.1 specifies is
therefore not extractable from `holdout_dev/v1` today.

§5.1's own escape hatch is used, and used visibly: *"add controlled synthetic
surface-variants only where needed for clean labels (marked as such)."*

| Arm | n | Provenance |
|---|---|---|
| real | 5 | `holdout_dev/v1`, via `parse_and_solve` — no hand-authoring |
| synthetic | 48 | four declared templates × 12 attribute realisations, `provenance="synthetic"` |

Consequence, stated now so it cannot be quietly dropped later: a verdict from
this corpus speaks about **the geometry**, not about coverage. §5.5's
compression estimate ("how many holdout families collapse to how few canonical
structures") is **not answerable** at 1.0% reader coverage and is not attempted.

## 4. Embedding (§5.2), declared

Full scheme in `embedding.py`'s module docstring. In brief: entity → conformal
point on the role circle at angle `2πk/8` by **order of introduction** (never by
name); relation → a point at the circular mean of its arguments' angles, radius
`2.0 + 0.35·j` (story order), height a declared per-kind constant; the unknown →
one point at the asked role. Undeclared relation kind ⇒ refusal, never a default
position. Clouds padded to 16 points with the cloud's own centroid.

**Two variants, because §5.2 and §5.3b pull against each other.** §5.2 says the
configuration must encode role-structure and "never surface words or literal
values"; §5.3b says residual must not move when numbers change. An embedding
that cannot see numbers satisfies §5.3b analytically — which is a proof about
the scheme, not a measurement. So both are run:

| Variant | `ATTR_SCALE` | §5.3b status |
|---|---|---|
| **RS-A** | 0.0 | analytic — attributes are not in the geometry |
| **RS-B** | 0.02 | **measured** — quantities displace points along `e3` |

Entity *names* are outside both variants by construction, so of §5.3b's three
perturbations, `rename` is analytic in RS-A **and** RS-B; only `rescale` and
`jitter` are empirical, and only in RS-B.

## 5. The decision rule — binding

Let τ be the single threshold chosen to maximise `min(same-below-rate,
cross-above-rate)` over all pairs.

| # | Measurement | Passes iff |
|---|---|---|
| (a) | **Separability** | ROC AUC ≥ **0.90** and one τ puts ≥ **95%** of same-structure pairs below it and ≥ **95%** of cross-structure pairs above it. Means alone are not sufficient — §5.3a says so explicitly. |
| (b) | **Attribute-invariance** | every attribute-only variant pair lands below τ, and their median is ≤ **25%** of the cross-structure median |
| (c) | **Structure-sensitivity** | every minimal pair — identical roles, identical numbers, exactly one relation kind changed — lands above τ |
| (d) | **Systematicity** | reported, **not gating**: §5.4's verdict rule names only (a), (b), (c) |

**VOID** if the non-convergence rate exceeds **5%**. An instrument that refuses
to answer has not answered, and that is neither GO nor NO-GO.

**GO** iff (a) ∧ (b) ∧ (c) hold **on the same variant**.

**NO-GO** otherwise — including the specific case worth naming in advance: if
RS-B fails (b) while RS-A passes (a) ∧ (c) with (b) analytic, that is **NO-GO
for H1 as stated**, recorded with the qualified finding. It is the outcome most
likely to tempt a re-reading of the bar, which is why the reading is fixed here.

**Ambiguity resolves to NO-GO** (`50-execution-plan.md` §8: *"Ambiguity is then
a NO-GO by default, not a re-run with a new bar."*)

A well-controlled NO-GO is full credit by ADR-0252 §5.4's own terms.

## 6. Discipline (§5.6)

Off-serving — `evals/structure_mapping/adr0252_s5/` is imported by no serving
path. Sealed test untouched. `holdout_dev/v1` is the only real-case source;
every non-holdout case is marked synthetic. No answers are emitted, so `wrong=0`
is not in play. Every number in the verdict document is produced by
`uv run python -m evals.structure_mapping.adr0252_s5.experiment`, and the report
carries a `deterministic_digest` so a regression flips it. STOP before
productionizing: this experiment authorizes nothing by itself; §6 remains Shay's
ratification.
