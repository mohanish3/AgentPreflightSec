# AgentPreflight: Research Evidence

---

## Real-World MCP Security Incidents

Research method: Web search + WebFetch on primary URLs. Claims labelled with source and date method. Unverified claims flagged.

### 1. Asana MCP Cross-Tenant Data Leak — June 2025

Asana launched MCP server feature May 1, 2025. Logic flaw in tenant isolation allowed users to access other organizations' project data, tasks, comments, and files for over one month until June 4, 2025. ~1,000 enterprise customers notified.

**Why it matters:** Enterprise SaaS. Named company. Real user data. The MCP server was the attack surface — not the core product. A pre-deployment MCP scan could have flagged the broken tenant-isolation logic before launch.

Source: BleepingComputer — fetched directly. https://www.bleepingcomputer.com/news/security/asana-warns-mcp-ai-feature-exposed-customer-data-to-other-orgs/ (June 4, 2025, date confirmed by WebFetch).

### 2. Invariant Labs Tool Poisoning + WhatsApp Exploit — April 2025

MCP tool descriptions — visible to AI models but hidden from users — can be weaponized. Two attacks demonstrated:

- **Rug pull:** Malicious MCP server served innocent tool descriptions on first launch. On second launch, description changed to hidden instructions redirecting any WhatsApp messages to an attacker-controlled number, including full chat history.
- **Message injection:** Crafted WhatsApp message containing prompt injection code caused agent processing `list_chats` to leak contact information — no malicious MCP server required.

Direct quote (Invariant Labs blog, fetched): "An untrusted MCP server can attack and exfiltrate data from an agentic system...side-stepping WhatsApp's encryption and security measures."

Invariant Labs also published `mcp-scan` — validates the market for a preflight scanner.

Sources: https://invariantlabs.ai/blog/mcp-security-notification-tool-poisoning-attacks (April 1, 2025) and https://invariantlabs.ai/blog/whatsapp-mcp-exploited (April 7, 2025). Dates confirmed by WebFetch.

### 3. CVE-2025-6514: mcp-remote RCE (CVSS 9.6) — July 2025

JFrog disclosed critical OS command-injection in `mcp-remote`, the npm package allowing LLM hosts (Claude Desktop, others) to talk to remote MCP servers. Malicious server responds with crafted `authorization_endpoint` URL that executes arbitrary commands when passed to OS `open()`.

- CVSS: 9.6 (Critical)
- Affected: versions 0.0.5 to 0.1.15 (fixed in 0.1.16)
- Downloads: 437,000+ at time of disclosure
- Attack: Windows = full arbitrary OS command execution; macOS/Linux = arbitrary executable execution

JFrog quote (fetched): "This is the first time that full remote code execution is achieved in a real-world scenario on the client operating system when connecting to an untrusted remote MCP server."

Sources: https://jfrog.com/blog/2025-6514-critical-mcp-remote-rce-vulnerability/ and https://github.com/advisories/GHSA-6xpm-ggf7-wc3p. Disclosure July 9, 2025 — confirmed by WebFetch.

### 4. Postmark MCP Supply Chain Attack — September 2025

Attacker copied legitimate Postmark MCP server code, republished on npm under same name, maintained for 15 versions to build trust. Then added single BCC line to `send_email` function silently copying every email to attacker address — intercepting password reset tokens, account confirmations, and payment notifications. Consistent commit history and profile picture — appeared fully legitimate.

**Why it matters:** Classic supply-chain compromise pattern identical to what `npm audit` catches in code packages — but in the MCP ecosystem pre-install scanner coverage is still fragmented. This is the exact scenario AgentPreflight must handle.

Source: Semgrep blog — fetched. https://semgrep.dev/blog/2025/so-the-first-malicious-mcp-server-has-been-found-on-npm-what-does-this-mean-for-mcp-security/ (September 25, 2025, confirmed by WebFetch).

