# AgentPreflight

Static preflight scanner for MCP servers and agent skills. Finds tool poisoning, prompt injection, secrets, and unsafe code before your agent runs — offline, no model calls required.

```
trust_score=0 verdict=fail findings=15   ← poisoned repo
trust_score=100 verdict=pass findings=0  ← after fix
```

---

## Install

```bash
pip install .
agentpreflight --version
```

---

## 90-Second Demo

```bash
# scan a poisoned MCP repo — expect fail
agentpreflight scan demo/poisoned --profile strict --fail-on high

# see exactly what to fix
agentpreflight fix demo/poisoned

# apply safe local fixes
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

# fix (dry run then apply)
agentpreflight fix <path>
agentpreflight fix <path> --apply

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
| `validation/pytest-may27.txt` | 26 unit tests pass (2026-05-27) |
| `validation/poisoned-scan-may27.txt` | poisoned demo → score 0, fail, 15 findings, truncation hint |
| `validation/clean-scan-may27.txt` | clean demo → score 100, pass, 0 findings |
| `validation/agentpreflight.sarif` | SARIF 2.1.0 output |
| `validation/sarif-validation.txt` | SARIF schema validates |
| `validation/pr-comment.md` | PR scorecard markdown |
| `validation/suppression-scan.txt` | suppression → suppressed=1 |
| `validation/benchmark-100.txt` | 100-file scan proof, avg 0.009s |
| `validation/inline-suppression.txt` | inline disable-line works |
| `validation/remediation-prompts.md` | Codex prompt pack (redacted) |
| `validation/api-security-proof.txt` | 401/403/429 enforced |
| `validation/latest-fix-proof.txt` | score 0 → 100 fix proof |

---

## Architecture

```
collector → normalizer → rule engine → trust scorer → reporter
                                           ↓
                                    agentpreflight fix
                                    (constrained patch → rescan)
```

Offline by default. No model calls in scan path. Redacted snippets only if Codex remediation is used.

---

## Research

| File | Contents |
|---|---|
| `PRODUCT.md` | Problem, solution, judge one-pager |
| `SPEC.md` | Architecture, rule catalog, scoring formula |
| `DEMO.md` | 90-second demo script, launch checklist |
| `COMPETITORS.md` | Competitive landscape, 10x differentiation |
| `EVIDENCE.md` | CVEs, incidents, scale stats, verification audit |
