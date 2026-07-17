# ADR-0243 Phase 3 — Lane Brief Pack

**Status**: ready for dispatch (Shay's call — see [[feedback-no-self-dispatch-of-subagents]])
**Plan of record**: `docs/plans/adr-0243-implementation-plan.md` §5 Phase 3
**Phase 2 status at time of writing**: pushed, unmerged. Branch `feat/adr-0243-phase2-lifecycle`
@ `c3b4d045`, stacked on `feat/adr-0243-phase0-governance` @ `904380e9`, on top of
`forgejo/main` @ `19819194`. Compare URL:
`https://core-gitquarters.acbcontent.org/core-labs/core/compare/main...feat/adr-0243-phase2-lifecycle`

Each lane's research below was run fresh against the worktree on 2026-07-17 (three
read-only Explore passes, not assumed from the plan text) — one correction to the
plan doc's substrate table came out of it and has already been applied (§2.3 readback
rules row; `packs/en/readback_rules.py` doesn't exist, it was deleted under audit
ratchet W-006).

## Dependency DAG — corrected from the plan's "all wait on Phase 2" framing

The plan text implies all three lanes start "after Phase 2 API lands." That's only
true for one of them:

- **Lane A** (discovery wiring) and **Lane C** (biography wiring) touch zero Phase-2
  code — every symbol they wire is already on `forgejo/main` today (`core/physics/surprise.py`,
  `core/physics/multi_scale_energy.py`, `core/physics/goldtether.py`,
  `core/contemplation/runner.py`, `teaching/discovery.py`, `evals/analogical_transfer/harness.py`,
  `core/physics/biography.py` all predate this arc). **They can branch off
  `forgejo/main` right now, in parallel with Phase 2's own review.**
- **Lane B** (sensorium corridor eval) is the only lane that imports
  `core.physics.cognitive_lifecycle` (`CognitiveLifecycleEngine`, `ingest_context`,
  `egress_gate`). It must branch off `feat/adr-0243-phase2-lifecycle` (or wait for
  Phase 2 to merge and branch off `forgejo/main` at that point).

```
Wave 1 (parallel, off forgejo/main now):        Wave 1b (off feat/adr-0243-phase2-lifecycle):
  Lane A — discovery wiring                        Lane B — sensorium corridor eval
  Lane C — biography wiring                        (rebase onto forgejo/main once Phase 2 merges)
```

All three are independent PRs — no lane blocks another.

## Bundling options

