"""Operator-facing CLI for the durable ``core_ingest`` boundary."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

from core_ingest import IngestPipeline, IngestPipelineConfig, SegmentManifold
from core_ingest.types import LearningArtifact, SourceSpan, ValidationReport


_MODALITY_HINTS = ("prose", "scripture", "code", "math")
_DEFAULT_MAX_BYTES = 1_048_576
_TRUST_BOUNDARY = (
    "read_only_durable_core_ingest_compile_no_gate_import_no_vault_or_pack_mutation"
)


def _source_from_args(args: argparse.Namespace) -> tuple[bytes, dict[str, Any]]:
    if args.text is not None:
        source = args.text.encode("utf-8")
        return source, {
            "kind": "text",
            "bytes": len(source),
            "sha256": hashlib.sha256(source).hexdigest(),
        }

    path = Path(args.file).expanduser()
    try:
        resolved = path.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValueError(f"source file does not exist: {path}") from exc

    if not resolved.is_file():
        raise ValueError(f"source path is not a regular file: {resolved}")

    size = resolved.stat().st_size
    if size > args.max_bytes:
        raise ValueError(
            f"source file is {size} bytes, above --max-bytes {args.max_bytes}"
        )

    source = resolved.read_bytes()
    return source, {
        "kind": "file",
        "path": str(resolved),
        "bytes": len(source),
        "sha256": hashlib.sha256(source).hexdigest(),
    }


def _span_payload(span: SourceSpan) -> dict[str, Any]:
    return {
        "byte_start": span.byte_start,
        "byte_end": span.byte_end,
        "source_sha256": span.source_sha256,
        "page": span.page,
        "region": span.region,
    }


def _report_payload(
    *,
    source_info: dict[str, Any],
    modality_hint: str,
    report: ValidationReport,
    artifacts: list[LearningArtifact],
    manifold: SegmentManifold,
    register_all: bool,
) -> dict[str, Any]:
    return {
        "command": "ingest compile",
        "path": "durable",
        "boundary_owner": "core_ingest",
        "runtime_gate": "ingest/gate.py is not imported or called",
        "trust_boundary": _TRUST_BOUNDARY,
        "mutates": False,
        "modality_hint": modality_hint,
        "source": source_info,
        "summary": {
            "results": len(report.results),
            "accepted": len(report.accepted_ids),
            "rejected": len(report.rejected_ids),
            "review_required": len(report.review_ids),
            "acceptance_rate": report.acceptance_rate,
            "manifold_keys": len(manifold),
            "register_all": register_all,
        },
        "results": [
            {
                "pressure_id": result.pressure_id,
                "semantic_key": result.semantic_key,
                "disposition": result.disposition.value,
                "gate_failed": result.gate_failed,
                "failure_reason": result.failure_reason,
                "warnings": list(result.warnings),
            }
            for result in report.results
        ],
        "artifacts": [
            {
                "pressure_id": artifact.packet.pressure_id,
                "semantic_key": artifact.packet.semantic_key,
                "kind": artifact.packet.kind,
                "modality": artifact.packet.modality.value,
                "review_level": artifact.packet.review_level.value,
                "instrument_id": artifact.packet.frontend.instrument_id,
                "lemma": artifact.packet.lemma,
                "spans": [_span_payload(span) for span in artifact.packet.provenance],
            }
            for artifact in artifacts
        ],
    }


def _print_text(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    source = payload["source"]
    source_label = (
        source["path"] if source["kind"] == "file" else f"inline:{source['sha256'][:12]}"
    )
    print("core_ingest durable compile")
    print(f"source         : {source_label}")
    print(f"source_bytes   : {source['bytes']}")
    print(f"modality_hint  : {payload['modality_hint']}")
    print(f"trust_boundary : {payload['trust_boundary']}")
    print(f"runtime_gate   : {payload['runtime_gate']}")
    print(f"mutates        : {payload['mutates']}")
    print(f"results        : {summary['results']}")
    print(f"accepted       : {summary['accepted']}")
    print(f"rejected       : {summary['rejected']}")
    print(f"review_required: {summary['review_required']}")
    print(f"acceptance_rate: {summary['acceptance_rate']:.3f}")
    for result in payload["results"][:10]:
        reason = f" {result['failure_reason']}" if result["failure_reason"] else ""
        print(
            f"  {result['disposition']:<20} "
            f"{result['pressure_id'][:12]} semantic={result['semantic_key'][:12]}"
            f"{reason}"
        )
    if len(payload["results"]) > 10:
        print(f"  ... {len(payload['results']) - 10} more result(s)")


def cmd_ingest_compile(args: argparse.Namespace) -> int:
    """Run the durable core_ingest pipeline and print a validation report."""
    try:
        source, source_info = _source_from_args(args)
        if not source:
            raise ValueError("ingest source is empty")
        manifold = SegmentManifold()
        pipeline = IngestPipeline(
            manifold=manifold,
            config=IngestPipelineConfig(register_all=args.register_all),
        )
        report, artifacts = pipeline.run(source, modality_hint=args.modality)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = _report_payload(
        source_info=source_info,
        modality_hint=args.modality,
        report=report,
        artifacts=artifacts,
        manifold=manifold,
        register_all=args.register_all,
    )
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_text(payload)
    return 0


def register(subparsers: argparse._SubParsersAction) -> None:
    """Attach the ``core ingest`` subcommand tree to a top-level parser."""
    ingest = subparsers.add_parser(
        "ingest",
        help="inspect durable input-to-pressure compilation",
        description=(
            "Run the durable core_ingest compiler. This is read-only: it does "
            "not import ingest/gate.py, write vault memory, mutate packs, or "
            "ratify learning."
        ),
    )
    sub = ingest.add_subparsers(
        dest="ingest_command", metavar="ingest-command", required=True,
    )

    compile_cmd = sub.add_parser(
        "compile",
        help="compile source bytes into validated candidate pressure",
        description=(
            "Compile source bytes through StructuralSegmenter -> "
            "IngestCompiler -> SegmentManifold and emit a validation report."
        ),
    )
    source = compile_cmd.add_mutually_exclusive_group(required=True)
    source.add_argument("--text", help="inline UTF-8 source text to compile")
    source.add_argument(
        "--file",
        type=Path,
        help="regular local file to read as source bytes",
    )
    compile_cmd.add_argument(
        "--modality",
        choices=_MODALITY_HINTS,
        default="prose",
        help="structural modality hint (default: prose)",
    )
    compile_cmd.add_argument(
        "--max-bytes",
        type=int,
        default=_DEFAULT_MAX_BYTES,
        help=f"maximum file size accepted by --file (default: {_DEFAULT_MAX_BYTES})",
    )
    compile_cmd.add_argument(
        "--register-all",
        action="store_true",
        help="index rejected packets in the reconstruction manifold report",
    )
    compile_cmd.add_argument("--json", action="store_true", help="emit JSON")
    compile_cmd.set_defaults(func=cmd_ingest_compile)
