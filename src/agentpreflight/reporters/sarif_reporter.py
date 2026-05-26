from __future__ import annotations

import json

from agentpreflight.models import ScanResult

_LEVELS = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
}


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
                    "artifactLocation": {"uri": finding.path.replace("\\", "/")},
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
                    "semanticVersion": "0.1.0",
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
