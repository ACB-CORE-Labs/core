# Antigravity worktree salvage — substrate linguistic anchors (2026-07-22)

**Context**: Weekly-audit **T3 ruling** (2026-07-22). The Antigravity worktree
`~/.gemini/antigravity/worktrees/core/implement-substrate-linguistic-anchors`
(branch tip `1ccef491`, on main history, no unique commits) held 4 uncommitted
files. They are **not** PR #96 material — they were a distinct, un-ADR'd
experiment. Per the ruling the unique utility is preserved here and the
worktree/branch are scrapped. Related handoff:
`docs/handoffs/legacy/HANDOFF-antigravity-2026-07-01.md`; anchor-lens substrate:
ADR-0073.

## What it attempted

Bias the reader→Hamiltonian compiler physics by anchor lenses: thread an
`anchor_lens_id` through `CandidateRelation` / `BoundRelation` /
`compile_quadratic_well` / `compile_propositional` / `compile_affine_relation`,
map relation types to Hebrew/Greek anchor packs by hand, and deepen the
Hamiltonian well by `0.1·curvature` (resp. `0.1·penalty`) on the blade hashed
from the lens atom.

## Why it was scrapped, not landed

1. **Fail-open**: both compiler hooks swallow all errors
   (`except Exception: pass`) — violates the typed fail-closed doctrine
   (INV-34 posture; "no opaque fallback cognition").
2. **Unratified serving-physics mutation**: the compile paths are load-bearing
   for the wrong=0 compiler lanes; a magic `0.1` well-deepening on a
   hash-derived blade is a serving change with no ADR, no measurement, no gate.
3. **Hand map, not measurement**: the `_RELATION_TO_ANCHOR` table is exactly
   the cue-table pattern the paradigm consolidation (ADR-0252) retired.

If the idea returns, it enters as an ADR + off-serving evidence under the
ADR-0252 §5 discipline (separable-with-margin, attribute-invariant,
structure-sensitive), not as inline compiler edits.

## The preserved hand map (for whoever picks this up)

`transfer→he_dabar_v1, consumption→he_chayyim_v1, transaction→he_tzedek_v1,
labor_rate→he_chesed_v1, travel→he_chokmah_v1, unary_delta→he_chayyim_v1,
decrease_to_fraction→he_tzedek_v1, container_packing→grc_synesis_v1,
partition→grc_synesis_v1, comparison→grc_logos_v1, percent_of→grc_synesis_v1,
subgroup_partition→grc_synesis_v1`

## Full recovered diff

