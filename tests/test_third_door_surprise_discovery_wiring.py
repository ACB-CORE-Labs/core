"""Third-Door #20 follow-up: high surprise → DiscoveryCandidate wiring.

Ledger §6 remaining surface (issue #30):
  - physics marks discovery_eligible (no teaching import)
  - teaching builds proposal-only DiscoveryCandidate (trigger=high_surprise)
  - opt-in sink emit; never VaultStore / self-install
"""

from __future__ import annotations

import inspect
import json

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from core.physics import surprise as surprise_mod
from core.physics.surprise import (
    DEFAULT_DISCOVERY_GAMMA,
    dual_operator,
    dual_procrustes_surprise,
    is_discovery_eligible,
    surprise_residual,
)
from teaching.discovery import (
    candidate_from_surprise_dual,
    emit_surprise_discovery,
)
from teaching.discovery_sink import DiscoveryBufferSink


def _id32() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _basis_identity() -> np.ndarray:
    """Single-column basis = identity versor (admits only near-identity probes)."""
    return _id32().reshape(N_COMPONENTS, 1)


# ---------------------------------------------------------------------------
# Physics layer — discovery_eligible flag
# ---------------------------------------------------------------------------


def test_is_discovery_eligible_predicate() -> None:
    assert is_discovery_eligible(
        surprise_norm=0.5, productive_or_transfer=False, discovery_gamma=0.35
    )
    assert not is_discovery_eligible(
        surprise_norm=0.1, productive_or_transfer=False, discovery_gamma=0.35
    )
    assert not is_discovery_eligible(
        surprise_norm=0.9, productive_or_transfer=True, discovery_gamma=0.35
    )
    assert not is_discovery_eligible(
        surprise_norm=0.9,
        productive_or_transfer=False,
        surprise_refused="degenerate_metric_span",
        discovery_gamma=0.35,
    )
    assert not is_discovery_eligible(
        surprise_norm=float("inf"), productive_or_transfer=False
    )


def test_dual_procrustes_marks_discovery_on_out_of_span_probe() -> None:
    """Non-identity probe against identity-only basis → high surprise → discovery."""
    basis = _basis_identity()
    src = _id32()
    tgt = make_rotor_from_angle(0.9, bivector_idx=6)
    dual = dual_procrustes_surprise(src, tgt, basis)
    assert dual["surprise_refused"] is None
    assert dual["surprise_norm"] > DEFAULT_DISCOVERY_GAMMA
    assert dual["transfer_accepted"] is False
    assert dual["discovery_eligible"] is True
    assert dual["discovery_gamma"] == DEFAULT_DISCOVERY_GAMMA


def test_dual_procrustes_no_discovery_on_identity_transfer() -> None:
    basis = _basis_identity()
    src = _id32()
    dual = dual_procrustes_surprise(src, src, basis)
    assert dual["surprise_norm"] < 1e-9
    assert dual["discovery_eligible"] is False


def test_dual_operator_discovery_eligible_when_surprise_high() -> None:
    x = make_rotor_from_angle(1.1, bivector_idx=7)
    basis = _basis_identity()
    analogs = [("a", _id32(), make_rotor_from_angle(0.4, bivector_idx=6))]
    out = dual_operator(x, basis, analogs, surprise_threshold=0.35)
    assert out["productive"] is False
    assert out["surprise_norm"] > 0.35
    assert out["discovery_eligible"] is True


