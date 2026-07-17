from __future__ import annotations

import hashlib
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Sequence

from core.contemplation.miners.contradiction_detection import (
    mine_contradiction_detection_report,
)
from core.contemplation.miners.frontier_compare import mine_frontier_compare_report
from core.contemplation.schema import (
    ContemplationFinding,
    ContemplationRun,
    format_contemplation_finding_jsonl,
)
from core.contemplation.snapshot import ContemplationSubstrate
from core.physics.surprise import DEFAULT_DISCOVERY_GAMMA, is_discovery_eligible
from teaching.discovery import DiscoveryCandidate, emit_surprise_discovery
from teaching.discovery_sink import DiscoveryCandidateSink

if TYPE_CHECKING:
    # A-04 process quarantine: chat/runtime.py's idle_tick lazily imports THIS
    # module inside the serve process (frontier contemplation pass), and
    # core.physics.multi_scale_energy is on the serve-banned list
    # (tests/test_serve_quarantine_transitive.py).  The gate import is
    # function-local in contemplate_surprise_history; only the type name is
    # needed here.
    from core.physics.multi_scale_energy import CrossBandVerdict


def _config_hash(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _emit_findings(
    findings: Iterable[ContemplationFinding],
    sink: DiscoveryCandidateSink | None,
) -> None:
    """Stream each finding through the shared sink protocol when set.

    No-op when *sink* is ``None`` — preserves the existing "build a
    ``ContemplationRun`` blob" path for callers that want a single
    in-memory result.

    When a sink is supplied, each finding is emitted as one canonical
    JSONL line via :func:`format_contemplation_finding_jsonl`.  This
    is the unification point with the discovery candidate stream
    (ADR-0055 Phase B sinks): both flow through the same
    ``DiscoveryCandidateSink`` protocol, both land in append-only
    monthly JSONL files when paired with
    :class:`teaching.discovery_sink.DiscoveryMonthlyFileSink`.

    Sink errors are NOT swallowed — see ADR-0055 fail-fast contract.
    """
    if sink is None:
        return
    for finding in findings:
        sink.emit(format_contemplation_finding_jsonl(finding))


# --- ADR-0243 §2.4 / ADR-0242 §5-P2 — surprise → discovery wiring ------------
#
# Surprise-signal sourcing (Lane A open question, resolved by reading the
# substrate): `ContemplationFinding` carries no surprise measurement — the
# report-mining paths above have no geometry, and fabricating a per-finding
# number would be exactly the failure mode the brief warns against.  The
# canonical surprise carrier is the ADR-0239 dual-operator audit dict
# (`dual_procrustes_surprise` / `dual_operator` output), produced live by
# `core.physics.self_authorship.SelfAuthorshipMiner` and the ADR-0240
# harness.  The wiring below therefore consumes explicit caller-timed
# observations of that dict; the report-mining finding paths are untouched.


@dataclass(frozen=True, slots=True)
class SurpriseObservation:
    """One caller-timed ADR-0239 dual-operator audit measurement.

    ``t`` is caller-supplied logical time (same clock as ``now`` in
    :func:`contemplate_surprise_history`) — never a wall clock, so the
    pipeline stays deterministic and replayable.
    """

    t: float
    dual: Mapping[str, Any]
    source_turn_trace: str = ""

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.t)):
            raise ValueError("SurpriseObservation.t must be finite")
        if "surprise_norm" not in self.dual:
            raise ValueError(
                "SurpriseObservation.dual must carry 'surprise_norm' "
                "(ADR-0239 dual-operator audit dict)"
            )
        try:
            norm = float(self.dual["surprise_norm"])
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "SurpriseObservation.dual['surprise_norm'] must be numeric"
            ) from exc
        if math.isfinite(norm) and norm < 0.0:
            raise ValueError(
                "SurpriseObservation.dual['surprise_norm'] must be >= 0 "
                "(it is a residual norm)"
            )
        refused = self.dual.get("surprise_refused")
        if refused is not None and not isinstance(refused, str):
            raise ValueError(
                "SurpriseObservation.dual['surprise_refused'] must be a string "
                "refusal reason or None — a non-string truthy marker would "
                "silently read as 'not refused'"
            )
        # Snapshot the mapping (shallow) so the observation cannot be mutated
        # out from under the deterministic gate after construction.
        object.__setattr__(self, "dual", MappingProxyType(dict(self.dual)))


@dataclass(frozen=True, slots=True)
class SurpriseDiscoveryOutcome:
    """Typed audit record of one discovery-gate pass.

    ``reason`` is one of: ``emitted``, ``not_discovery_eligible``,
    ``insufficient_span``, ``band_below_gamma``,
    ``candidate_not_constructed``.
    """

    candidate: DiscoveryCandidate | None
    verdict: CrossBandVerdict | None
    reason: str
    surprise_norm: float
    discovery_gamma: float


