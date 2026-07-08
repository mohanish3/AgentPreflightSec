# AgentPreflight: Technical Specification

## Command surface

```bash
agentpreflight scan . --profile strict --fail-on high --format json
agentpreflight scan . --profile strict --format sarif --output agentpreflight.sarif
agentpreflight scan ./skills --checks skills --offline
agentpreflight fix . --apply --rules AP-MCP-001,AP-SKILL-002,AP-CODE-001
agentpreflight fix . --codex --rules AP-MCP-001          # Codex AI proposals (OPENAI_API_KEY)
agentpreflight rules list
```

## API surface

```http
POST /v1/scans
Content-Type: application/json
```

```json
{
  "target": {"type": "path", "path": "."},
  "profile": "strict",
  "fail_on": "high",
  "formats": ["json", "sarif"],
  "offline": true
}
```

---

## Architecture

### Module layout

```text
src/
  collectors/
    path_collector.py
    mcp_collector.py
    skill_collector.py
    code_collector.py
    env_collector.py
  normalizers/
    unicode.py
    text.py
    paths.py
  rules/
    engine.py
    catalog.py
  scorer/
    trust_score.py
  reporters/
    json_reporter.py
    sarif_reporter.py
  remediator/
    prompt_builder.py
    redactor.py
  cli/
    main.py
  api/
    main.py
```

### Scan pipeline

```text
target path
  -> path collector
  -> artifact collectors (MCP config, skills, code, env)
  -> unicode/text normalization
  -> rule engine
  -> finding list
  -> trust scorer
  -> JSON/SARIF reporters
  -> optional remediation prompt generation
  -> rescan proof
```

### Core data models

```python
class Artifact:
    path: str
    kind: str
    content: str
    normalized_content: str
    metadata: dict

class Finding:
    id: str
    severity: str
    category: str
    title: str
    path: str
    line: int | None
    evidence: str
    risk: str
    fix: str
    references: list[str]

class ScanResult:
    target: str
    profile: str
    trust_score: int
    verdict: str
    findings: list[Finding]
    summary: dict
```

### Rule interface

```python
class Rule:
    id: str
    severity: str
    category: str
    applies_to: set[str]

    def check(self, artifact: Artifact) -> list[Finding]:
        ...
```

### Profiles

| Profile | Use | Behavior |
|---|---|---|
| `dev` | local experimentation | warn on medium/high, fail only critical |
| `balanced` | default | fail critical/high |
| `strict` | CI/security review | fail critical/high, elevate suspicious combos |

### Error handling

- Unreadable files become low-severity warnings unless path is required config.
- Malformed JSON/TOML/YAML becomes medium/high depending on artifact type.
- Binary files skipped unless name suggests secret/key material.
- Scanner never executes collected files.

---

## Rule catalog

Rule IDs are stable for JSON/SARIF output.

### MCP rules

| ID | Severity | Finding | Detection |
|---|---|---|---|
| AP-MCP-001 | high | Prompt override in tool description | Tool description contains override phrases: ignore previous, system override, developer message, urgent bypass, exfiltrate, reveal secrets. |
| AP-MCP-002 | medium | Over-assertive tool annotation | Annotation claims safety/trust without source or policy backing. |
| AP-MCP-003 | high | Tool result can carry executable instruction | Tool returns untrusted text intended to be passed directly to model without boundary marking. |
| AP-MCP-004 | medium | Missing/loose input schema | Tool accepts arbitrary object/string without required field validation. |
| AP-MCP-005 | high | Privileged tool exposed to untrusted context | Tool can read files, env, email, shell, browser, or network and is callable from external/untrusted context. |

### Skill rules

| ID | Severity | Finding | Detection |
|---|---|---|---|
| AP-SKILL-001 | high | Prompt injection language in `SKILL.md` | Skill instructions include override, bypass, hidden priority, or instruction hierarchy manipulation. |
| AP-SKILL-002 | high | Hidden Unicode instruction | Zero-width, bidi, homoglyph, or suspicious non-printing control characters in model-facing docs. |
| AP-SKILL-003 | medium | Remote instruction dependency | Skill asks agent to fetch or follow remote text at runtime. |
| AP-SKILL-004 | high | Credential-seeking skill behavior | Skill references env vars, tokens, keychains, cookies, or auth files without clear need. |
| AP-SKILL-005 | medium | Capability mismatch | README claims narrow function but scripts include shell, filesystem, or network primitives. |

