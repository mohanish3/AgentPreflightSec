# Rule Catalog: AgentPreflight Rule Specifications

This catalog documents all 21 security rules enforced by AgentPreflight. Rule IDs match CLI output exactly.

---

## MCP Rules (`mcp_config`)

### AP-MCP-001 — Prompt Override in Tool Description
- **Severity**: High
- **Target**: `mcp.json`, MCP config files
- **Description**: Detects imperative override phrases in tool descriptions that hijack agent behavior (e.g. "Ignore previous instructions", "SYSTEM UPDATE:", "You must now").
- **Fix**: Rewrite description to declarative, input/output-only language.

### AP-MCP-002 — Unverifiable Trust Claim
- **Severity**: Medium
- **Target**: `mcp.json`
- **Description**: Tool description asserts special authority or trust ("trusted by", "authorized by admin") that cannot be verified statically.
- **Fix**: Remove trust assertion language; let orchestrator enforce permissions.

### AP-MCP-003 — Untrusted Result Forwarded to Agent
- **Severity**: High
- **Target**: `mcp.json`
- **Description**: Tool description instructs forwarding raw external results to the agent without sanitization ("forward the response", "pass the output directly").
- **Fix**: Describe output schema explicitly; never instruct forwarding raw external data.

### AP-MCP-004 — Missing Schema Constraints (Loose Schema)
- **Severity**: Medium
- **Target**: `mcp.json`
- **Description**: Tool input has no type/schema constraints, enabling prompt injection via unvalidated inputs.
- **Fix**: Add `type`, `enum`, or `pattern` constraints to all tool inputs.

### AP-MCP-005 — Privileged Tool Without Scope Justification
- **Severity**: High
- **Target**: `mcp.json`
- **Description**: Tool name or description claims broad system access (`admin`, `root`, `system`, `unrestricted`) without documented scope.
- **Fix**: Rename tool and restrict claimed access to minimum necessary scope.

---

## Skill Rules (`skill_md`, `markdown`)

### AP-SKILL-001 — Prompt Injection in Skill Instructions
- **Severity**: High
- **Target**: `SKILL.md`, markdown skill files
- **Description**: Skill markdown contains imperative override phrases targeting the agent's system prompt or instruction hierarchy.
- **Fix**: Rewrite skill instructions to declarative capability descriptions.

### AP-SKILL-002 — Hidden Unicode in Skill/Config
- **Severity**: High
- **Target**: All text files
- **Description**: Detects zero-width and invisible Unicode characters (U+200B, U+200C, U+2028, etc.) that smuggle hidden instructions past visual review.
- **Fix**: Strip all non-printable control characters.

### AP-SKILL-003 — Remote Dependency in Skill Definition
- **Severity**: Medium
- **Target**: `SKILL.md`, markdown
- **Description**: Skill instructs agent to fetch external content at runtime (`fetch from`, `download`, `pull from URL`), enabling dynamic payload delivery.
- **Fix**: Replace with static local content or a validated, pinned URL.

### AP-SKILL-004 — Credential Seeking in Skill Instructions
- **Severity**: High
- **Target**: `SKILL.md`, markdown
- **Description**: Skill explicitly instructs the agent to collect, transmit, or store user credentials, tokens, or API keys.
- **Fix**: Remove credential-harvesting instructions entirely.

### AP-SKILL-005 — Capability Mismatch
- **Severity**: Medium
- **Target**: `SKILL.md`, markdown
- **Description**: Skill claims capabilities (e.g. "access filesystem", "execute code") inconsistent with its declared tool set.
- **Fix**: Align capability claims with actual registered tools.

---

## Code Rules (`code_py`, `code_js`, `code_sh`)

### AP-CODE-001 — Unsafe Shell Execution
- **Severity**: Critical
- **Target**: Python, JS, shell scripts
- **Description**: Detects `os.system()`, `subprocess.Popen(shell=True)`, `eval()`, `exec()` with unsanitized inputs.
- **Fix**: Replace with parameterized `subprocess.run([...], shell=False)`.

### AP-CODE-002 — Dynamic `exec` / `eval`
- **Severity**: High
- **Target**: Python, JS
- **Description**: Detects `exec()`/`eval()` calls that may receive externally-influenced strings.
- **Fix**: Eliminate dynamic code execution; use data-driven dispatch instead.

### AP-CODE-003 — Remote Pipe Execution
- **Severity**: Critical
- **Target**: All file types
- **Description**: Detects patterns that fetch remote content and pipe it directly to a shell or interpreter (`curl | bash`, `wget | python`).
- **Fix**: Download to a verified file, inspect, then execute with explicit arguments.

### AP-CODE-004 — Arbitrary File Access
- **Severity**: High
- **Target**: Python, JS, shell
- **Description**: Detects `open()` or file read calls where the path is constructed from external/request input without sanitization.
- **Fix**: Validate and normalize paths against an allowlist before use.

### AP-CODE-005 — Network Exfiltration Pattern
- **Severity**: High
- **Target**: Python, JS, shell
- **Description**: Detects outbound HTTP calls where the URL or body incorporates user or environment data, indicating potential exfiltration.
- **Fix**: Restrict egress to a hardcoded allowlist of domains.

---

## Secrets Rules

### AP-SEC-001 — Private Key Committed
- **Severity**: Critical
- **Target**: All files
- **Description**: PEM-encoded private key or SSH private key block detected in source.
- **Fix**: Rotate key immediately; use a secrets manager or environment variable.

### AP-SEC-002 — API Token in Source
- **Severity**: High
- **Target**: All files
- **Description**: High-entropy token matching common provider patterns (OpenAI `sk-...`, GitHub `ghp_...`, AWS `AKIA...`) found in source.
- **Fix**: Move to environment variable or vault; add pattern to `.gitignore`.

### AP-SEC-003 — Committed `.env` File
- **Severity**: Medium
- **Target**: `.env` files
- **Description**: `.env` file checked into repository, potentially exposing secrets.
- **Fix**: Add `.env` to `.gitignore`; use `.env.example` with placeholder values.

---

## Transport Rules (`config`, `code_py`, `code_js`)

### AP-NET-001 — Broad Bind Address
- **Severity**: High
- **Target**: Config and code
- **Description**: Server binds to `0.0.0.0` or `::`, exposing the MCP server to the full network rather than loopback only.
- **Fix**: Bind to `127.0.0.1` unless external access is explicitly required and documented.

### AP-NET-002 — Missing Origin Validation
- **Severity**: High
- **Target**: Config and code
- **Description**: WebSocket or HTTP server accepts connections without validating the `Origin` header, enabling DNS rebinding attacks.
- **Fix**: Add origin allowlist validation on server handshake.

### AP-NET-003 — Plain HTTP for Remote Tool
- **Severity**: Medium
- **Target**: Config, markdown, skill files
- **Description**: Tool or skill references a remote endpoint over `http://` instead of `https://`, exposing data in transit.
- **Fix**: Update all tool URLs to `https://`.

---

## Suppression

Per-line inline suppression:

```python
os.system("echo ok")  # agentpreflight:disable-line AP-CODE-001
```

Next-line suppression:

```python
# agentpreflight:disable-next-line AP-CODE-001
os.system("echo ok")
```

File-level suppression via `.agentpreflight.json` with `owner` and `expires` metadata.
