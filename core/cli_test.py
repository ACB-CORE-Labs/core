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
        "tests/test_architectural_invariants.py",
        # Audio sensorium lane — part of the smoke.yml PR gate (compiler,
        # CRDT merge, eval gates, pack manifest, mount, teachers; ~3s).
        # Listed explicitly so the local-first pre-push gate (AGENTS.md
        # protocol) equals the CI gate rather than silently narrowing it.
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
    # ADR-0024 chain suites (Phases 2-6). Each phase has its own contract
    # tests so reviewers can run them independently; ``adr-0024`` runs the full
    # chain end-to-end.
    "refusal": ("tests/test_refusal_contract.py",),
    "margin": ("tests/test_margin_admissibility.py",),
    "rotor": ("tests/test_rotor_admissibility.py",),
    "inner-loop": (
        "tests/test_inner_loop_admissibility.py",
        "tests/test_inner_loop_phase2.py",
        "tests/test_inner_loop_phase3.py",
        "tests/test_inner_loop_phase4.py",
    ),
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
        "tests/test_ratified_ledger_bridge.py",
        "tests/test_vocab_trigger_instrument.py",
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
