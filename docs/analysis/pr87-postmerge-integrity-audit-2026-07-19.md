# PR #87 Post-Merge Integrity Audit

**Date:** 2026-07-19  
**Audit branch:** `chore/postmerge-pr87-integrity-audit`  
**Worktree:** `../core-postmerge-pr87-integrity-audit`  
**Merged subject:** Forgejo PR #87 — `feat(eval): deterministic relational operator ablation + HE/GRC Logos roadmap`  
**Merge commit:** `5fae5a67f27fdc5c58b7e11fd71a18af99403a56`  
**Merge-base (pre-PR main tip):** `d8d62b8e`  
**PR tip commit (last feature commit):** `08881ab6`  
**Authority:** code, fixtures, git diff, call-chain traces, and local reproduction — **not** prior dossier trust.

**Scope discipline:** Audit-only. No production-code edits. No redesign. No HE/GRC implementation.

---

## Verdict

**VERIFIED: NO CORRECTIVE PR NEEDED**

PR #87 adds an isolated eval/ablation surface, sealed fixtures, tests, and planning docs. It does **not** alter serving, refusal gates, pack validation, canonical fraction-decrease organ code, geometric closure thresholds, feature flags, or existing benchmark score logic. Residual A2k scale>1 admission is pre-existing, documented, isolated outside the n=8 sealed set, and not masked by this merge.

---

## Seven-item matrix

