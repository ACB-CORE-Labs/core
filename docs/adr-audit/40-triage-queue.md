# Phase 5 — Triage Queue (Batch 1: ADR-0001–0050)

Ranked by blast radius × severity × Whitepaper/Yellowpaper divergence, per `00-scope-and-method.md`. This queue **recommends; it does not rule.** Per the charter's "settled rulings are constraints, not subjects" clause, every item below is a flag for the same ratification process `docs/assessment/` used, not an executed fix. **Verified against:** `main` @ `cbfc8ccb`.

## 🔴 Block (13 findings — full text, ranked)

**Rank 1 — the FA-1 cascade root cause, corroborated from two independent directions.**
- `AA-1` — `VocabManifold.nearest()` is a near-constant function of its query on the production mount (300/300 collisions to one word); 350/353 stored surfaces fail identity recall. Falsifies ADR-0003's relational-lookup claim and ADR-0001's "trust is absolute" consequence.
- `AA-2` — the vocabulary stores unit versors, never null CGA points, contradicting ADR-0001, and Whitepaper Invariants II and III simultaneously; the code that supposedly guarantees a valid CGA point would *reject* one if it ever arrived.
- `AA-41` — ADR-0005's eight-gate activation sequence is one boolean, true on all four logos packs.
- `AA-42` — `_blend_feature_versors` still returns the target verbatim, discarding 37 coordinates on the live trilingual mount (ratified as `G-25`).
- `AA-51` — `holonomy_encode`'s reverse-walk closure was deleted at commit `fca6216e`; the docstring describing it was not.
- `AA-52` — the retired Crown Proof claim is still asserted verbatim in a live docstring at HEAD (`packs/schema.py:181`).
- `AA-59` — `AlignmentEdge` carries no `epistemic_status` field, so FA-1's verdict has no typed runtime surface to attach to — the correction, once ruled, has nowhere to land without new schema work.
- `AA-74` — cross-language binding via shared `semantic_domains` atoms **is** the dominant collapse site (34 of 37 lost coordinates); the ADR-prescribed remedy is unreachable by construction.
**Why rank 1:** these eight findings are one causal chain, discovered independently by two separate audit stacks (A1 from the algebra side, A3 from the semantic-ground side) and by FA-1 itself (from a third, purely empirical angle) — three independent methods converging on the same defect is the strongest evidentiary posture any finding in this batch has. Fixing the underlying cause (Cluster 2 in `22-consolidation-report.md`: route L2 through the L0 rotor/geometric-product operators instead of a bespoke reimplementation) plausibly resolves `AA-1, 2, 41, 42, 51, 52, 74` together, not one at a time.

**Rank 2 — safety-relevant silent failures, each independently severe.**
- `AA-107` — requesting an unratified domain ethics pack (`legal_ethics_v1`, `research_ethics_v1`, `engineering_ethics_v1` — all three shipped, all three unratified) silently substitutes the zero-refusal default pack, with no log, warning, telemetry, or verdict field. Verified by executed probe.
- `AA-102` — the honest-refusal doctrine (ADR-0022 §2: "silent relaxation is the exact failure mode this ADR exists to eliminate") is violated by the code path that runs by default and honored only by the code path that never executes, eight lines apart in the same function.
**Why rank 2, not rank 1:** narrower blast radius than the semantic-ground chain (each is one mechanism, not a cascade), but directly safety/trust-relevant and independently actionable — either could be fixed today without waiting on a broader L2 ruling.

**Rank 3 — downstream/ratification consequences of the semantic-ground defect, requiring their own re-verdict.**
- `AA-64` — ADR-0180 asserts Holonomy Resonance as "the supreme architectural invariant of `core`" in cross-modal form; the CRDT sharding design is justified as its mechanical cost.
- `AA-68` — ADR-0240's Biography Holonomy Blade "reconstructible via `holonomy_encode`" rests on the deleted closure; `biography.py:94` steers an inert `alpha`.
- `AA-75` — a live `reasoning-capable` ledger license (ADR-0102/0103) rests on four packs whose alignment is destructive on one half and zero-resolving on the other; `G-25` independently records zero curriculum bands produced.
**Why rank 3:** these depend on Rank 1's finding being true (they inherit the semantic-ground defect) rather than being independently discovered — fix priority follows from Rank 1's resolution, but each needs its *own* re-verdict once that lands, since "the premise was wrong" doesn't automatically tell you what each dependent ADR's correct disposition becomes.

