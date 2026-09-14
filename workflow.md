# AgentPreflight: Build Instructions

## The One Problem

AI builders install MCP servers and agent skills from untrusted sources. Poisoned tool descriptions and malicious skill instructions can hijack an agent before runtime guardrails see anything. No static pre-deployment scanner with trust scoring and autofix exists as a developer-native tool.

**Ship**: `agentpreflight scan . --profile strict --fail-on high` → trust score → findings → `agentpreflight fix` → rescan proof. Under 2 minutes from fail to pass. There might be multiple agents working on it simulatenously so state your name and pick up a task. Update this file before you take a task in a common section.

Every decision, every feature, every research question should serve this one problem.

---

## How Agents Operate

1. Read this file at session start and every ~60 min.
2. Assess current state: what exists in `src/`, `tests/`, `research/`, `validation/`. Read the code.
3. Decide what to do next. Create your own task list based on the instructions below.
4. Write tasks into a `tasks/TRACK-[A|B|C]-TASKS.md` file as you discover them. Update status there.
5. After any feature: run tests, capture CLI output or screenshot, store proof in `validation/`.
6. Never mark a goal done without working proof.
7. When your current work is blocked or another agent is mid-edit on a file: pick something from the parallel goals list.

---

## Track A: Research

**Goal**: Keep the product sharp. Feed findings to Track B. Never stop learning what users actually need.

Start here: read `PRODUCT.md`, `SPEC.md`, `EVIDENCE.md`, `competitors/`. Understand what's been researched. Then go deeper.

**Research continuously:**

- Find real-world MCP and agent-skill poisoning incidents. What did attackers actually do? What would a static scanner have caught? Document in `research/`.
- Talk to users (proxy: you are the user). For each persona — AI builder installing an MCP server, AppSec engineer reviewing a PR, platform lead setting policy — ask: what pain are they in right now? What workaround do they use? What would make them trust a scanner? Write it down.
- Watch competitors. Open `competitors/`. Find the gaps. What do they not do? What can AgentPreflight own? Update findings.
- Validate the UX. Would a junior dev know what to do with a score of 47? Would an AppSec engineer trust a scan that takes 3 minutes? Test your assumptions. Improve the design.
- Design the demo narrative. Write the 90-second pitch as if demoing live. Exact CLI commands. Expected output. The emotional moment when the poisoned repo fails and the fix makes it pass.

**Keep asking**: Is the product still solving the right problem? Is there a sharper angle? Is there a user need we're missing that would make the demo land harder?

Document everything in `research/`. Feed insights to `workflow.md` or directly to Track B agent.

---

## Track B: Build

**Goal**: Ship working software. One feature at a time. Test before moving on.

Start here: read `SPEC.md` fully. Check `src/` for what exists. If nothing exists yet, start at the foundation.

**Build in this order** (do not skip ahead):

1. **Foundation first**: project scaffold, core data models (`Artifact`, `Finding`, `ScanResult`), path collector, file type classifier. Nothing else until this works.
2. **Rules next**: Unicode normalizer, rule engine skeleton, then rules one by one. For each rule: write it, write a malicious fixture, write a benign fixture, run both. Ship rules in order of severity — critical and high before medium and low. Target 20+ rules total.
3. **Score and output**: trust scorer (deductions, caps, verdicts), JSON reporter, SARIF reporter, CLI with Typer. Make the CLI output readable at a glance — trust score, findings, fix hints.
4. **Fix loop**: `agentpreflight fix` command, Codex patch templates (AP-MCP-001, AP-SKILL-002, AP-CODE-001), redaction before any model call, fix-rescan proof script.
5. **Demo repo**: `demo/poisoned/` that scores ≤50, `demo/clean/` that scores ≥90. These are the centerpiece of the demo.
6. **GitHub Action**: SARIF upload, PR comment, `--fail-on` exit code. Docs for wiring it into a workflow.
7. **Packaging**: `pip install .`, `agentpreflight --version`, FastAPI stub if time allows.

**When blocked on main build path**: check parallel goals below. Build demo fixtures, write tests for already-built modules, improve CLI output formatting, add suppression file support.

**Parallel goals** (safe to do anytime without touching the main build):

- Create demo fixtures in `demo/`
- Write tests for completed modules
- Polish CLI rich output
- Write suppression file parser
- Add `--quiet` and `--verbose` flags
- Benchmark scan speed on a 100-file repo

**After every feature**: `pytest`, capture output, store in `validation/`. Do not move to next feature until current one has proof.

---

## Track C: Validate

**Goal**: Ensure the product actually works. Find breaks before the demo. Make the demo irrefutable.

Start here: read `briefs/demo-script.md` and `briefs/launch-checklist.md`. Understand what needs to be true for the demo to land.

