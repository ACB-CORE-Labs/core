"""ADR-0246 §6.1/§6.2 synthetic geometric + path/holonomy eval suite (scaffold).

A runnable, deterministic harness that constructs every case in the preflight
§6.1 synthetic geometric table and §6.2 path/holonomy table, runs the pure
ADR-0246 primitives (induced action ``A(F)``, ``d_orth``, ``d_stab`` vs the locked
singleton ``H_id={I}``, typed residual channels, lawful-only path ledger), and
checks each against its expected geometric signature. Every case reports
``{name, checks, passed}`` and the suite reports an overall ``passed``.

Scope (bounded scaffold draft — NOT an accepted ADR):
  * Off-serving: imports only ``algebra`` + ``core.physics.identity_{manifold,action}``;
    never ``chat.runtime`` (A-04 quarantine).
  * ``H_id={I}`` only; refused turns are break markers, never soft-projected ``I``;
    the path composes lawful actions only — never the raw product.
  * No ``C_id`` corrector; admit-or-abstain only.
  * The path-suite ε values are UNCERTIFIED PLACEHOLDERS (see
    ``PLACEHOLDER_EPSILON_*``): D4 Phase 3 certified only ``γ_id``; ε_turn/ε_session
    are not yet calibrated. They exist here solely to exercise the mechanism and
    are flagged in the run log. Do NOT read them as policy.

No discrimination report, no claims about what the axes *mean* — that is
explicitly deferred to Opus/human review (see the slice-1 scaffold notes).
"""

from __future__ import annotations

from typing import Any, Callable

import numpy as np

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_manifold import (
    IdentityManifoldGeometry,
    ManifoldConditioningError,
    MalformedVersorError,
)
from core.physics.identity_action import (
    IdentityChainScope,
    PathBudget,
    advance_identity_path,
    raw_path_product,
    stabilizer_defect_for_versor,
)

# grade-2 bivector plane indices (grade-2 block starts at index 6)
_E12, _E13, _E14, _E15, _E23, _E24, _E25 = 6, 7, 8, 9, 10, 11, 12

# --- UNCERTIFIED PLACEHOLDERS (flagged; not policy) ---------------------------
# D4 Phase 3 certified γ_id only. ε_turn / ε_session are NOT calibrated; these
# illustrative values merely exercise the two-level path budget mechanism.
PLACEHOLDER_EPSILON_TURN: float = 0.1
PLACEHOLDER_EPSILON_SESSION: float = 0.3
# "clearly nonzero" marker for the >0 rows in the §6.1 table (not a threshold).
_NONZERO = 0.05
_ZERO = 1e-9


def default_geometry() -> IdentityManifoldGeometry:
    """The shipped default declared frame span(e1,e2,e3), Gram = I3."""
    return IdentityManifoldGeometry.from_directions(
        ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    )


