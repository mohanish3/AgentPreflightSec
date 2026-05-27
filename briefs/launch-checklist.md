# Launch Checklist: MVP & Go-Live Gates

This document defines the Quality Gates and Launch Checklist required to verify **AgentPreflight** before submission.

---

## 1. Phase 1: Code Freeze & Integrity Gates
- [x] **Unit Test Coverage**: 30 tests pass (`validation/pytest-may27.txt`). Covers parsers, normalizer, scoring, suppressions, Codex API mock.
- [x] **Fixture Assertions**: Scanner catches 100% of seeded malicious fixtures. `trust_score=0 findings=15` on `demo/poisoned` (`validation/poisoned-scan-may27.txt`).
- [x] **Negative Assertions**: Scanner triggers zero warnings on clean fixtures. `trust_score=100 findings=0` on `demo/clean` (`validation/clean-scan-may27.txt`).
- [x] **Exit-Code Verification**: CLI exits 1 on `--fail-on high` with violations; exits 0 on clean scan.
- [ ] **Code Linting**: Run `ruff check .` before final go-live.

---

## 2. Phase 2: Documentation & Spec Audit
- [x] **CLI Quickstart**: `README.md` has copy-pasteable install + demo commands; verified against cold-run.
- [x] **Rule Registry**: 21 rules documented in README and `briefs/rule-catalog.md`; IDs match engine output.
- [x] **Suppressions Guide**: File suppression (`.agentpreflight.json`) and inline (`# agentpreflight:disable-line`) both documented in README and validated (`validation/suppression-scan.txt`, `validation/inline-suppression.txt`).
- [ ] **API Schemas**: FastAPI `/docs` available when running with `pip install ".[api]"`. Not required for MVP demo.

---

## 3. Phase 3: Packaging & Release Gates
- [x] **Zero Network Default**: Default scan is fully offline. No API key required. `offline=True` in all scan output.
- [x] **SARIF Validation**: SARIF 2.1.0 validates against schema (`validation/sarif-validation.txt`, `validation/agentpreflight.sarif`).
- [x] **Benchmark**: 113 artifacts scanned in 0.079s avg (`validation/benchmark.txt`).
- [ ] **Lockfile Validation**: Verify `pyproject.toml` pins before go-live (May 30).

---

## 4. Phase 4: Demo Verification
- [x] **Fix Loop**: `agentpreflight fix demo/poisoned --apply` → `fixable=14 changed=7` → rescan `trust_score=100` (cold-run May 27).
- [x] **Codex Mode**: `agentpreflight fix --codex` makes live `chat.completions.create` call to `codex-mini-latest`. Returns structured patch. (`codex_fix.py`).
- [x] **Score Improvement**: `trust_score=0 → 100` verified end-to-end with `--apply`. Codex mode requires OPENAI_API_KEY for live demo.
- [x] **SARIF in GitHub**: SARIF output format correct; GitHub Action YAML in `.github/workflows/agentpreflight.yml` uploads to Security tab.
- [ ] **Live Codex demo**: Run `fix --codex` with real OPENAI_API_KEY before May 30 go-live to verify end-to-end.
