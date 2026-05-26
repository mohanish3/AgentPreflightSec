"""Additional code/dataflow heuristic rules."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


class ArbitraryFileAccessRule(Rule):
    id = "AP-CODE-004"
    severity = "high"
    category = "unsafe_file_access"
    applies_to = {"code_py", "code_js", "code_sh"}

    _pattern = re.compile(
        r"\b(open|Path\s*\([^)]*\)\.read_text|readFileSync|writeFileSync|fs\.(readFile|writeFile))\s*\([^)]*(user_input|request|req\.|args|argv|input)",
        re.I,
    )

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if self._pattern.search(line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Unvalidated file path access",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"File access with user/model-controlled path: {line.strip()[:120]}",
                    risk="Unvalidated paths can read or overwrite arbitrary files via traversal or model-controlled input.",
                    fix="Use allowlisted roots, path normalization, and explicit filename validation.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["CWE-22", "AP-CODE-004"],
                ))
        return findings


class NetworkExfiltrationRule(Rule):
    id = "AP-CODE-005"
    severity = "high"
    category = "network_egress"
    applies_to = {"code_py", "code_js", "code_sh"}

    _secret = re.compile(r"\b(os\.environ|getenv|process\.env|\.env|secret|token|api_key|password)\b", re.I)
    _network = re.compile(r"\b(requests\.(post|put)|httpx\.(post|put)|fetch\s*\(|axios\.(post|put)|curl\s+(-X\s+)?POST)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        lines = artifact.content.splitlines()
        has_secret = any(self._secret.search(line) for line in lines)
        has_network = any(self._network.search(line) for line in lines)
        if not (has_secret and has_network):
            return []
        line_no = next((idx for idx, line in enumerate(lines, 1) if self._network.search(line)), 1)
        return [Finding(
            id=self.id,
            severity=self.severity,
            category=self.category,
            title="Potential network exfiltration primitive",
            path=artifact.path,
            line=line_no,
            evidence="Secret/env access and outbound network write appear in same artifact",
            risk="A tool can collect local secrets and transmit them to external services.",
            fix="Separate secret access from network egress, add allowlisted destinations, and redact sensitive values.",
            fix_available=False,
            references=["CWE-200", "AP-CODE-005"],
        )]
