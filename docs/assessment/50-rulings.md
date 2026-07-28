# The Ruling Packet — Wave 0

**Prepared by:** Opus 5 · 2026-07-27 · every claim verified at `forgejo/main` @ `ed06dd64`
**Deciding authority:** Shay, for all fourteen.
**Contract:** each ruling below is prepared so that answering it costs **one word**. The evidence is gathered, the options are enumerated, a recommendation is made with its reasoning, and the exact change that follows from each option is written out. Nothing here recommends reversing a ratified decision; R-12 amends two ADRs' *records* without touching either decision.

**How to rule:** reply with the item and your choice — e.g. `R-1 A · R-3 B · R-8 C`. Anything left unruled stays `PENDING` and blocks only the wave named in its **Blocks** line.

**Status legend:** `PENDING` — awaiting ruling · `RULED` — decided, with the date and choice recorded inline · `WITHDRAWN` — the question dissolved before it was answered.

---

## R-1 · CR-3 efferent action — deferred, or out of telos?

**Status:** PENDING · **Register:** G-12 · **Blocks:** nothing; leaving it silent is the cost.

**The question.** CORE's telos ends at articulate/learn/replay. AGI-grade generality ordinarily implies acting on the world. No system-level statement exists either way.

**Evidence.** Typed deterministic tool operators are folded into `trace_hash` (ADR-0018) — so *some* efferent surface already exists and is governed. The environmental-falsification contract (ADR-0211) *explicitly forbids* motor/efferent units in v1 — a bench-level prohibition, not a system-level scope statement. Position paper §6's alignment posture is the relevant frame.

**Options.**
- **A — Deferred with an entry criterion.** Action is in scope eventually; nothing moves until the criterion is met.
- **B — Out of telos.** CORE is a comprehension-and-articulation engine by definition; efferent action is another system's job.
- **C — Leave unruled.** Status quo.

**Recommendation: A**, with the criterion stated as *"no efferent surface beyond typed, trace-folded tool operators until (i) the chooser (G-4) exists and is governed, and (ii) an efferent falsification bench exists at the standard `docs/specs/` sets for M2."* The alignment posture is *stronger* stated than silent — an unstated boundary reads as an unexamined one, and C is the only option that leaves a future reasoner guessing. B is coherent and cheap, but it forecloses a scope decision on a system whose chooser has not been designed yet; A costs nothing B does and preserves the option.

**What follows.**
- **A** → one paragraph in `AGENTS.md` scope + G-12 closed as DEFERRED-WITH-RULING, criterion recorded in-register.
- **B** → same locations, worded as an exclusion; CR-3 leaves the Candidate Register permanently.
- **C** → G-12 stays open and is re-asked at the next assessment.

---

## R-2 · CR-4 temporal self-location — the stance on "now"

**Status:** PENDING · **Register:** G-13 · **Blocks:** PR-11 (the soak's contract paragraph).

**The question.** A continuous life experiences sequence and duration; determinism bans clocks from cognition. Both commitments are correct and their intersection is undesigned. The 24h+ no-drift requirement cannot be *stated* precisely without a stance.

**Evidence.** What already exists and is not a clock: session-context ordering, engine-state `turn_count`, idle ticks as pseudo-time, and the Fibonacci recency constants schedule (τ_n, ADR-0242 — a constants schedule, not a clock). The soak already runs on beats, not seconds: `evals/l10_always_on` counts `n_beats`, and the recorded 5000-beat result (contract.md §"The measured result") has no wall-clock component at all.

**Options.**
- **A — Beats are the only time.** "Now" is the current beat index; "before" is a lower index; "how long" is a beat count. Wall-clock never enters cognition, and every continuity requirement is restated in beats.
- **B — Two clocks, one wall.** Beats govern cognition; a wall-clock stamp is recorded in telemetry only, never read by any cognitive path, enforced by a pin.
- **C — Defer to the L10 spike.** Let PR-11 answer it implicitly.

**Recommendation: B.** A is already how the system behaves and is the honest core of the answer — but the telos's own claim is *"24 hours without drift,"* which is a wall-clock claim, and a soak that cannot say how long it ran cannot evidence it. B keeps cognition clock-free (A's whole point) while making the *evidence* about the run legible, with a pin proving no cognitive path reads the stamp. C is the option the register explicitly warns against: *"the L10 spike gets designed with an implicit, accidental answer to a question nobody asked out loud."*

