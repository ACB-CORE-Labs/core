# Finding: the semantic ground collapses — "alignment" is implemented as overwrite

**Date:** 2026-07-28 · measured at `472fc0a8` · **FA-1** of the Foundations Audit · **G-25**
**Status:** substrate finding, L2. Load-bearing for every layer above it, for the keel's
`logos/` and `algebra/` contracts (K1/K3), and for the standing question of why capability
has not moved.

---

## 0. The one-sentence finding

`packs.compiler._blend_feature_versors` — the function every cross-language and
morphological "nudge" in the system calls, at three sites, with three different declared
strengths — **ignores its strength argument and returns the target verbatim**. Nothing in
CORE is blended toward anything. Aligned words are *overwritten* by their partners, so the
three-language manifold ADR-0005/0015 designs as three charts on one semantic space is, in
the mounted configuration the runtime actually uses, **one chart with aliases**.

```python
def _blend_feature_versors(source, target, strength):
    strength = max(0.0, min(1.0, float(strength)))
    if strength <= 0.0:
        return np.asarray(source, dtype=np.float32).copy()
    return np.asarray(target, dtype=np.float32).copy()   # ← any strength > 0
```

ADR-0015 states the requirement this violates twice over: aligned clauses must resonate
*"without flattening their distinctions"*, and *"cross-language alignment is a weighted
graph, **not** a translation table."* It is a translation table, applied destructively.

## 1. What it costs, measured

Instrument: `evals/logos/manifold_collapse.py`. Coordinates are compared **bit-exactly**
(`ndarray.tobytes()`) — there is no tolerance to tune, and no metric to argue about. Pinned
by `tests/test_manifold_collapse_floor.py` (registered in `smoke`).

| Configuration | surfaces | distinct coordinates | **lost** | groups |
|---|---|---|---|---|
| `en_minimal_v1` alone | 220 | 220 | **0** | 0 |
| `grc_logos_micro_v1` alone | 11 | 11 | **0** | 0 |
| `he_logos_micro_v1` alone | 9 | 8 | 1 | `אור`/`אוֹר` |
| **trilingual mounted** | **239** | **202** | **37** | **11** |

**Mounting the depth packs — the operation designed to *add* depth — removes 37 distinct
coordinates.** English alone is collision-free; English mounted with Hebrew and Greek is not.

The eleven collapsed groups, verbatim:

```
ask · how · question · what · when · where · which · who · why · ἐρωτάω
begin · beginning · origin · source · ראשית · ἀρχή
breath · spirit · πνεῦμα · רוח
create · image · κτίζω · ברא
light · φῶς · אוֹר · אור
read · receive · silence · λαμβάνω
say · speak · voice · λέγω
word · λόγος · דבר · דברים
answer · respond · ἀποκρίνομαι
truth · אמת · ἀλήθεια
life · חיים
```

Read the first line again. **Nine English question words occupy one coordinate.** In the
semantic ground the reader stands on, *who*, *why*, *when*, *where*, *how* and *which* are
the same point — and they are collapsed not by any English-side decision but because one
Greek verb, `ἐρωτάω`, shares their primary semantic domain and drags the whole group into
the multi-language branch. `read`, `receive` and `silence` are likewise one point.

**Attribution** (measured by disabling each site in turn):

| Site | lost coordinates | what it does |
|---|---|---|
| `_apply_mounted_primary_domain_resonance` (mount time, strength `0.40`) | **34** | overwrites *every member* of a multi-language primary-domain group with the English prototype |
| `_apply_alignment_corrections` (pack load, strength `weight × 0.10`) | 2 | overwrites the home token with the foreign token, last foreign pack wins |
| `_apply_morphology_cluster_corrections` (compile, strength `0.40`) | 1 | overwrites every same-root form with the cluster prototype |

The mount-time site is the dominant cause and carries a comment that named the open question
precisely — *"it does not yet isolate structural derivation (Hebrew/Greek morphology
operators) from this function's nudge"* — and pointed at `docs/handoff/ADR-0167-FOLLOWUPS.md`
§6, **a file that does not exist**. The isolation question is now answered: there is no
structural derivation left to isolate, because the 0.40 "blend factor" is a 1.00 replacement.

## 2. The inversion this produces

ADR-0005 assigns the roles: Hebrew as **depth anchor**, Greek as **relational depth**,
English as **articulation surface**. The mount-time prototype rule is
`next((surface for language, surface in surfaces if language == "en"), surfaces[0][1])` —
**English is preferred as the prototype**, and every other language is replaced by it.

The design's dependency runs exactly backwards. The depth languages do not anchor English;
they are deleted into it. `דבר` is not *near* `word` in the mounted manifold — it **is**
`word`, bit for bit, and so is `λόγος`, and so is `דברים`.

At pack-load time the same function runs with the foreign packs in `sorted()` order, so
`he[דבר]` is first overwritten by `en[word]` and then by `grc[λόγος]`: **which language a
Hebrew token becomes is decided by the alphabetical order of pack ids.**

