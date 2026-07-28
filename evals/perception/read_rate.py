"""The read-rate instrument — what fraction of real English the reader actually reads.

Perception Arc Phase 0 (G-21's open ask, G-24's headline number, the keel's baseline).

The 2026-07-28 diagnosis measured, ad hoc, that ``generate.meaning_graph.reader``
reads **23 of 1,798** sentences of `holdout_dev/v1` (1.28%), with 93.16% failing as
``no_template_match`` — upstream of vocabulary, upstream of every flag. That number
is the binding constraint every substrate experiment independently hit, and it is
the metric the keel's perception layer (K4) is accountable for moving in chunks.

An ad-hoc measurement is testimony. This module is the instrument: deterministic,
committed, and pinned by ``tests/test_read_rate_floor.py`` as a floor ratchet — the
recorded counts may only be updated deliberately, and only upward for ``read``.

Deliberately narrow: the LOGIC reader at sentence granularity. The math reader's
decision rate (5/500 holdout cases, G-21) is recorded where it was measured
(`docs/analysis/relational-operator-ablation-dossier-2026-07-19.md`, split table)
and will get its own lane if it ever moves; folding a slow full-solve sweep into
this fast lane would couple two instruments that fail differently.
"""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from generate.meaning_graph.reader import Refusal, _split_sentences, comprehend

_ROOT = Path(__file__).resolve().parents[2]
CORPUS = _ROOT / "evals" / "gsm8k_math" / "holdout_dev" / "v1" / "cases.jsonl"


@dataclass(frozen=True)
class ReadRateReport:
    corpus: str
    problems: int
    sentences: int
    read: int
    refusals: tuple[tuple[str, int], ...]  # (reason, count), descending

    @property
    def read_rate(self) -> float:
        return self.read / self.sentences if self.sentences else 0.0

    def as_dict(self) -> dict:
        return {
            "corpus": self.corpus,
            "problems": self.problems,
            "sentences": self.sentences,
            "read": self.read,
            "read_rate": round(self.read_rate, 6),
            "refusals": dict(self.refusals),
        }


def measure(corpus_path: Path = CORPUS) -> ReadRateReport:
    """Run the logic reader over every sentence of the corpus. Deterministic."""
    problems = [json.loads(line) for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    reasons: Counter[str] = Counter()
    read = 0
    sentences = 0
    for case in problems:
        for sentence, *_rest in _split_sentences(case["problem"]):
            sentence = sentence.strip()
            if not sentence:
                continue
            sentences += 1
            try:
                result = comprehend(sentence)
            except Exception as exc:  # a crashing reader is a finding, not a skip
                reasons[f"EXCEPTION:{type(exc).__name__}"] += 1
                continue
            if isinstance(result, Refusal):
                reasons[result.reason] += 1
            elif result is None:
                reasons["returned_none"] += 1
            else:
                read += 1
    return ReadRateReport(
        corpus=str(corpus_path.relative_to(_ROOT)),
        problems=len(problems),
        sentences=sentences,
        read=read,
        refusals=tuple(sorted(reasons.items(), key=lambda kv: (-kv[1], kv[0]))),
    )


def main() -> int:
    report = measure()
    print(json.dumps(report.as_dict(), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
