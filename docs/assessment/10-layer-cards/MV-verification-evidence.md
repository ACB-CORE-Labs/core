# MV — Verification & Evidence (cross-cutting)

**Kind:** layer (cross-cut) · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Re-verified:** `39331dbc` (2026-07-28) — see the arc note below.
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `partial-wiring-debt` · **Fitness:** `strained` · **Topology role:** benchmark/eval artifact + tooling surface

> How CORE knows what it knows about itself. MV is cross-cutting because replay is a *property* of every layer and an *apparatus* of this one. Its philosophical charge follows directly from the thesis: a decoding system's failures are locatable, so the machinery that locates them is not overhead — it is the difference between a structured failure that can be fixed and a stochastic one that can only be regularized. MV is also the layer this assessment most depends on, and therefore the one whose gaps most threaten the assessment's own conclusions.

**Telos stages:** replay deterministically (primary); learn (evidence for calibration)
**Macro role:** Produces the evidence that every other layer's claims are measured against, and fails loudly when a claim drifts.


**Arc note — 2026-07-28 (`39331dbc`).** PR-4 (curated-suite membership ratchet + the gate-guarding pin promoted onto the gate), PR-6 (three doctrine prohibitions pinned), G-7 and G-9 CLOSED. The layer's central finding is sharper than the card states: the recurring defect is not absent pins but **pins that exist and do not run** — four instances found this arc (the H-13 lifecycle pin, the smoke/CI parity pin, the safety-pack fail-closed contract, the ANN import ban), each indistinguishable from coverage in any document.

---

## What it is / What it does

`evals/` (375 modules) holds the lane runners and their contracts. `tests/` (881 modules) holds the pins. `core/cli_test.py` defines **21 suites** as hand-curated tuples — `fast, smoke, runtime, cognition, teaching, packs, algebra, sensorium, pulse, formation, proof, refusal, margin, rotor, inner-loop, phase5, phase6, adr-0024, math, deductive, full`. `CLAIMS.md` is machine-generated from in-tree state: Tier 1 = five ratified domains from `core.capability.ledger_report`; Tier 2 = eleven lanes pinned by report SHA-256, where mismatch is a CI failure. `workbench/` (22 modules) is the read-only operator/auditor projection. `scripts/verify_lane_shas.py` is the Tier-2 verifier.

The validation doctrine is **local-first**: the in-worktree run is the merge bar (`uv run core test --suite smoke -q` pre-push, larger suites pre-merge, `[Verification]:` on the PR). A pre-push hook runs smoke **plus** the `warmed_session` consistency lane pin, deliberately targeted at a regression class smoke does not cover. `scripts/ci/local-ci.sh` reads suite membership *from the CLI* rather than restating it, so the runner cannot drift from the hook. The interpreter contract is fail-closed: `requires-python == "3.12.13"` exactly, and a degraded run stamps itself **NON-CANONICAL** on every line — a degraded run is legitimate, a degraded run reporting itself as the real thing is not.

---

## Contract

- **Inputs:** every other layer's runtime behavior; lane runners; pinned SHAs.
- **Outputs:** lane reports (JSON), `CLAIMS.md` rows, `trace_hash`, `CognitivePipelineRecord`, telemetry events, capability ledger, `[Verification]:` evidence.
- **Invariants:**
  - Tier-2 lane report SHA-256 must reproduce byte-for-byte; drift is a CI failure and demotes the claim.
  - Replay treats `pipeline_record` as **critical evidence** — divergence is evidence against equivalence, not wall-clock noise.
  - Pre-widening journal rows must show `missing_evidence`, never a synthesized green pipeline.
  - `derive_evidence_digest` is deterministic in field order; re-running against on-disk lane results reproduces `claim_digest`.
  - Unknown lane ids **fail closed** (`lane <id> has no registered shape — introduce via ADR amendment`); a broken `reviewers.yaml` yields an empty registry rather than silently granting `audit_passed=true`.

---

## Design vs build

