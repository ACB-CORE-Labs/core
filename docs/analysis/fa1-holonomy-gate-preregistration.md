# Pre-registration: does a repaired semantic ground carry meaning across languages?

**FA-1 experiment · registered 2026-07-28 · criterion committed BEFORE any discrimination
measurement is taken.** Follows the ADR-0252 §5 precedent: the verdict is whatever the
criterion says, a well-controlled NO-GO is full credit, and the criterion is not touched
after the numbers exist.

---

## 1. Why this experiment is not a fourth re-run of a settled question

Three geometric-operator experiments have returned negative (field-reasoner wedge 2026-06-04;
relational-operator ablation 2026-07-19; ADR-0252 §5 structure-mapping 2026-07-28), and the
cross-language holonomy resonance itself returned negative on 2026-06-14 — under the engine's
own metric it **anti-correlated**. The reopening rule this repo set for itself is that a
geometric hypothesis may not be re-proposed blind.

It is not being re-proposed blind. Two preconditions of the June measurement were false, and
both are now measured facts rather than suspicions
(`docs/analysis/logos-substrate-collapse-2026-07-28.md`):

1. **The ground was flattened.** In the mounted trilingual configuration the June experiment
   used, 48 surfaces share 11 coordinates and 37 distinct coordinates are gone. Aligned
   cross-language tokens are *bit-identical*, so "is the aligned pair closer than the
   misaligned one" was not a question about meaning — it was a question about which tokens
   had been overwritten with which.
2. **The holonomy never closed.** `holonomy_encode` returns the forward walk only; the reverse
   walk was deleted at `fca6216e`. ADR-0015's gate is closure. An open path product has no
   reason to be invariant across representations, so the June negative is what the
   implementation predicts, not evidence about the design.

A negative result measured with a broken instrument on a corrupted sample constrains the
instrument and the sample, not the hypothesis. **This is the first measurement of the designed
gate.** If it too returns negative, the hypothesis is genuinely damaged — and *that* is the
outcome this registration exists to make binding.

## 2. The two repairs under test (both are mechanism, not tuning)

Neither repair invents anything; both call primitives the repo already ships.

**R1 — blend on the group instead of overwriting.**
```python
def _blend_feature_versors(source, target, strength):
    if strength <= 0.0:
        return source
    return geometric_product(rotor_power(word_transition_rotor(source, target), strength), source)
```
`algebra/rotor.py` has shipped `rotor_power` (exact closed form for simple rotors, invariant
bivector decomposition otherwise) and `word_transition_rotor` since the algebra layer's first
commit. Verified: unit residual stays `~1e-7` across `t ∈ [0,1]` — three orders of magnitude
inside `VocabManifold`'s `1e-5` tolerance — with `t=0` returning the source exactly and `t=1`
the target exactly. **The declared strengths are used as written** (`0.10`, `0.40`, `0.40`);
they are not free parameters in this experiment and will not be tuned.

**R2 — close the loop, and close it around the *pair*.** The June measurement compared two
open path-products with an external distance. Restoring `H = F · reverse(F)` for a single
clause would be worse — that is a scalar by construction and carries no information at all.
The object ADR-0015 actually describes is the loop formed by **two representations of the
same content**: transport out along clause `A`, return along clause `B`.

```
F(X) = v₁ · v₂ · … · vₙ            ordered geometric product of X's word versors
H(A,B) = unitize( F(A) · reverse(F(B)) )
d(A,B) = ‖H(A,B) − 1‖              deviation from the identity multivector
```

If `A` and `B` carry the same content, `F(A) ≈ F(B)` and the loop closes: `d → 0`. If they do
not, the loop has curvature. This needs **no metric calibration and no threshold on a
similarity score** — the null hypothesis is the identity, which is why the June failure mode
(Euclidean norm passing where the owned similarity metric inverted) cannot recur here.

Two deliberate choices, stated before the run:

* **The per-token `_position_rotor` is excluded.** It was introduced so that "path order
  survives even for scalar/vector fixtures" — degenerate test inputs — and it conjugates each
  token by its *absolute index*, so clauses of different lengths are transported through
  different schedules. Across languages, differing length is the norm, so the rotor injects a
  length artefact into every cross-language comparison. This is exactly RQ2 of the June
  finding (*"is the position rotor drowning the semantic signal in path-order geometry?"*),
  answered by removing it rather than by measuring around it.
* **Order sensitivity is not lost by removing it.** The geometric product is non-commutative,
  so `F(w₁w₂) ≠ F(w₂w₁)` intrinsically. G3 below tests this as a requirement rather than
  assuming it — if word-order sensitivity turns out to depend on the positional hack, the
  claim was never geometric and G3 fails, which is a result worth having.

**R3 — resolve alignment edges by pack membership, not by an id-prefix table**, so the 63
currently-dropped edges participate. This is a load-time correction with no free parameters:
an edge whose target id belongs to no loaded pack becomes an error instead of a `continue`.

All three are applied in a scratch harness against a **copy** of the compiler. `../core`'s
committed compiler is not modified by this experiment — the repaired contract is admitted to
the keel (K1 `algebra/`, K3 `logos/`), and the experiment exists to tell the keel whether the
repaired design earns its place there.

## 3. The corpus, fixed now

* **Aligned triples** — every alignment edge that resolves after R3, grouped into
  he/grc/en clause triples. Expected order 20–40 usable triples from the 83 authored edges;
  the exact set is whatever R3 resolves, chosen by the resolver and not by hand.
