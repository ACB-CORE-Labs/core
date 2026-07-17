"""ADR-0243 §2 cognitive lifecycle — ingress → relaxation → egress (Tier-2).

Authority: docs/plans/adr-0243-implementation-plan.md §5 Phase 2.
Companion pins: tests/test_adr_0243_sketch_defect_pins.py (SD-A/SD-B/SD-C).

Gold is INDEPENDENT of the module under test: propositional truth is a
truth-table evaluator written here; ground states are cross-checked against
direct spectral projection. Deterministic fixtures only — no random spinors.
"""

from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleEngine,
    CognitiveLifecycleError,
    CrystallizationProposal,
    EgressValidationError,
    HamiltonianCompileError,
    IngressDegenerate,
    ProblemHamiltonian,
    PropositionalProblem,
    RelaxationInputError,
    RelaxationNotConverged,
    RelaxationNumericalFailure,
    assignment_component_index,
    compile_propositional,
    compile_quadratic_well,
    egress_gate,
    ingest_context,
    propositional_entails,
    relax_to_ground,
    uniform_assignment_state,
)
from core.physics.sensorium_wave_feed import fake_deterministic_packet
from core.physics.wave_energy_boundary import crystallization_for_holographic_seal
from core.physics.wave_manifold import WaveManifold

_ROOT = Path(__file__).resolve().parents[1]


def _onehot(i: int) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[i] = 1.0
    return v


def _unit(v: np.ndarray) -> np.ndarray:
    return v / np.linalg.norm(v)


# --- Independent gold ---------------------------------------------------------


def _truth_table_counts(atoms, clauses) -> list[int]:
    """Clauses falsified per assignment mask — independent of the module."""
    index = {a: i for i, a in enumerate(atoms)}
    counts = []
    for mask in range(1 << len(atoms)):
        c = 0
        for clause in clauses:
            if not any(bool(mask >> index[a] & 1) == pol for a, pol in clause):
                c += 1
        counts.append(c)
    return counts


def _entails_gold(atoms, premises, conclusion) -> bool:
    """Semantic entailment by truth table — independent of the module."""
    index = {a: i for i, a in enumerate(atoms)}
    for mask in range(1 << len(atoms)):
        model = all(
            any(bool(mask >> index[a] & 1) == pol for a, pol in clause)
            for clause in premises
        )
        if model and not any(
            bool(mask >> index[a] & 1) == pol for a, pol in conclusion
        ):
            return False
    return True


_ATOMS3 = ("a", "b", "c")
_PREMISES3 = (
    (("a", True), ("b", True)),
    (("a", False), ("c", True)),
    (("b", False), ("c", True)),
)


# --- Blade lattice ↔ assignment lattice ----------------------------------------


def test_assignment_component_map_is_bijective_and_grade_consistent():
    indices = [assignment_component_index(m) for m in range(32)]
    assert sorted(indices) == list(range(32))
    assert assignment_component_index(0) == 0  # ∅ ↔ scalar
    for i in range(5):
        assert assignment_component_index(1 << i) == 1 + i  # {e_i} ↔ vector slot
    assert assignment_component_index(0b11111) == 31  # full set ↔ pseudoscalar


def test_assignment_component_index_out_of_range_refused():
    with pytest.raises(HamiltonianCompileError):
        assignment_component_index(32)


# --- Ingress --------------------------------------------------------------------


def test_ingest_context_superposes_normalizes_and_digests():
    packets = [
        fake_deterministic_packet("audio", angle=0.3, plane=6),
        fake_deterministic_packet("vision", angle=0.4, plane=7),
    ]
    ingress = ingest_context(packets, "demo")
    assert abs(float(np.linalg.norm(ingress.psi)) - 1.0) < 1e-12
    assert ingress.modality_ids == ("audio", "vision")
    again = ingest_context(packets, "demo")
    assert ingress.packet_digest == again.packet_digest
    assert np.array_equal(ingress.psi, again.psi)
    with pytest.raises(ValueError):
        ingress.psi[0] = 5.0  # frozen read-only field


def test_ingest_context_refuses_empty_and_degenerate():
    with pytest.raises(ValueError):
        ingest_context([], "demo")  # delegation: superpose_packets refuses empty
    p = fake_deterministic_packet("audio")
    anti = {"modality_id": "anti", "coefficients": -p.coefficients}
    with pytest.raises(IngressDegenerate):
        ingest_context([p, anti], "demo")  # destructive cancellation
    with pytest.raises(IngressDegenerate):
        ingest_context([p], "   ")  # empty domain id


