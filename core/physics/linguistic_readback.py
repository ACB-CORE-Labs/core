"""ADR-0243 §2.3 — Linguistic wave readback (Tier-2, OFF-SERVING).

Closes seam S1 (docs/research/spark-audit-adjudication-2026-07-18.md §4): the
egress route ``readback_eligible`` now flows into geometric token selection
over a vocabulary of Cl(4,1) versors,

    token_t = argmax_T ⟨ψ_steady ψ̃_T⟩_0   (descending resonance spectrum),

followed by the "hearing ourselves think" round-trip: the articulated tokens
are re-ingested through the same sensorium construction boundary
(:func:`~core.physics.cognitive_lifecycle.ingest_context`) and the
phase-locked agreement with the pre-articulation steady state is measured via
the I-04 sanctioned metric :meth:`WaveManifold.phase_correlation`
(ρ = ⟨ψ_A ψ̃_B + ψ_B ψ̃_A⟩_0; agreement = ρ/2). No cosine, no ANN.

Design pins:

* **Decoding, not generating**: a state with no resonant token above the
  caller's ``min_resonance`` raises a typed :class:`ReadbackRefusal` — never a
  fallback string. Sparse vocabulary coverage surfaces as honest refusal.
* **Layering**: vocabulary access is structural (:class:`VocabLike`), because
  the vocab package imports ``core.physics.energy`` — a reverse import here
  would cycle through the ``core.physics`` barrel. The real ``VocabManifold``
  satisfies the protocol as-is (proven in the test suite).
* **Policy is caller-supplied**: ``min_resonance`` / ``max_tokens`` are
  explicit keyword-only inputs — never invented here (same doctrine as the
  egress energy axes).
* **Certificate binding**: readback re-asserts ψ↔certificate digest identity
  (defense-in-depth mirroring :func:`~core.physics.cognitive_lifecycle.serving_cast`);
  a borrowed certificate refuses.

Serve quarantine (A-04): never imported by ``chat/runtime.py``; purity pinned
by ``tests/test_adr_0243_linguistic_readback.py``.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

import numpy as np

from core.physics.cognitive_lifecycle import (
    CognitiveLifecycleError,
    EgressVerdict,
    LifecycleOutcome,
    RelaxationCertificate,
    _as_psi,
    _content_id,
    _psi_digest,
    ingest_context,
)
from core.physics.sensorium_wave_feed import ModalityPacket
from core.physics.wave_manifold import WaveManifold


class ReadbackRefusal(CognitiveLifecycleError):
    """Typed fail-closed readback refusal (§2.3) — never a fallback string."""


class VocabLike(Protocol):
    """Structural view of ``VocabManifold`` (indexed word/versor access only)."""

    def __len__(self) -> int: ...

    def get_versor_at(self, idx: int) -> np.ndarray: ...

    def get_word_at(self, idx: int) -> str: ...


@dataclass(frozen=True, slots=True)
class ReadbackToken:
    """One decoded token: word, vocabulary index, grade-0 resonance score."""

    word: str
    index: int
    resonance: float

    def as_dict(self) -> dict[str, Any]:
        return {"word": self.word, "index": int(self.index), "resonance": float(self.resonance)}


@dataclass(frozen=True, slots=True)
class LinguisticReadback:
    """Ordered resonance-spectrum readback of one certified ψ_steady."""

    tokens: tuple[ReadbackToken, ...]
    psi_digest: str
    certificate_id: str
    min_resonance: float
    max_tokens: int
    vocab_size: int
    readback_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "readback_id",
            "readback-"
            + _content_id(
                {
                    "psi": self.psi_digest,
                    "certificate": self.certificate_id,
                    "tokens": [t.as_dict() for t in self.tokens],
                    "min_resonance": float(self.min_resonance),
                    "max_tokens": int(self.max_tokens),
                    "vocab_size": int(self.vocab_size),
                }
            ),
        )

    @property
    def words(self) -> tuple[str, ...]:
        return tuple(t.word for t in self.tokens)

    def as_dict(self) -> dict[str, Any]:
        return {
            "readback_id": self.readback_id,
            "psi_digest": self.psi_digest,
            "certificate_id": self.certificate_id,
            "tokens": [t.as_dict() for t in self.tokens],
            "min_resonance": float(self.min_resonance),
            "max_tokens": int(self.max_tokens),
            "vocab_size": int(self.vocab_size),
        }


@dataclass(frozen=True, slots=True)
class RoundTripReport:
    """"Hearing ourselves think" — phase-locked agreement of the re-ingested
    articulation with the pre-articulation steady state (agreement = ρ/2)."""

    agreement: float
    phase_correlation: float
    n_tokens: int
    domain_id: str
    psi_steady_digest: str
    psi_roundtrip_digest: str
    report_id: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "report_id",
            "roundtrip-"
            + _content_id(
                {
                    "steady": self.psi_steady_digest,
                    "roundtrip": self.psi_roundtrip_digest,
                    "phase_correlation": float(self.phase_correlation),
                    "domain": self.domain_id,
                    "n_tokens": int(self.n_tokens),
                }
            ),
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "agreement": float(self.agreement),
            "phase_correlation": float(self.phase_correlation),
            "n_tokens": int(self.n_tokens),
            "domain_id": self.domain_id,
            "psi_steady_digest": self.psi_steady_digest,
            "psi_roundtrip_digest": self.psi_roundtrip_digest,
        }


def linguistic_readback(
    psi_steady: np.ndarray,
    certificate: RelaxationCertificate,
    verdict: EgressVerdict,
    vocab: VocabLike,
    *,
    min_resonance: float,
    max_tokens: int,
) -> LinguisticReadback:
    """Decode a certified hot state into its resonant token spectrum.

    Admission chain (each failure is a typed refusal, in this order): policy
    validation → state validation → egress route must be ``readback_eligible``
    → ψ↔certificate digest binding → non-empty vocabulary → at least one token
    with resonance ≥ ``min_resonance``.
    """
    mr = float(min_resonance)
    if not np.isfinite(mr) or mr <= 0.0:
        raise ReadbackRefusal("min_resonance_not_positive", min_resonance=mr)
    mt = int(max_tokens)
    if mt < 1:
        raise ReadbackRefusal("max_tokens_not_positive", max_tokens=mt)

    arr = _as_psi(psi_steady, "ψ_steady", error=ReadbackRefusal)
    if not verdict.admitted or verdict.route != "readback_eligible":
        raise ReadbackRefusal(
            "route_not_readback_eligible", route=verdict.route, verdict_reason=verdict.reason
        )
    if _psi_digest(arr) != certificate.psi_digest:
        raise ReadbackRefusal(
            "certificate_state_mismatch", certificate_id=certificate.certificate_id
        )
    n = len(vocab)
    if n == 0:
        raise ReadbackRefusal("empty_vocabulary")

    # Resonance = ⟨ψ_steady ψ̃_T⟩_0 via the I-04 sanctioned symmetrized
    # correlation (ρ/2; reversion preserves grade-0, so the symmetrization is
    # exact — selection and the round-trip agreement share ONE metric). Note
    # ``cga_inner`` is the UN-reversed ⟨X Y⟩_0 — correct for null-vector word
    # points where reversion is identity, wrong for general versor states.
    m = WaveManifold()
    best_resonance = -np.inf
    scored: list[tuple[float, int]] = []
    for i in range(n):
        versor = np.asarray(vocab.get_versor_at(i), dtype=np.float64)
        score = float(m.phase_correlation(arr, versor)) / 2.0
        if not np.isfinite(score):
            raise ReadbackRefusal("nonfinite_resonance", index=i, word=vocab.get_word_at(i))
        if score > best_resonance:
            best_resonance = score
        if score >= mr:
            scored.append((score, i))
    if not scored:
        raise ReadbackRefusal(
            "no_resonant_token",
            best_resonance=float(best_resonance),
            min_resonance=mr,
            vocab_size=n,
        )
    # Descending resonance; ties break to the lower index (deterministic, the
    # same convention as VocabManifold.nearest's strict `>`).
    scored.sort(key=lambda pair: (-pair[0], pair[1]))
    tokens = tuple(
        ReadbackToken(word=vocab.get_word_at(i), index=i, resonance=s) for s, i in scored[:mt]
    )
    return LinguisticReadback(
        tokens=tokens,
        psi_digest=certificate.psi_digest,
        certificate_id=certificate.certificate_id,
        min_resonance=mr,
        max_tokens=mt,
        vocab_size=n,
    )


def readback_packets(readback: LinguisticReadback, vocab: VocabLike) -> tuple[ModalityPacket, ...]:
    """Lift the decoded tokens back into sensorium packets (one per token)."""
    return tuple(
        ModalityPacket(
            modality_id=f"linguistic:{t.word}",
            coefficients=np.asarray(vocab.get_versor_at(t.index), dtype=np.float64),
        )
        for t in readback.tokens
    )


def hearing_ourselves_think(
    psi_steady: np.ndarray,
    readback: LinguisticReadback,
    vocab: VocabLike,
    *,
    domain_id: str,
    manifold: WaveManifold | None = None,
) -> RoundTripReport:
    """Re-ingest the articulated tokens and measure phase-locked agreement.

    The articulated output is fed back through the SAME ingress construction
    boundary as external input (superpose → normalize; degenerate cancellation
    refuses there), then compared to the pre-articulation steady state with
    the metric-exact phase correlation. ``agreement = ρ/2`` so identical
    unit states score 1.0.
    """
    arr = _as_psi(psi_steady, "ψ_steady", error=ReadbackRefusal)
    if _psi_digest(arr) != readback.psi_digest:
        raise ReadbackRefusal("readback_state_mismatch", readback_id=readback.readback_id)
    roundtrip = ingest_context(readback_packets(readback, vocab), domain_id)
    m = manifold if manifold is not None else WaveManifold()
    rho = float(m.phase_correlation(arr, roundtrip.psi))
    return RoundTripReport(
        agreement=rho / 2.0,
        phase_correlation=rho,
        n_tokens=len(readback.tokens),
        domain_id=roundtrip.domain_id,
        psi_steady_digest=readback.psi_digest,
        psi_roundtrip_digest=_psi_digest(roundtrip.psi),
    )


def articulate_outcome(
    outcome: LifecycleOutcome,
    vocab: VocabLike,
    *,
    min_resonance: float,
    max_tokens: int,
    domain_id: str | None = None,
) -> tuple[LinguisticReadback, RoundTripReport]:
    """Composed seam-S1 stage: readback a lifecycle outcome, then round-trip it.

    The round-trip re-ingests under the outcome's own domain unless the caller
    supplies one — the feedback loop hears itself in the same domain it spoke.
    """
    rb = linguistic_readback(
        outcome.relaxation.psi_steady,
        outcome.relaxation.certificate,
        outcome.verdict,
        vocab,
        min_resonance=min_resonance,
        max_tokens=max_tokens,
    )
    report = hearing_ourselves_think(
        outcome.relaxation.psi_steady,
        rb,
        vocab,
        domain_id=outcome.ingress.domain_id if domain_id is None else str(domain_id),
    )
    return rb, report


__all__ = [
    "LinguisticReadback",
    "ReadbackRefusal",
    "ReadbackToken",
    "RoundTripReport",
    "VocabLike",
    "articulate_outcome",
    "hearing_ourselves_think",
    "linguistic_readback",
    "readback_packets",
]
