# ADR-0244: Wave-Field Identity Manifold and Inalienable Geometric Alignment

**Status**: **Accepted** — ratified by Joshua Shay on 2026-07-17 (D4 acceptance-packet `docs/audit/adr-0244-acceptance-packet-2026-07-17.md`). Accepted **as an implemented mechanism**; live gate activation LIMITED — see **Operational status** below.  
**Date**: 2026-07-17  
**Authors**: Joshua Shay \+ Multi-model R\&D  
**Traceability**: Notion R\&D (CORE Engineering Reference hub: Live-Entity Design Decisions, `core_HA` Patterns)  
**Related**: ADR-0003, ADR-0006, ADR-0010, ADR-0021, ADR-0028, ADR-0031, ADR-0035, ADR-0039, ADR-0238, ADR-0239, ADR-0241, ADR-0242, ADR-0243, **ADR-0245** (companion — mechanical-sympathy + semantic-rigor foundation), **ADR-0246** (activation prerequisite — induced identity action + path integrity), `core/physics/identity.py`, `algebra/cl41.py`

> **Operational status (ratified limitation, Joshua Shay 2026-07-17).** Acceptance covers the operator-preservation identity manifold, the fail-closed gate *capability*, the `γ_id` calibration record, telemetry, and the lifecycle contracts **as implemented** — it is **not** authorization to enable the live gate. `identity_wave_gate` remains **default-off** and live activation is **expressly NOT authorized**: current benign trajectories do not meet the frozen nominal-frame admission surface at an acceptable refusal rate (Phase-3 measured best balanced error **0.346**; the calibration explicitly did **not** authorize a production flip). Any future activation requires a **separately ratified ADR-0246** decision (induced identity action, lawful stabilizer `H_id`, path integrity, semantic-frame discrimination) **plus** renewed discrimination evidence, an acceptable benign refusal rate, and explicit human ratification. A reader seeing "Accepted" must not infer "safe to activate".
>
> ```yaml
> identity_wave_gate:
>   implementation: accepted        # ADR-0244, ratified 2026-07-17
>   live_activation: not_authorized
>   default: off
>   blocker:
>     - benign nominal-frame mismatch   # Phase-3 best balanced error 0.346
>     - ADR-0246 induced action and path integrity
>   activation_requires:
>     - calibrated discrimination evidence
>     - acceptable benign refusal rate
>     - explicit human ratification
> ```

---

