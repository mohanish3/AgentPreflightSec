# Implementation research - suppressions and scorecard - 2026-05-26

## Repository research used

- `workflow.md`: parallel goals include suppression file parser and CLI polish.
- `briefs/github-action-plan.md`: PR scorecard is required for AppSec review flow.
- `briefs/user-stories.md`: AppSec engineer and platform lead need auditable policy exceptions, not silent ignores.
- `briefs/privacy-security-model.md`: scanner should remain offline-first and deterministic.

## Research conclusion

Next useful feature after rule breadth was reviewer workflow support:

1. Suppressions let teams handle accepted risk without weakening rules globally.
2. Markdown scorecard turns CLI output into PR-ready review text.
3. Both remain offline and deterministic, fitting product trust model.

## Implementation

- Added `.agentpreflight.json` suppression support.
- Suppression format uses explicit `rule`, `path`, and `reason`.
- Scanner records suppressed count in `summary.suppressed`.
- CLI supports `--suppressions`.
- Markdown reporter emits PR scorecard via `--format markdown`.
- GitHub Action now writes SARIF, writes markdown scorecard, then enforces `--fail-on`.

## Validation result

- `pytest`: 14 passed.
- Suppression proof: `validation/suppression-scan.txt` shows 1 finding suppressed.
- PR scorecard artifact: `validation/pr-comment.md`.
- Screenshots:
  - `validation/screenshots/suppression-scan.png`
  - `validation/screenshots/pr-comment.png`
