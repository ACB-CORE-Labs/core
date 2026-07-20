"""Sealed four-arm ablation harness for observed-HE morph constraint v0."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from generate.observed_he_morph_v0.consumer import (
    ConstraintDecision,
    DecisionKind,
    apply_he_morph_constraint,
)
from generate.observed_he_morph_v0.records import load_observed_morphology


@dataclass(frozen=True, slots=True)
class ArmResult:
    arm: str
    decision: ConstraintDecision
    digest: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "arm": self.arm,
            "decision": self.decision.as_dict(),
            "digest": self.digest,
        }


@dataclass(frozen=True, slots=True)
class AblationReport:
    arms: tuple[ArmResult, ...]
    metadata_bit_identical_to_canonical: bool
    executable_changed_decision: bool
    wrong_count: int
    refusal_correct: bool
    provenance_complete: bool

    def as_dict(self) -> dict[str, Any]:
        return {
            "arms": [a.as_dict() for a in self.arms],
            "metadata_bit_identical_to_canonical": self.metadata_bit_identical_to_canonical,
            "executable_changed_decision": self.executable_changed_decision,
            "wrong_count": self.wrong_count,
            "refusal_correct": self.refusal_correct,
            "provenance_complete": self.provenance_complete,
        }


def _digest(decision: ConstraintDecision) -> str:
    payload = json.dumps(decision.as_dict(), sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def run_four_arm_ablation(
    *,
    lemma_key: str = "דבר",
    he_surface_plural: str | None = None,
    proposal_singular_claim: str = "דבר must be singular only — exclusive singular identity",
    proposal_neutral: str = "דבר is a logos utterance",
) -> AblationReport:
    """Run the sealed four-arm harness over compiled HE pack data."""
    catalog = load_observed_morphology("he_logos_micro_v1")
    # Prefer a known plural row from the pack.
    plural = next((s for s in catalog if s.number == "plural"), None)
    if plural is None:
        raise RuntimeError("compiled pack has no plural morphology row")
    surface = he_surface_plural or plural.surface
    lemma = plural.lemma

    arms: list[ArmResult] = []

    # 1. canonical-only baseline
    d_can = apply_he_morph_constraint(
        proposal_text=proposal_singular_claim,
        lemma_key=lemma,
        observed_catalog=catalog,
        mode="canonical",
        he_surface=surface,
    )
    arms.append(ArmResult("canonical", d_can, _digest(d_can)))

    # 2. metadata-only (must be decision-identical to canonical PASS)
    d_meta = apply_he_morph_constraint(
        proposal_text=proposal_singular_claim,
        lemma_key=lemma,
        observed_catalog=catalog,
        mode="metadata",
        he_surface=surface,
    )
    arms.append(ArmResult("metadata", d_meta, _digest(d_meta)))

    # 3. executable mapping rule
    d_exec = apply_he_morph_constraint(
        proposal_text=proposal_singular_claim,
        lemma_key=lemma,
        observed_catalog=catalog,
        mode="executable",
        he_surface=surface,
    )
    arms.append(ArmResult("executable", d_exec, _digest(d_exec)))

    # 4. adversarial: OOV + invalid + ambiguous
    d_oov = apply_he_morph_constraint(
        proposal_text=proposal_singular_claim,
        lemma_key=lemma,
        observed_catalog=catalog,
        mode="adversarial",
        he_surface="לא_קיים_oov_zzz",
    )
    d_missing = apply_he_morph_constraint(
        proposal_text=proposal_singular_claim,
        lemma_key=lemma,
        observed_catalog=catalog,
        mode="adversarial",
        he_surface=None,
    )
    # Bundle adversarial as one arm: all must fail closed
    adv_ok = (
        d_oov.kind is DecisionKind.FAIL_CLOSED
        and d_missing.kind is DecisionKind.FAIL_CLOSED
    )
    arms.append(
        ArmResult(
            "adversarial",
            d_oov if d_oov.kind is DecisionKind.FAIL_CLOSED else d_missing,
            _digest(d_oov),
        )
    )

    # Metrics — Stage 4 requires metadata bit-identical to canonical baseline
    # (full SHA-256 of decision payload, not kind-only equality).
    meta_identical = _digest(d_meta) == _digest(d_can) and d_meta.kind is DecisionKind.PASS
    # Executable must change decision to ABSTAIN vs baseline PASS.
    exec_changed = (
        d_can.kind is DecisionKind.PASS and d_exec.kind is DecisionKind.ABSTAIN
    )
    wrong = 0
    if not meta_identical:
        wrong += 1
    if not exec_changed:
        wrong += 1
    if not adv_ok:
        wrong += 1

    # Provenance: executable arm carries constraint with source_span
    provenance_ok = False
    if d_exec.constraints:
        payload = d_exec.constraints[0].payload
        provenance_ok = (
            "source_span" in payload
            and "morphology_id" in payload
            and "source_pack_id" in payload
        )

    return AblationReport(
        arms=tuple(arms),
        metadata_bit_identical_to_canonical=meta_identical,
        executable_changed_decision=exec_changed,
        wrong_count=wrong,
        refusal_correct=adv_ok,
        provenance_complete=provenance_ok,
    )