**Validate continuously** as Track B ships features:

- After every rule lands: run it on a malicious fixture and a benign fixture. Record pass/fail. Track false positive rate — keep it under 10% on real public MCP repos.
- After CLI ships: capture a screenshot of the full terminal output. Does it look good? Does it tell the story in under 10 lines?
- After scorer ships: verify the math against SPEC.md examples. Trust score 42 for that exact finding set.
- After SARIF ships: validate the output file against the SARIF 2.1.0 JSON schema. Zero violations.
- After fix command ships: run the full demo flow. Scan poisoned repo → run fix → rescan → score improves. Time it. Must be under 2 minutes.
- After GitHub Action ships: trigger it on a test branch. Screenshot the Security tab with findings visible.

**Regression policy**: after any Track B phase finishes, run the full test suite before the agent marks anything done. No regressions.

**Edge case sweep**: try empty `mcp.json`, binary files, deeply nested JSON, 100k-line Python file, Unicode-only filenames. Document what breaks. Report to Track B.

Store all screenshots and output captures in `validation/screenshots/`. Store all reports in `validation/`.

---

## Parallel Build Rules

When your current work is blocked:

- Track B blocked mid-feature? → Build demo fixtures, write tests for done modules, polish CLI output.
- Track A done with current research? → Start demo narrative, dig into competitive gaps, improve UX design.
- Track C waiting for a feature to land? → Run FP tests on existing rules, validate SARIF schema, document edge cases.
- Two agents in same file? → One waits or takes a different module. Never edit the same file simultaneously.

---

## Definition of Done

A goal is DONE only when:

- Code passes `pytest`
- CLI output or screenshot captured and stored in `validation/`
- Status updated in `tasks/TRACK-X-TASKS.md`
- No regressions in full test suite

---

## Milestones


| Date   | What must be true                                                                         |
| ------ | ----------------------------------------------------------------------------------------- |
| May 26 | Scanner runs. At least 5 rules fire correctly on fixtures. CLI scaffold exists.           |
| May 27 | Full scan pipeline: score + JSON + SARIF + CLI. Works end-to-end on demo/poisoned.        |
| May 28 | Fix loop works. Poisoned demo repo goes from fail to pass. Product brief + MVP submitted. |
| May 30 | Demo ready. GitHub Action works. Go-live version submitted.                               |

---

## Progress update - 2026-05-26

### Track A research

- Reviewed `problems.md`, `SPEC.md`, `PRODUCT.md`, `DEMO.md`, `EVIDENCE.md`, and competitor positioning.
- Confirmed AgentPreflight remains best 4-day winner path: offline MCP/skill scan -> trust score -> safe fix -> rescan proof.
- Added `research/implementation-research-2026-05-26.md` with source review, research conclusion, build decisions, and evidence-to-rule mapping.

### Track B build

- Implemented scan orchestrator: collector -> Unicode normalizer -> rule engine -> scorer -> result.
- Added CLI: `scan`, `fix`, `rules list`, and `--version`.
- Added JSON and SARIF output.
- Expanded rule set to 9 rules: `AP-MCP-001`, `AP-SKILL-001`, `AP-SKILL-002`, `AP-CODE-001`, `AP-CODE-002`, `AP-CODE-003`, `AP-SEC-001`, `AP-SEC-002`, `AP-SEC-003`.
- Added deterministic local fix loop for prompt override, skill injection, hidden Unicode, unsafe exec lines, dynamic exec, remote pipe, token redaction, and `.env` rename.
- Added demo repos under `demo/poisoned` and `demo/clean`.
- Added tests under `tests/`.

### Track C validation

- `pytest` passes: 7 tests.
- Poisoned demo: trust score 0, verdict fail, 10 findings.
- Clean demo: trust score 100, verdict pass, 0 findings.
- Fix-rescan proof on copied poisoned demo: score 0 -> 100.
- Reports stored:
  - `validation/pytest-output.txt`
  - `validation/poisoned-scan.txt`
  - `validation/clean-scan.txt`
  - `validation/poisoned-scan.json`
  - `validation/agentpreflight.sarif`
  - `validation/latest-fix-proof.txt`
- Screenshots stored:
  - `validation/screenshots/poisoned-cli.png`
  - `validation/screenshots/clean-cli.png`
  - `validation/screenshots/pytest.png`

### Next gaps

- Reach 20+ rules.
- Add official SARIF schema validation.
- Add GitHub Action wrapper and PR annotation path.
- Add Codex patch-prompt remediation mode beyond deterministic local sanitizers.

---

## Progress update - 2026-05-26 continued

### Track A research

