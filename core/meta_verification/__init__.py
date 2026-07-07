"""
Core Meta Verification Layer.

Auditor interno independiente.
Solo conoce dos axiomas:

    ALPHA = 26/27
    BETA  = 1/27
"""

from .engine import MetaVerificationEngine
from .constants import ALPHA, BETA

__all__ = [
    "MetaVerificationEngine",
    "ALPHA",
    "BETA",
]