**What follows.**
- **A** → the soak contract restates H1–H4 in beats; the "24h" language leaves the telos docs and becomes a beat count.
- **B** → one paragraph in `evals/l10_always_on/contract.md` + a telemetry-only field in the committed artifact + one pin (`no cognitive module imports the wall-clock stamp`). Ships inside PR-11.
- **C** → PR-11 proceeds and G-13 is re-asked after the fact.

---

## R-3 · The F-6 accrual flag — incomplete set, or intended dormancy?

**Status:** PENDING · **Register:** G-6 / H-6 · **Blocks:** Wave 4 (hard gate), PR-5.

**The question.** `CONTINUOUS_LIFE_CONFIG_FLAGS` (`chat/always_on_daemon.py:45-49`) forces `persist_session_state`, `consolidate_determinations`, `strict_identity_continuity` — and **not** `accrue_realized_knowledge`. The only turn-path writer of realized facts sits behind the unforced flag. **As coded, the continuous life may consolidate an empty set.**

**Evidence — strengthened since the register was written (N-6).** Both flags' own docstrings in `core/config.py` assert the opposite of the shipped configuration:

> `accrue_realized_knowledge` — *"…the production L10 process enables it alongside `persist_session_state`…"*
> `consolidate_determinations` — *"…the production L10 process enables it alongside `accrue_realized_knowledge` + `persist_session_state`…"*

Two flags' documentation describes a production profile the production profile does not have. This is H-8's failure mode located **inside the source**, one layer below the documents. The 2026-07-25 verification doc makes the same claim (C-5).

**Options.**
- **A — Incomplete flag set.** Add `accrue_realized_knowledge: True` to `CONTINUOUS_LIFE_CONFIG_FLAGS`. The loop's writer and consumer become coherent; three documents stop lying.
- **B — Intended dormancy.** The daemon deliberately consolidates only what a *user turn* accrued. Then two docstrings and the 07-25 doc are corrected to say so, and the rationale is written down.
- **C — Dormant until the chooser exists.** B, with an explicit re-open condition tied to G-4.

**Recommendation: A.** Three independent records — two docstrings and a verification document — all describe A as the existing state. The most economical explanation of "everyone wrote A and the code does B" is that A was intended and one line was missed. B remains genuinely coherent (an always-on process that only consolidates *reviewed* accruals is a defensible conservatism), which is why this is a ruling and not a bug report — but B now costs three corrections, and B's rationale has never been written anywhere.

**What follows.**
- **A** → one line in `always_on_daemon.py`, a soak re-run under PR-11 to confirm the loop is non-empty at horizon, and the F-6 hard gate on Wave 4 clears.
- **B/C** → two docstring corrections + a correction note on the 07-25 doc + a recorded rationale; the Wave-4 gate clears *only* once the "consolidating an empty set" concern is answered on its own terms.

---

## R-4 · Flag profiles — one-shot / eval / continuous-life

**Status:** PENDING · **Register:** G-8 / H-6 · **Blocks:** PR-5.

**The question.** `RuntimeConfig` defines **32 boolean fields: 28 default `False`, 4 default `True`** (`allow_cross_language_recall`, `use_salience`, `discourse_planner`, `deduction_serving_enabled`). Three are daemon-forced. No document states the set, which defaults are deliberate posture versus accumulated hesitancy, or what evidence would flip each. *(The assessment said "seventeen"; the real number is 28 — N-7. Two counts of the same set differing by eleven is itself the finding: nothing in the repo distinguishes capability flags from policy flags.)*

