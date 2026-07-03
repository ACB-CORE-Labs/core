"""Extracted commands."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

from core.cli import _validate_output_path, _DEFAULT_AUDIT_PATH
from core.cli import _die, _REPO_ROOT

def cmd_eval(args: argparse.Namespace) -> int:
    """Run an eval lane by name, or list available lanes."""
    if getattr(args, "lane", None) == "sensorium":
        return cmd_eval_sensorium(args)
    if getattr(args, "lane", None) == "environment-falsification":
        return cmd_eval_environment_falsification(args)
    if getattr(args, "lane", None) == "math-contemplation":
        return cmd_eval_math_contemplation(args)

    from evals._parallel import normalize_workers
    from evals.framework import (
        discover_lanes,
        get_lane,
        load_cases,
        run_lane,
        write_result,
    )

    if args.list_lanes:
        lanes = discover_lanes()
        if not lanes:
            print("no eval lanes found")
        for lane in lanes:
            versions = ", ".join(lane.versions) if lane.versions else "none"
            print(f"  {lane.name:20s}  versions: {versions}")
        return 0

    lane_name = args.lane
    if not lane_name:
        _die("eval requires a lane name. Use `core eval --list` to see available lanes.")

    try:
        lane = get_lane(lane_name)
    except FileNotFoundError as exc:
        _die(str(exc))

    version = args.version or (lane.versions[0] if lane.versions else "v1")
    split = args.split

    if not args.json and lane_name == "cognition":
        if split == "dev":
            cases_path = lane.dev_cases_path()
        elif split == "public":
            cases_path = lane.public_cases_path(version)
        else:
            cases_path = lane.holdout_cases_path(version)
        cases = load_cases(cases_path)
        effective_workers = normalize_workers(
            args.workers if args.workers is not None else 4,
            len(cases),
        )
        print(f"workers        : {effective_workers}")

    try:
        result = run_lane(
            lane,
            version=version,
            split=split,
            workers=args.workers,
        )
    except FileNotFoundError as exc:
        _die(str(exc))

    if args.json:
        print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"lane           : {result.lane}")
        print(f"version        : {result.version}")
        print(f"split          : {result.split}")
        print(f"cases          : {result.metrics.get('total', 0)}")
        for key, value in result.metrics.items():
            if key == "total":
                continue
            if isinstance(value, float):
                print(f"{key:15s}: {value:.1%}")
            else:
                print(f"{key:15s}: {value}")
        if lane_name == "cognition":
            # The cognition lane case_details carry `intent_correct` and
            # `versor_closure` booleans; other lanes do not, so the
            # cognition-specific failure printer is gated on lane identity to
            # avoid spurious "failures" output for lanes that pass cleanly.
            failures = [
                c for c in result.case_details
                if not c.get("intent_correct") or not c.get("versor_closure")
            ]
            if failures:
                print(f"\nfailures ({len(failures)}):")
                for c in failures:
                    issues = []
                    if not c.get("intent_correct"):
                        issues.append("intent")
                    if not c.get("versor_closure"):
                        vc = c.get("versor_condition", 0)
                        issues.append(f"versor={vc:.2e}")
                    cid = c.get("case_id") or c.get("id") or "<unknown>"
                    print(f"  {cid}: {', '.join(issues)}")

    if args.save:
        result_path = write_result(lane, result)
        print(f"\nresult written: {result_path}", file=sys.stderr)

    if args.report:
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result.as_dict(), ensure_ascii=False, indent=2, sort_keys=True)
        )
        print(f"\nreport written: {report_path}", file=sys.stderr)

    return 0


def cmd_eval_sensorium(args: argparse.Namespace) -> int:
    """Run deterministic sensorium modality evidence reports."""
    from evals.sensorium import build_sensorium_report

    modality = getattr(args, "modality", "vision") or "vision"
    try:
        report = build_sensorium_report(modality)
    except ValueError as exc:
        _die(str(exc), code=2)

    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"lane           : {report['lane']}")
        print(f"modality       : {report['modality']}")
        print(f"pack_id        : {report['pack_id']}")
        print(f"gate_engaged   : {report['gate_engaged']}")
        print(f"gate_closed    : {report['gate_closed']}")
        print(f"cases          : {report['total']}")
        print(f"passed         : {report['passed']}")
        print(f"failed         : {report['failed']}")

    if getattr(args, "report", None):
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        )
        print(f"\nreport written: {report_path}", file=sys.stderr)

    return 0 if report["failed"] == 0 and report["gate_closed"] else 1


def cmd_eval_environment_falsification(args: argparse.Namespace) -> int:
    """Run deterministic environmental falsification replay reports."""
    from evals.environment_falsification import build_environment_falsification_report

    report = build_environment_falsification_report()

    if getattr(args, "json", False):
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"lane           : {report['lane']}")
        print(f"version        : {report['version']}")
        print(f"cases          : {report['total']}")
        print(f"passed         : {report['passed']}")
        print(f"failed         : {report['failed']}")
        print(f"report_sha256  : {report['report_sha256']}")

    if getattr(args, "report", None):
        report_path = Path(args.report)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
        )
        print(f"\nreport written: {report_path}", file=sys.stderr)

    return 0 if report["failed"] == 0 and report["expected_report_hash_ok"] else 1


def cmd_eval_math_contemplation(args: argparse.Namespace) -> int:
    """ADR-0172 W3 — decompose an audit brief into refusal-shape proposals.

    Reads ``--audit`` (default: ``evals/gsm8k_math/train_sample/v1/audit_brief_11.json``),
    runs :func:`teaching.math_contemplation.decompose_audit`, and writes one
    ``canonical_bytes()`` JSON line per proposal to ``--output``
    (default: ``teaching/math_proposals/proposals.jsonl``).

    Idempotency: re-running on the same audit overwrites byte-identical bytes.
    Output is sorted by ``proposal_id`` (matches the decomposer sort contract).

    Exit codes:
      0  success
      1  audit file not found
      2  parse error or path-traversal rejection

    Forbidden by design: no proposal is auto-applied, no file outside
    ``teaching/math_proposals/`` is written, the audit file is not mutated.
    """
    from teaching.math_contemplation import decompose_audit
    from teaching.math_contemplation_proposal import to_jsonl_record

    audit_raw = getattr(args, "audit", None)
    output_raw = getattr(args, "output", None)

    audit_path = Path(audit_raw) if audit_raw else _DEFAULT_AUDIT_PATH
    if not audit_path.is_absolute():
        audit_path = (_REPO_ROOT / audit_path).resolve()

    if not audit_path.exists():
        _die(f"audit file not found: {audit_path}", code=1)

    output_path = _validate_output_path(output_raw)

    try:
        proposals = decompose_audit(audit_path)
    except json.JSONDecodeError as exc:
        _die(f"parse error in audit file {audit_path}: {exc}", code=2)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Self-contained JSONL (ADR-0172 tightening follow-up #1): each line
    # carries proposal_id, full evidence_pointers, and full
    # reasoning_trace.steps so consumers can load without re-running the
    # decomposer.
    lines: list[bytes] = []
    for proposal in proposals:
        record = to_jsonl_record(proposal)
        encoded = json.dumps(
            record,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        lines.append(encoded + b"\n")
    output_path.write_bytes(b"".join(lines))

    if not getattr(args, "json", False):
        print(f"proposals      : {len(proposals)}")
        print(f"output         : {output_path}")
    else:
        print(
            json.dumps(
                {
                    "proposals": len(proposals),
                    "output": str(output_path),
                },
                ensure_ascii=False,
                sort_keys=True,
            )
        )

    return 0


