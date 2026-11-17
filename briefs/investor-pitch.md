# AgentPreflight — 1-Page Investor Pitch

**The problem is invisible and growing fast.**

AI agents now install third-party MCP servers and skill packs much like developers install npm packages, but trust and behavior still need review. A poisoned tool description can redirect an agent to expose data, run commands, or follow hidden instructions before runtime controls intervene. Snyk's ToxicSkills study found flaws in 36.82% of 3,984 scanned skills and critical issues in 13.4%; static scanners already exist, so the opportunity is to improve clarity, remediation, and verification for agent-specific risks. See `EVIDENCE.md` for the study and source.

**AgentPreflight is the pre-deployment security gate for AI agents.**

One command — `agentpreflight scan . --profile strict --fail-on high` — audits MCP configs, skill prompts, Python/TypeScript scripts, and secrets in milliseconds. It returns a trust score (0–100), ranked findings, and machine-readable SARIF output that drops into GitHub's existing security tab. Unlike runtime guardrails (Llama Guard, Lakera), it runs statically before merge, costs nothing per conversation, and never sends code to a hosted endpoint.

**The loop is the wedge.**

Detection alone is not enough. AgentPreflight includes a fix loop: `agentpreflight fix . --apply` applies supported high-confidence patches, then reruns the scan to produce rescan evidence. The May 27 demo moved its seeded poisoned fixture from score 0 to 100 in under two minutes; reviewers can inspect the proposed or applied changes.

**Why now.**

MCP was released in November 2024. AgentPreflight targets the growing ecosystem of tools, skills, and configuration that agents rely on, while competing and adjacent scanners continue to evolve.

**Business model.**

- **Free CLI**: developer adoption, GitHub Stars, word-of-mouth.
- **Team plan**: policy management, suppression audit trail, PR comment integration. $20/seat/month.
- **Enterprise**: SSO, custom rule packs, SLA, on-prem deployment. $50k–$200k ACV.
- **Marketplace**: verified skill/MCP registry where publishers pay for a trust badge.

**Build snapshot (May 27, 2026; figures describe the delivery branch at that time).**

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
