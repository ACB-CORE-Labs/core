"""Phase D — the ``ledger_reseal`` ceremony stage and its CLI verb.

`RatificationReceipt.pending_stages` has named `ledger_reseal` since the
ratification ceremony was written and nothing performed it. This pins the verb
that performs it, and — more importantly — the reason it refuses by default.

The load-bearing property is **not** "the ledger can be rewritten". It is that
rewriting it cannot grant a serving license by accident. Reliability is
commitment precision, so a curriculum band clears θ_SERVE on correct
NON-COMMITMENTS alone; without the gate below, `reseal` would be a housekeeping
verb that silently made four bands authoritative.
"""

from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from core.ratified_ledger import CAPABILITY_LEDGERS, LedgerSpec, load_sealed_ledger
from core.reliability_gate import ClassTally
from teaching.ledger_reseal import (
    ReadyToReseal,
    ResealPlan,
    apply_reseal,
    plan_reseal,
    resealable_capabilities,
)


@pytest.fixture(scope="module")
def plan() -> ResealPlan:
    return plan_reseal("curriculum_serve")


# ---------------------------------------------------------------------------
# 1. What is resealable, and what must never be.
# ---------------------------------------------------------------------------

def test_only_curriculum_is_resealable() -> None:
    """`deduction_serve` must not be reachable from a CLI verb.

    Its ledger is SHA-sealed, ratified, and gating a live flag, and 21 of its 25
    bands do not clear θ_SERVE on distinct evidence
    (`tests/test_volume_honesty.py`). A reseal verb that regenerated it would
    erase a measured exposure as a side effect of housekeeping. `estimation`
    ships sealed with its own gate and has no reason to move.
    """
    assert resealable_capabilities() == ("curriculum_serve",)
    assert "deduction_serve" not in resealable_capabilities()
    assert "estimation" not in resealable_capabilities()
    # ...and both are still registered capabilities, so this is an exclusion by
    # decision rather than by them being unknown.
    assert {"deduction_serve", "estimation"} <= set(CAPABILITY_LEDGERS)


def test_unregistered_capability_refuses() -> None:
    with pytest.raises(ReadyToReseal, match="not resealable"):
        plan_reseal("deduction_serve")


# ---------------------------------------------------------------------------
# 2. Planning writes nothing, and reports the license delta.
# ---------------------------------------------------------------------------

def test_planning_writes_nothing(plan: ResealPlan) -> None:
    """A plan is a read. The artifact must still be absent afterwards."""
    assert not plan.path.exists(), (
        "planning a reseal must not create the ledger — see "
        "tests/test_curriculum_practice.py::test_curriculum_ledger_is_not_committed"
    )
    assert plan.capability == "curriculum_serve"
    assert plan.artifact["schema"] == "curriculum_serve_ledger_v1"


def test_plan_reports_the_bands_a_reseal_would_newly_license(plan: ResealPlan) -> None:
    """The whole point of the stage being a separate act.

    Nothing is licensed today (the ledger is absent), and a reseal would license
    four bands — every band whose routable atom space reaches 657. Those are the
    numbers `docs/research/curriculum-practice-producer-2026-07-26.md` §1 records.
    """
    assert plan.licensed_before == ()
    assert len(plan.licensed_after) == 4
    assert set(plan.newly_licensed) == set(plan.licensed_after)
    assert plan.revoked == ()
    assert plan.is_housekeeping is False


def test_newly_licensed_bands_are_licensed_on_non_commitments(plan: ResealPlan) -> None:
    """The mix the operator must see before authorizing — `ClassTally` has no
    verdict axis, so the gate itself cannot distinguish these from real
    competence."""
    for band in plan.newly_licensed:
        mix = plan.mix[band]
        assert mix.get("entailed", 0) <= 9
        assert mix.get("unknown", 0) > 600
        assert plan.committed[band] >= 657


# ---------------------------------------------------------------------------
# 3. Applying refuses to grant a license by accident. This is the unit.
# ---------------------------------------------------------------------------

