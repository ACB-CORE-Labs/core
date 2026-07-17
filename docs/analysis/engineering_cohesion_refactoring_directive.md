# Technical Directive: Re-aligning the CORE Physics Layer with the Three Engineering Pillars

**Status**: Mandatory (gated on local Phase 1 evaluation suites)  
**Target Audience**: CORE Engineering, Runtime, and Mathematics Teams  
**Date**: 2026-07-17  
**Traceability**: ADR-0241, ADR-0242, ADR-0243, ADR-0244, `core-labs/core` Main Branch  
**Canonical path**: `docs/analysis/engineering_cohesion_refactoring_directive.md`

---

## Executive Summary

A comprehensive, code-level audit of the recent integrations of **ADR-0241 (Wave-Field Substrate)**, **ADR-0242 (Fibonacci Operators)**, and **ADR-0243 (Cognitive Lifecycle)** has revealed minor but critical structural drift between our active implementation and the repository's three core design pillars: **Mechanical Sympathy, Semantic Rigor, and the Third Door**.

While the mathematical formulations are correct, our execution layer has quietly defaulted to CPython-layer heuristics, implicit numerical types, truncated address-spaces, and redundant LAPACK decompositions. This directive outlines the mandatory refactoring steps to eliminate these performance bottlenecks and semantic gaps on Apple Silicon M1 (UMA, AMX, NEON SIMD) and solidifies the system's structural integrity.

---

## Section 1: Hot-Path Refactoring Mandates (Pillar I — Mechanical Sympathy)

### Mandate 1: Wire the Rust PyO3 `geometric_product` Fast Path

* **The Drift**: `cl41.py::geometric_product` currently runs a nested CPython loop of $32 	imes 32 \= 1,024$ iterations. For dense wave-fields, this burns \~40 µs per call, entirely leaving the M1's NEON SIMD unit idle.  
* **Refactoring Requirement**: We must immediately wire the Python-layer `geometric_product` to our compiled Rust extension (`_rust_cl41`). The Python implementation must be preserved strictly as a bit-identical fallback/Workbench path.  
* **Actionable Code**:  
    
  \# algebra/cl41.py  
    
  try:  
    
      import \_rust\_cl41  
    
  except ImportError:  
    
      \_rust\_cl41 \= None  
    
  def geometric\_product(A, B):  
    
      \# Fast path: Rust compiled extension (SIMD-vectorised gather-scatter on CPU)  
    
      if \_rust\_cl41 is not None and A.dtype \== np.float32 and B.dtype \== np.float32:  
    
          return \_rust\_cl41.cl41\_geometric\_product(A, B)  
    
            
    
      \# Fallback: Pure-Python/NumPy Workbench path  
    
      result \= np.zeros(32, dtype=np.float32)  
    
      for i in range(32):  
    
          ai \= A\[i\]  
    
          if ai \== 0.0:  
    
              continue  
    
          for j in range(32):  
    
              bj \= B\[j\]  
    
              if bj \== 0.0:  
    
                  continue  
    
              result\[\_TABLE\_IDX\[i, j\]\] \+= \_TABLE\_SIGN\[i, j\] \* ai \* bj  
    
      return result

### Mandate 2: Implement `_cached_eigh` for Eigendecomposition Memoization

* **The Drift**: `relax_to_ground` performs a fresh LAPACK `np.linalg.eigh` on every call for non-diagonal Hamiltonians, wasting 50–200 µs of AMX compute per redundant call on identical, frozen `ProblemHamiltonian` instances.  
* **Refactoring Requirement**: Decorate the LAPACK solver with `functools.lru_cache(maxsize=128)` using the immutable `hamiltonian_id` and `matrix.tobytes()` as canonical keys to guarantee collision resistance.  
* **Actionable Code**:  
    
  \# core/physics/cognitive\_lifecycle.py  
    
  import functools  
    
  @functools.lru\_cache(maxsize=128)  
    
  def \_cached\_eigh(hamiltonian\_id: str, matrix\_bytes: bytes) \-\> Tuple\[np.ndarray, np.ndarray\]:  
    
      matrix \= np.frombuffer(matrix\_bytes, dtype=np.float64).reshape(32, 32\)  
    
      return np.linalg.eigh(matrix)  
    
  \# Inside relax\_to\_ground / solve\_via\_relaxation:  
    
  def relax\_to\_ground(hamiltonian: ProblemHamiltonian, psi: np.ndarray) \-\> np.ndarray:  
    
      if hamiltonian.is\_diagonal:  
    
          \# Fast path (Third Door)  
    
          evals \= hamiltonian.matrix.diagonal()  
    
          evecs \= np.eye(32, dtype=np.float64)  
    
      else:  
    
          \# Cached AMX-optimized LAPACK path  
    
          evals, evecs \= \_cached\_eigh(hamiltonian.hamiltonian\_id, hamiltonian.matrix.tobytes())  
    
      ...

### Mandate 3: Enforce the Serves-Boundary Cast Contract ($f64 	o f32$)

* **The Drift**: Eigen-relaxation operates in `float64` for numerical precision, but the identity gate (`IdentityCheck`) operates in `float32`. The un-cast handoff silently promotes `float32` axis directions to `float64` at the projection layer, halving NEON SIMD register lane throughput.  
* **Refactoring Requirement**: Cast the certified wave-field ($\\psi$) to `float32` at the serving boundary (before handing to `IdentityCheck`). The `RelaxationCertificate` retains the `float64` byte-digest as the uncorrupted audit trail.

