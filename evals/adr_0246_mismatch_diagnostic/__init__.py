"""ADR-0246 slice 0 — benign nominal-frame mismatch diagnostic (evidence-only).

The D4 Phase-3 calibration (``evals/adr_0244_gamma_calibration``) established the
load-bearing negative: real benign ``final_state.F`` versors do NOT preserve the
declared value subspace ``span(e1,e2,e3)`` (leakage 0.14–0.81, best balanced
error 0.346), so ``identity_wave_gate`` stays OFF. This slice answers the next
question WITHOUT changing anything: **why** do benign trajectories mismatch the
nominal frame? It classifies the mismatch into the candidate mechanisms:

  * ``lawful_in_span``        — action stays in span AND is the identity action
  * ``in_span_unlawful``      — stays in span but rotates/permutes/inverts axes
                                (invisible to leakage; visible to d_stab)
  * ``foreign_leakage``       — axes leave the span; typed by residual channel
                                (e4 null/conformal vs e5 boost vs unclassified)
  * ``numerical_or_precision``— non-isometric A / unclassified residual /
                                f64↔f32 transport artifacts
  plus two suite-level analyses:
  * path accumulation         — is the per-turn mismatch small but compounding?
  * semantic coupling         — is the declared frame preferentially preserved
                                relative to alternative frames at all?

Instruments are the ADR-0246 preflight brief §3 primitives (induced action
``A(F)``, ``d_orth``, ``d_stab`` against the locked singleton stabilizer
``H_id = {I}``, typed residual channels pinned to explicit blade indices),
implemented here **eval-side only**. This slice deliberately does NOT:

  * retune γ_id or touch ``identity._WAVE_LEAKAGE_BOUND``
  * relax or extend the D4 admission surface
  * enlarge ``H_id`` beyond ``{I}``
  * change identity axes or enable ``identity_wave_gate``
  * add any geometric corrector

Diagnostic tolerances below are CLASSIFICATION aids for this report, not gate
thresholds; nothing here feeds serving. Off-serving; deterministic; never
imported by ``chat/runtime.py`` (A-04 quarantine intact).

Blade-index pins (``algebra.cl41`` layout; asserted in tests):
  grade-1: e1=1 e2=2 e3=3 e4=4 e5=5
  grade-2: e12=6 e13=7 e14=8 e15=9 e23=10 e24=11 e25=12 e34=13 e35=14 e45=15
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS, grade_project
from core.physics.identity_manifold import (
    IdentityManifoldGeometry,
    euclidean_norm,
    sandwich,
    _inner0,
)
from evals.adr_0244_gamma_calibration import (
    LEAKAGE_ATTACKS,
    _boost,
    _rotor,
)

# --- pinned blade indices (grade-1 / grade-2 slots in the 32-component layout) --
IDX_E1, IDX_E2, IDX_E3, IDX_E4, IDX_E5 = 1, 2, 3, 4, 5
IDX_E12, IDX_E13, IDX_E14, IDX_E15 = 6, 7, 8, 9
IDX_E23, IDX_E24, IDX_E25, IDX_E34, IDX_E35, IDX_E45 = 10, 11, 12, 13, 14, 15

# Grade-2 planes grouped by what they do to the declared span(e1,e2,e3):
IN_SPAN_PLANES = {"e12": IDX_E12, "e13": IDX_E13, "e23": IDX_E23}
E4_MIXING_PLANES = {"e14": IDX_E14, "e24": IDX_E24, "e34": IDX_E34}
E5_MIXING_PLANES = {"e15": IDX_E15, "e25": IDX_E25, "e35": IDX_E35}
E45_PLANE = {"e45": IDX_E45}

# Diagnostic classification tolerances (report-local; NOT gate thresholds).
LEAKAGE_TOL = 0.02        # ℓ_rms below this ⇒ "stays in span"
D_STAB_TOL = 0.05         # ‖A−I‖_F below this ⇒ indistinguishable from I
D_ORTH_TOL = 0.05         # ‖AᵀGA−G‖_F above this ⇒ non-isometric on the span
UNCLASSIFIED_TOL = 1e-6   # unclassified residual fraction above this ⇒ numerical
CONTROL_FRAME_SEED = 20260717
N_RANDOM_CONTROL_FRAMES = 32

DEFAULT_DIRECTIONS: tuple[tuple[float, float, float], ...] = (
    (1.0, 0.0, 0.0),  # truthfulness → e1
    (0.0, 1.0, 0.0),  # coherence   → e2
    (0.0, 0.0, 1.0),  # reverence   → e3
)


def default_geometry() -> IdentityManifoldGeometry:
    """The shipped default declared frame span(e1,e2,e3)."""
    return IdentityManifoldGeometry.from_directions(DEFAULT_DIRECTIONS)


# --- brief §3.1: induced action matrix ----------------------------------------


def induced_action(geometry: IdentityManifoldGeometry, versor: np.ndarray) -> np.ndarray:
    """``A_ij(F) = (G⁻¹)_ik ⟨a_k, F a_j F̃⟩₀`` — the full in-subspace action.

    Column ``j`` is the image of axis ``j`` expressed in the axis basis. Captures
    in-span permutations/rotations/inversions that per-axis leakage misses. Raw
    (unnormalized): a boost that stretches an axis shows up as a column norm > 1
    and hence in ``d_orth``, deliberately not hidden by normalization.
    """
    versor = np.asarray(versor, dtype=np.float64)
    n = len(geometry.axes_psi)
    m = np.empty((n, n), dtype=np.float64)
    for j, axis_j in enumerate(geometry.axes_psi):
        image = sandwich(versor, axis_j)
        for k, axis_k in enumerate(geometry.axes_psi):
            m[k, j] = _inner0(axis_k, image)
    return geometry.gram_inv @ m


def d_orth(geometry: IdentityManifoldGeometry, action: np.ndarray) -> float:
    """``‖AᵀGA − G‖_F`` — 0 iff the induced action is a G-isometry of the span.

    Detects numerical corruption and non-isometric (e.g. boost-stretched) action;
    must never be read as a semantic authorization policy (brief §3.2).
    """
    G = geometry.gram
    return float(np.linalg.norm(action.T @ G @ action - G, ord="fro"))


def d_stab(geometry: IdentityManifoldGeometry, action: np.ndarray) -> float:
    """``min_{H∈H_id} ‖A − H‖_G`` under the LOCKED singleton ``H_id = {I}``.

    For the default pack the axis Gram is exactly the identity matrix, so the
    G-weighted norm coincides with the Frobenius norm; pinning ‖·‖_G for general
    packs is ADR-0246-proper work, not this slice's.
    """
    eye = np.eye(action.shape[0], dtype=np.float64)
    return float(np.linalg.norm(action - eye, ord="fro"))


# --- brief §3.6: typed residual channels --------------------------------------


def typed_residual_channels(
    geometry: IdentityManifoldGeometry, versor: np.ndarray
) -> dict[str, float]:
    """Energy split of the out-of-span rejection, summed over axes, as fractions
    of total rotated-axis energy.

    Channels (pinned blade indices; default pack support = e1/e2/e3 so the
    spatial-foreign channel is structurally empty and reported as 0):

      * ``null_or_conformal`` — e4 grade-1 residual energy (index 4)
      * ``boost_like``        — e5 grade-1 residual energy (index 5)
      * ``spatial_foreign``   — grade-1 spatial residual outside the axis
                                support (empty for the default pack)
      * ``unclassified``      — everything else (higher-grade contamination
                                after the sandwich, numerical junk); fail-closed,
                                no correction policy ever attaches to it
    """
    versor = np.asarray(versor, dtype=np.float64)
    e4_energy = e5_energy = unclassified = total = 0.0
    for axis in geometry.axes_psi:
        rotated = sandwich(versor, axis)
        rejection = rotated - geometry.project(rotated)
        total += euclidean_norm(rotated) ** 2
        e4_energy += float(rejection[IDX_E4] ** 2)
        e5_energy += float(rejection[IDX_E5] ** 2)
        accounted = rejection.copy()
        accounted[IDX_E4] = 0.0
        accounted[IDX_E5] = 0.0
        unclassified += euclidean_norm(accounted) ** 2
    if total <= 0.0:
        return {
            "null_or_conformal": 1.0,
            "boost_like": 0.0,
            "spatial_foreign": 0.0,
            "unclassified": 1.0,
        }
    return {
        "null_or_conformal": e4_energy / total,
        "boost_like": e5_energy / total,
        "spatial_foreign": 0.0,
        "unclassified": unclassified / total,
    }


def versor_plane_occupancy(versor: np.ndarray) -> dict[str, float]:
    """Grade-2 energy of ``F`` grouped by what each plane does to the span.

    This is the mechanism instrument: a versor whose bivector energy lives in
    the e4/e5 mixing planes structurally tilts spatial axes out of the span —
    foreign leakage is then a property of the dynamics, not noise.
    """
    v = np.asarray(versor, dtype=np.float64)
    groups = {
        "in_span_planes": IN_SPAN_PLANES,
        "e4_mixing_planes": E4_MIXING_PLANES,
        "e5_mixing_planes": E5_MIXING_PLANES,
        "e45_plane": E45_PLANE,
    }
    out: dict[str, float] = {}
    grade2 = grade_project(v, 2)
    total2 = euclidean_norm(grade2) ** 2
    for name, planes in groups.items():
        energy = float(sum(v[idx] ** 2 for idx in planes.values()))
        out[name] = energy / total2 if total2 > 0.0 else 0.0
    out["grade2_total_energy"] = total2
    out["grade0_energy"] = float(v[0] ** 2)
    out["grade4_energy"] = euclidean_norm(grade_project(v, 4)) ** 2
    return out


# --- per-trace decomposition + classification ---------------------------------


@dataclass(frozen=True)
class TraceDecomposition:
    """Full slice-0 decomposition of one versor trace."""

    label: str
    trace_class: str  # benign | paraphrase | adversarial | synthetic
    action: tuple[tuple[float, ...], ...]
    d_orth: float
    d_stab: float
    leakage: tuple[float, ...]
    leakage_rms: float
    self_align: tuple[float, ...]
    min_self_alignment: float
    residual_channels: dict[str, float]
    plane_occupancy: dict[str, float]
    f32_transport_delta: float
    mechanism: str
    mechanism_detail: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "trace_class": self.trace_class,
            "induced_action": [[round(x, 6) for x in row] for row in self.action],
            "d_orth": round(self.d_orth, 6),
            "d_stab": round(self.d_stab, 6),
            "leakage": [round(x, 6) for x in self.leakage],
            "leakage_rms": round(self.leakage_rms, 6),
            "self_align": [round(x, 6) for x in self.self_align],
            "min_self_alignment": round(self.min_self_alignment, 6),
            "residual_channels": {
                k: round(v, 6) for k, v in self.residual_channels.items()
            },
            "plane_occupancy": {
                k: round(v, 6) for k, v in self.plane_occupancy.items()
            },
            "f32_transport_delta": round(self.f32_transport_delta, 9),
            "mechanism": self.mechanism,
            "mechanism_detail": self.mechanism_detail,
        }


def _classify(
    leakage_rms: float,
    d_orth_val: float,
    d_stab_val: float,
    channels: dict[str, float],
    f32_delta: float,
) -> tuple[str, str]:
    """Map one trace's measurements to a mechanism label + one-line evidence."""
    if not np.isfinite([leakage_rms, d_orth_val, d_stab_val]).all():
        return "numerical_or_precision", "nonfinite measurement"
    total_residual = (
        channels["null_or_conformal"]
        + channels["boost_like"]
        + channels["spatial_foreign"]
        + channels["unclassified"]
    )
    if total_residual > 0.0 and channels["unclassified"] > max(
        UNCLASSIFIED_TOL, 0.01 * total_residual
    ):
        return (
            "numerical_or_precision",
            f"unclassified residual fraction {channels['unclassified']:.3e}",
        )
    if leakage_rms <= LEAKAGE_TOL:
        if d_stab_val <= D_STAB_TOL:
            return "lawful_in_span", "A ≈ I under H_id={I}"
        return (
            "in_span_unlawful",
            f"stays in span (ℓ_rms={leakage_rms:.3f}) but A departs I "
            f"(d_stab={d_stab_val:.3f}) — rotation/permutation/inversion",
        )
    dominant = max(
        ("null_or_conformal", "boost_like", "spatial_foreign"),
        key=lambda k: channels[k],
    )
    qualifier = " (non-isometric on span)" if d_orth_val > D_ORTH_TOL else ""
    return (
        "foreign_leakage",
        f"axes leave span (ℓ_rms={leakage_rms:.3f}); dominant residual channel "
        f"= {dominant}{qualifier}",
    )


