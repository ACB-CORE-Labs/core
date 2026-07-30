# Batch 5 — Tier A Misc Pair (0237, 0238) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
Two governance-sensitive singles pulled from the Batch 5 remainder: the Draft ABI and the GoldTether-autonomy proposal (whose physics underpins the live `goldtether_residual` token verified in ADR-0254's hedge allowlist). Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Per-ADR (terse)

- **0237** (GeometricDelta ABI, **Status: Draft**) — build **substantially landed despite Draft status**: `core/abi/geometric_delta.py` + `core/abi/geometric_delta_validator.py` exist. No dedicated `tests/test_*geometric_delta*` file found (validator may be covered elsewhere — not traced further at this rigor tier). Continuity hazard: its Related list cites `ADR-0025-hard-closure-and-master-substrate.md (Sopher)` — a **foreign repository's ADR-0025** that does not exist in this corpus (our 0025 is rotor-frame admissibility, cited on the adjacent line as "(CORE)") — bare cross-repo number reuse inside a citation list is a citation-graph trap for any tooling that resolves ADR references by number. `AA-500`, `AA-501`.
- **0238** (GoldTether-Modulated Supervised Autonomy, **Status: Proposed**, acceptance path "tests green + Josh review") — build **full**: `core/physics/goldtether.py` carries `GoldPromotionProof`, `OperatingMode`, `AutonomyBand`, synchronous `GoldTetherViolationError` on drift; **three** dedicated test files exist (`test_adr_0238_goldtether{,_alpha,_bootstrap_prune}.py`). The acceptance path's first condition (tests) appears satisfied; the record was never advanced — either the review half never happened or it happened unrecorded. Distinct from ADR-0199's Arena GoldTether per its own Related note (verified: `core/learning_arena/` is a separate consumer). `AA-502`.

## Findings rollup

- **`AA-500` 🟡** — ADR-0237 is `Draft` with a landed ABI (`core/abi/geometric_delta*.py`); same built-ahead-of-record class as `AA-502` but with no dedicated test file found.
- **`AA-501` 🟢** — ADR-0237 cites a foreign repo's `ADR-0025-hard-closure-...(Sopher)` alongside this repo's `ADR-0025-...(CORE)` — cross-repository number collision inside one citation list; recommend a `sopher:` prefix convention or full-path citation for external ADRs.
- **`AA-502` 🟡** — ADR-0238 is `Proposed` with a fully-built, three-test-file implementation; its own acceptance path is half-satisfied and the record never moved. (Batch 1-2 found ~20 stale-status ADRs; this and `AA-500` extend that corpus-wide pattern into Batch 5.)

**Severity tally: 0 🔴 / 2 🟡 / 0 🔵 / 1 🟢.**
