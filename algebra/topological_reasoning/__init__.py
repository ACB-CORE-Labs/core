"""ADR-0242 V5 (D6) — topological anyon / braid holonomy research quarantine.

Fibonacci anyon fusion research surface. BLOCKED from production, serve, FFI,
chat/runtime, vault COHERENT, teaching mutation, and GoldTether production
paths until algebraic and numerical proofs exist (see package README).

This module intentionally re-exports nothing into ``algebra``'s public API
and must not be imported by production packages.
"""

from __future__ import annotations

# Canonical Fibonacci anyon fusion rule under study (research label only).
# τ ⊗ τ = 1 ⊕ τ  — not a production operator; no evaluation semantics.
FUSION_RULE: str = "tau_otimes_tau_eq_1_oplus_tau"
"""Research label for the Fibonacci anyon fusion rule τ⊗τ = 1⊕τ.

Docstring / constant only. Does not implement fusion, braiding, or holonomy.
"""

__all__ = ["FUSION_RULE"]
