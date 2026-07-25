"""The domain-keyed ADR index must not rot into a page of dead links.

`docs/adr/INDEX-by-domain.md` exists because the corpus is at 312 files under
flat sequential numbering, and sequence records *when* a decision was made and
nothing about *what it governs*. An index whose links have decayed is worse
than no index, because it converts "I should grep" into "I already checked".

Deliberately narrow: this pins that every ADR the index names exists, and that
the index stays honest about being partial. It does not assert coverage of all
312 — the index says so itself, and a test demanding completeness would only
push someone to satisfy it with unread rows.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest


ADR_DIR = Path(__file__).resolve().parents[1] / "docs" / "adr"
INDEX = ADR_DIR / "INDEX-by-domain.md"


@pytest.fixture(scope="module")
def index_text() -> str:
    return INDEX.read_text(encoding="utf-8")


def test_index_exists(index_text: str) -> None:
    assert index_text.strip(), "the ADR domain index is empty"


def test_every_indexed_adr_resolves(index_text: str) -> None:
    """A dead link means an ADR was renamed and the index was not touched."""
    links = re.findall(r"\]\(\./([^)]+)\)", index_text)
    assert links, "no relative links parsed — the index format changed"
    dead = sorted({link for link in links if not (ADR_DIR / link).exists()})
    assert dead == [], f"index points at ADRs that do not exist: {dead}"


def test_index_covers_the_live_serving_arc(index_text: str) -> None:
    """The domains a next-arc session actually queries.

    These are the ADRs behind capabilities that are ON in production: if one is
    minted-and-forgotten out of the index, the index has stopped being the
    thing you can trust for the live surface, which is its whole job.
    """
    required = [
        "ADR-0256",  # deduction serving, earned license, flag ratified ON
        "ADR-0262",  # curriculum-grounded serving
        "ADR-0263",  # ratified-ledger bridge
        "ADR-0255",  # discovery-yield telemetry
        "ADR-0142",  # epistemic-state taxonomy
        "ADR-0162",  # workbench design system (the enum/badge contract)
        "ADR-0251",  # reader-arc prohibition on per-case pattern growth
    ]
    missing = [adr for adr in required if adr not in index_text]
    assert missing == [], f"live-arc ADRs absent from the domain index: {missing}"


def test_index_declares_its_own_partiality(index_text: str) -> None:
    """The honesty property. An index that silently claims completeness is a
    trap; this one states its scope, and that statement is load-bearing."""
    assert "not a complete index" in index_text.lower()


def test_all_six_deduction_bands_are_indexed(index_text: str) -> None:
    """v1b through v6-EX. The band cascade is the thing most likely to grow
    without the index following, because each new band is one more ADR."""
    for adr in ("ADR-0257", "ADR-0258", "ADR-0259", "ADR-0260", "ADR-0261"):
        assert adr in index_text, f"{adr} (a shipped band) is not indexed"