| # | Claim | Verdict | Exact evidence (path / symbol / line) | Command / test | Risk | Required action |
|---|-------|---------|----------------------------------------|----------------|------|-----------------|
| 1 | **Canonical semantics** — ablation invokes production fraction-decrease / A2k path for operator; baseline is intentional non-geometric contrast, not a second serving organ | **PASS (with noted harness duplication)** | Operator: `generate/relational_operator_ablation.py` `run_operator` → `resolve_promotable_fraction_decrease` (L361, import L40–45). Production organ: `generate/derivation/fraction_decrease.py` `resolve_promotable_fraction_decrease` L221–225 → `compose_fraction_decrease` L197–218 → `build_fraction_decrease` L103–138 (CGA `versor_apply`). Baseline: `run_baseline` L232–331 uses `build_problem_frame` + `assess_fraction_decrease` + shared `_asks_decrease_delta` / `_has_hazard_surface` (imports, not reimplemented) + harness-local `_extract_base_and_scale` L195–229 and pure rational `base * (1 - scale)` L307–308. No re-parse of “decrease to N/M of” prose in harness. | `PYTHONPATH=. python3 -c "from generate.derivation.fraction_decrease import resolve_promotable_fraction_decrease; …"`; `tests/test_relational_operator_ablation.py::test_operator_commits_geometric_binding_with_versor_integrity` | **Low.** Harness baseline duplicates *role extraction + rational formula + scale∈(0,1) check* for scientific contrast. Divergence risk if frame roles and organ base-picking disagree on multi-base prose; sealed gold has single base. Private `_asks_*` / `_has_hazard_*` import couples baseline refuse gates to organ internals (intentional shared gate). | None for merge integrity. Future organ work should keep baseline as non-serving contrast only. |
| 2 | **Fixture independence** — n=8 expected labels are static, hand-justified, not solver-generated | **PASS** | Static oracle: `evals/relational_operator_ablation/v1/cases.jsonl` (8 lines). Gold: `roa-v1-0001` 84×(1−3/4)=**21**; `roa-v1-0002` 60×(1−2/3)=**20** (notes field states formula). Adversarial 0003–0008: `expected_answer: null`, `expected_outcome: "refused"` with per-case hazard notes (final-value; affine confuser; percent partition; distractor qty; decrease-by language; multi-fraction). Runner loads JSONL only (`runner.py` `_load_cases` L45–63); does not write cases. Committed `report.json` is measurement artifact, not expectation source. | Independent hand math + live organ: all 8 organ outcomes match fixture labels without reading expected_answer into the solver. | **Low.** Tests assert against same static labels (normal sealed-eval pattern). Not a circular oracle: gold numbers are grade-school arithmetic from problem text; refuse labels match organ refuse, independently re-checked via `resolve_promotable_fraction_decrease is None`. | None. |
| 3 | **Honest condition labels** — baseline/operator equality is agreement on this lane, not improvement; depth inactive for EN-only; no global HE/GRC negation | **PASS** | Condition semantics in module docstring L16–25 and runners: `baseline` L232–331; `operator` L334–402; `depth` L405–437 (`inactive_no_mapping`, equals operator answer); `metadata_only` L440–522 (`assess_contracts(..., depth=)` decorate then same `resolve_promotable_*`). Runner findings L155–168: “should agree when both commit”; scientific_note records depth inactive on English-only. Dossier L120: metadata “does not improve arithmetic on **this English slice**”; HE/GRC roadmap L12–13, L28–29: do **not** generalize to “Hebrew/Greek never help.” Sealed counts 2/0/6 identical across baseline/operator/depth/metadata_only — equality, not uplift. | Runner stdout counts; `test_depth_condition_records_inactive_mapping_and_matches_operator`; `test_baseline_and_operator_agree_when_both_commit` | **Low.** Misread risk if a reader equates “operator” with “better”; text counters that. | None. |
| 4 | **Scale > 1** — pre-existing A2k admit; PR neither masks nor normalizes; outside n=8 interpretation | **PASS (gap real; isolated)** | Obligation path: `assess_fraction_decrease` L471–473 adds `scale_out_of_range` when not `(0 < scale.value < 1)`. Geometric binding: `_versor_binding_from_scale_value` L937–938 admits any finite `k > 0` (**no** upper bound). Fallback: `_resolve_fraction_decrease_contract` L179–194 prefers obligation-complete runnable, else geometric with bindings. **Runtime (this audit):** text `…decrease to 5/4…40 feet…decrease by?` → obligation `runnable=False` missing includes `scale_out_of_range`; geom `runnable=True` binding `5/4`; `resolve_promotable_fraction_decrease` → **≈ −10.0**. Baseline refuses (assessment not runnable). Sealed `cases.jsonl` contains **no** scale>1 surfaces. Test: `test_preexisting_scale_out_of_range_gap_isolated` L239–254 documents split; soft allow `{refused, wrong}` so a future refuse-fix does not break. Diff: `fraction_decrease.py` **byte-identical** merge-base↔merge (`shasum` equal). | Minimal repro (below). Unit test above. | **Medium product risk (pre-existing organ), zero PR-#87 introduction risk.** Soft test does not hard-pin current wrong-commit forever (by design). n=8 scores unaffected. | **Not a PR #87 corrective.** Optional later organ PR: tighten geometric scale to match obligation `(0,1)` — separate scope. |
| 5 | **Production / gate isolation** — PR does not alter serving, gates, packs, organ semantics, closure, flags, benchmark scores | **PASS** | Diff `d8d62b8e..5fae5a67` file set (10 paths only): 3 docs under `docs/analysis/`; `evals/relational_operator_ablation/**`; `generate/relational_operator_ablation.py` (**new**); `tests/test_relational_operator_ablation.py`. Zero line diff to `generate/derivation/`, `generate/problem_frame*.py`, `generate/construction_affordances.py`, `packs/`, `chat/`, `algebra/`. `relational_operator_ablation` **not** imported by `math_candidate_graph`, `chat/`, or `core/` serving paths. `serving_allowed=True` for fraction_decrease remains pre-existing in `construction_affordances.py` (unchanged). | `git diff d8d62b8e..5fae5a67 --name-only`; `git diff … -- generate/derivation/ … \| wc -l` → 0; `rg relational_operator_ablation generate/math_candidate_graph.py chat/ core/` → none | **None** for isolation. New `generate/` module is production-*adjacent placement* but eval-only consumers. | None. |
| 6 | **HE/GRC roadmap authority** — documentation only; draft/disconnected honesty; observed-morph rule | **PASS** | Single new doc: `docs/analysis/hebrew-koine-greek-logos-pack-capability-roadmap-2026-07-19.md`. No pack JSONL/data/compiler changes in diff. Verdict L18: READY ONLY FOR PREREQUISITE WIRING. Source packs draft/disconnected L22, L49, L68, Phase 0 L122. No-go list L155–167: no English→morph, no bulk pack build, no holonomy crown claim. Next unit L199–203 is **future** branch name only. Ablation boundary L26–29: EN depth inert; do not reopen fixtures without defect. | Diff name-only + doc read | **None** if future implementers follow no-go list. | None on this merge. |
| 7 | **Regression / reproducibility** — recorded commands green; report digest stable | **PASS** | Ablation tests **20 passed**; runner **passed** `report_sha256=53df6d17df934f0c44f5d1063b16259f6d9db0b59834b7ca20f895eb5e5719c7` matches committed `report.json`; dual `build_report` identical. Pre-existing: sprint8 affine/fraction tests **37 passed**; problem_frame_contracts + construction_affordances + proportional_decrease **green**. Smoke suite run recorded in Reproduction evidence. | See Reproduction evidence | **Low.** Runner rewrites `report.json` on disk when executed (measurement overwrite); digest stable. | None. |

