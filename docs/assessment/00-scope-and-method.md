# CORE Holistic Assessment — Scope and Method

**Status:** Ratified approach (Shay, 2026-07-27). Phase 0 complete.
**Branch:** `docs/holistic-assessment` (worktree `core-wt-assess`, based on `forgejo/main` @ `8927c563`).
**Nature:** Read-only investigation. This assessment changes no runtime behavior, fixes no defect, and decides nothing. It produces evidence and judgments for ruling.

---

## 1. The question being answered

Four questions, in order of dependency:

1. **Where does CORE actually stand** on its cognitive cycle — design articulated versus implementation fulfilled — from the telos down to individual components?
2. **Is the layer model itself complete?** Are there layers, sublayers, or components missing from the *design*, not merely from the implementation — things an AGI/ASI-grade system requires that nothing in the current architecture accounts for?
3. **What is the metadata for every layer, sublayer, and component?** Philosophical intent, functional contract, design shape, implementation status, evidence, capacity, and role — such that any future dive begins with a clear target rather than a grep.
4. **What is hindering us?** Implemented ADRs or designs that are the wrong solution for their underlying problem; responsibilities lodged in the wrong subsystem; trade-offs tuned rather than dissolved.

Question 4 is not a courtesy pass. It is the question with the highest expected value, because a wrong component that works is more expensive than a missing component that is known to be missing.

---

## 2. Governing method

The assessment is conducted under `docs/conceptualizing_engineering_mastery.md`, applied to the assessment itself and not only to its subject.

**Pillar I — Semantic Rigor.** Completeness criteria and the metadata schema are defined *before* any component is judged (Phase 1), so that "missing" and "complete" have fixed meanings rather than per-component ones. Every `implemented` verdict requires an evidence pointer: a test, an eval lane, a pinned SHA, or an acceptance packet. "The module exists" is not evidence that it executes; "the flag is threaded" is not evidence that it changes behavior.

**Pillar II — Mechanical Sympathy.** Components are judged against CORE's own doctrine — deterministic decoding, exact recall, field-as-substrate with intelligence in the wiring, replay-gated learning, `wrong=0`-or-refuse — and not against a generic AGI checklist. A capability only counts as a gap if CORE's own telos requires it. Importing an external architecture's expectations would manufacture false gaps.

**Pillar III — The Third Door.** The hindrance audit's explicit charter: find the places where a bad trade-off was split rather than dissolved, and the places where deletion beats addition. Per the execution algorithm, deletion (step 2) precedes optimization (step 3); a component that should not exist is never a performance problem.

**Two standing discipline rules carried in from prior work:**

- **The sabotage test.** For every claim that a mechanism is live and load-bearing, ask what the measurement would look like with the mechanism removed. If it would look identical, the claim is decoration and is recorded as such. This repository has produced exactly that failure before — a rate reported as evidence of a reader that was `0.0` throughout.
- **Identity, not value.** When measuring whether two things are the same thing, measure identity rather than equal-looking values. Source-scanning metrics can move the wrong way on success.

---

## 3. Phases and division of labor

| Phase | Deliverable | Executor |
|---|---|---|
| **0 — Ground truth** | Canonical-document ingestion; ADR triage; system-map recovery; raw material and open tensions for the taxonomy | Opus 5 — **complete** |
| **1 — Taxonomy & schema** | The macro→micro layer taxonomy and the metadata card schema every card must fill | Fable 5 |
| **2 — Macro layer cards** | One card per top-level layer; layer-level verdicts; cross-cutting concerns | Opus 5 |
| **3 — Micro component cards** | Per-subsystem descent, depth allocated by load-bearing-ness | Fable 5 |
| **4 — Gap register + hindrance audit** | Two separate registers; evidence-carrying | Fable 5 *(reassigned from Opus 5 by Shay, 2026-07-27)* |
| **5 — Synthesis** | Executive assessment; ranked gaps; ranked hindrances; recommended R&D attack order | Fable 5 *(same reassignment)* |

Phase 1 is the keystone. A wrong taxonomy miscategorizes everything downstream, and it is the cheapest phase to correct.

---

## 4. Deliverables

```
docs/assessment/
  00-scope-and-method.md      # this file
  01-phase0-ground-truth.md   # Phase 0 findings + Phase 1 handoff
  02-layer-taxonomy.md        # Phase 1
  03-card-schema.md           # Phase 1
  10-layer-cards/             # Phase 2
  20-component-cards/         # Phase 3
  30-gap-register.md          # Phase 4
  31-hindrance-audit.md       # Phase 4
  40-assessment.md            # Phase 5
```

---

## 5. Rules of engagement

1. **Read-only.** No runtime code is modified. No defect is fixed. Where a fix is obvious, it is recorded as a finding with its evidence, not applied.
2. **Verify against code, not against documents.** Documentation in this repository has been measurably wrong about the repository before — most recently `docs/research/architecture-assessment-verification-2026-07-25.md` falsified roughly a third of an external blueprint's work items by reading the implicated code. A claim sourced only from a document is labeled as such.
3. **Settled rulings are constraints, not subjects.** The deduction pivot, the scripture-content deferral, the no-merge-automation rule, and ratified ADRs enter as given. An ADR is reopened only on evidence of hindrance, and only as a flag for ruling — never as a unilateral recommendation to reverse.
4. **Known-and-held findings are recorded as such.** The PR #138 fabrication findings (`every dog is a mammal` → `member(every_dog, mammal)`; `Given: furthermore; p implies q; p.` reaching served output) are **measured and pinned, not fixed**. The fixes are known — two of the 13 mutations — and are deliberately held out pending ADR and ratification because they change what CORE comprehends from user input, which is serving-path truth behavior. They enter the gap register pre-labeled and are never re-presented as newly discovered.
5. **No timelines.** Scope size, phase, and priority only.
6. **All wrinkles surfaced.** Technical truths are volunteered unprompted, including ones that complicate the picture or reflect badly on prior work.
