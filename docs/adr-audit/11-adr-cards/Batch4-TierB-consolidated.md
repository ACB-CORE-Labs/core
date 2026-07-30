# Batch 4 — Tier B Consolidated Audit Cards (ADR-0151 to ADR-0200)

**Verified against:** `main` @ `cbfc8ccb` | **Date:** 2026-07-29  
**Audit Scope:** Batch 4 Tier B Zones (B4.1 to B4.3, 10 ADRs total)  
**Rigor Level:** Consolidated pass under 2026-07-29 cost correction protocol (bounded investigation depth, code/test inspection only, concise per-axis scoring).

---

## Zone B4.1 — CORE Workbench UI & HITL Async Queue

**Members:** ADR-0160, ADR-0161, ADR-0162, ADR-0173 (4 ADRs)  
**Zone:** `L11-hitl-async-queue` / `workbench-ui` | **Tier:** B  
**Prior Evidence:** `workbench/api.py`, `workbench-ui/`, `teaching/queue.py`, `.github/workflows/ratify-proposal.yml`

### ADR-0160 — CORE Workbench v1: operator/auditor UI before public chat
- **Content summary:** Establishes CORE Workbench v1 as an operator/auditor interface with read-only observability over Chat, Trace Drawer, Proposal Review Queue, Eval Center, and Replay Theater.
- **Build axis:** `full` — Implemented in backend `workbench/` (`api.py`, `server.py`, `schemas.py`, `readers.py`) and frontend React/Vite app `workbench-ui/` (`src/`, `package.json`).
- **Liveness axis:** `live` — Served via `core workbench serve` CLI subcommand and validated by `tests/test_workbench_api.py` and `tests/test_workbench_demos.py`.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 5 (Reconstruction-over-Storage) by keeping turn execution separate from proposal ratification and surfacing complete trace provenance.
- **Build fidelity:** `matches` — 5 primary modules implemented as specified with read-only default trust boundary.
- **Continuity:** `clean` — Foundational UI architecture for operator/auditor interaction with the CORE engine.
- **Necessity/generality:** `generalization-candidate` — High-leverage operator workbench for deterministic cognition engines.
- **Fitness/value:** Provides an inspectable, audit-native UI surface that matches CORE's deterministic, evidence-governed strengths.

### ADR-0161 — HITL Async Queue (W-009, L11)
- **Content summary:** Defines the HITL Async Queue as a derived projection over `proposals.jsonl` and `contemplation/runs/*.json` with a 256 pending proposal cap and dedup by `proposal_id`.
- **Build axis:** `full` — Implemented in `teaching/queue.py`, `teaching/proposals.py`, `.github/workflows/ratify-proposal.yml`, and `core teaching hitl-queue` CLI subcommands.
- **Liveness axis:** `live` — Validated by `tests/test_hitl_queue_submission_invariants.py` and active in proposal submission and review workflows.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Fail-Closed principles by enforcing deterministic queue identity and backpressure without introducing a new storage substrate.
- **Build fidelity:** `matches` — Supports 3 operator interaction surfaces (PR, workflow_dispatch, CLI), 256 cap, and auto-refusal on duplicate or dependent proposals.
- **Continuity:** `clean` — Extends ADR-0057 and ADR-0151 proposal pipeline into a bounded, replayable queue view.
- **Necessity/generality:** `irreducible` — Mandatory backpressure and queue projection logic for human-in-the-loop proposal lifecycle.
- **Fitness/value:** Closes W-009 substrate-liveness item and prevents unbounded pending proposal accumulation.

### ADR-0162 — Workbench Design System (v1)
- **Content summary:** Establishes the design substrate for Workbench UI, defining semantic CSS tokens, dark mode, `StableJsonViewer` invariants, and 1:1 badge mappings to engine enums.
- **Build axis:** `full` — Implemented in `workbench-ui/src/design/tokens/` (`tokens.css`, `tokens.ts`), `workbench-ui/src/design/components/StableJsonViewer/`, and badge components.
- **Liveness axis:** `live` — Active design system driving the `workbench-ui/` web app, verified by `workbench-ui/preview/` and e2e Playwright tests in `workbench-ui/e2e/`.
- **Design fidelity:** Honors Axiom 7 (Reality-over-Inheritance) and Pillar II by binding badge colors strictly to `EpistemicState`, `NormativeClearance`, `ReviewState`, and `GroundingSource` enums in `core/epistemic_state.py`.
- **Build fidelity:** `matches` — Enforces 6 `StableJsonViewer` trust invariants, keyboard navigation (`⌘K`, `Esc`), and a strict no-go list against animated cognition theater.
- **Continuity:** `clean` — Design substrate for all `workbench-ui` frontend routes and components.
- **Necessity/generality:** `generalization-candidate` — High-leverage design system pattern for deterministic audit UIs.
- **Fitness/value:** Prevents visual drift and guarantees an audit-grade, quiet, and responsive user experience bound strictly to engine state.

