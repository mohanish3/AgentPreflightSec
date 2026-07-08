# AgentPreflight — 1-Page Investor Pitch

**The problem is invisible and growing fast.**

AI agents now install third-party MCP servers and skill packs the same way developers install npm packages — except there is no lock file for trust. A poisoned tool description can redirect an agent to exfiltrate data, run arbitrary commands, or follow hidden instructions before any runtime guardrail sees a single token. Snyk found 36.82% of scanned agent skills had at least one security flaw; 13.4% had a critical issue. OWASP and GitHub Copilot's own security guidance acknowledge the problem. The tooling does not exist yet.

**AgentPreflight is the pre-deployment security gate for AI agents.**

One command — `agentpreflight scan . --profile strict --fail-on high` — audits MCP configs, skill prompts, Python/TypeScript scripts, and secrets in milliseconds. It returns a trust score (0–100), ranked findings, and machine-readable SARIF output that drops into GitHub's existing security tab. Unlike runtime guardrails (Llama Guard, Lakera), it runs statically before merge, costs nothing per conversation, and never sends code to a hosted endpoint.

**The loop is the wedge.**

Detection alone is not enough. AgentPreflight includes a fix loop: `agentpreflight fix --apply` applies constrained, high-confidence patches directly to the flagged lines, then reruns the scan to produce a rescan proof. Score 0 → 100 in under two minutes. No human reviewer has to read every tool description manually.

**Why now.**

MCP was released in November 2024. Adoption is moving fast — Claude Desktop, Cursor, OpenAI Agents SDK, and dozens of open-source agent frameworks all support the protocol. The window to become the default trust layer before the ecosystem consolidates is 6–12 months.

**Business model.**

- **Free CLI**: developer adoption, GitHub Stars, word-of-mouth.
- **Team plan**: policy management, suppression audit trail, PR comment integration. $20/seat/month.
- **Enterprise**: SSO, custom rule packs, SLA, on-prem deployment. $50k–$200k ACV.
- **Marketplace**: verified skill/MCP registry where publishers pay for a trust badge.

**Traction (Day 2 of build).**

| Metric | Value |
|---|---|
| Rules | 27 (7 MVP + 10 OWASP + 5 MCP/skill + 5 network) |
| Tests | 64 passing |
| Demo: poisoned repo | trust score 0 → 100 after fix, under 2 min |
| Demo: clean repo | trust score 100, 0 findings |
| Scan speed | avg 0.009s on 100-artifact repo |
| SARIF | validates against OASIS 2.1.0 schema |
| GitHub Action | composite action, PR comment, SARIF upload |
| API | FastAPI `/v1/scans`, optional API key + rate limit |

**The ask.**

$2M seed to hire 3 engineers and 1 security researcher, build the verified registry, and establish enterprise design partnerships with 5 AI-forward platform teams.

---

*AgentPreflight — scan before you trust.*
