# The Flag Register

**Status:** live · **Authority:** R-3 and R-4 (`docs/assessment/50-rulings.md`, ruled 2026-07-28) · **Register:** G-8 / H-6
**Enforced by:** `tests/test_flag_register.py` — the table below and `core/config.py` must name exactly the same set, in both directions. A flag cannot land unregistered, and a register entry cannot outlive its flag.

`RuntimeConfig` is a single frozen dataclass carrying **32 boolean fields: 28 default `False`, 4 default `True`.** Until this document existed, nothing in the repository stated that set, distinguished a *capability* flag from a *posture* flag from a *deployment* knob, or recorded what evidence would flip any of them. Two independent counts of the same set differed by eleven (the assessment said "seventeen"; N-7 measured 28 default-off) — and that disagreement was itself the finding.

---

## 0. What this register is for

A default-off flag is one of two things, and they look identical in code:

- **deliberate posture** — the capability works, and shipping it dark is the correct decision until named evidence arrives;
- **accumulated hesitancy** — nobody turned it on, nobody decided not to, and the default is an artifact of the order things were built in.

The distinction cannot be recovered from `core/config.py`, because both are spelled `= False`. This register records which is which and, for every flag, **what would change the answer**. A flag whose "what flips it" column reads *"no criterion recorded"* is not a posture. It is an open question wearing a default.

**The classes** — declared here, applied in the tables, and the reason the tables are separate:

| Class | What flipping it changes | Who may flip it |
|---|---|---|
| **CAPABILITY** | what CORE *can do* — a cognitive ability comes online | engineering, on the named evidence |
| **POSTURE** | what CORE *serves or refuses* as true | **ruling** — this is the `wrong=0` boundary |
| **DEPLOYMENT** | cost, lifecycle, process shape — not capability, not truth | per-deployment; profiles below |

The classification is the load-bearing half. `estimation_enabled` and `composed_surface` are both `= False` and are not the same kind of thing: one widens a surface, the other decides whether CORE may serve an approximation as an answer.

---

## 1. The default-ON surface — four flags, and the register's sharpest finding

These four are live in every default `RuntimeConfig`. They are the only flags whose behaviour is *on* unless someone turns them off, so they carry the highest burden of justification — and three of the four carry the least.

| flag | class | governing ADR | recorded rationale | what would turn it OFF |
|---|---|---|---|---|
| `allow_cross_language_recall` | ~~CAPABILITY~~ → **DEPLOYMENT (telemetry depth)** | **FA-1 verdict, 2026-07-28** | see the ruling below | flips if walk output is ever routed into the user-facing surface |
| `use_salience` | CAPABILITY | **none** | **none — no comment block in `core/config.py`** | *no criterion recorded* |
| `discourse_planner` | CAPABILITY | **none** | yes — builds a deterministic `DiscoursePlan`; BRIEF mode is byte-identical to single-clause output | evidence that multi-clause rendering degrades a served lane |
| `deduction_serving_enabled` | POSTURE | **ADR-0256** | yes — ROBDD entailment intercepts argument-shaped turns; 716/716 `wrong=0` | a `wrong>0` result on the sealed band, which revokes the license by construction |

**Finding (measured 2026-07-28).** Of the four flags that are ON in production, **one** has a governing ADR and **two have no recorded reason of any kind** — no ADR, no comment, no criterion. In an architecture whose entire posture is *earned* licenses and *refuse-don't-guess*, two permanently-on capability flags with no recorded decision is the mirror image of the hesitancy problem this register was built to find: **accumulated permissiveness**.

This was registered, not fixed. Writing a rationale after the fact would be inventing a decision that was never made, which is worse than recording that it is missing. **Owed:** a one-line rationale-or-flip for each, from whoever knows why they are on. `use_salience` remains owed; the other has since been **ruled by measurement** rather than by recollection:

> ### Ruling · `allow_cross_language_recall` · 2026-07-28 (FA-1 work-order item 3)
>
> **It does not do what its name says, and its blast radius is telemetry.** The flag has exactly one consumer: `chat/runtime.py:2844`, which passes `recall_top_k = 3 if allow_cross_language_recall else 0` into `generate()`. That parameter reaches `generate.stream._recall_state`, which calls `vault.recall(state.F, top_k)` — a **nearest-versor search over stored field states by CGA inner product**. It has no language argument, no pack, and no cross-language path of any kind. The flag sets vault-recall *depth*, and the word "cross_language" in its name describes nothing in the code it controls.
>
> Its effect is also bounded away from the user. `_recall_state`'s own INV-24 note records that recalled versors become rotor transitions on the **generation walk**, which feeds `walk_surface` — *"retained telemetry/evidence"* per `docs/specs/runtime_contracts.md:44` — while the user-facing surface comes from `realize(proposition, vocab)`. So the flag adjusts how much recalled context colours an evidence trace, not what anyone is told.
>
> **Ruled: stays ON, reclassified DEPLOYMENT, renamed in the keel.** Turning it off would reduce evidence richness to buy nothing, and it is not the CORE-Logos switch. **This also corrects the Foundations Audit's own characterisation of it as "the pillar's own switch"** — that read the name, not the call graph, which is the error the audit exists to find. **What flips it:** the condition `_recall_state` states itself — if walk output is ever routed into the user-facing surface, this becomes a CAPABILITY flag, must pass `min_status=COHERENT`, and needs a fresh ruling.

**A second-order gap, closed with this register.** `tests/test_adr_status_governance.py::test_default_on_flag_is_not_governed_by_a_proposed_adr` is parameterized over *(default-on flag × cited ADR)*. Three of the four ON flags cite no ADR, so they generate **zero** cases — the pin covers exactly one flag. Its non-vacuity guard asserts that *some* flag cites an ADR, which stays green even if the parametrization drops to zero. That guard is tightened alongside this register.

---

## 2. POSTURE flags — the `wrong=0` boundary

Flipping any of these changes what CORE serves or refuses **as true**. None may be flipped by engineering judgement; each needs a ruling. All are default-off.

| flag | governing ADR | posture | what flips it |
|---|---|---|---|
| `estimation_enabled` | ADR-0175 / ADR-0206 | a converse query CORE would refuse may return a **DISCLOSED approximate** estimate, if the predicate-class holds a SERVE license at θ_SERVE=0.99 | a sealed reliability ledger granting the license — **deliberate posture, criterion named and unmet** |
| `curriculum_serving_enabled` | ADR-0262 | exam-shaped polar questions answered from the ratified domain-chain curriculum, read OPEN-world (an untaught relation is UNKNOWN, never "no") | **R-8's outcome-mix rule + a sealed earning ledger** (PR-14). Four bands qualify on sealing |
| `ask_serving_enabled` | ADR-0262 | ASK serving allowed | the same ledger; *no independent criterion recorded* |
| `verified_serving_enabled` | ADR-0262 | VERIFIED serving allowed | the same ledger; *no independent criterion recorded* |
| `identity_wave_gate` | ADR-0244 | a flagged identity score becomes a **typed refusal** rather than a score | **R-5's discrimination bar** — γ_id separates attack signal from benign traffic poorly on the current nominal axis frame. Deliberate posture, criterion now named |
| `identity_action_surface` | ADR-0246 | the fuller induced-action admit surface layered on the wave gate | **NOT AUTHORIZED for live activation.** Thresholds are uncertified placeholders; §6.3 shows it refuses benign and adversarial traffic alike. Requires certification, then R-5's bar |
| `strict_identity_continuity` | ADR-0157 | on reboot, a changed engine identity **refuses to start** instead of warn-and-flag | deployment choice for hard-continuity operators — **forced ON in the continuous-life profile** (§4) |

`ask_serving_enabled` and `verified_serving_enabled` are the two entries here with no independent criterion. They are ADR-0262 siblings of `curriculum_serving_enabled` and are presumed to ride its ledger; that presumption is recorded rather than asserted, because nothing in the repository states it.

---

## 3. CAPABILITY flags — default-off, and what each is waiting for

Every entry preserves byte-identity when off; that is the design and it is why they accumulated. Grouped by what they are actually waiting on.