# --- Hamiltonian compilers -------------------------------------------------------


def test_quadratic_well_spectrum_and_refusals():
    target = _onehot(0)
    ham = compile_quadratic_well(target, curvature=2.0)
    evals, evecs = np.linalg.eigh(ham.matrix)
    assert abs(evals[0]) < 1e-12
    assert np.allclose(evals[1:], 2.0, atol=1e-12)
    assert abs(abs(float(evecs[:, 0] @ target)) - 1.0) < 1e-9
    with pytest.raises(HamiltonianCompileError):
        compile_quadratic_well(2.0 * target)  # non-unit target — no repair
    with pytest.raises(HamiltonianCompileError):
        compile_quadratic_well(target, curvature=0.0)
    bad = target.copy()
    bad[3] = np.nan
    with pytest.raises(HamiltonianCompileError):
        compile_quadratic_well(bad)


def test_problem_hamiltonian_validation_and_immutability():
    asym = np.zeros((N_COMPONENTS, N_COMPONENTS))
    asym[0, 1] = 1.0
    with pytest.raises(HamiltonianCompileError):
        ProblemHamiltonian(matrix=asym, domain="test")
    with pytest.raises(HamiltonianCompileError):
        ProblemHamiltonian(matrix=np.eye(16), domain="test")  # wrong shape
    nan_mat = np.eye(N_COMPONENTS)
    nan_mat[4, 4] = np.nan
    with pytest.raises(HamiltonianCompileError):
        ProblemHamiltonian(matrix=nan_mat, domain="test")
    ham = ProblemHamiltonian(matrix=np.eye(N_COMPONENTS), domain="test")
    assert ham.is_diagonal
    assert ham.hamiltonian_id
    with pytest.raises(ValueError):
        ham.matrix[0, 0] = 9.0  # read-only
    dense = compile_quadratic_well(_unit(_onehot(0) + _onehot(6)))
    assert not dense.is_diagonal


def test_propositional_diag_matches_independent_truth_table_gold():
    problem = PropositionalProblem(atoms=_ATOMS3, clauses=_PREMISES3)
    ham = compile_propositional(problem, penalty=1.0)
    assert ham.is_diagonal
    diag = np.diagonal(ham.matrix)
    gold = _truth_table_counts(_ATOMS3, _PREMISES3)
    mapped = set()
    for mask, count in enumerate(gold):
        idx = assignment_component_index(mask)
        mapped.add(idx)
        assert diag[idx] == float(count)
    out_of_domain = 1.0 * (len(_PREMISES3) + 1)
    for idx in set(range(N_COMPONENTS)) - mapped:
        assert diag[idx] == out_of_domain


def test_propositional_problem_validation():
    with pytest.raises(HamiltonianCompileError):
        PropositionalProblem(atoms=("a",) * 6, clauses=())  # >5 and duplicate
    with pytest.raises(HamiltonianCompileError):
        PropositionalProblem(atoms=("a", "a"), clauses=())
    with pytest.raises(HamiltonianCompileError):
        PropositionalProblem(atoms=("a",), clauses=((),))  # empty clause
    with pytest.raises(HamiltonianCompileError):
        PropositionalProblem(atoms=("a",), clauses=((("z", True),),))
    with pytest.raises(HamiltonianCompileError):
        PropositionalProblem(atoms=("a",), clauses=((("a", True), ("a", True)),))
    p1 = PropositionalProblem(atoms=("a", "b"), clauses=((("a", True),),))
    p2 = PropositionalProblem(atoms=("a", "b"), clauses=((("b", True),),))
    assert p1.problem_id and p1.problem_id != p2.problem_id
    with pytest.raises(HamiltonianCompileError):
        compile_propositional(p1, penalty=-1.0)


# --- Relaxation --------------------------------------------------------------------


def test_relaxation_decodes_quadratic_well_target_dense_path():
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    ham = compile_quadratic_well(target, curvature=1.0)
    psi0 = _unit(target + 0.5 * _onehot(2) + 0.3 * _onehot(9))
    result = relax_to_ground(psi0, ham)
    cert = result.certificate
    assert cert.converged and cert.reason == "ground_state_certified"
    assert abs(cert.ground_energy) < 1e-9
    assert abs(cert.spectral_gap - 1.0) < 1e-9
    assert cert.steps_taken >= 1
    # Independent gold: normalized spectral projection onto the ground space.
    proj = target * float(target @ psi0)
    gold = proj / np.linalg.norm(proj)
    assert np.allclose(result.psi_steady, gold, atol=1e-6)
    assert abs(abs(float(result.psi_steady @ target)) - 1.0) < 1e-8


