# Track B tasks

## 2026-05-26

- [x] Inspect current `src/`, `tests/`, `demo/`, and validation folders.
- [x] Add scan orchestrator around collector, normalizer, rule engine, scorer, and reporters.
- [x] Add Typer CLI for `scan`, `fix`, and `rules list`.
- [x] Add SARIF reporter.
- [x] Expand rule set from 5 to 9 rules: dynamic execution, hidden Unicode, API token, committed env file.
- [x] Add poisoned and clean demo repositories.
- [x] Add tests for scan, score, JSON, SARIF, CLI fail behavior, and hidden Unicode.
- [x] Capture validation outputs and screenshots.
- [x] Prove local fix loop on copied poisoned demo: score 0 -> 100.
- [x] Add remaining MVP rules toward 20+ total.
- [x] Add GitHub Action wrapper.
- [x] Add SARIF schema validation against official schema.
- [x] Add pytest coverage for rule expansion and fix-rescan loop.
- [x] Add PR comment markdown generator.
- [x] Add suppression file support.
- [x] Add benchmark command and 100-file scan proof.
- [x] Add FastAPI stub only if time remains.
- [x] Add suppression owner/expiry metadata.
- [x] Add inline suppression comments (`# agentpreflight:disable-line`) if time remains.
- [x] Add Codex remediation prompt pack generator.
- [x] Add API auth/rate-limit middleware if time remains.
- [ ] Add live GitHub Actions/security-tab proof when remote repo is available.
