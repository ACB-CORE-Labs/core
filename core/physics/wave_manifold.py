"""
core/physics/wave_manifold.py

Wave-field substrate for Cl(4,1) (ADR-0241).

Continuous multivector wave fields ψ ∈ ℝ³² under:
  * sandwich transport  ψ' = R ψ ~R   (multivector field path; matches versor_apply)
  * left spinor transport ψ' = R ψ    (odd-capable / chiral path)
  * spectral leakage (metric proj onto resonant modes)
  * wave polar analogy (sandwich conjugator)
  * unitary amplitude residual + chiral spinor charge readout

Algebra-native only (algebra/*). No scipy-as-truth. No teaching/vault imports.
Off-serving until explicit gates; dual-checked unitary residual.
"""

from __future__ import annotations

from typing import Any, Sequence, Tuple

import numpy as np

from algebra.cga import cga_inner
from algebra.cl41 import N_COMPONENTS, geometric_product, reverse, scalar_part
from algebra.versor import versor_apply, versor_condition, versor_unit_residual

_CLOSURE_TOL = 1e-6
_NEAR_ZERO = 1e-12
_NONSIMPLE_TOL = 1e-6


class WaveSpectralLeakageError(ValueError):
    """Fail-closed spectral leakage (metric-degenerate resonant span).

    Mapped to :class:`core.physics.surprise.SurpriseResidualError` at the
    surprise boundary so discovery / dual contracts keep a stable error type.
    """

    def __init__(self, reason: str, **disclosure: Any) -> None:
        self.reason = reason
        self.disclosure = dict(disclosure)
        super().__init__(f"spectral_leakage refused [{reason}]: {self.disclosure}")

# Unit pseudoscalar I₅ = e1 e2 e3 e4 e5 (central; I² = −1 in Cl(4,1)).
_I5 = np.zeros(N_COMPONENTS, dtype=np.float64)
_I5[31] = 1.0
_I5.setflags(write=False)


def _as_mv(x: np.ndarray, name: str = "ψ") -> np.ndarray:
    arr = np.asarray(x, dtype=np.float64)
    if arr.shape != (N_COMPONENTS,):
        raise ValueError(f"{name} must have shape ({N_COMPONENTS},); got {arr.shape}")
    return arr


def _identity() -> np.ndarray:
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    out[0] = 1.0
    return out


def _strict_close_rotor(V: np.ndarray, *, name: str) -> np.ndarray:
    """Rescale a true versor to unit weight; never seed-fabricate."""
    arr = _as_mv(V, name)
    product = geometric_product(arr, reverse(arr)).astype(np.float64)
    scalar_sq = float(product[0])
    residue = product.copy()
    residue[0] = 0.0
    residue_norm = float(np.linalg.norm(residue))
    if residue_norm >= 1e-2 or scalar_sq <= 0.0:
        raise ValueError(
            f"{name}: input not a versor "
            f"(residue_norm={residue_norm:.3e}, scalar_sq={scalar_sq:.3e})"
        )
    closed = (arr * (1.0 / np.sqrt(scalar_sq))).astype(np.float64)
    cond = versor_condition(closed)
    if cond >= _CLOSURE_TOL:
        raise ValueError(f"{name}: versor_condition={cond:.3e} after close")
    return closed


def _require_closed_rotor(R: np.ndarray, *, name: str = "R") -> np.ndarray:
    arr = _as_mv(R, name)
    cond = versor_condition(arr)
    if cond >= _CLOSURE_TOL:
        # Attempt strict close only if already a versor (scalar reverse product).
        return _strict_close_rotor(arr, name=name)
    return arr.astype(np.float64, copy=True)