## 🟡 Repair (68 findings — grouped, full text in `20-finding-register.md`)

| Theme | Count | Representative IDs | Stacks |
|---|---|---|---|
| Doc/ADR claims stale against running code (field tables, thresholds, status markers, citations) | ~18 | `AA-3`, `AA-4`, `AA-32`, `AA-88`, `AA-148` | A1, A2, A4, B3, B5 |
| Mechanism built, but structurally unreachable on the serving path (flags off, no producer, no CLI surface) | ~16 | `AA-86`, `AA-91`, `AA-93`, `AA-108`, `AA-118`, `AA-142` (partial) | A4, A5, B2, B4 |
| Enforcement/test coverage off the actual pre-push gate while the mechanism it guards is fully built | ~6 | `AA-109`, `AA-149` | A5, B5 |
| Named artifact fully absent (not degraded — entirely unbuilt) | ~5 | `AA-8` (partial-absence), `AA-124`/`AA-125` (ADR-0014 `train/`), `AA-16`/`AA-17` (valence consumers) | A2, B2 |
| Safety/ethics predicate reports "enforceable" while structurally unable to fail | 3 | `AA-104`, `AA-105`, `AA-106` | A5 |
| Everything else (misc. per-ADR repairs — see register) | ~20 | — | all stacks |

**Recommended sequencing:** the "reports enforceable but can't fail" cluster (`AA-104`–`AA-106`) should move with Rank-2's `AA-107` above — same stack, same failure shape (a boundary that reports itself healthy while doing nothing), and cheap to fix once someone is already in that code. The gate-coverage cluster (`AA-109`, `AA-149`) is a single mechanical PR (move N test files from `full_only_baseline.txt` into `smoke`) with no design risk — good first PR out of this audit regardless of what else gets ruled.

## 🔵 Consolidate (25 findings — full clusters in `22-consolidation-report.md`)

Six clusters, ranked by blast radius in the consolidation report itself:
1. Rotor-operator bypass (5 findings, `AA-5/6/14/15` + one more) — true redundancy, low risk, existing tested replacement.
2. **The semantic-ground/algebra duplication (`AA-84`)** — true redundancy, largest blast radius, same root cause as Rank-1 Block items above; resolving this cluster and Rank-1's Block items is effectively one piece of work.
3. SafetyCheck/EthicsCheck + pack-loader duplication (`AA-110`, `AA-111`) — true redundancy, ~2,600 lines of near-duplicate loader logic, moderate effort.
4. Admissibility/attention/identity triad (`AA-89/90/94/99/102`) — unresolved, feeds the existing open `CR-1` ruling rather than standing alone.
5. Hedge-injection duplication (`AA-142`) — unresolved, self-acknowledged by the code itself.
6. Two confirmed non-redundancies (`AA-157` and the B3 Rust-dispatch pattern) — no action; recorded so the pattern-matching above doesn't get applied where it doesn't belong.

## 🟢 Monitor (52 findings — full text in `20-finding-register.md`)

No individual item here rises to ranking; as a set, three sub-patterns are worth a single combined note rather than 52 separate lines:
- **Instrument gaps in adjacent tooling** (not ADR defects): `docs/census/`'s `param-no-effect` sweep missed `AA-5`'s exact target class (`AA-12`); `docs/audit/substrate-liveness-registry.md` is stale in 3 of 3 spot-checked rows (`AA-10`).
- **The existing `docs/assessment/` governing taxonomy has two of its own stale claims** (`AA-19`, `AA-20`) — already corrected by its own later registers, but the source document itself was never amended. Flagged for whoever owns that directory next, not for this audit to fix.
- **Recurring "two documents both claim X, reality is not-X" pairs** (the `H-8` pattern, per `AA-114` and `21-drift-report.md` §2) — low individual severity, but the third occurrence across three different governing documents in one batch suggests a house-wide documentation-maintenance gap worth its own small remediation pass once Batches 2–6 confirm the pattern continues.

## What's *not* in this queue

Three ADRs (0043, 0044, 0045) were Tier C triage only — existence-verified, not executed, not scored on design/axiom fidelity. If a future batch's synthesis needs their full 7-axis picture, promote them to Tier B first.