### Code rules

| ID | Severity | Finding | Detection |
|---|---|---|---|
| AP-CODE-001 | critical | Unsafe shell execution | `os.system`, `subprocess(..., shell=True)`, `child_process.exec`, backticks with user input. |
| AP-CODE-002 | high | Dynamic code execution | `eval`, `exec`, `Function`, dynamic import from variable/URL. |
| AP-CODE-003 | critical | Remote script execution | `curl \| sh`, `wget \| bash`, downloaded code executed directly. |
| AP-CODE-004 | high | Arbitrary file read/write | Path from user/model input reaches file read/write without allowlist. |
| AP-CODE-005 | high | Network exfiltration primitive | Reads secret/env/file then sends HTTP request in same flow or file. |

### Secret rules

| ID | Severity | Finding | Detection |
|---|---|---|---|
| AP-SEC-001 | critical | Private key material | PEM private key block or SSH private key block. |
| AP-SEC-002 | high | API token pattern | Common token/key regex in source, config, or docs. |
| AP-SEC-003 | medium | `.env` committed | `.env` or equivalent secret-bearing file present outside examples. |

### Transport rules

| ID | Severity | Finding | Detection |
|---|---|---|---|
| AP-NET-001 | high | Broad bind address | Server binds `0.0.0.0`/`::` without auth or explicit allow. |
| AP-NET-002 | high | Missing origin validation | Local HTTP/WebSocket server accepts requests without Origin/Host checks. |
| AP-NET-003 | medium | Plain HTTP remote tool | Remote MCP/tool URL uses HTTP instead of HTTPS. |

### Rule acceptance criteria

- Every rule has one malicious fixture and one benign fixture.
- Every finding includes path, line when available, severity, category, evidence, and fix.
- SARIF output validates against SARIF 2.1.0 schema.
- CLI exits nonzero when severity is at or above `--fail-on`.
- Default scan performs no network call.

---

## Trust scoring formula

### Base score

Start every scan at `100`.

### Severity deductions

| Severity | Deduction |
|---|---:|
| critical | 30 |
| high | 15 |
| medium | 7 |
| low | 2 |

### Caps (applied after deductions)

| Condition | Max score |
|---|---:|
| any critical finding | 50 |
| three or more high findings | 60 |
| secret finding | 55 |
| unsafe shell plus network egress in same artifact | 45 |
| hidden Unicode plus prompt override in same artifact | 50 |
| privileged file/env access plus remote instruction fetch | 45 |

### Verdicts

| Score | Verdict |
|---:|---|
| 85–100 | pass |
| 70–84 | warn |
| 0–69 | fail |

`--fail-on` can fail scan even when score is above 70.

### Profile modifiers

| Profile | Modifier |
|---|---|
| `dev` | critical fails; high warns; no caps except secret/critical |
| `balanced` | default formula |
| `strict` | medium counts as high for fail-on; combo caps enabled |

### Example

Findings: one critical unsafe shell, two high prompt/Unicode findings, one medium schema finding.

```text
100 - 30 - 15 - 15 - 7 = 33
Caps: any critical → max 50
Final: 33/100 fail
```

---

## Output schemas

### JSON scan result

