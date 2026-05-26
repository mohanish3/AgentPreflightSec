"""AP-SKILL-002: Hidden Unicode instruction risk."""
from __future__ import annotations

from agentpreflight.models import Artifact, Finding
from agentpreflight.normalizers.unicode import SUSPICIOUS_CONTROLS
from agentpreflight.rules.engine import Rule


class HiddenUnicodeRule(Rule):
    id = "AP-SKILL-002"
    severity = "high"
    category = "tool_poisoning"
    applies_to = {"skill_md", "markdown", "mcp_config", "config"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if any(char in SUSPICIOUS_CONTROLS for char in line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Hidden Unicode control character",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Suspicious non-printing Unicode controls on line {lineno}",
                    risk="Hidden Unicode can conceal model-facing instructions from code review.",
                    fix="Remove zero-width and bidi control characters. Keep model-facing text visible.",
                    fix_available=True,
                    fix_mode="local_sanitize",
                    references=["OWASP Agentic AI Security", "CWE-838"],
                ))
        return findings
