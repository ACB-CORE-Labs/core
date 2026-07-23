"""Deterministic shape-band classification for propositional arguments
(deduction-serve arc, Phase 3).

The **capability axis** the reliability ledger (ADR-0175) keys on for
deduction serving. A shape-band is a purely structural signature of the
projected ``(premises, query)`` formula strings — cheap, deterministic, and
computed identically by the practice arena (which earns the per-class SERVE
license) and the serving composer (which consults it). No decision logic:
this says *what kind of argument* a case is, never whether it is entailed.

The bands are deliberately coarse — each holds a MIX of entailed/refuted/
unknown cases — so a class's measured reliability answers "does the whole
serving pipeline (reader → projector → engine) decide arguments of this
shape correctly?", which is the fallible part (the reader can misparse; the
ROBDD engine cannot). A band that only ever saw entailed cases would measure
nothing the engine's soundness doesn't already guarantee.
"""

from __future__ import annotations

_IMPLIES = " implies "
_OR = " or "

#: The closed set of shape-bands. Serving classifies into exactly one of these;
#: the practice arena earns a per-band SERVE license over the same set.
DISJUNCTIVE = "disjunctive"
CONDITIONAL_CHAIN = "conditional_chain"
CONDITIONAL_SINGLE = "conditional_single"
ATOMIC = "atomic"
#: Band v1b (Phase 4) — categorical/syllogism arguments. Distinct from the four
#: propositional bands: a categorical argument is projected by ``to_syllogism``
#: (not ``to_deductive_logic``) and decided by ``generate.proof_chain.categorical``
#: (the propositional-lowering decider), so the serving composer assigns this band
#: directly rather than by ``classify_deduction_shape`` (which reads propositional
#: formula strings).
CATEGORICAL = "categorical"

SHAPE_BANDS: tuple[str, ...] = (
    DISJUNCTIVE,
    CONDITIONAL_CHAIN,
    CONDITIONAL_SINGLE,
    ATOMIC,
    CATEGORICAL,
)

#: Band v2-EN (ADR-0257) — English-clause propositional arguments, read by
#: ``generate.proof_chain.english`` (opaque clause-atoms). Namespaced ``en_``
#: because a band's earned license certifies READER fidelity per shape
#: (ADR-0256): the English reader is a different reader, so it must earn its
#: own per-shape record even though the engine underneath is identical.
EN_DISJUNCTIVE = "en_disjunctive"
EN_CONDITIONAL_CHAIN = "en_conditional_chain"
EN_CONDITIONAL_SINGLE = "en_conditional_single"
EN_ATOMIC = "en_atomic"

EN_SHAPE_BANDS: tuple[str, ...] = (
    EN_DISJUNCTIVE,
    EN_CONDITIONAL_CHAIN,
    EN_CONDITIONAL_SINGLE,
    EN_ATOMIC,
)

#: Every serving shape-band — the ratified ledger's full key set.
ALL_SHAPE_BANDS: tuple[str, ...] = SHAPE_BANDS + EN_SHAPE_BANDS


def classify_deduction_shape(premises: tuple[str, ...], query: str) -> str:
    """The structural shape-band of a projected propositional argument.

    Priority order (first match wins), by the connectives present in the
    PREMISES only (the query's shape is a downstream concern of the engine,
    not of the capability axis):

    - ``disjunctive``        — any premise is a disjunction (``A or B``).
    - ``conditional_chain``  — two or more conditional premises (``A implies B``).
    - ``conditional_single`` — exactly one conditional premise.
    - ``atomic``             — no conditional, no disjunction (bare atoms /
                               negations only).
    """
    has_or = any(_OR in p for p in premises)
    if has_or:
        return DISJUNCTIVE
    n_implies = sum(1 for p in premises if _IMPLIES in p)
    if n_implies >= 2:
        return CONDITIONAL_CHAIN
    if n_implies == 1:
        return CONDITIONAL_SINGLE
    return ATOMIC


__all__ = [
    "ALL_SHAPE_BANDS",
    "ATOMIC",
    "CATEGORICAL",
    "CONDITIONAL_CHAIN",
    "CONDITIONAL_SINGLE",
    "DISJUNCTIVE",
    "EN_ATOMIC",
    "EN_CONDITIONAL_CHAIN",
    "EN_CONDITIONAL_SINGLE",
    "EN_DISJUNCTIVE",
    "EN_SHAPE_BANDS",
    "SHAPE_BANDS",
    "classify_deduction_shape",
]