```diff
diff --git a/core/physics/cognitive_lifecycle.py b/core/physics/cognitive_lifecycle.py
index 60cc47ad..501dc819 100644
--- a/core/physics/cognitive_lifecycle.py
+++ b/core/physics/cognitive_lifecycle.py
@@ -302,7 +302,7 @@ class ProblemHamiltonian:
         )
 
 
-def compile_quadratic_well(target_psi: np.ndarray, *, curvature: float = 1.0) -> ProblemHamiltonian:
+def compile_quadratic_well(target_psi: np.ndarray, *, curvature: float = 1.0, anchor_lens_id: str | None = None) -> ProblemHamiltonian:
     """H = curvature·(Id − ψ₀ψ₀ᵀ): ground space span(ψ₀) at energy 0, gap = curvature."""
     target = _as_psi(target_psi, "target_psi", error=HamiltonianCompileError)
     c = float(curvature)
@@ -312,10 +312,23 @@ def compile_quadratic_well(target_psi: np.ndarray, *, curvature: float = 1.0) ->
     if norm_err > _UNIT_TOL:
         raise HamiltonianCompileError("target_not_unit", norm_residual=norm_err)
     matrix = c * (np.eye(N_COMPONENTS, dtype=np.float64) - np.outer(target, target))
+    
+    if anchor_lens_id:
+        try:
+            from packs.anchor_lens.loader import load_anchor_lens
+            from packs.compiler import _hash_to_blade
+            lens = load_anchor_lens(anchor_lens_id, require_ratified=False)
+            if lens.atom:
+                # Topologically constrain by deepening the well along the anchored semantic geometry
+                blade_idx = _hash_to_blade(lens.atom, "anchor")
+                matrix[blade_idx, blade_idx] -= (c * 0.1)
+        except Exception:
+            pass
+
     return ProblemHamiltonian(
         matrix=matrix,
         domain="quadratic_well",
-        metadata={"curvature": c, "target_digest": _psi_digest(target)},
+        metadata={"curvature": c, "target_digest": _psi_digest(target), "anchor_lens_id": str(anchor_lens_id) if anchor_lens_id else ""},
     )
 
 
@@ -379,7 +392,7 @@ def _falsification_counts(problem: PropositionalProblem) -> tuple[int, ...]:
     return tuple(counts)
 
 
-def compile_propositional(problem: PropositionalProblem, *, penalty: float = 1.0) -> ProblemHamiltonian:
+def compile_propositional(problem: PropositionalProblem, *, penalty: float = 1.0, anchor_lens_id: str | None = None) -> ProblemHamiltonian:
     """Diagonal penalty Hamiltonian: diag[component(a)] = penalty · #clauses falsified by a.
 
     Out-of-domain components (blades using vectors beyond the atom set) get
@@ -394,10 +407,23 @@ def compile_propositional(problem: PropositionalProblem, *, penalty: float = 1.0
     diag = np.full(N_COMPONENTS, p * float(len(problem.clauses) + 1), dtype=np.float64)
     for mask, count in enumerate(counts):
         diag[_SUBSET_COMPONENT[mask]] = p * float(count)
+        
+    if anchor_lens_id:
+        try:
+            from packs.anchor_lens.loader import load_anchor_lens
+            from packs.compiler import _hash_to_blade
+            lens = load_anchor_lens(anchor_lens_id, require_ratified=False)
+            if lens.atom:
+                # Topologically constrain by deepening the well along the anchored semantic geometry
+                blade_idx = _hash_to_blade(lens.atom, "anchor")
+                diag[blade_idx] -= (p * 0.1)
+        except Exception:
+            pass
+
     return ProblemHamiltonian(
         matrix=np.diag(diag),
         domain="propositional",
-        metadata={"problem_id": problem.problem_id, "penalty": p, "n_atoms": problem.n_atoms},
+        metadata={"problem_id": problem.problem_id, "penalty": p, "n_atoms": problem.n_atoms, "anchor_lens_id": str(anchor_lens_id) if anchor_lens_id else ""},
     )
 
 
diff --git a/core/physics/relation_compiler.py b/core/physics/relation_compiler.py
index fa03b4f7..a9d56a98 100644
--- a/core/physics/relation_compiler.py
+++ b/core/physics/relation_compiler.py
@@ -66,6 +66,7 @@ def compile_affine_relation(
     scale: float,
     offset: float,
     curvature: float = 1.0,
+    anchor_lens_id: str | None = None,
 ) -> ProblemHamiltonian:
     """``output = scale·input + offset`` as a quadratic-well constraint Hamiltonian.
 
@@ -88,4 +89,4 @@ def compile_affine_relation(
     if norm < _MIN_TARGET_NORM:
         raise HamiltonianCompileError("degenerate_affine_target", norm=norm)
     unit_target = (psi_target / norm).astype(np.float64)
-    return compile_quadratic_well(unit_target, curvature=curvature)
+    return compile_quadratic_well(unit_target, curvature=curvature, anchor_lens_id=anchor_lens_id)
diff --git a/generate/kernel_facts.py b/generate/kernel_facts.py
index 385795c5..93d6cab4 100644
--- a/generate/kernel_facts.py
+++ b/generate/kernel_facts.py
@@ -205,6 +205,7 @@ class CandidateRelation:
     roles: tuple[RelationRole, ...] = ()
     provenance: KernelProvenance | None = None
     hazards: tuple[KernelHazard, ...] = ()
+    anchor_lens_id: str | None = None
 
 
 # ---------------------------------------------------------------------------
@@ -254,6 +255,7 @@ class BoundRelation:
     relation_type: str
     roles: tuple[BoundRole, ...]
     evidence_spans: tuple[SourceSpan, ...]
+    anchor_lens_id: str | None = None
 
 
 # ---------------------------------------------------------------------------
diff --git a/generate/problem_frame_builder.py b/generate/problem_frame_builder.py
index 0c9c0db4..ea1a58c9 100644
--- a/generate/problem_frame_builder.py
+++ b/generate/problem_frame_builder.py
@@ -39,6 +39,22 @@ from generate.problem_frame_proposals import (
     _unary_delta_proposals,
 )
 from packs.scalar_equivalence import extract_scalar_candidates
+from dataclasses import replace
+
+_RELATION_TO_ANCHOR = {
+    "transfer": "he_dabar_v1",
+    "consumption": "he_chayyim_v1",
+    "transaction": "he_tzedek_v1",
+    "labor_rate": "he_chesed_v1",
+    "travel": "he_chokmah_v1",
+    "unary_delta": "he_chayyim_v1",
+    "decrease_to_fraction": "he_tzedek_v1",
+    "container_packing": "grc_synesis_v1",
+    "partition": "grc_synesis_v1",
+    "comparison": "grc_logos_v1",
+    "percent_of": "grc_synesis_v1",
+    "subgroup_partition": "grc_synesis_v1",
+}
 
 
 def build_problem_frame(problem_text: str) -> ProblemFrame:
@@ -75,6 +91,9 @@ def build_problem_frame(problem_text: str) -> ProblemFrame:
         builder.add_process_frame(frame)
 
     for relation in _extract_candidate_relations(problem_text, frames):
+        anchor_id = _RELATION_TO_ANCHOR.get(relation.relation_type)
+        if anchor_id:
+            relation = replace(relation, anchor_lens_id=anchor_id)
         builder.add_relation(relation)
 
     question_target = _detect_question_target(problem_text)
@@ -138,6 +157,9 @@ def build_problem_frame(problem_text: str) -> ProblemFrame:
         proposals_for_grounding,
         builder.unary_delta_cues,
     ):
+        anchor_id = _RELATION_TO_ANCHOR.get(relation.relation_type)
+        if anchor_id:
+            relation = replace(relation, anchor_lens_id=anchor_id)
         builder.add_bound_relation(relation)
     bound_target = _bound_question_target(problem_text, mentions)
     if bound_target is not None:
```
