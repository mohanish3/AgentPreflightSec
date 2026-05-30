# AgentPreflight

Pre-deployment security scanner for MCP servers and agent skills. Finds tool poisoning, prompt injection, secrets, and unsafe code before your agent runs — offline static scan, Codex-generated fixes, rescan proof.

```
trust_score=0 verdict=fail findings=15   ← poisoned repo
trust_score=100 verdict=pass findings=0  ← after Codex fix + rescan
```

---

## Why

The first confirmed malicious MCP server on npm ran for 15 versions before anyone noticed. Then, in a single commit, the attacker added one BCC line to `send_email`. Every password reset token forwarded to an attacker address. No CI check caught it.

This was not isolated:

- **14 documented MCP incidents** in 12 months (authzed.com) — WhatsApp exfiltration, GitHub MCP prompt injection exfiltrating private repo data including financial information, Asana cross-tenant data leak (~1,000 enterprise orgs, 35 days), Smithery supply-chain breach (3,000+ apps), Oura MCP malware campaign delivering StealC credential harvesters (Feb 2026), nginx-ui MCP auth bypass granting complete nginx service control across 2,600+ live infra instances (Mar 2026)
- **36.82% of 3,984 scanned agent skills** (1,467 skills) had at least one flaw; 13.4% (534 skills) had a critical issue; 76 confirmed malicious payloads, 91% combining prompt injection with traditional malware techniques — 8 payloads still publicly available at time of publication (Snyk ToxicSkills 2025)
- **43% of popular MCP server implementations** had command injection; Puppeteer MCP (91,000 monthly downloads) had SSRF + prompt injection + sandbox bypass — archived rather than patched. 45% of vendors dismissed Equixly's findings as "theoretical." Equixly's conclusion: "It feels like we're facing a regression in security." (March 2025)
- **CVSS 9.6 RCE** in `mcp-remote` (437,000+ downloads) — the package Claude Desktop uses for remote MCP
- **72.8% tool-poisoning attack success rate** against o1-mini in one evaluated setting (45 real-world servers); Claude-3.7-Sonnet refused fewer than 3% of malicious test cases (MCPTox)
- **April 2026**: OX Security found STDIO architectural flaw across 150M+ downloads — Anthropic declined to modify the protocol
- **Runtime defenses fail by design**: Invariant Labs demonstrated a "rug pull" — malicious server served innocent descriptions on first launch, then switched to data-exfiltrating instructions on second launch, after trust was already granted

MCP tool descriptions are natural-language, invisible to standard CI checks. Bandit and Semgrep scan Python syntax — they do not parse the semantic content of tool metadata strings. A Postmark-style BCC injection in a tool description is invisible to every general-purpose SAST tool on the market. The MCP specification requires clients to treat tool annotations from untrusted servers as untrusted — but provides no enforcement mechanism. Anthropic declined to modify the STDIO architecture (OX Security, April 2026). The gate must be built outside the protocol layer. AgentPreflight is that gate: sub-second pre-commit/PR linter — scan → trust score → Codex patch → rescan proof. Under two minutes, entirely static — offline-first, local static file parsing with straightforward logic, never executes the server to analyze it. First to market on the complete scan-to-Codex-patch-to-rescan-proof workflow for MCP security. Conservative time model: 15 minutes saved per agent-extension PR; 30–60 minutes saved per high-risk finding when Codex suggests a targeted patch.

---

## Install

```bash
# From PyPI (recommended):
pip install agentpreflight
agentpreflight --version

# From source:
pip install .

# Optional extras:
pip install "agentpreflight[api]"     # FastAPI scan endpoint
pip install "agentpreflight[codex]"   # Codex AI remediation
export OPENAI_API_KEY=<your-key>
```

---

## 90-Second Demo

```bash
# scan a poisoned MCP repo — expect fail
agentpreflight scan demo/poisoned --profile strict --fail-on high

# get Codex AI patch proposals (requires OPENAI_API_KEY)
agentpreflight fix demo/poisoned --rules AP-MCP-001 --codex

# apply deterministic safe fixes
cp -r demo/poisoned /tmp/fix-demo
agentpreflight fix /tmp/fix-demo --apply

# rescan — expect pass
agentpreflight scan /tmp/fix-demo --profile strict
```

---

## Sample Output

**Scan a poisoned MCP repo:**

