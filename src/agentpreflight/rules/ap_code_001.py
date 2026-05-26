"""AP-CODE-001: Unsafe shell execution — os.system or subprocess shell=True."""
from __future__ import annotations
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_PATTERNS = [
    (re.compile(r'\bos\.system\s*\('), "os.system() call"),
    (re.compile(r'\bsubprocess\.\w+\s*\([^)]*shell\s*=\s*True'), "subprocess with shell=True"),
    (re.compile(r'\bcommands\.getoutput\s*\('), "commands.getoutput() call"),
]


class UnsafeShellRule(Rule):
    id = "AP-CODE-001"
    severity = "critical"
    category = "unsafe_exec"
    applies_to = {"code_py", "code_js", "code_sh"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern, label in _PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Unsafe shell execution",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"{label}: {line.strip()[:120]}",
                        risk="User or model-controlled input reaching unsafe shell execution enables arbitrary command injection.",
                        fix="Replace shell string execution with argument-list form. Never pass shell=True with untrusted input.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP A03 Injection", "CWE-78"],
                    ))
        return findings
