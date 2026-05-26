from __future__ import annotations
from abc import ABC, abstractmethod

from agentpreflight.models import Artifact, Finding


class Rule(ABC):
    id: str
    severity: str
    category: str
    applies_to: set[str]

    @abstractmethod
    def check(self, artifact: Artifact) -> list[Finding]:
        ...


class RuleEngine:
    def __init__(self, rules: list[Rule]) -> None:
        self._rules = rules

    def run(self, artifacts: list[Artifact]) -> list[Finding]:
        findings: list[Finding] = []
        for artifact in artifacts:
            for rule in self._rules:
                if artifact.kind in rule.applies_to or "*" in rule.applies_to:
                    findings.extend(rule.check(artifact))
        return findings
