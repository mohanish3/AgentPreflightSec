# Scoring Rubric: Candidate Evaluation Method

This document defines the evaluation methodology used to score and rank candidate problem statements for the Outskill x OpenAI Codex Hackathon.

---

## 7 Core Evaluation Axes

We grade each candidate on a scale of **1 to 5** across exactly seven dimensions:

### 1. OpenAI Codex Leverage
- **1 Point**: Zero synergy; the product does not integrate or benefit from Codex.
- **3 Points**: Moderate synergy; Codex can be used to generate initial configurations.
- **5 Points**: Maximum synergy; Codex forms a key runtime or remediation loop in the product itself.

### 2. 4-Day Build Speed & Delivery Certainty
- **1 Point**: Extremely risky; relies on complex platform setups (like heavy kernel extensions or hypervisors).
- **3 Points**: Moderate risk; requires complex file parsers or multiple external integrations.
- **5 Points**: Extremely high build certainty; offline-first, local static file parsing with straightforward logic.

### 3. Developer Utility & Adoption Friction
- **1 Point**: Intrusive or high friction; adds heavy build times or requires code rewrite.
- **3 Points**: Moderate utility; helpful for isolated audits but lacks automated CI gates.
- **5 Points**: High utility; fast, sub-second pre-commit/PR linter with immediate value and clear action paths.

### 4. Market Space Vacancy (Gaps vs Snyk)
- **1 Point**: Highly occupied; free, mature OSS tools (like Snyk Agent Scan) already completely cover the space.
- **3 Points**: Moderately occupied; some commercial or platform options exist, but gaps remain.
- **5 Points**: Completely vacant; no existing pre-deployment tooling addresses this specific problem.

### 5. Aesthetics & Demo Wow Factor
- **1 Point**: Low visibility; plain text logs with no visual feedback.
- **3 Points**: Moderate visibility; standard console output with basic warnings.
- **5 Points**: High wow factor; beautiful terminal dashboards, detailed trust scoring, and automated Codex diff-patches.

### 6. Token & Compute Cost Efficiency
- **1 Point**: Extremely expensive; calls LLM APIs on every single line of code or user request.
- **3 Points**: Moderate cost; uses API calls for primary parsing but has basic local caching.
- **5 Points**: Zero or near-zero token cost; runs deterministic local rules, utilizing APIs only on high-severity triage.

### 7. Absolute Uniqueness & Winner Potential
- **1 Point**: Standard utility tool with no competitive edge.
- **3 Points**: Strong utility but unlikely to capture judges' attention.
- **5 Points**: Killer feature; first-mover advantage on a critical, emerging security standard.
