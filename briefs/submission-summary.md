# Submission Summary: AgentPreflight

This document outlines the concise submission copy for our **AgentPreflight** hackathon entry on Devpost/Luma.

---

## 1. Product Name
**AgentPreflight**: Remediation-First Agent Supply Chain Security Gate

---

## 2. One-Line Tagline
Security scanner that finds and patches dangerous AI agent extensions before they ship — offline static analysis, Codex-generated fixes, rescan proof.

---

## 3. The Problem
In September 2025, an attacker copied the legitimate Postmark MCP server, maintained it for 15 versions to build trust, then inserted one BCC line into the `send_email` function. Every password reset token and payment notification silently forwarded to an attacker address — undetected by any CI check.

This was not an isolated incident. Snyk's ToxicSkills study scanned 3,984 agent skills and found **36.82% had at least one flaw; 13.4% had a critical issue**. A CVE in `mcp-remote` (CVSS 9.6) affected 437,000+ downloads. Anthropic's own filesystem MCP server had a sandbox escape (CVSS 8.4) that went unpatched for three months. Equixly's March 2025 audit of popular MCP server implementations found **43% had command injection, 30% had SSRF, 22% had path traversal**. The official Anthropic-maintained Puppeteer MCP server — 91,000 monthly downloads — had SSRF, prompt injection, and sandbox bypass simultaneously. It was archived rather than patched.

The attack surface is new: MCP servers and agent skills bundle natural-language tool descriptions, executable code, config, secrets, and permissions in a single artifact. A poisoned description or malicious script can hijack an agent before runtime guardrails see anything. Existing AppSec tools were not designed for this surface. Security teams have no fast, offline-first gate that combines MCP/skill scanning, trust scoring, and Codex-assisted remediation in a single developer workflow.

---

## 4. The Solution: AgentPreflight
AgentPreflight shifts agent security left, acting like `npm audit` for the agent ecosystem:
- **Offline-First Scan**: Evaluates `mcp.json` schemas, skill markdown instructions, and Python/TypeScript scripts statically in milliseconds, preserving code privacy and avoiding costly API fees.
- **20+ Rule Engine**: Maps violations directly to the new OWASP MCP and OWASP Agentic Skills security guides, flagging prompt-injected tool descriptions, zero-width Unicode smuggling, secrets, unsafe shell commands, and local loopback binds.
- **Codex-Driven Remediation**: Two integrated fix modes — `--codex` sends redacted finding snippets (no secrets, no full file paths) to OpenAI Codex via chat completions API (`codex-mini-latest`) and returns AI-generated patch proposals; `--apply` runs a deterministic offline rewrite engine covering 14 rules across four categories. Both modes produce findings a developer can review, approve, and rescan in under two minutes.
- **Continuous Integration**: Emits unified Trust Scores (0-100) and exports standard JSON/SARIF files, blocking insecure PRs automatically in GitHub Actions.

---

## 5. Technology Stack
- **Core Engine**: Python, Pydantic, Regular Expressions, AST (Abstract Syntax Tree) Parser.
- **Hosted API**: FastAPI, Uvicorn.
- **Remediation**: OpenAI Codex API (`codex-mini-latest`, snippet-only mode with strict PII scrubbing).
- **CI/CD Integration**: Custom GitHub Action wrapper, OASIS SARIF v2.1.0 report exporter.

---

## 6. How We Built It

The scanner was designed Codex-first: we wrote the rule catalog and prompt templates before writing the detection engine, so every rule produces a Codex-ready remediation context from day one.

The detection pipeline is entirely static — AST parsing for Python, JSON schema validation for MCP configs, regex-based Unicode normalization for skill Markdown. No model calls, no sandboxing, no network. This keeps the scan path offline and sub-second.

Codex integration has two layers:
1. **`agentpreflight prompts`** — generates a structured prompt pack (system prompt + per-finding context) that can be fed to any Codex session.
2. **`agentpreflight fix --codex`** — makes a live `chat.completions.create` call to `codex-mini-latest` with a redacted snippet and structured instruction. Returns a patch proposal the developer reviews before applying.

The deterministic `--apply` mode was built as a CI-safe fallback: it applies the same fixes offline, using the rule logic we trust without Codex API dependency. The combination means the demo works with or without an API key.

---

## 7. What We Learned

The hardest part was not the detection logic — it was prompt engineering for constrained remediation. Codex is extremely capable at rewriting code, but without tight structuring it produces explanatory prose instead of a drop-in replacement. The `SYSTEM_PROMPT` in `prompt_builder.py` went through a dozen iterations before it reliably returned a patch instead of a paragraph.

The second insight: the trust score matters more than the finding list. Judges, developers, and CI gates all want a single number. A 0–100 score that moves from `fail` to `pass` is more compelling than a long finding list even if the long list contains more information.

---

## 8. What's Next

- **Suppression expiry enforcement**: surfacing when suppressed findings have exceeded their stated expiry date.
- **VS Code problem matcher**: inline findings in the editor as you write MCP tools.
- **Dynamic skill sandbox**: lightweight container that instruments a skill script at runtime and flags behavior the static scan missed.
- **Codex-powered rule generation**: feed a new MCP CVE to Codex and generate the detection rule + fixture automatically.
- **Registry scanner**: automated scan of new MCP packages on npm/PyPI as they publish.
