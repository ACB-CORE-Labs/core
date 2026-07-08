"""Project-wide pytest configuration and fixtures.

Includes support for 3-lang depth pack requirements (he/grc via DEPTH_PACK_IDS).
"""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Register additional markers (also declared in pyproject.toml for docs)."""
    config.addinivalue_line(
        "markers",
        "requires_depth_packs: 3-lang (he/grc) depth tests require DEPTH_PACK_IDS packs "
        "to be resolvable/mounted; otherwise explicit skip with documented pack names. "
        "See 3-lang depth PropGraph unification work and plan.md.",
    )


@pytest.fixture(autouse=True)
def _enforce_depth_packs_if_marked(request: pytest.FixtureRequest) -> None:
    """If test is marked requires_depth_packs, verify at least one DEPTH_PACK can resolve a Hebrew term.
    Produces explicit skip (with pack names) rather than silent no-depth execution path.
    """
    if request.node.get_closest_marker("requires_depth_packs"):
        try:
            from chat.pack_resolver import DEPTH_PACK_IDS, resolve_entry
        except Exception as e:  # pragma: no cover - import guard
            pytest.skip(f"requires_depth_packs: pack_resolver unavailable ({e}); packs={DEPTH_PACK_IDS if 'DEPTH_PACK_IDS' in dir() else 'unknown'}")

        if not DEPTH_PACK_IDS:
            pytest.skip("requires_depth_packs: DEPTH_PACK_IDS is empty")

        # Use a known Hebrew term that the he depth packs should ground for root
        term = "אמת"
        available = False
        for pid in DEPTH_PACK_IDS:
            try:
                if resolve_entry(term, pack_ids=(pid,)) is not None:
                    available = True
                    break
            except Exception:
                continue

        if not available:
            pytest.skip(
                f"requires_depth_packs: none of DEPTH_PACK_IDS={DEPTH_PACK_IDS} "
                f"resolvable for term='{term}' (he/grc depth packs not mounted or not providing root data)"
            )
        # else: proceed to run the test fully with real depth data
