from __future__ import annotations

import json

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES


def test_rules_list_json_exits_zero() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0


def test_rules_list_json_valid_json() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert isinstance(data, list)


def test_rules_list_json_all_21_rules() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert len(data) == len(ALL_RULES)


def test_rules_list_json_has_required_fields() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    for rule in data:
        assert "id" in rule
        assert "severity" in rule
        assert "category" in rule
        assert "applies_to" in rule


def test_rules_list_json_severity_filter_respected() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json", "--severity", "critical"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert all(r["severity"] == "critical" for r in data)
    assert len(data) > 0


def test_rules_list_json_category_filter_respected() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json", "--category", "secrets"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert all(r["category"] == "secrets" for r in data)
    assert len(data) > 0


def test_rules_list_default_still_shows_table() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list"])
    assert result.exit_code == 0
    # Table format — not valid top-level JSON array
    for rule in ALL_RULES:
        assert rule.id in result.output


def test_rules_list_json_has_description_field() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    # description may be empty string but key must exist
    assert all("description" in r for r in data)


def test_rules_list_json_ids_match_catalog() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["rules", "list", "--json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    catalog_ids = {r.id for r in ALL_RULES}
    json_ids = {r["id"] for r in data}
    assert json_ids == catalog_ids
