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

#: Band v3-MEM (ADR-0258) — singular-membership arguments with universal
#: premises ("Socrates is a man. All men are mortal. …"), read by
#: ``generate.proof_chain.member`` via per-individual propositional lowering.
#: Same ``en_`` license discipline: a different reader must earn its own
#: per-shape record. Priority order: negative > chain > single > atomic.
EN_MEMBER_NEGATIVE = "en_member_negative"
EN_MEMBER_CHAIN = "en_member_chain"
EN_MEMBER_SINGLE = "en_member_single"
EN_MEMBER_ATOMIC = "en_member_atomic"

EN_MEMBER_BANDS: tuple[str, ...] = (
    EN_MEMBER_NEGATIVE,
    EN_MEMBER_CHAIN,
    EN_MEMBER_SINGLE,
    EN_MEMBER_ATOMIC,
)

#: Band v4-CM (ADR-0259) — conditional-membership fusion arguments, composing
#: v2-EN's connective grammar with v3-MEM's singular-membership sentence
#: reading ("If Socrates is a man then Socrates is mortal. …"), read by
#: ``generate.proof_chain.cond_member``. Same ``en_`` license discipline: a
#: different reader must earn its own per-shape record. Priority order:
#: fused > disjunctive > chain > conditional.
EN_CONDMEM_FUSED = "en_condmem_fused"
EN_CONDMEM_DISJUNCTIVE = "en_condmem_disjunctive"
EN_CONDMEM_CHAIN = "en_condmem_chain"
EN_CONDMEM_CONDITIONAL = "en_condmem_conditional"

EN_CONDMEM_BANDS: tuple[str, ...] = (
    EN_CONDMEM_FUSED,
    EN_CONDMEM_DISJUNCTIVE,
    EN_CONDMEM_CHAIN,
    EN_CONDMEM_CONDITIONAL,
)

#: Band v5-VP (ADR-0260) — verb-predicate arguments ("All philosophers teach.
#: Socrates is a philosopher. Therefore Socrates teaches."), read by
#: ``generate.proof_chain.verb`` via per-individual lowering with a second
#: (individual, verb-group, object) atom family alongside v3-MEM's membership
#: atoms. Same ``en_`` license discipline: a different reader must earn its
#: own per-shape record. Priority order: negative > chain > universal > fact.
EN_VERB_NEGATIVE = "en_verb_negative"
EN_VERB_CHAIN = "en_verb_chain"
EN_VERB_UNIVERSAL = "en_verb_universal"
EN_VERB_FACT = "en_verb_fact"

EN_VERB_BANDS: tuple[str, ...] = (
    EN_VERB_NEGATIVE,
    EN_VERB_CHAIN,
    EN_VERB_UNIVERSAL,
    EN_VERB_FACT,
)

#: Band v6-EX (ADR-0261) — existential arguments ("All wolves are mammals.
#: Some wolves are tame. Therefore some mammals are tame."), read by
#: ``generate.proof_chain.exist``: v5-VP's per-individual lowering over a
#: domain widened with one Skolem witness per existential premise and one
#: arbitrary element per existential conclusion. Same ``en_`` license
#: discipline: a different reader must earn its own per-shape record.
#: Priority order: negative > chain > universal > witness.
EN_EXIST_NEGATIVE = "en_exist_negative"
EN_EXIST_CHAIN = "en_exist_chain"
EN_EXIST_UNIVERSAL = "en_exist_universal"
EN_EXIST_WITNESS = "en_exist_witness"

EN_EXIST_BANDS: tuple[str, ...] = (
    EN_EXIST_NEGATIVE,
    EN_EXIST_CHAIN,
    EN_EXIST_UNIVERSAL,
    EN_EXIST_WITNESS,
)

#: Every serving shape-band — the ratified ledger's full key set.
ALL_SHAPE_BANDS: tuple[str, ...] = (
    SHAPE_BANDS
    + EN_SHAPE_BANDS
    + EN_MEMBER_BANDS
    + EN_CONDMEM_BANDS
    + EN_VERB_BANDS
    + EN_EXIST_BANDS
)


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
    "EN_CONDMEM_BANDS",
    "EN_CONDMEM_CHAIN",
    "EN_CONDMEM_CONDITIONAL",
    "EN_CONDMEM_DISJUNCTIVE",
    "EN_CONDMEM_FUSED",
    "EN_DISJUNCTIVE",
    "EN_EXIST_BANDS",
    "EN_EXIST_CHAIN",
    "EN_EXIST_NEGATIVE",
    "EN_EXIST_UNIVERSAL",
    "EN_EXIST_WITNESS",
    "EN_MEMBER_ATOMIC",
    "EN_MEMBER_BANDS",
    "EN_MEMBER_CHAIN",
    "EN_MEMBER_NEGATIVE",
    "EN_MEMBER_SINGLE",
    "EN_SHAPE_BANDS",
    "EN_VERB_BANDS",
    "EN_VERB_CHAIN",
    "EN_VERB_FACT",
    "EN_VERB_NEGATIVE",
    "EN_VERB_UNIVERSAL",
    "SHAPE_BANDS",
    "classify_deduction_shape",
]
