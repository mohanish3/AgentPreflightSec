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
