"""Run the ADR-0246 slice-0 mismatch diagnostic and emit the evidence packet.

Usage:  uv run python -m evals.adr_0246_mismatch_diagnostic [out.json]

Collects live benign + paraphrase versor traces from a fresh empty-vault
``ChatRuntime`` (instrumented instance-locally; serving code untouched), runs
the full decomposition over all four trace classes, and writes the JSON packet.
Diagnostic-only: no gate, threshold, axis, or flag changes.
"""

from __future__ import annotations

import json
import sys

from evals.adr_0246_mismatch_diagnostic import (
    PARAPHRASE_PROBE_SEQUENCE,
    build_evidence_packet,
    collect_live_versors,
)
from evals.adr_0244_gamma_calibration import LIVE_PROBE_SEQUENCE


def main() -> int:
    out_path = sys.argv[1] if len(sys.argv) > 1 else None
    benign = collect_live_versors(LIVE_PROBE_SEQUENCE)
    paraphrase = collect_live_versors(PARAPHRASE_PROBE_SEQUENCE)
    packet = build_evidence_packet(benign, paraphrase)
    text = json.dumps(packet, indent=2, sort_keys=True)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"evidence packet written to {out_path}")
    summary = {
        "verdict": packet["verdict"],
        "semantic_coupling": packet["semantic_coupling"],
        "path_accumulation": {
            k: v
            for k, v in packet["path_accumulation"].items()
            if k != "raw_path_d_stab_curve"
        },
        "precision_transport": packet["precision_transport"],
        "mechanism_counts": packet["mechanism_counts"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
