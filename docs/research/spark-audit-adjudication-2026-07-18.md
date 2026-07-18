# Spark Audit Adjudication — claim-by-claim verification against `main`

**Status**: Record (verification complete 2026-07-18)
**Verified against**: `main @ 54659b76` (post Rings 2+3 merge)
**Inputs**: `docs/research/core_labs_core_technical_gap_audit.pdf` ("Evolutionary Landscape", 8pp),
`docs/research/core_repository_systems_audit_and_gap_analysis.pdf` (systems-grade review, 4pp)
**Method**: three independent read-only verification passes over the live tree; every claim
adjudicated with file:line evidence before being allowed to become a work item.
**Companion**: `docs/research/intelligence-loop-homestretch-plan-2026-07-18.md` (the plan built on this record)

---

## 1. Headline finding: the audits are one day stale

Both documents describe the repository **before the 2026-07-17 cohesion-directive waves**
(D1/D2, ADR-0244 Phases 2–6, ADR-0243 flagship lifecycle, ADR-0246 rings). Most named gaps
were closed on `main` the day before the audits were delivered:

| Closing commit | What it closed |
| :--- | :--- |
| `c3b4d045` feat(adr-0243) flagship cognitive_lifecycle.py | ingress → relax → egress orchestration |
| `4ec2c8b9` refactor(adr-0244) D1 semantic rigor | full 256-bit digests + LE byte-order |
| `82b031d1` perf(adr-0244) D2 mechanical sympathy | Rust f64 GP fast-path + `_cached_eigh` memoization |
| `5c69b741` Phase 5a §2.7 content-id semantic rigor | remaining content-id sites |
| `918aa843` Phase 4 governed f64→f32 serving-boundary cast | Serves-Boundary Cast Contract |
| `5027adf8` ADR-0244 + ADR-0245 Proposed→Accepted (Joshua Shay) | audits assume both still Proposed |

Rule reaffirmed: **external audit claims are point-in-time and must be verified against source
before being acted on** (see also `feedback-read-source-not-sandbox-traces`).

---

## 2. Claim-by-claim verdicts

### Refuted / already closed

| # | Audit claim | Verdict | Evidence |
| :--- | :--- | :--- | :--- |
| 1 | "Relax phase omitted — orchestrator skips ingest→egress" | **REFUTED** | `CognitiveLifecycleEngine.solve()` runs `ingest_context` → `relax_to_ground` → `egress` (`core/physics/cognitive_lifecycle.py:1054-1071`); `relax_to_ground` (`:530`) is deterministic imaginary-time relaxation with a certified `RelaxationCertificate` |
| 2 | "Hardcoded `[RESONANT_LOCK…]` mock readback; sine-wave proxies" | **REFUTED** | No such string anywhere (grep empty); real geometric readback exists: `VocabManifold.nearest()` = exact CGA inner-product argmax, "no cosine similarity, no ANN index" (`vocab/manifold.py:261-298`) |
| 3 | "`_cached_eigh` LRU completely missing in identity.py" | **REFUTED** (category error) | ADR-0245 §2.4 targets the frozen ProblemHamiltonian, not identity.py; implemented exactly to spec at `cognitive_lifecycle.py:509-522`, keyed `(hamiltonian_id, H_mat.tobytes())`, called at `:588`. `identity.py` performs zero eigendecompositions. ADR-0245 status map records §2.4 "✅ Done" |
| 4 | "Vault digests truncated to 24 hex chars" | **REFUTED** | Vault hashing is full 64-hex: `vault/store.py:513-515`, `vault/crdt.py:204`, `core/physics/holographic_vault.py:80`. Only human-readable labels truncate (`core/demos/*`, `core/cli_teaching.py:626,977`) — explicitly permitted by ADR-0245 §2.3 |
| 5 | "Platform-dependent hashing (no `<f8` coercion)" | **REFUTED** for all load-bearing sites | `_le_f64_bytes` (`cognitive_lifecycle.py:137-138`), `holographic_vault.py:79`, `identity_action.py:223,528` — all coerce `np.dtype("<f8")`. Lone hygiene residual: `biography.py:62` hashes bare `float64.tobytes()` (byte-identical on LE targets, outside the vault content-address set) — folded into plan Phase 2 |
| 6 | "Fibonacci API drift (missing `best_observed_point`/`eval_sequence`)" | **REFUTED** | `SearchTrace` compat dataclass carries exactly those fields (`fibonacci_search.py:108-112`) via `search_trace_from_result` (`:368`); `FibonacciSearchCertificate` keeps `minimizer`/`ordered_points`/`ordered_values` (`:60-63`) |
| 7 | "GoldTether residual math duplicated inline elsewhere" | **REFUTED** | One shared kernel: `goldtether.py:117-125` `coherence_residual` delegates to `WaveManifold.measure_unitary_residual`; `cognitive_lifecycle.py:831` calls the same kernel |
| 8 | "Biography holonomy not implemented — no lifelong learning mechanism" | **REFUTED as stated** (see §4 for what IS open) | `integrate_biography` builds the holonomy blade via `holonomy_encode` (`core/physics/biography.py:66-110`); pinned by `tests/test_adr_0240_biography_holonomy.py:17-51`; PASS-gated wiring layer exists (`biography_wiring.py:174`) |

