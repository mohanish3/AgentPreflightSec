"""Transport and local server hardening rules."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


class BroadBindRule(Rule):
    id = "AP-NET-001"
    severity = "high"
    category = "transport_hardening"
    applies_to = {"code_py", "code_js", "config", "mcp_config"}

    _pattern = re.compile(r"(host\s*[:=]\s*['\"]?0\.0\.0\.0|bind\s*\([^)]*0\.0\.0\.0|listen\s*\([^)]*0\.0\.0\.0|::)", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if self._pattern.search(line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Broad network bind",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Broad bind: {line.strip()[:120]}",
                    risk="Local tooling exposed beyond localhost increases DNS rebinding and LAN attack surface.",
                    fix="Bind to 127.0.0.1 by default and require explicit auth for remote access.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-NET-001"],
                ))
        return findings


class MissingOriginValidationRule(Rule):
    id = "AP-NET-002"
    severity = "high"
    category = "transport_hardening"
    applies_to = {"code_py", "code_js", "config", "mcp_config"}

    _pattern = re.compile(r"(allow_unauthenticated_localhost\s*[:=]\s*true|Access-Control-Allow-Origin['\"]?\s*[:,]\s*['\"]\*|cors\s*\(\s*\))", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if self._pattern.search(line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Missing origin validation",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Origin/auth bypass pattern: {line.strip()[:120]}",
                    risk="Local servers without Origin/Host/auth checks can be driven by malicious web pages.",
                    fix="Validate Origin and Host, require bearer token auth, and avoid wildcard CORS.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-NET-002"],
                ))
        return findings


class PlainHttpToolRule(Rule):
    id = "AP-NET-003"
    severity = "medium"
    category = "transport_hardening"
    applies_to = {"config", "mcp_config", "skill_md", "markdown"}

    _pattern = re.compile(r"http://(?!127\.0\.0\.1|localhost)", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if self._pattern.search(line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Plain HTTP remote tool URL",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Plain HTTP URL: {line.strip()[:120]}",
                    risk="Remote tool traffic over HTTP can be intercepted or modified before agent use.",
                    fix="Use HTTPS or a pinned local transport.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-NET-003"],
                ))
        return findings
