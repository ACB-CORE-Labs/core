"""PR-4 pin 3 / G-7 — a curated suite that no gate invokes is not a guarantee.

PR-4's ratchet closed *membership*: a new test file cannot land outside every
curated suite. Within the hour it turned out membership was never the property
that mattered.

This arc's first full-tree run found ``tests/test_ratification_ceremony.py``
**red on main, in the curated suite `teaching`, and invoked by no gate tier**.
Membership was satisfied and bought nothing — which is precisely the objection
PR-4 itself raised against G-7's original formulation: *a curated suite nobody
runs is the same non-guarantee as ``full``, wearing a different name.* The fix
had the same blind spot as the thing it fixed.

Measured at 2026-07-28: **21 curated suites, 2 gate-reachable** — then **17 and 2** after PR-3b deleted four aliases nothing invoked. ``smoke`` and
``deductive`` are invoked by ``scripts/hooks/pre-push`` and
``scripts/ci/local-ci.sh --tier gate``; the other nineteen have members and no
caller. That is why this is a **baseline plus ratchet** and not a flat rule —
demanding nineteen ``post-merge-only`` justifications in one sitting is the
ceremony failure rejected for the 749-file membership baseline, and it would
buy a wall of text rather than a decision.

What this pin does:
  * freezes the currently-unreachable set, so it cannot grow silently;
  * fails when a **new** curated suite is added with no gate caller and no
    explicit declaration;
  * fails when a suite leaves the unreachable set (promoted to a gate) and its
    baseline line is not removed — the same both-directions discipline that
    caught this file's author twice already.

What it deliberately does **not** do: decide which of the nineteen belong on
the gate. That is a real decision with a real time cost, and it is Shay's.
This pin makes the state visible and stops it worsening.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

#: Suites invoked by a gate tier today. Parsed rather than hard-coded would be
#: nicer, but the invocations are shell (``step "…" suite smoke``) and a parse
#: that silently matched nothing would make this pin vacuous — the exact
#: failure mode (N-1) that has produced three false conclusions in this repo.
#: So the set is declared here and *verified* against the shell below.
GATE_SUITES: frozenset[str] = frozenset({"smoke", "deductive"})

#: Curated suites with members and no gate caller.
#: 19 at first measurement; **15 after PR-3b (Wave 1) deleted four unreferenced
#: per-phase aliases** — `refusal`, `margin`, `rotor`, `inner-loop`. That is the
#: ratchet turning the way it is supposed to: the gap shrank by deletion rather
#: than by promotion, which costs no gate time at all.
#: This list may only SHRINK. A suite leaves it by being invoked from a gate
#: tier — not by being deleted from this file.
UNREACHABLE_BASELINE: frozenset[str] = frozenset(
    {
        "adr-0024",
        "algebra",
        "cognition",
        "fast",
        "formation",
        "full",
        "math",
        "packs",
        "phase5",
        "phase6",
        "proof",
        "pulse",
        "runtime",
        "sensorium",
        "teaching",
    }
)


def _curated_suites() -> dict[str, tuple[str, ...]]:
    src = (_ROOT / "core" / "cli_test.py").read_text(encoding="utf-8")
    match = re.search(r"TEST_SUITES\s*(?::[^=]+)?=\s*\{", src)
    assert match is not None, "TEST_SUITES literal not found"
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
    return ast.literal_eval(src[start:end])


def _suites_invoked_by_gate_tiers() -> set[str]:
    """Suites named by a ``suite <name>`` step in the hook or the gate tier."""
    found: set[str] = set()
    for rel in ("scripts/hooks/pre-push", "scripts/ci/local-ci.sh"):
        text = (_ROOT / rel).read_text(encoding="utf-8")
        found.update(re.findall(r"--suite\s+([a-z0-9-]+)", text))
        found.update(re.findall(r"\bsuite\s+([a-z0-9-]+)\s*$", text, re.MULTILINE))
    # ``full`` is the arc-boundary tier, not a gate; it is not a merge bar.
    found.discard("full")
    found.discard("only")  # prose match guard
    return found


def test_declared_gate_suites_match_the_shell() -> None:
    """GATE_SUITES must be what the hook and gate tier actually invoke.

    Without this, the pin below could pass while pointing at a fiction — a
    declared set that drifted from the scripts it claims to describe.
    """
    invoked = _suites_invoked_by_gate_tiers()
    assert invoked, "parsed no suite invocations — the pin would be vacuous"
    assert invoked == set(GATE_SUITES), (
        f"gate tiers invoke {sorted(invoked)}, but GATE_SUITES declares "
        f"{sorted(GATE_SUITES)} — update the constant with the change that "
        "moved the gate, and move any promoted suite out of "
        "UNREACHABLE_BASELINE in the same edit"
    )


def test_no_new_gate_unreachable_suite() -> None:
    """A new curated suite must be gate-reachable or explicitly baselined.

    If this fails on a suite you just added: either invoke it from a gate tier
    (``scripts/hooks/pre-push`` / ``local-ci.sh --tier gate``), or add it to
    UNREACHABLE_BASELINE with the reason in your commit message. The second is
    available and is a decision, not a default — a suite nobody runs guarantees
    nothing.
    """
    suites = set(_curated_suites())
    unreachable = suites - set(GATE_SUITES)
    undeclared = sorted(unreachable - UNREACHABLE_BASELINE)
    assert not undeclared, (
        "these curated suites have members and no gate caller, and are not in "
        f"the recorded baseline: {undeclared}"
    )


def test_baseline_has_no_stale_entries() -> None:
    """Both directions: a promoted or deleted suite must leave the baseline.

    Same discipline as ``test_suite_membership.py`` — a baseline that keeps
    entries it no longer needs stops being a measurement and becomes a story
    about one.
    """
    suites = set(_curated_suites())

    vanished = sorted(s for s in UNREACHABLE_BASELINE if s not in suites)
    assert not vanished, (
        f"baseline names suites that no longer exist: {vanished}"
    )

    promoted = sorted(s for s in UNREACHABLE_BASELINE if s in GATE_SUITES)
    assert not promoted, (
        "these suites are now gate-reachable (good) but are still listed as "
        f"unreachable — remove them from UNREACHABLE_BASELINE: {promoted}"
    )


def test_recorded_gate_gap_matches_the_measurement() -> None:
    """Pin the number so the gap moving is a reviewed decision, not a drift.

    15 of 17, after PR-3b. (19 of 21 before it.) Shrinking this is the point — it shrinks by putting
    a suite on the gate, which costs gate time and is therefore a decision
    someone has to make deliberately.
    """
    assert len(UNREACHABLE_BASELINE) <= 15, (
        f"gate-unreachable suites grew to {len(UNREACHABLE_BASELINE)} (was 15; "
        "19 before PR-3b deleted four unreferenced aliases). The ratchet only "
        "turns one way."
    )


def test_the_two_gate_suites_actually_exist() -> None:
    """A gate that names a suite the CLI does not define would fail closed at
    run time, but silently here. Pin it."""
    suites = _curated_suites()
    for name in GATE_SUITES:
        assert name in suites, f"gate tier invokes undefined suite {name!r}"
        assert suites[name], f"gate suite {name!r} is empty"
