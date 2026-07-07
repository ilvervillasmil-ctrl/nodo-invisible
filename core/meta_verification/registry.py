"""
core/meta_verification/registry.py

Registro central de auditorías.
"""

from collections.abc import Callable
from .result import MetaCheckResult


MetaAuditFunction = Callable[[str], MetaCheckResult]


class MetaAuditRegistry:
    def __init__(self):
        self._audits: list[MetaAuditFunction] = []

    def register(self, audit: MetaAuditFunction) -> None:
        self._audits.append(audit)

    def run_all(self, root: str) -> list[MetaCheckResult]:
        results = []

        for audit in self._audits:
            try:
                result = audit(root)
                results.append(result)
            except Exception as exc:
                results.append(
                    MetaCheckResult(
                        name=getattr(audit, "__name__", "unknown_audit"),
                        passed=False,
                        severity="ERROR",
                        message=f"Audit crashed: {exc}",
                        details={"exception": repr(exc)},
                    )
                )

        return results