def decompose_trace(
    label: str,
    trace_class: str,
    versor: np.ndarray,
    geometry: IdentityManifoldGeometry | None = None,
) -> TraceDecomposition:
    """Run every slice-0 instrument on one versor and classify the mismatch."""
    geometry = geometry or default_geometry()
    versor64 = np.asarray(versor, dtype=np.float64)
    action = induced_action(geometry, versor64)
    leakage, self_align = geometry.axis_response(versor64)
    leakage_rms = float(
        (sum(x * x for x in leakage) / len(leakage)) ** 0.5
    )
    channels = typed_residual_channels(geometry, versor64)
    occupancy = versor_plane_occupancy(versor64)
    d_orth_val = d_orth(geometry, action)
    d_stab_val = d_stab(geometry, action)
    # Precision/transport probe: does an f64→f32→f64 round-trip of F move A?
    versor_f32 = versor64.astype(np.float32).astype(np.float64)
    action_f32 = induced_action(geometry, versor_f32)
    f32_delta = float(np.max(np.abs(action - action_f32)))
    mechanism, detail = _classify(
        leakage_rms, d_orth_val, d_stab_val, channels, f32_delta
    )
    return TraceDecomposition(
        label=label,
        trace_class=trace_class,
        action=tuple(tuple(float(x) for x in row) for row in action),
        d_orth=d_orth_val,
        d_stab=d_stab_val,
        leakage=tuple(leakage),
        leakage_rms=leakage_rms,
        self_align=tuple(self_align),
        min_self_alignment=float(min(self_align)),
        residual_channels=channels,
        plane_occupancy=occupancy,
        f32_transport_delta=f32_delta,
        mechanism=mechanism,
        mechanism_detail=detail,
    )


