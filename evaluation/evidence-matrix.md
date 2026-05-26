# Evidence Matrix: Research to Rule Mapping

This document maps primary academic research, security benchmarks, and vulnerability data directly to **AgentPreflight's** core rule families.

---

## Mapping Matrix

| Rule Family | Key Evidence Source | Core Statistics & Findings | Specific Vuln / Exploit Pattern |
|---|---|---|---|
| **`tool_poisoning`** | *MCPTox* & *InjecAgent* | 72.8% attack success rate on real MCP servers using poisoned descriptions; refusers below 3%. | Indirect prompt injection injected into tool description strings to override user instructions. |
| **`unicode_smuggling`** | *OWASP Agentic Skills Top 10* | 76+ confirmed malicious payloads using zero-width / homoglyph smuggler characters. | Using invisible zero-width spaces or Russian homoglyphs to hide commands from developers. |
| **`unsafe_exec`** | *Snyk ToxicSkills* | 13.4% of 3,984 scanned skills contain critical flaws, with arbitrary command executions. | Unsafe script execution patterns: `os.system()`, `subprocess.Popen(shell=True)`, `eval()`, `exec()`. |
| **`remote_instruction_fetch`** | *Snyk ToxicSkills* | Dynamic script downloading and dynamic imports bypass static code check boundaries. | Scripts dynamically reading remote URLs (`urllib`, `requests`) or importing dynamic code to run commands. |
| **`transport_security`** | *OWASP MCP Security Guide* | MCP servers binding to broad addresses or exposing unauthenticated local communication channels. | Configs allowing unauthenticated local loopback bindings (`127.0.0.1`), exposing tools to DNS rebinding. |
| **`secrets`** | *Snyk ToxicSkills* | High percentage of custom repos leaking live credentials and API keys in source code. | Hardcoded tokens (`sk-...`), private keys, or environment files (`.env`) checked directly into the repo. |
| **`least_privilege`** | *OWASP LLM Top 10* | Over-broad tool scopes enable agents to execute high-severity deletions or transfers. | MCP servers requesting root directory file access or wildcard execution permissions. |