- **Max parallelism (3 PRs, recommended):** one operator per lane, dispatched as below.
- **Substrate-first (2 PRs):** bundle A+C (both off main today, both "wire an existing
  pinned primitive into a live call site") into one PR; B stays separate since it has
  the Phase-2 dependency and is the larger deliverable (new eval package).
- **All-in-one (1 PR):** only if Phase 2 merges first and you want one operator to do
  all three sequentially — loses the parallelism that's the whole point of splitting
  these out.

## Must-read memories (every operator, before touching code)

[[feedback-start-in-worktree-off-main]], [[feedback-parallel-agent-worktrees]],
[[feedback-no-self-dispatch-of-subagents]], [[feedback-core-main-diverges-from-forgejo-truth]]
(base/diff against `forgejo/main`, never local main), [[feedback-smoke-gate-not-full-suite]]
(run this lane's own tests locally on the rebased base before flagging ready),
[[feedback-cleanup-as-you-find]], [[feedback-adr-cross-reference-discipline]] (grep ALL
ADRs + code for existing mechanisms before adding anything that looks new — this pack's
whole point is that most of the "new" wiring in Lanes A/C is one missing call, not new
architecture).

---

## Brief A — Discovery wiring (surprise → contemplation → DiscoveryCandidate)

**Base**: `forgejo/main` @ `19819194`. **Branch**: `feat/adr-0243-phase3-lane-a-discovery`.
**Worktree**: `git worktree add ../core-adr0243-lane-a feat/adr-0243-phase3-lane-a-discovery`
(create the branch first off `forgejo/main`, then add the worktree).

### Outcome

`core/contemplation/runner.py`'s finding-processing path calls
`is_discovery_eligible` (`core/physics/surprise.py:206`) and, when eligible,
`cross_band_discovery_gate` (`core/physics/multi_scale_energy.py:276`) to decide
whether to construct and emit a `DiscoveryCandidate` (`teaching/discovery.py:149`)
through the existing `DiscoveryCandidateSink` protocol (`teaching/discovery_sink.py:29`,
one method: `emit(self, line: str) -> None`). Separately, wire a live caller of
`propose_kappa_line_search` (`core/physics/goldtether.py:567`) so its internal
`kappa_search_event` call (line 604) actually fires — confined to a
calibration/training-loop call site, never a hot/serve path (R-04:
`docs/analysis/core_cohesion_master_plan.md:337`, "trace generation... limited strictly
to the calibration and training-loop pipelines").

### Open question — resolve before writing code, don't guess

`is_discovery_eligible` requires `surprise_norm: float` and
`productive_or_transfer: bool`. Neither is obviously present on whatever finding type
`core/contemplation/runner.py` processes today (`_emit_findings`, `runner.py:32-51`).
Read the actual finding dataclass(es) the runner consumes before wiring anything — if
no surprise score is computed at this point in the pipeline, that's a real gap to
report back, not something to fabricate a plausible-looking number for.

### Hard requirements

1. Do not change `is_discovery_eligible` or `cross_band_discovery_gate`'s signatures —
   both are ADR-0242 §5 pinned primitives with existing tests
   (`tests/test_adr_0242_carry_seams.py`).
2. Construct `DiscoveryCandidate` through the existing dataclass
   (`teaching/discovery.py:149`) — no parallel candidate type.
3. `kappa_search_event` stays calibration/training-loop only (R-04) — if you can't find
   an existing calibration entry point to hang the caller off, say so rather than
   inventing a new hot-path call site.
4. Emitting a `DiscoveryCandidate` is proposal-plumbing, not a vault write — the only
   side effect should be `sink.emit(...)` (JSONL append via `DiscoveryMonthlyFileSink`
   or in-memory `DiscoveryBufferSink`).
5. No changes to `core/physics/cognitive_lifecycle.py` — this lane is orthogonal to
   Phase 2.

### Tests

- Must stay green: `tests/test_adr_0242_carry_seams.py`
- New: a high-surprise contemplation finding produces a `DiscoveryCandidate` on the
  sink; a low-surprise one does not.
- New: `propose_kappa_line_search`'s live caller fires `kappa_search_event` only from
  the calibration path.

### Forbidden actions

Touching `chat/runtime.py`'s serve path. Building a new always-on scheduler (out of
scope for this lane — flag it if you think the wiring needs one, don't build it).

### Deliverables

Runner wiring change (likely `core/contemplation/runner.py`), the live
`propose_kappa_line_search` caller, new test file(s).

### Operator profile

Real open design question (surprise-signal sourcing) — strong-reasoning tier suggested.

---

## Brief B — Sensorium corridor eval (first live I-04 consumer)

**Base**: `feat/adr-0243-phase2-lifecycle` @ `c3b4d045` (rebase onto `forgejo/main`
once Phase 2 merges). **Branch**: `feat/adr-0243-phase3-lane-b-corridor`.
**Worktree**: `git worktree add ../core-adr0243-lane-b feat/adr-0243-phase3-lane-b-corridor`.

### Outcome

New eval package `evals/adr_0243_cognitive_lifecycle/`, shaped like
`evals/adr_0242_v2_energy_compare/` (thin `__init__.py` with a
`run_fixed_replay(...) -> dict` entry point delegating to one pure artifact function;
`__main__.py` CLI dumping sorted-key JSON — no fixture files, deterministic
parametrized inputs). The corridor it exercises:

```
AudioCompiler.compile(...)          (sensorium/audio/compiler.py:117)
VisionCompiler.compile_tile(...)    (sensorium/vision/compiler.py:92)
        │  .versor
        ▼
packet_from_compilation_unit(modality_id, unit)   (core/physics/sensorium_wave_feed.py:151)
        ▼
CognitiveLifecycleEngine.solve(packets, domain_id, hamiltonian)  (ingress → relax → egress)
        ▼  (E3/E4 route: "readback_eligible")
generate/realizer.py:energy_modulated_surface(base_surface, energy_class)   (readback text)
        │
        └── separately, explicitly: GoldTetherMonitor.decide(...)  (core/physics/goldtether.py:451)
```

### Hard requirements

1. **OFF-SERVING.** Lives under `evals/` only. Never imported from `chat/runtime.py`.
   If this adds any new `core.physics` module (it shouldn't need to — it's
   composition, not a new organ), add it to `tests/test_serve_quarantine_transitive.py`'s
   `_BANNED` tuple and `tests/test_third_door_cohesion.py`'s `banned_roots`/`banned_substrings`.
2. Follow the `adr_0242_v2_energy_compare` shape — deterministic fixed-replay, one pure
   artifact function, no fixture files.
3. This is the first LIVE consumer of the I-04 feed
   (`docs/analysis/core_cohesion_master_plan.md:110`, non-stochastic multimodal
   resonance). The compilers and adapters already exist and are unit-tested
   (`tests/test_adr_0241_sensorium_wave_feed.py:230`) — do not re-implement them, import
   and compose.
4. Readback text goes through `generate/realizer.py:energy_modulated_surface` — **not**
   `packs/en/readback_rules.py` (deleted; plan doc §2 table corrected 2026-07-17).
5. `egress_gate` deliberately does not call `GoldTetherMonitor.decide` — it only
   reports the raw unitary residual it needs for its own routing. This lane calls
   `.decide(...)` explicitly as a separate step in the corridor.

### Tests

- Precedent for fixture inputs: `tests/test_adr_0241_sensorium_wave_feed.py:230`
  `test_real_audio_and_vision_compilers_feed_phase_correlate`.
- New: an end-to-end deterministic test exercising
  compiler → ingest → relax → egress → readback → GoldTether, asserting the whole
  chain composes without any layer silently repairing another's output.

### Forbidden actions

No cosine/ANN similarity anywhere in the corridor — I-04's own definition requires
algebraic phase correlation in Cl(4,1); cosine/ANN is explicitly what it rules out.
No vault writes — crystallization stays proposal-only, same as Phase 2.

### Deliverables

`evals/adr_0243_cognitive_lifecycle/__init__.py`, `evals/adr_0243_cognitive_lifecycle/__main__.py`,
new test file(s), quarantine-list additions if applicable.

### Operator profile

Mostly composition of already-tested organs — moderate tier should be sufficient, but
the GoldTether/readback ordering deserves care.

---

## Brief C — Biography wiring (ADR-0240 PASS → integrate_biography)

**Base**: `forgejo/main` @ `19819194`. **Branch**: `feat/adr-0243-phase3-lane-c-biography`.
**Worktree**: `git worktree add ../core-adr0243-lane-c feat/adr-0243-phase3-lane-c-biography`.

### Outcome

Wire the ADR-0240 validation harness's PASS signal —
`AnalogicalTransferReport.wrong == 0` / `.all_correct_or_refused`
(`evals/analogical_transfer/harness.py:59-61`), or per-case
`TransferResult.correct is True` (`reason="transfer_ok"`, harness.py:214-227) — into a
live call of `integrate_biography(trajectory, alpha=0.5)`
(`core/physics/biography.py:66-70`), which has zero production call sites today
(test-only). Add I-01 closure asserts at the call site (`blade.closure < _CLOSURE` and
`versor_condition(blade.blade) < _CLOSURE` — model on
`tests/test_third_door_cohesion.py:195-213`) and provenance recording.

**Note:** there is no literal `PASS` type/enum in the harness — that word in the plan
text is a paraphrase. The actual signal is `report.wrong == 0` (report-level) or
`TransferResult.correct` (case-level). Pick the granularity deliberately (report-level
gates a whole session's worth of transfers into one biography integration; case-level
would integrate per-transfer) and say which you chose and why.

### Open question — resolve before writing the mutation path, don't guess

Does wiring ADR-0240 PASS → `integrate_biography` count as a persisted
identity-substrate mutation, or a legitimate direct integration? `biography.py`'s own
docstring says biography holonomy is "reconstruction-over-storage... not a parallel
identity store," which reads differently from the Phase 2 module's proposal-only
crystallization discipline (D-5/I-03) — but that's a reading, not a ruling. Read
`docs/adr/ADR-0240-Analogical-Transfer-Validation-Harness-Biography-Holonomy.md` in
full. If it's genuinely ambiguous after that, this is an identity-substrate design
call — confirm with Shay before writing the mutation path rather than picking silently.

### Hard requirements

1. No existing biography-specific provenance helper exists (confirmed by grep across
   `core/physics/*.py` — `goldtether.py`, `self_authorship.py`, `holographic_vault.py`,
   `wave_manifold.py` all have zero provenance references). Model any new one on
   `self_authorship.py:20-36`'s `AuthorshipProposal` shape (`proposal_id, kind,
   epistemic_status, drift_residual, closure_proof, body, adr_refs`), or on
   `core/physics/identity.py:263`'s `TurnEvent` if you decide biography provenance is
   closer to a turn-scoped record. Document which you chose and why.
2. I-01 must hold at the call site itself, not just in the pre-existing unit test —
   assert `blade.closure` and `versor_condition(blade.blade)` against the same
   `_CLOSURE` threshold every time this wiring runs; fail closed (typed error) if not.
3. Do not change `integrate_biography`'s signature (`core/physics/biography.py:66-70`)
   — it's fully implemented and tested. This lane adds a caller, not a rewrite.
4. Do not change the ADR-0240 harness (`evals/analogical_transfer/harness.py`) —
   consume its output as-is.

### Tests

- Must stay green: `tests/test_adr_0240_biography_holonomy.py`,
  `tests/test_third_door_cohesion.py::test_i01_biography_holonomy_closed_and_modes_reloadable`
- New: an ADR-0240 harness PASS report drives a live `integrate_biography` call with
  I-01 asserts and a provenance record.
- New (must-reject): a harness report that is NOT all-correct-or-refused must not
  integrate.

### Forbidden actions

No direct vault/pack writes without going through whatever gating the ADR-0240 doc +
Shay's design-call answer requires. No relaxing `_CLOSURE` to make a borderline case
pass.

### Deliverables

Wiring module (location TBD by operator — likely `core/physics/`), the new provenance
helper, new test file(s).

### Operator profile

Genuine identity-substrate design ambiguity (see open question) — strong-reasoning
tier, and confirm the mutation-vs-proposal call with Shay before committing to it.

---

## Copy-paste dispatch lines

**Lane A:**
> Read `docs/handoff/ADR-0243-PHASE3-BRIEF-PACK.md` §Brief A. Worktree:
> `git worktree add ../core-adr0243-lane-a -b feat/adr-0243-phase3-lane-a-discovery forgejo/main`.
> Deliverable: contemplation-runner wiring for `is_discovery_eligible` +
> `cross_band_discovery_gate` → `DiscoveryCandidate`, plus a live
> `propose_kappa_line_search` caller. Run this lane's tests + the in-worktree smoke
> gate before flagging ready. Resolve the surprise-signal open question first.

**Lane B:**
> Read `docs/handoff/ADR-0243-PHASE3-BRIEF-PACK.md` §Brief B. Worktree:
> `git worktree add ../core-adr0243-lane-b -b feat/adr-0243-phase3-lane-b-corridor feat/adr-0243-phase2-lifecycle`.
> Deliverable: `evals/adr_0243_cognitive_lifecycle/` corridor eval (compiler → ingest →
> relax → egress → readback → GoldTether). Run this lane's tests + the in-worktree
> smoke gate before flagging ready.

**Lane C:**
> Read `docs/handoff/ADR-0243-PHASE3-BRIEF-PACK.md` §Brief C. Worktree:
> `git worktree add ../core-adr0243-lane-c -b feat/adr-0243-phase3-lane-c-biography forgejo/main`.
> Deliverable: ADR-0240 PASS → `integrate_biography` wiring with I-01 asserts and
> provenance recording. Resolve the mutation-vs-proposal open question with Shay
> before writing the mutation path. Run this lane's tests + the in-worktree smoke gate
> before flagging ready.
