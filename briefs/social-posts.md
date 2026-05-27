# Social Posts — Build in Public

## LinkedIn Post (Day 1/2 — May 27)

---

🔐 Day 2 of the OpenAI x Outskill Hackathon — shipping AgentPreflight.

In September 2025, an attacker copied a legitimate MCP server on npm, maintained 15 versions to look real, then added one BCC line to `send_email`. Every password reset token forwarded to an attacker address. No CI check caught it.

That's the problem I'm building against.

**AgentPreflight** is a pre-deployment security scanner for MCP servers and agent skills — `npm audit fix` for your AI agent extensions.

Here's the full loop in under 2 minutes:

```
$ agentpreflight scan demo/poisoned --profile strict --fail-on high
trust_score=0  verdict=fail  findings=15  critical=7  high=5

$ agentpreflight fix demo/poisoned --codex --rules AP-MCP-001
CODEX PATCH AP-MCP-001  mcp.json:5
"description": "Search repository files and return matching lines."

$ agentpreflight fix /tmp/fix-demo --apply

$ agentpreflight scan /tmp/fix-demo --profile strict
trust_score=100  verdict=pass  findings=0
```

Poisoned repo → Codex patch → clean rescan. Offline by default. Live Codex API for the fix.

The data behind this:
→ 36.82% of 3,984 scanned agent skills had at least one flaw (Snyk ToxicSkills)
→ 43% of popular MCP servers had command injection (Equixly March 2025)
→ CVSS 9.6 RCE in mcp-remote — 437,000+ downloads

What's shipped so far:
✅ 21-rule engine (OWASP MCP + Agentic Skills taxonomy)
✅ Trust score 0–100 with SARIF output
✅ Two fix modes: Codex AI patches + deterministic offline fix
✅ GitHub Action for PR gating
✅ 30 unit tests passing, sub-second scan

Building in public. #OpenAIHackathon #OutskillHackathon #MCP #DevSecurity #AIAgents #Codex

---

## X (Twitter) Thread — Day 2

**Tweet 1:**
Shipping AgentPreflight for @OpenAI x @OutskillHQ hackathon 🧵

An attacker added 1 BCC line to a fake Postmark MCP server. Every password reset token forwarded to them. No CI check caught it.

I'm building the gate that stops this.

**Tweet 2:**
AgentPreflight scans MCP servers + agent skills before they ship.

Static analysis. No model calls. Sub-second.

trust_score=0 → Codex patch → trust_score=100. Under 2 minutes.

**Tweet 3:**
The data is real:
• 36.82% of 3,984 agent skills had a flaw (Snyk)
• 43% of MCP servers had command injection (Equixly)
• CVSS 9.6 RCE in mcp-remote (437k+ downloads)

**Tweet 4:**
Two fix modes:
→ --codex: live codex-mini-latest API call, redacted snippet only, human-reviewable patch
→ --apply: deterministic offline fix, 14 rules, zero API cost

Both ship. Both are real code.

**Tweet 5:**
Shipped today:
✅ 21-rule OWASP-mapped engine
✅ Trust score + SARIF output
✅ Codex fix loop verified end-to-end
✅ 30 tests passing

#OpenAIHackathon #MCP #Codex #AgentSecurity

---

## Form field answers

**"What have you done today?"**
Built and shipped AgentPreflight MVP — static pre-deployment security scanner for MCP servers and agent skills. 21-rule detection engine covering tool poisoning, Unicode smuggling, unsafe exec, secrets, transport hardening. Trust score 0–100, JSON/SARIF output, live Codex AI patch proposals via `fix --codex` (codex-mini-latest), deterministic offline fix via `--apply`, GitHub Action for PR gating, 30 unit tests passing, fix loop cold-run verified (trust_score=0 → 100 in under 2 min). Phase 1 deliverables complete: pitch deck (4 slides), user flow doc, ICP defined.

**"Let us know if you are facing any issue"**
No blockers. MVP shipped. One pending: running fix --codex with real OPENAI_API_KEY for live Codex end-to-end verification before Session 1.
