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
GATE_SUITES: frozenset[str] = frozenset({"smoke", "deductive", "teaching"})

#: Curated suites with members and no gate caller.
#: 19 at first measurement; **15 after PR-3b (Wave 1)** deleted four unreferenced
#: per-phase aliases — `refusal`, `margin`, `rotor`, `inner-loop` — the ratchet
#: turning by deletion, which costs no gate time at all. **14 after PR-4b promoted
#: `teaching` onto the gate (2026-07-28)** — the first time it turned by PROMOTION,
#: which is the direction that actually buys coverage and the direction that costs.
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

    14 of 17, after PR-4b. (15 after PR-3b; 19 of 21 before it.) Shrinking this is
    the point, and it shrinks two ways: by deleting a suite nobody calls (free) or by
    putting one on the gate (costs gate time on every push, and is therefore a
    decision someone has to make deliberately). PR-4b was the first of the second
    kind — `teaching`, at a measured 22.1s for 9 net-new files.
    """
    assert len(UNREACHABLE_BASELINE) <= 14, (
        f"gate-unreachable suites grew to {len(UNREACHABLE_BASELINE)} (was 14; 15 "
        "before PR-4b promoted `teaching`, 19 before PR-3b deleted four unreferenced "
        "aliases). The ratchet only turns one way."
    )


def test_the_two_gate_suites_actually_exist() -> None:
    """A gate that names a suite the CLI does not define would fail closed at
    run time, but silently here. Pin it."""
    suites = _curated_suites()
    for name in GATE_SUITES:
        assert name in suites, f"gate tier invokes undefined suite {name!r}"
        assert suites[name], f"gate suite {name!r} is empty"


#: A gate step in either script, e.g. ``(4/4) teaching suite ... suite teaching``.
#: The ``(n/m)`` prefix is the discriminator: ``local-ci.sh`` defines other tiers
#: whose steps are unnumbered, so this scopes the parse to the gate tier without
#: needing to parse shell control flow.
_GATE_STEP_RE = re.compile(r"\(\d+/\d+\)[^\n]*?\bsuite[= ]+([a-z0-9-]+)")


def _gate_suites_in(rel: str) -> set[str]:
    text = (_ROOT / rel).read_text(encoding="utf-8")
    return set(_GATE_STEP_RE.findall(text))


def test_the_two_gate_scripts_invoke_the_same_suites() -> None:
    """``pre-push`` and ``local-ci.sh --tier gate`` must not drift apart.

    Both scripts state that they are the same gate — ``local-ci.sh`` says so in
    prose ("same four steps as scripts/hooks/pre-push"). Two records asserting the
    same thing is the shape that goes stale, and until this pin the drift was
    invisible: :func:`test_declared_gate_suites_match_the_shell` takes the UNION of
    the two files, so a suite present in either satisfies it. Removing `teaching`
    from ``local-ci.sh`` alone was sabotage-tested and passed — which is how this
    gap was found.

    **This is NOT the CI-parity pin that N-9 correctly killed.** That one asserted
    ``TEST_SUITES["smoke"] == smoke.yml`` and was reverted in ``50fa287d`` because
    ``AGENTS.md:280`` makes GitHub Actions billing-locked dead signals — parity with
    a dead signal buys nothing. Both scripts here are live local merge bars, and a
    developer running one is entitled to the coverage the other advertises.
    """
    hook = _gate_suites_in("scripts/hooks/pre-push")
    local = _gate_suites_in("scripts/ci/local-ci.sh")
    assert hook, "parsed no numbered gate steps from scripts/hooks/pre-push"
    assert local, "parsed no numbered gate steps from scripts/ci/local-ci.sh --tier gate"
    assert hook == local, (
        "the two gate scripts have drifted — a push through the hook and a run of "
        "local-ci.sh --tier gate would cover different suites:\n"
        f"  pre-push only: {sorted(hook - local)}\n"
        f"  local-ci only: {sorted(local - hook)}"
    )
    assert hook <= set(GATE_SUITES), (
        f"the scripts invoke suites GATE_SUITES does not declare: {sorted(hook - set(GATE_SUITES))}"
    )