* **Meaning-breaking negatives, three kinds, generated mechanically** so no negative is
  cherry-picked (the specific failure of the June measurement, which used one hand-chosen
  substitution):
  1. **Lexical substitution** — replace one content token with a token from a *different*
     primary semantic domain, every valid substitution enumerated, not sampled.
  2. **Word-order permutation** — ADR-0015's own stated test (*"word-order changes should
     change holonomy"*). Every non-identity permutation of clauses with ≤ 4 tokens.
  3. **Cross-triple pairing** — the English clause of triple *i* against the Hebrew/Greek
     clause of triple *j ≠ i*. This is the strongest negative class: same corpus, same
     lengths, same construction, different meaning.

**Amendment A1 (recorded before the run, no numbers seen).** R3 resolves more of the corpus
than this registration assumed: **24 aligned concepts**, of which 6 carry all three languages
and 18 carry two. Clause sets are therefore all `C(24,3) = 2,024` combinations rather than the
"20–40 triples" estimated above — a larger corpus than registered, in the direction that makes
the test harder to pass, not easier.

That makes negative class 3 complete-enumeration quadratic (≈4 M pairs). It is bounded by a
rule stated here, before any measurement: **for each aligned pair, the cross negatives are the
first 5 clause sets following it in the deterministic sorted enumeration that share no concept
with it.** Position in a sorted enumeration of concept keys is unrelated to meaning, so the
bound is unbiased; it is deterministic, so the experiment is reproducible; and the count of
generated negatives is reported, so nothing is dropped in silence. Classes 1 and 2 remain
**complete** — every valid substitution, every non-identity permutation.

The G2 threshold is **not** relaxed to compensate. A bound on how many negatives are drawn
does not change how well the aligned pairs must separate from them.

## 4. The criterion — committed, and deliberately unforgiving

Let `d(A,B)` be the loop-closure deviation of the cross-language loop (transport along clause
A, return along clause B): `d = ‖H − identity‖` after R2. Single declared metric; no
alternative is consulted after the fact.

**GO requires all four:**

| # | Condition | Threshold |
|---|---|---|
| G1 | **Separation** — aligned pairs close tighter than negatives | `median(d_aligned) < median(d_negative)` with **AUC ≥ 0.80** over all aligned vs all negatives |
| G2 | **Holds on the hardest class** — cross-triple negatives alone | **AUC ≥ 0.75** on class 3 |
| G3 | **Word-order sensitivity** — the ADR's own requirement | ≥ **90%** of non-identity permutations score `d` above their own unpermuted clause |
| G4 | **No collapse re-entry** — the repair must not buy separation by flattening | mounted `coordinates_lost` = **0** under R1 |

**NO-GO** if any of G1–G4 fails. **Any** of these outcomes is a full-credit result:

* GO → cross-language holonomy closure becomes the keel's L3 validation gate (ADR-0015 as
  designed), and the K3 contract carries it with these numbers as provenance.
* NO-GO with G4 held → the geometry does not carry meaning across representations *even on a
  clean, closed ground*. The pillar is then formally re-scoped: the depth packs stay as
  lexical and morphological resources, the "holonomy resonance is the validation gate" claim is
  struck from ADR-0005/0015 by amendment, and every document repeating it is corrected. This
  is the outcome that would retire the largest piece of unearned design in the system, and it
  is worth as much as a GO.
* NO-GO with G4 failed → the repair itself is wrong; report and stop. No third attempt at the
  same encoding without a new mechanism.

## 5. Anti-gaming rules, binding

1. **No threshold moves after numbers exist.** If a threshold is wrong, that is a finding to
   record, not an edit to make; the experiment re-registers under a new date and says why.
2. **No metric shopping.** `d` as defined in §4 is the only quantity consulted. The June
   failure mode — Euclidean norm "passing" where the owned similarity metric inverted — is
   forbidden by construction: one metric, declared here.
3. **No negative curation.** All three negative classes are generated mechanically and all
   generated negatives count. Dropping any requires a stated rule applied to all.
4. **The controls run first and are reported regardless of outcome:** aligned-vs-aligned (the
   floor), and identity-vs-identity (`d ≈ 0`, proving the instrument can report closure).
5. **The result is published whichever way it lands** — as an analysis doc with the raw
   numbers, next to this registration, in the commit that produces them.

## 6. What the answer changes

The keel's L3 design branches here, which is why FA-1 precedes K3:

* **GO** → `logos/` carries a real validation gate: a clause is admitted as understood when
  its cross-language loop closes. Perception (K4) gains a meaning criterion that is not
  template match — which is precisely the constraint the 1.28% read rate measures.
* **NO-GO** → `logos/` is admitted as lexicon + morphology only, the gate claim is retired,
  and K4's meaning criterion must come from somewhere else. That is a smaller keel, honestly
  scoped, and the Growth Law's *"coverage is data, not failure"* covers it.

Either way the keel gets a ruled foundation instead of an assumed one, which is the entire
purpose of running FA-1 before building on L2.

**Related:** `docs/analysis/logos-substrate-collapse-2026-07-28.md` (the defects this repairs)
· `docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md` (the prior negative and its
open questions RQ1–RQ3) · `docs/plans/2026-07-28-foundations-audit.md` §FA-1 ·
`docs/research/sme-experiment-verdict-797ebad5.md` (the pre-registration precedent).
