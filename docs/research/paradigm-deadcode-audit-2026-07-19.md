# Paradigm dead-code audit — 2026-07-19

**Companion to:** [ADR-0252 — Problem-Solving Paradigm Consolidation](../adr/ADR-0252-problem-solving-paradigm-consolidation.md)
**Branch:** `chore/paradigm-consolidation`
**Scope:** for each of the six retired paradigm formulations, trace every code module/function it
introduced or proposed, prove liveness or deadness by command, and remove only what is provably dead.

## Result summary

**Zero modules were removed.** Every code artifact traceable to the six retired paradigm documents is
in one of three states: (a) never actually built beyond the proposal doc, (b) already removed in a
prior pass, well before this consolidation, or (c) built and now live — imported by the serving reader
or by a protected dependency chain, and/or covered by tests. No candidate satisfied the dead-code bar
(§"Liveness method" below). This is a real finding, not a shortcut: the search was exhaustive across
every module named in the six documents plus a general zero-importer sweep of `generate/`, `core/`,
`evals/`. Because nothing was removed, the Step-0 baseline numbers are unchanged by construction —
there is no "after" run to diverge from "before."

## Liveness method

A candidate is **dead** only if all three hold, verified by command:
1. No live importer — `git grep` for every plausible import form (absolute dotted path, relative
   `from . import X`, relative `from .X import`), reachability from `generate/math_candidate_graph.py`'s
   `parse_and_solve` / `resolve_promotable_*` dispatch, eval runners, and any registry/entry-point/config.
2. No test exercises it — confirmed by the same `git grep` sweep over `tests/`.
3. No current/Accepted ADR references it.

Anything not cleanly meeting all three → **kept**, listed as ambiguous if borderline.

## Candidates traced from the six retired documents

### 1. Semantic-substrate problem-solving master plan (`semantic-substrate-problem-solving-master-plan-2026-06-20.md`)

| Candidate | Verdict | Evidence |
|---|---|---|
| `generate/problem_frame.py`, `problem_frame_builder.py`, `problem_frame_contracts.py`, `generate/kernel_facts.py`, `generate/process_frames.py` | **live — kept** (explicitly protected per task scope) | `git grep -n "problem_frame_contracts\|assess_fraction_decrease\|assess_percent_partition" generate/math_candidate_graph.py` shows `generate/math_candidate_graph.py:822-825` imports `build_problem_frame` and `assess_geometric_proposals` directly — the master plan's own §2.5/§9.1 non-goal (never wire `ProblemFrame` into the candidate graph) was later overridden by a subsequent, separate decision; the module is now load-bearing in the serving path itself. |
| `generate/construction_proposals.py` (PR4, proposal seam) | **never built — nothing to remove** | `find . -iname construction_proposals.py` → no match. |
| Construction catalog: `packs/compile_frames.py`, `packs/schema.py` | **live — kept, out of scope anyway** | Both are general pack-compiler infrastructure used far beyond math frames — `packs/schema.py` defines `MorphologyEntry`, `LexicalEntry`, `AlignmentEdge`, `LanguageRole`, `OOVPolicy`, imported by `ingest/gate.py`, `vocab/manifold.py`, `sensorium/protocol.py`, `alignment/graph.py`, `workbench/logos.py` and 10+ more. `packs/compile_frames.py` is imported by `packs/compile_pack.py` and directly tested (`tests/test_frame_registry_load.py`). Not paradigm-specific; predates and outlives this doc. |
| `packs/data/en_core_math_v1/frames.jsonl` | **0-byte data artifact, not code — out of scope, left untouched** | `wc -c` → 0 bytes. Only reference is a docstring in `teaching/math_frame_ratification.py` pointing at a directory path, not this file. This is the master plan's unshipped construction-catalog (PR3) — but it's a data file, not "code the paradigm left behind" per the task's own framing, and its presence/absence has zero behavioral effect (0 lines parsed either way). Flagged for a human call on cleanup, not removed here. |

### 2. Semantic state-transition blueprint (`SEMANTIC-STATE-TRANSITION-BLUEPRINT.md`)

| Candidate | Verdict | Evidence |
|---|---|---|
| `generate/derivation/state/{model,bind,change,ledger,replay,provenance,source}.py` | **live — kept** (this is exactly the "verify the ledger IF any live organ imports it" case named in the task) | `git grep -n "derivation\.state\|derivation/state"` shows direct imports from `generate/derivation/accumulate.py`, `pool.py`, and from the protected sprint-organ modules `affine_fraction_delta.py`, `giveaway_target_residual.py`, `goal_residual.py`, `question_bound_product.py`, `temporal_tariff.py`, plus `generate/derivation/__init__.py`. Confirmed live dependency of the serving path, not paradigm-only scaffolding — despite its parent ADR (ADR-0184-scoped-semantic-state-transitions.md) never having been promoted past Status: Proposed. |
| `generate/derivation/state/{frames,target,refusals,transfer,compare,rate,time,world,dag}.py` (blueprint Phases S5-S9, plus `frames.py`/`target.py`/`refusals.py`) | **never built — nothing to remove** | `ls generate/derivation/state/` shows only the 7 files above; none of these 9 additional proposed files exist. |
| Classes `EntityMention`, `CueMention`, `SemanticWorld` | **never built — nothing to remove** | `git grep -n "class SemanticWorld\|class EntityMention\|class CueMention"` → no matches anywhere in the repo. |
| `docs/handoffs/CLEANUP-C2-run-lane-migration.md` (referenced by ADR-0174, not this blueprint, but related) | **out of scope — not one of the six named documents, left untouched** | Not in the task's explicit archive list; flagged only as a documentation-staleness note (see ADR-0174 note below), no action taken. |

