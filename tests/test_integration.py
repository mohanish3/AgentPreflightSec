"""Integration tests: full scan_path() on demo fixtures."""
from __future__ import annotations

from pathlib import Path

import pytest

from agentpreflight.scanner import scan_path

REPO_ROOT = Path(__file__).parent.parent
POISONED = REPO_ROOT / "demo" / "poisoned"
CLEAN = REPO_ROOT / "demo" / "clean"


@pytest.mark.skipif(not POISONED.exists(), reason="demo/poisoned fixture missing")
def test_poisoned_repo_fails() -> None:
    result = scan_path(POISONED, profile="strict")
    assert result.verdict == "fail"
    assert result.trust_score < 70
    assert len(result.findings) > 0
    severities = {f.severity for f in result.findings}
    assert "critical" in severities or "high" in severities


@pytest.mark.skipif(not CLEAN.exists(), reason="demo/clean fixture missing")
def test_clean_repo_passes() -> None:
    result = scan_path(CLEAN, profile="balanced")
    assert result.verdict in {"pass", "warn"}
    assert result.trust_score >= 70


def test_scan_result_has_required_fields() -> None:
    if not POISONED.exists():
        pytest.skip("demo/poisoned fixture missing")
    result = scan_path(POISONED, profile="balanced")
    assert result.tool == "AgentPreflight"
    assert result.schema_version == "1.0"
    assert result.offline is True
    assert result.score is not None
    assert result.score.base == 100
    assert isinstance(result.summary["artifacts_scanned"], int)


def test_scan_single_file() -> None:
    fixture = POISONED / "server.py"
    if not fixture.exists():
        pytest.skip("demo/poisoned/server.py missing")
    result = scan_path(fixture, profile="strict")
    assert result.target == str(fixture.resolve())
    assert len(result.findings) >= 0


def test_json_output_is_valid() -> None:
    import json
    from agentpreflight.reporters import json_reporter
    if not POISONED.exists():
        pytest.skip("demo/poisoned fixture missing")
    result = scan_path(POISONED, profile="balanced")
    rendered = json_reporter.render(result)
    data = json.loads(rendered)
    assert "trust_score" in data
    assert "findings" in data
    assert "verdict" in data


def test_sarif_output_has_required_schema() -> None:
    import json
    from agentpreflight.reporters import sarif_reporter
    if not POISONED.exists():
        pytest.skip("demo/poisoned fixture missing")
    result = scan_path(POISONED, profile="balanced")
    rendered = sarif_reporter.render(result)
    data = json.loads(rendered)
    assert data["version"] == "2.1.0"
    assert "$schema" in data
    assert "runs" in data


def test_strict_profile_scores_lower_than_dev() -> None:
    if not POISONED.exists():
        pytest.skip("demo/poisoned fixture missing")
    strict = scan_path(POISONED, profile="strict")
    dev = scan_path(POISONED, profile="dev")
    assert strict.trust_score <= dev.trust_score


def test_suppression_reduces_finding_count(tmp_path) -> None:
    import json
    from agentpreflight.scanner import scan_path as _scan
    if not POISONED.exists():
        pytest.skip("demo/poisoned fixture missing")
    baseline = _scan(POISONED, profile="balanced")
    if not baseline.findings:
        pytest.skip("no findings to suppress")
    first = baseline.findings[0]
    sup_file = tmp_path / ".agentpreflight.json"
    sup_file.write_text(json.dumps({
        "suppressions": [{"rule": first.id, "path": "*", "reason": "test suppression"}]
    }), encoding="utf-8")
    suppressed = _scan(POISONED, profile="balanced", suppression_file=sup_file)
    assert suppressed.summary["suppressed"] >= 1
    assert len(suppressed.findings) < len(baseline.findings)
