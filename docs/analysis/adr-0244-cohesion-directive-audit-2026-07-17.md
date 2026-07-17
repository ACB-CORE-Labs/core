# Cohesion Directive Audit — repo state vs. `engineering_cohesion_refactoring_directive.md`

**Date:** 2026-07-17
**Scope:** Code-level verification of the seven mandates in `docs/analysis/engineering_cohesion_refactoring_directive.md` against `main @ 24078b11` (post ADR-0243 Phase 3, which landed *after* the directive was drafted).
**Related:** ADR-0244, ADR-0241, ADR-0242, ADR-0243, `docs/analysis/core_cohesion_master_plan.md`.

---

## Verdict

The directive is directionally sound but was drafted against a **pre-Phase-3 snapshot** and, in places, against **imagined code**. Two mandates (2, 4+5) are accurate and actionable as written. Mandate 1's diagnosis is right but its prescription is already built — the real gap is different (f64, not f32). Mandate 6 is ~85% already implemented; one legibility residual remains. Mandates 3 and 7 describe seams that **do not exist yet** — they are ADR-0244 implementation work, not refactors of drift. Notable: the `default=str` + 24-char-digest drift the directive flags was **replicated into Lane C (`biography_wiring.py`) after the directive was written** — the drift is spreading, raising the priority of the semantic-rigor batch.

---

## Per-mandate findings

