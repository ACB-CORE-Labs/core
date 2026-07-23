"""discovery-yield-per-served-turn telemetry (2026-07-23 directive).

Each test includes a ``*_bites`` mutation variant where the predicate
could otherwise pass vacuously (CLAUDE.md schema-as-proof discipline).
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from core.cli import main
from engine_state import EngineStateStore
from teaching.discovery import DiscoveryCandidate
from teaching.discovery_yield import DiscoveryYield, compute_discovery_yield


def _candidate(candidate_id: str) -> DiscoveryCandidate:
    return DiscoveryCandidate(
        candidate_id=candidate_id,
        proposed_chain={},
        trigger="would_have_grounded",
        source_turn_trace="deadbeef",
        pack_consistent=True,
        boundary_clean=True,
    )


def _write_gen(
    store: EngineStateStore,
    *,
    turn_count: int,
    turn_count_baseline: int | None,
    candidates: list[DiscoveryCandidate],
) -> None:
    gen_num, gen_dir = store.begin_generation()
    gs = EngineStateStore(gen_dir)
    gs.save_recognizers([])
    gs.save_discovery_candidates(candidates)
    gs.save_manifest(turn_count, turn_count_baseline=turn_count_baseline)
    store.commit_generation(gen_num, keep=1)


# ---------------------------------------------------------------------------
# Gate: no baseline stamped -> fail-closed None, never a fabricated denominator
# ---------------------------------------------------------------------------

def test_no_baseline_returns_none(tmp_path: Path) -> None:
    store = EngineStateStore(tmp_path)
    _write_gen(store, turn_count=100, turn_count_baseline=None, candidates=[])
    assert compute_discovery_yield(store) is None


def test_no_baseline_returns_none_bites(tmp_path: Path) -> None:
    """A store WITH a baseline must not also return None."""
    store = EngineStateStore(tmp_path)
    _write_gen(store, turn_count=100, turn_count_baseline=100, candidates=[])
    assert compute_discovery_yield(store) is not None


def test_no_committed_generation_returns_none(tmp_path: Path) -> None:
    store = EngineStateStore(tmp_path)
    assert compute_discovery_yield(store) is None


# ---------------------------------------------------------------------------
# Gate: served_turns_since_reset = turn_count - baseline
# ---------------------------------------------------------------------------

def test_served_turns_since_reset_is_delta(tmp_path: Path) -> None:
    store = EngineStateStore(tmp_path)
    _write_gen(store, turn_count=14995, turn_count_baseline=14990, candidates=[])
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.served_turns_since_reset == 5


def test_served_turns_since_reset_is_delta_bites(tmp_path: Path) -> None:
    """Must be the DELTA, not the raw turn_count."""
    store = EngineStateStore(tmp_path)
    _write_gen(store, turn_count=14995, turn_count_baseline=14990, candidates=[])
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.served_turns_since_reset != result.turn_count


# ---------------------------------------------------------------------------
# Gate: yield_rate = candidates_since_reset / served_turns_since_reset
# ---------------------------------------------------------------------------

def test_yield_rate_divides_candidates_by_served_turns(tmp_path: Path) -> None:
    store = EngineStateStore(tmp_path)
    _write_gen(
        store,
        turn_count=14994,
        turn_count_baseline=14990,
        candidates=[_candidate("a"), _candidate("b")],
    )
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.candidates_since_reset == 2
    assert result.served_turns_since_reset == 4
    assert result.yield_rate == 0.5


def test_yield_rate_divides_candidates_by_served_turns_bites(tmp_path: Path) -> None:
    """Must not be the reciprocal or the raw candidate count."""
    store = EngineStateStore(tmp_path)
    _write_gen(
        store,
        turn_count=14994,
        turn_count_baseline=14990,
        candidates=[_candidate("a"), _candidate("b")],
    )
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.yield_rate != 2.0


# ---------------------------------------------------------------------------
# Gate: zero served turns since reset -> yield_rate is None, not a ZeroDivisionError
# ---------------------------------------------------------------------------

def test_zero_served_turns_yields_none_rate_not_division_error(tmp_path: Path) -> None:
    store = EngineStateStore(tmp_path)
    _write_gen(store, turn_count=14990, turn_count_baseline=14990, candidates=[])
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.served_turns_since_reset == 0
    assert result.yield_rate is None


def test_zero_served_turns_yields_none_rate_not_division_error_bites(
    tmp_path: Path,
) -> None:
    """A store WITH served turns must produce a numeric rate, not None."""
    store = EngineStateStore(tmp_path)
    _write_gen(
        store,
        turn_count=14991,
        turn_count_baseline=14990,
        candidates=[_candidate("a")],
    )
    result = compute_discovery_yield(store)
    assert result is not None
    assert result.yield_rate is not None


# ---------------------------------------------------------------------------
# Gate: as_dict is a plain, JSON-safe mapping
# ---------------------------------------------------------------------------

def test_as_dict_round_trips_json_safe_types() -> None:
    dy = DiscoveryYield(
        turn_count=14994,
        turn_count_baseline=14990,
        served_turns_since_reset=4,
        candidates_since_reset=2,
        yield_rate=0.5,
    )
    payload = dy.as_dict()
    assert payload == {
        "turn_count": 14994,
        "turn_count_baseline": 14990,
        "served_turns_since_reset": 4,
        "candidates_since_reset": 2,
        "yield_rate": 0.5,
    }


# ---------------------------------------------------------------------------
# Gate: `core teaching discovery-yield` CLI surface
# ---------------------------------------------------------------------------

def test_cli_fails_closed_without_baseline(
    capsys: pytest.CaptureFixture[str],
) -> None:
    # conftest's autouse `_isolate_engine_state_default` already points the
    # bare-default store at a fresh per-test dir; nothing committed yet.
    exit_code = main(["teaching", "discovery-yield"])
    assert exit_code == 1
    err = capsys.readouterr().err
    assert "turn_count_baseline" in err


def test_cli_fails_closed_without_baseline_bites() -> None:
    """A store WITH a baseline must not also exit 1."""
    _write_gen(
        EngineStateStore(),
        turn_count=14990,
        turn_count_baseline=14990,
        candidates=[],
    )
    exit_code = main(["teaching", "discovery-yield"])
    assert exit_code == 0


def test_cli_json_emits_the_computed_snapshot(
    capsys: pytest.CaptureFixture[str],
) -> None:
    _write_gen(
        EngineStateStore(),
        turn_count=14992,
        turn_count_baseline=14990,
        candidates=[_candidate("a")],
    )
    exit_code = main(["teaching", "discovery-yield", "--json"])
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == {
        "turn_count": 14992,
        "turn_count_baseline": 14990,
        "served_turns_since_reset": 2,
        "candidates_since_reset": 1,
        "yield_rate": 0.5,
    }