def _measured_surprise(dual: Mapping[str, Any]) -> tuple[float, str | None, bool]:
    """Extract (surprise_norm, refusal, productive) from a dual audit dict.

    Types are guaranteed by ``SurpriseObservation.__post_init__`` — the dual
    always carries a numeric ``surprise_norm`` and a ``str | None`` refusal.
    """
    surprise_norm = float(dual["surprise_norm"])
    refusal = dual.get("surprise_refused")
    productive = bool(dual.get("productive", False) or dual.get("transfer_accepted", False))
    return surprise_norm, refusal, productive


def contemplate_surprise_history(
    observations: Sequence[SurpriseObservation],
    *,
    now: float,
    tau0: float = 1.0,
    discovery_gamma: float | None = None,
    sink: DiscoveryCandidateSink | None = None,
) -> SurpriseDiscoveryOutcome:
    """Gate a timed surprise history into at most one ``DiscoveryCandidate``.

    ADR-0243 §2.4: high surprise on a speculative wave is a discovery
    signal, held as a ``DiscoveryCandidate`` and routed to the offline
    review corridor.  Two gates run in order, both ADR-0242 §5 pinned
    primitives with unchanged signatures:

    1. :func:`core.physics.surprise.is_discovery_eligible` on the newest
       observation — measured residual above γ, no metric refusal, not a
       productive transfer.
    2. :func:`core.physics.multi_scale_energy.cross_band_discovery_gate`
       on the measured history — the signal must persist across the
       F5/F6/F7 Fibonacci bands, so transient noise never emits.

    Only when both pass is a candidate built and emitted through the
    existing sink protocol via
    :func:`teaching.discovery.emit_surprise_discovery` — the only side
    effect is ``sink.emit(...)`` (proposal plumbing, never a vault
    write).  Refused observations carry no measured energy and are
    excluded from the band accumulation (exclusion can only lower band
    energy — fail-closed); a refused *newest* observation never emits.
    """
    obs = tuple(observations)
    if not obs:
        raise ValueError("contemplate_surprise_history: empty observation history")
    for earlier, later in zip(obs, obs[1:]):
        if float(later.t) < float(earlier.t):
            raise ValueError(
                "contemplate_surprise_history: observations must be in "
                "non-decreasing time order"
            )

    current = obs[-1]
    surprise_norm, refusal, productive = _measured_surprise(current.dual)
    gamma = float(
        discovery_gamma
        if discovery_gamma is not None
        else current.dual.get("discovery_gamma", DEFAULT_DISCOVERY_GAMMA)
    )

    if not is_discovery_eligible(
        surprise_norm=surprise_norm,
        productive_or_transfer=productive,
        surprise_refused=refusal,
        discovery_gamma=gamma,
    ):
        return SurpriseDiscoveryOutcome(
            candidate=None,
            verdict=None,
            reason="not_discovery_eligible",
            surprise_norm=surprise_norm,
            discovery_gamma=gamma,
        )

    # Function-local on purpose (A-04): chat/runtime.py's idle_tick imports
    # this MODULE inside the serve process; the serve-banned Tier-2 gate may
    # only load when the discovery path actually runs (off-serving contexts).
    from core.physics.multi_scale_energy import cross_band_discovery_gate

    events: list[tuple[float, float]] = []
    for o in obs:
        norm, o_refusal, _ = _measured_surprise(o.dual)
        if o_refusal is None and math.isfinite(norm):
            events.append((float(o.t), norm))
    verdict = cross_band_discovery_gate(events, now=float(now), tau0=tau0, gamma=gamma)
    if not verdict.eligible:
        return SurpriseDiscoveryOutcome(
            candidate=None,
            verdict=verdict,
            reason=verdict.reason,
            surprise_norm=surprise_norm,
            discovery_gamma=gamma,
        )

    # The runner has already judged eligibility with the effective γ; a stale
    # measurement-time ``discovery_eligible`` flag baked into the dual dict
    # must not veto (or resurrect) that verdict — force downstream
    # recomputation against the same γ both gates used.
    dual_for_emit = dict(current.dual)
    dual_for_emit["discovery_gamma"] = gamma
    dual_for_emit.pop("discovery_eligible", None)
    candidate = emit_surprise_discovery(
        dual_for_emit,
        sink,
        source_turn_trace=current.source_turn_trace,
        discovery_gamma=gamma,
    )
    return SurpriseDiscoveryOutcome(
        candidate=candidate,
        verdict=verdict,
        reason="emitted" if candidate is not None else "candidate_not_constructed",
        surprise_norm=surprise_norm,
        discovery_gamma=gamma,
    )


