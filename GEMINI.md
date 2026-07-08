# Project: AgentPreflight

## Overview

- **Purpose**: Safe remediation-first pre-deployment scanner for MCP servers and agent skills.
- **Key Function**: Detect tool poisoning, malicious skill instructions, hidden Unicode, unsafe code primitives, secrets, and weak transport/auth posture before deployment, then generate reviewable patches and prove fixes by rescanning.
- **Primary Tech Stack**: Python, FastAPI, Pydantic, SARIF/JSON output.
- **Architecture**: `collector -> normalizer -> rule engine -> risk scorer -> reporter -> constrained fix -> rescan proof`.
- **Secondary Option**: DeployPreflight, destination-aware infrastructure redeploy preflight analyzer. Runner-up/future module.

## Key Commands

- `pip install -e .`
- `agentpreflight scan <path>`
- `agentpreflight fix <path> --apply`
- `uvicorn src.agentpreflight.api.main:app --reload`
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

## Reference Files

- `SPEC.md` - architecture, rule catalog, scoring, output schemas
- `briefs/mvp-implementation-spec.md` - command/API/rule spec
- `briefs/architecture.md` - module layout, data models
- `briefs/rule-catalog.md` - MVP rule IDs and acceptance criteria
- `briefs/scoring-formula.md` - trust score calculation
- `briefs/output-schemas.md` - JSON/SARIF/CLI contracts
- `briefs/remediation-prompts.md` - patch prompt templates
- `briefs/privacy-security-model.md` - offline guarantees
- `briefs/implementation-backlog.md` - P0-P3 build queue
- `briefs/user-stories.md` - acceptance criteria
- `briefs/demo-fixtures.md` - poisoned and clean demo data
- `briefs/launch-checklist.md` - MVP and go-live gates
- `briefs/github-action-plan.md` - SARIF and CI integration
- `competitors/competitor-landscape.md` - competitor landscape
- `competitors/remediation-first-competitor-analysis.md` - direct scanner recheck
- `evaluation/evidence-matrix.md` - rule-to-evidence mapping
- `evaluation/market-impact.md` - scale and adoption evidence
- `evaluation/research-questions.md` - engineering research questions
- `sources/source-register.md` - source URLs
