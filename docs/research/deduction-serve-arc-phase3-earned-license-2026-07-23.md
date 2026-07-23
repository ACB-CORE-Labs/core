# Deduction-serve arc — Phase 3 (earned SERVE license), 2026-07-23

**Base:** `main` @ `6a54d27a`. **Branch:** `feat/deduction-serve-phase2` (stacked on Phase 1+2).
**ADR:** `docs/adr/ADR-0256-deduction-serve-earned-license.md` (Proposed, ratify-on-merge).
**Depends on:** Phase 1 (composer), Phase 2 (lane).

## What shipped

Deduction serving stops being a bare `deduction_serving_enabled` flag and becomes an **earned capability** governed by the ADR-0175 reliability gate over the ADR-0199 learning arena — the arena's **second** concrete instance (GSM8K math is the first) and the reliability substrate's **first non-estimation serving consumer**.

```
> If p then q. p. Therefore q.
Given: p implies q; p. Your premises entail: q.          # earned band → authoritative

# (same input, ledger stripped)
(reasoned, but I haven't yet earned a verified track record on arguments of this
shape) Given: p implies q; p. Your premises entail: q.   # unearned → sound but disclosed
```

## The non-circular thesis

The ROBDD engine is sound+complete — it is *never wrong* on the problem it's handed, so a license cannot certify it. The **fallible** part is the template-based reader (`generate/meaning_graph/reader.py`): it can misparse an argument and hand the engine the *wrong* problem, which the engine then soundly decides — a wrong served answer. The reliability license certifies the **full pipeline** (reader → projector → engine) *per argument shape* — exactly the failure mode soundness doesn't cover. In the arena, a "wrong" is a misread caught by comparing the pipeline's committed outcome to by-construction gold.

## New files

- **`generate/proof_chain/shape.py`** — `classify_deduction_shape(premises, query)`, the capability axis: four exhaustive structural bands (`disjunctive`, `conditional_chain`, `conditional_single`, `atomic`). Computed identically by the arena and the serving composer (no drift). Bands are coarse on purpose — each mixes entailed/refuted/unknown gold so reliability measures decision correctness across outcomes.
- **`evals/deduction_serve/practice/gold.py`** — the arena's deduction instance: a deterministic, synthetic, indexed corpus per band (no clock/RNG), each case with **by-construction gold** (independent of the reader, ADR-0199 L-2); `DeductionSolver` (the real serving pipeline), `ConstructionGoldTether`, and `assert_corpus_sound` (cross-checks every gold against the independent truth-table oracle before sealing — a mis-stated gold can never inflate the ledger). Sized to the SERVE volume floor (`CASES_PER_BAND=720` ≥ the 657 a perfect record needs to clear θ_SERVE=0.99).
- **`evals/deduction_serve/practice/runner.py`** — `run()` (discrimination report), `seal_ledger()` (regenerates the committed SHA-sealed ledger; verifies corpus soundness first).
- **`chat/data/deduction_serve_ledger.json`** — the committed, self-sealed (`content_sha256`) ledger: all four bands, 720 correct / 0 wrong each.
- **`chat/deduction_serve_license.py`** — `deduction_serve_license(shape_band)`, the serving-side reader: loads + SHA-verifies the committed ledger, returns the `Action.SERVE` `LicenseDecision` per band under the safe default ceilings (θ_SERVE=0.99). Mirrors `generate/determine/estimation_license.py` exactly (tamper-evident, cached, pure gate).
- **`tests/test_deduction_serve_license.py`** — 13 tests (classifier, corpus soundness, earned-SERVE-per-band, committed-ledger SHA verify, tamper rejection, authoritative-vs-disclosed serving).
- **`docs/adr/ADR-0256-deduction-serve-earned-license.md`** — the decision + the ADR-0206 collision note (§2a).

## Changed files

- **`chat/deduction_surface.py`** — after the engine decides an in-band argument, the composer classifies its shape-band and consults the license: earned → authoritative (plain Phase-1 surface); unearned → disclosed hedge on the same sound answer. `license_lookup` is injectable for testing.
- **`core/config.py`** — `deduction_serving_enabled` docstring updated: it now enables an *earned* path, not a direct-serve switch.
- **`core/cli_test.py`** — `deductive` suite runs the new license test.

## Design decisions

**1. The license certifies pipeline-fidelity-per-shape, not engine soundness** (see thesis above). This is what makes the gate non-ceremonial: it measures the reader, which is genuinely fallible.

**2. Earned bands preserve Phase-1 behavior byte-for-byte.** All four structural bands earn SERVE on the committed ledger (reliability 0.99087), so every in-band argument serves authoritatively exactly as in Phase 1 — the license is transparent when earned. The gate's teeth are proven by injecting an empty ledger (test): the SAME sound answer degrades to a disclosed hedge. So authority rests on committed evidence, not a boolean — strip the ledger and CORE still reasons soundly but stops *claiming* verified authority.

**3. Did NOT reuse the ADR-0206 `govern_response`/`shape_surface` bridge.** Its STRICT/APPROXIMATE semantics are "widen past strict when licensed, disclosing an estimate" — the opposite shape from deduction (where the answer is *always* sound and the license governs authoritative-vs-disclosed *posture*). Forcing the bridge would invert its contract; a small, documented bespoke disclosure is more honest. Documented in ADR-0256 §3.

**4. ADR-numbering collision documented, not rewritten** (ADR-0256 §2a). `entail.py`'s real home is ADR-0218; response governance is ADR-0206; deduction serving is ADR-0256. `evals/deductive_logic/report.json` still stamps `"adr": "ADR-0206"` — deliberately NOT changed, because its bytes are SHA-pinned and rewriting them would cascade the lane pin for no capability change. The ADR records the correct homes so no reader trusts the stale pointer.

## Verification

```
uv run python -m evals.deduction_serve.practice.runner            # 4 bands, all SERVE, wrong=0
uv run python -m pytest tests/test_deduction_serve_license.py -q  # 13 passed
uv run core test --suite deductive -q                              # 38 passed
uv run core test --suite smoke -q                                  # 180 passed
uv run core test --suite cognition -q                               # 122 passed, 1 skipped
uv run python -m pytest tests/test_architectural_invariants.py -q   # 75 passed
```

## Verdict

Phase 3 complete. Deduction serving is now an *earned* capability: authority rests on a committed, SHA-sealed, independently-verified track record per argument shape, consumed read-only by the serving path. The ADR-0175/0199 reliability substrate gains its first real serving consumer beyond estimation — a concrete dent in that zone's standing "designed, not wired" critique.