### 5. Anthropic Filesystem MCP Server — Sandbox Escape (CVE-2025-53109/53110) — 2025

Cymulate found two CVEs in Anthropic's own official filesystem MCP server (all versions before 0.6.3 / 2025.7.1):

- **CVE-2025-53110** (CVSS 7.3): Naive prefix-string path check allowed directory containment bypass.
- **CVE-2025-53109** (CVSS 8.4): Crafted symlink bypassed sandbox entirely, allowing read/write to `/etc/sudoers` and dropping macOS Launch Agents for code execution.

Timeline: Discovered March 30, 2025 → Vendor acknowledgment May 1, 2025 → Patch July 1, 2025. Three-month disclosure lag on Anthropic's own reference server.

Source: https://cymulate.com/blog/cve-2025-53109-53110-escaperoute-anthropic/ — confirmed by WebFetch.

### 6. Equixly Audit: 43% of MCP Servers Had Command Injection — March 2025

Equixly assessed popular MCP server implementations:
- 43% — command injection vulnerabilities
- 30% — SSRF vulnerabilities
- 22% — path traversal / arbitrary file read

Vendor response: 30% acknowledged and fixed, 45% dismissed as "theoretical," 25% no response.

Quote (fetched): "It feels like we're facing a regression in security." Developer community adopted: "The 'S' in MCP stands for Security" (sarcastically).

Source: https://equixly.com/blog/2025/03/29/mcp-server-new-security-nightmare/ (March 29, 2025, confirmed by WebFetch).

### 7. Official Puppeteer MCP Server — SSRF, Prompt Injection, Sandbox Bypass — March 2026

GitHub Issue #3662 documented three high-severity vulns in `@modelcontextprotocol/server-puppeteer`:
- SSRF via `puppeteer_navigate` accepting arbitrary URLs with no schema filtering
- Indirect prompt injection via malicious webpage HTML comments → arbitrary JS execution → cookie/credential exfiltration
- Sandbox bypass via default `--allow-dangerous` flag

~91,000 monthly npm downloads. Repository archived. No active security maintenance.

Source: https://github.com/modelcontextprotocol/servers/issues/3662 (March 21, 2026, confirmed by WebFetch).

### 8. OX Security: Architectural RCE Flaw — 200,000 MCP Servers — April 2026

OX Security disclosed systemic design flaw in Anthropic's MCP STDIO transport enabling arbitrary command execution across all language SDKs (Python, TypeScript, Java, Rust). Not a patchable bug — architectural: unauthenticated command injection via STDIO interfaces.

Scale: 150+ million downloads, 7,000+ publicly accessible servers, ~200,000 vulnerable instances. Anthropic declined to modify protocol architecture, citing behavior as "expected." OX executed commands on six live production platforms including LiteLLM, LangChain, IBM LangFlow.

Source: https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/ (April 2026 — per search snippets from multiple outlets, not independently WebFetched. Flag: multi-source corroborated, date per search snippets.)

### 9. Full MCP Breach Timeline (April 2025 — April 2026)

Source: authzed.com timeline — fetched directly. https://authzed.com/blog/timeline-mcp-breaches

| Month | Incident |
|---|---|
| April 2025 | WhatsApp MCP exploit — full message history exfiltration |
| May 2025 | GitHub MCP prompt injection — private repo data including financial info |
| June 2025 | Asana MCP cross-tenant isolation failure — ~1,000 customers |
| June 2025 | MCP Inspector RCE — unauthenticated, exposes filesystem and API keys |
| July 2025 | mcp-remote command injection (CVE-2025-6514, CVSS 9.6, 437k downloads) |
| August 2025 | Anthropic Filesystem MCP sandbox escape (CVE-2025-53109/53110) |
| September 2025 | Postmark MCP supply-chain BCC injection |
| September 2025 | Flowise systemic STDIO RCE |
| October 2025 | Smithery supply-chain breach — Docker and Fly.io credentials for 3,000+ apps |
| October 2025 | Figma/Framelink RCE via unsanitized shell input |
| January 2026 | Gemini MCP tool 0-day — unauthenticated RCE |
| February 2026 | Oura MCP malware campaign — StealC credential harvester |
| March 2026 | nginx-ui auth bypass — complete nginx service takeover on 2,600+ instances |
| April 2026 | Core MCP STDIO architectural flaw — 150M+ downloads affected |

