"""Field integration — embed typed constraints into Cl(4,1); return outcomes.

Linguistic layers never decide the field outcome. Candidates are embedded as
conformal points / composed rotors; closure is versor_condition + GoldTether.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

import numpy as np

from algebra.backend import versor_condition
from algebra.cga import embed_point, is_null
from algebra.cl41 import geometric_product
from algebra.rotor import make_rotor_from_angle
from core.cognition.fail_closed import (
    CoherenceRefusal,
    FailureClass,
    ResidualState,
)
from core.cognition.proof_trace import (
    ProofTrace,
    build_closed_trace,
    build_refusal_trace,
)
from core.physics.goldtether import coherence_residual
from core.semantic_primitives import OperatorClass, ValidationError
from generate.linguistic_pipeline.layer_a_english import SurfaceConstraintSet
from generate.linguistic_pipeline.layer_b_hebrew import EventOperatorSet
from generate.linguistic_pipeline.layer_c_koine import RelationGraph, TemporalTopology


@dataclass(frozen=True, slots=True)
class CoherentFieldState:
    field: np.ndarray
    proof_trace: ProofTrace
    selected_operator_class: OperatorClass
    versor_condition: float
    goldtether_residual: float
    # Digests of embedded multivectors — proves structure entered the field.
    embed_digests: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.proof_trace.closed:
            raise ValidationError("CoherentFieldState requires a closed proof_trace")
        arr = np.asarray(self.field)
        if arr.shape != (32,):
            raise ValidationError("CoherentFieldState.field must be shape (32,)")


@dataclass(frozen=True, slots=True)
class AmbiguousFieldState:
    candidate_operator_classes: tuple[OperatorClass, ...]
    manifold_ids: tuple[str, ...]
    proof_trace: ProofTrace
    reason: str

    @property
    def emits_answer(self) -> bool:
        return False


FieldOutcome = CoherentFieldState | AmbiguousFieldState | CoherenceRefusal

_OP_PLANE: dict[OperatorClass, tuple[float, int]] = {
    OperatorClass.TRANSFER: (0.21, 6),
    OperatorClass.REMOVAL: (0.34, 7),
    OperatorClass.ACCUMULATION: (0.47, 8),
    OperatorClass.CREATION: (0.18, 10),
    OperatorClass.PARTITION: (0.29, 11),
    OperatorClass.COMPARISON: (0.41, 13),
    OperatorClass.TRANSFORMATION: (0.53, 6),
    OperatorClass.RECURRENCE: (0.37, 7),
    OperatorClass.CAUSATION: (0.44, 8),
    OperatorClass.IDENTITY_CONTINUITY: (0.11, 10),
    OperatorClass.UNKNOWN: (0.07, 11),
}


def _mv_digest(mv: np.ndarray) -> str:
    arr = np.asarray(mv, dtype=np.float64).tobytes()
    return hashlib.sha256(arr).hexdigest()[:16]


def _stable_euclidean(seed: str) -> np.ndarray:
    """Deterministic R^3 coords in (-1,1)^3 from a candidate id (not a count)."""
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    coords = []
    for i in range(3):
        u = int.from_bytes(digest[2 * i : 2 * i + 2], "big") / 65535.0
        coords.append(2.0 * u - 1.0)
    return np.asarray(coords, dtype=np.float64)


def _identity_rotor() -> np.ndarray:
    r = np.zeros(32, dtype=np.float64)
    r[0] = 1.0
    return r


def _compose_rotor(F: np.ndarray, R: np.ndarray) -> np.ndarray:
    """Left-compose rotors. Both operands must already be unit rotors.

    No ``unitize_versor`` here — that is forbidden outside owned construction
    boundaries (INV-02b). ``make_rotor_from_angle`` products stay on Spin by
    construction; if residual drifts, the caller refuses rather than repair.
    """
    product = geometric_product(
        np.asarray(R, dtype=np.float64),
        np.asarray(F, dtype=np.float64),
    )
    return np.asarray(product, dtype=np.float64)


def _point_to_seed_rotor(point: np.ndarray, *, plane: int = 6) -> np.ndarray:
    """Map a conformal null point into a small rotor via grade-1 projection angle.

    Uses the Euclidean e1 component as an angle seed so distinct points produce
    distinct rotors under composition (structure-sensitive, not count-only).
    Built only from ``make_rotor_from_angle`` (closed by construction).
    """
    p = np.asarray(point, dtype=np.float64).ravel()
    # e1 is component index 1 in Cl(4,1) layout
    e1 = float(p[1]) if p.shape[0] >= 2 else 0.0
    e2 = float(p[2]) if p.shape[0] >= 3 else 0.0
    angle = float(np.tanh(e1) * 0.4 + np.tanh(e2) * 0.25)
    return make_rotor_from_angle(angle, bivector_idx=plane)


def _embed_entity_point(entity_id: str) -> np.ndarray:
    coords = _stable_euclidean(entity_id)
    point = embed_point(coords, dtype=np.float64)
    if not is_null(point, tol=1e-5):
        raise ValidationError(f"entity embed not null for {entity_id!r}")
    return np.asarray(point, dtype=np.float64)


def _embed_quantity_point(value_text: str, unit: str, token_id: str) -> np.ndarray:
    try:
        value = float(value_text)
    except ValueError as exc:
        raise ValidationError(f"non-numeric quantity {value_text!r}") from exc
    # Bound into embed-safe Euclidean range; unit seed perturbs y/z.
    unit_vec = _stable_euclidean(f"unit:{unit}:{token_id}")
    scale = float(np.tanh(value / 100.0))
    coords = np.asarray(
        [scale, 0.15 * unit_vec[1], 0.15 * unit_vec[2]],
        dtype=np.float64,
    )
    point = embed_point(coords, dtype=np.float64)
    if not is_null(point, tol=1e-5):
        raise ValidationError(f"quantity embed not null for {token_id!r}")
    return np.asarray(point, dtype=np.float64)


def _relation_rotor(left_point: np.ndarray, right_point: np.ndarray) -> np.ndarray:
    """Structure rotor from two conformal points, using only closed rotors.

    Reads Euclidean components of the null points (already embedded via
    ``embed_point``) and composes ``make_rotor_from_angle`` factors — no
    unitize/repair. Distinct point pairs ⇒ distinct rotor products.
    """
    seed = _identity_rotor()
    # Separation in e1/e2/e3 of the conformal embeddings.
    for plane, idx in ((6, 1), (7, 2), (8, 3)):
        delta = float(left_point[idx] - right_point[idx])
        if abs(delta) < 1e-15:
            continue
        angle = float(np.tanh(delta) * 0.25)
        seed = geometric_product(
            make_rotor_from_angle(angle, bivector_idx=plane),
            seed,
        )
    # Relative radial (n_o weight / e4-e5 mix) as an extra plane.
    radial = float(left_point[4] - right_point[4])
    seed = geometric_product(
        make_rotor_from_angle(float(np.tanh(radial) * 0.15), bivector_idx=10),
        seed,
    )
    return np.asarray(seed, dtype=np.float64)


def embed_constraints_into_field(
    surface: SurfaceConstraintSet,
    relation_graph: RelationGraph,
    selected: OperatorClass,
) -> tuple[np.ndarray, tuple[tuple[str, str], ...], list[tuple[str, str, tuple[tuple[str, str], ...]]]]:
    """Embed entities, quantities, and relations into a closed Cl(4,1) versor field.

    Returns (field, embed_digests, atom_descriptors for proof).
    """
    field = _identity_rotor()
    digests: list[tuple[str, str]] = []
    atoms: list[tuple[str, str, tuple[tuple[str, str], ...]]] = []
    entity_points: dict[str, np.ndarray] = {}

    for ent in surface.entities:
        point = _embed_entity_point(ent.candidate_id)
        entity_points[ent.candidate_id] = point
        rotor = _point_to_seed_rotor(point, plane=6)
        field = _compose_rotor(field, rotor)
        d = _mv_digest(point)
        digests.append((f"entity:{ent.candidate_id}", d))
        atoms.append(
            (
                f"atom:ent:{ent.candidate_id}",
                ent.candidate_id,
                (
                    ("role", "entity"),
                    ("surface", ent.surface),
                    ("embed_digest", d),
                    ("kind_hint", ent.kind_hint),
                ),
            )
        )

    for num in surface.numerics:
        point = _embed_quantity_point(num.value_text, num.unit, num.token_id)
        rotor = _point_to_seed_rotor(point, plane=7)
        field = _compose_rotor(field, rotor)
        d = _mv_digest(point)
        digests.append((f"quantity:{num.token_id}", d))
        atoms.append(
            (
                f"atom:qty:{num.token_id}",
                num.token_id,
                (
                    ("role", "quantity"),
                    ("value", num.value_text),
                    ("unit", num.unit),
                    ("embed_digest", d),
                ),
            )
        )

    for i, rel in enumerate(relation_graph.relations):
        left = entity_points.get(rel.left_entity_id)
        right = entity_points.get(rel.right_entity_id)
        if left is None or right is None:
            raise ValidationError(
                f"relation {rel.relation_id} references unembedded entity"
            )
        rrot = _relation_rotor(left, right)
        field = _compose_rotor(field, rrot)
        d = _mv_digest(rrot)
        digests.append((f"relation:{rel.relation_id}", d))
        atoms.append(
            (
                f"atom:rel:{i}",
                rel.kind.value,
                (
                    ("left", rel.left_entity_id),
                    ("right", rel.right_entity_id),
                    ("kind", rel.kind.value),
                    ("embed_digest", d),
                ),
            )
        )

    # Operator class as a distinct plane/angle — part of the field, not a label only.
    angle, plane = _OP_PLANE.get(selected, (0.07, 11))
    field = _compose_rotor(field, make_rotor_from_angle(angle, bivector_idx=plane))
    digests.append((f"operator:{selected.value}", _mv_digest(field)))

    atoms.append(
        (
            "atom:operator",
            selected.value,
            (
                ("operator_class", selected.value),
                ("plane", str(plane)),
                ("angle", f"{angle:.6f}"),
            ),
        )
    )

    # No unitize — field is a product of construction-closed rotors only.
    return np.asarray(field, dtype=np.float64), tuple(digests), atoms


def integrate_constraints(
    surface: SurfaceConstraintSet,
    events: EventOperatorSet,
    relation_graph: RelationGraph,
    temporal: TemporalTopology,
    *,
    force_geometry_fail: bool = False,
) -> FieldOutcome:
    """Integrate layered constraints into Cl(4,1) outcomes only.

    Rules:
      * Missing referents that block unique closure → CoherenceRefusal
      * Multi-class HE manifold without unique operator → AmbiguousFieldState
      * Unique operator + embedded geometry closed → CoherentFieldState + proof
      * force_geometry_fail → CoherenceRefusal
    """
    del temporal  # frames recorded on event candidates; not a linguistic override

    if relation_graph.missing_referents:
        miss = relation_graph.missing_referents[0]
        return CoherenceRefusal(
            failure_class=FailureClass.MISSING_REFERENT,
            violated_condition=f"referent_present:{miss.role}",
            residual_state=ResidualState(
                detail=f"{miss.referent_id}:{miss.expected_kind}:{miss.context}"
            ),
            refusal_reason=(
                f"unresolvable referent role={miss.role} "
                f"expected={miss.expected_kind} context={miss.context!r}"
            ),
            surface_message=(
                f"I cannot certify an answer: missing referent for role "
                f"'{miss.role}' ({miss.expected_kind})."
            ),
        )

    if force_geometry_fail:
        return CoherenceRefusal(
            failure_class=FailureClass.COHERENCE,
            violated_condition="versor_condition",
            residual_state=ResidualState(versor_condition=1.0, detail="forced_open"),
            refusal_reason="geometric contract forced open for verification",
        )

    multi = [m for m in events.manifolds if not m.resolved and len(m.candidate_ids) > 1]
    if multi:
        classes = tuple(
            OperatorClass(k) for m in multi for k in m.candidate_kinds
        )
        unique = tuple(dict.fromkeys(classes))
        if len(unique) > 1:
            return AmbiguousFieldState(
                candidate_operator_classes=unique,
                manifold_ids=tuple(m.manifold_id for m in multi),
                proof_trace=build_refusal_trace(
                    reason="ambiguous_operator_class",
                    violated_condition="unique_operator_class",
                ),
                reason="hebrew_root_admits_multiple_operator_classes",
            )

    if events.candidates:
        classes = tuple(dict.fromkeys(c.operator_class for c in events.candidates))
        if len(classes) > 1:
            return AmbiguousFieldState(
                candidate_operator_classes=classes,
                manifold_ids=tuple(m.manifold_id for m in events.manifolds),
                proof_trace=build_refusal_trace(
                    reason="ambiguous_operator_class",
                    violated_condition="unique_operator_class",
                ),
                reason="multiple_event_operator_classes",
            )
        selected = classes[0]
    else:
        if not surface.numerics:
            return CoherenceRefusal(
                failure_class=FailureClass.CONSTRAINT,
                violated_condition="event_or_numeric_present",
                residual_state=ResidualState(detail="no event operators or numerics"),
                refusal_reason="no admissible event or numeric constraints to close",
            )
        selected = OperatorClass.IDENTITY_CONTINUITY

    try:
        field, digests, atoms = embed_constraints_into_field(
            surface, relation_graph, selected
        )
    except (ValidationError, ValueError) as exc:
        return CoherenceRefusal(
            failure_class=FailureClass.FIELD,
            violated_condition="cl41_embed",
            residual_state=ResidualState(detail=str(exc)),
            refusal_reason=f"Cl(4,1) embedding failed: {exc}",
        )

    vc = float(versor_condition(field))
    gt = float(coherence_residual(field))
    if vc >= 1e-6 or gt > 1e-6:
        return CoherenceRefusal(
            failure_class=FailureClass.COHERENCE,
            violated_condition="versor_condition|goldtether",
            residual_state=ResidualState(
                versor_condition=vc, goldtether_residual=gt
            ),
            refusal_reason="field failed versor/GoldTether closure after embedding",
        )

    parent_ids = tuple(a[0] for a in atoms)
    ops = [
        (
            "op:embed",
            "cl41_embed_close",
            (
                ("versor_condition", f"{vc:.6e}"),
                ("goldtether_residual", f"{gt:.6e}"),
                ("embed_count", str(len(digests))),
            ),
            parent_ids,
        )
    ]
    proof = build_closed_trace(
        atoms=atoms,
        operators=ops,
        closure_symbol="geometric_contract_closed",
        closure_payload=(
            ("versor_condition", f"{vc:.6e}"),
            ("goldtether_residual", f"{gt:.6e}"),
            ("operator_class", selected.value),
        ),
    )
    return CoherentFieldState(
        field=field,
        proof_trace=proof,
        selected_operator_class=selected,
        versor_condition=vc,
        goldtether_residual=gt,
        embed_digests=digests,
    )


def outcome_kind(outcome: FieldOutcome) -> str:
    if isinstance(outcome, CoherentFieldState):
        return "coherent"
    if isinstance(outcome, AmbiguousFieldState):
        return "ambiguous"
    if isinstance(outcome, CoherenceRefusal):
        return "refusal"
    raise TypeError(f"unknown field outcome type: {type(outcome)!r}")


def outcome_as_dict(outcome: FieldOutcome) -> dict[str, Any]:
    kind = outcome_kind(outcome)
    if isinstance(outcome, CoherentFieldState):
        return {
            "kind": kind,
            "operator_class": outcome.selected_operator_class.value,
            "versor_condition": outcome.versor_condition,
            "goldtether_residual": outcome.goldtether_residual,
            "embed_digests": [list(p) for p in outcome.embed_digests],
            "proof_trace": outcome.proof_trace.as_dict(),
        }
    if isinstance(outcome, AmbiguousFieldState):
        return {
            "kind": kind,
            "candidate_operator_classes": [
                c.value for c in outcome.candidate_operator_classes
            ],
            "manifold_ids": list(outcome.manifold_ids),
            "reason": outcome.reason,
            "emits_answer": False,
        }
    return {
        "kind": kind,
        **outcome.as_dict(),
    }
