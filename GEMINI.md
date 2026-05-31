# Project: AgentPreflight

## Overview

- **Purpose**: Safe remediation-first pre-deployment scanner for MCP servers and agent skills.
- **Key Function**: Detect tool poisoning, malicious skill instructions, hidden Unicode, unsafe code primitives, secrets, and weak transport/auth posture before deployment, then generate reviewable patches and prove fixes by rescanning.
- **Primary Tech Stack**: Python, FastAPI, Pydantic, SARIF/JSON output.
- **Architecture**: `collector -> normalizer -> rule engine -> risk scorer -> reporter -> constrained fix -> rescan proof`.
- **Secondary Option**: DeployPreflight, destination-aware infrastructure redeploy preflight analyzer. Runner-up/future module.

## Key Commands

- `pip install -e .`
- `agentpreflight scan <path> [--profile dev|balanced|strict] [--fail-on low|medium|high|critical]`
- `agentpreflight scan <path> --fail-on-score 70`  # fail if trust_score < 70
- `agentpreflight scan <path> --format json|sarif|markdown [--output file]`
- `agentpreflight fix <path> --apply`
- `agentpreflight fix <path> --codex`  # Codex AI patches (requires OPENAI_API_KEY)
- `agentpreflight rules list --description`  # include description column in table
- `agentpreflight rules list --applies-to code_py`  # filter by artifact type
- `agentpreflight rules list --severity critical --category unsafe_exec --json`
- `agentpreflight explain AP-CODE-001`  # top-level shortcut (alias for rules info)
- `agentpreflight rules info AP-CODE-001`
- `agentpreflight rules search "shell"`
- `agentpreflight watch <path>`  # rescan on file change
- `agentpreflight shell`  # interactive REPL
- `agentpreflight init`  # create .agentpreflight.json suppression template
- `agentpreflight profiles`  # show scoring profiles and deduction tables
- `uvicorn src.agentpreflight.api.main:app --reload`
- `pytest`
- `ruff check .`

## CLI Flags Added Post-MVP

- `--fail-on-score <int>` (1-100): gates CI on trust score; complementary to `--fail-on` severity
- `--description` on `rules list`: adds truncated description column to table output
- `--applies-to <type>` on `rules list`: filters rules by artifact type (code_py, skill_md, mcp_config, etc.); rules with `*` in applies_to always match

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
