# /compact Strategy for Long Sessions / New Threads

## Purpose
This strategy compacts the essential context, state, decisions, invariants, and next steps so a new AI session (or human handoff) can start with minimal token/context bloat while retaining full fidelity for continued R&D, verification, and eventual PR.

It replaces the retired heavy HANDOFF process with a lightweight, pragmatic approach aligned with current AGENTS.md (session-break-summary on pauses) and CORE principles (evidence-governed, inspectable, replayable, no unnecessary ceremony).

## When to Trigger /compact
- Session context approaching limits (e.g., "this session is getting a little long").
- Before/after major phases or natural breakpoints in active development.
- When preparing to switch threads, create PR, or resume after pause.
- Proactively after significant changes that affect outputs (e.g., spine modifications impacting demo lanes/SHAs).

Do **not** use for trivial edits. Use for feature work like the current 3-lang depth PropGraph unification.

## /compact Process (Step-by-Step)
1. **Gather Fresh State** (run these commands in terminal):
   - `git branch --show-current`
   - `git log --oneline -5`
   - `git status --porcelain`
   - `python3 scripts/verify_lane_shas.py` (note any drifts + remediation)
   - Relevant test suites: `python -m pytest -q --tb=no -k "cognition or oov or anti_unifier or depth_canonical"` (or full `core test --suite cognition -q`)
   - Quick 3-lang trace stability spot-check (fresh instances):
     ```
     python3 -c '
     from chat.runtime import ChatRuntime
     from core.cognition.pipeline import CognitiveTurnPipeline
     for i in range(2):
         rt = ChatRuntime()
         pl = CognitiveTurnPipeline(runtime=rt)
         r = pl.run("define אמת", max_tokens=3)
         print(f"fresh{i}: trace_hash[:12]={(getattr(r, \"trace_hash\", \"\") or \"\")[:12]}")
     '
     ```
   - Key artifacts: `cat plan.md | head -100` (or full relevant sections), recent scratch logs if any.

2. **Distill to Compact Artifact**:
   - Create or update a time-stamped compact: `docs/session-compacts/YYYY-MM-DD-compact.md` (or root-level for urgency).
   - Use the template below.
   - Include:
     - Branch + top commit(s).
     - Status of active work (e.g., Phases 1-5 complete for current slice).
     - Verification snapshot (cognition green? core lanes matching? drifts?).
     - What was intentionally changed and why (e.g., depth on PropGraph for 3-lang).
     - Things to watch / potential question marks (e.g., demo SHA drifts - intentional, re-pin later).
     - Open R&D items / shaping guidance (what to focus next, how to validate).
     - Must-read files + quick-start commands for new session.
     - Invariants to re-confirm (trace stability on fresh 3-lang cases, no regression in core lanes, versor etc. untouched).
   - Also update `plan.md` if it is the living plan (append a "Compact Checkpoint" section).
   - Optionally create `session-break-summary-YYYY-MM-DD-HHMM.md` at root if this is a pause point (per AGENTS.md lightweight rule).

3. **Validate the Compact**:
   - Run the state-gathering commands again and cross-check against the new compact.
   - Confirm no critical untracked work or dirty files that would surprise a new session.
   - Ensure the compact is self-contained enough that a new thread can answer "what next?" without the full history.

4. **Hand off / Begin New Thread**:
   - In new session prompt: Paste or reference the compact file + "Read docs/session-compacts/YYYY-MM-DD-compact.md, plan.md, AGENTS.md. Current branch is X. Run the quick-start commands."
   - Delete or archive the compact once the new thread has internalized and made progress (mirrors "delete the file once picked back up").
   - If on pause: Create the session-break-summary as well.

5. **Post-Compact Hygiene**:
   - Commit the compact (and any summary) with message like "docs: compact session state for new thread [feature]".
   - Continue R&D.
   - Re-run full verify + targeted suites after next significant change.
   - When ready for PR: Re-pin drifted SHAs if intentional (`--update` + `generate_claims.py`), ensure all core + feature tests green, update plan with test plan, then PR.

## Template for YYYY-MM-DD-compact.md (or session-break-summary)
```
# Compact Summary - [Feature/Topic] - YYYY-MM-DD

**Branch:** feat/...
**Top commit:** <sha> <msg>
**Working tree:** <clean/dirty summary + key files>

## Status of Active Work
- [ ] Phases X-Y complete for this slice (details in plan.md)
- Verification snapshot:
  - Cognition suite: 122 passed...
  - verify_lane_shas.py: 7/9 match (drifts only in demo_*: intentional)
  - Fresh trace stability (3-lang OOV): True
- Key achievements: <bullet list distilled from plan>

## What Changed & Why (Guiding R&D)
- Intentional spine updates for 3-lang depth on PropGraph (root canonicalization, depth propagation, graph helpers).
- This legitimately affects demo outputs → SHA drifts in public/demo lanes.
- Core invariants holding: trace hashes stable on fresh instances, no regression in cognition/math lanes.

## Things to Watch / Question Marks (from verification system)
- demo_composition + public_demo SHA drifts (expected; re-pin with --update when feature slice complete or pre-PR).
- After any output-affecting change: re-run `python3 scripts/verify_lane_shas.py` and targeted spine tests.
- Ensure fresh-instance trace_hash stability on "define אמת" and similar 3-lang cases.
- No drift repair or hidden normalization introduced.

## Quick-Start Commands for New Session / Thread
1. `git status --porcelain -b`
2. `python3 scripts/verify_lane_shas.py`
3. `python -m pytest -q --tb=no -k "oov or anti_unifier or depth or cognition"`
4. (Optional) 3-lang trace spot-check (fresh instances) as above.
5. Read: AGENTS.md (top section on session continuity), plan.md (full + Post-Implementation section), this compact.

## Next R&D / Shaping Guidance
- Continue active implementation of [specific next part of unification].
- Shape efforts around: keeping core lanes green, making depth/root effects visible/traceable in 3-lang paths, documenting intentional demo changes.
- When ready: Re-pin SHAs + regenerate claims; prepare PR with test plan.

## Key Artifacts
- plan.md (living plan + evidence)
- docs/session-compacts/ (this + priors)
- /tmp/grok-scratch/ (logs from capture scripts)
- tests/test_oov_pipeline.py + construction tests (feature coverage)

## Invariants to Re-Confirm
- Fresh trace_hash stability on equivalent 3-lang inputs.
- Cognition suite + key spine tests pass.
- Only expected demo lanes drift (no new unexpected drifts).
- No changes outside allowed normalization boundaries; immutability preserved.

(End of compact - delete or archive once progress is made in new thread.)
```

## Decision Guidance (PR vs. Continue + Compact)
- **Active R&D phase** (current state): Compact now (create the summary + this strategy doc). Continue on the branch. Use the compact to seed a new thread if context pressure builds. Do **not** PR yet — finish the current slice of the unification, gather more evidence if needed, then prepare PR (including re-pin).
- **Near PR / feature slice complete**: Compact + re-pin + update claims in one go. Then PR with the compact as part of the narrative or appendix.
- **Very long single thread without natural break**: Compact + create session-break-summary, start fresh thread with the compact pre-loaded. Continue until PR.
- Never compact in a way that loses evidence (always leave plan.md + scratch logs + test artifacts intact).

This strategy keeps us lightweight, evidence-governed, and aligned with "plan before execute", "smallest relevant validation lane", and "update plan/checklist".

Update this file if the process evolves.
