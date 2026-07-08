Q1. What problem did you solve?
Describe the problem, who experiences it, and why it matters.
A1. AI builders install MCP servers and agent skills from GitHub, registries, and local folders. These artifacts mix natural-language tool descriptions, executable code, config files, secrets, and permissions. A poisoned description or malicious skill can make an agent leak data, run unsafe commands, or follow hidden instructions before any runtime guardrail sees anything.

The missing gate is pre-deployment trust scoring for MCP servers and agent skills. Existing AppSec tools (Bandit, Semgrep) scan Python/JS syntax - they do not parse the semantic content of tool metadata strings. A Postmark-style BCC injection in a tool description is invisible to every general-purpose SAST tool on the market. The MCP specification requires clients to treat tool annotations from untrusted servers as untrusted - but provides no enforcement mechanism.

Scale of the problem:
- 36.82% of 3,984 scanned agent skills had at least one flaw; 13.4% had a critical issue (Snyk ToxicSkills 2025)
- 72.8% tool-poisoning attack success rate against o1-mini in one evaluated setting (MCPTox research)
- CVSS 9.6 RCE in mcp-remote, the package Claude Desktop uses for remote MCP (437,000+ downloads)
- 14 documented MCP security incidents in 12 months including a cross-tenant data leak affecting ~1,000 enterprise orgs (Asana, June 2025) and a supply-chain attack on the Postmark MCP npm package that ran undetected for 15 versions (September 2025)

Who experiences it: solo AI developers building or consuming MCP servers, AppSec engineers gating CI pipelines, and enterprise security teams needing org-wide visibility into agent extension risk.

Q2. Who is your target user?
Describe your ideal user and their pain points.
A2. Three primary personas:

1. Solo AI developer - installs MCP servers from npm/GitHub during active development. Pain: no fast, local signal on whether an extension is safe to run before committing it to a project.

2. AppSec/DevSecOps engineer - maintains CI pipelines for teams building agentic systems. Pain: standard SAST tools don't understand MCP semantics; there is no GitHub Code Scanning rule for tool poisoning or hidden Unicode in skill descriptions.

3. Enterprise security team - needs org-wide visibility and audit trails for agent extensions. Pain: no SARIF-based output format they can feed into GitHub Security tab or existing vulnerability dashboards.

Q3. How does your solution improve the user's life or workflow?
A3. AgentPreflight fits into the existing developer workflow at the PR/pre-commit stage:

- Scans fully offline in under 1 second on standard agent extension folders - no account, no API key, no network call required
- Outputs a trust score (0-100) giving an instant risk signal, not just a raw finding list
- Outputs SARIF 2.1.0 that GitHub Code Scanning accepts natively - no integration work required
- CLI exits 1 on threshold violations so CI gates work without any configuration beyond a flag
- `fix --apply` applies deterministic offline patches for 14 rule classes - no AI call, safe for every CI run
- `fix --codex` generates targeted Codex AI patch proposals in one command - developer reviews one diff and merges
- The full loop (scan - fail - fix - rescan - pass) completes in under 2 minutes in the demo

AgentPreflight is `npm audit fix` for agent extensions: a pattern developers already know, applied to an attack surface that has no dedicated tooling yet.

Q4. Describe your technical architecture.
Explain your stack, APIs, models, database, frontend, backend, etc.
A4. Stack: Python 3.11+, Typer (CLI framework), Rich (terminal rendering), FastAPI (optional HTTP endpoint).

Pipeline (offline static analysis only - never executes MCP servers or skill scripts):

  target path
    -> path collector
    -> artifact collectors (mcp.json, SKILL.md, Python/JS code, env files)
    -> unicode/text normalization (NFKC canonical form, zero-width character stripping)
    -> rule engine (21 deterministic rules, regex + pattern matching)
    -> trust scorer (base 100, severity-weighted deductions, combo caps)
    -> reporters (Rich table, JSON, SARIF 2.1.0, Markdown)
    -> optional Codex remediation (sends only redacted finding snippet to codex-mini-latest)
    -> rescan proof

