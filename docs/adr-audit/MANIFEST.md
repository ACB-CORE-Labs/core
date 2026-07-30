# ADR Audit — Batch Manifest

**Purpose:** the single file that survives context loss between sessions/subagents. If you are picking this work up cold — new session, new subagent, context got compacted — **read this file first**, then `00-scope-and-method.md` for the charter, then go to whichever batch row below is not `done`. Everything needed to resume lives in this tree; nothing about audit state should ever depend on conversation history.

Batches are numeric-sequence blocks of the ADR corpus (per `01-adr-census.md` §4), not priority order — a batch can, and Batch 1 does, contain a mix of Tier A/B/C ADRs. Tier is assigned per-ADR/per-stack in Phase 2/3, independent of which batch it's scheduled in.

## Batch table

| Batch | Range | Files | Phase 1 (census) | Phase 2 (stacks) | Phase 3 (audit) | Phase 4/5 (synthesis) |
|---|---|---|---|---|---|---|
| 1 | ADR-0001–0050 | 50 | done | done | **done** (5 Tier A dossiers, 6 Tier B zone-cards, 3 Tier C triage rows — 50/50) | **done** (158 findings, 13 🔴/68 🟡/25 🔵/52 🟢) |
| 2 | ADR-0051–0100 | 52 | done | done | **done** (6 Tier A dossiers, 7 Tier B zone-cards, 1 Tier C triage row — 52/52) | **done** (171 findings, 19 🔴/71 🟡/22 🔵/59 🟢) |
| 3 | ADR-0101–0150 | 91 | done | done | **done (REDO)** — `Batch3-TierA-redo.md` (53 ADRs, 19 findings, **5 🔴**) + `Batch3-TierB-redo.md` (38 ADRs incl. 3 the retracted map omitted, 26 findings) + 3 Tier C rows | **done** — `AA-439`–`AA-483` |
| 4 | ADR-0151–0200 | 56 | done | done | **done (REDO)** — 56/56 across 3 files: `-carryforward-` (0180/0181/0196/0197), `-reader-reliability-` (0164 fam/0165/0174/0175, **1 🔴**), `-redo-` (44 files, **3 🔴**, 25/44 status mismatches) | **done** — `AA-484`–`AA-492`, `AA-515`–`AA-540` |
| 5 | ADR-0201–0250 | 50 | done | done | **done (REDO)** — all 50 direct by main session across 4 files: `-cascade-` (0239–0246, **1 🔴**), `-collisions-` (0225×2/0226×3), `-misc-` (0237/0238), `-remainder-` (sweep of 37, **1 🔴**) | **done** — `AA-493`–`AA-506` |
| 6 | ADR-0251–0265 | 15 | done | done | **done (REDO)** — `Batch6-TierA-redo.md`, 15/15, audited directly by the main session | **done** — `AA-507`–`AA-514` (0 🔴/2 🟡/0 🔵/6 🟢) |

Phase 1 (the full 314-row mechanical census) is corpus-wide and already complete for every batch — see `01-adr-census.md`. Phase 2 onward is genuinely per-batch.

**⚠ Batches 3–6 retraction (2026-07-29):** an external process audited these batches while this Claude session was over its usage limit, without review. An audit-of-the-audit found the work unreliable (see `20-finding-register.md`'s retraction notice for full evidence — a direct, verified contradiction with an already-registered Batch 2 finding, a silent severity downgrade of a Batch 1 🔴, and a statistically implausible near-zero critical-finding rate against Batches 1-2's baseline). Findings `AA-331`–`AA-438` are void. The stack/zone **groupings** in `10-stack-dossiers/Batch3–6-*-consolidated.md` and `11-adr-cards/Batch3–5-*-consolidated.md` (which ADRs cluster together) are kept as reusable Phase 2 scaffolding; their verdicts are not. Redo resumes finding numbering at `AA-439`.

**Batch 3 note:** 91 files is roughly double the others because it swallows the `0114` (7 files) and `0131` (16 files) phased families whole — both are Tier A on their own merits (expert-promotion contract and the math-expert benchmark re-target) and are internally sequential, so they can't be split across batches. When Batch 3 comes up, expect to treat it as two sub-passes (families first, then the remaining ~68 singleton/small-stack files) rather than one uniform pass.

## Status definitions

- **not started** — nothing produced yet for this batch at this phase.
- **in progress** — some ADRs in this batch/phase have output, not all. Check the relevant deliverable file's own per-ADR status before assuming coverage.
- **done** — every ADR in this batch has a completed artifact at this phase, cross-checked against `01-adr-census.md`'s row count for that range.

## Per-batch deliverable locations

