"""ADR-0243 §2.3 — linguistic wave readback pins (seam S1 closure).

Ground truth: docs/research/spark-audit-adjudication-2026-07-18.md §4 (S1) and
ADR-0243 §2.3 — egress route ``readback_eligible`` must flow into geometric
token selection over a versor vocabulary (token_t = argmax_T ⟨ψ_steady ψ̃_T⟩_0),
then the "hearing ourselves think" round-trip: re-ingest the articulated tokens
through the sensorium boundary and measure phase-locked agreement with the
I-04 sanctioned metric (WaveManifold.phase_correlation — no cosine/ANN).

Fail-closed doctrine (decoding, not generating): no resonant token ⇒ typed
ReadbackRefusal, never a fallback string. The real VocabManifold is used in
these tests to prove the structural VocabLike protocol matches it.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleEngine,
    compile_quadratic_well,
)
from core.physics.linguistic_readback import (
    LinguisticReadback,
    ReadbackRefusal,
    RoundTripReport,
    articulate_outcome,
    hearing_ourselves_think,
    linguistic_readback,
    readback_packets,
)
from core.physics.sensorium_wave_feed import fake_deterministic_packet
from vocab.manifold import VocabManifold

# Hot-band energy inputs matching the E3/E4 precedent
# (test_egress_routes_hot_state_to_readback_eligible).
_HOT_ENERGY = {
    "convergence_density": 8,
    "activation_count": 8,
    "current_cycle": 1,
    "last_activation_cycle": 1,
    "morphology_features": {"mood": "imperative"},
}


def _target_rotor() -> np.ndarray:
    return np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)


def _hot_outcome():
    """Ingress → relax → egress with hot energy axes ⇒ route readback_eligible."""
    engine = CognitiveLifecycleEngine()
    target = _target_rotor()
    ham = compile_quadratic_well(target)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    outcome = engine.solve(packets, "readback-demo", ham, energy_inputs=_HOT_ENERGY)
    assert outcome.verdict.route == "readback_eligible"
    return target, outcome


def _vocab(target: np.ndarray) -> VocabManifold:
    """Real VocabManifold: the target mode, a kindred same-plane rotor, and two
    far large-angle rotors in other planes (resonance ≈ cos(0.15)·cos(θ/2) ≪ 0.5)."""
    v = VocabManifold()
    v.add("resonant", target)
    v.add("kindred", np.asarray(make_rotor_from_angle(0.5, bivector_idx=6), dtype=np.float64))
    v.add("far-a", np.asarray(make_rotor_from_angle(2.8, bivector_idx=7), dtype=np.float64))
    v.add("far-b", np.asarray(make_rotor_from_angle(2.9, bivector_idx=8), dtype=np.float64))
    return v


def test_readback_selects_most_resonant_token_first():
    target, outcome = _hot_outcome()
    vocab = _vocab(target)
    rb = linguistic_readback(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
        vocab,
        min_resonance=0.5,
        max_tokens=4,
    )
    assert isinstance(rb, LinguisticReadback)
    assert tuple(t.word for t in rb.tokens) == ("resonant", "kindred")
    assert rb.tokens[0].resonance > 0.999  # ψ_steady locked onto the target mode
    resonances = [t.resonance for t in rb.tokens]
    assert resonances == sorted(resonances, reverse=True)
    assert all(r >= 0.5 for r in resonances)
    json.dumps(rb.as_dict())  # JSON-safe artifact


def test_readback_respects_max_tokens_bound():
    target, outcome = _hot_outcome()
    rb = linguistic_readback(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
        _vocab(target),
        min_resonance=0.5,
        max_tokens=1,
    )
    assert tuple(t.word for t in rb.tokens) == ("resonant",)


def test_readback_refuses_when_route_not_eligible():
    engine = CognitiveLifecycleEngine()
    target = _target_rotor()
    ham = compile_quadratic_well(target)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    cold = engine.solve(packets, "readback-demo", ham)  # cold ⇒ crystallization route
    assert cold.verdict.route != "readback_eligible"
    with pytest.raises(ReadbackRefusal) as exc:
        linguistic_readback(
            cold.relaxation.psi_steady,
            cold.relaxation.certificate,
            cold.verdict,
            _vocab(target),
            min_resonance=0.5,
            max_tokens=4,
        )
    assert exc.value.reason == "route_not_readback_eligible"


def test_readback_refuses_without_resonant_token_no_fallback():
    _target, outcome = _hot_outcome()
    sparse = VocabManifold()
    sparse.add("far-a", np.asarray(make_rotor_from_angle(2.8, bivector_idx=7), dtype=np.float64))
    sparse.add("far-b", np.asarray(make_rotor_from_angle(2.9, bivector_idx=8), dtype=np.float64))
    with pytest.raises(ReadbackRefusal) as exc:
        linguistic_readback(
            outcome.relaxation.psi_steady,
            outcome.relaxation.certificate,
            outcome.verdict,
            sparse,
            min_resonance=0.5,
            max_tokens=4,
        )
    assert exc.value.reason == "no_resonant_token"
    assert 0.0 < exc.value.disclosure["best_resonance"] < 0.5


def test_readback_refuses_certificate_state_mismatch():
    target, outcome = _hot_outcome()
    foreign = np.asarray(make_rotor_from_angle(1.0, bivector_idx=7), dtype=np.float64)
    with pytest.raises(ReadbackRefusal) as exc:
        linguistic_readback(
            foreign,
            outcome.relaxation.certificate,
            outcome.verdict,
            _vocab(target),
            min_resonance=0.5,
            max_tokens=4,
        )
    assert exc.value.reason == "certificate_state_mismatch"


def test_readback_refuses_empty_vocabulary_and_bad_policy():
    target, outcome = _hot_outcome()
    args = (
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
    )
    with pytest.raises(ReadbackRefusal) as exc:
        linguistic_readback(*args, VocabManifold(), min_resonance=0.5, max_tokens=4)
    assert exc.value.reason == "empty_vocabulary"
    with pytest.raises(ReadbackRefusal):
        linguistic_readback(*args, _vocab(target), min_resonance=0.0, max_tokens=4)
    with pytest.raises(ReadbackRefusal):
        linguistic_readback(*args, _vocab(target), min_resonance=0.5, max_tokens=0)


def test_round_trip_agreement_above_099():
    """Hearing ourselves think: re-ingested articulation stays phase-locked."""
    target, outcome = _hot_outcome()
    vocab = _vocab(target)
    rb = linguistic_readback(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
        vocab,
        min_resonance=0.5,
        max_tokens=4,
    )
    report = hearing_ourselves_think(
        outcome.relaxation.psi_steady, rb, vocab, domain_id=outcome.ingress.domain_id
    )
    assert isinstance(report, RoundTripReport)
    assert report.n_tokens == 2
    assert report.agreement > 0.99
    assert report.agreement == pytest.approx(report.phase_correlation / 2.0)
    json.dumps(report.as_dict())


def test_readback_packets_carry_token_versors():
    target, outcome = _hot_outcome()
    vocab = _vocab(target)
    rb = linguistic_readback(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
        vocab,
        min_resonance=0.5,
        max_tokens=1,
    )
    (pkt,) = readback_packets(rb, vocab)
    assert pkt.modality_id == "linguistic:resonant"
    np.testing.assert_allclose(pkt.coefficients, target, atol=1e-6)  # f32 store rounding


def test_articulate_outcome_composes_and_is_deterministic():
    target, outcome = _hot_outcome()
    vocab = _vocab(target)
    rb1, rt1 = articulate_outcome(outcome, vocab, min_resonance=0.5, max_tokens=4)
    rb2, rt2 = articulate_outcome(outcome, vocab, min_resonance=0.5, max_tokens=4)
    assert rb1.readback_id == rb2.readback_id
    assert rt1.report_id == rt2.report_id
    assert rt1.agreement == rt2.agreement
    assert rb1.psi_digest == outcome.relaxation.certificate.psi_digest


def test_module_is_pure_offserving_and_vocab_decoupled():
    import core.physics.linguistic_readback as m

    with open(m.__file__, encoding="utf-8") as fh:
        src = fh.read()
    assert "chat.runtime" not in src
    assert "import chat" not in src
    # Layering pin: vocab access is structural (VocabLike protocol) — importing
    # the vocab package from core.physics would cycle through the barrel.
    assert "from vocab" not in src
    assert "import vocab" not in src
