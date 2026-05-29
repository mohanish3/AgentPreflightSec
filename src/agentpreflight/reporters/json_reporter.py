from __future__ import annotations
import json
from agentpreflight import __version__
from agentpreflight.models import ScanResult


def render(result: ScanResult) -> str:
    findings_out = []
    for f in result.findings:
        entry: dict = {
            "id": f.id,
            "severity": f.severity,
            "category": f.category,
            "title": f.title,
            "path": f.path,
            "evidence": f.evidence,
            "risk": f.risk,
            "fix": f.fix,
            "fix_available": f.fix_available,
        }
        if f.line is not None:
            entry["line"] = f.line
        if f.column is not None:
            entry["column"] = f.column
        if f.end_line is not None:
            entry["end_line"] = f.end_line
        if f.references:
            entry["references"] = f.references
        if f.snippet_hash is not None:
            entry["snippet_hash"] = f.snippet_hash
        if f.fix_mode is not None:
            entry["fix_mode"] = f.fix_mode
        if f.patch_preview is not None:
            entry["patch_preview"] = f.patch_preview
        findings_out.append(entry)

    score_block = None
    if result.score is not None:
        score_block = {
            "base": result.score.base,
            "deductions": result.score.deductions,
            "caps_applied": result.score.caps_applied,
            "final": result.score.final,
        }

    out = {
        "schema_version": result.schema_version,
        "tool": result.tool,
        "tool_version": __version__,
        "target": result.target,
        "profile": result.profile,
        "offline": result.offline,
        "trust_score": result.trust_score,
        "verdict": result.verdict,
        "summary": result.summary,
        "findings": findings_out,
    }
    if score_block is not None:
        out["score"] = score_block

    return json.dumps(out, indent=2)
