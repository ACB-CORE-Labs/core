# Batch 4 — Tier A Carry-Forward Stack (0180, 0181, 0196, 0197) — REDO

**Verified against:** `main` @ `cbfc8ccb` | **Auditor:** Claude (main session, direct) | **Date:** 2026-07-29
The four pre-flagged Batch-4 carry-forwards (`MANIFEST.md` table): three FA-1-cascade members (`AA-64`, `AA-66`, `AA-67`) + the Rust-dispatch generalization check (`AA-138`). Rest of Batch 4 scoped separately. Findings: renumbered into the corpus sequence (see `20-finding-register.md`).

## Per-ADR (terse)

- **0180** (Delta-CRDT Sharded Substrate) — Accepted 2026-05-31. Build full: `vault/crdt.py`, `core-rs/src/vault.rs` exist; G1 contract locked per ADR-0196. **Cascade posture, refined from `AA-64`:** the holonomy dependency is the *framing premise* (§1:15-18 — "supreme architectural invariant... Holonomy Resonance") that justified the design's mechanical cost, not a functional dependency — the shard/merge mechanics compute no holonomy and stand on ordinary concurrency merits. Recommendation for the re-verdict pass: an amendment note re-grounding §1's justification, not a mechanism change. This *downgrades the actionable severity* of `AA-64` from structural-🔴 to framing-🟡 — with the fresh evidence stated here, per the register's rule that severity changes require new evidence (`AA-484`).
- **0181** (Audio Compiler) — Accepted, ratified 2026-06-03. Build full: all 5 claimed test files + `sensorium/audio/` + `packs/audio/` exist. Cascade exposure is inherited-framing-only (depends on 0180's premise narrative; its compiler computes no holonomy). Continuity: no FA-1 note (0 mentions) — annotation-level exposure. `AA-485`.
- **0197** (Vision Compiler) — Accepted, ratified 2026-06-03. Build full: all 4 claimed test files + `sensorium/vision/` + `packs/vision/` exist. Same posture as 0181; also names ADR-0013's framing as a dependency (per `AA-67`), which B1's card already found understates what's built. `AA-485`.
- **0196** (Native Substrate Language Doctrine) — Accepted 2026-05-31. The doctrine itself (no wholesale Zig rewrite; G0–G8 adoption-gate ladder; G1 first instantiated by 0180) is sound and cheap to hold — 0 Zig files exist, consistent with gates unexercised. **`AA-138`'s question answered: the generalization did NOT inherit the dispatch pattern's caveats** — line 19 cites `CORE_BACKEND=rust` as "already parity-gated and opt-in," the exact claim B3 measured as bypassed (69 direct-import call sites skip the dispatch) with exception-swallowing making lane-hash parity unfalsifiable (`AA-136`/`AA-137`). The doctrine's exemplar is a mechanism whose guarantee doesn't currently bind. `AA-486`.

## Findings rollup

- **`AA-484` 🟡** — `AA-64` refined with primary evidence: ADR-0180's holonomy dependency is framing-premise-only (§1:15-18); the CRDT mechanics are holonomy-free. Re-verdict action: amendment note re-grounding the justification. (Supersedes `AA-64`'s 🔴 rating for triage purposes; the drift-report row should be updated at rollup.)
- **`AA-485` 🟡** — 0180/0181/0197 carry zero FA-1 annotations; with `AA-493` (Batch 5) this makes the cascade-annotation debt corpus-wide: **no** cascade member in any batch has been annotated post-retirement.
- **`AA-486` 🟡** — ADR-0196's doctrine cites the Rust dispatch pattern as its parity exemplar without the measured caveats (`AA-136`/`AA-137`); before any Zig gate clears G3 ("parity proof") the parity mechanism itself needs the fail-loud repair B3 recommended (`AA-139`'s harden-before-reuse).

**Severity tally: 0 🔴 / 3 🟡 / 0 🔵 / 0 🟢.**
