"""Curriculum → premise compiler (generalization arc Phase 2, ADR-0262).

The load-bearing half of the curriculum-entailment gold contract
(docs/plans/generalization-arc-2026-07-24.md §4): an exam question supplies
only the QUERY; its premises are compiled here, from the RATIFIED domain-chain
corpus of the subject being examined, and from nowhere else. Gold is therefore
a function of *(curriculum, question)* — never of case-local hidden text, and
never of what a model happens to know about the world. That is the
decoding-not-generating line in mechanical form: a fact absent from the
curriculum is UNKNOWN, however true it is.

**Ratification** (§4.3) is the same predicate the capability reporter applies
to these corpora, restated here rather than imported: a chain counts iff its
``review_status`` is ``reviewed`` AND both its subject and object lemmas are
resident in the packs the chain itself declares. The duplication is
deliberate and narrow — a serving path must not take a dependency on the
reporting subsystem, and this module must be able to state its own admission
rule in the terms the serve-time refusals name.

**Compilation is family-scoped.** A question about a `causes` relation is
answered from the `causes` chains. Restricting cannot lose an entailment (a
chain's family is fixed by its connective, so an edge that would answer the
question is always in the question's own family), and it keeps the compiled
premise set inside the reader's honesty caps as corpora grow.

The compiler emits plain English sentences — ``"force causes acceleration"`` —
because the argument bands are the decider (ADR-0256…0261). There is no
subject-specific decision code anywhere in this path: physics differs from
philosophy only in which rows load.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from core.capability.domains import (
    DOMAIN_CAPABILITY_CORPORA,
    DOMAIN_CORPORA,
    DOMAIN_PACKS,
)

_REPO_ROOT = Path(__file__).resolve().parents[1]

#: Connective → relation family. The closed set this path serves; a chain
#: whose connective is absent is not compiled (and cannot be questioned about
#: either, so the two ends stay consistent).
#:
#: The CONNECTIVE is the sole family authority here, deliberately — not the
#: row's own ``operator_family`` field. An exam question carries a relation
#: word and nothing else, so a family derived from anything the question does
#: not carry would let premise compilation and question routing disagree, and
#: a taught edge could then be missing from the premises compiled to decide
#: it — a wrong answer built from a correct curriculum. Two corpus rows
#: currently declare a family their connective does not imply
#: (``physics-causal-008`` and one systems_software row, both
#: ``requires``/``causal``); under this rule they are read as modal, which is
#: what their connective says.
CONNECTIVE_FAMILY: dict[str, str] = {
    "causes": "causal",
    "reveals": "causal",
    "grounds": "causal",
    "requires": "modal",
    "enables": "modal",
    "precedes": "sequence",
    "opposes": "contrast",
    "supports": "evidential",
}

#: Relation families, in a stable order (the band-key axis — ADR-0262 §4).
FAMILIES: tuple[str, ...] = ("causal", "modal", "sequence", "contrast", "evidential")


@dataclass(frozen=True, slots=True)
class CurriculumChain:
    """One ratified curriculum edge, as the exam path reads it."""

    chain_id: str
    subject: str
    connective: str
    obj: str
    family: str

    @property
    def sentence(self) -> str:
        """The English premise this chain compiles to. The connective is
        already a third-person-singular verb form, so the sentence lands in
        the verb-predicate grammar (ADR-0260) exactly as written."""
        return f"{self.subject} {self.connective} {self.obj}"


@dataclass(frozen=True, slots=True)
class Curriculum:
    """The ratified curriculum of one subject — the ONLY premise source."""

    domain: str
    chains: tuple[CurriculumChain, ...]
    vocabulary: frozenset[str]

    def family(self, family: str) -> tuple[CurriculumChain, ...]:
        return tuple(c for c in self.chains if c.family == family)

    def chain_by_id(self, chain_id: str) -> CurriculumChain | None:
        return next((c for c in self.chains if c.chain_id == chain_id), None)


@lru_cache(maxsize=None)
def _pack_lemmas(pack_id: str) -> frozenset[str]:
    path = _REPO_ROOT / "packs" / "data" / pack_id / "lexicon.jsonl"
    if not path.exists():
        return frozenset()
    lemmas: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        lemma = row.get("lemma") if isinstance(row, dict) else None
        if isinstance(lemma, str):
            lemmas.add(lemma)
    return frozenset(lemmas)


def _domain_vocabulary(domain: str) -> frozenset[str]:
    """Every lemma the subject's mounted packs teach — the vocabulary boundary
    an exam question may not cross (§4.6 ``untaught_vocabulary``)."""
    lemmas: set[str] = set()
    for pack_id in DOMAIN_PACKS.get(domain, ()):
        lemmas |= _pack_lemmas(pack_id)
    return frozenset(lemmas)


def _ratified_rows(corpus_id: str, domain: str) -> list[dict]:
    rel = DOMAIN_CAPABILITY_CORPORA.get(corpus_id)
    if rel is None:
        return []
    path = _REPO_ROOT / rel
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(row, dict):
            continue
        if row.get("review_status") != "reviewed":
            continue
        if str(row.get("domain") or "").strip() != domain:
            continue
        subject = str(row.get("subject") or "").strip()
        obj = str(row.get("object") or "").strip()
        subject_pack = str(row.get("subject_pack_id") or "").strip()
        object_pack = str(row.get("object_pack_id") or "").strip()
        if not subject or not obj:
            continue
        if subject_pack and subject not in _pack_lemmas(subject_pack):
            continue
        if object_pack and obj not in _pack_lemmas(object_pack):
            continue
        rows.append(row)
    return rows


@lru_cache(maxsize=None)
def load_curriculum(domain: str) -> Curriculum:
    """The ratified curriculum for *domain* — deterministic, corpus order.

    Unratified rows, rows whose terms have left their packs, and rows whose
    connective is outside :data:`CONNECTIVE_FAMILY` are DROPPED here, at the
    admission boundary, so that everything downstream can treat every chain it
    sees as licensed premise material. A dropped chain is not a silent
    weakening of an argument the way a dropped *premise* would be (ADR-0261
    §5.1): the exam path pins chain ids and fails loudly when a pinned chain
    did not survive admission — see ``resolve_pinned``.
    """
    chains: list[CurriculumChain] = []
    for corpus_id in DOMAIN_CORPORA.get(domain, ()):
        for row in _ratified_rows(corpus_id, domain):
            connective = str(row.get("connective") or "").strip()
            family = CONNECTIVE_FAMILY.get(connective)
            if family is None:
                continue
            chains.append(
                CurriculumChain(
                    chain_id=str(row.get("chain_id") or ""),
                    subject=str(row.get("subject") or "").strip(),
                    connective=connective,
                    obj=str(row.get("object") or "").strip(),
                    family=family,
                )
            )
    return Curriculum(
        domain=domain,
        chains=tuple(chains),
        vocabulary=_domain_vocabulary(domain),
    )


def compile_premises(
    curriculum: Curriculum, family: str
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """``(premise_sentences, chain_ids)`` for *family*, in corpus order.

    Deterministic: the same curriculum and family always compile to the same
    sentences in the same order, so a lane report over them is SHA-pinnable.
    """
    chains = curriculum.family(family)
    return tuple(c.sentence for c in chains), tuple(c.chain_id for c in chains)


class UnratifiedChain(LookupError):
    """A lane case pinned a chain that is absent or did not survive admission."""


def resolve_pinned(curriculum: Curriculum, chain_ids: tuple[str, ...]) -> tuple[CurriculumChain, ...]:
    """The pinned chains, or raise (§4.3).

    A case that pins a chain the curriculum no longer ratifies MUST fail — not
    quietly answer from whatever else is present. This is the provenance guard
    that keeps "gold is a function of the curriculum" true over time: if the
    curriculum changes under a case, the case breaks loudly.
    """
    resolved: list[CurriculumChain] = []
    for chain_id in chain_ids:
        chain = curriculum.chain_by_id(chain_id)
        if chain is None:
            raise UnratifiedChain(
                f"{curriculum.domain}: pinned chain {chain_id!r} is absent or unratified"
            )
        resolved.append(chain)
    return tuple(resolved)


__all__ = [
    "CONNECTIVE_FAMILY",
    "FAMILIES",
    "Curriculum",
    "CurriculumChain",
    "UnratifiedChain",
    "compile_premises",
    "load_curriculum",
    "resolve_pinned",
]
