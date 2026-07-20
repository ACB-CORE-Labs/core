# ADR-0253: Master Blueprint ADR Collision Resolution & Dual-Pack Boundary

**Status**: Accepted (Stage 1 governance freeze)  
**Date**: 2026-07-20  
**Deciders**: CORE engineering (Master Convergence Stage 1)  
**Related**: `docs/adr/MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`, Master Architectural Specification 2026-07-20

## Context

The Master Blueprint §3.2 lists ADRs 0240–0253 with intent titles that **collide by number** with the repository’s already-Accepted ADR-0246 through ADR-0252 (and with other live 0240–0245 titles). Overwriting Accepted history is forbidden by repository governance and by the Stage 1 program rule.

Separately, language packs exist as both:

- **compiled runtime artifacts** under `packs/data/<pack_id>/`, and  
- **source/draft trees** such as `packs/he`, `packs/grc`, `packs/en`, `packs/el`.

Serve paths must not treat draft source trees as importable authority.

## Decision

1. **ID history is immutable.** Accepted ADR numbers keep their live titles and scopes. Blueprint intent titles never renumber Accepted ADRs.
2. **Mapping is the reconciliation surface.** The file  
   `docs/adr/MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md`  
   is the authoritative Blueprint-ID → repository-home table (Covered / Partial / Gap / reserved new IDs 0254–0261).
3. **This ADR-0253 number is claimed for governance freeze**, not for the Blueprint’s “Holonomy Primacy Rust SIMD” title. That Blueprint intent is reserved as **ADR-0261** if implemented later.
4. **Dual-pack boundary**  
   - Runtime serve/load of language packs uses `packs.compiler` → `packs/data/<pack_id>/` only.  
   - `packs/he`, `packs/grc`, and peer source trees are draft/source material; they are not serve-import authority.  
   - Architecture tests pin that serve-entry modules do not import `packs.he` / `packs.grc` as packages for serving.

## Consequences

- Stage 3/4 Blueprint work must open **new** ADR numbers (0254+) or amend the correct existing owner ADR — never 0246–0252 renames.
- CI fails if draft HE/GRC package imports appear on the serve import graph.
- Documentation that cites Blueprint ADR numbers for convergence work must also cite this mapping.

## Validation

- `tests/test_pack_draft_serve_boundary.py`
- Mapping file present and linked from `docs/adr/README.md`
