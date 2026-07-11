"""DeltaStore frontier isolation (ADR-0026.1 §2.1).

Regression: ``DeltaStore.frontier`` used to return the live internal set.
A delta built with ``parents=store.frontier`` then aliased that set, so
``insert``'s frontier maintenance (``add`` + ``difference_update``) emptied
the frontier on every insert and rewrote every stored delta's parents to
``{}`` — the CRDT causal chain degenerated into all-roots. Both boundaries
must copy: ``frontier`` hands out snapshots, ``insert`` copies the delta's
parents into the event envelope.
"""

from __future__ import annotations

from core.abi import GeometricDelta
from core.epistemic_state import EpistemicState
from vault.delta_store import DeltaStore


def _delta(delta_id: str, parents: set[str]) -> GeometricDelta:
    versor = [0.0] * 32
    versor[0] = 1.0
    return GeometricDelta(
        id=delta_id,
        parents=parents,
        modality="lh_text",
        compiler_id="test_compiler_v1",
        semantic={"type": "text_token", "token": 1},
        amr_scope={"level": 0, "region_id": "root", "time_window": [0.0, 0.0]},
        delta_versor=versor,
        inverse_ref=None,
        provenance={"source": "test", "time": 0.0, "adr_refs": ["ADR-0026"], "hash": delta_id},
        epistemic=EpistemicState.UNVERIFIED_POSSIBLE,
    )


def test_frontier_returns_snapshot_not_live_set() -> None:
    store = DeltaStore()
    snapshot = store.frontier
    assert store.insert(_delta("sha256:d1", set()), author="test")
    assert snapshot == set(), "pre-insert snapshot must not see later mutations"
    assert store.frontier == {"sha256:d1"}


def test_insert_from_live_frontier_keeps_causal_chain() -> None:
    """The exact aliasing pattern that used to sever the chain: build each
    delta's parents directly from ``store.frontier`` and insert in sequence."""
    store = DeltaStore()
    ids = ["sha256:d1", "sha256:d2", "sha256:d3"]
    deltas = []
    for delta_id in ids:
        delta = _delta(delta_id, store.frontier)
        deltas.append(delta)
        assert store.insert(delta, author="test")

    assert store.frontier == {"sha256:d3"}, "a linear history has exactly one head"
    assert deltas[0].parents == set()
    assert deltas[1].parents == {"sha256:d1"}, "delta parents must survive insert"
    assert deltas[2].parents == {"sha256:d2"}

    event = store.get_event("sha256:d2")
    assert event is not None
    assert event.parents == {"sha256:d1"}


def test_insert_copies_delta_parents_into_event() -> None:
    store = DeltaStore()
    parents: set[str] = set()
    delta = _delta("sha256:root", parents)
    assert store.insert(delta, author="test")

    event = store.get_event("sha256:root")
    assert event is not None
    parents.add("sha256:injected-later")
    assert event.parents == set(), "event parents must be isolated from caller mutation"