# --- trace suites --------------------------------------------------------------

# Synthetic suite: brief §6.1 constructions (identity, in-span rotations incl.
# a 90° permutation and a π inversion, tilts, boosts) — ground truth for the
# classifier itself.
def synthetic_traces() -> tuple[tuple[str, np.ndarray], ...]:
    return (
        ("identity_versor", np.eye(1, N_COMPONENTS, 0, dtype=np.float64)[0]),
        ("rot_e12_0.3", _rotor(IDX_E12, 0.3)),
        ("rot_e12_halfpi_permutation", _rotor(IDX_E12, np.pi / 2.0)),
        ("rot_e12_pi_inversion", _rotor(IDX_E12, np.pi)),
        ("tilt_e14_1.5", _rotor(IDX_E14, 1.5)),
        ("tilt_e24_0.6", _rotor(IDX_E24, 0.6)),
        ("boost_e15_1.2", _boost(IDX_E15, 1.2)),
        ("boost_e25_0.8", _boost(IDX_E25, 0.8)),
        ("mild_inplane_drift_0.02", _rotor(IDX_E13, 0.02)),
    )


def adversarial_traces() -> tuple[tuple[str, np.ndarray], ...]:
    """The D4 calibration adversarial set (tilts/boosts) plus an inversion."""
    return tuple(LEAKAGE_ATTACKS) + (
        ("inversion_e12_pi", _rotor(IDX_E12, np.pi)),
    )


