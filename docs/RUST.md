# Rust Extension (core-rs)

## Why Rust

The active Rust extension is an opt-in native substrate for parity-gated hot
paths, not a shadow cognition path. These operations currently justify Rust:

1. `geometric_product` — O(32^2) = 1024 multiply-adds per call, called 2-3x per `versor_apply`
2. `vault_recall` scan — O(N) CGA inner product calls, N = all stored versors, called during generation recall
3. `cga_inner` — called by vocabulary/proposition nearest selection and vault recall
4. `diffusion_step` — zero-copy graph diffusion over `(N, 32)` field buffers

None of the Python fallback paths release the Python GIL. Rayon gives
`vault_recall` true multithreaded parallelism across CPU cores. The geometric
product loop is cache-friendly and compiler-optimized in release mode.

## What is in Rust

| Module | Rust file | Why |
|---|---|---|
| Cl(4,1) product | `cl41.rs` | Hot inner loop, 1024 MADs |
| Versor ops | `versor.rs` | 3x geometric product per field step |
| CGA inner product | `cga.rs` | Called by nearest search and recall |
| Vault top-k scan | `vault.rs` | Rayon parallel scan |
| Graph diffusion | `diffusion.rs` | Zero-copy field graph step |

## What stays in Python

| Layer | Why |
|---|---|
| `VocabManifold` | Word/morphology/language metadata and exact candidate filtering |
| `SessionContext` | Orchestration, not arithmetic |
| `FieldState` | Plain dataclass |
| `PersonaMotor` | Motor construction is infrequent |
| `holonomy_encode` | Python-canonical until a native port proves byte-for-byte parity with position-rotor/f64 construction semantics |
| `propagate_batch` | Not an active runtime surface; future native propagation must use closure-preserving `versor_apply` semantics |

## Buffer Semantics

Scalar multivector bindings validate numpy-compatible arrays of length 32,
copy them into fixed stack arrays, execute the kernel, and return a new numpy
array. Bulk bindings (`vault_recall`, `diffusion_step`) consume contiguous
numpy buffers via `PyReadonlyArray` views so they avoid Python-list marshalling.
The Python fallback remains behaviorally available when `core_rs` is not
installed or `CORE_BACKEND=rust` is not explicit. A fresh root install is
therefore correct without the native extension, but not mechanically optimal.

## Build / Activate

Requires a Rust toolchain and maturin. Prefer the uv-native flow so the repo does not depend on `pip` being installed inside `.venv`:

```bash
core rust status
core rust test
core rust build
core rust status --require-active
```

`core rust build` and `core rust test` set
`PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1` for their subprocesses so PyO3 0.21 can
build from Python 3.13+ uv environments. Operators who need a specific Python
interpreter can still override with `PYO3_PYTHON`.

Equivalent explicit maturin command:

```bash
uv run --with maturin maturin develop --release --manifest-path core-rs/Cargo.toml
```

Verify Rust backend is active from Python:

```bash
uv run python -c "from algebra.backend import using_rust; print(using_rust())"
```

Expected:

```text
True
```

## Running Rust Tests

```bash
core rust test
# or
PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1 cargo test --release --manifest-path core-rs/Cargo.toml
```

## Type Safety Contract

All multivectors entering the Rust layer must be numpy-compatible `float32` arrays of length 32. Type errors surface as Python `ValueError` rather than silent memory corruption.

## Failure Mode

If `core_rs` is absent or fails to import, `algebra.backend` silently falls back to Python. This keeps the engine correct but not mechanically optimal. Use:

```bash
core doctor
core doctor --rust --require-rust
```

`core doctor` reports whether `core_rs` is importable without failing the Python
runtime. `core doctor --rust --require-rust` fails fast when benchmarking or
profiling requires the Rust backend.
