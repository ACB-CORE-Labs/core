"""ADR-0243 Phase 3 Lane B — sensorium corridor eval (research evidence, OFF-SERVING).

First live consumer of the I-04 sensorium feed (`docs/plans/adr-0243-implementation-plan.md`
§5 Phase 3 Lane B). Composes already-built, already-tested organs into one deterministic
corridor — no new ``core.physics`` module, no new resonance math:

    AudioCompiler.compile / VisionCompiler.compile_tile          (sensorium/*)
            │  .versor
            ▼
    packet_from_compilation_unit(modality_id, unit)              (core/physics/sensorium_wave_feed.py)
            ▼
    relax_to_ground(ψ_partial, H(ψ_full))  via CognitiveLifecycleEngine.egress  (relax → egress)
            ▼  E3/E4 route: "readback_eligible"
    generate/realizer.py:energy_modulated_surface(base_surface, energy_class)
            │
            └── separately, explicitly: GoldTetherMonitor.decide(...)

Lives under ``evals/`` only; never imported by ``chat/runtime.py`` (A-04 quarantine —
inherited transitively from ``core.physics.cognitive_lifecycle`` /
``core.physics.sensorium_wave_feed``, both already pinned in
``tests/test_serve_quarantine_transitive.py`` / ``tests/test_third_door_cohesion.py``).

The corridor's Hamiltonian targets the FULL audio+vision integrated field
(``target_psi = ingress_full.psi``); relaxation starts from the audio-only PARTIAL
percept (``ingress_partial.psi``) so the relaxer actually decodes across real steps
toward the full percept — "recognize what was just perceived" only holds if the
relaxer starts short of what it is recognizing. ``engine.solve()`` is not used here
because it ties relaxation start == Hamiltonian target; the stages are driven
explicitly instead, then reassembled into one ``LifecycleOutcome`` (keeping
``outcome_id``/digests keyed off the full percept, not the partial start). No
cosine/ANN anywhere — resonance inside the corridor is algebraic
(``WaveManifold``-backed) only.
"""

from __future__ import annotations

from typing import Mapping

import numpy as np

from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleEngine,
    LifecycleOutcome,
    compile_quadratic_well,
    ingest_context,
    relax_to_ground,
)
from core.physics.goldtether import GoldTetherMonitor, OperatingMode
from core.physics.sensorium_wave_feed import packet_from_compilation_unit
from generate.realizer import energy_modulated_surface
from sensorium.audio.compiler import AudioCompiler
from sensorium.vision import VisionCompiler, canonicalize_image
from sensorium.vision.grid import iter_tile_signals

__all__ = [
    "run_fixed_replay",
    "sensorium_corridor_artifact",
]

# Hot-band energy inputs matching the existing E3/E4 precedent
# (tests/test_adr_0243_cognitive_lifecycle.py::test_egress_routes_hot_state_to_readback_eligible).
# Caller-supplied structural axes only — never invented inside the engine.
_DEFAULT_ENERGY_INPUTS: Mapping[str, object] = {
    "convergence_density": 8,
    "activation_count": 8,
    "current_cycle": 1,
    "last_activation_cycle": 1,
    "morphology_features": {"mood": "imperative"},
}


def _fixed_audio_tone(sample_rate: int, duration_s: float, freq_hz: float) -> np.ndarray:
    n = int(sample_rate * duration_s)
    t = np.arange(n, dtype=np.float64) / sample_rate
    return (0.5 * np.sin(2.0 * np.pi * freq_hz * t)).astype(np.float32)


