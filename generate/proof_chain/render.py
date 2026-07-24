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

#: A/E/I/O categorical form → an English sentence template over (subject, predicate).
_CATEGORICAL_PHRASE = {
    "A": "all {s} are {p}",
    "E": "no {s} are {p}",
    "I": "some {s} are {p}",
    "O": "some {s} are not {p}",
}


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


def render_entailment_english(
    trace: EntailmentTrace, premise_texts: tuple[str, ...], query_text: str
) -> str:
    """The user-facing surface for an English-clause (Band v2-EN) verdict.

    Same four-outcome discipline as :func:`render_entailment`, but the visible
    tokens are the user's own normalized clauses (``EnglishArgument`` texts),
    not formula strings. The ONE deliberate divergence is the UNKNOWN template:
    an opaque-atom "doesn't settle" is only true *of the reading* (internal
    clause structure this band did not parse could settle it — ADR-0257 §3),
    so the phrasing scopes the claim to that reading explicitly. ENTAILED /
    REFUTED / inconsistent are substitution-closed — true under any deeper
    reading — and are stated at full strength.
    """
    given = "; ".join(premise_texts)
    if trace.outcome is Entailment.ENTAILED:
        return f"Given: {given}. Your premises entail: {query_text}."
    if trace.outcome is Entailment.REFUTED:
        return (
            f"Given: {given}. Your premises entail the opposite of "
            f"{query_text} — it cannot hold."
        )
    if trace.outcome is Entailment.UNKNOWN:
        return (
            f"Given: {given}. Reading each clause as one indivisible claim, "
            f"your premises don't settle whether {query_text} — it holds in "
            f"some cases and fails in others."
        )
    # REFUSED
    if trace.reason == INCONSISTENT_PREMISES:
        return (
            f"Given: {given}. Those premises are inconsistent — they "
            f"can't all be true, so I won't assert anything from them."
        )
    return f"Given: {given}. I can't evaluate {query_text} from that as stated."


def render_entailment_member(
    trace: EntailmentTrace, premise_texts: tuple[str, ...], query_text: str
) -> str:
    """The user-facing surface for a member-argument (Band v3-MEM) verdict.

    Same discipline as :func:`render_entailment_english`; the UNKNOWN template
    scopes itself to THIS band's reading (ADR-0258 §3): distinct names are
    read as distinct individuals and class words at face value — co-reference
    or an unlinked class identity could settle what the lowering leaves open,
    so the claim is stated of the reading, disclosed as such. ENTAILED /
    REFUTED / inconsistent survive any such refinement (instantiation is
    sound and entailment is monotone) and are stated at full strength.
    """
    given = "; ".join(premise_texts)
    if trace.outcome is Entailment.ENTAILED:
        return f"Given: {given}. Your premises entail: {query_text}."
    if trace.outcome is Entailment.REFUTED:
        return (
            f"Given: {given}. Your premises entail the opposite of "
            f"{query_text} — it cannot hold."
        )
    if trace.outcome is Entailment.UNKNOWN:
        return (
            f"Given: {given}. Reading each name as one individual and each "
            f"class word at face value, your premises don't settle whether "
            f"{query_text} — it holds in some cases and fails in others."
        )
    # REFUSED
    if trace.reason == INCONSISTENT_PREMISES:
        return (
            f"Given: {given}. Those premises are inconsistent — they "
            f"can't all be true, so I won't assert anything from them."
        )
    return f"Given: {given}. I can't evaluate {query_text} from that as stated."


def render_entailment_verb(
    trace: EntailmentTrace, premise_texts: tuple[str, ...], query_text: str
) -> str:
    """The user-facing surface for a verb-predicate (Band v5-VP) verdict.

    Same discipline as :func:`render_entailment_member`; the UNKNOWN template
    additionally scopes the verb reading (ADR-0260 §3): each verb phrase is
    read at face value — an unlinked agreement form or an unstated relation
    between a verb and a class word could settle what the lowering leaves
    open, so the claim is stated of the reading, disclosed as such. ENTAILED /
    REFUTED / inconsistent survive any such refinement (instantiation is
    sound and entailment is monotone) and are stated at full strength.
    """
    given = "; ".join(premise_texts)
    if trace.outcome is Entailment.ENTAILED:
        return f"Given: {given}. Your premises entail: {query_text}."
    if trace.outcome is Entailment.REFUTED:
        return (
            f"Given: {given}. Your premises entail the opposite of "
            f"{query_text} — it cannot hold."
        )
    if trace.outcome is Entailment.UNKNOWN:
        return (
            f"Given: {given}. Reading each name as one individual and each "
            f"class word and verb phrase at face value, your premises don't "
            f"settle whether {query_text} — it holds in some cases and fails "
            f"in others."
        )
    # REFUSED
    if trace.reason == INCONSISTENT_PREMISES:
        return (
            f"Given: {given}. Those premises are inconsistent — they "
            f"can't all be true, so I won't assert anything from them."
        )
    return f"Given: {given}. I can't evaluate {query_text} from that as stated."


def _categorical_clause(prop: dict) -> str:
    """One categorical proposition dict → its English clause."""
    template = _CATEGORICAL_PHRASE.get(prop.get("form", ""), "{s} ~ {p}")
    return template.format(s=prop.get("subject", "?"), p=prop.get("predicate", "?"))


def render_syllogism(trace: EntailmentTrace, structure: dict, query: dict) -> str:
    """The user-facing surface for a categorical (syllogism) verdict.

    Deterministic templates over the argument's own clauses — no synthesis. The
    ``EntailmentTrace`` is the propositional-lowering decision (``ENTAILED`` ⇒
    valid; ``UNKNOWN``/``REFUTED`` ⇒ invalid; ``REFUSED`` ⇒ inconsistent).
    """
    premises = "; ".join(
        _categorical_clause(p) for p in structure.get("premises", [])
    )
    conclusion = _categorical_clause(query.get("conclusion", {}))
    if trace.outcome is Entailment.ENTAILED:
        return f"Given: {premises}. That's valid — {conclusion} follows."
    if trace.outcome is Entailment.REFUSED and trace.reason == INCONSISTENT_PREMISES:
        return (
            f"Given: {premises}. Those premises are inconsistent — they can't all "
            f"be true, so I won't assert anything from them."
        )
    if trace.outcome is Entailment.REFUSED:
        return f"Given: {premises}. I can't evaluate {conclusion} from that as stated."
    # UNKNOWN or REFUTED — the conclusion is not forced by the premises.
    return (
        f"Given: {premises}. That doesn't follow — {conclusion} isn't guaranteed "
        f"by those premises."
    )


__all__ = [
    "render_entailment",
    "render_entailment_english",
    "render_entailment_member",
    "render_entailment_verb",
    "render_syllogism",
]
