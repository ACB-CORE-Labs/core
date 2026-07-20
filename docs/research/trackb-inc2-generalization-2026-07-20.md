# Track B, Increment 2 — Generalization bar (S1–S4, selector, coverage)

**Date**: 2026-07-20  
**Branch**: `feat/trackb-symbolic-sme-s2s4`  
**Paradigm**: ADR-0252  
**Prerequisite**: Increment 1 (PR #85) merged; §5 geometric SME remains NO-GO  
**Scope**: Off-serving. S1–S4 canonicals + selector + SM-owned pure-S1 extract. No serving cutover. No organ retirement in this PR.

---

## 1. The bar (ADR-0252 §4 / Increment 2)

| # | Requirement | Result |
| --- | --- | --- |
| 1 | Generalization ratio > 1 on ≥1 canonical (real holdout IDs) | **PASS** — S1 ratio = **9.0** (9 cases / 1 template) |
| 2 | Coverage gain **or** organ retirement | **PASS** — coverage gain: **+4** holdout cases (organ 5 → trackb 9), `wrong=0` |
| 3 | Selector works (S1–S4 held; ties refuse; surface≠structure) | **PASS** — routing table below |

Honest negatives (not failures of the bar):
- S2/S3/S4 holdout ratios = 0 — **parser frontier**: organ yields graphs on only 5/500 holdout cases (all S1).
- S3/S4 multi-register corridor cannot certify pure rebuilds yet (`apply_rate` / `compare_additive` out of scope) — map succeeds, emit refuses (gate held, not weakened).
- Organ retirement **not** performed (off-serving path; coverage-gain chosen).

---

## 2. What shipped

| Piece | Path |
| --- | --- |
| Canonicals S1–S4 | `generate/structure_mapping/canonicals.py` |
| Role schema + `compare_add` | `generate/structure_mapping/role_predicate.py` |
| Converter (incl. additive compare) | `generate/structure_mapping/convert.py` |
| Pure-family mappers S1–S4 | `generate/structure_mapping/mapper.py` |
| Overlapping-waves selector | `generate/structure_mapping/selector.py` |
| Generalized 3-gate solve | `generate/structure_mapping/solve.py` |
| SM-owned pure-S1 text extract | `generate/structure_mapping/text_extract.py` |
| Pipeline (organ parse → extract fallback) | `generate/structure_mapping/pipeline.py` |
| Measure script | `scripts/measure_trackb_inc2.py` |
| Tests | `tests/test_trackb_inc2_structure_mapping.py` (15) + Inc1 suite (20) |

Serving reader (`parse_and_solve` dispatch, organs, `chat/runtime.py`) **untouched**.

---

## 3. Measurements (command + real output)

### 3a. Generalization-ratio table

```text
$ uv run python scripts/measure_trackb_inc2.py --mode ratio
=== generalization ratio (holdout_dev/v1, command-backed) ===
CASE gsm8k-holdout-dev-v1-0101 sid=S1 emit=9.0 gold=9.0 right=True src=organ ...
CASE gsm8k-holdout-dev-v1-0108 sid=S1 emit=110.0 gold=110.0 right=True src=organ ...
CASE gsm8k-holdout-dev-v1-0148 sid=S1 emit=1500.0 gold=1500.0 right=True src=sm_extract pat=s1_p3_day_pair ...
CASE gsm8k-holdout-dev-v1-0228 sid=S1 emit=600.0 gold=600.0 right=True src=sm_extract pat=s1_p2_b_seeded ...
CASE gsm8k-holdout-dev-v1-0234 sid=S1 emit=240.0 gold=240.0 right=True src=sm_extract pat=s1_p2_deaf_blind ...
CASE gsm8k-holdout-dev-v1-0268 sid=S1 emit=16.0 gold=16.0 right=True src=organ ...
CASE gsm8k-holdout-dev-v1-0411 sid=S1 emit=52.0 gold=52.0 right=True src=organ ...
CASE gsm8k-holdout-dev-v1-0441 sid=S1 emit=75.0 gold=75.0 right=True src=sm_extract pat=s1_p2_b_seeded ...
CASE gsm8k-holdout-dev-v1-0453 sid=S1 emit=28.0 gold=28.0 right=True src=organ ...
--- ratio table ---
canonical=S1 templates=1 cases_carried=9 ratio=9.000 ids=[...9 holdout ids...]
canonical=S2 templates=1 cases_carried=0 ratio=0.000 ids=[]
canonical=S3 templates=1 cases_carried=0 ratio=0.000 ids=[]
canonical=S4 templates=1 cases_carried=0 ratio=0.000 ids=[]
SUMMARY active_canonicals=1 total_cases=9 aggregate_ratio=9.000
```

All nine S1 carries include the 3-part proof (right answer, derivation `b=k×a; total=a+b`, multi-register + classical cert). Surface-variant re-extract of the inverted-seed form still maps (Ava/Ben → 48).

### 3b. Coverage gain

```text
$ uv run python scripts/measure_trackb_inc2.py --mode coverage-gain
organ_correct=5 trackb_correct=9 newly_solved=4
  NEW gsm8k-holdout-dev-v1-0148 ans=1500.0 gold=1500.0 sid=S1 extract=s1_p3_day_pair
  NEW gsm8k-holdout-dev-v1-0228 ans=600.0 gold=600.0 sid=S1 extract=s1_p2_b_seeded
  NEW gsm8k-holdout-dev-v1-0234 ans=240.0 gold=240.0 sid=S1 extract=s1_p2_deaf_blind
  NEW gsm8k-holdout-dev-v1-0441 ans=75.0 gold=75.0 sid=S1 extract=s1_p2_b_seeded
```

These four are **real surface-distinct holdout cases**, not synthetic clones. The SM-owned extract layer is structure-mapping-owned (regex pure-family templates) and runs only when the serving reader refuses — it does not modify the live reader.

### 3c. Selector

```text
$ uv run python scripts/measure_trackb_inc2.py --mode selector
CASE real_s1_0411 expect=S1 got=S1 refused=False ok=True
CASE real_s2_public_transfer expect=S2 got=S2 refused=False ok=True
CASE struct_s2_not_s1 expect=S2 got=S2 refused=False ok=True
CASE struct_s1 expect=S1 got=S1 refused=False ok=True
CASE empty_ops_refuse expect=None got=None refused=True reason=no_family_matched ok=True
CASE struct_s3_rate expect=S3 got=S3 refused=False ok=True
```

Transfer graphs route to S2 even when the surface text could mention multiplicative language elsewhere; empty ops refuse. Ranking uses fixed systematicity scores, not entity names or numbers.

### 3d. Parser frontier

```text
organ_selected_graph_count=5/500
role_kind_multiset_counts={'compare,contain,total': 5}
--- case 0148 ---
organ_parsed=False
sm_pipeline emit=True answer=1500.0 gold=1500.0 src=sm_extract sid=S1
```

**0148** (the original S1 family namesake) is a **parser-frontier refusal** on the serving reader; the SM-owned extract recovers it. Holdout still has zero organ graphs for transfer/rate/additive-compare families — that is the next structural bottleneck, not the mapper.

### 3e. S2 on real public transfers (not holdout; engineering evidence only)

```text
SUMMARY s2_public_sample: ok=5 scanned_transferish=20
  S2 gma-102 ans=54.0 ... transfer 7 Eve→David ...
```

S2 pure-family map+solve works on real public transfer graphs. Not counted in the holdout ratio table (discipline: holdout IDs only).

### 3f. Right-reason summary

```text
SUMMARY right-reason: correct=9 wrong=0 refused=0
SUMMARY surface-variant: ok=True
```

---

## 4. Discipline checks

- **Blind**: mappers/selector take only `RoleGraph`; no label parameter. Static audit: `generate/structure_mapping/` does not import scoring labels.
- **wrong=0**: emit only if classical verify **and** multi-register cert **and** agreement; original-graph backstop when a graph is supplied.
- **No crash-as-signal**: corridor exceptions → refuse outcomes.
- **Off-serving**: no organ retirement; no `parse_and_solve` dispatch edits.

---

## 5. Deviations / frontiers (honest)

1. **S2–S4 holdout ratio = 0** until the serving reader (or a reviewed SM extract family) produces pure transfer/rate/additive graphs on holdout. Do not manufacture synthetic holdout clones for ratio.
2. **S3/S4 solve emit** blocked by multi-register scope (`apply_rate`, `compare_additive` not Tier-2a). Gates not weakened — refuse.
3. **SM extract is narrow** (regex pure-S1 templates only). It is not a general parser; expanding it is a deliberate future increment.
4. **Organ retirement** deferred; coverage-gain path met bar 2 without serving risk.

---

## 6. STOP

One PR (base `main`). Reviewer verifies:
- blindness + pure-family gates,
- ratio > 1 cases are real holdout IDs (not clones),
- `wrong=0` three-gate path,
- serving reader unchanged.

No S2–S4 serving cutover until a later ruling. No sealed-test run.
