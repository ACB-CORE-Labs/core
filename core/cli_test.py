"""Curated pytest and ruff CLI command handlers."""

from __future__ import annotations

import argparse
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol


TEST_SUITES: dict[str, tuple[str, ...]] = {
    "fast": (
        "tests/test_cli_test_suites.py",
        "tests/test_cli_runner_contract.py",
        "tests/test_runtime_config.py",
        "tests/test_core_semantic_seed_pack.py",
        "tests/test_intent_proposition_graph.py",
        "tests/test_articulation_realizer_v2.py",
        "tests/test_reviewed_teaching_loop.py",
        "tests/test_cognitive_eval_harness.py",
    ),
    "smoke": (
        "tests/test_chat_runtime.py",
        "tests/test_achat.py",
        "tests/test_runtime_config.py",
        "tests/test_cognitive_turn_pipeline.py",
        "tests/test_audit_ledger_r7.py",
        "tests/test_architectural_invariants.py",
        "tests/test_cli_runner_contract.py",
        # Audio sensorium lane — also named in smoke.yml (compiler, CRDT
        # merge, eval gates, pack manifest, mount, teachers; ~3s).
        # Listed explicitly so the local-first pre-push gate (AGENTS.md
        # protocol) is never NARROWER than smoke.yml. It does not "equal"
        # it, and must not: this tuple is the SOURCE and is deliberately
        # broader (AGENTS.md §277/§280 — the workflows are secondary
        # observability, GitHub Actions are billing-locked dead signals).
        # The one-directional pin is
        # tests/test_cli_test_suites.py::test_cli_smoke_suite_covers_ci_smoke_gate,
        # whose symmetric version was tried and reverted in 50fa287d
        # (2026-07-25). Corrected 2026-07-28 per N-9: the earlier wording
        # claimed an equality that has never held and twice sent readers
        # looking for drift that is a design decision.
        "tests/test_audio_compiler.py",
        "tests/test_audio_crdt_merge.py",
        "tests/test_audio_eval_gates.py",
        "tests/test_audio_pack_manifest.py",
        "tests/test_audio_sensorium_mount.py",
        "tests/test_audio_teachers.py",
        # ADR-0043 — identity falsifiability: ratified identity packs must
        # produce distinct, directionally-correct articulations, with a
        # pack-invariant grounding/refusal floor and zero fabrication. Lives
        # only under ``full`` historically, so a divergence regression cleared
        # the PR gate and surfaced only post-merge. Promoted into smoke so
        # the falsifiability claim blocks-on-regression rather than
        # detect-after-merge.
        "tests/test_pack_measurements_phase2.py",
        # ADR-0253 dual-pack boundary — draft he/grc trees must not be serve imports.
        "tests/test_pack_draft_serve_boundary.py",
        # Register axis (ADR-0069/0071/0077) — the e2e tests here are the
        # falsifiable contract that terse/convivial registers actually differ
        # from neutral on pipeline-served surfaces. Red on main outside every
        # gate for 2026-07-20..24 (the register-axis serving regression,
        # docs/research/lane-drift-investigation-2026-07-24.md) because this
        # file lived only under `full`; the lane-shas job was the sole gate
        # that runs the demo lanes this axis shows up in, and its failures
        # were conflated with an unrelated flake. Promoted so this axis can
        # never silently regress again.
        "tests/test_register_substantive_consumption.py",
        # Deduction serving is LIVE (ADR-0256 ratified the flag ON), so its
        # cross-stack provenance contract is a serving-path contract, not a
        # capability-under-development one. Workbench's live chat route builds
        # a bare ChatRuntime(), which means these composers decide Workbench
        # turns too — and while their labels were unregistered the API coerced
        # them to "none" and recorded a proved answer as ungrounded. ~3s.
        "tests/test_workbench_deduction_provenance.py",
        # Correction binding anchors to hash_surface, in lockstep with every
        # substantive override of the served surface. Cheap, and the axis is
        # invisible until it breaks silently.
        "tests/test_prior_surface_deduction_binding.py",
        # CORE must not serve the affirmative of a proposition the user denied.
        # This was live behind `realizer_grounded_authority`: "evidence does not
        # support truth" and "evidence supports truth" served byte-identical
        # surfaces, because the graph had no slot for a denial. It is a truth
        # defect on a serving path, so it belongs on the pre-push gate, not
        # under `full` — and this file is registered in the same PR that
        # creates it, per the #136 finding that an unregistered pin runs
        # nowhere. ~6s, mostly two real pipeline turns per denial pair.
        "tests/test_negation_survives_articulation.py",
        # The speculative marker must survive a neighbour's review. Teaching
        # indexes a subject under its tokens, so one COHERENT correction used
        # to release a token an unrelated, still-unreviewed proposal was
        # relying on — serving unreviewed material with no "(speculative, not
        # yet reviewed)" prefix. That is a truth-on-the-served-surface defect,
        # so it belongs on the pre-push gate rather than under `full`. The file
        # predates the fix but ran in NO curated suite, which is why the
        # regression was invisible; it is registered here **and in smoke.yml**
        # in the same PR as the fix, per the #136 finding that an unregistered
        # pin runs nowhere. Registering it in both keeps the local/CI delta at
        # the same ten files (H-12), so it settles nothing R-14 has to rule.
        # ~9s, cache-level with two served-surface assertions.
        "tests/test_speculative_subject_lifecycle.py",
        # PR-9 (H-11) — the turn spine's three defensive backstops must stay
        # broad AND stay visible. Each used to write a value indistinguishable
        # from its healthy case: a raising accrual chain left the same None a
        # quiet turn leaves, a logos decision that raised looked like one never
        # consulted, a crashed probe recorded the same empty neighborhood as a
        # probe that found nothing. Silence in the one layer whose constitution
        # is "failures are typed, never silent" (INV-34). Registered in both
        # gates on creation, per #136. ~6s.
        "tests/test_accrual_swallow_telemetry.py",
        # PR-4 / G-7 — a new test file may not land outside every curated
        # suite. Four times in-repo a pin was written for a real defect,
        # registered nowhere, ran on no pre-merge gate, and the thing it
        # pinned regressed anyway (#113, #136, negation-survives-articulation,
        # speculative-subject-lifecycle). A ratchet against
        # tests/full_only_baseline.txt blocks the recurrence; the 749 legacy
        # full-only files stay a declared, shrinking number rather than 749
        # invented justifications (N-9). Filesystem + glob only, <1s.
        "tests/test_suite_membership.py",
        # PR-4 pin 3 / G-7 — MEMBERSHIP WAS NEVER THE GUARANTEE; EXECUTION IS.
        # The membership ratchet closed "no new orphans" and, within the hour,
        # this arc's full-tree run found test_ratification_ceremony.py RED, in
        # the curated suite `teaching`, invoked by no gate tier. Measured: 21
        # curated suites, 2 gate-reachable. This freezes the 19-suite gap so it
        # cannot grow silently, enforced in both directions, with the declared
        # gate set verified against the shell so the pin cannot go vacuous.
        # It deliberately does NOT decide which of the 19 belong on the gate —
        # that costs gate time and is Shay's call. <1s.
        "tests/test_suite_reachability.py",
        # G-23 — DOMAIN_PACKS and the pack manifests state one fact twice, and
        # only one direction was checked. domain_contract_predicates P3 validates
        # domain_id -> a known domain; NOTHING validated DOMAIN_PACKS -> the
        # manifest agrees, and P3 passes VACUOUSLY on a manifest with no
        # domain_id at all. Measured 7 of 9 bound, 0 contradictory, 2 absent —
        # both in philosophy_theology, a band queued to earn SERVE behind R-8.
        # The existing predicate tests run only on synthetic tmp_path manifests
        # and sit in no curated suite, so they could not have caught it.
        # Reads 30 small JSON files, <1s.
        "tests/test_domain_pack_binding.py",
        # G-22 — CLAIMS.md is a PUBLISHED capability artifact, deterministically
        # regenerable from the capability ledger + PINNED_SHAS. It published a
        # superseded evidence digest for deduction_serve_v1 for two days after
        # f9e9cc0c moved the lane, because that commit updated the lane, the
        # verifier and the lane test but not the published claim — and this pin,
        # which would have caught it, ran in no curated suite. A claim whose
        # evidence digest does not match its evidence is the exact failure the
        # digest exists to prevent. <1s.
        "tests/test_claims_md_is_current.py",
        # G-22 — ratification-corpus byte compatibility and unreviewed-status
        # refusal. Red on main and unverified since ADR-0264 R1 landed, because
        # the pins iterated ChainRecord.__slots__ while affirmative rows omit
        # `polarity` by design. Governance-path contract; belongs on the gate.
        "tests/test_ratification_ceremony.py",
        # PR-6 / G-9 — three AGENTS.md prohibitions enforced by test instead of
        # review: exact recall (no cosine/ANN/HNSW on any path that decides
        # recalled truth — the prior ban covered ONE physics module while
        # generate/realize/recall.py stated the law in a docstring and nothing
        # enforced it), governance non-bypass (a serving path may not assemble
        # verdicts without running the safety check), and the safety pack's
        # placement on this gate. Source scan only, <1s.
        "tests/test_doctrine_prohibitions.py",
        # The safety pack's fail-closed contract: unratified pack refused in
        # production, missing companion report refused, seal failure refused,
        # path traversal rejected, missing pack fails closed. It ran in NO
        # curated suite — a safety-critical contract verified only after merge
        # (G-9c). ~2s.
        "tests/test_safety_pack.py",
        # The smoke/CI parity pin must run on the gate it guards. It enforces
        # that this tuple is never NARROWER than smoke.yml — and it lived in
        # `fast`, which the pre-push gate does not run (N-9). ~1s.
        "tests/test_cli_test_suites.py",
        # ADR governance. An ADR that governs a default-ON flag records a
        # decision already in force, so leaving it "Proposed" makes the
        # governance record assert something false about the running system —
        # which is what happened to ADR-0256 while deduction serving was live.
        # Filesystem + regex only, ~1.2s, and it is the record for a serving
        # path, so it belongs on the pre-push gate rather than under `full`.
        # test_adr_index.py rides along: it landed in #113 registered in NO
        # curated suite, which is the same silent-red shape it exists to catch.
        "tests/test_adr_status_governance.py",
        "tests/test_adr_index.py",
        # Volume honesty (ADR-0264 R9). The Wilson floor assumes independent
        # trials; a deterministic pipeline replaying one case N times supplies
        # one trial's evidence, not N. This pins the measured exposure in the
        # ratified deduction ledger (21 of 25 bands short on distinct evidence)
        # in BOTH directions, and forces any new licensed capability to register
        # an audit source. It gates a live, flag-ON serving path, so it belongs
        # on the pre-push gate. ~1.5s.
        "tests/test_volume_honesty.py",
        # ADR-0264 R1-R4/R8 — taught curriculum NEGATIVES. Before this, a row
        # authored to refute compiled to a premise ASSERTING the atom, and the
        # independent oracle ignored polarity too, so gold agreed and wrong=0
        # stayed green. Corpus-level epistemology is unfalsifiable by every
        # other gate here, so this one belongs on the pre-push gate. ~0.4s.
        "tests/test_curriculum_polarity.py",
    ),
    "runtime": (
        "tests/test_chat_runtime.py",
        "tests/test_achat.py",
        "tests/test_runtime_config.py",
        "tests/test_session_coherence.py",
    ),
    "cognition": (
        "tests/test_intent_proposition_graph.py",
        "tests/test_cognitive_turn_pipeline.py",
        "tests/test_audit_ledger_r7.py",
        "tests/test_articulation_realizer_v2.py",
        "tests/test_semantic_realizer_integration.py",
        "tests/test_cognitive_eval_harness.py",
        "tests/test_deterministic_hash.py",
        "tests/test_morphology_irregular.py",
        "tests/test_realizer_quantifier_agreement.py",
        "tests/test_benchmarks_profiler.py",
        "tests/test_compose_relations.py",
        "tests/test_replay_vs_llm_benchmark.py",
    ),
    "teaching": (
        "tests/test_reviewed_teaching_loop.py",
        "tests/test_pipeline_teaching_integration.py",
        "tests/test_epistemic_invariants.py",
        "tests/test_adr_0172_w2_decomposer.py",
        "tests/test_adr_0172_w5_inference_proposal.py",
        "tests/test_math_frame_ratification.py",
        "tests/test_math_composition_ratification.py",
        "tests/test_teaching_coverage_cli.py",
        "tests/test_proposal_queue.py",
        # The ratification ceremony is the only path that turns a reviewed
        # proposal into a routable ratified chain — i.e. the one mechanism that
        # can move the curriculum-volume constraint. It landed in #113 in NO
        # curated suite, so its 14 tests ran only under `full`.
        "tests/test_ratification_ceremony.py",
    ),
    "packs": (
        "tests/test_pack_draft_serve_boundary.py",
        "tests/test_core_semantic_seed_pack.py",
        "tests/test_adr_0127_pack_ratification.py",
        "tests/test_frame_registry_load.py",
        "tests/test_composition_registry_load.py",
        "tests/test_composition_consult_in_injector.py",
        "tests/test_consumption_case_0050_hazard_pin.py",
        "tests/test_consumption_empty_registry_no_op.py",
        "tests/test_consumption_partition.py",
        "tests/test_matcher_extension_currency_per_unit.py",
        "tests/test_matcher_extension_case_0050_hazard_pin.py",
        "tests/test_matcher_extension_end_to_end_admission.py",
        "tests/test_me2_cross_sentence_subject.py",
        "tests/test_me2_case_0019_admits.py",
        "tests/test_me3_additive_composition.py",
        "tests/test_me4_subtractive_composition.py",
        "tests/test_me5_all_categories_integration.py",
        "tests/test_rat1_end_to_end_admission.py",
        "tests/test_wave_a_multiplicative_aggregation_injector.py",
    ),
    "algebra": (
        "tests/test_stage2_physics_hardening.py",
        "tests/test_geometric_convergence_checklist.py",
        "tests/test_versor_closure.py",
        "tests/test_holonomy.py",
        "tests/test_holonomy_resonance.py",
        "tests/test_energy.py",
        "tests/test_motor.py",
        "tests/test_null_cone.py",
        "tests/test_vault_recall.py",
        "tests/test_vault_recall_vectorised.py",
        "tests/test_vault_recall_rust_parity.py",
        "tests/test_cga_inner_rust_parity.py",
        "tests/test_geometric_product_rust_parity.py",
        "tests/test_versor_condition_rust_parity.py",
        "tests/test_versor_apply_rust_parity.py",
    ),
    "sensorium": (
        "tests/test_sensorium_compiler_delta.py",
        "tests/test_audio_compiler.py",
        "tests/test_audio_crdt_merge.py",
        "tests/test_audio_eval_gates.py",
        "tests/test_audio_pack_manifest.py",
        "tests/test_audio_sensorium_mount.py",
        "tests/test_vision_compiler.py",
        "tests/test_event_vision_compiler.py",
        "tests/test_vision_crdt_merge.py",
        "tests/test_vision_eval_gates.py",
        "tests/test_vision_sensorium_mount.py",
        "tests/test_sensorimotor_contract.py",
        "tests/test_sensorimotor_pack_manifest.py",
        "tests/test_observation_frame_contract.py",
        "tests/test_observation_frame_harness.py",
        "tests/test_environment_falsification.py",
        "tests/test_environment_falsification_eval_cli.py",
        "tests/test_witness_log_importer.py",
        "tests/test_tabletop_lab_protocol.py",
        "tests/test_sensorium_eval_cli.py",
        "tests/test_efferent_gate.py",
    ),
    "pulse": (
        "tests/test_pulse_integration.py",
        "tests/test_graph_diffusion.py",
    ),
    "formation": ("tests/formation",),
    "proof": ("tests/test_proof_properties.py",),
    # ADR-0024 chain suites (Phases 2-6). ``adr-0024`` runs the full chain
    # end-to-end; ``phase5``/``phase6`` survive because README.md and the
    # forward_semantic_control READMEs invoke them by name.
    #
    # PR-3b (Wave 1, 2026-07-28) — four per-phase aliases deleted: ``refusal``,
    # ``margin``, ``rotor``, ``inner-loop``. Each was offered so reviewers could
    # run a phase independently, and measured across the repository, **nothing
    # invoked any of them** — zero `--suite` references in code, docs, ADRs,
    # workflows or the CLI's own help. Every one of their seven files is still
    # covered by ``adr-0024``, so no coverage moved and nothing was orphaned.
    # An alias nobody calls is not a curation decision; it is a name that has to
    # be kept true. Two ratchets (membership, reachability) were policing these.
    "phase5": ("tests/test_phase5_corpus.py",),
    "phase6": ("tests/test_phase6_demo.py",),
    "adr-0024": (
        "tests/test_refusal_contract.py",
        "tests/test_margin_admissibility.py",
        "tests/test_rotor_admissibility.py",
        "tests/test_inner_loop_admissibility.py",
        "tests/test_inner_loop_phase2.py",
        "tests/test_inner_loop_phase3.py",
        "tests/test_inner_loop_phase4.py",
        "tests/test_phase5_corpus.py",
        "tests/test_phase6_demo.py",
    ),
    # ADR-0126 P6 — measurement harness for the GSM8K candidate-graph parser
    # exit criterion. ``wrong == 0`` is a hard gate (Obligation #4: refuse
    # rather than confabulate).
    "math": ("tests/test_adr_0126_train_sample_runner.py",),
    "deductive": (
        "tests/test_deductive_logic_entail.py",
        "tests/test_deduction_serve_lane.py",
        "tests/test_deduction_serve_license.py",
        "tests/test_categorical_decider.py",
        "tests/test_english_argument_reader.py",
        "tests/test_member_argument_reader.py",
        "tests/test_cond_member_argument_reader.py",
        "tests/test_verb_argument_reader.py",
        "tests/test_exist_argument_reader.py",
        "tests/test_deduction_serve_e2e.py",
        "tests/test_curriculum_serve.py",
        "tests/test_curriculum_practice.py",
        "tests/test_curriculum_polarity.py",
        "tests/test_ledger_reseal.py",
        "tests/test_ratified_ledger_bridge.py",
        "tests/test_vocab_trigger_instrument.py",
        "tests/test_grammar_roundtrip.py",
        "tests/test_lexicon_single_source.py",
        # Phase 4 — which realizer serves, and what the other one's score
        # means. Registered here deliberately: this file exists because a lane
        # reported 117/117 for a function nothing calls, and a pin that no
        # curated suite runs is the same defect one level up. Pure in-process
        # lane replay, ~0.4s.
        "tests/test_phase4_realizer_resolution.py",
        # The grammar arc's agreement oracle and the tail-preservation
        # invariant. It lived ONLY in the `cognition` suite, which is not on
        # the AGENTS.md pre-push gate (smoke + deductive) — so every pin
        # Phases 3 and 4 added to it, including the invariant that covers all
        # twelve inflection branches, ran in no gate at all. Exactly the
        # silent-red shape called out for test_adr_index.py above, and the
        # reason smoke stayed at 621 across two PRs that added 13 tests.
        # ~0.4s; it belongs with the other grammar pins.
        "tests/test_realizer_quantifier_agreement.py",
        # Phase 5 item 1 — the reader/writer construction overlap, plus the
        # fabrication pins. Gated rather than left to the `full` lane because
        # three of its pins are wrong=0 hazards on a serving path: the reader
        # accepts `every dog is a mammal` as an assertion about `every_dog`,
        # and recites `Given: furthermore; ...` back to the user. Those must
        # not be able to worsen silently. ~9.5s (sweeps the writer's whole
        # parameter space three times, once per vocabulary).
        "tests/test_construction_inventory.py",
    ),
    "full": ("tests/",),
}


