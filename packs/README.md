# Runtime Pack Artifacts

`packs/` contains ratified runtime pack artifacts and their narrow loaders:
safety, identity, ethics, register, anchor-lens, modality packs, source-language
packs, primitives, and companion validators.

This directory is not interchangeable with `language_packs/`:

- `packs/` stores runtime governance/style/safety/modality artifacts and source
  pack material such as `packs/en`, `packs/he`, `packs/grc`, and `packs/el`.
- `language_packs/` stores linguistic pack schemas, compilers, loaders, and
  reviewed semantic pack data under `language_packs/data/`.
- `core_ingest/` prepares external candidate pressure; it does not ratify or
  rewrite these packs.

Mutation rule: durable pack changes must be reviewed or proof-carrying and
must use the relevant validator/ratification lane. Do not add ad hoc runtime
pack writes.
