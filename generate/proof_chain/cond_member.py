"""Conditional-membership argument reader — Band v4-CM (ADR-0259).

Composes Band v2-EN's connective grammar (``if/then``, ``or``, ``and``,
``either`` sugar) with Band v3-MEM's singular-membership sentence reading, so
"If Socrates is a man then Socrates is mortal. Socrates is a man. Therefore
Socrates is mortal." decides — the ``mixed_structure_out_of_band`` gap
ADR-0258 §6.1 reserved as a future band.

Why this needs no new negation layer (unlike v2-EN): v2-EN's leaf minter
(``_AtomTable.mint``) is negation-BLIND, so its grammar must strip "not"
before minting. This band's leaf is ``generate.proof_chain.member``'s own
``_parse_singular`` — already negation-aware (leading "not", the sentential
"it is not the case that" prefix, and copular "is not") — so a leaf is parsed
directly, no separate negation-extraction step.

Why composing is sound (ADR-0259 §3, the load-bearing argument): every
connective built here (``&``, ``|``, ``->``) is standard propositional
structure the ROBDD engine already decides; every leaf is a v3-MEM singular
fact minted and linked by the SAME closed morphology relation ADR-0258 §3
proved sound and (for this fragment) complete. A bare universal may now
instantiate at an individual named only inside a connective's leaf — still
sound, since ADR-0258 §3's argument does not depend on WHERE a named
individual appears — and a connective's leaf atom may unify with an atom a
universal's instantiation also produced (the fusion this band is named for).
UNKNOWN is rendered by the UNCHANGED ``render_entailment_member`` (ADR-0258):
its scoping ("reading each name as one individual and each class word at
face value…") is exactly as accurate here, since every clause is read all
the way to individual+class — connectives add no new hidden structure.

Dispatch order is load-bearing: a sentence is checked for a connective token
BEFORE the universal-lead check (not after), so a connective token can never
silently leak into an opaque universal/singular name or class run.

Tried strictly AFTER Bands v1 / v1b / v2-EN / v3-MEM (a fallback tier) — pure
widening; every previously-served argument is served byte-identically.
Refusal-first, closed reason vocabulary:

  ``empty``, ``question_sentence``, ``no_conclusion``,
  ``multiple_conclusions``, ``conclusion_not_last``, ``no_premises``,
  ``empty_side``, ``quantifier_out_of_band``, ``bare_plural_out_of_band``,
  ``definite_description_out_of_band``, ``relative_clause_out_of_band``,
  ``universal_conclusion_out_of_band``, ``compound_conclusion_out_of_band``,
  ``internal_negation_unread``, ``sentence_shape_out_of_band``,
  ``structural_leak``, ``nested_conditional``, ``ambiguous_and_or``,
  ``too_many_premises``, ``too_many_atoms``.
"""

from __future__ import annotations

from dataclasses import dataclass

# The v2-EN sentence splitter, tokenizer, and generic token-run splitter are
# reused VERBATIM (one normalization discipline across every argument band —
# deliberate private-name imports inside the proof_chain package, same
# precedent as generate.proof_chain.member).
from generate.proof_chain.english import _SENTENCE_RE, _split_on, _tokenize
from generate.proof_chain.member import (
    _A_LEADS,
    _E_LEAD,
    _QUANTIFIER_TOKENS,
    _Singular,
    _Universal,
    _forms_link,
    _parse_singular,
    _parse_universal,
)
from generate.proof_chain.member import _Reject as _MemberReject
from generate.proof_chain.shape import (
    EN_CONDMEM_CHAIN,
    EN_CONDMEM_CONDITIONAL,
    EN_CONDMEM_DISJUNCTIVE,
    EN_CONDMEM_FUSED,
)

#: Connective structure this band's grammar composes (v2-EN's inventory,
#: minus "therefore" — that token is the commit-gate handled by the
#: outer sentence loop, never part of a clause's own structure).
_CONNECTIVE_TOKENS = frozenset({"if", "then", "or", "and", "either"})

#: Honesty caps — beyond these the argument is refused, never truncated.
#: ``MAX_ATOMS`` counts minted (individual, class) pairs.
MAX_PREMISE_SENTENCES = 16
MAX_ATOMS = 24


