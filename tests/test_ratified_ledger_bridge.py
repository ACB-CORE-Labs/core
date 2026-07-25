"""The ratified-ledger bridge (ADR-0263) — seal → ratify → SHA-verify → gate.

These tests pin the four rules the three adapters depend on, and the property
that made the extraction safe: re-sealing through the bridge reproduces the
committed artifacts byte-for-byte.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import pytest

from core.ratified_ledger import (
    CAPABILITY_LEDGERS,
    RatifiedLedgerError,
    load_capability_ledger,
    load_sealed_ledger,
    seal_artifact,
    serve_license,
    write_sealed_ledger,
)
from core.reliability_gate import ClassTally


def _tally(name: str, correct: int, wrong: int = 0) -> ClassTally:
    return ClassTally(class_name=name, correct=correct, wrong=wrong, refused=0)


def test_seal_then_load_round_trips(tmp_path) -> None:
    ledger = {"alpha": _tally("alpha", 700), "beta": _tally("beta", 12)}
    path = tmp_path / "ledger.json"
    write_sealed_ledger(
        path, seal_artifact(ledger, schema="t_v1", note="n", provenance="p")
    )
    loaded = load_sealed_ledger(path)
    assert set(loaded) == {"alpha", "beta"}
    assert loaded["alpha"].correct == 700


def test_a_hand_edited_ledger_is_rejected(tmp_path) -> None:
    """Rule 2 — tamper-evidence is structural. Editing a tally without
    re-sealing does not produce a slightly-wrong ledger; it produces an
    unratified one, and loading REFUSES."""
    path = tmp_path / "ledger.json"
    write_sealed_ledger(
        path,
        seal_artifact({"alpha": _tally("alpha", 10)}, schema="t_v1", note="n", provenance="p"),
    )
    artifact = json.loads(path.read_text())
    artifact["classes"]["alpha"]["correct"] = 9_999
    path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    with pytest.raises(RatifiedLedgerError):
        load_sealed_ledger(path)


def test_missing_ledger_refuses_unless_declared_optional(tmp_path) -> None:
    """A capability that SHIPS with a ledger is broken without it; one whose
    practice volume is still being built legitimately has none. Neither is
    answered by guessing a license."""
    path = tmp_path / "absent.json"
    with pytest.raises(RatifiedLedgerError):
        load_sealed_ledger(path)
    assert load_sealed_ledger(path, missing_ok=True) == {}


def test_absent_class_is_never_licensed() -> None:
    """Rule 4 — no evidence is not a license; the caller's ``None`` branch is
    what serves the disclosed surface."""
    assert serve_license("nobody", {"alpha": _tally("alpha", 700)}) is None


def test_volume_floor_is_enforced_by_the_gate() -> None:
    """A perfect but small record does not clear θ_SERVE=0.99 — the Wilson
    floor is what makes a license *earned* rather than merely clean."""
    small = serve_license("alpha", {"alpha": _tally("alpha", 12)})
    large = serve_license("alpha", {"alpha": _tally("alpha", 720)})
    assert small is not None and not small.licensed
    assert large is not None and large.licensed


def test_a_single_wrong_costs_the_license() -> None:
    dirty = serve_license("alpha", {"alpha": _tally("alpha", 720, wrong=1)})
    assert dirty is not None and not dirty.licensed


def test_committed_deduction_ledger_reseals_byte_identically() -> None:
    """The extraction's safety property: the bridge writes what the bespoke
    sealers wrote, so adopting it moves no committed artifact and no lane pin."""
    from pathlib import Path

    from evals.deduction_serve.practice.runner import build_sealed_artifact

    committed = Path("chat/data/deduction_serve_ledger.json")
    expected = json.dumps(build_sealed_artifact(), indent=2, sort_keys=True) + "\n"
    assert committed.read_text(encoding="utf-8") == expected


def test_every_adapter_reads_through_the_bridge() -> None:
    """All three instances now share one loader — the property that makes a
    future change to the ratification rule land everywhere at once."""
    import chat.curriculum_serve_license as curriculum
    import chat.deduction_serve_license as deduction
    import generate.determine.estimation_license as estimation

    for module in (deduction, estimation, curriculum):
        source = module.__file__ or ""
        assert source
        text = open(source, encoding="utf-8").read()
        assert "core.ratified_ledger" in text
        # The signal that an adapter still verifies for itself is that it
        # hashes for itself; docstrings may (and do) still explain the rule.
        assert "formation.hashing" not in text, (
            f"{module.__name__} still re-implements verification"
        )


class TestCapabilityManifest:
    """Rule 5 — absence policy is DECLARED, not passed at the call site.

    ``missing_ok`` answers a question about the capability ("does this ship
    with a ledger, or is its practice volume still being built?"), not about
    the call. While it was only a ``load_sealed_ledger`` keyword, any adapter
    onboarding a new subject through the bridge could pass ``True`` and quietly
    turn a should-be-hard-refuse into a disclosed hedge, with nothing to catch
    it. These pin the manifest that took the choice away from the call site.
    """

    def test_every_registered_ledger_resolves_inside_the_repo(self) -> None:
        """Same class as the ``derived_close_proposals`` ``parents[3]`` bug: a
        path constant that silently pointed outside the tree for five weeks
        because the feature was default-off and nothing asserted the path."""
        root = Path(__file__).resolve().parents[1]
        for spec in CAPABILITY_LEDGERS.values():
            assert root in spec.path.parents, (
                f"{spec.capability}: ledger path escapes the repo: {spec.path}"
            )

    def test_shipping_capabilities_are_declared_required(self) -> None:
        """A ledger that exists on disk must not be declared optional — that
        combination reads "absence is fine" about a capability whose absence
        would in fact be a broken deployment."""
        for spec in CAPABILITY_LEDGERS.values():
            if spec.path.exists():
                assert spec.missing_ok is False, (
                    f"{spec.capability} ships a committed ledger but is "
                    "registered missing_ok=True"
                )

    def test_deduction_serve_is_required_and_loads(self) -> None:
        ledger = load_capability_ledger("deduction_serve")
        assert len(ledger) == 25, "the 25 sealed shape-bands (ADR-0256)"
        assert all(tally.wrong == 0 for tally in ledger.values())

    def test_curriculum_serve_is_optional_and_empty_today(self) -> None:
        """ADR-0262 §5 — no band has earned a license from present volume."""
        assert CAPABILITY_LEDGERS["curriculum_serve"].missing_ok is True
        assert load_capability_ledger("curriculum_serve") == {}

    def test_unregistered_capability_refuses(self) -> None:
        """A capability the manifest never declared has no absence policy to
        inherit, so it cannot be consumed at all."""
        with pytest.raises(RatifiedLedgerError, match="unregistered"):
            load_capability_ledger("philosophy_serve")

    def test_no_production_adapter_passes_missing_ok(self) -> None:
        """The keyword survives on the primitive for tests and one-off tooling.
        If a serving path starts passing it again, the manifest has been routed
        around and this fails.

        Matched on the AST rather than the text: the string ``missing_ok``
        appears legitimately in the adapters' docstrings, which explain the
        policy they inherit. What must not appear is an *argument*.
        """
        root = Path(__file__).resolve().parents[1]
        offenders: list[str] = []
        for directory in ("chat", "core", "generate", "teaching", "workbench"):
            for path in sorted((root / directory).rglob("*.py")):
                if path.name == "ratified_ledger.py":
                    continue  # the primitive's own definition site
                tree = ast.parse(path.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    func = node.func
                    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
                    if name != "load_sealed_ledger":
                        continue
                    if any(kw.arg == "missing_ok" for kw in node.keywords):
                        offenders.append(f"{path.relative_to(root)}:{node.lineno}")
        assert offenders == [], f"missing_ok passed outside the manifest: {offenders}"
