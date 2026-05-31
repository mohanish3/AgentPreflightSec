# AgentPreflight: Competitor Analysis

## Key finding

The direct competitor landscape is crowded. AgentPreflight must not claim "first MCP/skill scanner," "unique trust score," "unique SARIF/CI," "unique local scan," or "only autofix." Multiple competitors now have these.

**Submission-safe positioning:**

> AgentPreflight is a source-static, reviewable remediation loop for MCP and agent-skill risks: scan, trust score, SARIF, constrained Codex patch, rescan proof.

**Primary wedge:** time-to-fix, not detection breadth. From poisoned agent artifact to fixed PR in under two minutes.

---

## Top 10 canonical competitors

| Rank | Competitor | Unique capability | AgentPreflight wedge |
|---:|---|---|---|
| 1 | SkillScan | Offline MCP/skill scanner with 150+ rules, SARIF, GitHub Actions. | Constrained patches and polished demo flow. |
| 2 | sinewaveai agent-security-scanner-mcp | MCP scanner server with 1000+ rules, SARIF, auto-fix claim. | Safer/static and demonstrable in two minutes. |
| 3 | SkillRisk | Local/browser skill scanner with security score and remediation. | Repo/CI workflow and rescan proof. |
| 4 | AgentSeal | OSS scanner for prompts, MCP, skills, machine guard, SARIF/JUnit, BYOK. | Static file-only fix/rescan simplicity. |
| 5 | Firmis | Agent-stack scanner with Deep Scan, Auto-Fix, Monitor. | Narrower and more auditable; demo-polished. |
| 6 | HackMyAgent | 147 checks, auto-fix with rollback, benchmark compliance, attack mode. | MCP/skill PR patches, not broad platform. |
| 7 | Inkog | CLI + MCP server that scans, explains, and applies fixes inside Claude/Cursor. | Better CI/SARIF and local static guarantees. |
| 8 | AgentAuditKit | MCP pipeline scanner with `fix`, SARIF, many rules, OWASP mapping. | Avoid feature sprawl; win UX and demo polish. |
| 9 | Snyk Agent Scan | Enterprise-backed: scans agents, MCP, skills, prompts, resources; local discovery, fleet reporting. | Free local fix/rescan path; no dangerous-flag requirement. |
| 10 | Aguara / agent-audit | Local/static scanners with SARIF/GitHub workflows. | Safer remediation; polished demo flow. |

Watchlist (reinforce scanner saturation): SafeSkills, Backslash, AiSkillsGuard, SkillShield, SkillTester, SkillProbe, SkillAttack, skill-lab.

Full URLs in `sources/source-register.md`.

---

## Remediation-first competitor analysis

Most direct competitors fit one of three buckets:

| Bucket | Competitors |
|---|---|
| Find only | Snyk Agent Scan, Aguara, agent-audit |
| Fix code | GitHub Copilot Autofix, Snyk Agent Fix, Semgrep Autofix |
| Test running agents | Promptfoo, Garak, PyRIT, Giskard |

AgentPreflight targets the missing square: **fix agent-supply-chain findings before the agent runs.**

### Top remediation competitors

| Rank | Competitor | Remediation strength | Why AgentPreflight still differs |
|---:|---|---|---|
| 1 | GitHub Copilot Autofix | CodeQL alert fixes; >90% alert-type coverage in JS/TS/Java/Python; >2/3 remediation with little or no editing. | Code-centric; no MCP/skill artifact trust scoring. |
| 2 | Snyk Agent Fix | Automated SAST/source-code fixes. | Separate from Agent Scan; no clear MCP/skill natural-language patch loop. |
| 3 | Semgrep Autofix/Assistant | PR/MR remediation guidance and AI-generated fixes; validates fixes by rerunning engine. | Generic code findings; no default MCP/skill supply-chain model. |
| 4 | AgentAuditKit | `fix` command + MCP scanning, SARIF, OWASP mapping. | Closest direct; AgentPreflight must win on UX and two-minute demo. |
| 5 | Snyk Agent Scan | Strong detection + fleet reporting. | Public workflow focuses on report/review; CI requires `--dangerously-run-mcp-servers`. |
| 6 | Aguara | Local-first agent/supply-chain scanner; no SaaS, no LLM calls. | Not positioned around generated patches. |
| 7 | agent-audit | SARIF, GitHub Action, MCP config auditing, taint analysis. | Scan/report/fail workflow, not fix/rescan loop. |

