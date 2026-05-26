# MVP Implementation Specification: CLI & API Contract

This document provides the exact developer CLI commands, HTTP API schemas, and core rule check specifications for the **AgentPreflight** MVP.

---

## 1. CLI Command Specification

The CLI runs locally as a packaged Python tool:

```bash
# General Scan Syntax
agentpreflight scan <path> [--profile balanced|strict] [--fail-on low|medium|high] [--format text|json|sarif] [--offline]

# Apply Codex Remediation
agentpreflight fix --rule <rule_id> [--interactive]
```

### Options:
- `<path>`: Absolute or relative path to the MCP server or skill directory.
- `--profile`: `balanced` (default, skips low-severity alerts) or `strict` (fails on any warning).
- `--fail-on`: Configures the CI exit-code barrier (`low`, `medium`, `high`).
- `--format`: Reporting formats (`text`, `json`, `sarif`).
- `--offline`: Bypasses all network calls, preventing any Codex API integration.

---

## 2. HTTP API Contract

For multi-repo environments or hosted platforms, the scanner runs as a FastAPI service.

### Endpoint: `POST /v1/scans`

#### Request Payload:
```json
{
  "target_path": "./my-mcp-server",
  "profile": "balanced",
  "fail_on": "high",
  "offline": false,
  "redact_pii": true
}
```

#### Response Payload (200 OK):
```json
{
  "scan_id": "scan_01HXYZ",
  "timestamp": "2026-05-25T20:30:00Z",
  "summary": {
    "trust_score": 65,
    "verdict": "fail",
    "findings_count": {
      "critical": 0,
      "high": 2,
      "medium": 1,
      "low": 1
    }
  },
  "findings": [
    {
      "id": "AP-PI-001",
      "severity": "high",
      "category": "tool_poisoning",
      "title": "Adversarial prompt injection in tool description",
      "file_path": "mcp.json",
      "line_number": 12,
      "evidence": "Contains imperative override text: 'ignore previous instructions'",
      "fix_available": true
    }
  ]
}
```

---

## 3. Core Rule Engine Specs

The rule engine executes targeted local regular expression and AST checks:

1. **AP-PI-001 (`tool_poisoning`)**:
   - *Target*: `mcp.json` tool descriptions.
   - *Pattern*: Imperative instructions directing the model to act as a system override.
2. **AP-US-001 (`unicode_smuggling`)**:
   - *Target*: `SKILL.md`, `README.md`.
   - *Pattern*: Non-printable control characters, zero-width joiners, and Latin/Cyrillic lookalikes.
3. **AP-EX-001 (`unsafe_exec`)**:
   - *Target*: Python and TypeScript files.
   - *Pattern*: Call strings for `eval()`, `exec()`, `os.system()`, or `shell=True` in subprocess.
4. **AP-SR-001 (`secrets`)**:
   - *Target*: All local files.
   - *Pattern*: High-entropy strings representing API keys, private tokens, or client secrets.