def contemplate_frontier_reports(
    report_paths: Iterable[str | Path],
    *,
    pack_ids: Iterable[str] = (),
    notes: Iterable[str] = (),
    sink: DiscoveryCandidateSink | None = None,
) -> ContemplationRun:
    """Run ADR-0080 Phase 1 over explicit frontier-compare reports.

    The runner is read-only.  It does not discover files implicitly, does not
    mutate packs, does not write teaching examples, and does not promote any
    finding beyond SPECULATIVE.

    When *sink* is supplied each finding is also emitted as one
    canonical JSONL line via the shared
    :class:`teaching.discovery_sink.DiscoveryCandidateSink` protocol,
    so contemplation findings flow into the same append-only stream
    discovery candidates use.
    """

    paths = tuple(Path(p) for p in report_paths)
    substrate = ContemplationSubstrate.from_report_paths(
        paths,
        pack_ids=tuple(pack_ids),
        notes=tuple(notes),
    )
    findings: list[ContemplationFinding] = []
    for path in paths:
        findings.extend(
            mine_frontier_compare_report(
                path,
                substrate_hash=substrate.substrate_hash,
            )
        )
    _emit_findings(findings, sink)
    config_hash = _config_hash(
        {
            "runner": "contemplate_frontier_reports",
            "report_paths": [str(p) for p in paths],
            "pack_ids": tuple(sorted(set(pack_ids))),
            "notes": tuple(notes),
        }
    )
    return ContemplationRun(
        substrate_hash=substrate.substrate_hash,
        config_hash=config_hash,
        findings=tuple(findings),
    )


def run_contemplation(
    report_paths: Iterable[str | Path] | None = None,
    *,
    pack_ids: Iterable[str] = (),
    notes: Iterable[str] = (),
) -> ContemplationRun:
    """Run ADR-0080 Phase 1 over frontier-compare reports.

    This is the stable operator-facing entry point for Phase 1.  If no
    explicit paths are supplied it reads the checked-in
    ``evals/frontier_compare/results/*.json`` reports in deterministic
    path order.  It never writes packs, teaching examples, proposal logs,
    or discovery sinks.
    """
    if report_paths is None:
        root = Path(__file__).resolve().parents[2]
        paths = tuple(sorted(root.glob("evals/frontier_compare/results/*.json")))
    else:
        paths = tuple(Path(p) for p in report_paths)
    return contemplate_frontier_reports(
        paths,
        pack_ids=pack_ids,
        notes=notes,
        sink=None,
    )


def contemplate_contradiction_reports(
    report_paths: Iterable[str | Path],
    *,
    pack_ids: Iterable[str] = (),
    notes: Iterable[str] = (),
    sink: DiscoveryCandidateSink | None = None,
) -> ContemplationRun:
    """Run ADR-0080 Phase 1 over explicit contradiction-detection reports.

    Mirrors :func:`contemplate_frontier_reports` for the
    ``evals/contradiction_detection`` lane.  Same read-only guarantees,
    same SPECULATIVE-only finding contract, separate runner so the
    config hash records which lane was contemplated.
    """

    paths = tuple(Path(p) for p in report_paths)
    substrate = ContemplationSubstrate.from_report_paths(
        paths,
        pack_ids=tuple(pack_ids),
        notes=tuple(notes),
    )
    findings: list[ContemplationFinding] = []
    for path in paths:
        findings.extend(
            mine_contradiction_detection_report(
                path,
                substrate_hash=substrate.substrate_hash,
            )
        )
    _emit_findings(findings, sink)
    config_hash = _config_hash(
        {
            "runner": "contemplate_contradiction_reports",
            "report_paths": [str(p) for p in paths],
            "pack_ids": tuple(sorted(set(pack_ids))),
            "notes": tuple(notes),
        }
    )
    return ContemplationRun(
        substrate_hash=substrate.substrate_hash,
        config_hash=config_hash,
        findings=tuple(findings),
    )


def write_contemplation_run(run: ContemplationRun, path: str | Path) -> None:
    # Atomic write (temp + os.replace): the always-on life is an indefinite-uptime process
    # where a SIGKILL/crash mid-write is expected, and the idle-pass skip-guard would NEVER
    # repair a torn canonical file. A crash leaves only the orphan .tmp; the canonical path
    # is either absent (re-mined next boot) or complete — never a half-written artifact.
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(run.as_dict(), ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    tmp = target.with_name(f".{target.name}.{os.getpid()}.tmp")
    tmp.write_text(payload, encoding="utf-8")
    os.replace(tmp, target)


__all__ = [
    "SurpriseDiscoveryOutcome",
    "SurpriseObservation",
    "contemplate_contradiction_reports",
    "contemplate_frontier_reports",
    "contemplate_surprise_history",
    "run_contemplation",
    "write_contemplation_run",
]
