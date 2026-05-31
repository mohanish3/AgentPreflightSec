from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES


def test_rules_list_no_category_filter_shows_all() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    for rule in ALL_RULES:
        assert rule.id in result.output


def test_rules_list_category_tool_poisoning_shows_only_that_category() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "tool_poisoning"])
    assert result.exit_code == 0
    tp_rules = [r for r in ALL_RULES if r.category == "tool_poisoning"]
    non_tp_rules = [r for r in ALL_RULES if r.category != "tool_poisoning"]
    assert len(tp_rules) > 0
    for rule in tp_rules:
        assert rule.id in result.output
    for rule in non_tp_rules:
        assert rule.id not in result.output


def test_rules_list_category_secrets_shows_only_secrets() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "secrets"])
    assert result.exit_code == 0
    sec_rules = [r for r in ALL_RULES if r.category == "secrets"]
    non_sec_rules = [r for r in ALL_RULES if r.category != "secrets"]
    assert len(sec_rules) > 0
    for rule in sec_rules:
        assert rule.id in result.output
    for rule in non_sec_rules:
        assert rule.id not in result.output


def test_rules_list_category_unsafe_exec() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "unsafe_exec"])
    assert result.exit_code == 0
    exec_rules = [r for r in ALL_RULES if r.category == "unsafe_exec"]
    assert len(exec_rules) > 0
    for rule in exec_rules:
        assert rule.id in result.output


def test_rules_list_category_case_insensitive() -> None:
    runner = CliRunner()
    lower = runner.invoke(app, ["rules", "list", "--category", "secrets"])
    upper = runner.invoke(app, ["rules", "list", "--category", "SECRETS"])
    assert lower.exit_code == 0
    assert upper.exit_code == 0
    assert lower.output == upper.output


def test_rules_list_category_invalid_exits_nonzero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "nonexistent_category_xyz"])
    assert result.exit_code != 0


def test_rules_list_category_invalid_shows_error() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "nonexistent_category_xyz"])
    assert "error" in result.output.lower() or "invalid" in result.output.lower()


def test_rules_list_severity_and_category_both_respected() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "high", "--category", "tool_poisoning"])
    assert result.exit_code == 0
    matched = [r for r in ALL_RULES if r.severity == "high" and r.category == "tool_poisoning"]
    unmatched = [r for r in ALL_RULES if not (r.severity == "high" and r.category == "tool_poisoning")]
    for rule in matched:
        assert rule.id in result.output
    for rule in unmatched:
        assert rule.id not in result.output