---

## 10x analysis

### New 10x thesis

AgentPreflight is not 10x because it finds MCP/skill issues first. It is 10x only if it makes the secure path safer and faster.

> From poisoned agent artifact to fixed PR in under two minutes.

### 10x comparison table

| Dimension | Direct/autofix scanners | AgentPreflight remediation-first |
|---|---|---|
| Core value | Find risky MCP/skill artifacts. | Find, patch, and prove the risk is gone. |
| Developer workflow | Read report, understand finding, edit manually, rerun. | `scan`, `fix`, review diff, `rescan`. |
| Demo clarity | Findings list. | Failing repo becomes passing repo live. |
| Risk control | Many findings can become alert fatigue. | Only high-confidence patch classes in MVP. |
| Codex leverage | Optional helper. | Central product loop. |

### Demo metric

```text
Before: trust_score=0  verdict=fail  findings=15
Fix:    agentpreflight fix . --codex (Codex AI proposals)
        agentpreflight fix . --apply (14 deterministic fixes)
After:  trust_score=100  verdict=pass  findings=0
Time:   under 2 minutes
```

---

## Remediation-first market evidence

GitHub Copilot Autofix validates the pattern. GitHub reports code scanning autofix covers more than 90% of alert types in JS/TS/Java/Python and remediates more than two-thirds of found vulnerabilities with little or no editing. GitHub also reports developers fixed vulnerabilities more than three times faster during public beta.

Snyk Agent Fix and Semgrep Autofix validate the same pattern for SAST: automated remediation is the way to reduce security backlog and developer friction.

The MCP/skill scanner market is crowded, but remediation is still weaker. Snyk Agent Scan needs `--dangerously-run-mcp-servers` for CI. Aguara avoids LLM calls by design. agent-audit has scan/report/fail, not patch/rescan.

AgentPreflight applies "found means fixed" to MCP/skill supply-chain artifacts.

---

## Differentiation vs categories

### vs direct scanners

Snyk Agent Scan, SkillScan, SkillRisk, AgentSeal, Firmis, HackMyAgent, Inkog, AgentAuditKit, Aguara, agent-audit all validate the category. AgentPreflight must differentiate through:

- constrained Codex remediation patches (exact-line, high-confidence only)
- transparent rule packs and trust scoring
- SARIF-first GitHub code scanning
- local policy customization
- concise two-minute demo flow
- rule mapping to OWASP MCP, OWASP Agentic Skills, MCPTox-style risks
- rescan proof that fixed rule IDs disappeared

### vs red-team frameworks

Promptfoo, Garak, PyRIT, Inspect AI need live agents and are too heavy for PR-native review. AgentPreflight: no live agent required, no model calls by default, deterministic CI gate, scans `mcp.json`/`SKILL.md`/code directly.

### vs runtime guardrails

Llama Guard, NeMo Guardrails, Lakera Guard work at runtime. AgentPreflight shifts left: blocks risky extensions before use, avoids hot-path latency, preserves source privacy by default, creates auditable PR artifacts.

---

## Product implications

- Build direct scanner MVP, but keep claims precise.
- Add visible rule catalog and scoring formula.
- Include fixture-backed demo for poisoned MCP metadata, hidden Unicode, unsafe shell, secret leakage, and over-broad tool permissions.
- Defer dynamic sandbox, hosted dashboard, and full RAG parsing until after MVP.
- Make `fix` first-class: `scan` → `fix` → `diff` → `rescan` must be the first screen and demo.
