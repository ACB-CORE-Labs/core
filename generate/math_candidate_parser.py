"""ADR-0126 — Candidate-emitting sentence parser.

Sibling to ``generate/math_parser.py``. Same regex spirit, different
topology: instead of first-match-wins with a single mutable state and
``ParseError`` on miss, each per-sentence extractor returns a *list of
candidates* (possibly empty) carrying full source-span provenance.

The wrong-answer firewall is :func:`generate.math_roundtrip.roundtrip_admissible`,
applied downstream in P3 (graph assembly). This module's job is purely
to *enumerate* the parses the grammar admits — telling truth from
falsehood is not its concern.

Determinism: candidate lists are returned in deterministic order
(canonical pattern key); the same input always produces the same
ordered output.

Scope of P2 (this module):
  - Initial-possession candidate extraction.
  - Operation candidate extraction for add / subtract / transfer
    via the canonical "<Subject> <verb> <value> <unit> [to <target>]"
    shape.
  - Permissive verb tables imported from
    :data:`generate.math_roundtrip.KIND_TO_VERBS` — much wider than
    ``math_parser._ADD_VERBS`` / ``_SUBTRACT_VERBS`` / ``_TRANSFER_VERBS``
    because the round-trip filter rejects wrong candidates downstream.

Out of scope for P2 (added in later phases):
  - Pronoun resolution (needs per-branch state — P3).
  - Unit inheritance from ``last_unit`` (needs per-branch state — P3).
  - Multiply / divide / rate / comparison candidates (later phases of
    ADR-0126; the candidate-emission machinery is identical, just more
    pattern matchers).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Final

from generate.math_problem_graph import (
    InitialPossession,
    Operation,
    Quantity,
    Unknown,
)
from generate.math_roundtrip import (
    ADD_VERBS,
    SUBTRACT_VERBS,
    TRANSFER_VERBS,
    WORD_NUMBERS,
    CandidateOperation,
)


# ---------------------------------------------------------------------------
# Initial-possession candidate
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CandidateInitial:
    """Initial-possession candidate with source-span provenance.

    Mirrors :class:`CandidateOperation` but for ``InitialPossession``.
    The round-trip filter for initials is the same shape: every claimed
    content slot (entity, value, unit, anchor verb 'has'/'have') must
    ground in the source sentence.
    """

    initial: InitialPossession
    source_span: str
    matched_anchor: str       # 'has' or 'have'
    matched_value_token: str  # '3' or 'three'
    matched_unit_token: str
    matched_entity_token: str

    def __post_init__(self) -> None:
        # ADR-0127 widens the anchor set to include 'there are/were/is/was'
        # for the implicit-subject initial-possession shape.
        if self.matched_anchor.lower() not in ("has", "have", "are", "were", "is", "was"):
            raise ValueError(
                f"CandidateInitial.matched_anchor must be has/have/are/were/is/was; "
                f"got {self.matched_anchor!r}"
            )


# ---------------------------------------------------------------------------
# Shared regex building blocks
# ---------------------------------------------------------------------------

# Title-cased proper noun OR "the <noun>" collective. Same widening as
# math_parser._INITIAL_HAS_RE's ADR-0123a entity slot.
_ENTITY: Final[str] = r"(?:[A-Z]\w+|[Tt]he\s+\w+)"

# Dynamic value-slot regex builder
def _build_value_regex() -> str:
    fallback_words = "|".join(
        re.escape(w) for w in sorted(WORD_NUMBERS.keys(), key=len, reverse=True)
    )
    fallback = rf"(?:\d+|{fallback_words})"
    try:
        from language_packs.numerics_loader import _index
        idx = _index()
        cardinal_words = sorted(idx.cardinals.keys(), key=len, reverse=True)
        ordinal_words = sorted(idx.ordinals.keys(), key=len, reverse=True)
        fraction_words = sorted(idx.fractions.keys(), key=len, reverse=True)
        multiplier_words = sorted(idx.multipliers.keys(), key=len, reverse=True)
        quantifier_words = sorted(idx.quantifiers.keys(), key=len, reverse=True)
        
        denom_plurals = ["halves", "thirds", "quarters", "fourths", "fifths", "sixths", "sevenths", "eighths", "ninths", "tenths", "sixteenths"]
        
        all_singles = set(cardinal_words + ordinal_words + fraction_words + multiplier_words + quantifier_words)
        
        cards_pat = "|".join(re.escape(w) for w in cardinal_words)
        ords_pat = "|".join(re.escape(w) for w in ordinal_words)
        fracs_pat = "|".join(re.escape(w) for w in fraction_words)
        denoms_pat = "|".join(re.escape(w) for w in (ordinal_words + fraction_words + denom_plurals))
        
        comp_card_pat = rf"(?:{cards_pat})(?:[- ](?:and[- ])?(?:{cards_pat})){{0,4}}"
        comp_frac_pat = rf"(?:{comp_card_pat})[- ](?:{denoms_pat})"
        
        patterns = [
            r"\d+\s+\d+/\d+",
            r"\d+/\d+",
            r"[\$\u20ac\u00a3\u00a5\u20b1\u00a2]?\d+(?:\.\d+)?",
            comp_frac_pat,
            comp_card_pat,
        ]
        for w in all_singles:
            patterns.append(re.escape(w))
        return "|".join(patterns)
    except Exception:
        return fallback

_VALUE: Final[str] = _build_value_regex()

_UNIT: Final[str] = (
    r"(?:(?!to\b)(?!more\b)(?!on\b)(?!from\b)(?!at\b)(?!in\b)"
    r"(?!onto\b)(?!into\b)(?!under\b)(?!over\b)(?!of\b)(?!for\b)(?!with\b)"
    r"(?!today\b)(?!now\b)(?!yesterday\b)(?!initially\b)\w+)+"
    r"(?:[- ]\w+)*"
)

# Verb alternation built from the permissive registry. Pre-compute one
# pattern per kind so we can attribute matched verbs to candidates.
def _verbs_pattern(verbs: frozenset[str]) -> str:
    # Longest-first so "passes" matches before "pass" inside the alternation.
    options = sorted(verbs, key=len, reverse=True)
    return r"(?:" + "|".join(re.escape(v) for v in options) + r")"


_ADD_VERBS_PATTERN: Final[str] = _verbs_pattern(ADD_VERBS)
_SUBTRACT_VERBS_PATTERN: Final[str] = _verbs_pattern(SUBTRACT_VERBS)
_TRANSFER_VERBS_PATTERN: Final[str] = _verbs_pattern(TRANSFER_VERBS)


# ---------------------------------------------------------------------------
# Initial-possession extractor
# ---------------------------------------------------------------------------

_INITIAL_THERE_ARE_RE: Final[re.Pattern[str]] = re.compile(
    r"^(?:.*\b)?there\s+(?P<anchor>are|were|is|was)\s+"
    rf"(?P<value>{_VALUE})\s+"
    rf"(?P<unit>{_UNIT})"
    r"(?:\s+of\s+(?P<substance>[a-zA-Z]\w*(?:\s+\w+)*))?"
    r"(?:\s+(?:in|on|at|inside|outside)\s+(?P<place>[A-Za-z]\w*(?:\s+\w+)?))?"
    r"(?:\s+[a-zA-Z]+)*"
    r"\s*\.?$",
    flags=re.IGNORECASE,
)


def _normalize_entity(raw: str) -> str:
    """Collapse whitespace + lowercase article. Mirrors math_parser
    canonicalization so candidate entity names hash-equal to legacy."""
    e = re.sub(r"\s+", " ", raw.strip())
    if e.lower().startswith("the "):
        return "the " + e[4:]
    return e


def _resolve_currency_and_value(value_token: str) -> tuple[float | int, str | None]:
    token = value_token.strip()
    currency_unit = None
    
    # Check for leading currency symbols ($, €, £, ¥, ₱, ¢)
    if token and not token[0].isalnum() and token[0] != '-':
        symbol = token[0]
        try:
            from language_packs.loader import lookup_unit
            entry = lookup_unit(symbol)
            if entry is not None:
                currency_unit = entry.plural.lower()
                token = token[1:].strip()
        except Exception:
            if symbol == '$':
                currency_unit = "dollars"
                token = token[1:].strip()
                
    if currency_unit is not None:
        if '.' in token:
            decimals = token.split('.')[-1].strip('%')
            if len(decimals) > 2:
                raise ValueError("Too many decimal places for currency")

    # Parse numeric value
    try:
        from language_packs.loader import match_number_format
        parsed = match_number_format(token)
        if parsed is not None:
            val = parsed.value
            from fractions import Fraction
            if isinstance(val, Fraction):
                val = float(val)
            return val, currency_unit
    except Exception:
        pass
        
    try:
        from language_packs.loader import lookup_fraction
        frac_entry = lookup_fraction(token)
        if frac_entry is not None:
            return float(frac_entry.decimal_value), currency_unit
    except Exception:
        pass
        
    try:
        from language_packs.loader import parse_compound_cardinal
        comp_val = parse_compound_cardinal(token)
        if comp_val is not None:
            return comp_val, currency_unit
    except Exception:
        pass
        
    if token.isdigit():
        return int(token), currency_unit
    try:
        return float(token), currency_unit
    except ValueError:
        pass
        
    lowered = token.lower()
    if lowered in WORD_NUMBERS:
        return WORD_NUMBERS[lowered], currency_unit
        
    raise ValueError(f"Could not resolve numeric value from token: {value_token!r}")


def _resolve_value(value_token: str) -> float | int:
    val, _ = _resolve_currency_and_value(value_token)
    return val


def _compose_unit(currency_unit: str | None, matched_unit: str | None) -> str | None:
    if not currency_unit:
        if not matched_unit:
            return None
        return _canonicalize_unit(matched_unit)
    if not matched_unit:
        return currency_unit
        
    mu_low = matched_unit.lower().strip()
    for conn in ("an ", "a ", "per ", "each "):
        if mu_low.startswith(conn):
            mu_low = mu_low[len(conn):].strip()
            
    if mu_low == "each" or mu_low == "":
        rate_denom = "item"
    else:
        rate_denom = _canonicalize_unit(mu_low)
        try:
            from language_packs.loader import lookup_unit
            entry = lookup_unit(rate_denom)
            if entry is not None:
                rate_denom = entry.singular
            elif rate_denom.endswith("s"):
                rate_denom = rate_denom[:-1]
        except Exception:
            if rate_denom.endswith("s"):
                rate_denom = rate_denom[:-1]
                
    composed_raw = f"{currency_unit} per {rate_denom}"
    try:
        from language_packs.loader import lookup_unit
        entry = lookup_unit(composed_raw)
        if entry is not None:
            return entry.plural.lower()
    except Exception:
        pass
    return _canonicalize_unit(composed_raw)


def _is_indefinite_quantifier(token: str) -> bool:
    """ADR-0128.4 — quantifier-driven refusal helper.

    Returns True when ``token`` resolves (via en_numerics_v1 lookup) to
    an indefinite quantifier (``some``, ``many``, ``few``, ``several``,
    etc.). Indefinite quantifiers in value-slot positions are refused
    rather than guessed — preserves wrong == 0.
    """
    try:
        from language_packs.loader import lookup_quantifier
        entry = lookup_quantifier(token.lower())
        if entry is not None and entry.semantic_type == "indefinite":
            return True
    except Exception:
        pass
    return False


def extract_initial_candidates(sentence: str) -> list[CandidateInitial]:
    """Return all admissible initial-possession candidates for ``sentence``.

    Recognized shapes:
      1. "<Entity> has <N> <unit> [of <substance>]" — canonical, supporting compound possessions.
      2. "There are <N> <unit> [in <place>]" — implicit-subject shape.
    """
    s = sentence.strip().rstrip(".")
    out: list[CandidateInitial] = []

    m_has = re.match(
        rf"^(?P<entity>{_ENTITY})\s+(?P<anchor>has|have)\s+(?P<quantities>.+)$",
        s,
        flags=re.IGNORECASE
    )
    if m_has is not None:
        entity_raw = m_has.group("entity")
        entity = _normalize_entity(entity_raw)
        anchor = m_has.group("anchor")
        quantities_str = m_has.group("quantities")
        
        parts = re.split(r",?\s+and\s+", quantities_str, flags=re.IGNORECASE)
        
        q_re = re.compile(
            rf"^(?P<value>{_VALUE})(?:\s+(?P<unit>{_UNIT}))?(?:\s+of\s+(?P<substance>.+))?$",
            flags=re.IGNORECASE
        )
        
        all_matched = True
        candidates_temp = []
        for p in parts:
            p = p.strip()
            mq = q_re.match(p)
            if mq is not None:
                value_raw = mq.group("value")
                if not _is_indefinite_quantifier(value_raw):
                    try:
                        val, curr_unit = _resolve_currency_and_value(value_raw)
                        unit_raw = mq.group("unit")
                        substance = mq.group("substance")
                        if unit_raw is not None and substance is not None:
                            unit_raw = f"{unit_raw} of {substance}"
                        elif unit_raw is None and substance is not None:
                            unit_raw = substance.strip()
                            lowered_sub = unit_raw.lower()
                            for art in ("a ", "an ", "the "):
                                if lowered_sub.startswith(art):
                                    unit_raw = unit_raw[len(art):].strip()
                                    break
                        unit = _compose_unit(curr_unit, unit_raw)
                        if unit is None:
                            all_matched = False
                            break
                        candidates_temp.append(
                            CandidateInitial(
                                initial=InitialPossession(
                                    entity=entity,
                                    quantity=Quantity(value=val, unit=unit),
                                ),
                                source_span=sentence,
                                matched_anchor=anchor,
                                matched_value_token=value_raw,
                                matched_unit_token=unit_raw if unit_raw is not None else "",
                                matched_entity_token=entity_raw,
                            )
                        )
                    except ValueError:
                        all_matched = False
                        break
                else:
                    all_matched = False
                    break
            else:
                all_matched = False
                break
                
        if all_matched and candidates_temp:
            out.extend(candidates_temp)
            return out

    m2 = _INITIAL_THERE_ARE_RE.match(s)
    if m2 is not None:
        value_raw = m2.group("value")
        if not _is_indefinite_quantifier(value_raw):
            try:
                val, curr_unit = _resolve_currency_and_value(value_raw)
                unit_raw = m2.group("unit")
                substance = m2.group("substance") if "substance" in m2.groupdict() else None
                if unit_raw is not None and substance is not None:
                    unit_raw = f"{unit_raw} of {substance}"
                elif unit_raw is None and substance is not None:
                    unit_raw = substance.strip()
                    lowered_sub = unit_raw.lower()
                    for art in ("a ", "an ", "the "):
                        if lowered_sub.startswith(art):
                            unit_raw = unit_raw[len(art):].strip()
                            break
                unit = _compose_unit(curr_unit, unit_raw)
                if unit is not None:
                    place = m2.group("place")
                    if place is not None:
                        entity = _normalize_entity(place)
                        entity_token = place
                    else:
                        entity = unit
                        entity_token = unit_raw
                    out.append(
                        CandidateInitial(
                            initial=InitialPossession(
                                entity=entity,
                                quantity=Quantity(value=val, unit=unit),
                            ),
                            source_span=sentence,
                            matched_anchor=m2.group("anchor"),
                            matched_value_token=value_raw,
                            matched_unit_token=unit_raw if unit_raw is not None else "",
                            matched_entity_token=entity_token,
                        )
                    )
            except ValueError:
                pass

    return out


# ---------------------------------------------------------------------------
# Operation candidate extractor
# ---------------------------------------------------------------------------

def _op_pattern(verbs_pattern: str, *, requires_target: bool) -> re.Pattern[str]:
    """Build the per-kind operation regex.

    For ``requires_target=True`` (transfer): the trailing ``to <Target>``
    clause is a captured slot.

    For ``requires_target=False`` (add/subtract): there is no target
    slot. A trailing ``to <noun>`` phrase, if present, is consumed as
    part of the discardable preposition tail so the regex still matches
    ambiguous sentences like "Sam gives 3 apples to Tom" (which we
    *do* want to match as a subtract candidate; the transfer-vs-subtract
    disambiguation happens at the candidate / filter / decision-rule
    layer, not by regex specificity).
    """
    if requires_target:
        target_part = r"\s+to\s+(?P<target>[A-Z]\w+)"
        trailing_prep = (
            r"(?:\s+(?:on|from|at|in|onto|into|under|over|of|for|with)\s+.+)?"
        )
    else:
        target_part = ""
        trailing_prep = (
            r"(?:\s+(?:on|from|at|in|onto|into|under|over|to|of|for|with)\s+.+)?"
        )
    return re.compile(
        r"^"
        rf"(?P<subject>{_ENTITY})\s+"
        rf"(?P<verb>{verbs_pattern})"
        rf"\s+(?P<value>{_VALUE})"
        r"(?:\s+more)?"
        r"(?:\s+(?P<unit>" + _UNIT + r"))?"
        rf"{target_part}"
        rf"{trailing_prep}"
        r"\s*\.?$",
        flags=re.IGNORECASE,
    )


_ADD_OP_RE: Final[re.Pattern[str]] = _op_pattern(_ADD_VERBS_PATTERN, requires_target=False)
_SUBTRACT_OP_RE: Final[re.Pattern[str]] = _op_pattern(_SUBTRACT_VERBS_PATTERN, requires_target=False)
_TRANSFER_OP_RE: Final[re.Pattern[str]] = _op_pattern(_TRANSFER_VERBS_PATTERN, requires_target=True)


def _canonicalize_unit(unit_raw: str) -> str:
    """Canonicalize a unit surface token to its plural form.

    ADR-0127 integration: consult en_units_v1 first. If the token is a
    pack-recognized unit, use the pack's canonical plural form (handles
    irregular plurals like feet/feet, children, mice, etc. correctly).
    Otherwise fall back to the legacy '+s' rule for count nouns.
    """
    lowered = unit_raw.lower()
    try:
        from language_packs.loader import lookup_unit
        entry = lookup_unit(lowered)
        if entry is not None:
            return entry.plural.lower()
    except Exception:
        pass
    if not lowered.endswith("s"):
        return lowered + "s"
    return lowered


def _build_op_candidate(
    m: re.Match[str], kind: str, source: str
) -> CandidateOperation | None:
    """Build a CandidateOperation from a regex match. Returns None if
    the match lacks a required slot (e.g. unit token absent — P2 does
    not emit unit-inherited candidates)."""
    unit_raw = m.group("unit")
    value_raw = m.group("value")
    
    try:
        value, curr_unit = _resolve_currency_and_value(value_raw)
    except ValueError:
        return None
        
    unit = _compose_unit(curr_unit, unit_raw)
    if unit is None:
        return None
        
    subject = _normalize_entity(m.group("subject"))
    verb = m.group("verb").lower()
    target_raw = m.group("target") if "target" in m.groupdict() else None
    target = target_raw if target_raw is not None else None

    op_kwargs: dict[str, object] = {
        "actor": subject,
        "kind": kind,
        "operand": Quantity(value=value, unit=unit),
    }
    if kind == "transfer":
        if target is None:
            return None  # transfer requires target
        op_kwargs["target"] = target
    else:
        if target is not None:
            return None  # add/subtract don't take targets

    return CandidateOperation(
        op=Operation(**op_kwargs),  # type: ignore[arg-type]
        source_span=source,
        matched_verb=verb,
        matched_value_token=value_raw,
        matched_unit_token=unit_raw if unit_raw is not None else "",
        matched_actor_token=m.group("subject"),
        matched_target_token=target,
    )


# ---------------------------------------------------------------------------
# Question candidate
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class CandidateUnknown:
    """Question-candidate with source-span provenance.

    Two question shapes in P3 scope:

    - ``How many <unit> does <Entity> have [left|now|in total|altogether]?``
      → ``Unknown(entity=<Entity>, unit=<unit>)``
    - ``How many <unit> do they have [left|now|in total|altogether]?``
      → ``Unknown(entity=None, unit=<unit>)`` (total-across)

    The round-trip filter for questions checks the unit token and (when
    present) the entity token both appear in the source span.
    """

    unknown: Unknown
    source_span: str
    matched_unit_token: str
    matched_entity_token: str | None  # None for total-across questions


_Q_ENTITY_RE: Final[re.Pattern[str]] = re.compile(
    r"^How\s+many\s+(?P<unit>" + _UNIT + r")\s+(?:does|do)\s+"
    rf"(?P<entity>{_ENTITY})"
    r"\s+have(?:\s+(?:left|now|in\s+total|altogether)){0,2}\s*\??$",
    flags=re.IGNORECASE,
)

_Q_TOTAL_RE: Final[re.Pattern[str]] = re.compile(
    r"^How\s+many\s+(?P<unit>" + _UNIT + r")\s+do\s+they\s+have"
    r"(?:\s+(?:in\s+total|altogether|left|now)){0,2}\s*\??$",
    flags=re.IGNORECASE,
)


def extract_question_candidates(sentence: str) -> list[CandidateUnknown]:
    """Return all admissible question candidates for ``sentence``.

    Tries the total-across pattern FIRST (same specificity order as
    legacy math_parser). The entity-pattern's widened regex would
    otherwise capture "they" as an entity name.

    Empty list if no shape matches.
    """
    s = sentence.strip()
    out: list[CandidateUnknown] = []

    m = _Q_TOTAL_RE.match(s)
    if m is not None:
        unit_raw = m.group("unit")
        unit = _canonicalize_unit(unit_raw)
        out.append(
            CandidateUnknown(
                unknown=Unknown(entity=None, unit=unit),
                source_span=sentence,
                matched_unit_token=unit_raw,
                matched_entity_token=None,
            )
        )
        return out  # specificity order: don't also try entity pattern

    m = _Q_ENTITY_RE.match(s)
    if m is not None:
        unit_raw = m.group("unit")
        unit = _canonicalize_unit(unit_raw)
        entity = _normalize_entity(m.group("entity"))
        out.append(
            CandidateUnknown(
                unknown=Unknown(entity=entity, unit=unit),
                source_span=sentence,
                matched_unit_token=unit_raw,
                matched_entity_token=m.group("entity"),
            )
        )

    return out


def extract_operation_candidates(sentence: str) -> list[CandidateOperation]:
    """Return all operation candidates for ``sentence``.

    Tries every verb-kind pattern independently. A sentence with an
    ambiguous verb (e.g. "Sam gives 3 apples to Tom" — "gives" appears
    in both SUBTRACT_VERBS and TRANSFER_VERBS) may emit multiple
    candidates. The round-trip filter
    (:func:`generate.math_roundtrip.roundtrip_admissible`) and the
    decision rule (P3) resolve which one becomes the chosen graph.

    Candidate emission order is canonical: add, subtract, transfer.
    Within each kind, the regex emits at most one candidate per
    sentence.
    """
    s = sentence.strip()
    out: list[CandidateOperation] = []

    for pattern, kind in (
        (_ADD_OP_RE, "add"),
        (_SUBTRACT_OP_RE, "subtract"),
        (_TRANSFER_OP_RE, "transfer"),
    ):
        m = pattern.match(s)
        if m is None:
            continue
        candidate = _build_op_candidate(m, kind, source=sentence)
        if candidate is not None:
            out.append(candidate)

    return out
