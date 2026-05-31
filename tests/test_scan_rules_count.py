from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app
from agentpreflight.rules.catalog import ALL_RULES

ROOT = Path(__file__).resolve().parents[1]
CLEAN = str(ROOT / "demo" / "clean")
POISONED = str(ROOT / "demo" / "poisoned")


def test_table_shows_rules_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN])
    assert result.exit_code == 0
    assert f"rules={len(ALL_RULES)}" in result.output


def test_table_rules_count_on_poisoned() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED])
    assert result.exit_code == 0
    assert f"rules={len(ALL_RULES)}" in result.output


def test_no_banner_still_shows_rules_count() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--no-banner"])
    assert result.exit_code == 0
    assert f"rules={len(ALL_RULES)}" in result.output


def test_json_format_unaffected() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["tool"] == "AgentPreflight"


def test_top_equality_still_holds() -> None:
    """Regression: adding rules= must not break default==explicit equality."""
    runner = CliRunner()
    default = runner.invoke(app, ["scan", POISONED])
    explicit = runner.invoke(app, ["scan", POISONED, "--top", "20"])
    assert default.exit_code == 0
    assert default.output == explicit.output
