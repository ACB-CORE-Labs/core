# The Execution Plan

**Planner:** Opus 5 · 2026-07-27 · verified at `forgejo/main` @ `ed06dd64`
**Governs:** everything in `30-gap-register.md` (G-1…G-21) and `31-hindrance-audit.md` (H-1…H-14), sequenced by `40-assessment.md` §6.
**Method:** `docs/conceptualizing_engineering_mastery.md` — scrub → **delete** → simplify/enforce → accelerate → automate last. Nothing is automated that Waves 0–3 have not proven.
**Status (2026-07-28):** Wave 0's builds are **done** — PR-0 merged (#140), PR-1 landed, R-10 discharged by merging #138. **Track A is run and returned NO-GO** (`docs/research/sme-experiment-verdict-797ebad5.md`), awaiting ratification. R-1…R-14 remain PENDING and gate Waves 1–4; Tracks B–E are unstarted behind them.

---

## 0. Seven corrections to the assessment, found while sizing and executing this plan

The assessment's authority rests on its self-correction chain — *"nothing in the chain was ever caught by re-reading documents"* (§8). Planning it produced seven more, all caught by reading code, workflows, and the ADRs' own supersession banners. Four of them change planned work: two change the design of the highest-leverage mechanical item, one **deletes a Wave-3 PR** because the work already shipped, and one **halves the severity** of a claim this plan made in its own first draft.

| # | Corrects | Effect on the plan |
|---|---|---|
| N-1 | G-5/G-7 "no suite contains any `l10` test" | scan artifact; G-7 respecified |
| N-2 | G-5 "nothing runs its pins" | pins run twice a day; severity lowered |
| N-3 | *(new)* local gate ≠ CI gate | G-7 gains a second pin; **severity lower than this plan first stated** |
| N-4 | G-5 "the soak has never produced an artifact" | **the soak was run**; the debt is the artifact, not the run |
| N-5 | G-10 "SERVE blocked by the 16-premise cap" | **the cap was removed 2026-07-26**; PR-13 withdrawn |
| N-6 | *(new)* H-8 has a fourth instance, in the code | strengthens R-3 toward "incomplete flag set" |
| N-7 | G-8 "seventeen capability flags" | the real number is 28 of 32; G-8 grows |
| N-8 | G-1 / this §6 "the §5 experiment is unrun" | **it had been run twice, returning GO twice, on unmerged branches** — both unsound; Track A's job was re-scoped from *run it* to *run it soundly* |
| N-9 | N-3 / H-12 / R-14 / PR-4 "the gate drift was never intended" | **it was deliberated and reverted on 2026-07-25** (`50fa287d`); the parity pin already exists, one-directional by decision. PR-4's pin 1 is **withdrawn**; R-14's premise is corrected |

### N-1 · "No suite contains any `l10`/`always_on` test" is a scan artifact — the same artifact class caught twice before

`TEST_SUITES["full"] = ("tests/",)` — a **directory**, not `.py` literals. Every test file in the repository is therefore trivially "in a suite," and a scan that reads only quoted `.py` names reports orphans that aren't. This is the third appearance of this exact artifact (Phase 4 caught `formation 0`; the same shape produced this claim).

**The true statement:** the five `tests/test_l10_*.py` files appear in **no curated suite tuple** — they are reachable only through `full`.

### N-2 · The L10 pins are not unrun — they run post-merge and nightly

CI does not invoke `core test --suite` at all. It runs raw pytest with marker filters:

| Workflow | Trigger | Selector | Covers L10? |
|---|---|---|---|
| `smoke.yml` | every PR push (**secondary observability**, AGENTS.md §CI/CD — *not* the merge gate) | 8 path patterns → 13 files | **no** |
| `full-pytest.yml` | post-merge on `main` | `-m "not quarantine and not slow"` | **yes** |
| `nightly-full-pytest.yml` | cron `0 2 * * *` | `-m "not quarantine"` | **yes** |

No `tests/test_l10_*.py` file carries `quarantine` or `slow`. **They execute twice a day.** G-5's "nothing runs its pins" is wrong and must be amended to "**nothing runs its pins on any pre-merge gate**" — real, but a different severity.

### N-3 · The local pre-push gate and the CI observability run have diverged — 10 files — *and the first draft of this plan overstated it*

`TEST_SUITES["smoke"]` = **23** files. `smoke.yml` = 8 patterns expanding to **13** files. Ten files are in the local gate and not in CI:

```
test_audit_ledger_r7            test_cli_runner_contract      test_pack_draft_serve_boundary
test_workbench_deduction_provenance   test_prior_surface_deduction_binding
test_negation_survives_articulation   test_adr_status_governance    test_adr_index
test_volume_honesty             test_curriculum_polarity
```