def test_apply_refuses_to_grant_a_license_and_writes_nothing(
    plan: ResealPlan, tmp_path: Path
) -> None:
    target = tmp_path / "curriculum_serve_ledger.json"
    redirected = dataclasses.replace(plan, path=target)
    with pytest.raises(ReadyToReseal, match="would newly license 4 band"):
        apply_reseal(redirected)
    assert not target.exists(), "a refused reseal must not have written"


def test_refusal_names_the_bands_and_their_entailed_counts(
    plan: ResealPlan, tmp_path: Path
) -> None:
    """A refusal an operator cannot act on is just an obstacle."""
    with pytest.raises(ReadyToReseal) as exc:
        apply_reseal(dataclasses.replace(plan, path=tmp_path / "l.json"))
    message = str(exc.value)
    for band in plan.newly_licensed:
        assert band in message
    assert "entailed=" in message
    assert "--allow-new-licenses" in message
    assert "NON-COMMITMENTS" in message


def test_apply_with_explicit_authorization_writes_a_verifying_artifact(
    plan: ResealPlan, tmp_path: Path
) -> None:
    """The grant path works — into tmp, never into `chat/data/`."""
    target = tmp_path / "curriculum_serve_ledger.json"
    written = apply_reseal(
        dataclasses.replace(plan, path=target), allow_new_licenses=True
    )
    assert written == target
    tallies = load_sealed_ledger(target)
    assert len(tallies) == 11
    assert all(t.wrong == 0 for t in tallies.values())
    artifact = json.loads(target.read_text(encoding="utf-8"))
    assert artifact["provenance"] == "evals.curriculum_serve.practice.runner.seal_ledger"


def test_a_reseal_that_only_revokes_needs_no_authorization(tmp_path: Path) -> None:
    """Losing a license is the gate becoming MORE conservative.

    Only granting is gated. A producer change that drops a band below the floor
    must be applicable without an authorization flag, or the safe direction
    becomes the hard one.
    """
    plan = ResealPlan(
        capability="curriculum_serve",
        path=tmp_path / "l.json",
        licensed_before=("band_a", "band_b"),
        licensed_after=("band_a",),
        committed={"band_a": 700, "band_b": 3},
        mix={"band_a": {"entailed": 700}, "band_b": {"entailed": 3}},
        artifact={"schema": "x", "classes": {}, "content_sha256": "y"},
    )
    assert plan.newly_licensed == ()
    assert plan.revoked == ("band_b",)
    assert plan.is_housekeeping is True
    assert apply_reseal(plan) == plan.path  # no flag needed
    assert plan.path.exists()


def test_a_pure_housekeeping_reseal_is_allowed(tmp_path: Path) -> None:
    """Identical before/after — the ordinary case once volume is settled."""
    plan = ResealPlan(
        capability="curriculum_serve",
        path=tmp_path / "l.json",
        licensed_before=("band_a",),
        licensed_after=("band_a",),
        committed={"band_a": 700},
        mix={"band_a": {"entailed": 700}},
        artifact={"schema": "x", "classes": {}, "content_sha256": "y"},
    )
    assert plan.is_housekeeping is True
    apply_reseal(plan)
    assert plan.path.exists()


# ---------------------------------------------------------------------------
# 4. A tampered ledger on disk refuses rather than being silently overwritten.
# ---------------------------------------------------------------------------

