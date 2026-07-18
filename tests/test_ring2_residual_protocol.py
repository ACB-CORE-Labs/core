"""Ring 2 — multi-port residual protocol pins (shared control grammar).

The preflight (ADR-0246 brief §9) fixes Ring 2 as a SHARED CONTROL GRAMMAR
only: witness → typed residual decomposition → permitted operator selection →
bounded operation or abstention → re-certification → articulation/action
decision → append-only replay record — with ports retaining NON-identical
native geometry. These tests pin:

  * the grammar runs all seven stages deterministically and purely;
  * v1 ships ONLY zero-bound operators (proceed_unmodified / abstain) — a
    nonzero-bound operator fails closed (no-silent-correction doctrine);
  * re-certification requires the witness unchanged after a zero-bound
    operation (a mutating "zero-bound" port fails closed);
  * the replay chain is append-only, content-addressed (full SHA-256), and
    verifiable; tampering any record breaks verification;
  * two REAL ports with genuinely different native geometry — Identity
    (ADR-0246 grade-1 frame preservation) and Precision (ADR-0244 §2.5 f32
    cast transport) — both speak the grammar without the grammar knowing
    either geometry;
  * a synthetic third port proves port-agnosticism (no port registry, no
    unified scheduler — brief §7 non-goal honored).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_action import AdmissionPolicy
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.ports.residual_protocol import (
    GENESIS_DIGEST,
    ActionDecision,
    PermittedOperator,
    PortWitness,
    ReplayRecord,
    ResidualDecomposition,
    ResidualProtocolError,
    run_residual_protocol,
    verify_replay_chain,
)
from core.ports.adapters import IdentityPort, PrecisionPort, PrecisionSubject

_E12, _E14 = 6, 8


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _identity_versor():
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


@pytest.fixture(scope="module")
def geometry():
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


@pytest.fixture(scope="module")
def identity_port(geometry):
    return IdentityPort(geometry, AdmissionPolicy.placeholder_default())


# --- a synthetic third port: proves the grammar is port-agnostic ---------------


class _ToyPort:
    """Minimal conforming port with a made-up native geometry (scalar residual)."""

    port_id = "toy"
    schema_version = "toy_v1"

    def witness(self, subject):
        return PortWitness(
            port_id=self.port_id,
            schema_version=self.schema_version,
            measurements=(("residual", float(subject)),),
        )

    def decompose(self, witness):
        value = dict(witness.measurements)["residual"]
        return ResidualDecomposition(
            port_id=self.port_id,
            channels=(("scalar", value),),
            unaccounted=0.0,
            unaccounted_tol=1e-9,
        )

    def admit(self, subject, decomposition):
        value = dict(decomposition.channels)["scalar"]
        if value <= 0.5:
            return True, ()
        return False, ("scalar>0.5",)


# --- grammar mechanics ----------------------------------------------------------


def test_toy_port_proceed_and_abstain_paths():
    port = _ToyPort()
    chain, decision = run_residual_protocol(port, 0.1, ())
    assert decision.action == "proceed"
    assert len(chain) == 1
    chain, decision = run_residual_protocol(port, 0.9, chain)
    assert decision.action == "abstain"
    assert decision.reasons == ("scalar>0.5",)
    assert len(chain) == 2


def test_replay_chain_is_append_only_content_addressed():
    port = _ToyPort()
    chain, _ = run_residual_protocol(port, 0.1, ())
    chain, _ = run_residual_protocol(port, 0.9, chain)
    chain, _ = run_residual_protocol(port, 0.2, chain)
    assert [r.sequence_index for r in chain] == [0, 1, 2]
    assert chain[0].prev_record_digest == GENESIS_DIGEST
    assert chain[1].prev_record_digest == chain[0].record_digest()
    assert chain[2].prev_record_digest == chain[1].record_digest()
    assert verify_replay_chain(chain) is True
    for record in chain:
        assert len(record.record_digest()) == 64
        int(record.record_digest(), 16)


def test_tampered_chain_fails_verification():
    port = _ToyPort()
    chain, _ = run_residual_protocol(port, 0.1, ())
    chain, _ = run_residual_protocol(port, 0.2, chain)
    from dataclasses import replace
    tampered = (chain[0], replace(chain[1], prev_record_digest="0" * 64))
    assert verify_replay_chain(tampered) is False
    # and altering a payload breaks the digest linkage of any later record
    tampered2 = (replace(chain[0], action="abstain"), chain[1])
    assert verify_replay_chain(tampered2) is False


def test_determinism_same_inputs_same_digests():
    port = _ToyPort()
    a, _ = run_residual_protocol(port, 0.3, ())
    b, _ = run_residual_protocol(port, 0.3, ())
    assert a[0].record_digest() == b[0].record_digest()


def test_nonzero_bound_operator_fails_closed():
    class _CorrectorPort(_ToyPort):
        port_id = "toy_corrector"

        def permitted_operators(self, decomposition):
            return (PermittedOperator(operator_id="nudge", bound=0.1),)

    with pytest.raises(ResidualProtocolError, match="nonzero_bound"):
        run_residual_protocol(_CorrectorPort(), 0.1, ())


def test_mutating_zero_bound_port_fails_recertification():
    class _MutatingPort(_ToyPort):
        port_id = "toy_mutator"

        def __init__(self):
            self._calls = 0

        def witness(self, subject):
            # a port whose measurement drifts between witness and re-certify:
            # a zero-bound operation must leave the witness unchanged, so this
            # MUST fail closed rather than record a corrupted replay.
            self._calls += 1
            return PortWitness(
                port_id=self.port_id,
                schema_version=self.schema_version,
                measurements=(("residual", 0.1 * self._calls),),
            )

    with pytest.raises(ResidualProtocolError, match="recertification"):
        run_residual_protocol(_MutatingPort(), 0.1, ())


def test_unaccounted_residual_fails_closed():
    class _LeakyPort(_ToyPort):
        port_id = "toy_leaky"

        def decompose(self, witness):
            return ResidualDecomposition(
                port_id=self.port_id,
                channels=(("scalar", 0.1),),
                unaccounted=0.5,       # energy the typed channels cannot account for
                unaccounted_tol=1e-6,  # -> fail closed, no correction policy
            )

    chain, decision = run_residual_protocol(_LeakyPort(), 0.1, ())
    assert decision.action == "abstain"
    assert any("unaccounted" in r for r in decision.reasons)


def test_cross_port_records_interleave_in_one_chain():
    toy = _ToyPort()
    chain, _ = run_residual_protocol(toy, 0.1, ())
    other = _ToyPort()
    other.port_id = "toy_b"
    chain, _ = run_residual_protocol(other, 0.2, chain)
    assert [r.port_id for r in chain] == ["toy", "toy_b"]
    assert verify_replay_chain(chain) is True


# --- real port: Identity (ADR-0246 native geometry) -----------------------------


def test_identity_port_proceeds_on_near_identity(identity_port):
    chain, decision = run_residual_protocol(identity_port, _identity_versor(), ())
    assert decision.action == "proceed"
    record = chain[-1]
    assert record.port_id == "identity"
    channels = dict(record.decomposition["channels"])
    assert set(channels) == {
        "null_or_conformal", "boost_like", "spatial_foreign", "unclassified",
    }


def test_identity_port_abstains_on_alien_tilt(identity_port):
    chain, decision = run_residual_protocol(identity_port, _rotor(_E14, 1.5), ())
    assert decision.action == "abstain"
    assert any("leakage" in r or "d_" in r for r in decision.reasons)


# --- real port: Precision (ADR-0244 §2.5 cast-transport native geometry) --------


def test_precision_port_proceeds_on_clean_cast():
    port = PrecisionPort(tol=1e-6)
    subject = PrecisionSubject(cast_error=1e-8, unit_norm_f32=1.0 + 1e-8)
    chain, decision = run_residual_protocol(port, subject, ())
    assert decision.action == "proceed"
    channels = dict(chain[-1].decomposition["channels"])
    assert set(channels) == {"cast_error", "unit_norm_deviation"}


def test_precision_port_abstains_on_precision_cliff():
    port = PrecisionPort(tol=1e-6)
    subject = PrecisionSubject(cast_error=1e-3, unit_norm_f32=1.0)
    chain, decision = run_residual_protocol(port, subject, ())
    assert decision.action == "abstain"


def test_identity_and_precision_share_one_replay_chain(identity_port):
    chain, _ = run_residual_protocol(identity_port, _identity_versor(), ())
    chain, _ = run_residual_protocol(
        PrecisionPort(tol=1e-6),
        PrecisionSubject(cast_error=1e-8, unit_norm_f32=1.0),
        chain,
    )
    assert [r.port_id for r in chain] == ["identity", "precision"]
    assert verify_replay_chain(chain) is True


def test_module_is_pure_offserving():
    import core.ports.residual_protocol as protocol
    import core.ports.adapters as ports

    for mod in (protocol, ports):
        assert mod.__file__ is not None
        with open(mod.__file__, encoding="utf-8") as fh:
            src = fh.read()
        assert "import chat" not in src and "from chat" not in src
