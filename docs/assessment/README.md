# docs/assessment/ — The Holistic Macro→Micro Assessment (2026-07-27)

A read-only, evidence-bearing assessment of CORE's cognitive-cycle design versus implementation fulfillment, conducted under `docs/conceptualizing_engineering_mastery.md` at `forgejo/main` @ `8927c563`. Phases 0–5 change no runtime behavior, fix no defect, and decide nothing — they produce evidence and judgments for ruling. Phase 6 adds the execution plan built on them and the ruling packet they require.

**Start here:** [`40-assessment.md`](40-assessment.md) — the synthesis (the verdict, the five frontiers, the recommended attack order). Then [`50-execution-plan.md`](50-execution-plan.md) for what follows from it, and [`50-rulings.md`](50-rulings.md) for what is waiting on a decision. The registers rank the work; the cards are the evidence base.

| File / dir | Phase | What it is |
|---|---|---|
| [`00-scope-and-method.md`](00-scope-and-method.md) | — | Charter, method, rules of engagement, phase/executor table |
| [`01-phase0-ground-truth.md`](01-phase0-ground-truth.md) | 0 | Corpus triage, the five unreconciled articulations, system-map recovery |
| [`02-layer-taxonomy.md`](02-layer-taxonomy.md) | 1 | The two-axis taxonomy: 7 macro layers + 2 cross-cuts over 33 zones; the Candidate Register (CR-1…4); completeness criteria |
| [`03-card-schema.md`](03-card-schema.md) | 1 | The card metadata schema: liveness ⊥ fitness, design ⊥ build, sabotage-tested evidence, `verified_at` stamps |
| [`10-layer-cards/`](10-layer-cards/) | 2 | Nine layer cards (M0–M6, MG, MV), every liveness label re-verified against code |
| [`04-phase2-findings.md`](04-phase2-findings.md) | 2 | Stage-coverage audit; corrections to Phase 0; findings F-1…F-5 |
| [`20-component-cards/`](20-component-cards/) | 3 | Eight component cards: the four zero-subsystem zones + always-on, derivation organs, surface selection, attention |
| [`05-phase3-findings.md`](05-phase3-findings.md) | 3 | Corrections C-1…C-5; findings F-6…F-10; the consolidated Phase-4 seed list |
| [`30-gap-register.md`](30-gap-register.md) | 4 | **The live gap register** — 22 entries (G-21, G-22 added during execution), 4 tiers, each with evidence + deciding authority; **supersedes `docs/gaps.md` and the substrate-liveness ratchet** per R-7 |
| [`31-hindrance-audit.md`](31-hindrance-audit.md) | 4 | Fourteen hindrances with fitness verdicts and better homes; eleven candidates examined and cleared (five in Phase 4, six in the 2026-07-28 external-assessment triage) |
| [`40-assessment.md`](40-assessment.md) | 5 | The synthesis |
| [`50-execution-plan.md`](50-execution-plan.md) | 6 | **The execution plan** — five waves + five frontier tracks over every G/H entry, with the dependency gates and the risks. §0 carries **nine** corrections to the assessment found while sizing and executing it; **§2.1 carries the adopted ruling docket and its execution order** |
| [`50-rulings.md`](50-rulings.md) | 6 | **The ruling packet** — R-1…R-14, each with evidence, options, a recommendation, and the exact diff that follows from each choice. **RULED 2026-07-28: twelve adopted, R-10 and R-14 stricken, §5 NO-GO ratified.** Wave 0's deliverable, and Wave 0 is closed |

**Maintenance contract** (from §8 of the synthesis): a card whose `verified_at` falls behind a load-bearing arc is testimony, not evidence. Update cards when their subsystems move, or this directory becomes the next dead instrument it was built to replace.

**Execution status (2026-07-28, `d0bedfc1`).** Phases 0–6 produced the evidence; the arc that followed executed everything in it that needed no ruling, and **Wave 0 then closed**: twelve rulings adopted, two stricken, the §5 **NO-GO ratified**. Landed: Track A's §5 verdict (pre-registered), PR-4 (+ pin 3), PR-6, PR-7, PR-9, PR-1, PR-3 + PR-3b (Wave 1, per R-7), and three defect fixes (H-13, H-8e, G-22). Closed: **G-7, G-9, G-22, H-7, H-11, H-13**. Added: **N-8, N-9, G-21, G-22, H-13, H-14**. What remains is **owed work, not open questions** — see [`50-execution-plan.md`](50-execution-plan.md) §Status for the board and **§2.1 for the adopted docket and its execution order**.

**Standing note:** the PR #138 fabrication findings appear throughout as *measured & pinned, fix held for ADR + ratification* — recorded, never re-discovered, never fixed here, per explicit instruction.
