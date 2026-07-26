"""Audit-ledger R7 — the turn event reaching the sink is the POST-override one.

Spec: `docs/handoff/curriculum-license-loop-2026-07/E1-R7-ASSERTION-SPEC.md`
(invariants I1-I8, mechanisms M1-M3). Contract:
`docs/specs/runtime_contracts.md`.

`ChatRuntime.chat` seals a `TurnEvent` before the surface authority and the
canonical `trace_hash` are known. `CognitiveTurnPipeline` then back-stamps both
onto `turn_log[-1]` after `chat` returns, so the in-memory log ended up correct
while the DURABLE stream carried the pre-override record. The fix stages the
turn event as an index and flushes it at the pipeline's serve boundary.

**One spec assertion was wrong and is corrected here, not quietly dropped.**
I2's third bullet and I3 both assert on an emitted `trace_hash`. There is no such
field: `chat/telemetry.py` never serializes `TurnEvent.trace_hash`, so the sink
never carried a trace_hash, stale or otherwise. The stale-SURFACE half of the
defect is real and is what R7 repairs. See
`test_trace_hash_is_not_in_the_wire_format_at_all`, which pins the absence so the
claim cannot be re-asserted later, and
`test_trace_hash_is_verified_by_replay_never_recomputation`, which keeps the
ruling's intent on the object that does carry it.
"""

from __future__ import annotations

import json

import pytest

from chat.runtime import ChatRuntime
from chat.telemetry import JsonlBufferSink
from core.cognition.pipeline import CognitiveTurnPipeline
from core.config import RuntimeConfig

#: The fixture that makes the override ACTUALLY fire. With the default config
#: `finalize_turn_surface` is a no-op for every input probed (36 turns, zero
#: divergences): the runtime's own surface already wins the resolver. Under
#: `realizer_grounded_authority` the grounded realizer beats it, and the sealed
#: TurnEvent genuinely disagrees with the served bytes — 24 divergences over 84
#: turns. A test built on the default config would pass while proving nothing,
#: which is exactly what the spec warned about.
_OVERRIDING_CONFIG = dict(realizer_grounded_authority=True)
_OVERRIDING_TEXT = "What is light?"


def _runtime(**config: object) -> tuple[ChatRuntime, JsonlBufferSink]:
    rt = ChatRuntime(config=RuntimeConfig(**config), no_load_state=True)  # type: ignore[arg-type]
    sink = JsonlBufferSink()
    rt.attach_telemetry_sink(sink, include_content=True)
    return rt, sink


def _turn_lines(sink: JsonlBufferSink) -> list[dict]:
    """Turn events only — reboot/correction events ride the same stream."""
    out = []
    for line in sink.lines:
        row = json.loads(line)
        if "turn" in row and "epistemic_state" in row:
            out.append(row)
    return out


# ---------------------------------------------------------------------------
# The premise: the override must actually fire, or nothing below proves anything.
# ---------------------------------------------------------------------------

def test_the_pipeline_really_does_override_the_sealed_surface() -> None:
    """Reproduces the PRE-FIX defect by bypassing the deferral wrapper.

    `_run_turn` is the turn body without `run`'s staging boundary, so calling it
    directly emits inline exactly as the code did before R7. If this ever stops
    diverging, the fixture has gone stale and every assertion below is vacuous.
    """
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    result = CognitiveTurnPipeline(runtime=rt)._run_turn(_OVERRIDING_TEXT)
    emitted = _turn_lines(sink)[-1]

    assert emitted["surface"] != result.surface, (
        "the pre-fix path must emit a STALE surface — if it does not, this "
        "fixture no longer exercises R7 and the tests below prove nothing"
    )
    # ...and the in-memory log was repaired, which is the asymmetry R7 is about.
    assert rt.turn_log[-1].surface == result.surface


# ---------------------------------------------------------------------------
# I1 — exactly once, on every path.
# ---------------------------------------------------------------------------

