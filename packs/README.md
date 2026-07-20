# Runtime Pack Artifacts

`packs/` holds runtime pack **artifacts**, **source language trees**, and **compilers/loaders**.

## Dual-pack boundary (ADR-0253 / Master Blueprint Stage 1)

| Path | Role | Serve / runtime authority |
|------|------|---------------------------|
| `packs/data/<pack_id>/` | **Compiled runtime** language packs (`manifest.json`, `lexicon.jsonl`, checksummed companions) | **Yes** — only via `packs.compiler.load_pack` / `load_pack_entries` |
| `packs/he`, `packs/grc`, `packs/en`, `packs/el`, … | **Source / draft** language material (lemmas, morphology, probes, pack.toml) | **No** — not importable serve authority; compile into `packs/data` first |
| `packs/safety`, `packs/identity`, `packs/ethics`, `packs/register`, `packs/anchor_lens`, modality packs | Governance / style / modality artifacts | Yes — via their dedicated loaders |
| `packs/primitives`, `packs/schema.py`, `packs/compiler.py`, `packs/loader.py` | Schemas, compilers, loaders | Tooling / load path only |

**Hard rule:** Durable pack mutation is reviewed or proof-carrying. Do not write ad hoc runtime pack files from serve.

## Compilers (two different boundaries)

| Compiler | Consumes | Produces |
|----------|----------|----------|
| `packs.compiler` | Reviewed pack data under `packs/data` | Runtime vocab / manifold structures |
| `core_ingest.compiler` | External candidate pressure | Validation reports + provisional learning artifacts |

The shared word “compiler” means deterministic lowering across a trust boundary; source material and outputs differ.

## Mutation

Durable changes must use the relevant validator/ratification lane. Session or speculative state must not masquerade as compiled pack COHERENT authority.

## Validation

Architecture pin: `tests/test_pack_draft_serve_boundary.py`  
Mapping: `docs/adr/MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`