@dataclass(frozen=True, slots=True)
class CondMemberArgument:
    """A successfully-read conditional-membership argument, engine-ready.

    Same shape as ``MemberArgument``/``EnglishArgument``: ``premise_formulas``/
    ``query_formula`` are propositional formula strings over minted atom ids;
    ``atoms[i]`` displays the *(individual, class)* pair behind ``a{i}``.
    ``premise_texts``/``query_text`` are the normalized original sentences.
    """

    premise_formulas: tuple[str, ...]
    query_formula: str
    premise_texts: tuple[str, ...]
    query_text: str
    band: str
    atoms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class CondMemberRefusal:
    """A typed refusal — the argument is not honestly readable by this band."""

    reason: str
    detail: str = ""


class _Reject(Exception):
    def __init__(self, reason: str, detail: str = "") -> None:
        super().__init__(reason)
        self.refusal = CondMemberRefusal(reason, detail)


# --- the formula tree: leaves are v3-MEM singular facts, not opaque atoms ----


@dataclass(frozen=True, slots=True)
class _Lit:
    leaf: int


@dataclass(frozen=True, slots=True)
class _And:
    left: "_Formula"
    right: "_Formula"


@dataclass(frozen=True, slots=True)
class _Or:
    left: "_Formula"
    right: "_Formula"


@dataclass(frozen=True, slots=True)
class _Implies:
    left: "_Formula"
    right: "_Formula"


_Formula = _Lit | _And | _Or | _Implies


@dataclass(frozen=True, slots=True)
class _Connective:
    """A parsed connective sentence: its formula tree over LOCAL leaf indices,
    plus the singular facts those indices reference (leaf-parse order)."""

    formula: _Formula
    leaves: tuple[_Singular, ...]


def _is_connective(toks: list[str]) -> bool:
    return any(t in _CONNECTIVE_TOKENS for t in toks)


def _leaf(toks: list[str], leaves: list[_Singular], detail: str) -> _Lit:
    """One membership leaf — reuses v3-MEM's own singular parser verbatim,
    which is already negation-aware and already guards every name/class run
    (quantifiers, relative clauses, definite descriptions, tense, bare
    plurals) via ``_check_run``."""
    leaves.append(_parse_singular(toks, detail))
    return _Lit(len(leaves) - 1)


def _parse_junction(toks: list[str], leaves: list[_Singular], detail: str) -> _Formula:
    """Or/and over membership leaves. "either" is consumed before a
    disjunction; mixed top-level and+or refuses (English scope is genuinely
    ambiguous); a conditional may not nest inside a junction."""
    if "if" in toks or "then" in toks:
        raise _Reject("nested_conditional", detail)
    if toks and toks[0] == "either" and "or" in toks:
        toks = toks[1:]
    has_or = "or" in toks
    has_and = "and" in toks
    if has_or and has_and:
        raise _Reject("ambiguous_and_or", detail)
    if has_or or has_and:
        sep = "or" if has_or else "and"
        parts = _split_on(toks, sep)
        if any(not p for p in parts):
            raise _Reject("empty_side", detail)
        combine = _Or if has_or else _And
        node = _leaf(parts[0], leaves, detail)
        for part in parts[1:]:
            node = combine(node, _leaf(part, leaves, detail))
        return node
    return _leaf(toks, leaves, detail)


def _parse_node(toks: list[str], leaves: list[_Singular], detail: str) -> _Formula:
    """One full connective sentence: ``if <A> then <B>`` (junctions allowed on
    both sides, no nested conditionals) or a bare junction."""
    if toks and toks[0] == "if":
        if "then" not in toks:
            raise _Reject("nested_conditional", detail)
        then_idx = toks.index("then")
        antecedent = toks[1:then_idx]
        consequent = toks[then_idx + 1 :]
        if not antecedent or not consequent:
            raise _Reject("empty_side", detail)
        left = _parse_junction(antecedent, leaves, detail)
        right = _parse_junction(consequent, leaves, detail)
        return _Implies(left, right)
    return _parse_junction(toks, leaves, detail)


