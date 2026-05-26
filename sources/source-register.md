# Source register

Current as of 2026-05-25. Used to ground problem scale, competitor gaps, and MVP choice.

| Source | URL | What it supports |
|---|---|---|
| OWASP MCP Top 10 | https://owasp.org/www-project-mcp-top-10/ | MCP-specific risk taxonomy, including prompt injection via contextual payloads and command injection risks. |
| OWASP Agentic Skills Top 10 | https://owasp.org/www-project-agentic-skills-top-10/ | Skills are an under-protected execution layer across agent platforms. |
| OWASP MCP Tool Poisoning | https://owasp.org/www-community/attacks/MCP_Tool_Poisoning | Defines MCP tool poisoning as indirect prompt injection through MCP tool responses and highlights privileged-tool exposure. |
| MCP tool specification | https://modelcontextprotocol.io/specification/2025-06-18/server/tools | Tool annotations from untrusted servers must be treated as untrusted. |
| MCP schema reference | https://modelcontextprotocol.io/specification/2025-11-25/schema | Tool descriptions are model-facing hints; clients should not trust untrusted annotations. |
| MCPTox paper | https://arxiv.org/abs/2508.14925 | Benchmark for MCP tool poisoning; reports 72.8% attack success for one evaluated model setting. |
| MCPTox AAAI PDF | https://ojs.aaai.org/index.php/AAAI/article/download/40895/44856 | Peer-reviewed/full-paper source for tool poisoning benchmark details. |
| Snyk ToxicSkills | https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/ | 3,984 skills scanned; 13.4% critical issue rate; 36.82% at least one flaw. |
| IBM Cost of a Data Breach 2025 | https://www.ibm.com/reports/data-breach | $4.4M average breach cost; AI oversight/access-control gap; security automation savings. |
| GitHub Octoverse 2025 developer workflow | https://github.blog/news-insights/octoverse/what-986-million-code-pushes-say-about-the-developer-workflow-in-2025/ | PR/CI workflow scale and expectation that automated checks run on pushes. |
| GitHub Octoverse 2025 AI adoption | https://github.blog/news-insights/octoverse/octoverse-a-new-developer-joins-github-every-second-as-ai-leads-typescript-to-1/ | AI SDK repo growth, Copilot first-week adoption, and coding-agent PR scale. |
| GitHub upload SARIF docs | https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/uploading-a-sarif-file-to-github | GitHub code scanning upload flow using `github/codeql-action/upload-sarif`. |
| GitHub SARIF support docs | https://docs.github.com/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning | GitHub SARIF support details and result-display behavior. |
| OASIS SARIF 2.1.0 | https://docs.oasis-open.org/sarif/sarif/v2.1.0/os/sarif-v2.1.0-os.html | SARIF 2.1.0 log format reference. |
| GitHub composite action docs | https://docs.github.com/en/actions/tutorials/create-actions/create-a-composite-action | Custom/composite action structure using `action.yml`. |
| Aguara scanner | https://aguarascan.com/ | Direct competitor: local security scanner for AI agents and software supply chains. |
| Aguara GitHub Actions docs | https://garagon-aguara-88.mintlify.app/ci/github-actions | Direct competitor evidence: GitHub Action and SARIF upload workflow. |
| agent-audit GitHub | https://github.com/HeadyZhang/agent-audit | Direct competitor: static LLM-agent scanner with SARIF/GitHub Action and MCP config auditing. |
| Agent Audit paper | https://arxiv.org/abs/2603.22853 | Research/source basis for agent-audit capabilities. |
| Agentic Radar GitHub | https://github.com/splx-ai/agentic-radar | Direct/adjacent competitor: agentic workflow security scanner and MCP detection. |
| Snyk Agent Scan repo | https://github.com/snyk/agent-scan | Existing agent/skill/MCP scanner proof that category is real, plus gap baseline. |
| Snyk Agent Scan skill inspector | https://labs.snyk.io/resources/agent-scan-skill-inspector/ | Natural-language skill instructions plus code need joint scanning. |
| AgentAuditKit Marketplace | https://github.com/marketplace/actions/agentauditkit-mcp-security-scan | Direct competitor: MCP security scan GitHub Action with SARIF, rules, OWASP mapping, and compliance positioning. |
| SkillScan | https://skillscan.sh/ | Direct competitor: offline skill security analysis, SARIF/CI, linting, and behavior tracing claims. |
| Inkog | https://inkog.io/ | Direct/near-direct competitor: CLI and MCP-server workflow that scans, explains, and applies fixes in AI assistant flow. |
| AgentSeal | https://agentseal.org/ | Direct competitor: open-source AI-agent scanner covering prompts, MCP, skills, machine guard, CI/SARIF/JUnit, and BYOK runtime probes. |
| Firmis | https://firmislabs.com/ | Direct competitor: AI-agent scanner/platform with Deep Scan, Auto-Fix, Monitor, and large skill-scan research claims. |
| HackMyAgent | https://www.hackmyagent.com/ | Direct competitor: AI-agent toolkit with auto-fix, rollback, MCP/config/credential checks, and benchmark positioning. |
| MCPSafe | https://mcpsafe.org/ | MCP scanner and registry with AST scanning, trust scores, CI/CD, and remediation guidance. |
| Syntrix | https://syntrix.solutions/ | Agentic AI scanner for MCP servers/endpoints with risk score, OWASP mapping, remediation, and CI integration. |
| AgentOpsSec | https://agentopssec.com/ | Local-first OSS stack for agent security and observability, including MCP Doctor, firewall, radar, sandbox, review, and cost tools. |
| AgentGrade | https://agentgrade.net/watch/ | MCP/agent endpoint grading registry using passive HTTP checks and public security grades. |
| SkillAudit | https://skillaudit.vercel.app/ | Skill and MCP tool scanner with risk score, intent detection, capability fingerprinting, and low-cost deep scans. |
| SkillRisk | https://skillrisk.org/ | Direct competitor: local/browser MCP and agent-skill scanner with security score and remediation steps. |
| sinewaveai agent security scanner MCP | https://github.com/sinewaveai/agent-security-scanner-mcp | Direct competitor: MCP scanner server with SARIF and auto-fix claims. |
| TrustTrace | https://www.trusttrace.io/ | Direct/adjacent competitor: AI-agent security platform with MCP scan, compliance mapping, and remediation roadmap. |
| Panguard AI | https://www.panguard.ai/ | Direct/adjacent competitor: decentralized AI-agent security scanner with large skill-scan claims. |
| FaberLens Skill Scanner | https://faberlens.ai/explore/skill-scanner | Direct/adjacent competitor: skill behavioral safety and malware/spyware scanner. |
| Skill Audit MCP Market | https://mcpmarket.com/server/skill-audit | Direct competitor: static MCP/skill scanner with SARIF, GitHub Action, Docker, MCP server, hosted API, and pre-commit hook. |
| AI Supply Chain Security Scanner | https://mcpmarket.com/ko/tools/skills/ai-supply-chain-security-scanner | Adjacent competitor: AI-BOM, MCP infrastructure, SLSA provenance, and remediation-plan skill. |
| SafeSkills | https://safeskills.io/ | Direct competitor: MCP/AI skill upload scanner with access analysis, risk score, and remediation steps. |
| Backslash AI Agent Skills Scanner | https://skills.backslash.security/ | Direct/adjacent competitor: GitHub-hosted AI skill scanner and MCP supply-chain risk content. |
| AiSkillsGuard | https://www.aiskillsguard.com/ | Direct competitor: AI skill scanner using static pre-scan plus model reasoning for exfiltration, injection, permissions, and supply-chain risk. |
| SkillShield | https://skillshield.io/ | Direct competitor: security-scored AI skills and MCP server directory from Git URLs. |
| SkillTester | https://arxiv.org/abs/2603.28815 | Research competitor: agent skill utility/security benchmark and scoring framework. |
| SkillAttack | https://arxiv.org/abs/2604.04989 | Research evidence: automated red-teaming of agent skills shows scanner bypass risk. |
| SkillProbe | https://arxiv.org/abs/2603.21019 | Research competitor: multi-agent auditing for emerging skill marketplaces. |
| Promptfoo GitHub | https://github.com/promptfoo/promptfoo | Large OSS runtime eval/red-team competitor with CI/CD and agent/RAG testing scope. |
| Garak GitHub | https://github.com/NVIDIA/garak | Large OSS LLM vulnerability scanner competitor; broad probe library. |
| PyRIT GitHub | https://github.com/microsoft/PyRIT | Microsoft GenAI risk identification framework; scanner/GUI/framework competitor. |
| Giskard | https://www.giskard.ai/ | Agent evaluation and red-team platform; black-box testing competitor. |
| Inspect AI GitHub | https://github.com/UKGovernmentBEIS/inspect_ai | AI Security Institute eval framework; adjacent model/agent eval competitor. |
| LLM Guard | https://github.com/protectai/llm-guard | Input/output security toolkit with prompt, secret, PII, and safety scanners. |
| Guardrails AI | https://github.com/guardrails-ai/guardrails | Runtime guardrail/validation framework competitor. |
| Protect AI Rebuff | https://github.com/ProtectAI/rebuff | Prompt-injection detector competitor. |
| Protect AI ModelScan | https://github.com/protectai/modelscan | Adjacent model supply-chain scanner; useful analogy for pre-deployment AI artifact scanning. |
| GitHub Copilot Autofix announcement | https://github.blog/2024-03-20-found-means-fixed-introducing-code-scanning-autofix-powered-by-github-copilot-and-codeql/ | Remediation-first validation: code scanning autofix coverage and fix-rate claims. |
| GitHub Copilot Autofix speed results | https://github.blog/news-insights/product-news/secure-code-more-than-three-times-faster-with-copilot-autofix/ | Remediation-first validation: public-beta speed improvement claim. |
| Snyk Agent Fix docs | https://docs.snyk.io/scan-with-snyk/snyk-code/manage-code-vulnerabilities/fix-code-vulnerabilities-automatically | Adjacent remediation competitor: automated fixes for source-code issues. |
| Snyk Code | https://snyk.io/product/snyk-code/ | Snyk remediation positioning around find/prioritize/auto-fix. |
| Semgrep Assistant docs | https://dev2.semgrep.dev/docs/semgrep-assistant/overview | Adjacent remediation competitor: AI remediation guidance and autofix suggestions in PR/MR workflow. |
| Semgrep Autofix update | https://semgrep.dev/products/product-updates/accelerate-remediation-with-semgrep-autofix | Adjacent remediation competitor: contextual remediation and AI-generated PR fix suggestions. |
| Semgrep Assistant technical post | https://semgrep.dev/blog/2024/the-tech-behind-semgrep-assistant/ | Validation pattern: generated fixes checked by rerunning scanner. |
| OpenAI Codex | https://openai.com/codex/ | Codex positioning as coding agent that helps build and ship products. |
| Promptfoo red-team docs | https://www.promptfoo.dev/docs/red-team/quickstart/ | Open-source red-team tool; scans many runtime vulnerabilities and supports CI. |
| Garak docs | https://docs.garak.ai/ | LLM vulnerability scanner baseline. |
| Microsoft PyRIT blog | https://www.microsoft.com/en-us/security/blog/2024/02/22/announcing-microsofts-open-automation-framework-to-red-team-generative-ai-systems/ | Red-team orchestration baseline; strong but heavier than CI preflight scanner. |
| Meta Llama Guard paper | https://ai.meta.com/research/publications/llama-guard-llm-based-input-output-safeguard-for-human-ai-conversations/ | Runtime input/output classifier baseline. |
| NVIDIA NeMo Guardrails docs | https://docs.nvidia.com/nemo/microservices/latest/guardrails/index.html | Runtime guardrail baseline. |
| Lakera Guard docs | https://docs.lakera.ai/docs/api/guard | Hosted runtime screening baseline; docs also recommend offline batch document screening for static corpora. |
| Microsoft Presidio | https://microsoft.github.io/presidio/ | PII detection baseline, useful for RAG but not agent-specific. |
| Semgrep docs | https://semgrep.dev/docs/ | Generic SAST/SCA/secrets baseline. |
| PoisonedRAG paper | https://arxiv.org/abs/2402.07867 | RAG poisoning scale; few malicious texts can steer target answers. |
| PoisonedRAG repo | https://github.com/sleeepeer/PoisonedRAG | Reproducible RAG poisoning benchmark material. |
| Snyk IaC docs | https://docs.snyk.io/scan-with-snyk/snyk-iac | Infra competitor: IaC security scanning before and after deployment with fix advice. |
| Snyk drift management | https://snyk.io/product/infrastructure-as-code-security/drift-management/ | Infra competitor: drift and unmanaged resource detection. |
| Checkov GitHub | https://github.com/bridgecrewio/checkov | Infra competitor: broad IaC scanning, Terraform plan support, SARIF output, remediation guides. |
| Trivy GitHub | https://github.com/aquasecurity/trivy | Infra competitor: broad security scanner including IaC misconfigurations, secrets, containers, Kubernetes, SBOM. |
| KICS GitHub | https://github.com/Checkmarx/kics | Infra competitor: IaC vulnerabilities, compliance issues, infrastructure misconfigurations. |
| Terrascan GitHub | https://github.com/tenable/terrascan | Infra competitor: IaC compliance/static scanning; archived but still relevant historically. |
| HCP Terraform drift detection | https://developer.hashicorp.com/terraform/tutorials/cloud/drift-detection | Infra competitor: Terraform-native drift/health assessment workflow. |
| Spacelift drift detection | https://docs.spacelift.io/self-hosted/latest/concepts/stack/drift-detection | Infra competitor: IaC platform drift detection and reconciliation. |
| env0 drift cause | https://docs.env0.com/docs/drift-cause | Infra competitor: drift cause analysis for Terraform/Terragrunt/OpenTofu environments. |
| Firefly drift detection | https://docs.firefly.ai/key-features/drift-detection | Infra competitor: drift detection/remediation and unmanaged-resource IaC generation. |
| Scalr drift detector | https://docs.scalr.io/docs/drift-detector | Infra competitor: Terraform/OpenTofu drift detection and notifications. |
| Infracost GitHub | https://github.com/infracost/infracost | Adjacent infra competitor: PR-native cloud cost intelligence for IaC. |
| DriftHound | https://drifthound.io/ | Infra competitor: open-source Terraform/OpenTofu/Terragrunt drift detection and monitoring. |
| DevPlus | https://devplus.io/ | Infra competitor: AI agents for drift, cost, capacity, and autonomous remediation workflows. |
| ThreatMitigator | https://threatmitigator.app/ | Infra competitor: AI-powered IaC threat modeling, drift detection, and optional remediation. |
| Gomboc Community | https://www.gomboc.ai/gomboc-community | Infra competitor: deterministic Terraform scanning and remediation engine packaged for individual adoption. |
| Gomboc ORL | https://www.gomboc.ai/blog/gomboc-expands-beyond-iac-with-orl-to-deliver-deterministic-remediation-cloud-and-code | Infra competitor: deterministic remediation language across cloud config, IaC, code, and dependencies. |
| DriftOps | https://driftops.dev/ | Infra competitor: AI-powered compliance/drift PR reports with Terraform fix instructions. |
| Kestrel AI GitLab IaC integration | https://usekestrel.ai/changelog/gitlab-iac-integration | Infra competitor: AI copilot reading live cloud and Terraform code, then opening remediation PRs. |
