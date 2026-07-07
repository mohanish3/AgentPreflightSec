"""Tests for SARIF reporter with partialFingerprints and security-severity."""
import json

from agentpreflight.models import Finding, ScanResult
from agentpreflight.reporters.sarif_reporter import render


def test_sarif_has_partial_fingerprints():
    """Test that each SARIF result has a non-empty partialFingerprints value."""
    finding = Finding(
        id="test-rule-1",
        severity="high",
        category="security",
        title="Test vulnerability",
        path="/repo/src/app.py",
        evidence="Some code here",
        risk="High risk",
        fix="Fix this",
    )
    result = ScanResult(
        target="test-target",
        profile="test-profile",
        trust_score=85,
        verdict="warn",
        findings=[finding],
        summary={},
    )
    sarif_json = render(result)
    doc = json.loads(sarif_json)
    assert "runs" in doc, "SARIF document must have 'runs' key"
    assert "results" in doc["runs"][0], "Run must have 'results' key"
    assert len(doc["runs"][0]["results"]) == 1
    sarif_result = doc["runs"][0]["results"][0]
    assert "partialFingerprints" in sarif_result
    assert len(sarif_result["partialFingerprints"]) > 0
    fingerprint = list(sarif_result["partialFingerprints"].values())[0]
    assert len(fingerprint) == 64, "SHA256 hash should be 64 hex chars"


def test_sarif_fingerprints_are_stable():
    """Test that identical findings produce identical fingerprints across runs."""
    finding = Finding(
        id="stable-rule",
        severity="medium",
        category="performance",
        title="Slow query",
        path="/repo/src/db.py",
        evidence="SELECT * FROM users",
        risk="Performance impact",
        fix="Index the column",
    )
    result1 = ScanResult(
        target="test",
        profile="test",
        trust_score=90,
        verdict="pass",
        findings=[finding],
        summary={},
    )
    result2 = ScanResult(
        target="test",
        profile="test",
        trust_score=90,
        verdict="pass",
        findings=[finding],
        summary={},
    )
    doc1 = json.loads(render(result1))
    doc2 = json.loads(render(result2))
    fingerprint1 = doc1["runs"][0]["results"][0]["partialFingerprints"]["apPrimary/v1"]
    fingerprint2 = doc2["runs"][0]["results"][0]["partialFingerprints"]["apPrimary/v1"]
    assert fingerprint1 == fingerprint2, "Identical findings must produce identical fingerprints"


def test_sarif_has_security_severity():
    """Test that each reporting rule has a security-severity property."""
    critical_finding = Finding(
        id="critical-rule",
        severity="critical",
        category="security",
        title="Critical vuln",
        path="/repo/src/critical.py",
        evidence="Critical code",
        risk="Critical risk",
        fix="Fix critical",
    )
    high_finding = Finding(
        id="high-rule",
        severity="high",
        category="security",
        title="High vuln",
        path="/repo/src/high.py",
        evidence="High code",
        risk="High risk",
        fix="Fix high",
    )
    medium_finding = Finding(
        id="medium-rule",
        severity="medium",
        category="security",
        title="Medium vuln",
        path="/repo/src/medium.py",
        evidence="Medium code",
        risk="Medium risk",
        fix="Fix medium",
    )
    low_finding = Finding(
        id="low-rule",
        severity="low",
        category="security",
        title="Low vuln",
        path="/repo/src/low.py",
        evidence="Low code",
        risk="Low risk",
        fix="Fix low",
    )
    result = ScanResult(
        target="test",
        profile="test",
        trust_score=100,
        verdict="pass",
        findings=[critical_finding, high_finding, medium_finding, low_finding],
        summary={},
    )
    doc = json.loads(render(result))
    rules_map = {r["id"]: r for r in doc["runs"][0]["tool"]["driver"]["rules"]}
    
    # Check security-severity for each rule
    assert rules_map["critical-rule"]["properties"]["security-severity"] == "9.0"
    assert rules_map["high-rule"]["properties"]["security-severity"] == "7.0"
    assert rules_map["medium-rule"]["properties"]["security-severity"] == "5.0"
    assert rules_map["low-rule"]["properties"]["security-severity"] == "3.0"
    
    # Verify required top-level keys
    assert "version" in doc
    assert "runs" in doc


def test_sarif_rule_index_bookkeeping():
    """Test that ruleIndex is properly assigned for each result."""
    finding1 = Finding(
        id="rule-a",
        severity="high",
        category="security",
        title="Rule A",
        path="/repo/src/a.py",
        evidence="Evidence A",
        risk="Risk A",
        fix="Fix A",
    )
    finding2 = Finding(
        id="rule-b",
        severity="critical",
        category="security",
        title="Rule B",
        path="/repo/src/b.py",
        evidence="Evidence B",
        risk="Risk B",
        fix="Fix B",
    )
    result = ScanResult(
        target="test",
        profile="test",
        trust_score=80,
        verdict="warn",
        findings=[finding1, finding2],
        summary={},
    )
    doc = json.loads(render(result))
    rules_map = {r["id"]: r for r in doc["runs"][0]["tool"]["driver"]["rules"]}
    
    # Check ruleIndex matches rule position
    assert rules_map["rule-a"]["ruleIndex"] == 0
    assert rules_map["rule-b"]["ruleIndex"] == 1
    
    # Results should have correct ruleIndex
    result_a = next(r for r in doc["runs"][0]["results"] if r["ruleId"] == "rule-a")
    result_b = next(r for r in doc["runs"][0]["results"] if r["ruleId"] == "rule-b")
    assert result_a["ruleIndex"] == 0
    assert result_b["ruleIndex"] == 1
