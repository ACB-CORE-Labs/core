# Runtime Pack Artifacts

`packs/` contains ratified runtime pack artifacts and their narrow loaders:
safety, identity, ethics, register, anchor-lens, modality packs, source-language
packs, primitives, and companion validators.

This directory is not interchangeable with `packs/`:

- `packs/` stores runtime governance/style/safety/modality artifacts and source
  pack material such as `packs/en`, `packs/he`, `packs/grc`, and `packs/el`.
- `packs/` stores linguistic pack schemas, compilers, loaders, and
  reviewed semantic pack data under `packs/data/`.
- `core_ingest/` prepares external candidate pressure; it does not ratify or
  rewrite these packs.

Mutation rule: durable pack changes must be reviewed or proof-carrying and
must use the relevant validator/ratification lane. Do not add ad hoc runtime
pack writes.


# Language Packs

`packs/` owns reviewed language-pack loading and compilation. It turns
pack manifests, lexicon rows, morphology, grammar attractors, and alignment
metadata into runtime vocab/manifold structures.

This compiler is distinct from `core_ingest.compiler`:

- `packs.compiler` consumes reviewed pack data and builds linguistic
  runtime structures.
- `core_ingest.compiler` consumes external candidate pressure and produces
  validation reports plus provisional learning artifacts.

The shared word "compiler" means "deterministic lowering across a boundary";
the source material, trust boundary, and output structures are different.
