# The macro→micro assessment arc — commit index and rollback map

**Span:** `797ebad5` (exclusive) → `199dc72d` (inclusive) · **29 commits** · 67 files · **+6,340 / −228**
**Date:** 2026-07-28 · **Branch:** `claude/assessment-docs-work-mh32mh` · **Baseline marker:** `baseline/pre-arc-797ebad5`

**Why this file exists.** It was meant to be a pull-request body. Neither remote could host one: the GitHub App lacks `pull_requests: write` (403 *"Resource not accessible by integration"*), and the agent proxy denies `core-gitquarters.acbcontent.org` at CONNECT (403, policy). So the index lives in the repository instead — which is the more durable home anyway, since it travels with the commits it describes rather than sitting in a forge that may be re-synced.

> **Mirror hazard, recorded because it already fired once.** On 2026-07-28 the GitHub remote's `main` was reset backwards from `199dc72d` to `797ebad5`, discarding 29 commits of remote history. `797ebad5` is *exactly* Forgejo's `main`. Per `AGENTS.md:280` GitHub is a **mirror only** — so this was almost certainly the mirror being re-synced from the canonical Forgejo remote, which is 29 commits behind. The local clone still had everything and restored GitHub by fast-forward (no force, nothing overwritten). **Until Forgejo receives this arc, any mirror re-sync will revert GitHub again.**

---

## Verification

`uv run bash scripts/ci/local-ci.sh --tier gate` @ `199dc72d` → **`EXIT=0`, PASSED in 554s**
smoke **775** · warmed_session **10** · deductive **520** · teaching **136** — **1,441 tests**

The gate went from **2 suites / 721 tests** to **4 suites / 1,441** across this arc. Every commit below was gated green before it was pushed.

---

## Commit index

Oldest → newest. **Independent** = safe to revert alone. **Coupled** = reverting alone leaves a record contradicting the code.

### Wave 0 — record amendments (needed no ruling)

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 1 | `9efd5a61` | PR-1: N-1…N-7 + H-12 applied to the registers | 6f +76/−29 | Independent |
| 2 | `0641e211` | H-12: the pre-push hook asserts the parity too | 1f +1/−1 | Independent |
| 3 | `0c11b530` | Merge of PR-1 into the docs branch | — | Merge — revert 1+2 instead |
| 4 | `635f2488` | Re-verified at main tip; **corrected H-8d**, which an earlier draft stated wrongly | 3f +4/−4 | Independent |

### Track A — ADR-0252 §5 run to a verdict

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 5 | `299c92be` | **Pre-registers the GO/NO-GO criterion** — thresholds as importable constants, no results | 5f +953 | ⚠️ **Never revert alone** — retroactively unbinds the criterion and voids #6 |
| 6 | `7728a25d` | **§5 run → NO-GO.** Corpus, experiment, report + pinned digest, verdict doc; two prior GO verdicts on unmerged branches voided (N-8) | 9f +862/−12 | Coupled to 5, 23 |
| 7 | `8f0ccfe3` | Re-anchored the §5 provenance SHAs to the commits that landed | 3f +13/−4 | Independent |

### Triage and two defect fixes

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 8 | `e025de7a` | External-assessment triage — H-13, H-14, H-8e added; six proposals cleared, each with the refuting file named | 4f +29/−6 | Independent |
| 9 | `71542e61` | H-13 first attempt — refcount. **This fix was WRONG** | 4f +177/−9 | ⚠️ Superseded by 10 |
| 10 | `2cfc6ad2` | **H-13 corrected** — claimant-set tracking; records *why* the refcount reasoning failed | 5f +188/−121 | Coupled to 9 |
| 11 | `98a6e8b4` | PR-9 / H-11 — three silent backstops made visible; byte-identical consumers by construction | 8f +252/−11 | Independent |

### Wave 2 — enforcement

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 12 | `68e68589` | PR-4 / G-7 — membership ratchet + `full_only_baseline.txt` (749). **Parity pin withdrawn** (N-9) | 8f +1056/−12 | Coupled to 14, 19 |
| 13 | `5f18b7e5` | PR-6 / G-9 — three doctrine prohibitions enforced by test; four sabotages observed red | 4f +293/−2 | Independent |
| 14 | `edf6c2a4` | The ratchet **caught its own author**: baseline 749 → 748 | 3f +7/−2 | Coupled to 12 |
| 15 | `39331dbc` | PR-7 / H-7 — M2 trust-boundary table; three boundaries **CLOSED**, one real delta | 3f +72/−1 | Independent |
| 16 | `3650331b` | Re-stamped the eight cards this arc touched | 10f +47/−1 | Independent |

### G-22 — `main` was red before the arc began

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 17 | `913111c0` | Recorded that `main` was red and that membership was never the guarantee | 2f +7 | Independent |
| 18 | `0329cc99` | **G-22 fix** — two stale ceremony pins; `CLAIMS.md` had published a superseded evidence digest for two days | 6f +37/−6 | ⚠️ Reverting re-publishes a false digest |
| 19 | `065826c5` | **Pin 3** — `test_suite_reachability.py`. Measured 21 curated suites, **2 gate-reachable** | 4f +201/−2 | Coupled to 12, 28 |

### Wave 1 and the docket record

| # | SHA | What it did | Δ | Revert |
|---|---|---|---|---|
| 20 | `d0bedfc1` | **R-7** — dead instruments retired; 4 unreferenced aliases deleted (21→17 suites; unreachable 19→15 **by deletion**) | 8f +74/−24 | Independent |
| 21 | `e6a30383` | Recorded the adopted docket + the **11 standing philosophies** in `AGENTS.md`; fixed 14 `PENDING` statuses that contradicted reality | 5f +172/−38 | ⚠️ Re-orphans every ruling record |
| 22 | `ca5e614e` | **G-23** — `DOMAIN_PACKS` vs manifest `domain_id`: 7 of 9 bound, **2 absent**, P3 passing vacuously. Pin + 4 sabotages | 7f +293/−30 | Independent |

