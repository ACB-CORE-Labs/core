"""§5.2 — the relational embedding, stated explicitly as §5.2 demands.

§5.2 requires the scheme be *declared*, derived from the paradigm rather than
improvised, and that the configuration encode **role-structure** — who plays
which role in which relation — rather than surface words. It also requires
(§5.3b) that residual not move with surface attributes. Those two sentences
pull against each other: an embedding that cannot see attributes is invariant
to them by construction, which makes §5.3b analytic rather than measured.

Both readings are therefore built, from one function with one constant changed:

    RS-A   ATTR_SCALE = 0.0    role skeleton only; attribute-invariance analytic
    RS-B   ATTR_SCALE > 0.0    quantities enter the geometry; §5.3b is measured

The scheme
----------
Let a graph have entities ``e_0 … e_{E-1}`` in order of introduction and
operations ``o_0 … o_{J-1}`` in source order. Names and units are never read.

*Entity points.* Entity ``k`` sits on the unit circle of the ``e1–e2`` plane at
angle ``θ_k = 2πk / SLOTS``. Its only identity is its **role index** — the
order in which the problem introduced it. Under RS-B its held quantity ``v``
displaces it along ``e3`` by ``ATTR_SCALE · v``.

*Relation points.* Operation ``j`` becomes one point at angle ``φ_j``, the
circular mean of its arguments' angles — so a relation literally sits between
the roles it relates. Its radius is ``R_OP + ORDER_STEP · j``, which encodes
*when* in the story the relation occurs. Its height is ``KIND_HEIGHT[kind]``, a
declared constant per relation kind; under RS-B the operand's magnitude adds
``ATTR_SCALE · w``.

*Unknown.* The asked-for role is marked by one point at that entity's angle,
radius ``R_UNKNOWN`` — the question is part of the problem's structure.

*Refusal.* A relation kind with no declared height raises. There is no default
geometry for an unknown relation: guessing one would silently place unrelated
structures on top of each other, which is exactly the failure this experiment
exists to detect.

*Padding.* Clouds are padded to ``MAX_POINTS`` with copies of the cloud's own
centroid, so a shorter configuration is not dragged toward a fixed foreign
point. Two clouds of different sizes still differ; the difference lands in
centroid mass rather than in an arbitrary corner of the space.

The cloud is handed to ``conformal_procrustes`` as a ``(5, K)`` array of
grade-1 components — the Kabsch + Umeyama path, whose residual is invariant to
rotation, translation and uniform scale (measured: ~1e-14) and which never
raises. The alternative sequence path performs field conjugacy and *does* raise
on structurally unlike inputs; residuals harvested from that exception are not
measurements, and this module does not use it.
"""

from __future__ import annotations

import math
from typing import Final, Mapping, Sequence

import numpy as np

from algebra.cga import embed_point
from generate.math_problem_graph import (
    Comparison,
    FractionPortion,
    MathProblemGraph,
    PartitionChunk,
    Quantity,
    Rate,
)

#: Angular slots on the role circle. Fixed across the corpus so role index k
#: means the same direction in every graph.
SLOTS: Final[int] = 8
R_ENTITY: Final[float] = 1.0
R_OP: Final[float] = 2.0
R_UNKNOWN: Final[float] = 3.0
ORDER_STEP: Final[float] = 0.35
MAX_POINTS: Final[int] = 16

#: Declared height per relation kind. Distinct constants, no arithmetic
#: relationship between them implied — they are labels on an axis, not values.
KIND_HEIGHT: Final[Mapping[str, float]] = {
    "add": 1.0,
    "subtract": -1.0,
    "transfer": 2.0,
    "multiply": 3.0,
    "divide": -3.0,
    "compare_multiplicative": 4.0,
    "compare_additive": -4.0,
    "apply_rate": 5.0,
    "unit_partition": -5.0,
    "fraction_portion": 6.0,
}

#: RS-A / RS-B selector.
ATTR_SCALE_STRUCTURE_ONLY: Final[float] = 0.0
ATTR_SCALE_ATTRIBUTE_BEARING: Final[float] = 0.02


