from __future__ import annotations

import hashlib
import json

from agentpreflight.models import ScanResult

_SECURITY_SEVERITY = {
    'critical': '9.0',
    'high': '7.0',
    'medium': '5.0',
    'low': '3.0',
}

_LEVELS = {
    "critical": "error",
    "high": "error",
    "medium": "warning",
    "low": "note",
}


def _partial_fingerprint(finding: "Finding") -> str:
    """Generate stable fingerprint for SARIF result dedup."""
    snippet = finding._get_snippet()
    rel_path = finding._get_relative_path()
    key = f"{finding.id}|{snippet}|{rel_path}"
    return hashlib.sha256(key.encode('utf-8')).hexdigest()


def _security_severity(severity: str) -> str:
    """Map finding severity to security-severity string."""
    return _SECURITY_SEVERITY.get(severity, '3.0')


def render(result: ScanResult) -> str:
    rules = {}
    rule_index = {}
    sarif_results = []
    for finding in result.findings:
        rule_key = finding.id
        if rule_key not in rules:
            rules[rule_key] = {
                "id": finding.id,
                "name": finding.title,
                "shortDescription": {"text": finding.title},
                "fullDescription": {"text": finding.risk},
                "help": {"text": finding.fix},
                "properties": {
                    "severity": finding.severity,
                    "category": finding.category,
                    "security-severity": _security_severity(finding.severity),
                },
            }
            rule_index[rule_key] = len(rules) - 1
        region = {"startLine": finding.line or 1}
        if finding.column:
            region["startColumn"] = finding.column
        sarif_results.append({
            "ruleId": finding.id,
            "ruleIndex": rule_index.get(finding.id, -1),
            "partialFingerprints": {"apPrimary/v1": _partial_fingerprint(finding)},
            "level": _LEVELS.get(finding.severity, "warning"),
            "message": {"text": finding.evidence},
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {"uri": finding.path.replace("\\", "/")},
                    "region": region,
                }
            }],
        })

    # Add ruleIndex to each rule for proper reference
    for rule_id, idx in rule_index.items():
        rules[rule_id]["ruleIndex"] = idx

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
