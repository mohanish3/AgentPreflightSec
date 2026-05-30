"""AP-CODE-003: Remote script execution — curl|sh, wget|bash patterns."""
from __future__ import annotations
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_PATTERNS = [
    re.compile(r'curl\s+[^\|]*\|\s*(ba)?sh', re.IGNORECASE),
    re.compile(r'wget\s+[^\|]*\|\s*(ba)?sh', re.IGNORECASE),
    re.compile(r'curl\s+[^\|]*\|\s*python', re.IGNORECASE),
    re.compile(r'curl\s+[^\|]*-\s*\|\s*(ba)?sh', re.IGNORECASE),
]


class RemoteScriptExecRule(Rule):
    id = "AP-CODE-003"
    severity = "critical"
    category = "unsafe_exec"
    applies_to = {"code_py", "code_js", "code_sh", "markdown", "skill_md", "config", "other"}
    description = "Remote script execution — curl/wget piped directly to shell without integrity check."
    remediation = "Download to a file, verify checksum, review content before executing."
    references = ["OWASP A08 Software Integrity Failures", "CWE-494"]

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern in _PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category="unsafe_exec",
                        title="Remote script execution",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"Remote pipe: {line.strip()[:120]}",
                        risk="Downloaded code executed directly with no integrity check. Attacker controls arbitrary code execution.",
                        fix="Download to a file, verify checksum, review content before executing.",
                        fix_available=True,
                        fix_mode="local_sanitize",
                        references=["OWASP A08 Software Integrity Failures", "CWE-494"],
                    ))
                    break
        return findings