### Rejected as doctrine violations — must NOT be applied

| Audit recommendation | Why rejected |
| :--- | :--- |
| "Wire Fibonacci search to run online calibration on live sensory streams" | Violates master-plan **A-04** (serve-path containment: wave/Fibonacci operators quarantined to `evals/` + calibration), **I-03** (no self-mutation), **R-04** (hot paths receive only pre-ratified frozen scalars). Calibration correctly lives in `evals/adr_0244_gamma_calibration/__init__.py:187` and `evals/analogical_transfer/kappa_calibration.py:30` (via `goldtether.propose_kappa_line_search`, `goldtether.py:567-606`) |
| "Integrate GoldTetherMonitor directly into WaveManifold" | Inverts layering: `goldtether.py` imports `WaveManifold`, not vice versa. Correct fix is the opposite direction (plan Phase 3) |

---

## 3. Naming / provenance reconciliation

- The audits' `multimodal_lifecycle.py` = the real `core/physics/cognitive_lifecycle.py`.
- The audits' `vocab/readback_rules.py` = the real `vocab/manifold.py` (`VocabManifold`).
- **`core_logos` does not exist as code.** It was the predecessor `core-ai` subsystem;
  `docs/adr/ADR-0011-renderer.md:96` states no `core_logos` equivalent will be introduced.
  The serve-time articulation role is played by `generate/` (`realizer.py`, `articulation.py`,
  `surface.py`, `stream.py`), consumed by `chat/runtime.py` (`:95-111`). "core_logos is the
  weakest link" therefore maps to the `generate/` stack.
- The `docs/research/` ADR-0241…0243 documents are the Spark research series that seeded the
  canonical `docs/adr/` ADR-0241…0245 (now **Accepted**, ratified 2026-07-17). The canonical
  ADRs supersede the research drafts wherever they diverge.

---

## 4. Confirmed real seams (survived verification — these ARE the work)

- **S1 — Articulation seam.** The lifecycle's `egress_gate` stops at `route="readback_eligible"`
  (`cognitive_lifecycle.py:803,852`) and never invokes `VocabManifold.nearest()`
  (`cognitive_lifecycle.py` imports no `vocab`, `:68-76`). The field→token step is unwired even
  inside the quarantine corridor; the comprehend→reason→articulate loop does not close, and the
  "hearing ourselves think" feedback (re-ingesting own articulation) does not exist.
- **S2 — Learning write-path dormant.** `integrate_validated_biography`
  (`biography_wiring.py:174`, eval-report-PASS gated) has zero live callers (tests only).
  Topological-charge conservation exists (`chiral_gate.py:1-114`, sgn(Q_top) latching) but is
  wired into `GoldTetherMonitor` (`goldtether.py:160,242`), decoupled from biography updates
  (which use the wave unitary residual instead). Machinery built; nothing drives it; the two
  guards are not composed.
- **S3 — Autonomy floor bypassed in the corridor.** `cognitive_lifecycle.py:831` checks the raw
  unitary residual directly, bypassing `GoldTetherMonitor` autonomy-level modulation + chiral
  latching (only `self_authorship.py:15` consumes the Monitor). One guard should govern, in the
  goldtether→WaveManifold layering direction.
- **S4 — The serving bridge is the ratification frontier.** Serving is the symbolic `generate/`
  path; the wave corridor is Tier-2 off-serving by design (`core/physics/__init__.py:156,187`
  TYPE_CHECKING-only; runtime instantiation only in `evals/adr_0243_cognitive_lifecycle/__init__.py:117,119`
  and tests). The governed seam machinery — ADR-0247 ports + ADR-0248 handoffs — is merged,
  flag-off, **Proposed**, awaiting evidence and Shay's ruling.
- **S5 — `generate/` upgrade deferred** by explicit direction until S1–S3 + the measurement
  instrument land (plan Phase 6).
