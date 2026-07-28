# ADR-0252 §5 — the structure-mapping experiment, run to a verdict

**Date:** 2026-07-28 · **Runner:** Opus 5 (Track A, `docs/assessment/50-execution-plan.md` §6)
**Base:** `forgejo/main` @ `797ebad5` · **Criterion:** pre-registered at `dfc394d2`, before the run
**Artifact:** `evals/structure_mapping/adr0252_s5/results/report-797ebad5.json`
**`deterministic_digest`:** `b3d9d27592e213104c51bcace7415fd819d722a1b06f7d0a5ca65bd5a234e4ec`
**Reproduce:** `uv run python -m evals.structure_mapping.adr0252_s5.experiment`

---

## VERDICT: **NO-GO**

Both embedding variants fail. Structure-sensitivity (§5.3c) fails at **every**
attribute weight tested — it is not a knife-edge on one constant. Per ADR-0252
§5.4, *"a well-controlled NO-GO is a full-credit result"*: it refutes geometric
SME for comprehension **in the embedding class tested** and redirects stage 2 to
a different representation.

For ratification. This document authorizes nothing on its own.

---

## 1. What was already there, and why it could not stand

The plan recorded §5 as *"authorized, scaffolded, and unrun."* It is scaffolded
and authorized. It is **not unrun** — it has been run twice, and both runs
returned GO on unmerged branches:

| Attempt | Branch @ SHA | Claimed | Why the claim does not hold |
|---|---|---|---|
| 1 | `rnd/structure-mapping-experiment` @ `fc9d0c14` | GO | Disowned by its own successor: the S1–S4 label entered the embedding via hand-typed "canonical" matrices, so all cases of a structure were the same byte-array. Procrustes on identical matrices is trivially zero. |
| 2 | `rnd/sme-experiment-v2` @ `96e5f468` | GO | Genuinely blind — and then `except ValueError: res = 1000.0`. Its rule `cross_mean > same_mean*2 and same_mean < 1.0` is satisfied by that sentinel alone. **A solver exception is not a distance.** |

Attempt 2 carries four further defects, each of which independently voids it:

1. **Wrong branch of the instrument.** It passed mixed versor/point *sequences*
   to `conformal_procrustes`, which dispatches those to field conjugacy
   `W F W⁻¹` — the branch that raises `field conjugacy versor not closed`. Its
   entire separability signal is that raise.
2. **Corpus provenance.** Its doc says "51 actual problem graphs from the
   `holdout_dev/v1` corpus." **5 of 51** carry holdout ids; 46 carry bare
   integers (`1`, `2`, `9`, … `2087`) matching nothing in that corpus, or
   `gma-*` ids belonging to the **public** lane. §5.6's discipline is
   *"`holdout_dev/v1` only"*, and §5.1 permits synthetic variants only *"marked
   as such."* Nothing is marked.
3. **Duplicate data.** At least three exact-duplicate graphs under different ids
   (`1`≡`51`, `2`≡`60`, `17`≡`46`) and three colliding ids (`gma-115`,
   `gma-121`, `gma-135` each appear twice with *different* graphs, so its
   `id → label` dict silently drops one of each pair). Duplicate graphs align at
   residual 0 by construction — attempt 1's tautology re-imported through the
   data instead of through the embedding.
4. **Unreproducible.** Its `scripts/extract_sme_corpus.py` is cited as an
   artifact and was never committed. It also scored only the first 20 rows.

None of this was caught by re-reading the documents. It was caught by reading
the script, the corpus file, and the ids.

## 2. The coverage fact that shaped this run

**Measured at `797ebad5`: the serving reader returns a selected graph for 5 of
the 500 `holdout_dev/v1` cases — 1.0% — and all five carry the same relational
skeleton** (`compare_multiplicative`; they are exactly the organ cohort in
`evals/structure_mapping/scoring/labels.py`). On the public lane the same
pipeline yields 24/150.

