from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from agentpreflight.cli.main import app

ROOT = Path(__file__).resolve().parents[1]
POISONED = str(ROOT / "demo" / "poisoned")
CLEAN = str(ROOT / "demo" / "clean")


def test_quiet_shows_suppressed_token() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet"])
    assert result.exit_code == 0
    assert "suppressed=" in result.output


def test_quiet_suppressed_zero_when_no_suppression_file() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet"])
    assert result.exit_code == 0
    token = next((t for t in result.output.split() if t.startswith("suppressed=")), None)
    assert token is not None
    assert token == "suppressed=0"


def test_quiet_stays_one_line() -> None:
    runner = CliRunner()
    result = runner.invoke(app, ["scan", POISONED, "--quiet"])
    assert result.exit_code == 0
    lines = [line for line in result.output.strip().splitlines() if line.strip()]
    assert len(lines) == 1


def test_quiet_suppressed_token_before_profile() -> None:
    """suppressed= appears in the single quiet line."""
    runner = CliRunner()
    result = runner.invoke(app, ["scan", CLEAN, "--quiet"])
    assert result.exit_code == 0
    line = result.output.strip()
    assert "suppressed=" in line
    assert "profile=" in line
