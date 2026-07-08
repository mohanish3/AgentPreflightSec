# CLAUDE.md

Guidance for AI coding agents working in this repository.

## Current Direction

Build **AgentPreflight**, a safe remediation-first MCP and agent-skill preflight scanner with trust scoring.

Secondary researched option: **DeployPreflight**, a destination-aware infrastructure redeploy preflight analyzer. Keep as runner-up/future module unless user redirects. IaC scanning/drift tooling is mature and live destination checks need credentials/state/platform integrations.

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
4. `agentpreflight fix . --apply` (deterministic) / `--codex` (Codex AI proposals)
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

## Research Artifacts

| File | Contents |
|---|---|
| `PRODUCT.md` | Problem, solution, narrative, differentiation, success metrics |
| `SPEC.md` | Architecture, rule catalog, scoring, output schemas, remediation prompts, backlog |
| `DEMO.md` | Demo script, fixtures, GitHub Action plan, launch checklist |
| `COMPETITORS.md` | Competitor analysis, 10x thesis, differentiation |
| `EVIDENCE.md` | Incidents, CVEs, scale stats, validation plan, risk register, verification audit |
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
