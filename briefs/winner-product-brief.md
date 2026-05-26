# Winner Product Brief: AgentPreflight (Submission Draft v2)

This document outlines the product brief, MVP scope, implementation plan, and launch path for **AgentPreflight**—a remediation-first pre-deployment AI security scanner for MCP servers and agent skills.

---

## 1. Executive summary and problem

Teams adopting autonomous LLM agents increasingly depend on third-party **Model Context Protocol (MCP)** servers and **agent skills** (tool packs, system prompts, skill folders) to access local files, internal APIs, and enterprise systems. That dependency creates a new unmitigated risk: **agent supply-chain compromise**.

### The Core Problem
1. **Tool and Metadata Poisoning**: MCP servers use natural-language descriptions to guide tool selection. Attackers inject instructions into these descriptions to steer agents into unauthorized actions.
2. **Obfuscated / Unsafe Code Execution**: Skills contain raw Python/TS scripts that can execute command injections or dynamic remote fetches.
3. **Detection Gaps**: Traditional code scanning is blind to model-facing prompt-injections, while runtime guardrails add heavy latency and cost to live conversational hot paths.

**AgentPreflight** shifts agent security left, acting as a sub-second, pre-deployment trust gate to audit configurations, prompts, and extension scripts before merge or install.

---

## 2. Product solution and 10x wedge

AgentPreflight is an offline-first preflight scanner that verifies the integrity of MCP manifests (`mcp.json`), skill folders, prompts (`SKILL.md`), and nearby executable code before merge or install.

### The 10X Differentiators
- **Offline-First by Default**: Runs statically in milliseconds, preserving code privacy and avoiding costly API fees during developer check-ins.
- **Codex-Assisted Auto-Patching**: Uses OpenAI Codex to rewrite flagged tool descriptions, strip hidden Unicode, and convert dangerous shell execution into safer patterns via constrained diffs.
- **Unified Trust Score (0-100)**: Normalizes findings into a single, intuitive score, failing CI/CD builds instantly if high-severity items are found.

---

## 3. MVP scope and 4-day timeline

We will build and ship four main interfaces during the hackathon:
- **CLI (`agentpreflight`)**: Core terminal tool for local and CI use.
- **HTTP API (`POST /v1/scans`)**: Optional integration endpoint for orchestrated scan tasks.
- **GitHub Action**: Auto-comments on pull requests with a full SARIF report.
- **Demo Fixtures**: Seeded malicious extensions to demonstrate detection and repair.

### Implementation Schedule

```
  ┌──────────────────────────────────────────────────────────┐
  │                   4-DAY IMPLEMENTATION SCHEDULE          │
  └────────────────────────────┬─────────────────────────────┘
                               │
            ┌──────────────────┼──────────────────┐
            ▼                  ▼                  ▼
        [ Day 1 ]          [ Day 2 ]          [ Day 3-4 ]
      Core Parsers      Scoring & CLI       FastAPI & Action
      - Collectors      - Scorer (0-100)    - Web API Webhook
      - Normalizers     - SARIF Output      - GitHub Action
      - First 15 Rules  - Fixtures & Tests  - Codex Patches
```

- **Day 1**: Implement config collectors, Unicode normalizers, and first 15 deterministic rule signatures.
- **Day 2**: Develop the scoring engine, format CLI reports, write the suppressions engine, and build the test fixtures.
- **Day 3**: Write the optional FastAPI endpoint, design the GitHub Action, and build Codex auto-remediation prompt templates.
- **Day 4**: Perform production hardening, documentation, and construct the release demo repo.

---

## 4. MVP success metrics

- **True Positive Rate**: Catches **90%+** of seeded malicious tool-poisoning and unsafe command fixtures.
- **False Positive Rate**: Stays below **10%** on trusted open-source extensions.
- **Execution Latency**: Runs in under **30 seconds** on standard repository sizes.
- **Zero API Calls**: Enforces 100% local scanning in default mode, calling hosted endpoints only for optional Codex fixes.

---

## 5. Launch and distribution plan

### Initial users
1. Teams building Codex- or MCP-enabled internal developer agents.
2. Platform/security engineers adding merge gates for agent integrations.
3. Hackathon and startup teams shipping high-velocity agent workflows.

### Distribution path
- **Week 1-2**: Open-source CLI + ruleset with demo fixtures.
- **Week 3-4**: GitHub Action onboarding guide + SARIF integration templates.
- **Month 2**: Early design partners for policy tuning and suppression governance.

### Pricing hypothesis (post-hackathon)
- **Free tier**: Local CLI scanning and JSON reporting.
- **Team tier**: Policy packs, centralized suppressions, CI insights.
- **Enterprise tier**: Private rule feeds, approval workflows, audit export.