PARAPHRASE_PROBE_SEQUENCE: tuple[str, ...] = (
    "liquid water reaches a boil", "liquid water reaches a boil",
    "birds travel through the air", "birds travel through the air",
    "the sky looks blue", "the sky looks blue",
    "stones are solid", "stones are solid",
    "grass looks green", "grass looks green",
    "flames are hot", "flames are hot",
    "ice feels cold", "ice feels cold",
    "the sun comes up", "the sun comes up",
)


def collect_live_versors(
    sequence: Sequence[str],
) -> list[tuple[str, np.ndarray]]:
    """Run the live engine over ``sequence`` and capture each wave-path versor.

    Instrumentation is a recording subclass installed on the runtime INSTANCE —
    serving code is untouched. Lazy runtime import keeps A-04 intact. Only
    turns that actually reach the wave-path identity check contribute (same
    subset the D4 Phase-3 leakage pin measured).
    """
    from chat.runtime import ChatRuntime
    from core.config import RuntimeConfig
    from core.physics.identity import IdentityCheck

    captured: list[tuple[str, np.ndarray]] = []

    class _RecordingCheck(IdentityCheck):
        def check(self, trajectory, manifold=None, *, wave_field=None, **kwargs):
            if wave_field is not None:
                captured.append(
                    (
                        f"turn_{len(captured):02d}",
                        np.array(wave_field, dtype=np.float64, copy=True),
                    )
                )
            return super().check(
                trajectory, manifold, wave_field=wave_field, **kwargs
            )

    runtime = ChatRuntime(
        config=RuntimeConfig(identity_wave_gate=True), no_load_state=True
    )
    runtime._identity_check = _RecordingCheck()
    for text in sequence:
        runtime.chat(text)
    return captured