### ADR-0173 — Workbench Ratification Trust Boundary
- **Content summary:** Amends ADR-0160's read-only stance to admit operator-driven proposal ratification via the UI as a local keyboard accelerator over existing Python handlers.
- **Build axis:** `full` — Implemented in `workbench/api.py` (`POST /math-proposals/{id}/ratify`) calling `apply_lexical_claim`, `apply_frame_claim`, and `apply_composition_claim` in `teaching/`.
- **Liveness axis:** `live` — Pinned by `tests/test_workbench_ratify_frame.py`, `test_workbench_ratify_lexical.py`, `test_workbench_ratify_composition.py`, and `test_workbench_operator_telemetry.py`.
- **Design fidelity:** Honors Fail-Closed principles, Pillar II, and ADR-0161 Surface C doctrine by binding `workbench/api.py` to local-only `127.0.0.1` and requiring replay-passed preconditions.
- **Build fidelity:** `matches` — Appends `ratifier_kind: "workbench"` to ratification records while maintaining exact CLI handler execution and case 0050 hazard pins.
- **Continuity:** `clean` — Narrowly amends ADR-0160 read-only stance while honoring ADR-0161 surface boundaries.
- **Necessity/generality:** `irreducible` — Non-negotiable trust boundary governing UI-driven corpus/proposal mutation.
- **Fitness/value:** Accelerates operator ratification loop while preserving complete replay-equivalence and safety gates.

### Zone B4.1 Findings (Rollup)
- **AA-368** 🟢 **Monitor** — CORE Workbench v1 (ADR-0160) and backend API (`workbench/api.py`, `workbench/server.py`) deliver read-only trace, replay, proposal, and eval inspection.
- **AA-369** 🟢 **Monitor** — HITL Async Queue (ADR-0161) derives queue projections from `proposals.jsonl` with a 256 pending cap, duplicate/dependency checks, and `core teaching hitl-queue` CLI.
- **AA-370** 🟢 **Monitor** — Workbench Design System (ADR-0162) implements semantic CSS tokens, dark mode, `StableJsonViewer` invariants, and 1:1 badge mappings to `EpistemicState` enums in `workbench-ui/`.
- **AA-371** 🟢 **Monitor** — Workbench Ratification Trust Boundary (ADR-0173) cleanly wraps Surface C local Python handlers with `ratifier_kind: "workbench"` and `127.0.0.1` local-only enforcement.

---

## Zone B4.2 — Learning Arena, Motor Efferent & Substrate Languages

**Members:** ADR-0196, ADR-0198, ADR-0199, ADR-0200 (4 ADRs)  
**Zone:** `L0-algebra` / `L2-sensorium` / `reliability-gate` | **Tier:** B  
**Prior Evidence:** `docs/zig/`, `sensorium/efferent.py`, `core/reliability_gate/`, `docs/claims_ledger.md`

### ADR-0196 — Native Substrate Language Doctrine (Python / Rust / Zig)
- **Content summary:** Ratifies component-by-component native substrate doctrine, keeping Python as Ring 2 cognition source of truth, Rust as Ring 1 algebra backend, and Zig as Ring 1 candidate under a G0–G8 proof ladder.
- **Build axis:** `full` — Implemented in `docs/zig/` (`README.md`, `adoption-gates.md`, `core-native-system/`, `runtime-ffi/`) and enforced across native integration PRs.
- **Liveness axis:** `live` — Enforces backend selector `CORE_BACKEND=rust` in `algebra/backend.py` and gates all candidate Zig integrations behind explicit G0–G8 proof ladder steps.
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 7 (Reality-over-Inheritance) by rejecting wholesale Zig rewrites and keeping fast-changing cognition semantics in Python.
- **Build fidelity:** `matches` — Strictly enforces locked reference contracts (G1 lock in ADR-0180) and prohibits default-by-availability or unreviewed native FFI code.
- **Continuity:** `clean` — Governs Ring 1 native substrate architecture for Rust (`core-rs`) and Zig candidate modules.
- **Necessity/generality:** `irreducible` — Essential architectural doctrine governing language boundaries and FFI safety.
- **Fitness/value:** Prevents language fragmentation while directing high-performance native compilation strictly to low-level algebraic and CRDT kernels.

