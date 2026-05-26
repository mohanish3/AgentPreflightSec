# Competitor Landscape: 10 Core Competitors

We evaluate **exactly 10 major competitors** in the LLM and AI agent security spaces, mapping their features and showing how **AgentPreflight** establishes its 10X edge.

---

## Competitor Matrix (Capped at Max 10)

| Competitor | Core Domain / Focus | Unique Capabilities & Features | Our 10X Gaps & Differentiators |
|---|---|---|---|
| **1. Snyk Agent Scan** | Skill Supply Chain | Free OSS CLI scanning tool for agent extensions and skills. | Blind to interactive remediation; AgentPreflight uses Codex to automatically generate patches and repair code. |
| **2. Promptfoo** | LLM/RAG Evaluation | CI-friendly runtime evaluation and adversarial prompt injection testing. | Non-deterministic, slow (dynamic endpoints), and does not parse local MCP/skill source files statically. |
| **3. Garak** | LLM Vulnerability Scanner | Extensive jailbreak, prompt exfiltration, and override probe database. | Heavy endpoint prober (takes 10-30 mins per run), high token cost, unsuitable for developer PR blocking. |
| **4. PyRIT (Microsoft)** | Red Teaming Orchestrator | Heavy multi-turn adversarial testing harness for security labs. | Complex setup for research experts; lacks lightweight developer-focused pre-commit checks. |
| **5. Llama Guard (Meta)** | Runtime Safety Model | Prompt and response text classification model. | Adds critical runtime latency (hot path), high token cost, and cannot inspect local environment configs. |
| **6. Lakera Guard** | API-based LLM Safety | SaaS-based prompt injection and PII leak detection API. | Requires sending source code to hosted servers (privacy risk) and adds network latency. |
| **7. NeMo Guardrails** | Conversational Rails | Rules engine middleware to guide live conversational dialogs. | Heavy integration complexity, high overhead, and blind to static file configurations. |
| **8. Semgrep** | AppSec Static Analysis | Powerful AST-based source code linter for general patterns. | Completely blind to agent semantics, prompt-injection patterns, and tool metadata strings. |
| **9. Presidio (Microsoft)** | PII Sanitization | Open-source pattern-matching engine for PII anonymization. | Restricted to sensitive data; blind to agent system execution or tool-poisoning risks. |
| **10. Inspect AI** | Safety Evaluation | Government-backed safety benchmarks and model auditing. | Designed for capability research labs, not as a fast developer PR gate. |

---

## Our 10x Edge: AgentPreflight

Unlike competitors that require running model servers or manual reviews, AgentPreflight acts like **`npm audit` for agents**:
1. **Offline-First**: Scan runs locally in milliseconds, preserving source code privacy.
2. **Interactive Codex Repair**: When a vulnerability is flagged, AgentPreflight interfaces with Codex to generate a reviewable code patch instantly.
3. **Transparent Scoring**: Normalizes findings into a clear, unified **Trust Score (0-100)** to fail or pass CI/CD builds instantly.
