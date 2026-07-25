"""teaching/ratification.py — the curriculum ratification ceremony.

The discovery loop is instrumented but not closed. Proposals flow into
``teaching/proposals/`` and a human can read them via ``core proposal-queue
review``, but `review_log.jsonl` explicitly *never* ratifies — it records that
someone looked. Nothing converts a reviewed proposal into a ratified chain, so
the loop terminates in a human decision that produces no artifact.

That gap is the binding constraint. Curriculum serving is OFF because no band
can earn a license from present volume (ADR-0262 §5) — every one of the eleven
live bands is 24×–73× short of the entailed-bucket floor — and the only way
volume grows is one ratified chain at a time.

This module is the code-bound ceremony: **a reviewed decision produces a chain
record, a corpus commit, and a receipt that proves the chain is actually
routable.**

Why the last clause is the whole design
---------------------------------------
``teaching.curriculum_premises._ratified_rows`` DROPS every row it cannot
admit — wrong ``review_status``, wrong domain, empty terms, a term absent from
its declared pack, a connective outside ``CONNECTIVE_FAMILY``. It drops
silently, by ``continue``, because at *serving* time that is right: a curriculum
must never route on a row it cannot license.

At *ratification* time the same silence is a trap. Appending a row that the
loader will drop looks exactly like appending a row that works: the file grows,
the commit lands, the band count does not move, and nobody learns why for weeks.
So this ceremony refuses to call an append a ratification until it has re-read
the curriculum through the real loader and observed the chain arrive. Validation
is a pre-flight courtesy; **admission is the proof**.

Scope, deliberately narrow
--------------------------
Nothing here decides *whether* a proposal is true. It cannot auto-ratify, has no
opinion on content, and requires a human-supplied reviewer identity and rationale
on every call. It converts an already-made decision into the artifacts that
decision implies — which is precisely what was missing.

The two downstream stages of the full ceremony, arena queue entry and ledger
reseal, are intentionally NOT performed here. Both are sealed-practice outputs,
and bridge rule 1 is that nothing outside a practice run may write a ledger
(``core.ratified_ledger``). :func:`ratify_chain` returns the receipt those
stages consume; running them stays an explicit, separate operator step.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from core.capability.domains import (
    DOMAIN_CAPABILITY_CORPORA,
    DOMAIN_CORPORA,
    DOMAIN_PACKS,
)
from teaching.curriculum_premises import CONNECTIVE_FAMILY, load_curriculum

_REPO_ROOT = Path(__file__).resolve().parents[1]

#: Chain ids are ``<domain>-<family>-<NNN>``, zero-padded to three.
_CHAIN_ID_RE = re.compile(r"^(?P<domain>[a-z_]+)-(?P<family>[a-z]+)-(?P<seq>\d{3,})$")

#: The committed row's field order. Chain corpora are reviewed as diffs, so the
#: key order is part of the artifact, not an implementation detail.
_ROW_FIELDS: tuple[str, ...] = (
    "chain_id",
    "domain",
    "operator_family",
    "subject",
    "intent",
    "connective",
    "object",
    "subject_pack_id",
    "object_pack_id",
    "review_status",
    "provenance",
)


class RatificationError(ValueError):
    """A proposed chain cannot be ratified, with the reason stated."""


@dataclass(frozen=True, slots=True)
class ChainRecord:
    """One curriculum edge, in the committed on-disk shape."""

    chain_id: str
    domain: str
    operator_family: str
    subject: str
    intent: str
    connective: str
    object: str
    subject_pack_id: str
    object_pack_id: str
    review_status: str
    provenance: str

    def as_row(self) -> dict[str, Any]:
        return {name: getattr(self, name) for name in _ROW_FIELDS}

    def as_jsonl_line(self) -> str:
        """Byte-compatible with the committed corpora: compact separators,
        insertion order preserved, one trailing newline."""
        return json.dumps(self.as_row(), separators=(",", ":")) + "\n"


@dataclass(frozen=True, slots=True)
class RatificationReceipt:
    """Proof that a ratification actually changed what the engine can route."""

    chain: ChainRecord
    corpus_id: str
    corpus_path: str
    chains_before: int
    chains_after: int
    family_chains_before: int
    family_chains_after: int
    #: Follow-on stages this receipt authorizes but does NOT perform.
    pending_stages: tuple[str, ...] = field(
        default=("arena_queue_entry", "ledger_reseal")
    )

    @property
    def admitted(self) -> bool:
        return self.chains_after == self.chains_before + 1

    def as_dict(self) -> dict[str, Any]:
        return {
            "chain": self.chain.as_row(),
            "corpus_id": self.corpus_id,
            "corpus_path": self.corpus_path,
            "chains_before": self.chains_before,
            "chains_after": self.chains_after,
            "family_chains_before": self.family_chains_before,
            "family_chains_after": self.family_chains_after,
            "admitted": self.admitted,
            "pending_stages": list(self.pending_stages),
        }


def _pack_lemmas(pack_id: str) -> frozenset[str]:
    """Mirror of the loader's pack reader, so validation sees what it sees."""
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
        if isinstance(row, dict):
            lemma = str(row.get("lemma") or "").strip()
            if lemma:
                lemmas.add(lemma)
    return frozenset(lemmas)


