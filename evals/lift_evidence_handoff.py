"""ADR-0247/0248 evidence run — lift-instrument turns through ports + handoff (seam S5).

Routes two corridor turns through the Ring-2 residual protocol and the Ring-3
integrity handoff, OFF-SERVING (no flags touched — this produces §8 ruling
evidence, not activation):

* an **identity-action** turn (the canonical identity versor — under the
  locked ADR-0246 stabilizer H_id={I} the identity action is the ONLY lawful
  action, so this is the canonical lawful turn, not a toy) → expected: both
  ports PROCEED, handoff PROCEED;
* a **frame-rotating** turn (e1∧e2 rotor — an in-span rotation the ADR-0246
  stabilizer refuses) → expected: identity port ABSTAIN with typed reasons,
  handoff ABSTAIN.

Each turn is a REAL certified lifecycle outcome (relax → egress → governed
serving cast), so the PrecisionPort witnesses a genuine f64→f32 transport.
The pair demonstrates the handoff DISCRIMINATES — the acceptance evidence is
the contrast, not a single green path.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from algebra.cl41 import N_COMPONENTS
from core.epistemic_state import EpistemicState, NormativeClearance
from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleEngine,
    compile_quadratic_well,
    serving_cast,
)
from core.physics.identity_action import AdmissionPolicy
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.physics.sensorium_wave_feed import ModalityPacket
from core.ports.adapters import (
    IdentityPort,
    PrecisionPort,
    PrecisionSubject,
)
from core.ports.integrity_handoff import coordinate_handoff
from core.ports.residual_protocol import run_residual_protocol, verify_replay_chain

__all__ = ["run_lift_evidence_handoff"]

_E12 = 6  # grade-2 bivector block index of e1∧e2


def _rotor_e12(theta: float) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = np.cos(theta / 2.0)
    v[_E12] = np.sin(theta / 2.0)
    return v


def _identity_versor() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _certified_turn(target: np.ndarray, label: str) -> tuple[Any, Any]:
    """One real corridor turn: relax onto the target versor, egress, cast."""
    engine = CognitiveLifecycleEngine()
    packets = (ModalityPacket(modality_id=f"seed:{label}", coefficients=target),)
    outcome = engine.solve(packets, f"handoff-evidence:{label}", compile_quadratic_well(target))
    serving = serving_cast(
        outcome.relaxation.psi_steady, outcome.relaxation.certificate, outcome.verdict
    )
    return outcome, serving


def run_lift_evidence_handoff() -> dict[str, Any]:
    geometry = IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )
    policy = AdmissionPolicy.placeholder_default()
    identity_port = IdentityPort(geometry, policy)
    precision_port = PrecisionPort(1e-6)

    artifact: dict[str, Any] = {"turns": {}, "adr_refs": ["ADR-0246", "ADR-0247", "ADR-0248"]}
    for label, target in (
        ("identity-action", _identity_versor()),
        ("frame-rotating", _rotor_e12(0.5)),
    ):
        outcome, serving = _certified_turn(target, label)
        chain, identity_decision = run_residual_protocol(
            identity_port, outcome.relaxation.psi_steady, ()
        )
        chain, precision_decision = run_residual_protocol(
            precision_port, PrecisionSubject.from_serving_state(serving), chain
        )
        handoff = coordinate_handoff(
            chain,
            epistemic_state=EpistemicState.DECODED,
            normative_clearance=NormativeClearance.CLEARED,
        )
        artifact["turns"][label] = {
            "outcome_id": outcome.outcome_id,
            "serving": serving.as_dict(),
            "identity_action": identity_decision.as_dict(),
            "precision_action": precision_decision.as_dict(),
            "chain_verified": verify_replay_chain(chain),
            "chain_records": [r.as_dict() for r in chain],
            "handoff": handoff.as_dict(),
            "handoff_digest": handoff.handoff_digest(),
        }
    return artifact