def test_tampered_current_ledger_refuses_instead_of_being_overwritten(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Overwriting a hand-edited ledger would destroy the evidence of tampering.

    `plan_reseal` reads the current ledger through the SAME verifier the serving
    path uses, so a broken `content_sha256` surfaces here.
    """
    target = tmp_path / "curriculum_serve_ledger.json"
    target.write_text(
        json.dumps(
            {
                "schema": "curriculum_serve_ledger_v1",
                "classes": {"curriculum_physics_causal": {"correct": 999, "wrong": 0}},
                "content_sha256": "0" * 64,
                "note": "hand-edited",
                "provenance": "not-sealed-practice",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    import teaching.ledger_reseal as mod

    monkeypatch.setitem(
        mod.CAPABILITY_LEDGERS,
        "curriculum_serve",
        LedgerSpec(
            capability="curriculum_serve", path=target, missing_ok=True, note="test"
        ),
    )
    with pytest.raises(Exception, match="content_sha256 mismatch"):
        plan_reseal("curriculum_serve")
    # The tampered bytes are still there to be investigated.
    assert "hand-edited" in target.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 5. The CLI verb.
# ---------------------------------------------------------------------------

def _run_cli(*argv: str) -> tuple[int, str]:
    import argparse
    import io
    import contextlib

    from core.cli_proposal_queue import register

    parser = argparse.ArgumentParser()
    register(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args(["proposal-queue", *argv])
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        code = args.func(args)
    return code, buf.getvalue()


def test_cli_dry_run_reports_without_writing() -> None:
    code, out = _run_cli("reseal", "curriculum_serve", "--dry-run")
    assert code == 0
    assert "nothing written" in out
    assert "NEWLY LICENSED" in out
    assert not CAPABILITY_LEDGERS["curriculum_serve"].path.exists()


def test_cli_refuses_without_authorization() -> None:
    code, out = _run_cli("reseal", "curriculum_serve")
    assert code == 1
    assert "REFUSED" in out
    assert not CAPABILITY_LEDGERS["curriculum_serve"].path.exists()


def test_cli_json_is_machine_readable() -> None:
    code, out = _run_cli("reseal", "curriculum_serve", "--dry-run", "--json")
    assert code == 0
    payload = json.loads(out)
    assert payload["written"] is False
    assert payload["is_housekeeping"] is False
    assert len(payload["newly_licensed"]) == 4
    assert payload["licensed_before"] == []


def test_reseal_verb_is_registered_under_proposal_queue() -> None:
    """The verb has to be reachable from `core proposal-queue`, not only importable."""
    import argparse

    from core.cli_proposal_queue import register

    parser = argparse.ArgumentParser()
    register(parser.add_subparsers(dest="command", required=True))
    args = parser.parse_args(
        ["proposal-queue", "reseal", "curriculum_serve", "--dry-run"]
    )
    assert args.proposal_queue_command == "reseal"
    assert args.capability == "curriculum_serve"
    assert args.dry_run is True
    assert args.allow_new_licenses is False


# ---------------------------------------------------------------------------
# 6. The receipt now names the command that performs its pending stage.
# ---------------------------------------------------------------------------

def test_ratify_output_names_the_reseal_command() -> None:
    """Naming a pending stage without naming its command is how `ledger_reseal`
    stayed unperformed since the ceremony was written.

    Asserted at SOURCE level deliberately. Exercising the branch needs a
    successful non-dry-run ratification, which appends to the real committed
    corpus — the test would either mutate `teaching/domain_chains/` or stub out
    the very ceremony it claims to check. A source pin is the honest instrument
    here, and it is stated as one rather than dressed up as a behavioural test.
    """
    import inspect

    from teaching.ratification import RatificationReceipt

    import core.cli_proposal_queue as cli

    assert "ledger_reseal" in RatificationReceipt.__dataclass_fields__[
        "pending_stages"
    ].default

    source = inspect.getsource(cli.cmd_proposal_queue_ratify)
    assert 'if "ledger_reseal" in receipt.pending_stages' in source
    assert "core proposal-queue reseal curriculum_serve" in source


def test_reseal_stage_is_not_reachable_from_ratify_chain() -> None:
    """Doctrine: no ratification automation. `ratify_chain` must not seal."""
    import inspect

    import teaching.ratification as ratification

    source = inspect.getsource(ratification)
    for forbidden in ("ledger_reseal", "seal_ledger", "write_sealed_ledger"):
        assert f"import {forbidden}" not in source
        assert f"{forbidden}(" not in source
    tally = ClassTally("x", correct=1)
    assert tally.committed == 1  # sanity: the gate module is importable here
