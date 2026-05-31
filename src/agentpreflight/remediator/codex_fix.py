from __future__ import annotations

import os
from dataclasses import dataclass

from agentpreflight.models import Finding
from agentpreflight.remediator.prompt_builder import SYSTEM_PROMPT, _prompt_for_finding, _redact


@dataclass
class CodexPatch:
    finding_id: str
    path: str
    line: int | None
    proposed: str


def run_codex_fix(
    findings: list[Finding],
    allowed: set[str] | None = None,
    max_findings: int = 5,
    model: str = "codex-mini-latest",
) -> list[CodexPatch]:
    """Call OpenAI Codex to generate security patches for flagged findings.

    Requires: pip install 'mcp-agent-preflight-sec[codex]'
    Requires: OPENAI_API_KEY env var
    Only sends redacted code snippets — no secrets, no repo context.
    """
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise ImportError(
            "openai package required. Install: pip install 'mcp-agent-preflight-sec[codex]'"
        ) from exc

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")

    client = OpenAI(api_key=api_key)
    fixable = [f for f in findings if f.fix_available and (not allowed or f.id in allowed)][:max_findings]

    patches: list[CodexPatch] = []
    for finding in fixable:
        user_msg = _prompt_for_finding(finding)
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            max_tokens=512,
            temperature=0,
        )
        raw = response.choices[0].message.content or ""
        patches.append(CodexPatch(
            finding_id=finding.id,
            path=finding.path,
            line=finding.line,
            proposed=_redact(raw.strip()),
        ))

    return patches
