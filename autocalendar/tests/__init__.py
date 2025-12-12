"""
autocalendar package.

Public API is re-exported here for convenient imports.
No business logic and no side-effects on import.
"""

from __future__ import annotations

__all__ = [
    "__version__",
    "parse_event_title",
]

__version__ = "0.1.0"

# Re-export public functions (thin wrapper)
from autocalendar.parsing import parse_event_title