def test_physics_surprise_does_not_import_teaching_or_vault() -> None:
    """No teaching/vault *imports* (docstrings may mention teaching by name)."""
    import ast
    from pathlib import Path

    tree = ast.parse(Path(surprise_mod.__file__).read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    assert "teaching" not in imported
    assert "vault" not in imported
    assert "VaultStore" not in inspect.getsource(surprise_mod)


# ---------------------------------------------------------------------------
# Teaching factory — proposal-only DiscoveryCandidate
# ---------------------------------------------------------------------------


def test_candidate_from_high_surprise_dual() -> None:
    dual = dual_procrustes_surprise(
        _id32(), make_rotor_from_angle(0.9, bivector_idx=6), _basis_identity()
    )
    assert dual["discovery_eligible"] is True
    c = candidate_from_surprise_dual(dual, source_turn_trace="trace-abc")
    assert c is not None
    assert c.trigger == "high_surprise"
    assert c.review_state == "unreviewed"
    assert c.domain == "math"
    assert c.proposed_chain["kind"] == "high_surprise"
    assert c.proposed_chain["subject"] == "geometric_frontier"
    assert c.proposed_chain["intent"] == "discovery"
    assert c.source_turn_trace == "trace-abc"
    assert c.boundary_clean is True
    assert float(c.proposed_chain["surprise_norm"]) == pytest.approx(
        dual["surprise_norm"]
    )


def test_candidate_absent_when_not_eligible() -> None:
    dual = dual_procrustes_surprise(_id32(), _id32(), _basis_identity())
    assert dual["discovery_eligible"] is False
    assert candidate_from_surprise_dual(dual) is None


def test_candidate_id_is_deterministic() -> None:
    # Angle must clear DEFAULT_DISCOVERY_GAMMA (0.35); 0.7 is just under.
    dual = dual_procrustes_surprise(
        _id32(), make_rotor_from_angle(1.0, bivector_idx=10), _basis_identity()
    )
    assert dual["discovery_eligible"] is True
    a = candidate_from_surprise_dual(dual, source_turn_trace="t1")
    b = candidate_from_surprise_dual(dual, source_turn_trace="t1")
    assert a is not None and b is not None
    assert a.candidate_id == b.candidate_id
    assert len(a.candidate_id) == 64  # sha256 hex


def test_emit_surprise_discovery_opt_in_sink() -> None:
    dual = dual_procrustes_surprise(
        _id32(), make_rotor_from_angle(1.0, bivector_idx=6), _basis_identity()
    )
    sink = DiscoveryBufferSink()
    c = emit_surprise_discovery(dual, sink, source_turn_trace="emit-1")
    assert c is not None
    assert len(sink.lines) == 1
    payload = json.loads(sink.lines[0])
    assert payload["trigger"] == "high_surprise"
    assert payload["review_state"] == "unreviewed"
    assert payload["domain"] == "math"
    assert payload["candidate_id"] == c.candidate_id


def test_emit_without_sink_is_pure() -> None:
    dual = dual_procrustes_surprise(
        _id32(), make_rotor_from_angle(0.8, bivector_idx=6), _basis_identity()
    )
    c = emit_surprise_discovery(dual, sink=None)
    assert c is not None
    assert c.trigger == "high_surprise"


def test_emit_no_candidate_leaves_sink_empty() -> None:
    dual = dual_procrustes_surprise(_id32(), _id32(), _basis_identity())
    sink = DiscoveryBufferSink()
    assert emit_surprise_discovery(dual, sink) is None
    assert sink.lines == []


def test_discovery_module_no_vault_store() -> None:
    import teaching.discovery as disc

    src = inspect.getsource(disc)
    assert "VaultStore" not in src
    # Factory must not call store() / write corpus paths
    assert "vault.store" not in src
    assert "VaultStore.store" not in src


def test_productive_transfer_is_not_discovery() -> None:
    """Low surprise + low procrustes → transfer, not discovery."""
    basis = np.column_stack([_id32(), make_rotor_from_angle(0.2, bivector_idx=6)])
    # Probe nearly in span of identity alone still low surprise on identity basis
    dual = dual_procrustes_surprise(_id32(), _id32(), _basis_identity())
    assert dual["transfer_accepted"] is True or dual["surprise_norm"] < 1e-4
    assert dual["discovery_eligible"] is False
    assert candidate_from_surprise_dual(dual) is None
    _ = basis  # reserved for future multi-column transfer fixtures
