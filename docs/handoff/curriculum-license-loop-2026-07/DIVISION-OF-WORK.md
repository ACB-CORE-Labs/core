# Division of Work — Curriculum License Loop

**Arc:** curriculum-license-loop-2026-07 · **Written:** 2026-07-25 · **By:** Opus 5
**Plan of record:** `docs/plans/curriculum-license-loop-2026-07-25.md` (binding)
**Read before any unit:** that plan §1–§3, then `AGENTS.md`.

This file is the contract for *who does which unit and why*. It is written to be
read cold, by a tier that was not present for the analysis. If it conflicts with
a memory or a chat instruction, the plan of record and `AGENTS.md` win.

---

## 0b. Status 2026-07-26 — every code unit in this arc is open as a PR

Superseding §0 below (kept for the reasoning, which still holds). All units are
**open, unmerged, awaiting Shay's authorization.**

| unit | PR | branch | state |
|---|---|---|---|
| E2 rename | #119 | — | **MERGED** |
| R5–R7 query-scoped premises | #120 | — | **MERGED** |
| **C** practice producer | **#121** | `feat/curriculum-practice-producer` | open |
| **D** `proposal-queue reseal` | **#122** | `feat/proposal-queue-reseal` (on #121) | open |
| **E1** code half (audit-ledger R7) | **#123** | `feat/audit-ledger-r7` | open |
| **parity** measurement + `core rust build` fix | **#124** | `fix/rust-build-env-and-parity-report` | open |
| **polarity** R1–R4/R8 | **#125** | `feat/curriculum-polarity` (on #121) | open |
| doc reconciliation + arc close | this branch | `docs/arc-reconciliation` | open |

Merge order: **#121 first** (#122 and #125 stack on it; retarget both to `main`
after it lands). #123 and #124 are independent of everything. Merge-commit, not
squash. #122 and #125 both touch `core/cli_proposal_queue.py` in different hunks.

