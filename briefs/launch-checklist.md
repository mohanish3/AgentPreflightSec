# Launch Checklist: MVP & Go-Live Gates

This document defines the Quality Gates and Launch Checklist required to verify **AgentPreflight** before submission.

---

## 1. Phase 1: Code Freeze & Integrity Gates
- [ ] **Unit Test Coverage**: Run `pytest` and verify that all parser, normalizer, and scoring tests pass.
- [ ] **Fixture Assertions**: Assert that the scanner catches 100% of the positive malicious fixtures in `demo/poisoned/`.
- [ ] **Negative Assertions**: Assert that the scanner triggers zero high-severity warnings on the negative benign fixtures in `demo/clean/`.
- [ ] **Exit-Code Verification**: Confirm the CLI returns exit code `1` when `--fail-on` is triggered, and `0` when all checks pass.
- [ ] **Code Linting**: Run `ruff check .` and format the codebase to PEP 8 standards.

---

## 2. Phase 2: Documentation & Spec Audit
- [ ] **CLI Quickstart**: Ensure the root `README.md` contains exact copy-pasteable installation and run commands.
- [ ] **API Schemas**: Verify that the FastAPI endpoints are fully documented in Swagger `/docs`.
- [ ] **Rule Registry**: Confirm every Rule ID flagged by the engine matches the documentation in the [Rule Catalog](rule-catalog.md).
- [ ] **Suppressions Guide**: Document how developers can use `# agentpreflight:disable-line AP-RULE` suppressions inside their extension repos.

---

## 3. Phase 3: Packaging & Release Gates
- [ ] **Lockfile Validation**: Verify all dependencies are strictly locked to avoid supply-chain breaks during judge testing.
- [ ] **Zero Network Default**: Double check that the default run requires zero external credentials, executing locally without hosted model keys.
- [ ] **SARIF Validation**: Validate that the exported `.sarif` file passes the official OASIS v2.1.0 schema validator.

---

## 4. Phase 4: Demo Verification
- [ ] **Dry-Run Fix**: Run `agentpreflight fix demo/poisoned` and verify fixable findings are listed with patch hints.
- [ ] **Score Improvement**: Run `agentpreflight fix demo/poisoned --apply` on a copy; verify trust score rises to **100** on rescan.
- [ ] **Action Integrity**: Run the custom GitHub Action on a mock pull request and confirm it publishes the comment report scorecard.
