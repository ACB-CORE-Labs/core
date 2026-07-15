# CRDT vs Bit-Exact Determinism: Decision Dossier

## 1. What exists: Claimed vs Implemented

The `core_ha` unification memo claimed state sync is built on "commutative, associative, idempotent sharded Delta-CRDT registers." The audit reveals a split between the Python layer and the Rust substrate. 

| Component | Claim | Implementation Reality | Evidence |
| :--- | :--- | :--- | :--- |
| **Python Sync** (`core/sync/`) | Delta-CRDT registers | Journal / Object Store only (No CRDT semantics) | `core/sync/*.py` (no `merge`, `semilattice`, or `join` logic exists). |
| **Rust Vault** (`core-rs`) | Delta-CRDT semilattice | **Real CRDT Semilattice** | `core-rs/src/vault.rs:276` defines `SemilatticeDelta` trait ensuring commutative, associative, and idempotent join operations. |
| **Determinism Mechanism** | Exact-recall via CRDT | **Single-writer Bit-Exact Codec** | `core/array_codec.py` enforces bit-exact deterministic persistence by encoding arrays to `{"dtype", "shape", "b64"}`. |

The true determinism mechanism today relies on bit-exact base64 array serialization (`core/array_codec.py`) coupled with a single-writer `VaultStore` (Shape B+). 

## 2. What the one-continuous-life telos actually needs

The "one continuous life" vision requires determinism across sessions. Right now, the architecture operates in a **single-writer** paradigm where a single agent resumes its own state. In this paradigm, bit-exact serialization (`array_codec.py`) is both necessary and sufficient for exact-recall replay.

A CRDT becomes load-bearing only when we cross into **multi-writer / multi-agent sync**, where concurrent, unsynchronized writes must resolve to a deterministic canonical state. 
Is the CRDT just a namesake? No. `tests/test_audio_crdt_merge.py` proves a real semilattice is in use for specialized domains (Audio). It rigorously tests `hash(Sequential) == hash(Concurrent)`, commutativity, associativity, and idempotence. However, this mathematically rigorous CRDT merge is not yet wired into the general `core/sync/` state layer.

## 3. Two honest paths + recommendation

### Path A: Build the Delta-CRDT layer now
* **Scope:** Lift the `SemilatticeDelta` logic from `core-rs/src/vault.rs` into `core/sync/`, replacing the pure object-store/journal pattern with real Delta-CRDTs for all field state.
* **Benefits:** Achieves the "one continuous life" future-state immediately, supporting multi-agent collaboration natively.
* **Risks:** High risk to the current exact-recall replay guarantees. CRDT merges introduce non-linear history resolution, which complicates the bit-exact reproducibility currently achieved by `array_codec.py`.

### Path B: Correct the core_ha doc and defer CRDT
* **Scope:** Correct the `core_ha` doc to state single-writer bit-exact determinism is the actual mechanism, and defer CRDT behind an explicit multi-writer gate.
* **Benefits:** Honors the "field = electricity" principle with maximum fidelity to the codebase. It avoids building speculative complexity before the multi-agent requirement is fully active.
* **Risks:** The multi-writer capability is delayed.
* **Trigger condition:** Revisit Path A explicitly when multi-agent shared-vault concurrency becomes a baseline requirement.

### Recommendation: Path B
**Recommend Path B.** The implementation is more correct than the blueprint's original speculative phrasing. Single-writer bit-exactness is solid, proven, and running in production. We should correct the doc to reflect reality and place the general Delta-CRDT behind an explicit "multi-writer" gate for the future. We must not leave a false claim floating in the blueprints, nor should we hastily build a CRDT layer where single-writer bit-exact serialization perfectly serves the immediate requirement.