---

## Developer Community Evidence

### Hacker News: "The 'S' in MCP Stands for Security" (March 2025)

URL: https://news.ycombinator.com/item?id=43600192 — 183 comments.

Top comments (fetched):

> **wat10000** (602 points): "The fact that all LLM input gets treated equally seems like a critical flaw that must be fixed before LLMs can be given control over anything privileged."

> **lbeurerkellner** (Invariant Labs): "The problem here is a special form of indirect prompt injection...one MCP server can easily override and manipulate the agent's behavior with respect to another MCP server."

> **TeMPOraL** (621 points): "Security and usefulness are opposing forces...all it takes is some little bug in your input parser, and suddenly data becomes code."

Top two comments by vote both assert the fundamental architecture is broken and the problem cannot be safely ignored. 600+ point votes indicate very wide developer agreement.

### GitHub Issue #630 — "MCP Server terminology creates dangerous user misconceptions" (June 2025)

URL: https://github.com/modelcontextprotocol/modelcontextprotocol/issues/630

Anthropic closed this issue as "not planned" — fundamental security communication gap acknowledged but protocol won't be changed. This is exactly the gap a preflight scanner fills.

---

## Scale Evidence

### Snyk ToxicSkills (February 2026)

3,984 skills scanned from ClawHub and skills.sh:
- 36.82% (1,467) have at least one security flaw
- 13.4% (534) have at least one critical issue
- 76 confirmed malicious payloads
- 8 remained publicly available at publication
- 91% of malicious skills combined prompt injection with traditional malware techniques

Skills can inherit shell, filesystem, credential, and messaging access from agents — not harmless prompts. They are executable supply-chain artifacts.

Source: https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/

### MCPTox (August 2025)

45 real-world MCP servers, 353 authentic tools, 1,312 malicious test cases. Attack success rate with o1-mini: 72.8%. Claude-3.7-Sonnet refusal rate: less than 3%.

Source: https://arxiv.org/abs/2508.14925 and https://ojs.aaai.org/index.php/AAAI/article/download/40895/44856

### GitHub Octoverse 2025

- 986M commits in 2025.
- 47.5M pull requests, up 20.4%.
- 1.13M+ public repos import generative AI SDKs, up 178% YoY.
- ~80% of new GitHub users tried Copilot within first week.
- 1M+ pull requests created by Copilot coding agent (May–Sep 2025).

Implication: agent/tool/security review must fit PR and CI workflows. Manual review cannot keep pace.

Sources: https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/ and https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/

### IBM Cost of a Data Breach 2025

- Global average breach cost: $4.4M
- 97% of organizations with AI-related security incident lacked proper AI access controls
- 63% lacked AI governance policies
- Extensive AI/security automation associated with $1.9M cost savings vs. organizations without

Source: https://www.ibm.com/reports/data-breach

---

## Evidence Matrix

