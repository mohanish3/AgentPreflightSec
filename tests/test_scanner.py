from __future__ import annotations

import json
import shutil
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import _should_fail, app
from agentpreflight.models import Finding
from agentpreflight.reporters import json_reporter, sarif_reporter
from agentpreflight.scanner import scan_path

ROOT = Path(__file__).resolve().parents[1]


def test_poisoned_demo_fails_with_expected_rules() -> None:
    result = scan_path(ROOT / "demo" / "poisoned", profile="strict")
    rule_ids = {finding.id for finding in result.findings}

    assert result.trust_score <= 50
    assert result.verdict == "fail"
    assert {"AP-MCP-001", "AP-MCP-004", "AP-SKILL-001", "AP-SKILL-003", "AP-CODE-001", "AP-CODE-002", "AP-CODE-003", "AP-SEC-002", "AP-SEC-003"} <= rule_ids


def test_clean_demo_passes() -> None:
    result = scan_path(ROOT / "demo" / "clean", profile="strict")

    assert result.trust_score >= 85
    assert result.verdict == "pass"
    assert result.findings == []


def test_json_report_shape() -> None:
    result = scan_path(ROOT / "demo" / "poisoned", profile="strict")
    payload = json.loads(json_reporter.render(result))

    assert payload["tool"] == "AgentPreflight"
    assert payload["schema_version"] == "1.0"
    assert payload["score"]["final"] == result.trust_score
    assert payload["findings"][0]["id"].startswith("AP-")


def test_sarif_report_shape() -> None:
    result = scan_path(ROOT / "demo" / "poisoned", profile="strict")
    payload = json.loads(sarif_reporter.render(result))

    assert payload["version"] == "2.1.0"
    assert payload["runs"][0]["tool"]["driver"]["name"] == "AgentPreflight"
    assert payload["runs"][0]["results"]


def test_cli_fail_on_high_exits_nonzero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--profile", "strict", "--fail-on", "high"])

    assert result.exit_code == 1
    assert "trust_score=" in result.output


def test_quiet_flag_prints_single_line() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--quiet"])

    assert result.exit_code == 0
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) == 1
    assert "trust_score=" in lines[0]
    assert "verdict=" in lines[0]
    assert "findings=" in lines[0]


def test_verbose_flag_shows_risk_and_fix() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", str(ROOT / "demo" / "poisoned"), "--verbose"])

    assert result.exit_code == 0
    assert "risk:" in result.output
    assert "fix:" in result.output


def test_fix_loop_turns_poisoned_copy_clean(tmp_path: Path) -> None:
    target = tmp_path / "poisoned"
    shutil.copytree(ROOT / "demo" / "poisoned", target)
    runner = CliRunner()

    before = scan_path(target, profile="strict")
    fixed = runner.invoke(app, ["fix", str(target), "--apply"])
    after = scan_path(target, profile="strict")

    assert before.verdict == "fail"
    assert fixed.exit_code == 0
    assert after.trust_score == 100
    assert after.findings == []


def _make_finding(severity: str) -> Finding:
    return Finding(
        id="AP-TEST-001",
        severity=severity,
        category="test",
        title="test",
        path="/tmp/test.py",
        evidence="test",
        risk="test",
        fix="test",
    )


def test_should_fail_strict_escalates_medium_to_high() -> None:
    medium_finding = _make_finding("medium")
    # balanced: medium finding should NOT trigger --fail-on high
    assert not _should_fail([medium_finding], "high", profile="balanced")
    # strict: medium finding SHOULD trigger --fail-on high
    assert _should_fail([medium_finding], "high", profile="strict")


def test_should_fail_strict_does_not_escalate_low() -> None:
    low_finding = _make_finding("low")
    # strict: low finding should NOT trigger --fail-on high (only medium escalates)
    assert not _should_fail([low_finding], "high", profile="strict")
    # but low should trigger --fail-on low under strict
    assert _should_fail([low_finding], "low", profile="strict")


def test_cli_strict_fail_on_high_triggers_on_medium_fixture(tmp_path: Path) -> None:
    # AP-NET-003 (medium): fires on plain http:// in markdown/config files
    fixture = tmp_path / "skill.md"
    fixture.write_text("Fetch data from http://api.example.com/data\n", encoding="utf-8")
    runner = CliRunner()

    balanced_result = runner.invoke(app, ["scan", str(tmp_path), "--profile", "balanced", "--fail-on", "high"])
    strict_result = runner.invoke(app, ["scan", str(tmp_path), "--profile", "strict", "--fail-on", "high"])

    # balanced profile: medium finding does not trigger --fail-on high
    assert balanced_result.exit_code == 0
    # strict profile: medium finding escalates to high → triggers --fail-on high
    assert strict_result.exit_code == 1