- Phase 2 output lives in `02-stack-taxonomy.md`, appended per batch (not one file per batch — stacks can span batch boundaries when a phased family straddles a `0050`/`0100`/etc. line, though none currently do).
- Phase 3 output: `10-stack-dossiers/<zone-or-family>.md` for every Tier A stack, `11-adr-cards/<zone>.md` for Tier B (one file per zone, all its ADRs' cards inside), `12-triage-log.md` appended per Tier C ADR.
- Phase 4/5 output: `20-finding-register.md`, `21-drift-report.md`, `22-consolidation-report.md`, `30-alignment-matrix.md`, `40-triage-queue.md` — all corpus-wide files, appended per batch as each batch's Phase 3 completes. Do not create per-batch copies of these five; append rows/sections and note which batch contributed them.

## Batch 1 — closed (ADR-0001–0050)

All 50 ADRs audited: 5 Tier A dossiers (`10-stack-dossiers/A1`–`A5`), 6 Tier B zone-cards (`11-adr-cards/B1`–`B6`), 3 Tier C triage rows (`12-triage-log.md`). 158 findings rolled into `20-finding-register.md` (`AA-1`…`AA-159`, `AA-40` a documented gap). Synthesis complete: `21-drift-report.md`, `22-consolidation-report.md`, `30-alignment-matrix.md`, `40-triage-queue.md`. Index repair done: `docs/adr/INDEX-by-domain.md` count and numbering-note corrected.

**Headline result:** the FA-1 cascade check (charter's day-one priority) found 19 ADRs + 2 non-ADR records depending on the retired cross-language-holonomy claim, independently corroborated by a from-scratch algebra-layer measurement in stack A1 (both converged on the same root cause via different methods). See `21-drift-report.md` §1.

**Cross-batch carry-forward — pre-flag these as Tier A on arrival, don't re-derive the FA-1 dependency cold:**

| ADR | Lands in batch | Why pre-flagged |
|---|---|---|
| 0073, 0073a–d | **2** (0051–0100) — *corrected; originally misrouted to Batch 3, caught while building Batch 2's ADR list* | FA-1-cascade mechanism — dominant collapse site (`AA-74`); this is also a 5-file phased family in Batch 2's own range, independently Tier A on complexity grounds |
| 0102, 0103 | 3 (0101–0150) | FA-1-cascade — live ledger license resting on the defective claim (`AA-75`) |
| 0180 | 4 (0151–0200) | FA-1-cascade — "supreme architectural invariant" premise (`AA-64`) |
| 0181, 0197 | 4 (0151–0200) — *corrected, both in range* | FA-1-cascade — inherited premise (`AA-66`, `AA-67`) |
| 0239, 0240, 0241, 0243, 0244, 0246 | 5 (0201–0250) | FA-1-cascade — implementation/downstream/boundary (`AA-68`–`AA-72`) |
| 0253, 0261 | **6** (0251–0265) — *corrected; 253 > 250, both in Batch 6* | FA-1-cascade — boundary freeze / reserved-unallocated NO-GO annotation (`AA-80`, `AA-73`) |
| 0254 | **6** (0251–0265) — *corrected; 254 > 250* | Adds a third independent hedge-injection mechanism, per B4's `AA-142` — pull into whatever stack covers hedging in Batch 6 |
| 0196 | 4 (0151–0200) | Generalizes the Rust bit-identity dispatch pattern B3 flagged as sound (`AA-138`) — verify the generalization inherited the pattern's caveats |

**Lesson for future batches:** double-check every carry-forward ADR number against the actual batch boundary table (§Batch table above) before filing it — arithmetic-by-eye on 4-digit numbers is error-prone, as this correction demonstrates.

## Batch 2 — closed (ADR-0051–0100)

All 52 ADRs audited: 6 Tier A dossiers (`A2.1`–`A2.6`), 7 Tier B zone-cards (`B2.1`–`B2.7`), 1 Tier C triage row. 171 findings (`AA-160`–`AA-330`) — spot-checked and confirmed reliable (see `20-finding-register.md`'s retraction notice for the contrast with Batches 3–6). Headline: stack A2.1 substantially revised Batch 1's `AA-74` (the specific collapse mechanism didn't hold up under independent re-derivation) but replaced it with a sharper finding — anchor-lens output is byte-identical across every lens, proven by running the demo; the axis reads no versor/rotor/manifold state at all. Stack A2.5 (capability ledger ratifications) produced 4 🔴 findings after recovering from a mid-run session-limit failure — verified reliable by direct spot-check (`AA-233` confirmed against `core/capability/reporting.py:428-434`).

**Batches 3-6 status:** see the retraction notice above — Phase 3/4/5 revert to not-started, Phase 2 groupings reusable.

~~Next action when resuming: redo Batch 3 Phase 3 using the existing stack/zone groupings in `10-stack-dossiers/Batch3-TierA-consolidated.md` / `11-adr-cards/Batch3-TierB-consolidated.md` as a starting map (not as evidence), explicitly checking the full `20-finding-register.md` and the FA-1 cascade list (`21-drift-report.md` §1) before scoring any ADR — this is the step that failed last time. Then Phase 4/5, findings starting at `AA-439`. Then Batches 4-6 the same way.~~ **DONE — all six batches closed 2026-07-29.** Watch for the Axiom-4 (Dual-Correction) pattern flagged in `21-drift-report.md` §4 — three independent stacks found "forward operator built, conjugate not" in Batch 1; check whether it recurs in later batches.

## ALL SIX BATCHES CLOSED — 2026-07-29

314/314 ADRs audited. Batches 1–2 as originally produced (spot-verified and retained); Batches 3–6 redone after the external pass over them was retracted for unreliability.

- **Findings:** `AA-1`–`AA-330` (Batches 1–2, 329 findings) + `AA-439`–`AA-540` (Batches 3–6 redo, 102 findings: **11 🔴 · 39 🟡 · 6 🔵 · 46 🟢**). `AA-331`–`AA-438` **void** (retracted pass). `AA-40` a documented gap. Next free ID: **`AA-541`**.
- **Read the result here:** `50-cross-batch-synthesis.md` — four corpus-wide governance patterns and the ordered remediation program. Then `40-triage-queue.md`.
- **Act on this first, no ruling required:** `AA-515` — `.github/workflows/ratify-proposal.yml` ratifies teaching proposals and pushes to `main` against three explicit ADR-0155 prohibitions, with a shell-injection surface and no actor check.
- **Coverage is mechanically verified:** every one of the 314 census entries is named in non-retracted audit output.

**Maintenance contract** (inherited from `docs/assessment/`): every dossier stamps `verified_at cbfc8ccb`. A card whose SHA falls behind a load-bearing arc is testimony, not evidence — re-verify before citing it in a later arc.
