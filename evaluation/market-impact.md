# Market impact and ROI

Purpose: explain why AgentPreflight affects many users and saves time/money.

## Adoption tailwind

GitHub Octoverse 2025 shows AI and agentic workflows moving into default developer workflow:

- 986M commits in 2025.
- 47.5M pull requests created, up 20.4%.
- 1.13M+ public repositories import generative AI SDKs, up 178% year over year.
- Roughly 80% of new GitHub users tried Copilot within their first week.
- 1M+ pull requests were created by Copilot coding agent between May and September 2025.

Implication: agent/tool/security review must fit PR and CI workflows. Manual review cannot keep pace.

## Security-cost tailwind

IBM Cost of a Data Breach Report 2025 reports:

- global average breach cost: $4.4M
- 97% of organizations with an AI-related security incident lacked proper AI access controls
- 63% lacked AI governance policies
- extensive AI/security automation was associated with $1.9M cost savings versus organizations without those solutions

Implication: CI-native AI governance and access-control checks have board-level cost relevance.

## Agent-skill risk tailwind

Snyk ToxicSkills reports:

- 3,984 skills scanned
- 534 skills, or 13.4%, had at least one critical issue
- 1,467 skills, or 36.82%, had at least one flaw
- 76 confirmed malicious payloads for credential theft, backdoors, and data exfiltration
- skills can inherit shell, filesystem, credential, and messaging access from agents

Implication: agent skills are not harmless prompts. They are executable supply-chain artifacts.

## Developer time saved

AgentPreflight saves time by turning review into one CI gate:

- no manual scan of `mcp.json`, `SKILL.md`, scripts, and env samples
- no repeated security explanation in PR comments
- SARIF routes findings to existing code-scanning UI
- Codex remediation handles first-pass fixes

Conservative time model:

- 15 minutes saved per agent-extension PR by automated scan and categorized findings
- 30-60 minutes saved per high-risk finding when Codex suggests targeted patch
- 1-2 days saved per team when bootstrapping agent-security policy, because rule packs and fixtures are included

## Business value claim

AgentPreflight is not breach insurance. It is a low-friction preventive control for agent extension supply chain risk. Value comes from catching poisoned tools/skills before they enter CI, developer laptops, or production agents.