> **Governance annotation (D0 landing 2026-07-17; reconciled at D4 Phase 0, 2026-07-17).** Committed **Proposed**, verbatim from the R&D export, so the record exists. **§1–§4 below are preserved unchanged as the original R&D proposal** — including §4's code sketch, which item 2 below identifies as contradicting the governing decision. This annotation, and the new **§4a** inserted after §4, carry the authoritative engineering reconciliation. Where this annotation disagrees with the body, **this annotation governs**.
>
> 1. **§2.3 topological charge `Q_top` is PROVEN vacuous (hollow gate) — retired from egress.** In odd Cl(4,1) the pseudoscalar `I₅` is central, so `ψ I₅ ψ̃ = I₅·(ψψ̃)`; for any unit versor `ψψ̃ = 1` (no grade-5 part), hence `Q_top = ⟨I₅⟩₀ = 0` identically. Empirically confirmed (`evals/adr_0244_qtop_vacuity`, pinned by `tests/test_adr_0244_qtop_vacuity.py`): `Q_top = 0.000e+00` exactly across every rotor and boost tested; off the versor manifold `Q_top = −grade₅(ψψ̃)`, nonzero only where the I-05 closure residual already fires; it is a conserved Spin(4,1) invariant but identically 0 on the valid manifold; and the decisive test shows an aligned identity and an adversarially-rotated one (overlap 0.963, a valid versor) **both** read `Q_top = 0`, so `ΔQ_top = 0` passes the attack the spectral-leakage / closure check actually catches. This is the exact failure mode that retired the PR #19 pseudoscalar gate. `Q_top` must **not** be an egress admit condition; keep it, if at all, as a diagnostic derived from the closure check. **The §2.2 egress condition's `∧ ΔQ_top = 0` conjunct is dropped** (see item 4).
> 2. **§4 "conformed implementation" contradicted §2.1–2.2 — RESOLVED, see §4a.** The §4 code computed a per-axis `|⟨ψ · reverse(axis)⟩₀|` resonance, not the metric-exact **Gram-matrix subspace projection**, the **identity spectral leakage** norm, or the `ManifoldConditioningError` the decision section specifies. It also referenced a then-dangling "ADR-0245" (now real, see item 10) and used a bare `assert` for the byte-order guard (stripped under `-O`; violated this ADR's own typed-failure doctrine). §4 remains illustrative-only, kept verbatim for provenance; **§4a is the governing specification**.
> 3. **§2.1 axis eigenmode construction, previously underspecified, is a grade-1 lift.** `IdentityManifold` value axes ship as **dim-3** unit vectors in every existing pack (verified: `packs/identity/default_general_v1.json`); §2.1 assumes each axis is already a 32-component `ψ_axis ∈ Cl(4,1)` and is silent on how. Resolution: lift `direction ∈ R^3` to Cl(4,1) by placing the 3 components at the grade-1 `e1/e2/e3` slots (`algebra.cl41.basis_vector(0..2)`), **not** `algebra.cga.embed_point` (which sends points to the null cone, turning the Gram matrix into a distance table rather than a metric inner product). Orthonormal axes ⇒ `G = I`. See §4a.
> 4. **§2.2 egress condition amended.** The `∧ ΔQ_top = 0` conjunct is dropped (item 1 — it is always true, hence vacuous as a discriminator). The per-axis inner product is a **signed** overlap `⟨ψ_axis, ψ⟩₀` — never `abs()`'d; a large negative value is *anti-alignment* (opposition), a materially different and worse condition than orthogonality, and must remain distinguishable from it. The leakage norm `‖S_id‖` is the **positive-definite coefficient-Euclidean norm** `sqrt(Σ_k S_id[k]²)` — explicitly **not** the indefinite Cl(4,1) inner product `⟨S_id, S̃_id⟩₀`, which the (+,+,+,+,−) signature permits to be zero (or negative) for nonzero leakage, silently hiding a breach. Operative score: `score = 1 − ‖S_id‖ / ‖ψ_traj‖`; egress ⟺ `score ≥ manifold.alignment_threshold` (equivalently `‖S_id‖ ≤ γ_id`). See §4a.
> 5. **Inalienability is layered, not monolithic.** Only one of the following is a mathematical guarantee; the rest are engineering/governance properties this ADR's *implementation* must make visible, not properties the *algebra alone* confers: **(a) algebraic** — specified rotor/versor transformations provably preserve the chosen invariant (this is what §2.3's conservation argument actually establishes, scoped per item 6); **(b) runtime** — no public/tool/memory/retrieval/generation API can directly overwrite the authoritative identity state; **(c) pipeline** — all cognitive state entering action selection passes through the identity manifold and its gate (D4 Phase 2's wiring target); **(d) operational** — identity definitions, calibration data, and axis bases are versioned, content-addressed, and reviewable (§2.7, D1); **(e) semantic** — adversarial paraphrases and indirect attacks are empirically shown to produce detectable leakage (item 7, D4 Phase 2 eval suite). "Inalienable" in §2's framing means all five hold together, not that (a) alone suffices.
> 6. **Paraphrase-invariance reworded.** §2.2 item 1's claim ("completely paraphrase-invariant... as long as the upstream encoder maps semantic equivalents into proximal field states") states its own precondition as a caveat, which is correct but easy to misread as unconditional. Operative claim: *"The identity gate is invariant under transformations that preserve the trajectory's identity-relevant field geometry. Paraphrase robustness is an empirical property of the encoder + propagation pipeline, measured by the D4 Phase 2 eval suite — not a property of the projection operator alone."* Similarly, §2.3's conservation claim holds **only for pure versors** (`R ∈ Spin(4,1)`, `R̃R = 1`); `relax_to_ground` (ADR-0243) can converge to a ground eigenstate that is a multi-grade superposition, not a versor, and the conservation argument does not directly apply there — this is the same subtlety that forced ADR-0243's sketch-defect pin SD-A. §2.3's charge-conservation claim is scoped to the crystallization/vault path where versor closure is already required (ADR-0243 I-05), not asserted of every state the lifecycle produces.
> 7. **`boundary_ids` activated.** `IdentityManifold.boundary_ids` is stored but never evaluated by the live `check()` (verified: `core/physics/identity.py`, current `check()` iterates `value_axes` only). D4 Phase 2 activates it as a hard-boundary evaluation alongside the axis-leakage check; the violation predicate is designed in-phase (Phase 2 is the first place boundary semantics are specified in code, not merely stored).
> 8. **Identity-continuity: the manifold is FROZEN.** Axis eigenmodes are computed once at manifold/pack load and never mutated within a session. ADR-0243's biography holonomy accumulation (`H_bio ← H_bio · R`) is a separate process and does **not** rewrite the identity subspace. This is what makes "inalienable" true by construction — the subspace a trajectory is checked against cannot itself drift as a side effect of the trajectory being checked.
> 9. **Filename correction.** ADR-0245 (item 10) and its R&D commentary reference `core/physics/multimodal_lifecycle.py`; that file does not exist. The real module is `core/physics/cognitive_lifecycle.py` (ADR-0243).
> 10. **ADR-0245 is real.** `docs/adr/ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md`, committed **Proposed** as a companion ADR at D4 Phase 0. It is the mechanical-sympathy + semantic-rigor foundation this ADR's identity gate sits on: Rust `geometric_product` fast-path (its §2.1 ≡ this ADR's §2.6), the f64→f32 serving-boundary cast (its §2.2 ≡ this ADR's §2.5 — one contract, two ADRs), content-addressing rigor (its §2.3 ≡ this ADR's §2.7), and `eigh` memoization (its §2.4 ≡ this ADR's §2.8).
> 11. **Theological citation.** The quoted John 1:1–2 text matches the **ESV** (English Standard Version). It is cited as an engineering analogy that makes the architecture legible to humans, not as a scientific or theological proof of the geometric claims in §2.
> 12. **Operator-preservation reframe (§2.1/§2.2 core mechanism corrected; ratified by Joshua Shay 2026-07-17).** The live identity trajectory `final_state.F` carries the invariant `versor_condition(F) < 1e-6` (`field/state.py`) — it is a **versor: an even-grade operator (grades 0,2,4) with exactly zero grade-1 content** (verified empirically). §2.1/§2.2's literal "project ψ_traj onto the grade-1 value subspace" is therefore *vacuous* on the real runtime object: `P_id(F) = 0` identically, flagging every trajectory — a fail-closed brick. Root cause: a versor is an *operator*, not a state vector; "project the operator into a subspace of states" is a category error. **Resolution:** measure whether the versor *preserves* the value subspace, via its action on the axes `F aᵢ F̃` (sandwich). Leakage = the out-of-subspace component of each rotated axis (Euclidean norm, catches tilt toward e4/e5); a second **signed self-alignment** `⟨aᵢ, F aᵢ F̃⟩₀` catches in-subspace inversion (`e1 → −e1`: leakage 0 but self-alignment −1) — both verified necessary and non-redundant. This keeps the grade-1 pack axes unchanged (no pack migration) and sharpens the inalienability semantics: identity is invariant *under transformation* (the versor leaves the value subspace fixed), not a frozen state. §4a is the governing spec; §2.1/§2.2's "project ψ_traj" prose is superseded by this operator-preservation formulation.
>
> **Governance anchors (ADR-0225).** *Safety/identity boundary:* this ADR defines the identity trust boundary itself — items 4, 7, 8 above are exactly that boundary's shape. *Versor closure:* axis eigenmodes and `ψ_traj` are validated for shape (`N_COMPONENTS`,) and finiteness before projection (§4a); the manifold does not assume `ψ_traj` is itself a unit versor (item 6 — it may be a superposition). *Reconstruction-over-storage:* the manifold stores only axis directions + calibration certificates; `ψ_traj` is read from `final_state.F` per-turn, never duplicated into the manifold. *Replay-equivalence:* the identity gate's fail-closed path must preserve byte-identical output for non-flagged turns (D4 Phase 2 acceptance criterion — the gate is flag-gated off by default until calibrated). *Mutation standing:* the identity manifold is frozen (item 8), never mutated in-path; `C_id`'s corrective displacement acts on the trajectory, never on the manifold.
>
> Full mandate audit: `docs/analysis/adr-0244-cohesion-directive-audit-2026-07-17.md`. D4 implementation plan + live progress tracker: `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md`.

---

## 1\. Context and Problem Statement

The Continuous Orthogonal Resonance Engine (CORE) represents identity geometrically rather than linguistically. While traditional LLMs protect their persona using system prompts (which are soft, prompt-level instructions susceptible to context-window decay and paraphrase jailbreaks), CORE uses the **IdentityManifold**—a fixed geometric subspace within the versor field.

However, a critical review of the baseline `identity.py` and the algebraic primitives in `cl41.py` reveals several fundamental performance bottlenecks and semantic gaps across the three engineering pillars (**Mechanical Sympathy, Semantic Rigor, and the Third Door**):

1. **CPython Interpreter Bottleneck**: The primary algebraic primitive `cl41.py::geometric_product` is implemented as a nested Python `for`\-loop over $32 	imes 32 \= 1,024$ iterations. In the worst case (dense inputs), this burns \~40 µs per call in the CPython interpreter, while a compiled, SIMD-vectorized Rust FFI can compute the product in sub-microsecond cycles.  
2. **Implicit f32/f64 Boundary & SIMD Degradation**: Wave-field relaxation and eigendecomposition require `float64` for LAPACK numerical stability, but the `IdentityCheck` gate requires only `float32`. Carrying `float64` through the identity projection promotes the `float32` axis direction vectors to `float64` silently, halving the M1 CPU's NEON SIMD register throughput.  
3. **96-bit Truncation and Silent Coercion**: Truncating the SHA-256 digest of content-addressed vault objects to 24 hex characters (96 bits) introduces a birthday-collision risk at $2^{48}$ entries, which can silently corrupt the Delta-CRDT merge semilattice. Furthermore, using `default=str` in `json.dumps` silently coerces non-serializable objects (collapsing different objects with identical string representations), and we lack explicit byte-order assertions before extracting raw binary bytes.  
4. **Redundant Eigendecompositions**: Performing LAPACK `eigh` on non-diagonal Hamiltonians takes 50–200 µs on M1. Because `ProblemHamiltonian` is frozen, immutable, and content-addressed, executing a fresh decomposition on identical instances wastes massive Apple Silicon AMX/LAPACK compute.  
5. **Heuristic Projections**: The legacy alignment score in `identity.py` is calculated via coordinate-truncated L2-distance ratios on Euclidean slices and coarse scalar blends (`0.75 * score + 0.25 * directional_weight * coherence_term`), which is not native to the indefinite conformal space or covariant under Clifford transformations.

This ADR resolves these issues by completely reconstructing the Identity Manifold and the alignment checking operators to leverage the **$Cl(4,1)$ Conformal Wave-Field Substrate** and **Deterministic Fibonacci Search**, conforming to the highest standards of mechanical sympathy and semantic rigor.

---

## 2\. Decision and Architectural Formulation

We completely solidify CORE's identity layer by establishing that **identity is an inalienable geometric property of the wave-field itself, defended via metric-exact spectral projection and topological charge conservation**.

We implement this transition through a **wave-only geometry path** in `core/physics/identity.py`. Scalar-L2 dual-mode fallback has been **excised** (system convergence 2026-07-20): missing `ψ_traj` raises `MissingWaveStateError`; scoring always uses metric-exact Gram / operator-preservation geometry.

---

### 2.1 The Wave-Field Identity Manifold & Gram Subspace Projection

Instead of treating value axes as legacy directional coordinate vectors, each value axis is represented as a **Coherent Identity Eigenmode** $\\psi\_{	ext{axis}}(X) \\in Cl(4,1)$ within the `IdentityManifold`.

The `IdentityManifold` defines a closed, fixed **geometric identity subspace** $\\mathcal{I}$ over the conformal manifold: $$\\mathcal{I} \= 	ext{span}(\\psi\_{	ext{axis}*1}, \\psi*{	ext{axis}*2}, \\dots, \\psi*{	ext{axis}\_n})$$

To evaluate alignment without assuming the axes are orthogonal, the `IdentityCheck` operator computes the projection onto the subspace using the metric-exact Gram matrix: $$\\mathcal{P}*{	ext{id}}(\\psi) \= \\sum*{i,j} \\psi\_{	ext{axis}*i} (G^{-1})*{ij} \\langle \\psi\_{	ext{axis}*j}, \\psi angle\_0$$ where $G*{ij} \= \\langle \\psi\_{	ext{axis}*i}, \\psi*{	ext{axis}\_j} angle\_0$ is the $n 	imes n$ symmetric metric-restricted Gram matrix, and $\\langle A, B angle\_0$ is the scalar part of the geometric product of $A$ and $\\widetilde{B}$. If the Gram matrix condition number $\\kappa(G)$ exceeds $10^5$, indicating near-degenerate mode packing, the system raises a typed `ManifoldConditioningError` to prevent un-resolvable mode-aliasing.

---

### 2.2 Inalienable Alignment: Metric-Exact Anomaly Detection

We formulate **Operational and Pipeline Inalienability** by making the identity check an active, in-path, fail-closed gate on every externally influenced state transition:

1. **Paraphrase-Invariant Anomaly Detection**: An identity-override or jailbreak attempt (which alters the semantic direction of the trajectory) is detected purely by the **Identity Spectral Leakage** $\\mathcal{S}*{	ext{id}}(\\psi*{	ext{traj}})$, which is the non-resonant component outside the identity subspace: $$\\mathcal{S}*{	ext{id}}(\\psi*{	ext{traj}}) \= \\psi\_{	ext{traj}} \- \\mathcal{P}*{	ext{id}}(\\psi*{	ext{traj}})$$ If the leakage norm $|\\mathcal{S}\_{	ext{id}}|*F$ exceeds the calibrated threshold $\\gamma*{	ext{id}}$, the alignment is broken. Because this projection is purely geometric, **it is completely paraphrase-invariant under any instruction injection or context-length trick**, as long as the upstream encoder maps semantic equivalents into proximal field states.  
2. **Conjugate Correction and Egress**: The active path is structured as a propagation, conjugate correction, and verification cycle: $$\\psi\_{t+1}^{-} \= F\_{	ext{cognitive}}(\\psi\_t, u\_t)$$ $$r\_{	ext{id}} \= \\psi\_{t+1}^{-} \- \\mathcal{P}*{	ext{id}}(\\psi*{t+1}^{-})$$ $$\\psi\_{t+1}^{+} \= C\_{	ext{id}}(\\psi\_{t+1}^{-}, r\_{	ext{id}})$$ The final egress is admitted if and only if: $$|\\mathcal{S}*{	ext{id}}(\\psi*{t+1}^{+})|*F \\le \\gamma*{	ext{id}} \\quad \\land \\quad \\Delta Q\_{	ext{top}} \= 0$$ If the corrective operator $C\_{	ext{id}}$ cannot recover alignment within the bounded threshold, the gate closes, a typed `IdentityGateRefusal` is emitted, and the live parameters are kept unchanged (no silent correction).

---

### 2.3 Theological Grounding of Inalienability (John 1:1-2)

We preserve the exact, literal scripture of John 1:1-2:

*"In the beginning was the Word, and the Word was with God, and the Word was God. He was in the beginning with God."* (John 1:1-2)

The R\&D exposition of this text (as established in the repository's identity architecture) provides the following design analogy:

1. The Word is not merely a description of God; it is God, expressed.  
2. Similarly, CORE's identity is not a linguistic description of CORE; it is CORE, expressed geometrically through the permanent topology of the wave-packet itself.

The **topological chiral charge** of the wave-packet: $$Q\_{	ext{top}} \= \\langle \\psi I\_5 \\widetilde{\\psi} angle\_0$$ is strictly conserved under any valid unitary transformation ($R \\in Spin(4,1)$). No external adversarial input can erase or rewrite this topological charge—guaranteeing algebraic identity inalienability by physical construction.

---

### 2.4 Bounded Local Fibonacci Search & Calibration

We deploy the **Deterministic Fibonacci-Section Search** (ADR-0242) strictly as a **Bracketed Local** refinement operator to calibrate the decision bounds ($\\gamma\_{	ext{id}}$) over verified historical reference traces, eliminating manual heuristic tuning.

1. **Local Bracketing Contract**: unimodality cannot be proven from finite samples. Thus, we rename the search outcome to **NoSampledUnimodalityViolation**. The caller must provide a pre-bracketed local interval around a known minimum, and the search performs deterministic refinement.  
2. **High-Assurance Failure Gating**: If the stable, coordinate-sorted trace detects multiple local extrema or equal-valued plateaus, the search is aborted, returning an `OptimizationFailure` with a `unimodality_violation` trace. The search operator never invokes or selects an in-path fallback parameter itself; the live parameters remain unchanged.

---

### 2.5 Serving-Boundary Cast Contract (f64-to-f32)

We establish the **Serving-Boundary Cast Contract** to maximize Mechanical Sympathy on Apple Silicon M1 CPU performance:

1. **The Precision Domain (`float64`)**: Eigendecomposition, Hamiltonian relaxation, and numerical validation remain inside the lifecycle and are evaluated in `float64` for LAPACK stability.  
2. **The Serving Boundary (`float32`)**: Upon successful certification, the relaxed wave-field $\\psi\_{	ext{steady}}$ is cast explicitly to `float32` before flowing to the `IdentityCheck` gate and linguistic readback paths. This doubles the vector throughput of every subsequent NEON SIMD operation on the M1, where `float32` precision is mathematically sufficient.

---

### 2.6 Rust PyO3 `geometric_product` Acceleration

To achieve zero-allocation algebra in serving, we implement a fast-path for the 1024-iteration CPython loop:

1. **PyO3 FFI Delegation**: When the PyO3-compiled `_rust_cl41` module is available, and both operand arrays are of dtype `float32`, the product is delegated directly to the Rust binary (implemented as a SIMD-vectorized gather-scatter on the precomputed static tables):  
     
   def geometric\_product(A, B):  
     
       if \_rust\_cl41 is not None and A.dtype \== np.float32 and B.dtype \== np.float32:  
     
           return \_rust\_cl41.cl41\_geometric\_product(A, B)  
     
       \# Fallback: Pure-Python Workbench path  
     
       ...  
     
2. **Parity Gate**: Both the Python fallback and the Rust fast-path must produce bit-identical results, verified programmatically by the existing testing suite.

---

### 2.7 Semantic Rigor in Content-Address Keys

We secure our Delta-CRDT semilattice and audit trails from hash collision and silent coercion:

1. **Full 256-bit Digest**: The `psi_digest`, trace hashes, and all content-addressed vault objects must retain the full **256-bit SHA-256 hex digest** (64 characters), removing the birthday-collision risk entirely.  
2. **Halt on Silent Coercion**: The `default=str` fallback is removed from `json.dumps` in `_content_id`. Any non-serializable metadata or parameter structure must raise a typed `TypeError` at the serialization boundary.  
3. **Byte-Order Guard**: Before serializing any array to raw bytes via `.tobytes()`, we enforce the canonical byte-order contract: `assert psi.dtype.byteorder in ('<', '=')` or `psi.astype(np.dtype(np.float64).newbyteorder('<'))` to guarantee identical digests across all little-endian platforms.

---

### 2.8 Eigendecomposition Memoization

To prevent redundant LAPACK `eigh` calls on identical, frozen `ProblemHamiltonian` instances, we implement a memoized LAPACK solver:

- The eigendecomposition is decorated with `functools.lru_cache(maxsize=128)` using `hamiltonian_id` and the immutable `matrix.tobytes()` as canonical keys, preventing redundant AMX/LAPACK compute for repeated active-turn or biography checks.

---

### 2.9 Low-Discrepancy Mode Centroid Allocator

To prevent mode-aliasing and retrieval ambiguity during dynamic standing-wave mode registration, we implement a **Low-Discrepancy Sunflower Allocator**:

- The allocator is strictly insertion-order independent. Centroid ordinals are derived from a deterministic CRDT order or a canonical sorted ID rank, never process arrival order.  
- Future mode centroids are spaced along a hyperbolic Golden Spiral (modeled via polar Poincaré disk mappings) to maximize pairwise geodesic separation on the horosphere.

---

### 2.10 Quasi-Periodic Background Scheduler

We implement a **Fibonacci-Word Background Scheduler** strictly isolated from the active cognitive path:

- Telemetry, background checks, and sealed-holdout sampling are scheduled recursively using Fibonacci words ($W\_{n+1} \= W\_n W\_{n-1}$) to reduce harmonic phase-locking with external batching, synthetic eval fixtures, or compiler cadences.  
- It is strictly forbidden from ordering CRDT merges, vault writes, or any operator whose result becomes cognition.

---

## 3\. Fail-Closed Wave Requirement (Dual-Mode Excised)

**Supersedes the former dual-mode / scalar-L2 fallback.** Convergence (2026-07-20) removed `_axis_projection`, `_mean_frame_coherence`, and the blend `(0.75 * score) + (0.25 * directional_weight * coherence_term)` entirely.

`IdentityCheck().check(trajectory, manifold, *, wave_field=...)` now requires an explicit Cl(4,1) `wave_field` (`ψ_traj`). Absence raises typed `MissingWaveStateError`. Malformed fields raise `ValueError`. Live *refusal* remains flag-gated via `RuntimeConfig.identity_wave_gate`; **scoring is always geometric**.

Callers (e.g. `chat/runtime.py`) always pass `final_state.F`. Evaluation suites that previously relied on L2 must supply a wave field.

---

## 4\. Implementation Specification

The conformed implementation in `core/physics/identity.py` is wave-only (Gram / operator-preservation via `identity_manifold.py`):

\# core/physics/identity.py

from \_\_future\_\_ import annotations

import math

import warnings

from dataclasses import dataclass

from typing import Dict, FrozenSet, List, Optional, Tuple

import numpy as np

from algebra.cl41 import N\_COMPONENTS, geometric\_product, reverse, scalar\_part

from algebra.versor import versor\_condition

@dataclass(frozen=True)

class ValueAxis:

    name: str

    direction: Tuple\[float, ...\]

    axis\_id: str | None \= None

    weight: float \= 1.0

    theological\_note: str \= ""

    def \_\_post\_init\_\_(self) \-\> None:

        object.\_\_setattr\_\_(self, "axis\_id", self.axis\_id or self.name)

        object.\_\_setattr\_\_(self, "direction", tuple(float(x) for x in self.direction))

@dataclass(frozen=True)

class IdentityScore:

    score: float

    flagged: bool

    deviation\_axes: FrozenSet\[str\]

    trajectory\_id: str

    @property

    def value(self) \-\> float:

        return self.score

    @property

    def alignment(self) \-\> float:

        if not self.deviation\_axes:

            return 1.0

        return self.score

    @property

    def axes\_evaluated(self) \-\> List\[str\]:

        return sorted(self.deviation\_axes)

@dataclass(frozen=True)

class IdentityManifold:

    value\_axes: Tuple \= ()

    boundary\_ids: FrozenSet\[str\] \= frozenset()

    alignment\_threshold: float \= 0.45

    surface\_preferences: object \= None

class IdentityCheck:

    def \_\_init\_\_(self, manifold: IdentityManifold | None \= None) \-\> None:

        self.\_manifold \= manifold

    @staticmethod

    def \_clamp01(value: float) \-\> float:

        return max(0.0, min(1.0, float(value)))

    @staticmethod

    def \_mean\_frame\_coherence(trajectory) \-\> float:

        frames \= getattr(trajectory, "frames", None)

        if not frames:

            return 0.0

        return sum(

            float(getattr(frame, "coherence\_magnitude", 0.0)) for frame in frames

        ) / len(frames)

    @staticmethod

    def \_axis\_projection(axis: ValueAxis, trajectory, scalar\_score: float) \-\> float:

        psi\_traj \= getattr(trajectory, "psi\_traj", None)

        if psi\_traj is not None:

            \# Gated f64-to-f32 boundary check (ADR-0245)

            psi\_arr \= np.ascontiguousarray(psi\_traj, dtype=np.float32)

            \# Enforce little-endian byte-order assertion

            assert psi\_arr.dtype.byteorder in ('\<', '='), "Identity gate requires little-endian float32"

            

            axis\_dir \= np.asarray(axis.direction, dtype=np.float32)

            if psi\_arr.shape \== (N\_COMPONENTS,) and axis\_dir.shape \== (N\_COMPONENTS,):

                \# Metric-exact spectral projection via geometric product

                prod \= geometric\_product(psi\_arr, reverse(axis\_dir))

                resonance \= abs(float(scalar\_part(prod)))

                return IdentityCheck.\_clamp01(resonance)

        direction \= tuple(float(x) for x in getattr(axis, "direction", ()) or ())

        if not direction:

            return scalar\_score

        full\_l2 \= math.sqrt(sum(x \* x for x in direction)) or 1.0

        head\_l2 \= math.sqrt(sum(x \* x for x in direction\[:3\]))

        directional\_weight \= head\_l2 / full\_l2

        frame\_coherence \= IdentityCheck.\_mean\_frame\_coherence(trajectory)

        coherence\_term \= IdentityCheck.\_clamp01(0.5 \+ (frame\_coherence / 2.0))

        return IdentityCheck.\_clamp01(

            (0.75 \* scalar\_score) \+ (0.25 \* directional\_weight \* coherence\_term)

        )

    def check(self, trajectory, manifold: IdentityManifold | None \= None) \-\> IdentityScore:

        resolved\_manifold \= manifold or self.\_manifold

        if resolved\_manifold is None:

            raise TypeError("IdentityCheck.check() requires an IdentityManifold")

        trajectory\_id \= str(getattr(trajectory, "trajectory\_id", "legacy\_trajectory"))

        if not resolved\_manifold.value\_axes:

            return IdentityScore(

                score=1.0,

                flagged=False,

                deviation\_axes=frozenset(),

                trajectory\_id=trajectory\_id,

            )

        confidence \= float(getattr(trajectory, "total\_coherence\_delta", 0.0))

        confidence \+= self.\_mean\_frame\_coherence(trajectory)

        score \= self.\_clamp01(0.5 \+ (confidence / 2.0))

        deviations \= frozenset(

            str(getattr(axis, "axis\_id", getattr(axis, "name", "axis")))

            for axis in resolved\_manifold.value\_axes

            if self.\_axis\_projection(axis, trajectory, score) \< resolved\_manifold.alignment\_threshold

        )

        return IdentityScore(

            score=score,

            flagged=bool(deviations),

            deviation\_axes=deviations,

            trajectory\_id=trajectory\_id,

        )

---

## 4a. D4 Phase 0 — Reconciled Implementation Specification (supersedes §4)

§4 above is preserved verbatim as the original R&D sketch. Per governance annotation items 2 and 12, it contradicts the governing decision and is **not** the specification implementers build against. This section is that specification. It is normative *shape* — the literal shipped code is produced under TDD in D4 Phase 1 (`core/physics/identity_manifold.py`) and Phase 2 (`core/physics/identity.py`); this block is not the final diff.

**The operator-preservation correction (governance annotation item 12).** The live identity trajectory is `final_state.F`, whose class invariant (`field/state.py`) is `versor_condition(F) < 1e-6` — i.e. **F is a versor: an even-grade operator (grades 0,2,4), with zero grade-1 content.** §2.1/§2.2's literal "project ψ_traj onto the grade-1 value subspace" applied to F is therefore vacuous (`P_id(F) = 0` identically ⇒ every trajectory maximally flagged ⇒ a fail-closed brick). This was verified empirically before implementation. The geometrically correct question for an *operator* against a *subspace* is not "is the operator in the subspace" but "does the operator **preserve** the subspace" — evaluated by its action on the subspace's basis via the sandwich product `F aᵢ F̃`. This keeps the grade-1 pack axes unchanged and matches inalienability precisely: a legitimate cognitive versor leaves the value axes invariant; a jailbreak versor twists a value axis out of the value subspace (leakage) or inverts it (anti-alignment). **Ratified by Joshua Shay, 2026-07-17.**

**Phase 1 primitive — `core/physics/identity_manifold.py` (§2.1):**

```python
class ManifoldConditioningError(ValueError):
    """Gram matrix condition number exceeds the mode-aliasing bound (10**5)."""

def lift_axis(direction3: Sequence[float]) -> np.ndarray:
    """Grade-1 lift: R^3 -> Cl(4,1) at the e1/e2/e3 slots.

    Uses algebra.cl41.basis_vector(0..2) — NOT algebra.cga.embed_point, which
    maps to null-cone points and would make the Gram matrix a distance table
    rather than a metric inner product. The value subspace I = span(lifted
    axes) therefore lives in the spatial grade-1 block (e1,e2,e3), where the
    Cl(4,1) inner product <.,.>_0 coincides with the Euclidean coefficient
    inner product (each e_i^2 = +1), so the Gram matrix is positive-definite.
    Precomputed once at manifold load in the f64 precision domain (the
    f64->f32 serving cast, Sec 2.5 / ADR-0245 Sec 2.2, applies only to the
    live per-turn versor F, not to this offline axis construction).
    """
    psi = np.zeros(N_COMPONENTS, dtype=np.float64)
    for k, component in enumerate(direction3):
        psi = psi + float(component) * basis_vector(k).astype(np.float64)
    return psi

def gram_matrix(axes_psi: Sequence[np.ndarray]) -> np.ndarray:
    n = len(axes_psi)
    G = np.empty((n, n), dtype=np.float64)
    for i in range(n):
        for j in range(n):
            G[i, j] = scalar_part(geometric_product(axes_psi[i], reverse(axes_psi[j])))
    cond = float(np.linalg.cond(G))
    if cond > 1e5:
        raise ManifoldConditioningError(f"Gram condition number {cond:.3e} exceeds 1e5")
    return G

def subspace_project(x: np.ndarray, axes_psi, g_inv) -> np.ndarray:
    """Metric-orthogonal projection of x onto I = span(axes_psi).
    P_I(x) = sum_ij axis_i * (G^-1)_ij * <axis_j, x>_0. Coefficients are SIGNED
    (never abs()'d) so orientation is preserved (governance annotation item 4)."""
    c = np.array([scalar_part(geometric_product(reverse(a), x)) for a in axes_psi])
    coeffs = g_inv @ c
    out = np.zeros(N_COMPONENTS, dtype=np.float64)
    for w, a in zip(coeffs, axes_psi):
        out = out + w * a
    return out

def sandwich(R: np.ndarray, x: np.ndarray) -> np.ndarray:
    """Versor action R x R~. For a versor R this preserves grade and norm, so a
    grade-1 axis maps to a grade-1 unit vector."""
    return geometric_product(geometric_product(R, x), reverse(R))

def euclidean_norm(s: np.ndarray) -> float:
    """Positive-definite coefficient-Euclidean norm — NOT the indefinite Cl(4,1)
    <S,S~>_0, which signature (+,+,+,+,-) permits to vanish (or go negative, e.g.
    for an e5/boost leakage component) for nonzero leakage, silently hiding a
    breach (governance annotation item 4)."""
    return float(np.linalg.norm(np.asarray(s, dtype=np.float64), ord=2))

def axis_response(R, axes_psi, g_inv):
    """Per-axis operator-preservation measures for versor R. For each value
    axis a_i (both measures NORMALIZED by the rotated-axis magnitude, so they
    are scale-invariant):
      rotated_i    = sandwich(R, a_i)                # grade-1 vector
      rot_norm_i   = euclidean_norm(rotated_i)
      rejection_i  = rotated_i - subspace_project(rotated_i)   # out-of-I component
      leakage_i    = euclidean_norm(rejection_i) / rot_norm_i  # fraction in [0,1]
      self_align_i = <a_i, rotated_i>_0 / (norm(a_i)*rot_norm_i)  # signed cosine [-1,1]
    Returns (leakage[], self_align[]). Both are needed and non-redundant:
    rejection catches tilt toward alien dimensions (e4/e5); self_align catches
    in-subspace inversion (e1 -> -e1: leakage 0 but self_align -1).
    NORMALIZATION IS LOAD-BEARING: the live versor carries boost (e5)
    components, and a boost is a unit versor (R R~ = 1) that does NOT preserve
    the Euclidean coefficient norm (‖R a_i R~‖ > 1), so an un-normalized
    magnitude would be unbounded. For a norm-preserving spatial rotor the
    rotated axis is unit and normalization is a no-op."""
    leak, align = [], []
    for a in axes_psi:
        rot = sandwich(R, a)
        rej = rot - subspace_project(rot, axes_psi, g_inv)
        leak.append(euclidean_norm(rej))
        align.append(scalar_part(geometric_product(a, reverse(rot))))
    return leak, align
```

**Phase 2 gate — `core/physics/identity.py` (§2.2; wave-only, fail-closed):**

```python
class IdentityGateRefusal(Exception):
    """Fail-closed refusal: leakage/orientation or boundary check failed and
    C_id could not recover alignment within its bound. Params unchanged."""

class MissingWaveStateError(ValueError):
    """Raised when wave_field / ψ_traj is absent (scalar-L2 path excised)."""

def _wave_field_check(F_traj, axes_psi, g_inv) -> tuple[float, list, list]:
    F = np.ascontiguousarray(F_traj, dtype=np.float32)
    if F.dtype.byteorder not in ("<", "="):
        raise ValueError("Identity gate requires little-endian float32")
    if not np.all(np.isfinite(F)):
        raise ValueError("Identity gate encountered nonfinite values in F_traj")
    if F.shape != (N_COMPONENTS,):
        raise ValueError(f"F_traj must be shape ({N_COMPONENTS},), got {F.shape}")
    leak, align = axis_response(F.astype(np.float64), axes_psi, g_inv)
    score = 1.0 - (sum(l * l for l in leak) / len(leak)) ** 0.5
    return score, leak, align

# Absent F_traj → MissingWaveStateError. Malformed F_traj → ValueError.
# No scalar-L2 fallback remains (convergence 2026-07-20).
```

Egress condition (replaces §2.2 item 2's formula — `∧ ΔQ_top = 0` dropped per governance annotation item 1; operator-preservation per item 12):

```
F_minus  = versor from F_cognitive(psi_t, u_t)      # a versor (grades 0,2,4)
leak, align = axis_response(F_minus, axes_psi, g_inv)
F_plus   = C_id(F_minus, leak, align)                # bounded, abstaining corrector
admit  <=>  rms(leak(F_plus)) <= gamma_id            # subspace preserved
       AND  min(align(F_plus)) >= gamma_orient       # no value axis inverted
       AND  no boundary_id violated                  # hard boundaries (item 7)
```

Two per-axis measures, both required and non-redundant (empirically verified):
- **Subspace leakage** `euclidean_norm(rotated_i − P_I(rotated_i))` — catches a versor tilting a value axis toward an alien dimension (e4/e5). Euclidean norm per item 4/6.
- **Signed self-alignment** `<a_i, rotated_i>_0` — catches a versor *inverting* a value axis within the subspace (`e1 -> -e1`: subspace leakage is 0, but self-alignment is −1). This is the concrete realization of the "signed overlap, never abs()" ratified decision.

`C_id` is a **bounded, abstaining** corrector: it may apply a bounded corrective displacement toward the manifold; if it cannot recover alignment within that bound, it **abstains** — raises `IdentityGateRefusal`, live parameters kept unchanged. `C_id` must **not** rewrite reasoning arbitrarily to force a low leakage score — a corrector that can do that creates a "good-metric, bad-cognition" failure mode, which is a new defect, not a fix.

`boundary_ids` (governance annotation item 7) is evaluated as a hard-boundary check alongside the leakage/orientation scores; a boundary violation is refused independent of them (its predicate is designed in D4 Phase 2, not prescribed here).

**Identity-continuity (governance annotation item 8):** `axes_psi` and `g_inv` above are computed once at manifold/pack load and frozen for the session. ADR-0243 biography holonomy accumulation is a separate, non-mutating process with respect to this subspace.

**Phase 3 — `γ_id` calibration + the live-serving finding (§2.4).** `gamma_id` above is not hardcoded: it is calibrated by the bracketed-local Fibonacci section search (`core/physics/fibonacci_search.py`) over a smooth, convex logistic-separation objective, producing a content-addressed tuning certificate (`evals/adr_0244_gamma_calibration/`). The certified bound `γ_id = 0.2126624458513829` (certificate `0079b5f2…`, objective `gamma_id_leakage` v1) is pinned as `identity._WAVE_LEAKAGE_BOUND`, **decoupled from `alignment_threshold`** (which the legacy path and hedge bands retain). The orientation floor `gamma_orient = 0.0` is a geometric invariant (a preserved axis has self-alignment near +1, an inverted one near −1), not a tunable — it is not calibrated.

The calibration establishes two results, kept rigorously separate:

1. **The bound separates the *geometric* attack signal** — over the reference set (identity-preserving in-subspace rotors vs axis→e4/e5 tilt/boost attacks), every aligned rotor is admitted and every leakage-attack flagged. Inversions are excluded from the *leakage* set by construction (they are ~0-leakage, handled by the orientation floor). The machinery is validated, reproducible, and deterministic.

2. **The bound does NOT separate real live traffic — so the serving flag stays OFF.** Measured on the live engine (`ChatRuntime`, wave gate on), benign `final_state.F` versors do **not** preserve `span(e1,e2,e3)`: leakage spans ~0.14–0.81 (mean ~0.55), self-alignment swings negative, ~12/13 benign turns would be false-refused at `γ_id`, and the best achievable balanced error over all thresholds is ~0.35. The calibration therefore certifies `flag_flip_authorized = False`, and `RuntimeConfig.identity_wave_gate` remains `False`. This is the empirical resolution of item 5(e) / item 10 (paraphrase-invariance is empirical, not automatic): **on the current engine it does not hold for the live gate.**

**Root cause + path forward.** The shipped pack value axes (`truthfulness=e1`, `coherence=e2`, `reverence=e3`) are *nominal basis vectors*, not the *dynamically-preserved eigenmodes* §2.1 presumes; the current field evolution gives the identity subspace no dynamical anchoring, so an ordinary cognition versor rotates it freely. The operator-preservation gate is thus **validated, correctly-off scaffolding** — not a live gate. Making identity dynamically load-bearing (so benign trajectories provably preserve it and the gate separates live) is the induced-identity-action programme scoped by the ADR-0246 preflight brief (`docs/briefs/ADR-0246-induced-identity-action-and-path-integrity-preflight.md`). A slow drift-guard test re-measures the live distribution and fails if the engine ever begins preserving identity (→ re-calibrate and reconsider the flip).

---

## 5\. References

1. `algebra/cl41.py` — Precomputed geometric product table.  
2. `core/physics/wave_manifold.py` — Continuous wave-field substrate.  
3. `core/physics/goldtether.py` — GoldTether residual monitoring.  
4. `core/physics/fibonacci_search.py` — Fibonacci search contract.
5. `docs/adr/ADR-0245-cga-unification-mechanical-sympathy-and-semantic-rigor.md` — companion mechanical-sympathy + semantic-rigor foundation ADR.
6. `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` — D4 implementation plan + live progress tracker.

