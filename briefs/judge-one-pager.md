# AgentPreflight — Investment Brief

**Category:** Developer Security Infrastructure  
**Stage:** Shipped MVP  
**Tagline:** `npm audit fix` for MCP servers and agent skills.

---

## The Opportunity

Every AI developer today installs MCP servers and agent skills the same way: pull from npm, GitHub, or a registry, and trust the description. No pre-deployment gate exists. The agent ecosystem is growing at the speed of Copilot — 1M+ pull requests created by Copilot coding agents (May–Sep 2025) — and the security tooling is twelve months behind.

The missing gate is pre-deployment trust scoring. AgentPreflight is that gate.

---

## The Problem

In September 2025, an attacker copied the legitimate Postmark MCP server on npm. They maintained 15 versions — a real commit history, a real profile picture — then in a single commit added one BCC line to `send_email`. Every password reset token, payment confirmation, and account notification silently forwarded to an attacker-controlled address. No runtime firewall caught it. No AppSec scanner flagged it.

This was not an anomaly. In the 12 months between April 2025 and April 2026, authzed.com documented **14 distinct MCP security incidents**: WhatsApp message exfiltration, GitHub private repo exposure, Anthropic's own filesystem server sandbox escape (CVSS 8.4), a Smithery supply-chain breach hitting 3,000+ apps, and a core STDIO architectural flaw affecting 150M+ downloads.

The vulnerability data is stark:

- **Snyk ToxicSkills (2025):** 3,984 agent skills scanned — 36.82% had at least one flaw; 13.4% had a critical issue.
- **Equixly March 2025 audit:** Popular MCP server implementations — 43% had command injection, 30% SSRF, 22% path traversal.
- **CVE-2025-6514:** `mcp-remote` (the package Claude Desktop uses for remote MCP) — CVSS 9.6 RCE, 437,000+ downloads.
- **CVE-2025-53109/53110:** Anthropic's official filesystem MCP server — CVSS 8.4 sandbox escape, unpatched for three months.
- **Official Puppeteer MCP server** — 91,000 monthly downloads, SSRF + prompt injection + sandbox bypass simultaneously. Archived rather than patched.

Runtime defenses fail this attack class. Invariant Labs demonstrated a "rug pull" where a malicious MCP server served innocent tool descriptions on first launch, switched to hidden instructions on the second — after trust was already granted. In one evaluated setting, MCPTox found a 72.8% tool-poisoning attack success rate; the best-defending model refused fewer than 3% of attacks.

The attack surface is new: MCP tool descriptions are natural-language, invisible to standard CI checks, and poisoned before the agent ever runs.

---

## The Product

AgentPreflight is a pre-deployment static scanner for MCP servers and agent skills. One command produces a trust score (0–100), ranked findings mapped to OWASP rule IDs, and a two-mode fix loop that goes from failing scan to passing PR in under two minutes.

```bash
# Scan — entirely offline, sub-second
$ agentpreflight scan demo/poisoned --profile strict --fail-on high
trust_score=0  verdict=fail  findings=15  critical=7  high=5

# Codex AI patch proposal (requires OPENAI_API_KEY)
$ agentpreflight fix demo/poisoned --codex --rules AP-MCP-001
CODEX PATCH AP-MCP-001  mcp.json:5
"description": "Search repository files and return matching lines. Does not execute code or access secrets."

# Deterministic offline fix — no API key, no cost
$ cp -r demo/poisoned /tmp/fix-demo && agentpreflight fix /tmp/fix-demo --apply

# Rescan proves the repair
$ agentpreflight scan /tmp/fix-demo --profile strict --fail-on high
trust_score=100  verdict=pass  findings=0
```

**Two fix modes. Both ship. Both are real code.**

- `--codex`: Live `chat.completions.create` call to `codex-mini-latest`. Sends only the redacted finding snippet — no file paths, no secrets. Returns a structured patch proposal the developer reviews and merges.
- `--apply`: Deterministic regex rewrite engine covering 14 rules across four categories (MCP, Skill, Code, Secrets). Works offline. Safe in every CI run.

**Codex as decision layer, not code generator.** Code rewriting is cheap. The scarce resource in security remediation is *selection*: which of the infinite possible rewrites is minimal, secure, compilable, and review-ready? Given the flagged line, the OWASP rule ID, and the constraint "return only the drop-in replacement," Codex selects `subprocess.run([...], check=True)` over every alternative. The developer reviews one diff. The rescan proves it held.

---

## Proof

| Metric | Result |
|---|---|
| True positive rate on seeded fixtures | 100% (15/15) |
| False positive rate on clean fixtures | 0% (0 false positives on `demo/clean`) |
| Median scan time | 0.079s avg (113-artifact benchmark) |
| API calls in default scan | 0 — fully offline |
| SARIF 2.1.0 validity | Schema validates |
| Fix loop (cold run, May 27) | `trust_score=0 → 100` in under 2 minutes |
| Unit tests | 30/30 passing |

---

## Competitive Position

Multiple MCP scanners exist. The wedge is not detection breadth — it is **time-to-fix**.

| | Static Scanners (mcp-scan) | Runtime Firewalls (Llama Guard) | AgentPreflight |
|---|---|---|---|
| Pipeline stage | Pre-deployment | Runtime | **Pre-deployment git gate** |
| Remediation | Finds only | Blocks only | **Codex patch + rescan proof** |
| Fix quality | — | — | **AI-generated, developer-reviewable** |
| CI integration | SARIF | None | **SARIF + `--fail-on` exit code** |

Existing scanners stop at the finding. AgentPreflight closes the PR.

---

## Why Now

- MCP protocol adoption is accelerating: 150M+ downloads on core packages.
- OWASP released MCP and Agentic Skills security guidance in 2025 — the standards infrastructure now exists.
- 14 documented incidents in 12 months — the risk is active, not theoretical.
- Developer toolchain (GitHub Actions, SARIF, PR review) is exactly where this gate belongs.
- No dominant remediation-first tool exists yet. The scanner market is crowded; the fix market is not.

---

## Why AgentPreflight

- **Offline-first.** Zero token cost in default scan mode. Security teams with sensitive codebases can audit without API exposure.
- **Codex is structural, not decorative.** The `--codex` flag is a live API call, not a template fill. The demo shows it. The rescan proves it held.
- **Developer workflow, not security dashboard.** `scan → fix → rescan` fits any PR review in under two minutes.
- **Shipped.** 30 tests, SARIF validates, GitHub Action wired, benchmark proofed, fix loop cold-run verified May 27 2026.
