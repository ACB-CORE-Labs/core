"""Extracted commands."""

from __future__ import annotations
import argparse
import json
from pathlib import Path


def cmd_capability_chains(args: argparse.Namespace) -> int:
    from core.capability import chain_report

    report = chain_report()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


def cmd_capability_flags(args: argparse.Namespace) -> int:
    from core.capability import flag_report

    report = flag_report()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


def cmd_capability_ledger(args: argparse.Namespace) -> int:
    from core.capability import ledger_report

    report = ledger_report()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


def cmd_capability_artifact(args: argparse.Namespace) -> int:
    from core.capability import CapabilityArtifactQuery, artifact_report

    report = artifact_report(
        CapabilityArtifactQuery(lane=args.lane, split=args.split, version=args.version)
    )
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


def cmd_capability_domain_contract(args: argparse.Namespace) -> int:
    """ADR-0093 domain-contract dry-run validator.

    Default behavior runs the nine ADR-0091 predicates plus eval-lane
    artifact resolution and exits non-zero on any predicate failure.
    The legacy structural-only output remains available via
    ``--structural-only`` for callers that depend on the prior shape.
    """
    from language_packs.domain_contract import validate_domain_contract_pack

    if getattr(args, "structural_only", False):
        report = validate_domain_contract_pack(args.pack_id).as_dict()
        print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
        return 0 if report["valid"] else 1

    from core.capability.domain_contract_predicates import evaluate_domain_contract

    predicate_report = evaluate_domain_contract(args.pack_id).as_dict()
    print(
        json.dumps(predicate_report, indent=2, sort_keys=True)
        if args.json
        else predicate_report
    )
    return 0 if predicate_report["all_passed"] else 1


def cmd_capability_evidence_plan(args: argparse.Namespace) -> int:
    from core.capability import evidence_plan_report

    report = evidence_plan_report()
    print(json.dumps(report, indent=2, sort_keys=True) if args.json else report)
    return 0


def cmd_capability_perturbation(args: argparse.Namespace) -> int:
    """ADR-0114a Obligation #5 — reasoning-isolation perturbation suite for B3.

    Generates and scores invariance-preserving and invariance-breaking
    perturbations over B3 (bounded grammar) expected-correct cases.
    Writes the report to ``evals/obligation_5_perturbation/<lane_id>.json``.
    Exit 0 iff both preserving_rate == 1.0 AND breaking_rate == 1.0.
    """
    from pathlib import Path as _Path
    from core.capability.perturbation_b3 import (
        validate_perturbation_suite,
        emit_perturbation_report,
    )

    lane_id = args.lane_id
    report = validate_perturbation_suite(lane_id=lane_id)

    out_dir = (
        _Path(__file__).resolve().parent.parent / "evals" / "obligation_5_perturbation"
    )
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{lane_id}.json"
    emit_perturbation_report(report, out_path)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"lane_id:             {report.lane_id}")
        print(f"cases_total:         {report.cases_total}")
        print(f"cases_expected_correct: {report.cases_expected_correct}")
        print(
            f"preserving: {report.preserving_correct}/{report.preserving_attempted} "
            f"= {report.preserving_rate:.4f}"
        )
        print(
            f"breaking:   {report.breaking_correct}/{report.breaking_attempted} "
            f"= {report.breaking_rate:.4f}"
        )
        print(f"obligation_5_passed: {report.obligation_5_passed}")
        print(f"report_digest:       {report.report_digest}")
        print(f"artifact:            {out_path}")
        if not report.obligation_5_passed:
            print(f"refusal_reason: {report.refusal_reason}")
    return 0 if report.obligation_5_passed else 1