Rule categories: tool_poisoning, unicode_smuggling, unsafe_exec, remote_instruction_fetch, secrets, transport_security, least_privilege.

Severity deductions: critical = 20pts, high = 15pts, medium = 7pts, low = 3pts. Conditional caps applied for high-risk combos (e.g., any critical caps score at 50; shell + network combo caps at 45).

Outputs: CLI table (Rich), JSON (structured finding objects), SARIF 2.1.0 (GitHub code scanning compatible), Markdown.

GitHub Action: wraps the CLI, uploads SARIF to GitHub Security tab, optional PR comment with scorecard.

API surface: POST /v1/scans FastAPI endpoint (pip install "mcp-agent-preflight-sec[api]").

Codex integration: uses OpenAI chat.completions API with codex-mini-latest. Sends only the redacted evidence snippet - no full file content, no secrets.

No database, no hosted dashboard, no auth/billing. Offline-first by design.

Q5. What features are fully working today?
A5. - 21 security rules across 7 categories, all validated against poisoned and clean fixtures
- CLI with 9 commands: scan, fix, watch, bench, prompts, rules (list/info/search), shell (interactive REPL), init, profiles
- 3 scan profiles: dev, balanced, strict (strict promotes medium findings to high before scoring)
- 4 output formats: Rich table, JSON, SARIF 2.1.0, Markdown
- Score-based CI gating via --fail-on (severity threshold) and --fail-on-score (trust score threshold)
- --fail-on-score 70 fails if trust score drops below 70 - complementary to severity-based gating
- Rule filtering by artifact type: rules list --applies-to code_py shows only rules relevant to Python code
- Deterministic offline fix (--apply): patches 14 rule classes, zero API calls
- Codex AI patch proposals (--fix --codex): live codex-mini-latest integration, returns structured patches
- Rescan proof: --prove flag rescans after --apply and prints before/after delta
- Suppression system: file-level .agentpreflight.json and inline # agentpreflight:disable-line
- Interactive shell (agentpreflight shell) with session state and command history
- Watch mode: polls target for file changes and rescans automatically
- GitHub Action in .github/workflows/agentpreflight.yml
- FastAPI endpoint POST /v1/scans
- `explain <rule_id>` top-level command - intuitive alias for `rules info` post-scan
- `--format github` output: GitHub Actions annotation format (::error/::warning/::notice) for inline PR diff comments without SARIF upload or GitHub Advanced Security
- 245 passing tests (pytest)
- SARIF 2.1.0 validated against schema

Q6. What was the most technically challenging part of the project?
A6. Two parts were particularly challenging:

1. Trust scoring with conditional caps. The scoring formula uses severity-weighted deductions (critical -20pts, high -15pts, medium -7pts, low -3pts) but also applies interaction caps: any critical finding caps the score at 50, three or more high findings cap at 60, shell + network combo caps at 45, Unicode override combo caps at 50. These interactions compound - the score takes the minimum of all applicable caps. Getting the cap logic correct and testing all combinations required careful fixture design and a dedicated test suite.

2. Unified rule model for heterogeneous artifact types. MCP servers expose security issues through natural-language tool descriptions (mcp.json) - semantic content that requires pattern matching against hidden-instruction phrases, capability claim patterns, and trust assertion strings. Agent skills (SKILL.md) are Markdown with embedded code. Python/JS code requires AST-adjacent pattern matching for unsafe shell calls, eval/exec usage, and subprocess configuration. All three artifact types share a common Artifact/Finding model but require fundamentally different detection strategies within the same rule engine pipeline.

Q7. How did you use Codex during the hackathon?
Be specific about coding, debugging, planning, refactoring, testing, etc.
A7. I used Codex as an active coding partner across implementation, debugging, packaging, and submission polish. Codex was not only embedded inside the product as the remediation engine; it also helped write and harden the codebase itself.

Specifically:

- Architecture and implementation planning: Codex helped turn the product spec into an implementation path: collectors, normalizers, rule engine, trust scorer, reporters, remediator, CLI, API, and GitHub Action support. This kept the build focused on the CLI-first MVP instead of drifting into a hosted dashboard too early.