### The ruling docket, in its corrected execution order

| # | SHA | Ruling | What it did | Δ | Revert |
|---|---|---|---|---|---|
| 23 | `b823d85d` | **R-12** | ADR-0146 addendum + ADR-0252 "34 organs" footnote + **§5 verdict banner** + **§6 retirement amendment**. Closed H-8a/H-8b/G-15 | 6f +86/−14 | ⚠️ Amends two **ratified ADRs** |
| 24 | `6c67e88d` | **R-3 + R-4** | PR-5 — flag register (32 booleans classified), profiles as units, **`accrue_realized_knowledge` added to the daemon profile**. Closed H-8 in full | 13f +498/−16 | ⚠️ **Behaviour change** — reverting returns the always-on life to consolidating an empty set |
| 25 | `9b190856` | **R-9 + R-2** | PR-11 — the 5,000-beat soak committed as evidence, `deterministic_digest` pinned, cadence enforced by a **source-hash pin** rather than a cron that silently does not run | 8f +369/−11 | Independent |
| 26 | `9cf6a164` | **R-13** | PR-12 — the Wilson re-count. **25 licensed shape-bands → 4**; the sealer now refuses a padded ledger. `wrong` stayed **0** | 11f +364/−69 | ⚠️ **Serving change** — reverting re-grants 21 licences the evidence never supported |
| 27 | `71d6366f` | **R-8** | PR-14 — outcome-mix rule as two capabilities. **Split, zero bands license — not four.** ADR-0264 §5 amended | 7f +261/−8 | ⚠️ Amends a ratified ADR |
| 28 | `294bbe7b` | — | PR-4b — `teaching` promoted onto the gate (**+136 tests**); pin 3's own union blind spot closed | 5f +93/−23 | Coupled to 19 |
| 29 | `199dc72d` | **R-1/5/6/11** | `docs/specs/postures.md` — three postures with criteria; **R-11's interim gate withdrawn** because measurement dissolved its premise | 4f +95/−12 | Independent |

---

## Cherry-pick guidance

**Self-contained — take alone:** `5f18b7e5` · `39331dbc` · `98a6e8b4` · `ca5e614e` · `9b190856` · `199dc72d`

**Take as a group or not at all:**
- `299c92be` + `7728a25d` + `b823d85d` — pre-registration, run, ratification. Any one alone misrepresents the others.
- `71542e61` + `2cfc6ad2` — the wrong fix and its correction.
- `68e68589` + `edf6c2a4` + `065826c5` + `294bbe7b` — the ratchet family; each later one repairs a blind spot in an earlier.

**Behaviour-changing — read the commit body before reverting:** `6c67e88d` (daemon profile) · `9cf6a164` (21 licences revoked) · `71d6366f` (four licences dissolve)

**Rollback targets:** `797ebad5` pre-arc · `065826c5` enforcement landed, docket unstarted · `d0bedfc1` Wave 1 done, docket unstarted

---

## What the arc produced, in three results

1. **ADR-0252 §5 → NO-GO**, against a criterion pre-registered *before* the run. Measured rather than argued: *the similarity quotient that delivers attribute-invariance is the same one that annihilates structural contrast.* An `add`-vs-`subtract` minimal pair aligns at residual exactly `0.0`. §6's organ-retirement condition was amended because a NO-GO left it naming a trigger that can never fire.

2. **Served capability shrank on purpose, twice.** Deduction: **25 → 4** licensed bands (replays counted as independent trials; 28 distinct cases inflated to 720). Curriculum: the four predicted licences **dissolved to zero** — 652–653 correct *refusals* pooled with 7–8 commitments to clear a **0.000046** margin. **`wrong` stayed 0 in both.** No answer changed; only the claim attached to it.

3. **R-11's instrumentation dissolved its own question.** Nothing is syntactically outside the verified inventory, because `atom_fact`'s template is `{p}` — it matches any string. G-2's fabrications are therefore **mis-reads of admissible surfaces**, not admissions of out-of-inventory constructions, and no gate over the admissibility set can catch them.

**Closed:** G-5…G-12, G-15, G-17, G-19, G-22, H-1, H-6, H-7, H-8 (all five instances), H-10, H-11, H-13 · **Pinned:** G-23 · **Rulings:** 12 executed, 2 stricken, 0 pending.

**Not moved, stated plainly:** comprehension breadth. The reader is still 19 constructions wide and decides 1.0% of `holdout_dev/v1`. Everything here is enforcement and evidence machinery. Track B (widening) and Track C (the chooser) are the next arc.

---

## Errors found in my own work, and how

Three, each surfaced by attacking a mechanism rather than trusting it:

- **A hollow guard in PR-12** — it compared two functions that agree *by construction*; the attack it existed to stop walked past it **and re-sealed the inflated ledger**. Fixed to take the built artifact as input.
- **A hollow spot in pin 3** — the two gate scripts could drift apart invisibly (`294bbe7b`).
- **Two invalid measurement passes in R-11**, both confident and plausible, caught only by asking whether the matcher could still say *no* to `"most birds can fly"`. It could not.

Two earlier statements were also wrong and were corrected in place rather than overwritten: `9efd5a61`'s H-8d claim (corrected in `635f2488`) and `71542e61`'s H-13 fix (corrected in `2cfc6ad2`). Both corrections sit next to the error, because an arc's self-correction chain is its strongest evidence.