- Reviewed `briefs/rule-catalog.md`, `briefs/github-action-plan.md`, and `briefs/output-schemas.md`.
- Confirmed next best work was rule breadth plus CI proof, not API surface.
- Added `research/implementation-research-2026-05-26-rules-and-ci.md`.

### Track B build

- Expanded rule catalog from 9 to 21 active rules.
- Added missing MCP rules: trust claims, untrusted result forwarding, loose schemas, privileged tools.
- Added missing skill rules: remote dependency, credential seeking, capability mismatch.
- Added code rules: arbitrary file access, network exfiltration.
- Added transport rules: broad bind, missing origin validation, plain HTTP remote tool.
- Added `.sh` collection as `code_sh`.
- Added composite GitHub Action in `action.yml`.
- Added sample workflow in `.github/workflows/agentpreflight.yml`.
- Added SARIF validator script in `scripts/validate_sarif.py`.
- Extended local fix loop to harden MCP schemas and clean new demo findings.

### Track C validation

- `pytest` passes: 12 tests.
- Active rule count: 21.
- Poisoned demo: trust score 0, verdict fail, 15 findings.
- Clean demo: trust score 100, verdict pass, 0 findings.
- Fix-rescan proof on copied poisoned demo: score 0 -> 100.
- SARIF validates against `https://json.schemastore.org/sarif-2.1.0.json`.
- New proof files:
  - `validation/rules-list.txt`
  - `validation/sarif-validation.txt`
  - `validation/screenshots/rules-list.png`
  - `validation/screenshots/sarif-validation.png`

### Remaining gaps

- Live GitHub Security tab screenshot not possible without remote repo run.
- PR comment markdown generator completed in later update below.
- Suppression file support completed in later update below.

---

## Progress update - 2026-05-26 final continuation

### Track A research

- Reviewed workflow parallel goals and GitHub Action/PR scorecard needs.
- Added `research/implementation-research-2026-05-26-suppressions-and-scorecard.md`.
- Research conclusion: reviewer workflow support matters next because AppSec/platform teams need auditable exceptions and PR-ready summaries.

### Track B build

- Added `.agentpreflight.json` suppression parser.
- Added scanner suppression filtering and `summary.suppressed`.
- Added CLI `--suppressions`.
- Added markdown PR scorecard reporter via `--format markdown`.
- Updated GitHub Action to emit SARIF, emit markdown scorecard, then enforce gate.
- Added tests for suppressions and markdown output.

### Track C validation

- `pytest` passes: 14 tests.
- Suppression proof: `validation/suppression-scan.txt` shows `suppressed=1`.
- PR scorecard proof: `validation/pr-comment.md`.
- Screenshots added:
  - `validation/screenshots/suppression-scan.png`
  - `validation/screenshots/pr-comment.png`

### Remaining gaps

- Live GitHub Security tab screenshot still requires remote Actions run.
- Benchmark proof completed in later update below.
- Suppression owner/expiry metadata completed in later update below.

---

## Progress update - 2026-05-26 benchmark and API

### Track A research

- Reviewed `SPEC.md`, `briefs/implementation-backlog.md`, and privacy model constraints.
- Added `research/implementation-research-2026-05-26-benchmark-and-api.md`.
- Research conclusion: benchmark proof and offline API stub support CI/platform adoption without changing core scanner trust model.

### Track B build

- Added `agentpreflight bench <target> --runs N`.
- Added suppression `owner` and `expires` metadata.
- Expired suppression entries no longer apply.
- Added FastAPI app in `src/agentpreflight/api/main.py`.
- Added endpoints:
  - `GET /healthz`
  - `POST /v1/scans`
- API rejects `offline=false` until remote triage is implemented.
- Added benchmark, expiry, and API tests.

### Track C validation

- `pytest` passes: 19 tests.
- 100-file benchmark proof: `validation/benchmark-100.txt`, screenshot `validation/screenshots/benchmark-100.png`.
- API proof: `validation/api-proof.txt`, screenshot `validation/screenshots/api-proof.png`.
- Benchmark result: 100 artifacts, 0 findings, 5 runs, avg about 0.009s.
- API result: clean demo scan returns trust score 100, verdict pass, 0 findings.

### Remaining gaps

- Live GitHub Security tab screenshot still requires remote Actions run.
- Inline suppression comments completed in later update below.
- API production hardening (auth/rate limits) remains post-MVP.

---

## Progress update - 2026-05-26 inline and prompts

### Track A research

- Reviewed `briefs/implementation-backlog.md`, `briefs/remediation-prompts.md`, and privacy model constraints.
- Added `research/implementation-research-2026-05-26-inline-and-prompts.md`.
- Research conclusion: inline suppressions and redacted prompt packs improve developer workflow without changing offline-first default.