### 3. Semantic/symbolic binding-graph proposal (`semantic-symbolic-binding-graph-proposal.md`)

| Candidate | Verdict | Evidence |
|---|---|---|
| `SemanticSymbolicBindingGraph`, `SymbolBinding`, `BoundFact`, `BoundEquation`, `BoundUnknown`, `BoundConstraint`, `SourceSpanLink` | **live — kept; this is the same binding graph, not a separate one** | These exact classes are defined in `generate/binding_graph/model.py` (predates/parallels this doc, built under ADR-0132/0133/0134/0135). `git grep` confirms the package is imported by `generate/quantitative_comprehension.py`, `generate/constraint_comprehension/expr.py`, `generate/realize/quantitative.py`, `generate/proof_chain/builder.py`, `core/comprehension_attempt/model.py`, `evals/setup_oracle/signature.py`, `evals/dimensional/runner.py` — 7 live non-test importers. |
| `generate/binding_graph/question_target.py`, `allocation.py` (initially flagged as zero-importer by a naive absolute-dotted-path grep) | **live — kept; grep false negative corrected** | Both are imported via relative import in `generate/binding_graph/__init__.py` (`from .allocation import allocate_symbols`; `from .question_target import (...)`), which itself is imported package-wide. Confirmed by direct `git grep` on `from .allocation import` / `from .question_target import`. |

### 4. Problem-solving capability roadmap v2 (`core-problem-solving-capability-roadmap-v2-2026-06-17.md`)

No new Python files introduced by this document — it's a meta/status roadmap that references
`scripts/gsm8k_post_gate_a1_frontier_microscope.py` (exists, live, referenced by the sprint lookbacks
below) and sets up the "Gate A1/A2" framing the sprint lookbacks implement. No removable candidates.

### 5. GSM8K capability-paradigm sprint 5-12 lookbacks (8 files)

**All 15 organ modules these retrospectives describe are live, currently dispatched, `wrong=0`-gated
serving code — confirmed by direct import trace from `generate/math_candidate_graph.py`.**

`git grep -n "from generate\.derivation\." generate/math_candidate_graph.py` shows direct imports of:
`goal_residual`, `question_bound_product`, `duration_segment_total`, `survey_rate_earnings`,
`round_trip_trip_duration`, `giveaway_target_residual`, `fraction_decrease`, `percent_partition`,
`temporal_tariff`, `affine_fraction_delta`, `affine_comparative_inversion_total`,
`sequential_comparative_scale`, `piecewise_daily_hours_total`, `nested_fraction_remainder_total`,
`loose_crayon_box_capacity`, `bounded_rate_projection`, `closed_reference_affine_aggregate` — 17 of the
18 direct dispatch imports (`r1_reconstruction` is the 18th, imported at module top-level). All exist on
disk, all match the "Implemented organs" tables in the corresponding sprint lookback.

The remaining `generate/derivation/*.py` helper modules (`extract.py`, `clauses.py`, `compose.py`,
`search.py`, `multistep.py`, `verify.py`, `model.py`, `target.py`, `pool.py`, `accumulate.py`,
`comparatives.py`, `calendar_grounding.py`, `product_bridge.py`) were cross-checked individually — each
has 2+ live importers among the protected organ modules above (full `git grep` output retained in the
session transcript). None is an orphan.

The lookbacks themselves explicitly record **rejected** candidates (e.g., "broad `product_bridge`
[wholesale promotion] stays disabled," "wholesale `multiplicative_aggregate` — Rejected," DCS/currency/
`sealed_elimination` families "blocked") — none of those rejected/never-promoted paths were ever built
(`find . -iname "multiplicative_aggregate.py"` → no match), so there is nothing to remove for them
either.

### 6. ADR-0174's deprecated per-category dispatch (ADR-0174 header `Deprecates:` line)

