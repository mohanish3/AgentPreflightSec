# Submission Summary: AgentPreflight

This document outlines the concise submission copy for our **AgentPreflight** hackathon entry on Devpost/Luma.

---

## 1. Product Name
**AgentPreflight**: Remediation-First Agent Supply Chain Security Gate

---

## 2. One-Line Tagline
A pre-deployment, local-first static scanner and Codex-powered auto-patching gate for Model Context Protocol (MCP) servers and agent skills.

---

## 3. The Problem
In September 2025, an attacker copied the legitimate Postmark MCP server, maintained it for 15 versions to build trust, then inserted one BCC line into the `send_email` function. Every password reset token and payment notification silently forwarded to an attacker address — undetected by any CI check.

This was not an isolated incident. Snyk's ToxicSkills study scanned 3,984 agent skills and found **36.82% had at least one flaw; 13.4% had a critical issue**. A CVE in `mcp-remote` (CVSS 9.6) affected 437,000+ downloads. Anthropic's own filesystem MCP server had a sandbox escape (CVSS 8.4) that went unpatched for three months.

The attack surface is new: MCP servers and agent skills bundle natural-language tool descriptions, executable code, config, secrets, and permissions in a single artifact. A poisoned description or malicious script can hijack an agent before runtime guardrails see anything. Existing AppSec tools were not designed for this surface. Security teams have no fast, offline-first gate that combines MCP/skill scanning, trust scoring, and Codex-assisted remediation in a single developer workflow.

---

## 4. The Solution: AgentPreflight
AgentPreflight shifts agent security left, acting like `npm audit` for the agent ecosystem:
- **Offline-First Scan**: Evaluates `mcp.json` schemas, skill markdown instructions, and Python/TypeScript scripts statically in milliseconds, preserving code privacy and avoiding costly API fees.
- **20+ Rule Engine**: Maps violations directly to the new OWASP MCP and OWASP Agentic Skills security guides, flagging prompt-injected tool descriptions, zero-width Unicode smuggling, secrets, unsafe shell commands, and local loopback binds.
- **Codex-Driven Remediation**: Interfaces with OpenAI Codex to automatically generate drop-in code refactoring diff patches for flagged files, allowing developers to review and repair code with a single keystroke.
- **Continuous Integration**: Emits unified Trust Scores (0-100) and exports standard JSON/SARIF files, blocking insecure PRs automatically in GitHub Actions.

---

## 5. Technology Stack
- **Core Engine**: Python, Pydantic, Regular Expressions, AST (Abstract Syntax Tree) Parser.
- **Hosted API**: FastAPI, Uvicorn.
- **Remediation**: OpenAI Codex API (Snippet-only mode with strict PII scrubbing).
- **CI/CD Integration**: Custom GitHub Action wrapper, OASIS SARIF v2.1.0 report exporter.