```json
{
  "schema_version": "1.0",
  "tool": "AgentPreflight",
  "target": ".",
  "profile": "strict",
  "offline": true,
  "trust_score": 42,
  "verdict": "fail",
  "summary": {
    "critical": 1,
    "high": 3,
    "medium": 2,
    "low": 0,
    "files_scanned": 18,
    "rules_run": 24
  },
  "findings": [
    {
      "id": "AP-MCP-001",
      "severity": "high",
      "category": "tool_poisoning",
      "title": "Prompt-like override in MCP tool description",
      "path": "mcp.json",
      "line": 12,
      "evidence": "description references external maintenance instructions",
      "risk": "Model may treat untrusted tool metadata as instruction.",
      "fix": "Rewrite tool description as neutral capability text.",
      "fix_available": true,
      "fix_mode": "codex_patch",
      "references": ["OWASP MCP Tool Poisoning", "MCPTox"]
    }
  ],
  "score": {
    "base": 100,
    "deductions": [
      {"severity": "high", "count": 3, "points": 45}
    ],
    "caps_applied": [],
    "final": 42
  }
}
```

### JSON finding contract

Required: `id`, `severity`, `category`, `title`, `path`, `evidence`, `risk`, `fix`, `fix_available`.

Optional: `line`, `column`, `end_line`, `references`, `snippet_hash`, `fix_mode`, `patch_preview`.

### SARIF mapping

| JSON field | SARIF field |
|---|---|
| `id` | `ruleId` |
| `title` | `message.text` |
| `severity` | `level` |
| `path` | `locations[].physicalLocation.artifactLocation.uri` |
| `line` | `locations[].physicalLocation.region.startLine` |
| `risk` + `fix` | `properties` |

Severity → SARIF level: `critical/high` → `error`, `medium` → `warning`, `low` → `note`.

### CLI human output

```text
AgentPreflight scan
Target: .
Profile: strict
Trust score: 42/100
Verdict: fail

Critical: 1  High: 3  Medium: 2  Low: 0

[HIGH] AP-MCP-001 mcp.json:12
Prompt-like override in MCP tool description
Fix: Rewrite tool description as neutral capability text.

SARIF: agentpreflight.sarif
JSON: agentpreflight.json
```

### JSON fix result

```json
{
  "schema_version": "1.0",
  "tool": "AgentPreflight",
  "mode": "fix",
  "input": "agentpreflight.json",
  "patches": [
    {
      "finding_id": "AP-MCP-001",
      "path": "mcp.json",
      "status": "patched",
      "strategy": "neutral_tool_description_rewrite",
      "requires_review": true
    }
  ],
  "rescan_required": true
}
```

### Exit codes

| Code | Meaning |
|---:|---|
| 0 | scan completed and policy passed |
| 1 | scan completed and policy failed |
| 2 | scanner usage/config error |
| 3 | scan could not complete |

---

## Remediation prompt templates

Purpose: keep Codex remediation scoped, auditable, and safe.

### General contract

Inputs: rule ID, severity, file path, redacted snippet, finding evidence, desired fix.

Outputs: minimal patch, short explanation, no unrelated refactor, no new dependency unless required, no new network/file capability.

### AP-MCP-001: tool poisoning

```text
You are fixing an AgentPreflight finding.

Rule: AP-MCP-001
Severity: high
Problem: MCP tool description contains prompt-like override or untrusted instruction text.

Patch only the flagged tool description. Rewrite it as neutral capability text.
Do not add new behavior. Do not mention hidden instructions, priority, authorization,
secrets, or external maintenance files.

File: {path}
Snippet:
{snippet}

Return a unified diff only.
```

### AP-SKILL-002: hidden Unicode

```text
You are fixing an AgentPreflight finding.

Rule: AP-SKILL-002
Severity: high
Problem: Skill instructions contain hidden Unicode or invisible control characters.

Patch only the flagged lines. Remove invisible/control characters.
Preserve visible benign instructions. If hidden text changes meaning, remove that hidden instruction.

File: {path}
Snippet:
{snippet}

Return a unified diff only.
```

### AP-CODE-001: unsafe shell execution

```text
You are fixing an AgentPreflight finding.

Rule: AP-CODE-001
Severity: critical
Problem: User/model-controlled input reaches unsafe shell execution.

Patch only the unsafe call. Replace shell string execution with safe argument-list execution.
Do not introduce shell=True. Do not add new dependencies.
Validate or allowlist user-controlled arguments when practical.

File: {path}
Snippet:
{snippet}

Return a unified diff only.
```

