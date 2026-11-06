# AgentPreflight

Pre-deployment security scanner for MCP servers and agent skills. Finds tool poisoning, prompt injection, secrets, and unsafe code before your agent runs: offline static scan, Codex-generated fixes, rescan proof.

```
trust_score=0 verdict=fail findings=15   ← poisoned repo
trust_score=100 verdict=pass findings=0  ← after Codex fix + rescan
```

---

## Why

The first confirmed malicious MCP server on npm ran for 15 versions before anyone noticed. Then, in a single commit, the attacker added one BCC line to `send_email`. Every password reset token forwarded to an attacker address. No CI check caught it. ([Full writeup, primary source](EVIDENCE.md#4-postmark-mcp-supply-chain-attack--september-2025).)

That wasn't isolated. Three more, each independently confirmed:

- **CVE-2025-6514** (CVSS 9.6): RCE in `mcp-remote`, the package Claude Desktop uses to talk to remote MCP servers (437,000+ downloads at disclosure).
- **Asana's MCP launch** leaked cross-tenant project data to ~1,000 enterprise customers for over a month before the tenant-isolation bug was caught (BleepingComputer, June 2025).
- **Invariant Labs' "rug pull"** demo: a malicious server served innocent tool descriptions on first launch, then switched to data-exfiltrating instructions on the second, after trust was already granted. Runtime monitoring can't catch this; it has to be caught before the server ever runs.

Full incident list with primary sources and dates: [EVIDENCE.md](EVIDENCE.md).

MCP tool descriptions are natural-language and invisible to standard CI checks: Bandit and Semgrep scan Python syntax, not the semantic content of a tool's metadata string. A Postmark-style BCC injection in a tool description passes every general-purpose SAST tool on the market. AgentPreflight is a static, offline pre-commit/PR linter built for that specific gap: scan → trust score → optional Codex-generated patch → rescan proof, in under two minutes, with zero API calls unless you opt into the `--codex` fix path.

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
# scan a poisoned MCP repo, expect fail
agentpreflight scan demo/poisoned --profile strict --fail-on high

# get Codex AI patch proposals (requires OPENAI_API_KEY)
agentpreflight fix demo/poisoned --rules AP-MCP-001 --codex

# apply deterministic safe fixes
cp -r demo/poisoned /tmp/fix-demo
agentpreflight fix /tmp/fix-demo --apply

# rescan, expect pass
agentpreflight scan /tmp/fix-demo --profile strict
```

All output above is real, verified output: see `validation/poisoned-scan.txt`, `validation/fix-proof-*/`, and `validation/clean-scan.txt`.

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

`.agentpreflight.json` at repo root, auto-detected:

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
Fix path: `--codex` sends a 5-line code window around the violation (redacted: no secrets, no file paths) to `codex-mini-latest`. Code rewriting is cheap; the scarce resource is *selection*: which of the infinite possible rewrites is minimal, compilable, and review-ready. Codex makes that call.  
CI path: `--fail-on high` exits 1 on violations; trust score thresholds: 85+=pass, 70–84=warn, <70=fail (critical finding caps at 50; secrets cap at 55; 3+ high cap at 60; combo caps lower); critical rules: AP-CODE-001 (unsafe shell), AP-CODE-003 (remote pipe exec), AP-SEC-001 (private key); SARIF uploads to GitHub Security tab.

---

## Research

| File | Contents |
|---|---|
| `briefs/winner-product-brief.md` | Full product brief: problem, solution, Codex integration, why this wins |
| `briefs/investor-one-pager.md` | Investment brief: competitive position, proof, ICP |
| `briefs/submission-summary.md` | Devpost/Luma submission entry |
| `briefs/pitch-deck.md` | 4-slide pitch deck |
| `PRODUCT.md` | Build plan, MVP scope, success metrics |
| `SPEC.md` | Architecture, rule catalog, scoring formula |
| `DEMO.md` | 90-second demo script, launch checklist |
| `COMPETITORS.md` | Competitive landscape, 10x differentiation |
| `EVIDENCE.md` | CVEs, incidents, scale stats, verification audit |
