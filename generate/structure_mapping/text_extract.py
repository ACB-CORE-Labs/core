"""Structure-mapping-owned pure-family text → MathProblemGraph extractors.

Off-serving only. Used when the live ``parse_and_solve`` reader refuses a
problem that is still a pure S1/S2/S3/S4 surface form. Does **not** modify
the serving reader or organ dispatch.

Deterministic regex extractors — no LLM, no gold labels. Refuse is the
default; only narrow pure-family patterns emit a graph.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from generate.math_problem_graph import (
    Comparison,
    InitialPossession,
    MathProblemGraph,
    Operation,
    Quantity,
    Unknown,
)

# Word → factor for multiplicative language.
_WORD_FACTORS: dict[str, float] = {
    "twice": 2.0,
    "double": 2.0,
    "two": 2.0,
    "three": 3.0,
    "triple": 3.0,
    "thrice": 3.0,
    "four": 4.0,
    "five": 5.0,
    "six": 6.0,
    "seven": 7.0,
    "eight": 8.0,
    "nine": 9.0,
    "ten": 10.0,
}


@dataclass(frozen=True, slots=True)
class TextExtractResult:
    graph: MathProblemGraph | None
    reason: str | None
    pattern_id: str | None = None


def _factor_from_token(tok: str) -> float | None:
    t = tok.strip().lower()
    if t in _WORD_FACTORS:
        return _WORD_FACTORS[t]
    try:
        v = float(t)
    except ValueError:
        return None
    return v if v > 0 else None


def extract_pure_s1(text: str) -> TextExtractResult:
    """Extract pure S1 graphs from narrow surface templates.

    Patterns (all require a total/altogether/combined/two-days query):

    P1 — reference seeded:
      ``<B> has|scored|taught <k> times (as many|the number of) ... as <A>.
       If <A> has <n> ... total|altogether``
      or ``<A> has <n>. <B> has <k> times as many ... total``

    P2 — scaled entity seeded (inverted):
      ``<B> has|wrote <k> times as many ... as <A>. If <B> ... <n> ... altogether``
      or ``<B> has <k> times as many as <A>. If <B> has <n>, how many ... combined``

    P3 — day/entity pair with ordinal:
      ``first day was twice ... second day. If <n> ... second day, how many ... two days``
    """
    if not isinstance(text, str) or not text.strip():
        return TextExtractResult(None, "empty_text")

    t = " ".join(text.split())

    # --- P3: people-counting / day1 = k × day2, day2 seeded (case 0148 family)
    m = re.search(
        r"(?:the\s+)?(?:number of\s+\w+\s+counted on\s+)?the\s+first\s+day\s+was\s+"
        r"(?P<kword>twice|double|triple|thrice|\d+|two|three|four|five|six|seven|eight|nine|ten)"
        r"(?:\s+times)?\s+(?:the\s+)?(?:total\s+)?(?:number\s+)?(?:counted\s+)?on\s+the\s+second\s+day"
        r".{0,80}?"
        r"(?P<n>\d+(?:\.\d+)?)\s+\w+\s+(?:were\s+)?counted\s+on\s+the\s+second\s+day"
        r".{0,40}?"
        r"(?:how many|total).{0,40}?(?:two days|both days|in total)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k = _factor_from_token(m.group("kword"))
        n = float(m.group("n"))
        if k is not None:
            a, b, unit = "second day", "first day", "people"
            graph = MathProblemGraph(
                entities=(a, b),
                initial_state=(
                    InitialPossession(
                        entity=a, quantity=Quantity(value=n, unit=unit)
                    ),
                ),
                operations=(
                    Operation(
                        actor=b,
                        kind="compare_multiplicative",
                        operand=Comparison(
                            reference_actor=a,
                            delta=None,
                            factor=k,
                            direction="times",
                        ),
                    ),
                ),
                unknown=Unknown(entity=None, unit=unit),
            )
            return TextExtractResult(graph, None, pattern_id="s1_p3_day_pair")

    # --- P2: inverted seed — B = k×A, B has n, total A+B
    # "Zig wrote four times as many books as Flo. If Zig wrote 60 books, how many ... altogether"
    m = re.search(
        r"(?P<b>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+"
        r"(?:wrote|has|have|scored|taught|caught|produced|bought)\s+"
        r"(?P<kword>twice|double|triple|thrice|\d+|two|three|four|five|six|seven|eight|nine|ten)"
        r"(?:\s+times)?\s+(?:as many|as much|more|the number of)\s+"
        r"(?P<unit>\w+)?\s*(?:as|than)\s+"
        r"(?P<a>[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
        r".{0,60}?"
        r"(?:if\s+)?(?P=b)\s+(?:wrote|has|have|scored|taught|caught|produced|bought)\s+"
        r"(?P<n>\d+(?:\.\d+)?)"
        r".{0,80}?"
        r"(?:altogether|in total|combined|total)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k = _factor_from_token(m.group("kword"))
        n = float(m.group("n"))
        a = m.group("a").strip()
        b = m.group("b").strip()
        unit = (m.group("unit") or "units").lower()
        if k is not None and a.lower() != b.lower():
            a_value = n / k
            graph = MathProblemGraph(
                entities=(a, b),
                initial_state=(
                    InitialPossession(
                        entity=a, quantity=Quantity(value=a_value, unit=unit)
                    ),
                ),
                operations=(
                    Operation(
                        actor=b,
                        kind="compare_multiplicative",
                        operand=Comparison(
                            reference_actor=a,
                            delta=None,
                            factor=k,
                            direction="times",
                        ),
                    ),
                ),
                unknown=Unknown(entity=None, unit=unit),
            )
            return TextExtractResult(graph, None, pattern_id="s1_p2_b_seeded")

    # Warehouse / population form:
    # "The first warehouse has twice as many boxes as the second warehouse.
    #  If the first warehouse has 400 boxes, how many boxes ... combined"
    m = re.search(
        r"(?:the\s+)?(?P<b>first\s+\w+|deaf\s+\w+\s+population|[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)\s+"
        r"has\s+"
        r"(?P<kword>twice|double|triple|thrice|\d+|two|three|four|five|six|seven|eight|nine|ten)"
        r"(?:\s+times)?\s+(?:as many|as much)\s+(?P<unit>\w+)\s+as\s+"
        r"(?:the\s+)?(?P<a>second\s+\w+|blind\s+\w+\s+population|[A-Z][A-Za-z]+(?:\s+[A-Z][A-Za-z]+)*)"
        r".{0,80}?"
        r"(?:if\s+)?(?:the\s+)?(?P=b)\s+has\s+(?P<n>\d+(?:\.\d+)?)"
        r".{0,80}?"
        r"(?:combined|altogether|in total|total|how many)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k = _factor_from_token(m.group("kword"))
        n = float(m.group("n"))
        a = re.sub(r"\s+", " ", m.group("a")).strip()
        b = re.sub(r"\s+", " ", m.group("b")).strip()
        unit = m.group("unit").lower()
        if k is not None and a.lower() != b.lower():
            a_value = n / k
            graph = MathProblemGraph(
                entities=(a, b),
                initial_state=(
                    InitialPossession(
                        entity=a, quantity=Quantity(value=a_value, unit=unit)
                    ),
                ),
                operations=(
                    Operation(
                        actor=b,
                        kind="compare_multiplicative",
                        operand=Comparison(
                            reference_actor=a,
                            delta=None,
                            factor=k,
                            direction="times",
                        ),
                    ),
                ),
                unknown=Unknown(entity=None, unit=unit),
            )
            return TextExtractResult(graph, None, pattern_id="s1_p2_b_seeded_has")

    # Special: "deaf student population three times the size of blind student
    # population. If the number of deaf students is 180, how many students
    # are there altogether"
    m = re.search(
        r"(?P<b>deaf\s+student\s+population)\s+"
        r"(?P<kword>twice|double|triple|thrice|\d+|two|three|four|five|six|seven|eight|nine|ten)"
        r"(?:\s+times)?\s+(?:the size of|as many as)\s+"
        r"(?P<a>blind\s+student\s+population)"
        r".{0,80}?"
        r"(?:number of\s+deaf\s+students\s+is|deaf\s+students\s+is)\s+(?P<n>\d+(?:\.\d+)?)"
        r".{0,60}?"
        r"(?:altogether|in total|total|how many students)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k = _factor_from_token(m.group("kword"))
        n = float(m.group("n"))
        if k is not None:
            a, b, unit = "blind students", "deaf students", "students"
            a_value = n / k
            graph = MathProblemGraph(
                entities=(a, b),
                initial_state=(
                    InitialPossession(
                        entity=a, quantity=Quantity(value=a_value, unit=unit)
                    ),
                ),
                operations=(
                    Operation(
                        actor=b,
                        kind="compare_multiplicative",
                        operand=Comparison(
                            reference_actor=a,
                            delta=None,
                            factor=k,
                            direction="times",
                        ),
                    ),
                ),
                unknown=Unknown(entity=None, unit=unit),
            )
            return TextExtractResult(graph, None, pattern_id="s1_p2_deaf_blind")

    return TextExtractResult(None, "no_pure_s1_pattern")


def extract_role_graph_from_text(text: str) -> TextExtractResult:
    """Best-effort SM-owned extract. Currently pure-S1 patterns only."""
    return extract_pure_s1(text)
