# Remediation-First Security: AgentPreflight vs. Snyk

This document conducts a deep dive analysis into our core technical differentiator: **Remediation-First Security**. We contrast **AgentPreflight's** Codex-driven auto-patching loop against **Snyk Agent Scan's** detection-only approach.

---

## The Core Limitation of Snyk Agent Scan (Detection-Only)

Snyk Agent Scan is a valuable baseline tool that validates the need for pre-deployment agent extension scanning. However, like most traditional AppSec tools, it follows a **detection-only** paradigm:
1. **Analysis**: Statically checks skill files or configurations for issues.
2. **Output**: Generates a long log of violations.
3. **Friction**: Stops there, leaving the developer to figure out *how* to rewrite complex model-facing tool descriptions or replace dangerous subprocess calls without breaking the skill.

For AI developers shipping code in fast-paced environments, detection without remediation leads to **security fatigue** and skipped checks.

---

## The AgentPreflight Remediation Loop (10X Better)

AgentPreflight redefines developer security by integrating a **Codex-Assisted Remediation Loop** directly into the scanner. We do not just find bugs; we repair them.

```
  ┌──────────────────────────────────────────────────────────┐
  │              THE AGENTPREFLIGHT REMEDIATION LOOP         │
  └────────────────────────────┬─────────────────────────────┘
                               │
                [ 1. Scan finds vulnerability ]
                               │
               [ 2. Redact proprietary context ]
                               │
             [ 3. Send snippet to OpenAI Codex ]
                               │
         [ 4. Codex generates safe, compilable patch ]
                               │
             [ 5. Developer reviews & applies patch ]
                               │
                [ 6. Rescan yields higher score! ]
```

### Key Differentiators:
1. **Context Redaction**: Before sending any flagged code snippet to the OpenAI Codex API, AgentPreflight redacts all local paths, custom variables, and proprietary strings. The model only sees the raw vulnerability pattern, ensuring **100% data privacy**.
2. **Compilable Patches**: Codex generates direct unified diffs. The developer runs a single command to apply the patch instantly:
   ```bash
   agentpreflight fix --rule MCP-PI-001
   ```
3. **Interactive Rescan**: Once applied, the scanner automatically re-runs the checks locally, verifying the fix and updating the **Trust Score** instantly.

---

## Business & Developer Value

- **Time Saved**: Slashes the time required to research, rewrite, and verify prompt-injections or dangerous python calls from **hours to seconds**.
- **Higher Compliance**: Makes security compliance the path of least resistance for developers, as they can remediate issues with a single keystroke.
- **Developer Personal Leverage**: Active AI builders using Codex have direct day-to-day utility from an automated Codex-driven security repair tool.
