"""core.physics.identity — Identity as geometric structure, not prompt veneer.

ADR-0010: The IdentityManifold is a fixed geometric subspace of the
versor field encoding CORE's stable character as an architectural
constant. Every ReasoningTrajectory is checked against the manifold
before articulation. Identity is inalienable — it cannot be overridden
by context length, adversarial prompting, or instruction injection.

Theological grounding: John 1:1-2.
The Word is not a description of God. It is God, expressed.
CORE's identity is not a description of CORE. It is CORE, expressed geometrically.
"""

from __future__ import annotations
import functools
import math
import warnings
from dataclasses import dataclass
from typing import Dict, FrozenSet, List, Optional, Tuple

import numpy as np

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_manifold import IdentityManifoldGeometry
from core.physics.identity_action import AdmissionPolicy, evaluate_admission

# ADR-0244 §2.2 / §4a / §2.4 — wave-gate thresholds.
#
# ``_WAVE_LEAKAGE_BOUND`` is the calibrated subspace-leakage bound γ_id: a versor
# whose RMS leakage out of the value subspace exceeds it is flagged. It was
# calibrated in D4 Phase 3 by a bracketed-local Fibonacci section search over a
# geometric reference set (identity-preserving in-subspace rotors vs axis→e4/e5
# tilt/boost attacks) — reproduce with ``evals.adr_0244_gamma_calibration``.
#   objective_id=gamma_id_leakage v1, budget=24, interval=[0,1], sharpness=10
#   certificate 0079b5f201fbf616a274f5776a16ebb682fb431384efe81c114edc68c3fbd80b
# It replaces the earlier provisional reuse of ``alignment_threshold`` so the
# wave path no longer borrows the legacy-path / hedge-band threshold.
#
# HONEST SCOPE (Phase 3 finding): this bound separates the *geometric* attack
# signal, NOT real benign traffic — live ``final_state.F`` versors do not preserve
# span(e1,e2,e3) (the shipped axes are nominal basis vectors, not dynamically
# preserved eigenmodes), so benign leakage overlaps the attack range and the
# calibration certifies ``flag_flip_authorized=False``. The wave gate therefore
# stays flag-gated OFF in the runtime (``identity_wave_gate=False``); this bound
# governs only the off-serve research/eval path until identity is made
# dynamically load-bearing (ADR-0246 induced action).
_WAVE_LEAKAGE_BOUND: float = 0.2126624458513829
# The orientation floor flags a value axis the versor has rotated *past
# orthogonal* (toward inversion). It is a geometric invariant (a preserved axis
# has self-alignment near +1; an inverted one near −1), not a tunable, so it is
# fixed at 0.0 rather than calibrated.
_WAVE_SELF_ALIGNMENT_FLOOR: float = 0.0


class IdentityGateRefusal(Exception):
    """Fail-closed identity-gate refusal (ADR-0244 §2.2 / §4a).

    Raised when the operator-preservation gate cannot admit a trajectory —
    subspace leakage over bound, a value axis inverted, or a committed
    ``boundary_id`` violated — and the conjugate corrector ``C_id`` cannot
    recover alignment within its bound. The live parameters are kept unchanged
    (no silent correction — this honors the safety-pack ``no_silent_correction``
    boundary).
    """


@functools.lru_cache(maxsize=32)
def _geometry_for_axis_directions(
    directions: Tuple[Tuple[float, ...], ...]
) -> IdentityManifoldGeometry:
    """Cached operator-preservation geometry for a set of value-axis directions.

    The identity subspace is frozen at pack load (ADR-0244 governance annotation
    item 8), so the Gram matrix + inverse are computed once and memoized on the
    canonical (hashable) axis-direction key.
    """
    return IdentityManifoldGeometry.from_directions(directions)


def _geometry_for_manifold(manifold: "IdentityManifold") -> IdentityManifoldGeometry:
    directions = tuple(
        tuple(float(x) for x in getattr(axis, "direction", ()) or ())
        for axis in manifold.value_axes
    )
    return _geometry_for_axis_directions(directions)