```
$ agentpreflight scan demo/poisoned --profile strict

╔════════════════════════════════════════════════════╗
║  ▄▀▄  █▀█                                          ║
║  █▀█  █▀   AgentPreflight  v0.1.0                  ║
║  ▀ ▀  ▀    Pre-deployment MCP & skill scanner      ║
║               offline · static · SARIF · 21 rules  ║
╚════════════════════════════════════════════════════╝
AgentPreflight target=demo/poisoned
trust_score=0 verdict=fail findings=15 offline=True
summary critical=7 high=5 medium=3 low=0 suppressed=0 artifacts=6
┌──────────┬──────────────┬────────────┬──────┬───────────────────────────────┐
│ Severity │ Rule         │ Path       │ Line │ Evidence                      │
├──────────┼──────────────┼────────────┼──────┼───────────────────────────────┤
│ critical │ AP-CODE-003  │ install.sh │    3 │ Remote pipe: curl … | bash    │
│ critical │ AP-CODE-001  │ run.py     │    5 │ os.system() call              │
│ critical │ AP-CODE-001  │ server.py  │    6 │ os.system() call              │
│ critical │ AP-CODE-001  │ server.py  │    7 │ subprocess with shell=True    │
│ critical │ AP-CODE-003  │ SKILL.md   │   10 │ Remote pipe: curl … | sh      │
│ high     │ AP-SEC-002   │ .env       │    1 │ Secret-like token pattern     │
│ high     │ AP-MCP-001   │ mcp.json   │      │ Tool description contains:    │
│          │              │            │      │ "Hidden instruction"          │
│ high     │ AP-SKILL-001 │ SKILL.md   │    5 │ Injection phrase: "Secret     │
│          │              │            │      │ directive"                    │
│ …        │              │            │      │                               │
└──────────┴──────────────┴────────────┴──────┴───────────────────────────────┘
fix_available=14  run: agentpreflight fix demo/poisoned
```

**Apply fixes and rescan:**

```
$ agentpreflight fix demo/poisoned --apply
fixable=14  changed=7

$ agentpreflight scan demo/poisoned --profile strict
╔════════════════════════════════════════════════════╗
║  ▄▀▄  █▀█                                          ║
║  █▀█  █▀   AgentPreflight  v0.1.0                  ║
║  ▀ ▀  ▀    Pre-deployment MCP & skill scanner      ║
║               offline · static · SARIF · 21 rules  ║
╚════════════════════════════════════════════════════╝
AgentPreflight target=demo/poisoned
trust_score=100 verdict=pass findings=0 offline=True
PASS: no issues found
```

**Scan a clean repo:**

```
$ agentpreflight scan demo/clean --profile strict
╔════════════════════════════════════════════════════╗
║  ▄▀▄  █▀█                                          ║
║  █▀█  █▀   AgentPreflight  v0.1.0                  ║
║  ▀ ▀  ▀    Pre-deployment MCP & skill scanner      ║
║               offline · static · SARIF · 21 rules  ║
╚════════════════════════════════════════════════════╝
AgentPreflight target=demo/clean
trust_score=100 verdict=pass findings=0 offline=True
PASS: no issues found
```

---

## Commands

```bash
# scan with trust score + table output
agentpreflight scan <path> --profile strict --fail-on high

# output formats
agentpreflight scan <path> --format sarif --output report.sarif
agentpreflight scan <path> --format json --output report.json
agentpreflight scan <path> --format markdown --output pr-comment.md

# suppression file
agentpreflight scan <path> --suppressions .agentpreflight.json

# fix (dry run → Codex proposals → apply)
agentpreflight fix <path>
agentpreflight fix <path> --codex                  # Codex AI patch (OPENAI_API_KEY)
agentpreflight fix <path> --codex --rules AP-MCP-001
agentpreflight fix <path> --apply                  # deterministic local fix

# generate Codex remediation prompt pack
agentpreflight prompts <path> --output remediation.md

# benchmark scan speed
agentpreflight bench <path> --runs 5

# list all 21 rules
agentpreflight rules list
```

---

## GitHub Action

```yaml
- uses: ./
  with:
    target: .
    profile: strict
    fail-on: high
    sarif-file: agentpreflight.sarif
    comment-file: agentpreflight-comment.md
```

