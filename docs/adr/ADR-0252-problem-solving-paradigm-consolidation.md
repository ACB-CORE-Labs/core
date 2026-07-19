# ADR-0252: Problem-Solving Paradigm Consolidation — Retire Six Competing Unratified Formulations

**Status**: Accepted — this ADR is a **decision record only**. It records that the six paradigm
formulations below are retired and archived, and that a single governing comprehension-and-solving
paradigm will be authored under this same ADR number as a separate, human-led step. **This ADR does
not itself define that paradigm.**
**Date**: 2026-07-19
**Deciders**: Joshua Shay (ruling authority) + Claude (consolidation executor, this pass)
**Related**: ADR-0164 (Incremental Comprehension Reader — Accepted, unmoved, annotated
`Superseded-by: ADR-0252` per this decision), ADR-0174 (Held-Hypothesis Comprehension — Accepted,
unmoved, annotated `Superseded-by: ADR-0252` per this decision), ADR-0243/0249/0250/0251 (current,
unaffected — see §3)
**Companion doc**: `docs/research/paradigm-deadcode-audit-2026-07-19.md` (the dead-code audit this
consolidation performed)

---

## 1. Context — six competing, unratified paradigm documents

Between 2026-06-17 and 2026-06-20 the repository accumulated six distinct, mutually-competing
problem-solving-paradigm formulations, none of which was ever ratified as an ADR. They sat alongside
each other in `docs/analysis/`, `docs/handoffs/`, and `docs/implementation/`, each proposing a
different shape for "how CORE should comprehend and solve a problem":

1. **Semantic-substrate master plan** —
   `docs/analysis/semantic-substrate-problem-solving-master-plan-2026-06-20.md`
2. **Semantic state-transition blueprint** —
   `docs/handoffs/SEMANTIC-STATE-TRANSITION-BLUEPRINT.md`
3. **Semantic/symbolic binding-graph proposal** —
   `docs/implementation/semantic-symbolic-binding-graph-proposal.md`
4. **Problem-solving capability roadmap v2** —
   `docs/analysis/core-problem-solving-capability-roadmap-v2-2026-06-17.md`
5. **GSM8K capability-paradigm sprint lookbacks** (eight dated retrospectives, one formulation
   iterated sprint-to-sprint) —
   `docs/analysis/gsm8k-capability-paradigm-sprint{5,6,7,8,9,10,11,12}-lookback-2026-06-17.md`
6. **ADR-0174's deprecated in-ADR dispatch prescription** — the per-category injector dispatch table
   and legacy-regex-parser fallback that ADR-0174 itself marked `Deprecates:` in its header (see
   ADR-0174 §Deprecates). ADR-0174 as a whole remains Accepted; only this specific dispatch
   prescription is superseded.

None of formulations 1–5 was ever promoted to ADR status. They were parallel, competing drafts —
none governing, none ratified, several mutually inconsistent about what "comprehension" and "solving"
should mean architecturally. Carrying six live-looking documents that read as authoritative but were
never ruled on is a standing hazard: a future reader (human or agent) has no way to tell which one, if
any, is load-bearing.

## 2. Decision

Retire all six formulations. Move documents 1–5 (ten files total, including the eight sprint
lookbacks) to `docs/paradigm-archive/`, each prefixed with:

```
> SUPERSEDED 2026-07-19 — consolidated under ADR-0252. Archived, not governing.
```

They are preserved for historical reference (the sprint lookbacks in particular record real,
verified measurement history) but carry no governance weight.

Formulation 6 (ADR-0174's deprecated dispatch prescription) is handled differently because ADR-0174
is itself an Accepted ADR and a permanent record: it is **not moved**. Instead, both ADR-0164 (the
parent ADR) and ADR-0174 receive a `**Superseded-by:** ADR-0252` line in their header, alongside their
existing `Status: Accepted`, to make the relationship explicit without rewriting history.

A single governing comprehension-and-solving paradigm will be authored under this ADR number,
**as a separate, human-led step** — not as part of this consolidation pass. See §4.

## 3. What this decision does NOT touch

This is a documentation-retirement decision plus a dead-code cleanup pass (audited separately in
`docs/research/paradigm-deadcode-audit-2026-07-19.md`). It does not change runtime behavior: the
serving reader's `wrong=0` and the full smoke/test/holdout numbers are required to be byte-identical
before and after every code removal performed under this consolidation (see the companion audit doc
for the baseline and post-removal numbers).

Explicitly unaffected and not superseded by this ADR:

- ADR-0243 (propositional falsifier), ADR-0249 (reader→Hamiltonian compiler composition frontier),
  ADR-0250 (tier-2 multi-entity arithmetic), ADR-0251 (reader-arc recalibration) — all current and
  standing.
- The `#77`/`#78` compare-multiplicative compiler tier and `NEUTRAL_COUNT_VERBS` positive-polarity
  foundations.
- Any module proven live by the companion dead-code audit (importers, test coverage, or ADR
  reference found) — those stay, even if a retired document originally proposed or referenced them.

## 4. The paradigm — TO BE AUTHORED (human-led)

This section is an explicit placeholder. The single governing comprehension-and-solving paradigm that
formulations 1–6 were each independently groping toward has not been authored. It is out of scope for
this consolidation pass and is reserved for a separate, human-led step under this same ADR number.
