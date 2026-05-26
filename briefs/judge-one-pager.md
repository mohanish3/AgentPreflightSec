# Investor One-Pager: AgentPreflight

This one-pager presents market pain, product wedge, business model, and near-term milestones for **AgentPreflight**.

---

## 1. Problem and market timing

AI software is shifting from chat interfaces to autonomous, action-taking agents. These agents rely on **Model Context Protocol (MCP)** servers and **agent skills** to read databases, write files, and call external APIs.

This introduces a new vulnerability layer: **the agent supply chain**. A compromised MCP extension or skill directory can hijack behavior before traditional AppSec scanners or runtime guardrails react.

**AgentPreflight** inserts a pre-deployment trust gate for MCP servers and skills, with deterministic findings and remediation-first workflows.

---

## 2. Competitive wedge (10x advantage)

| Security Aspect | Runtime Firewalls | Red-Team Tooling | AgentPreflight |
|---|---|---|---|
| **Pipeline Stage** | Runtime (Conversational path) | Testing Phase (Heavy dynamic evals) | **Pre-Deployment / Git Gate** |
| **Analysis Speed** | Adds latency on live traffic | Slow dynamic evaluation | **Sub-second local static checks** |
| **Data Privacy** | Requires request inspection | Often API-heavy | **Offline-first by default** |
| **Remediation** | Blocking only | Findings only | **Codex-assisted constrained patching** |

---

## 3. Product and monetization

### Core product
- CLI-first scanner for local development and CI.
- JSON + SARIF outputs for merge gating and security tooling.
- Constrained `fix` flow for safe, auditable remediation suggestions.

### Monetization path
- **Open-source adoption layer**: Free local scanner to maximize distribution.
- **Team plan**: Managed policies, centralized suppressions, trend dashboards.
- **Enterprise plan**: Private rule feeds, SSO/RBAC, audit and compliance exports.

## 4. Why Codex is a force multiplier

AgentPreflight demonstrates the ultimate partnership between a developer and OpenAI Codex:
- **Detection**: Deterministic local rules flag security risks (such as command injection in scripts or prompt injections in metadata).
- **Remediation**: Codex acts as our **automated repair engine**. It reads the isolated, scrubbed violation snippet, generates a clean drop-in patch, and refactors the code securely without breaking adjacent logic.
- **Verification**: A fast, local rescan instantly verifies the repair and updates the Trust Score to **100**.

## 5. Next 90 days

1. Ship OSS v1 scanner + GitHub Action onboarding.
2. Sign 3-5 design partners using MCP/Codex stacks.
3. Validate severity thresholds and suppression governance.
4. Launch paid private beta for team policy controls.