---

## Diff classification

Merge range: `d8d62b8e..5fae5a67` (includes merge commit + 5 feature commits).

| Path | Classification | Notes |
|------|----------------|-------|
| `docs/analysis/relational-operator-ablation-cartography-2026-07-19.md` | documentation only | Phase 1 ledger |
| `docs/analysis/relational-operator-ablation-dossier-2026-07-19.md` | documentation only | Measurement dossier |
| `docs/analysis/hebrew-koine-greek-logos-pack-capability-roadmap-2026-07-19.md` | documentation only | Planning; no pack authority |
| `evals/relational_operator_ablation/__init__.py` | test/eval harness only | Package marker |
| `evals/relational_operator_ablation/v1/__init__.py` | test/eval harness only | Package marker |
| `evals/relational_operator_ablation/v1/cases.jsonl` | test/eval harness only | Static sealed fixtures |
| `evals/relational_operator_ablation/v1/runner.py` | test/eval harness only | Measurement runner |
| `evals/relational_operator_ablation/v1/report.json` | test/eval harness only | Committed measurement artifact |
| `tests/test_relational_operator_ablation.py` | test/eval harness only | 20 unit/integration/adversarial tests |
| `generate/relational_operator_ablation.py` | **production-adjacent but behavior-preserving** | **New** module; not on serving path; imports production organ for operator condition; baseline is harness-local rational contrast |

**Absent from diff (verified):** any edit to fraction-decrease organ, problem-frame contracts, construction affordances / `serving_allowed`, pack manifests/data/compiler, chat runtime, algebra closure, existing GSM8K score fixtures, feature flags.

**Not present:** production semantic change; gate/config change.

---

## Canonical semantics (detail)

### Operator path (production)

```text
case.problem
  → resolve_promotable_fraction_decrease(text)     # fraction_decrease.py:221
      → compose_fraction_decrease
          → _resolve_fraction_decrease_contract    # build_problem_frame + assess_contracts / assess_geometric_proposals
          → build_fraction_decrease                # base extract + versor_apply dilation
          → self-verify
  → AblationResult.answer = resolution.answer
```

This **is** the live Gate A2k entry also used by `generate/math_candidate_graph.py` (pre-existing import of `resolve_promotable_fraction_decrease`). Ablation does not replace that graph; it calls the same function with raw text.

### Baseline path (harness contrast)

```text
case.problem
  → build_problem_frame
  → assess_fraction_decrease          # obligation completeness + scale_out_of_range
  → _asks_decrease_delta(question)    # shared private organ helper
  → _has_hazard_surface(...)          # shared private organ helper
  → _extract_base_and_scale(frame)    # HARVEST: unique decrease_to_fraction roles → Fraction values; require 0<scale<1
  → answer = float(base * (1 - scale))  # pure rational; no VersorBinding
```