def _parse_premise_records(
    toks: list[str], detail: str
) -> list[_Singular | _Universal | _Connective]:
    """A premise sentence -> one or more records. A top-level conjunction
    ("<A> and <B>.", no "if"/"or" anywhere) splits into separate singular
    records — identical to conjoining (v2-EN's exact discipline, ported).
    Any OTHER connective-bearing sentence builds a ``_Connective``. A
    connective-token check happens BEFORE the universal-lead check so a
    stray connective token can never leak into a bare universal's name/class
    run undetected."""
    if toks[0] != "if" and "and" in toks and "or" not in toks and "if" not in toks:
        parts = _split_on(toks, "and")
        if any(not p for p in parts):
            raise _Reject("empty_side", detail)
        return [_parse_singular(p, detail) for p in parts]
    if _is_connective(toks):
        leaves: list[_Singular] = []
        formula = _parse_node(toks, leaves, detail)
        return [_Connective(formula, tuple(leaves))]
    if toks[0] in _A_LEADS or toks[0] == _E_LEAD:
        return [_parse_universal(toks, detail)]
    if toks[0] in _QUANTIFIER_TOKENS:
        raise _Reject("quantifier_out_of_band", detail)
    return [_parse_singular(toks, detail)]


def _parse_conclusion(toks: list[str], detail: str) -> _Singular:
    """The conclusion stays a single singular fact (optionally negated) —
    matching v3-MEM's own discipline; a universal or connective-shaped
    conclusion refuses rather than attempting a compound render."""
    if _is_connective(toks):
        raise _Reject("compound_conclusion_out_of_band", detail)
    if toks[0] in _A_LEADS or toks[0] == _E_LEAD:
        raise _Reject("universal_conclusion_out_of_band", detail)
    if toks[0] in _QUANTIFIER_TOKENS:
        raise _Reject("quantifier_out_of_band", detail)
    return _parse_singular(toks, detail)


def _contains_or(node: _Formula) -> bool:
    if isinstance(node, _Lit):
        return False
    if isinstance(node, _Or):
        return True
    return _contains_or(node.left) or _contains_or(node.right)


def _count_implies(node: _Formula) -> int:
    if isinstance(node, _Lit):
        return 0
    n = 1 if isinstance(node, _Implies) else 0
    return n + _count_implies(node.left) + _count_implies(node.right)