### 3a · Waiting on a transition window that has not been closed

| flag | ADR | what flips it |
|---|---|---|
| `forward_graph_constraint` | 0046 / 0047 | closes Pillar 1→2→3 coupling on the live path. Off "during the transition window" — **the window's end is not recorded** |
| `unified_ingest` | 0090 | replaces the probe-then-commit path. Off preserves bit-identity — *no criterion recorded* |
| `realizer_grounded_authority` | 0088 | makes the realizer a real surface authority. Off yields `<pending>`/`...` on ungrounded graphs — *no criterion recorded* |
| `recognition_grounded_graph` | 0144 | articulation graph derived from the admitted `EpistemicNode` rather than intent classification — *no criterion recorded* |

These four are the register's clearest **accumulated hesitancy** cluster: each shipped complete, each is off "to preserve byte-identity," and none records what would end that preservation. Byte-identity is a migration tactic, not a destination.

### 3b · Surface-widening composers (each a strict superset of the last)

| flag | ADR | what flips it |
|---|---|---|
| `composed_surface` | 0062 | depth-1 follow-up chain |
| `transitive_surface` | 0083 | multi-hop; strict superset of 0062, byte-identical at `max_depth=0` |
| `gloss_aware_cause` | 0085 | gloss-first CAUSE surfaces |
| `thread_anaphora` | 0066 | deterministic backreference on pack/teaching-tier turns |

Deliberate posture as a group: each widens what CORE says without widening what it knows, so each needs an honesty check before it earns default-on. *No per-flag criterion recorded* — a shared one would suffice and is cheaper than four.

### 3c · The always-on life (Steps B and D, and the idle loop)

| flag | ADR | what flips it |
|---|---|---|
| `accrue_realized_knowledge` | — | **Step B.** The only turn-path writer of realized facts. **Forced ON in the continuous-life profile as of 2026-07-28 (R-3)** |
| `consolidate_determinations` | — | **Step D.** Consolidates soundly-derived determinations back into the held self. **Forced ON in the continuous-life profile** |
| `persist_session_state` | 0056 / 0151 | Shape B+ full lived-state resume. **DEPLOYMENT** — `O(turns)` snapshot cost; **forced ON in the continuous-life profile** |
| `vault_probe_discoveries` | 0021 / 0148 | session vault (T1) feeds discovery contemplation at `COHERENT` only |
| `vault_promotion_enabled` | 0021 / 0148 | SPECULATIVE → COHERENT crystallization at the turn boundary |
| `auto_contemplate` | 0056 / 0150 | contemplation over pending candidates at checkpoint |
| `auto_proposal_enabled` | 0056 / 0151 | `TeachingChainProposal`s from enriched candidates on load |
| `contemplate_frontier_during_idle` | 0080 | the always-on life mines its own frontier without a user turn; SPECULATIVE-only |
| `review_derived_close_proposals` | — | proposal-only artifacts from proof-gated derived facts; review-gated, no corpus mutation |
| `discourse_contemplation` | 0080 | plan-level contemplation pre-flight; read-only, SPECULATIVE-only |

**R-3's resolution, recorded at the point of change.** `accrue_realized_knowledge` was absent from `CONTINUOUS_LIFE_CONFIG_FLAGS` while `consolidate_determinations` was forced. Step D consolidates the facts Step B writes, so the daemon forced the consumer without the producer — *a continuous life consolidating an empty set*. Ruled **incomplete flag set**, not intended dormancy, because both flags' own comment blocks already described the corrected profile: `accrue_realized_knowledge` says *"the production L10 process enables it alongside `persist_session_state`"* and `consolidate_determinations` says *"...alongside `accrue_realized_knowledge` + `persist_session_state`."* **The documents were right about the intent and the code was incomplete.** Adding the flag made both statements true; the dormancy reading would have required correcting two docstrings that were correct.

### 3d · Undocumented

| flag | class | what flips it |
|---|---|---|
| `allow_cross_language_generation` | CAPABILITY | **no comment block, no ADR, no criterion** |
| `inner_loop_admissibility` | CAPABILITY | **no comment block, no ADR, no criterion** |

