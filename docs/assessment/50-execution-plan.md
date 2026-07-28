# The Execution Plan

**Planner:** Opus 5 · 2026-07-27 · verified at `forgejo/main` @ `ed06dd64`
**Governs:** everything in `30-gap-register.md` (G-1…G-21) and `31-hindrance-audit.md` (H-1…H-14), sequenced by `40-assessment.md` §6.
**Method:** `docs/conceptualizing_engineering_mastery.md` — scrub → **delete** → simplify/enforce → accelerate → automate last. Nothing is automated that Waves 0–3 have not proven.
**Status (2026-07-28, at `d0bedfc1`):** **Wave 0 is closed.** Twelve rulings adopted, two stricken, the §5 NO-GO ratified — recorded in `50-rulings.md`. Every plan item that needed neither a ruling nor an ADR was already landed; the ruling-gated items are now *unblocked and owed*, in the order fixed in §2.1 below.

| Landed | Blocked, and on what |
|---|---|
| PR-0 ruling packet (#140) · PR-1 record amendments · R-10 discharged (#138 merged) · **R-12 — both ADR amendments + the §5 verdict banner + the §6 retirement amendment** | PR-2 — CR-1/CR-2 design briefs that do not yet exist (**not** a ruling) |
| **Track A — ADR-0252 §5 run to NO-GO**, criterion pre-registered, artifact + digest committed, **verdict ratified 2026-07-28** | PR-8 — a small ADR (H-3/G-20) · PR-10 — a refactor ADR (H-4) |
| PR-4 membership + reachability ratchets · PR-6 three doctrine pins · PR-7 M2 trust table · PR-9 count-the-swallow · **PR-5 the flag register (R-3+R-4)** | PR-12 — an ADR **amendment** (R-13 authorizes it; the amendment is still owed) |
| PR-3 + PR-3b (**R-7**, Wave 1) · **PR-11 the soak to committed evidence (R-9+R-2)** · H-13 · H-8e · G-22 · G-23 | Track B — the fabrication ADR (standing instruction, unchanged) |
| **Closed:** G-5, G-6, G-7, G-8, G-9, G-10, G-15, G-19, G-22, H-1, H-6, H-7, H-8 (**all five**), H-11, H-13 · **Answered:** G-1 · **Discharged:** H-10 · **Pinned:** G-23 | Track C — invention, deliberately last |

**New this arc, not in the original assessment:** **N-8** (the §5 experiment had already returned GO twice, on unmerged branches, both unsound), **N-9** (the gate "drift" was a recorded decision — PR-4's pin 1 **withdrawn** rather than built, R-14 dissolved), **G-21** (the math reader decides **1.0%** of `holdout_dev/v1`), **G-22** (`main` was red before the arc, and `CLAIMS.md` published a superseded evidence digest for two days), **H-13**, **H-14**, **H-8e**.

**What has not moved, stated plainly:** comprehension breadth. The reader is still 19 constructions wide and decides 1.0% of the held-out corpus. *(Proof-of-life has moved: the soak is committed evidence with a pinned digest and a change-triggered cadence as of PR-11.)* Everything landed this arc is enforcement and evidence machinery. PR-11, PR-12, PR-14 and Track B are where capability moves — and after the rulings, **none of them is blocked on a question any more.** Three are blocked on work.

**The one strategic finding of the whole arc, stated once here so it is not lost in the registers:** every defect found this arc — G-22, H-13, H-14, N-8, N-9, the fourteen `PENDING` statuses, the four unused suite aliases, the fifteen unreachable ones — is a **record/reality divergence**, not a substrate defect. Nothing found says the geometry is wrong. The recurring class is **mechanisms whose failure state is indistinguishable from their success state**: a suite nobody runs, a pin nobody sees fail, a digest nobody re-derives, a verdict on an unmerged branch, a ruling adopted in conversation. That is what Waves 1–2 are for, and it is why the correct response to "too much going on" is deletion and enforcement rather than redesign.

---

## 0. Nine corrections to the assessment, found while sizing and executing this plan

The assessment's authority rests on its self-correction chain — *"nothing in the chain was ever caught by re-reading documents"* (§8). Planning it produced seven more and executing it produced two, all caught by reading code, workflows, branch tips, and the ADRs' own supersession banners. Six of them change planned work: two change the design of the highest-leverage mechanical item, one **deletes a Wave-3 PR** because the work already shipped, one **halves the severity** of a claim this plan made in its own first draft, one **withdraws a pin** this plan proposed re-adding after a prior agent had removed it for recorded reasons, and one **re-scopes a whole track** from *run the experiment* to *run it soundly*.

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

**Wave 0 exit:** every G/H entry has either a settled ruling or a named owner-wave. No later item is blocked on an unasked question. **Met 2026-07-28.**

---

## 2.1 The adopted docket — twelve rulings, and the order they execute in

**Ruled 2026-07-28 by Shay, explicitly.** Full text, options, and per-option diffs stay in [`50-rulings.md`](50-rulings.md); this section exists so the *plan* carries the order and the consequences, and so neither survives only in a conversation. (It did survive only in a conversation for several hours — see the note at the head of the ruling packet. That is the failure mode this arc is about, committed inside the arc.)

**Adopted:** R-1 A · R-2 B · R-3 A · R-4 A · R-5 A · R-6 A · R-7 A · R-8 C · R-9 A · R-11 B · R-12 A/A · R-13 A
**Stricken:** R-10 (discharged before the arc — #138 merged) · R-14 (dissolved by N-9)
**Also ratified:** the ADR-0252 §5 **NO-GO** verdict.

### The order, and why it is this order

The packet's original order was by register number. That is the wrong axis: it interleaves cheap record repairs with expensive capability work and puts the two ADR-record amendments last, when they are the only items that cost nothing and unblock reading everything else. The corrected order is **by what each item unblocks, cheapest first inside each tier.**

| Rank | Ruling(s) | Deliverable | Size | Why here |
|---|---|---|---|---|
| 1 | ~~**R-12**~~ | Two ratified-ADR record amendments — ADR-0146 (daemon) and ADR-0252 ("34 organs" footnote) — **plus** the §5 verdict banner and the §6 retirement-condition amendment, landed in the same edit | **S** | **EXECUTED 2026-07-28.** Zero-risk, changed no decision. Closed **H-8(a)** and **H-8(b)**, and discharged Track A's outstanding obligation. |
| 2 | ~~R-7~~ | ~~Register supersession~~ | — | **EXECUTED** — PR-3 + PR-3b, landed 2026-07-28. Listed so the order stays readable. |
| 3 | ~~**R-3 + R-4**~~ | PR-5 — the flag register, all 32 booleans classified, profiles as units, the bidirectional pin, `accrue_realized_knowledge` into the daemon profile | **M** | **EXECUTED 2026-07-28.** Closed **G-6, G-8, H-6, H-8(c), H-8(d)** — and **H-8 in full**. The N-6 docstring correction **dissolved**: the docstrings were right and the code was incomplete. **Wave 4's hard gate is lifted.** |
| 4 | ~~**R-9 + R-2**~~ | PR-11 — the soak re-run at 5000 beats under the **corrected** profile, artifact committed, digest pinned, cadence enforced by a source-hash pin, H1–H4 on the gate | **M** | **EXECUTED 2026-07-28.** Closed **G-5**. R-2 landed in the contract *before* the re-run, as designed. The staleness pin **would have caught PR-5** — verified by sabotage. |
| 5 | ~~**R-13**~~ | PR-12 — distinct-evidence counting at the seal boundary, the honest re-count, demotions applied, the producer hardened against re-padding | **L** | **EXECUTED 2026-07-28. 25 licensed bands → 4.** Served capability shrank by 21 bands and `wrong` stayed 0: no answer changed, only the claim attached to it. |
| 6 | ~~**R-8**~~ | PR-14 — the outcome-mix rule as two capabilities. **No ledger sealed: under the rule, zero bands license** | **M** | **EXECUTED 2026-07-28.** Overturns N-5 — the four bands cleared only on *pooled* evidence, by 0.000046. Closed **G-10**. |
| 7 | **R-1 · R-5 · R-6 · R-11** | Posture statements: efferent-action deferral with entry criterion (G-12) · the identity-enforcement discrimination bar (G-11) · non-text ingest deferral with the falsification bench as its standard (G-17) · **R-11 B — measure before gating** | **S** each | All four are prose with a criterion. None blocks anything; leaving them silent is the cost. They go last because they are the only items where lateness is cheap. |

**R-11's measurement is owed now, not later — and R-11 is the one adopted ruling that does not end in a decision.** Option B is *measure first, then re-ask*: an instrumentation PR (counts only, no behavior change) reporting how often the out-of-inventory reading path is taken on the practice corpora, after which **R-11 is put back to Shay with the number in hand.** So the docket owes two things here, not one: the measurement, and the second ruling. Until the number exists, R-11 has been ruled and nothing follows from it — which is a state worth naming, because a ruled-but-inert item is indistinguishable from a settled one at a glance. It lands with the R-1/R-5/R-6 batch at the latest and may land sooner, since the instrumentation is small and independent.

### Two items the docket added that were not rulings

**The claims register — HELD, deliberately, on my recommendation.** Proposed in the same message as the adoptions: a register mapping each pinned claim to the lane that verifies it. It is a good idea and it is **not scheduled yet.** The reason is G-22: `CLAIMS.md` published a superseded evidence digest for two days because one commit updated the lane and the verifier but not the published claim. A register built *now* would be a second surface with the same failure mode and no evidence yet that the first one holds. **Entry criterion:** it is scheduled once Wave 1's deletions and Wave 2's ratchets have gone one full arc without a record/reality divergence being found by hand. Building the index before the indexed things are trustworthy is exactly the pattern H-9 names.

**Gate width — promoted to a first-class plan item.** See PR-4b in §4. It was a parenthetical ("still open, and it is a decision") and parentheticals are how the fifteen got there.

---

## 3. Wave 1 — Delete

*The best part is no part. Small wave, disproportionate effect: after it, the code stops telling readers things that aren't true.*

### PR-2 · Delete the decoration · **S** · H-2
`DriveGradientMap` construction at `chat/runtime.py:716` and the class; `InhibitionMask`/`InhibitionOperator` exports from `core/physics/__init__.py`. Their *intents* are preserved in writing first: drive → the CR-2 design brief (G-4), the mask → the CR-1 ADR (G-14). **Verification:** the sabotage test in reverse — full `smoke` plus the deduction and cognition suites must be byte-identical before and after; a deletion that changes a surface means the object was not decoration and the PR is abandoned.

### PR-3 · Retire the dead instruments · **S** · H-9 — **LANDED 2026-07-28** (R-7 ruled A)
`docs/gaps.md` → historical banner pointing at `30-gap-register.md`; substrate-liveness ratchet → historical, 7 OPEN items migrated into G-5; the phantom `L12` stratum dropped from the local map generator. Per R-7.

**Landed.** Both banners written, naming *why* rather than just *what* — H-9's mechanism (an authoritative-looking instrument converts "I should check" into "I already checked") is quoted in the banner it explains. All seven OPEN ratchet items (**W-003, W-005, W-007, W-008, W-009, W-017, W-018** — every one L10-chained) migrated into G-5 with their dependency chains intact, because that reasoning is the ratchet's lasting contribution and its status column is not.

**One deliverable could not be executed as written, and is recorded rather than claimed:** `L12` has **no in-repo generator to drop it from**. The system map is local and gitignored (D5: a regeneratable index carrying no authority), so the phantom existed only in that local artifact and in one taxonomy row. The row now records the ruling instead of the flag.

### PR-3b · Collapse the suite aliases · **S** · *new, Wave 1* — **LANDED 2026-07-28**
Not in the original plan. Added when PR-4's two ratchets made the question unavoidable: *what exactly are they policing?* Measured — **21 curated suites, 9 holding exactly one file, 12 holding ≤4, and 2 reachable from any gate.**

The cut is much smaller than the sprawl suggests, and the measurement is why. `cognition`, `teaching`, `packs`, `algebra` are named in **AGENTS.md's own pre-merge-gate instruction**; `fast`, `pulse`, `proof` in the CLI's help text; `phase5`, `phase6`, `adr-0024`, `math`, `formation` in READMEs and ADRs. Deleting those breaks documented commands — worse than the sprawl.

**Four suites had zero `--suite` references anywhere in code, docs, ADRs, workflows or CLI help: `refusal`, `margin`, `rotor`, `inner-loop`.** Per-phase ADR-0024 aliases offered so reviewers could run a phase independently; nothing ever did. All seven of their files remain covered by `adr-0024`, so **nothing was orphaned and no coverage moved** — verified before the cut, not after.

**21 → 17 suites.** Pin 3's gate-unreachable gap went **19 → 15 by deletion**, which costs no gate time — the ratchet turning the way it should. An alias nobody calls is not a curation decision; it is one more name that has to be kept true, and two ratchets were policing these.

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

**STILL OWED — a third pin, found by this arc's own full-tree run (G-7 reopened-partly).** The ratchet closes membership; it does not close **execution**. The run found `tests/test_ratification_ceremony.py` red on `main`, **in a curated suite (`teaching`) that no gate invokes** — the gate runs `smoke` + warmed_session + `deductive`. Membership was satisfied and bought nothing, which is this item's own hollow-gate objection turned on its own fix. **Pin 3 — LANDED 2026-07-28**, `tests/test_suite_reachability.py`. Measured **21 curated suites, 2 gate-reachable**; the gap is **19**, not the handful first estimated. Shipped as baseline + ratchet for the same reason the membership pin was: 19 justifications written in one sitting is ceremony, not a decision. Freezes the gap, fails on growth, both directions enforced, declared gate set verified against `pre-push`/`local-ci.sh` so it cannot go vacuous. Two sabotages observed red.

### PR-4b · Gate width — which of the fifteen go on the gate · **S** · *new, Wave 2* · G-7

Promoted out of a parenthetical in PR-4, because a parenthetical is how fifteen suites got to be unreachable without anyone deciding it. Pin 3 froze the gap; **it deliberately does not choose**, and an unmade choice does not improve by being frozen.

**The decision, stated so it costs one reply.** The gate today is `smoke` + warmed_session + `deductive`. Fifteen curated suites have members and no gate caller. Every promotion costs gate time on every push, forever, which is why this is Shay's and not mine.

**Recommended first promotion: `teaching`, alone.** The evidence is not a preference — it is G-22: `tests/test_ratification_ceremony.py` was **red on `main`**, was **in `teaching`**, and no gate ran it. That is the only suite in the fifteen with a demonstrated escape. Promote it, measure the added wall-clock, and let the next promotion be argued from that measurement rather than from taste.

**Explicitly not recommended:** promoting all fifteen. That is the ceremony failure this plan rejected twice already (749 exclusion reasons; nineteen justifications in one sitting). Nor is deletion the default — PR-3b deleted the four with *zero* references anywhere; the remaining fifteen are all named in AGENTS.md, CLI help, READMEs or ADRs, so deleting them breaks documented commands.

**LANDED 2026-07-28 — and the recommendation was re-derived rather than executed, because its original justification had been spent.**

This item recommended `teaching` on the strength of G-22: `test_ratification_ceremony.py` was red on `main`, in `teaching`, run by no gate. **That hole was already closed a different way** — G-22's fix promoted that single file into `smoke`. So `teaching` would have added **9 net-new files, none with a demonstrated escape**, and promoting on a spent justification is the failure this arc exists to close.

**Promoted on a stronger, doctrinal basis instead.** `tests/test_epistemic_invariants.py` enforces AGENTS.md's *"Teaching and mutation safety"* non-negotiables in substance — INV-22/INV-23, that an unmarked proposal and an unmarked reviewed example default to **SPECULATIVE**, that the status enum has exactly its four positions, that pack-mutation proposals carry no hardening flag. Durable corpus mutation is the one irreversible thing in CORE, and the suite guarding it ran on no pre-merge gate. That justification does not depend on an incident having happened yet, which makes it the better one.

**Measured: 22.1s for 9 net-new files** (the tenth, `test_ratification_ceremony.py`, was already on the gate). Both invocation sites updated, `GATE_SUITES` extended, `teaching` removed from `UNREACHABLE_BASELINE` in the same edit, ratchet lowered `<= 15` → `<= 14`. **The reachability gap turned by promotion for the first time** — PR-3b's earlier turn was by deletion, which is free; this one costs, which is why it is a decision.

**A hollow spot in pin 3 itself, found by sabotage-testing the promotion.** `_suites_invoked_by_gate_tiers()` takes the **union** of `pre-push` and `local-ci.sh`, so a suite present in either satisfies it. Removing `teaching` from `local-ci.sh` alone **passed silently** — the two scripts could drift from each other invisibly, while `local-ci.sh` states in prose that it runs "the same four steps as `scripts/hooks/pre-push`." Closed by `test_the_two_gate_scripts_invoke_the_same_suites`, scoped to the numbered `(n/m)` gate steps so it reads the gate tier without parsing shell control flow. The identical sabotage now fires.

**This is not the CI-parity pin N-9 killed**, and the distinction is recorded at the assertion site so it is not re-litigated: that one asserted parity with `smoke.yml`, which `AGENTS.md:280` makes a billing-locked dead signal. Both scripts here are live local merge bars, and a developer running either is entitled to the coverage the other advertises.

### PR-5 · The flag-default register · **M** · G-8/H-6
`docs/specs/flag_register.md`: all **28** default-off flags plus the 4 default-on — current default, deliberate-posture vs accumulated-hesitancy, **what evidence flips it**, and named profiles (one-shot / eval / continuous-life) per R-4. Declared in the table, not the call site (ADR-0263 Rule 5). A pin asserts the register lists exactly the flags `core/config.py` defines — so a new flag cannot land unregistered. Includes the F-6 accrual resolution from R-3 and the N-6 docstring correction.

**LANDED 2026-07-28.** `docs/specs/flag_register.md` + `tests/test_flag_register.py` on the gate. All 32 booleans carry a class (**CAPABILITY** / **POSTURE** / **DEPLOYMENT**), a governing ADR or an honest "none", and *what evidence would flip it*. The classification is the load-bearing half: `estimation_enabled` and `composed_surface` are both `= False` and are not the same kind of thing, and nothing in the repository said so before. R-4's profiles are declared as the **unit of decision** — one-shot/eval and continuous-life — with the deliberate absence of a *serving* profile stated, since grouping the four POSTURE serving flags before the ledger is sealed would license by association.

**Three findings the item did not anticipate, all from measuring rather than reading:**

1. **Accumulated permissiveness.** Of the four default-ON flags, **one** has a governing ADR; **two have no recorded reason of any kind** — `allow_cross_language_recall` and `use_salience` carry no comment block, no ADR, no criterion. Registered, deliberately not fixed: inventing a rationale after the fact would fabricate a decision nobody made. Owed: one line each from whoever knows.
2. **A hollow gate inside the governance pin.** `test_default_on_flag_is_not_governed_by_a_proposed_adr` is parameterized over *(ON flag × cited ADR)*, so the three uncited ON flags produce **zero cases** — it covered one flag — while its non-vacuity guard only required that *some* flag cite an ADR, which default-off flags satisfy abundantly. One reformatted comment from zero coverage, fully green. Tightened, **observed red**.
3. **The daemon's own tests ran on no gate.** R-3 changes what the always-on process does every beat, and `tests/test_l10_always_on_daemon.py` was in no curated suite. Promoted with the change it guards — measured **+9.4s, +4.3% of smoke**, paid deliberately rather than estimated.

**Verification:** the R-3 assertion observed **red** before the flag was added; **four sabotages** on the register pin observed red, one caught by two independent pins; the tightened governance guard observed red by stripping ADR-0256's citation.

**One deliverable dissolved rather than shipping, and it is recorded rather than quietly dropped:** "the N-6 docstring correction." Both `core/config.py` docstrings already described the corrected profile, so adding the flag made them **true**. The documents were right about the intent; the code was incomplete. That is what R-3 A means, and a PR that silently ships less than it promised is the divergence class this plan exists to close.

**Consequence handed forward to PR-11:** the 5000-beat soak recorded in `evals/l10_always_on/contract.md` (2026-07-19) predates this change and **describes a configuration that no longer ships**. PR-11's re-run is the first soak of the corrected profile.

**Plus one page this PR is the natural home for (from the 2026-07-28 triage, proposal 6).** The repository's governing pattern is *declared in the table, not the call site* (ADR-0263 Rule 5) and it is implemented in many places — `GROUNDING_SOURCES`, `DOMAIN_PACKS`, `TEST_SUITES`, `GATE_SUITES`, `CONTINUOUS_LIFE_CONFIG_FLAGS`, the quarantine/slow registries, `PINNED_SHAS`. **Nobody can currently enumerate them, or say what enforces each.** That is a one-page index in the flag register's own document — *table → where declared → what pin makes it true* — and explicitly **not** a `contracts.toml` that centralizes them into a fifth copy needing agreement with four generators. The index is a reader's aid; the tables stay where their authority lives.

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
Distinct-evidence counting at the seal boundary: a replay refreshes, never increments. Declared in the ledger schema. Then re-count the 25 ratified bands and **apply the demotions honestly** — 21 fall short, a number already pinned in `test_volume_honesty.py` "in BOTH directions," so that pin moves in the same PR. Expect served capability to shrink. **Verification:** the re-count is a pinned computation, not a spreadsheet; the demoted bands' licences are revoked in the same PR.

**LANDED 2026-07-28. 25 licensed bands → 4; 21 demoted.** The four survivors are `en_conditional_chain`, `en_disjunctive`, `en_verb_fact`, `en_verb_universal` — the only bands whose corpus holds enough *independent* cases. The worst offenders inflated **28 distinct cases into 720 committed decisions**, taking `conservative_floor` from `0.808413` to `0.990868` and clearing θ_SERVE on evidence that never existed.

**What the demotion did and did not do, stated exactly:** no answer changed, no answer became wrong, `wrong` stayed **0** across all 25 bands. The engine is as correct as it was. What changed is the *claim* attached to the answer — 21 bands now serve the same sound conclusion with *"reasoned, but I haven't yet earned a verified track record on arguments of this shape."* **The reasoning did not get worse; the boast did.**

**The producer was hardened, which is the half that stops it recurring.** `seal_ledger` now refuses outright: `assert_sealed_evidence_distinct` compares the ledger about to be written against the corpus's distinct-case count and raises before anything is written. Curriculum's sealer has carried this guarantee since ADR-0264 R9; deduction's had no equivalent, which is exactly how the exposure arose.

**A hollow guard of my own, caught by sabotage rather than trusted.** The first version compared `all_gold_problems()` with `distinct_gold_problems()` — two functions that agree by construction, neither of which is what `build_ledger` folds. Reverting `build_ledger` to the raw corpus walked straight past it *and re-sealed the inflated artifact*. The guard now takes the **built ledger** as input, because the invariant is about the artifact. Re-run of the identical attack: refused, and **wrote nothing**.

**Four records corrected in the same PR**, each of which would otherwise have kept asserting the old capability: `CAPABILITY_LEDGERS`'s manifest note ("25 bands at 720/720"), the published `CLAIMS.md` claim (caught immediately by G-22's own pin), `test_volume_honesty.py`'s module docstring ("NOT silently repaired" — R-13 *is* that repair), and the exposure inventory's framing (it now pins the fix, not the gap). Eight tests encoded the unearned expectation and were updated to the honest one.

### ~~PR-13 · Curriculum query-scoping~~ · **WITHDRAWN** · N-5
Shipped as ADR-0264 R5, discharged 2026-07-26. The 16-premise cap does not exist in the running system. G-10 is re-scoped to R-8 alone.

### PR-14 · The earning ledger · **M** · G-10 — *unblocked by R-8 C*
`chat/data/curriculum_serve_ledger.json` exists and is an *earning* ledger. Four bands qualify the moment it is sealed (N-5). Depends on PR-12 (counting basis) — **no longer on any ruling and no longer on any engineering prerequisite**.

**Under R-8 C the deliverable is now specific:** two entries in `CAPABILITY_LEDGERS` — `unknown`-serving and `entailed`-serving licensed as **different capabilities on different evidence** — the mix rule declared in the table rather than at the call site (ADR-0263 Rule 5), an **ADR-0264 §5 amendment** recording the ruling, then the seal. The four bands license the thing they have actually demonstrated at 660 decisions (correct refusal); nothing licenses entailment on a maximum of 9 cases.

**It also carries G-23's decision, because it is the same band.** `DOMAIN_PACKS` places `en_core_cognition_v1` and `en_core_meta_v1` in `philosophy_theology`; neither manifest declares a `domain_id`, so `domain_contract_predicates` P3 has never run on them. The gap is pinned (`tests/test_domain_pack_binding.py`, on the gate, four sabotages red) and deliberately not fixed: whether those two are *philosophy_theology domain packs* or merely *grouped under it for ledger accounting* decides what the license actually covers. Sealing that band's ledger without answering it licenses a domain whose membership is asserted in one place and denied by silence in the other.

**LANDED 2026-07-28, and the result is the opposite of what this item predicted.**

**Split, zero bands license — not four.** The four leading bands hold **652–653 correct UNKNOWNs** and **7–8 entailments**. Pooled they reach 660 and clear θ_SERVE by **0.000046**; separated, neither half clears. `conservative_floor(9,9)` is **0.000000** — the Wilson bound at nine trials is not merely below θ, it is zero. The licence N-5 predicted was manufactured entirely by counting correct refusals and correct commitments as one kind of evidence.

**This is why the plan blocked PR-14 on R-8 rather than sealing first.** A ledger sealed on the pooled basis would have granted four licences the mix rule then had to revoke — and revoking a granted licence is the expensive direction, as PR-12 had just demonstrated across 21 deduction bands.

**No ledger is sealed, and that is the deliverable.** Under the rule there is nothing to license; the registered `missing_ok=True` absence states that once already. An artifact whose only content is its own emptiness would be a second statement of the same fact.

**The useful result is the *shape* of the gap, which pooling had hidden.** Non-commitment serving is **four to five distinct query atoms short per band**; entailed serving is **~648** short. Those are content tasks of completely different size, and a single pooled figure could not distinguish *"almost there"* from *"two orders of magnitude away."* Four cases is a morning's work; 648 is a program.

**Delivered:** `curriculum_serve_entailed` registered in `CAPABILITY_LEDGERS` (`missing_ok=True` — absent means nothing licensed, which is the honest state); an audit source for it, which the manifest's own pin demanded the moment the capability was declared; the **ADR-0264 §5 amendment** recording the ruling and correcting §4.1's "four bands would earn SERVE" expectation; and `tests/test_curriculum_outcome_mix.py` on the gate, pinning both capabilities, the shortfall, **and the counterfactual** — so the argument for the rule cannot drift away from the number it rests on.

**~~One sub-question the ruling leaves open~~ — RULED 2026-07-28 under the standing delegation: no new constant.** The packet's recommendation was *"C, with a floor from A applied to the entailed capability only"* — and **N was never named.** Adopting C adopts the floor in principle; the number is not derivable from the evidence, because the whole point is that no band is near it (max entailed volume = 9). This PR must therefore either carry a proposed N with its consequence measured, or land the two capabilities with the entailed one explicitly unlicensable-pending-N. It may not quietly ship without a floor — that would license entailment on 9 cases through an omission, which is the exact outcome C exists to prevent.

### Track B · The fabrications and the widening — *gated, see §6*
G-2's fix lands only under its ratified ADR (R-11 may add an interim defensive gate first). G-3's widening program is **shape-dependent on Track A's verdict** and does not start before it.

---

## 6. The five frontiers as tracks

Waves are hygiene and enforcement. The frontiers are the project. Track A runs **in parallel with Wave 0**, because it is execution-authorized already and everything else gets cheaper once it returns.

### Track A · **Run ADR-0252 §5 to a verdict** · G-1/H-10 · **DONE 2026-07-28 — NO-GO, RATIFIED 2026-07-28**
Protocol followed as written: criterion pre-registered at `299c92be` **before** the run (that commit carries the thresholds as importable constants and no results); corpus built with provenance on every case; full experiment run; `docs/research/sme-experiment-verdict-797ebad5.md` written with the criterion, the run, the numbers, and the verdict; report artifact committed with a pinned `deterministic_digest`.

**Verdict: NO-GO**, and it is the well-controlled kind the ADR pre-declares as full credit. Structure-sensitivity fails at every attribute weight tested — not a knife-edge on a constant. The mechanism is stated in one sentence and measured rather than argued: *the similarity quotient that would deliver attribute-invariance is the same quotient that annihilates structural contrast.* An `add`-vs-`subtract` minimal pair — one entity, identical numbers, one relation kind changed — aligns at residual exactly `0.0`, its two configurations being related by a proper rotation. Sweeping the attribute weight, every regime in which the SME property survives is a regime in which attributes contribute nothing (AUC 1.00 → 0.83 → 0.69 as they start to matter).

**Scope, deliberately narrow:** this refutes H1 for embeddings that encode role-structure as *point positions* aligned by conformal Procrustes *under similarity* — the argument is about the quotient, so it generalises across that class. It does not refute every Cl(4,1) representation, and it does not touch the symbolic structure-mapping lane already in `evals/structure_mapping/`.

**Two things the track found that were not on anyone's list.** (1) The experiment was **already run twice**, returning GO twice, on unmerged branches — see N-8; both verdicts are unsound and are voided by the verdict document. (2) The math reader decides **5 of 500** `holdout_dev/v1` cases (1.0%), all one skeleton, which is why §5.1's four-structure corpus was not extractable and is now registered as **G-21**.

**Ratified 2026-07-28, and it leaves one obligation the ADR itself cannot discharge.** ADR-0252 **§6 names an organ-retirement condition that a NO-GO makes unsatisfiable as written**: it retires the symbolic structure-mapping organs *on the strength of the geometric replacement*, and names **no replacement** for the NO-GO branch. A ratified NO-GO therefore has to be written back into the ADR or the ADR's §6 stands as a live instruction that can never fire — an instrument in the H-9 class, authoritative-looking and dead.

**DISCHARGED 2026-07-28, with R-12** — all three landed in one edit to ADR-0252, since they are one file under one authority and splitting them would have bought two reviews of the same document. The §6 bullet now reads *"the surface organs are RETAINED — that is the operative state, not a pause in a transition,"* and the §6 "Build" bullet is marked **NOT AUTHORIZED** with the reason. What was owed:
1. **§5 gains its verdict banner** — NO-GO, the run SHA, the report digest, the scope sentence (*point-position role encodings aligned by conformal Procrustes under similarity*, not every Cl(4,1) representation, and not the symbolic lane already in `evals/structure_mapping/`).
2. **§6's retirement condition is amended to state the NO-GO branch explicitly**: the symbolic organs are **retained**, and the condition that would retire them is re-stated as *a demonstrated replacement passing the §5 criterion*, which no longer exists. Retiring a working organ because a *hypothesis about its replacement* was written down is precisely backwards.
3. **The "34 organs" basis footnote** from R-12 lands in the same amendment — same file, same authority, one review instead of two.

*(Registered here rather than only in the verdict document because a verdict document is a research artifact and §6 is an instruction. The instruction is what has to change.)*

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
- ~~**Wave 4 ⟸ F-6 resolved (R-3)**~~ **— half-lifted 2026-07-28.** F-6 is resolved: the daemon now forces the producer (Step B) alongside the consumer (Step D), so the always-on process no longer consolidates an empty set. CORE shipped within one flag of the mastery framework's "garbage at high speed" for six weeks, guarded by tests no gate ran. **Wave 4 still waits on Track C existing** — that half of the gate is untouched.
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
5. ~~`smoke.yml` and `TEST_SUITES["smoke"]` are mechanically identical, and no test file hides in `full`.~~ **Superseded by N-9 and by PR-4's measurement.** Both halves were wrong. Gate parity with `smoke.yml` is not a goal — `AGENTS.md:280` makes the workflows dead signals, and the surviving direction has been pinned since before this assessment. And "no test file hides in `full`" is unreachable at 747 files without ceremony that changes nothing about what executes. **Replaced by:** the membership baseline only shrinks, the gate-unreachable baseline only shrinks, and both are enforced in both directions.
6. **At least one gate-unreachable suite has been promoted onto the gate by decision** (PR-4b), with the added wall-clock recorded as a number.
7. The flag register exists and lists all 32 `RuntimeConfig` booleans, with no flag in `core/config.py` unlisted.
8. No document **and no docstring** in the repository contradicts the code at a load-bearing point.
9. Every card in `docs/assessment/` carries a `verified_at` no older than the last arc that touched its layer.
10. **Every ruling in `50-rulings.md` carries a status that matches what has actually executed** — the arc's own closing check, added because for several hours it did not.

**What does *not* close with this arc:** the widening program (G-3) and the chooser (G-4). Those are the next arc, and they should be entered with the registers clean, the paradigm decided, and the evidence loops turning — which is precisely what this plan buys.

---

*Sequenced per `docs/conceptualizing_engineering_mastery.md`: scrub, delete, simplify, accelerate, automate last. Nothing above optimizes a thing that Wave 1 might delete, and nothing above automates a loop that Wave 3 has not proven turns. Nine corrections in §0 were found by reading code, workflows, branch tips, and ADR supersession banners — none by re-reading the assessment.*
