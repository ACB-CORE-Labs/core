"""Analogical transfer validation harness (ADR-0240)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import numpy as np

from algebra.cl41 import N_COMPONENTS
from algebra.rotor import make_rotor_from_angle
from algebra.versor import unitize_versor, versor_apply, versor_condition
from core.physics.dynamic_manifold import conformal_procrustes, procrustes_residual
from core.physics.goldtether import GoldTetherMonitor, coherence_residual
from core.physics.surprise import dual_procrustes_surprise, surprise_residual


@dataclass(frozen=True, slots=True)
class TransferCase:
    case_id: str
    source_domain: str
    target_domain: str
    source: np.ndarray
    target: np.ndarray
    novel_query: np.ndarray
    expected_novel: np.ndarray


@dataclass(frozen=True, slots=True)
class TransferResult:
    case_id: str
    residual: float
    goldtether_before: float
    goldtether_after: float
    correct: bool
    refused: bool
    reason: str


@dataclass(frozen=True, slots=True)
class AnalogicalTransferReport:
    results: tuple[TransferResult, ...]
    counts: dict[str, int]
    max_residual: float
    wrong: int

    @property
    def all_correct_or_refused(self) -> bool:
        return self.wrong == 0


def _identity() -> np.ndarray:
    v = np.zeros(N_COMPONENTS, dtype=np.float64)
    v[0] = 1.0
    return v


def make_fixture_pair() -> TransferCase:
    src = _identity()
    R = make_rotor_from_angle(0.7, bivector_idx=6)
    tgt = versor_apply(R, src)
    novel_q = unitize_versor(make_rotor_from_angle(0.3, bivector_idx=7))
    expected = versor_apply(R, novel_q)
    return TransferCase(
        case_id="fixture-rotation-transfer-v1",
        source_domain="domain_a_geometry",
        target_domain="domain_b_geometry",
        source=src,
        target=tgt,
        novel_query=novel_q,
        expected_novel=expected,
    )


def run_analogical_transfer(
    cases: Sequence[TransferCase],
    *,
    residual_threshold: float = 0.35,
    goldtether: GoldTetherMonitor | None = None,
) -> AnalogicalTransferReport:
    """Learn map source→target, apply to novel_query; gate with residual + GoldTether."""
    mon = goldtether or GoldTetherMonitor()
    results: list[TransferResult] = []
    counts = {"correct": 0, "wrong": 0, "refused": 0}

    for case in cases:
        gt_before = mon.residual(case.novel_query)
        try:
            V, proc_r = conformal_procrustes(case.source, case.target)
            mapped = versor_apply(V, case.novel_query)
            residual = float(np.linalg.norm(mapped - case.expected_novel))
            residual = min(residual, procrustes_residual(case.novel_query, case.expected_novel, V))
            closed = versor_condition(mapped) < 1e-6 and versor_condition(V) < 1e-6
            gt_after = mon.residual(mapped)
        except ValueError as exc:
            results.append(
                TransferResult(
                    case_id=case.case_id,
                    residual=float("inf"),
                    goldtether_before=gt_before,
                    goldtether_after=gt_before,
                    correct=False,
                    refused=True,
                    reason=f"refused:{exc}",
                )
            )
            counts["refused"] += 1
            continue

        basis = np.column_stack([_identity(), case.source])
        _sur_v, sur_n = surprise_residual(case.novel_query, basis)
        dual = dual_procrustes_surprise(case.source, case.target, basis)

        if not closed:
            results.append(
                TransferResult(
                    case_id=case.case_id,
                    residual=residual,
                    goldtether_before=gt_before,
                    goldtether_after=gt_after,
                    correct=False,
                    refused=True,
                    reason="closure_failed",
                )
            )
            counts["refused"] += 1
            continue

        # GoldTether residual must not increase (package acceptance criterion)
        gt_ok = gt_after <= gt_before + 1e-9
        if residual <= residual_threshold and gt_ok:
            mon.update(mapped, epistemic_elevation=True)
            results.append(
                TransferResult(
                    case_id=case.case_id,
                    residual=residual,
                    goldtether_before=gt_before,
                    goldtether_after=gt_after,
                    correct=True,
                    refused=False,
                    reason="transfer_ok",
                )
            )
            counts["correct"] += 1
        else:
            results.append(
                TransferResult(
                    case_id=case.case_id,
                    residual=residual,
                    goldtether_before=gt_before,
                    goldtether_after=gt_after,
                    correct=False,
                    refused=False,
                    reason=(
                        "goldtether_increased"
                        if not gt_ok
                        else f"residual_above_threshold sur={sur_n:.3g} dual={dual['procrustes_residual']:.3g}"
                    ),
                )
            )
            counts["wrong"] += 1

    max_res = max((r.residual for r in results if np.isfinite(r.residual)), default=0.0)
    return AnalogicalTransferReport(
        results=tuple(results),
        counts=counts,
        max_residual=float(max_res),
        wrong=int(counts["wrong"]),
    )
