"""
core/meta_verification/report.py
"""

import json
from pathlib import Path
from .result import MetaVerificationResult


def write_meta_report(result: MetaVerificationResult, out_dir: str) -> None:
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    md_path = out_path / f"META_VERIFICATION_{result.phase.upper()}.md"
    json_path = out_path / f"meta_verification_{result.phase.lower()}.json"

    lines = []
    lines.append("# META VERIFICATION REPORT")
    lines.append("")
    lines.append(f"**Phase:** `{result.phase}`")
    lines.append(f"**Passed:** `{result.passed}`")
    lines.append(f"**Integrity Score:** `{result.integrity_score:.2f}%`")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| Check | Status | Severity | Message |")
    lines.append("| --- | --- | --- | --- |")

    for check in result.checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(
            f"| {check.name} | {status} | {check.severity} | {check.message} |"
        )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    payload = {
        "phase": result.phase,
        "passed": result.passed,
        "integrity_score": result.integrity_score,
        "checks": [
            {
                "name": c.name,
                "passed": c.passed,
                "severity": c.severity,
                "message": c.message,
                "details": c.details,
            }
            for c in result.checks
        ],
    }

    json_path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
