# AgentPreflight — User Flow Diagrams

## Flow 1: Developer Scan & Fix Loop (CLI)

```
Developer installs an MCP server or skill pack
              │
              ▼
    ┌─────────────────────────────┐
    │  agentpreflight scan .      │
    │  --profile strict           │
    │  --fail-on high             │
    └─────────────┬───────────────┘
                  │
         ┌────────▼────────┐
         │  Collector      │  reads mcp.json, SKILL.md, *.py,
         │                 │  *.js, *.env, config files
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Normalizer     │  strips hidden Unicode, tags
         │                 │  artifact kinds
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Rule Engine    │  runs 27 rules in parallel
         │  (27 rules)     │  across artifact kinds
         └────────┬────────┘
                  │
         ┌────────▼────────┐
         │  Scorer         │  deduct per finding severity,
         │                 │  cap, apply verdict
         └────────┬────────┘
                  │
              ┌───┴────────────────┐
              │                    │
         trust ≥ 70           trust < 70
         verdict: pass        verdict: fail
              │                    │
    ┌─────────┘           ┌────────┴─────────────────┐
    │                     │                           │
    ▼                     ▼                           ▼
  Exit 0         agentpreflight fix          agentpreflight prompts .
  (CI green)     --apply                     --output prompts.md
                 (local deterministic        (Codex-ready redacted
                  patches applied)            remediation pack)
                      │
                      ▼
             agentpreflight scan .
             --profile strict
             --fail-on high
             (rescan proof)
                      │
                      ▼
                trust_score=100
                verdict=pass
                Exit 0
```

---

## Flow 2: CI / GitHub Actions Gate

```
Developer opens pull request
              │
              ▼
    GitHub Actions triggered
    (.github/workflows/agentpreflight.yml)
              │
              ▼
    ┌─────────────────────────────────┐
    │  actions/checkout               │
    │  pip install agentpreflight     │
    └────────────────┬────────────────┘
                     │
                     ▼
    ┌─────────────────────────────────┐
    │  agentpreflight scan .          │
    │  --profile strict               │
    │  --fail-on high                 │
    │  --format sarif                 │
    │  --output results.sarif         │
    └────────────────┬────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    findings ≥ high          no high/critical
         │                       │
         ▼                       ▼
    Exit 1                   Exit 0
    PR blocked               PR can merge
         │
         ▼
    ┌─────────────────────────────────┐
    │  github/codeql-action/upload    │
    │  (SARIF → GitHub Security tab)  │
    └─────────────────────────────────┘
         │
         ▼
    ┌─────────────────────────────────┐
    │  PR comment posted              │
    │  (markdown scorecard)           │
    │  trust_score / verdict /        │
    │  findings table / fix hint      │
    └─────────────────────────────────┘
```

---

## Flow 3: AppSec Engineer Review (Suppression Workflow)

```
AppSec engineer reviews flagged finding
              │
              ▼
    ┌─────────────────────────────────────┐
    │  Finding: AP-NET-003 medium         │
    │  path: skill.md:42                  │
    │  evidence: http://internal-api/...  │
    └────────────────┬────────────────────┘
                     │
           ┌─────────┴──────────┐
           │                    │
     False positive        True risk
     (internal URL)        (needs fix)
           │                    │
           ▼                    ▼
    Add to .agentpreflight.json  Fix code / apply patch
    {                            agentpreflight fix --apply
      "rule": "AP-NET-003",
      "path": "skill.md",
      "reason": "internal API",
      "owner": "alice@company.com",
      "expires": "2026-08-01"
    }
           │
           ▼
    agentpreflight scan .
    --suppressions .agentpreflight.json
           │
           ▼
    Finding suppressed (auditable)
    summary.suppressed += 1
```

---

## Flow 4: Platform Lead Sets Policy

```
Platform lead configures CI policy
              │
              ▼
    Edit .github/workflows/agentpreflight.yml
    Set: fail_on: "medium"
         profile: "strict"
              │
              ▼
    All PRs in org: medium+ blocked
    Suppression file required for exceptions
    Suppression owners + expiry auditable
    SARIF feeds org-wide GitHub Security tab
```

---

## Artifact Kinds & Rule Coverage

```
File type         Artifact kind       Rules applied
─────────────────────────────────────────────────────
mcp.json          mcp_config          AP-MCP-001..005
SKILL.md          skill_md            AP-SKILL-001..005, AP-NET-003
*.py              code_py             AP-CODE-001..003, AP-CODE-MORE,
                                      AP-OWASP-001..005
*.js / *.ts       code_js             AP-CODE-001..003, AP-OWASP-001..002,
                                      AP-OWASP-005
*.md / *.mdx      markdown            AP-SKILL-001, AP-NET-003
.env*             env_file            AP-SEC-002, AP-SEC-003
*.json / *.yaml   config              AP-NET-001..003, AP-MCP-002..005
requirements.txt  dep_requirements    AP-DEP-001
package-lock.json dep_lock            AP-DEP-001
```