## 3. Four "resonance proofs" that pass because the compared quantities are identical

`docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md` audited the *clause*-level
resonance and found it decoration. It explicitly deferred the token-level tests: *"whether
each is robust or another cherry-picked configuration is an open follow-up, not covered by
this finding."* That follow-up is now closed, and the answer is worse than cherry-picking:

| Test | Why it passes |
|---|---|
| `test_light_alignment_clusters_across_mounted_trilingual_field` | `cga_inner(light, אוֹר)` = `3.0220894813537598` = `cga_inner(light, light)`. The versors are the same array. |
| `test_triple_alignment_closer_than_other_triples` | same — aligned pairs are self-comparisons |
| `test_same_root_hebrew_forms_land_closer_than_unrelated_noun` | `דבר` and `דברים` are bit-identical after clustering |
| `test_structured_morphology_improves_same_root_hebrew_resonance` | asserts structured > unstructured for the same-root pair; structured makes them **identical**, so the "improvement" is total collapse |

The last one is the sharpest: a test named for an *improvement in resonance* is green
precisely because the distinction it should preserve was destroyed.

This is the repo's own disease definition met exactly — *"a test that passes under conditions
that bypass the obligation it nominally proves is decoration, not proof"* — and it is the
fourth independent instance this arc (CLAIMS.md staleness G-22, `DOMAIN_PACKS` G-23, the
hollow distinct-evidence guard in PR-12, and now the semantic ground itself).

## 4. The second defect: 63 of the 83 alignment edges are silently discarded

The audit charter recorded the alignment corpus as *"seed-scale: 11 edges… the ADR's
prescribed first cases, never grown beyond them."* **That is wrong, and the way it is wrong
is the finding.** Four packs carry `alignment.jsonl`:

| Pack | edges authored | edges that resolve | in serving? |
|---|---|---|---|
| `he_logos_micro_v1` | 11 | 11 (as overwrites) | secondary |
| `grc_logos_micro_v1` | 9 | 9 (as overwrites) | secondary |
| `he_core_cognition_v1` | **22** | **0** | **primary** (`chat/pack_grounding.py:57`) |
| `grc_logos_cognition_v1` | **41** | **0** | **primary** (`chat/pack_grounding.py:56`) |
| **total** | **83** | **20** | |

The corpus *was* grown — 7.5× beyond the seed, to 83 edges — and **76% of it is inert**.

The mechanism is four lines. `_infer_foreign_pack_ids` decides which foreign pack an edge
points into by splitting `target_id` on `"-"` and looking the first field up in a hardcoded
three-entry table:

```python
_PREFIX_TO_PACK = {"he": "he_logos_micro_v1", "grc": "grc_logos_micro_v1", "en": "en_minimal_v1"}
prefix = edge.target_id.split("-")[0]
```

`en-core-cog-001` has prefix `"en"`, so it resolves to `en_minimal_v1` — a pack with no such
entry id. The lookup misses, `_apply_alignment_corrections` hits `continue`, and the edge
vanishes without a warning, a counter, or a test. Entry ids are pack-local; the resolver is
global and frozen at three pack names, so **any pack beyond the original three is unreachable
by construction** — including the two that serving actually grounds Hebrew and Greek against.

Both branches of the pillar therefore fail, in opposite directions: the packs whose alignment
*works* destroy distinctions, and the packs serving actually uses have alignment that does
nothing at all. FA-1's work-order item 4 — *"grow-or-declare the alignment corpus"* — is
answered before it begins: it was grown, and the growth was never connected.

## 5. The third defect: `holonomy` does not close

Independent of the collapse, the object named `holonomy` is not one.

`algebra/holonomy.py` documents, in the module docstring and in the function docstring:

> *A prompt is encoded as the geometric holonomy of its forward+reverse versor walk.
> **The walk closes**… Forward walk: F = w1·…·wn · Reverse walk: R = (1−alpha)·reverse(wn)·…·reverse(w1) · Holonomy: H = F · R*

The implementation computes `F` and returns it. There is no `R`. Commit `fca6216e`
("Stabilize holonomy accumulation", 2026-05-13) **deleted the reverse accumulation and kept
the docstring that describes it** — the original at `b80dd57a` did compute
`H = geometric_product(F, R)`. Consequences, measured:

* `alpha` is validated (`0.0 <= alpha <= 1.0`) and then **never read**. `holonomy_encode(v, alpha=0.0)`
  and `holonomy_encode(v, alpha=1.0)` return bit-identical arrays. `core/physics/biography.py:94`
  passes `alpha=alpha` into it — a caller steering a parameter that does nothing.
* A walk followed by its own reverse does not return to identity (scalar `164.6`, non-scalar
  norm `4044.2`). A closed-loop transport must; an open path product need not, and this is one.

