# CGA Substrate Migration & Pack Registry Consolidation

## Overview

This PR completes the migration of the cognitive engine to the CGA (Conformal Geometric Algebra) substrate and the associated pack registry consolidation (language_packs → packs). The work enforces geometry-first principles, exact versor closure, and deterministic construction throughout the relevant paths.

## Lane History & Key Changes

- **Lane 1 (VersorBinding / ContractAssessment)**: Introduced `VersorBinding` and `ContractAssessment` as the authoritative geometric contract layer. Assessments now produce properly shaped 32-component payloads with `versor_error < 1e-6` enforcement.
- **Lane 3 (Geometric evaluation / organ migration)**: Derivations (e.g. `fraction_decrease`) now consume `ContractAssessment` bindings and drive calculations via `versor_apply` on the geometric payload (dilation rotors) instead of ad-hoc logic.
- **Lane 4 (Registry Consolidation)**: Full migration of `language_packs/` to `packs/`. All loaders, manifests, tests, and references updated.
- **Lane 5 (UI Trace Updates)**: Workbench UI test fixtures and traces updated for the new pack paths and geometric invariant evidence.
- **Final polish**: Removed stale paths in UI mocks; cleaned provider files (CLAUDE.md / GEMINI.md) to strict minimal per AGENTS.md; refactored the fraction-decrease geometric payload construction into a dedicated helper (evidence span → dilation versor using CGA hyperbolic encoding). No string parsing remains in the derivation organs themselves.

The geometric construction for parameterized cases like "decrease to N/M of" is currently implemented from evidence spans in the assessment layer (producing the appropriate cosh/sinh dilation versor). This can be extended to fully pack-driven parameterized `geometric_signature` entries in `senses.jsonl` + resolver support in followup work.

## Verification & Test Results

All relevant lanes were executed and are green:

- Pack / Registry / Language filter: **1141 passed**
- Cognition suite: **121 passed**, 1 skipped
- Algebra suite: **82 passed**, 50 skipped
- Workbench UI (Vitest, after path fixes): **73 files / 598 tests passed**

`uv run core test --suite smoke -q` and targeted versor/parity + architectural invariant tests also pass.

## Trust Boundaries & Invariants

- `versor_condition(F) < 1e-6` held by construction across injection, apply, anchoring, and assessment paths.
- Exact CGA inner-product recall only (no ANN/cosine).
- No normalization / drift repair outside owned boundaries (`algebra/versor.py`, `ingest/gate.py`, sanctioned session anchoring).
- No stochastic/LLM fallbacks in the deterministic path.
- Epistemic status and vault rules respected.
- Teaching / proposal paths unchanged in contract.

## Post-Merge Notes

- Clear `engine_state/` after this change (identity substrate and pack paths changed; ~16 warnings about stale checkpoints / continuity are expected and benign).
- The fraction / parameterized geometric signatures are evidence-driven today and ready for richer pack-provided support later.

This work is complete and ready to merge.
