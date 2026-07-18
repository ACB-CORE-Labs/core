"""core.ports.integrity_handoff — Ring 3 integrity-coordinated handoff (ADR-0248).

The preflight §9 fixes Ring 3's boundary: "Integrity coordinates handoffs; it
does not replace content-bearing cognition." This module is exactly that
coordination seam — a pure function that fuses:

  * the Ring-2 per-port action decisions (from the append-only replay chain),
  * the content organs' EXISTING epistemic standing (:class:`EpistemicState`),
  * the turn's EXISTING normative clearance (:class:`NormativeClearance`),

into one typed routing decision — ``proceed`` / ``hedge`` / ``abstain`` — for
discourse-planning and composition consumers. It carries NO content fields:
what gets said (if anything) remains the content organs' job; this only
decides whether integrity permits saying it plainly, qualified, or not at all.

Fusion rules (deterministic, conservative — the integrity floor is
conjunctive; the strongest restriction wins):

  1. no port evidence, or an unverifiable replay chain → ABSTAIN (fail-closed)
  2. any port abstained → ABSTAIN
  3. normative VIOLATED or SUPPRESSED → ABSTAIN
  4. normative UNASSESSABLE → at most HEDGE
  5. weak epistemic standing (undetermined / unverified / ambiguous /
     contradicted / needs-state / scope- or compute-bounded) → at most HEDGE
  6. otherwise → PROCEED

HEDGE (not ABSTAIN) for weak standing mirrors the existing hedge-injection
doctrine: qualified content may still surface; only integrity violations
silence a turn. The handoff binds the replay-chain tip digest so every routing
decision is auditable back to each port's recorded evidence.

Pure, deterministic, off-serving. Observe-only: nothing at serve consumes this
yet; wiring it into discourse planning is a future, flag-gated unit.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Sequence

from core.epistemic_state import EpistemicState, NormativeClearance
from core.ports.residual_protocol import (
    ACTION_ABSTAIN,
    ReplayRecord,
    verify_replay_chain,
)

HANDOFF_PROCEED: str = "proceed"
HANDOFF_HEDGE: str = "hedge"
HANDOFF_ABSTAIN: str = "abstain"

# Epistemic states whose standing is too weak for an unqualified PROCEED —
# content may still surface, hedged (mirrors the ADR-0028/0031 hedge doctrine).
_WEAK_EPISTEMIC_STATES: frozenset[EpistemicState] = frozenset(
    {
        EpistemicState.UNDETERMINED,
        EpistemicState.UNVERIFIED_POSSIBLE,
        EpistemicState.UNVERIFIED_NOVEL,
        EpistemicState.AMBIGUOUS,
        EpistemicState.CONTRADICTED,
        EpistemicState.EPISTEMIC_STATE_NEEDED,
        EpistemicState.SCOPE_BOUNDARY,
        EpistemicState.COMPUTATIONALLY_BOUNDED,
    }
)


@dataclass(frozen=True)
class IntegrityHandoff:
    """The typed routing decision integrity hands to content consumers.

    Deliberately content-free: routing, attribution, and digests only —
    Ring 3's contract is coordination, never generation.
    """

    handoff: str  # HANDOFF_PROCEED | HANDOFF_HEDGE | HANDOFF_ABSTAIN
    reasons: tuple[str, ...]
    port_actions: tuple[tuple[str, str], ...]  # (port_id, action) in chain order
    chain_tip_digest: str
    epistemic_state: str
    normative_clearance: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "handoff": self.handoff,
            "reasons": list(self.reasons),
            "port_actions": [[p, a] for p, a in self.port_actions],
            "chain_tip_digest": self.chain_tip_digest,
            "epistemic_state": self.epistemic_state,
            "normative_clearance": self.normative_clearance,
        }

    def handoff_digest(self) -> str:
        canonical = json.dumps(
            self.as_dict(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def coordinate_handoff(
    chain: Sequence[ReplayRecord],
    *,
    epistemic_state: EpistemicState,
    normative_clearance: NormativeClearance,
) -> IntegrityHandoff:
    """Fuse port decisions + content-organ standing into one routing decision.

    See the module docstring for the rule order. Conservative by construction:
    the strongest restriction wins, and missing/unverifiable evidence abstains.
    """
    port_actions = tuple((r.port_id, r.action) for r in chain)
    reasons: list[str] = []
    level = HANDOFF_PROCEED

    if not chain:
        level = HANDOFF_ABSTAIN
        reasons.append("no_port_evidence")
    elif not verify_replay_chain(chain):
        level = HANDOFF_ABSTAIN
        reasons.append("replay_chain_invalid")
    else:
        for record in chain:
            if record.action == ACTION_ABSTAIN:
                level = HANDOFF_ABSTAIN
                for reason in record.reasons or ("unspecified",):
                    reasons.append(f"port:{record.port_id}:{reason}")
        if normative_clearance in (
            NormativeClearance.VIOLATED,
            NormativeClearance.SUPPRESSED,
        ):
            level = HANDOFF_ABSTAIN
            reasons.append(f"normative:{normative_clearance.value}")
        elif normative_clearance is NormativeClearance.UNASSESSABLE:
            if level == HANDOFF_PROCEED:
                level = HANDOFF_HEDGE
            reasons.append("normative:unassessable")
        if epistemic_state in _WEAK_EPISTEMIC_STATES:
            if level == HANDOFF_PROCEED:
                level = HANDOFF_HEDGE
            reasons.append(f"epistemic:{epistemic_state.value}")

    return IntegrityHandoff(
        handoff=level,
        reasons=tuple(reasons),
        port_actions=port_actions,
        chain_tip_digest=chain[-1].record_digest() if chain else "",
        epistemic_state=epistemic_state.value,
        normative_clearance=normative_clearance.value,
    )
