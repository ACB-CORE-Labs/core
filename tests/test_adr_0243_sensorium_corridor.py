"""ADR-0243 Phase 3 Lane B — sensorium corridor eval (I-04 first live consumer).

End-to-end: real Audio/Vision compilers → ingress → relaxation → egress →
readback → GoldTether, all composed (no re-implementation) in
``evals/adr_0243_cognitive_lifecycle``. Deterministic fixed-replay; no fixture
files (precedent: tests/test_adr_0241_sensorium_wave_feed.py:230,
tests/test_adr_0242_multi_scale_energy.py::test_eval_entry_matches_physics_helper).

Off-serving (A-04): ``core.physics.cognitive_lifecycle`` and
``core.physics.sensorium_wave_feed`` are already pinned quarantined in
``tests/test_serve_quarantine_transitive.py`` / ``tests/test_third_door_cohesion.py``;
this file adds a direct pin that ``chat/runtime.py`` never imports this eval package.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

from evals.adr_0243_cognitive_lifecycle import run_fixed_replay, sensorium_corridor_artifact

_ROOT = Path(__file__).resolve().parents[1]
_PACKAGE = _ROOT / "evals" / "adr_0243_cognitive_lifecycle"
_CLOSURE = 1e-6


def test_corridor_is_deterministic():
    """Same fixed inputs → byte-identical artifact (no randomness, no hidden state)."""
    first = json.dumps(run_fixed_replay(), sort_keys=True)
    second = json.dumps(run_fixed_replay(), sort_keys=True)
    assert first == second


def test_corridor_end_to_end_composes_real_compilers_through_readback_and_goldtether():
    artifact = run_fixed_replay()

    # Real compilers ran (not fake_deterministic_packet) and closed their own versors.
    assert artifact["modality_ids"] == ["audio", "vision"]
    assert artifact["audio"]["versor_condition"] < _CLOSURE
    assert artifact["vision"]["versor_condition"] < _CLOSURE

    # Relaxation decodes from the audio-only PARTIAL percept toward a well targeting
    # the full audio+vision percept — steps_taken > 0 pins that the relaxer actually
    # did the decode instead of starting already at its own target (start != target).
    relax = artifact["relaxation"]
    assert relax["converged"] is True
    assert relax["reason"] == "ground_state_certified"
    assert relax["steps_taken"] > 0
    assert artifact["ingress"]["partial_packet_digest"] != artifact["ingress"]["packet_digest"]

    # Egress admitted and routed to the hot band — readback path taken.
    egress = artifact["egress"]
    assert egress["admitted"] is True
    assert egress["reason"] == "admitted"
    assert egress["route"] == "readback_eligible"
    assert egress["energy_class"] in ("E3", "E4")

    # A multi-mode superposition is NOT a closed versor — egress must not have
    # silently gated on versor closure to reach admitted/readback_eligible.
    assert egress["versor_closed"] is False
    assert egress["versor_residual"] > _CLOSURE

    # E3/E4 readback carries no hedge prefix (ADR-0006): energy_modulated_surface
    # must not have silently repaired/altered the base surface for a hot state.
    assert artifact["readback_text"] is not None
    assert artifact["readback_text"] == (
        f"the {artifact['domain_id']} field integrated 2 modality packets "
        f"and relaxed to a {egress['energy_class']} state"
    )

    # GoldTetherMonitor.decide is a genuinely separate, explicit call: egress_gate
    # never populates it, and a fresh monitor fails closed regardless of residual.
    gt = artifact["goldtether_decision"]
    assert gt["residual"] == egress["versor_residual"]
    assert gt["band"] == "fail_closed"
    assert gt["reason"] == "residual_or_autonomy_fail_closed"


def test_corridor_refuses_when_energy_inputs_stay_cold():
    """Sanity: the hot-band route is earned by the supplied energy_inputs, not hardcoded.

    Default (E0-band) energy_inputs on the same real-compiler packets must NOT
    reach readback_eligible — proves the corridor reports the engine's actual
    routing decision rather than a fixed "readback_eligible" stub.
    """
    cold = sensorium_corridor_artifact(
        domain_id="adr_0243_sensorium_corridor_v1",
        sample_rate=24_000,
        tone_freq_hz=160.0,
        tone_duration_s=0.35,
        curvature=1.0,
        energy_inputs={},
        epsilon_drift=1e-6,
    )
    assert cold["egress"]["route"] != "readback_eligible"
    assert cold["readback_text"] is None


def test_corridor_artifact_is_json_serializable():
    text = json.dumps(run_fixed_replay(), sort_keys=True)
    assert json.loads(text)["outcome_id"]


def test_corridor_module_calls_no_cosine_or_ann_similarity():
    """No cosine/ANN anywhere in the corridor — I-04's algebraic-only resonance."""
    forbidden = {"cosine_similarity", "resonant_recall", "resonant_reconstruct", "sklearn"}
    for path in (_PACKAGE / "__init__.py", _PACKAGE / "__main__.py"):
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
        called: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                called.add(node.func.attr)
            if isinstance(node, ast.Import):
                called.update(alias.name for alias in node.names)
            if isinstance(node, ast.ImportFrom) and node.module:
                called.add(node.module)
        assert not (called & forbidden), f"{path.name} touches forbidden similarity op: {called & forbidden}"


def test_chat_runtime_does_not_import_the_corridor_eval():
    """The corridor lives under evals/ only — never a serve-path import."""
    runtime_src = (_ROOT / "chat" / "runtime.py").read_text(encoding="utf-8")
    tree = ast.parse(runtime_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "adr_0243_cognitive_lifecycle" not in node.module
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "adr_0243_cognitive_lifecycle" not in alias.name
