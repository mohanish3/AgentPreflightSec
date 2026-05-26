"""AP-CODE-002: Dynamic code execution."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_PATTERNS = [
    (re.compile(r"\beval\s*\("), "eval() call"),
    (re.compile(r"\bexec\s*\("), "exec() call"),
    (re.compile(r"\bFunction\s*\("), "Function constructor"),
]


class DynamicCodeExecRule(Rule):
    id = "AP-CODE-002"
    severity = "high"
    category = "unsafe_exec"
    applies_to = {"code_py", "code_js"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Dynamic code execution",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="Model or user-controlled text can become executable code.",
                        fix="Replace dynamic execution with explicit dispatch or parsed data.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["CWE-94", "OWASP A03 Injection"],
                    ))
                    break
        return findings