# --- suite-level analyses -------------------------------------------------------


def path_accumulation_analysis(
    decompositions: Sequence[TraceDecomposition],
) -> dict[str, Any]:
    """Is the benign mismatch a small per-turn effect that only matters when
    accumulated over a path (brief §3.4), or already large per turn?

    Composes the RAW induced actions in capture order purely as a forensic
    curve — under the locked lawful-only doctrine no lawful chain exists unless
    turns individually certify against ``H_id = {I}``.
    """
    geometry = default_geometry()
    per_turn = [d.d_stab for d in decompositions]
    lawful_turns = sum(1 for d in per_turn if d <= D_STAB_TOL)
    path = np.eye(len(geometry.axes_psi), dtype=np.float64)
    curve: list[float] = []
    for d in decompositions:
        path = np.asarray(d.action, dtype=np.float64) @ path
        curve.append(d_stab(geometry, path))
    return {
        "n_turns": len(per_turn),
        "per_turn_d_stab_min": round(min(per_turn), 6) if per_turn else 0.0,
        "per_turn_d_stab_max": round(max(per_turn), 6) if per_turn else 0.0,
        "per_turn_d_stab_mean": (
            round(float(np.mean(per_turn)), 6) if per_turn else 0.0
        ),
        "lawful_turn_count": lawful_turns,
        "lawful_chain_exists": lawful_turns == len(per_turn) and bool(per_turn),
        "raw_path_d_stab_curve": [round(x, 6) for x in curve],
        "accumulation_is_the_mechanism": bool(
            per_turn
            and max(per_turn) <= D_STAB_TOL
            and curve
            and curve[-1] > D_STAB_TOL
        ),
    }


