#!/usr/bin/env python
"""One-off: reset the live discovery-candidate corpus (weekly-audit T11 ruling).

Weekly audit 2026-07-22, Ruling T11 (Shay): the 465 discovery candidates in the
live engine_state store were generated while pre-#100 smoke runs could WRITE the
live store (the module-scope conftest escape #100 sealed). They are provenance-
tainted. They are *inert* — candidates feed only the config-gated proposal /
contemplation loop, never the serving surface — but Absolute Provenance does not
tolerate synthetically-tainted records lingering in a production epistemic corpus.
Ruling: Option (a) — do not asterisk the ledger, clear it. Let idle-tick
discovery repopulate the corpus organically.

WHY THIS SCRIPT AND NOT `rm`:
The store is an ADR-0219 atomic-generation checkpoint. A raw file delete would
itself violate the checkpoint contract (torn state, orphaned pointer). This
routes the reset through the store's own two-phase commit so the wipe is itself
an atomic, auditable committed generation:

  1. begin_generation()            -> allocate the next gen dir
  2. carry forward recognizers + lived session_state + manifest (identity
     lineage + turn_count UNCHANGED — only the candidate ledger is reset)
  3. save_discovery_candidates([]) -> the wipe (empty ledger)
  4. commit_generation(keep=1)     -> atomic `current` pointer swap, then GC
     every older generation so the tainted candidate files are PHYSICALLY gone
     (keep=1 is deliberate: the point of the reset is to eliminate the taint,
     not retain it as a rollback generation).

Idempotent-ish guard: refuses to run unless the live store holds exactly the
EXPECTED_TAINTED count, so it cannot be misfired against a repopulated store.

EXECUTED once, 2026-07-22, against the live store @ 9a428d8466c3:
  pre:  candidates=465 recognizers=0 session_state=absent turn_count=14990
  post: candidates=0   turn_count=14990   remaining_generations=[gen-21703]
  (gen-21701 / gen-21702 GC'd; identity lineage c9e5968a… preserved)
Retained in-tree as the provenance record of the reset.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from engine_state import EngineStateStore

EXPECTED_TAINTED = 465  # the audited pre-#100 candidate count


def main() -> int:
    store_dir = os.environ.get("CORE_ENGINE_STATE_DIR")
    store = EngineStateStore(Path(store_dir)) if store_dir else EngineStateStore()
    print(f"[T11] target store: {store.path}")

    if not store.exists():
        print("[T11] ABORT: no committed checkpoint at target store.", file=sys.stderr)
        return 2

    candidates = store.load_discovery_candidates()
    manifest = store.load_manifest() or {}
    recognizers = store.load_recognizers()
    session_state = store.load_session_state()
    turn_count = int(manifest.get("turn_count", 0))

    print(
        f"[T11] pre-reset: candidates={len(candidates)} recognizers={len(recognizers)} "
        f"session_state={'present' if session_state is not None else 'absent'} "
        f"turn_count={turn_count}"
    )

    if len(candidates) != EXPECTED_TAINTED:
        print(
            f"[T11] ABORT: expected {EXPECTED_TAINTED} tainted candidates, found "
            f"{len(candidates)}. Refusing to run against an unexpected store.",
            file=sys.stderr,
        )
        return 3

    # --- atomic generation-dir reset (ADR-0219) -------------------------------
    gen_num, gen_dir = store.begin_generation()
    gen_store = EngineStateStore(gen_dir)
    gen_store.save_recognizers(recognizers)          # carry forward (faithful)
    gen_store.save_discovery_candidates([])          # THE WIPE
    if session_state is not None:
        gen_store.save_session_state(session_state)  # carry forward lived state
    gen_store.save_manifest(
        turn_count,                                  # UNCHANGED
        engine_identity=manifest.get("engine_identity", ""),
        parent_engine_identity=manifest.get("parent_engine_identity", ""),
        identity_scheme=int(manifest.get("identity_scheme", 2)),
    )
    store.commit_generation(gen_num, keep=1)          # swap + GC every older gen
    print(f"[T11] committed reset generation gen-{gen_num:04d} (keep=1)")

    # --- verify ---------------------------------------------------------------
    verify = EngineStateStore(store.path)
    post_candidates = verify.load_discovery_candidates()
    post_manifest = verify.load_manifest() or {}
    post_turn = int(post_manifest.get("turn_count", -1))
    remaining_gens = sorted(
        p.name for p in store.path.iterdir() if p.is_dir() and p.name.startswith("gen-")
    )

    ok = (
        len(post_candidates) == 0
        and post_turn == turn_count
        and remaining_gens == [f"gen-{gen_num:04d}"]
    )
    print(
        f"[T11] post-reset: candidates={len(post_candidates)} turn_count={post_turn} "
        f"remaining_generations={remaining_gens}"
    )
    if not ok:
        print("[T11] VERIFY FAILED — inspect the store manually.", file=sys.stderr)
        return 4
    print("[T11] OK — candidate corpus cleared; lived state + identity + turn_count intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
