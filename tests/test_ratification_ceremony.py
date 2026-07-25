"""The curriculum ratification ceremony — a decision must produce artifacts.

The discovery loop was instrumented but not closed: proposals reached a human,
`review_log.jsonl` recorded that they looked, and nothing converted a reviewed
decision into a ratified chain. These pin the ceremony that closes it, and in
particular the property the whole design exists for — **an append is not a
ratification until the curriculum loader is observed to admit it.**
"""

from __future__ import annotations

import pytest

from core.capability.domains import DOMAIN_CORPORA, DOMAIN_PACKS
from teaching.curriculum_premises import CONNECTIVE_FAMILY, load_curriculum
from teaching.ratification import (
    ChainRecord,
    RatificationError,
    build_chain_record,
    corpus_path_for,
    existing_rows,
    next_chain_id,
    ratify_chain,
    validate_admissible,
)


REVIEWER = "test-operator"
RATIONALE = "pinned by tests/test_ratification_ceremony.py"


@pytest.fixture
def physics_corpus_restored():
    """Any test that really writes must leave the committed corpus untouched."""
    _, path = corpus_path_for("physics")
    original = path.read_text(encoding="utf-8")
    try:
        yield path
    finally:
        path.write_text(original, encoding="utf-8")
        load_curriculum.cache_clear()


# ---------------------------------------------------------------------------
# Construction — a decision's provenance is not optional
# ---------------------------------------------------------------------------


def test_reviewer_and_rationale_are_required() -> None:
    """A ratified chain carries who ratified it and why, or the corpus loses
    the audit lineage that makes it reviewable as a diff."""
    for reviewer, rationale in ((" ", RATIONALE), (REVIEWER, "  ")):
        with pytest.raises(RatificationError, match="requires a"):
            build_chain_record(
                domain="physics",
                subject="force",
                connective="causes",
                obj="energy",
                reviewer=reviewer,
                rationale=rationale,
            )


def test_chain_id_is_deterministic_and_next_in_sequence() -> None:
    assert next_chain_id("physics", "causal") == next_chain_id("physics", "causal")
    seq = int(next_chain_id("physics", "causal").rsplit("-", 1)[1])
    committed = [
        int(str(r["chain_id"]).rsplit("-", 1)[1])
        for r in existing_rows("physics")
        if str(r.get("chain_id", "")).startswith("physics-causal-")
    ]
    assert seq == max(committed) + 1