def test_relaxation_decodes_propositional_model_set_uniform_start():
    problem = PropositionalProblem(
        atoms=("a", "b"),
        clauses=((("a", True), ("b", True)), (("a", False), ("b", True))),
    )
    gold_counts = _truth_table_counts(problem.atoms, problem.clauses)
    models = [m for m, c in enumerate(gold_counts) if c == 0]
    assert models == [2, 3]  # b=True with a free — independent check
    ham = compile_propositional(problem)
    result = relax_to_ground(uniform_assignment_state(problem), ham)
    cert = result.certificate
    assert cert.converged
    assert cert.ground_energy == 0.0  # exact on the diagonal path
    assert cert.spectral_gap == 1.0  # min nonzero falsification count × penalty
    psi = result.psi_steady
    model_components = {assignment_component_index(m) for m in models}
    for idx in range(N_COMPONENTS):
        if idx in model_components:
            assert abs(abs(psi[idx]) - 1.0 / np.sqrt(2.0)) < 1e-9
        else:
            assert abs(psi[idx]) < 1e-9


def test_relaxation_degenerate_ground_preserves_input_weighting():
    problem = PropositionalProblem(
        atoms=("a", "b"),
        clauses=((("a", True), ("b", True)), (("a", False), ("b", True))),
    )
    ham = compile_propositional(problem)
    c2, c3 = assignment_component_index(2), assignment_component_index(3)
    psi0 = np.zeros(N_COMPONENTS)
    psi0[c2], psi0[c3] = 0.8, 0.6  # unit by construction
    result = relax_to_ground(psi0, ham)
    assert abs(abs(result.psi_steady[c2]) - 0.8) < 1e-9
    assert abs(abs(result.psi_steady[c3]) - 0.6) < 1e-9


def test_relaxation_energy_is_monotone_nonincreasing():
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    psi0 = _unit(target + 0.5 * _onehot(2) + 0.3 * _onehot(9))
    result = relax_to_ground(psi0, compile_quadratic_well(target))
    assert result.certificate.energy_monotone


def test_relaxation_refuses_orthogonal_start_as_excited_eigenspace():
    ham = compile_quadratic_well(_onehot(0), curvature=1.0)
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(_onehot(6), ham)  # exactly orthogonal to the ground space
    cert = exc_info.value.certificate
    assert cert.reason == "excited_eigenspace"
    assert not cert.converged
    assert abs(cert.achieved_energy - 1.0) < 1e-9  # settled at the excited level


def test_relaxation_max_steps_exhaustion_and_nonconverged_return_path():
    diag = np.ones(N_COMPONENTS)
    diag[0], diag[1] = 0.0, 1e-6  # tiny gap — cannot converge in 3 steps
    ham = ProblemHamiltonian(matrix=np.diag(diag), domain="tiny_gap")
    psi0 = _unit(_onehot(0) + _onehot(1))
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(psi0, ham, max_steps=3)
    assert exc_info.value.certificate.reason == "max_steps_exhausted"
    result = relax_to_ground(psi0, ham, max_steps=3, require_converged=False)
    assert not result.certificate.converged


def test_relaxation_input_refusals_fail_closed():
    ham = compile_quadratic_well(_onehot(0))
    with pytest.raises(RelaxationInputError):
        relax_to_ground(0.5 * _onehot(0), ham)  # non-unit ψ0 — no hidden repair
    nan_psi = _onehot(0).copy()
    nan_psi[7] = np.nan
    with pytest.raises(RelaxationInputError):
        relax_to_ground(nan_psi, ham)
    with pytest.raises(RelaxationInputError):
        relax_to_ground(_onehot(0), ham, dt=0.0)
    with pytest.raises(RelaxationInputError):
        relax_to_ground(_onehot(0), ham, max_steps=0)
    with pytest.raises(RelaxationInputError):
        relax_to_ground(_onehot(0), ham, tol=0.0)


