# How Codex used for AgentPreflight build

## Scope
This document records Codex operating model used for implementation, validation, and overnight automation.

## 1) AGENTS setup and implementation workflow

### AGENTS control model
- Root `AGENTS.md` defines repository operating rules, structure, and roadmap priorities.
- Codex session starts by loading root instructions and applying them to all modified files.
- Instruction precedence: system/developer/user directives override AGENTS instructions when conflict exists.

### Implementation loop used
1. Read scoped requirements from `briefs/*` + `research/*`.
2. Implement bounded code/document change.
3. Run local validation (`pytest`, CLI smoke scans).
4. Commit atomic change with traceable message.
5. Repeat until MVP acceptance targets met.

## 2) Remote cloud runs on GitHub

### Purpose
- Execute clean-room scans in reproducible runner.
- Produce artifacts (JSON/SARIF/log) for review and gate decisions.

### Baseline pattern
- Trigger: pull request + manual dispatch.
- Steps:
  1. Checkout code.
  2. Install runtime.
  3. Run AgentPreflight scan on demo/fixture targets.
  4. Upload SARIF to Security tab.
  5. Upload logs/screenshots as workflow artifacts.

## 3) Codex CLI usage

### Local commands
- `PYTHONPATH=src python -m agentpreflight.cli.main scan demo/poisoned`
- `PYTHONPATH=src python -m agentpreflight.cli.main scan demo/clean`

### Remote control pattern
- Use shell scripts/CI jobs to invoke same CLI commands non-interactively.
- Persist outputs into artifact folder (`assets/screenshots/*.txt`, `reports/*.sarif`, `reports/*.json`).

## 4) Remote control of CLI

### Methods
- GitHub Actions job runner.
- Ephemeral VM/container session invoking deterministic command set.
- Optional scheduled cron workflow for repeated health scans.

### Controls
- Pin python/tool versions.
- Keep offline-first scan mode default.
- Fail fast on high/critical thresholds.

## 5) Script to schedule runs through night

Use script below as nightly wrapper.

```bash
#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="nightly-runs/$(date -u +%Y%m%d)"
mkdir -p "$OUT_DIR"

for hour in 00 02 04 06; do
  ts="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  PYTHONPATH=src python -m agentpreflight.cli.main scan demo/poisoned > "$OUT_DIR/poisoned-$ts.txt" || true
  PYTHONPATH=src python -m agentpreflight.cli.main scan demo/clean > "$OUT_DIR/clean-$ts.txt" || true
  sleep 7200
done
```

Recommended production variant: move schedule to GitHub Actions cron for better reliability than local sleep loops.
