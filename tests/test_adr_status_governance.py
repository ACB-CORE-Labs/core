"""An ADR that governs live behaviour must not still be stamped ``Proposed``.

Nine ADRs (0254, 0256-0263) sat at ``Proposed`` while merged into ``main``,
two of them carrying an explicit ``ratify-on-merge`` predicate that the merge
had already discharged, and one -- ADR-0256 -- governing
``deduction_serving_enabled``, which was ratified ``True`` and serving live
traffic.  Nothing failed.  The governance record and the running system
disagreed for a day and the only reason it surfaced was a human reading the
files.

This is the "pinned list goes stale" family that has now been caught four
separate ways in this repo (a stale suite tuple, a stale lane roster, an
unregistered grounding label, a masked lane pin).  Every previous instance was
fixed by making the divergence loud.  This module does that for ADR status.

Deliberately NOT a repo-wide status-vocabulary check.  The 312-file ADR corpus
carries real drift -- 27 files whose status line this module's regex cannot
parse, plus ``draft`` / ``ratified`` / ``active`` / ``accepted.`` variants.
Normalizing that is a separate, larger job (recorded in
``docs/research/adr-status-governance-2026-07-25.md``).  Asserting a closed
vocabulary here would fail on ~35 pre-existing files and get muted, which is
worse than no check.  So the scope is exactly the ADRs whose status is
*load-bearing right now*, and the parser fails loudly on any of those it cannot
read rather than skipping it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_DIR = REPO_ROOT / "docs" / "adr"
CONFIG_PATH = REPO_ROOT / "core" / "config.py"

#: ``**Status:** X`` / ``- **Status**: X`` / ``**Status**: **X**`` all appear in
#: the corpus.  Tolerant on the label, strict on capturing the remainder.
_STATUS_RE = re.compile(
    r"^[ \t]*(?:[-*][ \t]*)?\*\*Status\*{0,2}[ \t]*:?[ \t]*\*{0,2}[ \t]*:?[ \t]*(?P<value>.+?)[ \t]*$",
    re.MULTILINE,
)
_BOOL_FIELD_RE = re.compile(r"^\s*(?P<name>\w+)\s*:\s*bool\s*=\s*(?P<default>True|False)\b")
_ADR_REF_RE = re.compile(r"ADR-(\d{4})")
_RATIFY_ON_MERGE_RE = re.compile(r"ratify[- ]on[- ]merge|ratify on PR", re.IGNORECASE)


def _adr_paths() -> dict[str, Path]:
    """Map a four-digit ADR number to its file.

    Numbers are not unique in principle (``ADR-0131.3`` exists), so the key is
    the leading four digits and the first match wins deterministically by name.
    """
    out: dict[str, Path] = {}
    for path in sorted(ADR_DIR.glob("ADR-*.md")):
        match = re.match(r"ADR-(\d{4})", path.name)
        if match:
            out.setdefault(match.group(1), path)
    return out


def _status_of(path: Path) -> str | None:
    """Return the first status value in ``path``, or ``None`` if unparseable."""
    match = _STATUS_RE.search(path.read_text(encoding="utf-8"))
    if match is None:
        return None
    return match.group("value").strip().strip("*").strip()


def _is_proposed(status: str) -> bool:
    return status.lower().lstrip("*").startswith("proposed")


def _flag_adr_citations() -> dict[str, tuple[str, frozenset[str]]]:
    """Derive ``flag -> (default, cited ADR numbers)`` from ``core/config.py``.

    Derived, never restated.  A hand-copied mapping here would be the very
    defect ADR-0256's own arc fixed in ``workbench/api.py``: a second copy of a
    closed set that falls behind the original in silence.  A flag's comment
    block citing ``ADR-NNNN`` is read as a claim that the ADR governs the flag.
    """
    lines = CONFIG_PATH.read_text(encoding="utf-8").splitlines()
    out: dict[str, tuple[str, frozenset[str]]] = {}
    for index, line in enumerate(lines):
        field = _BOOL_FIELD_RE.match(line)
        if field is None:
            continue
        comment: list[str] = []
        cursor = index - 1
        while cursor >= 0:
            stripped = lines[cursor].strip()
            if stripped.startswith("#"):
                comment.append(stripped)
            elif not stripped and not comment:
                pass  # blank lines before the block start are skipped
            else:
                break
            cursor -= 1
        cited = frozenset(_ADR_REF_RE.findall("\n".join(comment)))
        out[field.group("name")] = (field.group("default"), cited)
    return out


def test_config_flag_parse_is_not_vacuous() -> None:
    """Guard the derivation itself.

    If ``core/config.py`` is reformatted such that the field regex stops
    matching, every downstream assertion would pass on an empty set and this
    module would go quietly blind -- silence reading as success, which is the
    failure mode it exists to prevent.
    """
    flags = _flag_adr_citations()
    assert len(flags) >= 25, f"expected the runtime config's bool flags; parsed only {len(flags)}"
    assert any(
        default == "True" for default, _ in flags.values()
    ), "no default-True flag parsed — the field regex has drifted from core/config.py"
    assert any(
        cited for _, cited in flags.values()
    ), "no flag cites an ADR — the comment-block walker has drifted"


@pytest.mark.parametrize(
    ("flag", "adr"),
    sorted(
        (flag, adr)
        for flag, (default, cited) in _flag_adr_citations().items()
        if default == "True"
        for adr in cited
    ),
)
def test_default_on_flag_is_not_governed_by_a_proposed_adr(flag: str, adr: str) -> None:
    """A flag that is ON by default is serving live traffic.

    The ADR that governs it therefore records a decision already in force.
    Leaving it ``Proposed`` makes the governance record assert something false
    about the running system -- exactly the asymmetry ADR-0256's arc found in
    ``workbench/api.py``, where the honest path degraded and the stale copy
    lied.

    If this fails because a flag's comment cites an ADR only as background
    rather than as its governing decision, move the citation into prose outside
    the flag's comment block.  Do not weaken the assertion.
    """
    paths = _adr_paths()
    assert adr in paths, f"{flag} cites ADR-{adr}, which does not exist in docs/adr/"

    status = _status_of(paths[adr])
    assert status is not None, (
        f"ADR-{adr} governs default-on flag {flag!r} but its status line is unparseable; "
        "a load-bearing ADR must declare a readable status"
    )
    assert not _is_proposed(status), (
        f"{flag} defaults to True (live serving) but ADR-{adr} is still {status!r}. "
        "Either stamp the ADR with the decision that put the flag on, or turn the flag off."
    )


@pytest.mark.parametrize("adr_path", sorted(ADR_DIR.glob("ADR-*.md")), ids=lambda p: p.name)
def test_ratify_on_merge_predicate_is_discharged(adr_path: Path) -> None:
    """An ADR whose status says "ratify on merge" cannot be merged AND Proposed.

    ADR-0254 (``ratify on PR #103 merge``) and ADR-0256 (``ratify-on-merge``)
    both sat ``Proposed`` after the merges that were supposed to ratify them.
    The predicate is self-discharging: the file being present on ``main`` IS
    the merge having happened, so the two states are contradictory by
    construction and need no external bookkeeping to detect.
    """
    status = _status_of(adr_path)
    if status is None or not _is_proposed(status):
        return
    assert not _RATIFY_ON_MERGE_RE.search(status), (
        f"{adr_path.name} is on main and still {status!r}. Its own status line makes the "
        "merge the ratifying act, so the merge already discharged it — stamp it Accepted "
        "and record which merge did so."
    )
