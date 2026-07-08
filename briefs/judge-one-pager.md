# Judge One-Pager: Securing the Agent Supply Chain

This one-pager presents the high-level product narrative, competitive edge, and hackathon win viability for **AgentPreflight**.

---

## 1. The Narrative: Securing the Next Frontier

The AI industry is transitioning from passive chatbots to autonomous, action-oriented agents. These agents rely on the **Model Context Protocol (MCP)** and **agent skills** to read databases, write local files, and invoke external APIs. 

However, this transition introduces a critical, unaddressed vulnerability: **The Agent Supply Chain**. If a developer pulls a compromised MCP extension or skill directory, the agent can be hijacked before traditional AppSec scanners or runtime guardrails can intervene.

**AgentPreflight** is the first pre-deployment security gate built specifically to trust-score and secure MCP servers and agent skills before they are ever installed or deployed.

---

## 2. Our Competitive Edge (The 10X Wedge)

| Security Aspect | Runtime Firewalls (e.g. Llama Guard) | Red-Team Tooling (e.g. Garak) | AgentPreflight (Our 10X Edge) |
|---|---|---|---|
| **Pipeline Stage** | Runtime (Conversational path) | Testing Phase (Heavy dynamic evals) | **Pre-Deployment / Git Gate** |
| **Analysis Speed** | High latency (adds 2-5s per request) | Slow (takes 10-30 mins per run) | **Sub-second (Local static check)** |
| **Data Privacy** | High token cost (reads every user input) | High cost (runs thousands of API calls) | **100% Offline-First by Default** |
| **Remediation** | None (Blocks conversational paths) | None (Identifies vulnerabilities only) | **Codex-Assisted Auto-Patching** |

---

## 3. The OpenAI Codex Synergy

AgentPreflight demonstrates the ultimate partnership between a developer and OpenAI Codex:
- **Detection**: Deterministic local rules flag security risks (such as command injection in scripts or prompt injections in metadata).
- **Remediation**: Codex acts as our **automated repair engine**. It reads the isolated, scrubbed violation snippet, generates a clean drop-in patch, and refactors the code securely without breaking adjacent logic.
- **Verification**: A fast, local rescan instantly verifies the repair and updates the Trust Score to **100**.

This loop represents the core theme of the hackathon: **using OpenAI Codex to build real, secure, and production-ready AI systems faster.**
