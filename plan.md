# 3-Lang Depth PropositionGraph Unification — Phases 1-5 Plan & Verification

Branch: feat/3lang-depth-proposition-graph-unification
Date: 2026-07-06
Status: COMPLETE (systematic implementation + skeptic gap fixes)
Effort: xhigh
Alignment: AGENTS.md (pre-edit traces, immutability via replace/new, exact recall, no ANN/drift repair/normalization outside boundaries, TDD-ish + evidence in scratch, small validation lanes, conventional discipline).

## Phases (as executed)

- **Phase 1: Anti-unifier root-aware canonicalization**
  - Pure `recognition/depth_canonical.py` (canonicalize_token, canonicalize_agent_slot nid+start_idx keyed, no first-proxy, build_node_depths, enrich_assessments_with_depth immutable).
  - derive_recognizer + recognize accept/use `depths`, `agent_node_id`; canonicalize on match path only; lift reports root for he/grc agent in prop (nid-prioritized).
  - root_normalize + graph_anti_unify helpers.
  - Evidence: test_anti_unifier_root_aware_with_depths (id equality, root "א-מ-ן" in proposition value).

- **Phase 2: Default depth enrichment**
  - Pipeline: node_depths ALWAYS emitted in oov_geometric_context (oov + default PropGraph branches); uses build_node_depths.
  - Enrichment via pack_resolver DEPTH_PACK_IDS (he/grc) + immutable GraphNode rebuild in comprehension path.
  - _current/_last attrs wired.

- **Phase 3: Contemplation / construction propagation**
  - runtime.py: contemplate(..., depth=...) from _last_node_depths (multiple sites).
  - teaching/contemplation.py: real (immutable replace on proposed_chain with depth_roots/langs); forward depth to recursion.
  - generate/contemplation/pass_manager.py: depth param, depth_framing_findings + Finding("depth", root=...) ; _solve_and_verify real (no synth).
  - generate/problem_frame_contracts.py: assess_contracts(depth) -> enrich_assessments_with_depth (immutable).
  - Evidence: test_contemplate_depth_framing, test_teaching_contemplate_depth_real_propagation (attach verified).

- **Phase 4: Graph-level anti-unif**
  - graph_anti_unify(topology, depths) -> matched_roots etc.
  - Wired into pipeline oov_geometric_context (always when depths).
  - PropositionGraph.get_node_depths() added (meaningful touch on graph_planner).
  - build_node_depths used centrally.

- **Phase 5: Real tests / logs / proof**
  - Non-empty 3lang ctx/root from actual `pl.run("define אמת")` (nid 'p0', root 'א-מ-נ', morphology).
  - Full transcripts via -v -s + scripts/capture_spine_evidence.sh -> /tmp/grok-scratch/spine_tests.log .
  - Asserts: id match, root in prop/ctx/gau/matched, pipeline attrs set, teaching attach, graph.get_node_depths.
  - Construction + oov tests green.
  - Scratch evidence captured; verif steps executed.

## Verification (executed)
- Pre-edit: traced imports/callers (grep on pipeline, anti, depth_canonical, contemplate, GraphNode, recognize etc); no cycles; callers limited to tests/runtime/pipeline/generate; evals use but no breakage.
- Targeted runs: 6/6 key spine tests PASS (anti, pipeline 3lang, graph_anti, depth_canonical, contemplate framing, teaching depth).
- Broader: construction_affordances, proposal_seam, percent, oov, recognition_phase1, contemplation tests: all PASS.
- Live smoke: python run("define אמת") -> ctx has non-empty depths + root.
- Capture script re-ran; logs contain:
  - "derive id1: ... id2: ..." (match)
  - "root form in proposition agent: א-מ-ן"
  - "pipeline oov node_depths for he query: {'p0': {'language': 'he', 'root': 'א-מ-נ', ...}}"
  - "ctx graph_anti_unify: {'matched_roots': [('p0', 'א-מ-נ')], ...}"
  - "pipeline _last_node_depths set: ..."
  - "teaching depth real attach: ('א-מ-ן',)"
- Invariants: No field ops touched (versor untouched); immutable (replace, new GraphNode/ tuples/ dicts); exact (no cosine etc); depth only at construction/enrich boundaries (pack resolver, graph build, canonical at recog derive time).
- No drift repair, no hidden unitize, no synth in production paths (tests use real resolver data).

