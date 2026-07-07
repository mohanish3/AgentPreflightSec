"""Baseline module for diff-based scanning - only fail on new findings."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _make_fingerprint(finding: dict[str, Any]) -> str:
    """Create a stable fingerprint for a finding to detect duplicates across scans.
    
    Fingerprint combines key identifying fields so that the same finding in the same
    file at the same line is detected as a duplicate, even if evidence text changes.
    """
    parts = [
        finding.get("id", ""),
        finding.get("path", ""),
        str(finding.get("line", "")),
        finding.get("category", ""),
        finding.get("severity", ""),
    ]
    return "|".join(parts)


def load_baseline(path: str | Path) -> dict[str, dict[str, Any]]:
    """Load a baseline findings file and return a dict keyed by fingerprint."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Baseline file not found: {path}")
    
    data = path.read_text(encoding="utf-8")
    if not data.strip():
        return {}
    
    findings = []
    try:
        findings = json.loads(data)
        if isinstance(findings, list):
            findings = [f for f in findings if isinstance(f, dict)]
        elif isinstance(findings, dict):
            findings = findings.get("findings", [])
            if not isinstance(findings, list):
                findings = []
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in baseline file: {e}")
    
    fingerprints = {}
    for finding in findings:
        if isinstance(finding, dict):
            fp = _make_fingerprint(finding)
            fingerprints[fp] = finding
    
    return fingerprints


def get_new_findings(current: list[dict[str, Any]], baseline: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Filter current findings to only those not present in the baseline.
    
    Args:
        current: List of current findings from a scan
        baseline: Dict of baseline findings keyed by fingerprint
    
    Returns:
        List of findings that are new (not in baseline)
    """
    baseline_fingerprints = set(baseline.keys())
    new = []
    
    for finding in current:
        if isinstance(finding, dict):
            fp = _make_fingerprint(finding)
            if fp not in baseline_fingerprints:
                new.append(finding)
    
    return new


def get_baseline_summary(baseline: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """Generate a summary of baseline findings for reporting."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
    paths = set()
    
    for finding in baseline.values():
        severity = finding.get("severity", "low")
        if severity in counts:
            counts[severity] += 1
        paths.add(finding.get("path", ""))
    
    return {
        "total": len(baseline),
        "by_severity": counts,
        "unique_paths": len(paths),
    }