**Harmless orchestration:** condition dispatch, scoring, readback assembly, depth provenance records, metadata decoration check.

**Semantic duplication (harness-only, intentional):**

| Symbol | Lines | What is duplicated | Production counterpart |
|--------|-------|--------------------|------------------------|
| `_extract_base_and_scale` | 195–229 | Role→value map for base/scale; scale∈(0,1) | `assess_fraction_decrease` roles + L471–473; organ `_current_base_quantity` (different base heuristic) |
| rational formula | 307–308 | `base*(1-scale)` | Geometric dilation then subtract in `build_fraction_decrease` L120–138 (math-equivalent for k∈(0,1)) |

**Not duplicated:** slash-fraction prose regex; multi-fraction hazard logic body (imported); serving dispatch; pack load.

### Depth / metadata

- `run_depth`: answer ≡ `run_operator`; `DepthContribution.validity = "inactive_no_mapping"`; empty pack/record ids.
- `run_metadata_only`: synthetic or override he/grc root labels into `assess_contracts(..., depth=)`; answer still from `resolve_promotable_fraction_decrease` only.

---

## Fixture independence (detail)

| case_id | Independent justification | Organ live outcome |
|---------|---------------------------|--------------------|
| roa-v1-0001 | 84×(1−3/4)=21; train_sample_0005 shape; asks decrease-by | answer≈21 |
| roa-v1-0002 | 60×(1−2/3)=20; sibling | answer≈20 |
| roa-v1-0003 | Final-value Q (“be” not “decrease by”) | refuse |
| roa-v1-0004 | “1/4 more than” affine confuser | refuse (hazard) |
| roa-v1-0005 | Percent partition out of family | refuse (hazard) |
| roa-v1-0006 | Two temperatures (84 + cabin 40); ambiguous base | refuse |
| roa-v1-0007 | “decrease by 3/4 of” not “decrease to … of” | refuse |
| roa-v1-0008 | Two slash-fractions 3/4 and 1/2 | refuse (hazard) |

No generator script writes `cases.jsonl`. Expectations are static data fields.

---

## Scale > 1 (detail)

**Root cause (pre-merge, pre-PR, still present):** geometric scale binding allows any `k > 0`; obligation assessment requires `0 < k < 1`; contract resolver falls back to geometric bindings when obligation is not runnable.

**Minimal repro (audit machine):**

```bash
cd ../core-postmerge-pr87-integrity-audit
PYTHONPATH=. python3 - <<'PY'
from generate.derivation.fraction_decrease import resolve_promotable_fraction_decrease
from generate.problem_frame_builder import build_problem_frame
from generate.problem_frame_contracts import assess_fraction_decrease, assess_geometric_proposals
text = (
  "In one hour, the river will decrease to 5/4 of its level. "
  "If the current level is 40 feet, what will the level decrease by?"
)
a = assess_fraction_decrease(build_problem_frame(text))
print(a.runnable, a.missing_bindings)
g = next(x for x in assess_geometric_proposals(build_problem_frame(text)) if x.candidate_organ=="fraction_decrease")
print(g.runnable, [b.semantic_identity for b in g.bindings])
print(resolve_promotable_fraction_decrease(text).answer)
PY
```

**Observed (SHA `5fae5a67`):** obligation not runnable (`scale_out_of_range`, …); geom runnable with `5/4`; promotable answer ≈ `-10.0`.

**PR #87 effect:** none on this path (organ file checksum unchanged). Documents via unit test + dossier remaining-gaps row. Sealed n=8 does not include scale>1 → **no change to sealed score interpretation**.

---

## HE/GRC roadmap authority boundary (detail)

- Diff adds **only** the roadmap Markdown under `docs/analysis/`.
- No `packs/data/*`, `packs/he/*`, `packs/grc/*`, `packs/el/*`, compiler, manifest, or `DEPTH_PACK_IDS` edits.
- Roadmap states source `packs/{he,grc,el}` draft/disconnected vs LIVE `packs/data/*`.
- Explicit rule: only observed, validated morphology may produce a future constraint; English→pseudo-depth forbidden.

