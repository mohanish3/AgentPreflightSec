"""AP-MCP-001: Prompt override phrases in MCP tool descriptions."""
from __future__ import annotations
import json
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule

_OVERRIDE_PHRASES = re.compile(
    r'\b('
    r'ignore (previous|prior|all) instructions?|'
    r'system override|'
    r'developer message|'
    r'urgent bypass|'
    r'exfiltrate|'
    r'reveal (secrets?|credentials?|keys?|tokens?)|'
    r'you (are|must|should) now|'
    r'hidden (instruction|priority|directive)|'
    r'override (all|previous|system)|'
    r'new (system )?prompt|'
    r'disregard (all|previous)|'
    r'maintenance (instruction|mode)|'
    r'administrator mode'
    r')',
    re.IGNORECASE,
)


def _extract_tool_descriptions(content: str) -> list[tuple[int, str, str]]:
    """Return list of (line_hint, tool_name, description) from MCP JSON."""
    try:
        data = json.loads(content)
    except (json.JSONDecodeError, ValueError):
        return []

    results = []
    tools = []
    if isinstance(data, dict):
        tools = data.get("tools", [])
        if not tools and "mcpServers" in data:
            # Claude Desktop format — no tool descriptions to check at config level
            return []

    for tool in tools:
        if isinstance(tool, dict):
            desc = tool.get("description", "")
            name = tool.get("name", "unknown")
            if desc:
                results.append((0, name, desc))
    return results


class McpPromptOverrideRule(Rule):
    id = "AP-MCP-001"
    severity = "high"
    category = "tool_poisoning"
    applies_to = {"mcp_config"}
    description = "Prompt-override phrases in MCP tool descriptions that hijack agent behavior."
    remediation = "Rewrite tool description as neutral capability text. Remove instruction-like language."
    references = ["OWASP MCP Tool Poisoning", "MCPTox"]

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        tool_descs = _extract_tool_descriptions(artifact.content)
        for _line, tool_name, description in tool_descs:
            match = _OVERRIDE_PHRASES.search(description)
            if match:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Prompt-like override in MCP tool description",
                    path=artifact.path,
                    line=None,
                    evidence=f"Tool '{tool_name}' description contains: \"{match.group(0)[:80]}\"",
                    risk="Model may treat untrusted tool metadata as instruction, hijacking agent behavior before runtime guardrails.",
                    fix="Rewrite tool description as neutral capability text. Remove instruction-like language.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["OWASP MCP Tool Poisoning", "MCPTox", "AP-MCP-001"],
                ))

        # Also scan raw text for files that failed JSON parse
        if not tool_descs:
            for lineno, line in enumerate(artifact.content.splitlines(), 1):
                if _OVERRIDE_PHRASES.search(line):
                    match = _OVERRIDE_PHRASES.search(line)
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Prompt-like override in MCP config",
                        path=artifact.path,
                        line=lineno,
                        evidence=f"Override phrase: \"{match.group(0)[:80]}\"",
                        risk="Prompt override language in tool metadata can hijack agent behavior.",
                        fix="Rewrite as neutral capability text.",
                        fix_available=True,
                        fix_mode="codex_patch",
                        references=["OWASP MCP Tool Poisoning"],
                    ))
        return findings