class EmbeddingRefusal(ValueError):
    """Fail closed: no guessed geometry for an undeclared relation kind."""


def _angle(role_index: int) -> float:
    return 2.0 * math.pi * (role_index % SLOTS) / SLOTS


def _circular_mean(angles: Sequence[float]) -> float:
    if not angles:
        raise EmbeddingRefusal("cannot place a relation with no arguments")
    x = sum(math.cos(a) for a in angles) / len(angles)
    y = sum(math.sin(a) for a in angles) / len(angles)
    if abs(x) < 1e-12 and abs(y) < 1e-12:
        # Antipodal arguments: the mean direction is undefined. Use the first
        # argument's angle rather than an arbitrary one.
        return angles[0]
    return math.atan2(y, x)


def _operand_magnitude(operand: object) -> float:
    """The scalar an operand carries, or 0.0 when it carries none."""
    if isinstance(operand, Quantity):
        return float(operand.value)
    if isinstance(operand, Comparison):
        if operand.factor is not None:
            return float(operand.factor)
        if operand.delta is not None:
            return float(operand.delta.value)
        return 0.0
    if isinstance(operand, Rate):
        return float(operand.value)
    if isinstance(operand, PartitionChunk):
        return float(getattr(operand, "chunk_size", 0.0) or 0.0)
    if isinstance(operand, FractionPortion):
        num = float(getattr(operand, "numerator", 0.0) or 0.0)
        den = float(getattr(operand, "denominator", 1.0) or 1.0)
        return num / den if den else 0.0
    return 0.0


def _second_argument(operation: object) -> str | None:
    target = getattr(operation, "target", None)
    if target:
        return str(target)
    operand = getattr(operation, "operand", None)
    if isinstance(operand, Comparison):
        return operand.reference_actor
    return None


def euclidean_configuration(
    graph: MathProblemGraph, *, attr_scale: float
) -> list[tuple[float, float, float]]:
    """The R^3 configuration, before conformal embedding. Blind to labels."""
    role: dict[str, int] = {name: i for i, name in enumerate(graph.entities)}
    held: dict[str, float] = {}
    for possession in graph.initial_state:
        held.setdefault(possession.entity, float(possession.quantity.value))

    points: list[tuple[float, float, float]] = []

    for name in graph.entities:
        theta = _angle(role[name])
        z = attr_scale * held.get(name, 0.0)
        points.append((R_ENTITY * math.cos(theta), R_ENTITY * math.sin(theta), z))

    for j, operation in enumerate(graph.operations):
        kind = operation.kind
        if kind not in KIND_HEIGHT:
            raise EmbeddingRefusal(f"no declared height for relation kind {kind!r}")
        angles = [_angle(role[operation.actor])]
        second = _second_argument(operation)
        if second is not None and second in role:
            angles.append(_angle(role[second]))
        phi = _circular_mean(angles)
        radius = R_OP + ORDER_STEP * j
        z = KIND_HEIGHT[kind] + attr_scale * _operand_magnitude(operation.operand)
        points.append((radius * math.cos(phi), radius * math.sin(phi), z))

    asked = graph.unknown.entity
    theta = _angle(role[asked]) if asked in role else 0.0
    points.append((R_UNKNOWN * math.cos(theta), R_UNKNOWN * math.sin(theta), 0.0))

    if len(points) > MAX_POINTS:
        raise EmbeddingRefusal(
            f"configuration has {len(points)} points, over MAX_POINTS={MAX_POINTS}"
        )
    return points


def embed(graph: MathProblemGraph, *, attr_scale: float) -> np.ndarray:
    """Return the padded ``(5, MAX_POINTS)`` grade-1 conformal point cloud."""
    points = euclidean_configuration(graph, attr_scale=attr_scale)
    centroid = (
        sum(p[0] for p in points) / len(points),
        sum(p[1] for p in points) / len(points),
        sum(p[2] for p in points) / len(points),
    )
    padded = list(points) + [centroid] * (MAX_POINTS - len(points))
    columns = [
        embed_point(np.asarray(p, dtype=np.float64), dtype=np.float64) for p in padded
    ]
    return np.stack(columns, axis=1)[1:6, :]
