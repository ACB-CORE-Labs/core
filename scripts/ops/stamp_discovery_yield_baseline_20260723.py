#!/usr/bin/env python
"""One-off: stamp the discovery-yield reset epoch (2026-07-23 directive).

Shay ruled the discovery-yield metric scoped as "candidates proposed per
served turn on clean, post-reset traffic" (2026-07-23). The candidate ledger
was already reset to empty by the T11 wipe
(``reset_candidate_corpus_t11_20260722.py``, executed 2026-07-22), but that
reset deliberately left ``turn_count`` unchanged (14990) rather than
fabricating a zero — Absolute Provenance does not permit resetting a scalar
that tracks real historical turns. That means the live manifest has no
marker for WHICH turn_count value corresponds to the clean epoch, so
``teaching.discovery_yield.compute_discovery_yield`` cannot compute a
denominator without one.

This script stamps that marker: ``turn_count_baseline = turn_count`` at the
moment it runs. Every served turn from here on advances ``turn_count`` past
the baseline; the delta is "served turns since reset", and the discovery
ledger's length is "candidates since reset" (already zero'd by T11, so no
double-count).

WHY THIS SCRIPT AND NOT A DIRECT WRITE:
Same rationale as the T11 script — the store is an ADR-0219 atomic-generation
checkpoint. This routes the stamp through the store's own begin/commit cycle
so it is itself an atomic, auditable committed generation, carrying forward
every other field (recognizers, candidates, session_state, identity lineage)
byte-faithfully. Only ``turn_count_baseline`` is new.

Idempotent-ish guard: refuses to run if the live manifest already has a
``turn_count_baseline`` stamped, so it cannot be misfired to silently move
the epoch.

EXECUTED once, 2026-07-23, against the live store:
  pre:  turn_count=14990 turn_count_baseline=absent candidates=0
  post: turn_count=14990 turn_count_baseline=14990   candidates=0
Retained in-tree as the provenance record of the stamp.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from engine_state import EngineStateStore


def main() -> int:
    store_dir = os.environ.get("CORE_ENGINE_STATE_DIR")
    store = EngineStateStore(Path(store_dir)) if store_dir else EngineStateStore()
    print(f"[discovery-yield] target store: {store.path}")

    if not store.exists():
        print(
            "[discovery-yield] ABORT: no committed checkpoint at target store.",
            file=sys.stderr,
        )
        return 2

    candidates = store.load_discovery_candidates()
    manifest = store.load_manifest() or {}
    recognizers = store.load_recognizers()
    session_state = store.load_session_state()
    turn_count = int(manifest.get("turn_count", 0))
    existing_baseline = manifest.get("turn_count_baseline")

    print(
        f"[discovery-yield] pre-stamp: turn_count={turn_count} "
        f"turn_count_baseline={existing_baseline!r} candidates={len(candidates)}"
    )

    if existing_baseline is not None:
        print(
            "[discovery-yield] ABORT: a turn_count_baseline is already stamped "
            f"({existing_baseline}). Refusing to move an existing epoch.",
            file=sys.stderr,
        )
        return 3

    # --- atomic generation-dir stamp (ADR-0219) -------------------------------
    gen_num, gen_dir = store.begin_generation()
    gen_store = EngineStateStore(gen_dir)
    gen_store.save_recognizers(recognizers)              # carry forward (faithful)
    gen_store.save_discovery_candidates(candidates)       # carry forward (faithful)
    if session_state is not None:
        gen_store.save_session_state(session_state)      # carry forward lived state
    gen_store.save_manifest(
        turn_count,                                       # UNCHANGED
        engine_identity=manifest.get("engine_identity", ""),
        parent_engine_identity=manifest.get("parent_engine_identity", ""),
        identity_scheme=int(manifest.get("identity_scheme", 2)),
        turn_count_baseline=turn_count,                    # THE STAMP
    )
    store.commit_generation(gen_num, keep=1)
    print(f"[discovery-yield] committed stamp generation gen-{gen_num:04d} (keep=1)")

    # --- verify ---------------------------------------------------------------
    verify = EngineStateStore(store.path)
    post_manifest = verify.load_manifest() or {}
    post_candidates = verify.load_discovery_candidates()
    post_turn = int(post_manifest.get("turn_count", -1))
    post_baseline = post_manifest.get("turn_count_baseline")
    remaining_gens = sorted(
        p.name for p in store.path.iterdir() if p.is_dir() and p.name.startswith("gen-")
    )

    ok = (
        post_turn == turn_count
        and post_baseline == turn_count
        and len(post_candidates) == len(candidates)
        and remaining_gens == [f"gen-{gen_num:04d}"]
    )
    print(
        f"[discovery-yield] post-stamp: turn_count={post_turn} "
        f"turn_count_baseline={post_baseline!r} candidates={len(post_candidates)} "
        f"remaining_generations={remaining_gens}"
    )
    if not ok:
        print("[discovery-yield] VERIFY FAILED — inspect the store manually.", file=sys.stderr)
        return 4
    print("[discovery-yield] OK — reset epoch stamped; lived state + identity intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
