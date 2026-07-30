# B3 — Roadmap & Rust Parity

**Zone:** cross-cutting infra (MV / M0) · **Tier:** B · **Members:** ADR-0016, ADR-0020
**Verified against:** `main` @ `cbfc8ccb` (2026-07-29)

Both ADRs are process/sequencing decisions rather than mechanism decisions, but they still bind hard artifacts: ADR-0016 defines the `evals/<lane>/` contract and the benchmark-discipline rules that `evals/framework.py` and `docs/eval_methodology.md` still enforce for the lanes that use them; ADR-0020 sequenced the Rust (`core-rs`) parity port against Phase 5 and is still the governing decision behind today's `algebra/backend.py` dispatch. Both read as well-executed on their own narrow terms — the specific artifacts each ADR promised were built and can be pointed to by file and line — and both show the same shape of drift once measured against the codebase's current scale rather than its 2026-05-15/16 scope: ADR-0016's universal lane-shape mandate now covers less than half of `evals/`'s 129 top-level directories, and ADR-0020's Rust track, while correctly gated and safely off-by-default, does not reach the hot path its own cost argument was built on. Neither drift is a build failure in the narrow sense (the named artifacts exist); both are fitness/necessity findings once "does it still describe what runs" is asked directly, which is the audit's job and not either ADR's.

---

# ADR-0016 — Capability Roadmap and Eval Methodology

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B3 — Roadmap & Rust Parity (per `02-stack-taxonomy.md`) | **Tier:** B
**ADR status (as recorded in the file):** Accepted | **ADR date:** 2026-05-15
**Card author:** ADR Audit — Tier B (B3) | **`verified_at` SHA:** `cbfc8ccb`

---

## 1. Content summary

- **Decision made:** Adopt the Verifiable Competence Benchmark framework (`docs/capability_roadmap.md`) as CORE's governing capability-development plan: five benchmark-discipline rules (three-set split, versioned escalation, adversarial regeneration on pass, frontier baseline tracking, honest reporting), six phases (0–5), a fixed `evals/<lane>/` directory contract, and three open scope decisions (agency, tool use, code generation) to be pinned before Phase 3.
- **Alternatives explicitly rejected:** none named; the ADR's context frames the alternative as the status quo ("vibes-based evaluation"), not a second concrete design.
- **Artifacts the ADR claims will exist:**
  - `docs/capability_roadmap.md` — the full phased plan
  - `docs/eval_methodology.md` — extracted Part I (benchmark discipline contract)
  - `docs/PROGRESS.md` — progress tracker with evidence links
  - The `evals/<lane>/` contract: `contract.md`, `dev/`, `public/v1/`, `holdouts/`, `runner.py`, `baselines/`, `results/`
  - `core eval cognition` retrofitted as the first lane under the new convention
  - A governance rule: "every new eval lane must follow the convention or it does not merge"

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `docs/capability_roadmap.md` | partial | `docs/plans/capability_roadmap.md` | Moved (not deleted) in the 2026-07-04 "reorganize docs landscape" commit (`54e6bfc0`); content itself last narratively updated 2026-05-22 |
| `docs/eval_methodology.md` | yes | `docs/eval_methodology.md` | Present, amended in place by ADR-0105 and ADR-0109 (dated sections), last updated 2026-05-22 |
| `docs/PROGRESS.md` | yes, but stale | `docs/PROGRESS.md` (977 lines) | Present and detailed through 2026-05-26; no narrative update since (git log), despite ~2 months and 100+ further ADRs of subsequent project history |
| `evals/<lane>/` contract (`contract.md`+`dev/`+`public/v1/`+`runner.py`) | partial | `evals/framework.py:1-13` | Framework module documents and enforces the shape for lanes that use it; **only 60 of 129 top-level `evals/` directories carry a `contract.md`** (measured directly) |
| `core eval cognition` retrofit | yes | `evals/cognition/{contract.md,dev,public,holdouts,runner.py}` | Fully conforms to the mandated shape |
| "must follow convention or it does not merge" gate | no | — | No CI/merge-time check found requiring `contract.md` presence; `evals/framework.py`'s docstring states the shape as a convention, not as an enforced precondition for merge |

