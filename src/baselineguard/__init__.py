"""BaselineGuard - offline Web platform Baseline guard for human and AI authors.

Zero third-party dependencies. Standard library only. Python 3.9+.
"""

__version__ = "1.0.0"
__all__ = ["__version__"]

STATUSES = ("widely", "newly", "limited", "deprecated")
SEVERITIES = ("error", "warning", "info")
SCANNABLE_CATEGORIES = ("css", "markup", "script")
