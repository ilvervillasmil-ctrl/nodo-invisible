"""
core/meta_verification/engine.py

Orquestador maestro.

No calcula coherencia.
No clasifica estados.
No importa engine.py.
No importa diagnostics.py.

Solo verifica integridad estructural antes/después de tests.
"""

from pathlib import Path

from .constants import verify_alpha_beta
from .registry import MetaAuditRegistry
from .result import MetaCheckResult, MetaVerificationResult
from .report import write_meta_report


class MetaVerificationEngine:
    def __init__(self, root: str = ".", phase: str = "pre", out: str = "diagnostics"):
        self.root = str(Path(root).resolve())
        self.phase = phase
        self.out = out
        self.registry = MetaAuditRegistry()

        self._register_builtin_audits()

    def _register_builtin_audits(self) -> None:
        self.registry.register(self._audit_alpha_beta)
        self.registry.register(self._audit_repository_exists)
        self.registry.register(self._audit_tests_folder_exists)
        self.registry.register(self._audit_python_files_exist)

    def run(self) -> MetaVerificationResult:
        checks = self.registry.run_all(self.root)

        passed = all(check.passed for check in checks)

        result = MetaVerificationResult(
            phase=self.phase,
            passed=passed,
            checks=checks,
        )

        write_meta_report(result, self.out)

        if not result.passed:
            failed = "\n".join(
                f"- {c.name}: {c.message}" for c in result.failed_checks
            )
            raise RuntimeError(
                "META VERIFICATION FAILED\n"
                f"{failed}"
            )

        return result

    # ========================================================
    # BUILTIN AUDITS
    # ========================================================

    @staticmethod
    def _audit_alpha_beta(root: str) -> MetaCheckResult:
        ok = verify_alpha_beta()

        return MetaCheckResult(
            name="alpha_beta_integrity",
            passed=ok,
            severity="CRITICAL" if not ok else "INFO",
            message="ALPHA/BETA invariants valid."
            if ok else
            "ALPHA/BETA invariant violation.",
        )

    @staticmethod
    def _audit_repository_exists(root: str) -> MetaCheckResult:
        path = Path(root)

        ok = path.exists() and path.is_dir()

        return MetaCheckResult(
            name="repository_exists",
            passed=ok,
            severity="CRITICAL" if not ok else "INFO",
            message=f"Repository root found: {path}"
            if ok else
            f"Repository root not found: {path}",
        )

    @staticmethod
    def _audit_tests_folder_exists(root: str) -> MetaCheckResult:
        tests = Path(root) / "tests"

        ok = tests.exists() and tests.is_dir()

        return MetaCheckResult(
            name="tests_folder_exists",
            passed=ok,
            severity="CRITICAL" if not ok else "INFO",
            message="tests/ folder found."
            if ok else
            "tests/ folder not found.",
            details={"path": str(tests)},
        )

    @staticmethod
    def _audit_python_files_exist(root: str) -> MetaCheckResult:
        path = Path(root)
        py_files = list(path.rglob("*.py"))

        ok = len(py_files) > 0

        return MetaCheckResult(
            name="python_files_exist",
            passed=ok,
            severity="CRITICAL" if not ok else "INFO",
            message=f"{len(py_files)} Python files found."
            if ok else
            "No Python files found.",
            details={"count": len(py_files)},
        )
