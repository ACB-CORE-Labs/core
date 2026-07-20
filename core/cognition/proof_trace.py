"""Minimal structured proof trace for proof-preserving articulation.

Ordered sequence: semantic atoms → field operators → closure result.
No free-text-only steps as authoritative proof content.

Citation rules (firewall):
  * Valid citation keys are ONLY step_id and ``kind:symbol``.
  * Raw payload values are never citation keys (prevents whitelist bypass
    via incidental values like ``"2"`` or ``"0.000000e+00"``).
  * Payload content is available separately for content certification.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Sequence


class ProofStepKind(str, Enum):
    ATOM = "atom"
    OPERATOR = "operator"
    CLOSURE = "closure"
    REFUSAL = "refusal"


_TOKEN_SPLIT = re.compile(r"[^a-z0-9_.:-]+", re.IGNORECASE)


@dataclass(frozen=True, slots=True)
class ProofStep:
    """One ordered, typed proof step."""

    step_id: str
    kind: ProofStepKind
    symbol: str
    """Machine id: entity id, operator class, closure predicate, etc."""
    payload: tuple[tuple[str, str], ...] = ()
    """Stringly-serialised structured payload pairs (key, value) only."""
    parent_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.step_id:
            raise ValueError("ProofStep.step_id must be non-empty")
        if not isinstance(self.kind, ProofStepKind):
            raise TypeError("ProofStep.kind must be a ProofStepKind")
        if not self.symbol:
            raise ValueError("ProofStep.symbol must be non-empty")
        for key, value in self.payload:
            if not isinstance(key, str) or not isinstance(value, str):
                raise TypeError("ProofStep.payload must be tuple[tuple[str, str], ...]")

    def as_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "kind": self.kind.value,
            "symbol": self.symbol,
            "payload": [[k, v] for k, v in self.payload],
            "parent_ids": list(self.parent_ids),
        }

    def citation_keys(self) -> frozenset[str]:
        """Keys an articulation claim may *cite* as trace_refs.

        Only step_id and kind:symbol — never bare payload values.
        """
        return frozenset(
            {
                self.step_id,
                f"{self.kind.value}:{self.symbol}",
            }
        )

    # Back-compat alias used by older call sites / tests.
    def claim_keys(self) -> frozenset[str]:
        return self.citation_keys()

    def certified_content_tokens(self) -> frozenset[str]:
        """Tokens that may appear in claim *text* when this step is cited.

        Includes step_id parts, symbol parts, and payload keys/values —
        but only as content vocabulary, not as citation keys.
        """
        tokens: set[str] = set()
        for raw in (self.step_id, self.symbol, self.kind.value):
            tokens |= _tokenize(raw)
        for k, v in self.payload:
            tokens |= _tokenize(k)
            tokens |= _tokenize(v)
        return frozenset(tokens)


def _tokenize(text: str) -> set[str]:
    out: set[str] = set()
    for part in _TOKEN_SPLIT.split(text.lower()):
        if part:
            out.add(part)
            # Also keep dotted/colon segments whole when present.
    # Whole lowercased string if multi-token machine id
    if text and " " not in text:
        out.add(text.lower())
    return out


@dataclass(frozen=True, slots=True)
class ProofTrace:
    """Ordered proof trace. Empty only for non-authoritative turns."""

    steps: tuple[ProofStep, ...] = ()
    closed: bool = False
    closure_step_id: str | None = None

    def __post_init__(self) -> None:
        if self.closed and not self.steps:
            raise ValueError("closed ProofTrace must contain at least one step")
        if self.closed:
            if self.closure_step_id is None:
                raise ValueError("closed ProofTrace requires closure_step_id")
            ids = {s.step_id for s in self.steps}
            if self.closure_step_id not in ids:
                raise ValueError("closure_step_id must reference a step in the trace")
            closure = next(s for s in self.steps if s.step_id == self.closure_step_id)
            if closure.kind is not ProofStepKind.CLOSURE:
                raise ValueError("closure_step_id must point at a CLOSURE step")

    def as_dict(self) -> dict[str, Any]:
        return {
            "closed": self.closed,
            "closure_step_id": self.closure_step_id,
            "steps": [s.as_dict() for s in self.steps],
        }

    def all_citation_keys(self) -> frozenset[str]:
        keys: set[str] = set()
        for step in self.steps:
            keys |= set(step.citation_keys())
        return frozenset(keys)

    def all_claim_keys(self) -> frozenset[str]:
        """Alias for citation keys (not payload-value whitelist)."""
        return self.all_citation_keys()

    def steps_for_refs(self, refs: Sequence[str]) -> tuple[ProofStep, ...]:
        """Resolve citation refs to steps; unknown refs yield empty match list."""
        by_key: dict[str, list[ProofStep]] = {}
        for step in self.steps:
            for key in step.citation_keys():
                by_key.setdefault(key, []).append(step)
        found: list[ProofStep] = []
        seen: set[str] = set()
        for ref in refs:
            for step in by_key.get(ref, ()):
                if step.step_id not in seen:
                    seen.add(step.step_id)
                    found.append(step)
        return tuple(found)

    def certified_content_for_refs(self, refs: Sequence[str]) -> frozenset[str]:
        tokens: set[str] = set()
        for step in self.steps_for_refs(refs):
            tokens |= set(step.certified_content_tokens())
        return frozenset(tokens)

    def extend(self, extra: Sequence[ProofStep]) -> "ProofTrace":
        return ProofTrace(
            steps=self.steps + tuple(extra),
            closed=self.closed,
            closure_step_id=self.closure_step_id,
        )


def build_closed_trace(
    atoms: Iterable[tuple[str, str, Sequence[tuple[str, str]]]],
    operators: Iterable[tuple[str, str, Sequence[tuple[str, str]], Sequence[str]]],
    *,
    closure_symbol: str = "versor_and_goldtether_closed",
    closure_payload: Sequence[tuple[str, str]] = (),
) -> ProofTrace:
    """Build a closed proof from atom and operator descriptors.

    atoms: (step_id, symbol, payload)
    operators: (step_id, symbol, payload, parent_ids)
    """
    steps: list[ProofStep] = []
    for step_id, symbol, payload in atoms:
        steps.append(
            ProofStep(
                step_id=step_id,
                kind=ProofStepKind.ATOM,
                symbol=symbol,
                payload=tuple((str(k), str(v)) for k, v in payload),
            )
        )
    for step_id, symbol, payload, parents in operators:
        steps.append(
            ProofStep(
                step_id=step_id,
                kind=ProofStepKind.OPERATOR,
                symbol=symbol,
                payload=tuple((str(k), str(v)) for k, v in payload),
                parent_ids=tuple(parents),
            )
        )
    closure_id = "closure:0"
    parent_ids = tuple(s.step_id for s in steps if s.kind is ProofStepKind.OPERATOR)
    if not parent_ids:
        parent_ids = tuple(s.step_id for s in steps)
    steps.append(
        ProofStep(
            step_id=closure_id,
            kind=ProofStepKind.CLOSURE,
            symbol=closure_symbol,
            payload=tuple((str(k), str(v)) for k, v in closure_payload),
            parent_ids=parent_ids,
        )
    )
    return ProofTrace(steps=tuple(steps), closed=True, closure_step_id=closure_id)


def build_refusal_trace(
    *,
    reason: str,
    violated_condition: str,
) -> ProofTrace:
    """Trace that certifies only the refusal itself (no answer claims)."""
    step = ProofStep(
        step_id="refusal:0",
        kind=ProofStepKind.REFUSAL,
        symbol="coherence_refusal",
        payload=(
            ("reason", reason),
            ("violated_condition", violated_condition),
        ),
    )
    return ProofTrace(steps=(step,), closed=False, closure_step_id=None)


def geometry_contract_trace(
    *,
    versor_condition: float,
    goldtether_residual: float,
    closed: bool,
) -> ProofTrace:
    """Proof fragment from live shadow-gate scalars."""
    payload = (
        ("versor_condition", f"{versor_condition:.6e}"),
        ("goldtether_residual", f"{goldtether_residual:.6e}"),
    )
    if closed:
        return build_closed_trace(
            atoms=(
                (
                    "atom:field",
                    "field_state",
                    payload,
                ),
            ),
            operators=(
                (
                    "op:geometry_gate",
                    "shadow_coherence_gate",
                    payload,
                    ("atom:field",),
                ),
            ),
            closure_symbol="geometric_contract_closed",
            closure_payload=payload,
        )
    return build_refusal_trace(
        reason="geometric_contract_open",
        violated_condition="versor_condition_and_goldtether",
    )


__all__ = [
    "ProofStepKind",
    "ProofStep",
    "ProofTrace",
    "build_closed_trace",
    "build_refusal_trace",
    "geometry_contract_trace",
]