With `allow_cross_language_recall` and `use_salience` from §1, these are the **four flags in `RuntimeConfig` with no recorded rationale whatsoever** — two on, two off. They are listed rather than explained, deliberately.

### 3e · Deployment surfaces

| flag | class | what flips it |
|---|---|---|
| `review_pending_proposals` | DEPLOYMENT | read-only idle sub-pass surfacing a proposal summary; a deployment that wants the surface pays for the scan |

---

## 4. Profiles — flag sets ruled as units (R-4)

R-4's mechanism: **profiles are the unit of decision, not individual flags.** A profile is a named, forced set with a stated purpose; a deployment adopts a profile rather than assembling flags. `CONTINUOUS_LIFE_CONFIG_FLAGS` was the pattern; this generalises it.

| Profile | Declared at | Forces | Purpose |
|---|---|---|---|
| **one-shot / eval** | `RuntimeConfig()` defaults | nothing | a fresh runtime per invocation. Must not pay for resume, accrual, or snapshotting it does not use — this is why the defaults are what they are, and it is a real reason rather than hesitancy |
| **continuous-life** | `chat/always_on_daemon.py::CONTINUOUS_LIFE_CONFIG_FLAGS` | `accrue_realized_knowledge`, `persist_session_state`, `consolidate_determinations`, `strict_identity_continuity` | ONE continuous life: accrue each turn, consolidate each beat, survive reboot, and refuse to resume as a different identity. **Forced, not defaulted** — these are not optional knobs for this process shape |

**Not yet a profile, and honestly so:** there is no *serving* profile. The four POSTURE serving flags (`deduction`, `curriculum`, `ask`, `verified`) are ruled individually today because each rides its own license. Grouping them before the ledger is sealed would license by association, which is exactly what R-8 exists to prevent.

---

## 5. The declared-table index

The repository's governing pattern is **declared in the table, not the call site** (ADR-0263 Rule 5). It is implemented in many places and, until now, enumerated in none — so nobody could answer *"which single-source-of-truth tables exist, and what makes each one true?"*

This index is a reader's aid, deliberately **not** a central `contracts.toml`. Centralizing these into one file would add a fifth copy that must agree with four generators, and would place four different authorities in one merge surface. Each table stays where its authority lives.

| Declared table | Where | What makes it true |
|---|---|---|
| `RuntimeConfig` booleans | `core/config.py` | **this register** + `tests/test_flag_register.py` (both directions) |
| `CONTINUOUS_LIFE_CONFIG_FLAGS` | `chat/always_on_daemon.py` | `tests/test_l10_always_on_daemon.py` (on the gate as of 2026-07-28) |
| `GroundingSource` / `GROUNDING_SOURCES` | `core/epistemic_state.py` | closed `Literal` + runtime frozenset + build-time enum-coverage test under `workbench-ui/` |
| `DOMAIN_PACKS` / `DOMAIN_OPERATOR_CLAIMS` | `core/capability/domains.py` | `tests/test_domain_pack_binding.py` (both directions) + `domain_contract_predicates` P3 |
| `TEST_SUITES` | `core/cli_test.py` | `tests/test_suite_membership.py` + `tests/full_only_baseline.txt` |
| `GATE_SUITES` | `tests/test_suite_reachability.py` | verified against `scripts/hooks/pre-push` and `scripts/ci/local-ci.sh` |
| `QUARANTINE` / `SLOW_FILES` / `SLOW_TESTS` | `conftest.py` | `pytest_collection_modifyitems` (stamps markers; never skips) |
| `PINNED_SHAS` → `CLAIMS.md` | the capability ledger | `tests/test_claims_md_is_current.py` |

---

## 6. What this register does not claim

- It does not assert that any default is **wrong**. It asserts that for 20 of 32 flags nothing recorded says whether the default is a decision.
- It does not invent rationales. Four flags have none, and the register says so rather than supplying one after the fact — a fabricated justification is worse than a recorded absence, and this repository has a register full of evidence for that.
- It does not flip anything. R-3's one change (`accrue_realized_knowledge` into the continuous-life profile) was ruled before this document existed and is recorded here, not decided here.
