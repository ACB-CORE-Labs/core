"""core.physics.relation_compiler — affine relation → constraint Hamiltonian (ADR-0249 P2).

Compiles a single affine relation ``output = scale·input + offset`` (Tier-1:
scale > 0, offset ∈ ℝ, input a known quantity) into a quadratic-well
ProblemHamiltonian whose ground state is the null point encoding the output.

Anti-hollow (spike §4.1): the compiler NEVER evaluates ``scale·input + offset``
in Python. It embeds the input as a null point (P1) and applies the relation's
*structure* as versor operators — a dilator for the scale, a translator for the
offset — so the arithmetic is performed by the substrate's geometric product,
not by the compiler. The returned Hamiltonian is a bare geometric constraint
(a projector well); it carries no answer and no relation coefficients. Only
relaxation + projective readback recover the output.

Reuses the ratified ``compile_quadratic_well`` + ``HamiltonianCompileError``
contracts (spike §4.3/§4.4); fail-closed on non-finite coefficients and on
non-positive scale (outside the positive-dilation Tier-1 envelope). This is the
single-relation primitive; multi-step chaining (previously-certified state as
the next input) is the P4 turn-program compiler. Serve-quarantined (A-04):
``core/physics/`` is never imported by ``chat/runtime.py``.
"""
from __future__ import annotations

import math

import numpy as np

from core.physics.cognitive_lifecycle import (
    HamiltonianCompileError,
    ProblemHamiltonian,
    compile_quadratic_well,
)
from core.physics.quantity_kernel import (
    dilate_quantity,
    embed_quantity,
    translate_quantity,
)

__all__ = ["compile_affine_relation", "affine_relaxation_start"]

# Below this the transported target has collapsed and cannot be unit-normalized.
_MIN_TARGET_NORM = 1e-12


def _finite(value: float, *, what: str) -> float:
    v = float(value)
    if not math.isfinite(v):
        raise HamiltonianCompileError(f"{what}_not_finite")
    return v


def affine_relaxation_start(input_quantity: float) -> np.ndarray:
    """Unit-norm null point of the KNOWN input — the natural relaxation start.

    Decodes to the input (a given of the relation), never to the answer, so
    exposing it is not a hollow leak.
    """
    q = _finite(input_quantity, what="input")
    psi = embed_quantity(q)
    return (psi / np.linalg.norm(psi)).astype(np.float64)


def compile_affine_relation(
    input_quantity: float,
    *,
    scale: float,
    offset: float,
    curvature: float = 1.0,
) -> ProblemHamiltonian:
    """``output = scale·input + offset`` as a quadratic-well constraint Hamiltonian.

    ``scale`` > 0 (positive-dilation Tier-1 envelope); ``offset`` any finite
    real. ``curvature`` is validated by ``compile_quadratic_well``.
    """
    q = _finite(input_quantity, what="input")
    s = _finite(scale, what="scale")
    o = _finite(offset, what="offset")
    if s <= 0.0:
        raise HamiltonianCompileError("scale_not_positive", scale=s)

    # Relation structure as versors — never ``s*q + o`` in Python. Dilation
    # scales by e^{-alpha}, so multiplying by s needs alpha = -ln(s); the
    # substrate's geometric product performs the actual arithmetic.
    psi_scaled = dilate_quantity(embed_quantity(q), -math.log(s))
    psi_target = translate_quantity(psi_scaled, o)

    norm = float(np.linalg.norm(psi_target))
    if norm < _MIN_TARGET_NORM:
        raise HamiltonianCompileError("degenerate_affine_target", norm=norm)
    unit_target = (psi_target / norm).astype(np.float64)
    return compile_quadratic_well(unit_target, curvature=curvature)
