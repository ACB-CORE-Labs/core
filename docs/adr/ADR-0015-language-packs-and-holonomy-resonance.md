# ADR-0015 — Language Packs as Compiled Linguistic Manifolds

**Status:** Accepted — **Crown Proof section AMENDED 2026-07-28: measured and not supported**  
**Date:** 2026-05-13

---

> ## Amendment · 2026-07-28 · the Crown Proof was tested and failed
>
> This ADR's "Crown Proof: Holonomy Resonance" section makes cross-language holonomy
> resonance **the validation gate of meaning** — *"This is the CORE-Logos proof"* — and the
> Consequences section lists *"Establishes holonomy-level resonance as the validation gate"*
> as a positive. **That claim is retired.** It was measured against a criterion registered
> before the run (`docs/analysis/fa1-holonomy-gate-preregistration.md`) and refused:
>
> * **AUC 0.557** separating aligned clauses from meaning-breaking ones (chance = 0.500,
>   required ≥ 0.80), over 1,016 aligned pairs and 58,375 mechanically-generated negatives;
> * **64.4%** word-order sensitivity against this ADR's own stated test (*"word-order changes
>   should change holonomy"*, required ≥ 0.90) — a third of permutations close the loop
>   *tighter* than the correct order;
> * measured on a ground with **zero coordinate collisions** and with a **genuinely closed
>   loop**, both of which had to be built first — the shipped compiler collapsed 37–53
>   coordinates and the shipped `holonomy_encode` never closed
>   (`docs/analysis/logos-substrate-collapse-2026-07-28.md`).
>
> **Diagnosis:** the encoding reacts more strongly to reordering a clause (median deviation
> 41.2) than to changing what the clause is *about* (32.2). It measures path shape, not
> content. The negative classes do order themselves correctly by meaning-distance, so the
> geometry is not noise — it is a weak correlation where the design asked for a gate.
>
> **What survives, unamended:** the three-language architecture with distinct roles, the pack
> contract, the compiled-manifold discipline, morphology as structure, and Hebrew root folding
> into geometry at compile time. What is struck is only the claim that holonomy closure
> *validates* meaning.
>
> **Verdict:** `docs/analysis/fa1-holonomy-gate-verdict-2026-07-28.md` ·
> **Tripwire:** `tests/test_fa1_gate_verdict.py` — if a future encoding makes the gate real,
> that test fails, and this amendment is withdrawn in the same commit that replaces it with a
> proof. The hypothesis was honestly stated and honestly testable; that is why it could be
> settled at all.

## Context

CORE's language philosophy is not localization. English, Hebrew, and Koine Greek
serve distinct architectural roles in CORE-Logos:

| Language | Role |
|---|---|
| English | Operational base and articulation surface |
| Hebrew | Depth-root language: root morphology, semantic compression, creation-word density |
| Koine Greek | Depth-relation language: Logos precision, case/aspect/voice/mood, clause relation |

The existing `sensorium/adapters/text.py` scaffold mounted `en`, `he`, and `grc`,
but the packs were only token lookup wrappers. That is insufficient for CORE.
A language pack must not be a dataset or a translation table. It must be a
compiled linguistic manifold.

---

## Decision

A CORE language pack is a deterministic, checksummed, compiled linguistic
manifold containing:

- a manifest with language role, script, normalization policy, source manifest,
  determinism class, checksum, gate state, and OOV policy;
- lexical entries and morphology entries;
- grammar attractors;
- cross-language resonance edges;
- holonomy alignment cases proving that aligned clauses produce coherent field
  path resonance.

## Terminology Boundary

This distinction is mandatory:

| Term | Meaning |
|---|---|
| Vocabulary point / manifold point | Position in the field; surface token entry |
| Transition rotor | Operator between points, constructed by algebra |
| Persona motor | Field-bias operator |
| Grammar attractor | Structural pressure seeded from recurring linguistic form |

Vocabulary entries are not transition rotors. Conflating point and operator is
an algebraic category error. The vocabulary may store multivectors/null points;
rotor construction belongs to the algebra layer.

## OOV Policy

Unknown surfaces must not silently collapse to a shared point.

| Pack role | OOV behavior |
|---|---|
| English operational/articulation | Tagged fallback may be used during early operation |
| Hebrew depth-root | Fail closed during and after seeding unless explicit expansion path is active |
| Koine Greek depth-relation | Fail closed during and after seeding unless explicit expansion path is active |
| Post-seeding expansion | OOV creates a vocab-expansion proposal; it is not projected silently |

Returning the same `e1` point for every unknown Hebrew or Greek form erases the
distinctions those languages exist to preserve; it is anti-Logos.

## Morphology / Semantics / Alignment

Morphology is operator composition. Semantic domain is attractor geometry.
Alignment is resonance. These must not be collapsed into one multiplication.

For Hebrew, composition order is load-bearing:

```text
V_surface = (((V_root · M_stem) · M_inflection) · M_affix_chain)
```

For Koine Greek, the pack should compose lemma anchors with case/aspect/voice/
mood/clause-role operators. The grammar relation is structural, not metadata.

Semantic domains seed attractors rather than becoming opaque morphology factors.
Cross-language alignment is a weighted graph, not a translation table.

## Crown Proof: Holonomy Resonance

Token-level alignment is necessary but insufficient. The decisive proof of the
three-language design is dynamic:

```text
holonomy(hebrew canonical clause)
  resonates with
holonomy(koine greek canonical clause)
  and maps coherently to
holonomy(english articulation clause)
```

Aligned clauses should produce nearby/coherent holonomies without flattening
their distinctions. Unrelated clauses should remain geometrically distinct.
Word-order changes should change holonomy. This is the CORE-Logos proof that
language packs preserve ordered field paths rather than merely mapping tokens.

The first holonomy alignment cases should be small and exact: Logos, beginning,
light, life, spirit, truth, covenant, grace, kingdom, creation.

---

## Consequences

**Positive:**
- Prevents future agents from treating language packs as datasets.
- Gives Hebrew and Koine Greek concrete architectural roles.
- Prevents silent OOV collapse in depth languages.
- Establishes holonomy-level resonance as the validation gate.

**Negative:**
- Requires a real Supervised Seeding Epoch before Hebrew/Greek gates engage.
- Requires deterministic morphology and grammar scaffolds before depth packs are
  operational.
- Requires carefully pinned canonical texts and checksums for D0 ingestion.

---

## Implementation Order

1. Terminology and schema foundation (`packs/schema.py`).
2. Pack roles and OOV policy in `sensorium`.
3. Split text adapters into English, Hebrew, Koine Greek specializations.
4. Add grammar scaffold artifacts.
5. Add tri-language resonance graph.
6. Add holonomy resonance proof cases.

No LLM extraction may feed the gate. Structural segmentation only.
