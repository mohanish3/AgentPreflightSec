"""AP-SKILL-001: Prompt injection language in SKILL.md."""
from __future__ import annotations
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_INJECTION_PHRASES = re.compile(
    r'\b('
    r'ignore (previous|prior|all) instructions?|'
    r'override (all|previous|system|the )?instructions?|'
    r'hidden (priority|instruction|directive)|'
    r'bypass (safety|guardrail|policy|restriction)|'
    r'(you are|act as) (now )?a[n]? (different|uncensored|jailbroken|unfiltered)|'
    r'do not (follow|obey|adhere to)|'
    r'secret (instruction|directive|mode)|'
    r'disregard (previous|all|the )?instructions?|'
    r'system (prompt|instruction) override|'
    r'priority override|'
    r'new persona|'
    r'forget (your|all) (previous )?instructions?'
    r')',
    re.IGNORECASE,
)


class SkillPromptInjectionRule(Rule):
    id = "AP-SKILL-001"
    severity = "high"
    category = "tool_poisoning"
    applies_to = {"skill_md", "markdown"}
    description = "Prompt injection language in SKILL.md — override/bypass phrases that hijack agent behavior at load time."
    remediation = "Remove instruction-hierarchy manipulation. Rewrite as plain capability description."
    references = ["OWASP Agentic AI Security", "OWASP LLM01"]

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        for lineno, line in enumerate(artifact.content.splitlines(), 1):
            match = _INJECTION_PHRASES.search(line)
            if match:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Prompt injection language in skill instructions",
                    path=artifact.path,
                    line=lineno,
                    evidence=f"Injection phrase: \"{match.group(0)[:80]}\" — {line.strip()[:100]}",
                    risk="Skill instructions with override/bypass language can hijack agent behavior at load time.",
                    fix="Remove instruction-hierarchy manipulation. Rewrite as plain capability description.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["OWASP Agentic AI Security", "AP-SKILL-001"],
                ))
        return findings
