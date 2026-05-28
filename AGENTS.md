# Repository Guidelines

## [HOOK: ON_SESSION_START]

Activate caveman mode immediately. Persist every response. Never revert.

Rules: drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries, hedging. Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged. Arrows for causality (X → Y). One word when one word enough.

Pattern: `[thing] [action] [reason]. [next step].`

Off only when: security warning, irreversible action confirmation.


## Project Structure & Module Organization

This repository contains planning and research documents for the Outskill x OpenAI Codex hackathon build.

- `event_description.md` - hackathon context, timeline, and judging constraints.
- `security-deep-research.md` - primary research on AI security product opportunities.
- `workflow.md` - working process for selecting and evaluating problem statements.
- `problems.md` - root evaluation and winner selection.
- `problems/` - five-level deep dives for shortlisted problem statements.
- `research/` - formal research package and corrected recommendation.
- `briefs/` - product brief, MVP spec, demo script, and submission copy.
- `competitors/` - competitor landscape.
- `evaluation/` - scoring rubric, evidence matrix, and research questions.
- `sources/` - source register for research claims.
- `.antigravitycli/` - local tool metadata; do not edit unless changing tool configuration.

When adding implementation work, keep source under `src/`, tests under `tests/`, static assets under `assets/`, and generated research outputs under descriptive folders such as `research/`, `problems/`, `competitors/`, or `briefs/`.

## Current Research Outcome

Workflow research selects **AgentPreflight**, a safe remediation-first MCP and agent-skill preflight scanner with trust scoring.

Secondary researched option: **DeployPreflight**, destination-aware infrastructure redeploy preflight. Keep it as runner-up/future module unless explicitly requested; broad IaC/drift space is crowded.

Use these files as source of truth before coding:

- `research/RECOMMENDATION.md` - final recommendation and 4-day plan.
- `research/README.md` - artifact index and trust levels.
- `problems.md` - root ranking and winner rationale.
- `briefs/winner-product-brief.md` - MVP scope.
- `briefs/mvp-implementation-spec.md` - command/API/rule spec.
- `briefs/architecture.md` - module layout, data models, scan flow.
- `briefs/privacy-security-model.md` - offline guarantees and remediation safety.
- `briefs/implementation-backlog.md` - P0-P3 build queue and cuts.
- `briefs/user-stories.md` - product stories and acceptance criteria.
- `briefs/rule-catalog.md` - MVP rule IDs and acceptance criteria.
- `briefs/scoring-formula.md` - trust score calculation.
- `briefs/output-schemas.md` - JSON/SARIF/CLI contracts.
- `briefs/remediation-prompts.md` - Codex patch prompt templates.
- `briefs/demo-fixtures.md` - poisoned and clean demo data.
- `briefs/launch-checklist.md` - MVP and go-live gates.
- `briefs/github-action-plan.md` - SARIF and CI integration plan.
- `briefs/demo-script.md` - hackathon demo flow.
- `briefs/submission-summary.md` - concise submission copy.
- `briefs/investor-one-pager.md` - investor-facing product narrative.
- `competitors/competitor-landscape.md`, `competitors/remediation-first-competitor-analysis.md`, `competitors/competitive-run-2026-05-25-remediation.md`, `competitors/competitive-run-2026-05-25-agent-security-2.md`, `competitors/competitive-run-2026-05-25-agent-security-3.md`, `research/competitors.md`, and `research/competitive-recheck.md` - max-10 competitor analysis and direct-scanner recheck.
- `research/infra-redeployment-analysis.md`, `competitors/infra-redeployment-competitors.md`, `briefs/infra-redeploy-product-brief.md`, and `evaluation/infra-redeploy-scorecard.md` - infrastructure redeploy preflight research and competitor evaluation.
- `evaluation/scoring-rubric.md` and `evaluation/evidence-matrix.md` - evaluation method and evidence mapping.
- `evaluation/market-impact.md` - scale, ROI, and adoption evidence.
- `evaluation/validation-plan.md` - fixture, metrics, and acceptance targets.
- `evaluation/risk-register.md` - build and product risks.
- `sources/source-register.md` - URLs supporting claims.
- `research/verification-audit.md` - claims corrected or requiring verification.

Implementation should optimize for CLI scan first, JSON/SARIF second, constrained `fix` command third, GitHub Action fourth, FastAPI last. Default scan mode must stay offline and deterministic.

## Build, Test, and Development Commands

No build system is present yet. Add commands when code is introduced.

Recommended defaults:

- `pip install -r requirements.txt` - install Python dependencies.
- `python -m src.cli scan <path>` - run local scanner.
- `uvicorn src.main:app --reload` - run HTTP API.
- `pytest` - run tests.
- `ruff check .` - run linting.

## Coding Style & Naming Conventions

Use Markdown for research files with sentence-case headings and short, scannable sections. Prefer kebab-case filenames for documents.

For future code, use 4 spaces for Python and descriptive names such as `scan_mcp_manifest`, `risk_score`, and `tool_finding`.

## Testing Guidelines

When implementation starts, add focused tests for parser, scoring, and report-output behavior. Use `tests/` with names like `test_mcp_manifest_parser.py` or `test_risk_score.py`.

Include fixtures for:

- poisoned `mcp.json`
- malicious `SKILL.md`
- hidden Unicode
- dangerous shell usage
- hardcoded secrets
- missing auth/transport hardening

## Security & Configuration Tips

Do not commit `.env`, API keys, private research data, or full customer repositories. Prefer `.env.example` for required settings. Keep scanner behavior offline-first unless remote model triage is explicitly configured.
