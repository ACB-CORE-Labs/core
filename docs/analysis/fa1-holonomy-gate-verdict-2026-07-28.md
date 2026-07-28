# FA-1 verdict: **NO-GO** — cross-language holonomy does not discriminate meaning

**Date:** 2026-07-28 · **Criterion registered before the run** at `94f05ba8`
(`docs/analysis/fa1-holonomy-gate-preregistration.md`, amendment A1 recorded before any
number existed) · Runner: `evals/logos/fa1_gate.py` · Deterministic, re-run bit-identical.

> **G4 held.** The repairs work: the ground is clean and the loop closes. The design's
> claim is what failed. Per the registration, this is a full-credit result — *"the outcome
> that would retire the largest piece of unearned design in the system, and it is worth as
> much as a GO."*

---

## 1. The result

| Gate | Requirement | Observed | |
|---|---|---|---|
| **G1** separation, all negatives | AUC ≥ 0.80 | **0.557** | ✗ |
| **G2** hardest class (cross-pair) | AUC ≥ 0.75 | **0.664** | ✗ |
| **G3** word-order sensitivity | ≥ 0.90 | **0.644** | ✗ |
| **G4** no collapse re-entry | `coordinates_lost == 0` | **0** | ✓ |

**VERDICT: NO-GO.** AUC 0.557 against a chance floor of 0.500.

**Controls, reported per anti-gaming rule 4.** Max self-loop deviation `d(A,A) = 3.6e-06`
across all 1,016 aligned pairs — the instrument can report closure, so a null result is a
measurement and not a broken metric. Corpus: **83 authored edges, 59 resolved under R3, 24
concepts** (6 tri-language, 18 bi-language), **2,024 clause sets**, **1,016 aligned pairs**,
**58,375 negatives** (50,748 lexical · 5,080 word-order · 2,547 cross-pair).

## 2. The signal is real, in the right direction, and far too weak

The negative classes order themselves exactly as meaning-distance would predict:

| Class | median `d` | AUC vs aligned |
|---|---|---|
| **aligned** (same content, two languages) | **27.20** | — |
| lexical substitution (one word changed) | 32.17 | 0.547 |
| word-order permutation (same words, reordered) | 41.17 | 0.602 |
| cross-pair (entirely different content) | 53.23 | 0.664 |

Aligned pairs *do* close tighter than negatives, and the further a negative is from the
original meaning the wider its loop opens. The geometry is not noise. But the distributions
overlap so heavily that a classifier built on `d` is barely better than a coin — and the
design does not ask for a correlation, it asks for **a validation gate**. A gate at AUC 0.557
would refuse correct articulations and admit wrong ones at nearly the same rate.

## 3. Why it fails — the diagnosis, not just the number

**The encoding is more sensitive to permutation than to substitution.** Reordering the same
three words moves `d` from 27.2 to 41.2. Replacing one of the three words with a *different
concept* moves it only to 32.2. A quantity that reacts more strongly to shuffling a clause
than to changing what the clause is about is measuring **path shape, not content**.

That follows from the algebra rather than from any defect: `F(X)` is an ordered geometric
product, so permutation acts on it through non-commutativity — a first-order effect — while
substituting one of three factors perturbs it only through that factor's own difference.
Word order is structurally louder than word identity, and meaning lives mostly in identity.

And even the order sensitivity is unreliable per-pair: **G3 = 0.644**, so a third of all
permutations make the loop close *tighter* than the correctly-ordered clause. ADR-0015's own
stated test — *"word-order changes should change holonomy"* — is satisfied only in the trivial
sense that the number moves. It does not move in a consistent direction.

## 4. What this does and does not settle

**Settled.** Cross-language holonomy closure, as ADR-0005/0015 specify it, is **not** a
validation gate of meaning — measured on a ground with zero coordinate collisions, with a
genuinely closed loop, with mechanically-generated negatives in three classes and no
cherry-picking, at a corpus 1,000× the size of the June measurement. The two conditions that
made the June negative uninterpretable were removed and the answer did not change; it became
*more* precise.

**Not settled, and deliberately not tested here.** The cross-language alignment strength is
`0.10` — the value the compiler declares — so aligned tokens across languages sit only 10% of
the way toward each other. A stronger coupling would raise separation, and at strength `1.0`
it would reach it trivially, by re-collapsing the manifold into exactly the state FA-1 found
and G4 forbids. Somewhere between those lies a question worth asking, and **this experiment
does not ask it**, because selecting a coupling *after* seeing the registered value fail is
the definition of the tuning this registration's anti-gaming rules forbid.

If it is ever asked, it must be its own pre-registration, and it must carry a criterion that
G4 cannot be traded against: **separation must improve faster than distinctness degrades**,
with both measured, or the "improvement" is just collapse arriving by a slower road.

**Also not settled:** the token-level question. Whether *individual* aligned versors sit
closer than unaligned ones on the repaired ground is a narrower claim than the clause gate,
and the four tests that nominally proved it are decoration
(`docs/analysis/logos-substrate-collapse-2026-07-28.md` §3). It is worth measuring honestly.
It is not this result and cannot be used to soften it.

## 5. Consequences — what changes

1. **The validation-gate claim is retired.** ADR-0005 and ADR-0015 are amended: cross-language
   holonomy resonance is recorded as **measured and not supported**, with this verdict as the
   authority. The phrase *"This is the CORE-Logos proof"* does not survive the measurement it
   invited. The ADRs are amended, not deleted — the design was a real hypothesis, honestly
   stated, and it was tested.
2. **The depth packs keep a smaller, earned role**: lexical and morphological resources with
   real cross-language concept alignment (24 concepts, 59 resolved edges), and Hebrew root
   folding into geometry at compile time (`triliteral:`), which is untouched by this verdict.
3. **The keel's L3 takes the NO-GO branch.** `logos/` is admitted as lexicon + morphology.
   K4's meaning criterion must come from somewhere other than cross-language closure — which
   is now a known constraint on the perception design rather than an assumption inside it.
4. **The repairs are worth carrying anyway, and independently of this verdict.** R1 (geodesic
   blending) removes 53 coordinate collisions from the six-pack mount and 37 from the
   trilingual one; R3 connects 39 of the 63 dead alignment edges. A ground that keeps its
   distinctions is worth having whether or not holonomy is its gate — the collapse harmed
   English's own vocabulary, and no theory of meaning was required to see that.

## 6. What this cost, and what it bought

One session. It closed the largest open design question in the system with a measurement
instead of a belief, and it did so by first finding that the question had never been askable:
the ground was collapsed and the loop was open, so the June negative measured neither the
design nor the geometry.

The register of geometric-substrate verdicts now reads: wedge **C3-decoration**, operator
ablation **identical-to-baseline**, ADR-0252 §5 **NO-GO**, cross-language holonomy **NO-GO on
a clean ground**. Four independent negatives is not a run of bad luck; it is a boundary. The
honest reading is that this substrate's value has not been demonstrated in *reasoning* — while
its value in *representation* (exact recall, versor conditioning, determinism) is measured and
holds. The keel should be built on what is measured.

**Reproduce:** `uv run python -m evals.logos.fa1_gate` · pinned by
`tests/test_fa1_gate_verdict.py` · raw output in this document's §1–2 tables.
