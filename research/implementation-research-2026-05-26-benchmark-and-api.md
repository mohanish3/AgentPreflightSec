# Implementation research - benchmark and API - 2026-05-26

## Repository research used

- `workflow.md`: validation requires scan speed proof and edge-case evidence.
- `SPEC.md`: API surface defines `POST /v1/scans` with offline path scan.
- `briefs/implementation-backlog.md`: FastAPI scanner API is P2 after CLI/SARIF/fix loop.
- `briefs/privacy-security-model.md`: API must preserve offline default and reject remote triage unless explicitly implemented.

## Research conclusion

Benchmark and API were best next work after PR/suppression flow:

1. Benchmark proof supports demo claim that scanner is fast enough for preflight and CI.
2. API stub unlocks future UI/webhook paths without changing scanner core.
3. Rejecting non-offline API requests keeps privacy model intact.

## Implementation

- Added `agentpreflight bench <target> --runs N` CLI command.
- Added suppression `owner` and `expires` metadata; expired suppressions no longer apply.
- Added FastAPI app:
  - `GET /healthz`
  - `POST /v1/scans`
- Added API dependencies to `pyproject.toml`.
- Added tests for benchmark CLI, expired suppressions, and API endpoints.

## Validation result

- `pytest`: 19 passed.
- 100-file benchmark: 100 artifacts, 0 findings, 5 runs, avg about 0.009s.
- API proof: `/healthz` 200; `/v1/scans` on clean demo returns score 100, pass, 0 findings.
- Screenshots:
  - `validation/screenshots/benchmark-100.png`
  - `validation/screenshots/api-proof.png`