**Options.**
- **A — Adopt profiles as the general mechanism.** `CONTINUOUS_LIFE_CONFIG_FLAGS` becomes one of three named, documented, individually-ruled profiles (one-shot / eval / continuous-life), declared in a register table per ADR-0263 Rule 5, with a pin that fails when `core/config.py` defines a flag the register does not list.
- **B — Register without profiles.** Document all 32 and what flips each; leave composition to call sites.
- **C — Defer.** Keep flags undocumented as a set.

**Recommendation: A.** The pattern already exists in-repo, is already correct, and is already applied to the wrong subset (H-6). B does the expensive half (classifying 32 flags) and skips the cheap half that prevents recurrence. The pin is what makes A permanent: after it, a new flag *cannot* land unregistered — which is the same mechanical-enforcement move as PR-4, applied to configuration instead of tests.

**What follows.**
- **A** → `docs/specs/flag_register.md` + three profile constants + one pin (PR-5).
- **B** → the register without profiles or constants; H-6 stays open.
- **C** → G-8 stays open; the largest lever in the system stays unregistered.

---

## R-5 · The identity-enforcement authorization bar

**Status:** PENDING · **Register:** G-11 · **Blocks:** nothing; it makes an honest posture *stay* honest.

**The question.** `identity_wave_gate` is off and `identity_action_surface` is off and documented as **"NOT authorized for live activation."** That is a deliberate, well-reasoned posture. What is missing is the *criterion*: no document states what evidence would authorize live refusal.

**Evidence.** `core/config.py` records the honest reasons: γ_id *"separates geometric attack signal from benign traffic poorly on the current nominal axis frame"* (ADR-0244 Phase 3 honesty notes), and the action surface's thresholds are *"UNCERTIFIED placeholders (only γ_id is certified)"* with a §6.3 discrimination report showing it *"refuses benign and adversarial traffic alike."* Scoring runs on the metric-exact wave path either way; the flag only controls whether a flagged score becomes a typed refusal.

**Options.**
- **A — Set a discrimination bar.** Live refusal is authorized when a stratified benign/adversarial corpus shows separation at a stated floor, with the corpus and floor named in advance (the δ=0.4 derivation is the in-repo template).
- **B — Set a frame bar.** Authorization requires a *certified* axis frame first; discrimination is measured only after.
- **C — Declare permanent scoring-only.** Identity enforcement never blocks; it informs.

**Recommendation: A**, with B's frame work named as its likely first blocker. A is falsifiable, matches how CORE has authorized every other gate, and — critically — makes the *current* off-state evidence-backed rather than indefinite. C is defensible but should not be arrived at by default.

**What follows.** Any of the three → one paragraph in `runtime_contracts.md`'s identity contract + G-11 closed. A additionally names the corpus and the floor.

---

## R-6 · Non-text ingest — entry criterion, or explicit deferral?

**Status:** PENDING · **Register:** G-17 · **Blocks:** nothing.

**The question.** 59 sensorium modules exist and reach no serving path. Projection heads do not exist. The position paper is honest about this. There is no entry criterion and no deferral ruling — so it reads as neither built nor deliberately postponed.

**Options.**
- **A — Deferral with the bench named.** Non-text ingest is deferred; when it moves, it must meet the falsification bench's standard (closed verdicts, first-sentence non-goals, checksummed evidence — the M2 standard §3 of the assessment calls *"what a v1 should look like"*).
- **B — Entry criterion now.** Name the first modality, its serving path, and its pins; schedule it.
- **C — Leave unruled.**

**Recommendation: A.** The audio lane is already in the smoke gate — six files, ~3s — so the *bench* exists and is proven; what does not exist is a reason to widen it now, with the reading frontier (Track B) unresolved and 19 constructions wide. A costs one paragraph and converts 59 modules from "unexplained absence" to "deferred with a standard," which is exactly the scripture-content model the register names as correct.

**What follows.**
- **A** → one paragraph in the position paper + G-17 closed as DEFERRED-WITH-RULING.
- **B** → a scoped track, competing with Tracks A–C for the same attention.
- **C** → G-17 recurs.

---

## R-7 · Register supersession — this directory vs `docs/gaps.md` and the ratchet

**Status:** PENDING · **Register:** H-9 · **Blocks:** PR-3.