def test_i1_exactly_one_event_per_pipeline_turn() -> None:
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    pipe = CognitiveTurnPipeline(runtime=rt)
    pipe.run(_OVERRIDING_TEXT)
    assert len(_turn_lines(sink)) == 1, "never zero (dropped), never twice (double flush)"
    pipe.run("What is truth?")
    assert len(_turn_lines(sink)) == 2


def test_i1_flush_is_idempotent() -> None:
    """A caller that flushes twice must not duplicate the record."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    before = len(_turn_lines(sink))
    rt.flush_deferred_turn_event()
    rt.flush_deferred_turn_event()
    assert len(_turn_lines(sink)) == before


def test_i1_refusal_stub_path_also_emits_exactly_once() -> None:
    """Both emission sites are in scope — the main path and the refusal stub."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt).run("zzz")
    lines = _turn_lines(sink)
    assert len(lines) == 1


# ---------------------------------------------------------------------------
# I2 — the emitted event is the POST-override event.
# ---------------------------------------------------------------------------

def test_i2_emitted_surface_is_the_served_surface() -> None:
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    result = CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    emitted = _turn_lines(sink)[-1]
    assert emitted["surface"] == result.surface
    assert emitted["surface"] == rt.turn_log[-1].surface


def test_i2_emitted_articulation_surface_is_the_resolved_one() -> None:
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    result = CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    emitted = _turn_lines(sink)[-1]
    assert emitted["articulation_surface"] == result.articulation_surface
    assert emitted["articulation_surface"] == rt.turn_log[-1].articulation_surface


def test_i2_emitted_line_equals_the_repaired_log_entry_byte_for_byte() -> None:
    """The strongest form: the stream carries the log entry, not a copy of an
    earlier state of it (M1 — stage an index, not the event)."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    expected = rt._format_turn_event(rt.turn_log[-1])
    assert sink.lines[-1] == expected


# ---------------------------------------------------------------------------
# I3 — trace_hash: the spec was wrong, and the correction is pinned.
# ---------------------------------------------------------------------------

def test_trace_hash_is_not_in_the_wire_format_at_all() -> None:
    """CORRECTION to the E1 spec (I2 bullet 3, I3).

    The spec asserted the sink held a stale `trace_hash`. It never held one:
    `chat/telemetry.py` does not serialize the field. So R7 repairs the SURFACE
    only, and any future claim that the stream carries a trace_hash has to
    change this test first.
    """
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    emitted = _turn_lines(sink)[-1]
    assert "trace_hash" not in emitted
    # The field exists on the object and IS back-stamped — it just never ships.
    assert rt.turn_log[-1].trace_hash != ""


def test_trace_hash_is_verified_by_replay_never_recomputation() -> None:
    """Keeps the ruling's intent on the object that carries the hash.

    The contract states recomputation from a turn record is unsupported and
    correct to be so (`TurnEvent` carries no `hash_surface`). So this compares a
    fresh pipeline REPLAY of the same input, never a rebuild from emitted fields.
    """
    rt_a, _ = _runtime(**_OVERRIDING_CONFIG)
    result_a = CognitiveTurnPipeline(runtime=rt_a).run(_OVERRIDING_TEXT)
    rt_b, _ = _runtime(**_OVERRIDING_CONFIG)
    result_b = CognitiveTurnPipeline(runtime=rt_b).run(_OVERRIDING_TEXT)

    assert result_a.trace_hash == result_b.trace_hash != ""
    assert rt_a.turn_log[-1].trace_hash == result_a.trace_hash


def test_emitted_line_is_deterministic_across_replays() -> None:
    rt_a, sink_a = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt_a).run(_OVERRIDING_TEXT)
    rt_b, sink_b = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt_b).run(_OVERRIDING_TEXT)
    assert sink_a.lines == sink_b.lines


# ---------------------------------------------------------------------------
# I4 — no pipeline, no change.
# ---------------------------------------------------------------------------

def test_i4_direct_runtime_emits_inline_at_the_same_moment() -> None:
    """A runtime used directly (the eval and demo paths) must be byte-identical
    to before R7, INCLUDING emission timing — the line exists the instant
    `chat()` returns, with no flush."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    rt.chat(_OVERRIDING_TEXT)
    assert len(_turn_lines(sink)) == 1, "direct chat must not defer"
    assert rt._staged_turn_index is None
    assert rt._deferred_turn_emission is False
    emitted = _turn_lines(sink)[-1]
    assert emitted["surface"] == rt.turn_log[-1].surface


