# Topological Reasoning — ADR-0242 Vector 5 (D6) Research Quarantine

**Status**: 🔴 RESEARCH ONLY — blocked from production  
**Authority**: ADR-0242 Vector 5 (topological anyon / braid holonomy)  
**Related**: `docs/adr/ADR-0242-atlas-packing-and-fibonacci.md`,  
`docs/analysis/fibonacci_applications_in_core_substrate.md` §2.2

---

## Purpose

Isolated study surface for Fibonacci anyon fusion and braid holonomy as a
**topological composition research program**. The canonical fusion rule under
study is:

\[
\tau \otimes \tau = \mathbf{1} \oplus \tau
\]

This package exists so research stubs, notes, and future proof-carrying
algebra can land **without** contaminating the live cognitive path:

```text
listen → comprehend → recall → think → articulate → learn → replay
```

## Hard quarantine (do not violate)

Until algebraic **and** numerical proofs exist, and until an explicit ADR
promotion gate is Accepted by human review, this package is **BLOCKED** from:

| Surface | Rule |
|---------|------|
| Production runtime | No imports from serve / hot path |
| `chat/` | Not for import by chat or `chat/runtime.py` |
| Serve / FFI | Must not enter serve or FFI bindings |
| `core/physics/` | Not a production physics operator |
| `generate/` | Not for articulation / planner / cognitive turns |
| `vault/` | Not for vault standing, seal, or COHERENT promotion |
| `teaching/` | Not for reviewed teaching or pack mutation |
| GoldTether / κ paths | Not for production residual / κ optimization |
| `algebra` public surface | Not re-exported from `algebra/__init__.py` |

Architectural pin: `tests/test_adr_0242_topological_quarantine.py` scans
production packages for any import of `topological_reasoning` and must find
none.

## Sovereignty (ADR-0242)

Fibonacci / topological operators may **never** dictate proposition truth,
safety policy, identity, or authorize autonomous COHERENT promotion. Active
reasoning remains governed by versor closure, exact CRDT recall, and
human-gated review.

## What is allowed here

- Research constants and docstring contracts (e.g. fusion rule labels)
- Future proof sketches, numerical experiments under tests/evals only when
  explicitly gated
- Documentation of open questions and proof obligations

## What is not allowed here

- Production logic wired into cognition, serve, or vault truth
- Stochastic / approximate substitutes for exact CGA recall
- Hidden normalization or drift repair outside owned algebra boundaries
- Silent promotion of research results into COHERENT standing

## API note

The package may expose minimal docstring / constant stubs (e.g. `FUSION_RULE`).
No production operators, no side effects, no I/O.

## Promotion path

1. Algebraic + numerical proofs land and are reviewable.  
2. ADR update records evidence and remaining risks.  
3. Human Accept of a production promotion gate.  
4. Only then may a **separate**, reviewed integration surface be designed —
   still subject to serve quarantine and sovereignty invariant.

Until then: this directory is a quarantine box, not a feature.
