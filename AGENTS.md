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

## CLI Reference (implemented commands)

```bash
# Core scan
agentpreflight scan <path> [--profile dev|balanced|strict] [--fail-on low|medium|high|critical]
agentpreflight scan <path> --fail-on-score 70   # fail if trust_score < 70
agentpreflight scan <path> --format json|sarif|markdown|github [--output file]
agentpreflight scan <path> --quiet              # one-line CI summary
agentpreflight scan <path> --verbose            # show ±2-line source context per finding
agentpreflight scan <path> --exclude 'tests/**' # glob exclusion
agentpreflight scan <path> --top 10            # limit table rows (0 = unlimited)
agentpreflight scan <path> --no-banner --exit-zero
agentpreflight scan <path> --list-files          # print affected file paths only (one per line, CI-scriptable)

# Remediation
agentpreflight fix <path> --apply              # deterministic offline patches (14 rule classes)
agentpreflight fix <path> --apply --prove      # apply then rescan and show delta
agentpreflight fix <path> --codex              # Codex AI patch proposals (requires OPENAI_API_KEY)
agentpreflight fix <path> --rules AP-CODE-001,AP-MCP-001  # target specific rules

# Rules
agentpreflight rules list                             # table of all 21 rules
agentpreflight rules list --description               # include description column (truncated to 60 chars)
agentpreflight rules list --severity critical         # filter by severity
agentpreflight rules list --category unsafe_exec      # filter by category
agentpreflight rules list --applies-to code_py        # filter by artifact type (code_py, skill_md, mcp_config, ...)
agentpreflight rules list --json                      # JSON array for programmatic use
agentpreflight rules info AP-CODE-001          # full rule detail panel
agentpreflight explain AP-CODE-001             # same as rules info — top-level shortcut
agentpreflight rules search "shell"            # keyword search across IDs, categories, descriptions

# Other commands
agentpreflight watch <path> [--interval 3]     # poll and rescan on file change
agentpreflight bench <path> [--runs 5]         # benchmark scan throughput
agentpreflight prompts <path>                  # build Codex remediation prompt pack
agentpreflight shell [path]                    # interactive REPL with session state
agentpreflight init [dir]                      # create .agentpreflight.json suppression template
agentpreflight profiles                        # show scoring profiles and deduction tables
```

## Key CLI flags added post-MVP

- `--fail-on-score <int>` (1-100): gates CI on trust score, complementing `--fail-on` severity. Example: `--fail-on-score 70` exits 1 if score < 70. Works with `--exit-zero`. Both `--fail-on` and `--fail-on-score` can be combined (OR logic).
- `--description` flag on `rules list`: adds a truncated description column to the rules table without changing other output.
- `explain <rule_id>`: top-level alias for `rules info`
- `--format github`: GitHub Actions annotation format (`::error`/`::warning`/`::notice` lines); displays inline on PR diffs without SARIF upload; works on all GitHub plans including free — `agentpreflight explain AP-CODE-001` reads more naturally after seeing a finding ID in scan output; reduces subcommand hierarchy friction.
- `--applies-to <type>` flag on `rules list`: filters by artifact type (code_py, code_js, code_sh, skill_md, mcp_config, env_file, markdown). Rules with `*` in their applies_to set always match. Combines with `--severity`, `--category`, `--description`, and `--json`.
- `--list-files`: prints only the paths of files that have findings, one per line. Suppresses all table/summary output. Exit code still controlled by `--fail-on`/`--fail-on-score`/`--exit-zero`. Designed for CI scripting: `agentpreflight scan . --list-files | xargs git diff HEAD --`.

## Post-MVP Feature Rationale

Why each post-MVP feature was added (sources: user-stories.md, briefs/user-flow.md, briefs/implementation-backlog.md):

**`scan --fail-on-score <int>`**
- Source: user-stories.md AC 2.1 requires CI to "block...extensions from merging" but severity thresholds alone are blunt - a repo with 10 medium findings (trust_score=30) would pass `--fail-on high` even though it is clearly risky. Score-based gating closes that gap. Teams already express risk appetite as numbers ("we require a trust score of at least 70") rather than just severity levels.
- Non-breaking: additive flag, existing `--fail-on` unchanged.

**`rules list --description`**
- Source: user-flow.md "Developer discovers an MCP security risk" - the typical first action after `rules list` is repeated `rules info <id>` calls to understand what each rule catches. Adding a truncated description column eliminates most of those lookups without changing the table for users who don't need it.
- Non-breaking: opt-in flag, default output unchanged.

**`rules list --applies-to <type>`**
- Source: briefs/rule-catalog.md shows 21 rules across 9 artifact types. A Python-only MCP server developer scanning for relevant rules would see JS-specific rules (code_js) that don't apply to their stack, creating noise. Filtering by artifact type surfaces only actionable rules.
- Non-breaking: additive flag, default output unchanged. Invalid type exits 1 with known-types hint.

**`scan --list-files`**
- Source: user-stories.md AC 2.1 AppSec persona needs "automated triage" - CI pipelines need to pass affected file paths to downstream tools (`git diff`, `pre-commit`, `slack notify`). A trust score and table are human-readable but not machine-parseable for scripting. `--list-files` outputs exactly the paths that need attention, one per line: `agentpreflight scan . --list-files | xargs ...`. Suppresses all table output; exit code still controlled by `--fail-on`/`--fail-on-score`.
- Non-breaking: additive flag, default table output unchanged.

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
