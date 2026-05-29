from __future__ import annotations
from abc import ABC, abstractmethod
from collections import defaultdict

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
        # Pre-bucket rules by artifact kind to avoid O(rules) scan per artifact.
        # Rules with "*" in applies_to run against every artifact kind.
        self._by_kind: dict[str, list[Rule]] = defaultdict(list)
        self._star_rules: list[Rule] = []
        for rule in rules:
            if "*" in rule.applies_to:
                self._star_rules.append(rule)
            else:
                for kind in rule.applies_to:
                    self._by_kind[kind].append(rule)

    def run(self, artifacts: list[Artifact]) -> list[Finding]:
        findings: list[Finding] = []
        for artifact in artifacts:
            applicable = self._by_kind.get(artifact.kind, []) + self._star_rules
            for rule in applicable:
                findings.extend(rule.check(artifact))
        return findings
