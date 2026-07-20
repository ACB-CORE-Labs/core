"""Blind measurement for Track B Increment 2 (S1–S4 + selector + generalization).

Usage::

    uv run python scripts/measure_trackb_inc2.py --mode all
    uv run python scripts/measure_trackb_inc2.py --mode ratio
    uv run python scripts/measure_trackb_inc2.py --mode coverage-gain
    uv run python scripts/measure_trackb_inc2.py --mode selector
    uv run python scripts/measure_trackb_inc2.py --mode parser-frontier
    uv run python scripts/measure_trackb_inc2.py --mode right-reason

Labels load only in scoring branches. Mapper/selector never see gold labels.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

from generate.math_candidate_graph import parse_and_solve
from generate.math_problem_graph import (
    Comparison,
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Rate,
    Unknown,
)
from generate.structure_mapping.convert import graph_to_role_graph
from generate.structure_mapping.mapper import (
    StructureMapRefuse,
    StructureMapResult,
    map_to_s1,
    map_to_s2,
)
from generate.structure_mapping.pipeline import run_structure_mapping_pipeline
from generate.structure_mapping.selector import select_structure
from generate.structure_mapping.solve import try_structure_map_and_solve

HOLDOUT_CASES = Path("evals/gsm8k_math/holdout_dev/v1/cases.jsonl")
PUBLIC_CASES = Path("evals/gsm8k_math/public/cases.jsonl")

# S1 organ cohort (already carried on serving reader).
S1_ORGAN_IDS = frozenset(
    {
        "gsm8k-holdout-dev-v1-0101",
        "gsm8k-holdout-dev-v1-0108",
        "gsm8k-holdout-dev-v1-0268",
        "gsm8k-holdout-dev-v1-0411",
        "gsm8k-holdout-dev-v1-0453",
    }
)

# Pure-S1 holdout cases the organ misses; SM-owned extract targets.
S1_COVERAGE_CANDIDATES = frozenset(
    {
        "gsm8k-holdout-dev-v1-0148",
        "gsm8k-holdout-dev-v1-0228",
        "gsm8k-holdout-dev-v1-0234",
        "gsm8k-holdout-dev-v1-0441",
    }
)


def _load_cases(path: Path = HOLDOUT_CASES) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        row = json.loads(line)
        out[row["id"]] = row
    return out


def mode_ratio() -> None:
    """Generalization-ratio table on real holdout case IDs."""
    print("=== generalization ratio (holdout_dev/v1, command-backed) ===")
    cases = _load_cases()
    by_canonical: dict[str, list[dict]] = defaultdict(list)

    target_ids = S1_ORGAN_IDS | S1_COVERAGE_CANDIDATES
    for cid in sorted(target_ids):
        row = cases[cid]
        gold = float(row["expected_answer"])
        out, trace, _graph = run_structure_mapping_pipeline(row["problem"])
        right = (
            out.emitted
            and out.answer is not None
            and abs(float(out.answer) - gold) <= 1e-6 * max(1.0, abs(gold))
            and out.derivation is not None
            and out.multi_register_certified
            and out.classical_verified
        )
        rec = {
            "id": cid,
            "structure_id": out.structure_id,
            "emitted": out.emitted,
            "answer": out.answer,
            "gold": gold,
            "right_reason": right,
            "derivation": out.derivation,
            "graph_source": trace.graph_source,
            "extract_pattern": trace.extract_pattern,
            "refusal": out.refusal_reason,
            "organ_parsed": trace.organ_parsed,
        }
        print(
            f"CASE {cid} sid={out.structure_id} emit={out.answer} gold={gold} "
            f"right={right} src={trace.graph_source} pat={trace.extract_pattern} "
            f"refuse={out.refusal_reason}"
        )
        if out.derivation:
            print(f"  derivation={out.derivation!r}")
        if right and out.structure_id:
            by_canonical[out.structure_id].append(rec)

    print("--- ratio table ---")
    n_templates = 0
    for sid in ("S1", "S2", "S3", "S4"):
        carried = by_canonical.get(sid, [])
        # One canonical template written per family in the library.
        templates = 1 if sid in ("S1", "S2", "S3", "S4") else 0
        n_templates += templates
        ids = [c["id"] for c in carried]
        ratio = (len(carried) / templates) if templates and carried else 0.0
        print(
            f"canonical={sid} templates=1 cases_carried={len(carried)} "
            f"ratio={ratio:.3f} ids={ids}"
        )
    # Overall for families that carried ≥1
    active = {k: v for k, v in by_canonical.items() if v}
    if active:
        total_cases = sum(len(v) for v in active.values())
        total_tmpl = len(active)
        print(
            f"SUMMARY active_canonicals={total_tmpl} total_cases={total_cases} "
            f"aggregate_ratio={total_cases / total_tmpl:.3f}"
        )
    else:
        print("SUMMARY no_cases_carried ratio=0")


def mode_coverage_gain() -> None:
    """Cases newly solved vs organ (holdout)."""
    print("=== coverage gain vs organ (holdout_dev/v1) ===")
    cases = _load_cases()
    organ_ok = 0
    tb_ok = 0
    newly = []
    both = []
    for cid, row in cases.items():
        gold = float(row["expected_answer"])
        organ = parse_and_solve(row["problem"])
        o_ok = (
            organ.answer is not None
            and abs(float(organ.answer) - gold) <= 1e-6 * max(1.0, abs(gold))
        )
        out, trace, _ = run_structure_mapping_pipeline(row["problem"])
        t_ok = (
            out.emitted
            and out.answer is not None
            and abs(float(out.answer) - gold) <= 1e-6 * max(1.0, abs(gold))
            and out.multi_register_certified
        )
        if o_ok:
            organ_ok += 1
        if t_ok:
            tb_ok += 1
        if t_ok and not o_ok:
            newly.append((cid, out.answer, gold, out.structure_id, trace.extract_pattern))
        if t_ok and o_ok:
            both.append(cid)

    print(f"organ_correct={organ_ok} trackb_correct={tb_ok} newly_solved={len(newly)}")
    for cid, ans, gold, sid, pat in newly:
        print(f"  NEW {cid} ans={ans} gold={gold} sid={sid} extract={pat}")
    print(f"both_correct_count={len(both)}")
    print(
        "NOTE: organ_retirement not performed (off-serving; coverage-gain path). "
        "Serving reader unchanged."
    )


def mode_selector() -> None:
    """Selector routing table: real + targeted synthetic."""
    print("=== selector routing (blind; synthetic + real graphs) ===")

    def show(label: str, graph: MathProblemGraph, expect_sid: str | None) -> None:
        rg = graph_to_role_graph(graph)
        sel = select_structure(rg)
        got = sel.selected.structure_id if sel.selected else None
        ok = got == expect_sid
        print(
            f"CASE {label} expect={expect_sid} got={got} refused={sel.refused} "
            f"reason={sel.reason} ok={ok} candidates="
            f"{[c.structure_id for c in sel.candidates]}"
        )

    # Real S1 organ graph
    s1_text = (
        "In a class, there were 13 female students. There were three times as many "
        "male students in this class. How many students were in the class?"
    )
    g = parse_and_solve(s1_text).selected_graph
    assert g is not None
    show("real_s1_0411", g, "S1")

    # Real S2 transfer from public corpus
    t2 = "Eve has 15 coins. David has 47 coins. Eve hands 7 coins to David. How many coins does David have?"
    g2 = parse_and_solve(t2).selected_graph
    assert g2 is not None
    show("real_s2_public_transfer", g2, "S2")

    # Lexically S1-looking but structurally S2: has "times" in entity names? Better:
    # transfer problem with multiplicative words in fluff is rare; instead use a
    # pure S2 vs pure S1 structural pair and a deliberately ambiguous dual graph.
    # Surface-similarity trap: text mentions "twice" but graph is transfer-only
    # (built synthetic role graph with transfer only).
    g_s2_trap = MathProblemGraph(
        entities=("Alice", "Bob"),
        initial_state=(
            InitialPossession(entity="Alice", quantity=Quantity(value=10, unit="apples")),
            InitialPossession(entity="Bob", quantity=Quantity(value=5, unit="apples")),
        ),
        operations=(
            Operation(
                actor="Alice",
                kind="transfer",
                operand=Quantity(value=3, unit="apples"),
                target="Bob",
            ),
        ),
        unknown=Unknown(entity="Bob", unit="apples"),
    )
    show("struct_s2_not_s1", g_s2_trap, "S2")

    # S1 pure
    g_s1 = MathProblemGraph(
        entities=("Ann", "Bea"),
        initial_state=(
            InitialPossession(entity="Ann", quantity=Quantity(value=7, unit="pts")),
        ),
        operations=(
            Operation(
                actor="Bea",
                kind="compare_multiplicative",
                operand=Comparison(
                    reference_actor="Ann",
                    delta=None,
                    factor=3.0,
                    direction="times",
                ),
            ),
        ),
        unknown=Unknown(entity=None, unit="pts"),
    )
    show("struct_s1", g_s1, "S1")

    # Ambiguous: empty role graph → refuse
    g_empty = MathProblemGraph(
        entities=("X",),
        initial_state=(
            InitialPossession(entity="X", quantity=Quantity(value=1, unit="u")),
        ),
        operations=(),
        unknown=Unknown(entity="X", unit="u"),
    )
    show("empty_ops_refuse", g_empty, None)

    # Rate graph → S3 map may succeed but note MR frontier later
    g_rate = MathProblemGraph(
        entities=("worker",),
        initial_state=(
            InitialPossession(entity="worker", quantity=Quantity(value=5, unit="hours")),
        ),
        operations=(
            Operation(
                actor="worker",
                kind="apply_rate",
                operand=Rate(value=10.0, numerator_unit="pages", denominator_unit="hours"),
            ),
        ),
        unknown=Unknown(entity="worker", unit="pages"),
    )
    show("struct_s3_rate", g_rate, "S3")


def mode_parser_frontier() -> None:
    """Parse→role coverage per family on holdout + note 0148."""
    print("=== parser-frontier report (holdout_dev/v1) ===")
    cases = _load_cases()
    organ_graphs = 0
    by_kinds: dict[str, int] = defaultdict(int)
    for cid, row in cases.items():
        organ = parse_and_solve(row["problem"])
        if organ.selected_graph is None:
            continue
        organ_graphs += 1
        rg = graph_to_role_graph(organ.selected_graph)
        kinds = ",".join(sorted(rg.kinds()))
        by_kinds[kinds] += 1
        mapped = []
        for fam, fn in (
            ("S1", map_to_s1),
            ("S2", map_to_s2),
        ):
            m = fn(rg)
            if isinstance(m, StructureMapResult):
                mapped.append(fam)
        if mapped:
            print(f"  organ_graph {cid} kinds={kinds} maps={mapped}")

    print(f"organ_selected_graph_count={organ_graphs}/500")
    print(f"role_kind_multiset_counts={dict(by_kinds)}")

    # 0148 status
    row = cases["gsm8k-holdout-dev-v1-0148"]
    organ = parse_and_solve(row["problem"])
    out, trace, _ = run_structure_mapping_pipeline(row["problem"])
    print("--- case 0148 ---")
    print(f"organ_parsed={organ.selected_graph is not None} organ_answer={organ.answer}")
    print(
        f"sm_pipeline emit={out.emitted} answer={out.answer} gold={row['expected_answer']} "
        f"src={trace.graph_source} pat={trace.extract_pattern} sid={out.structure_id}"
    )
    print(
        "NOTE: holdout non-S1 organ graphs remain near-zero; S2/S3/S4 holdout "
        "coverage is parser-frontier limited. S2 is demonstrated on public "
        "transfer graphs (real, not clones) in selector/right-reason modes."
    )


def mode_right_reason() -> None:
    """3-part right-reason on carried S1 holdout + surface variant."""
    print("=== right-for-right-reason (S1 holdout + coverage) ===")
    cases = _load_cases()
    correct = wrong = refused = 0
    for cid in sorted(S1_ORGAN_IDS | S1_COVERAGE_CANDIDATES):
        row = cases[cid]
        gold = float(row["expected_answer"])
        out, trace, _ = run_structure_mapping_pipeline(row["problem"])
        if not out.emitted or out.answer is None:
            refused += 1
            print(f"CASE {cid} REFUSED {out.refusal_reason} src={trace.graph_source}")
            continue
        match = abs(float(out.answer) - gold) <= 1e-6 * max(1.0, abs(gold))
        if match and out.derivation and out.multi_register_certified:
            correct += 1
            flag = False
        else:
            wrong += 1
            flag = True
        print(
            f"CASE {cid} emit={out.answer} gold={gold} match={match} wrong_flag={flag} "
            f"src={trace.graph_source} mr={out.multi_register_certified} "
            f"derivation={out.derivation!r}"
        )
    print(f"SUMMARY right-reason: correct={correct} wrong={wrong} refused={refused}")

    # Surface-variant on a coverage case (0148-style rephrase)
    print("=== surface-variant (re-parse / re-extract) ===")
    base = cases["gsm8k-holdout-dev-v1-0441"]["problem"]
    variant = (
        "Ava wrote five times as many essays as Ben. If Ava wrote 40 essays, "
        "how many essays did they write altogether?"
    )
    out_b, tr_b, _ = run_structure_mapping_pipeline(base)
    out_v, tr_v, _ = run_structure_mapping_pipeline(variant)
    print(f"BASE emit={out_b.answer} sid={out_b.structure_id} src={tr_b.graph_source}")
    print(
        f"VARIANT emit={out_v.answer} expected=48.0 sid={out_v.structure_id} "
        f"src={tr_v.graph_source} binding={out_v.binding}"
    )
    ok = (
        out_v.emitted
        and out_v.answer is not None
        and abs(float(out_v.answer) - 48.0) < 1e-6
        and out_v.structure_id == "S1"
    )
    print(f"SUMMARY surface-variant: ok={ok}")

    # S2 public real transfer right-reason
    print("=== S2 public transfer right-reason (real corpus, not holdout) ===")
    pub = _load_cases(PUBLIC_CASES) if PUBLIC_CASES.exists() else {}
    # scan a few known transfers
    s2_n = s2_ok = 0
    for cid, row in list(pub.items())[:80]:
        organ = parse_and_solve(row["problem"])
        if organ.selected_graph is None:
            continue
        rg = graph_to_role_graph(organ.selected_graph)
        if "transfer" not in rg.kinds():
            continue
        s2_n += 1
        out = try_structure_map_and_solve(organ.selected_graph, families=("S1", "S2", "S3", "S4"))
        gold = float(row["expected_answer"])
        if (
            out.emitted
            and out.answer is not None
            and abs(float(out.answer) - gold) <= 1e-6 * max(1.0, abs(gold))
            and out.structure_id == "S2"
        ):
            s2_ok += 1
            if s2_ok <= 3:
                print(f"  S2 {cid} ans={out.answer} gold={gold} der={out.derivation!r}")
        if s2_n >= 20:
            break
    print(f"SUMMARY s2_public_sample: ok={s2_ok} scanned_transferish={s2_n}")


def mode_full_holdout_wrong0() -> None:
    """Absolute wrong=0 gate over **all** holdout_dev/v1 cases (not curated subset).

    Any pipeline emit whose answer disagrees with gold is a hard failure of the
    wrong=0 bar. Overmatching SM extract that certifies garbage is the hazard
    this mode is designed to catch (regression: 0361).
    """
    print("=== full holdout_dev/v1 wrong=0 gate (all 500 cases) ===")
    cases = _load_cases()
    emit_ok = 0
    wrong: list[tuple[str, float | None, float, str | None, str | None]] = []
    refused = 0
    for cid, row in cases.items():
        gold = float(row["expected_answer"])
        out, trace, _ = run_structure_mapping_pipeline(row["problem"])
        if not out.emitted or out.answer is None:
            refused += 1
            continue
        if abs(float(out.answer) - gold) <= 1e-6 * max(1.0, abs(gold)):
            emit_ok += 1
        else:
            wrong.append(
                (
                    cid,
                    out.answer,
                    gold,
                    trace.graph_source,
                    trace.extract_pattern,
                )
            )
    print(
        f"SUMMARY full-holdout: emit_ok={emit_ok} wrong={len(wrong)} "
        f"refused={refused} n={len(cases)}"
    )
    for cid, ans, gold, src, pat in wrong:
        print(
            f"  WRONG {cid} emit={ans} gold={gold} src={src} extract={pat}"
        )
    if wrong:
        print("FAIL: wrong≠0 on holdout_dev/v1 — pure-family extract overmatch")
    else:
        print("PASS: wrong=0 absolute on full holdout_dev/v1")


def mode_all() -> None:
    mode_ratio()
    print()
    mode_coverage_gain()
    print()
    mode_selector()
    print()
    mode_parser_frontier()
    print()
    mode_right_reason()
    print()
    mode_full_holdout_wrong0()


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--mode",
        choices=(
            "ratio",
            "coverage-gain",
            "selector",
            "parser-frontier",
            "right-reason",
            "full-holdout-wrong0",
            "all",
        ),
        default="all",
    )
    args = p.parse_args(argv)
    {
        "ratio": mode_ratio,
        "coverage-gain": mode_coverage_gain,
        "selector": mode_selector,
        "parser-frontier": mode_parser_frontier,
        "right-reason": mode_right_reason,
        "full-holdout-wrong0": mode_full_holdout_wrong0,
        "all": mode_all,
    }[args.mode]()
    return 0


if __name__ == "__main__":
    sys.exit(main())