## Batch 2 & Batch 3 Triage Addendum

### Batch 2 (19 🔴 Block, 71 🟡 Repair, 22 🔵 Consolidate, 59 🟢 Monitor)
- **Top 🔴 Block Findings:**
  - `AA-250` — Sealed `fabrication_control` holdout leaked in plaintext in `results/v1_holdout.json`.
  - `AA-293` — ADR-0087 rhetorical-style substrate has zero consumers in runtime code.
  - `AA-233` — `reasoning_capable` predicate consults no eval result.
  - `AA-219` — ADR-0093 promotion path invariant unimplemented.
  - `AA-308` — Reviewer registry not wired into proposal review pipeline.
  - `AA-310` — Replay-equivalence pre-gate is no-op (`NoOpReplayChecker` always passes).
  - `AA-231` — `inference_closure` lane fails all 3 splits at HEAD against ≥0.95 bar.
  - `AA-232` — Capability reporting reads newest stored file; unsaved failing runs cannot demote ratified rows.
  - `AA-234` — Positive coverage lanes measure grammatical output, not domain content.
  - `AA-248` — Contract returns identical fingerprint on two vocabulary-disjoint domains.

### Batch 3 (0 🔴 Block, 12 🟡 Repair, 1 🔵 Consolidate, 8 🟢 Monitor)
- **Top 🟡 Repair & 🔵 Consolidate Findings:**
  - `AA-345` (🟡 Repair) — ADR-0101 systems_software ratification inherits retired holonomy premise (`AA-75`).
  - `AA-332` (🟡 Repair) — Hebrew-Greek ratification (ADR-0102) inherits retired holonomy premise (`AA-75`).
  - `AA-348`–`AA-351` (🟡 Repair) — ADR-0138, ADR-0139, ADR-0140~2, ADR-0141 versor arithmetic & translation spikes remain unbuilt draft designs.
  - `AA-334` (🟡 Repair) — Python module identifiers (`expert_demo.py`) un-renamed vs user-facing `audit-passed` (ADR-0113).
  - `AA-336`, `AA-338`, `AA-340` (🟡 Repair) — ADR headers remain `Status: Proposed` in document bodies while underlying code/gates are fully built and tested.
  - `AA-342` (🔵 Consolidate) — ADR-0136 regex sentence-template patterns explicitly superseded by ADR-0164 incremental comprehension reader while preserving empirical seed taxonomies.
  - `AA-346`, `AA-347` (🟢 Monitor) — Step 0b `DerivedRecognizer` execution and graph attachment wired in `pipeline.py` but gated behind default-off flag `recognition_grounded_graph`.

### Batch 4 (1 🔴 Block, 2 🟡 Repair, 2 🔵 Consolidate, 21 🟢 Monitor)
- **Top 🔴 Block & 🟡 Repair Findings:**
  - `AA-361` (🔴 Block) — ADR-0180 Delta-CRDT sharded substrate rests premise on retired Holonomy Resonance claim (`AA-64`, FA-1 cascade carry-forward).
  - `AA-362` (🟡 Repair) — Audio & Vision compilers (ADR-0181, 0197) inherit retired holonomy premise (`AA-66`, `AA-67`).
  - `AA-373` (🟡 Repair) — Motor Efferent Decoder Spike (ADR-0198) implemented fail-closed efferent gate while physical motor decoding remains deferred to ADR-0216.
  - `AA-363` (🔵 Consolidate) — ADR-0183 stub path for lawful audio-to-lexeme resolution consolidated directly into Audio compiler.
  - `AA-366` (🔵 Consolidate) — Candidate-graph completeness guard (`ADR-0191`) consolidates wrong=0 leg across candidate extractors.

### Batch 5 (1 🔴 Block, 0 🟡 Repair, 0 🔵 Consolidate, 45 🟢 Monitor)
- **Top 🔴 Block Finding:**
  - `AA-395` (🔴 Block) — Biography Holonomy Blade (ADR-0240) rests on deleted `holonomy_encode` closure (`AA-68`, FA-1 cascade carry-forward).

