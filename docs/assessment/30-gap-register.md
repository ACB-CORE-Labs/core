# The Gap Register

**Assessor:** Fable 5 (Phase 4) · **Verified at:** `8927c563` (2026-07-27)
**Standing:** This is CORE's first *live* gap register since `docs/gaps.md` closed its 26th entry. Proposal (for ruling): this register supersedes `docs/gaps.md`, which is marked historical; two dead registers plus a live one is worse than one live one.
**Discipline:** A gap is an *absence the telos requires filled* with no explicit deferral ruling. Deferred-with-ruling is not a gap (scripture content is the model). Every entry carries evidence, its **deciding authority**, and a leverage rank. The register decides nothing.

---

## Tier A — Frontier-blocking (each blocks a ratified commitment or the telos itself)

### G-1 · The ADR-0252 §5 experiment has never returned a verdict
**Layer:** M3 · **Leverage: 1 (highest in the assessment)**
The ratified governing paradigm's single load-bearing empirical claim — can Cl(4,1) geometry carry relational structure the SME way — sits authorized (§8.4), scaffolded (two unmerged `rnd/` worktrees, tip `bed29a09` "formalize §5 experiment scaffolding"), and unrun. Until it returns GO or NO-GO, the §6 comprehension correction cannot be authorized, and the 18 condemned organs serve indefinitely with no successor path. A well-controlled NO-GO is *defined by the ADR as full credit* — the experiment is cheap to finish and expensive to leave open. GSM8K's demotion to diagnostic mispriced this: the paradigm governs **all** future comprehension, not math.
**Evidence:** ADR-0252 §5/§8; worktree log; `M3` card. · **Authority:** execution (already authorized) + Shay's verdict ruling.

### G-2 · The #138 fabrications — *measured & pinned, fix held for ADR + ratification*
**Layer:** M3 (locus: `generate/meaning_graph/reader.py`) → blast radius M4 · **Leverage: 2**
`every dog is a mammal` → `member(every_dog, mammal)`; `Given: furthermore; p implies q; p.` → `asserted(furthermore)` recited back as a served premise. The reader fabricates on 22 constructions beyond its 19-wide verified inventory. The fixes are known — two of the 13 mutations — and are **deliberately held** because they change what CORE comprehends from user input: serving-path truth behavior, ADR + ratification territory. Entered here pre-labeled per standing instruction; never re-discovered, never fixed by this assessment.
**Evidence:** PR #138 @ `c69f9948`; `realize-phase` card (incl. the defensive-gate option: refuse to *hold* a reading outside the verified inventory). · **Authority:** the fabrication ADR + Shay's ratification.

### G-3 · Reader inventory: 19 constructions against a 1739-construction writer, overlap 6
**Layer:** M3 · **Leverage: 3**
The comprehension frontier itself, measured. Standing ruling: close fabrications (G-2) **before** widening. The widening program after that is the largest single capability gap between CORE and its telos — and its *shape* depends on G-1's verdict (structure-mapping vs more constructions).
**Evidence:** #138 inventory measurement; `M3` card capacity block. · **Authority:** sequenced rulings (G-2 → G-1 → widening plan).

### G-4 · CR-2 — the continuous life has no chooser
**Layer:** M6 / Candidate Register · **Leverage: 4**
Confirmed at component depth: drive objects exist (`DriveGradientMap` — constructed, never read; `ExertionMeter` — telemetry only); idle mechanisms exist (consolidation, proposal review, contemplation — each flag-gated, each doing one thing); **nothing ranks what matters next**. The daemon heartbeat advances `idle_tick` and nothing more ambitious. This is the AGI-grade conceptual absence: everything CORE does is chosen by the operator. Design work, not a flag flip.
**Evidence:** `attention-allocation` + `always-on-process` cards; `02-layer-taxonomy.md` CR-2. · **Authority:** design + ruling (does the L10 process own an agenda, governed by what).

