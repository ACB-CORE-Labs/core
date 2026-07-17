"""ADR-0244 §2.7 semantic-rigor pins (cohesion directive Mandates 4 + 5).

Content-address keys must (1) retain the full 256-bit SHA-256 digest — no
96-bit (24-hex) truncation, which floors a birthday collision at 2^48 and can
corrupt content-addressed merge keys; (2) fail closed on non-serializable
payload elements rather than silently coercing them via ``default=str``; and
(3) hash a canonical little-endian float64 byte layout so digests are identical
across little-endian platforms and deterministic on big-endian ones.
"""

from __future__ import annotations

import hashlib

import numpy as np
import pytest

from algebra.rotor import make_rotor_from_angle
from core.physics.cognitive_lifecycle import (
    _content_id as lifecycle_content_id,
    _le_f64_bytes,
    _psi_digest,
)
from core.physics.biography_wiring import _content_id as biography_content_id
from core.physics.self_authorship import _content_id as authorship_content_id

_CONTENT_ID_FUNCS = (
    lifecycle_content_id,
    biography_content_id,
    authorship_content_id,
)


def _sample_psi() -> np.ndarray:
    return np.ascontiguousarray(make_rotor_from_angle(0.7, 6), dtype=np.float64)


# --- Mandate 4: full 256-bit digests (no 96-bit truncation) -----------------------


@pytest.mark.parametrize("content_id", _CONTENT_ID_FUNCS)
def test_content_id_is_full_256_bit_hex(content_id) -> None:
    digest = content_id({"a": 1, "b": ["x", 2.0], "c": True})
    assert len(digest) == 64
    int(digest, 16)  # valid lowercase hex


def test_psi_digest_is_full_256_bit_hex() -> None:
    digest = _psi_digest(_sample_psi())
    assert len(digest) == 64
    int(digest, 16)


def test_full_digest_extends_the_old_truncated_prefix() -> None:
    """The widening is an un-truncation, not a different hash: the old 24-hex
    form is exactly the 64-hex digest's prefix (same underlying bytes)."""
    psi = _sample_psi()
    full = _psi_digest(psi)
    legacy_prefix = hashlib.sha256(_le_f64_bytes(psi)).hexdigest()[:24]
    assert full[:24] == legacy_prefix


# --- Mandate 4: fail closed on silent coercion ------------------------------------


@pytest.mark.parametrize("content_id", _CONTENT_ID_FUNCS)
def test_content_id_fails_closed_on_non_serializable(content_id) -> None:
    class _Opaque:
        pass

    with pytest.raises(TypeError):
        content_id({"bad": _Opaque()})


@pytest.mark.parametrize("content_id", _CONTENT_ID_FUNCS)
def test_content_id_is_deterministic(content_id) -> None:
    payload = {"k": "v", "n": 3, "xs": [1, 2, 3]}
    assert content_id(payload) == content_id(dict(payload))


# --- Mandate 5: canonical little-endian byte-order contract -----------------------


def test_le_bytes_are_byte_order_canonical() -> None:
    """A native-endian array and an explicit big-endian-dtype array carrying the
    same values must hash identically — the coercion, not the platform, decides
    the bytes."""
    psi = _sample_psi()
    native = np.ascontiguousarray(psi, dtype=np.float64)
    big_endian = native.astype(np.dtype(">f8"))
    assert _le_f64_bytes(native) == _le_f64_bytes(big_endian)
    assert _psi_digest(native) == _psi_digest(big_endian)


def test_le_bytes_match_explicit_little_endian_layout() -> None:
    psi = _sample_psi()
    expected = np.ascontiguousarray(psi, dtype=np.dtype("<f8")).tobytes()
    assert _le_f64_bytes(psi) == expected
    assert len(_le_f64_bytes(psi)) == 32 * 8  # 32 float64 components
