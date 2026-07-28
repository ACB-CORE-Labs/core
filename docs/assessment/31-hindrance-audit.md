# The Hindrance Audit

**Assessor:** Fable 5 (Phase 4) · **Verified at:** `8927c563` (2026-07-27)
**Discipline:** A hindrance is something *present* that works against the goal — a wrong solution for its underlying problem, a responsibility lodged in the wrong owner, a trade-off tuned instead of dissolved, or a record that misleads the next reasoner. Every entry carries evidence, a fitness verdict from the schema vocabulary, a **proposed better home**, and its deciding authority. Per standing rule: settled rulings are constraints — an entry may flag a ratified decision only on evidence, only for ruling, never as a unilateral recommendation to reverse. **This audit decides nothing.**

Ranked by leverage (cognitive/structural load removed ÷ effort), per the AGENTS.md protocol — not by ease.

**Amended:** 2026-07-27 at `ed06dd64` (Opus 5, Phase 6). **H-12 added** (the two smoke gates have diverged). **H-8 gains a fourth instance**, located inside the source rather than the documents. **H-1 gains a note**: its exposure is already pinned. Derivations in [`50-execution-plan.md`](50-execution-plan.md) §0.

---

## H-1 · License evidence counted on an independence assumption replay violates
**Verdict:** `wrong-solution` (the *counting basis*, not the gating) · **Layers:** M5
**Evidence:** Wilson lower-bound licensing (θ_SERVE=0.99, ADR-0175 lineage) assumes independent trials; a replay of the same sealed case is one trial observed again, not a new one. Measured consequence recorded in the prior arc: **21 of 25 ratified bands fall short** of their floor when replays are deduplicated.
**Why it hinders:** the entire earned-license architecture — CORE's mechanism for *deserving* to serve — rests on the evidence count. An overstated count grants licenses the evidence doesn't support, which is precisely the failure the mechanism exists to prevent. The gate is right; the arithmetic feeding it is not.
**Better home:** distinct-evidence counting at the seal boundary (count distinct cases; a replay refreshes, never increments), declared in the ledger schema the way ADR-0263 Rule 5 declares absence policy — in the table, not the call site.
**Note (Phase 6):** the exposure is **already pinned in-repo**. `tests/test_volume_honesty.py` (ADR-0264 R9, in the local smoke gate) pins *"21 of 25 bands do not clear θ_SERVE on distinct evidence"* **in both directions**, measured 2026-07-25 at `6ada6f7a` with every band at 720 committed decisions, and its own comment calls the inventory *"an EXPOSURE INVENTORY, not an approved baseline."* The audit source is `docs/research/distinct-evidence-audit-2026-07-25.md`. The open work is therefore **applying** the shortfall, not discovering it — and that pin moves in the same PR.
**Authority:** ADR amendment (0175/0263 lineage) + a re-count of the 25 bands, authorized by R-13. The re-count may demote licenses; that is the mechanism working.

## H-2 · Decoration in the runtime constructor — objects built and never read
**Verdict:** decoration (fails the sabotage test) · **Layers:** M6/M3
**Evidence:** `DriveGradientMap` constructed at `chat/runtime.py:716`, read nowhere. `InhibitionMask`/`InhibitionOperator` exported by `core/physics/__init__.py`, constructed on no path. Deleting either changes no output.
**Why it hinders:** dead structure is not neutral — it is *testimony*. Both objects tell every reader that drive mapping and inhibition masking are live, and Phase 1 of this very assessment initially believed them. Decoration is how architecture lies without anyone lying.
**Better home:** deletion (mastery algorithm step 2: the best part is no part), with their *intents* preserved where they belong — drive in the CR-2 design (G-4), the mask's disposition in the CR-1 ADR (G-14). If a future mechanism needs them, re-adding a deleted class is cheap; un-believing a phantom is not.
**Authority:** mechanical PR + one line each in the CR-1/CR-2 decisions.

