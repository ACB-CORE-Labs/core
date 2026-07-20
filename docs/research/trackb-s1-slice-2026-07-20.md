# Track B, Increment 1 — Symbolic Structure-Mapping S1 vertical slice

**Date**: 2026-07-20  
**Branch**: `feat/trackb-symbolic-sme-s1`  
**Paradigm**: ADR-0252 (Expert Structure-Mapping on a Predictive-Processing Substrate)  
**§5 status**: NO-GO for geometric SME (`conformal_procrustes` is Kabsch/Umeyama and presupposes role correspondence). PRs #83 and #84 closed as superseded.  
**Scope**: S1 only (compare-multiplicative-then-total). Off-serving. No S2–S4. No serving cutover.

---

## 1. What shipped

| Piece | Path | Role |
| --- | --- | --- |
| Role-predicate schema | `generate/structure_mapping/role_predicate.py` | Typed `contain` / `transfer` / `compare` / `rate` / `total` |
| Converter | `generate/structure_mapping/convert.py` | Deterministic `MathProblemGraph` → `RoleGraph` |
| S1 canonical | `generate/structure_mapping/canonicals.py` | `compare(b,a,k) ∧ contain(a,…) ∧ total(a,b,sum)` — role vars only |
| Symbolic mapper | `generate/structure_mapping/mapper.py` | Relational match → binding or refuse; **no gold labels** |
| Solve corridor | `generate/structure_mapping/solve_s1.py` | Binding → graph → classical `solve`+`verify` **and** multi-register certificate; emit only if both agree |
| Scoring labels (isolated) | `evals/structure_mapping/scoring/` | Gold S1 ids for scoring only; forbidden from mapper imports |
| Measure script | `scripts/measure_trackb_s1_slice.py` | Blind holdout / FP / surface-variant / vs-organ |
| Unit tests | `tests/test_trackb_s1_structure_mapping.py` | 16 tests driving shipped code |

Serving reader (`parse_and_solve` dispatch, `resolve_promotable_*`, `chat/runtime.py`) **untouched** (diff bytes vs main = 0).

---

## 2. Discipline checks

### Blindness
- Mapper signature: `map_to_s1(role_graph: RoleGraph)` — no label parameter.
- Static audit: `generate/structure_mapping/` does not import `evals.structure_mapping.scoring` or load `holdout_dev_v1_labels.jsonl`.
- Labels enter only after map decisions, in the measure script / scorer.

### No crash-as-signal
- Solve path catches `MultiRegisterError` / classical failures and returns refuse outcomes; exceptions are never treated as residual scores.

### wrong=0
- Emit only when classical verifier passes **and** multi-register chain is certified **and** answers agree within relative 1e-6.

---

## 3. Measurements (command + real output)

### 3a. Parse→role coverage on S1 holdout cohort

```text
$ uv run python scripts/measure_trackb_s1_slice.py --mode coverage
=== parse→role coverage on S1 holdout ===
gsm8k-holdout-dev-v1-0101 parsed=True kinds=['compare', 'contain', 'total'] mapped_s1=True refuse=None
gsm8k-holdout-dev-v1-0108 parsed=True kinds=['compare', 'contain', 'total'] mapped_s1=True refuse=None
gsm8k-holdout-dev-v1-0268 parsed=True kinds=['compare', 'contain', 'total'] mapped_s1=True refuse=None
gsm8k-holdout-dev-v1-0411 parsed=True kinds=['compare', 'contain', 'total'] mapped_s1=True refuse=None
gsm8k-holdout-dev-v1-0453 parsed=True kinds=['compare', 'contain', 'total'] mapped_s1=True refuse=None
```

Coverage: **5/5** S1 organ cases parse → role graph with `{compare, contain, total}` and map to S1.

### 3b. Right-for-right-reason (S1 holdout)

```text
$ uv run python scripts/measure_trackb_s1_slice.py --mode right-reason
=== S1 right-for-right-reason (holdout_dev/v1 S1 cohort) ===
CASE gsm8k-holdout-dev-v1-0101 emit=9.0 gold=9.0 match=True wrong_flag=False derivation='S1: Frankie = 2.0 × Eduardo; Eduardo = 3.0; total = Eduardo + Frankie = 3.0 + 2.0*3.0 = 9.0' mr_cert=True classical_v=True binding={'a': 'Eduardo', 'b': 'Frankie', 'k': 2.0, 'a_value': 3.0, 'unit': 'lasts', 'canonical_id': 'S1'} ...
CASE gsm8k-holdout-dev-v1-0108 emit=110.0 gold=110.0 match=True ... derivation='S1: Dana Point Beach = 4.0 × Newport Beach; ...'
CASE gsm8k-holdout-dev-v1-0268 emit=16.0 gold=16.0 match=True ... derivation='S1: Bruce Scored 4 Goals While Michael = 3.0 × Bruce; ...'
CASE gsm8k-holdout-dev-v1-0411 emit=52.0 gold=52.0 match=True ... derivation='S1: male students = 3.0 × female students; ...'
CASE gsm8k-holdout-dev-v1-0453 emit=28.0 gold=28.0 match=True ... derivation='S1: Olaf = 3.0 × dad; dad = 7.0; total = dad + Olaf = 7.0 + 3.0*7.0 = 28.0' ...
SUMMARY right-reason: correct=5 wrong=0 refused=0 n=5
```

**Result**: `correct=5 wrong=0 refused=0`. Every emit carries a derivation of the form `b = k×a; total = a+b`, with multi-register certificate + classical verify both true.

> Note on residuals: early runs emitted multi-register decoded floats (~`8.999999982`). That is geometric relaxation noise, **not** a zero residual trophy. The ship path requires MR certification then emits the classically verified scalar once corridors agree (relative 1e-6). Both corridors remain mandatory.

