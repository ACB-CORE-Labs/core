"""Doctor/package-health CLI command handler."""

from __future__ import annotations

import argparse
from pathlib import Path

from core import cli_rust


DEFAULT_REPO_ROOT = Path(__file__).resolve().parent.parent

IMPORT_CHECKS: tuple[tuple[str, str], ...] = (
    ("algebra", "algebra"),
    ("alignment", "alignment.graph"),
    ("benchmarks", "benchmarks.run_benchmarks"),
    ("calibration", "calibration"),
    ("chat", "chat.runtime"),
    ("core_ingest", "core_ingest"),
    ("demos", "demos.claude_tool_authority"),
    ("engine_state", "engine_state"),
    ("evals", "evals.framework"),
    ("language_packs", "language_packs"),
    ("morphology", "morphology.registry"),
    ("packs", "packs.safety.loader"),
    ("scripts", "scripts.run_pulse"),
    ("sensorium", "sensorium.protocol"),
    ("teaching", "teaching"),
    ("workbench", "workbench"),
)


def cmd_doctor(args: argparse.Namespace, *, repo_root: Path = DEFAULT_REPO_ROOT) -> int:
    """Inspect import/package health for the CLI runtime path."""
    ok = True
    print(f"repo_root: {repo_root}")
    for label, module_name in IMPORT_CHECKS:
        try:
            __import__(module_name)
        except Exception as exc:
            ok = False
            print(f"FAIL {label:<14} {module_name}: {exc.__class__.__name__}: {exc}")
        else:
            print(f"OK   {label:<14} {module_name}")

    rust_importable, rust_detail = cli_rust.probe_core_rs()
    print(
        "INFO native core_rs "
        f"{'importable' if rust_importable else 'not importable'}: {rust_detail}"
    )
    print(
        "INFO native policy  optional; run `core doctor --rust --require-rust` to gate it"
    )

    if args.packs:
        try:
            from language_packs import list_packs

            packs = list_packs()
        except Exception as exc:
            ok = False
            print(
                f"FAIL packs          language_packs.list_packs: {exc.__class__.__name__}: {exc}"
            )
        else:
            print("packs:")
            if packs:
                for pack_id in packs:
                    print(f"  {pack_id}")
            else:
                print("  none found")

    if args.rust:
        rust_active = cli_rust.print_rust_status(repo_root=repo_root)
        if args.require_rust and not rust_active:
            ok = False
    return 0 if ok else 1
