# User Stories & Acceptance Criteria

This document lists the user stories and clear acceptance criteria for **AgentPreflight**.

---

## Story 1: The Local Extension Developer

> **As an** AI Developer,  
> **I want to** scan my local MCP servers and agent skill folders during active coding,  
> **So that** I can detect security bugs (like hardcoded keys, unsafe command executions, or prompt overrides) before committing.

### Acceptance Criteria:
- **AC 1.1**: The scan runs locally in under **10 seconds** on standard extension folders.
- **AC 1.2**: The output is printed in a clean, color-coded CLI dashboard showing severity, rule violation, and line numbers.
- **AC 1.3**: The developer can suppress benign warnings locally using inline comment annotations (e.g. `# agentpreflight:disable-line AP-RULE`).
- **AC 1.4**: The developer can run `agentpreflight fix <path> --apply` to apply deterministic local sanitizations for flagged files, then rescan to verify.

---

## Story 2: The AppSec Engineer (CI/CD Gates)

> **As an** Application Security Engineer,  
> **I want to** integrate security gates into our GitHub Pull Request workflows,  
> **So that** we can automatically block compromised or non-compliant extensions from merging into production.

### Acceptance Criteria:
- **AC 2.1**: The CLI returns a non-zero exit code (`exit 1`) when a scan triggers violations matching the configured threshold (e.g. `--fail-on high`).
- **AC 2.2**: The scanner can export reports in standard **SARIF** format to integrate directly with GitHub Code Scanning.
- **AC 2.3**: A pre-built GitHub Action automatically comments on PRs with a simple Markdown scorecard and finding summaries.

---

## Story 3: The Hackathon Judge

> **As a** Hackathon Judge,  
> **I want to** view a clear, reproducible demonstration of AgentPreflight catching a poisoned extension and Codex repairing it,  
> **So that** I can verify the utility, Codex synergy, and technical completeness of the product.

### Acceptance Criteria:
- **AC 3.1**: The codebase contains pre-built mock fixtures representing a poisoned agent (positive test case) and a clean agent (negative test case).
- **AC 3.2**: A single command runs the scan on the poisoned fixture and fails, displaying a low **Trust Score**.
- **AC 3.3**: The fix command applies deterministic local patches (`agentpreflight fix demo/poisoned --apply`), instantly modifying the manifest and Python scripts.
- **AC 3.4**: A second scan command runs successfully, returning a **100/100 Trust Score**.
