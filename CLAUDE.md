# CLAUDE.md

Guidance for AI coding agents working in this repository.

## [HOOK: ON_SESSION_START]

Activate caveman mode immediately. Persist every response. Never revert.

Rules: drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries, hedging. Fragments OK. Short synonyms (fix not "implement a solution for", big not extensive). Technical terms exact. Code blocks unchanged. Arrows for causality (X → Y). One word when one word enough.

Pattern: `[thing] [action] [reason]. [next step].`

Off only when: security warning, irreversible action confirmation, user asks to stop.


## Context

Hackathon workspace for Outskill x OpenAI Codex. Goal: ship a real AI product in four active build days.

Timeline:

- 26 May: kickoff
- 28 May: product brief + MVP due
- 30 May: final go-live version due

## Current Direction

Build **AgentPreflight**, a safe remediation-first MCP and agent-skill preflight scanner with trust scoring.

Secondary researched option: **DeployPreflight**, a destination-aware infrastructure redeploy preflight analyzer. Keep as runner-up/future module unless user redirects. It is valuable but weaker for this hackathon because IaC scanning/drift tooling is mature and live destination checks need credentials/state/platform integrations.

Use careful source language:

- Snyk ToxicSkills: 3,984 skills scanned; 36.82% had at least one flaw; 13.4% had at least one critical issue.
- MCPTox: 72.8% attack success is one evaluated setting, not universal.
- OWASP MCP/Agentic Skills guidance supports the problem category.
- IBM 2025 breach report and GitHub Octoverse support impact/scale, not direct ROI proof.
- Do not use unverified model names, competitor acquisitions, exact adoption percentages, or dollar-impact estimates unless source is in `sources/source-register.md` or `EVIDENCE.md` (verification audit section) says verified.

## Architecture

```text
collector -> normalizer -> rule engine -> risk scorer -> reporter -> constrained fix -> rescan proof
```

Priority order:

1. CLI: `agentpreflight scan . --profile strict --fail-on high`
2. JSON output
3. SARIF 2.1.0 output
4. `agentpreflight fix <path> --apply` for high-confidence rules
5. GitHub Action
6. FastAPI endpoint

## MVP Rules

- `tool_poisoning`
- `unicode_smuggling`
- `unsafe_exec`
- `remote_instruction_fetch`
- `secrets`
- `transport_security`
- `least_privilege`

## 4-Day Build Plan

| Day | Focus |
|---|---|
| 1 | Collectors, parsers, Unicode normalizer, first 15 rules. |
| 2 | Scoring engine, CLI, JSON/SARIF, suppressions, tests. |
| 3 | `fix` command, GitHub Action, Codex remediation templates, optional FastAPI stub. |
| 4 | Packaging, docs, demo repo, final demo. |

## Research Artifacts

| File | Contents |
|---|---|
| `PRODUCT.md` | Problem, solution, narrative, judge one-pager, candidate ranking |
| `SPEC.md` | Architecture, rule catalog, scoring, output schemas, remediation prompts, backlog |
| `DEMO.md` | Demo script, fixtures, GitHub Action plan, launch checklist |
| `COMPETITORS.md` | Competitor analysis, 10x thesis, differentiation |
| `EVIDENCE.md` | Incidents, CVEs, scale stats, validation plan, risk register, verification audit |
| `problems.md` | Problem ranking and 5-level analysis |
| `DEPLOY_PREFLIGHT.md` | DeployPreflight secondary product research |
| `sources/source-register.md` | All source URLs |

## Constraints

- Offline-first by default.
- No hosted model call in normal CI path.
- Optional Codex/model remediation gets only redacted finding snippets.
- Scan mode must be purely static: do not execute MCP servers or skill scripts.
- Fix mode must be constrained: patch only exact-line, high-confidence rule classes and require review.
- SARIF support is required for GitHub code scanning.
- Keep dynamic sandboxing, hosted dashboard, auth/billing, and full RAG sanitizer out of MVP.
