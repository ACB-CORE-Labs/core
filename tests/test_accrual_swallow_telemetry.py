"""PR-9 (H-11) — the defensive backstops stop being invisible.

Three broad ``except`` guards on the turn spine are deliberate and stay:
accrual is additive and must never crash a turn; a pack/catalog failure must
not take down the logos authority; a probe failure must not affect the served
surface. Narrowing them would trade silent failure for served-surface failure,
which is the worse trade.

What was wrong is that each wrote a value indistinguishable from the healthy
case. A raising read→realize→determine chain left the same ``None`` accrual a
quiet turn leaves. A logos decision that raised looked exactly like a turn
where logos was never consulted. A crashed geometric probe recorded the same
empty neighborhood as a probe that ran and found nothing — in the block whose
whole job is producing the data that prices the anti-unification roadmap.

These pins hold the guards open *and* visible: behavior byte-identical,
cause recorded. INV-34's "failures are typed, never silent" applied to the
backstops that were exempt from it.
"""

from __future__ import annotations

import pytest

from chat.runtime import ChatRuntime
from core.cognition import CognitiveTurnPipeline
from core.cognition.result import CognitiveTurnResult


@pytest.fixture()
def runtime() -> ChatRuntime:
    return ChatRuntime()


# ---------------------------------------------------------------------------
# Accrual guard (chat/runtime.py::_accrue_in_turn)
# ---------------------------------------------------------------------------


def test_healthy_session_reports_no_swallows(runtime: ChatRuntime) -> None:
    swallows, last_error = runtime.accrual_swallow_telemetry()
    assert swallows == 0
    assert last_error is None


def test_accrual_guard_counts_and_names_what_it_absorbs(
    runtime: ChatRuntime, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A raising chain is absorbed exactly as before — and is now attributable."""
    runtime._context = object()  # get past the early return

    import generate.meaning_graph.reader as reader_mod

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("reader exploded")

    monkeypatch.setattr(reader_mod, "comprehend", _boom)

    runtime._accrue_in_turn("light reveals truth")

    swallows, last_error = runtime.accrual_swallow_telemetry()
    assert swallows == 1, "the guard fired but did not count itself"
    assert last_error is not None and "reader exploded" in last_error, (
        "the guard absorbed an exception without naming it"
    )


def test_accrual_guard_behavior_is_unchanged_by_the_telemetry(
    runtime: ChatRuntime, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The backstop still yields a None accrual — consumers see no difference.

    ``_maybe_surface_determination`` returns the response untouched on a None
    accrual, so this is the property that makes PR-9 additive by construction.
    """
    runtime._context = object()

    import generate.meaning_graph.reader as reader_mod

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("still exploding")

    monkeypatch.setattr(reader_mod, "comprehend", _boom)
    runtime._accrue_in_turn("light reveals truth")

    assert runtime.last_turn_accrual() is None


def test_a_quiet_turn_is_distinguishable_from_a_swallowed_one(
    runtime: ChatRuntime,
) -> None:
    """The whole point: two causes of a None accrual, now told apart."""
    runtime._accrue_in_turn("")  # nothing to accrue — not a failure

    assert runtime.last_turn_accrual() is None
    swallows, _ = runtime.accrual_swallow_telemetry()
    assert swallows == 0, "an empty turn must not read as a swallowed exception"


# ---------------------------------------------------------------------------
# Pipeline guards (core/cognition/pipeline.py)
# ---------------------------------------------------------------------------


def test_result_carries_a_logos_error_field_defaulting_empty() -> None:
    """An un-consulted logos path is "" — only a raise fills it."""
    import dataclasses

    field = {f.name: f for f in dataclasses.fields(CognitiveTurnResult)}["logos_error"]
    assert field.default == ""


def test_logos_guard_records_the_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    """A logos decision that raises is recorded, not silently treated as absent.

    Without this, ``logos_decision_kind == ""`` meant either "not consulted" or
    "raised" — and a constraint failing to block a certified answer left no
    trace anywhere. The pipeline imports the authority *inside* its guarded
    block, so patching the module attribute is what the running turn resolves.
    """
    from generate.observed_he_morph_v0 import authority as logos_mod

    def _boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("catalog unavailable")

    monkeypatch.setattr(logos_mod, "evaluate_logos_on_text", _boom)

    pipeline = CognitiveTurnPipeline(runtime=ChatRuntime())
    result = pipeline.run("what is light?")

    # The turn completed — the backstop did its job, exactly as before.
    assert isinstance(result.surface, str)
    # And it named the cause instead of being indistinguishable from silence.
    assert "catalog unavailable" in result.logos_error
    assert result.logos_decision_kind == ""


def test_oov_probe_context_exposes_its_failure_channels() -> None:
    """When the probe runs, its telemetry carries the error channels.

    A crashed probe and an empty neighborhood must not serialize identically —
    the roadmap this block feeds is only trustworthy if the two are distinct.
    """
    pipeline = CognitiveTurnPipeline(runtime=ChatRuntime())
    result = pipeline.run("what is zzqxwv?")  # OOV-shaped input

    ctx = result.oov_geometric_context
    if ctx is not None and "geometric_probe_performed" in ctx:
        assert "probe_error" in ctx, "probe telemetry lost its failure channel"
        assert "neighbor_scan_errors" in ctx
        # A healthy probe reports no error and an integer scan-failure count.
        assert isinstance(ctx["neighbor_scan_errors"], int)
        if ctx["geometric_probe_performed"]:
            assert ctx["probe_error"] == ""
