from __future__ import annotations

import json
from pathlib import Path

from agentpreflight import __version__
from agentpreflight.models import ScanResult

_LEVELS = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
}


def _relative_uri(path: str, target_root: str) -> str:
    """Return a POSIX-style relative URI for SARIF artifactLocation."""
    try:
        return Path(path).resolve().relative_to(Path(target_root).resolve()).as_posix()
    except ValueError:
        return Path(path).name


def render(result: ScanResult) -> str:
    rules = {}
    sarif_results = []
    for finding in result.findings:
        rules.setdefault(finding.id, {
            "id": finding.id,
            "name": finding.title,
            "shortDescription": {"text": finding.title},
            "fullDescription": {"text": finding.risk},
            "help": {"text": finding.fix},
            "properties": {"severity": finding.severity, "category": finding.category},
        })
        region = {"startLine": finding.line or 1}
        if finding.column:
            region["startColumn"] = finding.column
        sarif_results.append({
            "ruleId": finding.id,
            "level": _LEVELS.get(finding.severity, "warning"),
            "message": {"text": finding.evidence},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": _relative_uri(finding.path, result.target)},
                    "region": region,
                }
            }],
        })

    doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {
                "driver": {
                    "name": result.tool,
                    "semanticVersion": __version__,
                    "rules": list(rules.values()),
                }
            },
            "results": sarif_results,
            "properties": {
                "trustScore": result.trust_score,
                "verdict": result.verdict,
                "profile": result.profile,
            },
        }],
    }
    return json.dumps(doc, indent=2)