def test_relaxation_refuses_unresolvable_spectral_gap_but_certifies_true_ground():
    """A gap below the requested tolerance must never mis-certify (audit F4a).

    With gap 1e-7 and tol 1e-6 the energy window alone cannot separate ground
    from first-excited: the pure excited e-state passed both legacy checks with
    ZERO ground overlap. The excited-weight check refuses it — while the TRUE
    ground state (energy exactly λ0) still certifies under the same H and tol.
    """
    diag = np.ones(N_COMPONENTS)
    diag[0], diag[1] = 0.0, 1e-7
    ham = ProblemHamiltonian(matrix=np.diag(diag), domain="sub_tol_gap")
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(_onehot(1), ham, tol=1e-6)
    cert = exc_info.value.certificate
    assert cert.reason == "spectral_gap_below_tolerance"
    assert not cert.converged
    assert cert.spectral_gap == 1e-7  # exact on the diagonal path
    ground = relax_to_ground(_onehot(0), ham, tol=1e-6)
    assert ground.certificate.converged
    assert ground.certificate.reason == "ground_state_certified"


def test_relaxation_certificate_reports_rate_limiting_gap():
    """Cluster ⊆ acceptance window: the reported gap is the honest rate (audit F4b).

    A 5e-10 split sat inside the old 1e-9 degeneracy cluster, so the refusal
    certificate claimed gap=1.0 while the energy check refused that very level.
    The cluster is now capped at the acceptance window, so the certificate
    reports the true rate-limiting split.
    """
    diag = np.ones(N_COMPONENTS)
    diag[0], diag[1] = 0.0, 5e-10
    ham = ProblemHamiltonian(matrix=np.diag(diag), domain="hairline_split")
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(_onehot(1), ham)
    cert = exc_info.value.certificate
    assert cert.reason == "excited_eigenspace"
    assert cert.spectral_gap == 5e-10  # not the 1.0 the old cluster absorbed it into


def test_relaxation_dense_path_refusals_fail_closed():
    """The eigh/propagator branch must refuse honestly, not just decode happy paths.

    A projection-returning mutant with a fabricated converged certificate
    passed the suite when refusals were exercised only on the diagonal branch
    (audit F2a) — these two pin the dense branch's refusal mechanics.
    """
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    slow = compile_quadratic_well(target, curvature=1e-6)
    assert not slow.is_diagonal
    psi0 = _unit(target + 0.5 * _onehot(2))
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(psi0, slow, max_steps=3)
    assert exc_info.value.certificate.reason == "max_steps_exhausted"

    well = compile_quadratic_well(target, curvature=1.0)
    assert not well.is_diagonal
    with pytest.raises(RelaxationNotConverged) as exc_info:
        relax_to_ground(_onehot(2), well, max_steps=8)  # e2 ⊥ span(scalar, biv6)
    cert = exc_info.value.certificate
    assert cert.reason == "excited_eigenspace"
    assert not cert.converged


def test_relaxation_iterate_collapse_raises_numerical_failure():
    """Underflow of every surviving component is a typed failure, not a repair."""
    diag = np.ones(N_COMPONENTS)
    diag[0] = 0.0
    ham = ProblemHamiltonian(matrix=np.diag(diag), domain="collapse")
    psi0 = np.zeros(N_COMPONENTS)
    psi0[0], psi0[1] = 1e-13, 1.0  # ground weight below _NEAR_ZERO after one decay
    with pytest.raises(RelaxationNumericalFailure) as exc_info:
        relax_to_ground(_unit(psi0), ham, dt=100.0)
    assert exc_info.value.reason == "iterate_collapsed"


def test_relaxation_is_bit_deterministic():
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    ham = compile_quadratic_well(target)
    psi0 = _unit(target + 0.5 * _onehot(2))
    r1 = relax_to_ground(psi0, ham)
    r2 = relax_to_ground(psi0, ham)
    assert np.array_equal(r1.psi_steady, r2.psi_steady)
    assert r1.certificate.certificate_id == r2.certificate.certificate_id


# --- Propositional verdicts (exact spectrum path) -----------------------------------


@pytest.mark.parametrize(
    "conclusion",
    [
        (("c", True),),
        (("a", True),),
        (("a", True), ("b", True)),
        (("b", False),),
    ],
)
def test_entailment_matches_independent_truth_table_gold(conclusion):
    premises = PropositionalProblem(atoms=_ATOMS3, clauses=_PREMISES3)
    verdict = propositional_entails(premises, conclusion)
    assert verdict.entailed == _entails_gold(_ATOMS3, _PREMISES3, conclusion)
    assert verdict.satisfiable_premises  # these premises have models
    assert verdict.verdict_id


