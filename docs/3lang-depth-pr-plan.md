# PR Draft + Test Plan: 3-lang (he/grc) Depth PropositionGraph Unification

## Branch
feat/3lang-depth-proposition-graph-unification

## Summary of full commit history on branch (since integration)
- c1e723f1 feat: integrate 3-core-language depth into PropositionGraph spine for bidirectional unification
- 29284fae feat: implement phases 1-5 3-lang depth unification (antiunif root, default depth, contemplation prop, graph helper)
- 0dbcd63d feat: 3lang depth PropGraph unification - phase refinements, wiring, tests + session pickup cleanups/governance
- c57defdb chore: re-pin demo_* SHAs and regenerate CLAIMS.md for intentional 3lang depth spine changes
- 73bca055 chore: refresh canonical demo lane reports after 3lang depth re-pin
- c5dad6ac docs: update plan with 2026-07-08 pickup status + re-pin; archive Jul6 compact
- 3d08e103 chore: archive pickup seeds ...
- 05348e5a refactor: consolidate duplicate depth extraction — graph_planner.get_node_depths now delegates to build_node_depths
- 0e6dada0 chore(cleanup): complete post-pickup hygiene, consolidation, and review fixes for 3lang depth unification

(See `git log --oneline c1e723f1..HEAD` and full `git log` for details.)

## Key files changed (from git diff HEAD~6..HEAD and overall feature)
Core:
- recognition/depth_canonical.py (new pure canonicalize/build/enrich)
- recognition/anti_unifier.py
- core/cognition/pipeline.py (node_depths, graph_anti, attrs, result wiring, propagation)
- chat/pack_resolver.py (DEPTH_PACK_IDS)
- chat/runtime.py (depth reads + explicit attr)
- generate/graph_planner.py (GraphNode depth + get_node_depths delegation)
- generate/contemplation/pass_manager.py
- generate/problem_frame_contracts.py
- teaching/contemplation.py
- core/cognition/result.py (new node_depths, graph_anti_unify fields)
- tests/test_oov_pipeline.py (many depth tests + marker + new result fields test)
- tests/conftest.py (new, for requires_depth_packs fixture)
- pyproject.toml (marker registration)
- plan.md , docs/..., CLAIMS.md, scripts/verify_lane_shas.py, evals/demo_* reports (re-pin + docs)

Full feature touched ~15-20 files; see `git diff --name-only c1e723f1..HEAD`.

## Intentional demo SHA drifts story
- The two demo lanes (demo_composition, public_demo) intentionally drifted because we touched the spine: pipeline oov_geometric_context emission, runtime contemplate depth=, realizer-adjacent paths, GraphNode/PropositionGraph depth, anti-unif.
- All other 7/9 lanes remained stable (including post-CGA substrate).
- Re-pinned with `python scripts/verify_lane_shas.py --update` + `generate_claims.py` + refreshed reports (see commits c57defdb, 73bca055).
- Current: verify_lane_shas reports 9/9 match.
- This is expected/allowed per plan and compact: "only expected demo drifts".

## 3-lang evidence (Hebrew roots, depths, gau)
- "define אמת" produces node_depths e.g. {'p0': {'language': 'he', 'root': 'א-מ-נ', ...}}
- graph_anti_unify: {'matched_roots': [('p0', 'א-מ-נ')], 'topology': ('p0',)}
- anti-unifier canonicalizes to root for he/grc agent slots (nid-keyed)
- contemplate depth= framing findings contain root
- teaching contemplation attaches depth_roots immutably
- Direct tests: test_anti_unifier_root_aware..., test_pipeline_..., test_graph_anti..., test_depth_canonical..., test_contemplate..., test_teaching...
- Captured in scratch + prior logs: root in proposition, ctx, gau, result top-level fields.
- All via real shipped entry points (ChatRuntime + CognitiveTurnPipeline + contemplate fns), not synth.

## Test plan
- New/updated: marker @pytest.mark.requires_depth_packs + autouse fixture that does explicit skip (documenting DEPTH_PACK_IDS) if not resolvable. No silent no-depth branches for marked tests.
- New fields on CognitiveTurnResult proven by committed test + direct runs.
- Broader: verify_lane_shas 9/9; -k broad cognition/oov/anti/... pass.
- Smokes: multiple "define אמת" + teaching contemplate with depth produce consistent roots/matched.
- All changes preserve: frozen/immutable where appropriate, no trace_hash impact, exact recall, versor <1e-6.
- Run after edits: targeted depth tests + full verification plan steps.

## How to verify locally
python3 scripts/verify_lane_shas.py
python -m pytest -q -m "requires_depth_packs" -k "depth_canonical or graph_anti or contemplate_depth" tests/test_oov_pipeline.py
python -m pytest -q --tb=no -k "cognition or oov or anti or construction or depth_canonical or graph_anti" tests/
(plus direct python -c smokes as in plan)

## Deviations / notes
None for this slice. Work followed plan acceptance + checklist.

## References
- plan.md (full phases + pickup + cleanup sections)
- code review notes (MEDIUMs addressed: marker for tests, top-level fields on result, cleaned coupling + enrich)
- AGENTS.md invariants upheld.

This is the draft for PR description + test plan.