### Batch 6 (0 🔴 Block, 1 🟡 Repair, 1 🔵 Consolidate, 13 🟢 Monitor)
- **Top 🟡 Repair & 🔵 Consolidate Findings:**
  - `AA-429` (🟡 Repair) — Existential witness band v6-EX (`ADR-0261`) reserved slot requires explicit NO-GO annotation until witness resolution is built.
  - `AA-437` (🔵 Consolidate) — Grounded-open hedge arm (`ADR-0254`) consolidates shadow coherence gate hedging with ADR-0038/0054/0080/0174.





---

# Batches 3–6 additions (redo, `AA-439`–`AA-540`)

Appended 2026-07-29 after the Batch 3–6 redo. Batch 1's ranking above stands; these are the new entries. Corpus-level reasoning and the ordered remediation program: `50-cross-batch-synthesis.md` §4.

## 🔴 Block — new (11 findings; ranked)

**Rank 0 — act without a ruling.** `AA-515` — `.github/workflows/ratify-proposal.yml` ratifies teaching proposals (`--accept`) and `git push origin main` under `contents: write`, against ADR-0155's three explicit prohibitions; the operator note is interpolated unquoted into that shell, and the only guard is a repo variable (no actor check; ADR-0161's allow-list unbuilt). Verified line-by-line. Mitigated by this repo being Forgejo-primary with GitHub Actions dormant — likelihood, not defect. **One file; delete or neuter it.**

**Rank 1 — the unratified-authority pair (one ruling covers both).** `AA-491` (ADR-0175 `Proposed` supplies the invariants Accepted ADR-0256 cites by number and the θ_SERVE=0.99 ceiling licensing all 25 deduction bands) and `AA-504` (ADR-0201 `Proposed` is the `proof_chain` keystone that Accepted ADR-0201.1 hardens and Accepted 0202–0205 build four phases on). Joined by `AA-516` (0168/0168.1/0169/0169.1 `Proposed` yet sole authority for a live `packs/data/` mutation boundary) and `AA-517` (0199 `Proposed` while serving 4 eval lanes and named canonical by Accepted 0238). Zero runtime risk; pure record reconciliation; unblocks trusting the whole deduction arc.

**Rank 2 — the sealed-holdout tangle.** Batch 3 Tier A's 🔴 on `reasoning_capable` requiring a plaintext holdout ADR-0105 orders resealed, plus `AA-250` (holdout leaked verbatim in a git-tracked results file). Sequence matters: re-point the gate at the sealed artifact **before** resealing, or compliance demotes every domain. Repo-wide: 3 `.age` vs 32 plaintext.

**Rank 3 — the holonomy conjugate.** `AA-494` — `holonomy_encode` computes no reverse walk while its docstring and ADR-0240's central mechanism specify `H = F·R`; `alpha` validated-then-unused; `biography.py:94` asserts closure on a quantity closed by construction. **ADR-0240 must not be accepted as written.** Re-derived at HEAD.

**Rank 4 — remaining Batch 3 🔴s** (4 more, in `Batch3-TierA-redo.md`): the `audit-passed` gate never consulting its 9 predicates, Obligation-#1's substrate claim false repo-wide, and the ADR-0102/0103 license resting on unevaluated ground (`AA-75` confirmed, not downgraded).

## 🟡 Repair — new (39)

Dominated by two groups: **Status-vs-reality mismatches** (25 of Batch 4's 44 alone) and **cascade-annotation debt** (`AA-485`, `AA-493` — no cascade member in any batch carries a post-retirement note). Both are documentation-only fixes with no runtime risk. Individually listed in `20-finding-register.md`.

## 🔵 Consolidate — new (6)

Notably `AA-513` (ADR-0254 adds hedge site #3 *with* an explicit deferral — extends Cluster 5) and Batch 3's confirmation that ADR-0136's regex templates were cleanly superseded by ADR-0164. ADR-0263's ratified-ledger bridge is recorded as a **completed** consolidation — the positive template for the rest.

## 🟢 Monitor — new (46)

Includes ten positive exemplars worth citing when drafting remediation guidance: ADR-0252 (in-place ruled corrections), ADR-0244 (empirically-proven-vacuous gate retired in place), ADR-0164/0174 (scoped supersession banners), ADR-0165 (prohibition propagated into other authors' practice), ADR-0263 (completed consolidation), ADR-0228–0236 (honestly-parked unbuilt backlog), plus Batch 4's four (0170's self-reconciled status, 0185's banner, 0198's split, the GoldTether disambiguation).