### Track B build

- Added inline suppression directives:
  - `agentpreflight:disable-line AP-RULE`
  - `agentpreflight:disable-next-line AP-RULE`
- Added inline suppression filtering before file suppression filtering.
- Added `agentpreflight prompts <target> --output <file>`.
- Added redacted Codex remediation prompt pack builder.
- Added tests for inline suppressions and prompt pack redaction.

### Track C validation

- `pytest` passes: 23 tests.
- Inline suppression proof: `validation/inline-suppression.txt` shows score 100, pass, `suppressed=1`.
- Prompt pack proof: `validation/remediation-prompts.md`.
- Secret fixture token is redacted from prompt pack.
- Screenshots added:
  - `validation/screenshots/inline-suppression.png`
  - `validation/screenshots/remediation-prompts.png`

### Remaining gaps

- Live GitHub Security tab screenshot still requires remote Actions run.
- API auth/rate-limit middleware completed in later update below.

---

## Progress update - 2026-05-26 API security

### Track A research

- Reviewed privacy/security model and launch checklist concerns for API mode.
- Added `research/implementation-research-2026-05-26-api-security.md`.
- Research conclusion: API mode needs guardrails because service exposure can become new attack surface; CLI remains primary path.

### Track B build

- Added optional API key enforcement via `AGENTPREFLIGHT_API_KEY`.
- Added `x-agentpreflight-key` and `Authorization: Bearer` support.
- Added in-memory per-client rate limiting via `AGENTPREFLIGHT_RATE_LIMIT_PER_MINUTE`.
- Kept `/healthz` unauthenticated.
- Kept `/v1/scans` offline-only.
- Added API auth/rate-limit tests.

### Track C validation

- `pytest` passes: 25 tests.
- API auth proof:
  - missing key -> 401
  - wrong key -> 403
  - correct key -> 200
- API rate-limit proof:
  - first request -> 200
  - second request with limit 1/min -> 429
- Proof files:
  - `validation/api-security-proof.txt`
  - `validation/screenshots/api-security-proof.png`

### Remaining gaps

- Live GitHub Security tab screenshot still requires remote Actions run.

---

## Progress update - 2026-05-26 demo polish

### Track B build

- Updated README.md to demo-ready quality: installed `agentpreflight` CLI commands, pip install step, 90-second demo flow, rules table, all proof file references.
- Updated `validation/pytest-may26.txt` to current 25-test run.

### Track C validation

- `pytest` passes: 25 tests (all test files: rules, more_rules, scanner, suppressions, bench, prompt_builder, api).
- All validation proof files current.
- `agentpreflight --version` confirms CLI entry point installed correctly.

### Remaining gaps

- Live GitHub Security tab screenshot still requires remote Actions run with GitHub credentials.

---

## Progress update - 2026-05-27

### Track B build — 6 PRs raised (all pending merge)

| PR | Branch | What |
|---|---|---|
| #2 | `feature/owasp-dep-rules-flags` | 5 OWASP rules (AP-OWASP-001..005), AP-DEP-001 dep scanning, quiet/verbose flags. Rules 21→27. Tests 27→61. |
| #3 | `fix/strict-profile-fail-on` | `--profile strict --fail-on high` now escalates medium→high. Tests 61→64. |
| #4 | `docs/may-27-deliverables` | Investor pitch, user flow diagrams, workflow.md + CLAUDE.md updates. |
| #5 | `fix/cli-findings-truncation` | Table now shows "showing 12 of N findings — use --format json for full list" when clipped. |
| #6 | `fix/demo-script-accuracy` | Rewrote demo-script.md with real CLI output, correct paths, real rule IDs. |
| #7 | `docs/workflow-may27-progress2` | This update. |

### Track A research

- Confirmed all May 28 deliverables are in branches ready to merge: product brief (existing), investor pitch (PR #4), user flow diagrams (PR #4), demo script (PR #6).
- Edge case sweep run: empty mcp.json, binary files, unicode filenames — all handle cleanly (no crashes).

### Track C validation

- `pytest` passes: 26 tests on main (25 + truncation hint test from PR #5).
- Fresh scan proofs generated locally: `validation/poisoned-scan-may27.txt`, `validation/clean-scan-may27.txt`, `validation/pytest-may27.txt`.
- Truncation hint confirmed: poisoned demo shows "showing 12 of 15 findings — use --format json for full list".

### Remaining gaps

- Merge PRs #2–#7 to main to bring rule count, tests, and docs to current state.
- Live GitHub Security tab screenshot still requires remote Actions run.
- After PRs merge: run `agentpreflight rules list` and confirm 27 rules, capture as proof.
