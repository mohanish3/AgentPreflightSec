"""Additional MCP metadata risk rules."""
from __future__ import annotations

import json
import re

from agentpreflight.models import Artifact, Finding
from agentpreflight.rules.engine import Rule


def _load(content: str):
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return None
    return data if isinstance(data, dict) else None


def _tools(artifact: Artifact) -> list[dict]:
    data = _load(artifact.content)
    if not data or not isinstance(data.get("tools"), list):
        return []
    return [tool for tool in data["tools"] if isinstance(tool, dict)]


class McpTrustClaimRule(Rule):
    id = "AP-MCP-002"
    severity = "medium"
    category = "tool_poisoning"
    applies_to = {"mcp_config"}

    _pattern = re.compile(r"\b(always safe|fully trusted|guaranteed safe|verified secure|no review needed)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for tool in _tools(artifact):
            desc = str(tool.get("description", ""))
            match = self._pattern.search(desc)
            if match:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Unsupported trust claim in MCP tool description",
                    path=artifact.path,
                    evidence=f"Tool '{tool.get('name', 'unknown')}' claims: {match.group(0)}",
                    risk="Tool metadata can overstate safety and bias agent routing or reviewer judgment.",
                    fix="Remove broad trust claims. Describe concrete inputs, outputs, and limits.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-MCP-002"],
                ))
        return findings


class McpUntrustedResultRule(Rule):
    id = "AP-MCP-003"
    severity = "high"
    category = "tool_poisoning"
    applies_to = {"mcp_config"}

    _pattern = re.compile(r"\b(pass|send|forward|append).{0,40}(result|output|response).{0,40}(model|prompt|context)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for tool in _tools(artifact):
            desc = str(tool.get("description", ""))
            if self._pattern.search(desc):
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Tool result forwarded to model without boundary",
                    path=artifact.path,
                    evidence=f"Tool '{tool.get('name', 'unknown')}' describes direct model forwarding",
                    risk="Untrusted tool output can become prompt content without boundary marking.",
                    fix="Mark tool output as untrusted data and require summarization or escaping before model use.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-MCP-003"],
                ))
        return findings


class McpLooseSchemaRule(Rule):
    id = "AP-MCP-004"
    severity = "medium"
    category = "schema_hardening"
    applies_to = {"mcp_config"}

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for tool in _tools(artifact):
            schema = tool.get("inputSchema")
            loose = not isinstance(schema, dict)
            if isinstance(schema, dict):
                loose = schema.get("type") not in {"object", "string"} or (
                    schema.get("type") == "object"
                    and (
                        not schema.get("required")
                        or schema.get("additionalProperties") is not False
                    )
                )
            if loose:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Loose MCP input schema",
                    path=artifact.path,
                    evidence=f"Tool '{tool.get('name', 'unknown')}' lacks strict required fields/additionalProperties=false",
                    risk="Loose schemas let model-generated or attacker-influenced arguments reach privileged tool logic.",
                    fix="Declare required fields and set additionalProperties=false for object schemas.",
                    fix_available=True,
                    fix_mode="codex_patch",
                    references=["AP-MCP-004"],
                ))
        return findings


class McpPrivilegedToolRule(Rule):
    id = "AP-MCP-005"
    severity = "high"
    category = "privileged_access"
    applies_to = {"mcp_config"}

    _pattern = re.compile(r"\b(shell|terminal|execute command|environment variables|secrets|cookies|email|browser|http request)\b", re.I)

    def check(self, artifact: Artifact) -> list[Finding]:
        findings: list[Finding] = []
        for tool in _tools(artifact):
            text = f"{tool.get('name', '')} {tool.get('description', '')}"
            match = self._pattern.search(text)
            if match:
                findings.append(Finding(
                    id=self.id,
                    severity=self.severity,
                    category=self.category,
                    title="Privileged MCP tool exposed",
                    path=artifact.path,
                    evidence=f"Tool '{tool.get('name', 'unknown')}' references privileged capability: {match.group(0)}",
                    risk="Privileged tools need explicit auth, allowlists, and untrusted-context boundaries.",
                    fix="Restrict caller context, require confirmation/auth, and document least-privilege scope.",
                    fix_available=False,
                    references=["AP-MCP-005"],
                ))
        return findings