- Writing and refactoring code: Codex helped implement rule classes, CLI commands, reporter output, scoring behavior, deterministic fixes, and tests. It also helped refactor lint failures without changing behavior, including import ordering, unused imports, and ambiguous variable names before publishing.

- Test-driven debugging: Codex was used to inspect failing tests, identify where behavior differed from the intended CLI contract, add focused regression tests, and rerun `pytest`/`ruff` until the repo reached a clean state. The final local validation before publish was 217 passing tests.

- Packaging and release: Codex helped prepare the package for PyPI, fix package metadata, rename the distribution after PyPI rejected `agentpreflight` as too similar to an existing project, publish `mcp-agent-preflight-sec`, then verify a fresh `pip install` in a temporary virtual environment.

- Product copy and submission materials: Codex helped update README/install references, write the Q12 video walkthrough script, and remove overclaiming language about winning or category uniqueness before pushing the final branch.

Q8. Which AI tools, models, or APIs did you use?
A8. - OpenAI Codex - used as the coding assistant for implementation, debugging, test writing, packaging, documentation, and release prep.
- OpenAI Codex / codex-mini-latest - integrated into the product as the AI remediation engine behind `agentpreflight fix --codex`.
- OpenAI chat.completions API - used by the product's Codex remediation path. It sends redacted finding snippets and receives structured patch proposals.

Q9. Share 2-3 examples where Codex significantly accelerated development.
A9. Codex significantly accelerated development in these areas:

Example 1 - Rule engine and scanner behavior:
Codex helped translate the rule catalog into working Python classes for MCP metadata, SKILL.md files, code files, network risks, secrets, and hidden Unicode. It also helped keep the common Artifact/Finding model consistent across heterogeneous file types so the CLI, JSON reporter, SARIF reporter, Markdown reporter, scorer, and fixer could all consume the same scan result.

Example 2 - Tests, linting, and release hardening:
Codex helped add and repair focused tests for CLI behavior, score thresholds, rule listing, quiet output, display paths, and reporter behavior. When `ruff check .` failed, Codex identified behavior-preserving fixes: move imports, remove unused imports, and rename ambiguous local variables. This got the project to `217 passed` and `ruff check .` passing before release.

Example 3 - PyPI packaging and live install verification:
Codex helped publish the CLI as a real pip-installable package. When PyPI rejected `agentpreflight` because the name was too similar to an existing project, Codex renamed the distribution to `mcp-agent-preflight-sec` while keeping the CLI entry point `agentpreflight`, rebuilt the wheel/sdist, ran `twine check`, uploaded to PyPI, and verified it in a fresh virtual environment with `agentpreflight --version` and a real scan.

Q10. Approximately how much of your development workflow was assisted by Codex?
A10. The Codex AI remediation feature (fix --codex) is one of the four primary product interfaces and was a significant development focus. Building, iterating on, and validating the Codex integration - prompt engineering, redaction pipeline, patch quality testing - occupied a meaningful portion of the hackathon development time.

For code outside the Codex integration (rules engine, scorer, reporters, CLI), AI-assisted development was also used throughout.
(Provide estimate, e.g. 40-60%)

Q11. Live Product URL
Share deployed product link. If its An APK, upload it to google drive link and share it
A11. PyPI package: https://pypi.org/project/mcp-agent-preflight-sec/0.1.0/

Install command:

  pip install mcp-agent-preflight-sec

CLI entry point:

  agentpreflight --version

Q12. Demo Video Walkthrough Link
Share a 2-5 minute walkthrough video.
Share your problem you're solving
Walk us through your product/app & how a user will use it
What should judges pay special attention to while reviewing your project?
Once the video is recorded upload it to google drive or youtube and share the link here, please make sure sharing setting is "Open For All" or else we wont be able to see it.

A12. Recording script for a 3-4 minute demo video:

Opening (0:00-0:30)

