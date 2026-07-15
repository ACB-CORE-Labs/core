"""P12 governance close — contracts, checklist, and module inventory pins.

Does not re-execute the full physics suite. Asserts the load-bearing
governance surfaces for ADR-0241/0242 cohesion remain present and honest:
  * runtime_contracts documents off-serve quarantine + epistemic standing
  * acceptance checklist maps C0–C8 to tests
  * ADRs stay Proposed (ready for Joshua) — not self-Accepted
  * cohesion suite still names I-01…I-05 pins
"""

from __future__ import annotations

from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]

_QUARANTINE_NAMES = (
    "wave_manifold",
    "holographic_vault",
    "atlas_packing",
    "fibonacci_search",
    "wave_seam",
    "wave_energy_boundary",
)

_REQUIRED_MODULES = (
    "core/physics/wave_manifold.py",
    "core/physics/holographic_vault.py",
    "core/physics/atlas_packing.py",
    "core/physics/fibonacci_search.py",
    "core/contemplation/wave_seam.py",
    "core/physics/wave_energy_boundary.py",
    "docs/analysis/core_cohesion_master_plan.md",
    "docs/audit/adr_0241_cohesion_acceptance_checklist.md",
    "docs/specs/runtime_contracts.md",
    "docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md",
    "docs/adr/ADR-0242-atlas-packing-and-fibonacci.md",
    "tests/test_third_door_cohesion.py",
)


def test_required_cohesion_modules_exist():
    missing = [p for p in _REQUIRED_MODULES if not (_ROOT / p).is_file()]
    assert not missing, f"missing governance surfaces: {missing}"


def test_runtime_contracts_documents_wave_quarantine():
    text = (_ROOT / "docs/specs/runtime_contracts.md").read_text(encoding="utf-8")
    assert "Wave-field cohesion substrate" in text
    assert "Off-serve quarantine" in text
    for name in _QUARANTINE_NAMES:
        assert name in text, f"runtime_contracts missing quarantine name {name}"
    assert "SPECULATIVE" in text
    assert "seal_mode_reviewed" in text or "authorized=True" in text
    assert "reconstruct_as_evidence" in text
    assert "crystallization_for_holographic_seal" in text


def test_acceptance_checklist_maps_c0_c8_to_tests():
    text = (
        _ROOT / "docs/audit/adr_0241_cohesion_acceptance_checklist.md"
    ).read_text(encoding="utf-8")
    for cid in ("C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8"):
        assert cid in text
    assert "test_third_door_cohesion.py" in text
    assert "Joshua" in text
    assert "must **not** self-accept" in text or "must not self-accept" in text.lower()


def test_cohesion_suite_names_entity_invariants():
    text = (_ROOT / "tests/test_third_door_cohesion.py").read_text(encoding="utf-8")
    for inv in ("i01", "i02", "i03", "i04", "i05"):
        assert f"test_{inv}_" in text or f"test_i0" in text
    # Explicit per-invariant function names (progressive suite).
    for name in (
        "test_i01_biography_holonomy_closed_and_modes_reloadable",
        "test_i02_holographic_round_trip_float32_honest",
        "test_i03_self_authorship_proposals_are_speculative_only",
        "test_i04_phase_correlation_symmetric_algebraic",
        "test_i05_unitary_propagator_amplitude_conservation",
    ):
        assert name in text, f"missing entity pin {name}"


def test_adrs_ready_for_acceptance_not_self_accepted():
    """P12: implementation complete → Proposed + ready; Joshua alone Accepts."""
    for rel in (
        "docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md",
        "docs/adr/ADR-0242-atlas-packing-and-fibonacci.md",
    ):
        text = (_ROOT / rel).read_text(encoding="utf-8")
        # First status line must remain Proposed until human Accept.
        status_line = next(
            (ln for ln in text.splitlines() if ln.startswith("**Status**")),
            "",
        )
        assert "Proposed" in status_line, f"{rel} lost Proposed status"
        assert "Accepted" not in status_line, f"{rel} must not self-Accept"
        assert "Joshua" in status_line or "ready" in status_line.lower()


def test_serve_quarantine_list_matches_cohesion_ast_pin():
    cohesion = (_ROOT / "tests/test_third_door_cohesion.py").read_text(encoding="utf-8")
    for name in _QUARANTINE_NAMES:
        assert name in cohesion, f"cohesion AST pin missing {name}"