## H-3 · The typed refusal is constructed, then discarded at the public boundary
**Verdict:** `strained` — truth built and unserved · **Layers:** M4
**Evidence:** `InnerLoopExhaustion` carries reason, region, and per-step rejected-attempt evidence; `respond()`/`arespond()` convert it to `""` for the `str` contract, so a refusing turn serves the empty string with `refusal_reason == ""`. The plumbing to materialise (`CognitiveTurnResult.refusal_reason`, `compute_trace_hash` fold) already landed; `runtime_contracts.md` names it a residual awaiting a future ADR.
**Why it hinders:** the honesty machinery is the product. A system whose refusals are richer than its answers, serving its refusals as nothing, undersells its own thesis on every hard turn.
**Better home:** materialise into `ChatResponse.refusal_reason` (and a minimal honest surface), per the contract's own anticipation.
**Authority:** small ADR — the chain already reserved the seam.

## H-4 · Composer-arm precedence is ordered branches above a declarative resolver
**Verdict:** `strained` — a solved pattern not yet extended · **Layers:** M4
**Evidence:** `core/cognition/surface_resolution.py` (494 lines) resolves the pipeline seam by *declared* precedence, self-documenting, with an in-code falsifiable contract for its own regression. Upstream, the composer arms (deduction `:1834`, curriculum `:1850`, pack/narrative/example/relation `:1871–:1936`, determination, estimate, gate, hedge) remain ordered branches across `chat/runtime.py`, in a different package with a different owner — nothing structurally prevents arm N+1 from bypassing the resolver's disciplines.
**Why it hinders:** prospectively — each new serving capability adds an arm ahead of any declared order. With only deduction ON, the live complexity is modest; the time to dissolve the pattern is *before* the next three arms, not after.
**Better home:** extend the resolver's declared-precedence pattern upstream to arm selection — the Third Door here is half-built and proven to fit this codebase.
**Authority:** refactor ADR; low-risk while one arm is live.

## H-5 · Underived constants at the semantic center of generation
**Verdict:** `strained` — Pillar I violation with an in-repo counterexample · **Layers:** M3/CR-1
**Evidence:** `salience_top_k=16`, `inhibition_threshold=0.3` gate every token walk's candidate set; no recorded derivation exists for either. The contrast is instructive and in-repo: `admissibility_margin δ=0.4` was derived from the minimum observed margin of a characterization corpus (0.456), declared *falsifiable*, and survived a 20-case stratified attempt — the standard exists two config lines away.
**Why it hinders:** "thresholds tuned for good-enough" at the exact point where the system decides what it may consider. Also the self-narrowing budget feedback (`stream.py:637`) — a real cognitive property nobody has named or justified.
**Better home:** the CR-1 ADR (G-14) with an empirical derivation in the δ=0.4 style.
**Authority:** ADR + a small characterization run.

## H-6 · The half-forced flag pair gating the lived learning loop
**Verdict:** `misplaced` responsibility — a *set* decision made one flag at a time · **Layers:** M6/M5
**Evidence:** F-6 (`05-phase3-findings.md`): the daemon forces the consolidator, not the accruer; the loop's writer and its consumer are gated independently, and only the consumer is on.
**Why it hinders:** flags that must be coherent *as a set* are owned nowhere as a set. `CONTINUOUS_LIFE_CONFIG_FLAGS` is the right pattern (a named, documented flag *profile*) applied to the wrong subset.
**Better home:** the flag-default register (G-8) with named profiles (one-shot / eval / continuous-life), each profile ruled as a unit.
**Authority:** ruling on the accrual flag + the register PR.

## H-7 · The production ingest boundary lacks the trust contract its sibling has
**Verdict:** `strained` — the standard exists and stops one layer short · **Layers:** M2
**Evidence:** formation declares six boundaries — content-addressed in/out, no floats in hashed payloads, no pickle, an audit record per rejection. `ingest/gate.py`, facing untrusted user text in production, has the versor gate and the AGENTS.md trust-boundary defaults, but no comparable declared table.
**Why it hinders:** asymmetric rigor invites the assumption that the un-tabled boundary is the less important one; it is the opposite.
**Better home:** an M2 trust-boundary table in `runtime_contracts.md`, formation-style; hardening PRs only where the table exposes real deltas.
**Authority:** documentation first; evidence decides whether code follows.

