from __future__ import annotations

from collections import Counter
from pathlib import Path

from agentpreflight.models import ScanResult

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def render(result: ScanResult) -> str:
    counts = Counter(f.severity for f in result.findings)
    status = "PASS" if result.verdict == "pass" else "FAIL" if result.verdict == "fail" else "WARN"
    lines = [
        "## AgentPreflight Scan Scorecard",
        "",
        "| Target | Verdict | Trust score | Findings |",
        "|---|---:|---:|---:|",
        f"| `{Path(result.target).name or result.target}` | **{status}** | **{result.trust_score} / 100** | **{len(result.findings)}** |",
        "",
        "### Summary",
        "",
        f"- Critical: {counts.get('critical', 0)}",
        f"- High: {counts.get('high', 0)}",
        f"- Medium: {counts.get('medium', 0)}",
        f"- Low: {counts.get('low', 0)}",
    ]
    suppressed = result.summary.get("suppressed", 0)
    if suppressed:
        lines.append(f"- Suppressed: {suppressed}")
    if result.findings:
        lines.extend(["", "### Top findings", ""])
        ordered = sorted(
            result.findings,
            key=lambda f: SEVERITY_ORDER.get(f.severity, len(SEVERITY_ORDER)),
        )
        for finding in ordered[:15]:
            location = Path(finding.path).name
            if finding.line:
                location = f"{location}:{finding.line}"
            lines.append(f"- **{finding.severity.upper()}** `{finding.id}` `{location}` - {finding.title}")
    if any(f.fix_available for f in result.findings):
        lines.extend([
            "",
            "### Remediation",
            "",
            "`agentpreflight fix <target> --apply` can sanitize supported findings locally, then rescan for proof.",
        ])
    return "\n".join(lines) + "\n"
