# AgentPreflight

Pre-deployment security scanner for MCP servers and agent skills. Finds tool poisoning, prompt injection, secrets, and unsafe code before your agent runs — offline static scan, Codex-generated fixes, rescan proof.

```
trust_score=0 verdict=fail findings=15   ← poisoned repo
trust_score=100 verdict=pass findings=0  ← after Codex fix + rescan
```

---

## Why

14 documented MCP security incidents in 12 months (authzed.com timeline). Snyk's ToxicSkills study: 13.4% of 3,984 scanned skills had a critical issue. `mcp-remote` — the package Claude Desktop uses to connect to remote servers — had a CVSS 9.6 RCE in 437,000+ downloads.

Equixly's March 2025 audit of popular MCP server implementations found **43% had command injection, 30% had SSRF, 22% had path traversal**. The official Anthropic-maintained Puppeteer MCP server — 91,000 monthly downloads — had SSRF, prompt injection, and sandbox bypass simultaneously. It was archived rather than patched.

The attack surface is new: MCP tool descriptions are natural-language, readable by the model but invisible to most CI checks. In one evaluated setting, MCPTox tested tool poisoning against real MCP servers and found a 72.8% attack success rate. Runtime firewalls don't catch it — by the time the agent runs, the malicious instruction has already been injected.

The first confirmed malicious MCP server on npm ran for 15 versions before anyone noticed. Then, in a single commit, the attacker added one BCC line to `send_email`. Every password reset token forwarded to an attacker address. No existing CI check flagged it.

AgentPreflight is the pre-deployment gate: scan → trust score → Codex patch → rescan proof. Under two minutes from failing scan to passing PR.

---

## Install

```bash
pip install .
agentpreflight --version

# For Codex AI remediation (optional):
pip install ".[codex]"
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
| Code | AP-CODE-001 unsafe shell, AP-CODE-002 dynamic exec, AP-CODE-003 remote pipe exec, AP-CODE-004 file access, AP-CODE-005 network exfiltration |
| Secrets | AP-SEC-001 private key, AP-SEC-002 API token, AP-SEC-003 committed env file |
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

## Validation Proof

| File | What it proves |
|---|---|
| `validation/pytest-may26.txt` | 25 unit tests pass |
| `validation/pytest-may27.txt` | 30 unit tests pass (includes Codex API mocks) |
| `validation/poisoned-scan.txt` | poisoned demo → score 0, fail |
| `validation/clean-scan.txt` | clean demo → score 100, pass |
| `validation/agentpreflight.sarif` | SARIF 2.1.0 output |
| `validation/sarif-validation.txt` | SARIF schema validates |
| `validation/pr-comment.md` | PR scorecard markdown |
| `validation/suppression-scan.txt` | suppression → suppressed=1 |
| `validation/benchmark.txt` | 113 artifacts in 0.079s avg |
| `validation/benchmark-100.txt` | 100-file scan proof |
| `validation/inline-suppression.txt` | inline disable-line works |
| `validation/remediation-prompts.md` | Codex prompt pack (redacted) |
| `validation/api-security-proof.txt` | 401/403/429 enforced |
| `validation/fix-proof-*/` | score 0 → 100 fix proof |

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
Fix path: `--codex` sends only redacted snippets — no secrets, no full file contents.  
CI path: `--fail-on high` exits 1 on violations; SARIF uploads to GitHub Security tab.

---

## Research

| File | Contents |
|---|---|
| `PRODUCT.md` | Problem, solution, judge one-pager |
| `SPEC.md` | Architecture, rule catalog, scoring formula |
| `DEMO.md` | 90-second demo script, launch checklist |
| `COMPETITORS.md` | Competitive landscape, 10x differentiation |
| `EVIDENCE.md` | CVEs, incidents, scale stats, verification audit |