def test_entailment_hardcoded_canonical_verdicts():
    """Hand-verified verdicts, hardcoded — no shared code shape with the module.

    The truth-table gold above uses the same literal-evaluation idiom as the
    compiler (audit F2e), so these canonical cases pin absolute truth values.
    """
    mp = PropositionalProblem(
        atoms=("p", "q"),
        clauses=((("p", False), ("q", True)), (("p", True),)),  # p→q, p
    )
    assert propositional_entails(mp, (("q", True),)).entailed is True  # modus ponens
    assert propositional_entails(mp, (("q", False),)).entailed is False

    disj = PropositionalProblem(atoms=("p", "q"), clauses=((("p", True), ("q", True)),))
    assert propositional_entails(disj, (("p", True),)).entailed is False  # p∨q ⊭ p

    chain = PropositionalProblem(
        atoms=("p", "q", "r"),
        clauses=(
            (("p", False), ("q", True)),  # p→q
            (("q", False), ("r", True)),  # q→r
            (("p", True),),
        ),
    )
    verdict = propositional_entails(chain, (("r", True),))
    assert verdict.entailed is True  # hypothetical syllogism
    assert verdict.satisfiable_premises is True


def test_entailment_vacuous_from_unsat_premises_is_disclosed():
    premises = PropositionalProblem(
        atoms=("a",), clauses=((("a", True),), (("a", False),))
    )
    verdict = propositional_entails(premises, (("a", True),))
    assert verdict.entailed
    assert not verdict.satisfiable_premises  # ex falso — disclosed, not hidden
    assert verdict.ground_energy_premises > 0.0


def test_entailment_refuses_unknown_atom_and_empty_conclusion():
    premises = PropositionalProblem(atoms=("a",), clauses=((("a", True),),))
    with pytest.raises(HamiltonianCompileError):
        propositional_entails(premises, (("z", True),))
    with pytest.raises(HamiltonianCompileError):
        propositional_entails(premises, ())


# --- Egress ---------------------------------------------------------------------------


def _crystalline_outcome():
    engine = CognitiveLifecycleEngine()
    target = np.asarray(make_rotor_from_angle(0.3, bivector_idx=6), dtype=np.float64)
    ham = compile_quadratic_well(target)
    packets = [fake_deterministic_packet("audio", angle=0.25, plane=6)]
    return engine, engine.solve(packets, "crystal-demo", ham)


def test_egress_routes_cold_closed_versor_to_crystallization_proposal():
    _engine, outcome = _crystalline_outcome()
    verdict = outcome.verdict
    assert verdict.admitted and verdict.reason == "admitted"
    assert verdict.versor_closed
    assert verdict.energy_class.vault_candidate
    assert verdict.route == "crystallization_proposal"
    proposal = verdict.proposal
    assert proposal is not None
    assert proposal.epistemic_status == "SPECULATIVE"
    assert proposal.certificate_id == outcome.relaxation.certificate.certificate_id
    assert proposal.decision.may_speculative_seal
    json.dumps(proposal.as_dict())  # JSON-serializable artifact


def test_egress_routes_hot_state_to_readback_eligible():
    _engine, outcome = _crystalline_outcome()
    verdict = egress_gate(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        convergence_density=8,
        activation_count=8,
        current_cycle=1,
        last_activation_cycle=1,
        morphology_features={"mood": "imperative"},
    )
    assert verdict.admitted
    assert verdict.energy_class.value in ("E3", "E4")
    assert verdict.route == "readback_eligible"
    assert verdict.proposal is None


def test_egress_holds_cold_open_superposition_without_proposal():
    problem = PropositionalProblem(
        atoms=("a", "b"),
        clauses=((("a", True), ("b", True)), (("a", False), ("b", True))),
    )
    result = relax_to_ground(uniform_assignment_state(problem), compile_propositional(problem))
    verdict = egress_gate(result.psi_steady, result.certificate)
    assert verdict.admitted
    assert not verdict.versor_closed  # interference state, not a versor
    assert verdict.energy_class.vault_candidate
    assert verdict.route == "hold"  # cold but not crystalline: no proposal
    assert verdict.proposal is None