## Deviations / Notes
- None from plan or AGENTS.md. Minor: duplicate small depth lift in graph_planner.get_node_depths (avoids top-level import cycle with depth_canonical's optional GraphNode); non-fatal try in wiring.
- recognize in pipeline early (before full graph) uses prior-turn depths (chained via _last); current-turn recog+depth for 3lang OOV shapes covered by direct + post-graph ctx (acceptable for spine; depths originate from resolver on subject at comprehend time).
- plan.md created at root per prior workflow.

## Files changed (this completion)
- recognition/anti_unifier.py (nid-prioritized root in prop)
- recognition/depth_canonical.py (cleanup)
- core/cognition/pipeline.py (build use, sets, graph_anti wire, init attrs, last chaining)
- generate/graph_planner.py (get_node_depths)
- teaching/contemplation.py (real attach + propagate)
- tests/test_oov_pipeline.py (tightened asserts + new teaching test + graph helper assert)
- scripts/capture_spine_evidence.sh (expanded keys)
- plan.md (new, checklist+evidence)

## Next (if any)
- If recognition_grounded_graph + live 3lang taught shapes need same-turn root recog before graph, consider early subject resolve for depths pre-recog (future, not required for current ACs).
- Rebase/merge per git workflow after review.
- (retired) No longer create formal HANDOFF files. Use session-break-summary-<DATETIME>.md on pauses per AGENTS.md.
- SHA drifts (demo_composition + public_demo only) are expected/intentional from spine changes. Re-pin with `--update` + `generate_claims.py` when current active implementation slice is complete (or pre-PR). Continue R&D; monitor via `verify_lane_shas.py` after output-affecting edits. Fresh trace + core cognition lanes remain the key stability signals.
- /compact executed: See docs/COMPACT_STRATEGY.md (process) and docs/session-compacts/2026-07-06-compact.md (current distilled state for new thread). Use the 2026-07-06 compact to seed fresh session. Continue R&D there until slice + re-pin ready, then PR.

All skeptic gaps addressed (pipeline recog/ctx/attrs, runtime depth pass, teaching placeholder->real, anti nid, depth_canonical no-proxy, tests real+asserts+logs, pass_manager real, graph integration, plan/verif updated).

## Post-Implementation Verification (broad lane)
- 2026-07-06 background run: `pytest -q -k "oov or anti_unifier or proposition or realizer" tests/`
  - **524 passed, 1 skipped, 11388 deselected, 22 warnings, exit 0, ~199s**
  - Keyword filter directly exercises the changed spine: OOV/depth emission, anti-unifier root canonicalization, PropositionGraph nodes + depths, realizer consumption.
  - Warnings: only the pre-existing "engine identity continuity break" (runtime load, checkpoint vs current pack rev; unrelated to depth/3lang work). No new test warnings or failures from our edits.
  - Archived: /tmp/grok-scratch/broad_verif_oov_anti_prop_realizer.log + broad_verif_summary.txt
  - Follow-up spine subset (anti_unifier_root_aware | pipeline_node_depths | teaching_contemplate | depth_canonical): 4/4 + full 31 passed re-runs.
- This + prior targeted capture (spine_tests.log with explicit root/nid/ctx/graph_anti/attach prints) + construction tests constitute strong proof for Phases 1-5.
- No deviations introduced; invariants held.

## 2026-07-08 Pickup & Slice Close
- Worktree on feat/3lang-depth-proposition-graph-unification (local refinements committed post 29284fae).
- forgejo/main (incl. CGA Substrate #929 + construction_affordances tighten #930 + forgejo governance) is direct ancestor — no rebase needed; depth work already integrated atop latest substrate.
- Pickup actions executed:
  - Followed NEW_SESSION_PROMPT: state confirmed, spine tests (6/6), broader construction/oov/anti/contemplate (545 passed).
  - Live smoke: node_depths in oov_geometric_context for "define אמת" (he root visible).
  - verify_lane_shas: 7/9 (demos intentionally drifted from spine touch; others stable post-CGA).
  - Re-pinned demo_* SHAs + regenerated CLAIMS.md (test_claims_md_is_current green).
  - Refreshed canonical demo reports.
- Current top: 73bca055 (re-pin + reports).
- Slice feels complete for phases 1-5 + refinements + integration on current main. Depth travels: pack resolver → pipeline (node_depths + graph_anti + attrs) → recognize (canonical) → runtime contemplate → teaching/pass_manager/contracts (framing + enrich) → graph.
- Next if more R&D: extend root-aware to additional construction/derivation call sites for 3lang frames; add he/grc construction exemplars; wire depth into more geometric proposal paths; prep PR (push to forgejo remote, use tea pulls).
- Invariants re-confirmed: immutability (replace/new), exact, no drift repair, fresh trace stable, core lanes green.
- Pickup seeds (NEW_SESSION_PROMPT.txt, docs/session-compacts/2026-07-06-compact.md, COMPACT_STRATEGY.md) can now be archived per strategy.
