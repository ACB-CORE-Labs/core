# The Gap Register

**Assessor:** Fable 5 (Phase 4) · **Verified at:** `8927c563` (2026-07-27)
**Standing:** This is CORE's first *live* gap register since `docs/gaps.md` closed its 26th entry. Proposal (for ruling): this register supersedes `docs/gaps.md`, which is marked historical; two dead registers plus a live one is worse than one live one.
**Discipline:** A gap is an *absence the telos requires filled* with no explicit deferral ruling. Deferred-with-ruling is not a gap (scripture content is the model). Every entry carries evidence, its **deciding authority**, and a leverage rank. The register decides nothing.
**Amended:** 2026-07-27 at `ed06dd64` (Opus 5, Phase 6) · **re-verified 2026-07-28 at `797ebad5`** — every amended claim below was re-measured against code at the current tip before landing, and all held (suite sizes 23/13 with the same ten-file delta and no CI-only file; `full = ("tests/",)`; 32 `RuntimeConfig` booleans, 28 off; the daemon flag set unchanged; ADR-0264 §4.1's supersession banner in place; 18 `resolve_promotable_*` organs). Four entries carried claims that code, workflows, and an ADR's own supersession banner falsify. Each amendment is marked **[AMENDED N-x]** inline and derived in [`50-execution-plan.md`](50-execution-plan.md) §0: **G-5** (the soak ran and passed; the pins run twice a day), **G-7** (the orphan scan was an artifact; the mechanism is respecified), **G-8** (28 flags, not 17), **G-10** (the engineering blocker was discharged 2026-07-26). G-19 gains a note: its exposure is already pinned in-repo.

---

## Tier A — Frontier-blocking (each blocks a ratified commitment or the telos itself)

### G-1 · The ADR-0252 §5 experiment — **run to a NO-GO on 2026-07-28; awaiting ratification** **[AMENDED N-8]**
**Layer:** M3 · **Leverage: 1 (highest in the assessment)**
The ratified governing paradigm's single load-bearing empirical claim — can Cl(4,1) geometry carry relational structure the SME way — was authorized (§8.4), scaffolded, and is now **answered**: `docs/research/sme-experiment-verdict-797ebad5.md` records **NO-GO** against a criterion pre-registered at `299c92be` before the run, with a committed report artifact and a pinned `deterministic_digest`. A well-controlled NO-GO is *defined by the ADR as full credit*. The refutation is scoped: it holds for embeddings that encode role-structure as point positions and align them with conformal Procrustes under similarity, because the similarity quotient that would deliver attribute-invariance is the same quotient that annihilates structural contrast — measured, not argued (an `add`-vs-`subtract` minimal pair aligns at residual exactly `0.0`, the two configurations being related by a proper rotation). Across a sweep of attribute weights, every regime where the SME property survives is a regime where attributes contribute nothing.

**This entry's original claim — "has never returned a verdict" — was wrong (N-8).** The experiment had been run **twice**, on `rnd/structure-mapping-experiment` @ `fc9d0c14` and `rnd/sme-experiment-v2` @ `96e5f468`, returning GO both times. Attempt 1 leaked the label into the embedding (disowned by its own successor); attempt 2 was blind and then harvested its separability from `except ValueError: res = 1000.0` — a solver exception counted as a distance — on a corpus that was 46/51 outside `holdout_dev/v1` with nothing marked, carried duplicate graphs and colliding ids, and whose extractor was never committed. Two GO verdicts sat unmerged and unratified for nine days while the register recorded the item as unrun.
**Evidence:** `docs/research/sme-experiment-verdict-797ebad5.md`; `docs/research/sme-experiment-preregistration-2026-07-28.md`; `evals/structure_mapping/adr0252_s5/`; `tests/test_adr_0252_s5_blindness.py`. · **Authority:** Shay's ratification of the verdict, and the §6 build-authorization ruling it unblocks.

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

### G-5 · L10 proof debt — the soak ran and passed; what is owed is the artifact, the pinned digest, and a cadence **[AMENDED N-1/N-2/N-4]**
**Layer:** M6 / MV · **Leverage: 5**
The always-on process is built; the falsifiable harness (H1–H4, holds/bites pairs, vacuity-guarded) is built; **and it was run.** `evals/l10_always_on/contract.md` §"The measured result" records a **5000-beat soak with a reboot at beat 2500** (landed 2026-07-19 in `aed273b1`) in which all four predicates pass: `versor_condition` flat at `1.389e-07` across all 5000 beats, vault bounded at 6 entries, convergence at beat 1 with the 4999-beat tail at rest, reboot resuming the same life with derived learning intact.

What remains owed is the **ceremony**, and it is this assessment's own §8 maintenance contract operating on this assessment's own frontier:
- the result is **prose in a contract file** — no committed machine-readable report, no run SHA, no rerun path;
- `deterministic_digest` is computed by `report.py` and **pinned nowhere**, though the contract's closing line says *"Pin it once the lane is trusted so a regression flips it"*;
- **no cadence** rules the lane, and the local-first/Mac-runner doctrine makes "nightly" itself a ruling rather than a cron line.

A recorded prose result with no pinned digest is **testimony, not evidence** — the same failure mode as the map, the ratchet, and the blueprint.

**Absorbed 2026-07-28 (R-7, PR-3) — the substrate-liveness ratchet's seven OPEN items.** The ratchet is now historical; every one of its open entries was L10-chained, which is this entry, so they live here rather than in a stale instrument:

| Item | What it is | Chain |
|---|---|---|
| **W-003** | `VaultPromotionPolicy` dormant | audit-dependency on L10 |
| **W-005** | E0/E2 readback modulation absent | W-004 → W-005 |
| **W-007** | `DerivedRecognizer` not integrated into the live turn loop | W-003 → recognizer-storage ADR → W-007 |
| **W-008** | Runtime model (L10) scope adoption | scope landed (#236); spike/ADR pending |
| **W-009** | HITL async queue surface | W-008 → W-009 |
| **W-017** | Automated T1/T2 → T3 promotion absent | W-009 → W-017 |
| **W-018** | ADR-0080 contemplation not autonomous | W-008 → W-018 |

Their dependency reasoning is still sound and is the ratchet's lasting contribution; its *status column* was not, which is why the instrument is retired and its content is not.

**Two prior claims in this entry were wrong and are withdrawn.** (a) *"No suite contains any `l10`/`always_on` test"* was a scan artifact: `TEST_SUITES["full"] = ("tests/",)` is a **directory**, so every test file is trivially in a suite. The true statement is that the five `tests/test_l10_*.py` files are in **no curated suite tuple** — reachable only through `full`. (b) *"nothing runs its pins"* is false: CI never invokes `core test --suite`, it runs raw pytest with marker filters, and no L10 file carries `quarantine` or `slow` — so the pins **execute twice a day**, in `full-pytest.yml` (post-merge) and `nightly-full-pytest.yml` (cron `0 2 * * *`). The correct statement is that **nothing runs them on any pre-merge gate**.
**Evidence:** `M6` + `always-on-process` cards; `evals/l10_always_on/contract.md`; `core/cli_test.py:13`; `.github/workflows/{smoke,full-pytest,nightly-full-pytest}.yml`. · **Authority:** execution + the R-9 evidence-standard and cadence ruling.

### G-6 · F-6 — the lived learning loop is half-gated
**Layer:** M6/M5 · **Leverage: 6**
The daemon forces `consolidate_determinations` but not `accrue_realized_knowledge`; the only turn-path writer of realized facts sits behind the unforced flag. As coded, the continuous life may consolidate an empty set. Incomplete flag set, or intended dormancy — **neither is documented**, and a prior verification doc asserts the opposite of the code (C-5).
**Evidence:** `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:45-49`); `determine-phase` card gating table. · **Authority:** ruling (one flag + one sentence, or a documented dormancy rationale).

**CLOSED 2026-07-28 — R-3 ruled A (incomplete flag set), executed with PR-5.** `accrue_realized_knowledge` joined `CONTINUOUS_LIFE_CONFIG_FLAGS`; the daemon now forces the producer alongside the consumer. **The decisive evidence was in the code, not the documents:** *both* flags' own comment blocks in `core/config.py` already described the corrected profile — `accrue_realized_knowledge` says *"the production L10 process enables it alongside `persist_session_state`"* and `consolidate_determinations` says *"…alongside `accrue_realized_knowledge` + `persist_session_state`."* Three records (two docstrings and the 07-25 verification doc) agreed with each other and disagreed with four lines of code. Dormancy was a coherent ruling and would have cost correcting three records that were **right about the design**; incompleteness cost one line.

**The plan's "N-6 docstring correction" deliverable therefore dissolved rather than shipping** — adding the flag made both docstrings true. Recorded because a PR that quietly ships less than it promised is the same class of divergence this register exists to catch.

**Red before green:** the assertion `cfg.accrue_realized_knowledge is True` was added to `tests/test_l10_always_on_daemon.py` and **observed failing** before the flag was added. That file was in no curated suite, so the change would otherwise have shipped guarded only by tests no gate runs — it is now on the gate (measured +9.4s, +4.3% of smoke).

**Consequence for PR-11, and it is not incidental:** the 5000-beat soak recorded in `evals/l10_always_on/contract.md` (2026-07-19) ran *before* this change and therefore describes **a different configuration than the one that now ships.** PR-11's re-run is the first soak of the corrected profile, and Step B feeding Step D is exactly what a long horizon stresses.

---

## Tier B — Enforcement & instrument debt (capability exists; the guarantee doesn't)

### G-7 · No gate-parity pin and no *curated*-suite membership check **[AMENDED N-1/N-3]**
**Layer:** MV · **Leverage: 7** — **the highest-leverage single mechanical change in the repository**
Suite tuples are hand-curated; a test file in zero *curated* suites is indistinguishable from one that runs everywhere.

**The mechanism this entry originally proposed would not have worked.** "Every `tests/**/*.py` belongs to ≥1 suite or an explicit exclusion list" is **already satisfied**, because `TEST_SUITES["full"] = ("tests/",)` is a directory — the pin would ship green and prove nothing. A hollow gate by the Third-Door criterion, in the entry proposing to abolish hollow gates.

**The correct mechanism is two pins:**
1. **Gate parity** — `smoke.yml`'s path set must equal `TEST_SUITES["smoke"]`, parsed from the workflow file, failing on drift in either direction.
2. **Curated-suite membership** — every `tests/**/test_*.py` is in ≥1 suite **excluding `full`**, or in a registered exclusion list with a one-line reason.

Pin 1 exists because the two gates have **already** drifted (see H-12): the local suite is 23 files, `smoke.yml` is 13, and the 10-file delta includes ADR-0265's denial pin, both ADR-governance pins, volume honesty, and curriculum polarity. Measured parity cost: **429 tests in 46s** on the Act runner's own hardware.

**CLOSED 2026-07-28 — and pin 1 was withdrawn rather than built (N-9).**

*Pin 1 was already in the repository, in the only direction that protects anything.* `test_cli_smoke_suite_covers_ci_smoke_gate` has pinned `smoke.yml ⊆ TEST_SUITES["smoke"]` throughout (which is why every measurement above finds **CI-only = 0** — a pin, not luck), under a comment reading *"DELIBERATELY ONE-DIRECTIONAL."* The symmetric version was written and reverted the same day in `50fa287d` (2026-07-25), because `AGENTS.md:280` makes GitHub Actions *"billing-locked … dead signals"* and §277 makes the workflows *"secondary observability only."* This entry's "the two gates have already drifted" is therefore a **misreading of a design decision**, and the delta is not a defect to close.

*Pin 2 shipped, re-specified — and it caught its author within the hour:* PR-6 promoted `tests/test_safety_pack.py` onto the gate and left it in the baseline; the both-directions half failed the very next smoke run, and the count went 749 → 748. *Pin 2 shipped, re-specified.* Measured **749 of 877** test files in no curated suite. The mechanism this entry proposes — assign every orphan, or list it with a reason — is hollow at that scale for the same reason the entry itself identifies: glob topic-suites satisfy the assertion while changing nothing about what runs. All four demonstrated incidents were caused by a *newly landed* orphan, never a legacy one, so what shipped is a **ratchet**: `tests/test_suite_membership.py` + `tests/full_only_baseline.txt`, blocking new orphans, enforced in both directions, count pinned. Three sabotages observed red.

**REOPENED, PARTLY — 2026-07-28, by the arc's own full-tree run.** The ratchet closes *membership*. It does **not** close *execution*, and the difference is not academic: the first full-tree run of this arc found `tests/test_ratification_ceremony.py` **red on `main`, in a curated suite (`teaching`), and run by no gate** — the pre-push gate invokes `smoke` + the warmed_session lane + `deductive`, and nothing invokes `teaching`. That is exactly the hollow-gate failure this entry's own re-specification warned about — *"a curated suite nobody runs is the same non-guarantee as `full`, wearing a different name"* — demonstrated live, on a pin guarding ratification-corpus byte compatibility.

**PIN 3 LANDED 2026-07-28** — `tests/test_suite_reachability.py`, on the gate. **What PR-4 owed was a third pin: reachability.** Every curated suite must be reachable from a gate tier (`scripts/hooks/pre-push` / `local-ci.sh`), or be declared post-merge-only with a stated reason. `teaching`, `packs`, `algebra`, `sensorium`, `cognition`, `runtime` and the rest are currently in the unreachable set — they have members, and no gate calls them. Membership was never the guarantee; execution is.

**Shipped as baseline + ratchet**, sized to the measurement rather than to the rule: **21 curated suites, 2 gate-reachable** (`smoke`, `deductive`). Demanding 19 `post-merge-only` justifications in one sitting is the ceremony failure already rejected for the 749-file membership baseline. So the pin freezes the 19-suite gap, fails on growth, enforces both directions (a promoted suite must leave the baseline), **verifies its declared gate set against the shell** so it cannot go vacuous, and pins the count. Two sabotages observed red — a new curated suite with no gate caller, and a `GATE_SUITES` value drifting from `pre-push`/`local-ci.sh`.

**What pin 3 deliberately does not do — and what is now Shay's to decide:** *which* of the 19 belong on the gate. That costs gate time and is a real decision. `teaching` is the obvious first candidate: it just shipped a red ratification pin that no gate ran. Recorded as the open half of this entry.

**The gap is 15, not 19, and the open half is now a scheduled plan item.** PR-3b (Wave 1, per R-7) deleted four aliases with zero `--suite` references anywhere — `refusal`, `margin`, `rotor`, `inner-loop` — taking the curated set 21 → 17 and the unreachable set **19 → 15, by deletion**, which costs no gate time at all. That is the ratchet turning the way it is meant to. The remaining fifteen are each named in AGENTS.md, CLI help, a README or an ADR, so deletion is not available for them and promotion is the only way the number falls further. The decision was a parenthetical in this entry and in PR-4 — which is precisely how fifteen suites came to be unreachable without anyone choosing it — so it is now **PR-4b** in `50-execution-plan.md` §4, sized, recommended (`teaching` alone, first), and prepared so ruling costs one word.

*One real gap the entry was circling, now fixed:* the parity pin lived in `fast`, which the pre-push gate does not run — **the pin guarding the gate did not run on the gate**. It is now in `smoke`.
**Evidence:** `tests/test_suite_membership.py`; `tests/full_only_baseline.txt`; `tests/test_cli_test_suites.py:49`; `50fa287d`; `AGENTS.md:275-280`. · **Authority:** discharged mechanically; **no R-14 ruling is owed** for any of it.

### G-8 · No flag-default register **[AMENDED N-7]**
**Layer:** cross-cut · **Leverage: 8**
`RuntimeConfig` is a single frozen dataclass with **32 boolean fields: 28 default `False`, 4 default `True`** (`allow_cross_language_recall`, `use_salience`, `discourse_planner`, `deduction_serving_enabled` — the last ratified ON by ADR-0256). Three are daemon-forced (`persist_session_state`, `consolidate_determinations`, `strict_identity_continuity`). No document states the set, which defaults are deliberate posture vs accumulated hesitancy, or what evidence would flip each. The largest lever in the system, unregistered. The register format already exists in-repo: the ratified-ledger pattern (declare absence policy in the table, not the call site — ADR-0263 Rule 5).

*(This entry originally said "seventeen." The verified count is 28 default-off. That two counts of the same set differ by eleven is itself the finding: nothing in the repository distinguishes a capability flag from a policy or deployment flag, which is exactly the classification the register must make.)*
**Evidence:** `core/config.py` at `ed06dd64` (32 `bool` fields, 28 `= False`, 4 `= True`); daemon trio (Phase 3). · **Authority:** documentation PR + per-flag evidence bars set by ruling (R-4).

**CLOSED 2026-07-28 — `docs/specs/flag_register.md`, with R-4's profile mechanism, enforced by `tests/test_flag_register.py` on the gate.** All 32 booleans registered with class, governing ADR, recorded rationale, and *what evidence would flip it*. The classification this entry called for is made explicitly and is the document's load-bearing half — **CAPABILITY** (what CORE can do), **POSTURE** (what CORE serves or refuses as true — the `wrong=0` boundary, ruling-only), **DEPLOYMENT** (cost and lifecycle). `estimation_enabled` and `composed_surface` are both `= False` and are not the same kind of thing; nothing in the repository said so before.

**The pin is bidirectional**, because one direction would have passed through both failures it exists to prevent: a flag added to `core/config.py` and not registered fails; a register row outliving its flag fails; and the counts the register's prose states (32 / 4 ON) are pinned, since a stale count is how this entry came to exist. **Four sabotages observed red**, one of them caught by two independent pins.

**Two findings the register produced that this entry did not anticipate.**
1. **Accumulated permissiveness, not just hesitancy.** Of the **four default-ON flags, one** has a governing ADR (`deduction_serving_enabled` / ADR-0256) and **two have no recorded reason of any kind** — `allow_cross_language_recall` and `use_salience` have no comment block, no ADR, no criterion. In an architecture built on earned licenses, two permanently-on capability flags with no recorded decision is this entry's question inverted. Registered, deliberately **not** fixed: writing a rationale after the fact would invent a decision nobody made.
2. **A hollow gate inside the governance pin.** `test_default_on_flag_is_not_governed_by_a_proposed_adr` is parameterized over *(default-ON flag × cited ADR)*, so the three uncited ON flags contribute **zero cases** — it covered exactly one flag — while its non-vacuity guard checked only that *some* flag cites an ADR, which default-*off* flags satisfy in abundance. One reformatted comment away from zero coverage with everything green. Guard tightened and **observed red** by stripping ADR-0256's citation.

*Also delivered here, from the 2026-07-28 external-assessment triage:* **§5, the declared-table index** — the eight single-source-of-truth tables in the repository and the pin that makes each true. A reader's aid, explicitly not a central `contracts.toml`, which would add a fifth copy needing agreement with four generators and put four authorities in one merge surface.

### G-9 · Enforcement pins unverified for three doctrine-level prohibitions
**Layer:** M1 / MG · **Leverage: 9**
(a) No verified failing pin for the no-approximate-recall law (would a cosine ranker actually fail a test?); (b) no pin that fails when a layer *bypasses* governance entirely (as distinct from governance working when called); (c) safety-pack non-swappability not verified as mechanically enforced. All three are law in `AGENTS.md`; law-enforced-by-review is weaker than law-enforced-by-test.
**CLOSED 2026-07-28 — PR-6. The verification pass found the three in different states, and the differences are the finding.**

**(a) Exact recall — was the real gap, and worse than stated.** The question "would a cosine ranker actually fail a test?" had the answer *no, almost anywhere*. One import ban existed, over exactly one file (`core/physics/wave_manifold.py`, in `test_third_door_cohesion.py` — itself in no curated suite). Meanwhile `generate/realize/recall.py`, which *is* the recall path, states the prohibition in its module docstring — *"an exact, deterministic equality scan (no cosine / HNSW / ANN)"* — with nothing behind it. Law asserted where it executes, enforced nowhere: the H-8 failure mode applied to a prohibition. Now scanned across `vault/`, `generate/realize/`, `generate/meaning_graph/`, `field/`, `recognition/` for banned ANN libraries **and** for hand-rolled `cosine*` definitions — because an import ban only stops the convenient version, and ten lines of numpy is the realistic way a well-meaning contributor violates this.

**(b) Governance bypass — the pin now exists and is exact.** INV-07 proves governance works *when called*; nothing proved it could not be skipped. The mechanism: every function in `chat/runtime.py` that constructs a `TurnVerdicts` must also invoke `safety_check.check`, and every such call must pass `self.safety_pack` (a bypass need not skip the call — it can substitute the pack). Measured at close: two verdict-constructing functions, both governed.

**(c) Safety-pack non-swappability — was already well pinned; its gap was reach, not coverage.** `tests/test_safety_pack.py` pins unratified-pack-refused-in-production, missing-companion-report-refused, seal-failure-refused, path-traversal-rejected, missing-pack-fails-closed. It ran in **no curated suite** — a fail-closed safety contract verified only after merge. Promoted onto the gate; the new pin guards that placement rather than duplicating the substance.

**Verification:** four sabotages, each observed red and each caught by its own pin — a banned library imported on a recall path, a hand-rolled cosine ranker, a serving path assembling verdicts without governing, and the safety pack demoted off the gate.
**Evidence:** `tests/test_doctrine_prohibitions.py`; `tests/test_safety_pack.py`; `AGENTS.md` §"Exact recall"; `generate/realize/recall.py`. · **Authority:** discharged mechanically; no ruling was owed.

### G-10 · Curriculum SERVE is blocked by **one ruling**, and its ledger doesn't exist **[AMENDED N-5]**
**Layer:** M5 · **Leverage: 10**
**The engineering blocker this entry named does not exist.** ADR-0264 §4.1 carries a banner directly beneath its own heading: *"**SELF-SUPERSEDED by this ADR's own R5, discharged 2026-07-26. The heading is no longer true of the running system.** … R5 removed that: compilation is query-scoped, so a family of any size answers. With the cap gone, **four bands would earn SERVE the moment a ledger is sealed** — `physics·causal`, `systems_software·causal`, and `philosophy_theology·{modal,contrast}`."* Query-scoping already landed; this entry quoted a superseded heading past its own correction.

What survives, and is now the **whole** of the blockage: reliability is commitment precision and a correct UNKNOWN *is* a commitment, so a band clears θ_SERVE **on non-commitments alone** (`conservative_floor(660,660) = 0.990046`). The licensable evidence is 99.0–99.98% non-entailed and **max entailed volume in any band is 9**. `chat/data/curriculum_serve_ledger.json` is deliberately absent (the one honest `missing_ok=True` in production) and `core proposal-queue reseal` refuses a license without `--allow-new-licenses`, so nothing is licensed while the outcome-mix ruling is unmade. A committed ledger is necessarily an *earning* one.
**Evidence:** `M5` card; ADR-0264 §4.1 supersession banner + §5 (open); `docs/research/curriculum-practice-producer-2026-07-26.md` §1; `chat/curriculum_serve_license.py:40-52`. · **Authority:** the outcome-mix ruling (R-8) **alone** — no engineering prerequisite remains.

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

### G-15 · The daemon's ratifying ADR — **CLOSED 2026-07-28 (R-12a)**
`chat/always_on_daemon.py` was unowned while ADR-0146 explicitly rejected the daemon shape it implements. Whatever the right answer, the record contradicted the code (see H-8a). **Authority:** ADR amendment or a new short ADR.

**Closed by amendment, not by a new ADR — and the choice mattered.** ADR-0146 now carries an addendum owning the daemon: the Shape-A rejection **stands as reasoning** (a daemon does require supervision infrastructure Shape B does not), and the infrastructure was subsequently built. The three items its "What is NOT in Scope" excluded are each mapped to where they are implemented — `fcntl.flock` single-instance lock acquired before any signal or runtime setup, SIGINT/SIGTERM graceful stop, and the load-time strict-identity guard that makes a daemon restart *the same life or nothing*. Shape B remains the persistence model and the CLI default; the daemon is an additional process shape layered on it. A new ADR for a shape shipped six weeks earlier would have added a document without adding a decision.

**The stale bullet carries an inline pointer**, not just a note at the end. H-8's mechanism is that an authoritative-looking line converts *"I should check"* into *"I already checked"* — a reader who stops at the excluded-scope list is exactly the reader this gap is about, and they never reach a trailing addendum.

**Evidence:** `docs/adr/ADR-0146-…md` §"What is NOT in Scope" + Addendum; `chat/always_on_daemon.py:48,82,145`; introduced `18e25580` (2026-06-14, the same commit adding both the lock and the signals — established only after deepening a shallow 168-commit clone to 2340, since the shallow boundary was reporting a false date).

---

## Tier D — Latent & carried-forward (recorded so nothing silently drops)

- **G-16 · ADR-0265's defect class survives in `_inflect_predicate`'s aspect arms** (`generate/templates.py:79`) — 10,530/16,146 template points, *not reachable today*. Latent, recorded from the prior arc; becomes live if aspect arms become reachable. **Authority:** the widening program (G-3) must clear it first.
- **G-17 · Non-text ingest** — 59 sensorium modules, no serving path, no entry criterion; projection heads do not exist. Position paper is honest about this. Needs either an entry criterion or an explicit deferral ruling (the falsification bench is the standard the track should be held to when it moves). **Authority:** ruling.
- **G-18 · Identity-divergence curriculum may still bypass formation's gates** — known gap since 2026-05-17 (`teaching_order.md`); unverified at this SHA. **Authority:** Phase-3-style verification pass, then a routing PR.
- **G-19 · Wilson/replay evidence shortfall** — 21/25 ratified bands short if replays were counted as independent trials (see H-1 for the mechanism). Recorded here as *evidence debt on existing licenses*; the counting fix is the hindrance entry. **Note (Phase 6):** the exposure is **already pinned in-repo** — `tests/test_volume_honesty.py` (ADR-0264 R9, in the local smoke gate) pins the 21-of-25 shortfall *"in BOTH directions"* and calls its inventory *"an EXPOSURE INVENTORY, not an approved baseline."* So the open work is **applying** the demotions, not discovering them, and that pin moves in the same PR. **Authority:** ADR amendment + re-count, authorized by R-13.
- **G-22 · Three tests are red on `main`, and were red before this arc** *(new, 2026-07-28)* — found by the arc's first full-tree run (`3 failed, 13403 passed`), and reproduced identically at `797ebad5`, so **not arc-caused**. `tests/test_ratification_ceremony.py::{test_row_is_byte_compatible_with_the_committed_corpus, test_unreviewed_status_is_refused}` and `tests/test_claims_md_is_current.py::test_claims_md_matches_generator_output`. **Diagnosis:** the code is correct and the pins are stale. `ChainRecord.__slots__` gained `polarity` (ADR-0264 R1), and the serializer **deliberately omits it for affirmative rows** (`teaching/ratification.py:119`) — so a test that builds `ChainRecord(**{k: row[k] for k in __slots__})` `KeyError`s on a correctly-serialized row. Same class as H-8e: ratified design right, pin not updated. **Consequence:** the ratification-corpus byte-compatibility guarantee and the unreviewed-status refusal have been **unverified since ADR-0264 R1 landed**. `test_ratification_ceremony.py` is curated (`teaching`) but ungated; `test_claims_md_is_current.py` is an orphan. **RULED 2026-07-28 (Shay): fix, don't document.** The argument that settled it: *a red test on a serving-path contract, left with an explanatory note, IS the H-8 failure mode* — a document acknowledging a gap instead of closing it, which becomes the next assessor's finding. **FIXED**, and the `CLAIMS.md` half turned out to be the more serious of the two:

- **The two ceremony pins were stale against correct code** (H-8e's class). `polarity` defaults to `AFFIRMATIVE` and is *deliberately omitted* from affirmative rows; the pins iterated `__slots__` and indexed the row, so they broke on every correctly-serialized row. Now built from the row's own keys, letting absent fields take their defaults — which restores the guarantee rather than weakening it. Ratification-corpus byte compatibility and unreviewed-status refusal had been **unverified since ADR-0264 R1 landed**.
- **`CLAIMS.md` was publishing a superseded evidence digest for a licensed capability.** Commit `f9e9cc0c` (2026-07-26, *"the deduction lane hashes the prose it serves"*) strengthened the lane, rewrote `evals/deduction_serve/report.json`, and updated the authoritative pin in `scripts/verify_lane_shas.py:60` to `c855d55c…` — recording the old `0b461a5a…` as superseded on line 56. It did **not** regenerate `CLAIMS.md`. So for two days the published capability claim for `deduction_serve_v1` pointed at evidence that no longer existed. The claim *text* never changed; only the pointer was wrong — but a claim whose evidence digest does not match its evidence is exactly the failure the digest exists to prevent.
- **The drift had propagated to a third artifact — this directory.** `10-layer-cards/M3-comprehension-reasoning.md` cited the same stale `0b461a5a…` as its would-fail-if-absent evidence. Corrected.

**The mechanism, and why it is G-7's story again:** one commit updated the lane, its verifier and its test, and missed one downstream artifact. The pin that guards that artifact — `tests/test_claims_md_is_current.py` — **exists and is an orphan in no curated suite**, so nothing surfaced it until this arc ran the full tree once. Registered on the gate as part of the fix.
- **G-21 · The math reader decides 1.0% of `holdout_dev/v1`** *(new, 2026-07-28)* — measured while building the §5 corpus: `parse_and_solve` returns a selected graph for **5 of 500** held-out cases, all carrying the same relational skeleton (`compare_multiplicative`); on the public lane, 24/150. This is a sharper measurement of the comprehension frontier than G-3's construction count, on the corpus the project already treats as its held-out standard, and it is why ADR-0252 §5.1's four-structure corpus is not extractable today. Distinct from G-3 (which counts *constructions* the general reader admits); this counts *cases decided* on a standing eval corpus. **Authority:** the widening program (G-3) + a ruling on whether holdout decision-rate becomes a tracked lane metric.
- **G-20 · The `refusal_reason` materialisation** — typed refusal evidence exists and is discarded at the public `str` boundary; the plumbing for materialisation already landed. Cross-listed as H-3. **Authority:** small ADR (anticipated by the ADR-0024 chain).
- **G-23 · The domain↔pack binding is stated twice and checked in one direction** *(new, 2026-07-28; **pinned** the same day)* — `core/capability/domains.py`'s `DOMAIN_PACKS` declares domain→pack membership for the capability ledger; each `packs/data/<pack>/manifest.json` independently declares `domain_id`. `domain_contract_predicates.py` **P3** validates `domain_id → a known ledger domain` and is the only binding check that existed. Nothing validated the reverse, and **P3 passes vacuously on a manifest with no `domain_id` at all** — the same shape as its own `test_pack_without_contract_reports_absent`. **Measured: 7 of 9 bound, 0 contradictory, 2 absent** — `en_core_cognition_v1` and `en_core_meta_v1`, both placed in `philosophy_theology`, which is one of the four bands queued to earn a SERVE license behind R-8. The domain whose license is next to be earned is the one whose binding exists in only one place.

  *Why nothing caught it:* `tests/test_domain_contract_predicates.py` exercises P1–P9 entirely against synthetic `tmp_path` manifests — never against the real nine — and is itself in **no curated suite**. A predicate proven correct on fabricated input and never run on the real input is this arc's defect class stated precisely: its success state and *"it never ran here"* are indistinguishable.

  *How it was found, recorded because the method matters:* an external assessment proposed collapsing the pack/domain machinery, reasoning explicitly from a directory listing. Every specific it gave was falsified by opening the files (see the 2026-07-28 triage in `31-hindrance-audit.md`) — but the seam it pointed at was real. Bad method, useful direction; both halves are worth recording.

  **Pinned, not fixed** — `tests/test_domain_pack_binding.py`, on the gate. Freezes the 2-pack gap, fails on contradiction always and on absence unless baselined, enforces both directions, pins the reverse direction (a pack may not self-assign a ledger domain — clean across all 30 packs today), and guards its own parse against vacuity. **Four sabotages observed red.** The fix is deliberately *not* here: whether `en_core_cognition_v1` is *a philosophy_theology domain pack* or merely *grouped under that domain for ledger accounting* is a ratification-adjacent content question. **Authority:** R-8 / PR-14, where that band's license is decided.

---

## What is *not* in this register, and why

- **Scripture/theology content** — deferred by explicit ruling (2026-07-26); the model case for deferred-is-not-missing.
- **Benchmark wins** — excluded by the completeness criterion itself (taxonomy §6): architectural distinctiveness is the target; benchmarks are downstream validation.
- **Sociality, affect, full embodiment** — considered and not registered, with reasons, in the taxonomy's Candidate Register; importing them would violate Pillar II.
- **Rust-backend default** — an open *question* with a stated blocker (crates.io unreachable under sandbox), not a gap; the measured case for urgency dissolved (0.22%).