def test_egress_refuses_unnormalized_and_uncertified_states():
    _engine, outcome = _crystalline_outcome()
    cert = outcome.relaxation.certificate
    scaled = 0.5 * outcome.relaxation.psi_steady
    verdict = egress_gate(scaled, cert)
    assert not verdict.admitted and verdict.route == "refused"
    assert verdict.reason == "amplitude_density_not_unit"

    diag = np.ones(N_COMPONENTS)
    diag[0], diag[1] = 0.0, 1e-6
    slow = ProblemHamiltonian(matrix=np.diag(diag), domain="tiny_gap")
    nonconv = relax_to_ground(
        _unit(_onehot(0) + _onehot(1)), slow, max_steps=3, require_converged=False
    )
    verdict2 = egress_gate(nonconv.psi_steady, nonconv.certificate)
    assert not verdict2.admitted and verdict2.route == "refused"
    assert verdict2.reason.startswith("relaxation_not_certified")

    bad = outcome.relaxation.psi_steady.copy()
    bad[3] = np.inf
    with pytest.raises(EgressValidationError):
        egress_gate(bad, cert)
    with pytest.raises(EgressValidationError):
        egress_gate(np.zeros(16), cert)  # wrong shape — malformed, not refused


def test_egress_refuses_certificate_not_bound_to_state():
    """A borrowed converged certificate must not admit a foreign ψ (audit A).

    Before the binding, any unit state paired with any converged certificate
    was admitted and could emit a CrystallizationProposal whose psi_digest and
    certificate_id asserted a provenance that never existed.
    """
    _engine, outcome = _crystalline_outcome()
    psi = outcome.relaxation.psi_steady
    cert = outcome.relaxation.certificate
    # Independent gold for the binding: byte digest of the certified state.
    gold_digest = hashlib.sha256(
        np.ascontiguousarray(psi, dtype=np.float64).tobytes()
    ).hexdigest()[:24]
    assert cert.psi_digest == gold_digest
    assert cert.as_dict()["psi_digest"] == gold_digest

    foreign = np.asarray(make_rotor_from_angle(1.1, bivector_idx=8), dtype=np.float64)
    verdict = egress_gate(foreign, cert)  # unit closed versor, never relaxed
    assert not verdict.admitted
    assert verdict.reason == "certificate_state_mismatch"
    assert verdict.route == "refused"
    assert verdict.proposal is None


def test_egress_holds_e2_midband_without_proposal():
    """The E2 else-branch routes to hold — neither vault-cold nor readback-hot."""
    _engine, outcome = _crystalline_outcome()
    verdict = egress_gate(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        convergence_density=8,
        morphology_features={"aspect": "qatal"},
    )
    assert verdict.admitted
    assert verdict.energy_class.value == "E2"
    assert not verdict.energy_class.vault_candidate
    assert verdict.route == "hold"
    assert verdict.proposal is None


def test_crystallization_proposal_type_pins_speculative_status():
    rotor = np.asarray(make_rotor_from_angle(0.2, bivector_idx=6), dtype=np.float64)
    decision = crystallization_for_holographic_seal(rotor)
    with pytest.raises(CognitiveLifecycleError):
        CrystallizationProposal(
            proposal_id="crystal-x",
            epistemic_status="COHERENT",  # forbidden by the type itself (I-03)
            psi_digest="d",
            certificate_id="c",
            decision=decision,
        )


def test_composed_lifecycle_outcome_is_deterministic():
    _e1, o1 = _crystalline_outcome()
    _e2, o2 = _crystalline_outcome()
    assert o1.outcome_id == o2.outcome_id
    assert np.array_equal(o1.relaxation.psi_steady, o2.relaxation.psi_steady)


# --- Quarantine / structural pins -----------------------------------------------------


def test_module_imports_no_vault_surface():
    """I-03 structural pin: the lifecycle can propose, never touch a vault."""
    src = (_ROOT / "core/physics/cognitive_lifecycle.py").read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                assert "vault" not in alias.name, alias.name
        if isinstance(node, ast.ImportFrom) and node.module:
            assert "vault" not in node.module, node.module


def test_barrel_export_is_lazy_and_resolves():
    probe = (
        "import sys;"
        "import core.physics;"
        "assert 'core.physics.cognitive_lifecycle' not in sys.modules, 'eager load';"
        "core.physics.CognitiveLifecycleEngine;"
        "assert 'core.physics.cognitive_lifecycle' in sys.modules;"
        "print('ok')"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(_ROOT),
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(_ROOT), "PATH": ""},
    )
    assert result.returncode == 0, result.stderr[-2000:]
    assert result.stdout.strip().endswith("ok")


def test_versor_closure_of_steady_state_reported_via_wave_manifold():
    """Egress residual is the canonical WaveManifold measurement, not a fork."""
    _engine, outcome = _crystalline_outcome()
    manifold = WaveManifold()
    assert outcome.verdict.versor_residual == pytest.approx(
        manifold.measure_unitary_residual(outcome.relaxation.psi_steady), abs=0.0
    )
