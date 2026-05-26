"""Additional agent skill instruction rules."""
from __future__ import annotations

import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


class SkillRemoteDependencyRule(Rule):
    id = "AP-SKILL-003"
    severity = "medium"
    category = "tool_poisoning"
    applies_to = {"skill_md", "markdown"}

    _pattern = re.compile(r"\b(fetch|download|follow|load|read).{0,40}(https?://|remote|url)\b|https?://", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            if self._pattern.search(line):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Remote instruction dependency",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Remote dependency: {line.strip()[:120]}",
                    risk="Remote instructions can change after review and deliver new model-facing payloads.",
                    fix="Pin reviewed local instructions or use signed, allowlisted remote sources.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-SKILL-003"],
                ))
        return findings


class SkillCredentialSeekingRule(Rule):
    id = "AP-SKILL-004"
    severity = "high"
    category = "secrets"
    applies_to = {"skill_md", "markdown"}

    _pattern = re.compile(r"\b(env vars?|tokens?|api keys?|keychain|cookies?|ssh keys?|credentials?|auth files?)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            match = self._pattern.search(line)
            if match:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Credential-seeking skill instruction",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Credential reference: {match.group(0)}",
                    risk="Skills that request secrets can steer agents into credential disclosure or exfiltration.",
                    fix="Remove secret access from instructions or document exact least-privilege secret names.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-SKILL-004"],
                ))
        return findings


class SkillCapabilityMismatchRule(Rule):
    id = "AP-SKILL-005"
    severity = "medium"
    category = "capability_mismatch"
    applies_to = {"skill_md", "markdown"}

    _narrow = re.compile(r"\b(summarize|format|translate|lint|review text|documentation only)\b", re.I)
    _power = re.compile(r"\b(shell|subprocess|delete files|write files|network request|curl|wget|execute)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        text = re.sub(r"\bdo not execute commands?\b", "", artifact.content, flags=re.I)
        if not (self._narrow.search(text) and self._power.search(text)):
            return []
        return [Finding(
            id=self.id,
            severity=self.severity,
            category=self.category,
            title="Skill capability mismatch",
            path=artifact.path,
            evidence="Narrow skill description coexists with shell/filesystem/network capability language",
            risk="Capability mismatch hides privileged behavior behind benign skill positioning.",
            fix="Align stated capability with actual behavior or split privileged operations into reviewed tools.",
            fix_available=True,
            fix_mode="codex_patch",
            references=["AP-SKILL-005"],
        )]