### G-5 · L10 proof debt — the soak has never produced an artifact, and nothing runs its pins
**Layer:** M6 / MV · **Leverage: 5**
The always-on process is built; the falsifiable harness (H1–H4, holds/bites pairs, vacuity-guarded) is built; **no recorded long-horizon artifact exists, no suite contains any `l10`/`always_on` test, no nightly cadence exists** — and the local-first/Mac-runner doctrine makes "nightly" itself need a ruling rather than a cron line. The still-owed ADR-0146 Phase-4 spike, in its modern form: run the soak, record the artifact, schedule the pins.
**Evidence:** `M6` + `always-on-process` cards; suite-membership scan. · **Authority:** execution + MV suite ruling + cadence ruling.

### G-6 · F-6 — the lived learning loop is half-gated
**Layer:** M6/M5 · **Leverage: 6**
The daemon forces `consolidate_determinations` but not `accrue_realized_knowledge`; the only turn-path writer of realized facts sits behind the unforced flag. As coded, the continuous life may consolidate an empty set. Incomplete flag set, or intended dormancy — **neither is documented**, and a prior verification doc asserts the opposite of the code (C-5).
**Evidence:** `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:45-49`); `determine-phase` card gating table. · **Authority:** ruling (one flag + one sentence, or a documented dormancy rationale).

---

## Tier B — Enforcement & instrument debt (capability exists; the guarantee doesn't)

### G-7 · No orphaned-pin meta-check
**Layer:** MV · **Leverage: 7**
Suite tuples are hand-curated; a test file in zero suites is indistinguishable from one that runs everywhere. This is the *mechanism* by which G-5 happened. A meta-pin — every `tests/**/*.py` belongs to ≥1 suite or an explicit exclusion list — converts the doctrine "a pin in no suite never runs" into a failing test. Likely the highest-leverage *single mechanical change* in the repository.
**Evidence:** `MV` card; the M6 case as the demonstration. · **Authority:** mechanical (small PR); no ruling needed.

### G-8 · No flag-default register
**Layer:** cross-cut · **Leverage: 8**
Seventeen capability flags default `False`; one is ratified ON (`deduction_serving_enabled`); three are daemon-forced (`persist_session_state`, `consolidate_determinations`, `strict_identity_continuity`). No document states the set, which defaults are deliberate posture vs accumulated hesitancy, or what evidence would flip each. The largest lever in the system, unregistered. The register format already exists in-repo: the ratified-ledger pattern (declare absence policy in the table, not the call site — ADR-0263 Rule 5).
**Evidence:** `core/config.py` scan (Phase 2); daemon trio (Phase 3). · **Authority:** documentation PR + per-flag evidence bars set by ruling.

### G-9 · Enforcement pins unverified for three doctrine-level prohibitions
**Layer:** M1 / MG · **Leverage: 9**
(a) No verified failing pin for the no-approximate-recall law (would a cosine ranker actually fail a test?); (b) no pin that fails when a layer *bypasses* governance entirely (as distinct from governance working when called); (c) safety-pack non-swappability not verified as mechanically enforced. All three are law in `AGENTS.md`; law-enforced-by-review is weaker than law-enforced-by-test.
**Evidence:** `M1`/`MG` cards (flagged, not resolved, in Phase 2–3). · **Authority:** verification pass, then mechanical PRs.

### G-10 · Curriculum SERVE is fully blocked by one engineering item, and its ledger doesn't exist
**Layer:** M5 · **Leverage: 10**
ADR-0264 §4.1: the 16-premise compilation cap holds every band to ≤16 entailed cases, so **no curriculum band can earn SERVE until query-scoping lands** — an engineering blocker gating a content problem that is itself quantified at 24×–73× under-fed. Downstream, `chat/data/curriculum_serve_ledger.json` is absent (the one honest `missing_ok=True` in production), and a committed ledger is necessarily an *earning* one — the outcome-mix ruling remains the binding constraint.
**Evidence:** `M5` card; ADR-0264 §4.1; `chat/curriculum_serve_license.py:46`. · **Authority:** engineering (scoping) + outcome-mix ruling.

