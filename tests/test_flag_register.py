"""PR-5 / G-8 / H-6 — the flag register names exactly the flags that exist.

`RuntimeConfig` carries 32 boolean fields and, until `docs/specs/flag_register.md`,
nothing in the repository stated that set. Two independent counts of it differed by
eleven — the assessment said "seventeen capability flags," N-7 measured 28 default-off
plus 4 default-on — and neither count was wrong about what it looked at. They were
counting different things because nothing declared what the set *was*.

**Why a register needs a pin at all.** A document listing 32 flags is a 33rd copy of
the flag set, and a copy that nothing checks is exactly the artifact this arc keeps
finding: it looks like a source of truth right up until it silently falls behind the
thing it describes. `CLAIMS.md` published a superseded digest for two days that way
(G-22); `DOMAIN_PACKS` and the pack manifests drifted that way (G-23). A register
without this pin would be the third instance, shipped by the arc that catalogued the
first two.

So the check runs in **both directions**, which is the only version that means
anything:

  * a flag added to ``core/config.py`` and not to the register **fails** — this is the
    direction that stops the register decaying into a historical document;
  * a register row whose flag no longer exists **fails** — this is the direction that
    stops it accumulating entries nobody can act on.

Neither direction is the interesting one on its own. A one-directional version would
have passed happily through both of the failures it exists to prevent.
"""

from __future__ import annotations

import re
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CONFIG = _ROOT / "core" / "config.py"
_REGISTER = _ROOT / "docs" / "specs" / "flag_register.md"

#: ``name: bool = True|False`` in the ``RuntimeConfig`` dataclass body.
_FIELD_RE = re.compile(r"^\s*(?P<name>\w+)\s*:\s*bool\s*=\s*(?P<default>True|False)\b")

#: A register row whose FIRST cell is a lone backticked lower_snake_case name.
#: Lower-case is required on purpose: the declared-table index in §5 lists tables
#: (``TEST_SUITES``, ``GATE_SUITES``, ``CONTINUOUS_LIFE_CONFIG_FLAGS``) in the same
#: shape, and they are not `RuntimeConfig` flags. §5 is also cut off before parsing —
#: two guards, because a parser that silently over-matches would turn this pin into a
#: source of false failures, and a pin people learn to distrust is worse than none.
_ROW_RE = re.compile(r"^\|\s*`(?P<name>[a-z][a-z0-9_]*)`\s*\|", re.MULTILINE)

#: The section that stops being about individual flags.
_INDEX_HEADING = "## 5."


def _config_flags() -> dict[str, str]:
    """``flag -> "True"|"False"``, derived from the source. Never restated."""
    out: dict[str, str] = {}
    for line in _CONFIG.read_text(encoding="utf-8").splitlines():
        match = _FIELD_RE.match(line)
        if match:
            out[match.group("name")] = match.group("default")
    return out


def _register_text() -> str:
    text = _REGISTER.read_text(encoding="utf-8")
    cut = text.find(_INDEX_HEADING)
    return text[:cut] if cut != -1 else text


def _register_flags() -> set[str]:
    return {m.group("name") for m in _ROW_RE.finditer(_register_text())}


def test_the_register_exists() -> None:
    assert _REGISTER.exists(), (
        "docs/specs/flag_register.md is missing — G-8 reopens the moment it does"
    )


def test_neither_parse_is_vacuous() -> None:
    """Guard both derivations before asserting anything about their relationship.

    If either side parsed to an empty (or tiny) set, the equality assertions below
    would pass on nothing and this module would go quietly blind. Silence reading as
    success is the exact failure mode the register was written to expose, so it is
    asserted here rather than assumed.
    """
    config = _config_flags()
    register = _register_flags()
    assert len(config) >= 30, (
        f"parsed only {len(config)} bool fields from core/config.py — the field "
        "regex has drifted from the dataclass"
    )
    assert len(register) >= 30, (
        f"parsed only {len(register)} flag rows from the register — the table "
        "format changed and this pin can no longer read it"
    )
    assert any(d == "True" for d in config.values()), (
        "no default-True flag parsed — the field regex has drifted"
    )
    assert _INDEX_HEADING in _REGISTER.read_text(encoding="utf-8"), (
        "the declared-table index heading moved; the parser's cut-off is now wrong "
        "and §5's table names would be read as flags"
    )


def test_every_flag_is_registered() -> None:
    """A new flag cannot land unregistered.

    This is the direction that keeps the register alive. If it fails on a flag you
    just added: add a row with its class, its governing ADR (or an honest "none"),
    and **what evidence would flip it**. The last column is the one that matters —
    a flag whose criterion is unrecorded is an open question wearing a default.
    """
    unregistered = sorted(set(_config_flags()) - _register_flags())
    assert not unregistered, (
        "these RuntimeConfig booleans are not in docs/specs/flag_register.md: "
        f"{unregistered}"
    )


def test_no_register_row_outlives_its_flag() -> None:
    """The other direction: a removed flag must leave the register.

    Same discipline as the suite-membership, reachability and domain-pack ratchets.
    A register that keeps rows it no longer needs stops being a measurement and
    becomes a story about one.
    """
    orphaned = sorted(_register_flags() - set(_config_flags()))
    assert not orphaned, (
        "the register describes flags that no longer exist in core/config.py: "
        f"{orphaned}"
    )


def test_the_recorded_shape_of_the_set_matches() -> None:
    """Pin the counts the register's prose states.

    The register opens by asserting "32 boolean fields: 28 default False, 4 default
    True." That sentence is the thing readers quote, so it is the thing most likely
    to go stale — and a stale count is how this whole register came to be needed.
    """
    config = _config_flags()
    on = sorted(f for f, d in config.items() if d == "True")
    assert len(config) == 32, (
        f"RuntimeConfig now has {len(config)} boolean fields, not 32 — update the "
        "register's opening paragraph and §1 in the same change"
    )
    assert len(on) == 4, (
        f"the default-ON surface is now {len(on)} flags, not 4: {on}. §1 of the "
        "register is a per-flag table of exactly this set and must be updated — it "
        "carries the highest justification burden in the document"
    )


def test_the_default_on_surface_is_named_in_the_register() -> None:
    """§1 tables the ON flags by name; each must actually be ON.

    The ON surface is the only part of the register where being wrong is immediately
    dangerous: a flag listed as ON that is off understates what ships, and a flag
    that is ON but absent from §1 ships unjustified.
    """
    on = {f for f, d in _config_flags().items() if d == "True"}
    section = _register_text()
    start = section.find("## 1.")
    end = section.find("## 2.")
    assert start != -1 and end != -1, "the register's §1/§2 headings moved"
    named = {m.group("name") for m in _ROW_RE.finditer(section[start:end])}
    missing = sorted(on - named)
    overclaimed = sorted(named - on)
    assert not missing, f"default-ON flags absent from the register's §1 table: {missing}"
    assert not overclaimed, (
        f"the register's §1 table names flags that are not default-ON: {overclaimed}"
    )
