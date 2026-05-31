# AgentPreflight — User Flow / Product Journey

## Trigger: Developer discovers an MCP security risk

A developer finds a new MCP server on npm, reads about the Postmark BCC attack, or gets a security review request for an existing agent extension. They need a fast answer: is this safe to run?

---

## Journey Map

```
DISCOVER                SCAN                    FIX                     PROVE
────────────────────────────────────────────────────────────────────────────────
pip install             mcp-agent-preflight-sec agentpreflight          agentpreflight
agentpreflight          scan <path>             fix <path> --codex      scan <path>
                        --profile strict        (Codex AI patch)        --profile strict
                        --fail-on high          ──────────────          --fail-on high
                                                agentpreflight
                                                fix <path> --apply
                                                (deterministic fix)
────────────────────────────────────────────────────────────────────────────────
<2 min install          trust_score=0           CODEX PATCH             trust_score=100
                        findings=15             AP-MCP-001 ···          findings=0
                        verdict=fail            changed=7               verdict=pass
                        CI blocks PR            ↓                       CI gates pass
                                                dev reviews diff
                                                merges fix
```

---

## Step-by-Step

### Step 1 — Install (< 2 minutes)
```bash
pip install mcp-agent-preflight-sec
agentpreflight --version
```
Works offline from this point. No account, no API key, no dashboard.

### Step 2 — Scan
```bash
agentpreflight scan <path-to-mcp-or-skill> --profile strict --fail-on high
```
Output: trust score (0–100), ranked findings by severity, OWASP rule IDs, exact file + line.  
CI integration: exits 1 when findings exceed threshold → PR blocked automatically.

### Step 3a — Codex AI patch (optional, requires OPENAI_API_KEY)
```bash
agentpreflight fix <path> --codex --rules AP-MCP-001
```
Sends only the redacted finding snippet to `codex-mini-latest`. Returns a human-reviewable patch proposal. Developer reads one diff and merges.

### Step 3b — Deterministic fix (offline, no API key)
```bash
agentpreflight fix <path> --apply
```
Regex-based rewrite covering 14 rules. Zero API calls. Safe for every CI run. Modifies files in place.

### Step 4 — Rescan (proof the fix held)
```bash
agentpreflight scan <path> --profile strict --fail-on high
```
trust_score=100, findings=0. CI gate passes. PR unblocks.

---

## User Personas & Entry Points

| Persona | Entry point | Primary value |
|---|---|---|
| **Solo AI developer** | `pip install` during local dev | Catches poisoned MCP/skill before first commit |
| **AppSec/DevSecOps engineer** | GitHub Action in repo CI | Blocks risky extensions at PR review automatically |
| **Enterprise security team** | SARIF output → GitHub Security tab | Org-wide visibility + policy enforcement |

---

## What they DON'T need to do

- Create an account
- Set up infrastructure
- Pass credentials to the scanner
- Run the MCP server to test it (static scan only — no execution)
- Manually review 500 lines of MCP config
