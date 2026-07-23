"""Categorical-syllogism decider by propositional lowering (deduction-serve
arc, Phase 4 / Band v1b, ADR-0256).

The Phase-0 fork found that the ONLY categorical decider in the tree was
``evals/syllogism/oracle.py`` — the sealed independence oracle the comprehension
lane scores against, which serving must never import (INV-25). This is the
production decider: it lowers a categorical argument into the propositional
regime and decides it with the already-verified ROBDD engine
(``generate.proof_chain.entail``, 716/716 wrong=0). No new decision procedure —
soundness rides on the flagship engine; only the lowering is new.

The lowering is EXACT for the modern/Boolean reading of the categorical forms
(universals without existential import — the same reading the eval oracle uses).
A model of a k-term categorical argument is fully determined by which of the
``2^k`` term-membership *profiles* are occupied by at least one element. Introduce
one Boolean atom ``occ_j`` per profile ("profile j has ≥1 element") and every
A/E/I/O proposition becomes a propositional formula over those atoms:

    A  all S are P    ⋀_{j: S∈j, P∉j} ¬occ_j       (no S-but-not-P element exists)
    E  no S are P     ⋀_{j: S∈j, P∈j} ¬occ_j
    I  some S are P    ⋁_{j: S∈j, P∈j} occ_j
    O  some S are not P ⋁_{j: S∈j, P∉j} occ_j

Validity ("conclusion holds in every model of the premises") is then exactly
propositional entailment, which the ROBDD engine decides. Because the profile
atoms range over ALL occupancy patterns, this is sound AND complete (no reliance
on a lucky domain size). Independent of the eval oracle by mechanism: ROBDD over
a profile encoding vs. brute-force subset enumeration — no shared code.
"""

from __future__ import annotations

from itertools import combinations

from generate.proof_chain.entail import (
    Entailment,
    EntailmentTrace,
    evaluate_entailment_with_trace,
)

_FORMS = frozenset({"A", "E", "I", "O"})


class CategoricalError(ValueError):
    """Malformed / out-of-grammar categorical input; refuse, never guess."""


def _profiles(n_terms: int) -> tuple[tuple[int, ...], ...]:
    """All ``2^n`` membership profiles over ``n`` term-indices, as index tuples.

    A profile is the set of term-indices an element belongs to; ``occ_<bits>``
    names whether at least one element has that profile.
    """
    idxs = range(n_terms)
    out: list[tuple[int, ...]] = []
    for r in range(n_terms + 1):
        out.extend(combinations(idxs, r))
    return tuple(out)


def _atom(profile: tuple[int, ...]) -> str:
    """Deterministic occupancy-atom name for a profile (its member indices)."""
    return "occ_" + ("e" if not profile else "_".join(str(i) for i in profile))


def _lower_proposition(
    form: str, s_idx: int, p_idx: int, profiles: tuple[tuple[int, ...], ...]
) -> str:
    """One A/E/I/O proposition → a propositional formula over occupancy atoms."""
    if form == "A":  # ⋀ ¬occ_j over profiles with S and not P
        terms = [f"not {_atom(j)}" for j in profiles if s_idx in j and p_idx not in j]
        return " and ".join(terms) if terms else "true"
    if form == "E":  # ⋀ ¬occ_j over profiles with S and P
        terms = [f"not {_atom(j)}" for j in profiles if s_idx in j and p_idx in j]
        return " and ".join(terms) if terms else "true"
    if form == "I":  # ⋁ occ_j over profiles with S and P
        terms = [_atom(j) for j in profiles if s_idx in j and p_idx in j]
        return " or ".join(terms) if terms else "false"
    if form == "O":  # ⋁ occ_j over profiles with S and not P
        terms = [_atom(j) for j in profiles if s_idx in j and p_idx not in j]
        return " or ".join(terms) if terms else "false"
    raise CategoricalError(f"unsupported categorical form: {form!r}")  # pragma: no cover


def _term_index(terms: list[str], name: str) -> int:
    try:
        return terms.index(name)
    except ValueError as exc:
        raise CategoricalError(f"proposition names unknown term: {name!r}") from exc


def _check_proposition(raw: object) -> tuple[str, str, str]:
    if not isinstance(raw, dict):
        raise CategoricalError(f"proposition must be an object: {raw!r}")
    form = raw.get("form")
    subject = raw.get("subject")
    predicate = raw.get("predicate")
    if form not in _FORMS:
        raise CategoricalError(f"unsupported categorical form: {form!r}")
    if not isinstance(subject, str) or not isinstance(predicate, str):
        raise CategoricalError(f"proposition subject/predicate must be strings: {raw!r}")
    if subject == predicate:
        raise CategoricalError("subject and predicate must be distinct")
    return form, subject, predicate


def lower_syllogism(
    structure: dict, query: dict
) -> tuple[tuple[str, ...], str]:
    """Lower a categorical ``(structure, query)`` into ``(premises, query)``
    propositional formula strings over occupancy atoms. Raises
    :class:`CategoricalError` on malformed input."""
    raw_terms = structure.get("terms")
    if not isinstance(raw_terms, list) or len(raw_terms) < 2:
        raise CategoricalError("terms must be a list of at least two term names")
    terms = [t for t in raw_terms]
    if any(not isinstance(t, str) or not t for t in terms):
        raise CategoricalError("every term must be a non-empty string")
    if len(set(terms)) != len(terms):
        raise CategoricalError("terms contains duplicates")

    raw_premises = structure.get("premises")
    if not isinstance(raw_premises, list) or not raw_premises:
        raise CategoricalError("premises must be a non-empty list")
    if query.get("kind") != "validity":
        raise CategoricalError(f"unsupported query kind: {query.get('kind')!r}")

    profiles = _profiles(len(terms))
    premise_formulas: list[str] = []
    for raw in raw_premises:
        form, subject, predicate = _check_proposition(raw)
        premise_formulas.append(
            _lower_proposition(
                form, _term_index(terms, subject), _term_index(terms, predicate), profiles
            )
        )
    c_form, c_subject, c_predicate = _check_proposition(query.get("conclusion"))
    conclusion_formula = _lower_proposition(
        c_form, _term_index(terms, c_subject), _term_index(terms, c_predicate), profiles
    )
    return tuple(premise_formulas), conclusion_formula


def decide_syllogism(structure: dict, query: dict) -> EntailmentTrace:
    """Decide a categorical validity query via the verified ROBDD engine.

    Returns the underlying :class:`EntailmentTrace`. Map to a categorical
    reading: ``ENTAILED`` ⇒ the syllogism is VALID (the conclusion holds in
    every model of the premises); ``UNKNOWN``/``REFUTED`` ⇒ INVALID (the
    conclusion is not forced); ``REFUSED`` ⇒ the premises are inconsistent
    (no model) or the input was malformed.
    """
    premises, conclusion = lower_syllogism(structure, query)
    return evaluate_entailment_with_trace(premises, conclusion)


def syllogism_is_valid(structure: dict, query: dict) -> bool:
    """True iff the categorical argument is VALID (conclusion entailed)."""
    return decide_syllogism(structure, query).outcome is Entailment.ENTAILED


__all__ = [
    "CategoricalError",
    "decide_syllogism",
    "lower_syllogism",
    "syllogism_is_valid",
]