---

## Reproduction evidence

| Field | Value |
|-------|--------|
| Commit SHA | `5fae5a67f27fdc5c58b7e11fd71a18af99403a56` |
| Branch | `chore/postmerge-pr87-integrity-audit` @ `forgejo/main` |
| Python | 3.14.6 (`/opt/homebrew/bin/python3`) |
| uv | 0.8.22 |
| OS | macOS (host of local-first CI doctrine) |

### Commands and outcomes

```text
# Ablation unit/integration (PR-recorded)
PYTHONPATH=. python3 -m pytest -q tests/test_relational_operator_ablation.py
→ 20 passed in 0.66s

# Ablation runner (PR-recorded)
PYTHONPATH=. python3 -m evals.relational_operator_ablation.v1.runner
→ passed: true
→ operator/baseline/depth/metadata_only: correct=2 wrong=0 refused=6 n=8
→ invalid (adversarial n=6): correct=0 wrong=0 refused=6
→ report_sha256: 53df6d17df934f0c44f5d1063b16259f6d9db0b59834b7ca20f895eb5e5719c7
→ live build_report digest == committed report.json digest

# Pre-existing fraction-decrease / affine organ tests
PYTHONPATH=. python3 -m pytest -q \
  tests/test_math_candidate_graph_sprint8_r6_affine_lift.py \
  tests/test_math_candidate_graph_sprint8_review_patch.py
→ 37 passed in 1.60s

# Problem-frame / construction / proportional decrease
PYTHONPATH=. python3 -m pytest -q \
  tests/test_problem_frame_contracts.py \
  tests/test_construction_affordances.py \
  tests/test_proportional_decrease_proposal.py
→ all passed (36 tests in this invocation)

# Production path identity across PR
shasum of generate/derivation/fraction_decrease.py at d8d62b8e == 5fae5a67
git diff d8d62b8e..5fae5a67 -- generate/derivation/ generate/problem_frame*.py \
  generate/construction_affordances.py packs/ chat/ algebra/ → empty

# Smoke (PR-recorded merge-bar parity)
uv run core test --suite smoke -q
→ 176 passed in 132.61s (CPython 3.12.13 via uv .venv)
```

Targeted pre-existing + ablation lanes verify PR #87 surface; smoke confirms no ambient merge-bar breakage at audit HEAD.

---

## If corrective work is required

**Not required for PR #87 merge integrity.**

Optional **separate** future organ PR (out of scope here; pre-existing gap only):

| Field | Recommendation |
|-------|----------------|
| Branch | `fix/a2k-fraction-decrease-scale-range` |
| Worktree | `../core-a2k-fraction-decrease-scale-range` |
| Minimal files | `generate/problem_frame_contracts.py` (`_versor_binding_from_scale_value` and/or `_fraction_decrease_scale_binding`); possibly `generate/derivation/fraction_decrease.py` self-verify; tests under existing sprint8 / new pin |
| Regression tests | Hard-pin: scale `5/4` text → `resolve_promotable_fraction_decrease is None`; baseline and operator both refuse; sealed ROA n=8 still 2/0/6 |
| Acceptance | wrong=0 on organ confusers; no serving flag churn; smoke + targeted math tests green |

No rollback of PR #87 is indicated.

---

## Audit method notes (anti-trust of prior dossier)

1. Diff inventory and empty-diff proof on production paths.  
2. Full read of `generate/relational_operator_ablation.py`, runner, cases, tests.  
3. Trace into `fraction_decrease.py` and `problem_frame_contracts.py` scale/binding gates.  
4. Independent gold arithmetic and live organ refuse matrix for all 8 fixtures.  
5. Runtime scale>1 admit reproduction.  
6. Roadmap read for authority language; packs absent from diff.  
7. Re-run ablation + pre-existing organ tests; digest equality with committed report.

**Deliberately not used as authority:** prior session narrative; cartography/dossier claims without re-verification (claims re-checked against code).
