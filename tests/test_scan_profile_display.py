from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
CLEAN = str(ROOT / "demo" / "clean")
POISONED = str(ROOT / "demo" / "poisoned")


def test_table_shows_profile_balanced_default() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN])
    assert result.exit_code == 0
    assert "profile=balanced" in result.output


def test_table_shows_profile_strict() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--profile", "strict"])
    assert result.exit_code == 0
    assert "profile=strict" in result.output


def test_table_shows_profile_dev() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--profile", "dev"])
    assert result.exit_code == 0
    assert "profile=dev" in result.output


def test_quiet_also_shows_profile() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--quiet"])
    assert result.exit_code == 0
    assert "profile=" in result.output


def test_json_format_has_profile_field() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--format", "json"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["profile"] == "balanced"


def test_top_equality_still_holds_with_profile() -> None:
    """Regression: adding profile to table must not break default==explicit equality."""
    runner = CliRunner()
    default = runner.invoke(app, ["scan", POISONED])
    explicit = runner.invoke(app, ["scan", POISONED, "--top", "20"])
    assert default.exit_code == 0
    assert default.output == explicit.output
