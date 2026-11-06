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
Autonomous LLM agents are only as secure as the extensions (MCP servers and skill directories) they rely on to execute actions. These components combine natural language tool descriptions, configuration, permissions, and executable code in a single bundle. If a tool description is prompt-injected or a skill script contains unsafe commands, the agent can be hijacked before runtime guardrails can intercept. Security teams lack fast, pre-deployment tools to audit and secure this emerging agentic supply chain.

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
