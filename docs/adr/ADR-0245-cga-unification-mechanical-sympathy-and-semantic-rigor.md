# ADR-0245: CGA Unification — Mechanical Sympathy, Boundary Rigor, and Eigendecomposition Memoization

**Status**: **Accepted** — ratified by Joshua Shay on 2026-07-17 (D4 acceptance-packet `docs/audit/adr-0245-acceptance-packet-2026-07-17.md`; §3 gate green — parity, f32 467× speedup, 0-LAPACK-on-repeat, collision-resistance).  
**Date**: 2026-07-17  
**Authors**: Joshua Shay \+ Multi-model R\&D  
**Traceability**: Notion R\&D (CORE Engineering Reference hub: Live-Entity Design Decisions, `core_HA` Patterns)  
**Related**: ADR-0003, ADR-0006, ADR-0010, ADR-0238, ADR-0241, ADR-0242, ADR-0243, ADR-0244 (companion — identity-gate consumer of this ADR's foundation), `algebra/cl41.py`, `core/physics/wave_manifold.py`

---

> **Governance annotation (D4 Phase 0 landing, 2026-07-17).** Committed **Proposed**, verbatim from the R&D export, so the record exists. The body below is unchanged; this annotation is editorial (added at landing) and carries the engineering status map + corrections.
>
> **Filename correction.** §2 Context and §4 References (item 4) cite `core/physics/multimodal_lifecycle.py`. That file does not exist. The real module implementing the ADR-0243 wave-field cognitive lifecycle is `core/physics/cognitive_lifecycle.py`. All decisions below (§2.2 in particular) apply to that file.
>
> **Status map — three of four decisions were already landed by the ADR-0244-cohesion-directive arc before this ADR was committed to the repo:**
>
> | § | Decision | Status |
> |---|---|---|
> | 2.1 | PyO3 Rust `geometric_product` f32 fast-path | ✅ **Done** — `algebra/backend.py`, pre-existing before this arc. |
> | 2.2 | Gated f64→f32 serving boundary | ✅ **Built (D4 Phase 4)** — `serving_cast(psi_steady, certificate, verdict) → ServingState` in `cognitive_lifecycle.py`. A single explicit, fail-closed down-cast at the certified egress: casts only a certified/admitted/digest-matched state, precision-checks the f32 result (fails closed on a cliff), and keeps f64 as the source of truth (the digest chain is untouched). Same contract as ADR-0244 §2.5. Pinned by `tests/test_adr_0244_serving_cast.py` (10 tests). |
> | 2.3 | Semantic rigor in content addressing (full 256-bit digest, no `default=str`, byte-order guard) | ✅ **Done (D4 Phase 5a)** — hot path fixed at D1; the residual contemplation/vault sites now full-digest: `schema._content_digest`, `plan_preflight._plan_substrate_hash`, `miners/articulation_quality` (dropped `default=str`), and `holographic_vault._default_mode_id` (full digest + explicit LE byte-order). No truncation, no `default=str`, no bare `.tobytes()` left in these content-addresses. |
> | 2.4 | `_cached_eigh` memoization (`functools.lru_cache`, keyed on `hamiltonian_id` + `matrix.tobytes()`) | ✅ **Done** — `core/physics/cognitive_lifecycle.py::_cached_eigh` (cohesion-directive D2), exactly as specified including the canonical two-part cache key. |
>
> **§3 acceptance gate — ✅ complete (D4 Phase 5d):**
>
> - **Accuracy & parity** (bit-identical Rust vs Python, N=10,000): ✅ done — `tests/test_geometric_product_f64_parity.py` (f64) + `tests/test_geometric_product_rust_parity.py` (f32, component-exact).
> - **Latency & throughput** (≥10× f32 speedup, Rust vs pure-Python): ✅ done — `tests/test_adr_0245_acceptance_gate.py::test_rust_f32_geometric_product_is_at_least_10x` (Rust-guarded; skips with reason where `core_rs` is unbuilt). Measured on Apple M-series: rust 2.86 µs/op vs python 1340 µs/op = **467×** (asserts a conservative ≥10× with a parity sanity check).
> - **Memory allocations / 0 LAPACK on repeat** (`_cached_eigh`): ✅ done — `tests/test_adr_0244_mechanical_sympathy.py` (cache hit returns identical objects → no fresh `eigh`).
> - **Collision resistance** (`_content_id`): ✅ done — `tests/test_adr_0245_acceptance_gate.py` (full 256-bit, type/structure-faithful, fail-closed on non-serializable; `_psi_digest` sub-epsilon sensitive).
>
> All four §3 legs are green and mapped by a coverage-manifest test. ADR-0245's D4 scope (§2.2 cast + §2.3 residual + §3 gate) is complete; see `docs/handoff/ADR-0244-D4-IMPLEMENTATION-PLAN.md` and `docs/analysis/adr-0244-cohesion-directive-audit-2026-07-17.md`.

---

## 1\. Context and Problem Statement

With the continuous wave-field substrate ($\\psi \\in Cl(4,1)$) of [ADR-0241](https://drive.google.com/file/d/1F_7QYtPysBP4qMbLGlGPnXgYx9IXug8nUYrpiCGSunE/view?usp=drivesdk), the deterministic Fibonacci-section search of [ADR-0242](https://drive.google.com/file/d/15_NECCPy-tEWGfYi_BNqawm8GytUTMkz1DsOqGVMXhI/view?usp=drivesdk), and the wave-field cognitive lifecycle of [ADR-0243](https://drive.google.com/file/d/1-ZtokpoiQZD7sdcX54monT_WNeBkUhJuyLPN4mLCEmk/view?usp=drivesdk) established, we perform a deep codebase audit against our three core design pillars: **Mechanical Sympathy, Semantic Rigor, and the Third Door**.

This audit reveals four critical performance bottlenecks and semantic gaps across the algebraic and physics boundaries:

- **Concern A: `geometric_product` CPython Loop**: The primary algebraic primitive in `algebra/cl41.py` executes a nested Python loop of $32 	imes 32 \= 1,024$ iterations. In the worst case (dense input), this burns \~40 µs per call on the M1, while a compiled, vectorised Rust FFI can compute the product in sub-microsecond cycles.  
- **Concern B: Float32 vs. Float64 serving boundary**: Numerical stable eigen-relaxation in `multimodal_lifecycle.py` requires double precision (`float64`) for LAPACK convergence, but the `IdentityCheck` gate in `identity.py` requires only `float32`. Carrying `float64` through the identity gate promotes `float32` axis directions to `float64` silently, halving M1 NEON SIMD vector throughput.  
- **Concern C: Hash Truncation and Silent Coercion**: Truncating the SHA-256 digest of content-addressed vault objects to 24 hex characters (96 bits) introduces a birthday-collision risk at $2^{48}$ entries. This can silently corrupt the Delta-CRDT merge semilattice. Furthermore, using `default=str` in `json.dumps` silently coerces non-serializable objects (collapsing different objects with identical string representations), and we lack explicit byte-order assertions on raw array bytes.  
- **Concern D: Redundant Eigendecompositions**: Performing LAPACK `eigh` on non-diagonal Hamiltonians takes 50–200 µs on M1. Because `ProblemHamiltonian` is frozen, immutable, and content-addressed, executing a fresh decomposition on identical instances wastes massive Apple Silicon AMX compute.

This ADR resolves these concern areas by establishing clear, high-assurance contracts that maximize performance and ensure semantic rigor.

---

## 2\. Decision and Architectural Formulation

We resolve these four concern areas by implementing the following high-assurance system-level decisions:

  \[Ingress Wave (f64)\] \---\> \[Eigendecomposition: Cached/eigh\] (AMX Optimized)

                                         |

                                         v

                            \[GoldTether / Certification\]

                                         | (Serves-Boundary Cast Contract)

                                         v

                             \[Live Wave-State (f32)\]

                                         |

                       \+-----------------+-----------------+

                       |                                   |

                       v (M1 NEON SIMD Lanes)              v (Domain-Separated 256-bit Hash)

          \[Rust cl41\_geometric\_product\]              \[Delta-CRDT Vault Storage\]

               (Gather-Scatter FFI)                     (Zero Collision Risk)

---

### 2.1 Decision 1: PyO3 Rust-Wired `geometric_product` Fast-Path

To achieve the performance declared in our system's README ("Rust computes algebra on the CPU with zero heap allocation in the hot path"), we wire the CPython `cl41.py` module to our native Rust extension:

1. **Fast-Path Delegation**: When the PyO3-compiled `_rust_cl41` module is available, and both operand arrays are of dtype `float32`, the product is delegated directly to the Rust binary:  
     
   def geometric\_product(A, B):  
     
       \# Fast path: Rust extension available and both are float32  
     
       if \_rust\_cl41 is not None and A.dtype \== np.float32 and B.dtype \== np.float32:  
     
           return \_rust\_cl41.cl41\_geometric\_product(A, B)  
     
       \# Fallback: Pure-Python Workbench path  
     
       ...  
     
2. **SIMD Vectorization**: The Rust kernel implements the product as an auto-vectorized (or NEON-explicit) gather-scatter operation over static precomputed tables, bypassing CPython interpreter overhead.  
3. **Parity Gate**: Both the Python fallback and the Rust fast-path must produce bit-identical results, verified programmatically by the existing testing suite.

---

### 2.2 Decision 2: Gated f64-to-f32 Serving Boundary

We establish the **Serves-Boundary Cast Contract** to resolve the tension between precision and execution throughput:

1. **The Precision Domain (`float64`)**: Eigendecomposition, Hamiltonian relaxation, and numerical validation remain inside the lifecycle and are evaluated in `float64` for LAPACK stability.  
2. **The Serving Boundary (`float32`)**: Upon successful certification, the relaxed wave-field $\\psi\_{	ext{steady}}$ is cast explicitly to `float32` before flowing to the `IdentityCheck` gate and linguistic readback paths. This doubles the vector throughput of every subsequent NEON SIMD operation on the M1, where `float32` precision is mathematically sufficient.

---

### 2.3 Decision 3: Semantic Rigor in Content Addressing

We secure our Delta-CRDT semilattice and audit trails from hash collision and silent coercion:

1. **96-bit Truncation Removal**: For the Delta-CRDT merge key, the `psi_digest` and all content-addressed vault objects (such as `TurnEvent` trace hashes) must retain the full **256-bit SHA-256 hex digest** (64 characters), removing the birthday-collision risk entirely. Truncation is permitted only on human-readable labels, never on machine merge keys.  
2. **Halt on Silent Coercion**: The `default=str` fallback is removed from `json.dumps` in `_content_id`. Any non-serializable metadata or parameter structure must raise a typed `TypeError` at the serialization boundary rather than silently collapsing different objects.  
3. **Byte-Order Guard**: Before serializing any array to raw bytes via `.tobytes()`, we enforce the canonical byte-order contract: `assert psi.dtype.byteorder in ('<', '=')` This guarantees that the resulting content-addressed digest remains identical across all little-endian platforms (M1/x86\_64).

---

### 2.4 Decision 4: Eigendecomposition Memoization

To prevent redundant LAPACK `eigh` calls on identical, frozen `ProblemHamiltonian` instances, we implement a memoized LAPACK solver:

1. **Caching Strategy**: The eigendecomposition is decorated with `functools.lru_cache(maxsize=128)`.  
2. **Canonical Cache Keys**: To make the cache completely collision-resistant, the cache key comprises both the `hamiltonian_id` and the immutable `matrix.tobytes()` of the Hamiltonian:  
     
   @functools.lru\_cache(maxsize=128)  
     
   def \_cached\_eigh(hamiltonian\_id: str, matrix\_bytes: bytes):  
     
       matrix \= np.frombuffer(matrix\_bytes, dtype=np.float64).reshape(32, 32\)  
     
       return np.linalg.eigh(matrix)  
     
   This saves up to 200 µs of AMX compute per redundant call on the active reasoning turn.

---

## 3\. Comparative Benchmarking (Phase 1 Acceptance Gate)

Before promoting these updates, the implementation must be validated against the **Falsifiability & Benchmark Framework** in the local calibration area:

- **Accuracy & Parity**: Verify that the PyO3 Rust extension and the Python fallback produce bit-identical multivector coefficients for $N \= 10,000$ random products.  
- **Latency & Throughput**: Compare the pure-Python loop against the Rust extension. The target threshold is a **$\\ge 10	imes$ speedup** for dense products under the Rust path.  
- **Memory Allocations**: Assert that `_cached_eigh` results in exactly 0 heap allocations and 0 LAPACK calls during repeated evaluations of a static Hamiltonian.  
- **Collision Resistance**: Prove that no two distinct metadata dictionaries can produce identical `_content_id` outputs under the strict, non-coerced JSON path.

---

## 4\. References

1. `algebra/cl41.py` — Legacy precomputed geometric product table.  
2. `core/physics/wave_manifold.py` — Unified wave-field substrate.  
3. `core/physics/goldtether.py` — GoldTether residual monitoring.  
4. `core/physics/multimodal_lifecycle.py` — Ingestion and articulation.  
5. `core-rs/src/vault.rs` — Rust FFI Delta-CRDT semilattice.