def test_i4_direct_runtime_content_matches_the_sealed_event() -> None:
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    rt.chat(_OVERRIDING_TEXT)
    assert sink.lines[-1] == rt._format_turn_event(rt.turn_log[-1])


# ---------------------------------------------------------------------------
# I5 — exception safety. A pipeline error must not swallow a telemetry record.
# ---------------------------------------------------------------------------

def test_i5_staged_event_still_reaches_the_sink_when_the_pipeline_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Fault injected AFTER `chat()` returns, at the back-stamp itself.

    Without the `finally` this is a silently lost telemetry record — a worse
    failure than the staleness R7 fixes, because nothing reports it.
    """
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    pipe = CognitiveTurnPipeline(runtime=rt)

    def boom(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("injected fault at the serve boundary")

    monkeypatch.setattr(rt, "finalize_turn_surface", boom)
    with pytest.raises(RuntimeError, match="injected fault"):
        pipe.run(_OVERRIDING_TEXT)

    assert len(_turn_lines(sink)) == 1, "the staged event must survive the raise"
    assert rt._staged_turn_index is None
    assert rt._deferred_turn_emission is False, "deferral must not leak past the turn"


def test_i5_a_later_turn_still_emits_normally_after_a_raise(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The failure must not leave the runtime stuck in a deferring state."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    pipe = CognitiveTurnPipeline(runtime=rt)
    monkeypatch.setattr(
        rt, "finalize_turn_surface", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("x"))
    )
    with pytest.raises(RuntimeError):
        pipe.run(_OVERRIDING_TEXT)
    monkeypatch.undo()
    pipe.run("What is truth?")
    assert len(_turn_lines(sink)) == 2


# ---------------------------------------------------------------------------
# I6 — stream order stays monotone in turn number.
# ---------------------------------------------------------------------------

def test_i6_turn_events_appear_in_turn_order() -> None:
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    pipe = CognitiveTurnPipeline(runtime=rt)
    for text in (_OVERRIDING_TEXT, "What is truth?", "define wisdom"):
        pipe.run(text)
    turns = [row["turn"] for row in _turn_lines(sink)]
    assert turns == sorted(turns), turns
    assert len(turns) == 3


def test_i6_correction_event_follows_the_turn_it_corrects() -> None:
    """`_emit_correction_event` flushes any staged turn event first.

    `correct()` happens to emit the correction before calling `chat()`, so the
    order is right today by call sequence. Flushing explicitly makes it a
    property of the stream rather than of one call site.
    """
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    turns_before = len(_turn_lines(sink))
    assert turns_before == 1, "the corrected turn was flushed by its serve boundary"

    rt.correct("light reveals truth")
    # Nothing may be left in flight, and the corrected turn's own event was
    # already on the stream before the correction ran.
    assert rt._staged_turn_index is None
    assert len(_turn_lines(sink)) > turns_before, "correct() regenerates a turn"


def test_i6_a_staged_event_is_flushed_before_a_correction_event() -> None:
    """The ordering asserted directly, without relying on `correct()`'s shape."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    rt.begin_deferred_turn_emission()
    rt.chat(_OVERRIDING_TEXT)
    assert _turn_lines(sink) == [], "staged, not yet emitted"
    rt.correct("light reveals truth")
    # The staged turn event must precede anything the correction wrote.
    assert len(_turn_lines(sink)) >= 1
    first = json.loads(sink.lines[0])
    assert "epistemic_state" in first, "the turn event must be the first line out"