### Redaction rules

Before building prompt:
- replace secrets with `[REDACTED_SECRET]`
- replace tokens with `[REDACTED_TOKEN]`
- replace private keys with `[REDACTED_PRIVATE_KEY]`
- truncate snippet to smallest useful context

### Review policy

Generated patches are suggestions. User or CI must review patch before merge.

---

## Privacy and security model

### Default guarantee

`agentpreflight scan` is offline by default. Reads local files, writes local reports. Must not make network calls, execute scanned code, or upload source.

### Threat model

Protects against: poisoned MCP tool metadata, malicious skill instructions, hidden Unicode and prompt smuggling, unsafe shell/code execution patterns, secret leakage in agent-extension files, weak local transport/auth posture.

Does NOT fully protect against: runtime-only behavior behind dynamic dependencies, novel prompt injections missed by rules, malicious packages installed after scan, model behavior under all possible prompts, compromised CI runners.

### Remediation mode

Remediation is opt-in. Before any model/Codex call:

1. Select one finding.
2. Extract minimal surrounding snippet.
3. Redact secrets and tokens.
4. Include rule ID, severity, risk, and desired fix.
5. Never send whole repo by default.

### Redact before sending

API keys, private keys, bearer tokens, cookies, passwords, `.env` values, URLs with credentials, email/password pairs.

### Auditability

Every remote remediation call logged locally: timestamp, provider/model string, rule ID, file path, redaction count, token/cost estimate when available. Do not log unredacted prompt snippets.

---

## User stories

### Developer installing MCP server

Run one local command before wiring into agent. Output includes trust score, pass/warn/fail, and exact findings with file, line, evidence, fix.

### AppSec engineer

SARIF output from every scan. GitHub Action uploads SARIF. Findings map to stable AP-* rule IDs. `--fail-on high` fails job.

### AI platform lead

Reusable policy profiles: `balanced` locally, `strict` in CI. JSON output includes active profile.

### Hackathon judge

Poisoned repo fails, gets patched by Codex, passes — in under two minutes. Demo repo has believable malicious MCP/skill payloads. Remediation creates visible diff. Second scan passes.

### Security-conscious enterprise user

No network calls during `scan`. Remediation disabled unless explicitly requested. Redaction runs before any optional model call.

---

## Implementation backlog

### P0: irreducible MVP

- CLI command: `agentpreflight scan <path>`.
- Path walker with ignore rules for `.git`, `node_modules`, `.venv`, `dist`, `build`.
- Collectors for `mcp.json`, `SKILL.md`, Markdown, Python, JS/TS, env-like files.
- Unicode normalizer and hidden-character detector.
- Rule engine with at least 20 rules.
- Trust score from severity-weighted findings.
- JSON reporter.
- SARIF reporter.
- `--fail-on` exit code.
- Malicious and benign fixtures for each rule family.
- `agentpreflight fix <findings.json>` for top high-confidence rule classes.
- Rescan proof in demo: fail → patch → pass.

### P1: hackathon differentiators

- GitHub Action wrapper.
- SARIF upload workflow docs.
- Codex remediation prompt templates and patch generators for AP-MCP-001, AP-SKILL-002, AP-CODE-001.
- Suppression file with expiry.
- Demo poisoned repo.
- README quickstart.

### P2: polish

- FastAPI `POST /v1/scans`.
- HTML report.
- Configurable YAML rule packs.
- Benchmark timing output.
- More language collectors.

### P3: post-hackathon

- Dynamic skill sandbox.
- RAG ingestion gate.
- Prompt-hardening rule pack.
- Hosted dashboard.
- Marketplace scan reports.

### Cut order if time slips

1. Cut FastAPI.
2. Cut HTML report.
3. Cut TypeScript-specific AST handling; keep text-pattern checks.
4. Cut configurable rule DSL; hardcode rule catalog.
5. Cut all remediation except top 3 rule IDs.

Do not cut: trust score, JSON, SARIF, CLI exit code, poisoned demo repo, at least one Codex remediation path, rescan proof after remediation.