def _fixed_vision_tile():
    x = np.linspace(0.0, 1.0, 32, dtype=np.float32)
    y = np.linspace(0.0, 1.0, 32, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    image = np.stack([xx, yy, 1.0 - xx], axis=2).astype(np.float32)
    return iter_tile_signals(canonicalize_image(image))[0]


def sensorium_corridor_artifact(
    *,
    domain_id: str,
    sample_rate: int,
    tone_freq_hz: float,
    tone_duration_s: float,
    curvature: float,
    energy_inputs: Mapping[str, object],
    epsilon_drift: float,
) -> dict:
    """Run the full corridor once on deterministic fixed inputs; return a JSON-safe dict.

    Fails closed (raises the module's typed errors) rather than repairing a
    malformed intermediate state at any stage.
    """
    audio_unit = AudioCompiler().compile(
        _fixed_audio_tone(sample_rate, tone_duration_s, tone_freq_hz), sample_rate
    )
    vision_unit = VisionCompiler().compile_tile(_fixed_vision_tile())

    audio_pkt = packet_from_compilation_unit("audio", audio_unit)
    vision_pkt = packet_from_compilation_unit("vision", vision_unit)
    packets = (audio_pkt, vision_pkt)

    # Target: the full integrated percept. Start: the audio-only partial percept —
    # a genuinely different unit state with positive overlap on the full field, so
    # relaxation decodes across real steps instead of starting already-converged.
    ingress_full = ingest_context(packets, domain_id)
    hamiltonian = compile_quadratic_well(ingress_full.psi, curvature=curvature)
    ingress_partial = ingest_context((audio_pkt,), domain_id)

    engine = CognitiveLifecycleEngine(epsilon_drift=epsilon_drift)
    result = relax_to_ground(ingress_partial.psi, hamiltonian)
    verdict = engine.egress(result.psi_steady, result.certificate, **energy_inputs)
    outcome = LifecycleOutcome(ingress=ingress_full, relaxation=result, verdict=verdict)

    readback_text: str | None = None
    if verdict.route == "readback_eligible":
        base_surface = (
            f"the {domain_id} field integrated {len(packets)} modality packets "
            f"and relaxed to a {verdict.energy_class.value} state"
        )
        readback_text = energy_modulated_surface(base_surface, verdict.energy_class)

    # A fresh monitor is uncalibrated (autonomy=0) and the superposition residual
    # is well above epsilon_drift, so this legitimately comes back fail_closed —
    # that is the honest HITL-safe default, not a corridor bug.
    monitor = GoldTetherMonitor(epsilon_drift=epsilon_drift)
    decision = monitor.decide(verdict.versor_residual, mode=OperatingMode.PRACTICE)

    return {
        "domain_id": domain_id,
        "modality_ids": list(ingress_full.modality_ids),
        "audio": {
            "versor_condition": audio_unit.versor_condition,
            "projection_sha256": audio_unit.projection_sha256,
        },
        "vision": {
            "versor_condition": vision_unit.versor_condition,
            "projection_sha256": vision_unit.projection_sha256,
        },
        "ingress": {
            "packet_digest": ingress_full.packet_digest,
            "partial_packet_digest": ingress_partial.packet_digest,
        },
        "hamiltonian": {
            "hamiltonian_id": hamiltonian.hamiltonian_id,
            "domain": hamiltonian.domain,
        },
        "relaxation": outcome.relaxation.certificate.as_dict(),
        "egress": {
            "admitted": verdict.admitted,
            "reason": verdict.reason,
            "route": verdict.route,
            "unit_norm_residual": verdict.unit_norm_residual,
            "versor_residual": verdict.versor_residual,
            "versor_closed": verdict.versor_closed,
            "energy_class": verdict.energy_class.value,
            "energy_raw": verdict.energy_profile.raw,
        },
        "readback_text": readback_text,
        "goldtether_decision": {
            "band": decision.band.value,
            "residual": decision.residual,
            "floor": decision.floor,
            "autonomy": decision.autonomy,
            "mode": decision.mode.value,
            "reason": decision.reason,
        },
        "outcome_id": outcome.outcome_id,
    }


def run_fixed_replay(
    *,
    domain_id: str = "adr_0243_sensorium_corridor_v1",
    sample_rate: int = 24_000,
    tone_freq_hz: float = 160.0,
    tone_duration_s: float = 0.35,
    curvature: float = 1.0,
    energy_inputs: Mapping[str, object] | None = None,
    epsilon_drift: float = 1e-6,
) -> dict:
    """Entry point for the fixed-replay sensorium corridor eval (deterministic)."""
    return sensorium_corridor_artifact(
        domain_id=domain_id,
        sample_rate=sample_rate,
        tone_freq_hz=tone_freq_hz,
        tone_duration_s=tone_duration_s,
        curvature=curvature,
        energy_inputs=dict(energy_inputs) if energy_inputs is not None else dict(_DEFAULT_ENERGY_INPUTS),
        epsilon_drift=epsilon_drift,
    )
