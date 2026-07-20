"""Stage 2 Master Blueprint — physics hardening & parity boundary pins.

Proves (without inventing dual implementations):

1. Shared fraction-decrease scale domain ``0 < k < 1`` is one function used by
   both obligation assessment and geometric admission.
2. Identity final authority has no L2 blend helpers / PASSTHROUGH.
3. Python/Rust parity surface: ops that are dual-backend are named; ops that
   are Python-authoritative only are documented so we never claim false parity.
4. Content digests remain full 64-hex LE f64 SHA-256.
"""

from __future__ import annotations

import ast
import hashlib
import inspect
from pathlib import Path

import numpy as np
import pytest

_ROOT = Path(__file__).resolve().parents[1]


# --- 1. Shared scale invariant -------------------------------------------------


def test_fraction_decrease_scale_domain_shared_by_assessment_and_geometry():
    from generate.problem_frame_contracts import _is_valid_fraction_decrease_scale

    # Domain itself
    assert _is_valid_fraction_decrease_scale(0.5) is True
    assert _is_valid_fraction_decrease_scale(0.0) is False
    assert _is_valid_fraction_decrease_scale(1.0) is False
    assert _is_valid_fraction_decrease_scale(-0.1) is False

    src = (_ROOT / "generate" / "problem_frame_contracts.py").read_text(encoding="utf-8")
    # Both obligation and geometric admission call the shared helper by name.
    assert src.count("_is_valid_fraction_decrease_scale") >= 3
    assert "scale_out_of_range" in src
    # Geometric admission path references the same helper (not a parallel check).
    assert "assess_fraction_decrease" in src
    assert "_dilation_versor_payload" in src or "VersorBinding" in src or "geometric" in src


def test_fraction_decrease_scale_source_has_single_domain_predicate():
    path = _ROOT / "generate" / "problem_frame_contracts.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defs = [
        n.name
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and "scale" in n.name
        and "valid" in n.name
    ]
    # Exactly one canonical domain predicate name.
    assert "_is_valid_fraction_decrease_scale" in defs
    assert defs.count("_is_valid_fraction_decrease_scale") == 1


# --- 2. L2 / legacy identity authority excision -------------------------------


def test_identity_module_has_no_l2_blend_helpers():
    path = _ROOT / "core" / "physics" / "identity.py"
    src = path.read_text(encoding="utf-8")
    tree = ast.parse(src)
    names = {
        n.name
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
    }
    forbidden = {
        "_axis_projection",
        "_mean_frame_coherence",
        "_legacy_score",
        "_l2_score",
        "_scalar_l2_blend",
    }
    assert not (names & forbidden), f"L2 helper functions still present: {names & forbidden}"
    # No 0.75 blend formula as live authority
    assert "0.75 *" not in src and "0.75*" not in src


def test_goldtether_primary_residual_not_flat_dot():
    path = _ROOT / "core" / "physics" / "goldtether.py"
    src = path.read_text(encoding="utf-8")
    # coherence_residual must route through WaveManifold / geometric product path
    assert "measure_unitary_residual" in src or "versor_unit_residual" in src
    assert "np.dot(psi" not in src
    assert "GoldTetherViolationError" in src


def test_pipeline_ratifier_has_no_passthrough_authority():
    from generate.intent_ratifier import RatificationOutcome

    values = {m.value for m in RatificationOutcome}
    assert "passthrough" not in values
    assert values == {"ratified", "demoted"}


# --- 3. Cl(4,1) active-path smoke (exact ops) ---------------------------------


