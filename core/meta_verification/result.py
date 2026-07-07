"""
core/meta_verification/result.py
"""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetaCheckResult:
    name: str
    passed: bool
    message: str
    severity: str = "INFO"
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class MetaVerificationResult:
    phase: str
    passed: bool
    checks: list[MetaCheckResult] = field(default_factory=list)

    @property
    def failed_checks(self) -> list[MetaCheckResult]:
        return [c for c in self.checks if not c.passed]

    @property
    def passed_checks(self) -> list[MetaCheckResult]:
        return [c for c in self.checks if c.passed]

    @property
    def integrity_score(self) -> float:
        if not self.checks:
            return 0.0

        passed = len(self.passed_checks)
        total = len(self.checks)

        return 100.0 * passed / total