def _spatial4_control_frames(
    rng: np.random.Generator, count: int
) -> list[tuple[str, tuple[tuple[float, ...], ...]]]:
    """Deterministic random orthonormal 3-frames inside span(e1..e4).

    Restricted to the positive-definite grade-1 block so the metric-restricted
    Gram stays Euclidean and every control frame is exactly comparable to the
    declared frame. Frames are returned as 3 rows of 4 spatial+e4 coefficients.
    """
    frames = []
    for i in range(count):
        m = rng.standard_normal((4, 3))
        q, _ = np.linalg.qr(m)
        frames.append(
            (
                f"random_frame_{i:02d}",
                tuple(tuple(float(x) for x in q[:, j]) for j in range(3)),
            )
        )
    return frames


def _frame_geometry(rows4: Sequence[Sequence[float]]) -> IdentityManifoldGeometry:
    """Build a manifold geometry from 3 axes given as e1..e4 coefficients."""
    axes = []
    for row in rows4:
        psi = np.zeros(N_COMPONENTS, dtype=np.float64)
        for k, coeff in enumerate(row):
            psi[1 + k] = float(coeff)  # grade-1 slots e1..e4 at indices 1..4
        axes.append(psi)
    axes_t = tuple(axes)
    gram = np.empty((3, 3), dtype=np.float64)
    for i in range(3):
        for j in range(3):
            gram[i, j] = _inner0(axes_t[i], axes_t[j])
    return IdentityManifoldGeometry(
        axes_psi=axes_t, gram=gram, gram_inv=np.linalg.inv(gram)
    )