@dataclass(frozen=True)
class ValueAxis:
    """Compatibility value-axis shape for identity-gate tests and fixtures.

    Runtime code may also pass core.physics.drive.ValueAxis instances.  The
    identity checker only requires axis_id, name, direction, and optional
    theological_note, so both shapes are accepted.
    """
    name: str
    direction: Tuple[float, ...]
    axis_id: str | None = None
    weight: float = 1.0
    theological_note: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "axis_id", self.axis_id or self.name)
        object.__setattr__(self, "direction", tuple(float(x) for x in self.direction))


@dataclass(frozen=True)
class IdentityScore:
    """Result of checking a ReasoningTrajectory against the IdentityManifold."""
    score: float          # 0.0 = full deviation, 1.0 = full alignment
    flagged: bool         # True if any axis projection fell below alignment threshold
    deviation_axes: FrozenSet[str]  # ValueAxis IDs where deviation was detected
    trajectory_id: str
    # ADR-0244 §2.2 / §4a — operator-preservation wave-field measures. Populated
    # only on the wave path (``wave_mode_active=True``); legacy defaults preserve
    # the pre-ADR-0244 IdentityScore shape and all downstream serialization
    # (the telemetry serializer emits these keys only when the wave path ran).
    wave_mode_active: bool = False
    # RMS subspace-leakage over the value axes (0.0 = every axis preserved).
    leakage_norm: float = 0.0
    # Minimum signed self-alignment ⟨aᵢ, F aᵢ F̃⟩₀ across axes (+1 preserved,
    # −1 inverted); 1.0 in legacy mode.
    min_self_alignment: float = 1.0
    # Committed boundary_ids the turn violated (intersection with the manifold's
    # boundary set); a non-empty set is a hard identity-boundary breach.
    boundary_violations: FrozenSet[str] = frozenset()
    # ADR-0246 §3.7 induced-action admit-surface measures. Populated only when the
    # ``identity_action_surface`` policy runs (``action_surface_active=True``);
    # legacy defaults keep the flag-off wave/legacy IdentityScore byte-identical.
    action_surface_active: bool = False
    d_orth: float = 0.0
    d_stab: float = 0.0

    @property
    def value(self) -> float:
        """Alias for score — primary scalar alignment value (0.0–1.0)."""
        return self.score

    @property
    def alignment(self) -> float:
        """Fraction of axes that were NOT flagged as deviating."""
        axes = self.deviation_axes
        if not axes:
            return 1.0
        return self.score

    @property
    def axes_evaluated(self) -> List[str]:
        """Sorted list of deviation_axes IDs — used by the JSONL serialiser."""
        return sorted(self.deviation_axes)


@dataclass(frozen=True)
class AxisHedge:
    """Per-axis hedge phrases for ADR-0031 score-decomposition.

    When ``IdentityCheck`` flags one or more axes as deviating, the
    assembler can call out the specific axis instead of using the
    generic hedge.  v1 is English-only; depth-language axis hedges are
    a future ADR.
    """
    strong: str
    soft: str
    qualifier: str