**The question.** `docs/gaps.md` is 26/26 closed with no entry from any 2026-06+ arc. The substrate-liveness ratchet is v5, stale since ~2026-05-24, with **7 OPEN items, all L10-chained**. The local system map is gitignored, 48 days stale, and carries a phantom `L12` stratum that exists nowhere else. Two dead registers plus a live one is worse than one live one.

**Options.**
- **A — Supersede both.** `30-gap-register.md` becomes the live register; `docs/gaps.md` and the ratchet get historical banners pointing at it; the ratchet's 7 OPEN items migrate into G-5; `L12` is dropped from the map generator; the assessment directory becomes the standing ruled record with `verified_at` stamps.
- **B — Revive the ratchet.** Keep it as the liveness instrument and treat the gap register as assessment-scoped only.
- **C — Keep all three.**

**Recommendation: A.** H-9's mechanism is the point: *"an instrument that looks authoritative converts 'I should check' into 'I already checked'"* — and Phase 0 of this very assessment was that mechanism operating on this assessment. B splits the live surface again. C is the status quo that produced the failure.

**What follows.**
- **A** → PR-3: two banners, 7 items migrated into G-5, `L12` dropped, one line in `AGENTS.md` naming the live register.
- **B/C** → PR-3 shrinks or vanishes; H-9 stays open with its mechanism intact.

---

## R-8 · The curriculum outcome-mix rule — *now the sole blocker of an entire frontier*

**Status:** PENDING · **Register:** G-10 · **Blocks:** PR-14, Track E in full.

**The question changed shape since the register was written (N-5).** G-10 named the 16-premise compilation cap as the blocking engineering item. ADR-0264 §4.1 carries a banner directly beneath its own heading:

> **SELF-SUPERSEDED by this ADR's own R5, discharged 2026-07-26. The heading is no longer true of the running system.** … R5 removed that: compilation is query-scoped, so a family of any size answers. With the cap gone, **four bands would earn SERVE the moment a ledger is sealed** — `physics·causal`, `systems_software·causal`, and `philosophy_theology·{modal,contrast}`.

**The engineering blocker does not exist.** The whole of the throughput frontier is this one ruling.

**Evidence.** Reliability is commitment precision, and a correct UNKNOWN *is* a commitment — so a band clears θ_SERVE **on non-commitments alone**: `conservative_floor(660, 660) = 0.990046`. The licensable evidence is 99.0–99.98% non-entailed; **max entailed volume in any band is 9**. `chat/data/curriculum_serve_ledger.json` is deliberately absent, and `core proposal-queue reseal` refuses to grant a license without `--allow-new-licenses`, so nothing is licensed while this ruling is unmade. A committed ledger is necessarily an *earning* one.

**Options — each with its measured consequence.**
- **A — Minimum entailed floor.** A band licenses only with ≥N *entailed* decisions. At N=10, **zero** bands qualify today (max entailed = 9). At N=5, some do. Sets a content-volume bar that curriculum authoring must clear.
- **B — Mix ratio.** A band licenses only if entailed decisions are ≥X% of committed evidence. At any X above ~1.4%, today's bands fail (9/660).
- **C — Separate the license.** License `unknown`-serving and `entailed`-serving as different capabilities with different ledgers, each earned on its own evidence. Four bands could license the honest thing they actually demonstrate (correct refusal), and nothing licenses entailment on 9 cases.
- **D — Defer.** No ledger, no curriculum serving, frontier stays closed.

**Recommendation: C**, with a floor from A applied to the entailed capability only. C is the option that stops the arithmetic from being the problem: the bands genuinely *have* proven something at 660 decisions — the ability to correctly decline — and CORE's whole architecture says a correct UNKNOWN is a real commitment, not a null. Licensing that honestly, separately, is `wrong=0` reasoning applied to licensing itself. A and B are both defensible and both amount to "no curriculum licensing until authoring volume rises 10–50×," which is a true statement about content but delivers nothing from work already done. D forecloses.

