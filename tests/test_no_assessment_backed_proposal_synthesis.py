from __future__ import annotations

import dataclasses

import generate.construction_affordances as construction_affordances
from generate.problem_frame_builder import build_problem_frame
from generate.problem_frame_contracts import assess_contracts


def test_builder_does_not_synthesize_proposals_from_assessments() -> None:
    """Construction proposals must originate before ContractAssessment.

    This confirms the stale assessment-backed synthesis path (previously
    via make_proposal) is retired and does not exist, and a normal
    proposal-backed frame builds with the expected proposals.
    """
    import generate.construction_affordances as construction_affordances
    assert not hasattr(construction_affordances, "make_proposal")

    frame = build_problem_frame("Mia has 7 apples. How many apples does Mia have?")

    assert tuple(proposal.family_id for proposal in frame.proposals) == (
        "binding.quantity_entity",
    )
    assert all(proposal.status == "proposed" for proposal in frame.proposals)


def test_contract_assessments_do_not_create_proposal_free_fallback_source() -> None:
    """A proposal-free frame must not produce assessments for backfill synthesis."""

    frame = build_problem_frame("Mia has 7 apples. How many apples does Mia have?")
    proposal_free_frame = dataclasses.replace(frame, proposals=())

    assert assess_contracts(proposal_free_frame) == ()