def corpus_path_for(domain: str) -> tuple[str, Path]:
    """The single writable chain corpus for *domain*.

    A domain with several corpora (``philosophy_theology``) has no unambiguous
    append target, so the ceremony refuses rather than guessing which file a
    reviewer meant.
    """
    corpora = DOMAIN_CORPORA.get(domain, ())
    if not corpora:
        raise RatificationError(f"unknown domain: {domain!r}")
    writable = [c for c in corpora if c in DOMAIN_CAPABILITY_CORPORA]
    if len(writable) != 1:
        raise RatificationError(
            f"{domain}: expected exactly one writable chain corpus, found "
            f"{writable!r} — name the target explicitly before ratifying"
        )
    corpus_id = writable[0]
    return corpus_id, _REPO_ROOT / DOMAIN_CAPABILITY_CORPORA[corpus_id]


def existing_rows(domain: str) -> list[dict[str, Any]]:
    """Every row in *domain*'s corpus, admitted or not (raw file read)."""
    _, path = corpus_path_for(domain)
    if not path.exists():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def next_chain_id(domain: str, family: str) -> str:
    """The next free ``<domain>-<family>-NNN``, deterministic from the corpus."""
    highest = 0
    for row in existing_rows(domain):
        m = _CHAIN_ID_RE.match(str(row.get("chain_id") or ""))
        if m and m.group("domain") == domain and m.group("family") == family:
            highest = max(highest, int(m.group("seq")))
    return f"{domain}-{family}-{highest + 1:03d}"


def build_chain_record(
    *,
    domain: str,
    subject: str,
    connective: str,
    obj: str,
    reviewer: str,
    rationale: str,
    intent: str = "cause",
    chain_id: str | None = None,
) -> ChainRecord:
    """Construct the record a reviewed decision implies.

    ``reviewer`` and ``rationale`` are required and land in ``provenance``: a
    ratified chain must carry who ratified it and why, or the corpus loses the
    audit lineage that makes it reviewable as a diff.
    """
    reviewer = reviewer.strip()
    rationale = rationale.strip()
    if not reviewer:
        raise RatificationError("ratification requires a reviewer identity")
    if not rationale:
        raise RatificationError("ratification requires a stated rationale")

    family = CONNECTIVE_FAMILY.get(connective.strip())
    if family is None:
        raise RatificationError(
            f"connective {connective!r} is outside CONNECTIVE_FAMILY "
            f"{sorted(CONNECTIVE_FAMILY)} — the loader would drop this row"
        )

    packs = DOMAIN_PACKS.get(domain, ())
    if not packs:
        raise RatificationError(f"domain {domain!r} mounts no packs")

    subject, obj = subject.strip(), obj.strip()
    subject_pack = next((p for p in packs if subject in _pack_lemmas(p)), "")
    object_pack = next((p for p in packs if obj in _pack_lemmas(p)), "")
    if not subject_pack:
        raise RatificationError(
            f"subject {subject!r} is taught by no pack mounted for {domain} "
            f"({list(packs)}) — the loader would drop this row"
        )
    if not object_pack:
        raise RatificationError(
            f"object {obj!r} is taught by no pack mounted for {domain} "
            f"({list(packs)}) — the loader would drop this row"
        )

    return ChainRecord(
        chain_id=chain_id or next_chain_id(domain, family),
        domain=domain,
        operator_family=family,
        subject=subject,
        intent=intent,
        connective=connective.strip(),
        object=obj,
        subject_pack_id=subject_pack,
        object_pack_id=object_pack,
        review_status="reviewed",
        provenance=f"ratification-ceremony:{reviewer}:{rationale}",
    )


