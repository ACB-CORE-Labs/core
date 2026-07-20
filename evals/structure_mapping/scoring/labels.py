"""Isolated gold structure labels for scoring — never mapper input.

Source of S1 membership for holdout_dev/v1: the five cases that the serving
reader already solves via ``compare_multiplicative`` + total (documented in
``docs/research/compare-multiplicative-increment-plan-2026-07-18.md`` §2).
These ids are scoring-only; the symbolic mapper never reads this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Final, Mapping

# Absolute family membership for Increment 1 scoring on holdout_dev/v1.
# Labels are NOT derived at map time from parse kind alone in the scorer's
# primary list — they are the documented S1 organ cohort. Additional cases
# may be labeled S1 in extended JSONL if human-reviewed later.
S1_HOLDOUT_CASE_IDS: Final[frozenset[str]] = frozenset(
    {
        # Organ cohort (serving reader already solves)
        "gsm8k-holdout-dev-v1-0101",
        "gsm8k-holdout-dev-v1-0108",
        "gsm8k-holdout-dev-v1-0268",
        "gsm8k-holdout-dev-v1-0411",
        "gsm8k-holdout-dev-v1-0453",
        # Increment 2 coverage gain via SM-owned pure-S1 extract (organ misses)
        "gsm8k-holdout-dev-v1-0148",
        "gsm8k-holdout-dev-v1-0228",
        "gsm8k-holdout-dev-v1-0234",
        "gsm8k-holdout-dev-v1-0441",
    }
)

_LABELS_PATH: Final[Path] = Path(__file__).resolve().parent / "holdout_dev_v1_labels.jsonl"


def load_structure_labels(path: Path | None = None) -> dict[str, str]:
    """Load ``case_id → structure_label`` from the isolated scoring file."""
    p = path if path is not None else _LABELS_PATH
    out: dict[str, str] = {}
    text = p.read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        row = json.loads(line)
        cid = row["case_id"]
        lab = row["label"]
        if not isinstance(cid, str) or not isinstance(lab, str):
            raise ValueError(f"malformed label row: {row!r}")
        out[cid] = lab
    return out


def score_label(
    case_id: str,
    predicted_s1: bool,
    labels: Mapping[str, str] | None = None,
) -> dict[str, object]:
    """Score a binary S1-map decision against gold. Scoring-only API."""
    lab_map = labels if labels is not None else load_structure_labels()
    gold = lab_map.get(case_id)
    if gold is None:
        return {
            "case_id": case_id,
            "gold": None,
            "predicted_s1": predicted_s1,
            "tp": False,
            "fp": False,
            "fn": False,
            "tn": False,
            "note": "unlabeled",
        }
    is_s1 = gold == "S1"
    return {
        "case_id": case_id,
        "gold": gold,
        "predicted_s1": predicted_s1,
        "tp": bool(predicted_s1 and is_s1),
        "fp": bool(predicted_s1 and not is_s1),
        "fn": bool((not predicted_s1) and is_s1),
        "tn": bool((not predicted_s1) and not is_s1),
        "note": None,
    }
