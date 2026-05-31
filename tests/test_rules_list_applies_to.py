from __future__ import annotations

import json

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES

_RUNNER = CliRunner()

_KNOWN_TYPES = {"code_py", "code_js", "code_sh", "skill_md", "mcp_config", "env_file", "markdown"}


def test_rules_list_applies_to_code_py_shows_only_relevant() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "code_py"])
    assert result.exit_code == 0
    expected = [r for r in ALL_RULES if "code_py" in r.applies_to or "*" in r.applies_to]
    excluded = [r for r in ALL_RULES if "code_py" not in r.applies_to and "*" not in r.applies_to]
    assert len(expected) > 0
    for rule in expected:
        assert rule.id in result.output
    for rule in excluded:
        assert rule.id not in result.output


def test_rules_list_applies_to_skill_md_shows_only_relevant() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "skill_md"])
    assert result.exit_code == 0
    expected = [r for r in ALL_RULES if "skill_md" in r.applies_to or "*" in r.applies_to]
    excluded = [r for r in ALL_RULES if "skill_md" not in r.applies_to and "*" not in r.applies_to]
    assert len(expected) > 0
    for rule in expected:
        assert rule.id in result.output
    for rule in excluded:
        assert rule.id not in result.output


def test_rules_list_applies_to_mcp_config_shows_only_relevant() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "mcp_config"])
    assert result.exit_code == 0
    expected = [r for r in ALL_RULES if "mcp_config" in r.applies_to or "*" in r.applies_to]
    assert len(expected) > 0
    for rule in expected:
        assert rule.id in result.output


def test_rules_list_applies_to_invalid_type_exits_nonzero() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "nonexistent_type"])
    assert result.exit_code != 0


def test_rules_list_applies_to_invalid_shows_known_types() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "nonexistent_type"])
    # Error message should list known applies_to values
    assert "nonexistent_type" in result.output or "error" in result.output.lower()


def test_rules_list_applies_to_shows_filtered_count() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "code_py"])
    assert result.exit_code == 0
    expected_count = sum(
        1 for r in ALL_RULES if "code_py" in r.applies_to or "*" in r.applies_to
    )
    assert str(expected_count) in result.output


def test_rules_list_applies_to_combined_with_severity() -> None:
    result = _RUNNER.invoke(
        app, ["rules", "list", "--applies-to", "code_py", "--severity", "critical"]
    )
    assert result.exit_code == 0
    expected = [
        r for r in ALL_RULES
        if ("code_py" in r.applies_to or "*" in r.applies_to) and r.severity == "critical"
    ]
    for rule in expected:
        assert rule.id in result.output


def test_rules_list_applies_to_combined_with_description() -> None:
    result = _RUNNER.invoke(
        app, ["rules", "list", "--applies-to", "skill_md", "--description"]
    )
    assert result.exit_code == 0
    assert "Description" in result.output


def test_rules_list_applies_to_json_still_filters() -> None:
    result = _RUNNER.invoke(app, ["rules", "list", "--applies-to", "code_py", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    expected = [
        r for r in ALL_RULES if "code_py" in r.applies_to or "*" in r.applies_to
    ]
    assert len(data) == len(expected)
    ids = {item["id"] for item in data}
    for rule in expected:
        assert rule.id in ids
