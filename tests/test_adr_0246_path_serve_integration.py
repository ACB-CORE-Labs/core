"""ADR-0246 §3.4/§3.5 serve integration pins — session identity-path ledger.

Pins the §3.4-step-2 ``admitted`` gate on the pure ledger (a policy-refused turn
must break even when its d_stab is small), the ``advance_session_identity_path``
serve helper (scope from manifold digest + version ids; observe-only), the
runtime wiring (ledger advanced only when both flags are on; instance lifetime
is the session boundary), and the telemetry emission (identity_path_* keys only
when the path ran — flag-off wire format byte-identical).
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.config import RuntimeConfig
from core.physics.identity import (
    GEOMETRY_VERSION,
    IdentityManifold,
    ValueAxis,
    advance_session_identity_path,
    manifold_content_digest,
)
from core.physics.identity_action import (
    AdmissionPolicy,
    IdentityChainScope,
    PathBudget,
    advance_identity_path,
)
from core.physics.identity_manifold import IdentityManifoldGeometry
from chat.telemetry import serialize_turn_event

_E12, _E14 = 6, 8


def _rotor(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _boost(biv, theta):
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cosh(theta / 2.0)
    r[biv] = np.sinh(theta / 2.0)
    return r


def _identity_versor():
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _manifold():
    return IdentityManifold(
        value_axes=(
            ValueAxis(name="truthfulness", direction=(1.0, 0.0, 0.0)),
            ValueAxis(name="coherence", direction=(0.0, 1.0, 0.0)),
            ValueAxis(name="reverence", direction=(0.0, 0.0, 1.0)),
        )
    )


@pytest.fixture(scope="module")
def geometry():
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


# --- §3.4 step-2: the admitted gate on the pure ledger --------------------------


def test_policy_refused_turn_breaks_even_with_small_d_stab(geometry):
    scope = IdentityChainScope(
        pack_content_digest="p", geometry_version="g", policy_version="v",
        session_id="s",
    )
    budget = PathBudget(epsilon_turn=0.1, epsilon_session=0.3)
    small = geometry.induced_action(_rotor(_E12, 0.02))  # d_stab well under 0.1
    # admitted=False (e.g. refused on leakage alone) MUST break, not compose
    ledger, rec = advance_identity_path(
        None, scope, small, geometry.gram, budget, admitted=False
    )
    assert rec["lawful"] is False and rec["path_break"] is True
    assert ledger.composed_turn_count == 0 and ledger.break_count == 1
    assert np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)
    # same action with admitted=True composes
    ledger2, rec2 = advance_identity_path(
        None, scope, small, geometry.gram, budget, admitted=True
    )
    assert rec2["lawful"] is True and ledger2.composed_turn_count == 1


# --- advance_session_identity_path (serve helper) -------------------------------


def test_session_path_near_identity_composes():
    policy = AdmissionPolicy.placeholder_default()
    ledger, rec = advance_session_identity_path(
        None, _manifold(), _identity_versor(), policy
    )
    assert rec["hard_break"] is True and rec["lawful"] is True
    assert ledger.composed_turn_count == 1 and ledger.session_admit is True
    assert ledger.scope.pack_content_digest == manifold_content_digest(_manifold())
    assert ledger.scope.geometry_version == GEOMETRY_VERSION


def test_session_path_refused_turn_breaks():
    policy = AdmissionPolicy.placeholder_default()
    ledger, _ = advance_session_identity_path(
        None, _manifold(), _identity_versor(), policy
    )
    ledger, rec = advance_session_identity_path(
        ledger, _manifold(), _rotor(_E14, 1.5), policy  # alien tilt: refused
    )
    assert rec["lawful"] is False and rec["path_break"] is True
    assert ledger.break_count == 1 and ledger.composed_turn_count == 1


def test_session_path_hard_breaks_on_pack_change():
    policy = AdmissionPolicy.placeholder_default()
    ledger, _ = advance_session_identity_path(
        None, _manifold(), _identity_versor(), policy
    )
    first_chain = ledger.chain_id
    other_manifold = IdentityManifold(value_axes=_manifold().value_axes[:2])
    ledger, rec = advance_session_identity_path(
        ledger, other_manifold, _identity_versor(), policy
    )
    assert rec["hard_break"] is True
    assert ledger.chain_id != first_chain


# --- telemetry ------------------------------------------------------------------


class _Event:
    turn = 1
    identity_score = None
    identity_path = None


def test_telemetry_no_path_keys_when_absent():
    payload = serialize_turn_event(_Event())
    assert not any(k.startswith("identity_path_") for k in payload)


def test_telemetry_emits_path_keys_when_present():
    policy = AdmissionPolicy.placeholder_default()
    ledger, _ = advance_session_identity_path(
        None, _manifold(), _identity_versor(), policy
    )
    ev = _Event()
    ev.identity_path = ledger
    payload = serialize_turn_event(ev)
    assert payload["identity_path_chain_id"] == ledger.chain_id
    assert payload["identity_path_composed_turns"] == 1
    assert payload["identity_path_breaks"] == 0
    assert payload["identity_path_session_admit"] is True


# --- runtime wiring (flag-gated; observe-only) ----------------------------------


def test_runtime_ledger_attribute_defaults_none_and_flag_off_never_advances():
    from chat.runtime import ChatRuntime

    runtime = ChatRuntime(config=RuntimeConfig(), no_load_state=True)
    assert runtime._identity_path_ledger is None
    runtime.chat("water boils")
    assert runtime._identity_path_ledger is None  # both flags off: never advanced
    # and the emitted turn event carries no path ledger
    assert runtime.turn_log[-1].identity_path is None


def test_runtime_ledger_advances_when_both_flags_on():
    from chat.runtime import ChatRuntime

    runtime = ChatRuntime(
        config=RuntimeConfig(identity_wave_gate=True, identity_action_surface=True),
        no_load_state=True,
    )
    # Not every turn reaches the wave-path check (first-touch turns can take
    # the stub path — same reason slice-0 captured 13/16 probe turns), so run
    # the duplicated-probe pattern until one main-path turn advances the ledger.
    for text in ("water boils", "water boils", "birds fly", "birds fly"):
        runtime.chat(text)
        if runtime._identity_path_ledger is not None:
            break
    ledger = runtime._identity_path_ledger
    assert ledger is not None
    assert ledger.composed_turn_count + ledger.break_count >= 1
    # observe-only: chat() raised nothing regardless of session_admit; the
    # ledger-bearing turn's event serializes the path keys
    ledger_events = [e for e in runtime.turn_log if e.identity_path is not None]
    assert ledger_events, "no turn event carried the path ledger"
    payload = serialize_turn_event(ledger_events[-1])
    assert "identity_path_chain_id" in payload
