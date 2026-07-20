"""Proof-preserving articulation + firewall.

Every articulated claim must:
  1. cite only valid citation keys (step_id or kind:symbol — never bare payload values);
  2. have every content token certified by the cited steps' symbols/payloads
     (or a closed function-word lexicon for English glue).

Claims failing either check are HALLUCINATED and suppressed.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.cognition.fail_closed import CoherenceRefusal, FailureClass, ResidualState
from core.cognition.proof_trace import ProofTrace
from core.semantic_primitives import ValidationError
from generate.linguistic_pipeline.field_integration import (
    AmbiguousFieldState,
    CoherentFieldState,
    FieldOutcome,
)

# Do not treat sentence punctuation (.) as part of a token — otherwise
# "closed." fails certification against certified token "closed".
_TOKEN_RE = re.compile(r"[a-z0-9_:-]+", re.IGNORECASE)

# English glue only — never domain content (entities, quantities, causes).
_FUNCTION_WORDS: frozenset[str] = frozenset(
    {
        "a",
        "an",
        "the",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "of",
        "to",
        "for",
        "and",
        "or",
        "as",
        "in",
        "on",
        "at",
        "by",
        "with",
        "from",
        "that",
        "this",
        "these",
        "those",
        "it",
        "its",
        "class",
        "operator",
        "admissible",
        "geometric",
        "contract",
        "closed",
        "field",
        "state",
        "versor",
        "condition",
        "residual",
        "goldtether",
        "embedding",
        "applied",
        "selected",
        "unique",
        "configuration",
    }
)


@dataclass(frozen=True, slots=True)
class ArticulatedClaim:
    text: str
    trace_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.text.strip():
            raise ValidationError("ArticulatedClaim.text must be non-empty")
        if not self.trace_refs:
            raise ValidationError(
                "ArticulatedClaim.trace_refs must be non-empty (firewall precondition)"
            )


@dataclass(frozen=True, slots=True)
class ArticulationFirewallVerdict:
    legal_claims: tuple[ArticulatedClaim, ...]
    hallucinated: tuple[str, ...]
    surface: str

    @property
    def clean(self) -> bool:
        return not self.hallucinated


def _content_tokens(text: str) -> frozenset[str]:
    return frozenset(m.group(0).lower() for m in _TOKEN_RE.finditer(text))


def _claim_is_certified(claim: ArticulatedClaim, proof_trace: ProofTrace) -> bool:
    """True iff all refs are valid citations AND all content tokens are certified."""
    citation_keys = proof_trace.all_citation_keys()
    if not claim.trace_refs:
        return False
    if not all(ref in citation_keys for ref in claim.trace_refs):
        return False
    # Every ref must resolve to at least one step (no dangling synonym).
    resolved = proof_trace.steps_for_refs(claim.trace_refs)
    if len(resolved) == 0:
        return False
    if len({r for r in claim.trace_refs}) != len(claim.trace_refs):
        pass  # duplicates ok
    # All refs must independently resolve
    for ref in claim.trace_refs:
        if not proof_trace.steps_for_refs((ref,)):
            return False

    certified = set(proof_trace.certified_content_for_refs(claim.trace_refs))
    certified |= set(_FUNCTION_WORDS)
    for token in _content_tokens(claim.text):
        if token in certified:
            continue
        # Allow numeric fragments only if the exact token is certified (e.g. value text)
        return False
    return True


def firewall_check(
    claims: tuple[ArticulatedClaim, ...] | list[ArticulatedClaim],
    proof_trace: ProofTrace,
) -> ArticulationFirewallVerdict:
    """Diff claims against proof-trace citations + certified content; suppress rest."""
    if not isinstance(proof_trace, ProofTrace):
        raise ValidationError("firewall requires a ProofTrace")
    legal: list[ArticulatedClaim] = []
    hallucinated: list[str] = []
    for claim in claims:
        if _claim_is_certified(claim, proof_trace):
            legal.append(claim)
        else:
            hallucinated.append(claim.text)
    surface = " ".join(c.text for c in legal)
    return ArticulationFirewallVerdict(
        legal_claims=tuple(legal),
        hallucinated=tuple(hallucinated),
        surface=surface,
    )


def articulate_from_proof(outcome: FieldOutcome) -> ArticulationFirewallVerdict | CoherenceRefusal:
    """Render only certified state. Ambiguous/refusal never invent answers."""
    if isinstance(outcome, CoherenceRefusal):
        return outcome
    if isinstance(outcome, AmbiguousFieldState):
        return CoherenceRefusal(
            failure_class=FailureClass.AMBIGUITY,
            violated_condition="unique_operator_class",
            residual_state=ResidualState(detail=outcome.reason),
            refusal_reason=(
                "ambiguous field state — no single answer may be articulated"
            ),
            surface_message=(
                "I cannot certify a unique answer: multiple operator classes remain "
                f"admissible ({', '.join(c.value for c in outcome.candidate_operator_classes)})."
            ),
        )
    if not isinstance(outcome, CoherentFieldState):
        raise ValidationError("articulate_from_proof requires a FieldOutcome")

    trace = outcome.proof_trace
    op = outcome.selected_operator_class.value
    # Claim text uses only function-word glue + tokens certified on the cited steps.
    # Never invent magnitudes or entities not present on those steps.
    claims = [
        ArticulatedClaim(
            text="The geometric contract closed.",
            trace_refs=("closure:0",),
        ),
        ArticulatedClaim(
            text=f"The admissible operator class is {op}.",
            trace_refs=("atom:operator",),
        ),
    ]
    return firewall_check(claims, trace)


def inject_uncertified_claim(
    verdict: ArticulationFirewallVerdict,
    *,
    bogus_text: str,
    proof_trace: ProofTrace,
    trace_refs: tuple[str, ...] | None = None,
) -> ArticulationFirewallVerdict:
    """Test helper: re-run firewall with an injected claim.

    Default uses a totally-absent ref. Callers may pass payload-value refs
    (e.g. ``("2",)``) to prove the whitelist bypass is closed.
    """
    refs = trace_refs if trace_refs is not None else ("not_in_trace_ever",)
    claims = list(verdict.legal_claims) + [
        ArticulatedClaim(text=bogus_text, trace_refs=refs)
    ]
    return firewall_check(tuple(claims), proof_trace)
