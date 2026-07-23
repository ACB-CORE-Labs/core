# Weekly Audit — 2026-07-22 — cleanup-week integrity pass, stragglers, and TODO

**Scope**: main from PR #76 (`compare_multiplicative` increment plan) through
PR #97 (`logos` bulk live morph authority) — the week that landed the reader-arc
recalibration (ADR-0251), the paradigm consolidation (ADR-0252), the Master
Blueprint collision freeze (ADR-0253 + mapping), and Master Convergence
Stages 1–4 (#95) plus #96/#97. 134 files, +17,028/−770.

**Auditor**: Claude (session audit), read-only verification against
`forgejo/main` @ `f94dbd40` plus doctrine-authorized hygiene cleanup.

---

## 1. Verified sound (no action)

- **Smoke suite green on landed main**: 180 passed, 0 failed (2:17),
  `uv run core test --suite smoke -q` @ `f94dbd40`.
- **`uv lock --check`**: lock file consistent with `pyproject` (217 packages).
- **ADR status registry vs. mapping doc**: ADR-0240 Proposed; 0241–0250 and
  0252–0253 Accepted; 0251 partial (§§1–4 ratified) — matches
  `MASTER-BLUEPRINT-2026-07-20-ADR-MAPPING.md` registry table exactly.
- **Superseded-in-place annotations** (ADR-0164, ADR-0174, ADR-0243 sketch
  pins, ADR-0244 dual-mode excision rewrite) are present and accurate against
  code: no `_axis_projection` / `_mean_frame_coherence` / scalar-L2 remnants in
  `core/`; `tests/test_stage2_physics_hardening.py` pins the removed symbols
  as absent.
- **ADR-0252 §9 retirement record**: all five formulations physically moved to
  `docs/paradigm-archive/` with git history preserved (`--follow` verified);
  old paths gone from `docs/analysis|handoffs|implementation`.
- **Gate defaults match doc claims**: `RuntimeConfig.identity_wave_gate = False`
  (`core/config.py:301`) — consistent with ADR-0244's "live refusal remains
  flag-gated" and the standing non-authorization.
- **No new TODO/FIXME/HACK markers** entered `*.py` across the whole week's
  diff; no merge-conflict markers anywhere in tracked `*.py`/`*.md`.
- **New `scripts/measure_trackb_*.py`** are referenced by the Track-B research
  dossiers (not orphans).
- **`epistemic-taxonomy-ownership-stage3.md`** placement in `docs/adr/` is
  deliberate (binding ownership note, not an ADR renumber) — now indexed from
  `docs/adr/README.md` (fixed in this PR).

## 2. Small issues fixed in this PR

1. **ADR-0132 dangling parent pointer** — pointed at
   `docs/implementation/semantic-symbolic-binding-graph-proposal.md`, which
   ADR-0252 §9 moved to `docs/paradigm-archive/`. Pointer updated with the
   retirement annotation.
2. **Stale near-duplicate of ratified ADR-0243** —
   `docs/research/ADR-0243-…md` still carried `Status: Proposed` and had
   drifted from the canonical body by a few annotation lines. Replaced with a
   tombstone pointing at the canonical Accepted ADR; the one annotation unique
   to the copy (`modality_transition_sandwich` ingress note) is preserved in
   the tombstone.
3. **`docs/adr/README.md`** — added an index entry for the binding
   non-ADR ownership note (`epistemic-taxonomy-ownership-stage3.md`), which was
   referenced nowhere.

## 3. Hygiene cleanup performed (session, no PR needed)

Per the merge-then-cleanup doctrine (branch AND worktree deleted immediately
after merge) — all four verified clean and fully merged before removal:

- Worktrees removed: `core-postmerge-pr87-integrity-audit` (#88),
  `core-relational-operator-ablation` (#87), `core-wt-trackb` (#85),
  `core-wt-trackb2` (#86); matching local branches deleted.
- Forgejo remote branches deleted (0 commits ahead of main):
  `feat/trackb-symbolic-sme-s1`, `feat/trackb-symbolic-sme-s2s4`,
  `fix/a2k-fraction-decrease-scale-range`.
- Local `main` fast-forwarded to `forgejo/main` (`f94dbd40`).

## 4. TODO — items needing a ruling or deeper investigation

- [ ] **T1 (governance): register convergence-era runtime invariants — or rule
  that tests suffice.** `docs/specs/runtime_contracts.md` cites no ADR newer
  than the 0230s. The week landed several fail-closed runtime invariants that
  are currently enforced only by code + architecture tests: ADR-0244 wave-only
  identity (`MissingWaveStateError`), ADR-0253 dual-pack serve boundary
  (`tests/test_pack_draft_serve_boundary.py`), #96 fail-closed linguistic
  governance phases, #97 bulk live morph authority. `AGENTS.md` invariants
  (INV-…) also saw zero changes all week. Decide: add contract entries /
  INV lines, or record explicitly that the arch-test layer is the SoT here.
- [ ] **T2 (runtime state): stale `engine_state/` checkpoint.** Smoke emits
  `RuntimeWarning: engine_state checkpoint was written at revision '4b9dbe72…'
  but the current revision is 'f94dbd40…'` (`chat/runtime.py:807`). Given
  continuity doctrine, clearing is NOT something to do casually — decide
  whether to re-baseline the checkpoint on current main or keep it and accept
  the warning.
- [ ] **T3 (worktree): Antigravity worktree
  `~/.gemini/antigravity/worktrees/core/implement-substrate-linguistic-anchors`**
  — branch tip is ON main history (0 ahead) but the tree has 4 uncommitted
  files. Likely superseded by PR #96 (linguistic governance). Reconcile the
  4 files, then remove worktree + branch.
- [ ] **T4 (worktrees): two stale detached demo worktrees** —
  `/private/tmp/builder-ii-flagship-demo/demo-worktree` and the
  `grok-goal-…/recipe3_demo_loop/demo-worktree` under `$TMPDIR`, both clean,
  detached @ `18c578d9`. Remove via `git worktree remove` once confirmed no
  running demo serves from them (left alone in this pass for that reason).
- [ ] **T5 (branch garden): stale branch sweep.** ~50 local branches (many
  `audit-*`, `backup/*`, `chore/*` from May–June) and ~210 `origin/*` branches
  on the GitHub mirror. Needs a batched merged-vs-unmerged triage; separate
  authorization before any mass deletion.
- [ ] **T6 (active experiments): ADR-0252 §5 structure-mapping worktrees** —
  `core-wt-sme` (`rnd/structure-mapping-experiment`, 1 ahead) and
  `core-wt-sme2` (`rnd/sme-experiment-v2`, 1 ahead + 2 untracked scripts:
  `extract_sme_corpus.py`, `test_single_pair.py`). Active and authorized; track
  them to a dossier/PR so the untracked scripts don't rot outside history.
- [ ] **T7 (ADR annotation): `modality_transition_sandwich` sentence** — the
  annotation preserved in the ADR-0243 research tombstone exists nowhere in the
  canonical ADR. If it is load-bearing for the SD-B pin record, fold it into
  the canonical ADR-0243 annotation under a separate small ruling.
- [ ] **T8 (declared debt, consolidation): fold the week's declared residuals
  into next-arc planning.** #97's honest accounting
  (`docs/analysis/logos-bulk-live-authority-residual-2026-07-20.md`) lists six
  open residuals (parallel `generate/linguistic_pipeline` cue tables, lexicon
  breadth, legacy math/meaning_graph IR outside the morph seam, holonomy crown
  not LIVE, disconnected pack frames, single `plural_abstain` rule type). These
  are declared debt, not stragglers — but they now live only in an analysis
  doc; pull them into whatever planning artifact governs the next Logos/IR arc
  so they don't silently age out.
- [ ] **T9 (docs, minor): historical docs referencing pre-archive paths** —
  `docs/workbench/capability-mastery-implementation-plan.md:33,85-86` and
  `docs/briefs/parallel-2026-05-23/L2-opus2-binding-graph-phase1.md` cite the
  retired paradigm docs at their old `docs/analysis|implementation/` paths.
  Both are point-in-time records; either leave as history (default) or annotate
  with the archive location. No governance weight either way.
