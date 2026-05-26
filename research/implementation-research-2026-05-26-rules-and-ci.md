# Implementation research - rules and CI - 2026-05-26

## Repository research used

- `problems.md`: strongest wedge remains MCP and agent-skill trust verification before runtime.
- `briefs/rule-catalog.md`: MVP rule targets emphasize prompt injection, hidden Unicode, unsafe execution, weak transport, and hardcoded secrets.
- `SPEC.md`: full catalog expands to MCP schema/privilege checks, skill remote dependencies, file access, network egress, and transport rules.
- `briefs/github-action-plan.md`: required CI path is SARIF generation plus GitHub Security upload.
- `briefs/output-schemas.md`: SARIF 2.1.0 compatibility is required for GitHub integration.

## Research conclusion

Next best implementation leverage was not API work. It was rule coverage and CI proof.

Reason: AgentPreflight demo only lands if scanner catches mixed natural-language, config, code, secret, and transport risks in one offline pass. GitHub Action/SARIF support makes same proof useful for AppSec and platform teams.

## Implemented rule expansion

Rule count grew from 9 to 21:

- MCP: `AP-MCP-001` through `AP-MCP-005`
- Skills: `AP-SKILL-001` through `AP-SKILL-005`
- Code: `AP-CODE-001` through `AP-CODE-005`
- Secrets: `AP-SEC-001` through `AP-SEC-003`
- Transport: `AP-NET-001` through `AP-NET-003`

## CI/SARIF implementation

- Added `action.yml` composite action.
- Added `.github/workflows/agentpreflight.yml` sample security gate.
- Added `scripts/validate_sarif.py` using official SARIF 2.1.0 schema from `https://json.schemastore.org/sarif-2.1.0.json`.
- Validated generated SARIF successfully; proof in `validation/sarif-validation.txt`.

## Validation result

- `pytest`: 12 passed.
- `demo/poisoned`: score 0, fail, 15 findings.
- `demo/clean`: score 100, pass, 0 findings.
- Fix-rescan on copied poisoned demo: score 0 -> 100.
- Rule list screenshot stored in `validation/screenshots/rules-list.png`.
- SARIF validation screenshot stored in `validation/screenshots/sarif-validation.png`.
