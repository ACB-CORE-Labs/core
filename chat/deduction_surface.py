"""chat/deduction_surface.py — DEDUCTION composer (deduction-serve arc).

Wires the verified propositional-entailment engine (``generate.proof_chain``,
716/716 wrong=0 on ``evals/deductive_logic``) into serving. When a prompt
reads as a propositional argument — "P1. P2. ... Therefore C." — comprehend
the text into a ``MeaningGraph``, project into ``(premises, query)`` formula
strings, and decide with the sound+complete ROBDD entailment engine.
Deterministic templates only (``generate.proof_chain.render``) — no LLM, no
synthesis, matching every other composer in this package.

Bands (docs/research/deduction-serve-arc-phase0-baseline-2026-07-23.md):
- Band v1  — propositional arguments with single-token atoms.
- Band v1b (Phase 4) — categorical/syllogism arguments ("All M are P. All S are
  M. Therefore all S are P."), projected by ``to_syllogism`` and decided by
  ``generate.proof_chain.categorical`` (a propositional-lowering decider that
  rides the same verified ROBDD engine). ``evals.syllogism.oracle`` must never
  be imported here: it is the sealed independence oracle the comprehension lane
  scores against, not a serving decider — importing it would collapse INV-25
  (independent gold).

Fail-closed (INV-34): once ``looks_like_deductive_argument`` fires, every path
below returns a committed, honest surface — reader refusal, out-of-band shape,
and every decision outcome — never a silent fall-through to a different composer.
"""

from __future__ import annotations

import re

from typing import Callable

from chat.deduction_serve_license import deduction_serve_license
from core.reliability_gate import LicenseDecision
from generate.meaning_graph.projectors import to_deductive_logic, to_syllogism
from generate.meaning_graph.reader import Comprehension, comprehend
from generate.proof_chain.categorical import CategoricalError, decide_syllogism
from generate.proof_chain.entail import evaluate_entailment_with_trace
from generate.proof_chain.render import render_entailment, render_syllogism
from generate.proof_chain.shape import CATEGORICAL, classify_deduction_shape

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
    "That reads as an argument, but its form is outside what I can decide yet "
    "(I handle plain propositional and categorical 'all/no/some' arguments)."
)

#: Disclosed hedge prepended when a decided argument's shape-band has NOT earned
#: the SERVE license (ADR-0256). The ROBDD engine is sound — the answer is not
#: guessed — but an unearned band means the FULL pipeline (crucially the reader)
#: has no demonstrated track record on this shape, so committing it as verified
#: would overstate the pipeline's earned trust. The answer is served, disclosed.
_UNVERIFIED_SHAPE_DISCLOSURE = (
    "(reasoned, but I haven't yet earned a verified track record on arguments "
    "of this shape) "
)

_LicenseLookup = Callable[[str], LicenseDecision | None]


def deduction_grounded_surface(
    text: str, *, license_lookup: _LicenseLookup = deduction_serve_license,
) -> str | None:
    """Return a deterministic DEDUCTION-tier surface, or ``None``.

    Returns ``None`` only when *text* is not argument-shaped at all
    (``looks_like_deductive_argument`` is False) — the caller then falls
    through to the pre-existing dispatch, byte-identical to before this
    composer existed. Once argument-shaped, every branch below commits to
    an honest surface; see the module docstring's fail-closed contract.

    Earned-license gate (ADR-0256): a decided argument's rendered surface is
    served AUTHORITATIVELY only when its propositional shape-band holds a
    genuine ``Action.SERVE`` license on the committed, SHA-sealed reliability
    ledger (``chat/deduction_serve_license``). A band that has not earned it —
    including the forward-looking case of a future shape absent from the ledger,
    or any deployment whose ledger is stripped — still gets the sound answer,
    but DISCLOSED (hedged), never presented as a verified capability. This is
    what makes deduction serving an *earned* capability, not merely a flagged
    one. ``license_lookup`` is injectable for testing; it defaults to the real
    ratified-ledger reader.
    """
    if not looks_like_deductive_argument(text):
        return None
    comp = comprehend(text)
    if not isinstance(comp, Comprehension):
        return _READER_REFUSAL_SURFACE.format(reason=comp.reason)
    # Band v1 — propositional argument.
    projected = to_deductive_logic(comp)
    if projected is not None:
        premises, query = projected
        trace = evaluate_entailment_with_trace(premises, query)
        surface = render_entailment(trace, premises, query)
        return _license_gate(surface, classify_deduction_shape(premises, query), license_lookup)
    # Band v1b — categorical / syllogism argument. Decided by the propositional-
    # lowering categorical decider (rides the same verified ROBDD engine); a
    # malformed categorical shape declines rather than guessing.
    syllogism = to_syllogism(comp)
    if syllogism is not None:
        structure, s_query = syllogism
        try:
            trace = decide_syllogism(structure, s_query)
        except CategoricalError:
            return _OUT_OF_BAND_SURFACE
        surface = render_syllogism(trace, structure, s_query)
        return _license_gate(surface, CATEGORICAL, license_lookup)
    return _OUT_OF_BAND_SURFACE


def _license_gate(surface: str, band: str, license_lookup: _LicenseLookup) -> str:
    """Serve *surface* authoritatively iff *band* holds a SERVE license; else
    serve the same sound answer DISCLOSED (hedged). The one place the earned-
    license posture is applied, shared by the propositional and categorical
    bands (ADR-0256)."""
    decision = license_lookup(band)
    if decision is not None and decision.licensed:
        return surface  # earned SERVE — authoritative
    return _UNVERIFIED_SHAPE_DISCLOSURE + surface  # sound, but disclosed


__all__ = ["deduction_grounded_surface", "looks_like_deductive_argument"]