@dataclass(frozen=True)
class SurfacePreferences:
    """Pack-supplied surface phrasing preferences (ADR-0028).

    Drives the assembler's hedge and claim-strength decisions so that
    swapping identity packs produces visibly different surfaces on the
    same prompt.  Defaults preserve the pre-ADR-0028 behavior: the
    legacy ``HEDGE_STRONG_THRESHOLD`` / ``HEDGE_SOFT_THRESHOLD``
    constants and the canned ``"It seems that"`` / ``"Perhaps"`` hedges.

    ``claim_strength`` semantics:

    * ``"balanced"`` — no claim-strength effect outside the hedge band.
    * ``"qualified"`` — when alignment falls in
      ``[hedge_threshold_soft, qualified_band_high)``, prepend
      ``preferred_qualifier`` instead of leaving the surface bare.
    * ``"affirmative"`` — never qualify in the marginal band; let the
      assertion stand.
    """
    hedge_threshold_strong: float = 0.40
    hedge_threshold_soft: float = 0.50
    preferred_hedge_strong: str = "It seems that"
    preferred_hedge_soft: str = "Perhaps"
    claim_strength: str = "balanced"
    qualified_band_high: float = 0.75
    preferred_qualifier: str = "In some cases,"
    # ADR-0031 — per-axis hedge phrases keyed by axis_id.  When a
    # deviating axis matches an entry, the assembler uses that axis's
    # phrase instead of the generic ``preferred_hedge_*`` above.
    # Tuple of ``(axis_id, AxisHedge)`` pairs for hashability under
    # frozen dataclass semantics; pairs are kept in lex order on
    # ``axis_id`` so determinism is preserved across loads.
    axis_hedges: Tuple = ()  # Tuple[Tuple[str, AxisHedge], ...]


@dataclass(frozen=True)
class IdentityManifold:
    """Fixed geometric subspace encoding CORE's stable character."""
    value_axes: Tuple = ()  # Tuple[ValueAxis, ...]
    boundary_ids: FrozenSet[str] = frozenset()
    alignment_threshold: float = 0.45
    surface_preferences: SurfacePreferences = SurfacePreferences()