### 3c. False-positive / separability

```text
$ uv run python scripts/measure_trackb_s1_slice.py --mode false-positive
=== A: holdout_dev/v1 non-S1 cases (parse→map) ===
SUMMARY holdout-non-S1: fp=0 tn=495 n_non_s1=495 parse_fail_among_non_s1=495 fp_rate=0.000000
NOTE: holdout_dev/v1 currently yields selected_graph on only the 5 S1 organ cases; non-S1 holdout FP is vacuous at the graph layer when parse_fail=495. Layer B/C are the real separability tests.
=== B: synthetic non-S1 graphs ===
  transfer: mapped_s1=False refuse=non_s1_has_transfer
  contain_total_no_compare: mapped_s1=False refuse=compare_count_not_one:0
  compare_no_total: mapped_s1=False refuse=missing_total_query
  compare_with_b_seed: mapped_s1=False refuse=b_has_independent_contain_not_pure_s1
  apply_rate: mapped_s1=False refuse=non_s1_has_rate
SUMMARY synthetic: fp=0 tn=5 n=5 fp_rate=0.000000
=== C: other gsm8k_math corpora non-compare graphs ===
SUMMARY other-corpus non-S1 graphs: fp=0 tn=135 n=135 fp_rate=0.000000
```

**Honest reading**:
- Layer A (holdout non-S1): **vacuous at graph level** — the serving reader produces `selected_graph` only for the five S1 cases on this split. Reporting `fp_rate=0` here without the NOTE would be the same class of cheat as prior geometric “GO”s. We refuse that claim.
- Layer B (synthetic): **0/5** false positives on transfer / additive-total / compare-without-total / dual-seed compare / rate.
- Layer C (other corpora, 135 non-compare graphs): **0/135** false positives (mostly transfers from `public/`).

### 3d. Surface-variant generalization (re-parse)

```text
$ uv run python scripts/measure_trackb_s1_slice.py --mode surface-variant
BASE_ID gsm8k-holdout-dev-v1-0108
BASE_TEXT Dana Point beach has four times the number of sharks as Newport Beach. If Newport Beach has 22 sharks, how many sharks are there in total on the two beaches?
VARIANT_TEXT Cedar Cove beach has five times the number of dolphins as Harbor Beach. If Harbor Beach has 11 dolphins, how many dolphins are there in total on the two beaches?
BASE_MAP mapped_s1=True binding k=4.0 a_value=22.0 ...
VARIANT_MAP mapped_s1=True binding={'a': 'Harbor Beach', 'b': 'Cedar Cove Beach', 'k': 5.0, 'a_value': 11.0, 'unit': 'dolphins', ...}
VARIANT_SOLVE emitted=True answer=66.0 expected=66.0 derivation='S1: Cedar Cove Beach = 5.0 × Harbor Beach; Harbor Beach = 11.0; total = ... = 66.0'
SUMMARY surface-variant: map=True k_ok=True a_ok=True names_ok=True ans_ok=True
```

Re-parsed renamed/re-numbered text still maps to S1 with the **new** bindings and solves correctly. Driven by relations, not surface tokens.

### 3e. Side-by-side vs S1 surface organ

```text
$ uv run python scripts/measure_trackb_s1_slice.py --mode vs-organ
case_id                               organ     trackb       gold organ_ok    tb_ok    map
gsm8k-holdout-dev-v1-0101               9.0        9.0        9.0     True     True   True
gsm8k-holdout-dev-v1-0108             110.0      110.0      110.0     True     True   True
gsm8k-holdout-dev-v1-0268              16.0       16.0       16.0     True     True   True
gsm8k-holdout-dev-v1-0411              52.0       52.0       52.0     True     True   True
gsm8k-holdout-dev-v1-0453              28.0       28.0       28.0     True     True   True
```

Track B matches the organ on all five S1 cases (answer + map). Organ path remains the serving `parse_and_solve`; Track B is a parallel off-serving structure-map → certificate path.

---

## 4. Unit tests

```text
$ uv run pytest tests/test_trackb_s1_structure_mapping.py -v
16 passed in 0.62s
```

Includes real holdout texts, refuse paths, blindness import audit, and dual-corridor emit.

---

## 5. Baselines (serving invariant)

Pre-edit (worktree at main tip `1ccef491`, before Track B code):

```text
holdout report (committed): {'correct': 5, 'refused': 495, 'wrong': 0} n=500
uv run core test --suite smoke -q → 176 passed in 134.05s
```

Post-edit: same smoke suite (off-serving code only; serving modules diff empty). Holdout serving numbers unchanged by construction (no live path edits).

---

## 6. Explicit non-claims / STOP gate

- **Not claimed**: geometric SME revival; S2–S4 coverage; serving cutover; sealed-test movement.
- **Not claimed**: holdout non-S1 graph-level separability beyond the vacuous parse layer — only synthetic + other-corpus graphs.
- **Not claimed**: case 0148 (classic “twice the total…”) — reader currently refuses parse; out of converter reach until parse coverage grows.
- **STOP**: human reviewer verifies this slice against the code before any generalization.

---

## 7. Inventory: proven vs assumed

| Item | Status |
| --- | --- |
| S1 map+solve on organ cohort (5) | **Proven** (commands above) |
| wrong=0 on emitted path | **Proven** |
| Surface-variant re-parse | **Proven** |
| FP on synthetic + 135 non-compare graphs | **Proven** |
| Holdout non-S1 graph FP | **Unclaimed** (vacuous parse layer) |
| Generalization to S2–S4 | **Not in scope** |
| Serving supersede of organ | **Not in scope** |
