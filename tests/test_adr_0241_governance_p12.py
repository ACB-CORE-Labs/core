"""P12 governance close — contracts, checklist, and module inventory pins.

Does not re-execute the full physics suite. Asserts the load-bearing
governance surfaces for ADR-0241/0242 cohesion remain present and honest:
  * runtime_contracts documents off-serve quarantine + epistemic standing
  * acceptance checklist maps C0–C8 to tests
  * ADR statuses carry recorded ruling provenance (ratified 2026-07-15;
    a silent status flip in either direction fails)
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


def test_adrs_accepted_with_recorded_ruling_provenance():
    """P12 (post-ratification): status flips are valid ONLY with provenance.

    Joshua Shay ruled "Ratify" on 2026-07-15 (D10 acceptance packet §8), so
    the anti-self-Accept guard evolves rather than dies: each ADR must say
    Accepted WITH the ratification provenance inline, and the packet must
    carry the ruling record. A silent status flip in either direction — an
    Accept without provenance, or a quiet demotion — fails here.
    """
    packet = (
        _ROOT / "docs/audit/adr-0241-0242-acceptance-packet-2026-07-15.md"
    ).read_text(encoding="utf-8")
    assert "## 8. RULING RECORD" in packet, "ruling record section missing"
    assert "RATIFIED — Joshua Shay, 2026-07-15" in packet, "ruling attribution missing"

    for rel in (
        "docs/adr/ADR-0241-wave-field-driven-hyperbolic-atlas-and-resonant-cognition.md",
        "docs/adr/ADR-0242-atlas-packing-and-fibonacci.md",
    ):
        text = (_ROOT / rel).read_text(encoding="utf-8")
        status_line = next(
            (ln for ln in text.splitlines() if ln.startswith("**Status**")),
            "",
        )
        assert "Accepted" in status_line, f"{rel} lost Accepted status"
        assert "ratified by Joshua Shay" in status_line, (
            f"{rel} status lacks ratification provenance"
        )
        assert "acceptance-packet" in status_line, (
            f"{rel} status must cite the ruling packet"
        )


def test_serve_quarantine_list_matches_cohesion_ast_pin():
    cohesion = (_ROOT / "tests/test_third_door_cohesion.py").read_text(encoding="utf-8")
    for name in _QUARANTINE_NAMES:
        assert name in cohesion, f"cohesion AST pin missing {name}"
