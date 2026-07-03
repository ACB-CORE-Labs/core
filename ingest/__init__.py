"""Runtime injection gate for raw field construction.

See ``ingest/README.md`` for the boundary between runtime injection,
``core_ingest`` candidate-pressure validation, and reviewed teaching mutation.
"""

from .gate import inject as inject

__all__ = ["inject"]
