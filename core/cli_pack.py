"""Extracted commands."""

from __future__ import annotations
import argparse
import json
import sys

from core.cli_teaching import _safe_pack_id
from core.cli import _die, _REPO_ROOT, _run


def cmd_pack_list(args: argparse.Namespace) -> int:
    """List compiled language packs."""
    from language_packs import list_packs

    packs = list_packs()
    if not packs:
        print("no compiled packs found")
        return 0
    for pack_id in packs:
        print(pack_id)
    return 0


def cmd_pack_verify(args: argparse.Namespace) -> int:
    """Verify one language pack checksum."""
    return _run(sys.executable, "-m", "language_packs", "verify", args.pack_id)


def cmd_pack_validate(args: argparse.Namespace) -> int:
    """Run executable source-pack validation gates."""
    pack_id = _safe_pack_id(args.pack_id)
    pack_dir = _REPO_ROOT / "packs" / pack_id
    validator_path = pack_dir / "validators.py"

    if not validator_path.exists():
        _die(f"source-pack validator not found: {validator_path}", code=1)

    if getattr(args, "dry_run", False):
        if args.json:
            print(
                json.dumps(
                    {
                        "pack_id": pack_id,
                        "validator_path": str(validator_path),
                        "would_execute": False,
                        "exists": True,
                    },
                    ensure_ascii=False,
                    indent=2,
                    sort_keys=True,
                )
            )
        else:
            print(f"dry-run: pack_id={pack_id}")
            print(f"validator: {validator_path}")
            print("status: validator exists, would not execute")
        return 0

    if not getattr(args, "allow_arbitrary_code", False):
        _die(
            "dynamic validator execution requires --allow-arbitrary-code",
            code=2,
        )

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        f"{pack_id}_validators", validator_path
    )
    if spec is None or spec.loader is None:
        _die(f"cannot load source-pack validator: {validator_path}", code=1)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    report = module.validate_pack()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"pack_id: {report['pack_id']}")
        print(f"active : {report['active']}")
        for name, result in report["gates"].items():
            status = "PASS" if result["passed"] else "FAIL"
            print(f"{status} {name:<12} {result['reason']}")
    return 0 if report["active"] else 1
