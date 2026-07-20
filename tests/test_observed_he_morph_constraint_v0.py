"""Stage 4 — observed-HE morph constraint v0 four-arm ablation."""

from __future__ import annotations

from generate.observed_he_morph_v0 import (
    PLURAL_ABSTAIN_RULE_V0,
    apply_he_morph_constraint,
    load_observed_morphology,
    run_four_arm_ablation,
)
from generate.observed_he_morph_v0.consumer import DecisionKind
from teaching.epistemic import EpistemicStatus
from teaching.store import TeachingStore
from teaching.review import ReviewedTeachingExample, ReviewOutcome
from teaching.correction import CorrectionCandidate
from generate.intent import DialogueIntent, IntentTag


def test_load_compiled_he_morphology_with_provenance():
    rows = load_observed_morphology("he_logos_micro_v1")
    assert len(rows) >= 1
    assert all(r.language == "he" for r in rows)
    assert all(r.source_pack_id == "he_logos_micro_v1" for r in rows)
    assert all(isinstance(r.source_span, tuple) and len(r.source_span) == 2 for r in rows)
    assert any(r.number == "plural" for r in rows)
    assert any(r.root for r in rows)


def test_four_arm_ablation_sealed_metrics():
    report = run_four_arm_ablation()
    assert report.metadata_bit_identical_to_canonical is True
    assert report.executable_changed_decision is True
    assert report.wrong_count == 0
    assert report.refusal_correct is True
    assert report.provenance_complete is True
    arms = {a.arm: a for a in report.arms}
    assert arms["canonical"].decision.kind is DecisionKind.PASS
    assert arms["metadata"].decision.kind is DecisionKind.PASS
    assert arms["executable"].decision.kind is DecisionKind.ABSTAIN
    assert arms["adversarial"].decision.kind is DecisionKind.FAIL_CLOSED


def test_metadata_only_inert_vs_executable_effect():
    import hashlib
    import json

    catalog = load_observed_morphology("he_logos_micro_v1")
    plural = next(s for s in catalog if s.number == "plural")
    claim = f"{plural.lemma} must be singular only — exclusive singular identity"
    can = apply_he_morph_constraint(
        proposal_text=claim,
        lemma_key=plural.lemma,
        observed_catalog=catalog,
        mode="canonical",
        he_surface=plural.surface,
    )
    meta = apply_he_morph_constraint(
        proposal_text=claim,
        lemma_key=plural.lemma,
        observed_catalog=catalog,
        mode="metadata",
        he_surface=plural.surface,
    )
    exe = apply_he_morph_constraint(
        proposal_text=claim,
        lemma_key=plural.lemma,
        observed_catalog=catalog,
        mode="executable",
        he_surface=plural.surface,
    )
    # Bit-identical decision payloads (Stage 4 sealed requirement).
    d_can = hashlib.sha256(
        json.dumps(can.as_dict(), sort_keys=True).encode()
    ).hexdigest()
    d_meta = hashlib.sha256(
        json.dumps(meta.as_dict(), sort_keys=True).encode()
    ).hexdigest()
    assert d_can == d_meta
    assert meta.kind is DecisionKind.PASS
    assert exe.kind is DecisionKind.ABSTAIN
    assert exe.rule_id == PLURAL_ABSTAIN_RULE_V0.rule_id
    # Typed IR — no free meaning dict; provenance on fields + LogosConstraint.
    c0 = exe.constraints[0]
    assert c0.morphology_id
    assert c0.source_pack_id
    assert c0.rule_id == PLURAL_ABSTAIN_RULE_V0.rule_id
    assert c0.provenance_complete is True
    logos = c0.to_logos_constraint()
    assert logos.constraint_id == c0.constraint_id
    assert logos.provenance_complete is True


def test_oov_and_invalid_fail_closed():
    catalog = load_observed_morphology("he_logos_micro_v1")
    oov = apply_he_morph_constraint(
        proposal_text="x",
        lemma_key="x",
        observed_catalog=catalog,
        mode="executable",
        he_surface="zzz_not_in_pack",
    )
    assert oov.kind is DecisionKind.FAIL_CLOSED
    assert oov.reason == "oov_he_surface"


def test_teaching_store_consumer_seam_abstains_on_plural_rule():
    """Live TeachingStore.add path: HE plural rule auto-applies (no test-only kwarg)."""
    catalog = load_observed_morphology("he_logos_micro_v1")
    plural = next(s for s in catalog if s.number == "plural")
    store = TeachingStore(capacity=8)

    cand1 = CorrectionCandidate(
        correction_text=f"{plural.lemma} is a logos utterance",
        intent=DialogueIntent(tag=IntentTag.CORRECTION, subject=plural.lemma),
        prior_surface="prior",
        prior_turn=0,
        candidate_id="c1",
    )
    rev1 = ReviewedTeachingExample(
        candidate=cand1,
        outcome=ReviewOutcome.ACCEPTED,
        review_hash="h1",
        epistemic_status=EpistemicStatus.SPECULATIVE,
    )
    p1 = store.add(rev1)
    assert p1 is not None

    # Correction text includes the observed HE plural surface so the live
    # auto-path in TeachingStore.add finds the catalog row and abstains.
    cand2 = CorrectionCandidate(
        correction_text=(
            f"{plural.surface} ({plural.lemma}) must be singular only — "
            f"exclusive singular identity"
        ),
        intent=DialogueIntent(tag=IntentTag.CORRECTION, subject=plural.lemma),
        prior_surface="prior",
        prior_turn=1,
        candidate_id="c2",
    )
    rev2 = ReviewedTeachingExample(
        candidate=cand2,
        outcome=ReviewOutcome.ACCEPTED,
        review_hash="h2",
        epistemic_status=EpistemicStatus.SPECULATIVE,
    )
    # No he_morph_decision kwarg — production auto-path must fire.
    p2 = store.add(rev2)
    assert p2 is not None
    assert p2.epistemic_status is EpistemicStatus.CONTESTED


