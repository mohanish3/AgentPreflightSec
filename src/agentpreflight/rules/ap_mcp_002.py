"""AP-MCP-002: Hidden Unicode control characters in MCP tool descriptions and skill text."""
from __future__ import annotations

import json

from agentpreflight.models import Artifact, Finding
from agentpreflight.normalizers.unicode import SUSPICIOUS_CONTROLS
from agentpreflight.rules.engine import Rule


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


class HiddenUnicodeInDescriptionRule(Rule):
    id = "AP-MCP-002"
    severity = "high"
    category = "tool_poisoning"
    applies_to = {"mcp_config", "skill_md"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings = []
        
        # Check MCP tool descriptions via JSON parsing
        tool_descs = _extract_tool_descriptions(artifact.content)
        for _line, tool_name, description in tool_descs:
            found_chars = [char for char in description if char in SUSPICIOUS_CONTROLS]
            if found_chars:
                evidence_parts = []
                for char in found_chars:
                    codepoint = ord(char)
                    evidence_parts.append(f"U+{codepoint:04X} ({repr(char)})")
                evidence = f"Tool '{tool_name}' description contains hidden Unicode: {', '.join(evidence_parts)}"
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Hidden Unicode in MCP tool description",
                    path=artifact.path,
                    line=None,
                    evidence=evidence,
                    risk="Hidden Unicode control characters can conceal malicious instructions from code review and confuse model interpretation.",
                    fix="Remove zero-width and bidi override characters from tool descriptions.",
                    fix_available=True,
                    fix_mode="local_sanitize",
                    references=["OWASP Agentic AI Security", "CWE-838", "MCPTox"],
                ))

        # Also check skill_md files for hidden unicode in skill text (not just JSON parsed)
        if artifact.kind == "skill_md":
            for lineno, line in enumerate(artifact.content.splitlines(), 1):
                found_chars = [char for char in line if char in SUSPICIOUS_CONTROLS]
                if found_chars:
                    evidence_parts = []
                    for char in found_chars:
                        codepoint = ord(char)
                        evidence_parts.append(f"U+{codepoint:04X} ({repr(char)})")
                    evidence = f"Skill text on line {lineno} contains hidden Unicode: {', '.join(evidence_parts)}"
                    findings.append(Finding(
                        id=self.id,
                        severity=self.severity,
                        category=self.category,
                        title="Hidden Unicode in skill instruction text",
                        path=artifact.path,
                        line=lineno,
                        evidence=evidence,
                        risk="Hidden Unicode control characters can conceal malicious instructions from code review.",
                        fix="Remove zero-width and bidi override characters from skill text.",
                        fix_available=True,
                        fix_mode="local_sanitize",
                        references=["OWASP Agentic AI Security", "CWE-838"],
                    ))

        return findings
