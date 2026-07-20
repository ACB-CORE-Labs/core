"""Field-grounded intent ratification (ADR-0022 §TBD-1).

The rule-based regex classifier in ``generate/intent.py`` is the
*seed*; this module is the *ratifier*.  Forward semantic control on
top of a non-geometric classifier would recreate the same gap one
level up — the classifier becomes the oracle the field defers to.
ADR-0022 closes that gap by requiring the field to ratify the seed:
the prompt versor must lie within the seeded intent's admissible
region, or the intent demotes to ``IntentTag.UNKNOWN``.

Design decisions:

* **Smallest deterministic step.**  No new classifier model, no
  learned ratifier — the existing regex classifier remains the
  candidate generator; the field is the gate.
* **No sampling.**  Ratification is a CGA-inner-product threshold
  check, exact and replayable.  Same `(intent, prompt_versor)` →
  same verdict byte-for-byte.
* **No new closure invariant.**  The ratifier inspects the prompt
  versor; it does not normalize, repair, or mutate the field
  (CLAUDE.md §Normalization Rules).
* **No new trust surface.**  Pure function over typed in-memory
  state; no IO, no dynamic import.

The ratifier is wired into ``CognitiveTurnPipeline`` after the
seed classification and before the proposition graph is built; a
demotion routes through the existing UNKNOWN-domain surface path,
preserving honest refusal per ADR-0022 §2.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, unique

import numpy as np

from algebra.cga import cga_inner
from generate.admissibility import AdmissibilityRegion, region_from_relation_chain
from generate.intent import DialogueIntent, IntentTag


@unique
class RatificationOutcome(Enum):
    RATIFIED = "ratified"
    DEMOTED = "demoted"


@dataclass(frozen=True, slots=True)
class RatifiedIntent:
    """Result of field ratification of a seeded intent.

    ``intent`` is the (possibly demoted) intent the downstream
    pipeline should use.  ``outcome`` records what happened so the
    trace and failure surface can name *why* an intent was rejected.
    ``score`` carries the CGA inner product the verdict was based
    on; ``threshold`` records the gate it was checked against.
    """

    intent: DialogueIntent
    outcome: RatificationOutcome
    score: float
    threshold: float
    seed_tag: IntentTag


def _intent_subspace_anchors(vocab, intent: DialogueIntent) -> list[np.ndarray]:
    """Vocab-grounded intent-subspace anchors for conformal argmax scoring.

    Anchors are candidate points on the manifold (subject, tag predicates,
    relation). The prompt field is scored against these anchors only —
    never against a string-derived subject self-inner product.
    """
    candidates: list[str] = []
    if intent.subject:
        candidates.append(intent.subject.lower())
    if intent.relation:
        candidates.append(intent.relation.strip().lower())
    match intent.tag:
        case IntentTag.DEFINITION:
            candidates.extend(("is", "definition"))
        case IntentTag.CAUSE:
            candidates.extend(("causes", "because"))
        case IntentTag.COMPARISON:
            candidates.extend(("like", "unlike", "compared"))
        case _:
            pass
    anchors: list[np.ndarray] = []
    seen: set[str] = set()
    for token in candidates:
        if not token or token in seen:
            continue
        seen.add(token)
        try:
            anchors.append(np.asarray(vocab.get_versor(token), dtype=np.float32))
        except (KeyError, AttributeError):
            continue
    return anchors


def _intent_anchor_versor(vocab, intent: DialogueIntent) -> np.ndarray | None:
    """Return the first vocab-grounded intent-subspace anchor, or ``None``."""
    anchors = _intent_subspace_anchors(vocab, intent)
    return anchors[0] if anchors else None


#: Default ratification threshold (Finding 3, audit 2026-05-20).
#:
#: Pre-fix the default was ``0.0``, which admitted anything with non-
#: negative projection onto the anchor versor — the field gate was
#: structurally live but semantically transparent (ADR-0022 §TBD-1).
#: Measured against ``core eval cognition`` across all 45 cases (45 =
#: 13 public + 13 dev + 19 holdout), every ratifiable case scored
#: ``cga_inner(prompt, anchor) ≥ 1.10`` after a prime turn primed the
#: field — see ``scripts/calibrate_ratification_threshold.py``.  The
#: 0.5 floor is well below that 1.10 minimum (no regression on any
#: passing case) while clearly non-trivially positive (random Cl(4,1)
#: inner products fluctuate around zero, so 0.5 demands genuine
#: correlation with the anchor).  Off-corpus / adversarial prompts
#: with weakly-aligned anchors will now demote to ``UNKNOWN`` and
#: route through the honest-refusal surface.
_DEFAULT_RATIFICATION_THRESHOLD: float = 0.5


def ratify_intent(
    intent: DialogueIntent,
    prompt_versor: np.ndarray,
    *,
    vocab,
    threshold: float = _DEFAULT_RATIFICATION_THRESHOLD,
) -> RatifiedIntent:
    """Ratify a seeded intent against the prompt versor.

    The seed classifier produces ``intent`` syntactically. This function
    scores **only** the prompt field versor against the intent subspace
    anchors in ``vocab`` via conformal argmax:

        score = max_i cga_inner(prompt, anchor_i)

    No subject self-inner boost, no string-grounded survival path.

    Outcomes:

      * ``RATIFIED`` — prompt field correlates with the intent subspace
        at or above ``threshold``.
      * ``DEMOTED`` — field disagrees, seed is already ``UNKNOWN``, or
        no grounded anchors exist; intent becomes ``IntentTag.UNKNOWN``.
    """
    if intent.tag is IntentTag.UNKNOWN:
        return RatifiedIntent(
            intent=intent,
            outcome=RatificationOutcome.DEMOTED,
            score=0.0,
            threshold=threshold,
            seed_tag=intent.tag,
        )
    anchors = _intent_subspace_anchors(vocab, intent)
    if not anchors:
        demoted = DialogueIntent(
            tag=IntentTag.UNKNOWN,
            subject=intent.subject,
            secondary_subject=intent.secondary_subject,
            object=intent.object,
            relation=intent.relation,
            negated=intent.negated,
            frame=intent.frame,
        )
        return RatifiedIntent(
            intent=demoted,
            outcome=RatificationOutcome.DEMOTED,
            score=0.0,
            threshold=threshold,
            seed_tag=intent.tag,
        )
    prompt = np.asarray(prompt_versor, dtype=np.float32)
    # Argmax over intent subspace only — prompt field vs each anchor.
    score = max(float(cga_inner(prompt, a)) for a in anchors)
    if score >= threshold:
        return RatifiedIntent(
            intent=intent,
            outcome=RatificationOutcome.RATIFIED,
            score=score,
            threshold=threshold,
            seed_tag=intent.tag,
        )
    demoted = DialogueIntent(
        tag=IntentTag.UNKNOWN,
        subject=intent.subject,
        secondary_subject=intent.secondary_subject,
        object=intent.object,
        relation=intent.relation,
        negated=intent.negated,
        frame=intent.frame,
    )
    return RatifiedIntent(
        intent=demoted,
        outcome=RatificationOutcome.DEMOTED,
        score=score,
        threshold=threshold,
        seed_tag=intent.tag,
    )


def region_for_intent(
    intent: DialogueIntent,
    *,
    vocab,
    label: str | None = None,
) -> AdmissibilityRegion:
    """Build an ``AdmissibilityRegion`` from a (ratified) intent.

    The region's relation blade is the outer-product chain of
    grounded anchors for the intent's subject, predicate-anchor, and
    (when present) relation token.  Tokens that are not in the
    vocabulary are skipped — they cannot contribute to the blade.

    An intent that grounds *no* tokens yields an unconstrained
    region; this is the same behavior the propose/realize sites
    already accept (region=None) and preserves backwards
    compatibility during the ADR-0022 transition window
    (§TBD-3).
    """
    anchors: list[np.ndarray] = []
    candidates: list[str] = []
    if intent.subject:
        candidates.append(intent.subject.lower())
    if intent.relation:
        candidates.append(intent.relation.lower())
    match intent.tag:
        case IntentTag.DEFINITION:
            candidates.append("is")
        case IntentTag.CAUSE:
            candidates.append("causes")
        case _:
            pass
    for token in candidates:
        try:
            anchors.append(np.asarray(vocab.get_versor(token), dtype=np.float32))
        except (KeyError, AttributeError):
            continue
    if not anchors:
        return AdmissibilityRegion(label=label or f"intent[{intent.tag.value}]")
    return region_from_relation_chain(
        anchors,
        label=label or f"intent[{intent.tag.value}]",
    )
