"""AP-CODE-006: Remote fetch and execute — curl/wget piped to shell, eval of remote content."""
from __future__ import annotations
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_PATTERNS = [
    # curl ... | sh patterns (including variants like ba)sh
    re.compile(r'curl\s+[^\|]*\|\s*(ba)?sh', re.IGNORECASE),
    re.compile(r'wget\s+[^\|]*\|\s*(ba)?sh', re.IGNORECASE),
    # eval with command substitution fetching remote content
    re.compile(r'eval\s+(?:["\']?\$?\(\s*(?:curl|wget)[^\)]+\))', re.IGNORECASE),
    # Python exec with remote content via requests
    re.compile(r'exec\s*\(\s*(?:requests\.get\([^)]+\)|urllib\.request\.urlopen\([^)]+\))\s*\.\s*(?:text|read)', re.IGNORECASE),
]


class RemoteFetchExecRule(Rule):
    id = "AP-CODE-006"
    severity = "high"
    category = "remote_exec"
    applies_to = {"code_py", "code_js", "skill_md", "markdown", "other"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern in _PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Remote fetch and execute",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"Remote fetch and execute: {line.strip()[:120]}",
                        risk="Downloaded content executed directly without integrity verification. Attacker can inject arbitrary code via network.",
                        fix="Download to a file first, verify checksum, review content, and use a whitelist of trusted sources.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["Snyk ToxicSkills", "AP-CODE-006", "CWE-494"],
                    ))
                    break
        return findings
