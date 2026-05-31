from __future__ import annotations

import json

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES

_RUNNER = CliRunner()


def test_rules_list_description_flag_shows_column_header() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--description"])
    assert result.exit_code == 0
    assert "Description" in result.output


def test_rules_list_description_flag_shows_description_text() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--description"])
    assert result.exit_code == 0
    # Rich wraps cell text across lines; check individual words (>= 6 chars) from descriptions
    all_desc_words = {
        word
        for r in ALL_RULES
        if r.description
        for word in r.description.split()
        if len(word) >= 6
    }
    found = any(word in result.output for word in all_desc_words)
    assert found, "Expected at least one description word in output"


def test_rules_list_description_all_rule_ids_still_present() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--description"])
    assert result.exit_code == 0
    for rule in ALL_RULES:
        assert rule.id in result.output


def test_rules_list_no_description_flag_omits_description_header() -> None:
    result = _RUNNER.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    assert "Description" not in result.output


def test_rules_list_description_combined_with_severity_filter() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--description", "--severity", "critical"])
    assert result.exit_code == 0
    critical_rules = [r for r in ALL_RULES if r.severity == "critical"]
    assert len(critical_rules) > 0
    for rule in critical_rules:
        assert rule.id in result.output
    assert "Description" in result.output


def test_rules_list_description_combined_with_category_filter() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--description", "--category", "unsafe_exec"])
    assert result.exit_code == 0
    assert "Description" in result.output
    unsafe_exec_rules = [r for r in ALL_RULES if r.category == "unsafe_exec"]
    assert len(unsafe_exec_rules) > 0
    for rule in unsafe_exec_rules:
        assert rule.id in result.output


def test_rules_list_description_json_still_includes_description() -> None:
    """JSON output always includes description; --description has no effect on JSON."""
    result = _RUNNER.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert all("description" in r for r in data)
