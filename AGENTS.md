# Repository Guidelines

## Project Overview

AgentPreflight is a remediation-first MCP and agent-skill preflight scanner with trust scoring. It detects tool poisoning, hidden Unicode, unsafe execution primitives, secrets, remote instruction fetches, missing transport/auth hardening, and over-broad capabilities — before an agent runs.

## Project Structure

- `src/agentpreflight/` - main package: collectors, normalizers, rules, scorer, reporters, remediator, CLI, API
- `tests/` - pytest test suite
- `demo/` - poisoned and clean demo agent fixtures
- `fixtures/` - scanner test fixtures
- `briefs/` - product spec, rule catalog, scoring formula, output schemas, remediation prompts, demo materials
- `competitors/` - competitor landscape analysis
- `evaluation/` - evidence matrix, market impact, research questions
- `research/` - implementation research notes
- `sources/` - source register for research claims

## Source of Truth Files

Before coding, read:

- `SPEC.md` - architecture, rule catalog, scoring, output schemas, remediation prompts, backlog
- `briefs/mvp-implementation-spec.md` - command/API/rule spec
- `briefs/architecture.md` - module layout, data models, scan flow
- `briefs/rule-catalog.md` - MVP rule IDs and acceptance criteria
- `briefs/scoring-formula.md` - trust score calculation
- `briefs/output-schemas.md` - JSON/SARIF/CLI contracts
- `briefs/remediation-prompts.md` - Codex patch prompt templates
- `briefs/privacy-security-model.md` - offline guarantees and remediation safety
- `briefs/implementation-backlog.md` - P0-P3 build queue and cuts
- `briefs/user-stories.md` - product stories and acceptance criteria
- `briefs/demo-fixtures.md` - poisoned and clean demo data
- `briefs/launch-checklist.md` - MVP and go-live gates
- `briefs/github-action-plan.md` - SARIF and CI integration plan
- `evaluation/evidence-matrix.md` - rule-to-evidence mapping
- `evaluation/market-impact.md` - scale, ROI, and adoption evidence
- `sources/source-register.md` - URLs supporting claims

## Implementation Priority

CLI scan first → JSON/SARIF second → constrained `fix` command third → GitHub Action fourth → FastAPI last. Default scan mode must stay offline and deterministic.

## Build, Test, and Development Commands

```bash
pip install -e .          # install package in editable mode
agentpreflight scan .     # run scanner
pytest                    # run tests
ruff check .              # lint
```

## Coding Style

- Python: 4-space indent, descriptive names (`scan_mcp_manifest`, `risk_score`, `tool_finding`)
- Markdown: sentence-case headings, kebab-case filenames

## Testing Guidelines

Add focused tests for parser, scoring, and report-output behavior under `tests/`. Include fixtures for:

- poisoned `mcp.json`
- malicious `SKILL.md`
- hidden Unicode
- dangerous shell usage
- hardcoded secrets
- missing auth/transport hardening

## Security

Do not commit `.env`, API keys, or private data. Use `.env.example` for required settings. Scanner must be offline-first unless remote model triage is explicitly configured.
