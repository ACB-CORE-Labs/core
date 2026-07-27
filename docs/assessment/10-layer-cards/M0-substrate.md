# M0 — Substrate

**Kind:** layer · **Parent:** CORE · **Assessor:** Opus 5 (Phase 2)
**Verified at:** `8927c563` (2026-07-27)
**Liveness:** `live-serving` · **Fitness:** `fit` · **Topology role:** runtime boundary

> The medium, not the mind. Per the governing mental model, the field is the *electricity* and the intelligence is in the wiring — M0's entire job is to be a substrate so well-behaved that everything above it can be exact, replayable, and locatable when wrong. Cl(4,1) was chosen for one reason: it is the minimal algebra in which every conformal transformation is a versor, so every cognitive operation is algebraically closed by construction rather than by special-case handling. M0 must contain no cognition-specific policy; the moment it does, the substrate has started deciding.

**Telos stages:** recall, think/reason, articulate, backbone-runtime, replay/determinism (as the medium of all)
**Macro role:** Supplies closure, exactness, and bit-level replayability to every layer above.

---

## What it is / What it does

`algebra/` (9 modules) implements Cl(4,1) — geometric product, versor apply, reverse, `cga_inner`, the versor condition — with `algebra/backend.py` dispatching between a pure-Python implementation and an opt-in Rust one. `field/` (4 modules) holds `FieldState` and propagation. `core/physics/` (37 modules) sits atop the algebra with the wave/identity/quantity machinery.

The one non-negotiable invariant is `versor_condition(F) = ‖F·reverse(F) − 1‖_F < 1e-6`, checked at the injection gate and preserved across every transition, which is only ever the sandwich product `F' = V·F·reverse(V)`. Closure of field transitions is owned **solely** by `algebra/versor.py::_close_applied_versor`; no other site may repair it. `AGENTS.md` draws the bright line explicitly: *semantic anchoring* (allowed at named construction boundaries, preserves the condition by construction, expresses a relation in the cognitive model) versus *drift repair* (forbidden — restoring an invariant a prior function should have preserved). Naming may not disguise the distinction.

---

## Contract

- **Inputs:** injected multivectors from M2's gate; versors from packs and operators.
- **Outputs:** `FieldState`, exact CGA distances, closure verdicts.
- **Invariants:**
  - `versor_condition(F) < 1e-6` — never weakened to make code or tests pass — pin: algebra suite (15 files) — status: **running**.
  - No normalization/closure/repair outside owned boundaries; forbidden in `generate/stream.py`, `field/propagate.py`, `vault/store.py`, logging/telemetry — pin: `tests/test_third_door_cohesion.py` (AST-pinned off-serve quarantine).
  - Physics hot ops must import from `algebra.backend`, not direct pure-algebra modules — pin: `tests/test_physics_backend_dispatch_hygiene.py`.
  - f64 wave-residual pins stay on the Python product (Rust f32 GP is not parity-safe for 1e-9 pins).

---

## Design vs build

- **Design:** `docs/Yellowpaper.md` (formal Cl(4,1) specification), `docs/position_paper.md` §3, ADR-0241/0242 (wave-field, Fibonacci operators), ADR-0245 (CGA unification), ADR-0243 (lifecycle). `AGENTS.md` carries the invariants as law.
- **Build:** `live-serving`. Key files: `algebra/versor.py`, `algebra/backend.py`, `field/state.py`, `field/propagate.py`, `core/physics/`.
- **Evidence:**
  - Versor closure is enforced and the algebra suite runs it (15 test files) — pin+suite — would-fail-if-absent: **yes**.
  - Pure Python is the deterministic default; Rust is opt-in via `CORE_BACKEND=rust` — code-read — `algebra/backend.py:1-9` — would-fail-if-absent: **yes**.
  - `versor_condition` costs **0.448 ms against a 200 ms turn — 0.22%** — measurement — `docs/research/cga-hot-path-measurement-2026-07-25.md` — would-fail-if-absent: **n/a (a measurement)**.
  - CGA is ~73% of turn time via `cga_inner` → `geometric_product` at ~33,986 calls/turn in nearest-neighbour and salience search — measurement — same document.

---

## Capacity

- **Designed:** algebraically closed over the full conformal group; exact recall as a geometric fact.
- **Measured:** closure holds at the 1e-6 gate across all serving lanes; Rust backend records `core_rs import: False`, `using_rust(): False`, status `python_fallback` in the benchmark run.
- **Ceilings:** bit-exact determinism forbids JIT float reassociation (blocks MLX fusion without a ratifying ADR) and rules out bf16 (ε ≈ 7.8e-3, four orders coarser than the gate). Rust f32 geometric product is not parity-safe for the f64 residual pins.

---

## Dependencies & provenance

**feeds** → every layer; **constrained-by** → MV (bit-exact parity pins, `core-rs/tests/test_crdt_hash_parity.rs`); **owning ADRs:** ADR-0241, ADR-0242, ADR-0243, ADR-0245, ADR-0180.

---

## Stage coverage

| Stage | Verdict | Evidence |
|---|---|---|
| *(medium for)* recall / think / articulate / backbone / replay | **covered** | Closure enforced by a running suite; exact CGA distance is the recall primitive; determinism pinned bit-exact |

**Zone roster:** `L0-algebra` (live-serving, confirmed), `L1-field` (partial-wiring-debt, not individually re-verified).

**Rollup note:** weakest-link rollup. M0 is the most solid layer in CORE and the least in doubt.

---

## Judgment

**Fitness: `fit`.** M0 does exactly one thing and does it without compromise. Notably, the position paper's claim that drift-correction machinery "was deleted because it only exists when the algebra is not closed" is architecturally coherent with `AGENTS.md`'s bright-line rule — the doctrine and the code tell the same story here, which is not true everywhere else in this assessment.

**Honest wrinkles:**
- **The optimization target has been repeatedly misidentified**, twice in documented history. Both an external assessment and a hardware blueprint aimed at `versor_condition` (0.22%) rather than `cga_inner`/`geometric_product` (~73%). The lesson generalizes past M0: the invariant is the *most visible* thing in the layer, so it attracts attention the profile does not justify.
- **`CORE_BACKEND=rust` is off by default and nobody currently knows whether parity holds.** The verification attempt on 2026-07-25 was blocked — `cargo` could not reach `static.crates.io` under the sandbox network policy. This is an open question with a stated blocker, which is the honest state, but it means a written-and-shipped Rust kernel sits unused and unverified.
- The measured hot path (`cga_inner` in salience/nearest-neighbour search) is M0 *compute* driven by an M3/CR-1 *mechanism* that has no owning card or ADR. Optimization work here has nowhere to attach architecturally — see the Candidate Register CR-1 revision in the M2/M3 cards and Phase 4.

**Open questions:**
- Does `core_rs` still hold bit-exact parity, and should Rust become the default? (→ ruling; blocked on network access)
- Does the ~73% CGA cost in salience search justify an algorithmic change rather than a backend change? (→ Phase 4)
