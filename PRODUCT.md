# AgentPreflight: Product

## Canonical decision

Build **AgentPreflight** — safe remediation-first MCP and agent-skill preflight scanner with trust scoring.

Secondary researched option: **DeployPreflight** — destination-aware infra redeploy preflight. Keep as runner-up/future module. Full detail: `DEPLOY_PREFLIGHT.md`.

---

## Problem

AI builders install MCP servers and skills from GitHub, registries, and local folders. These artifacts mix natural-language tool descriptions, executable code, config, secrets, and permissions. A poisoned description or malicious skill can make an agent leak data, run unsafe commands, or follow hidden instructions before runtime guardrails see anything.

Existing AppSec tools scan code and dependencies. Runtime guardrails screen live interactions. The missing gate: pre-deployment trust scoring for MCP servers and agent skills.

---

## Solution

AgentPreflight scans `mcp.json`, `SKILL.md`, Markdown, Python/TypeScript scripts, and env-like files before merge, install, or deployment. It detects tool poisoning, hidden Unicode, unsafe execution primitives, secrets, remote instruction fetches, missing transport/auth hardening, and over-broad capabilities.

Output: one trust score (0–100), ranked findings, JSON/SARIF, Codex-generated remediation patches, and rescan proof. The product promise is not just "found" — it is "fixed and proven by rescan."

```bash
agentpreflight scan . --profile strict --fail-on high
agentpreflight fix . --apply --rules AP-MCP-001,AP-SKILL-002
agentpreflight scan . --profile strict --fail-on high   # rescan proof
```

---

## Why now

- OWASP has MCP and Agentic Skills security guidance.
- MCP spec warns clients to treat untrusted tool annotations as untrusted.
- MCPTox shows tool poisoning can succeed against real MCP servers in evaluated settings.
- Snyk ToxicSkills: 36.82% of scanned skills had at least one flaw; 13.4% had a critical issue.
- GitHub PR/CI workflows are the natural place to block risky agent extensions.
- 1M+ pull requests created by Copilot coding agent (May–Sep 2025); agent/tool review must fit CI.

---

## MVP scope

Four interfaces:

- CLI: `agentpreflight scan . --profile strict --fail-on high`
- Fix loop: `agentpreflight fix . --apply --rules AP-MCP-001,AP-SKILL-002,AP-CODE-001`
- API: `POST /v1/scans`
- GitHub Action: PR comment plus SARIF upload
- Demo repo: one clean agent, one poisoned agent

Core rule families: `tool_poisoning`, `unicode_smuggling`, `unsafe_exec`, `remote_instruction_fetch`, `secrets`, `transport_security`, `least_privilege`.

---

## 4-day build plan

| Day | Build |
|---|---|
| 1 | Collectors for MCP config, skills, Markdown, Python/TS files; Unicode normalizer; first 15 rules. |
| 2 | Scoring engine, CLI, JSON/SARIF, suppressions, test fixtures. |
| 3 | `fix` command for five high-confidence rules, Codex remediation prompt templates, demo poisoned repo. |
| 4 | Packaging, docs, benchmark timings, sample policies, release checklist, final demo. |

---

## MVP success metrics

- Catches 90%+ of seeded malicious fixtures.
- False positives under 10% on benign fixtures.
- Median scan under 30 seconds on small repos.
- Zero external API calls in default mode.
- SARIF loads correctly in GitHub code scanning.
- Fix loop moves poisoned demo repo from fail to pass in under two minutes.

---

## 10x remediation demo

1. Start with repo containing poisoned MCP tool description and malicious `SKILL.md`.
2. Run scanner. Trust score drops below threshold and CI fails.
3. Findings show exact lines and OWASP mappings.
4. `agentpreflight fix . --apply` applies deterministic local patches for flagged rules.
5. Patch rewrites tool description, strips hidden Unicode, replaces unsafe shell usage.
6. Rescan passes with higher trust score and SARIF report.

---

## Differentiation

The direct competitor landscape is crowded. AgentPreflight should not claim "first MCP/skill scanner," "unique trust score," "unique SARIF/CI," or "only autofix." Multiple competitors now have these.

**Safe positioning:**

> AgentPreflight combines MCP/skill preflight scanning, trust scoring, SARIF CI output, and Codex-assisted remediation in one developer workflow.

**Winning wedge:** time-to-fix. Existing scanners help teams find risk. AgentPreflight helps developers fix it in the same PR with constrained, auditable patches and rescan proof. Demo: failed poisoned repo → passing repo in under two minutes.

AgentPreflight is `npm audit fix` for agent extensions.

---

## Why it can win

- MCP/skill supply-chain risk is high-impact and documented.
- Four-day build is realistic.
- Codex remediation loop is core, constrained to reviewable high-confidence patches.
- Trust score + SARIF + fix + rescan demo is easy to understand and hard to dismiss as research.
- DeployPreflight has scale, but IaC/drift/remediation tooling is mature; scope creep risk is high.
- RAG and prompt-audit alternatives are weaker for demo and delivery.

---

## Candidate problem ranking

| Idea | Codex leverage | 4-day viability | Developer value | Market timing | Novelty | Total | Verdict |
|---|---:|---:|---:|---:|---:|---:|---|
| MCP and agent-skill preflight scanner | 5 | 5 | 5 | 5 | 2 | 22 | Build now as safe remediation-first |
| Infrastructure redeploy preflight | 5 | 4 | 5 | 5 | 2 | 21 | Runner-up / future module |
| RAG ingestion poisoning gate | 4 | 3 | 5 | 4 | 4 | 20 | Runner-up |
| System prompt leakage audit gate | 5 | 5 | 3 | 4 | 3 | 20 | Module/fallback |
| Codex config linter | 4 | 5 | 4 | 3 | 3 | 19 | Future module |
| Dynamic skill sandbox | 4 | 3 | 5 | 4 | 5 | 21 | Stretch after MVP |

---

## Judge-facing summary

AgentPreflight is a local-first security scanner for MCP servers and agent skills. Every agent extension gets a trust score before the agent runs it. Codex generates minimal reviewable remediation patches. A rescan proves the fix.

**Before:** Trust Score 31/100 FAIL — `agentpreflight fix` — **After:** Trust Score 92/100 PASS. Under two minutes.

---

## Submission-safe source language

Use:
- Snyk ToxicSkills: 3,984 skills scanned; 36.82% had at least one flaw; 13.4% had at least one critical issue.
- MCPTox: 72.8% attack success is one evaluated setting, not universal.
- OWASP MCP/Agentic Skills guidance supports the problem category.
- IBM 2025 breach report and GitHub Octoverse support impact/scale, not direct ROI proof.

Do NOT use: unverified model names, competitor acquisitions, exact adoption percentages, or dollar-impact estimates unless source is in `sources/source-register.md` or `EVIDENCE.md` (verification audit section) says verified.
