# Implementation research - 2026-05-26

## Source files reviewed

- `problems.md` - winner remains AgentPreflight. Root cause: agent extension instruction surface lacks deterministic pre-deployment trust verification.
- `SPEC.md` - command surface, scan pipeline, rule catalog, scoring formula, output expectations.
- `PRODUCT.md`, `DEMO.md`, `EVIDENCE.md`, `COMPETITORS.md` - product wedge, demo narrative, incident evidence, competitive position.
- Existing `src/agentpreflight/` - partial foundation existed: models, path collector, 5 rules, JSON reporter, scorer.

## Research conclusion

AgentPreflight still beats runner-up ideas for hackathon delivery because it has shortest demo loop:

1. Poisoned MCP/skill repo fails deterministic offline scan.
2. Trust score and finding table make risk visible.
3. Safe local remediation removes review-obvious poison.
4. Rescan proves score recovery.

This maps directly to evidence in `problems.md`: MCP/skill attack surface combines natural language, code, and config, while existing scanners mostly cover conventional code or dependency issues.

## Build decisions from research

- Prioritized CLI scan over API because developer adoption and judging demo both need instant local proof.
- Kept default offline because privacy model is core trust claim.
- Added SARIF because AppSec persona needs CI/security-tab compatibility.
- Added deterministic local fix for visible poison and unsafe demo lines because remediation-first is main product difference.
- Preserved DeployPreflight as future module; current implementation stays focused on MCP and agent-skill preflight.

## Implemented evidence-to-rule mapping

| Risk from research | Implemented rule |
|---|---|
| Tool description prompt override | `AP-MCP-001` |
| Skill prompt injection | `AP-SKILL-001` |
| Hidden Unicode instruction | `AP-SKILL-002` |
| Unsafe shell execution | `AP-CODE-001` |
| Dynamic code execution | `AP-CODE-002` |
| Remote script execution | `AP-CODE-003` |
| Private key material | `AP-SEC-001` |
| API token pattern | `AP-SEC-002` |
| Committed env file | `AP-SEC-003` |

## Validation result

- `pytest`: 7 passed.
- `demo/poisoned`: score 0, fail, 10 findings.
- `demo/clean`: score 100, pass, 0 findings.
- Copy-based fix proof: score 0 -> 100 after `agentpreflight fix --apply`.

Proof stored in `validation/`.