- **Design:** ADR-0092/0093/0096/0098/0099 (registry, contract validation, fabrication control, demo composition, public demo), ADR-0106/0109 (expert-demo promotion, lane-shape registry), ADR-0119.x (GSM8K lane + seal discipline), ADR-0167 (audit-as-evidence), `docs/testing-lanes.md`, `docs/eval_methodology.md`, `AGENTS.md` §Local-First CI Validation Protocol.
- **Build:** `partial-wiring-debt`.
- **Evidence:**
  - Eleven Tier-2 lanes carry pinned SHAs verified by CI — `CLAIMS.md` + `.github/workflows/lane-shas.yml` — would-fail-if-absent: **yes**.
  - Suite membership is read from the CLI by the local runner, so hook and runner cannot diverge — code-read — `scripts/ci/local-ci.sh` — would-fail-if-absent: **yes**.
  - Fabrication-control lane enforces per-class `refused == n, fabricated == 0` — lane shape — `core/capability/expert_demo.py` — would-fail-if-absent: **yes**.
  - Sealed holdout discipline: 1,319 GSM8K cases age-encrypted, plaintext never on disk, no CI workflow sets `CORE_HOLDOUT_KEY`, team operates blind — code-read + contract.
  - **Suite coverage is incomplete in a load-bearing way** — measurement — no `l10`/`always_on` test appears in any of the 21 suite tuples (see M6).

---

## Capacity

- **Designed:** every claim mechanically derived from in-tree state and verified by CI.
- **Measured:** 21 suites; 881 test modules; 11 SHA-pinned lanes; 5 Tier-1 domains; `deductive` suite at 20 files, `smoke` at 23, `sensorium` at 21, `algebra` at 15. The full ~12k fast-lane runs async by design so the pre-push hook stays targeted rather than gridlocking the push cycle.
- **Ceilings:** the smoke gate is not the full suite — a PR's own tests must be run against the rebased base pre-merge, which is process discipline rather than mechanism. Remote Actions are secondary observability only; GitHub mirror Actions are billing-locked dead signals. Roughly 31 red tests were retired historically. The sealed GSM8K holdout has never been opened against a parser with sufficient coverage.

---

## Dependencies & provenance

**witnesses** → every layer; **reads** → M5 (capability ledger, reviewer registry), M4 (telemetry, trace); **constrains** → M0 (bit-exact parity pins).

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| replay deterministically | **covered** | Tier-2 SHA pinning is mechanical and fails CI on drift; pipeline record is critical replay evidence |
| *(evidence for learning)* | **covered** | Sealed practice ledgers, capability ledger, lane-shape registry all fail closed on unknown shapes |
| *(coverage of the telos-critical layer)* | **uncovered** | No suite runs any L10/always-on pin |

**Zone roster:** `evals-determinism`, `tooling-cli-workbench-rs`; `capability` ✱ (owned by M5, cross-referenced here).

**Rollup note:** weakest-link rollup. MV's *mechanisms* for the things it covers are excellent; its *coverage map* has a hole at precisely the layer with the least other protection.

---

## Judgment

**Fitness: `strained`.** MV's design instincts are consistently right — machine-generated claims, fail-closed registries, SHA pinning, a non-canonical stamp for degraded runs, suite membership read rather than restated. These are the habits of a system that expects to be wrong and wants to find out. The strain is structural rather than qualitative: **suite membership is hand-curated**, so coverage is a curation artifact, and nothing detects the *absence* of a pin from every suite. That is how the most telos-critical layer in CORE came to be enforced by nothing while its tests exist and pass on demand.

**Honest wrinkles:**
- **The hole is where it hurts most.** M6 has a complete falsifiable soak harness with holds/bites predicate pairs — genuinely excellent test design — that no suite runs. The tests are not weak; they are *unscheduled*. A hand-curated suite list has no mechanism to notice.
- **There is no meta-pin for coverage.** The project has learned "a pin in no suite never runs" as doctrine, but nothing mechanically enforces it. A test file that belongs to zero suites is currently indistinguishable from a test file that runs everywhere. This is, in this assessor's reading, MV's single highest-leverage improvement and a strong Phase 4 Third-Door candidate: rather than curating harder, make orphaned pins detectable.
- The gap registers this layer ought to feed are dead (Phase 0 Finding 0-D): `docs/gaps.md` is 26/26 closed, the liveness ratchet is L10-blocked and stale, and `docs/analysis/` is a chronological archive of ~130 documents with no aggregator. MV produces excellent point-in-time evidence and has no standing instrument that accumulates it.
- Long-horizon evidence has no home. The soak harness's `__main__` exists; no results artifact does. Lanes are pinned by SHA precisely because point-in-time reports drift — but a lane nobody runs produces no report to pin.
- MV's honesty machinery (`missing_evidence`, NON-CANONICAL stamping, fail-closed unknown lanes) is a genuine model for the rest of the system and should be cited as such in Phase 5 rather than only audited.

**Open questions:**
- Add a meta-pin asserting every `tests/*.py` belongs to ≥1 suite (or an explicit exclusion list)? (→ Phase 4; likely highest-leverage single change in MV)
- Which suite should own the L10/always-on pins, given they are soaks? (→ Phase 4 / ruling)
- Should the assessment's gap register become the standing instrument MV lacks? (→ Phase 4)