| Evidence | Product decision |
|---|---|
| OWASP Agentic Skills Top 10: skills define real-world agent workflows and are under-protected. | Scan `SKILL.md`, skill manifests, scripts, permissions, and workflow instructions — not only MCP manifests. |
| Snyk ToxicSkills: 3,984 skills, 36.82% flawed, 13.4% critical, 76+ malicious. | Skill scanning first-class in MVP; include malicious/benign skill fixtures. |
| MCP spec: clients must treat tool annotations from untrusted servers as untrusted. | Add rule family for untrusted metadata and over-assertive annotations. |
| OWASP MCP Tool Poisoning: indirect prompt injection via MCP tool responses; privileged tools + external MCP servers = high risk. | Detect remote instruction fetch, dangerous tool result channels, sensitive file access, and network egress combinations. |
| MCPTox: 72.8% attack success in one evaluated model setting. | Use tool-poisoning fixtures as core demo and label risk as empirical, not hypothetical. |
| Snyk Agent Scan already scans skills and MCP servers. | Differentiate with Codex remediation, transparent rules, trust score, SARIF-first GitHub Action, policy packs, and demo-focused UX. |

---

## Validation Plan

### Targets

| Goal | Target |
|---|---|
| Catch seeded malicious fixtures | 90%+ true positive rate across MVP rule packs |
| Limit noise | under 10% false positive rate on benign fixtures |
| Fit CI | under 30 seconds on small repos |
| Preserve privacy | zero network calls in default scan |
| Integrate with GitHub | valid SARIF 2.1.0 output |
| Support remediation | Codex patch suggestion for every critical/high MVP finding class |
| Prove remediation loop | poisoned demo repo fails, patch applies, rescan passes under two minutes |

### Fixture matrix

| Fixture | Malicious case | Benign control |
|---|---|---|
| MCP description | tool description says ignore previous instructions or send secrets | neutral capability description |
| MCP schema | arbitrary free-form input schema for privileged tool | narrow required fields and enum/format constraints |
| Skill docs | zero-width prompt injection in `SKILL.md` | clean skill instructions with same visible text |
| Remote fetch | skill says fetch instructions from URL | skill fetches data from documented API only |
| Shell | `os.system(f"...{user_input}")` | `subprocess.run([...], check=True)` with allowlisted args |
| Secrets | committed private key or API token | `.env.example` placeholder |
| Transport | `0.0.0.0` unauthenticated local server | loopback-only or authenticated server |

### Demo validation

1. Poisoned repo looks plausible in normal review.
2. Scanner catches at least one MCP, one skill, and one code issue.
3. CLI exits nonzero with `--fail-on high`.
4. SARIF artifact exists.
5. `agentpreflight fix` changes only risky lines.
6. Rescan improves trust score and passes.
7. SARIF no longer reports fixed rule IDs.

### Residual risks

- Static scan cannot prove runtime safety.
- Rule patterns can miss novel obfuscation.
- Codex-generated fixes require human review.
- MVP fixes limited to: tool description rewrite, Unicode cleanup, remote instruction removal, unsafe shell hardening, secret redaction.
- MCP/skill ecosystems may use formats outside MVP collectors.

Frame: preflight gate, not full runtime sandbox.

---

## Risk Register

| Risk | Impact | Likelihood | Mitigation |
|---|---|---:|---|
| Demo feels like grep | reviewers discount novelty | medium | use subtle poisoned payloads, trust score drop, SARIF CI view, Codex patch loop |
| SARIF upload fails | CI demo weakens | medium | validate SARIF locally, use GitHub official upload action, keep JSON fallback |
| False positives too noisy | developer utility weak | medium | severity tiers, suppressions with expiry, benign fixtures |
| Static scan misses runtime behavior | false confidence | high | position as preflight gate; dynamic sandbox is stretch, not core claim |
| Codex remediation patch poor | demo fails | medium | restrict remediation to exact-line high-confidence rules first |
| Scope creep | MVP incomplete | high | cut FastAPI, HTML report, dynamic sandbox, broad RAG parsing |
| Source claims challenged | credibility loss | medium | use `sources/source-register.md`; avoid unverified claims |
| Cross-platform path issues | scanner bugs | medium | normalize paths and test Windows-style fixtures |
| Secret leakage during remediation | privacy/security issue | low/medium | redact snippets and default to offline scan |

Hard cut line — ship even if time is short: CLI scan, trust score, JSON, SARIF, 15+ rules, poisoned demo repo, one Codex remediation path.

