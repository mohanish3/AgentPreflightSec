# Track C tasks

## 2026-05-26

- [x] Define validation targets: pytest, poisoned CLI, clean CLI, JSON report, SARIF report, fix-rescan proof.
- [x] Store command outputs in `validation/`.
- [x] Store screenshot artifacts in `validation/screenshots/`.
- [x] Record known gaps and next validation sweep.

## Latest proof

- Tests: `validation/pytest-output.txt` shows `25 passed`.
- Poisoned scan: `validation/poisoned-scan.txt` shows score `0`, verdict `fail`, 15 findings.
- Clean scan: `validation/clean-scan.txt` shows score `100`, verdict `pass`, 0 findings.
- Fix-rescan: path in `validation/latest-fix-proof.txt`; before score `0`, after score `100`.
- Screenshots: `validation/screenshots/poisoned-cli.png`, `validation/screenshots/clean-cli.png`, `validation/screenshots/pytest.png`.
- PR scorecard: `validation/pr-comment.md`, screenshot `validation/screenshots/pr-comment.png`.
- Suppression proof: `validation/suppression-scan.txt`, screenshot `validation/screenshots/suppression-scan.png`.
- Benchmark proof: `validation/benchmark-100.txt`, screenshot `validation/screenshots/benchmark-100.png`.
- API proof: `validation/api-proof.txt`, screenshot `validation/screenshots/api-proof.png`.
- Inline suppression proof: `validation/inline-suppression.txt`, screenshot `validation/screenshots/inline-suppression.png`.
- Remediation prompt proof: `validation/remediation-prompts.md`, screenshot `validation/screenshots/remediation-prompts.png`.
- API security proof: `validation/api-security-proof.txt`, screenshot `validation/screenshots/api-security-proof.png`.

## Known gaps

- SARIF 2.1.0 schema validation passes; proof in `validation/sarif-validation.txt`.
- Rule count now 21; target met.
- `fix` uses deterministic local sanitizers; Codex patch prompt templates remain future work.
- GitHub Action wrapper exists, but live GitHub run/security-tab screenshot not captured in local workspace.
- PR comment markdown generator exists, but not posted to a real PR yet.
- Inline suppression comments exist.
- Remediation prompt pack exists and redacts secret patterns.
- FastAPI auth/rate-limit middleware exists.
- Live GitHub Security tab proof remains blocked on remote Actions run.