def rotor(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cos(theta / 2.0)
    r[biv] = np.sin(theta / 2.0)
    return r


def boost(biv: int, theta: float) -> np.ndarray:
    r = np.zeros(N_COMPONENTS, dtype=np.float64)
    r[0] = np.cosh(theta / 2.0)
    r[biv] = np.sinh(theta / 2.0)
    return r


def identity_versor() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def _case(name: str, checks: dict[str, bool]) -> dict[str, Any]:
    return {"name": name, "checks": checks, "passed": all(checks.values())}


def _expect_raises(name: str, fn: Callable[[], Any], exc: type[BaseException]) -> dict[str, Any]:
    raised = False
    try:
        fn()
    except exc:
        raised = True
    except Exception:  # wrong exception type is a failure
        raised = False
    return _case(name, {f"raises_{exc.__name__}": raised})


# --- §6.1 synthetic geometric suite -------------------------------------------


def run_geometric_suite(geometry: IdentityManifoldGeometry | None = None) -> list[dict[str, Any]]:
    geometry = geometry or default_geometry()
    cases: list[dict[str, Any]] = []

    # Identity versor → A≈I, ℓ≈0, s≈+1, d_orth≈0, d_stab≈0
    v = identity_versor()
    a = geometry.induced_action(v)
    leak, self_align = geometry.axis_response(v)
    cases.append(_case("identity_versor", {
        "A_is_identity": bool(np.allclose(a, np.eye(3), atol=1e-12)),
        "leakage_zero": max(leak) < _ZERO,
        "self_align_plus_one": min(self_align) > 1.0 - _ZERO,
        "d_orth_zero": geometry.orthogonality_defect(v) < _ZERO,
        "d_stab_zero": stabilizer_defect_for_versor(geometry, v) < _ZERO,
    }))

    # In-plane π inversion of e1/e2 → ℓ≈0, s(e1)≈-1, s(e3)≈+1, d_stab>0
    v = rotor(_E12, np.pi)
    leak, self_align = geometry.axis_response(v)
    cases.append(_case("inplane_pi_inversion_e12", {
        "leakage_zero": max(leak) < _ZERO,
        "self_align_e1_minus_one": self_align[0] < -1.0 + _ZERO,
        "self_align_e2_minus_one": self_align[1] < -1.0 + _ZERO,
        "self_align_e3_plus_one": self_align[2] > 1.0 - _ZERO,
        "d_stab_positive": stabilizer_defect_for_versor(geometry, v) > _NONZERO,
    }))

    # In-plane 90° permutation e1→e2 → ℓ≈0, s(e1)≈0, d_stab>0
    v = rotor(_E12, np.pi / 2.0)
    leak, self_align = geometry.axis_response(v)
    cases.append(_case("inplane_90deg_permutation_e12", {
        "leakage_zero": max(leak) < _ZERO,
        "self_align_e1_zero": abs(self_align[0]) < _ZERO,
        "self_align_e2_zero": abs(self_align[1]) < _ZERO,
        "d_stab_positive": stabilizer_defect_for_versor(geometry, v) > _NONZERO,
    }))

    # Mild in-plane drift step → small d_stab (per-turn passes ε_turn placeholder)
    v = rotor(_E12, 0.02)
    d_stab = stabilizer_defect_for_versor(geometry, v)
    leak, _ = geometry.axis_response(v)
    cases.append(_case("mild_inplane_drift_e12_0.02", {
        "leakage_zero": max(leak) < _ZERO,
        "d_stab_small_but_positive": _ZERO < d_stab < PLACEHOLDER_EPSILON_TURN,
    }))

    # Alien tilt e14 → ℓ>0, null_or_conformal channel fires, boost channel ≈0
    v = rotor(_E14, 1.5)
    ch = geometry.typed_residual_energy(v)
    cases.append(_case("alien_tilt_e14_1.5", {
        "leakage_positive": geometry.leakage_rms(v) > _NONZERO,
        "null_or_conformal_fires": ch["null_or_conformal"] > _NONZERO,
        "boost_like_zero": ch["boost_like"] < _ZERO,
        "unclassified_clean": ch["unclassified"] < _ZERO,
    }))

    # Boost component (e5) → ℓ,s normalized in range, boost channel fires, d_orth>0
    v = boost(_E15, 1.0)
    ch = geometry.typed_residual_energy(v)
    leak, self_align = geometry.axis_response(v)
    cases.append(_case("boost_e15_1.0", {
        "leakage_in_unit_range": 0.0 <= max(leak) <= 1.0,
        "self_align_in_range": all(-1.0 - _ZERO <= s <= 1.0 + _ZERO for s in self_align),
        "boost_like_fires": ch["boost_like"] > _NONZERO,
        "null_or_conformal_zero": ch["null_or_conformal"] < _ZERO,
        "d_orth_positive": geometry.orthogonality_defect(v) > _NONZERO,
    }))

    # Near-singular Gram (near-parallel axes) → ManifoldConditioningError at build
    cases.append(_expect_raises(
        "near_singular_gram",
        lambda: IdentityManifoldGeometry.from_directions(
            ((1.0, 0.0, 0.0), (1.0, 1e-9, 0.0), (0.0, 0.0, 1.0))
        ),
        ManifoldConditioningError,
    ))

    # Malformed F → MalformedVersorError (NaN and wrong-shape)
    nan_v = identity_versor()
    nan_v[0] = np.nan
    cases.append(_expect_raises(
        "malformed_f_nan", lambda: geometry.induced_action(nan_v), MalformedVersorError
    ))
    cases.append(_expect_raises(
        "malformed_f_wrong_shape",
        lambda: geometry.induced_action(np.ones(7, dtype=np.float64)),
        MalformedVersorError,
    ))
    return cases


# --- §6.2 path / holonomy suite -----------------------------------------------


def _scope(pack: str = "packA") -> IdentityChainScope:
    return IdentityChainScope(
        pack_content_digest=pack,
        geometry_version="geomV1",
        policy_version="polV1(PLACEHOLDER_epsilons)",
        session_id="sess1",
        biography_epoch=None,
    )


def run_path_suite(geometry: IdentityManifoldGeometry | None = None) -> list[dict[str, Any]]:
    geometry = geometry or default_geometry()
    budget = PathBudget(
        epsilon_turn=PLACEHOLDER_EPSILON_TURN,
        epsilon_session=PLACEHOLDER_EPSILON_SESSION,
    )
    gram = geometry.gram
    ident = geometry.induced_action(identity_versor())
    cases: list[dict[str, Any]] = []

    # Sequence of lawful near-I turns → A_path near I; no false path refusal
    ledger = None
    for _ in range(20):
        ledger, _ = advance_identity_path(ledger, _scope(), ident, gram, budget)
    cases.append(_case("lawful_near_identity_sequence", {
        "path_near_identity": bool(np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)),
        "session_admit": ledger.session_admit,
        "no_breaks": ledger.break_count == 0,
        "composed_20": ledger.composed_turn_count == 20,
    }))

    # Small in-plane rotations each < ε_turn → path eventually breaches ε_session
    small = geometry.induced_action(rotor(_E12, 0.05))
    ledger = None
    all_turns_lawful = True
    for _ in range(40):
        ledger, rec = advance_identity_path(ledger, _scope(), small, gram, budget)
        all_turns_lawful = all_turns_lawful and rec["lawful"]
        if not ledger.session_admit:
            break
    cases.append(_case("small_rotations_accumulate_to_session_refusal", {
        "each_turn_lawful": all_turns_lawful,
        "session_refused": not ledger.session_admit,
        "path_d_stab_exceeds_session": ledger.d_stab_path > PLACEHOLDER_EPSILON_SESSION,
    }))

    # Interleaved refuse + admit → refused turns break, excluded, raw recorded
    big = geometry.induced_action(rotor(_E12, np.pi / 2.0))
    seq = [ident, big, ident, big, ident]
    ledger = None
    breaks_pattern = []
    for a in seq:
        ledger, rec = advance_identity_path(ledger, _scope(), a, gram, budget)
        breaks_pattern.append(rec["path_break"])
    cases.append(_case("interleaved_refuse_admit", {
        "composed_3": ledger.composed_turn_count == 3,
        "breaks_2": ledger.break_count == 2,
        "break_pattern": breaks_pattern == [False, True, False, True, False],
    }))

    # Pack digest change → hard break, new chain_id, old path not continued
    ledger, _ = advance_identity_path(None, _scope("packA"), ident, gram, budget)
    ledger, _ = advance_identity_path(ledger, _scope("packA"), small, gram, budget)
    id_a, drifted = ledger.chain_id, ledger.a_path_lawful.copy()
    ledger, rec = advance_identity_path(ledger, _scope("packB"), ident, gram, budget)
    cases.append(_case("hard_break_on_pack_change", {
        "hard_break": rec["hard_break"],
        "new_chain_id": ledger.chain_id != id_a,
        "old_path_not_continued": not np.allclose(ledger.a_path_lawful, drifted),
        "fresh_chain": ledger.composed_turn_count == 1 and ledger.break_count == 0,
    }))

    # Raw product ≠ lawful product when a refused turn is present (forensic)
    seq = [ident, big, ident]
    ledger = None
    for a in seq:
        ledger, _ = advance_identity_path(ledger, _scope(), a, gram, budget)
    raw = raw_path_product(seq)
    cases.append(_case("raw_product_differs_from_lawful", {
        "raw_neq_lawful": not np.allclose(raw, ledger.a_path_lawful),
        "lawful_excludes_refused": bool(np.allclose(ledger.a_path_lawful, np.eye(3), atol=1e-12)),
    }))
    return cases


def build_suite_report() -> dict[str, Any]:
    geometry = default_geometry()
    geometric = run_geometric_suite(geometry)
    path = run_path_suite(geometry)
    all_cases = geometric + path
    return {
        "schema_version": "adr_0246_geometric_suite_v1",
        "declared_frame": ["truthfulness=e1", "coherence=e2", "reverence=e3"],
        "stabilizer": "H_id={I} (locked)",
        "placeholders": {
            "epsilon_turn": PLACEHOLDER_EPSILON_TURN,
            "epsilon_session": PLACEHOLDER_EPSILON_SESSION,
            "note": "UNCERTIFIED — D4 Phase 3 certified only gamma_id; ε not calibrated",
        },
        "geometric_suite": geometric,
        "path_suite": path,
        "case_count": len(all_cases),
        "passed_count": sum(1 for c in all_cases if c["passed"]),
        "all_passed": all(c["passed"] for c in all_cases),
    }