## H-8 · The record contradicts the code at three load-bearing points
**Verdict:** `wrong-solution` as *record-keeping* — divergence that reasoners inherit · **Layers:** governance
**Evidence:** (a) ADR-0146 rejects the daemon shape and places *"cross-process file locking, daemon synchronization, and signal handling"* out of scope; `chat/always_on_daemon.py` ships all three (`fcntl.flock` single-instance lock, SIGINT/SIGTERM, load-time identity guard) and is unowned. (b) ADR-0252's headline "34 organs" has no reproducible basis (18 `resolve_promotable_*` entry organs at the ratification commit *and* at `ed06dd64`; ~32 modules). (c) `architecture-assessment-verification-2026-07-25.md` asserts accrual "is enabled by the production L10 process"; the flag set says otherwise. **(d) — added Phase 6, and it is inside the code.** `core/config.py`'s docstring for `accrue_realized_knowledge` states *"the production L10 process enables it alongside `persist_session_state`"*, and the docstring for `consolidate_determinations` states the same about *"`accrue_realized_knowledge` + `persist_session_state`"*. `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:45-49`) contains neither claim's subject: it forces `persist_session_state`, `consolidate_determinations`, `strict_identity_continuity`, and **not** `accrue_realized_knowledge`.
**Why it hinders:** demonstrated, not hypothetical — this assessment's own Phase 0 inherited a stale-record error, and the 2026-07-25 doc (itself a *corrective* document) introduced one. Every divergence is a future wrong analysis. Instance (d) is the sharpest: it is one layer *below* the documents, where a reader checking the code against the docs would stop and believe.
**Better home:** four amendments — ADR-0146 addendum owning the daemon (drafted in `50-rulings.md` R-12a); ADR-0252 basis footnote (drafted, R-12b); a correction note on the 07-25 doc; and the two docstrings corrected or the flag added, per R-3.
**Authority:** docs PRs + ruling signatures (R-12 for the two ratified ADRs, R-3 for the docstrings).

## H-9 · Dead instruments still standing as if live
**Verdict:** `superseded-in-place` (unratified) · **Layers:** MV/governance
**Evidence:** `docs/gaps.md` — 26/26 closed, no entry from any 2026-06+ arc; `substrate-liveness-ratchet` — v5, stale since ~2026-05-24, all OPEN items L10-chained; ~130 analysis docs with no aggregator. The system map — the best macro artifact — is local, gitignored, 48 days stale, and was wrong precisely where the project moved fastest; its phantom "L12" stratum exists nowhere else.
**Why it hinders:** an instrument that *looks* authoritative converts "I should check" into "I already checked." Phase 0's error was this mechanism operating on this assessment.
**Better home:** this register supersedes `docs/gaps.md` (marked historical); the ratchet's 7 OPEN items migrate here (G-5 absorbs their L10 dependency); the map stays a regeneratable local index per D5, with "L12" dropped; the assessment directory becomes the standing ruled record, `verified_at`-stamped.
**Authority:** ruling (one PR).

## H-10 · The demotion that mispriced the paradigm experiment
**Verdict:** `strained` framing — a correct ruling casting an incorrect shadow · **Layers:** M3/governance
**Evidence:** GSM8K was demoted to diagnostic (correct — the flags-and-benchmarks reasoning stands). The §5 SME experiment lives in GSM8K's neighborhood (`holdout_dev/v1`, math structures), so it inherited the demotion's priority — but its verdict governs the *comprehension paradigm for everything*, per ADR-0252's own §4 conformance bar.
**Why it hinders:** the highest-leverage open item in the project (G-1) has been priced as math-lane housekeeping.
**Better home:** none needed — G-1's execution *is* the fix; this entry exists so the mispricing mechanism is named and not repeated.
**Authority:** already covered by G-1's ruling.

