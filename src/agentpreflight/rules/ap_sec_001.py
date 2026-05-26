"""AP-SEC-001: Private key material in source or config."""
from __future__ import annotations
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_PATTERNS = [
    re.compile(r'-----BEGIN (RSA |EC |OPENSSH |DSA |PGP )?PRIVATE KEY( BLOCK)?-----'),
    re.compile(r'-----BEGIN ENCRYPTED PRIVATE KEY-----'),
]


class PrivateKeyRule(Rule):
    id = "AP-SEC-001"
    severity = "critical"
    category = "secrets"
    applies_to = {"*"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            for pattern in _PATTERNS:
                if pattern.search(line):
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Private key material in file",
                        path=artifact.path,
                        line=lineno,
                        evidence="PEM private key block detected",
                        risk="Private key committed to source gives any reader full identity/signing capability.",
                        fix="Remove key from source. Rotate immediately. Use secrets manager or environment variable.",
                        fix_available=False,
                        references=["CWE-321", "OWASP A02 Cryptographic Failures"],
                    ))
                    break
        return findings
