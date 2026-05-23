"""ADR-0119.1 — fabrication_control sealed holdout tests.

Pins five load-bearing invariants:
1. The .age file exists.
2. The .age file has a valid age header.
3. Decrypting with the known identity reproduces original cases.
4. Running holdout without CORE_HOLDOUT_KEY raises EnvironmentError.
5. Running holdout with CORE_HOLDOUT_KEY succeeds and matches metrics.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest
from pyrage import decrypt
from pyrage import x25519

from evals.framework import get_lane, run_lane
from evals.holdout_runner import HOLDOUT_KEY_ENV


_REPO_ROOT = Path(__file__).resolve().parent.parent
_AGE_FILE = _REPO_ROOT / "evals" / "fabrication_control" / "holdouts" / "v1" / "cases.jsonl.age"
_RECIPIENTS_FILE = _REPO_ROOT / "docs" / "holdout_recipients.txt"

# Default local location of private key
_LOCAL_KEY_PATH = Path("/Users/kaizenpro/.config/core/holdout_keys/repo_holdout.txt")


def _get_identity_path() -> Path | None:
    key_env = os.environ.get(HOLDOUT_KEY_ENV)
    if key_env:
        p = Path(key_env)
        if p.exists():
            return p
    if _LOCAL_KEY_PATH.exists():
        return _LOCAL_KEY_PATH
    return None


def _get_original_cases_from_git() -> bytes:
    # Try main branch or parent commits
    for ref in ("main", "origin/main", "HEAD~1"):
        try:
            completed = subprocess.run(
                ["git", "show", f"{ref}:evals/fabrication_control/cases/holdout.jsonl"],
                capture_output=True,
                check=True,
            )
            if completed.stdout.strip():
                return completed.stdout
        except subprocess.CalledProcessError:
            continue
    raise FileNotFoundError("Could not locate reference holdout.jsonl in git history")


def test_age_file_exists() -> None:
    assert _AGE_FILE.exists()
    assert _AGE_FILE.stat().st_size > 0


def test_age_file_has_valid_header() -> None:
    data = _AGE_FILE.read_bytes()
    assert data.startswith(b"age-encryption.org/")


def test_recipients_file_exists_and_declares_lane() -> None:
    assert _RECIPIENTS_FILE.exists()
    content = _RECIPIENTS_FILE.read_text(encoding="utf-8")
    assert "fabrication_control:" in content


def test_decryption_matches_original_payload() -> None:
    key_path = _get_identity_path()
    if key_path is None:
        pytest.skip("No private identity key found for decryption test.")

    identity_text = key_path.read_text(encoding="utf-8")
    identities = [
        x25519.Identity.from_str(line.strip())
        for line in identity_text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert identities, "No identities found in key file"

    encrypted_bytes = _AGE_FILE.read_bytes()
    decrypted_bytes = decrypt(encrypted_bytes, identities)

    original_bytes = _get_original_cases_from_git()
    assert decrypted_bytes.strip() == original_bytes.strip()


def test_running_holdout_without_key_fails_closed() -> None:
    # Temporarily unset the key from env
    original_key = os.environ.get(HOLDOUT_KEY_ENV)
    try:
        if HOLDOUT_KEY_ENV in os.environ:
            del os.environ[HOLDOUT_KEY_ENV]
        
        lane = get_lane("fabrication_control")
        with pytest.raises(EnvironmentError) as exc_info:
            run_lane(lane, split="holdout")
        
        assert "Set CORE_HOLDOUT_KEY" in str(exc_info.value)
    finally:
        if original_key is not None:
            os.environ[HOLDOUT_KEY_ENV] = original_key


def test_running_holdout_with_key_succeeds_and_reproduces_metrics() -> None:
    key_path = _get_identity_path()
    if key_path is None:
        pytest.skip("No private identity key found to run holdout split.")

    original_key = os.environ.get(HOLDOUT_KEY_ENV)
    try:
        os.environ[HOLDOUT_KEY_ENV] = str(key_path)
        lane = get_lane("fabrication_control")
        result = run_lane(lane, split="holdout")
        
        # Verify that all cases were run and metrics matched expected values
        assert result.metrics["fabrication_rate"] == 0.0
        assert result.metrics["refusal_recall"] == 1.0
        assert result.metrics["grounding_source_matches_expected"] == 1.0
        assert result.metrics["coincidence_rate"] == 0.0
        assert result.metrics["trace_evidence_present"] == 1.0
    finally:
        if original_key is not None:
            os.environ[HOLDOUT_KEY_ENV] = original_key
        else:
            if HOLDOUT_KEY_ENV in os.environ:
                del os.environ[HOLDOUT_KEY_ENV]
