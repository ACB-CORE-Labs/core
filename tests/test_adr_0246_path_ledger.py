"""ADR-0246 §3.4/§3.5 — lawful-only identity-path ledger pins (§6.2 path suite).

The path ledger composes ONLY the induced actions of turns that were individually
certified lawful (``d_stab ≤ ε_turn`` under the locked singleton ``H_id={I}``).
Refused turns insert a break marker and are excluded from the product — never a
soft-projected identity matrix masquerading as a pass (brief §3.4 / non-goal #11).
A scope change (pack digest / geometry / policy / session / biography epoch) forces
a hard break: a new ``chain_id`` and a fresh path (§3.5). Pure, off-serving.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.physics.identity_action import (
    IdentityChainScope,
    PathBudget,
    advance_identity_path,
    raw_path_product,
)

_E12, _E13 = 6, 7


def _rotor(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def _identity_versor() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


@pytest.fixture(scope="module")
def geometry() -> IdentityManifoldGeometry:
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


def _scope(pack="packA", geom="geomV1", policy="polV1", session="sess1", bio=None):
    return IdentityChainScope(
        pack_content_digest=pack,
        geometry_version=geom,
        policy_version=policy,
        session_id=session,
        biography_epoch=bio,
    )


_BUDGET = PathBudget(epsilon_turn=0.1, epsilon_session=0.3)


def _action(geometry, versor):
    return geometry.induced_action(versor)


def test_first_lawful_turn_starts_chain_near_identity(geometry):
    ledger, rec = advance_identity_path(
        None, _scope(), _action(geometry, _identity_versor()), geometry.gram, _BUDGET
    )
    assert rec["hard_break"] is True
    assert rec["lawful"] is True and rec["path_break"] is False
    assert ledger.composed_turn_count == 1 and ledger.break_count == 0
    assert np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)
    assert ledger.d_stab_path < 1e-12
    assert ledger.session_admit is True


def test_lawful_identity_sequence_stays_admitted(geometry):
    ledger = None
    for _ in range(20):
        ledger, _ = advance_identity_path(
            ledger, _scope(), _action(geometry, _identity_versor()), geometry.gram, _BUDGET
        )
    assert ledger.composed_turn_count == 20 and ledger.break_count == 0
    assert np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)
    assert ledger.session_admit is True


def test_small_rotations_accumulate_to_session_refusal(geometry):
    small = _action(geometry, _rotor(_E12, 0.05))  # each turn is lawful (small d_stab)
    ledger = None
    admitted_turns = 0
    for _ in range(40):
        ledger, rec = advance_identity_path(ledger, _scope(), small, geometry.gram, _BUDGET)
        assert rec["lawful"] is True  # each small step passes ε_turn
        admitted_turns += 1
        if not ledger.session_admit:
            break
    # per-turn always lawful, but the composed path eventually breaches ε_session
    assert ledger.session_admit is False
    assert ledger.d_stab_path > _BUDGET.epsilon_session
    assert ledger.composed_turn_count == admitted_turns


def test_refused_turn_is_break_and_excluded(geometry):
    ledger, _ = advance_identity_path(
        None, _scope(), _action(geometry, _identity_versor()), geometry.gram, _BUDGET
    )
    before = ledger.a_path_lawful.copy()
    big = _action(geometry, _rotor(_E12, np.pi / 2.0))  # 90° rotation: d_stab huge
    ledger, rec = advance_identity_path(ledger, _scope(), big, geometry.gram, _BUDGET)
    assert rec["lawful"] is False and rec["path_break"] is True
    assert ledger.break_count == 1 and ledger.composed_turn_count == 1
    # the refused action does NOT compose (no soft-projected I either): path unchanged
    assert np.allclose(ledger.a_path_lawful, before, atol=1e-12)


def test_interleaved_refuse_admit_records_raw(geometry):
    ident = _action(geometry, _identity_versor())
    big = _action(geometry, _rotor(_E12, np.pi / 2.0))
    seq = [ident, big, ident, big, ident]
    ledger = None
    records = []
    for a in seq:
        ledger, rec = advance_identity_path(ledger, _scope(), a, geometry.gram, _BUDGET)
        records.append(rec)
    assert ledger.composed_turn_count == 3 and ledger.break_count == 2
    assert [r["path_break"] for r in records] == [False, True, False, True, False]


def test_hard_break_on_pack_digest_change(geometry):
    ident = _action(geometry, _identity_versor())
    ledger, _ = advance_identity_path(None, _scope(pack="packA"), ident, geometry.gram, _BUDGET)
    id_a = ledger.chain_id
    # drift the path a little so "not continued" is observable
    small = _action(geometry, _rotor(_E12, 0.05))
    ledger, _ = advance_identity_path(ledger, _scope(pack="packA"), small, geometry.gram, _BUDGET)
    drifted = ledger.a_path_lawful.copy()
    # pack change → hard break
    ledger, rec = advance_identity_path(ledger, _scope(pack="packB"), ident, geometry.gram, _BUDGET)
    assert rec["hard_break"] is True
    assert ledger.chain_id != id_a
    assert ledger.composed_turn_count == 1 and ledger.break_count == 0  # fresh chain
    assert not np.allclose(ledger.a_path_lawful, drifted)  # old path not continued
    assert np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)


@pytest.mark.parametrize(
    "changed",
    [
        {"geom": "geomV2"},
        {"policy": "polV2"},
        {"session": "sess2"},
        {"bio": "epoch2"},
    ],
)
def test_hard_break_on_each_scope_dimension(geometry, changed):
    ident = _action(geometry, _identity_versor())
    ledger, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    base_id = ledger.chain_id
    ledger, rec = advance_identity_path(ledger, _scope(**changed), ident, geometry.gram, _BUDGET)
    assert rec["hard_break"] is True
    assert ledger.chain_id != base_id


def test_raw_product_differs_from_lawful_product(geometry):
    ident = _action(geometry, _identity_versor())
    big = _action(geometry, _rotor(_E12, np.pi / 2.0))
    seq = [ident, big, ident]
    ledger = None
    for a in seq:
        ledger, _ = advance_identity_path(ledger, _scope(), a, geometry.gram, _BUDGET)
    # forensic pin: composing ALL raw actions (incl. the refused 90°) gives a very
    # different result than the lawful-only product — the category error §3.4 forbids.
    raw = raw_path_product(seq)
    assert not np.allclose(raw, ledger.a_path_lawful)
    assert np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)  # lawful excludes the big turn


def test_chain_id_is_deterministic_full_sha256(geometry):
    ident = _action(geometry, _identity_versor())
    l1, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    l2, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    assert l1.chain_id == l2.chain_id
    assert len(l1.chain_id) == 64
    int(l1.chain_id, 16)  # valid hex


def test_ledger_digest_deterministic_and_path_sensitive(geometry):
    ident = _action(geometry, _identity_versor())
    small = _action(geometry, _rotor(_E13, 0.05))
    l1, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    l1b, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    assert l1.ledger_digest() == l1b.ledger_digest()
    assert len(l1.ledger_digest()) == 64
    l2, _ = advance_identity_path(l1, _scope(), small, geometry.gram, _BUDGET)
    assert l2.ledger_digest() != l1.ledger_digest()


def test_advance_is_immutable(geometry):
    ident = _action(geometry, _identity_versor())
    ledger, _ = advance_identity_path(None, _scope(), ident, geometry.gram, _BUDGET)
    snapshot = ledger.a_path_lawful.copy()
    count_before = ledger.composed_turn_count
    _new, _ = advance_identity_path(
        ledger, _scope(), _action(geometry, _rotor(_E12, 0.05)), geometry.gram, _BUDGET
    )
    assert ledger.composed_turn_count == count_before  # original untouched
    assert np.allclose(ledger.a_path_lawful, snapshot)


def test_as_dict_shape(geometry):
    ledger, _ = advance_identity_path(
        None, _scope(), _action(geometry, _identity_versor()), geometry.gram, _BUDGET
    )
    d = ledger.as_dict()
    assert d["schema_version"] == "identity_path_v1"
    assert d["chain_id"] == ledger.chain_id
    assert d["composed_turn_count"] == 1
    assert d["break_count"] == 0
    assert d["session_admit"] is True
    assert "a_path_lawful" in d and "d_stab_path" in d and "ledger_digest" in d


def test_lawful_path_equals_lawful_subproduct_not_raw(geometry):
    # HARDENING (ADR-0246 §3.4): a mixed sequence of small LAWFUL rotations
    # interleaved with a large REFUSED rotation must compose to exactly the
    # product of the lawful actions alone. This fails loudly if the raw product
    # (which would include the refused 90° turn) ever sneaks into a_path_lawful.
    small_a = _action(geometry, _rotor(_E12, 0.03))
    small_b = _action(geometry, _rotor(_E13, 0.04))
    big = _action(geometry, _rotor(_E12, np.pi / 2.0))  # refused (d_stab huge)
    seq = [small_a, big, small_b, big, small_a]
    ledger = None
    for a in seq:
        ledger, _ = advance_identity_path(ledger, _scope(), a, geometry.gram, _BUDGET)
    # independently: product of the LAWFUL turns only, in time order (later on left)
    expected = small_a @ (small_b @ small_a)
    assert ledger.composed_turn_count == 3 and ledger.break_count == 2
    assert np.allclose(ledger.a_path_lawful, expected, atol=1e-12)
    # and it must NOT equal the raw product (which includes the two big turns)
    assert not np.allclose(ledger.a_path_lawful, raw_path_product(seq))


def test_module_is_pure_offserving():
    import core.physics.identity_action as a

    with open(a.__file__, encoding="utf-8") as fh:
        src = fh.read()
    assert "chat.runtime" not in src and "import chat" not in src