**What follows.**
- **A/B** → one rule in the ledger schema + a sealed ledger licensing zero or few bands; PR-14 lands mostly empty and honest.
- **C** → two capability entries in `CAPABILITY_LEDGERS`, the mix rule declared in the table (ADR-0263 Rule 5), an ADR-0264 §5 amendment recording the ruling, then PR-14.
- **D** → PR-14 withdrawn; G-10 closed as DEFERRED-WITH-RULING; Track E reduces to PR-12 alone.

---

## R-9 · The soak's evidence standard and cadence

**Status:** PENDING · **Register:** G-5 · **Blocks:** PR-11.

**The question changed shape since the register was written (N-4).** G-5 says *"the soak has never produced an artifact."* It has: `evals/l10_always_on/contract.md` §"The measured result" records a **5000-beat soak with a reboot at beat 2500** (landed 2026-07-19 in `aed273b1`) in which **all four predicates pass** — `versor_condition` flat at `1.389e-07` across all 5000 beats, vault bounded at 6 entries, convergence at beat 1 with the 4999-beat tail at rest, reboot resuming the same life with derived learning intact.

**What is actually owed** is the ceremony, and it is exactly the failure mode this assessment's own §8 maintenance contract names:

- the result is **prose in a contract file** — no committed machine-readable report, no run SHA, no rerun path;
- `deterministic_digest` is computed by `report.py` and **pinned nowhere** — the contract's closing line says *"Pin it once the lane is trusted so a regression flips it,"* and it never was;
- **no cadence** rules the lane, and the local-first/Mac-runner doctrine makes "nightly" itself a ruling rather than a cron line (AGENTS.md: *"when the Mac is asleep or away, the Actions queue waits… That is fine"*).

**Options.**
- **A — Commit the artifact, pin the digest, rule a manual cadence.** Re-run at horizon, commit the report, pin the digest so a regression flips it, and rule the cadence as *"before each arc close, and on any change to `chat/always_on.py` or `chat/always_on_daemon.py`"* — enforced by a pin on the changed-files set, not by a clock.
- **B — A, plus a nightly job.** Add the lane to `nightly-full-pytest.yml`, accepting that it runs only when the Mac is awake.
- **C — Prose is enough.** Record the run in the contract and move on.

**Recommendation: A.** It converts testimony into evidence with a pinned digest, and it ties cadence to *change* rather than to a clock the doctrine says will silently not fire. B's nightly is not harmful but is the weaker signal of the two, and it invites the same "green because it did not run" reading that H-9 names. C is the status quo and is precisely what the contract file itself asked not to happen.

**What follows.**
- **A** → PR-11 delivers: committed report artifact, pinned digest, the H1–H4 pins promoted into a curated suite, one cadence paragraph in the contract, one pin on the trigger set.
- **B** → A + one workflow line.
- **C** → G-5 closes as accepted-with-reason and the L10 frontier stays evidenced by prose.

---

## R-10 · PR #138 disposition

**Status:** PENDING · **Register:** G-2 / G-3 · **Blocks:** Track B in full.

**The question.** PR #138 — *"the reader/writer construction overlap is 6 — and the reader fabricates on 22 more"* — is open at `c69f9948` and is the only open PR in the repository. It is the measurement that established the reading frontier: writer 1739 constructions, reader 19, overlap **6**, fabrication on **22** beyond the verified inventory.

**Evidence.** The PR is **measurement-only**. The two known fixes — `every dog is a mammal` → `member(every_dog, mammal)`, and `Given: furthermore; p implies q; p.` → `asserted(furthermore)` recited back as a served premise — are two of the 13 mutations and are **deliberately held out** of it, because they change what CORE comprehends from user input, which is serving-path truth behavior and therefore ADR + ratification territory. That standing instruction is unchanged by this ruling.

**Options.**
- **A — Merge.** The inventory becomes the committed baseline the widening program measures against.
- **B — Hold until the fabrication ADR.** Merge measurement and fix together.
- **C — Close.** Re-derive later.

**Recommendation: A.** It changes no serving behavior and no flag; it lands a measurement that every subsequent Track-B decision references. Holding it makes the baseline live on a branch while the register cites it — the exact condition that lets a measurement go stale unnoticed. C discards work that cost an arc to produce.

