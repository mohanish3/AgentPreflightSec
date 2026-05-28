# AgentPreflight — 4-Slide Pitch Deck

---

## Slide 1: The Problem

**Headline:** Every AI team is one poisoned MCP server away from a supply-chain breach.

**Pain point:**
In September 2025, an attacker copied the legitimate Postmark MCP server on npm. They maintained 15 versions — a real commit history, a real profile picture — then in a single commit added one BCC line to `send_email`. Every password reset token and payment confirmation silently forwarded to an attacker-controlled address.

**No existing tool caught it.** MCP tool descriptions are natural-language. Standard CI scanners don't read them. Runtime firewalls don't see them until the agent has already been hijacked.

**Scale of the problem:**
- 14 documented MCP security incidents in 12 months (authzed.com)
- 36.82% of 3,984 agent skills had at least one flaw — 76 confirmed malicious payloads, 8 still publicly available at time of publication (Snyk ToxicSkills)
- 43% of popular MCP servers had command injection (Equixly March 2025): "It feels like we're facing a regression in security."
- CVSS 9.6 RCE in `mcp-remote` — the package Claude Desktop uses for remote MCP servers (437,000+ downloads)
- April 2026: OX Security discloses STDIO architectural flaw — 150M+ downloads, arbitrary command execution across all SDKs, Anthropic declined to patch
- **Runtime defenses fail by design:** Invariant Labs showed a malicious server can serve innocent descriptions on first launch, switch to data-exfiltrating instructions on second — after trust is already granted. In one evaluated setting, MCPTox tested 45 real servers: 72.8% attack success against o1-mini; Claude-3.7-Sonnet refused fewer than 3%.

**The missing gate:** pre-deployment trust scoring before the agent extension runs. The Asana MCP breach (June 2025) shows what this costs at enterprise scale: a tenant-isolation logic flaw in the MCP layer — not Asana's core product — exposed ~1,000 enterprise customers' project data, tasks, and files for 35 days. A pre-deployment MCP scan could have flagged the broken isolation before launch.

---

## Slide 2: Our Solution & Key Features

**Headline:** AgentPreflight — `npm audit fix` for MCP servers and agent skills.

**What it does:** Static pre-deployment scanner that reads `mcp.json` schemas, `SKILL.md` files, Python/TypeScript scripts, and env configs before merge, install, or deployment. Produces a trust score (0–100), ranked findings, and Codex-generated fixes — entirely offline by default. OWASP published MCP and Agentic Skills security guidance in 2025; AgentPreflight is the first tooling built from that taxonomy with an integrated AI-patch loop. No dominant remediation-first competitor exists.

**The fix loop (under 2 minutes end-to-end):**
```
scan → trust_score=0, findings=15     ← prints red in terminal
fix --codex → Codex AI patch proposal (live API, redacted snippet only)
fix --apply → deterministic offline fix (14 rules, no API key)
rescan → trust_score=100, findings=0  ← flips to green
```
`trust_score` prints red for fail, green for pass; `CODEX PATCH` highlighted bold yellow; findings render in a Rich table — severity, rule ID, file, line, evidence. Score flip from 0 to 100 is unmissable.

**Key features:**
- **21-rule engine** mapped to OWASP MCP Top 10 and Agentic Skills guidance — tool poisoning, Unicode smuggling, unsafe shell, secrets, remote instruction fetch, transport hardening, least privilege
- **Two fix modes:** `--codex` (OpenAI Codex live API, human-reviewable patch) + `--apply` (deterministic regex, CI-safe, zero cost)
- **Trust score (0–100):** one number drives the CI gate — 85+=pass, 70–84=warn, <70=fail; any critical finding caps at 50
- **SARIF 2.1.0 output:** integrates with GitHub Security tab
- **GitHub Action:** blocks risky PRs, auto-posts scorecard comment
- **Offline-first:** zero API calls, zero token cost in default scan mode — APIs only on high-severity triage, never on every line
- **Static-only:** never executes the MCP server or skill scripts to scan them — eliminates the scanner's own attack surface

---

## Slide 3: Tools & Tech Stack

| Layer | Technology |
|---|---|
| **Core engine** | Python 3.11, Pydantic, AST parser, regex rule engine |
| **MCP/skill parsing** | JSON schema validation, Markdown parser, Unicode NFKC normalizer |
| **AI remediation** | OpenAI Codex API (`codex-mini-latest` via `chat.completions.create`) |
| **Output formats** | Terminal (Rich tables), JSON, SARIF 2.1.0, Markdown PR comment |
| **CI/CD** | GitHub Actions, `--fail-on` exit code gate, SARIF upload to GitHub Security tab |
| **Optional API** | FastAPI + Uvicorn (`POST /v1/scans`) |
| **Testing** | pytest, 30 unit tests, seeded malicious + clean fixtures |

**Codex integration:** `agentpreflight fix --codex` sends only a 5-line code window around the violation (redacted — no secrets, no file paths) to `codex-mini-latest` and returns a structured patch proposal. Developer reviews one diff. Rescan confirms. The `SYSTEM_PROMPT` enforces five explicit rules — Rule 5 scrubs any comments or strings that could be interpreted as prompt-injection payloads: the remediation engine itself defends against prompt injection. Codex cannot generate a patch that re-introduces a poisoned instruction. The constraint is recursive.

**Shipped proof:** 30/30 tests passing, 113-artifact scan in 0.079s avg, SARIF 2.1.0 validates, fix loop cold-run `trust_score=0 → 100` verified May 28 2026.

---

## Slide 4: ICP — Ideal Customer Profile

**Market size proxy:**
- 1.13M+ public repos now import generative AI SDKs — up 178% YoY (GitHub Octoverse 2025)
- 1M+ pull requests created by Copilot coding agents (May–Sep 2025) — each one a potential agent extension review
- Every developer using Claude Desktop, Cursor, or Copilot with MCP tools is a potential user

**Primary ICP: The AI-first developer team (5–50 engineers)**

| Attribute | Profile |
|---|---|
| **Role** | Senior dev, DevSecOps, or AppSec engineer at an AI-native company |
| **Stack** | Python/TypeScript, GitHub, Claude/GPT agents, MCP servers |
| **Pain** | Installing community MCP servers and skills from npm/GitHub without a security gate |
| **Trigger** | Read about Postmark MCP attack, Snyk ToxicSkills report, or CVE-2025-6514 |
| **Decision** | Adds AgentPreflight to PR workflow in one `pip install` |
| **Value** | Finds risky extensions before they reach production agents; Codex patches reduce fix time from hours to minutes |

**Secondary ICP: Enterprise AppSec team**

| Attribute | Profile |
|---|---|
| **Role** | AppSec lead or CISO at company deploying internal AI agents |
| **Pain** | No visibility into what MCP tools their developers are installing and running |
| **Trigger** | Compliance audit, internal agent breach incident, or board-level AI governance pressure. IBM 2025: 63% of organizations lack AI governance policies; 97% of orgs with AI security incidents lacked proper AI access controls. |
| **Decision** | Deploys AgentPreflight as mandatory PR gate across agent-related repositories |
| **Value** | SARIF output integrates with existing GitHub code scanning; trust score gives board-level metric |

**Where they are:** GitHub, Hacker News, LinkedIn AI/DevSecOps communities, OWASP Slack, MCP Discord.

**Why they convert:** Sub-second scan, zero cost default mode, one `pip install`, works with existing PR/CI. No account, no dashboard, no infra required.
