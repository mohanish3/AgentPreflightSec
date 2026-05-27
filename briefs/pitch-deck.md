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

**The missing gate:** pre-deployment trust scoring before the agent extension runs.

---

## Slide 2: Our Solution & Key Features

**Headline:** AgentPreflight — `npm audit fix` for MCP servers and agent skills.

**What it does:** Static pre-deployment scanner that reads `mcp.json` schemas, `SKILL.md` files, Python/TypeScript scripts, and env configs before merge, install, or deployment. Produces a trust score (0–100), ranked findings, and Codex-generated fixes — entirely offline by default.

**The fix loop (under 2 minutes end-to-end):**
```
scan → trust_score=0, findings=15
fix --codex → Codex AI patch proposal (live API, redacted snippet only)
fix --apply → deterministic offline fix (14 rules, no API key)
rescan → trust_score=100, findings=0
```

**Key features:**
- **21-rule engine** mapped to OWASP MCP Top 10 and Agentic Skills guidance — tool poisoning, Unicode smuggling, unsafe shell, secrets, remote instruction fetch, transport hardening, least privilege
- **Two fix modes:** `--codex` (OpenAI Codex live API, human-reviewable patch) + `--apply` (deterministic regex, CI-safe, zero cost)
- **Trust score (0–100):** one number drives the CI gate
- **SARIF 2.1.0 output:** integrates with GitHub Security tab
- **GitHub Action:** blocks risky PRs, auto-posts scorecard comment
- **Offline-first:** zero API calls, zero token cost in default scan mode
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

**Codex integration:** `agentpreflight fix --codex` sends only a 5-line code window around the violation (redacted — no secrets, no file paths) to `codex-mini-latest` and returns a structured patch proposal. Developer reviews one diff. Rescan confirms.

**Shipped proof:** 30/30 tests passing, 113-artifact scan in 0.079s avg, SARIF 2.1.0 validates, fix loop cold-run `trust_score=0 → 100` verified May 27 2026.

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
| **Trigger** | Compliance audit, internal agent breach incident, or board-level AI governance pressure |
| **Decision** | Deploys AgentPreflight as mandatory PR gate across agent-related repositories |
| **Value** | SARIF output integrates with existing GitHub code scanning; trust score gives board-level metric |

**Where they are:** GitHub, Hacker News, LinkedIn AI/DevSecOps communities, OWASP Slack, MCP Discord.

**Why they convert:** Sub-second scan, zero cost default mode, one `pip install`, works with existing PR/CI. No account, no dashboard, no infra required.
