from __future__ import annotations

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES


def test_rules_list_shows_total_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    total = len(ALL_RULES)
    assert f"{total} rules" in result.output


def test_rules_list_severity_filter_shows_filtered_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "high"])
    assert result.exit_code == 0
    high_count = sum(1 for r in ALL_RULES if r.severity == "high")
    total = len(ALL_RULES)
    assert f"{high_count} of {total} rules" in result.output


def test_rules_list_category_filter_shows_filtered_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--category", "secrets"])
    assert result.exit_code == 0
    cat_count = sum(1 for r in ALL_RULES if r.category == "secrets")
    total = len(ALL_RULES)
    assert f"{cat_count} of {total} rules" in result.output


def test_rules_list_combined_filter_shows_filtered_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--severity", "high", "--category", "tool_poisoning"])
    assert result.exit_code == 0
    matched = sum(1 for r in ALL_RULES if r.severity == "high" and r.category == "tool_poisoning")
    total = len(ALL_RULES)
    assert f"{matched} of {total} rules" in result.output


def test_rules_list_count_footer_does_not_contain_rule_id_format() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    # footer line should contain "rules" but not look like a rule ID
    lines = result.output.splitlines()
    footer_lines = [l for l in lines if "rules" in l and "AP-" not in l]
    assert len(footer_lines) >= 1


def test_rules_search_no_count_footer_on_no_match() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "XYZZY_NOMATCH"])
    assert result.exit_code == 0
    # No count footer when no results — just "no rules matched"
    assert "0 of" not in result.output


def test_rules_search_shows_count_on_match() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "search", "exec"])
    assert result.exit_code == 0
    # Should show match count
    total = len(ALL_RULES)
    matched = sum(
        1 for r in ALL_RULES
        if "exec" in r.id.lower() or "exec" in r.category.lower()
        or "exec" in r.description.lower() or "exec" in r.remediation.lower()
        or any("exec" in ref.lower() for ref in r.references)
    )
    assert f"{matched} of {total} rules" in result.output