def test_vault_promotion_default_requires_geometric_unitarity():
    """Production VaultPromotionPolicy() uses 1e-6 residual, not soft 0.05."""
    from core.physics.learning import VaultPromotionPolicy
    from core.physics.energy import EnergyClass, EnergyProfile

    policy = VaultPromotionPolicy()  # production default
    assert policy.residual_threshold <= 1e-6
    soft = EnergyProfile(
        raw=0.05, energy_class=EnergyClass.E0, coherence_residual=0.02
    )
    assert policy.decide(soft).promote is False
    tight = EnergyProfile(
        raw=0.05, energy_class=EnergyClass.E0, coherence_residual=1e-9
    )
    assert policy.decide(tight).promote is True


def test_shared_authority_four_modes_and_typed_ir():
    """Live authority entry shares apply_he_morph_constraint; modes diverge correctly."""
    from generate.observed_he_morph_v0.authority import (
        evaluate_logos_on_text,
        first_logos_constraint,
        logos_blocks_certified_answer,
    )

    catalog = load_observed_morphology("he_logos_micro_v1")
    plural = next(s for s in catalog if s.number == "plural")
    claim = (
        f"{plural.surface} ({plural.lemma}) must be singular only — "
        f"exclusive singular identity"
    )
    can = evaluate_logos_on_text(text=claim, mode="canonical", catalog=catalog)
    meta = evaluate_logos_on_text(text=claim, mode="metadata", catalog=catalog)
    exe = evaluate_logos_on_text(text=claim, mode="executable", catalog=catalog)
    oov = evaluate_logos_on_text(
        text="zzz_not_a_surface must be singular only",
        mode="adversarial",
        catalog=catalog,
        he_surface="zzz_not_a_surface",
    )
    assert can is not None and meta is not None and exe is not None and oov is not None
    assert can.kind is DecisionKind.PASS
    assert meta.kind is DecisionKind.PASS
    assert can.as_dict() == meta.as_dict()
    assert exe.kind is DecisionKind.ABSTAIN
    assert logos_blocks_certified_answer(exe) is True
    assert oov.kind is DecisionKind.FAIL_CLOSED
    lc = first_logos_constraint(exe)
    assert lc is not None
    assert lc.rule_id == PLURAL_ABSTAIN_RULE_V0.rule_id
    assert lc.source_pack_id == "he_logos_micro_v1"
    assert lc.morphology_id == plural.morphology_id


def test_cognitive_turn_logos_authority_abstains_on_plural_singular_claim():
    """Live CognitiveTurnPipeline.run path: executable morph blocks certified answer."""
    from chat.runtime import ChatRuntime
    from core.cognition.pipeline import CognitiveTurnPipeline

    catalog = load_observed_morphology("he_logos_micro_v1")
    plural = next(s for s in catalog if s.number == "plural")
    claim = (
        f"{plural.surface} ({plural.lemma}) must be singular only — "
        f"exclusive singular identity"
    )
    pipe = CognitiveTurnPipeline(runtime=ChatRuntime())
    result = pipe.run(claim)
    assert result.logos_decision_kind == "abstain"
    assert result.logos_decision_reason == "plural_morph_blocks_singular_exclusivity"
    assert result.logos_rule_id == PLURAL_ABSTAIN_RULE_V0.rule_id
    assert result.logos_constraint_id
    assert result.authority_source == "logos_morph_constraint"
    assert "Abstaining" in result.surface or "abstain" in result.surface.lower()
    assert result.refusal_reason == "plural_morph_blocks_singular_exclusivity"
    # Hazard ledger records morph block (improvement observability).
    assert any("logos_morph" in h for h in result.substrate_hazard)


def test_cognitive_turn_english_only_no_logos_noop():
    """English-only turn does not invent HE morph or force logos authority."""
    from chat.runtime import ChatRuntime
    from core.cognition.pipeline import CognitiveTurnPipeline

    pipe = CognitiveTurnPipeline(runtime=ChatRuntime())
    result = pipe.run("What is light?")
    assert result.logos_decision_kind in ("", "pass")
    assert result.authority_source != "logos_morph_constraint"
    # Must not be a morph abstention surface when no HE present.
    assert "Logos morph" not in result.surface