### G-11 · Identity enforcement has no stated authorization bar
**Layer:** MG · **Leverage: 11**
`identity_wave_gate` is off and "not authorized" — a deliberate posture. What's missing is the *criterion*: no document states what evidence would authorize live refusal. Scoring-without-blocking is an honest state only while the path to blocking is defined.
**Evidence:** `MG` card; `runtime_contracts.md` identity contract. · **Authority:** ruling (set the bar).

---

## Tier C — One-line rulings (cheap to close; expensive only if left silent)

### G-12 · CR-3 efferent action — deferred, or out of telos?
No system-level statement exists either way; the only adjacent text is one bench's v1 prohibition. The alignment posture is arguably *stronger* with action explicitly deferred — the ruling costs one line. **Authority:** ruling.

### G-13 · CR-4 temporal self-location — a stance before the L10 spike
Determinism bans clocks; continuity implies lived time; the 24h+ no-drift requirement cannot be stated precisely without a stance on "now." The spike (G-5) should not be designed with an accidental answer. **Authority:** ruling (can be a paragraph in the soak's contract).

### G-14 · CR-1 attention governance — the one-page ADR
Own `use_salience`, the two underived constants, the self-narrowing budget feedback, and the `InhibitionMask` disposition. Mechanism verified live and sound; only the governance is absent. **Authority:** ADR (one page — the card is its draft evidence base).

### G-15 · The daemon's ratifying ADR
`chat/always_on_daemon.py` is unowned while ADR-0146 explicitly rejected the daemon shape it implements. Whatever the right answer, the record currently contradicts the code (see H-8). **Authority:** ADR amendment or a new short ADR.

---

## Tier D — Latent & carried-forward (recorded so nothing silently drops)

- **G-16 · ADR-0265's defect class survives in `_inflect_predicate`'s aspect arms** (`generate/templates.py:79`) — 10,530/16,146 template points, *not reachable today*. Latent, recorded from the prior arc; becomes live if aspect arms become reachable. **Authority:** the widening program (G-3) must clear it first.
- **G-17 · Non-text ingest** — 59 sensorium modules, no serving path, no entry criterion; projection heads do not exist. Position paper is honest about this. Needs either an entry criterion or an explicit deferral ruling (the falsification bench is the standard the track should be held to when it moves). **Authority:** ruling.
- **G-18 · Identity-divergence curriculum may still bypass formation's gates** — known gap since 2026-05-17 (`teaching_order.md`); unverified at this SHA. **Authority:** Phase-3-style verification pass, then a routing PR.
- **G-19 · Wilson/replay evidence shortfall** — 21/25 ratified bands short if replays were counted as independent trials (see H-1 for the mechanism). Recorded here as *evidence debt on existing licenses*; the counting fix is the hindrance entry. **Authority:** ADR amendment + re-count.
- **G-20 · The `refusal_reason` materialisation** — typed refusal evidence exists and is discarded at the public `str` boundary; the plumbing for materialisation already landed. Cross-listed as H-3. **Authority:** small ADR (anticipated by the ADR-0024 chain).

---

## What is *not* in this register, and why

- **Scripture/theology content** — deferred by explicit ruling (2026-07-26); the model case for deferred-is-not-missing.
- **Benchmark wins** — excluded by the completeness criterion itself (taxonomy §6): architectural distinctiveness is the target; benchmarks are downstream validation.
- **Sociality, affect, full embodiment** — considered and not registered, with reasons, in the taxonomy's Candidate Register; importing them would violate Pillar II.
- **Rust-backend default** — an open *question* with a stated blocker (crates.io unreachable under sandbox), not a gap; the measured case for urgency dissolved (0.22%).