"AgentPreflight is a pre-deployment security scanner for MCP servers and agent skills. The problem is that AI tools now install extensions that mix natural-language tool descriptions, executable code, secrets, and permissions. A poisoned MCP description or malicious SKILL.md can make an agent leak data or run unsafe commands before normal runtime guardrails see it. AgentPreflight gives developers a local trust score, exact findings, SARIF output for CI, and a fix-and-rescan loop."

Show the install (0:30-0:55)

On screen:

  pip install mcp-agent-preflight-sec
  agentpreflight --version
  agentpreflight --help

Say:

"This is live on PyPI. After install, the CLI command is agentpreflight. No account or API key is needed for normal scans because the default scan mode is offline and static."

Show poisoned fixture scan (0:55-1:40)

On screen:

  agentpreflight scan poisoned --profile strict --fail-on high

Say:

"Here I scan a poisoned demo MCP/skill folder. The scanner finds high-risk patterns like tool poisoning, hidden Unicode, unsafe shell usage, remote instruction fetches, secrets, and missing security hardening. It prints a trust score, verdict, finding count, rule IDs, severity, file paths, and remediation hints. The --fail-on high flag makes it CI-friendly because high severity findings fail the command."

Optional short view:

  agentpreflight rules list
  agentpreflight rules info AP-MCP-001

Say:

"Judges should notice that these are agent-specific rules, not generic Python lint checks. It scans natural-language MCP metadata and skill files, where standard SAST tools usually miss prompt-level attacks."

Show fix loop (1:40-2:35)

On screen:

  Copy-Item poisoned $env:TEMP\agentpreflight-demo -Recurse -Force
  agentpreflight fix $env:TEMP\agentpreflight-demo --apply --prove

If using bash:

  cp -r poisoned /tmp/agentpreflight-demo
  agentpreflight fix /tmp/agentpreflight-demo --apply --prove

Say:

"Now I run the deterministic offline fixer. It applies constrained local fixes for supported rule classes, then --prove rescans the target and shows before-and-after evidence. This is the key workflow: scan, fix, rescan, prove. It is closer to npm audit fix for agent extensions than a scanner that only reports problems."

Optional Codex remediation mention (2:35-3:00)

On screen, if OPENAI_API_KEY is configured:

  agentpreflight fix poisoned --codex --rules AP-MCP-001

Say:

"For findings that need human review, AgentPreflight can also call Codex with only a redacted finding snippet, not the whole repo or secrets. Codex returns a targeted patch proposal that the developer reviews before applying."

If no API key during recording, say:

"I am not calling the Codex API in this recording, but the product includes a codex-mini-latest remediation path for targeted patch proposals. The offline fixer and scanner work without network access."

Show JSON/SARIF CI output (3:00-3:35)

On screen:

  agentpreflight scan poisoned --format json --output agentpreflight.json
  agentpreflight scan poisoned --format sarif --output agentpreflight.sarif

Say:

"For teams, the same scanner can write JSON for automation and SARIF 2.1.0 for GitHub Code Scanning. That means the tool fits into pull requests and security dashboards without a custom backend."

Close (3:35-4:00)

Say:

"What judges should pay attention to: the tool is published and installable from PyPI, the scanner is offline-first, the rules target MCP and agent-skill risks specifically, and the product does the full remediation loop: find, patch, and prove the result with a rescan."

After recording, upload the video to YouTube or Google Drive and set sharing to public/unlisted-with-link. Paste the video URL here:

A12 video link: Video walkthrough script is written above. Record the 4-minute demo, upload to YouTube or Google Drive (set sharing to public or unlisted-with-link), and add the URL here: __________

Q13. LinkedIn Or X/Twitter Submission Post URL
In The Post Include:
Key learnings or highlights from your hackathon journey
Introduce your product & who is it for
Upload the video of your product to the post
Tag OpenAI & Outskill social handles
Add tags #Outskill #OpenAI #Codex #AIBuildersHackathon in your post at the end
Once the post is done, share the link of your post here, you can choose any platfrom to make a social post.