def test_family_is_derived_from_the_connective_not_supplied() -> None:
    record = build_chain_record(
        domain="physics",
        subject="force",
        connective="requires",
        obj="energy",
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    assert record.operator_family == CONNECTIVE_FAMILY["requires"] == "modal"


def test_row_is_byte_compatible_with_the_committed_corpus() -> None:
    """Chain corpora are reviewed as diffs, so key order and separators are
    part of the artifact. A reformatting ratification would show every row as
    changed and make the real change unreviewable."""
    committed = corpus_path_for("physics")[1].read_text(encoding="utf-8").splitlines()[0]
    row = existing_rows("physics")[0]
    rebuilt = ChainRecord(**{k: row[k] for k in ChainRecord.__slots__}).as_jsonl_line()
    assert rebuilt.rstrip("\n") == committed


# ---------------------------------------------------------------------------
# Validation — every rule the loader drops on, raised loudly
# ---------------------------------------------------------------------------


def test_connective_outside_the_family_table_is_refused() -> None:
    with pytest.raises(RatificationError, match="outside CONNECTIVE_FAMILY"):
        build_chain_record(
            domain="physics",
            subject="force",
            connective="influences",  # not in CONNECTIVE_FAMILY
            obj="energy",
            reviewer=REVIEWER,
            rationale=RATIONALE,
        )


def test_untaught_term_is_refused_with_the_loader_s_reason() -> None:
    """The anti-recall boundary, enforced at ratification: a chain about a term
    no mounted pack teaches cannot route, so committing it only inflates the
    file."""
    with pytest.raises(RatificationError, match="taught by no pack"):
        build_chain_record(
            domain="physics",
            subject="force",
            connective="causes",
            obj="photosynthesis",  # biology; no physics pack teaches it
            reviewer=REVIEWER,
            rationale=RATIONALE,
        )


def test_duplicate_edge_is_refused() -> None:
    """Re-teaching an edge inflates the volume count without adding coverage —
    exactly the repetition-padding ADR-0262 §5 rejected as dishonest."""
    row = existing_rows("physics")[0]
    dup = build_chain_record(
        domain="physics",
        subject=row["subject"],
        connective=row["connective"],
        obj=row["object"],
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    with pytest.raises(RatificationError, match="duplicate edge"):
        validate_admissible(dup)


def test_unreviewed_status_is_refused() -> None:
    row = existing_rows("physics")[0]
    record = ChainRecord(**{**{k: row[k] for k in ChainRecord.__slots__},
                            "chain_id": "physics-causal-900",
                            "subject": "entropy", "object": "temperature",
                            "review_status": "pending"})
    with pytest.raises(RatificationError, match="only 'reviewed' is admitted"):
        validate_admissible(record)


def test_every_served_domain_has_exactly_one_writable_corpus() -> None:
    """philosophy_theology lists three corpora in ``DOMAIN_CORPORA``, but only
    one is writable (present in ``DOMAIN_CAPABILITY_CORPORA``), so the append
    target is unambiguous today. This pins that it stays that way: the day a
    second writable corpus is registered for a domain, ratification has a real
    choice to make and must not make it silently."""
    for domain in DOMAIN_CORPORA:
        if domain not in DOMAIN_PACKS:
            continue
        corpus_id, path = corpus_path_for(domain)
        assert corpus_id, domain
        assert path.name.endswith(".jsonl"), domain


def test_ambiguous_append_target_refuses_rather_than_guessing(monkeypatch) -> None:
    """The guard itself, exercised against an injected second writable corpus.
    Picking one silently would scatter a subject's curriculum across files."""
    import teaching.ratification as mod

    monkeypatch.setitem(
        mod.DOMAIN_CORPORA, "physics", ("physics_chains_v1", "physics_chains_v2")
    )
    monkeypatch.setitem(
        mod.DOMAIN_CAPABILITY_CORPORA,
        "physics_chains_v2",
        "teaching/domain_chains/physics_chains_v2.jsonl",
    )
    with pytest.raises(RatificationError, match="exactly one writable"):
        corpus_path_for("physics")


# ---------------------------------------------------------------------------
# The ceremony itself — admission is the proof, not the append
# ---------------------------------------------------------------------------


def test_dry_run_reports_the_delta_without_touching_the_corpus() -> None:
    before = corpus_path_for("physics")[1].read_text(encoding="utf-8")
    record = build_chain_record(
        domain="physics",
        subject="entropy",
        connective="causes",
        obj="temperature",
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    receipt = ratify_chain(record, dry_run=True)
    assert receipt.admitted
    assert receipt.chains_after == receipt.chains_before + 1
    assert corpus_path_for("physics")[1].read_text(encoding="utf-8") == before


def test_ratification_moves_the_band_the_licence_is_scored_on(
    physics_corpus_restored,
) -> None:
    """End to end on the real corpus. The family count is the number that
    matters: licences are scored per (subject x family), so a ratification that
    moves the total but not the family has not moved a band."""
    record = build_chain_record(
        domain="physics",
        subject="entropy",
        connective="causes",
        obj="temperature",
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    receipt = ratify_chain(record)

    assert receipt.admitted
    assert receipt.family_chains_after == receipt.family_chains_before + 1
    assert receipt.chain.chain_id in {
        c.chain_id for c in load_curriculum("physics").chains
    }, "the ceremony reported success but the chain is not routable"


def test_receipt_names_the_stages_it_did_not_perform(
    physics_corpus_restored,
) -> None:
    """Bridge rule 1: nothing outside a sealed practice run writes a ledger.
    The ceremony hands those stages to the operator rather than doing them."""
    record = build_chain_record(
        domain="physics",
        subject="entropy",
        connective="causes",
        obj="temperature",
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    receipt = ratify_chain(record, dry_run=True)
    assert receipt.pending_stages == ("arena_queue_entry", "ledger_reseal")


def test_append_that_the_loader_would_drop_is_rolled_back(
    physics_corpus_restored, monkeypatch
) -> None:
    """**The property the design exists for.**

    ``_ratified_rows`` drops unadmissible rows silently, which is correct at
    serving time and a trap at ratification time: the file grows, the commit
    lands, the band count does not move, and nobody learns why. Simulated here
    by making the loader refuse to see the new row.
    """
    import teaching.ratification as mod

    before = physics_corpus_restored.read_text(encoding="utf-8")
    record = build_chain_record(
        domain="physics",
        subject="entropy",
        connective="causes",
        obj="temperature",
        reviewer=REVIEWER,
        rationale=RATIONALE,
    )
    calls = {"n": 0}

    def stuck_counts(domain: str, family: str) -> tuple[int, int]:
        calls["n"] += 1
        return (16, 8)  # never moves, whatever we append

    monkeypatch.setattr(mod, "_count_chains", stuck_counts)

    with pytest.raises(RatificationError, match="did not admit it"):
        ratify_chain(record)

    assert physics_corpus_restored.read_text(encoding="utf-8") == before, (
        "a non-admitted append must not survive — a corpus carrying rows the "
        "engine ignores makes the volume ledger lie"
    )
