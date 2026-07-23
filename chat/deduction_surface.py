"""chat/deduction_surface.py — Phase 1 DEDUCTION composer (deduction-serve arc).

Wires the verified propositional-entailment engine (``generate.proof_chain``,
716/716 wrong=0 on ``evals/deductive_logic``) into serving. When a prompt
reads as a propositional argument — "P1. P2. ... Therefore C." — comprehend
the text into a ``MeaningGraph``, project into ``(premises, query)`` formula
strings, and decide with the sound+complete ROBDD entailment engine.
Deterministic templates only (``generate.proof_chain.render``) — no LLM, no
synthesis, matching every other composer in this package.

Band v1 scope (docs/research/deduction-serve-arc-phase0-baseline-2026-07-23.md):
propositional arguments with single-token atoms only. A categorical/syllogism
"Therefore" argument is recognized as argument-shaped but declined as
out-of-band — a production categorical decider is Band v1b, deferred.
``evals.syllogism.oracle`` must never be imported here: it is the sealed
independence oracle the comprehension lane scores against, not a serving
decider — importing it would collapse INV-25 (independent gold).

Fail-closed (INV-34): once ``looks_like_deductive_argument`` fires, every
path below returns a committed, honest surface — reader refusal, out-of-band
shape, and all four ``EntailmentTrace`` outcomes (ENTAILED/REFUTED/UNKNOWN/
REFUSED) — never a silent fall-through to a different composer.
"""

from __future__ import annotations

import re

from generate.meaning_graph.projectors import to_deductive_logic
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.entail import evaluate_entailment_with_trace
from generate.proof_chain.render import render_entailment

#: An argument's conclusion clause starts a sentence with "therefore" — the
#: same shape ``generate.meaning_graph.reader`` recognizes per-clause
#: (``toks[0] == "therefore"``). Matching at this commit-gate with the same
#: sentence-initial discipline avoids drift between "looks like an argument"
#: and "is an argument" — the reader remains the sole decider of the latter.
_ARGUMENT_CONCLUSION_RE = re.compile(r"(?:^|[.!?]\s+)therefore\b", re.IGNORECASE)


def looks_like_deductive_argument(text: str) -> bool:
    """True iff *text* has a sentence-initial "therefore" conclusion clause.

    A cheap, deterministic COMMIT gate — not a decision. A match only
    signals "attempt deduction serving"; the reader and projector below
    remain the sole authority on whether the argument is actually
    well-formed and in-band.
    """
    return bool(_ARGUMENT_CONCLUSION_RE.search(text))


_READER_REFUSAL_SURFACE = (
    "That reads as an argument, but I can't parse it precisely enough to "
    "decide it yet ({reason})."
)
_OUT_OF_BAND_SURFACE = (
    "That reads as an argument, but right now I can only decide plain "
    "propositional arguments (not categorical 'all/no/some' ones yet)."
)


def deduction_grounded_surface(text: str) -> str | None:
    """Return a deterministic DEDUCTION-tier surface, or ``None``.

    Returns ``None`` only when *text* is not argument-shaped at all
    (``looks_like_deductive_argument`` is False) — the caller then falls
    through to the pre-existing dispatch, byte-identical to before this
    composer existed. Once argument-shaped, every branch below commits to
    an honest surface; see the module docstring's fail-closed contract.
    """
    if not looks_like_deductive_argument(text):
        return None
    comp = comprehend(text)
    if not isinstance(comp, Comprehension):
        return _READER_REFUSAL_SURFACE.format(reason=comp.reason)
    projected = to_deductive_logic(comp)
    if projected is None:
        return _OUT_OF_BAND_SURFACE
    premises, query = projected
    trace = evaluate_entailment_with_trace(premises, query)
    return render_entailment(trace, premises, query)


__all__ = ["deduction_grounded_surface", "looks_like_deductive_argument"]
