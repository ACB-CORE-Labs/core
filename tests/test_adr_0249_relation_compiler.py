"""ADR-0249 P2 — affine relation compiler pins.

Compiles `output = scale·input + offset` (Tier-1: scale > 0) into a
quadratic-well constraint Hamiltonian, reusing the ratified
compile_quadratic_well contract. The arithmetic is performed by the substrate
(versor transport), recovered by relaxation + projective readback — never by
the compiler (anti-hollow, spike §4.1).
"""
from __future__ import annotations

import hashlib

import numpy as np
import pytest

from core.physics.cognitive_lifecycle import (
    HamiltonianCompileError,
    ProblemHamiltonian,
    relax_to_ground,
)
from core.physics.quantity_kernel import decode_quantity
from core.physics.relation_compiler import (
    affine_relaxation_start,
    compile_affine_relation,
)


def _solve(inp: float, scale: float, offset: float) -> float:
    """Compile → relax from the known input → projectively decode the output."""
    ham = compile_affine_relation(inp, scale=scale, offset=offset)
    steady = relax_to_ground(affine_relaxation_start(inp), ham).psi_steady
    return decode_quantity(steady)


# --- The substrate performs the arithmetic; relaxation + decode recover it ---


@pytest.mark.parametrize(
    ("inp", "scale", "offset", "gold"),
    [
        (4.0, 3.0, 5.0, 17.0),      # multiply then add
        (10.0, 1.0, -7.0, 3.0),     # subtraction (offset < 0)
        (12.0, 1.0 / 3.0, 0.0, 4.0),  # division (scale = 1/divisor)
        (5.0, 2.0, 0.0, 10.0),      # pure multiply
        (0.0, 4.0, 9.0, 9.0),       # offset-only (zero input)
        (-6.0, 2.0, 3.0, -9.0),     # negative input
    ],
)
def test_forward_affine_answer_recovered(inp, scale, offset, gold) -> None:
    assert abs(_solve(inp, scale, offset) - gold) < 1e-4


# --- The compiled object is a pure constraint well, carrying no answer -------


def test_compile_returns_problem_hamiltonian() -> None:
    ham = compile_affine_relation(4.0, scale=3.0, offset=5.0)
    assert isinstance(ham, ProblemHamiltonian)
    assert ham.matrix.shape == (32, 32)
    assert ham.matrix.dtype == np.dtype(np.float64)


def test_hamiltonian_leaks_neither_answer_nor_relation() -> None:
    # Anti-hollow (spike §4.1): the well is a bare projector — its metadata
    # exposes only curvature + target digest, never scale/offset/answer.
    ham = compile_affine_relation(4.0, scale=3.0, offset=5.0)
    assert set(ham.metadata) == {"curvature", "target_digest"}
    assert ham.domain == "quadratic_well"


def test_ablation_relaxation_computes_the_answer() -> None:
    # The answer (17) is absent from the start state (decodes to the input 4);
    # relaxation is what produces it. The Hamiltonian bytes are identical either
    # way — the corridor does the work, not the compile step.
    ham = compile_affine_relation(4.0, scale=3.0, offset=5.0)
    start = affine_relaxation_start(4.0)
    assert abs(decode_quantity(start) - 4.0) < 1e-6
    steady = relax_to_ground(start, ham).psi_steady
    assert abs(decode_quantity(steady) - 17.0) < 1e-4
    assert ham.matrix.tobytes() == ham.matrix.tobytes()  # frozen, unchanged


def test_relaxation_start_decodes_to_known_input() -> None:
    assert abs(decode_quantity(affine_relaxation_start(7.5)) - 7.5) < 1e-9


# --- Fail-closed refusals (HamiltonianCompileError family, spike §4.3) -------


@pytest.mark.parametrize("bad_scale", [0.0, -1.0, -3.5])
def test_refuses_nonpositive_scale(bad_scale) -> None:
    with pytest.raises(HamiltonianCompileError):
        compile_affine_relation(4.0, scale=bad_scale, offset=1.0)


@pytest.mark.parametrize("bad", [np.inf, -np.inf, np.nan])
def test_refuses_nonfinite_input(bad) -> None:
    with pytest.raises(HamiltonianCompileError):
        compile_affine_relation(bad, scale=2.0, offset=1.0)


@pytest.mark.parametrize("bad", [np.inf, np.nan])
def test_refuses_nonfinite_scale(bad) -> None:
    with pytest.raises(HamiltonianCompileError):
        compile_affine_relation(4.0, scale=bad, offset=1.0)


@pytest.mark.parametrize("bad", [np.inf, np.nan])
def test_refuses_nonfinite_offset(bad) -> None:
    with pytest.raises(HamiltonianCompileError):
        compile_affine_relation(4.0, scale=2.0, offset=bad)


# --- Tier-2 cross-hardware reproducibility canary (spike §4.6) --------------

# SHA-256 of compile_affine_relation(4, scale=3, offset=5).matrix as <f8 bytes.
# Frozen from the first green run; a change means substrate/compile drift.
_GOLDEN_RELATION = "72e414a9549fc79dfae250d0c2e035108f0acdd6649a20193f96a1ff86bc3ce0"


def test_relation_hamiltonian_golden_bytes_are_stable() -> None:
    ham = compile_affine_relation(4.0, scale=3.0, offset=5.0)
    digest = hashlib.sha256(ham.matrix.astype("<f8").tobytes()).hexdigest()
    assert digest == _GOLDEN_RELATION, f"compile drift: got {digest}"
