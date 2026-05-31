from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES


_ALL_SEVERITIES = {"low", "medium", "high", "critical"}


def test_rules_list_no_filter_shows_all() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    for rule in ALL_RULES:
        assert rule.id in result.output


def test_rules_list_severity_critical_shows_only_critical() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "critical"])
    assert result.exit_code == 0
    critical_rules = [r for r in ALL_RULES if r.severity == "critical"]
    non_critical_rules = [r for r in ALL_RULES if r.severity != "critical"]
    assert len(critical_rules) > 0, "test assumes at least one critical rule exists"
    for rule in critical_rules:
        assert rule.id in result.output
    for rule in non_critical_rules:
        assert rule.id not in result.output


def test_rules_list_severity_high_shows_only_high() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "high"])
    assert result.exit_code == 0
    high_rules = [r for r in ALL_RULES if r.severity == "high"]
    non_high_rules = [r for r in ALL_RULES if r.severity != "high"]
    assert len(high_rules) > 0, "test assumes at least one high rule exists"
    for rule in high_rules:
        assert rule.id in result.output
    for rule in non_high_rules:
        assert rule.id not in result.output


def test_rules_list_severity_medium_shows_only_medium() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "medium"])
    assert result.exit_code == 0
    medium_rules = [r for r in ALL_RULES if r.severity == "medium"]
    non_medium_rules = [r for r in ALL_RULES if r.severity != "medium"]
    for rule in medium_rules:
        assert rule.id in result.output
    for rule in non_medium_rules:
        assert rule.id not in result.output


def test_rules_list_invalid_severity_exits_nonzero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "bogus"])
    assert result.exit_code != 0


def test_rules_list_invalid_severity_shows_error() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "bogus"])
    assert "error" in result.output.lower() or "invalid" in result.output.lower() or "bogus" in result.output


def test_rules_list_severity_case_insensitive() -> None:
    runner = CliRunner()
    lower = runner.invoke(app, ["rules", "list", "--severity", "critical"])
    upper = runner.invoke(app, ["rules", "list", "--severity", "CRITICAL"])
    assert lower.exit_code == 0
    assert upper.exit_code == 0
    assert lower.output == upper.output


def test_rules_list_severity_low() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "low"])
    assert result.exit_code == 0
    low_rules = [r for r in ALL_RULES if r.severity == "low"]
    for rule in low_rules:
        assert rule.id in result.output