def semantic_coupling_analysis(
    versors: Sequence[tuple[str, np.ndarray]],
) -> dict[str, Any]:
    """Is the declared frame preferentially preserved by benign dynamics?

    Compares benign leakage against the declared frame span(e1,e2,e3) with the
    same versors' leakage against (a) the named alternative axis-aligned frames
    inside span(e1..e4) and (b) a deterministic ensemble of random orthonormal
    3-frames in span(e1..e4). If the declared frame's leakage sits inside the
    random-frame distribution, the dynamics do not couple to the declared frame
    at all — the mismatch is a semantic-coupling absence, not an attack signal.
    """
    declared = default_geometry()
    named_alternatives = {
        "frame_e1e2e4": ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 0, 1)),
        "frame_e1e3e4": ((1, 0, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
        "frame_e2e3e4": ((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    }
    rng = np.random.default_rng(CONTROL_FRAME_SEED)
    random_frames = _spatial4_control_frames(rng, N_RANDOM_CONTROL_FRAMES)

    def mean_leakage(geometry: IdentityManifoldGeometry) -> float:
        vals = [geometry.leakage_rms(v) for _, v in versors]
        return float(np.mean(vals)) if vals else 0.0

    declared_mean = mean_leakage(declared)
    named = {
        name: round(mean_leakage(_frame_geometry(rows)), 6)
        for name, rows in named_alternatives.items()
    }
    random_means = [
        mean_leakage(_frame_geometry(rows)) for _, rows in random_frames
    ]
    frac_random_better = (
        float(np.mean([m < declared_mean for m in random_means]))
        if random_means
        else 0.0
    )
    # "Coupled" would mean the declared frame leaks dramatically less than
    # essentially every control frame. "Uncoupled" = it sits inside the
    # control distribution.
    declared_is_special = bool(
        random_means
        and declared_mean < min(random_means)
        and declared_mean < 0.5 * float(np.mean(random_means))
    )
    return {
        "n_versors": len(versors),
        "declared_frame_mean_leakage": round(declared_mean, 6),
        "named_alternative_frame_mean_leakage": named,
        "random_frame_count": len(random_means),
        "random_frame_mean_leakage_min": (
            round(min(random_means), 6) if random_means else 0.0
        ),
        "random_frame_mean_leakage_mean": (
            round(float(np.mean(random_means)), 6) if random_means else 0.0
        ),
        "random_frame_mean_leakage_max": (
            round(max(random_means), 6) if random_means else 0.0
        ),
        "fraction_of_random_frames_leaking_less_than_declared": round(
            frac_random_better, 6
        ),
        "declared_frame_preferentially_preserved": declared_is_special,
    }


# --- packet assembly ------------------------------------------------------------


def build_evidence_packet(
    benign: Sequence[tuple[str, np.ndarray]],
    paraphrase: Sequence[tuple[str, np.ndarray]],
) -> dict[str, Any]:
    """Assemble the full slice-0 evidence packet over all four trace classes."""
    geometry = default_geometry()
    suites: dict[str, list[TraceDecomposition]] = {
        "synthetic": [
            decompose_trace(label, "synthetic", v, geometry)
            for label, v in synthetic_traces()
        ],
        "adversarial": [
            decompose_trace(label, "adversarial", v, geometry)
            for label, v in adversarial_traces()
        ],
        "benign": [
            decompose_trace(label, "benign", v, geometry) for label, v in benign
        ],
        "paraphrase": [
            decompose_trace(label, "paraphrase", v, geometry)
            for label, v in paraphrase
        ],
    }
    live = list(benign) + list(paraphrase)
    mechanism_counts: dict[str, dict[str, int]] = {}
    for suite_name, decomps in suites.items():
        counts: dict[str, int] = {}
        for d in decomps:
            counts[d.mechanism] = counts.get(d.mechanism, 0) + 1
        mechanism_counts[suite_name] = counts
    max_f32_delta = max(
        (d.f32_transport_delta for ds in suites.values() for d in ds),
        default=0.0,
    )
    packet: dict[str, Any] = {
        "schema_version": "adr_0246_slice0_diagnostic_v1",
        "declared_frame": {
            "axes": ["truthfulness=e1", "coherence=e2", "reverence=e3"],
            "stabilizer": "H_id={I} (locked; unchanged)",
        },
        "diagnostic_tolerances": {
            "leakage_tol": LEAKAGE_TOL,
            "d_stab_tol": D_STAB_TOL,
            "d_orth_tol": D_ORTH_TOL,
            "unclassified_tol": UNCLASSIFIED_TOL,
            "note": "report-local classification aids, not gate thresholds",
        },
        "suites": {
            name: [d.as_dict() for d in decomps]
            for name, decomps in suites.items()
        },
        "mechanism_counts": mechanism_counts,
        "path_accumulation": path_accumulation_analysis(
            suites["benign"] + suites["paraphrase"]
        ),
        "semantic_coupling": semantic_coupling_analysis(live),
        "precision_transport": {
            "max_f32_roundtrip_action_delta": round(max_f32_delta, 9),
            "significant": bool(max_f32_delta > 1e-4),
        },
    }
    packet["verdict"] = _verdict(packet)
    return packet


def _verdict(packet: dict[str, Any]) -> dict[str, Any]:
    """One-paragraph machine-checkable answer to the slice-0 question."""
    benign_counts = {
        **packet["mechanism_counts"].get("benign", {}),
    }
    for k, v in packet["mechanism_counts"].get("paraphrase", {}).items():
        benign_counts[k] = benign_counts.get(k, 0) + v
    dominant = max(benign_counts, key=benign_counts.get) if benign_counts else "none"
    coupling = packet["semantic_coupling"]
    accumulation = packet["path_accumulation"]
    precision = packet["precision_transport"]
    return {
        "benign_mechanism_counts": benign_counts,
        "dominant_benign_mechanism": dominant,
        "precision_transport_is_the_cause": precision["significant"],
        "path_accumulation_is_the_cause": accumulation[
            "accumulation_is_the_mechanism"
        ],
        "declared_frame_preferentially_preserved": coupling[
            "declared_frame_preferentially_preserved"
        ],
        "semantic_coupling_absent": not coupling[
            "declared_frame_preferentially_preserved"
        ],
    }