| Candidate | Verdict | Evidence |
|---|---|---|
| Per-category injector dispatch table, `generate/recognizer_anchor_inject.py:233` (as it existed when ADR-0174 was written) | **already removed, prior to this session — nothing to do** | Line 233 of the file today is `def inject_discrete_count_statement(...)`, an unrelated live injector — not a dispatch table. |
| `generate/comprehension/lifecycle_runtime_adapter.py`, `tests/test_reader_coexistence.py` | **already removed, prior to this session — nothing to do** | `find . -iname lifecycle_runtime_adapter.py` and `find . -iname test_reader_coexistence.py` → no matches. |
| `generate/math_parser.py` (ADR-0174's other named deprecation target — "legacy regex parser... survives only as the offline measurement-comparison baseline") | **live — kept** | Still imported by `evals/gsm8k_math/runner.py`, `evals/gsm8k_math/verify.py`, `verify_all.py`, `core/capability/perturbation_b3.py`, `generate/perturbation_suite.py`, and the OOD/bounded-grammar lanes. |
| `--legacy-parser` CLI flag (ADR-0174 says this gates the offline-baseline use of `math_parser.py`) | **flag for documentation correction only — not a code-removal candidate** | The flag does not exist (`git grep -n "legacy.parser" evals/` finds no argparse flag); `docs/handoffs/CLEANUP-C2-run-lane-migration.md` only ever proposed it. ADR-0174's header description of this flag is stale relative to current code. Noted here for a human to correct if ADR-0174 is ever touched again; out of scope to edit an Accepted ADR's body as part of this consolidation. |

## General orphan sweep — `generate/`, `core/`, `evals/`

Ran a zero-importer sweep (absolute dotted-path + relative-import forms, excluding `runner.py`/
`__main__.py`/`if __name__ == "__main__"` entry-point scripts, which are legitimately invoked via
`python -m` and have no Python-level importer by design) across 531 non-entry-point modules under the
three roots. 22 files came back as zero-importer:

- 20 are `__init__.py` package markers for unrelated, pre-existing eval domains (`classical_literature_ood`,
  `koine_greek_fluency`, `hebrew_fluency`, `foundational_biology_ood`, `foundational_physics_ood`,
  `english_fluency_ood`, `elementary_mathematics_ood`, `adversarial_identity`, `multi_step_reasoning`,
  `discourse_paragraph`, `inference_closure`, `calibration`, `monotonic_learning`, `cross_domain_transfer`,
  `introspection`, `multi_agent_composition`, `provenance`, `symbolic_logic`, `sample_efficiency`,
  `compositionality`) — these are implicitly loaded by Python's package machinery when their sibling
  `runner.py` is invoked via `python -m evals.<domain>.runner`; a package `__init__.py` never needs an
  explicit textual import to be live.
- `evals/baseline_runner.py` — documented and referenced in `docs/PROGRESS.md` and
  `docs/frontier_baselines.md` as an extension point (`BaselineModel` protocol); not code-imported
  because it's designed to be extended/invoked directly, not imported by other modules.
- `evals/gsm8k_math/holdout_dev/v1/split.py` — the one-time deterministic split-generation script for
  the holdout_dev lane (per that lane's own README); run once to produce `cases.jsonl`, not imported.

**None of these 22 trace back to any of the six retired paradigm documents.** They are pre-existing,
unrelated repo infrastructure. Removing them would be outside this consolidation's stated scope
("remove only the provably-dead code those abandoned paradigms left behind") even where liveness is
debatable on its own terms — flagged here for visibility, not acted on.

## Protected list — verified untouched

Spot-checked per the task's explicit protect list: `generate/math_solver.py`, `math_completeness.py`,
`math_roundtrip.py`, `math_candidate_parser.py`, `math_candidate_graph.py`, `generate/problem_frame_contracts.py`,
`generate/derivation/fraction_decrease.py`, `evals/turn_program.py`, `evals/multi_register_program.py`,
`core/physics/quantity_kernel.py`, `cognitive_lifecycle.py`, `dynamic_manifold.py` — none were modified;
`git status` / `git diff` against the Step-0 baseline commit show no changes to any file outside
`docs/paradigm-archive/`, `docs/adr/`, and `docs/research/` for the entirety of this consolidation.

## Baseline numbers (Step 0, and unchanged — no code was removed)

Captured on `chore/paradigm-consolidation` at the branch tip (`origin/main` = `forgejo/main` =
`1de6dbc9`), before any change:

```
$ uv run core test --suite smoke -q
176 passed in 132.32s (0:02:12)

$ uv run core test --suite full -q
13163 passed, 111 skipped, 1 xfailed, 173 warnings in 1854.77s (0:30:54)
# 173 warnings are benign engine_state/identity-checkpoint-revision RuntimeWarnings — the checkpoint
# on disk records the git SHA it was written under, and the Part-A docs-only commit changed the repo
# SHA. No test failed or was skipped because of them; 0 failures.

$ uv run python -m evals.gsm8k_math.holdout_dev.v1.runner
holdout_dev: correct=5 wrong=0 refused=495 (n=500)
```

Because zero code was removed, there is no separate "after" measurement to report — the baseline
figures above are also the final figures. `wrong=0` on both the train-lookback-gated serving path
(smoke/full suites) and the held-out 500-case lane is unchanged.
