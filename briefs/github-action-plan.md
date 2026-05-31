# GitHub Action Plan: PR Gates & SARIF Integration

This document outlines the engineering plan to package and deploy **AgentPreflight** as a custom GitHub Action.

---

## 1. Action Workflow Definition

We define the complete workflow YAML for integration in developer repositories:

```yaml
name: AgentPreflight Security Gate

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  agent-security-scan:
    runs-on: ubuntu-latest
    permissions:
      security-events: write  # Required for SARIF upload
      pull-requests: write     # Required for PR scorecard commenting
      contents: read

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install AgentPreflight
        run: |
          pip install mcp-agent-preflight-sec

      - name: Run Preflight Scan
        id: scan
        run: |
          # Execute scan exporting to SARIF, failing on High severity alerts
          agentpreflight scan . --format sarif --fail-on high > agentpreflight-results.sarif
        continue-on-error: true

      - name: Upload SARIF to GitHub Security Tab
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: agentpreflight-results.sarif
          category: agentpreflight

      - name: Publish PR Scorecard Comment
        uses: agentpreflight/action-pr-commenter@v1
        with:
          sarif_file: agentpreflight-results.sarif
```

---

## 2. PR Scorecard Comment Mockup

When the scan finishes, the action commenter publishes a high-visibility visual scorecard directly onto the developer's pull request:

```markdown
## 🛡️ AgentPreflight Scan Scorecard

| Scan ID | Target Path | Verdict | Hardening Score |
|:---|:---|:---|:---|
| `scan_01HXYZ` | `./skills/calendar` | ❌ **FAILED** | **45 / 100** |

### ⚠️ Violations Summary:
- **Critical**: 1 violation (AP-MCP-001: Tool description override detected)
- **High**: 1 violation (AP-CODE-001: Unsafe subprocess call in weather.py)
- **Medium**: 1 warning (AP-NET-001: Local host bind lacks origin validation)

---
💡 **Remediation Available**: Run `agentpreflight fix . --codex --rules AP-MCP-001` for Codex AI patches, or `agentpreflight fix . --apply` for deterministic offline fixes.
```