def _exp_bivector_generator(B: np.ndarray, dt: float) -> np.ndarray:
    """R = exp(B·dt) for a pure (or nearly pure) bivector generator.

    Closed form when B² is scalar (simple plane); series fallback otherwise.
    Result is construction-closed (versor_condition < 1e-6).
    """
    G = _as_mv(B, "B") * float(dt)
    G = G.copy()
    G[0] = 0.0  # generator is grade ≥ 1; scalar part does not enter exp path
    if float(np.linalg.norm(G)) < _NEAR_ZERO:
        return _identity()

    Gsq = geometric_product(G, G).astype(np.float64)
    s = float(Gsq[0])
    higher = Gsq.copy()
    higher[0] = 0.0
    if float(np.linalg.norm(higher)) < _NONSIMPLE_TOL:
        out = np.zeros(N_COMPONENTS, dtype=np.float64)
        if abs(s) < _NEAR_ZERO:
            out[0] = 1.0
            out = out + G
        elif s < 0.0:
            mag = float(np.sqrt(-s))
            out[0] = float(np.cos(mag))
            out = out + (float(np.sin(mag)) / mag) * G
        else:
            mag = float(np.sqrt(s))
            out[0] = float(np.cosh(mag))
            out = out + (float(np.sinh(mag)) / mag) * G
        return _strict_close_rotor(out, name="exp_bivector")

    # Non-simple: truncated geometric series (construction boundary only).
    term = _identity()
    out = term.copy()
    for k in range(1, 48):
        term = geometric_product(term, G) / float(k)
        out = out + term
        if float(np.linalg.norm(term)) < 1e-18:
            break
    return _strict_close_rotor(out, name="exp_bivector_series")


def _metric_project(
    x: np.ndarray,
    modes: Sequence[np.ndarray],
) -> Tuple[np.ndarray, np.ndarray]:
    """Metric-orthogonal projection onto span(modes) under cga_inner.

    Solves G c = r with G_ij = ⟨b_i, b_j⟩, r_i = ⟨b_i, x⟩. Returns
    (projection, residual) with residual = x − projection.
    """
    x_arr = _as_mv(x, "ψ_incoming")
    cols = [_as_mv(m, f"mode[{i}]") for i, m in enumerate(modes)]
    k = len(cols)
    if k == 0:
        return np.zeros(N_COMPONENTS, dtype=np.float64), x_arr.copy()

    gram = np.array(
        [[cga_inner(cols[i], cols[j]) for j in range(k)] for i in range(k)],
        dtype=np.float64,
    )
    rhs = np.array([cga_inner(cols[i], x_arr) for i in range(k)], dtype=np.float64)
    # Fail-closed on metric-degenerate span (null direction with no reciprocal).
    Bmat = np.column_stack(cols)
    rank_b = int(np.linalg.matrix_rank(Bmat))
    rank_g = int(np.linalg.matrix_rank(gram))
    if rank_g < rank_b:
        _u, _sv, vh = np.linalg.svd(gram)
        degenerate_combo = [round(float(v), 6) for v in vh[-1]]
        null_columns = [
            i for i in range(k) if abs(float(gram[i, i])) < _NEAR_ZERO
        ]
        raise WaveSpectralLeakageError(
            "degenerate_metric_span",
            rank_basis=rank_b,
            rank_gram=rank_g,
            null_columns=null_columns,
            degenerate_combo=degenerate_combo,
        )
    coeffs, *_ = np.linalg.lstsq(gram, rhs, rcond=None)
    projection = np.zeros(N_COMPONENTS, dtype=np.float64)
    for c, col in zip(coeffs, cols):
        projection = projection + float(c) * col
    residual = x_arr - projection
    return projection, residual


