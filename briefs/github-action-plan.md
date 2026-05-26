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
          pip install agentpreflight

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
- **Critical**: 1 violation (AP-PI-001: Tool description override detected)
- **High**: 1 violation (AP-EX-001: Unsafe subprocess call in weather.py)
- **Medium**: 1 warning (AP-TS-001: Local host bind lacks origin validation)

---
💡 **Remediation Available**: Run `agentpreflight fix --rule AP-PI-001` locally to automatically generate secure Codex patches and fix these findings!
```
