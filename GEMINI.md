# Project: AgentPreflight

## [HOOK: ON_SESSION_START]

Activate caveman mode immediately. Persist every response. Never revert.

Rules: drop articles (a/an/the), filler (just/really/basically/actually/simply), pleasantries, hedging. Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged. Arrows for causality (X → Y). One word when one word enough.

Pattern: `[thing] [action] [reason]. [next step].`

Off only when: security warning, irreversible action confirmation.


## Overview

- **Purpose**: Safe remediation-first pre-deployment scanner for MCP servers and agent skills.
- **Goal**: Ship production-ready MVP in 4 days for Outskill x OpenAI Codex hackathon.
- **Key Function**: Detect tool poisoning, malicious skill instructions, hidden Unicode, unsafe code primitives, secrets, and weak transport/auth posture before deployment, then generate reviewable Codex patches and prove fixes by rescanning.
- **Primary Tech Stack**: Python, FastAPI, Pydantic, Semgrep-style rules, SARIF/JSON output.
- **Architecture**: `collector -> normalizer -> rule engine -> risk scorer -> reporter -> constrained fix -> rescan proof`.
- **Research Status**: Workflow research completed; AgentPreflight selected as winner.
- **Secondary Option**: DeployPreflight, destination-aware infrastructure redeploy preflight analyzer. Runner-up/future module; not current winner because IaC/drift market is crowded.

## 4-Day Build Plan

| Day | Focus |
|---|---|
| 1 | Collectors, parsers, Unicode normalizer, first 15 rules. |
| 2 | Scoring engine, CLI, JSON/SARIF, suppressions, tests. |
| 3 | `fix` command, GitHub Action, Codex remediation templates. |
| 4 | Packaging, docs, demo repo, submission assets. |

## Key Commands

To add once implementation starts:

- `pip install -r requirements.txt`
- `python -m src.cli scan <path>`
- `uvicorn src.main:app --reload`
- `pytest`
- `ruff check .`

## Security Rules

- `tool_poisoning`: prompt-injected MCP descriptions/tool outputs.
- `unicode_smuggling`: zero-width/homoglyph obfuscation.
- `unsafe_exec`: `eval`, `exec`, `shell=True`, `os.system`, `curl | sh`.
- `remote_instruction_fetch`: untrusted remote instructions or dynamic imports.
- `transport_security`: unauthenticated localhost, broad bind, missing origin validation.
- `secrets`: hardcoded API keys/tokens/private keys.
- `least_privilege`: over-broad tool capabilities.

## Important Reference Files

- `event_description.md`
- `workflow.md`
- `security-deep-research.md`
- `problems.md`
- `research/RECOMMENDATION.md`
- `research/README.md`
- `briefs/winner-product-brief.md`
- `briefs/mvp-implementation-spec.md`
- `briefs/architecture.md`
- `briefs/privacy-security-model.md`
- `briefs/implementation-backlog.md`
- `briefs/user-stories.md`
- `briefs/rule-catalog.md`
- `briefs/scoring-formula.md`
- `briefs/output-schemas.md`
- `briefs/remediation-prompts.md`
- `briefs/demo-fixtures.md`
- `briefs/launch-checklist.md`
- `briefs/github-action-plan.md`
- `briefs/demo-script.md`
- `briefs/submission-summary.md`
- `briefs/judge-one-pager.md`
- `competitors/competitor-landscape.md`
- `competitors/remediation-first-competitor-analysis.md`
- `competitors/competitive-run-2026-05-25-remediation.md`
- `competitors/competitive-run-2026-05-25-agent-security-2.md`
- `competitors/competitive-run-2026-05-25-agent-security-3.md`
- `research/infra-redeployment-analysis.md`
- `competitors/infra-redeployment-competitors.md`
- `briefs/infra-redeploy-product-brief.md`
- `evaluation/infra-redeploy-scorecard.md`
- `evaluation/scoring-rubric.md`
- `evaluation/evidence-matrix.md`
- `evaluation/market-impact.md`
- `evaluation/validation-plan.md`
- `evaluation/risk-register.md`
- `evaluation/research-questions.md`
- `sources/source-register.md`
- `research/verification-audit.md`