class WaveManifold:
    """Continuous wave propagation + resonant measures over Cl(4,1) fields.

    Construction-closed rotors; dual-checked unitary residual; deterministic.
    Optional standing-wave mode registry for resonant recall (ADR-0241 §2.2);
    not a vault/store — reconstruction-over-storage, off-serving.
    """

    def __init__(self, epsilon_drift: float = 1e-6) -> None:
        self.epsilon_drift = float(epsilon_drift)
        self.n_dims = N_COMPONENTS
        # Standing-wave eigenmode registry (session-local; not durable memory).
        self._resonant_modes: list[np.ndarray] = []

    # --- Transport -----------------------------------------------------------

    def sandwich_step(self, psi: np.ndarray, R: np.ndarray) -> np.ndarray:
        """Multivector field path: ψ' = R ψ ~R (matches :func:`versor_apply`)."""
        psi_arr = _as_mv(psi, "ψ")
        R_arr = _require_closed_rotor(R, name="R")
        return versor_apply(R_arr, psi_arr).astype(np.float64)

    def left_spinor_step(self, psi: np.ndarray, R: np.ndarray) -> np.ndarray:
        """Spinor / chiral path: ψ' = R ψ (left geometric product)."""
        psi_arr = _as_mv(psi, "ψ")
        R_arr = _require_closed_rotor(R, name="R")
        return geometric_product(R_arr, psi_arr).astype(np.float64)

    def algebraic_schrodinger_step(
        self,
        psi: np.ndarray,
        H_operator: np.ndarray,
        dt: float,
    ) -> np.ndarray:
        """Unitary step via R = exp(B·dt), sandwich on multivector fields.

        ``H_operator`` is the bivector generator B (32-vector). Default field
        law is sandwich so even field-state versors stay closed under the step.
        """
        psi_arr = _as_mv(psi, "ψ")
        R = _exp_bivector_generator(H_operator, dt)
        return self.sandwich_step(psi_arr, R)

    # --- Unitary residual (GoldTether wave form) -----------------------------

    def measure_unitary_residual(self, psi: np.ndarray) -> float:
        """Dual-checked amplitude drift: max(‖ψ ψ̃ − 1‖, ‖~ψ ψ − 1‖ proxy).

        Uses :func:`versor_unit_residual` on ψ and reverse(ψ).
        """
        psi_arr = _as_mv(psi, "ψ")
        r = float(versor_unit_residual(psi_arr))
        r_rev = float(versor_unit_residual(reverse(psi_arr)))
        return max(r, r_rev)

    # --- Spectral leakage (surprise) -----------------------------------------

    def compute_spectral_leakage(
        self,
        psi_incoming: np.ndarray,
        resonant_modes: Sequence[np.ndarray],
    ) -> Tuple[np.ndarray, float]:
        """Non-resonant spectral leakage: residual after metric proj onto modes.

        Returns ``(surprise_vector, energy)`` with energy = Euclidean ‖residual‖
        (definite readout after metric-exact projection; same doctrine as
        surprise_residual magnitude).
        """
        _proj, residual = _metric_project(psi_incoming, list(resonant_modes))
        energy = float(np.linalg.norm(residual))
        return residual.astype(np.float64), energy

    # --- Wave polar analogy (Procrustes upgrade) -----------------------------

    def wave_analogical_polar(
        self,
        psi_A: np.ndarray,
        psi_B: np.ndarray,
    ) -> np.ndarray:
        """Recover sandwich conjugator R with psi_B ≈ R psi_A ~R.

        Canonical single-field analogy rotor via field conjugacy (SVD + Spin GN).
        Analytic Clifford polar R = C (~C C)^{-1/2} is **not** used: for
        multi-grade Cl(4,1) fields ~C C is non-scalar (ADR-0241 P7 demotion;
        ``docs/briefs/P7_design_note.md``).
        """
        R, _residual = self.wave_field_conjugacy([psi_A], [psi_B])
        return R

    def wave_field_conjugacy(
        self,
        sources: Sequence[np.ndarray],
        targets: Sequence[np.ndarray],
    ) -> Tuple[np.ndarray, float]:
        """Multi-pair sandwich conjugacy (thin wrap over stacked field engine).

        Canonical multi-field path for Procrustes (ADR-0241 Slice 3). Returns
        ``(R, residual)`` where residual is the mean raw-sandwich residual from
        the conjugacy engine (callers may recompute pair residuals).
        """
        # Lazy import: dynamic_manifold may call WaveManifold at runtime.
        from core.physics.dynamic_manifold import _field_conjugacy_versor

        src = [_as_mv(s, f"source[{i}]") for i, s in enumerate(sources)]
        tgt = [_as_mv(t, f"target[{i}]") for i, t in enumerate(targets)]
        if len(src) != len(tgt) or not src:
            raise ValueError("wave_field_conjugacy: non-empty equal-length pairs required")
        R, residual = _field_conjugacy_versor(src, tgt)
        return _require_closed_rotor(R, name="R_conjugacy"), float(residual)

    # --- Standing-wave registry / resonant recall (ADR-0241 §2.2) ------------

    def register_resonant_mode(self, psi_k: np.ndarray) -> int:
        """Register a standing-wave mode. Returns mode index. Session-local only."""
        mode = _as_mv(psi_k, "ψ_k").copy()
        self._resonant_modes.append(mode)
        return len(self._resonant_modes) - 1

    def clear_resonant_modes(self) -> None:
        """Drop all registered modes (tests / session reset)."""
        self._resonant_modes.clear()

    @property
    def resonant_modes(self) -> tuple[np.ndarray, ...]:
        return tuple(m.copy() for m in self._resonant_modes)

    def resonant_recall(
        self,
        psi_query: np.ndarray,
        *,
        modes: Sequence[np.ndarray] | None = None,
    ) -> Tuple[np.ndarray, float, int]:
        """Holographic resonant lock-in: max constructive overlap with modes.

        Overlap uses the scalar part of ``ψ_q · ~ψ_k`` (algebraic inner structure
        via reverse product — not cosine/ANN). Returns
        ``(best_mode, resonance_energy, index)``.
        Empty mode set raises ``ValueError`` (no confabulated recall).
        """
        query = _as_mv(psi_query, "ψ_query")
        mode_list = self._resolve_modes(modes)
        if not mode_list:
            raise ValueError("resonant_recall: empty mode set (no confabulated recall)")

        best_i = 0
        best_E = -1.0
        for i, mode in enumerate(mode_list):
            # Resonance energy: |⟨ψ_q ~ψ_k⟩_0| — constructive phase lock magnitude.
            prod = geometric_product(query, reverse(mode))
            energy = abs(float(scalar_part(prod)))
            if energy > best_E:
                best_E = energy
                best_i = i
        return mode_list[best_i].copy(), float(best_E), int(best_i)

    def resonant_reconstruct(
        self,
        psi_query: np.ndarray,
        *,
        modes: Sequence[np.ndarray] | None = None,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Superposition reconstruction ψ̂ = Σ_k c_k ψ_k.

        Coefficients c_k are reverse-product scalar overlaps
        ⟨ψ_q ~ψ_k⟩_0, L1-normalized when the total absolute mass is nonzero.
        Reconstruction-over-storage via interference weights — not cosine
        similarity and not argmax-only lock-in (use :meth:`resonant_recall`
        for hard mode selection).

        Returns ``(psi_hat, coeffs, energies)``. Empty mode set raises
        ``ValueError`` (no confabulation).
        """
        query = _as_mv(psi_query, "ψ_query")
        mode_list = self._resolve_modes(modes)
        if not mode_list:
            raise ValueError(
                "resonant_reconstruct: empty mode set (no confabulated recall)"
            )
        energies = np.array(
            [
                float(scalar_part(geometric_product(query, reverse(m))))
                for m in mode_list
            ],
            dtype=np.float64,
        )
        mass = float(np.sum(np.abs(energies)))
        if mass < _NEAR_ZERO:
            coeffs = np.zeros(len(mode_list), dtype=np.float64)
            # Uniform refuse-to-invent: zero reconstruction when no overlap.
            psi_hat = np.zeros(N_COMPONENTS, dtype=np.float64)
            return psi_hat, coeffs, energies
        coeffs = energies / mass
        psi_hat = np.zeros(N_COMPONENTS, dtype=np.float64)
        for c, mode in zip(coeffs, mode_list):
            psi_hat = psi_hat + float(c) * mode
        return psi_hat.astype(np.float64), coeffs, energies

    def phase_correlation(
        self,
        psi_A: np.ndarray,
        psi_B: np.ndarray,
    ) -> float:
        """Algebraic multimodal resonance (cohesion I-04).

        rho(A,B) = ⟨ψ_A ~ψ_B + ψ_B ~ψ_A⟩_0

        Symmetric, deterministic, reverse-product structure. Not cosine/ANN.
        """
        a = _as_mv(psi_A, "ψ_A")
        b = _as_mv(psi_B, "ψ_B")
        ab = geometric_product(a, reverse(b))
        ba = geometric_product(b, reverse(a))
        return float(scalar_part(ab + ba))

    def _resolve_modes(
        self,
        modes: Sequence[np.ndarray] | None,
    ) -> list[np.ndarray]:
        if modes is None:
            return list(self._resonant_modes)
        return [_as_mv(m, f"mode[{i}]") for i, m in enumerate(modes)]

    # --- Chiral spinor charge ------------------------------------------------

    def chiral_charge(self, psi: np.ndarray) -> float:
        """Topological spinor charge Q = ⟨ψ I₅ ~ψ⟩_0 (ADR-0241 §2.4C).

        In real Cl(4,1), ψ~ψ is always even-grade, so ⟨I₅ (ψ~ψ)⟩_0 is structurally
        zero — the same odd-grade vacuity that retired Super §3.3 on even field
        states (#19). The formula is implemented honestly (returns ~0) and is
        conserved under left unitary multiply; a non-vacuous complex/pair-spinor
        extension remains future work. Even unit versors stay honest at ~0.
        """
        psi_arr = _as_mv(psi, "ψ")
        # ⟨ψ I ~ψ⟩_0 = ⟨I (ψ ~ψ)⟩_0 (I central)
        return float(
            scalar_part(
                geometric_product(
                    geometric_product(psi_arr, _I5),
                    reverse(psi_arr),
                )
            )
        )


__all__ = ["WaveManifold", "WaveSpectralLeakageError"]
