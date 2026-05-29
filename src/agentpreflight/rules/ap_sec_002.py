"""AP-SEC-002 and AP-SEC-003: token patterns and committed env files."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_TOKEN_PATTERNS = [
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),           # OpenAI
    re.compile(r"\bsk-ant-[A-Za-z0-9_-]{40,}"),        # Anthropic
    re.compile(r"\bghp_[A-Za-z0-9_]{20,}"),            # GitHub personal token
    re.compile(r"\bgho_[A-Za-z0-9_]{20,}"),            # GitHub OAuth
    re.compile(r"\bghs_[A-Za-z0-9_]{20,}"),            # GitHub server-to-server
    re.compile(r"\b(xox[baprs]-[A-Za-z0-9-]{20,})"),  # Slack
    re.compile(r"\bAKIA[A-Z0-9]{16}\b"),               # AWS access key ID
    re.compile(r"\bAIza[A-Za-z0-9_-]{35,}\b"),         # Google API key
    re.compile(r"(?i)\b(api[_-]?key|secret|token|password)\s*=\s*['\"]?[A-Za-z0-9_\-./+=]{16,}"),
]


class ApiTokenRule(Rule):
    id = "AP-SEC-002"
    severity = "high"
    category = "secrets"
    applies_to = {"*"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if any(pattern.search(line) for pattern in _TOKEN_PATTERNS):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="API token pattern in file",
                    path=artifact.path,
                    line=lineno,
                    evidence="Secret-like token pattern detected",
                    risk="Committed tokens can be used to access external services or customer data.",
                    fix="Remove token, rotate it, and load secrets from a secret manager or local environment.",
                    fix_available=True,
                    fix_mode="local_redact",
                    references=["CWE-798", "OWASP A02 Cryptographic Failures"],
                ))
        return findings


class EnvFileRule(Rule):
    id = "AP-SEC-003"
    severity = "medium"
    category = "secrets"
    applies_to = {"env_file"}

    def check(self, artifact: Artifact) -> list[Finding]:
        return [Finding(
            id=self.id,
            severity=self.severity,
            category=self.category,
            title="Committed environment file",
            path=artifact.path,
            line=1,
            evidence="Environment file included in scan target",
            risk="Environment files often contain credentials that should not be committed or shared.",
            fix="Move secrets to local environment or secret manager. Commit only .env.example.",
            fix_available=True,
            fix_mode="local_rename",
            references=["CWE-526"],
        )]