So §5.1's corpus — "minimum four structures with clean labels … drawn from
`holdout_dev/v1`" — **is not extractable today**. That is almost certainly why
attempt 2 reached for other lanes; the mistake was doing it silently.

This run uses §5.1's own escape hatch, visibly: 5 real cases extracted through
`parse_and_solve`, 48 synthetic from four declared templates, every one carrying
`provenance="synthetic"` and pinned by `tests/test_adr_0252_s5_blindness.py`.

**Consequence, stated rather than buried:** this verdict speaks about **the
geometry**, not about coverage. §5.5's compression estimate ("how many holdout
families collapse to how few canonical structures") is **not answerable** at
1.0% reader coverage and was not attempted.

## 3. The instrument, characterised before use

`conformal_procrustes` has two branches and they are not interchangeable:

| Input | Branch | Behaviour |
|---|---|---|
| `(5,K)` grade-1 point cloud | Kabsch + Umeyama | never raises; invariant to rotation, translation **and uniform scale** |
| mixed versor/point sequence | field conjugacy | **raises** on unlike inputs |

Measured on dummy clouds before any corpus was embedded — identical `1.8e-16`,
rotated `7.8e-16`, translated `3.9e-15`, uniformly scaled ×2.5 `1.4e-14`,
non-similar z-stretch `5.9e-1`, unrelated `1.1e0`. This run uses the first
branch. **Non-convergence rate: 0.0%** across 1378 pairs in both variants — no
pair was excluded, and no exception contributed to any number below.

## 4. Results

53 cases, 1378 pairs, 334 same-structure / 1044 cross-structure.

| | RS-A (`ATTR_SCALE=0`) | RS-B (`ATTR_SCALE=0.02`) |
|---|---|---|
| **(a) Separability** | **PASS** — AUC **1.0000**, τ=0.0935, 100% / 100%, margin **+0.0867** | **FAIL** — AUC 0.8297, 75.1% / 75.7%, margin **−0.4757** |
| **(b) Attribute-invariance** | PASS, but **analytic** — all 12 variants at exactly `0.000000` because attributes are not in the geometry | **FAIL** — median 0.0331 (ratio 0.107); the ×3 `rescale` pairs land at 0.093–0.227 |
| **(c) Structure-sensitivity** | **FAIL** — `add-vs-subtract` = **0.000000** | **FAIL** — `S1-vs-S2` = 0.1764 < τ=0.2225 |
| (d) Systematicity *(reported, not gating)* | chain↔chain **0.0000**, chain↔flat **0.8703** | chain↔chain 0.0448, chain↔flat 0.8661 |
| **Verdict** | **NO-GO** | **NO-GO** |

### 4.1 Why RS-A's decisive control fails, exactly

The two graphs in the `add-vs-subtract` minimal pair differ in exactly one
field — one entity, identical numbers, `add` against `subtract`. Their
configurations are:

```
subtract : (1,0,0)  (2,0,-1)  (3,0,0)
add      : (1,0,0)  (2,0,+1)  (3,0,0)
```

These are related by a **180° rotation about e1** — a *proper* rotation, det = +1.
Kabsch aligns them exactly, so the residual is not merely small, it is `0.0`.

**The similarity quotient that would give attribute-invariance is the same
quotient that annihilates the structural contrast.** A geometry blind to
rotation cannot distinguish "gain" from "loss" when their only encoded
difference is a signed offset on one axis.

This much *is* repairable by constants: with asymmetric kind heights
(`subtract → 7.0`) the three minimal pairs measure 0.162 / 1.940 / 0.217, all
above τ. **That repair is a diagnostic and does not change this verdict** — the
criterion was fixed in advance and a re-run under a repaired scheme requires its
own pre-registration. It is recorded here because concealing it would make the
NO-GO look deeper than it is.

### 4.2 What is *not* repairable by constants — the deeper result

Sweeping `ATTR_SCALE` under the same thresholds (committed as
`diagnostic_sweep` in the report):