| # | Mandate | Verdict | Evidence |
|---|---------|---------|----------|
| 1 | Rust `geometric_product` fast path | **Diagnosis right, prescription stale** | The 32×32 CPython loop exists (`algebra/cl41.py:116`). But no `_rust_cl41` module — `algebra/backend.py:67` **already** implements the exact f32-gated Rust dispatch the directive prescribes (opt-in via `CORE_BACKEND=rust`). The real gap: the hot wave-field substrate runs **f64**; Rust `geometric_product_f64` exists (`core-rs/src/cl41.rs:126`) but is **not exported** in `lib.rs`. The D9 parity suite explicitly pins *against* f32-truncating f64 workloads — the directive's f32-only gate never fires on the actual hot path. |
| 2 | `_cached_eigh` memoization | **Accurate — apply as written** | `relax_to_ground` runs fresh `np.linalg.eigh` per call on dense H (`cognitive_lifecycle.py:546`); `ProblemHamiltonian` is frozen + content-addressed — an ideal memoization key. |
| 3 | f64→f32 serving cast | **Premise false today; prospective** | `identity.py` has **no numpy/f32 path** — pure-Python scalar heuristics; no ψ handoff to `IdentityCheck` exists. The seam this mandate casts across only comes into being with ADR-0244 §2.1–2.2. `cognitive_lifecycle` is also A-04-banned from serve. → fold into the ADR-0244 arc (D4). |
| 4 | Full 256-bit digests; kill `default=str` | **Accurate; 3 live sites + spreading** | `cognitive_lifecycle.py:128–133` (`default=str` + `[:24]`, incl. `_psi_digest`), `self_authorship.py:42–43`, and **`biography_wiring.py:125–126` (Lane C, post-directive)**. `holographic_vault.py:74` is already full-length; `TurnEvent.trace_hash` is already full SHA-256 (the directive's trace-hash claim is stale — already satisfied). CRDT-collision rationale overstates current exposure (multi-writer deferred), but the fix is right and cheap. |
| 5 | Little-endian byte-order contract | **Accurate; zero-risk** | No byte-order coercion at any digest site. `astype('<f8')` is a byte-level no-op on our LE platforms → digests unchanged, contract made explicit. Pure hardening. |
| 6 | "No sampled unimodality violation" | **~85% already built (ADR-0242 V1 + Lane A)** | `fibonacci_search.py` already has the sampled check, typed `OptimizationFailure`, fail-closed nonfinite/bounds, the bracketed-interval contract, and "never a bare float." Lane A's `kappa_calibration.py` is proposal-only and R-04-compliant. Residual: `propose_kappa_from_search` returns baseline κ=1.0 on failure — but κ=1.0 *is* the "parameters unchanged" no-op the directive demands, and the typed failure is already the second tuple element. The fix is legibility + the reason rename, not a behavior change. |
| 7 | Insertion-order-independent allocation | **Premise stale; no live consumer** | `atlas_packing.py` is already ordinal-reconstructible (`ALLOCATOR_VERSION` pinned, "layout regenerates from identity + ordinal k") and has **zero production call sites**. Building `AnchorAllocator` now would be a hollow gate; its consumer arrives with ADR-0244 §2.9. → fold into the ADR-0244 arc (D4). |

---

## Spec-level wrinkles (all surfaced)

1. **ADR-0244 §2.3 `Q_top` — RESOLVED, proven vacuous** — central `I₅` in odd Cl(4,1) ⇒ the charge collapses identically to 0 on every versor state (the #19 pseudoscalar failure mode), confirmed empirically (`evals/adr_0244_qtop_vacuity`). See Q4 below. Retired from egress; ADR-0244 annotated.
2. **ADR-0244 §4 contradicted §2.1–2.2 — RESOLVED at D4 Phase 0** — per-axis resonance vs. Gram-projection/leakage-norm/`ManifoldConditioningError`; the then-dangling "ADR-0245" reference is now a real, committed companion ADR; the bare `assert` byte-order guard is replaced by typed `ValueError` guards (incl. `isfinite`). §2 governs; ADR-0244 §4a is the reconciled specification (see ADR-0244 governance annotation items 2–4, 10 and `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` Phase 0).
3. **Directive §4 says "six criteria" but lists five** — the missing one is the **Mechanical-Sympathy gate** (see below); criteria 1–2 cover Semantic Rigor, 3–4 honesty/falsifiability, 5 Autonomy/Third-Door — **Pillar I had no acceptance criterion**.
4. **Quarantine wording** — "every refactored module must reside strictly inside `evals/`" can't apply to an in-place `algebra/cl41.py` refactor. Adopted reading: *new capabilities* live in `evals/`; in-place core refactors keep the A-04 transitive serve-quarantine + smoke/fast-lane gates until acceptance.
5. **Doc placement** — the directive's canonical path is `docs/analysis/`; it sat untracked at `docs/`. The untracked `docs/research/core_cohesion_master_plan.md` and `docs/research/ADR-0243-…md` are stale raw re-exports (the research master-plan predates the AGENTS.md R-01 doctrine note the tracked `docs/analysis/` copy carries); removed, not committed.
6. **Directive perf numbers** (~40µs/call GP, 50–200µs eigh) are unverified assertions — `benchmarks/apple_uma_mechanical_sympathy.py` measures them as the D2 evidence rather than taking them on faith.

---

## Amended mandate → work-item mapping

| Directive mandate | Where it lands | Amendment |
|-------------------|----------------|-----------|
| M4 + M5 (digests, byte-order) | **D1** semantic rigor | apply as written; +Lane C site |
| M2 (`_cached_eigh`) | **D2** mechanical sympathy | apply as written |
| M1 (Rust GP) | **D2** mechanical sympathy | **f64**, bit-identical parity (not the already-built f32 gate) |
| M6 (unimodality) | **D3** search honesty | legibility + rename; behavior already correct |
| M3 (f64→f32 cast) | **D4** ADR-0244 arc | seam does not exist yet |
| M7 (allocator) | **D4** ADR-0244 arc | no live consumer yet |

---

## The sixth acceptance criterion (Pillar I coverage gap)

Directive §4 lists five gates but claims six. The missing one closes the Mechanical-Sympathy pillar, which otherwise has no acceptance test:

> **6. Mechanical-Sympathy Gain.** An accelerated path must demonstrate a **measured, reproducible M1/UMA speedup** (committed benchmark artifact, `benchmarks/apple_uma_mechanical_sympathy.py`) while the parity gate (criterion 1) holds. An "accelerated" path that does not beat the pure-Python baseline is rejected. This prevents shipping a fast path that isn't faster.

---

## Decisions (per the "most genius/optimal" directive)

- **Q1 (M1):** expose Rust **f64** GP; parity contract = **bit-identical** (matched i-major scatter order, no FMA), not tol-matched — else flipping `CORE_BACKEND=rust` breaks I-02 replay-determinism (`_psi_digest`/wave-residual bytes shift). Fail-closed on any ULP divergence over N=10,000; if bit-identity is unattainable, the f64 Rust path is **not shipped**.
- **Q2 (M6):** κ=1.0-on-failure *is* the required "parameters unchanged" no-op, and the typed `OptimizationFailure` is already returned alongside — so the fix is legibility (a test pinning that failure surfaces as `OptimizationFailure`) + the reason rename to `sampled_unimodality_violation_observed`, **not** breaking the working seam.
- **Q3:** the sixth criterion is the Mechanical-Sympathy gate above; adopt the quarantine reading in wrinkle #4.
- **Q4 (ADR-0244 §2.3):** **RESOLVED — `Q_top` proven vacuous, retire from egress.** The non-vacuity demonstration was attempted and failed: `evals/adr_0244_qtop_vacuity` (pinned by `tests/test_adr_0244_qtop_vacuity.py`) shows `Q_top = 0.000e+00` exactly on every versor, redundant with the closure residual off the manifold, and blind to a versor-preserving identity attack (`ΔQ_top = 0` passes an attack that drops identity overlap to 0.963). Do **not** wire it as an egress gate; keep only as a closure-derived diagnostic.
- **Q5 sequencing:** ADR-0243 Phase 4 → Phase 5 → **D0** (this) → **D1** (semantic rigor) → **D2** (mechanical sympathy) → **D3** (search honesty). **D4 = ADR-0244 + ADR-0245 implementation — IN PROGRESS.** Both prerequisites (§4-vs-§2 reconciliation, `Q_top` vacuity) are resolved in the ADRs as of D4 Phase 0 (2026-07-17); full phased plan + live progress: `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md`.

Every D-batch PR: in-worktree smoke gate + fast lane green before merge; merge-commit on explicit authorization; local-first CI.
