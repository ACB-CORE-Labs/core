"""PR-4 / G-7 — a test file may not land outside every curated suite.

The failure mode, demonstrated four times in this repository: a pin is written
for a real defect, lands in no curated suite, therefore runs on no pre-merge
gate, and the thing it pins regresses anyway. #113 (``test_adr_index``), #136,
``test_negation_survives_articulation``, and — while fixing H-13 on 2026-07-28
— ``test_speculative_subject_lifecycle``, which pinned the exact behavior that
had silently broken. Each was repaired individually, after shipping.

**Why this is a ratchet and not a membership assertion.** The plan originally
specified "every ``tests/**/test_*.py`` belongs to >=1 suite excluding ``full``,
or to a registered exclusion list with a reason." Measured at 2026-07-28 that is
749 files against 128 curated. Both ways of satisfying it at that scale are
hollow: glob-defined topic suites (``"adr": ("tests/test_adr_*.py",)`` alone
absorbs 172) make the assertion pass while changing nothing about what executes,
and 749 hand-written exclusion reasons are ceremony. A curated suite nobody runs
is the same non-guarantee as ``full``, wearing a different name — which is the
objection the plan itself raises against G-7's first formulation.

None of the 749 legacy files caused any of the four incidents. A *new* orphan
caused all four. So the pin with teeth is the one that blocks new orphans and
makes the legacy set a declared, monotonically shrinking number.

Recorded as N-9 in ``docs/assessment/50-execution-plan.md``.
"""

from __future__ import annotations

import ast
import glob
import re
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[1]
_BASELINE = _ROOT / "tests" / "full_only_baseline.txt"


def _curated_files() -> set[str]:
    """Every test path reachable from a curated suite other than ``full``.

    ``TEST_SUITES`` is parsed from source rather than imported so this pin keeps
    working if importing the CLI ever acquires a side effect; the tuple is a
    literal by construction (``test_cli_test_suites.py`` pins its shape).
    """
    src = (_ROOT / "core" / "cli_test.py").read_text(encoding="utf-8")
    match = re.search(r"TEST_SUITES\s*(?::[^=]+)?=\s*\{", src)
    assert match is not None, "TEST_SUITES literal not found in core/cli_test.py"
    start = match.end() - 1
    depth = 0
    end = len(src)
    for i, ch in enumerate(src[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    suites = ast.literal_eval(src[start:end])

    curated: set[str] = set()
    for name, patterns in suites.items():
        if name == "full":
            # ``full`` is ("tests/",) — a DIRECTORY, so it matches every test
            # file trivially. Counting it would make this pin vacuous; that
            # scan artifact is N-1 in the execution plan and has now produced
            # three false conclusions in this repository.
            continue
        for pattern in patterns:
            curated.update(str(Path(p).as_posix()) for p in glob.glob(pattern))
    return curated


def _all_test_files() -> set[str]:
    return {
        str(Path(p).as_posix())
        for p in glob.glob("tests/**/test_*.py", recursive=True)
    }


def _baseline() -> list[str]:
    lines = _BASELINE.read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.lstrip().startswith("#")]


def test_baseline_file_exists_and_is_sorted_and_unique() -> None:
    entries = _baseline()
    assert entries, "the baseline is empty — it should list the known full-only tests"
    assert entries == sorted(entries), "baseline must stay sorted (stable diffs)"
    assert len(entries) == len(set(entries)), "baseline contains duplicates"


def test_no_new_full_only_test_files() -> None:
    """A new test file must join a curated suite, or the gate it needs is absent.

    If this fails on a file you just added: put it in the suite whose lane it
    actually belongs to in ``core/cli_test.py::TEST_SUITES``. Adding it to the
    baseline instead is available and is almost always the wrong answer — the
    baseline is for files that predate this pin, not an opt-out.
    """
    orphans = _all_test_files() - _curated_files()
    unlisted = sorted(orphans - set(_baseline()))
    assert not unlisted, (
        "these test files are in no curated suite and are not in the recorded "
        "baseline, so they run on no pre-merge gate:\n  "
        + "\n  ".join(unlisted)
        + "\n\nRegister each in core/cli_test.py::TEST_SUITES."
    )


def test_baseline_has_no_stale_entries() -> None:
    """The list may only shrink — a promoted or deleted file must leave it.

    Enforced in BOTH directions, in the discipline ``test_volume_honesty.py``
    uses: a baseline that silently keeps entries it no longer needs stops being
    a measurement and becomes a story about one.
    """
    curated = _curated_files()
    present = _all_test_files()
    entries = _baseline()

    vanished = sorted(e for e in entries if e not in present)
    assert not vanished, (
        "baseline names files that no longer exist — delete these lines:\n  "
        + "\n  ".join(vanished)
    )

    promoted = sorted(e for e in entries if e in curated)
    assert not promoted, (
        "these files are now in a curated suite (good) but are still listed as "
        "full-only — delete their baseline lines so the count reflects reality:\n  "
        + "\n  ".join(promoted)
    )


def test_recorded_debt_matches_the_measurement() -> None:
    """Pin the number so a bulk change to it shows up as a reviewed decision.

    749 at 2026-07-28. Lowering this is the point; raising it must be argued
    for, not slipped in. The assertion names the direction so a reviewer of a
    failing run knows immediately which one happened.
    """
    entries = _baseline()
    assert len(entries) <= 749, (
        f"full-only test debt grew to {len(entries)} (was 749). The ratchet only "
        "turns one way — register the new files in a curated suite instead."
    )


def test_the_gate_guarding_pin_runs_on_the_gate() -> None:
    """The parity pin must itself be in ``smoke`` (N-9).

    ``test_cli_smoke_suite_covers_ci_smoke_gate`` enforces that the local suite
    is never narrower than ``smoke.yml``. It lived in ``fast``, while the
    pre-push gate runs ``smoke`` + ``deductive`` — so the pin guarding the gate
    did not run on the gate. This keeps it there.
    """
    curated_src = (_ROOT / "core" / "cli_test.py").read_text(encoding="utf-8")
    match = re.search(r"TEST_SUITES\s*(?::[^=]+)?=\s*\{", curated_src)
    assert match is not None
    start = match.end() - 1
    depth = 0
    end = len(curated_src)
    for i, ch in enumerate(curated_src[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    suites = ast.literal_eval(curated_src[start:end])
    assert "tests/test_cli_test_suites.py" in suites["smoke"], (
        "the smoke/CI parity pin must run on the gate it protects"
    )


def test_this_pin_is_itself_registered() -> None:
    """No exemption for the membership pin — #136's lesson applied to itself."""
    orphans = _all_test_files() - _curated_files()
    assert "tests/test_suite_membership.py" not in orphans
