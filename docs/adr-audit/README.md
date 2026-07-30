# docs/adr-audit/ — The ADR Audit (started 2026-07-29)

A read-only, evidence-bearing audit of every ADR in `docs/adr/` against the codebase, the three engineering pillars, the seven axioms, the Whitepaper/Yellowpaper, and each other — plus a necessity/generality pass asking which components are irreducible and which duplicate what the geometric substrate already provides. Full rationale: `docs/plans/2026-07-29-adr-audit-plan.md`. Working charter: `00-scope-and-method.md`.

**If you are resuming this work cold** (new session, new subagent, compacted context): read `MANIFEST.md` first — it's the single source of truth for what batch/phase is done vs. pending. Then `00-scope-and-method.md` for the charter. Then proceed.

| File / dir | Phase | What it is |
|---|---|---|
| [`00-scope-and-method.md`](00-scope-and-method.md) | — | The charter: pillars, axioms, discipline, tiering, execution order |
| [`MANIFEST.md`](MANIFEST.md) | — | **Batch tracker.** Check this before doing anything else. |
| [`TEMPLATE-adr-card.md`](TEMPLATE-adr-card.md) | — | Per-ADR fill-in template (Tier B/C) |
| [`TEMPLATE-stack-dossier.md`](TEMPLATE-stack-dossier.md) | — | Per-stack fill-in template (Tier A) |
| [`01-adr-census.md`](01-adr-census.md) | 1 | Full 314-file inventory, numbering-collision disambiguation, phased-family list |
| [`02-stack-taxonomy.md`](02-stack-taxonomy.md) | 2 | ADRs mapped onto `docs/assessment/02-layer-taxonomy.md`'s zones, tiered |
| [`10-stack-dossiers/`](10-stack-dossiers/) | 3 | Tier A dossiers. `A1`–`A5` = Batch 1, `A2.1`–`A2.6` = Batch 2, `Batch3–6-*-redo.md` = Batches 3–6. **`*-consolidated.md` files are RETRACTED** — do not cite (see `20-finding-register.md`) |
| [`11-adr-cards/`](11-adr-cards/) | 3 | Tier B cards. `B1`–`B6` = Batch 1, `B2.1`–`B2.7` = Batch 2, `Batch3-TierB-redo.md` = Batch 3. **`*-consolidated.md` = RETRACTED** |
| [`12-triage-log.md`](12-triage-log.md) | 3 | Tier C: rapid-triage log, one row per singleton/scope-note |
| [`20-finding-register.md`](20-finding-register.md) | 4 | The `AA-N` finding ledger |
| [`21-drift-report.md`](21-drift-report.md) | 4 | Whitepaper/Yellowpaper/prior-ADR contradictions |
| [`22-consolidation-report.md`](22-consolidation-report.md) | 4 | Necessity/generality clusters — the parsimony pass |
| [`30-alignment-matrix.md`](30-alignment-matrix.md) | 4 | Master table, one row per ADR (Batch 1 complete; Batches 2–6 verdicts live in their dossiers) |
| [`40-triage-queue.md`](40-triage-queue.md) | 5 | Ranked 🔴 Block / 🟡 Repair / 🔵 Consolidate / 🟢 Monitor |
| [`50-cross-batch-synthesis.md`](50-cross-batch-synthesis.md) | 6 | **Start here for the corpus-level result** — four corpus-wide governance patterns, what the audit got wrong about itself, and the ordered remediation program |
| `99-orchestration-log.md` | — | Log written by the retracted external pass; retained as a record of that episode, not as audit evidence |

**Status (2026-07-29): COMPLETE — all six batches, 314/314 ADRs.** Batches 3–6 were redone after an external pass over them was retracted for unreliability (fabricated artifact citations, a silent severity downgrade, and near-zero critical findings in territory already proven to have them) — full evidence in `20-finding-register.md`'s retraction notice; `AA-331`–`AA-438` are void and real findings resume at `AA-439`.

**Read in this order:** `50-cross-batch-synthesis.md` (the result) → `40-triage-queue.md` (what to do) → `20-finding-register.md` (every finding) → the dossiers/cards (the evidence). `MANIFEST.md` is the resume point for any unfinished work.