## H-11 · A silent-failure pinhole inside a typed layer
**Verdict:** `strained` (small, cheap, principled) · **Layers:** M3
**Evidence:** `_accrue_in_turn`'s broad guard converts any exception in the read→realize→determine chain into a no-op accrual with no telemetry (F-10). Defensible as a backstop; invisible as a signal — in the one layer whose constitution is "failures are typed, never silent" (INV-34).
**Better home:** count the swallow (a telemetry field on `IdleTickResult`/turn accrual), not a behavior change.
**Authority:** mechanical PR.

## H-12 · The two smoke gates have diverged by ten files, and one comment says they cannot
**Verdict:** `strained` — a real asymmetry, *smaller* than it first looks · **Layers:** MV
**Evidence:** `TEST_SUITES["smoke"]` is **23** files; `.github/workflows/smoke.yml` is 8 path patterns expanding to **13**. The ten local-only files are `test_audit_ledger_r7`, `test_cli_runner_contract`, `test_pack_draft_serve_boundary`, `test_workbench_deduction_provenance`, `test_prior_surface_deduction_binding`, `test_negation_survives_articulation`, `test_adr_status_governance`, `test_adr_index`, `test_volume_honesty`, `test_curriculum_polarity`.
**State the counter-evidence first.** AGENTS.md §CI/CD is explicit that `.github/workflows/*.yml` are *"secondary observability only — never a substitute for local gates"*: the merge gate **is** the in-worktree run, and the in-worktree run is the **superset**. Eight of the ten files carry in-code comments saying they belong *"on the pre-push gate"* — which is exactly where they are. **Under doctrine, nothing is unguarded**, and any reading of this entry as "ten pins run nowhere" is wrong.
**Why it hinders, precisely:** (1) **two independent places assert the parity** — the audio block in `core/cli_test.py` says it is listed explicitly *"so the local-first pre-push gate (AGENTS.md protocol) **equals** the CI gate rather than silently narrowing it,"* accurate about the six audio files and false as the statement about the suite a reader will take it for; and `scripts/hooks/pre-push`, the *automation of the AGENTS.md protocol itself*, describes its own step 1 as *"the `smoke` suite — **exact CI-gate parity**"* while running 23 files against CI's 13. A claim made twice inside the enforcement tooling is the strongest available evidence that the drift was never intended; (2) the real exposure is the **push that skipped the local gate** — from a cloud session, another machine, or an agent — for which CI is the only automatic check, and for which ADR-0265's denial pin, both ADR-governance pins, volume honesty, and curriculum polarity currently run nowhere before merge. Six of these files were promoted *after* real silent-regression incidents (#136, #113, the 2026-07-20..24 register-axis drift), so the failure mode they exist to catch is demonstrated, not hypothetical.
**Better home:** the gate-parity pin in G-7 — the drift is only invisible because nothing measures it. Measured parity cost: **429 tests in 46s** on the Act runner's own hardware (`ubuntu-latest:host` = native macOS host).
**Authority:** R-14 sets the direction (raise CI, or lower local, or keep them different and correct the comment); the pin itself is mechanical.

---

## Explicitly examined and cleared

For symmetry with the Candidate Register's "considered and not registered" — hindrance candidates this audit *rejects*:

- **The 18 derivation organs** — condemned but *ruled* to keep serving (`superseded-in-place` by explicit ruling); their continued service is governance working, not failing. The hindrance was their unreproducible count (H-8b), not their existence.
- **Off-serve quarantines** (holographic vault, wave modules, `topological_reasoning`) — capacity that exists and cannot be used *by AST-pinned design*; legitimate research containment with failing-when-violated enforcement. An exit criterion would be nice (M1 card); the quarantine itself is fit.
- **Pure-Python-by-default algebra** — measured as the correct posture: determinism is the product, `versor_condition` is 0.22% of turn time, and the urgency argument for Rust-by-default dissolved under measurement. The open parity question (blocked on network) is a question, not a hindrance.
- **The five unreconciled articulations** — dissolved by the taxonomy (D1), not a standing hindrance; the residue is one stale Draft banner (folded into H-8's amendment batch).
- **Flag-gated conservatism itself** — seventeen dark flags is not inherently hindrance; *unregistered* darkness is (G-8). The posture may be exactly right; the register exists so that judgment can be made deliberately.