SARIF uploads to GitHub Security tab. PR comment scorecard auto-posts.

Full workflow: `.github/workflows/agentpreflight.yml`

---

## Rules (21 total)

| Category | Rules |
|---|---|
| MCP | AP-MCP-001 prompt override, AP-MCP-002 trust claim, AP-MCP-003 untrusted result, AP-MCP-004 loose schema, AP-MCP-005 privileged tool |
| Skill | AP-SKILL-001 prompt injection, AP-SKILL-002 hidden Unicode, AP-SKILL-003 remote dependency, AP-SKILL-004 credential seeking, AP-SKILL-005 capability mismatch |
| Code | AP-CODE-001 unsafe shell **(crit)**, AP-CODE-002 dynamic exec, AP-CODE-003 remote pipe exec **(crit)**, AP-CODE-004 file access, AP-CODE-005 network exfiltration |
| Secrets | AP-SEC-001 private key **(crit)**, AP-SEC-002 API token, AP-SEC-003 committed env file |
| Transport | AP-NET-001 broad bind, AP-NET-002 missing origin validation, AP-NET-003 plain HTTP tool |

---

## Suppression File

`.agentpreflight.json` at repo root — auto-detected:

```json
{
  "suppressions": [
    {
      "rule": "AP-SEC-003",
      "path": ".env",
      "reason": "demo fixture",
      "owner": "appsec",
      "expires": "2026-06-30"
    }
  ]
}
```

Inline suppression in source:

```python
os.system("echo ok")  # agentpreflight:disable-line AP-CODE-001
```

---

## API (optional)

```bash
pip install ".[api]"
uvicorn agentpreflight.api.main:app --reload
```

```bash
curl -X POST http://localhost:8000/v1/scans \
  -H "Content-Type: application/json" \
  -d '{"target": {"path": "demo/clean"}, "profile": "strict"}'
```

Auth + rate limiting via env vars:

```bash
export AGENTPREFLIGHT_API_KEY=local-dev-key
export AGENTPREFLIGHT_RATE_LIMIT_PER_MINUTE=60
```

---

## Validation

53 tests pass (`pytest tests/ -q`). Covers: all 21 rules, scanner exclude, suppression, scoring caps, Codex API mock, SARIF output, fix proofs, API auth/rate limiting, benchmark.

```
$ pytest tests/ -q
.....................................................     [100%]
53 passed in 0.55s
```

Scan → fix → rescan proof:

```
$ agentpreflight scan demo/poisoned --profile strict
trust_score=0 verdict=fail findings=15  critical=7 high=5 medium=3

$ agentpreflight fix demo/poisoned --apply
fixable=14  changed=7

$ agentpreflight scan demo/poisoned --profile strict
trust_score=100 verdict=pass findings=0
PASS: no issues found
```

---

## Architecture

```
agentpreflight scan:
  collector → normalizer → rule engine → trust scorer → reporter
  (100% offline, zero API calls, sub-second on typical repos)

agentpreflight fix:
  findings → [--codex] redacted snippet → OpenAI Codex API → patch proposal
           → [--apply] deterministic regex rewrite → files modified

agentpreflight scan (rescan):
  new trust score confirms fix held
```

Scan path: offline by default, no model calls, no token cost.  
Fix path: `--codex` sends a 5-line code window around the violation (redacted — no secrets, no file paths) to `codex-mini-latest`. Code rewriting is cheap; the scarce resource is *selection* — which of the infinite possible rewrites is minimal, compilable, and review-ready. Codex makes that call.  
CI path: `--fail-on high` exits 1 on violations; trust score thresholds: 85+=pass, 70–84=warn, <70=fail (critical finding caps at 50; secrets cap at 55; 3+ high cap at 60; combo caps lower); critical rules: AP-CODE-001 (unsafe shell), AP-CODE-003 (remote pipe exec), AP-SEC-001 (private key); SARIF uploads to GitHub Security tab.

---

## Docs

| File | Contents |
|---|---|
| `PRODUCT.md` | Build plan, MVP scope, success metrics |
| `SPEC.md` | Architecture, rule catalog, scoring formula |
| `DEMO.md` | 90-second demo script, launch checklist |
| `COMPETITORS.md` | Competitive landscape, 10x differentiation |
| `EVIDENCE.md` | CVEs, incidents, scale stats, verification audit |
