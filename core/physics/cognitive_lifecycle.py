"""ADR-0243 §2 — Wave-Field Cognitive Lifecycle (Tier-2, OFF-SERVING).

Ingress → Hamiltonian-well relaxation → egress, on the Cl(4,1) coefficient
space. Implements the ADR-0243 lifecycle honestly, with the §3 reference
prototype's defects corrected (they are pinned in
``tests/test_adr_0243_sketch_defect_pins.py``; deviations D-1…D-5 are recorded
in ``docs/plans/adr-0243-implementation-plan.md`` §4):

* **Ingress** delegates to :mod:`core.physics.sensorium_wave_feed`
  (superposition) and normalizes ONCE at this module's owned construction
  boundary (deviation D-3; master-plan doctrine note — no hot-path repair).
* **Relaxation** is the dissipative imaginary-time semigroup
  ``ψ ← normalize(exp(−(H−λ0)·dt)·ψ)`` — deterministic power iteration that
  provably converges to the ground eigenspace at a rate set by the spectral
  gap (deviation D-1). The sketch's ``exp(H·I·t)`` loop oscillates and cannot
  relax (pin SD-B). Convergence is certified, never assumed (deviation D-2):
  the certificate carries the exact ground energy from the spectrum, the
  achieved Rayleigh energy, the eigen-residual, the gap (certification
  requires the gap be resolvable at the requested tolerance), and a byte
  digest of the certified state binding the evidence to that exact ψ.
* **Egress** composes the existing organs — unit amplitude density,
  the certificate↔state binding check (a borrowed certificate refuses),
  :meth:`WaveManifold.measure_unitary_residual` (the ADR's R_GoldTether;
  reported, and REQUIRED only on the crystallization route where states must
  be closed versors), ADR-0006 energy classes via
  :func:`core.physics.wave_energy_boundary.energy_profile_from_wave`, and the
  E0/E1 crystallization policy via
  :func:`~core.physics.wave_energy_boundary.crystallization_for_holographic_seal`.
  Gating a multi-mode superposition on versor closure would reject every
  legitimate interference state (the dual of pin SD-A), so versor closure
  routes rather than admits.
* **No mutation**: cold states emit a :class:`CrystallizationProposal`
  (``epistemic_status="SPECULATIVE"`` enforced by the type) — never a vault
  write (deviation D-5 / cohesion I-03). This module imports no vault store.

Problem domains (v1, plan §5 Phase 2 — two checkable domains only):

* ``quadratic_well`` — H = curvature·(Id − ψ₀ψ₀ᵀ): ground space is span(ψ₀);
  relaxation decodes the target from any non-orthogonal start.
* ``propositional`` — the Cl(4,1) blade lattice IS the assignment lattice of
  ≤ 5 atoms: blade {e_{i₁}…e_{i_k}} ↔ assignment with exactly those atoms
  True. Clauses compile to a DIAGONAL penalty Hamiltonian counting falsified
  clauses per assignment; the ground space is the span of satisfying
  assignments and relaxation decodes the model set. Verdicts (SAT /
  entailment) read the exact ground energy of the same H — integer counts
  scaled by ``penalty``, no floating eigensolve on the diagonal path.

Honesty note (D-2): the propositional compiler enumerates the ≤ 32 assignment
components — this is exact small-domain decoding, not a scalability claim.
Its value is falsifiability: verdicts are scored against independent gold
(truth tables here; ``generate.proof_chain`` ROBDD in the Phase 4 eval).

Serve quarantine (A-04): never imported by ``chat/runtime.py``; exported
lazily via the ``core.physics`` barrel; enforced by
``tests/test_serve_quarantine_transitive.py`` and the cohesion suite.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS, geometric_product
from core.physics.energy import EnergyClass, EnergyProfile, FieldEnergyOperator
from core.physics.sensorium_wave_feed import PacketLike, _coerce_packet, superpose_packets
from core.physics.wave_energy_boundary import (
    CrystallizationDecision,
    crystallization_for_holographic_seal,
    energy_profile_from_wave,
)
from core.physics.wave_manifold import WaveManifold

_NEAR_ZERO = 1e-12
_UNIT_TOL = 1e-9
_EPSILON_DRIFT = 1e-6
_MAX_ATOMS = 5
_SPECULATIVE = "SPECULATIVE"


# --- Typed fail-closed errors --------------------------------------------------


class CognitiveLifecycleError(ValueError):
    """Fail-closed lifecycle refusal with structured disclosure."""

    def __init__(self, reason: str, **disclosure: Any) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"cognitive_lifecycle refused [{reason}]: {self.disclosure}")


class IngressDegenerate(CognitiveLifecycleError):
    """Superposed context has no resolvable amplitude (no confabulated field)."""


class HamiltonianCompileError(CognitiveLifecycleError):
    """Problem → Hamiltonian compilation refused (malformed constraints)."""


class RelaxationInputError(CognitiveLifecycleError):
    """Relaxer input refused (shape / non-finite / non-unit ψ0). No repair."""


class RelaxationNumericalFailure(CognitiveLifecycleError):
    """Non-finite value produced during relaxation (mirrors OptimizationFailure)."""


class RelaxationNotConverged(CognitiveLifecycleError):
    """Relaxation did not certify the ground state; carries the certificate."""

    def __init__(self, reason: str, certificate: "RelaxationCertificate", **disclosure: Any) -> None:
        self.certificate = certificate
        super().__init__(reason, **disclosure)


class EgressValidationError(CognitiveLifecycleError):
    """Egress gate refused to evaluate a malformed state (shape / non-finite)."""


# --- Content addressing ----------------------------------------------------------


def _le_f64_bytes(arr: np.ndarray) -> bytes:
    """Canonical little-endian float64 bytes for cross-platform-stable digests.

    ADR-0244 §2.7 byte-order guard: coerce to little-endian float64 before
    hashing so the digest is identical on every little-endian platform and
    deterministic on big-endian ones. Byte-wise a no-op on the M1/x86 targets,
    but an explicit contract rather than an implicit platform assumption — and a
    coercion, not an ``assert`` (the assert form is stripped under ``-O``).
    """
    contiguous = np.ascontiguousarray(arr, dtype=np.float64)
    return contiguous.astype(np.dtype("<f8"), copy=False).tobytes()


def _content_id(payload: Mapping[str, Any]) -> str:
    # Full 256-bit digest (64 hex). No ``default=str``: a non-serializable
    # payload element fails closed with a typed ``TypeError`` at the
    # serialization boundary rather than silently collapsing distinct objects
    # onto identical string forms (ADR-0244 §2.7).
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _psi_digest(psi: np.ndarray) -> str:
    # Full 256-bit digest over canonical little-endian float64 bytes — no
    # 96-bit truncation (birthday-collision floor at 2^48), no platform
    # byte-order ambiguity (ADR-0244 §2.7).
    return hashlib.sha256(_le_f64_bytes(psi)).hexdigest()


def _as_psi(x: np.ndarray, name: str, *, error: type[CognitiveLifecycleError]) -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise error("bad_shape", name=name, shape=list(np.shape(x)))
    if not np.all(np.isfinite(arr)):
        raise error("non_finite", name=name)
    return arr


# --- Blade lattice ↔ assignment lattice (propositional substrate) -----------------
#
# Subset S ⊆ {0..4} of basis-vector indices ↔ the canonical blade e_{i1}…e_{ik}
# (ascending product) ↔ the truth assignment with exactly the atoms in S True.
# The component index and sign are DERIVED from the algebra's own geometric
# product — no hand-maintained table to drift from algebra/cl41.


def _vector_onehot(i: int) -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[1 + i] = 1.0  # basis vector e_i lives at component 1+i (0-indexed atoms)
    return v


def _build_subset_component_map() -> tuple[tuple[int, ...], tuple[float, ...]]:
    indices: list[int] = []
    signs: list[float] = []
    for mask in range(1 << _MAX_ATOMS):
        blade = np.zeros(N_COMPONENTS, dtype=np.float64)
        blade[0] = 1.0
        for i in range(_MAX_ATOMS):
            if mask & (1 << i):
                blade = geometric_product(blade, _vector_onehot(i))
        support = np.nonzero(np.abs(blade) > 0.5)[0]
        if support.size != 1:
            raise RuntimeError(f"blade map degenerate for mask {mask}: support={support}")
        idx = int(support[0])
        indices.append(idx)
        signs.append(float(np.sign(blade[idx])))
    if len(set(indices)) != (1 << _MAX_ATOMS):
        raise RuntimeError("blade map is not a bijection onto components")
    return tuple(indices), tuple(signs)


_SUBSET_COMPONENT, _SUBSET_SIGN = _build_subset_component_map()


def assignment_component_index(assignment_mask: int) -> int:
    """Component index of the blade encoding *assignment_mask* (bit i = atom i True)."""
    if not (0 <= int(assignment_mask) < (1 << _MAX_ATOMS)):
        raise HamiltonianCompileError("assignment_mask_out_of_range", mask=int(assignment_mask))
    return _SUBSET_COMPONENT[int(assignment_mask)]


# --- Ingress ----------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class IngressWavePacket:
    """Normalized ingress field ψ_context with provenance (ADR-0243 §2.1)."""

    psi: np.ndarray
    domain_id: str
    modality_ids: tuple[str, ...]
    packet_digest: str

    def __post_init__(self) -> None:
        arr = _as_psi(self.psi, "ψ_context", error=IngressDegenerate)
        arr = arr.copy()
        arr.setflags(write=False)
        object.__setattr__(self, "psi", arr)


def ingest_context(packets: Sequence[PacketLike], domain_id: str) -> IngressWavePacket:
    """Superpose modality packets and normalize at the owned construction boundary.

    Delegates superposition to :func:`sensorium_wave_feed.superpose_packets`
    (which refuses empty input). Normalization here is the ONE owned
    construction boundary of the lifecycle (D-3) — a degenerate superposition
    (destructive cancellation below ``1e-12``) is refused, never zero-filled.
    """
    domain = str(domain_id).strip()
    if not domain:
        raise IngressDegenerate("empty_domain_id")
    total = superpose_packets(packets)
    norm = float(np.linalg.norm(total))
    if not np.isfinite(norm) or norm < _NEAR_ZERO:
        raise IngressDegenerate("degenerate_superposition", norm=norm, n_packets=len(packets))
    psi = (total / norm).astype(np.float64)
    modality_ids = tuple(_coerce_packet(p).modality_id for p in packets)
    return IngressWavePacket(
        psi=psi,
        domain_id=domain,
        modality_ids=modality_ids,
        packet_digest=_content_id(
            {"psi": _psi_digest(psi), "domain": domain, "modalities": list(modality_ids)}
        ),
    )


# --- Problem Hamiltonians -----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ProblemHamiltonian:
    """Typed, content-addressed constraint operator H (symmetric, 32×32, f64).

    ``matrix`` is validated (shape, finiteness, symmetry ≤ 1e-12) and frozen
    read-only; asymmetric input is refused, never symmetrized (no repair).
    """

    matrix: np.ndarray
    domain: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
    hamiltonian_id: str = ""
    is_diagonal: bool = False

    def __post_init__(self) -> None:
        arr = np.asarray(self.matrix, dtype=np.float64)
        if arr.shape != (N_COMPONENTS, N_COMPONENTS):
            raise HamiltonianCompileError("bad_shape", shape=list(arr.shape))
        if not np.all(np.isfinite(arr)):
            raise HamiltonianCompileError("non_finite_matrix")
        asym = float(np.max(np.abs(arr - arr.T)))
        if asym > 1e-12:
            raise HamiltonianCompileError("not_symmetric", max_asymmetry=asym)
        arr = arr.copy()
        arr.setflags(write=False)
        diagonal = bool(np.count_nonzero(arr - np.diag(np.diagonal(arr))) == 0)
        meta = dict(self.metadata)
        object.__setattr__(self, "matrix", arr)
        object.__setattr__(self, "metadata", meta)
        object.__setattr__(self, "is_diagonal", diagonal)
        object.__setattr__(
            self,
            "hamiltonian_id",
            _content_id(
                {
                    "domain": str(self.domain),
                    "matrix_sha": hashlib.sha256(_le_f64_bytes(arr)).hexdigest(),
                    "metadata": {k: str(v) for k, v in sorted(meta.items())},
                }
            ),
        )


def compile_quadratic_well(target_psi: np.ndarray, *, curvature: float = 1.0) -> ProblemHamiltonian:
    """H = curvature·(Id − ψ₀ψ₀ᵀ): ground space span(ψ₀) at energy 0, gap = curvature."""
    target = _as_psi(target_psi, "target_psi", error=HamiltonianCompileError)
    c = float(curvature)
    if not np.isfinite(c) or c <= 0.0:
        raise HamiltonianCompileError("curvature_not_positive", curvature=c)
    norm_err = abs(float(np.linalg.norm(target)) - 1.0)
    if norm_err > _UNIT_TOL:
        raise HamiltonianCompileError("target_not_unit", norm_residual=norm_err)
    matrix = c * (np.eye(N_COMPONENTS, dtype=np.float64) - np.outer(target, target))
    return ProblemHamiltonian(
        matrix=matrix,
        domain="quadratic_well",
        metadata={"curvature": c, "target_digest": _psi_digest(target)},
    )


PropositionalLiteral = tuple[str, bool]
Clause = tuple[PropositionalLiteral, ...]


@dataclass(frozen=True, slots=True)
class PropositionalProblem:
    """CNF over ≤ 5 atoms; atom i ↔ basis vector e_i (order as given)."""

    atoms: tuple[str, ...]
    clauses: tuple[Clause, ...]
    problem_id: str = ""

    def __post_init__(self) -> None:
        atoms = tuple(str(a) for a in self.atoms)
        if not (1 <= len(atoms) <= _MAX_ATOMS):
            raise HamiltonianCompileError("atom_count_out_of_range", n_atoms=len(atoms))
        if len(set(atoms)) != len(atoms) or any(not a.strip() for a in atoms):
            raise HamiltonianCompileError("atoms_not_unique_nonempty", atoms=list(atoms))
        clauses: list[Clause] = []
        for ci, clause in enumerate(self.clauses):
            lits = tuple((str(a), bool(p)) for a, p in clause)
            if not lits:
                raise HamiltonianCompileError("empty_clause", clause_index=ci)
            if len(set(lits)) != len(lits):
                raise HamiltonianCompileError("duplicate_literal", clause_index=ci)
            for atom, _ in lits:
                if atom not in atoms:
                    raise HamiltonianCompileError("unknown_atom", clause_index=ci, atom=atom)
            clauses.append(lits)
        object.__setattr__(self, "atoms", atoms)
        object.__setattr__(self, "clauses", tuple(clauses))
        object.__setattr__(
            self,
            "problem_id",
            _content_id({"atoms": list(atoms), "clauses": [list(c) for c in clauses]}),
        )

    @property
    def n_atoms(self) -> int:
        return len(self.atoms)


def _falsification_counts(problem: PropositionalProblem) -> tuple[int, ...]:
    """Clauses falsified per assignment mask (exact integer counts)."""
    k = problem.n_atoms
    index = {a: i for i, a in enumerate(problem.atoms)}
    counts = [0] * (1 << k)
    for mask in range(1 << k):
        for clause in problem.clauses:
            satisfied = False
            for atom, polarity in clause:
                bit = bool(mask & (1 << index[atom]))
                if bit == polarity:
                    satisfied = True
                    break
            if not satisfied:
                counts[mask] += 1
    return tuple(counts)


def compile_propositional(problem: PropositionalProblem, *, penalty: float = 1.0) -> ProblemHamiltonian:
    """Diagonal penalty Hamiltonian: diag[component(a)] = penalty · #clauses falsified by a.

    Out-of-domain components (blades using vectors beyond the atom set) get
    ``penalty·(len(clauses)+1)`` — strictly above every in-domain value, so
    the ground space is always inside the assignment lattice. Satisfiable iff
    the exact ground energy is 0.
    """
    p = float(penalty)
    if not np.isfinite(p) or p <= 0.0:
        raise HamiltonianCompileError("penalty_not_positive", penalty=p)
    counts = _falsification_counts(problem)
    diag = np.full(N_COMPONENTS, p * float(len(problem.clauses) + 1), dtype=np.float64)
    for mask, count in enumerate(counts):
        diag[_SUBSET_COMPONENT[mask]] = p * float(count)
    return ProblemHamiltonian(
        matrix=np.diag(diag),
        domain="propositional",
        metadata={"problem_id": problem.problem_id, "penalty": p, "n_atoms": problem.n_atoms},
    )


def uniform_assignment_state(problem: PropositionalProblem) -> np.ndarray:
    """Unit uniform superposition over the problem's assignment components.

    Uses the algebra-derived blade signs so every assignment basis state enters
    with amplitude +1/√(2^k) on the CANONICAL blade orientation.
    """
    k = problem.n_atoms
    psi = np.zeros(N_COMPONENTS, dtype=np.float64)
    amp = 1.0 / float(np.sqrt(1 << k))
    for mask in range(1 << k):
        psi[_SUBSET_COMPONENT[mask]] = amp * _SUBSET_SIGN[mask]
    return psi


# --- Relaxation (imaginary-time semigroup; deviation D-1) ---------------------------


@dataclass(frozen=True, slots=True)
class RelaxationCertificate:
    """Convergence evidence for one relaxation run (D-2: certified, not assumed).

    ``psi_digest`` binds the certificate to the exact final state it describes
    (byte digest of ψ_steady) — the egress gate refuses a certificate presented
    with any other state, so convergence evidence cannot be borrowed.
    """

    hamiltonian_id: str
    domain: str
    dt: float
    tol: float
    max_steps: int
    steps_taken: int
    ground_energy: float
    achieved_energy: float
    spectral_gap: float
    eigen_residual: float
    energy_monotone: bool
    converged: bool
    reason: str
    psi_digest: str
    certificate_id: str = ""

    def __post_init__(self) -> None:
        payload = {
            "hamiltonian_id": self.hamiltonian_id,
            "domain": self.domain,
            "dt": repr(float(self.dt)),
            "tol": repr(float(self.tol)),
            "max_steps": int(self.max_steps),
            "steps_taken": int(self.steps_taken),
            "ground_energy": repr(float(self.ground_energy)),
            "achieved_energy": repr(float(self.achieved_energy)),
            "spectral_gap": repr(float(self.spectral_gap)),
            "eigen_residual": repr(float(self.eigen_residual)),
            "energy_monotone": bool(self.energy_monotone),
            "converged": bool(self.converged),
            "reason": self.reason,
            "psi_digest": self.psi_digest,
        }
        object.__setattr__(self, "certificate_id", _content_id(payload))

    def as_dict(self) -> dict[str, Any]:
        return {
            "hamiltonian_id": self.hamiltonian_id,
            "domain": self.domain,
            "dt": float(self.dt),
            "tol": float(self.tol),
            "max_steps": int(self.max_steps),
            "steps_taken": int(self.steps_taken),
            "ground_energy": float(self.ground_energy),
            "achieved_energy": float(self.achieved_energy),
            "spectral_gap": float(self.spectral_gap),
            "eigen_residual": float(self.eigen_residual),
            "energy_monotone": bool(self.energy_monotone),
            "converged": bool(self.converged),
            "reason": self.reason,
            "psi_digest": self.psi_digest,
            "certificate_id": self.certificate_id,
        }


@dataclass(frozen=True, slots=True)
class RelaxationResult:
    psi_steady: np.ndarray
    certificate: RelaxationCertificate

    def __post_init__(self) -> None:
        arr = np.asarray(self.psi_steady, dtype=np.float64).copy()
        arr.setflags(write=False)
        object.__setattr__(self, "psi_steady", arr)


def _spectral_gap(evals: np.ndarray, tol: float) -> tuple[float, float, float]:
    """(λ0, gap, energy_tol) with the degeneracy cluster ⊆ the acceptance window.

    Capping ``deg_tol`` at ``energy_tol`` keeps the certificate internally
    consistent: an eigenvalue counted into the ground cluster is never refused
    by the energy check, and ``gap`` is the honest rate-limiting gap (a split
    just above ``energy_tol`` is reported, not absorbed).
    """
    lam0 = float(evals[0])
    energy_tol = float(tol) * max(1.0, abs(lam0))
    deg_tol = min(1e-9 * max(1.0, abs(lam0)) + 1e-12, energy_tol)
    above = evals[evals > lam0 + deg_tol]
    gap = float(above[0] - lam0) if above.size else 0.0
    return lam0, gap, energy_tol


def relax_to_ground(
    psi0: np.ndarray,
    hamiltonian: ProblemHamiltonian,
    *,
    dt: float = 1.0,
    max_steps: int = 512,
    tol: float = 1e-10,
    require_converged: bool = True,
) -> RelaxationResult:
    """Deterministic imaginary-time relaxation to the ground eigenspace of H.

    ``ψ ← normalize(exp(−(H−λ0)·dt)·ψ)`` — normalized power iteration on the
    dissipative semigroup (D-1; the λ0 shift only rescales, dynamics
    identical). Along the iteration the Rayleigh energy is non-increasing (a
    falsifiable physics invariant, recorded as ``energy_monotone``).

    Converged means ``‖Hψ − Eψ‖ ≤ tol`` AND ``E − λ0 ≤ tol·max(1,|λ0|)`` AND,
    when the spectral gap is positive, ``E − λ0 ≤ tol·gap`` — the excited-space
    weight of ψ is bounded by ``(E−λ0)/gap``, so the third check certifies
    ground weight ≥ 1−tol instead of trusting an energy window the spectrum
    may not resolve. A start orthogonal to the ground space settles in an
    excited eigenspace with a small residual and is refused as
    ``excited_eigenspace``; a state whose energy sits inside the window while
    the gap is below the requested resolution is refused as
    ``spectral_gap_below_tolerance``, never mis-certified. Degenerate ground
    spaces (gap 0 after clustering) converge to the normalized projection of
    ψ0 (input-dependent decoding within the solution space). Fail-closed:
    non-finite input/iterates and non-unit ψ0 raise typed errors; nothing is
    repaired.
    """
    psi = _as_psi(psi0, "ψ0", error=RelaxationInputError).copy()
    unit_err = abs(float(np.linalg.norm(psi)) - 1.0)
    if unit_err > _UNIT_TOL:
        raise RelaxationInputError("psi0_not_normalized", norm_residual=unit_err)
    dt_f = float(dt)
    if not np.isfinite(dt_f) or dt_f <= 0.0:
        raise RelaxationInputError("dt_not_positive", dt=dt_f)
    steps = int(max_steps)
    if steps < 1:
        raise RelaxationInputError("max_steps_not_positive", max_steps=steps)
    tol_f = float(tol)
    if not np.isfinite(tol_f) or tol_f <= 0.0:
        raise RelaxationInputError("tol_not_positive", tol=tol_f)

    H_mat = hamiltonian.matrix
    if hamiltonian.is_diagonal:
        # Exact spectrum from the diagonal — no LAPACK on the propositional path.
        diag = np.diagonal(H_mat).copy()
        lam0, gap, energy_tol = _spectral_gap(np.sort(diag), tol_f)
        decay = np.exp(-(diag - lam0) * dt_f)

        def step(v: np.ndarray) -> np.ndarray:
            return decay * v

        def apply_h(v: np.ndarray) -> np.ndarray:
            return diag * v

    else:
        evals_full, evecs_full = np.linalg.eigh(H_mat)
        lam0, gap, energy_tol = _spectral_gap(evals_full, tol_f)
        propagator = evecs_full @ np.diag(np.exp(-(evals_full - lam0) * dt_f)) @ evecs_full.T

        def step(v: np.ndarray) -> np.ndarray:
            return propagator @ v

        def apply_h(v: np.ndarray) -> np.ndarray:
            return H_mat @ v

    def _measure(v: np.ndarray) -> tuple[float, float]:
        hv = apply_h(v)
        energy = float(v @ hv)
        residual = float(np.linalg.norm(hv - energy * v))
        return energy, residual

    def _certified(energy: float, residual: float) -> bool:
        near_ground = (energy - lam0) <= energy_tol
        gap_resolved = gap == 0.0 or (energy - lam0) <= tol_f * gap
        return residual <= tol_f and near_ground and gap_resolved

    energies: list[float] = []
    energy, residual = _measure(psi)
    energies.append(energy)
    steps_taken = 0
    for _ in range(steps):
        if _certified(energy, residual):
            break
        psi = step(psi)
        if not np.all(np.isfinite(psi)):
            # Defensive only: decay/propagator entries are exp(−x) with x ≥ 0.
            raise RelaxationNumericalFailure("non_finite_iterate", steps_taken=steps_taken)
        norm = float(np.linalg.norm(psi))
        if norm < _NEAR_ZERO:
            raise RelaxationNumericalFailure("iterate_collapsed", steps_taken=steps_taken)
        psi = psi / norm
        steps_taken += 1
        energy, residual = _measure(psi)
        energies.append(energy)

    monotone = all(
        energies[i + 1] <= energies[i] + 1e-9 * max(1.0, abs(energies[i]))
        for i in range(len(energies) - 1)
    )
    residual_ok = residual <= tol_f
    at_ground = (energy - lam0) <= energy_tol
    converged = _certified(energy, residual)
    if converged:
        reason = "ground_state_certified"
    elif residual_ok and not at_ground:
        reason = "excited_eigenspace"
    elif residual_ok:
        reason = "spectral_gap_below_tolerance"
    else:
        reason = "max_steps_exhausted"

    certificate = RelaxationCertificate(
        hamiltonian_id=hamiltonian.hamiltonian_id,
        domain=hamiltonian.domain,
        dt=dt_f,
        tol=tol_f,
        max_steps=steps,
        steps_taken=steps_taken,
        ground_energy=lam0,
        achieved_energy=energy,
        spectral_gap=gap,
        eigen_residual=residual,
        energy_monotone=monotone,
        converged=converged,
        reason=reason,
        psi_digest=_psi_digest(psi),
    )
    if not converged and require_converged:
        raise RelaxationNotConverged(
            reason,
            certificate,
            achieved_energy=energy,
            ground_energy=lam0,
            eigen_residual=residual,
        )
    return RelaxationResult(psi_steady=psi, certificate=certificate)


# --- Propositional verdicts (exact spectrum path) -----------------------------------


@dataclass(frozen=True, slots=True)
class PropositionalEntailmentVerdict:
    """Entailment via UNSAT(premises ∧ ¬conclusion) on the SAME compiled H family.

    ``satisfiable_premises=False`` discloses vacuous (ex falso) entailment.
    Distinct name from ``generate.proof_chain.EntailmentVerdict`` (the ROBDD
    flagship) — that is the independent gold this domain is scored against.
    """

    entailed: bool
    satisfiable_premises: bool
    ground_energy_premises: float
    ground_energy_augmented: float
    penalty: float
    verdict_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "verdict_id",
            _content_id(
                {
                    "entailed": bool(self.entailed),
                    "satisfiable_premises": bool(self.satisfiable_premises),
                    "ge_premises": repr(float(self.ground_energy_premises)),
                    "ge_augmented": repr(float(self.ground_energy_augmented)),
                    "penalty": repr(float(self.penalty)),
                }
            ),
        )


def _in_domain_ground_energy(problem: PropositionalProblem, *, penalty: float) -> float:
    counts = _falsification_counts(problem)
    return float(penalty) * float(min(counts))


def propositional_entails(
    premises: PropositionalProblem,
    conclusion: Clause,
    *,
    penalty: float = 1.0,
) -> PropositionalEntailmentVerdict:
    """premises ⊨ (⋁ conclusion) iff premises ∧ ¬conclusion is UNSAT.

    ¬conclusion compiles to unit clauses over the SAME atom set (unknown atoms
    are refused — the v1 domain is closed-vocabulary). The verdict reads exact
    integer ground energies of the compiled Hamiltonians; relaxation is the
    constructive decoder of the same operators, so what is asserted and what
    relaxes are one object.
    """
    p = float(penalty)
    if not np.isfinite(p) or p <= 0.0:
        raise HamiltonianCompileError("penalty_not_positive", penalty=p)
    lits = tuple((str(a), bool(pol)) for a, pol in conclusion)
    if not lits:
        raise HamiltonianCompileError("empty_conclusion")
    for atom, _ in lits:
        if atom not in premises.atoms:
            raise HamiltonianCompileError("unknown_atom_in_conclusion", atom=atom)
    negation_units: tuple[Clause, ...] = tuple(((atom, not pol),) for atom, pol in lits)
    augmented = PropositionalProblem(
        atoms=premises.atoms,
        clauses=premises.clauses + negation_units,
    )
    ge_premises = _in_domain_ground_energy(premises, penalty=p)
    ge_augmented = _in_domain_ground_energy(augmented, penalty=p)
    return PropositionalEntailmentVerdict(
        entailed=bool(ge_augmented > 0.0),
        satisfiable_premises=bool(ge_premises == 0.0),
        ground_energy_premises=ge_premises,
        ground_energy_augmented=ge_augmented,
        penalty=p,
    )


# --- Egress (ADR-0243 §2.3) ----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class CrystallizationProposal:
    """Proposal-only cold-state artifact (D-5 / I-03). NEVER a vault write.

    ``epistemic_status`` is pinned to ``"SPECULATIVE"`` by the type itself;
    ratification and any COHERENT promotion live outside this module, behind
    the one-mutation-path.
    """

    proposal_id: str
    epistemic_status: str
    psi_digest: str
    certificate_id: str
    decision: CrystallizationDecision
    adr_refs: tuple[str, ...] = ("ADR-0243", "ADR-0241")

    def __post_init__(self) -> None:
        if self.epistemic_status != _SPECULATIVE:
            raise CognitiveLifecycleError(
                "proposal_must_be_speculative", epistemic_status=self.epistemic_status
            )

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "epistemic_status": self.epistemic_status,
            "psi_digest": self.psi_digest,
            "certificate_id": self.certificate_id,
            "decision": self.decision.as_dict(),
            "adr_refs": list(self.adr_refs),
        }


@dataclass(frozen=True, slots=True)
class EgressVerdict:
    """Composed egress verdict (ADR-0243 §2.3, corrected per pin SD-A).

    ``admitted`` = unit amplitude density + a converged certificate BOUND to
    this exact ψ (``certificate.psi_digest`` must match the presented state
    byte-for-byte; a borrowed certificate refuses as
    ``certificate_state_mismatch``, so no proposal can pair a state with
    foreign convergence evidence). ``versor_closed`` (the ADR's R_GoldTether
    ≤ ε) ROUTES — it is required on the crystallization path (only closed
    versors may SPECULATIVE-seal) and reported on all paths; demanding it of
    multi-mode superpositions would reject every legitimate interference
    state.
    """

    admitted: bool
    reason: str
    route: str  # refused | readback_eligible | crystallization_proposal | hold
    unit_norm_residual: float
    versor_residual: float
    versor_closed: bool
    energy_class: EnergyClass
    energy_profile: EnergyProfile
    proposal: CrystallizationProposal | None


def egress_gate(
    psi_steady: np.ndarray,
    certificate: RelaxationCertificate,
    *,
    epsilon_drift: float = _EPSILON_DRIFT,
    manifold: WaveManifold | None = None,
    operator: FieldEnergyOperator | None = None,
    **energy_kwargs: object,
) -> EgressVerdict:
    """Thermodynamic egress: admit → classify → route (E0/E1 cold, E3/E4 hot).

    Structural energy axes (convergence, activation, aspect) are
    caller-supplied via ``energy_kwargs`` — never invented here; the
    coherence residual is measured on ψ by the energy boundary itself.
    Malformed states raise; legitimate bad states get ``admitted=False``.
    """
    arr = _as_psi(psi_steady, "ψ_steady", error=EgressValidationError)
    m = manifold if manifold is not None else WaveManifold(epsilon_drift=float(epsilon_drift))
    unit_norm_residual = abs(float(np.linalg.norm(arr)) - 1.0)
    versor_residual = float(m.measure_unitary_residual(arr))
    versor_closed = versor_residual <= float(epsilon_drift)
    psi_dig = _psi_digest(arr)
    profile = energy_profile_from_wave(
        arr, operator=operator, manifold=m, epsilon_drift=float(epsilon_drift), **energy_kwargs
    )
    energy_class = profile.energy_class

    if unit_norm_residual > float(epsilon_drift):
        admitted, reason = False, "amplitude_density_not_unit"
    elif psi_dig != certificate.psi_digest:
        admitted, reason = False, "certificate_state_mismatch"
    elif not certificate.converged:
        admitted, reason = False, f"relaxation_not_certified:{certificate.reason}"
    else:
        admitted, reason = True, "admitted"

    proposal: CrystallizationProposal | None = None
    if not admitted:
        route = "refused"
    elif energy_class in (EnergyClass.E3, EnergyClass.E4):
        route = "readback_eligible"
    elif energy_class.vault_candidate:
        decision = crystallization_for_holographic_seal(
            arr,
            epsilon_drift=float(epsilon_drift),
            manifold=m,
            operator=operator,
            **energy_kwargs,
        )
        if decision.may_speculative_seal:
            route = "crystallization_proposal"
            proposal = CrystallizationProposal(
                proposal_id="crystal-"
                + _content_id(
                    {
                        "psi": psi_dig,
                        "certificate": certificate.certificate_id,
                        "decision": decision.as_dict(),
                    }
                ),
                epistemic_status=_SPECULATIVE,
                psi_digest=psi_dig,
                certificate_id=certificate.certificate_id,
                decision=decision,
            )
        else:
            route = "hold"  # cold but not crystalline (e.g. open superposition)
    else:
        route = "hold"  # E2 mid-band: neither vault-cold nor readback-hot

    return EgressVerdict(
        admitted=admitted,
        reason=reason,
        route=route,
        unit_norm_residual=unit_norm_residual,
        versor_residual=versor_residual,
        versor_closed=versor_closed,
        energy_class=energy_class,
        energy_profile=profile,
        proposal=proposal,
    )


# --- Composed lifecycle ---------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class LifecycleOutcome:
    ingress: IngressWavePacket
    relaxation: RelaxationResult
    verdict: EgressVerdict
    outcome_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "outcome_id",
            _content_id(
                {
                    "ingress": self.ingress.packet_digest,
                    "certificate": self.relaxation.certificate.certificate_id,
                    "route": self.verdict.route,
                    "psi": _psi_digest(self.relaxation.psi_steady),
                }
            ),
        )


class CognitiveLifecycleEngine:
    """Thin deterministic composer over the pure lifecycle functions.

    Name matches the ADR §3 sketch for traceability; the implementation is
    the corrected one (pins SD-A/SD-B/SD-C; deviations D-1…D-5).
    """

    def __init__(self, *, epsilon_drift: float = _EPSILON_DRIFT) -> None:
        self.epsilon_drift = float(epsilon_drift)
        self.manifold = WaveManifold(epsilon_drift=self.epsilon_drift)

    def ingest_context(self, packets: Sequence[PacketLike], domain_id: str) -> IngressWavePacket:
        return ingest_context(packets, domain_id)

    def relax(
        self,
        ingress: IngressWavePacket,
        hamiltonian: ProblemHamiltonian,
        **kwargs: Any,
    ) -> RelaxationResult:
        return relax_to_ground(ingress.psi, hamiltonian, **kwargs)

    def egress(
        self,
        psi_steady: np.ndarray,
        certificate: RelaxationCertificate,
        **energy_kwargs: Any,
    ) -> EgressVerdict:
        return egress_gate(
            psi_steady,
            certificate,
            epsilon_drift=self.epsilon_drift,
            manifold=self.manifold,
            **energy_kwargs,
        )

    def solve(
        self,
        packets: Sequence[PacketLike],
        domain_id: str,
        hamiltonian: ProblemHamiltonian,
        *,
        dt: float = 1.0,
        max_steps: int = 512,
        tol: float = 1e-10,
        energy_inputs: Mapping[str, object] | None = None,
    ) -> LifecycleOutcome:
        """Ingress → relax → egress. Fail-closed at every stage (typed errors)."""
        ingress = self.ingest_context(packets, domain_id)
        result = relax_to_ground(ingress.psi, hamiltonian, dt=dt, max_steps=max_steps, tol=tol)
        verdict = self.egress(
            result.psi_steady, result.certificate, **dict(energy_inputs or {})
        )
        return LifecycleOutcome(ingress=ingress, relaxation=result, verdict=verdict)


__all__ = [
    "CognitiveLifecycleEngine",
    "CognitiveLifecycleError",
    "CrystallizationProposal",
    "EgressValidationError",
    "EgressVerdict",
    "HamiltonianCompileError",
    "IngressDegenerate",
    "IngressWavePacket",
    "LifecycleOutcome",
    "ProblemHamiltonian",
    "PropositionalEntailmentVerdict",
    "PropositionalProblem",
    "RelaxationCertificate",
    "RelaxationInputError",
    "RelaxationNotConverged",
    "RelaxationNumericalFailure",
    "RelaxationResult",
    "assignment_component_index",
    "compile_propositional",
    "compile_quadratic_well",
    "egress_gate",
    "ingest_context",
    "propositional_entails",
    "relax_to_ground",
    "uniform_assignment_state",
]
