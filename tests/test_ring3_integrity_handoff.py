"""Ring 3 — integrity-coordinated handoff pins.

The preflight (ADR-0246 brief §9) fixes Ring 3's coordination role: "Integrity
coordinates handoffs; it does not replace content-bearing cognition." These pin
the pure coordinator that fuses the Ring-2 per-port action decisions with the
EXISTING content-organ types (EpistemicState, NormativeClearance) into a single
typed handoff for discourse/composition consumers:

  * any port abstain → ABSTAIN (integrity floor is conjunctive);
  * normative VIOLATED/SUPPRESSED → ABSTAIN; UNASSESSABLE → at most HEDGE;
  * weak epistemic standing (undetermined/speculative-class) → at most HEDGE;
  * strong standing + all ports proceed + cleared → PROCEED;
  * the handoff binds the replay chain (content-addressed) so the decision is
    auditable back to every port's evidence;
  * the coordinator NEVER fabricates content — it returns a routing decision
    only (pinned by its output type having no surface/content fields).
"""

from __future__ import annotations

import pytest

from core.epistemic_state import EpistemicState, NormativeClearance
from core.ports.integrity_handoff import (
    HANDOFF_ABSTAIN,
    HANDOFF_HEDGE,
    HANDOFF_PROCEED,
    IntegrityHandoff,
    coordinate_handoff,
)
from core.ports.residual_protocol import PortWitness, ResidualDecomposition, run_residual_protocol


class _Port:
    schema_version = "toy_v1"

    def __init__(self, port_id, value):
        self.port_id = port_id
        self._value = value

    def witness(self, subject):
        return PortWitness(
            port_id=self.port_id, schema_version=self.schema_version,
            measurements=(("residual", self._value),),
        )

    def decompose(self, witness):
        return ResidualDecomposition(
            port_id=self.port_id,
            channels=(("scalar", dict(witness.measurements)["residual"]),),
            unaccounted=0.0, unaccounted_tol=1e-9,
        )

    def admit(self, subject, decomposition):
        value = dict(decomposition.channels)["scalar"]
        return (True, ()) if value <= 0.5 else (False, (f"{self.port_id}:refused",))


def _chain(*port_values):
    chain = ()
    for port_id, value in port_values:
        chain, _ = run_residual_protocol(_Port(port_id, value), None, chain)
    return chain


def test_all_proceed_cleared_verified_gives_proceed():
    chain = _chain(("identity", 0.1), ("precision", 0.2))
    handoff = coordinate_handoff(
        chain,
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.CLEARED,
    )
    assert handoff.handoff == HANDOFF_PROCEED
    assert handoff.port_actions == (("identity", "proceed"), ("precision", "proceed"))


def test_any_port_abstain_forces_abstain():
    chain = _chain(("identity", 0.1), ("precision", 0.9))
    handoff = coordinate_handoff(
        chain,
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.CLEARED,
    )
    assert handoff.handoff == HANDOFF_ABSTAIN
    assert any("precision" in r for r in handoff.reasons)


@pytest.mark.parametrize("clearance", [NormativeClearance.VIOLATED, NormativeClearance.SUPPRESSED])
def test_normative_violation_forces_abstain(clearance):
    chain = _chain(("identity", 0.1))
    handoff = coordinate_handoff(
        chain, epistemic_state=EpistemicState.VERIFIED, normative_clearance=clearance,
    )
    assert handoff.handoff == HANDOFF_ABSTAIN


def test_unassessable_clearance_caps_at_hedge():
    chain = _chain(("identity", 0.1))
    handoff = coordinate_handoff(
        chain,
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.UNASSESSABLE,
    )
    assert handoff.handoff == HANDOFF_HEDGE


@pytest.mark.parametrize(
    "state",
    [
        EpistemicState.UNDETERMINED,
        EpistemicState.UNVERIFIED_POSSIBLE,
        EpistemicState.UNVERIFIED_NOVEL,
        EpistemicState.AMBIGUOUS,
        EpistemicState.CONTRADICTED,
    ],
)
def test_weak_epistemic_standing_caps_at_hedge(state):
    chain = _chain(("identity", 0.1))
    handoff = coordinate_handoff(
        chain, epistemic_state=state, normative_clearance=NormativeClearance.CLEARED,
    )
    assert handoff.handoff in (HANDOFF_HEDGE, HANDOFF_ABSTAIN)
    assert handoff.handoff == HANDOFF_HEDGE  # hedge, not abstain: content may still surface qualified


def test_handoff_binds_replay_chain_digest():
    chain = _chain(("identity", 0.1))
    handoff = coordinate_handoff(
        chain,
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.CLEARED,
    )
    assert handoff.chain_tip_digest == chain[-1].record_digest()
    assert len(handoff.handoff_digest()) == 64
    int(handoff.handoff_digest(), 16)
    # deterministic
    again = coordinate_handoff(
        chain,
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.CLEARED,
    )
    assert again.handoff_digest() == handoff.handoff_digest()


def test_empty_chain_fails_closed():
    handoff = coordinate_handoff(
        (),
        epistemic_state=EpistemicState.VERIFIED,
        normative_clearance=NormativeClearance.CLEARED,
    )
    assert handoff.handoff == HANDOFF_ABSTAIN
    assert any("no_port_evidence" in r for r in handoff.reasons)


def test_coordinator_never_carries_content():
    # Ring 3 contract: integrity coordinates handoffs, it does NOT replace
    # content-bearing cognition. The handoff type must carry no content/surface
    # fields — only routing, attribution, and digests.
    fields = set(IntegrityHandoff.__dataclass_fields__)
    assert "surface" not in fields and "content" not in fields and "text" not in fields
    assert {"handoff", "reasons", "port_actions", "chain_tip_digest"} <= fields


def test_module_is_pure_offserving():
    import core.ports.integrity_handoff as mod

    assert mod.__file__ is not None
    with open(mod.__file__, encoding="utf-8") as fh:
        src = fh.read()
    assert "import chat" not in src and "from chat" not in src