### ADR-0198 — Motor as Efferent Modality — Protocol Gap & Governance (Design Spike)
- **Content summary:** Identifies efferent modality asymmetry (Gap A & Gap B) and introduces `ModalityRegistry.decode()` with `AuthorityToken` and `VerdictEnforcingEfferentGate` in `sensorium/efferent.py`.
- **Build axis:** `full` (for Gap A & efferent gate) / `scaffolded` (for motor decoder) — Implemented in `sensorium/efferent.py` and `sensorium/registry.py`.
- **Liveness axis:** `live` (gate fail-closed) / `dead` (decoder) — Gate is live and fail-closed (`tests/test_efferent_gate.py`), while physical motor decoding is `None` (deferred to ADR-0216).
- **Design fidelity:** Honors Fail-Closed principles and Pillar II by requiring `AuthorityToken` and per-decode safety/ethics/tool_scope action verdict checks before any motor output.
- **Build fidelity:** `matches` — Gap A `decode()` method and Gap B runtime efferent gate implemented; motor decoder intentionally unbuilt/fail-closed.
- **Continuity:** `clean` — Extends ADR-0013 sensorium protocol to efferent modalities.
- **Necessity/generality:** `generalization-candidate` — Canonical protocol for efferent modality output gating.
- **Fitness/value:** Establishes fail-closed output gating for efferent action execution before any actuator command can be formed.

### ADR-0199 — Cross-Domain Learning Arena Contract
- **Content summary:** Generalizes ADR-0175 attempt-and-eliminate practice into a 4-piece template (`DomainSolver`, Gold anchor set, Capability classes, Tier-2 verifier) using a single pinned Wilson lower bound floor across 5 capability domains.
- **Build axis:** `full` — Implemented in `core/reliability_gate/` (`floor.py`, `ledger.py`, `ceilings.py`, `gate.py`, `propose.py`) and `core/capability/domains.py` (`DomainSolver`, `GoldTether`, `run_practice`).
- **Liveness axis:** `live` — Validated by `tests/test_run_attempt_binding.py`, `tests/test_sealed_practice_trace.py`, and domain practice modules.
- **Design fidelity:** Honors Axiom 5 (Reconstruction-over-Storage) and Pillar II by reusing single Wilson lower bound floor (`WILSON_Z=2.576`, `N_MIN=10`) across all 5 capability domains.
- **Build fidelity:** `matches` — 4-piece template and 3 mandates (one floor, anchor independence, absolute seal) implemented with `run_practice` attempt-to-ledger pipeline.
- **Continuity:** `clean` — Generalizes ADR-0175 attempt-and-eliminate practice across all capability domains.
- **Necessity/generality:** `generalization-candidate` — Universal cross-domain practice and reliability contract.
- **Fitness/value:** Allows any domain subject to plug into attempt-and-eliminate practice without re-deriving reliability infrastructure.

### ADR-0200 — Expert-Claim Reconciliation: Record the Fail-Closed Revert as Designed Behavior
- **Content summary:** Reconciles documentary drift when `mathematics_logic` auto-reverted from `expert` to `audit-passed` due to GSM8K coverage report digest mismatch post-signing.
- **Build axis:** `full` — Reconciled in `docs/claims_ledger.md`, `evals/math_expert_claims/v1/expert_claims_math_v1_signed.json`, `docs/reviewers.yaml`, and test files.
- **Liveness axis:** `live` — Validated by `tests/test_mathlogic_expert_ledger_flip.py` and `tests/test_adr_0120_math_expert_promotion.py`.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II by treating digest mismatch revert as correct, load-bearing system behavior rather than a defect.
- **Build fidelity:** `matches` — History artifacts keep receipts; current-state files/tests reconcile to true machine state (`audit-passed`).
- **Continuity:** `clean` — Reconciles ADR-0120 expert claim status documentation with live code reality.
- **Necessity/generality:** `irreducible` — Mandatory governance reconciliation for audit-passed expert claims.
- **Fitness/value:** Eliminates document/code drift and proves the engine's fail-closed self-revocation mechanism when evidence bundles drift.

