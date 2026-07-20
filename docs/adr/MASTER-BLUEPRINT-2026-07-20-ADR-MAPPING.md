# Master Blueprint ADR Mapping (2026-07-20)

**Status**: Governing mapping for the Master Architectural Specification & System Convergence Blueprint (2026-07-20)  
**Policy**: Do **not** overwrite, renumber, or falsify Accepted ADR-0246 through ADR-0252.  
**Authority**: This mapping reconciles Blueprint §3.2 titles with the live `docs/adr/` registry.

## Collision rule

The Blueprint lists ADR-0240–0253 with intent titles that **collide by number** with already-Accepted repository ADRs (especially 0246–0252). Repository history wins for IDs. Blueprint *decisions* land as:

1. **Covered** — mapped to an existing Accepted ADR (or AGENTS.md / runtime_contracts) that already carries the intent; or  
2. **Amended** — small amendment to the correct existing ADR when scope already owns the decision; or  
3. **Newly allocated** — next free ADR number (starting ADR-0253+) for Blueprint intents with no home.

## Registry truth (live Accepted / Proposed)

| ID | Live title (repository) | Live status |
|----|-------------------------|-------------|
| 0240 | Analogical Transfer Validation Harness + Biography Holonomy Blade | Proposed |
| 0241 | Wave-Field Driven Hyperbolic Atlas and Resonant Algebraic Cognition | Accepted |
| 0242 | Deterministic Fibonacci Operators and Evidence-Gated Optimization | Accepted |
| 0243 | Wave-Field Cognitive Lifecycle | Accepted |
| 0244 | Wave-Field Identity Manifold and Inalienable Geometric Alignment | Accepted |
| 0245 | CGA Unification — Mechanical Sympathy, Boundary Rigor | Accepted |
| 0246 | Induced Identity Action and Path Integrity | Accepted |
| 0247 | Multi-Port Residual Protocol | Accepted |
| 0248 | Integrity-Coordinated Handoffs | Accepted |
| 0249 | Reader→Hamiltonian Compiler | Accepted |
| 0250 | Tier-2 Multi-Entity Arithmetic | Accepted |
| 0251 | Reader-Arc Recalibration | Partial / decision §§1–4 |
| 0252 | CORE Problem-Solving Paradigm | Accepted |
| 0253 | *(was vacant; reserved for governance — see below)* | — |

## Blueprint intent → home

| Blueprint ID / title (intent) | Resolution | Home in repository |
|-------------------------------|------------|--------------------|
| BP-0240 Cl(4,1) Conformal Wave-Field Sovereignty & Pipeline Integration | **Covered (multi-home)** | `AGENTS.md` invariants + ADR-0241 + ADR-0244 + cognitive pipeline contracts; do not steal ADR-0240 number from biography harness |
| BP-0241 Holographic Standing-Wave Storage & Resonant Recall | **Covered** | ADR-0241 (live title differs; wave/resonant substrate) + holographic vault research quarantine |
| BP-0242 Deterministic Fibonacci Operators & Bounded Local Search | **Covered** | ADR-0242 |
| BP-0243 Wave-Field Cognitive Lifecycle & Multimodal Ingress | **Covered** | ADR-0243 |
| BP-0244 Wave-Field Identity Manifold & Gram Subspace Projection | **Covered** | ADR-0244 |
| BP-0245 CGA Unification, PyO3 Fast-Paths, f64→f32 Boundary | **Covered** | ADR-0245 |
| BP-0246 Smith Chart Conformal Interconnect Grammar | **Gap / new allocation** | Not ADR-0246 (that ID is Induced Identity Action). Allocate **ADR-0254** if/when interconnect grammar is implemented |
| BP-0247 Multi-Step Inductive Closure & Conformal Atom Unification | **Gap / Stage 3** | Not ADR-0247 (Multi-Port Residual). Partial telemetry in `CognitiveTurnPipeline._proof_atom`. Allocate **ADR-0255** for full fixed-point closure |
| BP-0248 Fail-Closed Hebrew Root-Sense Ambiguity Policy | **Gap / Stage 3–4** | Not ADR-0248 (Integrity Handoffs). Allocate **ADR-0256** |
| BP-0249 Active Dual-Correction Backpressure Signaling | **Partial cover** | Backpressure types live under `core/cognition/backpressure.py`; not ADR-0249 (Reader compiler). Map intent to existing backpressure module; new ADR **0257** only if policy must be re-decided |
| BP-0250 Autonomous Geometric Promotion SPECULATIVE→COHERENT | **Covered (vault)** | `vault/store.py` promotion + `teaching.epistemic.EpistemicStatus`; not ADR-0250 (Tier-2 arithmetic). Document in vault/teaching ADRs; optional **ADR-0258** if geometric promotion conditions need a dedicated decision |
| BP-0251 Delta-CRDT Vault Serialization & 256-bit Digest Integrity | **Partial cover** | Digests: `multivector_content_digest` / vault metadata; CRDT claims must not overwrite ADR-0251. Allocate **ADR-0259** only if Delta-CRDT is newly decided |
| BP-0252 Low-Discrepancy Mode Centroid Sunflower Allocator | **Gap** | Not ADR-0252 (Problem-Solving Paradigm). Allocate **ADR-0260** if implemented |
| BP-0253 Holonomy Primacy Enforcement in Rust PyO3 SIMD Kernels | **Gap** | No live ADR-0253 holonomy doc. Allocate **ADR-0261** for holonomy/Rust primacy if needed |

## Governance ADRs allocated by Stage 1

| New ID | Title | Purpose |
|--------|-------|---------|
| **ADR-0253** | Master Blueprint ADR Collision Resolution & Dual-Pack Boundary | This freeze: mapping policy + dual-pack serve isolation (does **not** claim Blueprint holonomy content) |

Numbers **0254–0261** are **reserved** for Blueprint intents listed as Gap above; they are not materialised until the owning stage implements them.

## Dual-pack boundary (summary)

| Tree | Role | Serve authority |
|------|------|-----------------|
| `packs/data/<pack_id>/` | **Compiled runtime** language packs (manifest + lexicon + checksums) | **Yes** — via `packs.compiler.load_pack` |
| `packs/he`, `packs/grc`, `packs/en`, `packs/el`, … | **Source / draft** language material (morphology, lemmas, probes) | **No** as Python import for serve; compile into `packs/data` first |
| `packs/safety`, `packs/identity`, `packs/ethics`, … | Governance/style modality packs | Serve via dedicated loaders |

Enforcement: architecture test `tests/test_pack_draft_serve_boundary.py`.

## Non-goals

- Renaming or rewriting Accepted ADR-0246–0252 bodies to match Blueprint titles  
- Claiming Stage 3/4 decisions complete by documentation alone  
- Force-fitting Blueprint numbers onto Accepted history  
