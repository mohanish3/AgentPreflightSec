"""AP-SKILL-002: Hidden Unicode instruction risk."""
from __future__ import annotations

from agentpreflight.models import Artifact, Finding
from agentpreflight.normalizers.unicode import SUSPICIOUS_CONTROLS
from agentpreflight.rules.engine import Rule


class HiddenUnicodeRule(Rule):
    id = "AP-SKILL-002"
    severity = "high"
    category = "tool_poisoning"
    # code_py/js/sh included for Trojan Source (CVE-2021-42574): bidi overrides
    # in source make code appear different to humans than to the interpreter.
    applies_to = {"skill_md", "markdown", "mcp_config", "config", "code_py", "code_js", "code_sh", "env_file"}
    description = "Hidden Unicode control characters (zero-width, bidi) that conceal model-facing instructions from code review."
    remediation = "Remove zero-width and bidi control characters. Keep all model-facing text visible."
    references = ["CVE-2021-42574", "OWASP Agentic AI Security", "CWE-838"]

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
                    risk="Hidden Unicode can conceal model-facing instructions from code review (Trojan Source, CVE-2021-42574).",
                    fix="Remove zero-width and bidi control characters. Keep model-facing text visible.",
                    fix_available=True,
                    fix_mode="local_sanitize",
                    references=["CVE-2021-42574", "OWASP Agentic AI Security", "CWE-838"],
                ))
        return findings
