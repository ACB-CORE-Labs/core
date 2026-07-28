"""G-23 — `DOMAIN_PACKS` and the pack manifests state one fact in two places.

**How this was found.** An external assessment proposed collapsing the
pack/domain machinery, reasoning from a directory listing. Every specific it
gave was wrong — ``core/protocol/`` is the trace protocol, not governance;
``core/capability`` is reporting surfaces; ``packs/domain_contract.py`` says of
itself *"intentionally read-only … does not promote capability status."* But it
pointed at the right seam, and reading the code there found a real one.

**The seam.** ``core/capability/domains.py`` declares ``DOMAIN_PACKS`` — the
domain→pack membership the capability ledger reasons over. Each pack's
``packs/data/<pack>/manifest.json`` independently declares ``domain_id``. Two
statements of one fact, and only one of the two directions is checked:

* ``domain_contract_predicates.py`` **P3** validates ``domain_id`` → *a known
  ledger domain*. It is the only binding check that exists.
* Nothing validates ``DOMAIN_PACKS`` → *the manifest agrees*.

**P3 passes vacuously on a manifest with no ``domain_id`` at all** — the same
shape as its own ``test_pack_without_contract_reports_absent``. So a pack that
``DOMAIN_PACKS`` places in a domain, but whose manifest never says so, is
invisible to every check in the repository. Measured 2026-07-28: **7 of 9 bound,
0 contradictory, 2 absent** — ``en_core_cognition_v1`` and ``en_core_meta_v1``,
both placed in ``philosophy_theology``, which is one of the four bands queued to
earn a SERVE license behind R-8. The domain whose license is about to be earned
is the one whose binding exists in only one place.

**And the existing tests could not have caught it.**
``tests/test_domain_contract_predicates.py`` exercises P1–P9 entirely against
synthetic ``tmp_path`` manifests — never against the real nine — and is itself
in no curated suite. A predicate proven correct on fabricated input, never run
on the real input, is this arc's defect class stated precisely: *its success
state and "it never ran here" are indistinguishable.*

**What this pin does not do.** It does not add ``domain_id`` to the two
manifests. Whether ``en_core_cognition_v1`` is *a philosophy_theology domain
pack* or merely *grouped under that domain for ledger accounting* is a
ratification-adjacent content question, not an engineering one, and it is
routed to R-8 / PR-14 where that band's license is decided. This pin freezes
the state, fails on growth, and enforces both directions — so the gap is
visible and cannot widen while the decision is pending.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

_ROOT = Path(__file__).resolve().parents[1]
_DOMAINS_PY = _ROOT / "core" / "capability" / "domains.py"
_PACK_DATA = _ROOT / "packs" / "data"

#: Packs that ``DOMAIN_PACKS`` places in a domain whose manifest declares no
#: ``domain_id``. This list may only SHRINK. A pack leaves it by gaining the
#: field, not by being deleted from here.
UNBOUND_BASELINE: frozenset[str] = frozenset(
    {
        "en_core_cognition_v1",
        "en_core_meta_v1",
    }
)


def _domain_packs() -> dict[str, tuple[str, ...]]:
    """Read ``DOMAIN_PACKS`` without importing the package.

    ``core.capability`` imports ``chat`` imports ``generate`` imports numpy, so
    a plain import drags the whole runtime in to read one dict. Executing the
    module body is safe here: ``domains.py`` is pure data with no imports of
    its own beyond ``__future__``.
    """
    namespace: dict[str, Any] = {}
    source = _DOMAINS_PY.read_text(encoding="utf-8")
    exec(compile(ast.parse(source), str(_DOMAINS_PY), "exec"), namespace)  # noqa: S102
    packs = namespace["DOMAIN_PACKS"]
    assert isinstance(packs, dict), "DOMAIN_PACKS is not a dict"
    return packs


def _manifest_domain_id(pack: str) -> str | None:
    path = _PACK_DATA / pack / "manifest.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8")).get("domain_id")


def test_parse_is_not_vacuous() -> None:
    """A parse that silently matched nothing would make every pin below pass.

    That failure mode (N-1) has produced three false conclusions in this repo,
    so it is asserted rather than assumed.
    """
    packs = _domain_packs()
    members = [p for members in packs.values() for p in members]
    assert len(packs) >= 5, f"parsed only {len(packs)} domains from DOMAIN_PACKS"
    assert len(members) >= 9, f"parsed only {len(members)} pack memberships"
    assert list(_PACK_DATA.glob("*/manifest.json")), "no pack manifests found on disk"


def test_every_declared_pack_has_a_manifest() -> None:
    """``DOMAIN_PACKS`` may not name a pack that does not exist on disk."""
    missing = sorted(
        pack
        for members in _domain_packs().values()
        for pack in members
        if not (_PACK_DATA / pack / "manifest.json").exists()
    )
    assert not missing, (
        "DOMAIN_PACKS names packs with no manifest under packs/data: " f"{missing}"
    )


def test_manifest_domain_id_agrees_with_domain_packs() -> None:
    """The forward direction P3 does not check: the table must match the pack.

    A *contradiction* is always a failure. An *absence* is a failure unless the
    pack is in ``UNBOUND_BASELINE`` — which is a recorded gap with a named
    owner (R-8 / PR-14), not a default.
    """
    contradictions: list[str] = []
    undeclared_absences: list[str] = []

    for domain, members in _domain_packs().items():
        for pack in members:
            declared = _manifest_domain_id(pack)
            if declared is None:
                if pack not in UNBOUND_BASELINE:
                    undeclared_absences.append(f"{pack} (DOMAIN_PACKS: {domain})")
            elif declared != domain:
                contradictions.append(
                    f"{pack}: manifest says {declared!r}, DOMAIN_PACKS says {domain!r}"
                )

    assert not contradictions, (
        "pack manifests contradict DOMAIN_PACKS — one of the two is wrong and "
        "the capability ledger reasons over the second:\n  "
        + "\n  ".join(contradictions)
    )
    assert not undeclared_absences, (
        "these packs are placed in a domain by DOMAIN_PACKS and declare no "
        "domain_id, so P3 passes vacuously on them. Add domain_id to the "
        "manifest, or add the pack to UNBOUND_BASELINE with the reason in your "
        "commit message:\n  " + "\n  ".join(undeclared_absences)
    )


def test_no_manifest_claims_a_domain_the_table_does_not_grant() -> None:
    """The reverse direction: a pack may not self-assign a ledger domain.

    Measured clean at 2026-07-28 across all 30 packs under ``packs/data``. It is
    pinned because it is the direction a *content* edit would break — a new pack
    manifest copying ``domain_id`` from a sibling is the obvious mistake, and it
    would silently widen a domain the ledger licenses.
    """
    granted = {
        pack: domain for domain, members in _domain_packs().items() for pack in members
    }
    offenders: list[str] = []
    for manifest in sorted(_PACK_DATA.glob("*/manifest.json")):
        declared = json.loads(manifest.read_text(encoding="utf-8")).get("domain_id")
        if declared is None:
            continue
        pack = manifest.parent.name
        if pack not in granted:
            offenders.append(f"{pack}: claims {declared!r}, not in DOMAIN_PACKS at all")
        elif granted[pack] != declared:
            offenders.append(
                f"{pack}: claims {declared!r}, DOMAIN_PACKS grants {granted[pack]!r}"
            )
    assert not offenders, (
        "pack manifests claim ledger domains DOMAIN_PACKS does not grant:\n  "
        + "\n  ".join(offenders)
    )


def test_unbound_baseline_has_no_stale_entries() -> None:
    """Both directions — a pack that gains ``domain_id`` must leave the list.

    Same discipline as the suite-membership and reachability ratchets, for the
    same reason: a baseline that keeps entries it no longer needs stops being a
    measurement and becomes a story about one. That discipline has caught this
    file's author twice.
    """
    declared_packs = {
        pack for members in _domain_packs().values() for pack in members
    }

    vanished = sorted(p for p in UNBOUND_BASELINE if p not in declared_packs)
    assert not vanished, (
        f"UNBOUND_BASELINE names packs DOMAIN_PACKS no longer places: {vanished}"
    )

    now_bound = sorted(p for p in UNBOUND_BASELINE if _manifest_domain_id(p) is not None)
    assert not now_bound, (
        "these packs now declare domain_id (good) but are still listed as "
        f"unbound — remove them from UNBOUND_BASELINE: {now_bound}"
    )


def test_recorded_gap_matches_the_measurement() -> None:
    """Pin the number so the gap moving is a reviewed decision, not a drift.

    2 of 9 at 2026-07-28. Shrinking it is the point, and it shrinks by a
    ratification-adjacent content decision (R-8 / PR-14), not by an edit here.
    """
    assert len(UNBOUND_BASELINE) <= 2, (
        f"unbound domain packs grew to {len(UNBOUND_BASELINE)} (was 2). The "
        "ratchet only turns one way."
    )
