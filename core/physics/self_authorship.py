"""core.physics.self_authorship — Self-Authorship Miner scaffold (ADR-0240).

Geometry-guided ADR / teaching proposals under invariants. Emits
**proposal-only** artifacts (SPECULATIVE). Never writes vault COHERENT,
never mutates packs, never touches serving.

Complements the existing auto-proposal corridor (ADR-0151). This miner
produces structured proposal dicts; promotion remains human-reviewed.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.versor import versor_condition
from core.physics.dynamic_manifold import conformal_procrustes, signature_aware_pca
from core.physics.goldtether import CoherenceResidual, GoldTetherMonitor, OperatingMode
from core.physics.surprise import dual_operator, surprise_residual


@dataclass(frozen=True, slots=True)
class AuthorshipProposal:
    """Proposal-only artifact — never auto-accepted."""

    proposal_id: str
    kind: str
    epistemic_status: str  # always SPECULATIVE at emission
    drift_residual: float
    closure_proof: Mapping[str, Any]
    body: Mapping[str, Any]
    adr_refs: tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "kind": self.kind,
            "epistemic_status": self.epistemic_status,
            "drift_residual": self.drift_residual,
            "closure_proof": dict(self.closure_proof),
            "body": dict(self.body),
            "adr_refs": list(self.adr_refs),
        }


def _content_id(payload: Mapping[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


class SelfAuthorshipMiner:
    """Mine minimal extension proposals from geometric residual structure."""

    def __init__(
        self,
        *,
        goldtether: GoldTetherMonitor | None = None,
        residual_threshold: float = 0.25,
    ) -> None:
        self.goldtether = goldtether or GoldTetherMonitor()
        self.residual_threshold = float(residual_threshold)

    def mine_from_trajectory(
        self,
        current: np.ndarray,
        reference: np.ndarray,
        *,
        basis: Sequence[np.ndarray] = (),
        analogs: Sequence[tuple[str, np.ndarray, np.ndarray]] = (),
        notes: str = "",
    ) -> tuple[AuthorshipProposal, ...]:
        """Emit zero or more SPECULATIVE proposals. Never stores them."""
        cur = np.asarray(current, dtype=np.float64)
        ref = np.asarray(reference, dtype=np.float64)
        if cur.shape != (N_COMPONENTS,) or ref.shape != (N_COMPONENTS,):
            raise ValueError("current and reference must be 32-component multivectors")

        residual: CoherenceResidual = self.goldtether.measure(
            cur, ref, mode=OperatingMode.PRACTICE
        )
        proposals: list[AuthorshipProposal] = []

        # Closure proof for the reference/current pair under transition.
        try:
            proc = conformal_procrustes([ref], [cur])
            closure_ok = versor_condition(proc.versor) < 1e-6
            proc_res = float(proc.residual_norm)
        except ValueError as exc:
            closure_ok = False
            proc_res = float("inf")
            proc_err = str(exc)
        else:
            proc_err = ""

        closure_proof = {
            "versor_condition_current": float(versor_condition(cur)),
            "versor_condition_reference": float(versor_condition(ref)),
            "procrustes_residual": proc_res,
            "procrustes_closed": closure_ok,
            "procrustes_error": proc_err,
            "coherence_combined": float(residual.combined),
            "kappa": float(residual.kappa),
        }

        if residual.combined >= self.residual_threshold and closure_ok:
            body = {
                "notes": notes,
                "suggested_action": "review_coherence_gap",
                "drift": float(residual.drift),
                "geometric_distance": float(residual.geometric_distance),
            }
            pid = _content_id({"kind": "coherence_gap", "body": body, "proof": closure_proof})
            proposals.append(
                AuthorshipProposal(
                    proposal_id=f"selfauth-{pid}",
                    kind="coherence_gap",
                    epistemic_status="SPECULATIVE",
                    drift_residual=float(residual.combined),
                    closure_proof=closure_proof,
                    body=body,
                    adr_refs=("ADR-0238", "ADR-0240"),
                )
            )

        if basis:
            surp = surprise_residual(cur, basis)
            dual = dual_operator(
                cur,
                basis,
                analogs,
                kappa=max(residual.kappa, 1e-6),
            )
            if dual.productive:
                body = {
                    "notes": notes,
                    "suggested_action": "review_analogical_extension",
                    "surprise_norm": float(surp.residual_norm),
                    "selected_analog_id": dual.selected_analog_id,
                    "procrustes_residual": (
                        float(dual.procrustes.residual_norm) if dual.procrustes else None
                    ),
                }
                pid = _content_id(
                    {"kind": "analogical_extension", "body": body, "proof": closure_proof}
                )
                proposals.append(
                    AuthorshipProposal(
                        proposal_id=f"selfauth-{pid}",
                        kind="analogical_extension",
                        epistemic_status="SPECULATIVE",
                        drift_residual=float(surp.residual_norm),
                        closure_proof=closure_proof,
                        body=body,
                        adr_refs=("ADR-0239", "ADR-0240"),
                    )
                )

        # Optional manifold annotation when a small cloud is available via analogs.
        cloud = [ref, cur] + [s for _, s, _ in analogs] + [t for _, _, t in analogs]
        if len(cloud) >= 2:
            pca = signature_aware_pca(cloud, max_axes=4)
            if pca.n_null > 0:
                body = {
                    "notes": notes,
                    "suggested_action": "review_null_axes",
                    "n_null": int(pca.n_null),
                    "n_spacelike": int(pca.n_spacelike),
                    "n_timelike": int(pca.n_timelike),
                }
                pid = _content_id({"kind": "null_axis_review", "body": body})
                proposals.append(
                    AuthorshipProposal(
                        proposal_id=f"selfauth-{pid}",
                        kind="null_axis_review",
                        epistemic_status="SPECULATIVE",
                        drift_residual=float(residual.combined),
                        closure_proof=closure_proof,
                        body=body,
                        adr_refs=("ADR-0239", "ADR-0240"),
                    )
                )

        # Stable order by proposal_id for replay-determinism.
        proposals.sort(key=lambda p: p.proposal_id)
        return tuple(proposals)
