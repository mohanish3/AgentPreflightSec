from __future__ import annotations

import json
import re
from pathlib import Path

from agentpreflight.models import Finding
from agentpreflight.normalizers.unicode import SUSPICIOUS_CONTROLS

_OVERRIDE_RE = re.compile(
    r"(?i)(ignore previous instructions|ignore all instructions|system override|developer message|urgent bypass|"
    r"exfiltrate|reveal secrets|hidden instruction|administrator mode|disregard previous instructions)"
)
_SKILL_RE = re.compile(
    r"(?i)(ignore previous instructions|override all instructions|bypass safety|hidden priority|secret directive|"
    r"disregard previous instructions|new persona|forget your previous instructions)"
)


def apply_local_fixes(findings: list[Finding], allowed_rules: set[str] | None = None) -> list[str]:
    changed: list[str] = []
    by_path: dict[str, list[Finding]] = {}
    for finding in findings:
        if allowed_rules and finding.id not in allowed_rules:
            continue
        if finding.id not in {
            "AP-MCP-001",
            "AP-MCP-002",
            "AP-MCP-003",
            "AP-MCP-004",
            "AP-SKILL-001",
            "AP-SKILL-002",
            "AP-SKILL-003",
            "AP-SKILL-004",
            "AP-SKILL-005",
            "AP-CODE-001",
            "AP-CODE-002",
            "AP-CODE-003",
            "AP-SEC-002",
            "AP-SEC-003",
        }:
            continue
        by_path.setdefault(finding.path, []).append(finding)

    for raw_path, path_findings in by_path.items():
        path = Path(raw_path)
        text = path.read_text(encoding="utf-8", errors="replace")
        fixed = text
        if any(f.id == "AP-SKILL-002" for f in path_findings):
            fixed = "".join(char for char in fixed if char not in SUSPICIOUS_CONTROLS)
        if any(f.id == "AP-SKILL-001" for f in path_findings):
            fixed = _SKILL_RE.sub("use normal documented behavior", fixed)
        if any(f.id in {"AP-SKILL-003", "AP-SKILL-004", "AP-SKILL-005"} for f in path_findings):
            fixed = _fix_skill_lines(fixed, path_findings)
        if any(f.id in {"AP-MCP-001", "AP-MCP-002", "AP-MCP-003", "AP-MCP-004"} for f in path_findings):
            fixed = _fix_mcp_text(fixed)
        if any(f.id in {"AP-CODE-001", "AP-CODE-002", "AP-CODE-003"} for f in path_findings):
            fixed = _fix_code_lines(fixed, path_findings)
        if any(f.id == "AP-SEC-002" for f in path_findings):
            fixed = _redact_tokens(fixed)
        if fixed != text:
            path.write_text(fixed, encoding="utf-8")
            changed.append(str(path))
        if any(f.id == "AP-SEC-003" for f in path_findings) and path.name.startswith(".env"):
            dest = path.with_name(".env.example")
            if path.exists():
                path.replace(dest)
                changed.append(f"{path} -> {dest}")
    return changed


def _fix_mcp_text(text: str) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return _OVERRIDE_RE.sub("perform documented tool behavior", text)
    if isinstance(data, dict) and isinstance(data.get("tools"), list):
        for tool in data["tools"]:
            if isinstance(tool, dict) and isinstance(tool.get("description"), str):
                tool["description"] = _OVERRIDE_RE.sub(
                    "perform documented tool behavior",
                    tool["description"],
                )
                tool["description"] = re.sub(
                    r"(?i)\b(always safe|fully trusted|guaranteed safe|verified secure|no review needed)\b",
                    "documented",
                    tool["description"],
                )
                tool["description"] = re.sub(
                    r"(?i)\b(pass|send|forward|append).{0,40}(result|output|response).{0,40}(model|prompt|context)\b",
                    "return structured data to caller",
                    tool["description"],
                )
            schema = tool.get("inputSchema")
            if isinstance(tool, dict) and isinstance(schema, dict) and schema.get("type") == "object":
                properties = schema.get("properties")
                if isinstance(properties, dict) and properties:
                    schema["required"] = list(properties.keys())
                schema["additionalProperties"] = False
        return json.dumps(data, indent=2) + "\n"
    return _OVERRIDE_RE.sub("perform documented tool behavior", text)


def _fix_skill_lines(text: str, findings: list[Finding]) -> str:
    target_lines = {finding.line for finding in findings if finding.line}
    out: list[str] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if idx in target_lines:
            indent = line[:len(line) - len(line.lstrip())]
            out.append(f"{indent}Use only reviewed local instructions and documented least-privilege inputs.")
        else:
            out.append(line)
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _fix_code_lines(text: str, findings: list[Finding]) -> str:
    target_lines = {finding.line for finding in findings if finding.line}
    out: list[str] = []
    for idx, line in enumerate(text.splitlines(), 1):
        if idx not in target_lines:
            out.append(line)
            continue
        indent = line[:len(line) - len(line.lstrip())]
        if "eval(" in line or "exec(" in line or "Function(" in line:
            out.append(f"{indent}raise ValueError(\"dynamic execution disabled by AgentPreflight\")")
        elif "curl" in line or "wget" in line:
            out.append(f"{indent}# AgentPreflight removed remote script execution")
        elif "os.system" in line or "shell=True" in line or "commands.getoutput" in line:
            out.append(f"{indent}# AgentPreflight removed unsafe shell execution")
        else:
            out.append(f"{indent}# AgentPreflight removed risky executable line")
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def _redact_tokens(text: str) -> str:
    patterns = [
        re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
        re.compile(r"ghp_[A-Za-z0-9_]{20,}"),
        re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),
        re.compile(r"(?i)(api[_-]?key|secret|token|password)(\s*=\s*)['\"]?[A-Za-z0-9_\-./+=]{16,}"),
    ]
    fixed = text
    for pattern in patterns[:3]:
        fixed = pattern.sub("REDACTED", fixed)
    fixed = patterns[3].sub(r"\1\2REDACTED", fixed)
    return fixed