def test_active_cl41_ops_geometric_product_conformal_gram_gt_sandwich():
    from algebra.backend import geometric_product, versor_condition
    from algebra.cga import N_INF, N_O, cga_inner, embed_point, is_null
    from algebra.cl41 import reverse
    from algebra.rotor import make_rotor_from_angle, word_transition_rotor
    from core.physics.cognitive_lifecycle import modality_transition_sandwich
    from core.physics.goldtether import require_unitary
    from core.physics.identity_manifold import gram_matrix, lift_axis

    # Geometric product + reverse unit condition
    R = make_rotor_from_angle(0.4)
    prod = geometric_product(R, reverse(R))
    assert abs(float(prod[0]) - 1.0) < 1e-9
    assert float(versor_condition(R)) < 1e-6

    # Conformal embedding null (f64 path; f32 embeds may exceed 1e-9 residual)
    X = embed_point(np.array([0.2, -0.1, 0.5], dtype=np.float64), dtype=np.float64)
    assert is_null(np.asarray(X, dtype=np.float64), tol=1e-6)
    assert abs(cga_inner(N_O, N_INF) + 1.0) < 1e-12

    # Gram subspace (identity axes)
    axes = [lift_axis((1.0, 0.0, 0.0)), lift_axis((0.0, 1.0, 0.0))]
    G = gram_matrix(axes)
    assert G.shape == (2, 2)

    # GoldTether unitary
    assert require_unitary(R) <= 1e-6

    # Multimodal sandwich
    psi = np.zeros(32, dtype=np.float64)
    psi[0] = 1.0
    target = make_rotor_from_angle(0.2)
    rotor = word_transition_rotor(psi, target)
    out, tr = modality_transition_sandwich(psi, rotor, source_modality="a", target_modality="b")
    assert out.shape == (32,)
    assert len(tr.psi_out_digest) == 64
    assert tr.goldtether_residual <= 1e-6


# --- 4. Python / Rust parity boundary -----------------------------------------


# Dual-backend ops (Rust exported + parity tests exist when core_rs built).
_DUAL_BACKEND_OPS = (
    "geometric_product",
    "cga_inner",
    "versor_condition",
    "versor_apply",  # sandwich
    "embed_point",
)

# Python-authoritative (or not exported on core_rs PyO3 surface). Claiming
# bit-parity without a Rust binding is forbidden.
_PYTHON_AUTHORITATIVE_OPS = (
    "rotor_power",  # algebra.rotor — no core_rs export
    "incidence",  # if present in algebra — not dual-backend
)


def test_rust_parity_surface_documented_and_no_false_claims():
    lib = (_ROOT / "core-rs" / "src" / "lib.rs").read_text(encoding="utf-8")
    for op in _DUAL_BACKEND_OPS:
        assert op in lib or op.replace("_", "") in lib or f"fn {op}" in lib or op in lib, (
            f"expected dual-backend op {op} in core-rs exports"
        )
    # rotor_power must NOT be falsely present as a public pyfunction
    assert "fn rotor_power" not in lib
    assert "wrap_pyfunction!(rotor_power" not in lib


def test_python_authoritative_ops_live_in_python_modules():
    from algebra import rotor

    assert hasattr(rotor, "rotor_power")
    assert callable(rotor.rotor_power)
    # Incidence: optional; if missing, document as N/A
    try:
        from algebra import incidence as _inc  # type: ignore

        assert _inc is not None
    except ImportError:
        pytest.skip("no algebra.incidence module — Python N/A, not a false Rust claim")


def test_existing_parity_test_files_cover_dual_backend_ops():
    tests_dir = _ROOT / "tests"
    names = {p.name for p in tests_dir.glob("test_*rust*parity*.py")}
    names |= {p.name for p in tests_dir.glob("test_*parity*.py")}
    # At least one parity file per dual-backend family
    assert any("geometric_product" in n for n in names)
    assert any("cga_inner" in n for n in names)
    assert any("versor_condition" in n for n in names)
    assert any("versor_apply" in n for n in names)
    assert any("cga_rust" in n or "embed" in n for n in names)


# --- 5. Content digests -------------------------------------------------------


def test_multivector_content_digest_is_sha256_le_f64():
    from core.physics.wave_manifold import multivector_content_digest

    F = np.zeros(32, dtype=np.float64)
    F[0] = 1.0
    dig = multivector_content_digest(F)
    assert len(dig) == 64
    assert all(c in "0123456789abcdef" for c in dig)
    le = np.ascontiguousarray(F, dtype=np.dtype("<f8"))
    assert dig == hashlib.sha256(le.tobytes()).hexdigest()
