"""The ratified-ledger bridge (ADR-0263) — seal → ratify → SHA-verify → gate.

These tests pin the four rules the three adapters depend on, and the property
that made the extraction safe: re-sealing through the bridge reproduces the
committed artifacts byte-for-byte.
"""

from __future__ import annotations

import json

import pytest

from core.ratified_ledger import (
    RatifiedLedgerError,
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