def cmd_capability_math_expert_gate(args: argparse.Namespace) -> int:
    """ADR-0131.4 — evaluate the composite math-expert promotion gate
    (Benchmark 1 + 2 + 3, ADR-0131's revision of ADR-0120's single-lane
    coverage check). Emits ``expert_claims_math_v1.json`` to ``--out``
    (default: ``evals/math_expert_claims/v1/expert_claims_math_v1.json``).
    Exit 0 iff every benchmark passes."""
    from core.capability.composite_math_gate import (
        emit_expert_claims_artifact,
        evaluate_composite_math_gate,
    )

    verdict = evaluate_composite_math_gate()
    out_path = (
        Path(args.out)
        if args.out
        else (
            Path(__file__).resolve().parent.parent
            / "evals"
            / "math_expert_claims"
            / "v1"
            / "expert_claims_math_v1.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_expert_claims_artifact(verdict, out_path)

    if args.json:
        print(json.dumps(verdict.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"composite_gate_passed: {verdict.composite_gate_passed}")
        print(f"claim_digest:          {verdict.claim_digest}")
        print(f"artifact:              {out_path}")
        for b in verdict.benchmarks:
            print(
                f"  {b.benchmark_id:>20}  passed={b.passed}  "
                f"correct={b.correct}/{b.cases_total}  wrong={b.wrong}  "
                f"rate={b.correct_rate:.4f}"
            )
        hd = verdict.honest_disclosure
        print(
            f"GSM8K honest disclosure: admission={hd.get('admitted_solved', 0)}/"
            f"{hd.get('cases_total', 0)}, wrong={hd.get('admitted_wrong', 0)}, "
            f"substrate={hd.get('substrate', '?')}"
        )
        if not verdict.composite_gate_passed:
            print(f"refusal_reason: {verdict.refusal_reason}")
    return 0 if verdict.composite_gate_passed else 1


def cmd_capability_pack_provenance(args: argparse.Namespace) -> int:
    """ADR-0114a Obligation #10 — external audit that every solver
    step's ``pack_lemma_id`` resolves to a real entry in the domain's
    operator pack lexicon. Defaults to B3 (bounded grammar) under
    ``en_arithmetic_v1``. Emits report to ``--out`` (default:
    ``evals/obligation_10_pack_provenance/<lane_id>.json``).
    Exit 0 iff obligation passes."""
    from core.capability.pack_provenance import (
        emit_provenance_report,
        validate_lane,
    )

    report = validate_lane()
    out_path = (
        Path(args.out)
        if args.out
        else (
            Path(__file__).resolve().parent.parent
            / "evals"
            / "obligation_10_pack_provenance"
            / f"{report.lane_id}.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_provenance_report(report, out_path)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"lane:                       {report.lane_id}")
        print(f"pack_id:                    {report.pack_id}")
        print(f"cases_total:                {report.cases_total}")
        print(f"cases_validated:            {report.cases_validated}")
        print(f"cases_skipped_unsolved:     {report.cases_skipped_unsolved}")
        print(f"cases_violated:             {report.cases_violated}")
        print(f"obligation_10_passed:       {report.obligation_10_passed}")
        print("distinct_lemma_ids_observed:")
        for lid in report.distinct_lemma_ids_observed:
            print(f"  - {lid}")
        print(f"artifact:                   {out_path}")
        if report.refusal_reason:
            print(f"refusal_reason:             {report.refusal_reason}")
    return 0 if report.obligation_10_passed else 1


def cmd_capability_adversarial(args: argparse.Namespace) -> int:
    """ADR-0114a Obligation #8 — adversarial generation auditor. Runs
    a committed adversarial case set through the candidate-graph
    pipeline; gate is ``wrong == 0`` across all families AND
    ``cases_total >= 30`` AND ``families_total >= 8``. Default cases
    set ``evals/obligation_8_adversarial/v1/cases.jsonl``; writes
    report to ``--out`` (default
    ``evals/obligation_8_adversarial/<lane_id>.json``). Exit 0 iff
    obligation passes."""
    from core.capability.adversarial import (
        emit_adversarial_report,
        evaluate_adversarial,
    )

    report = evaluate_adversarial()
    out_path = (
        Path(args.out)
        if args.out
        else (
            Path(__file__).resolve().parent.parent
            / "evals"
            / "obligation_8_adversarial"
            / f"{report.lane_id}.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_adversarial_report(report, out_path)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"lane:                {report.lane_id}")
        print(
            f"cases_total:         {report.cases_total}  (min {report.cases_total >= 30 and 'OK' or 'FAIL'})"
        )
        print(
            f"families_total:      {report.families_total}  ({'OK' if report.families_total >= 8 else 'FAIL'})"
        )
        print(f"cases_refused:       {report.cases_refused}")
        print(f"cases_solved:        {report.cases_solved}")
        print(f"cases_wrong:         {report.cases_wrong} (gate: must be 0)")
        print(f"obligation_8_passed: {report.obligation_8_passed}")
        print()
        print(f"  {'family':<22} {'total':<7} {'refused':<8} {'solved':<8} {'wrong'}")
        for f in report.families:
            print(
                f"  {f.family:<22} {f.cases_total:<7} {f.cases_refused:<8} {f.cases_solved:<8} {f.cases_wrong}"
            )
        print(f"\nartifact: {out_path}")
        if report.refusal_reason:
            print(f"refusal_reason: {report.refusal_reason}")
    return 0 if report.obligation_8_passed else 1


def cmd_capability_depth_curve(args: argparse.Namespace) -> int:
    """ADR-0114a Obligation #6 — compositional-depth curve. Re-runs the
    lane's expected-correct cases, buckets by ``len(trace.steps)``,
    asserts ``accuracy(N) >= accuracy(depth_1) * (1 - eps)^(N-1)`` for
    eps = 0.05. Defaults to B3 (bounded grammar). Emits report to
    ``--out`` (default ``evals/obligation_6_depth_curve/<lane_id>.json``).
    Exit 0 iff the assertion holds."""
    from core.capability.depth_curve import (
        emit_depth_curve_report,
        evaluate_depth_curve,
    )

    report = evaluate_depth_curve()
    out_path = (
        Path(args.out)
        if args.out
        else (
            Path(__file__).resolve().parent.parent
            / "evals"
            / "obligation_6_depth_curve"
            / f"{report.lane_id}.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_depth_curve_report(report, out_path)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"lane:                          {report.lane_id}")
        print(f"cases_total:                   {report.cases_total}")
        print(f"cases_solved:                  {report.cases_solved}")
        print(f"epsilon:                       {report.epsilon}")
        print(f"mechanism_wired:               {report.obligation_6_mechanism_wired}")
        print(f"assertion_holds:               {report.obligation_6_assertion_holds}")
        print(f"coverage_sufficient:           {report.coverage_sufficient}")
        print(f"populated_buckets:             {list(report.populated_buckets)}")
        print()
        print(
            f"  {'bucket':<12} {'total':<7} {'correct':<8} {'accuracy':<10} {'bound':<10} {'satisfied'}"
        )
        for b in report.buckets:
            bound = (
                f"{b.bound_required:.4f}"
                if b.bound_required is not None
                else "(anchor)"
            )
            print(
                f"  {b.bucket:<12} {b.cases_total:<7} {b.cases_correct:<8} {b.accuracy:<10.4f} {bound:<10} {b.bound_satisfied}"
            )
        print(f"\nartifact: {out_path}")
        if report.refusal_reason:
            print(f"refusal_reason: {report.refusal_reason}")
    return 0 if report.obligation_6_assertion_holds else 1


def cmd_capability_ood_ratio(args: argparse.Namespace) -> int:
    """ADR-0114a Obligation #2 — OOD surface variation ratio auditor.

    Reads the B3 public ``report.json`` and the OOD lane ``report.json``,
    computes ``ood_ratio = ood_accuracy / public_accuracy``, and exits 0
    iff ratio >= 0.95 AND ood wrong == 0. Writes report to ``--out``
    (default: ``evals/obligation_2_ood_ratio/<lane_id>.json``)."""
    from core.capability.ood_ratio import (
        emit_ood_ratio_report,
        evaluate_ood_ratio,
    )
    from evals.obligation_2_ood_ratio.v1.runner import (
        build_report,
        load_cases,
        write_report as write_ood_report,
    )

    _repo_root = Path(__file__).resolve().parent.parent

    # Regenerate OOD report so auditor always reads fresh results.
    ood_report_path = (
        _repo_root / "evals" / "obligation_2_ood_ratio" / "v1" / "report.json"
    )
    ood_cases = load_cases()
    ood_runner_report = build_report(ood_cases)
    write_ood_report(ood_runner_report, ood_report_path)

    report = evaluate_ood_ratio()
    out_path = (
        Path(args.out)
        if args.out
        else (
            _repo_root / "evals" / "obligation_2_ood_ratio" / f"{report.lane_id}.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_ood_ratio_report(report, out_path)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"lane:                        {report.lane_id}")
        print(
            f"public_accuracy:             {report.public_accuracy:.4f}  ({report.public_cases_correct}/{report.public_cases_total})"
        )
        print(
            f"ood_accuracy:                {report.ood_accuracy:.4f}  ({report.ood_cases_correct}/{report.ood_cases_total})"
        )
        print(f"ood_ratio:                   {report.ood_ratio:.4f}")
        print(f"obligation_2_ratio_satisfied:{report.obligation_2_ratio_satisfied}")
        print(f"obligation_2_wrong_zero:     {report.obligation_2_wrong_zero}")
        print(f"obligation_2_passed:         {report.obligation_2_passed}")
        print(f"artifact:                    {out_path}")
        if report.refusal_reason:
            print(f"refusal_reason:              {report.refusal_reason}")
    return 0 if report.obligation_2_passed else 1


def cmd_capability_math_expert_promote(args: argparse.Namespace) -> int:
    """ADR-0120 math-expert promotion composer. Collects all 10 ADR-0114a
    obligation verdicts + the ADR-0131.4 composite math gate verdict +
    the reviewer-signed claim entry from ``docs/reviewers.yaml``;
    emits a deterministic ``expert_claims_math_v1_signed.json``
    artifact. Exit 0 iff ``promote_admitted == True``.
    """
    from core.capability.expert_promotion_math import (
        emit_promotion_artifact,
        evaluate_math_expert_promotion,
    )

    verdict = evaluate_math_expert_promotion()
    out_path = (
        Path(args.out)
        if args.out
        else (
            Path(__file__).resolve().parent.parent
            / "evals"
            / "math_expert_claims"
            / "v1"
            / "expert_claims_math_v1_signed.json"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    emit_promotion_artifact(verdict, out_path)

    if args.json:
        print(json.dumps(verdict.as_dict(), indent=2, sort_keys=True))
    else:
        print(f"domain:                      {verdict.domain}")
        print()
        print(f"  {'id':<4} {'passed':<7} title")
        for o in verdict.obligations:
            print(f"  {o.obligation_id:<4} {str(o.passed):<7} {o.title}")
            if not o.passed:
                print(f"          refusal: {o.refusal_reason}")
        print()
        print(f"composite_gate_passed:       {verdict.composite_gate_passed}")
        print(f"all_obligations_passed:      {verdict.all_obligations_passed}")
        print(f"technical_pass:              {verdict.technical_pass}")
        print(f"claim_digest:                {verdict.claim_digest}")
        print(f"reviewer_signature_present:  {verdict.reviewer_signature is not None}")
        print(f"reviewer_signature_matches:  {verdict.reviewer_signature_matches}")
        print(f"promote_admitted:            {verdict.promote_admitted}")
        print(f"artifact:                    {out_path}")
        if verdict.refusal_reason:
            print()
            print("refusal_reason:")
            print(f"  {verdict.refusal_reason}")
    return 0 if verdict.promote_admitted else 1