Suggested post draft (copy, post, then paste URL below):

---
Built AgentPreflight at the #AIBuildersHackathon: a pre-deployment security scanner for MCP servers and agent skills.

Key learnings: MCP tool descriptions are natural-language and invisible to standard SAST tools. A poisoned description can make an agent leak data or run hidden commands before runtime guardrails see it. 36.82% of scanned skills had at least one flaw (Snyk ToxicSkills 2025).

AgentPreflight gives developers: a trust score (0-100), offline static analysis, SARIF output for GitHub CI, and a Codex-powered fix-and-rescan loop. It is npm audit fix for agent extensions.

[paste your video here]

Built with @OpenAI Codex (codex-mini-latest) for AI-assisted remediation. #Outskill #OpenAI #Codex #AIBuildersHackathon

pip install mcp-agent-preflight-sec
GitHub: https://github.com/mohanish3/AgentPreflightSec
---

A13 post URL: Draft post is written above. Copy the text, post to LinkedIn or X/Twitter with the video attached, and add the post URL here: __________

Q14. OpenAI Organisation ID
Go to the OpenAI Platform: https://platform.openai.com/settings/organization/general
Your Organization ID will be displayed on this page. It will look similar to: "org-xxxxxxxxxxxxxxxxxxxx"
Copy the entire Organization ID, including the `org-` prefix, and share it with us.
Incase you used multiple accounts, submit org id of all accounts
PS: This will help us track the usage of Codex & OpenAI models and be rest assured team cannot see any of your personal data or conversations it just shows how much did you use OpenAI models
A14. Retrieve from platform.openai.com/settings/organization/general - will appear as org-XXXXXXXXXXXXXXXXXX. Add here: __________

Q15. What are you most proud of building during this hackathon?
A15. I am most proud that AgentPreflight is not a mockup or a one-off demo. It is a shipped developer tool that can be installed from PyPI, run locally, fail CI, produce SARIF, apply fixes, and prove the result with a rescan.

The strongest part is the closed loop:

  scan -> trust score -> fix -> rescan proof

A developer can start with a poisoned MCP or skill folder, see exactly why it is unsafe, apply deterministic fixes or request a Codex patch proposal, then rescan and show evidence that risk dropped. That is the difference between "here is a scary finding" and "here is a workflow that helps you ship safer code."

I am also proud of the product discipline. The tool stayed offline-first by default, never executes scanned code, redacts snippets before Codex remediation, and uses formats developers already understand: CLI output, JSON, SARIF, Markdown, exit codes, and PyPI install. The result is small enough to trust, but complete enough to use in a real pull request.

What I built is not just a scanner. It is a remediation-first safety gate for the new agent-extension supply chain.

Q16. Anything else you'd like the judges to know?
A16. The reason this project matters is that agent extensions changed the security boundary. MCP servers and agent skills are not normal dependencies: they contain code, configuration, permissions, tool descriptions, and natural-language instructions that the agent may treat as operational guidance. That creates a new supply-chain surface where a dangerous instruction can live in metadata, not just in executable code.

AgentPreflight focuses on that gap. It does not try to be a giant platform. It does one high-leverage job: before an agent runs an extension, inspect the local files, identify MCP/skill-specific risks, assign a trust score, provide machine-readable output for CI, and help the developer remediate.

The implementation choices are intentional:

- Offline by default, so scanning does not leak source code.
- Static by default, so suspicious tools are not executed during analysis.
- SARIF output, so results fit GitHub Code Scanning instead of living in a separate dashboard.
- Codex remediation, but constrained to redacted snippets and reviewable patch proposals.
- Rescan proof, so the developer can verify that the fix actually reduced risk.

This is the kind of tool I would want in every repository that installs MCP servers or agent skills: fast enough for local development, strict enough for CI, and practical enough that developers will actually use it.

If the core question is "does this use Codex to create real leverage?", my answer is yes: Codex is used both as a development accelerator and as part of the product's remediation workflow. The final result is live, installable, test-covered, and designed around a real security problem that is growing with the agent ecosystem.
