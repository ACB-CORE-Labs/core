"""ADR-0238 / R&D §5 — GoldTether 𝓘_gold bootstrap + principal-axis prune (#18).

Residual+α already landed (#24). Remaining fidelity:
  * promote with proof payload (closed + residual gate + optional replay hash)
  * still proposal-only unless authorized (ADR-0092 gate)
  * principal-axis prune retains primals, drops low-eigen members
  * retained members stay closed (versor_condition < 1e-6)

See docs/research/third-door-blueprint-fidelity.md finding #4 / issue #18.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from algebra.versor import versor_condition
from core.physics.goldtether import (
    GoldPromotionProof,
    GoldTetherMonitor,
    OperatingMode,
)


def _id() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 1.0
    return v


def _closed_rotor(angle: float = 0.3, plane: int = 6) -> np.ndarray:
    return make_rotor_from_angle(angle, bivector_idx=plane)


def _dirty() -> np.ndarray:
    v = np.zeros(32, dtype=np.float64)
    v[0] = 0.5
    v[1] = 0.5
    return v


def _proof_for(F: np.ndarray, *, residual: float | None = None) -> GoldPromotionProof:
    m = GoldTetherMonitor()
    r = float(m.goldtether_residual(F) if residual is None else residual)
    payload = np.asarray(F, dtype=np.float64).tobytes() + f"{r:.12g}".encode()
    return GoldPromotionProof(
        residual=r,
        replay_hash=hashlib.sha256(payload).hexdigest(),
        reviewer_id="test-reviewer",
        closed=versor_condition(F) < 1e-6,
    )


# --- promote: ADR-0092 gate + proof discipline ---------------------------------


def test_promote_refuses_without_authorization_even_with_proof():
    """Proposal-only: proof alone must not mutate 𝓘_gold."""
    m = GoldTetherMonitor()
    F = _closed_rotor(0.2)
    proof = _proof_for(F)
    with pytest.raises(ValueError, match="authorization|ADR-0092|authorized"):
        m.promote_gold_invariant(F, proof=proof)
    assert len(m.gold_invariants) == 3


def test_promote_refuses_without_authorization():
    m = GoldTetherMonitor()
    with pytest.raises(ValueError, match="authorization|ADR-0092|authorized"):
        m.promote_gold_invariant(_closed_rotor(0.3))
    assert len(m.gold_invariants) == 3


def test_promote_refuses_non_closed_even_when_authorized():
    m = GoldTetherMonitor()
    dirty = _dirty()
    with pytest.raises(ValueError, match="closed|versor|closure"):
        m.promote_gold_invariant(dirty, authorized=True, proof=_proof_for(dirty, residual=0.0))
    assert len(m.gold_invariants) == 3


def test_promote_refuses_high_residual_even_when_authorized():
    """Drift-loud states must not enter 𝓘_gold even under explicit authorize."""
    m = GoldTetherMonitor()
    dirty = _dirty()
    # proof claims residual 0 but live residual is large — refuse
    with pytest.raises(ValueError, match="residual|ε|epsilon|drift"):
        m.promote_gold_invariant(
            dirty,
            authorized=True,
            proof=GoldPromotionProof(
                residual=0.0,
                replay_hash="0" * 64,
                reviewer_id="test",
                closed=False,
            ),
        )
    assert len(m.gold_invariants) == 3


def test_promote_requires_proof_when_require_proof_true():
    m = GoldTetherMonitor()
    F = _closed_rotor(0.15)
    with pytest.raises(ValueError, match="proof"):
        m.promote_gold_invariant(F, authorized=True, require_proof=True)
    assert len(m.gold_invariants) == 3


def test_promote_authorized_closed_low_residual_with_proof_appends():
    m = GoldTetherMonitor()
    F = _id()  # on-seed, residual 0
    proof = _proof_for(F)
    m.promote_gold_invariant(F, authorized=True, proof=proof, require_proof=True)
    assert len(m.gold_invariants) == 4
    assert np.allclose(m.gold_invariants[-1], F)


def test_promote_determinism_same_proof_payload():
    F = _closed_rotor(0.4)
    p1 = _proof_for(F)
    p2 = _proof_for(F)
    assert p1.replay_hash == p2.replay_hash
    assert p1.residual == p2.residual


# --- prune: principal-axis mode -----------------------------------------------


def test_prune_fifo_mode_retains_primals():
    """Backward-compatible default: size bound keeps three primals."""
    m = GoldTetherMonitor()
    for i in range(40):
        m.promote_gold_invariant(_closed_rotor(0.01 * i + 0.05), authorized=True)
    m.prune_gold_invariants(max_size=10, mode="fifo")
    assert len(m.gold_invariants) == 10
    assert m.gold_invariants[0][0] == 1.0
    assert m.gold_invariants[1][5] == 0.5
    assert m.gold_invariants[2][4] == 1.0 and m.gold_invariants[2][5] == 1.0


def test_prune_principal_axes_retains_primals_and_bounds_size():
    m = GoldTetherMonitor()
    for i in range(30):
        # Stay on Euclidean rotation planes (6–8); boost planes need cosh form.
        m.promote_gold_invariant(
            _closed_rotor(0.05 * i + 0.1, plane=6 + (i % 3)),
            authorized=True,
        )
    n_before = len(m.gold_invariants)
    assert n_before > 10
    m.prune_gold_invariants(max_size=8, mode="principal_axes")
    assert len(m.gold_invariants) <= 8
    assert len(m.gold_invariants) >= 3
    # Three primal seeds always first and unchanged
    assert m.gold_invariants[0][0] == 1.0
    assert m.gold_invariants[1][5] == 0.5 and m.gold_invariants[1][4] == -0.5
    assert m.gold_invariants[2][4] == 1.0 and m.gold_invariants[2][5] == 1.0


def test_prune_principal_axes_retained_members_are_closed():
    m = GoldTetherMonitor()
    for i in range(20):
        m.promote_gold_invariant(_closed_rotor(0.08 * i + 0.05), authorized=True)
    m.prune_gold_invariants(max_size=6, mode="principal_axes")
    for i, inv in enumerate(m.gold_invariants):
        # Primals n_o / n_inf are null (not unit versors); skip strict unit check
        if i == 0:
            assert versor_condition(inv) < 1e-6
        elif i >= 3:
            assert versor_condition(inv) < 1e-6, f"member[{i}] not closed"


def test_prune_principal_axes_differs_from_fifo_on_ordered_promotions():
    """PCA prune is not last-N FIFO: different retention among non-primals.

    Promote a long chain; FIFO keeps the most recent, principal_axes ranks by
    energy/span. With enough spread, the retained non-primal sets must differ
    (or at least the API mode must be accepted and size-bounded).
    """
    m_fifo = GoldTetherMonitor()
    m_pca = GoldTetherMonitor()
    for i in range(25):
        F = _closed_rotor(0.12 * i + 0.05, plane=6 + (i % 3))
        m_fifo.promote_gold_invariant(F, authorized=True)
        m_pca.promote_gold_invariant(F, authorized=True)
    m_fifo.prune_gold_invariants(max_size=7, mode="fifo")
    m_pca.prune_gold_invariants(max_size=7, mode="principal_axes")
    assert len(m_fifo.gold_invariants) == 7
    assert len(m_pca.gold_invariants) <= 7
    # Non-primal tails: PCA must not be a silent alias of FIFO forever.
    fifo_tail = [tuple(np.round(v, 8)) for v in m_fifo.gold_invariants[3:]]
    pca_tail = [tuple(np.round(v, 8)) for v in m_pca.gold_invariants[3:]]
    assert fifo_tail != pca_tail or len(pca_tail) < len(fifo_tail)


def test_prune_unknown_mode_refused():
    m = GoldTetherMonitor()
    with pytest.raises(ValueError, match="mode"):
        m.prune_gold_invariants(max_size=5, mode="not_a_mode")


def test_prune_refuses_stripping_below_primal_count():
    """max_size < 3 must not drop primal seeds (clamp / refuse)."""
    m = GoldTetherMonitor()
    m.promote_gold_invariant(_closed_rotor(0.2), authorized=True)
    m.prune_gold_invariants(max_size=2, mode="principal_axes")
    assert len(m.gold_invariants) >= 3
    assert m.gold_invariants[0][0] == 1.0


# --- eligibility helper (bootstrap pipeline surface) --------------------------


def test_promotion_eligible_true_for_closed_on_seed():
    m = GoldTetherMonitor()
    assert m.promotion_eligible(_id()) is True


def test_promotion_eligible_false_for_dirty():
    m = GoldTetherMonitor()
    assert m.promotion_eligible(_dirty()) is False


def test_serve_mode_never_relaxes_via_gold_set_growth():
    """Containment: growing 𝓘_gold does not make SERVE autonomous."""
    m = GoldTetherMonitor()
    m.autonomy = 1.0
    for i in range(5):
        m.promote_gold_invariant(_closed_rotor(0.05 * i), authorized=True)
    assert m.alpha_constraint(_id(), mode=OperatingMode.SERVE) == 1.0