class IdentityCheck:
    """Checks a ReasoningTrajectory against an IdentityManifold.

    Canonical call style:
        IdentityCheck().check(trajectory, manifold)

    Deprecated compatibility style:
        IdentityCheck(manifold=manifold).check(trajectory)
    """

    def __init__(self, manifold: IdentityManifold | None = None) -> None:
        if manifold is not None:
            warnings.warn(
                "IdentityCheck(manifold=...) is deprecated; use "
                "IdentityCheck().check(trajectory, manifold).",
                DeprecationWarning,
                stacklevel=2,
            )
        self._manifold = manifold

    @staticmethod
    def _clamp01(value: float) -> float:
        return max(0.0, min(1.0, float(value)))

    @staticmethod
    def _mean_frame_coherence(trajectory) -> float:
        frames = getattr(trajectory, "frames", None)
        if not frames:
            return 0.0
        return sum(
            float(getattr(frame, "coherence_magnitude", 0.0)) for frame in frames
        ) / len(frames)

    @staticmethod
    def _axis_projection(axis, trajectory, scalar_score: float) -> float:
        """Deterministically project trajectory evidence onto one value axis."""
        direction = tuple(float(x) for x in getattr(axis, "direction", ()) or ())
        if not direction:
            return scalar_score
        full_l2 = math.sqrt(sum(x * x for x in direction)) or 1.0
        head_l2 = math.sqrt(sum(x * x for x in direction[:3]))
        directional_weight = head_l2 / full_l2
        frame_coherence = IdentityCheck._mean_frame_coherence(trajectory)
        coherence_term = IdentityCheck._clamp01(0.5 + (frame_coherence / 2.0))
        return IdentityCheck._clamp01(
            (0.75 * scalar_score) + (0.25 * directional_weight * coherence_term)
        )

    @staticmethod
    def _validate_wave_field(wave_field) -> np.ndarray:
        """Coerce + fail-closed-validate the live versor (ADR-0244 §4a).

        A malformed wave field (wrong shape, non-finite, wrong byte-order) is a
        typed ``ValueError`` — it never silently falls back to the legacy
        scalar-L2 path. The dual-mode fallback (see :meth:`check`) is for an
        ABSENT wave field only, not a malformed one.
        """
        F = np.ascontiguousarray(wave_field, dtype=np.float32)
        if F.dtype.byteorder not in ("<", "="):
            raise ValueError("identity gate requires little-endian float32")
        if not np.all(np.isfinite(F)):
            raise ValueError("identity gate encountered non-finite values in wave field")
        if F.shape != (N_COMPONENTS,):
            raise ValueError(
                f"identity gate wave field must have shape ({N_COMPONENTS},), got {F.shape}"
            )
        return F

    def _wave_field_score(
        self,
        wave_field,
        manifold: IdentityManifold,
        trajectory_id: str,
        boundary_violations: FrozenSet[str],
        admission_policy: "AdmissionPolicy | None" = None,
    ) -> IdentityScore:
        """Operator-preservation identity score for a live versor (ADR-0244 §2.2/§4a).

        The trajectory is a versor (an operator); we measure whether it PRESERVES
        the value subspace via its action on the axes ``F aᵢ F̃`` — subspace
        leakage (tilt toward alien dimensions) plus signed self-alignment
        (in-subspace inversion). See :mod:`core.physics.identity_manifold`.

        When ``admission_policy`` is supplied (ADR-0246 §3.7, flag-gated behind
        ``identity_action_surface``), the fuller induced-action admit surface
        (``d_orth``, ``d_stab`` vs locked ``H_id={I}``, typed residual channels)
        is additionally applied: a versor failing it folds into ``flagged`` (the
        existing ``would_violate`` refusal path abstains — admit-or-abstain, no
        corrector). When ``None`` (default) the result is byte-identical to the D4
        wave path.
        """
        F = self._validate_wave_field(wave_field)
        geometry = _geometry_for_manifold(manifold)
        leakage, self_align = geometry.axis_response(F.astype(np.float64))
        leakage_rms = float((sum(l * l for l in leakage) / len(leakage)) ** 0.5)
        min_align = float(min(self_align)) if self_align else 1.0
        score = self._clamp01(1.0 - leakage_rms)
        # The wave path uses the calibrated leakage bound γ_id (§2.4), decoupled
        # from the legacy-path / hedge-band ``alignment_threshold``. A versor is
        # flagged when its RMS subspace leakage exceeds γ_id, when any axis is
        # rotated past orthogonal (inversion, via the orientation floor), or when
        # a committed boundary_id fell. Per-axis attribution mirrors the aggregate.
        deviations = frozenset(
            str(getattr(axis, "axis_id", getattr(axis, "name", "axis")))
            for axis, leak, align in zip(manifold.value_axes, leakage, self_align)
            if leak > _WAVE_LEAKAGE_BOUND or align < _WAVE_SELF_ALIGNMENT_FLOOR
        )
        flagged = (
            leakage_rms > _WAVE_LEAKAGE_BOUND
            or min_align < _WAVE_SELF_ALIGNMENT_FLOOR
            or bool(deviations)
            or bool(boundary_violations)
        )
        # ADR-0246 §3.7 (flag-gated). When a policy is supplied, additionally apply
        # the induced-action admit surface; a refusal folds into ``flagged`` so the
        # existing ``would_violate`` egress abstains (admit-or-abstain, no
        # corrector). When absent, the fields keep legacy defaults ⇒ byte-identical.
        action_surface_active = False
        d_orth = 0.0
        d_stab = 0.0
        if admission_policy is not None:
            result = evaluate_admission(
                geometry,
                F.astype(np.float64),
                admission_policy,
                boundary_breach=bool(boundary_violations),
            )
            action_surface_active = True
            d_orth = result.d_orth
            d_stab = result.d_stab
            flagged = flagged or not result.admitted
        return IdentityScore(
            score=score,
            flagged=flagged,
            deviation_axes=deviations,
            trajectory_id=trajectory_id,
            wave_mode_active=True,
            leakage_norm=leakage_rms,
            min_self_alignment=min_align,
            boundary_violations=boundary_violations,
            action_surface_active=action_surface_active,
            d_orth=d_orth,
            d_stab=d_stab,
        )

    def check(
        self,
        trajectory,
        manifold: IdentityManifold | None = None,
        *,
        wave_field=None,
        violated_boundary_ids: FrozenSet[str] = frozenset(),
        admission_policy: "AdmissionPolicy | None" = None,
    ) -> IdentityScore:
        """Check a trajectory against the IdentityManifold (ADR-0010 / ADR-0244).

        Dual-mode (ADR-0244 §3): when a ``wave_field`` (the live versor
        ``final_state.F``) is supplied, run the metric-exact operator-preservation
        gate; otherwise fall back to the legacy scalar-L2 heuristic. A *malformed*
        wave field raises (fail-closed) — only an ABSENT one falls back.

        ``admission_policy`` (ADR-0246 §3.7, flag-gated behind
        ``identity_action_surface``) is forwarded to the wave path only; ``None``
        (default) keeps every caller byte-identical to the D4 gate.

        ``violated_boundary_ids`` (the turn's safety/ethics violated boundaries)
        is intersected with the manifold's committed ``boundary_ids``; a non-empty
        intersection is a hard identity-boundary breach (governance annotation
        item 7). Defaults empty so pre-ADR-0244 callers are byte-identical.
        """
        resolved_manifold = manifold or self._manifold
        if resolved_manifold is None:
            raise TypeError("IdentityCheck.check() requires an IdentityManifold")
        trajectory_id = str(getattr(trajectory, "trajectory_id", "legacy_trajectory"))
        boundary_violations = (
            frozenset(violated_boundary_ids) & resolved_manifold.boundary_ids
        )
        if not resolved_manifold.value_axes:
            return IdentityScore(
                score=1.0,
                flagged=bool(boundary_violations),
                deviation_axes=frozenset(),
                trajectory_id=trajectory_id,
                boundary_violations=boundary_violations,
            )
        if wave_field is not None:
            return self._wave_field_score(
                wave_field, resolved_manifold, trajectory_id, boundary_violations,
                admission_policy=admission_policy,
            )
        confidence = float(getattr(trajectory, "total_coherence_delta", 0.0))
        confidence += self._mean_frame_coherence(trajectory)
        score = self._clamp01(0.5 + (confidence / 2.0))
        deviations = frozenset(
            str(getattr(axis, "axis_id", getattr(axis, "name", "axis")))
            for axis in resolved_manifold.value_axes
            if self._axis_projection(axis, trajectory, score) < resolved_manifold.alignment_threshold
        )
        return IdentityScore(
            score=score,
            flagged=bool(deviations) or bool(boundary_violations),
            deviation_axes=deviations,
            trajectory_id=trajectory_id,
            boundary_violations=boundary_violations,
        )

    @staticmethod
    def conjugate_correct(
        score: IdentityScore, *, refuse: bool = False
    ) -> IdentityScore:
        """Conjugate corrector ``C_id`` + fail-closed egress (ADR-0244 §2.2/§4a).

        v1 policy is **admit-or-abstain**: it applies *no* corrective
        displacement to the versor (a corrector that could rewrite reasoning to
        force a low leakage score would be a "good-metric / bad-cognition"
        defect, and silently mutating the field would violate the safety-pack
        ``no_silent_correction`` boundary). When ``refuse=True`` and the score
        is a violation, it abstains — raises :class:`IdentityGateRefusal`,
        leaving the live parameters unchanged. Otherwise the score passes
        through unmodified. A bounded geometric corrective displacement is a
        future enhancement; v1 is the conservative bound (zero displacement).
        """
        if refuse and IdentityCheck.would_violate(score):
            raise IdentityGateRefusal(
                f"identity gate refused trajectory {score.trajectory_id!r}: "
                f"leakage={score.leakage_norm:.3f} min_self_align="
                f"{score.min_self_alignment:.3f} "
                f"boundary_violations={sorted(score.boundary_violations)}"
            )
        return score

    @staticmethod
    def would_violate(
        score: IdentityScore | None,
        manifold: IdentityManifold | None = None,
    ) -> bool:
        """Geometric identity-violation predicate (ADR-0010).

        Returns True when the trajectory's projection onto the IdentityManifold
        shows any value-axis falling below the manifold's alignment threshold,
        OR when the overall alignment scalar itself drops below threshold.

        This is the paraphrase-invariant defense: an identity-override attempt
        is recognised by the geometry of the field-state delta it induces, not
        by lexical surface.  Reviewers wire this in addition to (not instead
        of) any syntactic guard so the two layers remain independent.
        """
        if score is None:
            return False
        if score.flagged:
            return True
        # ADR-0244 §2.2 — a committed boundary breach or an inverted value axis
        # is a violation independent of the aggregate score. Legacy defaults
        # (empty boundary_violations, min_self_alignment=1.0) never trigger these.
        if score.boundary_violations:
            return True
        if score.min_self_alignment < _WAVE_SELF_ALIGNMENT_FLOOR:
            return True
        if manifold is not None and score.score < manifold.alignment_threshold:
            return True
        return False