Still Shay's, unchanged: **Phase F** content (`philosophy_theology · modal`),
**Phase G** the flag, **E3** the ADR vocab sweep (Haiku), and the four open
rulings — of which **outcome mix is now blocking rather than academic** (#121).

**What the units found that the plan did not predict** — all four are in the PRs
and the research notes, listed here because a status table is where someone looks:

1. **A committed curriculum ledger is necessarily an EARNING ledger.** The plan's
   Phase-1 exit criterion ("a real, still-unearned ledger") is unreachable: a
   band clears θ_SERVE on correct NON-COMMITMENTS alone, so sealing licenses four
   bands on ~99% non-entailed evidence. Hence #121 ships the writer and commits
   no artifact, and #122's verb refuses to grant a license without an explicit
   flag.
2. **§4.2's ceiling table was understated** (per-term vs per-pair routability);
   `systems_software · causal` is reachable, not impossible. Four bands can reach
   657, not three. ADR-0264 §4.2 now carries the correction.
3. **`then` and `therefore` are taught lemmas that collide with the argument
   reader's control grammar** — 164 atoms refuse, in the Phase F target band. The
   vocabulary boundary is never screened against the reader's grammar.
4. **The Rust lane-parity method cannot fail.** Sabotaging every Rust kernel
   still yields 11/11 lane pins matching, so §6B's premise needs re-earning.

---

## 0. Status at handoff — 2026-07-25, Opus units complete

The three Opus units are done and pushed. **Read the plan of record's AMENDED
block first**: Phases A and B falsified four premises, one of which reorders the
remaining work.

| Unit | Branch | State |
|---|---|---|
| A — negative-curriculum epistemology | `docs/adr-negative-curriculum` | ADR-0264, pushed. Proposed, awaiting ratification |
| B — volume-honesty invariant | `test/volume-honesty-invariant` (stacked on A) | pushed. 13 tests, mutation-checked, in `smoke` |
| E1 Opus half — the R7 assertion | `docs/e1-r7-assertion-spec` | this branch. `E1-R7-ASSERTION-SPEC.md` |

Merge order: **A, then B** (B is stacked on A), then E1's spec — merge-commit, not
squash. E1's spec branch is independent of A/B and can merge in any order.

**What changed for the Sonnet units.** Three things, all of which make the
remaining work different from §4 as originally written:

1. **A new implementation unit precedes everything: ADR-0264 R5–R7, query-scoped
   premise compilation.** `MAX_PREMISE_SENTENCES = 16` caps a family at 16 chains;
   at 17 the band declines every question, including ones that work today. Until
   this lands, no curriculum band can earn a license at any corpus size, so
   building Phase C first would produce a correct instrument reporting that every
   band is at its ceiling. R5 is fully specified and verified verdict-identical
   over 8,520 questions — it is a loud unit (the physics lane pins every verdict).
   (Precisely: identical wherever the full family was READABLE, and
   verdict-*improving* over the cap, where full-family compilation refuses
   outright. See ADR-0264 R5's precision note.)
2. **Phase F retargets to `philosophy_theology · modal`.** `physics · modal` has a
   hard ceiling of 480 against a 657 threshold. Do not author physics modal volume.
3. **Phase C's producer must call the Phase B audit.** `AUDIT_SOURCES` in
   `tests/test_volume_honesty.py` carries a declared `None` for
   `curriculum_serve` that fails the moment its ledger exists. That is deliberate:
   it is the forcing function against repeating the deduction pattern.

**Standing "do not fix" — the deduction ledger exposure.** 21 of 25 ratified
`deduction_serve` bands do not clear θ_SERVE on distinct evidence (worst: 28
distinct cases inflated to 720 committed). It is measured, pinned in both
directions, and **must not be repaired by any unit below.** The ledger is
SHA-sealed, ratified, and gating a live flag; re-sealing it is Shay's ratification.
If a unit's work makes `tests/test_volume_honesty.py` fail, that is a real signal
— report it, do not update the inventory to match.

**Revised order: E2 → R5–R7 → C → D → E1(code) → parity.**

---

## 1. The tiering criterion — read this first, it is the whole rationale

Units are **not** assigned by difficulty, and not by model prestige. The evidence
does not support that split. In the 2026-07-24/25 window Sonnet 5 (Tier S)
produced the six-worktree `public_demo` archaeology, found the
`derived_close_proposals.py::DEFAULT_SINK` bug that wrote outside the repository,
and found an engine-refused misclassification while building the instrument meant
to measure something else. In the same window Opus 5 mis-diagnosed the CGA hot
path by multiplying a microbenchmark by a call count, and made three wrong
readings of this branch's own commits that survived only until they were checked.

Model tier was not the variable. **Verification discipline was.**

So the split is by one question:

> **If this unit is done wrong, does a gate catch it, or is the error silent?**

- **Gate-caught** — a test fails, an import breaks, a lane goes red, a hash
  drifts. The work is safe to execute at the cheapest competent tier, because
  being wrong is *loud*. Iterating against a red gate needs no design authority.
- **Silent** — the system stays green while asserting something false. No
  downstream check can recover it, because the wrong thing has become the
  reference. These units need the tier that can reason about what the gate cannot
  see, and they must be finished before the units that depend on them.

Two units in this arc are silent-failure units *because they are themselves the
gate*. Those are the ones worth spending expensive tokens on. Everything else is
loud, and spending expensive tokens on it is waste.

**Corollary for whoever picks this up:** if you find yourself about to make a
judgment call that no test would catch, you have crossed a tier boundary. Stop
and escalate (§6). That is not a failure — it is the mechanism working.

---

## 2. Ownership at a glance

| Unit | Phase | Owner | Failure mode |
|---|---|---|---|
| Negative-curriculum epistemology ADR | A | **Opus** ✅ | silent |
| Volume-honesty invariant (tests first) | B | **Opus** ✅ | silent |
| R7 assertion — *what* to assert | E1 | **Opus** ✅ | silent |
| Articulation feasibility study | §6 of plan | **Opus** | silent |
| `assert_corpus_sound` rename | E2 | **Sonnet** ✅ #119 | loud |
| **Query-scoped premise compilation (R5–R7)** | **new, gates C/D/F** | **Sonnet** | loud |
| Practice producer implementation | C | **Sonnet** | loud |
| `core proposal-queue reseal` verb | D | **Sonnet** | loud |
| R7 code move + suite registration | E1 | **Sonnet** | loud |
| Rust parity measurement | plan §6 | **Sonnet** | loud |
| ADR status vocabulary sweep | E3 | **Haiku** | loud |
| Content authorship (≈219 relations) | F | **Shay** | — |
| Capability-index scoring / stratification / `hash_surface` rulings | plan §5 | **Shay** | — |
| `curriculum_serving_enabled` flip | G | **Shay** | — |

---

## 3. Opus units — expectations

### A. Negative-curriculum epistemology (ADR) — **do this first**

**Why Opus.** This is the highest-risk unit in the arc. If the epistemology is
wrong, the corpus encodes falsehoods and **`wrong=0` still passes** — because the
lane's gold derives from the same corpus, and `evals/curriculum_serve/oracle.py`
is independent in *code* but reads the *same rows*. Corpus-level epistemology
errors are structurally unfalsifiable by every gate this repo has. Nothing
downstream notices; the whole arena inherits the error and certifies it at
volume.

**Binding constraints (from the plan, not re-litigable):**
- Absent edge ⇒ UNKNOWN, never "no". This is the open-world reading and it is
  the reason curriculum serving is honest at all.
- Explicit negative edge ⇒ REFUTED. These are different states and the corpus
  must distinguish them.
- Polarity is a **row-level field or `intent` value**, never a new
  `operator_family`. Bands key on `(domain, operator_family)`
  (`chat/curriculum_surface.py:184`), so a `modal_negative` family creates a new
  band at n=0 rather than adding refuted volume to `curriculum_physics_modal`.
- The oracle must learn polarity **independently** of the serving path. Its
  code-level independence is the entire evidentiary value; do not let the two
  share a polarity helper.

**Done when:** ADR is Accepted, the row schema shape is fixed, and the
UNKNOWN-vs-REFUTED boundary is stated precisely enough that Phase B can enumerate
against it. **No code.**

### B. Volume-honesty invariant (tests, written before any producer)

**Why Opus.** This unit *is* the anti-gaming gate, so there is nothing above it
to catch a mistake. S6 already proved the exposure: `conservative_floor` cannot
distinguish "657 independent facts" from "16 facts asked 41 times each"
(`docs/research/curriculum-volume-quantification-2026-07-24.md` §1). An unbounded
generator therefore clears θ=0.99 at n≥657 **without earning anything**, and the
resulting license reads as identical to a real one. Getting the bounding rule
wrong silently invalidates all of Phase F's authoring effort.

**Expectations:**
- Tests come **first** and must fail for the right reason before any producer
  code exists. The test file is the specification of the invariant; that is why
  it is the deliverable and not a by-product.
- At most one committed case per distinct
  `(relation, direction, polarity, question-shape)` tuple. No paraphrase padding.
- Assert the bound structurally: *N* ratified chains cannot yield more than a
  bounded multiple of *N* committed cases.
- **Mutation-check it.** Pad the generator ⇒ red. A pin that cannot fail is
  worthless; this is the same discipline `tests/test_adr_status_governance.py`
  was held to.

**Done when:** tests exist, fail correctly, fail under mutation, and the module
interface they imply is unambiguous enough that Phase C needs no design decisions.

### E1 (Opus half). The R7 assertion

**Why Opus.** The code move is trivial and specified —
`docs/specs/runtime_contracts.md:448-456` already says "defer the single sink
emission to the pipeline serve boundary." What is *not* specified is what to
assert, and the default sink is `None`, so **nothing exercises this path**. A
wrong move is therefore silent. This is also the exact seam that regressed
silently for two days in the #96 register-axis incident, so it gets the careful
tier by history as well as by reasoning.

**Done when:** a written assertion exists — the sink receives the **post-override**
event, and its `trace_hash` matches a pipeline replay — precise enough for Sonnet
to implement against.

---

## 4. Sonnet units — expectations

Every unit here has a loud failure mode. You are expected to iterate against the
gate until it is green, not to re-derive design. If a unit seems to require a
design decision, that is the signal in §6.

**Order: E2 → R5–R7 → C → D → E1(code) → parity.** E2 first because Phase C adds a
third `assert_corpus_sound` caller and renaming after that is strictly more work.
R5–R7 second because nothing downstream can earn anything until it lands (§0).

> **Both landed (#119, #120), so this ordering constraint is spent.** The names are
> now `assert_practice_gold_sound` (no args, practice gold) and
> `assert_lane_cases_sound(domain, cases)` (lane contract); Phase C added its
> caller after the rename, as intended. Remaining units are order-independent
> except for the stacking recorded in §0b.

### R5–R7. Query-scoped premise compilation — **do this before C and D**

`teaching/curriculum_premises.py::compile_premises` emits *every* chain in the
family, and `read_verb_argument` refuses past `MAX_PREMISE_SENTENCES = 16`. So a
17-chain family answers nothing. Three rules, all specified in ADR-0264 §2:

- **R5** — compile a scope that is a **superset of the query-atom rows** and a
  subset of the family. Default: **term incidence** (rows whose subject or object
  is one of the query's two terms). If that would still exceed the cap, narrow to
  the query-atom rows. Never truncate arbitrarily, and never refuse for size.
- **R6** — an **empty scope is UNKNOWN**; only an empty *family* is the
  `empty_curriculum` refusal. Get this wrong and 8,463 of 8,520 questions flip
  from `unknown` to `declined`.
- **R7 (curriculum)** — `premise_count` keeps reporting **family size**, because it
  is user-visible. Carry the compiled-scope size as a separate field. (Unrelated to
  audit-ledger R7 in E1 — same numeral, different register.)

**Why this is loud, and why it is not the ADR-0261 §5.1 premise-dropping sin.**
Narrowing is verdict-*identical*, not merely sound: each compiled premise mints one
independent propositional atom, so a scope containing the query atom decides the
query exactly as the full family does — **wherever the full family was readable.**
Over the cap it is verdict-*improving*: full-family compilation refuses
`compiled_premises_unreadable` there, so the narrowed scope answers questions the
unscoped compiler could not. That is the unblock, not a deviation from it. Verified over 8,520 routable questions with
zero mismatches (`docs/research/curriculum-premise-scope-2026-07-25.md` probe 3).
Gold is preserved: physics stays `entailed 14 / unknown 12 / declined 6`.

**Gate:** the `curriculum_serve` lane at `wrong=0`, and the 20 tests in
`tests/test_curriculum_serve.py`. If any verdict moves, stop — the equivalence
argument has a hole and that is escalation §6.3.

### E2. `assert_corpus_sound` rename — **DONE, #119**
Renamed to `assert_practice_gold_sound` / `assert_lane_cases_sound`. Two
functions, one name: `evals/deduction_serve/practice/gold.py:1163` (no args,
practice corpus) and `evals/curriculum_serve/runner.py:71` (`domain, cases`, lane
contract). Not a missing contract — a name collision, flagged in
`BRIEF-CLOSE-assessment-verification-2026-07-25.md` §9.5. **Gate:** imports break.

### C. Practice producer
`evals/curriculum_serve/practice/{__init__,generator,runner}.py`. Mirror
`evals/deduction_serve/practice/` topology **exactly**: producer in `evals/`,
sealed artifact next to its reader in `chat/data/`.

> **Mirror the topology, NOT the volume strategy.** The deduction producer sets a
> flat `CASES_PER_BAND = 720` and fills the quota by cycling a template ×
> vocabulary space that is as small as 28 distinct instances — which is the
> exposure Phase B measured. Follow the **`estimation`** producer instead
> (`evals/determination_estimation`): 660 *distinct* cases per class, zero repeats,
> chosen just above the 657 a perfect record needs. Emit at most one case per
> distinct query atom (ADR-0264 R9) and let the count fall where the corpus puts
> it. Then register the producer in `AUDIT_SOURCES`
> (`tests/test_volume_honesty.py`) — the declared `None` there fails as soon as
> `chat/data/curriculum_serve_ledger.json` exists, which is how this unit is
> stopped from repeating the pattern.

**Reuse, do not rewrite** — this is why the unit is small:
- `evals/curriculum_serve/oracle.py` — already an independent decision procedure;
  wrap as the gold tether.
- `core/learning_arena/engine.py::run_practice` — the ADR-0199 pure fold.
- `core/ratified_ledger.py::{seal_artifact, tally_dict, write_sealed_ledger}` —
  extracted by ADR-0263 for exactly this third instance.
- `core/reliability_gate::{Action, Ceilings, ClassTally, license_for}`.
- `chat/curriculum_surface.py` — the solver under test.

Determinism is required: no clock, no RNG, byte-identical sealed output across
runs, so the artifact is safe to commit and SHA-verify on load. Read
`evals/deduction_serve/practice/runner.py` docstring for the pattern.

**Gate:** Phase B tests; `wrong=0` on the physics lane.

### D. `core proposal-queue reseal`
`teaching/ratification.py`, `core/cli_proposal_queue.py`. Explicit verb —
**never** auto-reseal on `ratify` (doctrine forbids ratification automation, and
per-row reseal would churn the ledger's `content_sha256`). `ratify_chain` records
the enqueue; a human runs the seal. Follow the existing
`status|list|show|review|ratify` verb patterns.

**Gate:** CLI tests; the verb produces a SHA-sealed
`chat/data/curriculum_serve_ledger.json`, and `curriculum_serve_license()` reads
a real but still-unearned ledger instead of an absent one.

### E1 (code half). R7
Move the emission per Opus's written assertion. Do not improvise the assertion.

### Rust parity measurement
`PYO3_PYTHON=/opt/homebrew/bin/python3.12`, `cargo test` in `core-rs/`, then rerun
the hash-pinned lanes under `CORE_BACKEND=rust`. cargo 1.97.1 and the registry
cache are present locally; the cloud session was blocked only by sandbox network
policy. **Report the measurement; do not act on it.** A parity *failure* is a
silent-class finding about determinism — escalate rather than "fix."

### Suite registration (all units)
Anything you add goes into a curated suite in `core/cli_test.py`. Two files from
PR #113 landed in **no** suite and ran only under `full`, which gates nothing —
that was the fifth instance of this pattern in three arcs. Do not make it six.

---

## 5. Haiku unit

### E3. ADR status vocabulary normalization
27 unparseable status lines plus `draft`/`ratified`/`active`/`accepted.` variants
across 312 ADR files (inventory: `docs/research/adr-status-governance-2026-07-25.md`
§6). Normalize to the intended lifecycle, then widen
`tests/test_adr_status_governance.py` from its deliberately narrow scope to a
closed vocabulary.

Bulk mechanical with an objective acceptance criterion: **the widened pin goes
green.** Do not change any ADR's *decision* — only its status token. If a file's
intended status is genuinely ambiguous, list it and stop; do not guess.

---

## 6. Escalation — when a cheaper tier must stop

Stop and hand back up when any of these is true. Escalating is the mechanism
working, not a failure; guessing past one of these is the only real error
available here.

1. **You are about to make a call no test would catch.** By definition you have
   crossed into a silent-failure unit.
2. **A gate is green but you do not believe it.** That is the signature of a
   reference that has become wrong — exactly the ADR-0256 shape, where the record
   asserted "not yet decided" about a live decision and nothing failed.
3. **The measurement contradicts the plan.** Say so with the numbers. Both prior
   arcs improved by having their premises falsified in writing; a falsified plan
   premise is a deliverable, not an interruption.
4. **A parity or determinism check fails.** Never "fix" a hash drift. Report it.
5. **Scope exceeds the unit as written.** Flag it in the PR/handoff rather than
   improvising, per the standing Tier-S/O constraint.

---

## 7. Standing constraints (non-negotiable, all tiers)

- `wrong=0`. No flag flips — those are Shay's ratification only.
- Forgejo-primary; no `gh`, no `tea`. SSH:29222 often times out — push over the
  authenticated HTTPS remote instead.
- Branch **and** worktree per unit; both deleted immediately after merge.
- Pre-push gate in-worktree on canonical **Python 3.12.13** with
  `uv sync --locked`: `core test --suite smoke -q` then `--suite deductive -q`.
  Baselines: **smoke 555 / deductive 285** at arc start; **smoke 569** after
  Phases A+B (+1 from ADR-0264 joining the derived ADR pin, +13 from
  `tests/test_volume_honesty.py`).
- `[Verification]:` line in every PR description, naming the interpreter.
- One PR per coherent unit. Compare-URL PRs; **Shay merges** — no merge
  automation, and green PRs sit until explicit authorization.
- Never `scripts/verify_lane_shas.py --update` — surgical single-line pin edits
  only. Three arcs depend on that rule.
- New tests go into a curated suite (§4).

## 8. At arc close

Fill in `docs/handoff/ARC-CLOSE-TEMPLATE.md` → this directory. The
**Falsified assumptions** section is the one that cannot be recovered from the
diff — state which parts of the plan of record turned out wrong, including your
own claims. Also record whether the articulation trigger fired, which the
previous arc left unrecorded.
