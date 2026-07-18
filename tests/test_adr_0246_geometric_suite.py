"""ADR-0246 §6.1/§6.2 eval-suite pins — every synthetic case fails loudly.

Pins the runnable ``evals.adr_0246_geometric_suite`` harness AND the specific
§6.1 rows the preflight table calls out (π-inversion ``s≈-1``, 90° permutation
``s≈0``, near-singular Gram → ``ManifoldConditioningError``, malformed F →
``MalformedVersorError``), so a regression names the exact broken case.
"""

from __future__ import annotations

import numpy as np
import pytest

from algebra.cl41 import N_COMPONENTS
from core.physics.identity_manifold import (
    IdentityManifoldGeometry,
    ManifoldConditioningError,
    MalformedVersorError,
)
from evals.adr_0246_geometric_suite import (
    build_suite_report,
    default_geometry,
    identity_versor,
    rotor,
    run_geometric_suite,
    run_path_suite,
)

_E12 = 6


@pytest.fixture(scope="module")
def geometry() -> IdentityManifoldGeometry:
    return default_geometry()


def test_full_suite_all_cases_pass():
    report = build_suite_report()
    # every case must pass; the assertion message names any that did not
    failed = [c["name"] for c in report["geometric_suite"] + report["path_suite"] if not c["passed"]]
    assert failed == [], f"failing cases: {failed}"
    assert report["all_passed"] is True
    assert report["case_count"] == report["passed_count"] == 14


@pytest.mark.parametrize("case", [c["name"] for c in run_geometric_suite()])
def test_each_geometric_case_passes(geometry, case):
    result = {c["name"]: c for c in run_geometric_suite(geometry)}[case]
    assert result["passed"], result["checks"]


@pytest.mark.parametrize("case", [c["name"] for c in run_path_suite()])
def test_each_path_case_passes(geometry, case):
    result = {c["name"]: c for c in run_path_suite(geometry)}[case]
    assert result["passed"], result["checks"]


# --- explicit §6.1 pins (directive step 4: fail loudly on the exact expected) --


def test_pi_inversion_self_align_is_minus_one(geometry):
    _, self_align = geometry.axis_response(rotor(_E12, np.pi))
    assert self_align[0] == pytest.approx(-1.0, abs=1e-9)  # e1 inverted
    assert self_align[1] == pytest.approx(-1.0, abs=1e-9)  # e2 inverted
    assert self_align[2] == pytest.approx(1.0, abs=1e-9)   # e3 fixed


def test_90deg_permutation_self_align_is_zero(geometry):
    _, self_align = geometry.axis_response(rotor(_E12, np.pi / 2.0))
    assert self_align[0] == pytest.approx(0.0, abs=1e-9)  # e1 → e2, orthogonal
    assert self_align[1] == pytest.approx(0.0, abs=1e-9)


def test_near_singular_gram_fails_closed():
    with pytest.raises(ManifoldConditioningError):
        IdentityManifoldGeometry.from_directions(
            ((1.0, 0.0, 0.0), (1.0, 1e-9, 0.0), (0.0, 0.0, 1.0))
        )


def test_malformed_versor_raises_typed_error(geometry):
    nan_v = identity_versor()
    nan_v[5] = np.inf
    with pytest.raises(MalformedVersorError):
        geometry.induced_action(nan_v)
    with pytest.raises(MalformedVersorError):
        geometry.typed_residual_energy(np.ones(N_COMPONENTS + 3, dtype=np.float64))


def test_suite_is_offserving():
    import evals.adr_0246_geometric_suite as suite

    assert suite.__file__ is not None
    with open(suite.__file__, encoding="utf-8") as fh:
        src = fh.read()
    # no actual import of serve modules (the A-04 note in the docstring names
    # chat.runtime as forbidden, so match import statements, not the substring)
    assert "import chat" not in src and "from chat" not in src