def read_cond_member_argument(text: str) -> CondMemberArgument | CondMemberRefusal:
    """Read *text* as a conditional-membership argument, or refuse (typed).

    Deterministic and pure: same text -> same ``CondMemberArgument``. The
    conclusion is the final sentence, the sole "therefore"-led one, and must
    be a single singular fact; every earlier sentence is a premise. Lowering
    is two-pass exactly as v3-MEM's — sentences (and connective leaves) parse
    first, THEN individuals/class-groups are collected from every singular
    fact wherever it appears (bare, and-split, or nested inside a connective
    tree), THEN atoms are minted and universals instantiate at every named
    individual — with premise formulas emitted in sentence order.
    """
    if not text or not text.strip():
        return CondMemberRefusal("empty")
    sentences = [
        (m.group(1), m.group(2)) for m in _SENTENCE_RE.finditer(text) if m.group(1).strip()
    ]
    if not sentences:
        return CondMemberRefusal("empty")

    premise_records: list[_Singular | _Universal | _Connective] = []
    record_details: list[str] = []
    premise_texts: list[str] = []
    conclusion: _Singular | None = None
    query_text: str | None = None

    try:
        for idx, (body, terminator) in enumerate(sentences):
            if terminator == "?":
                raise _Reject("question_sentence", body)
            toks = _tokenize(body)
            if not toks:
                continue
            if toks[0] == "therefore":
                if conclusion is not None:
                    raise _Reject("multiple_conclusions", body)
                if idx != len(sentences) - 1:
                    raise _Reject("conclusion_not_last", body)
                rest = toks[1:]
                if not rest:
                    raise _Reject("empty_side", body)
                conclusion = _parse_conclusion(rest, body)
                query_text = " ".join(rest)
                continue
            if len(premise_texts) >= MAX_PREMISE_SENTENCES:
                raise _Reject("too_many_premises", body)
            records = _parse_premise_records(toks, body)
            premise_records.extend(records)
            record_details.extend([body] * len(records))
            premise_texts.append(" ".join(toks))

        if conclusion is None or query_text is None:
            return CondMemberRefusal("no_conclusion")
        if not premise_records:
            return CondMemberRefusal("no_premises")

        # --- lowering (ADR-0259 §2): shared with v3-MEM's two-pass scheme --
        all_records: list[_Singular | _Universal | _Connective] = [
            *premise_records, conclusion,
        ]

        # Named individuals, first-appearance order — scanning bare
        # singulars AND every leaf nested inside a connective.
        individuals: list[tuple[str, ...]] = []

        def _visit_individual(ind: tuple[str, ...]) -> None:
            if ind not in individuals:
                individuals.append(ind)

        for rec in all_records:
            if isinstance(rec, _Singular):
                _visit_individual(rec.ind)
            elif isinstance(rec, _Connective):
                for leaf in rec.leaves:
                    _visit_individual(leaf.ind)

        # Class groups: each attested form joins the FIRST group whose
        # representative it links to — greedy, deterministic, closed (the
        # SAME morphology relation as v3-MEM).
        group_of: dict[tuple[str, ...], int] = {}
        reps: list[tuple[str, ...]] = []

        def _register_form(form: tuple[str, ...]) -> None:
            if form in group_of:
                return
            for gi, rep in enumerate(reps):
                if _forms_link(form, rep):
                    group_of[form] = gi
                    return
            group_of[form] = len(reps)
            reps.append(form)

        for rec in all_records:
            if isinstance(rec, _Singular):
                _register_form(rec.cls)
            elif isinstance(rec, _Universal):
                _register_form(rec.subject)
                _register_form(rec.predicate)
            elif isinstance(rec, _Connective):
                for leaf in rec.leaves:
                    _register_form(leaf.cls)

        mint: dict[tuple[int, int], str] = {}
        atom_display: list[str] = []

        def atom_for(ind_idx: int, group: int, detail: str) -> str:
            key = (ind_idx, group)
            if key not in mint:
                if len(atom_display) >= MAX_ATOMS:
                    raise _Reject("too_many_atoms", detail)
                mint[key] = f"a{len(atom_display)}"
                atom_display.append(
                    f"{' '.join(individuals[ind_idx])} : {' '.join(reps[group])}"
                )
            return mint[key]

        def atom_of_singular(fact: _Singular, detail: str) -> str:
            atom = atom_for(individuals.index(fact.ind), group_of[fact.cls], detail)
            return f"~({atom})" if fact.negated else atom

        def render_formula(node: _Formula, leaves: tuple[_Singular, ...], detail: str) -> str:
            if isinstance(node, _Lit):
                return atom_of_singular(leaves[node.leaf], detail)
            left = render_formula(node.left, leaves, detail)
            right = render_formula(node.right, leaves, detail)
            if isinstance(node, _And):
                return f"({left}) & ({right})"
            if isinstance(node, _Or):
                return f"({left}) | ({right})"
            return f"({left}) -> ({right})"  # _Implies

        premise_formulas: list[str] = []
        for rec, detail in zip(premise_records, record_details):
            if isinstance(rec, _Singular):
                premise_formulas.append(atom_of_singular(rec, detail))
            elif isinstance(rec, _Connective):
                premise_formulas.append(render_formula(rec.formula, rec.leaves, detail))
            else:  # _Universal — instantiate at every named individual
                for ind_idx in range(len(individuals)):
                    antecedent = atom_for(ind_idx, group_of[rec.subject], detail)
                    consequent = atom_for(ind_idx, group_of[rec.predicate], detail)
                    premise_formulas.append(
                        f"({antecedent}) -> (~({consequent}))"
                        if rec.negative
                        else f"({antecedent}) -> ({consequent})"
                    )

        query_formula = atom_of_singular(conclusion, query_text)
    except (_Reject, _MemberReject) as rej:
        # ``_parse_singular``/``_parse_universal`` are v3-MEM's own functions,
        # reused verbatim — their failures raise v3-MEM's OWN ``_Reject``
        # class (same shape, different identity), so both are caught here and
        # normalized to THIS band's refusal type.
        return CondMemberRefusal(rej.refusal.reason, rej.refusal.detail)

    connectives = [r for r in premise_records if isinstance(r, _Connective)]
    has_universal = any(isinstance(r, _Universal) for r in premise_records)
    if has_universal and connectives:
        band = EN_CONDMEM_FUSED
    elif any(_contains_or(c.formula) for c in connectives):
        band = EN_CONDMEM_DISJUNCTIVE
    elif sum(_count_implies(c.formula) for c in connectives) >= 2:
        band = EN_CONDMEM_CHAIN
    else:
        band = EN_CONDMEM_CONDITIONAL

    return CondMemberArgument(
        premise_formulas=tuple(premise_formulas),
        query_formula=query_formula,
        premise_texts=tuple(premise_texts),
        query_text=query_text,
        band=band,
        atoms=tuple(atom_display),
    )


__all__ = [
    "MAX_ATOMS",
    "MAX_PREMISE_SENTENCES",
    "CondMemberArgument",
    "CondMemberRefusal",
    "read_cond_member_argument",
]
