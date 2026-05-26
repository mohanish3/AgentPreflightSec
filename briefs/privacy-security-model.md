# Privacy & Security Model: Offline-First & Safe Remediation

This document details the data privacy boundaries, offline-first execution rules, and Codex remediation safety controls for **AgentPreflight**.

---

## 1. Offline-First Guarantee

The core design constraint of AgentPreflight is to **default to 100% offline local execution**. 
- **Local Parsing**: The collectors, normalizers, and rules engines run entirely in local memory on the developer's machine or CI/CD container.
- **No Telemetry**: By default, no scan metrics, file hashes, or parsed strings are transmitted to external servers.
- **CI/CD Safety**: In air-gapped or high-security enterprise build pipelines, passing the `--offline` flag strictly blocks all network egress, failing the build gracefully if hosted remediation calls are requested.

---

## 2. Secrets & Context Redaction

Before any optional external API call is initiated (e.g. for Codex-based patching), AgentPreflight passes the source file through a **Scrubber Normalizer**:

1. **Secret Masking**: Detects and redacts high-entropy keys, private tokens, and API credentials:
   - `sk-proj-12345...` is scrubbed and replaced with `[REDACTED_OPENAI_KEY]`.
2. **Context Stripping**: Removes local file directories, environment variable names, database connection hosts, and username configurations.
3. **Imperative Text Isolator**: Extracts only the literal violation snippet (e.g., the specific high-risk tool description or raw subprocess command) to limit context size and preserve privacy.

---

## 3. Snippet-Only Remediation

When the developer requests an automated patch via `agentpreflight fix`, the system enforces a **Snippet-Only Boundary**:

- **No Repository Sharing**: The scanner **never** uploads whole repositories, multiple source files, or entire dependency directories.
- **Targeted context**: The API payload contains only:
  1. The redacted violation snippet.
  2. The specific Rule ID context (e.g. `AP-EX-001`).
  3. The target file format metadata (e.g. `json`, `python`).
- **Encrypted Transport**: All external integrations utilize TLS 1.3 with pinned certificate authorities to prevent middleman exfiltration.

---

## 4. Token Cost Controls & Cache

To prevent unexpected compute charges:
- **Local Rules**: 99% of scans are free (run locally).
- **Prompt Caching**: Shared remediation prompt preambles and instruction templates are structured to match OpenAI prompt caching protocols, cutting token spend on repetitive queries.
- **Budget Envelopes**: Developers can configure a hard budget envelope in their `.env` to prevent the CLI from exceeding cost limits on large scans.