# ---------------------------------------------------------------------------
# I7 — at most one event in flight.
# ---------------------------------------------------------------------------

def test_i7_staging_a_second_event_flushes_the_first() -> None:
    """Two turns deferred without an intervening flush must not lose the first."""
    rt, sink = _runtime(**_OVERRIDING_CONFIG)
    rt.begin_deferred_turn_emission()
    rt.chat(_OVERRIDING_TEXT)
    assert _turn_lines(sink) == []
    rt.chat("What is truth?")
    assert len(_turn_lines(sink)) == 1, "staging turn 2 must flush turn 1, not drop it"
    rt.flush_deferred_turn_event()
    assert len(_turn_lines(sink)) == 2
    turns = [row["turn"] for row in _turn_lines(sink)]
    assert turns == sorted(turns)


# ---------------------------------------------------------------------------
# I8 — default deployment unaffected. This is what makes R7 flagless.
# ---------------------------------------------------------------------------

def test_i8_no_sink_means_no_behaviour_change() -> None:
    rt = ChatRuntime(config=RuntimeConfig(**_OVERRIDING_CONFIG), no_load_state=True)  # type: ignore[arg-type]
    assert rt._telemetry_sink is None
    result = CognitiveTurnPipeline(runtime=rt).run(_OVERRIDING_TEXT)
    assert rt._staged_turn_index is None, "nothing may be staged with no sink"
    assert rt.turn_log[-1].surface == result.surface, "back-stamping is unchanged"


def test_i8_surface_and_hash_match_a_sinkless_run() -> None:
    """Attaching a sink must not perturb the served bytes or the trace hash."""
    rt_sinkless = ChatRuntime(config=RuntimeConfig(**_OVERRIDING_CONFIG), no_load_state=True)  # type: ignore[arg-type]
    quiet = CognitiveTurnPipeline(runtime=rt_sinkless).run(_OVERRIDING_TEXT)
    rt_loud, _sink = _runtime(**_OVERRIDING_CONFIG)
    loud = CognitiveTurnPipeline(runtime=rt_loud).run(_OVERRIDING_TEXT)
    assert quiet.surface == loud.surface
    assert quiet.trace_hash == loud.trace_hash


# ---------------------------------------------------------------------------
# M2 — attach_telemetry_sink must NOT flush a staged turn event.
# ---------------------------------------------------------------------------

def test_m2_attaching_a_sink_does_not_flush_a_staged_turn_event() -> None:
    """The asymmetry with `_pending_reboot_payload` is deliberate.

    A buffered reboot payload is already final when buffered, so flushing it on
    attach is right. A staged turn event is mid-flight and may not yet be
    back-stamped; flushing it on attach would emit the pre-override record and
    silently restore the defect R7 fixed.
    """
    rt, first_sink = _runtime(**_OVERRIDING_CONFIG)
    rt.begin_deferred_turn_emission()
    rt.chat(_OVERRIDING_TEXT)
    assert _turn_lines(first_sink) == []

    second = JsonlBufferSink()
    rt.attach_telemetry_sink(second, include_content=True)
    assert _turn_lines(second) == [], "attach must not flush the staged turn event"
    assert rt._staged_turn_index is not None, "it must still be staged"

    rt.flush_deferred_turn_event()
    assert len(_turn_lines(second)) == 1


def test_m2_reboot_payload_flush_on_attach_is_untouched() -> None:
    """Leave the reboot flush exactly as it was — pinned so R7 cannot regress it."""
    rt = ChatRuntime(config=RuntimeConfig(), no_load_state=True)
    rt._pending_reboot_payload = '{"event":"reboot","synthetic":true}'
    sink = JsonlBufferSink()
    rt.attach_telemetry_sink(sink)
    assert sink.lines == ['{"event":"reboot","synthetic":true}']
    assert rt._pending_reboot_payload is None
