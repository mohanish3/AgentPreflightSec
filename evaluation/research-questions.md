# Research Questions: Preflight Scanner Engineering

This document outlines the core technical research questions guiding the design, execution, and verification of **AgentPreflight**.

---

## 1. Static Metadata Analysis & Tool Poisoning
- *Question*: How can we statically distinguish benign, highly descriptive tool descriptions from adversarial prompt-injection overrides without calling external APIs on every scan?
- *Approach*: Map a local dictionary of high-risk imperative phrases ("ignore", "override", "system directive") and combine with semantic layout checks.

## 2. Unicode Obfuscation & Smuggling Patterns
- *Question*: What are the most prevalent zero-width and homoglyph smuggling patterns observed in compromised third-party repository skills?
- *Approach*: Normalize Markdown files to NFKC Unicode representation and check for character ranges representing control codes, zero-width joiners, and Cyrillic/Latin lookalikes.

## 3. High-Performance AST Analysis
- *Question*: How can we parse Python and TypeScript AST structures to detect command injections while maintaining a sub-second developer CLI execution loop?
- *Approach*: Implement lightweight, targeted regex checks for broad indicators and trigger quick AST/Tree-Sitter parsing only on identified candidate files.

## 4. Codex Remediation Patch Integrity
- *Question*: What prompt structure guarantees that OpenAI Codex will consistently generate safe, compilable, and exact replacement diffs for flagged configs and scripts?
- *Approach*: Build constrained prompt templates that supply Codex with only the targeted finding context and demand a pure JSON/diff patch, avoiding syntax overhead.

## 5. Compositional Flow Mapping
- *Question*: How can we map the connections between tools to identify "toxic source-to-sink flows" (e.g. read_email connected directly to post_request) statically?
- *Approach*: Model the MCP manifests as a structural graph, evaluating capability bindings and flag connections that cross boundaries without user validation.
