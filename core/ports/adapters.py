"""core.ports.adapters — real port adapters for the Ring-2 residual protocol.

Two shipped ports with genuinely NON-identical native geometry (preflight §9:
"Ports retain non-identical native geometry"):

* :class:`IdentityPort` — ADR-0246 grade-1 frame preservation. The witness
  carries the §3.7 admit-surface scalars AND the §3.6 typed residual energies
  (they are all measurements of the subject, so they belong in the witness —
  this also keeps ``decompose`` a pure re-shaping of witness content, with no
  hidden adapter state to corrupt a replay). The admit verdict is
  ``evaluate_admission`` — the single source of truth; the adapter adds no
  policy of its own.
* :class:`PrecisionPort` — ADR-0244 §2.5 / ADR-0245 §2.2 f64→f32 cast
  transport. Witness = measured cast round-trip error + f32 unit-norm
  deviation; admit = both within tolerance. Subjects come from a certified
  ``ServingState`` (via :meth:`PrecisionSubject.from_serving_state`) or are
  built directly in evals.

Future adapters (Atlas, Evidence, Temporal/causal, Articulation, Action) plug
in the same way — the grammar has no registry and needs no change (proven by
the synthetic third port in the test suite).

Pure, deterministic, off-serving.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from core.physics.identity_action import AdmissionPolicy, evaluate_admission
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.ports.residual_protocol import (
    PortWitness,
    ResidualDecomposition,
)


class IdentityPort:
    """ADR-0246 identity organ speaking the Ring-2 grammar.

    Subject: a live versor ``F`` (32-component Cl(4,1) array).
    """

    port_id = "identity"
    schema_version = "identity_action_v1"

    def __init__(
        self, geometry: IdentityManifoldGeometry, policy: AdmissionPolicy
    ) -> None:
        self._geometry = geometry
        self._policy = policy

    def witness(self, subject: Any) -> PortWitness:
        versor = np.asarray(subject, dtype=np.float64)
        result = evaluate_admission(self._geometry, versor, self._policy)
        channels = self._geometry.typed_residual_energy(versor)
        return PortWitness(
            port_id=self.port_id,
            schema_version=self.schema_version,
            measurements=(
                ("d_orth", result.d_orth),
                ("d_stab", result.d_stab),
                ("leakage_rms", result.leakage_rms),
                ("max_leakage", result.max_leakage),
                ("min_self_alignment", result.min_self_alignment),
                ("ch_null_or_conformal", channels["null_or_conformal"]),
                ("ch_boost_like", channels["boost_like"]),
                ("ch_spatial_foreign", channels["spatial_foreign"]),
                ("ch_unclassified", channels["unclassified"]),
            ),
        )

    def decompose(self, witness: PortWitness) -> ResidualDecomposition:
        values = dict(witness.measurements)
        return ResidualDecomposition(
            port_id=self.port_id,
            channels=(
                ("null_or_conformal", values["ch_null_or_conformal"]),
                ("boost_like", values["ch_boost_like"]),
                ("spatial_foreign", values["ch_spatial_foreign"]),
                ("unclassified", values["ch_unclassified"]),
            ),
            unaccounted=values["ch_unclassified"],
            unaccounted_tol=self._policy.unclassified_tol,
        )

    def admit(
        self, subject: Any, decomposition: ResidualDecomposition
    ) -> tuple[bool, tuple[str, ...]]:
        result = evaluate_admission(
            self._geometry, np.asarray(subject, dtype=np.float64), self._policy
        )
        return result.admitted, tuple(result.refusal_reasons)


@dataclass(frozen=True)
class PrecisionSubject:
    """The Precision port's subject: a cast-transport measurement pair.

    Built from a certified :class:`~core.physics.cognitive_lifecycle.ServingState`
    (duck-typed via :meth:`from_serving_state` so this module stays light) or
    directly in evals/tests.
    """

    cast_error: float
    unit_norm_f32: float
    source_psi_digest: str = ""
    certificate_id: str = ""

    @classmethod
    def from_serving_state(cls, state: Any) -> "PrecisionSubject":
        return cls(
            cast_error=float(getattr(state, "cast_error")),
            unit_norm_f32=float(getattr(state, "unit_norm_f32")),
            source_psi_digest=str(getattr(state, "source_psi_digest", "")),
            certificate_id=str(getattr(state, "certificate_id", "")),
        )


class PrecisionPort:
    """ADR-0244 §2.5 cast-transport organ speaking the Ring-2 grammar.

    Native geometry: float-precision transport (round-trip error and unit-norm
    preservation across the governed f64→f32 boundary) — nothing like the
    identity port's grade-1 subspace geometry, which is exactly the point of a
    multi-port grammar.
    """

    port_id = "precision"
    schema_version = "serving_cast_v1"

    def __init__(self, tol: float) -> None:
        self._tol = float(tol)

    def witness(self, subject: PrecisionSubject) -> PortWitness:
        return PortWitness(
            port_id=self.port_id,
            schema_version=self.schema_version,
            measurements=(
                ("cast_error", float(subject.cast_error)),
                ("unit_norm_deviation", abs(1.0 - float(subject.unit_norm_f32))),
            ),
        )

    def decompose(self, witness: PortWitness) -> ResidualDecomposition:
        values = dict(witness.measurements)
        return ResidualDecomposition(
            port_id=self.port_id,
            channels=(
                ("cast_error", values["cast_error"]),
                ("unit_norm_deviation", values["unit_norm_deviation"]),
            ),
            unaccounted=0.0,  # both transport channels are fully typed
            unaccounted_tol=1e-12,
        )

    def admit(
        self, subject: PrecisionSubject, decomposition: ResidualDecomposition
    ) -> tuple[bool, tuple[str, ...]]:
        reasons: list[str] = []
        if float(subject.cast_error) > self._tol:
            reasons.append(f"cast_error>{self._tol:.3g}")
        if abs(1.0 - float(subject.unit_norm_f32)) > self._tol:
            reasons.append(f"unit_norm_deviation>{self._tol:.3g}")
        return (not reasons), tuple(reasons)
