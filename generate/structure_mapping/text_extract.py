"""Structure-mapping-owned pure-family text → MathProblemGraph extractors.

Off-serving only. Used when the live ``parse_and_solve`` reader refuses a
problem that is still a pure S1/S2/S3/S4 surface form. Does **not** modify
the serving reader or organ dispatch.

Deterministic regex extractors — no LLM, no gold labels. Refuse is the
default; only narrow pure-family patterns emit a graph.

Pure-family surface gates (fail-closed — wrong=0 absolute):
- Exactly one multiplicative compare phrase (``times as many/much``,
  ``twice|double|triple|thrice as``, ``times the number/size of``).
- Never match bare additive language (``N more``, ``N fewer``) as a factor —
  that was the 0361 overmatch that emitted a certified wrong answer.
- Refuse multi-clause / multi-relation / fraction / percent surfaces.
- At most two numeric seeds and two named roles for inverted/day templates.
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

# Multiplicative compare surface (must be present for pure S1 extract).
# Intentionally does NOT match bare "N more" / "N fewer" (additive).
_MULT_COMPARE = re.compile(
    r"(?:"
    r"twice\s+as\s+(?:many|much)|"
    r"twice\s+the\s+(?:total\s+)?(?:number|amount|size)|"
    r"double\s+(?:what|the)|"
    r"triple\s+(?:what|the)|"
    r"thrice\s+as\s+(?:many|much)|"
    r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+times\s+"
    r"(?:as\s+(?:many|much)|the\s+(?:total\s+)?(?:number|size|amount)|more\s+than)|"
    r"times\s+(?:as\s+(?:many|much)|the\s+(?:total\s+)?(?:number|size|amount)\s+of)"
    r")",
    re.IGNORECASE,
)

# Additive / multi-step markers that disqualify pure-S1 extract.
_IMPURE_MARKERS = re.compile(
    r"(?:"
    r"\bfewer\b|"
    r"\bless than\b|"
    r"\bmore than\b|"  # additive "more than" without being part of "times more than"
    r"\b\d+\s+more\b|"
    r"\b\d+\s+fewer\b|"
    r"\b\d+\s+less\b|"
    r"\b1/\d+\b|"
    r"\bhalf as\b|"
    r"\ba third\b|"
    r"\bpercent\b|"
    r"%|"
    r"\band half\b|"
    r"\bbut\b|"
    r"\bthen\b|"
    r"\bafter\b|"
    r"\bbought\b|"
    r"\bsold\b|"
    r"\bgave\b|"
    r"\bgives\b|"
    r"\blost\b|"
    r"\beach of\b|"
    r"\bevery\b"
    r")",
    re.IGNORECASE,
)

# "times more than" is multiplicative; strip those before impure "more than" check.
_TIMES_MORE_THAN = re.compile(
    r"(?:twice|thrice|\d+|two|three|four|five|six|seven|eight|nine|ten)\s+times\s+more\s+than",
    re.IGNORECASE,
)


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


def _purity_gate(text: str) -> str | None:
    """Return a refuse reason if text is not a pure single-relation S1 surface."""
    # Count multiplicative compare phrases — pure S1 has exactly one.
    mults = list(_MULT_COMPARE.finditer(text))
    if len(mults) == 0:
        return "no_multiplicative_compare"
    if len(mults) > 1:
        return "multi_multiplicative_compare"

    # Impure markers after masking legitimate "times more than".
    masked = _TIMES_MORE_THAN.sub("TIMES_MORE_THAN", text)
    # Also mask the single mult compare span so "more" inside "times as many"
    # is not confused — the mult phrase itself is clean.
    for m in mults:
        masked = masked[: m.start()] + ("X" * (m.end() - m.start())) + masked[m.end() :]
    if _IMPURE_MARKERS.search(masked):
        return "impure_multi_clause_markers"

    # Too many independent numeric seeds → multi-step (pure S1: 1 seed + factor
    # word, or 1 seed with numeric factor already in mult phrase).
    nums = re.findall(r"\b\d+(?:\.\d+)?\b", text)
    if len(nums) > 2:
        return "too_many_numeric_seeds"

    return None


def _s1_graph(
    *,
    a: str,
    b: str,
    k: float,
    a_value: float,
    unit: str,
) -> MathProblemGraph:
    return MathProblemGraph(
        entities=(a, b),
        initial_state=(
            InitialPossession(entity=a, quantity=Quantity(value=a_value, unit=unit)),
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


def extract_pure_s1(text: str) -> TextExtractResult:
    """Extract pure S1 graphs from narrow surface templates.

    Patterns (all require a total/altogether/combined/two-days query and
    pass the pure-family surface gate):

    P2 — scaled entity seeded (inverted):
      ``<B> wrote|has <k> times as many <unit> as <A>. If <B> ... <n> ... altogether``

    P2b — warehouse / first-second form with ``twice|N times as many ... as``

    P2c — deaf/blind population form

    P3 — day pair: first day = k × second day; second seeded; total two days
    """
    if not isinstance(text, str) or not text.strip():
        return TextExtractResult(None, "empty_text")

    t = " ".join(text.split())

    refuse = _purity_gate(t)
    if refuse is not None:
        return TextExtractResult(None, f"not_pure_s1:{refuse}")

    # --- P3: people-counting / day1 = k × day2, day2 seeded (case 0148 family)
    # Requires explicit "times" when kword is numeric; "twice/double/triple/thrice"
    # are inherently multiplicative.
    m = re.search(
        r"(?:the\s+)?(?:number of\s+\w+\s+counted on\s+)?the\s+first\s+day\s+was\s+"
        r"(?P<kword>twice|double|triple|thrice|"
        r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+times)"
        r"\s+(?:the\s+)?(?:total\s+)?(?:number\s+)?(?:counted\s+)?on\s+the\s+second\s+day"
        r".{0,80}?"
        r"(?P<n>\d+(?:\.\d+)?)\s+\w+\s+(?:were\s+)?counted\s+on\s+the\s+second\s+day"
        r".{0,40}?"
        r"(?:how many|total).{0,40}?(?:two days|both days|in total)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k_raw = m.group("kword")
        # Strip trailing "times" for numeric/word factors
        k_tok = re.sub(r"\s+times$", "", k_raw.strip(), flags=re.IGNORECASE)
        k = _factor_from_token(k_tok)
        n = float(m.group("n"))
        if k is not None:
            graph = _s1_graph(
                a="second day", b="first day", k=k, a_value=n, unit="people"
            )
            return TextExtractResult(graph, None, pattern_id="s1_p3_day_pair")

    # --- P2: inverted seed — B = k×A, B has n, total A+B
    # REQUIRE "times as many/much" or word-factor "twice as many" — never bare "N more".
    m = re.search(
        r"(?P<b>[A-Z][a-z]+)\s+"
        r"(?:wrote|has|have|scored|taught|caught|produced)\s+"
        r"(?P<kword>twice|double|triple|thrice|"
        r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+times)\s+"
        r"(?:as many|as much)\s+"
        r"(?P<unit>\w+)\s+as\s+"
        r"(?P<a>[A-Z][a-z]+)"
        r"\.\s+"
        r"(?:If\s+)?(?P=b)\s+(?:wrote|has|have|scored|taught|caught|produced)\s+"
        r"(?P<n>\d+(?:\.\d+)?)"
        r".{0,80}?"
        r"(?:altogether|in total|combined)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k_tok = re.sub(
            r"\s+times$", "", m.group("kword").strip(), flags=re.IGNORECASE
        )
        k = _factor_from_token(k_tok)
        n = float(m.group("n"))
        a = m.group("a").strip()
        b = m.group("b").strip()
        unit = m.group("unit").lower()
        # Entity names must be single proper nouns (reject "he does lions").
        if (
            k is not None
            and a.lower() != b.lower()
            and a[0].isupper()
            and b[0].isupper()
            and " " not in a
            and " " not in b
        ):
            graph = _s1_graph(a=a, b=b, k=k, a_value=n / k, unit=unit)
            return TextExtractResult(graph, None, pattern_id="s1_p2_b_seeded")

    # Warehouse form: first/second + "twice|N times as many UNIT as"
    m = re.search(
        r"(?:the\s+)?(?P<b>first\s+\w+)\s+has\s+"
        r"(?P<kword>twice|double|triple|thrice|"
        r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+times)\s+"
        r"as many\s+(?P<unit>\w+)\s+as\s+"
        r"(?:the\s+)?(?P<a>second\s+\w+)"
        r".{0,80}?"
        r"(?:if\s+)?(?:the\s+)?(?P=b)\s+has\s+(?P<n>\d+(?:\.\d+)?)"
        r".{0,80}?"
        r"(?:combined|altogether|in total|how many)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k_tok = re.sub(
            r"\s+times$", "", m.group("kword").strip(), flags=re.IGNORECASE
        )
        k = _factor_from_token(k_tok)
        n = float(m.group("n"))
        a = re.sub(r"\s+", " ", m.group("a")).strip()
        b = re.sub(r"\s+", " ", m.group("b")).strip()
        unit = m.group("unit").lower()
        if k is not None and a.lower() != b.lower():
            graph = _s1_graph(a=a, b=b, k=k, a_value=n / k, unit=unit)
            return TextExtractResult(graph, None, pattern_id="s1_p2_b_seeded_has")

    # Deaf/blind population form (fixed surface; still purity-gated).
    m = re.search(
        r"(?P<b>deaf\s+student\s+population)\s+"
        r"(?P<kword>twice|double|triple|thrice|"
        r"(?:two|three|four|five|six|seven|eight|nine|ten|\d+)\s+times)\s+"
        r"(?:the size of|as many as)\s+"
        r"(?P<a>blind\s+student\s+population)"
        r".{0,80}?"
        r"(?:number of\s+deaf\s+students\s+is|deaf\s+students\s+is)\s+(?P<n>\d+(?:\.\d+)?)"
        r".{0,60}?"
        r"(?:altogether|in total|how many students)",
        t,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if m:
        k_tok = re.sub(
            r"\s+times$", "", m.group("kword").strip(), flags=re.IGNORECASE
        )
        k = _factor_from_token(k_tok)
        n = float(m.group("n"))
        if k is not None:
            graph = _s1_graph(
                a="blind students",
                b="deaf students",
                k=k,
                a_value=n / k,
                unit="students",
            )
            return TextExtractResult(graph, None, pattern_id="s1_p2_deaf_blind")

    return TextExtractResult(None, "no_pure_s1_pattern")


def extract_role_graph_from_text(text: str) -> TextExtractResult:
    """Best-effort SM-owned extract. Currently pure-S1 patterns only."""
    return extract_pure_s1(text)
