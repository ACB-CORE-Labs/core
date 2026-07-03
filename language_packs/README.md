# Language Packs

`language_packs/` owns reviewed language-pack loading and compilation. It turns
pack manifests, lexicon rows, morphology, grammar attractors, and alignment
metadata into runtime vocab/manifold structures.

This compiler is distinct from `core_ingest.compiler`:

- `language_packs.compiler` consumes reviewed pack data and builds linguistic
  runtime structures.
- `core_ingest.compiler` consumes external candidate pressure and produces
  validation reports plus provisional learning artifacts.

The shared word "compiler" means "deterministic lowering across a boundary";
the source material, trust boundary, and output structures are different.