@dataclass(frozen=True)
class CharacterProfile:
    """Human-readable projection of the IdentityManifold."""
    traits: Dict[str, str]
    drive_summaries: Dict[str, float]
    fatigue_index: float
    boundary_commitments: Tuple[str, ...]
    theological_grounding: Dict[str, str]

    @classmethod
    def from_manifold(
        cls,
        manifold: IdentityManifold,
        drive_summaries: Optional[Dict[str, float]] = None,
        fatigue_index: float = 0.0,
    ) -> "CharacterProfile":
        traits: Dict[str, str] = {}
        theological_grounding: Dict[str, str] = {}
        for axis in manifold.value_axes:
            traits[axis.name] = (
                f"Fixed geometric direction {axis.direction} "
                f"in versor manifold — non-negotiable."
            )
            theological_note = getattr(axis, "theological_note", "")
            if theological_note:
                theological_grounding[axis.name] = theological_note

        return cls(
            traits=traits,
            drive_summaries=drive_summaries or {
                axis.name: 0.0 for axis in manifold.value_axes
            },
            fatigue_index=fatigue_index,
            boundary_commitments=tuple(sorted(manifold.boundary_ids)),
            theological_grounding=theological_grounding,
        )


@dataclass(frozen=True)
class TurnEvent:
    """Append-only provenance record for one chat turn."""
    turn: int
    input_tokens: Tuple[str, ...]
    surface: str
    walk_surface: str
    articulation_surface: str
    dialogue_role: str
    identity_score: Optional[IdentityScore]
    cycle_cost_total: float
    vault_hits: int
    versor_condition: float
    flagged: bool
    elaboration: Optional[str] = None
    # ADR-0035 — verdicts from SafetyCheck and EthicsCheck at end-of-turn.
    # Observational at v1: surfaced for audit; no behavioral effect.
    # Typed as ``object`` to avoid coupling identity.py to packs.*.
    safety_verdict: object = None
    ethics_verdict: object = None
    # ADR-0039 — unified verdict bundle (TurnVerdicts).  Typed as
    # ``object`` to avoid coupling identity.py to chat.verdicts.
    # Carries refusal_emitted / hedge_injected remediation flags
    # alongside the three verdict surfaces.
    verdicts: object = None
    # ADR-0048 / ADR-0050 / ADR-0052 — provenance tag mirroring
    # ChatResponse.grounding_source.  One of:
    #   "vault" | "pack" | "teaching" | "none".
    # Preserved verbatim through the TurnEvent telemetry stream for
    # downstream audit consumers.
    grounding_source: str = "none"
    # Epistemic Phase 3 — first-class proposition state axes.  Strings
    # intentionally mirror core.epistemic_state enum values without
    # importing that module here, preserving identity.py's low-coupling
    # role as a shared value-type module.
    epistemic_state: str = "undetermined"
    normative_clearance: str = "unassessable"
    normative_detail: str = ""
    # ADR-0206 — Response Governance Bridge reach level for this turn.
    # The reach policy that governed the response surface, as a
    # lower_snake_case string mirroring core.response_governance.ReachLevel
    # without importing that module here (preserving identity.py's
    # low-coupling shared-value-type role).  Scaffold contract: always
    # "strict" — govern_response emits STRICT-only until the risk-reward
    # widening loop is built (ADR-0206 §3).  Default "strict" so callers
    # that omit the field stay byte-identical and conservatively governed.
    reach_level: str = "strict"
    # ADR-0153 (W-020a) — canonical SHA-256 trace hash for this turn,
    # back-stamped by ``CognitiveTurnPipeline.process`` after
    # ``compute_trace_hash`` runs.  Empty string on construction;
    # populated via dataclass.replace in ``runtime.finalize_turn_trace_hash``.
    # Discovery candidates and OOV candidates emitted during the same
    # turn read this field to populate their ``source_turn_trace``
    # provenance, replacing the prior empty-string default that left
    # the audit trail unable to identify the originating turn.
    trace_hash: str = ""
    # ADR-0072 (R5) — operator-visible register identity per turn.
    # ``register_id`` is the loaded pack id (e.g. ``"convivial_v1"``),
    # or ``""`` for the in-memory UNREGISTERED sentinel.
    # ``register_variant_id`` is the 12-char SHA-256 prefix of the
    # selected ``(opening, closing)`` discourse-marker pair, or ``""``
    # when no decoration was applied this turn (empty buckets, or empty
    # surface).  Both default to ``""`` so pre-R5 callers stay
    # byte-identical.
    register_id: str = ""
    register_variant_id: str = ""
    # ADR-0073d (L1.4) — operator-visible anchor-lens identity per turn.
    # ``anchor_lens_id`` is the loaded pack id (e.g. ``"grc_logos_v1"``),
    # or ``""`` for the in-memory UNANCHORED sentinel.
    # ``anchor_lens_mode_label`` is the engaged ``cognitive_mode_label``
    # when the lens fired on this turn's lemma (extracted from the
    # composer-emitted ``[lens(<id>):<mode>]`` annotation), or ``""``
    # when the lens was loaded but did not engage on this turn's
    # lemma, or when no lens was loaded at all.  Both default to
    # ``""`` so pre-L1.4 callers stay byte-identical.
    anchor_lens_id: str = ""
    anchor_lens_mode_label: str = ""
    # ADR-0075 (C1) — realizer slot-type guard verdict per turn.
    # ``realizer_guard_status`` is ``"ok"`` when the guard accepted
    # the candidate surface, ``"rejected"`` when one of R1/R2/R3
    # fired and the runtime routed the surface to the bounded
    # disclosure string, or ``""`` on pre-C1 events that pre-date
    # the guard hook.  ``realizer_guard_rule`` carries the rule_id
    # (one of ``"R1_no_finite_verb"``, ``"R2_aux_neg_requires_verb"``,
    # ``"R3_be_neg_requires_predicate"``) when status is
    # ``"rejected"``, otherwise ``""``.  Both default to ``""`` so
    # pre-C1 callers stay byte-identical.
    realizer_guard_status: str = ""
    realizer_guard_rule: str = ""
    # ADR-0077 (R6) — register layering boundary.  Carries the composer
    # output BEFORE any register transformation (substantive or
    # decorative).  The cognition pipeline hashes this field for
    # ``trace_hash`` when present, preserving R5's load-bearing
    # invariant — substantive register transforms must not move
    # ``trace_hash``.  Pre-R6 callers leave this as ``""``; the
    # pipeline falls back to the existing ``pre_decoration_surface``
    # source in that case (byte-identity preserved).
    register_canonical_surface: str = ""
    # ADR-0078 (Phase 1) — observational composer/graph atom
    # equivalence telemetry.  Empty defaults preserve back-compat for
    # pre-ADR-0078 callers and non-applicable turns.
    composer_graph_atom_status: str = ""
    composer_atom_set_hash: str = ""
    graph_atom_set_hash: str = ""
    composer_graph_atom_overlap_count: int = 0