---

## Section 2: Corrective Actions for Boundary Safety (Pillar II — Semantic Rigor)

### Mandate 4: Eradicate `default=str` and Restore Full 256-bit SHA-256 Keys

* **The Drift**: Truncating the SHA-256 digest of content-addressed vault objects to 24 hex characters (96 bits) introduces a birthday-collision risk at $2^{48}$ entries, which can silently corrupt the Delta-CRDT merge semilattice. Secondly, using `default=str` in `json.dumps` silently coerces non-serializable objects, collapsing different objects with identical string representations.  
* **Refactoring Requirement**:  
  - Remove `default=str` from `_content_id` to enforce fail-closed behavior on non-serializable elements.  
  - Preserve the full **256-bit SHA-256 hex digest** (64 characters) for all content-addressed CRDT vault merge keys and `TurnEvent` trace hashes.  
* **Actionable Code**:  
    
  \# core/physics/identity.py / core/physics/cognitive\_lifecycle.py  
    
  def \_content\_id(payload: Mapping\[str, Any\]) \-\> str:  
    
      \# DO NOT use default=str; let non-serializable types raise TypeError (fail-closed)  
    
      raw \= json.dumps(payload, sort\_keys=True, separators=(",", ":"))  
    
      return hashlib.sha256(raw.encode("utf-8")).hexdigest()  \# Retain full 64-char 256-bit digest

### Mandate 5: Enforce the Little-Endian Float64 Byte-Order Assertion

* **The Drift**: Generating `psi_digest` via `psi.tobytes()` is platform-dependent: it produces little-endian bytes on standard Apple Silicon M1 and x86\_64, but lacks an explicit contract in the codebase.  
* **Refactoring Requirement**: Ensure that the array is explicitly coerced to little-endian float64 before extracting raw binary bytes for hashing.  
* **Actionable Code**:  
    
  def \_psi\_digest(psi: np.ndarray) \-\> str:  
    
      \# Explicitly assert and coerce to little-endian float64 before hashing  
    
      arr \= np.ascontiguousarray(psi, dtype=np.float64)  
    
      \# Force little-endian to ensure cross-platform auditability  
    
      arr\_le \= arr.astype(np.dtype(np.float64).newbyteorder('\<'))  
    
      return hashlib.sha256(arr\_le.tobytes()).hexdigest()

### Mandate 6: Implement the "No Sampled Unimodality Violation" Contract

* **The Drift**: The previous implementation claimed to "verify the unimodality assumption" of the Fibonacci-section search. However, a finite sample cannot prove global unimodality on the unsampled portions of $\[a, b\]$, and the algorithm used `kappa = 1.0` as a fallback, which silently changes behavior (a hot-path repair violation).  
* **Refactoring Requirement**:  
  - Rename the validator check to `sampled_unimodality_violation_observed`.  
  - Treat the Fibonacci search strictly as a **Bracketed Local** refinement operator. The caller must provide a pre-bracketed unimodal interval around a known minimum.  
  - If a violation (multi-extrema, flat plateaus) is observed, the operator must raise or return a typed `OptimizationFailure`. It is strictly forbidden from silently defaulting parameters in-path; the active parameters must remain unchanged.

---

## Section 3: Strategic Architecture (Pillar III — Third Door)

### Mandate 7: Enforce Insertion-Order Independent Mode Allocation

* **The Drift**: Registering new standing-wave mode centroids in the Hyperbolic Atlas using golden-angle or sunflower placements is sequential and susceptible to order sensitivity. If replicas register modes in different arrival orders, they will reconstruct different physical layouts, breaking exact-recall.  
* **Refactoring Requirement**:  
  - Define `AnchorAllocator` as a pure strategy interface.  
  - Centroid ordinals must be derived strictly from a deterministic CRDT order or a canonical sorted ID rank: $$	ext{ordinal} \= 	ext{rank}(	ext{canonical\_mode\_id})$$ This guarantees that the entire anchor layout is successfully reconstructed on-the-fly from the allocator identity and the ordinal sequence, preserving the *reconstruction-over-storage* doctrine.

---

## Section 4: Phase 1 Acceptance Gate (Evaluation Quarantine)

Every refactored module must reside strictly inside the `evals/` and `calibration/` quarantine zones until it passes the following six high-assurance criteria:

1. **Accuracy & Parity**: The PyO3 Rust extension and the Python fallback must yield bit-identical multivector coefficients for $N \= 10,000$ random products.  
2. **Deterministic Replay**: Running `IdentityCheck().check(wave_traj)` repeatedly with identical wave-field inputs must yield matching 256-bit trace hashes across different execution environments.  
3. **Falsifiability Gating**: The `IdentityCheck` must correctly identify and flag known non-resonant wave-field perturbations (e.g., pure bivector noise on a scalar identity axis) under the exact $Cl(4,1)$ inner product.  
4. **Honest Failure Gating**: Malformed wave functions, nonfinite values, or degenerate bounds must immediately trigger typed exceptions (`ValueError` / `OptimizationFailure`), rather than silently falling back to legacy paths.  
5. **Autonomy Invariant**: No search outcome, self-authored proposal, or live-state correction may autonomously modify the active manifold, truth state, or safety/ethics packs without explicit, human-gated review and signed ratification.

---

**Authorized Signatory**:  
Joshua Shay, Lead Architect  
**Approval Date**:  
2026-07-17  
