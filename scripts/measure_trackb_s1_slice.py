"""Blind measurement for Track B Increment 1 (S1 symbolic structure-mapping).

Usage (from worktree root)::

    uv run python scripts/measure_trackb_s1_slice.py --mode right-reason
    uv run python scripts/measure_trackb_s1_slice.py --mode false-positive
    uv run python scripts/measure_trackb_s1_slice.py --mode surface-variant
    uv run python scripts/measure_trackb_s1_slice.py --mode vs-organ
    uv run python scripts/measure_trackb_s1_slice.py --mode all

Labels are loaded only in scoring branches (after map decisions). The mapper
API is never passed a structure label.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from evals.structure_mapping.scoring.labels import (
    S1_HOLDOUT_CASE_IDS,
    load_structure_labels,
    score_label,
)
from generate.math_candidate_graph import parse_and_solve
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import StructureMapRefuse, StructureMapResult, map_to_s1
from generate.structure_mapping.solve_s1 import try_s1_structure_map_and_solve

HOLDOUT_CASES = Path("evals/gsm8k_math/holdout_dev/v1/cases.jsonl")


def _load_cases() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in HOLDOUT_CASES.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        out[row["id"]] = row
    return out


def _map_decision(problem: str) -> dict:
    """Parse → convert → map. Never loads labels."""
    parsed = parse_and_solve(problem)
    if parsed.selected_graph is None:
        return {
            "parsed": False,
            "mapped_s1": False,
            "refuse": parsed.refusal_reason or "no_graph",
            "binding": None,
            "role_kinds": [],
            "organ_answer": parsed.answer,
            "organ_refusal": parsed.refusal_reason,
        }
    rg = graph_to_role_graph(parsed.selected_graph)
    mapped = map_to_s1(rg)
    if isinstance(mapped, StructureMapRefuse):
        return {
            "parsed": True,
            "mapped_s1": False,
            "refuse": mapped.reason,
            "binding": None,
            "role_kinds": sorted(rg.kinds()),
            "organ_answer": parsed.answer,
            "organ_refusal": parsed.refusal_reason,
            "graph": parsed.selected_graph,
            "role_graph": rg,
        }
    assert isinstance(mapped, StructureMapResult)
    return {
        "parsed": True,
        "mapped_s1": True,
        "refuse": None,
        "binding": dict(mapped.binding),
        "role_kinds": sorted(rg.kinds()),
        "organ_answer": parsed.answer,
        "organ_refusal": parsed.refusal_reason,
        "graph": parsed.selected_graph,
        "role_graph": rg,
    }


def mode_right_reason() -> int:
    cases = _load_cases()
    labels = load_structure_labels()  # scoring only, after decisions
    print("=== S1 right-for-right-reason (holdout_dev/v1 S1 cohort) ===")
    wrong = 0
    correct = 0
    refused = 0
    for cid in sorted(S1_HOLDOUT_CASE_IDS):
        c = cases[cid]
        gold = float(c["expected_answer"])
        dec = _map_decision(c["problem"])
        # score label AFTER decision
        sc = score_label(cid, dec["mapped_s1"], labels)
        if not dec["mapped_s1"]:
            refused += 1
            print(
                f"CASE {cid} REFUSE map={dec['refuse']} organ_ans={dec['organ_answer']} "
                f"gold={gold} score={sc}"
            )
            continue
        assert dec["graph"] is not None
        out = try_s1_structure_map_and_solve(graph=dec["graph"])
        if not out.emitted or out.answer is None:
            refused += 1
            print(
                f"CASE {cid} REFUSE solve={out.refusal_reason} binding={out.binding} "
                f"gold={gold} derivation={out.derivation}"
            )
            continue
        ok = abs(out.answer - gold) <= 1e-6 * max(1.0, abs(gold))
        if ok:
            correct += 1
        else:
            wrong += 1
        print(
            f"CASE {cid} emit={out.answer} gold={gold} match={ok} wrong_flag={not ok} "
            f"derivation={out.derivation!r} "
            f"mr_cert={out.multi_register_certified} classical_v={out.classical_verified} "
            f"binding={out.binding} score={sc}"
        )
    print(
        f"SUMMARY right-reason: correct={correct} wrong={wrong} refused={refused} "
        f"n={len(S1_HOLDOUT_CASE_IDS)}"
    )
    return 0 if wrong == 0 else 2


def mode_false_positive() -> int:
    """Separability: S1-mapper must not map non-S1 structures.

    Layer A — holdout_dev/v1 non-S1 cohort (honest about vacuous parse layer).
    Layer B — synthetic non-S1 MathProblemGraphs (transfer/rate/no-compare/…).
    Layer C — other gsm8k_math corpora: every parsed graph whose ops are not
    pure compare_multiplicative (real non-S1 graphs the reader can emit).
    """
    from generate.math_problem_graph import (
        Comparison,
        InitialPossession,
        MathProblemGraph,
        Operation,
        Quantity,
        Rate,
        Unknown,
    )

    cases = _load_cases()
    print("=== A: holdout_dev/v1 non-S1 cases (parse→map) ===")
    fp = 0
    tn = 0
    parse_fail = 0
    n = 0
    fp_ids: list[str] = []
    for cid, c in cases.items():
        if cid in S1_HOLDOUT_CASE_IDS:
            continue
        n += 1
        dec = _map_decision(c["problem"])
        if not dec["parsed"]:
            parse_fail += 1
            tn += 1
            continue
        if dec["mapped_s1"]:
            fp += 1
            fp_ids.append(cid)
            print(
                f"FP {cid} binding={dec['binding']} kinds={dec['role_kinds']} "
                f"problem={c['problem'][:100]!r}"
            )
        else:
            tn += 1
    rate = fp / n if n else 0.0
    print(
        f"SUMMARY holdout-non-S1: fp={fp} tn={tn} n_non_s1={n} "
        f"parse_fail_among_non_s1={parse_fail} fp_rate={rate:.6f}"
    )
    print(
        "NOTE: holdout_dev/v1 currently yields selected_graph on only the 5 S1 "
        "organ cases; non-S1 holdout FP is vacuous at the graph layer when "
        f"parse_fail={parse_fail}. Layer B/C are the real separability tests."
    )
    if fp_ids:
        print("FP_IDS", json.dumps(fp_ids))

    print("=== B: synthetic non-S1 graphs ===")
    synth: list[tuple[str, MathProblemGraph]] = [
        (
            "transfer",
            MathProblemGraph(
                entities=("Sam", "Alex"),
                initial_state=(
                    InitialPossession("Sam", Quantity(10, "apples")),
                    InitialPossession("Alex", Quantity(2, "apples")),
                ),
                operations=(
                    Operation(
                        "Sam", "transfer", Quantity(3, "apples"), target="Alex"
                    ),
                ),
                unknown=Unknown("Sam", "apples"),
            ),
        ),
        (
            "contain_total_no_compare",
            MathProblemGraph(
                entities=("A", "B"),
                initial_state=(
                    InitialPossession("A", Quantity(5, "x")),
                    InitialPossession("B", Quantity(7, "x")),
                ),
                operations=(),
                unknown=Unknown(None, "x"),
            ),
        ),
        (
            "compare_no_total",
            MathProblemGraph(
                entities=("A", "B"),
                initial_state=(InitialPossession("A", Quantity(5, "x")),),
                operations=(
                    Operation(
                        "B",
                        "compare_multiplicative",
                        Comparison("A", None, 2.0, "times"),
                    ),
                ),
                unknown=Unknown("B", "x"),
            ),
        ),
        (
            "compare_with_b_seed",
            MathProblemGraph(
                entities=("A", "B"),
                initial_state=(
                    InitialPossession("A", Quantity(5, "x")),
                    InitialPossession("B", Quantity(10, "x")),
                ),
                operations=(
                    Operation(
                        "B",
                        "compare_multiplicative",
                        Comparison("A", None, 2.0, "times"),
                    ),
                ),
                unknown=Unknown(None, "x"),
            ),
        ),
        (
            "apply_rate",
            MathProblemGraph(
                entities=("shop",),
                initial_state=(InitialPossession("shop", Quantity(3, "apples")),),
                operations=(
                    Operation(
                        "shop", "apply_rate", Rate(2.0, "dollars", "apples")
                    ),
                ),
                unknown=Unknown("shop", "dollars"),
            ),
        ),
    ]
    s_fp = s_tn = 0
    for name, g in synth:
        rg = graph_to_role_graph(g)
        mapped = map_to_s1(rg)
        is_map = isinstance(mapped, StructureMapResult)
        reason = (
            mapped.reason if isinstance(mapped, StructureMapRefuse) else None
        )
        print(f"  {name}: mapped_s1={is_map} refuse={reason} kinds={sorted(rg.kinds())}")
        if is_map:
            s_fp += 1
        else:
            s_tn += 1
    print(
        f"SUMMARY synthetic: fp={s_fp} tn={s_tn} n={s_fp + s_tn} "
        f"fp_rate={(s_fp / (s_fp + s_tn) if s_fp + s_tn else 0):.6f}"
    )

    print("=== C: other gsm8k_math corpora non-compare graphs ===")
    c_fp = c_tn = 0
    fp_examples: list[object] = []
    for path in Path("evals/gsm8k_math").rglob("cases.jsonl"):
        if "holdout_dev" in str(path):
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            text = row.get("problem") or row.get("question")
            if not text:
                continue
            parsed = parse_and_solve(text)
            if parsed.selected_graph is None:
                continue
            kinds = {op.kind for op in parsed.selected_graph.operations}
            if "compare_multiplicative" in kinds:
                continue  # not a non-S1 negative for this check
            rg = graph_to_role_graph(parsed.selected_graph)
            mapped = map_to_s1(rg)
            if isinstance(mapped, StructureMapResult):
                c_fp += 1
                fp_examples.append(
                    {
                        "path": str(path),
                        "id": row.get("id") or row.get("case_id"),
                        "kinds": sorted(kinds),
                        "binding": dict(mapped.binding),
                    }
                )
            else:
                c_tn += 1
    print(
        f"SUMMARY other-corpus non-S1 graphs: fp={c_fp} tn={c_tn} "
        f"n={c_fp + c_tn} fp_rate={(c_fp / (c_fp + c_tn) if c_fp + c_tn else 0):.6f}"
    )
    if fp_examples:
        print("FP_EXAMPLES", json.dumps(fp_examples[:20]))
    return 0 if (fp + s_fp + c_fp) == 0 else 2


def mode_surface_variant() -> int:
    """Rename entity + change numbers in text; re-parse; must still map S1."""
    cases = _load_cases()
    print("=== surface-variant generalization (re-parse) ===")
    # Use 0108: clear entities and numbers
    base_id = "gsm8k-holdout-dev-v1-0108"
    base = cases[base_id]["problem"]
    # Original: Dana Point beach has four times the number of sharks as Newport Beach.
    # If Newport Beach has 22 sharks, how many sharks are there in total on the two beaches?
    variant = (
        "Cedar Cove beach has five times the number of dolphins as Harbor Beach. "
        "If Harbor Beach has 11 dolphins, how many dolphins are there in total on the two beaches?"
    )
    print("BASE_ID", base_id)
    print("BASE_TEXT", base)
    print("VARIANT_TEXT", variant)
    base_dec = _map_decision(base)
    var_dec = _map_decision(variant)
    print("BASE_MAP", {k: base_dec[k] for k in ("mapped_s1", "refuse", "binding", "role_kinds")})
    print("VARIANT_MAP", {k: var_dec[k] for k in ("mapped_s1", "refuse", "binding", "role_kinds")})
    if not var_dec["mapped_s1"]:
        print("SUMMARY surface-variant: FAIL not_mapped")
        return 2
    b = var_dec["binding"]
    assert b is not None
    ok_k = abs(float(b["k"]) - 5.0) < 1e-9
    ok_a = abs(float(b["a_value"]) - 11.0) < 1e-9
    # entity rename: Harbor / Cedar (parser may normalize casing/names)
    a_name = str(b["a"]).lower()
    b_name = str(b["b"]).lower()
    ok_names = ("harbor" in a_name) and ("cedar" in b_name or "cove" in b_name)
    out = try_s1_structure_map_and_solve(graph=var_dec["graph"])
    expected = 11.0 * (1.0 + 5.0)  # 66
    ans_ok = (
        out.emitted
        and out.answer is not None
        and abs(out.answer - expected) <= 1e-6 * expected
    )
    print(
        f"VARIANT_SOLVE emitted={out.emitted} answer={out.answer} expected={expected} "
        f"derivation={out.derivation!r} refuse={out.refusal_reason}"
    )
    print(
        f"SUMMARY surface-variant: map={var_dec['mapped_s1']} k_ok={ok_k} a_ok={ok_a} "
        f"names_ok={ok_names} ans_ok={ans_ok} binding={b}"
    )
    return 0 if (var_dec["mapped_s1"] and ok_k and ok_a and ans_ok) else 2


def mode_vs_organ() -> int:
    cases = _load_cases()
    print("=== side-by-side vs S1 surface organ (parse_and_solve) ===")
    print(
        f"{'case_id':<32} {'organ':>10} {'trackb':>10} {'gold':>10} "
        f"{'organ_ok':>8} {'tb_ok':>8} {'map':>6}"
    )
    for cid in sorted(S1_HOLDOUT_CASE_IDS):
        c = cases[cid]
        gold = float(c["expected_answer"])
        organ = parse_and_solve(c["problem"])
        dec = _map_decision(c["problem"])
        tb_ans = None
        if dec["mapped_s1"] and dec.get("graph") is not None:
            out = try_s1_structure_map_and_solve(graph=dec["graph"])
            tb_ans = out.answer if out.emitted else None
        organ_ok = organ.answer is not None and abs(organ.answer - gold) <= 1e-6 * max(
            1.0, abs(gold)
        )
        tb_ok = tb_ans is not None and abs(tb_ans - gold) <= 1e-6 * max(1.0, abs(gold))
        print(
            f"{cid:<32} {organ.answer!s:>10} {tb_ans!s:>10} {gold!s:>10} "
            f"{str(organ_ok):>8} {str(tb_ok):>8} {str(dec['mapped_s1']):>6}"
        )
    print("SUMMARY vs-organ: table above; organ is serving parse_and_solve path")
    return 0


def mode_coverage() -> int:
    """Parse→role coverage on S1 holdout cases."""
    cases = _load_cases()
    print("=== parse→role coverage on S1 holdout ===")
    for cid in sorted(S1_HOLDOUT_CASE_IDS):
        c = cases[cid]
        dec = _map_decision(c["problem"])
        print(
            f"{cid} parsed={dec['parsed']} kinds={dec['role_kinds']} "
            f"mapped_s1={dec['mapped_s1']} refuse={dec['refuse']}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--mode",
        choices=(
            "right-reason",
            "false-positive",
            "surface-variant",
            "vs-organ",
            "coverage",
            "all",
        ),
        required=True,
    )
    args = p.parse_args(argv)
    modes = {
        "right-reason": mode_right_reason,
        "false-positive": mode_false_positive,
        "surface-variant": mode_surface_variant,
        "vs-organ": mode_vs_organ,
        "coverage": mode_coverage,
    }
    if args.mode == "all":
        rc = 0
        for name in (
            "coverage",
            "right-reason",
            "false-positive",
            "surface-variant",
            "vs-organ",
        ):
            print()
            r = modes[name]()
            rc = rc or r
        return rc
    return modes[args.mode]()


if __name__ == "__main__":
    sys.exit(main())