ADR-0015's validation gate is **closure** — `holonomy(he) ≈ holonomy(grc) ≈ holonomy(en)`.
A quantity that never closes has no reason to be invariant across representations, so the
2026-06-14 negative result was not a surprising failure of the geometry: it is what this
implementation predicts. That doc's open question RQ2 — *"is the per-token `_position_rotor`
injection drowning the semantic signal in path-order geometry?"* — was aimed correctly and
could not see the deletion, because the docstring said the closure was there.

## 6. The cure was already in the algebra layer, one import away

A linear blend of two versors is not a versor — the Cl(4,1) versor group is not closed under
addition — and `VocabManifold.update()` correctly refuses non-versors (`residual > 1e-5`).
Substituting a naive lerp for the overwrite raises `ValueError: Word 'דברים': replacement
versor residual 3.68e-02 exceeds 1.0e-05` immediately. **The overwrite is what a lerp
degrades into once the guard rejects it.** The guard was right; the escape was wrong.

The correct operation is interpolation *on the group* — the geodesic from source to target in
Spin(4,1) — and `algebra/rotor.py` has implemented it since the algebra layer's first commit:

```python
blended = geometric_product(rotor_power(word_transition_rotor(source, target), strength), source)
```

Measured on `en[word] → en[light]`: unit residual stays at `~1e-7` for every `t` (three
orders of magnitude inside the manifold's tolerance), `t=0` returns the source exactly,
`t=1` the target exactly, and intermediate `t` genuinely interpolates.

So the deepest layer built the exact tool the layer above it needed, and the layer above
never called it. That is the Foundations Audit's thesis — *layers assuming connections that
were never made* — at the foundation, with both halves of the connection present and unjoined.

## 7. Why this is the answer to "why hasn't capability moved"

Every geometric experiment this project has run was run on this ground:

* the field-reasoner wedge (2026-06-04) — **decoration**,
* the relational-operator ablation (2026-07-19) — **identical to the symbolic baseline**,
* ADR-0252 §5 structure-mapping (2026-07-28) — **NO-GO at every attribute weight**,
* cross-language holonomy resonance (2026-06-14) — **anti-correlated**.

The convergent explanation recorded in the Perception Arc was *"wherever the geometric
operation is isomorphic to the arithmetic it replaces, it reproduces it exactly."* That is
true and insufficient. The measurement here adds the missing half: **the geometry had been
erased before the experiments started.** A fifth of the mounted vocabulary shares coordinates
with something else; the tokens that carry question type are one point; the depth languages
are aliases of English. No operator defined over that ground can distinguish what the ground
does not distinguish, so "geometry adds nothing" was the only available result.

This does **not** retroactively make those experiments positive — they were well-controlled
and their verdicts stand for the encodings they tested. It changes what they are evidence
*of*: they measured operators over a collapsed ground, not the value of geometric operators.
The reopening criterion in the foundations audit §4 — *"a domain where the geometric encoding
is not isomorphic to a trivial symbolic computation"* — is now joined by a second, stronger
one: **re-run on a ground that has not been flattened.**

## 8. Disposition

Not repaired here. `../core` is the quarry and the evidence source; L2 is rebuilt in the keel
(`coreai`, K3), where the corrected contract is admitted with these measurements as its
provenance. Repairing the compiler in place would move every versor in the system, and the
blast radius includes four tests whose current green depends on the collapse — those are
**decoration to be replaced with real proofs**, not regressions to be preserved, and doing
that properly is the keel's K3 work, not a patch here.

What lands here instead:

1. **The instrument** — `evals/logos/manifold_collapse.py`, deterministic, bit-exact.
2. **The pin** — `tests/test_manifold_collapse_floor.py` in `smoke`, both directions: the
   collapse may not widen silently, and it may not shrink silently either. Two sabotages
   observed red (a real interpolation → `ValueError` from the versor guard; disabling the
   mount-time site → `37 → 3`, which is also how the 34/2/1 attribution above was measured).
3. **The four decoration tests are left standing and named here.** They are not weakened in
   this commit: a test that is green for the wrong reason and a test that is red are different
   signals, and the honest move is the one the 2026-06-14 doc made — record exactly why each
   is green, so replacing it is a decision someone makes with the evidence in hand.

## 9. What FA-1 asks next — pre-registered separately

Whether a *repaired* ground discriminates meaning is a question with a criterion, and the
criterion is committed before the run (`docs/analysis/fa1-holonomy-gate-preregistration.md`),
the way ADR-0252 §5 was decided. The mechanism is proven; the capability is not claimed.

**Related:** `docs/analysis/holonomy-resonance-proof-not-robust-2026-06-14.md` (the clause-level
negative this extends) · `docs/plans/2026-07-28-foundations-audit.md` (FA-1) ·
`docs/assessment/30-gap-register.md` (G-25) · `coreai/docs/atlas/00-atlas-overview.md` (K1/K3).