class CommandRunner(Protocol):
    def __call__(
        self,
        *args: str,
        check: bool = False,
        cwd: Path | None = None,
        env: dict[str, str] | None = None,
    ) -> int: ...


def run_command(
    *args: str,
    check: bool = False,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> int:
    completed = subprocess.run(args, check=check, text=True, cwd=cwd, env=env)
    return int(completed.returncode)


def pytest_args_for_suite(suite: str, extra_args: Sequence[str]) -> list[str]:
    paths = TEST_SUITES[suite]
    forwarded = list(extra_args)
    if forwarded and forwarded[0] == "--":
        forwarded = forwarded[1:]
    return [*paths, *forwarded]


def xdist_available() -> bool:
    """Return True iff ``pytest-xdist`` is importable."""
    try:
        import xdist  # noqa: F401
    except ImportError:
        return False
    return True


def maybe_inject_xdist(forwarded: list[str], suite: str | None) -> list[str]:
    """Inject ``-n auto`` for suites large enough to benefit from parallelism."""
    if not xdist_available():
        return forwarded
    # Honour explicit operator override.
    if any(a.startswith("-n") or a == "--dist" for a in forwarded):
        return forwarded
    if suite == "full":
        return ["-n", "auto", *forwarded]
    return forwarded


def cmd_test(
    args: argparse.Namespace,
    *,
    run: CommandRunner = run_command,
    python_executable: str = sys.executable,
) -> int:
    """Run pytest through curated suite aliases or direct passthrough args."""
    default_args = ["-q", "--tb=short"]
    if args.list_suites:
        for name in sorted(TEST_SUITES):
            print(name)
        return 0
    if args.suite:
        forwarded = pytest_args_for_suite(args.suite, args.args or default_args)
    else:
        forwarded = list(args.args or default_args)
        if forwarded and forwarded[0] == "--":
            forwarded = forwarded[1:]
    forwarded = maybe_inject_xdist(forwarded, args.suite)
    return run(python_executable, "-m", "pytest", *forwarded)


def cmd_check(
    args: argparse.Namespace,
    *,
    run: CommandRunner = run_command,
    python_executable: str = sys.executable,
) -> int:
    """Run ruff over selected project paths."""
    targets = args.paths or [
        "algebra",
        "alignment",
        "chat",
        "core",
        "field",
        "generate",
        "ingest",
        "packs",
        "morphology",
        "persona",
        "sensorium",
        "session",
        "vault",
        "vocab",
        "tests",
    ]
    return run(python_executable, "-m", "ruff", "check", *targets)