*(This plan's first draft said 27 vs 13. The 27 was a regex artifact — comment prose inside the tuple matched as paths. The delta of 10 was correct; the tuple size was not. Recorded because a plan that corrects the assessment must correct itself by the same standard.)*

**The severity is lower than first stated, and the reason matters.** AGENTS.md §CI/CD Runner Architecture is explicit: *"The `.github/workflows/*.yml` files … are secondary observability only — never a substitute for local gates."* The merge gate **is** the in-worktree run, and the in-worktree run is the superset. Eight of the ten files carry comments saying they belong "on the pre-push gate" — which is exactly where they are. Under doctrine, **nothing is unguarded.**

Two things are still true and worth fixing:

1. **Two independent places assert the parity.** The audio block in `core/cli_test.py` says it is listed explicitly "so the local-first pre-push gate (AGENTS.md protocol) **equals** the CI gate rather than silently narrowing it" — read narrowly (about the six audio files) accurate, read as a statement about the smoke suite, false. And `scripts/hooks/pre-push` — the automation of the AGENTS.md protocol — opens by describing its own step 1 as "the `smoke` suite — **exact CI-gate parity**." It is not: 23 files against 13. The claim appears twice, in the enforcement tooling, which is the strongest evidence available that the drift was never intended.
2. **The real exposure is the push that skipped the local gate.** CI is the only *automatic* check on a push made from a cloud session, another machine, or an agent that did not run the worktree gate. For those pushes, ADR-0265's denial pin, the ADR-governance pins, volume honesty, and curriculum polarity run nowhere before merge.

**Consequence for G-7.** The meta-check as written in the register ("every test file belongs to ≥1 suite") is **already satisfied and would ship green while proving nothing** — a hollow gate by the Third-Door criterion. The correct mechanism is two pins:

1. **Gate parity** — `smoke.yml`'s path set must equal `TEST_SUITES["smoke"]` (a failing test when they drift). This is the pin that would have caught N-3.
2. **Curated-suite membership** — every `tests/**/test_*.py` belongs to ≥1 suite **other than `full`**, or to a registered exclusion list with a reason.

**Measured cost of parity:** the 10 files are **429 tests in 46s** on this Mac — which is the same hardware the Act runner executes on (`ubuntu-latest:host` = native macOS host). So the parity cost is a measured 46s, not an estimate. See R-14.

### N-4 · The L10 soak **has** been run — 5000 beats, all four gates pass. The debt is the artifact, not the run.

`evals/l10_always_on/contract.md` §"The measured result" records a **5000-beat soak with a reboot at beat 2500**, landed 2026-07-19 in `aed273b1`: all four predicates pass, `versor_condition` flat at `1.389e-07` across all 5000 beats, vault bounded at 6 entries, convergence at beat 1 with a 4999-beat tail at rest, reboot resuming the same life with derived learning intact.

G-5's *"the soak has never produced an artifact"* is therefore wrong as stated. What is **exactly** true, and is the real and unchanged debt:

- the result lives as **prose in a contract file** — no committed machine-readable report, no run SHA, no rerun path;
- `deterministic_digest` is computed by `report.py` and **pinned nowhere** — the contract's own last line says *"Pin it once the lane is trusted so a regression flips it,"* and it never was;
- **no cadence** rules the lane.

That is the assessment's own maintenance-contract failure mode operating on the assessment's own frontier: a recorded prose result with no pinned digest **is testimony, not evidence**. PR-11 gets *cheaper* (the run is known to pass at 5000 beats) and *sharper* (its deliverable is the committed artifact + the pinned digest + the cadence, not the discovery of whether it holds).

### N-5 · G-10's blocker was removed on 2026-07-26 — by the ADR the register cites

G-10 says curriculum SERVE is "fully blocked by one engineering item," the 16-premise compilation cap, with authority "engineering (scoping)." ADR-0264 §4.1 carries a banner directly under its heading:

> **SELF-SUPERSEDED by this ADR's own R5, discharged 2026-07-26. The heading is no longer true of the running system.** … R5 removed that: compilation is query-scoped, so a family of any size answers. With the cap gone, **four bands would earn SERVE the moment a ledger is sealed** — `physics·causal`, `systems_software·causal`, and `philosophy_theology·{modal,contrast}`.

**Query-scoping already landed.** The register quoted a superseded heading past its own correction banner. What survives — and is now the *whole* of the throughput frontier's blockage — is the sentence the same banner ends on: *"The binding constraint is now the outcome-mix ruling (§5, recorded as open and still open)."* A band clears θ_SERVE on non-commitments alone (`conservative_floor(660,660) = 0.990046`); max entailed volume in any band is **9**.

**Effect on the plan: PR-13 is withdrawn** — the work exists. R-8 is no longer one ruling among fourteen; it is the single item gating an entire frontier, and four bands are queued behind it.

### N-6 · H-8 has a fourth instance, and it is in the code itself

`core/config.py`'s docstring for `accrue_realized_knowledge` states: *"the production L10 process enables it alongside `persist_session_state`."* The docstring for `consolidate_determinations` states the same about *"accrue_realized_knowledge + persist_session_state."* The production flag set — `CONTINUOUS_LIFE_CONFIG_FLAGS` at `chat/always_on_daemon.py:45-49` — contains `persist_session_state`, `consolidate_determinations`, `strict_identity_continuity`, and **not** `accrue_realized_knowledge`.

Two flags' own documentation asserts a production configuration the production configuration does not have. This is H-8's failure mode located inside the source, one layer below the documents, and it moves R-3's evidence decisively: F-6 reads as an **incomplete flag set**, not intended dormancy. Dormancy remains a coherent ruling — but it would now require correcting two docstrings that say otherwise.

### N-9 · The gate "drift" was a decision, and the pin this plan proposes was already written, tried, and reverted

*(Added 2026-07-28, while executing PR-4. It is the most consequential correction in this section because it **prevents work** rather than re-scoping it.)*

N-3 concluded the 23-vs-13 delta was unintended, on the strength of two in-repo comments asserting parity, and called that *"the strongest evidence available that the drift was never intended."* H-12 repeated it. R-14 built three options on it, recommending **A — raise CI to parity, +46s measured**. PR-4 specified a bidirectional parity pin as its first deliverable.

**All of that is answered by a third artifact none of them read.** `tests/test_cli_test_suites.py::test_cli_smoke_suite_covers_ci_smoke_gate` has enforced the surviving direction — `smoke.yml ⊆ TEST_SUITES["smoke"]` — since before this assessment began. (It is why the delta measures **CI-only = 0**: not luck, a pin.) Directly beneath its assertion sits a comment headed *"DELIBERATELY ONE-DIRECTIONAL — do not 'complete' this by also asserting `local_paths <= ci_paths`."*

Its history is `50fa287d`, **2026-07-25**: *"revert(tests): drop the local-to-CI smoke parity assertion — CI is not a gate."* An earlier agent read the same suite comment this plan read, drew the same inference, made the assertion symmetric, and reported the same class of file as drift. The revert's own words: *"That was wrong, and AGENTS.md says so in a line I had already read."*

**The governing line is `AGENTS.md:280`** — *"GitHub (`AssetOverflow/core`) is a **mirror only**; its Actions are billing-locked and produce dead signals — never chase them."* With §275–279: local-first is the merge bar, `.github/workflows/*.yml` are *"secondary observability only,"* and the Forgejo host cannot run workflows either.

Three consequences:

1. **PR-4's pin 1 is withdrawn.** It exists in the only direction that protects anything, and the other direction has been tried and rejected with the reasoning recorded at the assertion site specifically to stop it being re-derived. This plan re-derived it anyway.
2. **R-14's premise is corrected.** Option A ("raise CI to parity, +46s on the runner's own hardware") spends 46s on a workflow that AGENTS.md says produces dead signals. The measurement was real; the thing measured does not gate.
3. **N-3's exposure claim was too generous to CI, and the real version is worse.** N-3 said *"CI is the only automatic check"* for a push that skipped the local gate. Under `AGENTS.md:280` there is **no automatic check at all** for such a push. The exposure is real and larger than stated — and it cannot be closed by editing `smoke.yml`. It is closed by the local gate being run, which is a hook-and-discipline question, not a workflow question.

**A fourth thing is genuinely open and is what PR-4 keeps:** the parity pin lives in the `fast` suite, and the pre-push gate runs `smoke` + `deductive` (`scripts/hooks/pre-push`, `scripts/ci/local-ci.sh --tier gate`). **The pin that guards the gate does not itself run on the gate.** That is cheap to fix and is real.

*(Two stale claims in the revert's own reasoning, noted for the record: it says pushing workflow changes "needs an OAuth scope the push credential lacks." This session pushed `smoke.yml` edits successfully in `98a6e8b4`. The constraint is not universal — though under §280 the edits buy observability, not gating.)*

### N-8 · The §5 experiment was not unrun — it had returned GO twice, on branches nobody merged

*(Added 2026-07-28, while executing Track A. It is the eighth correction, and like the other seven it came from reading code — here, a branch tip's commit message and the script under it.)*

`rnd/sme-experiment-v2` @ `96e5f468` is titled **"Verdict: GO"** and carries a completed feasibility document dated 2026-07-19. `rnd/structure-mapping-experiment` @ `fc9d0c14` carries an earlier one. This plan described both branches as "scaffolding" and the item as "unrun," which is what G-1 said, which is what the ADR's §5 status implied. All three were wrong on the same point for nine days.

Neither verdict survives inspection — attempt 1 leaked the label into the embedding, and attempt 2 measured separability with `except ValueError: res = 1000.0`, a solver exception counted as a distance — so **the plan's conclusion was right and its premise was wrong**. Track A still needed doing; what it needed was not "run the experiment" but "run it under a binding criterion, and say what the existing verdicts are worth."

The mechanism is worth naming because it is H-9's, one level up: *work that finishes on an unmerged branch is invisible to every instrument that describes the project.* The register, the plan, and the ADR all read the same absence and inherited the same error. A branch tip is not a record.

### N-7 · The flag count is 28 of 32, not seventeen

`RuntimeConfig` is a single frozen dataclass with **32 boolean fields: 28 default `False`, 4 default `True`** (`allow_cross_language_recall`, `use_salience`, `discourse_planner`, `deduction_serving_enabled`). The assessment's "seventeen capability flags default off" understates the built-and-dark surface by eleven.

Whether all 28 are *capability* flags or some are policy/deployment flags is precisely the classification PR-5's register must make — which is the finding: **nothing in the repository currently distinguishes them**, which is why two counts of the same set differ by eleven.

---

## 1. The unit of work

Every item below is one PR unless marked otherwise. Standing discipline, unchanged:

- **Worktree first** — `git worktree add ../core-wt-<slug> -b <branch>` off `forgejo/main`; never share a working directory with a parallel agent.
- **Local gate before push** — `uv run core test --suite smoke -q` **in the worktree**, plus the PR's own new pins; `[Verification]:` line in the PR body naming the SHA and the command.
- **Base and diff against `forgejo/main`**, never local `main`.
- **Merge is Shay's** — green PRs sit until explicit merge authorization. Merge-commit, not squash, for stacked work.
- **Merge then clean up** — remote branch, local branch, and worktree deleted in the same motion.
- **Cleanup as you find** — unambiguously dead code adjacent to a change goes out with that change.
- **Scope size, not clock time** — S (one file, one pin), M (a subsystem or a doc + pins), L (cross-cutting or a new mechanism), XL (design invention).

Two categories of work are **not** mine to complete: rulings (Shay) and ADR ratifications (Shay). The plan's job is to make each of those cost one line — everything a ruling needs is prepared before it is asked for.

---

## 2. Wave 0 — Scrub & rule

**Goal:** convert fourteen open questions into fourteen settled constraints in a single review pass, so every later wave stops branching on unknowns.

### PR-0 · The ruling packet — `docs/assessment/50-rulings.md` · **M**

One document, one decision per section: the evidence (already in the cards, verified at `ed06dd64`), the **options**, my **recommendation with reasoning**, and **the exact diff that follows from each choice** so ruling is a one-word reply. Nothing in it is a recommendation to reverse a ratified decision.

| # | Ruling | Register | Recommendation carried in the packet |
|---|---|---|---|
| R-1 | CR-3 efferent action — deferred or out of telos | G-12 | **Explicitly deferred**, with the entry criterion named; the alignment posture is stronger stated than silent |
| R-2 | CR-4 temporal self-location — the stance on "now" | G-13 | Ship as a paragraph in the soak contract *before* the soak is re-run, so G-5 doesn't answer it by accident |
| R-3 | The F-6 accrual flag — bug or intended dormancy | G-6/H-6 | Decide the **set**, not the flag. N-6 moves this to **incomplete flag set**; dormancy stays coherent but now costs two docstring corrections |
| R-4 | Flag profiles — one-shot / eval / continuous-life | G-8/H-6 | Adopt the `CONTINUOUS_LIFE_CONFIG_FLAGS` pattern as the general mechanism; rule profiles as units. Scope is **28 flags**, not 17 (N-7) |
| R-5 | Identity enforcement authorization bar | G-11 | State the evidence that would authorize live refusal; scoring-without-blocking stays honest only while the path exists |
| R-6 | Non-text ingest — entry criterion or deferral | G-17 | Deferral **with** the falsification bench named as the standard the track must meet when it moves |
| R-7 | Register supersession — this directory vs `docs/gaps.md` + ratchet | H-9 | Supersede both; migrate the 7 OPEN ratchet items into G-5; mark the originals historical |
| R-8 | **Curriculum outcome-mix** — now the sole blocker of the throughput frontier (N-5) | G-10 | Options with measured consequences; four bands are queued behind this one ruling. Content policy, not engineering |
| R-9 | Soak **evidence standard** + cadence | G-5/N-4 | Commit the artifact and pin the digest (the contract's own unmet instruction); a ruled manual-plus-recorded cadence beats a cron line that silently doesn't run while the Mac sleeps |
| R-10 | PR #138 disposition | G-2/G-3 | **Merge it.** Measurement-only, no serving change; the fabrication *fixes* stay held. Its inventory is the baseline for the widening program |
| R-11 | Do the fabrications get a defensive gate before their fix ADR | G-2 | Offer "refuse to hold a reading outside the verified inventory" as an interim posture; wrong=0-or-refuse says yes, cost says measure first |
| R-12 | The two ratified-ADR record amendments — ADR-0146 (daemon) and ADR-0252 ("34 organs") | G-15/H-8 | Exact drafted text for both, in the packet. Neither changes a decision; both stop the record contradicting the code |
| R-13 | Wilson re-count authorization — accept that licenses may be demoted | H-1/G-19 | **Authorize.** A demotion is the mechanism working; the exposure is *already pinned in-repo* (`test_volume_honesty.py`), so this ruling is about applying it, not discovering it |
| R-14 | Gate-parity direction — raise CI to the local suite, or lower local to CI | N-3 | **Raise CI**, at a measured cost of 46s / 429 tests on the runner's own hardware. Honest framing: defense-in-depth for pushes that skipped the local gate, not a hole |

### PR-1 · The record amendments that need no ruling · **S**
The assessment directory's own corrections (N-1…N-7 applied to `30-gap-register.md`, `31-hindrance-audit.md`, `40-assessment.md`, including N-3 entered as **H-12**), the correction note on `docs/research/architecture-assessment-verification-2026-07-25.md`, and the stale Draft banner on `MIND-PHYSICS-BLUEPRINT.md`. **The two ratified-ADR amendments are deliberately *not* here** — they are drafted in full inside R-12 and land the moment that ruling comes back, because editing a ratified ADR is Shay's authority even when the edit changes no decision.

### Track A opens here (see §6) — the §5 experiment does not wait for Wave 1.

**Wave 0 exit:** every G/H entry has either a settled ruling or a named owner-wave. No later item is blocked on an unasked question.

---

## 3. Wave 1 — Delete

*The best part is no part. Small wave, disproportionate effect: after it, the code stops telling readers things that aren't true.*

### PR-2 · Delete the decoration · **S** · H-2
`DriveGradientMap` construction at `chat/runtime.py:716` and the class; `InhibitionMask`/`InhibitionOperator` exports from `core/physics/__init__.py`. Their *intents* are preserved in writing first: drive → the CR-2 design brief (G-4), the mask → the CR-1 ADR (G-14). **Verification:** the sabotage test in reverse — full `smoke` plus the deduction and cognition suites must be byte-identical before and after; a deletion that changes a surface means the object was not decoration and the PR is abandoned.

### PR-3 · Retire the dead instruments · **S** · H-9
`docs/gaps.md` → historical banner pointing at `30-gap-register.md`; substrate-liveness ratchet → historical, 7 OPEN items migrated into G-5; the phantom `L12` stratum dropped from the local map generator. Per R-7.

---

## 4. Wave 2 — Simplify & enforce

*Convert doctrine into failing tests. Every item here makes a guarantee mechanical that is currently maintained by attention.*

### PR-4 · Curated-suite membership ratchet · **M** · G-7 — **LANDED 2026-07-28, re-specified by N-9**
~~1. `smoke.yml`'s path set == `TEST_SUITES["smoke"]` — fails on drift in either direction.~~ **WITHDRAWN (N-9).** The surviving direction (`smoke.yml ⊆ TEST_SUITES["smoke"]`) has been pinned since before this assessment by `test_cli_smoke_suite_covers_ci_smoke_gate`; the symmetric version was written and reverted on 2026-07-25 (`50fa287d`) because `AGENTS.md:280` makes the workflows dead signals. This plan proposed re-adding exactly what a prior agent removed, with the reasoning recorded at the assertion site to prevent it.

**What landed instead:**

1. **Membership ratchet** — `tests/test_suite_membership.py` + `tests/full_only_baseline.txt`. Measured: **749 of 877** test files belong to no curated suite. The plan's original mechanism ("assign every orphan, or write 749 exclusion reasons") is hollow at that scale — glob topic-suites would satisfy it while changing nothing about what executes, which is the Third-Door objection this plan itself levels at G-7's first formulation. All four demonstrated incidents (#113, #136, negation, speculative-lifecycle) were caused by a **newly landed** orphan, never a legacy one. So the ratchet blocks new orphans, enforces the baseline in **both** directions (a promoted or deleted file must leave the list), and pins the count so bulk movement is a reviewed decision.
2. **The gate-guarding pin now runs on the gate** — `test_cli_test_suites.py` moved into `smoke`; it had lived in `fast`, which the pre-push gate does not run.
3. **The two false parity comments corrected** (R-14 option C's live half): `core/cli_test.py`'s audio block and `scripts/hooks/pre-push` step 1 both claimed an equality that has never held and twice sent readers hunting drift that is a design decision.

**Verification:** three sabotages, each observed red — a new unregistered test file, a stale baseline entry, and the parity pin demoted out of `smoke`. Remediation half (adding the ten to `smoke.yml`) is **not owed**: it buys observability, not gating.

### PR-5 · The flag-default register · **M** · G-8/H-6
`docs/specs/flag_register.md`: all **28** default-off flags plus the 4 default-on — current default, deliberate-posture vs accumulated-hesitancy, **what evidence flips it**, and named profiles (one-shot / eval / continuous-life) per R-4. Declared in the table, not the call site (ADR-0263 Rule 5). A pin asserts the register lists exactly the flags `core/config.py` defines — so a new flag cannot land unregistered. Includes the F-6 accrual resolution from R-3 and the N-6 docstring correction.

### PR-6 · Failing pins for three doctrine-level prohibitions · **M** · G-9 — **LANDED 2026-07-28**
(a) no-approximate-recall — a pin that fails if a cosine/ANN ranker is substituted on the recall path; (b) a bypass pin — governance not merely working when called, but *unbypassable*; (c) safety-pack non-swappability mechanically enforced. Each demonstrated red-then-green; a law with a pin that cannot fail is a hollow gate.

**Landed, and the verification pass this item mandated is why the three came out differently.** (a) was the real gap and worse than the register stated: the only import ban covered a single physics module, while `generate/realize/recall.py` — the actual recall path — asserted the law in its docstring with nothing enforcing it. Now scanned across five roots for banned ANN libraries *and* hand-rolled `cosine*` definitions. (b) is now exact: no function may construct `TurnVerdicts` without invoking `safety_check.check`, and every call must pass `self.safety_pack` (substituting the pack is a bypass that skipping-detection would miss). (c) was already well pinned — its gap was **reach**: a fail-closed safety contract running in no curated suite, verified only after merge. Promoted onto the gate. **Four sabotages, each observed red**, each caught by its own pin.

### PR-7 · The M2 trust-boundary table · **M** · H-7 — **LANDED 2026-07-28**
Formation's six-boundary standard written for `ingest/gate.py` in `runtime_contracts.md`. **Documentation first** — the table's job is to expose real deltas at the surface facing untrusted user text; hardening PRs follow only where deltas are real, and are separate PRs.

**Landed, and the table's value turned out to be as much in what it closes as in what it opens.** Measured at `edf6c2a4`: two boundaries **already met** (no floats in hashed payloads, no pickle), three are **category differences** (content-addressing, self-sealing, source allow-list all presuppose a persisted artifact with citations — formation validates what it stores, the gate transforms what it does not), and **one is a real delta**: no audit record per rejection. Recording the three as closed is the load-bearing half; as owed obligations they would have generated three fake hardening tasks. The surviving delta is forensic, not containment (refusal is fail-closed), and is the same failure class PR-9 just closed on the turn spine.

### PR-8 · Materialise the typed refusal · **M** · H-3/G-20 — *needs a small ADR (the ADR-0024 chain reserved the seam)*
`InnerLoopExhaustion`'s reason/region/rejected-attempt evidence reaches `ChatResponse.refusal_reason` and a minimal honest served surface, instead of `""`. **Verification:** a refusing turn serves a non-empty, typed, replayable refusal, and `trace_hash` behavior is unchanged for non-refusing turns.

### PR-9 · Count the swallow · **S** · H-11 — **LANDED 2026-07-28**
A telemetry field on the turn/idle accrual result when `_accrue_in_turn`'s broad guard fires. **Behavior unchanged by construction** — the backstop stays; it stops being invisible.

**Widened to the same failure class elsewhere on the spine** (external-assessment triage): the logos-authority block's bare `except Exception` (`core/cognition/pipeline.py:555`) and the three layered OOV-probe swallows (`:605-657`) get the same remedy shape — record `probe_error = repr(e)` in the telemetry, keep the backstop. Observability that fails silently cannot distinguish "probe ran, found nothing" from "probe crashed first," which poisons the very roadmap data the OOV block exists to produce. **Explicitly not the narrow-catch alternative** (catching only `ImportError`/`OSError`): that converts a malformed decision object into a turn-spine crash — trading silent failure for served-surface failure.

**Landed.** All three instances instrumented; `_last_turn_accrual` still becomes `None` so every consumer is byte-identical (additive by construction, and pinned). `tests/test_accrual_swallow_telemetry.py` — 7 pins, the two behavioral ones **observed red** against a build with the fields present but the recording stripped. Registered in both gates on creation; delta unchanged at ten.

### PR-10 · Extend declared precedence to the composer arms · **L** · H-4 — *refactor ADR*
Lift `core/cognition/surface_resolution.py`'s declared-precedence pattern to arm selection in `chat/runtime.py`. **Do this while one arm is live** — the cost triples after the next three arms. Carries an in-code prospective sabotage note in the `surface_resolution.py` style. **Verification:** byte-identical serving on the full deduction + curriculum + register lanes; this refactor may not change a single served surface.

**Wave 2 exit:** every doctrine in AGENTS.md that this assessment found unenforced is enforced by a test that has been observed failing.

---

## 5. Wave 3 — Accelerate the evidence loops

*Carry built machinery to verdict. This is where the assessment's cultural finding — "this project finishes machinery and defers ceremonies" — gets reversed.*

### PR-11 · The L10 soak to a **committed** artifact · **M** · G-5/N-4
The run is known to pass at 5000 beats (N-4). The deliverable is therefore the ceremony the machinery never got: re-run at the contract's long horizon, **commit the report**, **pin the `deterministic_digest`** so a regression flips it (the contract's own unmet closing instruction), schedule per R-9, and promote the H1–H4 holds/bites pins into a curated suite (which PR-4 makes visible). If a hold *bites* at a longer horizon than 5000 beats, that is the highest-value result in this wave and it stops the wave.

### PR-12 · The Wilson re-count · **L** · H-1/G-19 — *ADR amendment (0175/0263 lineage), authorized by R-13*
Distinct-evidence counting at the seal boundary: a replay refreshes, never increments. Declared in the ledger schema. Then re-count the 25 ratified bands and **apply the demotions honestly** — 21 fall short, a number already pinned in `test_volume_honesty.py` "in BOTH directions," so that pin moves in the same PR. Expect served capability to shrink. **Verification:** the re-count is a pinned computation, not a spreadsheet; the demoted bands' licenses are revoked in the same PR.

### ~~PR-13 · Curriculum query-scoping~~ · **WITHDRAWN** · N-5
Shipped as ADR-0264 R5, discharged 2026-07-26. The 16-premise cap does not exist in the running system. G-10 is re-scoped to R-8 alone.

### PR-14 · The earning ledger · **M** · G-10
`chat/data/curriculum_serve_ledger.json` exists and is an *earning* ledger, under R-8's outcome-mix ruling. Four bands qualify the moment it is sealed (N-5). Depends on PR-12 (counting basis) and on R-8 — **no longer on any engineering prerequisite**.

### Track B · The fabrications and the widening — *gated, see §6*
G-2's fix lands only under its ratified ADR (R-11 may add an interim defensive gate first). G-3's widening program is **shape-dependent on Track A's verdict** and does not start before it.

---

## 6. The five frontiers as tracks

Waves are hygiene and enforcement. The frontiers are the project. Track A runs **in parallel with Wave 0**, because it is execution-authorized already and everything else gets cheaper once it returns.

### Track A · **Run ADR-0252 §5 to a verdict** · G-1/H-10 · **DONE 2026-07-28 — NO-GO, awaiting ratification**
Protocol followed as written: criterion pre-registered at `299c92be` **before** the run (that commit carries the thresholds as importable constants and no results); corpus built with provenance on every case; full experiment run; `docs/research/sme-experiment-verdict-797ebad5.md` written with the criterion, the run, the numbers, and the verdict; report artifact committed with a pinned `deterministic_digest`.

**Verdict: NO-GO**, and it is the well-controlled kind the ADR pre-declares as full credit. Structure-sensitivity fails at every attribute weight tested — not a knife-edge on a constant. The mechanism is stated in one sentence and measured rather than argued: *the similarity quotient that would deliver attribute-invariance is the same quotient that annihilates structural contrast.* An `add`-vs-`subtract` minimal pair — one entity, identical numbers, one relation kind changed — aligns at residual exactly `0.0`, its two configurations being related by a proper rotation. Sweeping the attribute weight, every regime in which the SME property survives is a regime in which attributes contribute nothing (AUC 1.00 → 0.83 → 0.69 as they start to matter).

**Scope, deliberately narrow:** this refutes H1 for embeddings that encode role-structure as *point positions* aligned by conformal Procrustes *under similarity* — the argument is about the quotient, so it generalises across that class. It does not refute every Cl(4,1) representation, and it does not touch the symbolic structure-mapping lane already in `evals/structure_mapping/`.

**Two things the track found that were not on anyone's list.** (1) The experiment was **already run twice**, returning GO twice, on unmerged branches — see N-8; both verdicts are unsound and are voided by the verdict document. (2) The math reader decides **5 of 500** `holdout_dev/v1` cases (1.0%), all one skeleton, which is why §5.1's four-structure corpus was not extractable and is now registered as **G-21**.

### Track B · **The reading** · G-2 → G-3 · **XL**
Sequenced and gated: merge #138 (R-10) → fabrication ADR + ratification → the two known mutations land → **then** widen from 19, in whatever shape Track A's verdict dictates. G-16's latent defect class in `_inflect_predicate`'s aspect arms must be cleared *by* the widening program, not after it. This is the intelligence frontier and the largest capability gap to the telos.

### Track C · **The chooser** · G-4 · **XL** · *the only frontier requiring genuine invention*
Deliverable order: a design brief (what may an agenda rank, what governs it, what forbids it from becoming a goal-seeking optimizer under the alignment posture) → ADR → implementation. Deliberately **last** to start and never automated into the daemon until Wave 2's enforcement and the F-6 resolution exist. Wave 1 deletes its decoration precisely so the design starts from an honest empty seat.

### Track D · **The proof of life** · G-5/G-6/G-13 · covered by PR-11 + R-2/R-3/R-9. Cheaper than the assessment priced it (N-4): the run passed; the ceremony is owed.

### Track E · **The throughput** · G-10/H-1/G-19 · covered by PR-12/PR-14 + R-8. **Now a single ruling wide** (N-5): the engineering blocker was discharged 2026-07-26, and four bands are queued behind the outcome-mix ruling alone.

---

## 7. Dependency graph

```
Wave 0 (rulings) ──┬─→ Wave 1 (delete) ──→ Wave 2 (enforce) ──→ Wave 4 (automate)
                   │                            ↑                      ↑
                   ├─→ Track A (§5 verdict) ────┼──→ Track B (widen)   │
                   │        (starts NOW)        │         ↑            │
                   ├─→ PR #138 merge ───────────┴─────────┘            │
                   ├─→ Wave 3 (evidence: soak, re-count, ledger) ──────┤
                   └─→ Track C (chooser design) ───────────────────────┘
```

Hard gates, non-negotiable:
- **Track B widening ⟸ Track A verdict.** Widening under the wrong paradigm is the most expensive possible mistake in this plan.
- **Track B fixes ⟸ the fabrication ADR.** Standing instruction; serving-path truth behavior is ratification territory.
- **Wave 4 ⟸ F-6 resolved (R-3) *and* Track C exists.** An always-on process consolidating an empty set is the mastery framework's "garbage at high speed," and CORE came within one flag of it.
- **PR-14 ⟸ PR-12 and R-8.** A ledger built on the old counting basis would have to be rebuilt; a ledger sealed without the mix rule licenses four bands on non-commitments.

---

## 8. Risks, stated before they are incurred

| Risk | Where | Mitigation |
|---|---|---|
| **The re-count demotes served capability** | PR-12 | This is the mechanism working, pre-authorized by R-13. The alternative — licenses the evidence never supported — is the exact failure the architecture exists to prevent. Report demotions as a headline, not a footnote. |
| **A soak hold bites past 5000 beats** | PR-11 | Stop the wave and report. A bitten hold is the most valuable result available; the harness was built to produce it. N-4 lowers the probability, not the value. |
| **Deleting decoration removes something live** | PR-2 | Byte-identical output across three suites before/after; abandon on any delta. |
| **Gate parity slows the observability run** | PR-4 | Measured: +46s / 429 tests on the runner's own hardware. If unacceptable, the ruling is which pins are *demoted*, made explicitly rather than by drift. |
| **The composer refactor changes a served surface** | PR-10 | Zero-delta requirement on the live lanes; the refactor is structural or it is abandoned. |
| **Track A returns an ambiguous verdict** | Track A | Criterion written **before** the run. Ambiguity is then a NO-GO by default, not a re-run with a new bar. |
| **Sealing a ledger licenses four bands on non-commitments** | PR-14 | Blocked on R-8 by construction; the mix rule is the license's precondition, not its follow-up. |
| **The plan itself decays** | all | Every PR body carries `[Verification]:` with a SHA; every card touched gets its `verified_at` bumped. A stale `verified_at` is testimony, not evidence — the N-4 finding is exactly this failure caught in-flight. |
| **Scope creep into Track C** | Track C | It stays a design brief until Waves 0–2 are closed. Invention is the one thing here that cannot be rushed by discipline. |

---

## 9. Definition of done

The arc closes when:

1. Every G-1…G-21 entry is CLOSED, or DEFERRED-WITH-RULING with the ruling recorded in-register.
2. Every H-1…H-14 entry is resolved, relocated to its better home, or explicitly accepted with a reason.
3. ADR-0252 §5 has a recorded verdict and the §6 question is settled either way.
4. A **committed** L10 soak artifact exists with a **pinned `deterministic_digest`**, and its pins run on a ruled cadence.
5. `smoke.yml` and `TEST_SUITES["smoke"]` are mechanically identical, and no test file hides in `full`.
6. The flag register exists and lists all 32 `RuntimeConfig` booleans, with no flag in `core/config.py` unlisted.
7. No document **and no docstring** in the repository contradicts the code at a load-bearing point.
8. Every card in `docs/assessment/` carries a `verified_at` no older than the last arc that touched its layer.

**What does *not* close with this arc:** the widening program (G-3) and the chooser (G-4). Those are the next arc, and they should be entered with the registers clean, the paradigm decided, and the evidence loops turning — which is precisely what this plan buys.

---

*Sequenced per `docs/conceptualizing_engineering_mastery.md`: scrub, delete, simplify, accelerate, automate last. Nothing above optimizes a thing that Wave 1 might delete, and nothing above automates a loop that Wave 3 has not proven turns. Seven corrections in §0 were found by reading code, workflows, and ADR supersession banners — none by re-reading the assessment.*