**Build axis:** partial — the mechanical contract (`evals/framework.py`) and roadmap documents (moved, not deleted) exist and are genuinely used by the lanes that conform (60/129, including all of the Phase 1–5 capability lanes checked: `english_fluency_ood`, `elementary_mathematics_ood`, `cognition`). But the universal governance clause ("every new eval lane must follow the convention or it does not merge") was never built as an enforced mechanism, and the majority of `evals/` subdirectories today (69/129) are ad hoc research/demo/probe tooling (`lab/`, `logos/`, `capability_index/`, `analogical_transfer/`, `adr_02xx_*/`, `comprehension/`, `conversation/`, `articulation/`, etc.) that were never intended to be lanes under this contract in the first place — the ADR's text does not anticipate that `evals/` would become a mixed-use directory.

## 3. Liveness / integration

- `evals/framework.py`'s lane-discovery and scoring machinery is genuinely used by the `core eval <lane>` CLI and is reached whenever a conforming lane (e.g. `cognition`, `english_fluency_ood`) is run — this part is live.
- The governance clause ("must follow convention or it does not merge") has no corresponding mechanism to sabotage: nothing enforces it today, so it cannot be un-wired — it was never wired.
- **Sabotage test:** removing `evals/framework.py` would break every conforming lane's CLI entry point — that part is load-bearing. Removing the (never-built) merge gate would change nothing observable, because nothing currently checks it; the drift already measured (54% non-conformance) is the sabotage test's answer in practice.
- **Liveness axis:** live for the mechanical contract and the lanes that use it; the universal-mandate half of the decision was never implemented as an enforced mechanism, so it never had a liveness state to lose — it is a decorative clause in the ADR's Consequences section, not a "was-live-now-dead" case.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | n/a | This is a process/methodology decision; it makes no hardware or substrate claim. |
| II. Semantic Rigor | Honors | Rule 5 ("Honest reporting... If a number cannot be reported honestly under these rules, the lane is not ready. Do not ship the lane.") is a direct instance of Pillar II's "no thresholds tuned for good enough." |
| III. Third Door | Tension | The ADR adopts a fairly conventional ML-benchmark playbook (dev/public/holdout split, versioned difficulty escalation, frontier baselines) rather than an original evaluation paradigm; sound and disciplined, but not a distinctively first-principles construction. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | Process decision, no geometric content. |
| 2. Field-State | n/a | — |
| 3. Propagation-over-Mutation | n/a | — |
| 4. Dual-Correction | n/a | — |
| 5. Reconstruction-over-Storage | n/a | — |
| 6. Compilation-Last | n/a | — |
| 7. Reality-over-Inheritance | n/a | — |

(This ADR governs methodology and documentation practice, not an algebra/field mechanism — the seven axioms, which grade geometric/computational design choices, have no bearing on it. Marked `n/a` per the schema rather than left blank.)

## 5. Build fidelity — does the code match the decision?

Where the mechanical contract is used, it matches: `evals/framework.py`'s required shape (`contract.md`, `runner.py`, `dev/cases.jsonl`, `public/v1/cases.jsonl`, optional `holdouts/`/`baselines/`/`results/`) is exactly what ADR-0016 specifies, and the 60 conforming lanes (including the ones ADR-0016 itself names as Phase 0/1 exit evidence) match it precisely.

Divergence, all measured directly against the current tree:
1. **Lane-shape coverage has collapsed from "universal" to "minority."** 60 of 129 top-level `evals/` directories (46%) carry `contract.md`; the remaining 69 are tooling, probes, demos, and ADR-specific one-off scripts that were never meant to be gated capability lanes but live in the same directory the ADR declared as lane-only territory.
2. **`docs/PROGRESS.md`, the ADR's own designated progress-tracking artifact, is stale.** Its last narrative entry is dated 2026-05-26; per `git log`, its last real edit was a 2026-07-03 mechanical refactor commit, not content. Two months and well over a hundred subsequent ADRs (through ADR-0265+, the Foundations Audit, FA-1) are not reflected there — the project's actual progress-tracking has migrated to `docs/assessment/` and `docs/adr-audit/` without this consequence being formally retired or redirected.
3. **A scope-decision deadline moved without a formal amendment to this ADR.** ADR-0016 lists "Code generation (first-class articulation target)" as one of three open scope decisions "to be pinned before Phase 3." One day later, ADR-0020 (Consequences) silently restates it as "before Phase 5" — a different deadline, asserted by a different ADR, not by a dated amendment to ADR-0016 itself, which is exactly the practice ADR-0016's own Consequences section rules out ("amendments are dated, never silently rewritten"). Even the moved deadline was missed: `docs/PROGRESS.md`'s Open Scope Decisions table still records "Code generation | Open | Before Phase 5" after Phase 5 and Phase 6 both opened.