**What follows.**
- **A** → merge to `main`; G-3's numbers become main-line facts; the branch and worktree are deleted in the same motion.
- **B** → the ADR (R-11's neighbor) becomes the gate on a measurement that is already correct.
- **C** → the frontier loses its only quantification.

---

## R-11 · An interim defensive gate for the fabrications?

**Status:** PENDING · **Register:** G-2 · **Blocks:** nothing; it is a posture choice while the ADR is pending.

**The question.** The fixes are held for their ADR. In the meantime CORE *serves* readings it fabricated — `member(every_dog, mammal)` from `every dog is a mammal`, and `asserted(furthermore)` recited back as a premise. Is there an interim posture that is neither the held fix nor the status quo?

**Evidence.** The `realize-phase` card records the option: **refuse to hold a reading outside the verified inventory.** That is a refusal, not a comprehension change — it uses the existing typed-refusal machinery and the existing 19-construction verified inventory as the admissibility set. It is the same shape as the `to_syllogism` ruling already ratified in ADR-0261 §5.1: *refuse, don't drop.*

**Options.**
- **A — Gate now.** Readings outside the verified inventory refuse instead of serving. Loud, honest, and reduces served coverage immediately by an unmeasured amount.
- **B — Measure first, then gate.** Instrument how often the out-of-inventory path is taken on the practice corpora, report it, and rule again with the number in hand.
- **C — No interim gate.** Wait for the ADR.

**Recommendation: B.** A is the doctrinally-correct instinct — `wrong=0`-or-refuse is CORE's whole posture, and ADR-0261 §5.1 already ratified exactly this trade in a neighboring surface. What makes B better *right now* is that nobody knows the cost: turning A on blind could refuse a large fraction of ordinary traffic, and a coverage collapse discovered after the fact is the kind of result that gets rolled back rather than reasoned about. B is one instrumentation PR and converts A from a guess into a ruling. If the number is small, A follows immediately.

**What follows.**
- **A** → a gate PR now; expect a coverage report as its headline.
- **B** → an instrumentation PR (counts only, no behavior change), then this ruling re-asked with the number.
- **C** → status quo until the fabrication ADR lands.

---

## R-12 · The two ratified-ADR record amendments

**Status:** PENDING · **Register:** G-15 / H-8 · **Blocks:** PR-1's completion (H-8 cannot close without this).

**The question.** Two ratified ADRs' *records* contradict the code. Neither amendment changes a decision; both are text. Editing a ratified ADR is Shay's authority even when the edit changes nothing, which is why they are here and not in PR-1.

### R-12a · ADR-0146 — the daemon it rejected, shipped

**Evidence.** ADR-0146 (Accepted, 2026-05-25) selects Shape B and states: *"Shape A (Rejected) is rejected because a background daemon process cannot survive host library-session interruptions … without complex process supervision infrastructure,"* and *"Since Shape B is single-process and synchronous, cross-process file locking, daemon synchronization, and signal handling are out of scope."*

`chat/always_on_daemon.py` ships a background daemon with an `fcntl.flock` single-instance lock (cross-process file locking), SIGINT/SIGTERM handling (signal handling), and a load-time identity guard — i.e. it implements the three things the ADR placed out of scope, and it built the supervision infrastructure the rejection said would be required. The rejection's *reasoning* was sound; the daemon simply paid the cost the rejection said it would.

**Drafted amendment (append to ADR-0146):**

> **Addendum — 2026-07-2X, daemon shape reconciled.** ADR-0146's Shape-A rejection stands as reasoning: a background daemon requires process-supervision infrastructure that Shape B does not. That infrastructure was subsequently built. `chat/always_on_daemon.py` (landed 2026-06-14) implements a supervised always-on daemon over Shape-B persistence: an advisory `fcntl.flock` single-instance lock, SIGINT/SIGTERM handling, and a load-time strict-identity guard that refuses to resume a different-identity checkpoint. Shape B remains the persistence model and the CLI's default; the daemon is an **additional** process shape layered on it, not a replacement, and it is owned by this ADR. The "out of scope" sentence in Consequences is superseded for the daemon path only.

- **Option A** — apply as written. **Option B** — a new short ADR owning the daemon instead, with a one-line pointer here. **Option C** — leave; H-8a stays open.
- **Recommendation: A.** The reasoning was never wrong; only the scope sentence went stale. A new ADR for a shape already shipped adds a document without adding a decision.

### R-12b · ADR-0252 — the "34 organs" headline

**Evidence.** ADR-0252 says the architectural error was *"a **novice** comprehender (34 bespoke surface organs) bolted onto an **expert** substrate."* The reproducible count is **18** `resolve_promotable_*` entry organs, all in `generate/derivation/`, at the ratification commit and still today (verified at `ed06dd64`). No consolidation occurred; the 34 appears to have counted modules. The diagnosis is unaffected — it does not depend on the cardinality.

**Drafted amendment (footnote at first use of "34"):**

> † **Basis note (2026-07-2X).** The figure "34" has no reproducible derivation. The reproducible count of surface entry organs is **18** `resolve_promotable_*` functions, all in `generate/derivation/`, at this ADR's ratification commit and unchanged at `ed06dd64`; ~32 *modules* participate in the derivation package, which is the likeliest origin of the number. The diagnosis, the supersession plan, and the §4 conformance bar are unaffected — none depends on the count. Later text saying "the 34 surface organs" should be read as "the surface organs."

- **Option A** — apply as written. **Option B** — replace every "34" with "18" throughout. **Option C** — leave; H-8b stays open.
- **Recommendation: A.** B rewrites a ratified document's prose; A records the correction where a reader meets the number, which is all H-8 asks for.

---

## R-13 · Wilson re-count — authorize, knowing licenses may be demoted

**Status:** PENDING · **Register:** H-1 / G-19 · **Blocks:** PR-12, and PR-14 through it.

**The question.** Wilson lower-bound licensing (θ_SERVE=0.99, ADR-0175 lineage) assumes independent trials. A replay of the same sealed case is one trial observed again, not a new one. Re-counting on a distinct-evidence basis will demote licenses.

**Evidence — and this is stronger than the register states.** The exposure is **already pinned in-repo**: `tests/test_volume_honesty.py` (ADR-0264 R9, in the local smoke gate) pins *"21 of 25 bands do not clear θ_SERVE on distinct evidence"* — explicitly *"in BOTH directions"*, and its own comment calls the inventory *"an EXPOSURE INVENTORY, not an approved baseline,"* measured 2026-07-25 at `6ada6f7a`, with every band at 720 committed decisions. The audit source is `docs/research/distinct-evidence-audit-2026-07-25.md`. **So this ruling is not about discovering the shortfall — it is about applying it.**

**Options.**
- **A — Authorize the re-count and the demotions.** Distinct-evidence counting is declared in the ledger schema; the 25 bands are re-counted; demoted bands lose their licenses in the same PR; `test_volume_honesty.py`'s pin moves with it.
- **B — Authorize the counting change, grandfather existing licenses.** New licenses use distinct evidence; the 25 keep theirs.
- **C — Decline.** Keep the current basis; H-1 closes as accepted-with-reason.

**Recommendation: A.** The earned-license machinery is CORE's mechanism for *deserving* to serve; a license the evidence never supported is precisely the failure it exists to prevent. B is the worst of the three — it institutionalizes two standards and makes "licensed" ambiguous exactly where the architecture needs it unambiguous. The demotion is the mechanism working, and it should be the PR's headline, not its footnote. Expect served capability to shrink.

**What follows.**
- **A** → PR-12 as specified; a public shrink in licensed bands; the pin updated in the same PR.
- **B** → PR-12 without revocations; two counting bases coexist and must be documented as such.
- **C** → PR-12 withdrawn; H-1 closed with a written rationale for why replay counts as independent evidence.

---

## R-14 · Gate parity — raise CI to the local suite, or lower the local suite to CI?

**Status:** PENDING · **Register:** N-3 / G-7 · **Blocks:** PR-4's remediation half (the pins themselves are unblocked).

**The question.** `TEST_SUITES["smoke"]` = **23** files. `smoke.yml` = 8 patterns → **13** files. Ten files are on the local gate and not in CI.

**Evidence, stated honestly in both directions.** AGENTS.md §CI/CD is explicit that `.github/workflows/*.yml` are *"secondary observability only — never a substitute for local gates"* — the merge gate **is** the in-worktree run, and the in-worktree run is the superset. Eight of the ten files carry comments saying they belong "on the pre-push gate," which is exactly where they are. **Under doctrine, nothing is unguarded.**

What is still wrong: the audio block's comment says it is listed explicitly *"so the local-first pre-push gate … **equals** the CI gate rather than silently narrowing it"* — accurate about the six audio files, false as the statement about the suite that a reader will take it for. And the real exposure is the **push that skipped the local gate** — from a cloud session, another machine, or an agent — for which CI is the only automatic check, and for which ADR-0265's denial pin, both ADR-governance pins, volume honesty, and curriculum polarity currently run nowhere before merge.

**Measured cost.** The ten files are **429 tests in 46s**, measured on this Mac — which is the hardware the Act runner executes on (`ubuntu-latest:host` = native macOS host, not a container). This is a measurement on the runner's own hardware, not an extrapolation.

**Options.**
- **A — Raise CI to parity.** Add the 10 files to `smoke.yml`; +46s; the parity pin then keeps them equal forever.
- **B — Lower local to CI.** Remove the 10 from `TEST_SUITES["smoke"]`; contradicts eight in-code promotion rationales, several written after real silent-regression incidents (#136, #113, the 2026-07-20..24 register-axis drift).
- **C — Keep them different, deliberately.** Rewrite the audio comment so the record stops claiming equality, and drop the parity pin; keep only the membership pin.

**Recommendation: A.** 46 seconds is a small price for closing the one hole doctrine leaves open — the push that did not run the local gate — and it is the option under which the record becomes true rather than being edited to match a weaker reality. B is a real option only if CI time is scarce, and it deletes protections added *because* things silently regressed. C is honest but leaves the automatic net at 13 files forever.

**What follows.**
- **A** → PR-4 adds 10 paths to `smoke.yml` + the parity pin + the membership pin.
- **B** → PR-4 removes 10 entries from the suite tuple + both pins; the promotion rationales are deleted with a note.
- **C** → PR-4 ships the membership pin only + a corrected audio comment.

---

## Summary — one line each

| # | Question | Recommendation | Blocks |
|---|---|---|---|
| R-1 | CR-3 efferent action | **A** deferred, criterion named | — |
| R-2 | CR-4 "now" | **B** beats govern cognition, wall-clock in telemetry only | PR-11 |
| R-3 | F-6 accrual flag | **A** incomplete set — add the flag | Wave 4, PR-5 |
| R-4 | Flag profiles | **A** profiles + register + pin (28 flags) | PR-5 |
| R-5 | Identity bar | **A** discrimination bar, corpus and floor named | — |
| R-6 | Non-text ingest | **A** deferral with the falsification bench as the standard | — |
| R-7 | Register supersession | **A** supersede both, migrate 7 items into G-5 | PR-3 |
| R-8 | Curriculum outcome-mix | **C** separate `unknown`- and `entailed`-serving licenses | PR-14, Track E |
| R-9 | Soak evidence + cadence | **A** commit artifact, pin digest, change-triggered cadence | PR-11 |
| R-10 | PR #138 | **A** merge — measurement only, fixes stay held | Track B |
| R-11 | Interim fabrication gate | **B** measure the cost, then rule again | — |
| R-12 | Two ADR record amendments | **A/A** apply both drafted texts | PR-1 / H-8 |
| R-13 | Wilson re-count | **A** authorize, apply demotions, move the pin | PR-12, PR-14 |
| R-14 | Gate parity direction | **A** raise CI, +46s measured | PR-4 |

*Fourteen questions. Every one has its evidence gathered, its options enumerated, and its consequent diff written. Nothing below Wave 0 branches on an unasked question once these are answered.*
