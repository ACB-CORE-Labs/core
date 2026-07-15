"""core.physics.self_authorship — Self-Authorship Miner scaffold (ADR-0240)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Mapping, Sequence

import numpy as np

from algebra.backend import versor_condition
from algebra.cl41 import N_COMPONENTS
from core.physics.dynamic_manifold import conformal_procrustes
from core.physics.goldtether import GoldTetherMonitor, coherence_residual
from core.physics.surprise import dual_procrustes_surprise, surprise_residual


@dataclass(frozen=True, slots=True)
class AuthorshipProposal:
    proposal_id: str
    kind: str
    epistemic_status: str
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
    def __init__(
        self,
        *,
        goldtether: GoldTetherMonitor | None = None,
        residual_threshold: float = 1e-5,
    ) -> None:
        self.goldtether = goldtether or GoldTetherMonitor()
        self.residual_threshold = float(residual_threshold)

    def mine_from_trajectory(
        self,
        current: np.ndarray,
        reference: np.ndarray,
        *,
        basis: Sequence[np.ndarray] | np.ndarray | None = None,
        notes: str = "",
    ) -> tuple[AuthorshipProposal, ...]:
        cur = np.asarray(current, dtype=np.float64)
        ref = np.asarray(reference, dtype=np.float64)
        if cur.shape != (N_COMPONENTS,) or ref.shape != (N_COMPONENTS,):
            raise ValueError("current and reference must be 32-component multivectors")

        r_cur = coherence_residual(cur)
        r_ref = coherence_residual(ref)
        try:
            V, proc_r = conformal_procrustes(ref, cur)
            closed = versor_condition(V) < 1e-6
        except ValueError as exc:
            V, proc_r, closed = None, float("inf"), False
            err = str(exc)
        else:
            err = ""

        closure_proof = {
            "coherence_residual_current": float(r_cur),
            "coherence_residual_reference": float(r_ref),
            "procrustes_residual": float(proc_r),
            "procrustes_closed": closed,
            "procrustes_error": err,
            "versor_condition_current": float(versor_condition(cur)),
            "versor_condition_reference": float(versor_condition(ref)),
        }

        proposals: list[AuthorshipProposal] = []
        if r_cur >= self.residual_threshold or proc_r >= self.residual_threshold:
            body = {
                "notes": notes,
                "suggested_action": "review_coherence_gap",
                "residual_current": float(r_cur),
            }
            pid = _content_id({"kind": "coherence_gap", "body": body, "proof": closure_proof})
            proposals.append(
                AuthorshipProposal(
                    proposal_id=f"selfauth-{pid}",
                    kind="coherence_gap",
                    epistemic_status="SPECULATIVE",
                    drift_residual=float(max(r_cur, proc_r if np.isfinite(proc_r) else r_cur)),
                    closure_proof=closure_proof,
                    body=body,
                    adr_refs=("ADR-0238", "ADR-0240"),
                )
            )

        if basis is not None:
            B = np.asarray(basis, dtype=np.float64)
            if B.ndim == 1:
                B = B.reshape(N_COMPONENTS, 1)
            elif B.shape[0] != N_COMPONENTS and B.shape[1] == N_COMPONENTS:
                B = B.T
            dual = dual_procrustes_surprise(ref, cur, B)
            if not dual["transfer_accepted"]:
                body = {
                    "notes": notes,
                    "suggested_action": "review_surprise_boundary",
                    "surprise_norm": float(dual["surprise_norm"]),
                    "procrustes_residual": float(dual["procrustes_residual"]),
                }
                pid = _content_id({"kind": "surprise_boundary", "body": body})
                proposals.append(
                    AuthorshipProposal(
                        proposal_id=f"selfauth-{pid}",
                        kind="surprise_boundary",
                        epistemic_status="SPECULATIVE",
                        drift_residual=float(dual["surprise_norm"]),
                        closure_proof=closure_proof,
                        body=body,
                        adr_refs=("ADR-0239", "ADR-0240"),
                    )
                )

        proposals.sort(key=lambda p: p.proposal_id)
        return tuple(proposals)
