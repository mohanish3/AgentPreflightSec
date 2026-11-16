from __future__ import annotations

import json
import shutil
from pathlib import Path

from agentpreflight.reporters import markdown_reporter
from agentpreflight.scanner import scan_path

ROOT = Path(__file__).resolve().parents[1]


def test_suppression_file_filters_matching_findings(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    suppression_file = target / ".agentpreflight.json"
    suppression_file.write_text(
        json.dumps({
            "suppressions": [
                {
                    "rule": "AP-SEC-003",
                    "path": ".env",
                    "reason": "demo fixture keeps env file intentionally",
                }
            ]
        }),
        encoding="utf-8",
    )

    result = scan_path(target, profile="strict")

    assert result.summary["suppressed"] == 1
    assert all(finding.id != "AP-SEC-003" for finding in result.findings)


def test_expired_suppression_does_not_filter(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    suppression_file = target / ".agentpreflight.json"
    suppression_file.write_text(
        json.dumps({
            "suppressions": [
                {
                    "rule": "AP-SEC-003",
                    "path": ".env",
                    "reason": "expired exception",
                    "owner": "appsec",
                    "expires": "2000-01-01",
                }
            ]
        }),
        encoding="utf-8",
    )

    result = scan_path(target, profile="strict")

    assert result.summary["suppressed"] == 0
    assert any(finding.id == "AP-SEC-003" for finding in result.findings)


def test_inline_disable_line_suppresses_matching_rule(tmp_path: Path) -> None:
    target = tmp_path / "inline"
    target.mkdir()
    (target / "tool.py").write_text(
        'import os\nos.system("echo unsafe")  # agentpreflight:disable-line AP-CODE-001 accepted fixture risk\n',
        encoding="utf-8",
    )

    result = scan_path(target, profile="strict")

    assert result.summary["suppressed"] == 1
    assert result.findings == []


def test_inline_disable_next_line_suppresses_matching_rule(tmp_path: Path) -> None:
    target = tmp_path / "inline-next"
    target.mkdir()
    (target / "tool.py").write_text(
        'import os\n# agentpreflight:disable-next-line AP-CODE-001 accepted fixture risk\nos.system("echo unsafe")\n',
        encoding="utf-8",
    )

    result = scan_path(target, profile="strict")

    assert result.summary["suppressed"] == 1
    assert result.findings == []


def test_markdown_reporter_outputs_pr_scorecard() -> None:
    result = scan_path(ROOT / "demo" / "poisoned", profile="strict")
    markdown = markdown_reporter.render(result)

    assert "AgentPreflight Scan Scorecard" in markdown
    assert "| Target | Verdict | Trust score | Findings |" in markdown
    assert "`AP-MCP-001`" in markdown


def test_apply_suppressions_returns_expired_suppressions(tmp_path: Path) -> None:
    from agentpreflight.suppressions import Suppression, apply_suppressions
    from agentpreflight.models import Finding
    
    suppression = Suppression(rule="AP-SEC-001", path="*.py", expires="2000-01-01")
    finding = Finding(
        id="AP-SEC-001",
        severity="high",
        category="security",
        title="Test Finding",
        path="test.py",
        evidence="test",
        risk="risk",
        fix="fix",
    )
    
    kept, suppressed, expired = apply_suppressions([finding], [suppression], tmp_path)
    
    assert expired == [suppression]
    assert finding in kept


def test_apply_suppressions_returns_no_expired_for_valid_date(tmp_path: Path) -> None:
    from agentpreflight.suppressions import Suppression, apply_suppressions
    from agentpreflight.models import Finding
    
    suppression = Suppression(rule="AP-SEC-001", path="*.py", expires="2030-01-01")
    finding = Finding(
        id="AP-SEC-001",
        severity="high",
        category="security",
        title="Test Finding",
        path="test.py",
        evidence="test",
        risk="risk",
        fix="fix",
    )
    
    kept, suppressed, expired = apply_suppressions([finding], [suppression], tmp_path)
    
    assert len(expired) == 0
    assert finding not in kept


def test_scan_result_includes_expired_suppressions(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    suppression_file = target / ".agentpreflight.json"
    suppression_file.write_text(
        json.dumps({
            "suppressions": [
                {
                    "rule": "AP-SEC-003",
                    "path": ".env",
                    "reason": "expired exception",
                    "owner": "appsec",
                    "expires": "2000-01-01",
                }
            ]
        }),
        encoding="utf-8",
    )

    result = scan_path(target, profile="strict")

    assert len(result.expired_suppressions) == 1
    assert result.expired_suppressions[0].expires == "2000-01-01"
    assert result.expired_suppressions[0].rule == "AP-SEC-003"
