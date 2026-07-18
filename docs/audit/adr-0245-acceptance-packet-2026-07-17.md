# ADR-0245 — D4 Acceptance Packet for Joshua

**Arc:** ADR-0245 CGA Unification: Mechanical Sympathy & Semantic Rigor — the foundation ADR-0244's identity gate sits on. Committed as a real companion ADR in D4 Phase 0; its D4 scope (§2.2 cast, §2.3 residual, §3 gate) closed across Phases 4–5.
**Evidence base:** `feat/adr-0244-d4 @ 8ef80daa` (Phases 0–5 on `main`).
**Status of ADR-0245:** **Proposed — submitted for your ruling.** The `Proposed → Accepted` flip is a **separate one-line governance commit** with your ratification provenance inline (anti-self-Accept guard). **I have NOT flipped it** — §8 is PENDING.

---

## 1. Evidence summary (what is proven, and how)

| ADR § | Claim | Built as | Evidence | Verdict |
|-------|-------|----------|----------|---------|
| §2.1 | PyO3 Rust `geometric_product` f32 fast-path | `algebra/backend.py` (pre-existing), gated behind `CORE_BACKEND=rust` | f32 parity + dispatch-hygiene tests | **Supported** |
| §2.2 | Gated f64→f32 serving boundary | `serving_cast(...) → ServingState` (== ADR-0244 §2.5) | `test_adr_0244_serving_cast.py` (10): certified/admitted-only, precision-checked, f64 stays source of truth | **Supported** |
| §2.3 | Semantic rigor in content addressing | D1 hot path + Phase 5a: 4 residual content-ids → full 256-bit, no `default=str`, LE byte-order | `schema`/`plan_preflight`/`articulation_quality`/`holographic_vault`; collision proof below | **Supported** |
| §2.4 | `_cached_eigh` memoization (LAPACK once per content-addressed H) | `cognitive_lifecycle._cached_eigh` (D2) | `test_adr_0244_mechanical_sympathy.py`: cache hit → identical objects, no fresh `eigh` | **Supported** |
| §3 | Acceptance gate: parity ∧ ≥10× f32 speedup ∧ 0-LAPACK-on-repeat ∧ collision-resistance | `test_adr_0245_acceptance_gate.py` + parity/mechanical-sympathy suites | see §2 below | **All four legs green** |

---

## 2. §3 acceptance gate — the four legs

1. **Parity** — Rust GP bit-identical to Python: f64 N=10,000 (`test_geometric_product_f64_parity.py`) + f32 component-exact (`test_geometric_product_rust_parity.py`). ✅
2. **≥10× f32 speedup** — `test_adr_0245_acceptance_gate.py::test_rust_f32_geometric_product_is_at_least_10x`, Rust-guarded (skips with a reason where `core_rs` is unbuilt), with a parity sanity check so the speedup can't come from skipped work. **Measured on Apple M-series this arc: rust 2.86 µs/op vs python 1340 µs/op = 467×** (assertion is a conservative ≥10× for CI timing robustness). ✅
3. **0 LAPACK on repeat** — `test_adr_0244_mechanical_sympathy.py` (`_cached_eigh` cache hit returns identical `(evals, evecs)`). ✅
4. **Collision-resistance** — `_content_id` full 256-bit, type/structure-faithful (int≠str, bool≠int, nested-sensitive, key-order-invariant), fails closed on non-serializable input (no `default=str` collapse); `_psi_digest` sub-epsilon sensitive + deterministic. A coverage-manifest test maps all four legs to their home files. ✅

---

## 3. Deferred items (NOT completion blockers)

- Rust §5 SIMD / MLX / 64-byte-alignment acceleration — a separate optimization backlog, not this ADR's D4 scope.
- The f32 speedup is **measured where `core_rs` is built**; the committed test skips (visibly, with a reason) on runners without the Rust extension. The default backend remains pure-Python (`CORE_BACKEND` unset), so no serve-path behavior depends on the Rust build.

---

## 4. Gate results

Landed across D4 Phases 0 (commit), 4 (§2.2), 5a (§2.3), 5d (§3). Phase 5 gate: smoke **176**; fast lane **12032 passed, 25 skipped** (with a local `core_rs` build, the ~126 Rust-parity + f32-speedup tests ran live, all green); 43 Phase-5 targeted tests.

---

## 5. Requested action

**Rule on the ADR-0245 arc.** All four §3 legs are green and the two D4 build items (§2.2 cast, §2.3 residual) are complete. If you rule **Ratify**, the follow-up one-line governance commit flips `**Status**: Proposed → **Accepted** — ratified by Joshua Shay <date>` and records the ruling in §8. **I have not flipped the status; it awaits your explicit word.**

---

## 8. RULING RECORD

**PENDING — awaiting Joshua Shay's ruling.** No status flip has been made; ADR-0245 remains **Proposed**.
