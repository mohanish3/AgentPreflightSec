from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")


def test_fail_line_shown_in_table_mode_when_threshold_exceeded() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "high"])
    assert result.exit_code == 1
    assert "FAIL" in result.output


def test_fail_line_shows_threshold() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "high"])
    assert result.exit_code == 1
    assert "threshold=high" in result.output


def test_fail_line_not_shown_in_quiet_mode() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet", "--fail-on", "high"])
    assert result.exit_code == 1
    lines = [l for l in result.output.strip().splitlines() if l.strip()]
    assert len(lines) == 1
    assert "FAIL" not in result.output


def test_fail_line_not_shown_when_threshold_not_exceeded() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--fail-on", "high"])
    assert result.exit_code == 0
    assert "FAIL" not in result.output


def test_fail_line_not_in_json_format() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--format", "json", "--fail-on", "high"])
    assert result.exit_code == 1
    import json
    data = json.loads(result.output)
    assert data["tool"] == "AgentPreflight"


def test_fail_line_threshold_critical() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--fail-on", "critical"])
    assert result.exit_code == 1
    assert "threshold=critical" in result.output


def test_no_fail_line_without_fail_on_flag() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED])
    assert result.exit_code == 0
    assert "threshold=" not in result.output