| `ATTR_SCALE` | AUC | (a) | (b) | (c) | `rescale` median |
|---|---|---|---|---|---|
| 0.0 | 1.0000 | PASS | PASS | FAIL | 0.00000 |
| 0.001 | 1.0000 | PASS | PASS | FAIL | 0.00615 |
| 0.002 | 1.0000 | PASS | PASS | FAIL | 0.01245 |
| 0.005 | 1.0000 | PASS | PASS | FAIL | 0.03259 |
| 0.01 | 0.9742 | FAIL | PASS | FAIL | 0.06682 |
| 0.02 | 0.8297 | FAIL | FAIL | FAIL | 0.13505 |
| 0.05 | 0.6888 | FAIL | FAIL | FAIL | 0.40610 |
| 0.1 | 0.6694 | FAIL | FAIL | FAIL | 1.16296 |

Read down the table: **every regime in which the SME property survives is a
regime in which attributes contribute essentially nothing.** Where attributes
are geometrically negligible (≤0.005, `rescale` residual ≤0.033), separability
is perfect — but "invariance" there is a restatement of blindness. The moment
attributes carry real weight, separability collapses monotonically
(1.00 → 0.97 → 0.83 → 0.69) and invariance degrades with it.

There is no setting at which the geometry both *sees* surface attributes and
*factors them out*. That is the SME signature §5.3b was written to detect, and
it is absent — not narrowly missed.

The mechanism is structural rather than incidental: Procrustes measures a metric
distance between point configurations modulo similarity. Any attribute that
moves a point either moves it **within** the similarity orbit — in which case it
was never carrying information the aligner could use — or **outside** it, in
which case invariance fails by construction. There is no third option in this
class of embedding.

## 5. Scope of the refutation — stated narrowly on purpose

**What this refutes.** H1 for the class of embeddings that encode role-structure
as point positions in Cl(4,1) and align them with conformal Procrustes under
similarity. The §4.2 argument is about the similarity quotient itself, so it
generalises across position-encoding schemes in this class, not just the
particular constants used here.

**What this does not refute.** That *some* Cl(4,1) representation could carry
relational structure — e.g. one where relations are versors composed rather than
points positioned, or where alignment is a non-metric admissibility check rather
than a Procrustes residual. Those are different experiments and would need their
own pre-registrations.

**What it does not touch at all.** Whether the *symbolic* structure-mapping
already in `evals/structure_mapping/` works. That lane is untouched here.

## 6. What follows

Under ADR-0252 §5.4 a NO-GO "cleanly refutes geometric SME for comprehension and
redirects stage 2 to a different representation," and §5.4 pre-declares this
full credit. Three consequences for the registers, offered for ruling and not
taken:

1. **G-1 can close** with a recorded verdict, and the §6 build authorization
   question is settled in the direction of "not on this representation."
2. **Track B's widening is unblocked in shape** (`50-execution-plan.md` §7's hard
   gate: *"Track B widening ⟸ Track A verdict"*). The verdict says widening
   proceeds by **more constructions**, not by geometric structure-mapping.
3. **H-10's mispricing is confirmed and discharged.** The experiment cost hours,
   not an arc, and it governs the comprehension paradigm — exactly as H-10 said.

A fourth item is new and is the one worth your attention most: **the 1.0% reader
coverage of `holdout_dev/v1`** (§2) is a sharper measurement of the comprehension
frontier than G-3's construction count, on a corpus the project already treats as
its held-out standard. It belongs in the gap register on its own.

---

*Every number above is produced by `uv run python -m
evals.structure_mapping.adr0252_s5.experiment` at `797ebad5` and is reproduced by
the committed report artifact and its digest. The criterion constants in
`experiment.py` are unchanged since `dfc394d2`, which carried them before the run
and carried no results; the only post-run edit to that file is the additive
`diagnostic_sweep` block, and `git log -p` shows it.*
