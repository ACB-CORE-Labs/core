# ADR-0241 / ADR-0242 — D10 Acceptance Packet for Joshua

**Date:** 2026-07-15 · **Prepared by:** Claude session (orchestration + adversarial verification) — **prepare-only; nothing here self-Accepts.**
**State under review:** `main @ 54228d45` (PR #36–#40 merged) + PR #41 pending (chiral sign-gate).
**Companion documents:**
- `docs/audit/adr_0241_cohesion_acceptance_checklist.md` — the P12 checklist itself
- `docs/research/third-door-blueprint-fidelity.md` §12 — behavioral acceptance table (every 🟢 row names a failable pin)
- `docs/research/adr-0241-0242-adversarial-and-fidelity-findings.md` — hostile independent verification (W1)
- `docs/research/adr-0241-0242-blueprint-integration-plan.md` — all 4 authority blueprints dispositioned clause-by-clause
- `docs/plans/adr-0241-0242-session-completion-summary-2026-07-15.md` — living status surface (Plan A/B archived beside it)

---

## 1. Evidence summary (what is proven, and how)

| Claim | Evidence |
|---|---|
| Wave substrate behaves per ADR-0241 §2 | Dedicated suites green (wave_manifold / cohesion I-01…I-05 / Trace A/B); independently re-run this session |
| Chiral charge non-vacuous + conserved (P8) | **Executed adversarially**: Q = −2.5 on the mixed-parity fixture (grade-1 ⊕ grade-4), transport drift 0.0e+00 exactly, even-versor Q = 0 (no #19 revival) |
| Fibonacci cert discipline (ADR-0242 V1) | **Executed adversarially**: live func-call counter == cert.evaluations == budget across 8/15/20/21; dual-run digest byte-stable |
| P9 seal discipline | `seal_mode` SPECULATIVE-by-construction; contemplation seam defensively re-checks; COHERENT requires `seal_mode_reviewed(authorized=True)` |
| Serve containment (A-04) | W1 found a **live transitive breach** (5 off-serving modules loaded via the `core/physics` barrel) → **fixed in #40** (lazy Tier-2 exports + process-level `sys.modules` guard test) |
| Deterministic lanes | lane-shas 9/9 pinned SHAs + CLAIMS.md current — local at the exact merged tip AND server-side (runs #184/#185 green) |
| PR gates | smoke 175 (×3 runs), affected-file lane 179, goldtether-consumer regression 99 — all green |

## 2. Deviations submitted for ruling

1. **P7 true Clifford polar — demoted with ill-posedness proof.** Plan A's written bar was "landed, not demoted." The implementation *proves* `~C C` is non-scalar for multigrade fields (`test_true_clifford_polar_fails_on_multigrade_field`), so the analytic polar `R = C(~C C)^{-1/2}` is ill-posed there; sandwich conjugacy (SVD + Spin-GN) is the honest authority. **Recommend: accept-as-honest** per the #19 RETIRE precedent. Note the implementation is *more* faithful to the algebra than the blueprint's own §4 prototype (which used Euclidean `np.outer`/SVD proxies).
2. **Serve-boundary reconciliation (T1/T2) — ruled by Shay 2026-07-15, submitted for ratification.** `wave_manifold` is Tier-1 sanctioned serve substrate (goldtether/surprise/biography delegate to it; the subsumption map and the A-04 ban list could not both be true). Tier-2 (holographic_vault, fibonacci_search, wave_energy_boundary, multi_scale_energy, wave_seam, sensorium_wave_feed, atlas_packing) stays off-serving, now enforced **process-level** (transitive guard), not just direct-AST.
3. **Sensorium feed** — staged packets + real ρ algebra; real compilers remain open (W5).
4. **Continuous-field integrals** — progressive (mode samples), research track.
5. **Holographic recall precision** — float32-honest (I-02 tol 1e-6), not the blueprint's implied bit-exactness; already pinned in-suite.

## 3. R&D-memo claims deliberately filtered (Accept should be informed)

- **Fibonacci anyons** ("immune to float32 drift") — NOT BUILT; ledger row corrected this session from a prose-only 🟢 to ⚪ claim-quarantined (W1 Finding #5).
- **Fibonacci "avoids division" cost claim** — implementation uses the correct ratio subdivision; the no-division micro-claim only holds on integer lattices and was not chased.

## 4. Capability additions since the checklist was written

- **Chiral orientation sign-gate** (`sgn(Q)=const`, ADR-0241 §2.4C / core_ha §5.2 mirror-inversion safeguard) — the audit's one missing enforcement, built TDD, **PR #41 pending**: fail-closed `ChiralOrientationError` on materially re-emerging flips; signed charge wired in `goldtether_residual` with residual values pinned byte-identical; vacuous (inert) on today's even serve fields.

## 5. Known open items (explicitly NOT completion blockers)

1. **ADR-0242 R&D memo** ("deterministic-fibonacci-operators-and-evidence-gated-optimization") has no local export — its blueprint-fidelity slice is partial (implementation verified against its own contract + committed ADR).
2. **CRDT-vs-bit-exact determinism** — core_ha memo claims Delta-CRDT in `core/sync/`; actual mechanism is bit-exact codec + single-writer VaultStore. Needs a decision (build CRDT for multi-writer, or correct the doc).
3. W5 backlog: Rust f64 GP parity (D9), real sensorium compilers, V2 energy promotion (benchmark-gated), progressive continuous field.
4. GitHub Actions mirror CI — billing-locked; validation is local-first + Forgejo Act per the AGENTS.md protocol (merged in #40).

## 6. Requested action

Rule on §2 deviations (recommendations inline) and, if satisfied, flip **ADR-0241 and ADR-0242 → Accepted**. PR #41 (chiral gate) can be folded into the Accept or ruled separately.

---

## 7. Addendum (same day, post-merge) — ADR-0242 memo fidelity slice CLOSED

§5 item 1 is resolved: the "deterministic-fibonacci-operators-and-evidence-gated-optimization" memo was retrieved in full (Drive connector; committed copy now at `docs/research/ADR-0242-deterministic-fibonacci-operators-and-evidence-gated-optimization.md`). Audit against the implementation: **no new defects — the implementation is stronger than the memo's own reference code** on four counts:

| Memo | Implementation | Direction |
|---|---|---|
| Prose demands a "content-addressed, cryptographic" certificate; the memo's own dataclass **omits** the digest field | `cert_id` sha256 present, dual-run byte-stable | impl > spec code |
| Reference unimodality check counts extrema (would **pass a pure local maximum**) | shape check (decrease-to-min-then-increase) fails it | impl > spec code |
| No nonfinite / bounds-violation guards; code non-executable as written (`np.argsort` without numpy import) | fail-closed on nonfinite, bounds, budget, eval error | impl > spec code |
| `minimizer` = bracket midpoint always | best sampled point when inside the final bracket (deviation documented at the code comment) | impl > spec, noise-robust |

Sovereignty invariant (§6 of the memo) verified: Fibonacci operators never touch truth status / safety / identity / promotion (T2 quarantine + proposal-only κ). The five-vector staging matches the memo's phase gating exactly, including anyons (Phase 5 pre-research, not built — consistent with the corrected ledger row).

**Carry items (staged, non-blocking):** (a) §5-P1 "certificate written to execution telemetry" seam not verified; (b) §5-P2 cross-band (F₅–F₇) DiscoveryCandidate persistence gate not built; (c) impl accepts `evaluation_budget ≥ 2` where the memo floor is 3 — kept deliberately (n=2 is mathematically valid and the impl validates harder elsewhere), noted for the ruling.
