# Implementation research - inline suppressions and prompt packs - 2026-05-26

## Repository research used

- `briefs/implementation-backlog.md`: local suppressions and Codex patch engine remain important P1/P2 items.
- `briefs/remediation-prompts.md`: Codex remediation needs redacted snippets, rule IDs, file context, and strict output instructions.
- `briefs/privacy-security-model.md`: prompt generation must not send data remotely by default and must redact secrets.
- `workflow.md`: validation requires proof artifacts and screenshots after each feature.

## Research conclusion

Inline suppressions and prompt packs improve developer workflow without weakening offline-first guarantees:

1. Inline suppressions handle one-off accepted findings close to code review context.
2. Prompt packs let Codex remediation be reviewed before any model call.
3. Redaction protects secrets inside generated remediation context.

## Implementation

- Added inline suppression directives:
  - `agentpreflight:disable-line AP-RULE`
  - `agentpreflight:disable-next-line AP-RULE`
- Inline suppressions count toward `summary.suppressed`.
- Added `agentpreflight prompts <target> --output <file>` command.
- Prompt pack includes system prompt, finding metadata, redacted snippets, and rule-specific remediation instructions.
- Added tests for inline suppressions and prompt redaction.

## Validation result

- `pytest`: 23 passed.
- Inline suppression proof: `validation/inline-suppression.txt` shows `suppressed=1` and pass verdict.
- Prompt pack proof: `validation/remediation-prompts.md`.
- Secret token pattern was not present in generated prompt pack.
- Screenshots:
  - `validation/screenshots/inline-suppression.png`
  - `validation/screenshots/remediation-prompts.png`
