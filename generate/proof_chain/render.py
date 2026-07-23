"""Deterministic surface rendering for a propositional ``EntailmentTrace``
(deduction-serve arc, Phase 1).

Renders the four ``Entailment`` outcomes into user-facing prose. Deterministic
templates only — no LLM, no synthesis; every visible token is either fixed
prose or a formula string ``to_deductive_logic`` produced directly from the
user's own text. This is the ONLY renderer for propositional-deduction
serving; it must not be confused with ``generate.determine.render`` (which
renders realized-structure DETERMINE answers — a different gear entirely).
"""

from __future__ import annotations

from generate.proof_chain.entail import (
    INCONSISTENT_PREMISES,
    Entailment,
    EntailmentTrace,
)


def render_entailment(
    trace: EntailmentTrace, premises: tuple[str, ...], query: str
) -> str:
    """The user-facing surface for a propositional deduction verdict.

    Every branch is a fixed template around the literal premise/query
    formula strings — no fabricated content. ``trace.outcome`` selects the
    template; REFUSED further branches on ``trace.reason`` since an
    inconsistent-premises refusal and an out-of-regime refusal warrant
    different honest phrasing.
    """
    given = "; ".join(premises)
    if trace.outcome is Entailment.ENTAILED:
        return f"Given: {given}. Your premises entail: {query}."
    if trace.outcome is Entailment.REFUTED:
        return (
            f"Given: {given}. Your premises entail the opposite of "
            f"{query} — it cannot hold."
        )
    if trace.outcome is Entailment.UNKNOWN:
        return (
            f"Given: {given}. Your premises don't settle whether "
            f"{query} — it holds in some cases and fails in others."
        )
    # REFUSED
    if trace.reason == INCONSISTENT_PREMISES:
        return (
            f"Given: {given}. Those premises are inconsistent — they "
            f"can't all be true, so I won't assert anything from them."
        )
    return f"Given: {given}. I can't evaluate {query} from that as stated."


__all__ = ["render_entailment"]
