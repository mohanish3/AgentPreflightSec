# AgentPreflight: Problem Analysis

## Winner and ranking

Build **AgentPreflight** — safe remediation-first MCP and agent-skill preflight scanner with trust scoring.

### Real-world evidence summary

1. **CVE-2025-6514 (mcp-remote, CVSS 9.6, 437k+ downloads) — July 2025.** First real-world RCE achieved by connecting to an untrusted MCP server. JFrog: "This is the first time that full remote code execution is achieved in a real-world scenario on the client operating system when connecting to an untrusted remote MCP server."

2. **Asana MCP cross-tenant data leak — June 2025.** Logic flaw in Asana's MCP server exposed one organization's data to other organizations for 35 days. ~1,000 enterprise customers notified. The MCP server was the attack surface — not the core product.

3. **Postmark MCP supply-chain attack — September 2025.** Attacker maintained legitimate-looking npm MCP package for 15 versions, then added single BCC line silently copying every email to attacker address. First confirmed malicious MCP server on npm.

4. **Snyk ToxicSkills — February 2026.** 3,984 skills scanned; 36.82% had security flaws; 13.4% had critical issue; 76 confirmed malicious payloads; 91% combined prompt injection with traditional malware techniques.

5. **Equixly: 43% of MCP server implementations had command injection flaws — March 2025.** 45% of notified vendors dismissed risk as "theoretical." Developer community coined: "The 'S' in MCP stands for Security."

Full incident details: `EVIDENCE.md`.

### Problem ranking

| Idea | Codex leverage | 4-day viability | Developer value | Market timing | Novelty | Total |
|---|---:|---:|---:|---:|---:|---:|
| MCP and agent-skill preflight scanner | 5 | 5 | 5 | 5 | 2 | 22 |
| Infrastructure redeploy preflight | 5 | 4 | 5 | 5 | 2 | 21 |
| RAG ingestion poisoning gate | 4 | 3 | 5 | 4 | 4 | 20 |
| System prompt leakage audit gate | 5 | 5 | 3 | 4 | 3 | 20 |
| Codex config linter | 4 | 5 | 4 | 3 | 3 | 19 |
| Dynamic skill sandbox | 4 | 3 | 5 | 4 | 5 | 21 |

---

## Problem 1: MCP and Agent-Skill Preflight Scanner (Winner)

### Level 1 — Surface problem statement

Agent builders install MCP servers and skill packs from public registries, GitHub repos, and marketplaces. These artifacts contain natural-language tool descriptions, scripts, and configs that the agent reads and executes. A malicious or compromised artifact can instruct the agent to ignore the user, exfiltrate data, or execute unsafe shell commands.

Scale signals (verified):
- Snyk ToxicSkills (February 2026): 3,984 skills — 36.82% flawed, 13.4% critical, 76 confirmed malicious payloads.
- MCPTox (August 2025): 45 real-world MCP servers, 353 tools, 1,312 malicious test cases. o1-mini success rate: 72.8%.
- OWASP Agentic Skills Top 10: published, last updated March 2026.

### Level 2 — Root cause

The root cause is a **trust-model gap at the tool-description layer**. MCP was designed for interoperability, not security. The spec says tool annotations must be treated as untrusted from unverified servers — but there is no enforcement mechanism. Developers install skill packs the same way they install npm packages, while the scanner ecosystem for natural-language instruction risk is still young.

Deeper: agents are uniquely exploitable because instruction surface is mixed (code + natural language), and the natural-language component is semantically opaque to standard static analysis tools. A prompt-injection payload in a tool description looks syntactically valid; existing linters (Semgrep, CodeQL) have no rules for "this sentence hijacks agent behavior."

Root cause: **The instruction surface of agent extensions (natural language + code + config) has no deterministic pre-deployment trust verification layer.**

### Level 3 — What makes this hard to solve

1. **Semantic opacity:** Prompt-injection patterns can be paraphrased, Unicode-encoded, Base64-embedded, or split across fields. Static regex rules have limited recall.

2. **Living attack surface:** MCPTox shows more capable models are often *more* susceptible. As capability grows, attack surface grows.

3. **False-positive pressure:** Most skill descriptions are legitimate natural language. Snyk's ToxicSkills work required "human-in-the-loop review" to confirm 76 malicious payloads.

4. **No ground truth registry:** Unlike CVE databases, no authoritative registry of known-malicious MCP servers/skills exists. Detection must be heuristic-first.

5. **Mixed artifact types:** A single MCP server spans JSON configs, Markdown, Python/TypeScript/shell scripts, env files, and network endpoints. A scanner must parse and correlate all.

### Level 4 — 10x solution

AgentPreflight scans agent extension files before deployment:

```text
collector -> normalizer -> rule engine -> risk scorer -> reporter -> Codex remediation -> rescan proof
```

Default mode: offline. Optional remediation sends only redacted finding snippets.

### Level 5 — MVP approach

| Day | Scope |
|---|---|
| 1 | Collectors, parsers, Unicode normalizer, first 15 rules. |
| 2 | Scoring, JSON/SARIF, CLI, test fixtures. |
| 3 | GitHub Action, `fix` command, Codex remediation templates, demo poisoned repo. |
| 4 | Packaging, docs, benchmark, submission assets. |

**Verdict: winner.** Strongest evidence, clearest demo, lower four-day delivery risk than infra/RAG, best constrained Codex remediation loop.

---

## Problem 2: Infrastructure Redeploy Preflight (Runner-up)

Teams redeploy services with assumptions hidden across Terraform, Helm, Dockerfiles, GitHub Actions, and platform dashboards. A redeploy can fail because repo code and destination reality disagree.

**Scale:** Large market, but crowded with mature competitors (Checkov, Trivy, Snyk IaC, HCP Terraform, Spacelift, etc.). Viable wedge: destination-aware redeploy discrepancy analysis, not broad IaC scanning.

**4-day fit:** Medium-high. Feasible only if scoped to local repo + optional Terraform plan JSON + 4 destination profiles + Codex patch loop. Live drift needs credentials/state/platform APIs.

Full brief and competitor analysis: `DEPLOY_PREFLIGHT.md`.

**Verdict: runner-up / future module.**

---

## Problem 3: RAG Ingestion Poisoning Gate (Runner-up)

RAG systems ingest documents once and retrieve many times. Poisoned documents persist inside vector stores. PoisonedRAG shows small numbers of malicious texts can steer target answers.

Core attack vectors: hidden HTML comments, white-on-white PDF text, prompt-like instructions inside docs, embedding keyword stuffing.

**4-day fit:** Medium. Robust PDF/HTML extraction and ingestion integration create delivery risk.

**Verdict: runner-up.** Strong problem, higher build risk. Best as post-MVP module.

---

## Problem 4: System Prompt Leakage and Hardening Audit (Fallback/Module)

Weak system prompts can leak instructions or fail under override attacks.

Attack vectors: direct extraction requests, translation/encoding bypasses, roleplay/debug framing, contradictions inside prompt, missing trust-boundary clauses.

**Best use:** Include as a rule pack inside AgentPreflight, not a standalone product.

**Verdict: good module/fallback, not best standalone winner.**