Cut first: FastAPI, HTML report, dynamic sandbox, hosted service, broad TypeScript coverage.

---

## Verification Audit

### Corrected

- Competitor count reduced to max 10 to match `workflow.md`.
- Unsupported "occupied/solved" claims removed.
- Product naming normalized to **AgentPreflight**.
- Static MCP/skill scanning confirmed as primary product — verified sources show need remains active despite Snyk Agent Scan existing.
- Codex config linter moved to future module — official OpenAI/Codex config source validation needed first.
- Dynamic skill sandbox moved to stretch — Docker/network tracing raises four-day delivery risk.

### Claims requiring verification before use

- "80% of developer environments use insecure Codex policies"
- "Prisma AIRS dominates RAG pre-ingestion sanitization"
- "Mend.io released automated prompt hardening in March 2026"
- "MCP-SandboxScan arXiv Jan 2026"
- exact Codex config keys (`approval_policy`, `allowed_network_hosts`, `allow_unauthenticated_localhost`)
- "Wiz State of AI 2026: 80% of orgs adopting MCP" — until source is directly reviewed
- competitor acquisition/shutdown/pricing claims unless source is directly reviewed
- exact current OpenAI/Codex model names and pricing unless from official OpenAI docs
- "$84M/year" or other precise ROI claims unless shown as rough estimate with assumptions
- "no competitor offers SARIF/GitHub Action for MCP" — false; Aguara and agent-audit appear to offer this
- "AgentPreflight is the first MCP/skill scanner" — false; Snyk Agent Scan, Aguara, agent-audit, AgentAuditKit, SkillScan overlap the category

### Corrected positioning (2026-05-25)

Verified safer: Remediation-first validated by GitHub Copilot Autofix, Snyk Agent Fix, and Semgrep Autofix in adjacent AppSec workflows. AgentPreflight should claim narrower gap: Codex-assisted fixes for MCP/skill natural-language supply-chain findings, followed by rescan proof. Avoid claiming no direct competitor has `fix` — AgentAuditKit publicly lists a `fix` command.

Do not claim: "no competitor has SARIF," "first scanner," "unique risk scoring," or any singular capability. Multiple scanners now have these.

Evaluation strength depends on demo polish and fix-loop quality, not category novelty.

---

## Evaluation Scorecards

### Final scorecard (1–10)

| Candidate | Demo evaluation fit | Feasibility | 10x workflow | Demo wow | Cost | Scale | Differentiation | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| AgentPreflight safe remediation-first | 8 | 8 | 10 | 10 | 9 | 9 | 6 | 60 |
| DeployPreflight destination-aware redeploy | 6 | 7 | 8 | 8 | 8 | 10 | 4 | 51 |
| RAG ingestion gate | 6 | 6 | 7 | 6 | 7 | 8 | 7 | 47 |
| Prompt leakage audit | 5 | 10 | 5 | 5 | 10 | 7 | 4 | 46 |

### Scoring rubric (1–5)

| Axis | 1 | 3 | 5 |
|---|---|---|---|
| Codex leverage | Codex only writes boilerplate. | Codex helps build or explain findings. | Codex is central to remediation, tests, and demo. |
| 4-day ship viability | Needs broad infra or model research. | Shippable with narrow cuts. | CLI/API/demo robust in four days. |
| Developer value | Nice-to-have lint. | Saves review time. | Blocks high-risk incidents or CI failures. |
| Market timing | Generic or crowded. | Active need but many tools exist. | New urgent surface with standards/research converging. |
| Novelty/wow | Looks like existing linter. | Specific demo, moderate surprise. | Judges see a fresh agentic security gap instantly. |

AgentPreflight should not rely on scanner novelty because 15+ direct competitors now overlap. The stronger case is realistic build scope, a clear demo loop, and remediation-first positioning validated by adjacent markets.