def validate_admissible(record: ChainRecord) -> None:
    """Pre-flight: every rule ``_ratified_rows`` drops on, raised LOUDLY.

    Serving is right to drop silently. Ratification is not: an append the
    loader will discard looks identical to one that works.
    """
    if record.review_status != "reviewed":
        raise RatificationError(
            f"review_status={record.review_status!r} — only 'reviewed' is admitted"
        )
    if not record.subject or not record.object:
        raise RatificationError("subject and object must both be non-empty")
    if CONNECTIVE_FAMILY.get(record.connective) is None:
        raise RatificationError(f"connective {record.connective!r} has no family")
    if record.subject_pack_id and record.subject not in _pack_lemmas(record.subject_pack_id):
        raise RatificationError(
            f"subject {record.subject!r} absent from pack {record.subject_pack_id}"
        )
    if record.object_pack_id and record.object not in _pack_lemmas(record.object_pack_id):
        raise RatificationError(
            f"object {record.object!r} absent from pack {record.object_pack_id}"
        )
    for row in existing_rows(record.domain):
        if str(row.get("chain_id")) == record.chain_id:
            raise RatificationError(f"chain_id {record.chain_id} already committed")
        if (
            str(row.get("subject")) == record.subject
            and str(row.get("connective")) == record.connective
            and str(row.get("object")) == record.object
        ):
            raise RatificationError(
                f"duplicate edge: {row.get('chain_id')} already teaches "
                f"{record.subject} {record.connective} {record.object}"
            )


def _count_chains(domain: str, family: str) -> tuple[int, int]:
    load_curriculum.cache_clear()
    curriculum = load_curriculum(domain)
    return len(curriculum.chains), sum(
        1 for c in curriculum.chains if c.family == family
    )


def ratify_chain(record: ChainRecord, *, dry_run: bool = False) -> RatificationReceipt:
    """The ceremony: validate → append → **confirm admission** → receipt.

    Raises :class:`RatificationError` if the appended row does not arrive in the
    reloaded curriculum. On that failure the append is rolled back, because a
    corpus carrying rows the engine silently ignores is worse than one that
    never grew: it makes the volume ledger lie.
    """
    validate_admissible(record)
    corpus_id, path = corpus_path_for(record.domain)
    before_total, before_family = _count_chains(record.domain, record.operator_family)

    if dry_run:
        return RatificationReceipt(
            chain=record,
            corpus_id=corpus_id,
            corpus_path=str(path),
            chains_before=before_total,
            chains_after=before_total + 1,
            family_chains_before=before_family,
            family_chains_after=before_family + 1,
        )

    original = path.read_text(encoding="utf-8") if path.exists() else ""
    if original and not original.endswith("\n"):
        original += "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(original + record.as_jsonl_line(), encoding="utf-8")

    after_total, after_family = _count_chains(record.domain, record.operator_family)
    if after_total != before_total + 1:
        path.write_text(original, encoding="utf-8")
        _count_chains(record.domain, record.operator_family)
        raise RatificationError(
            f"{record.chain_id} was appended but the curriculum loader did not "
            f"admit it ({before_total} -> {after_total}); append rolled back"
        )

    return RatificationReceipt(
        chain=record,
        corpus_id=corpus_id,
        corpus_path=str(path),
        chains_before=before_total,
        chains_after=after_total,
        family_chains_before=before_family,
        family_chains_after=after_family,
    )


__all__ = [
    "ChainRecord",
    "RatificationError",
    "RatificationReceipt",
    "build_chain_record",
    "corpus_path_for",
    "existing_rows",
    "next_chain_id",
    "ratify_chain",
    "validate_admissible",
]
