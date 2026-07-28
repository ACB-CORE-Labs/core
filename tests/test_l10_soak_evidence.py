"""PR-11 / G-5 / R-9 — the soak's evidence is committed, pinned, and still current.

The L10 always-on lane has passed a 5000-beat soak since 2026-07-19. That result
lived as **prose in a contract file** — no machine-readable artifact, no run SHA, no
rerun path, and a ``deterministic_digest`` that ``report.py`` computed and nothing
pinned. The contract's own closing line asked for the pin (*"Pin it once the lane is
trusted so a regression flips it"*) and it was never added. A recorded prose result
with no re-derivable artifact is testimony, not evidence.

This module makes it evidence, and it guards **two different failure modes** that are
easy to conflate:

**1. Regression.** The committed report's ``deterministic_digest`` is pinned. If the
per-beat shape or any verdict changes, the digest changes and this fails. The digest
deliberately excludes the machine-variant raw ``versor_condition`` float — and the
2026-07-28 re-run is the first evidence that exclusion was correct: every
*deterministic* fact reproduced exactly (vault bounded at 6, convergence at beat 1
with a 4999-beat tail, clean reboot resume with learning intact) while the float moved
from the prose's ``1.389e-07`` to ``6.177e-08``. A digest covering it would have
flipped on a machine change and taught everyone to ignore it.

**2. Staleness — the mode nothing guarded, and the one that already fired.**
R-9 ruled the cadence to be **change-triggered, not clock-triggered**: the local-first
doctrine makes "nightly" a ruling rather than a cron line, because a nightly that does
not run is green for the wrong reason. So instead of asking *"when did we last run
it?"*, this pin asks the question that actually matters — ***does this evidence still
describe the code that ships?*** — by pinning the SHA-256 of every source the soak
attests. Change one, and the pin says the evidence predates the change.

That is not hypothetical. It had **already happened, silently, for six weeks**: the
2026-07-19 soak ran with ``accrue_realized_knowledge`` absent from
``CONTINUOUS_LIFE_CONFIG_FLAGS``. R-3 added it on 2026-07-28 (PR-5), so the recorded
result stopped describing the shipping configuration — a soak result attesting a
process that no longer existed, with nothing anywhere able to notice. Had this pin
existed, PR-5 would have failed it, which is exactly the intended behaviour: *you
changed the always-on process; the soak evidence is now stale; re-run it.*

**When this fails, the fix is to re-run the soak — never to edit the constants.**
Updating a hash to match changed source, without re-running, converts this pin into a
record that says evidence exists when it does not. That is the failure this entire arc
is about, and it would be committed inside its own remedy.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_REPORT = _ROOT / "evals" / "l10_always_on" / "results" / "report-5000-6c67e88d.json"

#: The soak's verdict digest at 5000 beats, reboot at 2500, run 2026-07-28 under the
#: post-R-3 continuous-life profile. Covers the per-beat shape + the verdicts.
PINNED_DIGEST = "f814fd97f367840b0a9d31a48cb9fb28b2ed01961606f7b1e0b4c3a3593972d6"

#: Everything whose change invalidates the evidence above. Two groups, both load-bearing:
#: the always-on process itself (what the soak measures) and the harness (what the digest
#: *means*). A harness change with an unchanged digest would be the more dangerous of the
#: two, because it looks like stability.
ATTESTED_SOURCES: dict[str, str] = {
    "chat/always_on.py": "b733571e14fe540519861e9b7f24eb7be84782551dace43dab94cd96adf5d86b",
    "chat/always_on_daemon.py": "d69f234fcc15568016056da05a47c91b4abe16a6d8fb87512eec02b5526bc062",
    "evals/l10_always_on/runner.py": "9812cd549b41c36a8ee0477f7cb6282d5d9f110f931f3d770457a32aa54119f8",
    "evals/l10_always_on/predicates.py": "ef8e44db809e8fd2270ffa0d5ff8890ee09eedfce9f95836ea08d99ff9c12e2f",
    "evals/l10_always_on/report.py": "6c203af3eec6d78a1ddbfaadf3c7ad4ba18d0de0cc62a46227f210ca8b7f5277",
}

_RERUN = "PYTHONPATH=. uv run python -m evals.l10_always_on 5000 2500"


def _report() -> dict:
    return json.loads(_REPORT.read_text(encoding="utf-8"))


def test_the_committed_artifact_exists() -> None:
    """No artifact, no evidence. G-5 reopens the moment this file is gone."""
    assert _REPORT.exists(), (
        f"the committed soak report is missing: {_REPORT.relative_to(_ROOT)}. "
        f"Re-run and commit it: {_RERUN}"
    )


def test_the_artifact_records_the_horizon_it_claims() -> None:
    """A 24-beat report pinned as though it were the 5000-beat one would pass every
    other assertion here. The horizon *is* the claim."""
    report = _report()
    assert report["n_beats"] == 5000, (
        f"the committed report is a {report['n_beats']}-beat run; the contract's claim "
        "is the 5000-beat horizon"
    )
    assert report["reboot_beat"] == 2500, (
        f"reboot leg at beat {report['reboot_beat']}, not 2500 — H4 proves resume "
        "mid-soak, so where the reboot lands is part of the claim"
    )


def test_all_four_predicates_passed() -> None:
    """H1-H4, by name. ``all_gates_pass`` alone would be satisfied by an empty
    predicate list, which is the vacuity this repository keeps finding."""
    report = _report()
    outcomes = {p["name"]: p["passed"] for p in report["predicates"]}
    assert set(outcomes) == {
        "H1_closure",
        "H2_bounded_idle",
        "H3_convergence",
        "H4_reboot_resume",
    }, f"the report's predicate set is not H1-H4: {sorted(outcomes)}"
    failed = sorted(name for name, passed in outcomes.items() if not passed)
    assert not failed, f"the committed soak report records FAILING predicates: {failed}"
    assert report["all_gates_pass"] is True


def test_the_digest_is_pinned() -> None:
    """The contract's own unmet closing instruction, finally met.

    If this fails, the soak's per-beat shape or a verdict changed. That is either a
    regression or a deliberate improvement; either way it is a reviewed decision, which
    is the whole point of pinning it.
    """
    digest = _report()["deterministic_digest"]
    assert digest == PINNED_DIGEST, (
        "the committed soak report's deterministic_digest does not match the pin.\n"
        f"  pinned:    {PINNED_DIGEST}\n"
        f"  in report: {digest}\n"
        "The per-beat shape or a verdict moved. Investigate before re-pinning."
    )


def test_the_evidence_still_describes_the_code_that_ships() -> None:
    """R-9's change-triggered cadence, enforced as a pin rather than a clock.

    This is the assertion that would have caught the six-week divergence described in
    this module's docstring. It fails when a source the soak attests has changed since
    the soak ran.
    """
    drifted: list[str] = []
    missing: list[str] = []
    for rel, expected in sorted(ATTESTED_SOURCES.items()):
        path = _ROOT / rel
        if not path.exists():
            missing.append(rel)
            continue
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            drifted.append(f"{rel}\n      attested {expected[:16]}…\n      current  {actual[:16]}…")

    assert not missing, (
        f"the soak attests sources that no longer exist: {missing}. The pin cannot "
        "describe the current system; re-scope ATTESTED_SOURCES and re-run."
    )
    assert not drifted, (
        "the committed soak evidence PREDATES a change to the code it attests, so it no "
        "longer describes what ships:\n    "
        + "\n    ".join(drifted)
        + f"\n\n  RE-RUN THE SOAK — do not edit the hashes:\n    {_RERUN}\n"
        "  then commit the new report, update PINNED_DIGEST and ATTESTED_SOURCES\n"
        "  together, in one change. Editing a hash without re-running turns this pin\n"
        "  into a record asserting evidence that does not exist."
    )


def test_the_attested_set_is_not_vacuous() -> None:
    """Guard the guard.

    An empty or truncated ATTESTED_SOURCES would make the staleness check pass on
    nothing while still reporting success — the failure mode this module exists to
    close, reproduced inside it.
    """
    assert len(ATTESTED_SOURCES) >= 5, (
        f"only {len(ATTESTED_SOURCES)} sources attested; the staleness check is "
        "narrower than the lane it guards"
    )
    assert "chat/always_on_daemon.py" in ATTESTED_SOURCES, (
        "the daemon module carries CONTINUOUS_LIFE_CONFIG_FLAGS — the exact thing whose "
        "silent change made the previous soak result stale. It cannot leave this set."
    )
    assert all(len(h) == 64 for h in ATTESTED_SOURCES.values()), (
        "an attested hash is not a full SHA-256; a truncated hash weakens the check "
        "silently"
    )
