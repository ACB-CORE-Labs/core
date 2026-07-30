<!--
TEMPLATE — one file per ADR audited at Tier B or Tier C, or embedded inline (one section per
ADR) inside a Tier A stack dossier. Copy this whole template per ADR. Do not renumber or
reorder the sections — later automated rollups (the alignment matrix, the finding register)
parse this shape.

Delete this comment block in the filled copy. Keep every heading even if the answer is
"none found" / "no evidence" — an omitted section reads as "not checked", not "checked, clean".
-->

# ADR-XXXX[suffix] — <title>

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** — (per `02-stack-taxonomy.md`) | **Tier:** A / B / C
**ADR status (as recorded in the file):** — | **ADR date:** —
**Card author:** — | **`verified_at` SHA:** `——————`

---

## 1. Content summary

- **Decision made:** one or two sentences, in the ADR's own terms.
- **Alternatives explicitly rejected** (if the ADR names any): —
- **Artifacts the ADR claims will exist** (functions, modules, contracts, files, invariants — list every one by name, this is the checklist for §2):
  - —

## 2. Implementation cross-reference

For each claimed artifact from §1, one row. `rg`/grep the exact name; don't infer from the ADR's own prose that something exists.

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| — | yes / partial / no | `path:NN` | — |

**Build axis:** ghost / scaffolded / partial / full — <one line justifying the call, citing the row above that decided it>

## 3. Liveness / integration

- Is this reached on the live serving path, or only in tests/scaffolding/dead code? Trace the actual call chain — don't take a docstring's word for it.
- **Sabotage test:** if this mechanism were removed or stubbed to a no-op, what observable would change? If nothing would change, say so plainly — this is a decoration finding, not a minor caveat.
- **Liveness axis:** dead / scaffolded / wired-but-unreached / live — <justification>

## 4. Design fidelity — pillars and axioms

Score the *decision as written*, independent of whether it was built.

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | — | — |
| II. Semantic Rigor | — | — |
| III. Third Door | — | — |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | — | — |
| 2. Field-State | — | — |
| 3. Propagation-over-Mutation | — | — |
| 4. Dual-Correction | — | — |
| 5. Reconstruction-over-Storage | — | — |
| 6. Compilation-Last | — | — |
| 7. Reality-over-Inheritance | — | — |

(Axioms/pillars with no bearing on this ADR: mark `n/a` rather than leaving blank, so a blank always means "not yet assessed".)

## 5. Build fidelity — does the code match the decision?

Where §2 found `partial` or `full`: does the implementation match what §1 decided, or did it drift? Cite the specific divergence if any.

**Build-fidelity axis:** matches / partial drift / contradicts — <justification>

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Contradicts `Whitepaper.md`? Cite section.
- Contradicts `Yellowpaper.md`? Cite section.
- Contradicts, silently overlaps, or is superseded by another ADR (walk the citation graph from `01-adr-census.md` — `Supersedes`/`Extends`/`Related` fields, plus anything found by reading)? Name it.
- **Continuity axis:** clean / superseded-cleanly / unreconciled contradiction — <justification>

## 7. Necessity / generality

1. **Necessity** (restates §3's sabotage test from the design side): is this a genuinely irreducible primitive, or could the system lose it without losing capability?
2. **Reducibility**: does an operator already present at L0/L1 (algebra/field layer) already do this under a different name? Name it if so.
3. **Extensibility**: could this mechanism, generalized slightly, absorb another ADR's narrower construction — or vice versa? Name the candidate pairing if one comes to mind; full cross-stack pairing happens in `22-consolidation-report.md`.

**Necessity/generality axis:** irreducible / reducible-to-\<X\> / generalization-candidate — <justification>

## 8. Fitness / value

Evidence the decision (where built) delivered something measurable. Check, in order: `docs/assessment/10-layer-cards/` and `20-component-cards/` for this zone, the gap/hindrance registers, `evals/obligation_*/`, `docs/analysis/`, `docs/PROGRESS.md`. Cite the specific artifact, or record "no evidence found" — that is itself a finding, not a gap in the card.

**Fitness axis:** — <cite artifact, or "no evidence found">

## 9. Findings raised

List any `AA-N` findings this card raises (assign the next free number from `20-finding-register.md` at rollup time — leave a placeholder like `AA-?` if drafting before rollup). One line each: severity bucket (🔴/🟡/🔵/🟢) + one-sentence claim + pointer to the section above that supports it.

- —

## 10. Evidence sources actually consulted

List what was checked, not just what was found — per the "verify against code, not documents" discipline, a card that skipped the code and read only prose should say so.

- —