### Zone B4.2 Findings (Rollup)
- **AA-372** 🟢 **Monitor** — Native Substrate Language Doctrine (ADR-0196) locks Python as Ring 2 cognition source of truth and establishes G0–G8 adoption ladder for Ring 1 native code.
- **AA-373** 🟡 **Repair** — Motor Efferent Decoder Spike (ADR-0198) implemented Gap A `ModalityRegistry.decode()` and fail-closed efferent gate (`sensorium/efferent.py`), while physical motor decoding remains fail-closed and deferred to ADR-0216.
- **AA-374** 🟢 **Monitor** — Cross-Domain Learning Arena Contract (ADR-0199) generalizes ADR-0175 attempt-and-eliminate practice using a 4-piece template and pinned Wilson lower bound across all 5 capability domains.
- **AA-375** 🟢 **Monitor** — Expert-Claim Reconciliation (ADR-0200) reconciled document/code drift, confirming fail-closed auto-revert of `mathematics_logic` to `audit-passed` upon evidence bundle drift.

---

## Zone B4.3 — Measurement & Sequencing Governance

**Members:** ADR-0166, ADR-0170 (2 ADRs)  
**Zone:** `L4-comprehension` / `eval-governance` | **Tier:** B  
**Prior Evidence:** `evals/`, `generate/recognizer_anchor_inject.py`, `generate/math_candidate_graph.py`

### ADR-0166 — Measurement-Capability Sequencing Discipline
- **Content summary:** Establishes the binding rule that capability must land before the measurement lane depending on it, enforced via a 3-question test during PR review.
- **Build axis:** `full` — Governance discipline enforced across `evals/`, `core/cli_eval.py`, and PR reviews.
- **Liveness axis:** `live` — Active sequencing rule preventing ungrounded 0/N wishlist eval lanes (e.g. `evals/articulation_of_status`, `evals/gsm8k_math/`).
- **Design fidelity:** Honors Pillar II (Semantic Rigor) and Axiom 7 (Reality-over-Inheritance) by rejecting synthetic wishlist eval lanes authored ahead of capability.
- **Build fidelity:** `matches` — TBD rows are re-run debts for existing lanes, not placeholders for unbuilt operators.
- **Continuity:** `clean` — Foundational sequencing invariant across eval suites and capability roadmaps.
- **Necessity/generality:** `irreducible` — Mandatory governance rule for eval lane authoring.
- **Fitness/value:** Keeps eval surface signal-to-noise ratio high and prevents misleading zero-score measurement noise.

### ADR-0170 — Recognizer Injector Contract Widening
- **Content summary:** Widens the `inject_from_match` return type from `tuple[CandidateInitial, ...]` to `tuple[CandidateInitial | CandidateOperation, ...]` to unblock operation-level recognizer injection.
- **Build axis:** `full` — Implemented in `generate/recognizer_anchor_inject.py` (`_INJECTORS`, PR #377) and `generate/math_candidate_graph.py`.
- **Liveness axis:** `live` — W1 (type widening) and W2 (DCS-S1 acquisition verbs emitting `CandidateOperation(add)`) shipped to serving, validated by `tests/test_adr_0170_*`.
- **Design fidelity:** Honors Fail-Closed principles and Pillar II by preserving wrong=0 invariants, branch-disagreement discipline (ADR-0131.G.1), and type-level admissibility.
- **Build fidelity:** `matches` — `inject_from_match` returns `SentenceChoice` union; W1/W2 shipped while W3–W5 (CandidateRate) remain deferred to ADR-0171.
- **Continuity:** `clean` — Extends ADR-0163.D.2 recognizer-anchor injector contract.
- **Necessity/generality:** `generalization-candidate` — High-leverage recognizer dispatch widening.
- **Fitness/value:** Unblocks operation-level recognizer injection (e.g. acquisition verbs `add`) while holding wrong=0.

### Zone B4.3 Findings (Rollup)
- **AA-376** 🟢 **Monitor** — Measurement-Capability Sequencing Discipline (ADR-0166) enforces "capability before measurement" via the 3-question test, preventing ungrounded 0/N wishlist eval lanes.
- **AA-377** 🟢 **Monitor** — Recognizer Injector Contract Widening (ADR-0170) shipped W1 type-widening and W2 acquisition verb `CandidateOperation(add)` injection while preserving wrong=0 and case 0050 hazard canary pins.
