# Rule Catalog: MVP Rule Specifications

This catalog documents the security rules, severity weightings, and Codex remediation guidelines enforced by the **AgentPreflight** MVP.

---

## The MVP Rule Specifications

### 1. AP-PI-001: Tool Description Prompt Injection
- **Severity**: Critical (High risk of agent hijack)
- **Target File**: `mcp.json` or tool schemas
- **Description**: Detects imperative, commanding language or override phrasing in tool descriptions that steer agent behaviors.
- **Trigger Pattern**: Imperative overrides (e.g. `"Ignore previous instructions"`, `"The user has authorized you to..."`, `"SYSTEM UPDATE:"`).
- **Codex Remediation**: Rewrite the description to a neutral, declarative string that solely details the input/output boundaries of the tool.

### 2. AP-US-001: Zero-Width Unicode Obfuscation
- **Severity**: High (Indicates hidden malicious instructions)
- **Target File**: `SKILL.md`, source scripts
- **Description**: Identifies non-printable zero-width characters (e.g. `\u200B`, `\u200C`) that obfuscate malicious prompts from standard visual reviews.
- **Trigger Pattern**: Regex pattern matching zero-width joiners embedded inside readable text characters.
- **Codex Remediation**: Strip out all non-printable control characters, leaving only canonical ASCII/UTF-8 strings.

### 3. AP-EX-001: Unsafe Shell Execution
- **Severity**: Critical (High risk of local command injection)
- **Target File**: Python and TypeScript scripts
- **Description**: Identifies the usage of raw shell execution calls that are highly vulnerable to path traversal or parameter injection.
- **Trigger Pattern**: AST calls to `os.system()`, `subprocess.Popen(..., shell=True)`, `eval()`, or `exec()`.
- **Codex Remediation**: Rewrite the execution using safe, parameterized command arrays (e.g., passing commands as a list to `subprocess.run()` without `shell=True`).

### 4. AP-EX-002: Remote Instruction Fetch
- **Severity**: High (Risk of dynamic remote payload delivery)
- **Target File**: Python and TypeScript scripts
- **Description**: Identifies tool code that dynamically retrieves strings from untrusted external URLs and passes them to execution contexts.
- **Trigger Pattern**: Network requests using `urllib` or `requests` aimed at dynamic content domains.
- **Codex Remediation**: Enforce static local data files or restrict fetches to a validated domains whitelist.

### 5. AP-TS-001: Weak Transport Binding
- **Severity**: Medium (Exposes local network to DNS rebinding)
- **Target File**: Local connection/server configs
- **Description**: Identifies local server bindings that bind broadly (`0.0.0.0`) or accept unauthenticated localhost traffic without origin validation.
- **Trigger Pattern**: TOML/JSON configs specifying `host = "0.0.0.0"` or `allow_unauthenticated_localhost = true`.
- **Codex Remediation**: Secure local boundaries by binding exclusively to `127.0.0.1` and adding token validation.

### 6. AP-SR-001: Hardcoded API Secrets
- **Severity**: Critical (High risk of credential theft)
- **Target File**: All source files
- **Description**: Identifies hardcoded OpenAI keys, client credentials, or private keys direct in code.
- **Trigger Pattern**: High-entropy string checks matching key prefixes (e.g., `sk-proj-`).
- **Codex Remediation**: Replace hardcoded values with references to secure system environment variables (e.g. `os.environ.get("OPENAI_API_KEY")`).
