"""ADR-0244 §2.3 topological-charge (Q_top) vacuity probe — D4 decision evidence.

ADR-0244 §2.3 proposes a conserved topological chiral charge

    Q_top = <psi I5 ~psi>_0

and an egress admit condition ``ΔQ_top = 0``, claiming "no external adversarial
input can erase or rewrite this topological charge." This eval tests that claim
against the real Cl(4,1) algebra and finds the gate **hollow** — the same failure
mode that retired the PR #19 pseudoscalar gate:

1. **Vacuous on valid states.** I5 is central in odd Cl(4,1), so
   ``psi I5 ~psi = I5·(psi ~psi)``. For any unit versor ``psi ~psi = 1`` (a pure
   scalar with no grade-5 part), hence ``Q_top = <I5>_0 = 0`` — identically, for
   *every* rotor and boost. A conserved charge that is 0 across the whole valid
   (versor) manifold carries no usable information.
2. **Redundant on invalid states.** ``Q_top = −grade5(psi ~psi)``, nonzero only
   when ``psi`` is a non-versor — which the I-05 closure residual
   ``||psi ~psi − 1||`` already flags.
3. **Conserved but empty.** ``Q_top(R psi ~R) = Q_top(psi)`` holds (it *is* a
   Spin(4,1) invariant) — but on the valid manifold the conserved value is 0.
4. **Blind to the attack it claims to stop.** An aligned identity versor and an
   adversarially-rotated one (a valid versor) both have ``Q_top = 0`` → the gate
   passes the attack, while the state has demonstrably moved (overlap < 1). The
   spectral-leakage / closure residual (ADR-0244 §2.2) is what actually separates
   them.

Verdict: do **not** wire ``ΔQ_top = 0`` as an egress admit condition; keep Q_top,
if at all, as a diagnostic derived from the closure check. Off-serving research;
deterministic; never imported by ``chat/runtime.py``.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product as gp, reverse, scalar_part
from algebra.rotor import make_rotor_from_angle

__all__ = ["q_top", "run_qtop_vacuity_probe"]

# Pseudoscalar I5 = e1 e2 e3 e4 e5 (the single grade-5 blade, component 31).
_I5 = np.zeros(N_COMPONENTS, dtype=np.float64)
_I5[31] = 1.0

_VACUITY_TOL = 1e-12


def q_top(psi: np.ndarray) -> float:
    """Topological chiral charge Q_top = <psi I5 ~psi>_0 (ADR-0244 §2.3)."""
    return scalar_part(gp(gp(np.asarray(psi, dtype=np.float64), _I5), reverse(psi)))


def _closure_residual(psi: np.ndarray) -> float:
    n = gp(np.asarray(psi, dtype=np.float64), reverse(psi)).copy()
    n[0] -= 1.0
    return float(np.linalg.norm(n))


def _grade5(psi: np.ndarray) -> float:
    return float(gp(np.asarray(psi, dtype=np.float64), reverse(psi))[31])


def _sandwich(rotor: np.ndarray, x: np.ndarray) -> np.ndarray:
    return gp(gp(rotor, x), reverse(rotor))


def _boost(angle: float, biv: int) -> np.ndarray:
    """Unit boost versor cosh(θ/2) + sinh(θ/2)·e_biv for a B²=+1 (e5-containing)
    plane. ``~R R = cosh² − sinh² = 1``."""
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = float(np.cosh(angle / 2.0))
    v[int(biv)] = float(np.sinh(angle / 2.0))
    return v


def run_qtop_vacuity_probe() -> dict[str, Any]:
    """Score Q_top's discriminating power; return a JSON-safe artifact.

    Deterministic: fixed rotor/boost panel + a seeded RNG for the non-versor
    samples. All numeric outputs are plain floats/bools.
    """
    # 1. Valid states: spatial rotors (B²=−1) and boosts through e5 (B²=+1).
    versors: list[np.ndarray] = []
    for angle in (0.3, 0.9, 1.7, 2.5):
        for biv in (6, 7, 8, 13):
            versors.append(make_rotor_from_angle(angle, biv))
    for angle in (0.5, 1.3, 2.1):
        for biv in (9, 12, 14):
            versors.append(_boost(angle, biv))
    versors.append(gp(make_rotor_from_angle(0.7, 6), _boost(1.1, 9)))
    versor_worst_abs_qtop = max(abs(q_top(v)) for v in versors)

    # 2. Non-versor unit multivectors: Q_top == −grade5(psi ~psi).
    rng = np.random.default_rng(0)
    nonversor_cases: list[dict[str, float]] = []
    nonversor_match = True
    for _ in range(4):
        m = rng.standard_normal(N_COMPONENTS)
        m = m / float(np.linalg.norm(m))
        q, g5, cr = q_top(m), _grade5(m), _closure_residual(m)
        nonversor_cases.append({"q_top": q, "neg_grade5": -g5, "closure_resid": cr})
        nonversor_match = nonversor_match and abs(q - (-g5)) < 1e-12

    # 3. Conservation under Spin(4,1) conjugation.
    R = make_rotor_from_angle(0.8, 7)
    psi_v = make_rotor_from_angle(0.5, 6)
    psi_n = rng.standard_normal(N_COMPONENTS)
    psi_n = psi_n / float(np.linalg.norm(psi_n))
    conservation = {
        "versor_before": q_top(psi_v),
        "versor_after": q_top(_sandwich(R, psi_v)),
        "nonversor_before": q_top(psi_n),
        "nonversor_after": q_top(_sandwich(R, psi_n)),
    }

    # 4. Decisive hollow-gate test: aligned identity vs adversarially-rotated one.
    identity = make_rotor_from_angle(0.4, 6)
    adversary = make_rotor_from_angle(1.5, 8)  # a large "jailbreak" rotation (valid versor)
    attacked = _sandwich(adversary, identity)
    overlap = abs(float(np.dot(identity, attacked)))
    delta_qtop = abs(q_top(identity) - q_top(attacked))
    hollow_gate = {
        "aligned_qtop": q_top(identity),
        "attacked_qtop": q_top(attacked),
        "delta_qtop": delta_qtop,
        "identity_overlap_after_attack": overlap,
        "gate_passes_attack": bool(delta_qtop < _VACUITY_TOL and overlap < 1.0),
    }

    proven_vacuous = bool(
        versor_worst_abs_qtop < _VACUITY_TOL
        and nonversor_match
        and hollow_gate["gate_passes_attack"]
    )
    return {
        "kind": "ADR0244QtopVacuityProbe",
        "vacuity_tol": _VACUITY_TOL,
        "versor_count": len(versors),
        "versor_worst_abs_qtop": versor_worst_abs_qtop,
        "nonversor_cases": nonversor_cases,
        "nonversor_qtop_equals_neg_grade5": nonversor_match,
        "conservation": conservation,
        "hollow_gate": hollow_gate,
        "proven_vacuous": proven_vacuous,
        "verdict": "hollow_gate_retire_from_egress" if proven_vacuous else "inconclusive",
    }
