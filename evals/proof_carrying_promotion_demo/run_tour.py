"""Proof-carrying coherence promotion demo (PR D of ADR-0218).

Demonstrates the pure proof-carrying promotion decider and the mutation owner.
- Scene 1: Valid entailment from COHERENT premises promotes successfully.
- Scene 2: Unentailed consistency stays SPECULATIVE.
- Scene 3: Uncertified reading fails closed.
- Scene 4: Proposer payload (data) is ignored.
"""

from __future__ import annotations

import json
from typing import Any

import numpy as np

from algebra.cga import embed_point
from teaching.epistemic import EpistemicStatus
from teaching.proof_promotion import certify_promotion
from vault.store import VaultStore

_VERBOSE = True


def _say(*args, **kwargs) -> None:
    if _VERBOSE:
        print(*args, **kwargs)


def _print_header(title: str, claim: str) -> None:
    _say()
    _say("─" * 72)
    _say(f"  {title}")
    _say("─" * 72)
    _say(f"  CLAIM: {claim}")
    _say()


def _versor(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    return embed_point(rng.standard_normal(3).astype(np.float32))


def _store(
    vault: VaultStore,
    seed: int,
    form: str,
    status: EpistemicStatus,
    *,
    certified: bool = True,
) -> int:
    metadata: dict = {"reading_certified": certified, "propositional_form": form}
    return vault.store(_versor(seed), metadata, epistemic_status=status)


class _PoisonedPayload(dict):
    """A proposer payload that detonates on ANY read."""
    def _boom(self, *args, **kwargs):
        raise AssertionError("certify_promotion read the proposer payload — D3.5 violated")
    __getitem__ = _boom
    __iter__ = _boom
    __len__ = _boom
    __contains__ = _boom
    get = _boom
    keys = _boom
    values = _boom
    items = _boom


def _scene_1_valid_promotion() -> dict[str, Any]:
    _print_header(
        "Scene 1 — Valid deductive entailment promotes.",
        "A SPECULATIVE claim deductively entailed by COHERENT premises is certified and promoted."
    )
    vault = VaultStore(reproject_interval=0)
    p1 = _store(vault, 101, "p", EpistemicStatus.COHERENT)
    p2 = _store(vault, 102, "p -> q", EpistemicStatus.COHERENT)
    c1 = _store(vault, 7, "q", EpistemicStatus.SPECULATIVE)
    
    _say(f"    [Setup] Premise 1 (COHERENT): 'p' (entry {p1})")
    _say(f"    [Setup] Premise 2 (COHERENT): 'p -> q' (entry {p2})")
    _say(f"    [Setup] Claim (SPECULATIVE): 'q' (entry {c1})")
    
    decision = certify_promotion(
        claim_entry_index=c1,
        premise_entry_indices=(p1, p2),
        vault=vault,
    )
    _say(f"    [Decider] Promoted? {decision.promoted}")
    _say(f"    [Decider] Reason: {decision.reason}")
    
    mutation_applied = False
    if decision.promoted and decision.certificate:
        result = vault.apply_certified_promotion(c1, decision.certificate)
        _say(f"    [Mutation] applied: {result.applied}, reason: {result.reason}")
        mutation_applied = result.applied
        
        # Verify store state
        meta = next((m for i, m in vault.iter_metadata() if i == c1), None)
        if meta:
            _say(f"    [Verify] Final status in vault: {meta['epistemic_status']}")
        
    return {
        "promoted": decision.promoted,
        "reason": decision.reason,
        "mutation_applied": mutation_applied
    }


def _scene_2_not_entailed() -> dict[str, Any]:
    _print_header(
        "Scene 2 — Unentailed consistency stays SPECULATIVE.",
        "A claim consistent with premises but not entailed refuses to promote."
    )
    vault = VaultStore(reproject_interval=0)
    p1 = _store(vault, 101, "p", EpistemicStatus.COHERENT)
    c1 = _store(vault, 7, "q", EpistemicStatus.SPECULATIVE)
    
    _say(f"    [Setup] Premise 1 (COHERENT): 'p' (entry {p1})")
    _say(f"    [Setup] Claim (SPECULATIVE): 'q' (entry {c1})")
    
    decision = certify_promotion(
        claim_entry_index=c1,
        premise_entry_indices=(p1,),
        vault=vault,
    )
    _say(f"    [Decider] Promoted? {decision.promoted}")
    _say(f"    [Decider] Reason: {decision.reason}")
    
    return {
        "promoted": decision.promoted,
        "reason": decision.reason,
    }


def _scene_3_missing_reading() -> dict[str, Any]:
    _print_header(
        "Scene 3 — Uncertified reading fails closed.",
        "A valid entailment fails closed if a premise lacks curator reading certification."
    )
    vault = VaultStore(reproject_interval=0)
    p1 = _store(vault, 101, "p", EpistemicStatus.COHERENT, certified=False)
    p2 = _store(vault, 102, "p -> q", EpistemicStatus.COHERENT)
    c1 = _store(vault, 7, "q", EpistemicStatus.SPECULATIVE)
    
    _say(f"    [Setup] Premise 1 (COHERENT, NO CERT): 'p' (entry {p1})")
    _say(f"    [Setup] Premise 2 (COHERENT): 'p -> q' (entry {p2})")
    _say(f"    [Setup] Claim (SPECULATIVE): 'q' (entry {c1})")
    
    decision = certify_promotion(
        claim_entry_index=c1,
        premise_entry_indices=(p1, p2),
        vault=vault,
    )
    _say(f"    [Decider] Promoted? {decision.promoted}")
    _say(f"    [Decider] Reason: {decision.reason}")
    
    return {
        "promoted": decision.promoted,
        "reason": decision.reason,
    }


def _scene_4_proposer_payload_ignored() -> dict[str, Any]:
    _print_header(
        "Scene 4 — Proposer payload is data, not authority.",
        "The decider provably ignores proposer_payload. If it reads it, the demo crashes."
    )
    vault = VaultStore(reproject_interval=0)
    p1 = _store(vault, 101, "p", EpistemicStatus.COHERENT)
    p2 = _store(vault, 102, "p -> q", EpistemicStatus.COHERENT)
    c1 = _store(vault, 7, "q", EpistemicStatus.SPECULATIVE)
    
    _say(f"    [Setup] Premise 1 (COHERENT): 'p' (entry {p1})")
    _say(f"    [Setup] Premise 2 (COHERENT): 'p -> q' (entry {p2})")
    _say(f"    [Setup] Claim (SPECULATIVE): 'q' (entry {c1})")
    _say(f"    [Setup] Proposer payload: detonating dictionary")
    
    payload = _PoisonedPayload()
    decision = certify_promotion(
        claim_entry_index=c1,
        premise_entry_indices=(p1, p2),
        vault=vault,
        proposer_payload=payload,
    )
    _say(f"    [Decider] Promoted? {decision.promoted}")
    _say(f"    [Decider] Reason: {decision.reason}")
    _say(f"    [EVIDENCE] Demo did not crash; payload was ignored.")
    
    return {
        "promoted": decision.promoted,
        "reason": decision.reason,
    }


def run_tour(*, emit_json: bool = False) -> dict[str, Any]:
    global _VERBOSE
    _VERBOSE = not emit_json
    if not emit_json:
        _say()
        _say("=" * 72)
        _say("  CORE Proof-Carrying Coherence Promotion Demo")
        _say("=" * 72)
        _say("  Demonstrates ADR-0218 PR D: Local deterministic demo.")
        _say("  Proposer submits claim + proof candidate; CORE recomputes,")
        _say("  promotes or refuses on pinned verification only.")
    
    s1 = _scene_1_valid_promotion()
    s2 = _scene_2_not_entailed()
    s3 = _scene_3_missing_reading()
    s4 = _scene_4_proposer_payload_ignored()
    
    all_passed = (
        s1["promoted"] is True and s1["mutation_applied"] is True and
        s2["promoted"] is False and s2["reason"] == "refused_not_entailed" and
        s3["promoted"] is False and s3["reason"] == "refused_premise_reading_uncertified" and
        s4["promoted"] is True and s4["reason"] == "promoted_entailed_from_coherent_premises"
    )
    
    if not emit_json:
        _say()
        _say("=" * 72)
        _say("  Summary")
        _say("=" * 72)
        _say(f"  Valid entailment promoted:              {s1['promoted']}")
        _say(f"  Unentailed claim refused:               {not s2['promoted']}")
        _say(f"  Uncertified reading refused:            {not s3['promoted']}")
        _say(f"  Proposer payload ignored safely:        {s4['promoted']}")
        _say()
    
    return {
        "scene_1_valid_promotion": s1,
        "scene_2_not_entailed": s2,
        "scene_3_missing_reading": s3,
        "scene_4_proposer_payload_ignored": s4,
        "all_passed": all_passed,
    }


if __name__ == "__main__":
    import sys
    emit_json = "--json" in sys.argv
    result = run_tour(emit_json=emit_json)
    if emit_json:
        print(json.dumps(result, indent=2))