**Build-fidelity axis:** partial drift — the contract mechanism itself is faithfully implemented and used correctly where it's used; the universal-coverage claim and the progress-tracking consequence have both drifted well past the point a fresh reader of the ADR would expect.

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Contradicts `Whitepaper.md`? No section reviewed contradicts this ADR; it is not a Whitepaper-governed mechanism.
- Contradicts `Yellowpaper.md`? None found on the sections reviewed.
- Contradicts, silently overlaps, or is superseded by another ADR? Cleanly extended in dated stages: ADR-0091 (Domain Pack Contract v1) layers `dev/public/holdout` discipline onto packs; ADR-0105 (sealed-holdout encryption) hardens the holdout half; ADR-0109 (lane-shape-aware thresholds) generalizes the scoring contract to five typed shapes; ADR-0114/0119 (GSM8K lane substrate) build a full lane under the same contract. None of these contradict ADR-0016's terms. ADR-0020 depends on it directly for Phase sequencing. The one drift worth naming here (the silently-moved scope-decision deadline, §5 item 3) is a fidelity issue with the ADR's own text, not a contradiction between two ratified decisions, so it is scored under Build fidelity rather than Continuity.
- **Continuity axis:** clean.

## 7. Necessity / generality

1. **Necessity:** the underlying governance need — some falsifiable discipline for capability claims — is genuinely necessary for a project making the honesty claims CORE makes about itself (see `evals/CLAIMS.md`'s own verification-contract framing). The *specific* `evals/<lane>/` universal directory-shape mandate, however, is not load-bearing in its stated universal form: the system already runs fine with a bifurcated `evals/` (conforming lanes + ad hoc tooling), and nothing currently enforces or needs the "no exceptions" reading.
2. **Reducibility:** not reducible to an L0/L1 algebra/field operator — this is a documentation/process convention, outside that layer entirely.
3. **Extensibility:** the organic split already visible in `evals/` (60 conforming lanes vs. 69 non-lane tooling directories) is itself the shape of a natural amendment: ratify two first-class categories inside `evals/` — gated capability lanes (this ADR's contract, unchanged) and research/probe/demo tooling (currently untracked by any ADR) — rather than treating the 69 as unaddressed drift against a mandate that was never going to hold at this scale.

**Necessity/generality axis:** irreducible (as a governance need) / generalization-candidate (the specific directory-contract should be amended to name the two populations `evals/` has already become, rather than restating a universal mandate the tree has already outgrown).

## 8. Fitness / value

- `docs/assessment/10-layer-cards/MV-verification-evidence.md` cites this methodology's direct descendants as live and load-bearing: 11 Tier-2 lanes carry CI-enforced SHA pins (`CLAIMS.md` + `.github/workflows/lane-shas.yml`); the lane-shape registry fails closed on unknown lane ids; 21 hand-curated test suites exist over 881 test modules. This is strong evidence the *mechanism* this ADR started has real downstream teeth.
- The capability ledger promotions recorded in `docs/PROGRESS.md` Phase 6 (`mathematics_logic`, `physics`, `systems_software` reaching `audit-passed`) all trace through lane results scored under this methodology's discipline (three-set splits, SHA-pinned reproducibility).
- Against that, the ADR's own designated tracking artifact (`docs/PROGRESS.md`) going stale for two months while the project's actual tracking migrated elsewhere (`docs/assessment/`, `docs/adr-audit/`) is itself fitness evidence — for the *artifact*, not the mechanism: MV-verification-evidence.md independently notes a parallel pattern ("the gap registers this layer ought to feed are dead... `docs/analysis/` is a chronological archive of ~130 documents with no aggregator"), suggesting this is a project-wide pattern of tracking documents being organically abandoned in favor of newer ones rather than a defect specific to this ADR.

**Fitness axis:** the mechanism (lane contract, SHA-pinning, lane-shape registry) has cited, load-bearing evidence in `MV-verification-evidence.md` and `CLAIMS.md`; the specific progress-tracking artifact and the universal-coverage mandate do not — recorded above as "no evidence found" for those two sub-claims specifically.

## 9. Findings raised

- 🟡 **AA-B3-1** — `evals/` lane-shape coverage has drifted to a minority: only 60/129 (47%) top-level directories carry the ADR-0016-mandated `contract.md`, and no mechanical gate enforces "must follow convention or it does not merge." §2, §3, §5.
- 🟢 **AA-B3-2** — `docs/PROGRESS.md`, the ADR's own mandated progress-tracking artifact, has had no narrative update since 2026-05-26 while the project advanced through 100+ further ADRs and stood up parallel tracking systems (`docs/assessment/`, `docs/adr-audit/`) without a recorded handoff. §5, §8.
- 🔵 **AA-B3-3** — `evals/` has organically split into two populations (60 canonical lanes vs. 69 ad hoc research/demo/probe directories); recommend a small ADR amendment ratifying the split explicitly rather than continuing to measure the second population as drift against a mandate it was never going to satisfy. §5, §7.

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0016-capability-roadmap.md` (full read)
- `docs/eval_methodology.md` (full read)
- `docs/plans/capability_roadmap.md` (header read; git history for the move)
- `docs/PROGRESS.md` (phase-header scan, Phase 0/5/6 sections and tail read in full; git log)
- `evals/framework.py` (docstring + shape-defining methods read)
- `evals/CLAIMS.md` (partial read — thesis mapping and Tier 2 table)
- Direct filesystem measurement: 129 top-level `evals/` dirs, 60 with `contract.md`, sampled dir contents for `comprehension/`, `conversation/`, `articulation/`, `analogical_transfer/`, `capability_index/`, `lab/`, `logos/`, `audit_tour/`, `gsm8k_parser_dev/`
- `docs/assessment/10-layer-cards/MV-verification-evidence.md` (full read)
- `docs/adr-audit/01-adr-census.md`, `02-stack-taxonomy.md` (zone/row confirmation)
- `git log --oneline --follow` for `docs/capability_roadmap.md` / `docs/PROGRESS.md` / `docs/plans/capability_roadmap.md`

---

# ADR-0020 — Phase 5 / Rust Parity Sequencing

**Audit ID (if a numbering collision):** — | **Family (if phased):** —
**Zone / stack:** B3 — Roadmap & Rust Parity (per `02-stack-taxonomy.md`) | **Tier:** B
**ADR status (as recorded in the file):** Accepted (2026-05-16) | **ADR date:** 2026-05-16
**Card author:** ADR Audit — Tier B (B3) | **`verified_at` SHA:** `cbfc8ccb`

---

## 1. Content summary

- **Decision made:** Option C — open Phase 5 (Curriculum Era) on the Python runtime immediately, and in parallel open a Rust-parity track that ports one backend surface at a time, gated by bit-identity tests, without making Rust the default (`CORE_BACKEND=rust` stays explicit opt-in). Sequencing: `vault_recall` first, `geometric_product`/`versor_apply` second, `cga_inner` third; propagation/teaching/trace-hashing deferred until Phase 5 evidence demands them.
- **Alternatives explicitly rejected:** Option A (Phase 5 first, defer Rust entirely) and Option B (Rust parity fully first, then Phase 5) — both named and argued against in the ADR body.
- **Artifacts the ADR claims will exist:**
  - Per-surface bit-identity gates for `vault_recall`, `geometric_product`, `versor_apply`, `versor_condition`, `cga_inner`
  - `CORE_BACKEND=rust` dispatch, default-off, Python as deterministic default
  - A follow-on ADR documenting the Rust parity contract per-surface (test discipline, parity gate, default-off enablement, replay-determinism preservation)
  - `docs/PROGRESS.md` opening Phase 5 with "Status: IN PROGRESS" the same date

## 2. Implementation cross-reference

| Claimed artifact | Found? | File:line | Notes |
|---|---|---|---|
| `vault_recall` Rust port + gate | yes | `core-rs/src/vault.rs`; `algebra/backend.py:156-222`; `tests/test_vault_recall_rust_parity.py` | Rayon parallel scan present, dispatch wired |
| `geometric_product` Rust port + gate | yes | `core-rs/src/cl41.rs`; `algebra/backend.py:83-109`; `tests/test_geometric_product_rust_parity.py` | f32 and f64 kernels both present |
| `versor_apply` Rust port + gate | yes | `core-rs/src/versor.rs`; `algebra/backend.py:112-132`; `tests/test_versor_apply_rust_parity.py` | `versor_apply_closed_f64` / PyO3 `versor_apply_with_closure_f64` present, matching the ADR's own "landed" note |
| `cga_inner` Rust port + gate | yes | `core-rs/src/cga.rs`; `algebra/backend.py:146-153`; `tests/test_cga_inner_rust_parity.py` | f32-only dispatch gate |
| `versor_condition` Rust port + gate | yes | `algebra/backend.py:135-143`; `tests/test_versor_condition_rust_parity.py` | f32-only dispatch gate |
| `CORE_BACKEND=rust` opt-in / Python default | yes | `algebra/backend.py:16-23` | `_ALLOW_RUST` requires `CORE_BACKEND` in `{rust, core_rs, rs}`; confirmed opt-in |
| Follow-on per-surface Rust-parity-contract ADR | yes (broadened) | `docs/adr/ADR-0196-native-substrate-language-doctrine.md` (2026-05-31) | Fulfills the letter (a later ADR governs the Rust/native-substrate contract) but as a broader three-ring, three-language doctrine rather than the narrower "per-surface parity contract" the Consequences section described |
| Bit-identity gate actually verifiable in this environment | no | — | `python3 -c "import core_rs"` → `ModuleNotFoundError`; all five parity tests are `pytest.mark.skipif(not HAS_RUST, ...)` and currently skip rather than run |
| Ported kernels reached by the runtime hot path | mostly no | `docs/research/rust-parity-measurement-2026-07-26.md` | Instrumented count: **one** Rust kernel call per full turn (`versor_apply_with_closure_f64`); the ~73%-of-turn-time `cga_inner`/`geometric_product` traffic (≈34k calls/turn) bypasses `algebra.backend` via 69 direct-import call sites vs. 24 dispatch-routed ones |

**Build axis:** full for the five named per-surface ports (all exist, are PyO3-bound, and are wired into `algebra/backend.py` exactly as sequenced) — but the parity gate is currently unverifiable in this repo's own environment, and the runtime benefit the ADR's Option-C rationale rested on does not reach the code paths it was meant to accelerate. Build is scored on artifact presence; the rationale gap is scored under Fitness/Necessity below.

## 3. Liveness / integration

- `CORE_BACKEND=rust` is off by default in every serving configuration (`algebra/backend.py:16-23`; confirmed independently by `docs/RUST.md`: "activation is opt-in: importable is NOT active"). Default-configuration serving takes the Python path unconditionally.
- Even under explicit `CORE_BACKEND=rust`, `docs/research/rust-parity-measurement-2026-07-26.md`'s instrumented run found exactly **one** Rust kernel invocation per full `CognitiveTurnPipeline.run()` turn (`versor_apply_with_closure_f64`). The measured hot path — `cga_inner` → `geometric_product`, ~34,000 calls/turn, ~73% of turn time per `docs/assessment/10-layer-cards/M0-substrate.md` — is called through 69 call sites that import `algebra.cga`/`algebra.cl41` directly, bypassing `algebra.backend`'s dispatch entirely; only 24 call sites anywhere in the tree go through the dispatch.
- Both parity test files and `core-rs` itself are absent from this environment (`ModuleNotFoundError: No module named 'core_rs'`); the "algebra" suite's five Rust-parity tests are `skipif`-guarded and currently skip silently rather than assert anything.
- **Sabotage test:** deleting `core-rs/` entirely today would change nothing observable in default-configuration serving (Rust is off by default). Under explicit `CORE_BACKEND=rust`, it would change exactly one function call per turn. The measurement doc performed a stronger version of this test directly — it sabotaged every `core_rs` callable to raise on every call, re-ran the lane-hash verifier under `CORE_BACKEND=rust`, and still got "11/11 lanes match, parity holds" — because every dispatch arm in `algebra/backend.py` swallows all exceptions (`except (AttributeError, TypeError, ValueError, Exception): pass`) and falls back to Python silently. A parity check that cannot fail is not verifying the thing it claims to verify.
- **Liveness axis:** wired-but-unreached — the mechanism is built, correctly opt-in-gated, and passes its own narrow tests when built and enabled, but is off by default, absent from this environment, not part of any CI suite that actually exercises it, and — even when active — reaches only one call site per turn rather than the hot path the ADR's cost argument for doing this in parallel with Phase 5 depended on.

## 4. Design fidelity — pillars and axioms

| Pillar | Honors / Tension / Violates | Citation (ADR clause + pillar text) |
|---|---|---|
| I. Mechanical Sympathy | Honors | "Rayon gives `vault_recall` true multithreaded parallelism" / stack-allocated hot loop, zero-copy numpy buffers (`docs/RUST.md`) — directly matches Pillar I's "software must understand the machine it runs on," and Whitepaper §X cites these same Rust kernels by name. |
| II. Semantic Rigor | Honors | "Any divergence is a test failure, not a feature request" (Consequences) — bit-identity, not approximate equivalence, is exactly Pillar II's "no thresholds tuned for good enough." |
| III. Third Door | Honors | The ADR explicitly names and rejects Option A and Option B, then constructs Option C (parallel, bit-identity-gated, default-off) as a genuine third position rather than a compromise between the first two — a clean instance of the pillar by the ADR's own structure. |

| Axiom | Honors / Tension / Violates | Citation |
|---|---|---|
| 1. Geometry-First | n/a | This ADR sequences *when* to port, not the geometry itself (owned by ADR-0245/Yellowpaper). |
| 2. Field-State | n/a | — |
| 3. Propagation-over-Mutation | n/a | Explicitly deferred ("propagation... port only if Phase 5 evidence demands it"); not decided here either way. |
| 4. Dual-Correction | Honors (weak) | The bit-identity gate structure — every accelerated (Rust) forward path must reproduce its canonical (Python) reference exactly, divergence treated as a defect — is a systems-level analog of "every forward operator should have a corrective/conjugate counterpart," even though the axiom is stated for geometric operators specifically. |
| 5. Reconstruction-over-Storage | n/a | — |
| 6. Compilation-Last | Honors | Whitepaper axiom 6 text names this exact mechanism: "The algebra was defined first. The Rust kernels... were written to serve it." ADR-0020's own premise — "Add Rust backend parity only after Python semantics are locked by tests" — is this axiom applied to backend/language choice. |
| 7. Reality-over-Inheritance | n/a | No prior abstraction is being defended or discarded by this decision. |

## 5. Build fidelity — does the code match the decision?

**Matches:** the concrete per-surface sequencing in the Recommendation section was followed exactly — `vault_recall` first, `geometric_product`/`versor_apply` second, `cga_inner` third — and the ADR's own "Parity status (live)" table plus `docs/PROGRESS.md`'s Phase 5 parallel-track checklist both record all five surfaces landing 2026-05-16, matching the decision to the day.

**Divergence:**
1. **The rationale for doing this *in parallel with* Phase 5 (rather than deferring, i.e. Option A) has not been vindicated.** The measured hot path (`cga_inner`/`geometric_product` at ~73% of turn time) bypasses the dispatch layer via 69 direct-import call sites; only the ported `versor_apply` closure sees Rust today, at one call per turn. The "Phase 5 runs on a faster substrate" premise that justified Option C over Option A does not currently hold.
2. **The promised follow-on ADR arrived nine days later as ADR-0196, but broader than described.** The Consequences section promised "a new ADR... to document the Rust parity contract per-surface (test discipline, parity gate, default-off enablement, replay determinism preservation)." ADR-0196 does re-ratify exactly those terms for `core-rs` but folds them into a three-ring, three-language (Python/Rust/Zig) doctrine rather than the narrower per-surface contract described — a reasonable broadening, not a contradiction, but not a literal fulfillment either.
3. **Parity verification is currently blocked/stale in practice.** `docs/assessment/10-layer-cards/M0-substrate.md` records that the 2026-07-25 verification attempt failed because `cargo` could not reach `static.crates.io` under sandbox network policy, and this audit's own environment has no `core_rs` build at all. The bit-identity guarantee the ADR's safety case depends on ("any divergence is a test failure") is currently unverified, not merely opt-in-and-untaken.

**Build-fidelity axis:** partial drift — the per-surface artifacts match the decision precisely; the decision's own stated rationale for the parallel-track choice does not hold under the project's own later measurement.

## 6. Continuity — Whitepaper, Yellowpaper, prior/later ADRs

- Contradicts `Whitepaper.md`? No direct contradiction. Whitepaper §X ("Mechanical Sympathy: Hardware-Bound Intelligence") and axiom 6 both cite the Rust kernels approvingly, consistent with this ADR. One adjacent tension worth flagging (not this ADR's own contradiction): Whitepaper §X also asserts "MLX tensor operations execute on the Neural Engine" as already-true, while `docs/RUST.md` and ADR-0235 describe MLX as "exploratory... not required for serving" — a Whitepaper-vs.-ADR-0235 overstatement that belongs on ADR-0235's card, noted here only because this card's evidence trail crossed it.
- Contradicts `Yellowpaper.md`? None found on the sections reviewed.
- Contradicts, silently overlaps, or is superseded by another ADR? Cleanly extended: **ADR-0196** (2026-05-31) explicitly re-ratifies this ADR's terms ("Rust (`core-rs`) remains the incumbent native algebra backend... already parity-gated and opt-in via `CORE_BACKEND=rust`") and layers a G0–G8 adoption-gate ladder for a candidate fourth-ring material (Zig) on top, without altering this ADR's terms. **ADR-0235** (Apple Silicon UMA acceleration) extends the hardware-acceleration story into an explicitly exploratory MLX lane. **ADR-0245** (CGA unification) is the algebra-layer decision this backend serves. Depends cleanly on **ADR-0016** (Phase sequencing) and **ADR-0019** (vault-recall vectorization, the Stage 1 semantics-lock that unblocked this track, per this ADR's own Context section).
- **Continuity axis:** clean.

## 7. Necessity / generality

1. **Necessity:** measured **not** necessary at current scale. `docs/assessment/31-hindrance-audit.md`'s own verdict: "Pure-Python-by-default algebra — measured as the correct posture: determinism is the product, `versor_condition` is 0.22% of turn time, and the urgency argument for Rust-by-default dissolved under measurement." The Rust track is real, correctly gated, and safe (default-off, exception-swallowing fallback keeps it harmless even if broken) — but the capacity argument that justified building it *in parallel with* Phase 5, rather than deferring per Option A, has not been borne out by the project's own later measurement.
2. **Reducibility:** not reducible to an existing L0/L1 algebra/field operator — this is a backend/acceleration choice for operators that already exist in Python, not a duplicate of a geometric primitive. The *dispatch pattern* itself (`algebra/backend.py`: try-Rust-fall-back-to-Python-silently) is a thin, already-general "pick the fastest available implementation of the same closed operator" shape.
3. **Extensibility:** strong generalization-candidate. ADR-0196 already reuses this exact dispatch pattern as the template for a prospective Zig lane (Ring 1). But `docs/research/rust-parity-measurement-2026-07-26.md`'s finding — that the silent exception-swallow makes lane-hash-based parity checks unfalsifiable (sabotaging every `core_rs` callable still reports "parity holds") — means the pattern needs a hardening amendment (fail-loud mode, a "Rust call count > 0" parity assertion, both recommended in that document) before it is safe to extend to a second native backend. ADR-0196's own G3/G4 gates (parity proof, determinism proof) are aimed at exactly this gap.

**Necessity/generality axis:** generalization-candidate — the opt-in, bit-identity-gated dispatch pattern is sound and worth keeping and reusing (ADR-0196 already extends it toward Zig), but the specific urgency case this ADR made for running it in parallel with Phase 5 did not hold, and the hot path it targeted still does not reach it.

## 8. Fitness / value

- `docs/assessment/10-layer-cards/M0-substrate.md`: "`CORE_BACKEND=rust` is off by default and nobody currently knows whether parity holds... it means a written-and-shipped Rust kernel sits unused and unverified" — direct, cited fitness evidence against the broad "Phase 5 runs on a faster substrate" claim.
- `docs/assessment/31-hindrance-audit.md`: "the urgency argument for Rust-by-default dissolved under measurement" (0.22% of turn time for the one invariant check that *is* Rust-eligible today) — negative fitness evidence, directly on point.
- `docs/research/rust-parity-measurement-2026-07-26.md` is the most direct fitness evidence available: `cargo test` genuinely passes (43/43), and the one dispatched f64 path a turn actually takes is bit-identical — real, narrow evidence the port itself is correct. But the document's own conclusion is that the broader "parity holds, therefore Rust is a viable/beneficial default" claim "rests on a measurement that cannot fail" as currently constructed, and the ~73%-of-turn-time hot path the ADR's Option-C rationale was implicitly about accelerating does not route through the dispatch at all.
- `docs/benchmarks/apple-uma-rust-baseline.md` exists but was not read in depth for this card; flagged as an unconsulted source rather than folded into the verdict above.

**Fitness axis:** narrow claim ("the five ported kernels are bit-identical to their Python references, where they are actually invoked") — supported, cite `docs/research/rust-parity-measurement-2026-07-26.md` §1–2. Broad claim implicit in the ADR's Option-C choice ("doing this in parallel accelerates Phase 5's actual workload") — no supporting evidence found; the evidence found (M0-substrate.md, hindrance audit, the measurement doc itself) points the other way.

## 9. Findings raised

- 🟡 **AA-B3-4** — The Rust dispatch layer (`algebra/backend.py`) is bypassed by the runtime's actual hot path: 69 of 93 relevant call sites import `geometric_product`/`cga_inner`/`versor_condition` directly from `algebra.cga`/`algebra.cl41` rather than through the `CORE_BACKEND`-aware dispatch, so `CORE_BACKEND=rust` reaches exactly one call per turn regardless of the flag — the ADR's rationale for running the Rust track in parallel with (rather than after) Phase 5 does not hold under measurement. Partially surfaced as an open question in `M0-substrate.md` but not yet carrying a gap-register number. §3, §5, §8.
- 🟡 **AA-B3-5** — Every Rust dispatch arm in `algebra/backend.py` swallows all exceptions, which makes lane-hash-based parity verification unfalsifiable: sabotaging every `core_rs` callable to raise still produces "11/11 lanes match" (`docs/research/rust-parity-measurement-2026-07-26.md` §2). §3, §5.
- 🟢 **AA-B3-6** — `core_rs` is not built/importable in this repo's own environment, and the project's own 2026-07-25 verification attempt was blocked by sandbox network policy — the bit-identity guarantee this ADR's safety case rests on is currently unverified in practice, a known and explicitly-recorded blocker rather than a silent gap. §2, §3.
- 🔵 **AA-B3-7** — The opt-in, bit-identity-gated, silent-fallback dispatch pattern in `algebra/backend.py` is sound and already being generalized by ADR-0196 as the Ring-1 template for a prospective Zig lane; recommend hardening it (fail-loud mode + a nonzero-Rust-call-count parity assertion, both recommended directly in `docs/research/rust-parity-measurement-2026-07-26.md` §3) before extending it to a second native backend. §7.

## 10. Evidence sources actually consulted

- `docs/adr/ADR-0020-phase5-rust-parity-sequencing.md` (full read)
- `docs/adr/ADR-0196-native-substrate-language-doctrine.md` (partial read — Decision, Ring architecture, adoption gates)
- `algebra/backend.py` (full read)
- `core-rs/Cargo.toml` (full read); `core-rs/src/lib.rs` (grepped for PyO3 surface); full `.rs` file inventory (14 files, 2,051 lines total)
- `docs/RUST.md` (full read)
- `docs/research/rust-parity-measurement-2026-07-26.md` (full read)
- `docs/assessment/10-layer-cards/M0-substrate.md` (full read)
- `docs/assessment/31-hindrance-audit.md` (grepped; relevant excerpt read in full)
- `docs/assessment/30-gap-register.md` (grepped for Rust-tagged entries)
- `docs/PROGRESS.md` Phase 5 / parallel-track section (read)
- `core/cli_test.py` "algebra" suite listing (read, lines 324-340)
- `tests/test_rust_backend.py` (partial read — `skip_no_rust` guard confirmed)
- Direct execution: `python3 -c "import core_rs"` → `ModuleNotFoundError` (confirmed absent in this environment)
- `docs/Whitepaper.md` §X and axiom 6 (grepped, relevant passages read)
- `docs/adr-audit/01-adr-census.md`, `02-stack-taxonomy.md` (zone/row confirmation)

---

## Zone findings — B3 rollup

- 🟡 **AA-B3-1** — `evals/` lane-shape coverage has drifted to a minority (60/129 top-level dirs carry `contract.md`); no mechanical merge gate enforces ADR-0016's "must follow convention" clause. *(ADR-0016)*
- 🟢 **AA-B3-2** — `docs/PROGRESS.md`, ADR-0016's mandated progress-tracking artifact, has been narratively stale since 2026-05-26 while tracking migrated to `docs/assessment/`/`docs/adr-audit/` without a recorded handoff. *(ADR-0016)*
- 🔵 **AA-B3-3** — `evals/`'s organic split into canonical lanes vs. ad hoc tooling is a generalization-candidate for a small ADR-0016 amendment rather than continued drift-scoring. *(ADR-0016)*
- 🟡 **AA-B3-4** — The Rust dispatch layer is bypassed by the actual runtime hot path (69 direct-import call sites vs. 24 dispatch-routed); `CORE_BACKEND=rust` reaches one call per turn regardless of the flag, undermining the parallel-with-Phase-5 rationale. *(ADR-0020)*
- 🟡 **AA-B3-5** — Blanket exception-swallowing in every Rust dispatch arm makes lane-hash parity verification unfalsifiable. *(ADR-0020)*
- 🟢 **AA-B3-6** — `core_rs` is unbuilt/unverifiable in the current environment; the project's own last verification attempt was network-blocked, an acknowledged rather than silent gap. *(ADR-0020)*
- 🔵 **AA-B3-7** — The opt-in bit-identity dispatch pattern is sound and already being generalized (ADR-0196, toward Zig); harden before reuse (fail-loud mode + nonzero-call-count assertion). *(ADR-0020)*

**Zone-level pattern:** both ADRs' named artifacts were built faithfully and narrowly; both ADRs' broader operating claims (a universal eval-lane mandate; a parallel Rust track that accelerates Phase 5) have been overtaken by the codebase's growth and, in ADR-0020's case, directly refuted by the project's own later measurement work. Neither is a "ghost" or "dead" mechanism — both are real, running, and safe — but neither card supports treating either ADR's Consequences section as a current description of the system without the corrections above.
